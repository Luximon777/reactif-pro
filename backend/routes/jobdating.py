"""Job Dating routes — extracted from server.py for maintainability."""
from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
from database import db, get_current_token, _infer_sectors_from_profile, _SECTOR_KEYWORDS

router = APIRouter(prefix="/api")


def _build_user_profile_text(experiences, savoir_faire):
    """Build a combined text from user profile for display in AI summary."""
    parts = []
    exp_titles = []
    for e in (experiences or []):
        if isinstance(e, dict):
            t = e.get("title", "")
            if t:
                exp_titles.append(t)
    if exp_titles:
        parts.append(f"expériences : {', '.join(exp_titles[:4])}")

    skill_names = []
    for s in (savoir_faire or []):
        name = s.get("name", "") if isinstance(s, dict) else str(s)
        if name:
            skill_names.append(name)
    if skill_names:
        parts.append(f"compétences : {', '.join(skill_names[:4])}")

    return "; ".join(parts) if parts else None


def _generate_job_dating_events(experiences, savoir_faire, inferred_sectors):
    """Generate personalized job dating events based on user profile."""
    now = datetime.now(timezone.utc)

    base_events = [
        {"id": "evt-it-paris", "title": "Job Dating Numérique & IT — Paris La Défense", "city": "Paris", "postal_code": "92060", "address": "Grande Arche, Parvis de La Défense", "event_type": "job_dating", "mode": "presentiel", "source": "france_travail", "sectors": ["Informatique & Numérique"], "jobs_targeted": ["Développeur Web", "Data Analyst", "Admin Systèmes", "Chef de projet IT"], "companies_count": 35, "positions_count": 120, "description": "Rencontrez 35 entreprises du numérique. Plus de 120 postes à pourvoir en CDI et alternance."},
        {"id": "evt-sante-lyon", "title": "Forum Emploi Santé & Médico-social — Lyon", "city": "Lyon", "postal_code": "69003", "address": "Palais des Congrès de Lyon", "event_type": "forum", "mode": "presentiel", "source": "france_travail", "sectors": ["Santé & Médico-social"], "jobs_targeted": ["Aide-soignant(e)", "Infirmier(e)", "Éducateur spécialisé", "AMP"], "companies_count": 28, "positions_count": 200, "description": "Le plus grand forum emploi santé de la région AURA. Hôpitaux, EHPAD, associations."},
        {"id": "evt-commerce-online", "title": "E-Job Dating Commerce & Vente", "city": "En ligne", "postal_code": "", "address": "Plateforme Visio", "event_type": "e_job_dating", "mode": "distanciel", "source": "france_travail", "sectors": ["Commerce & Vente"], "jobs_targeted": ["Chargé de clientèle", "Commercial B2B", "Vendeur conseil", "Manager retail"], "companies_count": 20, "positions_count": 80, "description": "Passez vos entretiens depuis chez vous ! 20 enseignes et distributeurs recrutent."},
        {"id": "evt-btp-idf", "title": "Recrutement Collectif BTP — Île-de-France", "city": "Créteil", "postal_code": "94000", "address": "France Travail Créteil", "event_type": "recrutement_collectif", "mode": "presentiel", "source": "france_travail", "sectors": ["BTP & Construction"], "jobs_targeted": ["Électricien", "Plombier", "Conducteur de travaux", "Maçon"], "companies_count": 15, "positions_count": 65, "description": "Le secteur du BTP recrute massivement. Venez avec votre CV, repartez avec un contrat."},
        {"id": "evt-resto-bordeaux", "title": "Salon de l'Emploi Hôtellerie-Restauration — Bordeaux", "city": "Bordeaux", "postal_code": "33000", "address": "Palais de la Bourse", "event_type": "salon_emploi", "mode": "presentiel", "source": "salon_taf", "sectors": ["Restauration", "Hôtellerie"], "jobs_targeted": ["Cuisinier", "Serveur", "Réceptionniste", "Chef de rang", "Commis de cuisine", "Plongeur"], "companies_count": 40, "positions_count": 150, "description": "Saison estivale : hôtels, restaurants gastronomiques et chaînes recrutent. CDI, CDD saisonniers."},
        {"id": "evt-transport-marseille", "title": "Forum Emploi Transport & Logistique — Marseille", "city": "Marseille", "postal_code": "13002", "address": "Dock des Suds", "event_type": "forum", "mode": "presentiel", "source": "france_travail", "sectors": ["Logistique & Transport"], "jobs_targeted": ["Chauffeur-livreur", "Préparateur de commandes", "Cariste", "Chef de quai", "Magasinier"], "companies_count": 22, "positions_count": 95, "description": "Port de Marseille-Fos : logistique portuaire, messagerie, e-commerce. CACES apprécié."},
        {"id": "evt-proprete-lille", "title": "Job Dating Propreté & Services — Lille", "city": "Lille", "postal_code": "59000", "address": "Maison de l'Emploi Lille", "event_type": "job_dating", "mode": "presentiel", "source": "france_travail", "sectors": ["Propreté & Services"], "jobs_targeted": ["Agent d'entretien", "Chef d'équipe propreté", "Agent de maintenance", "Agent de service"], "companies_count": 12, "positions_count": 45, "description": "Entreprises de propreté des Hauts-de-France : CDI temps plein et temps partiel."},
        {"id": "evt-finance-online", "title": "E-Job Dating Comptabilité, Finance & RH", "city": "En ligne", "postal_code": "", "address": "Plateforme Visio", "event_type": "e_job_dating", "mode": "distanciel", "source": "24h_emploi", "sectors": ["Comptabilité, Finance & RH"], "jobs_targeted": ["Comptable", "Gestionnaire de paie", "Responsable RH", "Contrôleur de gestion"], "companies_count": 18, "positions_count": 55, "description": "Cabinets d'expertise comptable et services RH de grands groupes recrutent en visio."},
        {"id": "evt-industrie-strasbourg", "title": "Forum Emploi Industrie 4.0 — Grand Est", "city": "Strasbourg", "postal_code": "67000", "address": "Parc des Expositions", "event_type": "forum", "mode": "presentiel", "source": "france_travail", "sectors": ["Industrie & Production"], "jobs_targeted": ["Technicien maintenance", "Conducteur de ligne", "Opérateur CN", "Soudeur"], "companies_count": 30, "positions_count": 110, "description": "L'industrie du Grand Est recrute : automobile, agroalimentaire, pharma."},
        {"id": "evt-social-toulouse", "title": "Salon Emploi Social & Insertion — Toulouse", "city": "Toulouse", "postal_code": "31000", "address": "Espace Diversités", "event_type": "salon_emploi", "mode": "presentiel", "source": "salon_taf", "sectors": ["Petite Enfance & Social", "Santé & Médico-social"], "jobs_targeted": ["Éducateur spécialisé", "Conseiller insertion", "Moniteur éducateur", "Animateur socio-culturel"], "companies_count": 16, "positions_count": 50, "description": "Associations, collectivités et structures médico-sociales d'Occitanie recrutent."},
        {"id": "evt-agri-rennes", "title": "Job Dating Agriculture & Agroalimentaire — Rennes", "city": "Rennes", "postal_code": "35000", "address": "Parc Expo Rennes", "event_type": "job_dating", "mode": "presentiel", "source": "france_travail", "sectors": ["Agriculture & Agroalimentaire"], "jobs_targeted": ["Ouvrier agricole", "Technicien agro", "Conducteur d'engins"], "companies_count": 20, "positions_count": 70, "description": "Filière agricole et agroalimentaire bretonne : CDI, saisonniers, alternances."},
        {"id": "evt-marketing-online", "title": "E-Job Dating Marketing & Communication digitale", "city": "En ligne", "postal_code": "", "address": "Plateforme Visio", "event_type": "e_job_dating", "mode": "distanciel", "source": "village_recruteurs", "sectors": ["Communication & Marketing"], "jobs_targeted": ["Community Manager", "Chef de projet digital", "Traffic Manager", "Graphiste"], "companies_count": 15, "positions_count": 40, "description": "Agences et annonceurs recherchent des profils digitaux. Venez avec votre portfolio."},
        {"id": "evt-enfance-nantes", "title": "Forum Petite Enfance & Animation — Nantes", "city": "Nantes", "postal_code": "44000", "address": "Cité des Congrès", "event_type": "forum", "mode": "presentiel", "source": "france_travail", "sectors": ["Petite Enfance & Social"], "jobs_targeted": ["Auxiliaire de puériculture", "Agent de crèche", "Animateur périscolaire", "Assistante maternelle", "ATSEM"], "companies_count": 25, "positions_count": 80, "description": "Crèches, écoles maternelles et centres d'animation des Pays de la Loire recrutent."},
        {"id": "evt-resto-online", "title": "E-Job Dating Restauration Collective & Rapide", "city": "En ligne", "postal_code": "", "address": "Plateforme Visio", "event_type": "e_job_dating", "mode": "distanciel", "source": "france_travail", "sectors": ["Restauration"], "jobs_targeted": ["Employé polyvalent de restauration", "Cuisinier collectivité", "Agent de restauration", "Second de cuisine"], "companies_count": 18, "positions_count": 90, "description": "Restauration collective (hôpitaux, cantines, entreprises) et chaînes de restauration rapide."},
        {"id": "evt-logistique-online", "title": "E-Job Dating Logistique & Supply Chain", "city": "En ligne", "postal_code": "", "address": "Plateforme Visio", "event_type": "e_job_dating", "mode": "distanciel", "source": "24h_emploi", "sectors": ["Logistique & Transport"], "jobs_targeted": ["Magasinier", "Préparateur de commandes", "Agent logistique", "Responsable expéditions"], "companies_count": 22, "positions_count": 100, "description": "Amazon, Cdiscount, GLS et 19 autres acteurs de la logistique recrutent en visio."},
        {"id": "evt-admin-paris", "title": "Job Dating Secrétariat & Administration — Paris", "city": "Paris", "postal_code": "75012", "address": "France Travail Paris Bercy", "event_type": "job_dating", "mode": "presentiel", "source": "france_travail", "sectors": ["Administration & Secrétariat"], "jobs_targeted": ["Assistant(e) administratif", "Secrétaire", "Agent d'accueil", "Gestionnaire dossiers"], "companies_count": 14, "positions_count": 40, "description": "Administrations, cabinets et entreprises recherchent des profils administratifs."},
        {"id": "evt-multiservice-lyon", "title": "Forum Multi-Services & Polyvalence — Lyon", "city": "Lyon", "postal_code": "69007", "address": "Halle Tony Garnier", "event_type": "forum", "mode": "presentiel", "source": "salon_taf", "sectors": ["Propreté & Services", "Logistique & Transport", "Restauration"], "jobs_targeted": ["Agent polyvalent", "Employé polyvalent", "Agent d'entretien", "Manutentionnaire"], "companies_count": 30, "positions_count": 130, "description": "Recrutement tous secteurs : propreté, logistique, restauration, manutention. Venez sans CV !"},
    ]

    user_texts = []
    exp_titles = []
    for e in (experiences or []):
        if isinstance(e, dict):
            t = e.get("title", "")
            if t:
                user_texts.append(t.lower())
                exp_titles.append(t.lower())
            org = e.get("organization", "")
            if org:
                user_texts.append(org.lower())
    skill_names = []
    for s in (savoir_faire or []):
        name = s.get("name", "") if isinstance(s, dict) else str(s)
        if name:
            user_texts.append(name.lower())
            skill_names.append(name.lower())

    user_corpus = " ".join(user_texts)
    inferred_set = set(s.lower() for s in (inferred_sectors or []))
    events = []

    for i, base in enumerate(base_events):
        days_offset = 2 + ((i * 7 + 3) % 55)
        start = now + timedelta(days=days_offset, hours=9)
        end = start + timedelta(hours=4)

        match_score = 0
        match_reasons = []
        evt_sectors = [s.lower() for s in base.get("sectors", [])]
        evt_jobs = [j.lower() for j in base.get("jobs_targeted", [])]

        sector_match_found = False
        for es in evt_sectors:
            for inf_s in inferred_set:
                if inf_s in es or es in inf_s:
                    rank = list(inferred_set).index(inf_s) if inf_s in list(inferred_set) else 99
                    bonus = 40 if rank == 0 else 30 if rank == 1 else 20
                    match_score += bonus
                    sector_match_found = True
                    match_reasons.append(f"Secteur « {es.title()} » correspond à votre profil")
                    break
            if sector_match_found:
                break

        exp_match_count = 0
        for ej in evt_jobs:
            ej_words = [w for w in ej.split() if len(w) > 3]
            for ut in exp_titles:
                if any(w in ut for w in ej_words):
                    exp_match_count += 1
                    match_reasons.append(f"Votre expérience « {ut.title()} » correspond à « {ej.title()} »")
                    break
        if exp_match_count > 0:
            match_score += min(exp_match_count * 15, 30)

        skill_match_count = 0
        matched_skills = []
        for sk in skill_names:
            sk_words = [w for w in sk.split() if len(w) > 3]
            for ej in evt_jobs + evt_sectors:
                if any(w in ej for w in sk_words) or any(w in sk for w in ej.split() if len(w) > 3):
                    skill_match_count += 1
                    matched_skills.append(sk[:40])
                    break
        if skill_match_count > 0:
            match_score += min(skill_match_count * 5, 20)
            match_reasons.append(f"{skill_match_count} compétence(s) en lien ({', '.join(matched_skills[:3])})")

        if base.get("mode") == "distanciel":
            match_score += 5

        match_score = max(match_score, 5)
        match_score = min(match_score, 98)
        match_level = "fort" if match_score >= 55 else "moyen" if match_score >= 25 else "faible"

        event = {
            **base,
            "start_datetime": start.isoformat(),
            "end_datetime": end.isoformat(),
            "match_score": match_score,
            "match_level": match_level,
            "ai_reason": " · ".join(match_reasons[:3]) if match_reasons else "Événement à découvrir pour élargir votre recherche",
            "is_urgent": days_offset <= 3,
            "is_soon": days_offset <= 7,
            "is_partner_event": False,
            "has_profile_access": False,
            "registration_url": f"https://mesevenementsemploi.francetravail.fr/mes-evenements-emploi/evenement/{100000 + i}",
        }
        events.append(event)

    events.sort(key=lambda e: e["match_score"], reverse=True)
    return events


async def _get_user_profile_for_jobdating(token_doc):
    """Extract comprehensive user profile data for job dating matching."""
    passport = await db.passports.find_one({"token_id": token_doc["id"]})
    savoir_faire = (passport or {}).get("savoir_faire", [])
    experiences = (passport or {}).get("experiences", [])
    inferred_sectors = _infer_sectors_from_profile(experiences, savoir_faire)
    return experiences, savoir_faire, inferred_sectors


@router.get("/jobdating/events")
async def get_jobdating_events(token: str, q: str = None, days: str = None, mode: str = None):
    token_doc = await get_current_token(token)
    experiences, savoir_faire, inferred_sectors = await _get_user_profile_for_jobdating(token_doc)
    events = _generate_job_dating_events(experiences, savoir_faire, inferred_sectors)
    return {"events": events, "total": len(events)}


@router.get("/jobdating/sectors")
async def get_jobdating_sectors():
    return {"sectors": [
        {"name": "Informatique & Numérique", "count": 35},
        {"name": "Santé & Médico-social", "count": 28},
        {"name": "Commerce & Vente", "count": 20},
        {"name": "BTP & Construction", "count": 15},
        {"name": "Hôtellerie & Restauration", "count": 40},
        {"name": "Logistique & Transport", "count": 22},
        {"name": "Industrie & Production", "count": 30},
        {"name": "Comptabilité, Finance & RH", "count": 18},
        {"name": "Petite Enfance & Social", "count": 25},
        {"name": "Agriculture & Agroalimentaire", "count": 20},
        {"name": "Communication & Marketing", "count": 15},
        {"name": "Propreté & Services", "count": 12},
        {"name": "Administration & Secrétariat", "count": 14},
    ]}


@router.get("/jobdating/recommended")
async def get_jobdating_recommended(token: str, city: str = None):
    token_doc = await get_current_token(token)
    experiences, savoir_faire, inferred_sectors = await _get_user_profile_for_jobdating(token_doc)
    events = _generate_job_dating_events(experiences, savoir_faire, inferred_sectors)

    recommended = [e for e in events if e["match_score"] >= 25]
    if city:
        city_lower = city.lower()
        city_filtered = [e for e in recommended if city_lower in (e.get("city", "").lower()) or e.get("mode") == "distanciel"]
        if city_filtered:
            recommended = city_filtered

    profile_text = _build_user_profile_text(experiences, savoir_faire)
    sectors_text = ", ".join(inferred_sectors[:3]) if inferred_sectors else None

    if recommended:
        summary_parts = []
        if profile_text:
            summary_parts.append(f"Votre profil ({profile_text})")
        if sectors_text:
            summary_parts.append(f"secteurs détectés : {sectors_text}")
        base = " — ".join(summary_parts) if summary_parts else "Votre profil"
        ai_summary = f"{base}. {len(recommended)} événement(s) correspondent à vos compétences."
    else:
        ai_summary = "Enrichissez votre profil (CV, expériences) pour recevoir des recommandations personnalisées."

    return {"events": recommended[:10], "ai_summary": ai_summary, "total": len(recommended)}


@router.get("/jobdating/saved")
async def get_saved_events(token: str):
    token_doc = await get_current_token(token)
    saved = await db.saved_events.find({"token_id": token_doc["id"]}, {"_id": 0}).to_list(50)
    return {"events": saved}


@router.post("/jobdating/events/{event_id}/save")
async def save_event(event_id: str, token: str):
    token_doc = await get_current_token(token)
    existing = await db.saved_events.find_one({"token_id": token_doc["id"], "event_id": event_id})
    if not existing:
        await db.saved_events.insert_one({
            "token_id": token_doc["id"], "event_id": event_id,
            "saved_at": datetime.now(timezone.utc).isoformat()
        })
    return {"success": True}


@router.delete("/jobdating/events/{event_id}/save")
async def unsave_event(event_id: str, token: str):
    token_doc = await get_current_token(token)
    await db.saved_events.delete_one({"token_id": token_doc["id"], "event_id": event_id})
    return {"success": True}


@router.get("/jobdating/registrations")
async def get_registrations(token: str):
    token_doc = await get_current_token(token)
    regs = await db.event_registrations.find({"token_id": token_doc["id"]}, {"_id": 0}).to_list(50)
    return {"registrations": regs}


@router.post("/jobdating/events/{event_id}/register")
async def register_event(event_id: str, token: str):
    token_doc = await get_current_token(token)
    existing = await db.event_registrations.find_one({"token_id": token_doc["id"], "event_id": event_id})
    if not existing:
        await db.event_registrations.insert_one({
            "token_id": token_doc["id"], "event_id": event_id,
            "registered_at": datetime.now(timezone.utc).isoformat()
        })
    return {"success": True}


@router.get("/jobdating/history")
async def get_jobdating_history(token: str):
    token_doc = await get_current_token(token)
    regs = await db.event_registrations.find({"token_id": token_doc["id"]}, {"_id": 0}).to_list(50)
    now = datetime.now(timezone.utc)

    upcoming = []
    past = []
    for reg in regs:
        event_id = reg.get("event_id", "")
        start_str = reg.get("start_datetime", now.isoformat())
        try:
            start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        except Exception:
            start_dt = now
        days_until = (start_dt - now).days

        entry = {
            "title": event_id,
            "start_datetime": start_str,
            "city": reg.get("city", ""),
            "mode": reg.get("mode", "presentiel"),
            "days_until": max(0, days_until),
            "participated": reg.get("participated"),
            "evaluation": reg.get("evaluation"),
            "non_participation_reason": reg.get("non_participation_reason"),
            "companies_list": [],
            "address": reg.get("address", ""),
        }
        if start_dt > now:
            upcoming.append(entry)
        else:
            past.append(entry)

    return {"upcoming": upcoming, "past": past}


@router.post("/jobdating/events/{event_id}/participated")
async def mark_participated(event_id: str, token: str, participated: bool = True):
    token_doc = await get_current_token(token)
    await db.event_registrations.update_one(
        {"token_id": token_doc["id"], "event_id": event_id},
        {"$set": {"participated": participated}}
    )
    return {"success": True}


@router.post("/jobdating/events/{event_id}/evaluate")
async def evaluate_event(event_id: str, token: str, rating: int = 3, organization: int = 3, usefulness: int = 3, would_recommend: bool = True, comment: str = ""):
    token_doc = await get_current_token(token)
    evaluation = {
        "rating": rating, "organization": organization, "usefulness": usefulness,
        "would_recommend": would_recommend, "comment": comment,
        "evaluated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.event_registrations.update_one(
        {"token_id": token_doc["id"], "event_id": event_id},
        {"$set": {"evaluation": evaluation, "participated": True}}
    )
    return {"success": True}


@router.post("/jobdating/events/{event_id}/no-show")
async def no_show_event(event_id: str, token: str, reason: str = "", details: str = ""):
    token_doc = await get_current_token(token)
    await db.event_registrations.update_one(
        {"token_id": token_doc["id"], "event_id": event_id},
        {"$set": {"non_participation_reason": {"reason": reason, "details": details}, "participated": False}}
    )
    return {"success": True}


@router.get("/jobdating/web-search")
async def jobdating_web_search(token: str, city: str = ""):
    """Placeholder for web search - returns empty for now."""
    return {"events": [], "city": city}
