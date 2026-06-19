"""
D'CLIC PRO — Référentiel scientifique des Vertus, Forces et Compétences
Sources : Seligman & Peterson (2003), Schwartz, OMS, France Travail
Fichiers de référence : archeologie_competences.ods, tableau_ck1.xlsx, tableau_ck.ods
"""

# ─── Matrice de synthèse (6 Vertus de Seligman & Peterson) ────────────
# Source : archeologie_competences.ods
MATRICE_VERTUS = {
    "sagesse": {
        "nom": "Sagesse et Connaissance",
        "description": "Forces cognitives qui favorisent l'acquisition et l'usage de la connaissance.",
        "forces_caractere": ["Créativité", "Curiosité", "Jugement", "Amour de l'apprentissage", "Perspective"],
        "valeurs_schwartz": ["Autonomie", "Stimulation", "Réalisation de soi"],
        "qualites_humaines": ["Indépendance", "Créativité", "Curiosité", "Ouverture d'esprit", "Audace", "Liberté de pensée"],
        "competences_psychosociales_oms": ["Pensée critique", "Pensée créative", "Prise de décision"],
        "savoirs_etre_professionnels": [
            "Faire preuve de curiosité",
            "Faire preuve de créativité, d'inventivité",
            "Prendre des initiatives et être force de proposition",
        ],
        # Données détaillées (tableau_ck1.xlsx)
        "identite": ["Sagesse", "Connaissance", "Tempérance", "Prudence"],
        "valeurs_detaillees": [
            "Patience", "Ouverture d'esprit", "Indulgence", "Pardon",
            "Modestie", "Créativité", "Curiosité", "Aimer apprendre",
        ],
        "qualites_detaillees": [
            "Courtoisie", "Gentillesse", "Consultation", "Adaptabilité",
            "Sincérité", "Sobriété", "Modeste", "Pardonner",
        ],
        "competences_sociales": [
            "Prudent", "Modéré", "Calme", "Docile",
            "Raisonnable", "Curieux", "Maîtrise de soi",
        ],
        "competences_transferables": [
            "Diplomate", "Stable", "Prévoyant", "Médiateur", "Gérer son stress",
        ],
        "metiers_associes": ["Psychologue", "Conseiller", "Médiateur", "Chercheur", "Formateur"],
    },
    "courage": {
        "nom": "Courage",
        "description": "Forces émotionnelles qui impliquent l'exercice de la volonté pour atteindre les buts que l'on s'est fixés, malgré les obstacles internes et externes.",
        "forces_caractere": ["Bravoure", "Persévérance", "Honnêteté", "Enthousiasme"],
        "valeurs_schwartz": ["Hédonisme", "Réalisation de soi", "Stimulation"],
        "qualites_humaines": ["Joie de vivre", "Optimisme", "Gratitude", "Ambition", "Détermination", "Passion"],
        "competences_psychosociales_oms": ["Gestion du stress", "Résilience", "Estime de soi"],
        "savoirs_etre_professionnels": [
            "Faire preuve de persévérance",
            "Gérer son stress",
            "Faire preuve de réactivité",
        ],
        "identite": ["Courage", "Droiture"],
        "valeurs_detaillees": [
            "Sécurité", "Bravoure", "Persévérance", "Authenticité",
            "Vitalité", "Loyauté", "Dignité", "Excellence",
            "Liberté", "Autonomie",
        ],
        "qualites_detaillees": [
            "Dynamisme", "Fiabilité", "Confiance", "Vigilance",
            "Endurant", "Créatif", "Volonté",
        ],
        "competences_sociales": [
            "Habilité", "Rigueur", "Persévérant", "Responsabilité",
            "Intègre", "Discipline", "Dextérité",
        ],
        "competences_transferables": [
            "Consciencieux", "Minutieux", "Spontané", "Assidu",
            "Engagé", "Entrepreneur", "Organisé", "Déterminé",
            "Objectivité", "Passionné", "Ponctuel",
        ],
        "metiers_associes": ["Comptable", "Assureur", "Banquier", "Artisan", "Entrepreneur"],
    },
    "humanite": {
        "nom": "Humanité",
        "description": "Forces interpersonnelles consistant à tendre vers les autres et à leur venir en aide.",
        "forces_caractere": ["Amour", "Gentillesse", "Intelligence sociale"],
        "valeurs_schwartz": ["Bienveillance", "Universalisme", "Affiliation"],
        "qualites_humaines": ["Empathie", "Gentillesse", "Générosité", "Altruisme", "Compassion", "Écoute", "Solidarité"],
        "competences_psychosociales_oms": ["Communication efficace", "Compétences relationnelles", "Empathie"],
        "savoirs_etre_professionnels": [
            "Être à l'écoute",
            "Avoir le sens du service",
            "Travailler en équipe",
        ],
        "identite": ["Servitude", "Humanité", "Unicité", "Noblesse"],
        "valeurs_detaillees": [
            "Affection", "Gentillesse", "Assertivité", "Humilité",
            "Universalisme", "Unité", "Bonté", "Hospitalité",
            "Magnanimité", "Générosité", "Détachement", "Respect",
        ],
        "qualites_detaillees": [
            "Modestie", "Partager", "Amabilité", "Générosité",
            "Transmettre le savoir", "Accomplissement", "Enseigner",
            "Empathie", "Fidélité",
        ],
        "competences_sociales": [
            "Réservé", "Assertif", "Serviable", "Audacieux",
            "Intuitif", "Protecteur", "Éloquent", "Patient",
        ],
        "competences_transferables": [
            "Flexibilité", "Chercheur", "Conseiller", "Concepteur",
            "Pédagogue", "Perspicace", "Animation",
        ],
        "metiers_associes": ["Éducateur", "Travailleur social", "Infirmier", "Animateur", "Coach"],
    },
    "justice": {
        "nom": "Justice",
        "description": "Forces qui sont à la base d'une vie sociale harmonieuse.",
        "forces_caractere": ["Travail d'équipe", "Équité", "Leadership"],
        "valeurs_schwartz": ["Égalité", "Responsabilité sociale", "Pouvoir"],
        "qualites_humaines": ["Justice", "Impartialité", "Équité", "Respect des droits", "Intégrité", "Humilité", "Charisme", "Influence"],
        "competences_psychosociales_oms": ["Prise de décision", "Pensée critique", "Compétences relationnelles"],
        "savoirs_etre_professionnels": [
            "Faire preuve de leadership",
            "Inspirer, donner du sens",
            "Respecter ses engagements, assumer ses responsabilités",
        ],
        "identite": ["Justice"],
        "valeurs_detaillees": [
            "Honnêteté", "Obéissance", "Équité", "Fermeté", "Harmonie", "Pouvoir",
        ],
        "qualites_detaillees": [
            "Coopération", "Logique", "Juste", "Assertif",
        ],
        "competences_sociales": [
            "Lucidité", "Cohérent", "Esprit d'équipe", "Leadership",
        ],
        "competences_transferables": [
            "Pragmatique", "Méthodique", "Ordonné", "Conciliant", "Travail en équipe",
        ],
        "metiers_associes": ["Juriste", "Manager", "Responsable qualité", "Médiateur social"],
    },
    "temperance": {
        "nom": "Tempérance",
        "description": "Forces qui protègent contre les excès.",
        "forces_caractere": ["Pardon", "Humilité", "Prudence", "Maîtrise de soi"],
        "valeurs_schwartz": ["Conformité", "Sécurité", "Tradition"],
        "qualites_humaines": ["Respect des règles", "Prudence", "Stabilité", "Patience", "Humilité", "Modération", "Gratitude"],
        "competences_psychosociales_oms": ["Gestion des émotions", "Estime de soi", "Résilience"],
        "savoirs_etre_professionnels": [
            "Faire preuve de rigueur et de précision",
            "Organiser son travail selon les priorités et les objectifs",
        ],
        "identite": ["Tempérance", "Prudence"],
        "valeurs_detaillees": [
            "Patience", "Modestie", "Créativité", "Curiosité",
            "Aimer apprendre", "Pardon",
        ],
        "qualites_detaillees": [
            "Sincérité", "Sobriété", "Modeste", "Pardonner",
        ],
        "competences_sociales": [
            "Modéré", "Raisonnable", "Curieux", "Maîtrise de soi",
        ],
        "competences_transferables": [
            "Stable", "Prévoyant", "Gérer son stress", "Médiateur",
        ],
        "metiers_associes": ["Contrôleur de gestion", "Auditeur", "Technicien qualité", "Logisticien"],
    },
    "transcendance": {
        "nom": "Transcendance",
        "description": "Forces qui favorisent l'ouverture à une dimension universelle et donnent un sens à la vie.",
        "forces_caractere": ["Appréciation de la beauté", "Gratitude", "Espoir", "Humour", "Spiritualité"],
        "valeurs_schwartz": ["Universalisme", "Spiritualité", "Bienveillance"],
        "qualites_humaines": ["Tolérance", "Ouverture d'esprit", "Sagesse", "Gratitude", "Recherche de sens", "Sérénité", "Harmonie"],
        "competences_psychosociales_oms": ["Pensée créative", "Gestion du stress", "Résilience"],
        "savoirs_etre_professionnels": [
            "S'adapter aux changements",
            "Faire preuve d'autonomie",
        ],
        "identite": ["Pureté", "Transcendance", "Spiritualité"],
        "valeurs_detaillees": [
            "Fidélité", "Gratitude", "Excellence", "Dévotion",
            "Bienveillance", "Respect", "Foi", "Beauté",
        ],
        "qualites_detaillees": [
            "Joyeux", "Hédoniste", "Écouter", "Altruisme",
            "Compassion", "Politesse", "Tolérance", "Amitié", "Rigueur",
        ],
        "competences_sociales": [
            "Propreté", "Souriant", "Optimisme", "Sensibilité",
            "Solidarité", "Force", "Doux", "Humour",
        ],
        "competences_transferables": [
            "Dévoué", "Sociable", "Souple", "Solidaire", "Délicat", "Bénévole",
        ],
        "metiers_associes": ["Artiste", "Designer", "Thérapeute", "Philosophe", "Accompagnateur"],
    },
}


# ─── Citations philosophiques par vertu ────────────────────────────────
# Source : tableau_ck.ods (Feuil2)
CITATIONS_VERTUS = {
    "sagesse": {
        "citations": [
            "Aristote : « La sagesse ne peut être ni une science ni une technique, c'est un savoir-vivre. »",
            "Descartes : « Par la sagesse, on n'entend pas seulement la prudence dans les affaires, mais une parfaite connaissance de toutes les choses que l'homme peut savoir. »",
            "Einstein : « L'effort d'unir la sagesse et le pouvoir aboutit rarement et seulement très brièvement. »",
        ],
        "penseurs_orientaux": ["Krishnamurti", "Confucius", "Lao Tseu", "Omar Khayyam", "Bouddha"],
        "penseurs_occidentaux": ["Montaigne", "Spinoza", "Nietzsche", "Aristote", "Einstein"],
    },
    "justice": {
        "citations": [
            "Platon : « La justice est la vertu qui attribue à chacun ce qui lui est dû. »",
            "Martin Luther King : « L'injustice où qu'elle soit est une menace pour la justice partout. »",
        ],
        "penseurs_orientaux": ["Confucius", "Bouddha"],
        "penseurs_occidentaux": ["Platon", "Aristote", "Rawls"],
    },
    "courage": {
        "citations": [
            "Nelson Mandela : « Le courage n'est pas l'absence de peur, mais la capacité de la surmonter. »",
            "Aristote : « Le courage est la première des qualités humaines car c'est celle qui garantit toutes les autres. »",
        ],
        "penseurs_orientaux": ["Sun Tzu", "Miyamoto Musashi"],
        "penseurs_occidentaux": ["Mandela", "Churchill", "Aristote"],
    },
    "humanite": {
        "citations": [
            "Dalaï-Lama : « L'amour et la compassion sont des nécessités, pas un luxe. Sans eux, l'humanité ne peut pas survivre. »",
            "Albert Schweitzer : « Le but de la vie humaine est de servir et de montrer de la compassion et la volonté d'aider les autres. »",
        ],
        "penseurs_orientaux": ["Dalaï-Lama", "Thich Nhat Hanh"],
        "penseurs_occidentaux": ["Schweitzer", "Levinas", "Mère Teresa"],
    },
    "temperance": {
        "citations": [
            "Épicure : « Rien n'est suffisant pour celui à qui le suffisant ne suffit pas. »",
            "Sénèque : « Ce n'est pas parce que les choses sont difficiles que nous n'osons pas, c'est parce que nous n'osons pas qu'elles sont difficiles. »",
        ],
        "penseurs_orientaux": ["Bouddha", "Lao Tseu"],
        "penseurs_occidentaux": ["Épicure", "Sénèque", "Marc Aurèle"],
    },
    "transcendance": {
        "citations": [
            "Victor Frankl : « Celui qui a un pourquoi qui lui tient lieu de vivre peut supporter tous les comment. »",
            "Rumi : « Ce que tu cherches te cherche aussi. »",
        ],
        "penseurs_orientaux": ["Rumi", "Khalil Gibran"],
        "penseurs_occidentaux": ["Frankl", "Pascal", "Kierkegaard"],
    },
}


def format_referentiel_for_prompt() -> str:
    """Formate le référentiel complet en texte structuré pour injection dans le prompt IA."""
    lines = [
        "=== RÉFÉRENTIEL SCIENTIFIQUE DES VERTUS (Seligman & Peterson, 2003) ===",
        "Tu DOIS utiliser ce référentiel pour identifier les vertus dominantes et associer les compétences.\n",
    ]
    for code, v in MATRICE_VERTUS.items():
        lines.append(f"### {v['nom'].upper()}")
        lines.append(f"Description : {v['description']}")
        lines.append(f"Forces de caractère : {', '.join(v['forces_caractere'])}")
        lines.append(f"Valeurs Schwartz : {', '.join(v['valeurs_schwartz'])}")
        lines.append(f"Qualités humaines : {', '.join(v['qualites_humaines'])}")
        lines.append(f"CPS (OMS) : {', '.join(v['competences_psychosociales_oms'])}")
        lines.append(f"Savoirs-être pro : {', '.join(v['savoirs_etre_professionnels'])}")
        lines.append(f"Compétences transférables : {', '.join(v['competences_transferables'])}")
        lines.append(f"Métiers associés : {', '.join(v['metiers_associes'])}")
        # Citation
        cit = CITATIONS_VERTUS.get(code, {}).get("citations", [])
        if cit:
            lines.append(f"Citation de référence : {cit[0]}")
        lines.append("")
    return "\n".join(lines)
