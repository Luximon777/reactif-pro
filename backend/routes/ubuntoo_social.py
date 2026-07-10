"""UBUNTOO — réseau socio-professionnel solidaire, intégré à Ré'Actif Pro.

Porté depuis le projet standalone (repo Luximon777/ubuntoo, branche conflict_090726_1613).
Auth : SSO silencieux depuis la session Ré'Actif Pro (auto-provisionnement).
"""
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid
import os
import jwt

from database import db, get_current_token

SECRET_KEY = os.environ['UBUNTOO_JWT_SECRET']
ALGORITHM = "HS256"
security = HTTPBearer()

router = APIRouter(prefix="/api/social")

# ============== REALTIME CONNECTION MANAGER ==============

class ConnectionManager:
    def __init__(self):
        self.active: dict = {}

    async def connect(self, user_id: str, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(user_id, []).append(ws)

    def disconnect(self, user_id: str, ws: WebSocket):
        conns = self.active.get(user_id)
        if conns and ws in conns:
            conns.remove(ws)
            if not conns:
                self.active.pop(user_id, None)

    def is_online(self, user_id: str) -> bool:
        return user_id in self.active

    async def send_to_user(self, user_id: str, payload: dict):
        for ws in list(self.active.get(user_id, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                pass

manager = ConnectionManager()

# ============== MODELS ==============

class UserStatus:
    MEMBER = "member"

class SsoRequest(BaseModel):
    token: str

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    full_name: str
    bio: str
    role: str
    points: int
    badges: List[str]
    created_at: str
    avatar_url: Optional[str] = None
    location: Optional[str] = ""
    sector: Optional[str] = ""
    jobs_sought: List[str] = []
    skills: List[str] = []
    availability: Optional[str] = ""
    languages: List[str] = []

class AuthResponse(BaseModel):
    token: str
    user: UserResponse

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    sector: Optional[str] = None
    jobs_sought: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    availability: Optional[str] = None
    languages: Optional[List[str]] = None

class ReactionRequest(BaseModel):
    reaction_type: str

class ReportRequest(BaseModel):
    target_type: str
    target_id: str
    reason: str

class PostCreate(BaseModel):
    content: str
    post_type: str = "general"

class PostResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    author_id: str
    author_name: str
    author_role: str
    author_avatar: Optional[str] = None
    content: str
    post_type: str
    likes: List[str]
    reactions: dict = {}
    comments_count: int
    created_at: str

class CommentCreate(BaseModel):
    content: str
    post_id: str

class CommentResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    post_id: str
    author_id: str
    author_name: str
    author_role: str
    content: str
    created_at: str

class MessageCreate(BaseModel):
    receiver_id: str
    content: str

class MessageResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    sender_id: str
    sender_name: str
    receiver_id: str
    content: str
    read: bool
    status: str = "sent"
    created_at: str

class ConversationResponse(BaseModel):
    user_id: str
    user_name: str
    user_avatar: Optional[str]
    user_role: str
    last_message: str
    last_message_time: str
    unread_count: int
    online: bool = False

class GroupCreate(BaseModel):
    name: str
    description: str
    category: str

class GroupResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    description: str
    category: str
    creator_id: str
    members_count: int
    created_at: str

class DiscussionCreate(BaseModel):
    title: str
    content: str
    group_id: str

class DiscussionResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    title: str
    content: str
    group_id: str
    author_id: str
    author_name: str
    author_role: str
    replies_count: int
    created_at: str

class DiscussionReplyCreate(BaseModel):
    content: str

class DiscussionReplyResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    discussion_id: str
    author_id: str
    author_name: str
    author_role: str
    content: str
    created_at: str

# ============== HELPERS ==============

def create_token(user_id: str) -> str:
    payload = {"user_id": user_id, "exp": datetime.now(timezone.utc).timestamp() + 86400 * 7}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def user_to_response(u: dict) -> UserResponse:
    return UserResponse(
        id=u["id"], email=u["email"], full_name=u["full_name"], bio=u.get("bio", ""),
        role=u.get("status", u.get("role", "member")), points=u.get("points", 0),
        badges=u.get("badges", []), created_at=u["created_at"], avatar_url=u.get("avatar_url"),
        location=u.get("location", ""), sector=u.get("sector", ""),
        jobs_sought=u.get("jobs_sought", []), skills=u.get("skills", []),
        availability=u.get("availability", ""), languages=u.get("languages", []),
    )

async def fetch_authors_map(author_ids: list) -> dict:
    ids = list({a for a in author_ids if a})
    if not ids:
        return {}
    docs = await db.ubuntoo_users.find({"id": {"$in": ids}}, {"_id": 0, "password": 0}).to_list(len(ids))
    return {d["id"]: d for d in docs}

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user = await db.ubuntoo_users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

async def award_badge(user_id: str, badge_id: str):
    await db.ubuntoo_users.update_one({"id": user_id}, {"$addToSet": {"badges": badge_id}})

async def check_experience_badges(user_id: str, action: str, context: dict = None):
    user = await db.ubuntoo_users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        return
    current_badges = user.get("badges", [])
    if action == "first_post" and "first_post" not in current_badges:
        if await db.ubuntoo_posts.count_documents({"author_id": user_id}) >= 1:
            await award_badge(user_id, "first_post")
    if action == "first_comment" and "helping_hand" not in current_badges:
        if await db.ubuntoo_comments.count_documents({"author_id": user_id}) >= 1:
            await award_badge(user_id, "helping_hand")
    if action == "discussion_reply" and "good_listener" not in current_badges:
        if await db.ubuntoo_replies.count_documents({"author_id": user_id}) >= 5:
            await award_badge(user_id, "good_listener")
    if action == "resource_shared" and "knowledge_sharer" not in current_badges:
        if await db.ubuntoo_posts.count_documents({"author_id": user_id, "post_type": "resource"}) >= 1:
            await award_badge(user_id, "knowledge_sharer")
    if action == "first_message" and "connection_made" not in current_badges:
        if await db.ubuntoo_messages.count_documents({"sender_id": user_id}) >= 1:
            await award_badge(user_id, "connection_made")
    if action == "group_created" and "builder" not in current_badges:
        if await db.ubuntoo_groups.count_documents({"creator_id": user_id}) >= 1:
            await award_badge(user_id, "builder")
    if action == "discussion_created" and "facilitator" not in current_badges:
        if await db.ubuntoo_discussions.count_documents({"author_id": user_id}) >= 1:
            await award_badge(user_id, "facilitator")
    if action == "joined_group" and "weaver" not in current_badges:
        groups = await db.ubuntoo_groups.find({"members": user_id}, {"_id": 0}).to_list(100)
        if len(groups) >= 3:
            await award_badge(user_id, "weaver")
    if action == "received_comment" and "voice_heard" not in current_badges:
        if context and context.get("post_author_id") == user_id:
            await award_badge(user_id, "voice_heard")

async def persist_message(sender: dict, receiver_id: str, content: str) -> dict:
    message_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": message_id, "sender_id": sender["id"], "receiver_id": receiver_id,
        "content": content, "read": False, "status": "sent", "created_at": now,
    }
    await db.ubuntoo_messages.insert_one(doc)
    await check_experience_badges(sender["id"], "first_message")
    return {
        "id": message_id, "sender_id": sender["id"], "sender_name": sender["full_name"],
        "receiver_id": receiver_id, "content": content, "read": False, "status": "sent", "created_at": now,
    }

async def deliver_message(sender: dict, receiver_id: str, content: str) -> dict:
    msg = await persist_message(sender, receiver_id, content)
    if manager.is_online(receiver_id):
        await db.ubuntoo_messages.update_one({"id": msg["id"]}, {"$set": {"status": "delivered"}})
        msg["status"] = "delivered"
        await manager.send_to_user(receiver_id, {"type": "message", "message": msg})
    await manager.send_to_user(sender["id"], {"type": "message", "message": msg})
    return msg

async def broadcast_presence(user_id: str, online: bool):
    payload = {"type": "presence", "user_id": user_id, "online": online}
    for uid in list(manager.active.keys()):
        await manager.send_to_user(uid, payload)

# ============== AUTH (SSO Ré'Actif Pro) ==============

@router.post("/auth/sso", response_model=AuthResponse)
async def sso_login(data: SsoRequest):
    """Auto-provisionne le compte Ubuntoo depuis la session Ré'Actif Pro."""
    token_doc = await get_current_token(data.token)
    user = await db.ubuntoo_users.find_one({"id": token_doc["id"]}, {"_id": 0})
    if not user:
        pseudo = token_doc.get("pseudo") or token_doc.get("identifiant") or "Membre"
        email = str(token_doc.get("identifiant") or pseudo).strip().lower()
        if "@" not in email:
            email = f"{email}@reactif.pro"
        user = {
            "id": token_doc["id"],
            "email": email,
            "full_name": str(pseudo).title(),
            "bio": "",
            "status": UserStatus.MEMBER,
            "badges": ["welcome"],
            "avatar_url": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.ubuntoo_users.insert_one(dict(user))
    return AuthResponse(token=create_token(user["id"]), user=user_to_response(user))

@router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return user_to_response(current_user)

# ============== USERS ==============

@router.get("/users", response_model=List[UserResponse])
async def get_users(current_user: dict = Depends(get_current_user)):
    users = await db.ubuntoo_users.find({}, {"_id": 0, "password": 0}).to_list(100)
    return [user_to_response(u) for u in users]

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    user = await db.ubuntoo_users.find_one({"id": user_id}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_response(user)

@router.put("/users/profile", response_model=UserResponse)
async def update_profile(data: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if update_data:
        await db.ubuntoo_users.update_one({"id": current_user["id"]}, {"$set": update_data})
    updated = await db.ubuntoo_users.find_one({"id": current_user["id"]}, {"_id": 0, "password": 0})
    return user_to_response(updated)

# ============== POSTS ==============

@router.post("/posts", response_model=PostResponse)
async def create_post(data: PostCreate, current_user: dict = Depends(get_current_user)):
    post_id = str(uuid.uuid4())
    post_doc = {
        "id": post_id, "author_id": current_user["id"], "content": data.content,
        "post_type": data.post_type, "likes": [], "reactions": {},
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.ubuntoo_posts.insert_one(post_doc)
    await check_experience_badges(current_user["id"], "first_post")
    if data.post_type == "resource":
        await check_experience_badges(current_user["id"], "resource_shared")
    return PostResponse(
        id=post_id, author_id=current_user["id"], author_name=current_user["full_name"],
        author_role=current_user.get("status", "member"), author_avatar=current_user.get("avatar_url"),
        content=data.content, post_type=data.post_type, likes=[], reactions={},
        comments_count=0, created_at=post_doc["created_at"]
    )

@router.get("/posts", response_model=List[PostResponse])
async def get_posts(post_type: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    query = {}
    if post_type:
        query["post_type"] = post_type
    posts = await db.ubuntoo_posts.find(query, {"_id": 0}).sort("created_at", -1).to_list(50)
    authors = await fetch_authors_map([p["author_id"] for p in posts])
    post_ids = [p["id"] for p in posts]
    counts_agg = await db.ubuntoo_comments.aggregate([
        {"$match": {"post_id": {"$in": post_ids}}},
        {"$group": {"_id": "$post_id", "c": {"$sum": 1}}}
    ]).to_list(len(post_ids) or 1)
    counts = {x["_id"]: x["c"] for x in counts_agg}
    result = []
    for post in posts:
        author = authors.get(post["author_id"])
        result.append(PostResponse(
            id=post["id"], author_id=post["author_id"],
            author_name=author["full_name"] if author else "Unknown",
            author_role=(author.get("status", author.get("role", "member")) if author else "member"),
            author_avatar=author.get("avatar_url") if author else None,
            content=post["content"], post_type=post["post_type"],
            likes=post.get("likes", []), reactions=post.get("reactions", {}),
            comments_count=counts.get(post["id"], 0), created_at=post["created_at"]
        ))
    return result

@router.post("/posts/{post_id}/like")
async def like_post(post_id: str, current_user: dict = Depends(get_current_user)):
    post = await db.ubuntoo_posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if current_user["id"] in post.get("likes", []):
        await db.ubuntoo_posts.update_one({"id": post_id}, {"$pull": {"likes": current_user["id"]}})
        return {"liked": False}
    await db.ubuntoo_posts.update_one({"id": post_id}, {"$addToSet": {"likes": current_user["id"]}})
    return {"liked": True}

REACTIONS = ["merci", "bravo", "interessant", "courage", "inspirant"]

@router.post("/posts/{post_id}/react")
async def react_post(post_id: str, data: ReactionRequest, current_user: dict = Depends(get_current_user)):
    if data.reaction_type not in REACTIONS:
        raise HTTPException(status_code=400, detail="Réaction invalide")
    post = await db.ubuntoo_posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Publication introuvable")
    uid = current_user["id"]
    reactions = post.get("reactions", {})
    active = next((r for r in REACTIONS if uid in reactions.get(r, [])), None)
    if active == data.reaction_type:
        await db.ubuntoo_posts.update_one({"id": post_id}, {"$pull": {f"reactions.{data.reaction_type}": uid}})
        return {"reaction": None}
    pull_ops = {f"reactions.{r}": uid for r in REACTIONS}
    await db.ubuntoo_posts.update_one({"id": post_id}, {"$pull": pull_ops})
    await db.ubuntoo_posts.update_one({"id": post_id}, {"$addToSet": {f"reactions.{data.reaction_type}": uid}})
    return {"reaction": data.reaction_type}

# ============== COMMENTS ==============

@router.post("/comments", response_model=CommentResponse)
async def create_comment(data: CommentCreate, current_user: dict = Depends(get_current_user)):
    post = await db.ubuntoo_posts.find_one({"id": data.post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comment_id = str(uuid.uuid4())
    comment_doc = {
        "id": comment_id, "post_id": data.post_id, "author_id": current_user["id"],
        "content": data.content, "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.ubuntoo_comments.insert_one(comment_doc)
    await check_experience_badges(current_user["id"], "first_comment")
    await check_experience_badges(post["author_id"], "received_comment", {"post_author_id": post["author_id"]})
    return CommentResponse(
        id=comment_id, post_id=data.post_id, author_id=current_user["id"],
        author_name=current_user["full_name"], author_role=current_user.get("status", "member"),
        content=data.content, created_at=comment_doc["created_at"]
    )

@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
async def get_comments(post_id: str, current_user: dict = Depends(get_current_user)):
    comments = await db.ubuntoo_comments.find({"post_id": post_id}, {"_id": 0}).sort("created_at", 1).to_list(100)
    authors = await fetch_authors_map([c["author_id"] for c in comments])
    result = []
    for comment in comments:
        author = authors.get(comment["author_id"])
        result.append(CommentResponse(
            id=comment["id"], post_id=comment["post_id"], author_id=comment["author_id"],
            author_name=author["full_name"] if author else "Unknown",
            author_role=(author.get("status", author.get("role", "member")) if author else "member"),
            content=comment["content"], created_at=comment["created_at"]
        ))
    return result

# ============== MESSAGES ==============

@router.post("/messages", response_model=MessageResponse)
async def send_message(data: MessageCreate, current_user: dict = Depends(get_current_user)):
    receiver = await db.ubuntoo_users.find_one({"id": data.receiver_id})
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    msg = await deliver_message(current_user, data.receiver_id, data.content)
    return MessageResponse(**msg)

@router.get("/messages/conversations", response_model=List[ConversationResponse])
async def get_conversations(current_user: dict = Depends(get_current_user)):
    pipeline = [
        {"$match": {"$or": [{"sender_id": current_user["id"]}, {"receiver_id": current_user["id"]}]}},
        {"$sort": {"created_at": -1}},
        {"$group": {
            "_id": {"$cond": [{"$eq": ["$sender_id", current_user["id"]]}, "$receiver_id", "$sender_id"]},
            "last_message": {"$first": "$content"},
            "last_message_time": {"$first": "$created_at"},
            "unread_count": {"$sum": {"$cond": [
                {"$and": [{"$eq": ["$receiver_id", current_user["id"]]}, {"$eq": ["$read", False]}]}, 1, 0]}}
        }}
    ]
    conversations = await db.ubuntoo_messages.aggregate(pipeline).to_list(50)
    users_map = await fetch_authors_map([conv["_id"] for conv in conversations])
    result = []
    for conv in conversations:
        user = users_map.get(conv["_id"])
        if user:
            result.append(ConversationResponse(
                user_id=user["id"], user_name=user["full_name"], user_avatar=user.get("avatar_url"),
                user_role=user.get("status", user.get("role", "member")),
                last_message=conv["last_message"], last_message_time=conv["last_message_time"],
                unread_count=conv["unread_count"], online=manager.is_online(user["id"])
            ))
    return result

@router.get("/messages/{user_id}", response_model=List[MessageResponse])
async def get_messages_with_user(user_id: str, current_user: dict = Depends(get_current_user)):
    messages = await db.ubuntoo_messages.find({
        "$or": [
            {"sender_id": current_user["id"], "receiver_id": user_id},
            {"sender_id": user_id, "receiver_id": current_user["id"]}
        ]
    }, {"_id": 0}).sort("created_at", 1).to_list(100)
    await db.ubuntoo_messages.update_many(
        {"sender_id": user_id, "receiver_id": current_user["id"], "read": False},
        {"$set": {"read": True, "status": "read"}}
    )
    await manager.send_to_user(user_id, {"type": "read", "by": current_user["id"]})
    senders = await fetch_authors_map([m["sender_id"] for m in messages])
    result = []
    for msg in messages:
        sender = senders.get(msg["sender_id"])
        result.append(MessageResponse(
            id=msg["id"], sender_id=msg["sender_id"],
            sender_name=sender["full_name"] if sender else "Unknown",
            receiver_id=msg["receiver_id"], content=msg["content"], read=msg["read"],
            status=msg.get("status", "read" if msg.get("read") else "sent"),
            created_at=msg["created_at"]
        ))
    return result

# ============== REALTIME WEBSOCKET ==============

@router.get("/presence")
async def get_presence(current_user: dict = Depends(get_current_user)):
    return {"online": list(manager.active.keys())}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = ""):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user = await db.ubuntoo_users.find_one({"id": user_id}, {"_id": 0})
    except Exception:
        await websocket.close(code=1008)
        return
    if not user:
        await websocket.close(code=1008)
        return
    await manager.connect(user_id, websocket)
    await websocket.send_json({"type": "presence_snapshot", "online": list(manager.active.keys())})
    await broadcast_presence(user_id, True)
    try:
        while True:
            data = await websocket.receive_json()
            mtype = data.get("type")
            if mtype == "message":
                receiver_id = data.get("receiver_id")
                content = (data.get("content") or "").strip()
                if receiver_id and content:
                    await deliver_message(user, receiver_id, content)
            elif mtype == "typing":
                receiver_id = data.get("receiver_id")
                if receiver_id:
                    await manager.send_to_user(receiver_id, {
                        "type": "typing", "from": user_id, "is_typing": bool(data.get("is_typing"))
                    })
            elif mtype == "read":
                sender_id = data.get("sender_id")
                if sender_id:
                    await db.ubuntoo_messages.update_many(
                        {"sender_id": sender_id, "receiver_id": user_id, "read": False},
                        {"$set": {"read": True, "status": "read"}}
                    )
                    await manager.send_to_user(sender_id, {"type": "read", "by": user_id})
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
        await db.ubuntoo_users.update_one({"id": user_id}, {"$set": {"last_seen": datetime.now(timezone.utc).isoformat()}})
        if not manager.is_online(user_id):
            await broadcast_presence(user_id, False)
    except Exception:
        manager.disconnect(user_id, websocket)

# ============== GROUPS ==============

@router.post("/groups", response_model=GroupResponse)
async def create_group(data: GroupCreate, current_user: dict = Depends(get_current_user)):
    group_id = str(uuid.uuid4())
    group_doc = {
        "id": group_id, "name": data.name, "description": data.description,
        "category": data.category, "creator_id": current_user["id"],
        "members": [current_user["id"]], "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.ubuntoo_groups.insert_one(group_doc)
    await check_experience_badges(current_user["id"], "group_created")
    return GroupResponse(
        id=group_id, name=data.name, description=data.description, category=data.category,
        creator_id=current_user["id"], members_count=1, created_at=group_doc["created_at"]
    )

@router.get("/groups", response_model=List[GroupResponse])
async def get_groups(category: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    query = {}
    if category:
        query["category"] = category
    groups = await db.ubuntoo_groups.find(query, {"_id": 0}).to_list(50)
    return [GroupResponse(
        id=g["id"], name=g["name"], description=g["description"], category=g["category"],
        creator_id=g["creator_id"], members_count=len(g.get("members", [])), created_at=g["created_at"]
    ) for g in groups]

@router.post("/groups/{group_id}/join")
async def join_group(group_id: str, current_user: dict = Depends(get_current_user)):
    group = await db.ubuntoo_groups.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if current_user["id"] in group.get("members", []):
        await db.ubuntoo_groups.update_one({"id": group_id}, {"$pull": {"members": current_user["id"]}})
        return {"joined": False}
    await db.ubuntoo_groups.update_one({"id": group_id}, {"$addToSet": {"members": current_user["id"]}})
    await check_experience_badges(current_user["id"], "joined_group")
    return {"joined": True}

@router.get("/groups/{group_id}", response_model=GroupResponse)
async def get_group(group_id: str, current_user: dict = Depends(get_current_user)):
    group = await db.ubuntoo_groups.find_one({"id": group_id}, {"_id": 0})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return GroupResponse(
        id=group["id"], name=group["name"], description=group["description"],
        category=group["category"], creator_id=group["creator_id"],
        members_count=len(group.get("members", [])), created_at=group["created_at"]
    )

# ============== DISCUSSIONS ==============

@router.post("/discussions", response_model=DiscussionResponse)
async def create_discussion(data: DiscussionCreate, current_user: dict = Depends(get_current_user)):
    group = await db.ubuntoo_groups.find_one({"id": data.group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    discussion_id = str(uuid.uuid4())
    discussion_doc = {
        "id": discussion_id, "title": data.title, "content": data.content,
        "group_id": data.group_id, "author_id": current_user["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.ubuntoo_discussions.insert_one(discussion_doc)
    await check_experience_badges(current_user["id"], "discussion_created")
    return DiscussionResponse(
        id=discussion_id, title=data.title, content=data.content, group_id=data.group_id,
        author_id=current_user["id"], author_name=current_user["full_name"],
        author_role=current_user.get("status", "member"), replies_count=0,
        created_at=discussion_doc["created_at"]
    )

@router.get("/groups/{group_id}/discussions", response_model=List[DiscussionResponse])
async def get_group_discussions(group_id: str, current_user: dict = Depends(get_current_user)):
    discussions = await db.ubuntoo_discussions.find({"group_id": group_id}, {"_id": 0}).sort("created_at", -1).to_list(50)
    authors = await fetch_authors_map([d["author_id"] for d in discussions])
    disc_ids = [d["id"] for d in discussions]
    counts_agg = await db.ubuntoo_replies.aggregate([
        {"$match": {"discussion_id": {"$in": disc_ids}}},
        {"$group": {"_id": "$discussion_id", "c": {"$sum": 1}}}
    ]).to_list(len(disc_ids) or 1)
    counts = {x["_id"]: x["c"] for x in counts_agg}
    result = []
    for d in discussions:
        author = authors.get(d["author_id"])
        result.append(DiscussionResponse(
            id=d["id"], title=d["title"], content=d["content"], group_id=d["group_id"],
            author_id=d["author_id"], author_name=author["full_name"] if author else "Unknown",
            author_role=(author.get("status", author.get("role", "member")) if author else "member"),
            replies_count=counts.get(d["id"], 0), created_at=d["created_at"]
        ))
    return result

@router.get("/discussions/{discussion_id}", response_model=DiscussionResponse)
async def get_discussion(discussion_id: str, current_user: dict = Depends(get_current_user)):
    discussion = await db.ubuntoo_discussions.find_one({"id": discussion_id}, {"_id": 0})
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")
    author = await db.ubuntoo_users.find_one({"id": discussion["author_id"]}, {"_id": 0})
    replies_count = await db.ubuntoo_replies.count_documents({"discussion_id": discussion_id})
    return DiscussionResponse(
        id=discussion["id"], title=discussion["title"], content=discussion["content"],
        group_id=discussion["group_id"], author_id=discussion["author_id"],
        author_name=author["full_name"] if author else "Unknown",
        author_role=(author.get("status", author.get("role", "member")) if author else "member"),
        replies_count=replies_count, created_at=discussion["created_at"]
    )

@router.post("/discussions/{discussion_id}/replies", response_model=DiscussionReplyResponse)
async def create_discussion_reply(discussion_id: str, data: DiscussionReplyCreate, current_user: dict = Depends(get_current_user)):
    discussion = await db.ubuntoo_discussions.find_one({"id": discussion_id})
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")
    reply_id = str(uuid.uuid4())
    reply_doc = {
        "id": reply_id, "discussion_id": discussion_id, "author_id": current_user["id"],
        "content": data.content, "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.ubuntoo_replies.insert_one(reply_doc)
    await check_experience_badges(current_user["id"], "discussion_reply")
    return DiscussionReplyResponse(
        id=reply_id, discussion_id=discussion_id, author_id=current_user["id"],
        author_name=current_user["full_name"], author_role=current_user.get("status", "member"),
        content=data.content, created_at=reply_doc["created_at"]
    )

@router.get("/discussions/{discussion_id}/replies", response_model=List[DiscussionReplyResponse])
async def get_discussion_replies(discussion_id: str, current_user: dict = Depends(get_current_user)):
    replies = await db.ubuntoo_replies.find({"discussion_id": discussion_id}, {"_id": 0}).sort("created_at", 1).to_list(100)
    authors = await fetch_authors_map([r["author_id"] for r in replies])
    result = []
    for r in replies:
        author = authors.get(r["author_id"])
        result.append(DiscussionReplyResponse(
            id=r["id"], discussion_id=r["discussion_id"], author_id=r["author_id"],
            author_name=author["full_name"] if author else "Unknown",
            author_role=(author.get("status", author.get("role", "member")) if author else "member"),
            content=r["content"], created_at=r["created_at"]
        ))
    return result

# ============== REPORTS / SEARCH / BADGES / STATS ==============

@router.post("/reports")
async def create_report(data: ReportRequest, current_user: dict = Depends(get_current_user)):
    report_id = str(uuid.uuid4())
    await db.ubuntoo_reports.insert_one({
        "id": report_id, "target_type": data.target_type, "target_id": data.target_id,
        "reason": data.reason, "reporter_id": current_user["id"], "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    return {"message": "Signalement transmis à la modération", "id": report_id}

@router.get("/search")
async def search(q: str, current_user: dict = Depends(get_current_user)):
    q = q.strip()
    if not q:
        return {"users": [], "posts": [], "groups": []}
    regex = {"$regex": q, "$options": "i"}
    users_docs = await db.ubuntoo_users.find({"$or": [
        {"full_name": regex}, {"bio": regex}, {"sector": regex},
        {"skills": regex}, {"jobs_sought": regex}, {"location": regex}
    ]}, {"_id": 0, "password": 0}).to_list(20)
    users = [{"id": u["id"], "full_name": u["full_name"], "bio": u.get("bio", ""),
              "sector": u.get("sector", ""), "location": u.get("location", "")} for u in users_docs]
    posts_docs = await db.ubuntoo_posts.find({"content": regex}, {"_id": 0}).sort("created_at", -1).to_list(20)
    post_authors = await fetch_authors_map([p["author_id"] for p in posts_docs])
    posts = []
    for p in posts_docs:
        author = post_authors.get(p["author_id"])
        posts.append({"id": p["id"], "content": p["content"], "post_type": p.get("post_type", "general"),
                      "author_name": author["full_name"] if author else "Inconnu", "created_at": p["created_at"]})
    groups_docs = await db.ubuntoo_groups.find({"$or": [{"name": regex}, {"description": regex}]}, {"_id": 0}).to_list(20)
    groups = [{"id": g["id"], "name": g["name"], "description": g["description"],
               "category": g["category"], "members_count": len(g.get("members", []))} for g in groups_docs]
    return {"users": users, "posts": posts, "groups": groups}

BADGES = [
    {"id": "welcome", "name": "Bienvenue", "description": "Vous faites partie de la communauté", "icon": "🌱", "category": "parcours"},
    {"id": "first_post", "name": "Premier pas", "description": "Vous avez osé vous exprimer", "icon": "💬", "category": "parcours"},
    {"id": "voice_heard", "name": "Voix entendue", "description": "Quelqu'un vous a écouté", "icon": "👂", "category": "parcours"},
    {"id": "one_month", "name": "1 mois parmi nous", "description": "Vous êtes fidèle à la communauté", "icon": "📅", "category": "parcours"},
    {"id": "helping_hand", "name": "Main tendue", "description": "Vous avez soutenu quelqu'un", "icon": "🤝", "category": "entraide"},
    {"id": "good_listener", "name": "Oreille attentive", "description": "Vous prenez le temps d'écouter", "icon": "💭", "category": "entraide"},
    {"id": "knowledge_sharer", "name": "Passeur", "description": "Vous transmettez votre savoir", "icon": "📚", "category": "entraide"},
    {"id": "connection_made", "name": "Lien créé", "description": "Vous avez créé une connexion", "icon": "🔗", "category": "entraide"},
    {"id": "builder", "name": "Bâtisseur", "description": "Vous créez des espaces d'échange", "icon": "🏠", "category": "communaute"},
    {"id": "facilitator", "name": "Facilitateur", "description": "Vous initiez le dialogue", "icon": "💡", "category": "communaute"},
    {"id": "weaver", "name": "Tisserand", "description": "Vous tissez des liens", "icon": "🕸️", "category": "communaute"},
]

@router.get("/badges", response_model=List[dict])
async def get_all_badges(current_user: dict = Depends(get_current_user)):
    return BADGES

@router.get("/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    return {
        "users_count": await db.ubuntoo_users.count_documents({}),
        "posts_count": await db.ubuntoo_posts.count_documents({}),
        "groups_count": await db.ubuntoo_groups.count_documents({}),
        "discussions_count": await db.ubuntoo_discussions.count_documents({}),
    }

# ============== LEGACY PROTOTYPE (démo /ubuntoo-ancien) ==============

def _legacy_trust_score(d: dict) -> int:
    score = 50
    score += min(len(d.get("soft_skills", [])) * 5, 20)
    score += min(len(d.get("values", [])) * 3, 10)
    if d.get("professional_sector"):
        score += 5
    score += min(len(d.get("target_jobs", [])) * 2, 10)
    if d.get("potential_score", 0) > 0:
        score += 5
    return min(score, 100)

@router.post("/legacy/import-reactif-pro")
async def legacy_import_reactif_pro(payload: dict):
    """Mock import RE'ACTIF PRO pour le prototype historique."""
    data = {
        "user_id": payload.get("user_id", "demo-user-001"),
        "name": "Marie Dupont",
        "territory": "Grand Est",
        "soft_skills": [
            {"name": "Empathie", "level": 85, "certified": True},
            {"name": "Adaptabilité", "level": 78, "certified": True},
            {"name": "Organisation", "level": 72, "certified": True},
            {"name": "Communication", "level": 80, "certified": False},
            {"name": "Travail en équipe", "level": 88, "certified": True},
            {"name": "Résolution de problèmes", "level": 70, "certified": False},
        ],
        "values": ["Solidarité", "Entraide", "Développement personnel", "Innovation sociale"],
        "professional_sector": "Services à la personne / Économie sociale et solidaire",
        "target_jobs": ["Conseiller en insertion professionnelle", "Chargé de projet ESS", "Médiateur social", "Formateur adultes"],
        "potential_score": 82,
        "adaptation_potential": 76,
        "trajectory": "Reconversion professionnelle - Secteur social",
    }
    profile = {**data, "status": "Membre actif", "trust_score": _legacy_trust_score(data),
               "badges": ["Profil RE'ACTIF PRO"], "reactif_pro_synced": True}
    return {"status": "success", "message": "Profil importé depuis RE'ACTIF PRO (démo)", "profile": profile}
