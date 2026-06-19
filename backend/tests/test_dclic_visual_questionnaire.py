"""
D'CLIC PRO Visual Questionnaire Tests
Tests for the new GitHub-integrated visual questionnaire with 26 questions
Source: GitHub Luximon777/declic-pro integrated into Ré'Actif Pro
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://cv-analyzer-53.preview.emergentagent.com').rstrip('/')

# Sample visual answers as specified in the test request
SAMPLE_VISUAL_ANSWERS = {
    # MBTI questions (v1-v8)
    "v1": "E",
    "v2": "E", 
    "v3": "N",
    "v4": "N1,N2,S1,S2",  # Ranking
    "v5": "F",
    "v6": "F",
    "v7": "J",
    "v8": "P",
    # DISC questions (v9-v10)
    "v9": "I,D,S,C",  # Ranking
    "v10": "S,I,D,C",  # Ranking
    # Ennéagramme questions (v11-v12)
    "v11": "2,9,6,3",  # Ranking
    "v12": "1,5,8,4",  # Ranking
    # RIASEC questions (r1-r8)
    "r1": "S",
    "r2": "A",
    "r3": "S",
    "r4": "S,A,E,I",  # Ranking
    "r5": "S",
    "r6": "S,A,I,E",  # Ranking
    "r7": "S",
    "r8": "S,A,E,I,C,R",  # Ranking
    # Vertus questions (vv1-vv6)
    "vv1": "humanite",
    "vv2": "justice",
    "vv3": "transcendance",
    "vv4": "bienveillance,autonomie,securite,reussite",  # Ranking
    "vv5": "generosite",
    "vv6": "ecoute,leadership,rigueur,initiative",  # Ranking
}


class TestVisualQuestionnaire:
    """Tests for GET /api/dclic/questionnaire/visual endpoint"""
    
    def test_visual_questionnaire_returns_200(self):
        """Visual questionnaire endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire/visual")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ GET /api/dclic/questionnaire/visual returns 200")
    
    def test_visual_questionnaire_returns_26_questions(self):
        """Visual questionnaire returns exactly 26 questions"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire/visual")
        data = response.json()
        assert "questions" in data, "Response missing 'questions' field"
        assert data.get("total") == 26, f"Expected 26 questions, got {data.get('total')}"
        assert len(data["questions"]) == 26, f"Expected 26 questions in array, got {len(data['questions'])}"
        print(f"✓ Visual questionnaire returns 26 questions (total: {data.get('total')})")
    
    def test_visual_questionnaire_format_field(self):
        """Visual questionnaire returns format='visual'"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire/visual")
        data = response.json()
        assert data.get("format") == "visual", f"Expected format='visual', got {data.get('format')}"
        print("✓ Visual questionnaire has format='visual'")
    
    def test_visual_questions_have_visual_or_ranking_type(self):
        """All visual questions have type 'visual' or 'ranking'"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire/visual")
        data = response.json()
        questions = data.get("questions", [])
        
        for q in questions:
            assert q.get("type") in ["visual", "ranking"], f"Question {q.get('id')} has invalid type: {q.get('type')}"
        
        visual_count = sum(1 for q in questions if q.get("type") == "visual")
        ranking_count = sum(1 for q in questions if q.get("type") == "ranking")
        print(f"✓ All questions have valid types: {visual_count} visual, {ranking_count} ranking")
    
    def test_visual_questions_have_choices_with_labels(self):
        """All visual questions have choices with labels"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire/visual")
        data = response.json()
        questions = data.get("questions", [])
        
        for q in questions:
            assert "choices" in q, f"Question {q.get('id')} missing 'choices'"
            assert len(q["choices"]) >= 2, f"Question {q.get('id')} has less than 2 choices"
            for choice in q["choices"]:
                assert "label" in choice, f"Choice in {q.get('id')} missing 'label'"
                assert "value" in choice, f"Choice in {q.get('id')} missing 'value'"
        
        print("✓ All questions have choices with labels and values")
    
    def test_visual_questions_have_category_headers(self):
        """Visual questions have category field for headers"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire/visual")
        data = response.json()
        questions = data.get("questions", [])
        
        categories = set()
        for q in questions:
            assert "category" in q, f"Question {q.get('id')} missing 'category'"
            categories.add(q["category"])
        
        expected_categories = {"energie", "perception", "decision", "structure", "disc", "ennea", "riasec", "vertus", "valeurs", "qualites", "savoirs_etre"}
        print(f"✓ Questions have categories: {categories}")


class TestLegacyQuestionnaire:
    """Tests for GET /api/dclic/questionnaire (legacy text format)"""
    
    def test_legacy_questionnaire_returns_200(self):
        """Legacy questionnaire endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ GET /api/dclic/questionnaire returns 200")
    
    def test_legacy_questionnaire_returns_15_questions(self):
        """Legacy questionnaire returns 15 text questions"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        data = response.json()
        assert "questions" in data, "Response missing 'questions' field"
        assert data.get("total") == 15, f"Expected 15 questions, got {data.get('total')}"
        print(f"✓ Legacy questionnaire returns 15 questions")


class TestFilieres:
    """Tests for GET /api/dclic/filieres endpoint"""
    
    def test_filieres_returns_200(self):
        """Filieres endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/dclic/filieres")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ GET /api/dclic/filieres returns 200")
    
    def test_filieres_returns_list(self):
        """Filieres endpoint returns list of filieres"""
        response = requests.get(f"{BASE_URL}/api/dclic/filieres")
        data = response.json()
        assert "filieres" in data, "Response missing 'filieres' field"
        assert isinstance(data["filieres"], list), "filieres should be a list"
        assert len(data["filieres"]) > 0, "filieres list should not be empty"
        print(f"✓ Filieres returns {len(data['filieres'])} filieres")


class TestMetiers:
    """Tests for GET /api/dclic/metiers endpoint"""
    
    def test_metiers_returns_200(self):
        """Metiers endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/dclic/metiers")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ GET /api/dclic/metiers returns 200")
    
    def test_metiers_returns_more_than_50(self):
        """Metiers endpoint returns more than 50 metiers"""
        response = requests.get(f"{BASE_URL}/api/dclic/metiers")
        data = response.json()
        assert "metiers" in data, "Response missing 'metiers' field"
        metiers_count = len(data["metiers"])
        assert metiers_count > 50, f"Expected > 50 metiers, got {metiers_count}"
        print(f"✓ Metiers returns {metiers_count} metiers (> 50)")


class TestVertus:
    """Tests for GET /api/dclic/vertus endpoint"""
    
    def test_vertus_returns_200(self):
        """Vertus endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/dclic/vertus")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ GET /api/dclic/vertus returns 200")
    
    def test_vertus_returns_6_vertus(self):
        """Vertus endpoint returns 6 vertus (Seligman & Peterson)"""
        response = requests.get(f"{BASE_URL}/api/dclic/vertus")
        data = response.json()
        assert "vertus" in data, "Response missing 'vertus' field"
        vertus = data["vertus"]
        expected_vertus = {"sagesse", "courage", "humanite", "justice", "temperance", "transcendance"}
        actual_vertus = set(vertus.keys())
        assert actual_vertus == expected_vertus, f"Expected {expected_vertus}, got {actual_vertus}"
        print(f"✓ Vertus returns 6 vertus: {list(vertus.keys())}")


class TestSubmitVisualAnswers:
    """Tests for POST /api/dclic/submit with visual format answers"""
    
    @pytest.fixture(scope="class")
    def submit_result(self):
        """Submit visual answers and cache result for multiple tests"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": SAMPLE_VISUAL_ANSWERS},
            timeout=120  # GPT-5.2 takes 20-40 seconds
        )
        return response
    
    def test_submit_returns_200(self, submit_result):
        """Submit endpoint returns 200"""
        assert submit_result.status_code == 200, f"Expected 200, got {submit_result.status_code}"
        print("✓ POST /api/dclic/submit returns 200")
    
    def test_submit_returns_success_true(self, submit_result):
        """Submit returns success=true"""
        data = submit_result.json()
        assert data.get("success") == True, f"Expected success=true, got {data.get('success')}"
        print("✓ Submit returns success=true")
    
    def test_submit_returns_access_code(self, submit_result):
        """Submit returns access_code"""
        data = submit_result.json()
        assert "access_code" in data, "Response missing 'access_code'"
        assert len(data["access_code"]) >= 8, f"Access code too short: {data['access_code']}"
        print(f"✓ Submit returns access_code: {data['access_code']}")
    
    def test_submit_returns_profile_with_mbti(self, submit_result):
        """Submit returns profile with mbti field"""
        data = submit_result.json()
        profile = data.get("profile", {})
        assert "mbti" in profile, "Profile missing 'mbti'"
        assert len(profile["mbti"]) == 4, f"MBTI should be 4 chars, got: {profile['mbti']}"
        print(f"✓ Profile has mbti: {profile['mbti']}")
    
    def test_submit_returns_profile_with_disc(self, submit_result):
        """Submit returns profile with disc field"""
        data = submit_result.json()
        profile = data.get("profile", {})
        assert "disc" in profile, "Profile missing 'disc'"
        assert profile["disc"] in ["D", "I", "S", "C"], f"Invalid DISC: {profile['disc']}"
        print(f"✓ Profile has disc: {profile['disc']}")
    
    def test_submit_returns_profile_with_ennea_dominant(self, submit_result):
        """Submit returns profile with ennea_dominant field"""
        data = submit_result.json()
        profile = data.get("profile", {})
        assert "ennea_dominant" in profile, "Profile missing 'ennea_dominant'"
        assert profile["ennea_dominant"] in range(1, 10), f"Invalid ennea: {profile['ennea_dominant']}"
        print(f"✓ Profile has ennea_dominant: {profile['ennea_dominant']}")
    
    def test_submit_returns_profile_with_riasec_profile(self, submit_result):
        """Submit returns profile with riasec_profile field"""
        data = submit_result.json()
        profile = data.get("profile", {})
        assert "riasec_profile" in profile, "Profile missing 'riasec_profile'"
        riasec = profile["riasec_profile"]
        assert "scores" in riasec, "riasec_profile missing 'scores'"
        assert "major" in riasec, "riasec_profile missing 'major'"
        print(f"✓ Profile has riasec_profile with major: {riasec.get('major')}")
    
    def test_submit_returns_profile_with_vertus_profile(self, submit_result):
        """Submit returns profile with vertus_profile containing required fields"""
        data = submit_result.json()
        profile = data.get("profile", {})
        assert "vertus_profile" in profile, "Profile missing 'vertus_profile'"
        vp = profile["vertus_profile"]
        
        # Check required fields
        required_fields = ["dominant", "dominant_name", "citation", "forces_caractere", 
                          "competences_transferables", "metiers_associes", "penseurs"]
        for field in required_fields:
            assert field in vp, f"vertus_profile missing '{field}'"
        
        print(f"✓ vertus_profile has all required fields: dominant={vp.get('dominant')}")
    
    def test_vertus_profile_has_penseurs_structure(self, submit_result):
        """vertus_profile.penseurs has orientaux and occidentaux arrays"""
        data = submit_result.json()
        vp = data.get("profile", {}).get("vertus_profile", {})
        penseurs = vp.get("penseurs", {})
        
        assert "orientaux" in penseurs, "penseurs missing 'orientaux'"
        assert "occidentaux" in penseurs, "penseurs missing 'occidentaux'"
        assert isinstance(penseurs["orientaux"], list), "penseurs.orientaux should be list"
        assert isinstance(penseurs["occidentaux"], list), "penseurs.occidentaux should be list"
        print(f"✓ penseurs has orientaux ({len(penseurs['orientaux'])}) and occidentaux ({len(penseurs['occidentaux'])})")
    
    def test_submit_returns_profile_with_compass(self, submit_result):
        """Submit returns profile with compass (functioning compass)"""
        data = submit_result.json()
        profile = data.get("profile", {})
        assert "compass" in profile, "Profile missing 'compass'"
        compass = profile["compass"]
        assert "axes" in compass, "compass missing 'axes'"
        print(f"✓ Profile has compass with {len(compass.get('axes', []))} axes")
    
    def test_submit_returns_profile_with_profile_narrative(self, submit_result):
        """Submit returns profile with profile_narrative containing portrait"""
        data = submit_result.json()
        profile = data.get("profile", {})
        assert "profile_narrative" in profile, "Profile missing 'profile_narrative'"
        narrative = profile["profile_narrative"]
        assert "portrait" in narrative, "profile_narrative missing 'portrait'"
        assert len(narrative["portrait"]) > 20, "portrait should be substantial text"
        print(f"✓ Profile has profile_narrative with portrait ({len(narrative['portrait'])} chars)")
    
    def test_submit_returns_profile_with_ofman_quadrant(self, submit_result):
        """Submit returns profile with ofman_quadrant"""
        data = submit_result.json()
        profile = data.get("profile", {})
        assert "ofman_quadrant" in profile, "Profile missing 'ofman_quadrant'"
        ofman = profile["ofman_quadrant"]
        assert isinstance(ofman, list), "ofman_quadrant should be list"
        print(f"✓ Profile has ofman_quadrant with {len(ofman)} zones")


class TestResultsRetrieval:
    """Tests for GET /api/dclic/results/{code} endpoint"""
    
    @pytest.fixture(scope="class")
    def access_code(self):
        """Get access code from submit"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": SAMPLE_VISUAL_ANSWERS},
            timeout=120
        )
        return response.json().get("access_code")
    
    def test_results_returns_200_with_valid_code(self, access_code):
        """Results endpoint returns 200 with valid code"""
        response = requests.get(f"{BASE_URL}/api/dclic/results/{access_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ GET /api/dclic/results/{access_code} returns 200")
    
    def test_results_returns_saved_profile(self, access_code):
        """Results endpoint returns saved profile correctly"""
        response = requests.get(f"{BASE_URL}/api/dclic/results/{access_code}")
        data = response.json()
        assert data.get("success") == True, "Expected success=true"
        assert "profile" in data, "Response missing 'profile'"
        assert "mbti" in data["profile"], "Saved profile missing 'mbti'"
        print(f"✓ Results returns saved profile with mbti: {data['profile'].get('mbti')}")
    
    def test_results_returns_404_for_invalid_code(self):
        """Results endpoint returns 404 for invalid code"""
        response = requests.get(f"{BASE_URL}/api/dclic/results/INVALID-CODE")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ GET /api/dclic/results/INVALID-CODE returns 404")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
