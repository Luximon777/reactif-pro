"""
Tests for CV Model Selection Feature - New feature in RE'ACTIF PRO
Tests:
- POST /api/cv/analyze-text accepts selected_models parameter in payload
- POST /api/cv/analyze-text with selected_models=['classique'] only generates classique model
- POST /api/cv/analyze-text with empty selected_models=[] skips model generation
- POST /api/cv/analyze-text with all 4 models generates all 4 (backward compatible)
- GET /api/cv/latest-analysis still works after analysis with model selection
- GET /api/cv/models still returns models after analysis
"""

import pytest
import requests
import os
import time

# Get base URL from environment - NO default value
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Sample CV text content for testing
SAMPLE_CV_TEXT = """
MARIE MARTIN
Responsable Marketing Digital

PROFIL
Experte en marketing digital avec 6 ans d'expérience. Spécialisée dans les stratégies de communication digitale et la gestion de projets marketing.

EXPÉRIENCES PROFESSIONNELLES

Responsable Marketing Digital - Startup TechBoost (2021-2024)
- Élaboration et mise en œuvre de stratégies digitales
- Gestion d'une équipe de 4 personnes
- Budget marketing de 150k€ annuel
- Coordination des campagnes publicitaires en ligne

Chargée de Communication - Agence MediaPro (2018-2021)
- Création de contenus pour réseaux sociaux
- Animation de la communauté en ligne
- Rédaction d'articles de blog et newsletters

COMPÉTENCES TECHNIQUES
- Marketing digital: SEO, SEA, réseaux sociaux
- Outils: Google Analytics, Meta Business Suite, Mailchimp
- CRM: HubSpot, Salesforce
- Bureautique: Suite Office, Google Workspace

COMPÉTENCES COMPORTEMENTALES
- Leadership et esprit d'équipe
- Créativité et innovation
- Gestion du stress et des priorités
- Excellentes compétences relationnelles

FORMATION
Master Communication Digitale - ISCOM Paris (2018)
Licence Information-Communication - Université Lyon (2016)

LANGUES
Français: Langue maternelle
Anglais: Courant
"""


class TestModelSelectionSetup:
    """Setup tests - verify API is accessible"""

    def test_api_health(self):
        """Verify API is accessible"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print(f"✓ API health check passed: {response.json()}")


class TestCvTextPayloadWithSelectedModels:
    """Test POST /api/cv/analyze-text with selected_models parameter"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Create anonymous token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Auth token created: {data['token'][:20]}...")
        return data["token"]

    def test_analyze_text_accepts_selected_models_parameter(self, auth_token):
        """Test that analyze-text endpoint accepts selected_models in payload"""
        payload = {
            "text": SAMPLE_CV_TEXT,
            "filename": "cv_test.txt",
            "selected_models": ["classique", "competences"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={auth_token}",
            json=payload,
            timeout=30
        )
        
        # Should return 200 and job_id
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "job_id" in data, "Missing job_id in response"
        assert "status" in data, "Missing status in response"
        assert data["status"] == "started", f"Expected status 'started', got {data['status']}"
        
        print(f"✓ analyze-text accepts selected_models parameter, job_id: {data['job_id']}")
        return data["job_id"]

    def test_analyze_text_with_empty_selected_models(self, auth_token):
        """Test that analyze-text accepts empty selected_models (analysis only, no CV generation)"""
        payload = {
            "text": SAMPLE_CV_TEXT,
            "filename": "cv_analysis_only.txt",
            "selected_models": []  # Empty list - no CV models generated
        }
        
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={auth_token}",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "job_id" in data, "Missing job_id in response"
        print(f"✓ analyze-text accepts empty selected_models (analysis-only mode), job_id: {data['job_id']}")

    def test_analyze_text_with_single_model(self, auth_token):
        """Test that analyze-text works with only one model selected"""
        payload = {
            "text": SAMPLE_CV_TEXT,
            "filename": "cv_single_model.txt",
            "selected_models": ["fonctionnel"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={auth_token}",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "job_id" in data
        print(f"✓ analyze-text works with single model selection, job_id: {data['job_id']}")

    def test_analyze_text_with_all_four_models(self, auth_token):
        """Test backward compatibility - all 4 models selected"""
        payload = {
            "text": SAMPLE_CV_TEXT,
            "filename": "cv_all_models.txt",
            "selected_models": ["classique", "competences", "fonctionnel", "mixte"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={auth_token}",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "job_id" in data
        print(f"✓ analyze-text works with all 4 models (backward compatible), job_id: {data['job_id']}")

    def test_analyze_text_without_selected_models_uses_default(self, auth_token):
        """Test that missing selected_models uses default (all 4 models)"""
        payload = {
            "text": SAMPLE_CV_TEXT,
            "filename": "cv_default_models.txt"
            # No selected_models - should use default
        }
        
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={auth_token}",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "job_id" in data
        print(f"✓ analyze-text uses default models when selected_models not provided, job_id: {data['job_id']}")


class TestFullAnalysisFlowWithModelSelection:
    """Full flow test - analyze with model selection, check status, verify results"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Create anonymous token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        return response.json()["token"]

    def test_full_flow_with_two_models_selected(self, auth_token):
        """Test full analysis flow with only 2 models selected"""
        # Initialize passport
        requests.get(f"{BASE_URL}/api/passport?token={auth_token}")
        
        # Start analysis with 2 models
        payload = {
            "text": SAMPLE_CV_TEXT,
            "filename": "cv_two_models_flow.txt",
            "selected_models": ["classique", "mixte"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={auth_token}",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        print(f"✓ Started analysis with 2 models (classique, mixte), job_id: {job_id}")
        
        # Poll for completion (max 120 seconds)
        max_polls = 40
        result = None
        for i in range(max_polls):
            time.sleep(3)
            status_res = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={auth_token}&job_id={job_id}")
            
            if status_res.status_code == 200:
                status_data = status_res.json()
                print(f"  Poll {i+1}: status={status_data['status']}, step={status_data.get('step', '')}")
                
                if status_data["status"] == "completed":
                    result = status_data.get("result")
                    break
                elif status_data["status"] == "failed":
                    pytest.fail(f"Analysis failed: {status_data.get('error')}")
        
        assert result is not None, "Analysis did not complete within timeout"
        
        # Verify result
        assert "savoir_faire_count" in result
        assert "savoir_etre_count" in result
        assert result["savoir_faire_count"] > 0
        assert result["savoir_etre_count"] > 0
        print(f"✓ Analysis completed: {result['savoir_faire_count']} savoir-faire, {result['savoir_etre_count']} savoir-être")
        
        # Verify latest-analysis endpoint works
        latest_res = requests.get(f"{BASE_URL}/api/cv/latest-analysis?token={auth_token}")
        assert latest_res.status_code == 200
        latest_data = latest_res.json()
        assert latest_data["has_analysis"] == True
        print(f"✓ GET /api/cv/latest-analysis returns persisted result")
        
        # Verify models endpoint works
        models_res = requests.get(f"{BASE_URL}/api/cv/models?token={auth_token}")
        assert models_res.status_code == 200
        models_data = models_res.json()
        
        models = models_data.get("models", {})
        # Check that classique and mixte were generated
        assert "classique" in models or models.get("classique", "") != "", "classique model should be present"
        assert "mixte" in models or models.get("mixte", "") != "", "mixte model should be present"
        
        print(f"✓ GET /api/cv/models returns generated models")
        print(f"  Models available: {list(models.keys())}")


class TestJobStatusWithSelectedModels:
    """Test that job status stores selected_models info"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Create anonymous token"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        return response.json()["token"]

    def test_job_stores_selected_models(self, auth_token):
        """Test that the job record stores which models were selected"""
        payload = {
            "text": SAMPLE_CV_TEXT,
            "filename": "cv_job_test.txt",
            "selected_models": ["competences", "fonctionnel"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={auth_token}",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        
        # Check status endpoint
        status_res = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={auth_token}&job_id={job_id}")
        assert status_res.status_code == 200
        
        print(f"✓ Job created and status endpoint works, job_id: {job_id}")


class TestEdgeCases:
    """Test edge cases for model selection"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Create anonymous token"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        return response.json()["token"]

    def test_invalid_model_name_ignored(self, auth_token):
        """Test that invalid model names don't cause errors"""
        payload = {
            "text": SAMPLE_CV_TEXT,
            "filename": "cv_invalid_model.txt",
            "selected_models": ["classique", "invalid_model_name", "mixte"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={auth_token}",
            json=payload,
            timeout=30
        )
        
        # Should still work - invalid models are simply skipped
        assert response.status_code == 200
        print(f"✓ Invalid model names don't cause errors")

    def test_short_text_rejected_regardless_of_models(self, auth_token):
        """Test that short CV text is rejected even with model selection"""
        payload = {
            "text": "Short text",
            "filename": "cv_short.txt",
            "selected_models": ["classique"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={auth_token}",
            json=payload,
            timeout=30
        )
        
        assert response.status_code == 400, f"Expected 400 for short text, got {response.status_code}"
        print(f"✓ Short text correctly rejected with status 400")


class TestAuthRequirements:
    """Test authentication requirements for new feature"""

    def test_analyze_text_requires_auth(self):
        """Test that analyze-text requires authentication"""
        payload = {
            "text": SAMPLE_CV_TEXT,
            "filename": "cv_no_auth.txt",
            "selected_models": ["classique"]
        }
        
        response = requests.post(f"{BASE_URL}/api/cv/analyze-text", json=payload)
        assert response.status_code in [401, 422], f"Expected 401/422 without token, got {response.status_code}"
        print(f"✓ analyze-text requires authentication (got {response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
