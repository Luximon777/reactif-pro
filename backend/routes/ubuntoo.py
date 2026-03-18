from fastapi import APIRouter, HTTPException
from typing import Optional
import uuid
import logging
import json
from datetime import datetime, timezone
from models import EmergingSkill
from db import db, EMERGENT_LLM_KEY
from emergentintegrations.llm.chat import LlmChat, UserMessage

router = APIRouter()


async def analyze_ubuntoo_exchanges_with_ai(exchanges):
    if not EMERGENT_LLM_KEY or not exchanges:
        return {"detected_skills": ["Prompt Engineering", "No-Code"], "detected_tools": ["ChatGPT", "Notion"], "detected_practices": ["Automatisation de tâches"], "confidence": 0.6, "summary": "Analyse basique - IA non disponible"}
    try:
        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"ubuntoo-{uuid.uuid4()}", system_message="Tu es un expert RH français spécialisé dans l'analyse des tendances du marché du travail. Analyse ces échanges professionnels anonymisés et identifie les signaux faibles sur l'évolution des compétences et des métiers. Réponds en JSON avec: detected_skills (list), detected_tools (list), detected_practices (list), transformations (list of {job, description}), confidence (0-1), summary (string).").with_model("openai", "gpt-5.2")
        summaries = "\n".join([f"- [{e.get('exchange_type','discussion')}] {e.get('content_summary','')}" for e in exchanges[:10]])
        prompt = f"Analyse ces échanges anonymisés du réseau socio-professionnel Ubuntoo :\n\n{summaries}\n\nIdentifie :\n1. Les compétences émergentes mentionnées\n2. Les nouveaux outils ou technologies\n3. Les nouvelles pratiques professionnelles\n4. Les transformations de métiers en cours"
        response = await chat.send_message(UserMessage(text=prompt))
        try:
            return json.loads(response)
        except Exception:
            return {"detected_skills": [], "detected_tools": [], "detected_practices": [], "confidence": 0.6, "summary": response[:300]}
    except Exception as e:
        logging.error(f"Ubuntoo AI analysis error: {e}")
        return {"detected_skills": [], "detected_tools": [], "detected_practices": [], "confidence": 0.5, "summary": "Analyse automatique non disponible"}


async def integrate_ubuntoo_signal(signal: dict):
    existing = await db.emerging_skills.find_one({"skill_name": {"$regex": signal["name"], "$options": "i"}}, {"_id": 0})
    if existing:
        await db.emerging_skills.update_one({"id": existing["id"]}, {"$inc": {"mention_count": signal.get("mention_count", 1)}, "$set": {"last_updated": datetime.now(timezone.utc).isoformat()}, "$addToSet": {"related_sectors": {"$each": signal.get("related_sectors", [])}}})
    else:
        new_skill = EmergingSkill(skill_name=signal["name"], description=signal.get("description"), related_sectors=signal.get("related_sectors", []), related_jobs=signal.get("related_jobs", []), emergence_score=min(signal.get("ai_confidence", 0.5) + 0.1, 1.0), growth_rate=signal.get("growth_rate", 0.1), mention_count=signal.get("mention_count", 1), contributor_count=signal.get("source_exchanges_count", 1), status="emergente")
        await db.emerging_skills.insert_one(new_skill.model_dump())
    await db.ubuntoo_signals.update_one({"id": signal["id"]}, {"$set": {"validation_status": "integree"}})


@router.get("/ubuntoo/dashboard")
async def get_ubuntoo_dashboard():
    signals = await db.ubuntoo_signals.find({}, {"_id": 0}).to_list(100)
    exchanges = await db.ubuntoo_exchanges.find({}, {"_id": 0}).to_list(200)
    insights = await db.ubuntoo_insights.find({}, {"_id": 0}).to_list(50)
    total_signals = len(signals)
    detected = len([s for s in signals if s.get("validation_status") == "detectee"])
    analyzed = len([s for s in signals if s.get("validation_status") == "analysee_ia"])
    validated = len([s for s in signals if s.get("validation_status") == "validee_humain"])
    integrated = len([s for s in signals if s.get("validation_status") == "integree"])
    by_type = {}
    for s in signals:
        t = s.get("signal_type", "autre")
        by_type[t] = by_type.get(t, 0) + 1
    top_signals = sorted(signals, key=lambda x: x.get("mention_count", 0), reverse=True)[:10]
    recent_exchanges = sorted(exchanges, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
    return {"stats": {"total_exchanges_analyzed": len(exchanges), "total_signals_detected": total_signals, "signals_detected": detected, "signals_analyzed_ia": analyzed, "signals_validated_human": validated, "signals_integrated": integrated}, "by_type": by_type, "top_signals": top_signals, "recent_exchanges": recent_exchanges, "insights": insights}


@router.get("/ubuntoo/signals")
async def get_ubuntoo_signals(signal_type: Optional[str] = None, status: Optional[str] = None, sector: Optional[str] = None):
    query = {}
    if signal_type: query["signal_type"] = signal_type
    if status: query["validation_status"] = status
    if sector: query["related_sectors"] = sector
    signals = await db.ubuntoo_signals.find(query, {"_id": 0}).to_list(100)
    return sorted(signals, key=lambda x: x.get("mention_count", 0), reverse=True)


@router.get("/ubuntoo/signals/{signal_id}")
async def get_ubuntoo_signal_detail(signal_id: str):
    signal = await db.ubuntoo_signals.find_one({"id": signal_id}, {"_id": 0})
    if not signal:
        raise HTTPException(status_code=404, detail="Signal non trouvé")
    linked_skills = []
    for skill_name in signal.get("linked_observatory_skills", []):
        skill = await db.emerging_skills.find_one({"skill_name": {"$regex": skill_name, "$options": "i"}}, {"_id": 0})
        if skill: linked_skills.append(skill)
    linked_jobs = []
    for job_name in signal.get("linked_evolution_jobs", []):
        job = await db.job_evolution_indices.find_one({"job_name": {"$regex": job_name, "$options": "i"}}, {"_id": 0})
        if job: linked_jobs.append(job)
    related_exchanges = await db.ubuntoo_exchanges.find({"$or": [{"detected_skills": {"$in": [signal["name"]]}}, {"detected_tools": {"$in": [signal["name"]]}}, {"detected_practices": {"$in": [signal["name"]]}}]}, {"_id": 0}).to_list(20)
    return {"signal": signal, "linked_observatory_skills": linked_skills, "linked_evolution_jobs": linked_jobs, "related_exchanges": related_exchanges}


@router.post("/ubuntoo/signals/{signal_id}/validate")
async def validate_ubuntoo_signal(signal_id: str, approved: bool, notes: Optional[str] = None):
    update_data = {"validation_status": "validee_humain" if approved else "rejetee", "human_notes": notes}
    result = await db.ubuntoo_signals.update_one({"id": signal_id}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Signal non trouvé")
    if approved:
        signal = await db.ubuntoo_signals.find_one({"id": signal_id}, {"_id": 0})
        if signal and signal.get("mention_count", 0) >= 5 and signal.get("ai_confidence", 0) >= 0.7:
            await integrate_ubuntoo_signal(signal)
    return {"message": "Validation enregistrée", "status": update_data["validation_status"]}


@router.post("/ubuntoo/analyze")
async def trigger_ubuntoo_analysis():
    exchanges = await db.ubuntoo_exchanges.find({}, {"_id": 0}).to_list(50)
    if not exchanges:
        return {"message": "Aucun échange à analyser"}
    analysis = await analyze_ubuntoo_exchanges_with_ai(exchanges)
    return {"message": "Analyse terminée", "analysis": analysis, "exchanges_analyzed": len(exchanges)}


@router.get("/ubuntoo/insights")
async def get_ubuntoo_insights():
    insights = await db.ubuntoo_insights.find({}, {"_id": 0}).to_list(50)
    return sorted(insights, key=lambda x: {"haute": 0, "moyenne": 1, "basse": 2}.get(x.get("priority", "moyenne"), 1))


@router.get("/ubuntoo/cross-reference")
async def get_cross_reference_data():
    signals = await db.ubuntoo_signals.find({"validation_status": {"$in": ["analysee_ia", "validee_humain", "integree"]}}, {"_id": 0}).to_list(50)
    observatory_skills = await db.emerging_skills.find({}, {"_id": 0}).to_list(50)
    evolution_jobs = await db.job_evolution_indices.find({}, {"_id": 0}).to_list(50)
    cross_refs = []
    for signal in signals:
        matched_skills = [s for s in observatory_skills if any(signal["name"].lower() in sk.lower() or sk.lower() in signal["name"].lower() for sk in [s.get("skill_name", "")])]
        matched_jobs = [j for j in evolution_jobs if any(sector in j.get("sector", "").lower() for sector in [s.lower() for s in signal.get("related_sectors", [])])]
        if matched_skills or matched_jobs:
            cross_refs.append({"signal": signal["name"], "signal_type": signal.get("signal_type"), "mention_count": signal.get("mention_count", 0), "matched_observatory_skills": [s.get("skill_name") for s in matched_skills], "matched_jobs": [j.get("job_name") for j in matched_jobs], "validation_status": signal.get("validation_status"), "ai_confidence": signal.get("ai_confidence", 0)})
    return {"cross_references": cross_refs, "total_signals": len(signals), "total_cross_matched": len(cross_refs)}
