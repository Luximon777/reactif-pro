"""
OPC — Routes d'administration / intégrations externes
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from datetime import datetime, timezone
from typing import Optional

from .connecteurs.france_travail import (
    FranceTravailClient, GRAND_EST_DEPTS, map_offre_to_opc
)
from .db import col_offres

router = APIRouter(prefix="/api/opc/admin", tags=["OPC - Admin"])


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


@router.get("/france-travail/status")
async def ft_status():
    client = FranceTravailClient()
    if not client.is_configured():
        return {"configured": False, "souscriptions": None}
    souscriptions = await client.check_scopes()
    return {
        "configured": True,
        "client_id_prefix": (client.client_id or "")[:14] + "…",
        "departements_grand_est": GRAND_EST_DEPTS,
        "souscriptions": souscriptions,
        "ready_offres": souscriptions.get("offres_emploi_v2", {}).get("souscrit", False),
        "ready_rome": souscriptions.get("rome_4", {}).get("souscrit", False),
    }


@router.post("/france-travail/sync-rome")
async def ft_sync_rome(background_tasks: BackgroundTasks):
    """Importe les libellés ROME officiels (≈ 600 métiers)."""
    client = FranceTravailClient()
    if not client.is_configured():
        raise HTTPException(400, "FRANCE_TRAVAIL_CLIENT_ID/SECRET non configurés")

    async def _run():
        from .db import col_institutionnel
        try:
            metiers = await client.get_metiers_rome()
            # Stocke dans la collection dédiée pour la recherche full-text
            catalog_col = col_institutionnel().database["opc_rome_catalog"]
            await catalog_col.create_index("code", unique=True)
            await catalog_col.create_index("libelle")
            inserts = 0
            for m in metiers:
                if not m.get("code") or not m.get("libelle"):
                    continue
                res = await catalog_col.update_one(
                    {"code": m["code"]},
                    {"$set": {
                        "code": m["code"],
                        "libelle": m["libelle"],
                        "source": "france_travail",
                        "_synced_at": datetime.now(timezone.utc),
                    }},
                    upsert=True,
                )
                if res.upserted_id:
                    inserts += 1
            await col_institutionnel().update_one(
                {"source": "france_travail", "type_donnee": "referentiel",
                 "titre": "Catalogue ROME 4.0 — France Travail"},
                {"$set": {
                    "source": "france_travail",
                    "type_donnee": "referentiel",
                    "titre": "Catalogue ROME 4.0 — France Travail",
                    "contenu": {"nb_metiers": len(metiers), "nouveaux": inserts},
                    "periode_reference": "2026",
                    "territoire": "France",
                    "_ingested_at": datetime.now(timezone.utc),
                    "validation": {
                        "source": "france_travail", "fiabilite": "haute",
                        "territoire": "France", "niveau_preuve": "prouve",
                        "consentement_rgpd": True, "anonymise": True,
                    },
                }},
                upsert=True,
            )
            print(f"[FT ROME] {len(metiers)} métiers ROME synchronisés ({inserts} nouveaux)")
        except Exception as e:
            print(f"[FT ROME] Erreur : {e}")

    background_tasks.add_task(_run)
    return {"status": "lancement", "message": "Import ROME 4.0 démarré"}


@router.post("/france-travail/sync")
async def ft_sync(
    background_tasks: BackgroundTasks,
    code_rome: Optional[str] = Query(None),
    max_par_dept: int = Query(150, le=150),
    departements: Optional[str] = Query(None, description="CSV ex: '54,57,67'"),
):
    """Lance une synchronisation des offres France Travail en arrière-plan."""
    client = FranceTravailClient()
    if not client.is_configured():
        raise HTTPException(400, "FRANCE_TRAVAIL_CLIENT_ID/SECRET non configurés")

    depts = [d.strip() for d in departements.split(",")] if departements else GRAND_EST_DEPTS

    async def _run():
        total_inseres = 0
        total_majs = 0
        erreurs = []
        for d in depts:
            try:
                data = await client.search_offres(d, range_offres=f"0-{max_par_dept-1}",
                                                  code_rome=code_rome)
                for offre in data.get("resultats", []):
                    doc = map_offre_to_opc(offre, d)
                    doc["date_publication"] = datetime.now(timezone.utc)
                    doc["_ingested_at"] = datetime.now(timezone.utc)
                    if doc.get("_ft_id"):
                        res = await col_offres().update_one(
                            {"_ft_id": doc["_ft_id"]},
                            {"$set": doc},
                            upsert=True,
                        )
                        if res.upserted_id:
                            total_inseres += 1
                        elif res.modified_count:
                            total_majs += 1
            except Exception as e:
                erreurs.append({"departement": d, "error": str(e)[:200]})
        print(f"[FT SYNC] +{total_inseres} nouvelles, ~{total_majs} mises à jour, "
              f"{len(erreurs)} erreurs sur {len(depts)} départements")

    background_tasks.add_task(_run)
    return {
        "status": "lancement",
        "message": f"Synchronisation France Travail démarrée sur {len(depts)} département(s)",
        "departements": depts,
        "code_rome_filtre": code_rome,
        "started_at": _now_iso(),
    }


@router.get("/france-travail/last-sync")
async def ft_last_sync():
    """Statistiques sur les dernières offres France Travail importées."""
    pipeline = [
        {"$match": {"source": "france_travail", "_ft_id": {"$exists": True}}},
        {"$group": {
            "_id": "$code_departement",
            "count": {"$sum": 1},
            "derniere": {"$max": "$_ingested_at"},
        }},
        {"$sort": {"count": -1}},
    ]
    par_dept = []
    async for d in col_offres().aggregate(pipeline):
        par_dept.append({
            "departement": d["_id"],
            "nb_offres": d["count"],
            "derniere_synchro": d["derniere"].isoformat() if d.get("derniere") else None,
        })
    total = sum(d["nb_offres"] for d in par_dept)
    return {"total_offres_ft": total, "par_departement": par_dept}
