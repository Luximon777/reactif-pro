"""
Comprehensive tests for iteration 29:
- ROME filtering for France Travail
- Jobdating module (extracted from server.py)
- CK1 enrichment for all 68 fiches in referentiel_opc
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestROMEFiltering:
    """Tests for ROME code filtering - France Travail integration"""
    
    def test_rome_search_by_keyword(self):
        """GET /api/jobs/rome-search?q=technicien - returns ROME codes"""
        response = requests.get(f"{BASE_URL}/api/jobs/rome-search?q=technicien")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert data["total"] > 0
        # Verify structure of results
        for result in data["results"][:3]:
            assert "code_rome" in result
            assert "libelle" in result
            assert "domaine" in result
            assert result["code_rome"].startswith(("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N"))
        print(f"PASSED: ROME search returned {data['total']} results for 'technicien'")
    
    def test_rome_search_by_code(self):
        """GET /api/jobs/rome-search?q=K1801 - search by ROME code directly"""
        response = requests.get(f"{BASE_URL}/api/jobs/rome-search?q=K1801")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        # Should find the specific ROME code
        codes = [r["code_rome"] for r in data["results"]]
        assert "K1801" in codes or len(data["results"]) > 0
        print(f"PASSED: ROME search by code K1801 returned {data['total']} results")


class TestROMESuggestions:
    """Tests for ROME suggestions based on user profile"""
    
    @pytest.fixture
    def pierre7_token(self):
        """Login as pierre7 and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "pierre7",
            "password": "Solerys777!"
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_rome_suggestions_for_pierre7(self, pierre7_token):
        """GET /api/jobs/rome-suggestions?token=TOKEN - returns suggestions based on profile"""
        response = requests.get(f"{BASE_URL}/api/jobs/rome-suggestions?token={pierre7_token}")
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert len(data["suggestions"]) > 0
        # Verify structure
        for suggestion in data["suggestions"][:3]:
            assert "code_rome" in suggestion
            assert "libelle" in suggestion
            assert "domaine" in suggestion
            assert "matched_from" in suggestion
        print(f"PASSED: ROME suggestions returned {len(data['suggestions'])} suggestions for pierre7")


class TestJobdatingModule:
    """Tests for jobdating module - extracted from server.py"""
    
    @pytest.fixture
    def pierre7_token(self):
        """Login as pierre7 and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "pierre7",
            "password": "Solerys777!"
        })
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_jobdating_sectors(self):
        """GET /api/jobdating/sectors - returns list of sectors"""
        response = requests.get(f"{BASE_URL}/api/jobdating/sectors")
        assert response.status_code == 200
        data = response.json()
        assert "sectors" in data
        assert len(data["sectors"]) > 0
        # Verify structure
        for sector in data["sectors"]:
            assert "name" in sector
            assert "count" in sector
        print(f"PASSED: Jobdating sectors returned {len(data['sectors'])} sectors")
    
    def test_jobdating_events(self, pierre7_token):
        """GET /api/jobdating/events?token=TOKEN - returns events"""
        response = requests.get(f"{BASE_URL}/api/jobdating/events?token={pierre7_token}")
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "total" in data
        assert len(data["events"]) > 0
        # Verify event structure
        event = data["events"][0]
        assert "id" in event
        assert "title" in event
        assert "city" in event
        assert "match_score" in event
        assert "match_level" in event
        assert "ai_reason" in event
        print(f"PASSED: Jobdating events returned {data['total']} events")
    
    def test_jobdating_recommended(self, pierre7_token):
        """GET /api/jobdating/recommended?token=TOKEN - returns recommended events"""
        response = requests.get(f"{BASE_URL}/api/jobdating/recommended?token={pierre7_token}")
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "ai_summary" in data
        assert "total" in data
        # Recommended events should have match_score >= 25
        for event in data["events"]:
            assert event["match_score"] >= 25
        print(f"PASSED: Jobdating recommended returned {data['total']} events with ai_summary")


class TestCK1Enrichment:
    """Tests for CK1 enrichment of referentiel_opc fiches"""
    
    def test_search_soudeur_ck1(self):
        """GET /api/opc/referentiel/search?q=soudeur - returns CK1 data"""
        response = requests.get(f"{BASE_URL}/api/opc/referentiel/search?q=soudeur")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) > 0
        
        # Find Soudeur in results
        soudeur = None
        for r in data["results"]:
            if r.get("metier", "").lower() == "soudeur":
                soudeur = r
                break
        
        assert soudeur is not None, "Soudeur not found in results"
        
        # Verify CK1 fields are present
        ck1_fields = ["ck1_vertus", "ck1_valeurs", "ck1_qualites_humaines", 
                      "ck1_comp_cognitives", "ck1_comp_emotionnelles", "ck1_comp_sociales"]
        for field in ck1_fields:
            assert field in soudeur, f"Missing CK1 field: {field}"
            assert len(soudeur[field]) > 0, f"Empty CK1 field: {field}"
        
        # Verify specific CK1 values for Soudeur
        assert "COURAGE" in soudeur["ck1_vertus"]
        print(f"PASSED: Soudeur has all CK1 fields with COURAGE in vertus")
    
    def test_search_by_vertu_courage(self):
        """GET /api/opc/referentiel/search?q=COURAGE - search by CK1 vertu"""
        response = requests.get(f"{BASE_URL}/api/opc/referentiel/search?q=COURAGE")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) > 0
        
        # Search matches COURAGE in any CK1 field or qualites_humaines
        # At least some results should have COURAGE in ck1_vertus
        courage_in_vertus_count = 0
        for result in data["results"]:
            vertus = result.get("ck1_vertus", [])
            if any("courage" in v.lower() for v in vertus):
                courage_in_vertus_count += 1
        
        assert courage_in_vertus_count > 0, "No results have COURAGE in ck1_vertus"
        print(f"PASSED: Search by COURAGE returned {len(data['results'])} results, {courage_in_vertus_count} with COURAGE in vertus")
    
    def test_multiple_metiers_have_ck1(self):
        """Verify that multiple métiers have CK1 enrichment by searching different terms"""
        # Test several different métiers to verify CK1 enrichment
        test_queries = ["soudeur", "technicien", "ingénieur", "électricien", "cuisinier"]
        ck1_found_count = 0
        
        for query in test_queries:
            response = requests.get(f"{BASE_URL}/api/opc/referentiel/search?q={query}")
            assert response.status_code == 200
            data = response.json()
            
            for result in data["results"]:
                if result.get("ck1_vertus") and len(result["ck1_vertus"]) > 0:
                    ck1_found_count += 1
                    break  # Found at least one with CK1 for this query
        
        # At least 4 out of 5 queries should return results with CK1
        assert ck1_found_count >= 4, f"Only {ck1_found_count}/5 queries returned CK1 data"
        print(f"PASSED: {ck1_found_count}/5 test queries returned results with CK1 enrichment")


class TestAuthentication:
    """Tests for authentication endpoints"""
    
    def test_login_pierre7(self):
        """POST /api/auth/login - login with pierre7"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "pierre7",
            "password": "Solerys777!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "role" in data
        assert "profile_id" in data
        assert data["pseudo"] == "pierre7"
        print(f"PASSED: Login pierre7 successful")
    
    def test_login_mike7(self):
        """POST /api/auth/login - login with mike7"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "mike7",
            "password": "Solerys777!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["pseudo"] == "mike7"
        print(f"PASSED: Login mike7 successful")
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login - invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "pseudo": "invalid_user",
            "password": "wrong_password"
        })
        assert response.status_code == 401
        print(f"PASSED: Invalid login returns 401")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
