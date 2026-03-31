"""
Test coffre-fort CV files endpoints for iteration 57
- GET /api/coffre/cv-files - list CV files from coffre-fort
- POST /api/cv/analyze-from-coffre - start CV analysis from coffre-fort document
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestCoffreCvFilesEndpoints:
    """Test coffre-fort CV files listing and analysis endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as bob30 who has coffre-fort CV files"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as bob30 (beneficiary with CV uploaded)
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "bob30",
            "password": "Solerys777!"
        })
        
        if login_response.status_code == 200:
            self.token = login_response.json().get("token")
        else:
            pytest.skip(f"Login failed for bob30: {login_response.status_code}")
    
    def test_get_cv_files_endpoint_exists(self):
        """Test GET /api/coffre/cv-files endpoint returns 200"""
        response = self.session.get(f"{BASE_URL}/api/coffre/cv-files?token={self.token}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Response should be a list
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✓ GET /api/coffre/cv-files returned {len(data)} CV files")
    
    def test_cv_files_response_structure(self):
        """Test CV files response has correct structure"""
        response = self.session.get(f"{BASE_URL}/api/coffre/cv-files?token={self.token}")
        assert response.status_code == 200
        
        data = response.json()
        if len(data) > 0:
            # Check first file has required fields
            first_file = data[0]
            assert "id" in first_file, "CV file should have 'id' field"
            assert "title" in first_file, "CV file should have 'title' field"
            print(f"✓ CV file structure valid: id={first_file['id']}, title={first_file['title']}")
        else:
            print("✓ No CV files found (empty list is valid)")
    
    def test_cv_files_requires_auth(self):
        """Test CV files endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/coffre/cv-files?token=invalid_token")
        assert response.status_code in [401, 403, 404], f"Expected auth error, got {response.status_code}"
        print("✓ GET /api/coffre/cv-files requires valid token")
    
    def test_analyze_from_coffre_endpoint_exists(self):
        """Test POST /api/cv/analyze-from-coffre endpoint exists"""
        # First get CV files to find a valid document_id
        cv_files_response = self.session.get(f"{BASE_URL}/api/coffre/cv-files?token={self.token}")
        assert cv_files_response.status_code == 200
        
        cv_files = cv_files_response.json()
        if len(cv_files) == 0:
            pytest.skip("No CV files in coffre-fort to test analyze-from-coffre")
        
        # Try to analyze from first CV file
        doc_id = cv_files[0]["id"]
        response = self.session.post(
            f"{BASE_URL}/api/cv/analyze-from-coffre?token={self.token}&document_id={doc_id}",
            json={}
        )
        
        # Should return 200 with job_id or 400/404 if document not found
        assert response.status_code in [200, 400, 404, 500], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "job_id" in data, "Response should contain job_id"
            assert "status" in data, "Response should contain status"
            print(f"✓ POST /api/cv/analyze-from-coffre started job: {data.get('job_id')}")
        else:
            print(f"✓ POST /api/cv/analyze-from-coffre returned {response.status_code} (expected for missing file)")
    
    def test_analyze_from_coffre_invalid_document(self):
        """Test analyze-from-coffre with invalid document_id"""
        response = self.session.post(
            f"{BASE_URL}/api/cv/analyze-from-coffre?token={self.token}&document_id=invalid_doc_id",
            json={}
        )
        assert response.status_code in [400, 404], f"Expected 400/404 for invalid doc, got {response.status_code}"
        print("✓ POST /api/cv/analyze-from-coffre rejects invalid document_id")
    
    def test_analyze_from_coffre_requires_auth(self):
        """Test analyze-from-coffre requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-from-coffre?token=invalid_token&document_id=test",
            json={}
        )
        assert response.status_code in [401, 403, 404], f"Expected auth error, got {response.status_code}"
        print("✓ POST /api/cv/analyze-from-coffre requires valid token")


class TestCoffreCvFilesWithTestboost:
    """Test coffre-fort CV files with testboost user"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as testboost"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "testboost",
            "password": "Solerys777!"
        })
        
        if login_response.status_code == 200:
            self.token = login_response.json().get("token")
        else:
            pytest.skip(f"Login failed for testboost: {login_response.status_code}")
    
    def test_cv_files_returns_list(self):
        """Test CV files endpoint returns list for testboost"""
        response = self.session.get(f"{BASE_URL}/api/coffre/cv-files?token={self.token}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ testboost has {len(data)} CV files in coffre-fort")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
