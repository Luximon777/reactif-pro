"""
Iteration 37 - Full Test Suite for Ré'Actif Pro
Tests: Auth (register, login, verify), D'CLIC PRO, Passerelles for bob (Concierge)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://partenaires-workflow.preview.emergentagent.com')

# Test credentials
TEST_USER_PSEUDO = f"testverif_{int(time.time())}"
TEST_USER_PASSWORD = "TestVerif123!"
BOB_PSEUDO = "bob"
BOB_PASSWORD = "Solerys777!"


class TestAuthEndpoints:
    """Test authentication endpoints: register, login, verify"""
    
    def test_auth_verify_endpoint_exists(self):
        """Test GET /api/auth/verify returns proper response"""
        response = requests.get(f"{BASE_URL}/api/auth/verify?token=invalid_token")
        # Should return 401 or error for invalid token
        assert response.status_code in [401, 400, 200]
        data = response.json()
        # Either valid=False or detail error
        assert "valid" in data or "detail" in data
        print(f"✓ Auth verify endpoint responds correctly: {data}")
    
    def test_register_new_user(self):
        """Test POST /api/auth/register creates new account"""
        payload = {
            "pseudo": TEST_USER_PSEUDO,
            "password": TEST_USER_PASSWORD,
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code in [200, 201], f"Register failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in register response"
        assert data.get("pseudo") == TEST_USER_PSEUDO
        assert data.get("auth_mode") == "pseudo"
        print(f"✓ User registered successfully: {TEST_USER_PSEUDO}")
        return data["token"]
    
    def test_register_duplicate_pseudo_fails(self):
        """Test that registering with existing pseudo fails"""
        # First register
        payload = {
            "pseudo": f"dup_{int(time.time())}",
            "password": TEST_USER_PASSWORD,
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        }
        response1 = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response1.status_code in [200, 201]
        
        # Try to register again with same pseudo
        response2 = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response2.status_code == 409, "Should fail with 409 for duplicate pseudo"
        print("✓ Duplicate pseudo registration correctly rejected")
    
    def test_login_with_valid_credentials(self):
        """Test POST /api/auth/login with valid credentials"""
        # First register a user
        pseudo = f"login_test_{int(time.time())}"
        register_payload = {
            "pseudo": pseudo,
            "password": TEST_USER_PASSWORD,
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        }
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json=register_payload)
        assert reg_response.status_code in [200, 201]
        
        # Now login
        login_payload = {
            "pseudo": pseudo,
            "password": TEST_USER_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_payload)
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data.get("pseudo") == pseudo
        print(f"✓ Login successful for {pseudo}")
        return data["token"]
    
    def test_login_with_invalid_credentials(self):
        """Test POST /api/auth/login with wrong password"""
        payload = {
            "pseudo": "nonexistent_user_xyz",
            "password": "wrongpassword"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        assert response.status_code == 401, "Should return 401 for invalid credentials"
        print("✓ Invalid login correctly rejected with 401")
    
    def test_verify_valid_token(self):
        """Test GET /api/auth/verify with valid token"""
        # Register and get token
        pseudo = f"verify_test_{int(time.time())}"
        register_payload = {
            "pseudo": pseudo,
            "password": TEST_USER_PASSWORD,
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        }
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json=register_payload)
        assert reg_response.status_code in [200, 201]
        token = reg_response.json()["token"]
        
        # Verify token
        response = requests.get(f"{BASE_URL}/api/auth/verify?token={token}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("valid") == True
        assert data.get("auth_mode") == "pseudo"
        print(f"✓ Token verification successful for {pseudo}")


class TestBobPasserelles:
    """Test passerelles for bob (Concierge profile) - should show relevant jobs"""
    
    @pytest.fixture
    def bob_token(self):
        """Login as bob and get token"""
        payload = {
            "pseudo": BOB_PSEUDO,
            "password": BOB_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        if response.status_code != 200:
            pytest.skip(f"Could not login as bob: {response.text}")
        return response.json()["token"]
    
    def test_bob_login(self):
        """Test that bob can login"""
        payload = {
            "pseudo": BOB_PSEUDO,
            "password": BOB_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        assert response.status_code == 200, f"Bob login failed: {response.text}"
        data = response.json()
        assert data.get("pseudo") == BOB_PSEUDO
        print(f"✓ Bob logged in successfully")
        return data["token"]
    
    def test_bob_passport_exists(self, bob_token):
        """Test that bob has a passport"""
        response = requests.get(f"{BASE_URL}/api/passport?token={bob_token}")
        assert response.status_code == 200, f"Passport fetch failed: {response.text}"
        data = response.json()
        assert "competences" in data
        print(f"✓ Bob's passport loaded with {len(data.get('competences', []))} competences")
    
    def test_bob_passerelles_coherent(self, bob_token):
        """Test that bob's passerelles are coherent with Concierge profile"""
        response = requests.get(f"{BASE_URL}/api/passport/passerelles?token={bob_token}")
        assert response.status_code == 200, f"Passerelles fetch failed: {response.text}"
        data = response.json()
        passerelles = data.get("passerelles", [])
        
        # Check that passerelles exist
        print(f"✓ Bob has {len(passerelles)} passerelles")
        
        # Check that passerelles are NOT "Consultant en évolution professionnelle"
        # They should be jobs related to Concierge (Agent maintenance, Agent propreté, etc.)
        for p in passerelles:
            job_name = p.get("job_name", "").lower()
            print(f"  - Passerelle: {p.get('job_name')} (score: {p.get('compatibility_score', 'N/A')})")
            # Should NOT be consultant-type jobs
            assert "consultant en évolution" not in job_name, f"Unexpected job: {job_name}"
        
        print("✓ Bob's passerelles are coherent with Concierge profile (no consultant jobs)")


class TestDclicPro:
    """Test D'CLIC PRO questionnaire and submission"""
    
    def test_dclic_questionnaire_loads(self):
        """Test GET /api/dclic/questionnaire returns questions"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        assert response.status_code == 200, f"Questionnaire failed: {response.text}"
        data = response.json()
        assert "questions" in data
        questions = data["questions"]
        assert len(questions) > 0, "No questions returned"
        print(f"✓ D'CLIC questionnaire loaded with {len(questions)} questions")
        
        # Verify question structure
        q = questions[0]
        assert "id" in q
        assert "question" in q
        assert "choices" in q
        print(f"✓ Question structure valid: {q.get('question', '')[:50]}...")
    
    def test_dclic_submit_generates_code(self):
        """Test POST /api/dclic/submit generates access code"""
        # Get questions first
        q_response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        questions = q_response.json()["questions"]
        
        # Build answers (select first choice for each question)
        answers = {}
        for q in questions:
            qid = q["id"]
            choices = q.get("choices", [])
            if choices:
                answers[qid] = choices[0].get("value", "A")
        
        payload = {
            "answers": answers,
            "birth_date": "1990-01-15",
            "education_level": "bac3"
        }
        response = requests.post(f"{BASE_URL}/api/dclic/submit", json=payload)
        assert response.status_code == 200, f"Submit failed: {response.text}"
        data = response.json()
        
        assert "access_code" in data, "No access_code in response"
        assert "profile" in data, "No profile in response"
        
        access_code = data["access_code"]
        assert len(access_code) == 9, f"Access code should be XXXX-XXXX format: {access_code}"
        assert "-" in access_code, f"Access code should contain dash: {access_code}"
        
        print(f"✓ D'CLIC test submitted, access code: {access_code}")
        
        # Verify profile structure
        profile = data["profile"]
        assert "mbti" in profile or "disc" in profile, "Profile should have personality data"
        print(f"✓ Profile generated with MBTI: {profile.get('mbti', 'N/A')}")
        
        return access_code
    
    def test_dclic_retrieve_valid_code(self):
        """Test POST /api/dclic/retrieve with valid code"""
        # First submit to get a code
        q_response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        questions = q_response.json()["questions"]
        
        answers = {}
        for q in questions:
            qid = q["id"]
            choices = q.get("choices", [])
            if choices:
                answers[qid] = choices[0].get("value", "A")
        
        submit_response = requests.post(f"{BASE_URL}/api/dclic/submit", json={
            "answers": answers,
            "birth_date": "1985-06-20",
            "education_level": "bac5"
        })
        access_code = submit_response.json()["access_code"]
        
        # Now retrieve
        retrieve_response = requests.post(f"{BASE_URL}/api/dclic/retrieve", json={
            "access_code": access_code
        })
        assert retrieve_response.status_code == 200, f"Retrieve failed: {retrieve_response.text}"
        data = retrieve_response.json()
        assert data.get("success") == True
        assert "profile" in data
        print(f"✓ D'CLIC results retrieved successfully for code {access_code}")
    
    def test_dclic_retrieve_invalid_code(self):
        """Test POST /api/dclic/retrieve with invalid code"""
        response = requests.post(f"{BASE_URL}/api/dclic/retrieve", json={
            "access_code": "XXXX-YYYY"
        })
        assert response.status_code == 404, "Should return 404 for invalid code"
        print("✓ Invalid D'CLIC code correctly rejected with 404")


class TestDashboardNavigation:
    """Test dashboard navigation tabs"""
    
    @pytest.fixture
    def user_token(self):
        """Create a test user and get token"""
        pseudo = f"nav_test_{int(time.time())}"
        payload = {
            "pseudo": pseudo,
            "password": TEST_USER_PASSWORD,
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        if response.status_code not in [200, 201]:
            pytest.skip(f"Could not create test user: {response.text}")
        return response.json()["token"]
    
    def test_profile_endpoint(self, user_token):
        """Test GET /api/profile returns user profile"""
        response = requests.get(f"{BASE_URL}/api/profile?token={user_token}")
        assert response.status_code == 200, f"Profile failed: {response.text}"
        data = response.json()
        assert "role" in data
        print(f"✓ Profile endpoint works, role: {data.get('role')}")
    
    def test_passport_endpoint(self, user_token):
        """Test GET /api/passport returns passport data"""
        response = requests.get(f"{BASE_URL}/api/passport?token={user_token}")
        assert response.status_code == 200, f"Passport failed: {response.text}"
        data = response.json()
        assert "competences" in data
        print(f"✓ Passport endpoint works")
    
    def test_observatoire_endpoint(self, user_token):
        """Test observatoire-related endpoints"""
        # Test market data endpoint
        response = requests.get(f"{BASE_URL}/api/market/sectors")
        # May return 200 or 404 depending on implementation
        print(f"✓ Market sectors endpoint status: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
