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


@router.get("/observatoire/personalized")
async def get_personalized_observatoire(token: str):
    """Cross-reference observatory data with the user's CV analysis and passport."""
    token_doc = await get_current_token(token)
    token_id = token_doc["id"]

    # Fetch user data in parallel
    passport_data = await db.passports.find_one({"token_id": token_id}, {"_id": 0})
    cv_job = await db.cv_jobs.find_one(
        {"token_id": token_id, "status": "completed"},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    cv_optimized = await db.cv_models.find_one({"token_id": token_id}, {"_id": 0})
    user_emerging = await db.emerging_competences.find(
        {"token_id": token_id}, {"_id": 0}
    ).to_list(50)
    global_skills = await db.emerging_skills.find({}, {"_id": 0}).to_list(100)
    sector_trends = await db.sector_trends.find({}, {"_id": 0}).to_list(50)

    # Extract user skills from multiple sources (analysis + optimized + passport)
    user_skill_names = set()
    user_sectors = set()

    if passport_data:
        for c in passport_data.get("competences", []):
            name = c.get("name", "").strip()
            if name:
                user_skill_names.add(name.lower())
        for s in passport_data.get("target_sectors", []):
            if s:
                user_sectors.add(s)

    cv_result = cv_job.get("result", {}) if cv_job else {}
    for t in cv_result.get("competences_transversales", []):
        if t:
            user_skill_names.add(t.lower())

    # Enrich with optimized CV data (richer competences)
    if cv_optimized and cv_optimized.get("models"):
        for model_data in cv_optimized["models"].values():
            if isinstance(model_data, dict):
                for ck in model_data.get("competences_cles", []):
                    if isinstance(ck, str) and ck.strip():
                        user_skill_names.add(ck.lower())
                for sf in model_data.get("savoir_faire", []):
                    name = sf.get("name", "") if isinstance(sf, dict) else sf
                    if name:
                        user_skill_names.add(str(name).lower())
                titre = model_data.get("titre", "")
                if titre:
                    user_sectors.add(titre)
                break  # Use first available model

    if not user_skill_names and not user_emerging:
        return {
            "has_cv": False,
            "message": "Analysez votre CV pour obtenir des recommandations personnalisées",
            "user_skills_count": 0,
            "matches": [], "skill_gaps": [], "declining_alerts": [],
            "sector_relevance": [], "emerging_from_cv": [],
            "summary": {"total_skills_analyzed": 0, "skills_in_observatory": 0, "skills_declining": 0, "gaps_to_fill": 0, "sectors_relevant": 0, "cv_emerging_detected": 0}
        }

    # Cross-reference: user skills vs global emerging skills
    matches = []
    all_emerging_names = set()
    for skill in global_skills:
        skill_name_lower = skill.get("skill_name", "").lower()
        all_emerging_names.add(skill_name_lower)
        for us in user_skill_names:
            if us in skill_name_lower or skill_name_lower in us or _fuzzy_match(us, skill_name_lower):
                matches.append({
                    "user_skill": us,
                    "observatory_skill": skill.get("skill_name"),
                    "status": skill.get("status", "emergente"),
                    "emergence_score": skill.get("emergence_score", 0),
                    "growth_rate": skill.get("growth_rate", 0),
                    "related_sectors": skill.get("related_sectors", []),
                    "related_jobs": skill.get("related_jobs", [])
                })
                break

    # Identify declining skills from sector trends
    declining_alerts = []
    for trend in sector_trends:
        for declining in trend.get("declining_skills", []):
            if declining.lower() in user_skill_names:
                declining_alerts.append({
                    "skill": declining,
                    "sector": trend.get("sector_name"),
                    "transformation_index": trend.get("transformation_index", 0)
                })

    # Skill gaps: emerging skills the user doesn't have
    skill_gaps = []
    for skill in sorted(global_skills, key=lambda x: x.get("emergence_score", 0), reverse=True):
        skill_name_lower = skill.get("skill_name", "").lower()
        has_skill = any(us in skill_name_lower or skill_name_lower in us for us in user_skill_names)
        if not has_skill:
            skill_sectors = set(s.lower() for s in skill.get("related_sectors", []))
            user_sectors_lower = set(s.lower() for s in user_sectors)
            sector_match = bool(skill_sectors & user_sectors_lower) if user_sectors_lower else True
            skill_gaps.append({
                "skill_name": skill.get("skill_name"),
                "emergence_score": skill.get("emergence_score", 0),
                "growth_rate": skill.get("growth_rate", 0),
                "status": skill.get("status"),
                "related_sectors": skill.get("related_sectors", []),
                "sector_relevant": sector_match,
                "priority": "haute" if sector_match and skill.get("emergence_score", 0) > 0.7 else "moyenne" if skill.get("emergence_score", 0) > 0.5 else "basse"
            })

    # Sector relevance analysis
    sector_relevance = []
    for trend in sector_trends:
        sector_name = trend.get("sector_name", "")
        emerging = set(s.lower() for s in trend.get("emerging_skills", []))
        stable = set(s.lower() for s in trend.get("stable_skills", []))
        declining = set(s.lower() for s in trend.get("declining_skills", []))
        user_in_emerging = [s for s in user_skill_names if any(s in e or e in s for e in emerging)]
        user_in_stable = [s for s in user_skill_names if any(s in st or st in s for st in stable)]
        user_in_declining = [s for s in user_skill_names if any(s in d or d in s for d in declining)]
        if user_in_emerging or user_in_stable or user_in_declining:
            sector_relevance.append({
                "sector": sector_name,
                "transformation_index": trend.get("transformation_index", 0),
                "hiring_trend": trend.get("hiring_trend"),
                "your_emerging_skills": user_in_emerging,
                "your_stable_skills": user_in_stable,
                "your_declining_skills": user_in_declining,
                "skill_gap_alert": trend.get("skill_gap_alert", False)
            })

    # Emerging competences detected from CV
    emerging_from_cv = []
    for ec in user_emerging:
        emerging_from_cv.append({
            "name": ec.get("nom_principal"),
            "category": ec.get("categorie"),
            "score": ec.get("score_emergence", 0),
            "level": ec.get("niveau_emergence"),
            "sectors": ec.get("secteurs_porteurs", []),
            "jobs": ec.get("metiers_associes", []),
            "trend": ec.get("tendance")
        })

    # If DB data is too sparse, enrich with AI analysis
    db_data_sufficient = len(matches) >= 3 and len(skill_gaps) >= 3 and len(sector_relevance) >= 2
    user_title = ""
    if cv_optimized and cv_optimized.get("models"):
        for model_data in cv_optimized["models"].values():
            if isinstance(model_data, dict):
                user_title = model_data.get("titre", "")
                break
    if not user_title and cv_result:
        user_title = cv_result.get("titre_profil_suggere", "")

    if not db_data_sufficient and EMERGENT_LLM_KEY and user_skill_names:
        ai_data = await _generate_observatoire_ai(
            user_title, list(user_skill_names), list(user_sectors),
            EMERGENT_LLM_KEY, token_id
        )
        if ai_data:
            # Merge AI data with what we already found in DB
            ai_matches = ai_data.get("matches", [])
            ai_gaps = ai_data.get("skill_gaps", [])
            ai_declining = ai_data.get("declining_alerts", [])
            ai_sectors = ai_data.get("sector_relevance", [])

            existing_match_names = {m.get("observatory_skill", "").lower() for m in matches}
            for am in ai_matches:
                if am.get("observatory_skill", "").lower() not in existing_match_names:
                    matches.append(am)

            existing_gap_names = {g.get("skill_name", "").lower() for g in skill_gaps}
            for ag in ai_gaps:
                if ag.get("skill_name", "").lower() not in existing_gap_names:
                    skill_gaps.append(ag)

            existing_decline_skills = {d.get("skill", "").lower() for d in declining_alerts}
            for ad in ai_declining:
                if ad.get("skill", "").lower() not in existing_decline_skills:
                    declining_alerts.append(ad)

            existing_sector_names = {s.get("sector", "").lower() for s in sector_relevance}
            for asec in ai_sectors:
                if asec.get("sector", "").lower() not in existing_sector_names:
                    sector_relevance.append(asec)

    return {
        "has_cv": True,
        "user_skills_count": len(user_skill_names),
        "matches": sorted(matches, key=lambda x: x.get("emergence_score", 0), reverse=True),
        "skill_gaps": sorted(skill_gaps, key=lambda x: (x.get("priority") == "haute", x.get("emergence_score", 0)), reverse=True)[:10],
        "declining_alerts": declining_alerts,
        "sector_relevance": sorted(sector_relevance, key=lambda x: len(x.get("your_emerging_skills", [])), reverse=True),
        "emerging_from_cv": sorted(emerging_from_cv, key=lambda x: x.get("score", 0), reverse=True),
        "summary": {
            "total_skills_analyzed": len(user_skill_names),
            "skills_in_observatory": len(matches),
            "skills_declining": len(declining_alerts),
            "gaps_to_fill": len([g for g in skill_gaps if g.get("priority") == "haute"]),
            "sectors_relevant": len(sector_relevance),
            "cv_emerging_detected": len(emerging_from_cv)
        }
    }


async def _generate_observatoire_ai(user_title, user_skills, user_sectors, api_key, token_id):
    """Generate personalized observatory analysis via AI when DB data is sparse."""
    import json as _json

    skills_str = ", ".join(user_skills[:25])
    sectors_str = ", ".join(user_sectors[:5]) if user_sectors else "non précisé"
    context = f"Titre du profil: {user_title}\nCompétences du candidat: {skills_str}\nSecteurs: {sectors_str}"

    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f"obs-{token_id[:8]}",
            system_message="""Tu es un expert en prospective des compétences et du marché du travail en France (2025-2026).
Analyse les compétences du candidat et génère un rapport d'observatoire PERSONNALISÉ.

Réponds UNIQUEMENT en JSON valide:
{
  "matches": [
    {
      "user_skill": "compétence du candidat qui est émergente",
      "observatory_skill": "nom normalisé de la compétence émergente",
      "status": "emergente|en_croissance|etablie",
      "emergence_score": 0.85,
      "growth_rate": 0.25,
      "related_sectors": ["Secteur1", "Secteur2"],
      "related_jobs": ["Métier1", "Métier2"]
    }
  ],
  "skill_gaps": [
    {
      "skill_name": "Compétence manquante mais importante",
      "emergence_score": 0.8,
      "growth_rate": 0.3,
      "status": "emergente",
      "related_sectors": ["Secteur"],
      "sector_relevant": true,
      "priority": "haute|moyenne|basse"
    }
  ],
  "declining_alerts": [
    {
      "skill": "Compétence du candidat en déclin",
      "sector": "Secteur concerné",
      "transformation_index": 0.7
    }
  ],
  "sector_relevance": [
    {
      "sector": "Nom du secteur",
      "transformation_index": 0.75,
      "hiring_trend": "croissance|stable|recul",
      "your_emerging_skills": ["skill1 du candidat qui est émergente dans ce secteur"],
      "your_stable_skills": ["skill stable"],
      "your_declining_skills": ["skill en déclin"],
      "skill_gap_alert": true
    }
  ]
}

Règles:
- Identifie parmi les compétences du candidat celles qui sont émergentes/en croissance sur le marché (matches)
- Identifie 5-8 compétences manquantes prioritaires pour son profil (skill_gaps)
- Signale les compétences du candidat qui sont en déclin ou obsolètes (declining_alerts)
- Analyse 3-5 secteurs pertinents pour ce profil avec leur tendance
- Sois réaliste et basé sur les tendances réelles du marché français
- Les emergence_score sont entre 0 et 1 (0.8+ = très émergent)
- Les growth_rate sont entre 0 et 1 (0.3+ = forte croissance)"""
        ).with_model("openai", "gpt-5.2")

        response = await chat.send_message(UserMessage(text=context))
        raw = response.strip() if isinstance(response, str) else response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]

        return _json.loads(raw.strip())
    except Exception as e:
        logging.error(f"Observatoire AI analysis error: {e}")
        return None


def _fuzzy_match(a: str, b: str) -> bool:
    """Simple fuzzy matching for skill names."""
    a_words = set(a.lower().split())
    b_words = set(b.lower().split())
    if not a_words or not b_words:
        return False
    common = a_words & b_words
    return len(common) >= min(len(a_words), len(b_words)) * 0.5
