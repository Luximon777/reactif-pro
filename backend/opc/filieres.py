"""
OPC — Mapping Filière / Secteur d'activité / Métier (ROME)
Référence : familles ROME 4 (France Travail) regroupées par filière professionnelle.
"""

# ─── Filières professionnelles ───────────────────────────────────────────
# Une filière = un grand domaine d'emploi qui regroupe plusieurs secteurs.

FILIERES = {
    "numerique": {
        "label": "Numérique & Données",
        "secteurs": ["informatique", "telecom", "data"],
        "rome_prefixes": ["M18"],  # M1801-M1810
    },
    "industrie": {
        "label": "Industrie & Production",
        "secteurs": ["industrie", "metallurgie", "automobile", "aeronautique"],
        "rome_prefixes": ["H"],  # H1-H3
    },
    "sante": {
        "label": "Santé & Médico-social",
        "secteurs": ["sante", "medico_social"],
        "rome_prefixes": ["J"],
    },
    "social": {
        "label": "Services à la personne & Action sociale",
        "secteurs": ["social", "education", "services"],
        "rome_prefixes": ["K1", "K2"],
    },
    "logistique": {
        "label": "Transport & Logistique",
        "secteurs": ["logistique", "transport"],
        "rome_prefixes": ["N1", "N4"],
    },
    "btp": {
        "label": "BTP & Construction",
        "secteurs": ["btp", "construction"],
        "rome_prefixes": ["F"],
    },
    "commerce": {
        "label": "Commerce & Distribution",
        "secteurs": ["commerce", "distribution", "vente"],
        "rome_prefixes": ["D"],
    },
    "hotellerie": {
        "label": "Hôtellerie-Restauration-Tourisme",
        "secteurs": ["hotellerie", "restauration", "tourisme"],
        "rome_prefixes": ["G"],
    },
    "tertiaire": {
        "label": "Banque, Finance & Assurance",
        "secteurs": ["banque", "finance", "assurance"],
        "rome_prefixes": ["C"],
    },
    "support": {
        "label": "Pilotage & Support d'entreprise",
        "secteurs": ["administratif", "rh", "management"],
        "rome_prefixes": ["M11", "M12", "M13", "M14", "M15", "M16", "M17"],
    },
}


def filiere_pour_rome(code_rome: str) -> tuple[str, str]:
    """Retourne (filiere_key, filiere_label) pour un code ROME."""
    if not code_rome:
        return ("autre", "Autre")
    for key, f in FILIERES.items():
        for prefix in f["rome_prefixes"]:
            if code_rome.upper().startswith(prefix):
                return (key, f["label"])
    return ("autre", "Autre")


def secteur_principal_filiere(filiere_key: str) -> str:
    """Renvoie le secteur principal d'une filière (utile pour filtrer)."""
    f = FILIERES.get(filiere_key)
    return f["secteurs"][0] if f and f.get("secteurs") else ""
