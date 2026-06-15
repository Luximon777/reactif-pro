"""
OPC — Routes du moteur IA prédictif
"""

from fastapi import APIRouter, BackgroundTasks, Query
from datetime import datetime, timezone, timedelta

from .ia_predictif import (
    analyser_tendances_competences,
    generer_synthese_predictive,
    maj_referentiel_vivant
)
from .db import (
    col_referentiels, col_profils, col_offres
)

router = APIRouter(prefix="/api/opc/ia", tags=["OPC - IA Prédictif"])


@router.get("/tendances")
async def get_tendances(territoire: str = Query("Grand Est")):
    return await analyser_tendances_competences(territoire)


@router.get("/synthese")
async def get_synthese(
    territoire: str = Query("Grand Est"),
    filiere: str = Query(None),
    metier: str = Query(None),
):
    """Synthèse prédictive, optionnellement focalisée sur un métier ou une filière."""
    texte = await generer_synthese_predictive(territoire, filiere=filiere, metier=metier)
    return {"territoire": territoire, "filiere": filiere, "metier": metier, "synthese": texte}


@router.post("/maj-referentiel/{code_rome}")
async def maj_un_referentiel(code_rome: str, intitule_metier: str = Query(...)):
    return await maj_referentiel_vivant(code_rome, intitule_metier)


@router.post("/maj-tous-referentiels")
async def maj_tous_referentiels(background_tasks: BackgroundTasks):
    async def _run():
        count = 0
        async for ref in col_referentiels().find({}, {"code_rome": 1, "intitule_metier": 1}):
            await maj_referentiel_vivant(ref["code_rome"], ref["intitule_metier"])
            count += 1
        print(f"[OPC IA] {count} référentiels mis à jour")

    background_tasks.add_task(_run)
    return {"status": "lancement",
            "message": "Mise à jour des référentiels lancée en arrière-plan"}


@router.get("/kpis-confiance")
async def get_kpis_confiance():
    total_profils = await col_profils().count_documents({})
    profils_dclic = await col_profils().count_documents({"resultats_dclic": {"$ne": None}})
    profils_preuves = await col_profils().count_documents({
        "soft_skills_prouves": {"$exists": True, "$not": {"$size": 0}}
    })
    profils_complets = await col_profils().count_documents({
        "competences_techniques": {"$not": {"$size": 0}},
        "metier_vise": {"$ne": None},
        "annees_experience": {"$ne": None}
    })
    offres_recentes = await col_offres().count_documents({
        "date_publication": {"$gte": datetime.now(timezone.utc) - timedelta(days=30)}
    })
    total_offres = await col_offres().count_documents({})

    def pct(a, b):
        return round(a / b * 100, 1) if b > 0 else 0.0

    return {
        "fiabilite_prouvee_pct": pct(profils_preuves, total_profils),
        "completude_profils_pct": pct(profils_complets, total_profils),
        "coherence_parcours_pct": pct(profils_dclic, total_profils),
        "fraicheur_donnees_pct": pct(offres_recentes, total_offres),
        "total_profils": total_profils,
        "calcule_le": datetime.now(timezone.utc).isoformat()
    }
