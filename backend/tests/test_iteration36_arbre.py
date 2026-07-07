"""Iteration 36 — Tests for the new /api/passport/arbre endpoints
   Covers: GET (saved), GET (prefill=1) and POST + persistence."""
import os
import requests
import pytest

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"
LEVEL_KEYS = ["savoir_faire", "savoir_etre", "qualites", "valeurs", "vertus"]


@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{API}/auth/login", json={"pseudo": "mike9", "password": "Solerys777!"}, timeout=30)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    tok = r.json().get("token")
    assert tok, "no token in login response"
    return tok


# ---- GET /passport/arbre ----

def test_get_arbre_no_prefill_returns_5_levels(token):
    r = requests.get(f"{API}/passport/arbre", params={"token": token}, timeout=30)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "levels" in data
    for k in LEVEL_KEYS:
        assert k in data["levels"], f"missing key {k}"
        assert isinstance(data["levels"][k], list)


def test_get_arbre_prefill_populated_for_mike9(token):
    r = requests.get(f"{API}/passport/arbre", params={"token": token, "prefill": 1}, timeout=30)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("prefilled") is True
    lv = data["levels"]
    # mike9 profile expected populated
    assert len(lv["savoir_faire"]) >= 5, f"savoir_faire got {lv['savoir_faire']}"
    assert len(lv["savoir_etre"]) >= 3, f"savoir_etre got {lv['savoir_etre']}"
    # qualites/valeurs/vertus may be smaller but should have at least 1 each
    assert len(lv["qualites"]) >= 1
    assert len(lv["valeurs"]) >= 1
    assert len(lv["vertus"]) >= 1


# ---- POST /passport/arbre + persistence ----

def test_post_arbre_saves_and_get_returns_saved(token):
    payload = {
        "levels": {
            "savoir_faire": ["TEST_conduite_entretien", "TEST_excel"],
            "savoir_etre": ["TEST_ecoute_active"],
            "qualites": ["TEST_patience"],
            "valeurs": ["TEST_bienveillance"],
            "vertus": ["TEST_courage", "TEST_justice"],
        }
    }
    r = requests.post(f"{API}/passport/arbre", params={"token": token}, json=payload, timeout=30)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("status") == "ok"
    for k in LEVEL_KEYS:
        assert body["levels"][k] == payload["levels"][k]

    # GET without prefill should now return exactly what we saved
    r2 = requests.get(f"{API}/passport/arbre", params={"token": token}, timeout=30)
    assert r2.status_code == 200
    data = r2.json()
    assert data.get("prefilled") is False
    assert data["levels"]["vertus"] == ["TEST_courage", "TEST_justice"]
    assert data["levels"]["savoir_faire"] == ["TEST_conduite_entretien", "TEST_excel"]


def test_post_arbre_strips_and_dedupes(token):
    payload = {
        "levels": {
            "savoir_faire": ["  A  ", "", "B", "C"],
            "savoir_etre": [],
            "qualites": [],
            "valeurs": [],
            "vertus": [],
        }
    }
    r = requests.post(f"{API}/passport/arbre", params={"token": token}, json=payload, timeout=30)
    assert r.status_code == 200, r.text
    lv = r.json()["levels"]
    assert lv["savoir_faire"] == ["A", "B", "C"]
