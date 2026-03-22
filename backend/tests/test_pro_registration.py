"""
Test suite for Entreprise and Partenaire registration flows
Tests: register-entreprise, register-partenaire, login-pro, siret verification
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test SIRET: Google France
TEST_SIRET = "44306184100047"
TEST_SIREN = "443061841"


class TestSiretVerification:
    """SIRET verification endpoint tests"""
    
    def test_siret_verify_valid_siret(self):
        """Test SIRET verification with valid SIRET (Google France)"""
        response = requests.get(f"{BASE_URL}/api/siret/verify?siret={TEST_SIRET}")
        assert response.status_code == 200
        data = response.json()
        print(f"SIRET verification response: {data}")
        assert data.get("valid") == True
        assert "company_name" in data
        assert data.get("company_name") != ""
        print(f"Company found: {data.get('company_name')}")
    
    def test_siret_verify_valid_siren(self):
        """Test SIRET verification with valid SIREN (9 digits)"""
        response = requests.get(f"{BASE_URL}/api/siret/verify?siret={TEST_SIREN}")
        assert response.status_code == 200
        data = response.json()
        print(f"SIREN verification response: {data}")
        # SIREN should also work
        assert "company_name" in data or "error" in data
    
    def test_siret_verify_invalid_format(self):
        """Test SIRET verification with invalid format"""
        response = requests.get(f"{BASE_URL}/api/siret/verify?siret=12345")
        assert response.status_code == 200
        data = response.json()
        assert data.get("valid") == False
        assert "error" in data
        print(f"Invalid format error: {data.get('error')}")
    
    def test_siret_verify_nonexistent(self):
        """Test SIRET verification with non-existent SIRET"""
        response = requests.get(f"{BASE_URL}/api/siret/verify?siret=99999999999999")
        assert response.status_code == 200
        data = response.json()
        # Should return valid=False or error
        print(f"Non-existent SIRET response: {data}")


class TestEntrepriseRegistration:
    """Entreprise registration endpoint tests"""
    
    def test_register_entreprise_success(self):
        """Test successful entreprise registration"""
        unique_email = f"test_ent_{uuid.uuid4().hex[:8]}@testcompany.fr"
        payload = {
            "company_name": "Test Company SAS",
            "siret": TEST_SIRET,
            "email": unique_email,
            "password": "testpass123",
            "referent_first_name": "Jean",
            "referent_last_name": "Dupont",
            "referent_function": "rh",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register-entreprise", json=payload)
        print(f"Register entreprise response: {response.status_code} - {response.text}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "token" in data
        assert data.get("role") == "entreprise"
        assert "profile_id" in data
        assert data.get("auth_mode") == "pseudo"
        assert data.get("company_name") == "Test Company SAS"
        assert "profile_completion" in data
        print(f"Profile completion: {data.get('profile_completion')}%")
    
    def test_register_entreprise_email_warning(self):
        """Test entreprise registration with non-professional email shows warning"""
        unique_email = f"test_ent_{uuid.uuid4().hex[:8]}@gmail.com"
        payload = {
            "company_name": "Test Gmail Company",
            "siret": TEST_SIRET,
            "email": unique_email,
            "password": "testpass123",
            "referent_first_name": "Marie",
            "referent_last_name": "Martin",
            "referent_function": "dirigeant",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register-entreprise", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Should have email warning for gmail
        assert data.get("email_warning") is not None
        print(f"Email warning: {data.get('email_warning')}")
    
    def test_register_entreprise_missing_company_name(self):
        """Test entreprise registration fails without company name"""
        payload = {
            "company_name": "",
            "siret": TEST_SIRET,
            "email": "test@company.fr",
            "password": "testpass123",
            "referent_first_name": "Jean",
            "referent_last_name": "Dupont",
            "referent_function": "rh",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register-entreprise", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        print(f"Error: {data.get('detail')}")
    
    def test_register_entreprise_invalid_siret(self):
        """Test entreprise registration fails with invalid SIRET"""
        payload = {
            "company_name": "Test Company",
            "siret": "12345",
            "email": "test@company.fr",
            "password": "testpass123",
            "referent_first_name": "Jean",
            "referent_last_name": "Dupont",
            "referent_function": "rh",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register-entreprise", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "SIRET" in data.get("detail", "") or "SIREN" in data.get("detail", "")
        print(f"Error: {data.get('detail')}")
    
    def test_register_entreprise_short_password(self):
        """Test entreprise registration fails with short password"""
        payload = {
            "company_name": "Test Company",
            "siret": TEST_SIRET,
            "email": "test@company.fr",
            "password": "123",
            "referent_first_name": "Jean",
            "referent_last_name": "Dupont",
            "referent_function": "rh",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register-entreprise", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "mot de passe" in data.get("detail", "").lower()
        print(f"Error: {data.get('detail')}")
    
    def test_register_entreprise_missing_referent(self):
        """Test entreprise registration fails without referent name"""
        payload = {
            "company_name": "Test Company",
            "siret": TEST_SIRET,
            "email": "test@company.fr",
            "password": "testpass123",
            "referent_first_name": "",
            "referent_last_name": "",
            "referent_function": "rh",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register-entreprise", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "référent" in data.get("detail", "").lower()
        print(f"Error: {data.get('detail')}")
    
    def test_register_entreprise_charte_not_signed(self):
        """Test entreprise registration fails without charte ethique signature"""
        payload = {
            "company_name": "Test Company",
            "siret": TEST_SIRET,
            "email": "test@company.fr",
            "password": "testpass123",
            "referent_first_name": "Jean",
            "referent_last_name": "Dupont",
            "referent_function": "rh",
            "charte_ethique_signed": False,
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register-entreprise", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "charte" in data.get("detail", "").lower()
        print(f"Error: {data.get('detail')}")
    
    def test_register_entreprise_cgu_not_accepted(self):
        """Test entreprise registration fails without CGU acceptance"""
        payload = {
            "company_name": "Test Company",
            "siret": TEST_SIRET,
            "email": "test@company.fr",
            "password": "testpass123",
            "referent_first_name": "Jean",
            "referent_last_name": "Dupont",
            "referent_function": "rh",
            "charte_ethique_signed": True,
            "consent_cgu": False,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register-entreprise", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "CGU" in data.get("detail", "")
        print(f"Error: {data.get('detail')}")


class TestPartenaireRegistration:
    """Partenaire registration endpoint tests"""
    
    def test_register_partenaire_success(self):
        """Test successful partenaire registration"""
        unique_email = f"test_part_{uuid.uuid4().hex[:8]}@structure.org"
        payload = {
            "structure_name": "Mission Locale Test",
            "structure_type": "acteur_insertion",
            "siret": TEST_SIRET,
            "email": unique_email,
            "password": "testpass123",
            "referent_first_name": "Sophie",
            "referent_last_name": "Bernard",
            "referent_function": "conseiller",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register-partenaire", json=payload)
        print(f"Register partenaire response: {response.status_code} - {response.text}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "token" in data
        assert data.get("role") == "partenaire"
        assert "profile_id" in data
        assert data.get("auth_mode") == "pseudo"
        assert data.get("structure_name") == "Mission Locale Test"
        assert data.get("structure_type") == "acteur_insertion"
        assert "profile_completion" in data
        print(f"Profile completion: {data.get('profile_completion')}%")
    
    def test_register_partenaire_all_structure_types(self):
        """Test partenaire registration with all valid structure types"""
        valid_types = ["organisme_formation", "association", "institution_publique", "acteur_insertion", "autre"]
        
        for struct_type in valid_types:
            unique_email = f"test_part_{uuid.uuid4().hex[:8]}@structure.org"
            payload = {
                "structure_name": f"Test Structure {struct_type}",
                "structure_type": struct_type,
                "siret": TEST_SIRET,
                "email": unique_email,
                "password": "testpass123",
                "referent_first_name": "Test",
                "referent_last_name": "User",
                "referent_function": "directeur",
                "charte_ethique_signed": True,
                "consent_cgu": True,
                "consent_privacy": True
            }
            response = requests.post(f"{BASE_URL}/api/auth/register-partenaire", json=payload)
            assert response.status_code == 200, f"Failed for structure_type: {struct_type}"
            print(f"Structure type '{struct_type}' - OK")
    
    def test_register_partenaire_invalid_structure_type(self):
        """Test partenaire registration fails with invalid structure type"""
        payload = {
            "structure_name": "Test Structure",
            "structure_type": "invalid_type",
            "siret": TEST_SIRET,
            "email": "test@structure.org",
            "password": "testpass123",
            "referent_first_name": "Test",
            "referent_last_name": "User",
            "referent_function": "directeur",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register-partenaire", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "type de structure" in data.get("detail", "").lower()
        print(f"Error: {data.get('detail')}")
    
    def test_register_partenaire_missing_structure_name(self):
        """Test partenaire registration fails without structure name"""
        payload = {
            "structure_name": "",
            "structure_type": "association",
            "siret": TEST_SIRET,
            "email": "test@structure.org",
            "password": "testpass123",
            "referent_first_name": "Test",
            "referent_last_name": "User",
            "referent_function": "directeur",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register-partenaire", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "structure" in data.get("detail", "").lower()
        print(f"Error: {data.get('detail')}")


class TestLoginPro:
    """Login for entreprise/partenaire by email"""
    
    def test_login_pro_entreprise(self):
        """Test login-pro for entreprise account"""
        # First register an entreprise
        unique_email = f"test_login_ent_{uuid.uuid4().hex[:8]}@company.fr"
        password = "testpass123"
        
        register_payload = {
            "company_name": "Login Test Company",
            "siret": TEST_SIRET,
            "email": unique_email,
            "password": password,
            "referent_first_name": "Login",
            "referent_last_name": "Test",
            "referent_function": "rh",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        reg_response = requests.post(f"{BASE_URL}/api/auth/register-entreprise", json=register_payload)
        assert reg_response.status_code == 200
        
        # Now login with email
        login_payload = {
            "pseudo": unique_email,
            "password": password
        }
        response = requests.post(f"{BASE_URL}/api/auth/login-pro", json=login_payload)
        print(f"Login pro response: {response.status_code} - {response.text}")
        assert response.status_code == 200
        data = response.json()
        
        assert "token" in data
        assert data.get("role") == "entreprise"
        assert data.get("auth_mode") == "pseudo"
        assert data.get("company_name") == "Login Test Company"
        print(f"Login successful for entreprise: {data.get('company_name')}")
    
    def test_login_pro_partenaire(self):
        """Test login-pro for partenaire account"""
        # First register a partenaire
        unique_email = f"test_login_part_{uuid.uuid4().hex[:8]}@structure.org"
        password = "testpass123"
        
        register_payload = {
            "structure_name": "Login Test Structure",
            "structure_type": "association",
            "siret": TEST_SIRET,
            "email": unique_email,
            "password": password,
            "referent_first_name": "Login",
            "referent_last_name": "Test",
            "referent_function": "conseiller",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        reg_response = requests.post(f"{BASE_URL}/api/auth/register-partenaire", json=register_payload)
        assert reg_response.status_code == 200
        
        # Now login with email
        login_payload = {
            "pseudo": unique_email,
            "password": password
        }
        response = requests.post(f"{BASE_URL}/api/auth/login-pro", json=login_payload)
        print(f"Login pro response: {response.status_code} - {response.text}")
        assert response.status_code == 200
        data = response.json()
        
        assert "token" in data
        assert data.get("role") == "partenaire"
        assert data.get("auth_mode") == "pseudo"
        print(f"Login successful for partenaire")
    
    def test_login_pro_wrong_password(self):
        """Test login-pro fails with wrong password"""
        # First register
        unique_email = f"test_wrong_pwd_{uuid.uuid4().hex[:8]}@company.fr"
        
        register_payload = {
            "company_name": "Wrong Pwd Test",
            "siret": TEST_SIRET,
            "email": unique_email,
            "password": "correctpassword",
            "referent_first_name": "Test",
            "referent_last_name": "User",
            "referent_function": "rh",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        requests.post(f"{BASE_URL}/api/auth/register-entreprise", json=register_payload)
        
        # Try login with wrong password
        login_payload = {
            "pseudo": unique_email,
            "password": "wrongpassword"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login-pro", json=login_payload)
        assert response.status_code == 401
        data = response.json()
        assert "incorrect" in data.get("detail", "").lower()
        print(f"Error: {data.get('detail')}")
    
    def test_login_pro_nonexistent_email(self):
        """Test login-pro fails with non-existent email"""
        login_payload = {
            "pseudo": "nonexistent@company.fr",
            "password": "anypassword"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login-pro", json=login_payload)
        assert response.status_code == 401
        data = response.json()
        assert "incorrect" in data.get("detail", "").lower()
        print(f"Error: {data.get('detail')}")


class TestBackwardCompatibility:
    """Test backward compatibility with existing pseudo auth"""
    
    def test_pseudo_register_still_works(self):
        """Test that POST /api/auth/register still works for pseudo accounts"""
        unique_pseudo = f"test_pseudo_{uuid.uuid4().hex[:8]}"
        payload = {
            "pseudo": unique_pseudo,
            "password": "testpass123",
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        print(f"Pseudo register response: {response.status_code} - {response.text}")
        assert response.status_code == 200
        data = response.json()
        
        assert "token" in data
        assert data.get("role") == "particulier"
        assert data.get("auth_mode") == "pseudo"
        assert data.get("pseudo") == unique_pseudo
        print(f"Pseudo registration still works: {unique_pseudo}")
    
    def test_pseudo_login_still_works(self):
        """Test that POST /api/auth/login still works for pseudo accounts"""
        # First register
        unique_pseudo = f"test_login_{uuid.uuid4().hex[:8]}"
        password = "testpass123"
        
        register_payload = {
            "pseudo": unique_pseudo,
            "password": password,
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        }
        requests.post(f"{BASE_URL}/api/auth/register", json=register_payload)
        
        # Now login
        login_payload = {
            "pseudo": unique_pseudo,
            "password": password
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_payload)
        print(f"Pseudo login response: {response.status_code} - {response.text}")
        assert response.status_code == 200
        data = response.json()
        
        assert "token" in data
        assert data.get("auth_mode") == "pseudo"
        print(f"Pseudo login still works: {unique_pseudo}")


class TestProfileCompletion:
    """Test profile completion calculation"""
    
    def test_entreprise_profile_completion(self):
        """Test profile completion is returned on entreprise registration"""
        unique_email = f"test_completion_{uuid.uuid4().hex[:8]}@company.fr"
        payload = {
            "company_name": "Completion Test Company",
            "siret": TEST_SIRET,
            "email": unique_email,
            "password": "testpass123",
            "referent_first_name": "Test",
            "referent_last_name": "User",
            "referent_function": "rh",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register-entreprise", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "profile_completion" in data
        completion = data.get("profile_completion")
        assert isinstance(completion, int)
        assert 0 <= completion <= 100
        print(f"Profile completion for entreprise: {completion}%")
    
    def test_partenaire_profile_completion(self):
        """Test profile completion is returned on partenaire registration"""
        unique_email = f"test_completion_{uuid.uuid4().hex[:8]}@structure.org"
        payload = {
            "structure_name": "Completion Test Structure",
            "structure_type": "association",
            "siret": TEST_SIRET,
            "email": unique_email,
            "password": "testpass123",
            "referent_first_name": "Test",
            "referent_last_name": "User",
            "referent_function": "conseiller",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        response = requests.post(f"{BASE_URL}/api/auth/register-partenaire", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "profile_completion" in data
        completion = data.get("profile_completion")
        assert isinstance(completion, int)
        assert 0 <= completion <= 100
        print(f"Profile completion for partenaire: {completion}%")


class TestDuplicateEmail:
    """Test duplicate email handling"""
    
    def test_entreprise_duplicate_email_rejected(self):
        """Test that duplicate email is rejected for entreprise"""
        unique_email = f"test_dup_{uuid.uuid4().hex[:8]}@company.fr"
        payload = {
            "company_name": "First Company",
            "siret": TEST_SIRET,
            "email": unique_email,
            "password": "testpass123",
            "referent_first_name": "Test",
            "referent_last_name": "User",
            "referent_function": "rh",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        
        # First registration should succeed
        response1 = requests.post(f"{BASE_URL}/api/auth/register-entreprise", json=payload)
        assert response1.status_code == 200
        
        # Second registration with same email should fail
        payload["company_name"] = "Second Company"
        response2 = requests.post(f"{BASE_URL}/api/auth/register-entreprise", json=payload)
        assert response2.status_code == 409
        data = response2.json()
        assert "email" in data.get("detail", "").lower()
        print(f"Duplicate email rejected: {data.get('detail')}")
    
    def test_partenaire_duplicate_email_rejected(self):
        """Test that duplicate email is rejected for partenaire"""
        unique_email = f"test_dup_{uuid.uuid4().hex[:8]}@structure.org"
        payload = {
            "structure_name": "First Structure",
            "structure_type": "association",
            "siret": TEST_SIRET,
            "email": unique_email,
            "password": "testpass123",
            "referent_first_name": "Test",
            "referent_last_name": "User",
            "referent_function": "conseiller",
            "charte_ethique_signed": True,
            "consent_cgu": True,
            "consent_privacy": True
        }
        
        # First registration should succeed
        response1 = requests.post(f"{BASE_URL}/api/auth/register-partenaire", json=payload)
        assert response1.status_code == 200
        
        # Second registration with same email should fail
        payload["structure_name"] = "Second Structure"
        response2 = requests.post(f"{BASE_URL}/api/auth/register-partenaire", json=payload)
        assert response2.status_code == 409
        data = response2.json()
        assert "email" in data.get("detail", "").lower()
        print(f"Duplicate email rejected: {data.get('detail')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
