from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
from db import db
import uuid

router = APIRouter()


class ValidateCompetenceRequest(BaseModel):
    decision: str  # valide, modifie, rejete
    commentaire: str = ""
    nouveau_libelle: str = ""


@router.get("/emerging/competences")
async def list_emerging_competences(token: str, category: str = "", min_score: int = 0):
    """List all detected emerging competences for a user"""
    from routes.auth import get_current_token
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
    from routes.auth import get_current_token
    token_doc = await get_current_token(token)
    comp = await db.emerging_competences.find_one({"token_id": token_doc["id"], "id": comp_id}, {"_id": 0})
    if not comp:
        raise HTTPException(status_code=404, detail="Competence non trouvee")

    # Get aliases
    aliases = await db.competences_alias.find({"competence_id": comp_id}, {"_id": 0}).to_list(50)
    # Get sources
    sources = await db.sources_detection.find({"competence_id": comp_id}, {"_id": 0}).to_list(50)
    # Get validations
    validations = await db.validation_humaine.find({"competence_id": comp_id}, {"_id": 0}).to_list(50)

    return {**comp, "aliases": aliases, "sources": sources, "validations": validations}


@router.post("/emerging/validate/{comp_id}")
async def validate_competence(token: str, comp_id: str, request: ValidateCompetenceRequest):
    """Consultant validates/modifies/rejects an emerging competence"""
    from routes.auth import get_current_token
    token_doc = await get_current_token(token)

    comp = await db.emerging_competences.find_one({"token_id": token_doc["id"], "id": comp_id})
    if not comp:
        raise HTTPException(status_code=404, detail="Competence non trouvee")

    if request.decision not in ("valide", "modifie", "rejete"):
        raise HTTPException(status_code=400, detail="Decision invalide")

    # Store validation
    await db.validation_humaine.insert_one({
        "id": str(uuid.uuid4()),
        "competence_id": comp_id,
        "validateur_id": token_doc["id"],
        "decision": request.decision,
        "commentaire": request.commentaire,
        "date_validation": datetime.now(timezone.utc).isoformat()
    })

    # Update competence status
    updates = {"validation_humaine": request.decision, "date_mise_a_jour": datetime.now(timezone.utc).isoformat()}
    if request.decision == "valide":
        updates["valide"] = True
    elif request.decision == "rejete":
        updates["valide"] = False
    elif request.decision == "modifie" and request.nouveau_libelle:
        updates["nom_principal"] = request.nouveau_libelle

    await db.emerging_competences.update_one({"id": comp_id}, {"$set": updates})
    return {"status": "ok", "decision": request.decision}


@router.get("/emerging/observatory")
async def get_observatory_data(token: str):
    """Dashboard data for emerging competences observatory"""
    from routes.auth import get_current_token
    await get_current_token(token)

    pipeline_top = [
        {"$match": {"score_emergence": {"$gte": 31}}},
        {"$sort": {"score_emergence": -1}},
        {"$limit": 20},
        {"$project": {"_id": 0, "nom_principal": 1, "categorie": 1, "score_emergence": 1, "niveau_emergence": 1, "secteurs": 1}}
    ]
    top = await db.emerging_competences.aggregate(pipeline_top).to_list(20)

    pipeline_cat = [
        {"$match": {"score_emergence": {"$gte": 31}}},
        {"$group": {"_id": "$categorie", "count": {"$sum": 1}, "avg_score": {"$avg": "$score_emergence"}}},
        {"$sort": {"count": -1}}
    ]
    by_category = await db.emerging_competences.aggregate(pipeline_cat).to_list(10)

    pipeline_level = [
        {"$group": {"_id": "$niveau_emergence", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    by_level = await db.emerging_competences.aggregate(pipeline_level).to_list(10)

    return {
        "top_emerging": top,
        "by_category": [{"categorie": r["_id"], "count": r["count"], "avg_score": round(r.get("avg_score", 0))} for r in by_category],
        "by_level": [{"level": r["_id"], "count": r["count"]} for r in by_level],
    }
