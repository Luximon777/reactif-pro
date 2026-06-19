"""
D'CLIC PRO Import Flow Tests
Tests the complete flow: Submit test → Get code → Retrieve profile → Import to passport → Verify
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Sample answers for D'CLIC test (visual format)
SAMPLE_ANSWERS = {
    "v1": "E", "v2": "I", "v3": "N", "v4": "N1,N2,S1,S2",
    "v5": "F", "v6": "T", "v7": "J", "v8": "P",
    "v9": "I,D,S,C", "v10": "S,C,D,I", "v11": "2,5,7,9", "v12": "1,3,6,8",
    "r1": "S", "r2": "A", "r3": "I", "r4": "S,A,I,R",
    "r5": "E", "r6": "A,S,I,C", "r7": "I", "r8": "S,A,R,E",
    "vv1": "sagesse", "vv2": "humanite", "vv3": "temperance",
    "vv4": "bienveillance,autonomie,securite,reussite",
    "vv5": "creativite", "vv6": "ecoute,initiative,rigueur,leadership"
}

# Test credentials
TEST_USER = {"pseudo": "mike7", "password": "Solerys777!"}


class TestDclicSubmit:
    """Test POST /api/dclic/submit - Submit test answers"""
    
    def test_submit_returns_success(self):
        """Submit should return success=true"""
        response = requests.post(f"{BASE_URL}/api/dclic/submit", json={"answers": SAMPLE_ANSWERS})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True, f"Expected success=true, got {data}"
    
    def test_submit_returns_access_code(self):
        """Submit should return an access_code in format XXXX-XXXX"""
        response = requests.post(f"{BASE_URL}/api/dclic/submit", json={"answers": SAMPLE_ANSWERS})
        assert response.status_code == 200
        data = response.json()
        access_code = data.get("access_code")
        assert access_code is not None, "access_code should be present"
        assert len(access_code) == 9, f"access_code should be 9 chars (XXXX-XXXX), got {len(access_code)}"
        assert "-" in access_code, "access_code should contain hyphen"
    
    def test_submit_returns_profile_with_mbti(self):
        """Submit should return profile with mbti field"""
        response = requests.post(f"{BASE_URL}/api/dclic/submit", json={"answers": SAMPLE_ANSWERS})
        assert response.status_code == 200
        profile = response.json().get("profile", {})
        assert "mbti" in profile, "profile should have mbti"
        assert len(profile["mbti"]) == 4, f"mbti should be 4 chars, got {profile['mbti']}"
    
    def test_submit_returns_profile_with_disc(self):
        """Submit should return profile with disc and disc_label"""
        response = requests.post(f"{BASE_URL}/api/dclic/submit", json={"answers": SAMPLE_ANSWERS})
        assert response.status_code == 200
        profile = response.json().get("profile", {})
        assert "disc" in profile, "profile should have disc"
        assert profile["disc"] in ["D", "I", "S", "C"], f"disc should be D/I/S/C, got {profile['disc']}"
        assert "disc_label" in profile, "profile should have disc_label"
    
    def test_submit_returns_profile_with_vertus(self):
        """Submit should return profile with vertus_profile.dominant_name"""
        response = requests.post(f"{BASE_URL}/api/dclic/submit", json={"answers": SAMPLE_ANSWERS})
        assert response.status_code == 200
        profile = response.json().get("profile", {})
        vertus = profile.get("vertus_profile", {})
        assert "dominant_name" in vertus, "vertus_profile should have dominant_name"
        assert vertus["dominant_name"] is not None, "dominant_name should not be None"
    
    def test_submit_returns_profile_with_riasec(self):
        """Submit should return profile with riasec_profile.major_name"""
        response = requests.post(f"{BASE_URL}/api/dclic/submit", json={"answers": SAMPLE_ANSWERS})
        assert response.status_code == 200
        profile = response.json().get("profile", {})
        riasec = profile.get("riasec_profile", {})
        assert "major_name" in riasec or "major" in riasec, "riasec_profile should have major or major_name"
    
    def test_submit_returns_profile_with_ennea(self):
        """Submit should return profile with ennea_dominant and ennea_profile.name"""
        response = requests.post(f"{BASE_URL}/api/dclic/submit", json={"answers": SAMPLE_ANSWERS})
        assert response.status_code == 200
        profile = response.json().get("profile", {})
        assert "ennea_dominant" in profile, "profile should have ennea_dominant"
        assert isinstance(profile["ennea_dominant"], int), "ennea_dominant should be int"
        ennea_profile = profile.get("ennea_profile", {})
        assert "name" in ennea_profile, "ennea_profile should have name"
    
    def test_submit_returns_competences_fortes(self):
        """Submit should return profile with competences_fortes"""
        response = requests.post(f"{BASE_URL}/api/dclic/submit", json={"answers": SAMPLE_ANSWERS})
        assert response.status_code == 200
        profile = response.json().get("profile", {})
        assert "competences_fortes" in profile, "profile should have competences_fortes"
        assert isinstance(profile["competences_fortes"], list), "competences_fortes should be list"


class TestDclicRetrieve:
    """Test POST /api/dclic/retrieve - Retrieve profile using access_code"""
    
    @pytest.fixture
    def access_code(self):
        """Create a test submission and return the access code"""
        response = requests.post(f"{BASE_URL}/api/dclic/submit", json={"answers": SAMPLE_ANSWERS})
        assert response.status_code == 200
        return response.json()["access_code"]
    
    def test_retrieve_with_valid_code(self, access_code):
        """Retrieve should return profile with valid code"""
        response = requests.post(f"{BASE_URL}/api/dclic/retrieve", json={"access_code": access_code})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "profile" in data
    
    def test_retrieve_returns_all_profile_fields(self, access_code):
        """Retrieve should return profile with all required fields for Dashboard preview"""
        response = requests.post(f"{BASE_URL}/api/dclic/retrieve", json={"access_code": access_code})
        assert response.status_code == 200
        profile = response.json().get("profile", {})
        
        # Check all fields needed by Dashboard preview
        assert "mbti" in profile, "profile should have mbti"
        assert "disc" in profile, "profile should have disc"
        assert "disc_label" in profile, "profile should have disc_label"
        
        vertus = profile.get("vertus_profile", {})
        assert "dominant_name" in vertus, "vertus_profile should have dominant_name"
        
        riasec = profile.get("riasec_profile", {})
        assert "major_name" in riasec or "major" in riasec, "riasec_profile should have major_name or major"
        
        assert "ennea_dominant" in profile, "profile should have ennea_dominant"
        ennea = profile.get("ennea_profile", {})
        assert "name" in ennea, "ennea_profile should have name"
    
    def test_retrieve_with_invalid_code(self):
        """Retrieve should return 404 for invalid code"""
        response = requests.post(f"{BASE_URL}/api/dclic/retrieve", json={"access_code": "XXXX-XXXX"})
        assert response.status_code == 404


class TestDclicClaim:
    """Test POST /api/dclic/claim - Mark code as claimed"""
    
    @pytest.fixture
    def access_code(self):
        """Create a test submission and return the access code"""
        response = requests.post(f"{BASE_URL}/api/dclic/submit", json={"answers": SAMPLE_ANSWERS})
        assert response.status_code == 200
        return response.json()["access_code"]
    
    def test_claim_with_valid_code(self, access_code):
        """Claim should return success=true"""
        response = requests.post(f"{BASE_URL}/api/dclic/claim?access_code={access_code}&user_id=test")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
    
    def test_claim_with_invalid_code(self):
        """Claim should return 404 for invalid code"""
        response = requests.post(f"{BASE_URL}/api/dclic/claim?access_code=XXXX-XXXX")
        assert response.status_code == 404


class TestDclicImport:
    """Test POST /api/profile/import-dclic - Import D'CLIC profile into user passport"""
    
    @pytest.fixture
    def auth_token(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["token"]
    
    @pytest.fixture
    def dclic_profile(self):
        """Create a test submission and return the profile"""
        response = requests.post(f"{BASE_URL}/api/dclic/submit", json={"answers": SAMPLE_ANSWERS})
        assert response.status_code == 200
        return response.json()["profile"]
    
    def test_import_requires_token(self):
        """Import should return 401 without token"""
        response = requests.post(f"{BASE_URL}/api/profile/import-dclic", json={"dclic_profile": {}})
        assert response.status_code == 401
    
    def test_import_with_valid_token(self, auth_token, dclic_profile):
        """Import should return success=true and profile_completion"""
        payload = {"dclic_profile": dclic_profile}
        response = requests.post(f"{BASE_URL}/api/profile/import-dclic?token={auth_token}", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True, f"Expected success=true, got {data}"
        assert "profile_completion" in data, "Response should have profile_completion"
        assert isinstance(data["profile_completion"], int), "profile_completion should be int"
    
    def test_import_sets_dclic_imported_flag(self, auth_token, dclic_profile):
        """After import, GET /api/profile should have dclic_imported=true"""
        # Import the profile
        payload = {"dclic_profile": dclic_profile}
        import_response = requests.post(f"{BASE_URL}/api/profile/import-dclic?token={auth_token}", json=payload)
        assert import_response.status_code == 200
        
        # Verify dclic_imported flag
        profile_response = requests.get(f"{BASE_URL}/api/profile?token={auth_token}")
        assert profile_response.status_code == 200, f"GET profile failed: {profile_response.text}"
        profile_data = profile_response.json()
        assert profile_data.get("dclic_imported") == True, f"Expected dclic_imported=true, got {profile_data}"


class TestFullDclicFlow:
    """Test the complete D'CLIC import flow end-to-end"""
    
    def test_complete_flow(self):
        """Test: Submit → Get code → Retrieve → Login → Import → Verify"""
        # Step 1: Submit test answers
        submit_response = requests.post(f"{BASE_URL}/api/dclic/submit", json={"answers": SAMPLE_ANSWERS})
        assert submit_response.status_code == 200, f"Submit failed: {submit_response.text}"
        submit_data = submit_response.json()
        access_code = submit_data["access_code"]
        print(f"Step 1 PASS: Got access_code={access_code}")
        
        # Step 2: Retrieve profile using code
        retrieve_response = requests.post(f"{BASE_URL}/api/dclic/retrieve", json={"access_code": access_code})
        assert retrieve_response.status_code == 200, f"Retrieve failed: {retrieve_response.text}"
        retrieve_data = retrieve_response.json()
        dclic_profile = retrieve_data["profile"]
        print(f"Step 2 PASS: Retrieved profile with mbti={dclic_profile.get('mbti')}")
        
        # Step 3: Login as test user
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        token = login_response.json()["token"]
        print(f"Step 3 PASS: Logged in, got token")
        
        # Step 4: Import D'CLIC profile
        import_payload = {"dclic_profile": dclic_profile}
        import_response = requests.post(f"{BASE_URL}/api/profile/import-dclic?token={token}", json=import_payload)
        assert import_response.status_code == 200, f"Import failed: {import_response.text}"
        import_data = import_response.json()
        assert import_data.get("success") == True
        print(f"Step 4 PASS: Import success, completion={import_data.get('profile_completion')}%")
        
        # Step 5: Claim the code
        claim_response = requests.post(f"{BASE_URL}/api/dclic/claim?access_code={access_code}&user_id=test")
        assert claim_response.status_code == 200, f"Claim failed: {claim_response.text}"
        print(f"Step 5 PASS: Code claimed")
        
        # Step 6: Verify profile has dclic_imported=true
        profile_response = requests.get(f"{BASE_URL}/api/profile?token={token}")
        assert profile_response.status_code == 200, f"GET profile failed: {profile_response.text}"
        profile_data = profile_response.json()
        assert profile_data.get("dclic_imported") == True, f"Expected dclic_imported=true, got {profile_data}"
        print(f"Step 6 PASS: Profile has dclic_imported=true")
        
        print("COMPLETE FLOW TEST PASSED!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
