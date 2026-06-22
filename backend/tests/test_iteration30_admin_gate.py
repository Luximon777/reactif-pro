"""
Test Iteration 30: Admin Gate Authentication & User Login Flow
Tests:
1. Admin authentication flow - clicking Admin button, entering password, verifying gate_state
2. Admin blocked from Espace Personnel - should show toast and NOT redirect
3. Normal user login flow - mike7/Solerys777! redirected to /dashboard
4. Login modal is NOT blank when clicking 'Espace Personnel'
5. Gate state API endpoint works correctly
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://cv-analyzer-53.preview.emergentagent.com')

class TestGateStateAPI:
    """Tests for /api/admin/gate-state endpoints"""
    
    def test_get_gate_state(self):
        """GET /api/admin/gate-state returns spaces_open status"""
        response = requests.get(f"{BASE_URL}/api/admin/gate-state")
        assert response.status_code == 200
        data = response.json()
        assert "spaces_open" in data
        assert isinstance(data["spaces_open"], bool)
        print(f"✅ GET gate-state: spaces_open = {data['spaces_open']}")
    
    def test_post_gate_state_correct_password(self):
        """POST /api/admin/gate-state with correct password sets spaces_open"""
        response = requests.post(
            f"{BASE_URL}/api/admin/gate-state",
            json={"password": "Choukette@777", "spaces_open": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["spaces_open"] == True
        print("✅ POST gate-state with correct password: spaces_open = True")
    
    def test_post_gate_state_wrong_password(self):
        """POST /api/admin/gate-state with wrong password returns 403"""
        response = requests.post(
            f"{BASE_URL}/api/admin/gate-state",
            json={"password": "wrongpassword", "spaces_open": True}
        )
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "incorrect" in data["detail"].lower() or "administrateur" in data["detail"].lower()
        print(f"✅ POST gate-state with wrong password: 403 - {data['detail']}")
    
    def test_post_gate_state_toggle_off(self):
        """POST /api/admin/gate-state can set spaces_open to false"""
        response = requests.post(
            f"{BASE_URL}/api/admin/gate-state",
            json={"password": "Choukette@777", "spaces_open": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["spaces_open"] == False
        print("✅ POST gate-state: spaces_open = False")
        
        # Reset to True for other tests
        requests.post(
            f"{BASE_URL}/api/admin/gate-state",
            json={"password": "Choukette@777", "spaces_open": True}
        )


class TestUserAuthentication:
    """Tests for user authentication endpoints"""
    
    def test_login_mike7_success(self):
        """Login with mike7/Solerys777! returns valid token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"pseudo": "mike7", "password": "Solerys777!"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "role" in data
        assert "profile_id" in data
        assert "pseudo" in data
        assert data["pseudo"] == "mike7"
        assert data["role"] == "particulier"
        print(f"✅ Login mike7: token={data['token'][:20]}..., role={data['role']}")
    
    def test_login_pierre7_success(self):
        """Login with pierre7/Solerys777! returns valid token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"pseudo": "pierre7", "password": "Solerys777!"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["pseudo"] == "pierre7"
        print(f"✅ Login pierre7: token={data['token'][:20]}..., role={data['role']}")
    
    def test_login_invalid_credentials(self):
        """Login with invalid credentials returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"pseudo": "invaliduser", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        print("✅ Login with invalid credentials: 401")
    
    def test_login_wrong_password(self):
        """Login with correct user but wrong password returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"pseudo": "mike7", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        print("✅ Login mike7 with wrong password: 401")


class TestTokenVerification:
    """Tests for token verification"""
    
    def test_verify_valid_token(self):
        """Verify a valid token returns user info"""
        # First login to get a token
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"pseudo": "mike7", "password": "Solerys777!"}
        )
        token = login_response.json()["token"]
        
        # Verify the token
        response = requests.get(f"{BASE_URL}/api/auth/verify?token={token}")
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert "role" in data
        assert "profile_id" in data
        print(f"✅ Verify token: valid=True, role={data['role']}")
    
    def test_verify_invalid_token(self):
        """Verify an invalid token returns 401"""
        response = requests.get(f"{BASE_URL}/api/auth/verify?token=invalidtoken123")
        assert response.status_code == 401
        print("✅ Verify invalid token: 401")


class TestProfileAccess:
    """Tests for profile access after authentication"""
    
    def test_get_profile_with_valid_token(self):
        """Get profile with valid token returns profile data"""
        # First login to get a token
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"pseudo": "mike7", "password": "Solerys777!"}
        )
        token = login_response.json()["token"]
        
        # Get profile
        response = requests.get(f"{BASE_URL}/api/profile?token={token}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "token_id" in data
        print(f"✅ Get profile: id={data['id'][:20]}...")
    
    def test_get_profile_without_token(self):
        """Get profile without token returns 422 (validation error)"""
        response = requests.get(f"{BASE_URL}/api/profile")
        assert response.status_code == 422
        print("✅ Get profile without token: 422")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
