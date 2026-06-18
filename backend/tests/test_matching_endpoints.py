"""
Test suite for Matching Candidat / Offre endpoints
- POST /api/matching/analyze-offer-url - Analyze offer from France Travail URL
- POST /api/matching/analyze-offer - Analyze offer from pasted text
- POST /api/matching/match-profile - Match user profile with analyzed offer
- GET /api/matching/history - Get user's analysis history
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_PSEUDO = "mike7"
TEST_PASSWORD = "Solerys777!"

# France Travail test URL
FT_TEST_URL = "https://candidat.francetravail.fr/offres/recherche/detail/209YQWY"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for test user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "pseudo": TEST_PSEUDO,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "token" in data, "No token in login response"
    return data["token"]


class TestMatchingHistory:
    """Test GET /api/matching/history endpoint"""
    
    def test_history_returns_200(self, auth_token):
        """History endpoint returns 200 with valid token"""
        response = requests.get(f"{BASE_URL}/api/matching/history?token={auth_token}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_history_returns_analyses_list(self, auth_token):
        """History endpoint returns analyses array"""
        response = requests.get(f"{BASE_URL}/api/matching/history?token={auth_token}")
        assert response.status_code == 200
        data = response.json()
        assert "analyses" in data, "Response should contain 'analyses' key"
        assert isinstance(data["analyses"], list), "analyses should be a list"
    
    def test_history_requires_auth(self):
        """History endpoint returns 401 for invalid token"""
        response = requests.get(f"{BASE_URL}/api/matching/history?token=invalid_token_123")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestAnalyzeOfferUrl:
    """Test POST /api/matching/analyze-offer-url endpoint"""
    
    def test_analyze_url_returns_200(self, auth_token):
        """Analyze URL endpoint returns 200 with valid France Travail URL"""
        response = requests.post(
            f"{BASE_URL}/api/matching/analyze-offer-url?token={auth_token}",
            json={"url": FT_TEST_URL},
            timeout=60  # LLM calls can take 15-25 seconds
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_analyze_url_returns_analysis_structure(self, auth_token):
        """Analyze URL returns proper analysis structure"""
        response = requests.post(
            f"{BASE_URL}/api/matching/analyze-offer-url?token={auth_token}",
            json={"url": FT_TEST_URL},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "analysis_id" in data, "Response should contain analysis_id"
        assert "analyse" in data, "Response should contain analyse object"
        
        analyse = data["analyse"]
        assert "titre_poste" in analyse, "analyse should contain titre_poste"
        assert "entreprise" in analyse, "analyse should contain entreprise"
        assert "localisation" in analyse, "analyse should contain localisation"
        assert "missions" in analyse, "analyse should contain missions"
        assert "competences_requises" in analyse, "analyse should contain competences_requises"
        
        # Check synthesis fields
        assert "score_qualite_offre" in data, "Response should contain score_qualite_offre"
        assert isinstance(data["score_qualite_offre"], (int, float)), "score_qualite_offre should be numeric"
    
    def test_analyze_url_rejects_invalid_url(self, auth_token):
        """Analyze URL rejects invalid URLs"""
        response = requests.post(
            f"{BASE_URL}/api/matching/analyze-offer-url?token={auth_token}",
            json={"url": "not-a-valid-url"},
            timeout=30
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    def test_analyze_url_requires_auth(self):
        """Analyze URL endpoint returns 401 for invalid token"""
        response = requests.post(
            f"{BASE_URL}/api/matching/analyze-offer-url?token=invalid_token",
            json={"url": FT_TEST_URL},
            timeout=30
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestAnalyzeOfferText:
    """Test POST /api/matching/analyze-offer endpoint"""
    
    SAMPLE_OFFER_TEXT = """
    Titre: Agent d'entretien des locaux
    Entreprise: SARL Nettoyage Pro
    Lieu: Paris 75001
    Type de contrat: CDI
    
    Description du poste:
    Nous recherchons un agent d'entretien pour assurer le nettoyage de bureaux.
    
    Missions:
    - Nettoyage des sols et surfaces
    - Entretien des sanitaires
    - Gestion des déchets
    - Respect des protocoles d'hygiène
    
    Profil recherché:
    - Expérience souhaitée de 1 an minimum
    - Autonomie et rigueur
    - Sens du service
    
    Salaire: 1800€ brut mensuel
    """
    
    def test_analyze_text_returns_200(self, auth_token):
        """Analyze text endpoint returns 200 with valid text"""
        response = requests.post(
            f"{BASE_URL}/api/matching/analyze-offer?token={auth_token}",
            json={"text": self.SAMPLE_OFFER_TEXT, "source": "paste"},
            timeout=60
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_analyze_text_returns_analysis_structure(self, auth_token):
        """Analyze text returns proper analysis structure"""
        response = requests.post(
            f"{BASE_URL}/api/matching/analyze-offer?token={auth_token}",
            json={"text": self.SAMPLE_OFFER_TEXT, "source": "paste"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "analysis_id" in data, "Response should contain analysis_id"
        assert "analyse" in data, "Response should contain analyse object"
        
        analyse = data["analyse"]
        assert "titre_poste" in analyse, "analyse should contain titre_poste"
        assert "competences_requises" in analyse, "analyse should contain competences_requises"
        assert isinstance(analyse["competences_requises"], list), "competences_requises should be a list"
    
    def test_analyze_text_rejects_short_text(self, auth_token):
        """Analyze text rejects text shorter than 30 characters"""
        response = requests.post(
            f"{BASE_URL}/api/matching/analyze-offer?token={auth_token}",
            json={"text": "Too short", "source": "paste"},
            timeout=30
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    def test_analyze_text_requires_auth(self):
        """Analyze text endpoint returns 401 for invalid token"""
        response = requests.post(
            f"{BASE_URL}/api/matching/analyze-offer?token=invalid_token",
            json={"text": self.SAMPLE_OFFER_TEXT},
            timeout=30
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestMatchProfile:
    """Test POST /api/matching/match-profile endpoint"""
    
    @pytest.fixture(scope="class")
    def analysis_id(self, auth_token):
        """Create an analysis to use for matching tests"""
        sample_text = """
        Poste: Développeur Python
        Entreprise: Tech Corp
        Lieu: Lyon
        Contrat: CDI
        
        Missions:
        - Développement d'applications web
        - Maintenance du code existant
        - Tests unitaires
        
        Compétences requises:
        - Python, Django, FastAPI
        - SQL, MongoDB
        - Git
        
        Expérience: 2 ans minimum
        """
        response = requests.post(
            f"{BASE_URL}/api/matching/analyze-offer?token={auth_token}",
            json={"text": sample_text, "source": "test"},
            timeout=60
        )
        assert response.status_code == 200, f"Failed to create analysis: {response.text}"
        return response.json()["analysis_id"]
    
    def test_match_profile_returns_200(self, auth_token, analysis_id):
        """Match profile endpoint returns 200 with valid analysis_id"""
        response = requests.post(
            f"{BASE_URL}/api/matching/match-profile?token={auth_token}",
            json={"analysis_id": analysis_id},
            timeout=60  # LLM calls can take 10-15 seconds
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_match_profile_returns_matching_structure(self, auth_token, analysis_id):
        """Match profile returns proper matching result structure"""
        response = requests.post(
            f"{BASE_URL}/api/matching/match-profile?token={auth_token}",
            json={"analysis_id": analysis_id},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "score_global" in data, "Response should contain score_global"
        assert isinstance(data["score_global"], (int, float)), "score_global should be numeric"
        assert 0 <= data["score_global"] <= 100, "score_global should be between 0 and 100"
        
        assert "verdict" in data, "Response should contain verdict"
        assert isinstance(data["verdict"], str), "verdict should be a string"
        
        assert "details" in data, "Response should contain details"
        details = data["details"]
        assert "competences_techniques" in details, "details should contain competences_techniques"
        assert "soft_skills" in details, "details should contain soft_skills"
        assert "experience" in details, "details should contain experience"
        assert "formation" in details, "details should contain formation"
        
        assert "recommandations" in data, "Response should contain recommandations"
        assert isinstance(data["recommandations"], list), "recommandations should be a list"
        
        assert "message_accroche" in data, "Response should contain message_accroche"
    
    def test_match_profile_rejects_missing_analysis_id(self, auth_token):
        """Match profile rejects request without analysis_id"""
        response = requests.post(
            f"{BASE_URL}/api/matching/match-profile?token={auth_token}",
            json={},
            timeout=30
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    def test_match_profile_rejects_invalid_analysis_id(self, auth_token):
        """Match profile returns 404 for non-existent analysis_id"""
        response = requests.post(
            f"{BASE_URL}/api/matching/match-profile?token={auth_token}",
            json={"analysis_id": "non-existent-id-12345"},
            timeout=30
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_match_profile_requires_auth(self):
        """Match profile endpoint returns 401 for invalid token"""
        response = requests.post(
            f"{BASE_URL}/api/matching/match-profile?token=invalid_token",
            json={"analysis_id": "some-id"},
            timeout=30
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestEndToEndFlow:
    """Test complete flow: analyze URL -> match profile -> check history"""
    
    def test_complete_flow(self, auth_token):
        """Test complete analysis and matching flow"""
        # Step 1: Analyze France Travail URL
        print("Step 1: Analyzing France Travail URL...")
        analyze_response = requests.post(
            f"{BASE_URL}/api/matching/analyze-offer-url?token={auth_token}",
            json={"url": FT_TEST_URL},
            timeout=60
        )
        assert analyze_response.status_code == 200, f"Analyze failed: {analyze_response.text}"
        
        analysis_data = analyze_response.json()
        analysis_id = analysis_data["analysis_id"]
        print(f"  - Analysis ID: {analysis_id}")
        print(f"  - Titre: {analysis_data['analyse'].get('titre_poste', 'N/A')}")
        print(f"  - Score qualité: {analysis_data.get('score_qualite_offre', 'N/A')}")
        
        # Step 2: Match profile with analyzed offer
        print("\nStep 2: Matching profile with offer...")
        match_response = requests.post(
            f"{BASE_URL}/api/matching/match-profile?token={auth_token}",
            json={"analysis_id": analysis_id},
            timeout=60
        )
        assert match_response.status_code == 200, f"Match failed: {match_response.text}"
        
        match_data = match_response.json()
        print(f"  - Score global: {match_data.get('score_global', 'N/A')}%")
        print(f"  - Verdict: {match_data.get('verdict', 'N/A')}")
        
        # Step 3: Verify analysis appears in history
        print("\nStep 3: Checking history...")
        history_response = requests.get(f"{BASE_URL}/api/matching/history?token={auth_token}")
        assert history_response.status_code == 200, f"History failed: {history_response.text}"
        
        history_data = history_response.json()
        analyses = history_data.get("analyses", [])
        print(f"  - Total analyses in history: {len(analyses)}")
        
        # Verify our analysis is in history
        found = any(a.get("id") == analysis_id for a in analyses)
        assert found, f"Analysis {analysis_id} not found in history"
        print(f"  - Analysis {analysis_id} found in history ✓")
        
        print("\n✅ Complete flow test passed!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
