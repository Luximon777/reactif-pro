from fastapi import APIRouter, HTTPException
from typing import List
import logging
from datetime import datetime, timezone
from models import TrajectoryStep
from db import db, EMERGENT_LLM_KEY
from helpers import get_current_token
from emergentintegrations.llm.chat import LlmChat, UserMessage

router = APIRouter()


@router.get("/trajectory/steps")
async def get_steps(token: str):
    token_doc = await get_current_token(token)
    steps = await db.trajectory_steps.find(
        {"token_id": token_doc["id"]}, {"_id": 0}
    ).sort("order", 1).to_list(200)
    return steps


@router.post("/trajectory/steps")
async def create_step(token: str, step: TrajectoryStep):
    token_doc = await get_current_token(token)
    step.token_id = token_doc["id"]
    count = await db.trajectory_steps.count_documents({"token_id": token_doc["id"]})
    step.order = count
    await db.trajectory_steps.insert_one(step.model_dump())
    return {k: v for k, v in step.model_dump().items() if k != "_id"}


@router.put("/trajectory/steps/{step_id}")
async def update_step(token: str, step_id: str, updates: dict):
    token_doc = await get_current_token(token)
    existing = await db.trajectory_steps.find_one(
        {"id": step_id, "token_id": token_doc["id"]}, {"_id": 0}
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Etape non trouvee")
    updates.pop("id", None)
    updates.pop("token_id", None)
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.trajectory_steps.update_one(
        {"id": step_id, "token_id": token_doc["id"]},
        {"$set": updates}
    )
    updated = await db.trajectory_steps.find_one(
        {"id": step_id}, {"_id": 0}
    )
    return updated


@router.delete("/trajectory/steps/{step_id}")
async def delete_step(token: str, step_id: str):
    token_doc = await get_current_token(token)
    result = await db.trajectory_steps.delete_one(
        {"id": step_id, "token_id": token_doc["id"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Etape non trouvee")
    return {"message": "Etape supprimee"}


@router.post("/trajectory/auto-populate")
async def auto_populate(token: str):
    token_doc = await get_current_token(token)
    existing_count = await db.trajectory_steps.count_documents({"token_id": token_doc["id"]})

    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    new_steps = []
    order = existing_count

    if passport:
        for exp in passport.get("experiences", []):
            title = exp.get("title") or exp.get("poste") or ""
            org = exp.get("company") or exp.get("entreprise") or ""
            if not title:
                continue
            exists = await db.trajectory_steps.find_one(
                {"token_id": token_doc["id"], "title": title, "organization": org},
                {"_id": 0}
            )
            if exists:
                continue
            step = TrajectoryStep(
                token_id=token_doc["id"],
                step_type="emploi",
                title=title,
                organization=org,
                start_date=exp.get("start_date", ""),
                end_date=exp.get("end_date", ""),
                is_ongoing=exp.get("is_current", False),
                description=exp.get("description", ""),
                missions=exp.get("key_achievements", []),
                competences=exp.get("skills_used", []),
                acquis=exp.get("key_learning", ""),
                visibility="private",
                order=order
            )
            new_steps.append(step.model_dump())
            order += 1

    if profile and profile.get("dclic_imported"):
        exists = await db.trajectory_steps.find_one(
            {"token_id": token_doc["id"], "step_type": "certification", "title": {"$regex": "D'CLIC"}},
            {"_id": 0}
        )
        if not exists:
            step = TrajectoryStep(
                token_id=token_doc["id"],
                step_type="certification",
                title="Test D'CLIC PRO complété",
                organization="Ré'Actif Pro",
                description=f"MBTI: {profile.get('dclic_mbti', '')}, DISC: {profile.get('dclic_disc_label', '')}, RIASEC: {profile.get('dclic_riasec_major', '')}",
                competences=profile.get("dclic_competences", [])[:5],
                visibility="private",
                order=order
            )
            new_steps.append(step.model_dump())
            order += 1

    if new_steps:
        await db.trajectory_steps.insert_many(new_steps)

    return {"imported": len(new_steps), "total": existing_count + len(new_steps)}


@router.get("/trajectory/synthesis")
async def get_synthesis(token: str):
    token_doc = await get_current_token(token)

    steps = await db.trajectory_steps.find(
        {"token_id": token_doc["id"]}, {"_id": 0}
    ).sort("order", 1).to_list(200)

    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})

    if not steps and not (profile and profile.get("skills")):
        return {"has_data": False, "synthesis": None}

    context_parts = []
    if steps:
        for s in steps:
            context_parts.append(f"- {s.get('step_type','')}: {s.get('title','')} chez {s.get('organization','')} ({s.get('start_date','')} - {s.get('end_date','en cours')}). Compétences: {', '.join(s.get('competences',[]))}")

    if profile:
        skills_text = ", ".join([s.get("name", "") for s in profile.get("skills", [])[:15]])
        if skills_text:
            context_parts.append(f"Compétences identifiées: {skills_text}")
        if profile.get("dclic_mbti"):
            context_parts.append(f"Profil MBTI: {profile.get('dclic_mbti')}, DISC: {profile.get('dclic_disc_label')}, RIASEC: {profile.get('dclic_riasec_major')}")

    if passport:
        if passport.get("professional_summary"):
            context_parts.append(f"Résumé pro: {passport['professional_summary']}")

    context = "\n".join(context_parts)

    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            model="gpt-4o",
            system_message="""Tu es un conseiller en évolution professionnelle bienveillant. Analyse le parcours de cette personne et produis une synthèse valorisante en JSON.
Retourne UNIQUEMENT un JSON valide avec ces clés:
{
  "fil_conducteur": "Le fil rouge qui relie les étapes du parcours (2-3 phrases)",
  "forces_recurrentes": ["Liste de 3-5 forces récurrentes identifiées"],
  "capacite_adaptation": "Description de la capacité d'adaptation (1-2 phrases)",
  "environnements_maitrises": ["Types d'environnements professionnels maîtrisés"],
  "axes_evolution": ["2-3 axes d'évolution possibles"],
  "competences_transferables": ["3-5 compétences transférables vers d'autres métiers"],
  "message_valorisant": "Un message court et encourageant sur la valeur du parcours (2 phrases max)"
}
Ne retourne RIEN d'autre que le JSON."""
        )
        chat.add_message(UserMessage(content=f"Voici le parcours professionnel à analyser:\n{context}"))
        response = await chat.chat()
        import json
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        synthesis = json.loads(text)
        return {"has_data": True, "synthesis": synthesis}
    except Exception as e:
        logging.error(f"Trajectory synthesis error: {e}")
        return {"has_data": True, "synthesis": {
            "fil_conducteur": "Votre parcours montre une progression et une capacité d'adaptation remarquables.",
            "forces_recurrentes": ["Adaptabilité", "Engagement", "Polyvalence"],
            "capacite_adaptation": "Votre trajectoire témoigne d'une grande capacité à évoluer dans différents contextes.",
            "environnements_maitrises": ["Environnements variés"],
            "axes_evolution": ["Consolidation des acquis", "Nouvelles responsabilités"],
            "competences_transferables": ["Organisation", "Communication", "Gestion"],
            "message_valorisant": "Chaque étape de votre parcours a contribué à construire votre richesse professionnelle."
        }}


@router.get("/trajectory/access-log")
async def get_access_log(token: str):
    token_doc = await get_current_token(token)
    logs = await db.trajectory_access_log.find(
        {"token_id": token_doc["id"]}, {"_id": 0}
    ).sort("accessed_at", -1).to_list(50)
    return logs


@router.put("/trajectory/visibility-settings")
async def update_visibility_settings(token: str, settings: dict):
    token_doc = await get_current_token(token)
    await db.profiles.update_one(
        {"token_id": token_doc["id"]},
        {"$set": {"trajectory_visibility": settings}}
    )
    return {"message": "Paramètres de visibilité mis à jour"}


@router.get("/trajectory/visibility-settings")
async def get_visibility_settings(token: str):
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    return profile.get("trajectory_visibility", {
        "conseiller": False,
        "recruteur": False,
        "partenaire": False,
        "duree_acces": "30j"
    })
