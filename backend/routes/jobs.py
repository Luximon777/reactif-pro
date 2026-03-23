from fastapi import APIRouter, HTTPException
from typing import Optional
import logging
from datetime import datetime, timezone
from models import JobOffer, Beneficiary, CreateJobRequest, CandidateSearchProfile
from db import db
from helpers import get_current_token, calculate_match_with_ai
from job_matching import calculate_job_score

router = APIRouter()


async def _gather_user_context(token_id: str):
    """Gather CV, optimized CV, passport data for a user."""
    cv_job = await db.cv_jobs.find_one(
        {"token_id": token_id, "status": "completed"}, {"_id": 0},
        sort=[("created_at", -1)]
    )
    cv_optimized = await db.cv_models.find_one({"token_id": token_id}, {"_id": 0})
    passport = await db.passports.find_one({"token_id": token_id}, {"_id": 0})

    user_skills = set()
    user_title = ""
    career_project = ""

    if cv_job and cv_job.get("result"):
        for t in cv_job["result"].get("competences_transversales", []):
            if t:
                user_skills.add(t)

    if cv_optimized and cv_optimized.get("models"):
        for model_data in cv_optimized["models"].values():
            if isinstance(model_data, dict):
                user_title = model_data.get("titre", "")
                for ck in model_data.get("competences_cles", []):
                    if isinstance(ck, str):
                        user_skills.add(ck)
                for sf in model_data.get("savoir_faire", []):
                    name = sf.get("name", "") if isinstance(sf, dict) else sf
                    if name:
                        user_skills.add(str(name))
                break

    if passport:
        career_project = passport.get("career_project", "")
        for c in passport.get("competences", []):
            name = c.get("name", "")
            if name:
                user_skills.add(name)

    return cv_job, cv_optimized, passport, user_skills, user_title, career_project


async def _generate_ai_offers(token_id: str, user_skills: set, user_title: str, career_project: str, filters: dict = None):
    """Generate AI-powered job offers, optionally guided by user filters."""
    from db import EMERGENT_LLM_KEY
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    import json as _json

    if not EMERGENT_LLM_KEY or not user_skills:
        return []

    skills_str = ", ".join(list(user_skills)[:20])
    context = f"Titre du profil: {user_title}\nCompétences: {skills_str}"
    if career_project:
        context += f"\nProjet professionnel: {career_project[:200]}"

    # Add filter context to guide AI generation
    filter_context = ""
    if filters:
        if filters.get("metier") and filters["metier"].get("value"):
            val = filters["metier"]["value"]
            if isinstance(val, list):
                filter_context += f"\nMétier(s) visé(s): {', '.join(val)}"
            else:
                filter_context += f"\nMétier visé: {val}"
        if filters.get("secteur") and filters["secteur"].get("value"):
            val = filters["secteur"]["value"]
            if isinstance(val, list):
                filter_context += f"\nSecteur(s) préféré(s): {', '.join(val)}"
            else:
                filter_context += f"\nSecteur préféré: {val}"
        if filters.get("contrat") and filters["contrat"].get("value"):
            val = filters["contrat"]["value"]
            if isinstance(val, list):
                filter_context += f"\nType(s) de contrat: {', '.join(val)}"
            else:
                filter_context += f"\nType de contrat: {val}"

    if filter_context:
        context += f"\n\nCritères de recherche du candidat:{filter_context}"

    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"jobmatch-{token_id[:8]}",
            system_message="""Tu es un expert en recrutement et matching emploi en France.
Analyse le profil et génère 8 offres d'emploi RÉALISTES et CONCRÈTES qui correspondent au profil.

Règles:
- Les offres doivent être RÉALISTES (types d'offres qu'on trouve sur Indeed, Pôle Emploi, APEC)
- Si des critères de recherche sont fournis, génère des offres qui y correspondent ET des offres proches/alternatives
- Varie les types de contrats (CDI, CDD, missions)
- Varie les niveaux de compatibilité

Réponds UNIQUEMENT en JSON valide: un array de 8 objets:
{
  "titre": "Intitulé exact du poste",
  "entreprise_type": "Type d'entreprise (PME, Grand groupe, Association, etc.)",
  "secteur": "Secteur d'activité",
  "metier": "Intitulé du métier normalisé",
  "type_contrat": "CDI|CDD|Mission|Freelance|Alternance",
  "temps_travail": "temps plein|temps partiel",
  "localisation": "Ville ou région",
  "trajet_estime_minutes": 30,
  "teletravail": true ou false,
  "amenagement_possible": true ou false,
  "port_charges": false,
  "travail_nuit": false,
  "horaires_decales": false,
  "accessibilite_locaux": true,
  "environnement": "calme ou standard",
  "description": "Description courte (2-3 phrases)",
  "competences_requises": ["comp1", "comp2", "comp3", "comp4", "comp5"],
  "competences_matchees": ["comp du profil qui matche"],
  "salaire_indicatif": "fourchette salariale",
  "pourquoi_ce_match": "Explication courte du matching",
  "url_offre": ""
}"""
        ).with_model("openai", "gpt-5.2")

        response = await chat.send_message(UserMessage(text=context))
        raw = response.strip() if isinstance(response, str) else response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]

        ai_matches = _json.loads(raw.strip())
        if isinstance(ai_matches, list):
            return ai_matches
        elif isinstance(ai_matches, dict):
            return ai_matches.get("matches", ai_matches.get("offres", []))
    except Exception as e:
        logging.error(f"Job matching AI error: {e}")
    return []


@router.get("/jobs/matching")
async def get_job_matching(token: str):
    """Generate AI-powered job matching based on the user's CV analysis and optimized CV."""
    token_doc = await get_current_token(token)
    token_id = token_doc["id"]

    cv_job, cv_optimized, passport, user_skills, user_title, career_project = await _gather_user_context(token_id)

    if not cv_job:
        return {"has_data": False, "matches": [], "message": "Analysez votre CV pour obtenir des offres d'emploi personnalisées"}

    # Load saved preferences if any
    prefs = await db.job_search_preferences.find_one({"token_id": token_id}, {"_id": 0})
    filters = prefs.get("filters", {}) if prefs else {}

    # Generate AI offers
    ai_offers = await _generate_ai_offers(token_id, user_skills, user_title, career_project, filters)

    # If user has filters, score each offer with the algorithm
    matches = []
    if filters and any(filters.get(k) for k in ["metier", "secteur", "contrat", "temps_travail", "trajet_max_minutes", "teletravail", "amenagement_poste", "restrictions_fonctionnelles"]):
        candidate_profile = {}
        for key in ["metier", "secteur", "contrat", "temps_travail", "trajet_max_minutes", "teletravail", "amenagement_poste", "restrictions_fonctionnelles"]:
            if filters.get(key) and filters[key].get("value"):
                candidate_profile[key] = filters[key]

        for offer in ai_offers:
            job_data = {
                "metier": offer.get("metier", offer.get("titre", "")),
                "secteur": offer.get("secteur", ""),
                "contrat": offer.get("type_contrat", ""),
                "temps_travail": offer.get("temps_travail", ""),
                "trajet_estime_minutes": offer.get("trajet_estime_minutes", 30),
                "teletravail": offer.get("teletravail", False),
                "amenagement_possible": offer.get("amenagement_possible", False),
                "port_charges": offer.get("port_charges", False),
                "travail_nuit": offer.get("travail_nuit", False),
                "accessibilite_locaux": offer.get("accessibilite_locaux", True),
                "horaires_decales": offer.get("horaires_decales", False),
                "environnement": offer.get("environnement", ""),
            }
            scoring = calculate_job_score(candidate_profile, job_data)
            offer["scoring"] = scoring
            offer["matching_score"] = scoring["score"]
            offer["source"] = "ai_scored"
        matches = ai_offers
    else:
        for offer in ai_offers:
            offer["source"] = "ai_generated"
        matches = ai_offers

    matches.sort(key=lambda x: x.get("matching_score", 0), reverse=True)

    return {
        "has_data": True,
        "matches": matches[:10],
        "has_filters": bool(filters),
        "profile_summary": {
            "titre": user_title,
            "skills_count": len(user_skills),
            "has_optimized_cv": bool(cv_optimized),
            "has_career_project": bool(career_project)
        }
    }


@router.post("/jobs/matching/search")
async def search_job_matching(token: str, search_profile: CandidateSearchProfile):
    """Search job matches with advanced scoring based on candidate criteria."""
    token_doc = await get_current_token(token)
    token_id = token_doc["id"]

    cv_job, cv_optimized, passport, user_skills, user_title, career_project = await _gather_user_context(token_id)

    if not cv_job:
        return {"has_data": False, "matches": [], "message": "Analysez votre CV pour obtenir des offres d'emploi personnalisées"}

    # Build filters dict from search profile
    filters = {}
    profile_dict = search_profile.model_dump(exclude_none=True)
    for key, criterion in profile_dict.items():
        if criterion and criterion.get("value"):
            filters[key] = criterion

    # Save preferences
    await db.job_search_preferences.update_one(
        {"token_id": token_id},
        {"$set": {"token_id": token_id, "filters": filters, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )

    # Generate AI offers guided by filters
    ai_offers = await _generate_ai_offers(token_id, user_skills, user_title, career_project, filters)

    # Score each offer
    matches = []
    for offer in ai_offers:
        job_data = {
            "metier": offer.get("metier", offer.get("titre", "")),
            "secteur": offer.get("secteur", ""),
            "contrat": offer.get("type_contrat", ""),
            "temps_travail": offer.get("temps_travail", ""),
            "trajet_estime_minutes": offer.get("trajet_estime_minutes", 30),
            "teletravail": offer.get("teletravail", False),
            "amenagement_possible": offer.get("amenagement_possible", False),
            "port_charges": offer.get("port_charges", False),
            "travail_nuit": offer.get("travail_nuit", False),
            "accessibilite_locaux": offer.get("accessibilite_locaux", True),
            "horaires_decales": offer.get("horaires_decales", False),
            "environnement": offer.get("environnement", ""),
        }
        scoring = calculate_job_score(filters, job_data)
        offer["scoring"] = scoring
        offer["matching_score"] = scoring["score"]
        offer["source"] = "ai_scored"
        matches.append(offer)

    matches.sort(key=lambda x: x.get("matching_score", 0), reverse=True)

    return {
        "has_data": True,
        "matches": matches[:10],
        "has_filters": True,
        "filters_applied": filters,
        "profile_summary": {
            "titre": user_title,
            "skills_count": len(user_skills),
            "has_optimized_cv": bool(cv_optimized),
            "has_career_project": bool(career_project)
        }
    }


@router.get("/jobs/matching/preferences")
async def get_matching_preferences(token: str):
    """Get saved job matching preferences."""
    token_doc = await get_current_token(token)
    prefs = await db.job_search_preferences.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not prefs:
        return {"has_preferences": False, "filters": {}}
    return {"has_preferences": True, "filters": prefs.get("filters", {})}


@router.put("/jobs/matching/preferences")
async def save_matching_preferences(token: str, search_profile: CandidateSearchProfile):
    """Save job matching preferences without triggering search."""
    token_doc = await get_current_token(token)
    filters = {}
    profile_dict = search_profile.model_dump(exclude_none=True)
    for key, criterion in profile_dict.items():
        if criterion and criterion.get("value"):
            filters[key] = criterion
    await db.job_search_preferences.update_one(
        {"token_id": token_doc["id"]},
        {"$set": {"token_id": token_doc["id"], "filters": filters, "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"message": "Préférences sauvegardées", "filters": filters}



@router.get("/jobs")
async def get_jobs(token: str, limit: int = 20):
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    jobs = await db.jobs.find({"status": "active"}, {"_id": 0}).to_list(limit)

    # Get latest CV analysis for richer matching
    cv_data = await db.cv_jobs.find_one(
        {"token_id": token_doc["id"], "status": "completed"},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    cv_transversales = []
    cv_offres = []
    if cv_data and cv_data.get("result"):
        result = cv_data["result"]
        cv_transversales = result.get("competences_transversales", [])
        cv_offres = result.get("offres_emploi_suggerees", [])

    if profile and (profile.get("skills") or cv_transversales):
        profile_skill_names = [s.get("name", "").lower() for s in profile.get("skills", [])]
        all_skills = set(profile_skill_names + [c.lower() for c in cv_transversales])
        for job in jobs:
            req = [s.lower() for s in job.get("required_skills", [])]
            common = all_skills & set(req)
            job["match_score"] = min(100, int((len(common) / max(len(req), 1)) * 100) + 25)

    # If no jobs in DB but CV has suggestions, generate virtual job cards
    if not jobs and cv_offres:
        for i, offre in enumerate(cv_offres[:6]):
            jobs.append({
                "id": f"cv-suggestion-{i}",
                "title": offre,
                "company": "Suggestion basée sur votre CV",
                "location": "France",
                "contract_type": "Tous types",
                "match_score": max(60, 95 - i * 7),
                "required_skills": cv_transversales[:4],
                "salary_range": None,
                "sector": "Basé sur votre profil",
                "source": "cv_analysis",
                "status": "active"
            })

    return sorted(jobs, key=lambda x: x.get("match_score", 0), reverse=True)


@router.post("/jobs")
async def create_job(token: str, request: CreateJobRequest):
    token_doc = await get_current_token(token)
    if token_doc["role"] != "entreprise":
        raise HTTPException(status_code=403, detail="Accès réservé aux entreprises")
    job = JobOffer(**request.model_dump(), created_by=token_doc["id"])
    await db.jobs.insert_one(job.model_dump())
    return job.model_dump()


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    job = await db.jobs.find_one({"id": job_id}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    return job


@router.get("/jobs/{job_id}/match")
async def get_job_match(token: str, job_id: str):
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    job = await db.jobs.find_one({"id": job_id}, {"_id": 0})
    if not profile or not job:
        raise HTTPException(status_code=404, detail="Profil ou offre non trouvé")
    profile_skill_names = [s.get("name", "") for s in profile.get("skills", [])]
    return await calculate_match_with_ai(profile_skill_names, job.get("required_skills", []), profile.get("sectors", []), job.get("sector", ""))


@router.get("/learning")
async def get_learning_modules(token: str):
    token_doc = await get_current_token(token)
    token_id = token_doc["id"]
    modules = await db.learning_modules.find({}, {"_id": 0}).to_list(50)
    progress_docs = await db.learning_progress.find({"token_id": token_id}, {"_id": 0}).to_list(100)
    progress_map = {p["module_id"]: p["progress"] for p in progress_docs}

    # Collect user skills and gaps from CV + passport
    user_skills_lower = set()
    skill_gaps = set()

    passport = await db.passports.find_one({"token_id": token_id}, {"_id": 0})
    if passport:
        for c in passport.get("competences", []):
            name = c.get("name", "").strip().lower()
            if name:
                user_skills_lower.add(name)

    cv_job = await db.cv_jobs.find_one(
        {"token_id": token_id, "status": "completed"},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    cv_result = cv_job.get("result", {}) if cv_job else {}
    for t in cv_result.get("competences_transversales", []):
        if t:
            user_skills_lower.add(t.lower())

    # Get recommended skills from job evolution indices (skills user should acquire)
    user_sectors = set()
    if passport:
        for s in passport.get("target_sectors", []):
            if s:
                user_sectors.add(s)
    for sector in user_sectors:
        jobs = await db.job_evolution_indices.find({"sector": {"$regex": sector, "$options": "i"}}, {"_id": 0, "recommended_skills": 1}).to_list(10)
        for j in jobs:
            for rs in j.get("recommended_skills", []):
                if rs.lower() not in user_skills_lower:
                    skill_gaps.add(rs.lower())

    for module in modules:
        module["progress"] = progress_map.get(module["id"], 0)
        # Calculate relevance score based on skill gaps
        module_skills = set(s.lower() for s in module.get("skills_developed", []))
        gaps_addressed = module_skills & skill_gaps
        skills_already_have = module_skills & user_skills_lower
        if gaps_addressed:
            module["relevance"] = "haute"
            module["relevance_score"] = min(100, len(gaps_addressed) * 35 + 30)
            module["gaps_addressed"] = list(gaps_addressed)
        elif skills_already_have:
            module["relevance"] = "moyenne"
            module["relevance_score"] = 40
            module["gaps_addressed"] = []
        else:
            module["relevance"] = "basse"
            module["relevance_score"] = 10
            module["gaps_addressed"] = []

    # Sort: in-progress first, then by relevance, then alphabetical
    modules.sort(key=lambda m: (
        -(m.get("progress", 0) > 0 and m.get("progress", 0) < 100),
        -m.get("relevance_score", 0)
    ))

    return modules


@router.post("/learning/{module_id}/progress")
async def update_learning_progress(token: str, module_id: str, progress: int):
    token_doc = await get_current_token(token)
    await db.learning_progress.update_one(
        {"token_id": token_doc["id"], "module_id": module_id},
        {"$set": {"progress": min(100, max(0, progress)), "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    return {"message": "Progression mise à jour", "progress": progress}


@router.get("/learning/recommendations")
async def get_personalized_training_recommendations(token: str):
    """Generate AI-powered personalized training recommendations based on CV and passport."""
    from db import EMERGENT_LLM_KEY
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    import json as _json

    token_doc = await get_current_token(token)
    token_id = token_doc["id"]

    # Gather user context
    passport = await db.passports.find_one({"token_id": token_id}, {"_id": 0})
    cv_job = await db.cv_jobs.find_one(
        {"token_id": token_id, "status": "completed"}, {"_id": 0},
        sort=[("created_at", -1)]
    )

    if not passport and not cv_job:
        return {"has_data": False, "recommendations": [], "message": "Analysez votre CV pour obtenir des recommandations de formation personnalisées"}

    # Build context
    competences = []
    career_project = ""
    professional_summary = ""
    experiences = []

    if passport:
        competences = [c.get("name", "") for c in passport.get("competences", [])[:15]]
        career_project = passport.get("career_project", "")
        professional_summary = passport.get("professional_summary", "")
        experiences = [f"{e.get('title','')} - {e.get('company','')}" for e in passport.get("experiences", [])[:5]]

    cv_skills = []
    if cv_job and cv_job.get("result"):
        result = cv_job["result"]
        cv_skills = result.get("competences_transversales", [])

    context = f"""Profil de la personne:
- Compétences: {', '.join(competences[:15])}
- Compétences transversales CV: {', '.join(cv_skills[:10])}
- Résumé professionnel: {professional_summary[:200]}
- Projet professionnel: {career_project[:200]}
- Expériences: {', '.join(experiences[:5])}"""

    if not EMERGENT_LLM_KEY:
        return {"has_data": False, "recommendations": [], "message": "Service IA indisponible"}

    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"training-rec-{token_id[:8]}",
            system_message="""Tu es un conseiller en formation professionnelle expert en France.
Analyse le profil de la personne et propose 6 formations CONCRÈTES et PERTINENTES pour son évolution.

Règles:
- Propose des formations RÉELLES et accessibles en France (certifications, diplômes, formations courtes)
- Adapte les formations au niveau de la personne et à son projet professionnel
- Inclus un mix: formations certifiantes (titres RNCP), formations courtes (CPF), et MOOC/autoformation
- Sois SPÉCIFIQUE: pas de formations génériques, mais des formations adaptées au métier visé

Réponds UNIQUEMENT en JSON valide: un array de 6 objets avec:
{
  "title": "Titre exact de la formation",
  "provider": "Organisme (ex: AFPA, CNAM, Université...)",
  "type": "certifiante|courte|mooc|diplome",
  "duration": "durée estimée",
  "level": "debutant|intermediaire|avance",
  "description": "Description courte (2 phrases max)",
  "skills_developed": ["compétence1", "compétence2", "compétence3"],
  "relevance_reason": "Pourquoi cette formation est pertinente pour ce profil",
  "cpf_eligible": true/false,
  "priority": "haute|moyenne|basse"
}"""
        ).with_model("openai", "gpt-5.2")

        response = await chat.send_message(UserMessage(text=context))
        raw = response.strip() if isinstance(response, str) else response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]

        result = _json.loads(raw.strip())
        recs = result if isinstance(result, list) else result.get("formations", result.get("recommendations", []))

        return {
            "has_data": True,
            "recommendations": recs[:6],
            "profile_context": {
                "competences_count": len(competences),
                "has_cv": bool(cv_job),
                "has_career_project": bool(career_project)
            }
        }
    except Exception as e:
        logging.error(f"Training recommendations error: {e}")
        return {"has_data": False, "recommendations": [], "message": "Erreur lors de la génération des recommandations"}


@router.get("/rh/offers")
async def get_rh_offers(token: str):
    token_doc = await get_current_token(token)
    return await db.jobs.find({"created_by": token_doc["id"]}, {"_id": 0}).to_list(50)


@router.get("/rh/candidates")
async def get_candidates(token: str, job_id: Optional[str] = None):
    token_doc = await get_current_token(token)
    profiles = await db.profiles.find({"role": "particulier"}, {"_id": 0}).to_list(50)
    if job_id:
        job = await db.jobs.find_one({"id": job_id}, {"_id": 0})
        if job:
            for profile in profiles:
                profile_skill_names = [s.get("name", "") for s in profile.get("skills", [])]
                common = set(profile_skill_names) & set(job.get("required_skills", []))
                profile["match_score"] = min(100, int((len(common) / max(len(job.get("required_skills", [])), 1)) * 100) + 20)
            profiles = sorted(profiles, key=lambda x: x.get("match_score", 0), reverse=True)
    return profiles


@router.get("/partenaires/beneficiaires")
async def get_beneficiaires(token: str):
    token_doc = await get_current_token(token)
    return await db.beneficiaires.find({"partner_id": token_doc["id"]}, {"_id": 0}).to_list(100)


@router.post("/partenaires/beneficiaires")
async def create_beneficiaire(token: str, name: str, sector: str):
    token_doc = await get_current_token(token)
    beneficiary = Beneficiary(name=name, status="En accompagnement", sector=sector, partner_id=token_doc["id"])
    await db.beneficiaires.insert_one(beneficiary.model_dump())
    return beneficiary.model_dump()


@router.put("/partenaires/beneficiaires/{beneficiary_id}")
async def update_beneficiaire(token: str, beneficiary_id: str, status: Optional[str] = None, progress: Optional[int] = None):
    update_data = {}
    if status:
        update_data["status"] = status
    if progress is not None:
        update_data["progress"] = progress
    update_data["last_activity"] = datetime.now(timezone.utc).isoformat()
    await db.beneficiaires.update_one({"id": beneficiary_id}, {"$set": update_data})
    return await db.beneficiaires.find_one({"id": beneficiary_id}, {"_id": 0})


@router.get("/metrics")
async def get_metrics():
    particuliers_count = await db.profiles.count_documents({"role": "particulier"})
    entreprises_count = await db.profiles.count_documents({"role": "entreprise"})
    jobs_count = await db.jobs.count_documents({"status": "active"})
    beneficiaires_count = await db.beneficiaires.count_documents({})
    return {
        "particuliers": {"total": particuliers_count, "active": particuliers_count},
        "entreprises": {"total": entreprises_count, "jobs_posted": jobs_count},
        "partenaires": {"beneficiaires": beneficiaires_count, "active_support": beneficiaires_count}
    }
