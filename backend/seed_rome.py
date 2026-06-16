"""
Seed ROME 4.0 : Import des métiers France Travail dans MongoDB
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

ROME_GRANDS_DOMAINES = {
    "A": "Agriculture et Pêche, Espaces naturels et Espaces verts, Soins aux animaux",
    "B": "Arts et Façonnage d'ouvrages d'art",
    "C": "Banque, Assurance, Immobilier",
    "D": "Commerce, Vente et Grande distribution",
    "E": "Communication, Média et Multimédia",
    "F": "Construction, Bâtiment et Travaux publics",
    "G": "Hôtellerie-Restauration, Tourisme, Loisirs et Animation",
    "H": "Industrie",
    "I": "Installation et Maintenance",
    "J": "Santé",
    "K": "Services à la personne et à la collectivité",
    "L": "Spectacle",
    "M": "Support à l'entreprise",
    "N": "Transport et Logistique",
}


async def seed_rome():
    from opc.connecteurs.france_travail import FranceTravailClient

    client_ft = FranceTravailClient()
    if not client_ft.is_configured():
        print("❌ France Travail non configuré (FRANCE_TRAVAIL_CLIENT_ID/SECRET manquants)")
        return

    print("📡 Connexion à l'API France Travail ROME 4.0...")
    metiers_rome = await client_ft.get_metiers_rome()
    print(f"✓ {len(metiers_rome)} fiches ROME récupérées")

    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    await db.rome_metiers.drop()

    docs = []
    for m in metiers_rome:
        code = m.get("code", "")
        libelle = m.get("libelle", "")
        prefix = code[0] if code else ""
        grand_domaine = ROME_GRANDS_DOMAINES.get(prefix, "Inconnu")

        docs.append({
            "code_rome": code,
            "libelle": libelle,
            "grand_domaine_code": prefix,
            "grand_domaine_nom": grand_domaine,
            "source": "france_travail_rome_4",
        })

    if docs:
        await db.rome_metiers.insert_many(docs)

    await db.rome_metiers.create_index("code_rome")
    await db.rome_metiers.create_index("grand_domaine_code")
    await db.rome_metiers.create_index([("libelle", "text")])

    # Stats
    for prefix in sorted(ROME_GRANDS_DOMAINES.keys()):
        count = await db.rome_metiers.count_documents({"grand_domaine_code": prefix})
        print(f"  {prefix}: {count:4d} métiers — {ROME_GRANDS_DOMAINES[prefix][:50]}")

    total = await db.rome_metiers.count_documents({})
    print(f"\n✅ {total} fiches ROME importées dans MongoDB")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_rome())
