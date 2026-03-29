"""
Test suite for Outils d'accompagnement V2 and Consent System
Tests:
- GET /api/partenaires/outils/fiches - 12 V2 fiches with correct phases
- PUT /api/partenaires/beneficiaires/{id}/bilan - Save V2 fiche data with decision blocks
- GET /api/partenaires/beneficiaires/{id}/bilan - Retrieve saved V2 fiche data
- POST /api/partenaires/consent - Create consent with 3 levels
- GET /api/partenaires/consent/{beneficiary_id} - Get consents with status
- DELETE /api/partenaires/consent/{consent_id} - Revoke consent
- GET /api/partenaires/consent-modules - Get 12 consent modules
- PUT /api/partenaires/consent/{consent_id} - Update consent
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
PARTENAIRE_EMAIL = "test@missionlocale.fr"
PARTENAIRE_PASSWORD = "Solerys777!"


class TestOutilsV2AndConsent:
    """Test suite for V2 Outils d'accompagnement and Consent system"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login as partenaire and get token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as partenaire
        login_response = self.session.post(f"{BASE_URL}/api/auth/login-pro", json={
            "pseudo": PARTENAIRE_EMAIL,
            "password": PARTENAIRE_PASSWORD
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.token = login_response.json().get("token")
        assert self.token, "No token received"
        
        # Get beneficiaires for testing
        ben_response = self.session.get(f"{BASE_URL}/api/partenaires/beneficiaires?token={self.token}")
        assert ben_response.status_code == 200
        self.beneficiaires = ben_response.json()
        assert len(self.beneficiaires) > 0, "No beneficiaires found for testing"
        self.test_beneficiary_id = self.beneficiaires[0]["id"]
        
        yield
        
        # Cleanup: No specific cleanup needed as we're using existing data

    # ===== FICHES V2 TESTS =====
    
    def test_get_fiches_returns_12_v2_fiches(self):
        """GET /api/partenaires/outils/fiches returns 12 V2 fiches"""
        response = self.session.get(f"{BASE_URL}/api/partenaires/outils/fiches?token={self.token}")
        
        assert response.status_code == 200, f"Failed: {response.text}"
        fiches = response.json()
        
        # Should have exactly 12 fiches
        assert len(fiches) == 12, f"Expected 12 fiches, got {len(fiches)}"
        
        # Verify fiche structure
        for fiche in fiches:
            assert "id" in fiche
            assert "phase" in fiche
            assert "phase_label" in fiche
            assert "number" in fiche
            assert "title" in fiche
            assert "description" in fiche
        
        print(f"PASSED: GET /api/partenaires/outils/fiches returns {len(fiches)} V2 fiches")

    def test_fiches_have_correct_phases(self):
        """Verify fiches are organized in 5 phases: diagnostic, bilan_pro, identite_valeurs, strategie, activation"""
        response = self.session.get(f"{BASE_URL}/api/partenaires/outils/fiches?token={self.token}")
        
        assert response.status_code == 200
        fiches = response.json()
        
        expected_phases = ["diagnostic", "bilan_pro", "identite_valeurs", "strategie", "activation"]
        actual_phases = list(set(f["phase"] for f in fiches))
        
        for phase in expected_phases:
            assert phase in actual_phases, f"Missing phase: {phase}"
        
        # Count fiches per phase
        phase_counts = {}
        for f in fiches:
            phase_counts[f["phase"]] = phase_counts.get(f["phase"], 0) + 1
        
        print(f"PASSED: Fiches organized in 5 phases: {phase_counts}")

    def test_fiche_12_is_plan_activation(self):
        """Verify fiche 12 is 'Mon plan d'activation'"""
        response = self.session.get(f"{BASE_URL}/api/partenaires/outils/fiches?token={self.token}")
        
        assert response.status_code == 200
        fiches = response.json()
        
        fiche_12 = next((f for f in fiches if f["number"] == 12), None)
        assert fiche_12 is not None, "Fiche 12 not found"
        assert fiche_12["id"] == "plan_activation", f"Fiche 12 id should be 'plan_activation', got '{fiche_12['id']}'"
        assert "plan d'activation" in fiche_12["title"].lower(), f"Fiche 12 title should contain 'plan d'activation', got '{fiche_12['title']}'"
        
        print(f"PASSED: Fiche 12 is '{fiche_12['title']}'")

    # ===== BILAN SAVE/GET TESTS =====
    
    def test_save_fiche_with_decision_blocks(self):
        """PUT /api/partenaires/beneficiaires/{id}/bilan saves V2 fiche data with decision blocks"""
        fiche_data = {
            "fiche_id": "positionnement_depart",
            "data": {
                "clarte": "7",
                "energie": "8",
                "urgence": "3 mois",
                "question_cle": "Test question cle",
                "attentes": "Test attentes",
                "_decision_je_decide": "Je decide de tester cette fonctionnalite",
                "_decision_je_arrete": "J'arrete de procrastiner",
                "_decision_je_teste": "Je teste le nouveau workflow"
            }
        }
        
        response = self.session.put(
            f"{BASE_URL}/api/partenaires/beneficiaires/{self.test_beneficiary_id}/bilan?token={self.token}",
            json=fiche_data
        )
        
        assert response.status_code == 200, f"Failed: {response.text}"
        result = response.json()
        assert "message" in result
        assert result.get("completed") >= 1
        
        print(f"PASSED: Saved fiche with decision blocks - {result}")

    def test_get_bilan_retrieves_saved_data(self):
        """GET /api/partenaires/beneficiaires/{id}/bilan retrieves saved V2 fiche data"""
        # First save some data
        fiche_data = {
            "fiche_id": "courbe_trajectoire",
            "data": {
                "pics_reussite": "Test pics reussite",
                "zones_rupture": "Test zones rupture",
                "_decision_je_decide": "Decision test",
                "_decision_je_arrete": "Arret test",
                "_decision_je_teste": "Test test"
            }
        }
        
        save_response = self.session.put(
            f"{BASE_URL}/api/partenaires/beneficiaires/{self.test_beneficiary_id}/bilan?token={self.token}",
            json=fiche_data
        )
        assert save_response.status_code == 200
        
        # Now retrieve
        get_response = self.session.get(
            f"{BASE_URL}/api/partenaires/beneficiaires/{self.test_beneficiary_id}/bilan?token={self.token}"
        )
        
        assert get_response.status_code == 200, f"Failed: {get_response.text}"
        bilan = get_response.json()
        
        # Verify saved data is present
        assert "courbe_trajectoire" in bilan, "Saved fiche not found in bilan"
        saved_fiche = bilan["courbe_trajectoire"]
        assert saved_fiche.get("pics_reussite") == "Test pics reussite"
        assert saved_fiche.get("_decision_je_decide") == "Decision test"
        assert saved_fiche.get("_decision_je_arrete") == "Arret test"
        assert saved_fiche.get("_decision_je_teste") == "Test test"
        
        print(f"PASSED: Retrieved bilan with decision blocks")

    def test_save_invalid_fiche_returns_400(self):
        """PUT /api/partenaires/beneficiaires/{id}/bilan with invalid fiche_id returns 400"""
        fiche_data = {
            "fiche_id": "invalid_fiche_id_xyz",
            "data": {"test": "data"}
        }
        
        response = self.session.put(
            f"{BASE_URL}/api/partenaires/beneficiaires/{self.test_beneficiary_id}/bilan?token={self.token}",
            json=fiche_data
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"PASSED: Invalid fiche_id returns 400")

    # ===== CONSENT TESTS =====
    
    def test_create_consent_synthese(self):
        """POST /api/partenaires/consent creates consent with level 'synthese'"""
        consent_data = {
            "beneficiary_id": self.test_beneficiary_id,
            "level": "synthese",
            "duration_days": 30,
            "purpose": "Test synthese consent"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/partenaires/consent?token={self.token}",
            json=consent_data
        )
        
        assert response.status_code == 200, f"Failed: {response.text}"
        consent = response.json()
        
        assert consent.get("level") == "synthese"
        assert consent.get("active") == True
        assert consent.get("beneficiary_id") == self.test_beneficiary_id
        assert "id" in consent
        assert "expires_at" in consent
        
        # Store for cleanup
        self.synthese_consent_id = consent["id"]
        
        print(f"PASSED: Created synthese consent - ID: {consent['id']}")

    def test_create_consent_modulaire(self):
        """POST /api/partenaires/consent creates consent with level 'modulaire' and modules"""
        consent_data = {
            "beneficiary_id": self.test_beneficiary_id,
            "level": "modulaire",
            "modules": ["profil_administratif", "competences_techniques", "soft_skills"],
            "duration_days": 60,
            "purpose": "Test modulaire consent"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/partenaires/consent?token={self.token}",
            json=consent_data
        )
        
        assert response.status_code == 200, f"Failed: {response.text}"
        consent = response.json()
        
        assert consent.get("level") == "modulaire"
        assert consent.get("active") == True
        assert len(consent.get("modules", [])) == 3
        assert "profil_administratif" in consent["modules"]
        
        self.modulaire_consent_id = consent["id"]
        
        print(f"PASSED: Created modulaire consent with 3 modules")

    def test_create_consent_complet_temporaire(self):
        """POST /api/partenaires/consent creates consent with level 'complet_temporaire'"""
        consent_data = {
            "beneficiary_id": self.test_beneficiary_id,
            "level": "complet_temporaire",
            "duration_days": 90,
            "purpose": "Test complet temporaire consent"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/partenaires/consent?token={self.token}",
            json=consent_data
        )
        
        assert response.status_code == 200, f"Failed: {response.text}"
        consent = response.json()
        
        assert consent.get("level") == "complet_temporaire"
        assert consent.get("active") == True
        # complet_temporaire should have all modules
        assert len(consent.get("modules", [])) == 12, f"Expected 12 modules, got {len(consent.get('modules', []))}"
        
        self.complet_consent_id = consent["id"]
        
        print(f"PASSED: Created complet_temporaire consent with all 12 modules")

    def test_create_consent_modulaire_without_modules_fails(self):
        """POST /api/partenaires/consent with modulaire level but no modules returns 400"""
        consent_data = {
            "beneficiary_id": self.test_beneficiary_id,
            "level": "modulaire",
            "duration_days": 30,
            "purpose": "Test without modules"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/partenaires/consent?token={self.token}",
            json=consent_data
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"PASSED: Modulaire without modules returns 400")

    def test_create_consent_invalid_level_fails(self):
        """POST /api/partenaires/consent with invalid level returns 400"""
        consent_data = {
            "beneficiary_id": self.test_beneficiary_id,
            "level": "invalid_level",
            "duration_days": 30,
            "purpose": "Test invalid level"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/partenaires/consent?token={self.token}",
            json=consent_data
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"PASSED: Invalid consent level returns 400")

    def test_get_consents_returns_status_and_remaining_days(self):
        """GET /api/partenaires/consent/{beneficiary_id} returns consents with status and remaining days"""
        response = self.session.get(
            f"{BASE_URL}/api/partenaires/consent/{self.test_beneficiary_id}?token={self.token}"
        )
        
        assert response.status_code == 200, f"Failed: {response.text}"
        consents = response.json()
        
        assert isinstance(consents, list)
        
        # Check active consents have status and remaining_days
        active_consents = [c for c in consents if c.get("active")]
        if active_consents:
            for c in active_consents:
                assert "status" in c, "Missing status field"
                assert c["status"] == "actif"
                assert "remaining_days" in c, "Missing remaining_days field"
        
        print(f"PASSED: GET consents returns {len(consents)} consents with status/remaining_days")

    def test_revoke_consent(self):
        """DELETE /api/partenaires/consent/{consent_id} revokes consent"""
        # First create a consent to revoke
        consent_data = {
            "beneficiary_id": self.test_beneficiary_id,
            "level": "synthese",
            "duration_days": 30,
            "purpose": "Test consent to revoke"
        }
        
        create_response = self.session.post(
            f"{BASE_URL}/api/partenaires/consent?token={self.token}",
            json=consent_data
        )
        assert create_response.status_code == 200
        consent_id = create_response.json()["id"]
        
        # Now revoke it
        revoke_response = self.session.delete(
            f"{BASE_URL}/api/partenaires/consent/{consent_id}?token={self.token}"
        )
        
        assert revoke_response.status_code == 200, f"Failed: {revoke_response.text}"
        
        # Verify it's revoked
        get_response = self.session.get(
            f"{BASE_URL}/api/partenaires/consent/{self.test_beneficiary_id}?token={self.token}"
        )
        consents = get_response.json()
        revoked = next((c for c in consents if c["id"] == consent_id), None)
        
        assert revoked is not None
        assert revoked.get("active") == False
        assert revoked.get("status") == "revoque"
        
        print(f"PASSED: Consent revoked successfully")

    def test_get_consent_modules_returns_12_modules(self):
        """GET /api/partenaires/consent-modules returns 12 available consent modules"""
        response = self.session.get(
            f"{BASE_URL}/api/partenaires/consent-modules?token={self.token}"
        )
        
        assert response.status_code == 200, f"Failed: {response.text}"
        modules = response.json()
        
        assert len(modules) == 12, f"Expected 12 modules, got {len(modules)}"
        
        # Verify module structure
        for module in modules:
            assert "id" in module
            assert "label" in module
        
        # Verify expected modules are present
        module_ids = [m["id"] for m in modules]
        expected_modules = [
            "profil_administratif", "parcours_formation", "experiences_professionnelles",
            "competences_techniques", "soft_skills", "valeurs_moteurs",
            "contraintes_adaptation", "projet_professionnel", "documents",
            "resultats_tests", "plan_action", "journal_progression"
        ]
        
        for expected in expected_modules:
            assert expected in module_ids, f"Missing module: {expected}"
        
        print(f"PASSED: GET consent-modules returns 12 modules")

    def test_update_consent(self):
        """PUT /api/partenaires/consent/{consent_id} updates consent"""
        # First create a consent
        consent_data = {
            "beneficiary_id": self.test_beneficiary_id,
            "level": "synthese",
            "duration_days": 30,
            "purpose": "Test consent to update"
        }
        
        create_response = self.session.post(
            f"{BASE_URL}/api/partenaires/consent?token={self.token}",
            json=consent_data
        )
        assert create_response.status_code == 200
        consent_id = create_response.json()["id"]
        
        # Update it
        update_data = {
            "duration_days": 60
        }
        
        update_response = self.session.put(
            f"{BASE_URL}/api/partenaires/consent/{consent_id}?token={self.token}",
            json=update_data
        )
        
        assert update_response.status_code == 200, f"Failed: {update_response.text}"
        updated = update_response.json()
        
        assert updated.get("duration_days") == 60
        
        print(f"PASSED: Consent updated successfully")

    def test_update_consent_deactivate(self):
        """PUT /api/partenaires/consent/{consent_id} can deactivate consent"""
        # First create a consent
        consent_data = {
            "beneficiary_id": self.test_beneficiary_id,
            "level": "synthese",
            "duration_days": 30,
            "purpose": "Test consent to deactivate"
        }
        
        create_response = self.session.post(
            f"{BASE_URL}/api/partenaires/consent?token={self.token}",
            json=consent_data
        )
        assert create_response.status_code == 200
        consent_id = create_response.json()["id"]
        
        # Deactivate it
        update_data = {
            "active": False
        }
        
        update_response = self.session.put(
            f"{BASE_URL}/api/partenaires/consent/{consent_id}?token={self.token}",
            json=update_data
        )
        
        assert update_response.status_code == 200, f"Failed: {update_response.text}"
        updated = update_response.json()
        
        assert updated.get("active") == False
        assert "revoked_at" in updated
        
        print(f"PASSED: Consent deactivated via update")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
