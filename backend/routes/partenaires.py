from fastapi import APIRouter, HTTPException
from db import db
from helpers import get_current_token
from models import Beneficiary
from datetime import datetime, timezone
import uuid

router = APIRouter()


# ===== DASHBOARD STATS =====

@router.get("/partenaires/stats")
async def get_partenaire_stats(token: str):
    """Get dashboard statistics for the partner"""
    token_doc = await get_current_token(token)
    partner_id = token_doc["id"]

    beneficiaires = await db.beneficiaires.find(
        {"partner_id": partner_id}, {"_id": 0}
    ).to_list(500)

    total = len(beneficiaires)
    en_accompagnement = sum(1 for b in beneficiaires if b.get("status") == "En accompagnement")
    en_formation = sum(1 for b in beneficiaires if b.get("status") == "Formation en cours")
    en_emploi = sum(1 for b in beneficiaires if b.get("status") == "En emploi")
    en_recherche = sum(1 for b in beneficiaires if b.get("status") == "Recherche d'emploi")
    en_attente = sum(1 for b in beneficiaires if b.get("status") == "En attente")

    taux_insertion = round((en_emploi / max(total, 1)) * 100)

    # Count active freins
    total_freins = 0
    freins_resolus = 0
    for b in beneficiaires:
        for frein in b.get("freins", []):
            total_freins += 1
            if frein.get("status") == "resolu":
                freins_resolus += 1

    return {
        "total": total,
        "en_accompagnement": en_accompagnement,
        "en_formation": en_formation,
        "en_emploi": en_emploi,
        "en_recherche": en_recherche,
        "en_attente": en_attente,
        "taux_insertion": taux_insertion,
        "total_freins": total_freins,
        "freins_resolus": freins_resolus,
        "freins_actifs": total_freins - freins_resolus,
    }


# ===== BENEFICIAIRES CRUD =====

@router.get("/partenaires/beneficiaires")
async def get_beneficiaires(token: str):
    token_doc = await get_current_token(token)
    return await db.beneficiaires.find(
        {"partner_id": token_doc["id"]}, {"_id": 0}
    ).sort("last_activity", -1).to_list(500)


@router.get("/partenaires/beneficiaires/{beneficiary_id}")
async def get_beneficiaire_detail(beneficiary_id: str, token: str):
    token_doc = await get_current_token(token)
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")
    return ben


@router.post("/partenaires/beneficiaires")
async def create_beneficiaire(token: str, name: str, sector: str = "Autre", notes: str = ""):
    token_doc = await get_current_token(token)
    beneficiary = {
        "id": str(uuid.uuid4()),
        "name": name,
        "status": "En accompagnement",
        "progress": 0,
        "skills_acquired": [],
        "sector": sector,
        "notes": notes,
        "freins": [],
        "historique": [{
            "date": datetime.now(timezone.utc).isoformat(),
            "action": "creation",
            "detail": "Création du suivi"
        }],
        "last_activity": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "partner_id": token_doc["id"]
    }
    await db.beneficiaires.insert_one(beneficiary)
    beneficiary.pop("_id", None)
    return beneficiary


@router.put("/partenaires/beneficiaires/{beneficiary_id}")
async def update_beneficiaire(
    beneficiary_id: str,
    token: str,
    status: str = None,
    progress: int = None,
    notes: str = None,
    sector: str = None
):
    token_doc = await get_current_token(token)
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")

    update_data = {"last_activity": datetime.now(timezone.utc).isoformat()}
    hist_entry = {"date": datetime.now(timezone.utc).isoformat(), "action": "update"}

    if status and status != ben.get("status"):
        update_data["status"] = status
        hist_entry["detail"] = f"Statut: {ben.get('status')} -> {status}"
    if progress is not None:
        update_data["progress"] = progress
        hist_entry["detail"] = hist_entry.get("detail", "") + f" Progression: {progress}%"
    if notes is not None:
        update_data["notes"] = notes
    if sector:
        update_data["sector"] = sector

    await db.beneficiaires.update_one(
        {"id": beneficiary_id},
        {
            "$set": update_data,
            "$push": {"historique": hist_entry}
        }
    )
    updated = await db.beneficiaires.find_one({"id": beneficiary_id}, {"_id": 0})
    return updated


@router.delete("/partenaires/beneficiaires/{beneficiary_id}")
async def delete_beneficiaire(beneficiary_id: str, token: str):
    token_doc = await get_current_token(token)
    result = await db.beneficiaires.delete_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")
    return {"message": "Bénéficiaire supprimé"}


# ===== FREINS PERIPHERIQUES =====

@router.post("/partenaires/beneficiaires/{beneficiary_id}/freins")
async def add_frein(beneficiary_id: str, token: str, category: str, description: str = "", severity: str = "moyen"):
    """Add a peripheral obstacle for a beneficiary"""
    token_doc = await get_current_token(token)
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")

    valid_categories = ["logement", "sante", "mobilite", "garde_enfant", "handicap", "administratif", "financier", "autre"]
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Catégorie invalide. Valeurs: {', '.join(valid_categories)}")

    frein = {
        "id": str(uuid.uuid4()),
        "category": category,
        "description": description,
        "severity": severity,
        "status": "actif",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "resolved_at": None,
        "solution": ""
    }

    await db.beneficiaires.update_one(
        {"id": beneficiary_id},
        {
            "$push": {
                "freins": frein,
                "historique": {
                    "date": datetime.now(timezone.utc).isoformat(),
                    "action": "frein_ajout",
                    "detail": f"Frein ajouté: {category}"
                }
            },
            "$set": {"last_activity": datetime.now(timezone.utc).isoformat()}
        }
    )
    return frein


@router.put("/partenaires/beneficiaires/{beneficiary_id}/freins/{frein_id}")
async def update_frein(beneficiary_id: str, frein_id: str, token: str, status: str = None, solution: str = None):
    """Update a peripheral obstacle (resolve it, add solution)"""
    token_doc = await get_current_token(token)
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")

    freins = ben.get("freins", [])
    updated = False
    for frein in freins:
        if frein["id"] == frein_id:
            if status:
                frein["status"] = status
                if status == "resolu":
                    frein["resolved_at"] = datetime.now(timezone.utc).isoformat()
            if solution is not None:
                frein["solution"] = solution
            updated = True
            break

    if not updated:
        raise HTTPException(status_code=404, detail="Frein non trouvé")

    await db.beneficiaires.update_one(
        {"id": beneficiary_id},
        {
            "$set": {
                "freins": freins,
                "last_activity": datetime.now(timezone.utc).isoformat()
            },
            "$push": {
                "historique": {
                    "date": datetime.now(timezone.utc).isoformat(),
                    "action": "frein_update",
                    "detail": f"Frein mis à jour: {status or 'modification'}"
                }
            }
        }
    )
    return {"message": "Frein mis à jour", "frein": frein}


# ===== SKILLS MANAGEMENT =====

@router.post("/partenaires/beneficiaires/{beneficiary_id}/skills")
async def add_skill(beneficiary_id: str, token: str, skill: str):
    """Add a validated skill for a beneficiary"""
    token_doc = await get_current_token(token)
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")

    skills = ben.get("skills_acquired", [])
    if skill not in skills:
        skills.append(skill)

    await db.beneficiaires.update_one(
        {"id": beneficiary_id},
        {
            "$set": {
                "skills_acquired": skills,
                "last_activity": datetime.now(timezone.utc).isoformat()
            },
            "$push": {
                "historique": {
                    "date": datetime.now(timezone.utc).isoformat(),
                    "action": "skill_ajout",
                    "detail": f"Compétence validée: {skill}"
                }
            }
        }
    )
    return {"skills_acquired": skills}


# ===== PARTENAIRE PROFILE =====

@router.get("/partenaires/profile")
async def get_partenaire_profile(token: str):
    """Get the partner's own profile info"""
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    profile.pop("password_hash", None)
    return profile
