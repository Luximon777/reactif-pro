"""
D'CLIC PRO — Routes API (Version GitHub intégrale)
Source: GitHub Luximon777/declic-pro — intégré dans Ré'Actif Pro
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
import asyncio, json, logging, os, secrets, uuid

from dclic_data import (
    VISUAL_QUESTIONS, QUESTIONNAIRE, VERTUS, FILIERES, METIERS,
    ENNEA_TO_PROFILE, RIASEC_DESCRIPTIONS, LIFE_PATHS,
    MBTI_TO_VERTU_FALLBACK, ARCHEOLOGIE_COMPETENCES, TABLEAU_CK,
)
from dclic_scoring import (
    compute_profile, calculate_vertus_profile, calculate_riasec_profile,
    calculate_ofman_quadrant, get_zones_vigilance_for_profile,
    get_cross_analysis, get_functioning_compass, get_integrated_analysis,
    get_exploration_paths, score_job, get_favorable_environment,
)
from dclic_referentiel import CITATIONS_VERTUS, format_referentiel_for_prompt

load_dotenv()
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

logger = logging.getLogger(__name__)


# ─── Request models ──────────────────────────────────────────────────
class QuestionnaireResponse(BaseModel):
    answers: Dict[str, str]

class JobSearchRequest(BaseModel):
    answers: Dict[str, str]
    job_query: str = ""
    birth_date: Optional[str] = None
    education_level: Optional[str] = None

class ExploreRequest(BaseModel):
    answers: Dict[str, str]
    birth_date: Optional[str] = None
    education_level: Optional[str] = None

class AccessCodeRequest(BaseModel):
    access_code: str


# ─── Helper: access code ─────────────────────────────────────────────
def generate_access_code(length: int = 8) -> str:
    chars = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
    p1 = "".join(secrets.choice(chars) for _ in range(4))
    p2 = "".join(secrets.choice(chars) for _ in range(4))
    return f"{p1}-{p2}"


# ─── Helper: life path ──────────────────────────────────────────────
def get_life_path_data(birth_date: str) -> Optional[Dict]:
    try:
        digits = [int(c) for c in birth_date if c.isdigit()]
        total = sum(digits)
        while total > 9 and total not in (11, 22, 33):
            total = sum(int(d) for d in str(total))
        key = str(total)
        return LIFE_PATHS.get(key)
    except Exception:
        return None


def get_mbti_group(mbti: str) -> str:
    if len(mbti) < 4:
        return "?"
    if mbti[1] == "N" and mbti[2] == "T":
        return "NT (Analystes)"
    elif mbti[1] == "N" and mbti[2] == "F":
        return "NF (Diplomates)"
    elif mbti[1] == "S" and mbti[3] == "J":
        return "SJ (Sentinelles)"
    elif mbti[1] == "S" and mbti[3] == "P":
        return "SP (Explorateurs)"
    return "?"


# ─── AI Narrative generation ─────────────────────────────────────────
async def generate_profile_narrative(
    profile: Dict, ennea_profile: Dict, vertu_data: Dict,
    life_path_data: Optional[Dict] = None,
) -> Dict[str, str]:
    if not EMERGENT_LLM_KEY:
        return generate_fallback_narrative(profile, ennea_profile, vertu_data, life_path_data)
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"dclic-narr-{uuid.uuid4()}",
            system_message=(
                "Tu es un expert en insertion professionnelle et en orientation, "
                "spécialiste de l'archéologie des compétences. Tu rédiges des analyses "
                "personnalisées, bienveillantes et concrètes. Tu ne mentionnes JAMAIS "
                "les termes techniques (MBTI, DISC, Ennéagramme, codes). Tu parles "
                "directement à la personne ('vous'). Français courant, ton professionnel chaleureux."
            ),
        ).with_model("openai", "gpt-5.2")

        disc_desc = {
            "D": "orienté vers l'action et les résultats",
            "I": "communicatif et enthousiaste",
            "S": "fiable, loyal et orienté vers la collaboration",
            "C": "analytique, rigoureux et méthodique",
        }
        vertu_name = vertu_data.get("name", "Humanité")
        forces = vertu_data.get("forces", [])[:4]
        qualites = vertu_data.get("qualites_humaines", [])[:4]
        savoirs = vertu_data.get("savoirs_etre", [])[:3]
        cps = vertu_data.get("competences_oms", [])[:3]
        comp_pro = vertu_data.get("competences_pro", [])[:4]

        prompt = f"""Analyse le profil suivant et rédige un texte personnalisé.

PROFIL:
- Style de travail: {disc_desc.get(profile.get('disc', 'S'), 'équilibré')}
- Forces de caractère (vertu {vertu_name}): {', '.join(forces)}
- Qualités humaines: {', '.join(qualites)}
- Savoirs-être professionnels: {', '.join(savoirs)}
- Compétences psychosociales: {', '.join(cps)}
- Compétences professionnelles transférables: {', '.join(comp_pro)}
- Motivations: {', '.join(profile.get('motivations', ['Accomplissement']))}

Rédige en JSON valide:
{{
  "portrait": "Portrait professionnel (4-5 phrases)",
  "fonctionnement": "Mode de fonctionnement au travail (3-4 phrases)",
  "forces_et_vigilance": "Points forts et points de vigilance (3-4 phrases)",
  "conseil": "Conseil personnalisé d'orientation (2-3 phrases)"
}}"""
        resp = await asyncio.to_thread(chat.send_message, UserMessage(text=prompt))
        raw = resp.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        logger.warning(f"Narrative IA échouée: {e}")
        return generate_fallback_narrative(profile, ennea_profile, vertu_data, life_path_data)


def generate_fallback_narrative(
    profile: Dict, ennea_profile: Dict, vertu_data: Dict,
    life_path_data: Optional[Dict] = None,
) -> Dict[str, str]:
    vertu_name = vertu_data.get("name", "Humanité")
    forces = vertu_data.get("forces", [])[:3]
    qualites = vertu_data.get("qualites_humaines", [])[:3]
    return {
        "portrait": f"Votre profil révèle une personnalité ancrée dans la vertu de {vertu_name}, "
                     f"avec des forces marquées en {', '.join(forces)}.",
        "fonctionnement": f"Au travail, vous vous appuyez sur vos qualités de {', '.join(qualites)}.",
        "forces_et_vigilance": f"Vos points forts : {', '.join(ennea_profile.get('moteur', 'Accomplissement').split(',')[:2])}. "
                                "Points de vigilance : gérer votre énergie et poser vos limites.",
        "conseil": "Explorez des environnements qui valorisent vos compétences relationnelles et votre capacité d'adaptation.",
    }


async def generate_job_match_narrative(
    profile: Dict, job: Dict, score: int, reasons: List[str], risks: List[str],
) -> Dict[str, str]:
    if not EMERGENT_LLM_KEY:
        return generate_fallback_job_narrative(profile, job, score, reasons, risks)
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"dclic-job-{uuid.uuid4()}",
            system_message="Tu es un conseiller en insertion professionnelle. Analyse concise en JSON.",
        ).with_model("openai", "gpt-5.2")

        job_label = job.get("label", job.get("intitule_rome", "ce métier"))
        prompt = f"""Analyse la compatibilité (score {score}%) entre ce profil et le métier "{job_label}".
Atouts: {', '.join(reasons[:3])}
Risques: {', '.join(risks[:2])}

Réponds en JSON:
{{"analyse": "Analyse de compatibilité (3-4 phrases)", "conseil": "Conseil (2 phrases)", "formation": "Formation suggérée (1-2 phrases)"}}"""
        resp = await asyncio.to_thread(chat.send_message, UserMessage(text=prompt))
        raw = resp.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception:
        return generate_fallback_job_narrative(profile, job, score, reasons, risks)


def generate_fallback_job_narrative(
    profile: Dict, job: Dict, score: int, reasons: List[str], risks: List[str],
) -> Dict[str, str]:
    job_label = job.get("label", job.get("intitule_rome", "ce métier"))
    return {
        "analyse": f"Votre compatibilité avec {job_label} est de {score}%. "
                    f"Vos atouts : {', '.join(reasons[:2]) if reasons else 'polyvalence'}.",
        "conseil": "Développez les compétences spécifiques au poste via une formation ciblée.",
        "formation": "Identifiez les certifications professionnelles du secteur.",
    }


# ─── Register routes ─────────────────────────────────────────────────
def register_dclic_routes(app, db):
    router = APIRouter(prefix="/api/dclic", tags=["D'CLIC PRO"])
    passports_col = db["passports"]
    dclic_results_col = db["dclic_results"]

    # ── GET /questionnaire (legacy text) ──
    @router.get("/questionnaire")
    async def get_questionnaire():
        return {"questions": QUESTIONNAIRE, "total": len(QUESTIONNAIRE)}

    # ── GET /questionnaire/visual ──
    @router.get("/questionnaire/visual")
    async def get_visual_questionnaire():
        return {
            "questions": VISUAL_QUESTIONS,
            "total": len(VISUAL_QUESTIONS),
            "format": "visual",
        }

    # ── GET /filieres ──
    @router.get("/filieres")
    async def get_filieres():
        return {"filieres": FILIERES}

    # ── GET /metiers ──
    @router.get("/metiers")
    async def get_metiers():
        return {"metiers": METIERS}

    # ── GET /vertus ──
    @router.get("/vertus")
    async def get_vertus():
        return {"vertus": VERTUS}

    # ── POST /submit (compute profile + save) ──
    @router.post("/submit")
    async def submit_dclic(payload: QuestionnaireResponse):
        answers = payload.answers

        # 1. Scoring déterministe
        profile = compute_profile(answers)
        vertus_profile = calculate_vertus_profile(answers, mbti_type=profile.get("mbti"))
        riasec_profile = calculate_riasec_profile(answers, profile)

        # Ennéagramme data
        ennea_profile = ENNEA_TO_PROFILE.get(profile["ennea_dominant"], ENNEA_TO_PROFILE[5])

        # Croiser Vertus + Ennéagramme
        vertus_scores_enriched = vertus_profile.get("vertus_scores", {}).copy()
        ennea_vertu = ennea_profile["vertu"]
        if vertus_scores_enriched:
            max_s = max(vertus_scores_enriched.values()) if vertus_scores_enriched.values() else 100
            if ennea_vertu in vertus_scores_enriched:
                vertus_scores_enriched[ennea_vertu] += max_s * 0.2

        if vertus_scores_enriched and any(v > 0 for v in vertus_scores_enriched.values()):
            vertu_key = max(vertus_scores_enriched, key=vertus_scores_enriched.get)
        else:
            vertu_key = ennea_vertu

        vertu_data = dict(VERTUS.get(vertu_key, VERTUS["sagesse"]))
        vertu_data["ennea_contribution"] = ennea_vertu
        vertu_data["crossed_with_ennea"] = ennea_vertu == vertu_key

        # Citations
        cit_data = CITATIONS_VERTUS.get(vertu_key, {})

        # Fonctionnel
        zones_vigilance = get_zones_vigilance_for_profile(profile, vertu_data)
        functioning_compass = get_functioning_compass(profile)

        # Life path — from birth date or from profile
        life_path_data = None
        if "birth_date" in answers and answers.get("birth_date"):
            life_path_data = get_life_path_data(answers["birth_date"])
        if not life_path_data:
            # Generate a default life path from ennéagramme dominant
            ennea_dom = profile.get("ennea_dominant", 5)
            life_path_data = {
                "path_number": str(ennea_dom),
                "label": f"Parcours orienté {vertu_data.get('name', 'Humanité')}",
                "strengths": vertu_data.get("forces", [])[:3],
                "watchouts": [z.get("qualite", "") + " (excès : " + z.get("piege", "") + ")" for z in zones_vigilance[:2]] if zones_vigilance else ["Surcharge émotionnelle", "Difficulté à déléguer"],
                "micro_actions": [
                    {"focus": "Développement", "action": f"Explorer des métiers liés à vos forces : {', '.join(vertu_data.get('competences_pro', vertu_data.get('forces', []))[:3])}."},
                    {"focus": "Équilibre", "action": "Définir des limites claires entre engagement professionnel et temps personnel."},
                    {"focus": "Compétences", "action": f"Renforcer vos savoirs-être clés : {', '.join(vertu_data.get('savoirs_etre', [])[:3])}."},
                ],
                "work_preferences": get_favorable_environment(profile.get("disc", "S"), profile),
            }

        # Cross analysis
        cross_analysis = get_cross_analysis(life_path_data, profile, profile.get("ennea_dominant", 5))
        integrated_analysis = get_integrated_analysis(profile, vertu_data, life_path_data, zones_vigilance)

        # Narrative IA
        profile_narrative = await generate_profile_narrative(profile, ennea_profile, vertu_data)

        # Code d'accès
        access_code = generate_access_code()

        # Construire le profil complet
        full_profile = {
            "mbti": profile.get("mbti", ""),
            "disc": profile.get("disc", "S"),
            "disc_scores": profile.get("disc_scores", {}),
            "disc_label": f"Profil {profile.get('disc', 'S')}",
            "ennea_dominant": profile.get("ennea_dominant", 5),
            "ennea_runner_up": profile.get("ennea_runner_up", 5),
            "ennea_profile": ennea_profile,
            "motivations": profile.get("motivations", []),
            "competences_fortes": profile.get("competences_fortes", []),
            "vigilances": profile.get("vigilances", []),
            "dominant_vertus": profile.get("dominant_vertus", []),
            "riasec_profile": riasec_profile,
            "vertus_profile": {
                "dominant": vertu_key,
                "dominant_name": vertu_data.get("name", vertu_key),
                "description": f"La vertu de {vertu_data.get('name', vertu_key)} — {VERTUS.get(vertu_key, {}).get('name', '')}",
                "citation": cit_data.get("citations", [""])[0] if cit_data.get("citations") else "",
                "vertus_scores": vertus_scores_enriched,
                "forces_caractere": vertu_data.get("forces", []),
                "qualites_dominantes": vertus_profile.get("qualites_dominantes", vertu_data.get("qualites_humaines", [])[:4]),
                "valeurs_dominantes": vertu_data.get("valeurs_schwartz", [])[:3],
                "savoirs_etre_dominants": vertus_profile.get("savoirs_etre_dominants", vertu_data.get("savoirs_etre", [])[:3]),
                "competences_oms": vertus_profile.get("competences_oms", vertu_data.get("competences_oms", [])[:3]),
                "competences_transferables": vertu_data.get("competences_pro", [])[:5],
                "metiers_associes": TABLEAU_CK.get(vertu_key, {}).get("metiers_associes", []),
                "penseurs": {
                    "orientaux": cit_data.get("penseurs_orientaux", [])[:3],
                    "occidentaux": cit_data.get("penseurs_occidentaux", [])[:3],
                },
            },
            "vertu_data": {
                "name": vertu_data.get("name", ""),
                "cognition": vertu_data.get("cognition", [])[:3],
                "conation": vertu_data.get("conation", [])[:3],
                "affection": vertu_data.get("affection", [])[:3],
                "valeurs_schwartz": vertu_data.get("valeurs_schwartz", []),
                "forces": vertu_data.get("forces", []),
                "savoirs_etre": vertu_data.get("savoirs_etre", []),
            },
            "compass": functioning_compass,
            "zones_vigilance": zones_vigilance,
            "integrated_analysis": integrated_analysis,
            "cross_analysis": cross_analysis,
            "life_path": life_path_data,
            "profile_narrative": profile_narrative,
            "ofman_quadrant": zones_vigilance[:3],
        }

        # Sauvegarder en base
        doc = {
            "access_code": access_code,
            "created_at": datetime.now(timezone.utc),
            "is_claimed": False,
            "answers": answers,
            "profile": full_profile,
        }
        await dclic_results_col.insert_one(doc)

        return {"success": True, "access_code": access_code, "profile": full_profile}

    # ── POST /job-match ──
    @router.post("/job-match")
    async def job_match(payload: JobSearchRequest):
        answers = payload.answers
        profile = compute_profile(answers)
        riasec = calculate_riasec_profile(answers, profile)
        vertus_prof = calculate_vertus_profile(answers, mbti_type=profile.get("mbti"))

        # Score all local jobs
        results = [score_job(profile, job, riasec, vertus_prof) for job in METIERS]
        results.sort(key=lambda x: x["score"], reverse=True)

        best = results[0] if results else None
        matched_job = next((j for j in METIERS if j["id"] == best["job_id"]), None) if best else None

        ennea_profile = ENNEA_TO_PROFILE.get(profile["ennea_dominant"], ENNEA_TO_PROFILE[5])
        vertu_key = ennea_profile["vertu"]
        vertu_data = dict(VERTUS.get(vertu_key, VERTUS["sagesse"]))

        profile_narrative = await generate_profile_narrative(profile, ennea_profile, vertu_data)
        job_narrative = None
        if matched_job and best:
            job_narrative = await generate_job_match_narrative(
                profile, matched_job, best["score"], best.get("reasons", []), best.get("risks", [])
            )

        zones = get_zones_vigilance_for_profile(profile, vertu_data)
        compass = get_functioning_compass(profile)
        integrated = get_integrated_analysis(profile, vertu_data, None, zones)

        return {
            "profile_summary": {
                "mbti": profile.get("mbti"),
                "disc": profile.get("disc"),
                "disc_scores": profile.get("disc_scores"),
                "ennea_dominant": profile.get("ennea_dominant"),
                "riasec": riasec,
                "vertus": vertus_prof,
            },
            "profile_narrative": profile_narrative,
            "best_match": best,
            "job_narrative": job_narrative,
            "other_matches": results[1:5],
            "zones_vigilance": zones,
            "functioning_compass": compass,
            "integrated_analysis": integrated,
        }

    # ── POST /explore ──
    @router.post("/explore")
    async def explore_careers(payload: ExploreRequest):
        answers = payload.answers
        profile = compute_profile(answers)
        riasec = calculate_riasec_profile(answers, profile)
        vertus_prof = calculate_vertus_profile(answers, mbti_type=profile.get("mbti"))

        paths = get_exploration_paths(profile, riasec, vertus_prof)
        all_scores = [score_job(profile, job, riasec, vertus_prof) for job in METIERS]
        all_scores.sort(key=lambda x: x["score"], reverse=True)

        top_filieres = [p["filiere_id"] for p in paths[:3]]
        filtered = [j for j in all_scores if j.get("filiere") in top_filieres]
        if len(filtered) < 10:
            others = [j for j in all_scores if j.get("filiere") not in top_filieres]
            filtered.extend(others[: 10 - len(filtered)])
        compatible = [j for j in filtered if j["score"] >= 50]
        if len(compatible) < 10:
            compatible = [j for j in filtered if j["score"] >= 40][:10]

        ennea_profile = ENNEA_TO_PROFILE.get(profile["ennea_dominant"], ENNEA_TO_PROFILE[5])
        vertu_key = ennea_profile["vertu"]
        vertu_data = dict(VERTUS.get(vertu_key, VERTUS["sagesse"]))
        profile_narrative = await generate_profile_narrative(profile, ennea_profile, vertu_data)
        zones = get_zones_vigilance_for_profile(profile, vertu_data)
        compass = get_functioning_compass(profile)
        integrated = get_integrated_analysis(profile, vertu_data, None, zones)

        return {
            "profile_summary": {
                "mbti": profile.get("mbti"),
                "disc": profile.get("disc"),
                "riasec": riasec,
                "vertus": vertus_prof,
            },
            "profile_narrative": profile_narrative,
            "exploration_paths": paths,
            "top_jobs": compatible[:10],
            "zones_vigilance": zones,
            "functioning_compass": compass,
            "integrated_analysis": integrated,
        }

    # ── GET /results/{code} ──
    @router.get("/results/{code}")
    async def get_results_by_code(code: str):
        doc = await dclic_results_col.find_one({"access_code": code.upper().strip()})
        if not doc:
            raise HTTPException(status_code=404, detail="Code non trouvé")
        doc.pop("_id", None)
        return {"success": True, "access_code": doc["access_code"], "profile": doc.get("profile", {})}

    # ── POST /retrieve-results ──
    @router.post("/retrieve-results")
    async def retrieve_results(payload: AccessCodeRequest):
        code = payload.access_code.upper().strip()
        doc = await dclic_results_col.find_one({"access_code": code})
        if not doc:
            raise HTTPException(status_code=404, detail="Code non trouvé")
        if doc.get("is_claimed"):
            raise HTTPException(status_code=400, detail="Code déjà utilisé")
        doc.pop("_id", None)
        return {"success": True, "access_code": code, "result_data": doc}

    # ── POST /diagnostic/profile ──
    @router.post("/diagnostic/profile")
    async def diagnostic_profile(payload: QuestionnaireResponse):
        answers = payload.answers
        profile = compute_profile(answers)
        vertus_prof = calculate_vertus_profile(answers, mbti_type=profile.get("mbti"))
        riasec = calculate_riasec_profile(answers, profile)
        mbti = profile.get("mbti", "")
        return {
            "format_detecte": "VISUEL" if len([k for k in answers if k.startswith("v")]) > len([k for k in answers if k.startswith("q")]) else "LEGACY",
            "profil": {
                "mbti": mbti,
                "disc": profile.get("disc"),
                "disc_scores": profile.get("disc_scores"),
                "ennea_dominant": profile.get("ennea_dominant"),
            },
            "validation_mbti": {
                "type": mbti,
                "groupe": get_mbti_group(mbti),
                "vertu_attendue": MBTI_TO_VERTU_FALLBACK.get(mbti, ("?", "?")),
            },
            "riasec": riasec,
            "vertus": vertus_prof,
        }

    # ── Attach to my-results for authenticated users ──
    @router.get("/my-results")
    async def get_my_results(token: str = ""):
        if not token:
            raise HTTPException(status_code=401, detail="Token requis")
        token_doc = await db["tokens"].find_one({"token": token}, {"_id": 0})
        if not token_doc:
            raise HTTPException(status_code=401, detail="Token invalide")
        token_id = token_doc["id"]
        passport = await passports_col.find_one({"token_id": token_id})
        if not passport or "dclic_results" not in passport:
            raise HTTPException(status_code=404, detail="Aucun résultat D'CLIC PRO trouvé")
        return {"success": True, "profile": passport["dclic_results"]}

    # ── POST /retrieve (alias for Dashboard compatibility) ──
    @router.post("/retrieve")
    async def retrieve_for_dashboard(payload: AccessCodeRequest):
        code = payload.access_code.upper().strip()
        doc = await dclic_results_col.find_one({"access_code": code})
        if not doc:
            raise HTTPException(status_code=404, detail="Code introuvable")
        profile = doc.get("profile", {})
        # Return profile with flattened fields for Dashboard compatibility
        return {
            "success": True,
            "access_code": code,
            "profile": profile,
        }

    # ── POST /claim ──
    @router.post("/claim")
    async def claim_code(access_code: str = "", user_id: str = "", body: dict = {}):
        # Support both query params and body
        code = (access_code or body.get("access_code", "")).upper().strip()
        uid = user_id or body.get("user_id", "")
        if not code:
            raise HTTPException(status_code=400, detail="Code requis")
        doc = await dclic_results_col.find_one({"access_code": code})
        if not doc:
            raise HTTPException(status_code=404, detail="Code introuvable")
        await dclic_results_col.update_one(
            {"access_code": code},
            {"$set": {"is_claimed": True, "claimed_by": uid, "claimed_at": datetime.now(timezone.utc)}},
        )
        return {"success": True, "message": "Code validé"}

    app.include_router(router)

    # ── POST /api/profile/import-dclic (on main app, not dclic router) ──
    @app.post("/api/profile/import-dclic")
    async def import_dclic_profile(token: str = "", body: dict = {}):
        if not token:
            raise HTTPException(status_code=401, detail="Token requis")

        # Use the same token lookup as the rest of the app
        token_doc = await db["tokens"].find_one({"token": token}, {"_id": 0})
        if not token_doc:
            raise HTTPException(status_code=401, detail="Token invalide")
        token_id = token_doc["id"]

        dclic_profile = body.get("dclic_profile", {})
        if not dclic_profile:
            raise HTTPException(status_code=400, detail="Profil D'CLIC requis")

        # Build skills from D'CLIC data
        vp = dclic_profile.get("vertus_profile", {})
        skills = []
        for comp in dclic_profile.get("competences_fortes", []):
            skills.append({"name": comp, "category": "comportementale", "declared_level": 4, "status": "declaree"})
        for comp in vp.get("competences_transferables", []):
            skills.append({"name": comp, "category": "transferable", "declared_level": 4, "status": "declaree"})

        # Also include skills from body payload
        for s in body.get("skills", []):
            if s.get("name") and s["name"] not in [sk["name"] for sk in skills]:
                skills.append(s)

        # Update passport (using token_id, consistent with the rest of the app)
        update_data = {
            "dclic_results": dclic_profile,
            "dclic_imported_at": datetime.now(timezone.utc).isoformat(),
            "skills": skills,
            "target_job": body.get("target_job", ""),
        }

        evidences = body.get("evidences", [])
        if evidences:
            update_data["evidences"] = evidences

        passport = await db["passports"].find_one({"token_id": token_id})
        if passport:
            existing_skills = passport.get("skills", [])
            existing_names = {s["name"] for s in existing_skills}
            new_skills = [s for s in skills if s["name"] not in existing_names]
            update_data["skills"] = existing_skills + new_skills

            existing_ev = passport.get("evidences", [])
            update_data["evidences"] = existing_ev + evidences

            await db["passports"].update_one(
                {"token_id": token_id},
                {"$set": update_data},
            )
        else:
            update_data["token_id"] = token_id
            update_data["created_at"] = datetime.now(timezone.utc).isoformat()
            await db["passports"].insert_one(update_data)

        # Also set dclic_imported flag on the profiles collection (for Dashboard detection)
        await db["profiles"].update_one(
            {"token_id": token_id},
            {"$set": {"dclic_imported": True, "dclic_imported_at": datetime.now(timezone.utc).isoformat()}},
        )

        # Calculate completion
        updated = await db["passports"].find_one({"token_id": token_id})
        filled = 0
        total = 6
        if updated.get("dclic_results"): filled += 1
        if updated.get("skills") and len(updated["skills"]) > 0: filled += 1
        if updated.get("target_job"): filled += 1
        if updated.get("experiences") and len(updated.get("experiences", [])) > 0: filled += 1
        if updated.get("evidences") and len(updated.get("evidences", [])) > 0: filled += 1
        if updated.get("summary"): filled += 1
        completion = int((filled / total) * 100)

        return {
            "success": True,
            "message": "Profil D'CLIC PRO importé avec succès",
            "profile_completion": completion,
        }
