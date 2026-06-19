"""Tests de régression — Auth & Profile"""
import requests
import pytest
import os
BASE = f"{os.environ.get('REACT_APP_BACKEND_URL', 'https://cv-analyzer-53.preview.emergentagent.com')}/api"
TEST_USER = {"pseudo": "test_regression", "password": "TestReg2026!"}


class TestAuth:
    """Authentification: register, login, token validation."""

    def test_register_new_user(self, api):
        r = requests.post(f"{api}/auth/register", json={
            "pseudo": "regression_auth_test",
            "password": "RegTest2026!",
            "role": "particulier"
        })
        assert r.status_code in [200, 400, 409], f"Register failed: {r.text}"

    def test_login_valid(self, api, user_token):
        """Token obtained via fixture means login works."""
        assert user_token is not None
        assert len(user_token) > 10

    def test_login_invalid_password(self, api):
        r = requests.post(f"{api}/auth/login", json={"pseudo": TEST_USER["pseudo"], "password": "wrong"})
        assert r.status_code in [401, 403]

    def test_login_nonexistent_user(self, api):
        r = requests.post(f"{api}/auth/login", json={"pseudo": "nobody_exists_xyz", "password": "test"})
        assert r.status_code in [401, 404]


class TestProfile:
    """Profile: read, pseudo enrichment, confidence scores."""

    def test_get_profile(self, api, user_token):
        r = requests.get(f"{api}/profile", params={"token": user_token})
        assert r.status_code == 200
        data = r.json()
        assert "pseudo" in data
        assert data["pseudo"] is not None, "pseudo should not be None"

    def test_get_profile_invalid_token(self, api):
        r = requests.get(f"{api}/profile", params={"token": "invalid_token_xyz"})
        assert r.status_code in [401, 404]

    def test_confidence_scores(self, api, user_token):
        r = requests.get(f"{api}/profile/confidence-scores/simple", params={"token": user_token})
        assert r.status_code == 200
        data = r.json()
        assert "global_pct" in data
        assert "dimensions" in data
        assert isinstance(data["dimensions"], list)
        assert len(data["dimensions"]) == 4
        for dim in data["dimensions"]:
            assert "key" in dim
            assert "label" in dim
            assert "pct" in dim
            assert 0 <= dim["pct"] <= 100
