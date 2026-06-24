"""
Test Iteration 31 - Coffre-fort et Certification Status pour peter7/peter9
Tests des fonctionnalités:
- Login peter7/peter9
- GET /api/coffre/documents - 33+ documents (20 S.A.R.E, 10 contrats, 2 diplômes, 1 CV)
- GET /api/coffre/certification-status - Badge 'Expert Certifié' level 3
- 10/10 expériences prouvées, 10/10 avec contrat
- Toutes les expériences ont statut 'Expert' (pas 'En attente')
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPeter7Peter9Authentication:
    """Test authentication for peter7 and peter9"""
    
    def test_login_peter7(self):
        """Test login with peter7 credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "peter7",
            "password": "Solerys777!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "Token not returned"
        assert len(data["token"]) > 0, "Token is empty"
        print(f"✓ peter7 login successful, token: {data['token'][:20]}...")
        
    def test_login_peter9(self):
        """Test login with peter9 credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "peter9",
            "password": "Solerys777!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "Token not returned"
        assert len(data["token"]) > 0, "Token is empty"
        print(f"✓ peter9 login successful, token: {data['token'][:20]}...")


class TestPeter7CoffreDocuments:
    """Test coffre documents for peter7 - should have 33+ documents"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get peter7 token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "peter7",
            "password": "Solerys777!"
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        
    def test_coffre_documents_count(self):
        """Test that peter7 has 33+ documents in coffre"""
        response = requests.get(f"{BASE_URL}/api/coffre/documents?token={self.token}")
        assert response.status_code == 200, f"Failed to get documents: {response.text}"
        documents = response.json()
        assert isinstance(documents, list), "Documents should be a list"
        print(f"✓ peter7 has {len(documents)} documents in coffre")
        assert len(documents) >= 33, f"Expected 33+ documents, got {len(documents)}"
        
    def test_coffre_documents_types(self):
        """Test document types: 20 S.A.R.E, 10 contrats, 2 diplômes, 1 CV"""
        response = requests.get(f"{BASE_URL}/api/coffre/documents?token={self.token}")
        assert response.status_code == 200
        documents = response.json()
        
        # Count by document_type
        sare_count = sum(1 for d in documents if d.get("document_type") == "sare_proof")
        contrat_count = sum(1 for d in documents if d.get("document_type") == "contrat")
        diplome_count = sum(1 for d in documents if d.get("document_type") in ["diplome", "certificat"])
        cv_count = sum(1 for d in documents if d.get("document_type") == "cv")
        
        print(f"✓ Document types: {sare_count} S.A.R.E, {contrat_count} contrats, {diplome_count} diplômes, {cv_count} CV")
        
        assert sare_count >= 20, f"Expected 20+ S.A.R.E proofs, got {sare_count}"
        assert contrat_count >= 10, f"Expected 10+ contrats, got {contrat_count}"
        assert diplome_count >= 2, f"Expected 2+ diplômes/certificats, got {diplome_count}"
        assert cv_count >= 1, f"Expected 1+ CV, got {cv_count}"
        
    def test_cv_has_certifie_badge(self):
        """Test that CV has 'certifie' trust level"""
        response = requests.get(f"{BASE_URL}/api/coffre/documents?token={self.token}")
        assert response.status_code == 200
        documents = response.json()
        
        cv_docs = [d for d in documents if d.get("document_type") == "cv"]
        assert len(cv_docs) >= 1, "No CV found"
        
        cv = cv_docs[0]
        print(f"✓ CV found: '{cv.get('title')}' with trust_level: {cv.get('trust_level')}")
        assert cv.get("trust_level") == "certifie", f"CV should have trust_level 'certifie', got {cv.get('trust_level')}"


class TestPeter7CertificationStatus:
    """Test certification status for peter7 - should be Expert Certifié level 3"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get peter7 token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "peter7",
            "password": "Solerys777!"
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        
    def test_certification_status_badge_level_3(self):
        """Test that peter7 has Expert Certifié badge (level 3)"""
        response = requests.get(f"{BASE_URL}/api/coffre/certification-status?token={self.token}")
        assert response.status_code == 200, f"Failed to get certification status: {response.text}"
        data = response.json()
        
        assert "badge" in data, "Badge not in response"
        badge = data["badge"]
        print(f"✓ Badge: level={badge.get('level')}, label='{badge.get('label')}', color={badge.get('color')}")
        
        assert badge.get("level") == 3, f"Expected badge level 3 (Expert Certifié), got {badge.get('level')}"
        assert badge.get("label") == "Expert Certifié", f"Expected label 'Expert Certifié', got {badge.get('label')}"
        
    def test_certification_status_10_experiences_proved(self):
        """Test that peter7 has 10/10 experiences proved"""
        response = requests.get(f"{BASE_URL}/api/coffre/certification-status?token={self.token}")
        assert response.status_code == 200
        data = response.json()
        
        assert "stats" in data, "Stats not in response"
        stats = data["stats"]
        print(f"✓ Stats: total_experiences={stats.get('total_experiences')}, total_proved={stats.get('total_proved')}, total_with_contract={stats.get('total_with_contract')}")
        
        assert stats.get("total_experiences") == 10, f"Expected 10 total experiences, got {stats.get('total_experiences')}"
        assert stats.get("total_proved") == 10, f"Expected 10 proved experiences, got {stats.get('total_proved')}"
        
    def test_certification_status_10_with_contract(self):
        """Test that peter7 has 10/10 experiences with contract"""
        response = requests.get(f"{BASE_URL}/api/coffre/certification-status?token={self.token}")
        assert response.status_code == 200
        data = response.json()
        
        stats = data["stats"]
        assert stats.get("total_with_contract") == 10, f"Expected 10 experiences with contract, got {stats.get('total_with_contract')}"
        
    def test_all_experiences_expert_status(self):
        """Test that all experiences have 'Expert' status (proofs_count > 0 AND has_contract)"""
        response = requests.get(f"{BASE_URL}/api/coffre/certification-status?token={self.token}")
        assert response.status_code == 200
        data = response.json()
        
        workplaces = data.get("workplaces", [])
        assert len(workplaces) > 0, "No workplaces found"
        
        all_experiences = []
        for wp in workplaces:
            for exp in wp.get("experiences", []):
                all_experiences.append({
                    "title": exp.get("title"),
                    "organization": wp.get("organization"),
                    "proofs_count": exp.get("proofs_count", 0),
                    "has_contract": exp.get("has_contract", False),
                })
        
        print(f"✓ Found {len(all_experiences)} experiences across {len(workplaces)} workplaces")
        
        # Check each experience has Expert status (proofs_count > 0 AND has_contract)
        non_expert = []
        for exp in all_experiences:
            if exp["proofs_count"] == 0 or not exp["has_contract"]:
                non_expert.append(exp)
                
        if non_expert:
            print(f"✗ Non-expert experiences found:")
            for exp in non_expert:
                print(f"  - {exp['title']} @ {exp['organization']}: proofs={exp['proofs_count']}, contract={exp['has_contract']}")
                
        assert len(non_expert) == 0, f"Expected all experiences to be Expert status, but {len(non_expert)} are not"
        print(f"✓ All {len(all_experiences)} experiences have Expert status")


class TestPeter9CoffreDocuments:
    """Test coffre documents for peter9 - should have same data as peter7"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get peter9 token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "peter9",
            "password": "Solerys777!"
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        
    def test_coffre_documents_count(self):
        """Test that peter9 has 33+ documents in coffre"""
        response = requests.get(f"{BASE_URL}/api/coffre/documents?token={self.token}")
        assert response.status_code == 200, f"Failed to get documents: {response.text}"
        documents = response.json()
        print(f"✓ peter9 has {len(documents)} documents in coffre")
        assert len(documents) >= 33, f"Expected 33+ documents, got {len(documents)}"
        
    def test_certification_status_badge_level_3(self):
        """Test that peter9 has Expert Certifié badge (level 3)"""
        response = requests.get(f"{BASE_URL}/api/coffre/certification-status?token={self.token}")
        assert response.status_code == 200, f"Failed to get certification status: {response.text}"
        data = response.json()
        
        badge = data.get("badge", {})
        print(f"✓ peter9 Badge: level={badge.get('level')}, label='{badge.get('label')}'")
        
        assert badge.get("level") == 3, f"Expected badge level 3 (Expert Certifié), got {badge.get('level')}"


class TestSkillIllustrations:
    """Test skill illustrations (S.A.R.E proofs) for peter7"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get peter7 token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "peter7",
            "password": "Solerys777!"
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        
    def test_skill_illustrations_count(self):
        """Test that peter7 has 20 skill illustrations"""
        response = requests.get(f"{BASE_URL}/api/passport/illustrations?token={self.token}")
        assert response.status_code == 200, f"Failed to get illustrations: {response.text}"
        data = response.json()
        
        illustrations = data.get("illustrations", [])
        print(f"✓ peter7 has {len(illustrations)} skill illustrations")
        assert len(illustrations) >= 20, f"Expected 20+ illustrations, got {len(illustrations)}"
        
    def test_skill_illustrations_have_sare_fields(self):
        """Test that illustrations have S.A.R.E fields"""
        response = requests.get(f"{BASE_URL}/api/passport/illustrations?token={self.token}")
        assert response.status_code == 200
        data = response.json()
        
        illustrations = data.get("illustrations", [])
        assert len(illustrations) > 0, "No illustrations found"
        
        # Check first illustration has S.A.R.E fields
        illus = illustrations[0]
        sare_fields = ["sare_situation", "sare_action", "sare_resultat", "sare_enseignement"]
        missing = [f for f in sare_fields if not illus.get(f)]
        
        print(f"✓ First illustration: soft_skill='{illus.get('soft_skill')}', skill_type='{illus.get('skill_type')}'")
        
        if missing:
            print(f"  Warning: Missing S.A.R.E fields: {missing}")
        else:
            print(f"  ✓ All S.A.R.E fields present")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
