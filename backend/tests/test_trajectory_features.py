"""
Test suite for Trajectory Features - Espace Personnel 4 tabs restructuring
Tests: Trajectoire, Compétences, Documents, Matching tabs
Backend APIs: trajectory steps CRUD, auto-populate, AI synthesis, visibility settings
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
BENEFICIARY_PSEUDO = "bob23"
BENEFICIARY_PASSWORD = "Solerys777!"
PARTNER_EMAIL = "cluximon@gmail.com"
PARTNER_PASSWORD = "Solerys777!"


class TestBeneficiaryAuth:
    """Test beneficiary authentication"""
    
    def test_beneficiary_login(self):
        """Test bob23 login returns valid token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": BENEFICIARY_PSEUDO,
            "password": BENEFICIARY_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["role"] == "particulier"
        assert data["pseudo"] == BENEFICIARY_PSEUDO
        print(f"✓ Beneficiary login successful, token: {data['token'][:20]}...")


class TestPartnerAuth:
    """Test partner authentication"""
    
    def test_partner_login(self):
        """Test partner login via login-pro endpoint"""
        response = requests.post(f"{BASE_URL}/api/auth/login-pro", json={
            "pseudo": PARTNER_EMAIL,
            "password": PARTNER_PASSWORD
        })
        assert response.status_code == 200, f"Partner login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["role"] == "partenaire"
        print(f"✓ Partner login successful")


@pytest.fixture(scope="module")
def beneficiary_token():
    """Get beneficiary token for authenticated tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "pseudo": BENEFICIARY_PSEUDO,
        "password": BENEFICIARY_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip("Beneficiary authentication failed")
    return response.json()["token"]


class TestTrajectorySteps:
    """Test trajectory steps CRUD operations"""
    
    def test_get_trajectory_steps(self, beneficiary_token):
        """GET /api/trajectory/steps returns steps sorted by order"""
        response = requests.get(f"{BASE_URL}/api/trajectory/steps?token={beneficiary_token}")
        assert response.status_code == 200
        steps = response.json()
        assert isinstance(steps, list)
        # Verify steps are sorted by order
        if len(steps) > 1:
            orders = [s.get("order", 0) for s in steps]
            assert orders == sorted(orders), "Steps should be sorted by order"
        print(f"✓ GET trajectory steps: {len(steps)} steps returned")
        
        # Verify step structure
        if steps:
            step = steps[0]
            required_fields = ["id", "step_type", "title", "visibility", "order"]
            for field in required_fields:
                assert field in step, f"Missing field: {field}"
    
    def test_get_steps_has_expected_types(self, beneficiary_token):
        """Verify bob23 has 5 steps: certification, formation, emploi, recherche, emploi"""
        response = requests.get(f"{BASE_URL}/api/trajectory/steps?token={beneficiary_token}")
        assert response.status_code == 200
        steps = response.json()
        
        step_types = [s["step_type"] for s in steps]
        # bob23 should have: certification (D'CLIC), formation (BTS), emploi (Conseiller), recherche (Transition), emploi (Chargé RH)
        assert "certification" in step_types, "Should have certification step"
        assert "formation" in step_types, "Should have formation step"
        assert "emploi" in step_types, "Should have emploi step"
        assert "recherche" in step_types, "Should have recherche step"
        print(f"✓ Step types verified: {step_types}")
    
    def test_create_trajectory_step(self, beneficiary_token):
        """POST /api/trajectory/steps creates new step"""
        unique_title = f"TEST_Step_{uuid.uuid4().hex[:8]}"
        payload = {
            "step_type": "formation",
            "title": unique_title,
            "organization": "Test Organization",
            "start_date": "2025-01",
            "end_date": "2025-06",
            "is_ongoing": False,
            "description": "Test step description",
            "competences": ["Test Skill 1", "Test Skill 2"],
            "visibility": "private"
        }
        response = requests.post(f"{BASE_URL}/api/trajectory/steps?token={beneficiary_token}", json=payload)
        assert response.status_code == 200, f"Create step failed: {response.text}"
        
        created = response.json()
        assert created["title"] == unique_title
        assert created["step_type"] == "formation"
        assert "id" in created
        print(f"✓ Created step: {created['id']}")
        
        # Verify persistence with GET
        get_response = requests.get(f"{BASE_URL}/api/trajectory/steps?token={beneficiary_token}")
        steps = get_response.json()
        created_step = next((s for s in steps if s["id"] == created["id"]), None)
        assert created_step is not None, "Created step not found in GET response"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/trajectory/steps/{created['id']}?token={beneficiary_token}")
        return created["id"]
    
    def test_update_trajectory_step(self, beneficiary_token):
        """PUT /api/trajectory/steps/{id} updates step"""
        # First create a step
        unique_title = f"TEST_Update_{uuid.uuid4().hex[:8]}"
        create_response = requests.post(f"{BASE_URL}/api/trajectory/steps?token={beneficiary_token}", json={
            "step_type": "emploi",
            "title": unique_title,
            "visibility": "private"
        })
        assert create_response.status_code == 200
        step_id = create_response.json()["id"]
        
        # Update the step
        update_payload = {
            "title": f"{unique_title}_UPDATED",
            "description": "Updated description",
            "visibility": "accompagnateur"
        }
        update_response = requests.put(f"{BASE_URL}/api/trajectory/steps/{step_id}?token={beneficiary_token}", json=update_payload)
        assert update_response.status_code == 200, f"Update failed: {update_response.text}"
        
        updated = update_response.json()
        assert updated["title"] == f"{unique_title}_UPDATED"
        assert updated["visibility"] == "accompagnateur"
        print(f"✓ Updated step: {step_id}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/trajectory/steps/{step_id}?token={beneficiary_token}")
    
    def test_delete_trajectory_step(self, beneficiary_token):
        """DELETE /api/trajectory/steps/{id} deletes step"""
        # Create a step to delete
        unique_title = f"TEST_Delete_{uuid.uuid4().hex[:8]}"
        create_response = requests.post(f"{BASE_URL}/api/trajectory/steps?token={beneficiary_token}", json={
            "step_type": "stage",
            "title": unique_title,
            "visibility": "private"
        })
        assert create_response.status_code == 200
        step_id = create_response.json()["id"]
        
        # Delete the step
        delete_response = requests.delete(f"{BASE_URL}/api/trajectory/steps/{step_id}?token={beneficiary_token}")
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/trajectory/steps?token={beneficiary_token}")
        steps = get_response.json()
        deleted_step = next((s for s in steps if s["id"] == step_id), None)
        assert deleted_step is None, "Step should be deleted"
        print(f"✓ Deleted step: {step_id}")
    
    def test_delete_nonexistent_step_returns_404(self, beneficiary_token):
        """DELETE non-existent step returns 404"""
        fake_id = str(uuid.uuid4())
        response = requests.delete(f"{BASE_URL}/api/trajectory/steps/{fake_id}?token={beneficiary_token}")
        assert response.status_code == 404


class TestTrajectoryAutoPopulate:
    """Test auto-populate from existing data"""
    
    def test_auto_populate_endpoint(self, beneficiary_token):
        """POST /api/trajectory/auto-populate imports from existing data"""
        response = requests.post(f"{BASE_URL}/api/trajectory/auto-populate?token={beneficiary_token}")
        assert response.status_code == 200, f"Auto-populate failed: {response.text}"
        
        data = response.json()
        assert "imported" in data
        assert "total" in data
        print(f"✓ Auto-populate: imported={data['imported']}, total={data['total']}")


class TestTrajectorySynthesis:
    """Test AI synthesis generation"""
    
    def test_get_synthesis(self, beneficiary_token):
        """GET /api/trajectory/synthesis returns AI analysis"""
        response = requests.get(f"{BASE_URL}/api/trajectory/synthesis?token={beneficiary_token}")
        assert response.status_code == 200, f"Synthesis failed: {response.text}"
        
        data = response.json()
        assert "has_data" in data
        
        if data["has_data"]:
            synthesis = data.get("synthesis", {})
            # Verify synthesis structure
            expected_keys = ["fil_conducteur", "forces_recurrentes", "capacite_adaptation", 
                          "axes_evolution", "competences_transferables", "message_valorisant"]
            for key in expected_keys:
                assert key in synthesis, f"Missing synthesis key: {key}"
            print(f"✓ Synthesis generated with keys: {list(synthesis.keys())}")
        else:
            print("✓ Synthesis endpoint works (no data to analyze)")


class TestVisibilitySettings:
    """Test visibility settings management"""
    
    def test_get_visibility_settings(self, beneficiary_token):
        """GET /api/trajectory/visibility-settings returns settings"""
        response = requests.get(f"{BASE_URL}/api/trajectory/visibility-settings?token={beneficiary_token}")
        assert response.status_code == 200
        
        settings = response.json()
        expected_keys = ["conseiller", "recruteur", "partenaire"]
        for key in expected_keys:
            assert key in settings, f"Missing visibility key: {key}"
        print(f"✓ Visibility settings: {settings}")
    
    def test_update_visibility_settings(self, beneficiary_token):
        """PUT /api/trajectory/visibility-settings updates settings"""
        # Get current settings
        get_response = requests.get(f"{BASE_URL}/api/trajectory/visibility-settings?token={beneficiary_token}")
        original_settings = get_response.json()
        
        # Update settings
        new_settings = {
            "conseiller": True,
            "recruteur": False,
            "partenaire": False,
            "duree_acces": "30j"
        }
        update_response = requests.put(
            f"{BASE_URL}/api/trajectory/visibility-settings?token={beneficiary_token}",
            json=new_settings
        )
        assert update_response.status_code == 200, f"Update visibility failed: {update_response.text}"
        
        # Verify update
        verify_response = requests.get(f"{BASE_URL}/api/trajectory/visibility-settings?token={beneficiary_token}")
        updated = verify_response.json()
        assert updated.get("conseiller") == True, "Conseiller visibility should be True"
        print(f"✓ Visibility settings updated")
        
        # Restore original settings
        requests.put(f"{BASE_URL}/api/trajectory/visibility-settings?token={beneficiary_token}", json=original_settings)


class TestProfileWithDclic:
    """Test profile with D'CLIC data for bob23"""
    
    def test_profile_has_dclic_imported(self, beneficiary_token):
        """Verify bob23 has dclic_imported=True"""
        response = requests.get(f"{BASE_URL}/api/profile?token={beneficiary_token}")
        assert response.status_code == 200
        
        profile = response.json()
        assert profile.get("dclic_imported") == True, "bob23 should have dclic_imported=True"
        print(f"✓ Profile dclic_imported: {profile.get('dclic_imported')}")
    
    def test_profile_has_dclic_dimensions(self, beneficiary_token):
        """Verify bob23 has MBTI, DISC, RIASEC, Vertu"""
        response = requests.get(f"{BASE_URL}/api/profile?token={beneficiary_token}")
        assert response.status_code == 200
        
        profile = response.json()
        assert profile.get("dclic_mbti") == "ENFJ", f"Expected MBTI=ENFJ, got {profile.get('dclic_mbti')}"
        assert profile.get("dclic_disc_label") == "Influence", f"Expected DISC=Influence, got {profile.get('dclic_disc_label')}"
        assert profile.get("dclic_riasec_major") == "Social", f"Expected RIASEC=Social, got {profile.get('dclic_riasec_major')}"
        assert profile.get("dclic_vertu_dominante") == "Empathie", f"Expected Vertu=Empathie, got {profile.get('dclic_vertu_dominante')}"
        print(f"✓ D'CLIC dimensions verified: MBTI={profile.get('dclic_mbti')}, DISC={profile.get('dclic_disc_label')}, RIASEC={profile.get('dclic_riasec_major')}, Vertu={profile.get('dclic_vertu_dominante')}")


class TestRelatedEndpoints:
    """Test related endpoints for tabs functionality"""
    
    def test_get_jobs(self, beneficiary_token):
        """GET /api/jobs returns job list for Matching tab"""
        response = requests.get(f"{BASE_URL}/api/jobs?token={beneficiary_token}")
        assert response.status_code == 200
        jobs = response.json()
        assert isinstance(jobs, list)
        print(f"✓ Jobs endpoint: {len(jobs)} jobs returned")
    
    def test_get_learning(self, beneficiary_token):
        """GET /api/learning returns modules for Matching tab"""
        response = requests.get(f"{BASE_URL}/api/learning?token={beneficiary_token}")
        assert response.status_code == 200
        modules = response.json()
        assert isinstance(modules, list)
        print(f"✓ Learning endpoint: {len(modules)} modules returned")
    
    def test_get_passport(self, beneficiary_token):
        """GET /api/passport returns passport data"""
        response = requests.get(f"{BASE_URL}/api/passport?token={beneficiary_token}")
        assert response.status_code == 200
        passport = response.json()
        assert isinstance(passport, dict)
        print(f"✓ Passport endpoint works")
    
    def test_get_coffre_stats(self, beneficiary_token):
        """GET /api/coffre/stats for Documents tab"""
        response = requests.get(f"{BASE_URL}/api/coffre/stats?token={beneficiary_token}")
        assert response.status_code == 200
        stats = response.json()
        assert isinstance(stats, dict)
        print(f"✓ Coffre stats endpoint works")


class TestStepTypeValidation:
    """Test all 11 step types work correctly"""
    
    @pytest.mark.parametrize("step_type", [
        "emploi", "formation", "stage", "interim", "reconversion",
        "recherche", "pause", "benevolat", "creation", "mobilite", "certification"
    ])
    def test_create_step_with_type(self, beneficiary_token, step_type):
        """Test creating step with each valid step_type"""
        unique_title = f"TEST_{step_type}_{uuid.uuid4().hex[:6]}"
        payload = {
            "step_type": step_type,
            "title": unique_title,
            "visibility": "private"
        }
        response = requests.post(f"{BASE_URL}/api/trajectory/steps?token={beneficiary_token}", json=payload)
        assert response.status_code == 200, f"Failed to create {step_type} step: {response.text}"
        
        created = response.json()
        assert created["step_type"] == step_type
        print(f"✓ Created {step_type} step")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/trajectory/steps/{created['id']}?token={beneficiary_token}")


class TestVisibilityOptions:
    """Test all 4 visibility options work correctly"""
    
    @pytest.mark.parametrize("visibility", ["private", "accompagnateur", "recruteur", "public"])
    def test_create_step_with_visibility(self, beneficiary_token, visibility):
        """Test creating step with each visibility option"""
        unique_title = f"TEST_vis_{visibility}_{uuid.uuid4().hex[:6]}"
        payload = {
            "step_type": "emploi",
            "title": unique_title,
            "visibility": visibility
        }
        response = requests.post(f"{BASE_URL}/api/trajectory/steps?token={beneficiary_token}", json=payload)
        assert response.status_code == 200, f"Failed to create step with visibility {visibility}: {response.text}"
        
        created = response.json()
        assert created["visibility"] == visibility
        print(f"✓ Created step with visibility: {visibility}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/trajectory/steps/{created['id']}?token={beneficiary_token}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
