from fastapi import APIRouter
from db import db
from helpers import get_current_token

router = APIRouter()


@router.get("/coach/progress")
async def get_coach_progress(token: str):
    """Return the user's journey progress for the virtual coach."""
    token_doc = await get_current_token(token)
    token_id = token_doc["id"]

    profile = await db.profiles.find_one({"token_id": token_id}, {"_id": 0})
    dclic = await db.dclic_results.find_one({"token_id": token_id}, {"_id": 0})
    cv_job = await db.cv_jobs.find_one(
        {"token_id": token_id, "status": "completed"}, {"_id": 0}
    )
    passport = await db.passports.find_one({"token_id": token_id}, {"_id": 0})
    steps_count = await db.trajectory_steps.count_documents({"token_id": token_id})

    # Step 1: Personality (D'CLIC PRO)
    has_dclic = dclic is not None
    dclic_disc = profile.get("dclic_disc_label") if profile else None
    dclic_vertu = profile.get("dclic_vertu_dominante") if profile else None
    dclic_riasec = profile.get("dclic_riasec_major") if profile else None
    step1_complete = has_dclic or bool(dclic_disc)
    step1_partial = bool(profile and (profile.get("skills") or profile.get("strengths")))

    # Step 2: What makes sense (values, interests, trajectory)
    has_trajectory = steps_count > 0
    has_values = bool(dclic_vertu)
    has_interests = bool(dclic_riasec)
    has_project = bool(passport and passport.get("career_project"))
    step2_complete = (has_values or has_interests) and (has_trajectory or has_project)
    step2_partial = has_trajectory or has_values or has_interests or has_project

    # Step 3: CV and competences valorization
    has_cv = cv_job is not None
    passport_competences = len(passport.get("competences", [])) if passport else 0
    profile_skills = len(profile.get("skills", [])) if profile else 0
    step3_complete = has_cv and (passport_competences > 0 or profile_skills >= 3)
    step3_partial = has_cv or passport_competences > 0 or profile_skills > 0

    # Step 4: Market exploration
    has_target_job = bool(profile and profile.get("target_job"))
    has_sectors = bool(profile and profile.get("sectors"))
    profile_score = profile.get("profile_score", 0) if profile else 0
    step4_complete = has_target_job and profile_score >= 40
    step4_partial = has_target_job or has_sectors

    steps = [
        {
            "id": 1,
            "title": "Découvrir votre personnalité",
            "description": "Passez le test D'CLIC PRO pour révéler votre profil comportemental, vos intérêts et vos forces.",
            "complete": step1_complete,
            "partial": step1_partial,
            "action_label": "Importer D'CLIC PRO" if not step1_complete else None,
            "action_path": None,
            "action_type": "dclic",
            "details": {
                "disc": dclic_disc,
                "vertu": dclic_vertu,
                "riasec": dclic_riasec,
            }
        },
        {
            "id": 2,
            "title": "Ce qui fait sens pour vous",
            "description": "Explorez vos valeurs, vos vertus et tracez votre trajectoire pour donner du sens à votre parcours.",
            "complete": step2_complete,
            "partial": step2_partial,
            "action_label": "Tracer ma trajectoire" if not has_trajectory else ("Définir mon projet" if not has_project else None),
            "action_path": "/dashboard/trajectoire" if not has_trajectory else "/dashboard/profil",
            "action_type": "navigate",
            "details": {
                "has_trajectory": has_trajectory,
                "steps_count": steps_count,
                "has_values": has_values,
                "has_project": has_project,
            }
        },
        {
            "id": 3,
            "title": "Valoriser vos compétences",
            "description": "Déposez votre CV pour que l'IA identifie et valorise toutes vos compétences professionnelles.",
            "complete": step3_complete,
            "partial": step3_partial,
            "action_label": "Analyser mon CV" if not has_cv else ("Voir mes compétences" if not step3_complete else None),
            "action_path": "/dashboard/competences" if not has_cv else "/dashboard/competences",
            "action_type": "navigate",
            "details": {
                "has_cv": has_cv,
                "competences_count": passport_competences + profile_skills,
            }
        },
        {
            "id": 4,
            "title": "Explorer le marché",
            "description": "Découvrez les tendances de votre secteur, les compétences émergentes et les opportunités qui vous correspondent.",
            "complete": step4_complete,
            "partial": step4_partial,
            "action_label": "Voir le marché" if not step4_partial else ("Voir les opportunités" if not step4_complete else None),
            "action_path": "/dashboard/marche" if not step4_partial else "/dashboard/opportunites",
            "action_type": "navigate",
            "details": {
                "has_target_job": has_target_job,
                "profile_score": profile_score,
            }
        },
    ]

    completed = sum(1 for s in steps if s["complete"])
    current_step = next((s["id"] for s in steps if not s["complete"]), 5)

    # Generate contextual coach message based on current step
    if completed == 4:
        message = "Félicitations ! Vous avez complété tout votre parcours de découverte. Votre profil est riche et personnalisé. Continuez à l'enrichir au fil du temps !"
        emoji = "trophy"
    elif current_step == 1:
        message = "Bienvenue ! Commençons par découvrir votre personnalité avec le test D'CLIC PRO. C'est la base pour construire un parcours qui vous ressemble."
        emoji = "wave"
    elif current_step == 2:
        message = "Prenons le temps de comprendre ce qui fait vraiment sens pour vous. Tracez votre trajectoire et définissez votre projet professionnel."
        emoji = "star"
    elif current_step == 3:
        message = "Il est temps de mettre en lumière vos compétences ! Déposez votre CV et laissez l'IA révéler tout votre potentiel professionnel."
        emoji = "rocket"
    elif current_step == 4:
        message = "Dernière étape ! Explorez le marché pour découvrir où vos compétences sont les plus recherchées et quelles opportunités s'offrent à vous."
        emoji = "target"
    else:
        message = "Continuez à enrichir votre profil. Chaque information ajoutée rend vos recommandations plus pertinentes."
        emoji = "star"

    return {
        "steps": steps,
        "completed": completed,
        "total": 4,
        "current_step": current_step,
        "progress_pct": round((completed / 4) * 100),
        "message": message,
        "emoji": emoji,
    }
