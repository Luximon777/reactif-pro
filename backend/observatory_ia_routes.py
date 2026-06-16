"""
OPC — Routes IA pour les onglets Analyser / Anticiper / Orienter
Endpoints appelés par OpcView.jsx via runIa()
Utilise Claude Sonnet 4.5 via Emergent LLM Key pour générer des analyses métier.
"""

import os
import json
import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from fastapi import APIRouter, Query
from pydantic import BaseModel
import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/observatory", tags=["Observatory IA"])

# ─── DB ───────────────────────────────────────────────────────────────────────
_client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGO_URL"])
_db = _client[os.environ.get("DB_NAME", "test_database")]


# ─── Request model ────────────────────────────────────────────────────────────
class IaRequest(BaseModel):
    contexte_metier: Optional[str] = None


# ─── Helper: fetch metier context from DB ─────────────────────────────────────
async def _get_metier_context(query: str) -> Dict[str, Any]:
    """Fetch metier data from opc_metiers, rome_metiers, and RNCP to enrich IA prompts."""
    ctx: Dict[str, Any] = {"query": query, "metier": None, "rome": None, "filiere": None, "rncp": []}
    if not query:
        return ctx

    q_re = {"$regex": query, "$options": "i"}

    # Search opc_metiers (rich internal data)
    metier = await _db.opc_metiers.find_one({"metier": q_re}, {"_id": 0})
    if not metier:
        metier = await _db.opc_metiers.find_one(
            {"$or": [{"savoir_faire": q_re}, {"mission": q_re}]}, {"_id": 0}
        )
    ctx["metier"] = metier

    # Search rome_metiers (official ROME codes)
    rome = await _db.rome_metiers.find_one({"libelle": q_re}, {"_id": 0})
    ctx["rome"] = rome

    # Get filiere info
    if metier:
        filiere = await _db.opc_filieres.find_one(
            {"code": metier.get("filiere_code")}, {"_id": 0}
        )
        ctx["filiere"] = filiere

    # Search RNCP certifications linked to this métier
    rncp_certs = []
    if rome and rome.get("code_rome"):
        # Find RNCP via ROME mapping
        mappings = await _db.opc_rncp_rome.find(
            {"code_rome": rome["code_rome"]}, {"_id": 0}
        ).limit(10).to_list(10)
        cert_codes = [m["code_certification"] for m in mappings]
        if cert_codes:
            certs = await _db.opc_certifications.find(
                {"code": {"$in": cert_codes}, "statut": "ACTIVE"}, {"_id": 0}
            ).limit(5).to_list(5)
            rncp_certs = certs
    if not rncp_certs:
        # Fallback: search by intitulé
        certs = await _db.opc_certifications.find(
            {"intitule": q_re, "statut": "ACTIVE"}, {"_id": 0}
        ).limit(5).to_list(5)
        rncp_certs = certs
    ctx["rncp"] = rncp_certs

    return ctx


def _build_metier_prompt_block(ctx: Dict[str, Any]) -> str:
    """Build a context block from DB data to inject into IA prompts."""
    parts = []
    m = ctx.get("metier")
    if m:
        parts.append(f"Métier : {m.get('metier', ctx['query'])}")
        parts.append(f"Filière : {m.get('filiere_nom', 'N/A')} — Secteur : {m.get('sector_name', 'N/A')}")
        if m.get("mission"):
            parts.append(f"Mission : {m['mission']}")
        if m.get("savoir_faire"):
            parts.append(f"Savoir-faire : {', '.join(m['savoir_faire'][:8])}")
        if m.get("savoir_etre"):
            parts.append(f"Savoir-être : {', '.join(m['savoir_etre'][:8])}")
        if m.get("capacites_techniques"):
            parts.append(f"Capacités techniques (extrait) : {m['capacites_techniques'][0][:120]}")
    else:
        parts.append(f"Métier recherché : {ctx['query']}")

    r = ctx.get("rome")
    if r:
        parts.append(f"Code ROME : {r.get('code_rome', 'N/A')} — {r.get('libelle', '')}")
        parts.append(f"Grand domaine ROME : {r.get('grand_domaine_nom', 'N/A')}")

    # RNCP certifications
    rncp = ctx.get("rncp", [])
    if rncp:
        rncp_list = [f"{c.get('code', '')} {c.get('intitule', '')} ({c.get('niveau_libelle', '')})" for c in rncp[:5]]
        parts.append(f"Certifications RNCP associées : {'; '.join(rncp_list)}")

    return "\n".join(parts)


# ─── Helper: call Claude Sonnet 4.5 ──────────────────────────────────────────
async def _call_claude(system_msg: str, prompt: str, session_suffix: str = "") -> Optional[str]:
    """Call Claude Sonnet 4.5 via Emergent LLM Key. Returns raw text or None."""
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        logger.warning("[OPC IA] EMERGENT_LLM_KEY manquante")
        return None
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        chat = LlmChat(
            api_key=api_key,
            session_id=f"opc-ia-{session_suffix}-{uuid.uuid4().hex[:8]}",
            system_message=system_msg,
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        reply = await chat.send_message(UserMessage(text=prompt))
        return reply.strip() if isinstance(reply, str) else None
    except Exception as e:
        logger.error(f"[OPC IA] Erreur Claude: {e}")
        return None


def _parse_json(text: Optional[str]) -> Any:
    """Extract JSON from Claude response (handles ```json blocks)."""
    if not text:
        return None
    txt = text.strip()
    if txt.startswith("```"):
        lines = txt.split("\n")
        # Remove first and last ``` lines
        start = 1
        if lines[0].strip().startswith("```"):
            start = 1
        end = len(lines)
        for i in range(len(lines) - 1, 0, -1):
            if lines[i].strip().startswith("```"):
                end = i
                break
        txt = "\n".join(lines[start:end]).strip()
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        # Try to find JSON in the text
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            s = txt.find(start_char)
            e = txt.rfind(end_char)
            if s != -1 and e != -1 and e > s:
                try:
                    return json.loads(txt[s:e + 1])
                except json.JSONDecodeError:
                    continue
        logger.warning(f"[OPC IA] JSON parse failed: {txt[:200]}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 1: Corrélations compétences techniques ↔ savoir-être
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/ia/correlations")
async def ia_correlations(body: IaRequest = IaRequest(), token: str = None):
    ctx = await _get_metier_context(body.contexte_metier or "")
    context_block = _build_metier_prompt_block(ctx)

    system = (
        "Tu es l'IA analytique de l'Observatoire Prédictif des Compétences (OPC) RE'ACTIF PRO. "
        "Tu analyses les corrélations entre compétences techniques (hard skills) et savoir-être (soft skills) "
        "pour un métier donné. Réponds UNIQUEMENT en JSON valide, sans texte autour."
    )

    prompt = f"""Contexte métier :
{context_block}

Analyse les corrélations entre les compétences techniques et les savoir-être professionnels pour ce métier.
Pour chaque compétence technique clé, identifie les savoir-être indispensables et leur niveau d'importance (1 à 5).

Réponds avec un tableau JSON (6 à 8 éléments) au format exact :
[
  {{
    "competence_technique": "Nom de la compétence technique",
    "savoir_etre": [
      {{"nom": "Savoir-être 1", "importance": 4}},
      {{"nom": "Savoir-être 2", "importance": 3}}
    ]
  }}
]

Règles : 
- Chaque item doit avoir 2 à 4 savoir-être associés
- Les savoir-être doivent être pertinents par rapport à la compétence technique
- Importance de 1 (utile) à 5 (indispensable)
- Français uniquement, pas d'emoji"""

    raw = await _call_claude(system, prompt, f"corr-{body.contexte_metier or 'global'}")
    data = _parse_json(raw)

    if isinstance(data, list) and len(data) > 0:
        return data

    # Fallback: build from DB data
    m = ctx.get("metier")
    if m and m.get("savoir_faire") and m.get("savoir_etre"):
        fallback = []
        se_list = m["savoir_etre"][:6]
        for i, sf in enumerate(m["savoir_faire"][:6]):
            fallback.append({
                "competence_technique": sf,
                "savoir_etre": [
                    {"nom": se_list[j % len(se_list)], "importance": 5 - (j % 3)}
                    for j in range(min(3, len(se_list)))
                ]
            })
        return fallback

    return {"error": "Analyse impossible — aucun contexte métier disponible"}


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 2: Détection des compétences émergentes
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/ia/detect-emergentes")
async def ia_detect_emergentes(body: IaRequest = IaRequest(), token: str = None):
    ctx = await _get_metier_context(body.contexte_metier or "")
    context_block = _build_metier_prompt_block(ctx)

    # Gather existing emerging skills from DB
    existing_skills = []
    async for s in _db.emerging_skills.find({}, {"_id": 0}).limit(10):
        existing_skills.append(s.get("skill_name", ""))

    system = (
        "Tu es le moteur de détection des compétences émergentes de l'OPC RE'ACTIF PRO. "
        "Tu identifies les nouvelles compétences en progression sur le marché du travail français. "
        "Réponds UNIQUEMENT en JSON valide."
    )

    prompt = f"""Contexte métier :
{context_block}

Signaux déjà détectés sur la plateforme : {', '.join(existing_skills[:5]) if existing_skills else 'aucun'}

Identifie les compétences émergentes pour ce métier ou secteur d'activité.
Prends en compte : IA générative, transition écologique, cybersécurité, numérique, réglementaire.

Réponds avec un tableau JSON (8 à 12 éléments) au format exact :
[
  {{
    "competence": "Nom de la compétence émergente",
    "tendance": "émergente|en hausse|en forte hausse|stable",
    "score_emergence": 85,
    "secteurs": ["Secteur 1", "Secteur 2"]
  }}
]

Règles :
- score_emergence entre 40 et 98
- Trie par score_emergence décroissant
- Inclus des compétences transversales ET spécialisées
- Français uniquement"""

    raw = await _call_claude(system, prompt, f"emerg-{body.contexte_metier or 'global'}")
    data = _parse_json(raw)

    if isinstance(data, list) and len(data) > 0:
        return data

    # Fallback
    return [
        {"competence": "IA générative appliquée", "tendance": "en forte hausse", "score_emergence": 92, "secteurs": ["Numérique", "Management"]},
        {"competence": "Cybersécurité opérationnelle", "tendance": "en hausse", "score_emergence": 87, "secteurs": ["Informatique", "Finance"]},
        {"competence": "Green IT & éco-conception", "tendance": "émergente", "score_emergence": 78, "secteurs": ["Industrie", "Numérique"]},
        {"competence": "Data analyse métier", "tendance": "en hausse", "score_emergence": 75, "secteurs": ["RH", "Commerce"]},
        {"competence": "Accompagnement au changement", "tendance": "stable", "score_emergence": 68, "secteurs": ["RH", "Management"]},
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 3: Trajectoires / passerelles métiers IA
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/ia/trajectoires")
async def ia_trajectoires(body: IaRequest = IaRequest(), token: str = None):
    ctx = await _get_metier_context(body.contexte_metier or "")
    context_block = _build_metier_prompt_block(ctx)

    system = (
        "Tu es l'IA de cartographie des transitions professionnelles de l'OPC RE'ACTIF PRO. "
        "Tu identifies les passerelles métiers réalistes, basées sur la proximité des compétences. "
        "Réponds UNIQUEMENT en JSON valide."
    )

    metier_label = body.contexte_metier or "métier générique"

    prompt = f"""Contexte métier :
{context_block}

Identifie les trajectoires professionnelles réalistes depuis le métier « {metier_label} » vers d'autres métiers.
Prends en compte :
- La proximité des compétences techniques
- Les reconversions fréquemment observées en France
- Les passerelles vers des métiers en tension ou en croissance

Réponds avec un tableau JSON (6 à 8 trajectoires) au format exact :
[
  {{
    "metier_source": "{metier_label}",
    "metier_cible": "Métier cible réaliste",
    "probabilite": 75,
    "justification": "Explication courte (20-30 mots) de la passerelle",
    "competences_manquantes": ["Compétence 1", "Compétence 2"]
  }}
]

Règles :
- probabilite entre 30 et 95 (réaliste)
- Trie par probabilité décroissante
- competences_manquantes : 1 à 4 items
- Métiers cibles concrets et existants en France
- Français uniquement"""

    raw = await _call_claude(system, prompt, f"traj-{metier_label}")
    data = _parse_json(raw)

    if isinstance(data, list) and len(data) > 0:
        return data

    return {"error": "Impossible de générer les trajectoires — réessayez"}


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 4: Recommandation personnalisée
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/ia/recommandation")
async def ia_recommandation(body: IaRequest = IaRequest(), token: str = None):
    ctx = await _get_metier_context(body.contexte_metier or "")
    context_block = _build_metier_prompt_block(ctx)

    # Try to get user profile for personalization
    user_profile = None
    if token:
        tok = await _db.tokens.find_one({"token": token})
        if tok:
            user_profile = await _db.profiles.find_one(
                {"token_id": tok.get("id")}, {"_id": 0}
            )

    profile_block = ""
    if user_profile:
        profile_block = f"""
Profil utilisateur :
- Compétences déclarées : {', '.join((user_profile.get('skills') or [])[:8])}
- Expériences : {len(user_profile.get('experiences') or [])} postes
"""

    # Fetch RNCP certifications for context
    rncp_block = ""
    rncp_certs = ctx.get("rncp", [])
    if rncp_certs:
        rncp_lines = [f"- {c.get('code','')} : {c.get('intitule','')} ({c.get('niveau_libelle','')})" for c in rncp_certs[:5]]
        rncp_block = f"\nCertifications RNCP disponibles pour ce métier :\n" + "\n".join(rncp_lines)

    system = (
        "Tu es le conseiller en orientation de l'OPC RE'ACTIF PRO. "
        "Tu génères des recommandations personnalisées d'orientation professionnelle. "
        "Réponds UNIQUEMENT en JSON valide."
    )

    prompt = f"""Contexte métier :
{context_block}
{profile_block}
{rncp_block}

Génère une recommandation complète d'orientation professionnelle.

Réponds avec un objet JSON au format exact :
{{
  "plan_action": "Synthèse du plan d'action en 2-3 phrases (français institutionnel, 40-60 mots)",
  "metiers_accessibles": [
    {{"metier": "Nom du métier", "adequation": 85}}
  ],
  "metiers_evolution": [
    {{"metier": "Nom du métier", "duree": "6 à 12 mois"}}
  ],
  "competences_prioritaires": [
    {{"competence": "Compétence à développer", "urgence": "haute|moyenne"}}
  ],
  "savoir_etre_a_renforcer": [
    {{"savoir_etre": "Savoir-être", "contexte": "Pourquoi et dans quel contexte"}}
  ],
  "certifications_conseillees": [
    {{"code_rncp": "RNCP12345", "intitule": "Titre de la certification", "niveau": "Niveau X", "pertinence": "Pourquoi cette certification est pertinente (15-20 mots)"}}
  ]
}}

Règles :
- 3 à 5 métiers accessibles (adequation 50-95)
- 2 à 3 métiers avec montée en compétences
- 3 à 5 compétences prioritaires
- 2 à 4 savoir-être à renforcer
- 2 à 4 certifications RNCP conseillées (si disponibles dans le contexte, utilise les codes fournis)
- Basé sur le marché français actuel
- Français uniquement"""

    raw = await _call_claude(system, prompt, f"reco-{body.contexte_metier or 'global'}")
    data = _parse_json(raw)

    if isinstance(data, dict) and data.get("plan_action"):
        return data

    return {"error": "Impossible de générer la recommandation — réessayez"}


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 5: Prédictions globales compétences
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/predict-competences")
async def predict_competences(body: IaRequest = IaRequest(), token: str = None):
    ctx = await _get_metier_context(body.contexte_metier or "")
    context_block = _build_metier_prompt_block(ctx)

    # Stats from DB
    nb_profils = await _db.profiles.count_documents({})
    nb_metiers_opc = await _db.opc_metiers.count_documents({})
    nb_rome = await _db.rome_metiers.count_documents({})

    system = (
        "Tu es le moteur prédictif de l'OPC RE'ACTIF PRO. "
        "Tu produis des prévisions sur l'évolution des compétences et des métiers. "
        "Réponds UNIQUEMENT en JSON valide."
    )

    focus = f"pour le métier « {body.contexte_metier} »" if body.contexte_metier else "à l'échelle territoriale (Grand Est)"

    prompt = f"""Contexte :
{context_block}

Données plateforme : {nb_profils} profils, {nb_metiers_opc} métiers OPC, {nb_rome} fiches ROME.

Produis une analyse prédictive {focus}.

Réponds avec un objet JSON au format exact :
{{
  "synthese": "Synthèse prédictive en 2-3 phrases (40-60 mots, français institutionnel)",
  "tendances_competences": [
    {{
      "competence": "Nom de la compétence",
      "direction": "hausse|baisse|stable",
      "explication": "Explication courte (15-25 mots)"
    }}
  ],
  "metiers_en_tension": [
    {{
      "metier": "Nom du métier",
      "niveau_tension": "élevé|modéré|faible",
      "horizon": "6 mois|1 an|3 ans"
    }}
  ]
}}

Règles :
- 6 à 10 tendances de compétences (mix hausse/baisse/stable)
- 4 à 6 métiers en tension
- Basé sur le marché français réel
- Français uniquement, aucune emoji"""

    raw = await _call_claude(system, prompt, f"pred-{body.contexte_metier or 'global'}")
    data = _parse_json(raw)

    if isinstance(data, dict) and data.get("synthese"):
        return data

    # Fallback
    return {
        "synthese": f"L'analyse prédictive {focus} identifie une demande croissante en compétences numériques et en accompagnement au changement. Les métiers de la transition écologique et du numérique concentrent les tensions de recrutement les plus fortes.",
        "tendances_competences": [
            {"competence": "Intelligence artificielle", "direction": "hausse", "explication": "Demande en forte croissance dans tous les secteurs"},
            {"competence": "Cybersécurité", "direction": "hausse", "explication": "Réglementation NIS2 et menaces croissantes"},
            {"competence": "Gestion de projet agile", "direction": "hausse", "explication": "Adoption généralisée des méthodes agiles"},
            {"competence": "Saisie de données", "direction": "baisse", "explication": "Automatisation progressive par l'IA"},
            {"competence": "Communication digitale", "direction": "stable", "explication": "Compétence désormais transversale et acquise"},
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 6: Analyse complète (combine tous les endpoints)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/ia/analyse-complete")
async def ia_analyse_complete(body: IaRequest = IaRequest(), token: str = None):
    """Run all IA analyses and return combined results."""
    import asyncio

    results = await asyncio.gather(
        ia_detect_emergentes(body, token),
        ia_correlations(body, token),
        ia_trajectoires(body, token),
        ia_recommandation(body, token),
        return_exceptions=True,
    )

    emergentes = results[0] if isinstance(results[0], list) else []
    correlations = results[1] if isinstance(results[1], list) else []
    trajectoires = results[2] if isinstance(results[2], list) else []
    recommandation = results[3] if isinstance(results[3], dict) and not results[3].get("error") else None

    return {
        "emergentes": emergentes,
        "correlations": correlations,
        "trajectoires": trajectoires,
        "recommandation": recommandation,
        "contexte_metier": body.contexte_metier,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 7: Preuves terrain S.A.R.E (Situation-Action-Résultat-Enseignement)
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/sare-terrain")
async def get_sare_terrain(limit: int = Query(5, le=20)):
    """Return terrain proofs grouped by soft skill."""
    # Query real terrain observations from opc_terrain
    terrain_docs = await _db.opc_terrain.find(
        {"soft_skills_mentionnes": {"$exists": True, "$ne": []}},
        {"_id": 0}
    ).limit(50).to_list(50)

    # Also check trajectory_steps for SARE data
    traj_docs = await _db.trajectory_steps.find(
        {"skills": {"$exists": True, "$ne": []}},
        {"_id": 0}
    ).limit(50).to_list(50)

    # Group by soft skill
    from collections import defaultdict
    grouped: Dict[str, list] = defaultdict(list)

    for t in terrain_docs:
        for ss in t.get("soft_skills_mentionnes", []):
            grouped[ss].append({
                "poste": t.get("metier_concerne", "Poste non précisé"),
                "sare_situation": t.get("observation", "")[:200],
                "sare_action": t.get("facteur_succes", ""),
                "sare_resultat": t.get("sentiment", ""),
                "sare_enseignement": "",
                "texte_brut": t.get("observation", ""),
            })

    for step in traj_docs:
        for skill in step.get("skills", []):
            grouped[skill].append({
                "poste": step.get("title", step.get("organization", "Expérience")),
                "sare_situation": step.get("description", "")[:200] if step.get("description") else "",
                "sare_action": "",
                "sare_resultat": "",
                "sare_enseignement": "",
                "texte_brut": step.get("description", ""),
            })

    # Build response
    terrain_proofs = []
    for ss, proofs in sorted(grouped.items(), key=lambda x: -len(x[1])):
        terrain_proofs.append({
            "soft_skill": ss,
            "count": len(proofs),
            "proofs": proofs[:3],  # Max 3 proofs per skill
        })
        if len(terrain_proofs) >= limit:
            break

    return {"terrain_proofs": terrain_proofs}
