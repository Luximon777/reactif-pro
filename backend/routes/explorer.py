from fastapi import APIRouter, HTTPException
import asyncio
import uuid
import logging
from datetime import datetime, timezone
from db import db
from helpers import get_current_token, _llm_call_with_retry
from referentiel_data import REFERENTIEL_VERTUS, REFERENTIEL_VALEURS, REFERENTIEL_FILIERES, ARCHEOLOGIE_SAVOIR_ETRE

router = APIRouter()


@router.get("/referentiel/archeologie")
async def get_referentiel_archeologie():
    return {"vertus": REFERENTIEL_VERTUS, "valeurs": REFERENTIEL_VALEURS, "filieres": REFERENTIEL_FILIERES, "savoir_etre_map": ARCHEOLOGIE_SAVOIR_ETRE}


@router.get("/referentiel/filieres")
async def get_referentiel_filieres():
    return {"filieres": REFERENTIEL_FILIERES}


@router.get("/referentiel/vertus")
async def get_referentiel_vertus():
    return {"vertus": REFERENTIEL_VERTUS, "valeurs": REFERENTIEL_VALEURS}


@router.get("/referentiel/explorer")
async def get_explorer_filieres():
    all_data = await db.referentiel_metiers.find({}, {"_id": 0, "name": 1, "id": 1, "secteurs.name": 1, "secteurs.metiers.name": 1}).to_list(100)
    for f in all_data:
        for s in f.get("secteurs", []):
            metier_names = [m.get("name", "") for m in s.get("metiers", [])]
            s["metiers"] = metier_names
            s["metiers_count"] = len(metier_names)
    return {"filieres": all_data, "total_filieres": len(all_data)}


@router.get("/referentiel/explorer/secteur/{secteur_name}")
async def get_explorer_secteur(secteur_name: str):
    doc = await db.referentiel_metiers.find_one({"secteurs.name": secteur_name}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Secteur non trouvé")
    for s in doc.get("secteurs", []):
        if s["name"] == secteur_name:
            return {"filiere": doc["name"], "secteur": secteur_name, "metiers": s.get("metiers", [])}
    raise HTTPException(status_code=404, detail="Secteur non trouvé")


@router.get("/referentiel/explorer/metier/{metier_name}")
async def get_explorer_metier(metier_name: str):
    all_data = await db.referentiel_metiers.find({}, {"_id": 0}).to_list(100)
    found = None
    same_secteur_metiers = []
    for f in all_data:
        for s in f.get("secteurs", []):
            for m in s.get("metiers", []):
                if m["name"].lower() == metier_name.lower():
                    found = {"filiere": f["name"], "secteur": s["name"], "metier": m}
                    same_secteur_metiers = [om["name"] for om in s.get("metiers", []) if om["name"].lower() != metier_name.lower()]
    if not found:
        raise HTTPException(status_code=404, detail="Métier non trouvé")
    found["metiers_similaires"] = same_secteur_metiers
    return found


@router.get("/referentiel/explorer/search")
async def search_explorer(q: str):
    q_lower = q.lower()
    results = {"filieres": [], "secteurs": [], "metiers": [], "savoirs_faire": [], "savoirs_etre": []}
    all_data = await db.referentiel_metiers.find({}, {"_id": 0}).to_list(100)
    for f in all_data:
        if q_lower in f["name"].lower():
            results["filieres"].append({"name": f["name"], "type": "filiere"})
        for s in f.get("secteurs", []):
            if q_lower in s["name"].lower():
                results["secteurs"].append({"name": s["name"], "filiere": f["name"], "type": "secteur"})
            for m in s.get("metiers", []):
                if q_lower in m["name"].lower():
                    results["metiers"].append({"name": m["name"], "secteur": s["name"], "filiere": f["name"], "type": "metier"})
                for sf in m.get("savoirs_faire", []):
                    if q_lower in sf["name"].lower():
                        results["savoirs_faire"].append({"name": sf["name"], "metier": m["name"], "type": "savoir_faire"})
                for se in m.get("savoirs_etre", []):
                    if q_lower in se["name"].lower():
                        results["savoirs_etre"].append({"name": se["name"], "metier": m["name"], "type": "savoir_etre"})
    return results


@router.get("/referentiel/explorer/stats")
async def get_explorer_stats():
    all_data = await db.referentiel_metiers.find({}, {"_id": 0}).to_list(100)
    n_filieres = len(all_data)
    n_secteurs = sum(len(f.get("secteurs", [])) for f in all_data)
    n_metiers = sum(len(m.get("metiers", [])) for f in all_data for m in f.get("secteurs", []))
    sf_set = set()
    se_set = set()
    for f in all_data:
        for s in f.get("secteurs", []):
            for m in s.get("metiers", []):
                for sf in m.get("savoirs_faire", []):
                    sf_set.add(sf["name"])
                for se in m.get("savoirs_etre", []):
                    se_set.add(se["name"])
    return {"filieres": n_filieres, "secteurs": n_secteurs, "metiers": n_metiers, "savoirs_faire": len(sf_set), "savoirs_etre": len(se_set)}


@router.post("/referentiel/explorer/generate")
async def generate_metier_fiche(token: str, payload: dict):
    await get_current_token(token)
    metier_name = payload.get("metier", "").strip()
    if not metier_name or len(metier_name) < 2:
        raise HTTPException(status_code=400, detail="Nom de métier invalide")
    cached = await db.generated_metiers.find_one({"name_lower": metier_name.lower()}, {"_id": 0})
    if cached:
        return cached["data"]
    job_id = str(uuid.uuid4())
    await db.explorer_jobs.insert_one({"job_id": job_id, "metier": metier_name, "status": "started", "created_at": datetime.now(timezone.utc).isoformat()})
    asyncio.create_task(_generate_metier_fiche(job_id, metier_name))
    return {"job_id": job_id, "status": "started"}


@router.get("/referentiel/explorer/generate/status")
async def get_generate_status(token: str, job_id: str):
    await get_current_token(token)
    job = await db.explorer_jobs.find_one({"job_id": job_id}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job non trouvé")
    return {"job_id": job["job_id"], "status": job["status"], "result": job.get("result"), "error": job.get("error")}


async def _generate_metier_fiche(job_id: str, metier_name: str):
    try:
        await db.explorer_jobs.update_one({"job_id": job_id}, {"$set": {"status": "generating"}})
        result = await _llm_call_with_retry(
            system_msg="""Tu es un expert en référentiels métiers et en archéologie des compétences.
Pour le métier demandé, génère une fiche complète en JSON valide:
{
  "filiere": "nom de la filière professionnelle",
  "secteur": "secteur d'activité",
  "metier": {
    "name": "nom du métier",
    "mission": "description détaillée de la mission (2-3 phrases)",
    "savoirs_faire": [
      {"name": "savoir-faire", "capacite_technique": "description de la capacité technique associée"}
    ],
    "savoirs_etre": [
      {"name": "savoir-être", "capacite_professionnelle": "description de la capacité professionnelle", "qualites_humaines": ["qualité1"], "valeurs": ["id_valeur"], "vertus": ["id_vertu"]}
    ]
  },
  "metiers_similaires": ["métier1", "métier2", "métier3", "métier4", "métier5"]
}
Règles:
- 6 à 10 savoir-faire avec capacités techniques détaillées
- 5 à 8 savoir-être avec la chaîne complète (capacité pro -> qualités -> valeurs -> vertus)
- 5 métiers similaires dans le même secteur
- IDs valeurs: autonomie, stimulation, hedonisme, realisation_de_soi, pouvoir, securite, conformite, tradition, bienveillance, universalisme
- IDs vertus: sagesse, courage, humanite, justice, temperance, transcendance""",
            user_msg=f"Génère la fiche métier complète pour : {metier_name}"
        )
        await db.generated_metiers.update_one({"name_lower": metier_name.lower()}, {"$set": {"name_lower": metier_name.lower(), "data": result, "created_at": datetime.now(timezone.utc).isoformat()}}, upsert=True)
        await db.explorer_jobs.update_one({"job_id": job_id}, {"$set": {"status": "completed", "result": result}})
    except Exception as e:
        logging.error(f"Metier generation failed: {e}")
        await db.explorer_jobs.update_one({"job_id": job_id}, {"$set": {"status": "failed", "error": str(e)}})
