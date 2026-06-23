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
    # Note: seed_peter7_demo_data and seed_referentiel_opc are called from server.py on_startup
    # AFTER user creation to ensure peter7/peter9 tokens exist

    logger.info("[Migrations] Migrations terminées.")


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

        # Seed coffre documents (preuves) — ALWAYS check independently of passport state
        coffre_path = os.path.join(os.path.dirname(__file__), "seed_data_coffre_documents.json")
        if os.path.exists(coffre_path):
            with open(coffre_path, "r") as cf:
                coffre_templates = json.load(cf)
            existing_coffre = await db.coffre_documents.count_documents({"token_id": tid})
            expected_min = len(coffre_templates)
            # Seed if user has fewer S.A.R.E/diplome proofs than expected
            existing_sare = await db.coffre_documents.count_documents({"token_id": tid, "document_type": "sare_proof"})
            existing_diplomes = await db.coffre_documents.count_documents({"token_id": tid, "category": "diplome"})
            if existing_sare < 10 or existing_diplomes < 2:
                # Remove old seed-type docs to avoid duplicates, keep user-uploaded files (with grid_id)
                await db.coffre_documents.delete_many({
                    "token_id": tid,
                    "document_type": {"$in": ["sare_proof", "diplome", "certificat", "contrat"]},
                    "grid_id": {"$exists": False}
                })
                now_iso = datetime.now(timezone.utc).isoformat()
                for tmpl in coffre_templates:
                    doc = copy.deepcopy(tmpl)
                    doc["id"] = str(uuid.uuid4())
                    doc["token_id"] = tid
                    doc["uploaded_at"] = now_iso
                    doc["updated_at"] = now_iso
                    doc.setdefault("file_name", None)
                    await db.coffre_documents.insert_one(doc)
                final_count = await db.coffre_documents.count_documents({"token_id": tid})
                logger.info(f"[Migration] {len(coffre_templates)} preuves coffre-fort injectées pour {pseudo} (total: {final_count})")


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

    # Seed opc_metiers
    met_count = await db.opc_metiers.count_documents({})
    if met_count == 0:
        met_path = os.path.join(os.path.dirname(__file__), "seed_data_opc_metiers.json")
        if os.path.exists(met_path):
            with open(met_path, "r") as f:
                docs = json.load(f)
            if docs:
                await db.opc_metiers.insert_many(docs)
                logger.info(f"[Migration] OPC Métiers initialisé: {len(docs)} fiches")
