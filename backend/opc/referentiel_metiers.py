"""
OPC — Référentiel hiérarchique RE'ACTIF PRO
4 niveaux :
  1. Filière professionnelle (20)
  2. Secteur d'activité (≈ 90)
  3. Métier (avec mission)
  4. Capacités techniques + Savoirs-être + Capacités professionnelles + Qualités humaines

Source : grille fournie par ALT&ACT (Doc Filières/Secteurs/Métiers/Capacités).
"""

from typing import Optional
import re
import unicodedata


def slugify(s: str) -> str:
    """Métier → slug stable (sans accent, kebab-case)."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
    s = re.sub(r"[^\w\s-]", "", s).strip().lower()
    return re.sub(r"[-\s]+", "-", s)


# ─── Savoirs-être professionnels & Qualités humaines (Doc 4) ──────────────

SAVOIRS_ETRE = [
    "Résolution de problèmes", "Pensée critique", "Créativité", "Adaptabilité",
    "Collaboration", "Communication", "Gestion du temps", "Persévérance",
    "Orientation client", "Éthique professionnelle", "Leadership",
    "Curiosité", "Rigueur", "Esprit d'équipe", "Autonomie",
]

QUALITES_HUMAINES = {
    "Pensée critique": "Perspicacité — percevoir rapidement les aspects essentiels d'un problème.",
    "Créativité": "Capacité à penser de manière innovante et à proposer des idées nouvelles.",
    "Adaptabilité": "Flexibilité — s'adapter rapidement à des situations différentes.",
    "Communication": "Empathie — comprendre les perspectives des autres parties impliquées.",
    "Persévérance": "Courage et patience — résilience face aux obstacles.",
    "Curiosité": "Soif de comprendre les causes profondes des problèmes rencontrés.",
    "Rigueur": "Esprit analytique — analyser de manière critique les données et informations.",
    "Esprit d'équipe": "Collaboration — écouter et partager pour trouver des solutions conjointes.",
    "Autonomie": "Confiance en soi — résoudre les problèmes tout en restant ouvert aux suggestions.",
}


# ─── Référentiel par défaut (capacités génériques) ───────────────────────

CAPACITES_DEFAUT = {
    "techniques": [
        "Maîtrise des outils métiers (logiciels et équipements spécifiques au secteur)",
        "Connaissance des normes et réglementations applicables",
        "Capacité à diagnostiquer et résoudre des problèmes techniques",
        "Veille technologique et mise à jour continue des compétences",
    ],
    "savoirs_etre": ["Résolution de problèmes", "Rigueur", "Collaboration", "Adaptabilité"],
    "professionnelles": [
        "Analyser des situations complexes pour élaborer des solutions efficaces",
        "Travailler en équipe et communiquer clairement avec les parties prenantes",
        "Respecter les délais et les normes de qualité du métier",
    ],
}


# ─── Détails métiers spécifiques (Doc 2) ─────────────────────────────────
# Mappés par slug pour lookup rapide. Mission obligatoire, capacités optionnelles.

METIERS_DETAILS = {
    # ─── Mécanique ─────────────────────────────────────────────────────
    "ingenieur-en-mecanique": {
        "mission": "Responsable de la conception, du développement et de l'amélioration des produits et systèmes mécaniques.",
        "techniques": [
            "Maîtrise CAO (SolidWorks, CATIA, AutoCAD)",
            "Calcul et dimensionnement de pièces mécaniques (résistance, rigidité, durabilité)",
            "Analyse numérique (FEA, simulations dynamiques)",
            "Connaissance des matériaux (métaux, polymères, composites)",
            "Procédés de fabrication (usinage, soudure, injection plastique, impression 3D)",
        ],
        "savoirs_etre": ["Résolution de problèmes", "Pensée critique", "Créativité",
                         "Adaptabilité", "Collaboration", "Communication",
                         "Gestion du temps", "Leadership"],
    },
    "technicien-en-bureau-detudes": {"mission": "Collaborateur des ingénieurs, chargé de réaliser des plans et schémas techniques, ainsi que de participer à la conception des produits."},
    "technicien-de-maintenance-industrielle": {"mission": "Chargé de l'entretien préventif et curatif des équipements mécaniques dans les entreprises industrielles."},
    "operateur-sur-machines-outils": {"mission": "Responsable de la programmation, de l'installation et du fonctionnement des machines-outils pour la production de pièces mécaniques."},
    "monteur-assembleur": {"mission": "Chargé d'assembler les pièces mécaniques pour la fabrication de produits finis, en suivant les plans et instructions techniques."},
    "soudeur": {"mission": "Spécialisé dans l'assemblage de pièces métalliques par soudage (TIG, MIG/MAG, soudage à l'arc, par points)."},
    "technicien-en-qualite": {"mission": "Responsable de contrôler la conformité des produits mécaniques aux normes et spécifications techniques."},
    "chef-de-projet-industriel": {"mission": "Pilote les projets de développement de produits ou d'amélioration des processus de fabrication."},
    "regleur-sur-machines-de-production": {"mission": "Réalise le réglage et la mise en service des machines de production mécanique."},
    "ingenieur-en-robotique-industrielle": {"mission": "Conçoit et met en place des solutions robotiques pour automatiser les processus de fabrication."},
    "controleur-dimensionnel": {"mission": "Effectue des mesures précises sur les pièces mécaniques pour garantir leur conformité."},
    "expert-en-simulation-numerique": {"mission": "Utilise des logiciels de simulation pour modéliser et optimiser le comportement des produits et systèmes mécaniques."},

    # ─── Électrotechnique ──────────────────────────────────────────────
    "ingenieur-en-electrotechnique": {"mission": "Responsable de la conception, du développement et de la mise en œuvre de systèmes électriques et électroniques."},
    "technicien-en-electrotechnique": {"mission": "Assiste les ingénieurs dans la conception, la fabrication, l'installation et la maintenance des équipements électriques."},
    "technicien-de-maintenance-electrique-industrielle": {"mission": "Chargé de la maintenance préventive et corrective des équipements électriques en milieu industriel."},
    "electricien-industriel": {"mission": "Installe, câble et met en service les équipements électriques dans les installations industrielles."},
    "automaticien": {"mission": "Spécialisé dans la conception, la programmation et la maintenance des systèmes automatisés industriels."},
    "chef-de-chantier-electrotechnique": {"mission": "Supervise l'installation et la mise en service des équipements électriques sur les chantiers industriels."},
    "chef-de-projet-electrotechnique": {"mission": "Pilote les projets de conception et de réalisation d'installations électriques (délais, budgets)."},
    "electromecanicien": {"mission": "Intervient sur des équipements combinant composants électriques et mécaniques (maintenance, réparation)."},
    "technicien-en-automatismes-industriels": {"mission": "Spécialisé dans la programmation et la maintenance des systèmes automatisés et automates programmables."},
    "controleur-en-electricite": {"mission": "Effectue les tests et mesures pour vérifier la conformité des installations électriques aux normes."},
    "ingenieur-en-securite-electrique": {"mission": "Conçoit et met en place des mesures de sécurité pour prévenir les risques électriques sur les sites industriels."},
    "expert-en-energie-electrique": {"mission": "Analyse et optimise la gestion de l'énergie électrique dans les installations industrielles."},

    # ─── Automatisme ───────────────────────────────────────────────────
    "ingenieur-en-automatisme": {"mission": "Responsable de la conception, du développement et de l'optimisation des systèmes automatisés."},
    "technicien-en-automatisme-industriel": {"mission": "Chargé de la programmation, installation, mise en service et maintenance des équipements automatisés."},
    "programmeur-plc-automates-programmables": {"mission": "Spécialisé dans la programmation des automates programmables industriels (API) pour contrôler les processus de production."},
    "technicien-en-robotique-industrielle": {"mission": "Responsable de la programmation, installation et maintenance des robots industriels."},
    "superviseur-de-ligne-de-production-automatisee": {"mission": "Pilote et surveille les lignes de production automatisées pour garantir leur efficacité."},
    "technicien-en-instrumentation-et-controle": {"mission": "Installe et calibre les capteurs et instruments utilisés dans les systèmes automatisés."},
    "technicien-de-maintenance-en-automatisme": {"mission": "Réalise la maintenance préventive et corrective des équipements automatisés."},
    "expert-en-systemes-scada": {"mission": "Conçoit et configure les systèmes SCADA pour la supervision et le contrôle à distance des processus industriels."},
    "ingenieur-en-controle-commande": {"mission": "Spécialisé dans la conception et la mise en œuvre des systèmes de contrôle-commande industriels."},
    "technicien-en-electronique-industrielle": {"mission": "Assure la maintenance des composants électroniques (cartes, capteurs, actionneurs) dans les systèmes automatisés."},

    # ─── Génie Civil ───────────────────────────────────────────────────
    "ingenieur-en-genie-civil": {"mission": "Responsable de la conception, planification, coordination et supervision des projets de construction et d'infrastructures."},
    "conducteur-de-travaux": {"mission": "Supervise l'exécution des travaux sur chantier (équipes, délais, qualité)."},
    "chef-de-projet-en-genie-civil": {"mission": "Pilote les projets de construction, réhabilitation ou extension d'infrastructures de la conception à la livraison."},
    "technicien-en-genie-civil": {"mission": "Collabore aux études techniques, à la mise en œuvre des plans et à la surveillance des travaux."},
    "dessinateur-projeteur-en-genie-civil": {"mission": "Réalise les plans techniques et schémas de construction en utilisant des logiciels CAO."},
    "geometre-topographe": {"mission": "Effectue les relevés topographiques et établit les plans nécessaires aux projets de génie civil."},
    "chef-de-chantier": {"mission": "Organise et supervise les travaux sur chantier (équipes, suivi, normes de sécurité)."},
    "conducteur-dengins-de-chantier": {"mission": "Manipule les engins de terrassement, de levage et de transport sur les chantiers."},
    "expert-en-structures": {"mission": "Spécialisé dans le calcul et la conception des structures porteuses (ponts, bâtiments, ouvrages d'art)."},
    "inspecteur-en-genie-civil": {"mission": "Effectue les inspections régulières des ouvrages existants pour évaluer leur état."},
    "responsable-qhse": {"mission": "Garantit le respect des normes de qualité, sécurité et protection de l'environnement sur les chantiers."},
    "expert-en-genie-parasismique": {"mission": "Conçoit des ouvrages résistants aux séismes (études dynamiques, solutions de renforcement)."},

    # ─── Chimie ────────────────────────────────────────────────────────
    "ingenieur-chimiste": {"mission": "Responsable de la conception, développement et optimisation des procédés de fabrication des produits chimiques."},
    "technicien-de-laboratoire": {"mission": "Effectue les analyses chimiques pour contrôler la qualité des matières et produits finis."},
    "operateur-de-production-chimique": {"mission": "Pilote les installations de production et surveille les paramètres de fabrication."},
    "responsable-de-la-securite-chimique": {"mission": "Met en place et supervise les mesures de prévention des risques chimiques."},
    "technicien-en-controle-qualite": {"mission": "Effectue les contrôles sur matières premières et produits finis pour garantir la conformité."},
    "ingenieur-procedes": {"mission": "Analyse et optimise les procédés de production pour améliorer efficacité, rentabilité et sécurité."},
    "technicien-en-developpement-analytique": {"mission": "Participe à la mise au point des méthodes analytiques pour le contrôle qualité."},
    "responsable-environnement": {"mission": "Veille à la conformité réglementaire en matière d'environnement, gestion des déchets et impacts environnementaux."},
    "ingenieur-de-recherche-en-chimie": {"mission": "Développe de nouveaux produits, améliore des procédés existants ou résout des problèmes techniques."},
    "technicien-de-maintenance-en-chimie": {"mission": "Assure la maintenance préventive et corrective des équipements et installations chimiques."},
    "responsable-assurance-qualite": {"mission": "Met en place et supervise les systèmes d'assurance qualité (normes, exigences réglementaires)."},
    "expert-en-chimie-analytique": {"mission": "Utilise des techniques avancées pour caractériser les substances chimiques et étudier leurs propriétés."},

    # ─── Métallurgie ───────────────────────────────────────────────────
    "metallurgiste": {"mission": "Étudie les propriétés des métaux, développe alliages et processus de fabrication, supervise la production."},
    "operateur-de-machines-outils": {"mission": "Utilise tours, fraiseuses, perceuses pour façonner les métaux selon des spécifications précises."},
    "forgeur": {"mission": "Utilise des techniques de forgeage pour façonner les métaux en pièces utiles (outils, pièces automobiles)."},
    "fondeur": {"mission": "Prépare et fond les métaux dans des fours pour produire des pièces moulées."},
    "technicien-en-traitement-thermique": {"mission": "Contrôle les processus de chauffage/refroidissement pour améliorer les propriétés mécaniques des métaux."},
    "controleur-qualite": {"mission": "Effectue des inspections visuelles et dimensionnelles sur les produits métallurgiques."},
    "ingenieur-en-materiaux": {"mission": "Conçoit et développe des matériaux métalliques répondant aux besoins industriels et technologiques."},
    "operateur-de-controle-commande": {"mission": "Surveille et contrôle les processus de production via systèmes informatisés et automatisés dans les usines métallurgiques."},
    "soudeur-tig": {
        "mission": "Spécialisé dans le soudage TIG (Tungsten Inert Gas) sur métaux nobles (inox, aluminium, titane).",
        "techniques": ["Soudage TIG (acier, inox, aluminium)", "Lecture de plans techniques",
                       "Préparation des chanfreins", "Contrôle qualité visuel des soudures"],
        "savoirs_etre": ["Rigueur", "Persévérance", "Autonomie", "Adaptabilité"],
    },

    # ─── BTP (filière 2) ────────────────────────────────────────────────
    "macon": {"mission": "Réalise les ouvrages en maçonnerie : fondations, murs, dallages, ouvertures."},
    "chef-dequipe-maconnerie": {"mission": "Supervise une équipe de maçons sur chantier, organise le travail, contrôle la qualité."},
    "macon-coffreur": {"mission": "Spécialiste des coffrages bois ou métalliques pour le béton armé."},
    "menuisier": {"mission": "Fabrique et installe des éléments en bois (portes, fenêtres, escaliers, agencements)."},
    "plombier": {"mission": "Installe et entretient les canalisations d'eau et de gaz dans le bâtiment."},
    "plombier-chauffagiste": {"mission": "Installe systèmes de chauffage, sanitaires et plomberie ; assure la maintenance."},
    "electricien-du-batiment": {"mission": "Pose, raccorde et met en service les installations électriques basse tension du bâtiment."},
    "charpentier": {"mission": "Conçoit, fabrique et pose les charpentes bois et structures porteuses des bâtiments."},
    "conducteur-de-travaux-btp": {"mission": "Pilote les chantiers BTP : équipes, délais, budgets, sécurité."},
    "chef-de-chantier-btp": {"mission": "Encadre les ouvriers sur chantier, organise les travaux et veille au respect des plannings."},

    # ─── Santé & Social (filière 4) ─────────────────────────────────────
    "infirmier-de": {
        "mission": "Dispense les soins infirmiers prescrits, surveille l'état de santé des patients et accompagne les traitements.",
        "techniques": ["Pose de perfusion", "Pharmacologie", "Dossier patient informatisé",
                       "Gestes de premiers secours", "Coordination de parcours"],
        "savoirs_etre": ["Empathie", "Rigueur", "Communication", "Gestion du temps", "Persévérance"],
    },
    "infirmier-coordinateur": {"mission": "Coordonne les soins entre les différents intervenants et services médicaux."},
    "infirmier-coordinateur-telesurveillance": {
        "mission": "Coordonne la télésurveillance médicale : suivi à distance des patients chroniques via plateforme connectée.",
        "techniques": ["Plateformes de télésurveillance", "Dossier patient connecté",
                       "IA d'aide au diagnostic", "Coordination multidisciplinaire", "Pharmacologie"],
        "savoirs_etre": ["Empathie", "Rigueur", "Adaptabilité", "Communication"],
    },
    "infirmier-de-bloc-operatoire": {"mission": "Assiste le chirurgien au bloc opératoire ; gère stérilisation et instrumentation."},
    "aide-soignant": {"mission": "Accompagne les patients dans les soins d'hygiène, alimentation et confort."},
    "aide-soignant-en-geriatrie": {"mission": "Aide-soignant spécialisé dans l'accompagnement des personnes âgées en EHPAD."},
    "psychologue-clinicien": {"mission": "Évalue et accompagne les patients en souffrance psychique."},
    "assistant-de-service-social": {"mission": "Accompagne les personnes en difficulté sociale dans leurs démarches et leur insertion."},
    "conseiller-en-insertion-sociale": {
        "mission": "Accompagne les publics en difficulté vers l'emploi et l'autonomie sociale (RSA, jeunes décrocheurs, IAE).",
        "techniques": ["Écoute active", "Médiation sociale", "Connaissance des dispositifs RSA/RQTH/AAH",
                       "Insertion numérique", "Construction de parcours individualisés"],
        "savoirs_etre": ["Empathie", "Éthique professionnelle", "Communication", "Persévérance", "Adaptabilité"],
    },

    # ─── Informatique & Numérique (filière 8) ───────────────────────────
    "developpeur-full-stack-pythonreact": {
        "mission": "Conçoit et développe des applications web complètes (frontend React + backend Python) avec base de données et API REST.",
        "techniques": ["Python (FastAPI, Django, Flask)", "React / Next.js", "PostgreSQL / MongoDB",
                       "Git / GitHub Actions", "Docker", "LLM prompting & RAG", "TypeScript", "Cloud (GCP/AWS)"],
        "savoirs_etre": ["Autonomie", "Curiosité", "Rigueur", "Collaboration", "Communication", "Adaptabilité"],
    },
    "developpeur-web": {"mission": "Conçoit et code des sites et applications web (frontend, backend ou full-stack)."},
    "developpeur-mobile-ios": {"mission": "Développe des applications mobiles natives pour iOS (Swift, SwiftUI)."},
    "developpeur-mobile-android": {"mission": "Développe des applications mobiles natives pour Android (Kotlin, Jetpack Compose)."},
    "ingenieur-data-ia": {
        "mission": "Construit des pipelines de données et des modèles IA/ML pour exploiter la donnée d'entreprise.",
        "techniques": ["Python (Pandas, scikit-learn, PyTorch)", "SQL avancé", "MLOps (MLflow, Airflow)",
                       "LLM / RAG / LangChain", "Cloud (GCP BigQuery, AWS SageMaker)", "Spark / Databricks"],
        "savoirs_etre": ["Pensée critique", "Curiosité", "Rigueur", "Communication"],
    },
    "lead-developer": {"mission": "Anime une équipe de développeurs, garantit la qualité technique et la cohérence architecturale."},
    "administrateur-systemes": {"mission": "Installe, configure et maintient les serveurs et systèmes d'exploitation."},
    "administrateur-reseaux": {"mission": "Conçoit et administre les infrastructures réseau (LAN, WAN, sécurité périmétrique)."},
    "ingenieur-devops": {"mission": "Automatise les chaînes de déploiement et de monitoring entre dev et opérations."},
    "technicien-support-n2": {"mission": "Traite les incidents techniques niveau 2 (escalade depuis le N1), diagnostic et résolution."},
    "analyste-soc": {"mission": "Surveille en continu le SI pour détecter et traiter les incidents de cybersécurité."},
    "pentester": {"mission": "Réalise des tests d'intrusion pour identifier les vulnérabilités d'un SI."},
    "responsable-securite-si-rssi": {"mission": "Définit et pilote la stratégie de sécurité du SI de l'entreprise."},
    "consultant-cybersecurite": {"mission": "Conseille les entreprises sur leur sécurité informatique (audit, conformité, sensibilisation)."},

    # ─── Transport & Logistique (filière 9) ─────────────────────────────
    "cariste": {
        "mission": "Conduit les chariots élévateurs pour déplacer, charger et stocker les marchandises en entrepôt.",
        "techniques": ["CACES R489 (catégories 1, 3, 5)", "Lecture de bons de commande",
                       "WMS connecté", "Tablette PDA", "Sécurité entrepôt"],
        "savoirs_etre": ["Rigueur", "Autonomie", "Adaptabilité"],
    },
    "preparateur-de-commandes": {"mission": "Prépare les commandes en entrepôt : prélèvement, conditionnement, expédition."},
    "chauffeur-poids-lourd": {"mission": "Conduit les véhicules poids-lourds pour le transport routier de marchandises."},
    "chauffeur-spl": {"mission": "Conduit les ensembles articulés (camion + semi-remorque) sur longues distances."},
}


# ─── Hiérarchie complète : 20 Filières → Secteurs → Métiers ──────────────

FILIERES_REFERENTIEL = [
    {
        "key": "industrielle", "code": "SI", "label": "Filière Industrielle", "ordre": 1,
        "secteurs": [
            {"key": "mecanique", "label": "Mécanique", "metiers": [
                "Ingénieur en mécanique", "Technicien en bureau d'études",
                "Technicien de maintenance industrielle", "Opérateur sur machines-outils",
                "Monteur-assembleur", "Soudeur", "Technicien en qualité",
                "Chef de projet industriel", "Régleur sur machines de production",
                "Ingénieur en robotique industrielle", "Contrôleur dimensionnel",
                "Expert en simulation numérique",
            ]},
            {"key": "electrotechnique", "label": "Électrotechnique", "metiers": [
                "Ingénieur en électrotechnique", "Technicien en électrotechnique",
                "Technicien de maintenance électrique industrielle", "Électricien industriel",
                "Automaticien", "Chef de chantier électrotechnique",
                "Chef de projet électrotechnique", "Électromécanicien",
                "Technicien en automatismes industriels", "Contrôleur en électricité",
                "Ingénieur en sécurité électrique", "Expert en énergie électrique",
            ]},
            {"key": "automatisme", "label": "Automatisme", "metiers": [
                "Ingénieur en automatisme", "Technicien en automatisme industriel",
                "Programmeur PLC (automates programmables)",
                "Technicien en robotique industrielle",
                "Superviseur de ligne de production automatisée",
                "Technicien en instrumentation et contrôle",
                "Technicien de maintenance en automatisme",
                "Expert en systèmes SCADA", "Ingénieur en contrôle-commande",
                "Technicien en électronique industrielle",
            ]},
            {"key": "genie-civil-industriel", "label": "Génie civil", "metiers": [
                "Ingénieur en génie civil", "Conducteur de travaux",
                "Chef de projet en génie civil", "Technicien en génie civil",
                "Dessinateur-projeteur en génie civil", "Géomètre-topographe",
                "Chef de chantier", "Conducteur d'engins de chantier",
                "Expert en structures", "Inspecteur en génie civil",
                "Responsable QHSE", "Expert en génie parasismique",
            ]},
            {"key": "chimie", "label": "Chimie", "metiers": [
                "Ingénieur chimiste", "Technicien de laboratoire",
                "Opérateur de production chimique", "Responsable de la sécurité chimique",
                "Technicien en contrôle qualité", "Ingénieur procédés",
                "Technicien en développement analytique", "Responsable environnement",
                "Ingénieur de recherche en chimie", "Technicien de maintenance en chimie",
                "Responsable assurance qualité", "Expert en chimie analytique",
            ]},
            {"key": "metallurgie", "label": "Métallurgie", "metiers": [
                "Métallurgiste", "Opérateur de machines-outils", "Soudeur",
                "Soudeur TIG",
                "Forgeur", "Fondeur", "Technicien en traitement thermique",
                "Contrôleur qualité", "Ingénieur en matériaux",
                "Technicien de maintenance industrielle", "Opérateur de contrôle commande",
            ]},
        ],
    },
    {
        "key": "btp", "code": "SBTP", "label": "Filière Bâtiment et Travaux Publics (BTP)", "ordre": 2,
        "secteurs": [
            {"key": "maconnerie", "label": "Maçonnerie", "metiers": ["Maçon", "Chef d'équipe maçonnerie", "Maçon-coffreur"]},
            {"key": "menuiserie", "label": "Menuiserie", "metiers": ["Menuisier", "Menuisier-poseur", "Chef d'atelier menuiserie"]},
            {"key": "plomberie", "label": "Plomberie", "metiers": ["Plombier", "Plombier-chauffagiste", "Chef d'équipe plomberie"]},
            {"key": "electricite-batiment", "label": "Électricité du bâtiment", "metiers": ["Électricien du bâtiment", "Domoticien", "Tableautier"]},
            {"key": "charpenterie", "label": "Charpenterie", "metiers": ["Charpentier", "Charpentier-couvreur"]},
            {"key": "genie-civil-btp", "label": "Génie civil", "metiers": ["Conducteur de travaux BTP", "Chef de chantier BTP", "Géomètre-topographe"]},
        ],
    },
    {
        "key": "services-personne", "code": "SPSC", "label": "Filière Services à la Personne et à la Communauté", "ordre": 3,
        "secteurs": [
            {"key": "aide-domicile", "label": "Aide à domicile", "metiers": ["Auxiliaire de vie", "Aide à domicile", "Assistant de vie aux familles"]},
            {"key": "education-specialisee", "label": "Éducation spécialisée", "metiers": [
                "Éducateur spécialisé", "Moniteur-éducateur",
                "Conseiller en insertion sociale"
            ]},
            {"key": "animation-socio-culturelle", "label": "Animation socio-culturelle", "metiers": ["Animateur socio-culturel", "Coordinateur d'animation"]},
            {"key": "petite-enfance", "label": "Petite enfance", "metiers": ["Auxiliaire de puériculture", "Éducateur de jeunes enfants", "Assistant maternel"]},
            {"key": "accompagnement-ages", "label": "Accompagnement des personnes âgées", "metiers": ["Aide-soignant en EHPAD", "Auxiliaire de vie sociale", "Coordinateur gérontologie"]},
        ],
    },
    {
        "key": "sante-social", "code": "SSS", "label": "Filière Santé et Social", "ordre": 4,
        "secteurs": [
            {"key": "infirmier", "label": "Infirmier(e)", "metiers": [
                "Infirmier DE", "Infirmier coordinateur",
                "Infirmier coordinateur télésurveillance",
                "Infirmier de bloc opératoire"
            ]},
            {"key": "aide-soignant", "label": "Aide-soignant(e)", "metiers": ["Aide-soignant", "Aide-soignant en gériatrie"]},
            {"key": "assistant-service-social", "label": "Assistant(e) de service social", "metiers": ["Assistant de service social", "Conseiller en économie sociale et familiale"]},
            {"key": "educateur-specialise", "label": "Éducateur(trice) spécialisé(e)", "metiers": ["Éducateur spécialisé", "Éducateur technique spécialisé"]},
            {"key": "psychologue", "label": "Psychologue", "metiers": ["Psychologue clinicien", "Psychologue du travail", "Neuropsychologue"]},
        ],
    },
    {
        "key": "commerce-vente", "code": "SCV", "label": "Filière Commerce et Vente", "ordre": 5,
        "secteurs": [
            {"key": "vente-magasin", "label": "Vente en magasin", "metiers": ["Vendeur", "Chef de rayon", "Responsable de magasin"]},
            {"key": "commerce-international", "label": "Commerce international", "metiers": ["Responsable export", "Chargé de zone export", "Acheteur international"]},
            {"key": "negociation-commerciale", "label": "Négociation commerciale", "metiers": ["Commercial terrain", "Ingénieur d'affaires", "Key Account Manager"]},
            {"key": "marketing", "label": "Marketing", "metiers": ["Chef de produit", "Chargé d'études marketing", "Responsable marketing digital", "Brand Manager"]},
        ],
    },
    {
        "key": "hotellerie-restauration", "code": "SHR", "label": "Filière Hôtellerie-Restauration", "ordre": 6,
        "secteurs": [
            {"key": "cuisine", "label": "Cuisine", "metiers": ["Chef de cuisine", "Cuisinier", "Commis de cuisine", "Pâtissier"]},
            {"key": "service-salle", "label": "Service en salle", "metiers": ["Maître d'hôtel", "Serveur", "Chef de rang", "Sommelier"]},
            {"key": "hebergement", "label": "Hébergement", "metiers": ["Réceptionniste", "Gouvernant(e)", "Concierge"]},
            {"key": "gestion-hoteliere", "label": "Gestion hôtelière", "metiers": ["Directeur d'hôtel", "Responsable hébergement", "Revenue Manager"]},
        ],
    },
    {
        "key": "agriculture-agroalimentaire", "code": "SAA", "label": "Filière Agriculture et Agroalimentaire", "ordre": 7,
        "secteurs": [
            {"key": "production-agricole", "label": "Production agricole", "metiers": ["Chef d'exploitation agricole", "Ouvrier agricole", "Maraîcher"]},
            {"key": "transformation-agricole", "label": "Transformation des produits agricoles", "metiers": ["Opérateur agroalimentaire", "Technicien qualité agroalimentaire", "Responsable de production agroalimentaire"]},
            {"key": "agroequipement", "label": "Agroéquipement", "metiers": ["Mécanicien agricole", "Technicien agroéquipement"]},
            {"key": "viticulture", "label": "Viticulture", "metiers": ["Viticulteur", "Œnologue", "Caviste"]},
        ],
    },
    {
        "key": "informatique-numerique", "code": "SIN", "label": "Filière Informatique et Numérique", "ordre": 8,
        "secteurs": [
            {"key": "dev-web-mobile", "label": "Développement web et mobile", "metiers": [
                "Développeur Full-Stack Python/React",
                "Développeur web", "Développeur mobile iOS", "Développeur mobile Android",
                "Ingénieur data IA", "Lead developer",
            ]},
            {"key": "admin-sys-reseaux", "label": "Administration systèmes et réseaux", "metiers": [
                "Administrateur systèmes", "Administrateur réseaux", "Ingénieur DevOps",
                "Technicien support N2",
            ]},
            {"key": "cybersecurite", "label": "Cybersécurité", "metiers": [
                "Analyste SOC", "Pentester", "Responsable sécurité SI (RSSI)", "Consultant cybersécurité",
            ]},
            {"key": "design-numerique", "label": "Design numérique", "metiers": [
                "UI/UX Designer", "Product Designer", "Motion designer",
            ]},
        ],
    },
    {
        "key": "transport-logistique", "code": "STL", "label": "Filière Transport et Logistique", "ordre": 9,
        "secteurs": [
            {"key": "conduite-routiere", "label": "Conduite routière", "metiers": ["Chauffeur poids lourd", "Chauffeur SPL", "Chauffeur livreur"]},
            {"key": "logistique-transports", "label": "Logistique et gestion des transports", "metiers": ["Responsable logistique", "Affréteur", "Exploitant transport"]},
            {"key": "manutention", "label": "Manutention", "metiers": ["Cariste", "Préparateur de commandes", "Magasinier"]},
        ],
    },
    {
        "key": "artisanat-art", "code": "SAAT", "label": "Filière Artisanat d'Art", "ordre": 10,
        "secteurs": [
            {"key": "ebenisterie", "label": "Ébénisterie", "metiers": ["Ébéniste", "Marqueteur"]},
            {"key": "poterie", "label": "Poterie", "metiers": ["Potier", "Céramiste"]},
            {"key": "ferronnerie", "label": "Ferronnerie", "metiers": ["Ferronnier d'art", "Forgeron"]},
            {"key": "joaillerie", "label": "Joaillerie", "metiers": ["Joaillier", "Bijoutier", "Sertisseur"]},
        ],
    },
    {
        "key": "communication-medias", "code": "SCM", "label": "Filière Communication et Médias", "ordre": 11,
        "secteurs": [
            {"key": "journalisme", "label": "Journalisme", "metiers": ["Journaliste", "Reporter", "Rédacteur en chef"]},
            {"key": "communication-entreprise", "label": "Communication d'entreprise", "metiers": ["Chargé de communication", "Responsable communication interne", "Community manager"]},
            {"key": "relations-publiques", "label": "Relations publiques", "metiers": ["Attaché de presse", "Chargé de relations publiques"]},
            {"key": "audiovisuel", "label": "Audiovisuel et production multimédia", "metiers": ["Cadreur", "Monteur vidéo", "Ingénieur du son", "Réalisateur"]},
        ],
    },
    {
        "key": "environnement", "code": "SEDD", "label": "Filière Environnement et Développement Durable", "ordre": 12,
        "secteurs": [
            {"key": "gestion-dechets", "label": "Gestion des déchets", "metiers": ["Technicien valorisation des déchets", "Responsable centre de tri"]},
            {"key": "energies-renouvelables", "label": "Énergies renouvelables", "metiers": ["Technicien photovoltaïque", "Technicien éolien", "Ingénieur énergies renouvelables"]},
            {"key": "gestion-eau", "label": "Gestion de l'eau et de l'assainissement", "metiers": ["Technicien assainissement", "Ingénieur eau et environnement"]},
            {"key": "eco-conception", "label": "Éco-conception et gestion environnementale", "metiers": ["Éco-concepteur", "Consultant RSE", "Auditeur environnemental"]},
        ],
    },
    {
        "key": "metiers-art", "code": "SMA", "label": "Filière Métiers d'Art", "ordre": 13,
        "secteurs": [
            {"key": "restauration-oeuvres", "label": "Restauration d'œuvres d'art", "metiers": ["Restaurateur d'œuvres d'art", "Doreur"]},
            {"key": "dorure", "label": "Dorure et restauration de mobilier", "metiers": ["Doreur sur bois", "Restaurateur de mobilier"]},
            {"key": "tapisserie", "label": "Tapisserie", "metiers": ["Tapissier d'ameublement", "Tapissier décorateur"]},
            {"key": "maroquinerie", "label": "Maroquinerie", "metiers": ["Maroquinier", "Sellier", "Coupeur en maroquinerie"]},
        ],
    },
    {
        "key": "tourisme", "code": "STO", "label": "Filière Tourisme", "ordre": 14,
        "secteurs": [
            {"key": "accueil-touristique", "label": "Accueil touristique", "metiers": ["Agent d'accueil touristique", "Conseiller en séjour"]},
            {"key": "guide-touristique", "label": "Guide touristique", "metiers": ["Guide-conférencier", "Guide accompagnateur"]},
            {"key": "gestion-hoteliere-tourisme", "label": "Gestion hôtelière", "metiers": ["Responsable établissement touristique", "Gestionnaire d'hébergement"]},
            {"key": "animation-promotion-tourisme", "label": "Animation et promotion touristique", "metiers": ["Animateur tourisme", "Chargé de promotion touristique"]},
        ],
    },
    {
        "key": "sport-loisirs", "code": "SSL", "label": "Filière Sport et Loisirs", "ordre": 15,
        "secteurs": [
            {"key": "entrainement-sportif", "label": "Entraînement sportif", "metiers": ["Entraîneur sportif", "Préparateur physique", "Coach sportif"]},
            {"key": "animation-sportive", "label": "Animation sportive et socio-culturelle", "metiers": ["Animateur sportif", "Éducateur sportif"]},
            {"key": "gestion-infrastructures-sport", "label": "Gestion d'infrastructures sportives", "metiers": ["Directeur de complexe sportif", "Responsable d'équipement"]},
            {"key": "evenementiel-sportif", "label": "Événementiel sportif", "metiers": ["Chargé d'événementiel sportif", "Coordinateur d'événements"]},
        ],
    },
    {
        "key": "gestion-administration", "code": "SGAE", "label": "Filière Gestion et Administration des Entreprises", "ordre": 16,
        "secteurs": [
            {"key": "comptabilite-finance", "label": "Gestion comptable et financière", "metiers": ["Comptable", "Contrôleur de gestion", "Directeur administratif et financier"]},
            {"key": "rh", "label": "Ressources humaines", "metiers": ["Chargé RH", "Responsable RH", "Gestionnaire de paie", "Recruteur"]},
            {"key": "gestion-administrative", "label": "Gestion administrative", "metiers": ["Assistant de direction", "Office Manager", "Secrétaire administratif"]},
            {"key": "audit-controle", "label": "Audit et contrôle de gestion", "metiers": ["Auditeur interne", "Auditeur externe", "Contrôleur interne"]},
        ],
    },
    {
        "key": "securite-defense", "code": "SSD", "label": "Filière Sécurité et Défense", "ordre": 17,
        "secteurs": [
            {"key": "securite-privee", "label": "Sécurité privée", "metiers": ["Agent de sécurité", "Maître-chien", "Responsable sécurité"]},
            {"key": "securite-publique", "label": "Sécurité publique", "metiers": ["Policier", "Gendarme", "Sapeur-pompier"]},
            {"key": "surete-aeroportuaire", "label": "Sûreté aéroportuaire", "metiers": ["Agent de sûreté aéroportuaire", "Coordinateur sûreté"]},
            {"key": "forces-armees", "label": "Forces armées", "metiers": ["Militaire du rang", "Sous-officier", "Officier"]},
        ],
    },
    {
        "key": "mode-textile", "code": "SMT", "label": "Filière Mode et Textile", "ordre": 18,
        "secteurs": [
            {"key": "stylisme", "label": "Stylisme", "metiers": ["Styliste", "Designer de mode"]},
            {"key": "modelisme", "label": "Modélisme", "metiers": ["Modéliste", "Patronnier"]},
            {"key": "couture", "label": "Couture", "metiers": ["Couturier", "Mécanicien en confection"]},
            {"key": "design-textile", "label": "Design textile", "metiers": ["Designer textile", "Coloriste textile"]},
        ],
    },
    {
        "key": "education-formation", "code": "SEF", "label": "Filière Éducation et Formation", "ordre": 19,
        "secteurs": [
            {"key": "enseignement", "label": "Enseignement primaire et secondaire", "metiers": ["Professeur des écoles", "Professeur du secondaire", "CPE"]},
            {"key": "formation-pro", "label": "Formation professionnelle", "metiers": ["Formateur en alternance", "Coordinateur pédagogique"]},
            {"key": "formation-adultes", "label": "Formation pour adultes", "metiers": ["Formateur d'adultes", "Conseiller en formation continue"]},
            {"key": "pedagogie-specialisee", "label": "Pédagogie spécialisée", "metiers": ["Enseignant spécialisé", "Éducateur en pédagogie spécialisée"]},
        ],
    },
    {
        "key": "design-arts-appliques", "code": "SDAA", "label": "Filière Design et Arts Appliqués", "ordre": 20,
        "secteurs": [
            {"key": "design-industriel", "label": "Design industriel", "metiers": ["Designer industriel", "Designer produit"]},
            {"key": "design-graphique", "label": "Design graphique", "metiers": ["Graphiste", "Directeur artistique", "Webdesigner"]},
            {"key": "design-mode", "label": "Design de mode", "metiers": ["Designer de mode", "Directeur artistique mode"]},
            {"key": "design-interieur", "label": "Design d'intérieur", "metiers": ["Architecte d'intérieur", "Designer d'espace"]},
        ],
    },
]


# ─── API pratique ─────────────────────────────────────────────────────────

def all_filieres() -> list:
    """Hiérarchie complète avec slugs calculés."""
    out = []
    for f in FILIERES_REFERENTIEL:
        secteurs = []
        for s in f["secteurs"]:
            metiers = []
            for label in s["metiers"]:
                slug = slugify(label)
                detail = METIERS_DETAILS.get(slug, {})
                metiers.append({
                    "label": label,
                    "slug": slug,
                    "mission": detail.get("mission"),
                    "has_details": slug in METIERS_DETAILS,
                })
            secteurs.append({
                "key": s["key"],
                "label": s["label"],
                "metiers": metiers,
                "nb_metiers": len(metiers),
            })
        out.append({
            "key": f["key"],
            "code": f["code"],
            "label": f["label"],
            "ordre": f["ordre"],
            "secteurs": secteurs,
            "nb_metiers": sum(len(s["metiers"]) for s in f["secteurs"]),
        })
    return out


def find_metier(slug: str) -> Optional[dict]:
    """Cherche un métier par slug ; retourne filière + secteur + détails."""
    for f in FILIERES_REFERENTIEL:
        for s in f["secteurs"]:
            for label in s["metiers"]:
                if slugify(label) == slug:
                    detail = METIERS_DETAILS.get(slug, {})
                    return {
                        "label": label,
                        "slug": slug,
                        "filiere": {"key": f["key"], "code": f["code"], "label": f["label"]},
                        "secteur": {"key": s["key"], "label": s["label"]},
                        "mission": detail.get("mission"),
                        "capacites_techniques": detail.get("techniques", CAPACITES_DEFAUT["techniques"]),
                        "savoirs_etre": detail.get("savoirs_etre", CAPACITES_DEFAUT["savoirs_etre"]),
                        "capacites_professionnelles": detail.get("professionnelles",
                                                                 CAPACITES_DEFAUT["professionnelles"]),
                        "qualites_humaines": {
                            se: QUALITES_HUMAINES.get(se)
                            for se in detail.get("savoirs_etre", CAPACITES_DEFAUT["savoirs_etre"])
                            if QUALITES_HUMAINES.get(se)
                        },
                    }
    return None


def find_metier_by_label(label: str) -> Optional[dict]:
    return find_metier(slugify(label))


# ─── Mapping ROME (métier slug → code ROME) ───────────────────────────────

ROME_MAP = {
    # Informatique & Numérique
    "developpeur-full-stack-pythonreact": "M1805",
    "developpeur-web": "M1805",
    "developpeur-mobile-ios": "M1805",
    "developpeur-mobile-android": "M1805",
    "ingenieur-data-ia": "M1805",
    "lead-developer": "M1805",
    "administrateur-systemes": "M1810",
    "administrateur-reseaux": "M1810",
    "ingenieur-devops": "M1810",
    "technicien-support-n2": "M1802",
    "analyste-soc": "M1802",
    "pentester": "M1802",
    "responsable-securite-si-rssi": "M1802",
    "consultant-cybersecurite": "M1802",

    # Industrielle - Mécanique
    "ingenieur-en-mecanique": "H1206",
    "technicien-de-maintenance-industrielle": "I1304",
    "operateur-sur-machines-outils": "H2903",
    "soudeur": "H2913",
    "soudeur-tig": "H2604",

    # Industrielle - Métallurgie
    "metallurgiste": "H1503",
    "forgeur": "H2911",
    "fondeur": "H2901",
    "technicien-en-traitement-thermique": "H2503",

    # Santé & Social
    "infirmier-de": "J1506",
    "infirmier-coordinateur": "J1506",
    "infirmier-coordinateur-telesurveillance": "J1506",
    "infirmier-de-bloc-operatoire": "J1502",
    "aide-soignant": "J1501",
    "aide-soignant-en-geriatrie": "J1501",
    "psychologue-clinicien": "K1104",
    "assistant-de-service-social": "K1201",
    "conseiller-en-insertion-sociale": "K1302",

    # Transport & Logistique
    "cariste": "N1101",
    "preparateur-de-commandes": "N1103",
    "chauffeur-poids-lourd": "N4101",
    "chauffeur-spl": "N4101",

    # BTP
    "macon": "F1703",
    "macon-coffreur": "F1701",
    "menuisier": "F1607",
    "plombier": "F1603",
    "plombier-chauffagiste": "F1603",
    "electricien-du-batiment": "F1602",
    "charpentier": "F1503",
    "conducteur-de-travaux-btp": "F1201",
    "chef-de-chantier-btp": "F1202",
}


def code_rome_for_slug(slug: str) -> Optional[str]:
    """Renvoie le code ROME associé à un métier (slug)."""
    return ROME_MAP.get(slug)


def code_rome_for_label(label: str) -> Optional[str]:
    return ROME_MAP.get(slugify(label))


# ─── Recherche full-text ──────────────────────────────────────────────────

def search_metiers(query: str, limit: int = 20) -> list:
    """Recherche full-text simple sur tous les métiers (label + mission)."""
    if not query or len(query) < 2:
        return []
    q = query.lower().strip()
    results = []
    for f in FILIERES_REFERENTIEL:
        for s in f["secteurs"]:
            for label in s["metiers"]:
                slug = slugify(label)
                detail = METIERS_DETAILS.get(slug, {})
                mission = (detail.get("mission") or "").lower()
                label_lc = label.lower()
                score = 0
                if q in label_lc:
                    score += 10 if label_lc.startswith(q) else 5
                if q in mission:
                    score += 2
                if score > 0:
                    results.append({
                        "label": label,
                        "slug": slug,
                        "filiere": {"key": f["key"], "code": f["code"], "label": f["label"]},
                        "secteur": {"key": s["key"], "label": s["label"]},
                        "mission": detail.get("mission"),
                        "code_rome": ROME_MAP.get(slug),
                        "score": score,
                    })
    results.sort(key=lambda x: -x["score"])
    return results[:limit]
