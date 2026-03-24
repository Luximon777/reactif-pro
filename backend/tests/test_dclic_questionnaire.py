"""
Test D'CLIC PRO Questionnaire Feature
- GET /api/dclic/questionnaire - Returns 17 questions with correct structure
- POST /api/dclic/submit - Submit answers, returns access_code (XXXX-XXXX) and profile
- POST /api/dclic/retrieve - Retrieve profile by access code
- POST /api/dclic/claim - Mark results as claimed by user
"""
import pytest
import requests
import os
import uuid
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestDclicQuestionnaire:
    """Test D'CLIC PRO questionnaire endpoints"""
    
    def test_get_questionnaire_returns_17_questions(self):
        """GET /api/dclic/questionnaire - Should return 17 questions"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "questions" in data, "Response should contain 'questions' key"
        assert "total" in data, "Response should contain 'total' key"
        assert data["total"] == 17, f"Expected 17 questions, got {data['total']}"
        assert len(data["questions"]) == 17, f"Expected 17 questions in list, got {len(data['questions'])}"
        print(f"PASSED: GET /api/dclic/questionnaire returns {data['total']} questions")
    
    def test_questionnaire_structure(self):
        """Verify each question has correct structure"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        assert response.status_code == 200
        
        questions = response.json()["questions"]
        required_fields = ["id", "question", "category", "type", "choices"]
        
        for q in questions:
            for field in required_fields:
                assert field in q, f"Question {q.get('id')} missing field: {field}"
            
            # Verify choices structure
            assert len(q["choices"]) >= 2, f"Question {q['id']} should have at least 2 choices"
            for choice in q["choices"]:
                assert "id" in choice, f"Choice in {q['id']} missing 'id'"
                assert "value" in choice, f"Choice in {q['id']} missing 'value'"
                assert "label" in choice, f"Choice in {q['id']} missing 'label'"
        
        print(f"PASSED: All 17 questions have correct structure")
    
    def test_questionnaire_has_visual_and_ranking_types(self):
        """Verify questionnaire has both visual and ranking question types"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        assert response.status_code == 200
        
        questions = response.json()["questions"]
        types = set(q["type"] for q in questions)
        
        assert "visual" in types, "Should have visual type questions"
        assert "ranking" in types, "Should have ranking type questions"
        
        visual_count = sum(1 for q in questions if q["type"] == "visual")
        ranking_count = sum(1 for q in questions if q["type"] == "ranking")
        
        print(f"PASSED: Questionnaire has {visual_count} visual and {ranking_count} ranking questions")
    
    def test_visual_questions_have_images(self):
        """Verify visual questions have image URLs"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        assert response.status_code == 200
        
        questions = response.json()["questions"]
        visual_questions = [q for q in questions if q["type"] == "visual"]
        
        for q in visual_questions:
            for choice in q["choices"]:
                assert "image" in choice, f"Visual choice {choice['id']} missing image"
                assert choice["image"].startswith("http"), f"Image URL should be valid: {choice['image']}"
        
        print(f"PASSED: All visual questions have valid image URLs")
    
    def test_ranking_questions_have_4_or_more_choices(self):
        """Verify ranking questions have at least 4 choices"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        assert response.status_code == 200
        
        questions = response.json()["questions"]
        ranking_questions = [q for q in questions if q["type"] == "ranking"]
        
        for q in ranking_questions:
            assert len(q["choices"]) >= 4, f"Ranking question {q['id']} should have at least 4 choices, got {len(q['choices'])}"
            assert "instruction" in q, f"Ranking question {q['id']} should have instruction"
        
        print(f"PASSED: All {len(ranking_questions)} ranking questions have 4+ choices")


class TestDclicSubmit:
    """Test D'CLIC PRO submit endpoint"""
    
    @pytest.fixture(scope="class")
    def sample_answers(self):
        """Sample answers for all 17 questions"""
        return {
            "v1": "E",
            "v2": "I",
            "v3": "S",
            "v4": "S1,N1,S2,N2",
            "v5": "T",
            "v6": "F",
            "v7": "J",
            "v8": "P",
            "v9": "D,I,S,C",
            "v11": "2,3,5,4",
            "r1": "R",
            "r2": "A",
            "r3": "E",
            "vv1": "sagesse",
            "vv2": "humanite",
            "vv3": "temperance",
            "vv4": "autonomie,bienveillance,reussite,securite"
        }
    
    def test_submit_returns_access_code(self, sample_answers):
        """POST /api/dclic/submit - Should return access code in XXXX-XXXX format"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": sample_answers}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_code" in data, "Response should contain access_code"
        
        # Verify code format XXXX-XXXX
        code = data["access_code"]
        assert re.match(r'^[A-Z0-9]{4}-[A-Z0-9]{4}$', code), f"Code format invalid: {code}"
        
        print(f"PASSED: POST /api/dclic/submit returns access_code: {code}")
        return code
    
    def test_submit_returns_profile(self, sample_answers):
        """POST /api/dclic/submit - Should return profile with MBTI, DISC, RIASEC, Vertus"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": sample_answers}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "profile" in data, "Response should contain profile"
        
        profile = data["profile"]
        
        # Verify MBTI
        assert "mbti" in profile, "Profile should contain mbti"
        assert len(profile["mbti"]) == 4, f"MBTI should be 4 characters: {profile['mbti']}"
        
        # Verify DISC
        assert "disc_dominant" in profile, "Profile should contain disc_dominant"
        assert "disc_scores" in profile, "Profile should contain disc_scores"
        assert profile["disc_dominant"] in ["D", "I", "S", "C"], f"Invalid DISC: {profile['disc_dominant']}"
        
        # Verify RIASEC
        assert "riasec_major" in profile, "Profile should contain riasec_major"
        assert "riasec_minor" in profile, "Profile should contain riasec_minor"
        assert "riasec_scores" in profile, "Profile should contain riasec_scores"
        
        # Verify Vertus
        assert "vertu_dominante" in profile, "Profile should contain vertu_dominante"
        assert "vertu_dominante_name" in profile, "Profile should contain vertu_dominante_name"
        assert "vertus_scores" in profile, "Profile should contain vertus_scores"
        
        # Verify competences
        assert "competences_fortes" in profile, "Profile should contain competences_fortes"
        assert len(profile["competences_fortes"]) > 0, "Should have at least 1 competence"
        
        print(f"PASSED: Profile contains MBTI={profile['mbti']}, DISC={profile['disc_dominant']}, RIASEC={profile['riasec_major']}/{profile['riasec_minor']}, Vertu={profile['vertu_dominante']}")
    
    def test_submit_with_partial_answers(self):
        """POST /api/dclic/submit - Should work with partial answers"""
        partial_answers = {
            "v1": "E",
            "v2": "I",
            "v3": "S"
        }
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": partial_answers}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_code" in data
        assert "profile" in data
        
        print(f"PASSED: Submit with partial answers works")
    
    def test_submit_with_empty_answers(self):
        """POST /api/dclic/submit - Should work with empty answers"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": {}}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_code" in data
        assert "profile" in data
        
        print(f"PASSED: Submit with empty answers works")


class TestDclicRetrieve:
    """Test D'CLIC PRO retrieve endpoint"""
    
    @pytest.fixture(scope="class")
    def valid_code(self):
        """Create a valid access code by submitting answers"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": {"v1": "E", "v2": "I", "v3": "S"}}
        )
        assert response.status_code == 200
        return response.json()["access_code"]
    
    def test_retrieve_with_valid_code(self, valid_code):
        """POST /api/dclic/retrieve - Should return profile for valid code"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/retrieve",
            json={"access_code": valid_code}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] == True, "Response should have success=True"
        assert data["access_code"] == valid_code, "Response should echo access_code"
        assert "profile" in data, "Response should contain profile"
        assert "is_claimed" in data, "Response should contain is_claimed"
        
        print(f"PASSED: Retrieve with valid code {valid_code} returns profile")
    
    def test_retrieve_with_lowercase_code(self, valid_code):
        """POST /api/dclic/retrieve - Should work with lowercase code"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/retrieve",
            json={"access_code": valid_code.lower()}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        print(f"PASSED: Retrieve works with lowercase code")
    
    def test_retrieve_with_invalid_code(self):
        """POST /api/dclic/retrieve - Should return 404 for invalid code"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/retrieve",
            json={"access_code": "XXXX-YYYY"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "detail" in data, "Response should contain error detail"
        
        print(f"PASSED: Retrieve with invalid code returns 404")
    
    def test_retrieve_with_malformed_code(self):
        """POST /api/dclic/retrieve - Should return 400 for malformed code"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/retrieve",
            json={"access_code": "INVALID"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "detail" in data, "Response should contain error detail"
        
        print(f"PASSED: Retrieve with malformed code returns 400")
    
    def test_retrieve_with_empty_code(self):
        """POST /api/dclic/retrieve - Should return 400 for empty code"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/retrieve",
            json={"access_code": ""}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        
        print(f"PASSED: Retrieve with empty code returns 400")


class TestDclicClaim:
    """Test D'CLIC PRO claim endpoint"""
    
    @pytest.fixture(scope="class")
    def test_user_and_code(self):
        """Create test user and valid access code"""
        # Create user
        unique_id = str(uuid.uuid4())[:8]
        pseudo = f"TEST_dclic_claim_{unique_id}"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "Test1234!",
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        })
        
        if response.status_code not in [200, 201]:
            pytest.skip(f"Could not create test user: {response.status_code}")
        
        user_data = response.json()
        
        # Create access code
        submit_response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": {"v1": "E", "v2": "I"}}
        )
        assert submit_response.status_code == 200
        
        return {
            "token": user_data["token"],
            "profile_id": user_data.get("profile_id", "test_id"),
            "access_code": submit_response.json()["access_code"]
        }
    
    def test_claim_valid_code(self, test_user_and_code):
        """POST /api/dclic/claim - Should mark code as claimed"""
        code = test_user_and_code["access_code"]
        user_id = test_user_and_code["profile_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/dclic/claim",
            params={"access_code": code, "user_id": user_id}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] == True, "Response should have success=True"
        
        print(f"PASSED: Claim valid code {code} works")
    
    def test_claim_already_claimed_code(self, test_user_and_code):
        """POST /api/dclic/claim - Should return 400 for already claimed code"""
        code = test_user_and_code["access_code"]
        user_id = test_user_and_code["profile_id"]
        
        # Try to claim again
        response = requests.post(
            f"{BASE_URL}/api/dclic/claim",
            params={"access_code": code, "user_id": user_id}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        
        print(f"PASSED: Claim already claimed code returns 400")
    
    def test_retrieve_shows_claimed_status(self, test_user_and_code):
        """POST /api/dclic/retrieve - Should show is_claimed=True after claim"""
        code = test_user_and_code["access_code"]
        
        response = requests.post(
            f"{BASE_URL}/api/dclic/retrieve",
            json={"access_code": code}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_claimed"] == True, "is_claimed should be True after claim"
        
        print(f"PASSED: Retrieve shows is_claimed=True after claim")


class TestDclicProfileComputation:
    """Test D'CLIC PRO profile computation logic"""
    
    def test_mbti_computation_extravert(self):
        """Test MBTI computation for extravert profile"""
        answers = {
            "v1": "E",  # Extravert
            "v2": "E",  # Extravert
            "v3": "S",  # Sensing
            "v5": "T",  # Thinking
            "v6": "T",  # Thinking
            "v7": "J",  # Judging
            "v8": "J"   # Judging
        }
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": answers}
        )
        assert response.status_code == 200
        
        profile = response.json()["profile"]
        assert profile["mbti"][0] == "E", f"Expected E, got {profile['mbti'][0]}"
        assert profile["mbti"][1] == "S", f"Expected S, got {profile['mbti'][1]}"
        assert profile["mbti"][2] == "T", f"Expected T, got {profile['mbti'][2]}"
        assert profile["mbti"][3] == "J", f"Expected J, got {profile['mbti'][3]}"
        
        print(f"PASSED: MBTI computation for ESTJ profile: {profile['mbti']}")
    
    def test_mbti_computation_introvert(self):
        """Test MBTI computation for introvert profile"""
        answers = {
            "v1": "I",  # Introvert
            "v2": "I",  # Introvert
            "v3": "N",  # Intuition
            "v5": "F",  # Feeling
            "v6": "F",  # Feeling
            "v7": "P",  # Perceiving
            "v8": "P"   # Perceiving
        }
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": answers}
        )
        assert response.status_code == 200
        
        profile = response.json()["profile"]
        assert profile["mbti"][0] == "I", f"Expected I, got {profile['mbti'][0]}"
        assert profile["mbti"][1] == "N", f"Expected N, got {profile['mbti'][1]}"
        assert profile["mbti"][2] == "F", f"Expected F, got {profile['mbti'][2]}"
        assert profile["mbti"][3] == "P", f"Expected P, got {profile['mbti'][3]}"
        
        print(f"PASSED: MBTI computation for INFP profile: {profile['mbti']}")
    
    def test_disc_ranking_computation(self):
        """Test DISC computation from ranking question"""
        answers = {
            "v9": "D,I,S,C"  # D first, then I, S, C
        }
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": answers}
        )
        assert response.status_code == 200
        
        profile = response.json()["profile"]
        assert profile["disc_dominant"] == "D", f"Expected D dominant, got {profile['disc_dominant']}"
        
        # Verify scores (D should have highest)
        scores = profile["disc_scores"]
        assert scores["D"] > scores["I"], "D should score higher than I"
        assert scores["I"] > scores["S"], "I should score higher than S"
        assert scores["S"] > scores["C"], "S should score higher than C"
        
        print(f"PASSED: DISC ranking computation: {profile['disc_dominant']} - {scores}")
    
    def test_riasec_computation(self):
        """Test RIASEC computation from visual questions"""
        answers = {
            "r1": "R",  # Réaliste
            "r2": "A",  # Artistique
            "r3": "E"   # Entreprenant
        }
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": answers}
        )
        assert response.status_code == 200
        
        profile = response.json()["profile"]
        assert profile["riasec_major"] in ["R", "A", "E"], f"RIASEC major should be R, A, or E: {profile['riasec_major']}"
        assert profile["riasec_major_name"] != "", "RIASEC major name should not be empty"
        
        print(f"PASSED: RIASEC computation: {profile['riasec_major']}/{profile['riasec_minor']} ({profile['riasec_major_name']}/{profile['riasec_minor_name']})")
    
    def test_vertus_computation(self):
        """Test Vertus computation from visual questions"""
        answers = {
            "vv1": "sagesse",
            "vv2": "humanite",
            "vv3": "temperance",
            "vv4": "autonomie,bienveillance,reussite,securite"
        }
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": answers}
        )
        assert response.status_code == 200
        
        profile = response.json()["profile"]
        assert profile["vertu_dominante"] in ["sagesse", "courage", "humanite", "justice", "temperance", "transcendance"]
        assert profile["vertu_dominante_name"] != "", "Vertu name should not be empty"
        assert len(profile["forces"]) > 0, "Should have forces"
        assert len(profile["qualites"]) > 0, "Should have qualites"
        assert len(profile["savoirs_etre"]) > 0, "Should have savoirs_etre"
        
        print(f"PASSED: Vertus computation: {profile['vertu_dominante']} ({profile['vertu_dominante_name']})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
