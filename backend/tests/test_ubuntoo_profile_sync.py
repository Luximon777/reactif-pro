"""
Test suite for Ubuntoo Profile Sync API endpoints
Tests GET /api/ubuntoo/profile and POST /api/ubuntoo/sync-profile
User bob22 has passport but NO CV/DCLIC data
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://journey-partners-1.preview.emergentagent.com').rstrip('/')


class TestUbuntooProfileEndpoints:
    """Tests for Ubuntoo profile sync endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login with bob22 and get token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"pseudo": "bob22", "password": "Solerys777!"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in login response"
        print(f"✓ Logged in as bob22, token: {data['token'][:20]}...")
        return data["token"]
    
    def test_get_profile_without_token_returns_not_synced(self):
        """GET /api/ubuntoo/profile without token returns synced:false"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/profile")
        assert response.status_code == 200
        data = response.json()
        assert data["synced"] == False
        assert data["profile"] is None
        print("✓ GET profile without token returns synced:false")
    
    def test_get_profile_with_invalid_token_returns_not_synced(self):
        """GET /api/ubuntoo/profile with invalid token returns synced:false"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/profile?token=invalid_token_xyz")
        assert response.status_code == 200
        data = response.json()
        assert data["synced"] == False
        assert data["profile"] is None
        print("✓ GET profile with invalid token returns synced:false")
    
    def test_get_profile_with_valid_token_before_sync(self, auth_token):
        """GET /api/ubuntoo/profile with valid token before sync returns synced:false or true"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/profile?token={auth_token}")
        assert response.status_code == 200
        data = response.json()
        # Could be synced or not depending on previous tests
        assert "synced" in data
        assert "profile" in data
        assert "has_dclic" in data
        assert "has_cv" in data
        print(f"✓ GET profile with valid token: synced={data['synced']}, has_dclic={data['has_dclic']}, has_cv={data['has_cv']}")
    
    def test_sync_profile_without_token_fails(self):
        """POST /api/ubuntoo/sync-profile without token returns 401"""
        response = requests.post(f"{BASE_URL}/api/ubuntoo/sync-profile")
        assert response.status_code == 401
        print("✓ POST sync-profile without token returns 401")
    
    def test_sync_profile_with_invalid_token_fails(self):
        """POST /api/ubuntoo/sync-profile with invalid token returns 404"""
        response = requests.post(f"{BASE_URL}/api/ubuntoo/sync-profile?token=invalid_token_xyz")
        assert response.status_code == 404
        print("✓ POST sync-profile with invalid token returns 404")
    
    def test_sync_profile_with_valid_token_creates_profile(self, auth_token):
        """POST /api/ubuntoo/sync-profile creates ubuntoo profile"""
        response = requests.post(
            f"{BASE_URL}/api/ubuntoo/sync-profile?token={auth_token}",
            timeout=30  # AI may take time
        )
        assert response.status_code == 200, f"Sync failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "profile" in data
        assert "message" in data
        assert "ai_generated" in data
        
        profile = data["profile"]
        assert "token_id" in profile
        assert "pseudo" in profile
        assert "status" in profile
        assert "trust" in profile
        assert "softskills" in profile
        assert "badges" in profile
        assert "synced_at" in profile
        assert "synced_from" in profile
        
        print(f"✓ Sync profile created successfully")
        print(f"  Pseudo: {profile.get('pseudo')}")
        print(f"  Status: {profile.get('status')}")
        print(f"  Trust: {profile.get('trust')}")
        print(f"  AI generated: {data.get('ai_generated')}")
        print(f"  Synced from: {profile.get('synced_from')}")
    
    def test_get_profile_after_sync_returns_synced_true(self, auth_token):
        """GET /api/ubuntoo/profile after sync returns synced:true with profile data"""
        # First ensure profile is synced
        sync_response = requests.post(
            f"{BASE_URL}/api/ubuntoo/sync-profile?token={auth_token}",
            timeout=30
        )
        assert sync_response.status_code == 200
        
        # Now get profile
        response = requests.get(f"{BASE_URL}/api/ubuntoo/profile?token={auth_token}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["synced"] == True
        assert data["profile"] is not None
        
        profile = data["profile"]
        assert "pseudo" in profile
        assert "status" in profile
        assert "trust" in profile
        assert "softskills" in profile
        assert "synced_at" in profile
        
        print(f"✓ GET profile after sync returns synced:true")
        print(f"  Profile pseudo: {profile.get('pseudo')}")
        print(f"  Profile status: {profile.get('status')}")
    
    def test_resync_profile_updates_synced_at(self, auth_token):
        """POST /api/ubuntoo/sync-profile again updates synced_at timestamp"""
        # First sync
        first_response = requests.post(
            f"{BASE_URL}/api/ubuntoo/sync-profile?token={auth_token}",
            timeout=30
        )
        assert first_response.status_code == 200
        first_synced_at = first_response.json()["profile"]["synced_at"]
        
        # Wait a bit
        time.sleep(1)
        
        # Second sync
        second_response = requests.post(
            f"{BASE_URL}/api/ubuntoo/sync-profile?token={auth_token}",
            timeout=30
        )
        assert second_response.status_code == 200
        second_synced_at = second_response.json()["profile"]["synced_at"]
        
        # Timestamps should be different
        assert second_synced_at != first_synced_at, "synced_at should update on resync"
        print(f"✓ Resync updates synced_at: {first_synced_at[:19]} → {second_synced_at[:19]}")


class TestUbuntooProfileDataIntegrity:
    """Tests for profile data integrity and persistence"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login with bob22 and get token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"pseudo": "bob22", "password": "Solerys777!"}
        )
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_profile_has_synced_from_sources(self, auth_token):
        """Profile includes synced_from with source flags"""
        # Sync first
        requests.post(f"{BASE_URL}/api/ubuntoo/sync-profile?token={auth_token}", timeout=30)
        
        # Get profile
        response = requests.get(f"{BASE_URL}/api/ubuntoo/profile?token={auth_token}")
        assert response.status_code == 200
        profile = response.json()["profile"]
        
        assert "synced_from" in profile
        synced_from = profile["synced_from"]
        assert "dclic_pro" in synced_from
        assert "cv_analysis" in synced_from
        assert "passport" in synced_from
        
        print(f"✓ Profile has synced_from: dclic_pro={synced_from['dclic_pro']}, cv_analysis={synced_from['cv_analysis']}, passport={synced_from['passport']}")
    
    def test_profile_trust_score_is_valid(self, auth_token):
        """Profile trust score is between 0 and 100"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/profile?token={auth_token}")
        assert response.status_code == 200
        profile = response.json()["profile"]
        
        if profile:
            trust = profile.get("trust", 0)
            assert 0 <= trust <= 100, f"Trust score {trust} out of range"
            print(f"✓ Trust score is valid: {trust}")
    
    def test_profile_status_is_valid(self, auth_token):
        """Profile status is one of expected values"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/profile?token={auth_token}")
        assert response.status_code == 200
        profile = response.json()["profile"]
        
        if profile:
            valid_statuses = ["Accompagné", "Membre actif", "Pair-aidant", "Mentor", "Ambassadeur"]
            status = profile.get("status", "")
            assert status in valid_statuses, f"Invalid status: {status}"
            print(f"✓ Profile status is valid: {status}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
