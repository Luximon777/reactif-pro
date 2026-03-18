"""
Regression test suite for Re'Actif Pro API after major modular refactoring.
Tests all endpoints across the 10 route modules to ensure functionality preserved.
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRootAndAuth:
    """Test root and authentication endpoints - routes/seed.py and routes/auth.py"""
    
    def test_root_api_returns_version_2_0_0(self):
        """GET /api/ returns API info with version 2.0.0"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "2.0.0"
        assert "Re'Actif Pro" in data["message"]
        print(f"✓ Root API: version {data['version']}")
    
    def test_create_anonymous_token(self):
        """POST /api/auth/anonymous creates a token successfully"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["role"] == "particulier"
        assert "profile_id" in data
        print(f"✓ Anonymous token created: {data['token'][:20]}...")
        return data["token"]
    
    def test_verify_token(self):
        """GET /api/auth/verify validates a token"""
        # Create token first
        create_resp = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = create_resp.json()["token"]
        
        # Verify it
        response = requests.get(f"{BASE_URL}/api/auth/verify", params={"token": token})
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert data["role"] == "particulier"
        print(f"✓ Token verified: valid={data['valid']}")
    
    def test_verify_invalid_token(self):
        """GET /api/auth/verify returns 401 for invalid token"""
        response = requests.get(f"{BASE_URL}/api/auth/verify", params={"token": "invalid_token_xyz"})
        assert response.status_code == 401
        print(f"✓ Invalid token rejected with 401")
    
    def test_seed_database(self):
        """POST /api/seed populates demo data"""
        response = requests.post(f"{BASE_URL}/api/seed")
        assert response.status_code == 200
        data = response.json()
        assert data["jobs"] == 5
        assert data["modules"] == 5
        assert data["emerging_skills"] == 5
        print(f"✓ Seed complete: {data['jobs']} jobs, {data['modules']} modules")


class TestProfileEndpoints:
    """Test profile endpoints - routes/auth.py"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        resp = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        self.token = resp.json()["token"]
    
    def test_get_profile(self):
        """GET /api/profile returns user profile"""
        response = requests.get(f"{BASE_URL}/api/profile", params={"token": self.token})
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "role" in data
        print(f"✓ Profile retrieved: role={data['role']}")
    
    def test_update_profile(self):
        """PUT /api/profile updates user profile"""
        response = requests.put(f"{BASE_URL}/api/profile", 
                               params={"token": self.token},
                               json={"name": "Test User Updated"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test User Updated"
        print(f"✓ Profile updated: name={data['name']}")


class TestCVEndpoints:
    """Test CV analysis endpoints - routes/cv.py"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        resp = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        self.token = resp.json()["token"]
    
    def test_get_latest_analysis_new_user(self):
        """GET /api/cv/latest-analysis returns has_analysis:false for new user"""
        response = requests.get(f"{BASE_URL}/api/cv/latest-analysis", params={"token": self.token})
        assert response.status_code == 200
        data = response.json()
        assert data["has_analysis"] == False
        print(f"✓ Latest analysis for new user: has_analysis={data['has_analysis']}")
    
    def test_get_latest_analysis_invalid_token(self):
        """GET /api/cv/latest-analysis returns 401 for invalid token"""
        response = requests.get(f"{BASE_URL}/api/cv/latest-analysis", params={"token": "bad_token"})
        assert response.status_code == 401
        print(f"✓ Invalid token rejected with 401")
    
    def test_analyze_text_starts_job(self):
        """POST /api/cv/analyze-text starts background analysis job"""
        cv_text = """
        Jean Dupont - Développeur Full Stack
        5 ans d'expérience en développement web
        Compétences: JavaScript, Python, React, Node.js, SQL, Git
        Formation: Master en Informatique
        Expérience: Développeur chez TechCorp (2019-2024)
        """
        response = requests.post(f"{BASE_URL}/api/cv/analyze-text",
                                params={"token": self.token},
                                json={"text": cv_text, "filename": "cv_test.txt"})
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "started"
        print(f"✓ CV analysis job started: job_id={data['job_id'][:8]}...")
        return data["job_id"]
    
    def test_analyze_text_too_short(self):
        """POST /api/cv/analyze-text returns 400 for too short text"""
        response = requests.post(f"{BASE_URL}/api/cv/analyze-text",
                                params={"token": self.token},
                                json={"text": "Short", "filename": "cv.txt"})
        assert response.status_code == 400
        print(f"✓ Short CV text rejected with 400")
    
    def test_get_analysis_status(self):
        """GET /api/cv/analyze/status returns job status"""
        # Start a job first
        cv_text = "Test CV content with enough text for analysis " * 10
        start_resp = requests.post(f"{BASE_URL}/api/cv/analyze-text",
                                  params={"token": self.token},
                                  json={"text": cv_text, "filename": "test.txt"})
        job_id = start_resp.json()["job_id"]
        
        # Check status
        response = requests.get(f"{BASE_URL}/api/cv/analyze/status",
                               params={"token": self.token, "job_id": job_id})
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["status"] in ["started", "analyzing", "completed", "failed"]
        print(f"✓ Job status: {data['status']}")
    
    def test_get_analysis_status_invalid_job(self):
        """GET /api/cv/analyze/status returns 404 for invalid job_id"""
        response = requests.get(f"{BASE_URL}/api/cv/analyze/status",
                               params={"token": self.token, "job_id": "nonexistent-job-id"})
        assert response.status_code == 404
        print(f"✓ Invalid job_id rejected with 404")
    
    def test_get_cv_models(self):
        """GET /api/cv/models returns cv models"""
        response = requests.get(f"{BASE_URL}/api/cv/models", params={"token": self.token})
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        print(f"✓ CV models retrieved: {len(data.get('models', {}))} models")


class TestPassportEndpoints:
    """Test passport endpoints - routes/passport.py"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        resp = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        self.token = resp.json()["token"]
        # Create passport by calling GET /api/passport first
        requests.get(f"{BASE_URL}/api/passport", params={"token": self.token})
    
    def test_get_passport(self):
        """GET /api/passport returns or creates passport"""
        response = requests.get(f"{BASE_URL}/api/passport", params={"token": self.token})
        assert response.status_code == 200
        data = response.json()
        assert "token_id" in data
        assert "completeness_score" in data
        assert "competences" in data
        assert "experiences" in data
        print(f"✓ Passport retrieved: completeness={data['completeness_score']}")
    
    def test_get_passport_archeologie(self):
        """GET /api/passport/archeologie returns archaeology chains"""
        response = requests.get(f"{BASE_URL}/api/passport/archeologie", params={"token": self.token})
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "chains" in data
        assert "savoir_faire_list" in data
        assert "savoir_etre_list" in data
        print(f"✓ Archaeology chains: {len(data['chains'])} chains")
    
    def test_get_passport_diagnostic(self):
        """GET /api/passport/diagnostic returns CCSP diagnostic"""
        response = requests.get(f"{BASE_URL}/api/passport/diagnostic", params={"token": self.token})
        assert response.status_code == 200
        data = response.json()
        assert "total_competences" in data
        assert "lamri_lubart_profile" in data
        assert "ccsp_distribution" in data
        print(f"✓ Diagnostic retrieved: {data['total_competences']} competences")


class TestReferentielExplorerEndpoints:
    """Test referentiel/explorer endpoints - routes/explorer.py"""
    
    def test_get_referentiel_archeologie(self):
        """GET /api/referentiel/archeologie returns vertus, valeurs, filieres"""
        response = requests.get(f"{BASE_URL}/api/referentiel/archeologie")
        assert response.status_code == 200
        data = response.json()
        assert "vertus" in data
        assert "valeurs" in data
        assert "filieres" in data
        print(f"✓ Referentiel archeologie: {len(data['vertus'])} vertus, {len(data['valeurs'])} valeurs")
    
    def test_get_explorer_filieres(self):
        """GET /api/referentiel/explorer returns filieres with secteurs"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer")
        assert response.status_code == 200
        data = response.json()
        assert "filieres" in data
        assert "total_filieres" in data
        print(f"✓ Explorer filieres: {data['total_filieres']} filieres")
    
    def test_get_explorer_search(self):
        """GET /api/referentiel/explorer/search returns search results"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/search", params={"q": "test"})
        assert response.status_code == 200
        data = response.json()
        assert "filieres" in data
        assert "secteurs" in data
        assert "metiers" in data
        assert "savoirs_faire" in data
        assert "savoirs_etre" in data
        print(f"✓ Search results retrieved")
    
    def test_get_explorer_stats(self):
        """GET /api/referentiel/explorer/stats returns statistics"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/stats")
        assert response.status_code == 200
        data = response.json()
        assert "filieres" in data
        assert "secteurs" in data
        assert "metiers" in data
        print(f"✓ Explorer stats: {data['filieres']} filieres, {data['secteurs']} secteurs, {data['metiers']} metiers")


class TestObservatoireEndpoints:
    """Test observatoire endpoints - routes/observatoire.py"""
    
    def test_get_observatoire_dashboard(self):
        """GET /api/observatoire/dashboard returns observatoire data"""
        # Seed first to ensure data exists
        requests.post(f"{BASE_URL}/api/seed")
        
        response = requests.get(f"{BASE_URL}/api/observatoire/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "emerging_skills" in data
        assert "sector_trends" in data
        assert "indicators" in data
        print(f"✓ Observatoire dashboard: {len(data['emerging_skills'])} emerging skills")
    
    def test_get_emerging_skills(self):
        """GET /api/observatoire/emerging-skills returns skills list"""
        response = requests.get(f"{BASE_URL}/api/observatoire/emerging-skills")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Emerging skills: {len(data)} skills")
    
    def test_get_sector_trends(self):
        """GET /api/observatoire/sector-trends returns sector trends"""
        response = requests.get(f"{BASE_URL}/api/observatoire/sector-trends")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Sector trends: {len(data)} sectors")


class TestEvolutionIndexEndpoints:
    """Test evolution-index endpoints - routes/evolution.py"""
    
    def test_get_evolution_dashboard(self):
        """GET /api/evolution-index/dashboard returns evolution dashboard"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "distribution" in data
        assert "top_transforming_jobs" in data
        assert "most_stable_jobs" in data
        print(f"✓ Evolution dashboard: {data['summary']['total_jobs_analyzed']} jobs analyzed")
    
    def test_get_jobs_evolution_index(self):
        """GET /api/evolution-index/jobs returns jobs with evolution indices"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/jobs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert "evolution_index" in data[0]
            assert "interpretation" in data[0]
        print(f"✓ Jobs evolution: {len(data)} jobs")
    
    def test_get_sectors_evolution_index(self):
        """GET /api/evolution-index/sectors returns sectors with evolution indices"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/sectors")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Sectors evolution: {len(data)} sectors")


class TestUbuntooEndpoints:
    """Test ubuntoo endpoints - routes/ubuntoo.py"""
    
    def test_get_ubuntoo_dashboard(self):
        """GET /api/ubuntoo/dashboard returns ubuntoo dashboard"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        assert "top_signals" in data
        assert "recent_exchanges" in data
        assert "insights" in data
        print(f"✓ Ubuntoo dashboard: {data['stats']['total_signals_detected']} signals")
    
    def test_get_ubuntoo_signals(self):
        """GET /api/ubuntoo/signals returns signals list"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/signals")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Ubuntoo signals: {len(data)} signals")
    
    def test_get_ubuntoo_insights(self):
        """GET /api/ubuntoo/insights returns insights list"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/insights")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Ubuntoo insights: {len(data)} insights")


class TestCoffreEndpoints:
    """Test coffre-fort endpoints - routes/coffre.py"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        resp = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        self.token = resp.json()["token"]
    
    def test_get_coffre_categories(self):
        """GET /api/coffre/categories returns document categories"""
        response = requests.get(f"{BASE_URL}/api/coffre/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)
        print(f"✓ Coffre categories retrieved")
    
    def test_get_coffre_documents(self):
        """GET /api/coffre/documents returns documents list"""
        response = requests.get(f"{BASE_URL}/api/coffre/documents", params={"token": self.token})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Coffre documents: {len(data)} documents")
    
    def test_get_coffre_stats(self):
        """GET /api/coffre/stats returns coffre statistics"""
        response = requests.get(f"{BASE_URL}/api/coffre/stats", params={"token": self.token})
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "by_category" in data
        print(f"✓ Coffre stats: {data['total_documents']} documents")


class TestJobsEndpoints:
    """Test jobs/learning/metrics endpoints - routes/jobs.py"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        resp = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        self.token = resp.json()["token"]
    
    def test_get_jobs(self):
        """GET /api/jobs returns job offers"""
        response = requests.get(f"{BASE_URL}/api/jobs", params={"token": self.token})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Jobs: {len(data)} offers")
    
    def test_get_learning_modules(self):
        """GET /api/learning returns learning modules"""
        response = requests.get(f"{BASE_URL}/api/learning", params={"token": self.token})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Learning modules: {len(data)} modules")
    
    def test_get_metrics(self):
        """GET /api/metrics returns platform metrics"""
        response = requests.get(f"{BASE_URL}/api/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "particuliers" in data
        assert "entreprises" in data
        assert "partenaires" in data
        print(f"✓ Metrics: {data['particuliers']['total']} particuliers, {data['entreprises']['total']} entreprises")


class TestCriticalFlowIntegration:
    """Test critical end-to-end flow: auth -> profile -> passport -> cv -> explorer"""
    
    def test_full_user_flow(self):
        """Complete user journey from auth to explorer"""
        # 1. Create anonymous token
        auth_resp = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert auth_resp.status_code == 200
        token = auth_resp.json()["token"]
        print(f"✓ Step 1: Auth token created")
        
        # 2. Get profile
        profile_resp = requests.get(f"{BASE_URL}/api/profile", params={"token": token})
        assert profile_resp.status_code == 200
        print(f"✓ Step 2: Profile retrieved")
        
        # 3. Get passport (creates if not exists)
        passport_resp = requests.get(f"{BASE_URL}/api/passport", params={"token": token})
        assert passport_resp.status_code == 200
        print(f"✓ Step 3: Passport created/retrieved")
        
        # 4. Check CV latest analysis
        cv_resp = requests.get(f"{BASE_URL}/api/cv/latest-analysis", params={"token": token})
        assert cv_resp.status_code == 200
        assert cv_resp.json()["has_analysis"] == False
        print(f"✓ Step 4: CV latest-analysis checked (no analysis yet)")
        
        # 5. Get explorer data
        explorer_resp = requests.get(f"{BASE_URL}/api/referentiel/explorer")
        assert explorer_resp.status_code == 200
        print(f"✓ Step 5: Explorer filieres retrieved")
        
        # 6. Get observatoire dashboard
        obs_resp = requests.get(f"{BASE_URL}/api/observatoire/dashboard")
        assert obs_resp.status_code == 200
        print(f"✓ Step 6: Observatoire dashboard retrieved")
        
        # 7. Get evolution index
        evol_resp = requests.get(f"{BASE_URL}/api/evolution-index/dashboard")
        assert evol_resp.status_code == 200
        print(f"✓ Step 7: Evolution dashboard retrieved")
        
        # 8. Get ubuntoo dashboard
        ubuntoo_resp = requests.get(f"{BASE_URL}/api/ubuntoo/dashboard")
        assert ubuntoo_resp.status_code == 200
        print(f"✓ Step 8: Ubuntoo dashboard retrieved")
        
        print(f"\n✓✓✓ Full critical flow completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
