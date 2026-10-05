"""
Iteration 57 — Reconversion / Explorer une nouvelle trajectoire
Backend tests for:
  POST /api/trajectoire/explorer
  GET  /api/trajectoire/explorer/status/{job_id}
  GET  /api/trajectoire/explorer/latest
  GET  /api/trajectoire/coherence
  POST /api/trajectory/steps (step_type persistence)
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cv-analyzer-53.preview.emergentagent.com").rstrip("/")
PETER = ("peter7", "Solerys777!")
MIKE = ("mike7", "Solerys777!")


def _login(pseudo, password):
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"pseudo": pseudo, "password": password}, timeout=30)
    assert r.status_code == 200, f"login failed {pseudo}: {r.status_code} {r.text[:200]}"
    tok = r.json().get("token") or r.json().get("access_token")
    assert tok, f"no token in response: {r.json()}"
    return tok


@pytest.fixture(scope="module")
def peter_token():
    return _login(*PETER)


@pytest.fixture(scope="module")
def mike_token():
    return _login(*MIKE)


# ----- /latest cache (peter7) -----
def test_explorer_latest_peter_cache(peter_token):
    r = requests.get(f"{BASE_URL}/api/trajectoire/explorer/latest", params={"token": peter_token}, timeout=30)
    assert r.status_code == 200, r.text[:300]
    data = r.json()
    assert data.get("has_data") is True, f"expected has_data=True for peter7 cache, got {data}"
    result = data.get("result") or data.get("data") or data
    # Validate structure
    assert "ligne_coherence" in result or "ligne_coherence" in data, f"ligne_coherence missing: {list(result.keys())[:20]}"
    r_body = result if "ligne_coherence" in result else data
    for key in ["ligne_coherence", "invariants", "acquis", "competences_transferables", "niveaux"]:
        assert key in r_body, f"missing {key} in cached result keys={list(r_body.keys())}"
    niveaux = r_body["niveaux"]
    for lvl in ["evoluer", "reconvertir", "explorer"]:
        assert lvl in niveaux, f"niveau {lvl} missing"
        metiers = niveaux[lvl]
        assert isinstance(metiers, list) and len(metiers) >= 1, f"{lvl} metiers list empty"
        m = metiers[0]
        for field in ["metier", "pourquoi", "sf_mobilisables", "se_mobilisables", "manquantes", "reduire_ecart", "rome_code"]:
            assert field in m, f"metier field {field} missing in {lvl}: keys={list(m.keys())}"


# ----- /coherence (peter7, cache chaud) -----
def test_coherence_peter(peter_token):
    r = requests.get(f"{BASE_URL}/api/trajectoire/coherence", params={"token": peter_token}, timeout=60)
    assert r.status_code == 200, r.text[:300]
    data = r.json()
    assert "transitions" in data, f"transitions missing: {list(data.keys())}"
    assert "fil_conducteur" in data, f"fil_conducteur missing"
    transitions = data["transitions"]
    assert isinstance(transitions, list)
    if transitions:
        t = transitions[0]
        for key in ["step_id", "est_changement"]:
            assert key in t, f"{key} missing in transition keys={list(t.keys())}"


# ----- trajectory step with step_type persistence -----
def test_create_trajectory_step_persists_step_type(peter_token):
    payload = {
        "title": "TEST_iter57 Projet reconversion",
        "step_type": "projet",
        "type": "projet",
        "description": "Test persistence step_type",
        "skills": ["python"],
        "visibility": "private"
    }
    r = requests.post(f"{BASE_URL}/api/trajectory/steps", params={"token": peter_token}, json=payload, timeout=30)
    assert r.status_code in (200, 201), f"create step failed: {r.status_code} {r.text[:300]}"
    body = r.json()
    step_id = body.get("id") or body.get("step_id") or (body.get("step", {}) or {}).get("id")
    assert step_id, f"no step id in response: {body}"

    try:
        g = requests.get(f"{BASE_URL}/api/trajectory/steps", params={"token": peter_token}, timeout=30)
        assert g.status_code == 200, g.text[:200]
        steps_body = g.json()
        steps = steps_body if isinstance(steps_body, list) else steps_body.get("steps", [])
        found = next((s for s in steps if s.get("id") == step_id or s.get("title") == payload["title"]), None)
        assert found, f"created step not found in list (count={len(steps)})"
        assert found.get("step_type") == "projet", f"step_type not persisted: got {found.get('step_type')}, full={found}"
    finally:
        # cleanup
        requests.delete(f"{BASE_URL}/api/trajectory/steps/{step_id}", params={"token": peter_token}, timeout=15)


# ----- POST /explorer job + status polling (lightweight, do not force new LLM run if too costly) -----
def test_explorer_job_launch_and_status_shape(peter_token):
    r = requests.post(f"{BASE_URL}/api/trajectoire/explorer", params={"token": peter_token}, timeout=30)
    assert r.status_code in (200, 202), f"explorer launch failed: {r.status_code} {r.text[:300]}"
    body = r.json()
    job_id = body.get("job_id")
    assert job_id, f"no job_id returned: {body}"

    # Poll a few times just to validate shape (processing or completed)
    s = requests.get(f"{BASE_URL}/api/trajectoire/explorer/status/{job_id}", params={"token": peter_token}, timeout=30)
    assert s.status_code == 200, s.text[:200]
    sb = s.json()
    assert "status" in sb, f"no status field: {sb}"
    assert sb["status"] in ("processing", "completed", "pending", "running", "failed"), f"unexpected status {sb['status']}"
    assert "progress" in sb or sb["status"] == "completed", f"no progress and not completed: {sb}"


# ----- mike7 latest may or may not have cache -----
def test_explorer_latest_mike(mike_token):
    r = requests.get(f"{BASE_URL}/api/trajectoire/explorer/latest", params={"token": mike_token}, timeout=30)
    assert r.status_code == 200, r.text[:300]
    data = r.json()
    assert "has_data" in data, f"has_data missing: {data}"
    # mike7 may have no cache — just assert key present and boolean
    assert isinstance(data["has_data"], bool)
