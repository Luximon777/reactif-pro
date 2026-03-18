DOCUMENT_CATEGORIES = {
    "identite_professionnelle": {
        "label": "Identité professionnelle",
        "types": ["CV", "CV ciblé", "Lettre de motivation", "Présentation professionnelle", "Projet professionnel", "Portfolio", "Bilan de compétences"]
    },
    "diplomes_certifications": {
        "label": "Diplômes et certifications",
        "types": ["Diplôme", "Titre professionnel", "Certificat", "Attestation de formation", "Habilitation", "Certification", "Permis", "CACES", "SST"]
    },
    "experiences_professionnelles": {
        "label": "Expériences professionnelles",
        "types": ["Contrat de travail", "Certificat de travail", "Attestation employeur", "Fiche de poste", "Évaluation annuelle", "Lettre de recommandation", "Attestation de mission"]
    },
    "competences_preuves": {
        "label": "Compétences et preuves",
        "types": ["Réalisation professionnelle", "Rapport", "Support créé", "Projet réalisé", "Badge de compétence", "Auto-évaluation", "Production écrite"]
    },
    "accompagnement_insertion": {
        "label": "Accompagnement et insertion",
        "types": ["Compte rendu d'entretien", "Diagnostic", "Synthèse de parcours", "Objectifs personnalisés", "Plan d'action", "Prescription", "Bilan"]
    },
    "recherche_emploi": {
        "label": "Recherche d'emploi",
        "types": ["Candidature", "Réponse employeur", "Convocation entretien", "Compte rendu entretien", "Offre sauvegardée", "Simulation entretien"]
    },
    "formation_apprentissages": {
        "label": "Formation et apprentissages",
        "types": ["Attestation de participation", "Certificat de module", "Résultat de quiz", "Badge interne", "Validation de parcours", "Exercice réalisé"]
    },
    "documents_administratifs": {
        "label": "Documents administratifs",
        "types": ["Permis de conduire", "Justificatif de mobilité", "Carte professionnelle", "Convention de stage", "Contrat d'alternance", "Autre document"]
    }
}

REFERENTIEL_VERTUS = [
    {
        "id": "sagesse", "name": "Sagesse et Connaissance",
        "description": "Forces cognitives qui favorisent l'acquisition et l'usage de la connaissance.",
        "forces": ["Créativité", "Curiosité", "Jugement", "Amour de l'apprentissage", "Perspective"],
        "valeurs": ["autonomie", "stimulation", "realisation_de_soi"],
        "qualites": ["Patience", "Ouverture d'esprit", "Indulgence", "Adaptabilité", "Curiosité"],
        "savoirs_etre": ["Faire preuve de curiosité", "Faire preuve de créativité", "Prendre des initiatives"],
    },
    {
        "id": "courage", "name": "Courage",
        "description": "Forces émotionnelles impliquant l'exercice de la volonté malgré les obstacles.",
        "forces": ["Bravoure", "Persévérance", "Honnêteté", "Enthousiasme"],
        "valeurs": ["securite", "pouvoir", "realisation_de_soi"],
        "qualites": ["Bravoure", "Fiabilité", "Confiance", "Loyauté", "Persévérance", "Détermination"],
        "savoirs_etre": ["Faire preuve de persévérance", "Gérer son stress", "Faire preuve de réactivité"],
    },
    {
        "id": "humanite", "name": "Humanité",
        "description": "Forces interpersonnelles consistant à tendre vers les autres et leur venir en aide.",
        "forces": ["Amour", "Gentillesse", "Intelligence sociale"],
        "valeurs": ["bienveillance", "universalisme"],
        "qualites": ["Empathie", "Gentillesse", "Générosité", "Altruisme", "Compassion", "Humilité"],
        "savoirs_etre": ["Être à l'écoute", "Avoir le sens du service", "Travailler en équipe"],
    },
    {
        "id": "justice", "name": "Justice",
        "description": "Forces qui sont à la base d'une vie sociale harmonieuse.",
        "forces": ["Travail d'équipe", "Équité", "Leadership"],
        "valeurs": ["conformite", "tradition", "bienveillance"],
        "qualites": ["Honnêteté", "Équité", "Coopération", "Leadership", "Intégrité"],
        "savoirs_etre": ["Faire preuve de leadership", "Inspirer et donner du sens", "Respecter ses engagements"],
    },
    {
        "id": "temperance", "name": "Tempérance",
        "description": "Forces qui protègent contre les excès.",
        "forces": ["Pardon", "Humilité", "Prudence", "Maîtrise de soi"],
        "valeurs": ["conformite", "securite", "tradition"],
        "qualites": ["Modestie", "Sobriété", "Prudence", "Rigueur", "Maîtrise de soi"],
        "savoirs_etre": ["Faire preuve de rigueur et de précision", "Organiser son travail selon les priorités"],
    },
    {
        "id": "transcendance", "name": "Transcendance",
        "description": "Forces qui favorisent l'ouverture à une dimension universelle et donnent un sens à la vie.",
        "forces": ["Appréciation de la beauté", "Gratitude", "Espoir", "Humour", "Spiritualité"],
        "valeurs": ["universalisme", "bienveillance", "autonomie"],
        "qualites": ["Gratitude", "Optimisme", "Tolérance", "Bienveillance", "Sensibilité"],
        "savoirs_etre": ["S'adapter aux changements", "Faire preuve d'autonomie"],
    },
]

REFERENTIEL_VALEURS = [
    {"id": "autonomie", "name": "Autonomie", "description": "Pensée et action indépendantes", "vertus": ["sagesse"]},
    {"id": "stimulation", "name": "Stimulation", "description": "Nouveauté et défis", "vertus": ["sagesse"]},
    {"id": "hedonisme", "name": "Hédonisme", "description": "Plaisir et gratification", "vertus": ["courage"]},
    {"id": "realisation_de_soi", "name": "Réalisation de soi", "description": "Ambition et succès", "vertus": ["sagesse", "courage"]},
    {"id": "pouvoir", "name": "Pouvoir", "description": "Leadership et influence", "vertus": ["justice", "courage"]},
    {"id": "securite", "name": "Sécurité", "description": "Stabilité et harmonie", "vertus": ["temperance", "courage"]},
    {"id": "conformite", "name": "Conformité", "description": "Respect des normes", "vertus": ["temperance", "justice"]},
    {"id": "tradition", "name": "Tradition", "description": "Modération et humilité", "vertus": ["temperance", "justice"]},
    {"id": "bienveillance", "name": "Bienveillance", "description": "Soin et altruisme", "vertus": ["humanite", "transcendance"]},
    {"id": "universalisme", "name": "Universalisme", "description": "Compréhension et tolérance", "vertus": ["humanite", "transcendance"]},
    {"id": "affiliation", "name": "Affiliation", "description": "Relations proches", "vertus": ["humanite"]},
]

REFERENTIEL_FILIERES = [
    {"id": "SI", "name": "Filière Industrielle", "secteurs": ["Mécanique", "Électrotechnique", "Automatisme", "Génie civil", "Chimie", "Métallurgie"]},
    {"id": "SBTP", "name": "Filière Bâtiment et Travaux Publics", "secteurs": ["Maçonnerie", "Menuiserie", "Plomberie", "Électricité du bâtiment", "Charpenterie"]},
    {"id": "SPSC", "name": "Filière Services à la Personne", "secteurs": ["Aide à domicile", "Éducation spécialisée", "Animation socio-culturelle", "Petite enfance"]},
    {"id": "SSS", "name": "Filière Santé et Social", "secteurs": ["Infirmier(e)", "Aide-soignant(e)", "Assistant(e) social", "Psychologue"]},
    {"id": "SCV", "name": "Filière Commerce et Vente", "secteurs": ["Vente en magasin", "Commerce international", "Négociation commerciale", "Marketing"]},
    {"id": "SHR", "name": "Filière Hôtellerie-Restauration", "secteurs": ["Cuisine", "Service en salle", "Hébergement", "Gestion hôtelière"]},
    {"id": "SAA", "name": "Filière Agriculture et Agroalimentaire", "secteurs": ["Production agricole", "Transformation des produits", "Agroéquipement"]},
    {"id": "SIN", "name": "Filière Informatique et Numérique", "secteurs": ["Développement web et mobile", "Administration systèmes et réseaux", "Cybersécurité", "Design numérique"]},
    {"id": "STL", "name": "Filière Transport et Logistique", "secteurs": ["Conduite routière", "Logistique et gestion", "Manutention"]},
    {"id": "SAAT", "name": "Filière Artisanat d'Art", "secteurs": ["Ébénisterie", "Poterie", "Ferronnerie", "Joaillerie"]},
    {"id": "SCM", "name": "Filière Communication et Médias", "secteurs": ["Journalisme", "Communication d'entreprise", "Relations publiques", "Audiovisuel"]},
    {"id": "SEDD", "name": "Filière Environnement et Développement Durable", "secteurs": ["Gestion des déchets", "Énergies renouvelables", "Éco-conception"]},
    {"id": "ST", "name": "Filière Tourisme", "secteurs": ["Accueil touristique", "Guide touristique", "Animation touristique"]},
    {"id": "SSL", "name": "Filière Sport et Loisirs", "secteurs": ["Entraînement sportif", "Animation sportive", "Gestion d'infrastructures"]},
]

ARCHEOLOGIE_SAVOIR_ETRE = {
    "Résolution de problèmes": {"qualites": ["Perspicacité", "Créativité", "Flexibilité"], "valeurs": ["autonomie", "stimulation"], "vertus": ["sagesse"]},
    "Pensée critique": {"qualites": ["Perspicacité", "Esprit analytique"], "valeurs": ["autonomie"], "vertus": ["sagesse"]},
    "Créativité": {"qualites": ["Créativité", "Audace", "Intuition"], "valeurs": ["autonomie", "stimulation"], "vertus": ["sagesse"]},
    "Adaptabilité": {"qualites": ["Flexibilité", "Ouverture d'esprit"], "valeurs": ["stimulation", "autonomie"], "vertus": ["sagesse"]},
    "Communication": {"qualites": ["Empathie", "Éloquence", "Écoute"], "valeurs": ["bienveillance", "affiliation"], "vertus": ["humanite"]},
    "Gestion du temps": {"qualites": ["Rigueur", "Organisation"], "valeurs": ["conformite", "securite"], "vertus": ["temperance"]},
    "Persévérance": {"qualites": ["Courage", "Patience", "Détermination"], "valeurs": ["realisation_de_soi", "securite"], "vertus": ["courage"]},
    "Leadership": {"qualites": ["Charisme", "Confiance en soi", "Intégrité"], "valeurs": ["pouvoir", "realisation_de_soi"], "vertus": ["justice"]},
    "Curiosité": {"qualites": ["Curiosité", "Ouverture d'esprit"], "valeurs": ["stimulation", "autonomie"], "vertus": ["sagesse"]},
    "Rigueur": {"qualites": ["Esprit analytique", "Précision", "Discipline"], "valeurs": ["conformite", "securite"], "vertus": ["temperance"]},
    "Esprit d'équipe": {"qualites": ["Collaboration", "Solidarité", "Écoute"], "valeurs": ["bienveillance", "affiliation"], "vertus": ["humanite", "justice"]},
    "Autonomie": {"qualites": ["Confiance en soi", "Initiative", "Indépendance"], "valeurs": ["autonomie", "realisation_de_soi"], "vertus": ["sagesse", "courage"]},
    "Collaboration": {"qualites": ["Coopération", "Empathie", "Partage"], "valeurs": ["bienveillance", "universalisme"], "vertus": ["humanite"]},
    "Écoute": {"qualites": ["Empathie", "Patience", "Bienveillance"], "valeurs": ["bienveillance", "affiliation"], "vertus": ["humanite"]},
    "Gestion du stress": {"qualites": ["Résilience", "Calme", "Maîtrise de soi"], "valeurs": ["securite"], "vertus": ["courage", "temperance"]},
    "Orientation client": {"qualites": ["Empathie", "Serviabilité", "Écoute"], "valeurs": ["bienveillance"], "vertus": ["humanite"]},
    "Éthique professionnelle": {"qualites": ["Intégrité", "Honnêteté", "Responsabilité"], "valeurs": ["conformite", "universalisme"], "vertus": ["justice"]},
    "Sens du service": {"qualites": ["Serviabilité", "Altruisme", "Générosité"], "valeurs": ["bienveillance", "universalisme"], "vertus": ["humanite", "transcendance"]},
}
