"""
OPC — 4 vues par public
GET /api/opc/vue/particulier/{user_id}
GET /api/opc/vue/rh/{entreprise_id}
GET /api/opc/vue/conseiller
GET /api/opc/vue/institution
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timezone

from .db import (
    col_profils, col_entreprises, col_offres, col_formations,
    col_institutionnel, col_terrain, col_parcours, col_referentiels
)
from .filieres import FILIERES, filiere_pour_rome
from .referentiel_metiers import (
    all_filieres, find_metier, find_metier_by_label, slugify,
    search_metiers, code_rome_for_label, FILIERES_REFERENTIEL
)

router = APIRouter(prefix="/api/opc/vue", tags=["OPC - Vues publics"])


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _strip_id(d: dict) -> dict:
    if d and "_id" in d:
        d["_id"] = str(d["_id"])
    return d


# ─── Catalogue Filières / Secteurs / Métiers (recherche hiérarchique) ─────

@router.get("/filieres")
async def liste_filieres(territoire: str = Query("Grand Est")):
    """
    Renvoie l'arborescence officielle RE'ACTIF (20 filières → secteurs → métiers)
    fusionnée avec les données MongoDB (référentiels vivants + profils utilisateurs).
    """
    # Index des métiers présents en base (par label normalisé)
    profil_by_label = {}
    async for p in col_profils().find(
        {"metier_vise": {"$ne": None},
         "territoire": {"$regex": territoire, "$options": "i"}},
        {"user_id": 1, "metier_vise": 1, "code_rome_vise": 1}
    ):
        if p.get("metier_vise") and not str(p["metier_vise"]).startswith("TEST"):
            profil_by_label[slugify(p["metier_vise"])] = {
                "user_id": p["user_id"],
                "code_rome": p.get("code_rome_vise"),
            }

    ref_by_label = {}
    async for r in col_referentiels().find(
        {"territoire": {"$regex": territoire, "$options": "i"}},
        {"code_rome": 1, "intitule_metier": 1, "statut": 1, "taux_tension_territorial": 1}
    ):
        if r.get("intitule_metier") and not str(r["intitule_metier"]).startswith("Test"):
            ref_by_label[slugify(r["intitule_metier"])] = {
                "code_rome": r.get("code_rome"),
                "statut": r.get("statut"),
                "taux_tension": r.get("taux_tension_territorial"),
            }

    # Construit l'arborescence à partir du référentiel statique
    arbre = all_filieres()
    for f in arbre:
        for s in f["secteurs"]:
            for m in s["metiers"]:
                slug = m["slug"]
                m["user_id"] = profil_by_label.get(slug, {}).get("user_id")
                # Code ROME : prend la valeur du référentiel MongoDB si dispo, sinon profil
                m["code_rome"] = (
                    ref_by_label.get(slug, {}).get("code_rome")
                    or profil_by_label.get(slug, {}).get("code_rome")
                )
                m["statut"] = ref_by_label.get(slug, {}).get("statut")
                m["taux_tension"] = ref_by_label.get(slug, {}).get("taux_tension")
                m["filiere_key"] = f["key"]
                m["filiere_label"] = f["label"]
                m["secteur"] = s["key"]

    return {
        "territoire": territoire,
        "filieres": arbre,
        "total_filieres": len(arbre),
        "total_secteurs": sum(len(f["secteurs"]) for f in arbre),
        "total_metiers": sum(f["nb_metiers"] for f in arbre),
    }


# ─── Catalogue des métiers disponibles (autocomplete) ─────────────────────

@router.get("/metiers-vises")
async def liste_metiers_vises(
    territoire: str = Query("Grand Est"),
    filiere: Optional[str] = Query(None),
    secteur: Optional[str] = Query(None),
):
    """
    Renvoie la liste à plat des métiers, filtrable par filière et/ou secteur.
    """
    tree = await liste_filieres(territoire)
    metiers = []
    for f in tree["filieres"]:
        if filiere and f["key"] != filiere:
            continue
        for s in f["secteurs"]:
            if secteur and s["key"] != secteur:
                continue
            for m in s["metiers"]:
                metiers.append(m)
    metiers.sort(key=lambda x: x["label"].lower())
    return {"territoire": territoire, "metiers": metiers}


# ─── Métiers en lien (passerelles) ───────────────────────────────────────

@router.get("/metiers-lies/{code_rome}")
async def metiers_lies(code_rome: str, territoire: str = Query("Grand Est")):
    """
    Métiers en lien avec un ROME donné :
    - Trajectoires compatibles (depuis le référentiel)
    - Métiers du même secteur d'activité
    """
    ref = await col_referentiels().find_one({"code_rome": code_rome})
    trajectoires = []
    secteur_principal = None

    if ref:
        for c in ref.get("trajectoires_compatibles", [])[:6]:
            r = await col_referentiels().find_one({"code_rome": c})
            if r:
                trajectoires.append({
                    "code_rome": r["code_rome"],
                    "intitule": r["intitule_metier"],
                    "statut": r["statut"],
                    "taux_tension": r.get("taux_tension_territorial"),
                    "lien": "trajectoire"
                })

    # Secteur dominant pour ce ROME
    async for s in col_offres().aggregate([
        {"$match": {"code_rome": code_rome, "secteur": {"$ne": None}}},
        {"$group": {"_id": "$secteur", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}, {"$limit": 1}
    ]):
        secteur_principal = s["_id"]

    meme_secteur = []
    if secteur_principal:
        vus = set()
        async for o in col_offres().aggregate([
            {"$match": {"secteur": secteur_principal,
                        "code_rome": {"$ne": code_rome, "$ne": None}}},
            {"$group": {"_id": "$code_rome", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}, {"$limit": 12}
        ]):
            rome = o["_id"]
            if rome in vus:
                continue
            vus.add(rome)
            r = await col_referentiels().find_one({"code_rome": rome})
            meme_secteur.append({
                "code_rome": rome,
                "intitule": r["intitule_metier"] if r else rome,
                "statut": r["statut"] if r else None,
                "taux_tension": r.get("taux_tension_territorial") if r else None,
                "nb_offres": o["count"],
                "lien": "meme_secteur"
            })
            if len(meme_secteur) >= 6:
                break

    return {
        "code_rome": code_rome,
        "secteur_principal": secteur_principal,
        "trajectoires_compatibles": trajectoires,
        "metiers_meme_secteur": meme_secteur,
    }


@router.get("/recherche-metier")
async def recherche_metier(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, le=50),
):
    """
    Recherche full-text dans :
    1. Les 284 métiers du référentiel hiérarchisé RE'ACTIF (avec filière + secteur)
    2. Les 1584 métiers ROME 4.0 importés depuis France Travail (codes officiels)
    Dédupliqué par code ROME.
    """
    # Référentiel statique RE'ACTIF
    results = search_metiers(q, limit=limit)
    seen_romes = {r.get("code_rome") for r in results if r.get("code_rome")}

    # Catalogue ROME officiel France Travail (si importé)
    q_lc = q.lower()
    async for doc in col_institutionnel().find(
        {"source": "france_travail", "type_donnee": "referentiel",
         "titre": {"$regex": "ROME 4.0", "$options": "i"}}
    ).limit(2):
        # Le catalogue complet est trop gros pour le contenu : on relance un lookup direct
        pass
    # Recherche directe dans la collection dédiée si présente
    catalog_col = col_institutionnel().database["opc_rome_catalog"]
    async for m in catalog_col.find(
        {"$or": [
            {"libelle": {"$regex": q, "$options": "i"}},
            {"code": {"$regex": f"^{q.upper()}", "$options": "i"}},
        ]}
    ).limit(limit):
        if m.get("code") in seen_romes:
            continue
        results.append({
            "label": m.get("libelle"),
            "slug": slugify(m.get("libelle", "")),
            "filiere": {"key": "rome", "code": "ROME", "label": "Catalogue ROME 4.0"},
            "secteur": {"key": "rome", "label": "France Travail"},
            "mission": None,
            "code_rome": m.get("code"),
            "score": 3 if q_lc in (m.get("libelle") or "").lower() else 1,
            "_source": "france_travail",
        })
        seen_romes.add(m.get("code"))
    results.sort(key=lambda x: -x["score"])
    return {"query": q, "count": len(results[:limit]), "results": results[:limit]}


async def _generate_fiche_via_claude(label: str, filiere_label: str, secteur_label: str):
    """Génère mission + capacités + savoirs-être via Claude Sonnet 4.5. None si erreur."""
    import os
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        return None
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        prompt = (
            f"Tu es l'IA de référentiel métier RE'ACTIF PRO. "
            f"Rédige une fiche pour le métier suivant en JSON strict (français institutionnel, aucune emoji) :\n\n"
            f"Métier : {label}\nFilière : {filiere_label}\nSecteur : {secteur_label}\n\n"
            "Réponds UNIQUEMENT avec un objet JSON valide à plat ayant exactement ces 4 clés :\n"
            '{\n'
            '  "mission": "Une phrase de 20 à 35 mots décrivant la mission centrale.",\n'
            '  "techniques": ["compétence technique 1", "...", "5 à 7 items précis au métier"],\n'
            '  "savoirs_etre": ["3 à 5 savoirs-être adaptés"],\n'
            '  "professionnelles": ["3 capacités professionnelles concrètes (verbes d\'action)"]\n'
            '}\nAucune balise, aucun texte autour, juste le JSON.'
        )
        chat = LlmChat(
            api_key=api_key,
            session_id=f"opc-fiche-{label[:30]}",
            system_message="Tu génères des fiches métier au format JSON strict."
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        reply = await chat.send_message(UserMessage(text=prompt))
        if not isinstance(reply, str):
            return None
        import json
        txt = reply.strip()
        if txt.startswith("```"):
            txt = txt.split("```")[1]
            if txt.startswith("json"):
                txt = txt[4:]
            txt = txt.strip().rstrip("`").strip()
        return json.loads(txt)
    except Exception as e:
        print(f"[Claude fiche] erreur {label}: {e}")
        return None


# ─── Fiche métier (mission + capacités + savoirs-être) ──────────────────

@router.get("/metier-details")
async def metier_details(
    slug: Optional[str] = Query(None),
    label: Optional[str] = Query(None),
):
    """Retourne la fiche complète d'un métier (mission + capacités + savoirs-être + qualités humaines).
    Si le métier n'a pas de détail statique, génère via Claude Sonnet 4.5 (avec cache MongoDB)."""
    if not slug and not label:
        raise HTTPException(400, "Fournir slug ou label")
    detail = find_metier(slug) if slug else find_metier_by_label(label)
    if not detail:
        raise HTTPException(404, f"Métier introuvable : {slug or label}")

    # Détection : capacités génériques par défaut → on tente Claude
    from .referentiel_metiers import CAPACITES_DEFAUT, METIERS_DETAILS
    metier_slug = detail["slug"]
    static_entry = METIERS_DETAILS.get(metier_slug, {})
    # Considère "complet" seulement si techniques + savoirs_etre spécifiques sont fournis
    has_complete_static = bool(static_entry.get("techniques") and static_entry.get("savoirs_etre"))
    if not has_complete_static:
        # Cache MongoDB
        cache_col = col_institutionnel().database["opc_fiches_ia_cache"]
        cached = await cache_col.find_one({"slug": metier_slug})
        ia_fiche = cached.get("data") if cached else None
        if not ia_fiche:
            ia_fiche = await _generate_fiche_via_claude(
                detail["label"], detail["filiere"]["label"], detail["secteur"]["label"]
            )
            if ia_fiche:
                await cache_col.update_one(
                    {"slug": metier_slug},
                    {"$set": {"slug": metier_slug, "data": ia_fiche,
                              "generated_at": datetime.now(timezone.utc)}},
                    upsert=True,
                )
        if ia_fiche:
            from .referentiel_metiers import QUALITES_HUMAINES
            detail["mission"] = ia_fiche.get("mission") or detail.get("mission")
            detail["capacites_techniques"] = ia_fiche.get("techniques") or detail["capacites_techniques"]
            detail["savoirs_etre"] = ia_fiche.get("savoirs_etre") or detail["savoirs_etre"]
            detail["capacites_professionnelles"] = (
                ia_fiche.get("professionnelles") or detail["capacites_professionnelles"]
            )
            detail["qualites_humaines"] = {
                se: QUALITES_HUMAINES.get(se)
                for se in detail["savoirs_etre"]
                if QUALITES_HUMAINES.get(se)
            }
            detail["_source_fiche"] = "claude-sonnet-4-5"
        else:
            detail["_source_fiche"] = "default-template"
    else:
        detail["_source_fiche"] = "referentiel-statique"

    return detail


# ─── Vue Particulier par métier (résolution → user_id ou anonyme) ────────

@router.get("/particulier-par-metier")
async def vue_particulier_par_metier(
    metier: str = Query(..., min_length=2),
    territoire: str = Query("Grand Est"),
    horizon: str = Query("3_ans")
):
    """
    Trouve un profil démo correspondant au métier (regex insensible),
    sinon construit une vue anonyme à partir du référentiel + offres + formations.
    """
    profil = await col_profils().find_one({
        "metier_vise": {"$regex": metier, "$options": "i"},
        "territoire": {"$regex": territoire, "$options": "i"}
    })
    if profil:
        return await vue_particulier(profil["user_id"], territoire, horizon)

    # Mode anonyme : pas de profil utilisateur, mais référentiel + marché
    referentiel = await col_referentiels().find_one({
        "$or": [
            {"intitule_metier": {"$regex": metier, "$options": "i"}},
            {"code_rome": {"$regex": f"^{metier}$", "$options": "i"}}
        ]
    })

    # Fallback : si pas de référentiel vivant, on utilise le référentiel statique
    fiche = find_metier_by_label(metier) if not referentiel else None

    if not referentiel and not fiche:
        raise HTTPException(404, f"Aucun métier correspondant à « {metier} » trouvé")

    code_rome = None
    if referentiel:
        _strip_id(referentiel)
        code_rome = referentiel.get("code_rome")
    if not code_rome and fiche:
        # Fallback : code ROME issu du mapping statique sur le slug
        code_rome = code_rome_for_label(metier) or fiche.get("code_rome")

    offres = []
    if code_rome:
        async for o in col_offres().find({
            "code_rome": code_rome,
            "localisation": {"$regex": territoire, "$options": "i"}
        }).sort("date_publication", -1).limit(10):
            offres.append(_strip_id(o))

    formations = []
    if code_rome:
        async for f in col_formations().find({
            "codes_rome": code_rome,
            "localisation": {"$regex": territoire, "$options": "i"}
        }).limit(5):
            formations.append(_strip_id(f))

    # Compétences attendues : depuis le marché si code_rome, sinon depuis la fiche métier
    competences_marche = set()
    if code_rome:
        async for o in col_offres().find({"code_rome": code_rome}).limit(50):
            for c in o.get("competences_demandees", []):
                competences_marche.add(c)
    # Fallback fiche métier : on tente d'enrichir via Claude si pas de techniques spécifiques
    if not competences_marche and fiche:
        # Si la fiche a des capacités génériques (slug pas dans METIERS_DETAILS),
        # essaie le cache IA / Claude pour récupérer des compétences spécifiques.
        from .referentiel_metiers import METIERS_DETAILS
        if fiche["slug"] not in METIERS_DETAILS or not METIERS_DETAILS.get(fiche["slug"], {}).get("techniques"):
            cache_col = col_institutionnel().database["opc_fiches_ia_cache"]
            cached = await cache_col.find_one({"slug": fiche["slug"]})
            ia_data = cached.get("data") if cached else None
            if not ia_data:
                ia_data = await _generate_fiche_via_claude(
                    fiche["label"], fiche["filiere"]["label"], fiche["secteur"]["label"]
                )
                if ia_data:
                    await cache_col.update_one(
                        {"slug": fiche["slug"]},
                        {"$set": {"slug": fiche["slug"], "data": ia_data,
                                  "generated_at": datetime.now(timezone.utc)}},
                        upsert=True,
                    )
            if ia_data and ia_data.get("techniques"):
                for c in ia_data["techniques"]:
                    competences_marche.add(c)
        if not competences_marche:
            for c in fiche.get("capacites_techniques", []):
                competences_marche.add(c)

    trajectoires = []
    if referentiel:
        for code in referentiel.get("trajectoires_compatibles", [])[:5]:
            r = await col_referentiels().find_one({"code_rome": code})
            if r:
                trajectoires.append({
                    "code_rome": r["code_rome"],
                    "intitule": r["intitule_metier"],
                    "statut": r["statut"],
                    "horizon": r.get("horizon_prevision"),
                    "taux_tension": r.get("taux_tension_territorial")
                })

    intitule = referentiel["intitule_metier"] if referentiel else (fiche["label"] if fiche else metier)

    return {
        "public": "particulier",
        "user_id": None,
        "anonyme": True,
        "territoire": territoire,
        "horizon": horizon,
        "profil": {
            "metier_vise": intitule,
            "metier_exerce": None,
            "competences_techniques": [],
            "soft_skills": [],
            "soft_skills_prouves": [],
            "projet_reconversion": None,
            "resultats_dclic": None,
            "annees_experience": None
        },
        "referentiel_metier": referentiel,
        "ecart_competences_prioritaires": list(competences_marche)[:10],
        "offres_compatibles": offres,
        "formations_accessibles": formations,
        "trajectoires_conseillees": trajectoires,
        "suivi_parcours": None,
        "generated_at": _now_iso()
    }


# ─── VUE 1 — PARTICULIER ─────────────────────────────────────────────────

@router.get("/particulier/{user_id}")
async def vue_particulier(
    user_id: str,
    territoire: str = Query("Grand Est"),
    horizon: str = Query("3_ans")
):
    profil = await col_profils().find_one({"user_id": user_id})
    if not profil:
        raise HTTPException(404, f"Profil {user_id} introuvable")
    _strip_id(profil)

    code_rome_vise = profil.get("code_rome_vise")
    competences = profil.get("competences_techniques", [])

    referentiel = None
    if code_rome_vise:
        referentiel = await col_referentiels().find_one({"code_rome": code_rome_vise})
        if referentiel:
            _strip_id(referentiel)

    offres_query = {"localisation": {"$regex": territoire, "$options": "i"}}
    if code_rome_vise:
        offres_query["code_rome"] = code_rome_vise
    offres = []
    async for o in col_offres().find(offres_query).sort("date_publication", -1).limit(10):
        offres.append(_strip_id(o))

    formations_query = {"localisation": {"$regex": territoire, "$options": "i"}}
    if code_rome_vise:
        formations_query["codes_rome"] = code_rome_vise
    formations = []
    async for f in col_formations().find(formations_query).limit(5):
        formations.append(_strip_id(f))

    competences_demandees = set()
    if code_rome_vise:
        async for offre in col_offres().find({"code_rome": code_rome_vise}).limit(50):
            for c in offre.get("competences_demandees", []):
                competences_demandees.add(c)
    ecart = list(competences_demandees - set(competences))[:10]

    trajectoires = []
    if referentiel:
        for code in referentiel.get("trajectoires_compatibles", [])[:5]:
            r = await col_referentiels().find_one({"code_rome": code})
            if r:
                trajectoires.append({
                    "code_rome": r["code_rome"],
                    "intitule": r["intitule_metier"],
                    "statut": r["statut"],
                    "horizon": r.get("horizon_prevision"),
                    "taux_tension": r.get("taux_tension_territorial")
                })

    suivi = await col_parcours().find_one({"user_id": user_id})
    if suivi:
        _strip_id(suivi)

    return {
        "public": "particulier",
        "user_id": user_id,
        "territoire": territoire,
        "horizon": horizon,
        "profil": {
            "metier_vise": profil.get("metier_vise"),
            "metier_exerce": profil.get("metier_exerce"),
            "competences_techniques": competences,
            "soft_skills": profil.get("soft_skills", []),
            "soft_skills_prouves": profil.get("soft_skills_prouves", []),
            "projet_reconversion": profil.get("projet_reconversion"),
            "resultats_dclic": profil.get("resultats_dclic"),
            "annees_experience": profil.get("annees_experience")
        },
        "referentiel_metier": referentiel,
        "ecart_competences_prioritaires": ecart,
        "offres_compatibles": offres,
        "formations_accessibles": formations,
        "trajectoires_conseillees": trajectoires,
        "suivi_parcours": suivi,
        "generated_at": _now_iso()
    }


# ─── VUE 2 — RH ──────────────────────────────────────────────────────────

@router.get("/rh/{entreprise_id}")
async def vue_rh(
    entreprise_id: str,
    territoire: str = Query("Grand Est")
):
    entreprise = await col_entreprises().find_one({"entreprise_id": entreprise_id})
    if not entreprise:
        raise HTTPException(404, f"Entreprise {entreprise_id} introuvable")
    _strip_id(entreprise)

    metiers_tension = entreprise.get("metiers_en_tension", [])
    competences_manquantes = entreprise.get("competences_manquantes", [])

    profils_disponibles = []
    if metiers_tension:
        async for p in col_profils().find({
            "metier_vise": {"$in": metiers_tension},
            "territoire": {"$regex": territoire, "$options": "i"}
        }).limit(20):
            profils_disponibles.append({
                "user_id": p["user_id"],
                "metier_vise": p.get("metier_vise"),
                "competences_techniques": p.get("competences_techniques", [])[:5],
                "soft_skills_prouves": p.get("soft_skills_prouves", []),
                "annees_experience": p.get("annees_experience")
            })

    referentiels_tension = []
    for metier in metiers_tension[:5]:
        r = await col_referentiels().find_one({
            "$or": [
                {"intitule_metier": {"$regex": metier, "$options": "i"}},
                {"code_rome": metier}
            ]
        })
        if r:
            referentiels_tension.append(_strip_id(r))

    total_profils = await col_profils().count_documents(
        {"territoire": {"$regex": territoire, "$options": "i"}}
    )
    pc = len(profils_disponibles)
    taux = round((pc / total_profils * 100) if total_profils > 0 else 0, 1)

    formations_gepp = []
    if competences_manquantes:
        async for f in col_formations().find({
            "blocs_competences": {"$in": competences_manquantes},
            "localisation": {"$regex": territoire, "$options": "i"}
        }).limit(5):
            formations_gepp.append(_strip_id(f))

    observations_secteur = []
    secteur = entreprise.get("secteur", "")
    async for t in col_terrain().find({
        "type_source": "recruteur",
        "tags": {"$in": [secteur]}
    }).limit(5):
        observations_secteur.append({
            "observation": t["observation"],
            "sentiment": t.get("sentiment"),
            "competences": t.get("competences_mentionnees", [])
        })

    return {
        "public": "employeur_rh",
        "entreprise_id": entreprise_id,
        "territoire": territoire,
        "entreprise": {
            "secteur": entreprise.get("secteur"),
            "metiers_en_tension": metiers_tension,
            "competences_manquantes": competences_manquantes,
            "besoins_recrutement": entreprise.get("besoins_recrutement", []),
            "besoins_gepp": entreprise.get("besoins_gepp"),
            "taille": entreprise.get("taille")
        },
        "matching": {
            "total_profils_territoire": total_profils,
            "profils_compatibles": pc,
            "taux_matching_pct": taux,
            "profils": profils_disponibles[:10]
        },
        "referentiels_metiers_tension": referentiels_tension,
        "formations_gepp_disponibles": formations_gepp,
        "retours_recruteurs_secteur": observations_secteur,
        "generated_at": _now_iso()
    }


# ─── VUE 3 — CONSEILLER ──────────────────────────────────────────────────

@router.get("/conseiller")
async def vue_conseiller(
    territoire: str = Query("Grand Est"),
    secteur: Optional[str] = Query(None),
    limite_profils: int = Query(50, le=200)
):
    kpis = {
        "profils_actifs": await col_profils().count_documents(
            {"territoire": {"$regex": territoire, "$options": "i"}}
        ),
        "emplois_retrouves": await col_parcours().count_documents(
            {"emploi_retrouve": True, "territoire": {"$regex": territoire, "$options": "i"}}
        ),
        "offres_actives": await col_offres().count_documents(
            {"localisation": {"$regex": territoire, "$options": "i"}}
        ),
        "formations_disponibles": await col_formations().count_documents(
            {"localisation": {"$regex": territoire, "$options": "i"}}
        )
    }
    kpis["taux_retour_emploi_pct"] = round(
        kpis["emplois_retrouves"] / kpis["profils_actifs"] * 100, 1
    ) if kpis["profils_actifs"] > 0 else 0

    pipeline_competences = [
        {"$match": {"localisation": {"$regex": territoire, "$options": "i"}}},
        {"$unwind": "$competences_demandees"},
        {"$group": {"_id": "$competences_demandees", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15}
    ]
    competences_marche = []
    async for c in col_offres().aggregate(pipeline_competences):
        competences_marche.append({"competence": c["_id"], "occurrences": c["count"]})

    metiers_tension = []
    async for r in col_referentiels().find(
        {"taux_tension_territorial": {"$gte": 50}}
    ).sort("taux_tension_territorial", -1).limit(10):
        metiers_tension.append({
            "code_rome": r["code_rome"],
            "intitule": r["intitule_metier"],
            "statut": r["statut"],
            "taux_tension": r.get("taux_tension_territorial"),
            "competences_emergentes": r.get("competences_emergentes", [])[:3]
        })

    observations_recentes = []
    async for t in col_terrain().find({}).sort("_id", -1).limit(10):
        observations_recentes.append({
            "type_source": t["type_source"],
            "metier": t.get("metier_concerne"),
            "observation": t["observation"][:200],
            "sentiment": t.get("sentiment"),
            "competences": t.get("competences_mentionnees", [])
        })

    profils_en_difficulte = []
    async for p in col_profils().find({
        "freins_emploi": {"$exists": True, "$not": {"$size": 0}},
        "territoire": {"$regex": territoire, "$options": "i"}
    }).limit(limite_profils):
        suivi = await col_parcours().find_one({"user_id": p["user_id"]})
        profils_en_difficulte.append({
            "user_id": p["user_id"],
            "metier_vise": p.get("metier_vise"),
            "freins": p.get("freins_emploi", []),
            "emploi_retrouve": suivi.get("emploi_retrouve", False) if suivi else False,
            "soft_skills_prouves": p.get("soft_skills_prouves", [])
        })

    pipeline_maintien = [
        {"$group": {
            "_id": None,
            "maintien_3m": {"$avg": {"$cond": [{"$eq": ["$maintien_3mois", True]}, 1, 0]}},
            "maintien_6m": {"$avg": {"$cond": [{"$eq": ["$maintien_6mois", True]}, 1, 0]}},
            "maintien_12m": {"$avg": {"$cond": [{"$eq": ["$maintien_12mois", True]}, 1, 0]}},
            "total": {"$sum": 1}
        }}
    ]
    maintien_stats = {}
    async for m in col_parcours().aggregate(pipeline_maintien):
        maintien_stats = {
            "maintien_3mois_pct": round((m.get("maintien_3m") or 0) * 100, 1),
            "maintien_6mois_pct": round((m.get("maintien_6m") or 0) * 100, 1),
            "maintien_12mois_pct": round((m.get("maintien_12m") or 0) * 100, 1),
            "total_parcours_suivis": m.get("total", 0)
        }

    return {
        "public": "conseiller_service_emploi",
        "territoire": territoire,
        "kpis_territoire": kpis,
        "competences_les_plus_demandees": competences_marche,
        "metiers_en_tension": metiers_tension,
        "observations_terrain_recentes": observations_recentes,
        "profils_en_difficulte": profils_en_difficulte[:20],
        "efficacite_accompagnements": maintien_stats,
        "generated_at": _now_iso()
    }


# ─── VUE 4 — INSTITUTION ─────────────────────────────────────────────────

@router.get("/institution")
async def vue_institution(
    territoire: str = Query("Grand Est"),
    periode_jours: int = Query(90)
):
    kpis_macro = {
        "total_profils_plateforme": await col_profils().count_documents({}),
        "total_offres_analysees": await col_offres().count_documents({}),
        "total_formations_repertoriees": await col_formations().count_documents({}),
        "total_referentiels_vivants": await col_referentiels().count_documents({}),
        "total_observations_terrain": await col_terrain().count_documents({}),
        "total_parcours_suivis": await col_parcours().count_documents({}),
        "emplois_retrouves_total": await col_parcours().count_documents({"emploi_retrouve": True})
    }

    cartographie = []
    async for t in col_referentiels().aggregate([
        {"$group": {
            "_id": "$statut",
            "count": {"$sum": 1},
            "metiers": {"$push": "$intitule_metier"}
        }},
        {"$sort": {"count": -1}}
    ]):
        cartographie.append({
            "statut": t["_id"],
            "nombre_metiers": t["count"],
            "exemples": t["metiers"][:5]
        })

    competences_emergentes = []
    async for c in col_referentiels().aggregate([
        {"$unwind": "$competences_emergentes"},
        {"$group": {"_id": "$competences_emergentes", "nb_metiers": {"$sum": 1}}},
        {"$sort": {"nb_metiers": -1}},
        {"$limit": 20}
    ]):
        competences_emergentes.append({
            "competence": c["_id"],
            "nb_metiers_concernes": c["nb_metiers"]
        })

    mots_cles_marche = []
    async for m in col_offres().aggregate([
        {"$unwind": "$mots_cles_emergents"},
        {"$group": {"_id": "$mots_cles_emergents", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]):
        mots_cles_marche.append({"mot_cle": m["_id"], "frequence": m["count"]})

    offres_par_secteur = []
    async for s in col_offres().aggregate([
        {"$group": {"_id": "$secteur", "nb_offres": {"$sum": 1}}},
        {"$sort": {"nb_offres": -1}},
        {"$limit": 15}
    ]):
        nb_profils_s = await col_profils().count_documents({
            "metier_vise": {"$regex": s["_id"] or "", "$options": "i"}
        }) if s["_id"] else 0
        offres_par_secteur.append({
            "secteur": s["_id"],
            "nb_offres": s["nb_offres"],
            "nb_profils_disponibles": nb_profils_s,
            "ratio_offres_profils": round(s["nb_offres"] / nb_profils_s, 2) if nb_profils_s > 0 else None
        })

    competences_non_couvertes = []
    async for c in col_offres().aggregate([
        {"$unwind": "$competences_demandees"},
        {"$group": {"_id": "$competences_demandees", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 30}
    ]):
        existe = await col_formations().find_one({"blocs_competences": c["_id"]})
        if not existe:
            competences_non_couvertes.append({
                "competence": c["_id"],
                "demande_marche": c["count"],
                "formation_disponible": False
            })

    sources_disponibles = []
    async for s in col_institutionnel().aggregate([
        {"$group": {"_id": "$source", "count": {"$sum": 1},
                    "derniere_maj": {"$max": "$_ingested_at"}}},
        {"$sort": {"count": -1}}
    ]):
        sources_disponibles.append({
            "source": s["_id"],
            "documents": s["count"],
            "derniere_maj": s["derniere_maj"].isoformat() if s.get("derniere_maj") else None
        })

    return {
        "public": "institution_publique",
        "territoire": territoire,
        "periode_analyse_jours": periode_jours,
        "kpis_macro": kpis_macro,
        "cartographie_tensions_par_statut": cartographie,
        "competences_emergentes_territoriales": competences_emergentes,
        "signaux_marche_mots_cles": mots_cles_marche,
        "adequation_offre_demande_par_secteur": offres_par_secteur,
        "besoins_formation_non_couverts": competences_non_couvertes[:15],
        "sources_institutionnelles_integrees": sources_disponibles,
        "generated_at": _now_iso()
    }
