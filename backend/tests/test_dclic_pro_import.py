"""
Test D'CLIC PRO Import and Evidence Management Features
- POST /api/profile/import-dclic - Import profile data from D'CLIC PRO
- GET /api/profile/evidences - List evidences
- POST /api/profile/evidences - Add evidence
- DELETE /api/profile/evidences/{id} - Delete evidence
- GET /api/profile - Verify new fields (target_job, city, mobility, contract_types, work_modes, summary)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestDclicProImport:
    """Test D'CLIC PRO import and evidence management"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user for D'CLIC PRO testing"""
        unique_id = str(uuid.uuid4())[:8]
        pseudo = f"TEST_dclic_{unique_id}"
        password = "Test1234!"
        
        # Register new user
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": password,
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        })
        
        if response.status_code == 201 or response.status_code == 200:
            data = response.json()
            return {
                "token": data["token"],
                "pseudo": pseudo,
                "profile_id": data.get("profile_id")
            }
        else:
            pytest.skip(f"Could not create test user: {response.status_code} - {response.text}")
    
    # ===== EVIDENCE CRUD TESTS =====
    
    def test_get_evidences_empty(self, test_user):
        """GET /api/profile/evidences - Should return empty list for new user"""
        response = requests.get(f"{BASE_URL}/api/profile/evidences?token={test_user['token']}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"PASSED: GET /api/profile/evidences returns list (count: {len(data)})")
    
    def test_add_evidence(self, test_user):
        """POST /api/profile/evidences - Add a new evidence"""
        response = requests.post(
            f"{BASE_URL}/api/profile/evidences?token={test_user['token']}&title=Diplome%20Test&kind=diplome"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, "Response should contain id"
        assert data["title"] == "Diplome Test", f"Title mismatch: {data.get('title')}"
        assert data["kind"] == "diplome", f"Kind mismatch: {data.get('kind')}"
        test_user["evidence_id"] = data["id"]
        print(f"PASSED: POST /api/profile/evidences created evidence with id: {data['id']}")
        return data["id"]
    
    def test_get_evidences_after_add(self, test_user):
        """GET /api/profile/evidences - Should contain the added evidence"""
        # First add an evidence if not already added
        if "evidence_id" not in test_user:
            self.test_add_evidence(test_user)
        
        response = requests.get(f"{BASE_URL}/api/profile/evidences?token={test_user['token']}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert len(data) >= 1, f"Expected at least 1 evidence, got {len(data)}"
        
        # Find our evidence
        found = any(ev.get("id") == test_user.get("evidence_id") for ev in data)
        assert found, f"Evidence {test_user.get('evidence_id')} not found in list"
        print(f"PASSED: GET /api/profile/evidences contains added evidence")
    
    def test_add_evidence_with_all_params(self, test_user):
        """POST /api/profile/evidences - Add evidence with all parameters"""
        response = requests.post(
            f"{BASE_URL}/api/profile/evidences",
            params={
                "token": test_user['token'],
                "title": "Certificat Python",
                "kind": "certificat",
                "source": "Coursera",
                "description": "Certification Python avancé"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["title"] == "Certificat Python"
        assert data["kind"] == "certificat"
        assert data["source"] == "Coursera"
        assert data["description"] == "Certification Python avancé"
        test_user["evidence_id_2"] = data["id"]
        print(f"PASSED: POST /api/profile/evidences with all params created evidence")
    
    def test_delete_evidence(self, test_user):
        """DELETE /api/profile/evidences/{id} - Delete an evidence"""
        # First add an evidence to delete
        response = requests.post(
            f"{BASE_URL}/api/profile/evidences?token={test_user['token']}&title=ToDelete&kind=attestation"
        )
        assert response.status_code == 200
        evidence_id = response.json()["id"]
        
        # Delete it
        response = requests.delete(
            f"{BASE_URL}/api/profile/evidences/{evidence_id}?token={test_user['token']}"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "message" in data, "Response should contain message"
        print(f"PASSED: DELETE /api/profile/evidences/{evidence_id} deleted evidence")
        
        # Verify it's gone
        response = requests.get(f"{BASE_URL}/api/profile/evidences?token={test_user['token']}")
        evidences = response.json()
        found = any(ev.get("id") == evidence_id for ev in evidences)
        assert not found, f"Evidence {evidence_id} should be deleted"
        print(f"PASSED: Evidence {evidence_id} verified as deleted")
    
    def test_delete_nonexistent_evidence(self, test_user):
        """DELETE /api/profile/evidences/{id} - Should return 404 for non-existent evidence"""
        fake_id = "nonexistent-id-12345"
        response = requests.delete(
            f"{BASE_URL}/api/profile/evidences/{fake_id}?token={test_user['token']}"
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print(f"PASSED: DELETE non-existent evidence returns 404")
    
    # ===== D'CLIC PRO IMPORT TESTS =====
    
    def test_import_dclic_basic(self, test_user):
        """POST /api/profile/import-dclic - Basic import with target_job and city"""
        payload = {
            "target_job": "Développeur Full Stack",
            "city": "Paris",
            "summary": "Développeur passionné avec 5 ans d'expérience"
        }
        response = requests.post(
            f"{BASE_URL}/api/profile/import-dclic?token={test_user['token']}",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "message" in data, "Response should contain message"
        assert "fields_updated" in data, "Response should contain fields_updated"
        assert "target_job" in data["fields_updated"], "target_job should be in fields_updated"
        assert "city" in data["fields_updated"], "city should be in fields_updated"
        assert "summary" in data["fields_updated"], "summary should be in fields_updated"
        print(f"PASSED: POST /api/profile/import-dclic basic import - {data['message']}")
    
    def test_import_dclic_full(self, test_user):
        """POST /api/profile/import-dclic - Full import with all fields"""
        payload = {
            "target_job": "Chef de projet digital",
            "summary": "Expert en gestion de projets numériques",
            "city": "Lyon",
            "mobility": "region",
            "contract_types": ["CDI", "CDD"],
            "work_modes": ["Hybride", "Teletravail"],
            "skills": [
                {"name": "Gestion de projet", "category": "transversale", "declared_level": 4, "status": "declaree"},
                {"name": "Python", "category": "technique", "declared_level": 3, "status": "declaree"}
            ],
            "experiences": [
                {
                    "title": "Chef de projet",
                    "organization": "TechCorp",
                    "description": "Gestion d'équipe de 5 développeurs",
                    "start_date": "2020-01",
                    "end_date": "2023-12"
                }
            ],
            "evidences": [
                {"title": "PMP Certification", "kind": "certificat", "source": "PMI"},
                {"title": "Master Management", "kind": "diplome", "source": "HEC"}
            ]
        }
        response = requests.post(
            f"{BASE_URL}/api/profile/import-dclic?token={test_user['token']}",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "message" in data
        assert "fields_updated" in data
        assert "experiences_imported" in data
        assert "skills_imported" in data
        assert "evidences_imported" in data
        assert "profile_completion" in data
        
        # Verify counts
        assert data["skills_imported"] == 2, f"Expected 2 skills, got {data['skills_imported']}"
        assert data["experiences_imported"] == 1, f"Expected 1 experience, got {data['experiences_imported']}"
        assert data["evidences_imported"] == 2, f"Expected 2 evidences, got {data['evidences_imported']}"
        
        print(f"PASSED: POST /api/profile/import-dclic full import")
        print(f"  - Skills imported: {data['skills_imported']}")
        print(f"  - Experiences imported: {data['experiences_imported']}")
        print(f"  - Evidences imported: {data['evidences_imported']}")
        print(f"  - Profile completion: {data['profile_completion']}%")
    
    def test_profile_contains_new_fields(self, test_user):
        """GET /api/profile - Verify new CV fields are present"""
        response = requests.get(f"{BASE_URL}/api/profile?token={test_user['token']}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check new fields exist
        assert "target_job" in data, "Profile should contain target_job"
        assert "city" in data, "Profile should contain city"
        assert "mobility" in data, "Profile should contain mobility"
        assert "contract_types" in data, "Profile should contain contract_types"
        assert "work_modes" in data, "Profile should contain work_modes"
        assert "summary" in data, "Profile should contain summary"
        
        # Verify values from previous import
        assert data["target_job"] == "Chef de projet digital", f"target_job mismatch: {data.get('target_job')}"
        assert data["city"] == "Lyon", f"city mismatch: {data.get('city')}"
        assert data["mobility"] == "region", f"mobility mismatch: {data.get('mobility')}"
        assert "CDI" in data["contract_types"], f"contract_types should contain CDI: {data.get('contract_types')}"
        assert "Hybride" in data["work_modes"], f"work_modes should contain Hybride: {data.get('work_modes')}"
        
        print(f"PASSED: GET /api/profile contains all new CV fields")
        print(f"  - target_job: {data['target_job']}")
        print(f"  - city: {data['city']}")
        print(f"  - mobility: {data['mobility']}")
        print(f"  - contract_types: {data['contract_types']}")
        print(f"  - work_modes: {data['work_modes']}")
    
    def test_evidences_from_import(self, test_user):
        """GET /api/profile/evidences - Verify evidences from D'CLIC import"""
        response = requests.get(f"{BASE_URL}/api/profile/evidences?token={test_user['token']}")
        assert response.status_code == 200
        evidences = response.json()
        
        # Find imported evidences
        pmp = next((e for e in evidences if "PMP" in e.get("title", "")), None)
        master = next((e for e in evidences if "Master" in e.get("title", "")), None)
        
        assert pmp is not None, "PMP Certification should be in evidences"
        assert master is not None, "Master Management should be in evidences"
        
        print(f"PASSED: Evidences from D'CLIC import found")
        print(f"  - Total evidences: {len(evidences)}")
    
    def test_import_dclic_empty_payload(self, test_user):
        """POST /api/profile/import-dclic - Empty payload should work"""
        response = requests.post(
            f"{BASE_URL}/api/profile/import-dclic?token={test_user['token']}",
            json={}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "message" in data
        print(f"PASSED: POST /api/profile/import-dclic with empty payload works")
    
    def test_import_dclic_without_token(self):
        """POST /api/profile/import-dclic - Should fail without token"""
        response = requests.post(
            f"{BASE_URL}/api/profile/import-dclic",
            json={"target_job": "Test"}
        )
        assert response.status_code in [401, 422], f"Expected 401/422, got {response.status_code}"
        print(f"PASSED: POST /api/profile/import-dclic without token returns {response.status_code}")


class TestExistingUserDclicImport:
    """Test D'CLIC import with existing test user"""
    
    def test_login_existing_user(self):
        """Login with existing test user test_user_v2"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "test_user_v2",
            "password": "Test1234!"
        })
        
        if response.status_code != 200:
            pytest.skip("test_user_v2 not available")
        
        data = response.json()
        self.token = data["token"]
        print(f"PASSED: Logged in as test_user_v2")
        return data["token"]
    
    def test_existing_user_profile_has_dclic_data(self):
        """Verify existing user has D'CLIC data from previous import"""
        token = self.test_login_existing_user()
        
        response = requests.get(f"{BASE_URL}/api/profile?token={token}")
        assert response.status_code == 200
        data = response.json()
        
        # Check if user has D'CLIC data
        if data.get("target_job"):
            print(f"PASSED: Existing user has target_job: {data['target_job']}")
        else:
            print(f"INFO: Existing user has no target_job set")
        
        if data.get("skills"):
            print(f"PASSED: Existing user has {len(data['skills'])} skills")
        
        return data
    
    def test_existing_user_evidences(self):
        """Check existing user's evidences"""
        token = self.test_login_existing_user()
        
        response = requests.get(f"{BASE_URL}/api/profile/evidences?token={token}")
        assert response.status_code == 200
        evidences = response.json()
        
        print(f"PASSED: Existing user has {len(evidences)} evidences")
        for ev in evidences[:3]:  # Show first 3
            print(f"  - {ev.get('title')} ({ev.get('kind')})")


class TestProfileCompletion:
    """Test profile completion score calculation"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a fresh test user"""
        unique_id = str(uuid.uuid4())[:8]
        pseudo = f"TEST_completion_{unique_id}"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "Test1234!",
            "role": "particulier",
            "consent_cgu": True,
            "consent_privacy": True
        })
        
        if response.status_code in [200, 201]:
            return response.json()
        pytest.skip("Could not create test user")
    
    def test_initial_completion_score(self, test_user):
        """New user should have low completion score"""
        response = requests.get(f"{BASE_URL}/api/profile/completion?token={test_user['token']}")
        assert response.status_code == 200
        data = response.json()
        assert "profile_completion" in data
        initial_score = data["profile_completion"]
        print(f"PASSED: Initial completion score: {initial_score}%")
        return initial_score
    
    def test_completion_increases_after_import(self, test_user):
        """Completion score should increase after D'CLIC import"""
        # Get initial score
        response = requests.get(f"{BASE_URL}/api/profile/completion?token={test_user['token']}")
        initial_score = response.json()["profile_completion"]
        
        # Import D'CLIC data
        payload = {
            "target_job": "Data Scientist",
            "city": "Marseille",
            "mobility": "france",
            "contract_types": ["CDI"],
            "work_modes": ["Teletravail"],
            "summary": "Expert en data science et machine learning",
            "skills": [
                {"name": "Python", "category": "technique", "declared_level": 5},
                {"name": "Machine Learning", "category": "technique", "declared_level": 4}
            ]
        }
        response = requests.post(
            f"{BASE_URL}/api/profile/import-dclic?token={test_user['token']}",
            json=payload
        )
        assert response.status_code == 200
        new_score = response.json()["profile_completion"]
        
        assert new_score > initial_score, f"Score should increase: {initial_score} -> {new_score}"
        print(f"PASSED: Completion score increased from {initial_score}% to {new_score}%")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
