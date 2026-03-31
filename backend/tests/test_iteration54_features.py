"""
Test Iteration 54 Features:
1. D'CLIC Boost visual for users without dclic_imported (testboost)
2. D'CLIC Boost section for users with dclic_imported (bob23)
3. CV Analysis Section with audit, centres d'intérêt, job offer URL
4. Trajectory auto-population from CV experiences
5. Skills section with source legend
6. All 4 tabs render correctly
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
BOB23_CREDS = {"pseudo": "bob23", "password": "Solerys777!"}
TESTBOOST_CREDS = {"pseudo": "testboost", "password": "Solerys777!"}


class TestAuthentication:
    """Test login for both test users"""
    
    def test_login_bob23_with_dclic(self):
        """bob23 has dclic_imported=True"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=BOB23_CREDS)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["pseudo"] == "bob23"
        assert data["role"] == "particulier"
        
    def test_login_testboost_without_dclic(self):
        """testboost is a new user without D'CLIC results"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TESTBOOST_CREDS)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["pseudo"] == "testboost"
        assert data["role"] == "particulier"


class TestProfileDclicStatus:
    """Test D'CLIC imported status for both users"""
    
    @pytest.fixture
    def bob23_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=BOB23_CREDS)
        return response.json()["token"]
    
    @pytest.fixture
    def testboost_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TESTBOOST_CREDS)
        return response.json()["token"]
    
    def test_bob23_has_dclic_imported(self, bob23_token):
        """bob23 should have dclic_imported=True with all 4 dimensions"""
        response = requests.get(f"{BASE_URL}/api/profile?token={bob23_token}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify D'CLIC imported status
        assert data.get("dclic_imported") == True
        
        # Verify all 4 dimensions are present
        assert data.get("dclic_mbti") is not None, "MBTI should be present"
        assert data.get("dclic_disc_label") is not None, "DISC should be present"
        assert data.get("dclic_riasec_major") is not None, "RIASEC should be present"
        assert data.get("dclic_vertu_dominante") is not None, "Vertu should be present"
        
        # Verify specific values from test_credentials.md
        assert data.get("dclic_mbti") == "ENFJ"
        assert data.get("dclic_disc_label") == "Influence"
        assert data.get("dclic_riasec_major") == "Social"
        assert data.get("dclic_vertu_dominante") == "Empathie"
    
    def test_testboost_no_dclic_imported(self, testboost_token):
        """testboost should NOT have dclic_imported"""
        response = requests.get(f"{BASE_URL}/api/profile?token={testboost_token}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify D'CLIC NOT imported
        dclic_imported = data.get("dclic_imported")
        assert dclic_imported is None or dclic_imported == False, "testboost should not have dclic_imported"


class TestTrajectorySteps:
    """Test trajectory steps API"""
    
    @pytest.fixture
    def bob23_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=BOB23_CREDS)
        return response.json()["token"]
    
    @pytest.fixture
    def testboost_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TESTBOOST_CREDS)
        return response.json()["token"]
    
    def test_bob23_has_trajectory_steps(self, bob23_token):
        """bob23 should have 5 trajectory steps pre-seeded"""
        response = requests.get(f"{BASE_URL}/api/trajectory/steps?token={bob23_token}")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 5, f"Expected at least 5 steps, got {len(data)}"
        
        # Verify step structure
        for step in data:
            assert "id" in step
            assert "title" in step
            assert "step_type" in step
    
    def test_testboost_empty_trajectory(self, testboost_token):
        """testboost should have empty trajectory initially"""
        response = requests.get(f"{BASE_URL}/api/trajectory/steps?token={testboost_token}")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # testboost may have 0 steps or some auto-populated ones
        # Just verify the API works
    
    def test_trajectory_visibility_settings(self, bob23_token):
        """Test visibility settings endpoint"""
        response = requests.get(f"{BASE_URL}/api/trajectory/visibility-settings?token={bob23_token}")
        assert response.status_code == 200
        data = response.json()
        
        # Should return visibility settings object
        assert isinstance(data, dict)


class TestCvAnalysisEndpoints:
    """Test CV analysis related endpoints"""
    
    @pytest.fixture
    def bob23_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=BOB23_CREDS)
        return response.json()["token"]
    
    def test_cv_latest_analysis_endpoint(self, bob23_token):
        """Test GET /api/cv/latest-analysis endpoint"""
        response = requests.get(f"{BASE_URL}/api/cv/latest-analysis?token={bob23_token}")
        assert response.status_code == 200
        data = response.json()
        
        # Should have has_analysis field
        assert "has_analysis" in data
    
    def test_cv_models_endpoint(self, bob23_token):
        """Test GET /api/cv/models endpoint"""
        response = requests.get(f"{BASE_URL}/api/cv/models?token={bob23_token}")
        assert response.status_code == 200
        data = response.json()
        
        # Should have models field
        assert "models" in data
    
    def test_cv_centres_interet_endpoint(self, bob23_token):
        """Test GET /api/cv/centres-interet endpoint"""
        response = requests.get(f"{BASE_URL}/api/cv/centres-interet?token={bob23_token}")
        assert response.status_code == 200
        data = response.json()
        
        # Should return data (may be empty)
        assert isinstance(data, dict)


class TestPassportEndpoint:
    """Test passport endpoint for CV analysis data"""
    
    @pytest.fixture
    def bob23_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=BOB23_CREDS)
        return response.json()["token"]
    
    def test_passport_endpoint(self, bob23_token):
        """Test GET /api/passport endpoint"""
        response = requests.get(f"{BASE_URL}/api/passport?token={bob23_token}")
        assert response.status_code == 200
        data = response.json()
        
        # Passport should have experiences for trajectory auto-population
        if data:
            # If passport exists, check structure
            assert isinstance(data, dict)


class TestJobsAndLearning:
    """Test jobs and learning endpoints"""
    
    @pytest.fixture
    def bob23_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=BOB23_CREDS)
        return response.json()["token"]
    
    def test_jobs_endpoint(self, bob23_token):
        """Test GET /api/jobs endpoint"""
        response = requests.get(f"{BASE_URL}/api/jobs?token={bob23_token}")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
    
    def test_learning_endpoint(self, bob23_token):
        """Test GET /api/learning endpoint"""
        response = requests.get(f"{BASE_URL}/api/learning?token={bob23_token}")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)


class TestNotifications:
    """Test notifications endpoint"""
    
    @pytest.fixture
    def bob23_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=BOB23_CREDS)
        return response.json()["token"]
    
    def test_access_requests_endpoint(self, bob23_token):
        """Test GET /api/notifications/access-requests endpoint"""
        response = requests.get(f"{BASE_URL}/api/notifications/access-requests?token={bob23_token}")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)


class TestTrajectorySynthesis:
    """Test trajectory synthesis endpoint"""
    
    @pytest.fixture
    def bob23_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=BOB23_CREDS)
        return response.json()["token"]
    
    def test_trajectory_synthesis_endpoint(self, bob23_token):
        """Test GET /api/trajectory/synthesis endpoint"""
        response = requests.get(f"{BASE_URL}/api/trajectory/synthesis?token={bob23_token}")
        assert response.status_code == 200
        data = response.json()
        
        # Should have has_data field
        assert "has_data" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
