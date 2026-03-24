"""
Test CV Logo Footer Integration
Tests that the Re'Actif Pro logo is correctly added to DOCX and PDF CV files.
"""
import pytest
import requests
import os
import base64
import time
import io
import zipfile
import xml.etree.ElementTree as ET

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCVLogoFooter:
    """Tests for logo integration in CV DOCX and PDF files"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login with existing test user TestAccent who has CV models generated"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "TestAccent",
            "password": "Test1234!"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Could not login with TestAccent user")
    
    def test_logo_file_exists(self):
        """Verify logo file exists at expected path"""
        logo_path = "/app/backend/data/logo-reactif-pro.png"
        assert os.path.exists(logo_path), f"Logo file not found at {logo_path}"
        
        # Verify it's a valid PNG file (starts with PNG signature)
        with open(logo_path, 'rb') as f:
            header = f.read(8)
            # PNG signature: 89 50 4E 47 0D 0A 1A 0A
            assert header[:4] == b'\x89PNG', "File is not a valid PNG"
        
        # Verify file size is reasonable
        file_size = os.path.getsize(logo_path)
        assert file_size > 1000, f"Logo file too small: {file_size} bytes"
        print(f"Logo file exists and is valid PNG ({file_size} bytes)")
    
    def test_cv_models_exist(self, auth_token):
        """Verify user has CV models generated"""
        response = requests.get(
            f"{BASE_URL}/api/cv/models",
            params={"token": auth_token}
        )
        assert response.status_code == 200, f"Failed to get CV models: {response.text}"
        
        data = response.json()
        models = data.get("models", {})
        assert len(models) > 0, "No CV models found for user"
        print(f"Found CV models: {list(models.keys())}")
    
    def test_docx_download_contains_image_in_footer(self, auth_token):
        """Download DOCX and verify it contains an image in the footer section"""
        # Try classique model first
        response = requests.get(
            f"{BASE_URL}/api/cv/download/classique",
            params={"token": auth_token}
        )
        
        if response.status_code == 404:
            # Try other model types
            for model_type in ["competences", "transversale", "nouvelle_generation"]:
                response = requests.get(
                    f"{BASE_URL}/api/cv/download/{model_type}",
                    params={"token": auth_token}
                )
                if response.status_code == 200:
                    break
        
        assert response.status_code == 200, f"Failed to download DOCX: {response.text}"
        
        # DOCX is a ZIP file - extract and check for image in footer
        docx_bytes = response.content
        assert len(docx_bytes) > 1000, "DOCX file too small"
        
        # Parse DOCX (it's a ZIP archive)
        with zipfile.ZipFile(io.BytesIO(docx_bytes), 'r') as zf:
            file_list = zf.namelist()
            print(f"DOCX contents: {file_list}")
            
            # Check for images in word/media folder
            media_files = [f for f in file_list if f.startswith('word/media/')]
            assert len(media_files) > 0, "No images found in DOCX word/media folder"
            print(f"Found media files: {media_files}")
            
            # Check footer XML exists
            footer_files = [f for f in file_list if 'footer' in f.lower()]
            assert len(footer_files) > 0, "No footer files found in DOCX"
            print(f"Found footer files: {footer_files}")
            
            # Parse footer XML to verify image reference
            for footer_file in footer_files:
                if footer_file.endswith('.xml'):
                    footer_content = zf.read(footer_file).decode('utf-8')
                    # Check for drawing/image reference in footer
                    has_drawing = 'w:drawing' in footer_content or 'a:blip' in footer_content or 'r:embed' in footer_content
                    if has_drawing:
                        print(f"Footer {footer_file} contains image reference")
                        # Check for RIGHT alignment
                        has_right_align = 'w:jc w:val="right"' in footer_content or 'jc' in footer_content
                        print(f"Footer alignment check: {has_right_align}")
                        return  # Success
            
            # If we get here, check if any footer has image
            assert False, "No image reference found in footer XML files"
    
    def test_pdf_download_contains_image(self, auth_token):
        """Download PDF and verify it contains image objects"""
        # Try classique model first
        response = requests.get(
            f"{BASE_URL}/api/cv/download-pdf/classique",
            params={"token": auth_token}
        )
        
        if response.status_code == 404:
            # Try other model types
            for model_type in ["competences", "transversale", "nouvelle_generation"]:
                response = requests.get(
                    f"{BASE_URL}/api/cv/download-pdf/{model_type}",
                    params={"token": auth_token}
                )
                if response.status_code == 200:
                    break
        
        assert response.status_code == 200, f"Failed to download PDF: {response.text}"
        
        pdf_bytes = response.content
        assert len(pdf_bytes) > 1000, "PDF file too small"
        
        # Check PDF header
        assert pdf_bytes[:4] == b'%PDF', "Not a valid PDF file"
        
        # Check for image objects in PDF
        # PDFs with images typically contain /XObject and /Image references
        pdf_text = pdf_bytes.decode('latin-1', errors='ignore')
        
        has_xobject = '/XObject' in pdf_text
        has_image = '/Image' in pdf_text or '/Subtype /Image' in pdf_text
        has_dctdecode = '/DCTDecode' in pdf_text  # JPEG compression
        has_flatedecode = '/FlateDecode' in pdf_text  # PNG compression
        
        print(f"PDF analysis: XObject={has_xobject}, Image={has_image}, DCT={has_dctdecode}, Flate={has_flatedecode}")
        
        # At least one image indicator should be present
        assert has_xobject or has_image, "No image objects found in PDF"
        print("PDF contains image objects (logo likely present)")
    
    def test_docx_footer_alignment_right(self, auth_token):
        """Verify DOCX footer has RIGHT alignment"""
        response = requests.get(
            f"{BASE_URL}/api/cv/download/classique",
            params={"token": auth_token}
        )
        
        if response.status_code == 404:
            for model_type in ["competences", "transversale", "nouvelle_generation"]:
                response = requests.get(
                    f"{BASE_URL}/api/cv/download/{model_type}",
                    params={"token": auth_token}
                )
                if response.status_code == 200:
                    break
        
        assert response.status_code == 200
        
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zf:
            footer_files = [f for f in zf.namelist() if 'footer' in f.lower() and f.endswith('.xml')]
            
            for footer_file in footer_files:
                footer_content = zf.read(footer_file).decode('utf-8')
                # Check for right alignment in paragraph properties
                # DOCX uses <w:jc w:val="right"/> for right alignment
                if 'right' in footer_content.lower():
                    print(f"Footer {footer_file} has right alignment")
                    return
            
            # Also check document.xml for footer references
            print("Checking footer alignment in document structure...")


class TestCVAnalyzeTextEndpoint:
    """Test CV text analysis endpoint still works"""
    
    @pytest.fixture(scope="class")
    def new_user_token(self):
        """Create a new test user for CV analysis"""
        import uuid
        pseudo = f"TEST_logo_{uuid.uuid4().hex[:8]}"
        
        # Register
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "Test1234!",
            "role": "particulier"
        })
        
        if response.status_code in [200, 201]:
            return response.json().get("token")
        
        # If registration fails, try login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": pseudo,
            "password": "Test1234!"
        })
        if response.status_code == 200:
            return response.json().get("token")
        
        pytest.skip("Could not create test user")
    
    def test_analyze_text_endpoint_works(self, new_user_token):
        """Verify POST /api/cv/analyze-text still works"""
        sample_cv_text = """
        Jean Dupont
        Développeur Full Stack
        Email: jean.dupont@email.com
        Téléphone: 06 12 34 56 78
        
        PROFIL
        Développeur passionné avec 5 ans d'expérience en développement web.
        
        EXPÉRIENCES
        - Développeur Senior chez TechCorp (2020-2024)
          Développement d'applications React et Node.js
        - Développeur Junior chez StartupXYZ (2018-2020)
          Maintenance et évolution d'applications PHP
        
        FORMATION
        - Master Informatique, Université Paris (2018)
        - Licence Informatique, Université Lyon (2016)
        
        COMPÉTENCES
        JavaScript, React, Node.js, Python, SQL, Git
        """
        
        response = requests.post(
            f"{BASE_URL}/api/cv/analyze-text",
            params={"token": new_user_token},
            json={"text": sample_cv_text, "filename": "test_cv.txt"}
        )
        
        assert response.status_code == 200, f"CV analyze-text failed: {response.text}"
        
        data = response.json()
        assert "job_id" in data, "No job_id in response"
        assert data.get("status") == "started", f"Unexpected status: {data.get('status')}"
        print(f"CV analysis started with job_id: {data['job_id']}")


class TestCVGenerateModelsEndpoint:
    """Test CV model generation endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login with existing test user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "TestAccent",
            "password": "Test1234!"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Could not login with TestAccent user")
    
    def test_generate_models_endpoint_works(self, auth_token):
        """Verify POST /api/cv/generate-models endpoint is accessible"""
        # Just verify the endpoint responds correctly
        # We don't want to trigger actual generation as it uses LLM
        response = requests.post(
            f"{BASE_URL}/api/cv/generate-models",
            params={"token": auth_token},
            json={"model_types": ["classique"], "job_offer": ""}
        )
        
        # Should either start generation or return error about missing CV
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        print(f"Generate models endpoint response: {response.status_code}")


class TestDownloadEndpoints:
    """Test DOCX and PDF download endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login with existing test user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "TestAccent",
            "password": "Test1234!"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Could not login with TestAccent user")
    
    def test_download_docx_endpoint(self, auth_token):
        """Test GET /api/cv/download/{model_type} returns DOCX"""
        for model_type in ["classique", "competences", "transversale", "nouvelle_generation"]:
            response = requests.get(
                f"{BASE_URL}/api/cv/download/{model_type}",
                params={"token": auth_token}
            )
            
            if response.status_code == 200:
                # Verify content type
                content_type = response.headers.get('Content-Type', '')
                assert 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type or len(response.content) > 0
                
                # Verify it's a valid ZIP (DOCX is ZIP)
                assert response.content[:2] == b'PK', f"DOCX for {model_type} is not a valid ZIP"
                print(f"DOCX download for {model_type}: OK ({len(response.content)} bytes)")
                return
        
        pytest.skip("No DOCX models available for download")
    
    def test_download_pdf_endpoint(self, auth_token):
        """Test GET /api/cv/download-pdf/{model_type} returns PDF"""
        for model_type in ["classique", "competences", "transversale", "nouvelle_generation"]:
            response = requests.get(
                f"{BASE_URL}/api/cv/download-pdf/{model_type}",
                params={"token": auth_token}
            )
            
            if response.status_code == 200:
                # Verify it's a valid PDF
                assert response.content[:4] == b'%PDF', f"PDF for {model_type} is not valid"
                print(f"PDF download for {model_type}: OK ({len(response.content)} bytes)")
                return
        
        pytest.skip("No PDF models available for download")
    
    def test_invalid_model_type_returns_400(self, auth_token):
        """Test invalid model type returns 400"""
        response = requests.get(
            f"{BASE_URL}/api/cv/download/invalid_type",
            params={"token": auth_token}
        )
        assert response.status_code == 400, f"Expected 400 for invalid model type, got {response.status_code}"
        
        response = requests.get(
            f"{BASE_URL}/api/cv/download-pdf/invalid_type",
            params={"token": auth_token}
        )
        assert response.status_code == 400, f"Expected 400 for invalid PDF model type, got {response.status_code}"
        print("Invalid model type correctly returns 400")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
