"""
Test suite for RE'ACTIF PRO Workflow Features (Iteration 49)
Tests the new workflow modules:
1. Synthèse pré-entretien IA
2. Compte rendu d'entretien IA
3. Plan d'action intelligent
4. Vue lecture rapide
5. Export intelligent
6. Détection de décrochage
7. Bilan de fin de parcours
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
PARTNER_EMAIL = "cluximon@gmail.com"
PARTNER_PASSWORD = "Solerys777!"
BENEFICIARY_ID = "27deb12f-4eea-42e5-9117-3771a085a00e"  # bob meyer


class TestPartnerLogin:
    """Test partner authentication"""
    
    def test_partner_login(self):
        """Test partner login and get token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login-pro",
            json={"pseudo": PARTNER_EMAIL, "password": PARTNER_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        print(f"✓ Partner login successful, token: {data['token'][:20]}...")
        return data["token"]


@pytest.fixture(scope="module")
def partner_token():
    """Get partner token for all tests"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login-pro",
        json={"pseudo": PARTNER_EMAIL, "password": PARTNER_PASSWORD}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["token"]


class TestLectureRapide:
    """Test Vue Lecture Rapide (Quick Read View)"""
    
    def test_get_lecture_rapide(self, partner_token):
        """GET /api/partenaires/beneficiaires/{id}/lecture-rapide returns proper JSON"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/beneficiaires/{BENEFICIARY_ID}/lecture-rapide?token={partner_token}"
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify required fields
        assert "identite" in data, "Missing 'identite' field"
        assert "diagnostic_resume" in data, "Missing 'diagnostic_resume' field"
        assert "risque_decrochage" in data, "Missing 'risque_decrochage' field"
        
        # Verify identite structure
        identite = data["identite"]
        assert "nom" in identite, "Missing 'nom' in identite"
        assert "progression" in identite, "Missing 'progression' in identite"
        
        # Verify risk score structure
        risk = data["risque_decrochage"]
        assert "score" in risk, "Missing 'score' in risque_decrochage"
        assert "niveau" in risk, "Missing 'niveau' in risque_decrochage"
        
        print(f"✓ Lecture rapide returned: {identite['nom']}, progression: {identite['progression']}%, risk: {risk['niveau']}")


class TestSynthesePreEntretien:
    """Test Synthèse Pré-Entretien IA"""
    
    def test_generate_synthese(self, partner_token):
        """POST /api/partenaires/beneficiaires/{id}/synthese-pre-entretien generates AI content"""
        response = requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires/{BENEFICIARY_ID}/synthese-pre-entretien?token={partner_token}",
            timeout=60  # AI calls can take time
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify AI-generated content structure
        assert "resume_parcours" in data, "Missing 'resume_parcours'"
        assert "points_forts" in data, "Missing 'points_forts'"
        assert "points_vigilance" in data, "Missing 'points_vigilance'"
        assert "questions_a_explorer" in data, "Missing 'questions_a_explorer'"
        assert "niveau_urgence" in data, "Missing 'niveau_urgence'"
        assert "niveau_autonomie" in data, "Missing 'niveau_autonomie'"
        
        # Verify lists are populated
        assert isinstance(data["points_forts"], list), "points_forts should be a list"
        assert isinstance(data["questions_a_explorer"], list), "questions_a_explorer should be a list"
        
        print(f"✓ Synthèse generated with {len(data.get('points_forts', []))} points forts, urgence: {data['niveau_urgence']}")


class TestCompteRendu:
    """Test Compte Rendu d'Entretien IA"""
    
    def test_generate_compte_rendu_diagnostic(self, partner_token):
        """POST /api/partenaires/beneficiaires/{id}/compte-rendu with type_entretien=diagnostic"""
        payload = {
            "type_entretien": "diagnostic",
            "notes_conseiller": "Test notes for diagnostic interview"
        }
        response = requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires/{BENEFICIARY_ID}/compte-rendu?token={partner_token}",
            json=payload,
            timeout=60
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify report structure
        assert "id" in data, "Missing 'id'"
        assert "type" in data, "Missing 'type'"
        assert data["type"] == "diagnostic", f"Expected type 'diagnostic', got '{data['type']}'"
        assert "content" in data, "Missing 'content'"
        assert "ai_generated" in data, "Missing 'ai_generated'"
        assert data["ai_generated"] == True, "Should be AI generated"
        
        # Verify content structure
        content = data["content"]
        assert "texte_complet" in content, "Missing 'texte_complet' in content"
        
        print(f"✓ Compte rendu generated: ID={data['id'][:8]}..., type={data['type']}")
        return data["id"]
    
    def test_get_comptes_rendus(self, partner_token):
        """GET /api/partenaires/beneficiaires/{id}/comptes-rendus returns list"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/beneficiaires/{BENEFICIARY_ID}/comptes-rendus?token={partner_token}"
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Should return a list"
        print(f"✓ Found {len(data)} compte(s) rendu(s)")


class TestPlanAction:
    """Test Plan d'Action Intelligent"""
    
    def test_generate_plan_action(self, partner_token):
        """POST /api/partenaires/beneficiaires/{id}/plan-action/generer generates action plan"""
        response = requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires/{BENEFICIARY_ID}/plan-action/generer?token={partner_token}",
            timeout=60
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify plan structure
        assert "id" in data, "Missing 'id'"
        assert "objectif_principal" in data, "Missing 'objectif_principal'"
        assert "actions" in data, "Missing 'actions'"
        assert "dispositifs_recommandes" in data, "Missing 'dispositifs_recommandes'"
        
        # Verify actions structure
        actions = data["actions"]
        assert isinstance(actions, list), "actions should be a list"
        if len(actions) > 0:
            action = actions[0]
            assert "id" in action, "Action missing 'id'"
            assert "titre" in action, "Action missing 'titre'"
            assert "status" in action, "Action missing 'status'"
            assert "categorie" in action, "Action missing 'categorie'"
        
        print(f"✓ Plan d'action generated: {len(actions)} actions, objectif: {data['objectif_principal'][:50]}...")
        return data
    
    def test_get_plan_action(self, partner_token):
        """GET /api/partenaires/beneficiaires/{id}/plan-action returns plan"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/beneficiaires/{BENEFICIARY_ID}/plan-action?token={partner_token}"
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        if data:
            assert "actions" in data, "Missing 'actions'"
            print(f"✓ Plan d'action retrieved: {len(data.get('actions', []))} actions")
        else:
            print("✓ No plan d'action exists yet (null response)")
    
    def test_update_action_status(self, partner_token):
        """PUT /api/partenaires/plan-action/{plan_id}/actions/{action_id} updates status"""
        # First get the plan
        response = requests.get(
            f"{BASE_URL}/api/partenaires/beneficiaires/{BENEFICIARY_ID}/plan-action?token={partner_token}"
        )
        assert response.status_code == 200
        plan = response.json()
        
        if not plan or not plan.get("actions"):
            pytest.skip("No plan or actions to update")
        
        plan_id = plan["id"]
        action_id = plan["actions"][0]["id"]
        
        # Update action status
        response = requests.put(
            f"{BASE_URL}/api/partenaires/plan-action/{plan_id}/actions/{action_id}?token={partner_token}",
            json={"status": "en_cours"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "message" in data, "Missing 'message'"
        
        print(f"✓ Action status updated to 'en_cours'")


class TestExport:
    """Test Export Intelligent"""
    
    def test_export_dossier(self, partner_token):
        """GET /api/partenaires/beneficiaires/{id}/export returns text content"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/beneficiaires/{BENEFICIARY_ID}/export?token={partner_token}&format=text"
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "content" in data, "Missing 'content'"
        assert "format" in data, "Missing 'format'"
        assert data["format"] == "text", f"Expected format 'text', got '{data['format']}'"
        
        content = data["content"]
        assert len(content) > 100, "Content seems too short"
        assert "DOSSIER BÉNÉFICIAIRE" in content, "Missing header in export"
        
        print(f"✓ Export generated: {len(content)} characters")


class TestRisqueDecrochage:
    """Test Détection de Décrochage"""
    
    def test_get_risque_beneficiaire(self, partner_token):
        """GET /api/partenaires/beneficiaires/{id}/risque returns risk score"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/beneficiaires/{BENEFICIARY_ID}/risque?token={partner_token}"
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "score" in data, "Missing 'score'"
        assert "niveau" in data, "Missing 'niveau'"
        assert "facteurs" in data, "Missing 'facteurs'"
        
        assert isinstance(data["score"], int), "score should be int"
        assert data["niveau"] in ["critique", "eleve", "moyen", "faible"], f"Invalid niveau: {data['niveau']}"
        
        print(f"✓ Risk score: {data['score']}, niveau: {data['niveau']}, facteurs: {len(data['facteurs'])}")
    
    def test_get_risques_globaux(self, partner_token):
        """GET /api/partenaires/risques-globaux returns all risk scores"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/risques-globaux?token={partner_token}"
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Should return a list"
        
        if len(data) > 0:
            item = data[0]
            assert "beneficiary_id" in item, "Missing 'beneficiary_id'"
            assert "name" in item, "Missing 'name'"
            assert "risque" in item, "Missing 'risque'"
        
        print(f"✓ Risques globaux: {len(data)} beneficiaires with risk >= 20")


class TestBilanFinal:
    """Test Bilan de Fin de Parcours"""
    
    def test_generate_bilan_final(self, partner_token):
        """POST /api/partenaires/beneficiaires/{id}/bilan-final generates final assessment"""
        response = requests.post(
            f"{BASE_URL}/api/partenaires/beneficiaires/{BENEFICIARY_ID}/bilan-final?token={partner_token}",
            timeout=60
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify bilan structure
        assert "id" in data, "Missing 'id'"
        assert "content" in data, "Missing 'content'"
        assert "ai_generated" in data, "Missing 'ai_generated'"
        
        content = data["content"]
        assert "synthese_globale" in content, "Missing 'synthese_globale'"
        assert "competences_developpees" in content, "Missing 'competences_developpees'"
        assert "recommandations_suite" in content, "Missing 'recommandations_suite'"
        
        print(f"✓ Bilan final generated: ID={data['id'][:8]}...")
    
    def test_get_bilan_final(self, partner_token):
        """GET /api/partenaires/beneficiaires/{id}/bilan-final returns latest bilan"""
        response = requests.get(
            f"{BASE_URL}/api/partenaires/beneficiaires/{BENEFICIARY_ID}/bilan-final?token={partner_token}"
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        if data:
            assert "content" in data, "Missing 'content'"
            print(f"✓ Bilan final retrieved: ID={data['id'][:8]}...")
        else:
            print("✓ No bilan final exists yet (null response)")


class TestValidateCompteRendu:
    """Test compte rendu validation"""
    
    def test_validate_compte_rendu(self, partner_token):
        """PUT /api/partenaires/comptes-rendus/{report_id}/valider validates report"""
        # First get existing reports
        response = requests.get(
            f"{BASE_URL}/api/partenaires/beneficiaires/{BENEFICIARY_ID}/comptes-rendus?token={partner_token}"
        )
        assert response.status_code == 200
        reports = response.json()
        
        if not reports:
            pytest.skip("No reports to validate")
        
        # Find an unvalidated report
        unvalidated = [r for r in reports if not r.get("validated")]
        if not unvalidated:
            print("✓ All reports already validated")
            return
        
        report_id = unvalidated[0]["id"]
        
        # Validate it
        response = requests.put(
            f"{BASE_URL}/api/partenaires/comptes-rendus/{report_id}/valider?token={partner_token}"
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "message" in data, "Missing 'message'"
        
        print(f"✓ Compte rendu validated: {report_id[:8]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
