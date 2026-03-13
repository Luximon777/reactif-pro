from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import secrets
from emergentintegrations.llm.chat import LlmChat, UserMessage

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

class MatchRequest(BaseModel):
    profile_skills: List[str]
    job_requirements: List[str]
    profile_sectors: List[str] = []
    job_sector: str = ""

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
    
    return {"message": "Base de données initialisée", "jobs": len(demo_jobs), "modules": len(demo_modules), "emerging_skills": len(demo_emerging_skills), "sector_trends": len(demo_sector_trends)}

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
