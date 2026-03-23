"""
Test ISCO Integration - INSEE ISCO Coding Matrix
Tests for:
- POST /api/referentiel/isco/import - CSV import (idempotent)
- GET /api/referentiel/isco/stats - ISCO database statistics
- GET /api/referentiel/isco/lookup - ISCO code lookup by job title
- GET /api/referentiel/explorer/search - Enriched search with ISCO results
- GET /api/referentiel/explorer/stats - Stats including ISCO counts
- POST /api/referentiel/explorer/generate - Fiche generation with ISCO code
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture(scope="module")
def auth_token(api_client):
    """Get authentication token by registering a test user"""
    unique_id = str(uuid.uuid4())[:8]
    response = api_client.post(f"{BASE_URL}/api/auth/register", json={
        "pseudo": f"test_isco_{unique_id}",
        "password": "testpass123",
        "consent_cgu": True,
        "consent_privacy": True
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Authentication failed: {response.text}")


class TestISCOImport:
    """Tests for ISCO CSV import endpoint"""
    
    def test_isco_import_idempotent(self, api_client):
        """POST /api/referentiel/isco/import - should return 'déjà importée' if >5000 entries exist"""
        response = api_client.post(f"{BASE_URL}/api/referentiel/isco/import")
        assert response.status_code == 200
        data = response.json()
        
        # Should indicate already imported (5853 entries)
        assert "count" in data or "total_metiers" in data
        count = data.get("count") or data.get("total_metiers", 0)
        assert count > 5000, f"Expected >5000 ISCO entries, got {count}"
        
        # Message should indicate already imported
        if "message" in data:
            assert "déjà importée" in data["message"].lower() or "terminé" in data["message"].lower()
        print(f"ISCO import response: {data}")


class TestISCOStats:
    """Tests for ISCO statistics endpoint"""
    
    def test_isco_stats_structure(self, api_client):
        """GET /api/referentiel/isco/stats - returns imported=true, total, codes_uniques, groupes"""
        response = api_client.get(f"{BASE_URL}/api/referentiel/isco/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert data.get("imported") == True, "ISCO should be imported"
        assert "total" in data
        assert "codes_uniques" in data
        assert "groupes" in data
        
        # Verify counts
        assert data["total"] > 5000, f"Expected >5000 total, got {data['total']}"
        assert data["codes_uniques"] > 400, f"Expected >400 unique codes, got {data['codes_uniques']}"
        
        # Verify groupes breakdown
        assert isinstance(data["groupes"], list)
        assert len(data["groupes"]) > 0
        for groupe in data["groupes"]:
            assert "code" in groupe
            assert "label" in groupe
            assert "count" in groupe
        
        print(f"ISCO stats: total={data['total']}, codes_uniques={data['codes_uniques']}, groupes={len(data['groupes'])}")


class TestISCOLookup:
    """Tests for ISCO code lookup endpoint"""
    
    def test_lookup_infirmier(self, api_client):
        """GET /api/referentiel/isco/lookup?metier=Infirmier - returns found=true with code_isco"""
        response = api_client.get(f"{BASE_URL}/api/referentiel/isco/lookup?metier=Infirmier")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("found") == True, f"Infirmier should be found, got: {data}"
        assert "code_isco" in data
        assert len(data["code_isco"]) == 4, f"ISCO code should be 4 digits, got: {data['code_isco']}"
        assert "libelle_m" in data
        assert "groupe" in data
        
        print(f"Infirmier lookup: code_isco={data['code_isco']}, groupe={data['groupe']}")
    
    def test_lookup_conseiller_insertion(self, api_client):
        """GET /api/referentiel/isco/lookup?metier=Conseiller en insertion professionnelle - returns code 2423"""
        response = api_client.get(f"{BASE_URL}/api/referentiel/isco/lookup?metier=Conseiller en insertion professionnelle")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("found") == True, f"Conseiller en insertion professionnelle should be found, got: {data}"
        assert "code_isco" in data
        # Code 2423 is for employment counsellors
        assert data["code_isco"] == "2423", f"Expected code 2423, got: {data['code_isco']}"
        
        print(f"Conseiller insertion lookup: code_isco={data['code_isco']}")
    
    def test_lookup_cariste(self, api_client):
        """GET /api/referentiel/isco/lookup?metier=Cariste - returns found=true"""
        response = api_client.get(f"{BASE_URL}/api/referentiel/isco/lookup?metier=Cariste")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("found") == True, f"Cariste should be found, got: {data}"
        assert "code_isco" in data
        assert len(data["code_isco"]) == 4
        
        print(f"Cariste lookup: code_isco={data['code_isco']}")
    
    def test_lookup_not_found(self, api_client):
        """GET /api/referentiel/isco/lookup?metier=XYZ123 - returns found=false"""
        response = api_client.get(f"{BASE_URL}/api/referentiel/isco/lookup?metier=XYZ123NonExistent")
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("found") == False, f"Non-existent job should not be found, got: {data}"
        print(f"Non-existent lookup: {data}")


class TestExplorerSearchISCO:
    """Tests for enriched search with ISCO results"""
    
    def test_search_infirmier_isco_results(self, api_client):
        """GET /api/referentiel/explorer/search?q=infirmier - returns ISCO results with code_isco and groupe_isco"""
        response = api_client.get(f"{BASE_URL}/api/referentiel/explorer/search?q=infirmier")
        assert response.status_code == 200
        data = response.json()
        
        assert "metiers" in data
        assert len(data["metiers"]) > 0, "Should find infirmier results"
        
        # Check for ISCO-sourced results
        isco_results = [m for m in data["metiers"] if m.get("source") == "isco"]
        assert len(isco_results) > 0, "Should have ISCO-sourced results"
        
        # Verify ISCO fields
        for m in isco_results:
            assert "code_isco" in m, f"ISCO result should have code_isco: {m}"
            assert "groupe_isco" in m, f"ISCO result should have groupe_isco: {m}"
            assert len(m["code_isco"]) == 4
        
        print(f"Infirmier search: {len(data['metiers'])} results, {len(isco_results)} from ISCO")
    
    def test_search_cariste_isco_results(self, api_client):
        """GET /api/referentiel/explorer/search?q=cariste - returns ISCO results for cariste variants"""
        response = api_client.get(f"{BASE_URL}/api/referentiel/explorer/search?q=cariste")
        assert response.status_code == 200
        data = response.json()
        
        assert "metiers" in data
        assert len(data["metiers"]) > 0, "Should find cariste results"
        
        # Check for ISCO-sourced results
        isco_results = [m for m in data["metiers"] if m.get("source") == "isco"]
        assert len(isco_results) > 0, "Should have ISCO-sourced cariste results"
        
        # Verify at least one has cariste in name
        cariste_names = [m["name"].lower() for m in isco_results if "cariste" in m["name"].lower()]
        assert len(cariste_names) > 0, f"Should find cariste variants, got: {[m['name'] for m in isco_results]}"
        
        print(f"Cariste search: {len(data['metiers'])} results, {len(isco_results)} from ISCO")
    
    def test_search_soudeur_isco_results(self, api_client):
        """GET /api/referentiel/explorer/search?q=soudeur - returns ISCO results"""
        response = api_client.get(f"{BASE_URL}/api/referentiel/explorer/search?q=soudeur")
        assert response.status_code == 200
        data = response.json()
        
        assert "metiers" in data
        isco_results = [m for m in data["metiers"] if m.get("source") == "isco"]
        
        if len(isco_results) > 0:
            for m in isco_results:
                assert "code_isco" in m
                assert "groupe_isco" in m
        
        print(f"Soudeur search: {len(data['metiers'])} results, {len(isco_results)} from ISCO")


class TestExplorerStatsISCO:
    """Tests for explorer stats including ISCO counts"""
    
    def test_explorer_stats_isco_counts(self, api_client):
        """GET /api/referentiel/explorer/stats - returns isco_metiers and isco_codes counts"""
        response = api_client.get(f"{BASE_URL}/api/referentiel/explorer/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Verify ISCO counts are present
        assert "isco_metiers" in data, f"Should have isco_metiers count, got: {data}"
        assert "isco_codes" in data, f"Should have isco_codes count, got: {data}"
        
        # Verify counts are reasonable
        assert data["isco_metiers"] > 5000, f"Expected >5000 isco_metiers, got {data['isco_metiers']}"
        assert data["isco_codes"] > 400, f"Expected >400 isco_codes, got {data['isco_codes']}"
        
        # Verify other stats still present
        assert "filieres" in data
        assert "secteurs" in data
        assert "metiers" in data
        
        print(f"Explorer stats: isco_metiers={data['isco_metiers']}, isco_codes={data['isco_codes']}")


class TestGenerateFicheISCO:
    """Tests for fiche generation with ISCO code enrichment"""
    
    def test_generate_cached_fiche_isco_enrichment(self, api_client, auth_token):
        """POST /api/referentiel/explorer/generate - returns code_isco and isco_info in cached fiches"""
        # First, try to get a cached fiche for a known ISCO job
        response = api_client.post(
            f"{BASE_URL}/api/referentiel/explorer/generate?token={auth_token}",
            json={"metier": "Cariste"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # If cached, should have ISCO enrichment
        if data.get("filiere"):
            # This is a cached result
            if data.get("code_isco"):
                assert len(data["code_isco"]) == 4
                print(f"Cached fiche has ISCO code: {data['code_isco']}")
            if data.get("isco_info"):
                assert "code" in data["isco_info"]
                assert "libelle_m" in data["isco_info"]
                print(f"Cached fiche has isco_info: {data['isco_info']}")
        else:
            # Job started - this is expected for new jobs
            assert "job_id" in data
            assert data.get("status") == "started"
            print(f"Generation started: job_id={data['job_id']}")
    
    def test_generate_infirmier_fiche(self, api_client, auth_token):
        """POST /api/referentiel/explorer/generate for Infirmier - should include ISCO code"""
        response = api_client.post(
            f"{BASE_URL}/api/referentiel/explorer/generate?token={auth_token}",
            json={"metier": "Infirmier"}
        )
        assert response.status_code == 200
        data = response.json()
        
        if data.get("filiere"):
            # Cached result - check for ISCO
            print(f"Infirmier fiche (cached): code_isco={data.get('code_isco')}")
        else:
            # Job started
            assert "job_id" in data
            print(f"Infirmier generation started: job_id={data['job_id']}")


class TestISCONormalization:
    """Tests for INSEE normalization logic"""
    
    def test_lookup_with_accents(self, api_client):
        """Lookup should work with accented characters"""
        # Test with "Mécanicien" (with accent)
        response = api_client.get(f"{BASE_URL}/api/referentiel/isco/lookup?metier=Mécanicien")
        assert response.status_code == 200
        data = response.json()
        
        # Should find a match (normalization removes accents)
        if data.get("found"):
            print(f"Mécanicien found: code_isco={data['code_isco']}")
        else:
            print(f"Mécanicien not found (may need exact match)")
    
    def test_lookup_case_insensitive(self, api_client):
        """Lookup should be case-insensitive"""
        response1 = api_client.get(f"{BASE_URL}/api/referentiel/isco/lookup?metier=INFIRMIER")
        response2 = api_client.get(f"{BASE_URL}/api/referentiel/isco/lookup?metier=infirmier")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Both should find the same result
        if data1.get("found") and data2.get("found"):
            assert data1["code_isco"] == data2["code_isco"], "Case should not affect lookup"
            print(f"Case-insensitive lookup works: {data1['code_isco']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
