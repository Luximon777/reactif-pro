from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
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
    token_doc = await get_current_token(token)
    token_id = token_doc["id"]
    profile = await db.profiles.find_one({"token_id": token_id}, {"_id": 0})

    # Enrich user data from multiple sources: profile + passport + CV analysis
    user_sectors = set()
    user_skills = set()

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

    user_skills_list = list(user_skills)
    user_sectors_list = list(user_sectors)

    # If no data, try to match all job indices
    relevant_jobs = []
    if user_sectors_list:
        for sector in user_sectors_list:
            jobs = await db.job_evolution_indices.find({"sector": {"$regex": sector, "$options": "i"}}, {"_id": 0}).to_list(20)
            relevant_jobs.extend(jobs)
    else:
        # Fallback: use all jobs for general view
        relevant_jobs = await db.job_evolution_indices.find({}, {"_id": 0}).to_list(20)

    # Deduplicate jobs by name
    seen_jobs = set()
    unique_jobs = []
    for job in relevant_jobs:
        if job.get("job_name") not in seen_jobs:
            seen_jobs.add(job.get("job_name"))
            unique_jobs.append(job)
    relevant_jobs = unique_jobs

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

    # Fetch emerging competences detected from CV
    cv_emerging = await db.emerging_competences.find({"token_id": token_id}, {"_id": 0}).to_list(20)
    emerging_from_cv = [
        {"name": ec.get("nom_principal"), "score": ec.get("score_emergence", 0),
         "level": ec.get("niveau_emergence"), "sectors": ec.get("secteurs_porteurs", [])}
        for ec in cv_emerging
    ]

    avg_exposure = sum(j.get("evolution_index", 0) for j in relevant_jobs) / len(relevant_jobs) if relevant_jobs else 50

    has_cv = bool(cv_job)
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
