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
from datetime import datetime, timezone
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
    
    return {"message": "Base de données initialisée", "jobs": len(demo_jobs), "modules": len(demo_modules)}

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
