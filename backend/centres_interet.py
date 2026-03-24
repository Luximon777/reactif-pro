"""
Moteur d'analyse des centres d'intérêt - Re'Actif Pro
Transforme les loisirs en compétences transversales, valeurs et leviers d'employabilité.
"""

RULES = [
    {
        "keywords": ["football", "basket", "handball", "rugby", "volley", "sport collectif", "equipe"],
        "category": "sport_collectif",
        "competences": ["travail en équipe", "discipline", "gestion de la pression", "coordination", "persévérance"],
        "valeurs": ["engagement", "coopération", "dépassement de soi"],
        "environnements": ["équipes opérationnelles", "environnements collaboratifs", "fonctions nécessitant coordination et réactivité"],
        "cv_template": "Pratique régulière de {label}, illustrant le travail en équipe, la discipline et la gestion de la pression.",
    },
    {
        "keywords": ["course", "running", "marathon", "natation", "vélo", "cyclisme", "triathlon", "trail", "sport individuel", "musculation", "fitness"],
        "category": "sport_individuel",
        "competences": ["autonomie", "rigueur", "endurance", "persévérance", "gestion de l'effort"],
        "valeurs": ["constance", "dépassement de soi", "exigence personnelle"],
        "environnements": ["missions demandant autonomie", "postes avec objectifs individuels", "activités nécessitant régularité"],
        "cv_template": "Pratique de {label}, traduisant une bonne autonomie, de la rigueur et une forte persévérance.",
    },
    {
        "keywords": ["théâtre", "theatre", "impro", "improvisation", "chant", "danse", "musique", "piano", "guitare", "batterie", "chorale"],
        "category": "artistique_expression",
        "competences": ["aisance orale", "expression", "créativité", "gestion du regard des autres", "confiance en soi"],
        "valeurs": ["expression", "créativité", "sensibilité"],
        "environnements": ["métiers relationnels", "animation", "communication", "présentation ou médiation"],
        "cv_template": "Engagement dans {label}, favorisant l'aisance relationnelle, l'expression et la créativité.",
    },
    {
        "keywords": ["dessin", "peinture", "photo", "photographie", "écriture", "lecture créative", "création", "couture", "bricolage", "sculpture", "poterie", "céramique", "vidéo"],
        "category": "creatif",
        "competences": ["créativité", "sens de l'observation", "patience", "concentration", "capacité de conception"],
        "valeurs": ["créativité", "esthétique", "expression personnelle"],
        "environnements": ["marketing", "design", "innovation", "création de contenu"],
        "cv_template": "Passion pour {label}, développant la créativité, le sens du détail et la capacité de conception.",
    },
    {
        "keywords": ["bénévolat", "benevolat", "association", "humanitaire", "volontariat", "croix-rouge", "restos du coeur", "secours populaire", "entraide", "maraude"],
        "category": "social_engagement",
        "competences": ["empathie", "sens du service", "communication", "écoute active", "organisation"],
        "valeurs": ["solidarité", "altruisme", "engagement citoyen"],
        "environnements": ["accompagnement social", "relation client", "fonctions RH", "management bienveillant"],
        "cv_template": "Implication dans {label}, reflétant un sens aigu du service, de l'empathie et de la communication.",
    },
    {
        "keywords": ["lecture", "échecs", "chess", "puzzle", "mots croisés", "sudoku", "jeux stratégiques", "jeux de société", "philosophie", "histoire", "documentaire"],
        "category": "intellectuel",
        "competences": ["analyse", "concentration", "curiosité intellectuelle", "pensée critique", "prise de décision"],
        "valeurs": ["réflexion", "savoir", "rigueur intellectuelle"],
        "environnements": ["postes analytiques", "recherche", "gestion de projets complexes", "conseil"],
        "cv_template": "Intérêt pour {label}, témoignant de capacités d'analyse, de concentration et de curiosité intellectuelle.",
    },
    {
        "keywords": ["informatique", "programmation", "code", "maker", "robotique", "électronique", "impression 3d", "arduino", "raspberry", "jeux vidéo", "gaming", "modding"],
        "category": "technique",
        "competences": ["logique", "résolution de problème", "rigueur", "autonomie technique", "innovation"],
        "valeurs": ["curiosité technique", "précision", "persévérance"],
        "environnements": ["technique", "IT", "industrie", "innovation", "R&D"],
        "cv_template": "Pratique de {label}, démontrant une logique solide, de la rigueur et une capacité à résoudre des problèmes complexes.",
    },
    {
        "keywords": ["yoga", "méditation", "relaxation", "tai chi", "qi gong", "sophrologie", "bien-être", "randonnée", "marche", "jardinage", "nature"],
        "category": "bien_etre",
        "competences": ["gestion du stress", "équilibre", "patience", "écoute de soi", "résilience"],
        "valeurs": ["harmonie", "bien-être", "développement personnel"],
        "environnements": ["postes nécessitant calme et recul", "accompagnement", "management", "qualité de vie au travail"],
        "cv_template": "Pratique de {label}, favorisant la gestion du stress, l'équilibre personnel et la résilience.",
    },
    {
        "keywords": ["voyage", "voyages", "découverte", "langues", "culture", "échange", "international", "backpack", "road trip"],
        "category": "exploration",
        "competences": ["adaptabilité", "ouverture d'esprit", "communication interculturelle", "débrouillardise", "curiosité"],
        "valeurs": ["ouverture", "découverte", "tolérance"],
        "environnements": ["environnements internationaux", "postes multilingues", "gestion de la diversité", "commercial export"],
        "cv_template": "Passion pour {label}, illustrant une forte adaptabilité, une ouverture d'esprit et une aisance interculturelle.",
    },
]

IMPLICATION_WEIGHTS = {
    "occasionnel": {"credibility": "modérée", "score_factor": 0.6},
    "regulier": {"credibility": "moyenne", "score_factor": 0.8},
    "intensif": {"credibility": "forte", "score_factor": 1.0},
}


def _normalize(text):
    import unicodedata
    return unicodedata.normalize("NFD", text.lower()).encode("ascii", "ignore").decode("ascii").strip()


def find_matching_rule(label):
    normalized = _normalize(label)
    for rule in RULES:
        for keyword in rule["keywords"]:
            if _normalize(keyword) in normalized:
                return rule
    return None


def analyze_centre_interet(label, implication="regulier"):
    rule = find_matching_rule(label)

    if not rule:
        return {
            "label": label,
            "category": "autre",
            "competences": ["adaptabilité", "curiosité"],
            "valeurs": ["ouverture"],
            "environnements": [],
            "implication": implication,
            "credibility": IMPLICATION_WEIGHTS.get(implication, IMPLICATION_WEIGHTS["regulier"])["credibility"],
            "cv_reformulation": f"Intérêt pour {label}, témoignant de curiosité et d'ouverture.",
        }

    weight = IMPLICATION_WEIGHTS.get(implication, IMPLICATION_WEIGHTS["regulier"])

    return {
        "label": label,
        "category": rule["category"],
        "competences": rule["competences"],
        "valeurs": rule["valeurs"],
        "environnements": rule["environnements"],
        "implication": implication,
        "credibility": weight["credibility"],
        "cv_reformulation": rule["cv_template"].format(label=label),
    }


def analyze_multiple(centres_list):
    """
    centres_list: list of dicts with keys: label, implication (optional)
    or list of strings
    """
    results = []
    all_competences = set()
    all_valeurs = set()
    all_environnements = set()

    for ci in centres_list:
        if isinstance(ci, str):
            label = ci
            implication = "regulier"
        else:
            label = ci.get("label", ci.get("nom", ""))
            implication = ci.get("implication", "regulier")

        if not label.strip():
            continue

        result = analyze_centre_interet(label.strip(), implication)
        results.append(result)
        all_competences.update(result["competences"])
        all_valeurs.update(result["valeurs"])
        all_environnements.update(result["environnements"])

    return {
        "analyses": results,
        "competences_transversales": list(all_competences),
        "valeurs_dominantes": list(all_valeurs),
        "environnements_adaptes": list(all_environnements),
        "cv_reformulations": [r["cv_reformulation"] for r in results],
    }
