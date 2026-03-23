"""
Algorithme de Job Matching RE'ACTIF PRO
Basé sur le système de pondération à 5 niveaux avec critères bloquants
"""
import re

# Pondération par priorité (1-5)
WEIGHTS = {1: 1, 2: 3, 3: 5, 4: 7, 5: 10}

# Familles de métiers pour le matching approché
METIER_PROXIMITY = {
    "assistant administratif": ["agent administratif", "secrétaire administratif"],
    "agent administratif": ["assistant administratif", "employé administratif"],
    "secrétaire": ["assistant administratif", "secrétaire administratif"],
    "employé libre service": ["mise en rayon", "agent de rayon"],
    "téléconseiller": ["conseiller clientèle", "chargé de relation client"],
    "conseiller en insertion professionnelle": ["chargé d'accompagnement", "conseiller emploi", "chargé de mission insertion", "conseiller en évolution professionnelle"],
    "conseiller emploi": ["conseiller en insertion professionnelle", "chargé de placement"],
    "consultant en transition professionnelle": ["conseiller en évolution professionnelle", "coach emploi", "conseiller en insertion professionnelle"],
    "formateur": ["animateur de formation", "responsable pédagogique", "formateur pour adultes"],
    "chargé de recrutement": ["consultant rh", "responsable recrutement", "talent acquisition"],
}

METIER_FAMILIES = {
    "administratif": ["assistant administratif", "agent administratif", "secrétaire", "secrétaire administratif", "employé administratif"],
    "commerce": ["employé libre service", "mise en rayon", "agent de rayon", "vendeur", "commercial"],
    "relation_client": ["téléconseiller", "conseiller clientèle", "chargé de relation client", "chargé de clientèle"],
    "insertion_emploi": ["conseiller en insertion professionnelle", "conseiller emploi", "chargé d'accompagnement", "chargé de mission insertion", "médiateur emploi", "conseiller en évolution professionnelle", "consultant en transition professionnelle"],
    "formation": ["formateur", "animateur de formation", "responsable pédagogique", "ingénieur pédagogique", "formateur pour adultes"],
    "rh": ["chargé de recrutement", "consultant rh", "responsable rh", "gestionnaire rh", "chargé de développement rh"],
    "social": ["assistant social", "éducateur spécialisé", "conseiller en économie sociale", "travailleur social"],
    "informatique": ["développeur", "tech lead", "ingénieur logiciel", "administrateur système", "data analyst"],
}

SECTOR_GROUPS = [
    ["association", "social", "insertion", "formation", "économie sociale et solidaire"],
    ["commerce", "distribution", "vente", "grande distribution"],
    ["santé", "médico-social", "social", "paramédical"],
    ["administration", "public", "collectivité", "fonction publique"],
    ["informatique", "numérique", "tech", "digital", "logiciel"],
    ["industrie", "production", "manufacturing"],
    ["conseil", "consulting", "rh", "ressources humaines"],
    ["éducation", "enseignement", "formation professionnelle"],
]


def normalize(value):
    if value is None:
        return ""
    return str(value).strip().lower()


def normalize_array(value):
    if isinstance(value, list):
        return [normalize(v) for v in value if normalize(v)]
    if not value:
        return []
    return [normalize(value)]


def compare_metier(candidate_values, job_value):
    candidates = normalize_array(candidate_values)
    job = normalize(job_value)
    if not job or not candidates:
        return 0.5

    if job in candidates:
        return 1

    for c in candidates:
        if c in job or job in c:
            return 0.85

    for c in candidates:
        close = METIER_PROXIMITY.get(c, [])
        if job in close:
            return 0.7

    for family in METIER_FAMILIES.values():
        c_in = any(c in family for c in candidates)
        j_in = job in family
        if c_in and j_in:
            return 0.5

    return 0


def compare_secteur(candidate_values, job_value):
    candidates = normalize_array(candidate_values)
    job = normalize(job_value)
    if not job or not candidates:
        return 0.5

    if job in candidates:
        return 1

    for c in candidates:
        if c in job or job in c:
            return 0.8

    for group in SECTOR_GROUPS:
        c_in = any(c in group for c in candidates)
        j_in = job in group or any(g in job for g in group)
        if c_in and j_in:
            return 0.5

    return 0


def compare_contrat(candidate_values, job_value):
    candidates = normalize_array(candidate_values)
    job = normalize(job_value)
    if not candidates or not job:
        return 1
    return 1 if job in candidates else 0


def compare_temps_travail(candidate_value, job_value):
    c = normalize(candidate_value)
    j = normalize(job_value)
    if not c or c in ("indifférent", "indifferent"):
        return 1
    return 1 if c == j else 0


def compare_mobility(max_minutes, offered_minutes):
    if not isinstance(max_minutes, (int, float)) or not isinstance(offered_minutes, (int, float)):
        return 0.5
    if offered_minutes <= max_minutes:
        return 1
    if offered_minutes <= max_minutes + 10:
        return 0.5
    return 0


def compare_teletravail(candidate_value, job_has_remote):
    c = normalize(candidate_value)
    has = bool(job_has_remote)
    if not c or c == "non prioritaire":
        return 1
    if c in ("souhaité", "souhaite"):
        return 1 if has else 0.5
    if c in ("nécessaire", "necessaire"):
        return 1 if has else 0
    return 1


def compare_amenagement(candidate_value, job_allows):
    c = normalize(candidate_value)
    allows = bool(job_allows)
    if not c or c == "aucun":
        return 1
    if c == "souhaitable":
        return 1 if allows else 0.5
    if c in ("nécessaire", "necessaire"):
        return 1 if allows else 0
    return 1


def compare_restrictions(candidate_restrictions, job_conditions):
    if not candidate_restrictions:
        return 1
    checks = []
    if candidate_restrictions.get("port_charges_impossible"):
        checks.append(0 if job_conditions.get("port_charges") else 1)
    if candidate_restrictions.get("travail_nuit_impossible"):
        checks.append(0 if job_conditions.get("travail_nuit") else 1)
    if candidate_restrictions.get("accessibilite_necessaire"):
        acc = job_conditions.get("accessibilite_locaux")
        checks.append(1 if acc is True else (0 if acc is False else 0.5))
    if candidate_restrictions.get("horaires_stables_recherches"):
        checks.append(0 if job_conditions.get("horaires_decales") else 1)
    return min(checks) if checks else 1


def evaluate_criterion(label, priority, compatibility, blocking=False, reason_blocked="", warning_partial="", success_matched=""):
    weight = WEIGHTS.get(priority, 0)
    is_blocking = blocking and compatibility == 0
    return {
        "label": label,
        "priority": priority,
        "weight": weight,
        "compatibility": compatibility,
        "score": weight * compatibility,
        "blocking": is_blocking,
        "reason": reason_blocked if compatibility == 0 else "",
        "warning": warning_partial if 0 < compatibility < 1 else "",
        "success": success_matched if compatibility == 1 else "",
    }


def calculate_job_score(candidate_profile, job_offer):
    """
    Calcule le score de matching entre un profil candidat et une offre d'emploi.
    candidate_profile: dict avec clés comme metier, secteur, contrat, etc.
                       Chaque clé a {value, priority}
    job_offer: dict avec les champs de l'offre
    """
    evaluations = []

    # Métier
    if candidate_profile.get("metier"):
        c = candidate_profile["metier"]
        compat = compare_metier(c.get("value"), job_offer.get("metier", ""))
        evaluations.append(evaluate_criterion(
            "Métier visé", c.get("priority", 3), compat,
            blocking=c.get("priority", 3) >= 5,
            reason_blocked="Le métier proposé ne correspond pas au métier visé.",
            warning_partial="Le métier est proche mais pas identique.",
            success_matched="Le métier correspond à votre recherche."
        ))

    # Secteur
    if candidate_profile.get("secteur"):
        c = candidate_profile["secteur"]
        compat = compare_secteur(c.get("value"), job_offer.get("secteur", ""))
        evaluations.append(evaluate_criterion(
            "Secteur d'activité", c.get("priority", 3), compat,
            blocking=c.get("priority", 3) >= 5,
            reason_blocked="Le secteur n'est pas compatible.",
            warning_partial="Le secteur est proche ou acceptable.",
            success_matched="Le secteur correspond à vos préférences."
        ))

    # Contrat
    if candidate_profile.get("contrat"):
        c = candidate_profile["contrat"]
        compat = compare_contrat(c.get("value"), job_offer.get("contrat", ""))
        evaluations.append(evaluate_criterion(
            "Type de contrat", c.get("priority", 3), compat,
            blocking=c.get("priority", 3) >= 5,
            reason_blocked="Le type de contrat ne correspond pas.",
            success_matched="Le type de contrat correspond."
        ))

    # Temps de travail
    if candidate_profile.get("temps_travail"):
        c = candidate_profile["temps_travail"]
        compat = compare_temps_travail(c.get("value"), job_offer.get("temps_travail", ""))
        evaluations.append(evaluate_criterion(
            "Temps de travail", c.get("priority", 3), compat,
            blocking=c.get("priority", 3) >= 5,
            reason_blocked="Le temps de travail ne convient pas.",
            success_matched="Le temps de travail est compatible."
        ))

    # Mobilité
    if candidate_profile.get("trajet_max_minutes"):
        c = candidate_profile["trajet_max_minutes"]
        compat = compare_mobility(c.get("value", 60), job_offer.get("trajet_estime_minutes", 30))
        evaluations.append(evaluate_criterion(
            "Mobilité / trajet", c.get("priority", 3), compat,
            blocking=c.get("priority", 3) >= 5,
            reason_blocked="Le temps de trajet dépasse le maximum acceptable.",
            warning_partial="Le trajet dépasse légèrement le seuil souhaité.",
            success_matched="Le temps de trajet est compatible."
        ))

    # Télétravail
    if candidate_profile.get("teletravail"):
        c = candidate_profile["teletravail"]
        compat = compare_teletravail(c.get("value"), job_offer.get("teletravail", False))
        evaluations.append(evaluate_criterion(
            "Télétravail", c.get("priority", 2), compat,
            blocking=c.get("priority", 2) >= 5,
            reason_blocked="Le télétravail est indispensable mais absent.",
            warning_partial="Le télétravail est souhaité mais non proposé.",
            success_matched="Le télétravail correspond au besoin."
        ))

    # Aménagement
    if candidate_profile.get("amenagement_poste"):
        c = candidate_profile["amenagement_poste"]
        compat = compare_amenagement(c.get("value"), job_offer.get("amenagement_possible", False))
        evaluations.append(evaluate_criterion(
            "Aménagement de poste", c.get("priority", 3), compat,
            blocking=c.get("priority", 3) >= 5,
            reason_blocked="L'aménagement nécessaire n'est pas possible.",
            warning_partial="L'aménagement souhaité n'est pas garanti.",
            success_matched="L'aménagement semble possible."
        ))

    # Restrictions RQTH
    if candidate_profile.get("restrictions_fonctionnelles"):
        c = candidate_profile["restrictions_fonctionnelles"]
        compat = compare_restrictions(c.get("value", {}), {
            "port_charges": job_offer.get("port_charges", False),
            "travail_nuit": job_offer.get("travail_nuit", False),
            "accessibilite_locaux": job_offer.get("accessibilite_locaux"),
            "horaires_decales": job_offer.get("horaires_decales", False),
        })
        evaluations.append(evaluate_criterion(
            "Restrictions fonctionnelles", c.get("priority", 4), compat,
            blocking=c.get("priority", 4) >= 5,
            reason_blocked="Le poste n'est pas compatible avec certaines restrictions.",
            warning_partial="Certaines conditions nécessitent vérification.",
            success_matched="Les restrictions sont compatibles avec le poste."
        ))

    # Calcul du score final
    score_max = sum(e["weight"] for e in evaluations)
    score_obtained = sum(e["score"] for e in evaluations)
    final_score = round((score_obtained / score_max) * 100) if score_max > 0 else 0

    blocages = [{"critere": e["label"], "raison": e["reason"]} for e in evaluations if e["blocking"]]
    vigilances = [{"critere": e["label"], "message": e["warning"]} for e in evaluations if e["warning"]]
    points_forts = [{"critere": e["label"], "message": e["success"]} for e in evaluations if e["success"]]

    if blocages:
        statut = "Incompatible"
    elif final_score >= 90:
        statut = "Excellent match"
    elif final_score >= 75:
        statut = "Match pertinent"
    elif final_score >= 60:
        statut = "Match moyen"
    else:
        statut = "Faible compatibilité"

    return {
        "statut": statut,
        "score": final_score,
        "score_detail": {"obtenu": round(score_obtained, 1), "maximum": score_max},
        "blocages": blocages,
        "vigilances": vigilances,
        "points_forts": points_forts,
        "evaluations": evaluations,
    }
