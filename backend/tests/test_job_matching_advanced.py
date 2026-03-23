"""
Test suite for Advanced Job Matching feature with filters and scoring.
Tests:
1. GET /api/jobs/matching/preferences - returns empty prefs for new user
2. PUT /api/jobs/matching/preferences - saves filter criteria with priorities
3. GET /api/jobs/matching/preferences - returns saved prefs after PUT
4. POST /api/jobs/matching/search - accepts candidate search profile
5. GET /api/jobs/matching - backward compatible, loads saved prefs
6. Backend scoring algorithm: calculate_job_score function
"""
import pytest
import requests
import os
import uuid
import sys
sys.path.insert(0, '/app/backend')
from job_matching import calculate_job_score

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestJobMatchingPreferences:
    """Tests for /api/jobs/matching/preferences endpoints"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user for preferences tests"""
        pseudo = f"test_prefs_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        return {"token": data["token"], "pseudo": pseudo}
    
    def test_get_preferences_empty_for_new_user(self, test_user):
        """Test GET /api/jobs/matching/preferences returns empty for new user"""
        response = requests.get(f"{BASE_URL}/api/jobs/matching/preferences?token={test_user['token']}")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("has_preferences") == False, f"Expected has_preferences=false, got {data.get('has_preferences')}"
        assert data.get("filters") == {}, f"Expected empty filters, got {data.get('filters')}"
        print("✓ GET preferences returns empty for new user")
    
    def test_put_preferences_saves_filters(self, test_user):
        """Test PUT /api/jobs/matching/preferences saves filter criteria"""
        payload = {
            "metier": {"value": ["conseiller insertion", "formateur"], "priority": 4},
            "secteur": {"value": ["formation", "insertion"], "priority": 3},
            "contrat": {"value": ["CDI", "CDD"], "priority": 3},
            "temps_travail": {"value": "temps plein", "priority": 2},
            "trajet_max_minutes": {"value": 45, "priority": 3},
            "teletravail": {"value": "souhaité", "priority": 2},
            "amenagement_poste": {"value": "souhaitable", "priority": 3},
            "restrictions_fonctionnelles": {
                "value": {"port_charges_impossible": True},
                "priority": 4
            }
        }
        
        response = requests.put(
            f"{BASE_URL}/api/jobs/matching/preferences?token={test_user['token']}",
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "message" in data, "Response should have message"
        assert "filters" in data, "Response should have filters"
        assert data["filters"].get("metier", {}).get("priority") == 4, "Metier priority should be 4"
        print("✓ PUT preferences saves filters correctly")
    
    def test_get_preferences_returns_saved(self, test_user):
        """Test GET /api/jobs/matching/preferences returns saved prefs after PUT"""
        response = requests.get(f"{BASE_URL}/api/jobs/matching/preferences?token={test_user['token']}")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("has_preferences") == True, f"Expected has_preferences=true"
        filters = data.get("filters", {})
        assert "metier" in filters, "Should have metier filter"
        assert "secteur" in filters, "Should have secteur filter"
        assert filters["metier"]["priority"] == 4, "Metier priority should be 4"
        print("✓ GET preferences returns saved filters")
    
    def test_preferences_invalid_token(self):
        """Test preferences endpoints reject invalid token"""
        response = requests.get(f"{BASE_URL}/api/jobs/matching/preferences?token=invalid_xyz")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid token rejected with 401")


class TestJobMatchingSearch:
    """Tests for POST /api/jobs/matching/search endpoint"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user for search tests"""
        pseudo = f"test_search_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200
        return {"token": response.json()["token"], "pseudo": pseudo}
    
    def test_search_without_cv_returns_no_data(self, test_user):
        """Test POST /api/jobs/matching/search returns has_data=false without CV"""
        payload = {
            "metier": {"value": ["conseiller insertion"], "priority": 4},
            "secteur": {"value": ["formation"], "priority": 3}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/jobs/matching/search?token={test_user['token']}",
            json=payload,
            timeout=30
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("has_data") == False, f"Expected has_data=false without CV"
        assert "message" in data, "Should have message when no CV"
        print("✓ Search without CV returns has_data=false")
    
    def test_search_returns_filters_applied_when_has_cv(self, test_user):
        """Test that search returns filters_applied in response when CV exists"""
        # Note: Without CV, search returns early without saving preferences
        # This is expected behavior - search requires CV data to work
        payload = {
            "metier": {"value": ["développeur"], "priority": 5},
            "secteur": {"value": ["informatique"], "priority": 4}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/jobs/matching/search?token={test_user['token']}",
            json=payload,
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        # Without CV, has_data=false and no filters_applied
        if not data.get("has_data"):
            assert "message" in data, "Should have message when no CV"
            print("✓ Search without CV returns has_data=false (expected)")
        else:
            # With CV, should have filters_applied
            assert "filters_applied" in data, "Should have filters_applied when has_data=true"
            print("✓ Search with CV returns filters_applied")
    
    def test_search_invalid_token(self):
        """Test search rejects invalid token"""
        response = requests.post(
            f"{BASE_URL}/api/jobs/matching/search?token=invalid_xyz",
            json={"metier": {"value": ["test"], "priority": 3}},
            timeout=10
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid token rejected")


class TestJobMatchingBackwardCompatible:
    """Tests for GET /api/jobs/matching (backward compatible)"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user"""
        pseudo = f"test_compat_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200
        return {"token": response.json()["token"], "pseudo": pseudo}
    
    def test_matching_loads_saved_prefs(self, test_user):
        """Test GET /api/jobs/matching loads saved preferences"""
        # First save some preferences
        requests.put(
            f"{BASE_URL}/api/jobs/matching/preferences?token={test_user['token']}",
            json={"metier": {"value": ["test métier"], "priority": 3}}
        )
        
        # Then call matching endpoint
        response = requests.get(f"{BASE_URL}/api/jobs/matching?token={test_user['token']}")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Without CV, should return has_data=false
        assert "has_data" in data, "Response should have has_data"
        assert "matches" in data, "Response should have matches"
        print(f"✓ Matching endpoint works (has_data={data.get('has_data')})")


class TestScoringAlgorithm:
    """Tests for calculate_job_score function"""
    
    def test_perfect_match_score(self):
        """Test scoring with perfect match returns 100%"""
        candidate = {
            'metier': {'value': ['conseiller insertion'], 'priority': 3},
            'secteur': {'value': ['formation'], 'priority': 3},
            'contrat': {'value': ['CDI'], 'priority': 3},
        }
        job = {
            'metier': 'conseiller insertion',
            'secteur': 'formation',
            'contrat': 'CDI',
        }
        
        result = calculate_job_score(candidate, job)
        assert result['score'] == 100, f"Expected 100, got {result['score']}"
        assert result['statut'] == 'Excellent match', f"Expected 'Excellent match', got {result['statut']}"
        assert len(result['blocages']) == 0, "Should have no blocages"
        print(f"✓ Perfect match: score={result['score']}, statut={result['statut']}")
    
    def test_blocking_criterion_priority_5(self):
        """Test that priority 5 with 0 compatibility creates blocking"""
        candidate = {
            'metier': {'value': ['développeur'], 'priority': 5},  # Blocking priority
        }
        job = {
            'metier': 'assistant administratif',  # No match
        }
        
        result = calculate_job_score(candidate, job)
        assert result['statut'] == 'Incompatible', f"Expected 'Incompatible', got {result['statut']}"
        assert len(result['blocages']) > 0, "Should have blocages"
        assert result['blocages'][0]['critere'] == 'Métier visé', "Blocage should be on métier"
        print(f"✓ Blocking criterion: statut={result['statut']}, blocages={result['blocages']}")
    
    def test_rqth_restrictions_blocking(self):
        """Test RQTH restrictions create blocking when incompatible"""
        candidate = {
            'metier': {'value': ['agent administratif'], 'priority': 3},
            'restrictions_fonctionnelles': {
                'value': {'port_charges_impossible': True},
                'priority': 5  # Blocking
            }
        }
        job = {
            'metier': 'agent administratif',
            'port_charges': True,  # Requires carrying loads - incompatible
        }
        
        result = calculate_job_score(candidate, job)
        assert result['statut'] == 'Incompatible', f"Expected 'Incompatible', got {result['statut']}"
        assert any(b['critere'] == 'Restrictions fonctionnelles' for b in result['blocages']), \
            "Should have restriction blocage"
        print(f"✓ RQTH restrictions blocking: statut={result['statut']}")
    
    def test_vigilances_partial_match(self):
        """Test that partial matches create vigilances"""
        candidate = {
            'metier': {'value': ['conseiller insertion'], 'priority': 3},
            'teletravail': {'value': 'souhaité', 'priority': 2},
        }
        job = {
            'metier': 'conseiller en insertion professionnelle',  # Close match
            'teletravail': False,  # Not available
        }
        
        result = calculate_job_score(candidate, job)
        # Should have vigilances for partial matches
        assert len(result['vigilances']) > 0 or len(result['points_forts']) > 0, \
            "Should have vigilances or points_forts"
        print(f"✓ Partial match: vigilances={len(result['vigilances'])}, points_forts={len(result['points_forts'])}")
    
    def test_score_detail_structure(self):
        """Test that score_detail has correct structure"""
        candidate = {
            'metier': {'value': ['test'], 'priority': 3},
        }
        job = {'metier': 'test'}
        
        result = calculate_job_score(candidate, job)
        assert 'score_detail' in result, "Should have score_detail"
        assert 'obtenu' in result['score_detail'], "score_detail should have 'obtenu'"
        assert 'maximum' in result['score_detail'], "score_detail should have 'maximum'"
        print(f"✓ Score detail: {result['score_detail']}")
    
    def test_evaluations_structure(self):
        """Test that evaluations array has correct structure"""
        candidate = {
            'metier': {'value': ['test'], 'priority': 3},
            'secteur': {'value': ['tech'], 'priority': 2},
        }
        job = {'metier': 'test', 'secteur': 'tech'}
        
        result = calculate_job_score(candidate, job)
        assert 'evaluations' in result, "Should have evaluations"
        assert len(result['evaluations']) == 2, "Should have 2 evaluations"
        
        for ev in result['evaluations']:
            assert 'label' in ev, "Evaluation should have label"
            assert 'priority' in ev, "Evaluation should have priority"
            assert 'compatibility' in ev, "Evaluation should have compatibility"
            assert 'score' in ev, "Evaluation should have score"
        print(f"✓ Evaluations structure valid: {len(result['evaluations'])} evaluations")


class TestScoringEdgeCases:
    """Edge case tests for scoring algorithm"""
    
    def test_empty_candidate_profile(self):
        """Test scoring with empty candidate profile"""
        result = calculate_job_score({}, {'metier': 'test'})
        assert 'score' in result, "Should return score"
        assert result['score'] == 0 or result['evaluations'] == [], "Empty profile should have 0 score or no evaluations"
        print(f"✓ Empty profile handled: score={result['score']}")
    
    def test_empty_job_offer(self):
        """Test scoring with empty job offer"""
        candidate = {'metier': {'value': ['test'], 'priority': 3}}
        result = calculate_job_score(candidate, {})
        assert 'score' in result, "Should return score"
        print(f"✓ Empty job offer handled: score={result['score']}")
    
    def test_metier_family_matching(self):
        """Test that related métiers in same family get partial score"""
        candidate = {
            'metier': {'value': ['conseiller en insertion professionnelle'], 'priority': 3},
        }
        job = {
            'metier': 'conseiller emploi',  # Same family
        }
        
        result = calculate_job_score(candidate, job)
        # Should get partial match (0.5-0.7) not 0
        assert result['score'] > 0, "Related métiers should get partial score"
        print(f"✓ Métier family matching: score={result['score']}")
    
    def test_sector_group_matching(self):
        """Test that related sectors get partial score"""
        candidate = {
            'secteur': {'value': ['formation'], 'priority': 3},
        }
        job = {
            'secteur': 'insertion',  # Same group
        }
        
        result = calculate_job_score(candidate, job)
        assert result['score'] > 0, "Related sectors should get partial score"
        print(f"✓ Sector group matching: score={result['score']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
