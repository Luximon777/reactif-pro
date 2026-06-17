"""
Test suite for Document Proof Upload feature (Certification des expériences)
Tests: POST upload-proof, GET proof-file, DELETE proof-file
Validates: MIME types, file size, experience_id validation, GridFS storage
"""
import pytest
import requests
import base64
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
MIKE7_TOKEN = "UHrqIUZvfNQnUf6SJYFNdUDlBSg_LobaMY3sKXo6EoQ"
FANNY95_TOKEN = "J3IYR6zGDSK6qCA40U4aC2ishnu5Zsyd3CPrlFW8INI"

# Known experience IDs for mike7
MIKE7_EXPERIENCE_WITH_PROOF = "e835e221-ca97-466a-b4d4-ca0e2f61b8d2"  # Agent d'entretien - has proof
MIKE7_EXPERIENCE_WITHOUT_PROOF = "c08f3d20-0955-49db-b83a-42cd32bf34b1"  # Employé polyvalent - no proof
MIKE7_EXPERIENCE_WITHOUT_PROOF_2 = "5ce6443c-6ca1-4b1f-a1ce-88285e99b531"  # Second de cuisine - no proof
EXISTING_PROOF_FILE_ID = "f2ebb355-44a4-4906-9eec-d3f74dad41e9"


class TestProofDocumentUpload:
    """Tests for POST /api/passport/experiences/upload-proof"""

    def test_upload_pdf_document_success(self):
        """Upload a valid PDF document and verify it creates proof_document"""
        # Create a minimal valid PDF (base64 encoded)
        pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000052 00000 n \n0000000101 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF"
        b64_data = base64.b64encode(pdf_content).decode('utf-8')
        
        # Upload the document to mike7's experience without proof
        payload = {
            "experience_id": MIKE7_EXPERIENCE_WITHOUT_PROOF,
            "file_data": b64_data,
            "file_name": "TEST_contrat_travail.pdf",
            "mime_type": "application/pdf"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/passport/experiences/upload-proof?token={MIKE7_TOKEN}",
            json=payload
        )
        
        assert response.status_code == 200, f"Upload failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert data.get("success") is True
        assert "file_id" in data
        assert "proof_document" in data
        assert data["proof_document"]["original_filename"] == "TEST_contrat_travail.pdf"
        assert data["proof_document"]["mime_type"] == "application/pdf"
        
        # Store file_id for cleanup
        self.__class__.uploaded_file_id = data["file_id"]
        
        print(f"✓ PDF upload successful, file_id: {data['file_id']}")

    def test_upload_jpg_document_success(self):
        """Upload a valid JPG image"""
        # Minimal JPEG header
        jpg_bytes = bytes([
            0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
            0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
            0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
            0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
            0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
            0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
            0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
            0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
            0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
            0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
            0x09, 0x0A, 0x0B, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01, 0x00, 0x00, 0x3F,
            0x00, 0xFB, 0xD5, 0xFF, 0xD9
        ])
        b64_data = base64.b64encode(jpg_bytes).decode('utf-8')
        
        payload = {
            "experience_id": MIKE7_EXPERIENCE_WITHOUT_PROOF_2,
            "file_data": b64_data,
            "file_name": "TEST_attestation.jpg",
            "mime_type": "image/jpeg"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/passport/experiences/upload-proof?token={MIKE7_TOKEN}",
            json=payload
        )
        
        assert response.status_code == 200, f"JPG upload failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data["proof_document"]["mime_type"] == "image/jpeg"
        
        self.__class__.jpg_file_id = data["file_id"]
        print(f"✓ JPG upload successful, file_id: {data['file_id']}")

    def test_upload_png_document_success(self):
        """Upload a valid PNG image"""
        # Minimal PNG (1x1 pixel)
        png_bytes = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,
            0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,
            0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,  # IEND chunk
            0x44, 0xAE, 0x42, 0x60, 0x82
        ])
        b64_data = base64.b64encode(png_bytes).decode('utf-8')
        
        # Get another experience without proof
        passport_resp = requests.get(f"{BASE_URL}/api/passport?token={MIKE7_TOKEN}")
        experiences = passport_resp.json().get("experiences", [])
        
        target_exp = None
        for exp in experiences:
            if not exp.get("proof_document") and exp["id"] not in [MIKE7_EXPERIENCE_WITHOUT_PROOF, MIKE7_EXPERIENCE_WITHOUT_PROOF_2]:
                target_exp = exp
                break
        
        if not target_exp:
            pytest.skip("No third experience without proof_document found")
        
        payload = {
            "experience_id": target_exp["id"],
            "file_data": b64_data,
            "file_name": "TEST_certificat.png",
            "mime_type": "image/png"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/passport/experiences/upload-proof?token={MIKE7_TOKEN}",
            json=payload
        )
        
        assert response.status_code == 200, f"PNG upload failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data["proof_document"]["mime_type"] == "image/png"
        
        self.__class__.png_file_id = data["file_id"]
        print(f"✓ PNG upload successful, file_id: {data['file_id']}")


class TestProofDocumentValidation:
    """Tests for validation rules on upload-proof endpoint"""

    def test_reject_invalid_mime_type(self):
        """Reject non-allowed MIME types (e.g., text/plain)"""
        b64_data = base64.b64encode(b"This is plain text").decode('utf-8')
        
        payload = {
            "experience_id": MIKE7_EXPERIENCE_WITH_PROOF,
            "file_data": b64_data,
            "file_name": "test.txt",
            "mime_type": "text/plain"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/passport/experiences/upload-proof?token={MIKE7_TOKEN}",
            json=payload
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid MIME, got {response.status_code}"
        assert "non autorisé" in response.text.lower() or "format" in response.text.lower()
        print("✓ Invalid MIME type correctly rejected")

    def test_reject_file_over_10mb(self):
        """Reject files larger than 10 MB"""
        # Create a 11 MB file (base64 encoded)
        large_content = b"X" * (11 * 1024 * 1024)  # 11 MB
        b64_data = base64.b64encode(large_content).decode('utf-8')
        
        payload = {
            "experience_id": MIKE7_EXPERIENCE_WITH_PROOF,
            "file_data": b64_data,
            "file_name": "large_file.pdf",
            "mime_type": "application/pdf"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/passport/experiences/upload-proof?token={MIKE7_TOKEN}",
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 400, f"Expected 400 for large file, got {response.status_code}"
        assert "volumineux" in response.text.lower() or "10" in response.text
        print("✓ File over 10 MB correctly rejected")

    def test_reject_nonexistent_experience_id(self):
        """Return 404 for non-existent experience_id"""
        b64_data = base64.b64encode(b"%PDF-1.4 test").decode('utf-8')
        
        payload = {
            "experience_id": "nonexistent-uuid-12345",
            "file_data": b64_data,
            "file_name": "test.pdf",
            "mime_type": "application/pdf"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/passport/experiences/upload-proof?token={MIKE7_TOKEN}",
            json=payload
        )
        
        assert response.status_code == 404, f"Expected 404 for nonexistent experience, got {response.status_code}"
        print("✓ Non-existent experience_id correctly returns 404")

    def test_reject_invalid_base64(self):
        """Reject invalid base64 data"""
        payload = {
            "experience_id": MIKE7_EXPERIENCE_WITH_PROOF,
            "file_data": "not-valid-base64!!!@@@",
            "file_name": "test.pdf",
            "mime_type": "application/pdf"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/passport/experiences/upload-proof?token={MIKE7_TOKEN}",
            json=payload
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid base64, got {response.status_code}"
        print("✓ Invalid base64 correctly rejected")


class TestProofDocumentDownload:
    """Tests for GET /api/passport/experiences/proof-file/{file_id}"""

    def test_download_existing_proof_file(self):
        """Download the existing proof file for mike7"""
        response = requests.get(
            f"{BASE_URL}/api/passport/experiences/proof-file/{EXISTING_PROOF_FILE_ID}?token={MIKE7_TOKEN}"
        )
        
        assert response.status_code == 200, f"Download failed: {response.status_code} - {response.text}"
        
        # Check content-type header
        content_type = response.headers.get("content-type", "")
        assert content_type in ["application/pdf", "image/jpeg", "image/png", "image/jpg", "application/octet-stream"], \
            f"Unexpected content-type: {content_type}"
        
        # Check content-disposition header
        content_disp = response.headers.get("content-disposition", "")
        assert "filename" in content_disp.lower(), f"Missing filename in content-disposition: {content_disp}"
        
        print(f"✓ Download successful, content-type: {content_type}")

    def test_download_nonexistent_file_returns_404(self):
        """Return 404 for non-existent file_id"""
        response = requests.get(
            f"{BASE_URL}/api/passport/experiences/proof-file/nonexistent-file-id?token={MIKE7_TOKEN}"
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Non-existent file correctly returns 404")

    def test_download_requires_valid_token(self):
        """Download requires valid authentication token"""
        response = requests.get(
            f"{BASE_URL}/api/passport/experiences/proof-file/{EXISTING_PROOF_FILE_ID}?token=invalid-token"
        )
        
        # Should return 401 or 404 (depending on implementation)
        assert response.status_code in [401, 404], f"Expected 401/404 for invalid token, got {response.status_code}"
        print("✓ Invalid token correctly rejected")


class TestProofDocumentDelete:
    """Tests for DELETE /api/passport/experiences/proof-file/{file_id}"""

    def test_delete_nonexistent_file_returns_404(self):
        """Return 404 when deleting non-existent file"""
        response = requests.delete(
            f"{BASE_URL}/api/passport/experiences/proof-file/nonexistent-file-id?token={MIKE7_TOKEN}"
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Delete non-existent file correctly returns 404")


class TestPassportCertificationStatus:
    """Tests for GET /api/passport - verify is_certified flag"""

    def test_passport_shows_certified_experience(self):
        """Verify passport returns is_certified=true for experiences with proof_document"""
        response = requests.get(f"{BASE_URL}/api/passport?token={MIKE7_TOKEN}")
        
        assert response.status_code == 200, f"Failed to get passport: {response.text}"
        passport = response.json()
        
        experiences = passport.get("experiences", [])
        assert len(experiences) > 0, "No experiences found in passport"
        
        # Find the experience with proof_document
        certified_exp = None
        for exp in experiences:
            if exp.get("proof_document"):
                certified_exp = exp
                break
        
        assert certified_exp is not None, "No experience with proof_document found"
        assert certified_exp.get("is_certified") is True, "Experience with proof_document should have is_certified=true"
        assert "file_id" in certified_exp["proof_document"], "proof_document should contain file_id"
        
        print(f"✓ Certified experience found: {certified_exp['title']}")
        print(f"  - is_certified: {certified_exp.get('is_certified')}")
        print(f"  - proof_document.file_id: {certified_exp['proof_document']['file_id']}")


class TestCleanup:
    """Cleanup test data created during tests"""

    def test_cleanup_uploaded_files(self):
        """Delete test files uploaded during tests"""
        cleaned = 0
        
        # Cleanup PDF file
        pdf_file_id = getattr(TestProofDocumentUpload, 'uploaded_file_id', None)
        if pdf_file_id:
            response = requests.delete(
                f"{BASE_URL}/api/passport/experiences/proof-file/{pdf_file_id}?token={MIKE7_TOKEN}"
            )
            if response.status_code == 200:
                print(f"✓ Cleaned up PDF file: {pdf_file_id}")
                cleaned += 1
            else:
                print(f"⚠ Could not cleanup PDF file: {response.status_code}")
        
        # Cleanup JPG file
        jpg_file_id = getattr(TestProofDocumentUpload, 'jpg_file_id', None)
        if jpg_file_id:
            response = requests.delete(
                f"{BASE_URL}/api/passport/experiences/proof-file/{jpg_file_id}?token={MIKE7_TOKEN}"
            )
            if response.status_code == 200:
                print(f"✓ Cleaned up JPG file: {jpg_file_id}")
                cleaned += 1
            else:
                print(f"⚠ Could not cleanup JPG file: {response.status_code}")
        
        # Cleanup PNG file
        png_file_id = getattr(TestProofDocumentUpload, 'png_file_id', None)
        if png_file_id:
            response = requests.delete(
                f"{BASE_URL}/api/passport/experiences/proof-file/{png_file_id}?token={MIKE7_TOKEN}"
            )
            if response.status_code == 200:
                print(f"✓ Cleaned up PNG file: {png_file_id}")
                cleaned += 1
            else:
                print(f"⚠ Could not cleanup PNG file: {response.status_code}")
        
        print(f"Total files cleaned: {cleaned}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
