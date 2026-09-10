"""Regression tests for iteration 51 - Body(default_factory=dict) refactor + admin gate env."""
import os
import requests
import pytest
from conftest import TEST_USER_PASSWORD

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL")
if not BASE_URL:
    # Fallback: read frontend env
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL"):
                BASE_URL = line.split("=", 1)[1].strip().strip('"')
BASE_URL = BASE_URL.rstrip("/")

ADMIN_PWD = "Choukette@777"


@pytest.fixture(scope="module")
def michel_token():
    r = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"pseudo": "michel", "password": TEST_USER_PASSWORD},
        timeout=15,
    )
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text[:300]}"
    return r.json()["token"]


# ---------------- Admin Gate ----------------
class TestAdminGate:
    def test_get_gate_state(self):
        r = requests.get(f"{BASE_URL}/api/admin/gate-state", timeout=10)
        assert r.status_code == 200
        assert "spaces_open" in r.json()

    def test_post_gate_state_ok(self):
        r = requests.post(
            f"{BASE_URL}/api/admin/gate-state",
            json={"password": ADMIN_PWD, "spaces_open": True},
            timeout=10,
        )
        assert r.status_code == 200, r.text[:300]
        assert r.json().get("spaces_open") is True

    def test_post_gate_state_bad_password(self):
        r = requests.post(
            f"{BASE_URL}/api/admin/gate-state",
            json={"password": "wrong-password", "spaces_open": True},
            timeout=10,
        )
        assert r.status_code == 403


# ---------------- Body(default_factory=dict) regression ----------------
class TestBodyDefaultFactory:
    def test_jobs_matching_search_empty_body(self, michel_token):
        r = requests.post(
            f"{BASE_URL}/api/jobs/matching/search?token={michel_token}",
            json={},
            timeout=30,
        )
        assert r.status_code == 200, r.text[:300]

    def test_jobs_matching_search_isolation(self, michel_token):
        """Call twice with empty body; must be idempotent (no shared mutable default state)."""
        r1 = requests.post(
            f"{BASE_URL}/api/jobs/matching/search?token={michel_token}",
            json={},
            timeout=30,
        )
        r2 = requests.post(
            f"{BASE_URL}/api/jobs/matching/search?token={michel_token}",
            json={},
            timeout=30,
        )
        assert r1.status_code == 200
        assert r2.status_code == 200
        # Both should have same top-level keys
        assert set(r1.json().keys()) == set(r2.json().keys())

    def test_notifications_mark_all_read(self, michel_token):
        r = requests.post(
            f"{BASE_URL}/api/notifications/mark-all-read?token={michel_token}",
            json={},
            timeout=15,
        )
        assert r.status_code == 200, r.text[:300]

    def test_matching_preferences(self, michel_token):
        r = requests.post(
            f"{BASE_URL}/api/jobs/matching/preferences?token={michel_token}",
            json={"villes": ["Strasbourg"]},
            timeout=15,
        )
        assert r.status_code == 200, r.text[:300]

    def test_matching_analyze_offer(self, michel_token):
        r = requests.post(
            f"{BASE_URL}/api/matching/analyze-offer?token={michel_token}",
            json={"text": "Recherche chauffeur livreur permis B à Strasbourg en CDI, mission de livraison locale et régionale, expérience 2 ans souhaitée."},
            timeout=60,
        )
        assert r.status_code == 200, r.text[:300]
        data = r.json()
        assert isinstance(data, dict) and len(data) > 0


# ---------------- D'Clic routes regression ----------------
class TestDclicRoutes:
    def test_dclic_questionnaire(self):
        r = requests.get(f"{BASE_URL}/api/dclic/questionnaire", timeout=15)
        assert r.status_code == 200, r.text[:300]

    def test_dclic_import_profile_empty_body(self, michel_token):
        r = requests.post(
            f"{BASE_URL}/api/dclic/import-profile?token={michel_token}",
            json={},
            timeout=30,
        )
        # Must NOT be a 500 (regression guard on Body refactor)
        assert r.status_code != 500, f"Regression: 500 on dclic/import-profile: {r.text[:300]}"
        # 200 or clean 4xx acceptable
        assert 200 <= r.status_code < 500
