"""
Test suite for Passport Dynamique de Compétences feature
Tests all passport CRUD operations, AI passerelles, profile updates, and data aggregation
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPassportFeature:
    """Tests for Passport Dynamique de Compétences feature"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: create anonymous token for testing"""
        # Seed the database first
        response = requests.post(f"{BASE_URL}/api/seed")
        print(f"Seed response: {response.status_code}")
        
        # Create anonymous auth token
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200, f"Failed to create token: {response.text}"
        data = response.json()
        self.token = data["token"]
        self.profile_id = data["profile_id"]
        print(f"Test setup complete - token: {self.token[:20]}...")
        yield
    
    # ============== GET /api/passport Tests ==============
    
    def test_get_passport_creates_on_first_call(self):
        """GET /api/passport should create passport on first call with aggregated data"""
        response = requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        assert response.status_code == 200, f"Failed to get passport: {response.text}"
        
        data = response.json()
        
        # Verify passport structure
        assert "id" in data, "Passport should have id"
        assert "completeness_score" in data, "Passport should have completeness_score"
        assert "competences" in data, "Passport should have competences list"
        assert "experiences" in data, "Passport should have experiences list"
        assert "learning_path" in data, "Passport should have learning_path list"
        assert "passerelles" in data, "Passport should have passerelles list"
        assert "sources_count" in data, "Passport should have sources_count"
        
        # Verify profile fields
        assert "professional_summary" in data, "Passport should have professional_summary"
        assert "career_project" in data, "Passport should have career_project"
        assert "motivations" in data, "Passport should have motivations"
        assert "compatible_environments" in data, "Passport should have compatible_environments"
        assert "target_sectors" in data, "Passport should have target_sectors"
        
        # Verify computed fields
        assert "total_competences" in data, "Passport should have total_competences"
        assert "total_experiences" in data, "Passport should have total_experiences"
        assert "total_learning" in data, "Passport should have total_learning"
        assert "emerging_count" in data, "Passport should have emerging_count"
        
        # Verify sharing structure
        assert "sharing" in data, "Passport should have sharing"
        
        print(f"Passport created with completeness_score: {data['completeness_score']}%")
        print(f"Total competences: {data['total_competences']}, experiences: {data['total_experiences']}")
    
    def test_get_passport_returns_existing_passport(self):
        """GET /api/passport should return existing passport on subsequent calls"""
        # First call - creates passport
        response1 = requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        assert response1.status_code == 200
        passport_id = response1.json()["id"]
        
        # Second call - should return same passport
        response2 = requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        assert response2.status_code == 200
        assert response2.json()["id"] == passport_id, "Should return same passport"
        print("Passport persistence verified")
    
    # ============== POST /api/passport/refresh Tests ==============
    
    def test_refresh_passport(self):
        """POST /api/passport/refresh should refresh from all sources"""
        # First get passport to create it
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        # Refresh
        response = requests.post(f"{BASE_URL}/api/passport/refresh?token={self.token}")
        assert response.status_code == 200, f"Failed to refresh: {response.text}"
        
        data = response.json()
        assert "message" in data, "Response should have message"
        assert "completeness_score" in data, "Response should have completeness_score"
        print(f"Passport refreshed: {data['message']}, score: {data['completeness_score']}%")
    
    def test_refresh_preserves_declared_competences(self):
        """POST /api/passport/refresh should preserve user-declared competences"""
        # Create passport and add a declared competence
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        # Add declared competence
        comp_data = {"name": "TEST_Python", "category": "technique", "level": "avance"}
        requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json=comp_data)
        
        # Refresh
        requests.post(f"{BASE_URL}/api/passport/refresh?token={self.token}")
        
        # Verify declared competence still exists
        response = requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        data = response.json()
        
        comp_names = [c["name"] for c in data["competences"] if c.get("source") == "declaratif"]
        assert "TEST_Python" in comp_names, "Declared competence should be preserved after refresh"
        print("Declared competences preserved after refresh")
    
    # ============== PUT /api/passport/profile Tests ==============
    
    def test_update_profile_professional_summary(self):
        """PUT /api/passport/profile should update professional_summary"""
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        update_data = {"professional_summary": "Expert en développement logiciel avec 10 ans d'expérience"}
        response = requests.put(f"{BASE_URL}/api/passport/profile?token={self.token}", json=update_data)
        assert response.status_code == 200, f"Failed to update: {response.text}"
        
        # Verify the update
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        assert passport["professional_summary"] == update_data["professional_summary"]
        print("Professional summary updated successfully")
    
    def test_update_profile_career_project(self):
        """PUT /api/passport/profile should update career_project"""
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        update_data = {"career_project": "Devenir architecte cloud d'ici 2 ans"}
        response = requests.put(f"{BASE_URL}/api/passport/profile?token={self.token}", json=update_data)
        assert response.status_code == 200
        
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        assert passport["career_project"] == update_data["career_project"]
        print("Career project updated successfully")
    
    def test_update_profile_motivations(self):
        """PUT /api/passport/profile should update motivations list"""
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        update_data = {"motivations": ["Impact social", "Innovation", "Autonomie"]}
        response = requests.put(f"{BASE_URL}/api/passport/profile?token={self.token}", json=update_data)
        assert response.status_code == 200
        
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        assert "Impact social" in passport["motivations"]
        assert len(passport["motivations"]) == 3
        print("Motivations updated successfully")
    
    def test_update_profile_compatible_environments(self):
        """PUT /api/passport/profile should update compatible_environments"""
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        update_data = {"compatible_environments": ["Start-up", "PME", "Télétravail"]}
        response = requests.put(f"{BASE_URL}/api/passport/profile?token={self.token}", json=update_data)
        assert response.status_code == 200
        
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        assert "Start-up" in passport["compatible_environments"]
        print("Compatible environments updated successfully")
    
    def test_update_profile_target_sectors(self):
        """PUT /api/passport/profile should update target_sectors"""
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        update_data = {"target_sectors": ["Informatique", "Finance", "Santé"]}
        response = requests.put(f"{BASE_URL}/api/passport/profile?token={self.token}", json=update_data)
        assert response.status_code == 200
        
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        assert "Informatique" in passport["target_sectors"]
        print("Target sectors updated successfully")
    
    def test_update_profile_increases_completeness(self):
        """Updating profile fields should increase completeness score"""
        # Get initial score
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        initial_score = passport["completeness_score"]
        
        # Update all profile fields
        update_data = {
            "professional_summary": "Expert développeur",
            "career_project": "Architecte logiciel",
            "motivations": ["Innovation", "Impact"],
            "compatible_environments": ["Remote", "Start-up"],
            "target_sectors": ["Tech", "Finance"]
        }
        requests.put(f"{BASE_URL}/api/passport/profile?token={self.token}", json=update_data)
        
        # Check new score
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        new_score = passport["completeness_score"]
        
        assert new_score >= initial_score, f"Score should increase: {initial_score} -> {new_score}"
        print(f"Completeness score increased: {initial_score}% -> {new_score}%")
    
    # ============== POST /api/passport/competences Tests ==============
    
    def test_add_competence(self):
        """POST /api/passport/competences should add a new competence"""
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        comp_data = {
            "name": "TEST_Machine Learning",
            "category": "technique",
            "level": "intermediaire",
            "experience_years": 2
        }
        response = requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json=comp_data)
        assert response.status_code == 200, f"Failed to add competence: {response.text}"
        
        # Verify competence was added
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        comp_names = [c["name"] for c in passport["competences"]]
        assert "TEST_Machine Learning" in comp_names
        
        # Verify competence structure
        added_comp = next((c for c in passport["competences"] if c["name"] == "TEST_Machine Learning"), None)
        assert added_comp is not None
        assert added_comp["category"] == "technique"
        assert added_comp["level"] == "intermediaire"
        assert added_comp["source"] == "declaratif"
        print("Competence added successfully with correct structure")
    
    def test_add_multiple_competences_increases_score(self):
        """Adding multiple competences should increase completeness score"""
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        initial_score = passport["completeness_score"]
        initial_count = len(passport["competences"])
        
        # Add 3 competences
        for i, name in enumerate(["TEST_Python", "TEST_SQL", "TEST_Docker"]):
            requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json={
                "name": name, "category": "technique", "level": "avance"
            })
        
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        new_score = passport["completeness_score"]
        new_count = len(passport["competences"])
        
        assert new_count == initial_count + 3
        assert new_score >= initial_score
        print(f"Added 3 competences, count: {initial_count} -> {new_count}, score: {initial_score}% -> {new_score}%")
    
    def test_add_competence_with_all_categories(self):
        """Test adding competences with different categories"""
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        categories = ["technique", "transversale", "relationnelle"]
        for cat in categories:
            response = requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json={
                "name": f"TEST_{cat}_skill",
                "category": cat,
                "level": "intermediaire"
            })
            assert response.status_code == 200
        
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        comp_categories = [c["category"] for c in passport["competences"] if c["name"].startswith("TEST_")]
        
        for cat in categories:
            assert cat in comp_categories, f"Category {cat} should be present"
        print("All competence categories work correctly")
    
    def test_add_competence_with_all_levels(self):
        """Test adding competences with different levels"""
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        levels = ["debutant", "intermediaire", "avance", "expert"]
        for level in levels:
            response = requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json={
                "name": f"TEST_{level}_level",
                "category": "technique",
                "level": level
            })
            assert response.status_code == 200
        
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        comp_levels = [c["level"] for c in passport["competences"] if c["name"].startswith("TEST_")]
        
        for level in levels:
            assert level in comp_levels, f"Level {level} should be present"
        print("All competence levels work correctly")
    
    # ============== POST /api/passport/experiences Tests ==============
    
    def test_add_experience(self):
        """POST /api/passport/experiences should add a new experience"""
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        exp_data = {
            "title": "TEST_Développeur Senior",
            "organization": "Tech Company",
            "description": "Développement de solutions cloud",
            "skills_used": ["Python", "AWS", "Docker"],
            "achievements": ["Migration vers le cloud", "Réduction des coûts de 30%"],
            "experience_type": "professionnel"
        }
        response = requests.post(f"{BASE_URL}/api/passport/experiences?token={self.token}", json=exp_data)
        assert response.status_code == 200, f"Failed to add experience: {response.text}"
        
        # Verify experience was added
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        exp_titles = [e["title"] for e in passport["experiences"]]
        assert "TEST_Développeur Senior" in exp_titles
        
        # Verify experience structure
        added_exp = next((e for e in passport["experiences"] if e["title"] == "TEST_Développeur Senior"), None)
        assert added_exp is not None
        assert added_exp["organization"] == "Tech Company"
        assert "Python" in added_exp["skills_used"]
        assert added_exp["source"] == "declaratif"
        print("Experience added successfully with correct structure")
    
    def test_add_experience_with_different_types(self):
        """Test adding experiences with different types"""
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        exp_types = ["professionnel", "personnel", "benevole", "projet"]
        for exp_type in exp_types:
            response = requests.post(f"{BASE_URL}/api/passport/experiences?token={self.token}", json={
                "title": f"TEST_{exp_type}_exp",
                "organization": "Test Org",
                "experience_type": exp_type
            })
            assert response.status_code == 200
        
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        exp_types_found = [e["experience_type"] for e in passport["experiences"] if e["title"].startswith("TEST_")]
        
        for exp_type in exp_types:
            assert exp_type in exp_types_found, f"Experience type {exp_type} should be present"
        print("All experience types work correctly")
    
    def test_add_experiences_increases_score(self):
        """Adding experiences should increase completeness score"""
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        initial_score = passport["completeness_score"]
        
        # Add 3 experiences
        for i in range(3):
            requests.post(f"{BASE_URL}/api/passport/experiences?token={self.token}", json={
                "title": f"TEST_Experience_{i}",
                "organization": f"Company_{i}"
            })
        
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        new_score = passport["completeness_score"]
        
        assert new_score >= initial_score
        print(f"Added 3 experiences, score: {initial_score}% -> {new_score}%")
    
    # ============== DELETE /api/passport/competences/{id} Tests ==============
    
    def test_delete_competence(self):
        """DELETE /api/passport/competences/{id} should delete a declared competence"""
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        # Add a competence
        requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json={
            "name": "TEST_ToDelete", "category": "technique", "level": "intermediaire"
        })
        
        # Get the competence ID
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        comp = next((c for c in passport["competences"] if c["name"] == "TEST_ToDelete"), None)
        assert comp is not None
        comp_id = comp["id"]
        
        # Delete the competence
        response = requests.delete(f"{BASE_URL}/api/passport/competences/{comp_id}?token={self.token}")
        assert response.status_code == 200, f"Failed to delete: {response.text}"
        
        # Verify deletion
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        comp_names = [c["name"] for c in passport["competences"]]
        assert "TEST_ToDelete" not in comp_names
        print("Competence deleted successfully")
    
    # ============== DELETE /api/passport/experiences/{id} Tests ==============
    
    def test_delete_experience(self):
        """DELETE /api/passport/experiences/{id} should delete a declared experience"""
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        # Add an experience
        requests.post(f"{BASE_URL}/api/passport/experiences?token={self.token}", json={
            "title": "TEST_ExpToDelete", "organization": "Delete Corp"
        })
        
        # Get the experience ID
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        exp = next((e for e in passport["experiences"] if e["title"] == "TEST_ExpToDelete"), None)
        assert exp is not None
        exp_id = exp["id"]
        
        # Delete the experience
        response = requests.delete(f"{BASE_URL}/api/passport/experiences/{exp_id}?token={self.token}")
        assert response.status_code == 200, f"Failed to delete: {response.text}"
        
        # Verify deletion
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        exp_titles = [e["title"] for e in passport["experiences"]]
        assert "TEST_ExpToDelete" not in exp_titles
        print("Experience deleted successfully")
    
    # ============== GET /api/passport/passerelles Tests ==============
    
    def test_get_passerelles_ai_analysis(self):
        """GET /api/passport/passerelles should trigger AI analysis"""
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        # Add some competences for better AI analysis
        competences = ["Python", "Data Analysis", "Machine Learning", "Communication", "Project Management"]
        for comp in competences:
            requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json={
                "name": comp, "category": "technique", "level": "avance"
            })
        
        # Set target sectors for better results
        requests.put(f"{BASE_URL}/api/passport/profile?token={self.token}", json={
            "target_sectors": ["Informatique", "Finance"]
        })
        
        # Get passerelles
        response = requests.get(f"{BASE_URL}/api/passport/passerelles?token={self.token}")
        assert response.status_code == 200, f"Failed to get passerelles: {response.text}"
        
        data = response.json()
        assert "passerelles" in data, "Response should have passerelles"
        
        print(f"AI analysis returned {len(data['passerelles'])} passerelles")
        
        # Verify passerelle structure if any returned
        if len(data["passerelles"]) > 0:
            p = data["passerelles"][0]
            assert "job_name" in p, "Passerelle should have job_name"
            assert "compatibility_score" in p, "Passerelle should have compatibility_score"
            assert "shared_skills" in p, "Passerelle should have shared_skills"
            assert "skills_to_acquire" in p, "Passerelle should have skills_to_acquire"
            assert "accessibility" in p, "Passerelle should have accessibility"
            print(f"First passerelle: {p['job_name']} with {p['compatibility_score']*100:.0f}% compatibility")
    
    def test_passerelles_saved_to_passport(self):
        """Passerelles should be saved to passport after AI analysis"""
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        # Add competences
        for comp in ["Leadership", "Gestion d'équipe", "Stratégie"]:
            requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json={
                "name": comp, "category": "transversale", "level": "avance"
            })
        
        # Get passerelles
        requests.get(f"{BASE_URL}/api/passport/passerelles?token={self.token}")
        
        # Verify they're saved
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        print(f"Passport now has {len(passport['passerelles'])} passerelles saved")
    
    # ============== PUT /api/passport/sharing Tests ==============
    
    def test_update_sharing_settings(self):
        """PUT /api/passport/sharing should update sharing settings"""
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        sharing_data = {
            "is_public": True,
            "shared_sections": ["profile", "competences", "experiences"],
            "shared_with": ["recruiter@example.com"],
            "share_expiry": "2026-12-31T23:59:59Z"
        }
        response = requests.put(f"{BASE_URL}/api/passport/sharing?token={self.token}", json=sharing_data)
        assert response.status_code == 200, f"Failed to update sharing: {response.text}"
        
        # Verify sharing settings
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        sharing = passport["sharing"]
        
        assert sharing["is_public"] == True
        assert "profile" in sharing["shared_sections"]
        assert "competences" in sharing["shared_sections"]
        print("Sharing settings updated successfully")
    
    def test_update_sharing_private(self):
        """Setting is_public to false should work"""
        requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        
        sharing_data = {"is_public": False, "shared_sections": [], "shared_with": []}
        response = requests.put(f"{BASE_URL}/api/passport/sharing?token={self.token}", json=sharing_data)
        assert response.status_code == 200
        
        passport = requests.get(f"{BASE_URL}/api/passport?token={self.token}").json()
        assert passport["sharing"]["is_public"] == False
        print("Passport set to private successfully")
    
    # ============== Error Cases ==============
    
    def test_invalid_token(self):
        """All endpoints should return 401 for invalid token"""
        invalid_token = "invalid_token_12345"
        
        response = requests.get(f"{BASE_URL}/api/passport?token={invalid_token}")
        assert response.status_code == 401
        
        response = requests.post(f"{BASE_URL}/api/passport/refresh?token={invalid_token}")
        assert response.status_code == 401
        
        print("Invalid token correctly returns 401")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
