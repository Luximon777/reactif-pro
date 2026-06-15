from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="RE'ACTIF PRO — OPC API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

@api_router.get("/")
async def root():
    return {"message": "RE'ACTIF PRO — OPC API opérationnelle", "module": "Observatoire Prédictif des Compétences"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks

# ─── Auth Espace Personnel (pseudonyme + mot de passe) ─────────────────────
import hashlib

class AuthRegister(BaseModel):
    pseudonyme: str
    password: str

class AuthLogin(BaseModel):
    pseudonyme: str
    password: str

def _hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

@api_router.post("/auth/register")
async def auth_register(body: AuthRegister):
    existing = await db.users.find_one({"pseudonyme": body.pseudonyme})
    if existing:
        raise HTTPException(status_code=400, detail="Pseudonyme déjà utilisé")
    user = {
        "id": str(uuid.uuid4()),
        "pseudonyme": body.pseudonyme,
        "password": _hash_pw(body.password),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.users.insert_one({**user, "_id": user["id"]})
    return {"id": user["id"], "pseudonyme": user["pseudonyme"]}

@api_router.post("/auth/login")
async def auth_login(body: AuthLogin):
    user = await db.users.find_one({"pseudonyme": body.pseudonyme, "password": _hash_pw(body.password)}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    return user

# ─── Inclusion des routers OPC ────────────────────────────────────────────
from opc.routes_ingestion import router as opc_ingestion_router
from opc.routes_vues import router as opc_vues_router
from opc.routes_ia import router as opc_ia_router
from opc.routes_admin import router as opc_admin_router
from opc.db import create_indexes as opc_create_indexes
from opc.seed import seed_if_empty

# ─── Inclusion du router Ubuntoo ──────────────────────────────────────────
from ubuntoo_routes import ubuntoo_router

app.include_router(api_router)
app.include_router(opc_ingestion_router)
app.include_router(opc_vues_router)
app.include_router(opc_ia_router)
app.include_router(opc_admin_router)
app.include_router(ubuntoo_router)

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

@app.on_event("startup")
async def on_startup():
    try:
        await opc_create_indexes()
        await seed_if_empty()
        # Seed default user marc19
        existing = await db.users.find_one({"pseudonyme": "marc19"})
        if not existing:
            await db.users.insert_one({
                "_id": str(uuid.uuid4()),
                "id": str(uuid.uuid4()),
                "pseudonyme": "marc19",
                "password": _hash_pw("Solerys777!"),
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            logger.info("[Seed] Utilisateur marc19 créé")
    except Exception as e:
        logger.error(f"[OPC startup error] {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
