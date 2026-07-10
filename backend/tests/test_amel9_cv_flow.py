"""
Iteration 41 - Reproduce production bug (amel9): upload CV -> verify formations extracted.
Backend E2E flow via /api/cv/analyze-text (text path, no multipart).
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cv-analyzer-53.preview.emergentagent.com").rstrip("/")
CV_PATH = "/tmp/cv_amel.txt"
PSEUDO = "amel9"
PWD = "Solerys777!"

EXPECTED_TITLES = [
    "BTS",  # BTS SAM
    "Baccalauréat",  # Bac STMG
    "TOEIC",  # TOEIC
    "Gestion de projet",  # Gestion projet agile
]
EXPECTED_CI = ["Yoga", "Cuisine", "Lecture"]


@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"pseudo": PSEUDO, "password": PWD}, timeout=15)
    assert r.status_code == 200, r.text
    return r.json()["token"]


@pytest.fixture(scope="module")
def cv_text():
    with open(CV_PATH, "r", encoding="utf-8") as f:
        return f.read()


def _wait_completed(token, job_id, timeout=180):
    start = time.time()
    last_step = None
    while time.time() - start < timeout:
        r = requests.get(f"{BASE_URL}/api/cv/analyze/status", params={"token": token, "job_id": job_id}, timeout=15)
        assert r.status_code == 200, r.text
        j = r.json()
        step = j.get("step")
        if step != last_step:
            print(f"[status] {j.get('status')} - {step}")
            last_step = step
        if j.get("status") == "completed":
            return j
        if j.get("status") == "failed":
            pytest.fail(f"Analyse échouée: {j.get('error') or j}")
        time.sleep(3)
    pytest.fail("Timeout attente analyse CV")


def test_01_analyze_cv_amel9(token, cv_text):
    """Upload CV via analyze-text and wait for completion"""
    r = requests.post(
        f"{BASE_URL}/api/cv/analyze-text",
        params={"token": token},
        json={"text": cv_text, "filename": "cv_amel.txt"},
        timeout=30,
    )
    assert r.status_code == 200, r.text
    job_id = r.json()["job_id"]
    result = _wait_completed(token, job_id)
    assert result["status"] == "completed"


def test_02_passport_has_4_formations(token):
    """Verify passeport.formations contains all 4 formations with title+institution+year"""
    r = requests.get(f"{BASE_URL}/api/passport", params={"token": token}, timeout=15)
    assert r.status_code == 200, r.text
    p = r.json()
    formations = p.get("formations", [])
    print(f"Formations count: {len(formations)}")
    for f in formations:
        print(f"  - title='{f.get('title')}' | institution='{f.get('institution')}' | year='{f.get('year')}' | source='{f.get('source')}'")

    assert len(formations) >= 4, f"Attendu >=4 formations, obtenu {len(formations)}"
    # Sanity: source must be cv_analysis (not ia_detectee/inventée)
    for f in formations:
        assert f.get("source") in ("cv_analysis", "declaratif"), f"Formation avec source suspecte: {f}"
        assert f.get("title"), f"Formation sans title: {f}"

    titles_joined = " | ".join([f.get("title", "") for f in formations]).lower()
    for expected in EXPECTED_TITLES:
        assert expected.lower() in titles_joined, f"Titre attendu manquant: {expected}. Got: {titles_joined}"


def test_03_centres_interet_extracted(token):
    """Verify centres d'intérêt extracted (Yoga, Cuisine, Lecture)"""
    r = requests.get(f"{BASE_URL}/api/cv/centres-interet", params={"token": token}, timeout=15)
    assert r.status_code == 200, r.text
    body = r.json()
    centres = body.get("centres", []) if isinstance(body, dict) else body
    print(f"Centres d'intérêt: {centres}")
    themes = " | ".join([(c.get("theme") if isinstance(c, dict) else str(c)) for c in centres]).lower()
    for expected in EXPECTED_CI:
        assert expected.lower() in themes, f"Centre d'intérêt manquant: {expected}. Got: {themes}"


def test_04_refresh_fallback_reextracts_formations(token):
    """Vider les formations puis appeler /passport/refresh → doit ré-extraire depuis cv_text"""
    # We use the API only. Empty formations by resetting the passport formations via mongo? We don't have that direct handle.
    # Instead we simulate by directly writing to DB via a shell script.
    import subprocess
    profile_id = requests.post(f"{BASE_URL}/api/auth/login", json={"pseudo": PSEUDO, "password": PWD}, timeout=15).json()["profile_id"]
    # Not needed. Use token_id via passport
    passport_before = requests.get(f"{BASE_URL}/api/passport", params={"token": token}, timeout=15).json()
    token_id = passport_before["token_id"]

    # Wipe formations directly in MongoDB
    py = f"""
import asyncio, os
from motor.motor_asyncio import AsyncIOMotorClient
async def main():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    r = await db.passports.update_one({{'token_id': '{token_id}'}}, {{'$set': {{'formations': []}}}})
    print('matched', r.matched_count, 'modified', r.modified_count)
asyncio.run(main())
"""
    result = subprocess.run(["python3", "-c", py], capture_output=True, text=True, env={**os.environ, "MONGO_URL": "mongodb://localhost:27017", "DB_NAME": "test_database"})
    print("DB wipe:", result.stdout, result.stderr)
    assert "modified 1" in result.stdout or "matched 1" in result.stdout

    # Confirm empty
    p = requests.get(f"{BASE_URL}/api/passport", params={"token": token}, timeout=15).json()
    assert len(p.get("formations", [])) == 0, "Wipe échoué"

    # Refresh
    r = requests.post(f"{BASE_URL}/api/passport/refresh", params={"token": token}, timeout=180)
    assert r.status_code == 200, r.text

    # Verify re-extracted
    p2 = requests.get(f"{BASE_URL}/api/passport", params={"token": token}, timeout=15).json()
    formations = p2.get("formations", [])
    print(f"Formations after refresh: {len(formations)}")
    for f in formations:
        print(f"  - '{f.get('title')}' | inst='{f.get('institution')}' | year='{f.get('year')}' | source='{f.get('source')}'")
    assert len(formations) >= 4, f"Fallback refresh n'a pas ré-extrait 4 formations, got {len(formations)}"
    for f in formations:
        assert f.get("source") == "cv_analysis", f"Fallback devrait retourner source=cv_analysis (depuis cv_text), got: {f}"
    titles_joined = " | ".join([f.get("title", "") for f in formations]).lower()
    for expected in EXPECTED_TITLES:
        assert expected.lower() in titles_joined, f"Fallback: titre attendu manquant: {expected}"
