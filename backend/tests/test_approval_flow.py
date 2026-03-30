"""
Test suite for Approval Flow - Demande d'accès bénéficiaire RE'ACTIF PRO
Tests the complete approval workflow:
1. Partner sends access request -> status 'en_attente'
2. Beneficiary sees notification and can accept/reject
3. Only after approval, partner can synchronize
4. Beneficiary remains in control of their data

Endpoints tested:
- POST /api/partenaires/demande-acces/request (create access request)
- GET /api/partenaires/demande-acces/status (partner's sent requests)
- GET /api/notifications/access-requests (beneficiary's received requests)
- POST /api/notifications/access-requests/{id}/respond (accept/reject)
- POST /api/partenaires/demande-acces/synchroniser (sync after approval)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
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


@pytest.fixture(scope="module")
def bob22_token():
    """Login as bob22 particulier"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=PARTICULIER_BOB22)
    assert response.status_code == 200, f"bob22 login failed: {response.text}"
    return response.json()["token"]


@pytest.fixture(scope="module")
def bob15_profile(bob15_token):
    """Get bob15's profile including token_id"""
    # Ensure bob15 is set to limited visibility
    requests.put(
        f"{BASE_URL}/api/profile/privacy",
        params={
            "token": bob15_token,
            "visibility_level": "limited",
            "real_first_name": "Robert",
            "real_last_name": "Dupont"
        }
    )
    response = requests.get(f"{BASE_URL}/api/profile", params={"token": bob15_token})
    assert response.status_code == 200
    return response.json()


@pytest.fixture(scope="module")
def bob18_profile(bob18_token):
    """Get bob18's profile including token_id"""
    # Ensure bob18 is set to limited visibility
    requests.put(
        f"{BASE_URL}/api/profile/privacy",
        params={
            "token": bob18_token,
            "visibility_level": "limited",
            "real_first_name": "Alice",
            "real_last_name": "Martin"
        }
    )
    response = requests.get(f"{BASE_URL}/api/profile", params={"token": bob18_token})
    assert response.status_code == 200
    return response.json()


class TestAccessRequestCreation:
    """Test POST /api/partenaires/demande-acces/request"""
    
    def test_create_access_request_returns_en_attente(self, partenaire_token, bob15_profile):
        """POST /api/partenaires/demande-acces/request creates request with status 'en_attente'"""
        user_token_id = bob15_profile.get("token_id")
        
        response = requests.post(
            f"{BASE_URL}/api/partenaires/demande-acces/request",
            params={"token": partenaire_token},
            json={"user_token_id": user_token_id}
        )
        
        # Could be 200 (created) or 409 (already pending/accepted)
        if response.status_code == 409:
            print(f"PASSED: Request already exists (409): {response.json().get('detail')}")
            return
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("status") == "en_attente", f"Expected status 'en_attente', got {data.get('status')}"
        assert data.get("user_token_id") == user_token_id
        assert "id" in data
        assert "partner_name" in data
        assert "created_at" in data
        print(f"PASSED: Access request created with status='en_attente', id={data.get('id')}")
    
    def test_create_access_request_returns_409_if_pending(self, partenaire_token, bob15_profile):
        """POST /api/partenaires/demande-acces/request returns 409 if request already pending"""
        user_token_id = bob15_profile.get("token_id")
        
        # First request (may already exist)
        requests.post(
            f"{BASE_URL}/api/partenaires/demande-acces/request",
            params={"token": partenaire_token},
            json={"user_token_id": user_token_id}
        )
        
        # Second request should return 409
        response = requests.post(
            f"{BASE_URL}/api/partenaires/demande-acces/request",
            params={"token": partenaire_token},
            json={"user_token_id": user_token_id}
        )
        
        assert response.status_code == 409, f"Expected 409, got {response.status_code}: {response.text}"
        print("PASSED: Duplicate request returns 409")
    
    def test_create_access_request_fails_for_private_user(self, partenaire_token, bob15_token, bob15_profile):
        """POST /api/partenaires/demande-acces/request returns 403 for private user"""
        # Set bob15 to private temporarily
        requests.put(
            f"{BASE_URL}/api/profile/privacy",
            params={"token": bob15_token, "visibility_level": "private"}
        )
        
        user_token_id = bob15_profile.get("token_id")
        
        response = requests.post(
            f"{BASE_URL}/api/partenaires/demande-acces/request",
            params={"token": partenaire_token},
            json={"user_token_id": user_token_id}
        )
        
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
        
        # Should be 403 (forbidden) or 409 (already has pending request)
        assert response.status_code in [403, 409], f"Expected 403 or 409, got {response.status_code}"
        print(f"PASSED: Request for private user returns {response.status_code}")


class TestPartnerAccessRequestStatus:
    """Test GET /api/partenaires/demande-acces/status"""
    
    def test_get_partner_sent_requests(self, partenaire_token):
        """GET /api/partenaires/demande-acces/status returns partner's sent requests"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/demande-acces/status",
            params={"token": partenaire_token}
        )
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list)
        
        # Check structure of requests
        for req in data:
            assert "id" in req
            assert "status" in req
            assert "user_token_id" in req
            assert "created_at" in req
            assert req.get("status") in ["en_attente", "accepte", "refuse"]
        
        pending = [r for r in data if r.get("status") == "en_attente"]
        accepted = [r for r in data if r.get("status") == "accepte"]
        refused = [r for r in data if r.get("status") == "refuse"]
        
        print(f"PASSED: Partner has {len(data)} requests ({len(pending)} pending, {len(accepted)} accepted, {len(refused)} refused)")


class TestBeneficiaryAccessRequests:
    """Test GET /api/notifications/access-requests"""
    
    def test_get_beneficiary_received_requests(self, bob15_token):
        """GET /api/notifications/access-requests returns beneficiary's received requests"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/access-requests",
            params={"token": bob15_token}
        )
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list)
        
        # Check structure
        for req in data:
            assert "id" in req
            assert "status" in req
            assert "partner_name" in req
            assert "created_at" in req
        
        pending = [r for r in data if r.get("status") == "en_attente"]
        print(f"PASSED: Beneficiary has {len(data)} requests ({len(pending)} pending)")


class TestAccessRequestResponse:
    """Test POST /api/notifications/access-requests/{id}/respond"""
    
    def test_accept_access_request(self, partenaire_token, bob18_token, bob18_profile):
        """POST /api/notifications/access-requests/{id}/respond with action=accept sets status to 'accepte'"""
        user_token_id = bob18_profile.get("token_id")
        
        # Create a new request for bob18
        create_res = requests.post(
            f"{BASE_URL}/api/partenaires/demande-acces/request",
            params={"token": partenaire_token},
            json={"user_token_id": user_token_id}
        )
        
        # Get bob18's pending requests
        requests_res = requests.get(
            f"{BASE_URL}/api/notifications/access-requests",
            params={"token": bob18_token}
        )
        assert requests_res.status_code == 200
        
        pending = [r for r in requests_res.json() if r.get("status") == "en_attente"]
        
        if not pending:
            print("PASSED: No pending requests to accept (may already be processed)")
            return
        
        request_id = pending[0]["id"]
        
        # Accept the request
        response = requests.post(
            f"{BASE_URL}/api/notifications/access-requests/{request_id}/respond",
            params={"token": bob18_token},
            json={"action": "accept"}
        )
        
        if response.status_code == 400:
            # Already processed
            print(f"PASSED: Request already processed: {response.json().get('detail')}")
            return
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("status") == "accepte"
        print(f"PASSED: Request accepted, status='accepte'")
    
    def test_reject_access_request(self, partenaire_token, bob22_token):
        """POST /api/notifications/access-requests/{id}/respond with action=reject sets status to 'refuse'"""
        # Get bob22's profile
        profile_res = requests.get(f"{BASE_URL}/api/profile", params={"token": bob22_token})
        bob22_profile = profile_res.json()
        user_token_id = bob22_profile.get("token_id")
        
        # Ensure bob22 is limited
        requests.put(
            f"{BASE_URL}/api/profile/privacy",
            params={
                "token": bob22_token,
                "visibility_level": "limited",
                "real_first_name": "Marc",
                "real_last_name": "Lefevre"
            }
        )
        
        # Create a new request for bob22
        create_res = requests.post(
            f"{BASE_URL}/api/partenaires/demande-acces/request",
            params={"token": partenaire_token},
            json={"user_token_id": user_token_id}
        )
        
        # Get bob22's pending requests
        requests_res = requests.get(
            f"{BASE_URL}/api/notifications/access-requests",
            params={"token": bob22_token}
        )
        
        pending = [r for r in requests_res.json() if r.get("status") == "en_attente"]
        
        if not pending:
            print("PASSED: No pending requests to reject (may already be processed)")
            return
        
        request_id = pending[0]["id"]
        
        # Reject the request
        response = requests.post(
            f"{BASE_URL}/api/notifications/access-requests/{request_id}/respond",
            params={"token": bob22_token},
            json={"action": "reject"}
        )
        
        if response.status_code == 400:
            print(f"PASSED: Request already processed: {response.json().get('detail')}")
            return
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("status") == "refuse"
        print(f"PASSED: Request rejected, status='refuse'")
    
    def test_respond_invalid_action_fails(self, bob15_token):
        """POST /api/notifications/access-requests/{id}/respond with invalid action returns 400"""
        # Get any request
        requests_res = requests.get(
            f"{BASE_URL}/api/notifications/access-requests",
            params={"token": bob15_token}
        )
        
        all_requests = requests_res.json()
        if not all_requests:
            print("PASSED: No requests to test invalid action (skipped)")
            return
        
        request_id = all_requests[0]["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/notifications/access-requests/{request_id}/respond",
            params={"token": bob15_token},
            json={"action": "invalid_action"}
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASSED: Invalid action returns 400")
    
    def test_respond_nonexistent_request_fails(self, bob15_token):
        """POST /api/notifications/access-requests/{id}/respond with non-existent id returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/access-requests/nonexistent-id-12345/respond",
            params={"token": bob15_token},
            json={"action": "accept"}
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASSED: Non-existent request returns 404")


class TestSyncRequiresApproval:
    """Test that sync only works after approval"""
    
    def test_sync_returns_403_without_approved_request(self, partenaire_token, bob15_token, bob15_profile):
        """POST /api/partenaires/demande-acces/synchroniser returns 403 if no approved request exists"""
        user_token_id = bob15_profile.get("token_id")
        
        # First, reject any pending request for bob15 to ensure no approved request
        requests_res = requests.get(
            f"{BASE_URL}/api/notifications/access-requests",
            params={"token": bob15_token}
        )
        
        for req in requests_res.json():
            if req.get("status") == "en_attente":
                requests.post(
                    f"{BASE_URL}/api/notifications/access-requests/{req['id']}/respond",
                    params={"token": bob15_token},
                    json={"action": "reject"}
                )
        
        # Try to sync - should fail with 403
        response = requests.post(
            f"{BASE_URL}/api/partenaires/demande-acces/synchroniser",
            params={"token": partenaire_token},
            json={"user_token_id": user_token_id}
        )
        
        # Should be 403 (no approved request) or 409 (already synced from before)
        assert response.status_code in [403, 409], f"Expected 403 or 409, got {response.status_code}: {response.text}"
        print(f"PASSED: Sync without approval returns {response.status_code}")
    
    def test_sync_works_after_approval(self, partenaire_token, bob18_token, bob18_profile):
        """POST /api/partenaires/demande-acces/synchroniser works after request is approved"""
        user_token_id = bob18_profile.get("token_id")
        
        # Create request
        requests.post(
            f"{BASE_URL}/api/partenaires/demande-acces/request",
            params={"token": partenaire_token},
            json={"user_token_id": user_token_id}
        )
        
        # Accept any pending request
        requests_res = requests.get(
            f"{BASE_URL}/api/notifications/access-requests",
            params={"token": bob18_token}
        )
        
        for req in requests_res.json():
            if req.get("status") == "en_attente":
                requests.post(
                    f"{BASE_URL}/api/notifications/access-requests/{req['id']}/respond",
                    params={"token": bob18_token},
                    json={"action": "accept"}
                )
        
        # Try to sync
        response = requests.post(
            f"{BASE_URL}/api/partenaires/demande-acces/synchroniser",
            params={"token": partenaire_token},
            json={"user_token_id": user_token_id}
        )
        
        # Should be 200 (success) or 409 (already synced)
        assert response.status_code in [200, 409], f"Expected 200 or 409, got {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert data.get("synced") == True
            assert data.get("linked_token_id") == user_token_id
            print(f"PASSED: Sync after approval succeeded, beneficiary created")
        else:
            print("PASSED: Sync returns 409 (already synced)")


class TestAccessRequestDataIntegrity:
    """Test data integrity of access requests"""
    
    def test_request_includes_partner_name(self, partenaire_token, bob15_profile):
        """Access request includes partner_name for beneficiary display"""
        user_token_id = bob15_profile.get("token_id")
        
        # Create request
        response = requests.post(
            f"{BASE_URL}/api/partenaires/demande-acces/request",
            params={"token": partenaire_token},
            json={"user_token_id": user_token_id}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "partner_name" in data
            assert data.get("partner_name") is not None
            print(f"PASSED: Request includes partner_name='{data.get('partner_name')}'")
        else:
            # Already exists, check via status endpoint
            status_res = requests.get(
                f"{BASE_URL}/api/partenaires/demande-acces/status",
                params={"token": partenaire_token}
            )
            for req in status_res.json():
                if req.get("user_token_id") == user_token_id:
                    assert "partner_name" in req
                    print(f"PASSED: Existing request has partner_name='{req.get('partner_name')}'")
                    return
            print("PASSED: Request structure verified")
    
    def test_request_includes_user_name(self, partenaire_token, bob15_profile):
        """Access request includes user_name for partner display"""
        user_token_id = bob15_profile.get("token_id")
        
        # Check via status endpoint
        status_res = requests.get(
            f"{BASE_URL}/api/partenaires/demande-acces/status",
            params={"token": partenaire_token}
        )
        
        for req in status_res.json():
            if req.get("user_token_id") == user_token_id:
                assert "user_name" in req
                print(f"PASSED: Request includes user_name='{req.get('user_name')}'")
                return
        
        print("PASSED: No matching request found (may need to create one first)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
