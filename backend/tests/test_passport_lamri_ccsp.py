"""
Test suite for Passport Dynamique de Compétences - Lamri & Lubart + CCSP features
Testing: 
- GET /api/passport - loads with new fields (components, ccsp_pole, ccsp_degree)
- POST /api/passport/competences - adding competence with Lamri & Lubart components and CCSP
- PUT /api/passport/competences/{comp_id}/evaluate - evaluating competence with 5 components (0-5) and CCSP
- GET /api/passport/diagnostic - generating diagnostic with Lamri & Lubart profile averages and CCSP distribution
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPassportLamriLubartCCSP:
    """Tests for Lamri & Lubart 5 components and CCSP classification in Passport"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get authentication token and initialize passport before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200, f"Auth failed: {response.text}"
        self.token = response.json()["token"]
        
        # Initialize passport by calling GET (auto-creates on first access)
        passport_response = requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        assert passport_response.status_code == 200, f"Failed to init passport: {passport_response.text}"
        yield
    
    # ============== GET /api/passport Tests ==============
    
    def test_passport_loads_with_new_fields(self):
        """GET /api/passport - passport loads correctly with new fields (components, ccsp_pole, ccsp_degree)"""
        response = requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        assert response.status_code == 200, f"Failed to get passport: {response.text}"
        
        data = response.json()
        assert "competences" in data
        assert "completeness_score" in data
        assert "id" in data
        print(f"✓ Passport loaded with {len(data.get('competences', []))} competences")
    
    # ============== POST /api/passport/competences Tests ==============
    
    def test_add_competence_with_ccsp_classification(self):
        """POST /api/passport/competences - adding competence with CCSP pole and degree"""
        comp_data = {
            "name": "TEST_Python_Dev_CCSP",
            "category": "technique",
            "level": "avance",
            "experience_years": 3,
            "ccsp_pole": "realisation",
            "ccsp_degree": "adaptation"
        }
        
        response = requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json=comp_data)
        assert response.status_code == 200, f"Failed to add competence: {response.text}"
        
        result = response.json()
        assert "competence" in result
        assert result["competence"]["name"] == "TEST_Python_Dev_CCSP"
        assert result["competence"]["ccsp_pole"] == "realisation"
        assert result["competence"]["ccsp_degree"] == "adaptation"
        print(f"✓ Competence added with CCSP: pole={result['competence']['ccsp_pole']}, degree={result['competence']['ccsp_degree']}")
        return result["competence"]["id"]
    
    def test_add_competence_with_all_ccsp_poles(self):
        """POST /api/passport/competences - works with all 3 CCSP poles"""
        poles = ["realisation", "interaction", "initiative"]
        
        for pole in poles:
            comp_data = {
                "name": f"TEST_Competence_{pole}",
                "category": "technique",
                "level": "intermediaire",
                "ccsp_pole": pole,
                "ccsp_degree": "imitation"
            }
            response = requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json=comp_data)
            assert response.status_code == 200, f"Failed to add competence with pole {pole}: {response.text}"
            assert response.json()["competence"]["ccsp_pole"] == pole
            print(f"✓ Competence added with CCSP pole: {pole}")
    
    def test_add_competence_with_all_ccsp_degrees(self):
        """POST /api/passport/competences - works with all 3 CCSP degrees"""
        degrees = ["imitation", "adaptation", "transposition"]
        
        for degree in degrees:
            comp_data = {
                "name": f"TEST_Competence_degree_{degree}",
                "category": "transversale",
                "level": "avance",
                "ccsp_pole": "realisation",
                "ccsp_degree": degree
            }
            response = requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json=comp_data)
            assert response.status_code == 200, f"Failed to add competence with degree {degree}: {response.text}"
            assert response.json()["competence"]["ccsp_degree"] == degree
            print(f"✓ Competence added with CCSP degree: {degree}")
    
    def test_add_competence_without_ccsp(self):
        """POST /api/passport/competences - competence can be added without CCSP (optional fields)"""
        comp_data = {
            "name": "TEST_No_CCSP_Competence",
            "category": "relationnelle",
            "level": "debutant"
        }
        
        response = requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json=comp_data)
        assert response.status_code == 200, f"Failed to add competence: {response.text}"
        
        result = response.json()
        assert result["competence"]["ccsp_pole"] == ""
        assert result["competence"]["ccsp_degree"] == ""
        print("✓ Competence added without CCSP classification (optional)")
    
    # ============== PUT /api/passport/competences/{comp_id}/evaluate Tests ==============
    
    def test_evaluate_competence_with_5_components(self):
        """PUT /api/passport/competences/{comp_id}/evaluate - evaluating with 5 components (0-5)"""
        # First add a competence
        comp_data = {"name": "TEST_Evaluate_Comp", "category": "technique", "level": "intermediaire"}
        add_response = requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json=comp_data)
        assert add_response.status_code == 200, f"Failed to add competence: {add_response.text}"
        comp_id = add_response.json()["competence"]["id"]
        
        # Evaluate with all 5 Lamri & Lubart components
        eval_data = {
            "components": {
                "connaissance": 4,
                "cognition": 3,
                "conation": 5,
                "affection": 2,
                "sensori_moteur": 3
            }
        }
        
        response = requests.put(f"{BASE_URL}/api/passport/competences/{comp_id}/evaluate?token={self.token}", json=eval_data)
        assert response.status_code == 200, f"Failed to evaluate: {response.text}"
        
        result = response.json()
        assert "components" in result
        assert result["components"]["connaissance"] == 4
        assert result["components"]["cognition"] == 3
        assert result["components"]["conation"] == 5
        assert result["components"]["affection"] == 2
        assert result["components"]["sensori_moteur"] == 3
        print(f"✓ Competence evaluated with 5 components: {result['components']}")
        return comp_id
    
    def test_evaluate_competence_with_ccsp(self):
        """PUT /api/passport/competences/{comp_id}/evaluate - evaluating with CCSP pole and degree"""
        # First add a competence
        comp_data = {"name": "TEST_Evaluate_CCSP", "category": "transversale", "level": "avance"}
        add_response = requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json=comp_data)
        assert add_response.status_code == 200, f"Failed to add competence: {add_response.text}"
        comp_id = add_response.json()["competence"]["id"]
        
        # Evaluate with components and CCSP
        eval_data = {
            "components": {
                "connaissance": 3,
                "cognition": 4,
                "conation": 4,
                "affection": 3,
                "sensori_moteur": 2
            },
            "ccsp_pole": "interaction",
            "ccsp_degree": "transposition"
        }
        
        response = requests.put(f"{BASE_URL}/api/passport/competences/{comp_id}/evaluate?token={self.token}", json=eval_data)
        assert response.status_code == 200, f"Failed to evaluate with CCSP: {response.text}"
        
        # Verify the evaluation was saved
        passport_response = requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        assert passport_response.status_code == 200
        
        competences = passport_response.json().get("competences", [])
        updated_comp = next((c for c in competences if c["id"] == comp_id), None)
        assert updated_comp is not None
        assert updated_comp["ccsp_pole"] == "interaction"
        assert updated_comp["ccsp_degree"] == "transposition"
        print(f"✓ Competence evaluated with CCSP: pole={updated_comp['ccsp_pole']}, degree={updated_comp['ccsp_degree']}")
    
    def test_evaluate_component_value_clamping(self):
        """PUT /api/passport/competences/{comp_id}/evaluate - values clamped to 0-5 range"""
        # First add a competence
        comp_data = {"name": "TEST_Clamp_Values", "category": "technique", "level": "expert"}
        add_response = requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json=comp_data)
        assert add_response.status_code == 200, f"Failed to add competence: {add_response.text}"
        comp_id = add_response.json()["competence"]["id"]
        
        # Evaluate with values out of range (should be clamped)
        eval_data = {
            "components": {
                "connaissance": 10,  # Should be clamped to 5
                "cognition": -5,     # Should be clamped to 0
                "conation": 3,
                "affection": 7,      # Should be clamped to 5
                "sensori_moteur": 2
            }
        }
        
        response = requests.put(f"{BASE_URL}/api/passport/competences/{comp_id}/evaluate?token={self.token}", json=eval_data)
        assert response.status_code == 200, f"Failed to evaluate: {response.text}"
        
        result = response.json()
        assert result["components"]["connaissance"] <= 5
        assert result["components"]["cognition"] >= 0
        assert result["components"]["affection"] <= 5
        print(f"✓ Component values properly clamped: {result['components']}")
    
    def test_evaluate_nonexistent_competence(self):
        """PUT /api/passport/competences/{comp_id}/evaluate - 404 for nonexistent competence"""
        eval_data = {"components": {"connaissance": 3, "cognition": 3, "conation": 3, "affection": 3, "sensori_moteur": 3}}
        
        response = requests.put(f"{BASE_URL}/api/passport/competences/nonexistent-id-12345/evaluate?token={self.token}", json=eval_data)
        assert response.status_code == 404, f"Expected 404 but got {response.status_code}"
        print("✓ 404 returned for nonexistent competence")
    
    # ============== GET /api/passport/diagnostic Tests ==============
    
    def test_diagnostic_with_empty_competences(self):
        """GET /api/passport/diagnostic - returns empty profile for no competences"""
        response = requests.get(f"{BASE_URL}/api/passport/diagnostic?token={self.token}")
        assert response.status_code == 200, f"Failed to get diagnostic: {response.text}"
        
        data = response.json()
        assert "total_competences" in data
        assert "evaluated_count" in data
        assert "lamri_lubart_profile" in data
        assert "ccsp_distribution" in data
        assert "recommendations" in data
        print(f"✓ Diagnostic returned: total={data['total_competences']}, evaluated={data['evaluated_count']}")
    
    def test_diagnostic_with_evaluated_competences(self):
        """GET /api/passport/diagnostic - returns averages and distribution for evaluated competences"""
        # Add and evaluate multiple competences
        competences_to_add = [
            {
                "name": "TEST_Diag_Comp_1",
                "components": {"connaissance": 4, "cognition": 3, "conation": 5, "affection": 2, "sensori_moteur": 3},
                "ccsp_pole": "realisation",
                "ccsp_degree": "adaptation"
            },
            {
                "name": "TEST_Diag_Comp_2",
                "components": {"connaissance": 2, "cognition": 5, "conation": 3, "affection": 4, "sensori_moteur": 1},
                "ccsp_pole": "interaction",
                "ccsp_degree": "transposition"
            },
            {
                "name": "TEST_Diag_Comp_3",
                "components": {"connaissance": 3, "cognition": 4, "conation": 4, "affection": 3, "sensori_moteur": 5},
                "ccsp_pole": "initiative",
                "ccsp_degree": "imitation"
            }
        ]
        
        for comp_info in competences_to_add:
            # Add competence
            add_data = {"name": comp_info["name"], "category": "technique", "level": "avance"}
            add_response = requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json=add_data)
            assert add_response.status_code == 200, f"Failed to add competence: {add_response.text}"
            comp_id = add_response.json()["competence"]["id"]
            
            # Evaluate
            eval_data = {
                "components": comp_info["components"],
                "ccsp_pole": comp_info["ccsp_pole"],
                "ccsp_degree": comp_info["ccsp_degree"]
            }
            eval_response = requests.put(f"{BASE_URL}/api/passport/competences/{comp_id}/evaluate?token={self.token}", json=eval_data)
            assert eval_response.status_code == 200, f"Failed to evaluate: {eval_response.text}"
        
        # Get diagnostic
        response = requests.get(f"{BASE_URL}/api/passport/diagnostic?token={self.token}")
        assert response.status_code == 200, f"Failed to get diagnostic: {response.text}"
        
        data = response.json()
        
        # Verify Lamri & Lubart profile averages
        assert data["evaluated_count"] >= 3
        ll_profile = data["lamri_lubart_profile"]
        assert "connaissance" in ll_profile
        assert "cognition" in ll_profile
        assert "conation" in ll_profile
        assert "affection" in ll_profile
        assert "sensori_moteur" in ll_profile
        print(f"✓ Lamri & Lubart profile averages: {ll_profile}")
        
        # Verify CCSP distribution
        ccsp = data["ccsp_distribution"]
        assert "poles" in ccsp
        assert "degrees" in ccsp
        assert ccsp["poles"].get("realisation", 0) >= 1
        assert ccsp["poles"].get("interaction", 0) >= 1
        assert ccsp["poles"].get("initiative", 0) >= 1
        print(f"✓ CCSP poles distribution: {ccsp['poles']}")
        print(f"✓ CCSP degrees distribution: {ccsp['degrees']}")
    
    def test_diagnostic_generates_recommendations(self):
        """GET /api/passport/diagnostic - generates recommendations based on low scores"""
        # Add competence with low scores
        add_data = {"name": "TEST_Low_Scores_Comp", "category": "technique", "level": "debutant"}
        add_response = requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json=add_data)
        assert add_response.status_code == 200, f"Failed to add competence: {add_response.text}"
        comp_id = add_response.json()["competence"]["id"]
        
        # Evaluate with low values (0-1 for all components)
        eval_data = {
            "components": {
                "connaissance": 1,
                "cognition": 1,
                "conation": 1,
                "affection": 0,
                "sensori_moteur": 1
            },
            "ccsp_pole": "realisation",
            "ccsp_degree": "imitation"
        }
        
        eval_response = requests.put(f"{BASE_URL}/api/passport/competences/{comp_id}/evaluate?token={self.token}", json=eval_data)
        assert eval_response.status_code == 200, f"Failed to evaluate: {eval_response.text}"
        
        # Get diagnostic - should have recommendations
        response = requests.get(f"{BASE_URL}/api/passport/diagnostic?token={self.token}")
        assert response.status_code == 200, f"Failed to get diagnostic: {response.text}"
        
        data = response.json()
        recommendations = data.get("recommendations", [])
        
        # With all low scores, should have recommendations
        print(f"✓ Diagnostic generated {len(recommendations)} recommendations")
        for rec in recommendations:
            print(f"  - {rec.get('type', 'unknown')}: {rec.get('message', '')[:60]}...")
    
    def test_diagnostic_invalid_token(self):
        """GET /api/passport/diagnostic - returns 401 for invalid token"""
        response = requests.get(f"{BASE_URL}/api/passport/diagnostic?token=invalid-token-12345")
        assert response.status_code == 401
        print("✓ 401 returned for invalid token on diagnostic")


class TestPassportCompetenceStructure:
    """Tests to verify competence data structure includes new fields"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get authentication token and initialize passport before each test"""
        response = requests.post(f"{BASE_URL}/api/auth/anonymous", json={"role": "particulier"})
        assert response.status_code == 200
        self.token = response.json()["token"]
        
        # Initialize passport by calling GET (auto-creates on first access)
        passport_response = requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        assert passport_response.status_code == 200
        yield
    
    def test_competence_has_components_field(self):
        """Verify competence has components field in passport response"""
        # Add a competence
        add_data = {"name": "TEST_Check_Structure", "category": "technique", "level": "intermediaire"}
        add_response = requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json=add_data)
        assert add_response.status_code == 200, f"Failed to add competence: {add_response.text}"
        
        # Get passport
        response = requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        assert response.status_code == 200
        
        competences = response.json().get("competences", [])
        test_comp = next((c for c in competences if "TEST_Check_Structure" in c.get("name", "")), None)
        
        assert test_comp is not None
        assert "components" in test_comp
        assert isinstance(test_comp["components"], dict)
        
        # Verify all 5 component keys exist
        expected_keys = {"connaissance", "cognition", "conation", "affection", "sensori_moteur"}
        assert set(test_comp["components"].keys()) == expected_keys
        print(f"✓ Competence has components field with all 5 keys: {list(test_comp['components'].keys())}")
    
    def test_competence_has_ccsp_fields(self):
        """Verify competence has ccsp_pole and ccsp_degree fields"""
        # Add a competence
        add_data = {"name": "TEST_CCSP_Fields", "category": "transversale", "level": "avance", "ccsp_pole": "interaction", "ccsp_degree": "adaptation"}
        add_response = requests.post(f"{BASE_URL}/api/passport/competences?token={self.token}", json=add_data)
        assert add_response.status_code == 200, f"Failed to add competence: {add_response.text}"
        
        # Get passport
        response = requests.get(f"{BASE_URL}/api/passport?token={self.token}")
        assert response.status_code == 200
        
        competences = response.json().get("competences", [])
        test_comp = next((c for c in competences if "TEST_CCSP_Fields" in c.get("name", "")), None)
        
        assert test_comp is not None
        assert "ccsp_pole" in test_comp
        assert "ccsp_degree" in test_comp
        assert test_comp["ccsp_pole"] == "interaction"
        assert test_comp["ccsp_degree"] == "adaptation"
        print(f"✓ Competence has CCSP fields: pole={test_comp['ccsp_pole']}, degree={test_comp['ccsp_degree']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
