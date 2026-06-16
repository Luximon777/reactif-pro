"""
OPC — Routes API RNCP / France Compétences
============================================
Expose les données RNCP importées par l'ETL (seed_rncp.py) pour :
- Recherche de certifications
- Détail des blocs de compétences
- Mapping RNCP ↔ ROME
- Statistiques
- Analyse des écarts (gap analysis) entre profil utilisateur et certification
"""

import os
import logging
from typing import Optional, List
from datetime import datetime, timezone

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/referentiel/rncp", tags=["RNCP"])

_client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGO_URL"])
_db = _client[os.environ.get("DB_NAME", "test_database")]


# ─── Request models ───────────────────────────────────────────────────────────
class GapAnalysisRequest(BaseModel):
    code_rncp: str
    competences_utilisateur: List[str] = []


# ─── ENDPOINT: Recherche de certifications ────────────────────────────────────

@router.get("/search")
async def search_certifications(
    q: str = Query("", description="Recherche textuelle"),
    type: str = Query("", description="RNCP ou RS"),
    niveau: str = Query("", description="NIV3, NIV4, NIV5, NIV6, NIV7"),
    statut: str = Query("ACTIVE", description="ACTIVE ou INACTIVE"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Rechercher des certifications RNCP/RS."""
    query = {}
    if statut:
        query["statut"] = statut
    if type:
        query["type"] = type.upper()
    if niveau:
        query["niveau"] = niveau.upper()
    if q:
        query["$or"] = [
            {"intitule": {"$regex": q, "$options": "i"}},
            {"code": {"$regex": q, "$options": "i"}},
        ]

    skip = (page - 1) * limit
    total = await _db.opc_certifications.count_documents(query)
    docs = await _db.opc_certifications.find(
        query, {"_id": 0}
    ).sort("intitule", 1).skip(skip).limit(limit).to_list(limit)

    return {
        "results": docs,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
    }


# ─── ENDPOINT: Détail d'une certification ─────────────────────────────────────

@router.get("/fiche/{code}")
async def get_certification(code: str):
    """Détail complet d'une fiche RNCP ou RS."""
    code_upper = code.upper()
    cert = await _db.opc_certifications.find_one({"code": code_upper}, {"_id": 0})
    if not cert:
        raise HTTPException(status_code=404, detail=f"Certification {code_upper} non trouvée")

    # Blocs de compétences
    blocs = await _db.opc_blocs_competences.find(
        {"code_certification": code_upper}, {"_id": 0}
    ).to_list(100)

    # Codes ROME associés
    rome_codes = await _db.opc_rncp_rome.find(
        {"code_certification": code_upper}, {"_id": 0}
    ).to_list(50)

    # Certificateurs
    certificateurs = await _db.opc_certificateurs.find(
        {"code_certification": code_upper}, {"_id": 0}
    ).to_list(20)

    return {
        **cert,
        "blocs_competences": blocs,
        "codes_rome": rome_codes,
        "certificateurs": certificateurs,
    }


# ─── ENDPOINT: Blocs de compétences ──────────────────────────────────────────

@router.get("/fiche/{code}/blocs")
async def get_blocs(code: str):
    """Liste des blocs de compétences d'une certification."""
    code_upper = code.upper()
    blocs = await _db.opc_blocs_competences.find(
        {"code_certification": code_upper}, {"_id": 0}
    ).to_list(100)
    return {"code": code_upper, "blocs": blocs, "count": len(blocs)}


# ─── ENDPOINT: Mapping RNCP ↔ ROME ───────────────────────────────────────────

@router.get("/rome/{code_rome}")
async def get_certifications_by_rome(code_rome: str, statut: str = "ACTIVE"):
    """Trouver les certifications RNCP liées à un code ROME."""
    mappings = await _db.opc_rncp_rome.find(
        {"code_rome": code_rome.upper()}, {"_id": 0}
    ).to_list(200)

    if not mappings:
        return {"code_rome": code_rome, "certifications": [], "count": 0}

    cert_codes = [m["code_certification"] for m in mappings]
    query = {"code": {"$in": cert_codes}}
    if statut:
        query["statut"] = statut

    certs = await _db.opc_certifications.find(query, {"_id": 0}).to_list(200)

    return {
        "code_rome": code_rome,
        "libelle_rome": mappings[0].get("libelle_rome", ""),
        "certifications": certs,
        "count": len(certs),
    }


# ─── ENDPOINT: Statistiques RNCP ─────────────────────────────────────────────

@router.get("/stats")
async def get_rncp_stats():
    """Statistiques globales RNCP/RS."""
    total = await _db.opc_certifications.count_documents({})
    active = await _db.opc_certifications.count_documents({"statut": "ACTIVE"})
    rncp = await _db.opc_certifications.count_documents({"type": "RNCP", "statut": "ACTIVE"})
    rs = await _db.opc_certifications.count_documents({"type": "RS", "statut": "ACTIVE"})
    blocs = await _db.opc_blocs_competences.count_documents({})
    rome_mappings = await _db.opc_rncp_rome.count_documents({})

    # By level
    pipeline = [
        {"$match": {"statut": "ACTIVE", "type": "RNCP"}},
        {"$group": {"_id": "$niveau_libelle", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    levels = await _db.opc_certifications.aggregate(pipeline).to_list(20)

    # ETL metadata
    meta = await _db.opc_etl_metadata.find_one(
        {"source": "rncp_france_competences"}, {"_id": 0}
    )

    return {
        "total_certifications": total,
        "actives": active,
        "rncp_actives": rncp,
        "rs_actives": rs,
        "blocs_competences": blocs,
        "mappings_rome": rome_mappings,
        "par_niveau": {l["_id"] or "Non renseigné": l["count"] for l in levels},
        "derniere_importation": meta.get("last_import") if meta else None,
        "source": "France Compétences (data.gouv.fr)",
    }


# ─── ENDPOINT: Analyse des écarts (Gap Analysis) ─────────────────────────────

@router.post("/gap-analysis")
async def gap_analysis(body: GapAnalysisRequest):
    """
    Compare les compétences d'un utilisateur avec les blocs
    d'une certification RNCP pour identifier les écarts.
    """
    code = body.code_rncp.upper()
    cert = await _db.opc_certifications.find_one({"code": code}, {"_id": 0})
    if not cert:
        raise HTTPException(status_code=404, detail=f"Certification {code} non trouvée")

    blocs = await _db.opc_blocs_competences.find(
        {"code_certification": code}, {"_id": 0}
    ).to_list(100)

    # Simple matching: check if user competences overlap with bloc titles
    user_comps_lower = [c.lower() for c in body.competences_utilisateur]
    matched_blocs = []
    missing_blocs = []

    for bloc in blocs:
        bloc_title = bloc.get("intitule", "").lower()
        matched = any(comp in bloc_title for comp in user_comps_lower)
        if matched:
            matched_blocs.append(bloc)
        else:
            missing_blocs.append(bloc)

    total_blocs = len(blocs)
    coverage = (len(matched_blocs) / total_blocs * 100) if total_blocs > 0 else 0

    return {
        "certification": cert,
        "total_blocs": total_blocs,
        "blocs_maitrises": len(matched_blocs),
        "blocs_manquants": len(missing_blocs),
        "couverture_pct": round(coverage, 1),
        "detail_maitrises": matched_blocs,
        "detail_manquants": missing_blocs,
        "plan_action": f"Vous maîtrisez {len(matched_blocs)}/{total_blocs} blocs de la certification {cert.get('intitule', code)}. "
                       f"Il reste {len(missing_blocs)} bloc(s) à acquérir pour obtenir cette certification."
                       if total_blocs > 0 else "Aucun bloc de compétences enregistré pour cette certification.",
    }


# ─── ENDPOINT: Top certifications en tension (territorial) ───────────────────

@router.get("/tension")
async def get_certifications_en_tension(
    territoire: str = Query("Grand Est", description="Territoire cible"),
    limit: int = Query(10, ge=1, le=50),
):
    """
    Certifications les plus demandées (basé sur le nombre de codes ROME associés
    et le statut actif) — proxy de tension.
    """
    pipeline = [
        {"$group": {"_id": "$code_certification", "nb_rome": {"$sum": 1}}},
        {"$sort": {"nb_rome": -1}},
        {"$limit": limit * 2},
    ]
    rome_counts = await _db.opc_rncp_rome.aggregate(pipeline).to_list(limit * 2)

    results = []
    for item in rome_counts:
        code = item["_id"]
        cert = await _db.opc_certifications.find_one(
            {"code": code, "statut": "ACTIVE"}, {"_id": 0}
        )
        if cert:
            results.append({
                **cert,
                "nb_metiers_associes": item["nb_rome"],
            })
            if len(results) >= limit:
                break

    return {
        "territoire": territoire,
        "certifications_en_tension": results,
        "count": len(results),
    }
