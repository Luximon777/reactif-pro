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

