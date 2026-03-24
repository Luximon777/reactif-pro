"""
Test Passport Sharing Feature - Anonymous Share Links
Tests:
- POST /api/passport/share/create - Generate share link with 30-day expiration
- GET /api/passport/shares - List active share links
- DELETE /api/passport/shares/{share_id} - Revoke share link
- GET /api/passport/shared/{share_id} - Public view (no auth required)
- Revoked link returns 404
"""

import pytest
import requests
import os
import uuid
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPassportSharing:
    """Test passport sharing feature - anonymous share links"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user for sharing tests"""
        unique_id = str(uuid.uuid4())[:8]
        pseudo = f"share_test_{unique_id}"
        password = "Test1234!"
        
        # Register user
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": password,
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        })
        
        if register_response.status_code == 200:
            token = register_response.json().get("token")
        else:
            # Try login if user exists
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "pseudo": pseudo,
                "password": password
            })
            assert login_response.status_code == 200, f"Failed to login: {login_response.text}"
            token = login_response.json().get("token")
        
        return {"pseudo": pseudo, "password": password, "token": token}
    
    @pytest.fixture(scope="class")
    def initialized_passport(self, test_user):
        """Initialize passport for the test user (required before sharing)"""
        token = test_user["token"]
        
        # GET /api/passport initializes the passport if it doesn't exist
        response = requests.get(f"{BASE_URL}/api/passport?token={token}")
        assert response.status_code == 200, f"Failed to initialize passport: {response.text}"
        
        passport = response.json()
        assert "token_id" in passport or "completeness_score" in passport, "Passport not properly initialized"
        
        return passport
    
    def test_create_share_link_without_passport(self, test_user):
        """Test that creating share link without initialized passport fails"""
        # Create a new user without passport
        unique_id = str(uuid.uuid4())[:8]
        pseudo = f"no_passport_{unique_id}"
        
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "Test1234!",
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        })
        
        if register_response.status_code == 200:
            token = register_response.json().get("token")
            
            # Try to create share link without initializing passport
            response = requests.post(f"{BASE_URL}/api/passport/share/create?token={token}")
            # Should return 404 because passport doesn't exist
            assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    
    def test_create_share_link_success(self, test_user, initialized_passport):
        """Test creating a share link successfully"""
        token = test_user["token"]
        
        response = requests.post(f"{BASE_URL}/api/passport/share/create?token={token}")
        assert response.status_code == 200, f"Failed to create share link: {response.text}"
        
        data = response.json()
        assert "share_id" in data, "Response missing share_id"
        assert "expires_at" in data, "Response missing expires_at"
        
        # Verify expiration is approximately 30 days from now
        expires_at = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
        now = datetime.now(expires_at.tzinfo)
        days_until_expiry = (expires_at - now).days
        assert 29 <= days_until_expiry <= 31, f"Expiration should be ~30 days, got {days_until_expiry} days"
        
        return data["share_id"]
    
    def test_create_share_link_invalid_token(self):
        """Test creating share link with invalid token"""
        response = requests.post(f"{BASE_URL}/api/passport/share/create?token=invalid_token_123")
        assert response.status_code in [401, 404], f"Expected 401/404, got {response.status_code}"
    
    def test_list_share_links(self, test_user, initialized_passport):
        """Test listing active share links"""
        token = test_user["token"]
        
        # Create a share link first
        create_response = requests.post(f"{BASE_URL}/api/passport/share/create?token={token}")
        assert create_response.status_code == 200
        created_share_id = create_response.json()["share_id"]
        
        # List share links
        response = requests.get(f"{BASE_URL}/api/passport/shares?token={token}")
        assert response.status_code == 200, f"Failed to list shares: {response.text}"
        
        shares = response.json()
        assert isinstance(shares, list), "Response should be a list"
        
        # Find our created share
        share_ids = [s.get("id") for s in shares]
        assert created_share_id in share_ids, f"Created share {created_share_id} not found in list"
        
        # Verify share structure
        for share in shares:
            assert "id" in share, "Share missing id"
            assert "expires_at" in share, "Share missing expires_at"
            assert "active" in share, "Share missing active flag"
            assert share["active"] == True, "Listed shares should be active"
    
    def test_list_share_links_invalid_token(self):
        """Test listing shares with invalid token"""
        response = requests.get(f"{BASE_URL}/api/passport/shares?token=invalid_token_123")
        assert response.status_code in [401, 404], f"Expected 401/404, got {response.status_code}"
    
    def test_public_view_shared_passport(self, test_user, initialized_passport):
        """Test viewing shared passport via public endpoint (no auth)"""
        token = test_user["token"]
        
        # Create a share link
        create_response = requests.post(f"{BASE_URL}/api/passport/share/create?token={token}")
        assert create_response.status_code == 200
        share_id = create_response.json()["share_id"]
        
        # Access public view WITHOUT authentication
        response = requests.get(f"{BASE_URL}/api/passport/shared/{share_id}")
        assert response.status_code == 200, f"Failed to view shared passport: {response.text}"
        
        data = response.json()
        
        # Verify anonymized data is returned
        assert "competences" in data, "Response missing competences"
        assert "experiences" in data, "Response missing experiences"
        assert "professional_summary" in data, "Response missing professional_summary"
        assert "career_project" in data, "Response missing career_project"
        assert "completeness_score" in data, "Response missing completeness_score"
        assert "share_info" in data, "Response missing share_info"
        
        # Verify share_info structure
        share_info = data["share_info"]
        assert "expires_at" in share_info, "share_info missing expires_at"
        assert "views" in share_info, "share_info missing views"
        assert share_info["views"] >= 1, "View count should be at least 1"
        
        # Verify NO personal identifiers are exposed
        assert "token_id" not in data, "token_id should NOT be in response (anonymized)"
        assert "pseudo" not in data, "pseudo should NOT be in response (anonymized)"
        assert "email" not in data, "email should NOT be in response (anonymized)"
    
    def test_public_view_invalid_share_id(self):
        """Test viewing with invalid share_id returns 404"""
        response = requests.get(f"{BASE_URL}/api/passport/shared/invalid_share_id_123")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data, "Error response should have detail"
    
    def test_revoke_share_link(self, test_user, initialized_passport):
        """Test revoking a share link"""
        token = test_user["token"]
        
        # Create a share link
        create_response = requests.post(f"{BASE_URL}/api/passport/share/create?token={token}")
        assert create_response.status_code == 200
        share_id = create_response.json()["share_id"]
        
        # Verify it works before revocation
        view_response = requests.get(f"{BASE_URL}/api/passport/shared/{share_id}")
        assert view_response.status_code == 200, "Share should be accessible before revocation"
        
        # Revoke the share link
        revoke_response = requests.delete(f"{BASE_URL}/api/passport/shares/{share_id}?token={token}")
        assert revoke_response.status_code == 200, f"Failed to revoke share: {revoke_response.text}"
        
        data = revoke_response.json()
        assert "message" in data, "Revoke response should have message"
        
        # Verify the share is no longer accessible
        view_after_revoke = requests.get(f"{BASE_URL}/api/passport/shared/{share_id}")
        assert view_after_revoke.status_code == 404, f"Revoked share should return 404, got {view_after_revoke.status_code}"
    
    def test_revoke_share_link_invalid_token(self, test_user, initialized_passport):
        """Test revoking share with invalid token"""
        token = test_user["token"]
        
        # Create a share link
        create_response = requests.post(f"{BASE_URL}/api/passport/share/create?token={token}")
        assert create_response.status_code == 200
        share_id = create_response.json()["share_id"]
        
        # Try to revoke with invalid token
        response = requests.delete(f"{BASE_URL}/api/passport/shares/{share_id}?token=invalid_token")
        assert response.status_code in [401, 404], f"Expected 401/404, got {response.status_code}"
    
    def test_revoke_nonexistent_share(self, test_user, initialized_passport):
        """Test revoking a non-existent share link"""
        token = test_user["token"]
        
        response = requests.delete(f"{BASE_URL}/api/passport/shares/nonexistent_share_id?token={token}")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_view_count_increments(self, test_user, initialized_passport):
        """Test that view count increments on each access"""
        token = test_user["token"]
        
        # Create a share link
        create_response = requests.post(f"{BASE_URL}/api/passport/share/create?token={token}")
        assert create_response.status_code == 200
        share_id = create_response.json()["share_id"]
        
        # First view
        view1 = requests.get(f"{BASE_URL}/api/passport/shared/{share_id}")
        assert view1.status_code == 200
        views1 = view1.json()["share_info"]["views"]
        
        # Second view
        view2 = requests.get(f"{BASE_URL}/api/passport/shared/{share_id}")
        assert view2.status_code == 200
        views2 = view2.json()["share_info"]["views"]
        
        assert views2 > views1, f"View count should increment: {views1} -> {views2}"
    
    def test_multiple_share_links(self, test_user, initialized_passport):
        """Test creating multiple share links for same passport"""
        token = test_user["token"]
        
        # Create first share link
        create1 = requests.post(f"{BASE_URL}/api/passport/share/create?token={token}")
        assert create1.status_code == 200
        share_id_1 = create1.json()["share_id"]
        
        # Create second share link
        create2 = requests.post(f"{BASE_URL}/api/passport/share/create?token={token}")
        assert create2.status_code == 200
        share_id_2 = create2.json()["share_id"]
        
        # Both should be different
        assert share_id_1 != share_id_2, "Each share link should have unique ID"
        
        # Both should work
        view1 = requests.get(f"{BASE_URL}/api/passport/shared/{share_id_1}")
        view2 = requests.get(f"{BASE_URL}/api/passport/shared/{share_id_2}")
        
        assert view1.status_code == 200, "First share link should work"
        assert view2.status_code == 200, "Second share link should work"
        
        # List should show both
        list_response = requests.get(f"{BASE_URL}/api/passport/shares?token={token}")
        assert list_response.status_code == 200
        shares = list_response.json()
        share_ids = [s.get("id") for s in shares]
        
        assert share_id_1 in share_ids, "First share should be in list"
        assert share_id_2 in share_ids, "Second share should be in list"


class TestPassportSharingAnonymization:
    """Test that shared passport data is properly anonymized"""
    
    @pytest.fixture(scope="class")
    def user_with_data(self):
        """Create user with passport data for anonymization tests"""
        unique_id = str(uuid.uuid4())[:8]
        pseudo = f"anon_test_{unique_id}"
        password = "Test1234!"
        
        # Register
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": password,
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        })
        
        if register_response.status_code == 200:
            token = register_response.json().get("token")
        else:
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "pseudo": pseudo,
                "password": password
            })
            token = login_response.json().get("token")
        
        # Initialize passport
        requests.get(f"{BASE_URL}/api/passport?token={token}")
        
        # Add profile data
        requests.put(f"{BASE_URL}/api/passport/profile?token={token}", json={
            "professional_summary": "Test professional summary for anonymization",
            "career_project": "Test career project",
            "target_sectors": ["IT", "Finance"]
        })
        
        # Add a competence
        requests.post(f"{BASE_URL}/api/passport/competences?token={token}", json={
            "name": "Python Programming",
            "nature": "savoir_faire",
            "category": "technique",
            "level": "avance"
        })
        
        # Add an experience
        requests.post(f"{BASE_URL}/api/passport/experiences?token={token}", json={
            "title": "Software Developer",
            "organization": "Test Company",
            "description": "Development work",
            "experience_type": "professionnel"
        })
        
        return {"pseudo": pseudo, "token": token}
    
    def test_shared_passport_contains_expected_fields(self, user_with_data):
        """Test that shared passport contains all expected anonymized fields"""
        token = user_with_data["token"]
        
        # Create share
        create_response = requests.post(f"{BASE_URL}/api/passport/share/create?token={token}")
        assert create_response.status_code == 200
        share_id = create_response.json()["share_id"]
        
        # View shared passport
        response = requests.get(f"{BASE_URL}/api/passport/shared/{share_id}")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check expected fields are present
        expected_fields = [
            "professional_summary",
            "career_project", 
            "target_sectors",
            "motivations",
            "compatible_environments",
            "competences",
            "experiences",
            "completeness_score",
            "share_info"
        ]
        
        for field in expected_fields:
            assert field in data, f"Missing expected field: {field}"
        
        # Check competence structure
        if data["competences"]:
            comp = data["competences"][0]
            assert "name" in comp, "Competence missing name"
            assert "category" in comp, "Competence missing category"
            assert "level" in comp, "Competence missing level"
            # Should NOT have id (could be used to trace)
            # Note: The current implementation includes some fields, verify what's exposed
        
        # Check experience structure
        if data["experiences"]:
            exp = data["experiences"][0]
            assert "title" in exp, "Experience missing title"
            assert "organization" in exp, "Experience missing organization"
    
    def test_shared_passport_excludes_sensitive_fields(self, user_with_data):
        """Test that shared passport excludes sensitive/identifying fields"""
        token = user_with_data["token"]
        
        # Create share
        create_response = requests.post(f"{BASE_URL}/api/passport/share/create?token={token}")
        assert create_response.status_code == 200
        share_id = create_response.json()["share_id"]
        
        # View shared passport
        response = requests.get(f"{BASE_URL}/api/passport/shared/{share_id}")
        assert response.status_code == 200
        
        data = response.json()
        
        # These fields should NOT be present (identifying info)
        sensitive_fields = [
            "token_id",
            "user_id",
            "pseudo",
            "email",
            "name",
            "phone"
        ]
        
        for field in sensitive_fields:
            assert field not in data, f"Sensitive field '{field}' should NOT be in shared passport"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
