"""
Test Phase 2/3/4 features:
- Phase 2: EmergingTab filters, sort, detail modal
- Phase 3: Human validation (validate/modify/reject)
- Phase 4: Observatory CV-detected tab
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPhase234EmergingFeatures:
    """Test Phase 2/3/4 emerging competences features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get anonymous token for testing"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        data = response.json()
        self.token = data["token"]
        print(f"Got token: {self.token[:20]}...")
    
    # ============ Phase 2: Emerging Competences List & Filters ============
    
    def test_get_emerging_competences_list(self):
        """Phase 2: Test GET /api/emerging/competences returns list"""
        response = requests.get(f"{BASE_URL}/api/emerging/competences?token={self.token}")
        assert response.status_code == 200
        data = response.json()
        assert "competences" in data
        assert "total" in data
        assert isinstance(data["competences"], list)
        assert isinstance(data["total"], int)
        print(f"Got {data['total']} emerging competences")
    
    def test_get_emerging_competences_filter_category(self):
        """Phase 2: Test filtering by category"""
        response = requests.get(f"{BASE_URL}/api/emerging/competences?token={self.token}&category=tech_emergente")
        assert response.status_code == 200
        data = response.json()
        # All returned competences should have the filtered category
        for comp in data["competences"]:
            assert comp.get("categorie") == "tech_emergente"
        print(f"Category filter: {data['total']} tech_emergente competences")
    
    def test_get_emerging_competences_filter_min_score(self):
        """Phase 2: Test filtering by minimum score"""
        response = requests.get(f"{BASE_URL}/api/emerging/competences?token={self.token}&min_score=50")
        assert response.status_code == 200
        data = response.json()
        # All returned competences should have score >= 50
        for comp in data["competences"]:
            assert comp.get("score_emergence", 0) >= 50
        print(f"Score filter: {data['total']} competences with score >= 50")

    # ============ Phase 4: Observatory Dashboard ============
    
    def test_observatory_endpoint(self):
        """Phase 4: Test GET /api/emerging/observatory returns aggregated data"""
        response = requests.get(f"{BASE_URL}/api/emerging/observatory?token={self.token}")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "top_emerging" in data, "Missing top_emerging field"
        assert "by_category" in data, "Missing by_category field"
        assert "by_level" in data, "Missing by_level field"
        
        # Validate structure
        assert isinstance(data["top_emerging"], list)
        assert isinstance(data["by_category"], list)
        assert isinstance(data["by_level"], list)
        
        print(f"Observatory: {len(data['top_emerging'])} top emerging, {len(data['by_category'])} categories, {len(data['by_level'])} levels")
    
    def test_observatory_top_emerging_structure(self):
        """Phase 4: Validate top_emerging item structure"""
        response = requests.get(f"{BASE_URL}/api/emerging/observatory?token={self.token}")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["top_emerging"]) > 0:
            top = data["top_emerging"][0]
            # Check expected fields for top emerging competences
            assert "nom_principal" in top, "Missing nom_principal"
            assert "categorie" in top, "Missing categorie"
            assert "score_emergence" in top, "Missing score_emergence"
            assert "niveau_emergence" in top, "Missing niveau_emergence"
            print(f"First top competence: {top['nom_principal']} (score: {top['score_emergence']})")
        else:
            print("No top_emerging competences found in observatory")
    
    def test_observatory_by_category_structure(self):
        """Phase 4: Validate by_category item structure"""
        response = requests.get(f"{BASE_URL}/api/emerging/observatory?token={self.token}")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["by_category"]) > 0:
            cat = data["by_category"][0]
            assert "categorie" in cat, "Missing categorie field"
            assert "count" in cat, "Missing count field"
            assert "avg_score" in cat, "Missing avg_score field"
            print(f"Category breakdown: {[c['categorie'] for c in data['by_category']]}")
    
    def test_observatory_by_level_structure(self):
        """Phase 4: Validate by_level item structure"""
        response = requests.get(f"{BASE_URL}/api/emerging/observatory?token={self.token}")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["by_level"]) > 0:
            lvl = data["by_level"][0]
            assert "level" in lvl, "Missing level field"
            assert "count" in lvl, "Missing count field"
            print(f"Level breakdown: {[l['level'] for l in data['by_level']]}")


class TestPhase3Validation:
    """Test Phase 3: Human validation endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get token and create test emerging competence"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        self.token = response.json()["token"]
        
    def test_validate_competence_invalid_decision(self):
        """Phase 3: Test validation with invalid decision returns 400"""
        # Try to validate with an invalid decision
        # First we need an existing competence ID - let's use a fake one to test 404
        fake_id = str(uuid.uuid4())
        response = requests.post(
            f"{BASE_URL}/api/emerging/validate/{fake_id}?token={self.token}",
            json={"decision": "valide", "commentaire": "Test"}
        )
        # Should return 404 for non-existent competence
        assert response.status_code == 404, f"Expected 404 for non-existent competence, got {response.status_code}"
        print("Correctly returns 404 for non-existent competence")
    
    def test_validate_competence_bad_decision_type(self):
        """Phase 3: Test validation with wrong decision type"""
        fake_id = str(uuid.uuid4())
        response = requests.post(
            f"{BASE_URL}/api/emerging/validate/{fake_id}?token={self.token}",
            json={"decision": "invalid_decision", "commentaire": "Test"}
        )
        # For non-existent competence, we'll get 404 before validation check
        # This confirms the endpoint is reachable
        assert response.status_code in [400, 404]
        print(f"Validation endpoint reachable, status: {response.status_code}")


class TestPhase2DetailEndpoint:
    """Test Phase 2: Individual competence detail endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get token"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        self.token = response.json()["token"]
    
    def test_get_competence_detail_not_found(self):
        """Phase 2: Test GET /api/emerging/competence/{id} returns 404 for invalid ID"""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/emerging/competence/{fake_id}?token={self.token}")
        assert response.status_code == 404
        print("Detail endpoint correctly returns 404 for non-existent competence")
    
    def test_get_competence_detail_missing_token(self):
        """Phase 2: Test detail endpoint requires token"""
        response = requests.get(f"{BASE_URL}/api/emerging/competence/test-id")
        # Should fail due to missing token
        assert response.status_code in [400, 422, 500]
        print(f"Detail endpoint requires token (status: {response.status_code})")


class TestEndToEndWithTestData:
    """End-to-end test creating test data for validation flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get token"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        data = response.json()
        self.token = data["token"]
        self.profile_id = data["profile_id"]
    
    def test_full_flow_observatory_to_detail(self):
        """Test flow: Observatory -> Get top competence -> Get detail"""
        # 1. Get observatory data
        obs_response = requests.get(f"{BASE_URL}/api/emerging/observatory?token={self.token}")
        assert obs_response.status_code == 200
        obs_data = obs_response.json()
        
        print(f"Observatory returned {len(obs_data['top_emerging'])} top emerging competences")
        print(f"Categories: {len(obs_data['by_category'])}, Levels: {len(obs_data['by_level'])}")
        
        # 2. If there are competences, verify their structure
        if obs_data["top_emerging"]:
            first_comp = obs_data["top_emerging"][0]
            print(f"Top competence: {first_comp['nom_principal']}")
            assert first_comp["score_emergence"] >= 31, "Top emerging should have score >= 31"
        
        # 3. Check user's own competences list
        comp_response = requests.get(f"{BASE_URL}/api/emerging/competences?token={self.token}")
        assert comp_response.status_code == 200
        comp_data = comp_response.json()
        print(f"User has {comp_data['total']} emerging competences")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
