"""Shared fixtures for all tests."""
import os
import pytest

API_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cv-analyzer-53.preview.emergentagent.com")
BASE = f"{API_URL}/api"

TEST_USER = {"pseudo": "test_regression", "password": "TestReg2026!"}
ADMIN_USER = {"pseudo": "admin@reactifpro.fr", "password": "Choukette@777"}


@pytest.fixture(scope="session")
def api():
    return BASE


@pytest.fixture(scope="session")
def user_token(api):
    """Create test user and return token."""
    import requests
    # Register (may already exist)
    requests.post(f"{api}/auth/register", json={**TEST_USER, "role": "particulier"})
    r = requests.post(f"{api}/auth/login", json=TEST_USER)
    assert r.status_code == 200, f"Login failed: {r.text}"
    data = r.json()
    assert "token" in data
    return data["token"]


@pytest.fixture(scope="session")
def admin_token(api):
    """Login as admin and return token."""
    import requests
    r = requests.post(f"{api}/auth/login", json=ADMIN_USER)
    assert r.status_code == 200, f"Admin login failed: {r.text}"
    return r.json()["token"]
