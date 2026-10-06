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

RECOGNITION_TYPES = {
    "partage_experience": "Partage d'expérience",
    "conseil": "Conseil",
    "information_metier": "Information métier",
    "mise_en_relation": "Mise en relation",
    "encouragement": "Encouragement",
    "partage_opportunite": "Partage d'opportunité",
}

BADGES = {
    # --- Premiers badges accessibles à tous (automatiques) ---
    "bienvenue": {
        "label": "Bienvenue UBUNTOO", "categorie": "premiers", "target": 1, "validation_humaine": False,
        "desc": "Marque votre entrée dans la communauté UBUNTOO.",
        "pourquoi": "Chaque parcours commence par un premier pas. Ce badge célèbre votre arrivée.",
        "comment": "Créer son profil et découvrir les principes de la communauté.",
        "actions": ["Accéder à UBUNTOO avec votre compte Ré'Actif Pro"],
        "valorise": "Votre entrée dans la communauté.",
        "etape_suivante": "Complétez votre profil professionnel pour faciliter les mises en relation."},
    "profil_pro": {
        "label": "Profil professionnel", "categorie": "premiers", "target": 1, "validation_humaine": False,
        "desc": "Votre profil contient les informations essentielles.",
        "pourquoi": "Un profil renseigné facilite les mises en relation pertinentes.",
        "comment": "Compléter les informations essentielles de son profil (projet, compétences ou disponibilité pour aider).",
        "actions": ["Renseigner votre projet professionnel", "Ajouter des compétences ou une disponibilité pour aider"],
        "valorise": "Votre identité professionnelle au sein du réseau.",
        "etape_suivante": "Participez à votre premier échange avec un membre ou une communauté."},
    "premier_echange": {
        "label": "Premier échange", "categorie": "premiers", "target": 1, "validation_humaine": False,
        "desc": "Vous êtes passé(e) de l'observation à la participation.",
        "pourquoi": "Encourager le premier pas vers les autres.",
        "comment": "Participer à son premier échange : publication, réponse, message ou mise en relation acceptée.",
        "actions": ["Publier dans une communauté", "Répondre à un membre", "Envoyer un message", "Accepter une mise en relation"],
        "valorise": "Votre passage à l'action dans la communauté.",
        "etape_suivante": "Découvrez différentes communautés avec le badge Explorateur."},
    "explorateur": {
        "label": "Explorateur", "categorie": "premiers", "target": 2, "validation_humaine": False,
        "desc": "Vous découvrez différentes communautés, métiers et expériences.",
        "pourquoi": "Valoriser la curiosité et l'ouverture professionnelle.",
        "comment": "Rejoindre au moins 2 communautés (métiers, situations, territoires ou thématiques).",
        "actions": ["Rejoindre des communautés", "Découvrir des métiers et des expériences"],
        "valorise": "Votre curiosité professionnelle.",
        "etape_suivante": "Choisissez une façon de contribuer : aider, partager, connecter ou animer."},
    # --- Badges de contribution ---
    "coup_de_pouce": {
        "label": "Coup de pouce", "categorie": "contribution", "target": 3, "validation_humaine": False,
        "desc": "Reconnaît une aide concrète apportée à un autre membre.",
        "pourquoi": "Reconnaître votre capacité à contribuer à la réussite des autres.",
        "comment": "Répondre utilement à une demande, partager une information pertinente ou aider quelqu'un dans une démarche. Les aides sont reconnues par les membres (bouton « Utile » ou reconnaissance directe).",
        "actions": ["Réponses marquées « Utile » par d'autres membres", "Reconnaissances « Conseil » ou « Information métier » reçues"],
        "valorise": "Votre entraide concrète.",
        "etape_suivante": "Avec le badge Bienveillant, vous complétez le Parcours entraide vers Contributeur."},
    "partageur_experience": {
        "label": "Partageur d'expérience", "categorie": "contribution", "target": 2, "validation_humaine": False,
        "desc": "Reconnaît le partage d'expériences utiles aux autres.",
        "pourquoi": "Votre vécu (reconversion, métier, formation, entretien, intégration) peut éclairer le chemin des autres.",
        "comment": "Publier des témoignages d'expérience dans les communautés, ou être reconnu(e) par des membres pour un partage d'expérience.",
        "actions": ["Publications de type « Expérience »", "Reconnaissances « Partage d'expérience » reçues"],
        "valorise": "La transmission de votre vécu professionnel.",
        "etape_suivante": "Avec Éclaireur métier, vous complétez le Parcours expérience vers Contributeur."},
    "eclaireur_metier": {
        "label": "Éclaireur métier", "categorie": "contribution", "target": 3, "validation_humaine": False,
        "desc": "Vous aidez les autres à mieux comprendre un métier.",
        "pourquoi": "Faire découvrir les réalités d'un métier ou d'un secteur aide les personnes en orientation ou en reconversion.",
        "comment": "Participer aux échanges dans les communautés métiers : présenter son métier, expliquer un secteur, détailler les compétences nécessaires.",
        "actions": ["Publications et réponses dans les communautés Métiers"],
        "valorise": "Votre connaissance de terrain des métiers.",
        "etape_suivante": "Avec Partageur d'expérience, vous complétez le Parcours expérience vers Contributeur."},
    "connecteur": {
        "label": "Connecteur", "categorie": "contribution", "target": 2, "validation_humaine": False,
        "desc": "Reconnaît la capacité à mettre utilement des personnes en relation.",
        "pourquoi": "« Je connais quelqu'un qui pourrait vous aider » : le réseau est une richesse qui se partage, toujours avec le consentement des personnes.",
        "comment": "Être reconnu(e) pour des mises en relation utiles, ou développer un réseau actif de contacts acceptés.",
        "actions": ["Reconnaissances « Mise en relation » reçues", "Mises en relation acceptées"],
        "valorise": "Votre rôle de facilitateur de rencontres professionnelles.",
        "etape_suivante": "Avec Partageur d'opportunités, vous complétez le Parcours réseau vers Contributeur."},
    "partageur_opportunites": {
        "label": "Partageur d'opportunités", "categorie": "contribution", "target": 3, "validation_humaine": False,
        "desc": "Reconnaît le partage d'opportunités professionnelles utiles.",
        "pourquoi": "Une offre, une formation, une immersion ou un événement partagé peut changer la trajectoire de quelqu'un.",
        "comment": "Publier des opportunités (emploi, formation, PMSMP, alternance, événement, job dating) dans les communautés.",
        "actions": ["Publications de type « Opportunité »", "Reconnaissances « Partage d'opportunité » reçues"],
        "valorise": "Votre contribution à l'accès à l'emploi des autres.",
        "etape_suivante": "Avec Connecteur, vous complétez le Parcours réseau vers Contributeur."},
    "bienveillant": {
        "label": "Bienveillant", "categorie": "contribution", "target": 3, "validation_humaine": False,
        "desc": "Reconnaît une attitude constructive et respectueuse dans les échanges.",
        "pourquoi": "La qualité des interactions compte plus que leur volume.",
        "comment": "Être reconnu(e) par d'autres membres pour vos encouragements et votre attitude constructive.",
        "actions": ["Reconnaissances « Encouragement » reçues de membres différents"],
        "valorise": "Votre contribution au climat d'entraide de la communauté.",
        "etape_suivante": "Avec Coup de pouce, vous complétez le Parcours entraide vers Contributeur."},
    "esprit_collectif": {
        "label": "Esprit collectif", "categorie": "contribution", "target": 5, "validation_humaine": False,
        "desc": "Reconnaît une participation régulière et constructive à une communauté.",
        "pourquoi": "Les communautés vivent grâce à ceux qui y participent dans la durée.",
        "comment": "Participer régulièrement à une même communauté (publications et réponses).",
        "actions": ["Participations (publications + réponses) dans une même communauté"],
        "valorise": "Votre engagement durable dans un collectif.",
        "etape_suivante": "Avec Premier échange, vous complétez le Parcours communauté vers Contributeur."},
    # --- Badge vérifié ---
    "passeport_pro": {
        "label": "Passeport professionnel", "categorie": "verifie", "target": 1, "validation_humaine": True,
        "desc": "Parcours ou compétences vérifiées via Ré'Actif Pro.",
        "pourquoi": "Relier votre engagement communautaire à votre identité professionnelle vérifiée.",
        "comment": "Déposer une preuve (diplôme, certificat, attestation) dans votre coffre-fort Ré'Actif Pro ou atteindre un passeport de compétences complet.",
        "actions": ["Preuve vérifiée déposée dans Ré'Actif Pro", "Passeport de compétences complété à 70 %"],
        "valorise": "La fiabilité de votre parcours documenté.",
        "etape_suivante": "Vos badges de contribution complètent ce socle vérifié — sans jamais se substituer à une certification de compétence."},
}

PARCOURS_CONTRIBUTEUR = {
    "entraide": {"label": "Parcours entraide", "desc": "Aider concrètement les autres membres", "badges": ["coup_de_pouce", "bienveillant"]},
    "experience": {"label": "Parcours expérience", "desc": "Transmettre son vécu et faire découvrir les métiers", "badges": ["partageur_experience", "eclaireur_metier"]},
    "reseau": {"label": "Parcours réseau", "desc": "Connecter les personnes et partager des opportunités", "badges": ["connecteur", "partageur_opportunites"]},
    "communaute": {"label": "Parcours communauté", "desc": "Faire vivre une communauté dans la durée", "badges": ["premier_echange", "esprit_collectif"]},
}

CHARTE_MENTOR = [
    "J'adopte une posture d'écoute, de bienveillance et de non-jugement.",
    "Je connais les limites de mon rôle : je partage mon expérience, je ne me substitue pas à un professionnel de l'accompagnement.",
    "Je m'engage à la non-discrimination et au respect de chaque personne.",
    "Je respecte la confidentialité des échanges avec mon mentoré.",
    "J'oriente vers un professionnel lorsque la situation dépasse mon rôle.",
]

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
    earned_badges = prof.get("badges_earned", [])
    displayed = prof.get("displayed_badges")
    public_badges = [b for b in earned_badges if (not isinstance(displayed, list)) or b in displayed]
    out = {"token_id": prof["token_id"], "display_name": prof.get("display_name", ""), "headline": "", "is_contact": is_contact,
           "mentoring_role": prof.get("mentoring_role", "none"), "badges": public_badges,
           "level": prof.get("level", "Membre"),
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
        mentor_prog = await db.ubuntoo2_progression.find_one({"token_id": conn["mentor_id"]}, {"_id": 0, "mentor_status": 1})
        if (mentor_prog or {}).get("mentor_status") not in ("mentor", "confirme"):
            raise HTTPException(status_code=403, detail="Le mentorat nécessite un Mentor UBUNTOO validé (charte acceptée et candidature approuvée).")
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
    validated_mentors = {p["token_id"] for p in await db.ubuntoo2_progression.find(
        {"mentor_status": {"$in": ["mentor", "confirme"]}}, {"_id": 0, "token_id": 1}).to_list(500)}
    for as_what, roles in target_roles:
        candidates = await db.ubuntoo2_profiles.find(
            {"token_id": {"$ne": me}, "mentoring_role": {"$in": roles}}, {"_id": 0}).to_list(100)
        for c in candidates:
            if c["token_id"] in seen:
                continue
            if as_what == "mentor" and c["token_id"] not in validated_mentors:
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
    relations = []
    for c in conns:
        my_role = "mentor" if c.get("mentor_id") == me else "mentee"
        other = c.get("mentee_id") if my_role == "mentor" else c.get("mentor_id")
        prof = await db.ubuntoo2_profiles.find_one({"token_id": other}, {"_id": 0})
        if prof:
            relations.append({
                "conn_id": c["id"], "my_role": my_role,
                "other": _filter_profile(prof, False, True),
                "objective": c.get("message", ""),
                "mentorat_status": c.get("mentorat_status", "actif"),
                "bilan": c.get("bilan", ""),
                "feedback_given": bool(c.get("feedback")) if my_role == "mentee" else None,
            })
    mentors = [r["other"] for r in relations if r["my_role"] == "mentee" and r["mentorat_status"] == "actif"]
    mentores = [r["other"] for r in relations if r["my_role"] == "mentor" and r["mentorat_status"] == "actif"]
    return {"mentors": mentors, "mentores": mentores, "relations": relations}


@router.post("/mentoring/relations/{conn_id}/terminate")
async def terminate_mentorat(conn_id: str, token: str, body: dict):
    token_doc = await get_current_token(token)
    me = token_doc["id"]
    conn = await db.ubuntoo2_connections.find_one({"id": conn_id, "kind": "mentorat", "status": "accepted",
                                                   "$or": [{"from_id": me}, {"to_id": me}]})
    if not conn:
        raise HTTPException(status_code=404, detail="Mentorat introuvable")
    if conn.get("mentorat_status") == "termine":
        raise HTTPException(status_code=400, detail="Ce mentorat est déjà clôturé.")
    bilan = (body.get("bilan") or "").strip()[:800]
    await db.ubuntoo2_connections.update_one(
        {"id": conn_id}, {"$set": {"mentorat_status": "termine", "bilan": bilan, "terminated_at": now_iso(), "terminated_by": me}})
    other = conn["to_id"] if conn["from_id"] == me else conn["from_id"]
    my_prof = await _get_or_create_profile(token_doc)
    await _notify(other, "mentorat_termine", f"{my_prof.get('display_name')} a clôturé votre mentorat avec un bilan.", "/ubuntoo/reseau?tab=mentorat")
    if conn.get("mentee_id") == other:
        await _notify(other, "mentorat_feedback", "Vous pouvez donner un retour confidentiel sur la qualité de l'accompagnement.", "/ubuntoo/reseau?tab=mentorat")
    return {"status": "termine"}


@router.post("/mentoring/relations/{conn_id}/feedback")
async def mentorat_feedback(conn_id: str, token: str, body: dict):
    token_doc = await get_current_token(token)
    me = token_doc["id"]
    conn = await db.ubuntoo2_connections.find_one({"id": conn_id, "kind": "mentorat", "mentee_id": me})
    if not conn:
        raise HTTPException(status_code=404, detail="Mentorat introuvable (retour réservé au mentoré)")
    if conn.get("feedback"):
        raise HTTPException(status_code=400, detail="Retour déjà transmis.")
    rating = body.get("rating")
    if not isinstance(rating, int) or not 1 <= rating <= 5:
        raise HTTPException(status_code=400, detail="Note entre 1 et 5 requise")
    await db.ubuntoo2_connections.update_one(
        {"id": conn_id},
        {"$set": {"feedback": {"rating": rating, "comment": (body.get("comment") or "")[:500], "created_at": now_iso()}}})
    return {"status": "ok", "message": "Merci, votre retour confidentiel a été enregistré."}


# ============== PARCOURS DE PROGRESSION (rôles de confiance) ==============

def _is_admin(token_doc: dict) -> bool:
    return token_doc.get("role") == "admin" or (token_doc.get("pseudo") or "").lower() in ("admin@reactifpro.fr", "rh@reactifpro.fr")


async def _get_prog(token_id: str) -> dict:
    return await db.ubuntoo2_progression.find_one({"token_id": token_id}, {"_id": 0}) or \
        {"token_id": token_id, "mentor_status": "none", "animateur": False, "ambassadeur_status": "none"}


async def _compute_progression(token_id: str) -> dict:
    prof = await db.ubuntoo2_profiles.find_one({"token_id": token_id}, {"_id": 0}) or {}
    prog = await _get_prog(token_id)
    posts = await db.ubuntoo2_posts.find({"author_id": token_id}, {"_id": 0, "type": 1, "utile_by": 1}).to_list(500)
    replies_count = await db.ubuntoo2_replies.count_documents({"author_id": token_id})
    my_comms_count = await db.ubuntoo2_communities.count_documents({"members": token_id})
    created_comms = await db.ubuntoo2_communities.count_documents({"created_by": token_id})
    accepted_conns = await db.ubuntoo2_connections.count_documents(
        {"status": "accepted", "$or": [{"from_id": token_id}, {"to_id": token_id}]})
    utiles_recus = sum(len(p.get("utile_by", [])) for p in posts)
    ressources = sum(1 for p in posts if p.get("type") in ("ressource", "information", "opportunite"))
    contributions = len(posts) + replies_count
    participations = contributions + my_comms_count + accepted_conns
    profil_complet = bool(prof.get("headline") or prof.get("projet")) and bool(prof.get("competences") or prof.get("help_offers"))

    membre_actif = participations >= 3
    badges = await _compute_badges(token_id)
    parcours = _parcours_state(badges)
    contributeur = any(p["complete"] for p in parcours) or (ressources + replies_count) >= 5 or utiles_recus >= 3

    mentorats_termines = await db.ubuntoo2_connections.count_documents(
        {"kind": "mentorat", "mentor_id": token_id, "mentorat_status": "termine"})
    mentorats_actifs = await db.ubuntoo2_connections.count_documents(
        {"kind": "mentorat", "mentor_id": token_id, "status": "accepted", "mentorat_status": {"$ne": "termine"}})
    fb = await db.ubuntoo2_connections.find(
        {"kind": "mentorat", "mentor_id": token_id, "feedback": {"$exists": True}}, {"_id": 0, "feedback": 1}).to_list(50)
    ratings = [f["feedback"]["rating"] for f in fb if f.get("feedback", {}).get("rating")]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else None

    mentor_status = prog.get("mentor_status", "none")
    if mentor_status == "mentor" and mentorats_termines >= 2 and ratings and avg_rating >= 4:
        mentor_status = "confirme"
        await db.ubuntoo2_progression.update_one({"token_id": token_id}, {"$set": {"token_id": token_id, "mentor_status": "confirme"}}, upsert=True)
        await _notify(token_id, "progression", "Vous êtes désormais Mentor confirmé UBUNTOO — merci pour la qualité de vos accompagnements. Vous pouvez accompagner les futurs mentors.", "/ubuntoo/profil")

    animateur = prog.get("animateur", False)
    animateur_eligible = contributeur and (created_comms >= 1 or (contributions >= 10 and my_comms_count >= 3))
    if animateur_eligible and not animateur:
        animateur = True
        await db.ubuntoo2_progression.update_one({"token_id": token_id}, {"$set": {"token_id": token_id, "animateur": True}}, upsert=True)
        await _notify(token_id, "progression", "Votre engagement dans l'animation de la communauté est reconnu : vous êtes Animateur UBUNTOO.", "/ubuntoo/profil")

    ambassadeur_status = prog.get("ambassadeur_status", "none")
    can_apply_ambassadeur = ambassadeur_status == "none" and (mentor_status == "confirme" or animateur)
    can_apply_mentor = mentor_status == "none" and contributeur and profil_complet

    if ambassadeur_status == "ambassadeur":
        current = "Ambassadeur UBUNTOO"
    elif mentor_status == "confirme":
        current = "Mentor confirmé"
    elif mentor_status == "mentor":
        current = "Mentor UBUNTOO"
    elif animateur:
        current = "Animateur"
    elif mentor_status == "candidat":
        current = "Mentor candidat"
    elif contributeur:
        current = "Contributeur"
    elif membre_actif:
        current = "Membre actif"
    else:
        current = "Membre"
    if prof.get("level") != current:
        await db.ubuntoo2_profiles.update_one({"token_id": token_id}, {"$set": {"level": current}})

    next_steps = []
    if not profil_complet:
        next_steps.append("Complétez votre profil (projet, compétences ou disponibilité pour aider).")
    if not membre_actif:
        next_steps.append("Participez : rejoignez une communauté, échangez, posez une question.")
    elif not contributeur:
        next_steps.append("Apportez des contributions utiles : expérience, ressource, opportunité ou réponse à un membre.")
    if can_apply_mentor:
        next_steps.append("Devenez Mentor candidat : acceptez la charte du mentor et proposez un accompagnement.")
    elif contributeur and mentor_status == "none" and not profil_complet:
        next_steps.append("Niveau Contributeur atteint : complétez votre profil pour pouvoir candidater comme Mentor.")
    if mentor_status == "candidat":
        next_steps.append("Votre candidature mentor est en cours d'examen par l'équipe UBUNTOO.")
    if mentor_status == "mentor":
        next_steps.append(f"Menez des mentorats à leur terme avec des retours positifs pour devenir Mentor confirmé ({mentorats_termines}/2 terminés).")
    if contributeur and not animateur:
        next_steps.append("Branche Animateur : créez ou animez une communauté, accueillez les nouveaux membres.")
    if can_apply_ambassadeur:
        next_steps.append("Vous pouvez candidater comme Ambassadeur UBUNTOO (validation par l'équipe).")
    if ambassadeur_status == "candidat":
        next_steps.append("Votre candidature Ambassadeur est en cours d'examen.")

    return {
        "current_label": current,
        "levels": {
            "membre": True, "membre_actif": membre_actif, "contributeur": contributeur,
            "mentor_candidat": mentor_status in ("candidat", "mentor", "confirme"),
            "mentor": mentor_status in ("mentor", "confirme"),
            "mentor_confirme": mentor_status == "confirme",
            "animateur": animateur,
            "ambassadeur": ambassadeur_status == "ambassadeur",
        },
        "mentor_status": mentor_status,
        "ambassadeur_status": ambassadeur_status,
        "ambassadeur_mandat_end": prog.get("ambassadeur_mandat_end"),
        "can_apply_mentor": can_apply_mentor,
        "can_apply_ambassadeur": can_apply_ambassadeur,
        "charte": CHARTE_MENTOR,
        "contributions": {
            "publications": len(posts), "reponses": replies_count, "utiles_recus": utiles_recus,
            "ressources_partagees": ressources, "communautes": my_comms_count, "communautes_creees": created_comms,
            "mentorats_actifs": mentorats_actifs, "mentorats_termines": mentorats_termines,
            "note_moyenne_mentorat": avg_rating,
        },
        "next_steps": next_steps[:4],
        "badges": badges,
        "parcours": parcours,
    }


@router.get("/progression")
async def get_progression(token: str):
    token_doc = await get_current_token(token)
    return await _compute_progression(token_doc["id"])


@router.post("/progression/mentor-candidature")
async def apply_mentor(token: str, body: dict):
    token_doc = await get_current_token(token)
    if not body.get("accept_charte"):
        raise HTTPException(status_code=400, detail="Vous devez accepter la charte du mentor UBUNTOO.")
    prog_data = await _compute_progression(token_doc["id"])
    if not prog_data["can_apply_mentor"]:
        raise HTTPException(status_code=400, detail="Prérequis : niveau Contributeur atteint et profil renseigné.")
    await db.ubuntoo2_progression.update_one(
        {"token_id": token_doc["id"]},
        {"$set": {"token_id": token_doc["id"], "mentor_status": "candidat", "charte_accepted_at": now_iso()}}, upsert=True)
    prof = await _get_or_create_profile(token_doc)
    await db.ubuntoo2_candidatures.insert_one({
        "id": str(uuid.uuid4()), "token_id": token_doc["id"], "display_name": prof.get("display_name"),
        "type": "mentor", "motivation": (body.get("motivation") or "")[:500],
        "status": "pending", "created_at": now_iso()})
    return {"status": "candidat", "message": "Candidature mentor enregistrée. Elle sera examinée par l'équipe UBUNTOO."}


@router.post("/progression/ambassadeur-candidature")
async def apply_ambassadeur(token: str, body: dict):
    token_doc = await get_current_token(token)
    prog_data = await _compute_progression(token_doc["id"])
    if not prog_data["can_apply_ambassadeur"]:
        raise HTTPException(status_code=400, detail="Prérequis : être Mentor confirmé ou Animateur.")
    await db.ubuntoo2_progression.update_one(
        {"token_id": token_doc["id"]}, {"$set": {"token_id": token_doc["id"], "ambassadeur_status": "candidat"}}, upsert=True)
    prof = await _get_or_create_profile(token_doc)
    await db.ubuntoo2_candidatures.insert_one({
        "id": str(uuid.uuid4()), "token_id": token_doc["id"], "display_name": prof.get("display_name"),
        "type": "ambassadeur", "motivation": (body.get("motivation") or "")[:500],
        "status": "pending", "created_at": now_iso()})
    return {"status": "candidat", "message": "Candidature Ambassadeur transmise pour validation humaine."}


@router.get("/admin/candidatures")
async def list_candidatures(token: str):
    token_doc = await get_current_token(token)
    if not _is_admin(token_doc):
        raise HTTPException(status_code=403, detail="Réservé à l'équipe UBUNTOO")
    return await db.ubuntoo2_candidatures.find({"status": "pending"}, {"_id": 0}).sort("created_at", 1).to_list(100)


@router.post("/admin/candidatures/{cand_id}/decide")
async def decide_candidature(cand_id: str, token: str, body: dict):
    token_doc = await get_current_token(token)
    if not _is_admin(token_doc):
        raise HTTPException(status_code=403, detail="Réservé à l'équipe UBUNTOO")
    action = body.get("action")
    if action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="Action invalide")
    cand = await db.ubuntoo2_candidatures.find_one({"id": cand_id, "status": "pending"})
    if not cand:
        raise HTTPException(status_code=404, detail="Candidature introuvable")
    await db.ubuntoo2_candidatures.update_one(
        {"id": cand_id}, {"$set": {"status": "approved" if action == "approve" else "rejected", "decided_at": now_iso(), "decided_by": token_doc["id"]}})
    uid = cand["token_id"]
    if cand["type"] == "mentor":
        if action == "approve":
            await db.ubuntoo2_progression.update_one({"token_id": uid}, {"$set": {"mentor_status": "mentor"}}, upsert=True)
            await _notify(uid, "progression", "Félicitations : votre candidature est validée, vous êtes Mentor UBUNTOO. Vous pouvez désormais accompagner des membres.", "/ubuntoo/reseau?tab=mentorat")
        else:
            await db.ubuntoo2_progression.update_one({"token_id": uid}, {"$set": {"mentor_status": "none"}}, upsert=True)
            await _notify(uid, "progression", "Votre candidature mentor n'a pas été retenue pour le moment. Continuez à contribuer, vous pourrez candidater à nouveau.", "/ubuntoo/profil")
    else:
        if action == "approve":
            from datetime import timedelta
            mandat_end = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
            await db.ubuntoo2_progression.update_one(
                {"token_id": uid}, {"$set": {"ambassadeur_status": "ambassadeur", "ambassadeur_mandat_end": mandat_end}}, upsert=True)
            await _notify(uid, "progression", "La communauté vous accorde sa confiance : vous êtes Ambassadeur UBUNTOO pour un mandat de 12 mois.", "/ubuntoo/profil")
        else:
            await db.ubuntoo2_progression.update_one({"token_id": uid}, {"$set": {"ambassadeur_status": "none"}}, upsert=True)
            await _notify(uid, "progression", "Votre candidature Ambassadeur n'a pas été retenue pour le moment.", "/ubuntoo/profil")
    return {"status": "ok"}


# ============== BADGES ==============

async def _compute_badges(token_id: str) -> list:
    prof = await db.ubuntoo2_profiles.find_one({"token_id": token_id}, {"_id": 0}) or {}
    posts = await db.ubuntoo2_posts.find({"author_id": token_id}, {"_id": 0, "type": 1, "community_id": 1, "utile_by": 1}).to_list(500)
    my_replies = await db.ubuntoo2_replies.find({"author_id": token_id}, {"_id": 0, "post_id": 1, "utile_by": 1}).to_list(1000)
    replies_count = len(my_replies)
    my_comms = await db.ubuntoo2_communities.find({"members": token_id}, {"_id": 0, "id": 1, "category": 1}).to_list(100)
    accepted_conns = await db.ubuntoo2_connections.count_documents(
        {"status": "accepted", "$or": [{"from_id": token_id}, {"to_id": token_id}]})
    msgs_sent = await db.ubuntoo2_messages.count_documents({"sender_id": token_id})
    profil_complet = bool(prof.get("headline") or prof.get("projet")) and bool(prof.get("competences") or prof.get("help_offers"))

    # Reconnaissances reçues par type (confirmées par d'autres membres)
    reco = {}
    async for r in db.ubuntoo2_recognitions.aggregate([
            {"$match": {"to_id": token_id}},
            {"$group": {"_id": "$type", "n": {"$sum": 1}}}]):
        reco[r["_id"]] = r["n"]

    utiles_sur_reponses = sum(len(r.get("utile_by", [])) for r in my_replies)

    all_metier_ids = {c["id"] for c in await db.ubuntoo2_communities.find({"category": "metiers"}, {"_id": 0, "id": 1}).to_list(100)}
    metier_posts = sum(1 for p in posts if p.get("community_id") in all_metier_ids)
    metier_replies = 0
    if all_metier_ids and my_replies:
        metier_post_ids = {p["id"] for p in await db.ubuntoo2_posts.find(
            {"community_id": {"$in": list(all_metier_ids)}}, {"_id": 0, "id": 1}).to_list(2000)}
        metier_replies = sum(1 for r in my_replies if r.get("post_id") in metier_post_ids)

    # Participations par communauté (esprit collectif = régularité dans UNE communauté)
    per_comm = {}
    for p in posts:
        per_comm[p.get("community_id")] = per_comm.get(p.get("community_id"), 0) + 1
    if my_replies:
        reply_post_ids = list({r["post_id"] for r in my_replies})
        posts_of_replies = await db.ubuntoo2_posts.find({"id": {"$in": reply_post_ids}}, {"_id": 0, "id": 1, "community_id": 1}).to_list(2000)
        post_comm = {p["id"]: p.get("community_id") for p in posts_of_replies}
        for r in my_replies:
            cid = post_comm.get(r["post_id"])
            if cid:
                per_comm[cid] = per_comm.get(cid, 0) + 1
    max_comm_participations = max(per_comm.values()) if per_comm else 0

    exp_posts = sum(1 for p in posts if p.get("type") == "experience")
    oppo_posts = sum(1 for p in posts if p.get("type") == "opportunite")

    has_proof = await db["proof_documents.files"].count_documents({"metadata.token_id": token_id}) > 0
    passport = await db.passports.find_one({"token_id": token_id}, {"_id": 0, "completeness_score": 1})
    passeport_ok = has_proof or (passport or {}).get("completeness_score", 0) >= 70

    progress = {
        "bienvenue": 1,
        "profil_pro": 1 if profil_complet else 0,
        "premier_echange": min(1, len(posts) + replies_count + msgs_sent + accepted_conns),
        "explorateur": len(my_comms),
        "coup_de_pouce": utiles_sur_reponses + reco.get("conseil", 0) + reco.get("information_metier", 0),
        "partageur_experience": max(exp_posts, reco.get("partage_experience", 0)),
        "eclaireur_metier": metier_posts + metier_replies,
        "connecteur": max(reco.get("mise_en_relation", 0), accepted_conns // 3),
        "partageur_opportunites": max(oppo_posts, reco.get("partage_opportunite", 0)),
        "bienveillant": reco.get("encouragement", 0),
        "esprit_collectif": max_comm_participations,
        "passeport_pro": 1 if passeport_ok else 0,
    }

    existing = await db.ubuntoo2_badges.find_one({"token_id": token_id}, {"_id": 0}) or {"token_id": token_id, "earned": {}}
    newly = []
    for bid, meta in BADGES.items():
        if progress.get(bid, 0) >= meta["target"] and bid not in existing["earned"]:
            existing["earned"][bid] = now_iso()
            newly.append(bid)
    if newly:
        await db.ubuntoo2_badges.update_one({"token_id": token_id}, {"$set": {"earned": existing["earned"]}}, upsert=True)
        await db.ubuntoo2_profiles.update_one({"token_id": token_id}, {"$set": {"badges_earned": list(existing["earned"].keys())}})
        for bid in newly:
            await _notify(token_id, "badge", f"Badge obtenu : « {BADGES[bid]['label']} » — {BADGES[bid]['desc']}", "/ubuntoo/profil")

    displayed = prof.get("displayed_badges")
    return [{
        "id": bid, **BADGES[bid],
        "earned": bid in existing["earned"],
        "earned_at": existing["earned"].get(bid),
        "progress": {"current": min(progress.get(bid, 0), BADGES[bid]["target"]), "target": BADGES[bid]["target"]},
        "displayed": (bid in displayed) if isinstance(displayed, list) else True,
    } for bid in BADGES]


def _parcours_state(badges: list) -> list:
    earned_ids = {b["id"] for b in badges if b["earned"]}
    by_id = {b["id"]: b for b in badges}
    out = []
    for pid, p in PARCOURS_CONTRIBUTEUR.items():
        steps = [{"id": bid, "label": by_id[bid]["label"], "earned": bid in earned_ids,
                  "progress": by_id[bid]["progress"]} for bid in p["badges"]]
        out.append({"id": pid, "label": p["label"], "desc": p["desc"], "badges": steps,
                    "complete": all(s["earned"] for s in steps)})
    return out


@router.get("/badges")
async def get_badges(token: str):
    token_doc = await get_current_token(token)
    badges = await _compute_badges(token_doc["id"])
    return {"badges": badges, "parcours": _parcours_state(badges),
            "recognition_types": RECOGNITION_TYPES}


@router.put("/badges/display")
async def set_badge_display(token: str, body: dict):
    token_doc = await get_current_token(token)
    badge_id = body.get("badge_id")
    if badge_id not in BADGES:
        raise HTTPException(status_code=400, detail="Badge inconnu")
    prof = await _get_or_create_profile(token_doc)
    displayed = prof.get("displayed_badges")
    if not isinstance(displayed, list):
        doc = await db.ubuntoo2_badges.find_one({"token_id": token_doc["id"]}, {"_id": 0}) or {"earned": {}}
        displayed = list(doc.get("earned", {}).keys())
    if body.get("displayed"):
        if badge_id not in displayed:
            displayed.append(badge_id)
    else:
        displayed = [b for b in displayed if b != badge_id]
    await db.ubuntoo2_profiles.update_one({"token_id": token_doc["id"]}, {"$set": {"displayed_badges": displayed}})
    return {"displayed_badges": displayed}


@router.post("/recognitions")
async def give_recognition(token: str, body: dict):
    token_doc = await get_current_token(token)
    me = token_doc["id"]
    to_id = body.get("to_id")
    rtype = body.get("type")
    if rtype not in RECOGNITION_TYPES:
        raise HTTPException(status_code=400, detail="Type de reconnaissance invalide")
    if not to_id or to_id == me:
        raise HTTPException(status_code=400, detail="Destinataire invalide")
    target = await db.ubuntoo2_profiles.find_one({"token_id": to_id}, {"_id": 0, "display_name": 1})
    if not target:
        raise HTTPException(status_code=404, detail="Membre introuvable")
    existing = await db.ubuntoo2_recognitions.find_one({"from_id": me, "to_id": to_id, "type": rtype})
    if existing:
        raise HTTPException(status_code=400, detail="Vous avez déjà reconnu cette contribution pour ce membre.")
    await db.ubuntoo2_recognitions.insert_one({
        "id": str(uuid.uuid4()), "from_id": me, "to_id": to_id, "type": rtype, "created_at": now_iso()})
    my_prof = await _get_or_create_profile(token_doc)
    await _notify(to_id, "reconnaissance",
                  f"{my_prof.get('display_name')} a reconnu votre contribution : « {RECOGNITION_TYPES[rtype]} ». Merci pour votre aide !",
                  "/ubuntoo/profil")
    await _compute_badges(to_id)
    return {"status": "ok", "message": f"Contribution « {RECOGNITION_TYPES[rtype]} » reconnue."}


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
    badges_prog = await _compute_progression(me)
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
        "badges": [b for b in badges_prog["badges"] if b["earned"] and b["displayed"]],
        "progression": {"current_label": badges_prog["current_label"], "next_steps": badges_prog["next_steps"][:3],
                        "parcours": badges_prog["parcours"]},
        "mentoring": {"role": prof.get("mentoring_role", "none"), "mentors": mentor_names, "mentores": mentore_names},
    }
