"""
OPC — Schémas Pydantic v2
8 collections correspondant aux 8 flux d'alimentation.
"""

from datetime import datetime, timezone
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class ValidationMeta(BaseModel):
    """Métadonnées de validation RGPD — obligatoire sur chaque document."""
    source: str
    date_collecte: datetime = Field(default_factory=_now_utc)
    fiabilite: Literal["haute", "moyenne", "faible"] = "moyenne"
    territoire: str = "Grand Est"
    secteur: Optional[str] = None
    metier_concerne: Optional[str] = None
    niveau_preuve: Literal["prouve", "declare", "infere"] = "declare"
    consentement_rgpd: bool = False
    anonymise: bool = True


# ─── FLUX 1 — Profils utilisateurs ───────────────────────────────────────────

class ProfilUtilisateur(BaseModel):
    model_config = ConfigDict(extra="ignore")

    user_id: str
    metier_vise: Optional[str] = None
    metier_exerce: Optional[str] = None
    code_rome_vise: Optional[str] = None
    code_rome_exerce: Optional[str] = None
    diplomes: List[str] = []
    annees_experience: Optional[int] = None
    competences_techniques: List[str] = []
    soft_skills: List[str] = []
    soft_skills_prouves: List[str] = []
    valeurs_professionnelles: List[str] = []
    freins_emploi: List[str] = []
    projet_reconversion: Optional[str] = None
    formations_envisagees: List[str] = []
    resultats_dclic: Optional[dict] = None
    territoire: str = "Grand Est"
    validation: ValidationMeta


# ─── FLUX 2 — Données entreprises ────────────────────────────────────────────

class DonneeEntreprise(BaseModel):
    model_config = ConfigDict(extra="ignore")

    entreprise_id: str
    secteur: str
    taille: Optional[Literal["TPE", "PME", "ETI", "GE"]] = None
    fiches_poste: List[dict] = []
    competences_attendues: List[str] = []
    metiers_en_tension: List[str] = []
    besoins_recrutement: List[dict] = []
    competences_manquantes: List[str] = []
    evolutions_internes: List[str] = []
    sorties_salaries: List[dict] = []
    besoins_gepp: Optional[str] = None
    territoire: str = "Grand Est"
    validation: ValidationMeta


# ─── FLUX 3 — Offres d'emploi ────────────────────────────────────────────────

class OffreEmploi(BaseModel):
    model_config = ConfigDict(extra="ignore")

    source: Literal["france_travail", "eures", "orient_est", "scraping", "partenaire"]
    intitule_poste: str
    code_rome: Optional[str] = None
    competences_demandees: List[str] = []
    mots_cles_emergents: List[str] = []
    salaire_min: Optional[float] = None
    salaire_max: Optional[float] = None
    localisation: str
    code_departement: Optional[str] = None
    niveau_experience_requis: Optional[str] = None
    type_contrat: Optional[Literal["CDI", "CDD", "interim", "apprentissage", "stage", "autre"]] = None
    secteur: str
    date_publication: datetime = Field(default_factory=_now_utc)
    validation: ValidationMeta


# ─── FLUX 4 — Formations ─────────────────────────────────────────────────────

class Formation(BaseModel):
    model_config = ConfigDict(extra="ignore")

    intitule: str
    organisme: str
    prerequis: List[str] = []
    blocs_competences: List[str] = []
    certifications: List[str] = []
    taux_insertion: Optional[float] = None
    duree_heures: Optional[int] = None
    cout_euros: Optional[float] = None
    financements_possibles: List[str] = []
    localisation: str
    code_departement: Optional[str] = None
    modalites: List[Literal["presentiel", "distanciel", "alternance", "hybride"]] = []
    metiers_vises: List[str] = []
    codes_rome: List[str] = []
    validation: ValidationMeta


# ─── FLUX 5 — Données institutionnelles ──────────────────────────────────────

class DonneeInstitutionnelle(BaseModel):
    model_config = ConfigDict(extra="ignore")

    source: Literal["france_travail", "rome_4", "orient_est", "carif_oref",
                    "insee", "dares", "region_grand_est", "opco", "eures"]
    type_donnee: Literal["statistique", "referentiel", "cartographie",
                         "prevision", "tension_recrutement"]
    titre: str
    contenu: dict
    periode_reference: Optional[str] = None
    territoire: str = "Grand Est"
    metiers_concernes: List[str] = []
    secteurs_concernes: List[str] = []
    validation: ValidationMeta


# ─── FLUX 6 — Données terrain ─────────────────────────────────────────────────

class DonneeTerrain(BaseModel):
    model_config = ConfigDict(extra="ignore")

    type_source: Literal["conseiller_emploi", "atelier_vsi", "formateur",
                         "recruteur", "bilan_pmsmp", "retour_entretien", "autre"]
    observation: str
    metier_concerne: Optional[str] = None
    competences_mentionnees: List[str] = []
    soft_skills_mentionnes: List[str] = []
    sentiment: Optional[Literal["positif", "negatif", "neutre"]] = None
    facteur_succes: Optional[str] = None
    facteur_echec: Optional[str] = None
    territoire: str = "Grand Est"
    tags: List[str] = []
    validation: ValidationMeta


# ─── FLUX 7 — Suivi parcours ─────────────────────────────────────────────────

class SuiviParcours(BaseModel):
    model_config = ConfigDict(extra="ignore")

    user_id: str
    date_debut_accompagnement: Optional[datetime] = None
    evolution_cv: List[dict] = []
    candidatures_envoyees: int = 0
    entretiens_obtenus: int = 0
    retours_employeurs: List[str] = []
    emploi_retrouve: bool = False
    emploi_metier: Optional[str] = None
    emploi_code_rome: Optional[str] = None
    formation_commencee: bool = False
    formation_intitule: Optional[str] = None
    maintien_3mois: Optional[bool] = None
    maintien_6mois: Optional[bool] = None
    maintien_12mois: Optional[bool] = None
    territoire: str = "Grand Est"
    validation: ValidationMeta


# ─── FLUX 8 — Référentiels vivants ──────────────────────────────────────────

class ReferentielVivant(BaseModel):
    model_config = ConfigDict(extra="ignore")

    code_rome: str
    intitule_metier: str
    statut: Literal["en_croissance", "stable", "en_transformation",
                    "en_declin", "emergent"]
    competences_core: List[str] = []
    competences_emergentes: List[str] = []
    competences_en_declin: List[str] = []
    soft_skills_prioritaires: List[str] = []
    taux_tension_territorial: Optional[float] = None
    horizon_prevision: Literal["1_an", "3_ans", "5_ans", "10_ans"] = "3_ans"
    trajectoires_compatibles: List[str] = []
    score_confiance_ia: Optional[float] = None
    derniere_maj: datetime = Field(default_factory=_now_utc)
    territoire: str = "Grand Est"
    validation: ValidationMeta
