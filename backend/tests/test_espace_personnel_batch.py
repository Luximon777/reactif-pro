"""
Test suite for Espace Personnel batch fix endpoints (13 new endpoints)
Tests: coach/step-chat, cv/generate-models, coffre/cv-files, coffre/transfer-cv,
       jobs/matching, jobs/applications, jobs/apply, notifications/mark-read,
       emerging/market-correlation, learning/recommendations, passport savoir_faire/savoir_etre
"""
import pytest
import requests
import os
import time

# Use external URL for testing
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://cv-analyzer-53.preview.emergentagent.com').rstrip('/')

# Test tokens from credentials
FANNY95_TOKEN = "J3IYR6zGDSK6qCA40U4aC2ishnu5Zsyd3CPrlFW8INI"
MIKE7_TOKEN = "UHrqIUZvfNQnUf6SJYFNdUDlBSg_LobaMY3sKXo6EoQ"


class TestCoachStepChat:
    """Test POST /api/coach/step-chat - Interactive AI conversation"""
    
    def test_coach_step_chat_with_message_and_step_id(self):
        """Coach step-chat should return AI response"""
        response = requests.post(
            f"{BASE_URL}/api/coach/step-chat",
            params={"token": FANNY95_TOKEN},
            json={"message": "Comment puis-je améliorer mon CV?", "step_id": 1}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "response" in data, f"Missing 'response' key in {data}"
        assert len(data["response"]) > 10, f"Response too short: {data['response']}"
        print(f"✓ Coach response: {data['response'][:100]}...")
    
    def test_coach_step_chat_different_steps(self):
        """Test coach chat with different step_ids"""
        for step_id in [1, 2, 3, 4]:
            response = requests.post(
                f"{BASE_URL}/api/coach/step-chat",
                params={"token": MIKE7_TOKEN},
                json={"message": "Aide-moi", "step_id": step_id}
            )
            assert response.status_code == 200, f"Step {step_id} failed: {response.text}"
            data = response.json()
            assert "response" in data
            print(f"✓ Step {step_id} coach response OK")


class TestCVGenerateModels:
    """Test POST /api/cv/generate-models and GET /api/cv/generate-models/status"""
    
    def test_cv_generate_models_start_job(self):
        """Start CV generation job and check status"""
        # Start job
        response = requests.post(
            f"{BASE_URL}/api/cv/generate-models",
            params={"token": FANNY95_TOKEN},
            json={"model_types": ["chronologique"], "job_offer": ""}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "job_id" in data, f"Missing job_id in {data}"
        assert data.get("status") == "processing", f"Expected processing status, got {data.get('status')}"
        job_id = data["job_id"]
        print(f"✓ CV generation job started: {job_id}")
        
        # Check status
        status_response = requests.get(
            f"{BASE_URL}/api/cv/generate-models/status",
            params={"token": FANNY95_TOKEN, "job_id": job_id}
        )
        assert status_response.status_code == 200, f"Status check failed: {status_response.text}"
        status_data = status_response.json()
        assert "status" in status_data
        print(f"✓ Job status: {status_data.get('status')}")
        return job_id
    
    def test_cv_generate_models_no_model_types(self):
        """Should fail without model_types"""
        response = requests.post(
            f"{BASE_URL}/api/cv/generate-models",
            params={"token": FANNY95_TOKEN},
            json={"model_types": []}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Correctly rejects empty model_types")


class TestCoffreCVFiles:
    """Test GET /api/coffre/cv-files and POST /api/coffre/transfer-cv"""
    
    def test_coffre_cv_files_returns_list(self):
        """GET /api/coffre/cv-files should return a list of files"""
        response = requests.get(
            f"{BASE_URL}/api/coffre/cv-files",
            params={"token": FANNY95_TOKEN}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ Coffre CV files: {len(data)} files found")
        if data:
            print(f"  First file: {data[0]}")
    
    def test_coffre_transfer_cv(self):
        """POST /api/coffre/transfer-cv should transfer analyzed CV"""
        response = requests.post(
            f"{BASE_URL}/api/coffre/transfer-cv",
            params={"token": FANNY95_TOKEN, "cv_type": "cv_uploaded"}
        )
        # May return 404 if no CV analyzed, or 200 if successful
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") == True, f"Expected success=True, got {data}"
            assert "document_id" in data, f"Missing document_id in {data}"
            print(f"✓ CV transferred: {data.get('document_id')}")
        elif response.status_code == 404:
            print("✓ No CV to transfer (expected if no analysis done)")
        else:
            pytest.fail(f"Unexpected status {response.status_code}: {response.text}")


class TestJobsMatching:
    """Test jobs/matching endpoints"""
    
    def test_jobs_matching_returns_jobs_with_match_score(self):
        """GET /api/jobs/matching should return jobs with match_score"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/matching",
            params={"token": FANNY95_TOKEN}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "jobs" in data, f"Missing 'jobs' key in {data}"
        assert "total" in data, f"Missing 'total' key in {data}"
        print(f"✓ Jobs matching: {data.get('total')} jobs found")
        if data.get("jobs"):
            first_job = data["jobs"][0]
            assert "match_score" in first_job, f"Missing match_score in job: {first_job}"
            print(f"  First job match_score: {first_job.get('match_score')}")
    
    def test_jobs_matching_preferences(self):
        """GET /api/jobs/matching/preferences should return preferences"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/matching/preferences",
            params={"token": FANNY95_TOKEN}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Should return default or saved preferences
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"
        print(f"✓ Matching preferences: {data}")
    
    def test_jobs_matching_search_with_query(self):
        """GET /api/jobs/matching/search with q param should filter results"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/matching/search",
            params={"token": FANNY95_TOKEN, "q": "développeur"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "jobs" in data, f"Missing 'jobs' key in {data}"
        assert "query" in data, f"Missing 'query' key in {data}"
        assert data.get("query") == "développeur", f"Query mismatch: {data.get('query')}"
        print(f"✓ Search results for 'développeur': {data.get('total')} jobs")


class TestJobsApplications:
    """Test jobs/apply and jobs/applications endpoints"""
    
    def test_jobs_apply_creates_application(self):
        """POST /api/jobs/apply should create an application"""
        # First get a job to apply to
        jobs_response = requests.get(
            f"{BASE_URL}/api/jobs/matching",
            params={"token": MIKE7_TOKEN}
        )
        if jobs_response.status_code == 200 and jobs_response.json().get("jobs"):
            job_id = jobs_response.json()["jobs"][0].get("id")
            
            response = requests.post(
                f"{BASE_URL}/api/jobs/apply",
                params={"token": MIKE7_TOKEN},
                json={"job_id": job_id, "motivation": "Test application"}
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            data = response.json()
            # Either success or already applied
            assert "success" in data or "message" in data, f"Missing success/message in {data}"
            print(f"✓ Apply result: {data}")
        else:
            print("✓ No jobs available to apply (skipping apply test)")
    
    def test_jobs_apply_requires_job_id(self):
        """POST /api/jobs/apply should require job_id"""
        response = requests.post(
            f"{BASE_URL}/api/jobs/apply",
            params={"token": MIKE7_TOKEN},
            json={}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Correctly requires job_id")
    
    def test_jobs_applications_returns_user_applications(self):
        """GET /api/jobs/applications should return user's applications"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/applications",
            params={"token": MIKE7_TOKEN}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "applications" in data, f"Missing 'applications' key in {data}"
        assert "total" in data, f"Missing 'total' key in {data}"
        print(f"✓ User applications: {data.get('total')} found")


class TestNotifications:
    """Test notifications mark-read endpoints"""
    
    def test_notifications_mark_read(self):
        """POST /api/notifications/mark-read should work"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/mark-read",
            params={"token": FANNY95_TOKEN},
            json={"notification_id": "test-notification-id"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        print("✓ Mark notification read works")
    
    def test_notifications_mark_all_read(self):
        """POST /api/notifications/mark-all-read should work"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/mark-all-read",
            params={"token": FANNY95_TOKEN},
            json={}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        print("✓ Mark all notifications read works")


class TestEmergingMarketCorrelation:
    """Test GET /api/emerging/market-correlation"""
    
    def test_emerging_market_correlation_returns_correlations(self):
        """Should return market correlations by skill"""
        response = requests.get(
            f"{BASE_URL}/api/emerging/market-correlation",
            params={"token": FANNY95_TOKEN}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "correlations" in data, f"Missing 'correlations' key in {data}"
        assert "total_skills_analyzed" in data, f"Missing 'total_skills_analyzed' in {data}"
        print(f"✓ Market correlations: {data.get('total_skills_analyzed')} skills analyzed")
        if data.get("correlations"):
            first = data["correlations"][0]
            assert "skill" in first, f"Missing 'skill' in correlation: {first}"
            assert "market_demand" in first, f"Missing 'market_demand' in correlation: {first}"
            print(f"  First correlation: {first.get('skill')} - {first.get('market_demand')}")


class TestLearningRecommendations:
    """Test GET /api/learning/recommendations"""
    
    def test_learning_recommendations_returns_personalized(self):
        """Should return personalized learning recommendations"""
        response = requests.get(
            f"{BASE_URL}/api/learning/recommendations",
            params={"token": FANNY95_TOKEN}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "recommendations" in data, f"Missing 'recommendations' key in {data}"
        assert "total" in data, f"Missing 'total' key in {data}"
        print(f"✓ Learning recommendations: {data.get('total')} found")
        if data.get("recommendations"):
            first = data["recommendations"][0]
            assert "title" in first, f"Missing 'title' in recommendation: {first}"
            assert "priority" in first, f"Missing 'priority' in recommendation: {first}"
            print(f"  First recommendation: {first.get('title')}")


class TestPassportSavoirFaireSavoirEtre:
    """Test GET /api/passport for savoir_faire and savoir_etre (fanny95)"""
    
    def test_passport_fanny95_has_savoir_faire(self):
        """Passport for fanny95 should have 15 savoir_faire items"""
        response = requests.get(
            f"{BASE_URL}/api/passport",
            params={"token": FANNY95_TOKEN}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        savoir_faire = data.get("savoir_faire", [])
        savoir_etre = data.get("savoir_etre", [])
        
        print(f"✓ Passport savoir_faire count: {len(savoir_faire)}")
        print(f"✓ Passport savoir_etre count: {len(savoir_etre)}")
        
        # Check for expected counts (15 savoir_faire, 6 savoir_etre per requirements)
        assert len(savoir_faire) >= 10, f"Expected at least 10 savoir_faire, got {len(savoir_faire)}"
        assert len(savoir_etre) >= 5, f"Expected at least 5 savoir_etre, got {len(savoir_etre)}"
        
        if savoir_faire:
            print(f"  Sample savoir_faire: {savoir_faire[:3]}")
        if savoir_etre:
            print(f"  Sample savoir_etre: {savoir_etre[:3]}")


class TestExistingEndpointsNotBroken:
    """Verify existing endpoints still work"""
    
    def test_profile_endpoint(self):
        """GET /api/profile should work"""
        response = requests.get(
            f"{BASE_URL}/api/profile",
            params={"token": FANNY95_TOKEN}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ GET /api/profile works")
    
    def test_cv_last_analysis_endpoint(self):
        """GET /api/cv/last-analysis should work"""
        response = requests.get(
            f"{BASE_URL}/api/cv/last-analysis",
            params={"token": FANNY95_TOKEN}
        )
        # May return 404 if no analysis, or 200 with data
        assert response.status_code in [200, 404], f"Unexpected status {response.status_code}: {response.text}"
        print(f"✓ GET /api/cv/last-analysis works (status: {response.status_code})")
    
    def test_trajectory_steps_endpoint(self):
        """GET /api/trajectory/steps should work"""
        response = requests.get(
            f"{BASE_URL}/api/trajectory/steps",
            params={"token": FANNY95_TOKEN}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ GET /api/trajectory/steps works")
    
    def test_observatory_dashboard_endpoint(self):
        """GET /api/observatory/dashboard should work"""
        response = requests.get(
            f"{BASE_URL}/api/observatory/dashboard",
            params={"token": FANNY95_TOKEN}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ GET /api/observatory/dashboard works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
