"""Iteration 55: Validate cartographie exhaustive source_stats fix (word-pattern search)."""
import os
import sys
import asyncio
import pytest
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path("/app/frontend/.env"))

sys.path.insert(0, "/app/backend")

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
PSEUDO = "peter7"
PASSWORD = "Solerys777!"


@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"pseudo": PSEUDO, "password": PASSWORD}, timeout=15)
    assert r.status_code == 200, r.text
    tok = r.json().get("token")
    assert tok
    return tok


# --- Data layer direct (no LLM) : run 3 queries within one event loop ---

def test_fetch_all_matching_data_layer():
    from observatory_ia_routes import _fetch_all_matching_data

    async def run_all():
        results = {}
        results["chef"] = await _fetch_all_matching_data("chef de cuisine")
        results["empty"] = await _fetch_all_matching_data("")
        ctx = "Restauration commerciale, Traiteur / événementiel, Hôtellerie, Élaboration de cartes et menus (créativité, saisonnalité), Gestion des approvisionnements, stocks et prévisions, Application des normes HACCP et sécurité alimentaire"
        results["full"] = await _fetch_all_matching_data(ctx)
        return results

    results = asyncio.run(run_all())
    chef = results["chef"]
    print("chef de cuisine → rome:", len(chef["rome"]), "opc:", len(chef["opc"]), "rncp:", len(chef["rncp"]))
    assert len(chef["rome"]) >= 20
    assert len(chef["opc"]) >= 3
    assert len(chef["rncp"]) >= 20

    empty = results["empty"]
    assert empty["rome"] == [] and empty["opc"] == [] and empty["rncp"] == []

    full = results["full"]
    print("full ctx → rome:", len(full["rome"]), "opc:", len(full["opc"]), "rncp:", len(full["rncp"]))
    assert len(full["rome"]) > 0
    assert len(full["opc"]) > 0
    assert len(full["rncp"]) > 0


# --- Regression: Référentiel search (helper mutualisé) ---

def test_referentiel_search_chef_de_cuisine(token):
    r = requests.get(f"{BASE_URL}/api/referentiel/search",
                     params={"q": "chef de cuisine", "token": token}, timeout=30)
    assert r.status_code == 200, r.text
    data = r.json()
    total = data.get("total", 0) or len(data.get("metiers", []))
    assert total >= 1, f"expected >=1, got {total}"


def test_opc_referentiel_search_chef_cuisinier():
    r = requests.get(f"{BASE_URL}/api/opc/referentiel/search",
                     params={"q": "chef cuisinier"}, timeout=30)
    assert r.status_code == 200, r.text
    data = r.json()
    results = data.get("results") or data.get("metiers") or []
    assert len(results) > 0, f"empty results"


# --- Cartographie exhaustive (1 LLM call) ---

def test_cartographie_exhaustive_source_stats(token):
    ctx = "Restauration commerciale, Traiteur / événementiel, Hôtellerie, Élaboration de cartes et menus (créativité, saisonnalité), Gestion des approvisionnements, stocks et prévisions, Application des normes HACCP et sécurité alimentaire"
    # Use localhost to bypass Cloudflare 60s edge timeout (LLM ~60-90s)
    r = requests.post(
        "http://localhost:8001/api/observatory/ia/cartographie-exhaustive",
        params={"token": token},
        json={"contexte_metier": ctx},
        timeout=180,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    print("cartographie response keys:", list(data.keys()))
    if data.get("error"):
        pytest.fail(f"LLM returned error: {data}")
    stats = data.get("source_stats") or {}
    print("source_stats:", stats)
    assert stats.get("rome_matches", 0) > 0
    assert stats.get("opc_matches", 0) > 0
    assert stats.get("rncp_matches", 0) > 0
