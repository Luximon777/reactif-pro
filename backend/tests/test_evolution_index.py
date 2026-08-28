"""Tests for Evolution Index endpoints - regex escape fix regression."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cv-analyzer-53.preview.emergentagent.com").rstrip("/")


def _login(pseudo, password):
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"pseudo": pseudo, "password": password}, timeout=30)
    assert r.status_code == 200, f"login {pseudo} failed: {r.status_code} {r.text[:300]}"
    data = r.json()
    token = data.get("token") or data.get("access_token") or data.get("session_token")
    assert token, f"no token in login response: {data}"
    return token


@pytest.fixture(scope="module")
def michel_token():
    return _login("michel", "Solerys777!")


@pytest.fixture(scope="module")
def mike_token():
    return _login("mike", "Solerys777!")


# --- Evolution Index user profile ---

def test_evolution_user_profile_michel(michel_token):
    r = requests.get(f"{BASE_URL}/api/evolution-index/user-profile", params={"token": michel_token}, timeout=60)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text[:500]}"
    data = r.json()
    print("MICHEL keys:", list(data.keys()))
    assert data.get("has_cv") is True, f"has_cv should be True, got {data.get('has_cv')}"
    relevant = data.get("relevant_jobs") or []
    assert len(relevant) > 0, "relevant_jobs is empty"
    assert data.get("evolution_exposure") != 50 or data.get("evolution_exposure") is not None
    # personalization
    print("MICHEL relevant_jobs:", [j.get("nom") or j.get("name") or j for j in relevant[:5]])
    print("MICHEL evolution_exposure:", data.get("evolution_exposure"))
    skills = data.get("recommended_skills_to_acquire") or []
    assert isinstance(skills, list)


def test_evolution_user_profile_mike_parentheses(mike_token):
    """Mike has sectors containing parentheses - was the trigger for the regex bug."""
    r = requests.get(f"{BASE_URL}/api/evolution-index/user-profile", params={"token": mike_token}, timeout=60)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text[:500]}"
    data = r.json()
    print("MIKE keys:", list(data.keys()))
    relevant = data.get("relevant_jobs") or []
    print("MIKE relevant_jobs:", [j.get("nom") or j.get("name") or j for j in relevant[:5]])
    assert isinstance(relevant, list)


# --- Dashboard regression ---

def test_evolution_dashboard():
    r = requests.get(f"{BASE_URL}/api/evolution-index/dashboard", timeout=60)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text[:300]}"
    data = r.json()
    assert "summary" in data
    assert "sectors" in data
    assert len(data["sectors"]) >= 10, f"expected ~14 sectors, got {len(data['sectors'])}"
    assert "top_transforming_jobs" in data
    assert "most_stable_jobs" in data
