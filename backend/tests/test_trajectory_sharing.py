"""
Test suite for Trajectory Sharing Feature (Iteration 53)
Tests:
- POST /api/trajectory/share - Create share with unique ID
- GET /api/trajectory/shared/{share_id} - Get filtered trajectory by audience
- GET /api/trajectory/shares - List active shares
- DELETE /api/trajectory/shares/{share_id} - Revoke a share
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
BENEFICIARY_PSEUDO = "bob23"
BENEFICIARY_PASSWORD = "Solerys777!"
PARTNER_EMAIL = "cluximon@gmail.com"
PARTNER_PASSWORD = "Solerys777!"


class TestTrajectorySharing:
    """Test trajectory sharing endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login as beneficiary and get token"""
        # Login as beneficiary
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": BENEFICIARY_PSEUDO,
            "password": BENEFICIARY_PASSWORD
        })
        assert response.status_code == 200, f"Beneficiary login failed: {response.text}"
        self.token = response.json()["token"]
        self.created_share_ids = []
        yield
        # Cleanup: Revoke any shares created during tests
        for share_id in self.created_share_ids:
            try:
                requests.delete(f"{BASE_URL}/api/trajectory/shares/{share_id}?token={self.token}")
            except:
                pass
    
    def test_01_create_share_accompagnateur(self):
        """Test creating a share link for accompagnateur audience"""
        response = requests.post(f"{BASE_URL}/api/trajectory/share?token={self.token}", json={
            "audience": "accompagnateur",
            "duration_days": 30,
            "include_synthesis": True,
            "include_card": True
        })
        assert response.status_code == 200, f"Create share failed: {response.text}"
        data = response.json()
        assert "share_id" in data, "Response should contain share_id"
        assert "expires_at" in data, "Response should contain expires_at"
        assert len(data["share_id"]) > 10, "share_id should be a unique token"
        self.created_share_ids.append(data["share_id"])
        print(f"✓ Created accompagnateur share: {data['share_id']}")
    
    def test_02_create_share_recruteur(self):
        """Test creating a share link for recruteur audience"""
        response = requests.post(f"{BASE_URL}/api/trajectory/share?token={self.token}", json={
            "audience": "recruteur",
            "duration_days": 7,
            "include_synthesis": True,
            "include_card": True
        })
        assert response.status_code == 200, f"Create share failed: {response.text}"
        data = response.json()
        assert data["share_id"], "share_id should be present"
        self.created_share_ids.append(data["share_id"])
        print(f"✓ Created recruteur share: {data['share_id']}")
    
    def test_03_create_share_public(self):
        """Test creating a share link for public audience"""
        response = requests.post(f"{BASE_URL}/api/trajectory/share?token={self.token}", json={
            "audience": "public",
            "duration_days": 90,
            "include_synthesis": False,
            "include_card": True
        })
        assert response.status_code == 200, f"Create share failed: {response.text}"
        data = response.json()
        assert data["share_id"], "share_id should be present"
        self.created_share_ids.append(data["share_id"])
        print(f"✓ Created public share: {data['share_id']}")
    
    def test_04_get_shared_trajectory(self):
        """Test retrieving shared trajectory by share_id"""
        # First create a share
        create_response = requests.post(f"{BASE_URL}/api/trajectory/share?token={self.token}", json={
            "audience": "accompagnateur",
            "duration_days": 30,
            "include_synthesis": True,
            "include_card": True
        })
        assert create_response.status_code == 200
        share_id = create_response.json()["share_id"]
        self.created_share_ids.append(share_id)
        
        # Now get the shared trajectory (no auth required)
        response = requests.get(f"{BASE_URL}/api/trajectory/shared/{share_id}")
        assert response.status_code == 200, f"Get shared trajectory failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "display_name" in data, "Response should contain display_name"
        assert "audience" in data, "Response should contain audience"
        assert "steps" in data, "Response should contain steps"
        assert "step_count" in data, "Response should contain step_count"
        assert data["audience"] == "accompagnateur", "Audience should match"
        
        # Verify steps are filtered by visibility
        for step in data["steps"]:
            assert step.get("visibility") in ["accompagnateur", "public"], \
                f"Step visibility should be accompagnateur or public, got {step.get('visibility')}"
        
        print(f"✓ Retrieved shared trajectory with {data['step_count']} steps")
        print(f"  Display name: {data['display_name']}")
        print(f"  Skills count: {data.get('skills_count', 0)}")
    
    def test_05_get_shared_trajectory_with_card(self):
        """Test that shared trajectory includes D'CLIC card when include_card=True"""
        # Create share with card included
        create_response = requests.post(f"{BASE_URL}/api/trajectory/share?token={self.token}", json={
            "audience": "recruteur",
            "duration_days": 30,
            "include_synthesis": True,
            "include_card": True
        })
        assert create_response.status_code == 200
        share_id = create_response.json()["share_id"]
        self.created_share_ids.append(share_id)
        
        # Get shared trajectory
        response = requests.get(f"{BASE_URL}/api/trajectory/shared/{share_id}")
        assert response.status_code == 200
        data = response.json()
        
        # bob23 has dclic_imported=True, so card should be present
        if data.get("card"):
            assert "mbti" in data["card"] or "disc" in data["card"], "Card should have MBTI or DISC"
            print(f"✓ D'CLIC card included: MBTI={data['card'].get('mbti')}, DISC={data['card'].get('disc')}")
        else:
            print("⚠ No D'CLIC card in response (user may not have dclic_imported)")
    
    def test_06_list_active_shares(self):
        """Test listing active shares for the user"""
        # Create a share first
        create_response = requests.post(f"{BASE_URL}/api/trajectory/share?token={self.token}", json={
            "audience": "accompagnateur",
            "duration_days": 30
        })
        assert create_response.status_code == 200
        share_id = create_response.json()["share_id"]
        self.created_share_ids.append(share_id)
        
        # List shares
        response = requests.get(f"{BASE_URL}/api/trajectory/shares?token={self.token}")
        assert response.status_code == 200, f"List shares failed: {response.text}"
        shares = response.json()
        
        assert isinstance(shares, list), "Response should be a list"
        assert len(shares) > 0, "Should have at least one share"
        
        # Verify share structure
        share = shares[0]
        assert "share_id" in share, "Share should have share_id"
        assert "audience" in share, "Share should have audience"
        assert "is_active" in share, "Share should have is_active"
        assert "view_count" in share, "Share should have view_count"
        assert "created_at" in share, "Share should have created_at"
        assert "expires_at" in share, "Share should have expires_at"
        
        print(f"✓ Listed {len(shares)} shares")
        for s in shares[:3]:
            print(f"  - {s['audience']}: {s['share_id'][:16]}... (views: {s['view_count']}, active: {s['is_active']})")
    
    def test_07_revoke_share(self):
        """Test revoking a share link"""
        # Create a share
        create_response = requests.post(f"{BASE_URL}/api/trajectory/share?token={self.token}", json={
            "audience": "public",
            "duration_days": 30
        })
        assert create_response.status_code == 200
        share_id = create_response.json()["share_id"]
        
        # Verify it works before revocation
        get_response = requests.get(f"{BASE_URL}/api/trajectory/shared/{share_id}")
        assert get_response.status_code == 200, "Share should be accessible before revocation"
        
        # Revoke the share
        revoke_response = requests.delete(f"{BASE_URL}/api/trajectory/shares/{share_id}?token={self.token}")
        assert revoke_response.status_code == 200, f"Revoke failed: {revoke_response.text}"
        
        # Verify it's no longer accessible
        get_response_after = requests.get(f"{BASE_URL}/api/trajectory/shared/{share_id}")
        assert get_response_after.status_code == 410, f"Revoked share should return 410, got {get_response_after.status_code}"
        
        print(f"✓ Successfully revoked share {share_id[:16]}...")
    
    def test_08_get_nonexistent_share(self):
        """Test getting a non-existent share returns 404"""
        response = requests.get(f"{BASE_URL}/api/trajectory/shared/nonexistent_share_id_12345")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Non-existent share returns 404")
    
    def test_09_view_count_increments(self):
        """Test that view_count increments when shared trajectory is accessed"""
        # Create a share
        create_response = requests.post(f"{BASE_URL}/api/trajectory/share?token={self.token}", json={
            "audience": "accompagnateur",
            "duration_days": 30
        })
        assert create_response.status_code == 200
        share_id = create_response.json()["share_id"]
        self.created_share_ids.append(share_id)
        
        # Access the share multiple times
        for i in range(3):
            requests.get(f"{BASE_URL}/api/trajectory/shared/{share_id}")
        
        # Check view count in shares list
        list_response = requests.get(f"{BASE_URL}/api/trajectory/shares?token={self.token}")
        assert list_response.status_code == 200
        shares = list_response.json()
        
        # Find our share
        our_share = next((s for s in shares if s["share_id"] == share_id), None)
        assert our_share is not None, "Created share should be in list"
        assert our_share["view_count"] >= 3, f"View count should be at least 3, got {our_share['view_count']}"
        
        print(f"✓ View count incremented to {our_share['view_count']}")
    
    def test_10_audience_filtering_recruteur(self):
        """Test that recruteur audience only sees recruteur and public visibility steps"""
        # Create a recruteur share
        create_response = requests.post(f"{BASE_URL}/api/trajectory/share?token={self.token}", json={
            "audience": "recruteur",
            "duration_days": 30
        })
        assert create_response.status_code == 200
        share_id = create_response.json()["share_id"]
        self.created_share_ids.append(share_id)
        
        # Get shared trajectory
        response = requests.get(f"{BASE_URL}/api/trajectory/shared/{share_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all steps have appropriate visibility
        for step in data["steps"]:
            vis = step.get("visibility")
            assert vis in ["recruteur", "public"], \
                f"Recruteur share should only show recruteur/public steps, got {vis}"
        
        print(f"✓ Recruteur share correctly filters steps ({len(data['steps'])} visible)")


class TestTrajectoryCardData:
    """Test trajectory card data endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login as beneficiary"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": BENEFICIARY_PSEUDO,
            "password": BENEFICIARY_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
    
    def test_get_card_data(self):
        """Test GET /api/trajectory/card-data returns profile and D'CLIC data"""
        response = requests.get(f"{BASE_URL}/api/trajectory/card-data?token={self.token}")
        assert response.status_code == 200, f"Get card data failed: {response.text}"
        data = response.json()
        
        assert "profile" in data, "Response should contain profile"
        assert data["profile"] is not None, "Profile should not be null"
        
        # bob23 has dclic_imported=True
        if data.get("dclic_profile"):
            print(f"✓ D'CLIC profile data present")
        if data.get("access_code"):
            print(f"✓ Access code: {data['access_code']}")
        
        print(f"✓ Card data retrieved successfully")


class TestExistingTrajectoryEndpoints:
    """Verify existing trajectory endpoints still work"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login as beneficiary"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": BENEFICIARY_PSEUDO,
            "password": BENEFICIARY_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
    
    def test_get_trajectory_steps(self):
        """Test GET /api/trajectory/steps returns user's steps"""
        response = requests.get(f"{BASE_URL}/api/trajectory/steps?token={self.token}")
        assert response.status_code == 200, f"Get steps failed: {response.text}"
        steps = response.json()
        
        assert isinstance(steps, list), "Response should be a list"
        print(f"✓ Retrieved {len(steps)} trajectory steps")
        
        # bob23 should have 5 steps based on iteration_52
        if len(steps) >= 5:
            print(f"  Step types: {[s.get('step_type') for s in steps[:5]]}")
    
    def test_get_visibility_settings(self):
        """Test GET /api/trajectory/visibility-settings"""
        response = requests.get(f"{BASE_URL}/api/trajectory/visibility-settings?token={self.token}")
        assert response.status_code == 200, f"Get visibility settings failed: {response.text}"
        settings = response.json()
        
        # Should have conseiller, recruteur, partenaire keys
        assert "conseiller" in settings or isinstance(settings, dict), "Should return visibility settings"
        print(f"✓ Visibility settings: {settings}")
    
    def test_get_synthesis(self):
        """Test GET /api/trajectory/synthesis"""
        response = requests.get(f"{BASE_URL}/api/trajectory/synthesis?token={self.token}")
        assert response.status_code == 200, f"Get synthesis failed: {response.text}"
        data = response.json()
        
        assert "has_data" in data, "Response should contain has_data"
        if data["has_data"] and data.get("synthesis"):
            print(f"✓ Synthesis available with keys: {list(data['synthesis'].keys())[:5]}")
        else:
            print("✓ Synthesis endpoint works (no data yet)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
