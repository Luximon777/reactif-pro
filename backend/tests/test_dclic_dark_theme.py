"""
Test D'CLIC PRO Dark Theme Redesign
- GET /api/dclic/questionnaire - Returns 26 questions with unique images
- POST /api/dclic/submit - Submit answers, returns access_code (XXXX-XXXX) and full profile
- POST /api/dclic/retrieve - Retrieve profile by access code
- Verify no duplicate images in questionnaire
"""
import pytest
import requests
import os
import re
from collections import Counter

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://reactif-pro-sync.preview.emergentagent.com').rstrip('/')


class TestDclicQuestionnaire:
    """Test D'CLIC PRO questionnaire endpoints - 26 questions with unique images"""
    
    def test_get_questionnaire_returns_26_questions(self):
        """GET /api/dclic/questionnaire - Should return 26 questions"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "questions" in data, "Response should contain 'questions' key"
        assert "total" in data, "Response should contain 'total' key"
        assert data["total"] == 26, f"Expected 26 questions, got {data['total']}"
        assert len(data["questions"]) == 26, f"Expected 26 questions in list, got {len(data['questions'])}"
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
        
        print(f"PASSED: All {len(questions)} questions have correct structure")
    
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
        
        print(f"PASSED: Found {visual_count} visual and {ranking_count} ranking questions")
    
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
        
        print(f"PASSED: All {len(visual_questions)} visual questions have valid image URLs")
    
    def test_no_duplicate_images(self):
        """Verify no duplicate images in questionnaire"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        assert response.status_code == 200
        
        questions = response.json()["questions"]
        images = []
        
        for q in questions:
            for choice in q.get("choices", []):
                if choice.get("image"):
                    images.append(choice["image"])
        
        # Check for duplicates
        counts = Counter(images)
        duplicates = {k: v for k, v in counts.items() if v > 1}
        
        assert len(duplicates) == 0, f"Found duplicate images: {duplicates}"
        print(f"PASSED: All {len(images)} images are unique (no duplicates)")
    
    def test_ranking_questions_have_4_or_more_choices(self):
        """Verify ranking questions have at least 4 choices"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        assert response.status_code == 200
        
        questions = response.json()["questions"]
        ranking_questions = [q for q in questions if q["type"] == "ranking"]
        
        for q in ranking_questions:
            assert len(q["choices"]) >= 4, f"Ranking question {q['id']} should have at least 4 choices"
            assert "instruction" in q, f"Ranking question {q['id']} should have instruction"
        
        print(f"PASSED: All {len(ranking_questions)} ranking questions have 4+ choices")


class TestDclicSubmit:
    """Test D'CLIC PRO submit endpoint"""
    
    @pytest.fixture
    def sample_answers(self):
        """Sample answers for all 26 questions"""
        return {
            "v1": "E", "v2": "I", "v3": "S", "v4": "S1,N1,S2,N2", "v5": "T", "v6": "F",
            "v7": "J", "v8": "P", "v9": "D,I,S,C", "v10": "D,I,S,C", "v11": "2,3,5,4",
            "v12": "2,3,5,4", "r1": "R", "r2": "A", "r3": "E", "r4": "R,A,S,E",
            "r5": "I", "r6": "R,I,C,E", "r7": "S", "r8": "I,A,S,C",
            "vv1": "sagesse", "vv2": "humanite", "vv3": "temperance",
            "vv4": "autonomie,bienveillance,reussite,securite", "vv5": "creativite",
            "vv6": "initiative,ecoute,rigueur,leadership"
        }
    
    def test_submit_returns_access_code(self, sample_answers):
        """POST /api/dclic/submit - Should return access code in XXXX-XXXX format"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": sample_answers, "birth_date": "1990-05-15", "education_level": "bac3"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_code" in data, "Response should contain 'access_code'"
        
        # Verify access code format: XXXX-XXXX
        code = data["access_code"]
        assert re.match(r'^[A-Z0-9]{4}-[A-Z0-9]{4}$', code), f"Access code format invalid: {code}"
        
        print(f"PASSED: Submit returns access code: {code}")
    
    def test_submit_returns_full_profile(self, sample_answers):
        """POST /api/dclic/submit - Should return complete profile with all sub-profiles"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": sample_answers, "birth_date": "1990-05-15", "education_level": "bac3"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "profile" in data, "Response should contain 'profile'"
        
        profile = data["profile"]
        
        # Check for all required sub-profiles
        required_profiles = [
            "mbti", "vertus_profile", "riasec_profile", "compass",
            "integrated_analysis", "ofman_quadrant", "life_path", "cross_analysis"
        ]
        
        for key in required_profiles:
            assert key in profile, f"Profile missing '{key}'"
        
        # Verify MBTI format
        assert re.match(r'^[EI][SN][TF][JP]$', profile["mbti"]), f"Invalid MBTI: {profile['mbti']}"
        
        print(f"PASSED: Submit returns full profile with MBTI: {profile['mbti']}")
    
    def test_submit_with_birth_date_includes_life_path(self, sample_answers):
        """POST /api/dclic/submit with birth_date - Should include life_path and cross_analysis"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": sample_answers, "birth_date": "1990-05-15", "education_level": "bac3"}
        )
        assert response.status_code == 200
        
        profile = response.json()["profile"]
        
        assert profile.get("life_path") is not None, "life_path should be present when birth_date provided"
        assert profile.get("cross_analysis") is not None, "cross_analysis should be present when birth_date provided"
        
        print("PASSED: Submit with birth_date includes life_path and cross_analysis")
    
    def test_submit_without_birth_date(self, sample_answers):
        """POST /api/dclic/submit without birth_date - Should still work"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": sample_answers}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "access_code" in data
        assert "profile" in data
        
        print("PASSED: Submit without birth_date works correctly")


class TestDclicRetrieve:
    """Test D'CLIC PRO retrieve endpoint"""
    
    @pytest.fixture
    def valid_code(self):
        """Create a test submission and return the access code"""
        answers = {
            "v1": "E", "v2": "I", "v3": "S", "v4": "S1,N1,S2,N2", "v5": "T", "v6": "F",
            "v7": "J", "v8": "P", "v9": "D,I,S,C", "v10": "D,I,S,C", "v11": "2,3,5,4",
            "v12": "2,3,5,4", "r1": "R", "r2": "A", "r3": "E", "r4": "R,A,S,E",
            "r5": "I", "r6": "R,I,C,E", "r7": "S", "r8": "I,A,S,C",
            "vv1": "sagesse", "vv2": "humanite", "vv3": "temperance",
            "vv4": "autonomie,bienveillance,reussite,securite", "vv5": "creativite",
            "vv6": "initiative,ecoute,rigueur,leadership"
        }
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": answers}
        )
        return response.json()["access_code"]
    
    def test_retrieve_with_valid_code(self, valid_code):
        """POST /api/dclic/retrieve - Should return profile for valid code"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/retrieve",
            json={"access_code": valid_code}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "profile" in data
        assert data["access_code"] == valid_code
        
        print(f"PASSED: Retrieve with valid code {valid_code} returns profile")
    
    def test_retrieve_with_lowercase_code(self, valid_code):
        """POST /api/dclic/retrieve - Should work with lowercase code"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/retrieve",
            json={"access_code": valid_code.lower()}
        )
        assert response.status_code == 200
        
        print("PASSED: Retrieve works with lowercase code")
    
    def test_retrieve_with_invalid_code(self):
        """POST /api/dclic/retrieve - Should return 404 for invalid code"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/retrieve",
            json={"access_code": "XXXX-YYYY"}
        )
        assert response.status_code == 404
        
        print("PASSED: Retrieve returns 404 for invalid code")
    
    def test_retrieve_with_malformed_code(self):
        """POST /api/dclic/retrieve - Should return 400 for malformed code"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/retrieve",
            json={"access_code": "AB"}
        )
        assert response.status_code == 400
        
        print("PASSED: Retrieve returns 400 for malformed code")


class TestDclicProfileComputation:
    """Test D'CLIC PRO profile computation logic"""
    
    def test_mbti_computation_extravert(self):
        """Test MBTI computation with extravert answers"""
        answers = {
            "v1": "E", "v2": "E",  # Extravert
            "v3": "S", "v4": "S1,S2,N1,N2",  # Sensing
            "v5": "T", "v6": "T",  # Thinking
            "v7": "J", "v8": "J",  # Judging
            "v9": "D,I,S,C", "v10": "D,I,S,C", "v11": "2,3,5,4", "v12": "2,3,5,4",
            "r1": "R", "r2": "A", "r3": "E", "r4": "R,A,S,E",
            "r5": "I", "r6": "R,I,C,E", "r7": "S", "r8": "I,A,S,C",
            "vv1": "sagesse", "vv2": "humanite", "vv3": "temperance",
            "vv4": "autonomie,bienveillance,reussite,securite", "vv5": "creativite",
            "vv6": "initiative,ecoute,rigueur,leadership"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": answers}
        )
        assert response.status_code == 200
        
        profile = response.json()["profile"]
        mbti = profile["mbti"]
        
        assert mbti[0] == "E", f"Expected Extravert (E), got {mbti[0]}"
        print(f"PASSED: MBTI computation returns {mbti} for extravert answers")
    
    def test_mbti_computation_introvert(self):
        """Test MBTI computation with introvert answers"""
        answers = {
            "v1": "I", "v2": "I",  # Introvert
            "v3": "N", "v4": "N1,N2,S1,S2",  # Intuitive
            "v5": "F", "v6": "F",  # Feeling
            "v7": "P", "v8": "P",  # Perceiving
            "v9": "D,I,S,C", "v10": "D,I,S,C", "v11": "2,3,5,4", "v12": "2,3,5,4",
            "r1": "R", "r2": "A", "r3": "E", "r4": "R,A,S,E",
            "r5": "I", "r6": "R,I,C,E", "r7": "S", "r8": "I,A,S,C",
            "vv1": "sagesse", "vv2": "humanite", "vv3": "temperance",
            "vv4": "autonomie,bienveillance,reussite,securite", "vv5": "creativite",
            "vv6": "initiative,ecoute,rigueur,leadership"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": answers}
        )
        assert response.status_code == 200
        
        profile = response.json()["profile"]
        mbti = profile["mbti"]
        
        assert mbti[0] == "I", f"Expected Introvert (I), got {mbti[0]}"
        print(f"PASSED: MBTI computation returns {mbti} for introvert answers")
    
    def test_riasec_profile_structure(self):
        """Test RIASEC profile has correct structure"""
        answers = {
            "v1": "E", "v2": "I", "v3": "S", "v4": "S1,N1,S2,N2", "v5": "T", "v6": "F",
            "v7": "J", "v8": "P", "v9": "D,I,S,C", "v10": "D,I,S,C", "v11": "2,3,5,4",
            "v12": "2,3,5,4", "r1": "R", "r2": "A", "r3": "E", "r4": "R,A,S,E",
            "r5": "I", "r6": "R,I,C,E", "r7": "S", "r8": "I,A,S,C",
            "vv1": "sagesse", "vv2": "humanite", "vv3": "temperance",
            "vv4": "autonomie,bienveillance,reussite,securite", "vv5": "creativite",
            "vv6": "initiative,ecoute,rigueur,leadership"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": answers}
        )
        assert response.status_code == 200
        
        riasec = response.json()["profile"]["riasec_profile"]
        
        assert "scores" in riasec, "RIASEC should have scores"
        assert "major" in riasec, "RIASEC should have major"
        assert "minor" in riasec, "RIASEC should have minor"
        
        # Check all 6 RIASEC dimensions
        expected_keys = ["R", "I", "A", "S", "E", "C"]
        for key in expected_keys:
            assert key in riasec["scores"], f"RIASEC scores missing {key}"
        
        print(f"PASSED: RIASEC profile has correct structure with major={riasec['major']}")
    
    def test_vertus_profile_structure(self):
        """Test Vertus profile has correct structure"""
        answers = {
            "v1": "E", "v2": "I", "v3": "S", "v4": "S1,N1,S2,N2", "v5": "T", "v6": "F",
            "v7": "J", "v8": "P", "v9": "D,I,S,C", "v10": "D,I,S,C", "v11": "2,3,5,4",
            "v12": "2,3,5,4", "r1": "R", "r2": "A", "r3": "E", "r4": "R,A,S,E",
            "r5": "I", "r6": "R,I,C,E", "r7": "S", "r8": "I,A,S,C",
            "vv1": "sagesse", "vv2": "humanite", "vv3": "temperance",
            "vv4": "autonomie,bienveillance,reussite,securite", "vv5": "creativite",
            "vv6": "initiative,ecoute,rigueur,leadership"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": answers}
        )
        assert response.status_code == 200
        
        vertus = response.json()["profile"]["vertus_profile"]
        
        assert "vertus_scores" in vertus, "Vertus should have vertus_scores"
        assert "dominant" in vertus, "Vertus should have dominant"
        
        # Check all 6 vertus dimensions
        expected_vertus = ["sagesse", "courage", "humanite", "justice", "temperance", "transcendance"]
        for v in expected_vertus:
            assert v in vertus["vertus_scores"], f"Vertus scores missing {v}"
        
        print(f"PASSED: Vertus profile has correct structure with dominant={vertus['dominant']}")
    
    def test_compass_has_4_axes(self):
        """Test Compass (Boussole) has 4 MBTI axes"""
        answers = {
            "v1": "E", "v2": "I", "v3": "S", "v4": "S1,N1,S2,N2", "v5": "T", "v6": "F",
            "v7": "J", "v8": "P", "v9": "D,I,S,C", "v10": "D,I,S,C", "v11": "2,3,5,4",
            "v12": "2,3,5,4", "r1": "R", "r2": "A", "r3": "E", "r4": "R,A,S,E",
            "r5": "I", "r6": "R,I,C,E", "r7": "S", "r8": "I,A,S,C",
            "vv1": "sagesse", "vv2": "humanite", "vv3": "temperance",
            "vv4": "autonomie,bienveillance,reussite,securite", "vv5": "creativite",
            "vv6": "initiative,ecoute,rigueur,leadership"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": answers}
        )
        assert response.status_code == 200
        
        compass = response.json()["profile"]["compass"]
        
        assert "axes" in compass, "Compass should have axes"
        assert len(compass["axes"]) == 4, f"Compass should have 4 axes, got {len(compass['axes'])}"
        
        print("PASSED: Compass has 4 MBTI axes")
    
    def test_integrated_analysis_has_3_levels(self):
        """Test Integrated Analysis has 3 levels"""
        answers = {
            "v1": "E", "v2": "I", "v3": "S", "v4": "S1,N1,S2,N2", "v5": "T", "v6": "F",
            "v7": "J", "v8": "P", "v9": "D,I,S,C", "v10": "D,I,S,C", "v11": "2,3,5,4",
            "v12": "2,3,5,4", "r1": "R", "r2": "A", "r3": "E", "r4": "R,A,S,E",
            "r5": "I", "r6": "R,I,C,E", "r7": "S", "r8": "I,A,S,C",
            "vv1": "sagesse", "vv2": "humanite", "vv3": "temperance",
            "vv4": "autonomie,bienveillance,reussite,securite", "vv5": "creativite",
            "vv6": "initiative,ecoute,rigueur,leadership"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": answers}
        )
        assert response.status_code == 200
        
        integrated = response.json()["profile"]["integrated_analysis"]
        
        assert "niveau_1_preuves" in integrated, "Should have niveau_1_preuves"
        assert "niveau_2_fonctionnement" in integrated, "Should have niveau_2_fonctionnement"
        assert "niveau_3_regulation" in integrated, "Should have niveau_3_regulation"
        
        print("PASSED: Integrated Analysis has 3 levels")
    
    def test_ofman_quadrant_structure(self):
        """Test Ofman Quadrant (Zones de Vigilance) structure"""
        answers = {
            "v1": "E", "v2": "I", "v3": "S", "v4": "S1,N1,S2,N2", "v5": "T", "v6": "F",
            "v7": "J", "v8": "P", "v9": "D,I,S,C", "v10": "D,I,S,C", "v11": "2,3,5,4",
            "v12": "2,3,5,4", "r1": "R", "r2": "A", "r3": "E", "r4": "R,A,S,E",
            "r5": "I", "r6": "R,I,C,E", "r7": "S", "r8": "I,A,S,C",
            "vv1": "sagesse", "vv2": "humanite", "vv3": "temperance",
            "vv4": "autonomie,bienveillance,reussite,securite", "vv5": "creativite",
            "vv6": "initiative,ecoute,rigueur,leadership"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": answers}
        )
        assert response.status_code == 200
        
        ofman = response.json()["profile"]["ofman_quadrant"]
        
        assert isinstance(ofman, list), "Ofman quadrant should be a list"
        assert len(ofman) > 0, "Ofman quadrant should have at least one zone"
        
        # Check structure of first zone
        zone = ofman[0]
        assert "qualite" in zone, "Zone should have qualite"
        assert "piege" in zone, "Zone should have piege"
        assert "defi" in zone, "Zone should have defi"
        assert "allergie" in zone, "Zone should have allergie"
        
        print(f"PASSED: Ofman Quadrant has {len(ofman)} zones de vigilance")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
