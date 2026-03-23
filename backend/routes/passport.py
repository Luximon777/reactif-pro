from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import uuid
import logging
import json
from datetime import datetime, timezone
from models import Passport, PassportCompetence, PassportExperience, AddCompetenceRequest, AddExperienceRequest, UpdatePassportProfileRequest, SharePassportRequest, EvaluateCompetenceRequest
from db import db, EMERGENT_LLM_KEY
from helpers import get_current_token
from referentiel_data import REFERENTIEL_VERTUS, REFERENTIEL_VALEURS, ARCHEOLOGIE_SAVOIR_ETRE
from emergentintegrations.llm.chat import LlmChat, UserMessage

router = APIRouter()


def calculate_completeness(passport: dict) -> int:
    score = 0
    if passport.get("professional_summary"): score += 12
    if passport.get("career_project"): score += 8
    if passport.get("motivations"): score += 5
    if passport.get("compatible_environments"): score += 5
    if passport.get("target_sectors"): score += 5
    comps = passport.get("competences", [])
    if len(comps) >= 1: score += 8
    if len(comps) >= 3: score += 7
    if len(comps) >= 5: score += 5
    exps = passport.get("experiences", [])
    if len(exps) >= 1: score += 8
    if len(exps) >= 3: score += 7
    learning = passport.get("learning_path", [])
    if len(learning) >= 1: score += 8
    if len(learning) >= 2: score += 5
    evaluated = sum(1 for c in comps if any(c.get("components", {}).get(k, 0) > 0 for k in ["connaissance", "cognition", "conation", "affection", "sensori_moteur"]))
    if evaluated >= 1: score += 5
    if evaluated >= 3: score += 7
    ccsp_classified = sum(1 for c in comps if c.get("ccsp_pole"))
    if ccsp_classified >= 1: score += 5
    return min(score, 100)


async def aggregate_passport_from_sources(token_id: str) -> dict:
    aggregated = {"competences": [], "experiences": [], "learning_path": []}
    seen_comp_names = set()
    seen_exp_titles = set()
    docs = await db.documents.find({"user_token": token_id}, {"_id": 0}).to_list(50)
    for doc in docs:
        for skill in doc.get("skills", []):
            if skill.lower() not in seen_comp_names:
                seen_comp_names.add(skill.lower())
                aggregated["competences"].append({"id": str(uuid.uuid4()), "name": skill, "category": "technique", "level": "intermediaire", "experience_years": 0, "proof": doc.get("title"), "source": "coffre_fort", "is_emerging": False, "added_at": datetime.now(timezone.utc).isoformat()})
    profile = await db.profiles.find_one({"token_id": token_id}, {"_id": 0})
    if profile:
        for skill_data in profile.get("skills", []):
            sname = skill_data.get("name", "") if isinstance(skill_data, dict) else str(skill_data)
            if sname.lower() not in seen_comp_names:
                seen_comp_names.add(sname.lower())
                level = skill_data.get("level", "intermediaire") if isinstance(skill_data, dict) else "intermediaire"
                aggregated["competences"].append({"id": str(uuid.uuid4()), "name": sname, "category": "technique", "level": level, "experience_years": 0, "proof": None, "source": "profil", "is_emerging": False, "added_at": datetime.now(timezone.utc).isoformat()})
    modules = await db.modules.find({}, {"_id": 0}).to_list(50)
    for mod in modules:
        aggregated["learning_path"].append({"id": str(uuid.uuid4()), "title": mod.get("title", ""), "provider": "RE'ACTIF PRO", "skills_acquired": mod.get("skills", []), "status": "en_cours", "completion_date": None, "badge": None, "source": "plateforme"})
    signals = await db.ubuntoo_signals.find({"validation_status": {"$in": ["validee_humain", "integree"]}}, {"_id": 0}).to_list(20)
    for signal in signals:
        if signal.get("signal_type") == "competence_emergente" and signal["name"].lower() not in seen_comp_names:
            seen_comp_names.add(signal["name"].lower())
            aggregated["competences"].append({"id": str(uuid.uuid4()), "name": signal["name"], "category": "technique", "level": "debutant", "experience_years": 0, "proof": None, "source": "ubuntoo", "is_emerging": True, "added_at": datetime.now(timezone.utc).isoformat()})
    contributions = await db.contributions.find({"user_token": token_id, "status": {"$in": ["validee_ia", "validee"]}}, {"_id": 0}).to_list(20)
    for contrib in contributions:
        sname = contrib.get("skill_name", "")
        if sname and sname.lower() not in seen_comp_names:
            seen_comp_names.add(sname.lower())
            aggregated["competences"].append({"id": str(uuid.uuid4()), "name": sname, "category": "technique", "level": "intermediaire", "experience_years": 0, "proof": None, "source": "contribution", "is_emerging": True, "added_at": datetime.now(timezone.utc).isoformat()})
    return aggregated


async def generate_passerelles_with_ai(competences: List[dict], sectors: List[str], cv_data: dict = None, passport: dict = None) -> List[dict]:
    if not EMERGENT_LLM_KEY or (not competences and not cv_data):
        return []
    try:
        skills_list = ", ".join([c.get("name", "") for c in competences[:15]])
        sectors_str = ", ".join(sectors[:5]) if sectors else "tous secteurs"

        # Enrich with CV data if available
        cv_context = ""
        if cv_data:
            result = cv_data.get("result", {})
            ct = result.get("competences_transversales", [])
            offres = result.get("offres_emploi_suggerees", [])
            if ct:
                cv_context += f"\nCompétences transversales du CV: {', '.join(ct[:10])}"
            if offres:
                cv_context += f"\nMétiers suggérés par l'analyse CV: {', '.join(offres[:5])}"

        # Enrich with passport context (professional summary, career project, experiences)
        profile_context = ""
        if passport:
            summary = passport.get("professional_summary", "")
            career = passport.get("career_project", "")
            if summary:
                profile_context += f"\nRésumé professionnel: {summary[:300]}"
            if career:
                profile_context += f"\nProjet professionnel: {career[:300]}"
            exps = passport.get("experiences", [])
            if exps:
                exp_titles = [f"{e.get('title','')} ({e.get('company','')})" for e in exps[:5] if e.get('title')]
                if exp_titles:
                    profile_context += f"\nExpériences récentes: {', '.join(exp_titles)}"

        system_msg = """Tu es un conseiller en évolution professionnelle français expert, spécialisé dans les reconversions et transitions de carrière.
Analyse le PROFIL COMPLET de la personne (compétences, expériences, projet professionnel) et propose des passerelles professionnelles RÉALISTES et PERTINENTES.

Règles:
- Les métiers proposés doivent être DIRECTEMENT accessibles avec les compétences existantes ou avec une formation courte
- Priorise les métiers dans les secteurs d'intérêt de la personne
- Tiens compte du projet professionnel et de l'expérience pour proposer des métiers COHÉRENTS avec le parcours
- Ne propose PAS de métiers trop éloignés ou irréalistes (ex: ne propose pas "Développeur" à un conseiller en insertion)

Réponds UNIQUEMENT en JSON valide: un array de max 5 objets avec les clés:
job_name (str), compatibility_score (float 0-1), shared_skills (list str - compétences communes), skills_to_acquire (list str max 3), training_needed (str court), accessibility (str: accessible/formation_courte/formation_longue), sector (str)."""

        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"passerelle-{uuid.uuid4()}", system_message=system_msg).with_model("openai", "gpt-5.2")
        prompt = f"Compétences de la personne: {skills_list}\nSecteurs d'intérêt: {sectors_str}{cv_context}{profile_context}\n\nPropose 5 passerelles professionnelles réalistes et pertinentes pour cette personne."
        response = await chat.send_message(UserMessage(text=prompt))
        try:
            result = json.loads(response)
            if isinstance(result, list):
                return result[:5]
            return result.get("passerelles", result.get("pathways", []))[:5]
        except Exception:
            return []
    except Exception as e:
        logging.error(f"Passerelles AI error: {e}")
        return []


@router.get("/passport")
async def get_passport(token: str):
    token_doc = await get_current_token(token)
    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not passport:
        aggregated = await aggregate_passport_from_sources(token_doc["id"])
        new_passport = Passport(token_id=token_doc["id"])
        passport_data = new_passport.model_dump()
        passport_data["competences"] = aggregated["competences"]
        passport_data["learning_path"] = aggregated["learning_path"]
        passport_data["completeness_score"] = calculate_completeness(passport_data)
        await db.passports.insert_one(passport_data)
        passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    sources_count = {}
    for c in passport.get("competences", []):
        src = c.get("source", "declaratif")
        sources_count[src] = sources_count.get(src, 0) + 1
    passport["sources_count"] = sources_count
    passport["total_competences"] = len(passport.get("competences", []))
    passport["total_experiences"] = len(passport.get("experiences", []))
    passport["total_learning"] = len(passport.get("learning_path", []))
    passport["emerging_count"] = len([c for c in passport.get("competences", []) if c.get("is_emerging")])
    return passport


@router.post("/passport/refresh")
async def refresh_passport(token: str):
    token_doc = await get_current_token(token)
    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not passport:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")
    aggregated = await aggregate_passport_from_sources(token_doc["id"])
    existing_names = {c.get("name", "").lower() for c in passport.get("competences", []) if c.get("source") == "declaratif"}
    new_comps = [c for c in aggregated["competences"] if c.get("name", "").lower() not in existing_names]
    declared_comps = [c for c in passport.get("competences", []) if c.get("source") == "declaratif"]
    all_comps = declared_comps + new_comps
    passport["competences"] = all_comps
    passport["learning_path"] = aggregated["learning_path"]
    passport["completeness_score"] = calculate_completeness(passport)
    passport["last_updated"] = datetime.now(timezone.utc).isoformat()
    await db.passports.update_one({"token_id": token_doc["id"]}, {"$set": {"competences": passport["competences"], "learning_path": passport["learning_path"], "completeness_score": passport["completeness_score"], "last_updated": passport["last_updated"]}})
    return {"message": "Passeport actualisé", "completeness_score": passport["completeness_score"]}


@router.put("/passport/profile")
async def update_passport_profile(token: str, data: UpdatePassportProfileRequest):
    token_doc = await get_current_token(token)
    update = {}
    if data.professional_summary is not None: update["professional_summary"] = data.professional_summary
    if data.career_project is not None: update["career_project"] = data.career_project
    if data.motivations is not None: update["motivations"] = data.motivations
    if data.compatible_environments is not None: update["compatible_environments"] = data.compatible_environments
    if data.target_sectors is not None: update["target_sectors"] = data.target_sectors
    if not update:
        raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")
    update["last_updated"] = datetime.now(timezone.utc).isoformat()
    result = await db.passports.update_one({"token_id": token_doc["id"]}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")
    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    new_score = calculate_completeness(passport)
    await db.passports.update_one({"token_id": token_doc["id"]}, {"$set": {"completeness_score": new_score}})
    return {"message": "Profil mis à jour", "completeness_score": new_score}


@router.post("/passport/competences")
async def add_passport_competence(token: str, data: AddCompetenceRequest):
    token_doc = await get_current_token(token)
    components = data.components or {"connaissance": 0, "cognition": 0, "conation": 0, "affection": 0, "sensori_moteur": 0}
    new_comp = PassportCompetence(name=data.name, nature=data.nature, category=data.category, level=data.level, experience_years=data.experience_years, proof=data.proof, source="declaratif", components=components, ccsp_pole=data.ccsp_pole or "", ccsp_degree=data.ccsp_degree or "", linked_qualites=data.linked_qualites, linked_valeurs=data.linked_valeurs, linked_vertus=data.linked_vertus).model_dump()
    result = await db.passports.update_one({"token_id": token_doc["id"]}, {"$push": {"competences": new_comp}, "$set": {"last_updated": datetime.now(timezone.utc).isoformat()}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")
    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    new_score = calculate_completeness(passport)
    await db.passports.update_one({"token_id": token_doc["id"]}, {"$set": {"completeness_score": new_score}})
    return {"message": "Compétence ajoutée", "competence": new_comp, "completeness_score": new_score}


@router.post("/passport/experiences")
async def add_passport_experience(token: str, data: AddExperienceRequest):
    token_doc = await get_current_token(token)
    new_exp = PassportExperience(title=data.title, organization=data.organization, description=data.description, skills_used=data.skills_used, achievements=data.achievements, start_date=data.start_date, end_date=data.end_date, is_current=data.is_current, experience_type=data.experience_type, source="declaratif").model_dump()
    result = await db.passports.update_one({"token_id": token_doc["id"]}, {"$push": {"experiences": new_exp}, "$set": {"last_updated": datetime.now(timezone.utc).isoformat()}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")
    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    new_score = calculate_completeness(passport)
    await db.passports.update_one({"token_id": token_doc["id"]}, {"$set": {"completeness_score": new_score}})
    return {"message": "Expérience ajoutée", "experience": new_exp, "completeness_score": new_score}


@router.delete("/passport/competences/{comp_id}")
async def delete_passport_competence(comp_id: str, token: str):
    token_doc = await get_current_token(token)
    result = await db.passports.update_one({"token_id": token_doc["id"]}, {"$pull": {"competences": {"id": comp_id}}, "$set": {"last_updated": datetime.now(timezone.utc).isoformat()}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")
    return {"message": "Compétence supprimée"}


@router.delete("/passport/experiences/{exp_id}")
async def delete_passport_experience(exp_id: str, token: str):
    token_doc = await get_current_token(token)
    result = await db.passports.update_one({"token_id": token_doc["id"]}, {"$pull": {"experiences": {"id": exp_id}}, "$set": {"last_updated": datetime.now(timezone.utc).isoformat()}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")
    return {"message": "Expérience supprimée"}


@router.get("/passport/passerelles")
async def get_passport_passerelles(token: str):
    token_doc = await get_current_token(token)
    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not passport:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")

    # Also get latest CV analysis for richer context
    cv_data = await db.cv_jobs.find_one(
        {"token_id": token_doc["id"], "status": "completed"},
        {"_id": 0},
        sort=[("created_at", -1)]
    )

    passerelles = await generate_passerelles_with_ai(
        passport.get("competences", []),
        passport.get("target_sectors", []),
        cv_data,
        passport
    )
    await db.passports.update_one({"token_id": token_doc["id"]}, {"$set": {"passerelles": passerelles, "last_updated": datetime.now(timezone.utc).isoformat()}})
    return {"passerelles": passerelles}


@router.put("/passport/sharing")
async def update_passport_sharing(token: str, data: SharePassportRequest):
    token_doc = await get_current_token(token)
    sharing = {"is_public": data.is_public, "shared_sections": data.shared_sections, "shared_with": data.shared_with, "share_expiry": data.share_expiry}
    result = await db.passports.update_one({"token_id": token_doc["id"]}, {"$set": {"sharing": sharing, "last_updated": datetime.now(timezone.utc).isoformat()}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")
    return {"message": "Paramètres de partage mis à jour", "sharing": sharing}


@router.put("/passport/competences/{comp_id}/evaluate")
async def evaluate_competence(comp_id: str, token: str, data: EvaluateCompetenceRequest):
    token_doc = await get_current_token(token)
    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not passport:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")
    valid_keys = {"connaissance", "cognition", "conation", "affection", "sensori_moteur"}
    components = {}
    for key in valid_keys:
        val = data.components.get(key, 0)
        components[key] = max(0, min(5, val))
    comps = passport.get("competences", [])
    found = False
    for comp in comps:
        if comp.get("id") == comp_id:
            comp["components"] = components
            if data.ccsp_pole: comp["ccsp_pole"] = data.ccsp_pole
            if data.ccsp_degree: comp["ccsp_degree"] = data.ccsp_degree
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="Compétence non trouvée")
    await db.passports.update_one({"token_id": token_doc["id"]}, {"$set": {"competences": comps, "last_updated": datetime.now(timezone.utc).isoformat()}})
    return {"message": "Évaluation enregistrée", "competence_id": comp_id, "components": components}


@router.get("/passport/diagnostic")
async def get_ccsp_diagnostic(token: str):
    token_doc = await get_current_token(token)
    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not passport:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")
    comps = passport.get("competences", [])
    total = len(comps)
    if total == 0:
        return {"total_competences": 0, "evaluated_count": 0, "lamri_lubart_profile": {"connaissance": 0, "cognition": 0, "conation": 0, "affection": 0, "sensori_moteur": 0}, "ccsp_distribution": {"poles": {}, "degrees": {}}, "recommendations": []}
    ll_totals = {"connaissance": 0, "cognition": 0, "conation": 0, "affection": 0, "sensori_moteur": 0}
    evaluated_count = 0
    for comp in comps:
        cdata = comp.get("components", {})
        if any(cdata.get(k, 0) > 0 for k in ll_totals):
            evaluated_count += 1
            for k in ll_totals:
                ll_totals[k] += cdata.get(k, 0)
    ll_avg = {k: round(v / max(evaluated_count, 1), 1) for k, v in ll_totals.items()}
    poles = {"realisation": 0, "interaction": 0, "initiative": 0}
    degrees = {"imitation": 0, "adaptation": 0, "transposition": 0}
    for comp in comps:
        pole = comp.get("ccsp_pole", "")
        degree = comp.get("ccsp_degree", "")
        if pole in poles: poles[pole] += 1
        if degree in degrees: degrees[degree] += 1
    recommendations = []
    if ll_avg.get("connaissance", 0) < 2: recommendations.append({"type": "formation", "message": "Renforcez vos savoirs théoriques par des formations ou lectures spécialisées.", "component": "connaissance"})
    if ll_avg.get("cognition", 0) < 2: recommendations.append({"type": "formation", "message": "Développez vos capacités d'analyse et de raisonnement critique.", "component": "cognition"})
    if ll_avg.get("conation", 0) < 2: recommendations.append({"type": "accompagnement", "message": "Travaillez votre motivation et votre engagement par un accompagnement personnalisé.", "component": "conation"})
    if ll_avg.get("affection", 0) < 2: recommendations.append({"type": "developpement", "message": "Renforcez votre intelligence émotionnelle et votre empathie.", "component": "affection"})
    if ll_avg.get("sensori_moteur", 0) < 2: recommendations.append({"type": "pratique", "message": "Augmentez la pratique terrain pour développer vos habiletés techniques.", "component": "sensori_moteur"})
    if poles.get("initiative", 0) == 0 and total > 2: recommendations.append({"type": "ccsp", "message": "Aucune compétence d'initiative identifiée. Explorez l'autonomie et l'innovation.", "component": "initiative"})
    if degrees.get("transposition", 0) == 0 and total > 2: recommendations.append({"type": "ccsp", "message": "Développez votre capacité à transposer vos compétences dans de nouveaux contextes.", "component": "transposition"})
    nature_dist = {"savoir_faire": 0, "savoir_etre": 0, "non_classee": 0}
    for comp in comps:
        n = comp.get("nature", "")
        if n == "savoir_faire": nature_dist["savoir_faire"] += 1
        elif n == "savoir_etre": nature_dist["savoir_etre"] += 1
        else: nature_dist["non_classee"] += 1
    if nature_dist["savoir_etre"] == 0 and total > 2: recommendations.append({"type": "orientation", "message": "Identifiez vos savoir-être (soft skills) pour enrichir votre stratégie d'orientation professionnelle.", "component": "savoir_etre"})
    if nature_dist["savoir_faire"] == 0 and total > 2: recommendations.append({"type": "orientation", "message": "Ajoutez vos compétences techniques (savoir-faire) pour mieux cibler les métiers compatibles.", "component": "savoir_faire"})
    if nature_dist["non_classee"] > 0: recommendations.append({"type": "classification", "message": f"{nature_dist['non_classee']} compétence(s) non classée(s). Précisez leur nature (savoir-faire ou savoir-être) pour un meilleur diagnostic.", "component": "nature"})
    return {"total_competences": total, "evaluated_count": evaluated_count, "lamri_lubart_profile": ll_avg, "ccsp_distribution": {"poles": poles, "degrees": degrees}, "nature_distribution": nature_dist, "recommendations": recommendations}


@router.get("/passport/archeologie")
async def get_passport_archeologie(token: str):
    token_doc = await get_current_token(token)
    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not passport:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")
    comps = passport.get("competences", [])
    savoir_faire = [c for c in comps if c.get("nature") == "savoir_faire"]
    savoir_etre = [c for c in comps if c.get("nature") == "savoir_etre"]
    non_classees = [c for c in comps if not c.get("nature")]
    chains = []
    for comp in savoir_etre:
        name = comp.get("name", "")
        ref = ARCHEOLOGIE_SAVOIR_ETRE.get(name, {})
        qualites = comp.get("linked_qualites", []) or ref.get("qualites", [])
        valeurs_ids = comp.get("linked_valeurs", []) or ref.get("valeurs", [])
        vertus_ids = comp.get("linked_vertus", []) or ref.get("vertus", [])
        valeurs_names = [v["name"] for v in REFERENTIEL_VALEURS if v["id"] in valeurs_ids]
        vertus_names = [v["name"] for v in REFERENTIEL_VERTUS if v["id"] in vertus_ids]
        chains.append({"competence": name, "nature": "savoir_etre", "qualites": qualites, "valeurs": valeurs_names, "vertus": vertus_names})
    all_vertus = set()
    all_valeurs = set()
    for comp in savoir_etre:
        ref = ARCHEOLOGIE_SAVOIR_ETRE.get(comp.get("name", ""), {})
        for v in (comp.get("linked_vertus", []) or ref.get("vertus", [])): all_vertus.add(v)
        for v in (comp.get("linked_valeurs", []) or ref.get("valeurs", [])): all_valeurs.add(v)
    return {
        "summary": {"total": len(comps), "savoir_faire": len(savoir_faire), "savoir_etre": len(savoir_etre), "non_classees": len(non_classees), "vertus_covered": list(all_vertus), "valeurs_covered": list(all_valeurs)},
        "chains": chains,
        "savoir_faire_list": [{"id": c.get("id"), "name": c.get("name"), "category": c.get("category")} for c in savoir_faire],
        "savoir_etre_list": [{"id": c.get("id"), "name": c.get("name"), "category": c.get("category")} for c in savoir_etre],
        "non_classees_list": [{"id": c.get("id"), "name": c.get("name")} for c in non_classees],
    }
