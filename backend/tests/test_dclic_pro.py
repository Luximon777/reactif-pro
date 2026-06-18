"""
D'CLIC PRO API Tests
Tests for the 5-bloc questionnaire system:
- Bloc 1: Archéologie des compétences (10 open_text questions)
- Bloc 2: RIASEC (10 scale questions 1-5)
- Bloc 3: Valeurs professionnelles (10 scale questions 1-5)
- Bloc 4: Savoir-être professionnels (10 scale questions 1-5)
- Bloc 5: Projection professionnelle (5 mixed questions)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestDclicQuestionnaire:
    """Tests for GET /api/dclic/questionnaire endpoint"""
    
    def test_questionnaire_returns_200(self):
        """Questionnaire endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/dclic/questionnaire returns 200")
    
    def test_questionnaire_has_5_blocs(self):
        """Questionnaire should have exactly 5 blocs"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        data = response.json()
        assert "blocs" in data, "Response should have 'blocs' key"
        assert len(data["blocs"]) == 5, f"Expected 5 blocs, got {len(data['blocs'])}"
        print("PASS: Questionnaire has 5 blocs")
    
    def test_bloc1_archeologie_has_10_questions(self):
        """Bloc 1 (Archéologie) should have 10 open_text questions"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        data = response.json()
        bloc1 = data["blocs"][0]
        
        assert bloc1["id"] == "archeologie", f"Expected bloc id 'archeologie', got '{bloc1['id']}'"
        assert bloc1["type"] == "open_text", f"Expected type 'open_text', got '{bloc1['type']}'"
        assert len(bloc1["questions"]) == 10, f"Expected 10 questions, got {len(bloc1['questions'])}"
        
        # Verify all questions are open_text type
        for q in bloc1["questions"]:
            assert q["type"] == "open_text", f"Question {q['id']} should be open_text"
        
        print("PASS: Bloc 1 (Archéologie) has 10 open_text questions")
    
    def test_bloc2_riasec_has_10_scale_questions(self):
        """Bloc 2 (RIASEC) should have 10 scale questions"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        data = response.json()
        bloc2 = data["blocs"][1]
        
        assert bloc2["id"] == "riasec", f"Expected bloc id 'riasec', got '{bloc2['id']}'"
        assert bloc2["type"] == "scale", f"Expected type 'scale', got '{bloc2['type']}'"
        assert bloc2["scale_min"] == 1, "Scale min should be 1"
        assert bloc2["scale_max"] == 5, "Scale max should be 5"
        assert len(bloc2["questions"]) == 10, f"Expected 10 questions, got {len(bloc2['questions'])}"
        
        print("PASS: Bloc 2 (RIASEC) has 10 scale questions (1-5)")
    
    def test_bloc3_valeurs_has_10_scale_questions(self):
        """Bloc 3 (Valeurs) should have 10 scale questions"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        data = response.json()
        bloc3 = data["blocs"][2]
        
        assert bloc3["id"] == "valeurs", f"Expected bloc id 'valeurs', got '{bloc3['id']}'"
        assert bloc3["type"] == "scale", f"Expected type 'scale', got '{bloc3['type']}'"
        assert len(bloc3["questions"]) == 10, f"Expected 10 questions, got {len(bloc3['questions'])}"
        
        print("PASS: Bloc 3 (Valeurs) has 10 scale questions")
    
    def test_bloc4_savoir_etre_has_10_scale_questions(self):
        """Bloc 4 (Savoir-être) should have 10 scale questions"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        data = response.json()
        bloc4 = data["blocs"][3]
        
        assert bloc4["id"] == "savoir_etre", f"Expected bloc id 'savoir_etre', got '{bloc4['id']}'"
        assert bloc4["type"] == "scale", f"Expected type 'scale', got '{bloc4['type']}'"
        assert len(bloc4["questions"]) == 10, f"Expected 10 questions, got {len(bloc4['questions'])}"
        
        print("PASS: Bloc 4 (Savoir-être) has 10 scale questions")
    
    def test_bloc5_projection_has_5_mixed_questions(self):
        """Bloc 5 (Projection) should have 5 mixed questions"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        data = response.json()
        bloc5 = data["blocs"][4]
        
        assert bloc5["id"] == "projection", f"Expected bloc id 'projection', got '{bloc5['id']}'"
        assert bloc5["type"] == "mixed", f"Expected type 'mixed', got '{bloc5['type']}'"
        assert len(bloc5["questions"]) == 5, f"Expected 5 questions, got {len(bloc5['questions'])}"
        
        # Verify mixed types: open_text and choice
        types = [q["type"] for q in bloc5["questions"]]
        assert "open_text" in types, "Bloc 5 should have open_text questions"
        assert "choice" in types, "Bloc 5 should have choice questions"
        
        print("PASS: Bloc 5 (Projection) has 5 mixed questions (open_text + choice)")
    
    def test_total_45_questions(self):
        """Total questions should be 45"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        data = response.json()
        
        total = sum(len(bloc["questions"]) for bloc in data["blocs"])
        assert total == 45, f"Expected 45 total questions, got {total}"
        
        print("PASS: Total 45 questions across all blocs")


class TestDclicSubmit:
    """Tests for POST /api/dclic/submit endpoint"""
    
    @pytest.fixture
    def sample_answers(self):
        """Generate sample answers for all 45 questions"""
        answers = {}
        
        # Bloc 1: Archéologie (10 open_text)
        for i in range(1, 11):
            answers[f"arche_{i}"] = f"Test answer for archeologie question {i}"
        
        # Bloc 2: RIASEC (10 scale 1-5)
        for i in range(1, 11):
            answers[f"riasec_{i}"] = (i % 5) + 1  # Values 1-5
        
        # Bloc 3: Valeurs (10 scale 1-5)
        for i in range(1, 11):
            answers[f"val_{i}"] = (i % 5) + 1
        
        # Bloc 4: Savoir-être (10 scale 1-5)
        for i in range(1, 11):
            answers[f"sep_{i}"] = (i % 5) + 1
        
        # Bloc 5: Projection (5 mixed)
        answers["proj_1"] = "Développeur, Designer"
        answers["proj_2"] = "Comptable, Avocat"
        answers["proj_3"] = "personnes"
        answers["proj_4"] = "bureau"
        answers["proj_5"] = "Un travail épanouissant avec de bonnes conditions"
        
        return answers
    
    def test_submit_returns_200_with_valid_answers(self, sample_answers):
        """Submit should return 200 with valid answers"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": sample_answers}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: POST /api/dclic/submit returns 200 with valid answers")
    
    def test_submit_returns_profile_structure(self, sample_answers):
        """Submit should return proper profile structure"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": sample_answers}
        )
        data = response.json()
        
        assert data.get("success") == True, "Response should have success=True"
        assert "access_code" in data, "Response should have access_code"
        assert "profile" in data, "Response should have profile"
        
        profile = data["profile"]
        
        # Check required profile sections
        assert "riasec" in profile, "Profile should have riasec"
        assert "valeurs" in profile, "Profile should have valeurs"
        assert "savoir_etre" in profile, "Profile should have savoir_etre"
        assert "archeologie_competences" in profile, "Profile should have archeologie_competences"
        assert "projection" in profile, "Profile should have projection"
        
        print("PASS: Submit returns proper profile structure")
    
    def test_submit_riasec_has_code_and_scores(self, sample_answers):
        """RIASEC profile should have code and scores"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": sample_answers}
        )
        data = response.json()
        riasec = data["profile"]["riasec"]
        
        assert "code" in riasec, "RIASEC should have code"
        assert "scores" in riasec, "RIASEC should have scores"
        assert "profile" in riasec, "RIASEC should have profile"
        
        # Code should be 3 letters from RIASEC
        code = riasec["code"]
        assert len(code) == 3, f"RIASEC code should be 3 letters, got '{code}'"
        for letter in code:
            assert letter in "RIASEC", f"Invalid RIASEC letter: {letter}"
        
        print(f"PASS: RIASEC has code '{code}' and scores")
    
    def test_submit_valeurs_has_dominantes(self, sample_answers):
        """Valeurs profile should have dominantes"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": sample_answers}
        )
        data = response.json()
        valeurs = data["profile"]["valeurs"]
        
        assert "dominantes" in valeurs, "Valeurs should have dominantes"
        assert len(valeurs["dominantes"]) > 0, "Should have at least one dominant value"
        
        # Each dominant should have code, score, label
        for v in valeurs["dominantes"]:
            assert "code" in v, "Dominant value should have code"
            assert "score" in v, "Dominant value should have score"
            assert "label" in v, "Dominant value should have label"
        
        print("PASS: Valeurs has dominantes with proper structure")
    
    def test_submit_savoir_etre_has_forces(self, sample_answers):
        """Savoir-être profile should have forces"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": sample_answers}
        )
        data = response.json()
        sep = data["profile"]["savoir_etre"]
        
        assert "forces" in sep, "Savoir-être should have forces"
        assert "all" in sep, "Savoir-être should have all"
        
        print("PASS: Savoir-être has forces and all")
    
    def test_submit_archeologie_has_categories(self, sample_answers):
        """Archéologie should have categories"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": sample_answers}
        )
        data = response.json()
        arche = data["profile"]["archeologie_competences"]
        
        assert "categories" in arche, "Archéologie should have categories"
        categories = arche["categories"]
        
        expected_cats = ["visibles", "enfouies", "transferables", "adaptatives", "potentielles"]
        for cat in expected_cats:
            assert cat in categories, f"Should have category '{cat}'"
        
        print("PASS: Archéologie has all 5 categories")
    
    def test_submit_projection_has_all_fields(self, sample_answers):
        """Projection should have all fields"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": sample_answers}
        )
        data = response.json()
        proj = data["profile"]["projection"]
        
        expected_fields = ["metiers_attires", "metiers_exclus", "preference_travail", "environnement", "vision_5_ans"]
        for field in expected_fields:
            assert field in proj, f"Projection should have '{field}'"
        
        print("PASS: Projection has all expected fields")
    
    def test_submit_rejects_incomplete_answers(self):
        """Submit should reject answers with less than 15 responses"""
        incomplete_answers = {
            "arche_1": "Test",
            "riasec_1": 3,
            "val_1": 4
        }
        
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": incomplete_answers}
        )
        assert response.status_code == 400, f"Expected 400 for incomplete answers, got {response.status_code}"
        
        print("PASS: Submit rejects incomplete answers (< 15)")


class TestDclicResults:
    """Tests for GET /api/dclic/results/{code} endpoint"""
    
    @pytest.fixture
    def submitted_result(self):
        """Submit answers and return the access code"""
        answers = {}
        for i in range(1, 11):
            answers[f"arche_{i}"] = f"Test answer {i}"
        for i in range(1, 11):
            answers[f"riasec_{i}"] = 4
        for i in range(1, 11):
            answers[f"val_{i}"] = 3
        for i in range(1, 11):
            answers[f"sep_{i}"] = 5
        answers["proj_1"] = "Métier test"
        answers["proj_2"] = "Métier exclus"
        answers["proj_3"] = "idees"
        answers["proj_4"] = "terrain"
        answers["proj_5"] = "Vision 5 ans test"
        
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": answers}
        )
        return response.json()
    
    def test_results_returns_200_with_valid_code(self, submitted_result):
        """Results endpoint should return 200 with valid code"""
        code = submitted_result["access_code"]
        response = requests.get(f"{BASE_URL}/api/dclic/results/{code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"PASS: GET /api/dclic/results/{code} returns 200")
    
    def test_results_returns_profile_data(self, submitted_result):
        """Results should return the saved profile data"""
        code = submitted_result["access_code"]
        response = requests.get(f"{BASE_URL}/api/dclic/results/{code}")
        data = response.json()
        
        # Should have the same structure as submit response
        assert "riasec" in data, "Results should have riasec"
        assert "valeurs" in data, "Results should have valeurs"
        assert "savoir_etre" in data, "Results should have savoir_etre"
        assert "archeologie_competences" in data, "Results should have archeologie_competences"
        assert "projection" in data, "Results should have projection"
        
        print("PASS: Results returns complete profile data")
    
    def test_results_returns_404_for_invalid_code(self):
        """Results should return 404 for invalid code"""
        response = requests.get(f"{BASE_URL}/api/dclic/results/INVALID-CODE-123")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        
        print("PASS: Results returns 404 for invalid code")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
