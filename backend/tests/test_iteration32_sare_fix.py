"""
Test Iteration 32 - Validation du fix S.A.R.E pour peter7/peter9
Bug: Les preuves S.A.R.E affichaient 'Aucun contenu S.A.R.E disponible' car les IDs d'expériences
dans coffre_documents ne correspondaient pas aux vrais IDs du passeport.
Fix: Migration dynamique qui lit les vrais IDs d'expériences et crée coffre docs + skill_illustrations avec les bons IDs.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSAREFix:
    """Tests pour valider le fix du bug S.A.R.E"""
    
    @pytest.fixture(scope="class")
    def peter7_token(self):
        """Login peter7 et récupérer le token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "peter7",
            "password": "Solerys777!"
        })
        assert response.status_code == 200, f"Login peter7 failed: {response.text}"
        data = response.json()
        assert "token" in data, "Token manquant dans la réponse"
        return data["token"]
    
    @pytest.fixture(scope="class")
    def peter9_token(self):
        """Login peter9 et récupérer le token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "peter9",
            "password": "Solerys777!"
        })
        assert response.status_code == 200, f"Login peter9 failed: {response.text}"
        data = response.json()
        assert "token" in data, "Token manquant dans la réponse"
        return data["token"]
    
    # ═══ TESTS PETER7 ═══
    
    def test_peter7_coffre_documents_count(self, peter7_token):
        """peter7 doit avoir 33 documents (1 CV + 20 S.A.R.E + 10 contrats + 2 diplômes)"""
        response = requests.get(f"{BASE_URL}/api/coffre/documents?token={peter7_token}")
        assert response.status_code == 200, f"API coffre/documents failed: {response.text}"
        docs = response.json()  # API returns list directly
        assert len(docs) == 33, f"Expected 33 documents, got {len(docs)}"
        
        # Vérifier la répartition par type
        cv_count = sum(1 for d in docs if d.get("document_type") == "cv")
        sare_count = sum(1 for d in docs if d.get("document_type") == "sare_proof")
        contrat_count = sum(1 for d in docs if d.get("document_type") == "contrat")
        diplome_count = sum(1 for d in docs if d.get("document_type") in ["diplome", "certificat"])
        
        assert cv_count == 1, f"Expected 1 CV, got {cv_count}"
        assert sare_count == 20, f"Expected 20 S.A.R.E proofs, got {sare_count}"
        assert contrat_count == 10, f"Expected 10 contrats, got {contrat_count}"
        assert diplome_count == 2, f"Expected 2 diplômes/certificats, got {diplome_count}"
    
    def test_peter7_illustrations_count_and_content(self, peter7_token):
        """peter7 doit avoir 20 illustrations avec contenu S.A.R.E non-vide"""
        response = requests.get(f"{BASE_URL}/api/passport/illustrations?token={peter7_token}")
        assert response.status_code == 200, f"API passport/illustrations failed: {response.text}"
        data = response.json()
        illustrations = data.get("illustrations", [])
        assert len(illustrations) == 20, f"Expected 20 illustrations, got {len(illustrations)}"
        
        # Vérifier que chaque illustration a du contenu S.A.R.E
        for illus in illustrations:
            assert illus.get("sare_situation"), f"sare_situation vide pour illustration {illus.get('id')}"
            assert illus.get("sare_action"), f"sare_action vide pour illustration {illus.get('id')}"
            assert illus.get("sare_resultat"), f"sare_resultat vide pour illustration {illus.get('id')}"
            assert illus.get("sare_enseignement"), f"sare_enseignement vide pour illustration {illus.get('id')}"
    
    def test_peter7_certification_status(self, peter7_token):
        """peter7 doit avoir badge='Expert Certifié' level=3, 10/10 prouvées, 10/10 contrats"""
        response = requests.get(f"{BASE_URL}/api/coffre/certification-status?token={peter7_token}")
        assert response.status_code == 200, f"API certification-status failed: {response.text}"
        data = response.json()
        
        badge = data.get("badge", {})
        assert badge.get("level") == 3, f"Expected badge level 3, got {badge.get('level')}"
        assert badge.get("label") == "Expert Certifié", f"Expected 'Expert Certifié', got {badge.get('label')}"
        
        stats = data.get("stats", {})
        assert stats.get("total_experiences") == 10, f"Expected 10 experiences, got {stats.get('total_experiences')}"
        assert stats.get("total_proved") == 10, f"Expected 10 proved, got {stats.get('total_proved')}"
        assert stats.get("total_with_contract") == 10, f"Expected 10 with contract, got {stats.get('total_with_contract')}"
    
    def test_peter7_experience_ids_match(self, peter7_token):
        """Les IDs linked_experience_id des coffre_documents correspondent aux IDs d'expériences du passeport"""
        # Get passport experiences
        passport_resp = requests.get(f"{BASE_URL}/api/passport?token={peter7_token}")
        assert passport_resp.status_code == 200
        passport = passport_resp.json()
        passport_exp_ids = set(exp.get("id") for exp in passport.get("experiences", []) if exp.get("id"))
        
        # Get coffre documents (API returns list directly)
        coffre_resp = requests.get(f"{BASE_URL}/api/coffre/documents?token={peter7_token}")
        assert coffre_resp.status_code == 200
        docs = coffre_resp.json()
        
        # Get linked_experience_id from S.A.R.E proofs
        coffre_exp_ids = set(d.get("linked_experience_id") for d in docs 
                            if d.get("document_type") == "sare_proof" and d.get("linked_experience_id"))
        
        # All coffre exp IDs should be in passport exp IDs
        assert coffre_exp_ids.issubset(passport_exp_ids), \
            f"Mismatch! Coffre IDs not in passport: {coffre_exp_ids - passport_exp_ids}"
        
        # Each passport experience should have 2 S.A.R.E proofs
        for exp_id in passport_exp_ids:
            sare_for_exp = [d for d in docs if d.get("linked_experience_id") == exp_id and d.get("document_type") == "sare_proof"]
            assert len(sare_for_exp) == 2, f"Expected 2 S.A.R.E proofs for exp {exp_id}, got {len(sare_for_exp)}"
    
    def test_peter7_illustrations_match_coffre(self, peter7_token):
        """Les illustrations ont les mêmes experience_id et soft_skill que les coffre_documents"""
        # Get illustrations
        illus_resp = requests.get(f"{BASE_URL}/api/passport/illustrations?token={peter7_token}")
        assert illus_resp.status_code == 200
        illustrations = illus_resp.json().get("illustrations", [])
        
        # Get coffre documents (API returns list directly)
        coffre_resp = requests.get(f"{BASE_URL}/api/coffre/documents?token={peter7_token}")
        assert coffre_resp.status_code == 200
        docs = coffre_resp.json()
        sare_docs = [d for d in docs if d.get("document_type") == "sare_proof"]
        
        # For each S.A.R.E doc, there should be a matching illustration
        for doc in sare_docs:
            exp_id = doc.get("linked_experience_id")
            skill = doc.get("linked_soft_skill")
            matching_illus = [i for i in illustrations 
                             if i.get("experience_id") == exp_id and i.get("soft_skill") == skill]
            assert len(matching_illus) >= 1, \
                f"No matching illustration for coffre doc exp_id={exp_id}, skill={skill}"
    
    # ═══ TESTS PETER9 ═══
    
    def test_peter9_coffre_documents_count(self, peter9_token):
        """peter9 doit aussi avoir 33 documents"""
        response = requests.get(f"{BASE_URL}/api/coffre/documents?token={peter9_token}")
        assert response.status_code == 200, f"API coffre/documents failed: {response.text}"
        docs = response.json()  # API returns list directly
        assert len(docs) == 33, f"Expected 33 documents for peter9, got {len(docs)}"
    
    def test_peter9_illustrations_with_sare_content(self, peter9_token):
        """peter9 doit avoir des illustrations avec contenu S.A.R.E"""
        response = requests.get(f"{BASE_URL}/api/passport/illustrations?token={peter9_token}")
        assert response.status_code == 200
        illustrations = response.json().get("illustrations", [])
        assert len(illustrations) == 20, f"Expected 20 illustrations for peter9, got {len(illustrations)}"
        
        # Vérifier contenu non-vide
        for illus in illustrations:
            assert illus.get("sare_situation"), f"sare_situation vide pour peter9 illustration"
            assert illus.get("sare_action"), f"sare_action vide pour peter9 illustration"
    
    def test_peter9_experience_ids_match(self, peter9_token):
        """Les IDs d'expériences de peter9 correspondent aussi"""
        # Get passport experiences
        passport_resp = requests.get(f"{BASE_URL}/api/passport?token={peter9_token}")
        assert passport_resp.status_code == 200
        passport = passport_resp.json()
        passport_exp_ids = set(exp.get("id") for exp in passport.get("experiences", []) if exp.get("id"))
        
        # Get coffre documents (API returns list directly)
        coffre_resp = requests.get(f"{BASE_URL}/api/coffre/documents?token={peter9_token}")
        assert coffre_resp.status_code == 200
        docs = coffre_resp.json()
        
        coffre_exp_ids = set(d.get("linked_experience_id") for d in docs 
                            if d.get("document_type") == "sare_proof" and d.get("linked_experience_id"))
        
        assert coffre_exp_ids.issubset(passport_exp_ids), \
            f"peter9 mismatch! Coffre IDs not in passport: {coffre_exp_ids - passport_exp_ids}"
    
    def test_peter9_certification_status(self, peter9_token):
        """peter9 doit aussi avoir le badge Expert Certifié"""
        response = requests.get(f"{BASE_URL}/api/coffre/certification-status?token={peter9_token}")
        assert response.status_code == 200
        data = response.json()
        
        badge = data.get("badge", {})
        assert badge.get("level") == 3, f"Expected badge level 3 for peter9, got {badge.get('level')}"
        assert badge.get("label") == "Expert Certifié"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
