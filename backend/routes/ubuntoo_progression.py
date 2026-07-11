"""UBUNTOO — Parcours d'évolution des membres (badges de niveaux).

Explorateur → Contributeur → Ambassadeur → Expert → Mentor → Leader Communautaire → Pionnier Ubuntoo
Progression évaluée sur 4 dimensions : Contribution, Expertise, Engagement, Impact humain.
"""
from fastapi import APIRouter, Depends
from datetime import datetime, timezone

from database import db
from routes.ubuntoo_social import get_current_user, award_badge

router = APIRouter(prefix="/api/social")

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


@router.get("/progression")
async def get_progression(current_user: dict = Depends(get_current_user)):
    stats = await compute_stats(current_user)
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

    next_level = levels[achieved_index + 1] if achieved_index + 1 < len(levels) else None
    return {
        "current_level": levels[achieved_index] if achieved_index >= 0 else None,
        "next_level": next_level,
        "levels": levels,
        "dimensions": compute_dimensions(stats),
        "stats": stats,
        "is_pioneer": is_pioneer,
        "level_up": level_up,
    }


@router.post("/charter/accept")
async def accept_charter(current_user: dict = Depends(get_current_user)):
    await db.ubuntoo_users.update_one(
        {"id": current_user["id"]},
        {"$set": {"charter_accepted": True, "charter_accepted_at": datetime.now(timezone.utc).isoformat()}},
    )
    return {"accepted": True}
