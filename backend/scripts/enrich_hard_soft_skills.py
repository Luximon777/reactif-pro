"""Script d'enrichissement Hard Skills / Soft Skills par IA pour les 68 fiches métiers."""
import asyncio
import json
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

EMERGENT_KEY = os.environ.get('EMERGENT_LLM_KEY')
MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

BATCH_SIZE = 10

PROMPT_TEMPLATE = """Tu es un expert en compétences professionnelles.
Pour chaque métier ci-dessous, génère des Hard Skills (compétences techniques concrètes, courtes — 3-5 mots max par skill) et Soft Skills (compétences comportementales, courtes).

IMPORTANT: Réponds UNIQUEMENT en JSON valide, sans commentaires ni markdown.

Format pour chaque métier:
{{
  "metier": "nom_exact_du_metier",
  "hard_skills": ["Gestion de projet", "Analyse de données", "Excel avancé", ...],
  "soft_skills": ["Leadership", "Communication", "Travail d'équipe", ...]
}}

Règles:
- hard_skills: 6-10 compétences techniques COURTES et spécifiques au métier
- soft_skills: 5-8 compétences comportementales COURTES
- Chaque skill = 2-5 mots maximum
- Pas de phrases longues

Métiers:
{metiers_list}

Réponds avec un tableau JSON: [{{}}, {{}}, ...]"""


async def enrich_batch(metiers_batch, db):
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    metiers_list = "\n".join([f"- {m['metier']}" for m in metiers_batch])

    chat = LlmChat(
        api_key=EMERGENT_KEY,
        session_id="hs-ss-enrich",
        system_message="Tu es un expert RH. Réponds uniquement en JSON valide."
    ).with_model("openai", "gpt-5.2")

    prompt = PROMPT_TEMPLATE.format(metiers_list=metiers_list)
    response = await asyncio.to_thread(
        lambda: asyncio.run(chat.send_message(UserMessage(text=prompt)))
    )

    text = str(response).strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    if text.startswith("json"):
        text = text[4:].strip()

    results = json.loads(text)
    if not isinstance(results, list):
        results = [results]

    updated = 0
    for result in results:
        metier_name = result.get("metier", "").strip().lower()
        for fiche in metiers_batch:
            if fiche["metier"].strip().lower() == metier_name or metier_name in fiche["metier"].strip().lower() or fiche["metier"].strip().lower() in metier_name:
                update_data = {}
                hs = result.get("hard_skills", [])
                ss = result.get("soft_skills", [])
                if isinstance(hs, list) and len(hs) > 0:
                    update_data["hard_skills"] = hs
                if isinstance(ss, list) and len(ss) > 0:
                    update_data["soft_skills"] = ss
                if update_data:
                    await db.referentiel_opc.update_one(
                        {"metier": fiche["metier"]},
                        {"$set": update_data}
                    )
                    updated += 1
                    print(f"  ✓ {fiche['metier']} — HS:{len(hs)} SS:{len(ss)}")
                break
    return updated


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    fiches = await db.referentiel_opc.find(
        {"$or": [{"hard_skills": {"$exists": False}}, {"hard_skills": []}, {"hard_skills": {"$size": 0}}]},
        {"_id": 0, "metier": 1}
    ).to_list(100)

    total = len(fiches)
    print(f"\n{'='*60}")
    print(f"  Enrichissement Hard/Soft Skills — {total} fiches")
    print(f"{'='*60}\n")

    if total == 0:
        print("Toutes les fiches ont déjà des hard_skills !")
        return

    total_updated = 0
    for i in range(0, total, BATCH_SIZE):
        batch = fiches[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"\n[Batch {batch_num}/{total_batches}] {len(batch)} fiches...")
        try:
            updated = await enrich_batch(batch, db)
            total_updated += updated
        except Exception as e:
            print(f"  ✗ Erreur batch {batch_num}: {e}")
        if i + BATCH_SIZE < total:
            await asyncio.sleep(1)

    print(f"\n{'='*60}")
    print(f"  Résultat: {total_updated}/{total} fiches enrichies")
    print(f"{'='*60}")

    hs_count = await db.referentiel_opc.count_documents({"hard_skills": {"$exists": True, "$ne": []}})
    ss_count = await db.referentiel_opc.count_documents({"soft_skills": {"$exists": True, "$ne": []}})
    print(f"Hard Skills non-vide: {hs_count}/68")
    print(f"Soft Skills non-vide: {ss_count}/68")


if __name__ == "__main__":
    asyncio.run(main())
