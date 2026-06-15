"""
OPC — Moteur IA prédictif
Analyse tendances + mise à jour automatique des référentiels vivants.
Synthèse textuelle générée par Claude Sonnet 4.5 (Emergent LLM key).
"""

import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict
from collections import Counter

from .db import (
    col_offres, col_profils, col_terrain, col_referentiels
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def analyser_tendances_competences(territoire: str = "Grand Est") -> Dict:
    """Compétences en hausse/baisse sur le territoire."""
    demandees: Counter = Counter()
    async for offre in col_offres().find({"localisation": {"$regex": territoire, "$options": "i"}}):
        for c in offre.get("competences_demandees", []):
            demandees[c] += 1
        for c in offre.get("mots_cles_emergents", []):
            demandees[c] += 2

    disponibles: Counter = Counter()
    async for profil in col_profils().find({"territoire": {"$regex": territoire, "$options": "i"}}):
        for c in profil.get("competences_techniques", []):
            disponibles[c] += 1

    terrain_mentions: Counter = Counter()
    async for obs in col_terrain().find({}):
        for c in obs.get("competences_mentionnees", []):
            terrain_mentions[c] += 1

    toutes = set(demandees.keys()) | set(terrain_mentions.keys())
    resultats = []
    for comp in toutes:
        sd = demandees.get(comp, 0)
        st = terrain_mentions.get(comp, 0)
        sp = disponibles.get(comp, 0)
        score_tension = sd + st - sp
        if sd > 0:
            resultats.append({
                "competence": comp,
                "score_demande_marche": sd,
                "score_signal_terrain": st,
                "score_disponibilite_profils": sp,
                "score_tension": score_tension,
                "tendance": "emergente" if score_tension > 3 else (
                    "en_tension" if score_tension > 0 else "equilibree"
                )
            })

    resultats.sort(key=lambda x: x["score_tension"], reverse=True)
    return {
        "territoire": territoire,
        "timestamp": _now().isoformat(),
        "competences_analysees": len(resultats),
        "top_emergentes": [r for r in resultats if r["tendance"] == "emergente"][:10],
        "en_tension": [r for r in resultats if r["tendance"] == "en_tension"][:10],
        "equilibrees": [r for r in resultats if r["tendance"] == "equilibree"][:5]
    }


async def calculer_taux_tension_metier(code_rome: str, territoire: str = "Grand Est") -> float:
    nb_offres = await col_offres().count_documents({
        "code_rome": code_rome,
        "localisation": {"$regex": territoire, "$options": "i"}
    })
    nb_profils = await col_profils().count_documents({
        "code_rome_vise": code_rome,
        "territoire": {"$regex": territoire, "$options": "i"}
    })
    if nb_profils == 0:
        return 100.0 if nb_offres > 0 else 0.0
    return round(min((nb_offres / nb_profils) * 100, 100.0), 1)


async def detecter_competences_emergentes_metier(code_rome: str) -> List[str]:
    depuis_30j = _now() - timedelta(days=30)
    co: Counter = Counter()
    async for o in col_offres().find({
        "code_rome": code_rome,
        "date_publication": {"$gte": depuis_30j}
    }):
        for c in o.get("competences_demandees", []):
            co[c] += 1
        for c in o.get("mots_cles_emergents", []):
            co[c] += 2

    cp: Counter = Counter()
    async for p in col_profils().find({"code_rome_vise": code_rome}):
        for c in p.get("competences_techniques", []):
            cp[c] += 1

    emergentes = [
        c for c, count in co.most_common(20)
        if cp.get(c, 0) < count * 0.3
    ]
    return emergentes[:8]


async def maj_referentiel_vivant(code_rome: str, intitule_metier: str) -> Dict:
    taux = await calculer_taux_tension_metier(code_rome)
    emergentes = await detecter_competences_emergentes_metier(code_rome)

    if taux >= 70:
        statut = "en_transformation"
    elif taux >= 50:
        statut = "en_croissance"
    elif taux >= 20:
        statut = "stable"
    else:
        statut = "en_declin"

    comp_core: Counter = Counter()
    async for o in col_offres().find({"code_rome": code_rome}).limit(100):
        for c in o.get("competences_demandees", []):
            comp_core[c] += 1
    core = [c for c, _ in comp_core.most_common(10)]

    soft: Counter = Counter()
    async for p in col_profils().find({"code_rome_vise": code_rome}).limit(50):
        for s in p.get("soft_skills", []):
            soft[s] += 1
    async for obs in col_terrain().find({"metier_concerne": code_rome}).limit(20):
        for s in obs.get("soft_skills_mentionnes", []):
            soft[s] += 2
    soft_top = [s for s, _ in soft.most_common(5)]

    score_conf = min(
        round((await col_offres().count_documents({"code_rome": code_rome})) / 10, 2),
        1.0
    )

    doc = {
        "code_rome": code_rome,
        "intitule_metier": intitule_metier,
        "statut": statut,
        "competences_core": core,
        "competences_emergentes": emergentes,
        "competences_en_declin": [],
        "soft_skills_prioritaires": soft_top,
        "taux_tension_territorial": taux,
        "horizon_prevision": "3_ans",
        "score_confiance_ia": score_conf,
        "derniere_maj": _now(),
        "territoire": "Grand Est",
        "validation": {
            "source": "moteur_ia_opc",
            "date_collecte": _now(),
            "fiabilite": "haute" if taux > 0 else "faible",
            "territoire": "Grand Est",
            "niveau_preuve": "infere",
            "consentement_rgpd": True,
            "anonymise": True
        }
    }
    await col_referentiels().update_one(
        {"code_rome": code_rome},
        {"$set": doc},
        upsert=True
    )
    return {
        "code_rome": code_rome,
        "statut": statut,
        "taux_tension": taux,
        "competences_emergentes": emergentes,
        "updated_at": _now().isoformat()
    }


# ─── Synthèse prédictive via Claude Sonnet 4.5 ──────────────────────────────

async def generer_synthese_predictive(territoire: str = "Grand Est",
                                       filiere: str = None,
                                       metier: str = None) -> str:
    """
    Génère une synthèse prédictive textuelle via Claude Sonnet 4.5.
    Si filiere est précisé, focalise l'analyse sur cette filière.
    Fallback templating si la clé LLM est manquante ou en cas d'erreur.
    """
    tendances = await analyser_tendances_competences(territoire)
    top_emergentes = [t["competence"] for t in tendances["top_emergentes"][:5]]
    top_tension = [t["competence"] for t in tendances["en_tension"][:5]]

    nb_metiers_tension = await col_referentiels().count_documents({
        "taux_tension_territorial": {"$gte": 50}
    })
    nb_metiers_croissance = await col_referentiels().count_documents({
        "statut": {"$in": ["en_croissance", "en_transformation"]}
    })
    nb_offres = await col_offres().count_documents(
        {"localisation": {"$regex": territoire, "$options": "i"}}
    )
    nb_profils = await col_profils().count_documents(
        {"territoire": {"$regex": territoire, "$options": "i"}}
    )

    # Récupère le label de la filière si demandée
    filiere_label = None
    if filiere:
        try:
            from .referentiel_metiers import FILIERES_REFERENTIEL
            for f in FILIERES_REFERENTIEL:
                if f["key"] == filiere:
                    filiere_label = f["label"]
                    break
        except Exception:
            pass

    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        return _synthese_template(territoire, nb_metiers_tension, top_emergentes, top_tension, filiere_label)

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        if metier:
            prompt = (
                f"Tu es l'IA prédictive de l'Observatoire des Compétences RE'ACTIF PRO d'ALT&ACT "
                f"pour la région {territoire}.\n\n"
                f"Produis une analyse prédictive du métier : « {metier} ».\n\n"
                "Mobilise ta connaissance générale du marché du travail français et de la région "
                f"{territoire}. Structure ta réponse en 3 paragraphes courts (max 130 mots au total) :\n"
                f"1. État actuel et niveau de tension du métier en {territoire} (recrutement, démographie, attractivité).\n"
                "2. Compétences émergentes ou en transformation pour ce métier (technologies, "
                "réglementations, attentes employeurs récentes).\n"
                "3. Recommandation opérationnelle pour les acteurs territoriaux "
                "(orientations, formations à mobiliser, signaux à surveiller).\n\n"
                "Style : français institutionnel et factuel. Aucune emoji. Aucune liste à puces. "
                "Aucune mention du modèle ou de l'IA générative. Présente les éléments comme "
                "une analyse de l'Observatoire."
            )
            session_suffix = f"-metier-{metier[:30]}"
        else:
            focus_filiere = ""
            if filiere_label:
                focus_filiere = f"\nFocus demandé : {filiere_label}. Centre l'analyse sur cette filière uniquement.\n"
            prompt = (
                f"Tu es l'IA de synthèse de l'Observatoire Prédictif des Compétences (OPC) "
                f"de la plateforme RE'ACTIF PRO d'ALT&ACT pour la région {territoire}.\n"
                f"{focus_filiere}\n"
                f"Données réellement disponibles en base (à ce jour) :\n"
                f"- {nb_profils} profil(s) utilisateur actif(s)\n"
                f"- {nb_offres} offre(s) d'emploi en base\n"
                f"- {nb_metiers_tension} métier(s) sous forte tension de recrutement\n"
                f"- {nb_metiers_croissance} métier(s) en croissance ou transformation\n"
                f"- Compétences émergentes prioritaires : {', '.join(top_emergentes) or 'aucune détectée'}\n"
                f"- Compétences en tension : {', '.join(top_tension) or 'aucune détectée'}\n\n"
                "Règles strictes :\n"
                "1. Tu ne dois citer AUCUN chiffre, métier, secteur ou compétence qui ne soit pas dans la liste ci-dessus.\n"
                "2. Si les compteurs sont à zéro ou très bas, indique-le honnêtement et précise qu'on attend "
                "l'ingestion des sources officielles (France Travail, partenaires) pour produire l'analyse complète.\n"
                "3. Pas de chiffres inventés, pas de moyennes nationales, pas de projections génériques.\n\n"
                "Rédige une synthèse de 2 à 3 paragraphes courts (max 110 mots au total), "
                "en français institutionnel et factuel, sans emoji, sans liste à puces."
            )
            session_suffix = f"-{filiere}" if filiere else ""
        chat = LlmChat(
            api_key=api_key,
            session_id=f"opc-synthese-{territoire}{session_suffix}",
            system_message="Tu es l'IA prédictive d'un observatoire des compétences territorial français."
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        reply = await chat.send_message(UserMessage(text=prompt))
        if isinstance(reply, str) and reply.strip():
            return reply.strip()
        return _synthese_template(territoire, nb_metiers_tension, top_emergentes, top_tension, filiere_label)
    except Exception as e:
        print(f"[OPC IA] Erreur synthèse Claude : {e}")
        return _synthese_template(territoire, nb_metiers_tension, top_emergentes, top_tension, filiere_label)


def _synthese_template(territoire, nb_tension, top_emergentes, top_tension, filiere_label=None) -> str:
    portee = f"sur le territoire {territoire}"
    if filiere_label:
        portee += f", filière {filiere_label}"
    s = f"Synthèse {portee} : "
    if nb_tension > 0:
        s += f"{nb_tension} métier(s) restent sous forte tension de recrutement. "
    if top_emergentes:
        s += f"Les compétences émergentes prioritaires sont : {', '.join(top_emergentes[:3])}. "
    if top_tension:
        s += f"Les compétences les plus recherchées sans profils disponibles : {', '.join(top_tension[:3])}. "
    s += "Une montée en compétences ciblée sur ces axes permettrait de réduire significativement les tensions territoriales."
    return s
