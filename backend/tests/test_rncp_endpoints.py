"""
Test RNCP API Endpoints - RE'ACTIF PRO OPC
==========================================
Tests for the RNCP/France Compétences ETL data endpoints:
- /api/referentiel/rncp/stats
- /api/referentiel/rncp/search
- /api/referentiel/rncp/fiche/{code}
- /api/referentiel/rncp/fiche/{code}/blocs
- /api/referentiel/rncp/rome/{code_rome}
- /api/referentiel/rncp/gap-analysis
- /api/referentiel/rncp/tension
- /api/observatory/ia/recommandation (enriched with RNCP)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestRNCPStats:
    """Test /api/referentiel/rncp/stats endpoint"""
    
    def test_stats_returns_expected_counts(self):
        """Stats should return total_certifications >= 30000, actives >= 6000, blocs >= 50000"""
        response = requests.get(f"{BASE_URL}/api/referentiel/rncp/stats")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify required fields exist
        assert "total_certifications" in data
        assert "actives" in data
        assert "blocs_competences" in data
        assert "mappings_rome" in data
        assert "source" in data
        
        # Verify counts meet requirements
        assert data["total_certifications"] >= 30000, f"Expected >= 30000 certifications, got {data['total_certifications']}"
        assert data["actives"] >= 6000, f"Expected >= 6000 active certifications, got {data['actives']}"
        assert data["blocs_competences"] >= 50000, f"Expected >= 50000 blocs, got {data['blocs_competences']}"
        
        # Verify source
        assert data["source"] == "France Compétences (data.gouv.fr)"
        
        print(f"PASS: Stats - {data['total_certifications']} certifications, {data['actives']} actives, {data['blocs_competences']} blocs")


class TestRNCPSearch:
    """Test /api/referentiel/rncp/search endpoint"""
    
    def test_search_comptable_returns_results(self):
        """Search for 'comptable' should return results with required fields"""
        response = requests.get(f"{BASE_URL}/api/referentiel/rncp/search?q=comptable")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify structure
        assert "results" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        
        # Verify results exist
        assert len(data["results"]) > 0, "Expected at least one result for 'comptable'"
        assert data["total"] > 0
        
        # Verify first result has required fields
        first_result = data["results"][0]
        assert "code" in first_result
        assert "intitule" in first_result
        assert "niveau" in first_result
        assert "statut" in first_result
        
        # Verify code format (RNCP or RS)
        assert first_result["code"].startswith("RNCP") or first_result["code"].startswith("RS")
        
        print(f"PASS: Search 'comptable' - {data['total']} results found")
    
    def test_search_with_filters(self):
        """Search with status filter should work"""
        response = requests.get(f"{BASE_URL}/api/referentiel/rncp/search?q=comptable&statut=ACTIVE")
        assert response.status_code == 200
        
        data = response.json()
        
        # All results should be ACTIVE
        for result in data["results"]:
            assert result["statut"] == "ACTIVE"
        
        print(f"PASS: Search with ACTIVE filter - {len(data['results'])} results")


class TestRNCPFiche:
    """Test /api/referentiel/rncp/fiche/{code} endpoint"""
    
    def test_get_fiche_rncp42012(self):
        """Get fiche RNCP42012 should return certification with blocs_competences"""
        response = requests.get(f"{BASE_URL}/api/referentiel/rncp/fiche/RNCP42012")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify main fields
        assert data["code"] == "RNCP42012"
        assert "intitule" in data
        assert "niveau" in data
        assert "statut" in data
        
        # Verify blocs_competences array exists
        assert "blocs_competences" in data
        assert isinstance(data["blocs_competences"], list)
        assert len(data["blocs_competences"]) > 0, "Expected at least one bloc de compétences"
        
        # Verify bloc structure
        first_bloc = data["blocs_competences"][0]
        assert "code_bloc" in first_bloc
        assert "intitule" in first_bloc
        assert "code_certification" in first_bloc
        
        # Verify codes_rome exists
        assert "codes_rome" in data
        
        print(f"PASS: Fiche RNCP42012 - {len(data['blocs_competences'])} blocs, {len(data['codes_rome'])} codes ROME")
    
    def test_get_fiche_not_found(self):
        """Get non-existent fiche should return 404"""
        response = requests.get(f"{BASE_URL}/api/referentiel/rncp/fiche/RNCP99999999")
        assert response.status_code == 404


class TestRNCPBlocs:
    """Test /api/referentiel/rncp/fiche/{code}/blocs endpoint"""
    
    def test_get_blocs_rncp42012(self):
        """Get blocs for RNCP42012 should return blocs array"""
        response = requests.get(f"{BASE_URL}/api/referentiel/rncp/fiche/RNCP42012/blocs")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify structure
        assert "code" in data
        assert "blocs" in data
        assert "count" in data
        
        assert data["code"] == "RNCP42012"
        assert isinstance(data["blocs"], list)
        assert len(data["blocs"]) > 0
        assert data["count"] == len(data["blocs"])
        
        # Verify bloc structure
        for bloc in data["blocs"]:
            assert "code_bloc" in bloc
            assert "intitule" in bloc
        
        print(f"PASS: Blocs RNCP42012 - {data['count']} blocs returned")


class TestRNCPRome:
    """Test /api/referentiel/rncp/rome/{code_rome} endpoint"""
    
    def test_get_certifications_by_rome_m1608(self):
        """Get certifications for ROME M1608 (Secrétariat comptable)"""
        response = requests.get(f"{BASE_URL}/api/referentiel/rncp/rome/M1608")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify structure
        assert "code_rome" in data
        assert "libelle_rome" in data
        assert "certifications" in data
        assert "count" in data
        
        assert data["code_rome"] == "M1608"
        assert "comptable" in data["libelle_rome"].lower() or "secrétariat" in data["libelle_rome"].lower()
        
        # Verify certifications exist
        assert len(data["certifications"]) > 0, "Expected certifications linked to M1608"
        assert data["count"] == len(data["certifications"])
        
        # Verify certification structure
        for cert in data["certifications"]:
            assert "code" in cert
            assert "intitule" in cert
        
        print(f"PASS: ROME M1608 - {data['count']} certifications, libelle: {data['libelle_rome']}")
    
    def test_get_certifications_by_rome_not_found(self):
        """Get certifications for non-existent ROME should return empty list"""
        response = requests.get(f"{BASE_URL}/api/referentiel/rncp/rome/ZZZZZ")
        assert response.status_code == 200
        
        data = response.json()
        assert data["certifications"] == []
        assert data["count"] == 0


class TestRNCPGapAnalysis:
    """Test /api/referentiel/rncp/gap-analysis endpoint"""
    
    def test_gap_analysis_with_competences(self):
        """Gap analysis should return couverture_pct > 0 with matching competences"""
        payload = {
            "code_rncp": "RNCP42012",
            "competences_utilisateur": ["comptabilité", "gestion"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/referentiel/rncp/gap-analysis",
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify structure
        assert "certification" in data
        assert "total_blocs" in data
        assert "blocs_maitrises" in data
        assert "blocs_manquants" in data
        assert "couverture_pct" in data
        assert "detail_maitrises" in data
        assert "detail_manquants" in data
        assert "plan_action" in data
        
        # Verify couverture_pct > 0 (since we provided matching competences)
        assert data["couverture_pct"] > 0, f"Expected couverture_pct > 0, got {data['couverture_pct']}"
        
        # Verify certification info
        assert data["certification"]["code"] == "RNCP42012"
        
        # Verify blocs counts
        assert data["total_blocs"] > 0
        assert data["blocs_maitrises"] + data["blocs_manquants"] == data["total_blocs"]
        
        print(f"PASS: Gap analysis - {data['couverture_pct']}% coverage, {data['blocs_maitrises']}/{data['total_blocs']} blocs maîtrisés")
    
    def test_gap_analysis_not_found(self):
        """Gap analysis for non-existent certification should return 404"""
        payload = {
            "code_rncp": "RNCP99999999",
            "competences_utilisateur": ["test"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/referentiel/rncp/gap-analysis",
            json=payload
        )
        assert response.status_code == 404


class TestRNCPTension:
    """Test /api/referentiel/rncp/tension endpoint"""
    
    def test_get_certifications_en_tension(self):
        """Get certifications en tension should return array"""
        response = requests.get(f"{BASE_URL}/api/referentiel/rncp/tension?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify structure
        assert "territoire" in data
        assert "certifications_en_tension" in data
        assert "count" in data
        
        # Verify certifications_en_tension is array
        assert isinstance(data["certifications_en_tension"], list)
        
        # Verify count matches
        assert data["count"] == len(data["certifications_en_tension"])
        
        # If results exist, verify structure
        if len(data["certifications_en_tension"]) > 0:
            cert = data["certifications_en_tension"][0]
            assert "code" in cert
            assert "intitule" in cert
            assert "nb_metiers_associes" in cert
        
        print(f"PASS: Tension - {data['count']} certifications en tension for {data['territoire']}")


class TestIARecommandationWithRNCP:
    """Test /api/observatory/ia/recommandation endpoint enriched with RNCP data"""
    
    def test_recommandation_includes_certifications_conseillees(self):
        """IA recommandation should include certifications_conseillees in response"""
        payload = {"contexte_metier": "comptable"}
        
        response = requests.post(
            f"{BASE_URL}/api/observatory/ia/recommandation",
            json=payload,
            timeout=90  # Claude AI can take time
        )
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify main structure
        assert "plan_action" in data or "error" in data
        
        if "error" not in data:
            # Verify certifications_conseillees exists
            assert "certifications_conseillees" in data, "Expected certifications_conseillees in response"
            
            certs = data["certifications_conseillees"]
            assert isinstance(certs, list)
            
            # If certifications exist, verify structure
            if len(certs) > 0:
                cert = certs[0]
                assert "code_rncp" in cert or "intitule" in cert
                
                # Verify other expected fields
                if "code_rncp" in cert:
                    assert cert["code_rncp"].startswith("RNCP") or cert["code_rncp"].startswith("RS")
                
                print(f"PASS: IA Recommandation - {len(certs)} certifications conseillées")
            else:
                print("PASS: IA Recommandation - certifications_conseillees field present (empty)")
        else:
            pytest.skip("IA returned error - may be temporary")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
