"""Explorer une nouvelle trajectoire (reconversion) — analyse IA job + polling + cohérence de frise."""
import os
import re
import json
import uuid
import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from database import db, get_current_token, search_word_patterns
from emergentintegrations.llm.chat import LlmChat, UserMessage

router = APIRouter(prefix="/api/trajectoire")
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')


def _sync_llm(chat, message):
    return asyncio.run(chat.send_message(message))


async def _llm(system_message: str, prompt: str, model: str = "gpt-5.2") -> str:
    chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"reconv-{uuid.uuid4()}",
                   system_message=system_message).with_model("openai", model)
    return await asyncio.to_thread(_sync_llm, chat, UserMessage(text=prompt))


def _parse_json(text: str):
    t = (text or "").strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    try:
        return json.loads(t)
    except Exception:
        m = re.search(r"\{.*\}", t, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    return None


def _names(items, limit=15):
    out = []
    for x in (items or [])[:limit]:
        n = x.get("name", "") if isinstance(x, dict) else str(x)
        if n:
            out.append(n)
    return out


async def _gather_profile(token_id: str) -> dict:
    passport = await db.passports.find_one({"token_id": token_id}, {"_id": 0}) or {}
    steps = await db.trajectory_steps.find({"token_id": token_id}, {"_id": 0}).to_list(200)
    steps.sort(key=lambda s: s.get("start_date") or "0000")

    competences = passport.get("competences", [])
    sf = _names(passport.get("savoir_faire", [])) or _names([c for c in competences if isinstance(c, dict) and c.get("nature") == "savoir_faire"])
    se = _names(passport.get("savoir_etre", [])) or _names([c for c in competences if isinstance(c, dict) and c.get("nature") == "savoir_etre"])
    if not sf:
        sf = _names(competences, 20)

    dclic = passport.get("dclic_results", {}) or {}
    if not dclic:
        doc = await db.dclic_results.find_one({"claimed_by": token_id}, {"_id": 0})
        if doc and doc.get("profile"):
            dclic = doc["profile"]
    dclic_txt = ""
    if dclic:
        parts = []
        for k, label in [("mbti", "MBTI"), ("disc", "DISC"), ("riasec", "RIASEC")]:
            if dclic.get(k):
                parts.append(f"{label}: {dclic[k]}")
        fortes = dclic.get("competences_fortes", [])
        if fortes:
            parts.append(f"Compétences fortes: {', '.join(str(c) for c in fortes[:8])}")
        dclic_txt = ". ".join(parts)

    exp_lines = []
    for i, s in enumerate(steps):
        period = f"{s.get('start_date', '?')} → {s.get('end_date') or ('aujourd''hui' if s.get('is_ongoing') else '?')}"
        exp_lines.append(f"{i+1}. [{s.get('step_type', 'emploi')}] {s.get('title', '')} chez {s.get('organization', '') or 'N/A'} ({period}) — {(s.get('description') or '')[:150]}")

    aspirations = passport.get("career_project") or passport.get("motivations") or ""
    if isinstance(aspirations, list):
        aspirations = ", ".join(str(a) for a in aspirations[:5])

    return {
        "steps": steps,
        "exp_text": "\n".join(exp_lines) if exp_lines else "Aucune expérience renseignée",
        "sf": sf, "se": se,
        "dclic_txt": dclic_txt,
        "aspirations": str(aspirations)[:400],
    }


async def _enrich_rome(metiers: list):
    for m in metiers:
        if not isinstance(m, dict) or m.get("rome_code"):
            continue
        patterns = search_word_patterns(m.get("metier", ""))
        if not patterns:
            continue
        query = {"$and": [{"libelle": {"$regex": p, "$options": "i"}} for p in patterns[:3]]}
        doc = await db.rome_metiers.find_one(query, {"_id": 0, "code_rome": 1, "libelle": 1})
        if not doc and len(patterns) > 1:
            doc = await db.rome_metiers.find_one({"libelle": {"$regex": patterns[0], "$options": "i"}}, {"_id": 0, "code_rome": 1, "libelle": 1})
        if doc:
            m["rome_code"] = doc.get("code_rome")
            m["rome_libelle"] = doc.get("libelle")


async def _run_exploration(job_id: str, token_id: str):
    async def _progress(pct, label):
        await db.reconversion_jobs.update_one({"id": job_id}, {"$set": {"progress": pct, "step_label": label}})

    try:
        await _progress(10, "Lecture de votre trajectoire et de vos acquis…")
        p = await _gather_profile(token_id)
        has_dclic = bool(p["dclic_txt"])

        base_ctx = f"""EXPÉRIENCES (chronologiques) :
{p['exp_text']}

SAVOIR-FAIRE : {', '.join(p['sf'][:20]) or 'Non renseignés'}
SAVOIR-ÊTRE : {', '.join(p['se'][:15]) or 'Non renseignés'}
PROFIL D'CLIC PRO : {p['dclic_txt'] or 'Test non réalisé'}
ASPIRATIONS : {p['aspirations'] or 'Non renseignées'}"""

        await _progress(25, "Extraction de vos invariants et compétences transférables…")

        sys_a = """Tu es un conseiller en évolution professionnelle français, approche phénoménologique/constructiviste.
La reconversion n'est PAS une rupture : c'est une nouvelle lecture de l'expérience acquise.
Réponds UNIQUEMENT en JSON valide, en français."""
        prompt_a = f"""{base_ctx}

Analyse cette trajectoire et réponds en JSON :
{{
  "ligne_coherence": "Formulation narrative (2-3 phrases) commençant par 'Malgré des environnements différents, votre trajectoire montre une constante : …' — fil conducteur de l'identité professionnelle",
  "invariants": ["4 à 6 verbes/constantes extraits des expériences, ex: Aider, Organiser, Transmettre"],
  "acquis": ["5 à 8 acquis majeurs tirés des expériences (ce que ça m'a appris)"],
  "competences_transferables": ["6 à 10 compétences transférables vers d'autres métiers"]
}}"""

        sys_b = """Tu es un expert français de l'orientation professionnelle et du référentiel ROME.
RÈGLE ABSOLUE : pour le niveau 'explorer' (rupture), ne JAMAIS dire 'ce métier vous correspond' — toujours 'ce métier mérite d'être exploré parce que…'. L'IA ouvre des possibles, la personne construit son choix.
Réponds UNIQUEMENT en JSON valide, en français."""
        prompt_b = f"""{base_ctx}

Propose des métiers sur 3 niveaux (curseur Proche → Rupture). Pour CHAQUE métier, une fiche passerelle complète.
{('IMPORTANT : intègre le profil D''CLIC PRO (personnalité, compétences fortes) dans les arguments.' if has_dclic else '')}

JSON attendu :
{{
  "evoluer": [3 métiers PROCHES du même univers (ex: serveur → responsable de restauration)],
  "reconvertir": [3 métiers DIFFÉRENTS réutilisant les compétences transférables (ex: → conseiller clientèle)],
  "explorer": [3 métiers en RUPTURE, formulés en hypothèses argumentées ('mérite d'être exploré parce que…')]
}}
Chaque métier = {{
  "metier": "Intitulé du métier",
  "pourquoi": "Pourquoi ce métier peut vous correspondre / mérite d'être exploré (2-3 phrases, s'appuyer sur les expériences réelles)",
  "sf_mobilisables": ["3-5 savoir-faire déjà possédés et mobilisables"],
  "se_mobilisables": ["2-4 savoir-être mobilisables"],
  "transferables_count": nombre de compétences transférables possédées (entier),
  "manquantes": ["2-4 compétences techniques à acquérir"],
  "reduire_ecart": ["3-4 actions concrètes : formation précise, certification, PMSMP (immersion), enquête métier, mentor UBUNTOO"],
  "rome_code": "code ROME si connu, sinon null"
}}"""

        res_a, res_b = await asyncio.gather(
            _llm(sys_a, prompt_a),
            _llm(sys_b, prompt_b),
        )
        await _progress(75, "Construction des fiches passerelles et croisement ROME…")

        data_a = _parse_json(res_a) or {}
        data_b = _parse_json(res_b) or {}
        niveaux = {
            "evoluer": data_b.get("evoluer", []) or [],
            "reconvertir": data_b.get("reconvertir", []) or [],
            "explorer": data_b.get("explorer", []) or [],
        }
        for lvl in niveaux.values():
            await _enrich_rome(lvl)

        result = {
            "ligne_coherence": data_a.get("ligne_coherence", ""),
            "invariants": data_a.get("invariants", []),
            "acquis": data_a.get("acquis", []),
            "competences_transferables": data_a.get("competences_transferables", []),
            "niveaux": niveaux,
            "dclic_utilise": has_dclic,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.reconversion_jobs.update_one(
            {"id": job_id},
            {"$set": {"status": "completed", "progress": 100, "step_label": "Analyse terminée", "result": result}})
        await db.reconversion_results.update_one(
            {"token_id": token_id}, {"$set": {"token_id": token_id, "result": result}}, upsert=True)
    except Exception as e:
        logging.error(f"[Reconversion] Job {job_id} failed: {e}")
        await db.reconversion_jobs.update_one(
            {"id": job_id}, {"$set": {"status": "failed", "error": str(e)[:300]}})


@router.post("/explorer")
async def start_exploration(token: str):
    token_doc = await get_current_token(token)
    token_id = token_doc["id"]
    existing = await db.reconversion_jobs.find_one({"token_id": token_id, "status": "processing"}, {"_id": 0, "id": 1})
    if existing:
        return {"job_id": existing["id"], "status": "processing"}
    steps = await db.trajectory_steps.count_documents({"token_id": token_id})
    passport = await db.passports.find_one({"token_id": token_id}, {"_id": 0, "competences": 1})
    if steps == 0 and not (passport or {}).get("competences"):
        raise HTTPException(status_code=400, detail="Ajoutez d'abord des expériences à votre trajectoire ou chargez votre CV.")
    job_id = str(uuid.uuid4())
    await db.reconversion_jobs.insert_one({
        "id": job_id, "token_id": token_id, "status": "processing",
        "progress": 5, "step_label": "Initialisation de l'exploration…",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    asyncio.create_task(_run_exploration(job_id, token_id))
    return {"job_id": job_id, "status": "processing"}


@router.get("/explorer/status/{job_id}")
async def exploration_status(job_id: str, token: str):
    token_doc = await get_current_token(token)
    job = await db.reconversion_jobs.find_one({"id": job_id, "token_id": token_doc["id"]}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job introuvable")
    return job


@router.get("/explorer/latest")
async def exploration_latest(token: str):
    token_doc = await get_current_token(token)
    doc = await db.reconversion_results.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not doc:
        return {"has_data": False, "result": None, "custom_metiers": []}
    return {"has_data": bool(doc.get("result")), "result": doc.get("result"), "custom_metiers": doc.get("custom_metiers", [])}


async def _run_metier_analysis(job_id: str, token_id: str, metier: str):
    try:
        await db.reconversion_jobs.update_one({"id": job_id}, {"$set": {"progress": 20, "step_label": f"Analyse du matching avec « {metier} »…"}})
        p = await _gather_profile(token_id)
        has_dclic = bool(p["dclic_txt"])
        sys_msg = """Tu es un expert français de l'orientation professionnelle et du référentiel ROME.
Tu réalises un DIAGNOSTIC DE MATCHING honnête entre un profil et un métier cible choisi par la personne.
Sois réaliste : ni complaisant, ni décourageant. Formule les points de vigilance de façon constructive.
Réponds UNIQUEMENT en JSON valide, en français."""
        prompt = f"""PROFIL :
EXPÉRIENCES (chronologiques) :
{p['exp_text']}

SAVOIR-FAIRE : {', '.join(p['sf'][:20]) or 'Non renseignés'}
SAVOIR-ÊTRE : {', '.join(p['se'][:15]) or 'Non renseignés'}
PROFIL D'CLIC PRO : {p['dclic_txt'] or 'Test non réalisé'}
ASPIRATIONS : {p['aspirations'] or 'Non renseignées'}

MÉTIER CIBLE SAISI PAR LA PERSONNE : « {metier} »

Produis un diagnostic de matching complet en JSON :
{{
  "metier": "Intitulé normalisé du métier",
  "score_matching": score 0-100 (réaliste : compétences transférables, écart technique, cohérence de trajectoire),
  "verdict": "1 phrase de synthèse du matching (honnête et nuancée)",
  "pourquoi": "Pourquoi ce métier mérite d'être exploré au regard de la trajectoire réelle (2-3 phrases)",
  "points_forts": ["3-5 atouts concrets du profil pour ce métier"],
  "points_vigilance": ["2-4 points de vigilance ou freins à anticiper"],
  "sf_mobilisables": ["3-5 savoir-faire déjà possédés et mobilisables"],
  "se_mobilisables": ["2-4 savoir-être mobilisables"],
  "transferables_count": nombre de compétences transférables possédées (entier),
  "manquantes": ["2-5 compétences techniques à acquérir"],
  "reduire_ecart": ["3-4 actions concrètes : formation précise, certification, PMSMP (immersion), enquête métier, mentor UBUNTOO"],
  "rome_code": "code ROME si connu, sinon null"
}}"""
        raw = await _llm(sys_msg, prompt)
        fiche = _parse_json(raw)
        if not fiche:
            raise ValueError("Réponse IA illisible")
        fiche["saisie_utilisateur"] = metier
        fiche["dclic_utilise"] = has_dclic
        fiche["analyzed_at"] = datetime.now(timezone.utc).isoformat()
        await _enrich_rome([fiche])
        await db.reconversion_jobs.update_one(
            {"id": job_id},
            {"$set": {"status": "completed", "progress": 100, "step_label": "Diagnostic terminé", "result": fiche}})
        await db.reconversion_results.update_one(
            {"token_id": token_id},
            {"$push": {"custom_metiers": {"$each": [fiche], "$slice": -10}}, "$setOnInsert": {"token_id": token_id}},
            upsert=True)
    except Exception as e:
        logging.error(f"[Reconversion] Metier job {job_id} failed: {e}")
        await db.reconversion_jobs.update_one(
            {"id": job_id}, {"$set": {"status": "failed", "error": str(e)[:300]}})


@router.post("/explorer/metier")
async def start_metier_analysis(token: str, body: dict):
    token_doc = await get_current_token(token)
    metier = (body.get("metier") or "").strip()
    if not metier or len(metier) < 3:
        raise HTTPException(status_code=400, detail="Saisissez un intitulé de métier (3 caractères minimum).")
    job_id = str(uuid.uuid4())
    await db.reconversion_jobs.insert_one({
        "id": job_id, "token_id": token_doc["id"], "kind": "metier", "metier": metier,
        "status": "processing", "progress": 10, "step_label": "Lecture de votre profil…",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    asyncio.create_task(_run_metier_analysis(job_id, token_doc["id"], metier))
    return {"job_id": job_id, "status": "processing"}


@router.delete("/explorer/metier")
async def delete_custom_metier(token: str, analyzed_at: str):
    token_doc = await get_current_token(token)
    await db.reconversion_results.update_one(
        {"token_id": token_doc["id"]},
        {"$pull": {"custom_metiers": {"analyzed_at": analyzed_at}}})
    return {"status": "ok"}


COHERENCE_SYS = """Tu es un conseiller en évolution professionnelle français.
Tu analyses une frise chronologique d'étapes professionnelles pour détecter les CHANGEMENTS DE MÉTIER et mettre en valeur la cohérence globale de la trajectoire.
Réponds UNIQUEMENT en JSON valide, en français."""


@router.get("/coherence")
async def trajectory_coherence(token: str):
    token_doc = await get_current_token(token)
    token_id = token_doc["id"]
    steps = await db.trajectory_steps.find({"token_id": token_id}, {"_id": 0}).to_list(200)
    pro_steps = [s for s in steps if s.get("step_type") in (None, "emploi", "interim", "stage", "creation", "reconversion", "projet")]
    if len(pro_steps) < 2:
        return {"has_data": False, "transitions": [], "fil_conducteur": None}
    pro_steps.sort(key=lambda s: s.get("start_date") or "0000")

    sig = hashlib.md5("|".join(f"{s.get('id')}:{s.get('title', '')}" for s in pro_steps).encode()).hexdigest()
    cached = await db.trajectoire_coherence.find_one({"token_id": token_id}, {"_id": 0})
    if cached and cached.get("steps_hash") == sig:
        return {"has_data": True, "transitions": cached.get("transitions", []), "fil_conducteur": cached.get("fil_conducteur")}

    lines = [f"{i+1}. (id={s['id']}) {s.get('title', '')} — {s.get('organization', '') or 'N/A'} ({s.get('start_date', '?')} → {s.get('end_date') or 'en cours'})" for i, s in enumerate(pro_steps)]
    prompt = f"""Frise professionnelle chronologique :
{chr(10).join(lines)}

Pour chaque étape (sauf la première), détermine si elle représente un CHANGEMENT DE MÉTIER significatif par rapport à l'étape précédente (pas un simple changement d'employeur sur le même métier).
JSON attendu :
{{
  "transitions": [
    {{"step_id": "id de l'étape", "est_changement": true/false, "nouveau_metier": "métier abordé" ou null, "lien_coherence": "si changement : 1-2 phrases expliquant ce qui relie ce nouveau métier au reste de la trajectoire (compétences communes, posture, fil conducteur) — valorisant et concret" ou null}}
  ],
  "fil_conducteur": "1-2 phrases : la constante qui donne une cohérence globale à TOUTE la trajectoire malgré les changements" ou null si aucun changement détecté
}}"""
    try:
        raw = await _llm(COHERENCE_SYS, prompt)
        data = _parse_json(raw) or {}
    except Exception as e:
        logging.error(f"[Coherence] LLM error: {e}")
        return {"has_data": False, "transitions": [], "fil_conducteur": None}

    transitions = [t for t in data.get("transitions", []) if isinstance(t, dict) and t.get("step_id")]
    fil = data.get("fil_conducteur")
    await db.trajectoire_coherence.update_one(
        {"token_id": token_id},
        {"$set": {"token_id": token_id, "steps_hash": sig, "transitions": transitions, "fil_conducteur": fil,
                  "updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True)
    return {"has_data": True, "transitions": transitions, "fil_conducteur": fil}
