"""
Test CV 3-Step Flow: Upload -> Analyze (10 rules audit) -> Optimize (3 models)
Tests the complete CV analysis and optimization workflow with:
- 10 audit rules with score/statut/diagnostic/recommandation
- 3 model types: classique, competences, transversale
- DOCX and PDF downloads
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test token with existing analysis data
TEST_TOKEN = "BzCnm4CfG4cm6aixgdgcrwcjM-tIpnl99ycJWySXOGs"

# Sample CV text for testing new analysis
SAMPLE_CV_TEXT = """Jean DUPONT
Developpeur Full Stack Senior
Email: jean.dupont@email.com
Tel: 06 12 34 56 78
Paris

Developpeur Full Stack avec 8 ans d'experience. Expert React, Node.js, Python.

EXPERIENCES

Developpeur Full Stack Senior - TechCorp Paris - 2020-2024
- Conception plateforme SaaS avec 50000 utilisateurs
- Migration microservices
- CI/CD couverture 85%

Developpeur Backend - StartupWeb Lyon - 2017-2020
- APIs REST et GraphQL
- Optimisation BDD

FORMATION
Master Informatique - Universite Bordeaux - 2016

COMPETENCES
React, TypeScript, Node.js, Python, Django, FastAPI, Docker, Kubernetes, AWS

LANGUES
Francais natif, Anglais courant
"""


class TestExistingAnalysis:
    """Tests using existing token with analysis data (no LLM calls)"""
    
    def test_latest_analysis_has_audit_cv(self):
        """Verify latest analysis contains audit_cv with 10 rules"""
        response = requests.get(f"{BASE_URL}/api/cv/latest-analysis?token={TEST_TOKEN}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["has_analysis"] == True
        
        result = data["result"]
        assert "audit_cv" in result
        assert len(result["audit_cv"]) == 10, f"Expected 10 audit rules, got {len(result['audit_cv'])}"
    
    def test_audit_rule_structure(self):
        """Verify each audit rule has required fields"""
        response = requests.get(f"{BASE_URL}/api/cv/latest-analysis?token={TEST_TOKEN}")
        assert response.status_code == 200
        
        result = response.json()["result"]
        required_fields = ["regle", "score", "statut", "diagnostic", "recommandation"]
        valid_statuts = ["ok", "ameliorable", "absent"]
        
        for i, rule in enumerate(result["audit_cv"]):
            for field in required_fields:
                assert field in rule, f"Rule {i} missing field: {field}"
            
            # Validate score is 0-10
            assert 0 <= rule["score"] <= 10, f"Rule {i} score {rule['score']} out of range"
            
            # Validate statut
            assert rule["statut"] in valid_statuts, f"Rule {i} invalid statut: {rule['statut']}"
    
    def test_score_global_cv(self):
        """Verify score_global_cv is 0-100"""
        response = requests.get(f"{BASE_URL}/api/cv/latest-analysis?token={TEST_TOKEN}")
        assert response.status_code == 200
        
        result = response.json()["result"]
        assert "score_global_cv" in result
        assert 0 <= result["score_global_cv"] <= 100
    
    def test_modele_suggere_is_valid(self):
        """Verify modele_suggere is one of classique/competences/transversale"""
        response = requests.get(f"{BASE_URL}/api/cv/latest-analysis?token={TEST_TOKEN}")
        assert response.status_code == 200
        
        result = response.json()["result"]
        assert "modele_suggere" in result
        
        valid_models = ["classique", "competences", "transversale"]
        assert result["modele_suggere"] in valid_models, f"Invalid model: {result['modele_suggere']}"
    
    def test_raison_modele_present(self):
        """Verify raison_modele is present"""
        response = requests.get(f"{BASE_URL}/api/cv/latest-analysis?token={TEST_TOKEN}")
        assert response.status_code == 200
        
        result = response.json()["result"]
        assert "raison_modele" in result
        assert len(result["raison_modele"]) > 0


class TestCvModelsEndpoint:
    """Test CV models CRUD"""
    
    def test_get_cv_models(self):
        """Verify GET /api/cv/models returns generated models"""
        response = requests.get(f"{BASE_URL}/api/cv/models?token={TEST_TOKEN}")
        assert response.status_code == 200
        
        data = response.json()
        assert "models" in data
        
        # Should have classique model
        assert "classique" in data["models"]


class TestDownloadEndpoints:
    """Test DOCX and PDF download"""
    
    def test_download_classique_docx(self):
        """Test DOCX download returns valid file"""
        response = requests.get(f"{BASE_URL}/api/cv/download/classique?token={TEST_TOKEN}")
        assert response.status_code == 200
        
        # Check content type
        assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers.get("Content-Type", "")
        
        # Check content disposition
        assert "CV_Classique.docx" in response.headers.get("Content-Disposition", "")
        
        # Check minimum file size
        assert len(response.content) > 5000, "DOCX file too small"
    
    def test_download_classique_pdf(self):
        """Test PDF download returns valid file"""
        response = requests.get(f"{BASE_URL}/api/cv/download-pdf/classique?token={TEST_TOKEN}")
        assert response.status_code == 200
        
        # Check content type
        assert "application/pdf" in response.headers.get("Content-Type", "")
        
        # Check content disposition
        assert "CV_Classique.pdf" in response.headers.get("Content-Disposition", "")
        
        # Check minimum file size
        assert len(response.content) > 1000, "PDF file too small"
    
    def test_download_invalid_model_type(self):
        """Test download with invalid model type returns 400"""
        response = requests.get(f"{BASE_URL}/api/cv/download/invalid?token={TEST_TOKEN}")
        assert response.status_code == 400
    
    def test_download_nonexistent_model(self):
        """Test download for non-generated model returns 404"""
        # competences might not be generated, so test with transversale
        response = requests.get(f"{BASE_URL}/api/cv/download/transversale?token={TEST_TOKEN}")
        # Can be 200 if generated, 404 if not
        assert response.status_code in [200, 404]


class TestGenerateModelsEndpoint:
    """Test CV generation endpoint structure"""
    
    def test_generate_models_invalid_types(self):
        """Test generate-models with invalid types returns error"""
        response = requests.post(
            f"{BASE_URL}/api/cv/generate-models?token={TEST_TOKEN}",
            json={"model_types": ["invalid", "fonctionnel"]}
        )
        assert response.status_code == 400
        assert "valide" in response.json().get("detail", "").lower()
    
    def test_generate_models_accepts_valid_types(self):
        """Test that valid model types are accepted"""
        # Just test the endpoint accepts valid types - don't actually generate
        response = requests.post(
            f"{BASE_URL}/api/cv/generate-models?token={TEST_TOKEN}",
            json={"model_types": ["classique"]}
        )
        # Should return 200 with job_id
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "started"
        assert "classique" in data["model_types"]


class TestAnalyzeTextEndpoint:
    """Test analyze-text endpoint structure"""
    
    def test_analyze_text_returns_job_id(self):
        """Test POST /api/cv/analyze-text returns job_id"""
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={TEST_TOKEN}",
            json={"text": SAMPLE_CV_TEXT, "filename": "test_cv.txt"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "started"
        assert "message" in data
    
    def test_analyze_text_too_short(self):
        """Test analyze-text with too short text returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={TEST_TOKEN}",
            json={"text": "Short", "filename": "test.txt"}
        )
        assert response.status_code == 400


class TestAnalyzeStatus:
    """Test analyze status endpoint"""
    
    def test_status_invalid_job_id(self):
        """Test status with invalid job_id returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/cv/analyze/status?token={TEST_TOKEN}&job_id=invalid-job-id"
        )
        assert response.status_code == 404


class TestGenerateModelsStatus:
    """Test generate-models status endpoint"""
    
    def test_status_invalid_job_id(self):
        """Test status with invalid job_id returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/cv/generate-models/status?token={TEST_TOKEN}&job_id=invalid-job-id"
        )
        assert response.status_code == 404


class TestThreeModelsOnly:
    """Verify only 3 model types are accepted"""
    
    def test_only_three_valid_models(self):
        """Verify the 3 valid model types"""
        valid_models = ["classique", "competences", "transversale"]
        
        for model in valid_models:
            # Test download endpoint accepts these
            response = requests.get(f"{BASE_URL}/api/cv/download/{model}?token={TEST_TOKEN}")
            assert response.status_code in [200, 404], f"Model {model} should be valid"
        
        # Test invalid models are rejected
        invalid_models = ["fonctionnel", "mixte", "moderne", "creatif"]
        for model in invalid_models:
            response = requests.get(f"{BASE_URL}/api/cv/download/{model}?token={TEST_TOKEN}")
            assert response.status_code == 400, f"Model {model} should be invalid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
