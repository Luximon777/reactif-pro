"""
OPC — Accès MongoDB (Motor async)
Réutilise la connexion existante du backend RE'ACTIF PRO.
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient

_MONGO_URL = os.environ.get("MONGO_URL")
_DB_NAME = os.environ.get("DB_NAME")

_client: AsyncIOMotorClient | None = None


def _get_db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(_MONGO_URL)
    return _client[_DB_NAME]


# ─── Accesseurs des 8 collections ─────────────────────────────────────────

def col_profils():
    return _get_db()["opc_profils"]

def col_entreprises():
    return _get_db()["opc_entreprises"]

def col_offres():
    return _get_db()["opc_offres"]

def col_formations():
    return _get_db()["opc_formations"]

def col_institutionnel():
    return _get_db()["opc_institutionnel"]

def col_terrain():
    return _get_db()["opc_terrain"]

def col_parcours():
    return _get_db()["opc_parcours"]

def col_referentiels():
    return _get_db()["opc_referentiels"]


async def create_indexes():
    """Crée les index recommandés sur les 8 collections."""
    db = _get_db()

    await db["opc_profils"].create_index([("user_id", 1)])
    await db["opc_profils"].create_index([("code_rome_vise", 1), ("territoire", 1)])
    await db["opc_profils"].create_index([("competences_techniques", 1)])

    await db["opc_entreprises"].create_index([("entreprise_id", 1)])
    await db["opc_entreprises"].create_index([("secteur", 1), ("territoire", 1)])
    await db["opc_entreprises"].create_index([("metiers_en_tension", 1)])

    await db["opc_offres"].create_index([("code_rome", 1), ("localisation", 1)])
    await db["opc_offres"].create_index([("date_publication", -1)])
    await db["opc_offres"].create_index([("mots_cles_emergents", 1)])

    await db["opc_formations"].create_index([("codes_rome", 1), ("localisation", 1)])
    await db["opc_formations"].create_index([("financements_possibles", 1)])

    await db["opc_institutionnel"].create_index([("source", 1), ("type_donnee", 1)])

    await db["opc_terrain"].create_index([("type_source", 1), ("metier_concerne", 1)])
    await db["opc_terrain"].create_index([("competences_mentionnees", 1)])

    await db["opc_parcours"].create_index([("user_id", 1)])
    await db["opc_parcours"].create_index([("emploi_retrouve", 1), ("territoire", 1)])

    await db["opc_referentiels"].create_index([("code_rome", 1)], unique=True)
    await db["opc_referentiels"].create_index([("statut", 1), ("territoire", 1)])
    await db["opc_referentiels"].create_index([("competences_emergentes", 1)])

    print("[OPC] Index MongoDB créés")
