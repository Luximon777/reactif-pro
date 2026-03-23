from fastapi import APIRouter, HTTPException
import asyncio
import csv
import os
import re
import uuid
import logging
from datetime import datetime, timezone
from db import db
from helpers import get_current_token, _llm_call_with_retry
from referentiel_data import REFERENTIEL_VERTUS, REFERENTIEL_VALEURS, REFERENTIEL_FILIERES, ARCHEOLOGIE_SAVOIR_ETRE

router = APIRouter()

# ISCO groups for human-readable labels
ISCO_GROUPS = {
    "0": "Forces armées", "01": "Officiers", "02": "Sous-officiers", "03": "Autres membres",
    "1": "Directeurs, cadres de direction et gérants",
    "2": "Professions intellectuelles et scientifiques",
    "3": "Professions intermédiaires",
    "4": "Employés de type administratif",
    "5": "Personnel des services directs aux particuliers, commerçants et vendeurs",
    "6": "Agriculteurs et ouvriers qualifiés de l'agriculture, de la sylviculture et de la pêche",
    "7": "Métiers qualifiés de l'industrie et de l'artisanat",
    "8": "Conducteurs d'installations et de machines, et ouvriers de l'assemblage",
    "9": "Professions élémentaires",
}


def _normalize_isco(text: str) -> str:
    """Normalisation INSEE pour la codification ISCO."""
    s = text.lower()
    for old, new in [('-à-', 'a'), ('à', 'a'), ('â', 'a'), ('é', 'e'), ('è', 'e'),
                     ('ê', 'e'), ('ë', 'e'), ('ï', 'i'), ('î', 'i'), ('û', 'u'),
                     ('ù', 'u'), ('ü', 'u'), ('ô', 'o'), ('ç', 'c'), ('œ', 'oe'),
                     ('(', ' '), (')', ' '), ('/', ' '), ('-', ''), (',', ' '),
                     ("'", ' '), ('\u2019', ' '), ('.', ' ')]:
        s = s.replace(old, new)
    for stop in [' dans ', ' en ', ' de ', ' sur ', ' aux ', ' au ', ' des ', ' d ',
                 ' l ', ' a ', ' un ', ' une ', ' du ', ' et ', ' la ', ' le ',
                 ' ou ', ' pour ', ' avec ', ' chez ', ' par ', ' les ']:
        s = s.replace(stop, ' ')
    s = re.sub(r'\s+', '', s).upper()
    return s


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

    # Lookup ISCO code
    normalized = _normalize_isco(metier_name)
    isco_doc = await db.isco_metiers.find_one({"$or": [
        {"sgnm": normalized}, {"sgnf": normalized},
        {"libm": {"$regex": f"^{re.escape(metier_name)}$", "$options": "i"}},
    ]}, {"_id": 0})
    if isco_doc:
        found["code_isco"] = isco_doc["code_isco"]
        found["isco_info"] = {"code": isco_doc["code_isco"], "libelle_m": isco_doc["libm"], "libelle_f": isco_doc.get("libf", ""), "groupe": isco_doc.get("groupe_isco", "")}

    return found


@router.get("/referentiel/explorer/search")
async def search_explorer(q: str):
    q_lower = q.lower()
    q_normalized = _normalize_isco(q)
    results = {"filieres": [], "secteurs": [], "metiers": [], "savoirs_faire": [], "savoirs_etre": []}

    # 1) Search in existing referentiel_metiers
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

    # 2) Search in ISCO database (5852 job titles)
    existing_names = {m["name"].lower() for m in results["metiers"]}
    isco_query = {"$or": [
        {"libm": {"$regex": q, "$options": "i"}},
        {"libf": {"$regex": q, "$options": "i"}},
        {"sgnm": {"$regex": q_normalized}},
        {"sgnf": {"$regex": q_normalized}},
    ]}
    isco_results = await db.isco_metiers.find(isco_query, {"_id": 0}).to_list(20)
    for r in isco_results:
        name = r.get("libm", "")
        if name.lower() not in existing_names:
            existing_names.add(name.lower())
            isco_group = ISCO_GROUPS.get(r.get("code_isco", "")[:1], "")
            results["metiers"].append({
                "name": name,
                "name_f": r.get("libf", ""),
                "type": "metier",
                "source": "isco",
                "code_isco": r.get("code_isco", ""),
                "groupe_isco": isco_group,
            })

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
    isco_count = await db.isco_metiers.count_documents({})
    isco_codes = len(await db.isco_metiers.distinct("code_isco"))
    return {
        "filieres": n_filieres, "secteurs": n_secteurs, "metiers": n_metiers,
        "savoirs_faire": len(sf_set), "savoirs_etre": len(se_set),
        "isco_metiers": isco_count, "isco_codes": isco_codes
    }


@router.post("/referentiel/isco/import")
async def import_isco_matrix():
    """Import the INSEE ISCO coding matrix into MongoDB."""
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "isco_matrix.csv")
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Fichier isco_matrix.csv non trouvé")

    existing = await db.isco_metiers.count_documents({})
    if existing > 5000:
        return {"message": f"Base ISCO déjà importée ({existing} entrées)", "count": existing}

    await db.isco_metiers.delete_many({})

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        batch = []
        skipped = 0
        for row in reader:
            libm = row.get("libm", "").strip()
            code = row.get("ssvaran", "").strip()
            if not libm or not code or code == "ISCO" or len(code) != 4:
                skipped += 1
                continue
            batch.append({
                "libm": libm,
                "libf": row.get("libf", "").strip(),
                "code_isco": code,
                "code_unique": row.get("codeu", "").strip(),
                "sgnm": row.get("sgnm", "").strip(),
                "sgnf": row.get("sgnf", "").strip(),
                "liste": row.get("liste", ""),
                "groupe_isco": ISCO_GROUPS.get(code[:1], ""),
            })
            if len(batch) >= 500:
                await db.isco_metiers.insert_many(batch)
                batch = []
        if batch:
            await db.isco_metiers.insert_many(batch)

    # Create indexes for search performance
    await db.isco_metiers.create_index("libm")
    await db.isco_metiers.create_index("libf")
    await db.isco_metiers.create_index("sgnm")
    await db.isco_metiers.create_index("sgnf")
    await db.isco_metiers.create_index("code_isco")

    total = await db.isco_metiers.count_documents({})
    codes = len(await db.isco_metiers.distinct("code_isco"))
    return {"message": "Import ISCO terminé", "total_metiers": total, "codes_isco_uniques": codes, "skipped": skipped}


@router.get("/referentiel/isco/lookup")
async def lookup_isco_code(metier: str):
    """Look up the ISCO code for a job title."""
    normalized = _normalize_isco(metier)
    # Try exact normalized match first
    doc = await db.isco_metiers.find_one({"$or": [{"sgnm": normalized}, {"sgnf": normalized}]}, {"_id": 0})
    if doc:
        return {"found": True, "code_isco": doc["code_isco"], "libelle_m": doc["libm"], "libelle_f": doc["libf"], "groupe": doc.get("groupe_isco", "")}

    # Try case-insensitive match on original labels
    doc = await db.isco_metiers.find_one({"$or": [
        {"libm": {"$regex": f"^{re.escape(metier)}$", "$options": "i"}},
        {"libf": {"$regex": f"^{re.escape(metier)}$", "$options": "i"}},
    ]}, {"_id": 0})
    if doc:
        return {"found": True, "code_isco": doc["code_isco"], "libelle_m": doc["libm"], "libelle_f": doc["libf"], "groupe": doc.get("groupe_isco", "")}

    # Partial match
    doc = await db.isco_metiers.find_one({"$or": [
        {"libm": {"$regex": re.escape(metier), "$options": "i"}},
        {"libf": {"$regex": re.escape(metier), "$options": "i"}},
    ]}, {"_id": 0})
    if doc:
        return {"found": True, "code_isco": doc["code_isco"], "libelle_m": doc["libm"], "libelle_f": doc["libf"], "groupe": doc.get("groupe_isco", ""), "partial": True}

    return {"found": False, "message": "Code ISCO non trouvé pour ce libellé"}


@router.get("/referentiel/isco/stats")
async def get_isco_stats():
    """Get statistics about the ISCO database."""
    total = await db.isco_metiers.count_documents({})
    if total == 0:
        return {"imported": False, "total": 0}
    codes = await db.isco_metiers.distinct("code_isco")
    # Group by major group (first digit)
    pipeline = [
        {"$group": {"_id": {"$substr": ["$code_isco", 0, 1]}, "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    groups = await db.isco_metiers.aggregate(pipeline).to_list(20)
    return {
        "imported": True, "total": total, "codes_uniques": len(codes),
        "groupes": [{
            "code": g["_id"], "label": ISCO_GROUPS.get(g["_id"], ""), "count": g["count"]
        } for g in groups]
    }


@router.post("/referentiel/explorer/generate")
async def generate_metier_fiche(token: str, payload: dict):
    await get_current_token(token)
    metier_name = payload.get("metier", "").strip()
    if not metier_name or len(metier_name) < 2:
        raise HTTPException(status_code=400, detail="Nom de métier invalide")
    cached = await db.generated_metiers.find_one({"name_lower": metier_name.lower()}, {"_id": 0})
    if cached:
        data = cached["data"]
        # Enrich with ISCO code if not already present
        if not data.get("code_isco"):
            normalized = _normalize_isco(metier_name)
            isco_doc = await db.isco_metiers.find_one({"$or": [
                {"sgnm": normalized}, {"sgnf": normalized},
                {"libm": {"$regex": f"^{re.escape(metier_name)}$", "$options": "i"}},
                {"libf": {"$regex": f"^{re.escape(metier_name)}$", "$options": "i"}},
            ]}, {"_id": 0})
            if isco_doc:
                data["code_isco"] = isco_doc["code_isco"]
                data["isco_info"] = {"code": isco_doc["code_isco"], "libelle_m": isco_doc["libm"], "libelle_f": isco_doc.get("libf", ""), "groupe": isco_doc.get("groupe_isco", "")}
        return data
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

        # Lookup ISCO code for this job title
        isco_info = None
        normalized = _normalize_isco(metier_name)
        isco_doc = await db.isco_metiers.find_one({"$or": [
            {"sgnm": normalized}, {"sgnf": normalized},
            {"libm": {"$regex": f"^{re.escape(metier_name)}$", "$options": "i"}},
            {"libf": {"$regex": f"^{re.escape(metier_name)}$", "$options": "i"}},
        ]}, {"_id": 0})
        if isco_doc:
            isco_info = {"code": isco_doc["code_isco"], "libelle_m": isco_doc["libm"], "libelle_f": isco_doc.get("libf", ""), "groupe": isco_doc.get("groupe_isco", "")}

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

        # Attach ISCO code to the result
        if isco_info and isinstance(result, dict):
            result["code_isco"] = isco_info["code"]
            result["isco_info"] = isco_info

        await db.generated_metiers.update_one({"name_lower": metier_name.lower()}, {"$set": {"name_lower": metier_name.lower(), "data": result, "created_at": datetime.now(timezone.utc).isoformat()}}, upsert=True)
        await db.explorer_jobs.update_one({"job_id": job_id}, {"$set": {"status": "completed", "result": result}})
    except Exception as e:
        logging.error(f"Metier generation failed: {e}")
        await db.explorer_jobs.update_one({"job_id": job_id}, {"$set": {"status": "failed", "error": str(e)}})
