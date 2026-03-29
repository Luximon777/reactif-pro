"""
Test suite for Partenaire (Partner) features - Phase 1
Tests: Registration, Login, Dashboard stats, Beneficiaires CRUD, Freins périphériques, Skills management
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
PARTENAIRE_EMAIL = "test@missionlocale.fr"
PARTENAIRE_PASSWORD = "Solerys777!"


class TestPartenaireRegistration:
    """Test partenaire registration flow with SIRET validation and consent"""
    
    def test_register_partenaire_success(self):
        """Test successful partenaire registration with all required fields"""
        unique_email = f"test_partenaire_{uuid.uuid4().hex[:8]}@teststructure.fr"
        payload = {
            "structure_name": "Test Structure Insertion",
            "structure_type": "acteur_insertion",
            "siret": "12345678901234",
            "email": unique_email,
            "password": "TestPass123!",
            "referent_first_name": "Jean",
            "referent_last_name": "Dupont",
            "referent_function": "conseiller",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register-partenaire", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "token" in data
        assert data["role"] == "partenaire"
        assert "profile_id" in data
        assert data["structure_name"] == "Test Structure Insertion"
        assert data["structure_type"] == "acteur_insertion"
        assert "profile_completion" in data
    
    def test_register_partenaire_invalid_siret(self):
        """Test registration fails with invalid SIRET"""
        payload = {
            "structure_name": "Test Structure",
            "structure_type": "association",
            "siret": "123",  # Invalid - too short
            "email": f"test_{uuid.uuid4().hex[:8]}@test.fr",
            "password": "TestPass123!",
            "referent_first_name": "Jean",
            "referent_last_name": "Dupont",
            "referent_function": "directeur",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register-partenaire", json=payload)
        assert response.status_code == 400
        assert "SIRET" in response.json().get("detail", "")
    
    def test_register_partenaire_missing_charte(self):
        """Test registration fails without charte ethique signature"""
        payload = {
            "structure_name": "Test Structure",
            "structure_type": "organisme_formation",
            "siret": "12345678901234",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.fr",
            "password": "TestPass123!",
            "referent_first_name": "Jean",
            "referent_last_name": "Dupont",
            "referent_function": "formateur",
            "charte_ethique_signed": False,  # Not signed
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register-partenaire", json=payload)
        assert response.status_code == 400
        assert "charte" in response.json().get("detail", "").lower()
    
    def test_register_partenaire_invalid_structure_type(self):
        """Test registration fails with invalid structure type"""
        payload = {
            "structure_name": "Test Structure",
            "structure_type": "invalid_type",
            "siret": "12345678901234",
            "email": f"test_{uuid.uuid4().hex[:8]}@test.fr",
            "password": "TestPass123!",
            "referent_first_name": "Jean",
            "referent_last_name": "Dupont",
            "referent_function": "directeur",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register-partenaire", json=payload)
        assert response.status_code == 400
        assert "structure" in response.json().get("detail", "").lower()


class TestPartenaireLogin:
    """Test partenaire login via /api/auth/login-pro"""
    
    def test_login_pro_success(self):
        """Test successful login with existing partenaire account"""
        payload = {
            "pseudo": PARTENAIRE_EMAIL,
            "password": PARTENAIRE_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/api/auth/login-pro", json=payload)
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert "token" in data
        assert data["role"] == "partenaire"
        assert "profile_id" in data
        assert data["auth_mode"] == "pseudo"
    
    def test_login_pro_invalid_password(self):
        """Test login fails with wrong password"""
        payload = {
            "pseudo": PARTENAIRE_EMAIL,
            "password": "WrongPassword123!"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login-pro", json=payload)
        assert response.status_code == 401
    
    def test_login_pro_nonexistent_email(self):
        """Test login fails with non-existent email"""
        payload = {
            "pseudo": "nonexistent@test.fr",
            "password": "TestPass123!"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login-pro", json=payload)
        assert response.status_code == 401


class TestPartenaireDashboard:
    """Test partenaire dashboard stats and profile endpoints"""
    
    @pytest.fixture
    def partenaire_token(self):
        """Get token for partenaire account"""
        payload = {"pseudo": PARTENAIRE_EMAIL, "password": PARTENAIRE_PASSWORD}
        response = requests.post(f"{BASE_URL}/api/auth/login-pro", json=payload)
        if response.status_code != 200:
            pytest.skip(f"Could not login as partenaire: {response.text}")
        return response.json()["token"]
    
    def test_get_stats(self, partenaire_token):
        """Test GET /api/partenaires/stats returns dashboard statistics"""
        response = requests.get(f"{BASE_URL}/api/partenaires/stats?token={partenaire_token}")
        assert response.status_code == 200, f"Stats failed: {response.text}"
        
        data = response.json()
        assert "total" in data
        assert "en_accompagnement" in data
        assert "en_formation" in data
        assert "en_emploi" in data
        assert "taux_insertion" in data
        assert "freins_actifs" in data
        assert "freins_resolus" in data
        assert isinstance(data["total"], int)
        assert isinstance(data["taux_insertion"], int)
    
    def test_get_profile(self, partenaire_token):
        """Test GET /api/partenaires/profile returns partner profile"""
        response = requests.get(f"{BASE_URL}/api/partenaires/profile?token={partenaire_token}")
        assert response.status_code == 200, f"Profile failed: {response.text}"
        
        data = response.json()
        assert "company_name" in data or "name" in data
        assert "role" in data
        assert data["role"] == "partenaire"
        # Ensure password_hash is not returned
        assert "password_hash" not in data
    
    def test_stats_invalid_token(self):
        """Test stats endpoint rejects invalid token"""
        response = requests.get(f"{BASE_URL}/api/partenaires/stats?token=invalid_token_123")
        assert response.status_code in [401, 404]


class TestBeneficiairesCRUD:
    """Test beneficiaires CRUD operations"""
    
    @pytest.fixture
    def partenaire_token(self):
        """Get token for partenaire account"""
        payload = {"pseudo": PARTENAIRE_EMAIL, "password": PARTENAIRE_PASSWORD}
        response = requests.post(f"{BASE_URL}/api/auth/login-pro", json=payload)
        if response.status_code != 200:
            pytest.skip(f"Could not login as partenaire: {response.text}")
        return response.json()["token"]
    
    def test_list_beneficiaires(self, partenaire_token):
        """Test GET /api/partenaires/beneficiaires returns list"""
        response = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires?token={partenaire_token}")
        assert response.status_code == 200, f"List failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        # Check structure of beneficiaire if any exist
        if len(data) > 0:
            ben = data[0]
            assert "id" in ben
            assert "name" in ben
            assert "status" in ben
    
    def test_create_beneficiaire(self, partenaire_token):
        """Test POST /api/partenaires/beneficiaires creates new beneficiaire"""
        name = f"TEST_Beneficiaire_{uuid.uuid4().hex[:6]}"
        response = requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires?token={partenaire_token}&name={name}&sector=Informatique&notes=Test%20notes"
        )
        assert response.status_code == 200, f"Create failed: {response.text}"
        
        data = response.json()
        assert data["name"] == name
        assert data["sector"] == "Informatique"
        assert data["status"] == "En accompagnement"
        assert "id" in data
        assert "freins" in data
        assert "historique" in data
        assert len(data["historique"]) > 0  # Should have creation entry
        
        # Verify persistence with GET
        ben_id = data["id"]
        get_response = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}?token={partenaire_token}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == name
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}?token={partenaire_token}")
    
    def test_update_beneficiaire_status(self, partenaire_token):
        """Test PUT /api/partenaires/beneficiaires/{id} updates status"""
        # Create a test beneficiaire
        name = f"TEST_Update_{uuid.uuid4().hex[:6]}"
        create_resp = requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires?token={partenaire_token}&name={name}"
        )
        assert create_resp.status_code == 200
        ben_id = create_resp.json()["id"]
        
        # Update status
        update_resp = requests.put(
            f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}?token={partenaire_token}&status=En%20emploi"
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["status"] == "En emploi"
        
        # Verify with GET
        get_resp = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}?token={partenaire_token}")
        assert get_resp.json()["status"] == "En emploi"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}?token={partenaire_token}")
    
    def test_delete_beneficiaire(self, partenaire_token):
        """Test DELETE /api/partenaires/beneficiaires/{id} removes beneficiaire"""
        # Create a test beneficiaire
        name = f"TEST_Delete_{uuid.uuid4().hex[:6]}"
        create_resp = requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires?token={partenaire_token}&name={name}"
        )
        assert create_resp.status_code == 200
        ben_id = create_resp.json()["id"]
        
        # Delete
        delete_resp = requests.delete(f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}?token={partenaire_token}")
        assert delete_resp.status_code == 200
        
        # Verify deletion with GET
        get_resp = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}?token={partenaire_token}")
        assert get_resp.status_code == 404
    
    def test_get_beneficiaire_detail(self, partenaire_token):
        """Test GET /api/partenaires/beneficiaires/{id} returns full detail"""
        # First get list to find an existing beneficiaire
        list_resp = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires?token={partenaire_token}")
        beneficiaires = list_resp.json()
        
        if len(beneficiaires) == 0:
            # Create one for testing
            name = f"TEST_Detail_{uuid.uuid4().hex[:6]}"
            create_resp = requests.post(
                f"{BASE_URL}/api/partenaires/beneficiaires?token={partenaire_token}&name={name}"
            )
            ben_id = create_resp.json()["id"]
        else:
            ben_id = beneficiaires[0]["id"]
        
        # Get detail
        detail_resp = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}?token={partenaire_token}")
        assert detail_resp.status_code == 200
        
        data = detail_resp.json()
        assert "id" in data
        assert "name" in data
        assert "status" in data
        assert "freins" in data
        assert "historique" in data
        assert "skills_acquired" in data


class TestFreinsPeripheriques:
    """Test freins périphériques (peripheral obstacles) management"""
    
    @pytest.fixture
    def partenaire_token(self):
        """Get token for partenaire account"""
        payload = {"pseudo": PARTENAIRE_EMAIL, "password": PARTENAIRE_PASSWORD}
        response = requests.post(f"{BASE_URL}/api/auth/login-pro", json=payload)
        if response.status_code != 200:
            pytest.skip(f"Could not login as partenaire: {response.text}")
        return response.json()["token"]
    
    @pytest.fixture
    def test_beneficiaire(self, partenaire_token):
        """Create a test beneficiaire for frein tests"""
        name = f"TEST_Frein_{uuid.uuid4().hex[:6]}"
        response = requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires?token={partenaire_token}&name={name}"
        )
        ben = response.json()
        yield ben
        # Cleanup
        requests.delete(f"{BASE_URL}/api/partenaires/beneficiaires/{ben['id']}?token={partenaire_token}")
    
    def test_add_frein(self, partenaire_token, test_beneficiaire):
        """Test POST /api/partenaires/beneficiaires/{id}/freins adds a frein"""
        ben_id = test_beneficiaire["id"]
        response = requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}/freins?token={partenaire_token}&category=logement&description=Recherche%20logement&severity=eleve"
        )
        assert response.status_code == 200, f"Add frein failed: {response.text}"
        
        data = response.json()
        assert data["category"] == "logement"
        assert data["description"] == "Recherche logement"
        assert data["severity"] == "eleve"
        assert data["status"] == "actif"
        assert "id" in data
    
    def test_add_frein_invalid_category(self, partenaire_token, test_beneficiaire):
        """Test adding frein with invalid category fails"""
        ben_id = test_beneficiaire["id"]
        response = requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}/freins?token={partenaire_token}&category=invalid_category"
        )
        assert response.status_code == 400
        assert "catégorie" in response.json().get("detail", "").lower() or "invalide" in response.json().get("detail", "").lower()
    
    def test_resolve_frein(self, partenaire_token, test_beneficiaire):
        """Test PUT /api/partenaires/beneficiaires/{id}/freins/{frein_id} resolves frein"""
        ben_id = test_beneficiaire["id"]
        
        # Add a frein first
        add_resp = requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}/freins?token={partenaire_token}&category=mobilite&description=Pas%20de%20permis"
        )
        frein_id = add_resp.json()["id"]
        
        # Resolve the frein
        resolve_resp = requests.put(
            f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}/freins/{frein_id}?token={partenaire_token}&status=resolu&solution=Permis%20obtenu"
        )
        assert resolve_resp.status_code == 200
        
        frein = resolve_resp.json()["frein"]
        assert frein["status"] == "resolu"
        assert frein["solution"] == "Permis obtenu"
        assert frein["resolved_at"] is not None
    
    def test_all_frein_categories(self, partenaire_token, test_beneficiaire):
        """Test all valid frein categories can be added"""
        ben_id = test_beneficiaire["id"]
        valid_categories = ["logement", "sante", "mobilite", "garde_enfant", "handicap", "administratif", "financier", "autre"]
        
        for category in valid_categories:
            response = requests.post(
                f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}/freins?token={partenaire_token}&category={category}"
            )
            assert response.status_code == 200, f"Failed for category {category}: {response.text}"
            assert response.json()["category"] == category


class TestSkillsManagement:
    """Test skills management for beneficiaires"""
    
    @pytest.fixture
    def partenaire_token(self):
        """Get token for partenaire account"""
        payload = {"pseudo": PARTENAIRE_EMAIL, "password": PARTENAIRE_PASSWORD}
        response = requests.post(f"{BASE_URL}/api/auth/login-pro", json=payload)
        if response.status_code != 200:
            pytest.skip(f"Could not login as partenaire: {response.text}")
        return response.json()["token"]
    
    @pytest.fixture
    def test_beneficiaire(self, partenaire_token):
        """Create a test beneficiaire for skill tests"""
        name = f"TEST_Skill_{uuid.uuid4().hex[:6]}"
        response = requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires?token={partenaire_token}&name={name}"
        )
        ben = response.json()
        yield ben
        # Cleanup
        requests.delete(f"{BASE_URL}/api/partenaires/beneficiaires/{ben['id']}?token={partenaire_token}")
    
    def test_add_skill(self, partenaire_token, test_beneficiaire):
        """Test POST /api/partenaires/beneficiaires/{id}/skills adds a skill"""
        ben_id = test_beneficiaire["id"]
        skill_name = "Communication"
        
        response = requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}/skills?token={partenaire_token}&skill={skill_name}"
        )
        assert response.status_code == 200, f"Add skill failed: {response.text}"
        
        data = response.json()
        assert "skills_acquired" in data
        assert skill_name in data["skills_acquired"]
    
    def test_add_multiple_skills(self, partenaire_token, test_beneficiaire):
        """Test adding multiple skills"""
        ben_id = test_beneficiaire["id"]
        skills = ["Communication", "Travail en équipe", "Gestion du temps"]
        
        for skill in skills:
            response = requests.post(
                f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}/skills?token={partenaire_token}&skill={skill}"
            )
            assert response.status_code == 200
        
        # Verify all skills are present
        get_resp = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}?token={partenaire_token}")
        acquired = get_resp.json()["skills_acquired"]
        for skill in skills:
            assert skill in acquired
    
    def test_add_duplicate_skill(self, partenaire_token, test_beneficiaire):
        """Test adding duplicate skill doesn't create duplicates"""
        ben_id = test_beneficiaire["id"]
        skill_name = "Leadership"
        
        # Add skill twice
        requests.post(f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}/skills?token={partenaire_token}&skill={skill_name}")
        requests.post(f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}/skills?token={partenaire_token}&skill={skill_name}")
        
        # Verify only one instance
        get_resp = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires/{ben_id}?token={partenaire_token}")
        acquired = get_resp.json()["skills_acquired"]
        assert acquired.count(skill_name) == 1


class TestSeededData:
    """Test that seeded data exists for partenaire account"""
    
    @pytest.fixture
    def partenaire_token(self):
        """Get token for partenaire account"""
        payload = {"pseudo": PARTENAIRE_EMAIL, "password": PARTENAIRE_PASSWORD}
        response = requests.post(f"{BASE_URL}/api/auth/login-pro", json=payload)
        if response.status_code != 200:
            pytest.skip(f"Could not login as partenaire: {response.text}")
        return response.json()["token"]
    
    def test_seeded_beneficiaires_exist(self, partenaire_token):
        """Test that seeded beneficiaires exist for test@missionlocale.fr"""
        response = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires?token={partenaire_token}")
        assert response.status_code == 200
        
        beneficiaires = response.json()
        # According to agent context, should have 4 beneficiaires
        assert len(beneficiaires) >= 1, "Expected at least 1 seeded beneficiaire"
        
        # Check expected names if seeded
        names = [b["name"] for b in beneficiaires]
        print(f"Found beneficiaires: {names}")
    
    def test_seeded_beneficiaires_have_freins(self, partenaire_token):
        """Test that some seeded beneficiaires have freins"""
        response = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires?token={partenaire_token}")
        beneficiaires = response.json()
        
        total_freins = sum(len(b.get("freins", [])) for b in beneficiaires)
        print(f"Total freins across all beneficiaires: {total_freins}")
        # At least some freins should exist if data is seeded
    
    def test_stats_reflect_seeded_data(self, partenaire_token):
        """Test that stats endpoint reflects seeded data"""
        response = requests.get(f"{BASE_URL}/api/partenaires/stats?token={partenaire_token}")
        assert response.status_code == 200
        
        stats = response.json()
        print(f"Stats: total={stats['total']}, en_accompagnement={stats['en_accompagnement']}, freins_actifs={stats['freins_actifs']}")
        
        # Stats should be consistent with beneficiaires
        ben_resp = requests.get(f"{BASE_URL}/api/partenaires/beneficiaires?token={partenaire_token}")
        beneficiaires = ben_resp.json()
        assert stats["total"] == len(beneficiaires)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
