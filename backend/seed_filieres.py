"""
Seed script : Import FILIERES PROFESSIONNELLES.ods into MongoDB
Structure pyramidale : Filière → Secteur → Métier → Compétences
"""
import asyncio
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")


async def seed_filieres():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    # Load parsed data
    with open(os.path.join(os.path.dirname(__file__), "parsed_filieres.json")) as f:
        data = json.load(f)

    filieres = data["filieres"]
    metiers_raw = data["metiers"]
    metier_details = data.get("metier_details", [])
    qualites = data.get("qualites_humaines", [])

    # Build detail lookup by detail_code
    detail_lookup = {}
    for md in metier_details:
        key = md["detail_code"]
        detail_lookup[key] = md

    # Build qualites lookup by ref_code
    qualite_lookup = {}
    for q in qualites:
        ref = q["ref_code"].strip().replace(" ", "")
        if ref not in qualite_lookup:
            qualite_lookup[ref] = []
        qualite_lookup[ref].append({
            "savoir_etre": q["savoir_etre"],
            "qualite_humaine": q["qualite_humaine"]
        })

    # ========= 1. Seed opc_filieres =========
    await db.opc_filieres.drop()
    filiere_docs = []
    for f in filieres:
        filiere_docs.append({
            "numero": f["numero"],
            "nom": f["nom"],
            "code": f["code"],
            "secteurs": f["secteurs"]
        })
    if filiere_docs:
        await db.opc_filieres.insert_many(filiere_docs)
    print(f"✓ {len(filiere_docs)} filières insérées")

    # ========= 2. Seed opc_metiers =========
    await db.opc_metiers.drop()

    # Map sector_code to filiere
    sector_to_filiere = {}
    for m in metiers_raw:
        fc = m.get("filiere_code", "")
        sc = m.get("sector_code", "")
        sn = m.get("sector_name", "")
        if fc and sc:
            sector_to_filiere[sc] = {"filiere_code": fc, "sector_name": sn}

    metier_docs = []
    for m in metiers_raw:
        fc = m.get("filiere_code", "")
        sc = m.get("sector_code", "")
        sn = m.get("sector_name", "")
        metier_name = m.get("metier", "")
        mission = m.get("mission", "")

        # Find the filière name
        filiere_nom = ""
        filiere_code = fc
        for f in filieres:
            if f["code"] == fc:
                filiere_nom = f["nom"]
                break

        # Look for detailed competences
        detail = None
        for md in metier_details:
            if md["metier"].lower().strip() == metier_name.lower().strip():
                detail = md
                break

        doc = {
            "filiere_code": filiere_code,
            "filiere_nom": filiere_nom,
            "sector_code": sc,
            "sector_name": sn,
            "metier": metier_name,
            "mission": mission,
            "savoir_faire": detail["savoir_faire"] if detail else [],
            "capacites_techniques": detail["capacites_techniques"] if detail else [],
            "savoir_etre": detail["savoir_etre"] if detail else [],
            "capacites_professionnelles": detail["capacites_professionnelles"] if detail else [],
        }

        # Add qualites humaines if available
        if detail:
            ref_key = f"{sc}/{detail.get('detail_code', '')}".replace(" ", "")
            alt_key = detail.get("detail_code", "")
            qh = qualite_lookup.get(ref_key) or qualite_lookup.get(alt_key) or []
            # Also try with the sector_code prefix
            for k, v in qualite_lookup.items():
                if alt_key and alt_key in k:
                    qh = v
                    break
            doc["qualites_humaines"] = qh
        else:
            doc["qualites_humaines"] = []

        metier_docs.append(doc)

    if metier_docs:
        await db.opc_metiers.insert_many(metier_docs)
    print(f"✓ {len(metier_docs)} métiers insérés")

    # ========= 3. Seed opc_qualites =========
    await db.opc_qualites.drop()
    if qualites:
        await db.opc_qualites.insert_many([{**q} for q in qualites])
    print(f"✓ {len(qualites)} qualités humaines insérées")

    # ========= 4. Create indexes =========
    await db.opc_filieres.create_index("code")
    await db.opc_filieres.create_index("nom")
    await db.opc_metiers.create_index("filiere_code")
    await db.opc_metiers.create_index("sector_name")
    await db.opc_metiers.create_index("metier")
    await db.opc_metiers.create_index([("metier", "text"), ("sector_name", "text"), ("mission", "text")])
    print("✓ Index créés")

    client.close()
    print("\n✅ Seed terminé avec succès !")


if __name__ == "__main__":
    asyncio.run(seed_filieres())
