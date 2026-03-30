from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from db import db
from helpers import get_current_token
from datetime import datetime, timezone, timedelta
import uuid
import os
import json
import io

router = APIRouter()


# ===== HELPERS =====

async def _get_beneficiaire_context(beneficiary_id: str, partner_id: str):
    """Gather all data for a beneficiary — used by multiple AI endpoints"""
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": partner_id}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")

    profile = None
    passport = None
    cv_analyses = []
    dclic = None

    if ben.get("linked_token_id"):
        tid = ben["linked_token_id"]
        profile = await db.profiles.find_one({"token_id": tid}, {"_id": 0, "password_hash": 0})
        passport = await db.passports.find_one({"token_id": tid}, {"_id": 0})
        cv_analyses = await db.cv_analyses.find({"token_id": tid}, {"_id": 0}).to_list(10)
        dclic = await db.dclic_results.find_one({"token_id": tid}, {"_id": 0})

    # Get action plan
    plan = await db.action_plans.find_one(
        {"beneficiary_id": beneficiary_id, "partner_id": partner_id}, {"_id": 0}
    )

    # Get interview reports
    reports = await db.interview_reports.find(
        {"beneficiary_id": beneficiary_id, "partner_id": partner_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(20)

    return {
        "ben": ben,
        "profile": profile,
        "passport": passport,
        "cv_analyses": cv_analyses,
        "dclic": dclic,
        "plan": plan,
        "reports": reports,
    }


def _build_context_text(ctx):
    """Build a textual context from gathered data"""
    ben = ctx["ben"]
    profile = ctx["profile"]
    passport = ctx["passport"]
    dclic = ctx["dclic"]
    cv_analyses = ctx["cv_analyses"]

    parts = [f"Nom: {ben['name']}", f"Statut: {ben.get('status', 'inconnu')}", f"Secteur: {ben.get('sector', 'non défini')}"]

    if ben.get("skills_acquired"):
        parts.append(f"Compétences validées: {', '.join(ben['skills_acquired'][:15])}")

    freins = [f for f in ben.get("freins", []) if f.get("status") != "resolu"]
    if freins:
        parts.append(f"Freins actifs: {', '.join(f['category'] for f in freins)}")

    diag = ben.get("diagnostic", {})
    if diag.get("contexte_social"):
        parts.append(f"Contexte social: {diag['contexte_social']}")
    if diag.get("motivation_level"):
        parts.append(f"Motivation: {diag['motivation_level']}")
    if diag.get("posture"):
        parts.append(f"Posture: {diag['posture']}")
    if diag.get("autonomie"):
        parts.append(f"Autonomie: {diag['autonomie']}")
    if diag.get("mobilite_detail"):
        parts.append(f"Mobilité: {diag['mobilite_detail']}")
    if diag.get("observations"):
        parts.append(f"Observations: {diag['observations']}")

    if profile:
        if profile.get("skills"):
            skills = [s.get("name", str(s)) if isinstance(s, dict) else str(s) for s in profile["skills"][:15]]
            parts.append(f"Compétences RE'ACTIF PRO: {', '.join(skills)}")
        if profile.get("sectors"):
            parts.append(f"Secteurs visés: {', '.join(profile['sectors'])}")

    if passport:
        if passport.get("professional_summary"):
            parts.append(f"Synthèse professionnelle: {passport['professional_summary'][:400]}")
        if passport.get("career_project"):
            parts.append(f"Projet professionnel: {passport['career_project'][:400]}")

    if dclic and dclic.get("scores"):
        scores = ", ".join(f"{k}: {v}" for k, v in dclic["scores"].items() if isinstance(v, (int, float)))
        parts.append(f"Scores D'CLIC: {scores}")
        if dclic.get("summary"):
            parts.append(f"Synthèse D'CLIC: {dclic['summary'][:300]}")

    if cv_analyses:
        parts.append(f"CV analysés: {len(cv_analyses)}")

    bilan = ben.get("bilan", {})
    if bilan:
        completed = [k for k in bilan.keys() if k != "updated_at"]
        if completed:
            parts.append(f"Fiches bilan complétées: {', '.join(completed)}")

    return "\n".join(parts)


async def _call_llm(system_prompt: str, user_message: str, session_id: str):
    """Call the Emergent LLM"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    emergent_key = os.environ.get("EMERGENT_LLM_KEY", "")
    chat = LlmChat(
        api_key=emergent_key,
        session_id=session_id,
        system_message=system_prompt,
    ).with_model("openai", "gpt-4.1-mini")
    response = await chat.send_message(UserMessage(text=user_message))
    return response.strip()


def _parse_json_response(text):
    """Parse JSON from LLM response"""
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    return json.loads(text)


# ===== 1. SYNTHESE PRE-ENTRETIEN =====

@router.post("/partenaires/beneficiaires/{beneficiary_id}/synthese-pre-entretien")
async def generate_synthese_pre_entretien(beneficiary_id: str, token: str):
    """Generate AI pre-interview summary for a beneficiary"""
    token_doc = await get_current_token(token)
    ctx = await _get_beneficiaire_context(beneficiary_id, token_doc["id"])
    context_text = _build_context_text(ctx)

    system_prompt = """Tu es un assistant pour conseillers emploi en France. Tu prépares des synthèses pré-entretien claires et exploitables.

CONTEXTE: Tu travailles dans le cadre de RE'ACTIF PRO, interface complémentaire aux dispositifs existants (France Travail, Mission Locale, APEC).

Génère une synthèse pré-entretien au format JSON:
{
  "resume_parcours": "Résumé du parcours en 3-4 phrases",
  "points_forts": ["Point fort 1", "Point fort 2", "Point fort 3"],
  "points_vigilance": ["Vigilance 1", "Vigilance 2"],
  "freins_identifies": ["Frein 1 avec contexte", "Frein 2"],
  "hypotheses_projet": "Hypothèse(s) de projet professionnel",
  "questions_a_explorer": ["Question 1 pour l'entretien", "Question 2", "Question 3"],
  "dispositifs_a_envisager": ["Dispositif 1", "Dispositif 2"],
  "niveau_urgence": "immediat|3_mois|6_mois|non_urgent",
  "niveau_autonomie": "fort|moyen|faible|tres_faible",
  "recommandation_entretien": "Conseil pour l'approche de l'entretien"
}

Sois concret, factuel, exploitable en 2 minutes de lecture. Maximum 4 éléments par liste."""

    try:
        response = await _call_llm(system_prompt, f"Voici le dossier du bénéficiaire:\n\n{context_text}", f"synthese_{beneficiary_id}")
        synthese = _parse_json_response(response)

        now = datetime.now(timezone.utc)
        await db.beneficiaires.update_one(
            {"id": beneficiary_id},
            {
                "$set": {
                    "last_synthese": {"data": synthese, "generated_at": now.isoformat()},
                    "last_activity": now.isoformat()
                },
                "$push": {"historique": {"date": now.isoformat(), "action": "synthese_pre_entretien", "detail": "Synthèse pré-entretien générée par IA"}}
            }
        )
        return synthese
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erreur de format IA")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur IA: {str(e)}")


# ===== 2. COMPTE RENDU D'ENTRETIEN =====

class CompteRenduRequest(BaseModel):
    type_entretien: str = "diagnostic"  # diagnostic, intermediaire, final
    notes_conseiller: Optional[str] = None
    points_abordes: Optional[List[str]] = None
    decisions_prises: Optional[List[str]] = None
    prochaine_etape: Optional[str] = None


@router.post("/partenaires/beneficiaires/{beneficiary_id}/compte-rendu")
async def generate_compte_rendu(beneficiary_id: str, token: str, payload: CompteRenduRequest):
    """Generate AI-assisted interview report"""
    token_doc = await get_current_token(token)
    ctx = await _get_beneficiaire_context(beneficiary_id, token_doc["id"])
    context_text = _build_context_text(ctx)

    extra = ""
    if payload.notes_conseiller:
        extra += f"\nNotes du conseiller: {payload.notes_conseiller}"
    if payload.points_abordes:
        extra += f"\nPoints abordés: {', '.join(payload.points_abordes)}"
    if payload.decisions_prises:
        extra += f"\nDécisions prises: {', '.join(payload.decisions_prises)}"
    if payload.prochaine_etape:
        extra += f"\nProchaine étape: {payload.prochaine_etape}"

    type_labels = {"diagnostic": "Entretien diagnostic", "intermediaire": "Entretien intermédiaire", "final": "Entretien de clôture"}
    type_label = type_labels.get(payload.type_entretien, "Entretien")

    system_prompt = f"""Tu es un assistant pour conseillers emploi. Tu rédiges des comptes rendus d'entretien professionnels, exploitables dans les outils métier (type France Travail).

TYPE: {type_label}

Génère un compte rendu au format JSON:
{{
  "titre": "Compte rendu — {type_label}",
  "date": "{datetime.now(timezone.utc).strftime('%d/%m/%Y')}",
  "contexte": "Contexte de l'entretien (2-3 phrases)",
  "situation_actuelle": "Situation actuelle du bénéficiaire",
  "parcours_synthese": "Synthèse du parcours professionnel",
  "freins_identifies": "Freins et contraintes identifiés",
  "competences_identifiees": "Compétences et points forts",
  "projet_professionnel": "État du projet professionnel",
  "actions_definies": "Actions définies pendant l'entretien",
  "dispositifs_mobilises": "Dispositifs à mobiliser",
  "observations": "Observations du conseiller",
  "prochaine_etape": "Prochaine étape et date prévisionnelle",
  "texte_complet": "Texte narratif complet du compte rendu (format paragraphe, copiable directement dans l'outil métier)"
}}

Le texte_complet doit être un texte professionnel de 200-300 mots, directement copiable dans un outil type France Travail. Vocabulaire professionnel, factuel, structuré."""

    try:
        response = await _call_llm(system_prompt, f"Dossier bénéficiaire:\n{context_text}\n{extra}", f"cr_{beneficiary_id}_{uuid.uuid4().hex[:8]}")
        cr_data = _parse_json_response(response)

        now = datetime.now(timezone.utc)
        report = {
            "id": str(uuid.uuid4()),
            "beneficiary_id": beneficiary_id,
            "partner_id": token_doc["id"],
            "type": payload.type_entretien,
            "date": now.strftime("%d/%m/%Y"),
            "content": cr_data,
            "notes_conseiller": payload.notes_conseiller,
            "ai_generated": True,
            "validated": False,
            "created_at": now.isoformat(),
        }

        await db.interview_reports.insert_one(report)
        report.pop("_id", None)

        await db.beneficiaires.update_one(
            {"id": beneficiary_id},
            {
                "$set": {"last_activity": now.isoformat()},
                "$push": {"historique": {"date": now.isoformat(), "action": "compte_rendu", "detail": f"{type_label} — compte rendu généré"}}
            }
        )
        return report
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erreur de format IA")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur IA: {str(e)}")


@router.get("/partenaires/beneficiaires/{beneficiary_id}/comptes-rendus")
async def get_comptes_rendus(beneficiary_id: str, token: str):
    """Get all interview reports for a beneficiary"""
    token_doc = await get_current_token(token)
    reports = await db.interview_reports.find(
        {"beneficiary_id": beneficiary_id, "partner_id": token_doc["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return reports


@router.put("/partenaires/comptes-rendus/{report_id}/valider")
async def valider_compte_rendu(report_id: str, token: str):
    """Validate an interview report"""
    token_doc = await get_current_token(token)
    report = await db.interview_reports.find_one(
        {"id": report_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not report:
        raise HTTPException(status_code=404, detail="Compte rendu non trouvé")

    now = datetime.now(timezone.utc)
    await db.interview_reports.update_one(
        {"id": report_id},
        {"$set": {"validated": True, "validated_at": now.isoformat()}}
    )
    return {"message": "Compte rendu validé", "validated_at": now.isoformat()}


# ===== 3. PLAN D'ACTION INTELLIGENT =====

@router.post("/partenaires/beneficiaires/{beneficiary_id}/plan-action/generer")
async def generate_plan_action(beneficiary_id: str, token: str):
    """Generate a smart action plan using AI"""
    token_doc = await get_current_token(token)
    ctx = await _get_beneficiaire_context(beneficiary_id, token_doc["id"])
    context_text = _build_context_text(ctx)

    system_prompt = """Tu es un expert en accompagnement vers l'emploi en France. Tu génères des plans d'action concrets et réalistes.

Génère un plan d'action au format JSON:
{
  "objectif_principal": "Objectif à 3-6 mois",
  "actions": [
    {
      "titre": "Titre de l'action",
      "description": "Description concrète",
      "categorie": "formation|emploi|administratif|personnel|accompagnement|reseau",
      "priorite": "haute|moyenne|basse",
      "echeance_jours": 14,
      "dispositif": "Dispositif concerné si applicable",
      "indicateur": "Comment mesurer la réalisation"
    }
  ],
  "dispositifs_recommandes": [
    {"nom": "Nom du dispositif", "raison": "Pourquoi", "acteur": "France Travail|Mission Locale|APEC|Région|Autre"}
  ],
  "jalons": [
    {"titre": "Jalon", "echeance_semaines": 4, "description": "Ce qui doit être atteint"}
  ],
  "risques": ["Risque identifié 1", "Risque 2"]
}

Maximum 8 actions, 4 dispositifs, 3 jalons, 3 risques. Sois concret et réaliste."""

    try:
        response = await _call_llm(system_prompt, f"Dossier bénéficiaire:\n{context_text}", f"plan_{beneficiary_id}")
        plan_data = _parse_json_response(response)

        now = datetime.now(timezone.utc)

        # Build action items with IDs and deadlines
        actions = []
        for a in plan_data.get("actions", []):
            echeance_days = a.get("echeance_jours", 30)
            actions.append({
                "id": str(uuid.uuid4()),
                "titre": a.get("titre", ""),
                "description": a.get("description", ""),
                "categorie": a.get("categorie", "accompagnement"),
                "priorite": a.get("priorite", "moyenne"),
                "echeance": (now + timedelta(days=echeance_days)).isoformat(),
                "dispositif": a.get("dispositif", ""),
                "indicateur": a.get("indicateur", ""),
                "status": "a_faire",
                "completed_at": None,
            })

        plan = {
            "id": str(uuid.uuid4()),
            "beneficiary_id": beneficiary_id,
            "partner_id": token_doc["id"],
            "objectif_principal": plan_data.get("objectif_principal", ""),
            "actions": actions,
            "dispositifs_recommandes": plan_data.get("dispositifs_recommandes", []),
            "jalons": plan_data.get("jalons", []),
            "risques": plan_data.get("risques", []),
            "ai_generated": True,
            "generated_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        # Upsert — replace existing plan
        existing = await db.action_plans.find_one(
            {"beneficiary_id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
        )
        if existing:
            await db.action_plans.update_one(
                {"id": existing["id"]},
                {"$set": {**plan, "id": existing["id"]}}
            )
            plan["id"] = existing["id"]
        else:
            await db.action_plans.insert_one(plan)
            plan.pop("_id", None)

        await db.beneficiaires.update_one(
            {"id": beneficiary_id},
            {
                "$set": {"last_activity": now.isoformat()},
                "$push": {"historique": {"date": now.isoformat(), "action": "plan_action", "detail": "Plan d'action intelligent généré"}}
            }
        )
        return plan
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erreur de format IA")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur IA: {str(e)}")


@router.get("/partenaires/beneficiaires/{beneficiary_id}/plan-action")
async def get_plan_action(beneficiary_id: str, token: str):
    """Get action plan for a beneficiary"""
    token_doc = await get_current_token(token)
    plan = await db.action_plans.find_one(
        {"beneficiary_id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not plan:
        return None
    return plan


class ActionStatusUpdate(BaseModel):
    status: str  # a_faire, en_cours, termine, annule


@router.put("/partenaires/plan-action/{plan_id}/actions/{action_id}")
async def update_action_status(plan_id: str, action_id: str, token: str, payload: ActionStatusUpdate):
    """Update status of an action item"""
    token_doc = await get_current_token(token)
    plan = await db.action_plans.find_one(
        {"id": plan_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan non trouvé")

    now = datetime.now(timezone.utc)
    actions = plan.get("actions", [])
    found = False
    for a in actions:
        if a["id"] == action_id:
            a["status"] = payload.status
            if payload.status == "termine":
                a["completed_at"] = now.isoformat()
            found = True
            break

    if not found:
        raise HTTPException(status_code=404, detail="Action non trouvée")

    await db.action_plans.update_one(
        {"id": plan_id},
        {"$set": {"actions": actions, "updated_at": now.isoformat()}}
    )
    return {"message": "Action mise à jour"}


# ===== 4. LECTURE RAPIDE =====

@router.get("/partenaires/beneficiaires/{beneficiary_id}/lecture-rapide")
async def get_lecture_rapide(beneficiary_id: str, token: str):
    """Get a quick-read summary of a beneficiary — designed for 2-minute pre-meeting prep"""
    token_doc = await get_current_token(token)
    ctx = await _get_beneficiaire_context(beneficiary_id, token_doc["id"])
    ben = ctx["ben"]

    # Compute risk score
    risk = _compute_risk_score(ben)

    # Build quick summary
    freins_actifs = [f for f in ben.get("freins", []) if f.get("status") != "resolu"]
    diag = ben.get("diagnostic", {})

    # Action plan summary
    plan = ctx["plan"]
    actions_summary = None
    if plan:
        total_actions = len(plan.get("actions", []))
        done = len([a for a in plan.get("actions", []) if a.get("status") == "termine"])
        en_cours = len([a for a in plan.get("actions", []) if a.get("status") == "en_cours"])
        en_retard = len([a for a in plan.get("actions", []) if a.get("status") == "a_faire" and a.get("echeance") and a["echeance"] < datetime.now(timezone.utc).isoformat()])
        actions_summary = {"total": total_actions, "terminees": done, "en_cours": en_cours, "en_retard": en_retard}

    # Last report
    last_report = ctx["reports"][0] if ctx["reports"] else None

    # Synthese
    synthese = ben.get("last_synthese", {}).get("data")

    return {
        "identite": {
            "nom": ben["name"],
            "secteur": ben.get("sector", "Non défini"),
            "statut": ben.get("status", "Inconnu"),
            "progression": ben.get("progress", 0),
            "synced": ben.get("synced", False),
            "pseudo_lie": ben.get("linked_pseudo"),
        },
        "diagnostic_resume": {
            "motivation": diag.get("motivation_level"),
            "posture": diag.get("posture"),
            "autonomie": diag.get("autonomie"),
            "contexte": diag.get("contexte_social", "")[:200],
        },
        "freins": [{"categorie": f["category"], "severite": f.get("severity", "moyen")} for f in freins_actifs],
        "competences_count": len(ben.get("skills_acquired", [])),
        "bilan_progress": ben.get("bilan_progress", 0),
        "risque_decrochage": risk,
        "plan_action": actions_summary,
        "dernier_compte_rendu": {
            "date": last_report["date"] if last_report else None,
            "type": last_report["type"] if last_report else None,
            "valide": last_report.get("validated") if last_report else None,
        } if last_report else None,
        "synthese_ia": synthese,
        "derniere_activite": ben.get("last_activity"),
        "cree_le": ben.get("created_at"),
    }


# ===== 5. DETECTION DE DECROCHAGE =====

def _compute_risk_score(ben):
    """Compute a dropout risk score (0-100)"""
    score = 0
    now = datetime.now(timezone.utc)

    # Inactivity
    last = ben.get("last_activity")
    if last:
        try:
            last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
            days_inactive = (now - last_dt).days
            if days_inactive > 30:
                score += 35
            elif days_inactive > 15:
                score += 20
            elif days_inactive > 7:
                score += 10
        except (ValueError, TypeError):
            score += 15

    # Critical barriers
    freins = ben.get("freins", [])
    critical_freins = [f for f in freins if f.get("status") != "resolu" and f.get("severity") == "critique"]
    score += min(len(critical_freins) * 15, 30)

    # Active barriers count
    active_freins = [f for f in freins if f.get("status") != "resolu"]
    if len(active_freins) >= 3:
        score += 10

    # Low motivation
    diag = ben.get("diagnostic", {})
    if diag.get("motivation_level") in ("faible", "a_travailler"):
        score += 15
    if diag.get("autonomie") in ("limitee", "tres_limitee"):
        score += 10

    # No progress
    if ben.get("progress", 0) == 0:
        score += 5

    # Status "En attente" for too long
    if ben.get("status") == "En attente":
        created = ben.get("created_at")
        if created:
            try:
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if (now - created_dt).days > 21:
                    score += 10
            except (ValueError, TypeError):
                pass

    return {
        "score": min(score, 100),
        "niveau": "critique" if score >= 60 else "eleve" if score >= 40 else "moyen" if score >= 20 else "faible",
        "facteurs": _get_risk_factors(ben, now),
    }


def _get_risk_factors(ben, now):
    factors = []
    last = ben.get("last_activity")
    if last:
        try:
            last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
            days = (now - last_dt).days
            if days > 7:
                factors.append(f"Inactif depuis {days} jours")
        except (ValueError, TypeError):
            pass

    freins = [f for f in ben.get("freins", []) if f.get("status") != "resolu"]
    critical = [f for f in freins if f.get("severity") == "critique"]
    if critical:
        factors.append(f"{len(critical)} frein(s) critique(s) non résolu(s)")
    if len(freins) >= 3:
        factors.append(f"{len(freins)} freins actifs")

    diag = ben.get("diagnostic", {})
    if diag.get("motivation_level") in ("faible", "a_travailler"):
        factors.append("Motivation faible")
    if diag.get("autonomie") in ("limitee", "tres_limitee"):
        factors.append("Autonomie limitée")

    if ben.get("progress", 0) == 0 and ben.get("synced"):
        factors.append("Aucune progression depuis la synchronisation")

    return factors


@router.get("/partenaires/beneficiaires/{beneficiary_id}/risque")
async def get_risque_decrochage(beneficiary_id: str, token: str):
    """Get dropout risk score for a beneficiary"""
    token_doc = await get_current_token(token)
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")
    return _compute_risk_score(ben)


@router.get("/partenaires/risques-globaux")
async def get_risques_globaux(token: str):
    """Get dropout risk scores for all beneficiaries"""
    token_doc = await get_current_token(token)
    beneficiaires = await db.beneficiaires.find(
        {"partner_id": token_doc["id"]}, {"_id": 0}
    ).to_list(500)

    results = []
    for ben in beneficiaires:
        risk = _compute_risk_score(ben)
        if risk["score"] >= 20:
            results.append({
                "beneficiary_id": ben["id"],
                "name": ben["name"],
                "status": ben.get("status"),
                "risque": risk,
            })

    results.sort(key=lambda r: r["risque"]["score"], reverse=True)
    return results


# ===== 6. EXPORT INTELLIGENT =====

@router.get("/partenaires/beneficiaires/{beneficiary_id}/export")
async def export_dossier(beneficiary_id: str, token: str, format: str = "text"):
    """Export beneficiary dossier in a copy-paste friendly format"""
    token_doc = await get_current_token(token)
    ctx = await _get_beneficiaire_context(beneficiary_id, token_doc["id"])
    ben = ctx["ben"]
    diag = ben.get("diagnostic", {})

    lines = []
    lines.append(f"DOSSIER BÉNÉFICIAIRE — {ben['name'].upper()}")
    lines.append(f"Date d'export: {datetime.now(timezone.utc).strftime('%d/%m/%Y')}")
    lines.append("=" * 60)
    lines.append("")

    # Section 1: Identité
    lines.append("1. IDENTITÉ ET SITUATION")
    lines.append("-" * 40)
    lines.append(f"Nom: {ben['name']}")
    lines.append(f"Statut: {ben.get('status', 'Non défini')}")
    lines.append(f"Secteur visé: {ben.get('sector', 'Non défini')}")
    lines.append(f"Progression: {ben.get('progress', 0)}%")
    if ben.get("linked_pseudo"):
        lines.append(f"Profil RE'ACTIF PRO: @{ben['linked_pseudo']}")
    lines.append("")

    # Section 2: Diagnostic
    lines.append("2. DIAGNOSTIC")
    lines.append("-" * 40)
    if diag.get("contexte_social"):
        lines.append(f"Contexte social: {diag['contexte_social']}")
    if diag.get("motivation_level"):
        labels = {"tres_elevee": "Très élevée", "elevee": "Élevée", "moyenne": "Moyenne", "faible": "Faible", "a_travailler": "À travailler"}
        lines.append(f"Motivation: {labels.get(diag['motivation_level'], diag['motivation_level'])}")
    if diag.get("posture"):
        lines.append(f"Posture: {diag['posture']}")
    if diag.get("autonomie"):
        lines.append(f"Autonomie: {diag['autonomie']}")
    if diag.get("mobilite_detail"):
        lines.append(f"Mobilité: {diag['mobilite_detail']}")
    if diag.get("observations"):
        lines.append(f"Observations: {diag['observations']}")
    lines.append("")

    # Section 3: Compétences
    skills = ben.get("skills_acquired", [])
    lines.append("3. COMPÉTENCES VALIDÉES")
    lines.append("-" * 40)
    if skills:
        for s in skills:
            lines.append(f"  - {s}")
    else:
        lines.append("  Aucune compétence validée")
    lines.append("")

    # Section 4: Freins
    freins = ben.get("freins", [])
    lines.append("4. FREINS PÉRIPHÉRIQUES")
    lines.append("-" * 40)
    actifs = [f for f in freins if f.get("status") != "resolu"]
    resolus = [f for f in freins if f.get("status") == "resolu"]
    if actifs:
        lines.append("Actifs:")
        for f in actifs:
            lines.append(f"  - [{f.get('severity', 'moyen').upper()}] {f['category']}: {f.get('description', '')}")
    if resolus:
        lines.append("Résolus:")
        for f in resolus:
            lines.append(f"  - {f['category']} (résolu)")
    if not freins:
        lines.append("  Aucun frein déclaré")
    lines.append("")

    # Section 5: Plan d'action
    plan = ctx["plan"]
    lines.append("5. PLAN D'ACTION")
    lines.append("-" * 40)
    if plan:
        lines.append(f"Objectif: {plan.get('objectif_principal', 'Non défini')}")
        for a in plan.get("actions", []):
            status_map = {"a_faire": "À FAIRE", "en_cours": "EN COURS", "termine": "TERMINÉ", "annule": "ANNULÉ"}
            lines.append(f"  [{status_map.get(a['status'], a['status'])}] {a['titre']}")
            if a.get("description"):
                lines.append(f"    {a['description']}")
    else:
        lines.append("  Aucun plan d'action défini")
    lines.append("")

    # Section 6: Historique
    lines.append("6. HISTORIQUE DU PARCOURS")
    lines.append("-" * 40)
    for h in (ben.get("historique", []) or [])[-10:]:
        date_str = ""
        try:
            date_str = datetime.fromisoformat(h["date"].replace("Z", "+00:00")).strftime("%d/%m/%Y")
        except (ValueError, TypeError, KeyError):
            pass
        lines.append(f"  {date_str} — {h.get('detail', h.get('action', ''))}")
    lines.append("")

    # Section 7: Profil RE'ACTIF PRO
    if ctx["profile"] or ctx["passport"] or ctx["dclic"]:
        lines.append("7. DONNÉES RE'ACTIF PRO")
        lines.append("-" * 40)
        if ctx["profile"]:
            p = ctx["profile"]
            if p.get("sectors"):
                lines.append(f"Secteurs: {', '.join(p['sectors'])}")
            if p.get("skills"):
                skills_names = [s.get("name", str(s)) if isinstance(s, dict) else str(s) for s in p["skills"][:20]]
                lines.append(f"Compétences: {', '.join(skills_names)}")
        if ctx["passport"]:
            pp = ctx["passport"]
            if pp.get("professional_summary"):
                lines.append(f"Synthèse pro: {pp['professional_summary'][:500]}")
            if pp.get("career_project"):
                lines.append(f"Projet pro: {pp['career_project'][:500]}")
        if ctx["dclic"] and ctx["dclic"].get("scores"):
            scores = ", ".join(f"{k}: {v}" for k, v in ctx["dclic"]["scores"].items() if isinstance(v, (int, float)))
            lines.append(f"Scores D'CLIC: {scores}")

    text = "\n".join(lines)

    if format == "text":
        return {"content": text, "format": "text"}
    else:
        return {"content": text, "format": "text"}


# ===== 7. BILAN FINAL =====

@router.post("/partenaires/beneficiaires/{beneficiary_id}/bilan-final")
async def generate_bilan_final(beneficiary_id: str, token: str):
    """Generate a final assessment for end of journey"""
    token_doc = await get_current_token(token)
    ctx = await _get_beneficiaire_context(beneficiary_id, token_doc["id"])
    context_text = _build_context_text(ctx)

    # Add action plan info
    plan = ctx["plan"]
    if plan:
        actions = plan.get("actions", [])
        done = len([a for a in actions if a.get("status") == "termine"])
        total = len(actions)
        context_text += f"\nPlan d'action: {done}/{total} actions terminées"
        context_text += f"\nObjectif: {plan.get('objectif_principal', '')}"

    # Add interview reports count
    reports = ctx["reports"]
    if reports:
        context_text += f"\nEntretiens réalisés: {len(reports)}"

    system_prompt = """Tu es un expert en accompagnement vers l'emploi. Tu rédiges un bilan de fin de parcours professionnel et complet.

Génère un bilan final au format JSON:
{
  "titre": "Bilan de fin de parcours",
  "synthese_globale": "Synthèse globale du parcours d'accompagnement (5-6 phrases)",
  "competences_developpees": ["Compétence 1", "Compétence 2"],
  "competences_transversales": ["Soft skill 1", "Soft skill 2"],
  "freins_leves": ["Frein résolu 1"],
  "freins_restants": ["Frein non résolu 1"],
  "actions_realisees": ["Action 1", "Action 2"],
  "evolution_observee": "Description de l'évolution du bénéficiaire",
  "recommandations_suite": ["Recommandation 1 pour la suite", "Recommandation 2"],
  "dispositifs_a_maintenir": ["Dispositif à continuer"],
  "texte_bilan_complet": "Texte narratif complet du bilan (300-400 mots, format professionnel, copiable dans outil métier)"
}

Sois factuel, valorisant mais réaliste. Le texte doit être directement exploitable."""

    try:
        response = await _call_llm(system_prompt, f"Dossier complet:\n{context_text}", f"bilan_{beneficiary_id}")
        bilan_data = _parse_json_response(response)

        now = datetime.now(timezone.utc)
        bilan = {
            "id": str(uuid.uuid4()),
            "beneficiary_id": beneficiary_id,
            "partner_id": token_doc["id"],
            "content": bilan_data,
            "ai_generated": True,
            "validated": False,
            "created_at": now.isoformat(),
        }

        await db.bilan_finals.insert_one(bilan)
        bilan.pop("_id", None)

        await db.beneficiaires.update_one(
            {"id": beneficiary_id},
            {
                "$set": {"last_activity": now.isoformat(), "bilan_final": bilan_data},
                "$push": {"historique": {"date": now.isoformat(), "action": "bilan_final", "detail": "Bilan de fin de parcours généré"}}
            }
        )
        return bilan
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erreur de format IA")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur IA: {str(e)}")


@router.get("/partenaires/beneficiaires/{beneficiary_id}/bilan-final")
async def get_bilan_final(beneficiary_id: str, token: str):
    """Get the latest final assessment"""
    token_doc = await get_current_token(token)
    bilan = await db.bilan_finals.find_one(
        {"beneficiary_id": beneficiary_id, "partner_id": token_doc["id"]},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    return bilan
