"""
Quick tests for CV endpoints in Re'Actif Pro
Tests: analyze-text, analyze/status, generate-models, generate-models/status, download, download-pdf, models
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

SAMPLE_CV_TEXT = """Jean DUPONT - Développeur Full Stack
Email: jean.dupont@email.com | Tel: 06 12 34 56 78

EXPÉRIENCES
Développeur Full Stack Senior - TechCorp (2020-2024)
- Développement d'applications web
- Architecture microservices

COMPÉTENCES
Frontend: React, TypeScript
Backend: Python, FastAPI
"""


class TestCVEndpoints:
    """Quick tests for CV API endpoints"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Create anonymous token"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200, f"Auth failed: {response.text}"
        token = response.json()["token"]
        # Initialize passport
        requests.get(f"{BASE_URL}/api/passport?token={token}")
        return token

    def test_analyze_text_starts_job(self, auth_token):
        """POST /api/cv/analyze-text returns job_id"""
        payload = {"text": SAMPLE_CV_TEXT, "filename": "test_cv.txt"}
        response = requests.post(f"{BASE_URL}/api/cv/analyze-text?token={auth_token}", json=payload, timeout=15)
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "started"
        print(f"✓ analyze-text returns job_id: {data['job_id']}")

    def test_analyze_status_endpoint(self, auth_token):
        """GET /api/cv/analyze/status returns job status"""
        # Start analysis
        payload = {"text": SAMPLE_CV_TEXT, "filename": "status_test.txt"}
        response = requests.post(f"{BASE_URL}/api/cv/analyze-text?token={auth_token}", json=payload)
        job_id = response.json()["job_id"]
        
        # Poll status
        time.sleep(3)
        status_res = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={auth_token}&job_id={job_id}")
        
        assert status_res.status_code == 200
        data = status_res.json()
        assert "status" in data
        assert data["status"] in ["started", "analyzing", "completed", "failed"]
        print(f"✓ analyze/status returns status: {data['status']}")

    def test_generate_models_requires_cv_text(self, auth_token):
        """POST /api/cv/generate-models returns 404 without CV text"""
        # Create new token without CV
        new_token = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"}).json()["token"]
        
        response = requests.post(
            f"{BASE_URL}/api/cv/generate-models?token={new_token}",
            json={"model_types": ["classique"]},
            timeout=10
        )
        
        assert response.status_code == 404
        print("✓ generate-models returns 404 when no CV analyzed")

    def test_generate_models_rejects_invalid_types(self, auth_token):
        """POST /api/cv/generate-models rejects invalid model types"""
        response = requests.post(
            f"{BASE_URL}/api/cv/generate-models?token={auth_token}",
            json={"model_types": ["invalid_model"]},
            timeout=10
        )
        
        assert response.status_code == 400
        print("✓ generate-models rejects invalid model types")

    def test_generate_models_rejects_empty_list(self, auth_token):
        """POST /api/cv/generate-models rejects empty list"""
        response = requests.post(
            f"{BASE_URL}/api/cv/generate-models?token={auth_token}",
            json={"model_types": []},
            timeout=10
        )
        
        assert response.status_code == 400
        print("✓ generate-models rejects empty model_types list")

    def test_cv_models_endpoint(self, auth_token):
        """GET /api/cv/models returns models data"""
        response = requests.get(f"{BASE_URL}/api/cv/models?token={auth_token}")
        
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        print(f"✓ cv/models returns models: {list(data.get('models', {}).keys())}")

    def test_latest_analysis_endpoint(self, auth_token):
        """GET /api/cv/latest-analysis returns analysis data"""
        response = requests.get(f"{BASE_URL}/api/cv/latest-analysis?token={auth_token}")
        
        assert response.status_code == 200
        data = response.json()
        assert "has_analysis" in data
        print(f"✓ latest-analysis returns has_analysis: {data['has_analysis']}")


class TestDownloadEndpoints:
    """Test download endpoints with existing generated models"""

    @pytest.fixture(scope="class")
    def token_with_models(self):
        """Get token from previous test that has generated models"""
        # Use a fresh token and generate a model
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        requests.get(f"{BASE_URL}/api/passport?token={token}")
        
        # Analyze CV
        payload = {"text": SAMPLE_CV_TEXT, "filename": "download_test.txt"}
        response = requests.post(f"{BASE_URL}/api/cv/analyze-text?token={token}", json=payload)
        job_id = response.json()["job_id"]
        
        # Wait for analysis
        for _ in range(30):
            time.sleep(3)
            status = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={job_id}")
            if status.status_code == 200 and status.json()["status"] in ["completed", "failed"]:
                break
        
        return token

    def test_download_docx_without_generation(self, token_with_models):
        """GET /api/cv/download returns 404 if model not generated"""
        response = requests.get(f"{BASE_URL}/api/cv/download/fonctionnel?token={token_with_models}")
        
        # Should be 404 since we didn't generate fonctionnel
        assert response.status_code == 404
        print("✓ download returns 404 for non-generated model")

    def test_download_pdf_without_generation(self, token_with_models):
        """GET /api/cv/download-pdf returns 404 if model not generated"""
        response = requests.get(f"{BASE_URL}/api/cv/download-pdf/mixte?token={token_with_models}")
        
        # Should be 404 since we didn't generate mixte
        assert response.status_code == 404
        print("✓ download-pdf returns 404 for non-generated model")

    def test_invalid_model_type_download(self, token_with_models):
        """GET /api/cv/download returns 400 for invalid model type"""
        response = requests.get(f"{BASE_URL}/api/cv/download/invalid_model?token={token_with_models}")
        
        assert response.status_code == 400
        print("✓ download returns 400 for invalid model type")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
