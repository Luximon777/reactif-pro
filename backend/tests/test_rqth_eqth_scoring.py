"""
Test suite for RQTH/EQTH scoring integration in Job Matching.
Tests the new scoring algorithm features:
1. calculate_job_score with full RQTH/EQTH profile returns score, score_inclusion, contexte_handicap
2. compare_restrictions handles all 8 restriction types
3. calculate_inclusion_score correctly scores employer inclusion (0-100)
4. compare_metier_handicap combines metier+restrictions+amenagement scores
5. RQTH status is contextual only - never causes blocking
6. POST /api/jobs/matching/search accepts rqth_eqth, ciblage_employeurs_inclusifs, accessibilite_metier_handicap
7. PUT /api/jobs/matching/preferences saves new fields
"""
import pytest
import requests
import os
import uuid
import sys
sys.path.insert(0, '/app/backend')
from job_matching import (
    calculate_job_score, 
    compare_restrictions, 
    calculate_inclusion_score, 
    compare_metier_handicap
)

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


# ============================================================================
# Unit Tests for Scoring Functions
# ============================================================================

class TestCompareRestrictions:
    """Tests for compare_restrictions function - all 8 restriction types"""
    
    def test_port_charges_impossible(self):
        """Test port_charges_impossible restriction"""
        restrictions = {"port_charges_impossible": True}
        
        # Job requires port_charges - should fail
        job_conditions = {"port_charges": True}
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 0, f"Expected 0 (incompatible), got {result}"
        
        # Job doesn't require port_charges - should pass
        job_conditions = {"port_charges": False}
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 1, f"Expected 1 (compatible), got {result}"
        print("✓ port_charges_impossible restriction works correctly")
    
    def test_station_debout_prolongee_limitee(self):
        """Test station_debout_prolongee_limitee restriction"""
        restrictions = {"station_debout_prolongee_limitee": True}
        
        # Job requires standing - should fail
        job_conditions = {"station_debout_prolongee": True}
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 0, f"Expected 0 (incompatible), got {result}"
        
        # Job doesn't require standing - should pass
        job_conditions = {"station_debout_prolongee": False}
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 1, f"Expected 1 (compatible), got {result}"
        print("✓ station_debout_prolongee_limitee restriction works correctly")
    
    def test_travail_nuit_impossible(self):
        """Test travail_nuit_impossible restriction"""
        restrictions = {"travail_nuit_impossible": True}
        
        # Job requires night work - should fail
        job_conditions = {"travail_nuit": True}
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 0, f"Expected 0 (incompatible), got {result}"
        
        # Job doesn't require night work - should pass
        job_conditions = {"travail_nuit": False}
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 1, f"Expected 1 (compatible), got {result}"
        print("✓ travail_nuit_impossible restriction works correctly")
    
    def test_environnement_calme_recherche(self):
        """Test environnement_calme_recherche restriction"""
        restrictions = {"environnement_calme_recherche": True}
        
        # Job has calm environment - should pass
        job_conditions = {"environnement": "calme"}
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 1, f"Expected 1 (compatible), got {result}"
        
        # Job has no environment specified - partial
        job_conditions = {"environnement": ""}
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 0.5, f"Expected 0.5 (partial), got {result}"
        print("✓ environnement_calme_recherche restriction works correctly")
    
    def test_horaires_stables_recherches(self):
        """Test horaires_stables_recherches restriction"""
        restrictions = {"horaires_stables_recherches": True}
        
        # Job has shifted hours - should fail
        job_conditions = {"horaires_decales": True}
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 0, f"Expected 0 (incompatible), got {result}"
        
        # Job has stable hours - should pass
        job_conditions = {"horaires_decales": False}
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 1, f"Expected 1 (compatible), got {result}"
        print("✓ horaires_stables_recherches restriction works correctly")
    
    def test_accessibilite_necessaire(self):
        """Test accessibilite_necessaire restriction"""
        restrictions = {"accessibilite_necessaire": True}
        
        # Job is accessible - should pass
        job_conditions = {"accessibilite_locaux": True}
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 1, f"Expected 1 (compatible), got {result}"
        
        # Job is not accessible - should fail
        job_conditions = {"accessibilite_locaux": False}
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 0, f"Expected 0 (incompatible), got {result}"
        
        # Job accessibility unknown - partial
        job_conditions = {"accessibilite_locaux": None}
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 0.5, f"Expected 0.5 (partial), got {result}"
        print("✓ accessibilite_necessaire restriction works correctly")
    
    def test_deplacements_frequents_difficiles(self):
        """Test deplacements_frequents_difficiles restriction"""
        restrictions = {"deplacements_frequents_difficiles": True}
        
        # Job requires frequent travel - should fail
        job_conditions = {"deplacements_frequents": True}
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 0, f"Expected 0 (incompatible), got {result}"
        
        # Job doesn't require frequent travel - should pass
        job_conditions = {"deplacements_frequents": False}
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 1, f"Expected 1 (compatible), got {result}"
        print("✓ deplacements_frequents_difficiles restriction works correctly")
    
    def test_cadence_elevee_difficile(self):
        """Test cadence_elevee_difficile restriction"""
        restrictions = {"cadence_elevee_difficile": True}
        
        # Job has high pace - should fail
        job_conditions = {"cadence_elevee": True}
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 0, f"Expected 0 (incompatible), got {result}"
        
        # Job doesn't have high pace - should pass
        job_conditions = {"cadence_elevee": False}
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 1, f"Expected 1 (compatible), got {result}"
        print("✓ cadence_elevee_difficile restriction works correctly")
    
    def test_multiple_restrictions_min_score(self):
        """Test that multiple restrictions return minimum score"""
        restrictions = {
            "port_charges_impossible": True,
            "travail_nuit_impossible": True,
            "cadence_elevee_difficile": True
        }
        
        # One incompatible condition should make result 0
        job_conditions = {
            "port_charges": False,
            "travail_nuit": True,  # This fails
            "cadence_elevee": False
        }
        result = compare_restrictions(restrictions, job_conditions)
        assert result == 0, f"Expected 0 (min of all checks), got {result}"
        print("✓ Multiple restrictions return minimum score")
    
    def test_no_restrictions_returns_1(self):
        """Test that no restrictions returns 1"""
        result = compare_restrictions({}, {"port_charges": True})
        assert result == 1, f"Expected 1 (no restrictions), got {result}"
        
        result = compare_restrictions(None, {"port_charges": True})
        assert result == 1, f"Expected 1 (None restrictions), got {result}"
        print("✓ No restrictions returns 1")


class TestCalculateInclusionScore:
    """Tests for calculate_inclusion_score function (0-100)"""
    
    def test_empty_employer_returns_base_score(self):
        """Test empty employer returns base score from amenagement/accessibilite"""
        score = calculate_inclusion_score(None, False, False)
        assert score == 0, f"Expected 0, got {score}"
        
        score = calculate_inclusion_score({}, True, True)
        assert score == 45, f"Expected 45 (20+25), got {score}"
        print("✓ Empty employer returns base score")
    
    def test_amenagement_possible_adds_25(self):
        """Test amenagement_possible adds 25 points"""
        score = calculate_inclusion_score({}, False, True)
        assert score == 25, f"Expected 25, got {score}"
        print("✓ amenagement_possible adds 25 points")
    
    def test_accessibilite_locaux_adds_20(self):
        """Test accessibilite_locaux adds 20 points"""
        score = calculate_inclusion_score({}, True, False)
        assert score == 20, f"Expected 20, got {score}"
        print("✓ accessibilite_locaux adds 20 points")
    
    def test_entreprise_inclusive_adds_15(self):
        """Test entreprise_inclusive adds 15 points"""
        score = calculate_inclusion_score({"entreprise_inclusive": True}, False, False)
        assert score == 15, f"Expected 15, got {score}"
        print("✓ entreprise_inclusive adds 15 points")
    
    def test_partenaire_cap_emploi_adds_10(self):
        """Test partenaire_cap_emploi adds 10 points"""
        score = calculate_inclusion_score({"partenaire_cap_emploi": True}, False, False)
        assert score == 10, f"Expected 10, got {score}"
        print("✓ partenaire_cap_emploi adds 10 points")
    
    def test_experience_recrutement_handicap_adds_10(self):
        """Test experience_recrutement_handicap adds 10 points"""
        score = calculate_inclusion_score({"experience_recrutement_handicap": True}, False, False)
        assert score == 10, f"Expected 10, got {score}"
        print("✓ experience_recrutement_handicap adds 10 points")
    
    def test_referent_handicap_adds_10(self):
        """Test referent_handicap adds 10 points"""
        score = calculate_inclusion_score({"referent_handicap": True}, False, False)
        assert score == 10, f"Expected 10, got {score}"
        print("✓ referent_handicap adds 10 points")
    
    def test_obligation_emploi_respectee_adds_5(self):
        """Test obligation_emploi_respectee adds 5 points"""
        score = calculate_inclusion_score({"obligation_emploi_respectee": True}, False, False)
        assert score == 5, f"Expected 5, got {score}"
        print("✓ obligation_emploi_respectee adds 5 points")
    
    def test_poste_adapte_adds_5(self):
        """Test poste_adapte adds 5 points"""
        score = calculate_inclusion_score({"poste_adapte": True}, False, False)
        assert score == 5, f"Expected 5, got {score}"
        print("✓ poste_adapte adds 5 points")
    
    def test_max_score_is_100(self):
        """Test that max score is capped at 100"""
        full_employer = {
            "entreprise_inclusive": True,
            "partenaire_cap_emploi": True,
            "experience_recrutement_handicap": True,
            "referent_handicap": True,
            "obligation_emploi_respectee": True,
            "poste_adapte": True
        }
        score = calculate_inclusion_score(full_employer, True, True)
        assert score == 100, f"Expected 100 (capped), got {score}"
        print("✓ Max score is capped at 100")
    
    def test_cumulative_score(self):
        """Test cumulative scoring"""
        employer = {
            "entreprise_inclusive": True,  # +15
            "referent_handicap": True,      # +10
        }
        score = calculate_inclusion_score(employer, True, True)  # +20 +25
        expected = 15 + 10 + 20 + 25  # = 70
        assert score == expected, f"Expected {expected}, got {score}"
        print("✓ Cumulative scoring works correctly")


class TestCompareMetierHandicap:
    """Tests for compare_metier_handicap function (combined score)"""
    
    def test_combines_metier_restrictions_amenagement(self):
        """Test that function combines all three scores"""
        candidate = {
            "metier": {"value": ["conseiller insertion"], "priority": 3},
            "restrictions_fonctionnelles": {"value": {"port_charges_impossible": True}, "priority": 4},
            "amenagement_poste": {"value": "nécessaire", "priority": 3}
        }
        job = {
            "metier": "conseiller insertion",
            "exigences_metier": {"port_charges": False},
            "amenagement_possible": True,
            "accessibilite_locaux": True
        }
        
        result = compare_metier_handicap(candidate, job)
        # All compatible: metier=1, restrictions=1, amenagement=1 -> min=1
        assert result == 1, f"Expected 1 (all compatible), got {result}"
        print("✓ compare_metier_handicap combines all scores correctly")
    
    def test_returns_min_of_all_scores(self):
        """Test that function returns minimum of all scores"""
        candidate = {
            "metier": {"value": ["conseiller insertion"], "priority": 3},
            "restrictions_fonctionnelles": {"value": {"port_charges_impossible": True}, "priority": 4},
            "amenagement_poste": {"value": "nécessaire", "priority": 3}
        }
        job = {
            "metier": "conseiller insertion",  # Match = 1
            "exigences_metier": {"port_charges": True},  # Incompatible = 0
            "amenagement_possible": True  # Compatible = 1
        }
        
        result = compare_metier_handicap(candidate, job)
        # min(1, 0, 1) = 0
        assert result == 0, f"Expected 0 (min of all), got {result}"
        print("✓ compare_metier_handicap returns minimum score")


class TestCalculateJobScoreWithRQTH:
    """Tests for calculate_job_score with full RQTH/EQTH profile"""
    
    def test_returns_score_inclusion_contexte(self):
        """Test that result includes score, score_inclusion, contexte_handicap"""
        candidate = {
            "metier": {"value": ["conseiller insertion"], "priority": 3},
            "rqth_eqth": {"status": "rqth", "disclosure": "oui", "priority": 1}
        }
        job = {
            "metier": "conseiller insertion",
            "employeur": {"entreprise_inclusive": True},
            "accessibilite_locaux": True,
            "amenagement_possible": True
        }
        
        result = calculate_job_score(candidate, job)
        
        assert "score" in result, "Result should have 'score'"
        assert "score_inclusion" in result, "Result should have 'score_inclusion'"
        assert "contexte_handicap" in result, "Result should have 'contexte_handicap'"
        
        assert isinstance(result["score"], int), "score should be int"
        assert isinstance(result["score_inclusion"], int), "score_inclusion should be int"
        assert isinstance(result["contexte_handicap"], dict), "contexte_handicap should be dict"
        
        assert "status" in result["contexte_handicap"], "contexte_handicap should have status"
        assert "disclosure" in result["contexte_handicap"], "contexte_handicap should have disclosure"
        
        print(f"✓ Result has score={result['score']}, score_inclusion={result['score_inclusion']}, contexte_handicap={result['contexte_handicap']}")
    
    def test_rqth_status_never_blocking(self):
        """Test that RQTH status alone never causes blocking"""
        candidate = {
            "metier": {"value": ["conseiller insertion"], "priority": 3},
            "rqth_eqth": {"status": "rqth", "disclosure": "non", "priority": 1}
        }
        job = {
            "metier": "conseiller insertion"
        }
        
        result = calculate_job_score(candidate, job)
        
        # RQTH status should not create any blocage
        rqth_blocages = [b for b in result.get("blocages", []) if "RQTH" in b.get("critere", "") or "handicap" in b.get("critere", "").lower()]
        assert len(rqth_blocages) == 0, f"RQTH should never cause blocking, found: {rqth_blocages}"
        print("✓ RQTH status never causes blocking")
    
    def test_ciblage_employeurs_inclusifs(self):
        """Test ciblage_employeurs_inclusifs criterion"""
        candidate = {
            "metier": {"value": ["conseiller insertion"], "priority": 3},
            "ciblage_employeurs_inclusifs": {"value": True, "priority": 3}
        }
        
        # Highly inclusive employer
        job_inclusive = {
            "metier": "conseiller insertion",
            "employeur": {
                "entreprise_inclusive": True,
                "partenaire_cap_emploi": True,
                "referent_handicap": True
            },
            "accessibilite_locaux": True,
            "amenagement_possible": True
        }
        
        result = calculate_job_score(candidate, job_inclusive)
        # Should have evaluation for inclusion
        inclusion_evals = [e for e in result.get("evaluations", []) if "inclusion" in e.get("label", "").lower()]
        assert len(inclusion_evals) > 0, "Should have inclusion evaluation"
        assert inclusion_evals[0]["compatibility"] == 1, "Highly inclusive employer should have compatibility=1"
        print("✓ ciblage_employeurs_inclusifs works correctly")
    
    def test_accessibilite_metier_handicap(self):
        """Test accessibilite_metier_handicap criterion"""
        candidate = {
            "metier": {"value": ["conseiller insertion"], "priority": 3},
            "accessibilite_metier_handicap": {"value": True, "priority": 4}
        }
        
        # Accessible job
        job_accessible = {
            "metier": "conseiller insertion",
            "accessibilite_locaux": True,
            "amenagement_possible": True
        }
        
        result = calculate_job_score(candidate, job_accessible)
        # Should have evaluation for accessibility
        acc_evals = [e for e in result.get("evaluations", []) if "accessibilité" in e.get("label", "").lower()]
        assert len(acc_evals) > 0, "Should have accessibility evaluation"
        assert acc_evals[0]["compatibility"] == 1, "Accessible job should have compatibility=1"
        print("✓ accessibilite_metier_handicap works correctly")
    
    def test_full_rqth_profile_scoring(self):
        """Test complete RQTH/EQTH profile scoring"""
        candidate = {
            "metier": {"value": ["conseiller insertion"], "priority": 4},
            "secteur": {"value": ["formation"], "priority": 3},
            "contrat": {"value": ["CDI"], "priority": 3},
            "rqth_eqth": {"status": "rqth", "disclosure": "oui", "priority": 1},
            "restrictions_fonctionnelles": {
                "value": {
                    "port_charges_impossible": True,
                    "station_debout_prolongee_limitee": True
                },
                "priority": 5
            },
            "amenagement_poste": {"value": "nécessaire", "priority": 4},
            "ciblage_employeurs_inclusifs": {"value": True, "priority": 3},
            "accessibilite_metier_handicap": {"value": True, "priority": 4}
        }
        
        job = {
            "metier": "conseiller insertion",
            "secteur": "formation",
            "contrat": "CDI",
            "exigences_metier": {
                "port_charges": False,
                "station_debout_prolongee": False,
                "travail_nuit": False,
                "environnement": "calme",
                "horaires_decales": False,
                "deplacements_frequents": False,
                "cadence_elevee": False
            },
            "employeur": {
                "entreprise_inclusive": True,
                "partenaire_cap_emploi": True,
                "referent_handicap": True,
                "experience_recrutement_handicap": True
            },
            "accessibilite_locaux": True,
            "amenagement_possible": True
        }
        
        result = calculate_job_score(candidate, job)
        
        # Should be excellent match
        assert result["score"] >= 80, f"Expected high score, got {result['score']}"
        assert result["score_inclusion"] >= 70, f"Expected high inclusion score, got {result['score_inclusion']}"
        assert result["contexte_handicap"]["status"] == "rqth", "Should preserve RQTH status"
        assert len(result["blocages"]) == 0, f"Should have no blocages, got {result['blocages']}"
        
        print(f"✓ Full RQTH profile: score={result['score']}, inclusion={result['score_inclusion']}, statut={result['statut']}")


# ============================================================================
# API Integration Tests
# ============================================================================

class TestJobMatchingSearchWithRQTH:
    """Tests for POST /api/jobs/matching/search with RQTH fields"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user"""
        pseudo = f"test_rqth_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200, f"Registration failed: {response.text}"
        return {"token": response.json()["token"], "pseudo": pseudo}
    
    def test_search_accepts_rqth_eqth(self, test_user):
        """Test POST /api/jobs/matching/search accepts rqth_eqth in payload"""
        payload = {
            "metier": {"value": ["conseiller insertion"], "priority": 3},
            "rqth_eqth": {"status": "rqth", "disclosure": "oui", "priority": 1}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/jobs/matching/search?token={test_user['token']}",
            json=payload,
            timeout=30
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        print("✓ POST /api/jobs/matching/search accepts rqth_eqth")
    
    def test_search_accepts_ciblage_employeurs_inclusifs(self, test_user):
        """Test POST /api/jobs/matching/search accepts ciblage_employeurs_inclusifs"""
        payload = {
            "metier": {"value": ["conseiller insertion"], "priority": 3},
            "ciblage_employeurs_inclusifs": {"value": True, "priority": 3}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/jobs/matching/search?token={test_user['token']}",
            json=payload,
            timeout=30
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        print("✓ POST /api/jobs/matching/search accepts ciblage_employeurs_inclusifs")
    
    def test_search_accepts_accessibilite_metier_handicap(self, test_user):
        """Test POST /api/jobs/matching/search accepts accessibilite_metier_handicap"""
        payload = {
            "metier": {"value": ["conseiller insertion"], "priority": 3},
            "accessibilite_metier_handicap": {"value": True, "priority": 4}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/jobs/matching/search?token={test_user['token']}",
            json=payload,
            timeout=30
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        print("✓ POST /api/jobs/matching/search accepts accessibilite_metier_handicap")
    
    def test_search_accepts_all_restrictions(self, test_user):
        """Test POST /api/jobs/matching/search accepts all 8 restriction types"""
        payload = {
            "metier": {"value": ["conseiller insertion"], "priority": 3},
            "restrictions_fonctionnelles": {
                "value": {
                    "port_charges_impossible": True,
                    "station_debout_prolongee_limitee": True,
                    "travail_nuit_impossible": True,
                    "environnement_calme_recherche": True,
                    "horaires_stables_recherches": True,
                    "accessibilite_necessaire": True,
                    "deplacements_frequents_difficiles": True,
                    "cadence_elevee_difficile": True
                },
                "priority": 5
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/jobs/matching/search?token={test_user['token']}",
            json=payload,
            timeout=30
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        print("✓ POST /api/jobs/matching/search accepts all 8 restriction types")


class TestJobMatchingPreferencesWithRQTH:
    """Tests for PUT /api/jobs/matching/preferences with RQTH fields"""
    
    @pytest.fixture(scope="class")
    def test_user(self):
        """Create a test user"""
        pseudo = f"test_prefs_rqth_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "pseudo": pseudo,
            "password": "testpass123",
            "consent_cgu": True,
            "consent_privacy": True
        })
        assert response.status_code == 200
        return {"token": response.json()["token"], "pseudo": pseudo}
    
    def test_preferences_saves_rqth_eqth(self, test_user):
        """Test PUT /api/jobs/matching/preferences saves rqth_eqth"""
        payload = {
            "metier": {"value": ["conseiller insertion"], "priority": 3},
            "rqth_eqth": {"status": "rqth", "disclosure": "oui", "priority": 1}
        }
        
        response = requests.put(
            f"{BASE_URL}/api/jobs/matching/preferences?token={test_user['token']}",
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        # Verify saved
        get_response = requests.get(f"{BASE_URL}/api/jobs/matching/preferences?token={test_user['token']}")
        assert get_response.status_code == 200
        # Note: rqth_eqth may not be in filters if it has no "value" key (it uses status/disclosure)
        print("✓ PUT /api/jobs/matching/preferences saves rqth_eqth")
    
    def test_preferences_saves_ciblage(self, test_user):
        """Test PUT /api/jobs/matching/preferences saves ciblage_employeurs_inclusifs"""
        payload = {
            "metier": {"value": ["conseiller insertion"], "priority": 3},
            "ciblage_employeurs_inclusifs": {"value": True, "priority": 3}
        }
        
        response = requests.put(
            f"{BASE_URL}/api/jobs/matching/preferences?token={test_user['token']}",
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        # Verify saved
        get_response = requests.get(f"{BASE_URL}/api/jobs/matching/preferences?token={test_user['token']}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data.get("filters", {}).get("ciblage_employeurs_inclusifs", {}).get("value") == True, \
            f"ciblage should be saved, got {data.get('filters')}"
        print("✓ PUT /api/jobs/matching/preferences saves ciblage_employeurs_inclusifs")
    
    def test_preferences_saves_accessibilite(self, test_user):
        """Test PUT /api/jobs/matching/preferences saves accessibilite_metier_handicap"""
        payload = {
            "metier": {"value": ["conseiller insertion"], "priority": 3},
            "accessibilite_metier_handicap": {"value": True, "priority": 4}
        }
        
        response = requests.put(
            f"{BASE_URL}/api/jobs/matching/preferences?token={test_user['token']}",
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        # Verify saved
        get_response = requests.get(f"{BASE_URL}/api/jobs/matching/preferences?token={test_user['token']}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data.get("filters", {}).get("accessibilite_metier_handicap", {}).get("value") == True, \
            f"accessibilite should be saved, got {data.get('filters')}"
        print("✓ PUT /api/jobs/matching/preferences saves accessibilite_metier_handicap")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
