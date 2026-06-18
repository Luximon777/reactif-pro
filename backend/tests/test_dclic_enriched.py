"""
D'CLIC PRO Enriched Profile Tests
Tests the GPT-5.2 enriched profile with MBTI, DISC, Boussole, Vertus, RIASEC, 
Integrated Analysis, Cross Analysis, Ofman Quadrant, and Life Path
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Sample answers for testing
SAMPLE_ANSWERS = {
    "arche_1": "J'ai organisé un événement caritatif pour 200 personnes",
    "arche_2": "Les gens viennent me voir pour des conseils en organisation",
    "arche_3": "J'ai coordonné une équipe de 10 bénévoles",
    "arche_4": "J'ai aidé mon frère dans sa recherche d'emploi",
    "arche_5": "Président d'une association sportive pendant 3 ans",
    "arche_6": "J'ai surmonté une période de chômage difficile",
    "arche_7": "Je sais écouter et conseiller les autres",
    "arche_8": "J'ai appris la photographie en autodidacte",
    "arche_9": "Je suis efficace quand je dois résoudre des problèmes",
    "arche_10": "Je transmettrais la gestion de projet",
    "riasec_1": 5, "riasec_2": 4, "riasec_3": 4, "riasec_4": 5, "riasec_5": 4,
    "riasec_6": 5, "riasec_7": 3, "riasec_8": 5, "riasec_9": 5, "riasec_10": 4,
    "val_1": 5, "val_2": 5, "val_3": 4, "val_4": 5, "val_5": 4,
    "val_6": 5, "val_7": 5, "val_8": 4, "val_9": 5, "val_10": 4,
    "sep_1": 5, "sep_2": 4, "sep_3": 5, "sep_4": 4, "sep_5": 5,
    "sep_6": 5, "sep_7": 4, "sep_8": 4, "sep_9": 5, "sep_10": 5,
    "proj_1": "Consultant en management, Coach professionnel",
    "proj_2": "Comptable, Travail isolé",
    "proj_3": "personnes",
    "proj_4": "contact",
    "proj_5": "Un travail où j'accompagne les autres dans leur développement"
}


class TestDclicQuestionnaire:
    """Tests for GET /api/dclic/questionnaire"""
    
    def test_questionnaire_returns_200(self):
        """Questionnaire endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        assert response.status_code == 200
        print("✓ GET /api/dclic/questionnaire returns 200")
    
    def test_questionnaire_has_5_blocs(self):
        """Questionnaire has exactly 5 blocs"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        data = response.json()
        assert "blocs" in data
        assert len(data["blocs"]) == 5
        print("✓ Questionnaire has 5 blocs")
    
    def test_questionnaire_has_45_questions(self):
        """Questionnaire has 45 total questions"""
        response = requests.get(f"{BASE_URL}/api/dclic/questionnaire")
        data = response.json()
        total = sum(len(b.get("questions", [])) for b in data["blocs"])
        assert total == 45
        print(f"✓ Questionnaire has {total} questions (expected 45)")


class TestDclicSubmitEnriched:
    """Tests for POST /api/dclic/submit with GPT-5.2 enrichment"""
    
    @pytest.fixture(scope="class")
    def submit_response(self):
        """Submit answers and get enriched profile (shared across tests)"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": SAMPLE_ANSWERS},
            timeout=120  # GPT-5.2 call may take 15-30 seconds
        )
        assert response.status_code == 200
        return response.json()
    
    def test_submit_returns_success(self, submit_response):
        """Submit returns success=true"""
        assert submit_response.get("success") is True
        print("✓ POST /api/dclic/submit returns success=true")
    
    def test_submit_returns_access_code(self, submit_response):
        """Submit returns access_code"""
        assert "access_code" in submit_response
        assert len(submit_response["access_code"]) >= 8
        print(f"✓ Access code returned: {submit_response['access_code']}")
    
    def test_profile_has_mbti(self, submit_response):
        """Profile has MBTI (4 letter string)"""
        profile = submit_response.get("profile", {})
        assert "mbti" in profile
        assert len(profile["mbti"]) == 4
        assert all(c in "EINFSTJP" for c in profile["mbti"])
        print(f"✓ MBTI: {profile['mbti']}")
    
    def test_profile_has_disc(self, submit_response):
        """Profile has DISC and disc_label"""
        profile = submit_response.get("profile", {})
        assert "disc" in profile
        assert "disc_label" in profile
        print(f"✓ DISC: {profile['disc']} - {profile['disc_label']}")
    
    def test_profile_has_disc_scores(self, submit_response):
        """Profile has disc_scores with D/I/S/C"""
        profile = submit_response.get("profile", {})
        assert "disc_scores" in profile
        disc_scores = profile["disc_scores"]
        for key in ["D", "I", "S", "C"]:
            assert key in disc_scores
            assert 0 <= disc_scores[key] <= 100
        print(f"✓ DISC scores: D={disc_scores['D']}, I={disc_scores['I']}, S={disc_scores['S']}, C={disc_scores['C']}")
    
    def test_profile_has_compass(self, submit_response):
        """Profile has compass (Boussole) with 4 axes"""
        profile = submit_response.get("profile", {})
        assert "compass" in profile
        compass = profile["compass"]
        assert "axes" in compass
        assert len(compass["axes"]) == 4
        for axis in compass["axes"]:
            assert "name" in axis
            assert "dominant" in axis
            assert "pole_a" in axis
            assert "pole_b" in axis
            assert "insight" in axis
        print(f"✓ Compass has 4 axes: {[a['name'] for a in compass['axes']]}")
    
    def test_profile_has_vertus_profile(self, submit_response):
        """Profile has vertus_profile with 6 vertus scores"""
        profile = submit_response.get("profile", {})
        assert "vertus_profile" in profile
        vp = profile["vertus_profile"]
        assert "vertus_scores" in vp
        expected_vertus = ["sagesse", "courage", "humanite", "justice", "temperance", "transcendance"]
        for v in expected_vertus:
            assert v in vp["vertus_scores"]
            assert 0 <= vp["vertus_scores"][v] <= 100
        print(f"✓ Vertus profile with 6 scores: {list(vp['vertus_scores'].keys())}")
    
    def test_profile_has_vertu_data(self, submit_response):
        """Profile has vertu_data with cognition/conation/affection arrays"""
        profile = submit_response.get("profile", {})
        assert "vertu_data" in profile
        vd = profile["vertu_data"]
        assert "cognition" in vd and isinstance(vd["cognition"], list)
        assert "conation" in vd and isinstance(vd["conation"], list)
        assert "affection" in vd and isinstance(vd["affection"], list)
        print(f"✓ Vertu data: cognition={len(vd['cognition'])}, conation={len(vd['conation'])}, affection={len(vd['affection'])}")
    
    def test_profile_has_riasec_profile(self, submit_response):
        """Profile has riasec_profile with major/minor and scores 0-100"""
        profile = submit_response.get("profile", {})
        assert "riasec_profile" in profile
        rp = profile["riasec_profile"]
        assert "major" in rp
        assert "minor" in rp
        assert "scores" in rp
        for key in ["R", "I", "A", "S", "E", "C"]:
            assert key in rp["scores"]
            assert 0 <= rp["scores"][key] <= 100
        print(f"✓ RIASEC profile: {rp['major']}/{rp['minor']}")
    
    def test_profile_has_integrated_analysis(self, submit_response):
        """Profile has integrated_analysis with 3 levels"""
        profile = submit_response.get("profile", {})
        assert "integrated_analysis" in profile
        ia = profile["integrated_analysis"]
        assert "niveau_1_preuves" in ia
        assert "niveau_2_fonctionnement" in ia
        assert "niveau_3_regulation" in ia
        print("✓ Integrated analysis has 3 levels")
    
    def test_profile_has_cross_analysis(self, submit_response):
        """Profile has cross_analysis"""
        profile = submit_response.get("profile", {})
        assert "cross_analysis" in profile
        ca = profile["cross_analysis"]
        assert "has_cross_analysis" in ca
        print(f"✓ Cross analysis present: has_cross_analysis={ca['has_cross_analysis']}")
    
    def test_profile_has_ofman_quadrant(self, submit_response):
        """Profile has ofman_quadrant (array of 3 objects)"""
        profile = submit_response.get("profile", {})
        assert "ofman_quadrant" in profile
        oq = profile["ofman_quadrant"]
        assert isinstance(oq, list)
        assert len(oq) == 3
        for item in oq:
            assert "qualite" in item
            assert "piege" in item
            assert "defi" in item
            assert "allergie" in item
        print(f"✓ Ofman quadrant has 3 items: {[q['qualite'] for q in oq]}")
    
    def test_profile_has_life_path(self, submit_response):
        """Profile has life_path"""
        profile = submit_response.get("profile", {})
        assert "life_path" in profile
        lp = profile["life_path"]
        assert "label" in lp
        assert "strengths" in lp
        assert "watchouts" in lp
        assert "micro_actions" in lp
        print(f"✓ Life path: {lp['label']}")


class TestDclicResults:
    """Tests for GET /api/dclic/results/{code}"""
    
    @pytest.fixture(scope="class")
    def access_code(self):
        """Get access code from submit"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": SAMPLE_ANSWERS},
            timeout=120
        )
        return response.json().get("access_code")
    
    def test_results_returns_200(self, access_code):
        """Results endpoint returns 200 for valid code"""
        response = requests.get(f"{BASE_URL}/api/dclic/results/{access_code}")
        assert response.status_code == 200
        print(f"✓ GET /api/dclic/results/{access_code} returns 200")
    
    def test_results_returns_enriched_profile(self, access_code):
        """Results returns enriched profile with all fields"""
        response = requests.get(f"{BASE_URL}/api/dclic/results/{access_code}")
        profile = response.json()
        # Check all enriched fields are present
        required_fields = ["mbti", "disc", "disc_scores", "compass", "vertus_profile", 
                          "vertu_data", "riasec_profile", "integrated_analysis", 
                          "cross_analysis", "ofman_quadrant", "life_path"]
        for field in required_fields:
            assert field in profile, f"Missing field: {field}"
        print(f"✓ Results contains all enriched fields: {required_fields}")
    
    def test_results_returns_404_for_invalid_code(self):
        """Results returns 404 for invalid code"""
        response = requests.get(f"{BASE_URL}/api/dclic/results/INVALID-CODE-XYZ")
        assert response.status_code == 404
        print("✓ GET /api/dclic/results/INVALID-CODE returns 404")


class TestDclicValidation:
    """Tests for validation and edge cases"""
    
    def test_submit_rejects_incomplete_answers(self):
        """Submit rejects answers with < 15 responses"""
        response = requests.post(
            f"{BASE_URL}/api/dclic/submit",
            json={"answers": {"arche_1": "test", "riasec_1": 3}}
        )
        assert response.status_code == 400
        print("✓ Submit rejects incomplete answers (< 15)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
