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


async def _get_user_reactif_data(token: str):
    """Fetch all Re'Actif Pro data for a user to build their Ubuntoo profile."""
    token_doc = await db.tokens.find_one({"token": token}, {"_id": 0})
    if not token_doc:
        return None
    token_id = token_doc.get("id")
    profile = await db.profiles.find_one({"token_id": token_id}, {"_id": 0})
    passport = await db.passports.find_one({"token_id": token_id}, {"_id": 0})
    cv_result = await db.cv_results.find_one({"token_id": token_id}, {"_id": 0})
    cv_optimized = await db.cv_optimized.find_one({"token_id": token_id}, {"_id": 0})
    dclic = await db.dclic_results.find_one({"token_id": token_id}, {"_id": 0})
    return {
        "token_id": token_id,
        "pseudo": profile.get("pseudo", profile.get("name", "")) if profile else "",
        "profile": profile,
        "passport": passport,
        "cv_result": cv_result,
        "cv_optimized": cv_optimized,
        "dclic": dclic,
    }


@router.get("/ubuntoo/profile")
async def get_ubuntoo_profile(token: str = None):
    """Get saved Ubuntoo profile for user, or null if not synced."""
    if not token:
        return {"profile": None, "synced": False}
    token_doc = await db.tokens.find_one({"token": token}, {"_id": 0})
    if not token_doc:
        return {"profile": None, "synced": False}
    token_id = token_doc["id"]
    ub_profile = await db.ubuntoo_profiles.find_one({"token_id": token_id}, {"_id": 0})
    has_dclic = await db.dclic_results.find_one({"token_id": token_id}, {"_id": 0}) is not None
    has_cv = await db.cv_results.find_one({"token_id": token_id}, {"_id": 0}) is not None
    return {
        "profile": ub_profile,
        "synced": ub_profile is not None,
        "has_dclic": has_dclic,
        "has_cv": has_cv,
        "pseudo": token_doc.get("pseudo", ""),
    }


@router.post("/ubuntoo/sync-profile")
async def sync_ubuntoo_profile(token: str = None):
    """Sync Re'Actif Pro data to Ubuntoo profile using AI."""
    if not token:
        raise HTTPException(status_code=401, detail="Token requis")

    data = await _get_user_reactif_data(token)
    if not data:
        raise HTTPException(status_code=404, detail="Utilisateur non trouv\u00e9")

    token_id = data["token_id"]
    pseudo = data["pseudo"]
    profile = data["profile"] or {}
    passport = data["passport"] or {}
    cv_result = data["cv_result"] or {}
    cv_optimized = data["cv_optimized"] or {}
    dclic = data["dclic"] or {}

    # Gather skills from all sources
    skills = set()
    for s in profile.get("skills", []):
        if isinstance(s, str): skills.add(s)
        elif isinstance(s, dict): skills.add(s.get("name", ""))
    for c in passport.get("competences", []):
        if isinstance(c, dict): skills.add(c.get("name", c.get("competence", "")))
        elif isinstance(c, str): skills.add(c)
    for c in cv_result.get("competences_transversales", []):
        if isinstance(c, str): skills.add(c)
    skills.discard("")

    # D'CLIC PRO results
    dclic_mbti = dclic.get("mbti", "")
    dclic_disc = dclic.get("disc", "")
    dclic_riasec = dclic.get("riasec", "")
    dclic_skills = dclic.get("competences_cles", [])
    dclic_vertu = dclic.get("vertu", "")

    # Job title
    title = ""
    if cv_optimized.get("models"):
        title = cv_optimized["models"][0].get("titre", "")
    if not title:
        title = cv_result.get("titre_profil_suggere", "")

    # Sectors
    sectors = list(set(profile.get("sectors", []) + passport.get("target_sectors", [])))

    # Territory
    territory = profile.get("lieu_residence", profile.get("territory", "France"))

    # AI generation
    ai_profile = None
    if EMERGENT_LLM_KEY and (skills or dclic_mbti):
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"ubuntoo-sync-{user_id[:8]}",
                system_message="""Tu es un expert en accompagnement professionnel. \u00c0 partir des donn\u00e9es Re'Actif Pro d'un utilisateur, g\u00e9n\u00e8re son profil Ubuntoo personnalis\u00e9.

R\u00e9ponds UNIQUEMENT en JSON valide :
{
  "suggested_status": "Accompagn\u00e9|Pair-aidant|Mentor|Ambassadeur",
  "status_reason": "Raison courte du statut sugg\u00e9r\u00e9",
  "trust_score": 45,
  "softskills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
  "badges": ["badge1", "badge2"],
  "recommended_groups": ["reconversion", "numerique", "handicap", "vsi"],
  "ai_summary": "R\u00e9sum\u00e9 personnalis\u00e9 en 2-3 phrases du profil Ubuntoo",
  "strengths": ["force1", "force2", "force3"],
  "growth_areas": ["axe1", "axe2"]
}

R\u00e8gles :
- Le trust_score d\u00e9pend de la compl\u00e9tude du profil (CV + D'CLIC PRO = 60-80, un seul = 30-50)
- Les softskills doivent provenir des r\u00e9sultats D'CLIC PRO et CV
- Les badges refl\u00e8tent les \u00e9tapes r\u00e9elles franchies ("D'CLIC PRO certifi\u00e9", "CV analys\u00e9", etc.)
- Les groupes recommand\u00e9s doivent correspondre aux secteurs/comp\u00e9tences
- Le statut sugg\u00e9r\u00e9 d\u00e9pend du niveau d'exp\u00e9rience et de contribution"""
            ).with_model("openai", "gpt-5.2")

            passport_status = "Oui" if passport.get("competences") else "Non"
            cv_status = "Oui" if cv_result else "Non"
            dclic_skills_str = ", ".join(dclic_skills[:10]) if dclic_skills else "Aucune"
            sectors_str = ", ".join(sectors) if sectors else "Non renseign\u00e9s"
            skills_str = ", ".join(list(skills)[:20])
            title_str = title or "Non renseign\u00e9"
            mbti_str = dclic_mbti or "Non pass\u00e9"
            disc_str = dclic_disc or "Non pass\u00e9"
            riasec_str = dclic_riasec or "Non pass\u00e9"
            vertu_str = dclic_vertu or "Non pass\u00e9"

            lines = [
                "DONN\u00c9ES RE'ACTIF PRO DE L'UTILISATEUR :",
                "",
                "Pseudo : " + pseudo,
                "Titre/M\u00e9tier : " + title_str,
                "Territoire : " + territory,
                "Secteurs : " + sectors_str,
                "Comp\u00e9tences (" + str(len(skills)) + ") : " + skills_str,
                "",
                "R\u00e9sultats D'CLIC PRO :",
                "- MBTI : " + mbti_str,
                "- DISC : " + disc_str,
                "- RIASEC : " + riasec_str,
                "- Vertu : " + vertu_str,
                "- Comp\u00e9tences cl\u00e9s D'CLIC : " + dclic_skills_str,
                "",
                "CV analys\u00e9 : " + cv_status,
                "Passeport rempli : " + passport_status,
            ]
            context = "\n".join(lines)

            response = await chat.send_message(UserMessage(text=context))
            raw = response.strip() if isinstance(response, str) else response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
            ai_profile = json.loads(raw.strip())
        except Exception as e:
            logging.warning(f"AI sync profile failed: {e}")

    # Build Ubuntoo profile
    now = datetime.now(timezone.utc).isoformat()
    existing = await db.ubuntoo_profiles.find_one({"token_id": token_id})

    ub_profile = {
        "token_id": token_id,
        "pseudo": pseudo,
        "name": pseudo,
        "title": title,
        "territory": territory,
        "sectors": sectors,
        "status": ai_profile.get("suggested_status", "Accompagn\u00e9") if ai_profile else "Accompagn\u00e9",
        "status_reason": ai_profile.get("status_reason", "") if ai_profile else "",
        "trust": ai_profile.get("trust_score", 35) if ai_profile else 35,
        "badges": ai_profile.get("badges", []) if ai_profile else [],
        "softskills": ai_profile.get("softskills", list(skills)[:5]) if ai_profile else list(skills)[:5],
        "strengths": ai_profile.get("strengths", []) if ai_profile else [],
        "growth_areas": ai_profile.get("growth_areas", []) if ai_profile else [],
        "recommended_groups": ai_profile.get("recommended_groups", []) if ai_profile else [],
        "ai_summary": ai_profile.get("ai_summary", "") if ai_profile else "",
        "contributions": existing.get("contributions", 0) if existing else 0,
        "all_skills": list(skills),
        "synced_from": {
            "dclic_pro": bool(dclic_mbti),
            "cv_analysis": bool(cv_result),
            "passport": bool(passport.get("competences")),
        },
        "synced_at": now,
        "created_at": existing.get("created_at", now) if existing else now,
    }

    if existing:
        await db.ubuntoo_profiles.update_one({"token_id": token_id}, {"$set": ub_profile})
    else:
        await db.ubuntoo_profiles.insert_one(ub_profile)

    # Remove _id before returning
    ub_profile.pop("_id", None)

    return {
        "profile": ub_profile,
        "message": "Profil Ubuntoo synchronis\u00e9 avec succ\u00e8s !",
        "ai_generated": ai_profile is not None,
    }


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
    # Auto-create or update signals from AI analysis
    if analysis and analysis.get("detected_skills"):
        await _update_signals_from_analysis(analysis)
    return {"message": "Analyse terminée", "analysis": analysis, "exchanges_analyzed": len(exchanges)}


async def _update_signals_from_analysis(analysis):
    """Create or update ubuntoo_signals from AI analysis results."""
    now = datetime.now(timezone.utc).isoformat()
    for category, signal_type in [
        ("detected_skills", "competence_emergente"),
        ("detected_tools", "nouvel_outil"),
        ("detected_practices", "pratique_nouvelle"),
    ]:
        for name in analysis.get(category, []):
            if not name:
                continue
            existing = await db.ubuntoo_signals.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
            if existing:
                await db.ubuntoo_signals.update_one(
                    {"_id": existing["_id"]},
                    {"$inc": {"mention_count": 1, "source_exchanges_count": 1},
                     "$set": {"last_detected": now, "validation_status": "analysee_ia"}}
                )
            else:
                await db.ubuntoo_signals.insert_one({
                    "id": str(uuid.uuid4()),
                    "signal_type": signal_type,
                    "name": name,
                    "description": "Signal détecté automatiquement dans les échanges Ubuntoo.",
                    "mention_count": 1,
                    "first_detected": now,
                    "last_detected": now,
                    "related_jobs": [],
                    "related_sectors": [],
                    "source_exchanges_count": 1,
                    "trend_direction": "hausse",
                    "growth_rate": 0.1,
                    "validation_status": "detectee",
                    "ai_confidence": analysis.get("confidence", 0.5),
                    "linked_observatory_skills": [],
                    "linked_evolution_jobs": [],
                    "created_at": now,
                })


@router.get("/ubuntoo/community/exchanges")
async def get_community_exchanges(group: Optional[str] = None, exchange_type: Optional[str] = None):
    """List exchanges for the Ubuntoo community page."""
    query = {}
    if group:
        query["group"] = group
    if exchange_type:
        query["exchange_type"] = exchange_type
    exchanges = await db.ubuntoo_exchanges.find(query, {"_id": 0}).to_list(100)
    return sorted(exchanges, key=lambda x: x.get("timestamp", ""), reverse=True)


@router.post("/ubuntoo/community/exchanges")
async def post_community_exchange(data: dict):
    """Post a new exchange from the Ubuntoo community and trigger signal detection."""
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    exchange_type = data.get("exchange_type", "discussion")
    group = data.get("group", "reconversion")
    author = data.get("author", "Anonyme")

    if not title or not content:
        raise HTTPException(status_code=400, detail="Le titre et le contenu sont requis.")

    now = datetime.now(timezone.utc).isoformat()
    exchange_id = str(uuid.uuid4())

    # AI analysis of the exchange content
    detected = {"detected_skills": [], "detected_tools": [], "detected_practices": []}
    if EMERGENT_LLM_KEY:
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"ubuntoo-detect-{exchange_id[:8]}",
                system_message="Tu es un expert RH. Analyse ce message d'un forum professionnel et identifie les compétences, outils et pratiques mentionnés. Réponds UNIQUEMENT en JSON: {\"detected_skills\": [], \"detected_tools\": [], \"detected_practices\": []}"
            ).with_model("openai", "gpt-5.2")
            response = await chat.send_message(UserMessage(text=f"Titre: {title}\nContenu: {content}"))
            raw = response.strip() if isinstance(response, str) else response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
            detected = json.loads(raw.strip())
        except Exception as e:
            logging.warning(f"AI detection for exchange failed: {e}")

    exchange_doc = {
        "id": exchange_id,
        "exchange_type": exchange_type,
        "group": group,
        "title": title,
        "content_summary": content[:300],
        "author": author,
        "detected_skills": detected.get("detected_skills", []),
        "detected_tools": detected.get("detected_tools", []),
        "detected_practices": detected.get("detected_practices", []),
        "related_jobs": [],
        "related_sectors": [],
        "author_role": "professionnel",
        "timestamp": now,
        "likes": 0,
        "replies_count": 0,
    }
    await db.ubuntoo_exchanges.insert_one(exchange_doc)

    # Update signals from detected items
    all_detected = (
        [(s, "competence_emergente") for s in detected.get("detected_skills", [])] +
        [(s, "nouvel_outil") for s in detected.get("detected_tools", [])] +
        [(s, "pratique_nouvelle") for s in detected.get("detected_practices", [])]
    )
    signals_updated = 0
    for name, signal_type in all_detected:
        if not name:
            continue
        existing = await db.ubuntoo_signals.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
        if existing:
            await db.ubuntoo_signals.update_one(
                {"_id": existing["_id"]},
                {"$inc": {"mention_count": 1, "source_exchanges_count": 1},
                 "$set": {"last_detected": now}}
            )
        else:
            await db.ubuntoo_signals.insert_one({
                "id": str(uuid.uuid4()),
                "signal_type": signal_type,
                "name": name,
                "description": f"Détecté dans un échange Ubuntoo : {title[:80]}",
                "mention_count": 1,
                "first_detected": now,
                "last_detected": now,
                "related_jobs": [],
                "related_sectors": [],
                "source_exchanges_count": 1,
                "trend_direction": "hausse",
                "growth_rate": 0.1,
                "validation_status": "detectee",
                "ai_confidence": 0.6,
                "linked_observatory_skills": [],
                "linked_evolution_jobs": [],
                "created_at": now,
            })
        signals_updated += 1

    # Remove _id before returning
    exchange_doc.pop("_id", None)

    return {
        "exchange": exchange_doc,
        "signals_detected": signals_updated,
        "message": "Échange publié et analysé avec succès."
    }


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
