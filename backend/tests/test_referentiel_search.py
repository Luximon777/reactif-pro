"""Backend tests for referentiel search fix (stopwords + racine souple)"""
import os
import pytest
import requests
from urllib.parse import quote

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://cv-analyzer-53.preview.emergentagent.com').rstrip('/')


@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{BASE_URL}/api/auth/login",
                      json={"pseudo": "peter7", "password": "Solerys777!"}, timeout=20)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text[:200]}"
    return r.json().get("token")


# ---- GET /api/referentiel/search (peter7 token) ----
class TestReferentielSearch:
    def _search(self, q, token, **extra):
        params = {"q": q, "token": token, **extra}
        return requests.get(f"{BASE_URL}/api/referentiel/search", params=params, timeout=25)

    def test_chef_de_cuisine_returns_terrain_fiche(self, token):
        r = self._search("chef de cuisine", token)
        assert r.status_code == 200, r.text[:300]
        d = r.json()
        total = d.get("total", 0)
        assert total >= 1, f"expected total>=1 got {total} data={d}"
        metiers = d.get("metiers", []) or d.get("results", {}).get("metiers", [])
        joined = " | ".join([str(m.get("nom", "")) + " " + str(m.get("intitule", "")) + " " + str(m.get("titre", "")) for m in metiers]).lower()
        assert "chef cuisinier" in joined or "cuisinier" in joined, f"expected chef cuisinier in results: {joined[:400]}"

    def test_chef_cuisinier_non_regression(self, token):
        r = self._search("chef cuisinier", token)
        assert r.status_code == 200
        assert r.json().get("total", 0) >= 1

    def test_cuisinier_alone(self, token):
        r = self._search("cuisinier", token)
        assert r.status_code == 200
        assert r.json().get("total", 0) >= 1

    def test_la_cuisine_stopword_ignored(self, token):
        r = self._search("la cuisine", token)
        assert r.status_code == 200
        assert r.json().get("total", 0) >= 1

    def test_inexistant_returns_zero_no_500(self, token):
        r = self._search("xyzinexistant", token)
        assert r.status_code == 200
        assert r.json().get("total", 0) == 0

    def test_chauffeur_non_regression(self, token):
        r = self._search("chauffeur", token)
        assert r.status_code == 200
        assert r.json().get("total", 0) >= 1

    def test_vente_non_regression(self, token):
        r = self._search("vente", token)
        assert r.status_code == 200
        assert r.json().get("total", 0) >= 1

    def test_no_q_with_filiere_all(self, token):
        r = requests.get(f"{BASE_URL}/api/referentiel/search",
                         params={"token": token, "filiere": "all"}, timeout=25)
        assert r.status_code == 200


# ---- GET /api/opc/referentiel/search (no auth?) ----
class TestOpcReferentielSearch:
    def _search(self, q):
        return requests.get(f"{BASE_URL}/api/opc/referentiel/search",
                            params={"q": q}, timeout=25)

    def test_chef_de_cuisine(self):
        r = self._search("chef de cuisine")
        assert r.status_code == 200, r.text[:300]
        d = r.json()
        results = d.get("results", d.get("metiers", []))
        # Accept either a list or dict with 'total'
        if isinstance(results, dict):
            total = results.get("total") or d.get("total") or 0
        else:
            total = len(results) if isinstance(results, list) else d.get("total", 0)
        assert total >= 1, f"expected >=1 for 'chef de cuisine' got {total} body={d}"

    def test_chef_cuisinier(self):
        r = self._search("chef cuisinier")
        assert r.status_code == 200
        d = r.json()
        results = d.get("results", d.get("metiers", []))
        total = (len(results) if isinstance(results, list) else (results.get("total", 0) if isinstance(results, dict) else d.get("total", 0)))
        assert total >= 1
