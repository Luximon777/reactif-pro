from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="DE'CLIC PRO API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class ProfileCreate(BaseModel):
    soft_skills: List[str]
    values: List[str]
    potentials: List[str]
    answers: Optional[Dict[str, Any]] = None

class Profile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    soft_skills: List[str]
    values: List[str]
    potentials: List[str]
    answers: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class JobMatch(BaseModel):
    title: str
    compatibility: int
    sector: str

class MatchingJobsRequest(BaseModel):
    soft_skills: List[str]
    values: List[str]
    potentials: List[str]

class MatchingJobsResponse(BaseModel):
    jobs: List[JobMatch]

# Job database with skill requirements
JOBS_DATABASE = [
    {
        "title": "Chef de projet",
        "sector": "Management",
        "required_skills": ["Organisation", "Communication orale", "Leadership", "Gestion du stress"],
        "required_values": ["Esprit d'équipe", "Structure", "Reconnaissance"],
        "base_score": 75
    },
    {
        "title": "Consultant",
        "sector": "Conseil",
        "required_skills": ["Esprit analytique", "Communication orale", "Adaptabilité", "Vision stratégique"],
        "required_values": ["Développement personnel", "Flexibilité", "Impact social"],
        "base_score": 70
    },
    {
        "title": "Product Manager",
        "sector": "Tech",
        "required_skills": ["Vision stratégique", "Communication orale", "Créativité", "Sens opérationnel"],
        "required_values": ["Innovation", "Autonomie", "Flexibilité"],
        "base_score": 72
    },
    {
        "title": "Responsable RH",
        "sector": "Ressources Humaines",
        "required_skills": ["Écoute active", "Empathie", "Communication orale", "Organisation"],
        "required_values": ["Impact social", "Esprit d'équipe", "Développement personnel"],
        "base_score": 68
    },
    {
        "title": "Entrepreneur",
        "sector": "Entrepreneuriat",
        "required_skills": ["Proactivité", "Résilience", "Vision stratégique", "Prise de décision"],
        "required_values": ["Autonomie", "Innovation", "Flexibilité"],
        "base_score": 65
    },
    {
        "title": "Data Analyst",
        "sector": "Data Science",
        "required_skills": ["Esprit analytique", "Organisation", "Communication écrite", "Expertise technique"],
        "required_values": ["Développement personnel", "Structure", "Autonomie"],
        "base_score": 70
    },
    {
        "title": "UX Designer",
        "sector": "Design",
        "required_skills": ["Créativité", "Empathie", "Écoute active", "Communication visuelle"],
        "required_values": ["Innovation", "Impact social", "Flexibilité"],
        "base_score": 68
    },
    {
        "title": "Commercial",
        "sector": "Vente",
        "required_skills": ["Relationnel", "Communication orale", "Résilience", "Prise de décision"],
        "required_values": ["Reconnaissance", "Autonomie", "Flexibilité"],
        "base_score": 72
    },
    {
        "title": "Développeur",
        "sector": "Tech",
        "required_skills": ["Expertise technique", "Esprit analytique", "Organisation", "Adaptabilité"],
        "required_values": ["Autonomie", "Développement personnel", "Innovation"],
        "base_score": 70
    },
    {
        "title": "Formateur",
        "sector": "Formation",
        "required_skills": ["Communication orale", "Empathie", "Adaptabilité", "Organisation"],
        "required_values": ["Impact social", "Développement personnel", "Esprit d'équipe"],
        "base_score": 68
    }
]

def calculate_job_compatibility(job: dict, soft_skills: List[str], values: List[str], potentials: List[str]) -> int:
    """Calculate compatibility score between a job and user profile"""
    score = job["base_score"]
    
    # Check soft skills match
    all_user_skills = soft_skills + potentials
    for skill in job["required_skills"]:
        if skill in all_user_skills:
            score += 5
    
    # Check values match
    for value in job["required_values"]:
        if value in values:
            score += 4
    
    # Cap at 98
    return min(score, 98)

# Routes
@api_router.get("/")
async def root():
    return {"message": "DE'CLIC PRO API - Intelligence Professionnelle"}

@api_router.post("/profile", response_model=Profile)
async def create_profile(input: ProfileCreate):
    """Create a new professional profile"""
    profile_obj = Profile(
        soft_skills=input.soft_skills,
        values=input.values,
        potentials=input.potentials,
        answers=input.answers
    )
    
    # Convert to dict and serialize datetime for MongoDB
    doc = profile_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.profiles.insert_one(doc)
    return profile_obj

@api_router.get("/profile/{profile_id}", response_model=Profile)
async def get_profile(profile_id: str):
    """Get a profile by ID"""
    profile = await db.profiles.find_one({"id": profile_id}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Convert ISO string back to datetime
    if isinstance(profile.get('created_at'), str):
        profile['created_at'] = datetime.fromisoformat(profile['created_at'])
    
    return profile

@api_router.post("/matching-jobs", response_model=MatchingJobsResponse)
async def get_matching_jobs(request: MatchingJobsRequest):
    """Get jobs matching the user's profile"""
    jobs_with_scores = []
    
    for job in JOBS_DATABASE:
        compatibility = calculate_job_compatibility(
            job,
            request.soft_skills,
            request.values,
            request.potentials
        )
        jobs_with_scores.append({
            "title": job["title"],
            "sector": job["sector"],
            "compatibility": compatibility
        })
    
    # Sort by compatibility descending
    jobs_with_scores.sort(key=lambda x: x["compatibility"], reverse=True)
    
    # Return top 5
    return MatchingJobsResponse(jobs=jobs_with_scores[:5])

@api_router.get("/jobs")
async def get_all_jobs():
    """Get all available jobs"""
    return {"jobs": [{"title": j["title"], "sector": j["sector"]} for j in JOBS_DATABASE]}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
