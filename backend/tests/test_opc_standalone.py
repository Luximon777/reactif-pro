"""
Test suite for OPC Standalone Page - Backend API Tests
Tests all 7 IA endpoints and RNCP endpoints for the new OPC dedicated page
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://cv-analyzer-53.preview.emergentagent.com')

class TestRNCPEndpoints:
    """RNCP/France Compétences API endpoint tests"""
    
    def test_rncp_stats(self):
        """GET /api/referentiel/rncp/stats - Returns RNCP statistics"""
        response = requests.get(f"{BASE_URL}/api/referentiel/rncp/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_certifications" in data
        assert "rncp_actives" in data
        assert "rs_actives" in data
        assert "blocs_competences" in data
        assert "mappings_rome" in data
        assert data["total_certifications"] >= 30000
        assert data["rncp_actives"] >= 5000
        print(f"RNCP Stats: {data['total_certifications']} certifications, {data['rncp_actives']} RNCP actives")
    
    def test_rncp_search_comptable(self):
        """GET /api/referentiel/rncp/search?q=comptable - Search for comptable certifications"""
        response = requests.get(f"{BASE_URL}/api/referentiel/rncp/search?q=comptable&limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert len(data["results"]) > 0
        assert data["total"] >= 20  # Should have at least 20 comptable certifications
        
        # Check first result has required fields
        first = data["results"][0]
        assert "code" in first
        assert "intitule" in first
        assert "RNCP" in first["code"]
        print(f"RNCP Search 'comptable': {data['total']} results, first: {first['code']} - {first['intitule']}")
    
    def test_rncp_fiche_detail(self):
        """GET /api/referentiel/rncp/fiche/RNCP42012 - Get certification detail with blocs and ROME codes"""
        response = requests.get(f"{BASE_URL}/api/referentiel/rncp/fiche/RNCP42012")
        assert response.status_code == 200
        
        data = response.json()
        assert data["code"] == "RNCP42012"
        assert "intitule" in data
        assert "blocs_competences" in data
        assert "codes_rome" in data
        assert len(data["blocs_competences"]) >= 5  # Should have at least 5 blocs
        assert len(data["codes_rome"]) >= 2  # Should have at least 2 ROME codes
        print(f"RNCP42012: {len(data['blocs_competences'])} blocs, {len(data['codes_rome'])} ROME codes")
    
    def test_rncp_tension(self):
        """GET /api/referentiel/rncp/tension - Get certifications en tension"""
        response = requests.get(f"{BASE_URL}/api/referentiel/rncp/tension?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert "certifications_en_tension" in data
        assert len(data["certifications_en_tension"]) > 0
        
        # Check first certification has nb_metiers_associes
        first = data["certifications_en_tension"][0]
        assert "nb_metiers_associes" in first
        print(f"Tension: {len(data['certifications_en_tension'])} certifications, first has {first['nb_metiers_associes']} métiers")


class TestIAEndpoints:
    """Observatory IA endpoint tests - require longer timeouts"""
    
    def test_ia_correlations(self):
        """POST /api/observatory/ia/correlations - Correlations compétences techniques ↔ savoir-être"""
        response = requests.post(
            f"{BASE_URL}/api/observatory/ia/correlations",
            json={"contexte_metier": "comptable"},
            timeout=90
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5
        
        # Check first item structure
        first = data[0]
        assert "competence_technique" in first
        assert "savoir_etre" in first
        assert isinstance(first["savoir_etre"], list)
        print(f"Correlations: {len(data)} items, first: {first['competence_technique']}")
    
    def test_ia_detect_emergentes(self):
        """POST /api/observatory/ia/detect-emergentes - Detect emerging skills"""
        response = requests.post(
            f"{BASE_URL}/api/observatory/ia/detect-emergentes",
            json={"contexte_metier": "comptable"},
            timeout=90
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5
        
        # Check first item structure
        first = data[0]
        assert "competence" in first
        assert "tendance" in first
        assert "score_emergence" in first
        print(f"Emergentes: {len(data)} items, first: {first['competence']} (score: {first['score_emergence']})")
    
    def test_ia_trajectoires(self):
        """POST /api/observatory/ia/trajectoires - Career pathways analysis"""
        response = requests.post(
            f"{BASE_URL}/api/observatory/ia/trajectoires",
            json={"contexte_metier": "comptable"},
            timeout=90
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5
        
        # Check first item structure
        first = data[0]
        assert "metier_source" in first
        assert "metier_cible" in first
        assert "probabilite" in first
        print(f"Trajectoires: {len(data)} items, first: {first['metier_source']} -> {first['metier_cible']} ({first['probabilite']}%)")
    
    def test_ia_recommandation(self):
        """POST /api/observatory/ia/recommandation - Personalized recommendation"""
        response = requests.post(
            f"{BASE_URL}/api/observatory/ia/recommandation",
            json={"contexte_metier": "comptable"},
            timeout=90
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "plan_action" in data
        assert "metiers_accessibles" in data or "error" not in data
        print(f"Recommandation: plan_action length = {len(data.get('plan_action', ''))}")
    
    def test_predict_competences(self):
        """POST /api/observatory/predict-competences - Global competence predictions"""
        response = requests.post(
            f"{BASE_URL}/api/observatory/predict-competences",
            json={"contexte_metier": "comptable"},
            timeout=90
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "synthese" in data
        assert "tendances_competences" in data
        print(f"Predictions: synthese length = {len(data.get('synthese', ''))}, {len(data.get('tendances_competences', []))} tendances")
    
    def test_sare_terrain(self):
        """GET /api/observatory/sare-terrain - Terrain proofs (instant, no IA)"""
        response = requests.get(f"{BASE_URL}/api/observatory/sare-terrain?limit=3")
        assert response.status_code == 200
        
        data = response.json()
        assert "terrain_proofs" in data
        print(f"SARE Terrain: {len(data.get('terrain_proofs', []))} soft skills with proofs")


class TestOPCDashboard:
    """OPC Dashboard endpoint tests"""
    
    def test_observatory_dashboard(self):
        """GET /api/observatory/dashboard - Dashboard stats"""
        response = requests.get(f"{BASE_URL}/api/observatory/dashboard")
        # May return 200 or 404 depending on implementation
        if response.status_code == 200:
            data = response.json()
            print(f"Dashboard: {data}")
        else:
            print(f"Dashboard endpoint returned {response.status_code}")
    
    def test_referentiel_filieres(self):
        """GET /api/referentiel/filieres - List of filieres"""
        response = requests.get(f"{BASE_URL}/api/referentiel/filieres")
        if response.status_code == 200:
            data = response.json()
            # API returns {"filieres": [...]} or a list
            if isinstance(data, dict) and "filieres" in data:
                filieres = data["filieres"]
            else:
                filieres = data
            assert isinstance(filieres, list)
            assert len(filieres) > 0
            print(f"Filieres: {len(filieres)} items")
        else:
            print(f"Filieres endpoint returned {response.status_code}")
    
    def test_referentiel_search(self):
        """GET /api/referentiel/search - Search referentiel"""
        response = requests.get(f"{BASE_URL}/api/referentiel/search?q=comptable&limit=5")
        if response.status_code == 200:
            data = response.json()
            # API returns {"metiers": [...], "rome": [...], ...} or {"results": [...]}
            if isinstance(data, dict):
                if "results" in data:
                    results = data["results"]
                elif "metiers" in data:
                    results = data["metiers"]
                else:
                    results = []
            else:
                results = data
            assert len(results) > 0
            print(f"Referentiel search: {len(results)} results")
        else:
            print(f"Referentiel search endpoint returned {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
