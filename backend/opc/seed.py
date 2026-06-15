"""
OPC — Seed automatique de données démo (région Grand Est)
Idempotent : ne re-seed pas si les collections sont déjà peuplées.
"""

from datetime import datetime, timezone, timedelta
import random

from .db import (
    col_profils, col_entreprises, col_offres, col_formations,
    col_institutionnel, col_terrain, col_parcours, col_referentiels
)


def _val(source="seed_demo", fiabilite="moyenne", consentement=True,
         secteur=None, metier=None, niveau="declare"):
    return {
        "source": source,
        "date_collecte": datetime.now(timezone.utc),
        "fiabilite": fiabilite,
        "territoire": "Grand Est",
        "secteur": secteur,
        "metier_concerne": metier,
        "niveau_preuve": niveau,
        "consentement_rgpd": consentement,
        "anonymise": True
    }


# ─── Référentiels métiers ─────────────────────────────────────────────────

REFERENTIELS = [
    {
        "code_rome": "M1805", "intitule_metier": "Études et développement informatique",
        "statut": "en_transformation", "taux_tension_territorial": 78.5,
        "competences_core": ["Python", "JavaScript", "SQL", "Git", "API REST"],
        "competences_emergentes": ["LLM prompting", "RAG", "TypeScript", "Cloud GCP", "DevSecOps"],
        "competences_en_declin": ["jQuery", "PHP procédural"],
        "soft_skills_prioritaires": ["autonomie", "veille technologique", "communication", "rigueur"],
        "trajectoires_compatibles": ["M1802", "M1810"],
    },
    {
        "code_rome": "M1802", "intitule_metier": "Expertise et support en systèmes d'information",
        "statut": "en_croissance", "taux_tension_territorial": 62.0,
        "competences_core": ["Linux", "Active Directory", "Réseaux", "ITIL"],
        "competences_emergentes": ["Cybersécurité", "Zero Trust", "Cloud Azure", "IaC Terraform"],
        "competences_en_declin": ["Windows Server 2008"],
        "soft_skills_prioritaires": ["sang-froid", "pédagogie", "écoute"],
        "trajectoires_compatibles": ["M1805", "M1810"],
    },
    {
        "code_rome": "M1810", "intitule_metier": "Production et exploitation de systèmes d'information",
        "statut": "stable", "taux_tension_territorial": 45.0,
        "competences_core": ["Supervision", "Bash", "Monitoring", "Docker"],
        "competences_emergentes": ["Kubernetes", "GitOps", "FinOps", "Observabilité"],
        "competences_en_declin": [],
        "soft_skills_prioritaires": ["rigueur", "résistance au stress"],
        "trajectoires_compatibles": ["M1802", "M1805"],
    },
    {
        "code_rome": "H2604", "intitule_metier": "Montage de structures métalliques",
        "statut": "en_croissance", "taux_tension_territorial": 71.0,
        "competences_core": ["Soudage TIG", "Lecture de plans", "CACES R486"],
        "competences_emergentes": ["Soudage robotisé", "Lecture plans BIM"],
        "competences_en_declin": [],
        "soft_skills_prioritaires": ["précision", "sécurité au travail", "esprit d'équipe"],
        "trajectoires_compatibles": ["H2901"],
    },
    {
        "code_rome": "K1302", "intitule_metier": "Action sociale",
        "statut": "stable", "taux_tension_territorial": 38.0,
        "competences_core": ["Écoute active", "Médiation", "Connaissance RSA"],
        "competences_emergentes": ["Insertion numérique", "Démarches dématérialisées"],
        "competences_en_declin": [],
        "soft_skills_prioritaires": ["empathie", "discrétion", "gestion de conflits"],
        "trajectoires_compatibles": ["K1201"],
    },
    {
        "code_rome": "K2204", "intitule_metier": "Nettoyage de locaux",
        "statut": "en_declin", "taux_tension_territorial": 15.0,
        "competences_core": ["Hygiène HACCP", "Auto-laveuse"],
        "competences_emergentes": ["Produits écologiques"],
        "competences_en_declin": ["Produits chimiques chlorés"],
        "soft_skills_prioritaires": ["ponctualité", "discrétion"],
        "trajectoires_compatibles": [],
    },
    {
        "code_rome": "J1506", "intitule_metier": "Soins infirmiers généralistes",
        "statut": "en_transformation", "taux_tension_territorial": 88.0,
        "competences_core": ["Pose de perfusion", "Dossier patient informatisé", "Pharmacologie"],
        "competences_emergentes": ["Télésurveillance", "IA d'aide au diagnostic", "Coordination de parcours"],
        "competences_en_declin": [],
        "soft_skills_prioritaires": ["empathie", "résistance émotionnelle", "travail en équipe"],
        "trajectoires_compatibles": ["J1501"],
    },
    {
        "code_rome": "N1101", "intitule_metier": "Conduite d'engins de déplacement des charges",
        "statut": "emergent", "taux_tension_territorial": 56.0,
        "competences_core": ["CACES R489", "Sécurité entrepôt", "Inventaire"],
        "competences_emergentes": ["WMS connecté", "AGV supervision", "Tablette PDA"],
        "competences_en_declin": [],
        "soft_skills_prioritaires": ["vigilance", "ponctualité"],
        "trajectoires_compatibles": [],
    },
]


# ─── Offres d'emploi ───────────────────────────────────────────────────────

OFFRES_TEMPLATES = [
    ("M1805", "Développeur(se) Full-Stack Python/React", "Metz", "CDI", "informatique",
     ["Python", "React", "PostgreSQL", "Git", "Docker"], ["LLM", "RAG", "TypeScript"]),
    ("M1805", "Ingénieur(e) data IA", "Strasbourg", "CDI", "informatique",
     ["Python", "SQL", "Pandas"], ["RAG", "LangChain", "MLOps"]),
    ("M1802", "Technicien support N2", "Nancy", "CDI", "informatique",
     ["Active Directory", "Linux", "ITIL"], ["Zero Trust"]),
    ("M1810", "Devops engineer", "Reims", "CDI", "informatique",
     ["Docker", "Kubernetes", "Bash"], ["GitOps", "FinOps"]),
    ("H2604", "Soudeur(se) TIG-MIG", "Mulhouse", "CDI", "industrie",
     ["Soudage TIG", "Lecture de plans"], ["Soudage robotisé"]),
    ("H2604", "Chaudronnier(e) soudeur", "Thionville", "CDD", "industrie",
     ["Soudage", "Pliage"], []),
    ("J1506", "Infirmier(e) DE bloc", "Strasbourg", "CDI", "sante",
     ["Bloc opératoire", "Stérilisation"], ["Coordination parcours"]),
    ("J1506", "Infirmier(e) coordinateur télésurveillance", "Metz", "CDI", "sante",
     ["Dossier patient", "Pharmacologie"], ["Télésurveillance", "IA diagnostic"]),
    ("K1302", "Conseiller(e) en insertion sociale", "Nancy", "CDD", "social",
     ["Médiation", "Écoute active"], ["Insertion numérique"]),
    ("K2204", "Agent(e) d'entretien", "Reims", "CDI", "services",
     ["Auto-laveuse", "Hygiène HACCP"], ["Produits écologiques"]),
    ("N1101", "Cariste 5 CACES", "Mulhouse", "interim", "logistique",
     ["CACES R489", "Inventaire"], ["WMS connecté"]),
    ("N1101", "Préparateur(trice) commandes", "Strasbourg", "CDD", "logistique",
     ["CACES R489", "Sécurité entrepôt"], ["Tablette PDA"]),
]


# ─── Profils ───────────────────────────────────────────────────────────────

PROFILS_DEMO = [
    {
        "user_id": "user_demo_001",
        "metier_vise": "Développeur Full-Stack Python/React",
        "metier_exerce": "Technicien helpdesk",
        "code_rome_vise": "M1805",
        "code_rome_exerce": "M1802",
        "diplomes": ["Bac+2 SIO"],
        "annees_experience": 3,
        "competences_techniques": ["Python", "JavaScript", "Git", "SQL"],
        "soft_skills": ["autonomie", "rigueur", "communication"],
        "soft_skills_prouves": ["autonomie", "rigueur"],
        "valeurs_professionnelles": ["impact", "apprentissage"],
        "freins_emploi": [],
        "projet_reconversion": "Devenir développeur full-stack et travailler sur des projets à impact",
        "formations_envisagees": ["Bootcamp React", "Formation Cloud GCP"],
        "resultats_dclic": {"profil_disc": "C/I", "moteurs_riasec": ["Investigatif", "Réaliste"]},
    },
    {
        "user_id": "user_demo_002",
        "metier_vise": "Soudeur TIG",
        "metier_exerce": "Manutentionnaire",
        "code_rome_vise": "H2604",
        "code_rome_exerce": "N1103",
        "diplomes": ["CAP Métallerie"],
        "annees_experience": 5,
        "competences_techniques": ["Soudage à l'arc", "Lecture de plans"],
        "soft_skills": ["précision", "esprit d'équipe"],
        "soft_skills_prouves": ["précision"],
        "freins_emploi": ["mobilité limitée"],
        "projet_reconversion": "Évoluer vers soudage TIG et travailler sur chantiers BIM",
        "formations_envisagees": ["Habilitation soudage TIG"],
    },
    {
        "user_id": "user_demo_003",
        "metier_vise": "Infirmier coordinateur télésurveillance",
        "metier_exerce": "Infirmier généraliste",
        "code_rome_vise": "J1506",
        "code_rome_exerce": "J1506",
        "diplomes": ["DE Infirmier"],
        "annees_experience": 8,
        "competences_techniques": ["Pose de perfusion", "Dossier patient informatisé", "Pharmacologie"],
        "soft_skills": ["empathie", "travail en équipe", "résistance émotionnelle"],
        "soft_skills_prouves": ["empathie", "résistance émotionnelle"],
        "freins_emploi": [],
        "projet_reconversion": None,
    },
    {
        "user_id": "user_demo_004",
        "metier_vise": "Cariste",
        "code_rome_vise": "N1101",
        "diplomes": ["CAP Logistique"],
        "annees_experience": 2,
        "competences_techniques": ["CACES R489"],
        "soft_skills": ["vigilance", "ponctualité"],
        "soft_skills_prouves": ["ponctualité"],
        "freins_emploi": ["pas de permis B", "garde d'enfants"],
        "projet_reconversion": None,
    },
    {
        "user_id": "user_demo_005",
        "metier_vise": "Conseiller en insertion sociale",
        "code_rome_vise": "K1302",
        "diplomes": ["DEJEPS"],
        "annees_experience": 4,
        "competences_techniques": ["Écoute active", "Médiation"],
        "soft_skills": ["empathie", "discrétion"],
        "soft_skills_prouves": ["empathie"],
        "freins_emploi": ["temps partiel uniquement"],
        "projet_reconversion": None,
    },
]


# ─── Entreprises ───────────────────────────────────────────────────────────

ENTREPRISES_DEMO = [
    {
        "entreprise_id": "ent_demo_001",
        "secteur": "informatique",
        "taille": "PME",
        "fiches_poste": [
            {"intitule": "Dev Full-Stack", "code_rome": "M1805", "niveau": "confirmé"},
            {"intitule": "Ingénieur data", "code_rome": "M1805", "niveau": "senior"}
        ],
        "competences_attendues": ["Python", "React", "Cloud", "LLM"],
        "metiers_en_tension": ["Développeur Full-Stack Python/React", "Ingénieur data IA"],
        "besoins_recrutement": [
            {"metier": "Développeur Full-Stack Python/React", "nb_postes": 4, "horizon_mois": 6},
            {"metier": "Ingénieur data IA", "nb_postes": 2, "horizon_mois": 12}
        ],
        "competences_manquantes": ["LLM prompting", "RAG", "Cloud GCP"],
        "evolutions_internes": ["Plan de formation IA générative 2026"],
        "sorties_salaries": [],
        "besoins_gepp": "Anticipation des mutations IA — montée en compétences de l'équipe sur LLM/RAG d'ici 12 mois",
    },
    {
        "entreprise_id": "ent_demo_002",
        "secteur": "industrie",
        "taille": "ETI",
        "fiches_poste": [
            {"intitule": "Soudeur TIG", "code_rome": "H2604", "niveau": "confirmé"}
        ],
        "competences_attendues": ["Soudage TIG", "Lecture plans BIM"],
        "metiers_en_tension": ["Soudeur TIG"],
        "besoins_recrutement": [
            {"metier": "Soudeur TIG", "nb_postes": 6, "horizon_mois": 6}
        ],
        "competences_manquantes": ["Soudage robotisé", "Lecture plans BIM"],
        "besoins_gepp": "Recrutement urgent — 6 soudeurs TIG en région Mulhouse / Thionville",
    },
]


# ─── Formations ────────────────────────────────────────────────────────────

FORMATIONS_DEMO = [
    {
        "intitule": "Bootcamp Développeur Full-Stack Python/React",
        "organisme": "WildCode Strasbourg",
        "prerequis": ["Notions de programmation"],
        "blocs_competences": ["Python", "React", "SQL", "Git", "Docker"],
        "certifications": ["Titre RNCP Développeur Web"],
        "taux_insertion": 78.0,
        "duree_heures": 700,
        "cout_euros": 8500,
        "financements_possibles": ["CPF", "Pôle Emploi", "Région Grand Est"],
        "localisation": "Strasbourg",
        "code_departement": "67",
        "modalites": ["presentiel", "hybride"],
        "metiers_vises": ["Développeur Full-Stack Python/React"],
        "codes_rome": ["M1805"]
    },
    {
        "intitule": "Spécialisation IA générative & RAG",
        "organisme": "DataScientest",
        "prerequis": ["Python avancé"],
        "blocs_competences": ["LLM prompting", "RAG", "LangChain", "Cloud GCP"],
        "certifications": ["Certificat IA générative"],
        "taux_insertion": 82.0,
        "duree_heures": 200,
        "cout_euros": 3800,
        "financements_possibles": ["CPF", "OPCO"],
        "localisation": "Metz",
        "modalites": ["distanciel"],
        "metiers_vises": ["Ingénieur data IA", "Développeur Full-Stack Python/React"],
        "codes_rome": ["M1805"]
    },
    {
        "intitule": "Habilitation Soudage TIG / MIG",
        "organisme": "AFPA Mulhouse",
        "prerequis": ["CAP Métallerie"],
        "blocs_competences": ["Soudage TIG", "Soudage robotisé", "Lecture de plans"],
        "certifications": ["Habilitation soudage TIG"],
        "taux_insertion": 89.0,
        "duree_heures": 450,
        "cout_euros": 5200,
        "financements_possibles": ["CPF", "FSE", "Région Grand Est"],
        "localisation": "Mulhouse",
        "code_departement": "68",
        "modalites": ["presentiel", "alternance"],
        "metiers_vises": ["Soudeur TIG"],
        "codes_rome": ["H2604"]
    },
    {
        "intitule": "Coordination parcours patient & télésurveillance",
        "organisme": "Université de Lorraine",
        "prerequis": ["DE Infirmier"],
        "blocs_competences": ["Télésurveillance", "Coordination parcours", "Pharmacologie"],
        "certifications": ["DU Coordination parcours"],
        "taux_insertion": 92.0,
        "duree_heures": 120,
        "cout_euros": 2400,
        "financements_possibles": ["CPF", "Plan de développement employeur"],
        "localisation": "Nancy",
        "modalites": ["hybride"],
        "metiers_vises": ["Infirmier coordinateur télésurveillance"],
        "codes_rome": ["J1506"]
    },
    {
        "intitule": "CACES R489 catégories 1-3-5",
        "organisme": "AFTRAL Reims",
        "prerequis": [],
        "blocs_competences": ["CACES R489", "Sécurité entrepôt", "WMS connecté"],
        "certifications": ["CACES R489 1/3/5"],
        "taux_insertion": 85.0,
        "duree_heures": 70,
        "cout_euros": 1300,
        "financements_possibles": ["CPF", "Pôle Emploi"],
        "localisation": "Reims",
        "modalites": ["presentiel"],
        "metiers_vises": ["Cariste"],
        "codes_rome": ["N1101"]
    },
]


# ─── Observations terrain ──────────────────────────────────────────────────

TERRAIN_DEMO = [
    {
        "type_source": "conseiller_emploi",
        "observation": "Trois candidats ont été retenus chez ent_demo_001 suite à l'atelier IA générative — l'enjeu RAG est désormais central.",
        "metier_concerne": "M1805",
        "competences_mentionnees": ["RAG", "LLM prompting", "Python"],
        "soft_skills_mentionnes": ["autonomie", "veille technologique"],
        "facteur_succes": "Atelier RAG en groupe",
        "tags": ["informatique"]
    },
    {
        "type_source": "recruteur",
        "observation": "Difficile de trouver des soudeurs TIG capables de lire des plans BIM — formation à anticiper.",
        "metier_concerne": "H2604",
        "competences_mentionnees": ["Soudage TIG", "Lecture plans BIM"],
        "soft_skills_mentionnes": ["précision"],
        "facteur_echec": "Plans BIM peu maîtrisés",
        "tags": ["industrie"]
    },
    {
        "type_source": "formateur",
        "observation": "Les stagiaires infirmiers en télésurveillance progressent rapidement quand on combine présentiel et e-learning.",
        "metier_concerne": "J1506",
        "competences_mentionnees": ["Télésurveillance", "Coordination parcours"],
        "soft_skills_mentionnes": ["empathie"],
        "facteur_succes": "Modalité hybride",
        "tags": ["sante"]
    },
    {
        "type_source": "atelier_vsi",
        "observation": "Trois personnes ont validé leur projet de reconversion vers le numérique après l'atelier VSI PRO de mars.",
        "metier_concerne": "M1805",
        "competences_mentionnees": ["Python", "Git"],
        "soft_skills_mentionnes": ["autonomie", "communication"],
        "tags": ["informatique"]
    },
    {
        "type_source": "recruteur",
        "observation": "Les caristes recrutés cette année manquent souvent de pratique du WMS — module dédié à prévoir.",
        "metier_concerne": "N1101",
        "competences_mentionnees": ["CACES R489", "WMS connecté"],
        "tags": ["logistique"]
    },
    {
        "type_source": "bilan_pmsmp",
        "observation": "Bilan positif : la PMSMP a permis à user_demo_005 de confirmer son projet en insertion sociale.",
        "metier_concerne": "K1302",
        "competences_mentionnees": ["Écoute active", "Insertion numérique"],
        "soft_skills_mentionnes": ["empathie", "discrétion"],
        "tags": ["social"]
    },
]


# ─── Parcours ──────────────────────────────────────────────────────────────

PARCOURS_DEMO = [
    {
        "user_id": "user_demo_001",
        "date_debut_accompagnement": datetime.now(timezone.utc) - timedelta(days=180),
        "candidatures_envoyees": 22,
        "entretiens_obtenus": 8,
        "retours_employeurs": ["Profil intéressant, manque expérience React", "Très motivé"],
        "emploi_retrouve": True,
        "emploi_metier": "Développeur Full-Stack Python/React",
        "emploi_code_rome": "M1805",
        "formation_commencee": True,
        "formation_intitule": "Bootcamp Développeur Full-Stack Python/React",
        "maintien_3mois": True,
        "maintien_6mois": True,
        "maintien_12mois": None
    },
    {
        "user_id": "user_demo_002",
        "date_debut_accompagnement": datetime.now(timezone.utc) - timedelta(days=120),
        "candidatures_envoyees": 12,
        "entretiens_obtenus": 3,
        "emploi_retrouve": False,
        "formation_commencee": True,
        "formation_intitule": "Habilitation Soudage TIG / MIG",
        "maintien_3mois": None,
    },
    {
        "user_id": "user_demo_003",
        "date_debut_accompagnement": datetime.now(timezone.utc) - timedelta(days=400),
        "candidatures_envoyees": 5,
        "entretiens_obtenus": 4,
        "emploi_retrouve": True,
        "emploi_metier": "Infirmier coordinateur télésurveillance",
        "emploi_code_rome": "J1506",
        "maintien_3mois": True,
        "maintien_6mois": True,
        "maintien_12mois": True
    },
    {
        "user_id": "user_demo_004",
        "candidatures_envoyees": 8,
        "entretiens_obtenus": 1,
        "emploi_retrouve": False,
        "maintien_3mois": False,
    },
    {
        "user_id": "user_demo_005",
        "candidatures_envoyees": 15,
        "entretiens_obtenus": 5,
        "emploi_retrouve": True,
        "emploi_metier": "Conseiller en insertion sociale",
        "emploi_code_rome": "K1302",
        "maintien_3mois": True,
        "maintien_6mois": False,
    },
]


# ─── Données institutionnelles ─────────────────────────────────────────────

INSTITUTIONNEL_DEMO = [
    {
        "source": "france_travail",
        "type_donnee": "tension_recrutement",
        "titre": "Baromètre BMO Grand Est 2026 — informatique & industrie",
        "contenu": {"informatique": 78, "industrie": 71, "sante": 88, "logistique": 56},
        "periode_reference": "2026-T1",
        "metiers_concernes": ["M1805", "H2604", "J1506", "N1101"],
        "secteurs_concernes": ["informatique", "industrie", "sante", "logistique"]
    },
    {
        "source": "insee",
        "type_donnee": "statistique",
        "titre": "Démographie active Grand Est",
        "contenu": {"population_active": 2381000, "taux_chomage_pct": 6.9},
        "periode_reference": "2025-T4",
    },
    {
        "source": "carif_oref",
        "type_donnee": "cartographie",
        "titre": "Offre de formation continue Grand Est",
        "contenu": {"nb_formations_certifiantes": 4250, "nb_organismes": 1180},
        "periode_reference": "2026",
    },
    {
        "source": "dares",
        "type_donnee": "prevision",
        "titre": "Métiers en transformation à 5 ans",
        "contenu": {"transformation": ["IT", "santé"], "declin": ["nettoyage manuel"]},
        "periode_reference": "2026-2031",
    },
]


async def seed_if_empty():
    """Seed les 8 collections si la BDD est vide. Idempotent."""
    if await col_referentiels().count_documents({}) > 0:
        print("[OPC] Seed déjà présent — skip")
        return False

    print("[OPC] Seed démo Grand Est en cours...")

    # Référentiels
    for r in REFERENTIELS:
        doc = {
            **r,
            "horizon_prevision": "3_ans",
            "score_confiance_ia": 0.78,
            "derniere_maj": datetime.now(timezone.utc),
            "territoire": "Grand Est",
            "validation": _val(source="moteur_ia_opc", fiabilite="haute", niveau="infere")
        }
        await col_referentiels().update_one(
            {"code_rome": doc["code_rome"]}, {"$set": doc}, upsert=True
        )

    # Profils
    for p in PROFILS_DEMO:
        doc = {**p, "territoire": "Grand Est",
               "validation": _val(source="apply_vsi_pro", fiabilite="haute",
                                  niveau="prouve" if p.get("soft_skills_prouves") else "declare")}
        await col_profils().update_one(
            {"user_id": doc["user_id"]}, {"$set": doc}, upsert=True
        )

    # Entreprises
    for e in ENTREPRISES_DEMO:
        doc = {**e, "territoire": "Grand Est",
               "validation": _val(source="espace_entreprise", fiabilite="haute",
                                  secteur=e.get("secteur"))}
        await col_entreprises().update_one(
            {"entreprise_id": doc["entreprise_id"]}, {"$set": doc}, upsert=True
        )

    # Offres
    offres_to_insert = []
    rng = random.Random(42)
    for code_rome, intitule, loc, contrat, secteur, demandees, emergents in OFFRES_TEMPLATES:
        for _ in range(rng.randint(2, 5)):
            offres_to_insert.append({
                "source": "france_travail",
                "intitule_poste": intitule,
                "code_rome": code_rome,
                "competences_demandees": demandees,
                "mots_cles_emergents": emergents,
                "salaire_min": rng.choice([24000, 28000, 32000, 38000, 42000]),
                "salaire_max": rng.choice([35000, 42000, 52000, 58000, 65000]),
                "localisation": f"{loc} (Grand Est)",
                "code_departement": {"Metz": "57", "Strasbourg": "67", "Nancy": "54",
                                     "Reims": "51", "Mulhouse": "68", "Thionville": "57"}.get(loc),
                "niveau_experience_requis": rng.choice(["junior", "confirmé", "senior"]),
                "type_contrat": contrat,
                "secteur": secteur,
                "date_publication": datetime.now(timezone.utc) - timedelta(days=rng.randint(1, 45)),
                "validation": _val(source="france_travail", fiabilite="haute",
                                   secteur=secteur, niveau="prouve")
            })
    if offres_to_insert:
        await col_offres().insert_many(offres_to_insert)

    # Formations
    for f in FORMATIONS_DEMO:
        f = {**f, "localisation": f"{f['localisation']} (Grand Est)"}
        doc = {**f, "validation": _val(source="carif_oref", fiabilite="haute", niveau="prouve")}
        await col_formations().update_one(
            {"intitule": doc["intitule"], "organisme": doc["organisme"],
             "localisation": doc["localisation"]},
            {"$set": doc}, upsert=True
        )

    # Terrain
    for t in TERRAIN_DEMO:
        doc = {**t, "territoire": "Grand Est", "sentiment": "positif" if "succes" in t else "neutre",
               "validation": _val(source="terrain_conseiller", fiabilite="moyenne",
                                  metier=t.get("metier_concerne"))}
        await col_terrain().insert_one(doc)

    # Parcours
    for p in PARCOURS_DEMO:
        doc = {**p, "territoire": "Grand Est",
               "validation": _val(source="apply_vsi_pro", fiabilite="haute",
                                  consentement=True, niveau="prouve")}
        await col_parcours().update_one(
            {"user_id": doc["user_id"]}, {"$set": doc}, upsert=True
        )

    # Institutionnel
    for i in INSTITUTIONNEL_DEMO:
        doc = {**i, "territoire": "Grand Est",
               "_ingested_at": datetime.now(timezone.utc),
               "validation": _val(source=i["source"], fiabilite="haute", niveau="prouve")}
        await col_institutionnel().insert_one(doc)

    print(f"[OPC] Seed terminé : {len(REFERENTIELS)} référentiels, "
          f"{len(PROFILS_DEMO)} profils, {len(OFFRES_TEMPLATES)} familles d'offres, "
          f"{len(FORMATIONS_DEMO)} formations, {len(TERRAIN_DEMO)} observations.")
    return True
