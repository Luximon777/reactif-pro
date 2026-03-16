"""
Test suite for Explorateur des Filières Professionnelles API endpoints
Tests the hierarchical navigation: Filière → Secteur → Métier → Compétences
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

class TestExplorerEndpoints:
    """Tests for /api/referentiel/explorer/* endpoints"""

    # ============ GET /api/referentiel/explorer - List all filières ============
    
    def test_get_all_filieres_returns_200(self):
        """GET /api/referentiel/explorer should return 200 and list of filieres"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer")
        assert response.status_code == 200
        data = response.json()
        assert "filieres" in data
        assert "total_filieres" in data
        print(f"✓ GET /api/referentiel/explorer returns {data['total_filieres']} filieres")
    
    def test_get_filieres_has_20_filieres(self):
        """Should return 20 filieres as per ODS import"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer")
        data = response.json()
        assert data["total_filieres"] == 20, f"Expected 20 filieres, got {data['total_filieres']}"
        assert len(data["filieres"]) == 20
        print("✓ Exactly 20 filieres present")
    
    def test_filieres_have_secteurs(self):
        """Each filiere should have secteurs array with name and metiers_count"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer")
        data = response.json()
        for filiere in data["filieres"]:
            assert "id" in filiere, f"Filiere missing id: {filiere}"
            assert "name" in filiere, f"Filiere missing name: {filiere}"
            assert "secteurs" in filiere, f"Filiere missing secteurs: {filiere}"
            assert isinstance(filiere["secteurs"], list)
            for secteur in filiere["secteurs"]:
                assert "name" in secteur
                assert "metiers_count" in secteur
        print("✓ All filieres have proper structure with secteurs")
    
    def test_filiere_industrielle_exists(self):
        """Filière Industrielle should exist with expected secteurs"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer")
        data = response.json()
        industrielle = next((f for f in data["filieres"] if "Industrielle" in f["name"]), None)
        assert industrielle is not None, "Filière Industrielle not found"
        secteur_names = [s["name"] for s in industrielle["secteurs"]]
        assert "Mécanique" in secteur_names, f"Mécanique not in {secteur_names}"
        print(f"✓ Filière Industrielle found with secteurs: {secteur_names[:3]}...")

    # ============ GET /api/referentiel/explorer/stats ============
    
    def test_stats_returns_200(self):
        """GET /api/referentiel/explorer/stats should return 200"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/stats")
        assert response.status_code == 200
        print("✓ GET /api/referentiel/explorer/stats returns 200")
    
    def test_stats_correct_counts(self):
        """Stats should return correct counts for filieres, secteurs, metiers"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/stats")
        data = response.json()
        
        assert "filieres" in data
        assert "secteurs" in data
        assert "metiers" in data
        assert "savoirs_faire" in data
        assert "savoirs_etre" in data
        
        assert data["filieres"] == 20, f"Expected 20 filieres, got {data['filieres']}"
        assert data["secteurs"] == 85, f"Expected 85 secteurs, got {data['secteurs']}"
        assert data["metiers"] == 45, f"Expected 45 metiers, got {data['metiers']}"
        assert data["savoirs_faire"] > 0, "Should have savoirs_faire"
        assert data["savoirs_etre"] > 0, "Should have savoirs_etre"
        
        print(f"✓ Stats correct: {data['filieres']} filieres, {data['secteurs']} secteurs, {data['metiers']} metiers")
        print(f"  {data['savoirs_faire']} savoirs_faire, {data['savoirs_etre']} savoirs_etre")

    # ============ GET /api/referentiel/explorer/secteur/{name} ============
    
    def test_get_secteur_mecanique(self):
        """GET /api/referentiel/explorer/secteur/Mécanique should return metiers"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/secteur/Mécanique")
        assert response.status_code == 200
        data = response.json()
        
        assert "filiere" in data
        assert "secteur" in data
        assert "metiers" in data
        assert data["secteur"] == "Mécanique"
        assert len(data["metiers"]) > 0, "Mécanique should have metiers"
        
        print(f"✓ Secteur Mécanique has {len(data['metiers'])} metiers in {data['filiere']}")
    
    def test_secteur_metiers_have_savoirs(self):
        """Metiers in secteur should have savoirs_faire and savoirs_etre"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/secteur/Mécanique")
        data = response.json()
        
        for metier in data["metiers"]:
            assert "name" in metier
            assert "savoirs_faire" in metier or "savoirs_etre" in metier, \
                f"Metier {metier['name']} should have some savoirs"
        
        # Check first metier has detailed savoirs
        first_metier = data["metiers"][0]
        if "savoirs_faire" in first_metier:
            for sf in first_metier["savoirs_faire"]:
                assert "name" in sf, "Savoir-faire should have name"
        
        print("✓ Metiers in Mécanique have savoirs")
    
    def test_secteur_not_found(self):
        """GET /api/referentiel/explorer/secteur/Unknown should return 404"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/secteur/SecteurInexistant")
        assert response.status_code == 404
        print("✓ Unknown secteur returns 404")

    # ============ GET /api/referentiel/explorer/metier/{name} ============
    
    def test_get_metier_ingenieur_mecanique(self):
        """GET /api/referentiel/explorer/metier/ingénieur en mécanique should return full detail"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/metier/ingénieur en mécanique")
        assert response.status_code == 200
        data = response.json()
        
        assert "filiere" in data
        assert "secteur" in data
        assert "metier" in data
        
        metier = data["metier"]
        assert metier["name"].lower() == "ingénieur en mécanique"
        assert "mission" in metier
        assert "savoirs_faire" in metier
        assert "savoirs_etre" in metier
        
        print(f"✓ Métier 'ingénieur en mécanique' found in {data['filiere']}/{data['secteur']}")
    
    def test_metier_has_savoir_faire_with_capacite_technique(self):
        """Metier savoirs_faire should include capacite_technique"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/metier/ingénieur en mécanique")
        data = response.json()
        metier = data["metier"]
        
        assert len(metier["savoirs_faire"]) > 0, "Should have savoirs_faire"
        
        # Check structure of savoir_faire
        sf = metier["savoirs_faire"][0]
        assert "name" in sf
        assert "capacite_technique" in sf, "Savoir-faire should have capacite_technique"
        
        print(f"✓ Metier has {len(metier['savoirs_faire'])} savoirs_faire with capacite_technique")
    
    def test_metier_savoir_etre_has_chain(self):
        """Savoir-etre should have chain: qualites_humaines → valeurs → vertus"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/metier/ingénieur en mécanique")
        data = response.json()
        metier = data["metier"]
        
        assert len(metier["savoirs_etre"]) > 0, "Should have savoirs_etre"
        
        # Check at least one savoir_etre has the full chain
        found_chain = False
        for se in metier["savoirs_etre"]:
            assert "name" in se
            assert "capacite_professionnelle" in se, f"Savoir-etre {se['name']} missing capacite_professionnelle"
            
            if "qualites_humaines" in se and len(se["qualites_humaines"]) > 0:
                found_chain = True
                assert "valeurs" in se, f"Savoir-etre {se['name']} has qualites but missing valeurs"
                assert "vertus" in se, f"Savoir-etre {se['name']} has qualites but missing vertus"
                print(f"  Chain found for '{se['name']}': {se['qualites_humaines']} → {se['valeurs']} → {se['vertus']}")
        
        assert found_chain, "At least one savoir-etre should have the full chain"
        print(f"✓ Metier has {len(metier['savoirs_etre'])} savoirs_etre with qualités→valeurs→vertus chain")
    
    def test_metier_not_found(self):
        """GET /api/referentiel/explorer/metier/Unknown should return 404"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/metier/MetierInexistant")
        assert response.status_code == 404
        print("✓ Unknown metier returns 404")

    # ============ GET /api/referentiel/explorer/search ============
    
    def test_search_leadership_returns_results(self):
        """Search for 'leadership' should return savoir_faire and savoir_etre results"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/search?q=leadership")
        assert response.status_code == 200
        data = response.json()
        
        assert "filieres" in data
        assert "secteurs" in data
        assert "metiers" in data
        assert "savoirs_faire" in data
        assert "savoirs_etre" in data
        
        # Leadership should appear in savoirs
        total_results = (
            len(data["filieres"]) + len(data["secteurs"]) + 
            len(data["metiers"]) + len(data["savoirs_faire"]) + len(data["savoirs_etre"])
        )
        assert total_results > 0, "Search 'leadership' should return some results"
        
        print(f"✓ Search 'leadership' returned {total_results} results")
        print(f"  savoirs_faire: {len(data['savoirs_faire'])}, savoirs_etre: {len(data['savoirs_etre'])}")
    
    def test_search_mecanique_returns_filiere_and_secteur(self):
        """Search for 'mécanique' should return relevant results"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/search?q=mécanique")
        assert response.status_code == 200
        data = response.json()
        
        # Should find Mécanique as secteur or metier
        has_results = (
            len(data["secteurs"]) > 0 or 
            len(data["metiers"]) > 0
        )
        assert has_results, "Search 'mécanique' should find secteur or metier"
        
        print(f"✓ Search 'mécanique' found: secteurs={len(data['secteurs'])}, metiers={len(data['metiers'])}")
    
    def test_search_empty_query(self):
        """Search with short query should return empty or limited results"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/search?q=x")
        assert response.status_code == 200
        print("✓ Short search query handled")
    
    def test_search_results_have_type(self):
        """Search results should include type field"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/search?q=gestion")
        data = response.json()
        
        # Check results have proper type markers
        for sf in data.get("savoirs_faire", []):
            assert "type" in sf
            assert sf["type"] == "savoir_faire"
        for se in data.get("savoirs_etre", []):
            assert "type" in se
            assert se["type"] == "savoir_etre"
        
        print("✓ Search results have type field")


class TestExplorerDataIntegrity:
    """Tests for data integrity of imported ODS data"""
    
    def test_all_secteurs_counted(self):
        """Total secteurs from explorer should match stats"""
        explorer_resp = requests.get(f"{BASE_URL}/api/referentiel/explorer")
        stats_resp = requests.get(f"{BASE_URL}/api/referentiel/explorer/stats")
        
        explorer_data = explorer_resp.json()
        stats_data = stats_resp.json()
        
        total_secteurs = sum(len(f["secteurs"]) for f in explorer_data["filieres"])
        assert total_secteurs == stats_data["secteurs"], \
            f"Explorer has {total_secteurs} secteurs but stats says {stats_data['secteurs']}"
        
        print(f"✓ Secteur count matches: {total_secteurs}")
    
    def test_filiere_names_unique(self):
        """All filiere names should be unique"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer")
        data = response.json()
        
        names = [f["name"] for f in data["filieres"]]
        assert len(names) == len(set(names)), "Filiere names should be unique"
        
        print("✓ All filiere names are unique")
    
    def test_chain_completeness_for_sample_metier(self):
        """Sample metier should have complete chain data"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/metier/ingénieur en mécanique")
        data = response.json()
        metier = data["metier"]
        
        # Count data presence
        sf_count = len(metier.get("savoirs_faire", []))
        se_count = len(metier.get("savoirs_etre", []))
        
        assert sf_count >= 5, f"Expected at least 5 savoirs_faire, got {sf_count}"
        assert se_count >= 3, f"Expected at least 3 savoirs_etre, got {se_count}"
        
        # Check chain data in savoirs_etre
        chains_with_qualites = sum(1 for se in metier["savoirs_etre"] if se.get("qualites_humaines"))
        assert chains_with_qualites > 0, "At least some savoirs_etre should have qualites_humaines"
        
        print(f"✓ Metier chain completeness: {sf_count} SF, {se_count} SE, {chains_with_qualites} with qualités")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
