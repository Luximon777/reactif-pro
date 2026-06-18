"""
D'CLIC PRO — Questionnaire & Scoring Engine
Routes: /api/dclic/questionnaire, /api/dclic/submit, /api/dclic/retrieve, /api/dclic/claim
"""

import os
import json
import uuid
import random
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from emergentintegrations.llm.chat import LlmChat, UserMessage

router = APIRouter(prefix="/api")

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "test_database")
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")

# ============================================================================
# QUESTIONNAIRE DATA
# ============================================================================

QUESTIONNAIRE = [
    # --- MBTI: Énergie (E/I) ---
    {
        "id": "mbti_ei_1",
        "category": "energie",
        "text": "Quand vous devez recharger vos batteries après une journée intense, vous préférez :",
        "type": "choice",
        "choices": [
            {"value": "E", "label": "Retrouver des amis ou collègues pour échanger"},
            {"value": "I", "label": "Vous retrouver seul(e) pour un moment calme"}
        ]
    },
    {
        "id": "mbti_ei_2",
        "category": "energie",
        "text": "En réunion professionnelle, vous avez tendance à :",
        "type": "choice",
        "choices": [
            {"value": "E", "label": "Prendre la parole spontanément et rebondir sur les idées"},
            {"value": "I", "label": "Écouter attentivement puis formuler une réponse réfléchie"}
        ]
    },
    # --- MBTI: Perception (S/N) ---
    {
        "id": "mbti_sn_1",
        "category": "perception",
        "text": "Face à un nouveau projet, vous vous concentrez d'abord sur :",
        "type": "choice",
        "choices": [
            {"value": "S", "label": "Les faits concrets, les données et l'expérience passée"},
            {"value": "N", "label": "Les possibilités futures, les connexions et les idées innovantes"}
        ]
    },
    {
        "id": "mbti_sn_2",
        "category": "perception",
        "text": "Vous apprenez mieux quand :",
        "type": "choice",
        "choices": [
            {"value": "S", "label": "On vous montre des exemples concrets, étape par étape"},
            {"value": "N", "label": "On vous explique le concept global et vous explorez par vous-même"}
        ]
    },
    # --- MBTI: Décision (T/F) ---
    {
        "id": "mbti_tf_1",
        "category": "decision",
        "text": "Quand un collègue fait une erreur sur un projet important, vous :",
        "type": "choice",
        "choices": [
            {"value": "T", "label": "Analysez objectivement l'erreur et proposez des corrections"},
            {"value": "F", "label": "Tenez compte de la situation personnelle du collègue d'abord"}
        ]
    },
    {
        "id": "mbti_tf_2",
        "category": "decision",
        "text": "Pour prendre une décision professionnelle importante, vous vous fiez à :",
        "type": "choice",
        "choices": [
            {"value": "T", "label": "Une analyse logique des avantages et inconvénients"},
            {"value": "F", "label": "Votre ressenti et l'impact sur les personnes concernées"}
        ]
    },
    # --- MBTI: Structure (J/P) ---
    {
        "id": "mbti_jp_1",
        "category": "structure",
        "text": "Face à une deadline, vous avez plutôt tendance à :",
        "type": "choice",
        "choices": [
            {"value": "J", "label": "Planifier à l'avance et terminer bien avant l'échéance"},
            {"value": "P", "label": "Travailler par à-coups en vous adaptant au fil de l'eau"}
        ]
    },
    {
        "id": "mbti_jp_2",
        "category": "structure",
        "text": "Votre espace de travail idéal est :",
        "type": "choice",
        "choices": [
            {"value": "J", "label": "Bien organisé avec un système de classement clair"},
            {"value": "P", "label": "Flexible avec plusieurs projets ouverts en parallèle"}
        ]
    },
    # --- DISC ---
    {
        "id": "disc_1",
        "category": "disc",
        "text": "Classez ces 4 affirmations de la plus à la moins vous caractérisante :",
        "type": "ranking",
        "choices": [
            {"value": "D", "label": "J'aime prendre des décisions rapides et diriger"},
            {"value": "I", "label": "J'aime convaincre et motiver les autres"},
            {"value": "S", "label": "J'aime la stabilité et aider les membres de mon équipe"},
            {"value": "C", "label": "J'aime analyser les détails et garantir la qualité"}
        ]
    },
    {
        "id": "disc_2",
        "category": "disc",
        "text": "En situation de conflit professionnel, vous avez tendance à :",
        "type": "choice",
        "choices": [
            {"value": "D", "label": "Affronter directement le problème et trancher"},
            {"value": "I", "label": "Chercher un compromis par la discussion ouverte"},
            {"value": "S", "label": "Écouter toutes les parties et chercher l'harmonie"},
            {"value": "C", "label": "Analyser les faits et proposer une solution rationnelle"}
        ]
    },
    {
        "id": "disc_3",
        "category": "disc",
        "text": "Ce qui vous motive le plus dans votre travail :",
        "type": "choice",
        "choices": [
            {"value": "D", "label": "Atteindre des résultats concrets et relever des défis"},
            {"value": "I", "label": "Collaborer, inspirer et créer une dynamique positive"},
            {"value": "S", "label": "Contribuer à un environnement stable et bienveillant"},
            {"value": "C", "label": "Produire un travail précis et de haute qualité"}
        ]
    },
    # --- RIASEC ---
    {
        "id": "riasec_1",
        "category": "riasec",
        "text": "Classez ces activités par ordre de préférence :",
        "type": "ranking",
        "choices": [
            {"value": "R", "label": "Construire, réparer ou manipuler des objets"},
            {"value": "I", "label": "Rechercher, analyser ou résoudre des problèmes complexes"},
            {"value": "A", "label": "Créer, concevoir ou exprimer des idées"},
            {"value": "S", "label": "Aider, enseigner ou conseiller des personnes"},
            {"value": "E", "label": "Diriger, vendre ou négocier"},
            {"value": "C", "label": "Organiser, classer ou gérer des données"}
        ]
    },
    {
        "id": "riasec_2",
        "category": "riasec",
        "text": "L'environnement de travail qui vous attire le plus :",
        "type": "choice",
        "choices": [
            {"value": "R", "label": "En atelier, en plein air, avec des outils ou machines"},
            {"value": "I", "label": "En laboratoire ou bureau d'études, avec de la recherche"},
            {"value": "A", "label": "Un studio créatif, une scène, un espace artistique"},
            {"value": "S", "label": "Un lieu d'accueil, de soins ou d'accompagnement"},
            {"value": "E", "label": "Un bureau de direction, un espace commercial"},
            {"value": "C", "label": "Un bureau structuré avec des procédures claires"}
        ]
    },
    # --- Ennéagramme ---
    {
        "id": "ennea_1",
        "category": "enneagramme",
        "text": "Ce qui guide vos choix professionnels en profondeur :",
        "type": "choice",
        "choices": [
            {"value": "1", "label": "Le besoin de faire les choses correctement et d'améliorer le monde"},
            {"value": "2", "label": "Le besoin d'aider et d'être apprécié(e) pour ma contribution"},
            {"value": "3", "label": "Le besoin de réussir et d'être reconnu(e) pour mes accomplissements"},
            {"value": "4", "label": "Le besoin d'authenticité et de sens profond dans ce que je fais"},
            {"value": "5", "label": "Le besoin de comprendre et de maîtriser mon domaine d'expertise"},
            {"value": "6", "label": "Le besoin de sécurité et de loyauté envers mon équipe"},
            {"value": "7", "label": "Le besoin de variété, de liberté et de nouvelles expériences"},
            {"value": "8", "label": "Le besoin de contrôle, d'autonomie et de protéger les plus faibles"},
            {"value": "9", "label": "Le besoin d'harmonie, de paix et de consensus"}
        ]
    },
    {
        "id": "ennea_2",
        "category": "enneagramme",
        "text": "Votre plus grande crainte dans le contexte professionnel :",
        "type": "choice",
        "choices": [
            {"value": "1", "label": "Être imparfait(e) ou corrompu(e)"},
            {"value": "2", "label": "Ne pas être aimé(e) ou utile"},
            {"value": "3", "label": "Échouer ou ne pas être reconnu(e)"},
            {"value": "4", "label": "Perdre mon identité ou être ordinaire"},
            {"value": "5", "label": "Être envahi(e) ou incompétent(e)"},
            {"value": "6", "label": "Être abandonné(e) ou sans soutien"},
            {"value": "7", "label": "Être limité(e) ou souffrir"},
            {"value": "8", "label": "Être contrôlé(e) ou vulnérable"},
            {"value": "9", "label": "Le conflit ou la séparation"}
        ]
    },
    # --- Vertus (Seligman & Peterson) ---
    {
        "id": "vertus_1",
        "category": "vertus",
        "text": "Classez ces qualités de la plus à la moins importante pour vous :",
        "type": "ranking",
        "choices": [
            {"value": "sagesse", "label": "La sagesse (curiosité, créativité, ouverture d'esprit)"},
            {"value": "courage", "label": "Le courage (persévérance, authenticité, vitalité)"},
            {"value": "humanite", "label": "L'humanité (empathie, gentillesse, intelligence sociale)"},
            {"value": "justice", "label": "La justice (équité, leadership, travail d'équipe)"},
            {"value": "temperance", "label": "La tempérance (humilité, prudence, maîtrise de soi)"},
            {"value": "transcendance", "label": "La transcendance (gratitude, espoir, humour, spiritualité)"}
        ]
    },
    {
        "id": "vertus_2",
        "category": "vertus",
        "text": "Dans votre vie professionnelle, ce qui vous définit le mieux :",
        "type": "choice",
        "choices": [
            {"value": "sagesse", "label": "Ma curiosité intellectuelle et mon désir d'apprendre"},
            {"value": "courage", "label": "Ma persévérance face aux obstacles"},
            {"value": "humanite", "label": "Mon empathie et ma capacité à créer du lien"},
            {"value": "justice", "label": "Mon sens de l'équité et du collectif"},
            {"value": "temperance", "label": "Ma capacité à garder le recul et la mesure"},
            {"value": "transcendance", "label": "Mon optimisme et ma capacité à donner du sens"}
        ]
    },
    # --- Valeurs (Schwartz) ---
    {
        "id": "valeurs_1",
        "category": "valeurs",
        "text": "Classez ces valeurs par ordre d'importance pour votre carrière :",
        "type": "ranking",
        "choices": [
            {"value": "autonomie", "label": "Autonomie : liberté de pensée et d'action"},
            {"value": "stimulation", "label": "Stimulation : variété, nouveauté, défis"},
            {"value": "realisation", "label": "Réalisation de soi : ambition, compétence, succès"},
            {"value": "bienveillance", "label": "Bienveillance : entraide, loyauté, honnêteté"},
            {"value": "securite", "label": "Sécurité : stabilité, ordre, santé"},
            {"value": "universalisme", "label": "Universalisme : justice sociale, tolérance, environnement"}
        ]
    },
    # --- Style de travail ---
    {
        "id": "style_1",
        "category": "style",
        "text": "Votre manière préférée de travailler :",
        "type": "choice",
        "choices": [
            {"value": "solo", "label": "En autonomie, avec mes propres méthodes"},
            {"value": "duo", "label": "En binôme, avec un partenaire de confiance"},
            {"value": "equipe", "label": "En équipe pluridisciplinaire"},
            {"value": "reseau", "label": "En réseau, avec des connexions variées"}
        ]
    },
    {
        "id": "style_2",
        "category": "style",
        "text": "Face à un problème complexe au travail, votre premier réflexe :",
        "type": "choice",
        "choices": [
            {"value": "analyser", "label": "Décomposer le problème en sous-parties logiques"},
            {"value": "consulter", "label": "Consulter des collègues pour avoir différents avis"},
            {"value": "experimenter", "label": "Tester rapidement une solution, quitte à ajuster"},
            {"value": "recul", "label": "Prendre du recul pour voir le tableau d'ensemble"}
        ]
    },
    # --- Compétences perçues ---
    {
        "id": "competences_1",
        "category": "competences",
        "text": "Parmi ces compétences transversales, classez vos 4 plus fortes :",
        "type": "ranking",
        "choices": [
            {"value": "communication", "label": "Communication et expression"},
            {"value": "organisation", "label": "Organisation et planification"},
            {"value": "leadership", "label": "Leadership et influence"},
            {"value": "creativite", "label": "Créativité et innovation"},
            {"value": "analyse", "label": "Analyse et résolution de problèmes"},
            {"value": "adaptabilite", "label": "Adaptabilité et flexibilité"},
            {"value": "cooperation", "label": "Coopération et travail d'équipe"},
            {"value": "rigueur", "label": "Rigueur et attention au détail"}
        ]
    },
    # --- Gestion du stress ---
    {
        "id": "stress_1",
        "category": "stress",
        "text": "Sous forte pression au travail, vous avez plutôt tendance à :",
        "type": "choice",
        "choices": [
            {"value": "action", "label": "Redoubler d'efforts et passer à l'action immédiate"},
            {"value": "planifier", "label": "Réorganiser vos priorités et planifier"},
            {"value": "soutien", "label": "Chercher du soutien auprès de vos proches ou collègues"},
            {"value": "retrait", "label": "Prendre du recul et analyser la situation calmement"}
        ]
    },
]


# ============================================================================
# SCORING ENGINE
# ============================================================================

def _compute_scores(answers: dict) -> dict:
    """Compute raw dimension scores from questionnaire answers."""

    # MBTI scores
    mbti = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    for qid, val in answers.items():
        if qid.startswith("mbti_ei"):
            mbti[val] = mbti.get(val, 0) + 1
        elif qid.startswith("mbti_sn"):
            mbti[val] = mbti.get(val, 0) + 1
        elif qid.startswith("mbti_tf"):
            mbti[val] = mbti.get(val, 0) + 1
        elif qid.startswith("mbti_jp"):
            mbti[val] = mbti.get(val, 0) + 1

    mbti_code = ""
    mbti_code += "E" if mbti["E"] >= mbti["I"] else "I"
    mbti_code += "S" if mbti["S"] >= mbti["N"] else "N"
    mbti_code += "T" if mbti["T"] >= mbti["F"] else "F"
    mbti_code += "J" if mbti["J"] >= mbti["P"] else "P"

    mbti_pcts = {
        "energie": int(max(mbti["E"], mbti["I"]) / max(mbti["E"] + mbti["I"], 1) * 100),
        "perception": int(max(mbti["S"], mbti["N"]) / max(mbti["S"] + mbti["N"], 1) * 100),
        "decision": int(max(mbti["T"], mbti["F"]) / max(mbti["T"] + mbti["F"], 1) * 100),
        "structure": int(max(mbti["J"], mbti["P"]) / max(mbti["J"] + mbti["P"], 1) * 100),
    }

    # DISC scores
    disc = {"D": 0, "I": 0, "S": 0, "C": 0}
    for qid, val in answers.items():
        if not qid.startswith("disc_"):
            continue
        if "," in val:  # ranking
            parts = val.split(",")
            for rank, v in enumerate(parts):
                disc[v] = disc.get(v, 0) + (len(parts) - rank)
        else:
            disc[val] = disc.get(val, 0) + 3

    disc_total = max(sum(disc.values()), 1)
    disc_pcts = {k: int(v / disc_total * 100) for k, v in disc.items()}
    disc_dominant = max(disc, key=disc.get)
    disc_labels = {"D": "Dominance", "I": "Influence", "S": "Stabilité", "C": "Conformité"}

    # RIASEC scores
    riasec = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
    for qid, val in answers.items():
        if not qid.startswith("riasec_"):
            continue
        if "," in val:
            parts = val.split(",")
            for rank, v in enumerate(parts):
                riasec[v] = riasec.get(v, 0) + (len(parts) - rank)
        else:
            riasec[v] = riasec.get(v, 0) + 3
    riasec_total = max(sum(riasec.values()), 1)
    riasec_pcts = {k: int(v / riasec_total * 100) for k, v in riasec.items()}
    sorted_riasec = sorted(riasec.items(), key=lambda x: -x[1])
    riasec_major = sorted_riasec[0][0]
    riasec_minor = sorted_riasec[1][0] if len(sorted_riasec) > 1 else riasec_major

    riasec_names = {"R": "Réaliste", "I": "Investigateur", "A": "Artistique", "S": "Social", "E": "Entreprenant", "C": "Conventionnel"}

    # Enneagram
    ennea_counts = {}
    for qid, val in answers.items():
        if qid.startswith("ennea_"):
            ennea_counts[val] = ennea_counts.get(val, 0) + 1
    ennea_type = max(ennea_counts, key=ennea_counts.get) if ennea_counts else "2"
    ennea_labels = {"1": "Le Perfectionniste", "2": "L'Altruiste", "3": "Le Battant", "4": "L'Artiste", "5": "L'Observateur", "6": "Le Loyaliste", "7": "L'Épicurien", "8": "Le Leader", "9": "Le Médiateur"}

    # Vertus
    vertus = {"sagesse": 0, "courage": 0, "humanite": 0, "justice": 0, "temperance": 0, "transcendance": 0}
    for qid, val in answers.items():
        if not qid.startswith("vertus_"):
            continue
        if "," in val:
            parts = val.split(",")
            for rank, v in enumerate(parts):
                if v in vertus:
                    vertus[v] += (len(parts) - rank)
        elif val in vertus:
            vertus[val] += 3
    vertus_total = max(sum(vertus.values()), 1)
    vertus_pcts = {k: int(v / vertus_total * 100) for k, v in vertus.items()}
    vertus_dominant = max(vertus, key=vertus.get)
    vertus_names = {"sagesse": "Sagesse", "courage": "Courage", "humanite": "Humanité", "justice": "Justice", "temperance": "Tempérance", "transcendance": "Transcendance"}

    # Valeurs Schwartz
    valeurs = {}
    for qid, val in answers.items():
        if not qid.startswith("valeurs_"):
            continue
        if "," in val:
            parts = val.split(",")
            for rank, v in enumerate(parts):
                valeurs[v] = valeurs.get(v, 0) + (len(parts) - rank)
        elif val:
            valeurs[val] = valeurs.get(val, 0) + 3

    # Competences ranking
    competences = {}
    for qid, val in answers.items():
        if qid == "competences_1" and "," in val:
            parts = val.split(",")
            for rank, v in enumerate(parts):
                competences[v] = len(parts) - rank

    # Style & stress
    style = answers.get("style_1", "equipe")
    problem_style = answers.get("style_2", "analyser")
    stress_style = answers.get("stress_1", "planifier")

    return {
        "mbti_code": mbti_code,
        "mbti_raw": mbti,
        "mbti_pcts": mbti_pcts,
        "disc_dominant": disc_dominant,
        "disc_label": disc_labels.get(disc_dominant, ""),
        "disc_scores": disc_pcts,
        "riasec_major": riasec_major,
        "riasec_minor": riasec_minor,
        "riasec_major_name": riasec_names.get(riasec_major, ""),
        "riasec_minor_name": riasec_names.get(riasec_minor, ""),
        "riasec_scores": riasec_pcts,
        "ennea_type": int(ennea_type),
        "ennea_label": ennea_labels.get(ennea_type, ""),
        "vertus_dominant": vertus_dominant,
        "vertus_dominant_name": vertus_names.get(vertus_dominant, ""),
        "vertus_scores": vertus_pcts,
        "valeurs_top": sorted(valeurs.items(), key=lambda x: -x[1])[:4] if valeurs else [],
        "competences_top": sorted(competences.items(), key=lambda x: -x[1])[:4] if competences else [],
        "style": style,
        "problem_style": problem_style,
        "stress_style": stress_style,
    }


async def _generate_ai_profile(scores: dict, birth_date: str = None, target_job: str = None) -> dict:
    """Use AI to generate rich narrative profile from raw scores."""
    if not EMERGENT_LLM_KEY:
        logging.warning("No EMERGENT_LLM_KEY, using fallback profile")
        return _fallback_profile(scores)

    prompt = f"""Tu es un expert en psychologie du travail et en bilan de compétences. 
À partir des scores D'CLIC PRO suivants, génère un profil professionnel riche et personnalisé.

SCORES:
- MBTI: {scores['mbti_code']}
- DISC dominant: {scores['disc_dominant']} ({scores['disc_label']})  scores: {json.dumps(scores['disc_scores'])}
- RIASEC: {scores['riasec_major']} ({scores['riasec_major_name']}) / {scores['riasec_minor']} ({scores['riasec_minor_name']})  scores: {json.dumps(scores['riasec_scores'])}
- Ennéagramme: Type {scores['ennea_type']} ({scores['ennea_label']})
- Vertu dominante: {scores['vertus_dominant_name']}  scores: {json.dumps(scores['vertus_scores'])}
- Valeurs top: {json.dumps(scores['valeurs_top'])}
- Compétences fortes: {json.dumps(scores['competences_top'])}
- Style de travail: {scores['style']}, résolution: {scores['problem_style']}, stress: {scores['stress_style']}
{"- Métier visé: " + target_job if target_job else ""}
{"- Date de naissance: " + birth_date if birth_date else ""}

Réponds UNIQUEMENT en JSON valide (pas de markdown). Structure:
{{
  "compass": {{
    "summary": "2-3 phrases sur le profil global",
    "axes": [
      {{"name": "Énergie", "dominant": "{scores['mbti_code'][0]}", "pole_a": {{"code": "E", "label": "Extraversion"}}, "pole_b": {{"code": "I", "label": "Introversion"}}, "insight": "phrase explicative"}},
      {{"name": "Perception", "dominant": "{scores['mbti_code'][1]}", "pole_a": {{"code": "S", "label": "Sensation"}}, "pole_b": {{"code": "N", "label": "Intuition"}}, "insight": "phrase explicative"}},
      {{"name": "Décision", "dominant": "{scores['mbti_code'][2]}", "pole_a": {{"code": "T", "label": "Pensée"}}, "pole_b": {{"code": "F", "label": "Sentiment"}}, "insight": "phrase explicative"}},
      {{"name": "Organisation", "dominant": "{scores['mbti_code'][3]}", "pole_a": {{"code": "J", "label": "Jugement"}}, "pole_b": {{"code": "P", "label": "Perception"}}, "insight": "phrase explicative"}}
    ]
  }},
  "vertu_data": {{
    "name": "{scores['vertus_dominant_name']}",
    "cognition": ["3-4 forces cognitives liées au profil"],
    "conation": ["3-4 forces de volonté liées"],
    "affection": ["3-4 forces émotionnelles liées"],
    "valeurs_schwartz": ["4-5 valeurs Schwartz les plus alignées"],
    "forces": ["4-5 forces de caractère Seligman/Peterson"],
    "savoirs_etre": ["5-6 savoirs-être professionnels France Travail"]
  }},
  "integrated_analysis": {{
    "synthese": "Paragraphe de synthèse intégrée du profil",
    "niveau_1_preuves": {{
      "competences_prouvees": ["5-6 compétences clés"],
      "forces_cles": ["3-4 forces"]
    }},
    "niveau_2_fonctionnement": {{
      "style_travail": "Description du style de travail",
      "environnement_favorable": ["3-4 types d'environnements"]
    }},
    "niveau_3_regulation": {{
      "moteur_interne": "Ce qui drive la personne",
      "leviers_croissance": ["3-4 leviers"],
      "signaux_stress": ["2-3 signaux d'alerte"]
    }}
  }},
  "riasec_detail": {{
    "traits": ["4-5 traits dominants"],
    "environnements_preferes": ["3-4 environnements"],
    "major_description": "Description du type majeur"
  }},
  "vertus_detail": {{
    "qualites_dominantes": ["4-5 qualités humaines"]
  }},
  "life_path": {{
    "label": "Titre du chemin de développement",
    "strengths": ["3-4 forces naturelles"],
    "watchouts": ["2-3 points de vigilance"],
    "micro_actions": [
      {{"focus": "domaine", "action": "action concrète"}},
      {{"focus": "domaine", "action": "action concrète"}},
      {{"focus": "domaine", "action": "action concrète"}}
    ],
    "work_preferences": ["3-4 préférences"]
  }},
  "cross_analysis": {{
    "has_cross_analysis": {"true" if birth_date else "false"},
    "synergy_disc": "Synergie entre DISC et style de travail",
    "synergy_ennea": "Synergie entre Ennéagramme et motivations profondes",
    "tension": "Tension potentielle à transformer",
    "integration_insight": "Insight d'intégration"
  }},
  "ofman_quadrant": [
    {{"qualite": "qualité 1", "piege": "excès de cette qualité", "defi": "compétence à développer", "allergie": "ce qui irrite", "source": "MBTI/DISC/etc", "recommandation": "conseil"}},
    {{"qualite": "qualité 2", "piege": "excès", "defi": "développer", "allergie": "irrite", "source": "source", "recommandation": "conseil"}},
    {{"qualite": "qualité 3", "piege": "excès", "defi": "développer", "allergie": "irrite", "source": "source", "recommandation": "conseil"}}
  ],
  "competences_fortes": ["6-8 compétences transversales identifiées"],
  "ennea_detail": {{
    "type_name": "{scores['ennea_label']}",
    "motivations": ["2-3 motivations profondes"],
    "peurs": ["1-2 peurs fondamentales"]
  }}
}}"""

    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"dclic-{uuid.uuid4()}",
            system_message="Tu es un expert en psychologie du travail. Réponds uniquement en JSON valide."
        ).with_model("openai", "gpt-5.2")
        response = await chat.send_message(UserMessage(text=prompt))
        raw = response.strip() if isinstance(response, str) else response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()
        return json.loads(raw)
    except Exception as e:
        logging.error(f"[D'CLIC] AI profile generation failed: {e}")
        return _fallback_profile(scores)


def _fallback_profile(scores: dict) -> dict:
    """Generate a basic profile when AI is unavailable."""
    return {
        "compass": {
            "summary": f"Profil {scores['mbti_code']} avec un style {scores['disc_label']}. Orientation {scores['riasec_major_name']}/{scores['riasec_minor_name']}.",
            "axes": [
                {"name": "Énergie", "dominant": scores["mbti_code"][0], "pole_a": {"code": "E", "label": "Extraversion"}, "pole_b": {"code": "I", "label": "Introversion"}, "insight": "Votre source d'énergie principale."},
                {"name": "Perception", "dominant": scores["mbti_code"][1], "pole_a": {"code": "S", "label": "Sensation"}, "pole_b": {"code": "N", "label": "Intuition"}, "insight": "Votre mode de perception."},
                {"name": "Décision", "dominant": scores["mbti_code"][2], "pole_a": {"code": "T", "label": "Pensée"}, "pole_b": {"code": "F", "label": "Sentiment"}, "insight": "Votre mode de décision."},
                {"name": "Organisation", "dominant": scores["mbti_code"][3], "pole_a": {"code": "J", "label": "Jugement"}, "pole_b": {"code": "P", "label": "Perception"}, "insight": "Votre style d'organisation."},
            ]
        },
        "vertu_data": {
            "name": scores["vertus_dominant_name"],
            "cognition": ["Curiosité", "Jugement critique", "Perspective"],
            "conation": ["Persévérance", "Authenticité", "Vitalité"],
            "affection": ["Gentillesse", "Intelligence sociale", "Amour"],
            "valeurs_schwartz": [v[0] for v in scores.get("valeurs_top", [])[:4]],
            "forces": [c[0] for c in scores.get("competences_top", [])[:4]],
            "savoirs_etre": ["Autonomie", "Rigueur", "Sens du relationnel", "Adaptabilité"]
        },
        "integrated_analysis": {
            "synthese": f"Profil {scores['mbti_code']} à dominante {scores['disc_label']}.",
            "niveau_1_preuves": {"competences_prouvees": [c[0] for c in scores.get("competences_top", [])], "forces_cles": ["Adaptabilité", "Communication"]},
            "niveau_2_fonctionnement": {"style_travail": f"Style {scores['style']}", "environnement_favorable": ["Équipe structurée", "Environnement collaboratif"]},
            "niveau_3_regulation": {"moteur_interne": scores["ennea_label"], "leviers_croissance": ["Formation continue", "Mentorat"], "signaux_stress": ["Surcharge", "Isolement"]}
        },
        "riasec_detail": {"traits": ["Méthodique", "Communicant"], "environnements_preferes": ["Bureau", "Terrain"], "major_description": f"Profil {scores['riasec_major_name']}"},
        "vertus_detail": {"qualites_dominantes": ["Empathie", "Persévérance", "Intégrité"]},
        "life_path": {
            "label": "Développement professionnel",
            "strengths": ["Adaptabilité", "Engagement"],
            "watchouts": ["Perfectionnisme", "Surmenage"],
            "micro_actions": [{"focus": "Réseau", "action": "Développer votre réseau professionnel"}, {"focus": "Formation", "action": "Identifier une formation clé"}],
            "work_preferences": ["Autonomie", "Collaboration"]
        },
        "cross_analysis": {"has_cross_analysis": False, "synergy_disc": "", "synergy_ennea": "", "tension": "", "integration_insight": ""},
        "ofman_quadrant": [{"qualite": "Rigueur", "piege": "Perfectionnisme", "defi": "Flexibilité", "allergie": "Négligence", "source": "MBTI", "recommandation": "Accepter l'imperfection"}],
        "competences_fortes": [c[0] for c in scores.get("competences_top", [])[:6]],
        "ennea_detail": {"type_name": scores["ennea_label"], "motivations": ["Contribution", "Excellence"], "peurs": ["Échec"]}
    }


# ============================================================================
# ROUTES
# ============================================================================

@router.get("/dclic/questionnaire")
async def get_questionnaire():
    """Return the D'CLIC PRO questionnaire."""
    return {"questions": QUESTIONNAIRE}


class DclicSubmitPayload(BaseModel):
    answers: dict
    birth_date: Optional[str] = None
    education_level: Optional[str] = None
    target_job: Optional[str] = None


@router.post("/dclic/submit")
async def submit_dclic(payload: DclicSubmitPayload):
    """Process D'CLIC PRO answers and return full profile."""
    if not payload.answers or len(payload.answers) < 5:
        raise HTTPException(status_code=400, detail="Réponses insuffisantes")

    scores = _compute_scores(payload.answers)
    ai_profile = await _generate_ai_profile(scores, payload.birth_date, payload.target_job)

    access_code = f"DCLIC-{uuid.uuid4().hex[:6].upper()}"

    profile = {
        "mbti": scores["mbti_code"],
        "disc": scores["disc_dominant"],
        "disc_label": scores["disc_label"],
        "disc_scores": scores["disc_scores"],
        "ennea_type": scores["ennea_type"],
        "ennea_label": scores["ennea_label"],
        "scores": scores["mbti_pcts"],
        "riasec_profile": {
            "major": scores["riasec_major"],
            "minor": scores["riasec_minor"],
            "major_name": scores["riasec_major_name"],
            "minor_name": scores["riasec_minor_name"],
            "major_description": ai_profile.get("riasec_detail", {}).get("major_description", ""),
            "scores": scores["riasec_scores"],
            "traits": ai_profile.get("riasec_detail", {}).get("traits", []),
            "environnements_preferes": ai_profile.get("riasec_detail", {}).get("environnements_preferes", []),
        },
        "vertus_profile": {
            "dominant": scores["vertus_dominant"],
            "dominant_name": scores["vertus_dominant_name"],
            "vertu_dominante_name": scores["vertus_dominant_name"],
            "vertus_scores": scores["vertus_scores"],
            "qualites_dominantes": ai_profile.get("vertus_detail", {}).get("qualites_dominantes", []),
        },
        "vertu_data": ai_profile.get("vertu_data", {}),
        "compass": ai_profile.get("compass", {}),
        "integrated_analysis": ai_profile.get("integrated_analysis", {}),
        "life_path": ai_profile.get("life_path", {}),
        "cross_analysis": ai_profile.get("cross_analysis", {}),
        "ofman_quadrant": ai_profile.get("ofman_quadrant", []),
        "competences_fortes": ai_profile.get("competences_fortes", []),
        "ennea_detail": ai_profile.get("ennea_detail", {}),
    }

    # Save to database
    result_doc = {
        "access_code": access_code,
        "profile": profile,
        "answers": payload.answers,
        "birth_date": payload.birth_date,
        "education_level": payload.education_level,
        "target_job": payload.target_job,
        "raw_scores": scores,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.dclic_results.insert_one(result_doc)

    return {"access_code": access_code, "profile": profile}


class DclicRetrievePayload(BaseModel):
    access_code: str


@router.post("/dclic/retrieve")
async def retrieve_dclic(payload: DclicRetrievePayload):
    """Retrieve D'CLIC PRO results by access code."""
    doc = await db.dclic_results.find_one({"access_code": payload.access_code}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Code d'accès introuvable")
    return {"access_code": doc["access_code"], "profile": doc["profile"]}


@router.get("/dclic/claim")
async def claim_dclic(access_code: str, user_id: str = ""):
    """Claim a D'CLIC result for a user."""
    doc = await db.dclic_results.find_one({"access_code": access_code})
    if not doc:
        raise HTTPException(status_code=404, detail="Code d'accès introuvable")
    if user_id:
        await db.dclic_results.update_one({"access_code": access_code}, {"$set": {"claimed_by": user_id}})
    return {"status": "claimed", "profile": doc.get("profile", {})}


class ImportDclicPayload(BaseModel):
    dclic_profile: dict
    target_job: Optional[str] = None
    skills: list = []


@router.post("/profile/import-dclic")
async def import_dclic(token: str, payload: ImportDclicPayload):
    """Import D'CLIC PRO results into user profile."""
    # Validate token directly to avoid circular import
    token_doc = await db.tokens.find_one({"token": token})
    if not token_doc:
        raise HTTPException(status_code=401, detail="Token invalide")
    token_id = str(token_doc["_id"])

    profile_update = {
        "dclic_result": payload.dclic_profile,
        "dclic_imported_at": datetime.now(timezone.utc).isoformat(),
    }
    if payload.target_job:
        profile_update["target_job"] = payload.target_job

    await db.profiles.update_one(
        {"token_id": token_id},
        {"$set": profile_update},
        upsert=True
    )

    # Also add skills from D'CLIC to passport
    if payload.skills:
        passport = await db.passports.find_one({"token_id": token_id})
        if passport:
            existing_names = {c.get("name", "").lower() for c in passport.get("competences", [])}
            new_comps = list(passport.get("competences", []))
            for skill in payload.skills:
                if skill.get("name", "").lower() not in existing_names:
                    new_comps.append({
                        "name": skill["name"],
                        "nature": "savoir_faire",
                        "category": skill.get("category", "transversale"),
                        "level": "intermediaire",
                        "source": "dclic_pro",
                    })
                    existing_names.add(skill["name"].lower())
            await db.passports.update_one({"token_id": token_id}, {"$set": {"competences": new_comps}})

    return {"status": "ok", "message": "Profil D'CLIC importé avec succès"}
