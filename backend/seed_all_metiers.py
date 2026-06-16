"""
Seed complet : Métiers pour les 19 filières manquantes (hors SI déjà peuplée)
Chaque secteur contient 8-12 métiers avec missions, savoir-faire, savoir-être et capacités
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

# ============== MÉTIERS PAR FILIÈRE/SECTEUR ==============
METIERS_DATA = {
    "SBTP": {
        "Maçonnerie": [
            ("Maçon", "Réalise les fondations, murs et structures en briques, parpaings ou pierres", ["Lecture de plans", "Maçonnerie traditionnelle", "Coffrage", "Enduits"], ["Précision", "Endurance physique", "Esprit d'équipe"]),
            ("Chef de chantier maçonnerie", "Coordonne les équipes et supervise l'avancement des travaux de maçonnerie", ["Gestion d'équipe", "Planification chantier", "Contrôle qualité", "Sécurité chantier"], ["Leadership", "Organisation", "Communication"]),
            ("Coffreur-bancheur", "Réalise des moules (coffrages) pour couler le béton armé", ["Coffrage bois et métal", "Lecture de plans", "Ferraillage", "Coulage béton"], ["Précision", "Rigueur", "Travail en hauteur"]),
            ("Tailleur de pierre", "Taille et sculpte la pierre pour la construction ou la restauration", ["Taille de pierre", "Sculpture", "Restauration patrimoine"], ["Minutie", "Créativité", "Patience"]),
            ("Façadier", "Réalise les enduits et revêtements de façade", ["Application d'enduits", "Isolation thermique extérieure", "Ravalement"], ["Sens esthétique", "Précision", "Autonomie"]),
            ("Constructeur en béton armé", "Réalise les structures en béton armé des bâtiments", ["Ferraillage", "Coffrage", "Coulage béton", "Lecture de plans"], ["Rigueur", "Force physique", "Esprit d'équipe"]),
        ],
        "Menuiserie": [
            ("Menuisier", "Fabrique et pose des ouvrages en bois : portes, fenêtres, escaliers, placards", ["Travail du bois", "Lecture de plans", "Pose de menuiseries", "Machines-outils bois"], ["Précision", "Créativité", "Minutie"]),
            ("Ébéniste", "Conçoit et réalise des meubles et objets en bois de qualité", ["Ébénisterie fine", "Marqueterie", "Vernissage", "Design mobilier"], ["Créativité", "Patience", "Sens esthétique"]),
            ("Charpentier bois", "Conçoit et réalise les charpentes en bois des bâtiments", ["Taille de charpente", "Assemblage", "Levage", "Lecture de plans"], ["Précision", "Travail en hauteur", "Force physique"]),
            ("Agenceur", "Aménage les espaces intérieurs : cuisines, salles de bain, bureaux", ["Agencement intérieur", "Pose de mobilier", "Lecture de plans", "Finitions"], ["Sens esthétique", "Précision", "Relation client"]),
            ("Menuisier aluminium", "Fabrique et pose des menuiseries en aluminium et PVC", ["Découpe aluminium", "Assemblage", "Pose de vitrages", "Étanchéité"], ["Précision", "Dextérité", "Rigueur"]),
        ],
        "Plomberie": [
            ("Plombier", "Installe et répare les canalisations d'eau et de gaz", ["Installation sanitaire", "Soudure cuivre", "Diagnostic fuites", "Normes sanitaires"], ["Précision", "Autonomie", "Résolution de problèmes"]),
            ("Chauffagiste", "Installe et entretient les systèmes de chauffage", ["Installation chaudières", "Pompes à chaleur", "Plancher chauffant", "Régulation thermique"], ["Rigueur", "Adaptabilité", "Sens du service"]),
            ("Plombier-chauffagiste", "Polyvalent sur les installations sanitaires et de chauffage", ["Plomberie", "Chauffage", "Climatisation", "Diagnostic pannes"], ["Polyvalence", "Autonomie", "Résolution de problèmes"]),
            ("Installateur sanitaire", "Spécialiste de l'installation des équipements sanitaires", ["Pose sanitaires", "Raccordement", "Étanchéité", "Normes PMR"], ["Précision", "Sens du service", "Propreté"]),
            ("Technicien en génie climatique", "Installe et maintient les systèmes de ventilation et climatisation", ["VMC", "Climatisation", "Traitement d'air", "Régulation"], ["Rigueur", "Adaptabilité", "Analyse"]),
        ],
        "Electricité du bâtiment": [
            ("Électricien du bâtiment", "Réalise les installations électriques des bâtiments", ["Câblage", "Tableau électrique", "Normes NF C 15-100", "Domotique"], ["Rigueur", "Précision", "Sécurité"]),
            ("Chef de chantier électricité", "Coordonne les travaux d'installation électrique", ["Gestion d'équipe", "Planification", "Contrôle conformité", "Budget chantier"], ["Leadership", "Organisation", "Communication"]),
            ("Technicien domotique", "Installe les systèmes de contrôle automatisé des bâtiments", ["Domotique", "Programmation automates", "Réseaux", "Objets connectés"], ["Innovation", "Curiosité technique", "Pédagogie"]),
            ("Électricien tertiaire", "Spécialiste des installations électriques tertiaires", ["Courants forts/faibles", "Éclairage", "Sécurité incendie", "Contrôle d'accès"], ["Rigueur", "Polyvalence", "Autonomie"]),
        ],
        "Charpenterie": [
            ("Charpentier", "Conçoit, fabrique et pose les charpentes", ["Taille traditionnelle", "Charpente industrielle", "Levage", "Couverture"], ["Précision", "Travail en hauteur", "Force physique"]),
            ("Couvreur", "Réalise et répare les toitures", ["Pose de tuiles", "Zinguerie", "Étanchéité toiture", "Isolation"], ["Travail en hauteur", "Précision", "Résistance physique"]),
            ("Couvreur-zingueur", "Spécialiste de la couverture et des éléments en zinc", ["Zinguerie", "Couverture", "Gouttières", "Étanchéité"], ["Dextérité", "Travail en hauteur", "Autonomie"]),
        ],
        "Génie civil": [
            ("Ingénieur génie civil", "Conçoit les ouvrages de génie civil : ponts, routes, barrages", ["Calcul de structures", "Logiciels BIM", "Géotechnique", "Gestion de projet"], ["Rigueur", "Analyse", "Leadership"]),
            ("Conducteur de travaux", "Dirige les opérations de construction sur le terrain", ["Planification chantier", "Gestion budgétaire", "Management équipes", "Sécurité"], ["Organisation", "Leadership", "Résistance au stress"]),
            ("Géomètre-topographe", "Réalise les mesures et relevés topographiques", ["Topographie", "GPS", "SIG", "Relevés terrain"], ["Précision", "Rigueur", "Autonomie"]),
            ("Technicien VRD", "Réalise les voiries et réseaux divers", ["Terrassement", "Réseaux", "Enrobés", "Assainissement"], ["Rigueur", "Endurance", "Esprit d'équipe"]),
        ],
    },
    "SGAE": {
        "Comptabilité et finance": [
            ("Comptable", "Tient les comptes de l'entreprise, établit les bilans et comptes de résultat", ["Comptabilité générale", "Fiscalité", "Logiciels comptables (Sage, Cegid)", "Déclarations fiscales", "Analyse financière"], ["Rigueur", "Organisation", "Discrétion", "Esprit d'analyse"]),
            ("Expert-comptable", "Certifie les comptes, conseille les entreprises en gestion financière et fiscale", ["Audit comptable", "Conseil fiscal", "Normes IFRS", "Consolidation", "Gestion de cabinet"], ["Rigueur", "Éthique professionnelle", "Leadership", "Pédagogie"]),
            ("Contrôleur de gestion", "Pilote la performance financière de l'entreprise", ["Tableaux de bord", "Budget prévisionnel", "Analyse des écarts", "Reporting", "Business Intelligence"], ["Esprit analytique", "Rigueur", "Communication", "Proactivité"]),
            ("Auditeur financier", "Vérifie la conformité des comptes et des procédures internes", ["Audit interne/externe", "Contrôle interne", "Normes ISA", "Analyse de risques"], ["Objectivité", "Rigueur", "Esprit critique", "Discrétion"]),
            ("Trésorier d'entreprise", "Gère la trésorerie et optimise les flux financiers", ["Gestion de trésorerie", "Prévisions de cash-flow", "Relations bancaires", "Couverture de change"], ["Anticipation", "Rigueur", "Réactivité", "Négociation"]),
            ("Analyste financier", "Évalue la valeur des entreprises et recommande des investissements", ["Analyse financière", "Modélisation", "Valorisation", "Due diligence"], ["Esprit analytique", "Curiosité", "Rigueur", "Communication"]),
            ("Assistant comptable", "Assiste le comptable dans la tenue des comptes courants", ["Saisie comptable", "Rapprochement bancaire", "Lettrage", "Classement"], ["Rigueur", "Organisation", "Discrétion"]),
            ("Responsable administratif et financier", "Supervise la gestion administrative, comptable et financière", ["Management", "Comptabilité", "Gestion budgétaire", "Reporting direction", "Conformité"], ["Leadership", "Vision stratégique", "Rigueur", "Polyvalence"]),
        ],
        "Ressources humaines": [
            ("Responsable RH", "Pilote la politique RH de l'entreprise", ["Gestion des talents", "Droit du travail", "GPEC", "Relations sociales", "Paie"], ["Écoute", "Leadership", "Discrétion", "Diplomatie"]),
            ("Chargé de recrutement", "Identifie et recrute les talents pour l'entreprise", ["Sourcing", "Entretiens", "ATS", "Marque employeur", "Évaluation"], ["Communication", "Écoute", "Jugement", "Persévérance"]),
            ("Gestionnaire de paie", "Établit les bulletins de paie et gère les déclarations sociales", ["Logiciels de paie", "Droit social", "DSN", "Convention collective"], ["Rigueur", "Discrétion", "Organisation", "Précision"]),
            ("Chargé de formation", "Élabore et déploie le plan de développement des compétences", ["Ingénierie de formation", "OPCO", "Budget formation", "Évaluation"], ["Pédagogie", "Organisation", "Écoute", "Innovation"]),
            ("Responsable diversité et inclusion", "Promeut la diversité et l'inclusion dans l'entreprise", ["Politique diversité", "Sensibilisation", "Indicateurs RH", "Conformité"], ["Empathie", "Communication", "Engagement", "Diplomatie"]),
            ("Juriste en droit social", "Conseille l'entreprise sur les questions de droit du travail", ["Droit du travail", "Contentieux prud'homal", "Négociation collective", "Veille juridique"], ["Rigueur", "Analyse", "Discrétion", "Diplomatie"]),
        ],
        "Management et stratégie": [
            ("Directeur général", "Définit et met en œuvre la stratégie de l'entreprise", ["Stratégie d'entreprise", "Management", "Finance", "Développement commercial"], ["Vision", "Leadership", "Décision", "Résilience"]),
            ("Consultant en management", "Accompagne les entreprises dans leur transformation", ["Diagnostic organisationnel", "Conduite du changement", "Stratégie", "Gestion de projet"], ["Analyse", "Communication", "Adaptabilité", "Pédagogie"]),
            ("Chef de projet", "Pilote les projets transversaux de l'entreprise", ["Gestion de projet", "Agile/Scrum", "Budget", "Planning", "Risques"], ["Organisation", "Communication", "Leadership", "Résolution de problèmes"]),
            ("Business analyst", "Analyse les processus métier et propose des améliorations", ["Analyse de processus", "Modélisation BPMN", "Cahier des charges", "KPIs"], ["Esprit analytique", "Communication", "Curiosité", "Rigueur"]),
            ("Responsable qualité", "Assure et améliore le système de management de la qualité", ["Normes ISO", "Audit qualité", "Amélioration continue", "Indicateurs qualité"], ["Rigueur", "Pédagogie", "Persévérance", "Analyse"]),
        ],
        "Administration et secrétariat": [
            ("Assistant de direction", "Assiste le dirigeant dans l'organisation de son activité", ["Gestion agenda", "Organisation réunions", "Rédaction courriers", "Outils bureautiques"], ["Organisation", "Discrétion", "Réactivité", "Communication"]),
            ("Secrétaire administratif", "Gère les tâches administratives courantes", ["Bureautique", "Classement", "Accueil", "Gestion courrier"], ["Organisation", "Rigueur", "Polyvalence", "Discrétion"]),
            ("Office manager", "Gère le fonctionnement quotidien des bureaux et services généraux", ["Gestion des locaux", "Achats", "Prestataires", "Organisation événements"], ["Polyvalence", "Organisation", "Réactivité", "Communication"]),
            ("Archiviste", "Organise et conserve les archives de l'entreprise", ["Archivage physique et numérique", "GED", "Normes archivistiques", "RGPD"], ["Rigueur", "Organisation", "Méthodologie", "Discrétion"]),
        ],
    },
    "SPSC": {
        "Aide à domicile": [
            ("Auxiliaire de vie sociale", "Accompagne les personnes dépendantes dans les gestes du quotidien", ["Aide à la toilette", "Préparation des repas", "Accompagnement", "Premiers secours"], ["Empathie", "Patience", "Discrétion", "Adaptabilité"]),
            ("Aide à domicile", "Assiste les personnes âgées ou handicapées à leur domicile", ["Entretien du logement", "Courses", "Accompagnement sorties", "Aide aux repas"], ["Bienveillance", "Autonomie", "Ponctualité", "Écoute"]),
            ("Technicien de l'intervention sociale et familiale", "Intervient auprès des familles en difficulté", ["Accompagnement familial", "Médiation", "Aide éducative", "Gestion administrative"], ["Écoute", "Empathie", "Discrétion", "Adaptabilité"]),
        ],
        "Éducation spécialisée": [
            ("Éducateur spécialisé", "Accompagne les personnes en difficulté dans leur insertion sociale", ["Accompagnement éducatif", "Projet personnalisé", "Médiation", "Travail en réseau"], ["Écoute", "Patience", "Empathie", "Résilience"]),
            ("Moniteur-éducateur", "Anime et organise la vie quotidienne des personnes accompagnées", ["Animation", "Accompagnement quotidien", "Projet éducatif", "Travail d'équipe"], ["Créativité", "Patience", "Écoute", "Dynamisme"]),
            ("Éducateur de jeunes enfants", "Accompagne le développement des enfants de 0 à 7 ans", ["Éveil de l'enfant", "Activités pédagogiques", "Observation", "Relation parents"], ["Patience", "Créativité", "Bienveillance", "Observation"]),
        ],
        "Animation socio-culturelle": [
            ("Animateur socio-culturel", "Conçoit et anime des activités pour différents publics", ["Animation de groupes", "Conception de projets", "Gestion de budget", "Partenariats"], ["Créativité", "Dynamisme", "Écoute", "Adaptabilité"]),
            ("Directeur de centre social", "Dirige un établissement d'animation de la vie sociale", ["Management", "Gestion budgétaire", "Projet social", "Partenariats institutionnels"], ["Leadership", "Vision", "Communication", "Engagement"]),
            ("Médiateur social", "Facilite le dialogue entre les habitants et les institutions", ["Médiation", "Écoute active", "Connaissance du territoire", "Gestion de conflits"], ["Empathie", "Diplomatie", "Patience", "Neutralité"]),
        ],
        "Petite enfance": [
            ("Auxiliaire de puériculture", "Assure les soins et l'éveil des jeunes enfants en crèche", ["Soins aux nourrissons", "Éveil", "Hygiène", "Observation"], ["Douceur", "Patience", "Vigilance", "Bienveillance"]),
            ("Agent de crèche", "Participe à l'accueil et aux activités des enfants en crèche", ["Accueil", "Activités d'éveil", "Hygiène", "Repas"], ["Bienveillance", "Dynamisme", "Patience", "Travail d'équipe"]),
            ("Directeur de crèche", "Gère un établissement d'accueil de la petite enfance", ["Management", "Projet pédagogique", "Gestion administrative", "Relations familles"], ["Leadership", "Organisation", "Bienveillance", "Communication"]),
            ("Assistante maternelle", "Accueille des enfants à son domicile", ["Garde d'enfants", "Éveil", "Sécurité", "Communication avec les parents"], ["Patience", "Bienveillance", "Autonomie", "Responsabilité"]),
        ],
        "Accompagnement des personnes âgées": [
            ("Aide-soignant en EHPAD", "Dispense des soins de nursing aux résidents", ["Soins d'hygiène", "Aide à la mobilité", "Surveillance", "Transmissions"], ["Empathie", "Patience", "Résistance physique", "Écoute"]),
            ("Animateur en gérontologie", "Conçoit des activités adaptées aux personnes âgées", ["Animation adaptée", "Stimulation cognitive", "Activités manuelles", "Sorties"], ["Créativité", "Patience", "Bienveillance", "Adaptabilité"]),
            ("Responsable de résidence seniors", "Gère une résidence pour personnes âgées autonomes", ["Management", "Gestion locative", "Animation", "Services à la personne"], ["Organisation", "Écoute", "Leadership", "Diplomatie"]),
        ],
    },
    "SSS": {
        "Infirmier(e)": [
            ("Infirmier diplômé d'État", "Dispense les soins infirmiers sur prescription médicale", ["Soins techniques", "Administration médicaments", "Surveillance clinique", "Éducation thérapeutique"], ["Empathie", "Rigueur", "Réactivité", "Résistance au stress"]),
            ("Infirmier en bloc opératoire", "Assiste le chirurgien pendant les interventions", ["Instrumentation", "Stérilisation", "Protocoles chirurgicaux", "Asepsie"], ["Précision", "Réactivité", "Calme", "Rigueur"]),
            ("Infirmier coordinateur", "Coordonne les soins et l'équipe soignante", ["Coordination des soins", "Management", "Protocoles", "Planification"], ["Leadership", "Organisation", "Communication", "Empathie"]),
        ],
        "Aide-soignant(e)": [
            ("Aide-soignant", "Assure les soins d'hygiène et de confort des patients", ["Toilette", "Aide aux repas", "Mobilisation", "Transmissions"], ["Bienveillance", "Patience", "Résistance physique", "Écoute"]),
            ("Aide médico-psychologique", "Accompagne les personnes dépendantes dans les actes essentiels", ["Accompagnement quotidien", "Stimulation", "Soins de nursing", "Projet de vie"], ["Empathie", "Patience", "Observation", "Créativité"]),
            ("Brancardier", "Transporte les patients au sein de l'établissement de santé", ["Transport patients", "Hygiène", "Brancardage", "Urgences"], ["Calme", "Force physique", "Sens du service", "Réactivité"]),
        ],
        "Assistant(e) de service social": [
            ("Assistant de service social", "Accompagne les personnes en difficulté sociale", ["Écoute sociale", "Orientation", "Accès aux droits", "Médiation"], ["Écoute", "Empathie", "Discrétion", "Persévérance"]),
            ("Conseiller en économie sociale et familiale", "Aide les familles à gérer leur budget et leur quotidien", ["Conseil budgétaire", "Insertion", "Accès au logement", "Éducation financière"], ["Pédagogie", "Patience", "Empathie", "Organisation"]),
        ],
        "Éducateur(trice) spécialisé(e)": [
            ("Éducateur technique spécialisé", "Forme des personnes en difficulté par l'apprentissage d'un métier", ["Formation technique", "Accompagnement éducatif", "Ateliers professionnels", "Insertion"], ["Pédagogie", "Patience", "Adaptabilité", "Écoute"]),
            ("Chef de service éducatif", "Encadre une équipe éducative dans un établissement social", ["Management", "Projet d'établissement", "Coordination", "Partenariats"], ["Leadership", "Communication", "Rigueur", "Empathie"]),
        ],
        "Psychologue": [
            ("Psychologue clinicien", "Évalue et accompagne les troubles psychologiques", ["Entretiens cliniques", "Bilans psychologiques", "Psychothérapie", "Supervision"], ["Écoute", "Empathie", "Patience", "Analyse"]),
            ("Psychologue du travail", "Accompagne les salariés et organisations sur les questions de bien-être au travail", ["Risques psychosociaux", "Bilans de compétences", "Accompagnement au changement", "Prévention"], ["Écoute", "Analyse", "Discrétion", "Pédagogie"]),
        ],
    },
    "SCV": {
        "Vente en magasin": [
            ("Vendeur", "Accueille et conseille les clients en magasin", ["Techniques de vente", "Connaissance produits", "Encaissement", "Merchandising"], ["Sens du contact", "Écoute", "Persuasion", "Dynamisme"]),
            ("Responsable de magasin", "Gère un point de vente : équipe, stocks, CA", ["Management", "Gestion des stocks", "Merchandising", "Objectifs commerciaux"], ["Leadership", "Organisation", "Résistance au stress", "Sens commercial"]),
            ("Chef de rayon", "Gère un rayon en grande distribution", ["Gestion de rayon", "Commandes", "Merchandising", "Animation commerciale"], ["Organisation", "Sens commercial", "Dynamisme", "Réactivité"]),
            ("Visual merchandiser", "Conçoit la mise en scène visuelle des produits", ["Vitrinisme", "Agencement", "Tendances", "Identité visuelle"], ["Créativité", "Sens esthétique", "Organisation", "Minutie"]),
        ],
        "Commerce international": [
            ("Responsable export", "Développe les ventes à l'international", ["Commerce international", "Incoterms", "Douanes", "Négociation interculturelle"], ["Ouverture d'esprit", "Adaptabilité", "Persévérance", "Communication"]),
            ("Assistant commerce international", "Gère les formalités administratives des échanges internationaux", ["Documents douaniers", "Incoterms", "Transport international", "Anglais commercial"], ["Rigueur", "Organisation", "Polyvalence", "Langues"]),
            ("Acheteur international", "Sélectionne et négocie avec les fournisseurs étrangers", ["Sourcing", "Négociation", "Chaîne logistique", "Analyse des marchés"], ["Négociation", "Analyse", "Persévérance", "Curiosité"]),
        ],
        "Négociation commerciale": [
            ("Commercial terrain", "Prospecte et développe un portefeuille clients", ["Prospection", "Négociation", "CRM", "Closing"], ["Persévérance", "Écoute", "Persuasion", "Autonomie"]),
            ("Ingénieur commercial", "Vend des solutions techniques complexes aux entreprises", ["Vente B2B", "Technique produit", "Négociation", "Réponse appels d'offres"], ["Technique", "Communication", "Persévérance", "Écoute"]),
            ("Responsable grands comptes", "Gère et développe les clients stratégiques", ["Account management", "Négociation stratégique", "Plan de compte", "Upselling"], ["Relationnel", "Stratégie", "Patience", "Leadership"]),
            ("Technico-commercial", "Combine expertise technique et compétences commerciales", ["Conseil technique", "Vente", "Démonstration produit", "SAV"], ["Polyvalence", "Communication", "Écoute", "Pédagogie"]),
        ],
        "Marketing": [
            ("Responsable marketing", "Définit et pilote la stratégie marketing", ["Plan marketing", "Études de marché", "Mix marketing", "Budget"], ["Créativité", "Analyse", "Leadership", "Vision stratégique"]),
            ("Chef de produit", "Gère le cycle de vie d'un produit ou service", ["Lancement produit", "Pricing", "Veille concurrentielle", "P&L"], ["Analyse", "Créativité", "Organisation", "Communication"]),
            ("Community manager", "Anime les réseaux sociaux et la communauté en ligne", ["Réseaux sociaux", "Création de contenu", "Veille e-réputation", "Analytics"], ["Créativité", "Réactivité", "Empathie", "Rédaction"]),
            ("Chargé d'études marketing", "Réalise des études pour orienter les décisions marketing", ["Études quantitatives/qualitatives", "Analyse données", "Sondages", "Reporting"], ["Analyse", "Rigueur", "Curiosité", "Synthèse"]),
        ],
    },
    "SHR": {
        "Cuisine": [
            ("Chef cuisinier", "Dirige la brigade et crée les menus", ["Création culinaire", "Gestion de brigade", "HACCP", "Gestion des coûts matière"], ["Créativité", "Leadership", "Résistance au stress", "Passion"]),
            ("Commis de cuisine", "Assiste les cuisiniers dans la préparation des plats", ["Préparations de base", "Découpe", "Mise en place", "Hygiène"], ["Rigueur", "Rapidité", "Travail d'équipe", "Motivation"]),
            ("Pâtissier", "Réalise des pâtisseries, desserts et viennoiseries", ["Pâtisserie", "Chocolaterie", "Décoration", "Créativité culinaire"], ["Précision", "Créativité", "Patience", "Sens esthétique"]),
            ("Second de cuisine", "Seconde le chef et le remplace en son absence", ["Coordination cuisine", "Cuisson", "Dressage", "Gestion stocks"], ["Organisation", "Polyvalence", "Résistance au stress", "Leadership"]),
        ],
        "Service en salle": [
            ("Serveur", "Accueille et sert les clients en restaurant", ["Service à table", "Prise de commande", "Encaissement", "Conseil mets et vins"], ["Sens du contact", "Rapidité", "Mémoire", "Courtoisie"]),
            ("Maître d'hôtel", "Supervise le service en salle et coordonne l'équipe", ["Management salle", "Accueil VIP", "Protocole", "Gestion des réservations"], ["Élégance", "Leadership", "Communication", "Calme"]),
            ("Sommelier", "Conseille les clients dans le choix des vins", ["Œnologie", "Accords mets-vins", "Gestion de cave", "Dégustation"], ["Sens gustatif", "Pédagogie", "Curiosité", "Mémoire"]),
            ("Barman", "Prépare et sert les boissons au bar", ["Cocktails", "Service au bar", "Gestion des stocks boissons", "Animation"], ["Créativité", "Rapidité", "Sens du contact", "Dextérité"]),
        ],
        "Hébergement": [
            ("Réceptionniste d'hôtel", "Accueille les clients et gère les réservations", ["Accueil client", "Check-in/check-out", "Logiciel hôtelier", "Langues étrangères"], ["Sens du service", "Communication", "Organisation", "Polyvalence"]),
            ("Gouvernant d'hôtel", "Supervise la propreté des chambres et parties communes", ["Management", "Contrôle qualité", "Gestion du linge", "Hygiène"], ["Rigueur", "Organisation", "Sens du détail", "Leadership"]),
            ("Concierge d'hôtel", "Accompagne les clients dans leurs demandes et souhaits", ["Conciergerie", "Réseau local", "Réservations", "Langues"], ["Sens du service", "Débrouillardise", "Discrétion", "Culture générale"]),
        ],
        "Gestion hôtelière": [
            ("Directeur d'hôtel", "Gère l'ensemble de l'établissement hôtelier", ["Management", "Gestion financière", "Marketing hôtelier", "Qualité de service"], ["Leadership", "Vision stratégique", "Résistance au stress", "Diplomatie"]),
            ("Revenue manager", "Optimise le chiffre d'affaires par la gestion tarifaire", ["Yield management", "Analyse data", "Tarification dynamique", "Prévisions"], ["Analyse", "Rigueur", "Réactivité", "Sens commercial"]),
        ],
    },
    "SIN": {
        "Développement web et mobile": [
            ("Développeur web full-stack", "Conçoit et développe des applications web complètes", ["JavaScript", "React/Vue", "Node.js/Python", "Bases de données", "API REST"], ["Logique", "Curiosité", "Autonomie", "Résolution de problèmes"]),
            ("Développeur mobile", "Crée des applications pour smartphones et tablettes", ["Swift/Kotlin", "React Native", "Flutter", "UI/UX mobile"], ["Créativité", "Rigueur", "Adaptabilité", "Curiosité"]),
            ("Développeur front-end", "Conçoit l'interface utilisateur des sites et applications", ["HTML/CSS", "JavaScript", "React", "Responsive design", "Accessibilité"], ["Sens esthétique", "Précision", "Créativité", "Empathie"]),
            ("Développeur back-end", "Conçoit la logique serveur et les APIs", ["Python/Java/PHP", "Bases de données", "API", "Architecture logicielle"], ["Logique", "Rigueur", "Analyse", "Autonomie"]),
            ("DevOps", "Automatise les déploiements et maintient l'infrastructure", ["CI/CD", "Docker/Kubernetes", "Cloud AWS/GCP", "Monitoring", "Infrastructure as Code"], ["Rigueur", "Analyse", "Autonomie", "Curiosité"]),
        ],
        "Administration systèmes et réseaux": [
            ("Administrateur systèmes", "Gère et maintient les serveurs et systèmes informatiques", ["Linux/Windows Server", "Virtualisation", "Sauvegarde", "Monitoring"], ["Rigueur", "Réactivité", "Analyse", "Organisation"]),
            ("Administrateur réseaux", "Conçoit et maintient l'infrastructure réseau", ["Cisco/Juniper", "Routage/Switching", "Firewall", "VPN", "WiFi"], ["Analyse", "Rigueur", "Réactivité", "Méthodologie"]),
            ("Technicien support informatique", "Assiste les utilisateurs dans la résolution de problèmes techniques", ["Diagnostic", "Dépannage", "Installation", "Support utilisateur"], ["Patience", "Pédagogie", "Réactivité", "Écoute"]),
            ("Ingénieur cloud", "Conçoit et gère les infrastructures cloud", ["AWS/Azure/GCP", "Conteneurisation", "Automatisation", "Sécurité cloud"], ["Innovation", "Rigueur", "Autonomie", "Veille technologique"]),
        ],
        "Cybersécurité": [
            ("Analyste en cybersécurité", "Surveille et protège les systèmes contre les cyberattaques", ["SIEM", "Analyse de vulnérabilités", "Incident response", "Forensics"], ["Vigilance", "Rigueur", "Curiosité", "Réactivité"]),
            ("Pentester", "Teste la sécurité des systèmes par des simulations d'attaques", ["Tests d'intrusion", "OWASP", "Scripting", "Social engineering"], ["Curiosité", "Créativité", "Éthique", "Rigueur"]),
            ("RSSI", "Définit et pilote la politique de sécurité informatique", ["Politique de sécurité", "Gestion des risques", "Conformité RGPD", "Management"], ["Leadership", "Analyse", "Communication", "Anticipation"]),
        ],
        "Design numérique": [
            ("UX Designer", "Conçoit l'expérience utilisateur des produits numériques", ["Recherche utilisateur", "Wireframes", "Prototypage", "Tests utilisateurs"], ["Empathie", "Créativité", "Analyse", "Communication"]),
            ("UI Designer", "Conçoit les interfaces visuelles des applications", ["Design d'interface", "Figma", "Design system", "Typographie"], ["Sens esthétique", "Précision", "Créativité", "Attention au détail"]),
            ("Web designer", "Conçoit le design visuel des sites web", ["Design graphique", "HTML/CSS", "Responsive design", "Outils Adobe"], ["Créativité", "Sens esthétique", "Curiosité", "Communication"]),
            ("Data analyst", "Analyse les données pour guider les décisions", ["SQL", "Python", "Visualisation", "Statistiques", "Tableau/Power BI"], ["Esprit analytique", "Rigueur", "Curiosité", "Communication"]),
        ],
    },
    "SAA": {
        "Production agricole": [
            ("Agriculteur", "Gère une exploitation agricole", ["Culture végétale", "Machinisme agricole", "Gestion d'exploitation", "Agriculture durable"], ["Endurance", "Polyvalence", "Autonomie", "Observation"]),
            ("Chef de culture", "Supervise la production végétale d'une exploitation", ["Agronomie", "Plan de culture", "Phytosanitaire", "Irrigation"], ["Organisation", "Observation", "Anticipation", "Rigueur"]),
            ("Ouvrier agricole polyvalent", "Effectue les travaux agricoles courants", ["Semis", "Récolte", "Conduite d'engins", "Entretien"], ["Endurance", "Polyvalence", "Ponctualité", "Travail d'équipe"]),
        ],
        "Transformation des produits agricoles": [
            ("Opérateur de production agroalimentaire", "Conduit une ligne de production alimentaire", ["Conduite de machines", "HACCP", "Contrôle qualité", "Traçabilité"], ["Rigueur", "Vigilance", "Réactivité", "Hygiène"]),
            ("Technicien qualité agroalimentaire", "Contrôle la qualité des produits alimentaires", ["Analyses microbiologiques", "HACCP", "Audits", "Normes IFS/BRC"], ["Rigueur", "Précision", "Analyse", "Méthodologie"]),
            ("Responsable de production agroalimentaire", "Gère la production d'une usine agroalimentaire", ["Management", "Planification production", "Optimisation", "Sécurité alimentaire"], ["Leadership", "Organisation", "Réactivité", "Rigueur"]),
        ],
        "Agroéquipement": [
            ("Mécanicien agricole", "Entretient et répare les engins agricoles", ["Mécanique", "Hydraulique", "Électronique embarquée", "Diagnostic"], ["Polyvalence", "Débrouillardise", "Rigueur", "Autonomie"]),
            ("Technicien SAV agricole", "Assure le service après-vente des équipements agricoles", ["Diagnostic", "Réparation", "Conseil client", "Formation utilisateur"], ["Sens du service", "Polyvalence", "Pédagogie", "Réactivité"]),
        ],
        "Viticulture": [
            ("Viticulteur", "Cultive la vigne et produit du vin", ["Viticulture", "Vinification", "Œnologie", "Gestion de domaine"], ["Passion", "Patience", "Observation", "Endurance"]),
            ("Maître de chai", "Supervise la vinification et l'élevage du vin", ["Vinification", "Dégustation", "Élevage", "Hygiène de cave"], ["Sens gustatif", "Rigueur", "Patience", "Créativité"]),
            ("Caviste", "Conseille et vend le vin en boutique", ["Œnologie", "Conseil client", "Gestion de stocks", "Accords mets-vins"], ["Passion", "Communication", "Sens commercial", "Curiosité"]),
        ],
    },
    "STL": {
        "Conduite routière": [
            ("Conducteur routier", "Transporte des marchandises par la route", ["Conduite PL/SPL", "Réglementation transport", "Chargement/déchargement", "RSE"], ["Prudence", "Autonomie", "Ponctualité", "Endurance"]),
            ("Conducteur de bus", "Assure le transport de voyageurs", ["Conduite bus", "Sécurité passagers", "Réglementation", "Service client"], ["Prudence", "Calme", "Ponctualité", "Sens du service"]),
            ("Chauffeur-livreur", "Assure la livraison de marchandises en zone urbaine", ["Conduite VL", "Livraison", "PDA", "Organisation tournée"], ["Ponctualité", "Autonomie", "Sens du service", "Organisation"]),
        ],
        "Logistique et gestion des transports": [
            ("Responsable logistique", "Pilote la chaîne logistique de l'entreprise", ["Supply chain", "WMS", "Transport", "Gestion de stocks", "KPIs"], ["Organisation", "Analyse", "Leadership", "Réactivité"]),
            ("Préparateur de commandes", "Rassemble les produits pour expédition", ["Picking", "CACES", "Scan", "Contrôle qualité"], ["Rapidité", "Précision", "Endurance", "Rigueur"]),
            ("Gestionnaire de stocks", "Gère les entrées/sorties et l'inventaire du stock", ["Gestion de stocks", "ERP/WMS", "Inventaire", "Prévisions"], ["Organisation", "Rigueur", "Analyse", "Anticipation"]),
            ("Affréteur", "Organise le transport de marchandises en sélectionnant les transporteurs", ["Négociation tarifaire", "Réglementation transport", "Coordination", "Incoterms"], ["Négociation", "Réactivité", "Organisation", "Analyse"]),
        ],
        "Manutention": [
            ("Cariste", "Conduit des chariots élévateurs pour déplacer des marchandises", ["Conduite chariot", "CACES", "Chargement/déchargement", "Sécurité"], ["Vigilance", "Précision", "Rigueur", "Calme"]),
            ("Magasinier", "Réceptionne, stocke et expédie les marchandises", ["Réception", "Stockage", "Expédition", "Inventaire"], ["Organisation", "Rigueur", "Endurance", "Esprit d'équipe"]),
            ("Agent de quai", "Organise le chargement et déchargement des camions", ["Organisation quai", "Contrôle marchandises", "Manutention", "PDA"], ["Organisation", "Rapidité", "Vigilance", "Travail d'équipe"]),
        ],
    },
    "SEDD": {
        "Gestion des déchets": [
            ("Technicien traitement des déchets", "Gère le traitement et la valorisation des déchets", ["Tri", "Valorisation", "Réglementation ICPE", "Analyses"], ["Rigueur", "Sens de l'environnement", "Organisation"]),
            ("Responsable environnement", "Pilote la politique environnementale de l'entreprise", ["Normes ISO 14001", "Bilan carbone", "Réglementation", "RSE"], ["Engagement", "Analyse", "Communication", "Leadership"]),
        ],
        "Énergies renouvelables": [
            ("Technicien en énergie solaire", "Installe et maintient les panneaux photovoltaïques", ["Installation PV", "Onduleurs", "Raccordement", "Maintenance"], ["Rigueur", "Travail en hauteur", "Autonomie"]),
            ("Ingénieur en énergies renouvelables", "Conçoit des projets d'énergies renouvelables", ["Éolien", "Solaire", "Études de faisabilité", "Dimensionnement"], ["Innovation", "Analyse", "Engagement", "Rigueur"]),
            ("Chef de projet éolien", "Pilote le développement de parcs éoliens", ["Développement éolien", "Autorisations", "Concertation", "Études d'impact"], ["Persévérance", "Communication", "Organisation", "Diplomatie"]),
        ],
        "Eau et assainissement": [
            ("Technicien eau potable", "Assure la production et distribution d'eau potable", ["Traitement de l'eau", "Réseaux", "Analyses", "Maintenance"], ["Rigueur", "Vigilance", "Autonomie"]),
            ("Agent d'assainissement", "Entretient les réseaux d'assainissement", ["Curage", "Inspection vidéo", "Maintenance réseau", "Sécurité"], ["Endurance", "Rigueur", "Travail d'équipe"]),
        ],
        "Biodiversité et espaces naturels": [
            ("Écologue", "Étudie les écosystèmes et réalise des inventaires naturalistes", ["Inventaires faune/flore", "Études d'impact", "SIG", "Rédaction scientifique"], ["Observation", "Patience", "Rigueur", "Passion nature"]),
            ("Garde forestier", "Protège et gère les espaces forestiers", ["Sylviculture", "Surveillance", "Éducation environnement", "Cartographie"], ["Autonomie", "Observation", "Endurance", "Pédagogie"]),
        ],
    },
    "SEF": {
        "Enseignement": [
            ("Professeur des écoles", "Enseigne toutes les matières en école primaire", ["Pédagogie", "Programme scolaire", "Évaluation", "Gestion de classe"], ["Patience", "Pédagogie", "Créativité", "Écoute"]),
            ("Professeur de collège/lycée", "Enseigne une discipline spécifique dans le secondaire", ["Discipline enseignée", "Pédagogie", "Évaluation", "Projet éducatif"], ["Pédagogie", "Autorité bienveillante", "Patience", "Culture générale"]),
        ],
        "Formation professionnelle": [
            ("Formateur professionnel", "Transmet des compétences techniques à des adultes", ["Ingénierie pédagogique", "Animation de groupe", "Évaluation", "E-learning"], ["Pédagogie", "Adaptabilité", "Communication", "Patience"]),
            ("Conseiller en formation", "Oriente et accompagne les adultes dans leur parcours de formation", ["Conseil en orientation", "Bilan de compétences", "Dispositifs de formation", "VAE"], ["Écoute", "Empathie", "Analyse", "Pédagogie"]),
            ("Ingénieur pédagogique", "Conçoit des dispositifs de formation innovants", ["Ingénierie de formation", "E-learning", "Scénarisation pédagogique", "Outils digitaux"], ["Créativité", "Innovation", "Rigueur", "Pédagogie"]),
        ],
        "Accompagnement scolaire": [
            ("Accompagnant d'élèves en situation de handicap (AESH)", "Accompagne les élèves handicapés en milieu scolaire", ["Aide aux apprentissages", "Adaptation", "Communication", "Inclusion"], ["Patience", "Empathie", "Adaptabilité", "Bienveillance"]),
            ("Conseiller principal d'éducation", "Assure le suivi éducatif des élèves", ["Vie scolaire", "Médiation", "Projets éducatifs", "Gestion de conflits"], ["Écoute", "Autorité", "Diplomatie", "Organisation"]),
        ],
        "Recherche en éducation": [
            ("Chercheur en sciences de l'éducation", "Mène des recherches sur les pratiques éducatives", ["Méthodologie de recherche", "Analyse de données", "Publication scientifique", "Expérimentation"], ["Curiosité", "Rigueur", "Persévérance", "Analyse"]),
        ],
    },
    "SCM": {
        "Journalisme": [
            ("Journaliste", "Recherche, vérifie et diffuse l'information", ["Rédaction", "Enquête", "Interview", "Veille informationnelle"], ["Curiosité", "Rigueur", "Réactivité", "Éthique"]),
            ("Journaliste web", "Produit du contenu pour les médias en ligne", ["Rédaction web", "SEO", "Réseaux sociaux", "Multimédia"], ["Réactivité", "Polyvalence", "Créativité", "Rédaction"]),
        ],
        "Communication d'entreprise": [
            ("Chargé de communication", "Met en œuvre la stratégie de communication", ["Rédaction", "Événementiel", "Relations presse", "Outils digitaux"], ["Créativité", "Organisation", "Communication", "Polyvalence"]),
            ("Directeur de communication", "Définit la stratégie de communication globale", ["Stratégie de communication", "Management", "Relations publiques", "Gestion de crise"], ["Vision", "Leadership", "Créativité", "Diplomatie"]),
            ("Attaché de presse", "Gère les relations avec les médias", ["Relations presse", "Communiqués", "Conférences de presse", "Revue de presse"], ["Communication", "Réactivité", "Réseau", "Rédaction"]),
        ],
        "Production audiovisuelle": [
            ("Réalisateur", "Dirige la création d'œuvres audiovisuelles", ["Direction artistique", "Scénarisation", "Tournage", "Post-production"], ["Créativité", "Leadership", "Vision artistique", "Persévérance"]),
            ("Monteur vidéo", "Monte et assemble les séquences vidéo", ["Montage vidéo", "After Effects", "Premiere Pro", "Color grading"], ["Créativité", "Rigueur", "Sens du rythme", "Patience"]),
            ("Cadreur", "Réalise les prises de vue", ["Cadrage", "Éclairage", "Caméra", "Composition"], ["Sens esthétique", "Stabilité", "Créativité", "Adaptabilité"]),
        ],
        "Édition et graphisme": [
            ("Graphiste", "Conçoit des visuels pour la communication", ["Suite Adobe", "Design graphique", "Typographie", "Identité visuelle"], ["Créativité", "Précision", "Sens esthétique", "Écoute client"]),
            ("Directeur artistique", "Définit l'univers visuel des projets créatifs", ["Direction artistique", "Brand identity", "Management créatif", "Tendances"], ["Vision créative", "Leadership", "Culture visuelle", "Communication"]),
            ("Infographiste", "Crée des visuels informatifs et pédagogiques", ["Infographie", "Data visualisation", "Illustration", "Outils graphiques"], ["Précision", "Pédagogie", "Créativité", "Synthèse"]),
        ],
    },
    "STOU": {
        "Tourisme culturel": [
            ("Guide touristique", "Accompagne et informe les visiteurs", ["Culture locale", "Animation", "Langues étrangères", "Histoire"], ["Communication", "Passion", "Pédagogie", "Adaptabilité"]),
            ("Agent de voyage", "Conseille et organise des voyages pour les clients", ["Réservation", "Conseil voyage", "GDS", "Vente"], ["Sens du service", "Organisation", "Curiosité", "Communication"]),
        ],
        "Tourisme d'aventure": [
            ("Accompagnateur en montagne", "Guide les randonneurs en milieu montagnard", ["Randonnée", "Orientation", "Sécurité montagne", "Faune/Flore"], ["Endurance", "Pédagogie", "Sens des responsabilités", "Passion nature"]),
            ("Moniteur de sports nautiques", "Enseigne les activités nautiques", ["Voile/Kayak/Surf", "Sécurité nautique", "Animation", "Pédagogie"], ["Pédagogie", "Sportivité", "Calme", "Vigilance"]),
        ],
        "Tourisme de bien-être": [
            ("Spa manager", "Gère un espace de bien-être", ["Management", "Soins spa", "Gestion planning", "Qualité de service"], ["Sens du service", "Organisation", "Calme", "Leadership"]),
            ("Hydrothérapeute", "Administre des soins par l'eau à visée thérapeutique", ["Hydrothérapie", "Protocoles de soins", "Anatomie", "Accueil"], ["Empathie", "Douceur", "Rigueur", "Écoute"]),
        ],
        "Événementiel": [
            ("Chef de projet événementiel", "Organise des événements de A à Z", ["Gestion de projet", "Budget", "Prestataires", "Logistique"], ["Organisation", "Créativité", "Résistance au stress", "Communication"]),
            ("Wedding planner", "Organise des mariages sur mesure", ["Organisation mariage", "Décoration", "Coordination prestataires", "Budget"], ["Créativité", "Organisation", "Empathie", "Diplomatie"]),
        ],
    },
    "SSL": {
        "Sport professionnel": [
            ("Entraîneur sportif", "Prépare et encadre des sportifs en compétition", ["Préparation physique", "Tactique", "Coaching mental", "Analyse vidéo"], ["Leadership", "Pédagogie", "Motivation", "Analyse"]),
            ("Préparateur physique", "Optimise la condition physique des sportifs", ["Programmation d'entraînement", "Physiologie", "Tests physiques", "Prévention blessures"], ["Rigueur", "Pédagogie", "Écoute", "Adaptabilité"]),
        ],
        "Loisirs et animation": [
            ("Animateur sportif", "Anime des activités sportives pour tous publics", ["Animation de groupe", "Techniques sportives", "Sécurité", "Pédagogie"], ["Dynamisme", "Pédagogie", "Écoute", "Créativité"]),
            ("Directeur d'accueil de loisirs", "Gère un centre de loisirs", ["Management", "Projet pédagogique", "Réglementation", "Budget"], ["Leadership", "Organisation", "Créativité", "Responsabilité"]),
        ],
        "Bien-être et fitness": [
            ("Coach sportif", "Accompagne individuellement les personnes dans leur pratique sportive", ["Programmation sportive", "Nutrition de base", "Motivation", "Adaptation"], ["Écoute", "Motivation", "Pédagogie", "Empathie"]),
            ("Professeur de yoga", "Enseigne la pratique du yoga", ["Postures", "Respiration", "Méditation", "Anatomie"], ["Calme", "Patience", "Pédagogie", "Bienveillance"]),
        ],
        "Gestion d'installations sportives": [
            ("Directeur d'équipement sportif", "Gère un complexe sportif", ["Management", "Gestion d'équipements", "Budget", "Sécurité"], ["Leadership", "Organisation", "Polyvalence", "Communication"]),
            ("Agent d'entretien sportif", "Entretient les terrains et équipements sportifs", ["Entretien terrains", "Maintenance", "Sécurité", "Traçage"], ["Rigueur", "Polyvalence", "Autonomie", "Disponibilité"]),
        ],
    },
    "SSD": {
        "Sécurité privée": [
            ("Agent de sécurité", "Assure la protection des personnes et des biens", ["Surveillance", "Contrôle d'accès", "Rondes", "Gestion de conflits"], ["Vigilance", "Calme", "Autorité", "Discrétion"]),
            ("Directeur de la sécurité", "Pilote la politique de sécurité d'une organisation", ["Analyse des risques", "Plan de sûreté", "Management", "Réglementation"], ["Leadership", "Analyse", "Sang-froid", "Organisation"]),
        ],
        "Défense nationale": [
            ("Militaire du rang", "Exécute les missions opérationnelles", ["Combat", "Discipline", "Techniques militaires", "Premiers secours"], ["Courage", "Discipline", "Esprit d'équipe", "Résistance"]),
            ("Sous-officier", "Encadre les militaires et dirige les opérations terrain", ["Commandement", "Tactique", "Formation", "Administration"], ["Leadership", "Discipline", "Sang-froid", "Responsabilité"]),
        ],
        "Sécurité civile": [
            ("Sapeur-pompier", "Intervient pour secourir et protéger les populations", ["Lutte incendie", "Secourisme", "Sauvetage", "Prévention"], ["Courage", "Sang-froid", "Endurance", "Esprit d'équipe"]),
            ("Agent de sécurité civile", "Participe à la prévention et gestion des risques", ["Plans d'urgence", "Exercices", "Veille", "Communication de crise"], ["Rigueur", "Réactivité", "Calme", "Organisation"]),
        ],
        "Cyberdéfense": [
            ("Analyste en cyberdéfense", "Détecte et neutralise les cybermenaces", ["SOC", "Analyse de menaces", "Forensics", "Veille sécurité"], ["Vigilance", "Rigueur", "Curiosité", "Analyse"]),
            ("Expert en guerre électronique", "Maîtrise les technologies de guerre électronique", ["Radiofréquences", "Brouillage", "Renseignement signal", "Cryptographie"], ["Analyse", "Discrétion", "Rigueur", "Innovation"]),
        ],
    },
    "SMT": {
        "Création textile": [
            ("Styliste", "Crée des collections de vêtements", ["Dessin de mode", "Connaissance textiles", "Tendances", "Patronage"], ["Créativité", "Sens esthétique", "Curiosité", "Persévérance"]),
            ("Designer textile", "Conçoit des motifs et matières textiles", ["Design de motifs", "Impression textile", "Colorimétrie", "CAO textile"], ["Créativité", "Sens des couleurs", "Précision", "Innovation"]),
        ],
        "Confection": [
            ("Couturier", "Réalise des vêtements sur mesure", ["Couture", "Patronage", "Retouches", "Ajustements"], ["Précision", "Patience", "Sens esthétique", "Dextérité"]),
            ("Modéliste", "Transforme les dessins du styliste en patrons", ["Patronage", "Gradation", "Moulage", "CAO"], ["Précision", "Rigueur", "Analyse", "Sens des volumes"]),
            ("Mécanicien en confection", "Opère les machines de couture industrielle", ["Machines à coudre", "Assemblage", "Contrôle qualité", "Cadences"], ["Dextérité", "Rapidité", "Rigueur", "Endurance"]),
        ],
        "Commerce de la mode": [
            ("Responsable de collection", "Gère le développement d'une collection de mode", ["Sourcing", "Planning collection", "Achat", "Suivi production"], ["Organisation", "Sens commercial", "Créativité", "Négociation"]),
            ("Acheteur mode", "Sélectionne les produits pour les points de vente", ["Veille tendances", "Négociation fournisseurs", "Analyse ventes", "Budgets d'achat"], ["Sens commercial", "Intuition", "Négociation", "Analyse"]),
        ],
        "Innovation textile": [
            ("Ingénieur textile", "Développe de nouvelles matières et procédés textiles", ["R&D textile", "Fibres techniques", "Tests qualité", "Innovation"], ["Innovation", "Rigueur", "Curiosité", "Analyse"]),
            ("Technicien en ennoblissement textile", "Réalise les traitements de finition des textiles", ["Teinture", "Impression", "Apprêt", "Contrôle qualité"], ["Précision", "Rigueur", "Sens des couleurs", "Méthode"]),
        ],
    },
    "SAAT": {
        "Céramique": [
            ("Céramiste", "Crée des pièces en céramique", ["Tournage", "Modelage", "Émaillage", "Cuisson"], ["Créativité", "Patience", "Précision", "Sens artistique"]),
        ],
        "Bijouterie-joaillerie": [
            ("Bijoutier-joaillier", "Fabrique et répare des bijoux", ["Sertissage", "Soudure", "Polissage", "Design bijoux"], ["Minutie", "Créativité", "Patience", "Précision"]),
        ],
        "Reliure et dorure": [
            ("Relieur-doreur", "Restaure et crée des reliures de livres", ["Reliure", "Dorure à chaud", "Restauration", "Papier marbré"], ["Minutie", "Patience", "Sens artistique", "Dextérité"]),
        ],
        "Vitrail": [
            ("Maître verrier", "Crée et restaure des vitraux", ["Découpe de verre", "Soudure au plomb", "Peinture sur verre", "Restauration"], ["Créativité", "Précision", "Patience", "Sens artistique"]),
        ],
    },
    "SMA": {
        "Restauration d'art": [
            ("Restaurateur d'art", "Restaure les œuvres d'art endommagées", ["Restauration", "Chimie des matériaux", "Histoire de l'art", "Techniques anciennes"], ["Patience", "Minutie", "Respect du patrimoine", "Analyse"]),
        ],
        "Sculpture": [
            ("Sculpteur", "Crée des œuvres en trois dimensions", ["Modelage", "Taille directe", "Moulage", "Bronze"], ["Créativité", "Force physique", "Vision spatiale", "Persévérance"]),
        ],
        "Ferronnerie d'art": [
            ("Ferronnier d'art", "Crée des ouvrages en fer forgé", ["Forge", "Soudure", "Design", "Restauration"], ["Créativité", "Force physique", "Précision", "Sens esthétique"]),
        ],
        "Gravure et estampe": [
            ("Graveur", "Réalise des gravures sur différents supports", ["Gravure taille-douce", "Lithographie", "Sérigraphie", "Impression"], ["Précision", "Patience", "Sens artistique", "Minutie"]),
        ],
    },
    "SDAA": {
        "Design produit": [
            ("Designer produit", "Conçoit des objets du quotidien", ["Design industriel", "3D/CAO", "Prototypage", "Ergonomie"], ["Créativité", "Sens pratique", "Analyse des usages", "Communication"]),
            ("Designer d'espace", "Aménage des espaces intérieurs et extérieurs", ["Architecture intérieure", "3D", "Matériaux", "Éclairage"], ["Créativité", "Sens spatial", "Écoute", "Sens esthétique"]),
        ],
        "Design graphique": [
            ("Designer graphique", "Crée des identités visuelles et supports de communication", ["Suite Adobe", "Typographie", "Mise en page", "Identité visuelle"], ["Créativité", "Sens esthétique", "Rigueur", "Écoute"]),
            ("Illustrateur", "Réalise des illustrations pour divers supports", ["Dessin", "Illustration numérique", "Narration visuelle", "Style personnel"], ["Créativité", "Patience", "Imagination", "Technique de dessin"]),
        ],
        "Design numérique et interactif": [
            ("Motion designer", "Crée des animations et vidéos graphiques", ["After Effects", "Animation 2D/3D", "Storytelling visuel", "Sound design"], ["Créativité", "Sens du rythme", "Précision", "Curiosité"]),
            ("Game designer", "Conçoit les mécaniques et l'expérience de jeu", ["Game design", "Level design", "Prototypage", "Narration interactive"], ["Créativité", "Logique", "Empathie joueur", "Communication"]),
        ],
        "Arts appliqués": [
            ("Directeur artistique", "Dirige la création visuelle de projets", ["Direction artistique", "Création visuelle", "Management créatif", "Tendances"], ["Vision créative", "Leadership", "Communication", "Culture artistique"]),
            ("Photographe", "Réalise des prises de vue professionnelles", ["Prise de vue", "Retouche", "Éclairage", "Post-production"], ["Sens esthétique", "Technique", "Créativité", "Patience"]),
        ],
    },
}


async def seed_all_metiers():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    total_inserted = 0
    for filiere_code, secteurs in METIERS_DATA.items():
        # Get filière name
        filiere_doc = await db.opc_filieres.find_one({"code": filiere_code})
        filiere_nom = filiere_doc["nom"] if filiere_doc else ""

        for sector_name, metiers_list in secteurs.items():
            for metier_tuple in metiers_list:
                nom, mission, savoir_faire, savoir_etre = metier_tuple
                # Check if already exists
                exists = await db.opc_metiers.find_one({
                    "filiere_code": filiere_code,
                    "sector_name": sector_name,
                    "metier": nom
                })
                if exists:
                    continue

                doc = {
                    "filiere_code": filiere_code,
                    "filiere_nom": filiere_nom,
                    "sector_code": f"{filiere_code}_{sector_name[:3].upper()}",
                    "sector_name": sector_name,
                    "metier": nom,
                    "mission": mission,
                    "savoir_faire": savoir_faire,
                    "capacites_techniques": savoir_faire,
                    "savoir_etre": savoir_etre,
                    "capacites_professionnelles": [],
                    "qualites_humaines": []
                }
                await db.opc_metiers.insert_one(doc)
                total_inserted += 1

    # Final count
    total = await db.opc_metiers.count_documents({})
    pipeline = [
        {"$group": {"_id": "$filiere_code", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    print(f"\n✅ {total_inserted} nouveaux métiers ajoutés. Total: {total} métiers")
    async for doc in db.opc_metiers.aggregate(pipeline):
        f_doc = await db.opc_filieres.find_one({"code": doc["_id"]})
        name = f_doc["nom"] if f_doc else doc["_id"]
        print(f"  {doc['_id']:6s} {doc['count']:3d} métiers — {name}")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed_all_metiers())
