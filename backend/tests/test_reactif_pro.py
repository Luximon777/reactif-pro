"""
Comprehensive Backend Tests for Ré'Actif Pro Platform
Tests all API endpoints including:
- Anonymous authentication
- Role switching  
- Profile management
- Jobs and matching
- Coffre-fort (document vault)
- Observatoire (skills observatory)
- Evolution Index
"""

import pytest
import requests
import os
import time

# Get base URL from environment - NO default value
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSetup:
    """Initial setup and seed data tests"""
    
    def test_health_check(self):
        """Test API is accessible"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print(f"✓ API accessible, response: {response.json()}")
    
    def test_seed_database(self):
        """Seed database with demo data"""
        response = requests.post(f"{BASE_URL}/api/seed")
        assert response.status_code == 200
        print(f"✓ Database seeded successfully: {response.json()}")


class TestAnonymousAuth:
    """Anonymous authentication flow tests"""
    
    def test_create_anonymous_token_particulier(self):
        """Create anonymous token for particulier role"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "role" in data
        assert data["role"] == "particulier"
        assert "profile_id" in data
        print(f"✓ Particulier token created: {data['token'][:20]}...")
        return data["token"]
    
    def test_create_anonymous_token_entreprise(self):
        """Create anonymous token for entreprise role"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "entreprise"})
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "entreprise"
        print(f"✓ Entreprise token created")
        return data["token"]
    
    def test_create_anonymous_token_partenaire(self):
        """Create anonymous token for partenaire role"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "partenaire"})
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "partenaire"
        print(f"✓ Partenaire token created")
        return data["token"]
    
    def test_verify_token(self):
        """Verify token is valid"""
        # Create a token first
        create_response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = create_response.json()["token"]
        
        # Verify it
        verify_response = requests.get(f"{BASE_URL}/api/auth/verify?token={token}")
        assert verify_response.status_code == 200
        data = verify_response.json()
        assert data["valid"] == True
        assert "role" in data
        assert "profile_id" in data
        print(f"✓ Token verified successfully")
    
    def test_verify_invalid_token(self):
        """Verify invalid token returns error"""
        response = requests.get(f"{BASE_URL}/api/auth/verify?token=invalid_token_12345")
        assert response.status_code == 401
        print(f"✓ Invalid token rejected correctly")


class TestRoleSwitching:
    """Role switching functionality tests"""
    
    @pytest.fixture
    def token(self):
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        return response.json()["token"]
    
    def test_switch_to_entreprise(self, token):
        """Switch from particulier to entreprise"""
        response = requests.post(f"{BASE_URL}/api/auth/switch-role?token={token}&new_role=entreprise")
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "entreprise"
        print(f"✓ Switched to entreprise role")
    
    def test_switch_to_partenaire(self, token):
        """Switch to partenaire role"""
        response = requests.post(f"{BASE_URL}/api/auth/switch-role?token={token}&new_role=partenaire")
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "partenaire"
        print(f"✓ Switched to partenaire role")
    
    def test_switch_invalid_role(self, token):
        """Attempt to switch to invalid role"""
        response = requests.post(f"{BASE_URL}/api/auth/switch-role?token={token}&new_role=invalid_role")
        assert response.status_code == 400
        print(f"✓ Invalid role rejected correctly")


class TestProfile:
    """Profile management tests"""
    
    @pytest.fixture
    def auth_data(self):
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        return response.json()
    
    def test_get_profile(self, auth_data):
        """Get user profile"""
        token = auth_data["token"]
        response = requests.get(f"{BASE_URL}/api/profile?token={token}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "role" in data
        assert "skills" in data
        print(f"✓ Profile retrieved: {data['name']}")
    
    def test_update_profile(self, auth_data):
        """Update profile with skills"""
        token = auth_data["token"]
        update_data = {
            "name": "TEST_User",
            "skills": [
                {"name": "Python", "level": 80},
                {"name": "JavaScript", "level": 70}
            ],
            "sectors": ["Informatique", "Administration"],
            "experience_years": 5
        }
        response = requests.put(f"{BASE_URL}/api/profile?token={token}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TEST_User"
        assert len(data["skills"]) == 2
        print(f"✓ Profile updated with skills and sectors")


class TestJobs:
    """Jobs API tests"""
    
    @pytest.fixture
    def particulier_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        return response.json()["token"]
    
    @pytest.fixture
    def entreprise_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "entreprise"})
        return response.json()["token"]
    
    def test_get_jobs(self, particulier_token):
        """Get available jobs"""
        response = requests.get(f"{BASE_URL}/api/jobs?token={particulier_token}")
        assert response.status_code == 200
        jobs = response.json()
        assert isinstance(jobs, list)
        if len(jobs) > 0:
            assert "title" in jobs[0]
            assert "company" in jobs[0]
            assert "required_skills" in jobs[0]
        print(f"✓ Retrieved {len(jobs)} jobs")
    
    def test_get_job_detail(self, particulier_token):
        """Get specific job details"""
        # First get jobs list
        jobs_response = requests.get(f"{BASE_URL}/api/jobs?token={particulier_token}")
        jobs = jobs_response.json()
        
        if len(jobs) > 0:
            job_id = jobs[0]["id"]
            response = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
            assert response.status_code == 200
            job = response.json()
            assert job["id"] == job_id
            print(f"✓ Job detail retrieved: {job['title']}")
    
    def test_ai_job_matching(self, particulier_token):
        """Test AI-powered job matching"""
        # Update profile with skills first
        skills_data = {
            "skills": [
                {"name": "Excel", "level": 80},
                {"name": "Communication", "level": 70},
                {"name": "Gestion administrative", "level": 60}
            ],
            "sectors": ["Administration"]
        }
        requests.put(f"{BASE_URL}/api/profile?token={particulier_token}", json=skills_data)
        
        # Get jobs
        jobs_response = requests.get(f"{BASE_URL}/api/jobs?token={particulier_token}")
        jobs = jobs_response.json()
        
        if len(jobs) > 0:
            job_id = jobs[0]["id"]
            # Test AI matching - allow some time for AI response
            response = requests.get(f"{BASE_URL}/api/jobs/{job_id}/match?token={particulier_token}", timeout=30)
            assert response.status_code == 200
            match_result = response.json()
            assert "score" in match_result
            assert "rationale" in match_result
            assert isinstance(match_result["score"], (int, float))
            print(f"✓ AI Match score: {match_result['score']}, rationale: {match_result['rationale'][:50]}...")
    
    def test_create_job_as_entreprise(self, entreprise_token):
        """Create job as entreprise role"""
        job_data = {
            "title": "TEST_Développeur Python",
            "company": "TEST Company",
            "location": "Paris, France",
            "contract_type": "CDI",
            "salary_range": "45000-55000€",
            "required_skills": ["Python", "FastAPI", "MongoDB"],
            "description": "Développeur Python pour notre équipe tech",
            "sector": "Informatique"
        }
        response = requests.post(f"{BASE_URL}/api/jobs?token={entreprise_token}", json=job_data)
        assert response.status_code == 200
        job = response.json()
        assert job["title"] == "TEST_Développeur Python"
        print(f"✓ Job created: {job['title']}")


class TestCoffreFort:
    """Coffre-fort (Document Vault) tests"""
    
    @pytest.fixture
    def token(self):
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        return response.json()["token"]
    
    def test_get_categories(self):
        """Get document categories"""
        response = requests.get(f"{BASE_URL}/api/coffre/categories")
        assert response.status_code == 200
        categories = response.json()
        assert "identite_professionnelle" in categories
        assert "diplomes_certifications" in categories
        print(f"✓ Retrieved {len(categories)} document categories")
    
    def test_create_document(self, token):
        """Create document in coffre-fort"""
        doc_data = {
            "title": "TEST_CV Marketing",
            "category": "identite_professionnelle",
            "document_type": "CV",
            "file_name": "cv_marketing.pdf",
            "competences_liees": ["Marketing", "Communication"],
            "description": "Mon CV pour les postes marketing",
            "privacy_level": "private"
        }
        response = requests.post(f"{BASE_URL}/api/coffre/documents?token={token}", json=doc_data)
        assert response.status_code == 200
        doc = response.json()
        assert doc["title"] == "TEST_CV Marketing"
        assert doc["category"] == "identite_professionnelle"
        print(f"✓ Document created: {doc['title']}")
        return doc["id"]
    
    def test_get_documents(self, token):
        """Get user's documents"""
        response = requests.get(f"{BASE_URL}/api/coffre/documents?token={token}")
        assert response.status_code == 200
        docs = response.json()
        assert isinstance(docs, list)
        print(f"✓ Retrieved {len(docs)} documents")
    
    def test_get_coffre_stats(self, token):
        """Get coffre-fort statistics"""
        response = requests.get(f"{BASE_URL}/api/coffre/stats?token={token}")
        assert response.status_code == 200
        stats = response.json()
        assert "total_documents" in stats
        assert "competences_prouvees" in stats
        print(f"✓ Coffre stats: {stats['total_documents']} documents")


class TestObservatoire:
    """Observatoire Prédictif des Compétences tests"""
    
    @pytest.fixture
    def token(self):
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        return response.json()["token"]
    
    def test_get_dashboard(self):
        """Get observatoire dashboard data"""
        response = requests.get(f"{BASE_URL}/api/observatoire/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "emerging_skills" in data
        assert "sector_trends" in data
        assert "indicators" in data
        print(f"✓ Observatoire dashboard: {data['indicators'].get('total_emerging_skills', 0)} emerging skills")
    
    def test_get_emerging_skills(self):
        """Get emerging skills list"""
        response = requests.get(f"{BASE_URL}/api/observatoire/emerging-skills")
        assert response.status_code == 200
        skills = response.json()
        assert isinstance(skills, list)
        if len(skills) > 0:
            assert "skill_name" in skills[0]
            assert "emergence_score" in skills[0]
        print(f"✓ Retrieved {len(skills)} emerging skills")
    
    def test_get_sector_trends(self):
        """Get sector trends"""
        response = requests.get(f"{BASE_URL}/api/observatoire/sector-trends")
        assert response.status_code == 200
        trends = response.json()
        assert isinstance(trends, list)
        if len(trends) > 0:
            assert "sector_name" in trends[0]
            assert "transformation_index" in trends[0]
        print(f"✓ Retrieved {len(trends)} sector trends")
    
    def test_create_contribution_with_ai(self, token):
        """Submit contribution with AI analysis"""
        contrib_data = {
            "contribution_type": "nouvelle_competence",
            "skill_name": "TEST_Prompt Engineering Avancé",
            "skill_description": "Optimisation de prompts pour LLM",
            "related_job": "Data Scientist",
            "related_sector": "Informatique",
            "related_tools": ["ChatGPT", "Claude"],
            "context": "Observé dans le cadre de projets d'IA"
        }
        response = requests.post(f"{BASE_URL}/api/observatoire/contributions?token={token}", json=contrib_data, timeout=30)
        assert response.status_code == 200
        result = response.json()
        assert "contribution_id" in result
        assert "status" in result
        assert "ai_analysis" in result
        print(f"✓ Contribution created with AI analysis: status={result['status']}")
    
    def test_get_contributions(self, token):
        """Get user's contributions"""
        response = requests.get(f"{BASE_URL}/api/observatoire/contributions?token={token}")
        assert response.status_code == 200
        contribs = response.json()
        assert isinstance(contribs, list)
        print(f"✓ Retrieved {len(contribs)} contributions")


class TestEvolutionIndex:
    """Indice d'Évolution des Compétences tests"""
    
    @pytest.fixture
    def token(self):
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        return response.json()["token"]
    
    def test_get_evolution_dashboard(self):
        """Get evolution index dashboard"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "distribution" in data
        assert "top_transforming_jobs" in data
        assert "most_stable_jobs" in data
        assert "sectors" in data
        
        # Validate summary structure
        summary = data["summary"]
        assert "total_jobs_analyzed" in summary
        assert "total_sectors_analyzed" in summary
        assert "average_job_evolution_index" in summary
        
        print(f"✓ Evolution dashboard: {summary['total_jobs_analyzed']} jobs, {summary['total_sectors_analyzed']} sectors")
    
    def test_get_jobs_evolution_index(self):
        """Get evolution index by job"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/jobs")
        assert response.status_code == 200
        jobs = response.json()
        assert isinstance(jobs, list)
        if len(jobs) > 0:
            assert "job_name" in jobs[0]
            assert "evolution_index" in jobs[0]
            assert "interpretation" in jobs[0]
        print(f"✓ Retrieved {len(jobs)} job evolution indices")
    
    def test_get_sectors_evolution_index(self):
        """Get evolution index by sector"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/sectors")
        assert response.status_code == 200
        sectors = response.json()
        assert isinstance(sectors, list)
        if len(sectors) > 0:
            assert "sector_name" in sectors[0]
            assert "evolution_index" in sectors[0]
        print(f"✓ Retrieved {len(sectors)} sector evolution indices")
    
    def test_get_user_evolution_analysis(self, token):
        """Get personalized evolution analysis"""
        # Update profile with sectors first
        profile_data = {
            "sectors": ["Informatique", "Administration"],
            "skills": [
                {"name": "Python", "level": 80},
                {"name": "Excel", "level": 60}
            ]
        }
        requests.put(f"{BASE_URL}/api/profile?token={token}", json=profile_data)
        
        response = requests.get(f"{BASE_URL}/api/evolution-index/user-profile?token={token}")
        assert response.status_code == 200
        analysis = response.json()
        assert "evolution_exposure" in analysis
        assert "exposure_interpretation" in analysis
        print(f"✓ User evolution exposure: {analysis['evolution_exposure']}")


class TestLearning:
    """Learning modules tests"""
    
    @pytest.fixture
    def token(self):
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        return response.json()["token"]
    
    def test_get_learning_modules(self, token):
        """Get learning modules"""
        response = requests.get(f"{BASE_URL}/api/learning?token={token}")
        assert response.status_code == 200
        modules = response.json()
        assert isinstance(modules, list)
        if len(modules) > 0:
            assert "title" in modules[0]
            assert "description" in modules[0]
            assert "skills_developed" in modules[0]
        print(f"✓ Retrieved {len(modules)} learning modules")


class TestMetrics:
    """Platform metrics tests"""
    
    def test_get_metrics(self):
        """Get platform metrics"""
        response = requests.get(f"{BASE_URL}/api/metrics")
        assert response.status_code == 200
        metrics = response.json()
        assert "particuliers" in metrics
        assert "entreprises" in metrics
        assert "partenaires" in metrics
        print(f"✓ Platform metrics retrieved")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
