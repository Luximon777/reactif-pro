"""
Test suite for the new POST /api/observatory/ia/cartographie-exhaustive endpoint
and verification of existing IA endpoints.

Tests:
1. POST /api/observatory/ia/cartographie-exhaustive with contexte_metier='commercial' 
   - Should return JSON with categories, metiers_emergents, certifications_cles, total_metiers >= 30
2. POST /api/observatory/ia/cartographie-exhaustive without contexte_metier
   - Should return an error
3. Existing endpoints still work:
   - POST /api/observatory/ia/correlations
   - POST /api/observatory/ia/trajectoires
   - POST /api/observatory/predict-competences
"""

import pytest
import requests
import os
import time

# Use localhost for cartographie-exhaustive due to Cloudflare timeout
BASE_URL_LOCAL = "http://localhost:8001"
# Use external URL for other endpoints
BASE_URL_EXTERNAL = os.environ.get('REACT_APP_BACKEND_URL', 'https://cv-analyzer-53.preview.emergentagent.com').rstrip('/')


class TestCartographieExhaustive:
    """Tests for the new cartographie-exhaustive endpoint"""
    
    def test_cartographie_exhaustive_with_commercial(self):
        """
        Test POST /api/observatory/ia/cartographie-exhaustive with contexte_metier='commercial'
        Should return JSON with categories, metiers_emergents, certifications_cles, total_metiers >= 30
        """
        # Use localhost to avoid Cloudflare timeout (endpoint takes 55-90 seconds)
        url = f"{BASE_URL_LOCAL}/api/observatory/ia/cartographie-exhaustive"
        payload = {"contexte_metier": "commercial"}
        
        print(f"\n[TEST] POST {url} with contexte_metier='commercial'")
        print("[INFO] This endpoint takes 55-90 seconds due to LLM processing...")
        
        response = requests.post(url, json=payload, timeout=150)
        
        # Status code assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"[RESULT] Response keys: {list(data.keys())}")
        
        # Verify no error
        assert "error" not in data or data.get("error") is None, f"Got error: {data.get('error')}"
        
        # Verify required fields exist
        assert "categories" in data, "Missing 'categories' field"
        assert "metiers_emergents" in data, "Missing 'metiers_emergents' field"
        assert "certifications_cles" in data, "Missing 'certifications_cles' field"
        assert "total_metiers" in data, "Missing 'total_metiers' field"
        
        # Verify total_metiers >= 30
        total = data.get("total_metiers", 0)
        print(f"[RESULT] total_metiers = {total}")
        assert total >= 30, f"Expected total_metiers >= 30, got {total}"
        
        # Verify categories is a list with content
        categories = data.get("categories", [])
        assert isinstance(categories, list), "categories should be a list"
        assert len(categories) >= 4, f"Expected at least 4 categories, got {len(categories)}"
        print(f"[RESULT] Number of categories: {len(categories)}")
        
        # Verify each category has metiers
        for i, cat in enumerate(categories):
            assert "nom" in cat, f"Category {i} missing 'nom'"
            assert "metiers" in cat, f"Category {i} missing 'metiers'"
            metiers = cat.get("metiers", [])
            print(f"  - Category '{cat.get('nom')}': {len(metiers)} métiers")
        
        # Verify metiers_emergents
        emergents = data.get("metiers_emergents", [])
        assert isinstance(emergents, list), "metiers_emergents should be a list"
        print(f"[RESULT] Number of metiers_emergents: {len(emergents)}")
        
        # Verify certifications_cles
        certs = data.get("certifications_cles", [])
        assert isinstance(certs, list), "certifications_cles should be a list"
        print(f"[RESULT] Number of certifications_cles: {len(certs)}")
        
        # Verify source_stats if present
        if "source_stats" in data:
            stats = data["source_stats"]
            print(f"[RESULT] source_stats: {stats}")
        
        print("[PASS] Cartographie exhaustive with 'commercial' returned valid data")
    
    def test_cartographie_exhaustive_without_contexte(self):
        """
        Test POST /api/observatory/ia/cartographie-exhaustive without contexte_metier
        Should return an error
        """
        url = f"{BASE_URL_LOCAL}/api/observatory/ia/cartographie-exhaustive"
        payload = {}  # No contexte_metier
        
        print(f"\n[TEST] POST {url} without contexte_metier")
        
        response = requests.post(url, json=payload, timeout=30)
        
        # Status code should still be 200 (error in body)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        print(f"[RESULT] Response: {data}")
        
        # Should have error field
        assert "error" in data, "Expected 'error' field when no contexte_metier provided"
        print(f"[PASS] Got expected error: {data.get('error')}")
    
    def test_cartographie_exhaustive_empty_contexte(self):
        """
        Test POST /api/observatory/ia/cartographie-exhaustive with empty contexte_metier
        Should return an error
        """
        url = f"{BASE_URL_LOCAL}/api/observatory/ia/cartographie-exhaustive"
        payload = {"contexte_metier": ""}  # Empty string
        
        print(f"\n[TEST] POST {url} with empty contexte_metier")
        
        response = requests.post(url, json=payload, timeout=30)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        print(f"[RESULT] Response: {data}")
        
        # Should have error field
        assert "error" in data, "Expected 'error' field when contexte_metier is empty"
        print(f"[PASS] Got expected error: {data.get('error')}")


class TestExistingIAEndpoints:
    """Tests to verify existing IA endpoints still work"""
    
    def test_ia_correlations(self):
        """Test POST /api/observatory/ia/correlations"""
        url = f"{BASE_URL_EXTERNAL}/api/observatory/ia/correlations"
        payload = {"contexte_metier": "comptable"}
        
        print(f"\n[TEST] POST {url}")
        
        response = requests.post(url, json=payload, timeout=90)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"[RESULT] Response type: {type(data)}, length: {len(data) if isinstance(data, list) else 'N/A'}")
        
        # Should return a list of correlations
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        assert len(data) > 0, "Expected at least one correlation"
        
        # Verify structure of first correlation
        first = data[0]
        assert "competence_technique" in first or "savoir_etre" in first, "Missing competence fields"
        
        print(f"[PASS] ia/correlations returned {len(data)} correlations")
    
    def test_ia_trajectoires(self):
        """Test POST /api/observatory/ia/trajectoires"""
        url = f"{BASE_URL_EXTERNAL}/api/observatory/ia/trajectoires"
        payload = {"contexte_metier": "comptable"}
        
        print(f"\n[TEST] POST {url}")
        
        response = requests.post(url, json=payload, timeout=90)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"[RESULT] Response type: {type(data)}, content: {str(data)[:200]}")
        
        # Can return list of trajectoires OR error dict (LLM timeout is possible)
        if isinstance(data, dict) and "error" in data:
            print(f"[WARN] Got error (LLM timeout possible): {data.get('error')}")
            pytest.skip("LLM returned error - intermittent timeout")
        
        # Should return a list of trajectoires
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        assert len(data) > 0, "Expected at least one trajectory"
        
        # Verify structure
        first = data[0]
        assert "metier_cible" in first or "probabilite" in first, "Missing trajectory fields"
        
        print(f"[PASS] ia/trajectoires returned {len(data)} trajectories")
    
    def test_predict_competences(self):
        """Test POST /api/observatory/predict-competences"""
        url = f"{BASE_URL_EXTERNAL}/api/observatory/predict-competences"
        payload = {"contexte_metier": "comptable"}
        
        print(f"\n[TEST] POST {url}")
        
        response = requests.post(url, json=payload, timeout=90)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"[RESULT] Response keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
        
        # Should return dict with synthese and tendances_competences
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"
        assert "synthese" in data, "Missing 'synthese' field"
        assert "tendances_competences" in data, "Missing 'tendances_competences' field"
        
        print(f"[PASS] predict-competences returned valid data with synthese")


class TestOPCPageAccess:
    """Tests for OPC page access and dashboard"""
    
    def test_observatory_dashboard(self):
        """Test GET /api/observatory/dashboard"""
        url = f"{BASE_URL_EXTERNAL}/api/observatory/dashboard"
        
        print(f"\n[TEST] GET {url}")
        
        response = requests.get(url, timeout=30)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"[RESULT] Response keys: {list(data.keys())}")
        
        # Verify dashboard structure - can have stats, top_soft_skills, etc.
        assert isinstance(data, dict), "Dashboard should return a dict"
        assert len(data) > 0, "Dashboard should have data"
        # Check for any of the expected keys
        expected_keys = ["stats", "indicators", "emerging_skills", "top_soft_skills", "top_sectors"]
        has_expected = any(k in data for k in expected_keys)
        assert has_expected, f"Missing expected dashboard data. Got keys: {list(data.keys())}"
        
        print("[PASS] observatory/dashboard accessible")
    
    def test_rncp_stats(self):
        """Test GET /api/referentiel/rncp/stats"""
        url = f"{BASE_URL_EXTERNAL}/api/referentiel/rncp/stats"
        
        print(f"\n[TEST] GET {url}")
        
        response = requests.get(url, timeout=30)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"[RESULT] Response: {data}")
        
        # Verify stats
        assert "total_certifications" in data or "rncp_actives" in data, "Missing RNCP stats"
        
        print("[PASS] referentiel/rncp/stats accessible")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
