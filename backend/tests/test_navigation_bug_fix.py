"""
Test suite for RE'ACTIF PRO Navigation Bug Fix
Bug: All landing page cards were redirecting to /observatoire instead of their correct destinations

Tests:
- Auth login API with marc19/Solerys777!
- Reactif impact API
- Reactif contact API
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthAPI:
    """Authentication endpoint tests for Espace Personnel"""
    
    def test_login_success_marc19(self):
        """Test login with marc19/Solerys777! credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudonyme": "marc19",
            "password": "Solerys777!"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should contain 'id'"
        assert "pseudonyme" in data, "Response should contain 'pseudonyme'"
        assert data["pseudonyme"] == "marc19", f"Expected pseudonyme 'marc19', got '{data['pseudonyme']}'"
        print(f"✅ Login successful for marc19, user_id: {data['id']}")
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudonyme": "invalid_user",
            "password": "wrong_password"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ Invalid credentials correctly rejected with 401")


class TestReactifAPI:
    """Tests for RE'ACTIF PRO API endpoints (used by /reactif/* pages)"""
    
    def test_reactif_impact_returns_stats(self):
        """Test GET /api/reactif/impact returns impact statistics"""
        response = requests.get(f"{BASE_URL}/api/reactif/impact")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Verify all expected fields are present
        expected_fields = ["taux_clarification", "taux_mise_en_action_30j", "progression_posture", "satisfaction"]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
            assert isinstance(data[field], (int, float)), f"Field {field} should be numeric"
        
        print(f"✅ Impact stats: clarification={data['taux_clarification']}%, action_30j={data['taux_mise_en_action_30j']}%, posture={data['progression_posture']}%, satisfaction={data['satisfaction']}%")
    
    def test_reactif_contact_rh(self):
        """Test POST /api/reactif/contact for RH type (used by /reactif/services-rh)"""
        response = requests.post(f"{BASE_URL}/api/reactif/contact", json={
            "type": "rh",
            "nom": "TEST_Contact RH",
            "email": "test_rh@example.com",
            "telephone": "0123456789",
            "organisation": "Test Organisation",
            "message": "Test message for RH contact"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "ok", f"Expected status 'ok', got '{data.get('status')}'"
        assert "id" in data, "Response should contain 'id'"
        print(f"✅ RH contact created with id: {data['id']}")
    
    def test_reactif_contact_partenaire(self):
        """Test POST /api/reactif/contact for partenaire type (used by /reactif/partenaires)"""
        response = requests.post(f"{BASE_URL}/api/reactif/contact", json={
            "type": "partenaire",
            "nom": "TEST_Contact Partenaire",
            "email": "test_partenaire@example.com",
            "telephone": "0987654321",
            "organisation": "Test Partenaire Org",
            "message": "Test message for partenaire contact"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "ok", f"Expected status 'ok', got '{data.get('status')}'"
        assert "id" in data, "Response should contain 'id'"
        print(f"✅ Partenaire contact created with id: {data['id']}")


class TestAPIHealth:
    """Basic API health checks"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "message" in data, "Response should contain 'message'"
        print(f"✅ API root: {data['message']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
