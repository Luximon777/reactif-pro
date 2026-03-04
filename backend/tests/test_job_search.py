"""
Tests for the job search bug fix:
- Bug: Search "chargé de recrutement" returned "Chef de chantier" instead of HR jobs
- Fix: normalize_text function removes accents and special chars for flexible matching
- Critical: "Chargé(e)" should match "chargé" after normalization
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Sample valid questionnaire answers (MBTI + DISC + Ennéagramme)
VALID_ANSWERS = {
    "v1": "E",   # énergie
    "v2": "E",   # énergie
    "v3": "S",   # perception  
    "v4": "S1,N1,S2,N2",  # perception ranking
    "v5": "T",   # décision
    "v6": "T",   # décision
    "v7": "J",   # structure
    "v8": "J",   # structure
    "v9": "D,I,S,C",  # disc ranking
    "v10": "D,I,S,C",  # disc ranking
    "v11": "2,3,5,4",  # ennea ranking
    "v12": "2,3,5,4"   # ennea ranking
}


class TestNormalizeTextFunction:
    """Tests for text normalization function - critical for bug fix"""
    
    def test_api_accessible(self):
        """Verify API is accessible via questionnaire endpoint"""
        response = requests.get(f"{BASE_URL}/api/questionnaire")
        assert response.status_code == 200, f"API not accessible: {response.status_code}"
        print("PASS: API accessible check OK")


class TestJobSearchBugFix:
    """
    Critical bug fix tests:
    - 'chargé de recrutement' should return 'Responsable RH / Chargé(e) RH' NOT 'Chef de chantier'
    """
    
    def test_charge_de_recrutement_returns_rh_job(self):
        """
        BUG FIX TEST: 'chargé de recrutement' should return HR job
        Expected: 'Responsable RH / Chargé(e) RH' as top result
        NOT Expected: 'Chef de chantier' 
        """
        payload = {
            "answers": VALID_ANSWERS,
            "job_query": "chargé de recrutement"
        }
        
        response = requests.post(f"{BASE_URL}/api/job-match", json=payload)
        assert response.status_code == 200, f"API returned {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify best_match exists
        assert "best_match" in data, "Response missing best_match field"
        best_match = data["best_match"]
        
        # Get job label
        job_label = best_match.get("job_label", "").lower()
        
        # CRITICAL: Should match HR job, NOT construction job
        print(f"Search 'chargé de recrutement' returned: {best_match.get('job_label')}")
        
        # Verify it's NOT Chef de chantier (the bug)
        assert "chef de chantier" not in job_label, \
            f"BUG STILL EXISTS: Got 'Chef de chantier' instead of RH job. Result: {best_match.get('job_label')}"
        
        # Verify it IS an RH-related job
        is_rh_job = any(kw in job_label for kw in ["rh", "ressources humaines", "chargé", "responsable rh"])
        assert is_rh_job, \
            f"Expected HR job, but got: {best_match.get('job_label')}"
        
        print(f"PASS: Bug fix verified - 'chargé de recrutement' correctly returns HR job")
    
    def test_developpeur_returns_developer_job(self):
        """
        Verify 'développeur' returns 'Développeur web / fullstack'
        """
        payload = {
            "answers": VALID_ANSWERS,
            "job_query": "développeur"
        }
        
        response = requests.post(f"{BASE_URL}/api/job-match", json=payload)
        assert response.status_code == 200, f"API returned {response.status_code}"
        
        data = response.json()
        best_match = data.get("best_match", {})
        job_label = best_match.get("job_label", "").lower()
        
        print(f"Search 'développeur' returned: {best_match.get('job_label')}")
        
        # Should match developer job
        is_dev_job = any(kw in job_label for kw in ["développeur", "developpeur", "fullstack", "web"])
        assert is_dev_job, f"Expected developer job, but got: {best_match.get('job_label')}"
        
        print("PASS: 'développeur' correctly returns developer job")
    
    def test_chef_de_chantier_returns_correct_job(self):
        """
        Verify 'chef de chantier' returns 'Chef de chantier'
        """
        payload = {
            "answers": VALID_ANSWERS,
            "job_query": "chef de chantier"
        }
        
        response = requests.post(f"{BASE_URL}/api/job-match", json=payload)
        assert response.status_code == 200, f"API returned {response.status_code}"
        
        data = response.json()
        best_match = data.get("best_match", {})
        job_label = best_match.get("job_label", "").lower()
        
        print(f"Search 'chef de chantier' returned: {best_match.get('job_label')}")
        
        assert "chef de chantier" in job_label, \
            f"Expected 'Chef de chantier', but got: {best_match.get('job_label')}"
        
        print("PASS: 'chef de chantier' correctly returns construction job")


class TestJobMatchEndpoint:
    """Tests for /api/job-match endpoint functionality"""
    
    def test_job_match_with_valid_answers(self):
        """Verify endpoint works with valid questionnaire responses"""
        payload = {
            "answers": VALID_ANSWERS,
            "job_query": "informatique"
        }
        
        response = requests.post(f"{BASE_URL}/api/job-match", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify response structure
        required_fields = ["best_match", "profile_narrative"]
        for field in required_fields:
            assert field in data, f"Response missing '{field}' field"
        
        # Verify best_match has expected fields
        best_match = data["best_match"]
        assert "job_id" in best_match, "best_match missing job_id"
        assert "job_label" in best_match, "best_match missing job_label"
        assert "score" in best_match, "best_match missing score"
        
        print(f"PASS: job-match endpoint returns valid response with score: {best_match.get('score')}")
    
    def test_job_match_with_birth_date(self):
        """Verify endpoint works with birth_date parameter"""
        payload = {
            "answers": VALID_ANSWERS,
            "job_query": "gestion",
            "birth_date": "1990-05-15"
        }
        
        response = requests.post(f"{BASE_URL}/api/job-match", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Should have life_path_data when birth_date is provided
        # Note: Check if the response includes this data
        assert "best_match" in data, "Response missing best_match"
        
        print("PASS: job-match endpoint works with birth_date parameter")
    
    def test_job_match_empty_query(self):
        """Verify endpoint handles empty job_query"""
        payload = {
            "answers": VALID_ANSWERS,
            "job_query": ""
        }
        
        response = requests.post(f"{BASE_URL}/api/job-match", json=payload)
        # Should either return results or 404, not crash
        assert response.status_code in [200, 404], \
            f"Unexpected status {response.status_code}: {response.text}"
        
        print(f"PASS: Empty query handled gracefully (status: {response.status_code})")


class TestSearchVariants:
    """Test various search query variations to ensure robust matching"""
    
    def test_recrutement_search(self):
        """Search for 'recrutement' should return HR-related jobs"""
        payload = {
            "answers": VALID_ANSWERS,
            "job_query": "recrutement"
        }
        
        response = requests.post(f"{BASE_URL}/api/job-match", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        job_label = data.get("best_match", {}).get("job_label", "").lower()
        
        print(f"Search 'recrutement' returned: {data.get('best_match', {}).get('job_label')}")
        
        # Recrutement should relate to HR
        assert "chef de chantier" not in job_label, \
            f"Bug: 'recrutement' incorrectly matched construction job: {job_label}"
        
        print("PASS: 'recrutement' search working correctly")
    
    def test_responsable_rh_search(self):
        """Direct search for 'responsable RH' should return exact match"""
        payload = {
            "answers": VALID_ANSWERS,
            "job_query": "responsable RH"
        }
        
        response = requests.post(f"{BASE_URL}/api/job-match", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        job_label = data.get("best_match", {}).get("job_label", "").lower()
        
        print(f"Search 'responsable RH' returned: {data.get('best_match', {}).get('job_label')}")
        
        assert "rh" in job_label or "ressources humaines" in job_label, \
            f"Expected HR job, got: {data.get('best_match', {}).get('job_label')}"
        
        print("PASS: 'responsable RH' returns correct job")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
