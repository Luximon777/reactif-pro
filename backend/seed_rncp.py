"""
Connecteur ETL RNCP / France Compétences → OPC RE'ACTIF PRO
============================================================
Télécharge les données RNCP/RS depuis data.gouv.fr (open data),
transforme et charge dans MongoDB.

Collections créées :
  - opc_certifications     (fiches RNCP/RS principales)
  - opc_blocs_competences  (blocs de compétences par certification)
  - opc_rncp_rome          (mapping RNCP ↔ codes ROME)
  - opc_certificateurs     (organismes certificateurs)

Usage :
  python seed_rncp.py              # Import complet
  python seed_rncp.py --active     # Uniquement les certifications actives
  python seed_rncp.py --stats      # Afficher les statistiques sans importer
"""

import os
import sys
import csv
import io
import zipfile
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

import requests
import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [RNCP-ETL] %(message)s")
log = logging.getLogger("rncp_etl")

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ.get("DB_NAME", "test_database")

# data.gouv.fr API for France Compétences datasets
DATASET_SLUG = "repertoire-national-des-certifications-professionnelles-et-repertoire-specifique"
DATAGOUV_API = f"https://www.data.gouv.fr/api/1/datasets/{DATASET_SLUG}/"


def _find_latest_csv_url() -> str:
    """Find the latest export-fiches-csv ZIP URL from data.gouv.fr API."""
    log.info("Recherche du dernier export CSV sur data.gouv.fr...")
    resp = requests.get(DATAGOUV_API, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    for resource in data.get("resources", []):
        title = resource.get("title", "")
        if title.startswith("export-fiches-csv-") and title.endswith(".zip"):
            url = resource["url"]
            log.info(f"Fichier trouvé : {title}")
            return url

    raise RuntimeError("Aucun export CSV trouvé sur data.gouv.fr")


def _download_and_extract(url: str) -> dict:
    """Download ZIP and extract CSV files into memory."""
    log.info(f"Téléchargement : {url[:80]}...")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    log.info(f"Téléchargé : {len(resp.content) / 1024 / 1024:.1f} Mo")

    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    files = {}
    for name in zf.namelist():
        if name.endswith(".csv"):
            # Identify file type from name
            low = name.lower()
            if "standard" in low:
                files["standard"] = zf.read(name).decode("utf-8")
            elif "blocs" in low and "comp" in low:
                files["blocs"] = zf.read(name).decode("utf-8")
            elif "rome" in low:
                files["rome"] = zf.read(name).decode("utf-8")
            elif "certificateurs" in low:
                files["certificateurs"] = zf.read(name).decode("utf-8")
            elif "nsf" in low:
                files["nsf"] = zf.read(name).decode("utf-8")
            elif "formacode" in low:
                files["formacode"] = zf.read(name).decode("utf-8")
            elif "voixdacc" in low or "voix" in low:
                files["voies_acces"] = zf.read(name).decode("utf-8")
            else:
                log.info(f"  Fichier ignoré : {name}")

    log.info(f"Fichiers extraits : {list(files.keys())}")
    return files


def _parse_date(date_str: str) -> Optional[str]:
    """Parse French date (dd/mm/yyyy) to ISO format."""
    if not date_str or not date_str.strip():
        return None
    try:
        dt = datetime.strptime(date_str.strip(), "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None


def _parse_certifications(csv_text: str, active_only: bool = False) -> list:
    """Parse Standard CSV into certification documents."""
    reader = csv.DictReader(io.StringIO(csv_text), delimiter=";")
    docs = []
    for row in reader:
        numero = row.get("Numero_Fiche", "").strip()
        statut = row.get("Actif", "").strip()

        if active_only and statut != "ACTIVE":
            continue

        is_rncp = numero.startswith("RNCP")
        doc = {
            "code": numero,
            "type": "RNCP" if is_rncp else "RS",
            "intitule": row.get("Intitule", "").strip(),
            "abrege_libelle": row.get("Abrege_Libelle", "").strip(),
            "abrege_intitule": row.get("Abrege_Intitule", "").strip(),
            "niveau": row.get("Nomenclature_Europe_Niveau", "").strip(),
            "niveau_libelle": row.get("Nomenclature_Europe_Intitule", "").strip(),
            "statut": statut,
            "type_enregistrement": row.get("Type_Enregistrement", "").strip(),
            "date_decision": _parse_date(row.get("Date_Decision", "")),
            "date_fin_enregistrement": _parse_date(row.get("Date_Fin_Enregistrement", "")),
            "date_effet": _parse_date(row.get("Date_Effet", "")),
            "date_dernier_jo": _parse_date(row.get("Date_dernier_jo", "")),
            "validation_partielle": row.get("Validation_Partielle", "").strip(),
            "source": "france_competences_open_data",
            "imported_at": datetime.now(timezone.utc).isoformat(),
        }
        docs.append(doc)
    return docs


def _parse_blocs(csv_text: str) -> list:
    """Parse Blocs de Compétences CSV."""
    reader = csv.DictReader(io.StringIO(csv_text), delimiter=";")
    docs = []
    for row in reader:
        docs.append({
            "code_certification": row.get("Numero_Fiche", "").strip(),
            "code_bloc": row.get("Bloc_Competences_Code", "").strip(),
            "intitule": row.get("Bloc_Competences_Libelle", "").strip(),
            "source": "france_competences_open_data",
        })
    return docs


def _parse_rome_mapping(csv_text: str) -> list:
    """Parse ROME mapping CSV."""
    reader = csv.DictReader(io.StringIO(csv_text), delimiter=";")
    docs = []
    for row in reader:
        docs.append({
            "code_certification": row.get("Numero_Fiche", "").strip(),
            "code_rome": row.get("Codes_Rome_Code", "").strip(),
            "libelle_rome": row.get("Codes_Rome_Libelle", "").strip(),
            "source": "france_competences_open_data",
        })
    return docs


def _parse_certificateurs(csv_text: str) -> list:
    """Parse Certificateurs CSV."""
    reader = csv.DictReader(io.StringIO(csv_text), delimiter=";")
    docs = []
    for row in reader:
        docs.append({
            "code_certification": row.get("Numero_Fiche", "").strip(),
            "siret": row.get("Siret_Certificateur", "").strip(),
            "nom": row.get("Nom_Certificateur", "").strip(),
            "source": "france_competences_open_data",
        })
    return docs


async def _insert_batch(collection, docs: list, key_field: str, batch_name: str):
    """Bulk upsert documents into MongoDB."""
    if not docs:
        log.warning(f"  {batch_name}: aucun document à insérer")
        return 0

    from pymongo import UpdateOne
    operations = []
    for doc in docs:
        filt = {key_field: doc[key_field]} if key_field != "_compound" else {
            "code_certification": doc["code_certification"],
            "code_bloc": doc.get("code_bloc", doc.get("code_rome", "")),
        }
        operations.append(UpdateOne(filt, {"$set": doc}, upsert=True))

    # Insert in batches of 5000
    inserted = 0
    for i in range(0, len(operations), 5000):
        batch = operations[i:i + 5000]
        result = await collection.bulk_write(batch, ordered=False)
        inserted += result.upserted_count + result.modified_count
        if i % 10000 == 0 and i > 0:
            log.info(f"  {batch_name}: {i}/{len(operations)} traités...")

    log.info(f"  {batch_name}: {inserted} documents upserted ({len(docs)} total)")
    return inserted


async def run_etl(active_only: bool = False, stats_only: bool = False):
    """Main ETL pipeline."""
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    if stats_only:
        certs = await db.opc_certifications.count_documents({})
        active = await db.opc_certifications.count_documents({"statut": "ACTIVE"})
        rncp = await db.opc_certifications.count_documents({"type": "RNCP"})
        rs = await db.opc_certifications.count_documents({"type": "RS"})
        blocs = await db.opc_blocs_competences.count_documents({})
        rome = await db.opc_rncp_rome.count_documents({})
        certif = await db.opc_certificateurs.count_documents({})

        print(f"\n=== Statistiques OPC RNCP ===")
        print(f"  Certifications : {certs} (RNCP: {rncp}, RS: {rs}, Actives: {active})")
        print(f"  Blocs de compétences : {blocs}")
        print(f"  Mappings RNCP↔ROME : {rome}")
        print(f"  Certificateurs : {certif}")

        # Breakdown by level
        pipeline = [
            {"$match": {"statut": "ACTIVE"}},
            {"$group": {"_id": "$niveau_libelle", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        levels = await db.opc_certifications.aggregate(pipeline).to_list(20)
        if levels:
            print(f"\n  Par niveau (actives) :")
            for l in levels:
                print(f"    {l['_id'] or '(non renseigné)'}: {l['count']}")

        client.close()
        return

    # Step 1: Download
    url = _find_latest_csv_url()
    files = _download_and_extract(url)

    # Step 2: Transform
    log.info("Transformation des données...")

    certifications = _parse_certifications(files["standard"], active_only)
    log.info(f"  Certifications parsées : {len(certifications)}")

    blocs = _parse_blocs(files.get("blocs", "")) if "blocs" in files else []
    log.info(f"  Blocs de compétences parsés : {len(blocs)}")

    rome_mappings = _parse_rome_mapping(files.get("rome", "")) if "rome" in files else []
    log.info(f"  Mappings ROME parsés : {len(rome_mappings)}")

    certificateurs = _parse_certificateurs(files.get("certificateurs", "")) if "certificateurs" in files else []
    log.info(f"  Certificateurs parsés : {len(certificateurs)}")

    # Step 3: Load
    log.info("Chargement dans MongoDB...")

    await _insert_batch(db.opc_certifications, certifications, "code", "Certifications")
    await _insert_batch(db.opc_blocs_competences, blocs, "_compound", "Blocs")
    await _insert_batch(db.opc_rncp_rome, rome_mappings, "_compound", "ROME")
    await _insert_batch(db.opc_certificateurs, certificateurs, "_compound", "Certificateurs")

    # Step 4: Create indexes
    log.info("Création des index...")
    await db.opc_certifications.create_index("code", unique=True)
    await db.opc_certifications.create_index("intitule")
    await db.opc_certifications.create_index("statut")
    await db.opc_certifications.create_index("niveau")
    await db.opc_certifications.create_index("type")
    await db.opc_certifications.create_index([("intitule", "text")])

    await db.opc_blocs_competences.create_index("code_certification")
    await db.opc_blocs_competences.create_index("code_bloc")
    await db.opc_blocs_competences.create_index([("intitule", "text")])

    await db.opc_rncp_rome.create_index("code_certification")
    await db.opc_rncp_rome.create_index("code_rome")

    await db.opc_certificateurs.create_index("code_certification")

    # Step 5: Store ETL metadata
    await db.opc_etl_metadata.update_one(
        {"source": "rncp_france_competences"},
        {"$set": {
            "source": "rncp_france_competences",
            "last_import": datetime.now(timezone.utc).isoformat(),
            "download_url": url,
            "certifications_count": len(certifications),
            "blocs_count": len(blocs),
            "rome_mappings_count": len(rome_mappings),
            "certificateurs_count": len(certificateurs),
            "active_only": active_only,
        }},
        upsert=True,
    )

    log.info("=" * 50)
    log.info(f"ETL terminé avec succès !")
    log.info(f"  Certifications : {len(certifications)}")
    log.info(f"  Blocs compétences : {len(blocs)}")
    log.info(f"  Mappings ROME : {len(rome_mappings)}")
    log.info(f"  Certificateurs : {len(certificateurs)}")

    client.close()


if __name__ == "__main__":
    active_only = "--active" in sys.argv
    stats_only = "--stats" in sys.argv
    asyncio.run(run_etl(active_only=active_only, stats_only=stats_only))
