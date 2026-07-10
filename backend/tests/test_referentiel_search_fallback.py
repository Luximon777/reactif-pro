# Tests for GET /api/referentiel/search fallback behavior and re-seed on startup
# Bug fix: /opc "Référentiel vivant" — search 'chef cuisinier' must return total > 0
# even when opc_metiers/opc_filieres/rome_metiers are empty (fallback to referentiel_opc + fiches_metier_opc)
import os
import time
import requests
import pytest
from pymongo import MongoClient

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cv-analyzer-53.preview.emergentagent.com").rstrip("/")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")


@pytest.fixture(scope="module")
def db():
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=3000)
    return client[DB_NAME]


# --- Feature 1: normal search should return the terrain fiche ---
class TestReferentielSearchNormal:
    def test_search_chef_cuisinier_returns_terrain_fiche(self):
        r = requests.get(f"{BASE_URL}/api/referentiel/search", params={"q": "chef cuisinier"}, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert data.get("total", 0) > 0, f"total should be >0, got {data.get('total')}"
        metier_names = [m.get("nom", "") for m in data.get("metiers", [])]
        assert any("Remplacement Chef cuisinier" in n for n in metier_names), \
            f"expected 'Remplacement Chef cuisinier' in metiers, got {metier_names}"

    def test_search_chef_cuisinier_returns_associated_skills(self):
        r = requests.get(f"{BASE_URL}/api/referentiel/search", params={"q": "chef cuisinier"}, timeout=30)
        data = r.json()
        # Fiche terrain has Rigueur (savoir-etre) and HACCP (capacite technique) per the bug report
        se_labels = [s.get("nom", "") if isinstance(s, dict) else str(s) for s in data.get("savoir_etre", [])]
        ct_labels = [c.get("nom", "") if isinstance(c, dict) else str(c) for c in data.get("capacites_techniques", [])]
        # At least one of these should be present
        assert len(se_labels) > 0 or len(ct_labels) > 0, \
            f"expected savoir_etre or capacites_techniques, got se={se_labels} ct={ct_labels}"

    def test_search_cuisinier(self):
        r = requests.get(f"{BASE_URL}/api/referentiel/search", params={"q": "cuisinier"}, timeout=30)
        assert r.status_code == 200
        assert r.json().get("total", 0) > 0

    def test_search_rigueur(self):
        r = requests.get(f"{BASE_URL}/api/referentiel/search", params={"q": "Rigueur"}, timeout=30)
        assert r.status_code == 200
        d = r.json()
        assert d.get("total", 0) > 0
        assert len(d.get("savoir_etre", [])) > 0

    def test_search_electrotechnique_classic_referentiel(self):
        r = requests.get(f"{BASE_URL}/api/referentiel/search", params={"q": "électrotechnique"}, timeout=30)
        assert r.status_code == 200
        d = r.json()
        assert d.get("total", 0) > 0
        assert len(d.get("metiers", [])) > 0

    def test_search_chef_chantier_regression(self):
        # Regression: another search should still return classic referentiel results
        r = requests.get(f"{BASE_URL}/api/referentiel/search", params={"q": "chef de chantier"}, timeout=30)
        assert r.status_code == 200
        assert r.json().get("total", 0) > 0


# --- Feature 2: robustness — fallback when opc_metiers/opc_filieres/rome_metiers are empty ---
class TestReferentielSearchFallbackEmptyCollections:
    def test_fallback_when_collections_empty(self, db):
        # Backup counts (we will restore via startup re-seed later)
        before_opc_metiers = db.opc_metiers.count_documents({})
        before_opc_filieres = db.opc_filieres.count_documents({})
        before_rome_metiers = db.rome_metiers.count_documents({})

        # Wipe the 3 collections
        db.opc_metiers.delete_many({})
        db.opc_filieres.delete_many({})
        db.rome_metiers.delete_many({})

        # Assert wipe worked
        assert db.opc_metiers.count_documents({}) == 0
        assert db.opc_filieres.count_documents({}) == 0
        assert db.rome_metiers.count_documents({}) == 0

        # Fallback must still return the terrain fiche
        r = requests.get(f"{BASE_URL}/api/referentiel/search", params={"q": "chef cuisinier"}, timeout=30)
        assert r.status_code == 200
        d = r.json()
        assert d.get("total", 0) > 0, \
            f"FALLBACK BROKEN — total should be >0 when collections are empty, got {d.get('total')}"
        metier_names = [m.get("nom", "") for m in d.get("metiers", [])]
        assert any("Remplacement Chef cuisinier" in n for n in metier_names), \
            f"FALLBACK BROKEN — expected 'Remplacement Chef cuisinier' from fiches_metier_opc, got {metier_names}"

        # Record before-counts on the class for the next test to compare
        TestReferentielSearchFallbackEmptyCollections.before_counts = (
            before_opc_metiers, before_opc_filieres, before_rome_metiers
        )


# --- Feature 3: re-seed on startup should restore the 3 collections ---
class TestReferentielReseedOnStartup:
    def test_reseed_after_restart(self, db):
        # This test depends on the previous test having wiped the collections
        # Restart backend and wait ~20s
        import subprocess
        subprocess.run(["sudo", "supervisorctl", "restart", "backend"], check=False, capture_output=True)
        # Poll until backend is up and reseed has run
        deadline = time.time() + 60
        api_up = False
        while time.time() < deadline:
            try:
                r = requests.get(f"{BASE_URL}/api/", timeout=5)
                if r.status_code == 200:
                    api_up = True
                    break
            except Exception:
                pass
            time.sleep(2)
        assert api_up, "Backend did not come back after restart within 60s"

        # Give startup seeds time to complete
        time.sleep(15)

        opc_metiers = db.opc_metiers.count_documents({})
        opc_filieres = db.opc_filieres.count_documents({})
        rome_metiers = db.rome_metiers.count_documents({})

        assert opc_metiers >= 10, f"opc_metiers should be re-seeded (>=10), got {opc_metiers}"
        assert opc_filieres >= 5, f"opc_filieres should be re-seeded (>=5), got {opc_filieres}"
        assert rome_metiers >= 100, f"rome_metiers should be re-seeded (>=100), got {rome_metiers}"

    def test_search_still_works_after_restart(self):
        r = requests.get(f"{BASE_URL}/api/referentiel/search", params={"q": "chef cuisinier"}, timeout=30)
        assert r.status_code == 200
        assert r.json().get("total", 0) > 0
