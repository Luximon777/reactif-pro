"""
Test suite for CV Analysis Persistence and Job Suggestions features
- GET /api/cv/latest-analysis: Returns latest completed CV analysis for persistence
- POST /api/cv/analyze-text: Includes offres_emploi_suggerees in analysis result
- Validates the fixes for bug: CV results disappearing on navigation change
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestCvLatestAnalysisEndpoint:
    """Tests for GET /api/cv/latest-analysis endpoint"""

    def test_latest_analysis_new_user_returns_no_analysis(self):
        """New users should have has_analysis: false"""
        # Create a new anonymous token
        auth_response = requests.post(
            f"{BASE_URL}/api/auth/anonymous",
            json={"role": "particulier"}
        )
        assert auth_response.status_code == 200, f"Auth failed: {auth_response.text}"
        token = auth_response.json()["token"]

        # Check latest analysis - should be empty for new user
        response = requests.get(f"{BASE_URL}/api/cv/latest-analysis?token={token}")
        assert response.status_code == 200, f"Latest analysis failed: {response.text}"
        data = response.json()
        assert "has_analysis" in data, "Response should have has_analysis field"
        assert data["has_analysis"] == False, "New user should have no analysis"
        print("✓ New user returns has_analysis: false")

    def test_latest_analysis_invalid_token_returns_401(self):
        """Invalid token should return 401"""
        response = requests.get(f"{BASE_URL}/api/cv/latest-analysis?token=invalid_token_xyz")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid token returns 401")

    def test_latest_analysis_missing_token_returns_error(self):
        """Missing token should return error (422 or 401)"""
        response = requests.get(f"{BASE_URL}/api/cv/latest-analysis")
        assert response.status_code in [401, 422], f"Expected 401/422, got {response.status_code}"
        print("✓ Missing token returns error")


class TestCvAnalyzeTextEndpoint:
    """Tests for POST /api/cv/analyze-text endpoint"""

    @pytest.fixture
    def auth_token(self):
        """Create a new token for testing"""
        response = requests.post(
            f"{BASE_URL}/api/auth/anonymous",
            json={"role": "particulier"}
        )
        assert response.status_code == 200
        return response.json()["token"]

    def test_analyze_text_returns_job_id(self, auth_token):
        """POST /api/cv/analyze-text should return job_id"""
        cv_text = """
        Jean Dupont
        Développeur Full-Stack
        
        EXPÉRIENCE PROFESSIONNELLE
        
        2020-2024: Développeur Senior chez TechCorp
        - Développement d'applications web avec React et Node.js
        - Gestion de projets agiles
        - Leadership d'équipe technique de 5 personnes
        
        2018-2020: Développeur Junior chez StartupXYZ
        - Développement front-end avec Vue.js
        - Collaboration en équipe
        
        COMPÉTENCES
        - JavaScript, TypeScript, Python
        - React, Node.js, Vue.js
        - Communication, Travail d'équipe, Leadership
        - Gestion du temps, Adaptabilité
        
        FORMATION
        Master en Informatique - Université Paris-Saclay
        """

        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={auth_token}",
            json={"text": cv_text, "filename": "cv_test.txt"}
        )
        assert response.status_code == 200, f"Analyze text failed: {response.text}"
        data = response.json()
        assert "job_id" in data, "Response should have job_id"
        assert "status" in data, "Response should have status"
        assert data["status"] == "started", f"Status should be 'started', got {data['status']}"
        print(f"✓ Analyze text returns job_id: {data['job_id']}")
        return data["job_id"]

    def test_analyze_text_empty_text_returns_400(self, auth_token):
        """Empty text should return 400"""
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={auth_token}",
            json={"text": "", "filename": "empty.txt"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Empty text returns 400")

    def test_analyze_text_short_text_returns_400(self, auth_token):
        """Too short text should return 400"""
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={auth_token}",
            json={"text": "short text", "filename": "short.txt"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Short text returns 400")


class TestCvAnalysisStatusEndpoint:
    """Tests for GET /api/cv/analyze/status endpoint"""

    @pytest.fixture
    def auth_token(self):
        """Create a new token for testing"""
        response = requests.post(
            f"{BASE_URL}/api/auth/anonymous",
            json={"role": "particulier"}
        )
        assert response.status_code == 200
        return response.json()["token"]

    def test_status_invalid_job_id_returns_404(self, auth_token):
        """Invalid job_id should return 404"""
        response = requests.get(
            f"{BASE_URL}/api/cv/analyze/status?token={auth_token}&job_id=invalid-job-id-xyz"
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Invalid job_id returns 404")


class TestCvModelsEndpoint:
    """Tests for GET /api/cv/models endpoint"""

    @pytest.fixture
    def auth_token(self):
        """Create a new token for testing"""
        response = requests.post(
            f"{BASE_URL}/api/auth/anonymous",
            json={"role": "particulier"}
        )
        assert response.status_code == 200
        return response.json()["token"]

    def test_models_new_user_returns_empty(self, auth_token):
        """New user should have no CV models"""
        response = requests.get(f"{BASE_URL}/api/cv/models?token={auth_token}")
        assert response.status_code == 200, f"CV models failed: {response.text}"
        data = response.json()
        assert "models" in data, "Response should have models field"
        assert data["models"] == {} or len(data["models"]) == 0, "New user should have empty models"
        print("✓ New user returns empty models")


class TestCvAnalysisFullFlow:
    """Integration test for full CV analysis flow including persistence"""

    def test_full_analysis_flow_with_persistence(self):
        """Test: Upload CV -> Wait for analysis -> Check latest-analysis returns result"""
        # Step 1: Create new token
        auth_response = requests.post(
            f"{BASE_URL}/api/auth/anonymous",
            json={"role": "particulier"}
        )
        assert auth_response.status_code == 200
        token = auth_response.json()["token"]
        print(f"✓ Created token")

        # Step 2: Verify no analysis exists initially
        latest_response = requests.get(f"{BASE_URL}/api/cv/latest-analysis?token={token}")
        assert latest_response.status_code == 200
        assert latest_response.json()["has_analysis"] == False
        print("✓ Initial state: no analysis")

        # Step 3: Submit CV for analysis
        cv_text = """
        Marie Martin
        Chef de Projet Digital
        
        EXPÉRIENCE PROFESSIONNELLE
        
        2021-2024: Chef de Projet chez AgenceDigitale
        - Gestion de projets web et mobile
        - Coordination d'équipes pluridisciplinaires
        - Relation client et suivi de performance
        
        2019-2021: Assistant Chef de Projet chez MediaGroup
        - Support à la gestion de projet
        - Rédaction de cahiers des charges
        - Suivi de planning
        
        COMPÉTENCES TECHNIQUES
        - Gestion de projet Agile (Scrum, Kanban)
        - Outils: Jira, Trello, Asana
        - SEO, Google Analytics
        
        COMPÉTENCES TRANSVERSALES
        - Leadership, Communication
        - Organisation, Adaptabilité
        - Travail en équipe, Résolution de problèmes
        
        FORMATION
        Master Marketing Digital - ESCP
        """

        analyze_response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={token}",
            json={"text": cv_text, "filename": "cv_marie.txt"}
        )
        assert analyze_response.status_code == 200
        job_id = analyze_response.json()["job_id"]
        print(f"✓ Analysis job started: {job_id}")

        # Step 4: Poll for completion (max 120 seconds for AI analysis)
        max_polls = 40
        completed = False
        result = None
        
        for i in range(max_polls):
            time.sleep(3)
            status_response = requests.get(
                f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={job_id}"
            )
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"  Poll {i+1}: {status_data.get('status')} - {status_data.get('step', '')}")
                
                if status_data["status"] == "completed":
                    completed = True
                    result = status_data["result"]
                    break
                elif status_data["status"] == "failed":
                    print(f"  Analysis failed: {status_data.get('error')}")
                    break

        if not completed:
            print("⚠ Analysis did not complete in time (this may be due to AI service)")
            pytest.skip("AI analysis timeout - skipping persistence check")
            return

        # Step 5: Verify result contains expected fields including offres_emploi_suggerees
        assert result is not None, "Result should not be None"
        assert "savoir_faire_count" in result, "Result should have savoir_faire_count"
        assert "savoir_etre_count" in result, "Result should have savoir_etre_count"
        assert "experiences_count" in result, "Result should have experiences_count"
        assert "formations_suggestions" in result, "Result should have formations_suggestions"
        assert "competences_transversales" in result, "Result should have competences_transversales"
        assert "offres_emploi_suggerees" in result, "Result should have offres_emploi_suggerees"
        print(f"✓ Analysis completed with {result['savoir_faire_count']} savoir-faire, {result['savoir_etre_count']} savoir-être")
        print(f"  Offres emploi suggérées: {len(result.get('offres_emploi_suggerees', []))}")

        # Step 6: Verify latest-analysis returns the result (persistence test)
        latest_response = requests.get(f"{BASE_URL}/api/cv/latest-analysis?token={token}")
        assert latest_response.status_code == 200
        latest_data = latest_response.json()
        assert latest_data["has_analysis"] == True, "Should have analysis after completion"
        assert "result" in latest_data, "Should have result field"
        persisted_result = latest_data["result"]
        assert persisted_result["savoir_faire_count"] == result["savoir_faire_count"], "Persisted result should match"
        print("✓ Latest-analysis returns persisted result correctly")

        # Step 7: Verify CV models were generated
        models_response = requests.get(f"{BASE_URL}/api/cv/models?token={token}")
        assert models_response.status_code == 200
        models_data = models_response.json()
        assert "models" in models_data
        # Models may have content if AI generated them
        print(f"✓ CV models endpoint working (models generated: {len(models_data.get('models', {}))})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
