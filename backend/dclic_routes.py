"""
D'CLIC PRO — Questionnaire & Scoring Engine (Version originale complète)
5 Blocs : Archéologie, RIASEC, Valeurs, Savoir-être, Projection
Restitution : RIASEC, Carte valeurs, Forces, Savoir-être, Compétences, Pistes métiers
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import json, logging, secrets, string

router = APIRouter(prefix="/api/dclic", tags=["dclic"])

# ─── BLOC 1 : Archéologie des compétences (10 questions ouvertes) ─────

BLOC_1_ARCHEOLOGIE = [
    {
        "id": "arche_1",
        "text": "Quelle activité avez-vous réalisée dans votre vie dont vous êtes le plus fier(e) ?",
        "type": "open_text",
        "placeholder": "Décrivez cette activité et ce qu'elle représente pour vous...",
    },
    {
        "id": "arche_2",
        "text": "Dans quelles situations les autres viennent-ils spontanément vous demander de l'aide ?",
        "type": "open_text",
        "placeholder": "Ex: pour organiser, réparer, écouter, expliquer...",
    },
    {
        "id": "arche_3",
        "text": "Avez-vous déjà organisé un événement, une activité ou coordonné plusieurs personnes ?",
        "type": "open_text",
        "placeholder": "Décrivez ce que vous avez organisé et votre rôle...",
    },
    {
        "id": "arche_4",
        "text": "Avez-vous déjà accompagné un proche dans une démarche importante ?",
        "type": "open_text",
        "placeholder": "Ex: démarche administrative, recherche d'emploi, soutien scolaire...",
    },
    {
        "id": "arche_5",
        "text": "Avez-vous exercé des responsabilités dans une association, un club, une communauté ou un groupe informel ?",
        "type": "open_text",
        "placeholder": "Décrivez votre rôle et vos responsabilités...",
    },
    {
        "id": "arche_6",
        "text": "Quelle difficulté importante avez-vous réussi à surmonter dans votre parcours ?",
        "type": "open_text",
        "placeholder": "Décrivez la difficulté et comment vous l'avez surmontée...",
    },
    {
        "id": "arche_7",
        "text": "Quels savoir-faire utilisez-vous régulièrement sans considérer qu'il s'agit de compétences ?",
        "type": "open_text",
        "placeholder": "Ex: cuisiner, bricoler, écouter, organiser, négocier...",
    },
    {
        "id": "arche_8",
        "text": "Qu'avez-vous appris en dehors de l'école ou du travail ?",
        "type": "open_text",
        "placeholder": "Ex: langue, instrument, mécanique, couture, informatique...",
    },
    {
        "id": "arche_9",
        "text": "Quelle activité vous donne le sentiment d'être particulièrement efficace ?",
        "type": "open_text",
        "placeholder": "L'activité où vous vous sentez dans votre élément...",
    },
    {
        "id": "arche_10",
        "text": "Si vous deviez transmettre une compétence à quelqu'un demain, laquelle choisiriez-vous ?",
        "type": "open_text",
        "placeholder": "La compétence que vous maîtrisez le mieux...",
    },
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
    {
        "id": "proj_1",
        "text": "Quels métiers vous attirent aujourd'hui ?",
        "type": "open_text",
        "placeholder": "Listez 2 ou 3 métiers qui vous attirent...",
    },
    {
        "id": "proj_2",
        "text": "Quels métiers vous n'envisageriez jamais ?",
        "type": "open_text",
        "placeholder": "Listez les métiers qui ne vous correspondent pas du tout...",
    },
    {
        "id": "proj_3",
        "text": "Préférez-vous travailler avec :",
        "type": "choice",
        "choices": [
            {"value": "personnes", "label": "Les personnes"},
            {"value": "donnees", "label": "Les données"},
            {"value": "objets", "label": "Les objets"},
            {"value": "idees", "label": "Les idées"},
            {"value": "combinaison", "label": "Une combinaison de plusieurs"},
        ],
    },
    {
        "id": "proj_4",
        "text": "Dans quel environnement vous sentez-vous le plus à l'aise ?",
        "type": "choice",
        "choices": [
            {"value": "bureau", "label": "En bureau / espace structuré"},
            {"value": "terrain", "label": "Sur le terrain / en extérieur"},
            {"value": "atelier", "label": "En atelier / espace technique"},
            {"value": "contact", "label": "En contact direct avec le public"},
            {"value": "domicile", "label": "À domicile / en télétravail"},
            {"value": "itinerant", "label": "En déplacement / itinérant"},
        ],
    },
    {
        "id": "proj_5",
        "text": "Quel serait pour vous un travail réussi dans cinq ans ?",
        "type": "open_text",
        "placeholder": "Décrivez votre vision d'un travail épanouissant dans 5 ans...",
    },
]


# ─── Scoring Engine ──────────────────────────────────────────────────

RIASEC_LABELS = {
    "R": "Réaliste — Concret, manuel, technique",
    "I": "Investigateur — Analytique, intellectuel, scientifique",
    "A": "Artistique — Créatif, expressif, imaginatif",
    "S": "Social — Aidant, coopératif, pédagogue",
    "E": "Entreprenant — Leader, persuasif, ambitieux",
    "C": "Conventionnel — Organisé, précis, méthodique",
}

VALEUR_LABELS = {
    "benevolence": "Bienveillance — Bien-être des proches et des autres",
    "stimulation": "Stimulation — Nouveauté, défis, apprentissage",
    "securite": "Sécurité — Stabilité, protection, cadre",
    "autonomie": "Autonomie — Liberté de pensée et d'action",
    "reussite": "Réussite — Accomplissement et reconnaissance",
    "universalisme": "Universalisme — Justice sociale, environnement",
    "conformite": "Conformité — Respect des règles et de l'ordre",
    "tradition": "Tradition — Respect des convictions et des valeurs",
}

SEP_LABELS = {
    "fiabilite": "Fiabilité — Respect des engagements",
    "adaptabilite": "Adaptabilité — Souplesse face au changement",
    "initiative": "Initiative — Proactivité et prise de décision",
    "gestion_stress": "Gestion du stress — Calme sous pression",
    "cooperation": "Coopération — Esprit d'équipe",
    "ouverture": "Ouverture — Acceptation du feedback",
    "perseverance": "Persévérance — Ténacité face aux obstacles",
    "organisation": "Organisation — Gestion multi-tâches",
    "communication": "Communication — Aisance relationnelle",
    "resolution": "Résolution — Orientation solutions",
}


def compute_dclic_profile(answers: dict) -> dict:
    """Calcule le profil D'CLIC PRO complet."""

    # ── Archéologie des compétences ──────────────────────────────
    archeologie = {}
    for q in BLOC_1_ARCHEOLOGIE:
        val = answers.get(q["id"], "")
        if val and len(str(val)) > 2:
            archeologie[q["id"]] = str(val)

    # Catégorisation archéologique
    arche_categories = {
        "visibles": [],
        "enfouies": [],
        "transferables": [],
        "adaptatives": [],
        "potentielles": [],
    }
    # Q1 (fierté) + Q9 (efficacité) = visibles
    for k in ["arche_1", "arche_9"]:
        if archeologie.get(k):
            arche_categories["visibles"].append(archeologie[k])
    # Q3 (organisation) + Q5 (responsabilités asso) = transferables
    for k in ["arche_3", "arche_5"]:
        if archeologie.get(k):
            arche_categories["transferables"].append(archeologie[k])
    # Q4 (accompagnement) + Q2 (aide spontanée) = enfouies
    for k in ["arche_2", "arche_4"]:
        if archeologie.get(k):
            arche_categories["enfouies"].append(archeologie[k])
    # Q6 (difficulté surmontée) = adaptatives
    if archeologie.get("arche_6"):
        arche_categories["adaptatives"].append(archeologie["arche_6"])
    # Q7 (savoir-faire non reconnus) + Q8 (apprentissages informels) + Q10 (transmission) = potentielles
    for k in ["arche_7", "arche_8", "arche_10"]:
        if archeologie.get(k):
            arche_categories["potentielles"].append(archeologie[k])

    # ── RIASEC ───────────────────────────────────────────────────
    riasec_scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
    for item in BLOC_2_RIASEC:
        val = answers.get(item["id"])
        if val is not None:
            try:
                score = int(val)
                riasec_scores[item["dimension"]] += score
            except (ValueError, TypeError):
                pass

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

    # ── Valeurs (Schwartz simplifié) ─────────────────────────────
    valeur_scores = {}
    for item in BLOC_3_VALEURS:
        val = answers.get(item["id"])
        dim = item["dimension"]
        if val is not None:
            try:
                score = int(val)
                valeur_scores[dim] = valeur_scores.get(dim, 0) + score
            except (ValueError, TypeError):
                pass

    valeur_sorted = sorted(valeur_scores.items(), key=lambda x: x[1], reverse=True)
    valeurs_dominantes = [
        {"code": v[0], "score": v[1], "label": VALEUR_LABELS.get(v[0], v[0])}
        for v in valeur_sorted[:4]
    ]

    # ── Savoir-être professionnels (SEP) ─────────────────────────
    sep_scores = {}
    for item in BLOC_4_SAVOIR_ETRE:
        val = answers.get(item["id"])
        dim = item["dimension"]
        if val is not None:
            try:
                sep_scores[dim] = int(val)
            except (ValueError, TypeError):
                pass

    sep_sorted = sorted(sep_scores.items(), key=lambda x: x[1], reverse=True)
    sep_forces = [
        {"code": s[0], "score": s[1], "label": SEP_LABELS.get(s[0], s[0])}
        for s in sep_sorted if s[1] >= 4
    ]
    sep_all = [
        {"code": s[0], "score": s[1], "label": SEP_LABELS.get(s[0], s[0])}
        for s in sep_sorted
    ]

    # ── Projection professionnelle ───────────────────────────────
    projection = {
        "metiers_attires": answers.get("proj_1", ""),
        "metiers_exclus": answers.get("proj_2", ""),
        "preference_travail": answers.get("proj_3", ""),
        "environnement": answers.get("proj_4", ""),
        "vision_5_ans": answers.get("proj_5", ""),
    }

    # ── Code d'accès ─────────────────────────────────────────────
    code = "-".join([
        "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        for _ in range(2)
    ])

    return {
        "access_code": code,
        "archeologie_competences": {
            "reponses": archeologie,
            "categories": arche_categories,
        },
        "riasec": {
            "code": riasec_code,
            "dominant": riasec_sorted[0][0] if riasec_sorted else "S",
            "dominant_label": RIASEC_LABELS.get(riasec_sorted[0][0], "") if riasec_sorted else "",
            "scores": riasec_scores,
            "profile": riasec_profile,
        },
        "valeurs": {
            "dominantes": valeurs_dominantes,
            "scores": dict(valeur_scores),
        },
        "savoir_etre": {
            "forces": sep_forces,
            "all": sep_all,
        },
        "projection": projection,
    }


# ─── Routes ──────────────────────────────────────────────────────

def register_dclic_routes(app, db_ref):
    global db
    db = db_ref

    @router.get("/questionnaire")
    async def get_questionnaire():
        return {
            "title": "D'CLIC PRO — Révélateur de potentiel professionnel",
            "description": "Identifiez vos intérêts, valeurs, qualités et compétences cachées pour révéler votre potentiel.",
            "blocs": [
                {
                    "id": "archeologie",
                    "title": "Archéologie des compétences",
                    "subtitle": "Explorons vos compétences visibles et cachées",
                    "icon": "pickaxe",
                    "type": "open_text",
                    "questions": BLOC_1_ARCHEOLOGIE,
                },
                {
                    "id": "riasec",
                    "title": "Intérêts professionnels",
                    "subtitle": "Évaluez chaque affirmation de 1 (pas du tout) à 5 (tout à fait)",
                    "icon": "compass",
                    "type": "scale",
                    "scale_min": 1,
                    "scale_max": 5,
                    "scale_labels": {"1": "Pas du tout", "2": "Un peu", "3": "Moyennement", "4": "Beaucoup", "5": "Tout à fait"},
                    "questions": [{"id": q["id"], "text": q["text"], "type": "scale"} for q in BLOC_2_RIASEC],
                },
                {
                    "id": "valeurs",
                    "title": "Valeurs professionnelles",
                    "subtitle": "Évaluez l'importance de chaque valeur de 1 (pas important) à 5 (essentiel)",
                    "icon": "heart",
                    "type": "scale",
                    "scale_min": 1,
                    "scale_max": 5,
                    "scale_labels": {"1": "Pas important", "2": "Peu important", "3": "Moyennement", "4": "Important", "5": "Essentiel"},
                    "questions": [{"id": q["id"], "text": q["text"], "type": "scale"} for q in BLOC_3_VALEURS],
                },
                {
                    "id": "savoir_etre",
                    "title": "Savoir-être professionnels",
                    "subtitle": "Évaluez-vous de 1 (rarement) à 5 (toujours)",
                    "icon": "user-check",
                    "type": "scale",
                    "scale_min": 1,
                    "scale_max": 5,
                    "scale_labels": {"1": "Rarement", "2": "Parfois", "3": "Souvent", "4": "Très souvent", "5": "Toujours"},
                    "questions": [{"id": q["id"], "text": q["text"], "type": "scale"} for q in BLOC_4_SAVOIR_ETRE],
                },
                {
                    "id": "projection",
                    "title": "Projection professionnelle",
                    "subtitle": "Projetez-vous dans votre avenir professionnel",
                    "icon": "rocket",
                    "type": "mixed",
                    "questions": BLOC_5_PROJECTION,
                },
            ],
        }

    @router.post("/submit")
    async def submit_dclic(body: dict = {}):
        token = body.get("token")
        answers = body.get("answers", {})

        if len(answers) < 15:
            raise HTTPException(400, f"Questionnaire incomplet ({len(answers)} réponses minimum 15 requises)")

        profile = compute_dclic_profile(answers)

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
                {"$set": {
                    "dclic_results": profile,
                    "dclic_completed_at": datetime.now(timezone.utc).isoformat(),
                }},
                upsert=True,
            )

        await db.dclic_profiles.insert_one(doc)
        doc.pop("_id", None)

        return {
            "success": True,
            "access_code": profile["access_code"],
            "profile": profile,
        }

    @router.get("/results/{code}")
    async def get_dclic_results(code: str):
        doc = await db.dclic_profiles.find_one(
            {"access_code": code.upper()},
            {"_id": 0},
        )
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
