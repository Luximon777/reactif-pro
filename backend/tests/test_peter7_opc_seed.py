"""Tests for peter7 OPC sync, RNCP stats, migration skip, and admin gate-state regression."""
import os
import requests
import pytest

BASE = os.environ.get("REACT_APP_BACKEND_URL", "https://cv-analyzer-53.preview.emergentagent.com").rstrip("/")


@pytest.fixture(scope="module")
def peter7_token():
    r = requests.post(f"{BASE}/api/auth/login", json={"pseudo": "peter7", "password": "Solerys777!"}, timeout=30)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    data = r.json()
    return data.get("token") or data.get("access_token"), data


def test_peter7_login(peter7_token):
    token, data = peter7_token
    assert token
    assert data.get("profile_id") or data.get("user")


def test_rncp_stats():
    r = requests.get(f"{BASE}/api/referentiel/rncp/stats", timeout=30)
    assert r.status_code == 200, r.text
    data = r.json()
    total = data.get("total_certifications") or data.get("total") or 0
    assert total >= 30000, f"expected >=30000, got {total}: {data}"


def test_observatory_dashboard():
    r = requests.get(f"{BASE}/api/observatory/dashboard", timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert data and isinstance(data, dict)


def test_opc_sync_peter7(peter7_token):
    """The frontend sync = GET /api/profile?token=... which fills skills/sectors used for OPC context."""
    token, _ = peter7_token
    r = requests.get(f"{BASE}/api/profile", params={"token": token}, timeout=60)
    assert r.status_code == 200, f"{r.status_code}: {r.text}"
    p = r.json()
    assert p.get("name") or p.get("pseudo") == "peter7"
    # Ensure skills/sectors keys exist (even if empty lists)
    assert "skills" in p or "sectors" in p


def test_referentiel_search():
    r = requests.get(f"{BASE}/api/referentiel/search", params={"q": "chef cuisinier"}, timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert data  # non-empty response


def test_admin_gate_state():
    # First read current state
    cur = requests.get(f"{BASE}/api/admin/gate-state", timeout=15).json()
    current = cur.get("spaces_open", True)
    r = requests.post(
        f"{BASE}/api/admin/gate-state",
        json={"password": "Choukette@777", "spaces_open": current},
        timeout=30,
    )
    assert r.status_code == 200, f"{r.status_code}: {r.text}"


def test_migration_skip_no_etl_log():
    """Verify no '[Migration] ETL RNCP' lines in backend log (skip worked)."""
    for path in ["/var/log/supervisor/backend.err.log", "/var/log/supervisor/backend.out.log"]:
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
            assert "[Migration] ETL RNCP en arrière-plan" not in content, f"Migration ETL was triggered in {path}!"
