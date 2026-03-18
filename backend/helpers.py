import json
import uuid
import logging
import io
from typing import List, Dict, Any

import PyPDF2
from fastapi import HTTPException
from emergentintegrations.llm.chat import LlmChat, UserMessage

from db import db, EMERGENT_LLM_KEY


async def get_current_token(token: str) -> dict:
    token_doc = await db.tokens.find_one({"token": token}, {"_id": 0})
    if not token_doc:
        raise HTTPException(status_code=401, detail="Token invalide")
    return token_doc


async def _llm_call_with_retry(system_msg: str, user_msg: str, max_retries: int = 2) -> dict:
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"cv-{uuid.uuid4()}",
                system_message=system_msg
            ).with_model("openai", "gpt-5.2")
            response = await chat.send_message(UserMessage(text=user_msg))
            raw = response.strip() if isinstance(response, str) else response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
                raw = raw.strip()
            return json.loads(raw)
        except json.JSONDecodeError as e:
            last_error = f"Réponse IA non valide (tentative {attempt+1})"
            logging.warning(f"CV analysis JSON error attempt {attempt+1}: {e}")
        except Exception as e:
            last_error = str(e)
            logging.warning(f"CV analysis LLM error attempt {attempt+1}: {e}")
    raise Exception(f"Erreur IA après {max_retries+1} tentatives: {last_error}")


def _extract_text_from_bytes(content: bytes, filename: str) -> str:
    text = ""
    if filename.lower().endswith(".pdf"):
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
    elif filename.lower().endswith((".docx", ".doc")):
        import docx
        doc = docx.Document(io.BytesIO(content))
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        text = content.decode("utf-8", errors="ignore")
    return text.strip()


async def calculate_match_with_ai(profile_skills: List[str], job_requirements: List[str], profile_sectors: List[str], job_sector: str) -> Dict[str, Any]:
    if not EMERGENT_LLM_KEY:
        common_skills = set(profile_skills) & set(job_requirements)
        score = int((len(common_skills) / max(len(job_requirements), 1)) * 100)
        return {"score": min(score + 20, 100), "rationale": "Correspondance basée sur les compétences communes."}
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"match-{uuid.uuid4()}",
            system_message="Tu es un expert RH français. Analyse la correspondance entre un profil et une offre d'emploi. Réponds en JSON avec 'score' (0-100) et 'rationale' (explication courte en français)."
        ).with_model("openai", "gpt-5.2")
        prompt = f"""
        Compétences du candidat: {', '.join(profile_skills)}
        Compétences requises pour le poste: {', '.join(job_requirements)}
        Secteurs du candidat: {', '.join(profile_sectors)}
        Secteur du poste: {job_sector}
        Calcule un score de correspondance et explique pourquoi.
        """
        response = await chat.send_message(UserMessage(text=prompt))
        try:
            result = json.loads(response)
            return {"score": result.get("score", 50), "rationale": result.get("rationale", "Analyse IA")}
        except Exception:
            return {"score": 65, "rationale": response[:200]}
    except Exception as e:
        logging.error(f"AI matching error: {e}")
        common_skills = set(profile_skills) & set(job_requirements)
        score = int((len(common_skills) / max(len(job_requirements), 1)) * 100)
        return {"score": min(score + 20, 100), "rationale": "Correspondance basée sur les compétences communes."}
