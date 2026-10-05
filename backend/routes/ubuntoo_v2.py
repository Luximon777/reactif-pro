"""UBUNTOO v2 — réseau professionnel communautaire (MVP CDC section 31). API-first, compte Ré'Actif Pro unique."""
import uuid
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from database import db, get_current_token, search_word_patterns

router = APIRouter(prefix="/api/ubuntoo2")

HELP_OFFERS = ["Mentorat", "Partage d'expérience", "Conseil métier", "Découverte d'un secteur", "Préparation d'entretien", "Réseau", "Orientation"]
POST_TYPES = ["question", "experience", "information", "ressource", "opportunite", "aide"]
REPORT_REASONS = ["Comportement inapproprié", "Discrimination", "Harcèlement", "Spam", "Fraude", "Contenu commercial non autorisé", "Fausse information professionnelle", "Atteinte à la confidentialité"]
PRIVACY_FIELDS = ["projet", "experiences", "competences", "soft_skills", "interests", "help_offers"]

BADGES = {
    "bienvenue": {"label": "Bienvenue UBUNTOO", "desc": "Profil complété et première participation"},
    "explorateur": {"label": "Explorateur métier", "desc": "Participation à plusieurs échanges sur des métiers"},
    "contributeur": {"label": "Contributeur", "desc": "Partage régulier de ressources utiles"},
    "mentor": {"label": "Mentor", "desc": "Participation active à un accompagnement"},
    "ambassadeur": {"label": "Ambassadeur", "desc": "Contribution durable à la communauté"},
    "passeport_pro": {"label": "Passeport professionnel", "desc": "Parcours ou compétences vérifiées via Ré'Actif Pro"},
}

SEED_COMMUNITIES = [
    ("metiers", "Informatique", "Développement, réseaux, data, cybersécurité : échangez entre professionnels du numérique."),
    ("metiers", "Industrie", "Production, maintenance, qualité : la communauté des métiers industriels."),
    ("metiers", "Commerce", "Vente, relation client, négociation : partagez vos pratiques commerciales."),
    ("metiers", "Santé", "Soins, accompagnement, médico-social : entraide entre professionnels de santé."),
    ("metiers", "Logistique", "Transport, supply chain, entreposage : les métiers de la logistique."),
    ("metiers", "BTP", "Gros œuvre, second œuvre, conduite de travaux : la communauté du bâtiment."),
    ("situations", "Reconversion professionnelle", "Vous changez de métier ? Partagez vos questions et vos parcours de reconversion."),
    ("situations", "Recherche d'emploi", "Conseils, entraide et soutien pour votre recherche d'emploi."),
    ("situations", "Création d'entreprise", "Entrepreneurs et porteurs de projet : avancez ensemble."),
    ("situations", "Premier emploi", "Jeunes diplômés et débutants : réussir son entrée dans la vie active."),
    ("situations", "Retour à l'emploi", "Reprendre une activité après une pause : vous n'êtes pas seul(e)."),
    ("territoires", "Strasbourg", "Le réseau professionnel local de Strasbourg et son agglomération."),
    ("territoires", "Alsace", "Opportunités et entraide professionnelle en Alsace."),
    ("territoires", "Grand Est", "La communauté des professionnels de la région Grand Est."),
    ("territoires", "France", "Échanges professionnels à l'échelle nationale."),
    ("territoires", "Espace transfrontalier", "Travailler entre France, Allemagne, Suisse et Luxembourg."),
    ("thematiques", "Soft skills", "Développer et valoriser ses compétences comportementales."),
    ("thematiques", "Intelligence artificielle", "Comprendre et utiliser l'IA dans son métier."),
    ("thematiques", "Management", "Encadrer, animer, faire grandir une équipe."),
    ("thematiques", "Handicap et emploi", "Emploi et handicap : droits, pratiques, entraide."),
    ("thematiques", "Mobilité professionnelle", "Changer de poste, de région ou de secteur."),
    ("thematiques", "Formation", "Se former tout au long de la vie : dispositifs, retours d'expérience."),
]

now_iso = lambda: datetime.now(timezone.utc).isoformat()


async def _notify(token_id: str, ntype: str, text: str, link: str = ""):
    await db.ubuntoo2_notifications.insert_one({
        "id": str(uuid.uuid4()), "token_id": token_id, "type": ntype,
        "text": text, "link": link, "read": False, "created_at": now_iso()})


async def _get_or_create_profile(token_doc: dict) -> dict:
    token_id = token_doc["id"]
    prof = await db.ubuntoo2_profiles.find_one({"token_id": token_id}, {"_id": 0})
    if prof:
        return prof
    rp_profile = await db.profiles.find_one({"token_id": token_id}, {"_id": 0}) or {}
    passport = await db.passports.find_one({"token_id": token_id}, {"_id": 0}) or {}
    competences = passport.get("competences", []) or []
    sf = [c.get("name") for c in competences if isinstance(c, dict) and c.get("nature") == "savoir_faire" and c.get("name")][:12]
    se = [c.get("name") for c in competences if isinstance(c, dict) and c.get("nature") == "savoir_etre" and c.get("name")][:10]
    if not sf:
        sf = [c.get("name") for c in competences if isinstance(c, dict) and c.get("name")][:12]
    interests = [c.get("name") for c in competences if isinstance(c, dict) and c.get("source") == "centres_interet" and c.get("name")][:8]
    experiences = [{"title": e.get("title", ""), "organization": e.get("organization", "")}
                   for e in (passport.get("experiences") or []) if isinstance(e, dict) and e.get("title")][:6]
    projet = passport.get("career_project") or passport.get("professional_summary") or ""
    if isinstance(projet, list):
        projet = ", ".join(str(p) for p in projet[:3])
    prof = {
        "token_id": token_id,
        "display_name": token_doc.get("pseudo") or rp_profile.get("name") or f"Membre {token_id[:6].upper()}",
        "headline": str(projet)[:160],
        "projet": str(projet)[:600],
        "experiences": experiences,
        "competences": sf,
        "soft_skills": se,
        "interests": interests,
        "help_offers": [],
        "mentoring_role": "none",
        "mentoring_topics": [],
        "mentoring_goal": "",
        "privacy": {f: "reseau" for f in PRIVACY_FIELDS},
        "created_at": now_iso(),
    }
    await db.ubuntoo2_profiles.insert_one({**prof})
    return prof


async def _are_contacts(a: str, b: str) -> bool:
    doc = await db.ubuntoo2_connections.find_one({
        "status": "accepted",
        "$or": [{"from_id": a, "to_id": b}, {"from_id": b, "to_id": a}]})
    return bool(doc)


def _filter_profile(prof: dict, is_self: bool, is_contact: bool) -> dict:
    out = {"token_id": prof["token_id"], "display_name": prof.get("display_name", ""), "headline": "", "is_contact": is_contact,
           "mentoring_role": prof.get("mentoring_role", "none"), "badges": prof.get("badges_earned", []),
           "mentoring_topics": prof.get("mentoring_topics", [])}
    privacy = prof.get("privacy", {})
    def visible(field):
        lvl = privacy.get(field, "reseau")
        return is_self or lvl == "public" or (lvl == "reseau" and is_contact)
    if is_self or visible("projet"):
        out["headline"] = prof.get("headline", "")
        out["projet"] = prof.get("projet", "")
    for f, key in [("experiences", "experiences"), ("competences", "competences"), ("soft_skills", "soft_skills"), ("interests", "interests"), ("help_offers", "help_offers")]:
        pf = "competences" if f == "competences" else f
        if is_self or visible("experiences" if f == "experiences" else pf if pf in PRIVACY_FIELDS else "competences"):
            out[key] = prof.get(key, [])
    if is_self:
        out["privacy"] = privacy
    return out


# ============== PROFIL ==============

@router.get("/me")
async def get_me(token: str):
    token_doc = await get_current_token(token)
    prof = await _get_or_create_profile(token_doc)
    return _filter_profile(prof, True, True)


@router.put("/me")
async def update_me(token: str, body: dict):
    token_doc = await get_current_token(token)
    await _get_or_create_profile(token_doc)
    allowed = {"display_name", "headline", "projet", "competences", "soft_skills", "interests", "help_offers", "privacy",
               "mentoring_role", "mentoring_topics", "mentoring_goal"}
    update = {k: v for k, v in body.items() if k in allowed}
    if "mentoring_role" in update and update["mentoring_role"] not in ("none", "mentor", "mentee", "both"):
        update.pop("mentoring_role")
    if "privacy" in update:
        update["privacy"] = {f: v for f, v in update["privacy"].items() if f in PRIVACY_FIELDS and v in ("prive", "reseau", "public")}
    if update:
        await db.ubuntoo2_profiles.update_one({"token_id": token_doc["id"]}, {"$set": update})
    prof = await db.ubuntoo2_profiles.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    return _filter_profile(prof, True, True)


@router.post("/me/sync")
async def resync_me(token: str):
    token_doc = await get_current_token(token)
    await db.ubuntoo2_profiles.delete_one({"token_id": token_doc["id"]})
    prof = await _get_or_create_profile(token_doc)
    return _filter_profile(prof, True, True)


@router.get("/members/{member_id}")
async def get_member(member_id: str, token: str):
    token_doc = await get_current_token(token)
    prof = await db.ubuntoo2_profiles.find_one({"token_id": member_id}, {"_id": 0})
    if not prof:
        raise HTTPException(status_code=404, detail="Membre introuvable")
    is_self = member_id == token_doc["id"]
    is_contact = False if is_self else await _are_contacts(token_doc["id"], member_id)
    return _filter_profile(prof, is_self, is_contact)


# ============== RECHERCHE MEMBRES ==============

@router.get("/members")
async def search_members(token: str, q: str = ""):
    token_doc = await get_current_token(token)
    me = token_doc["id"]
    await _get_or_create_profile(token_doc)
    query = {"token_id": {"$ne": me}}
    if q.strip():
        patterns = search_word_patterns(q)
        if patterns:
            ors = []
            for p in patterns:
                rx = {"$regex": p, "$options": "i"}
                ors.extend([{"display_name": rx}, {"headline": rx}, {"competences": rx}, {"soft_skills": rx}, {"interests": rx}])
            query["$or"] = ors
    profiles = await db.ubuntoo2_profiles.find(query, {"_id": 0}).to_list(50)
    conns = await db.ubuntoo2_connections.find(
        {"$or": [{"from_id": me}, {"to_id": me}]}, {"_id": 0}).to_list(500)
    status_map = {}
    for c in conns:
        other = c["to_id"] if c["from_id"] == me else c["from_id"]
        if c["status"] == "accepted":
            status_map[other] = "contact"
        elif c["status"] == "pending":
            status_map[other] = "pending_sent" if c["from_id"] == me else "pending_received"
    out = []
    for p in profiles:
        is_contact = status_map.get(p["token_id"]) == "contact"
        card = _filter_profile(p, False, is_contact)
        card["connection_status"] = status_map.get(p["token_id"], "none")
        out.append(card)
    return out


# ============== MISE EN RELATION (CONSENTEMENT) ==============

@router.post("/connections")
async def request_connection(token: str, body: dict):
    token_doc = await get_current_token(token)
    me = token_doc["id"]
    to_id = body.get("to_id")
    message = (body.get("message") or "").strip()[:300]
    if not to_id or to_id == me:
        raise HTTPException(status_code=400, detail="Destinataire invalide")
    target = await db.ubuntoo2_profiles.find_one({"token_id": to_id})
    if not target:
        raise HTTPException(status_code=404, detail="Membre introuvable")
    kind = body.get("kind") if body.get("kind") in ("standard", "mentorat") else "standard"
    kind_filter = {"kind": "mentorat"} if kind == "mentorat" else {"kind": {"$ne": "mentorat"}}
    existing = await db.ubuntoo2_connections.find_one({
        "status": {"$in": ["pending", "accepted"]}, **kind_filter,
        "$or": [{"from_id": me, "to_id": to_id}, {"from_id": to_id, "to_id": me}]})
    if existing:
        raise HTTPException(status_code=400, detail="Une demande ou une relation de ce type existe déjà avec ce membre.")
    my_prof = await _get_or_create_profile(token_doc)
    conn = {"id": str(uuid.uuid4()), "from_id": me, "to_id": to_id, "message": message,
            "kind": kind, "status": "pending", "created_at": now_iso()}
    if kind == "mentorat":
        as_role = body.get("as_role") if body.get("as_role") in ("mentor", "mentee") else "mentee"
        conn["mentor_id"] = me if as_role == "mentor" else to_id
        conn["mentee_id"] = to_id if as_role == "mentor" else me
    await db.ubuntoo2_connections.insert_one({**conn})
    notif_text = (f"{my_prof.get('display_name')} vous propose un accompagnement mentorat" if kind == "mentorat" and conn.get("mentor_id") == me
                  else f"{my_prof.get('display_name')} souhaite être accompagné(e) par vous (mentorat)" if kind == "mentorat"
                  else f"{my_prof.get('display_name')} souhaite entrer en contact avec vous")
    await _notify(to_id, "connection_request", notif_text + (f" : « {message} »" if message else "."), "/ubuntoo/reseau")
    return conn


@router.get("/connections")
async def list_connections(token: str, box: str = "received"):
    token_doc = await get_current_token(token)
    me = token_doc["id"]
    query = {"to_id": me, "status": "pending"} if box == "received" else {"from_id": me, "status": "pending"}
    conns = await db.ubuntoo2_connections.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    for c in conns:
        other = c["from_id"] if box == "received" else c["to_id"]
        prof = await db.ubuntoo2_profiles.find_one({"token_id": other}, {"_id": 0})
        c["member"] = _filter_profile(prof, False, False) if prof else {"display_name": "Membre", "token_id": other}
    return conns


@router.post("/connections/{conn_id}/respond")
async def respond_connection(conn_id: str, token: str, body: dict):
    token_doc = await get_current_token(token)
    action = body.get("action")
    if action not in ("accept", "decline"):
        raise HTTPException(status_code=400, detail="Action invalide")
    conn = await db.ubuntoo2_connections.find_one({"id": conn_id, "to_id": token_doc["id"], "status": "pending"})
    if not conn:
        raise HTTPException(status_code=404, detail="Demande introuvable")
    new_status = "accepted" if action == "accept" else "declined"
    await db.ubuntoo2_connections.update_one({"id": conn_id}, {"$set": {"status": new_status, "responded_at": now_iso()}})
    if action == "accept":
        my_prof = await _get_or_create_profile(token_doc)
        label = "votre proposition de mentorat" if conn.get("kind") == "mentorat" else "votre demande de mise en relation"
        await _notify(conn["from_id"], "connection_accepted",
                      f"{my_prof.get('display_name')} a accepté {label}.", "/ubuntoo/reseau")
    return {"status": new_status}


@router.get("/contacts")
async def list_contacts(token: str):
    token_doc = await get_current_token(token)
    me = token_doc["id"]
    conns = await db.ubuntoo2_connections.find(
        {"status": "accepted", "$or": [{"from_id": me}, {"to_id": me}]}, {"_id": 0}).sort("responded_at", -1).to_list(300)
    out = []
    seen = set()
    for c in conns:
        other = c["to_id"] if c["from_id"] == me else c["from_id"]
        if other in seen:
            continue
        seen.add(other)
        prof = await db.ubuntoo2_profiles.find_one({"token_id": other}, {"_id": 0})
        if prof:
            card = _filter_profile(prof, False, True)
            card["since"] = c.get("responded_at")
            out.append(card)
    return out


# ============== MESSAGERIE INDIVIDUELLE ==============

@router.post("/conversations")
async def open_conversation(token: str, body: dict):
    token_doc = await get_current_token(token)
    me = token_doc["id"]
    contact_id = body.get("contact_id")
    if not contact_id or not await _are_contacts(me, contact_id):
        raise HTTPException(status_code=403, detail="La messagerie est réservée à vos contacts acceptés.")
    conv = await db.ubuntoo2_conversations.find_one({"participants": {"$all": [me, contact_id]}}, {"_id": 0})
    if not conv:
        conv = {"id": str(uuid.uuid4()), "participants": [me, contact_id],
                "created_at": now_iso(), "last_message_at": None, "last_message_text": ""}
        await db.ubuntoo2_conversations.insert_one({**conv})
    return conv


@router.get("/conversations")
async def list_conversations(token: str):
    token_doc = await get_current_token(token)
    me = token_doc["id"]
    convs = await db.ubuntoo2_conversations.find({"participants": me}, {"_id": 0}).sort("last_message_at", -1).to_list(100)
    for c in convs:
        other = next((p for p in c["participants"] if p != me), None)
        prof = await db.ubuntoo2_profiles.find_one({"token_id": other}, {"_id": 0, "display_name": 1, "token_id": 1})
        c["other"] = {"token_id": other, "display_name": (prof or {}).get("display_name", "Membre")}
        c["unread"] = await db.ubuntoo2_messages.count_documents({"conversation_id": c["id"], "sender_id": {"$ne": me}, "read": False})
    return convs


@router.get("/conversations/{conv_id}/messages")
async def get_messages(conv_id: str, token: str):
    token_doc = await get_current_token(token)
    me = token_doc["id"]
    conv = await db.ubuntoo2_conversations.find_one({"id": conv_id, "participants": me})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation introuvable")
    await db.ubuntoo2_messages.update_many(
        {"conversation_id": conv_id, "sender_id": {"$ne": me}, "read": False}, {"$set": {"read": True}})
    return await db.ubuntoo2_messages.find({"conversation_id": conv_id}, {"_id": 0}).sort("created_at", 1).to_list(500)


@router.post("/conversations/{conv_id}/messages")
async def send_message(conv_id: str, token: str, body: dict):
    token_doc = await get_current_token(token)
    me = token_doc["id"]
    conv = await db.ubuntoo2_conversations.find_one({"id": conv_id, "participants": me})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation introuvable")
    text = (body.get("text") or "").strip()[:3000]
    if not text:
        raise HTTPException(status_code=400, detail="Message vide")
    msg = {"id": str(uuid.uuid4()), "conversation_id": conv_id, "sender_id": me,
           "text": text, "read": False, "created_at": now_iso()}
    await db.ubuntoo2_messages.insert_one({**msg})
    await db.ubuntoo2_conversations.update_one(
        {"id": conv_id}, {"$set": {"last_message_at": msg["created_at"], "last_message_text": text[:80]}})
    other = next((p for p in conv["participants"] if p != me), None)
    my_prof = await _get_or_create_profile(token_doc)
    await _notify(other, "new_message", f"Nouveau message de {my_prof.get('display_name')}", "/ubuntoo/messages")
    return msg


# ============== COMMUNAUTÉS ==============

async def _seed_communities():
    if await db.ubuntoo2_communities.count_documents({}) >= len(SEED_COMMUNITIES):
        return
    for cat, name, desc in SEED_COMMUNITIES:
        await db.ubuntoo2_communities.update_one(
            {"name": name},
            {"$setOnInsert": {"id": str(uuid.uuid4()), "name": name, "category": cat, "description": desc,
                              "members": [], "created_by": "system", "created_at": now_iso()}},
            upsert=True)
    logging.info("[Ubuntoo2] Communautés seedées")


@router.get("/communities")
async def list_communities(token: str, category: str = ""):
    token_doc = await get_current_token(token)
    await _seed_communities()
    query = {"category": category} if category else {}
    comms = await db.ubuntoo2_communities.find(query, {"_id": 0}).to_list(200)
    me = token_doc["id"]
    for c in comms:
        c["members_count"] = len(c.get("members", []))
        c["joined"] = me in c.get("members", [])
        c.pop("members", None)
    comms.sort(key=lambda c: (not c["joined"], -c["members_count"]))
    return comms


@router.post("/communities")
async def create_community(token: str, body: dict):
    token_doc = await get_current_token(token)
    name = (body.get("name") or "").strip()[:80]
    if len(name) < 3:
        raise HTTPException(status_code=400, detail="Nom trop court (3 caractères minimum)")
    if await db.ubuntoo2_communities.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}}):
        raise HTTPException(status_code=400, detail="Cette communauté existe déjà")
    comm = {"id": str(uuid.uuid4()), "name": name,
            "category": body.get("category") if body.get("category") in ("metiers", "situations", "territoires", "thematiques") else "thematiques",
            "description": (body.get("description") or "").strip()[:300],
            "members": [token_doc["id"]], "created_by": token_doc["id"], "created_at": now_iso()}
    await db.ubuntoo2_communities.insert_one({**comm})
    comm["members_count"] = 1
    comm["joined"] = True
    comm.pop("members")
    return comm


@router.post("/communities/{comm_id}/join")
async def join_community(comm_id: str, token: str):
    token_doc = await get_current_token(token)
    r = await db.ubuntoo2_communities.update_one({"id": comm_id}, {"$addToSet": {"members": token_doc["id"]}})
    if r.matched_count == 0:
        raise HTTPException(status_code=404, detail="Communauté introuvable")
    return {"status": "joined"}


@router.post("/communities/{comm_id}/leave")
async def leave_community(comm_id: str, token: str):
    token_doc = await get_current_token(token)
    await db.ubuntoo2_communities.update_one({"id": comm_id}, {"$pull": {"members": token_doc["id"]}})
    return {"status": "left"}


@router.get("/communities/{comm_id}")
async def get_community(comm_id: str, token: str):
    token_doc = await get_current_token(token)
    comm = await db.ubuntoo2_communities.find_one({"id": comm_id}, {"_id": 0})
    if not comm:
        raise HTTPException(status_code=404, detail="Communauté introuvable")
    comm["members_count"] = len(comm.get("members", []))
    comm["joined"] = token_doc["id"] in comm.get("members", [])
    comm.pop("members", None)
    return comm


# ============== PUBLICATIONS ==============

@router.get("/communities/{comm_id}/posts")
async def list_posts(comm_id: str, token: str, post_type: str = ""):
    token_doc = await get_current_token(token)
    query = {"community_id": comm_id}
    if post_type in POST_TYPES:
        query["type"] = post_type
    posts = await db.ubuntoo2_posts.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    me = token_doc["id"]
    for p in posts:
        p["utile_by_me"] = me in p.get("utile_by", [])
        p["utile_count"] = len(p.get("utile_by", []))
        p.pop("utile_by", None)
    return posts


@router.post("/communities/{comm_id}/posts")
async def create_post(comm_id: str, token: str, body: dict):
    token_doc = await get_current_token(token)
    comm = await db.ubuntoo2_communities.find_one({"id": comm_id})
    if not comm:
        raise HTTPException(status_code=404, detail="Communauté introuvable")
    if token_doc["id"] not in comm.get("members", []):
        raise HTTPException(status_code=403, detail="Rejoignez la communauté pour publier.")
    content = (body.get("content") or "").strip()[:4000]
    if len(content) < 3:
        raise HTTPException(status_code=400, detail="Contenu trop court")
    prof = await _get_or_create_profile(token_doc)
    post = {"id": str(uuid.uuid4()), "community_id": comm_id, "author_id": token_doc["id"],
            "author_name": prof.get("display_name", "Membre"),
            "type": body.get("type") if body.get("type") in POST_TYPES else "information",
            "title": (body.get("title") or "").strip()[:150], "content": content,
            "utile_by": [], "replies_count": 0, "created_at": now_iso()}
    await db.ubuntoo2_posts.insert_one({**post})
    post["utile_by_me"] = False
    post["utile_count"] = 0
    post.pop("utile_by")
    return post


@router.post("/posts/{post_id}/utile")
async def toggle_post_utile(post_id: str, token: str):
    token_doc = await get_current_token(token)
    me = token_doc["id"]
    post = await db.ubuntoo2_posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Publication introuvable")
    if me in post.get("utile_by", []):
        await db.ubuntoo2_posts.update_one({"id": post_id}, {"$pull": {"utile_by": me}})
        return {"utile": False, "utile_count": len(post.get("utile_by", [])) - 1}
    await db.ubuntoo2_posts.update_one({"id": post_id}, {"$addToSet": {"utile_by": me}})
    return {"utile": True, "utile_count": len(post.get("utile_by", [])) + 1}


@router.get("/posts/{post_id}/replies")
async def list_replies(post_id: str, token: str):
    await get_current_token(token)
    return await db.ubuntoo2_replies.find({"post_id": post_id}, {"_id": 0, "utile_by": 0}).sort("created_at", 1).to_list(200)


@router.post("/posts/{post_id}/replies")
async def create_reply(post_id: str, token: str, body: dict):
    token_doc = await get_current_token(token)
    post = await db.ubuntoo2_posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Publication introuvable")
    content = (body.get("content") or "").strip()[:2000]
    if len(content) < 2:
        raise HTTPException(status_code=400, detail="Réponse trop courte")
    prof = await _get_or_create_profile(token_doc)
    reply = {"id": str(uuid.uuid4()), "post_id": post_id, "author_id": token_doc["id"],
             "author_name": prof.get("display_name", "Membre"), "content": content, "created_at": now_iso()}
    await db.ubuntoo2_replies.insert_one({**reply})
    await db.ubuntoo2_posts.update_one({"id": post_id}, {"$inc": {"replies_count": 1}})
    if post["author_id"] != token_doc["id"]:
        await _notify(post["author_id"], "post_reply",
                      f"{prof.get('display_name')} a répondu à votre publication « {(post.get('title') or post.get('content',''))[:40]}… »",
                      f"/ubuntoo/communautes/{post['community_id']}")
    return reply


# ============== SIGNALEMENT ==============

@router.post("/reports")
async def create_report(token: str, body: dict):
    token_doc = await get_current_token(token)
    reason = body.get("reason")
    if reason not in REPORT_REASONS:
        raise HTTPException(status_code=400, detail="Motif invalide")
    report = {"id": str(uuid.uuid4()), "reporter_id": token_doc["id"],
              "target_type": body.get("target_type", "post"), "target_id": body.get("target_id", ""),
              "reason": reason, "details": (body.get("details") or "")[:500],
              "status": "open", "created_at": now_iso()}
    await db.ubuntoo2_reports.insert_one({**report})
    return {"status": "ok", "message": "Signalement transmis à la modération. Merci de contribuer à un espace sûr."}


# ============== NOTIFICATIONS ==============

@router.get("/notifications")
async def list_notifications(token: str):
    token_doc = await get_current_token(token)
    notifs = await db.ubuntoo2_notifications.find({"token_id": token_doc["id"]}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return notifs


@router.post("/notifications/mark-read")
async def mark_notifications_read(token: str):
    token_doc = await get_current_token(token)
    await db.ubuntoo2_notifications.update_many({"token_id": token_doc["id"], "read": False}, {"$set": {"read": True}})
    return {"status": "ok"}


# ============== MENTORAT ==============

def _match_score(my: dict, other: dict) -> tuple:
    mine = set(x.lower() for x in (my.get("competences", []) + my.get("interests", []) + my.get("mentoring_topics", [])) if x)
    theirs = set(x.lower() for x in (other.get("competences", []) + other.get("interests", []) + other.get("mentoring_topics", [])) if x)
    common = mine & theirs
    score = min(100, 30 + len(common) * 15)
    reasons = sorted(common)[:4]
    if "mentorat" in [h.lower() for h in other.get("help_offers", [])]:
        score = min(100, score + 10)
        reasons.append("Disponible pour le mentorat")
    return score, reasons


@router.get("/mentoring/matches")
async def mentoring_matches(token: str):
    token_doc = await get_current_token(token)
    me = token_doc["id"]
    my_prof = await _get_or_create_profile(token_doc)
    my_role = my_prof.get("mentoring_role", "none")
    if my_role == "none":
        return {"role": "none", "matches": []}
    target_roles = []
    if my_role in ("mentee", "both"):
        target_roles.append(("mentor", ["mentor", "both"]))
    if my_role in ("mentor", "both"):
        target_roles.append(("mentee", ["mentee", "both"]))
    out = []
    seen = set()
    for as_what, roles in target_roles:
        candidates = await db.ubuntoo2_profiles.find(
            {"token_id": {"$ne": me}, "mentoring_role": {"$in": roles}}, {"_id": 0}).to_list(100)
        for c in candidates:
            if c["token_id"] in seen:
                continue
            seen.add(c["token_id"])
            score, reasons = _match_score(my_prof, c)
            card = _filter_profile(c, False, await _are_contacts(me, c["token_id"]))
            card["match_score"] = score
            card["match_reasons"] = reasons
            card["propose_as"] = as_what
            existing = await db.ubuntoo2_connections.find_one({
                "status": {"$in": ["pending", "accepted"]}, "kind": "mentorat",
                "$or": [{"from_id": me, "to_id": c["token_id"]}, {"from_id": c["token_id"], "to_id": me}]})
            card["connection_status"] = ("contact" if existing and existing["status"] == "accepted"
                                         else "pending" if existing else "none")
            out.append(card)
    out.sort(key=lambda x: -x["match_score"])
    return {"role": my_role, "matches": out[:20]}


@router.get("/mentoring/relations")
async def mentoring_relations(token: str):
    token_doc = await get_current_token(token)
    me = token_doc["id"]
    conns = await db.ubuntoo2_connections.find(
        {"kind": "mentorat", "status": "accepted", "$or": [{"from_id": me}, {"to_id": me}]}, {"_id": 0}).to_list(50)
    mentors, mentores = [], []
    for c in conns:
        if c.get("mentor_id") == me:
            other = c.get("mentee_id")
            bucket = mentores
        else:
            other = c.get("mentor_id")
            bucket = mentors
        prof = await db.ubuntoo2_profiles.find_one({"token_id": other}, {"_id": 0})
        if prof:
            bucket.append(_filter_profile(prof, False, True))
    return {"mentors": mentors, "mentores": mentores}


# ============== BADGES ==============

async def _compute_badges(token_id: str) -> list:
    prof = await db.ubuntoo2_profiles.find_one({"token_id": token_id}, {"_id": 0}) or {}
    posts = await db.ubuntoo2_posts.find({"author_id": token_id}, {"_id": 0, "type": 1, "community_id": 1, "utile_by": 1}).to_list(500)
    replies_count = await db.ubuntoo2_replies.count_documents({"author_id": token_id})
    my_comms = await db.ubuntoo2_communities.find({"members": token_id}, {"_id": 0, "id": 1, "category": 1}).to_list(100)
    contributions = len(posts) + replies_count
    profil_complet = bool(prof.get("headline") or prof.get("projet")) and bool(prof.get("competences") or prof.get("help_offers"))

    metier_comm_ids = {c["id"] for c in my_comms if c.get("category") == "metiers"}
    all_metier_ids = {c["id"] for c in await db.ubuntoo2_communities.find({"category": "metiers"}, {"_id": 0, "id": 1}).to_list(100)}
    metier_posts = sum(1 for p in posts if p.get("community_id") in all_metier_ids)
    metier_replies = 0
    if all_metier_ids:
        metier_post_ids = [p["id"] for p in await db.ubuntoo2_posts.find({"community_id": {"$in": list(all_metier_ids)}}, {"_id": 0, "id": 1}).to_list(1000)]
        if metier_post_ids:
            metier_replies = await db.ubuntoo2_replies.count_documents({"author_id": token_id, "post_id": {"$in": metier_post_ids}})

    utiles_recus = sum(len(p.get("utile_by", [])) for p in posts)
    ressources = sum(1 for p in posts if p.get("type") in ("ressource", "information", "opportunite"))
    is_mentor = await db.ubuntoo2_connections.count_documents({"kind": "mentorat", "status": "accepted", "mentor_id": token_id}) > 0

    has_proof = await db["proof_documents.files"].count_documents({"metadata.token_id": token_id}) > 0
    passport = await db.passports.find_one({"token_id": token_id}, {"_id": 0, "completeness_score": 1})
    passeport_ok = has_proof or (passport or {}).get("completeness_score", 0) >= 70

    earned = {
        "bienvenue": profil_complet and (contributions >= 1 or len(my_comms) >= 1),
        "explorateur": (metier_posts + metier_replies) >= 3 or len(metier_comm_ids) >= 2,
        "contributeur": (ressources + replies_count) >= 5 or utiles_recus >= 3,
        "mentor": is_mentor,
        "ambassadeur": contributions >= 15 and len(my_comms) >= 3,
        "passeport_pro": passeport_ok,
    }
    existing = await db.ubuntoo2_badges.find_one({"token_id": token_id}, {"_id": 0}) or {"token_id": token_id, "earned": {}}
    newly = []
    for bid, ok in earned.items():
        if ok and bid not in existing["earned"]:
            existing["earned"][bid] = now_iso()
            newly.append(bid)
    if newly:
        await db.ubuntoo2_badges.update_one({"token_id": token_id}, {"$set": {"earned": existing["earned"]}}, upsert=True)
        await db.ubuntoo2_profiles.update_one({"token_id": token_id}, {"$set": {"badges_earned": list(existing["earned"].keys())}})
        for bid in newly:
            await _notify(token_id, "badge", f"Badge obtenu : « {BADGES[bid]['label']} » — {BADGES[bid]['desc']}.", "/ubuntoo/profil")
    return [{"id": bid, **BADGES[bid], "earned": bid in existing["earned"], "earned_at": existing["earned"].get(bid)}
            for bid in BADGES]


@router.get("/badges")
async def get_badges(token: str):
    token_doc = await get_current_token(token)
    return await _compute_badges(token_doc["id"])


# ============== TABLEAU DE BORD ==============

@router.get("/dashboard")
async def dashboard(token: str):
    token_doc = await get_current_token(token)
    me = token_doc["id"]
    prof = await _get_or_create_profile(token_doc)
    await _seed_communities()
    conns_all = await db.ubuntoo2_connections.find(
        {"status": "accepted", "$or": [{"from_id": me}, {"to_id": me}]}, {"_id": 0, "from_id": 1, "to_id": 1}).to_list(500)
    contacts_count = len({(c["to_id"] if c["from_id"] == me else c["from_id"]) for c in conns_all})
    pending_received = await db.ubuntoo2_connections.count_documents({"to_id": me, "status": "pending"})
    my_comms = await db.ubuntoo2_communities.find({"members": me}, {"_id": 0, "id": 1, "name": 1, "category": 1}).to_list(20)
    convs = await db.ubuntoo2_conversations.find({"participants": me}, {"_id": 0}).sort("last_message_at", -1).to_list(3)
    for c in convs:
        other = next((p for p in c["participants"] if p != me), None)
        op = await db.ubuntoo2_profiles.find_one({"token_id": other}, {"_id": 0, "display_name": 1})
        c["other_name"] = (op or {}).get("display_name", "Membre")
    posts_count = await db.ubuntoo2_posts.count_documents({"author_id": me})
    replies_count = await db.ubuntoo2_replies.count_documents({"author_id": me})
    unread_notifs = await db.ubuntoo2_notifications.count_documents({"token_id": me, "read": False})
    unread_msgs = 0
    my_conv_ids = [c["id"] for c in await db.ubuntoo2_conversations.find({"participants": me}, {"_id": 0, "id": 1}).to_list(100)]
    if my_conv_ids:
        unread_msgs = await db.ubuntoo2_messages.count_documents(
            {"conversation_id": {"$in": my_conv_ids}, "sender_id": {"$ne": me}, "read": False})
    recent_contacts = []
    seen_rc = set()
    recent_conns = await db.ubuntoo2_connections.find(
        {"status": "accepted", "$or": [{"from_id": me}, {"to_id": me}]}, {"_id": 0}).sort("responded_at", -1).to_list(10)
    for c in recent_conns:
        other = c["to_id"] if c["from_id"] == me else c["from_id"]
        if other in seen_rc or len(recent_contacts) >= 3:
            continue
        seen_rc.add(other)
        op = await db.ubuntoo2_profiles.find_one({"token_id": other}, {"_id": 0, "display_name": 1, "headline": 1, "token_id": 1})
        if op:
            recent_contacts.append(op)
    badges = await _compute_badges(me)
    mentoring_conns = await db.ubuntoo2_connections.find(
        {"kind": "mentorat", "status": "accepted", "$or": [{"from_id": me}, {"to_id": me}]}, {"_id": 0}).to_list(20)
    mentor_names, mentore_names = [], []
    for c in mentoring_conns:
        other = c.get("mentee_id") if c.get("mentor_id") == me else c.get("mentor_id")
        op = await db.ubuntoo2_profiles.find_one({"token_id": other}, {"_id": 0, "display_name": 1})
        if op:
            (mentore_names if c.get("mentor_id") == me else mentor_names).append(op["display_name"])
    return {
        "display_name": prof.get("display_name"),
        "contacts_count": contacts_count,
        "pending_requests": pending_received,
        "recent_contacts": recent_contacts,
        "communities": my_comms,
        "recent_conversations": convs,
        "contributions_count": posts_count + replies_count,
        "unread_notifications": unread_notifs,
        "unread_messages": unread_msgs,
        "badges": [b for b in badges if b["earned"]],
        "mentoring": {"role": prof.get("mentoring_role", "none"), "mentors": mentor_names, "mentores": mentore_names},
    }
