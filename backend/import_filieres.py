"""Import ODS file into MongoDB referentiel_metiers collection."""
import asyncio
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "reactif_pro")

# Mapping savoir-être → qualités humaines → valeurs → vertus
SE_QUALITES_VALEURS_VERTUS = {
    "Résolution de problèmes": {"qualites": ["Perspicacité"], "valeurs": ["realisation_de_soi", "autonomie"], "vertus": ["sagesse"]},
    "Pensée critique": {"qualites": ["Perspicacité"], "valeurs": ["autonomie", "stimulation"], "vertus": ["sagesse"]},
    "Créativité": {"qualites": ["Créativité"], "valeurs": ["stimulation", "autonomie"], "vertus": ["sagesse", "transcendance"]},
    "Adaptabilité": {"qualites": ["Flexibilité"], "valeurs": ["autonomie", "stimulation"], "vertus": ["courage", "temperance"]},
    "Collaboration": {"qualites": ["Esprit d'équipe"], "valeurs": ["bienveillance", "universalisme"], "vertus": ["humanite", "justice"]},
    "Communication": {"qualites": ["Empathie"], "valeurs": ["bienveillance"], "vertus": ["humanite"]},
    "Gestion du temps": {"qualites": ["Rigueur"], "valeurs": ["realisation_de_soi", "conformite"], "vertus": ["temperance"]},
    "Persévérance": {"qualites": ["Courageux"], "valeurs": ["realisation_de_soi"], "vertus": ["courage"]},
    "Curiosité": {"qualites": ["Curiosité"], "valeurs": ["stimulation", "autonomie"], "vertus": ["sagesse", "transcendance"]},
    "Rigueur": {"qualites": ["Esprit analytique"], "valeurs": ["conformite", "securite"], "vertus": ["temperance", "justice"]},
    "Esprit d'équipe": {"qualites": ["Collaboration"], "valeurs": ["bienveillance", "universalisme"], "vertus": ["humanite", "justice"]},
    "Autonome": {"qualites": ["Confiance en soi"], "valeurs": ["autonomie", "realisation_de_soi"], "vertus": ["courage"]},
    "Leadership": {"qualites": ["Charisme", "Vision"], "valeurs": ["pouvoir", "realisation_de_soi"], "vertus": ["courage", "justice"]},
    "Organisation": {"qualites": ["Méthode", "Rigueur"], "valeurs": ["conformite", "securite"], "vertus": ["temperance"]},
    "Empathie": {"qualites": ["Empathie"], "valeurs": ["bienveillance", "universalisme"], "vertus": ["humanite"]},
    "Patience": {"qualites": ["Patience"], "valeurs": ["bienveillance", "conformite"], "vertus": ["temperance", "humanite"]},
    "Intégrité": {"qualites": ["Honnêteté"], "valeurs": ["conformite", "bienveillance"], "vertus": ["justice"]},
    "Initiative": {"qualites": ["Proactivité"], "valeurs": ["autonomie", "stimulation"], "vertus": ["courage"]},
}


async def import_data():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    xls = pd.ExcelFile("/tmp/filieres.ods", engine="odf")

    # Parse Feuille 1: Filières → Secteurs
    df1 = pd.read_excel(xls, sheet_name="Feuille1")
    filieres = {}
    current_filiere = None
    current_num = None
    for _, row in df1.iterrows():
        num = row.iloc[0]
        filiere = row.iloc[1]
        secteur = row.iloc[3]
        if pd.notna(num):
            current_num = int(num)
        if pd.notna(filiere):
            current_filiere = str(filiere).strip()
            if current_filiere not in filieres:
                filieres[current_filiere] = {"id": current_num, "name": current_filiere, "secteurs": []}
        if pd.notna(secteur) and current_filiere:
            filieres[current_filiere]["secteurs"].append(str(secteur).strip())

    # Parse Feuille 2: Secteurs → Métiers → Missions
    df2 = pd.read_excel(xls, sheet_name="Feuille2")
    secteur_metiers = {}
    current_secteur = None
    for _, row in df2.iterrows():
        secteur = row.iloc[1]
        metier = row.iloc[2]
        mission = row.iloc[3]
        if pd.notna(secteur):
            current_secteur = str(secteur).strip()
        if pd.notna(metier) and current_secteur:
            if current_secteur not in secteur_metiers:
                secteur_metiers[current_secteur] = []
            secteur_metiers[current_secteur].append({
                "name": str(metier).strip(),
                "mission": str(mission).strip() if pd.notna(mission) else "",
            })

    # Parse Feuille 3: Métiers → SF → CT → SE → CP
    df3 = pd.read_excel(xls, sheet_name="Feuille3")
    metier_competences = {}
    current_metier = None
    for _, row in df3.iterrows():
        metier = row.iloc[2]
        sf = row.iloc[3]
        ct = row.iloc[4]
        se = row.iloc[5]
        cp = row.iloc[6]
        if pd.notna(metier):
            current_metier = str(metier).strip()
            if current_metier not in metier_competences:
                metier_competences[current_metier] = {"savoirs_faire": [], "savoirs_etre": []}
        if current_metier:
            if pd.notna(sf):
                metier_competences[current_metier]["savoirs_faire"].append({
                    "name": str(sf).strip(),
                    "capacite_technique": str(ct).strip() if pd.notna(ct) else "",
                })
            if pd.notna(se):
                se_name = str(se).strip()
                links = SE_QUALITES_VALEURS_VERTUS.get(se_name, {"qualites": [], "valeurs": [], "vertus": []})
                metier_competences[current_metier]["savoirs_etre"].append({
                    "name": se_name,
                    "capacite_professionnelle": str(cp).strip() if pd.notna(cp) else "",
                    "qualites_humaines": links["qualites"],
                    "valeurs": links["valeurs"],
                    "vertus": links["vertus"],
                })

    # Parse Feuille 4: SE → Qualités humaines (additional detail)
    df4 = pd.read_excel(xls, sheet_name="Feuille4")
    se_qualites_detail = {}
    current_se = None
    for _, row in df4.iterrows():
        se = row.iloc[1]
        qh = row.iloc[2]
        if pd.notna(se):
            current_se = str(se).strip()
        if pd.notna(qh) and current_se:
            se_qualites_detail[current_se] = str(qh).strip()

    # Build final structure
    result = []
    for filiere_name, filiere_data in filieres.items():
        filiere_doc = {
            "id": filiere_data["id"],
            "name": filiere_name,
            "secteurs": [],
        }
        for secteur_name in filiere_data["secteurs"]:
            secteur_doc = {
                "name": secteur_name,
                "metiers": [],
            }
            for metier in secteur_metiers.get(secteur_name, []):
                metier_name = metier["name"]
                comps = metier_competences.get(metier_name, {"savoirs_faire": [], "savoirs_etre": []})

                # Enrich SE with qualites detail from Feuille 4
                for se in comps["savoirs_etre"]:
                    if se["name"] in se_qualites_detail:
                        se["qualite_detail"] = se_qualites_detail[se["name"]]

                metier_doc = {
                    "name": metier_name,
                    "mission": metier["mission"],
                    "savoirs_faire": comps["savoirs_faire"],
                    "savoirs_etre": comps["savoirs_etre"],
                }
                secteur_doc["metiers"].append(metier_doc)
            filiere_doc["secteurs"].append(secteur_doc)
        result.append(filiere_doc)

    # Save to MongoDB
    await db.referentiel_metiers.delete_many({})
    if result:
        await db.referentiel_metiers.insert_many(result)

    # Also save flat lookup collections for quick access
    all_metiers = []
    all_se = {}
    for f in result:
        for s in f["secteurs"]:
            for m in s["metiers"]:
                all_metiers.append({
                    "name": m["name"],
                    "mission": m["mission"],
                    "filiere": f["name"],
                    "secteur": s["name"],
                    "savoirs_faire_count": len(m["savoirs_faire"]),
                    "savoirs_etre_count": len(m["savoirs_etre"]),
                })
                for se in m["savoirs_etre"]:
                    if se["name"] not in all_se:
                        all_se[se["name"]] = {
                            "name": se["name"],
                            "qualites_humaines": se.get("qualites_humaines", []),
                            "valeurs": se.get("valeurs", []),
                            "vertus": se.get("vertus", []),
                            "qualite_detail": se.get("qualite_detail", ""),
                            "metiers": [],
                        }
                    all_se[se["name"]]["metiers"].append(m["name"])

    await db.referentiel_metiers_flat.delete_many({})
    if all_metiers:
        await db.referentiel_metiers_flat.insert_many(all_metiers)

    await db.referentiel_se_links.delete_many({})
    if all_se:
        await db.referentiel_se_links.insert_many(list(all_se.values()))

    print(f"Imported: {len(result)} filières, {sum(len(f['secteurs']) for f in result)} secteurs, {len(all_metiers)} métiers, {len(all_se)} savoir-être uniques")

    client.close()


if __name__ == "__main__":
    asyncio.run(import_data())
