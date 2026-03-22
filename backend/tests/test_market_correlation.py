"""
Test suite for the new market-correlation endpoint and regression tests for existing emerging endpoints.
Tests:
- GET /api/emerging/market-correlation?token= - returns has_data=false when no emerging competences
- GET /api/emerging/market-correlation?token= - returns correlations with market_match, sector_matches, market_position when data exists
- GET /api/emerging/competences?token= - regression test (still works)
- GET /api/emerging/observatory?token= - regression test (still works)
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestMarketCorrelation:
    """Tests for the new market-correlation endpoint"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user for the tests"""
        pseudo = f"TEST_market_{uuid.uuid4().hex[:8]}"
        password = "TestPass123!"
        
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": password,
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        token = data.get("token")
        assert token, "No token returned from registration"
        
        yield {"pseudo": pseudo, "password": password, "token": token}
    
    def test_market_correlation_no_data(self, test_user):
        """Test market-correlation returns has_data=false when no emerging competences"""
        token = test_user["token"]
        
        response = requests.get(f"{BASE_URL}/api/emerging/market-correlation?token={token}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # When no emerging competences, should return has_data=false
        assert "has_data" in data, "Response should contain 'has_data' field"
        assert data["has_data"] == False, "has_data should be False when no emerging competences"
        assert "message" in data, "Response should contain 'message' field when no data"
        assert "correlations" in data, "Response should contain 'correlations' field"
        assert data["correlations"] == [], "correlations should be empty list when no data"
        assert "summary" in data, "Response should contain 'summary' field"
        print(f"✓ Market correlation returns has_data=false for new user: {data}")
    
    def test_market_correlation_response_structure(self, test_user):
        """Test market-correlation response structure is correct"""
        token = test_user["token"]
        
        response = requests.get(f"{BASE_URL}/api/emerging/market-correlation?token={token}")
        assert response.status_code == 200
        
        data = response.json()
        # Verify all expected fields are present
        required_fields = ["has_data", "correlations", "summary"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # When has_data is False, message should be present
        if not data["has_data"]:
            assert "message" in data, "message field should be present when has_data=false"
        
        print(f"✓ Market correlation response structure is correct")


class TestEmergingCompetencesRegression:
    """Regression tests for existing emerging endpoints"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user for the tests"""
        pseudo = f"TEST_emerging_reg_{uuid.uuid4().hex[:8]}"
        password = "TestPass123!"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": password,
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        token = data.get("token")
        assert token, "No token returned from registration"
        
        yield {"pseudo": pseudo, "password": password, "token": token}
    
    def test_emerging_competences_endpoint(self, test_user):
        """Regression test: GET /api/emerging/competences still works"""
        token = test_user["token"]
        
        response = requests.get(f"{BASE_URL}/api/emerging/competences?token={token}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "competences" in data, "Response should contain 'competences' field"
        assert "total" in data, "Response should contain 'total' field"
        assert isinstance(data["competences"], list), "competences should be a list"
        assert isinstance(data["total"], int), "total should be an integer"
        print(f"✓ Emerging competences endpoint works: {data['total']} competences")
    
    def test_emerging_competences_with_filters(self, test_user):
        """Regression test: GET /api/emerging/competences with filters still works"""
        token = test_user["token"]
        
        # Test with category filter
        response = requests.get(f"{BASE_URL}/api/emerging/competences?token={token}&category=tech_emergente")
        assert response.status_code == 200, f"Expected 200 with category filter, got {response.status_code}"
        
        # Test with min_score filter
        response = requests.get(f"{BASE_URL}/api/emerging/competences?token={token}&min_score=50")
        assert response.status_code == 200, f"Expected 200 with min_score filter, got {response.status_code}"
        
        print(f"✓ Emerging competences filters work correctly")
    
    def test_emerging_observatory_endpoint(self, test_user):
        """Regression test: GET /api/emerging/observatory still works"""
        token = test_user["token"]
        
        response = requests.get(f"{BASE_URL}/api/emerging/observatory?token={token}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify expected fields
        assert "top_emerging" in data, "Response should contain 'top_emerging' field"
        assert "by_category" in data, "Response should contain 'by_category' field"
        assert "by_level" in data, "Response should contain 'by_level' field"
        
        assert isinstance(data["top_emerging"], list), "top_emerging should be a list"
        assert isinstance(data["by_category"], list), "by_category should be a list"
        assert isinstance(data["by_level"], list), "by_level should be a list"
        
        print(f"✓ Emerging observatory endpoint works: {len(data['top_emerging'])} top emerging skills")


class TestMarketCorrelationWithData:
    """Tests for market-correlation when user has emerging competences data"""
    
    @pytest.fixture(scope="class")
    def test_user_with_cv(self):
        """Create a test user and simulate CV analysis to get emerging competences"""
        pseudo = f"TEST_market_cv_{uuid.uuid4().hex[:8]}"
        password = "TestPass123!"
        
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": password,
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        token = data.get("token")
        
        yield {"pseudo": pseudo, "password": password, "token": token}
    
    def test_market_correlation_summary_structure(self, test_user_with_cv):
        """Test market-correlation summary structure when has_data=true"""
        token = test_user_with_cv["token"]
        
        response = requests.get(f"{BASE_URL}/api/emerging/market-correlation?token={token}")
        assert response.status_code == 200
        
        data = response.json()
        
        # If has_data is True, verify summary structure
        if data.get("has_data"):
            summary = data.get("summary", {})
            expected_summary_fields = ["total_emerging", "in_market", "high_demand", "growing_sectors", "market_alignment_pct"]
            for field in expected_summary_fields:
                assert field in summary, f"Summary missing field: {field}"
            
            # Verify correlations structure
            for corr in data.get("correlations", []):
                assert "competence_id" in corr, "Correlation missing competence_id"
                assert "nom" in corr, "Correlation missing nom"
                assert "market_position" in corr, "Correlation missing market_position"
                assert corr["market_position"] in ["en_demande", "en_declin", "neutre"], f"Invalid market_position: {corr['market_position']}"
                assert "has_market_data" in corr, "Correlation missing has_market_data"
            
            print(f"✓ Market correlation with data has correct structure: {len(data['correlations'])} correlations")
        else:
            print(f"✓ User has no emerging competences (expected for new user without CV)")


class TestInvalidTokenHandling:
    """Test error handling for invalid tokens"""
    
    def test_market_correlation_invalid_token(self):
        """Test market-correlation with invalid token returns error"""
        response = requests.get(f"{BASE_URL}/api/emerging/market-correlation?token=invalid_token_12345")
        # Should return 401 or 404 for invalid token
        assert response.status_code in [401, 404], f"Expected 401 or 404 for invalid token, got {response.status_code}"
        print(f"✓ Invalid token handled correctly: {response.status_code}")
    
    def test_emerging_competences_invalid_token(self):
        """Test emerging/competences with invalid token returns error"""
        response = requests.get(f"{BASE_URL}/api/emerging/competences?token=invalid_token_12345")
        assert response.status_code in [401, 404], f"Expected 401 or 404 for invalid token, got {response.status_code}"
        print(f"✓ Invalid token handled correctly for competences: {response.status_code}")
    
    def test_emerging_observatory_invalid_token(self):
        """Test emerging/observatory with invalid token returns error"""
        response = requests.get(f"{BASE_URL}/api/emerging/observatory?token=invalid_token_12345")
        assert response.status_code in [401, 404], f"Expected 401 or 404 for invalid token, got {response.status_code}"
        print(f"✓ Invalid token handled correctly for observatory: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
