"""
Migrations automatiques - S'exécute au démarrage du backend.
Garantit l'intégrité des données et la compatibilité des schémas.
Figé le 22 juin 2026.
"""
import logging
from datetime import datetime, timezone

logger = logging.getLogger("migrations")


async def run_migrations(db):
    """Run all migrations on startup to ensure data integrity."""
    logger.info("[Migrations] Démarrage des migrations automatiques...")

    await migrate_passports_add_formations(db)
    await migrate_passports_ensure_dclic_fields(db)
    await migrate_coffre_optional_file_name(db)
    await migrate_illustrations_add_skill_type(db)
    await migrate_fiches_opc_skill_type(db)
    await migrate_remove_ubuntoo_global_competences(db)
    # Note: seed_peter7_demo_data and seed_referentiel_opc are called from server.py on_startup
    # AFTER user creation to ensure peter7/peter9 tokens exist

    logger.info("[Migrations] Migrations terminées.")


async def migrate_remove_ubuntoo_global_competences(db):
    """Retire les compétences émergentes globales (source ubuntoo) injectées à tort dans les passeports (fix août 2026)."""
    result = await db.passports.update_many(
        {"competences.source": "ubuntoo"},
        {"$pull": {"competences": {"source": "ubuntoo"}}}
    )
    if result.modified_count:
        logger.info(f"[Migration] Compétences globales 'ubuntoo' retirées de {result.modified_count} passeports")


async def migrate_passports_add_formations(db):
    """Ensure all passports have a 'formations' field (added 22 juin 2026)."""
    result = await db.passports.update_many(
        {"formations": {"$exists": False}},
        {"$set": {"formations": []}}
    )
    if result.modified_count > 0:
        logger.info(f"[Migration] Ajout du champ 'formations' à {result.modified_count} passeports")


async def migrate_passports_ensure_dclic_fields(db):
    """Ensure passports with dclic_results have proper sub-fields."""
    passports = await db.passports.find(
        {"dclic_results": {"$exists": True, "$ne": {}}},
        {"_id": 1, "dclic_results": 1}
    ).to_list(None)

    for p in passports:
        dclic = p.get("dclic_results", {})
        updates = {}
        # Ensure vertus_profile exists
        if "vertus_profile" not in dclic and "vertus_scores" in dclic:
            updates["dclic_results.vertus_profile"] = {
                "vertus_scores": dclic.get("vertus_scores", {}),
                "dominant_name": dclic.get("vertu_dominante_name", ""),
                "qualites_dominantes": dclic.get("qualites_dominantes", []),
                "savoirs_etre_dominants": dclic.get("savoirs_etre_dominants", []),
            }
        if updates:
            await db.passports.update_one({"_id": p["_id"]}, {"$set": updates})

    if passports:
        logger.info(f"[Migration] Vérifié {len(passports)} passeports avec D'CLIC")


async def migrate_coffre_optional_file_name(db):
    """Ensure coffre_documents without file_name don't break (added 22 juin 2026)."""
    result = await db.coffre_documents.update_many(
        {"file_name": {"$exists": False}},
        {"$set": {"file_name": None}}
    )
    if result.modified_count > 0:
        logger.info(f"[Migration] Correction de {result.modified_count} docs coffre sans file_name")


async def migrate_illustrations_add_skill_type(db):
    """Ensure all illustrations have skill_type field (added 22 juin 2026)."""
    result = await db.skill_illustrations.update_many(
        {"skill_type": {"$exists": False}},
        {"$set": {"skill_type": "soft"}}
    )
    if result.modified_count > 0:
        logger.info(f"[Migration] Ajout skill_type='soft' à {result.modified_count} illustrations")


async def migrate_fiches_opc_skill_type(db):
    """Backfill skill_type in fiches_metier_opc competences from coffre_documents (added 22 juin 2026)."""
    fiches = await db.fiches_metier_opc.find().to_list(500)
    updated = 0
    for fiche in fiches:
        competences = fiche.get("competences", {})
        changed = False
        for skill_name, skill_data in competences.items():
            if isinstance(skill_data, dict) and "skill_type" not in skill_data:
                # Try to find skill_type from coffre_documents
                coffre = await db.coffre_documents.find_one({
                    "linked_soft_skill": skill_name,
                    "skill_type": {"$exists": True}
                })
                if coffre:
                    skill_data["skill_type"] = coffre.get("skill_type", "soft")
                else:
                    skill_data["skill_type"] = "soft"
                changed = True
        if changed:
            await db.fiches_metier_opc.update_one(
                {"_id": fiche["_id"]},
                {"$set": {"competences": competences}}
            )
            updated += 1
    if updated > 0:
        logger.info(f"[Migration] Ajout skill_type aux compétences de {updated} fiches métier OPC")



async def seed_peter7_demo_data(db):
    """Seed peter7 AND peter9 passports with demo data (formations, experiences, competences, D'CLIC, OPC contributions).
    Only runs if the user exists and has an empty passport (no experiences)."""
    import json, os

    data_path = os.path.join(os.path.dirname(__file__), "seed_data_peter7_passport.json")
    extra_path = os.path.join(os.path.dirname(__file__), "seed_data_peter7_extra.json")

    if not os.path.exists(data_path):
        return

    with open(data_path, "r") as f:
        passport_data = json.load(f)

    extra = {}
    if os.path.exists(extra_path):
        with open(extra_path, "r") as f:
            extra = json.load(f)

    import copy, uuid

    for pseudo in ["peter7", "peter9"]:
        token_doc = await db.tokens.find_one({"pseudo": pseudo})
        if not token_doc:
            continue

        tid = token_doc["id"]
        passport = await db.passports.find_one({"token_id": tid})

        # Seed if passport has no experiences (fresh) OR no formations (partially filled)
        needs_full_seed = not passport or len(passport.get("experiences", [])) == 0
        needs_formations = passport and len(passport.get("formations", [])) == 0

        if needs_full_seed or needs_formations:
            update_fields = {
                "formations": copy.deepcopy(passport_data.get("formations", [])),
                "experiences": copy.deepcopy(passport_data.get("experiences", [])),
                "competences": copy.deepcopy(passport_data.get("competences", [])),
                "professional_summary": passport_data.get("professional_summary", ""),
                "career_project": passport_data.get("career_project", ""),
                "savoir_faire": copy.deepcopy(passport_data.get("savoir_faire", [])),
                "savoir_etre": copy.deepcopy(passport_data.get("savoir_etre", [])),
                "completeness_score": passport_data.get("completeness_score", 0),
                "dclic_results": copy.deepcopy(passport_data.get("dclic_results", {})),
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

            if passport and needs_formations and not needs_full_seed:
                update_partial = {
                    "formations": copy.deepcopy(passport_data.get("formations", [])),
                }
                if not passport.get("dclic_results", {}).get("vertus_profile"):
                    update_partial["dclic_results"] = copy.deepcopy(passport_data.get("dclic_results", {}))
                await db.passports.update_one({"token_id": tid}, {"$set": update_partial})
            elif passport:
                await db.passports.update_one({"token_id": tid}, {"$set": update_fields})
            else:
                update_fields["token_id"] = tid
                update_fields["learning_path"] = []
                update_fields["passerelles"] = []
                update_fields["sharing"] = {"is_public": False}
                update_fields["created_at"] = datetime.now(timezone.utc).isoformat()
                await db.passports.insert_one(update_fields)

            # Update profile
            profile_data = extra.get("profile", {})
            if profile_data:
                profile_update = {
                    "skills": copy.deepcopy(profile_data.get("skills", [])),
                    "strengths": copy.deepcopy(profile_data.get("strengths", [])),
                    "gaps": copy.deepcopy(profile_data.get("gaps", [])),
                    "savoir_etre": copy.deepcopy(profile_data.get("savoir_etre", [])),
                    "cv_analyzed": True,
                    "sectors": copy.deepcopy(profile_data.get("sectors", [])),
                }
                dclic_data = passport_data.get("dclic_results", {})
                vp = dclic_data.get("vertus_profile", {})
                if vp:
                    vertus_scores = vp.get("vertus_scores", {})
                    active_vertus = [v.capitalize() for v, s in vertus_scores.items() if s and s >= 40]
                    profile_update["dclic_vertu_dominante"] = vp.get("dominant_name", "")
                    profile_update["dclic_competences"] = vp.get("qualites_dominantes", [])
                    profile_update["dclic_mbti"] = ""
                    profile_update["dclic_disc_label"] = f"{len(active_vertus)} vertus actives"
                    profile_update["dclic_riasec_major"] = vp.get("dominant_name", "")
                    dclic_skills = []
                    for vname, vscore in vertus_scores.items():
                        if vscore and vscore >= 40:
                            dclic_skills.append({"name": vname.capitalize(), "level": vscore, "source": "dclic_pro"})
                    existing_skills = copy.deepcopy(profile_data.get("skills", []))
                    existing_non_dclic = [s for s in existing_skills if s.get("source") != "dclic_pro"]
                    profile_update["skills"] = existing_non_dclic + dclic_skills

                await db.profiles.update_one(
                    {"token_id": tid},
                    {"$set": profile_update}
                )

            # Seed OPC contributions (only if none exist for this user)
            existing_contribs = await db.opc_contributions.count_documents({"token_id": tid})
            if existing_contribs == 0:
                for contrib in extra.get("opc_contributions", []):
                    c = copy.deepcopy(contrib)
                    c["token_id"] = tid
                    c.pop("_id", None)
                    await db.opc_contributions.insert_one(c)

            # Seed fiches metier (only if none exist globally)
            existing_fiches = await db.fiches_metier_opc.count_documents({})
            if existing_fiches == 0:
                for fiche in extra.get("fiches_metier", []):
                    f = copy.deepcopy(fiche)
                    f.pop("_id", None)
                    await db.fiches_metier_opc.insert_one(f)

            logger.info(f"[Migration] Passport {pseudo} initialisé ({len(update_fields.get('formations', []))} formations, {len(update_fields.get('experiences', []))} expériences)")

        # ═══ DYNAMIC SEEDING: coffre docs + skill_illustrations based on ACTUAL experience IDs ═══
        passport_now = await db.passports.find_one({"token_id": tid})
        if not passport_now:
            continue
        actual_exps = passport_now.get("experiences", [])
        if not actual_exps:
            continue

        # Define S.A.R.E content templates (by experience title pattern)
        sare_bank = {
            "Chef cuisinier": {
                "soft": {"skill": "Rigueur", "S": "Lors de la réouverture après la période Covid, nous avons dû remettre en place l'ensemble des procédures de cuisine en 10 jours.", "A": "J'ai élaboré des fiches de poste individuelles avec les tâches à contrôler heure par heure.", "R": "Zéro non-conformité lors du premier contrôle sanitaire post-réouverture.", "E": "La rigueur ne s'impose pas, elle se coconstruit avec l'équipe."},
                "hard": {"skill": "Application des normes HACCP et sécurité alimentaire", "S": "Lors d'un événement traiteur pour 135 convives, la chaîne du froid a été compromise.", "A": "J'ai contrôlé les températures à cœur, écarté les produits hors seuil HACCP.", "R": "Aucun incident alimentaire. L'événement s'est déroulé sans retard.", "E": "J'intègre systématiquement un thermomètre sonde et une glacière de secours."},
            },
            "Chef Privé": {
                "soft": {"skill": "Créativité culinaire", "S": "Un client m'a commandé un dîner pour 8 personnes avec restrictions multiples (sans gluten, sans lactose, végétarien).", "A": "J'ai conçu un menu de 5 services entièrement adapté aux contraintes.", "R": "Le client a renouvelé sa commande 4 fois et m'a recommandé à 3 familles.", "E": "Les contraintes alimentaires sont des opportunités créatives."},
                "hard": {"skill": "Gestion de la relation client", "S": "Un client mécontent a exprimé son insatisfaction en direct lors d'un dîner privé.", "A": "J'ai écouté, proposé une alternative en 15 minutes, et échangé sur ses préférences.", "R": "Le client est devenu ambassadeur de mon service.", "E": "La gestion d'une insatisfaction est une opportunité de fidélisation."},
            },
            "Co-fondateur": {
                "soft": {"skill": "Leadership", "S": "En tant que co-fondateur, j'ai dû constituer et manager une brigade de 4 cuisiniers.", "A": "J'ai instauré des briefings quotidiens et mis en place un système de mentorat croisé.", "R": "Brigade autonome en 6 semaines. Turnover nul pendant 18 mois.", "E": "Le leadership n'est pas la direction mais la facilitation."},
                "hard": {"skill": "Gestion des coûts et approvisionnement", "S": "Les marges du restaurant étaient insuffisantes malgré un bon taux de remplissage.", "A": "J'ai renégocié 5 contrats fournisseurs et conçu des menus à rentabilité variable.", "R": "Le food cost est passé de 35% à 28% en 3 mois.", "E": "La maîtrise des coûts passe par l'intelligence des approvisionnements."},
            },
            "Sous-chef": {
                "soft": {"skill": "Adaptabilité interculturelle", "S": "En arrivant à Melbourne, j'ai intégré une brigade de 8 nationalités différentes.", "A": "J'ai observé 2 semaines, appris les techniques locales, proposé mes méthodes françaises.", "R": "Promu sous-chef en 4 mois. Mon approche fusion est devenue la signature du restaurant.", "E": "L'adaptabilité interculturelle est un accélérateur de carrière."},
                "hard": {"skill": "Techniques de cuisson avancées", "S": "Le chef m'a confié un menu dégustation de 7 services axé cuissons basse température.", "A": "J'ai testé 40 combinaisons temps/température sur 3 semaines et formé l'équipe.", "R": "Augmentation de 25% du ticket moyen. Mentionné dans le guide Broadsheet Melbourne.", "E": "La maîtrise technique est un processus itératif documenté."},
            },
            "événementiel": {
                "soft": {"skill": "Gestion du stress en environnement événementiel", "S": "Lors de la Foire aux Vins, 500 couverts en 3h avec équipement réduit et brigade inexpérimentée.", "A": "J'ai simplifié le menu en 3 formules et mis en place un flux de production tendu.", "R": "Tous les couverts servis dans les temps. Contrat reconduit pour 2 éditions.", "E": "En événementiel, la simplification est la clé de la réussite."},
                "hard": {"skill": "Production en volume et cadences événementielles", "S": "Pour 300 personnes, un plat nécessitait une cuisson minute impossible en série.", "A": "J'ai reconçu la recette en batch-cooking et optimisé le circuit en 4 postes.", "R": "Plat servi chaud à tous en moins de 20 minutes.", "E": "L'adaptation du geste au contexte événementiel est une compétence distincte."},
            },
            "Demi-chef": {
                "soft": {"skill": "Précision et régularité", "S": "Le chef exigeait une constance absolue dans le dressage de 80 assiettes par service.", "A": "J'ai développé une routine standardisée et créé des gabarits de dressage.", "R": "Taux de retour en cuisine de 0% sur 6 mois.", "E": "La régularité est le fondement de l'excellence en restauration gastronomique."},
                "hard": {"skill": "Mise en place et organisation du poste", "S": "Mon poste nécessitait 12 composants dans un espace restreint.", "A": "J'ai chronométré chaque étape et réorganisé physiquement le poste.", "R": "Temps de mise en place réduit de 3h30 à 2h45.", "E": "L'organisation d'un poste de cuisine s'optimise par la mesure et l'itération."},
            },
            "Commis": {
                "soft": {"skill": "Curiosité et apprentissage", "S": "En tant que commis au poste froid, j'étais fasciné par les techniques du pâtissier.", "A": "J'ai proposé d'arriver 1h plus tôt chaque jour pour observer et assister le pâtissier.", "R": "En 3 mois, j'ai acquis les bases et créé 2 desserts pour la carte.", "E": "La curiosité active est le meilleur accélérateur d'apprentissage."},
                "hard": {"skill": "Techniques de base en cuisine", "S": "Mes premières semaines, je devais réaliser des tailles de légumes parfaites.", "A": "J'ai pratiqué 30 min supplémentaires chaque jour et demandé un feedback quotidien.", "R": "En 6 semaines, mes brunoise et julienne ont atteint le standard. Promu au poste chaud.", "E": "Les techniques de base sont le socle de toute progression en cuisine."},
            },
            "Voyages": {
                "soft": {"skill": "Communication commerciale", "S": "J'ai dû vendre des forfaits voyage haut de gamme à une clientèle exigeante.", "A": "J'ai développé une approche conseil personnalisée et créé des dossiers visuels uniques.", "R": "Portefeuille clients augmenté de 30% en 6 mois.", "E": "La vente premium repose sur la personnalisation et l'écoute."},
                "hard": {"skill": "Conseil et vente de prestations touristiques", "S": "Un client pro cherchait un voyage incentive pour 25 personnes avec budget serré.", "A": "J'ai négocié avec 3 réceptifs locaux et construit un programme sur mesure.", "R": "Voyage réalisé 15% sous budget. L'entreprise a renouvelé pour 3 ans.", "E": "La négociation directe offre toujours un meilleur rapport qualité-prix."},
            },
            "Chef de Partie": {
                "soft": {"skill": "Polyvalence", "S": "J'ai dû couvrir simultanément les postes chaud et froid lors d'absences répétées.", "A": "J'ai réorganisé ma mise en place et formé un commis en urgence sur le poste froid.", "R": "Service jamais interrompu malgré brigade réduite de 40%. Promu responsable cuisine midi.", "E": "La polyvalence est une compétence stratégique qui maintient la qualité en toute circonstance."},
                "hard": {"skill": "Gestion simultanée de plusieurs postes", "S": "Un soir de forte affluence (90 couverts), deux cuisiniers ont fait défaut.", "A": "J'ai priorisé les envois par table et communiqué en continu avec la salle.", "R": "Aucune table n'a attendu plus de 5 minutes au-delà du temps normal.", "E": "La gestion multi-postes exige une vision globale et une capacité d'anticipation."},
            },
            "default": {
                "soft": {"skill": "Travail en équipe", "S": "Lors d'un service de 200 couverts, un collègue est tombé malade en plein service.", "A": "J'ai réorganisé la brigade et pris en charge le poste vacant.", "R": "Service terminé sans retard ni retour négatif.", "E": "Le travail en équipe implique de pouvoir occuper n'importe quel poste."},
                "hard": {"skill": "Maîtrise des cuissons et dressage gastronomique", "S": "Le chef m'a demandé de concevoir le dressage d'un nouveau menu pour un banquet.", "A": "J'ai réalisé 15 essais de dressage et formé 4 commis à la reproduction.", "R": "Le banquet a été un succès. Le protocole a gardé notre carte de dressage.", "E": "Le dressage gastronomique est un langage visuel reproductible."},
            },
        }

        def match_sare(title):
            title_lower = title.lower()
            for key in sare_bank:
                if key.lower() in title_lower:
                    return sare_bank[key]
            return sare_bank["default"]

        # Check if we need to re-seed (match coffre docs to actual exp IDs)
        existing_coffre_sare = await db.coffre_documents.count_documents({"token_id": tid, "document_type": "sare_proof"})
        existing_illus = await db.skill_illustrations.count_documents({"token_id": tid})
        
        # Check if existing coffre docs reference wrong exp IDs (mismatch with passport)
        actual_exp_ids = set(e.get("id") for e in actual_exps if e.get("id"))
        coffre_exp_ids = set()
        async for cdoc in db.coffre_documents.find({"token_id": tid, "document_type": "sare_proof"}, {"linked_experience_id": 1}):
            if cdoc.get("linked_experience_id"):
                coffre_exp_ids.add(cdoc["linked_experience_id"])
        
        ids_mismatch = coffre_exp_ids and not coffre_exp_ids.issubset(actual_exp_ids)
        needs_reseed = existing_coffre_sare < len(actual_exps) * 2 or existing_illus < len(actual_exps) * 2 or ids_mismatch
        
        if needs_reseed:
            logger.info(f"[Migration] {pseudo}: reseed nécessaire (coffre_sare={existing_coffre_sare}, illus={existing_illus}, mismatch={ids_mismatch}, exps={len(actual_exps)})")
            
            # Clear old seeded data (keep user-uploaded files with grid_id)
            await db.coffre_documents.delete_many({"token_id": tid, "grid_id": {"$exists": False}})
            await db.skill_illustrations.delete_many({"token_id": tid})
            
            now_iso = datetime.now(timezone.utc).isoformat()
            
            # Add CV original
            await db.coffre_documents.insert_one({
                "id": str(uuid.uuid4()), "token_id": tid, "title": "CV original",
                "category": "cv", "document_type": "cv", "source_type": "utilisateur",
                "description": "CV original analysé et validé par RE'ACTIF PRO",
                "trust_level": "certifie", "uploaded_at": now_iso, "updated_at": now_iso, "file_name": None
            })
            
            # Add diplomas
            for title, desc, dtype in [
                ("Certification HACCP — Hygiène alimentaire", "Certification HACCP — hygiène alimentaire en restauration", "certificat"),
                ("Diplôme — CAP Cuisine", "CAP Cuisine — Diplôme national de niveau V", "diplome"),
            ]:
                await db.coffre_documents.insert_one({
                    "id": str(uuid.uuid4()), "token_id": tid, "title": title,
                    "category": "diplome", "document_type": dtype, "source_type": "utilisateur",
                    "description": desc, "trust_level": "certifie",
                    "uploaded_at": now_iso, "updated_at": now_iso, "file_name": None
                })
            
            # For each ACTUAL experience, create: 2 S.A.R.E proofs + 1 contrat + 2 illustrations
            for exp in actual_exps:
                exp_id = exp.get("id")
                exp_title = exp.get("title", "")
                exp_org = exp.get("organization", "Non spécifié")
                sare_content = match_sare(exp_title)
                
                for skill_type_key in ["soft", "hard"]:
                    s = sare_content[skill_type_key]
                    # Coffre document
                    await db.coffre_documents.insert_one({
                        "id": str(uuid.uuid4()), "token_id": tid,
                        "title": f"Preuve S.A.R.E — {exp_title} ({exp_org})",
                        "category": "experience_prouvee", "document_type": "sare_proof",
                        "linked_experience_id": exp_id, "linked_soft_skill": s["skill"],
                        "linked_skill_type": skill_type_key, "linked_organization": exp_org,
                        "description": f"{skill_type_key.capitalize()} skill '{s['skill']}' prouvé par méthode S.A.R.E",
                        "source_type": "utilisateur", "trust_level": "valide",
                        "skill_type": skill_type_key,
                        "uploaded_at": now_iso, "updated_at": now_iso, "file_name": None
                    })
                    # Skill illustration
                    await db.skill_illustrations.insert_one({
                        "id": str(uuid.uuid4()), "token_id": tid,
                        "experience_id": exp_id, "soft_skill": s["skill"],
                        "skill_type": skill_type_key, "situation_text": "",
                        "sare_situation": s["S"], "sare_action": s["A"],
                        "sare_resultat": s["R"], "sare_enseignement": s["E"],
                        "opc_consent": True, "created_at": now_iso
                    })
                
                # Contrat
                await db.coffre_documents.insert_one({
                    "id": str(uuid.uuid4()), "token_id": tid,
                    "title": f"Contrat — {exp_title} ({exp_org})",
                    "category": "contrat_travail", "document_type": "contrat",
                    "linked_experience_id": exp_id, "linked_organization": exp_org,
                    "description": f"Contrat de travail — {exp_org}",
                    "source_type": "utilisateur", "trust_level": "certifie",
                    "uploaded_at": now_iso, "updated_at": now_iso, "file_name": None
                })
                
                # Mark experience as certified
                if not exp.get("proof_document"):
                    exp["proof_document"] = "contrat_seed"
                if not exp.get("is_certified"):
                    exp["is_certified"] = True
            
            await db.passports.update_one({"token_id": tid}, {"$set": {"experiences": actual_exps}})
            
            final_coffre = await db.coffre_documents.count_documents({"token_id": tid})
            final_illus = await db.skill_illustrations.count_documents({"token_id": tid})
            logger.info(f"[Migration] {pseudo}: {final_coffre} coffre docs + {final_illus} illustrations injectées (dynamique)")
        else:
            # Still ensure proof_document on all experiences
            updated = False
            for exp in actual_exps:
                if not exp.get("proof_document"):
                    exp["proof_document"] = "contrat_seed"
                    updated = True
                if not exp.get("is_certified"):
                    exp["is_certified"] = True
                    updated = True
            if updated:
                await db.passports.update_one({"token_id": tid}, {"$set": {"experiences": actual_exps}})
                logger.info(f"[Migration] {pseudo}: expériences marquées certifiées")


async def seed_referentiel_opc(db):
    """Seed referentiel_opc and opc_metiers from exported data if empty (added 22 juin 2026)."""
    import json, os

    # Seed referentiel_opc
    ref_count = await db.referentiel_opc.count_documents({})
    if ref_count == 0:
        ref_path = os.path.join(os.path.dirname(__file__), "seed_data_referentiel_opc.json")
        if os.path.exists(ref_path):
            with open(ref_path, "r") as f:
                docs = json.load(f)
            if docs:
                await db.referentiel_opc.insert_many(docs)
                logger.info(f"[Migration] Référentiel OPC initialisé: {len(docs)} métiers")

    # Seed opc_metiers (re-seed if empty or incomplete)
    met_count = await db.opc_metiers.count_documents({})
    if met_count < 10:
        met_path = os.path.join(os.path.dirname(__file__), "seed_data_opc_metiers.json")
        if os.path.exists(met_path):
            with open(met_path, "r") as f:
                docs = json.load(f)
            if docs:
                await db.opc_metiers.delete_many({})
                await db.opc_metiers.insert_many(docs)
                logger.info(f"[Migration] OPC Métiers initialisé: {len(docs)} fiches")
