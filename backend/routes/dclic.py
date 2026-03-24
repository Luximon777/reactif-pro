from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import secrets
import uuid
import logging
import os
from db import db

router = APIRouter(prefix="/dclic", tags=["dclic"])

# ============================================================================
# ACCESS CODE UTILITIES
# ============================================================================

def generate_access_code() -> str:
    chars = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
    p1 = ''.join(secrets.choice(chars) for _ in range(4))
    p2 = ''.join(secrets.choice(chars) for _ in range(4))
    return f"{p1}-{p2}"

# ============================================================================
# VISUAL QUESTIONNAIRE DATA
# ============================================================================

VISUAL_QUESTIONS = [
    # BLOC 1 - SOURCE D'ÉNERGIE (E/I)
    {
        "id": "v1", "question": "Après une journée intense, vous préférez...",
        "category": "energie", "type": "visual",
        "choices": [
            {"id": "v1a", "value": "E", "label": "Retrouver des amis", "image": "https://images.pexels.com/photos/5414003/pexels-photo-5414003.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Groupe d'amis"},
            {"id": "v1b", "value": "I", "label": "Un moment seul(e)", "image": "https://images.pexels.com/photos/3771836/pexels-photo-3771836.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Personne seule"}
        ]
    },
    {
        "id": "v2", "question": "En réunion, vous êtes plutôt...",
        "category": "energie", "type": "visual",
        "choices": [
            {"id": "v2a", "value": "E", "label": "Je prends la parole", "image": "https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Personne qui présente"},
            {"id": "v2b", "value": "I", "label": "J'écoute et je réfléchis", "image": "https://images.pexels.com/photos/7437095/pexels-photo-7437095.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Personne attentive"}
        ]
    },
    # BLOC 2 - TRAITEMENT INFO (S/N)
    {
        "id": "v3", "question": "Pour résoudre un problème, je préfère...",
        "category": "perception", "type": "visual",
        "choices": [
            {"id": "v3a", "value": "S", "label": "Des étapes concrètes", "image": "https://images.pexels.com/photos/590020/pexels-photo-590020.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Checklist"},
            {"id": "v3b", "value": "N", "label": "Une vision globale", "image": "https://images.pexels.com/photos/7369/startup-photos.jpg?auto=compress&cs=tinysrgb&w=600", "alt": "Mind map"}
        ]
    },
    {
        "id": "v4", "question": "Classez ces approches de la plus naturelle (1) à la moins naturelle (4) :",
        "category": "perception", "type": "ranking",
        "instruction": "Sélectionnez vos 4 choix dans l'ordre de préférence",
        "choices": [
            {"id": "v4a", "value": "S1", "label": "Les faits concrets et vérifiables", "image": "https://images.pexels.com/photos/590020/pexels-photo-590020.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Données"},
            {"id": "v4b", "value": "N1", "label": "Les idées innovantes et créatives", "image": "https://images.pexels.com/photos/7369/startup-photos.jpg?auto=compress&cs=tinysrgb&w=600", "alt": "Brainstorming"},
            {"id": "v4c", "value": "S2", "label": "Les méthodes éprouvées et pratiques", "image": "https://images.pexels.com/photos/416405/pexels-photo-416405.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Outils pratiques"},
            {"id": "v4d", "value": "N2", "label": "Les connexions et possibilités futures", "image": "https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Vision future"}
        ]
    },
    # BLOC 3 - MODE DE DÉCISION (T/F)
    {
        "id": "v5", "question": "Pour prendre une décision importante...",
        "category": "decision", "type": "visual",
        "choices": [
            {"id": "v5a", "value": "T", "label": "J'analyse les données", "image": "https://images.pexels.com/photos/669615/pexels-photo-669615.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Analyse"},
            {"id": "v5b", "value": "F", "label": "J'écoute mon coeur", "image": "https://images.pexels.com/photos/6646918/pexels-photo-6646918.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Coeur"}
        ]
    },
    {
        "id": "v6", "question": "Face à un conflit, je cherche d'abord...",
        "category": "decision", "type": "visual",
        "choices": [
            {"id": "v6a", "value": "T", "label": "La solution logique", "image": "https://images.pexels.com/photos/590020/pexels-photo-590020.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Logique"},
            {"id": "v6b", "value": "F", "label": "L'harmonie du groupe", "image": "https://images.pexels.com/photos/6340697/pexels-photo-6340697.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Équipe unie"}
        ]
    },
    # BLOC 4 - ORGANISATION (J/P)
    {
        "id": "v7", "question": "Je préfère travailler avec...",
        "category": "structure", "type": "visual",
        "choices": [
            {"id": "v7a", "value": "J", "label": "Un planning précis", "image": "https://images.unsplash.com/photo-1435527173128-983b87201f4d?w=600", "alt": "Planning"},
            {"id": "v7b", "value": "P", "label": "De la flexibilité", "image": "https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Flexibilité"}
        ]
    },
    {
        "id": "v8", "question": "Face à un imprévu...",
        "category": "structure", "type": "visual",
        "choices": [
            {"id": "v8a", "value": "J", "label": "Je réorganise tout", "image": "https://images.pexels.com/photos/669615/pexels-photo-669615.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Organisation"},
            {"id": "v8b", "value": "P", "label": "Je m'adapte au fur et à mesure", "image": "https://images.pexels.com/photos/3184325/pexels-photo-3184325.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Adaptation"}
        ]
    },
    # BLOC 5 - STYLE DISC
    {
        "id": "v9", "question": "Classez ces styles de travail du plus naturel (1) au moins naturel (4) :",
        "category": "disc", "type": "ranking",
        "instruction": "Sélectionnez vos 4 choix dans l'ordre de préférence",
        "choices": [
            {"id": "v9a", "value": "D", "label": "Décider et agir vite", "image": "https://images.pexels.com/photos/684387/pexels-photo-684387.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Décision rapide"},
            {"id": "v9b", "value": "I", "label": "Motiver et convaincre", "image": "https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Motivation"},
            {"id": "v9c", "value": "S", "label": "Soutenir et coopérer", "image": "https://images.pexels.com/photos/5684551/pexels-photo-5684551.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Solidarité"},
            {"id": "v9d", "value": "C", "label": "Analyser et vérifier", "image": "https://images.pexels.com/photos/590020/pexels-photo-590020.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Analyse"}
        ]
    },
    # BLOC 6 - MOTIVATION ENNÉAGRAMME
    {
        "id": "v11", "question": "Classez ce qui vous rend heureux/se, du plus important (1) au moins important (4) :",
        "category": "ennea", "type": "ranking",
        "instruction": "Sélectionnez vos 4 choix dans l'ordre de préférence",
        "choices": [
            {"id": "v11a", "value": "2", "label": "Aider les autres"},
            {"id": "v11b", "value": "3", "label": "Réussir mes objectifs"},
            {"id": "v11c", "value": "5", "label": "Apprendre et comprendre"},
            {"id": "v11d", "value": "4", "label": "Créer quelque chose d'unique"},
            {"id": "v11e", "value": "6", "label": "Avoir de la stabilité"},
            {"id": "v11f", "value": "7", "label": "Vivre des aventures"},
            {"id": "v11g", "value": "8", "label": "Avoir de l'influence"},
            {"id": "v11h", "value": "9", "label": "Être en paix avec tous"},
            {"id": "v11i", "value": "1", "label": "Faire les choses bien"}
        ]
    },
    # BLOC 7 - RIASEC
    {
        "id": "r1", "question": "Quand quelque chose tombe en panne...",
        "category": "riasec", "type": "visual",
        "choices": [
            {"id": "r1a", "value": "R", "label": "Je répare moi-même", "image": "https://images.pexels.com/photos/4491881/pexels-photo-4491881.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Réparation"},
            {"id": "r1b", "value": "I", "label": "Je cherche à comprendre pourquoi", "image": "https://images.pexels.com/photos/4145190/pexels-photo-4145190.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Analyse"}
        ]
    },
    {
        "id": "r2", "question": "Pendant votre temps libre, vous préférez...",
        "category": "riasec", "type": "visual",
        "choices": [
            {"id": "r2a", "value": "A", "label": "Créer (dessiner, écrire, jouer de la musique...)", "image": "https://images.pexels.com/photos/3094218/pexels-photo-3094218.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Créer"},
            {"id": "r2b", "value": "S", "label": "Aider ou accompagner quelqu'un", "image": "https://images.pexels.com/photos/6646918/pexels-photo-6646918.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Aider"}
        ]
    },
    {
        "id": "r3", "question": "Dans un projet professionnel, vous préférez...",
        "category": "riasec", "type": "visual",
        "choices": [
            {"id": "r3a", "value": "E", "label": "Convaincre et mener l'équipe", "image": "https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Leader"},
            {"id": "r3b", "value": "C", "label": "Organiser et structurer le travail", "image": "https://images.pexels.com/photos/669615/pexels-photo-669615.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Organisation"}
        ]
    },
    # BLOC 8 - VERTUS ET VALEURS
    {
        "id": "vv1", "question": "Face à un défi important, vous comptez d'abord sur...",
        "category": "vertus", "type": "visual",
        "choices": [
            {"id": "vv1a", "value": "sagesse", "label": "La réflexion et l'analyse", "image": "https://images.pexels.com/photos/3808057/pexels-photo-3808057.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Réflexion"},
            {"id": "vv1b", "value": "courage", "label": "La détermination et l'action", "image": "https://images.pexels.com/photos/3756165/pexels-photo-3756165.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Détermination"}
        ]
    },
    {
        "id": "vv2", "question": "Dans vos relations, ce qui compte le plus...",
        "category": "vertus", "type": "visual",
        "choices": [
            {"id": "vv2a", "value": "humanite", "label": "L'empathie et le soutien", "image": "https://images.pexels.com/photos/6646918/pexels-photo-6646918.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Empathie"},
            {"id": "vv2b", "value": "justice", "label": "L'équité et le respect", "image": "https://images.pexels.com/photos/5668858/pexels-photo-5668858.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Justice"}
        ]
    },
    {
        "id": "vv3", "question": "Ce qui vous apporte le plus de sérénité...",
        "category": "vertus", "type": "visual",
        "choices": [
            {"id": "vv3a", "value": "temperance", "label": "L'organisation et la maîtrise de soi", "image": "https://images.pexels.com/photos/6802049/pexels-photo-6802049.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Organisation"},
            {"id": "vv3b", "value": "transcendance", "label": "La beauté, la gratitude et le sens", "image": "https://images.pexels.com/photos/3560044/pexels-photo-3560044.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Contemplation"}
        ]
    },
    {
        "id": "vv4", "question": "Classez ces valeurs de la plus importante (1) à la moins importante (4) :",
        "category": "valeurs", "type": "ranking",
        "instruction": "Sélectionnez vos 4 choix dans l'ordre de préférence",
        "choices": [
            {"id": "vv4a", "value": "autonomie", "label": "Autonomie - Liberté de penser et d'agir", "image": "https://images.pexels.com/photos/1051838/pexels-photo-1051838.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Liberté"},
            {"id": "vv4b", "value": "bienveillance", "label": "Bienveillance - Prendre soin des proches", "image": "https://images.pexels.com/photos/7176317/pexels-photo-7176317.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Bienveillance"},
            {"id": "vv4c", "value": "reussite", "label": "Réussite - Accomplissement personnel", "image": "https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Réussite"},
            {"id": "vv4d", "value": "securite", "label": "Sécurité - Stabilité et harmonie", "image": "https://images.pexels.com/photos/7176026/pexels-photo-7176026.jpeg?auto=compress&cs=tinysrgb&w=600", "alt": "Sécurité"}
        ]
    },
]

# ============================================================================
# PROFILE COMPUTATION
# ============================================================================

VERTUS_MAP = {
    "sagesse": {"name": "Sagesse et Connaissance", "forces": ["Créativité", "Curiosité", "Jugement", "Amour de l'apprentissage"], "qualites": ["Patience", "Ouverture d'esprit", "Indulgence"], "savoirs_etre": ["Faire preuve de curiosité", "Faire preuve de créativité", "Pensée critique"]},
    "courage": {"name": "Courage", "forces": ["Bravoure", "Persévérance", "Honnêteté", "Enthousiasme"], "qualites": ["Dynamisme", "Fiabilité", "Confiance"], "savoirs_etre": ["Faire preuve de persévérance", "Gérer son stress", "Prendre des initiatives"]},
    "humanite": {"name": "Humanité", "forces": ["Amour", "Gentillesse", "Intelligence sociale"], "qualites": ["Empathie", "Générosité", "Écoute"], "savoirs_etre": ["Être à l'écoute", "Avoir le sens du service", "Travailler en équipe"]},
    "justice": {"name": "Justice", "forces": ["Travail d'équipe", "Équité", "Leadership"], "qualites": ["Coopération", "Logique", "Assertivité"], "savoirs_etre": ["Faire preuve de leadership", "Respecter ses engagements", "Esprit d'équipe"]},
    "temperance": {"name": "Tempérance", "forces": ["Pardon", "Humilité", "Prudence", "Maîtrise de soi"], "qualites": ["Modestie", "Sincérité", "Sobriété"], "savoirs_etre": ["Faire preuve de rigueur", "Organiser son travail", "Maîtrise de soi"]},
    "transcendance": {"name": "Transcendance", "forces": ["Gratitude", "Espoir", "Humour", "Spiritualité"], "qualites": ["Optimisme", "Souplesse", "Sociabilité"], "savoirs_etre": ["S'adapter aux changements", "Faire preuve d'autonomie", "Créativité"]},
}

DISC_LABELS = {"D": "Dominance", "I": "Influence", "S": "Stabilité", "C": "Conformité"}
RIASEC_LABELS = {"R": "Réaliste", "I": "Investigateur", "A": "Artistique", "S": "Social", "E": "Entreprenant", "C": "Conventionnel"}


def compute_dclic_profile(answers: Dict[str, str]) -> Dict[str, Any]:
    """Compute personality profile from questionnaire answers."""
    # MBTI dimensions
    dims = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    # DISC scores
    disc = {"D": 0, "I": 0, "S": 0, "C": 0}
    # Ennéagramme
    ennea = {}
    # RIASEC
    riasec = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
    # Vertus
    vertus_scores = {"sagesse": 0, "courage": 0, "humanite": 0, "justice": 0, "temperance": 0, "transcendance": 0}

    cat_map = {
        "energie": ["E", "I"], "perception": ["S", "N"],
        "decision": ["T", "F"], "structure": ["J", "P"]
    }

    for q in VISUAL_QUESTIONS:
        qid = q["id"]
        ans = answers.get(qid)
        if not ans:
            continue
        cat = q["category"]

        if q["type"] == "ranking":
            parts = ans.split(",")
            for rank_idx, val in enumerate(parts):
                weight = max(4 - rank_idx, 1)
                if cat == "disc":
                    if val in disc:
                        disc[val] += weight
                elif cat == "ennea":
                    ennea[val] = ennea.get(val, 0) + weight
                elif cat in ("perception",):
                    if val.startswith("S"):
                        dims["S"] += weight
                    elif val.startswith("N"):
                        dims["N"] += weight
                elif cat == "riasec":
                    if val in riasec:
                        riasec[val] += weight
                elif cat == "valeurs":
                    val_to_vertu = {"autonomie": "sagesse", "bienveillance": "humanite", "reussite": "courage", "securite": "temperance"}
                    if val in val_to_vertu:
                        vertus_scores[val_to_vertu[val]] += weight
        else:
            # Visual (binary) question
            if cat in cat_map:
                if ans in dims:
                    dims[ans] += 3
            elif cat == "disc":
                if ans in disc:
                    disc[ans] += 3
            elif cat == "riasec":
                if ans in riasec:
                    riasec[ans] += 3
            elif cat == "vertus":
                if ans in vertus_scores:
                    vertus_scores[ans] += 3
            elif cat == "ennea":
                ennea[ans] = ennea.get(ans, 0) + 3

    # Compute MBTI
    e_val = "E" if dims["E"] >= dims["I"] else "I"
    s_val = "S" if dims["S"] >= dims["N"] else "N"
    t_val = "T" if dims["T"] >= dims["F"] else "F"
    j_val = "J" if dims["J"] >= dims["P"] else "P"
    mbti = f"{e_val}{s_val}{t_val}{j_val}"

    # DISC dominant
    disc_dom = max(disc, key=disc.get) if any(disc.values()) else "S"

    # Ennéagramme
    sorted_ennea = sorted(ennea.items(), key=lambda x: x[1], reverse=True)
    ennea_dom = int(sorted_ennea[0][0]) if sorted_ennea else 5
    ennea_sec = int(sorted_ennea[1][0]) if len(sorted_ennea) > 1 else ennea_dom

    # RIASEC dominant
    sorted_riasec = sorted(riasec.items(), key=lambda x: x[1], reverse=True)
    riasec_major = sorted_riasec[0][0] if sorted_riasec else "S"
    riasec_minor = sorted_riasec[1][0] if len(sorted_riasec) > 1 else riasec_major

    # Vertus dominant
    sorted_vertus = sorted(vertus_scores.items(), key=lambda x: x[1], reverse=True)
    vertu_dom = sorted_vertus[0][0] if sorted_vertus else "sagesse"
    vertu_sec = sorted_vertus[1][0] if len(sorted_vertus) > 1 else vertu_dom

    vertu_data = VERTUS_MAP.get(vertu_dom, VERTUS_MAP["sagesse"])

    # Competences fortes
    competences = vertu_data["savoirs_etre"][:3]
    if disc_dom == "D":
        competences.append("Leadership")
    elif disc_dom == "I":
        competences.append("Communication")
    elif disc_dom == "S":
        competences.append("Coopération")
    elif disc_dom == "C":
        competences.append("Rigueur analytique")

    return {
        "mbti": mbti,
        "disc_dominant": disc_dom,
        "disc_scores": disc,
        "ennea_dominant": ennea_dom,
        "ennea_secondary": ennea_sec,
        "riasec_major": riasec_major,
        "riasec_minor": riasec_minor,
        "riasec_scores": riasec,
        "vertu_dominante": vertu_dom,
        "vertu_dominante_name": vertu_data["name"],
        "vertu_secondaire": vertu_sec,
        "vertus_scores": vertus_scores,
        "forces": vertu_data["forces"],
        "qualites": vertu_data["qualites"],
        "savoirs_etre": vertu_data["savoirs_etre"],
        "competences_fortes": competences,
        "riasec_major_name": RIASEC_LABELS.get(riasec_major, ""),
        "riasec_minor_name": RIASEC_LABELS.get(riasec_minor, ""),
        "disc_dominant_name": DISC_LABELS.get(disc_dom, ""),
    }


# ============================================================================
# MODELS
# ============================================================================

class DclicSubmitRequest(BaseModel):
    answers: Dict[str, str]

class DclicRetrieveRequest(BaseModel):
    access_code: str

# ============================================================================
# ROUTES
# ============================================================================

@router.get("/questionnaire")
async def get_dclic_questionnaire():
    return {"questions": VISUAL_QUESTIONS, "total": len(VISUAL_QUESTIONS)}


@router.post("/submit")
async def submit_dclic_test(request: DclicSubmitRequest):
    """Submit answers, compute profile, generate access code."""
    profile = compute_dclic_profile(request.answers)
    access_code = generate_access_code()

    doc = {
        "access_code": access_code,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "is_claimed": False,
        "claimed_at": None,
        "answers": request.answers,
        "profile": profile,
    }
    await db.dclic_results.insert_one(doc)

    return {"access_code": access_code, "profile": profile}


@router.post("/retrieve")
async def retrieve_dclic_results(request: DclicRetrieveRequest):
    """Retrieve D'CLIC PRO results by access code."""
    code = request.access_code.upper().strip()
    if len(code) != 9 or code[4] != '-':
        raise HTTPException(status_code=400, detail="Format de code invalide. Attendu: XXXX-XXXX")

    result = await db.dclic_results.find_one({"access_code": code}, {"_id": 0})
    if not result:
        raise HTTPException(status_code=404, detail="Code d'accès non trouvé")

    return {"success": True, "access_code": code, "profile": result.get("profile", {}), "is_claimed": result.get("is_claimed", False)}


@router.post("/claim")
async def claim_dclic_results(access_code: str, user_id: str):
    """Mark results as claimed by a Re'Actif Pro user."""
    code = access_code.upper().strip()
    result = await db.dclic_results.update_one(
        {"access_code": code, "is_claimed": False},
        {"$set": {"is_claimed": True, "claimed_at": datetime.now(timezone.utc).isoformat(), "claimed_by": user_id}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Code déjà utilisé ou inexistant")
    return {"success": True}
