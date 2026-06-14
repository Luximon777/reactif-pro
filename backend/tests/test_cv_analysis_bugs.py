"""
Tests for CV Analysis Bug Fixes - RE'ACTIF PRO
Bug 1: CV upload/analysis must work (LLM key was expired, now fixed)
Bug 2: CV analysis data must persist when navigating between dashboard tabs
Bug 3: CV analysis must auto-fill all sections (competences_transversales, offres_emploi, strengths, gaps)
"""

import pytest
import requests
import os
import time

# Get base URL from environment - NO default value
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Sample CV text content for testing (100+ chars as required)
SAMPLE_CV_TEXT = """
MARIE MARTIN
Développeuse Full Stack Senior

PROFIL PROFESSIONNEL
Développeuse passionnée avec 7 ans d'expérience en développement web et mobile.
Expertise en React, Node.js, Python et bases de données SQL/NoSQL.
Forte capacité d'adaptation et excellent esprit d'équipe.

EXPÉRIENCES PROFESSIONNELLES

Développeuse Full Stack Senior - TechStartup Paris (2021-2024)
- Développement d'applications React/Node.js pour clients B2B
- Architecture microservices avec Docker et Kubernetes
- Mentorat de 3 développeurs juniors
- Mise en place de CI/CD avec GitHub Actions
Réalisations: Réduction de 40% du temps de déploiement, amélioration de la couverture de tests à 85%

Développeuse Backend - AgenceWeb Lyon (2018-2021)
- Développement d'APIs REST avec Python/Django
- Gestion de bases de données PostgreSQL et MongoDB
- Intégration de services tiers (Stripe, SendGrid, AWS)
Réalisations: Migration réussie de 3 applications legacy vers architecture moderne

Développeuse Junior - StartupTech Bordeaux (2017-2018)
- Développement frontend avec Vue.js
- Tests unitaires et d'intégration
- Participation aux code reviews

COMPÉTENCES TECHNIQUES
- Frontend: React, Vue.js, TypeScript, HTML5, CSS3, Tailwind
- Backend: Node.js, Python, Django, FastAPI, Express
- Bases de données: PostgreSQL, MongoDB, Redis
- DevOps: Docker, Kubernetes, AWS, CI/CD
- Outils: Git, Jira, Figma

COMPÉTENCES COMPORTEMENTALES
- Leadership technique et mentorat
- Communication claire et pédagogie
- Résolution de problèmes complexes
- Travail en équipe agile
- Autonomie et proactivité
- Gestion du stress et des priorités

FORMATION
Master Informatique - Université de Lyon (2017)
Licence Informatique - Université de Bordeaux (2015)

LANGUES
Français: Langue maternelle
Anglais: Courant (TOEIC 920)
"""


class TestAuthAnonymous:
    """Test POST /api/auth/anonymous creates token successfully"""

    def test_create_anonymous_token(self):
        """Bug 1 prerequisite: Auth must work"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "token" in data, "Missing 'token' in response"
        assert "role" in data, "Missing 'role' in response"
        assert "profile_id" in data, "Missing 'profile_id' in response"
        assert data["role"] == "particulier"
        assert len(data["token"]) > 20, "Token seems too short"
        
        print(f"✓ Anonymous token created successfully: {data['token'][:20]}...")
        return data


class TestCvAnalyzeText:
    """Test POST /api/cv/analyze-text accepts text and returns job_id"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Create anonymous token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        return response.json()["token"]

    def test_analyze_text_returns_job_id(self, auth_token):
        """Bug 1: CV analysis must accept text and return job_id"""
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={auth_token}",
            json={"text": SAMPLE_CV_TEXT, "filename": "cv_test.txt"},
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "job_id" in data, "Missing 'job_id' in response"
        assert "status" in data, "Missing 'status' in response"
        assert data["status"] == "started", f"Expected status 'started', got {data['status']}"
        
        print(f"✓ CV analyze-text returned job_id: {data['job_id']}")
        return data["job_id"]

    def test_analyze_text_rejects_short_text(self, auth_token):
        """Test that short text (<50 chars) is rejected"""
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={auth_token}",
            json={"text": "Too short", "filename": "short.txt"},
            timeout=10
        )
        
        assert response.status_code == 400, f"Expected 400 for short text, got {response.status_code}"
        print(f"✓ Short text correctly rejected with status 400")


class TestCvAnalysisStatusPolling:
    """Test GET /api/cv/analyze/status polls for results with status completed"""

    @pytest.fixture(scope="class")
    def analysis_job(self):
        """Create token and start CV analysis"""
        # Create token
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        
        # Start analysis
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={token}",
            json={"text": SAMPLE_CV_TEXT, "filename": "cv_poll_test.txt"},
            timeout=30
        )
        job_id = response.json()["job_id"]
        
        return {"token": token, "job_id": job_id}

    def test_poll_for_completion(self, analysis_job):
        """Bug 1: Poll for CV analysis completion (up to 120s)"""
        token = analysis_job["token"]
        job_id = analysis_job["job_id"]
        
        max_polls = 40  # 40 * 3s = 120s max
        final_status = None
        result = None
        
        for i in range(max_polls):
            time.sleep(3)
            response = requests.get(
                f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={job_id}",
                timeout=10
            )
            
            assert response.status_code == 200, f"Status poll failed: {response.status_code}"
            data = response.json()
            
            print(f"  Poll {i+1}: status={data['status']}, step={data.get('step', '')}")
            
            if data["status"] == "completed":
                final_status = "completed"
                result = data.get("result")
                break
            elif data["status"] == "failed":
                final_status = "failed"
                print(f"  ERROR: Analysis failed: {data.get('error')}")
                break
        
        assert final_status == "completed", f"Analysis did not complete. Final status: {final_status}"
        assert result is not None, "Result is None after completion"
        
        print(f"✓ CV analysis completed successfully")
        return result


class TestCvAnalysisResultFields:
    """Test that CV analysis result contains all required fields (Bug 3)"""

    @pytest.fixture(scope="class")
    def completed_analysis(self):
        """Create token, analyze CV, and wait for completion"""
        # Create token
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        
        # Start analysis
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={token}",
            json={"text": SAMPLE_CV_TEXT, "filename": "cv_fields_test.txt"},
            timeout=30
        )
        job_id = response.json()["job_id"]
        
        # Poll for completion
        result = None
        for i in range(40):
            time.sleep(3)
            response = requests.get(
                f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={job_id}",
                timeout=10
            )
            data = response.json()
            if data["status"] == "completed":
                result = data.get("result")
                break
            elif data["status"] == "failed":
                pytest.fail(f"Analysis failed: {data.get('error')}")
        
        if result is None:
            pytest.fail("Analysis did not complete within timeout")
        
        return {"token": token, "result": result}

    def test_result_has_offres_emploi(self, completed_analysis):
        """Bug 3: Analysis must include offres_emploi"""
        result = completed_analysis["result"]
        
        assert "offres_emploi" in result, "Missing 'offres_emploi' in result"
        offres = result["offres_emploi"]
        
        assert isinstance(offres, list), "offres_emploi should be a list"
        assert len(offres) > 0, "Expected at least 1 offre d'emploi"
        
        # Verify offre structure
        for offre in offres[:3]:
            assert "title" in offre, "Offre missing 'title'"
            assert "match_score" in offre, "Offre missing 'match_score'"
        
        print(f"✓ Result has {len(offres)} offres d'emploi")
        for o in offres[:3]:
            print(f"  - {o.get('title')} ({o.get('match_score')}% match)")

    def test_result_has_competences_transversales(self, completed_analysis):
        """Bug 3: Analysis must include competences_transversales"""
        result = completed_analysis["result"]
        
        assert "competences_transversales" in result, "Missing 'competences_transversales' in result"
        ct = result["competences_transversales"]
        
        assert isinstance(ct, list), "competences_transversales should be a list"
        assert len(ct) > 0, "Expected at least 1 competence transversale"
        
        print(f"✓ Result has {len(ct)} competences transversales: {ct[:5]}")

    def test_result_has_strengths(self, completed_analysis):
        """Bug 3: Analysis must include strengths (points forts)"""
        result = completed_analysis["result"]
        
        assert "strengths" in result, "Missing 'strengths' in result"
        strengths = result["strengths"]
        
        assert isinstance(strengths, list), "strengths should be a list"
        assert len(strengths) > 0, "Expected at least 1 strength"
        
        print(f"✓ Result has {len(strengths)} strengths: {strengths[:5]}")

    def test_result_has_gaps(self, completed_analysis):
        """Bug 3: Analysis must include gaps (lacunes)"""
        result = completed_analysis["result"]
        
        assert "gaps" in result, "Missing 'gaps' in result"
        gaps = result["gaps"]
        
        assert isinstance(gaps, list), "gaps should be a list"
        # Gaps may be empty if CV is very complete
        
        print(f"✓ Result has {len(gaps)} gaps: {gaps[:5] if gaps else 'None'}")


class TestLastAnalysisEndpoint:
    """Test GET /api/cv/last-analysis returns last completed analysis"""

    @pytest.fixture(scope="class")
    def user_with_analysis(self):
        """Create token and complete CV analysis"""
        # Create token
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        
        # Start analysis
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={token}",
            json={"text": SAMPLE_CV_TEXT, "filename": "cv_last_test.txt"},
            timeout=30
        )
        job_id = response.json()["job_id"]
        
        # Poll for completion
        for i in range(40):
            time.sleep(3)
            response = requests.get(
                f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={job_id}",
                timeout=10
            )
            data = response.json()
            if data["status"] == "completed":
                break
            elif data["status"] == "failed":
                pytest.fail(f"Analysis failed: {data.get('error')}")
        
        return token

    def test_last_analysis_returns_result(self, user_with_analysis):
        """Bug 2: GET /api/cv/last-analysis must return last completed analysis"""
        token = user_with_analysis
        
        response = requests.get(f"{BASE_URL}/api/cv/last-analysis?token={token}", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "has_analysis" in data, "Missing 'has_analysis' in response"
        assert data["has_analysis"] == True, "Expected has_analysis=True"
        assert "result" in data, "Missing 'result' in response"
        assert data["result"] is not None, "Result should not be None"
        
        # Verify result has key fields
        result = data["result"]
        assert "offres_emploi" in result, "Result missing offres_emploi"
        assert "competences_transversales" in result, "Result missing competences_transversales"
        assert "strengths" in result, "Result missing strengths"
        assert "gaps" in result, "Result missing gaps"
        
        print(f"✓ GET /api/cv/last-analysis returns complete result")
        print(f"  - offres_emploi: {len(result.get('offres_emploi', []))}")
        print(f"  - competences_transversales: {len(result.get('competences_transversales', []))}")
        print(f"  - strengths: {len(result.get('strengths', []))}")
        print(f"  - gaps: {len(result.get('gaps', []))}")

    def test_last_analysis_empty_for_new_user(self):
        """Test that new user without analysis gets has_analysis=False"""
        # Create fresh token
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        
        response = requests.get(f"{BASE_URL}/api/cv/last-analysis?token={token}", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert data["has_analysis"] == False, "Expected has_analysis=False for new user"
        
        print(f"✓ New user correctly gets has_analysis=False")


class TestCvModelsEndpoint:
    """Test GET /api/cv/models returns generated CV models after analysis"""

    @pytest.fixture(scope="class")
    def user_with_analysis(self):
        """Create token and complete CV analysis"""
        # Create token
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        
        # Start analysis
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={token}",
            json={"text": SAMPLE_CV_TEXT, "filename": "cv_models_test.txt"},
            timeout=30
        )
        job_id = response.json()["job_id"]
        
        # Poll for completion
        for i in range(40):
            time.sleep(3)
            response = requests.get(
                f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={job_id}",
                timeout=10
            )
            data = response.json()
            if data["status"] == "completed":
                break
            elif data["status"] == "failed":
                pytest.fail(f"Analysis failed: {data.get('error')}")
        
        return token

    def test_cv_models_returns_4_models(self, user_with_analysis):
        """Test that GET /api/cv/models returns 4 CV models"""
        token = user_with_analysis
        
        response = requests.get(f"{BASE_URL}/api/cv/models?token={token}", timeout=10)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "models" in data, "Missing 'models' in response"
        
        models = data["models"]
        expected_models = ["classique", "competences", "fonctionnel", "mixte"]
        
        for model_name in expected_models:
            assert model_name in models, f"Missing '{model_name}' model"
            assert models[model_name], f"Model '{model_name}' is empty"
        
        print(f"✓ GET /api/cv/models returns 4 CV models:")
        for name in expected_models:
            print(f"  - {name}: {len(models[name])} chars")


class TestProfileUpdatedAfterAnalysis:
    """Test GET /api/profile returns updated strengths, gaps, skills after CV analysis"""

    @pytest.fixture(scope="class")
    def user_with_analysis(self):
        """Create token and complete CV analysis"""
        # Create token
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        
        # Start analysis
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={token}",
            json={"text": SAMPLE_CV_TEXT, "filename": "cv_profile_test.txt"},
            timeout=30
        )
        job_id = response.json()["job_id"]
        
        # Poll for completion
        for i in range(40):
            time.sleep(3)
            response = requests.get(
                f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={job_id}",
                timeout=10
            )
            data = response.json()
            if data["status"] == "completed":
                break
            elif data["status"] == "failed":
                pytest.fail(f"Analysis failed: {data.get('error')}")
        
        return token

    def test_profile_has_strengths(self, user_with_analysis):
        """Test that profile has strengths after CV analysis"""
        token = user_with_analysis
        
        response = requests.get(f"{BASE_URL}/api/profile?token={token}", timeout=10)
        assert response.status_code == 200
        
        profile = response.json()
        assert "strengths" in profile, "Missing 'strengths' in profile"
        assert len(profile["strengths"]) > 0, "Expected strengths to be populated"
        
        print(f"✓ Profile has {len(profile['strengths'])} strengths: {profile['strengths'][:3]}")

    def test_profile_has_gaps(self, user_with_analysis):
        """Test that profile has gaps after CV analysis"""
        token = user_with_analysis
        
        response = requests.get(f"{BASE_URL}/api/profile?token={token}", timeout=10)
        assert response.status_code == 200
        
        profile = response.json()
        assert "gaps" in profile, "Missing 'gaps' in profile"
        # Gaps may be empty for complete profiles
        
        print(f"✓ Profile has {len(profile.get('gaps', []))} gaps")

    def test_profile_has_skills(self, user_with_analysis):
        """Test that profile has skills after CV analysis"""
        token = user_with_analysis
        
        response = requests.get(f"{BASE_URL}/api/profile?token={token}", timeout=10)
        assert response.status_code == 200
        
        profile = response.json()
        assert "skills" in profile, "Missing 'skills' in profile"
        assert len(profile["skills"]) > 0, "Expected skills to be populated"
        
        print(f"✓ Profile has {len(profile['skills'])} skills")
        for skill in profile["skills"][:3]:
            print(f"  - {skill.get('name')}: {skill.get('level')}%")


class TestPassportUpdatedAfterAnalysis:
    """Test GET /api/passport returns competences_transversales, offres_emploi after CV analysis"""

    @pytest.fixture(scope="class")
    def user_with_analysis(self):
        """Create token and complete CV analysis"""
        # Create token
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        
        # Initialize passport first
        requests.get(f"{BASE_URL}/api/passport?token={token}")
        
        # Start analysis
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={token}",
            json={"text": SAMPLE_CV_TEXT, "filename": "cv_passport_test.txt"},
            timeout=30
        )
        job_id = response.json()["job_id"]
        
        # Poll for completion
        for i in range(40):
            time.sleep(3)
            response = requests.get(
                f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={job_id}",
                timeout=10
            )
            data = response.json()
            if data["status"] == "completed":
                break
            elif data["status"] == "failed":
                pytest.fail(f"Analysis failed: {data.get('error')}")
        
        return token

    def test_passport_has_competences_transversales(self, user_with_analysis):
        """Test that passport has competences_transversales after CV analysis"""
        token = user_with_analysis
        
        response = requests.get(f"{BASE_URL}/api/passport?token={token}", timeout=10)
        assert response.status_code == 200
        
        passport = response.json()
        assert "competences_transversales" in passport, "Missing 'competences_transversales' in passport"
        ct = passport["competences_transversales"]
        
        assert isinstance(ct, list), "competences_transversales should be a list"
        assert len(ct) > 0, "Expected competences_transversales to be populated"
        
        print(f"✓ Passport has {len(ct)} competences_transversales: {ct[:3]}")

    def test_passport_has_offres_emploi(self, user_with_analysis):
        """Test that passport has offres_emploi after CV analysis"""
        token = user_with_analysis
        
        response = requests.get(f"{BASE_URL}/api/passport?token={token}", timeout=10)
        assert response.status_code == 200
        
        passport = response.json()
        assert "offres_emploi" in passport, "Missing 'offres_emploi' in passport"
        offres = passport["offres_emploi"]
        
        assert isinstance(offres, list), "offres_emploi should be a list"
        assert len(offres) > 0, "Expected offres_emploi to be populated"
        
        print(f"✓ Passport has {len(offres)} offres_emploi")
        for o in offres[:3]:
            print(f"  - {o.get('title')} ({o.get('match_score')}% match)")

    def test_passport_has_competences(self, user_with_analysis):
        """Test that passport has competences (savoir_faire/savoir_etre) after CV analysis"""
        token = user_with_analysis
        
        response = requests.get(f"{BASE_URL}/api/passport?token={token}", timeout=10)
        assert response.status_code == 200
        
        passport = response.json()
        assert "competences" in passport, "Missing 'competences' in passport"
        competences = passport["competences"]
        
        assert len(competences) > 0, "Expected competences to be populated"
        
        # Count by nature
        savoir_faire = [c for c in competences if c.get("nature") == "savoir_faire"]
        savoir_etre = [c for c in competences if c.get("nature") == "savoir_etre"]
        
        print(f"✓ Passport has {len(competences)} competences:")
        print(f"  - savoir_faire: {len(savoir_faire)}")
        print(f"  - savoir_etre: {len(savoir_etre)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
