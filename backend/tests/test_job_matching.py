"""
Test Job Matching endpoints:
- GET /api/jobs/matching - Initial matching without filters
- POST /api/jobs/matching/search - Matching with scoring filters
- GET /api/jobs/matching/preferences - Get saved preferences
- POST /api/jobs/france-travail/search - France Travail job search
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
TEST_PSEUDO = "mike7"
TEST_PASSWORD = "Solerys777!"


class TestJobMatchingEndpoints:
    """Test Job Matching API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token before each test"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get token
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"pseudo": TEST_PSEUDO, "password": TEST_PASSWORD}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.token = login_response.json().get("token")
        assert self.token, "No token returned from login"
    
    # ============== GET /api/jobs/matching ==============
    
    def test_jobs_matching_get_returns_200(self):
        """GET /api/jobs/matching returns 200 with valid token"""
        response = self.session.get(f"{BASE_URL}/api/jobs/matching?token={self.token}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: GET /api/jobs/matching returns 200")
    
    def test_jobs_matching_get_has_correct_format(self):
        """GET /api/jobs/matching returns correct format: {has_data, has_filters, profile_summary, matches}"""
        response = self.session.get(f"{BASE_URL}/api/jobs/matching?token={self.token}")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "has_data" in data, "Missing 'has_data' field"
        assert "has_filters" in data, "Missing 'has_filters' field"
        assert "profile_summary" in data, "Missing 'profile_summary' field"
        assert "matches" in data, "Missing 'matches' field"
        
        # has_filters should be False for initial GET
        assert data["has_filters"] == False, f"Expected has_filters=False, got {data['has_filters']}"
        
        # matches should be a list
        assert isinstance(data["matches"], list), "matches should be a list"
        
        print(f"PASS: GET /api/jobs/matching has correct format - has_data={data['has_data']}, matches_count={len(data['matches'])}")
    
    def test_jobs_matching_get_profile_summary_structure(self):
        """GET /api/jobs/matching profile_summary has correct structure"""
        response = self.session.get(f"{BASE_URL}/api/jobs/matching?token={self.token}")
        assert response.status_code == 200
        data = response.json()
        
        profile_summary = data.get("profile_summary", {})
        assert "titre" in profile_summary, "Missing 'titre' in profile_summary"
        assert "skills_count" in profile_summary, "Missing 'skills_count' in profile_summary"
        assert "has_optimized_cv" in profile_summary, "Missing 'has_optimized_cv' in profile_summary"
        assert "has_career_project" in profile_summary, "Missing 'has_career_project' in profile_summary"
        
        print(f"PASS: profile_summary structure correct - titre={profile_summary.get('titre')}, skills_count={profile_summary.get('skills_count')}")
    
    def test_jobs_matching_get_match_entry_structure(self):
        """GET /api/jobs/matching match entries have correct structure"""
        response = self.session.get(f"{BASE_URL}/api/jobs/matching?token={self.token}")
        assert response.status_code == 200
        data = response.json()
        
        if data["matches"]:
            match = data["matches"][0]
            # Check required fields in match entry
            assert "titre" in match, "Missing 'titre' in match"
            assert "matching_score" in match, "Missing 'matching_score' in match"
            assert "secteur" in match, "Missing 'secteur' in match"
            assert "type_contrat" in match, "Missing 'type_contrat' in match"
            
            # scoring should be null for initial GET (no filters applied)
            assert match.get("scoring") is None, f"Expected scoring=null for initial GET, got {match.get('scoring')}"
            
            print(f"PASS: Match entry structure correct - titre={match.get('titre')}, score={match.get('matching_score')}")
        else:
            print("PASS: No matches returned (empty list is valid)")
    
    def test_jobs_matching_get_invalid_token(self):
        """GET /api/jobs/matching returns 401 for invalid token"""
        response = self.session.get(f"{BASE_URL}/api/jobs/matching?token=invalid_token_123")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: GET /api/jobs/matching returns 401 for invalid token")
    
    # ============== POST /api/jobs/matching/search ==============
    
    def test_jobs_matching_search_returns_200(self):
        """POST /api/jobs/matching/search returns 200 with valid token"""
        response = self.session.post(
            f"{BASE_URL}/api/jobs/matching/search?token={self.token}",
            json={"metier": {"value": ["Conseiller"], "priority": 3}}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: POST /api/jobs/matching/search returns 200")
    
    def test_jobs_matching_search_has_filters_true(self):
        """POST /api/jobs/matching/search returns has_filters=True"""
        response = self.session.post(
            f"{BASE_URL}/api/jobs/matching/search?token={self.token}",
            json={"zone_geographique": {"value": "Paris", "priority": 4}}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("has_filters") == True, f"Expected has_filters=True, got {data.get('has_filters')}"
        print("PASS: POST /api/jobs/matching/search returns has_filters=True")
    
    def test_jobs_matching_search_returns_scoring_object(self):
        """POST /api/jobs/matching/search returns matches with scoring object"""
        response = self.session.post(
            f"{BASE_URL}/api/jobs/matching/search?token={self.token}",
            json={
                "metier": {"value": ["Développeur"], "priority": 3},
                "zone_geographique": {"value": "Paris", "priority": 4}
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        if data["matches"]:
            match = data["matches"][0]
            scoring = match.get("scoring")
            
            # scoring should NOT be null when filters are applied
            assert scoring is not None, "Expected scoring object when filters applied"
            
            # Check scoring structure
            assert "statut" in scoring, "Missing 'statut' in scoring"
            assert "score_detail" in scoring, "Missing 'score_detail' in scoring"
            assert "evaluations" in scoring, "Missing 'evaluations' in scoring"
            assert "blocages" in scoring, "Missing 'blocages' in scoring"
            assert "vigilances" in scoring, "Missing 'vigilances' in scoring"
            assert "points_forts" in scoring, "Missing 'points_forts' in scoring"
            
            print(f"PASS: Scoring object present - statut={scoring.get('statut')}, score_detail={scoring.get('score_detail')}")
        else:
            print("PASS: No matches returned (empty list is valid)")
    
    def test_jobs_matching_search_scoring_statut_values(self):
        """POST /api/jobs/matching/search scoring.statut has valid values"""
        response = self.session.post(
            f"{BASE_URL}/api/jobs/matching/search?token={self.token}",
            json={"contrat": {"value": ["CDI"], "priority": 3}}
        )
        assert response.status_code == 200
        data = response.json()
        
        valid_statuts = ["Excellent match", "Match pertinent", "Match moyen", "Faible compatibilité", "Incompatible"]
        
        for match in data.get("matches", []):
            scoring = match.get("scoring")
            if scoring:
                statut = scoring.get("statut")
                assert statut in valid_statuts, f"Invalid statut: {statut}"
        
        print("PASS: All scoring.statut values are valid")
    
    def test_jobs_matching_search_with_multiple_filters(self):
        """POST /api/jobs/matching/search works with multiple filters"""
        response = self.session.post(
            f"{BASE_URL}/api/jobs/matching/search?token={self.token}",
            json={
                "metier": {"value": ["Conseiller", "Formateur"], "priority": 3},
                "secteur": {"value": ["Formation", "Insertion"], "priority": 3},
                "contrat": {"value": ["CDI", "CDD"], "priority": 3},
                "zone_geographique": {"value": "Paris", "priority": 4},
                "salaire_minimum": {"value": 25000, "priority": 3}
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "matches" in data
        assert "has_filters" in data
        assert data["has_filters"] == True
        
        print(f"PASS: Multiple filters work - {len(data['matches'])} matches returned")
    
    def test_jobs_matching_search_invalid_token(self):
        """POST /api/jobs/matching/search returns 401 for invalid token"""
        response = self.session.post(
            f"{BASE_URL}/api/jobs/matching/search?token=invalid_token_123",
            json={"metier": {"value": ["Test"], "priority": 3}}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: POST /api/jobs/matching/search returns 401 for invalid token")
    
    # ============== GET /api/jobs/matching/preferences ==============
    
    def test_jobs_matching_preferences_get_returns_200(self):
        """GET /api/jobs/matching/preferences returns 200 with valid token"""
        response = self.session.get(f"{BASE_URL}/api/jobs/matching/preferences?token={self.token}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: GET /api/jobs/matching/preferences returns 200")
    
    def test_jobs_matching_preferences_get_has_correct_format(self):
        """GET /api/jobs/matching/preferences returns {has_preferences, filters}"""
        response = self.session.get(f"{BASE_URL}/api/jobs/matching/preferences?token={self.token}")
        assert response.status_code == 200
        data = response.json()
        
        assert "has_preferences" in data, "Missing 'has_preferences' field"
        assert "filters" in data, "Missing 'filters' field"
        
        print(f"PASS: Preferences format correct - has_preferences={data['has_preferences']}")
    
    def test_jobs_matching_preferences_get_invalid_token(self):
        """GET /api/jobs/matching/preferences returns 401 for invalid token"""
        response = self.session.get(f"{BASE_URL}/api/jobs/matching/preferences?token=invalid_token_123")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: GET /api/jobs/matching/preferences returns 401 for invalid token")
    
    # ============== POST /api/jobs/france-travail/search ==============
    
    def test_france_travail_search_returns_200(self):
        """POST /api/jobs/france-travail/search returns 200 with valid token"""
        response = self.session.post(
            f"{BASE_URL}/api/jobs/france-travail/search?token={self.token}",
            json={"departement": "75"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: POST /api/jobs/france-travail/search returns 200")
    
    def test_france_travail_search_has_correct_format(self):
        """POST /api/jobs/france-travail/search returns correct format"""
        response = self.session.post(
            f"{BASE_URL}/api/jobs/france-travail/search?token={self.token}",
            json={"departement": "75"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "has_data" in data, "Missing 'has_data' field"
        assert "matches" in data, "Missing 'matches' field"
        assert isinstance(data["matches"], list), "matches should be a list"
        
        print(f"PASS: France Travail search format correct - has_data={data['has_data']}, matches_count={len(data['matches'])}")
    
    def test_france_travail_search_with_different_departement(self):
        """POST /api/jobs/france-travail/search works with different departement"""
        response = self.session.post(
            f"{BASE_URL}/api/jobs/france-travail/search?token={self.token}",
            json={"departement": "69"}  # Lyon
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "matches" in data
        print(f"PASS: France Travail search with departement 69 - {len(data['matches'])} matches")
    
    def test_france_travail_search_match_entry_structure(self):
        """POST /api/jobs/france-travail/search match entries have correct structure"""
        response = self.session.post(
            f"{BASE_URL}/api/jobs/france-travail/search?token={self.token}",
            json={"departement": "75"}
        )
        assert response.status_code == 200
        data = response.json()
        
        if data["matches"]:
            match = data["matches"][0]
            # Check required fields in match entry
            assert "titre" in match, "Missing 'titre' in match"
            assert "matching_score" in match, "Missing 'matching_score' in match"
            
            print(f"PASS: FT match entry structure correct - titre={match.get('titre')}, score={match.get('matching_score')}")
        else:
            print("PASS: No FT matches returned (API may be unavailable or no results)")
    
    def test_france_travail_search_invalid_token(self):
        """POST /api/jobs/france-travail/search returns 401 for invalid token"""
        response = self.session.post(
            f"{BASE_URL}/api/jobs/france-travail/search?token=invalid_token_123",
            json={"departement": "75"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: POST /api/jobs/france-travail/search returns 401 for invalid token")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
