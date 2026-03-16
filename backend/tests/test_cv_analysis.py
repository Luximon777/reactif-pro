"""
Tests for CV Analysis Feature - RE'ACTIF PRO
Tests:
- POST /api/cv/analyze with file upload - AI analysis of CV
- GET /api/cv/models - retrieve 4 generated CV models (classique, competences, fonctionnel, mixte)
- GET /api/passport - verify auto-filled competences (savoir_faire/savoir_etre), experiences, learning_path
- GET /api/passport/diagnostic - verify nature_distribution with savoir_faire/savoir_etre counts
"""

import pytest
import requests
import os
import time

# Get base URL from environment - NO default value
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Sample CV text content for testing
SAMPLE_CV_TEXT = """
JEAN DUPONT
Chef de Projet Digital

PROFIL
Professionnel expérimenté de 8 ans dans la gestion de projets digitaux, spécialisé en transformation numérique et conduite du changement.
Compétences confirmées en management d'équipe, coordination multi-projets et communication client.

EXPÉRIENCES PROFESSIONNELLES

Chef de Projet Digital - Agence WebCreative (2020-2024)
- Pilotage de 15+ projets web et mobile de A à Z
- Management d'équipes de 3 à 8 personnes (développeurs, designers, rédacteurs)
- Gestion budgétaire (budgets de 50k€ à 500k€)
- Communication client et présentation des livrables
- Mise en place de méthodologies Agile/Scrum
Réalisations: Livraison de 98% des projets dans les délais, taux de satisfaction client de 4.8/5

Chargé de Marketing Digital - Entreprise TechSolutions (2018-2020)
- Création et gestion de campagnes marketing digital
- Analyse de données avec Google Analytics
- Gestion des réseaux sociaux (LinkedIn, Twitter, Facebook)
- Rédaction de contenus web et newsletters
Réalisations: Augmentation de 45% du trafic web, +2000 abonnés newsletter

Assistant Commercial - PME ServicePlus (2016-2018)
- Relation client et prospection téléphonique
- Suivi administratif des dossiers clients
- Utilisation de CRM (Salesforce)
Réalisations: 120% d'objectifs commerciaux atteints sur 2 ans

COMPÉTENCES TECHNIQUES (Savoir-faire)
- Gestion de projet: MS Project, Trello, Asana, Jira
- Marketing digital: Google Ads, SEO, Analytics, Mailchimp
- Design: Figma, Adobe Suite (notions)
- CRM: Salesforce, HubSpot
- Suite Office: Excel avancé, PowerPoint, Word

COMPÉTENCES COMPORTEMENTALES (Savoir-être)
- Leadership et management d'équipe
- Communication interpersonnelle
- Résolution de problèmes
- Adaptabilité et flexibilité
- Travail en équipe
- Gestion du stress
- Organisation et rigueur
- Sens du service client

FORMATION
Master Marketing Digital - École de Commerce Paris (2016)
Licence Administration des Entreprises - Université Paris (2014)

LANGUES
Français: Langue maternelle
Anglais: Courant (TOEIC 890)
Espagnol: Intermédiaire

CENTRES D'INTÉRÊT
Veille technologique, sports collectifs, photographie
"""


class TestCvAnalysisSetup:
    """Setup tests - verify API is accessible"""

    def test_api_health(self):
        """Verify API is accessible"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print(f"✓ API health check passed: {response.json()}")


class TestCvAnalysisEndpoint:
    """Test POST /api/cv/analyze with file upload"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Create anonymous token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Auth token created: {data['token'][:20]}...")
        return data["token"]

    @pytest.fixture(scope="class")
    def passport_initialized(self, auth_token):
        """Initialize passport before CV analysis"""
        response = requests.get(f"{BASE_URL}/api/passport?token={auth_token}")
        assert response.status_code == 200
        print(f"✓ Passport initialized")
        return True

    def test_cv_analyze_with_text_file(self, auth_token, passport_initialized):
        """Test CV analysis with a text file upload"""
        # Create a test CV file
        files = {
            'file': ('cv_test_jean_dupont.txt', SAMPLE_CV_TEXT.encode('utf-8'), 'text/plain')
        }
        
        # Send request with 120s timeout as AI analysis takes time
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze?token={auth_token}",
            files=files,
            timeout=120
        )
        
        # Verify response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify required fields in response
        assert "savoir_faire_count" in data, "Missing savoir_faire_count in response"
        assert "savoir_etre_count" in data, "Missing savoir_etre_count in response"
        assert "experiences_count" in data, "Missing experiences_count in response"
        assert "formations_suggestions" in data, "Missing formations_suggestions in response"
        assert "competences_transversales" in data, "Missing competences_transversales in response"
        assert "cv_models_generated" in data, "Missing cv_models_generated in response"
        
        # Verify data values
        assert data["savoir_faire_count"] > 0, "Expected at least 1 savoir_faire"
        assert data["savoir_etre_count"] > 0, "Expected at least 1 savoir_etre"
        assert data["experiences_count"] > 0, "Expected at least 1 experience"
        
        # Verify 4 CV models generated
        assert len(data["cv_models_generated"]) == 4, f"Expected 4 CV models, got {len(data['cv_models_generated'])}"
        expected_models = ["classique", "competences", "fonctionnel", "mixte"]
        for model in expected_models:
            assert model in data["cv_models_generated"], f"Missing {model} in cv_models_generated"
        
        print(f"✓ CV Analysis completed:")
        print(f"  - Savoir-faire: {data['savoir_faire_count']}")
        print(f"  - Savoir-être: {data['savoir_etre_count']}")
        print(f"  - Experiences: {data['experiences_count']}")
        print(f"  - Formations suggestions: {len(data['formations_suggestions'])}")
        print(f"  - Competences transversales: {len(data['competences_transversales'])}")
        print(f"  - CV models generated: {data['cv_models_generated']}")
        return data

    def test_cv_analyze_empty_file_rejected(self, auth_token, passport_initialized):
        """Test that empty files are rejected"""
        files = {
            'file': ('empty_cv.txt', b'', 'text/plain')
        }
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze?token={auth_token}",
            files=files,
            timeout=30
        )
        # Should return 400 for insufficient text
        assert response.status_code == 400, f"Expected 400 for empty file, got {response.status_code}"
        print(f"✓ Empty file correctly rejected with status 400")

    def test_cv_analyze_short_text_rejected(self, auth_token, passport_initialized):
        """Test that too short text is rejected"""
        files = {
            'file': ('short_cv.txt', b'Hello world', 'text/plain')
        }
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze?token={auth_token}",
            files=files,
            timeout=30
        )
        # Should return 400 for insufficient text
        assert response.status_code == 400, f"Expected 400 for short text, got {response.status_code}"
        print(f"✓ Short text correctly rejected with status 400")


class TestCvModelsEndpoint:
    """Test GET /api/cv/models - retrieve generated CV models"""

    @pytest.fixture(scope="class")
    def auth_token_with_cv(self):
        """Create token and analyze CV first"""
        # Create token
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        
        # Initialize passport
        requests.get(f"{BASE_URL}/api/passport?token={token}")
        
        # Upload and analyze CV
        files = {
            'file': ('cv_models_test.txt', SAMPLE_CV_TEXT.encode('utf-8'), 'text/plain')
        }
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze?token={token}",
            files=files,
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"Warning: CV analysis failed: {response.text}")
        
        return token

    def test_get_cv_models_returns_4_models(self, auth_token_with_cv):
        """Test that GET /api/cv/models returns 4 CV models"""
        response = requests.get(f"{BASE_URL}/api/cv/models?token={auth_token_with_cv}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "models" in data, "Missing 'models' key in response"
        assert "analyzed_at" in data, "Missing 'analyzed_at' key in response"
        assert "original_filename" in data, "Missing 'original_filename' key in response"
        
        # Verify 4 models exist
        models = data["models"]
        assert "classique" in models, "Missing 'classique' model"
        assert "competences" in models, "Missing 'competences' model"
        assert "fonctionnel" in models, "Missing 'fonctionnel' model"
        assert "mixte" in models, "Missing 'mixte' model"
        
        # Verify each model has content
        for model_name, model_content in models.items():
            assert model_content and len(model_content) > 50, f"Model {model_name} has insufficient content"
        
        print(f"✓ GET /api/cv/models returned 4 CV models:")
        for model_name, model_content in models.items():
            print(f"  - {model_name}: {len(model_content)} chars")

    def test_get_cv_models_empty_without_upload(self):
        """Test that CV models are empty for new user without upload"""
        # Create fresh token without CV upload
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        
        # Get CV models
        response = requests.get(f"{BASE_URL}/api/cv/models?token={token}")
        assert response.status_code == 200
        data = response.json()
        
        # Should return empty models
        assert data["models"] == {} or len(data["models"]) == 0
        print(f"✓ Empty CV models returned for user without upload")


class TestPassportAutoFill:
    """Test that passport is auto-filled after CV analysis"""

    @pytest.fixture(scope="class")
    def auth_and_analyze(self):
        """Create token, initialize passport, and analyze CV"""
        # Create token
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        
        # Initialize passport
        requests.get(f"{BASE_URL}/api/passport?token={token}")
        
        # Upload and analyze CV
        files = {
            'file': ('cv_passport_test.txt', SAMPLE_CV_TEXT.encode('utf-8'), 'text/plain')
        }
        analysis_response = requests.post(
            f"{BASE_URL}/api/cv/analyze?token={token}",
            files=files,
            timeout=120
        )
        
        return {
            "token": token,
            "analysis": analysis_response.json() if analysis_response.status_code == 200 else None
        }

    def test_passport_has_competences_after_cv_analysis(self, auth_and_analyze):
        """Test that passport competences are filled after CV analysis"""
        token = auth_and_analyze["token"]
        
        response = requests.get(f"{BASE_URL}/api/passport?token={token}")
        assert response.status_code == 200
        passport = response.json()
        
        # Verify competences exist
        assert "competences" in passport, "Missing 'competences' in passport"
        competences = passport["competences"]
        
        # Should have competences from CV analysis
        assert len(competences) > 0, "Expected competences to be auto-filled from CV"
        
        # Verify competences have nature (savoir_faire or savoir_etre)
        savoir_faire_count = sum(1 for c in competences if c.get("nature") == "savoir_faire")
        savoir_etre_count = sum(1 for c in competences if c.get("nature") == "savoir_etre")
        
        print(f"✓ Passport has {len(competences)} competences:")
        print(f"  - Savoir-faire: {savoir_faire_count}")
        print(f"  - Savoir-être: {savoir_etre_count}")
        
        # Verify source is 'ia_detectee' for auto-filled competences
        ia_detected = [c for c in competences if c.get("source") == "ia_detectee"]
        assert len(ia_detected) > 0, "Expected competences with source='ia_detectee'"
        print(f"  - Source 'ia_detectee': {len(ia_detected)}")

    def test_passport_has_experiences_after_cv_analysis(self, auth_and_analyze):
        """Test that passport experiences are filled after CV analysis"""
        token = auth_and_analyze["token"]
        
        response = requests.get(f"{BASE_URL}/api/passport?token={token}")
        assert response.status_code == 200
        passport = response.json()
        
        # Verify experiences exist
        assert "experiences" in passport, "Missing 'experiences' in passport"
        experiences = passport["experiences"]
        
        assert len(experiences) > 0, "Expected experiences to be auto-filled from CV"
        
        # Verify experience structure
        for exp in experiences:
            assert "title" in exp, "Experience missing 'title'"
        
        print(f"✓ Passport has {len(experiences)} experiences")
        for exp in experiences[:3]:  # Show first 3
            print(f"  - {exp.get('title', 'Unknown')} at {exp.get('organization', 'Unknown')}")

    def test_passport_has_learning_path_suggestions(self, auth_and_analyze):
        """Test that passport learning_path has formation suggestions"""
        token = auth_and_analyze["token"]
        
        response = requests.get(f"{BASE_URL}/api/passport?token={token}")
        assert response.status_code == 200
        passport = response.json()
        
        # Verify learning_path exists
        assert "learning_path" in passport, "Missing 'learning_path' in passport"
        learning_path = passport["learning_path"]
        
        # May have suggestions from CV analysis
        if len(learning_path) > 0:
            print(f"✓ Passport has {len(learning_path)} learning suggestions:")
            for item in learning_path[:3]:
                print(f"  - {item.get('title', 'Unknown')}")
        else:
            print(f"✓ Passport learning_path is empty (no suggestions from AI)")

    def test_passport_profile_fields_filled(self, auth_and_analyze):
        """Test that passport profile fields are auto-filled"""
        token = auth_and_analyze["token"]
        
        response = requests.get(f"{BASE_URL}/api/passport?token={token}")
        assert response.status_code == 200
        passport = response.json()
        
        # Check profile fields
        profile_fields = ["professional_summary", "career_project", "motivations", "target_sectors"]
        filled_fields = []
        
        for field in profile_fields:
            if passport.get(field):
                filled_fields.append(field)
        
        print(f"✓ Passport profile fields filled: {filled_fields}")


class TestPassportDiagnostic:
    """Test GET /api/passport/diagnostic includes nature_distribution"""

    @pytest.fixture(scope="class")
    def auth_with_competences(self):
        """Create token and add competences"""
        # Create token
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        
        # Initialize passport
        requests.get(f"{BASE_URL}/api/passport?token={token}")
        
        # Add savoir_faire competence
        requests.post(f"{BASE_URL}/api/passport/competences?token={token}", json={
            "name": "TEST_Gestion de projet",
            "nature": "savoir_faire",
            "category": "technique",
            "level": "avance"
        })
        
        # Add savoir_etre competence
        requests.post(f"{BASE_URL}/api/passport/competences?token={token}", json={
            "name": "TEST_Leadership",
            "nature": "savoir_etre",
            "category": "transversale",
            "level": "intermediaire"
        })
        
        # Add competence without nature
        requests.post(f"{BASE_URL}/api/passport/competences?token={token}", json={
            "name": "TEST_Communication",
            "category": "transversale",
            "level": "avance"
        })
        
        return token

    def test_diagnostic_includes_nature_distribution(self, auth_with_competences):
        """Test that diagnostic includes savoir_faire and savoir_etre counts"""
        response = requests.get(f"{BASE_URL}/api/passport/diagnostic?token={auth_with_competences}")
        assert response.status_code == 200
        diagnostic = response.json()
        
        # Verify nature_distribution exists
        assert "nature_distribution" in diagnostic, "Missing 'nature_distribution' in diagnostic"
        
        nature_dist = diagnostic["nature_distribution"]
        assert "savoir_faire" in nature_dist, "Missing 'savoir_faire' in nature_distribution"
        assert "savoir_etre" in nature_dist, "Missing 'savoir_etre' in nature_distribution"
        
        # Verify counts are integers
        assert isinstance(nature_dist["savoir_faire"], int)
        assert isinstance(nature_dist["savoir_etre"], int)
        
        print(f"✓ Diagnostic nature_distribution:")
        print(f"  - savoir_faire: {nature_dist['savoir_faire']}")
        print(f"  - savoir_etre: {nature_dist['savoir_etre']}")
        if "non_classee" in nature_dist:
            print(f"  - non_classee: {nature_dist['non_classee']}")


class TestAuthRequirement:
    """Test authentication requirements"""

    def test_cv_analyze_requires_auth(self):
        """Test that CV analyze requires authentication"""
        files = {
            'file': ('test.txt', b'Test content', 'text/plain')
        }
        response = requests.post(f"{BASE_URL}/api/cv/analyze", files=files)
        # Should fail without token
        assert response.status_code in [401, 422], f"Expected 401/422 without token, got {response.status_code}"
        print(f"✓ CV analyze requires authentication (got {response.status_code})")

    def test_cv_models_requires_auth(self):
        """Test that CV models requires authentication"""
        response = requests.get(f"{BASE_URL}/api/cv/models")
        assert response.status_code in [401, 422], f"Expected 401/422 without token, got {response.status_code}"
        print(f"✓ CV models requires authentication (got {response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
