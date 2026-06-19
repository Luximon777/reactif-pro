"""
Test OPC Référentiel Vivant with CK1 data integration
Tests the /api/opc/referentiel/search endpoint for CK1 enriched data
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestOpcReferentielCK1:
    """Tests for OPC Référentiel Vivant CK1 data"""
    
    def test_search_returns_results(self):
        """Test that search returns results for valid query"""
        response = requests.get(f"{BASE_URL}/api/opc/referentiel/search?q=maintenance")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert len(data["results"]) > 0
        print(f"✓ Search returned {len(data['results'])} results for 'maintenance'")
    
    def test_search_returns_ck1_fields(self):
        """Test that CK1 enriched fiches have CK1 fields"""
        response = requests.get(f"{BASE_URL}/api/opc/referentiel/search?q=maintenance")
        assert response.status_code == 200
        data = response.json()
        
        # Find a CK1 enriched result
        ck1_results = [r for r in data["results"] if r.get("ck1_vertus") and len(r.get("ck1_vertus", [])) > 0]
        assert len(ck1_results) > 0, "No CK1 enriched results found"
        
        ck1_result = ck1_results[0]
        print(f"✓ Found CK1 enriched fiche: {ck1_result.get('metier')}")
        
        # Check CK1 fields exist
        assert "ck1_vertus" in ck1_result
        assert "ck1_valeurs" in ck1_result
        assert "ck1_qualites_humaines" in ck1_result
        assert "ck1_comp_cognitives" in ck1_result
        assert "ck1_comp_emotionnelles" in ck1_result
        assert "ck1_comp_sociales" in ck1_result
        print(f"✓ All CK1 fields present in response")
    
    def test_search_ck1_vertus_content(self):
        """Test that ck1_vertus contains expected values"""
        response = requests.get(f"{BASE_URL}/api/opc/referentiel/search?q=maintenance")
        assert response.status_code == 200
        data = response.json()
        
        ck1_results = [r for r in data["results"] if r.get("ck1_vertus") and len(r.get("ck1_vertus", [])) > 0]
        assert len(ck1_results) > 0
        
        ck1_result = ck1_results[0]
        vertus = ck1_result.get("ck1_vertus", [])
        assert isinstance(vertus, list)
        assert len(vertus) > 0
        print(f"✓ ck1_vertus: {vertus}")
    
    def test_search_ck1_valeurs_content(self):
        """Test that ck1_valeurs contains expected values"""
        response = requests.get(f"{BASE_URL}/api/opc/referentiel/search?q=maintenance")
        assert response.status_code == 200
        data = response.json()
        
        ck1_results = [r for r in data["results"] if r.get("ck1_valeurs") and len(r.get("ck1_valeurs", [])) > 0]
        assert len(ck1_results) > 0
        
        ck1_result = ck1_results[0]
        valeurs = ck1_result.get("ck1_valeurs", [])
        assert isinstance(valeurs, list)
        assert len(valeurs) > 0
        print(f"✓ ck1_valeurs: {valeurs}")
    
    def test_search_by_ck1_term_connaissance(self):
        """Test search by CK1 term CONNAISSANCE"""
        response = requests.get(f"{BASE_URL}/api/opc/referentiel/search?q=CONNAISSANCE")
        assert response.status_code == 200
        data = response.json()
        
        # Should find fiches with CONNAISSANCE in ck1_vertus
        assert len(data["results"]) > 0, "No results for CONNAISSANCE search"
        print(f"✓ Search for 'CONNAISSANCE' returned {len(data['results'])} results")
    
    def test_search_by_ck1_term_adaptabilite(self):
        """Test search by CK1 term ADAPTABILITE"""
        response = requests.get(f"{BASE_URL}/api/opc/referentiel/search?q=ADAPTABILITE")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Search for 'ADAPTABILITE' returned {len(data['results'])} results")
    
    def test_search_industrielle(self):
        """Test search for 'industrielle' returns CK1 data"""
        response = requests.get(f"{BASE_URL}/api/opc/referentiel/search?q=industrielle")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["results"]) > 0, "No results for 'industrielle' search"
        print(f"✓ Search for 'industrielle' returned {len(data['results'])} results")
        
        # Check if any have CK1 data
        ck1_count = sum(1 for r in data["results"] if r.get("ck1_vertus") and len(r.get("ck1_vertus", [])) > 0)
        print(f"✓ {ck1_count} results have CK1 data")
    
    def test_non_ck1_fiches_have_empty_ck1_fields(self):
        """Test that non-CK1 fiches have empty CK1 fields"""
        response = requests.get(f"{BASE_URL}/api/opc/referentiel/search?q=maintenance")
        assert response.status_code == 200
        data = response.json()
        
        # Find a non-CK1 result
        non_ck1_results = [r for r in data["results"] if not r.get("ck1_vertus") or len(r.get("ck1_vertus", [])) == 0]
        
        if len(non_ck1_results) > 0:
            non_ck1_result = non_ck1_results[0]
            print(f"✓ Found non-CK1 fiche: {non_ck1_result.get('metier')}")
            # Should have empty arrays for CK1 fields
            assert non_ck1_result.get("ck1_vertus", []) == [] or non_ck1_result.get("ck1_vertus") is None
            print(f"✓ Non-CK1 fiche has empty ck1_vertus")
        else:
            print("✓ All results have CK1 data (no non-CK1 fiches to test)")
    
    def test_search_returns_standard_fields(self):
        """Test that search returns standard fields (metier, hard_skills, soft_skills, etc.)"""
        response = requests.get(f"{BASE_URL}/api/opc/referentiel/search?q=maintenance")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["results"]) > 0
        result = data["results"][0]
        
        # Check standard fields
        assert "metier" in result
        assert "hard_skills" in result
        assert "soft_skills" in result
        assert "qualites_humaines" in result
        assert "filiere" in result
        assert "secteur" in result
        print(f"✓ Standard fields present: metier, hard_skills, soft_skills, qualites_humaines, filiere, secteur")
    
    def test_search_empty_query(self):
        """Test that empty query returns empty results"""
        response = requests.get(f"{BASE_URL}/api/opc/referentiel/search?q=")
        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []
        assert data["total"] == 0
        print(f"✓ Empty query returns empty results")
    
    def test_search_short_query(self):
        """Test that short query (< 2 chars) returns empty results"""
        response = requests.get(f"{BASE_URL}/api/opc/referentiel/search?q=a")
        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []
        assert data["total"] == 0
        print(f"✓ Short query returns empty results")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
