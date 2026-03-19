"""
Test suite for Emerging Competences Detection Feature
Tests:
1. GET /api/emerging/competences - list emerging competences for a user
2. GET /api/emerging/competence/{comp_id} - get single emerging competence detail
3. POST /api/emerging/validate/{comp_id} - validate/reject emerging competences
4. GET /api/emerging/observatory - get observatory dashboard data
5. POST /api/cv/analyze-text - triggers 3rd parallel LLM call for emerging detection
6. Integration: After CV analysis, emerging competences are stored in MongoDB
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Sample French CV text with diverse skills for emerging detection
SAMPLE_CV_TEXT = """
Jean Dupont
Data Scientist et IA Engineer - 5 ans d'expérience

COORDONNÉES
Email: jean.dupont@email.com
Téléphone: 06 12 34 56 78
LinkedIn: linkedin.com/in/jeandupont

COMPÉTENCES TECHNIQUES
- Python, TensorFlow, PyTorch, scikit-learn
- MLOps, Kubernetes, Docker, CI/CD
- Prompt Engineering, LLM Fine-tuning, RAG
- Cloud Architecture AWS/GCP/Azure
- Data Engineering avec Spark et Airflow
- Gestion de projets agiles (Scrum, SAFe)

COMPÉTENCES TRANSVERSALES
- Leadership agile et management d'équipes
- Design Thinking et Innovation
- Communication data storytelling
- Mentoring et formation d'équipes
- Négociation et gestion des parties prenantes

EXPÉRIENCES PROFESSIONNELLES

DataCorp - Chef de Projet IA (2020-2025)
- Pilotage de projets d'intelligence artificielle générative
- Mise en place de pipelines MLOps automatisés
- Développement de modèles de NLP pour l'analyse de sentiment
- Management d'une équipe de 6 data scientists
- Réduction de 40% des coûts d'infrastructure cloud

TechStartup - Data Scientist Senior (2018-2020)
- Développement de modèles de machine learning prédictifs
- Mise en production de modèles via API REST
- Collaboration avec les équipes produit pour intégrer l'IA

FORMATION
- Master Data Science - École Polytechnique (2018)
- Certification AWS Solutions Architect (2021)
- Certification Google Professional ML Engineer (2022)

LANGUES
- Français (natif)
- Anglais (courant - TOEIC 950)
"""


class TestEmergingCompetencesAPI:
    """Test emerging competences CRUD endpoints"""
    
    @pytest.fixture(scope="class")
    def test_token(self):
        """Create anonymous token for testing"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200, f"Failed to create token: {response.text}"
        data = response.json()
        assert "token" in data
        return data["token"]
    
    def test_get_emerging_competences_empty_user(self, test_token):
        """GET /api/emerging/competences returns empty list for new user"""
        response = requests.get(f"{BASE_URL}/api/emerging/competences?token={test_token}")
        assert response.status_code == 200
        data = response.json()
        assert "competences" in data
        assert "total" in data
        assert isinstance(data["competences"], list)
        # New user should have no emerging competences initially
        print(f"Initial emerging competences count: {data['total']}")
    
    def test_get_emerging_competence_not_found(self, test_token):
        """GET /api/emerging/competence/{comp_id} returns 404 for non-existent"""
        fake_comp_id = "non-existent-comp-id-12345"
        response = requests.get(f"{BASE_URL}/api/emerging/competence/{fake_comp_id}?token={test_token}")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        print(f"404 response: {data['detail']}")
    
    def test_validate_competence_not_found(self, test_token):
        """POST /api/emerging/validate/{comp_id} returns 404 for non-existent"""
        fake_comp_id = "non-existent-comp-id-12345"
        response = requests.post(
            f"{BASE_URL}/api/emerging/validate/{fake_comp_id}?token={test_token}",
            json={"decision": "valide", "commentaire": "Test validation"}
        )
        assert response.status_code == 404
        print(f"Validation 404 response: {response.json()}")
    
    def test_get_observatory_data(self, test_token):
        """GET /api/emerging/observatory returns observatory dashboard data"""
        response = requests.get(f"{BASE_URL}/api/emerging/observatory?token={test_token}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify observatory structure
        assert "top_emerging" in data
        assert "by_category" in data
        assert "by_level" in data
        
        assert isinstance(data["top_emerging"], list)
        assert isinstance(data["by_category"], list)
        assert isinstance(data["by_level"], list)
        
        print(f"Observatory data - Top: {len(data['top_emerging'])}, Categories: {len(data['by_category'])}, Levels: {len(data['by_level'])}")


class TestCVAnalysisEmergingDetection:
    """Test CV analysis triggers emerging competences detection"""
    
    @pytest.fixture(scope="class")
    def analysis_token(self):
        """Create anonymous token for CV analysis testing"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200, f"Failed to create token: {response.text}"
        return response.json()["token"]
    
    def test_cv_analysis_triggers_emerging_detection(self, analysis_token):
        """POST /api/cv/analyze-text triggers 3 parallel LLM calls including emerging detection"""
        # Submit CV for analysis
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={analysis_token}",
            json={"text": SAMPLE_CV_TEXT, "filename": "test_cv_emerging.txt"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "started"
        job_id = data["job_id"]
        print(f"CV analysis job started: {job_id}")
        
        # Poll for completion (max 60 seconds)
        max_wait = 60
        poll_interval = 3
        elapsed = 0
        job_result = None
        
        while elapsed < max_wait:
            status_response = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={analysis_token}&job_id={job_id}")
            assert status_response.status_code == 200
            status_data = status_response.json()
            print(f"Job status: {status_data['status']} - Step: {status_data.get('step', 'N/A')} ({elapsed}s)")
            
            if status_data["status"] == "completed":
                job_result = status_data.get("result")
                break
            elif status_data["status"] == "failed":
                pytest.fail(f"CV analysis failed: {status_data.get('error')}")
            
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        assert job_result is not None, f"CV analysis did not complete within {max_wait} seconds"
        
        # Verify result contains emerging_count
        assert "emerging_count" in job_result, "Result should contain emerging_count from 3rd LLM call"
        print(f"Analysis result - Emerging count: {job_result['emerging_count']}")
        print(f"Savoir-faire: {job_result.get('savoir_faire_count')}, Savoir-être: {job_result.get('savoir_etre_count')}")
        
        return job_result
    
    def test_emerging_competences_after_analysis(self, analysis_token):
        """After CV analysis, GET /api/emerging/competences should return detected competences"""
        # First run the analysis
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={analysis_token}",
            json={"text": SAMPLE_CV_TEXT, "filename": "test_cv_emerging2.txt"}
        )
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        
        # Wait for completion
        max_wait = 60
        elapsed = 0
        while elapsed < max_wait:
            status = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={analysis_token}&job_id={job_id}")
            if status.json()["status"] == "completed":
                break
            elif status.json()["status"] == "failed":
                pytest.fail("Analysis failed")
            time.sleep(3)
            elapsed += 3
        
        # Now fetch emerging competences
        emerging_response = requests.get(f"{BASE_URL}/api/emerging/competences?token={analysis_token}")
        assert emerging_response.status_code == 200
        emerging_data = emerging_response.json()
        
        print(f"Emerging competences count: {emerging_data['total']}")
        
        # If analysis detected emerging competences, verify their structure
        if emerging_data["total"] > 0:
            comp = emerging_data["competences"][0]
            assert "id" in comp
            assert "nom_principal" in comp
            assert "categorie" in comp
            assert "score_emergence" in comp
            assert "niveau_emergence" in comp
            assert "justification" in comp
            assert "indicateurs_cles" in comp
            assert "secteurs_porteurs" in comp
            assert "metiers_associes" in comp
            assert "tendance" in comp
            
            print(f"First emerging competence: {comp['nom_principal']} (score: {comp['score_emergence']}, niveau: {comp['niveau_emergence']})")
            
            # Verify score is 0-100
            assert 0 <= comp["score_emergence"] <= 100
            
            # Verify niveau_emergence is valid
            valid_niveaux = ["signal_faible", "emergente", "en_croissance", "etablie"]
            assert comp["niveau_emergence"] in valid_niveaux
            
            # Verify categorie is valid
            valid_categories = ["tech_emergente", "hybride", "soft_skill_avancee", "methodologique", "sectorielle"]
            assert comp["categorie"] in valid_categories
            
            return comp
        else:
            print("No emerging competences detected in this analysis")
            return None


class TestEmergingCompetenceValidation:
    """Test validation workflow for emerging competences"""
    
    @pytest.fixture(scope="class")
    def setup_with_emerging(self):
        """Create token and run CV analysis to get emerging competences"""
        # Create token
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        token = response.json()["token"]
        
        # Run CV analysis
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={token}",
            json={"text": SAMPLE_CV_TEXT, "filename": "test_cv_validation.txt"}
        )
        job_id = response.json()["job_id"]
        
        # Wait for completion
        max_wait = 60
        elapsed = 0
        while elapsed < max_wait:
            status = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={job_id}")
            if status.json()["status"] == "completed":
                break
            time.sleep(3)
            elapsed += 3
        
        # Get emerging competences
        emerging = requests.get(f"{BASE_URL}/api/emerging/competences?token={token}")
        competences = emerging.json()["competences"]
        
        return {"token": token, "competences": competences}
    
    def test_validate_competence_valid_decision(self, setup_with_emerging):
        """POST /api/emerging/validate/{comp_id} with valid decision"""
        token = setup_with_emerging["token"]
        competences = setup_with_emerging["competences"]
        
        if len(competences) == 0:
            pytest.skip("No emerging competences available for validation test")
        
        comp_id = competences[0]["id"]
        
        # Test 'valide' decision
        response = requests.post(
            f"{BASE_URL}/api/emerging/validate/{comp_id}?token={token}",
            json={"decision": "valide", "commentaire": "Test validation - confirmed"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["decision"] == "valide"
        print(f"Validated competence {comp_id} as 'valide'")
    
    def test_validate_competence_with_modification(self, setup_with_emerging):
        """POST /api/emerging/validate/{comp_id} with 'modifie' decision and new label"""
        token = setup_with_emerging["token"]
        competences = setup_with_emerging["competences"]
        
        if len(competences) < 2:
            pytest.skip("Not enough emerging competences for modification test")
        
        comp_id = competences[1]["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/emerging/validate/{comp_id}?token={token}",
            json={
                "decision": "modifie",
                "commentaire": "Renamed for clarity",
                "nouveau_libelle": "Compétence modifiée test"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["decision"] == "modifie"
        print(f"Modified competence {comp_id}")
    
    def test_validate_competence_invalid_decision(self, setup_with_emerging):
        """POST /api/emerging/validate/{comp_id} with invalid decision returns 400"""
        token = setup_with_emerging["token"]
        competences = setup_with_emerging["competences"]
        
        if len(competences) == 0:
            pytest.skip("No emerging competences available")
        
        comp_id = competences[0]["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/emerging/validate/{comp_id}?token={token}",
            json={"decision": "invalid_decision", "commentaire": "Test"}
        )
        assert response.status_code == 400
        print(f"Invalid decision correctly rejected: {response.json()}")


class TestEmergingCompetenceDetail:
    """Test single competence detail endpoint"""
    
    @pytest.fixture(scope="class")
    def setup_for_detail(self):
        """Create token and run CV analysis"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        
        # Run CV analysis
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={token}",
            json={"text": SAMPLE_CV_TEXT, "filename": "test_cv_detail.txt"}
        )
        job_id = response.json()["job_id"]
        
        # Wait for completion
        max_wait = 60
        elapsed = 0
        while elapsed < max_wait:
            status = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={job_id}")
            if status.json()["status"] == "completed":
                break
            time.sleep(3)
            elapsed += 3
        
        emerging = requests.get(f"{BASE_URL}/api/emerging/competences?token={token}")
        return {"token": token, "competences": emerging.json()["competences"]}
    
    def test_get_competence_detail(self, setup_for_detail):
        """GET /api/emerging/competence/{comp_id} returns full detail with related data"""
        token = setup_for_detail["token"]
        competences = setup_for_detail["competences"]
        
        if len(competences) == 0:
            pytest.skip("No emerging competences for detail test")
        
        comp_id = competences[0]["id"]
        
        response = requests.get(f"{BASE_URL}/api/emerging/competence/{comp_id}?token={token}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify core fields
        assert data["id"] == comp_id
        assert "nom_principal" in data
        assert "categorie" in data
        assert "score_emergence" in data
        
        # Verify related data is included
        assert "aliases" in data
        assert "sources" in data
        assert "validations" in data
        
        print(f"Competence detail: {data['nom_principal']}")
        print(f"Aliases: {len(data['aliases'])}, Sources: {len(data['sources'])}, Validations: {len(data['validations'])}")


class TestFilteringAndQueries:
    """Test filtering capabilities of emerging competences endpoint"""
    
    @pytest.fixture(scope="class")
    def setup_with_data(self):
        """Create token and analyze CV"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = response.json()["token"]
        
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text?token={token}",
            json={"text": SAMPLE_CV_TEXT, "filename": "test_cv_filter.txt"}
        )
        job_id = response.json()["job_id"]
        
        max_wait = 60
        elapsed = 0
        while elapsed < max_wait:
            status = requests.get(f"{BASE_URL}/api/cv/analyze/status?token={token}&job_id={job_id}")
            if status.json()["status"] == "completed":
                break
            time.sleep(3)
            elapsed += 3
        
        return token
    
    def test_filter_by_category(self, setup_with_data):
        """GET /api/emerging/competences with category filter"""
        token = setup_with_data
        
        categories = ["tech_emergente", "hybride", "soft_skill_avancee", "methodologique", "sectorielle"]
        for category in categories:
            response = requests.get(f"{BASE_URL}/api/emerging/competences?token={token}&category={category}")
            assert response.status_code == 200
            data = response.json()
            # All returned competences should match the category filter
            for comp in data["competences"]:
                assert comp["categorie"] == category, f"Competence {comp['nom_principal']} has wrong category"
            print(f"Category '{category}': {data['total']} competences")
    
    def test_filter_by_min_score(self, setup_with_data):
        """GET /api/emerging/competences with min_score filter"""
        token = setup_with_data
        
        response = requests.get(f"{BASE_URL}/api/emerging/competences?token={token}&min_score=50")
        assert response.status_code == 200
        data = response.json()
        
        # All returned competences should have score >= 50
        for comp in data["competences"]:
            assert comp["score_emergence"] >= 50, f"Competence {comp['nom_principal']} has score below minimum"
        print(f"Competences with score >= 50: {data['total']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
