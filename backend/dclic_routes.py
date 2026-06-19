"""
D'CLIC PRO — Questionnaire & Scoring Engine (Version complète avec restitution IA)
5 Blocs : Archéologie, RIASEC, Valeurs, Savoir-être, Projection
Restitution riche : RIASEC, MBTI/Boussole, Archéologie GSA, Cadran d'Ofman,
                     Analyse intégrée, Carte d'identité Pro, QR Code
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage
from pathlib import Path
from dotenv import load_dotenv
from dclic_referentiel import MATRICE_VERTUS, CITATIONS_VERTUS, format_referentiel_for_prompt
import asyncio, json, logging, os, secrets, string, uuid

load_dotenv(Path(__file__).parent / ".env")
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

router = APIRouter(prefix="/api/dclic", tags=["dclic"])
logger = logging.getLogger("dclic")

# ─── Helpers LLM ─────────────────────────────────────────────────────
def _sync_llm_call(chat, message):
    return asyncio.run(chat.send_message(message))

async def run_llm(chat, message):
    return await asyncio.to_thread(_sync_llm_call, chat, message)

# ─── BLOC 1 : Archéologie des compétences (10 questions ouvertes) ─────

BLOC_1_ARCHEOLOGIE = [
    {"id": "arche_1", "text": "Quelle activité avez-vous réalisée dans votre vie dont vous êtes le plus fier(e) ?", "type": "open_text", "placeholder": "Décrivez cette activité et ce qu'elle représente pour vous..."},
    {"id": "arche_2", "text": "Dans quelles situations les autres viennent-ils spontanément vous demander de l'aide ?", "type": "open_text", "placeholder": "Ex: pour organiser, réparer, écouter, expliquer..."},
    {"id": "arche_3", "text": "Avez-vous déjà organisé un événement, une activité ou coordonné plusieurs personnes ?", "type": "open_text", "placeholder": "Décrivez ce que vous avez organisé et votre rôle..."},
    {"id": "arche_4", "text": "Avez-vous déjà accompagné un proche dans une démarche importante ?", "type": "open_text", "placeholder": "Ex: démarche administrative, recherche d'emploi, soutien scolaire..."},
    {"id": "arche_5", "text": "Avez-vous exercé des responsabilités dans une association, un club, une communauté ou un groupe informel ?", "type": "open_text", "placeholder": "Décrivez votre rôle et vos responsabilités..."},
    {"id": "arche_6", "text": "Quelle difficulté importante avez-vous réussi à surmonter dans votre parcours ?", "type": "open_text", "placeholder": "Décrivez la difficulté et comment vous l'avez surmontée..."},
    {"id": "arche_7", "text": "Quels savoir-faire utilisez-vous régulièrement sans considérer qu'il s'agit de compétences ?", "type": "open_text", "placeholder": "Ex: cuisiner, bricoler, écouter, organiser, négocier..."},
    {"id": "arche_8", "text": "Qu'avez-vous appris en dehors de l'école ou du travail ?", "type": "open_text", "placeholder": "Ex: langue, instrument, mécanique, couture, informatique..."},
    {"id": "arche_9", "text": "Quelle activité vous donne le sentiment d'être particulièrement efficace ?", "type": "open_text", "placeholder": "L'activité où vous vous sentez dans votre élément..."},
    {"id": "arche_10", "text": "Si vous deviez transmettre une compétence à quelqu'un demain, laquelle choisiriez-vous ?", "type": "open_text", "placeholder": "La compétence que vous maîtrisez le mieux..."},
]

# ─── BLOC 2 : Intérêts professionnels RIASEC (10 items, échelle 1-5) ──

BLOC_2_RIASEC = [
    {"id": "riasec_1", "text": "J'aime résoudre des problèmes concrets.", "dimension": "R"},
    {"id": "riasec_2", "text": "J'aime comprendre comment fonctionnent les choses.", "dimension": "I"},
    {"id": "riasec_3", "text": "J'aime créer ou imaginer de nouvelles idées.", "dimension": "A"},
    {"id": "riasec_4", "text": "J'aime aider et accompagner les personnes.", "dimension": "S"},
    {"id": "riasec_5", "text": "J'aime convaincre ou négocier.", "dimension": "E"},
    {"id": "riasec_6", "text": "J'aime organiser et planifier.", "dimension": "C"},
    {"id": "riasec_7", "text": "J'aime travailler avec des outils ou des machines.", "dimension": "R"},
    {"id": "riasec_8", "text": "J'aime transmettre des connaissances.", "dimension": "S"},
    {"id": "riasec_9", "text": "J'aime prendre des initiatives.", "dimension": "E"},
    {"id": "riasec_10", "text": "J'aime travailler selon des procédures précises.", "dimension": "C"},
]

# ─── BLOC 3 : Valeurs professionnelles (10 items, échelle 1-5) ────────

BLOC_3_VALEURS = [
    {"id": "val_1", "text": "Dans mon travail, il est important d'aider les autres.", "dimension": "benevolence"},
    {"id": "val_2", "text": "Il est important de pouvoir évoluer et apprendre.", "dimension": "stimulation"},
    {"id": "val_3", "text": "Il est important de disposer d'une stabilité professionnelle.", "dimension": "securite"},
    {"id": "val_4", "text": "Il est important d'avoir de l'autonomie.", "dimension": "autonomie"},
    {"id": "val_5", "text": "Il est important d'être reconnu pour ses résultats.", "dimension": "reussite"},
    {"id": "val_6", "text": "Il est important de contribuer à quelque chose d'utile à la société.", "dimension": "universalisme"},
    {"id": "val_7", "text": "Il est important de travailler dans un environnement respectueux.", "dimension": "conformite"},
    {"id": "val_8", "text": "Il est important de pouvoir innover.", "dimension": "autonomie"},
    {"id": "val_9", "text": "Il est important de coopérer avec les autres.", "dimension": "benevolence"},
    {"id": "val_10", "text": "Il est important d'agir conformément à mes convictions.", "dimension": "tradition"},
]

# ─── BLOC 4 : Savoir-être professionnels (10 items, échelle 1-5) ──────

BLOC_4_SAVOIR_ETRE = [
    {"id": "sep_1", "text": "Je respecte mes engagements.", "dimension": "fiabilite"},
    {"id": "sep_2", "text": "Je m'adapte facilement aux changements.", "dimension": "adaptabilite"},
    {"id": "sep_3", "text": "Je prends des initiatives lorsque c'est nécessaire.", "dimension": "initiative"},
    {"id": "sep_4", "text": "Je reste calme face aux difficultés.", "dimension": "gestion_stress"},
    {"id": "sep_5", "text": "Je travaille facilement en équipe.", "dimension": "cooperation"},
    {"id": "sep_6", "text": "J'accepte les remarques constructives.", "dimension": "ouverture"},
    {"id": "sep_7", "text": "Je persévère lorsque les résultats tardent à venir.", "dimension": "perseverance"},
    {"id": "sep_8", "text": "Je sais gérer plusieurs tâches simultanément.", "dimension": "organisation"},
    {"id": "sep_9", "text": "Je communique facilement avec différents interlocuteurs.", "dimension": "communication"},
    {"id": "sep_10", "text": "Je recherche des solutions plutôt que des excuses.", "dimension": "resolution"},
]

# ─── BLOC 5 : Projection professionnelle (5 questions mixtes) ─────────

BLOC_5_PROJECTION = [
    {"id": "proj_1", "text": "Quels métiers vous attirent aujourd'hui ?", "type": "open_text", "placeholder": "Listez 2 ou 3 métiers qui vous attirent..."},
    {"id": "proj_2", "text": "Quels métiers vous n'envisageriez jamais ?", "type": "open_text", "placeholder": "Listez les métiers qui ne vous correspondent pas du tout..."},
    {"id": "proj_3", "text": "Préférez-vous travailler avec :", "type": "choice", "choices": [
        {"value": "personnes", "label": "Les personnes"},
        {"value": "donnees", "label": "Les données"},
        {"value": "objets", "label": "Les objets"},
        {"value": "idees", "label": "Les idées"},
        {"value": "combinaison", "label": "Une combinaison de plusieurs"},
    ]},
    {"id": "proj_4", "text": "Dans quel environnement vous sentez-vous le plus à l'aise ?", "type": "choice", "choices": [
        {"value": "bureau", "label": "En bureau / espace structuré"},
        {"value": "terrain", "label": "Sur le terrain / en extérieur"},
        {"value": "atelier", "label": "En atelier / espace technique"},
        {"value": "contact", "label": "En contact direct avec le public"},
        {"value": "domicile", "label": "À domicile / en télétravail"},
        {"value": "itinerant", "label": "En déplacement / itinérant"},
    ]},
    {"id": "proj_5", "text": "Quel serait pour vous un travail réussi dans cinq ans ?", "type": "open_text", "placeholder": "Décrivez votre vision d'un travail épanouissant dans 5 ans..."},
]


# ─── Labels ──────────────────────────────────────────────────────────

RIASEC_LABELS = {
    "R": "Réaliste — Concret, manuel, technique",
    "I": "Investigateur — Analytique, intellectuel, scientifique",
    "A": "Artistique — Créatif, expressif, imaginatif",
    "S": "Social — Aidant, coopératif, pédagogue",
    "E": "Entreprenant — Leader, persuasif, ambitieux",
    "C": "Conventionnel — Organisé, précis, méthodique",
}

VALEUR_LABELS = {
    "benevolence": "Bienveillance", "stimulation": "Stimulation",
    "securite": "Sécurité", "autonomie": "Autonomie",
    "reussite": "Réussite", "universalisme": "Universalisme",
    "conformite": "Conformité", "tradition": "Tradition",
}

SEP_LABELS = {
    "fiabilite": "Fiabilité", "adaptabilite": "Adaptabilité",
    "initiative": "Initiative", "gestion_stress": "Gestion du stress",
    "cooperation": "Coopération", "ouverture": "Ouverture",
    "perseverance": "Persévérance", "organisation": "Organisation",
    "communication": "Communication", "resolution": "Résolution",
}


# ─── Scoring Engine (déterministe) ───────────────────────────────────

def compute_dclic_profile(answers: dict) -> dict:
    """Calcule les scores de base du profil D'CLIC PRO."""

    # ── Archéologie ──
    archeologie = {}
    for q in BLOC_1_ARCHEOLOGIE:
        val = answers.get(q["id"], "")
        if val and len(str(val)) > 2:
            archeologie[q["id"]] = str(val)

    arche_categories = {"visibles": [], "enfouies": [], "transferables": [], "adaptatives": [], "potentielles": []}
    for k in ["arche_1", "arche_9"]:
        if archeologie.get(k): arche_categories["visibles"].append(archeologie[k])
    for k in ["arche_3", "arche_5"]:
        if archeologie.get(k): arche_categories["transferables"].append(archeologie[k])
    for k in ["arche_2", "arche_4"]:
        if archeologie.get(k): arche_categories["enfouies"].append(archeologie[k])
    if archeologie.get("arche_6"):
        arche_categories["adaptatives"].append(archeologie["arche_6"])
    for k in ["arche_7", "arche_8", "arche_10"]:
        if archeologie.get(k): arche_categories["potentielles"].append(archeologie[k])

    # ── RIASEC ──
    riasec_scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
    for item in BLOC_2_RIASEC:
        val = answers.get(item["id"])
        if val is not None:
            try: riasec_scores[item["dimension"]] += int(val)
            except: pass

    riasec_sorted = sorted(riasec_scores.items(), key=lambda x: x[1], reverse=True)
    riasec_code = "".join([r[0] for r in riasec_sorted[:3]])
    riasec_max = max(riasec_scores.values()) if riasec_scores.values() else 1

    riasec_profile = {}
    for dim, score in riasec_scores.items():
        riasec_profile[dim] = {
            "score": score,
            "pct": round((score / max(riasec_max, 1)) * 100),
            "label": RIASEC_LABELS.get(dim, dim),
        }

    # ── Valeurs ──
    valeur_scores = {}
    for item in BLOC_3_VALEURS:
        val = answers.get(item["id"])
        dim = item["dimension"]
        if val is not None:
            try: valeur_scores[dim] = valeur_scores.get(dim, 0) + int(val)
            except: pass

    valeur_sorted = sorted(valeur_scores.items(), key=lambda x: x[1], reverse=True)
    valeurs_dominantes = [{"code": v[0], "score": v[1], "label": VALEUR_LABELS.get(v[0], v[0])} for v in valeur_sorted[:4]]

    # ── Savoir-être ──
    sep_scores = {}
    for item in BLOC_4_SAVOIR_ETRE:
        val = answers.get(item["id"])
        dim = item["dimension"]
        if val is not None:
            try: sep_scores[dim] = int(val)
            except: pass

    sep_sorted = sorted(sep_scores.items(), key=lambda x: x[1], reverse=True)
    sep_forces = [{"code": s[0], "score": s[1], "label": SEP_LABELS.get(s[0], s[0])} for s in sep_sorted if s[1] >= 4]
    sep_all = [{"code": s[0], "score": s[1], "label": SEP_LABELS.get(s[0], s[0])} for s in sep_sorted]

    # ── Projection ──
    projection = {
        "metiers_attires": answers.get("proj_1", ""),
        "metiers_exclus": answers.get("proj_2", ""),
        "preference_travail": answers.get("proj_3", ""),
        "environnement": answers.get("proj_4", ""),
        "vision_5_ans": answers.get("proj_5", ""),
    }

    code = "-".join(["".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4)) for _ in range(2)])

    return {
        "access_code": code,
        "archeologie_competences": {"reponses": archeologie, "categories": arche_categories},
        "riasec": {"code": riasec_code, "dominant": riasec_sorted[0][0] if riasec_sorted else "S", "dominant_label": RIASEC_LABELS.get(riasec_sorted[0][0], "") if riasec_sorted else "", "scores": riasec_scores, "profile": riasec_profile},
        "valeurs": {"dominantes": valeurs_dominantes, "scores": dict(valeur_scores)},
        "savoir_etre": {"forces": sep_forces, "all": sep_all},
        "projection": projection,
    }


# ─── Analyse IA enrichie ─────────────────────────────────────────────

async def generate_rich_profile(answers: dict, basic_profile: dict) -> dict:
    """Utilise GPT-5.2 pour générer l'analyse riche : MBTI, DISC, Boussole,
       Archéologie GSA, Vertus, Cadran d'Ofman, Analyse intégrée, Pistes."""

    # Préparer le résumé des réponses
    arche_text = "\n".join([f"- {q['text']}: {answers.get(q['id'], '(vide)')}" for q in BLOC_1_ARCHEOLOGIE if answers.get(q["id"])])
    riasec_text = ", ".join([f"{k}={v}" for k, v in basic_profile["riasec"]["scores"].items()])
    valeurs_text = ", ".join([f"{v['code']}({v['score']})" for v in basic_profile["valeurs"]["dominantes"]])
    sep_text = ", ".join([f"{s['code']}({s['score']})" for s in basic_profile["savoir_etre"]["all"]])
    proj = basic_profile["projection"]

    # Injecter le référentiel scientifique complet
    referentiel_text = format_referentiel_for_prompt()

    prompt = f"""Tu es un expert en psychologie du travail et en orientation professionnelle.
À partir des réponses D'CLIC PRO ci-dessous et du RÉFÉRENTIEL SCIENTIFIQUE fourni,
génère une analyse complète en JSON.

{referentiel_text}

=== RÉPONSES ARCHÉOLOGIE DES COMPÉTENCES ===
{arche_text}

=== SCORES RIASEC (échelle 1-5, 2 items par dimension) ===
{riasec_text}
Code dominant: {basic_profile['riasec']['code']}

=== VALEURS PROFESSIONNELLES (Schwartz simplifié) ===
{valeurs_text}

=== SAVOIR-ÊTRE PROFESSIONNELS ===
{sep_text}

=== PROJECTION ===
Métiers attirants: {proj['metiers_attires']}
Métiers exclus: {proj['metiers_exclus']}
Préfère travailler avec: {proj['preference_travail']}
Environnement: {proj['environnement']}
Vision 5 ans: {proj['vision_5_ans']}

=== INSTRUCTIONS POUR L'ANALYSE DES VERTUS ===
1. Identifie les 2-3 vertus dominantes du candidat en croisant ses réponses d'archéologie, ses valeurs Schwartz et ses savoir-être.
2. Pour chaque vertu dominante, utilise EXCLUSIVEMENT les correspondances du référentiel ci-dessus (forces de caractère, qualités humaines, compétences transférables, métiers associés).
3. Ne génère JAMAIS de qualités ou compétences qui ne figurent pas dans le référentiel pour la vertu concernée.
4. La citation de référence de la vertu dominante doit être incluse dans vertus_profile.citation.

=== FORMAT JSON ATTENDU ===
Réponds UNIQUEMENT avec un objet JSON valide (pas de markdown, pas de commentaires) contenant :

{{
  "mbti": "XXXX",
  "disc": "XX",
  "disc_label": "Dominant-Influent (par ex.)",
  "disc_scores": {{"D": 0-100, "I": 0-100, "S": 0-100, "C": 0-100}},
  "compass": {{
    "summary": "Synthèse de la boussole de fonctionnement (3-4 phrases)",
    "axes": [
      {{"name": "Énergie", "dominant": "E ou I", "pole_a": {{"code": "E", "label": "Extraversion"}}, "pole_b": {{"code": "I", "label": "Introversion"}}, "insight": "Explication courte"}},
      {{"name": "Perception", "dominant": "S ou N", "pole_a": {{"code": "S", "label": "Sensation"}}, "pole_b": {{"code": "N", "label": "Intuition"}}, "insight": "Explication courte"}},
      {{"name": "Décision", "dominant": "T ou F", "pole_a": {{"code": "T", "label": "Pensée"}}, "pole_b": {{"code": "F", "label": "Sentiment"}}, "insight": "Explication courte"}},
      {{"name": "Organisation", "dominant": "J ou P", "pole_a": {{"code": "J", "label": "Jugement"}}, "pole_b": {{"code": "P", "label": "Perception"}}, "insight": "Explication courte"}}
    ]
  }},
  "vertus_profile": {{
    "dominant": "code_vertu (sagesse|courage|humanite|justice|temperance|transcendance)",
    "dominant_name": "Nom affiché (ex: Sagesse et Connaissance)",
    "description": "Description de la vertu dominante issue du référentiel",
    "citation": "Citation philosophique de référence pour cette vertu",
    "vertus_scores": {{"sagesse": 0-100, "courage": 0-100, "humanite": 0-100, "justice": 0-100, "temperance": 0-100, "transcendance": 0-100}},
    "forces_caractere": ["Force 1 du référentiel", "Force 2", "Force 3"],
    "qualites_dominantes": ["Qualité du référentiel 1", "Qualité 2", "Qualité 3", "Qualité 4"],
    "valeurs_dominantes": ["Valeur Schwartz du référentiel 1", "Valeur 2", "Valeur 3"],
    "savoirs_etre_dominants": ["Savoir-être pro du référentiel 1", "Savoir-être 2", "Savoir-être 3"],
    "competences_oms": ["Compétence psychosociale OMS 1", "CPS 2", "CPS 3"],
    "competences_transferables": ["Compétence transférable du référentiel 1", "CT 2", "CT 3", "CT 4"],
    "metiers_associes": ["Métier associé du référentiel 1", "Métier 2", "Métier 3"],
    "penseurs": {{"orientaux": ["Penseur 1", "Penseur 2"], "occidentaux": ["Penseur 1", "Penseur 2"]}}
  }},
  "vertu_data": {{
    "name": "Nom de la vertu dominante",
    "cognition": ["Force cognitive 1", "Force cognitive 2", "Force cognitive 3"],
    "conation": ["Force conationale 1", "Force conationale 2", "Force conationale 3"],
    "affection": ["Force affective 1", "Force affective 2", "Force affective 3"],
    "valeurs_schwartz": ["Valeur Schwartz du référentiel 1", "Valeur 2", "Valeur 3"],
    "forces": ["Force de caractère du référentiel 1", "Force 2", "Force 3", "Force 4"],
    "savoirs_etre": ["Savoir-être FT du référentiel 1", "Savoir-être 2", "Savoir-être 3", "Savoir-être 4"]
  }},
  "riasec_profile": {{
    "major": "X",
    "minor": "Y",
    "major_name": "Nom complet",
    "minor_name": "Nom complet",
    "major_description": "Description du type dominant (2-3 phrases)",
    "scores": {{"R": 0-100, "I": 0-100, "A": 0-100, "S": 0-100, "E": 0-100, "C": 0-100}},
    "traits": ["Trait 1", "Trait 2", "Trait 3", "Trait 4"],
    "environnements_preferes": ["Env 1", "Env 2", "Env 3"]
  }},
  "integrated_analysis": {{
    "niveau_1_preuves": {{
      "competences_prouvees": ["Compétence du référentiel 1", "Compétence 2", "Compétence 3"],
      "forces_cles": ["Force du référentiel 1", "Force 2", "Force 3"]
    }},
    "niveau_2_fonctionnement": {{
      "style_travail": "Description du style de travail basée sur les vertus dominantes (2-3 phrases)",
      "environnement_favorable": ["Caractéristique 1", "Caractéristique 2", "Caractéristique 3"]
    }},
    "niveau_3_regulation": {{
      "moteur_interne": "Ce qui motive cette personne selon ses vertus dominantes (1-2 phrases)",
      "leviers_croissance": ["Levier 1", "Levier 2", "Levier 3"],
      "signaux_stress": ["Signal 1", "Signal 2"]
    }},
    "synthese": "Synthèse globale intégrant les vertus dominantes identifiées (4-5 phrases)"
  }},
  "cross_analysis": {{
    "has_cross_analysis": true,
    "synergy_disc": "Comment le style DISC et la boussole MBTI se complètent (2-3 phrases)",
    "synergy_ennea": "Comment les valeurs et le moteur interne se renforcent (2-3 phrases)",
    "tension": "Tension principale à surveiller (1-2 phrases)",
    "integration_insight": "Conseil d'intégration personnalisé (2-3 phrases)"
  }},
  "ofman_quadrant": [
    {{
      "qualite": "Qualité fondamentale issue des vertus dominantes",
      "piege": "L'excès de cette qualité",
      "defi": "Ce qu'il faut développer pour équilibrer",
      "allergie": "Ce qui irrite chez les autres",
      "source": "Vertu / RIASEC / Valeurs",
      "recommandation": "Conseil pratique (1-2 phrases)"
    }},
    {{
      "qualite": "Qualité fondamentale 2",
      "piege": "L'excès",
      "defi": "L'équilibre",
      "allergie": "L'irritant",
      "source": "Vertu / RIASEC / Valeurs",
      "recommandation": "Conseil"
    }},
    {{
      "qualite": "Qualité fondamentale 3",
      "piege": "L'excès",
      "defi": "L'équilibre",
      "allergie": "L'irritant",
      "source": "Vertu / RIASEC / Valeurs",
      "recommandation": "Conseil"
    }}
  ],
  "life_path": {{
    "label": "Titre du chemin de vie professionnelle lié aux vertus dominantes",
    "strengths": ["Force naturelle du référentiel 1", "Force 2", "Force 3"],
    "watchouts": ["Point de vigilance 1", "Point 2"],
    "micro_actions": [
      {{"focus": "Domaine", "action": "Action concrète à mettre en place"}},
      {{"focus": "Domaine", "action": "Action concrète"}}
    ],
    "work_preferences": ["Préférence 1", "Préférence 2", "Préférence 3"]
  }}
}}

IMPORTANT:
- Base ton analyse sur les réponses réelles du candidat.
- Les vertus, forces, qualités, compétences et métiers DOIVENT provenir du référentiel scientifique fourni ci-dessus.
- Sois précis, personnalisé et cohérent entre les différentes dimensions.
- Le profil doit refléter fidèlement les réponses données tout en s'appuyant sur le cadre scientifique du référentiel."""

    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"dclic-{uuid.uuid4()}",
            system_message="Tu es un psychologue du travail expert en orientation professionnelle, spécialisé dans les modèles RIASEC, MBTI, DISC, Schwartz, Seligman & Peterson (6 Vertus), et le Cadran d'Ofman. Tu t'appuies sur le référentiel scientifique fourni pour ancrer ton analyse. Tu génères des analyses précises et personnalisées en JSON pur."
        ).with_model("openai", "gpt-5.2")

        response = await run_llm(chat, UserMessage(text=prompt))

        # Nettoyer la réponse (enlever ```json ... ``` si présent)
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        return json.loads(text)
    except Exception as e:
        logger.error(f"Erreur analyse IA D'CLIC PRO: {e}")
        return _fallback_rich_profile(basic_profile)


def _fallback_rich_profile(bp: dict) -> dict:
    """Profil enrichi de secours si l'IA échoue — utilise le référentiel scientifique."""
    riasec = bp.get("riasec", {})
    scores = riasec.get("scores", {})
    code = riasec.get("code", "SEC")
    sep = bp.get("savoir_etre", {})
    vals = bp.get("valeurs", {})

    # Déduire un MBTI simplifié des scores
    mbti = ""
    mbti += "E" if scores.get("S", 0) + scores.get("E", 0) > scores.get("I", 0) + scores.get("C", 0) else "I"
    mbti += "N" if scores.get("A", 0) + scores.get("I", 0) > scores.get("R", 0) + scores.get("C", 0) else "S"
    mbti += "F" if scores.get("S", 0) + scores.get("A", 0) > scores.get("E", 0) + scores.get("R", 0) else "T"
    mbti += "J" if scores.get("C", 0) + scores.get("E", 0) > scores.get("A", 0) + scores.get("R", 0) else "P"

    dom = code[0] if code else "S"
    top_vals = [v["code"] for v in vals.get("dominantes", [])[:3]]
    top_sep = [s["code"] for s in sep.get("forces", [])[:4]]

    # Déduire la vertu dominante depuis les scores RIASEC + valeurs
    vertu_mapping = {"S": "humanite", "I": "sagesse", "A": "transcendance", "E": "justice", "C": "temperance", "R": "courage"}
    vertu_code = vertu_mapping.get(dom, "humanite")
    vertu = MATRICE_VERTUS[vertu_code]
    citation_data = CITATIONS_VERTUS.get(vertu_code, {})

    return {
        "mbti": mbti,
        "disc": dom + (code[1] if len(code) > 1 else ""),
        "disc_label": f"Profil {RIASEC_LABELS.get(dom, dom).split('—')[0].strip()}",
        "disc_scores": {"D": min(scores.get("E", 3) * 10, 100), "I": min(scores.get("S", 3) * 10, 100), "S": min(scores.get("C", 3) * 10, 100), "C": min(scores.get("R", 3) * 10, 100)},
        "compass": {
            "summary": f"Profil {mbti} — Une personne orientée vers l'action et les relations humaines.",
            "axes": [
                {"name": "Énergie", "dominant": mbti[0], "pole_a": {"code": "E", "label": "Extraversion"}, "pole_b": {"code": "I", "label": "Introversion"}, "insight": "Votre source d'énergie principale."},
                {"name": "Perception", "dominant": mbti[1], "pole_a": {"code": "S", "label": "Sensation"}, "pole_b": {"code": "N", "label": "Intuition"}, "insight": "Comment vous percevez l'information."},
                {"name": "Décision", "dominant": mbti[2], "pole_a": {"code": "T", "label": "Pensée"}, "pole_b": {"code": "F", "label": "Sentiment"}, "insight": "Comment vous prenez vos décisions."},
                {"name": "Organisation", "dominant": mbti[3], "pole_a": {"code": "J", "label": "Jugement"}, "pole_b": {"code": "P", "label": "Perception"}, "insight": "Comment vous organisez votre vie."},
            ],
        },
        "vertus_profile": {
            "dominant": vertu_code,
            "dominant_name": vertu["nom"],
            "description": vertu["description"],
            "citation": citation_data.get("citations", [""])[0],
            "vertus_scores": {k: 60 + (10 if k == vertu_code else 0) for k in MATRICE_VERTUS},
            "forces_caractere": vertu["forces_caractere"],
            "qualites_dominantes": vertu["qualites_humaines"][:4],
            "valeurs_dominantes": [VALEUR_LABELS.get(v, v) for v in top_vals] or vertu["valeurs_schwartz"][:3],
            "savoirs_etre_dominants": [SEP_LABELS.get(s, s) for s in top_sep] or vertu["savoirs_etre_professionnels"],
            "competences_oms": vertu["competences_psychosociales_oms"],
            "competences_transferables": vertu["competences_transferables"][:4],
            "metiers_associes": vertu["metiers_associes"][:3],
            "penseurs": {
                "orientaux": citation_data.get("penseurs_orientaux", [])[:3],
                "occidentaux": citation_data.get("penseurs_occidentaux", [])[:3],
            },
        },
        "vertu_data": {
            "name": vertu["nom"],
            "cognition": vertu["forces_caractere"][:3],
            "conation": vertu["competences_transferables"][:3],
            "affection": vertu["qualites_humaines"][:3],
            "valeurs_schwartz": [VALEUR_LABELS.get(v, v) for v in top_vals] or vertu["valeurs_schwartz"],
            "forces": vertu["forces_caractere"],
            "savoirs_etre": [SEP_LABELS.get(s, s) for s in top_sep] or vertu["savoirs_etre_professionnels"],
        },
        "riasec_profile": {
            "major": code[0] if code else "S", "minor": code[1] if len(code) > 1 else "E",
            "major_name": RIASEC_LABELS.get(code[0], "").split("—")[0].strip() if code else "Social",
            "minor_name": RIASEC_LABELS.get(code[1], "").split("—")[0].strip() if len(code) > 1 else "Entreprenant",
            "major_description": RIASEC_LABELS.get(code[0], "") if code else "",
            "scores": {k: min(v * 10, 100) for k, v in scores.items()},
            "traits": vertu["qualites_detaillees"][:4],
            "environnements_preferes": ["Équipe pluridisciplinaire", "Contact humain", "Structure souple"],
        },
        "integrated_analysis": {
            "niveau_1_preuves": {"competences_prouvees": vertu["competences_transferables"][:3], "forces_cles": vertu["forces_caractere"][:3]},
            "niveau_2_fonctionnement": {"style_travail": f"Profil orienté vers la {vertu['nom'].lower()}, avec des compétences en {', '.join(vertu['competences_transferables'][:2])}.", "environnement_favorable": ["Travail en équipe", "Missions variées", "Autonomie encadrée"]},
            "niveau_3_regulation": {"moteur_interne": f"Le sens et les valeurs de {vertu['valeurs_schwartz'][0].lower()} guident cette personne.", "leviers_croissance": ["Prise de recul", "Gestion des priorités"], "signaux_stress": ["Surcharge", "Manque de reconnaissance"]},
            "synthese": f"Un profil ancré dans la vertu de {vertu['nom']}, avec des forces en {', '.join(vertu['forces_caractere'][:3])}.",
        },
        "cross_analysis": {
            "has_cross_analysis": True,
            "synergy_disc": "Le style comportemental et les préférences cognitives convergent vers un profil collaboratif.",
            "synergy_ennea": f"Les valeurs de {vertu['valeurs_schwartz'][0].lower()} renforcent la motivation intrinsèque.",
            "tension": "Risque de sur-engagement au détriment de l'équilibre personnel.",
            "integration_insight": "Développer la capacité à dire non pour préserver son énergie.",
        },
        "ofman_quadrant": [
            {"qualite": vertu["qualites_humaines"][0], "piege": "Excès d'implication", "defi": "Distance juste", "allergie": "Indifférence", "source": f"Vertu {vertu['nom']}", "recommandation": "Apprendre à équilibrer engagement et recul."},
            {"qualite": vertu["qualites_humaines"][1] if len(vertu["qualites_humaines"]) > 1 else "Organisation", "piege": "Rigidité", "defi": "Flexibilité", "allergie": "Chaos", "source": "RIASEC", "recommandation": "Accepter l'imprévu comme source d'opportunité."},
            {"qualite": vertu["qualites_humaines"][2] if len(vertu["qualites_humaines"]) > 2 else "Initiative", "piege": "Impatience", "defi": "Patience stratégique", "allergie": "Passivité", "source": "Valeurs", "recommandation": "Attendre le bon moment avant d'agir."},
        ],
        "life_path": {
            "label": f"Parcours orienté {vertu['nom'].lower()}",
            "strengths": vertu["forces_caractere"][:3],
            "watchouts": ["Surcharge émotionnelle", "Difficulté à déléguer"],
            "micro_actions": [{"focus": "Équilibre", "action": "Définir des limites claires dans les relations professionnelles."}, {"focus": "Développement", "action": f"Explorer des métiers liés à la {vertu['nom'].lower()} : {', '.join(vertu['metiers_associes'][:3])}."}],
            "work_preferences": ["Travail en équipe", "Contact humain", "Missions à impact social"],
        },
    }


# ─── Routes ──────────────────────────────────────────────────────────

def register_dclic_routes(app, db_ref):
    global db
    db = db_ref

    @router.get("/questionnaire")
    async def get_questionnaire():
        return {
            "title": "D'CLIC PRO — Révélateur de potentiel professionnel",
            "description": "Identifiez vos intérêts, valeurs, qualités et compétences cachées pour révéler votre potentiel.",
            "blocs": [
                {"id": "archeologie", "title": "Archéologie des compétences", "subtitle": "Explorons vos compétences visibles et cachées", "icon": "pickaxe", "type": "open_text", "questions": BLOC_1_ARCHEOLOGIE},
                {"id": "riasec", "title": "Intérêts professionnels", "subtitle": "Évaluez chaque affirmation de 1 (pas du tout) à 5 (tout à fait)", "icon": "compass", "type": "scale", "scale_min": 1, "scale_max": 5, "scale_labels": {"1": "Pas du tout", "2": "Un peu", "3": "Moyennement", "4": "Beaucoup", "5": "Tout à fait"}, "questions": [{"id": q["id"], "text": q["text"], "type": "scale"} for q in BLOC_2_RIASEC]},
                {"id": "valeurs", "title": "Valeurs professionnelles", "subtitle": "Évaluez l'importance de chaque valeur de 1 (pas important) à 5 (essentiel)", "icon": "heart", "type": "scale", "scale_min": 1, "scale_max": 5, "scale_labels": {"1": "Pas important", "2": "Peu important", "3": "Moyennement", "4": "Important", "5": "Essentiel"}, "questions": [{"id": q["id"], "text": q["text"], "type": "scale"} for q in BLOC_3_VALEURS]},
                {"id": "savoir_etre", "title": "Savoir-être professionnels", "subtitle": "Évaluez-vous de 1 (rarement) à 5 (toujours)", "icon": "user-check", "type": "scale", "scale_min": 1, "scale_max": 5, "scale_labels": {"1": "Rarement", "2": "Parfois", "3": "Souvent", "4": "Très souvent", "5": "Toujours"}, "questions": [{"id": q["id"], "text": q["text"], "type": "scale"} for q in BLOC_4_SAVOIR_ETRE]},
                {"id": "projection", "title": "Projection professionnelle", "subtitle": "Projetez-vous dans votre avenir professionnel", "icon": "rocket", "type": "mixed", "questions": BLOC_5_PROJECTION},
            ],
        }

    @router.post("/submit")
    async def submit_dclic(body: dict = {}):
        token = body.get("token")
        answers = body.get("answers", {})

        if len(answers) < 15:
            raise HTTPException(400, f"Questionnaire incomplet ({len(answers)} réponses, minimum 15 requises)")

        # 1. Scores déterministes
        basic_profile = compute_dclic_profile(answers)

        # 2. Analyse IA enrichie (MBTI, DISC, Ofman, etc.)
        rich = await generate_rich_profile(answers, basic_profile)

        # 3. Fusionner
        profile = {**basic_profile, **rich}

        doc = {
            "access_code": profile["access_code"],
            "answers": answers,
            "profile": profile,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        if token:
            doc["token_id"] = token
            await db.passports.update_one(
                {"token_id": token},
                {"$set": {"dclic_results": profile, "dclic_completed_at": datetime.now(timezone.utc).isoformat()}},
                upsert=True,
            )

        await db.dclic_profiles.insert_one(doc)
        doc.pop("_id", None)

        return {"success": True, "access_code": profile["access_code"], "profile": profile}

    @router.get("/results/{code}")
    async def get_dclic_results(code: str):
        doc = await db.dclic_profiles.find_one({"access_code": code.upper()}, {"_id": 0})
        if not doc:
            raise HTTPException(404, "Code D'CLIC PRO introuvable")
        return doc.get("profile", doc)

    @router.get("/my-results")
    async def get_my_dclic_results(token: str):
        passport = await db.passports.find_one({"token_id": token}, {"_id": 0})
        if not passport or not passport.get("dclic_results"):
            raise HTTPException(404, "Aucun résultat D'CLIC PRO trouvé. Passez d'abord le test.")
        return passport["dclic_results"]

    app.include_router(router)
