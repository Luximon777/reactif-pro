from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime, timezone
from models import JobOffer, Beneficiary, CreateJobRequest
from db import db
from helpers import get_current_token, calculate_match_with_ai

router = APIRouter()


@router.get("/jobs")
async def get_jobs(token: str, limit: int = 20):
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    jobs = await db.jobs.find({"status": "active"}, {"_id": 0}).to_list(limit)
    if profile and profile.get("skills"):
        profile_skill_names = [s.get("name", "") for s in profile.get("skills", [])]
        for job in jobs:
            common = set(profile_skill_names) & set(job.get("required_skills", []))
            job["match_score"] = min(100, int((len(common) / max(len(job.get("required_skills", [])), 1)) * 100) + 25)
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
    modules = await db.learning_modules.find({}, {"_id": 0}).to_list(50)
    progress_docs = await db.learning_progress.find({"token_id": token_doc["id"]}, {"_id": 0}).to_list(100)
    progress_map = {p["module_id"]: p["progress"] for p in progress_docs}
    for module in modules:
        module["progress"] = progress_map.get(module["id"], 0)
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
