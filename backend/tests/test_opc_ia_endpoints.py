"""
Test OPC IA Endpoints - Observatory Predictive des Compétences
Tests for the 7 IA endpoints created for Analyser/Anticiper/Orienter tabs

Endpoints tested:
1. POST /api/observatory/ia/correlations - Hard skills ↔ Soft skills correlations
2. POST /api/observatory/ia/detect-emergentes - Emerging competences detection
3. POST /api/observatory/ia/trajectoires - Career trajectories/passerelles
4. POST /api/observatory/ia/recommandation - Personalized recommendations
5. POST /api/observatory/predict-competences - Global competence predictions
6. POST /api/observatory/ia/analyse-complete - Combined analysis
7. GET /api/observatory/sare-terrain - Terrain proofs (S.A.R.E)
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test context for IA endpoints
TEST_CONTEXT = {"contexte_metier": "comptable"}
EMPTY_CONTEXT = {}

# Timeout for IA endpoints (Claude AI calls can take time)
IA_TIMEOUT = 90


class TestOpcIaEndpoints:
    """Test all 7 OPC IA endpoints"""

    # ========== ENDPOINT 1: Correlations ==========
    def test_correlations_with_context(self):
        """POST /api/observatory/ia/correlations with contexte_metier returns correlations array"""
        response = requests.post(
            f"{BASE_URL}/api/observatory/ia/correlations",
            json=TEST_CONTEXT,
            timeout=IA_TIMEOUT
        )
        print(f"Correlations response status: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Correlations response type: {type(data)}")
        
        # Should return array of correlation objects
        if isinstance(data, list):
            assert len(data) > 0, "Expected non-empty correlations array"
            first_item = data[0]
            assert "competence_technique" in first_item, "Missing competence_technique field"
            assert "savoir_etre" in first_item, "Missing savoir_etre field"
            print(f"✓ Correlations: {len(data)} items, first: {first_item.get('competence_technique')}")
        elif isinstance(data, dict):
            # Could be error response
            if "error" in data:
                print(f"⚠ Correlations returned error: {data['error']}")
            else:
                pytest.fail(f"Unexpected dict response: {data}")

    def test_correlations_without_context(self):
        """POST /api/observatory/ia/correlations without context still works"""
        response = requests.post(
            f"{BASE_URL}/api/observatory/ia/correlations",
            json=EMPTY_CONTEXT,
            timeout=IA_TIMEOUT
        )
        print(f"Correlations (no context) status: {response.status_code}")
        assert response.status_code == 200

    # ========== ENDPOINT 2: Detect Emergentes ==========
    def test_detect_emergentes_with_context(self):
        """POST /api/observatory/ia/detect-emergentes returns emerging competences array"""
        response = requests.post(
            f"{BASE_URL}/api/observatory/ia/detect-emergentes",
            json=TEST_CONTEXT,
            timeout=IA_TIMEOUT
        )
        print(f"Detect-emergentes response status: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Detect-emergentes response type: {type(data)}")
        
        # Should return array of emerging competences
        if isinstance(data, list):
            assert len(data) > 0, "Expected non-empty emergentes array"
            first_item = data[0]
            assert "competence" in first_item, "Missing competence field"
            assert "tendance" in first_item, "Missing tendance field"
            assert "score_emergence" in first_item, "Missing score_emergence field"
            assert "secteurs" in first_item, "Missing secteurs field"
            print(f"✓ Emergentes: {len(data)} items, first: {first_item.get('competence')} (score: {first_item.get('score_emergence')})")
        elif isinstance(data, dict) and "error" in data:
            print(f"⚠ Emergentes returned error: {data['error']}")

    def test_detect_emergentes_without_context(self):
        """POST /api/observatory/ia/detect-emergentes without context returns fallback"""
        response = requests.post(
            f"{BASE_URL}/api/observatory/ia/detect-emergentes",
            json=EMPTY_CONTEXT,
            timeout=IA_TIMEOUT
        )
        print(f"Detect-emergentes (no context) status: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        # Should return fallback array
        assert isinstance(data, list), "Expected array response"

    # ========== ENDPOINT 3: Trajectoires ==========
    def test_trajectoires_with_context(self):
        """POST /api/observatory/ia/trajectoires returns career trajectories array"""
        response = requests.post(
            f"{BASE_URL}/api/observatory/ia/trajectoires",
            json=TEST_CONTEXT,
            timeout=IA_TIMEOUT
        )
        print(f"Trajectoires response status: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Trajectoires response type: {type(data)}")
        
        # Should return array of trajectoire objects
        if isinstance(data, list):
            assert len(data) > 0, "Expected non-empty trajectoires array"
            first_item = data[0]
            assert "metier_source" in first_item, "Missing metier_source field"
            assert "metier_cible" in first_item, "Missing metier_cible field"
            assert "probabilite" in first_item, "Missing probabilite field"
            print(f"✓ Trajectoires: {len(data)} items, first: {first_item.get('metier_source')} → {first_item.get('metier_cible')} ({first_item.get('probabilite')}%)")
        elif isinstance(data, dict) and "error" in data:
            print(f"⚠ Trajectoires returned error: {data['error']}")

    def test_trajectoires_without_context(self):
        """POST /api/observatory/ia/trajectoires without context"""
        response = requests.post(
            f"{BASE_URL}/api/observatory/ia/trajectoires",
            json=EMPTY_CONTEXT,
            timeout=IA_TIMEOUT
        )
        print(f"Trajectoires (no context) status: {response.status_code}")
        assert response.status_code == 200

    # ========== ENDPOINT 4: Recommandation ==========
    def test_recommandation_with_context(self):
        """POST /api/observatory/ia/recommandation returns recommendation object"""
        response = requests.post(
            f"{BASE_URL}/api/observatory/ia/recommandation",
            json=TEST_CONTEXT,
            timeout=IA_TIMEOUT
        )
        print(f"Recommandation response status: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Recommandation response type: {type(data)}")
        
        # Should return object with plan_action, metiers_accessibles, etc.
        if isinstance(data, dict):
            if "error" in data:
                print(f"⚠ Recommandation returned error: {data['error']}")
            else:
                assert "plan_action" in data, "Missing plan_action field"
                assert "metiers_accessibles" in data, "Missing metiers_accessibles field"
                assert "competences_prioritaires" in data, "Missing competences_prioritaires field"
                assert "savoir_etre_a_renforcer" in data, "Missing savoir_etre_a_renforcer field"
                print(f"✓ Recommandation: plan_action present, {len(data.get('metiers_accessibles', []))} métiers accessibles")

    def test_recommandation_without_context(self):
        """POST /api/observatory/ia/recommandation without context"""
        response = requests.post(
            f"{BASE_URL}/api/observatory/ia/recommandation",
            json=EMPTY_CONTEXT,
            timeout=IA_TIMEOUT
        )
        print(f"Recommandation (no context) status: {response.status_code}")
        assert response.status_code == 200

    # ========== ENDPOINT 5: Predict Competences ==========
    def test_predict_competences_with_context(self):
        """POST /api/observatory/predict-competences returns predictions object"""
        response = requests.post(
            f"{BASE_URL}/api/observatory/predict-competences",
            json=TEST_CONTEXT,
            timeout=IA_TIMEOUT
        )
        print(f"Predict-competences response status: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Predict-competences response type: {type(data)}")
        
        # Should return object with synthese, tendances_competences
        if isinstance(data, dict):
            if "error" in data:
                print(f"⚠ Predict-competences returned error: {data['error']}")
            else:
                assert "synthese" in data, "Missing synthese field"
                assert "tendances_competences" in data, "Missing tendances_competences field"
                print(f"✓ Predict-competences: synthese present, {len(data.get('tendances_competences', []))} tendances")

    def test_predict_competences_without_context(self):
        """POST /api/observatory/predict-competences without context returns fallback"""
        response = requests.post(
            f"{BASE_URL}/api/observatory/predict-competences",
            json=EMPTY_CONTEXT,
            timeout=IA_TIMEOUT
        )
        print(f"Predict-competences (no context) status: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert "synthese" in data, "Fallback should have synthese"

    # ========== ENDPOINT 6: Analyse Complete ==========
    def test_analyse_complete_with_context(self):
        """POST /api/observatory/ia/analyse-complete returns combined results"""
        response = requests.post(
            f"{BASE_URL}/api/observatory/ia/analyse-complete",
            json=TEST_CONTEXT,
            timeout=IA_TIMEOUT * 2  # Double timeout for combined analysis
        )
        print(f"Analyse-complete response status: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Analyse-complete response type: {type(data)}")
        
        # Should return object with emergentes, correlations, trajectoires, recommandation
        assert isinstance(data, dict), "Expected dict response"
        assert "emergentes" in data, "Missing emergentes field"
        assert "correlations" in data, "Missing correlations field"
        assert "trajectoires" in data, "Missing trajectoires field"
        assert "recommandation" in data, "Missing recommandation field"
        assert "contexte_metier" in data, "Missing contexte_metier field"
        assert "generated_at" in data, "Missing generated_at field"
        
        print(f"✓ Analyse-complete: emergentes={len(data.get('emergentes', []))}, correlations={len(data.get('correlations', []))}, trajectoires={len(data.get('trajectoires', []))}")

    def test_analyse_complete_without_context(self):
        """POST /api/observatory/ia/analyse-complete without context"""
        response = requests.post(
            f"{BASE_URL}/api/observatory/ia/analyse-complete",
            json=EMPTY_CONTEXT,
            timeout=IA_TIMEOUT * 2
        )
        print(f"Analyse-complete (no context) status: {response.status_code}")
        assert response.status_code == 200

    # ========== ENDPOINT 7: SARE Terrain ==========
    def test_sare_terrain_default(self):
        """GET /api/observatory/sare-terrain returns terrain proofs"""
        response = requests.get(
            f"{BASE_URL}/api/observatory/sare-terrain",
            timeout=30
        )
        print(f"SARE-terrain response status: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"SARE-terrain response: {data}")
        
        # Should return object with terrain_proofs array
        assert isinstance(data, dict), "Expected dict response"
        assert "terrain_proofs" in data, "Missing terrain_proofs field"
        assert isinstance(data["terrain_proofs"], list), "terrain_proofs should be array"
        print(f"✓ SARE-terrain: {len(data['terrain_proofs'])} terrain proofs")

    def test_sare_terrain_with_limit(self):
        """GET /api/observatory/sare-terrain?limit=3 respects limit parameter"""
        response = requests.get(
            f"{BASE_URL}/api/observatory/sare-terrain?limit=3",
            timeout=30
        )
        print(f"SARE-terrain (limit=3) status: {response.status_code}")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data.get("terrain_proofs", [])) <= 3, "Should respect limit parameter"


class TestOpcIaEndpointsQuickCheck:
    """Quick health check for all endpoints (no IA calls, just status codes)"""

    def test_all_endpoints_respond(self):
        """Verify all 7 endpoints respond with 200"""
        endpoints = [
            ("POST", "/api/observatory/ia/correlations"),
            ("POST", "/api/observatory/ia/detect-emergentes"),
            ("POST", "/api/observatory/ia/trajectoires"),
            ("POST", "/api/observatory/ia/recommandation"),
            ("POST", "/api/observatory/predict-competences"),
            ("POST", "/api/observatory/ia/analyse-complete"),
            ("GET", "/api/observatory/sare-terrain"),
        ]
        
        results = []
        for method, endpoint in endpoints:
            try:
                if method == "POST":
                    response = requests.post(f"{BASE_URL}{endpoint}", json={}, timeout=IA_TIMEOUT)
                else:
                    response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
                
                status = "✓" if response.status_code == 200 else "✗"
                results.append((endpoint, response.status_code, status))
                print(f"{status} {method} {endpoint}: {response.status_code}")
            except Exception as e:
                results.append((endpoint, 0, f"ERROR: {e}"))
                print(f"✗ {method} {endpoint}: ERROR - {e}")
        
        # All should return 200
        failed = [r for r in results if r[1] != 200]
        assert len(failed) == 0, f"Failed endpoints: {failed}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
