from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
import logging
import uuid
import json
from datetime import datetime, timezone
from models import SkillContribution, EmergingSkill, CreateContributionRequest
from db import db, EMERGENT_LLM_KEY
from helpers import get_current_token
from emergentintegrations.llm.chat import LlmChat, UserMessage

router = APIRouter()


async def analyze_contribution_with_ai(contribution: SkillContribution) -> Dict[str, Any]:
    if not EMERGENT_LLM_KEY:
        is_valid = 3 < len(contribution.skill_name) < 100
        return {"is_valid": is_valid, "confidence_score": 0.6 if is_valid else 0.3, "category": "technique" if any(kw in contribution.skill_name.lower() for kw in ["code", "data", "dev", "ia", "cyber"]) else "transversale", "similar_existing": [], "rationale": "Analyse basique - cohérence vérifiée"}
    try:
        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"contrib-{contribution.id}", system_message="Tu es un expert RH français. Analyse cette contribution à un observatoire des compétences. Réponds en JSON avec: is_valid (bool), confidence_score (0-1), category (technique/transversale/sectorielle), similar_existing (list), rationale (string).").with_model("openai", "gpt-5.2")
        prompt = f"Nouvelle compétence proposée: {contribution.skill_name}\nDescription: {contribution.skill_description or 'Non fournie'}\nMétier associé: {contribution.related_job or 'Non spécifié'}\nSecteur: {contribution.related_sector or 'Non spécifié'}\nContexte: {contribution.context or 'Non fourni'}\n\nAnalyse si cette compétence est valide, pertinente, précise et potentiellement émergente."
        response = await chat.send_message(UserMessage(text=prompt))
        try:
            return json.loads(response)
        except Exception:
            return {"is_valid": True, "confidence_score": 0.65, "category": "transversale", "similar_existing": [], "rationale": response[:200]}
    except Exception as e:
        logging.error(f"AI contribution analysis error: {e}")
        return {"is_valid": True, "confidence_score": 0.5, "category": "non_classifie", "similar_existing": [], "rationale": "Analyse automatique non disponible"}


async def integrate_contribution_to_skills(contribution: dict):
    existing = await db.emerging_skills.find_one({"skill_name": {"$regex": contribution["skill_name"], "$options": "i"}}, {"_id": 0})
    if existing:
        await db.emerging_skills.update_one({"id": existing["id"]}, {"$inc": {"mention_count": 1, "contributor_count": 1}, "$set": {"last_updated": datetime.now(timezone.utc).isoformat()}})
    else:
        new_skill = EmergingSkill(skill_name=contribution["skill_name"], description=contribution.get("skill_description"), related_sectors=[contribution["related_sector"]] if contribution.get("related_sector") else [], related_jobs=[contribution["related_job"]] if contribution.get("related_job") else [], related_tools=contribution.get("related_tools", []), emergence_score=0.5, growth_rate=0.1, mention_count=contribution.get("similar_count", 1), contributor_count=1)
        await db.emerging_skills.insert_one(new_skill.model_dump())
    await db.skill_contributions.update_one({"id": contribution["id"]}, {"$set": {"status": "integree"}})


@router.get("/observatoire/dashboard")
async def get_observatoire_dashboard():
    emerging_skills = await db.emerging_skills.find({}, {"_id": 0}).to_list(50)
    sector_trends = await db.sector_trends.find({}, {"_id": 0}).to_list(20)
    contributions_count = await db.skill_contributions.count_documents({})
    validated_count = await db.skill_contributions.count_documents({"status": "integree"})
    total_emerging = len([s for s in emerging_skills if s.get("status") == "emergente"])
    total_growing = len([s for s in emerging_skills if s.get("status") == "en_croissance"])
    sectors_in_transformation = len([t for t in sector_trends if t.get("transformation_index", 0) > 0.6])
    return {
        "emerging_skills": emerging_skills, "sector_trends": sector_trends,
        "indicators": {"total_emerging_skills": total_emerging, "total_growing_skills": total_growing, "sectors_in_transformation": sectors_in_transformation, "total_contributions": contributions_count, "validated_contributions": validated_count, "skill_gap_alerts": len([t for t in sector_trends if t.get("skill_gap_alert")])}
    }


@router.get("/observatoire/emerging-skills")
async def get_emerging_skills(sector: Optional[str] = None, status: Optional[str] = None):
    query = {}
    if sector: query["related_sectors"] = sector
    if status: query["status"] = status
    skills = await db.emerging_skills.find(query, {"_id": 0}).to_list(100)
    return sorted(skills, key=lambda x: x.get("emergence_score", 0), reverse=True)


@router.get("/observatoire/sector-trends")
async def get_sector_trends(sector: Optional[str] = None):
    query = {}
    if sector: query["sector_name"] = sector
    trends = await db.sector_trends.find(query, {"_id": 0}).to_list(50)
    return sorted(trends, key=lambda x: x.get("transformation_index", 0), reverse=True)


@router.get("/observatoire/sector/{sector_name}")
async def get_sector_detail(sector_name: str):
    trend = await db.sector_trends.find_one({"sector_name": sector_name}, {"_id": 0})
    if not trend:
        raise HTTPException(status_code=404, detail="Secteur non trouvé")
    related_skills = await db.emerging_skills.find({"related_sectors": sector_name}, {"_id": 0}).to_list(20)
    contributions = await db.skill_contributions.find({"related_sector": sector_name, "status": {"$in": ["validee_ia", "validee_humain", "integree"]}}, {"_id": 0}).to_list(10)
    return {"trend": trend, "related_skills": related_skills, "recent_contributions": contributions}


@router.post("/observatoire/contributions")
async def create_contribution(token: str, request: CreateContributionRequest):
    token_doc = await get_current_token(token)
    contribution = SkillContribution(contributor_id=token_doc["id"], **request.model_dump())
    ai_analysis = await analyze_contribution_with_ai(contribution)
    contribution.ai_analysis = ai_analysis
    contribution.ai_score = ai_analysis.get("confidence_score", 0.5)
    if ai_analysis.get("is_valid", False) and ai_analysis.get("confidence_score", 0) > 0.7:
        contribution.status = "validee_ia"
    elif ai_analysis.get("confidence_score", 0) < 0.3:
        contribution.status = "rejetee_ia"
    similar = await db.skill_contributions.find_one({"skill_name": {"$regex": contribution.skill_name, "$options": "i"}, "status": {"$ne": "rejetee_ia"}}, {"_id": 0})
    if similar:
        await db.skill_contributions.update_one({"id": similar["id"]}, {"$inc": {"similar_count": 1}})
        contribution.similar_count = similar.get("similar_count", 1) + 1
    await db.skill_contributions.insert_one(contribution.model_dump())
    return {"contribution_id": contribution.id, "status": contribution.status, "ai_analysis": ai_analysis, "message": "Contribution enregistrée et analysée"}


@router.get("/observatoire/contributions")
async def get_contributions(token: str, status: Optional[str] = None):
    token_doc = await get_current_token(token)
    query = {"contributor_id": token_doc["id"]}
    if status: query["status"] = status
    return await db.skill_contributions.find(query, {"_id": 0}).to_list(100)


@router.get("/observatoire/contributions/pending")
async def get_pending_contributions():
    return await db.skill_contributions.find({"status": "validee_ia"}, {"_id": 0}).to_list(50)


@router.post("/observatoire/contributions/{contribution_id}/validate")
async def validate_contribution(contribution_id: str, approved: bool, notes: Optional[str] = None):
    update_data = {"status": "validee_humain" if approved else "rejetee_humain", "human_notes": notes, "validated_at": datetime.now(timezone.utc).isoformat()}
    result = await db.skill_contributions.update_one({"id": contribution_id}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Contribution non trouvée")
    if approved:
        contribution = await db.skill_contributions.find_one({"id": contribution_id}, {"_id": 0})
        if contribution and contribution.get("similar_count", 1) >= 3:
            await integrate_contribution_to_skills(contribution)
    return {"message": "Validation enregistrée", "status": update_data["status"]}


@router.post("/observatoire/contributions/{contribution_id}/upvote")
async def upvote_contribution(token: str, contribution_id: str):
    await get_current_token(token)
    result = await db.skill_contributions.update_one({"id": contribution_id}, {"$inc": {"upvotes": 1}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Contribution non trouvée")
    return {"message": "Vote enregistré"}


@router.get("/observatoire/predictions")
async def get_predictions():
    trends = await db.sector_trends.find({}, {"_id": 0}).to_list(50)
    predictions = []
    for trend in trends:
        for pred in trend.get("predicted_skills_demand", []):
            predictions.append({"sector": trend["sector_name"], **pred})
    return sorted(predictions, key=lambda x: x.get("demand_change", "0%"), reverse=True)


@router.get("/observatoire/skill-gaps")
async def get_skill_gaps():
    return await db.sector_trends.find({"skill_gap_alert": True}, {"_id": 0}).to_list(20)
