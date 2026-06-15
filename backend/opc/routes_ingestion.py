"""
OPC — Routes d'ingestion des 8 flux
POST /api/opc/ingestion/{flux}
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone
from typing import List

from .schemas import (
    ProfilUtilisateur, DonneeEntreprise, OffreEmploi,
    Formation, DonneeInstitutionnelle, DonneeTerrain,
    SuiviParcours, ReferentielVivant
)
from .db import (
    col_profils, col_entreprises, col_offres, col_formations,
    col_institutionnel, col_terrain, col_parcours, col_referentiels
)

router = APIRouter(prefix="/api/opc/ingestion", tags=["OPC - Ingestion"])


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ─── FLUX 1 — Profils ─────────────────────────────────────────────────────

@router.post("/profils", status_code=status.HTTP_201_CREATED)
async def ingest_profil(profil: ProfilUtilisateur):
    doc = profil.model_dump()
    doc["_ingested_at"] = _now()
    if not doc.get("validation", {}).get("consentement_rgpd"):
        raise HTTPException(400, "Consentement RGPD obligatoire pour ingérer un profil utilisateur")
    result = await col_profils().update_one(
        {"user_id": doc["user_id"]}, {"$set": doc}, upsert=True
    )
    return {
        "status": "ok", "flux": "profils_utilisateurs",
        "upserted": result.upserted_id is not None,
        "modified": result.modified_count > 0
    }


@router.post("/profils/batch", status_code=status.HTTP_201_CREATED)
async def ingest_profils_batch(profils: List[ProfilUtilisateur]):
    if len(profils) > 100:
        raise HTTPException(400, "Maximum 100 profils par batch")
    results = []
    for p in profils:
        doc = p.model_dump()
        doc["_ingested_at"] = _now()
        if doc.get("validation", {}).get("consentement_rgpd"):
            await col_profils().update_one(
                {"user_id": doc["user_id"]}, {"$set": doc}, upsert=True
            )
            results.append({"user_id": doc["user_id"], "status": "ok"})
        else:
            results.append({"user_id": doc.get("user_id"), "status": "skip_rgpd"})
    return {"flux": "profils_batch", "count": len(results), "results": results}


# ─── FLUX 2 — Entreprises ─────────────────────────────────────────────────

@router.post("/entreprises", status_code=status.HTTP_201_CREATED)
async def ingest_entreprise(data: DonneeEntreprise):
    doc = data.model_dump()
    doc["_ingested_at"] = _now()
    result = await col_entreprises().update_one(
        {"entreprise_id": doc["entreprise_id"]}, {"$set": doc}, upsert=True
    )
    return {"status": "ok", "flux": "donnees_entreprises",
            "upserted": result.upserted_id is not None}


# ─── FLUX 3 — Offres d'emploi ─────────────────────────────────────────────

@router.post("/offres", status_code=status.HTTP_201_CREATED)
async def ingest_offre(offre: OffreEmploi):
    doc = offre.model_dump()
    doc["_ingested_at"] = _now()
    result = await col_offres().insert_one(doc)
    return {"status": "ok", "flux": "offres_emploi", "id": str(result.inserted_id)}


@router.post("/offres/batch", status_code=status.HTTP_201_CREATED)
async def ingest_offres_batch(offres: List[OffreEmploi]):
    if len(offres) > 500:
        raise HTTPException(400, "Maximum 500 offres par batch")
    docs = []
    for o in offres:
        d = o.model_dump()
        d["_ingested_at"] = _now()
        docs.append(d)
    result = await col_offres().insert_many(docs)
    return {"flux": "offres_batch", "inserted": len(result.inserted_ids)}


# ─── FLUX 4 — Formations ──────────────────────────────────────────────────

@router.post("/formations", status_code=status.HTTP_201_CREATED)
async def ingest_formation(formation: Formation):
    doc = formation.model_dump()
    doc["_ingested_at"] = _now()
    result = await col_formations().update_one(
        {"intitule": doc["intitule"], "organisme": doc["organisme"],
         "localisation": doc["localisation"]},
        {"$set": doc}, upsert=True
    )
    return {"status": "ok", "flux": "formations",
            "upserted": result.upserted_id is not None}


# ─── FLUX 5 — Institutionnel ──────────────────────────────────────────────

@router.post("/institutionnel", status_code=status.HTTP_201_CREATED)
async def ingest_institutionnel(data: DonneeInstitutionnelle):
    doc = data.model_dump()
    doc["_ingested_at"] = _now()
    result = await col_institutionnel().insert_one(doc)
    return {"status": "ok", "flux": "institutionnel",
            "source": doc["source"], "id": str(result.inserted_id)}


# ─── FLUX 6 — Terrain ─────────────────────────────────────────────────────

@router.post("/terrain", status_code=status.HTTP_201_CREATED)
async def ingest_terrain(data: DonneeTerrain):
    doc = data.model_dump()
    doc["_ingested_at"] = _now()
    if not doc.get("sentiment") and doc.get("observation"):
        obs = doc["observation"].lower()
        pos = ["réussi", "embauché", "validé", "excellent", "positif", "retenu"]
        neg = ["échec", "refus", "abandon", "difficile", "problème", "rejeté"]
        if any(m in obs for m in pos):
            doc["sentiment"] = "positif"
        elif any(m in obs for m in neg):
            doc["sentiment"] = "negatif"
        else:
            doc["sentiment"] = "neutre"
    result = await col_terrain().insert_one(doc)
    return {"status": "ok", "flux": "terrain",
            "type_source": doc["type_source"],
            "sentiment_detecte": doc.get("sentiment"),
            "id": str(result.inserted_id)}


# ─── FLUX 7 — Parcours ────────────────────────────────────────────────────

@router.post("/parcours", status_code=status.HTTP_201_CREATED)
async def ingest_parcours(data: SuiviParcours):
    doc = data.model_dump()
    doc["_updated_at"] = _now()
    if not doc.get("validation", {}).get("consentement_rgpd"):
        raise HTTPException(400, "Consentement RGPD obligatoire pour le suivi de parcours")
    await col_parcours().update_one(
        {"user_id": doc["user_id"]}, {"$set": doc}, upsert=True
    )
    return {"status": "ok", "flux": "suivi_parcours",
            "user_id": doc["user_id"],
            "emploi_retrouve": doc.get("emploi_retrouve", False)}


# ─── FLUX 8 — Référentiels vivants ────────────────────────────────────────

@router.post("/referentiels", status_code=status.HTTP_201_CREATED)
async def upsert_referentiel(data: ReferentielVivant):
    doc = data.model_dump()
    doc["derniere_maj"] = _now()
    result = await col_referentiels().update_one(
        {"code_rome": doc["code_rome"]}, {"$set": doc}, upsert=True
    )
    return {"status": "ok", "flux": "referentiels_vivants",
            "code_rome": doc["code_rome"],
            "statut_metier": doc["statut"],
            "upserted": result.upserted_id is not None}


# ─── Stats globales ───────────────────────────────────────────────────────

@router.get("/stats")
async def get_ingestion_stats():
    return {
        "profils_utilisateurs": await col_profils().count_documents({}),
        "donnees_entreprises": await col_entreprises().count_documents({}),
        "offres_emploi": await col_offres().count_documents({}),
        "formations": await col_formations().count_documents({}),
        "donnees_institutionnelles": await col_institutionnel().count_documents({}),
        "observations_terrain": await col_terrain().count_documents({}),
        "suivis_parcours": await col_parcours().count_documents({}),
        "referentiels_vivants": await col_referentiels().count_documents({}),
        "timestamp": _now().isoformat()
    }
