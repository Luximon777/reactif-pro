"""
Test suite for D'CLIC Boost Section and Coffre-Fort features
Tests:
1. D'CLIC Boost profile data (MBTI, DISC, RIASEC, Vertu dominante)
2. Coffre-fort file upload/download with real storage
3. Coffre-fort stats endpoint
4. Login flows for beneficiary and partner
"""
import pytest
import requests
import os
import io

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
BENEFICIARY_PSEUDO = "bob23"
BENEFICIARY_PASSWORD = "Solerys777!"
PARTNER_EMAIL = "cluximon@gmail.com"
PARTNER_PASSWORD = "Solerys777!"


class TestLoginFlows:
    """Test authentication for beneficiary and partner"""

    def test_beneficiary_login(self):
        """Test beneficiary login with pseudo/password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": BENEFICIARY_PSEUDO,
            "password": BENEFICIARY_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "Token not returned"
        assert data.get("pseudo") == BENEFICIARY_PSEUDO
        print(f"✓ Beneficiary login successful, token: {data['token'][:20]}...")

    def test_partner_login(self):
        """Test partner login with email/password via login-pro"""
        response = requests.post(f"{BASE_URL}/api/auth/login-pro", json={
            "pseudo": PARTNER_EMAIL,
            "password": PARTNER_PASSWORD
        })
        assert response.status_code == 200, f"Partner login failed: {response.text}"
        data = response.json()
        assert "token" in data, "Token not returned"
        print(f"✓ Partner login successful, token: {data['token'][:20]}...")


class TestDclicBoostProfile:
    """Test D'CLIC PRO profile data for bob23 user"""

    @pytest.fixture
    def beneficiary_token(self):
        """Get beneficiary token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": BENEFICIARY_PSEUDO,
            "password": BENEFICIARY_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Could not login as beneficiary")
        return response.json()["token"]

    def test_profile_has_dclic_imported(self, beneficiary_token):
        """Verify bob23 has dclic_imported=True"""
        response = requests.get(f"{BASE_URL}/api/profile?token={beneficiary_token}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("dclic_imported") is True, "dclic_imported should be True"
        print(f"✓ dclic_imported = {data.get('dclic_imported')}")

    def test_profile_has_dclic_mbti(self, beneficiary_token):
        """Verify bob23 has dclic_mbti=ENFJ"""
        response = requests.get(f"{BASE_URL}/api/profile?token={beneficiary_token}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("dclic_mbti") == "ENFJ", f"Expected ENFJ, got {data.get('dclic_mbti')}"
        print(f"✓ dclic_mbti = {data.get('dclic_mbti')}")

    def test_profile_has_dclic_disc(self, beneficiary_token):
        """Verify bob23 has dclic_disc_label=Influence"""
        response = requests.get(f"{BASE_URL}/api/profile?token={beneficiary_token}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("dclic_disc_label") == "Influence", f"Expected Influence, got {data.get('dclic_disc_label')}"
        print(f"✓ dclic_disc_label = {data.get('dclic_disc_label')}")

    def test_profile_has_dclic_riasec(self, beneficiary_token):
        """Verify bob23 has dclic_riasec_major=Social"""
        response = requests.get(f"{BASE_URL}/api/profile?token={beneficiary_token}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("dclic_riasec_major") == "Social", f"Expected Social, got {data.get('dclic_riasec_major')}"
        print(f"✓ dclic_riasec_major = {data.get('dclic_riasec_major')}")

    def test_profile_has_dclic_vertu(self, beneficiary_token):
        """Verify bob23 has dclic_vertu_dominante=Empathie"""
        response = requests.get(f"{BASE_URL}/api/profile?token={beneficiary_token}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("dclic_vertu_dominante") == "Empathie", f"Expected Empathie, got {data.get('dclic_vertu_dominante')}"
        print(f"✓ dclic_vertu_dominante = {data.get('dclic_vertu_dominante')}")


class TestCoffreFortStats:
    """Test Coffre-Fort stats endpoint"""

    @pytest.fixture
    def beneficiary_token(self):
        """Get beneficiary token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": BENEFICIARY_PSEUDO,
            "password": BENEFICIARY_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Could not login as beneficiary")
        return response.json()["token"]

    def test_coffre_stats_endpoint(self, beneficiary_token):
        """Test GET /api/coffre/stats returns correct structure"""
        response = requests.get(f"{BASE_URL}/api/coffre/stats?token={beneficiary_token}")
        assert response.status_code == 200, f"Stats failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "total_documents" in data, "Missing total_documents"
        assert "by_category" in data, "Missing by_category"
        assert "competences_prouvees" in data, "Missing competences_prouvees"
        assert "documents_partages" in data, "Missing documents_partages"
        assert "documents_expirants" in data, "Missing documents_expirants"
        
        print(f"✓ Coffre stats: {data['total_documents']} documents, {len(data.get('competences_prouvees', []))} competences")

    def test_coffre_documents_list(self, beneficiary_token):
        """Test GET /api/coffre/documents returns list"""
        response = requests.get(f"{BASE_URL}/api/coffre/documents?token={beneficiary_token}")
        assert response.status_code == 200, f"Documents list failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of documents"
        print(f"✓ Coffre documents: {len(data)} documents found")

    def test_coffre_categories(self, beneficiary_token):
        """Test GET /api/coffre/categories returns categories"""
        response = requests.get(f"{BASE_URL}/api/coffre/categories")
        assert response.status_code == 200, f"Categories failed: {response.text}"
        data = response.json()
        assert isinstance(data, dict), "Expected dict of categories"
        assert "identite_professionnelle" in data, "Missing identite_professionnelle category"
        print(f"✓ Coffre categories: {len(data)} categories")


class TestCoffreFortUploadDownload:
    """Test Coffre-Fort file upload and download with real storage"""

    @pytest.fixture
    def beneficiary_token(self):
        """Get beneficiary token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": BENEFICIARY_PSEUDO,
            "password": BENEFICIARY_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Could not login as beneficiary")
        return response.json()["token"]

    def test_upload_file_to_coffre(self, beneficiary_token):
        """Test POST /api/coffre/upload with real file"""
        # Create a test file
        test_content = b"This is a test document for Coffre-Fort upload testing."
        files = {"file": ("test_document.txt", io.BytesIO(test_content), "text/plain")}
        params = {
            "token": beneficiary_token,
            "title": "TEST_Upload_Document",
            "category": "documents_administratifs",
            "document_type": "autre",
            "description": "Test document for automated testing",
            "competences_liees": "Test,Automation"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/coffre/upload",
            params=params,
            files=files
        )
        assert response.status_code == 200, f"Upload failed: {response.text}"
        data = response.json()
        
        assert "document_id" in data, "Missing document_id in response"
        assert "storage_path" in data, "Missing storage_path in response"
        assert data.get("message") == "Document uploadé dans le coffre-fort"
        
        print(f"✓ File uploaded successfully, document_id: {data['document_id']}")
        return data["document_id"]

    def test_download_uploaded_file(self, beneficiary_token):
        """Test GET /api/coffre/download/{document_id}"""
        # First upload a file
        test_content = b"Download test content for Coffre-Fort."
        files = {"file": ("download_test.txt", io.BytesIO(test_content), "text/plain")}
        params = {
            "token": beneficiary_token,
            "title": "TEST_Download_Document",
            "category": "documents_administratifs",
            "document_type": "autre"
        }
        
        upload_response = requests.post(
            f"{BASE_URL}/api/coffre/upload",
            params=params,
            files=files
        )
        assert upload_response.status_code == 200, f"Upload failed: {upload_response.text}"
        document_id = upload_response.json()["document_id"]
        
        # Now download the file
        download_response = requests.get(
            f"{BASE_URL}/api/coffre/download/{document_id}?token={beneficiary_token}"
        )
        assert download_response.status_code == 200, f"Download failed: {download_response.text}"
        
        # Verify content
        assert download_response.content == test_content, "Downloaded content doesn't match"
        assert "Content-Disposition" in download_response.headers
        
        print(f"✓ File downloaded successfully, size: {len(download_response.content)} bytes")

    def test_download_nonexistent_file(self, beneficiary_token):
        """Test download of non-existent document returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/coffre/download/nonexistent-id?token={beneficiary_token}"
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Non-existent document returns 404")

    def test_document_with_storage_path_has_file_badge(self, beneficiary_token):
        """Verify uploaded document has storage_path set"""
        # Upload a file
        test_content = b"Badge test content."
        files = {"file": ("badge_test.txt", io.BytesIO(test_content), "text/plain")}
        params = {
            "token": beneficiary_token,
            "title": "TEST_Badge_Document",
            "category": "identite_professionnelle",
            "document_type": "cv"
        }
        
        upload_response = requests.post(
            f"{BASE_URL}/api/coffre/upload",
            params=params,
            files=files
        )
        assert upload_response.status_code == 200
        document_id = upload_response.json()["document_id"]
        
        # Get document details
        doc_response = requests.get(
            f"{BASE_URL}/api/coffre/documents/{document_id}?token={beneficiary_token}"
        )
        assert doc_response.status_code == 200
        doc = doc_response.json()
        
        assert doc.get("storage_path") is not None, "storage_path should be set"
        assert doc.get("file_name") is not None, "file_name should be set"
        assert doc.get("file_size") > 0, "file_size should be > 0"
        
        print(f"✓ Document has storage_path: {doc['storage_path'][:50]}...")


class TestDashboardMetrics:
    """Test dashboard metrics display"""

    @pytest.fixture
    def beneficiary_token(self):
        """Get beneficiary token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": BENEFICIARY_PSEUDO,
            "password": BENEFICIARY_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Could not login as beneficiary")
        return response.json()["token"]

    def test_profile_endpoint(self, beneficiary_token):
        """Test profile endpoint returns data for metrics"""
        response = requests.get(f"{BASE_URL}/api/profile?token={beneficiary_token}")
        assert response.status_code == 200
        data = response.json()
        assert "profile_score" in data, "Missing profile_score"
        assert "skills" in data, "Missing skills"
        print(f"✓ Profile score: {data.get('profile_score')}%")

    def test_jobs_endpoint(self, beneficiary_token):
        """Test jobs endpoint returns data for metrics"""
        response = requests.get(f"{BASE_URL}/api/jobs?token={beneficiary_token}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Expected list of jobs"
        print(f"✓ Jobs: {len(data)} jobs available")

    def test_learning_endpoint(self, beneficiary_token):
        """Test learning endpoint returns data for metrics"""
        response = requests.get(f"{BASE_URL}/api/learning?token={beneficiary_token}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Expected list of learning modules"
        print(f"✓ Learning: {len(data)} modules available")

    def test_passport_endpoint(self, beneficiary_token):
        """Test passport endpoint returns data"""
        response = requests.get(f"{BASE_URL}/api/passport?token={beneficiary_token}")
        assert response.status_code == 200
        data = response.json()
        assert "competences" in data or data is not None
        print(f"✓ Passport data retrieved")


class TestCleanup:
    """Cleanup test documents"""

    @pytest.fixture
    def beneficiary_token(self):
        """Get beneficiary token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": BENEFICIARY_PSEUDO,
            "password": BENEFICIARY_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Could not login as beneficiary")
        return response.json()["token"]

    def test_cleanup_test_documents(self, beneficiary_token):
        """Delete TEST_ prefixed documents"""
        # Get all documents
        response = requests.get(f"{BASE_URL}/api/coffre/documents?token={beneficiary_token}")
        if response.status_code != 200:
            pytest.skip("Could not get documents")
        
        documents = response.json()
        deleted = 0
        for doc in documents:
            if doc.get("title", "").startswith("TEST_"):
                del_response = requests.delete(
                    f"{BASE_URL}/api/coffre/documents/{doc['id']}?token={beneficiary_token}"
                )
                if del_response.status_code == 200:
                    deleted += 1
        
        print(f"✓ Cleaned up {deleted} test documents")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
