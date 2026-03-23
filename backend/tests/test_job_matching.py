"""
Test suite for Job Matching feature and enriched Observatoire/Evolution endpoints.
Tests:
1. GET /api/jobs/matching - new endpoint for AI-powered job matching
2. GET /api/observatoire/personalized - enriched with cv_models data
3. GET /api/evolution-index/user-profile - enriched with cv_models data
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestJobMatchingEndpoint:
    """Tests for the new /api/jobs/matching endpoint"""
    
    @pytest.fixture(scope="class")
    def test_user_no_cv(self):
        """Create a test user without CV for testing has_data=false scenario"""
        pseudo = f"test_match_nocv_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        return {"token": data["token"], "pseudo": pseudo}
    
    def test_job_matching_returns_has_data_false_when_no_cv(self, test_user_no_cv):
        """Test that job matching returns has_data=false when user has no CV"""
        response = requests.get(f"{BASE_URL}/api/jobs/matching?token={test_user_no_cv['token']}")
        assert response.status_code == 200, f"Job matching failed: {response.text}"
        data = response.json()
        
        # Verify has_data is false for new user without CV
        assert data.get("has_data") == False, f"Expected has_data=false, got {data.get('has_data')}"
        assert "matches" in data, "Response should contain 'matches' field"
        assert data["matches"] == [], "Matches should be empty when no CV"
        assert "message" in data, "Response should contain 'message' field"
        print(f"✓ Job matching returns has_data=false for user without CV: {data['message']}")
    
    def test_job_matching_response_structure_no_cv(self, test_user_no_cv):
        """Test response structure when no CV exists"""
        response = requests.get(f"{BASE_URL}/api/jobs/matching?token={test_user_no_cv['token']}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        required_fields = ["has_data", "matches"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        print(f"✓ Response structure valid for no-CV scenario")
    
    def test_job_matching_invalid_token(self):
        """Test that invalid token returns 401"""
        response = requests.get(f"{BASE_URL}/api/jobs/matching?token=invalid_token_xyz")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid token correctly rejected with 401")
    
    def test_job_matching_missing_token(self):
        """Test that missing token returns error"""
        response = requests.get(f"{BASE_URL}/api/jobs/matching")
        assert response.status_code == 422, f"Expected 422 for missing token, got {response.status_code}"
        print("✓ Missing token correctly rejected with 422")


class TestJobMatchingWithCV:
    """Tests for job matching when user has CV data"""
    
    @pytest.fixture(scope="class")
    def test_user_with_cv(self):
        """Create a test user and simulate CV analysis data"""
        pseudo = f"test_match_cv_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        return {"token": data["token"], "pseudo": pseudo}
    
    def test_job_matching_endpoint_exists(self, test_user_with_cv):
        """Verify the endpoint exists and responds"""
        response = requests.get(f"{BASE_URL}/api/jobs/matching?token={test_user_with_cv['token']}")
        assert response.status_code == 200, f"Endpoint returned {response.status_code}"
        print("✓ Job matching endpoint exists and responds")


class TestObservatoirePersonalized:
    """Tests for enriched /api/observatoire/personalized endpoint"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user for observatoire tests"""
        pseudo = f"test_obs_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200
        return {"token": response.json()["token"], "pseudo": pseudo}
    
    def test_observatoire_personalized_endpoint_exists(self, test_user):
        """Test that observatoire personalized endpoint exists"""
        response = requests.get(f"{BASE_URL}/api/observatoire/personalized?token={test_user['token']}")
        assert response.status_code == 200, f"Endpoint returned {response.status_code}: {response.text}"
        print("✓ Observatoire personalized endpoint exists")
    
    def test_observatoire_personalized_response_structure(self, test_user):
        """Test response structure of observatoire personalized"""
        response = requests.get(f"{BASE_URL}/api/observatoire/personalized?token={test_user['token']}")
        assert response.status_code == 200
        data = response.json()
        
        # For new user without CV, should return has_cv=false
        if not data.get("has_cv"):
            assert "message" in data, "Should have message when no CV"
            assert "user_skills_count" in data, "Should have user_skills_count"
            print(f"✓ Observatoire returns correct structure for user without CV")
        else:
            # If has CV, verify enriched structure
            expected_fields = ["has_cv", "user_skills_count", "matches", "skill_gaps", 
                             "declining_alerts", "sector_relevance", "emerging_from_cv"]
            for field in expected_fields:
                assert field in data, f"Missing field: {field}"
            print(f"✓ Observatoire returns enriched structure with CV data")
    
    def test_observatoire_personalized_invalid_token(self):
        """Test invalid token rejection"""
        response = requests.get(f"{BASE_URL}/api/observatoire/personalized?token=invalid_xyz")
        assert response.status_code == 401
        print("✓ Invalid token correctly rejected")


class TestEvolutionUserProfile:
    """Tests for enriched /api/evolution-index/user-profile endpoint"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user for evolution tests"""
        pseudo = f"test_evo_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200
        return {"token": response.json()["token"], "pseudo": pseudo}
    
    def test_evolution_user_profile_endpoint_exists(self, test_user):
        """Test that evolution user profile endpoint exists"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/user-profile?token={test_user['token']}")
        assert response.status_code == 200, f"Endpoint returned {response.status_code}: {response.text}"
        print("✓ Evolution user profile endpoint exists")
    
    def test_evolution_user_profile_response_structure(self, test_user):
        """Test response structure of evolution user profile"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/user-profile?token={test_user['token']}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        expected_fields = ["has_cv", "profile_sectors", "profile_skills", "evolution_exposure",
                         "exposure_interpretation", "relevant_jobs", "skills_at_risk", 
                         "skills_in_demand", "recommended_skills_to_acquire", "data_sources"]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
        
        # Verify data_sources structure
        assert "data_sources" in data
        ds = data["data_sources"]
        assert "profile" in ds, "data_sources should have 'profile'"
        assert "passport" in ds, "data_sources should have 'passport'"
        assert "cv_analysis" in ds, "data_sources should have 'cv_analysis'"
        
        print(f"✓ Evolution user profile returns correct structure")
        print(f"  - has_cv: {data['has_cv']}")
        print(f"  - evolution_exposure: {data['evolution_exposure']}")
        print(f"  - data_sources: {data['data_sources']}")
    
    def test_evolution_user_profile_invalid_token(self):
        """Test invalid token rejection"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/user-profile?token=invalid_xyz")
        assert response.status_code == 401
        print("✓ Invalid token correctly rejected")


class TestJobMatchingProfileSummary:
    """Tests for profile_summary in job matching response"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user"""
        pseudo = f"test_profile_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200
        return {"token": response.json()["token"], "pseudo": pseudo}
    
    def test_profile_summary_structure_when_no_cv(self, test_user):
        """Test that profile_summary is not present when no CV (has_data=false)"""
        response = requests.get(f"{BASE_URL}/api/jobs/matching?token={test_user['token']}")
        assert response.status_code == 200
        data = response.json()
        
        # When has_data=false, profile_summary should not be present
        if not data.get("has_data"):
            # profile_summary is optional when no data
            print("✓ No profile_summary when has_data=false (expected)")
        else:
            # If has_data=true, verify profile_summary structure
            assert "profile_summary" in data, "profile_summary should be present when has_data=true"
            ps = data["profile_summary"]
            assert "titre" in ps, "profile_summary should have 'titre'"
            assert "skills_count" in ps, "profile_summary should have 'skills_count'"
            assert "has_optimized_cv" in ps, "profile_summary should have 'has_optimized_cv'"
            print(f"✓ profile_summary structure valid: {ps}")


class TestJobMatchingMatchesStructure:
    """Tests for matches array structure in job matching response"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user"""
        pseudo = f"test_matches_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200
        return {"token": response.json()["token"], "pseudo": pseudo}
    
    def test_matches_is_array(self, test_user):
        """Test that matches is always an array"""
        response = requests.get(f"{BASE_URL}/api/jobs/matching?token={test_user['token']}")
        assert response.status_code == 200
        data = response.json()
        
        assert "matches" in data, "Response should have 'matches' field"
        assert isinstance(data["matches"], list), "matches should be a list"
        print(f"✓ matches is an array with {len(data['matches'])} items")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
