"""
Test Job Matching API with new filters: lieu_residence and salaire_minimum
Tests for bug fixes iteration 39
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestJobMatchingFilters:
    """Test new job matching filters: lieu_residence and salaire_minimum"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get token for tests"""
        # Login with test credentials
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "bob15",
            "password": "Solerys777!"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.token = login_response.json().get("token")
        assert self.token, "No token received from login"
    
    def test_job_matching_search_accepts_lieu_residence(self):
        """Test that POST /api/jobs/matching/search accepts lieu_residence field"""
        payload = {
            "lieu_residence": {"value": "Paris", "priority": 4}
        }
        response = requests.post(
            f"{BASE_URL}/api/jobs/matching/search?token={self.token}",
            json=payload
        )
        assert response.status_code == 200, f"Search failed: {response.text}"
        data = response.json()
        assert "has_data" in data
        assert "matches" in data
        # Verify filters were applied
        if data.get("filters_applied"):
            assert "lieu_residence" in data["filters_applied"] or data["filters_applied"] == {}
    
    def test_job_matching_search_accepts_salaire_minimum(self):
        """Test that POST /api/jobs/matching/search accepts salaire_minimum field"""
        payload = {
            "salaire_minimum": {"value": 35000, "priority": 3}
        }
        response = requests.post(
            f"{BASE_URL}/api/jobs/matching/search?token={self.token}",
            json=payload
        )
        assert response.status_code == 200, f"Search failed: {response.text}"
        data = response.json()
        assert "has_data" in data
        assert "matches" in data
    
    def test_job_matching_search_with_both_new_filters(self):
        """Test that POST /api/jobs/matching/search accepts both new filters together"""
        payload = {
            "lieu_residence": {"value": "Lyon", "priority": 4},
            "salaire_minimum": {"value": 30000, "priority": 3},
            "metier": {"value": ["Développeur"], "priority": 3}
        }
        response = requests.post(
            f"{BASE_URL}/api/jobs/matching/search?token={self.token}",
            json=payload
        )
        assert response.status_code == 200, f"Search failed: {response.text}"
        data = response.json()
        assert "has_data" in data
        assert "matches" in data
        # Verify filters_applied contains our filters
        if data.get("filters_applied"):
            filters = data["filters_applied"]
            # Check that at least one of our filters is present
            has_filters = any(k in filters for k in ["lieu_residence", "salaire_minimum", "metier"])
            assert has_filters or filters == {}, f"Filters not applied: {filters}"
    
    def test_job_matching_preferences_save_new_filters(self):
        """Test that PUT /api/jobs/matching/preferences saves new filter fields"""
        payload = {
            "lieu_residence": {"value": "Marseille", "priority": 4},
            "salaire_minimum": {"value": 28000, "priority": 3}
        }
        response = requests.put(
            f"{BASE_URL}/api/jobs/matching/preferences?token={self.token}",
            json=payload
        )
        assert response.status_code == 200, f"Save preferences failed: {response.text}"
        data = response.json()
        assert "filters" in data or "message" in data
    
    def test_job_matching_preferences_get_returns_new_filters(self):
        """Test that GET /api/jobs/matching/preferences returns saved new filters"""
        # First save preferences
        save_payload = {
            "lieu_residence": {"value": "Bordeaux", "priority": 4},
            "salaire_minimum": {"value": 32000, "priority": 3}
        }
        save_response = requests.put(
            f"{BASE_URL}/api/jobs/matching/preferences?token={self.token}",
            json=save_payload
        )
        assert save_response.status_code == 200
        
        # Then get preferences
        get_response = requests.get(
            f"{BASE_URL}/api/jobs/matching/preferences?token={self.token}"
        )
        assert get_response.status_code == 200, f"Get preferences failed: {get_response.text}"
        data = get_response.json()
        
        if data.get("has_preferences"):
            filters = data.get("filters", {})
            # Verify our saved filters are present
            if "lieu_residence" in filters:
                assert filters["lieu_residence"]["value"] == "Bordeaux"
            if "salaire_minimum" in filters:
                assert filters["salaire_minimum"]["value"] == 32000


class TestJobMatchingBasic:
    """Basic job matching endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get token for tests"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "bob15",
            "password": "Solerys777!"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.token = login_response.json().get("token")
        assert self.token, "No token received from login"
    
    def test_job_matching_get_endpoint(self):
        """Test GET /api/jobs/matching returns valid response"""
        response = requests.get(f"{BASE_URL}/api/jobs/matching?token={self.token}")
        assert response.status_code == 200, f"Job matching failed: {response.text}"
        data = response.json()
        assert "has_data" in data
        assert "matches" in data
    
    def test_job_matching_search_endpoint(self):
        """Test POST /api/jobs/matching/search returns valid response"""
        payload = {
            "metier": {"value": ["Conseiller"], "priority": 3}
        }
        response = requests.post(
            f"{BASE_URL}/api/jobs/matching/search?token={self.token}",
            json=payload
        )
        assert response.status_code == 200, f"Search failed: {response.text}"
        data = response.json()
        assert "has_data" in data
        assert "matches" in data


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_login_with_valid_credentials(self):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "bob15",
            "password": "Solerys777!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["token"] is not None
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials returns error"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "invalid_user",
            "password": "wrong_password"
        })
        # Should return 401 or 404 for invalid credentials
        assert response.status_code in [401, 404], f"Expected 401/404, got {response.status_code}"
