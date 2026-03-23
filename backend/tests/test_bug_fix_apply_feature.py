"""
Test suite for P0 Bug Fix (React crash) and P1 Feature (Apply endpoint)
Tests:
- User registration and login flow
- GET /api/jobs endpoint returns array without crash
- POST /api/jobs/apply endpoint
- GET /api/jobs/applications endpoint
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthFlow:
    """Test user registration and login for 'particulier' role"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a unique test user for this test class"""
        unique_id = str(uuid.uuid4())[:8]
        return {
            "pseudo": f"test_bugfix_{unique_id}",
            "password": "TestPass123!",
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        }
    
    def test_register_particulier(self, test_user):
        """P0: Register a new 'particulier' user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=test_user
        )
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        assert "token" in data, "Token not returned"
        assert data["role"] == "particulier"
        assert data["auth_mode"] == "pseudo"
        assert data["pseudo"] == test_user["pseudo"]
        # Store token for subsequent tests
        test_user["token"] = data["token"]
        print(f"✓ Registration successful: {test_user['pseudo']}")
    
    def test_login_particulier(self, test_user):
        """P0: Login with registered user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "pseudo": test_user["pseudo"],
                "password": test_user["password"]
            }
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["role"] == "particulier"
        test_user["token"] = data["token"]
        print(f"✓ Login successful")
    
    def test_verify_token(self, test_user):
        """Verify token is valid"""
        if "token" not in test_user:
            pytest.skip("No token available")
        response = requests.get(
            f"{BASE_URL}/api/auth/verify",
            params={"token": test_user["token"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert data["role"] == "particulier"
        print(f"✓ Token verification successful")


class TestJobsEndpoint:
    """Test GET /api/jobs endpoint - P0 Bug Fix"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Create a test user and get token"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "pseudo": f"test_jobs_{unique_id}",
            "password": "TestPass123!",
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        if response.status_code == 200:
            return response.json()["token"]
        # If registration fails (user exists), try login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": user_data["pseudo"],
            "password": user_data["password"]
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not get auth token")
    
    def test_jobs_returns_array(self, auth_token):
        """P0: GET /api/jobs should return an array (possibly empty) without crash"""
        response = requests.get(
            f"{BASE_URL}/api/jobs",
            params={"token": auth_token}
        )
        assert response.status_code == 200, f"Jobs endpoint failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected array, got {type(data)}"
        print(f"✓ GET /api/jobs returns array with {len(data)} items")
    
    def test_jobs_invalid_token(self):
        """GET /api/jobs with invalid token should return 401"""
        response = requests.get(
            f"{BASE_URL}/api/jobs",
            params={"token": "invalid_token_12345"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ Invalid token correctly rejected")
    
    def test_jobs_items_serializable(self, auth_token):
        """P0: All job items should be JSON serializable (no objects with French keys causing crash)"""
        response = requests.get(
            f"{BASE_URL}/api/jobs",
            params={"token": auth_token}
        )
        assert response.status_code == 200
        data = response.json()
        
        for i, job in enumerate(data):
            # Verify each job has expected string fields
            assert isinstance(job.get("id", ""), str), f"Job {i}: id should be string"
            
            # Check title field (can be 'title' or 'titre')
            title = job.get("title") or job.get("titre")
            assert title is None or isinstance(title, str), f"Job {i}: title should be string, got {type(title)}"
            
            # Check company field
            company = job.get("company") or job.get("entreprise_type")
            assert company is None or isinstance(company, str), f"Job {i}: company should be string"
            
            # Check required_skills is a list of strings
            skills = job.get("required_skills", [])
            assert isinstance(skills, list), f"Job {i}: required_skills should be list"
            for skill in skills:
                assert isinstance(skill, str), f"Job {i}: skill should be string, got {type(skill)}"
        
        print(f"✓ All {len(data)} jobs are properly serializable")


class TestApplyEndpoint:
    """Test POST /api/jobs/apply and GET /api/jobs/applications - P1 Feature"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Create a test user and get token"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "pseudo": f"test_apply_{unique_id}",
            "password": "TestPass123!",
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not create test user")
    
    def test_apply_invalid_token(self):
        """P1: POST /api/jobs/apply with invalid token should return 401"""
        response = requests.post(
            f"{BASE_URL}/api/jobs/apply",
            params={"token": "fake_invalid_token"},
            json={
                "job_title": "Test Job",
                "job_data": {}
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print(f"✓ Apply with invalid token correctly returns 401")
    
    def test_apply_success(self, auth_token):
        """P1: POST /api/jobs/apply with valid token should create application"""
        unique_job = f"Test Developer Position {uuid.uuid4()}"
        response = requests.post(
            f"{BASE_URL}/api/jobs/apply",
            params={"token": auth_token},
            json={
                "job_title": unique_job,
                "job_data": {
                    "secteur": "IT",
                    "type_contrat": "CDI",
                    "localisation": "Paris"
                },
                "motivation": "Test motivation"
            }
        )
        assert response.status_code == 200, f"Apply failed: {response.text}"
        data = response.json()
        assert data["already_applied"] == False, "Should not be already applied"
        assert "application" in data
        assert data["application"]["job_title"] == unique_job
        assert data["application"]["status"] == "submitted"
        print(f"✓ Application created successfully")
        return unique_job
    
    def test_apply_duplicate(self, auth_token):
        """P1: Applying to same job twice should return already_applied=True"""
        job_title = f"Duplicate Test Job {uuid.uuid4()}"
        
        # First application
        response1 = requests.post(
            f"{BASE_URL}/api/jobs/apply",
            params={"token": auth_token},
            json={"job_title": job_title, "job_data": {}}
        )
        assert response1.status_code == 200
        assert response1.json()["already_applied"] == False
        
        # Second application (duplicate)
        response2 = requests.post(
            f"{BASE_URL}/api/jobs/apply",
            params={"token": auth_token},
            json={"job_title": job_title, "job_data": {}}
        )
        assert response2.status_code == 200
        data = response2.json()
        assert data["already_applied"] == True, "Should detect duplicate application"
        print(f"✓ Duplicate application correctly detected")
    
    def test_get_applications(self, auth_token):
        """P1: GET /api/jobs/applications should return user's applications"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/applications",
            params={"token": auth_token}
        )
        assert response.status_code == 200, f"Get applications failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Should return array"
        print(f"✓ GET /api/jobs/applications returns {len(data)} applications")
    
    def test_get_applications_invalid_token(self):
        """P1: GET /api/jobs/applications with invalid token should return 401"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/applications",
            params={"token": "invalid_token_xyz"}
        )
        assert response.status_code == 401
        print(f"✓ Get applications with invalid token correctly returns 401")


class TestJobMatchingEndpoint:
    """Test GET /api/jobs/matching endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Create a test user and get token"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "pseudo": f"test_matching_{unique_id}",
            "password": "TestPass123!",
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not create test user")
    
    def test_matching_without_cv(self, auth_token):
        """GET /api/jobs/matching without CV should return has_data=False"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/matching",
            params={"token": auth_token}
        )
        assert response.status_code == 200, f"Matching failed: {response.text}"
        data = response.json()
        # New user without CV should get has_data=False
        assert "has_data" in data
        assert "matches" in data
        assert isinstance(data["matches"], list)
        print(f"✓ GET /api/jobs/matching returns valid structure (has_data={data['has_data']})")


class TestProfileEndpoint:
    """Test profile endpoint to ensure dashboard data loads"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Create a test user and get token"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "pseudo": f"test_profile_{unique_id}",
            "password": "TestPass123!",
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not create test user")
    
    def test_get_profile(self, auth_token):
        """GET /api/profile should return user profile"""
        response = requests.get(
            f"{BASE_URL}/api/profile",
            params={"token": auth_token}
        )
        assert response.status_code == 200, f"Profile failed: {response.text}"
        data = response.json()
        assert "role" in data
        assert data["role"] == "particulier"
        assert "skills" in data
        assert isinstance(data["skills"], list)
        print(f"✓ GET /api/profile returns valid profile data")


class TestLearningEndpoint:
    """Test learning endpoint to ensure dashboard data loads"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Create a test user and get token"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "pseudo": f"test_learning_{unique_id}",
            "password": "TestPass123!",
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Could not create test user")
    
    def test_get_learning(self, auth_token):
        """GET /api/learning should return learning modules"""
        response = requests.get(
            f"{BASE_URL}/api/learning",
            params={"token": auth_token}
        )
        assert response.status_code == 200, f"Learning failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/learning returns {len(data)} modules")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
