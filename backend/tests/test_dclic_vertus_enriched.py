"""
D'CLIC PRO - Vertus Enriched Profile Tests
Tests for the new enriched vertus fields from dclic_referentiel.py (Seligman & Peterson 6 Vertus)
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Sample answers for D'CLIC PRO test (minimum 15 required)
SAMPLE_ANSWERS = {
    # Bloc 1: Archéologie (10 open_text questions)
    "arche_1": "J'ai organisé un événement caritatif pour 200 personnes, coordonnant bénévoles et logistique.",
    "arche_2": "Les gens viennent me voir pour des conseils sur leur carrière et pour résoudre des conflits.",
    "arche_3": "J'ai coordonné une équipe de 15 personnes pour un projet associatif pendant 6 mois.",
    "arche_4": "J'ai accompagné mon frère dans sa reconversion professionnelle, l'aidant à rédiger son CV.",
    "arche_5": "J'étais trésorier d'une association sportive pendant 3 ans.",
    "arche_6": "J'ai surmonté une période de chômage en me formant à de nouvelles compétences.",
    "arche_7": "Je sais écouter activement, organiser des réunions efficaces et négocier.",
    "arche_8": "J'ai appris l'anglais en autodidacte et la programmation Python.",
    "arche_9": "Je me sens efficace quand j'aide les autres à résoudre leurs problèmes.",
    "arche_10": "Je transmettrais la compétence d'écoute active et de communication bienveillante.",
    
    # Bloc 2: RIASEC (10 scale questions, 1-5)
    "riasec_1": 4,  # Résoudre problèmes concrets
    "riasec_2": 5,  # Comprendre fonctionnement
    "riasec_3": 4,  # Créer/imaginer
    "riasec_4": 5,  # Aider/accompagner (Social)
    "riasec_5": 4,  # Convaincre/négocier
    "riasec_6": 4,  # Organiser/planifier
    "riasec_7": 3,  # Travailler outils/machines
    "riasec_8": 5,  # Transmettre connaissances (Social)
    "riasec_9": 4,  # Prendre initiatives
    "riasec_10": 3, # Procédures précises
    
    # Bloc 3: Valeurs (10 scale questions, 1-5)
    "val_1": 5,  # Aider les autres (benevolence)
    "val_2": 4,  # Évoluer/apprendre (stimulation)
    "val_3": 3,  # Stabilité (securite)
    "val_4": 4,  # Autonomie
    "val_5": 3,  # Reconnaissance (reussite)
    "val_6": 5,  # Contribuer société (universalisme)
    "val_7": 4,  # Environnement respectueux (conformite)
    "val_8": 4,  # Innover (autonomie)
    "val_9": 5,  # Coopérer (benevolence)
    "val_10": 4, # Convictions (tradition)
    
    # Bloc 4: Savoir-être (10 scale questions, 1-5)
    "sep_1": 5,  # Respecter engagements (fiabilite)
    "sep_2": 4,  # S'adapter (adaptabilite)
    "sep_3": 4,  # Prendre initiatives
    "sep_4": 4,  # Rester calme (gestion_stress)
    "sep_5": 5,  # Travailler en équipe (cooperation)
    "sep_6": 5,  # Accepter remarques (ouverture)
    "sep_7": 4,  # Persévérer
    "sep_8": 4,  # Gérer plusieurs tâches (organisation)
    "sep_9": 5,  # Communiquer (communication)
    "sep_10": 4, # Chercher solutions (resolution)
    
    # Bloc 5: Projection (5 mixed questions)
    "proj_1": "Formateur, Coach professionnel, Conseiller en insertion",
    "proj_2": "Comptable, Développeur isolé, Travail répétitif",
    "proj_3": "personnes",
    "proj_4": "contact",
    "proj_5": "Un travail où j'aide les autres à se développer, avec une équipe bienveillante.",
}


class TestDclicQuestionnaireEndpoint:
    """Test GET /api/dclic/questionnaire"""
    
    def test_questionnaire_returns_200(self):
        """GET /api/dclic/questionnaire returns 200"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        assert response.status_code == 200
        
    def test_questionnaire_has_5_blocs_with_45_questions(self):
        """GET /api/dclic/questionnaire returns 5 blocs with 45 questions"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        data = response.json()
        
        assert "blocs" in data
        assert len(data["blocs"]) == 5
        
        total_questions = sum(len(bloc.get("questions", [])) for bloc in data["blocs"])
        assert total_questions == 45


class TestDclicSubmitEnrichedVertus:
    """Test POST /api/dclic/submit with enriched vertus fields"""
    
    @pytest.fixture(scope="class")
    def submit_response(self):
        """Submit D'CLIC PRO test and cache response (takes 30-60s due to GPT-5.2)"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": SAMPLE_ANSWERS},
            timeout=180  # 3 minutes timeout for GPT-5.2
        )
        return response
    
    def test_submit_returns_success(self, submit_response):
        """POST /api/dclic/submit returns success=true"""
        assert submit_response.status_code == 200
        data = submit_response.json()
        assert data.get("success") == True
        
    def test_submit_returns_access_code(self, submit_response):
        """POST /api/dclic/submit returns access_code"""
        data = submit_response.json()
        assert "access_code" in data
        assert len(data["access_code"]) >= 4
        
    def test_submit_returns_profile(self, submit_response):
        """POST /api/dclic/submit returns profile object"""
        data = submit_response.json()
        assert "profile" in data
        assert isinstance(data["profile"], dict)
        
    def test_vertus_profile_exists(self, submit_response):
        """POST /api/dclic/submit returns vertus_profile in profile"""
        data = submit_response.json()
        profile = data.get("profile", {})
        assert "vertus_profile" in profile
        
    def test_vertus_profile_has_dominant(self, submit_response):
        """vertus_profile has dominant (vertu code)"""
        data = submit_response.json()
        vp = data.get("profile", {}).get("vertus_profile", {})
        assert "dominant" in vp
        assert vp["dominant"] in ["sagesse", "courage", "humanite", "justice", "temperance", "transcendance"]
        
    def test_vertus_profile_has_dominant_name(self, submit_response):
        """vertus_profile has dominant_name (display name)"""
        data = submit_response.json()
        vp = data.get("profile", {}).get("vertus_profile", {})
        assert "dominant_name" in vp
        assert isinstance(vp["dominant_name"], str)
        assert len(vp["dominant_name"]) > 0
        
    def test_vertus_profile_has_description(self, submit_response):
        """vertus_profile has description"""
        data = submit_response.json()
        vp = data.get("profile", {}).get("vertus_profile", {})
        assert "description" in vp
        assert isinstance(vp["description"], str)
        
    def test_vertus_profile_has_citation(self, submit_response):
        """vertus_profile.citation is a non-empty string"""
        data = submit_response.json()
        vp = data.get("profile", {}).get("vertus_profile", {})
        assert "citation" in vp
        assert isinstance(vp["citation"], str)
        assert len(vp["citation"]) > 0, "citation should be a non-empty string"
        
    def test_vertus_profile_has_forces_caractere(self, submit_response):
        """vertus_profile has forces_caractere array"""
        data = submit_response.json()
        vp = data.get("profile", {}).get("vertus_profile", {})
        assert "forces_caractere" in vp
        assert isinstance(vp["forces_caractere"], list)
        assert len(vp["forces_caractere"]) > 0
        
    def test_vertus_profile_has_qualites_dominantes(self, submit_response):
        """vertus_profile has qualites_dominantes array"""
        data = submit_response.json()
        vp = data.get("profile", {}).get("vertus_profile", {})
        assert "qualites_dominantes" in vp
        assert isinstance(vp["qualites_dominantes"], list)
        
    def test_vertus_profile_has_competences_transferables(self, submit_response):
        """vertus_profile.competences_transferables is a non-empty array"""
        data = submit_response.json()
        vp = data.get("profile", {}).get("vertus_profile", {})
        assert "competences_transferables" in vp
        assert isinstance(vp["competences_transferables"], list)
        assert len(vp["competences_transferables"]) > 0, "competences_transferables should be a non-empty array"
        
    def test_vertus_profile_has_metiers_associes(self, submit_response):
        """vertus_profile.metiers_associes is a non-empty array"""
        data = submit_response.json()
        vp = data.get("profile", {}).get("vertus_profile", {})
        assert "metiers_associes" in vp
        assert isinstance(vp["metiers_associes"], list)
        assert len(vp["metiers_associes"]) > 0, "metiers_associes should be a non-empty array"
        
    def test_vertus_profile_has_penseurs(self, submit_response):
        """vertus_profile.penseurs has orientaux and occidentaux arrays"""
        data = submit_response.json()
        vp = data.get("profile", {}).get("vertus_profile", {})
        assert "penseurs" in vp
        assert isinstance(vp["penseurs"], dict)
        assert "orientaux" in vp["penseurs"]
        assert "occidentaux" in vp["penseurs"]
        assert isinstance(vp["penseurs"]["orientaux"], list)
        assert isinstance(vp["penseurs"]["occidentaux"], list)
        
    def test_vertus_profile_has_competences_oms(self, submit_response):
        """vertus_profile has competences_oms (CPS OMS) array"""
        data = submit_response.json()
        vp = data.get("profile", {}).get("vertus_profile", {})
        assert "competences_oms" in vp
        assert isinstance(vp["competences_oms"], list)
        
    def test_vertus_profile_has_vertus_scores(self, submit_response):
        """vertus_profile has vertus_scores with 6 vertus"""
        data = submit_response.json()
        vp = data.get("profile", {}).get("vertus_profile", {})
        assert "vertus_scores" in vp
        scores = vp["vertus_scores"]
        assert isinstance(scores, dict)
        expected_vertus = ["sagesse", "courage", "humanite", "justice", "temperance", "transcendance"]
        for vertu in expected_vertus:
            assert vertu in scores, f"Missing vertu score: {vertu}"


class TestDclicResultsEndpoint:
    """Test GET /api/dclic/results/{code}"""
    
    @pytest.fixture(scope="class")
    def access_code(self):
        """Get access code from submit"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": SAMPLE_ANSWERS},
            timeout=180
        )
        return response.json().get("access_code")
    
    def test_results_returns_200_with_valid_code(self, access_code):
        """GET /api/dclic/results/{code} returns 200 with valid code"""
        response = requests.get(f"{BASE_URL}/api/dclic/results/{access_code}")
        assert response.status_code == 200
        
    def test_results_returns_enriched_vertus_profile(self, access_code):
        """GET /api/dclic/results/{code} returns profile with enriched vertus fields"""
        response = requests.get(f"{BASE_URL}/api/dclic/results/{access_code}")
        data = response.json()
        
        # Check vertus_profile exists
        assert "vertus_profile" in data
        vp = data["vertus_profile"]
        
        # Check all enriched fields
        assert "citation" in vp, "Missing citation in vertus_profile"
        assert "competences_transferables" in vp, "Missing competences_transferables"
        assert "metiers_associes" in vp, "Missing metiers_associes"
        assert "penseurs" in vp, "Missing penseurs"
        assert "forces_caractere" in vp, "Missing forces_caractere"
        assert "competences_oms" in vp, "Missing competences_oms"
        
    def test_results_returns_404_for_invalid_code(self):
        """GET /api/dclic/results/{code} returns 404 for invalid code"""
        response = requests.get(f"{BASE_URL}/api/dclic/results/INVALID-CODE-123")
        assert response.status_code == 404


class TestDclicSubmitValidation:
    """Test POST /api/dclic/submit validation"""
    
    def test_submit_rejects_incomplete_answers(self):
        """POST /api/dclic/submit rejects answers < 15"""
        incomplete_answers = {
            "arche_1": "Test answer 1",
            "arche_2": "Test answer 2",
            "riasec_1": 3,
            "riasec_2": 4,
        }
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": incomplete_answers},
            timeout=30
        )
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
