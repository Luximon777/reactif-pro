"""
Test suite for Anonymat & Pseudonymat feature
Tests: Registration, Login, Upgrade, Change Password, Privacy Settings, Export, Delete
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAnonymousAuth:
    """Test backward compatibility - anonymous auth still works"""
    
    def test_anonymous_token_creation(self):
        """POST /api/auth/anonymous - Create anonymous token"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "token" in data
        assert "profile_id" in data
        assert data["auth_mode"] == "anonymous"
        assert data["role"] == "particulier"
        print(f"✓ Anonymous token created: {data['token'][:20]}...")
        return data
    
    def test_anonymous_token_verify(self):
        """GET /api/auth/verify - Verify anonymous token"""
        # First create anonymous token
        create_resp = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = create_resp.json()["token"]
        
        # Verify it
        response = requests.get(f"{BASE_URL}/api/auth/verify?token={token}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == True
        assert data["auth_mode"] == "anonymous"
        assert data["identity_level"] == "none"
        print(f"✓ Anonymous token verified, auth_mode={data['auth_mode']}")


class TestPseudonymousRegistration:
    """Test pseudonymous account registration"""
    
    def test_register_success(self):
        """POST /api/auth/register - Register with valid pseudo + password"""
        unique_pseudo = f"TestUser_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": unique_pseudo,
            "password": "testpass123",
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True,
            "consent_marketing": False
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "token" in data
        assert data["pseudo"] == unique_pseudo
        assert data["auth_mode"] == "pseudo"
        print(f"✓ Registered pseudo account: {unique_pseudo}")
        return data
    
    def test_register_pseudo_too_short(self):
        """POST /api/auth/register - Reject pseudo < 3 chars"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": "ab",
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 400
        assert "3 caractères" in response.json()["detail"]
        print("✓ Rejected short pseudo")
    
    def test_register_password_too_short(self):
        """POST /api/auth/register - Reject password < 6 chars"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": "ValidPseudo",
            "password": "12345",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 400
        assert "6 caractères" in response.json()["detail"]
        print("✓ Rejected short password")
    
    def test_register_missing_consent(self):
        """POST /api/auth/register - Reject without CGU/privacy consent"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": "ValidPseudo",
            "password": "testpass123",
            "consent_cgu": False,
            "consent_privacy": True
        })
        assert response.status_code == 400
        assert "CGU" in response.json()["detail"] or "confidentialité" in response.json()["detail"]
        print("✓ Rejected missing consent")
    
    def test_register_duplicate_pseudo(self):
        """POST /api/auth/register - Reject duplicate pseudo"""
        unique_pseudo = f"DupTest_{uuid.uuid4().hex[:8]}"
        
        # First registration
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": unique_pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        
        # Second registration with same pseudo
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": unique_pseudo,
            "password": "differentpass",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 409
        assert "déjà utilisé" in response.json()["detail"]
        print("✓ Rejected duplicate pseudo")


class TestPseudonymousLogin:
    """Test pseudonymous login"""
    
    def test_login_success(self):
        """POST /api/auth/login - Login with valid credentials"""
        unique_pseudo = f"LoginTest_{uuid.uuid4().hex[:8]}"
        
        # Register first
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": unique_pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        
        # Login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": unique_pseudo,
            "password": "testpass123"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "token" in data
        assert data["pseudo"] == unique_pseudo
        assert data["auth_mode"] == "pseudo"
        print(f"✓ Login successful for {unique_pseudo}")
        return data
    
    def test_login_wrong_password(self):
        """POST /api/auth/login - Reject wrong password"""
        unique_pseudo = f"WrongPwd_{uuid.uuid4().hex[:8]}"
        
        # Register
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": unique_pseudo,
            "password": "correctpass",
            "consent_cgu": True,
            "consent_privacy": True
        })
        
        # Login with wrong password
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": unique_pseudo,
            "password": "wrongpass"
        })
        assert response.status_code == 401
        print("✓ Rejected wrong password")
    
    def test_login_nonexistent_pseudo(self):
        """POST /api/auth/login - Reject nonexistent pseudo"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "NonExistentUser12345",
            "password": "anypassword"
        })
        assert response.status_code == 401
        print("✓ Rejected nonexistent pseudo")


class TestCheckPseudo:
    """Test pseudo availability check"""
    
    def test_check_available_pseudo(self):
        """GET /api/auth/check-pseudo - Check available pseudo"""
        unique_pseudo = f"Available_{uuid.uuid4().hex[:8]}"
        response = requests.get(f"{BASE_URL}/api/auth/check-pseudo?pseudo={unique_pseudo}")
        assert response.status_code == 200
        assert response.json()["available"] == True
        print(f"✓ Pseudo {unique_pseudo} is available")
    
    def test_check_taken_pseudo(self):
        """GET /api/auth/check-pseudo - Check taken pseudo"""
        unique_pseudo = f"Taken_{uuid.uuid4().hex[:8]}"
        
        # Register first
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": unique_pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        
        # Check availability
        response = requests.get(f"{BASE_URL}/api/auth/check-pseudo?pseudo={unique_pseudo}")
        assert response.status_code == 200
        assert response.json()["available"] == False
        print(f"✓ Pseudo {unique_pseudo} is taken")
    
    def test_check_short_pseudo(self):
        """GET /api/auth/check-pseudo - Reject short pseudo"""
        response = requests.get(f"{BASE_URL}/api/auth/check-pseudo?pseudo=ab")
        assert response.status_code == 200
        assert response.json()["available"] == False
        assert "3 caractères" in response.json().get("reason", "")
        print("✓ Short pseudo rejected")


class TestVerifyToken:
    """Test token verification returns correct auth info"""
    
    def test_verify_pseudo_token(self):
        """GET /api/auth/verify - Returns auth_mode, pseudo, identity_level for pseudo account"""
        unique_pseudo = f"Verify_{uuid.uuid4().hex[:8]}"
        
        # Register
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": unique_pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        token = reg_resp.json()["token"]
        
        # Verify
        response = requests.get(f"{BASE_URL}/api/auth/verify?token={token}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == True
        assert data["auth_mode"] == "pseudo"
        assert data["pseudo"] == unique_pseudo
        assert data["identity_level"] == "none"
        print(f"✓ Verified pseudo token: auth_mode={data['auth_mode']}, pseudo={data['pseudo']}")


class TestUpgradeAccount:
    """Test upgrading anonymous account to pseudo"""
    
    def test_upgrade_success(self):
        """POST /api/auth/upgrade - Upgrade anonymous to pseudo"""
        # Create anonymous account
        anon_resp = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = anon_resp.json()["token"]
        
        unique_pseudo = f"Upgraded_{uuid.uuid4().hex[:8]}"
        
        # Upgrade
        response = requests.post(f"{BASE_URL}/api/auth/upgrade?token={token}", json={
            "pseudo": unique_pseudo,
            "password": "newpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["auth_mode"] == "pseudo"
        assert data["pseudo"] == unique_pseudo
        print(f"✓ Upgraded to pseudo: {unique_pseudo}")
    
    def test_upgrade_already_pseudo(self):
        """POST /api/auth/upgrade - Reject if already pseudo"""
        unique_pseudo = f"AlreadyPseudo_{uuid.uuid4().hex[:8]}"
        
        # Register pseudo account
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": unique_pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        token = reg_resp.json()["token"]
        
        # Try to upgrade
        response = requests.post(f"{BASE_URL}/api/auth/upgrade?token={token}", json={
            "pseudo": "NewPseudo",
            "password": "newpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 400
        assert "déjà" in response.json()["detail"]
        print("✓ Rejected upgrade for already pseudo account")


class TestChangePassword:
    """Test password change for pseudo accounts"""
    
    def test_change_password_success(self):
        """POST /api/auth/change-password - Change password successfully"""
        unique_pseudo = f"ChangePwd_{uuid.uuid4().hex[:8]}"
        
        # Register
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": unique_pseudo,
            "password": "oldpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        token = reg_resp.json()["token"]
        
        # Change password
        response = requests.post(f"{BASE_URL}/api/auth/change-password?token={token}", json={
            "current_password": "oldpass123",
            "new_password": "newpass456"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ Password changed successfully")
        
        # Verify can login with new password
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": unique_pseudo,
            "password": "newpass456"
        })
        assert login_resp.status_code == 200
        print("✓ Login with new password successful")
    
    def test_change_password_wrong_current(self):
        """POST /api/auth/change-password - Reject wrong current password"""
        unique_pseudo = f"WrongCurrent_{uuid.uuid4().hex[:8]}"
        
        # Register
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": unique_pseudo,
            "password": "correctpass",
            "consent_cgu": True,
            "consent_privacy": True
        })
        token = reg_resp.json()["token"]
        
        # Try to change with wrong current password
        response = requests.post(f"{BASE_URL}/api/auth/change-password?token={token}", json={
            "current_password": "wrongpass",
            "new_password": "newpass456"
        })
        assert response.status_code == 401
        print("✓ Rejected wrong current password")
    
    def test_change_password_anonymous_rejected(self):
        """POST /api/auth/change-password - Reject for anonymous accounts"""
        # Create anonymous account
        anon_resp = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        token = anon_resp.json()["token"]
        
        # Try to change password
        response = requests.post(f"{BASE_URL}/api/auth/change-password?token={token}", json={
            "current_password": "anypass",
            "new_password": "newpass456"
        })
        assert response.status_code == 400
        print("✓ Rejected password change for anonymous account")


class TestPrivacySettings:
    """Test privacy settings update"""
    
    def test_update_privacy_settings(self):
        """PUT /api/profile/privacy - Update visibility, display_name, bio, consent_marketing"""
        unique_pseudo = f"Privacy_{uuid.uuid4().hex[:8]}"
        
        # Register
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": unique_pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        token = reg_resp.json()["token"]
        
        # Update privacy settings
        response = requests.put(
            f"{BASE_URL}/api/profile/privacy?token={token}&visibility_level=limited&display_name=MyDisplayName&bio=My bio text&consent_marketing=true"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["visibility_level"] == "limited"
        assert data["display_name"] == "MyDisplayName"
        assert data["bio"] == "My bio text"
        assert data["consent_marketing"] == True
        print("✓ Privacy settings updated")
    
    def test_visibility_levels(self):
        """PUT /api/profile/privacy - Test all visibility levels"""
        unique_pseudo = f"Visibility_{uuid.uuid4().hex[:8]}"
        
        # Register
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": unique_pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        token = reg_resp.json()["token"]
        
        for level in ["private", "limited", "public"]:
            response = requests.put(f"{BASE_URL}/api/profile/privacy?token={token}&visibility_level={level}")
            assert response.status_code == 200
            assert response.json()["visibility_level"] == level
            print(f"✓ Visibility level '{level}' set successfully")


class TestProfileNoPasswordHash:
    """Test that profile endpoint never returns password_hash"""
    
    def test_get_profile_no_password(self):
        """GET /api/profile - Should NOT return password_hash"""
        unique_pseudo = f"NoHash_{uuid.uuid4().hex[:8]}"
        
        # Register
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": unique_pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        token = reg_resp.json()["token"]
        
        # Get profile
        response = requests.get(f"{BASE_URL}/api/profile?token={token}")
        assert response.status_code == 200
        
        data = response.json()
        assert "password_hash" not in data, "password_hash should not be in profile response"
        assert data["pseudo"] == unique_pseudo
        print("✓ Profile does not contain password_hash")


class TestExportData:
    """Test data export functionality"""
    
    def test_export_data(self):
        """GET /api/auth/export-data - Export all user data as JSON"""
        unique_pseudo = f"Export_{uuid.uuid4().hex[:8]}"
        
        # Register
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": unique_pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        token = reg_resp.json()["token"]
        
        # Export data
        response = requests.get(f"{BASE_URL}/api/auth/export-data?token={token}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "export_date" in data
        assert "profile" in data
        assert "consent_history" in data
        assert "password_hash" not in data.get("profile", {}), "password_hash should not be in export"
        print(f"✓ Data exported successfully, keys: {list(data.keys())}")


class TestDeleteAccount:
    """Test account deletion"""
    
    def test_delete_account(self):
        """DELETE /api/auth/account - Delete account and all associated data"""
        unique_pseudo = f"Delete_{uuid.uuid4().hex[:8]}"
        
        # Register
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": unique_pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        token = reg_resp.json()["token"]
        
        # Delete account
        response = requests.delete(f"{BASE_URL}/api/auth/account?token={token}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ Account deleted")
        
        # Verify token no longer works
        verify_resp = requests.get(f"{BASE_URL}/api/auth/verify?token={token}")
        assert verify_resp.status_code in [401, 404], "Token should be invalid after deletion"
        print("✓ Token invalid after deletion")
        
        # Verify cannot login with deleted pseudo
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": unique_pseudo,
            "password": "testpass123"
        })
        assert login_resp.status_code == 401
        print("✓ Cannot login with deleted account")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
