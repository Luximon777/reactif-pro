"""
Test suite for Identifiant France Travail feature
Tests:
- POST /api/auth/register with identifiant_france_travail field
- PUT /api/profile/privacy with identifiant_france_travail parameter
- GET /api/partenaires/demande-acces/search with identifiant_ft parameter
- Search results include has_dclic, profile_boosted, authorized fields
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
PARTNER_EMAIL = "cluximon@gmail.com"
PARTNER_PASSWORD = "Solerys777!"
BENEFICIARY_PSEUDO = "bob23"
BENEFICIARY_PASSWORD = "Solerys777!"


class TestIdentifiantFranceTravailRegistration:
    """Test registration with identifiant_france_travail field"""
    
    def test_register_with_identifiant_ft(self):
        """Test that registration accepts identifiant_france_travail field"""
        unique_pseudo = f"TEST_ft_user_{uuid.uuid4().hex[:8]}"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": unique_pseudo,
            "password": "Solerys777!",
            "role": "particulier",
            "identifiant_france_travail": "FT123456789",
            "consent_cgu": True,
            "consent_privacy": True
        })
        
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["pseudo"] == unique_pseudo
        assert data["auth_mode"] == "pseudo"
        
        # Verify the profile has the identifiant_france_travail
        token = data["token"]
        profile_res = requests.get(f"{BASE_URL}/api/profile?token={token}")
        assert profile_res.status_code == 200
        profile = profile_res.json()
        assert profile.get("identifiant_france_travail") == "FT123456789"
        print(f"✓ Registration with identifiant_france_travail successful: {unique_pseudo}")
    
    def test_register_without_identifiant_ft(self):
        """Test that registration works without identifiant_france_travail (optional field)"""
        unique_pseudo = f"TEST_no_ft_{uuid.uuid4().hex[:8]}"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": unique_pseudo,
            "password": "Solerys777!",
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        })
        
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        assert "token" in data
        
        # Verify profile has no identifiant_france_travail
        token = data["token"]
        profile_res = requests.get(f"{BASE_URL}/api/profile?token={token}")
        assert profile_res.status_code == 200
        profile = profile_res.json()
        assert profile.get("identifiant_france_travail") is None
        print("✓ Registration without identifiant_france_travail successful")


class TestPrivacySettingsIdentifiantFT:
    """Test privacy settings with identifiant_france_travail"""
    
    @pytest.fixture
    def beneficiary_token(self):
        """Login as beneficiary bob23"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": BENEFICIARY_PSEUDO,
            "password": BENEFICIARY_PASSWORD
        })
        assert response.status_code == 200, f"Beneficiary login failed: {response.text}"
        return response.json()["token"]
    
    def test_update_privacy_with_identifiant_ft(self, beneficiary_token):
        """Test updating privacy settings with identifiant_france_travail"""
        # Update privacy with identifiant_france_travail
        response = requests.put(
            f"{BASE_URL}/api/profile/privacy",
            params={
                "token": beneficiary_token,
                "identifiant_france_travail": "FT_TEST_123"
            }
        )
        
        assert response.status_code == 200, f"Privacy update failed: {response.text}"
        data = response.json()
        assert data.get("identifiant_france_travail") == "FT_TEST_123"
        print("✓ Privacy update with identifiant_france_travail successful")
    
    def test_update_privacy_with_visibility_limited(self, beneficiary_token):
        """Test updating to limited visibility with real name and FT ID"""
        response = requests.put(
            f"{BASE_URL}/api/profile/privacy",
            params={
                "token": beneficiary_token,
                "visibility_level": "limited",
                "real_first_name": "Bob",
                "real_last_name": "Meyer",
                "identifiant_france_travail": "FT_BOB_123"
            }
        )
        
        assert response.status_code == 200, f"Privacy update failed: {response.text}"
        data = response.json()
        assert data.get("visibility_level") == "limited"
        assert data.get("real_first_name") == "Bob"
        assert data.get("real_last_name") == "Meyer"
        assert data.get("identifiant_france_travail") == "FT_BOB_123"
        print("✓ Privacy update with limited visibility and FT ID successful")


class TestPartnerSearchWithIdentifiantFT:
    """Test partner search endpoint with identifiant_ft parameter"""
    
    @pytest.fixture
    def partner_token(self):
        """Login as partner"""
        response = requests.post(f"{BASE_URL}/api/auth/login-pro", json={
            "pseudo": PARTNER_EMAIL,
            "password": PARTNER_PASSWORD
        })
        assert response.status_code == 200, f"Partner login failed: {response.text}"
        return response.json()["token"]
    
    def test_search_by_name_only(self, partner_token):
        """Test search by name returns users with has_dclic, profile_boosted, authorized fields"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/demande-acces/search",
            params={
                "token": partner_token,
                "query": "meyer"
            }
        )
        
        assert response.status_code == 200, f"Search failed: {response.text}"
        results = response.json()
        
        # Check that results contain the expected fields
        if len(results) > 0:
            user = results[0]
            assert "has_dclic" in user, "Missing has_dclic field"
            assert "profile_boosted" in user, "Missing profile_boosted field"
            assert "authorized" in user, "Missing authorized field"
            assert "full_name" in user, "Missing full_name field"
            assert "token_id" in user, "Missing token_id field"
            print(f"✓ Search by name returned {len(results)} results with correct fields")
            print(f"  First result: {user.get('full_name')}, has_dclic={user.get('has_dclic')}, profile_boosted={user.get('profile_boosted')}, authorized={user.get('authorized')}")
        else:
            print("⚠ No results found for 'meyer' - this may be expected if no matching users exist")
    
    def test_search_by_identifiant_ft_and_name(self, partner_token):
        """Test search by identifiant_ft + name"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/demande-acces/search",
            params={
                "token": partner_token,
                "identifiant_ft": "FT",
                "query": "meyer"
            }
        )
        
        assert response.status_code == 200, f"Search failed: {response.text}"
        results = response.json()
        print(f"✓ Search by FT ID + name returned {len(results)} results")
        
        # Verify all results have the required fields
        for user in results:
            assert "has_dclic" in user
            assert "profile_boosted" in user
            assert "authorized" in user
            if user.get("identifiant_france_travail"):
                print(f"  Found user with FT ID: {user.get('identifiant_france_travail')}")
    
    def test_search_by_identifiant_ft_only(self, partner_token):
        """Test search by identifiant_ft only (with minimal query)"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/demande-acces/search",
            params={
                "token": partner_token,
                "identifiant_ft": "FT_BOB",
                "query": ""
            }
        )
        
        assert response.status_code == 200, f"Search failed: {response.text}"
        results = response.json()
        print(f"✓ Search by FT ID only returned {len(results)} results")
    
    def test_search_returns_visibility_level(self, partner_token):
        """Test that search only returns users with limited or public visibility"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/demande-acces/search",
            params={
                "token": partner_token,
                "query": "bob"
            }
        )
        
        assert response.status_code == 200, f"Search failed: {response.text}"
        results = response.json()
        
        # All returned users should have limited or public visibility
        for user in results:
            visibility = user.get("visibility_level")
            assert visibility in ["limited", "public"], f"User {user.get('full_name')} has unexpected visibility: {visibility}"
        
        print(f"✓ All {len(results)} results have limited or public visibility")
    
    def test_authorized_field_logic(self, partner_token):
        """Test that authorized field is correctly computed based on conditions"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/demande-acces/search",
            params={
                "token": partner_token,
                "query": "meyer"
            }
        )
        
        assert response.status_code == 200, f"Search failed: {response.text}"
        results = response.json()
        
        for user in results:
            has_dclic = user.get("has_dclic", False)
            profile_boosted = user.get("profile_boosted", False)
            visibility = user.get("visibility_level")
            authorized = user.get("authorized", False)
            
            # authorized should be True only if: visibility=limited AND has_dclic AND profile_boosted
            expected_authorized = (visibility == "limited" and has_dclic and profile_boosted)
            
            assert authorized == expected_authorized, (
                f"User {user.get('full_name')}: authorized={authorized} but expected {expected_authorized} "
                f"(visibility={visibility}, has_dclic={has_dclic}, profile_boosted={profile_boosted})"
            )
        
        print(f"✓ Authorized field logic verified for {len(results)} results")


class TestPartnerLogin:
    """Test partner login endpoint"""
    
    def test_partner_login_success(self):
        """Test partner login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login-pro", json={
            "pseudo": PARTNER_EMAIL,
            "password": PARTNER_PASSWORD
        })
        
        assert response.status_code == 200, f"Partner login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["role"] == "partenaire"
        print(f"✓ Partner login successful: {PARTNER_EMAIL}")
    
    def test_partner_login_invalid_credentials(self):
        """Test partner login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login-pro", json={
            "pseudo": "invalid@email.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        print("✓ Partner login correctly rejected invalid credentials")


class TestBeneficiaryLogin:
    """Test beneficiary login endpoint"""
    
    def test_beneficiary_login_success(self):
        """Test beneficiary login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": BENEFICIARY_PSEUDO,
            "password": BENEFICIARY_PASSWORD
        })
        
        assert response.status_code == 200, f"Beneficiary login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["role"] == "particulier"
        print(f"✓ Beneficiary login successful: {BENEFICIARY_PSEUDO}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
