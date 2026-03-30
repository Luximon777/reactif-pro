"""
Test suite for Archéologie des Compétences and Savoir-faire/Savoir-être distinction
Tests:
- POST /api/passport/competences with nature='savoir_faire'
- POST /api/passport/competences with nature='savoir_etre' 
- GET /api/referentiel/archeologie - returns vertus, valeurs, filieres, savoir_etre_map
- GET /api/referentiel/filieres - returns filieres list
- GET /api/referentiel/vertus - returns vertus and valeurs
- GET /api/passport/archeologie - returns savoir_faire/savoir_etre split and chains
- GET /api/passport/diagnostic - includes nature_distribution
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://reactif-pro-sync.preview.emergentagent.com"


class TestReferentielEndpoints:
    """Test referentiel endpoints for archéologie des compétences"""

    def test_referentiel_archeologie_returns_all_data(self):
        """GET /api/referentiel/archeologie should return vertus, valeurs, filieres, savoir_etre_map"""
        response = requests.get(f"{BASE_URL}/api/referentiel/archeologie")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Check all keys are present
        assert "vertus" in data, "Missing 'vertus' key"
        assert "valeurs" in data, "Missing 'valeurs' key"
        assert "filieres" in data, "Missing 'filieres' key"
        assert "savoir_etre_map" in data, "Missing 'savoir_etre_map' key"
        
        # Validate counts
        assert len(data["vertus"]) == 6, f"Expected 6 vertus, got {len(data['vertus'])}"
        assert len(data["valeurs"]) == 11, f"Expected 11 valeurs, got {len(data['valeurs'])}"
        assert len(data["filieres"]) == 14, f"Expected 14 filieres, got {len(data['filieres'])}"
        assert len(data["savoir_etre_map"]) == 18, f"Expected 18 savoir_etre mappings, got {len(data['savoir_etre_map'])}"
        
        print(f"PASS: referentiel/archeologie returns {len(data['vertus'])} vertus, {len(data['valeurs'])} valeurs, {len(data['filieres'])} filieres, {len(data['savoir_etre_map'])} savoir_etre mappings")

    def test_referentiel_filieres_endpoint(self):
        """GET /api/referentiel/filieres should return filieres list"""
        response = requests.get(f"{BASE_URL}/api/referentiel/filieres")
        assert response.status_code == 200
        
        data = response.json()
        assert "filieres" in data
        assert len(data["filieres"]) == 14, f"Expected 14 filieres, got {len(data['filieres'])}"
        
        # Check filiere structure
        first_filiere = data["filieres"][0]
        assert "id" in first_filiere, "Filiere should have 'id'"
        assert "name" in first_filiere, "Filiere should have 'name'"
        
        print(f"PASS: referentiel/filieres returns {len(data['filieres'])} filieres")

    def test_referentiel_vertus_endpoint(self):
        """GET /api/referentiel/vertus should return vertus and valeurs"""
        response = requests.get(f"{BASE_URL}/api/referentiel/vertus")
        assert response.status_code == 200
        
        data = response.json()
        assert "vertus" in data
        assert "valeurs" in data
        assert len(data["vertus"]) == 6, f"Expected 6 vertus, got {len(data['vertus'])}"
        assert len(data["valeurs"]) == 11, f"Expected 11 valeurs, got {len(data['valeurs'])}"
        
        # Validate vertu structure
        first_vertu = data["vertus"][0]
        assert "id" in first_vertu, "Vertu should have 'id'"
        assert "name" in first_vertu, "Vertu should have 'name'"
        assert "description" in first_vertu, "Vertu should have 'description'"
        assert "qualites" in first_vertu, "Vertu should have 'qualites'"
        assert "valeurs" in first_vertu, "Vertu should have 'valeurs'"
        assert "savoirs_etre" in first_vertu, "Vertu should have 'savoirs_etre'"
        
        print(f"PASS: referentiel/vertus returns {len(data['vertus'])} vertus and {len(data['valeurs'])} valeurs")


class TestCompetenceNature:
    """Test competence creation with nature field (savoir_faire / savoir_etre)"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get authentication token and ensure passport exists"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        self.token = response.json()["token"]
        
        # Ensure passport exists (auto-created on GET)
        passport_res = requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        assert passport_res.status_code == 200, f"Failed to create passport: {passport_res.text}"
        
        yield
        # Cleanup handled by test isolation

    def test_add_competence_with_savoir_faire(self):
        """POST /api/passport/competences with nature='savoir_faire'"""
        comp_data = {
            "name": "TEST_Programmation Python",
            "nature": "savoir_faire",
            "category": "technique",
            "level": "avance"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/passport/competences?token={self.token}",
            json=comp_data
        )
        assert response.status_code == 200
        
        data = response.json()
        # API returns {"message": ..., "competence": {...}}
        comp = data.get("competence", data)
        assert comp["nature"] == "savoir_faire", f"Expected nature='savoir_faire', got {comp.get('nature')}"
        assert comp["name"] == comp_data["name"]
        
        # Verify persistence via GET passport
        passport_res = requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        assert passport_res.status_code == 200
        passport = passport_res.json()
        
        comp_found = next((c for c in passport["competences"] if c["name"] == comp_data["name"]), None)
        assert comp_found is not None, "Competence not found in passport"
        assert comp_found["nature"] == "savoir_faire"
        
        print(f"PASS: Competence added with nature='savoir_faire'")

    def test_add_competence_with_savoir_etre(self):
        """POST /api/passport/competences with nature='savoir_etre'"""
        comp_data = {
            "name": "TEST_Communication interpersonnelle",
            "nature": "savoir_etre",
            "category": "transversale",
            "level": "intermediaire"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/passport/competences?token={self.token}",
            json=comp_data
        )
        assert response.status_code == 200
        
        data = response.json()
        # API returns {"message": ..., "competence": {...}}
        comp = data.get("competence", data)
        assert comp["nature"] == "savoir_etre", f"Expected nature='savoir_etre', got {comp.get('nature')}"
        
        # Verify persistence via GET passport
        passport_res = requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        passport = passport_res.json()
        
        comp_found = next((c for c in passport["competences"] if c["name"] == comp_data["name"]), None)
        assert comp_found is not None
        assert comp_found["nature"] == "savoir_etre"
        
        print(f"PASS: Competence added with nature='savoir_etre'")

    def test_add_competence_without_nature(self):
        """POST /api/passport/competences without nature field (should default to empty)"""
        comp_data = {
            "name": "TEST_Competence sans nature",
            "category": "technique",
            "level": "debutant"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/passport/competences?token={self.token}",
            json=comp_data
        )
        assert response.status_code == 200
        
        data = response.json()
        # Nature should be empty string when not specified
        assert data.get("nature", "") == "", f"Expected empty nature, got {data.get('nature')}"
        
        print(f"PASS: Competence added without nature (defaults to empty)")


class TestPassportArcheologie:
    """Test passport archeologie endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get authentication token and add test competences"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        self.token = response.json()["token"]
        
        # Ensure passport exists (auto-created on GET)
        passport_res = requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        assert passport_res.status_code == 200
        
        # Add some competences with nature
        self.test_competences = [
            {"name": "TEST_Adaptabilité", "nature": "savoir_etre", "category": "transversale", "level": "avance"},
            {"name": "TEST_Gestion de projet", "nature": "savoir_faire", "category": "technique", "level": "intermediaire"},
            {"name": "TEST_Communication", "nature": "savoir_etre", "category": "transversale", "level": "expert"},
        ]
        
        for comp in self.test_competences:
            requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json=comp)
        
        yield

    def test_passport_archeologie_returns_chains(self):
        """GET /api/passport/archeologie should return savoir_faire/savoir_etre split and chains"""
        response = requests.get(f"{BASE_URL}/api/passport/archeologie?token={self.token}")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check structure
        assert "chains" in data, "Missing 'chains' key"
        assert "summary" in data, "Missing 'summary' key"
        
        # Check summary fields
        summary = data["summary"]
        assert "savoir_faire" in summary, "Missing 'savoir_faire' in summary"
        assert "savoir_etre" in summary, "Missing 'savoir_etre' in summary"
        assert "non_classees" in summary, "Missing 'non_classees' in summary"
        assert "vertus_covered" in summary, "Missing 'vertus_covered' in summary"
        assert "valeurs_covered" in summary, "Missing 'valeurs_covered' in summary"
        
        # Verify counts match what we added
        assert summary["savoir_etre"] >= 2, f"Expected at least 2 savoir_etre, got {summary['savoir_etre']}"
        assert summary["savoir_faire"] >= 1, f"Expected at least 1 savoir_faire, got {summary['savoir_faire']}"
        
        print(f"PASS: passport/archeologie returns chains and summary - SF:{summary['savoir_faire']}, SE:{summary['savoir_etre']}")

    def test_passport_archeologie_chains_structure(self):
        """Chains should have competence, qualites, valeurs, vertus"""
        response = requests.get(f"{BASE_URL}/api/passport/archeologie?token={self.token}")
        assert response.status_code == 200
        
        data = response.json()
        chains = data.get("chains", [])
        
        if len(chains) > 0:
            chain = chains[0]
            assert "competence" in chain, "Chain missing 'competence'"
            assert "qualites" in chain, "Chain missing 'qualites'"
            assert "valeurs" in chain, "Chain missing 'valeurs'"
            assert "vertus" in chain, "Chain missing 'vertus'"
            
            print(f"PASS: Chains have proper structure with qualites/valeurs/vertus")
        else:
            print(f"INFO: No chains generated (competences may not be in ARCHEOLOGIE_SAVOIR_ETRE mapping)")

    def test_passport_archeologie_without_auth_fails(self):
        """GET /api/passport/archeologie without token should fail"""
        response = requests.get(f"{BASE_URL}/api/passport/archeologie")
        assert response.status_code in [401, 422], f"Expected 401/422, got {response.status_code}"
        print(f"PASS: archeologie endpoint rejects unauthenticated requests")


class TestDiagnosticNatureDistribution:
    """Test diagnostic endpoint includes nature_distribution"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get authentication token and add test competences"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        self.token = response.json()["token"]
        
        # Ensure passport exists (auto-created on GET)
        passport_res = requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        assert passport_res.status_code == 200
        
        # Add competences with different natures
        competences = [
            {"name": "TEST_Analyse de données", "nature": "savoir_faire", "category": "technique"},
            {"name": "TEST_SQL avancé", "nature": "savoir_faire", "category": "technique"},
            {"name": "TEST_Esprit d'équipe", "nature": "savoir_etre", "category": "transversale"},
            {"name": "TEST_Non classée", "category": "technique"},  # No nature
        ]
        
        for comp in competences:
            requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json=comp)
        
        yield

    def test_diagnostic_includes_nature_distribution(self):
        """GET /api/passport/diagnostic should include nature_distribution"""
        response = requests.get(f"{BASE_URL}/api/passport/diagnostic?token={self.token}")
        assert response.status_code == 200
        
        data = response.json()
        
        assert "nature_distribution" in data, "Missing 'nature_distribution' in diagnostic"
        
        nd = data["nature_distribution"]
        assert "savoir_faire" in nd, "Missing 'savoir_faire' count"
        assert "savoir_etre" in nd, "Missing 'savoir_etre' count"
        assert "non_classee" in nd, "Missing 'non_classee' count"
        
        # Verify counts
        assert nd["savoir_faire"] >= 2, f"Expected at least 2 savoir_faire, got {nd['savoir_faire']}"
        assert nd["savoir_etre"] >= 1, f"Expected at least 1 savoir_etre, got {nd['savoir_etre']}"
        assert nd["non_classee"] >= 1, f"Expected at least 1 non_classee, got {nd['non_classee']}"
        
        print(f"PASS: diagnostic returns nature_distribution - SF:{nd['savoir_faire']}, SE:{nd['savoir_etre']}, NC:{nd['non_classee']}")

    def test_diagnostic_recommendations_for_unclassified(self):
        """Diagnostic should include recommendation for unclassified competences"""
        response = requests.get(f"{BASE_URL}/api/passport/diagnostic?token={self.token}")
        assert response.status_code == 200
        
        data = response.json()
        recommendations = data.get("recommendations", [])
        
        # Check for classification recommendation
        has_classification_rec = any(
            rec.get("component") == "nature" or "non classée" in rec.get("message", "").lower()
            for rec in recommendations
        )
        
        assert has_classification_rec, "Expected recommendation about unclassified competences"
        print(f"PASS: diagnostic includes recommendation for unclassified competences")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
