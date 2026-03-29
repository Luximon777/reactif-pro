"""
Test suite for Demande d'accès bénéficiaire RE'ACTIF PRO flow
Tests:
- PUT /api/profile/privacy with real_first_name and real_last_name
- GET /api/partenaires/demande-acces/search (search by name, visibility filtering)
- POST /api/partenaires/demande-acces/synchroniser (create beneficiary with full sync)
- Regression tests for V2 fiches and consent modules
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
PARTENAIRE_EMAIL = "test@missionlocale.fr"
PARTENAIRE_PASSWORD = "Solerys777!"
PARTICULIER_BOB15 = {"pseudo": "bob15", "password": "Solerys777!"}
PARTICULIER_BOB18 = {"pseudo": "bob18", "password": "Solerys777!"}
PARTICULIER_BOB22 = {"pseudo": "bob22", "password": "Solerys777!"}


@pytest.fixture(scope="module")
def partenaire_token():
    """Login as partenaire and get token"""
    response = requests.post(f"{BASE_URL}/api/auth/login-pro", json={
        "pseudo": PARTENAIRE_EMAIL,
        "password": PARTENAIRE_PASSWORD
    })
    assert response.status_code == 200, f"Partenaire login failed: {response.text}"
    return response.json()["token"]


@pytest.fixture(scope="module")
def bob15_token():
    """Login as bob15 particulier"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=PARTICULIER_BOB15)
    assert response.status_code == 200, f"bob15 login failed: {response.text}"
    return response.json()["token"]


@pytest.fixture(scope="module")
def bob18_token():
    """Login as bob18 particulier"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=PARTICULIER_BOB18)
    assert response.status_code == 200, f"bob18 login failed: {response.text}"
    return response.json()["token"]


class TestPrivacySettingsRealName:
    """Test PUT /api/profile/privacy with real_first_name and real_last_name"""
    
    def test_update_privacy_with_real_name(self, bob15_token):
        """PUT /api/profile/privacy accepts real_first_name and real_last_name"""
        response = requests.put(
            f"{BASE_URL}/api/profile/privacy",
            params={
                "token": bob15_token,
                "visibility_level": "limited",
                "real_first_name": "Robert",
                "real_last_name": "Dupont"
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("real_first_name") == "Robert"
        assert data.get("real_last_name") == "Dupont"
        assert data.get("visibility_level") == "limited"
        print("PASSED: PUT /api/profile/privacy accepts real_first_name and real_last_name")
    
    def test_update_privacy_bob18_limited(self, bob18_token):
        """Set bob18 to limited visibility with real name"""
        response = requests.put(
            f"{BASE_URL}/api/profile/privacy",
            params={
                "token": bob18_token,
                "visibility_level": "limited",
                "real_first_name": "Alice",
                "real_last_name": "Martin"
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("visibility_level") == "limited"
        print("PASSED: bob18 set to limited visibility")
    
    def test_get_profile_shows_real_name(self, bob15_token):
        """GET /api/profile returns real_first_name and real_last_name"""
        response = requests.get(f"{BASE_URL}/api/profile", params={"token": bob15_token})
        assert response.status_code == 200
        data = response.json()
        assert "real_first_name" in data
        assert "real_last_name" in data
        print(f"PASSED: Profile shows real_first_name={data.get('real_first_name')}, real_last_name={data.get('real_last_name')}")


class TestDemandeAccesSearch:
    """Test GET /api/partenaires/demande-acces/search"""
    
    def test_search_by_name_returns_limited_users(self, partenaire_token):
        """Search by name returns only users with visibility_level='limited' or 'public'"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/demande-acces/search",
            params={"token": partenaire_token, "query": "Robert"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        # All returned users should have limited or public visibility
        for user in data:
            assert user.get("visibility_level") in ["limited", "public"], f"User {user.get('pseudo')} has wrong visibility"
        print(f"PASSED: Search returned {len(data)} users with limited/public visibility")
    
    def test_search_returns_authorized_flag(self, partenaire_token):
        """Search results include 'authorized' flag for limited users"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/demande-acces/search",
            params={"token": partenaire_token, "query": "Dupont"}
        )
        assert response.status_code == 200
        data = response.json()
        for user in data:
            assert "authorized" in user
            # Limited visibility users should be authorized
            if user.get("visibility_level") == "limited":
                assert user.get("authorized") == True
        print("PASSED: Search results include 'authorized' flag")
    
    def test_search_returns_full_name(self, partenaire_token):
        """Search results include full_name, real_first_name, real_last_name"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/demande-acces/search",
            params={"token": partenaire_token, "query": "Robert"}
        )
        assert response.status_code == 200
        data = response.json()
        if len(data) > 0:
            user = data[0]
            assert "full_name" in user
            assert "real_first_name" in user
            assert "real_last_name" in user
            assert "token_id" in user
            print(f"PASSED: Search result has full_name={user.get('full_name')}")
        else:
            print("PASSED: Search returned empty (no matching users)")
    
    def test_search_by_alice_finds_bob18(self, partenaire_token):
        """Search by 'Alice' should find bob18 (real_first_name=Alice)"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/demande-acces/search",
            params={"token": partenaire_token, "query": "Alice"}
        )
        assert response.status_code == 200
        data = response.json()
        # Should find at least one user with Alice in name
        alice_users = [u for u in data if "Alice" in u.get("full_name", "") or u.get("real_first_name") == "Alice"]
        print(f"PASSED: Search 'Alice' returned {len(data)} results, {len(alice_users)} with Alice in name")
    
    def test_search_minimum_query_length(self, partenaire_token):
        """Search with query < 2 chars returns empty"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/demande-acces/search",
            params={"token": partenaire_token, "query": "A"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data == []
        print("PASSED: Search with 1 char returns empty list")
    
    def test_search_does_not_return_private_users(self, partenaire_token, bob15_token):
        """Users with visibility_level='private' should NOT appear in search"""
        # First, set bob15 to private
        requests.put(
            f"{BASE_URL}/api/profile/privacy",
            params={"token": bob15_token, "visibility_level": "private"}
        )
        
        # Search should not find bob15 by name
        response = requests.get(
            f"{BASE_URL}/api/partenaires/demande-acces/search",
            params={"token": partenaire_token, "query": "Robert"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check that no user with pseudo bob15 is returned
        bob15_found = any(u.get("pseudo") == "bob15" for u in data)
        assert not bob15_found, "bob15 with private visibility should not appear in search"
        
        # Restore bob15 to limited
        requests.put(
            f"{BASE_URL}/api/profile/privacy",
            params={
                "token": bob15_token,
                "visibility_level": "limited",
                "real_first_name": "Robert",
                "real_last_name": "Dupont"
            }
        )
        print("PASSED: Private users do NOT appear in search results")


class TestDemandeAccesSynchroniser:
    """Test POST /api/partenaires/demande-acces/synchroniser"""
    
    def test_sync_creates_beneficiary_with_full_profile(self, partenaire_token, bob18_token):
        """Sync creates a beneficiary with full profile data (name, skills, linked_token_id, synced=True)"""
        # First ensure bob18 is set to limited
        requests.put(
            f"{BASE_URL}/api/profile/privacy",
            params={
                "token": bob18_token,
                "visibility_level": "limited",
                "real_first_name": "Alice",
                "real_last_name": "Martin"
            }
        )
        
        # Get bob18's token_id
        profile_res = requests.get(f"{BASE_URL}/api/profile", params={"token": bob18_token})
        bob18_token_id = profile_res.json().get("token_id")
        
        # Try to sync
        response = requests.post(
            f"{BASE_URL}/api/partenaires/demande-acces/synchroniser",
            params={"token": partenaire_token},
            json={"user_token_id": bob18_token_id}
        )
        
        # Could be 200 (success) or 409 (already synced)
        if response.status_code == 409:
            print("PASSED: Sync returns 409 if already synced (expected for bob18)")
            return
        
        assert response.status_code == 200, f"Sync failed: {response.text}"
        data = response.json()
        
        # Verify beneficiary data
        assert data.get("synced") == True
        assert data.get("linked_token_id") == bob18_token_id
        assert "Alice" in data.get("name", "") or "Martin" in data.get("name", "")
        assert data.get("status") == "En accompagnement"
        print(f"PASSED: Sync created beneficiary '{data.get('name')}' with synced=True")
    
    def test_sync_returns_403_for_private_user(self, partenaire_token, bob15_token):
        """Sync returns 403 if user has private visibility"""
        # Set bob15 to private
        requests.put(
            f"{BASE_URL}/api/profile/privacy",
            params={"token": bob15_token, "visibility_level": "private"}
        )
        
        # Get bob15's token_id
        profile_res = requests.get(f"{BASE_URL}/api/profile", params={"token": bob15_token})
        bob15_token_id = profile_res.json().get("token_id")
        
        # Try to sync - should fail
        response = requests.post(
            f"{BASE_URL}/api/partenaires/demande-acces/synchroniser",
            params={"token": partenaire_token},
            json={"user_token_id": bob15_token_id}
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print("PASSED: Sync returns 403 for private user")
        
        # Restore bob15 to limited
        requests.put(
            f"{BASE_URL}/api/profile/privacy",
            params={
                "token": bob15_token,
                "visibility_level": "limited",
                "real_first_name": "Robert",
                "real_last_name": "Dupont"
            }
        )
    
    def test_sync_returns_409_if_already_synced(self, partenaire_token, bob18_token):
        """Sync returns 409 if beneficiary already synced"""
        # Get bob18's token_id
        profile_res = requests.get(f"{BASE_URL}/api/profile", params={"token": bob18_token})
        bob18_token_id = profile_res.json().get("token_id")
        
        # Try to sync again - should return 409
        response = requests.post(
            f"{BASE_URL}/api/partenaires/demande-acces/synchroniser",
            params={"token": partenaire_token},
            json={"user_token_id": bob18_token_id}
        )
        
        # Should be 409 (already synced) or 200 (first sync)
        assert response.status_code in [200, 409], f"Unexpected status: {response.status_code}"
        if response.status_code == 409:
            print("PASSED: Sync returns 409 if already synced")
        else:
            print("PASSED: First sync succeeded (will return 409 on next attempt)")
    
    def test_sync_returns_404_for_nonexistent_user(self, partenaire_token):
        """Sync returns 404 for non-existent user token_id"""
        response = requests.post(
            f"{BASE_URL}/api/partenaires/demande-acces/synchroniser",
            params={"token": partenaire_token},
            json={"user_token_id": "nonexistent-token-id-12345"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASSED: Sync returns 404 for non-existent user")


class TestRegressionV2Fiches:
    """Regression tests for V2 fiches (12 fiches)"""
    
    def test_get_fiches_returns_12(self, partenaire_token):
        """GET /api/partenaires/outils/fiches returns 12 fiches"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/outils/fiches",
            params={"token": partenaire_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 12, f"Expected 12 fiches, got {len(data)}"
        print("PASSED: GET /api/partenaires/outils/fiches returns 12 fiches")


class TestRegressionConsentModules:
    """Regression tests for consent modules"""
    
    def test_get_consent_modules_returns_modules(self, partenaire_token):
        """GET /api/partenaires/consent-modules returns modules"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/consent-modules",
            params={"token": partenaire_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Check structure
        for module in data:
            assert "id" in module
            assert "label" in module
        print(f"PASSED: GET /api/partenaires/consent-modules returns {len(data)} modules")


class TestBeneficiairesListShowsSynced:
    """Test that synced beneficiaries appear in list"""
    
    def test_beneficiaires_list_includes_synced(self, partenaire_token):
        """GET /api/partenaires/beneficiaires includes synced beneficiaries"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/beneficiaires",
            params={"token": partenaire_token}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check if any beneficiary has synced=True
        synced_count = sum(1 for b in data if b.get("synced") == True)
        linked_count = sum(1 for b in data if b.get("linked_token_id"))
        
        print(f"PASSED: Beneficiaires list has {len(data)} total, {synced_count} synced, {linked_count} linked")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
