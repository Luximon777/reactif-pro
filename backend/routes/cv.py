from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
import asyncio
import uuid
import json
import logging
import base64
import io
from datetime import datetime, timezone
from models import CvTextPayload, CvBase64Payload, PassportCompetence, PassportExperience
from db import db, EMERGENT_LLM_KEY
from helpers import get_current_token, _llm_call_with_retry, _extract_text_from_bytes
from routes.passport import calculate_completeness
from emergentintegrations.llm.chat import LlmChat, UserMessage
from pydantic import BaseModel
from typing import List

router = APIRouter()


class GenerateModelRequest(BaseModel):
    model_types: List[str]


async def _claude_generate_single_cv(cv_text: str, model_type: str) -> dict:
    """Use Claude to generate structured CV content as JSON sections"""
    model_descriptions = {
        "classique": "CV chronologique classique : profil, expériences par ordre chronologique inverse, formation, compétences.",
        "competences": "CV axé compétences : compétences clés regroupées par domaine en premier, puis expériences.",
        "fonctionnel": "CV fonctionnel : compétences par domaines fonctionnels, sans chronologie stricte.",
        "mixte": "CV mixte : parcours chronologique + compétences transférables mises en valeur.",
    }
    desc = model_descriptions.get(model_type, model_descriptions["classique"])

    for attempt in range(3):
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"cv-gen-{uuid.uuid4()}",
                system_message=f"""Tu es un rédacteur de CV professionnel expert en France.
Génère un CV complet et détaillé. Réponds UNIQUEMENT en JSON valide.

Type : {desc}

Structure JSON exacte :
{{
  "nom": "Prénom NOM",
  "titre": "Titre professionnel",
  "contact": {{"email": "...", "telephone": "...", "adresse": "...", "linkedin": "..."}},
  "profil": "Résumé professionnel en 3-4 phrases percutantes",
  "competences_cles": ["compétence 1", "compétence 2", ...],
  "experiences": [
    {{"poste": "...", "entreprise": "...", "periode": "...", "missions": ["mission 1", "mission 2", ...]}}
  ],
  "formations": [
    {{"diplome": "...", "etablissement": "...", "annee": "..."}}
  ],
  "competences_techniques": {{"Domaine 1": ["comp1", "comp2"], "Domaine 2": ["comp3"]}},
  "langues": [{{"langue": "...", "niveau": "..."}}],
  "centres_interet": ["..."]
}}

IMPORTANT : Contenu riche et détaillé, minimum 6 expériences/missions par poste, vocabulaire professionnel."""
            ).with_model("anthropic", "claude-sonnet-4-5-20250929")
            response = await chat.send_message(UserMessage(text=f"Reconstitue ce CV au format '{model_type}' :\n\n{cv_text[:6000]}"))
            raw = response.strip() if isinstance(response, str) else response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
                raw = raw.strip()
            return json.loads(raw)
        except json.JSONDecodeError:
            logging.warning(f"Claude CV gen JSON error attempt {attempt+1}")
        except Exception as e:
            logging.warning(f"Claude CV gen attempt {attempt+1} failed: {e}")
            if attempt == 2:
                try:
                    chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"cv-gpt-{uuid.uuid4()}", system_message=f"Génère un CV en JSON structuré. Type: {desc}. Même structure JSON que demandé.").with_model("openai", "gpt-5.2")
                    response = await chat.send_message(UserMessage(text=f"CV :\n\n{cv_text[:6000]}"))
                    raw = response.strip() if isinstance(response, str) else response.text.strip()
                    if raw.startswith("```"):
                        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                        if raw.endswith("```"):
                            raw = raw[:-3]
                    return json.loads(raw.strip())
                except Exception as e2:
                    raise Exception(f"Impossible de générer le CV: {e2}")
    raise Exception("Échec après 3 tentatives")


def _build_docx(cv_data: dict, model_type: str) -> bytes:
    """Build a professionally formatted DOCX from structured CV data"""
    from docx import Document
    from docx.shared import Pt, Inches, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    # Page margins
    for section in doc.sections:
        section.top_margin = Cm(1.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(10)
    font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    NAVY = RGBColor(0x1e, 0x3a, 0x5f)
    DARK = RGBColor(0x1e, 0x29, 0x3b)
    GRAY = RGBColor(0x64, 0x74, 0x8b)

    def add_heading_styled(text, level=1):
        h = doc.add_heading(text, level=level)
        for run in h.runs:
            run.font.color.rgb = NAVY
            run.font.name = 'Calibri'
        return h

    # Name
    name = cv_data.get("nom", "Candidat")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(name.upper())
    run.font.size = Pt(22)
    run.font.color.rgb = NAVY
    run.bold = True
    run.font.name = 'Calibri'

    # Title
    titre = cv_data.get("titre", "")
    if titre:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(titre)
        run.font.size = Pt(13)
        run.font.color.rgb = GRAY
        run.font.name = 'Calibri'

    # Contact
    contact = cv_data.get("contact", {})
    contact_parts = []
    if contact.get("email"): contact_parts.append(contact["email"])
    if contact.get("telephone"): contact_parts.append(contact["telephone"])
    if contact.get("adresse"): contact_parts.append(contact["adresse"])
    if contact_parts:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(" | ".join(contact_parts))
        run.font.size = Pt(9)
        run.font.color.rgb = GRAY

    # Separator
    doc.add_paragraph("_" * 60).runs[0].font.color.rgb = RGBColor(0xd1, 0xd5, 0xdb)

    # Profile
    profil = cv_data.get("profil", "")
    if profil:
        add_heading_styled("PROFIL PROFESSIONNEL", level=2)
        p = doc.add_paragraph(profil)
        p.paragraph_format.space_after = Pt(6)

    # Key skills
    competences_cles = cv_data.get("competences_cles", [])
    if competences_cles:
        add_heading_styled("COMPÉTENCES CLÉS", level=2)
        p = doc.add_paragraph(" • ".join(competences_cles))
        for run in p.runs:
            run.font.size = Pt(10)

    # Experiences
    experiences = cv_data.get("experiences", [])
    if experiences:
        add_heading_styled("EXPÉRIENCES PROFESSIONNELLES", level=2)
        for exp in experiences:
            p = doc.add_paragraph()
            run = p.add_run(exp.get("poste", ""))
            run.bold = True
            run.font.size = Pt(11)
            run.font.color.rgb = DARK
            if exp.get("entreprise") or exp.get("periode"):
                run = p.add_run(f"\n{exp.get('entreprise', '')} — {exp.get('periode', '')}")
                run.font.size = Pt(9)
                run.font.color.rgb = GRAY
            for mission in exp.get("missions", []):
                mp = doc.add_paragraph(mission, style='List Bullet')
                mp.paragraph_format.space_after = Pt(1)
                mp.paragraph_format.left_indent = Cm(1)

    # Education
    formations = cv_data.get("formations", [])
    if formations:
        add_heading_styled("FORMATION", level=2)
        for f in formations:
            p = doc.add_paragraph()
            run = p.add_run(f.get("diplome", ""))
            run.bold = True
            run.font.color.rgb = DARK
            details = []
            if f.get("etablissement"): details.append(f["etablissement"])
            if f.get("annee"): details.append(f["annee"])
            if details:
                run = p.add_run(f"\n{' — '.join(details)}")
                run.font.size = Pt(9)
                run.font.color.rgb = GRAY

    # Technical skills
    comp_tech = cv_data.get("competences_techniques", {})
    if comp_tech:
        add_heading_styled("COMPÉTENCES TECHNIQUES", level=2)
        for domain, skills in comp_tech.items():
            p = doc.add_paragraph()
            run = p.add_run(f"{domain} : ")
            run.bold = True
            run.font.size = Pt(10)
            run = p.add_run(", ".join(skills) if isinstance(skills, list) else str(skills))
            run.font.size = Pt(10)

    # Languages
    langues = cv_data.get("langues", [])
    if langues:
        add_heading_styled("LANGUES", level=2)
        for l in langues:
            doc.add_paragraph(f"{l.get('langue', '')} — {l.get('niveau', '')}")

    # Interests
    centres = cv_data.get("centres_interet", [])
    if centres:
        add_heading_styled("CENTRES D'INTÉRÊT", level=2)
        doc.add_paragraph(" • ".join(centres))

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


async def _run_cv_analysis(job_id: str, token_id: str, file_content: bytes, filename: str, text_ready: bool = False):
    """Analysis only - no CV generation. Fast."""
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

        # Store CV text for later model generation
        await db.cv_texts.update_one(
            {"token_id": token_id},
            {"$set": {"token_id": token_id, "text": cv_text, "filename": filename, "updated_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )

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
- competences_transversales: liste de 5-10 compétences transversales identifiées
- offres_emploi_suggerees: liste de 3-5 offres d'emploi pertinentes
Valeurs IDs: autonomie, stimulation, hedonisme, realisation_de_soi, pouvoir, securite, conformite, tradition, bienveillance, universalisme.
Vertus: sagesse, courage, humanite, justice, temperance, transcendance.""",
            user_msg=f"Analyse ce CV:\n\n{cv_excerpt}"
        )

        await db.cv_jobs.update_one({"job_id": job_id}, {"$set": {"step": "Remplissage du passeport..."}})

        # Fill passport from analysis
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
    await db.cv_jobs.insert_one({"job_id": job_id, "token_id": token_doc["id"], "filename": payload.filename, "status": "started", "step": "Démarrage de l'analyse...", "created_at": datetime.now(timezone.utc).isoformat()})
    asyncio.create_task(_run_cv_analysis(job_id, token_doc["id"], payload.text.encode("utf-8"), payload.filename, text_ready=True))
    return {"job_id": job_id, "status": "started", "message": "Analyse lancée en arrière-plan"}


@router.post("/cv/generate-models")
async def generate_cv_models(token: str, request: GenerateModelRequest):
    """Generate selected CV models on demand using Claude AI"""
    token_doc = await get_current_token(token)
    valid_types = {"classique", "competences", "fonctionnel", "mixte"}
    selected = [m for m in request.model_types if m in valid_types]
    if not selected:
        raise HTTPException(status_code=400, detail="Aucun type de modèle valide sélectionné")

    cv_text_doc = await db.cv_texts.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not cv_text_doc or not cv_text_doc.get("text"):
        raise HTTPException(status_code=404, detail="Aucun CV analysé. Veuillez d'abord uploader votre CV.")

    job_id = str(uuid.uuid4())
    await db.cv_gen_jobs.insert_one({"job_id": job_id, "token_id": token_doc["id"], "model_types": selected, "status": "started", "progress": 0, "total": len(selected), "created_at": datetime.now(timezone.utc).isoformat()})

    async def _generate_all():
        try:
            for i, model_type in enumerate(selected):
                await db.cv_gen_jobs.update_one({"job_id": job_id}, {"$set": {"status": "generating", "progress": i, "current_model": model_type}})
                cv_data = await _claude_generate_single_cv(cv_text_doc["text"], model_type)
                # Build DOCX
                docx_bytes = _build_docx(cv_data, model_type)
                docx_b64 = base64.b64encode(docx_bytes).decode("utf-8")
                # Store structured data + DOCX
                await db.cv_models.update_one(
                    {"token_id": token_doc["id"]},
                    {"$set": {
                        f"models.{model_type}": json.dumps(cv_data, ensure_ascii=False),
                        f"docx.{model_type}": docx_b64,
                        "analyzed_at": datetime.now(timezone.utc).isoformat()
                    }},
                    upsert=True
                )
            await db.cv_gen_jobs.update_one({"job_id": job_id}, {"$set": {"status": "completed", "progress": len(selected)}})
        except Exception as e:
            logging.error(f"CV models generation failed: {e}")
            await db.cv_gen_jobs.update_one({"job_id": job_id}, {"$set": {"status": "failed", "error": str(e)}})

    asyncio.create_task(_generate_all())
    return {"job_id": job_id, "status": "started", "model_types": selected, "total": len(selected)}


@router.get("/cv/download/{model_type}")
async def download_cv_docx(token: str, model_type: str):
    """Download a generated CV as DOCX file"""
    token_doc = await get_current_token(token)
    if model_type not in ("classique", "competences", "fonctionnel", "mixte"):
        raise HTTPException(status_code=400, detail="Type de modèle invalide")
    cv_doc = await db.cv_models.find_one({"token_id": token_doc["id"]}, {"_id": 0})
    if not cv_doc or not cv_doc.get("docx", {}).get(model_type):
        raise HTTPException(status_code=404, detail="Ce modèle de CV n'a pas encore été généré")
    docx_bytes = base64.b64decode(cv_doc["docx"][model_type])
    filename = f"CV_{model_type.capitalize()}.docx"
    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/cv/generate-models/status")
async def get_cv_generate_status(token: str, job_id: str):
    token_doc = await get_current_token(token)
    job = await db.cv_gen_jobs.find_one({"job_id": job_id, "token_id": token_doc["id"]}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job non trouvé")
    return {"job_id": job["job_id"], "status": job["status"], "progress": job.get("progress", 0), "total": job.get("total", 0), "current_model": job.get("current_model"), "error": job.get("error")}


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
