"""Script d'enrichissement CK1 par IA pour les fiches métiers du référentiel OPC.
Utilise GPT-5.2 via Emergent LLM Key pour générer les compétences CK1 manquantes."""
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

BATCH_SIZE = 5  # Process 5 fiches per LLM call

PROMPT_TEMPLATE = """Tu es un expert en psychologie du travail et en ingénierie des compétences.
Pour chaque métier ci-dessous, génère les données CK1 (Compétences, Vertus, Valeurs, Qualités humaines).

IMPORTANT: Réponds UNIQUEMENT en JSON valide, sans commentaires ni markdown.

Format attendu pour chaque métier:
{{
  "metier": "nom_du_metier",
  "ck1_vertus": ["COURAGE", "SAGESSE", ...],
  "ck1_valeurs": ["PERSEVERANCE", "CREATIVITE", ...],
  "ck1_qualites_humaines": ["ADAPTABILITE", "RIGUEUR", ...],
  "ck1_comp_cognitives": ["Résolution de problèmes", "Analyse critique", ...],
  "ck1_comp_emotionnelles": ["Gestion du stress", "Empathie", ...],
  "ck1_comp_sociales": ["Travail en équipe", "Communication", ...]
}}

Règles:
- ck1_vertus: 4-6 vertus cardinales EN MAJUSCULES (CONNAISSANCE, DROITURE, JUSTICE, PRUDENCE, SAGESSE, TRANSCENDANCE, COURAGE, TEMPERANCE)
- ck1_valeurs: 10-16 valeurs EN MAJUSCULES pertinentes au métier
- ck1_qualites_humaines: 10-15 qualités EN MAJUSCULES
- ck1_comp_cognitives: 8-12 compétences cognitives (Première lettre majuscule)
- ck1_comp_emotionnelles: 8-11 compétences émotionnelles (Première lettre majuscule)
- ck1_comp_sociales: 6-9 compétences sociales EN MAJUSCULES

Métiers à traiter:
{metiers_list}

Réponds avec un tableau JSON: [{{}}, {{}}, ...]"""


async def enrich_batch(metiers_batch, db):
    """Enrich a batch of fiches using GPT-5.2."""
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    metiers_list = "\n".join([f"- {m['metier']} (mission: {(m.get('mission') or '')[:100]})" for m in metiers_batch])

    chat = LlmChat(
        api_key=EMERGENT_KEY,
        session_id="ck1-enrich-batch",
        system_message="Tu es un expert en archéologie des compétences. Réponds uniquement en JSON valide."
    ).with_model("openai", "gpt-5.2")

    prompt = PROMPT_TEMPLATE.format(metiers_list=metiers_list)
    response = await asyncio.to_thread(
        lambda: asyncio.run(chat.send_message(UserMessage(text=prompt)))
    )

    text = str(response).strip()
    # Clean up markdown code blocks if present
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
        # Find matching fiche
        for fiche in metiers_batch:
            if fiche["metier"].strip().lower() == metier_name or metier_name in fiche["metier"].strip().lower():
                update_data = {}
                for key in ["ck1_vertus", "ck1_valeurs", "ck1_qualites_humaines", "ck1_comp_cognitives", "ck1_comp_emotionnelles", "ck1_comp_sociales"]:
                    if key in result and isinstance(result[key], list) and len(result[key]) > 0:
                        update_data[key] = result[key]

                if update_data:
                    await db.referentiel_opc.update_one(
                        {"metier": fiche["metier"]},
                        {"$set": update_data}
                    )
                    updated += 1
                    print(f"  ✓ {fiche['metier']} — {len(update_data)} champs enrichis")
                break

    return updated


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    # Get all non-enriched fiches
    fiches = await db.referentiel_opc.find(
        {"$or": [{"ck1_vertus": {"$exists": False}}, {"ck1_vertus": []}]},
        {"_id": 0, "metier": 1, "mission": 1, "hard_skills": 1, "filiere": 1}
    ).to_list(100)

    total = len(fiches)
    print(f"\n{'='*60}")
    print(f"  Enrichissement CK1 par IA — {total} fiches à traiter")
    print(f"{'='*60}\n")

    if total == 0:
        print("Toutes les fiches sont déjà enrichies !")
        return

    total_updated = 0
    for i in range(0, total, BATCH_SIZE):
        batch = fiches[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"\n[Batch {batch_num}/{total_batches}] Traitement de {len(batch)} fiches...")

        try:
            updated = await enrich_batch(batch, db)
            total_updated += updated
            print(f"  → {updated}/{len(batch)} fiches enrichies")
        except json.JSONDecodeError as e:
            print(f"  ✗ Erreur JSON batch {batch_num}: {e}")
        except Exception as e:
            print(f"  ✗ Erreur batch {batch_num}: {e}")

        # Small delay between batches
        if i + BATCH_SIZE < total:
            await asyncio.sleep(1)

    print(f"\n{'='*60}")
    print(f"  Résultat: {total_updated}/{total} fiches enrichies")
    print(f"{'='*60}\n")

    # Verify
    enriched_count = await db.referentiel_opc.count_documents({"ck1_vertus": {"$exists": True, "$ne": []}})
    print(f"Total fiches enrichies CK1: {enriched_count}/68")


if __name__ == "__main__":
    asyncio.run(main())
