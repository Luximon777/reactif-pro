from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
from db import db
from helpers import get_current_token
import uuid

router = APIRouter()


class ValidateCompetenceRequest(BaseModel):
    decision: str  # valide, modifie, rejete
    commentaire: str = ""
    nouveau_libelle: str = ""


@router.get("/emerging/competences")
async def list_emerging_competences(token: str, category: str = "", min_score: int = 0):
    """List all detected emerging competences for a user"""
    token_doc = await get_current_token(token)

    query = {"token_id": token_doc["id"]}
    if category:
        query["categorie"] = category
    if min_score > 0:
        query["score_emergence"] = {"$gte": min_score}

    competences = await db.emerging_competences.find(query, {"_id": 0}).sort("score_emergence", -1).to_list(200)
    return {"competences": competences, "total": len(competences)}


@router.get("/emerging/competence/{comp_id}")
async def get_emerging_competence(token: str, comp_id: str):
    """Get detailed card for an emerging competence"""
    token_doc = await get_current_token(token)
    comp = await db.emerging_competences.find_one({"token_id": token_doc["id"], "id": comp_id}, {"_id": 0})
    if not comp:
        raise HTTPException(status_code=404, detail="Competence non trouvee")

    aliases = await db.competences_alias.find({"competence_id": comp_id}, {"_id": 0}).to_list(50)
    sources = await db.sources_detection.find({"competence_id": comp_id}, {"_id": 0}).to_list(50)
    validations = await db.validation_humaine.find({"competence_id": comp_id}, {"_id": 0}).to_list(50)

    return {**comp, "aliases": aliases, "sources": sources, "validations": validations}


@router.post("/emerging/validate/{comp_id}")
async def validate_competence(token: str, comp_id: str, request: ValidateCompetenceRequest):
    """Consultant validates/modifies/rejects an emerging competence"""
    token_doc = await get_current_token(token)

    comp = await db.emerging_competences.find_one({"token_id": token_doc["id"], "id": comp_id})
    if not comp:
        raise HTTPException(status_code=404, detail="Competence non trouvee")

    if request.decision not in ("valide", "modifie", "rejete"):
        raise HTTPException(status_code=400, detail="Decision invalide")

    await db.validation_humaine.insert_one({
        "id": str(uuid.uuid4()),
        "competence_id": comp_id,
        "validateur_id": token_doc["id"],
        "decision": request.decision,
        "commentaire": request.commentaire,
        "date_validation": datetime.now(timezone.utc).isoformat()
    })

    updates = {"validation_humaine": request.decision, "date_mise_a_jour": datetime.now(timezone.utc).isoformat()}
    if request.decision == "valide":
        updates["valide"] = True
    elif request.decision == "rejete":
        updates["valide"] = False
    elif request.decision == "modifie" and request.nouveau_libelle:
        updates["nom_principal"] = request.nouveau_libelle

    await db.emerging_competences.update_one({"id": comp_id}, {"$set": updates})
    return {"status": "ok", "decision": request.decision}


# NOTE: /emerging/observatory route is defined in observatoire.py (personalized version)
# It cross-references user CV skills with market trends for a personalized response


@router.get("/emerging/market-correlation")
async def get_market_correlation(token: str):
    """Cross-reference user's emerging competences with market trends."""
    token_doc = await get_current_token(token)
    token_id = token_doc["id"]

    user_emerging = await db.emerging_competences.find(
        {"token_id": token_id}, {"_id": 0}
    ).to_list(100)

    if not user_emerging:
        return {"has_data": False, "message": "Analysez votre CV pour détecter vos compétences émergentes", "correlations": [], "summary": {}}

    global_skills = await db.emerging_skills.find({}, {"_id": 0}).to_list(100)
    sector_trends = await db.sector_trends.find({}, {"_id": 0}).to_list(50)

    global_skills_map = {}
    for gs in global_skills:
        global_skills_map[gs.get("skill_name", "").lower()] = gs

    sector_map = {}
    for st in sector_trends:
        sector_map[st.get("sector_name", "").lower()] = st

    correlations = []
    in_market = 0
    high_demand = 0
    growing_sectors_set = set()

    for ec in user_emerging:
        ec_name = (ec.get("nom_principal") or "").lower()
        ec_sectors = [s.lower() for s in ec.get("secteurs_porteurs", [])]

        # Match with global emerging skills
        market_match = None
        for gs_name, gs_data in global_skills_map.items():
            if ec_name in gs_name or gs_name in ec_name or _fuzzy_match_words(ec_name, gs_name):
                market_match = {
                    "skill_name": gs_data.get("skill_name"),
                    "status": gs_data.get("status"),
                    "emergence_score": gs_data.get("emergence_score", 0),
                    "growth_rate": gs_data.get("growth_rate", 0),
                    "related_jobs": gs_data.get("related_jobs", [])
                }
                in_market += 1
                if gs_data.get("emergence_score", 0) > 0.7:
                    high_demand += 1
                break

        # Match sectors with sector trends
        sector_matches = []
        for ec_sector in ec_sectors:
            for st_name, st_data in sector_map.items():
                if ec_sector in st_name or st_name in ec_sector:
                    growing_sectors_set.add(st_data.get("sector_name"))
                    sector_matches.append({
                        "sector": st_data.get("sector_name"),
                        "hiring_trend": st_data.get("hiring_trend"),
                        "transformation_index": st_data.get("transformation_index", 0)
                    })
                    break

        # Is this skill in any sector's emerging or declining lists?
        market_position = "neutre"
        for st_data in sector_trends:
            emerging_in_sector = [s.lower() for s in st_data.get("emerging_skills", [])]
            declining_in_sector = [s.lower() for s in st_data.get("declining_skills", [])]
            if any(ec_name in e or e in ec_name for e in emerging_in_sector):
                market_position = "en_demande"
                break
            if any(ec_name in d or d in ec_name for d in declining_in_sector):
                market_position = "en_declin"
                break

        correlations.append({
            "competence_id": ec.get("id"),
            "nom": ec.get("nom_principal"),
            "score_emergence": ec.get("score_emergence", 0),
            "categorie": ec.get("categorie"),
            "market_match": market_match,
            "sector_matches": sector_matches[:3],
            "market_position": market_position,
            "has_market_data": market_match is not None
        })

    # Sort: market-matched first, then by score
    correlations.sort(key=lambda x: (not x["has_market_data"], -x.get("score_emergence", 0)))

    return {
        "has_data": True,
        "correlations": correlations,
        "summary": {
            "total_emerging": len(user_emerging),
            "in_market": in_market,
            "high_demand": high_demand,
            "growing_sectors": len(growing_sectors_set),
            "market_alignment_pct": round((in_market / len(user_emerging)) * 100) if user_emerging else 0
        }
    }


def _fuzzy_match_words(a: str, b: str) -> bool:
    a_words = set(a.split())
    b_words = set(b.split())
    if not a_words or not b_words:
        return False
    common = a_words & b_words
    return len(common) >= min(len(a_words), len(b_words)) * 0.5
