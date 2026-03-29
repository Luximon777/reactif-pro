from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
import secrets
from datetime import datetime, timezone


class AnonymousToken(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    token: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    role: str = "particulier"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    profile_id: Optional[str] = None


class Profile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    token_id: str
    name: str = "Utilisateur Anonyme"
    role: str = "particulier"
    skills: List[Dict[str, Any]] = []
    strengths: List[str] = []
    gaps: List[str] = []
    experience_years: int = 0
    sectors: List[str] = []
    profile_score: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    # Anonymat & Pseudonymat fields
    pseudo: Optional[str] = None
    email_recovery: Optional[str] = None
    password_hash: Optional[str] = None
    auth_mode: str = "anonymous"  # anonymous, pseudo, certified
    identity_level: str = "none"  # none, verified, verified_plus
    visibility_level: str = "private"  # private, limited, public
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    consent_cgu: bool = False
    consent_privacy: bool = False
    consent_marketing: bool = False
    # Legal identity (FranceConnect - stored but hidden by default)
    legal_first_name: Optional[str] = None
    legal_last_name: Optional[str] = None
    birth_date: Optional[str] = None
    birth_place: Optional[str] = None
    # Real identity (shared when visibility_level = "limited")
    real_first_name: Optional[str] = None
    real_last_name: Optional[str] = None
    verified_at: Optional[str] = None
    last_identity_sync_at: Optional[str] = None
    # Entreprise fields
    company_name: Optional[str] = None
    siret: Optional[str] = None
    referent_first_name: Optional[str] = None
    referent_last_name: Optional[str] = None
    referent_function: Optional[str] = None
    company_verified: bool = False
    badge_insertion: bool = False
    charte_ethique_signed: bool = False
    charte_ethique_signed_at: Optional[str] = None
    # Partenaire fields
    structure_type: Optional[str] = None
    config_suivi_beneficiaires: bool = False
    config_acces_coffre_fort: bool = False
    config_co_construction: bool = False
    config_contribution_competences: bool = False
    config_signalement_besoins: bool = False
    # Profile completion
    profile_completion: int = 0
    # CV Nouvelle Generation fields
    target_job: Optional[str] = None
    city: Optional[str] = None
    mobility: Optional[str] = None
    contract_types: List[str] = []
    work_modes: List[str] = []
    summary: Optional[str] = None


class JobOffer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    company: str
    location: str
    contract_type: str
    salary_range: Optional[str] = None
    required_skills: List[str] = []
    description: str
    sector: str
    match_score: int = 0
    status: str = "active"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    created_by: Optional[str] = None


class LearningModule(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    duration: str
    level: str
    skills_developed: List[str] = []
    progress: int = 0
    category: str
    image_url: Optional[str] = None


class Beneficiary(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    status: str
    progress: int = 0
    skills_acquired: List[str] = []
    sector: str
    last_activity: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    partner_id: str


class CandidateSearchCriterion(BaseModel):
    model_config = ConfigDict(extra="ignore")
    value: Any = None
    priority: int = 3


class RqthEqthInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    status: str = "ne_souhaite_pas_repondre"
    disclosure: str = "non"
    priority: int = 1


class CandidateSearchProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    metier: Optional[CandidateSearchCriterion] = None
    secteur: Optional[CandidateSearchCriterion] = None
    contrat: Optional[CandidateSearchCriterion] = None
    temps_travail: Optional[CandidateSearchCriterion] = None
    trajet_max_minutes: Optional[CandidateSearchCriterion] = None
    teletravail: Optional[CandidateSearchCriterion] = None
    amenagement_poste: Optional[CandidateSearchCriterion] = None
    restrictions_fonctionnelles: Optional[CandidateSearchCriterion] = None
    rqth_eqth: Optional[RqthEqthInfo] = None
    ciblage_employeurs_inclusifs: Optional[CandidateSearchCriterion] = None
    accessibilite_metier_handicap: Optional[CandidateSearchCriterion] = None
    zone_geographique: Optional[CandidateSearchCriterion] = None
    distance_km: Optional[CandidateSearchCriterion] = None
    lieu_residence: Optional[CandidateSearchCriterion] = None
    salaire_minimum: Optional[CandidateSearchCriterion] = None


class CoffreDocument(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    token_id: str
    title: str
    category: str
    document_type: str
    file_name: str = ""
    file_url: Optional[str] = None
    file_size: int = 0
    mime_type: str = "application/pdf"
    date_document: Optional[str] = None
    metier_associe: Optional[str] = None
    secteur: Optional[str] = None
    competences_liees: List[str] = []
    description: Optional[str] = None
    privacy_level: str = "private"
    shared_with: List[str] = []
    share_expiry: Optional[str] = None
    date_expiration: Optional[str] = None
    is_expiring_soon: bool = False
    is_sensitive: bool = False
    source_ref: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    view_history: List[Dict[str, Any]] = []


class DocumentShare(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    shared_by: str
    shared_with_email: Optional[str] = None
    shared_with_role: Optional[str] = None
    access_token: str = Field(default_factory=lambda: secrets.token_urlsafe(16))
    expires_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    accessed_at: Optional[str] = None
    access_count: int = 0


class CreateDocumentRequest(BaseModel):
    title: str
    category: str
    document_type: str
    file_name: str
    file_url: Optional[str] = None
    date_document: Optional[str] = None
    metier_associe: Optional[str] = None
    secteur: Optional[str] = None
    competences_liees: List[str] = []
    description: Optional[str] = None
    privacy_level: str = "private"
    date_expiration: Optional[str] = None
    is_sensitive: bool = False


class SkillContribution(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contributor_id: str
    contribution_type: str = "nouvelle_competence"
    skill_name: str
    skill_description: Optional[str] = None
    related_job: Optional[str] = None
    related_sector: Optional[str] = None
    related_tools: List[str] = []
    context: Optional[str] = None
    status: str = "en_attente"
    ai_analysis: Optional[Dict[str, Any]] = None
    ai_score: float = 0.0
    human_validator: Optional[str] = None
    human_notes: Optional[str] = None
    similar_count: int = 1
    upvotes: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    validated_at: Optional[str] = None


class EmergingSkill(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    skill_name: str
    description: Optional[str] = None
    related_sectors: List[str] = []
    related_jobs: List[str] = []
    related_tools: List[str] = []
    emergence_score: float = 0.0
    growth_rate: float = 0.0
    mention_count: int = 0
    contributor_count: int = 0
    status: str = "emergente"
    first_detected: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CreateContributionRequest(BaseModel):
    contribution_type: str = "nouvelle_competence"
    skill_name: str
    skill_description: Optional[str] = None
    related_job: Optional[str] = None
    related_sector: Optional[str] = None
    related_tools: List[str] = []
    context: Optional[str] = None


class PassportCompetence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    nature: str = ""
    category: str = "technique"
    level: str = "intermediaire"
    experience_years: float = 0
    proof: Optional[str] = None
    source: str = "declaratif"
    is_emerging: bool = False
    components: Dict[str, int] = Field(default_factory=lambda: {
        "connaissance": 0, "cognition": 0, "conation": 0,
        "affection": 0, "sensori_moteur": 0
    })
    ccsp_pole: str = ""
    ccsp_degree: str = ""
    linked_qualites: List[str] = []
    linked_valeurs: List[str] = []
    linked_vertus: List[str] = []
    added_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PassportExperience(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    organization: str = ""
    description: str = ""
    skills_used: List[str] = []
    achievements: List[str] = []
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    experience_type: str = "professionnel"
    source: str = "declaratif"
    added_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Passport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    token_id: str
    professional_summary: str = ""
    career_project: str = ""
    motivations: List[str] = []
    compatible_environments: List[str] = []
    target_sectors: List[str] = []
    competences: List[Dict[str, Any]] = []
    experiences: List[Dict[str, Any]] = []
    learning_path: List[Dict[str, Any]] = []
    passerelles: List[Dict[str, Any]] = []
    completeness_score: int = 0
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sharing: Dict[str, Any] = Field(default_factory=lambda: {
        "is_public": False, "shared_sections": [], "shared_with": [], "share_expiry": None
    })


class AddCompetenceRequest(BaseModel):
    name: str
    nature: str = ""
    category: str = "technique"
    level: str = "intermediaire"
    experience_years: float = 0
    proof: Optional[str] = None
    components: Optional[Dict[str, int]] = None
    ccsp_pole: Optional[str] = None
    ccsp_degree: Optional[str] = None
    linked_qualites: List[str] = []
    linked_valeurs: List[str] = []
    linked_vertus: List[str] = []


class EvaluateCompetenceRequest(BaseModel):
    components: Dict[str, int]
    ccsp_pole: Optional[str] = None
    ccsp_degree: Optional[str] = None


class AddExperienceRequest(BaseModel):
    title: str
    organization: str = ""
    description: str = ""
    skills_used: List[str] = []
    achievements: List[str] = []
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    experience_type: str = "professionnel"


class UpdatePassportProfileRequest(BaseModel):
    professional_summary: Optional[str] = None
    career_project: Optional[str] = None
    motivations: Optional[List[str]] = None
    compatible_environments: Optional[List[str]] = None
    target_sectors: Optional[List[str]] = None


class SharePassportRequest(BaseModel):
    is_public: bool = False
    shared_sections: List[str] = []
    shared_with: List[str] = []
    share_expiry: Optional[str] = None


class CreateTokenRequest(BaseModel):
    role: str = "particulier"


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    skills: Optional[List[Dict[str, Any]]] = None
    experience_years: Optional[int] = None
    sectors: Optional[List[str]] = None
    target_job: Optional[str] = None
    city: Optional[str] = None
    mobility: Optional[str] = None
    contract_types: Optional[List[str]] = None
    work_modes: Optional[List[str]] = None
    summary: Optional[str] = None


class CreateJobRequest(BaseModel):
    title: str
    company: str
    location: str
    contract_type: str
    salary_range: Optional[str] = None
    required_skills: List[str] = []
    description: str
    sector: str


class CvTextPayload(BaseModel):
    text: str
    filename: str = "cv.txt"
    selected_models: List[str] = ["classique", "competences", "fonctionnel", "mixte"]


class CvBase64Payload(BaseModel):
    data: str
    filename: str = "cv.pdf"


class UbuntooExchange(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exchange_type: str
    content_summary: str
    detected_skills: List[str] = []
    detected_tools: List[str] = []
    detected_practices: List[str] = []
    related_jobs: List[str] = []
    related_sectors: List[str] = []
    author_role: str = "professionnel"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class UbuntooSignal(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str
    name: str
    description: str
    mention_count: int = 1
    first_detected: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_detected: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    related_jobs: List[str] = []
    related_sectors: List[str] = []
    source_exchanges_count: int = 1
    trend_direction: str = "hausse"
    growth_rate: float = 0.0
    validation_status: str = "detectee"
    ai_confidence: float = 0.0
    ai_analysis: Optional[Dict[str, Any]] = None
    human_validator: Optional[str] = None
    human_notes: Optional[str] = None
    linked_observatory_skills: List[str] = []
    linked_evolution_jobs: List[str] = []
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class UbuntooInsight(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    insight_type: str
    title: str
    description: str
    supporting_signals: List[str] = []
    impacted_jobs: List[str] = []
    impacted_sectors: List[str] = []
    recommendation: str = ""
    priority: str = "moyenne"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())



# ===== Anonymat & Pseudonymat Models =====

class RegisterRequest(BaseModel):
    pseudo: str
    password: str
    role: str = "particulier"
    email_recovery: Optional[str] = None
    consent_cgu: bool = True
    consent_privacy: bool = True
    consent_marketing: bool = False


class LoginRequest(BaseModel):
    pseudo: str
    password: str


class UpdatePrivacyRequest(BaseModel):
    visibility_level: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    consent_marketing: Optional[str] = None


class UpgradeAccountRequest(BaseModel):
    pseudo: str
    password: str
    email_recovery: Optional[str] = None
    consent_cgu: bool = True
    consent_privacy: bool = True


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ExternalIdentity(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    provider: str  # franceconnect, franceconnect_plus, identite_numerique_laposte
    provider_user_id: str
    provider_email: Optional[str] = None
    provider_data: Dict[str, Any] = {}
    is_active: bool = True
    linked_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_login_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ConsentRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    consent_type: str  # cgu, privacy, marketing
    consent_value: bool
    policy_version: str = "1.0"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class IdentityVerification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    provider: str
    verification_level: str  # verified, verified_plus
    verification_status: str = "success"  # success, failed, revoked
    details: Dict[str, Any] = {}
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())



class RegisterEntrepriseRequest(BaseModel):
    company_name: str
    siret: str
    email: str
    password: str
    referent_first_name: str
    referent_last_name: str
    referent_function: str
    charte_ethique_signed: bool = True
    consent_cgu: bool = True
    consent_privacy: bool = True


class RegisterPartenaireRequest(BaseModel):
    structure_name: str
    structure_type: str  # organisme_formation, association, institution_publique, acteur_insertion
    siret: str
    email: str
    password: str
    referent_first_name: str
    referent_last_name: str
    referent_function: str
    charte_ethique_signed: bool = True
    consent_cgu: bool = True
    consent_privacy: bool = True


class JobApplication(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    token_id: str
    job_title: str
    job_data: Dict[str, Any] = {}
    motivation: str = ""
    status: str = "submitted"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Evidence(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    token_id: str
    title: str
    kind: str = "attestation"  # diplome, certificat, attestation, portfolio, recommandation
    source: str = ""
    description: str = ""
    linked_skill_ids: List[str] = []
    linked_skill_names: List[str] = []
    obtained_date: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DclicProImport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    target_job: Optional[str] = None
    summary: Optional[str] = None
    city: Optional[str] = None
    mobility: Optional[str] = None
    contract_types: List[str] = []
    work_modes: List[str] = []
    experiences: List[Dict[str, Any]] = []
    skills: List[Dict[str, Any]] = []
    evidences: List[Dict[str, Any]] = []
    dclic_profile: Optional[Dict[str, Any]] = None
