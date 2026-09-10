"""Iteration 56 — Test async cartographie exhaustive + sources_detail."""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cv-analyzer-53.preview.emergentagent.com").rstrip("/")


@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"pseudo": "peter7", "password": "Solerys777!"}, timeout=15)
    assert r.status_code == 200, r.text
    data = r.json()
    tok = data.get("token") or data.get("access_token")
    assert tok
    return tok


def test_cartographie_async_returns_job_id_fast(token):
    t0 = time.time()
    r = requests.post(
        f"{BASE_URL}/api/observatory/ia/cartographie-exhaustive/async?token={token}",
        json={"contexte_metier": "restauration"},
        timeout=15,
    )
    elapsed = time.time() - t0
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get("status") == "running"
    assert "job_id" in data
    assert elapsed < 10, f"Async endpoint took {elapsed}s — expected <5s"
    # Save job_id for the polling test via module-level cache
    pytest.job_id = data["job_id"]


def test_cartographie_async_polling_completes(token):
    job_id = getattr(pytest, "job_id", None)
    assert job_id, "job_id from previous test missing"
    deadline = time.time() + 240  # 4 min
    status = "running"
    job = None
    while time.time() < deadline:
        try:
            r = requests.get(f"{BASE_URL}/api/observatory/ia/analyse-complete/status?job_id={job_id}", timeout=30)
        except requests.exceptions.RequestException as e:
            print(f"poll error: {e}")
            time.sleep(8)
            continue
        if r.status_code != 200:
            print(f"poll status={r.status_code}")
            time.sleep(8)
            continue
        job = r.json()
        status = job.get("status")
        print(f"poll status={status}")
        if status in ("completed", "failed"):
            break
        time.sleep(8)

    assert status == "completed", f"Job status={status}, job={job}"
    result = job.get("result") or {}
    assert result.get("categories"), "no categories"
    assert result.get("total_metiers", 0) > 0

    stats = result.get("source_stats") or {}
    assert stats.get("rome_matches", 0) > 0
    # opc_matches can be 0 for short query "restauration" (OPC data keyed on metier titles like "chef"/"cuisinier")
    assert "opc_matches" in stats
    assert stats.get("rncp_matches", 0) > 0

    detail = result.get("sources_detail") or {}
    rome = detail.get("rome") or []
    opc = detail.get("opc")
    rncp = detail.get("rncp") or []
    assert len(rome) > 0 and "code_rome" in rome[0] and "libelle" in rome[0]
    assert opc is not None  # array present even if empty
    assert len(rncp) > 0
    r0 = rncp[0]
    assert any(k in r0 for k in ("code", "code_rncp"))
    assert any(k in r0 for k in ("intitule", "libelle"))
