"""UBUNTOO — Parcours d'évolution des membres (badges de niveaux).

Explorateur → Contributeur → Ambassadeur → Expert → Mentor → Leader Communautaire → Pionnier Ubuntoo
Progression évaluée sur 4 dimensions : Contribution, Expertise, Engagement, Impact humain.
"""
from fastapi import APIRouter, Depends
from datetime import datetime, timezone

from database import db
from routes.ubuntoo_social import get_current_user, award_badge, BADGES

router = APIRouter(prefix="/api/social")

# ============== SYSTÈME DE BADGES UBUNTOO (2 pistes + ICU) ==============

PROOF_TIERS = [
    {"threshold": 1, "id": "proof_1", "name": "Premier pas", "icon": "👣"},
    {"threshold": 5, "id": "proof_5", "name": "Constructeur de preuves", "icon": "🧱"},
    {"threshold": 10, "id": "proof_10", "name": "Professionnel documenté", "icon": "📁"},
    {"threshold": 25, "id": "proof_25", "name": "Expert documenté", "icon": "📜"},
    {"threshold": 50, "id": "proof_50", "name": "Référent de confiance", "icon": "🛡️"},
]

EXTRA_BADGES = [
    {"id": "skills_demonstrated", "name": "Compétences démontrées", "description": "Preuves issues de plusieurs origines différentes", "icon": "🎯"},
    {"id": "skill_verified", "name": "Compétence vérifiée", "description": "Preuve confirmée par un tiers qualifié", "icon": "✅"},
    {"id": "level_ambassadeur", "name": "Ambassadeur", "description": "Moteur de la communauté", "icon": "📣"},
    {"id": "level_mentor", "name": "Mentor", "description": "Accompagne les autres membres", "icon": "🎓"},
    {"id": "level_leader", "name": "Leader Communautaire", "description": "Contribue au développement d'Ubuntoo", "icon": "👑"},
    {"id": "level_pionnier", "name": "Pionnier Ubuntoo", "description": "Badge ultime attribué par le comité", "icon": "💎"},
]

BADGE_REGISTRY = {b["id"]: b for b in BADGES}
BADGE_REGISTRY.update({t["id"]: {"id": t["id"], "name": t["name"], "description": f"{t['threshold']} preuve{'s' if t['threshold'] > 1 else ''} validée{'s' if t['threshold'] > 1 else ''}", "icon": t["icon"]} for t in PROOF_TIERS})
BADGE_REGISTRY.update({b["id"]: b for b in EXTRA_BADGES})

FAMILIES = [
    {"id": "engagement", "name": "Engagement", "desc": "Participation, régularité, ancienneté", "icon": "🌱", "badges": ["welcome", "first_post", "voice_heard", "one_month", "weaver"]},
    {"id": "expertise", "name": "Expertise", "desc": "Compétences techniques, métiers, certifications", "icon": "🧠", "badges": ["proof_1", "proof_5", "proof_10", "proof_25", "proof_50", "skills_demonstrated", "skill_verified"]},
    {"id": "solidarite", "name": "Solidarité", "desc": "Aide apportée, mentorat, coopération", "icon": "🤝", "badges": ["helping_hand", "good_listener", "connection_made"]},
    {"id": "innovation", "name": "Innovation", "desc": "Idées, projets, publications, recherche", "icon": "💡", "badges": ["knowledge_sharer", "facilitator"]},
    {"id": "leadership", "name": "Leadership", "desc": "Animation, gouvernance, développement de communautés", "icon": "👑", "badges": ["builder", "level_ambassadeur", "level_mentor", "level_leader", "level_pionnier"]},
]

LEVELS = [
    {
        "id": "explorateur", "name": "Explorateur", "icon": "compass",
        "tagline": "Découverte de la communauté",
        "unlocks": ["Accès aux groupes publics", "Participation aux discussions", "Création du premier réseau"],
    },
    {
        "id": "contributeur", "name": "Contributeur", "icon": "sprout",
        "tagline": "Le membre commence à apporter de la valeur",
        "unlocks": ["Création de groupes", "Publication d'articles", "Badge visible sur le profil"],
    },
    {
        "id": "ambassadeur", "name": "Ambassadeur", "icon": "megaphone",
        "tagline": "Le membre devient moteur de la communauté",
        "unlocks": ["Animation d'événements", "Validation de certaines publications", "Visibilité renforcée dans les recherches"],
    },
    {
        "id": "expert", "name": "Expert", "icon": "award",
        "tagline": "Le membre est reconnu pour son expertise métier",
        "unlocks": ["Badge premium", "Priorité dans les recommandations", "Réponse aux appels d'expertise", "Accès aux espaces professionnels"],
    },
    {
        "id": "mentor", "name": "Mentor", "icon": "graduation-cap",
        "tagline": "Le membre accompagne les autres",
        "unlocks": ["Programme officiel de mentorat", "Mise en avant sur la plateforme", "Validation des compétences comportementales"],
    },
    {
        "id": "leader", "name": "Leader Communautaire", "icon": "crown",
        "tagline": "Le membre contribue au développement d'Ubuntoo",
        "unlocks": ["Accès aux espaces de gouvernance", "Participation aux groupes de réflexion", "Création de communautés thématiques"],
    },
    {
        "id": "pionnier", "name": "Pionnier Ubuntoo", "icon": "gem",
        "tagline": "Badge ultime — attribué par le comité ALT&ACT + communauté selon l'impact",
        "unlocks": ["Reconnaissance suprême de la communauté", "Participation à l'évolution d'Ubuntoo", "Incarnation des valeurs de solidarité, d'inclusion et de coopération"],
    },
]

PROFILE_FIELDS = ["bio", "location", "sector", "skills", "jobs_sought", "availability", "languages"]


async def compute_stats(user: dict) -> dict:
    uid = user["id"]
    filled = sum(1 for f in PROFILE_FIELDS if user.get(f))
    posts = await db.ubuntoo_posts.find({"author_id": uid}, {"_id": 0, "likes": 1, "reactions": 1, "post_type": 1}).to_list(500)
    comments_count = await db.ubuntoo_comments.count_documents({"author_id": uid})
    replies_count = await db.ubuntoo_replies.count_documents({"author_id": uid})
    discussions_count = await db.ubuntoo_discussions.count_documents({"author_id": uid})
    groups_created = await db.ubuntoo_groups.find({"creator_id": uid}, {"_id": 0, "members": 1}).to_list(100)
    groups_joined = await db.ubuntoo_groups.count_documents({"members": uid})
    receivers = await db.ubuntoo_messages.distinct("receiver_id", {"sender_id": uid})
    messages_sent = await db.ubuntoo_messages.count_documents({"sender_id": uid})

    resources = sum(1 for p in posts if p.get("post_type") == "resource")
    recognitions = sum(len(p.get("likes", [])) + sum(len(v) for v in p.get("reactions", {}).values()) for p in posts)
    try:
        created = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
        days_member = max(0, (datetime.now(timezone.utc) - created).days)
    except Exception:
        days_member = 0

    return {
        "profile_completion": round(filled / len(PROFILE_FIELDS) * 100),
        "has_bio": bool(user.get("bio", "").strip()),
        "charter_accepted": bool(user.get("charter_accepted")),
        "posts_count": len(posts),
        "comments_count": comments_count,
        "replies_count": replies_count,
        "discussions_count": discussions_count,
        "resources_count": resources,
        "groups_created": len(groups_created),
        "groups_joined": groups_joined,
        "max_group_members": max((len(g.get("members", [])) for g in groups_created), default=0),
        "distinct_receivers": len(receivers),
        "messages_sent": messages_sent,
        "recognitions": recognitions,
        "skills_count": len(user.get("skills", [])),
        "days_member": days_member,
    }


def build_criteria(s: dict, is_pioneer: bool) -> dict:
    """Critères par niveau, chacun avec libellé + état."""
    return {
        "explorateur": [
            {"label": "Profil complété à plus de 70 %", "met": s["profile_completion"] >= 70, "detail": f"{s['profile_completion']} %"},
            {"label": "Acceptation de la charte éthique", "met": s["charter_accepted"]},
            {"label": "Présentation personnelle (bio)", "met": s["has_bio"]},
        ],
        "contributeur": [
            {"label": "Participation régulière (5 publications ou commentaires)", "met": s["posts_count"] + s["comments_count"] >= 5, "detail": f"{s['posts_count'] + s['comments_count']}/5"},
            {"label": "Réponses utiles (3 commentaires ou réponses)", "met": s["comments_count"] + s["replies_count"] >= 3, "detail": f"{s['comments_count'] + s['replies_count']}/3"},
            {"label": "Premier partage de ressource", "met": s["resources_count"] >= 1, "detail": f"{s['resources_count']}/1"},
            {"label": "Participation à un groupe ou événement", "met": s["groups_joined"] >= 1, "detail": f"{s['groups_joined']}/1"},
        ],
        "ambassadeur": [
            {"label": "Mentorat (5 messages d'accompagnement)", "met": s["messages_sent"] >= 5, "detail": f"{s['messages_sent']}/5"},
            {"label": "Recommandations positives (5 réactions reçues)", "met": s["recognitions"] >= 5, "detail": f"{s['recognitions']}/5"},
            {"label": "Animation d'un groupe", "met": s["groups_created"] >= 1, "detail": f"{s['groups_created']}/1"},
            {"label": "Contributions reconnues (10 reconnaissances)", "met": s["recognitions"] >= 10, "detail": f"{s['recognitions']}/10"},
        ],
        "expert": [
            {"label": "Compétences renseignées ou certifiées (3 min.)", "met": s["skills_count"] >= 3, "detail": f"{s['skills_count']}/3"},
            {"label": "Publications de qualité (10 publications)", "met": s["posts_count"] >= 10, "detail": f"{s['posts_count']}/10"},
            {"label": "Interventions (3 discussions lancées)", "met": s["discussions_count"] >= 3, "detail": f"{s['discussions_count']}/3"},
            {"label": "Évaluations positives de la communauté (20)", "met": s["recognitions"] >= 20, "detail": f"{s['recognitions']}/20"},
        ],
        "mentor": [
            {"label": "Accompagnement de plusieurs membres (3 min.)", "met": s["distinct_receivers"] >= 3, "detail": f"{s['distinct_receivers']}/3"},
            {"label": "Évaluations positives (30 reconnaissances)", "met": s["recognitions"] >= 30, "detail": f"{s['recognitions']}/30"},
            {"label": "Respect de la charte", "met": s["charter_accepted"]},
            {"label": "Participation à des jurys ou validations (10 réponses)", "met": s["replies_count"] >= 10, "detail": f"{s['replies_count']}/10"},
        ],
        "leader": [
            {"label": "Animation durable (90 jours d'ancienneté)", "met": s["days_member"] >= 90, "detail": f"{s['days_member']}/90 j"},
            {"label": "Développement d'une communauté (groupe de 10 membres)", "met": s["max_group_members"] >= 10, "detail": f"{s['max_group_members']}/10"},
            {"label": "Organisation de projets collaboratifs (3 groupes créés)", "met": s["groups_created"] >= 3, "detail": f"{s['groups_created']}/3"},
            {"label": "Forte réputation (50 reconnaissances)", "met": s["recognitions"] >= 50, "detail": f"{s['recognitions']}/50"},
        ],
        "pionnier": [
            {"label": "Engagement exceptionnel démontré", "met": is_pioneer},
            {"label": "A aidé un grand nombre de personnes", "met": is_pioneer},
            {"label": "Contribue activement à l'évolution d'Ubuntoo", "met": is_pioneer},
            {"label": "Incarne les valeurs de solidarité, d'inclusion et de coopération", "met": is_pioneer},
        ],
    }


def compute_dimensions(s: dict) -> dict:
    return {
        "contribution": min(100, s["posts_count"] * 8 + s["comments_count"] * 4 + s["resources_count"] * 15),
        "expertise": min(100, s["skills_count"] * 15 + s["discussions_count"] * 10 + s["resources_count"] * 10),
        "engagement": min(100, s["days_member"] + s["groups_joined"] * 10 + s["replies_count"] * 5),
        "impact": min(100, s["recognitions"] * 4 + s["distinct_receivers"] * 12),
    }


async def compute_proofs(uid: str) -> dict:
    """Piste 1 — preuves issues de RE'ACTIF PRO (portefeuille de compétences)."""
    illus_count = await db.skill_illustrations.count_documents({"token_id": uid})
    passport = await db.passports.find_one({"token_id": uid}, {"_id": 0, "experiences": 1})
    exps = (passport or {}).get("experiences", []) or []
    certified = sum(1 for e in exps if e.get("is_certified"))
    with_contract = sum(1 for e in exps if e.get("proof_document"))
    coffre_agg = await db.coffre_documents.aggregate([
        {"$match": {"token_id": uid}},
        {"$group": {"_id": "$category", "c": {"$sum": 1}}},
    ]).to_list(20)
    coffre = {c["_id"]: c["c"] for c in coffre_agg}
    diplomes = coffre.get("diplome", 0)
    exp_prouvee = coffre.get("experience_prouvee", 0)
    contrats = coffre.get("contrat_travail", 0)

    proof_count = illus_count + diplomes + exp_prouvee + contrats
    origins = [
        {"id": "experience_pro", "label": "Expérience professionnelle", "count": illus_count + exp_prouvee},
        {"id": "formation", "label": "Formation / Diplôme", "count": diplomes},
        {"id": "certification", "label": "Certification", "count": certified},
        {"id": "evaluation_terrain", "label": "Évaluation terrain (PMSMP)", "count": with_contract},
        {"id": "projet_perso", "label": "Projet personnel", "count": 0},
        {"id": "benevolat", "label": "Bénévolat", "count": 0},
    ]
    origins_met = sum(1 for o in origins if o["count"] > 0)
    verified_count = with_contract + certified
    return {
        "count": proof_count,
        "origins": origins,
        "origins_met": origins_met,
        "verified_count": verified_count,
        "certified_count": certified,
    }


def compute_icu(s: dict, p: dict) -> dict:
    """Indice de Contribution Ubuntoo — score vivant sur 5 dimensions."""
    icu = {
        "competence": min(100, p["count"] * 4 + p["origins_met"] * 8 + (20 if p["verified_count"] > 0 else 0)),
        "fiabilite": min(100, (25 if s["charter_accepted"] else 0) + p["verified_count"] * 15 + min(25, s["days_member"])),
        "collaboration": min(100, s["recognitions"] * 3 + s["comments_count"] * 3 + s["distinct_receivers"] * 10),
        "impact": min(100, p["certified_count"] * 15 + s["recognitions"] * 2 + s["resources_count"] * 8),
        "engagement": min(100, s["posts_count"] * 5 + s["groups_joined"] * 10 + min(30, s["days_member"]) + s["replies_count"] * 4),
    }
    icu["global"] = round(sum(icu.values()) / 5)
    return icu


def build_proof_track(p: dict) -> dict:
    tiers = [{**t, "earned": p["count"] >= t["threshold"]} for t in PROOF_TIERS]
    next_tier = next((t for t in tiers if not t["earned"]), None)
    return {
        "count": p["count"],
        "tiers": tiers,
        "next_tier": next_tier,
        "origins": p["origins"],
        "diversity_earned": p["origins_met"] >= 2,
        "verified_earned": p["verified_count"] > 0,
    }


def build_families(earned_ids: set) -> list:
    return [
        {**{k: f[k] for k in ("id", "name", "desc", "icon")},
         "badges": [{**BADGE_REGISTRY[bid], "earned": bid in earned_ids} for bid in f["badges"] if bid in BADGE_REGISTRY]}
        for f in FAMILIES
    ]


@router.get("/progression")
async def get_progression(current_user: dict = Depends(get_current_user)):
    stats = await compute_stats(current_user)
    proofs = await compute_proofs(current_user["id"])
    is_pioneer = bool(current_user.get("is_pioneer"))
    criteria = build_criteria(stats, is_pioneer)

    achieved_index = -1
    levels = []
    for i, lvl in enumerate(LEVELS):
        crits = criteria[lvl["id"]]
        if lvl["id"] == "pionnier":
            achieved = is_pioneer
        else:
            achieved = all(c["met"] for c in crits) and achieved_index == i - 1
        if achieved:
            achieved_index = i
        levels.append({**lvl, "index": i, "achieved": achieved, "criteria": crits})

    current_index = max(achieved_index, 0)
    stored = current_user.get("level_index", -1)
    level_up = achieved_index > stored and achieved_index >= 0
    if achieved_index != stored:
        await db.ubuntoo_users.update_one({"id": current_user["id"]}, {"$set": {"level_index": achieved_index}})
        if achieved_index >= 0:
            await award_badge(current_user["id"], f"level_{LEVELS[achieved_index]['id']}")

    for lvl in levels:
        lvl["current"] = lvl["index"] == current_index and achieved_index >= 0

    # Piste 1 : attribution persistante des badges de preuves
    proof_track = build_proof_track(proofs)
    new_proof_badges = [t["id"] for t in proof_track["tiers"] if t["earned"]]
    if proof_track["diversity_earned"]:
        new_proof_badges.append("skills_demonstrated")
    if proof_track["verified_earned"]:
        new_proof_badges.append("skill_verified")
    to_award = [b for b in new_proof_badges if b not in current_user.get("badges", [])]
    if to_award:
        await db.ubuntoo_users.update_one({"id": current_user["id"]}, {"$addToSet": {"badges": {"$each": to_award}}})

    earned_ids = set(current_user.get("badges", [])) | set(new_proof_badges)
    if achieved_index >= 0:
        earned_ids |= {f"level_{LEVELS[j]['id']}" for j in range(achieved_index + 1)}

    next_level = levels[achieved_index + 1] if achieved_index + 1 < len(levels) else None
    return {
        "current_level": levels[achieved_index] if achieved_index >= 0 else None,
        "next_level": next_level,
        "levels": levels,
        "dimensions": compute_dimensions(stats),
        "icu": compute_icu(stats, proofs),
        "proof_track": proof_track,
        "families": build_families(earned_ids),
        "stats": stats,
        "is_pioneer": is_pioneer,
        "level_up": level_up,
        "new_badges": to_award,
    }


@router.post("/charter/accept")
async def accept_charter(current_user: dict = Depends(get_current_user)):
    await db.ubuntoo_users.update_one(
        {"id": current_user["id"]},
        {"$set": {"charter_accepted": True, "charter_accepted_at": datetime.now(timezone.utc).isoformat()}},
    )
    return {"accepted": True}
