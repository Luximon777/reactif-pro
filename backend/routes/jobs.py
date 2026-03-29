from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from datetime import datetime, timezone
from models import JobOffer, Beneficiary, CreateJobRequest, CandidateSearchProfile, JobApplication
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

    # Priority 1: Use CV optimized model title and core competences
    if cv_optimized and cv_optimized.get("models"):
        for model_data in cv_optimized["models"].values():
            parsed = model_data
            if isinstance(parsed, str):
                try:
                    import json as _j
                    parsed = _j.loads(parsed)
                except Exception:
                    continue
            if isinstance(parsed, dict):
                user_title = parsed.get("titre", "")
                # Add core competences first (most relevant to current role)
                for ck in parsed.get("competences_cles", []):
                    if isinstance(ck, str):
                        user_skills.add(ck)
                # Add technique/transversale savoir_faire (directly relevant to role)
                for sf in parsed.get("savoir_faire", []):
                    if isinstance(sf, dict):
                        cat = sf.get("category", "")
                        if cat in ("technique", "transversale"):
                            user_skills.add(sf.get("name", ""))
                break

    # Priority 2: Add some CV raw transversales if we don't have enough skills
    if cv_job and cv_job.get("result"):
        for t in cv_job["result"].get("competences_transversales", []):
            if t and len(user_skills) < 20:
                user_skills.add(t)

    # Priority 3: Add passport competences (lowest priority to avoid transferable skill pollution)
    if passport:
        career_project = passport.get("career_project", "")
        for c in passport.get("competences", []):
            name = c.get("name", "")
            if name and len(user_skills) < 25:
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
    context = f"MÉTIER ACTUEL DU CV (RÉFÉRENCE PRINCIPALE): {user_title}\nCompétences du métier: {skills_str}"
    if career_project:
        context += f"\nProjet professionnel (contexte secondaire): {career_project[:200]}"

    # Add filter context to guide AI generation
    filter_context = ""
    if filters:
        if filters.get("lieu_residence") and filters["lieu_residence"].get("value"):
            filter_context += f"\nLieu de résidence du candidat: {filters['lieu_residence']['value']}"
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
        if filters.get("zone_geographique") and filters["zone_geographique"].get("value"):
            filter_context += f"\nZone géographique souhaitée: {filters['zone_geographique']['value']}"
        if filters.get("distance_km") and filters["distance_km"].get("value"):
            filter_context += f"\nDistance maximale depuis le domicile: {filters['distance_km']['value']} km"
        if filters.get("salaire_minimum") and filters["salaire_minimum"].get("value"):
            filter_context += f"\nSalaire minimum souhaité: {filters['salaire_minimum']['value']} € brut/an"

    if filter_context:
        context += f"\n\nCritères de recherche du candidat:{filter_context}"

    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"jobmatch-{token_id[:8]}",
            system_message="""Tu es un expert en recrutement et matching emploi en France.
Analyse le profil et génère 8 offres d'emploi RÉALISTES et CONCRÈTES qui correspondent au profil.

RÈGLE CRITIQUE:
- Le MÉTIER ACTUEL DU CV est la référence principale. Les offres DOIVENT correspondre à ce métier ou à des métiers proches/accessibles.
- NE GÉNÈRE PAS d'offres basées uniquement sur des compétences transférables issues d'anciennes expériences si elles ne correspondent pas au métier actuel.
- Si des critères de recherche sont fournis, génère des offres qui y correspondent ET des offres proches/alternatives
- Varie les types de contrats (CDI, CDD, missions)
- Varie les niveaux de compatibilité
- Varie les niveaux d'inclusion employeur (certains très inclusifs, d'autres non)

Réponds UNIQUEMENT en JSON valide: un array de 8 objets:
{
  "titre": "Intitulé exact du poste",
  "entreprise_type": "Type d'entreprise (PME, Grand groupe, Association, etc.)",
  "secteur": "Secteur d'activité",
  "metier": "Intitulé du métier normalisé",
  "type_contrat": "CDI|CDD|Mission|Freelance|Alternance",
  "temps_travail": "temps plein|temps partiel",
  "localisation": "Ville ou région (respecter la zone géographique demandée)",
  "distance_domicile_km": 15,
  "teletravail": true ou false,
  "amenagement_possible": true ou false,
  "accessibilite_locaux": true ou false,
  "exigences_metier": {
    "port_charges": false,
    "station_debout_prolongee": false,
    "travail_nuit": false,
    "environnement": "calme|standard|bruyant",
    "horaires_decales": false,
    "deplacements_frequents": false,
    "cadence_elevee": false
  },
  "employeur": {
    "entreprise_inclusive": true ou false,
    "partenaire_cap_emploi": true ou false,
    "experience_recrutement_handicap": true ou false,
    "referent_handicap": true ou false,
    "obligation_emploi_respectee": true ou false,
    "poste_adapte": true ou false
  },
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


def _build_job_data(offer):
    """Map an AI-generated offer to the structured format expected by calculate_job_score."""
    exigences = offer.get("exigences_metier", {})
    return {
        "metier": offer.get("metier", offer.get("titre", "")),
        "secteur": offer.get("secteur", ""),
        "contrat": offer.get("type_contrat", ""),
        "temps_travail": offer.get("temps_travail", ""),
        "trajet_estime_minutes": offer.get("trajet_estime_minutes", 30),
        "teletravail": offer.get("teletravail", False),
        "amenagement_possible": offer.get("amenagement_possible", False),
        "accessibilite_locaux": offer.get("accessibilite_locaux", True),
        "exigences_metier": {
            "port_charges": exigences.get("port_charges", offer.get("port_charges", False)),
            "station_debout_prolongee": exigences.get("station_debout_prolongee", False),
            "travail_nuit": exigences.get("travail_nuit", offer.get("travail_nuit", False)),
            "environnement": exigences.get("environnement", offer.get("environnement", "")),
            "horaires_decales": exigences.get("horaires_decales", offer.get("horaires_decales", False)),
            "deplacements_frequents": exigences.get("deplacements_frequents", False),
            "cadence_elevee": exigences.get("cadence_elevee", False),
        },
        "employeur": offer.get("employeur", {}),
    }



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
    all_filter_keys = ["metier", "secteur", "contrat", "temps_travail", "trajet_max_minutes", "teletravail",
                       "amenagement_poste", "restrictions_fonctionnelles", "ciblage_employeurs_inclusifs", "accessibilite_metier_handicap",
                       "zone_geographique", "distance_km", "lieu_residence", "salaire_minimum"]
    if filters and any(filters.get(k) for k in all_filter_keys):
        candidate_profile = {}
        for key in all_filter_keys:
            if filters.get(key) and filters[key].get("value"):
                candidate_profile[key] = filters[key]
        # Include rqth_eqth context if present
        if filters.get("rqth_eqth"):
            candidate_profile["rqth_eqth"] = filters["rqth_eqth"]

        for offer in ai_offers:
            job_data = _build_job_data(offer)
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
        job_data = _build_job_data(offer)
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
            if isinstance(offre, dict):
                jobs.append({
                    "id": f"cv-suggestion-{i}",
                    "title": offre.get("titre", offre.get("title", "Offre suggérée")),
                    "company": offre.get("entreprise_type", offre.get("company", "Suggestion basée sur votre CV")),
                    "location": offre.get("localisation", offre.get("location", "France")),
                    "contract_type": offre.get("type_contrat", offre.get("contract_type", "Tous types")),
                    "match_score": max(60, 95 - i * 7),
                    "required_skills": offre.get("competences_requises", offre.get("required_skills", cv_transversales[:4])),
                    "salary_range": offre.get("salaire_indicatif", None),
                    "sector": offre.get("secteur", offre.get("sector", "Basé sur votre profil")),
                    "description": offre.get("description_courte", offre.get("description", "")),
                    "source": "cv_analysis",
                    "status": "active"
                })
            else:
                jobs.append({
                    "id": f"cv-suggestion-{i}",
                    "title": str(offre),
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


# NOTE: /jobs/apply and /jobs/applications MUST be defined BEFORE /jobs/{job_id}
# to avoid FastAPI matching "apply" or "applications" as a job_id

class ApplyRequest(BaseModel):
    job_title: str
    job_data: dict = {}
    motivation: str = ""


@router.post("/jobs/apply")
async def apply_to_job(token: str, request: ApplyRequest):
    """Submit an application for a job offer."""
    token_doc = await get_current_token(token)
    token_id = token_doc["id"]

    # Check if already applied to this exact job title
    existing = await db.job_applications.find_one(
        {"token_id": token_id, "job_title": request.job_title},
        {"_id": 0}
    )
    if existing:
        return {"already_applied": True, "application": existing, "message": "Vous avez déjà postulé à cette offre"}

    application = JobApplication(
        token_id=token_id,
        job_title=request.job_title,
        job_data=request.job_data,
        motivation=request.motivation,
    )
    await db.job_applications.insert_one(application.model_dump())
    return {"already_applied": False, "application": application.model_dump(), "message": "Candidature enregistrée avec succès"}


@router.get("/jobs/applications")
async def get_my_applications(token: str):
    """Get all applications for the current user."""
    token_doc = await get_current_token(token)
    apps = await db.job_applications.find(
        {"token_id": token_doc["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return apps


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
    from db import EMERGENT_LLM_KEY

    token_doc = await get_current_token(token)
    token_id = token_doc["id"]

    # Collect emerging competences from passport + CV
    emerging_skills = []
    user_skills = []
    career_project = ""
    professional_summary = ""

    passport = await db.passports.find_one({"token_id": token_id}, {"_id": 0})
    if passport:
        for c in passport.get("competences", []):
            name = c.get("name", "").strip()
            if name:
                user_skills.append(name)
                if c.get("is_emerging"):
                    emerging_skills.append(name)
        career_project = passport.get("career_project", "")
        professional_summary = passport.get("professional_summary", "")

    cv_job = await db.cv_jobs.find_one(
        {"token_id": token_id, "status": "completed"},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    cv_result = cv_job.get("result", {}) if cv_job else {}
    for comp in cv_result.get("competences_emergentes", []):
        if isinstance(comp, dict):
            name = comp.get("nom", comp.get("name", "")).strip()
        else:
            name = str(comp).strip()
        if name and name not in emerging_skills:
            emerging_skills.append(name)

    cv_skills = cv_result.get("competences_transversales", [])

    # Check if we already have personalized modules for this user
    personalized = await db.learning_modules_personalized.find(
        {"token_id": token_id}, {"_id": 0}
    ).to_list(20)

    # Regenerate if no personalized modules or emerging skills changed or profile has data but no personalized modules
    stored_emerging = set()
    for m in personalized:
        for es in m.get("emerging_match", []):
            stored_emerging.add(es.lower())
    current_emerging = set(e.lower() for e in emerging_skills)

    has_profile = bool(user_skills) or bool(cv_skills) or bool(professional_summary)
    needs_generation = (not personalized and has_profile) or (emerging_skills and current_emerging != stored_emerging)

    if needs_generation and EMERGENT_LLM_KEY:
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            import json as _json

            emerging_instruction = ""
            if emerging_skills:
                emerging_instruction = f"\nCOMPÉTENCES ÉMERGENTES À CIBLER EN PRIORITÉ: {', '.join(emerging_skills)}"
            else:
                emerging_instruction = "\nAucune compétence émergente détectée. Propose des formations adaptées au profil et au projet professionnel."

            context = f"""Profil:
- Compétences actuelles: {', '.join(user_skills[:15])}
- Compétences transversales CV: {', '.join(cv_skills[:10])}
- Résumé: {professional_summary[:200]}
- Projet: {career_project[:200]}
{emerging_instruction}"""

            system_msg = """Tu es un expert en ingénierie de formation en France.
Génère 8 modules de formation CONCRETS et PERTINENTS adaptés au profil."""
            if emerging_skills:
                system_msg += " Les 4 premiers DOIVENT cibler directement les compétences émergentes listées."
            else:
                system_msg += " Adapte chaque formation au profil, aux compétences et au projet professionnel de la personne."

            system_msg += """

Réponds UNIQUEMENT en JSON valide: un array de 8 objets:
{
  "title": "Titre concret de la formation",
  "description": "Description en 2 phrases max",
  "duration": "durée (ex: 12 heures, 3 jours)",
  "level": "Debutant|Intermediaire|Avance",
  "category": "catégorie courte",
  "skills_developed": ["comp1", "comp2", "comp3"],
  "emerging_match": ["nom exact de la compétence émergente ciblée, ou array vide si non applicable"],
  "provider": "organisme suggéré",
  "cpf_eligible": true/false
}"""

            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"learning-modules-{token_id[:8]}-{hash(tuple(user_skills[:5] + emerging_skills)) % 10000}",
                system_message=system_msg
            ).with_model("openai", "gpt-5.2")

            response = await chat.send_message(UserMessage(text=context))
            raw = response.strip() if isinstance(response, str) else response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]

            modules_data = _json.loads(raw.strip())
            if not isinstance(modules_data, list):
                modules_data = modules_data.get("modules", modules_data.get("formations", []))

            # Store personalized modules
            await db.learning_modules_personalized.delete_many({"token_id": token_id})
            for i, m in enumerate(modules_data[:8]):
                m["id"] = f"ai-module-{token_id[:8]}-{i}"
                m["token_id"] = token_id
                m["source"] = "ai_personalized"
            if modules_data:
                await db.learning_modules_personalized.insert_many([m for m in modules_data[:8]])
            personalized = modules_data[:8]
        except Exception as e:
            logging.error(f"Learning modules AI generation error: {e}")

    # Load progress
    progress_docs = await db.learning_progress.find({"token_id": token_id}, {"_id": 0}).to_list(100)
    progress_map = {p["module_id"]: p["progress"] for p in progress_docs}

    # Also load static modules as fallback
    static_modules = await db.learning_modules.find({}, {"_id": 0}).to_list(50)

    # Merge: personalized first, then static
    all_modules = []
    for m in personalized:
        m.pop("_id", None)
        m.pop("token_id", None)
        m["progress"] = progress_map.get(m.get("id", ""), 0)
        m["source"] = "ai_personalized"
        em = m.get("emerging_match", [])
        if isinstance(em, list) and em:
            m["relevance"] = "haute"
            m["relevance_score"] = 90
        else:
            m["relevance"] = "moyenne"
            m["relevance_score"] = 50
            m["emerging_match"] = []
        all_modules.append(m)

    for m in static_modules:
        m["progress"] = progress_map.get(m.get("id", ""), 0)
        m["source"] = "static"
        m["emerging_match"] = []
        m["relevance"] = "basse"
        m["relevance_score"] = 10
        all_modules.append(m)

    # Sort: emerging match first, then AI personalized, then by relevance
    all_modules.sort(key=lambda m: (
        -len(m.get("emerging_match", [])),
        -(m.get("source") == "ai_personalized"),
        -(m.get("progress", 0) > 0 and m.get("progress", 0) < 100),
        -m.get("relevance_score", 0)
    ))

    return all_modules


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
    emerging_competences = []
    career_project = ""
    professional_summary = ""
    experiences = []

    if passport:
        for c in passport.get("competences", []):
            name = c.get("name", "")
            if name:
                competences.append(name)
                if c.get("is_emerging"):
                    emerging_competences.append(name)
        career_project = passport.get("career_project", "")
        professional_summary = passport.get("professional_summary", "")
        experiences = [f"{e.get('title','')} - {e.get('company','')}" for e in passport.get("experiences", [])[:5]]

    cv_skills = []
    if cv_job and cv_job.get("result"):
        result = cv_job["result"]
        cv_skills = result.get("competences_transversales", [])
        for comp in result.get("competences_emergentes", []):
            if isinstance(comp, dict):
                name = comp.get("nom", comp.get("name", ""))
            else:
                name = str(comp)
            if name and name not in emerging_competences:
                emerging_competences.append(name)

    context = f"""Profil de la personne:
- Compétences: {', '.join(competences[:15])}
- Compétences transversales CV: {', '.join(cv_skills[:10])}
- Résumé professionnel: {professional_summary[:200]}
- Projet professionnel: {career_project[:200]}
- Expériences: {', '.join(experiences[:5])}

COMPÉTENCES ÉMERGENTES DÉTECTÉES (PRIORITÉ ABSOLUE):
{', '.join(emerging_competences) if emerging_competences else 'Aucune détectée'}

INSTRUCTION PRIORITAIRE: Les 3 premières formations recommandées DOIVENT cibler les compétences émergentes listées ci-dessus. Ces compétences sont en développement et nécessitent un renforcement prioritaire par la formation. Pour chaque formation liée à une compétence émergente, ajoute le champ "emerging_skills" avec la liste des compétences émergentes concernées."""

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
  "priority": "haute|moyenne|basse",
  "emerging_skills": ["compétence émergente ciblée si applicable, sinon array vide"]
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
