"""
ubuntoo_routes.py
Routes FastAPI pour la messagerie Ubuntoo — prototype 50 utilisateurs
À placer dans : backend/ubuntoo_routes.py
Puis ajouter dans server.py :
    from ubuntoo_routes import ubuntoo_router
    app.include_router(ubuntoo_router)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid
import os
import hashlib

ubuntoo_router = APIRouter(prefix="/api/ubuntoo", tags=["ubuntoo"])

# MongoDB (réutilise la connexion existante)
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

# ─── Modèles ───────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    nom: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class MessageCreate(BaseModel):
    conversation_id: str
    sender_id: str
    text: str

class GroupCreate(BaseModel):
    nom: str
    description: str
    theme: str   # VSI_PRO, EMPLOI, ACCOMPAGNEMENT, FORMATION, LIBRE
    creator_id: str
    membres: List[str] = []

class ConversationCreate(BaseModel):
    user1_id: str
    user2_id: str

# ─── Auth ──────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@ubuntoo_router.post("/auth/register")
async def register(body: UserRegister):
    # Vérifie si email déjà pris
    existing = await db.ubuntoo_users.find_one({"email": body.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    user = {
        "id": str(uuid.uuid4()),
        "nom": body.nom,
        "email": body.email.lower(),
        "password": hash_password(body.password),
        "avatar": body.nom[0].upper(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "online": False,
    }
    await db.ubuntoo_users.insert_one({**user, "_id": user["id"]})
    user.pop("password")
    return user

@ubuntoo_router.post("/auth/login")
async def login(body: UserLogin):
    user = await db.ubuntoo_users.find_one(
        {"email": body.email.lower(), "password": hash_password(body.password)},
        {"_id": 0}
    )
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    # Marque en ligne
    await db.ubuntoo_users.update_one(
        {"id": user["id"]}, {"$set": {"online": True}}
    )
    user.pop("password", None)
    return user

@ubuntoo_router.post("/auth/logout/{user_id}")
async def logout(user_id: str):
    await db.ubuntoo_users.update_one(
        {"id": user_id}, {"$set": {"online": False}}
    )
    return {"ok": True}

# ─── Utilisateurs ──────────────────────────────────────────────────────────

@ubuntoo_router.get("/users")
async def get_users(current_user_id: str = ""):
    users = await db.ubuntoo_users.find(
        {"id": {"$ne": current_user_id}},
        {"_id": 0, "password": 0}
    ).to_list(200)
    return users

@ubuntoo_router.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await db.ubuntoo_users.find_one({"id": user_id}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user

# ─── Conversations individuelles ──────────────────────────────────────────

@ubuntoo_router.post("/conversations")
async def create_or_get_conversation(body: ConversationCreate):
    # Cherche une conversation existante entre ces 2 utilisateurs
    conv = await db.ubuntoo_conversations.find_one({
        "type": "direct",
        "membres": {"$all": [body.user1_id, body.user2_id]}
    }, {"_id": 0})
    
    if conv:
        return conv
    
    # Crée une nouvelle
    conv = {
        "id": str(uuid.uuid4()),
        "type": "direct",
        "membres": [body.user1_id, body.user2_id],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_message": None,
        "last_message_at": None,
    }
    await db.ubuntoo_conversations.insert_one({**conv, "_id": conv["id"]})
    return conv

@ubuntoo_router.get("/conversations/user/{user_id}")
async def get_user_conversations(user_id: str):
    convs = await db.ubuntoo_conversations.find(
        {"membres": user_id},
        {"_id": 0}
    ).sort("last_message_at", -1).to_list(100)
    
    # Enrichit avec les infos des membres
    result = []
    for conv in convs:
        enriched = dict(conv)
        if conv["type"] == "direct":
            other_id = next((m for m in conv["membres"] if m != user_id), None)
            if other_id:
                other = await db.ubuntoo_users.find_one(
                    {"id": other_id}, {"_id": 0, "password": 0}
                )
                enriched["other_user"] = other
        result.append(enriched)
    return result

# ─── Groupes ───────────────────────────────────────────────────────────────

GROUPES_DEFAUT = [
    {"nom": "VSI PRO — Valoriser Son Identité", "theme": "VSI_PRO", "description": "Construisez et valorisez votre identité professionnelle unique.", "color": "#E1F5EE", "icon": "🪪"},
    {"nom": "Emploi & Mobilité", "theme": "EMPLOI", "description": "Offres, candidatures, retours d'expérience.", "color": "#EEEDFE", "icon": "💼"},
    {"nom": "Accompagnement & Conseils", "theme": "ACCOMPAGNEMENT", "description": "Espace d'entre-aide bienveillant.", "color": "#FAECE7", "icon": "🤝"},
    {"nom": "Formation & Compétences", "theme": "FORMATION", "description": "Formations, certifications, OPC.", "color": "#FAEEDA", "icon": "🎓"},
    {"nom": "Réseau Grand Est", "theme": "RESEAU", "description": "Annonces et événements du territoire.", "color": "#E6F1FB", "icon": "🌍"},
]

@ubuntoo_router.post("/groups/init")
async def init_default_groups():
    """Crée les groupes par défaut si ils n'existent pas encore."""
    created = []
    for g in GROUPES_DEFAUT:
        existing = await db.ubuntoo_conversations.find_one({"theme": g["theme"], "type": "group"})
        if not existing:
            group = {
                "id": str(uuid.uuid4()),
                "type": "group",
                "nom": g["nom"],
                "description": g["description"],
                "theme": g["theme"],
                "color": g["color"],
                "icon": g["icon"],
                "membres": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_message": None,
                "last_message_at": None,
            }
            await db.ubuntoo_conversations.insert_one({**group, "_id": group["id"]})
            created.append(group["nom"])
    return {"created": created}

@ubuntoo_router.get("/groups")
async def get_groups():
    groups = await db.ubuntoo_conversations.find(
        {"type": "group"},
        {"_id": 0}
    ).sort("theme", 1).to_list(50)
    return groups

@ubuntoo_router.post("/groups")
async def create_group(body: GroupCreate):
    group = {
        "id": str(uuid.uuid4()),
        "type": "group",
        "nom": body.nom,
        "description": body.description,
        "theme": body.theme,
        "color": "#E6F1FB",
        "icon": "💬",
        "membres": [body.creator_id] + body.membres,
        "creator_id": body.creator_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_message": None,
        "last_message_at": None,
    }
    await db.ubuntoo_conversations.insert_one({**group, "_id": group["id"]})
    return group

@ubuntoo_router.post("/groups/{group_id}/join/{user_id}")
async def join_group(group_id: str, user_id: str):
    await db.ubuntoo_conversations.update_one(
        {"id": group_id},
        {"$addToSet": {"membres": user_id}}
    )
    return {"ok": True}

# ─── Messages ──────────────────────────────────────────────────────────────

@ubuntoo_router.get("/messages/{conversation_id}")
async def get_messages(conversation_id: str, limit: int = 50):
    messages = await db.ubuntoo_messages.find(
        {"conversation_id": conversation_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(limit)
    return messages

@ubuntoo_router.post("/messages")
async def send_message(body: MessageCreate):
    # Récupère le nom de l'expéditeur
    sender = await db.ubuntoo_users.find_one({"id": body.sender_id}, {"nom": 1})
    sender_nom = sender["nom"] if sender else "Inconnu"

    now = datetime.now(timezone.utc).isoformat()
    msg = {
        "id": str(uuid.uuid4()),
        "conversation_id": body.conversation_id,
        "sender_id": body.sender_id,
        "sender_nom": sender_nom,
        "text": body.text,
        "created_at": now,
        "lu": False,
    }
    await db.ubuntoo_messages.insert_one({**msg, "_id": msg["id"]})
    
    # Met à jour le dernier message de la conversation
    await db.ubuntoo_conversations.update_one(
        {"id": body.conversation_id},
        {"$set": {"last_message": body.text, "last_message_at": now}}
    )
    
    return msg

@ubuntoo_router.get("/messages/{conversation_id}/new")
async def get_new_messages(conversation_id: str, since: str):
    """Récupère les messages plus récents que 'since' (polling)."""
    messages = await db.ubuntoo_messages.find(
        {"conversation_id": conversation_id, "created_at": {"$gt": since}},
        {"_id": 0}
    ).sort("created_at", 1).to_list(100)
    return messages
