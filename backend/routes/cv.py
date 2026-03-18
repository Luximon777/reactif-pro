from fastapi import APIRouter, HTTPException, UploadFile, File
import asyncio
import uuid
import json
import logging
import base64
from datetime import datetime, timezone
from models import CvTextPayload, CvBase64Payload, PassportCompetence, PassportExperience
from db import db, EMERGENT_LLM_KEY
from helpers import get_current_token, _llm_call_with_retry, _extract_text_from_bytes
from routes.passport import calculate_completeness
from emergentintegrations.llm.chat import LlmChat, UserMessage

router = APIRouter()


async def _claude_generate_cv(system_msg: str, user_msg: str, max_retries: int = 2) -> dict:
    """Use Claude Sonnet for CV text generation - superior writing quality"""
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"cv-claude-{uuid.uuid4()}",
                system_message=system_msg
            ).with_model("anthropic", "claude-sonnet-4-5-20250929")
            response = await chat.send_message(UserMessage(text=user_msg))
            raw = response.strip() if isinstance(response, str) else response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
                raw = raw.strip()
            return json.loads(raw)
        except json.JSONDecodeError as e:
            last_error = f"Réponse Claude non valide (tentative {attempt+1})"
            logging.warning(f"Claude CV generation JSON error attempt {attempt+1}: {e}")
        except Exception as e:
            last_error = str(e)
            logging.warning(f"Claude CV generation error attempt {attempt+1}: {e}")
    raise Exception(f"Erreur Claude après {max_retries+1} tentatives: {last_error}")


async def _run_cv_analysis(job_id: str, token_id: str, file_content: bytes, filename: str, text_ready: bool = False, selected_models: list = None):
    if selected_models is None:
        selected_models = ["classique", "competences", "fonctionnel", "mixte"]
    try:
        await db.cv_jobs.update_one({"job_id": job_id}, {"$set": {"status": "analyzing", "step": "Extraction du texte..."}})
        if text_ready:
            cv_text = file_content.decode("utf-8", errors="ignore")
        else:
            cv_text = _extract_text_from_bytes(file_content, filename)
        if not cv_text or len(cv_text) < 50:
            await db.cv_jobs.update_one({"job_id": job_id}, {"$set": {"status": "failed", "error": "Le fichier ne contient pas assez de texte exploitable", "step": "Erreur"}})
            return
        cv_excerpt = cv_text[:6000]
        await db.cv_jobs.update_one({"job_id": job_id}, {"$set": {"step": "Analyse des compétences..."}})

        analysis = await _llm_call_with_retry(
            system_msg="""Tu es un expert RH. Analyse ce CV. Réponds UNIQUEMENT en JSON valide (pas de markdown).
Structure exacte:
{
  "profile": {"professional_summary": "2-3 phrases", "career_project": "string", "motivations": [], "compatible_environments": [], "target_sectors": []},
  "savoir_faire": [{"name": "string", "category": "technique|transversale|transferable|sectorielle", "level": "debutant|intermediaire|avance|expert", "ccsp_pole": "realisation|interaction|initiative", "ccsp_degree": "imitation|adaptation|transposition"}],
  "savoir_etre": [{"name": "string", "category": "transversale|transferable", "level": "debutant|intermediaire|avance|expert", "linked_qualites": [], "linked_valeurs": [], "linked_vertus": []}],
  "competences_transversales": ["communication", "travail en equipe", ...],
  "competences_transferables": [],
  "experiences": [{"title": "string", "organization": "string", "description": "string", "experience_type": "professionnel|personnel|benevole|projet", "skills_used": [], "achievements": []}],
  "formations_suggestions": [{"title": "string", "reason": "string", "priority": "haute|moyenne|basse", "skills_to_gain": []}],
  "offres_emploi_suggerees": [{"titre": "string", "secteur": "string", "type_contrat": "CDI|CDD|Interim|Alternance", "description_courte": "string", "competences_requises": []}]
}
IMPORTANT:
- competences_transversales: liste de 5-10 compétences transversales identifiées (communication, adaptabilité, gestion du temps, travail en équipe, résolution de problèmes, etc.)
- offres_emploi_suggerees: liste de 3-5 offres d'emploi pertinentes basées sur le profil, le secteur et les compétences du candidat
Valeurs IDs: autonomie, stimulation, hedonisme, realisation_de_soi, pouvoir, securite, conformite, tradition, bienveillance, universalisme.
Vertus: sagesse, courage, humanite, justice, temperance, transcendance.""",
            user_msg=f"Analyse ce CV:\n\n{cv_excerpt}"
        )

        await db.cv_jobs.update_one({"job_id": job_id}, {"$set": {"step": "Génération des CV par Claude IA..."}})

        cv_gen = {}
        if selected_models:
            model_map = {
                "classique": ("cv_classique", "CV chronologique classique : sobre, professionnel, avec sections claires (Coordonnées, Profil, Expériences, Formation, Compétences). Utilise un ton formel et structuré."),
                "competences": ("cv_competences", "CV axé compétences : organise par domaines de savoir-faire et savoir-être. Met en avant les compétences clés regroupées par thématique avant les expériences."),
                "fonctionnel": ("cv_fonctionnel", "CV fonctionnel : présente les compétences par grands domaines fonctionnels sans chronologie. Idéal pour reconversion ou parcours atypique."),
                "mixte": ("cv_mixte", "CV mixte : combine parcours chronologique et mise en valeur des compétences transférables. Montre l'évolution professionnelle tout en soulignant la polyvalence."),
            }
            selected = {k: v for k, v in model_map.items() if k in selected_models}
            if selected:
                keys_json = ", ".join([f'"{v[0]}": "texte complet du CV"' for v in selected.values()])
                instructions = "\n".join([f"- {v[0]}: {v[1]}" for v in selected.values()])
                try:
                    cv_gen = await _claude_generate_cv(
                        system_msg=f"""Tu es un rédacteur de CV professionnel expert en France. Reconstitue et génère des CV complets, bien rédigés et prêts à l'emploi à partir du profil fourni.

RÈGLES IMPORTANTES :
- Rédige des CV complets, détaillés et professionnels en français
- Chaque CV doit faire au moins 300 mots avec des phrases complètes
- Utilise un vocabulaire riche et professionnel adapté au secteur
- Mets en valeur les réalisations concrètes et les résultats chiffrés quand possible
- Adapte le ton et la structure au type de CV demandé
- Réponds UNIQUEMENT en JSON valide (pas de markdown, pas de commentaires)

Structure attendue : {{{keys_json}}}

Description de chaque modèle :
{instructions}""",
                        user_msg=f"Voici le profil à partir duquel reconstituer les CV :\n\n{cv_excerpt}"
                    )
                except Exception as e:
                    logging.warning(f"Claude CV generation failed ({e}), falling back to GPT")
                    try:
                        cv_gen = await _llm_call_with_retry(
                            system_msg=f"""Tu es un rédacteur de CV professionnel. Génère les versions demandées d'un CV. Réponds UNIQUEMENT en JSON valide.
Structure: {{{keys_json}}}
{instructions}""",
                            user_msg=f"Génère les versions de CV pour ce profil:\n\n{cv_excerpt}"
                        )
                    except Exception:
                        logging.warning("Fallback GPT CV generation also failed")

        await db.cv_jobs.update_one({"job_id": job_id}, {"$set": {"step": "Remplissage du passeport..."}})

        cv_models = {
            "classique": cv_gen.get("cv_classique", ""),
            "competences": cv_gen.get("cv_competences", ""),
            "fonctionnel": cv_gen.get("cv_fonctionnel", ""),
            "mixte": cv_gen.get("cv_mixte", ""),
        }
        await db.cv_models.update_one({"token_id": token_id}, {"$set": {"token_id": token_id, "models": cv_models, "original_filename": filename, "analyzed_at": datetime.now(timezone.utc).isoformat()}}, upsert=True)

        passport = await db.passports.find_one({"token_id": token_id})
        if not passport:
            passport = {"token_id": token_id, "professional_summary": "", "career_project": "", "motivations": [], "compatible_environments": [], "target_sectors": [], "competences": [], "experiences": [], "learning_path": [], "passerelles": [], "sharing": {"is_public": False}, "created_at": datetime.now(timezone.utc).isoformat()}
            await db.passports.insert_one(passport)

        new_competences = list(passport.get("competences", []))
        existing_names = {c.get("name", "").lower() for c in new_competences}
        for sf in analysis.get("savoir_faire", []):
            if sf.get("name", "").lower() not in existing_names:
                new_competences.append(PassportCompetence(name=sf["name"], nature="savoir_faire", category=sf.get("category", "technique"), level=sf.get("level", "intermediaire"), source="ia_detectee", ccsp_pole=sf.get("ccsp_pole", ""), ccsp_degree=sf.get("ccsp_degree", "")).model_dump())
                existing_names.add(sf["name"].lower())
        for se in analysis.get("savoir_etre", []):
            if se.get("name", "").lower() not in existing_names:
                new_competences.append(PassportCompetence(name=se["name"], nature="savoir_etre", category=se.get("category", "transversale"), level=se.get("level", "intermediaire"), source="ia_detectee", linked_qualites=se.get("linked_qualites", []), linked_valeurs=se.get("linked_valeurs", []), linked_vertus=se.get("linked_vertus", [])).model_dump())
                existing_names.add(se["name"].lower())

        new_experiences = list(passport.get("experiences", []))
        existing_exp_titles = {e.get("title", "").lower() for e in new_experiences}
        for exp in analysis.get("experiences", []):
            if exp.get("title", "").lower() not in existing_exp_titles:
                new_experiences.append(PassportExperience(title=exp["title"], organization=exp.get("organization", ""), description=exp.get("description", ""), experience_type=exp.get("experience_type", "professionnel"), skills_used=exp.get("skills_used", []), achievements=exp.get("achievements", []), source="ia_detectee").model_dump())
                existing_exp_titles.add(exp["title"].lower())

        new_learning = list(passport.get("learning_path", []))
        for fs in analysis.get("formations_suggestions", []):
            new_learning.append({"title": fs.get("title", ""), "provider": f"Suggestion IA - Priorité {fs.get('priority', 'moyenne')}", "status": "suggere", "skills_acquired": fs.get("skills_to_gain", []), "reason": fs.get("reason", ""), "source": "ia_detectee"})

        profile_data = analysis.get("profile", {})
        update_fields = {"competences": new_competences, "experiences": new_experiences, "learning_path": new_learning, "last_updated": datetime.now(timezone.utc).isoformat()}
        if profile_data.get("professional_summary") and not passport.get("professional_summary"): update_fields["professional_summary"] = profile_data["professional_summary"]
        if profile_data.get("career_project") and not passport.get("career_project"): update_fields["career_project"] = profile_data["career_project"]
        if profile_data.get("motivations") and not passport.get("motivations"): update_fields["motivations"] = profile_data["motivations"]
        if profile_data.get("compatible_environments") and not passport.get("compatible_environments"): update_fields["compatible_environments"] = profile_data["compatible_environments"]
        if profile_data.get("target_sectors") and not passport.get("target_sectors"): update_fields["target_sectors"] = profile_data["target_sectors"]

        merged = {**passport, **update_fields}
        update_fields["completeness_score"] = calculate_completeness(merged)
        await db.passports.update_one({"token_id": token_id}, {"$set": update_fields})

        result = {
            "message": "CV analysé avec succès", "filename": filename,
            "savoir_faire_count": len(analysis.get("savoir_faire", [])),
            "savoir_etre_count": len(analysis.get("savoir_etre", [])),
            "experiences_count": len(analysis.get("experiences", [])),
            "formations_suggestions": analysis.get("formations_suggestions", []),
            "competences_transversales": analysis.get("competences_transversales", []),
            "competences_transferables": analysis.get("competences_transferables", []),
            "offres_emploi_suggerees": analysis.get("offres_emploi_suggerees", []),
            "cv_models_generated": list(cv_models.keys()),
            "completeness_score": update_fields.get("completeness_score", 0),
        }
        await db.cv_jobs.update_one({"job_id": job_id}, {"$set": {"status": "completed", "result": result, "step": "Terminé"}})
        logging.info(f"CV analysis job {job_id} completed successfully")
    except Exception as e:
        logging.error(f"CV analysis job {job_id} failed: {e}")
        await db.cv_jobs.update_one({"job_id": job_id}, {"$set": {"status": "failed", "error": str(e), "step": "Erreur"}})


@router.post("/cv/analyze")
async def analyze_cv(token: str, file: UploadFile = File(...)):
    token_doc = await get_current_token(token)
    ext = (file.filename or "").lower().split(".")[-1]
    if ext not in ("pdf", "docx", "doc", "txt"):
        raise HTTPException(status_code=400, detail="Format non supporté. Utilisez PDF, DOCX ou TXT.")
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 10 Mo)")
    job_id = str(uuid.uuid4())
    await db.cv_jobs.insert_one({"job_id": job_id, "token_id": token_doc["id"], "filename": file.filename, "status": "started", "step": "Démarrage de l'analyse...", "created_at": datetime.now(timezone.utc).isoformat()})
    asyncio.create_task(_run_cv_analysis(job_id, token_doc["id"], file_content, file.filename))
    return {"job_id": job_id, "status": "started", "message": "Analyse lancée en arrière-plan"}


@router.post("/cv/extract-text")
async def extract_cv_text(token: str, file: UploadFile = File(...)):
    await get_current_token(token)
    content = await file.read()
    text = _extract_text_from_bytes(content, file.filename or "file.txt")
    if not text or len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Impossible d'extraire du texte de ce fichier")
    return {"text": text, "length": len(text)}


@router.post("/cv/extract-text-b64")
async def extract_cv_text_base64(token: str, payload: CvBase64Payload):
    await get_current_token(token)
    try:
        content = base64.b64decode(payload.data)
    except Exception:
        raise HTTPException(status_code=400, detail="Données invalides")
    text = _extract_text_from_bytes(content, payload.filename)
    if not text or len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Impossible d'extraire du texte de ce fichier")
    return {"text": text, "length": len(text)}


@router.post("/cv/analyze-text")
async def analyze_cv_text(token: str, payload: CvTextPayload):
    token_doc = await get_current_token(token)
    if not payload.text or len(payload.text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Le texte du CV est trop court pour être analysé")
    job_id = str(uuid.uuid4())
    await db.cv_jobs.insert_one({"job_id": job_id, "token_id": token_doc["id"], "filename": payload.filename, "status": "started", "step": "Démarrage de l'analyse...", "selected_models": payload.selected_models, "created_at": datetime.now(timezone.utc).isoformat()})
    asyncio.create_task(_run_cv_analysis(job_id, token_doc["id"], payload.text.encode("utf-8"), payload.filename, text_ready=True, selected_models=payload.selected_models))
    return {"job_id": job_id, "status": "started", "message": "Analyse lancée en arrière-plan"}


@router.get("/cv/analyze/status")
async def get_cv_analysis_status(token: str, job_id: str):
    token_doc = await get_current_token(token)
    job = await db.cv_jobs.find_one({"job_id": job_id, "token_id": token_doc["id"]}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job non trouvé")
    return {"job_id": job["job_id"], "status": job["status"], "step": job.get("step", ""), "result": job.get("result"), "error": job.get("error")}


@router.get("/cv/latest-analysis")
async def get_latest_cv_analysis(token: str):
    token_doc = await get_current_token(token)
    job = await db.cv_jobs.find_one({"token_id": token_doc["id"], "status": "completed"}, {"_id": 0}, sort=[("created_at", -1)])
    if not job or not job.get("result"):
        return {"has_analysis": False}
    return {"has_analysis": True, "result": job["result"]}


@router.get("/cv/models")
async def get_cv_models(token: str):
    token_doc = await get_current_token(token)
    cv_data = await db.cv_models.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not cv_data:
        return {"models": {}, "analyzed_at": None, "original_filename": None}
    return {"models": cv_data.get("models", {}), "analyzed_at": cv_data.get("analyzed_at"), "original_filename": cv_data.get("original_filename")}
