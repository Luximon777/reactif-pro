"""
Test suite for personalized CV correlation features:
- GET /api/observatoire/personalized - Personalized observatory data based on CV
- GET /api/evolution-index/user-profile - Enriched evolution analysis with CV data
- GET /api/learning - Learning modules with relevance scoring based on CV gaps
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestPersonalizedObservatoire:
    """Tests for /api/observatoire/personalized endpoint"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user for the test class"""
        pseudo = f"test_obs_{int(time.time())}"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200, f"Failed to create user: {response.text}"
        data = response.json()
        return {"token": data["token"], "pseudo": pseudo}
    
    def test_personalized_observatoire_no_cv(self, test_user):
        """Test personalized observatoire returns has_cv=false when no CV analyzed"""
        response = requests.get(f"{BASE_URL}/api/observatoire/personalized?token={test_user['token']}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["has_cv"] == False
        assert "message" in data
        assert data["user_skills_count"] == 0
        assert data["matches"] == []
        assert data["skill_gaps"] == []
        assert data["declining_alerts"] == []
        assert data["sector_relevance"] == []
        assert data["emerging_from_cv"] == []
    
    def test_personalized_observatoire_response_structure(self, test_user):
        """Test personalized observatoire response has correct structure"""
        response = requests.get(f"{BASE_URL}/api/observatoire/personalized?token={test_user['token']}")
        assert response.status_code == 200
        
        data = response.json()
        # Required fields
        assert "has_cv" in data
        assert "user_skills_count" in data
        assert "matches" in data
        assert "skill_gaps" in data
        assert "declining_alerts" in data
        assert "sector_relevance" in data
        assert "emerging_from_cv" in data
    
    def test_personalized_observatoire_invalid_token(self):
        """Test personalized observatoire with invalid token returns 401"""
        response = requests.get(f"{BASE_URL}/api/observatoire/personalized?token=invalid_token_xyz")
        assert response.status_code == 401


class TestEvolutionIndexUserProfile:
    """Tests for /api/evolution-index/user-profile endpoint"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user for the test class"""
        pseudo = f"test_evo_{int(time.time())}"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200, f"Failed to create user: {response.text}"
        data = response.json()
        return {"token": data["token"], "pseudo": pseudo}
    
    def test_user_profile_no_cv(self, test_user):
        """Test user profile returns has_cv=false when no CV analyzed"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/user-profile?token={test_user['token']}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["has_cv"] == False
        assert data["profile_sectors"] == []
        assert data["profile_skills"] == []
        assert data["emerging_from_cv"] == []
    
    def test_user_profile_data_sources(self, test_user):
        """Test user profile returns data_sources field"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/user-profile?token={test_user['token']}")
        assert response.status_code == 200
        
        data = response.json()
        assert "data_sources" in data
        assert "profile" in data["data_sources"]
        assert "passport" in data["data_sources"]
        assert "cv_analysis" in data["data_sources"]
        # All should be false for new user
        assert data["data_sources"]["cv_analysis"] == False
    
    def test_user_profile_exposure_interpretation(self, test_user):
        """Test user profile returns exposure interpretation"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/user-profile?token={test_user['token']}")
        assert response.status_code == 200
        
        data = response.json()
        assert "evolution_exposure" in data
        assert "exposure_interpretation" in data
        
        interp = data["exposure_interpretation"]
        assert "level" in interp
        assert "label" in interp
        assert "description" in interp
        assert "color" in interp
        assert "recommendation" in interp
    
    def test_user_profile_recommended_trainings(self, test_user):
        """Test user profile returns recommended trainings"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/user-profile?token={test_user['token']}")
        assert response.status_code == 200
        
        data = response.json()
        assert "recommended_trainings" in data
        assert isinstance(data["recommended_trainings"], list)
    
    def test_user_profile_recommended_skills(self, test_user):
        """Test user profile returns recommended skills to acquire"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/user-profile?token={test_user['token']}")
        assert response.status_code == 200
        
        data = response.json()
        assert "recommended_skills_to_acquire" in data
        assert isinstance(data["recommended_skills_to_acquire"], list)
    
    def test_user_profile_invalid_token(self):
        """Test user profile with invalid token returns 401"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/user-profile?token=invalid_token_xyz")
        assert response.status_code == 401


class TestLearningModulesRelevance:
    """Tests for /api/learning endpoint with relevance scoring"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user for the test class"""
        pseudo = f"test_learn_{int(time.time())}"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200, f"Failed to create user: {response.text}"
        data = response.json()
        return {"token": data["token"], "pseudo": pseudo}
    
    def test_learning_modules_returns_list(self, test_user):
        """Test learning modules returns a list"""
        response = requests.get(f"{BASE_URL}/api/learning?token={test_user['token']}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_learning_modules_have_relevance_fields(self, test_user):
        """Test learning modules have relevance, relevance_score, gaps_addressed fields"""
        response = requests.get(f"{BASE_URL}/api/learning?token={test_user['token']}")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) > 0, "No learning modules returned"
        
        for module in data:
            assert "relevance" in module, f"Module {module.get('id')} missing relevance field"
            assert "relevance_score" in module, f"Module {module.get('id')} missing relevance_score field"
            assert "gaps_addressed" in module, f"Module {module.get('id')} missing gaps_addressed field"
    
    def test_learning_modules_relevance_values(self, test_user):
        """Test learning modules relevance is one of: haute, moyenne, basse"""
        response = requests.get(f"{BASE_URL}/api/learning?token={test_user['token']}")
        assert response.status_code == 200
        
        data = response.json()
        valid_relevance = ["haute", "moyenne", "basse"]
        
        for module in data:
            assert module["relevance"] in valid_relevance, f"Invalid relevance: {module['relevance']}"
    
    def test_learning_modules_relevance_score_range(self, test_user):
        """Test learning modules relevance_score is between 0 and 100"""
        response = requests.get(f"{BASE_URL}/api/learning?token={test_user['token']}")
        assert response.status_code == 200
        
        data = response.json()
        
        for module in data:
            assert 0 <= module["relevance_score"] <= 100, f"Invalid relevance_score: {module['relevance_score']}"
    
    def test_learning_modules_gaps_addressed_is_list(self, test_user):
        """Test learning modules gaps_addressed is a list"""
        response = requests.get(f"{BASE_URL}/api/learning?token={test_user['token']}")
        assert response.status_code == 200
        
        data = response.json()
        
        for module in data:
            assert isinstance(module["gaps_addressed"], list), f"gaps_addressed should be list"
    
    def test_learning_modules_invalid_token(self):
        """Test learning modules with invalid token returns 401"""
        response = requests.get(f"{BASE_URL}/api/learning?token=invalid_token_xyz")
        assert response.status_code == 401


class TestGlobalDashboardsStillWork:
    """Tests to ensure global dashboards still work after personalization changes"""
    
    def test_observatoire_dashboard_works(self):
        """Test /api/observatoire/dashboard still returns global data"""
        response = requests.get(f"{BASE_URL}/api/observatoire/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "emerging_skills" in data
        assert "sector_trends" in data
        assert "indicators" in data
        assert isinstance(data["emerging_skills"], list)
        assert isinstance(data["sector_trends"], list)
    
    def test_evolution_dashboard_works(self):
        """Test /api/evolution-index/dashboard still returns global data"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert "summary" in data
        assert "distribution" in data
        assert "top_transforming_jobs" in data
        assert "most_stable_jobs" in data
        assert "sectors" in data
    
    def test_observatoire_emerging_skills_works(self):
        """Test /api/observatoire/emerging-skills still works"""
        response = requests.get(f"{BASE_URL}/api/observatoire/emerging-skills")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_observatoire_sector_trends_works(self):
        """Test /api/observatoire/sector-trends still works"""
        response = requests.get(f"{BASE_URL}/api/observatoire/sector-trends")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_evolution_jobs_works(self):
        """Test /api/evolution-index/jobs still works"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/jobs")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_evolution_sectors_works(self):
        """Test /api/evolution-index/sectors still works"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/sectors")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
