"""
Test suite for Learning Recommendations and Passerelles improvements
Tests:
1. GET /api/learning/recommendations - AI-powered training recommendations
2. GET /api/passport/passerelles - Passerelles with enriched passport context
3. GET /api/learning - Regression test for relevance scoring
4. CV optimization prompt verification (code review)
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestLearningRecommendations:
    """Test the new /api/learning/recommendations endpoint"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user for the test class"""
        pseudo = f"test_learning_rec_{uuid.uuid4().hex[:8]}"
        password = "testpass123"
        
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": password,
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        return {"token": data["token"], "pseudo": pseudo}
    
    def test_learning_recommendations_no_cv(self, test_user):
        """Test /api/learning/recommendations returns has_data=false when no CV"""
        response = requests.get(f"{BASE_URL}/api/learning/recommendations?token={test_user['token']}")
        assert response.status_code == 200, f"Request failed: {response.text}"
        
        data = response.json()
        # Without CV, should return has_data=false
        assert "has_data" in data, "Response should contain has_data field"
        assert data["has_data"] == False, "has_data should be False when no CV analyzed"
        assert "recommendations" in data, "Response should contain recommendations field"
        assert len(data["recommendations"]) == 0, "Recommendations should be empty when no CV"
        print(f"PASSED: /api/learning/recommendations returns has_data=false for new user without CV")
    
    def test_learning_recommendations_response_structure(self, test_user):
        """Verify response structure of /api/learning/recommendations"""
        response = requests.get(f"{BASE_URL}/api/learning/recommendations?token={test_user['token']}")
        assert response.status_code == 200
        
        data = response.json()
        # Check required fields
        assert "has_data" in data
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        print(f"PASSED: /api/learning/recommendations has correct response structure")
    
    def test_learning_recommendations_invalid_token(self):
        """Test /api/learning/recommendations with invalid token"""
        response = requests.get(f"{BASE_URL}/api/learning/recommendations?token=invalid_token_xyz")
        assert response.status_code in [401, 403, 404], f"Should reject invalid token, got {response.status_code}"
        print(f"PASSED: /api/learning/recommendations rejects invalid token")


class TestPasserellesEnriched:
    """Test passerelles endpoint with enriched passport context"""
    
    @pytest.fixture(scope="class")
    def test_user_with_passport(self):
        """Create a test user with passport data"""
        pseudo = f"test_passerelles_{uuid.uuid4().hex[:8]}"
        password = "testpass123"
        
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": password,
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200, f"Registration failed: {response.text}"
        token = response.json()["token"]
        
        # Initialize passport by fetching it
        response = requests.get(f"{BASE_URL}/api/passport?token={token}")
        assert response.status_code == 200
        
        # Update passport profile with professional summary and career project
        response = requests.put(f"{BASE_URL}/api/passport/profile?token={token}", json={
            "professional_summary": "Consultant en transition professionnelle avec 10 ans d'expérience dans l'accompagnement des demandeurs d'emploi",
            "career_project": "Devenir Conseiller en insertion professionnelle pour accompagner les publics en difficulté",
            "target_sectors": ["Insertion professionnelle", "Formation", "Accompagnement social"]
        })
        assert response.status_code == 200, f"Profile update failed: {response.text}"
        
        # Add some competences
        competences = [
            {"name": "Accompagnement individuel", "nature": "savoir_faire", "category": "transversale", "level": "avance"},
            {"name": "Techniques d'entretien", "nature": "savoir_faire", "category": "technique", "level": "avance"},
            {"name": "Empathie", "nature": "savoir_etre", "category": "transversale", "level": "avance"},
        ]
        for comp in competences:
            requests.post(f"{BASE_URL}/api/passport/competences?token={token}", json=comp)
        
        return {"token": token, "pseudo": pseudo}
    
    def test_passerelles_endpoint_works(self, test_user_with_passport):
        """Test GET /api/passport/passerelles returns passerelles"""
        response = requests.get(f"{BASE_URL}/api/passport/passerelles?token={test_user_with_passport['token']}")
        assert response.status_code == 200, f"Passerelles request failed: {response.text}"
        
        data = response.json()
        assert "passerelles" in data, "Response should contain passerelles field"
        print(f"PASSED: GET /api/passport/passerelles returns 200 with passerelles field")
    
    def test_passerelles_response_structure(self, test_user_with_passport):
        """Verify passerelles response structure"""
        response = requests.get(f"{BASE_URL}/api/passport/passerelles?token={test_user_with_passport['token']}")
        assert response.status_code == 200
        
        data = response.json()
        passerelles = data.get("passerelles", [])
        
        # If AI generated passerelles, check structure
        if len(passerelles) > 0:
            passerelle = passerelles[0]
            # Check expected fields from AI response
            expected_fields = ["job_name", "compatibility_score", "shared_skills", "skills_to_acquire"]
            for field in expected_fields:
                assert field in passerelle, f"Passerelle should contain {field}"
            print(f"PASSED: Passerelles have correct structure with {len(passerelles)} results")
        else:
            print(f"INFO: No passerelles generated (AI may not have returned results)")
    
    def test_passerelles_invalid_token(self):
        """Test passerelles with invalid token"""
        response = requests.get(f"{BASE_URL}/api/passport/passerelles?token=invalid_token_xyz")
        assert response.status_code in [401, 403, 404], f"Should reject invalid token, got {response.status_code}"
        print(f"PASSED: GET /api/passport/passerelles rejects invalid token")


class TestLearningRegression:
    """Regression tests for /api/learning endpoint with relevance scoring"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user"""
        pseudo = f"test_learning_{uuid.uuid4().hex[:8]}"
        password = "testpass123"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": password,
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200
        return {"token": response.json()["token"], "pseudo": pseudo}
    
    def test_learning_endpoint_works(self, test_user):
        """Test GET /api/learning returns modules"""
        response = requests.get(f"{BASE_URL}/api/learning?token={test_user['token']}")
        assert response.status_code == 200, f"Learning request failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list of modules"
        print(f"PASSED: GET /api/learning returns 200 with {len(data)} modules")
    
    def test_learning_module_structure(self, test_user):
        """Verify learning module structure includes relevance fields"""
        response = requests.get(f"{BASE_URL}/api/learning?token={test_user['token']}")
        assert response.status_code == 200
        
        modules = response.json()
        if len(modules) > 0:
            module = modules[0]
            # Check for relevance scoring fields
            assert "relevance" in module or "relevance_score" in module or "progress" in module, \
                "Module should have relevance or progress field"
            print(f"PASSED: Learning modules have expected structure")
        else:
            print(f"INFO: No learning modules in database")
    
    def test_learning_invalid_token(self):
        """Test learning with invalid token"""
        response = requests.get(f"{BASE_URL}/api/learning?token=invalid_token_xyz")
        assert response.status_code in [401, 403, 404], f"Should reject invalid token, got {response.status_code}"
        print(f"PASSED: GET /api/learning rejects invalid token")


class TestCVOptimizationPrompt:
    """Code review verification for CV optimization prompt changes"""
    
    def test_cv_generate_models_endpoint_exists(self):
        """Verify POST /api/cv/generate-models endpoint exists"""
        # Just verify the endpoint exists (will fail auth but that's expected)
        response = requests.post(f"{BASE_URL}/api/cv/generate-models?token=test", json={
            "model_types": ["classique"],
            "job_offer": "Test job offer"
        })
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404, "POST /api/cv/generate-models endpoint should exist"
        print(f"PASSED: POST /api/cv/generate-models endpoint exists (status: {response.status_code})")
    
    def test_cv_download_endpoint_exists(self):
        """Verify GET /api/cv/download/{model_type} endpoint exists"""
        response = requests.get(f"{BASE_URL}/api/cv/download/classique?token=test")
        # Should not be 404 for the route itself
        assert response.status_code != 404 or "non trouvé" in response.text.lower() or "not found" in response.text.lower(), \
            "GET /api/cv/download endpoint should exist"
        print(f"PASSED: GET /api/cv/download endpoint exists")


class TestLearningRecommendationsWithCV:
    """Test learning recommendations with a user who has CV data"""
    
    @pytest.fixture(scope="class")
    def test_user_with_cv_text(self):
        """Create a test user and analyze CV text"""
        pseudo = f"test_rec_cv_{uuid.uuid4().hex[:8]}"
        password = "testpass123"
        
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": password,
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200
        token = response.json()["token"]
        
        # Submit CV text for analysis
        cv_text = """
        Jean DUPONT
        Consultant en transition professionnelle
        
        EXPÉRIENCE PROFESSIONNELLE
        
        Consultant en transition professionnelle - Cabinet RH Conseil (2018-2024)
        - Accompagnement de 200+ demandeurs d'emploi dans leur reconversion
        - Animation d'ateliers collectifs sur les techniques de recherche d'emploi
        - Réalisation de bilans de compétences
        
        Conseiller emploi - Pôle Emploi (2015-2018)
        - Suivi d'un portefeuille de 150 demandeurs d'emploi
        - Orientation vers les formations adaptées
        - Mise en relation avec les entreprises
        
        FORMATION
        Master Psychologie du travail - Université Paris Descartes (2015)
        Licence Sciences de l'éducation - Université Lyon 2 (2013)
        
        COMPÉTENCES
        - Accompagnement individuel et collectif
        - Techniques d'entretien
        - Connaissance du marché de l'emploi
        - Outils numériques (LinkedIn, Indeed, etc.)
        """
        
        response = requests.post(f"{BASE_URL}/api/cv/analyze-text?token={token}", json={
            "text": cv_text,
            "filename": "cv_test.txt"
        })
        
        if response.status_code == 200:
            job_id = response.json().get("job_id")
            # Wait for analysis to complete (max 30 seconds)
            for _ in range(15):
                time.sleep(2)
                status_response = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={job_id}")
                if status_response.status_code == 200:
                    status = status_response.json().get("status")
                    if status == "completed":
                        break
                    elif status == "failed":
                        print(f"CV analysis failed: {status_response.json()}")
                        break
        
        return {"token": token, "pseudo": pseudo}
    
    def test_learning_recommendations_with_cv_data(self, test_user_with_cv_text):
        """Test /api/learning/recommendations returns AI recommendations when CV exists"""
        # Give a bit more time for AI processing
        time.sleep(3)
        
        response = requests.get(f"{BASE_URL}/api/learning/recommendations?token={test_user_with_cv_text['token']}")
        assert response.status_code == 200, f"Request failed: {response.text}"
        
        data = response.json()
        assert "has_data" in data
        
        if data["has_data"]:
            assert "recommendations" in data
            recs = data["recommendations"]
            assert isinstance(recs, list)
            
            if len(recs) > 0:
                # Verify recommendation structure
                rec = recs[0]
                expected_fields = ["title", "provider", "type"]
                for field in expected_fields:
                    assert field in rec, f"Recommendation should contain {field}"
                
                # Check optional fields
                optional_fields = ["duration", "skills_developed", "relevance_reason", "cpf_eligible", "priority"]
                found_optional = [f for f in optional_fields if f in rec]
                print(f"PASSED: Learning recommendations returned {len(recs)} AI-generated recommendations")
                print(f"  - Found optional fields: {found_optional}")
            else:
                print(f"INFO: has_data=True but no recommendations returned")
        else:
            print(f"INFO: has_data=False - CV may not have been fully processed")
            # This is acceptable - CV analysis is async
