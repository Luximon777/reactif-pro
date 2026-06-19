"""Shared database connection and utilities for all route modules."""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from fastapi import HTTPException
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
gridfs_bucket = AsyncIOMotorGridFSBucket(db, bucket_name="proof_documents")

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')


async def get_current_token(token: str) -> dict:
    token_doc = await db.tokens.find_one({"token": token}, {"_id": 0})
    if not token_doc:
        raise HTTPException(status_code=401, detail="Token invalide")
    return token_doc


def _sync_llm_call(chat, message):
    """Run async LLM call synchronously in a thread."""
    return asyncio.run(chat.send_message(message))


async def run_llm_nonblocking(chat, message):
    """Run LLM call in a thread pool to avoid blocking the FastAPI event loop."""
    return await asyncio.to_thread(_sync_llm_call, chat, message)


_SECTOR_KEYWORDS = {
    "Restauration": ["cuisine", "cuisinier", "serveur", "restauration", "chef", "commis", "plonge", "rang", "salle", "buffalo", "mcdonald", "quick", "pizz"],
    "Hôtellerie": ["hôtel", "réception", "hébergement", "tourisme", "ibis", "novotel", "accor", "camping"],
    "Propreté & Services": ["entretien", "nettoyage", "propreté", "ménage", "agent entretien", "maintenance bâtiment"],
    "Logistique & Transport": ["logistique", "magasinier", "préparateur", "commande", "cariste", "chauffeur", "livreur", "manutention", "quai", "colis", "expédition"],
    "Commerce & Vente": ["vente", "vendeur", "commerce", "commercial", "caissier", "rayon", "magasin", "retail", "clientèle"],
    "BTP & Construction": ["btp", "maçon", "électricien", "plombier", "chantier", "construction", "conducteur travaux", "peintre bâtiment"],
    "Industrie & Production": ["industrie", "usine", "production", "opérateur", "conducteur ligne", "soudeur", "technicien maintenance"],
    "Petite Enfance & Social": ["enfant", "crèche", "animat", "éducateur", "éducatrice", "moniteur", "insertion", "social", "petite enfance", "assistante maternelle", "puériculture", "sieste", "change", "parents", "maternelle", "ase", "atsem", "périscolaire"],
    "Santé & Médico-social": ["santé", "soignant", "infirmier", "aide-soignant", "ehpad", "médico-social", "paramédical", "pharmacie"],
    "Informatique & Numérique": ["développeur", "informatique", "numérique", "data", "web", "digital", "devops", "systèmes", "réseau"],
    "Comptabilité, Finance & RH": ["comptab", "paie", "finance", "audit", "ressources humaines", "contrôle gestion", "facturation", "bilan"],
    "Communication & Marketing": ["community", "graphi", "rédact", "content", "traffic", "publicité", "réseaux sociaux"],
    "Agriculture & Agroalimentaire": ["agricul", "agro", "culture", "élevage", "viticul", "maraîch"],
    "Administration & Secrétariat": ["secrétariat", "administratif", "office manager", "standardiste", "assistante direction", "archivage"],
}


def _infer_sectors_from_profile(experiences, savoir_faire):
    """Infer user's sectors from their experience titles, orgs and skills."""
    sector_scores = {}
    texts = []
    for e in (experiences or []):
        if isinstance(e, dict):
            texts.append(e.get("title", "").lower())
            texts.append(e.get("organization", "").lower())
            if e.get("sector"):
                texts.append(e["sector"].lower())
    for s in (savoir_faire or []):
        name = s.get("name", "") if isinstance(s, dict) else str(s)
        texts.append(name.lower())

    combined = " ".join(texts)
    for sector, keywords in _SECTOR_KEYWORDS.items():
        score = sum(combined.count(kw) for kw in keywords)
        if score > 0:
            sector_scores[sector] = score

    sorted_sectors = sorted(sector_scores.items(), key=lambda x: -x[1])
    return [s[0] for s in sorted_sectors]
