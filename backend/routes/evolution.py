from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import hashlib
from db import db
from helpers import get_current_token

router = APIRouter()


def calculate_index_level(index: float) -> str:
    if index < 20: return "stable"
    elif index < 50: return "evolutif"
    elif index < 80: return "en_transformation"
    else: return "forte_mutation"


def get_index_interpretation(index: float, job_name: str = None) -> Dict[str, Any]:
    if index < 20:
        return {"level": "stable", "label": "Métier très stable", "description": "Les compétences de ce métier évoluent peu. La formation initiale reste pertinente sur le long terme.", "color": "emerald", "recommendation": "Maintenez vos compétences actuelles et restez en veille sur les évolutions du secteur."}
    elif index < 50:
        return {"level": "evolutif", "label": "Métier évolutif", "description": "Ce métier connaît des évolutions modérées. Certaines compétences nouvelles apparaissent progressivement.", "color": "blue", "recommendation": "Renforcez vos compétences numériques et suivez une formation continue régulière."}
    elif index < 80:
        return {"level": "en_transformation", "label": "Métier en transformation", "description": "Ce métier évolue significativement sous l'effet des innovations technologiques ou organisationnelles.", "color": "amber", "recommendation": "Anticipez les changements en développant les compétences émergentes de votre secteur."}
    else:
        return {"level": "forte_mutation", "label": "Forte mutation", "description": "Ce métier est fortement impacté par les transformations. Une adaptation rapide est nécessaire.", "color": "rose", "recommendation": "Envisagez une montée en compétences significative ou une reconversion vers des métiers connexes."}


@router.get("/evolution-index/jobs")
async def get_jobs_evolution_index(sector: Optional[str] = None):
    query = {}
    if sector: query["sector"] = sector
    indices = await db.job_evolution_indices.find(query, {"_id": 0}).to_list(100)
    for idx in indices:
        idx["interpretation"] = get_index_interpretation(idx.get("evolution_index", 0), idx.get("job_name"))
    return sorted(indices, key=lambda x: x.get("evolution_index", 0), reverse=True)


@router.get("/evolution-index/jobs/{job_name}")
async def get_job_evolution_detail(job_name: str):
    index = await db.job_evolution_indices.find_one({"job_name": {"$regex": job_name, "$options": "i"}}, {"_id": 0})
    if not index:
        raise HTTPException(status_code=404, detail="Métier non trouvé")
    index["interpretation"] = get_index_interpretation(index.get("evolution_index", 0), job_name)
    related_skills = await db.emerging_skills.find({"related_jobs": {"$regex": job_name, "$options": "i"}}, {"_id": 0}).to_list(10)
    index["related_emerging_skills"] = related_skills
    return index


@router.get("/evolution-index/sectors")
async def get_sectors_evolution_index():
    indices = await db.sector_evolution_indices.find({}, {"_id": 0}).to_list(50)
    for idx in indices:
        idx["interpretation"] = get_index_interpretation(idx.get("evolution_index", 0))
    return sorted(indices, key=lambda x: x.get("evolution_index", 0), reverse=True)


@router.get("/evolution-index/sectors/{sector_name}")
async def get_sector_evolution_detail(sector_name: str):
    index = await db.sector_evolution_indices.find_one({"sector_name": {"$regex": sector_name, "$options": "i"}}, {"_id": 0})
    if not index:
        raise HTTPException(status_code=404, detail="Secteur non trouvé")
    index["interpretation"] = get_index_interpretation(index.get("evolution_index", 0))
    jobs = await db.job_evolution_indices.find({"sector": {"$regex": sector_name, "$options": "i"}}, {"_id": 0}).to_list(50)
    index["jobs"] = jobs
    return index


@router.get("/evolution-index/dashboard")
async def get_evolution_dashboard():
    job_indices = await db.job_evolution_indices.find({}, {"_id": 0}).to_list(100)
    sector_indices = await db.sector_evolution_indices.find({}, {"_id": 0}).to_list(50)
    total_jobs = len(job_indices)
    jobs_stable = len([j for j in job_indices if j.get("evolution_index", 0) < 20])
    jobs_evolving = len([j for j in job_indices if 20 <= j.get("evolution_index", 0) < 50])
    jobs_transforming = len([j for j in job_indices if 50 <= j.get("evolution_index", 0) < 80])
    jobs_highly_impacted = len([j for j in job_indices if j.get("evolution_index", 0) >= 80])
    avg_job_index = sum(j.get("evolution_index", 0) for j in job_indices) / max(total_jobs, 1)
    avg_sector_index = sum(s.get("evolution_index", 0) for s in sector_indices) / max(len(sector_indices), 1)
    top_transforming = sorted(job_indices, key=lambda x: x.get("evolution_index", 0), reverse=True)[:5]
    most_stable = sorted(job_indices, key=lambda x: x.get("evolution_index", 0))[:5]
    for sector in sector_indices:
        sector["interpretation"] = get_index_interpretation(sector.get("evolution_index", 0))
    return {
        "summary": {"total_jobs_analyzed": total_jobs, "total_sectors_analyzed": len(sector_indices), "average_job_evolution_index": round(avg_job_index, 1), "average_sector_evolution_index": round(avg_sector_index, 1)},
        "distribution": {"stable": {"count": jobs_stable, "percentage": round(jobs_stable / max(total_jobs, 1) * 100, 1)}, "evolving": {"count": jobs_evolving, "percentage": round(jobs_evolving / max(total_jobs, 1) * 100, 1)}, "transforming": {"count": jobs_transforming, "percentage": round(jobs_transforming / max(total_jobs, 1) * 100, 1)}, "highly_impacted": {"count": jobs_highly_impacted, "percentage": round(jobs_highly_impacted / max(total_jobs, 1) * 100, 1)}},
        "top_transforming_jobs": top_transforming, "most_stable_jobs": most_stable, "sectors": sector_indices,
        "interpretation_guide": {"stable": {"range": "0-20", "description": "Métier très stable, évolution lente"}, "evolutif": {"range": "20-50", "description": "Métier évolutif mais relativement stable"}, "en_transformation": {"range": "50-80", "description": "Métier en transformation importante"}, "forte_mutation": {"range": "80-100", "description": "Métier fortement impacté par les innovations"}}
    }


@router.get("/evolution-index/user-profile")
async def get_user_evolution_analysis(token: str):
    from db import EMERGENT_LLM_KEY

    token_doc = await get_current_token(token)
    token_id = token_doc["id"]
    profile = await db.profiles.find_one({"token_id": token_id}, {"_id": 0})

    # Enrich user data from multiple sources: profile + passport + CV analysis
    user_sectors = set()
    user_skills = set()
    user_title = ""

    if profile:
        for s in profile.get("sectors", []):
            if s:
                user_sectors.add(s)
        for sk in profile.get("skills", []):
            name = sk.get("name", "")
            if name:
                user_skills.add(name)

    # Pull from passport (richer data from CV analysis)
    passport = await db.passports.find_one({"token_id": token_id}, {"_id": 0})
    if passport:
        for c in passport.get("competences", []):
            name = c.get("name", "")
            if name:
                user_skills.add(name)
        for s in passport.get("target_sectors", []):
            if s:
                user_sectors.add(s)

    # Pull from latest CV analysis
    cv_job = await db.cv_jobs.find_one(
        {"token_id": token_id, "status": "completed"},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    cv_result = cv_job.get("result", {}) if cv_job else {}
    for t in cv_result.get("competences_transversales", []):
        if t:
            user_skills.add(t)

    # Pull from optimized CV (richer data with competences_cles, savoir_faire)
    cv_optimized = await db.cv_models.find_one({"token_id": token_id}, {"_id": 0})
    if cv_optimized and cv_optimized.get("models"):
        for model_data in cv_optimized["models"].values():
            if isinstance(model_data, dict):
                user_title = model_data.get("titre", "")
                for ck in model_data.get("competences_cles", []):
                    if isinstance(ck, str) and ck.strip():
                        user_skills.add(ck)
                for sf in model_data.get("savoir_faire", []):
                    name = sf.get("name", "") if isinstance(sf, dict) else sf
                    if name:
                        user_skills.add(str(name))
                break

    # Also try to get title from raw CV
    if not user_title and cv_result:
        user_title = cv_result.get("titre_profil_suggere", "")
    # Also try from experiences
    if not user_title and cv_result:
        exps = cv_result.get("experiences", [])
        if exps and isinstance(exps[0], dict):
            user_title = exps[0].get("title", "") or exps[0].get("poste", "")
    # Last resort: filename
    if not user_title and cv_job:
        fn = cv_job.get("filename", "")
        if fn:
            user_title = fn.replace(".pdf", "").replace(".docx", "").replace(".txt", "").replace("_", " ")

    user_skills_list = list(user_skills)
    user_sectors_list = list(user_sectors)

    # Try to find matching job indices in DB
    relevant_jobs = []
    if user_sectors_list:
        for sector in user_sectors_list:
            jobs = await db.job_evolution_indices.find({"sector": {"$regex": sector, "$options": "i"}}, {"_id": 0}).to_list(20)
            relevant_jobs.extend(jobs)

    # Deduplicate jobs by name
    seen_jobs = set()
    unique_jobs = []
    for job in relevant_jobs:
        if job.get("job_name") not in seen_jobs:
            seen_jobs.add(job.get("job_name"))
            unique_jobs.append(job)
    relevant_jobs = unique_jobs

    # Fetch emerging competences detected from CV
    cv_emerging = await db.emerging_competences.find({"token_id": token_id}, {"_id": 0}).to_list(20)
    emerging_from_cv = [
        {"name": ec.get("nom_principal"), "score": ec.get("score_emergence", 0),
         "level": ec.get("niveau_emergence"), "sectors": ec.get("secteurs_porteurs", [])}
        for ec in cv_emerging
    ]

    has_cv = bool(cv_job)

    # If we have a CV but no matching job indices, generate personalized analysis via AI
    if has_cv and (not relevant_jobs or len(relevant_jobs) < 2) and EMERGENT_LLM_KEY and user_skills:
        # Check cache with skills hash to auto-invalidate when profile changes
        skills_hash = hashlib.md5((user_title + "|" + "|".join(sorted(user_skills_list))).encode()).hexdigest()[:12]
        cached = await db.evolution_cache.find_one({"token_id": token_id}, {"_id": 0})
        if cached and cached.get("ai_analysis") and cached.get("skills_hash") == skills_hash:
            ai_analysis = cached["ai_analysis"]
        else:
            ai_analysis = await _generate_evolution_analysis_ai(
                user_title, user_skills_list, user_sectors_list, EMERGENT_LLM_KEY, token_id
            )
            if ai_analysis:
                await db.evolution_cache.update_one(
                    {"token_id": token_id},
                    {"$set": {"token_id": token_id, "ai_analysis": ai_analysis, "user_title": user_title, "skills_hash": skills_hash, "updated_at": datetime.now(timezone.utc).isoformat()}},
                    upsert=True
                )
        if ai_analysis:
            return {
                "has_cv": True,
                "profile_sectors": user_sectors_list,
                "profile_skills": user_skills_list,
                "user_title": user_title,
                "analysis_summary": ai_analysis.get("analysis_summary", ""),
                "evolution_exposure": ai_analysis.get("evolution_exposure", 50),
                "exposure_interpretation": get_index_interpretation(ai_analysis.get("evolution_exposure", 50)),
                "relevant_jobs": ai_analysis.get("relevant_jobs", [])[:5],
                "skills_at_risk": ai_analysis.get("skills_at_risk", []),
                "skills_in_demand": ai_analysis.get("skills_in_demand", []),
                "recommended_skills_to_acquire": ai_analysis.get("recommended_skills_to_acquire", [])[:10],
                "recommended_trainings": ai_analysis.get("recommended_trainings", [])[:5],
                "emerging_from_cv": emerging_from_cv,
                "data_sources": {
                    "profile": bool(profile and profile.get("skills")),
                    "passport": bool(passport and passport.get("competences")),
                    "cv_analysis": True
                }
            }

    # Standard path with DB data
    skills_at_risk = []
    skills_in_demand = []
    user_skills_lower = {s.lower() for s in user_skills}
    for job in relevant_jobs:
        for skill in job.get("declining_skills", []):
            if skill.lower() in user_skills_lower:
                skills_at_risk.append({"skill": skill, "job": job["job_name"]})
        for skill in job.get("emerging_skills", []):
            if skill.lower() in user_skills_lower:
                skills_in_demand.append({"skill": skill, "job": job["job_name"]})

    all_recommended = set()
    for job in relevant_jobs:
        all_recommended.update(job.get("recommended_skills", []))

    avg_exposure = sum(j.get("evolution_index", 0) for j in relevant_jobs) / len(relevant_jobs) if relevant_jobs else 50

    return {
        "has_cv": has_cv,
        "profile_sectors": user_sectors_list, "profile_skills": user_skills_list,
        "evolution_exposure": round(avg_exposure, 1),
        "exposure_interpretation": get_index_interpretation(avg_exposure),
        "relevant_jobs": relevant_jobs[:5],
        "skills_at_risk": skills_at_risk, "skills_in_demand": skills_in_demand,
        "recommended_skills_to_acquire": list(all_recommended - user_skills)[:10],
        "recommended_trainings": list(set(t for j in relevant_jobs for t in j.get("recommended_trainings", [])))[:5],
        "emerging_from_cv": emerging_from_cv,
        "data_sources": {
            "profile": bool(profile and profile.get("skills")),
            "passport": bool(passport and passport.get("competences")),
            "cv_analysis": has_cv
        }
    }


@router.post("/evolution-index/refresh")
async def refresh_evolution_analysis(token: str):
    """Force refresh the cached evolution analysis."""
    token_doc = await get_current_token(token)
    token_id = token_doc["id"]
    await db.evolution_cache.delete_one({"token_id": token_id})
    return {"message": "Cache rafraîchi. Rechargez la page pour obtenir une nouvelle analyse."}



async def _generate_evolution_analysis_ai(user_title, user_skills, user_sectors, api_key, token_id):
    """Generate a personalized evolution analysis using AI when no DB data matches."""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    import json as _json
    import logging

    skills_str = ", ".join(user_skills[:30])
    sectors_str = ", ".join(user_sectors[:5]) if user_sectors else "non renseign\u00e9"
    title_display = user_title if user_title else "Profil polyvalent (titre non d\u00e9tect\u00e9)"

    context = f"""PROFIL PROFESSIONNEL \u00c0 ANALYSER (donn\u00e9es extraites du CV r\u00e9el de l'utilisateur) :

M\u00c9TIER / TITRE ACTUEL : {title_display}
COMP\u00c9TENCES DU CV (liste exacte) : {skills_str}
SECTEURS D'ACTIVIT\u00c9 : {sectors_str}

CONSIGNES STRICTES :
1. Ton analyse DOIT \u00eatre 100% centr\u00e9e sur le m\u00e9tier "{title_display}" et les {len(user_skills)} comp\u00e9tences list\u00e9es ci-dessus.
2. Dans "skills_at_risk", utilise UNIQUEMENT des comp\u00e9tences pr\u00e9sentes dans la liste ci-dessus qui sont en d\u00e9clin sur le march\u00e9.
3. Dans "skills_in_demand", utilise UNIQUEMENT des comp\u00e9tences pr\u00e9sentes dans la liste ci-dessus qui sont recherch\u00e9es.
4. Les "recommended_skills_to_acquire" doivent \u00eatre des comp\u00e9tences NOUVELLES (absentes du CV) mais directement li\u00e9es au m\u00e9tier "{title_display}".
5. Les "relevant_jobs" doivent \u00eatre des m\u00e9tiers accessibles depuis le profil actuel (passerelles r\u00e9alistes).
6. Les formations recommand\u00e9es doivent \u00eatre des formations r\u00e9elles disponibles en France (CPF, universit\u00e9s, organismes).
7. NE G\u00c9N\u00c8RE PAS de contenu g\u00e9n\u00e9rique sans lien avec ce profil sp\u00e9cifique."""

    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f"evolution-{token_id[:8]}",
            system_message="""Tu es un expert en prospective des m\u00e9tiers et \u00e9volution des comp\u00e9tences sur le march\u00e9 du travail fran\u00e7ais.
Tu re\u00e7ois un profil professionnel r\u00e9el extrait d'un CV. Tu dois produire une analyse d'\u00e9volution ENTI\u00c8REMENT personnalis\u00e9e.

\u00c9value sur 0-100 la vitesse \u00e0 laquelle les comp\u00e9tences de ce profil sp\u00e9cifique \u00e9voluent :
- 0-20 : Tr\u00e8s stable (comp\u00e9tences p\u00e9rennes, peu d'obsolescence)
- 20-50 : \u00c9volutif (adaptations progressives n\u00e9cessaires)
- 50-80 : En transformation (requ\u00e9rant une mont\u00e9e en comp\u00e9tences significative)
- 80-100 : Forte mutation (reconversion ou formation lourde n\u00e9cessaire)

R\u00e8gles ABSOLUES :
- "skills_at_risk" et "skills_in_demand" ne doivent contenir QUE des comp\u00e9tences qui existent dans le CV du candidat.
- "recommended_skills_to_acquire" ne doit contenir QUE des comp\u00e9tences ABSENTES du CV mais pertinentes pour l'\u00e9volution du m\u00e9tier.
- Les m\u00e9tiers propos\u00e9s dans "relevant_jobs" doivent \u00eatre accessibles avec les comp\u00e9tences actuelles + une formation compl\u00e9mentaire raisonnable.
- Base-toi sur les vraies tendances du march\u00e9 fran\u00e7ais 2025-2026 (IA, num\u00e9rique, transition \u00e9cologique, sant\u00e9, etc.)

R\u00e9ponds UNIQUEMENT en JSON valide (sans commentaires, sans markdown) :
{
  "evolution_exposure": 55,
  "analysis_summary": "R\u00e9sum\u00e9 en 2-3 phrases de l'analyse personnalis\u00e9e",
  "skills_at_risk": [
    {"skill": "comp\u00e9tence exacte du CV en d\u00e9clin", "job": "m\u00e9tier concern\u00e9", "reason": "raison courte"}
  ],
  "skills_in_demand": [
    {"skill": "comp\u00e9tence exacte du CV recherch\u00e9e", "job": "m\u00e9tier concern\u00e9", "reason": "raison courte"}
  ],
  "recommended_skills_to_acquire": ["comp\u00e9tence nouvelle 1", "comp\u00e9tence nouvelle 2"],
  "recommended_trainings": ["Formation 1 (organisme)", "Formation 2 (organisme)"],
  "relevant_jobs": [
    {
      "job_name": "M\u00e9tier proche",
      "sector": "Secteur",
      "evolution_index": 60,
      "emerging_skills": ["skill1", "skill2"],
      "declining_skills": ["old skill"],
      "stable_skills": ["stable1", "stable2"],
      "recommended_skills": ["rec1"],
      "recommended_trainings": ["formation1"],
      "job_passerelles": ["m\u00e9tier passerelle 1"]
    }
  ]
}"""
        ).with_model("openai", "gpt-5.2")

        response = await chat.send_message(UserMessage(text=context))
        raw = response.strip() if isinstance(response, str) else response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]

        return _json.loads(raw.strip())
    except Exception as e:
        logging.error(f"Evolution AI analysis error: {e}")
        return None
