from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import json
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import secrets
from emergentintegrations.llm.chat import LlmChat, UserMessage
import PyPDF2
import io

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# OpenAI via Emergent
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

app = FastAPI()
api_router = APIRouter(prefix="/api")

# ============== MODELS ==============

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

# ============== COFFRE-FORT MODELS ==============

class DocumentCategory(str):
    IDENTITE = "identite_professionnelle"
    DIPLOMES = "diplomes_certifications"
    EXPERIENCES = "experiences_professionnelles"
    COMPETENCES = "competences_preuves"
    ACCOMPAGNEMENT = "accompagnement_insertion"
    CANDIDATURES = "recherche_emploi"
    FORMATION = "formation_apprentissages"
    ADMINISTRATIF = "documents_administratifs"

class PrivacyLevel(str):
    PRIVATE = "private"
    CONSEILLER = "shared_conseiller"
    RECRUTEUR = "shared_recruteur"
    PUBLIC = "public"

class CoffreDocument(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    token_id: str
    title: str
    category: str
    document_type: str
    file_name: str
    file_url: Optional[str] = None
    file_size: int = 0
    mime_type: str = "application/pdf"
    
    # Indexation
    date_document: Optional[str] = None
    metier_associe: Optional[str] = None
    secteur: Optional[str] = None
    competences_liees: List[str] = []
    description: Optional[str] = None
    
    # Confidentialité
    privacy_level: str = "private"
    shared_with: List[str] = []
    share_expiry: Optional[str] = None
    
    # Métadonnées
    date_expiration: Optional[str] = None
    is_expiring_soon: bool = False
    is_sensitive: bool = False
    
    # Audit
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

# ============== OBSERVATOIRE MODELS ==============

class ContributionType(str):
    NEW_SKILL = "nouvelle_competence"
    SKILL_EVOLUTION = "evolution_competence"
    NEW_TOOL = "nouvel_outil"
    JOB_EVOLUTION = "evolution_metier"
    SECTOR_TREND = "tendance_secteur"
    SKILL_OBSOLESCENCE = "competence_obsolete"

class ContributionStatus(str):
    PENDING = "en_attente"
    AI_VALIDATED = "validee_ia"
    AI_REJECTED = "rejetee_ia"
    HUMAN_VALIDATED = "validee_humain"
    HUMAN_REJECTED = "rejetee_humain"
    INTEGRATED = "integree"

class SkillContribution(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contributor_id: str
    contribution_type: str = "nouvelle_competence"
    
    # Contenu de la contribution
    skill_name: str
    skill_description: Optional[str] = None
    related_job: Optional[str] = None
    related_sector: Optional[str] = None
    related_tools: List[str] = []
    context: Optional[str] = None
    
    # Métadonnées
    status: str = "en_attente"
    ai_analysis: Optional[Dict[str, Any]] = None
    ai_score: float = 0.0
    human_validator: Optional[str] = None
    human_notes: Optional[str] = None
    
    # Compteurs
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
    
    # Indicateurs
    emergence_score: float = 0.0
    growth_rate: float = 0.0
    mention_count: int = 0
    contributor_count: int = 0
    
    # Statut
    status: str = "emergente"  # emergente, en_croissance, etablie, en_declin
    first_detected: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class SectorTrend(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sector_name: str
    
    # Compétences
    emerging_skills: List[str] = []
    declining_skills: List[str] = []
    stable_skills: List[str] = []
    
    # Indicateurs
    transformation_index: float = 0.0
    hiring_trend: str = "stable"  # croissance, stable, declin
    skill_gap_alert: bool = False
    
    # Prédictions
    predicted_skills_demand: List[Dict[str, Any]] = []
    
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CreateContributionRequest(BaseModel):
    contribution_type: str = "nouvelle_competence"
    skill_name: str
    skill_description: Optional[str] = None
    related_job: Optional[str] = None
    related_sector: Optional[str] = None
    related_tools: List[str] = []
    context: Optional[str] = None

# ============== INDICE D'ÉVOLUTION DES COMPÉTENCES ==============

class EvolutionIndexLevel(str):
    STABLE = "stable"  # 0-20
    EVOLVING = "evolutif"  # 20-50
    TRANSFORMING = "en_transformation"  # 50-80
    HIGHLY_IMPACTED = "forte_mutation"  # 80-100

class JobEvolutionIndex(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_name: str
    sector: str
    
    # Indice principal (0-100)
    evolution_index: float = 0.0
    index_level: str = "stable"
    
    # Variables de calcul
    new_skills_count: int = 0
    skill_frequency_score: float = 0.0
    task_evolution_score: float = 0.0
    new_tools_score: float = 0.0
    job_posting_evolution: float = 0.0
    declining_skills_count: int = 0
    
    # Compétences associées
    emerging_skills: List[str] = []
    stable_skills: List[str] = []
    declining_skills: List[str] = []
    recommended_skills: List[str] = []
    
    # Recommandations
    recommended_trainings: List[str] = []
    job_passerelles: List[str] = []
    
    # Métadonnées
    last_calculated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    data_sources: List[str] = []
    confidence_level: float = 0.0

class SectorEvolutionIndex(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sector_name: str
    
    # Indice sectoriel (0-100)
    evolution_index: float = 0.0
    index_level: str = "stable"
    
    # Statistiques des métiers
    jobs_count: int = 0
    jobs_in_transformation: int = 0
    jobs_stable: int = 0
    jobs_emerging: int = 0
    
    # Compétences clés
    top_emerging_skills: List[Dict[str, Any]] = []
    top_declining_skills: List[Dict[str, Any]] = []
    skill_gap_areas: List[str] = []
    
    # Indicateurs économiques
    hiring_trend: str = "stable"
    innovation_intensity: float = 0.0
    
    # Prévisions
    predicted_evolution_6m: float = 0.0
    predicted_evolution_12m: float = 0.0
    
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ============== UBUNTOO INTELLIGENCE MODELS ==============

class UbuntooExchange(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exchange_type: str  # discussion, mentorat, conseil, retour_experience, question
    content_summary: str
    detected_skills: List[str] = []
    detected_tools: List[str] = []
    detected_practices: List[str] = []
    related_jobs: List[str] = []
    related_sectors: List[str] = []
    author_role: str = "professionnel"  # anonymized
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class UbuntooSignal(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str  # competence_emergente, nouvel_outil, pratique_nouvelle, transformation_metier, difficulte_metier
    name: str
    description: str
    mention_count: int = 1
    first_detected: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_detected: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    related_jobs: List[str] = []
    related_sectors: List[str] = []
    source_exchanges_count: int = 1
    trend_direction: str = "hausse"  # hausse, stable, baisse
    growth_rate: float = 0.0
    # Validation pipeline
    validation_status: str = "detectee"  # detectee, analysee_ia, validee_humain, integree, rejetee
    ai_confidence: float = 0.0
    ai_analysis: Optional[Dict[str, Any]] = None
    human_validator: Optional[str] = None
    human_notes: Optional[str] = None
    # Cross-reference
    linked_observatory_skills: List[str] = []
    linked_evolution_jobs: List[str] = []
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class UbuntooInsight(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    insight_type: str  # tendance_emergente, alerte_competence, opportunite_formation, transformation_metier
    title: str
    description: str
    supporting_signals: List[str] = []
    impacted_jobs: List[str] = []
    impacted_sectors: List[str] = []
    recommendation: str = ""
    priority: str = "moyenne"  # haute, moyenne, basse
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class MatchRequest(BaseModel):
    profile_skills: List[str]
    job_requirements: List[str]
    profile_sectors: List[str] = []
    job_sector: str = ""

# ============== PASSEPORT DYNAMIQUE DE COMPÉTENCES ==============

class LamriLubartComponents(BaseModel):
    """Modèle Lamri & Lubart: 5 composantes d'une compétence (0-5 scale)"""
    connaissance: int = 0  # Savoirs théoriques et factuels
    cognition: int = 0     # Processus cognitifs (analyse, raisonnement)
    conation: int = 0      # Motivation, volonté, engagement
    affection: int = 0     # Gestion émotionnelle, empathie
    sensori_moteur: int = 0  # Habiletés physiques et pratiques

class CCSPClassification(BaseModel):
    """Référentiel CCSP: Pôle et degré de maîtrise"""
    pole: str = ""  # realisation, interaction, initiative
    degree: str = ""  # imitation, adaptation, transposition

class PassportCompetence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    nature: str = ""  # savoir_faire, savoir_etre
    category: str = "technique"  # technique, transversale (cross-sector/universal), transferable (within sector/company), sectorielle
    level: str = "intermediaire"  # debutant, intermediaire, avance, expert
    experience_years: float = 0
    proof: Optional[str] = None
    source: str = "declaratif"
    is_emerging: bool = False
    # Lamri & Lubart: 5 composantes
    components: Dict[str, int] = Field(default_factory=lambda: {
        "connaissance": 0, "cognition": 0, "conation": 0,
        "affection": 0, "sensori_moteur": 0
    })
    # CCSP: pôle et degré
    ccsp_pole: str = ""
    ccsp_degree: str = ""
    # Archéologie: liens vers la chaîne vertus-valeurs-qualités
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
    experience_type: str = "professionnel"  # professionnel, personnel, benevole, projet
    source: str = "declaratif"
    added_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PassportLearning(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    provider: str = ""
    skills_acquired: List[str] = []
    status: str = "en_cours"  # en_cours, termine, valide
    completion_date: Optional[str] = None
    badge: Optional[str] = None
    source: str = "plateforme"  # plateforme, externe, declaratif

class PassportPasserelle(BaseModel):
    job_name: str
    compatibility_score: float = 0
    shared_skills: List[str] = []
    skills_to_acquire: List[str] = []
    training_needed: str = ""
    accessibility: str = "accessible"  # accessible, formation_courte, formation_longue
    sector: str = ""

class Passport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    token_id: str
    # Profil professionnel
    professional_summary: str = ""
    career_project: str = ""
    motivations: List[str] = []
    compatible_environments: List[str] = []
    target_sectors: List[str] = []
    # Compétences
    competences: List[Dict[str, Any]] = []
    # Expériences
    experiences: List[Dict[str, Any]] = []
    # Parcours d'apprentissage
    learning_path: List[Dict[str, Any]] = []
    # Passerelles (generated by AI)
    passerelles: List[Dict[str, Any]] = []
    # Métadonnées
    completeness_score: int = 0
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    # Partage
    sharing: Dict[str, Any] = Field(default_factory=lambda: {
        "is_public": False,
        "shared_sections": [],
        "shared_with": [],
        "share_expiry": None
    })

class AddCompetenceRequest(BaseModel):
    name: str
    nature: str = ""  # savoir_faire, savoir_etre
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
    components: Dict[str, int]  # connaissance, cognition, conation, affection, sensori_moteur (0-5)
    ccsp_pole: Optional[str] = None
    ccsp_degree: Optional[str] = None

class CCSPDiagnosticRequest(BaseModel):
    competence_ids: List[str] = []  # If empty, analyze all competences

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

class CreateJobRequest(BaseModel):
    title: str
    company: str
    location: str
    contract_type: str
    salary_range: Optional[str] = None
    required_skills: List[str] = []
    description: str
    sector: str

class MetricData(BaseModel):
    particuliers: Dict[str, int]
    entreprises: Dict[str, int]
    partenaires: Dict[str, int]

# ============== HELPER FUNCTIONS ==============

async def get_current_token(token: str) -> dict:
    token_doc = await db.tokens.find_one({"token": token}, {"_id": 0})
    if not token_doc:
        raise HTTPException(status_code=401, detail="Token invalide")
    return token_doc

async def calculate_match_with_ai(profile_skills: List[str], job_requirements: List[str], profile_sectors: List[str], job_sector: str) -> Dict[str, Any]:
    """Use OpenAI to calculate intelligent matching"""
    if not EMERGENT_LLM_KEY:
        # Fallback to simple matching
        common_skills = set(profile_skills) & set(job_requirements)
        score = int((len(common_skills) / max(len(job_requirements), 1)) * 100)
        return {"score": min(score + 20, 100), "rationale": "Correspondance basée sur les compétences communes."}
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"match-{uuid.uuid4()}",
            system_message="Tu es un expert RH français. Analyse la correspondance entre un profil et une offre d'emploi. Réponds en JSON avec 'score' (0-100) et 'rationale' (explication courte en français)."
        ).with_model("openai", "gpt-5.2")
        
        prompt = f"""
        Compétences du candidat: {', '.join(profile_skills)}
        Compétences requises pour le poste: {', '.join(job_requirements)}
        Secteurs du candidat: {', '.join(profile_sectors)}
        Secteur du poste: {job_sector}
        
        Calcule un score de correspondance et explique pourquoi.
        """
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Parse response
        import json
        try:
            result = json.loads(response)
            return {"score": result.get("score", 50), "rationale": result.get("rationale", "Analyse IA")}
        except:
            return {"score": 65, "rationale": response[:200]}
    except Exception as e:
        logging.error(f"AI matching error: {e}")
        common_skills = set(profile_skills) & set(job_requirements)
        score = int((len(common_skills) / max(len(job_requirements), 1)) * 100)
        return {"score": min(score + 20, 100), "rationale": "Correspondance basée sur les compétences communes."}

# ============== AUTH ENDPOINTS ==============

@api_router.post("/auth/anonymous")
async def create_anonymous_token(request: CreateTokenRequest):
    """Create an anonymous secure token"""
    token = AnonymousToken(role=request.role)
    token_dict = token.model_dump()
    await db.tokens.insert_one(token_dict)
    
    # Create associated profile
    profile = Profile(
        token_id=token.id,
        role=request.role,
        name=f"Utilisateur {token.id[:8].upper()}"
    )
    profile_dict = profile.model_dump()
    await db.profiles.insert_one(profile_dict)
    
    # Update token with profile_id
    await db.tokens.update_one({"id": token.id}, {"$set": {"profile_id": profile.id}})
    
    return {"token": token.token, "role": token.role, "profile_id": profile.id}

@api_router.get("/auth/verify")
async def verify_token(token: str):
    """Verify token validity"""
    token_doc = await get_current_token(token)
    return {"valid": True, "role": token_doc["role"], "profile_id": token_doc.get("profile_id")}

@api_router.post("/auth/switch-role")
async def switch_role(token: str, new_role: str):
    """Switch user role"""
    if new_role not in ["particulier", "entreprise", "partenaire"]:
        raise HTTPException(status_code=400, detail="Rôle invalide")
    
    await db.tokens.update_one({"token": token}, {"$set": {"role": new_role}})
    return {"message": "Rôle mis à jour", "role": new_role}

# ============== PROFILE ENDPOINTS ==============

@api_router.get("/profile")
async def get_profile(token: str):
    """Get user profile"""
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    return profile

@api_router.put("/profile")
async def update_profile(token: str, request: UpdateProfileRequest):
    """Update user profile"""
    token_doc = await get_current_token(token)
    
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    
    if update_data:
        # Calculate profile score based on completeness
        profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
        if profile:
            skills_count = len(update_data.get("skills", profile.get("skills", [])))
            sectors_count = len(update_data.get("sectors", profile.get("sectors", [])))
            exp = update_data.get("experience_years", profile.get("experience_years", 0))
            score = min(100, skills_count * 10 + sectors_count * 5 + (10 if exp > 0 else 0) + 30)
            update_data["profile_score"] = score
        
        await db.profiles.update_one({"token_id": token_doc["id"]}, {"$set": update_data})
    
    return await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})

# ============== JOBS ENDPOINTS ==============

@api_router.get("/jobs")
async def get_jobs(token: str, limit: int = 20):
    """Get job offers with match scores"""
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    
    jobs = await db.jobs.find({"status": "active"}, {"_id": 0}).to_list(limit)
    
    # Calculate match scores
    if profile and profile.get("skills"):
        profile_skill_names = [s.get("name", "") for s in profile.get("skills", [])]
        for job in jobs:
            common = set(profile_skill_names) & set(job.get("required_skills", []))
            job["match_score"] = min(100, int((len(common) / max(len(job.get("required_skills", [])), 1)) * 100) + 25)
    
    return sorted(jobs, key=lambda x: x.get("match_score", 0), reverse=True)

@api_router.post("/jobs")
async def create_job(token: str, request: CreateJobRequest):
    """Create a new job offer (RH only)"""
    token_doc = await get_current_token(token)
    if token_doc["role"] != "entreprise":
        raise HTTPException(status_code=403, detail="Accès réservé aux entreprises")
    
    job = JobOffer(**request.model_dump(), created_by=token_doc["id"])
    await db.jobs.insert_one(job.model_dump())
    return job.model_dump()

@api_router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job details"""
    job = await db.jobs.find_one({"id": job_id}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    return job

@api_router.get("/jobs/{job_id}/match")
async def get_job_match(token: str, job_id: str):
    """Get AI-powered match analysis for a job"""
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    job = await db.jobs.find_one({"id": job_id}, {"_id": 0})
    
    if not profile or not job:
        raise HTTPException(status_code=404, detail="Profil ou offre non trouvé")
    
    profile_skill_names = [s.get("name", "") for s in profile.get("skills", [])]
    match_result = await calculate_match_with_ai(
        profile_skill_names,
        job.get("required_skills", []),
        profile.get("sectors", []),
        job.get("sector", "")
    )
    
    return match_result

# ============== LEARNING ENDPOINTS ==============

@api_router.get("/learning")
async def get_learning_modules(token: str):
    """Get recommended learning modules"""
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    
    modules = await db.learning_modules.find({}, {"_id": 0}).to_list(50)
    
    # Get user progress
    progress_docs = await db.learning_progress.find({"token_id": token_doc["id"]}, {"_id": 0}).to_list(100)
    progress_map = {p["module_id"]: p["progress"] for p in progress_docs}
    
    for module in modules:
        module["progress"] = progress_map.get(module["id"], 0)
    
    return modules

@api_router.post("/learning/{module_id}/progress")
async def update_learning_progress(token: str, module_id: str, progress: int):
    """Update learning progress"""
    token_doc = await get_current_token(token)
    
    await db.learning_progress.update_one(
        {"token_id": token_doc["id"], "module_id": module_id},
        {"$set": {"progress": min(100, max(0, progress)), "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    
    return {"message": "Progression mise à jour", "progress": progress}

# ============== RH ENDPOINTS ==============

@api_router.get("/rh/offers")
async def get_rh_offers(token: str):
    """Get offers created by RH"""
    token_doc = await get_current_token(token)
    offers = await db.jobs.find({"created_by": token_doc["id"]}, {"_id": 0}).to_list(50)
    return offers

@api_router.get("/rh/candidates")
async def get_candidates(token: str, job_id: Optional[str] = None):
    """Get compatible candidates for RH"""
    token_doc = await get_current_token(token)
    
    # Get all profiles (in real app, would filter by job compatibility)
    profiles = await db.profiles.find({"role": "particulier"}, {"_id": 0}).to_list(50)
    
    if job_id:
        job = await db.jobs.find_one({"id": job_id}, {"_id": 0})
        if job:
            for profile in profiles:
                profile_skill_names = [s.get("name", "") for s in profile.get("skills", [])]
                common = set(profile_skill_names) & set(job.get("required_skills", []))
                profile["match_score"] = min(100, int((len(common) / max(len(job.get("required_skills", [])), 1)) * 100) + 20)
            profiles = sorted(profiles, key=lambda x: x.get("match_score", 0), reverse=True)
    
    return profiles

# ============== PARTENAIRES ENDPOINTS ==============

@api_router.get("/partenaires/beneficiaires")
async def get_beneficiaires(token: str):
    """Get beneficiaries for social partners"""
    token_doc = await get_current_token(token)
    beneficiaires = await db.beneficiaires.find({"partner_id": token_doc["id"]}, {"_id": 0}).to_list(100)
    return beneficiaires

@api_router.post("/partenaires/beneficiaires")
async def create_beneficiaire(token: str, name: str, sector: str):
    """Create a new beneficiary"""
    token_doc = await get_current_token(token)
    
    beneficiary = Beneficiary(
        name=name,
        status="En accompagnement",
        sector=sector,
        partner_id=token_doc["id"]
    )
    await db.beneficiaires.insert_one(beneficiary.model_dump())
    return beneficiary.model_dump()

@api_router.put("/partenaires/beneficiaires/{beneficiary_id}")
async def update_beneficiaire(token: str, beneficiary_id: str, status: Optional[str] = None, progress: Optional[int] = None):
    """Update beneficiary status"""
    update_data = {}
    if status:
        update_data["status"] = status
    if progress is not None:
        update_data["progress"] = progress
    update_data["last_activity"] = datetime.now(timezone.utc).isoformat()
    
    await db.beneficiaires.update_one({"id": beneficiary_id}, {"$set": update_data})
    return await db.beneficiaires.find_one({"id": beneficiary_id}, {"_id": 0})

# ============== METRICS ENDPOINTS ==============

@api_router.get("/metrics")
async def get_metrics():
    """Get platform metrics"""
    particuliers_count = await db.profiles.count_documents({"role": "particulier"})
    entreprises_count = await db.profiles.count_documents({"role": "entreprise"})
    jobs_count = await db.jobs.count_documents({"status": "active"})
    beneficiaires_count = await db.beneficiaires.count_documents({})
    
    return {
        "particuliers": {
            "total": particuliers_count,
            "active": particuliers_count
        },
        "entreprises": {
            "total": entreprises_count,
            "jobs_posted": jobs_count
        },
        "partenaires": {
            "beneficiaires": beneficiaires_count,
            "active_support": beneficiaires_count
        }
    }

# ============== COFFRE-FORT ENDPOINTS ==============

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

@api_router.get("/coffre/categories")
async def get_coffre_categories():
    """Get all document categories for the coffre-fort"""
    return DOCUMENT_CATEGORIES

@api_router.get("/coffre/documents")
async def get_coffre_documents(token: str, category: Optional[str] = None, search: Optional[str] = None):
    """Get all documents in user's coffre-fort"""
    token_doc = await get_current_token(token)
    
    query = {"token_id": token_doc["id"]}
    if category:
        query["category"] = category
    
    documents = await db.coffre_documents.find(query, {"_id": 0}).to_list(500)
    
    if search:
        search_lower = search.lower()
        documents = [d for d in documents if 
            search_lower in d.get("title", "").lower() or 
            search_lower in d.get("description", "").lower() or
            any(search_lower in c.lower() for c in d.get("competences_liees", []))]
    
    # Check for expiring documents
    today = datetime.now(timezone.utc)
    for doc in documents:
        if doc.get("date_expiration"):
            try:
                exp_date = datetime.fromisoformat(doc["date_expiration"].replace('Z', '+00:00'))
                days_until = (exp_date - today).days
                doc["is_expiring_soon"] = 0 <= days_until <= 30
                doc["days_until_expiry"] = days_until
            except:
                pass
    
    return sorted(documents, key=lambda x: x.get("created_at", ""), reverse=True)

@api_router.get("/coffre/documents/{document_id}")
async def get_coffre_document(token: str, document_id: str):
    """Get a specific document"""
    token_doc = await get_current_token(token)
    doc = await db.coffre_documents.find_one({"id": document_id, "token_id": token_doc["id"]}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return doc

@api_router.post("/coffre/documents")
async def create_coffre_document(token: str, request: CreateDocumentRequest):
    """Create a new document in coffre-fort"""
    token_doc = await get_current_token(token)
    
    document = CoffreDocument(
        token_id=token_doc["id"],
        **request.model_dump()
    )
    
    await db.coffre_documents.insert_one(document.model_dump())
    
    # If competences are linked, update profile skills
    if request.competences_liees:
        profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
        if profile:
            existing_skills = [s.get("name") for s in profile.get("skills", [])]
            new_skills = profile.get("skills", [])
            for comp in request.competences_liees:
                if comp not in existing_skills:
                    new_skills.append({"name": comp, "level": 50, "proven": True})
            await db.profiles.update_one({"token_id": token_doc["id"]}, {"$set": {"skills": new_skills}})
    
    return document.model_dump()

@api_router.put("/coffre/documents/{document_id}")
async def update_coffre_document(token: str, document_id: str, request: CreateDocumentRequest):
    """Update a document"""
    token_doc = await get_current_token(token)
    
    update_data = request.model_dump()
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.coffre_documents.update_one(
        {"id": document_id, "token_id": token_doc["id"]},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    return await db.coffre_documents.find_one({"id": document_id}, {"_id": 0})

@api_router.delete("/coffre/documents/{document_id}")
async def delete_coffre_document(token: str, document_id: str):
    """Delete a document"""
    token_doc = await get_current_token(token)
    result = await db.coffre_documents.delete_one({"id": document_id, "token_id": token_doc["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return {"message": "Document supprimé"}

@api_router.post("/coffre/documents/{document_id}/share")
async def share_document(token: str, document_id: str, shared_with_email: Optional[str] = None, shared_with_role: Optional[str] = None, expires_in_days: int = 7):
    """Create a share link for a document"""
    token_doc = await get_current_token(token)
    
    doc = await db.coffre_documents.find_one({"id": document_id, "token_id": token_doc["id"]}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    expires_at = (datetime.now(timezone.utc) + timedelta(days=expires_in_days)).isoformat()
    
    share = DocumentShare(
        document_id=document_id,
        shared_by=token_doc["id"],
        shared_with_email=shared_with_email,
        shared_with_role=shared_with_role,
        expires_at=expires_at
    )
    
    await db.document_shares.insert_one(share.model_dump())
    
    # Update document privacy
    await db.coffre_documents.update_one(
        {"id": document_id},
        {
            "$set": {"privacy_level": "shared_recruteur" if shared_with_role == "recruteur" else "shared_conseiller"},
            "$push": {"shared_with": share.id}
        }
    )
    
    return {"share_id": share.id, "access_token": share.access_token, "expires_at": expires_at}

@api_router.get("/coffre/shares")
async def get_document_shares(token: str):
    """Get all active shares for user's documents"""
    token_doc = await get_current_token(token)
    shares = await db.document_shares.find({"shared_by": token_doc["id"]}, {"_id": 0}).to_list(100)
    
    # Enrich with document info
    for share in shares:
        doc = await db.coffre_documents.find_one({"id": share["document_id"]}, {"_id": 0})
        if doc:
            share["document_title"] = doc.get("title")
            share["document_category"] = doc.get("category")
    
    return shares

@api_router.delete("/coffre/shares/{share_id}")
async def revoke_share(token: str, share_id: str):
    """Revoke a document share"""
    token_doc = await get_current_token(token)
    
    share = await db.document_shares.find_one({"id": share_id, "shared_by": token_doc["id"]}, {"_id": 0})
    if not share:
        raise HTTPException(status_code=404, detail="Partage non trouvé")
    
    await db.document_shares.delete_one({"id": share_id})
    
    # Update document
    await db.coffre_documents.update_one(
        {"id": share["document_id"]},
        {"$pull": {"shared_with": share_id}}
    )
    
    return {"message": "Partage révoqué"}

@api_router.get("/coffre/stats")
async def get_coffre_stats(token: str):
    """Get coffre-fort statistics"""
    token_doc = await get_current_token(token)
    
    documents = await db.coffre_documents.find({"token_id": token_doc["id"]}, {"_id": 0}).to_list(500)
    
    stats = {
        "total_documents": len(documents),
        "by_category": {},
        "competences_prouvees": set(),
        "documents_partages": 0,
        "documents_expirants": 0,
        "documents_sensibles": 0
    }
    
    today = datetime.now(timezone.utc)
    
    for doc in documents:
        cat = doc.get("category", "autre")
        stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
        
        for comp in doc.get("competences_liees", []):
            stats["competences_prouvees"].add(comp)
        
        if doc.get("privacy_level") != "private":
            stats["documents_partages"] += 1
        
        if doc.get("is_sensitive"):
            stats["documents_sensibles"] += 1
        
        if doc.get("date_expiration"):
            try:
                exp_date = datetime.fromisoformat(doc["date_expiration"].replace('Z', '+00:00'))
                if 0 <= (exp_date - today).days <= 30:
                    stats["documents_expirants"] += 1
            except:
                pass
    
    stats["competences_prouvees"] = list(stats["competences_prouvees"])
    
    return stats

@api_router.get("/coffre/expiring")
async def get_expiring_documents(token: str):
    """Get documents expiring in the next 30 days"""
    token_doc = await get_current_token(token)
    documents = await db.coffre_documents.find({"token_id": token_doc["id"]}, {"_id": 0}).to_list(500)
    
    today = datetime.now(timezone.utc)
    expiring = []
    
    for doc in documents:
        if doc.get("date_expiration"):
            try:
                exp_date = datetime.fromisoformat(doc["date_expiration"].replace('Z', '+00:00'))
                days_until = (exp_date - today).days
                if 0 <= days_until <= 30:
                    doc["days_until_expiry"] = days_until
                    expiring.append(doc)
            except:
                pass
    
    return sorted(expiring, key=lambda x: x.get("days_until_expiry", 999))

# ============== OBSERVATOIRE ENDPOINTS ==============

@api_router.get("/observatoire/dashboard")
async def get_observatoire_dashboard():
    """Get observatoire main dashboard data"""
    emerging_skills = await db.emerging_skills.find({}, {"_id": 0}).to_list(50)
    sector_trends = await db.sector_trends.find({}, {"_id": 0}).to_list(20)
    contributions_count = await db.skill_contributions.count_documents({})
    validated_count = await db.skill_contributions.count_documents({"status": "integree"})
    
    # Calculate global indicators
    total_emerging = len([s for s in emerging_skills if s.get("status") == "emergente"])
    total_growing = len([s for s in emerging_skills if s.get("status") == "en_croissance"])
    sectors_in_transformation = len([t for t in sector_trends if t.get("transformation_index", 0) > 0.6])
    
    return {
        "emerging_skills": emerging_skills,
        "sector_trends": sector_trends,
        "indicators": {
            "total_emerging_skills": total_emerging,
            "total_growing_skills": total_growing,
            "sectors_in_transformation": sectors_in_transformation,
            "total_contributions": contributions_count,
            "validated_contributions": validated_count,
            "skill_gap_alerts": len([t for t in sector_trends if t.get("skill_gap_alert")])
        }
    }

@api_router.get("/observatoire/emerging-skills")
async def get_emerging_skills(sector: Optional[str] = None, status: Optional[str] = None):
    """Get emerging skills with optional filters"""
    query = {}
    if sector:
        query["related_sectors"] = sector
    if status:
        query["status"] = status
    
    skills = await db.emerging_skills.find(query, {"_id": 0}).to_list(100)
    return sorted(skills, key=lambda x: x.get("emergence_score", 0), reverse=True)

@api_router.get("/observatoire/sector-trends")
async def get_sector_trends(sector: Optional[str] = None):
    """Get sector transformation trends"""
    query = {}
    if sector:
        query["sector_name"] = sector
    
    trends = await db.sector_trends.find(query, {"_id": 0}).to_list(50)
    return sorted(trends, key=lambda x: x.get("transformation_index", 0), reverse=True)

@api_router.get("/observatoire/sector/{sector_name}")
async def get_sector_detail(sector_name: str):
    """Get detailed information about a sector"""
    trend = await db.sector_trends.find_one({"sector_name": sector_name}, {"_id": 0})
    if not trend:
        raise HTTPException(status_code=404, detail="Secteur non trouvé")
    
    # Get related emerging skills
    related_skills = await db.emerging_skills.find(
        {"related_sectors": sector_name}, 
        {"_id": 0}
    ).to_list(20)
    
    # Get recent contributions for this sector
    contributions = await db.skill_contributions.find(
        {"related_sector": sector_name, "status": {"$in": ["validee_ia", "validee_humain", "integree"]}},
        {"_id": 0}
    ).to_list(10)
    
    return {
        "trend": trend,
        "related_skills": related_skills,
        "recent_contributions": contributions
    }

@api_router.post("/observatoire/contributions")
async def create_contribution(token: str, request: CreateContributionRequest):
    """Submit a new skill/job contribution"""
    token_doc = await get_current_token(token)
    
    contribution = SkillContribution(
        contributor_id=token_doc["id"],
        **request.model_dump()
    )
    
    # AI Analysis (simplified - would use OpenAI in production)
    ai_analysis = await analyze_contribution_with_ai(contribution)
    contribution.ai_analysis = ai_analysis
    contribution.ai_score = ai_analysis.get("confidence_score", 0.5)
    
    if ai_analysis.get("is_valid", False) and ai_analysis.get("confidence_score", 0) > 0.7:
        contribution.status = "validee_ia"
    elif ai_analysis.get("confidence_score", 0) < 0.3:
        contribution.status = "rejetee_ia"
    
    # Check for similar contributions
    similar = await db.skill_contributions.find_one({
        "skill_name": {"$regex": contribution.skill_name, "$options": "i"},
        "status": {"$ne": "rejetee_ia"}
    }, {"_id": 0})
    
    if similar:
        # Increment similar count
        await db.skill_contributions.update_one(
            {"id": similar["id"]},
            {"$inc": {"similar_count": 1}}
        )
        contribution.similar_count = similar.get("similar_count", 1) + 1
    
    await db.skill_contributions.insert_one(contribution.model_dump())
    
    return {
        "contribution_id": contribution.id,
        "status": contribution.status,
        "ai_analysis": ai_analysis,
        "message": "Contribution enregistrée et analysée"
    }

@api_router.get("/observatoire/contributions")
async def get_contributions(token: str, status: Optional[str] = None):
    """Get user's contributions"""
    token_doc = await get_current_token(token)
    
    query = {"contributor_id": token_doc["id"]}
    if status:
        query["status"] = status
    
    contributions = await db.skill_contributions.find(query, {"_id": 0}).to_list(100)
    return contributions

@api_router.get("/observatoire/contributions/pending")
async def get_pending_contributions():
    """Get contributions pending human validation (for validators)"""
    contributions = await db.skill_contributions.find(
        {"status": "validee_ia"},
        {"_id": 0}
    ).to_list(50)
    return contributions

@api_router.post("/observatoire/contributions/{contribution_id}/validate")
async def validate_contribution(contribution_id: str, approved: bool, notes: Optional[str] = None):
    """Human validation of a contribution"""
    update_data = {
        "status": "validee_humain" if approved else "rejetee_humain",
        "human_notes": notes,
        "validated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = await db.skill_contributions.update_one(
        {"id": contribution_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Contribution non trouvée")
    
    # If validated, potentially add to emerging skills
    if approved:
        contribution = await db.skill_contributions.find_one({"id": contribution_id}, {"_id": 0})
        if contribution and contribution.get("similar_count", 1) >= 3:
            await integrate_contribution_to_skills(contribution)
    
    return {"message": "Validation enregistrée", "status": update_data["status"]}

@api_router.post("/observatoire/contributions/{contribution_id}/upvote")
async def upvote_contribution(token: str, contribution_id: str):
    """Upvote a contribution"""
    await get_current_token(token)
    
    result = await db.skill_contributions.update_one(
        {"id": contribution_id},
        {"$inc": {"upvotes": 1}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Contribution non trouvée")
    
    return {"message": "Vote enregistré"}

@api_router.get("/observatoire/predictions")
async def get_predictions():
    """Get skill demand predictions"""
    trends = await db.sector_trends.find({}, {"_id": 0}).to_list(50)
    
    predictions = []
    for trend in trends:
        for pred in trend.get("predicted_skills_demand", []):
            predictions.append({
                "sector": trend["sector_name"],
                **pred
            })
    
    return sorted(predictions, key=lambda x: x.get("demand_change", "0%"), reverse=True)

@api_router.get("/observatoire/skill-gaps")
async def get_skill_gaps():
    """Get sectors with skill gap alerts"""
    trends = await db.sector_trends.find({"skill_gap_alert": True}, {"_id": 0}).to_list(20)
    return trends

# ============== INDICE D'ÉVOLUTION ENDPOINTS ==============

def calculate_index_level(index: float) -> str:
    """Determine the level based on index value"""
    if index < 20:
        return "stable"
    elif index < 50:
        return "evolutif"
    elif index < 80:
        return "en_transformation"
    else:
        return "forte_mutation"

def get_index_interpretation(index: float, job_name: str = None) -> Dict[str, Any]:
    """Get human-readable interpretation of the index"""
    if index < 20:
        return {
            "level": "stable",
            "label": "Métier très stable",
            "description": f"Les compétences de ce métier évoluent peu. La formation initiale reste pertinente sur le long terme.",
            "color": "emerald",
            "recommendation": "Maintenez vos compétences actuelles et restez en veille sur les évolutions du secteur."
        }
    elif index < 50:
        return {
            "level": "evolutif",
            "label": "Métier évolutif",
            "description": f"Ce métier connaît des évolutions modérées. Certaines compétences nouvelles apparaissent progressivement.",
            "color": "blue",
            "recommendation": "Renforcez vos compétences numériques et suivez une formation continue régulière."
        }
    elif index < 80:
        return {
            "level": "en_transformation",
            "label": "Métier en transformation",
            "description": f"Ce métier évolue significativement sous l'effet des innovations technologiques ou organisationnelles.",
            "color": "amber",
            "recommendation": "Anticipez les changements en développant les compétences émergentes de votre secteur."
        }
    else:
        return {
            "level": "forte_mutation",
            "label": "Forte mutation",
            "description": f"Ce métier est fortement impacté par les transformations. Une adaptation rapide est nécessaire.",
            "color": "rose",
            "recommendation": "Envisagez une montée en compétences significative ou une reconversion vers des métiers connexes."
        }

@api_router.get("/evolution-index/jobs")
async def get_jobs_evolution_index(sector: Optional[str] = None):
    """Get evolution index for all jobs"""
    query = {}
    if sector:
        query["sector"] = sector
    
    indices = await db.job_evolution_indices.find(query, {"_id": 0}).to_list(100)
    
    # Enrich with interpretation
    for idx in indices:
        idx["interpretation"] = get_index_interpretation(idx.get("evolution_index", 0), idx.get("job_name"))
    
    return sorted(indices, key=lambda x: x.get("evolution_index", 0), reverse=True)

@api_router.get("/evolution-index/jobs/{job_name}")
async def get_job_evolution_detail(job_name: str):
    """Get detailed evolution index for a specific job"""
    index = await db.job_evolution_indices.find_one(
        {"job_name": {"$regex": job_name, "$options": "i"}}, 
        {"_id": 0}
    )
    
    if not index:
        raise HTTPException(status_code=404, detail="Métier non trouvé")
    
    index["interpretation"] = get_index_interpretation(index.get("evolution_index", 0), job_name)
    
    # Get related emerging skills
    related_skills = await db.emerging_skills.find(
        {"related_jobs": {"$regex": job_name, "$options": "i"}},
        {"_id": 0}
    ).to_list(10)
    
    index["related_emerging_skills"] = related_skills
    
    return index

@api_router.get("/evolution-index/sectors")
async def get_sectors_evolution_index():
    """Get evolution index for all sectors"""
    indices = await db.sector_evolution_indices.find({}, {"_id": 0}).to_list(50)
    
    for idx in indices:
        idx["interpretation"] = get_index_interpretation(idx.get("evolution_index", 0))
    
    return sorted(indices, key=lambda x: x.get("evolution_index", 0), reverse=True)

@api_router.get("/evolution-index/sectors/{sector_name}")
async def get_sector_evolution_detail(sector_name: str):
    """Get detailed evolution index for a sector"""
    index = await db.sector_evolution_indices.find_one(
        {"sector_name": {"$regex": sector_name, "$options": "i"}},
        {"_id": 0}
    )
    
    if not index:
        raise HTTPException(status_code=404, detail="Secteur non trouvé")
    
    index["interpretation"] = get_index_interpretation(index.get("evolution_index", 0))
    
    # Get all jobs in this sector
    jobs = await db.job_evolution_indices.find(
        {"sector": {"$regex": sector_name, "$options": "i"}},
        {"_id": 0}
    ).to_list(50)
    
    index["jobs"] = jobs
    
    return index

@api_router.get("/evolution-index/dashboard")
async def get_evolution_dashboard():
    """Get comprehensive evolution index dashboard"""
    job_indices = await db.job_evolution_indices.find({}, {"_id": 0}).to_list(100)
    sector_indices = await db.sector_evolution_indices.find({}, {"_id": 0}).to_list(50)
    
    # Calculate statistics
    total_jobs = len(job_indices)
    jobs_stable = len([j for j in job_indices if j.get("evolution_index", 0) < 20])
    jobs_evolving = len([j for j in job_indices if 20 <= j.get("evolution_index", 0) < 50])
    jobs_transforming = len([j for j in job_indices if 50 <= j.get("evolution_index", 0) < 80])
    jobs_highly_impacted = len([j for j in job_indices if j.get("evolution_index", 0) >= 80])
    
    avg_job_index = sum(j.get("evolution_index", 0) for j in job_indices) / max(total_jobs, 1)
    avg_sector_index = sum(s.get("evolution_index", 0) for s in sector_indices) / max(len(sector_indices), 1)
    
    # Top transforming jobs
    top_transforming = sorted(job_indices, key=lambda x: x.get("evolution_index", 0), reverse=True)[:5]
    most_stable = sorted(job_indices, key=lambda x: x.get("evolution_index", 0))[:5]
    
    # Sectors overview
    for sector in sector_indices:
        sector["interpretation"] = get_index_interpretation(sector.get("evolution_index", 0))
    
    return {
        "summary": {
            "total_jobs_analyzed": total_jobs,
            "total_sectors_analyzed": len(sector_indices),
            "average_job_evolution_index": round(avg_job_index, 1),
            "average_sector_evolution_index": round(avg_sector_index, 1)
        },
        "distribution": {
            "stable": {"count": jobs_stable, "percentage": round(jobs_stable / max(total_jobs, 1) * 100, 1)},
            "evolving": {"count": jobs_evolving, "percentage": round(jobs_evolving / max(total_jobs, 1) * 100, 1)},
            "transforming": {"count": jobs_transforming, "percentage": round(jobs_transforming / max(total_jobs, 1) * 100, 1)},
            "highly_impacted": {"count": jobs_highly_impacted, "percentage": round(jobs_highly_impacted / max(total_jobs, 1) * 100, 1)}
        },
        "top_transforming_jobs": top_transforming,
        "most_stable_jobs": most_stable,
        "sectors": sector_indices,
        "interpretation_guide": {
            "stable": {"range": "0-20", "description": "Métier très stable, évolution lente"},
            "evolutif": {"range": "20-50", "description": "Métier évolutif mais relativement stable"},
            "en_transformation": {"range": "50-80", "description": "Métier en transformation importante"},
            "forte_mutation": {"range": "80-100", "description": "Métier fortement impacté par les innovations"}
        }
    }

@api_router.get("/evolution-index/user-profile")
async def get_user_evolution_analysis(token: str):
    """Get evolution analysis based on user's profile and skills"""
    token_doc = await get_current_token(token)
    profile = await db.profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    user_sectors = profile.get("sectors", [])
    user_skills = [s.get("name", "") for s in profile.get("skills", [])]
    
    # Find relevant job indices
    relevant_jobs = []
    for sector in user_sectors:
        jobs = await db.job_evolution_indices.find(
            {"sector": {"$regex": sector, "$options": "i"}},
            {"_id": 0}
        ).to_list(20)
        relevant_jobs.extend(jobs)
    
    # Find skills at risk
    skills_at_risk = []
    skills_in_demand = []
    
    for job in relevant_jobs:
        for skill in user_skills:
            if skill in job.get("declining_skills", []):
                skills_at_risk.append({"skill": skill, "job": job["job_name"]})
            if skill in job.get("emerging_skills", []):
                skills_in_demand.append({"skill": skill, "job": job["job_name"]})
    
    # Recommendations
    all_recommended = set()
    for job in relevant_jobs:
        all_recommended.update(job.get("recommended_skills", []))
    
    # Calculate personal evolution exposure
    if relevant_jobs:
        avg_exposure = sum(j.get("evolution_index", 0) for j in relevant_jobs) / len(relevant_jobs)
    else:
        avg_exposure = 50
    
    return {
        "profile_sectors": user_sectors,
        "profile_skills": user_skills,
        "evolution_exposure": round(avg_exposure, 1),
        "exposure_interpretation": get_index_interpretation(avg_exposure),
        "relevant_jobs": relevant_jobs[:5],
        "skills_at_risk": skills_at_risk,
        "skills_in_demand": skills_in_demand,
        "recommended_skills_to_acquire": list(all_recommended - set(user_skills))[:10],
        "recommended_trainings": list(set(t for j in relevant_jobs for t in j.get("recommended_trainings", [])))[:5]
    }

async def analyze_contribution_with_ai(contribution: SkillContribution) -> Dict[str, Any]:
    """Analyze a contribution using AI"""
    if not EMERGENT_LLM_KEY:
        # Fallback analysis
        is_valid = len(contribution.skill_name) > 3 and len(contribution.skill_name) < 100
        return {
            "is_valid": is_valid,
            "confidence_score": 0.6 if is_valid else 0.3,
            "category": "technique" if any(kw in contribution.skill_name.lower() for kw in ["code", "data", "dev", "ia", "cyber"]) else "transversale",
            "similar_existing": [],
            "rationale": "Analyse basique - cohérence vérifiée"
        }
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"contrib-{contribution.id}",
            system_message="Tu es un expert RH français. Analyse cette contribution à un observatoire des compétences. Réponds en JSON avec: is_valid (bool), confidence_score (0-1), category (technique/transversale/sectorielle), similar_existing (list), rationale (string)."
        ).with_model("openai", "gpt-5.2")
        
        prompt = f"""
        Nouvelle compétence proposée: {contribution.skill_name}
        Description: {contribution.skill_description or 'Non fournie'}
        Métier associé: {contribution.related_job or 'Non spécifié'}
        Secteur: {contribution.related_sector or 'Non spécifié'}
        Contexte: {contribution.context or 'Non fourni'}
        
        Analyse si cette compétence est:
        1. Valide et pertinente pour le marché du travail
        2. Suffisamment précise
        3. Potentiellement émergente
        """
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        import json
        try:
            result = json.loads(response)
            return result
        except:
            return {
                "is_valid": True,
                "confidence_score": 0.65,
                "category": "transversale",
                "similar_existing": [],
                "rationale": response[:200]
            }
    except Exception as e:
        logging.error(f"AI contribution analysis error: {e}")
        return {
            "is_valid": True,
            "confidence_score": 0.5,
            "category": "non_classifie",
            "similar_existing": [],
            "rationale": "Analyse automatique non disponible"
        }

async def integrate_contribution_to_skills(contribution: dict):
    """Integrate a validated contribution into emerging skills"""
    existing = await db.emerging_skills.find_one(
        {"skill_name": {"$regex": contribution["skill_name"], "$options": "i"}},
        {"_id": 0}
    )
    
    if existing:
        # Update existing skill
        await db.emerging_skills.update_one(
            {"id": existing["id"]},
            {
                "$inc": {"mention_count": 1, "contributor_count": 1},
                "$set": {"last_updated": datetime.now(timezone.utc).isoformat()}
            }
        )
    else:
        # Create new emerging skill
        new_skill = EmergingSkill(
            skill_name=contribution["skill_name"],
            description=contribution.get("skill_description"),
            related_sectors=[contribution["related_sector"]] if contribution.get("related_sector") else [],
            related_jobs=[contribution["related_job"]] if contribution.get("related_job") else [],
            related_tools=contribution.get("related_tools", []),
            emergence_score=0.5,
            growth_rate=0.1,
            mention_count=contribution.get("similar_count", 1),
            contributor_count=1
        )
        await db.emerging_skills.insert_one(new_skill.model_dump())
    
    # Mark contribution as integrated
    await db.skill_contributions.update_one(
        {"id": contribution["id"]},
        {"$set": {"status": "integree"}}
    )

# ============== PASSEPORT DYNAMIQUE ENDPOINTS ==============

def calculate_completeness(passport: dict) -> int:
    """Calculate passport completeness score (0-100)"""
    score = 0
    if passport.get("professional_summary"): score += 12
    if passport.get("career_project"): score += 8
    if passport.get("motivations"): score += 5
    if passport.get("compatible_environments"): score += 5
    if passport.get("target_sectors"): score += 5
    comps = passport.get("competences", [])
    if len(comps) >= 1: score += 8
    if len(comps) >= 3: score += 7
    if len(comps) >= 5: score += 5
    exps = passport.get("experiences", [])
    if len(exps) >= 1: score += 8
    if len(exps) >= 3: score += 7
    learning = passport.get("learning_path", [])
    if len(learning) >= 1: score += 8
    if len(learning) >= 2: score += 5
    # Bonus for Lamri & Lubart evaluations
    evaluated = sum(1 for c in comps if any(c.get("components", {}).get(k, 0) > 0 for k in ["connaissance", "cognition", "conation", "affection", "sensori_moteur"]))
    if evaluated >= 1: score += 5
    if evaluated >= 3: score += 7
    # Bonus for CCSP classification
    ccsp_classified = sum(1 for c in comps if c.get("ccsp_pole"))
    if ccsp_classified >= 1: score += 5
    return min(score, 100)

async def aggregate_passport_from_sources(token_id: str) -> dict:
    """Aggregate passport data from all platform sources"""
    aggregated = {"competences": [], "experiences": [], "learning_path": []}
    seen_comp_names = set()
    seen_exp_titles = set()

    # 1. From coffre-fort documents
    docs = await db.documents.find({"user_token": token_id}, {"_id": 0}).to_list(50)
    for doc in docs:
        for skill in doc.get("skills", []):
            if skill.lower() not in seen_comp_names:
                seen_comp_names.add(skill.lower())
                aggregated["competences"].append({
                    "id": str(uuid.uuid4()), "name": skill, "category": "technique",
                    "level": "intermediaire", "experience_years": 0, "proof": doc.get("title"),
                    "source": "coffre_fort", "is_emerging": False,
                    "added_at": datetime.now(timezone.utc).isoformat()
                })

    # 2. From learning modules
    profile = await db.profiles.find_one({"token_id": token_id}, {"_id": 0})
    if profile:
        for skill_data in profile.get("skills", []):
            sname = skill_data.get("name", "") if isinstance(skill_data, dict) else str(skill_data)
            if sname.lower() not in seen_comp_names:
                seen_comp_names.add(sname.lower())
                level = skill_data.get("level", "intermediaire") if isinstance(skill_data, dict) else "intermediaire"
                aggregated["competences"].append({
                    "id": str(uuid.uuid4()), "name": sname, "category": "technique",
                    "level": level, "experience_years": 0, "proof": None,
                    "source": "profil", "is_emerging": False,
                    "added_at": datetime.now(timezone.utc).isoformat()
                })

    modules = await db.modules.find({}, {"_id": 0}).to_list(50)
    for mod in modules:
        aggregated["learning_path"].append({
            "id": str(uuid.uuid4()), "title": mod.get("title", ""),
            "provider": "RE'ACTIF PRO", "skills_acquired": mod.get("skills", []),
            "status": "en_cours", "completion_date": None, "badge": None,
            "source": "plateforme"
        })

    # 3. From Ubuntoo signals (emerging skills)
    signals = await db.ubuntoo_signals.find(
        {"validation_status": {"$in": ["validee_humain", "integree"]}}, {"_id": 0}
    ).to_list(20)
    for signal in signals:
        if signal.get("signal_type") == "competence_emergente" and signal["name"].lower() not in seen_comp_names:
            seen_comp_names.add(signal["name"].lower())
            aggregated["competences"].append({
                "id": str(uuid.uuid4()), "name": signal["name"], "category": "technique",
                "level": "debutant", "experience_years": 0, "proof": None,
                "source": "ubuntoo", "is_emerging": True,
                "added_at": datetime.now(timezone.utc).isoformat()
            })

    # 4. From contributions
    contributions = await db.contributions.find(
        {"user_token": token_id, "status": {"$in": ["validee_ia", "validee"]}}, {"_id": 0}
    ).to_list(20)
    for contrib in contributions:
        sname = contrib.get("skill_name", "")
        if sname and sname.lower() not in seen_comp_names:
            seen_comp_names.add(sname.lower())
            aggregated["competences"].append({
                "id": str(uuid.uuid4()), "name": sname, "category": "technique",
                "level": "intermediaire", "experience_years": 0, "proof": None,
                "source": "contribution", "is_emerging": True,
                "added_at": datetime.now(timezone.utc).isoformat()
            })

    return aggregated

async def generate_passerelles_with_ai(competences: List[dict], sectors: List[str]) -> List[dict]:
    """Use AI to suggest career pathways based on passport competences"""
    if not EMERGENT_LLM_KEY or not competences:
        return []
    try:
        skills_list = ", ".join([c.get("name", "") for c in competences[:15]])
        sectors_str = ", ".join(sectors[:5]) if sectors else "tous secteurs"

        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"passerelle-{uuid.uuid4()}",
            system_message="Tu es un conseiller en évolution professionnelle français expert. Analyse les compétences et suggère des passerelles professionnelles réalistes. Réponds UNIQUEMENT en JSON valide: un array de max 5 objets avec les clés: job_name (str), compatibility_score (float 0-1), shared_skills (list str), skills_to_acquire (list str max 3), training_needed (str court), accessibility (str: accessible/formation_courte/formation_longue), sector (str)."
        ).with_model("openai", "gpt-5.2")

        response = await chat.send_message(UserMessage(text=f"""Compétences de la personne: {skills_list}
Secteurs d'intérêt: {sectors_str}

Propose 5 passerelles professionnelles réalistes."""))

        import json
        try:
            result = json.loads(response)
            if isinstance(result, list):
                return result[:5]
            return result.get("passerelles", result.get("pathways", []))[:5]
        except:
            return []
    except Exception as e:
        logging.error(f"Passerelles AI error: {e}")
        return []

@api_router.get("/passport")
async def get_passport(token: str):
    """Get or create the user's dynamic passport"""
    token_doc = await get_current_token(token)

    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not passport:
        # Create new passport with aggregated data
        aggregated = await aggregate_passport_from_sources(token_doc["id"])
        new_passport = Passport(token_id=token_doc["id"])
        passport_data = new_passport.model_dump()
        passport_data["competences"] = aggregated["competences"]
        passport_data["learning_path"] = aggregated["learning_path"]
        passport_data["completeness_score"] = calculate_completeness(passport_data)
        await db.passports.insert_one(passport_data)
        passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})

    # Count sources
    sources_count = {}
    for c in passport.get("competences", []):
        src = c.get("source", "declaratif")
        sources_count[src] = sources_count.get(src, 0) + 1

    passport["sources_count"] = sources_count
    passport["total_competences"] = len(passport.get("competences", []))
    passport["total_experiences"] = len(passport.get("experiences", []))
    passport["total_learning"] = len(passport.get("learning_path", []))
    passport["emerging_count"] = len([c for c in passport.get("competences", []) if c.get("is_emerging")])

    return passport

@api_router.post("/passport/refresh")
async def refresh_passport(token: str):
    """Refresh passport by re-aggregating from all sources"""
    token_doc = await get_current_token(token)
    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not passport:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")

    aggregated = await aggregate_passport_from_sources(token_doc["id"])

    # Merge: keep existing user-declared competences, add new from sources
    existing_names = {c.get("name", "").lower() for c in passport.get("competences", []) if c.get("source") == "declaratif"}
    new_comps = [c for c in aggregated["competences"] if c.get("name", "").lower() not in existing_names]
    declared_comps = [c for c in passport.get("competences", []) if c.get("source") == "declaratif"]

    all_comps = declared_comps + new_comps
    passport["competences"] = all_comps
    passport["learning_path"] = aggregated["learning_path"]
    passport["completeness_score"] = calculate_completeness(passport)
    passport["last_updated"] = datetime.now(timezone.utc).isoformat()

    await db.passports.update_one(
        {"token_id": token_doc["id"]},
        {"$set": {
            "competences": passport["competences"],
            "learning_path": passport["learning_path"],
            "completeness_score": passport["completeness_score"],
            "last_updated": passport["last_updated"]
        }}
    )
    return {"message": "Passeport actualisé", "completeness_score": passport["completeness_score"]}

@api_router.put("/passport/profile")
async def update_passport_profile(token: str, data: UpdatePassportProfileRequest):
    """Update passport profile section"""
    token_doc = await get_current_token(token)
    update = {}
    if data.professional_summary is not None: update["professional_summary"] = data.professional_summary
    if data.career_project is not None: update["career_project"] = data.career_project
    if data.motivations is not None: update["motivations"] = data.motivations
    if data.compatible_environments is not None: update["compatible_environments"] = data.compatible_environments
    if data.target_sectors is not None: update["target_sectors"] = data.target_sectors

    if not update:
        raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")

    update["last_updated"] = datetime.now(timezone.utc).isoformat()
    result = await db.passports.update_one({"token_id": token_doc["id"]}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")

    # Recalculate completeness
    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    new_score = calculate_completeness(passport)
    await db.passports.update_one({"token_id": token_doc["id"]}, {"$set": {"completeness_score": new_score}})

    return {"message": "Profil mis à jour", "completeness_score": new_score}

@api_router.post("/passport/competences")
async def add_passport_competence(token: str, data: AddCompetenceRequest):
    """Add a competence to the passport"""
    token_doc = await get_current_token(token)

    components = data.components or {"connaissance": 0, "cognition": 0, "conation": 0, "affection": 0, "sensori_moteur": 0}
    new_comp = PassportCompetence(
        name=data.name, nature=data.nature, category=data.category, level=data.level,
        experience_years=data.experience_years, proof=data.proof, source="declaratif",
        components=components,
        ccsp_pole=data.ccsp_pole or "",
        ccsp_degree=data.ccsp_degree or "",
        linked_qualites=data.linked_qualites,
        linked_valeurs=data.linked_valeurs,
        linked_vertus=data.linked_vertus
    ).model_dump()

    result = await db.passports.update_one(
        {"token_id": token_doc["id"]},
        {"$push": {"competences": new_comp}, "$set": {"last_updated": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")

    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    new_score = calculate_completeness(passport)
    await db.passports.update_one({"token_id": token_doc["id"]}, {"$set": {"completeness_score": new_score}})

    return {"message": "Compétence ajoutée", "competence": new_comp, "completeness_score": new_score}

@api_router.post("/passport/experiences")
async def add_passport_experience(token: str, data: AddExperienceRequest):
    """Add an experience to the passport"""
    token_doc = await get_current_token(token)

    new_exp = PassportExperience(
        title=data.title, organization=data.organization, description=data.description,
        skills_used=data.skills_used, achievements=data.achievements,
        start_date=data.start_date, end_date=data.end_date, is_current=data.is_current,
        experience_type=data.experience_type, source="declaratif"
    ).model_dump()

    result = await db.passports.update_one(
        {"token_id": token_doc["id"]},
        {"$push": {"experiences": new_exp}, "$set": {"last_updated": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")

    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    new_score = calculate_completeness(passport)
    await db.passports.update_one({"token_id": token_doc["id"]}, {"$set": {"completeness_score": new_score}})

    return {"message": "Expérience ajoutée", "experience": new_exp, "completeness_score": new_score}

@api_router.delete("/passport/competences/{comp_id}")
async def delete_passport_competence(comp_id: str, token: str):
    """Remove a competence from the passport"""
    token_doc = await get_current_token(token)
    result = await db.passports.update_one(
        {"token_id": token_doc["id"]},
        {"$pull": {"competences": {"id": comp_id}}, "$set": {"last_updated": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")
    return {"message": "Compétence supprimée"}

@api_router.delete("/passport/experiences/{exp_id}")
async def delete_passport_experience(exp_id: str, token: str):
    """Remove an experience from the passport"""
    token_doc = await get_current_token(token)
    result = await db.passports.update_one(
        {"token_id": token_doc["id"]},
        {"$pull": {"experiences": {"id": exp_id}}, "$set": {"last_updated": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")
    return {"message": "Expérience supprimée"}

@api_router.get("/passport/passerelles")
async def get_passport_passerelles(token: str):
    """Get AI-suggested career pathways"""
    token_doc = await get_current_token(token)
    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not passport:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")

    passerelles = await generate_passerelles_with_ai(
        passport.get("competences", []),
        passport.get("target_sectors", [])
    )

    await db.passports.update_one(
        {"token_id": token_doc["id"]},
        {"$set": {"passerelles": passerelles, "last_updated": datetime.now(timezone.utc).isoformat()}}
    )

    return {"passerelles": passerelles}

@api_router.put("/passport/sharing")
async def update_passport_sharing(token: str, data: SharePassportRequest):
    """Update passport sharing settings"""
    token_doc = await get_current_token(token)
    sharing = {
        "is_public": data.is_public,
        "shared_sections": data.shared_sections,
        "shared_with": data.shared_with,
        "share_expiry": data.share_expiry
    }
    result = await db.passports.update_one(
        {"token_id": token_doc["id"]},
        {"$set": {"sharing": sharing, "last_updated": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")
    return {"message": "Paramètres de partage mis à jour", "sharing": sharing}

@api_router.put("/passport/competences/{comp_id}/evaluate")
async def evaluate_competence(comp_id: str, token: str, data: EvaluateCompetenceRequest):
    """Evaluate a competence using Lamri & Lubart 5-component model and CCSP"""
    token_doc = await get_current_token(token)
    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not passport:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")

    # Validate component values (0-5)
    valid_keys = {"connaissance", "cognition", "conation", "affection", "sensori_moteur"}
    components = {}
    for key in valid_keys:
        val = data.components.get(key, 0)
        components[key] = max(0, min(5, val))

    # Find and update the competence
    comps = passport.get("competences", [])
    found = False
    for comp in comps:
        if comp.get("id") == comp_id:
            comp["components"] = components
            if data.ccsp_pole:
                comp["ccsp_pole"] = data.ccsp_pole
            if data.ccsp_degree:
                comp["ccsp_degree"] = data.ccsp_degree
            found = True
            break

    if not found:
        raise HTTPException(status_code=404, detail="Compétence non trouvée")

    await db.passports.update_one(
        {"token_id": token_doc["id"]},
        {"$set": {"competences": comps, "last_updated": datetime.now(timezone.utc).isoformat()}}
    )

    return {"message": "Évaluation enregistrée", "competence_id": comp_id, "components": components}

@api_router.get("/passport/diagnostic")
async def get_ccsp_diagnostic(token: str):
    """Generate a CCSP diagnostic based on all passport competences"""
    token_doc = await get_current_token(token)
    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not passport:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")

    comps = passport.get("competences", [])
    total = len(comps)
    if total == 0:
        return {
            "total_competences": 0,
            "evaluated_count": 0,
            "lamri_lubart_profile": {"connaissance": 0, "cognition": 0, "conation": 0, "affection": 0, "sensori_moteur": 0},
            "ccsp_distribution": {"poles": {}, "degrees": {}},
            "recommendations": []
        }

    # Aggregate Lamri & Lubart components
    ll_totals = {"connaissance": 0, "cognition": 0, "conation": 0, "affection": 0, "sensori_moteur": 0}
    evaluated_count = 0
    for comp in comps:
        cdata = comp.get("components", {})
        has_evaluation = any(cdata.get(k, 0) > 0 for k in ll_totals)
        if has_evaluation:
            evaluated_count += 1
            for k in ll_totals:
                ll_totals[k] += cdata.get(k, 0)

    ll_avg = {}
    for k, v in ll_totals.items():
        ll_avg[k] = round(v / max(evaluated_count, 1), 1)

    # CCSP distribution
    poles = {"realisation": 0, "interaction": 0, "initiative": 0}
    degrees = {"imitation": 0, "adaptation": 0, "transposition": 0}
    for comp in comps:
        pole = comp.get("ccsp_pole", "")
        degree = comp.get("ccsp_degree", "")
        if pole in poles:
            poles[pole] += 1
        if degree in degrees:
            degrees[degree] += 1

    # Generate recommendations
    recommendations = []
    if ll_avg.get("connaissance", 0) < 2:
        recommendations.append({"type": "formation", "message": "Renforcez vos savoirs théoriques par des formations ou lectures spécialisées.", "component": "connaissance"})
    if ll_avg.get("cognition", 0) < 2:
        recommendations.append({"type": "formation", "message": "Développez vos capacités d'analyse et de raisonnement critique.", "component": "cognition"})
    if ll_avg.get("conation", 0) < 2:
        recommendations.append({"type": "accompagnement", "message": "Travaillez votre motivation et votre engagement par un accompagnement personnalisé.", "component": "conation"})
    if ll_avg.get("affection", 0) < 2:
        recommendations.append({"type": "developpement", "message": "Renforcez votre intelligence émotionnelle et votre empathie.", "component": "affection"})
    if ll_avg.get("sensori_moteur", 0) < 2:
        recommendations.append({"type": "pratique", "message": "Augmentez la pratique terrain pour développer vos habiletés techniques.", "component": "sensori_moteur"})

    if poles.get("initiative", 0) == 0 and total > 2:
        recommendations.append({"type": "ccsp", "message": "Aucune compétence d'initiative identifiée. Explorez l'autonomie et l'innovation.", "component": "initiative"})
    if degrees.get("transposition", 0) == 0 and total > 2:
        recommendations.append({"type": "ccsp", "message": "Développez votre capacité à transposer vos compétences dans de nouveaux contextes.", "component": "transposition"})

    # Nature distribution (savoir-faire vs savoir-être)
    nature_dist = {"savoir_faire": 0, "savoir_etre": 0, "non_classee": 0}
    for comp in comps:
        n = comp.get("nature", "")
        if n == "savoir_faire":
            nature_dist["savoir_faire"] += 1
        elif n == "savoir_etre":
            nature_dist["savoir_etre"] += 1
        else:
            nature_dist["non_classee"] += 1

    # Recommendations based on nature balance
    if nature_dist["savoir_etre"] == 0 and total > 2:
        recommendations.append({"type": "orientation", "message": "Identifiez vos savoir-être (soft skills) pour enrichir votre stratégie d'orientation professionnelle.", "component": "savoir_etre"})
    if nature_dist["savoir_faire"] == 0 and total > 2:
        recommendations.append({"type": "orientation", "message": "Ajoutez vos compétences techniques (savoir-faire) pour mieux cibler les métiers compatibles.", "component": "savoir_faire"})
    if nature_dist["non_classee"] > 0:
        recommendations.append({"type": "classification", "message": f"{nature_dist['non_classee']} compétence(s) non classée(s). Précisez leur nature (savoir-faire ou savoir-être) pour un meilleur diagnostic.", "component": "nature"})

    return {
        "total_competences": total,
        "evaluated_count": evaluated_count,
        "lamri_lubart_profile": ll_avg,
        "ccsp_distribution": {"poles": poles, "degrees": degrees},
        "nature_distribution": nature_dist,
        "recommendations": recommendations
    }

# ============== CV ANALYSIS & GENERATION ==============

async def extract_text_from_upload(file: UploadFile) -> str:
    """Extract text from uploaded PDF or DOCX file"""
    content = await file.read()
    text = ""
    if file.filename.lower().endswith(".pdf"):
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
    elif file.filename.lower().endswith((".docx", ".doc")):
        import docx
        doc = docx.Document(io.BytesIO(content))
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        text = content.decode("utf-8", errors="ignore")
    return text.strip()


async def _llm_call_with_retry(system_msg: str, user_msg: str, max_retries: int = 2) -> dict:
    """Make an LLM call with retry logic and JSON parsing."""
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"cv-{uuid.uuid4()}",
                system_message=system_msg
            ).with_model("openai", "gpt-5.2")
            response = await chat.send_message(UserMessage(text=user_msg))
            raw = response.strip() if isinstance(response, str) else response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
                raw = raw.strip()
            return json.loads(raw)
        except json.JSONDecodeError as e:
            last_error = f"Réponse IA non valide (tentative {attempt+1})"
            logging.warning(f"CV analysis JSON error attempt {attempt+1}: {e}")
        except Exception as e:
            last_error = str(e)
            logging.warning(f"CV analysis LLM error attempt {attempt+1}: {e}")
    raise Exception(f"Erreur IA après {max_retries+1} tentatives: {last_error}")


def _extract_text_from_bytes(content: bytes, filename: str) -> str:
    """Extract text from file bytes (PDF, DOCX, TXT)"""
    text = ""
    if filename.lower().endswith(".pdf"):
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
    elif filename.lower().endswith((".docx", ".doc")):
        import docx
        doc = docx.Document(io.BytesIO(content))
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        text = content.decode("utf-8", errors="ignore")
    return text.strip()


async def _run_cv_analysis(job_id: str, token_id: str, file_content: bytes, filename: str, text_ready: bool = False):
    """Background task: extract text, run CV analysis and save results to DB."""
    try:
        await db.cv_jobs.update_one({"job_id": job_id}, {"$set": {"status": "analyzing", "step": "Extraction du texte..."}})

        if text_ready:
            cv_text = file_content.decode("utf-8", errors="ignore")
        else:
            cv_text = _extract_text_from_bytes(file_content, filename)
        if not cv_text or len(cv_text) < 50:
            await db.cv_jobs.update_one({"job_id": job_id}, {"$set": {"status": "failed", "error": "Le fichier ne contient pas assez de texte exploitable", "step": "Erreur"}})
            return

        cv_excerpt = cv_text[:6000]

        await db.cv_jobs.update_one({"job_id": job_id}, {"$set": {"step": "Analyse des compétences..."}})

        # CALL 1: Analyse des compétences
        analysis = await _llm_call_with_retry(
            system_msg="""Tu es un expert RH. Analyse ce CV. Réponds UNIQUEMENT en JSON valide (pas de markdown).
Structure exacte:
{
  "profile": {"professional_summary": "2-3 phrases", "career_project": "string", "motivations": [], "compatible_environments": [], "target_sectors": []},
  "savoir_faire": [{"name": "string", "category": "technique|transversale|transferable|sectorielle", "level": "debutant|intermediaire|avance|expert", "ccsp_pole": "realisation|interaction|initiative", "ccsp_degree": "imitation|adaptation|transposition"}],
  "savoir_etre": [{"name": "string", "category": "transversale|transferable", "level": "debutant|intermediaire|avance|expert", "linked_qualites": [], "linked_valeurs": [], "linked_vertus": []}],
  "competences_transversales": ["communication", "travail en equipe", ...],
  "competences_transferables": [],
  "experiences": [{"title": "string", "organization": "string", "description": "string", "experience_type": "professionnel|personnel|benevole|projet", "skills_used": [], "achievements": []}],
  "formations_suggestions": [{"title": "string", "reason": "string", "priority": "haute|moyenne|basse", "skills_to_gain": []}],
  "offres_emploi_suggerees": [{"titre": "string", "secteur": "string", "type_contrat": "CDI|CDD|Interim|Alternance", "description_courte": "string", "competences_requises": []}]
}
IMPORTANT:
- competences_transversales: liste de 5-10 compétences transversales identifiées (communication, adaptabilité, gestion du temps, travail en équipe, résolution de problèmes, etc.)
- offres_emploi_suggerees: liste de 3-5 offres d'emploi pertinentes basées sur le profil, le secteur et les compétences du candidat
Valeurs IDs: autonomie, stimulation, hedonisme, realisation_de_soi, pouvoir, securite, conformite, tradition, bienveillance, universalisme.
Vertus: sagesse, courage, humanite, justice, temperance, transcendance.""",
            user_msg=f"Analyse ce CV:\n\n{cv_excerpt}"
        )

        await db.cv_jobs.update_one({"job_id": job_id}, {"$set": {"step": "Génération des modèles de CV..."}})

        # CALL 2: Génération des 4 modèles de CV
        try:
            cv_gen = await _llm_call_with_retry(
                system_msg="""Tu es un rédacteur de CV professionnel. Génère 4 versions d'un CV. Réponds UNIQUEMENT en JSON valide.
Structure: {"cv_classique": "texte complet", "cv_competences": "texte complet", "cv_fonctionnel": "texte complet", "cv_mixte": "texte complet"}
- cv_classique: chronologique, sobre, professionnel
- cv_competences: axé savoir-faire et savoir-être par domaine
- cv_fonctionnel: par domaines de compétences, sans chronologie
- cv_mixte: parcours + compétences transférables""",
                user_msg=f"Génère 4 versions de CV pour ce profil:\n\n{cv_excerpt}"
            )
        except Exception:
            logging.warning("CV model generation failed, continuing with analysis only")
            cv_gen = {"cv_classique": "", "cv_competences": "", "cv_fonctionnel": "", "cv_mixte": ""}

        await db.cv_jobs.update_one({"job_id": job_id}, {"$set": {"step": "Remplissage du passeport..."}})

        # Save CV models
        cv_models = {
            "classique": cv_gen.get("cv_classique", ""),
            "competences": cv_gen.get("cv_competences", ""),
            "fonctionnel": cv_gen.get("cv_fonctionnel", ""),
            "mixte": cv_gen.get("cv_mixte", ""),
        }
        await db.cv_models.update_one(
            {"token_id": token_id},
            {"$set": {"token_id": token_id, "models": cv_models, "original_filename": filename, "analyzed_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )

        # Auto-fill Passport
        passport = await db.passports.find_one({"token_id": token_id})
        if not passport:
            passport = {"token_id": token_id, "professional_summary": "", "career_project": "", "motivations": [], "compatible_environments": [], "target_sectors": [], "competences": [], "experiences": [], "learning_path": [], "passerelles": [], "sharing": {"is_public": False}, "created_at": datetime.now(timezone.utc).isoformat()}
            await db.passports.insert_one(passport)

        new_competences = list(passport.get("competences", []))
        existing_names = {c.get("name", "").lower() for c in new_competences}
        for sf in analysis.get("savoir_faire", []):
            if sf.get("name", "").lower() not in existing_names:
                new_competences.append(PassportCompetence(name=sf["name"], nature="savoir_faire", category=sf.get("category", "technique"), level=sf.get("level", "intermediaire"), source="ia_detectee", ccsp_pole=sf.get("ccsp_pole", ""), ccsp_degree=sf.get("ccsp_degree", "")).model_dump())
                existing_names.add(sf["name"].lower())
        for se in analysis.get("savoir_etre", []):
            if se.get("name", "").lower() not in existing_names:
                new_competences.append(PassportCompetence(name=se["name"], nature="savoir_etre", category=se.get("category", "transversale"), level=se.get("level", "intermediaire"), source="ia_detectee", linked_qualites=se.get("linked_qualites", []), linked_valeurs=se.get("linked_valeurs", []), linked_vertus=se.get("linked_vertus", [])).model_dump())
                existing_names.add(se["name"].lower())

        new_experiences = list(passport.get("experiences", []))
        existing_exp_titles = {e.get("title", "").lower() for e in new_experiences}
        for exp in analysis.get("experiences", []):
            if exp.get("title", "").lower() not in existing_exp_titles:
                new_experiences.append(PassportExperience(title=exp["title"], organization=exp.get("organization", ""), description=exp.get("description", ""), experience_type=exp.get("experience_type", "professionnel"), skills_used=exp.get("skills_used", []), achievements=exp.get("achievements", []), source="ia_detectee").model_dump())
                existing_exp_titles.add(exp["title"].lower())

        new_learning = list(passport.get("learning_path", []))
        for fs in analysis.get("formations_suggestions", []):
            new_learning.append({"title": fs.get("title", ""), "provider": f"Suggestion IA - Priorité {fs.get('priority', 'moyenne')}", "status": "suggere", "skills_acquired": fs.get("skills_to_gain", []), "reason": fs.get("reason", ""), "source": "ia_detectee"})

        profile_data = analysis.get("profile", {})
        update_fields = {"competences": new_competences, "experiences": new_experiences, "learning_path": new_learning, "last_updated": datetime.now(timezone.utc).isoformat()}
        if profile_data.get("professional_summary") and not passport.get("professional_summary"):
            update_fields["professional_summary"] = profile_data["professional_summary"]
        if profile_data.get("career_project") and not passport.get("career_project"):
            update_fields["career_project"] = profile_data["career_project"]
        if profile_data.get("motivations") and not passport.get("motivations"):
            update_fields["motivations"] = profile_data["motivations"]
        if profile_data.get("compatible_environments") and not passport.get("compatible_environments"):
            update_fields["compatible_environments"] = profile_data["compatible_environments"]
        if profile_data.get("target_sectors") and not passport.get("target_sectors"):
            update_fields["target_sectors"] = profile_data["target_sectors"]

        merged = {**passport, **update_fields}
        update_fields["completeness_score"] = calculate_completeness(merged)
        await db.passports.update_one({"token_id": token_id}, {"$set": update_fields})

        # Store result in job
        result = {
            "message": "CV analysé avec succès",
            "filename": filename,
            "savoir_faire_count": len(analysis.get("savoir_faire", [])),
            "savoir_etre_count": len(analysis.get("savoir_etre", [])),
            "experiences_count": len(analysis.get("experiences", [])),
            "formations_suggestions": analysis.get("formations_suggestions", []),
            "competences_transversales": analysis.get("competences_transversales", []),
            "competences_transferables": analysis.get("competences_transferables", []),
            "offres_emploi_suggerees": analysis.get("offres_emploi_suggerees", []),
            "cv_models_generated": list(cv_models.keys()),
            "completeness_score": update_fields.get("completeness_score", 0),
        }
        await db.cv_jobs.update_one({"job_id": job_id}, {"$set": {"status": "completed", "result": result, "step": "Terminé"}})
        logging.info(f"CV analysis job {job_id} completed successfully")

    except Exception as e:
        logging.error(f"CV analysis job {job_id} failed: {e}")
        await db.cv_jobs.update_one({"job_id": job_id}, {"$set": {"status": "failed", "error": str(e), "step": "Erreur"}})


@api_router.post("/cv/analyze")
async def analyze_cv(token: str, file: UploadFile = File(...)):
    """Upload CV, start background analysis, return job_id immediately"""
    token_doc = await get_current_token(token)

    # Validate file type
    ext = (file.filename or "").lower().split(".")[-1]
    if ext not in ("pdf", "docx", "doc", "txt"):
        raise HTTPException(status_code=400, detail="Format non supporté. Utilisez PDF, DOCX ou TXT.")

    # Read raw content (fast)
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 10 Mo)")

    job_id = str(uuid.uuid4())
    await db.cv_jobs.insert_one({
        "job_id": job_id,
        "token_id": token_doc["id"],
        "filename": file.filename,
        "status": "started",
        "step": "Démarrage de l'analyse...",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    # Launch background task with raw file bytes
    asyncio.create_task(_run_cv_analysis(job_id, token_doc["id"], file_content, file.filename))

    return {"job_id": job_id, "status": "started", "message": "Analyse lancée en arrière-plan"}


class CvTextPayload(BaseModel):
    text: str
    filename: str = "cv.txt"


@api_router.post("/cv/extract-text")
async def extract_cv_text(token: str, file: UploadFile = File(...)):
    """Extract text from PDF/DOCX - lightweight, no AI, fast response"""
    await get_current_token(token)
    content = await file.read()
    text = _extract_text_from_bytes(content, file.filename or "file.txt")
    if not text or len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Impossible d'extraire du texte de ce fichier")
    return {"text": text, "length": len(text)}


class CvBase64Payload(BaseModel):
    data: str
    filename: str = "cv.pdf"


@api_router.post("/cv/extract-text-b64")
async def extract_cv_text_base64(token: str, payload: CvBase64Payload):
    """Extract text from base64-encoded file. No multipart upload - avoids proxy issues."""
    await get_current_token(token)
    import base64
    try:
        content = base64.b64decode(payload.data)
    except Exception:
        raise HTTPException(status_code=400, detail="Données invalides")
    text = _extract_text_from_bytes(content, payload.filename)
    if not text or len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Impossible d'extraire du texte de ce fichier")
    return {"text": text, "length": len(text)}


@api_router.post("/cv/analyze-text")
async def analyze_cv_text(token: str, payload: CvTextPayload):
    """Analyze pre-extracted CV text. No file upload needed - avoids proxy issues."""
    token_doc = await get_current_token(token)

    if not payload.text or len(payload.text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Le texte du CV est trop court pour être analysé")

    job_id = str(uuid.uuid4())
    await db.cv_jobs.insert_one({
        "job_id": job_id,
        "token_id": token_doc["id"],
        "filename": payload.filename,
        "status": "started",
        "step": "Démarrage de l'analyse...",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    # Launch background task with text directly (no file extraction needed)
    asyncio.create_task(_run_cv_analysis(job_id, token_doc["id"], payload.text.encode("utf-8"), payload.filename, text_ready=True))

    return {"job_id": job_id, "status": "started", "message": "Analyse lancée en arrière-plan"}


@api_router.get("/cv/analyze/status")
async def get_cv_analysis_status(token: str, job_id: str):
    """Poll for CV analysis job status"""
    token_doc = await get_current_token(token)
    job = await db.cv_jobs.find_one({"job_id": job_id, "token_id": token_doc["id"]}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job non trouvé")
    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "step": job.get("step", ""),
        "result": job.get("result"),
        "error": job.get("error"),
    }


@api_router.get("/cv/latest-analysis")
async def get_latest_cv_analysis(token: str):
    """Get the most recent completed CV analysis for this user"""
    token_doc = await get_current_token(token)
    job = await db.cv_jobs.find_one(
        {"token_id": token_doc["id"], "status": "completed"},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    if not job or not job.get("result"):
        return {"has_analysis": False}
    return {"has_analysis": True, "result": job["result"]}


@api_router.get("/cv/models")
async def get_cv_models(token: str):
    """Get generated CV models for the user"""
    token_doc = await get_current_token(token)
    cv_data = await db.cv_models.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not cv_data:
        return {"models": {}, "analyzed_at": None, "original_filename": None}
    return {
        "models": cv_data.get("models", {}),
        "analyzed_at": cv_data.get("analyzed_at"),
        "original_filename": cv_data.get("original_filename"),
    }


# ============== REFERENTIEL & ARCHÉOLOGIE DES COMPÉTENCES ==============

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

# Mapping savoir-être → qualités humaines → valeurs → vertus (from user's "archéologie des compétences")
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


@api_router.get("/referentiel/archeologie")
async def get_referentiel_archeologie():
    """Get the full archaeology of competences hierarchy"""
    return {
        "vertus": REFERENTIEL_VERTUS,
        "valeurs": REFERENTIEL_VALEURS,
        "filieres": REFERENTIEL_FILIERES,
        "savoir_etre_map": ARCHEOLOGIE_SAVOIR_ETRE,
    }

@api_router.get("/referentiel/filieres")
async def get_referentiel_filieres():
    """Get all professional sectors/pathways"""
    return {"filieres": REFERENTIEL_FILIERES}

@api_router.get("/referentiel/vertus")
async def get_referentiel_vertus():
    """Get vertues with their full chain"""
    return {"vertus": REFERENTIEL_VERTUS, "valeurs": REFERENTIEL_VALEURS}


# ===== Explorateur des Filières Professionnelles =====

@api_router.get("/referentiel/explorer")
async def get_explorer_filieres():
    """Get all filières with their secteurs and metier names"""
    all_data = await db.referentiel_metiers.find({}, {"_id": 0, "name": 1, "id": 1, "secteurs.name": 1, "secteurs.metiers.name": 1}).to_list(100)
    for f in all_data:
        for s in f.get("secteurs", []):
            metier_names = [m.get("name", "") for m in s.get("metiers", [])]
            s["metiers"] = metier_names
            s["metiers_count"] = len(metier_names)
    return {"filieres": all_data, "total_filieres": len(all_data)}


@api_router.get("/referentiel/explorer/secteur/{secteur_name}")
async def get_explorer_secteur(secteur_name: str):
    """Get metiers for a specific secteur"""
    doc = await db.referentiel_metiers.find_one(
        {"secteurs.name": secteur_name}, {"_id": 0}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Secteur non trouvé")
    for s in doc.get("secteurs", []):
        if s["name"] == secteur_name:
            return {
                "filiere": doc["name"],
                "secteur": secteur_name,
                "metiers": s.get("metiers", []),
            }
    raise HTTPException(status_code=404, detail="Secteur non trouvé")


@api_router.get("/referentiel/explorer/metier/{metier_name}")
async def get_explorer_metier(metier_name: str):
    """Get full detail for a specific metier with chains and similar metiers"""
    all_data = await db.referentiel_metiers.find({}, {"_id": 0}).to_list(100)
    found = None
    same_secteur_metiers = []
    for f in all_data:
        for s in f.get("secteurs", []):
            for m in s.get("metiers", []):
                if m["name"].lower() == metier_name.lower():
                    found = {"filiere": f["name"], "secteur": s["name"], "metier": m}
                    # Collect other metiers in same secteur
                    same_secteur_metiers = [om["name"] for om in s.get("metiers", []) if om["name"].lower() != metier_name.lower()]
    if not found:
        raise HTTPException(status_code=404, detail="Métier non trouvé")
    found["metiers_similaires"] = same_secteur_metiers
    return found


@api_router.get("/referentiel/explorer/search")
async def search_explorer(q: str):
    """Search across filieres, secteurs, metiers, savoirs"""
    q_lower = q.lower()
    results = {"filieres": [], "secteurs": [], "metiers": [], "savoirs_faire": [], "savoirs_etre": []}
    all_data = await db.referentiel_metiers.find({}, {"_id": 0}).to_list(100)
    for f in all_data:
        if q_lower in f["name"].lower():
            results["filieres"].append({"name": f["name"], "type": "filiere"})
        for s in f.get("secteurs", []):
            if q_lower in s["name"].lower():
                results["secteurs"].append({"name": s["name"], "filiere": f["name"], "type": "secteur"})
            for m in s.get("metiers", []):
                if q_lower in m["name"].lower():
                    results["metiers"].append({"name": m["name"], "secteur": s["name"], "filiere": f["name"], "type": "metier"})
                for sf in m.get("savoirs_faire", []):
                    if q_lower in sf["name"].lower():
                        results["savoirs_faire"].append({"name": sf["name"], "metier": m["name"], "type": "savoir_faire"})
                for se in m.get("savoirs_etre", []):
                    if q_lower in se["name"].lower():
                        results["savoirs_etre"].append({"name": se["name"], "metier": m["name"], "type": "savoir_etre"})
    return results


@api_router.get("/referentiel/explorer/stats")
async def get_explorer_stats():
    """Get overall statistics for the referentiel"""
    all_data = await db.referentiel_metiers.find({}, {"_id": 0}).to_list(100)
    n_filieres = len(all_data)
    n_secteurs = sum(len(f.get("secteurs", [])) for f in all_data)
    n_metiers = sum(len(m.get("metiers", [])) for f in all_data for m in f.get("secteurs", []))
    sf_set = set()
    se_set = set()
    for f in all_data:
        for s in f.get("secteurs", []):
            for m in s.get("metiers", []):
                for sf in m.get("savoirs_faire", []):
                    sf_set.add(sf["name"])
                for se in m.get("savoirs_etre", []):
                    se_set.add(se["name"])
    return {
        "filieres": n_filieres,
        "secteurs": n_secteurs,
        "metiers": n_metiers,
        "savoirs_faire": len(sf_set),
        "savoirs_etre": len(se_set),
    }


@api_router.post("/referentiel/explorer/generate")
async def generate_metier_fiche(token: str, payload: dict):
    """Generate a complete metier fiche using AI when not found in DB"""
    await get_current_token(token)
    metier_name = payload.get("metier", "").strip()
    if not metier_name or len(metier_name) < 2:
        raise HTTPException(status_code=400, detail="Nom de métier invalide")

    # Check cache first
    cached = await db.generated_metiers.find_one({"name_lower": metier_name.lower()}, {"_id": 0})
    if cached:
        return cached["data"]

    job_id = str(uuid.uuid4())
    await db.explorer_jobs.insert_one({"job_id": job_id, "metier": metier_name, "status": "started", "created_at": datetime.now(timezone.utc).isoformat()})

    asyncio.create_task(_generate_metier_fiche(job_id, metier_name))
    return {"job_id": job_id, "status": "started"}


@api_router.get("/referentiel/explorer/generate/status")
async def get_generate_status(token: str, job_id: str):
    """Poll for metier generation status"""
    await get_current_token(token)
    job = await db.explorer_jobs.find_one({"job_id": job_id}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job non trouvé")
    return {"job_id": job["job_id"], "status": job["status"], "result": job.get("result"), "error": job.get("error")}


async def _generate_metier_fiche(job_id: str, metier_name: str):
    """Background: generate complete metier fiche via AI"""
    try:
        await db.explorer_jobs.update_one({"job_id": job_id}, {"$set": {"status": "generating"}})
        result = await _llm_call_with_retry(
            system_msg="""Tu es un expert en référentiels métiers et en archéologie des compétences.
Pour le métier demandé, génère une fiche complète en JSON valide:
{
  "filiere": "nom de la filière professionnelle",
  "secteur": "secteur d'activité",
  "metier": {
    "name": "nom du métier",
    "mission": "description détaillée de la mission (2-3 phrases)",
    "savoirs_faire": [
      {"name": "savoir-faire", "capacite_technique": "description de la capacité technique associée"}
    ],
    "savoirs_etre": [
      {"name": "savoir-être", "capacite_professionnelle": "description de la capacité professionnelle", "qualites_humaines": ["qualité1"], "valeurs": ["id_valeur"], "vertus": ["id_vertu"]}
    ]
  },
  "metiers_similaires": ["métier1", "métier2", "métier3", "métier4", "métier5"]
}
Règles:
- 6 à 10 savoir-faire avec capacités techniques détaillées
- 5 à 8 savoir-être avec la chaîne complète (capacité pro → qualités → valeurs → vertus)
- 5 métiers similaires dans le même secteur
- IDs valeurs: autonomie, stimulation, hedonisme, realisation_de_soi, pouvoir, securite, conformite, tradition, bienveillance, universalisme
- IDs vertus: sagesse, courage, humanite, justice, temperance, transcendance""",
            user_msg=f"Génère la fiche métier complète pour : {metier_name}"
        )
        # Cache the result
        await db.generated_metiers.update_one(
            {"name_lower": metier_name.lower()},
            {"$set": {"name_lower": metier_name.lower(), "data": result, "created_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )
        await db.explorer_jobs.update_one({"job_id": job_id}, {"$set": {"status": "completed", "result": result}})
    except Exception as e:
        logging.error(f"Metier generation failed: {e}")
        await db.explorer_jobs.update_one({"job_id": job_id}, {"$set": {"status": "failed", "error": str(e)}})

@api_router.get("/passport/archeologie")
async def get_passport_archeologie(token: str):
    """For a user's competences, trace the full archaeology chain"""
    token_doc = await get_current_token(token)
    passport = await db.passports.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not passport:
        raise HTTPException(status_code=404, detail="Passeport non trouvé")

    comps = passport.get("competences", [])
    savoir_faire = [c for c in comps if c.get("nature") == "savoir_faire"]
    savoir_etre = [c for c in comps if c.get("nature") == "savoir_etre"]
    non_classees = [c for c in comps if not c.get("nature")]

    # Build archaeology chains for savoir-être
    chains = []
    for comp in savoir_etre:
        name = comp.get("name", "")
        # Try to find in the reference map
        ref = ARCHEOLOGIE_SAVOIR_ETRE.get(name, {})
        qualites = comp.get("linked_qualites", []) or ref.get("qualites", [])
        valeurs_ids = comp.get("linked_valeurs", []) or ref.get("valeurs", [])
        vertus_ids = comp.get("linked_vertus", []) or ref.get("vertus", [])
        valeurs_names = [v["name"] for v in REFERENTIEL_VALEURS if v["id"] in valeurs_ids]
        vertus_names = [v["name"] for v in REFERENTIEL_VERTUS if v["id"] in vertus_ids]
        chains.append({
            "competence": name,
            "nature": "savoir_etre",
            "qualites": qualites,
            "valeurs": valeurs_names,
            "vertus": vertus_names,
        })

    # Aggregate vertus coverage
    all_vertus = set()
    all_valeurs = set()
    for comp in savoir_etre:
        ref = ARCHEOLOGIE_SAVOIR_ETRE.get(comp.get("name", ""), {})
        for v in (comp.get("linked_vertus", []) or ref.get("vertus", [])):
            all_vertus.add(v)
        for v in (comp.get("linked_valeurs", []) or ref.get("valeurs", [])):
            all_valeurs.add(v)

    return {
        "summary": {
            "total": len(comps),
            "savoir_faire": len(savoir_faire),
            "savoir_etre": len(savoir_etre),
            "non_classees": len(non_classees),
            "vertus_covered": list(all_vertus),
            "valeurs_covered": list(all_valeurs),
        },
        "chains": chains,
        "savoir_faire_list": [{"id": c.get("id"), "name": c.get("name"), "category": c.get("category")} for c in savoir_faire],
        "savoir_etre_list": [{"id": c.get("id"), "name": c.get("name"), "category": c.get("category")} for c in savoir_etre],
        "non_classees_list": [{"id": c.get("id"), "name": c.get("name")} for c in non_classees],
    }

# ============== UBUNTOO INTELLIGENCE ENDPOINTS ==============

async def analyze_ubuntoo_exchanges_with_ai(exchanges: List[dict]) -> Dict[str, Any]:
    """Use AI to analyze Ubuntoo exchanges and detect signals"""
    if not EMERGENT_LLM_KEY:
        return {
            "detected_skills": ["Prompt Engineering", "No-Code"],
            "detected_tools": ["ChatGPT", "Notion"],
            "detected_practices": ["Automatisation de tâches"],
            "confidence": 0.6,
            "summary": "Analyse basique - IA non disponible"
        }
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"ubuntoo-{uuid.uuid4()}",
            system_message="Tu es un expert RH français spécialisé dans l'analyse des tendances du marché du travail. Analyse ces échanges professionnels anonymisés et identifie les signaux faibles sur l'évolution des compétences et des métiers. Réponds en JSON avec: detected_skills (list), detected_tools (list), detected_practices (list), transformations (list of {job, description}), confidence (0-1), summary (string)."
        ).with_model("openai", "gpt-5.2")

        summaries = "\n".join([f"- [{e.get('exchange_type','discussion')}] {e.get('content_summary','')}" for e in exchanges[:10]])
        prompt = f"""Analyse ces échanges anonymisés du réseau socio-professionnel Ubuntoo :

{summaries}

Identifie :
1. Les compétences émergentes mentionnées
2. Les nouveaux outils ou technologies
3. Les nouvelles pratiques professionnelles
4. Les transformations de métiers en cours
"""
        response = await chat.send_message(UserMessage(text=prompt))
        import json
        try:
            return json.loads(response)
        except:
            return {"detected_skills": [], "detected_tools": [], "detected_practices": [], "confidence": 0.6, "summary": response[:300]}
    except Exception as e:
        logging.error(f"Ubuntoo AI analysis error: {e}")
        return {"detected_skills": [], "detected_tools": [], "detected_practices": [], "confidence": 0.5, "summary": "Analyse automatique non disponible"}

@api_router.get("/ubuntoo/dashboard")
async def get_ubuntoo_dashboard():
    """Get Ubuntoo intelligence dashboard"""
    signals = await db.ubuntoo_signals.find({}, {"_id": 0}).to_list(100)
    exchanges = await db.ubuntoo_exchanges.find({}, {"_id": 0}).to_list(200)
    insights = await db.ubuntoo_insights.find({}, {"_id": 0}).to_list(50)

    # Compute stats
    total_signals = len(signals)
    detected = len([s for s in signals if s.get("validation_status") == "detectee"])
    analyzed = len([s for s in signals if s.get("validation_status") == "analysee_ia"])
    validated = len([s for s in signals if s.get("validation_status") == "validee_humain"])
    integrated = len([s for s in signals if s.get("validation_status") == "integree"])

    # Signal types breakdown
    by_type = {}
    for s in signals:
        t = s.get("signal_type", "autre")
        by_type[t] = by_type.get(t, 0) + 1

    # Top signals by mention count
    top_signals = sorted(signals, key=lambda x: x.get("mention_count", 0), reverse=True)[:10]

    # Recent exchanges
    recent_exchanges = sorted(exchanges, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]

    return {
        "stats": {
            "total_exchanges_analyzed": len(exchanges),
            "total_signals_detected": total_signals,
            "signals_detected": detected,
            "signals_analyzed_ia": analyzed,
            "signals_validated_human": validated,
            "signals_integrated": integrated
        },
        "by_type": by_type,
        "top_signals": top_signals,
        "recent_exchanges": recent_exchanges,
        "insights": insights
    }

@api_router.get("/ubuntoo/signals")
async def get_ubuntoo_signals(signal_type: Optional[str] = None, status: Optional[str] = None, sector: Optional[str] = None):
    """Get Ubuntoo detected signals with filters"""
    query = {}
    if signal_type:
        query["signal_type"] = signal_type
    if status:
        query["validation_status"] = status
    if sector:
        query["related_sectors"] = sector
    signals = await db.ubuntoo_signals.find(query, {"_id": 0}).to_list(100)
    return sorted(signals, key=lambda x: x.get("mention_count", 0), reverse=True)

@api_router.get("/ubuntoo/signals/{signal_id}")
async def get_ubuntoo_signal_detail(signal_id: str):
    """Get detailed signal with cross-references"""
    signal = await db.ubuntoo_signals.find_one({"id": signal_id}, {"_id": 0})
    if not signal:
        raise HTTPException(status_code=404, detail="Signal non trouvé")

    # Cross-reference with observatory
    linked_skills = []
    for skill_name in signal.get("linked_observatory_skills", []):
        skill = await db.emerging_skills.find_one({"skill_name": {"$regex": skill_name, "$options": "i"}}, {"_id": 0})
        if skill:
            linked_skills.append(skill)

    linked_jobs = []
    for job_name in signal.get("linked_evolution_jobs", []):
        job = await db.job_evolution_indices.find_one({"job_name": {"$regex": job_name, "$options": "i"}}, {"_id": 0})
        if job:
            linked_jobs.append(job)

    # Related exchanges
    related_exchanges = await db.ubuntoo_exchanges.find(
        {"$or": [
            {"detected_skills": {"$in": [signal["name"]]}},
            {"detected_tools": {"$in": [signal["name"]]}},
            {"detected_practices": {"$in": [signal["name"]]}}
        ]},
        {"_id": 0}
    ).to_list(20)

    return {
        "signal": signal,
        "linked_observatory_skills": linked_skills,
        "linked_evolution_jobs": linked_jobs,
        "related_exchanges": related_exchanges
    }

@api_router.post("/ubuntoo/signals/{signal_id}/validate")
async def validate_ubuntoo_signal(signal_id: str, approved: bool, notes: Optional[str] = None):
    """Human validation of an Ubuntoo signal"""
    update_data = {
        "validation_status": "validee_humain" if approved else "rejetee",
        "human_notes": notes,
    }
    result = await db.ubuntoo_signals.update_one({"id": signal_id}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Signal non trouvé")

    # If validated, check if should be integrated into observatory
    if approved:
        signal = await db.ubuntoo_signals.find_one({"id": signal_id}, {"_id": 0})
        if signal and signal.get("mention_count", 0) >= 5 and signal.get("ai_confidence", 0) >= 0.7:
            await integrate_ubuntoo_signal(signal)

    return {"message": "Validation enregistrée", "status": update_data["validation_status"]}

async def integrate_ubuntoo_signal(signal: dict):
    """Integrate a validated Ubuntoo signal into the observatory"""
    existing = await db.emerging_skills.find_one(
        {"skill_name": {"$regex": signal["name"], "$options": "i"}}, {"_id": 0}
    )
    if existing:
        await db.emerging_skills.update_one(
            {"id": existing["id"]},
            {"$inc": {"mention_count": signal.get("mention_count", 1)},
             "$set": {"last_updated": datetime.now(timezone.utc).isoformat()},
             "$addToSet": {"related_sectors": {"$each": signal.get("related_sectors", [])}}}
        )
    else:
        new_skill = EmergingSkill(
            skill_name=signal["name"],
            description=signal.get("description"),
            related_sectors=signal.get("related_sectors", []),
            related_jobs=signal.get("related_jobs", []),
            emergence_score=min(signal.get("ai_confidence", 0.5) + 0.1, 1.0),
            growth_rate=signal.get("growth_rate", 0.1),
            mention_count=signal.get("mention_count", 1),
            contributor_count=signal.get("source_exchanges_count", 1),
            status="emergente"
        )
        await db.emerging_skills.insert_one(new_skill.model_dump())

    await db.ubuntoo_signals.update_one({"id": signal["id"]}, {"$set": {"validation_status": "integree"}})

@api_router.post("/ubuntoo/analyze")
async def trigger_ubuntoo_analysis():
    """Trigger AI analysis on recent Ubuntoo exchanges"""
    exchanges = await db.ubuntoo_exchanges.find({}, {"_id": 0}).to_list(50)
    if not exchanges:
        return {"message": "Aucun échange à analyser"}

    analysis = await analyze_ubuntoo_exchanges_with_ai(exchanges)

    return {
        "message": "Analyse terminée",
        "analysis": analysis,
        "exchanges_analyzed": len(exchanges)
    }

@api_router.get("/ubuntoo/insights")
async def get_ubuntoo_insights():
    """Get cross-referenced insights"""
    insights = await db.ubuntoo_insights.find({}, {"_id": 0}).to_list(50)
    return sorted(insights, key=lambda x: {"haute": 0, "moyenne": 1, "basse": 2}.get(x.get("priority", "moyenne"), 1))

@api_router.get("/ubuntoo/cross-reference")
async def get_cross_reference_data():
    """Get cross-reference between Ubuntoo signals, observatory skills, and evolution indices"""
    signals = await db.ubuntoo_signals.find({"validation_status": {"$in": ["analysee_ia", "validee_humain", "integree"]}}, {"_id": 0}).to_list(50)
    observatory_skills = await db.emerging_skills.find({}, {"_id": 0}).to_list(50)
    evolution_jobs = await db.job_evolution_indices.find({}, {"_id": 0}).to_list(50)

    # Build cross-reference map
    cross_refs = []
    for signal in signals:
        matched_skills = [s for s in observatory_skills if any(
            signal["name"].lower() in sk.lower() or sk.lower() in signal["name"].lower()
            for sk in [s.get("skill_name", "")]
        )]
        matched_jobs = [j for j in evolution_jobs if any(
            sector in j.get("sector", "").lower()
            for sector in [s.lower() for s in signal.get("related_sectors", [])]
        )]
        if matched_skills or matched_jobs:
            cross_refs.append({
                "signal": signal["name"],
                "signal_type": signal.get("signal_type"),
                "mention_count": signal.get("mention_count", 0),
                "matched_observatory_skills": [s.get("skill_name") for s in matched_skills],
                "matched_jobs": [j.get("job_name") for j in matched_jobs],
                "validation_status": signal.get("validation_status"),
                "ai_confidence": signal.get("ai_confidence", 0)
            })

    return {
        "cross_references": cross_refs,
        "total_signals": len(signals),
        "total_cross_matched": len(cross_refs)
    }

# ============== SEED DATA ==============

@api_router.post("/seed")
async def seed_database():
    """Seed database with demo data"""
    # Clear existing data
    await db.jobs.delete_many({})
    await db.learning_modules.delete_many({})
    await db.beneficiaires.delete_many({})
    
    # Seed jobs
    demo_jobs = [
        {
            "id": str(uuid.uuid4()),
            "title": "Assistant Administratif",
            "company": "TechCorp France",
            "location": "Paris, France",
            "contract_type": "CDI",
            "salary_range": "28 000€ - 35 000€",
            "required_skills": ["Gestion administrative", "Excel", "Communication", "Organisation"],
            "description": "Nous recherchons un assistant administratif polyvalent pour rejoindre notre équipe.",
            "sector": "Administration",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Chargé de Clientèle",
            "company": "ServicePlus",
            "location": "Lyon, France",
            "contract_type": "CDI",
            "salary_range": "32 000€ - 40 000€",
            "required_skills": ["Relation client", "Négociation", "CRM", "Écoute active"],
            "description": "Rejoignez notre équipe commerciale en tant que chargé de clientèle.",
            "sector": "Commerce",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Gestionnaire de Paie",
            "company": "Fiduciaire Nationale",
            "location": "Bordeaux, France",
            "contract_type": "CDI",
            "salary_range": "35 000€ - 45 000€",
            "required_skills": ["Paie", "Droit social", "SILAE", "Excel avancé"],
            "description": "Expert en paie recherché pour cabinet comptable en pleine croissance.",
            "sector": "Comptabilité",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Développeur Web Junior",
            "company": "DigitalStart",
            "location": "Nantes, France",
            "contract_type": "CDI",
            "salary_range": "30 000€ - 38 000€",
            "required_skills": ["JavaScript", "HTML/CSS", "React", "Git"],
            "description": "Opportunité pour développeur junior motivé dans une startup innovante.",
            "sector": "Informatique",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Responsable Formation",
            "company": "FormaPro Institute",
            "location": "Toulouse, France",
            "contract_type": "CDI",
            "salary_range": "40 000€ - 50 000€",
            "required_skills": ["Ingénierie pédagogique", "Management", "Gestion de projet", "Formation adultes"],
            "description": "Pilotez notre département formation et accompagnez le développement des compétences.",
            "sector": "Formation",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Seed learning modules
    demo_modules = [
        {
            "id": str(uuid.uuid4()),
            "title": "Maîtriser Excel pour la Gestion",
            "description": "Apprenez les fonctions avancées d'Excel pour optimiser votre productivité.",
            "duration": "12 heures",
            "level": "Intermédiaire",
            "skills_developed": ["Excel", "Tableaux croisés", "Formules avancées"],
            "category": "Bureautique",
            "image_url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&q=80"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Communication Professionnelle",
            "description": "Développez vos compétences en communication écrite et orale.",
            "duration": "8 heures",
            "level": "Débutant",
            "skills_developed": ["Communication", "Rédaction", "Présentation"],
            "category": "Soft Skills",
            "image_url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&q=80"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Gestion de Projet Agile",
            "description": "Initiez-vous aux méthodes agiles et au framework Scrum.",
            "duration": "16 heures",
            "level": "Intermédiaire",
            "skills_developed": ["Gestion de projet", "Scrum", "Kanban"],
            "category": "Management",
            "image_url": "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?auto=format&fit=crop&q=80"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Initiation au Développement Web",
            "description": "Découvrez les bases de HTML, CSS et JavaScript.",
            "duration": "20 heures",
            "level": "Débutant",
            "skills_developed": ["HTML/CSS", "JavaScript", "Git"],
            "category": "Informatique",
            "image_url": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&q=80"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Droit du Travail Essentiel",
            "description": "Comprenez les fondamentaux du droit social français.",
            "duration": "10 heures",
            "level": "Intermédiaire",
            "skills_developed": ["Droit social", "Contrats", "Réglementation"],
            "category": "Juridique",
            "image_url": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&q=80"
        }
    ]
    
    await db.jobs.insert_many(demo_jobs)
    await db.learning_modules.insert_many(demo_modules)
    
    # Seed observatoire data
    await db.emerging_skills.delete_many({})
    await db.sector_trends.delete_many({})
    await db.skill_contributions.delete_many({})
    
    demo_emerging_skills = [
        {
            "id": str(uuid.uuid4()),
            "skill_name": "Prompt Engineering",
            "description": "Conception et optimisation de prompts pour l'IA générative",
            "related_sectors": ["Informatique", "Marketing", "Communication"],
            "related_jobs": ["Développeur IA", "Content Manager", "Data Analyst"],
            "related_tools": ["ChatGPT", "Claude", "Midjourney"],
            "emergence_score": 0.92,
            "growth_rate": 0.45,
            "mention_count": 156,
            "contributor_count": 89,
            "status": "emergente",
            "first_detected": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "skill_name": "No-Code / Low-Code",
            "description": "Création d'applications sans programmation traditionnelle",
            "related_sectors": ["Informatique", "Administration", "PME"],
            "related_jobs": ["Business Analyst", "Chef de projet", "Responsable digital"],
            "related_tools": ["Bubble", "Webflow", "Airtable", "Notion"],
            "emergence_score": 0.85,
            "growth_rate": 0.38,
            "mention_count": 234,
            "contributor_count": 112,
            "status": "en_croissance",
            "first_detected": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "skill_name": "Green IT",
            "description": "Pratiques informatiques éco-responsables et durables",
            "related_sectors": ["Informatique", "Environnement", "Industrie"],
            "related_jobs": ["Responsable RSE", "Architecte SI", "Chef de projet IT"],
            "related_tools": ["Cloud Carbon Footprint", "Green Algorithms"],
            "emergence_score": 0.78,
            "growth_rate": 0.28,
            "mention_count": 98,
            "contributor_count": 45,
            "status": "emergente",
            "first_detected": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "skill_name": "Data Storytelling",
            "description": "Communication narrative basée sur l'analyse de données",
            "related_sectors": ["Marketing", "Communication", "Conseil"],
            "related_jobs": ["Data Analyst", "Consultant", "Responsable marketing"],
            "related_tools": ["Tableau", "Power BI", "Looker"],
            "emergence_score": 0.72,
            "growth_rate": 0.25,
            "mention_count": 187,
            "contributor_count": 78,
            "status": "en_croissance",
            "first_detected": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "skill_name": "Cybersécurité opérationnelle",
            "description": "Protection des systèmes et gestion des incidents de sécurité",
            "related_sectors": ["Informatique", "Banque", "Santé"],
            "related_jobs": ["Analyste SOC", "RSSI", "Pentester"],
            "related_tools": ["SIEM", "EDR", "Firewall NextGen"],
            "emergence_score": 0.88,
            "growth_rate": 0.35,
            "mention_count": 312,
            "contributor_count": 134,
            "status": "en_croissance",
            "first_detected": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    demo_sector_trends = [
        {
            "id": str(uuid.uuid4()),
            "sector_name": "Informatique",
            "emerging_skills": ["Prompt Engineering", "No-Code", "Green IT", "Cybersécurité"],
            "declining_skills": ["Flash", "COBOL", "jQuery"],
            "stable_skills": ["Python", "JavaScript", "SQL", "Git"],
            "transformation_index": 0.82,
            "hiring_trend": "croissance",
            "skill_gap_alert": True,
            "predicted_skills_demand": [
                {"skill": "IA Générative", "demand_change": "+45%", "horizon": "2025"},
                {"skill": "Cloud Native", "demand_change": "+32%", "horizon": "2025"},
                {"skill": "DevSecOps", "demand_change": "+28%", "horizon": "2025"}
            ],
            "last_updated": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "sector_name": "Administration",
            "emerging_skills": ["No-Code", "Automatisation", "IA bureautique"],
            "declining_skills": ["Sténographie", "Classement papier"],
            "stable_skills": ["Excel", "Rédaction", "Organisation", "Accueil"],
            "transformation_index": 0.58,
            "hiring_trend": "stable",
            "skill_gap_alert": False,
            "predicted_skills_demand": [
                {"skill": "Outils collaboratifs", "demand_change": "+25%", "horizon": "2025"},
                {"skill": "GED", "demand_change": "+18%", "horizon": "2025"}
            ],
            "last_updated": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "sector_name": "Commerce",
            "emerging_skills": ["Social Selling", "CRM avancé", "Data Analytics"],
            "declining_skills": ["Vente terrain classique"],
            "stable_skills": ["Négociation", "Relation client", "Prospection"],
            "transformation_index": 0.65,
            "hiring_trend": "croissance",
            "skill_gap_alert": True,
            "predicted_skills_demand": [
                {"skill": "E-commerce", "demand_change": "+35%", "horizon": "2025"},
                {"skill": "Marketing automation", "demand_change": "+30%", "horizon": "2025"}
            ],
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.emerging_skills.insert_many(demo_emerging_skills)
    await db.sector_trends.insert_many(demo_sector_trends)
    
    # Seed Evolution Indices
    await db.job_evolution_indices.delete_many({})
    await db.sector_evolution_indices.delete_many({})
    
    demo_job_indices = [
        {
            "id": str(uuid.uuid4()),
            "job_name": "Assistant Administratif",
            "sector": "Administration",
            "evolution_index": 58.0,
            "index_level": "en_transformation",
            "new_skills_count": 5,
            "skill_frequency_score": 0.62,
            "task_evolution_score": 0.55,
            "new_tools_score": 0.68,
            "job_posting_evolution": 0.45,
            "declining_skills_count": 2,
            "emerging_skills": ["Outils collaboratifs", "GED", "No-Code", "IA bureautique"],
            "stable_skills": ["Excel", "Rédaction", "Organisation", "Accueil"],
            "declining_skills": ["Sténographie", "Classement papier"],
            "recommended_skills": ["Teams/Slack", "Notion", "Automatisation"],
            "recommended_trainings": ["Maîtriser les outils collaboratifs", "Introduction à l'automatisation"],
            "job_passerelles": ["Office Manager", "Gestionnaire de projet", "Chargé de clientèle"],
            "last_calculated": datetime.now(timezone.utc).isoformat(),
            "data_sources": ["contributions", "offres_emploi", "experts"],
            "confidence_level": 0.85
        },
        {
            "id": str(uuid.uuid4()),
            "job_name": "Développeur Web",
            "sector": "Informatique",
            "evolution_index": 82.0,
            "index_level": "forte_mutation",
            "new_skills_count": 12,
            "skill_frequency_score": 0.88,
            "task_evolution_score": 0.78,
            "new_tools_score": 0.92,
            "job_posting_evolution": 0.75,
            "declining_skills_count": 4,
            "emerging_skills": ["IA Générative", "Prompt Engineering", "No-Code", "Cloud Native", "DevSecOps"],
            "stable_skills": ["JavaScript", "Git", "API REST", "SQL"],
            "declining_skills": ["jQuery", "Flash", "PHP legacy"],
            "recommended_skills": ["React/Vue", "TypeScript", "Docker", "CI/CD", "GPT API"],
            "recommended_trainings": ["Intégration IA Générative", "DevOps moderne", "Architecture Cloud"],
            "job_passerelles": ["Lead Developer", "Architecte logiciel", "Product Owner technique"],
            "last_calculated": datetime.now(timezone.utc).isoformat(),
            "data_sources": ["contributions", "offres_emploi", "experts", "github_trends"],
            "confidence_level": 0.92
        },
        {
            "id": str(uuid.uuid4()),
            "job_name": "Chargé de Clientèle",
            "sector": "Commerce",
            "evolution_index": 65.0,
            "index_level": "en_transformation",
            "new_skills_count": 6,
            "skill_frequency_score": 0.58,
            "task_evolution_score": 0.62,
            "new_tools_score": 0.72,
            "job_posting_evolution": 0.55,
            "declining_skills_count": 1,
            "emerging_skills": ["Social Selling", "CRM avancé", "Data Analytics", "Visio-commerce"],
            "stable_skills": ["Négociation", "Relation client", "Écoute active", "Prospection"],
            "declining_skills": ["Vente terrain classique"],
            "recommended_skills": ["LinkedIn Sales Navigator", "Salesforce", "Analytics client"],
            "recommended_trainings": ["Social Selling avancé", "CRM et automatisation commerciale"],
            "job_passerelles": ["Key Account Manager", "Responsable commercial", "Customer Success Manager"],
            "last_calculated": datetime.now(timezone.utc).isoformat(),
            "data_sources": ["contributions", "offres_emploi"],
            "confidence_level": 0.78
        },
        {
            "id": str(uuid.uuid4()),
            "job_name": "Gestionnaire de Paie",
            "sector": "Comptabilité",
            "evolution_index": 48.0,
            "index_level": "evolutif",
            "new_skills_count": 3,
            "skill_frequency_score": 0.42,
            "task_evolution_score": 0.45,
            "new_tools_score": 0.55,
            "job_posting_evolution": 0.38,
            "declining_skills_count": 1,
            "emerging_skills": ["DSN automatisée", "SIRH intégré", "Paie dématérialisée"],
            "stable_skills": ["Droit social", "Paie", "SILAE", "Excel avancé"],
            "declining_skills": ["Paie manuelle"],
            "recommended_skills": ["Cegid", "ADP", "Paramétrage DSN"],
            "recommended_trainings": ["Évolutions réglementaires 2025", "SIRH avancé"],
            "job_passerelles": ["Responsable paie", "RH généraliste", "Consultant SIRH"],
            "last_calculated": datetime.now(timezone.utc).isoformat(),
            "data_sources": ["contributions", "offres_emploi"],
            "confidence_level": 0.82
        },
        {
            "id": str(uuid.uuid4()),
            "job_name": "Artisan Boulanger",
            "sector": "Artisanat",
            "evolution_index": 15.0,
            "index_level": "stable",
            "new_skills_count": 1,
            "skill_frequency_score": 0.12,
            "task_evolution_score": 0.15,
            "new_tools_score": 0.18,
            "job_posting_evolution": 0.10,
            "declining_skills_count": 0,
            "emerging_skills": ["Vente en ligne"],
            "stable_skills": ["Pétrissage", "Fermentation", "Cuisson", "Hygiène alimentaire"],
            "declining_skills": [],
            "recommended_skills": ["Gestion de commerce", "Réseaux sociaux"],
            "recommended_trainings": ["Gestion d'entreprise artisanale"],
            "job_passerelles": ["Chef boulanger", "Formateur métiers de bouche"],
            "last_calculated": datetime.now(timezone.utc).isoformat(),
            "data_sources": ["experts"],
            "confidence_level": 0.75
        },
        {
            "id": str(uuid.uuid4()),
            "job_name": "Analyste Cybersécurité",
            "sector": "Informatique",
            "evolution_index": 88.0,
            "index_level": "forte_mutation",
            "new_skills_count": 15,
            "skill_frequency_score": 0.92,
            "task_evolution_score": 0.85,
            "new_tools_score": 0.95,
            "job_posting_evolution": 0.88,
            "declining_skills_count": 2,
            "emerging_skills": ["IA défensive", "Zero Trust", "Cloud Security", "DevSecOps", "Threat Intelligence"],
            "stable_skills": ["Firewall", "SIEM", "Incident Response", "Pentest"],
            "declining_skills": ["Antivirus traditionnel", "Sécurité périmétrique"],
            "recommended_skills": ["XDR/EDR", "SOAR", "Container Security"],
            "recommended_trainings": ["Certification CISSP", "Cloud Security Architecture", "IA et Cybersécurité"],
            "job_passerelles": ["RSSI", "Architecte Sécurité", "Consultant Cyber"],
            "last_calculated": datetime.now(timezone.utc).isoformat(),
            "data_sources": ["contributions", "offres_emploi", "experts", "certifications"],
            "confidence_level": 0.95
        }
    ]
    
    demo_sector_indices = [
        {
            "id": str(uuid.uuid4()),
            "sector_name": "Informatique",
            "evolution_index": 78.0,
            "index_level": "en_transformation",
            "jobs_count": 25,
            "jobs_in_transformation": 18,
            "jobs_stable": 3,
            "jobs_emerging": 4,
            "top_emerging_skills": [
                {"skill": "IA Générative", "growth": "+145%"},
                {"skill": "Cloud Native", "growth": "+68%"},
                {"skill": "DevSecOps", "growth": "+52%"}
            ],
            "top_declining_skills": [
                {"skill": "jQuery", "decline": "-35%"},
                {"skill": "Flash", "decline": "-90%"}
            ],
            "skill_gap_areas": ["Cybersécurité", "IA", "Cloud"],
            "hiring_trend": "croissance",
            "innovation_intensity": 0.92,
            "predicted_evolution_6m": 82.0,
            "predicted_evolution_12m": 85.0,
            "last_updated": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "sector_name": "Administration",
            "evolution_index": 52.0,
            "index_level": "en_transformation",
            "jobs_count": 15,
            "jobs_in_transformation": 8,
            "jobs_stable": 6,
            "jobs_emerging": 1,
            "top_emerging_skills": [
                {"skill": "Outils collaboratifs", "growth": "+45%"},
                {"skill": "GED", "growth": "+32%"},
                {"skill": "Automatisation", "growth": "+28%"}
            ],
            "top_declining_skills": [
                {"skill": "Classement papier", "decline": "-40%"}
            ],
            "skill_gap_areas": ["Numérique", "Automatisation"],
            "hiring_trend": "stable",
            "innovation_intensity": 0.55,
            "predicted_evolution_6m": 55.0,
            "predicted_evolution_12m": 58.0,
            "last_updated": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "sector_name": "Commerce",
            "evolution_index": 62.0,
            "index_level": "en_transformation",
            "jobs_count": 20,
            "jobs_in_transformation": 12,
            "jobs_stable": 6,
            "jobs_emerging": 2,
            "top_emerging_skills": [
                {"skill": "Social Selling", "growth": "+55%"},
                {"skill": "E-commerce", "growth": "+42%"},
                {"skill": "Data Analytics", "growth": "+38%"}
            ],
            "top_declining_skills": [
                {"skill": "Vente terrain", "decline": "-25%"}
            ],
            "skill_gap_areas": ["Digital", "Analytics"],
            "hiring_trend": "croissance",
            "innovation_intensity": 0.68,
            "predicted_evolution_6m": 65.0,
            "predicted_evolution_12m": 70.0,
            "last_updated": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "sector_name": "Artisanat",
            "evolution_index": 18.0,
            "index_level": "stable",
            "jobs_count": 30,
            "jobs_in_transformation": 2,
            "jobs_stable": 27,
            "jobs_emerging": 1,
            "top_emerging_skills": [
                {"skill": "Vente en ligne", "growth": "+22%"},
                {"skill": "Réseaux sociaux", "growth": "+18%"}
            ],
            "top_declining_skills": [],
            "skill_gap_areas": ["Digital"],
            "hiring_trend": "stable",
            "innovation_intensity": 0.15,
            "predicted_evolution_6m": 20.0,
            "predicted_evolution_12m": 22.0,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.job_evolution_indices.insert_many(demo_job_indices)
    await db.sector_evolution_indices.insert_many(demo_sector_indices)
    
    # Seed Ubuntoo Intelligence Data
    await db.ubuntoo_exchanges.delete_many({})
    await db.ubuntoo_signals.delete_many({})
    await db.ubuntoo_insights.delete_many({})

    demo_ubuntoo_exchanges = [
        {
            "id": str(uuid.uuid4()),
            "exchange_type": "retour_experience",
            "content_summary": "Depuis 6 mois, j'utilise ChatGPT quotidiennement pour rédiger mes rapports et synthèses. Mon manager me demande maintenant de former l'équipe à ces outils.",
            "detected_skills": ["Prompt Engineering", "IA Générative", "Formation interne"],
            "detected_tools": ["ChatGPT", "GPT-4"],
            "detected_practices": ["Automatisation de la rédaction", "Formation pair-à-pair"],
            "related_jobs": ["Assistant Administratif", "Chargé de communication"],
            "related_sectors": ["Administration", "Communication"],
            "author_role": "professionnel",
            "timestamp": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "exchange_type": "discussion",
            "content_summary": "Notre service RH a remplacé 3 outils par une seule plateforme SIRH intégrée. Les gestionnaires de paie doivent maintenant maîtriser le paramétrage complet du système.",
            "detected_skills": ["SIRH intégré", "Paramétrage logiciel", "Conduite du changement"],
            "detected_tools": ["SIRH", "Cegid", "ADP"],
            "detected_practices": ["Centralisation des outils", "Digitalisation RH"],
            "related_jobs": ["Gestionnaire de Paie", "Responsable RH"],
            "related_sectors": ["Comptabilité", "Administration"],
            "author_role": "professionnel",
            "timestamp": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "exchange_type": "mentorat",
            "content_summary": "En tant que développeur senior, je constate que les juniors qui maîtrisent les assistants de code IA (Copilot, Cursor) sont 2 fois plus productifs. C'est devenu un critère d'embauche chez nous.",
            "detected_skills": ["IA assistée au code", "Pair programming IA", "Productivité développeur"],
            "detected_tools": ["GitHub Copilot", "Cursor", "Claude Code"],
            "detected_practices": ["Développement assisté par IA", "Revue de code IA"],
            "related_jobs": ["Développeur Web", "Lead Developer"],
            "related_sectors": ["Informatique"],
            "author_role": "mentor",
            "timestamp": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "exchange_type": "conseil",
            "content_summary": "Pour ceux en reconversion vers le commercial : le social selling sur LinkedIn est devenu incontournable. Les recruteurs cherchent des profils qui maîtrisent la prospection digitale, pas juste le terrain.",
            "detected_skills": ["Social Selling", "Personal Branding", "Prospection digitale"],
            "detected_tools": ["LinkedIn Sales Navigator", "Lemlist", "Hubspot"],
            "detected_practices": ["Prospection sur réseaux sociaux", "Création de contenu professionnel"],
            "related_jobs": ["Chargé de Clientèle", "Commercial", "Business Developer"],
            "related_sectors": ["Commerce"],
            "author_role": "professionnel",
            "timestamp": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "exchange_type": "question",
            "content_summary": "Comment gérer la cybersécurité quand on passe au full cloud ? Notre DSI nous demande de tous devenir 'security champions' dans nos équipes respectives.",
            "detected_skills": ["Cloud Security", "Security Champion", "Sensibilisation sécurité"],
            "detected_tools": ["AWS Security Hub", "Azure Sentinel"],
            "detected_practices": ["Security by design", "Décentralisation de la sécurité"],
            "related_jobs": ["Analyste Cybersécurité", "Développeur Web", "Architecte Cloud"],
            "related_sectors": ["Informatique"],
            "author_role": "professionnel",
            "timestamp": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "exchange_type": "retour_experience",
            "content_summary": "Notre boulangerie a lancé un site de commande en ligne et une page Instagram. Les ventes ont augmenté de 30%. J'ai dû apprendre le marketing digital en autodidacte.",
            "detected_skills": ["Marketing digital", "E-commerce", "Gestion réseaux sociaux"],
            "detected_tools": ["Shopify", "Instagram Business", "Canva"],
            "detected_practices": ["Vente en ligne artisanale", "Communication digitale"],
            "related_jobs": ["Artisan Boulanger", "Commerçant"],
            "related_sectors": ["Artisanat", "Commerce"],
            "author_role": "professionnel",
            "timestamp": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "exchange_type": "discussion",
            "content_summary": "Les outils no-code comme Notion, Airtable et Make nous permettent de créer des workflows sans passer par l'IT. C'est une révolution pour les fonctions support.",
            "detected_skills": ["No-Code", "Automatisation workflows", "Autonomie numérique"],
            "detected_tools": ["Notion", "Airtable", "Make", "Zapier"],
            "detected_practices": ["Citizen development", "Automatisation sans code"],
            "related_jobs": ["Assistant Administratif", "Chef de projet", "Office Manager"],
            "related_sectors": ["Administration", "Informatique"],
            "author_role": "professionnel",
            "timestamp": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "exchange_type": "mentorat",
            "content_summary": "Conseil pour les gestionnaires de paie : la maîtrise de la DSN automatisée et du paramétrage des SIRH sera indispensable d'ici 2 ans. Les traitements manuels disparaissent progressivement.",
            "detected_skills": ["DSN automatisée", "Paramétrage SIRH", "Veille réglementaire digitale"],
            "detected_tools": ["SILAE", "Cegid HR", "PayFit"],
            "detected_practices": ["Paie dématérialisée", "Automatisation des déclarations"],
            "related_jobs": ["Gestionnaire de Paie", "Responsable paie"],
            "related_sectors": ["Comptabilité"],
            "author_role": "mentor",
            "timestamp": (datetime.now(timezone.utc) - timedelta(days=6)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "exchange_type": "retour_experience",
            "content_summary": "En tant que commercial terrain depuis 15 ans, j'ai dû me former au CRM Salesforce et à l'analyse de données clients. Aujourd'hui 60% de mon travail se fait devant un écran.",
            "detected_skills": ["CRM avancé", "Data Analytics client", "Vente hybride"],
            "detected_tools": ["Salesforce", "Power BI", "Teams"],
            "detected_practices": ["Vente hybride terrain/digital", "Pilotage par la data"],
            "related_jobs": ["Chargé de Clientèle", "Commercial terrain"],
            "related_sectors": ["Commerce"],
            "author_role": "professionnel",
            "timestamp": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "exchange_type": "discussion",
            "content_summary": "La montée en puissance du Green IT dans nos projets informatiques est impressionnante. On nous demande maintenant de mesurer l'empreinte carbone de nos applications.",
            "detected_skills": ["Green IT", "Éco-conception logicielle", "Mesure empreinte carbone"],
            "detected_tools": ["Cloud Carbon Footprint", "Lighthouse", "EcoIndex"],
            "detected_practices": ["Développement durable numérique", "Sobriété numérique"],
            "related_jobs": ["Développeur Web", "Architecte SI", "Chef de projet IT"],
            "related_sectors": ["Informatique"],
            "author_role": "professionnel",
            "timestamp": (datetime.now(timezone.utc) - timedelta(days=9)).isoformat()
        }
    ]

    demo_ubuntoo_signals = [
        {
            "id": str(uuid.uuid4()),
            "signal_type": "competence_emergente",
            "name": "Prompt Engineering",
            "description": "Compétence de rédaction et optimisation de prompts pour les IA génératives, de plus en plus demandée dans tous les métiers tertiaires.",
            "mention_count": 47,
            "first_detected": (datetime.now(timezone.utc) - timedelta(days=60)).isoformat(),
            "last_detected": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "related_jobs": ["Assistant Administratif", "Développeur Web", "Chargé de communication", "Content Manager"],
            "related_sectors": ["Administration", "Informatique", "Communication", "Marketing"],
            "source_exchanges_count": 32,
            "trend_direction": "hausse",
            "growth_rate": 0.85,
            "validation_status": "integree",
            "ai_confidence": 0.95,
            "ai_analysis": {"category": "technique", "impact": "transversal", "urgence": "haute"},
            "linked_observatory_skills": ["Prompt Engineering"],
            "linked_evolution_jobs": ["Assistant Administratif", "Développeur Web"],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "signal_type": "nouvel_outil",
            "name": "Assistants de code IA",
            "description": "Outils comme GitHub Copilot et Cursor qui transforment la pratique du développement logiciel. Les développeurs les utilisant sont significativement plus productifs.",
            "mention_count": 38,
            "first_detected": (datetime.now(timezone.utc) - timedelta(days=45)).isoformat(),
            "last_detected": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
            "related_jobs": ["Développeur Web", "Lead Developer", "Analyste Cybersécurité"],
            "related_sectors": ["Informatique"],
            "source_exchanges_count": 25,
            "trend_direction": "hausse",
            "growth_rate": 0.72,
            "validation_status": "validee_humain",
            "ai_confidence": 0.91,
            "ai_analysis": {"category": "outil", "impact": "sectoriel", "urgence": "haute"},
            "linked_observatory_skills": [],
            "linked_evolution_jobs": ["Développeur Web"],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "signal_type": "pratique_nouvelle",
            "name": "Citizen Development (No-Code)",
            "description": "Les fonctions support créent leurs propres outils et workflows grâce aux plateformes no-code, réduisant la dépendance aux équipes IT.",
            "mention_count": 29,
            "first_detected": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat(),
            "last_detected": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
            "related_jobs": ["Assistant Administratif", "Office Manager", "Chef de projet"],
            "related_sectors": ["Administration", "Informatique"],
            "source_exchanges_count": 18,
            "trend_direction": "hausse",
            "growth_rate": 0.55,
            "validation_status": "analysee_ia",
            "ai_confidence": 0.82,
            "ai_analysis": {"category": "pratique", "impact": "transversal", "urgence": "moyenne"},
            "linked_observatory_skills": ["No-Code / Low-Code"],
            "linked_evolution_jobs": ["Assistant Administratif"],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "signal_type": "transformation_metier",
            "name": "Vente hybride terrain/digital",
            "description": "Les commerciaux terrain évoluent vers un modèle hybride où 50-60% du travail se fait en digital (CRM, visioconférence, social selling).",
            "mention_count": 22,
            "first_detected": (datetime.now(timezone.utc) - timedelta(days=50)).isoformat(),
            "last_detected": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
            "related_jobs": ["Chargé de Clientèle", "Commercial", "Business Developer"],
            "related_sectors": ["Commerce"],
            "source_exchanges_count": 15,
            "trend_direction": "hausse",
            "growth_rate": 0.48,
            "validation_status": "validee_humain",
            "ai_confidence": 0.88,
            "ai_analysis": {"category": "transformation", "impact": "sectoriel", "urgence": "moyenne"},
            "linked_observatory_skills": ["Social Selling"],
            "linked_evolution_jobs": ["Chargé de Clientèle"],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=50)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "signal_type": "competence_emergente",
            "name": "Security Champion",
            "description": "Nouveau rôle au sein des équipes de développement : des référents sécurité non-spécialistes qui portent les bonnes pratiques cyber au quotidien.",
            "mention_count": 15,
            "first_detected": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
            "last_detected": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "related_jobs": ["Développeur Web", "Analyste Cybersécurité", "Chef de projet IT"],
            "related_sectors": ["Informatique"],
            "source_exchanges_count": 11,
            "trend_direction": "hausse",
            "growth_rate": 0.62,
            "validation_status": "analysee_ia",
            "ai_confidence": 0.78,
            "ai_analysis": {"category": "technique", "impact": "sectoriel", "urgence": "moyenne"},
            "linked_observatory_skills": [],
            "linked_evolution_jobs": ["Analyste Cybersécurité", "Développeur Web"],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "signal_type": "difficulte_metier",
            "name": "Obsolescence des compétences paie manuelles",
            "description": "Les gestionnaires de paie signalent une accélération de la digitalisation qui rend les compétences manuelles obsolètes plus vite que prévu.",
            "mention_count": 12,
            "first_detected": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
            "last_detected": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
            "related_jobs": ["Gestionnaire de Paie", "Responsable paie"],
            "related_sectors": ["Comptabilité"],
            "source_exchanges_count": 9,
            "trend_direction": "hausse",
            "growth_rate": 0.35,
            "validation_status": "detectee",
            "ai_confidence": 0.72,
            "ai_analysis": {"category": "difficulte", "impact": "sectoriel", "urgence": "haute"},
            "linked_observatory_skills": [],
            "linked_evolution_jobs": ["Gestionnaire de Paie"],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "signal_type": "nouvel_outil",
            "name": "Green IT / Éco-conception",
            "description": "Les outils de mesure d'empreinte carbone numérique deviennent obligatoires dans les projets IT, créant un nouveau besoin de compétences.",
            "mention_count": 18,
            "first_detected": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat(),
            "last_detected": (datetime.now(timezone.utc) - timedelta(days=6)).isoformat(),
            "related_jobs": ["Développeur Web", "Architecte SI", "Chef de projet IT"],
            "related_sectors": ["Informatique"],
            "source_exchanges_count": 12,
            "trend_direction": "hausse",
            "growth_rate": 0.42,
            "validation_status": "validee_humain",
            "ai_confidence": 0.85,
            "ai_analysis": {"category": "outil", "impact": "sectoriel", "urgence": "moyenne"},
            "linked_observatory_skills": ["Green IT"],
            "linked_evolution_jobs": ["Développeur Web"],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "signal_type": "pratique_nouvelle",
            "name": "Artisanat digital",
            "description": "Les artisans adoptent le e-commerce et le marketing digital pour étendre leur clientèle, créant un besoin de double compétence métier/numérique.",
            "mention_count": 8,
            "first_detected": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat(),
            "last_detected": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(),
            "related_jobs": ["Artisan Boulanger", "Commerçant"],
            "related_sectors": ["Artisanat", "Commerce"],
            "source_exchanges_count": 6,
            "trend_direction": "hausse",
            "growth_rate": 0.25,
            "validation_status": "detectee",
            "ai_confidence": 0.65,
            "ai_analysis": {"category": "pratique", "impact": "sectoriel", "urgence": "basse"},
            "linked_observatory_skills": [],
            "linked_evolution_jobs": ["Artisan Boulanger"],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
        }
    ]

    demo_ubuntoo_insights = [
        {
            "id": str(uuid.uuid4()),
            "insight_type": "tendance_emergente",
            "title": "L'IA générative transforme tous les métiers tertiaires",
            "description": "Les échanges Ubuntoo confirment une adoption massive des outils d'IA générative (ChatGPT, Copilot) bien au-delà du secteur IT. Les fonctions support, communication et RH sont fortement impactées.",
            "supporting_signals": ["Prompt Engineering", "Assistants de code IA"],
            "impacted_jobs": ["Assistant Administratif", "Développeur Web", "Chargé de communication"],
            "impacted_sectors": ["Administration", "Informatique", "Communication"],
            "recommendation": "Intégrer des modules de formation IA générative dans tous les parcours de reconversion, pas seulement les filières IT.",
            "priority": "haute",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "insight_type": "alerte_competence",
            "title": "Accélération de l'obsolescence dans la gestion de paie",
            "description": "Le croisement entre les signaux Ubuntoo et les données de l'observatoire montre que la digitalisation de la paie s'accélère plus vite que les prévisions initiales.",
            "supporting_signals": ["Obsolescence des compétences paie manuelles", "Citizen Development (No-Code)"],
            "impacted_jobs": ["Gestionnaire de Paie", "Responsable paie"],
            "impacted_sectors": ["Comptabilité"],
            "recommendation": "Anticiper la montée en compétences SIRH des gestionnaires de paie via des formations accélérées.",
            "priority": "haute",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "insight_type": "opportunite_formation",
            "title": "Le No-Code comme levier d'autonomie professionnelle",
            "description": "Les échanges montrent que les professionnels qui maîtrisent les outils no-code gagnent en autonomie et en valeur. Cette compétence est transversale à tous les secteurs.",
            "supporting_signals": ["Citizen Development (No-Code)"],
            "impacted_jobs": ["Assistant Administratif", "Office Manager", "Chef de projet"],
            "impacted_sectors": ["Administration", "Informatique"],
            "recommendation": "Créer un parcours 'Autonomie numérique' centré sur le no-code pour les professionnels en reconversion.",
            "priority": "moyenne",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "insight_type": "transformation_metier",
            "title": "La vente évolue vers un modèle hybride digital/terrain",
            "description": "Les témoignages du réseau confirment une transformation profonde du métier commercial, avec une digitalisation de 50-60% des activités.",
            "supporting_signals": ["Vente hybride terrain/digital"],
            "impacted_jobs": ["Chargé de Clientèle", "Commercial", "Business Developer"],
            "impacted_sectors": ["Commerce"],
            "recommendation": "Adapter les formations commerciales pour inclure le social selling et l'analyse de données client.",
            "priority": "moyenne",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]

    await db.ubuntoo_exchanges.insert_many(demo_ubuntoo_exchanges)
    await db.ubuntoo_signals.insert_many(demo_ubuntoo_signals)
    await db.ubuntoo_insights.insert_many(demo_ubuntoo_insights)

    return {
        "message": "Base de données initialisée", 
        "jobs": len(demo_jobs), 
        "modules": len(demo_modules), 
        "emerging_skills": len(demo_emerging_skills), 
        "sector_trends": len(demo_sector_trends),
        "job_indices": len(demo_job_indices),
        "sector_indices": len(demo_sector_indices),
        "ubuntoo_exchanges": len(demo_ubuntoo_exchanges),
        "ubuntoo_signals": len(demo_ubuntoo_signals),
        "ubuntoo_insights": len(demo_ubuntoo_insights)
    }

# ============== ROOT ==============

@api_router.get("/")
async def root():
    return {"message": "Ré'Actif Pro API", "version": "1.0.0"}

# Include router and middleware
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
