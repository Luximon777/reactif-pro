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
        raise HTTPException(status_code=404, detail="Beneficiaire non trouve")
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
        raise HTTPException(status_code=404, detail="Beneficiaire non trouve")

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
        raise HTTPException(status_code=404, detail="Beneficiaire non trouve")
    return {"message": "Beneficiaire supprime"}


# ===== LIAISON PROFIL RE'ACTIF PRO =====

@router.post("/partenaires/beneficiaires/{beneficiary_id}/link")
async def link_beneficiaire_to_user(beneficiary_id: str, token: str, pseudo: str):
    """Link a beneficiary to a Re'Actif Pro user by pseudo"""
    token_doc = await get_current_token(token)
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Beneficiaire non trouve")

    user_profile = await db.profiles.find_one({"pseudo": pseudo}, {"_id": 0, "password_hash": 0})
    if not user_profile:
        raise HTTPException(status_code=404, detail="Utilisateur non trouve avec ce pseudo")

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
                    "detail": f"Profil lie a l'utilisateur {pseudo}"
                }
            }
        }
    )
    return {"message": "Profil lie avec succes", "linked_token_id": user_token_id}


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
                    "detail": "Liaison profil supprimee"
                }
            }
        }
    )
    return {"message": "Liaison supprimee"}


@router.get("/partenaires/beneficiaires/{beneficiary_id}/linked-profile")
async def get_linked_profile(beneficiary_id: str, token: str):
    """Get the linked Re'Actif Pro user's full profile (skills, CV, passport, D'CLIC)"""
    token_doc = await get_current_token(token)
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Beneficiaire non trouve")
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
        raise HTTPException(status_code=404, detail="Beneficiaire non trouve")

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
                    "detail": f"Diagnostic enrichi mis a jour ({', '.join(update_fields.keys())})"
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
        raise HTTPException(status_code=404, detail="Beneficiaire non trouve")

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
        context_parts.append(f"Competences validees: {', '.join(ben['skills_acquired'])}")

    freins_actifs = [f for f in ben.get("freins", []) if f.get("status") != "resolu"]
    if freins_actifs:
        context_parts.append(f"Freins peripheriques actifs: {', '.join(f['category'] for f in freins_actifs)}")

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
            context_parts.append(f"Competences Re'Actif Pro: {', '.join(skills_list)}")
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
- Le reseau EURES (si potentiel de mobilite europeenne)
- Les dispositifs France Travail, Mission Locale, Cap Emploi

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
                        "detail": "Orientation IA generee"
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
        raise HTTPException(status_code=404, detail="Beneficiaire non trouve")

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
                    "detail": f"Frein ajoute: {category}"
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
        raise HTTPException(status_code=404, detail="Beneficiaire non trouve")

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
        raise HTTPException(status_code=404, detail="Frein non trouve")

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
                    "detail": f"Frein mis a jour: {status or 'modification'}"
                }
            }
        }
    )
    return {"message": "Frein mis a jour", "frein": target_frein}


# ===== SKILLS =====

@router.post("/partenaires/beneficiaires/{beneficiary_id}/skills")
async def add_skill(beneficiary_id: str, token: str, skill: str):
    token_doc = await get_current_token(token)
    ben = await db.beneficiaires.find_one(
        {"id": beneficiary_id, "partner_id": token_doc["id"]}, {"_id": 0}
    )
    if not ben:
        raise HTTPException(status_code=404, detail="Beneficiaire non trouve")

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
                    "detail": f"Competence validee: {skill}"
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
        raise HTTPException(status_code=404, detail="Profil non trouve")
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
    return {"message": "Contribution envoyee a l'Observatoire", "signal": signal}


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
