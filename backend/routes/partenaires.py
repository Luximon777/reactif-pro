from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from db import db
from helpers import get_current_token
from datetime import datetime, timezone, timedelta
import uuid
import os

router = APIRouter()


# ===== DASHBOARD STATS =====

@router.get("/partenaires/stats")
async def get_partenaire_stats(token: str):
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

    total_freins = 0
    freins_resolus = 0
    for b in beneficiaires:
        for frein in b.get("freins", []):
            total_freins += 1
            if frein.get("status") == "resolu":
                freins_resolus += 1

    linked_count = sum(1 for b in beneficiaires if b.get("linked_token_id"))

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
        "linked_profiles": linked_count,
    }


# ===== ALERTES =====

@router.get("/partenaires/alertes")
async def get_partenaire_alertes(token: str):
    token_doc = await get_current_token(token)
    partner_id = token_doc["id"]

    beneficiaires = await db.beneficiaires.find(
        {"partner_id": partner_id}, {"_id": 0}
    ).to_list(500)

    alertes = []
    now = datetime.now(timezone.utc)
    seuil_inactivite = now - timedelta(days=15)

    for b in beneficiaires:
        last = b.get("last_activity")
        if last:
            try:
                last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
                if last_dt < seuil_inactivite and b.get("status") not in ["En emploi"]:
                    days_inactive = (now - last_dt).days
                    alertes.append({
                        "type": "inactivite",
                        "severity": "critique" if days_inactive > 30 else "eleve",
                        "beneficiaire_id": b["id"],
                        "beneficiaire_name": b["name"],
                        "message": f"Inactif depuis {days_inactive} jours",
                        "date": last
                    })
            except (ValueError, TypeError):
                pass

        for frein in b.get("freins", []):
            if frein.get("status") != "resolu" and frein.get("severity") == "critique":
                alertes.append({
                    "type": "frein_critique",
                    "severity": "critique",
                    "beneficiaire_id": b["id"],
                    "beneficiaire_name": b["name"],
                    "message": f"Frein critique non résolu : {frein.get('category', 'inconnu')}",
                    "date": frein.get("created_at", "")
                })

        if b.get("status") == "En attente":
            created = b.get("created_at", "")
            if created:
                try:
                    created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    if created_dt < seuil_inactivite:
                        alertes.append({
                            "type": "attente_prolongee",
                            "severity": "moyen",
                            "beneficiaire_id": b["id"],
                            "beneficiaire_name": b["name"],
                            "message": "En attente depuis plus de 15 jours",
                            "date": created
                        })
                except (ValueError, TypeError):
                    pass

    alertes.sort(key=lambda a: {"critique": 0, "eleve": 1, "moyen": 2}.get(a["severity"], 3))
    return alertes


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
        "diagnostic": {},
        "linked_token_id": None,
        "historique": [{
            "date": datetime.now(timezone.utc).isoformat(),
            "action": "creation",
            "detail": "Creation du suivi"
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
    details = []

    if status and status != ben.get("status"):
        update_data["status"] = status
        details.append(f"Statut: {ben.get('status')} -> {status}")
    if progress is not None:
        update_data["progress"] = progress
        details.append(f"Progression: {progress}%")
    if notes is not None:
        update_data["notes"] = notes
    if sector:
        update_data["sector"] = sector

    hist_entry["detail"] = " | ".join(details) if details else "Mise a jour"

    await db.beneficiaires.update_one(
        {"id": beneficiary_id},
        {"$set": update_data, "$push": {"historique": hist_entry}}
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


# ===== LIAISON PROFIL RE'ACTIF PRO =====

@router.post("/partenaires/beneficiaires/{beneficiary_id}/link")
async def link_beneficiaire_to_user(beneficiary_id: str, token: str, pseudo: str):
    """Link a beneficiary to a Re'Actif Pro user by pseudo"""
    token_doc = await get_current_token(token)
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")

    user_profile = await db.profiles.find_one({"pseudo": pseudo}, {"_id": 0, "password_hash": 0})
    if not user_profile:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé avec ce pseudo")

    user_token_id = user_profile["token_id"]

    await db.consent_history.insert_one({
        "id": str(uuid.uuid4()),
        "type": "partenaire_link",
        "user_token_id": user_token_id,
        "partner_id": token_doc["id"],
        "beneficiary_id": beneficiary_id,
        "accepted": True,
        "date": datetime.now(timezone.utc).isoformat()
    })

    await db.beneficiaires.update_one(
        {"id": beneficiary_id},
        {
            "$set": {
                "linked_token_id": user_token_id,
                "linked_pseudo": pseudo,
                "last_activity": datetime.now(timezone.utc).isoformat()
            },
            "$push": {
                "historique": {
                    "date": datetime.now(timezone.utc).isoformat(),
                    "action": "link",
                    "detail": f"Profil lié à l'utilisateur {pseudo}"
                }
            }
        }
    )
    return {"message": "Profil lié avec succès", "linked_token_id": user_token_id}


@router.delete("/partenaires/beneficiaires/{beneficiary_id}/link")
async def unlink_beneficiaire(beneficiary_id: str, token: str):
    token_doc = await get_current_token(token)
    await db.beneficiaires.update_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]},
        {
            "$set": {"linked_token_id": None, "linked_pseudo": None},
            "$push": {
                "historique": {
                    "date": datetime.now(timezone.utc).isoformat(),
                    "action": "unlink",
                    "detail": "Liaison profil supprimée"
                }
            }
        }
    )
    return {"message": "Liaison supprimée"}


@router.get("/partenaires/beneficiaires/{beneficiary_id}/linked-profile")
async def get_linked_profile(beneficiary_id: str, token: str):
    """Get the linked Re'Actif Pro user's full profile (skills, CV, passport, D'CLIC)"""
    token_doc = await get_current_token(token)
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")
    if not ben.get("linked_token_id"):
        raise HTTPException(status_code=400, detail="Aucun profil lie")

    user_tid = ben["linked_token_id"]

    profile = await db.profiles.find_one({"token_id": user_tid}, {"_id": 0, "password_hash": 0})
    passport = await db.passports.find_one({"token_id": user_tid}, {"_id": 0})
    cv_analyses = await db.cv_analyses.find({"token_id": user_tid}, {"_id": 0}).to_list(10)
    dclic = await db.dclic_results.find_one({"token_id": user_tid}, {"_id": 0})

    return {
        "profile": profile,
        "passport": passport,
        "cv_analyses": cv_analyses,
        "dclic_results": dclic,
    }


# ===== DIAGNOSTIC ENRICHI =====

class DiagnosticUpdate(BaseModel):
    contexte_social: Optional[str] = None
    mobilite_detail: Optional[str] = None
    motivation_level: Optional[str] = None
    posture: Optional[str] = None
    autonomie: Optional[str] = None
    soft_skills: Optional[List[str]] = None
    observations: Optional[str] = None


@router.put("/partenaires/beneficiaires/{beneficiary_id}/diagnostic")
async def update_diagnostic(beneficiary_id: str, token: str, data: DiagnosticUpdate):
    token_doc = await get_current_token(token)
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")

    diag = ben.get("diagnostic", {})
    update_fields = data.model_dump(exclude_none=True)
    diag.update(update_fields)
    diag["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.beneficiaires.update_one(
        {"id": beneficiary_id},
        {
            "$set": {
                "diagnostic": diag,
                "last_activity": datetime.now(timezone.utc).isoformat()
            },
            "$push": {
                "historique": {
                    "date": datetime.now(timezone.utc).isoformat(),
                    "action": "diagnostic",
                    "detail": f"Diagnostic enrichi mis à jour ({', '.join(update_fields.keys())})"
                }
            }
        }
    )
    return {"diagnostic": diag}


# ===== ORIENTATION IA =====

@router.post("/partenaires/beneficiaires/{beneficiary_id}/orientation")
async def get_orientation_ia(beneficiary_id: str, token: str):
    """Generate AI-based orientation recommendations for a beneficiary"""
    token_doc = await get_current_token(token)
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")

    profile_data = None
    passport_data = None
    dclic_data = None

    if ben.get("linked_token_id"):
        user_tid = ben["linked_token_id"]
        profile_data = await db.profiles.find_one({"token_id": user_tid}, {"_id": 0, "password_hash": 0})
        passport_data = await db.passports.find_one({"token_id": user_tid}, {"_id": 0})
        dclic_data = await db.dclic_results.find_one({"token_id": user_tid}, {"_id": 0})

    context_parts = [f"Nom: {ben['name']}", f"Secteur vise: {ben.get('sector', 'non defini')}"]

    if ben.get("skills_acquired"):
        context_parts.append(f"Compétences validées: {', '.join(ben['skills_acquired'])}")

    freins_actifs = [f for f in ben.get("freins", []) if f.get("status") != "resolu"]
    if freins_actifs:
        context_parts.append(f"Freins périphériques actifs: {', '.join(f['category'] for f in freins_actifs)}")

    diag = ben.get("diagnostic", {})
    if diag:
        if diag.get("contexte_social"):
            context_parts.append(f"Contexte social: {diag['contexte_social']}")
        if diag.get("motivation_level"):
            context_parts.append(f"Motivation: {diag['motivation_level']}")
        if diag.get("soft_skills"):
            context_parts.append(f"Soft skills: {', '.join(diag['soft_skills'])}")

    if profile_data:
        if profile_data.get("skills"):
            skills_list = [s.get("name", str(s)) if isinstance(s, dict) else str(s) for s in profile_data["skills"][:15]]
            context_parts.append(f"Compétences Re'Actif Pro: {', '.join(skills_list)}")
        if profile_data.get("sectors"):
            context_parts.append(f"Secteurs: {', '.join(profile_data['sectors'])}")

    if passport_data:
        if passport_data.get("professional_summary"):
            context_parts.append(f"Synthese pro: {passport_data['professional_summary'][:300]}")
        if passport_data.get("career_project"):
            context_parts.append(f"Projet professionnel: {passport_data['career_project'][:300]}")

    if dclic_data:
        if dclic_data.get("scores"):
            scores_str = ", ".join(f"{k}: {v}" for k, v in dclic_data["scores"].items() if isinstance(v, (int, float)))
            context_parts.append(f"Scores D'CLIC: {scores_str}")

    beneficiary_context = "\n".join(context_parts)

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        import asyncio
        emergent_api_key = os.environ.get("EMERGENT_LLM_KEY", "")

        system_prompt = """Tu es un expert en preparation et securisation des parcours professionnels en France.
Tu travailles dans le cadre de RE'ACTIF PRO, une interface de coordination qui agit en complementarite des dispositifs existants (Orient'Est, EURES, France Travail).

POSTURE IMPORTANTE:
- Tu ne fais PAS de l'orientation a la place des services existants
- Tu PREPARES le profil, REVELES les competences, IDENTIFIES les freins et SECURISES le passage a l'action
- Tu ORIENTES VERS les dispositifs existants quand c'est pertinent
- Tu fournis des pistes de preparation, pas des decisions d'orientation

Reponds TOUJOURS en JSON avec cette structure exacte:
{
  "metiers_recommandes": [
    {"titre": "...", "compatibilite": 85, "raison": "..."}
  ],
  "formations_suggerees": [
    {"titre": "...", "type": "certifiante|qualifiante|courte", "raison": "..."}
  ],
  "dispositifs_adaptes": [
    {"nom": "...", "description": "...", "pertinence": "haute|moyenne"}
  ],
  "actions_immediates": ["..."],
  "points_vigilance": ["..."]
}

Dans "dispositifs_adaptes", inclus quand pertinent:
- Les ressources Orient'Est (information metiers, formations regionales)
- Le reseau EURES (si potentiel de mobilite europeenne ou transfrontaliere)
- Les dispositifs France Travail (offres, aides, accompagnement)
- Les Missions Locales (insertion jeunes 16-25 ans)
- L'APEC (cadres et evolution professionnelle)
- Les politiques de la Region Grand Est (formations, aides regionales)

Base tes recommandations sur:
- Le profil reel (pas seulement le diplome)
- Les contraintes (freins peripheriques, handicap, mobilite)
- Les competences transversales et soft skills
- Le bassin d'emploi et les tensions metiers
Maximum 4 elements par categorie. Sois concret et realiste."""

        session_id = f"orientation_{beneficiary_id}"
        chat = LlmChat(
            api_key=emergent_api_key,
            session_id=session_id,
            system_message=system_prompt,
        ).with_model("openai", "gpt-4.1-mini")
        
        user_message = UserMessage(text=f"Voici le profil du beneficiaire:\n\n{beneficiary_context}")
        
        # send_message is async
        response_text = await chat.send_message(user_message)
        response_text = response_text.strip()

        import json
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        orientation = json.loads(response_text)

        await db.beneficiaires.update_one(
            {"id": beneficiary_id},
            {
                "$set": {
                    "last_orientation": {
                        "data": orientation,
                        "generated_at": datetime.now(timezone.utc).isoformat()
                    },
                    "last_activity": datetime.now(timezone.utc).isoformat()
                },
                "$push": {
                    "historique": {
                        "date": datetime.now(timezone.utc).isoformat(),
                        "action": "orientation_ia",
                        "detail": "Orientation IA générée"
                    }
                }
            }
        )

        return orientation

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur IA: {str(e)}")


# ===== FREINS PERIPHERIQUES =====

@router.post("/partenaires/beneficiaires/{beneficiary_id}/freins")
async def add_frein(beneficiary_id: str, token: str, category: str, description: str = "", severity: str = "moyen"):
    token_doc = await get_current_token(token)
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")

    valid_categories = ["logement", "sante", "mobilite", "garde_enfant", "handicap", "administratif", "financier", "autre"]
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Categorie invalide. Valeurs: {', '.join(valid_categories)}")

    frein = {
        "id": str(uuid.uuid4()),
        "category": category,
        "description": description,
        "severity": severity,
        "status": "actif",
        "solution": "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "resolved_at": None,
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
    token_doc = await get_current_token(token)
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")

    freins = ben.get("freins", [])
    updated = False
    target_frein = None
    for frein in freins:
        if frein["id"] == frein_id:
            if status:
                frein["status"] = status
                if status == "resolu":
                    frein["resolved_at"] = datetime.now(timezone.utc).isoformat()
            if solution is not None:
                frein["solution"] = solution
            target_frein = frein
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
    return {"message": "Frein mis à jour", "frein": target_frein}


# ===== SKILLS =====

@router.post("/partenaires/beneficiaires/{beneficiary_id}/skills")
async def add_skill(beneficiary_id: str, token: str, skill: str):
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
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    profile.pop("password_hash", None)
    return profile


# ===== CONTRIBUTION OBSERVATOIRE =====

@router.post("/partenaires/contribution-observatoire")
async def contribute_to_observatoire(token: str):
    """Aggregate partenaire data into observatoire signals"""
    token_doc = await get_current_token(token)
    partner_id = token_doc["id"]
    profile = await db.profiles.find_one({"token_id": partner_id}, {"_id": 0})

    beneficiaires = await db.beneficiaires.find(
        {"partner_id": partner_id}, {"_id": 0}
    ).to_list(500)

    freins_count = {}
    skills_count = {}
    sectors_count = {}

    for b in beneficiaires:
        for f in b.get("freins", []):
            if f.get("status") != "resolu":
                cat = f.get("category", "autre")
                freins_count[cat] = freins_count.get(cat, 0) + 1
        for s in b.get("skills_acquired", []):
            skills_count[s] = skills_count.get(s, 0) + 1
        sector = b.get("sector", "Autre")
        sectors_count[sector] = sectors_count.get(sector, 0) + 1

    signal = {
        "id": str(uuid.uuid4()),
        "source": "partenaire",
        "partner_id": partner_id,
        "structure_name": profile.get("company_name", "Structure partenaire") if profile else "Structure partenaire",
        "date": datetime.now(timezone.utc).isoformat(),
        "data": {
            "total_beneficiaires": len(beneficiaires),
            "freins_repartition": freins_count,
            "competences_emergentes": dict(sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:10]),
            "secteurs_tension": dict(sorted(sectors_count.items(), key=lambda x: x[1], reverse=True)[:5]),
        }
    }

    await db.ubuntoo_signals.insert_one(signal)
    signal.pop("_id", None)
    return {"message": "Contribution envoyée à l'Observatoire", "signal": signal}


# ===== SEARCH USERS =====

@router.get("/partenaires/search-users")
async def search_users(token: str, query: str):
    """Search Re'Actif Pro users by pseudo for linking"""
    await get_current_token(token)
    if len(query) < 2:
        return []

    users = await db.profiles.find(
        {
            "pseudo": {"$regex": query, "$options": "i"},
            "role": "particulier"
        },
        {"_id": 0, "password_hash": 0, "email_recovery": 0}
    ).to_list(10)

    results = []
    for u in users:
        results.append({
            "pseudo": u.get("pseudo"),
            "display_name": u.get("display_name") or u.get("name", "Anonyme"),
            "sectors": u.get("sectors", []),
            "skills_count": len(u.get("skills", [])),
            "token_id": u.get("token_id"),
        })
    return results


@router.get("/partenaires/demande-acces/search")
async def search_users_by_name(token: str, query: str, identifiant_ft: str = None):
    """Search Re'Actif Pro users by identifiant France Travail + name — only returns users with visibility limited or public"""
    await get_current_token(token)
    if len(query) < 2 and not identifiant_ft:
        return []

    # Build search filter
    filter_conditions = {
        "role": "particulier",
        "visibility_level": {"$in": ["limited", "public"]},
    }

    # If identifiant France Travail provided, search by it
    if identifiant_ft and identifiant_ft.strip():
        ft_clean = identifiant_ft.strip()
        name_regex = {"$regex": query, "$options": "i"} if query and len(query) >= 2 else None

        # Search by FT ID + name
        if name_regex:
            filter_conditions["identifiant_france_travail"] = {"$regex": ft_clean, "$options": "i"}
            filter_conditions["$or"] = [
                {"real_first_name": name_regex},
                {"real_last_name": name_regex},
                {"display_name": name_regex},
            ]
        else:
            filter_conditions["identifiant_france_travail"] = {"$regex": ft_clean, "$options": "i"}
    else:
        # Fallback: search by name only
        regex = {"$regex": query, "$options": "i"}
        filter_conditions["$or"] = [
            {"real_first_name": regex},
            {"real_last_name": regex},
            {"display_name": regex},
        ]

    users = await db.profiles.find(
        filter_conditions,
        {"_id": 0, "password_hash": 0, "email_recovery": 0}
    ).to_list(20)

    # Check D'CLIC completion and profile boost for each user
    results = []
    for u in users:
        first = u.get("real_first_name") or ""
        last = u.get("real_last_name") or ""
        full_name = f"{first} {last}".strip() or u.get("display_name") or u.get("name", "Anonyme")

        # Check if D'CLIC test is completed
        tid = u.get("token_id")
        dclic = await db.dclic_results.find_one({"token_id": tid}, {"_id": 0, "token_id": 1})
        has_dclic = dclic is not None

        # Check if profile is boosted (has skills or passport)
        has_skills = len(u.get("skills", [])) > 0
        passport = await db.passports.find_one({"token_id": tid}, {"_id": 0, "token_id": 1})
        has_passport = passport is not None
        profile_boosted = has_skills or has_passport

        # User must have: visibility limited + D'CLIC done + profile boosted
        authorized = (u.get("visibility_level") == "limited" and has_dclic and profile_boosted)

        results.append({
            "token_id": tid,
            "profile_id": u.get("id"),
            "full_name": full_name,
            "real_first_name": first,
            "real_last_name": last,
            "pseudo": u.get("pseudo"),
            "display_name": u.get("display_name"),
            "visibility_level": u.get("visibility_level"),
            "identifiant_france_travail": u.get("identifiant_france_travail"),
            "sectors": u.get("sectors", []),
            "skills_count": len(u.get("skills", [])),
            "has_dclic": has_dclic,
            "profile_boosted": profile_boosted,
            "authorized": authorized,
        })
    return results


class SyncRequest(BaseModel):
    user_token_id: str


class AccessRequestResponse(BaseModel):
    action: str  # "accept" or "reject"


# ===== DEMANDE D'ACCES (APPROBATION PAR LE BENEFICIAIRE) =====

@router.post("/partenaires/demande-acces/request")
async def create_access_request(token: str, payload: SyncRequest):
    """Partner sends an access request to a RE'ACTIF PRO user — requires user approval"""
    token_doc = await get_current_token(token)
    partner_id = token_doc["id"]

    profile = await db.profiles.find_one(
        {"token_id": payload.user_token_id, "role": "particulier"},
        {"_id": 0, "password_hash": 0, "email_recovery": 0}
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Profil utilisateur non trouvé")

    if profile.get("visibility_level") not in ("limited", "public"):
        raise HTTPException(status_code=403, detail="Accès non autorisé — l'utilisateur n'a pas ouvert son profil")

    existing = await db.access_requests.find_one(
        {"partner_id": partner_id, "user_token_id": payload.user_token_id, "status": {"$in": ["en_attente", "accepte"]}},
        {"_id": 0}
    )
    if existing:
        if existing["status"] == "en_attente":
            raise HTTPException(status_code=409, detail="Une demande est déjà en attente pour ce bénéficiaire")
        if existing["status"] == "accepte":
            raise HTTPException(status_code=409, detail="L'accès a déjà été accordé")

    partner_profile = await db.profiles.find_one({"token_id": partner_id}, {"_id": 0})
    partner_name = partner_profile.get("company_name") or partner_profile.get("display_name") or partner_profile.get("name", "Partenaire")

    first = profile.get("real_first_name") or ""
    last = profile.get("real_last_name") or ""
    user_full_name = f"{first} {last}".strip() or profile.get("display_name") or "Anonyme"

    now = datetime.now(timezone.utc)
    request_doc = {
        "id": str(uuid.uuid4()),
        "partner_id": partner_id,
        "partner_name": partner_name,
        "user_token_id": payload.user_token_id,
        "user_name": user_full_name,
        "user_pseudo": profile.get("pseudo"),
        "status": "en_attente",
        "created_at": now.isoformat(),
        "responded_at": None,
    }

    await db.access_requests.insert_one(request_doc)
    request_doc.pop("_id", None)
    return request_doc


@router.get("/partenaires/demande-acces/status")
async def get_access_requests_partner(token: str):
    """Get all access requests sent by this partner"""
    token_doc = await get_current_token(token)
    requests = await db.access_requests.find(
        {"partner_id": token_doc["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return requests


# Endpoints for the beneficiary (user side)
@router.get("/notifications/access-requests")
async def get_access_requests_user(token: str):
    """Get pending access requests for the current user"""
    token_doc = await get_current_token(token)
    requests = await db.access_requests.find(
        {"user_token_id": token_doc["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return requests


@router.post("/notifications/access-requests/{request_id}/respond")
async def respond_access_request(request_id: str, token: str, payload: AccessRequestResponse):
    """Beneficiary accepts or rejects an access request"""
    token_doc = await get_current_token(token)

    req = await db.access_requests.find_one(
        {"id": request_id, "user_token_id": token_doc["id"]},
        {"_id": 0}
    )
    if not req:
        raise HTTPException(status_code=404, detail="Demande non trouvée")

    if req["status"] != "en_attente":
        raise HTTPException(status_code=400, detail="Cette demande a déjà été traitée")

    if payload.action not in ("accept", "reject"):
        raise HTTPException(status_code=400, detail="Action invalide: accept ou reject")

    now = datetime.now(timezone.utc)
    new_status = "accepte" if payload.action == "accept" else "refuse"

    await db.access_requests.update_one(
        {"id": request_id},
        {"$set": {"status": new_status, "responded_at": now.isoformat()}}
    )

    return {"message": f"Demande {new_status}", "status": new_status}


@router.post("/partenaires/demande-acces/synchroniser")
async def synchroniser_beneficiaire(token: str, payload: SyncRequest):
    """Sync profile — only works if the access request was approved by the beneficiary"""
    token_doc = await get_current_token(token)
    partner_id = token_doc["id"]

    approved = await db.access_requests.find_one(
        {"partner_id": partner_id, "user_token_id": payload.user_token_id, "status": "accepte"},
        {"_id": 0}
    )
    if not approved:
        raise HTTPException(status_code=403, detail="Accès non autorisé — le bénéficiaire n'a pas encore accepté votre demande")

    profile = await db.profiles.find_one(
        {"token_id": payload.user_token_id, "role": "particulier"},
        {"_id": 0, "password_hash": 0, "email_recovery": 0}
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Profil utilisateur non trouvé")

    existing = await db.beneficiaires.find_one(
        {"partner_id": partner_id, "linked_token_id": payload.user_token_id},
        {"_id": 0}
    )
    if existing:
        raise HTTPException(status_code=409, detail="Ce bénéficiaire est déjà synchronisé")

    first = profile.get("real_first_name") or ""
    last = profile.get("real_last_name") or ""
    full_name = f"{first} {last}".strip() or profile.get("display_name") or profile.get("name", "Anonyme")

    passport = await db.passports.find_one({"token_id": payload.user_token_id}, {"_id": 0})
    cv_analyses = await db.cv_analyses.find({"token_id": payload.user_token_id}, {"_id": 0}).to_list(10)
    dclic = await db.dclic_results.find_one({"token_id": payload.user_token_id}, {"_id": 0})

    skills_from_profile = [s.get("name", "") for s in profile.get("skills", []) if s.get("name")]
    skills_from_passport = []
    if passport:
        for comp in passport.get("competences", []):
            if isinstance(comp, dict):
                skills_from_passport.append(comp.get("nom", comp.get("name", "")))
            elif isinstance(comp, str):
                skills_from_passport.append(comp)
    all_skills = list(set(s for s in skills_from_profile + skills_from_passport if s))

    sectors = profile.get("sectors", [])
    sector = sectors[0] if sectors else "Autre"

    # Calcul automatique de la progression basée sur les données synchronisées
    progress_points = 0
    # Profil de base rempli (nom, secteurs) = 10%
    if full_name and full_name != "Anonyme":
        progress_points += 5
    if sectors:
        progress_points += 5
    # Compétences identifiées = 20%
    if all_skills:
        progress_points += min(20, len(all_skills) * 4)
    # CV analysé = 20%
    if cv_analyses:
        progress_points += 20
    # Passeport de compétences = 25%
    if passport:
        progress_points += 10
        if passport.get("professional_summary"):
            progress_points += 8
        if passport.get("career_project"):
            progress_points += 7
    # Test D'CLIC réalisé = 25%
    if dclic:
        progress_points += 25
    sync_progress = min(progress_points, 100)

    now = datetime.now(timezone.utc)
    beneficiary = {
        "id": str(uuid.uuid4()),
        "name": full_name,
        "status": "En accompagnement",
        "progress": sync_progress,
        "skills_acquired": all_skills[:20],
        "sector": sector,
        "notes": f"Synchronisé depuis RE'ACTIF PRO le {now.strftime('%d/%m/%Y')}",
        "freins": [],
        "diagnostic": {},
        "linked_token_id": payload.user_token_id,
        "linked_pseudo": profile.get("pseudo"),
        "synced": True,
        "sync_date": now.isoformat(),
        "sync_data": {
            "profile_score": profile.get("profile_score", 0),
            "experience_years": profile.get("experience_years", 0),
            "strengths": profile.get("strengths", []),
            "gaps": profile.get("gaps", []),
            "dclic_summary": dclic.get("summary") if dclic else None,
            "cv_count": len(cv_analyses),
            "passport_competences_count": len(passport.get("competences", [])) if passport else 0,
        },
        "historique": [{
            "date": now.isoformat(),
            "action": "sync",
            "detail": f"Profil synchronisé depuis RE'ACTIF PRO ({profile.get('pseudo', 'N/A')})"
        }],
        "last_activity": now.isoformat(),
        "created_at": now.isoformat(),
        "partner_id": partner_id,
    }

    await db.beneficiaires.insert_one(beneficiary)
    beneficiary.pop("_id", None)

    await db.consent_history.insert_one({
        "id": str(uuid.uuid4()),
        "type": "partenaire_sync",
        "user_token_id": payload.user_token_id,
        "partner_id": partner_id,
        "beneficiary_id": beneficiary["id"],
        "accepted": True,
        "date": now.isoformat()
    })

    return beneficiary


@router.post("/partenaires/beneficiaires/{beneficiary_id}/resync")
async def resync_beneficiaire(beneficiary_id: str, token: str):
    """Re-sync a linked beneficiary's data and recalculate progress"""
    token_doc = await get_current_token(token)
    partner_id = token_doc["id"]

    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": partner_id}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")
    if not ben.get("linked_token_id"):
        raise HTTPException(status_code=400, detail="Ce bénéficiaire n'est pas lié à un profil RE'ACTIF PRO")

    user_tid = ben["linked_token_id"]
    profile = await db.profiles.find_one(
        {"token_id": user_tid, "role": "particulier"},
        {"_id": 0, "password_hash": 0, "email_recovery": 0}
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Profil utilisateur non trouvé")

    passport = await db.passports.find_one({"token_id": user_tid}, {"_id": 0})
    cv_analyses = await db.cv_analyses.find({"token_id": user_tid}, {"_id": 0}).to_list(10)
    dclic = await db.dclic_results.find_one({"token_id": user_tid}, {"_id": 0})

    skills_from_profile = [s.get("name", "") for s in profile.get("skills", []) if s.get("name")]
    skills_from_passport = []
    if passport:
        for comp in passport.get("competences", []):
            if isinstance(comp, dict):
                skills_from_passport.append(comp.get("nom", comp.get("name", "")))
            elif isinstance(comp, str):
                skills_from_passport.append(comp)
    all_skills = list(set(s for s in skills_from_profile + skills_from_passport if s))

    first = profile.get("real_first_name") or ""
    last = profile.get("real_last_name") or ""
    full_name = f"{first} {last}".strip() or profile.get("display_name") or profile.get("name", "Anonyme")

    sectors = profile.get("sectors", [])
    sector = sectors[0] if sectors else ben.get("sector", "Autre")

    # Calcul de la progression
    progress_points = 0
    if full_name and full_name != "Anonyme":
        progress_points += 5
    if sectors:
        progress_points += 5
    if all_skills:
        progress_points += min(20, len(all_skills) * 4)
    if cv_analyses:
        progress_points += 20
    if passport:
        progress_points += 10
        if passport.get("professional_summary"):
            progress_points += 8
        if passport.get("career_project"):
            progress_points += 7
    if dclic:
        progress_points += 25
    # Ajouter progression du bilan partenaire
    bilan_progress = ben.get("bilan_progress", 0)
    if bilan_progress > 0:
        progress_points += int(bilan_progress * 0.1)
    sync_progress = min(progress_points, 100)

    now = datetime.now(timezone.utc)
    update_data = {
        "name": full_name,
        "progress": sync_progress,
        "skills_acquired": all_skills[:20],
        "sector": sector,
        "sync_date": now.isoformat(),
        "sync_data": {
            "profile_score": profile.get("profile_score", 0),
            "experience_years": profile.get("experience_years", 0),
            "strengths": profile.get("strengths", []),
            "gaps": profile.get("gaps", []),
            "dclic_summary": dclic.get("summary") if dclic else None,
            "cv_count": len(cv_analyses),
            "passport_competences_count": len(passport.get("competences", [])) if passport else 0,
        },
        "last_activity": now.isoformat(),
    }

    await db.beneficiaires.update_one(
        {"id": beneficiary_id},
        {
            "$set": update_data,
            "$push": {
                "historique": {
                    "date": now.isoformat(),
                    "action": "resync",
                    "detail": f"Profil re-synchronisé — progression {sync_progress}%"
                }
            }
        }
    )

    updated = await db.beneficiaires.find_one({"id": beneficiary_id}, {"_id": 0})
    return updated


# ===== OUTILS D'ACCOMPAGNEMENT V2 (BILAN AUGMENTE RE'ACTIF PRO) =====

BILAN_FICHES = [
    {"id": "positionnement_depart", "phase": "diagnostic", "phase_label": "Diagnostic initial", "number": 1, "title": "Positionnement de départ", "description": "Clarifier le niveau de clarté, d'énergie et d'urgence avant l'accompagnement"},
    {"id": "courbe_trajectoire", "phase": "diagnostic", "phase_label": "Diagnostic initial", "number": 2, "title": "Courbe de trajectoire", "description": "Lecture stratégique du parcours : pics de réussite, zones de rupture, fil rouge"},
    {"id": "recit_carriere", "phase": "bilan_pro", "phase_label": "Bilan professionnel", "number": 3, "title": "Récit de carrière analytique", "description": "Analyse approfondie de chaque poste : compétences, énergie, alignement valeurs"},
    {"id": "realisations", "phase": "bilan_pro", "phase_label": "Bilan professionnel", "number": 4, "title": "Réalisations et impact", "description": "Méthode STAR augmentée : impact réel, niveau de preuve, contexte de reproductibilité"},
    {"id": "competences_dynamiques", "phase": "bilan_pro", "phase_label": "Bilan professionnel", "number": 5, "title": "Compétences dynamiques", "description": "3 dimensions (techniques, transversales, comportementales), 3 états, transférabilité"},
    {"id": "identite_professionnelle", "phase": "identite_valeurs", "phase_label": "Identité et valeurs", "number": 6, "title": "Identité professionnelle", "description": "Ce que je suis, ce que je fais, ce que je renvoie — phrase d'identité exploitable"},
    {"id": "valeurs_decisionnelles", "phase": "identite_valeurs", "phase_label": "Identité et valeurs", "number": 7, "title": "Valeurs décisionnelles", "description": "Valeurs vécues, situations de non-respect, 5 non-négociables pour l'avenir"},
    {"id": "environnement_rqth", "phase": "identite_valeurs", "phase_label": "Identité et valeurs", "number": 8, "title": "Environnement et contraintes", "description": "Contraintes réelles (santé, mobilité, vie perso), conditions compatibles, adaptations RQTH"},
    {"id": "confrontation_marche", "phase": "strategie", "phase_label": "Stratégie et trajectoire", "number": 9, "title": "Confrontation au marché", "description": "3 métiers ciblés, compétences demandées, écarts, décision GO / PAS GO / AJUSTEMENT"},
    {"id": "strategie_trajectoire", "phase": "strategie", "phase_label": "Stratégie et trajectoire", "number": 10, "title": "Stratégie de trajectoire", "description": "3 scénarios : projet principal, projet sécurisé, projet exploratoire"},
    {"id": "reseau_leviers", "phase": "activation", "phase_label": "Activation", "number": 11, "title": "Réseau et leviers", "description": "Cartographie réseau : personnes ressources, entreprises cibles, canaux d'accès"},
    {"id": "plan_activation", "phase": "activation", "phase_label": "Activation", "number": 12, "title": "Mon plan d'activation", "description": "Actions terrain, contacts pro, mises en situation, suivi des résultats"},
]

# V1 fiche IDs kept for backward compatibility with existing bilan data
V1_FICHE_IDS = [
    "attentes", "courbe_satisfaction", "formation", "recit_carriere", "interets",
    "realisations", "competences", "synthese_pro", "situations_difficiles",
    "points_forts", "valeurs", "moteurs", "environnement", "synthese_perso",
    "reflexion_projet", "definition_projet"
]


@router.get("/partenaires/outils/fiches")
async def get_fiches_list(token: str):
    """Get the list of all V2 bilan fiches"""
    await get_current_token(token)
    return BILAN_FICHES


@router.get("/partenaires/beneficiaires/{beneficiary_id}/bilan")
async def get_beneficiaire_bilan(beneficiary_id: str, token: str):
    """Get all bilan data for a beneficiary"""
    token_doc = await get_current_token(token)
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")
    return ben.get("bilan", {})


class FicheData(BaseModel):
    fiche_id: str
    data: dict


@router.put("/partenaires/beneficiaires/{beneficiary_id}/bilan")
async def save_fiche_bilan(beneficiary_id: str, token: str, payload: FicheData):
    """Save a specific fiche for a beneficiary's bilan (V2 + backward compat V1)"""
    token_doc = await get_current_token(token)
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")

    valid_ids = [f["id"] for f in BILAN_FICHES] + V1_FICHE_IDS
    if payload.fiche_id not in valid_ids:
        raise HTTPException(status_code=400, detail="Fiche invalide")

    bilan = ben.get("bilan", {})
    bilan[payload.fiche_id] = {
        **payload.data,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    v2_ids = [f["id"] for f in BILAN_FICHES]
    completed_count = len([fid for fid in v2_ids if fid in bilan])

    await db.beneficiaires.update_one(
        {"id": beneficiary_id},
        {
            "$set": {
                "bilan": bilan,
                "bilan_progress": round((completed_count / len(BILAN_FICHES)) * 100),
                "last_activity": datetime.now(timezone.utc).isoformat()
            },
            "$push": {
                "historique": {
                    "date": datetime.now(timezone.utc).isoformat(),
                    "action": "bilan_fiche",
                    "detail": f"Fiche {payload.fiche_id} complétée"
                }
            }
        }
    )
    return {"message": "Fiche sauvegardée", "completed": completed_count, "total": len(BILAN_FICHES)}


# ===== CONSENTEMENT GRANULAIRE =====

CONSENT_MODULES = [
    "profil_administratif", "parcours_formation", "experiences_professionnelles",
    "competences_techniques", "soft_skills", "valeurs_moteurs",
    "contraintes_adaptation", "projet_professionnel", "documents",
    "resultats_tests", "plan_action", "journal_progression"
]


class ConsentCreate(BaseModel):
    beneficiary_id: str
    level: str  # synthese, modulaire, complet_temporaire
    modules: Optional[List[str]] = None  # for modulaire level
    duration_days: int = 90
    purpose: str = "Accompagnement socioprofessionnel"


class ConsentUpdate(BaseModel):
    level: Optional[str] = None
    modules: Optional[List[str]] = None
    duration_days: Optional[int] = None
    active: Optional[bool] = None


@router.post("/partenaires/consent")
async def create_consent(token: str, payload: ConsentCreate):
    """Create a granular consent for data sharing"""
    token_doc = await get_current_token(token)
    partner_id = token_doc["id"]

    ben = await db.beneficiaires.find_one(
        {"id": payload.beneficiary_id, "partner_id": partner_id}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")

    if payload.level not in ["synthese", "modulaire", "complet_temporaire"]:
        raise HTTPException(status_code=400, detail="Niveau invalide: synthese, modulaire, complet_temporaire")

    if payload.level == "modulaire" and not payload.modules:
        raise HTTPException(status_code=400, detail="Modules requis pour le niveau modulaire")

    if payload.modules:
        invalid = [m for m in payload.modules if m not in CONSENT_MODULES]
        if invalid:
            raise HTTPException(status_code=400, detail=f"Modules invalides: {', '.join(invalid)}")

    now = datetime.now(timezone.utc)
    consent = {
        "id": str(uuid.uuid4()),
        "beneficiary_id": payload.beneficiary_id,
        "partner_id": partner_id,
        "level": payload.level,
        "modules": payload.modules if payload.level == "modulaire" else (
            CONSENT_MODULES if payload.level == "complet_temporaire" else []
        ),
        "purpose": payload.purpose,
        "duration_days": payload.duration_days,
        "active": True,
        "created_at": now.isoformat(),
        "expires_at": (now + timedelta(days=payload.duration_days)).isoformat(),
        "revoked_at": None,
        "access_log": []
    }

    await db.consents.insert_one(consent)
    consent.pop("_id", None)

    await db.beneficiaires.update_one(
        {"id": payload.beneficiary_id},
        {
            "$set": {"last_activity": now.isoformat()},
            "$push": {
                "historique": {
                    "date": now.isoformat(),
                    "action": "consent_created",
                    "detail": f"Consentement {payload.level} cree ({payload.duration_days}j)"
                }
            }
        }
    )

    return consent


@router.get("/partenaires/consent/{beneficiary_id}")
async def get_consent(beneficiary_id: str, token: str):
    """Get active consent for a beneficiary"""
    token_doc = await get_current_token(token)
    consents = await db.consents.find(
        {"beneficiary_id": beneficiary_id, "partner_id": token_doc["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)

    now = datetime.now(timezone.utc)
    for c in consents:
        if c.get("active") and c.get("expires_at"):
            try:
                exp = datetime.fromisoformat(c["expires_at"].replace("Z", "+00:00"))
                if exp < now:
                    c["active"] = False
                    c["status"] = "expire"
                    await db.consents.update_one({"id": c["id"]}, {"$set": {"active": False}})
                else:
                    remaining = (exp - now).days
                    c["status"] = "actif"
                    c["remaining_days"] = remaining
            except (ValueError, TypeError):
                c["status"] = "actif"
        elif not c.get("active"):
            c["status"] = "revoque" if c.get("revoked_at") else "expire"

    return consents


@router.put("/partenaires/consent/{consent_id}")
async def update_consent(consent_id: str, token: str, payload: ConsentUpdate):
    """Update a consent"""
    token_doc = await get_current_token(token)
    consent = await db.consents.find_one(
        {"id": consent_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not consent:
        raise HTTPException(status_code=404, detail="Consentement non trouvé")

    update_data = {}
    if payload.level is not None:
        update_data["level"] = payload.level
    if payload.modules is not None:
        update_data["modules"] = payload.modules
    if payload.duration_days is not None:
        update_data["duration_days"] = payload.duration_days
        update_data["expires_at"] = (
            datetime.fromisoformat(consent["created_at"].replace("Z", "+00:00"))
            + timedelta(days=payload.duration_days)
        ).isoformat()
    if payload.active is not None:
        update_data["active"] = payload.active
        if not payload.active:
            update_data["revoked_at"] = datetime.now(timezone.utc).isoformat()

    if update_data:
        await db.consents.update_one({"id": consent_id}, {"$set": update_data})

    updated = await db.consents.find_one({"id": consent_id}, {"_id": 0})
    return updated


@router.delete("/partenaires/consent/{consent_id}")
async def revoke_consent(consent_id: str, token: str):
    """Revoke a consent"""
    token_doc = await get_current_token(token)
    consent = await db.consents.find_one(
        {"id": consent_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not consent:
        raise HTTPException(status_code=404, detail="Consentement non trouvé")

    now = datetime.now(timezone.utc)
    await db.consents.update_one(
        {"id": consent_id},
        {"$set": {"active": False, "revoked_at": now.isoformat()}}
    )

    await db.beneficiaires.update_one(
        {"id": consent["beneficiary_id"]},
        {
            "$set": {"last_activity": now.isoformat()},
            "$push": {
                "historique": {
                    "date": now.isoformat(),
                    "action": "consent_revoked",
                    "detail": f"Consentement {consent['level']} revoque"
                }
            }
        }
    )

    return {"message": "Consentement revoque"}


@router.get("/partenaires/consent-modules")
async def get_consent_modules(token: str):
    """Get list of available consent modules"""
    await get_current_token(token)
    modules_labels = {
        "profil_administratif": "Profil administratif",
        "parcours_formation": "Parcours de formation",
        "experiences_professionnelles": "Expériences professionnelles",
        "competences_techniques": "Compétences techniques",
        "soft_skills": "Soft skills",
        "valeurs_moteurs": "Valeurs et moteurs",
        "contraintes_adaptation": "Contraintes et besoins d'adaptation",
        "projet_professionnel": "Projet professionnel",
        "documents": "Documents",
        "resultats_tests": "Résultats de tests",
        "plan_action": "Plan d'action",
        "journal_progression": "Journal de progression",
    }
    return [{"id": m, "label": modules_labels.get(m, m)} for m in CONSENT_MODULES]
