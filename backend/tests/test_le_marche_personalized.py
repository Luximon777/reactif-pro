"""
Test suite for Le Marché personalized features:
- POST /api/marche-cache/diagnostic - AI diagnostic for hidden job market
- GET /api/referentiel/explorer/suggestions - Personalized job suggestions
- GET /api/evolution-index/user-profile - Enhanced evolution data with passport
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
MIKE7_CREDS = {"pseudo": "mike7", "password": "Solerys777!"}


class TestLeMarchePersonalized:
    """Tests for Le Marché personalized features"""
    
    @pytest.fixture(scope="class")
    def mike7_token(self):
        """Login as mike7 and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=MIKE7_CREDS)
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["token"]
    
    # ============== EVOLUTION INDEX USER PROFILE ==============
    
    def test_evolution_index_user_profile_returns_200(self, mike7_token):
        """GET /api/evolution-index/user-profile returns 200 with valid token"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/user-profile?token={mike7_token}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_evolution_index_user_profile_has_required_fields(self, mike7_token):
        """Response contains all required fields for personalized display"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/user-profile?token={mike7_token}")
        data = response.json()
        
        # Check required fields
        assert "has_cv" in data, "Missing has_cv field"
        assert "profile_sectors" in data, "Missing profile_sectors field"
        assert "profile_skills" in data, "Missing profile_skills field"
        assert "evolution_exposure" in data, "Missing evolution_exposure field"
        assert "exposure_interpretation" in data, "Missing exposure_interpretation field"
        assert "relevant_jobs" in data, "Missing relevant_jobs field"
        
        # Check exposure_interpretation structure
        interp = data["exposure_interpretation"]
        assert "level" in interp, "Missing level in exposure_interpretation"
        assert "label" in interp, "Missing label in exposure_interpretation"
        assert "description" in interp, "Missing description in exposure_interpretation"
        assert "recommendation" in interp, "Missing recommendation in exposure_interpretation"
    
    def test_evolution_index_user_profile_has_cv_data(self, mike7_token):
        """Mike7 has CV data so has_cv should be True"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/user-profile?token={mike7_token}")
        data = response.json()
        
        assert data["has_cv"] == True, "Mike7 should have CV data"
        assert len(data["profile_skills"]) > 0, "Mike7 should have skills"
        assert len(data["profile_sectors"]) > 0, "Mike7 should have sectors"
    
    def test_evolution_index_user_profile_has_passport_data(self, mike7_token):
        """Response includes passport-derived data"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/user-profile?token={mike7_token}")
        data = response.json()
        
        # Check for emerging_from_cv (derived from passport/CV skills)
        assert "emerging_from_cv" in data, "Missing emerging_from_cv field"
        assert "data_sources" in data, "Missing data_sources field"
        
        # Check data_sources structure
        sources = data["data_sources"]
        assert "cv_analysis" in sources, "Missing cv_analysis in data_sources"
        assert "passport" in sources, "Missing passport in data_sources"
    
    def test_evolution_index_user_profile_evolution_exposure_valid(self, mike7_token):
        """Evolution exposure is a valid number between 0-100"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/user-profile?token={mike7_token}")
        data = response.json()
        
        exposure = data["evolution_exposure"]
        assert isinstance(exposure, (int, float)), "evolution_exposure should be numeric"
        assert 0 <= exposure <= 100, f"evolution_exposure should be 0-100, got {exposure}"
    
    def test_evolution_index_user_profile_invalid_token(self):
        """Returns 401 for invalid token"""
        response = requests.get(f"{BASE_URL}/api/evolution-index/user-profile?token=invalid_token_xyz")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    # ============== EXPLORER SUGGESTIONS ==============
    
    def test_explorer_suggestions_returns_200(self, mike7_token):
        """GET /api/referentiel/explorer/suggestions returns 200"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/suggestions?token={mike7_token}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_explorer_suggestions_has_required_fields(self, mike7_token):
        """Response contains all required fields"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/suggestions?token={mike7_token}")
        data = response.json()
        
        assert "has_profile" in data, "Missing has_profile field"
        assert "suggestions" in data, "Missing suggestions field"
        assert "skills_count" in data, "Missing skills_count field"
        assert "sectors" in data, "Missing sectors field"
    
    def test_explorer_suggestions_has_profile_for_mike7(self, mike7_token):
        """Mike7 has profile data so has_profile should be True"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/suggestions?token={mike7_token}")
        data = response.json()
        
        assert data["has_profile"] == True, "Mike7 should have profile data"
        assert data["skills_count"] > 0, "Mike7 should have skills"
    
    def test_explorer_suggestions_returns_suggestions(self, mike7_token):
        """Returns personalized job suggestions"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/suggestions?token={mike7_token}")
        data = response.json()
        
        suggestions = data["suggestions"]
        assert isinstance(suggestions, list), "suggestions should be a list"
        assert len(suggestions) > 0, "Should return at least one suggestion"
        
        # Check suggestion structure
        for s in suggestions:
            assert "name" in s, "Suggestion missing name"
            assert "reason" in s, "Suggestion missing reason"
    
    def test_explorer_suggestions_reasons_are_personalized(self, mike7_token):
        """Suggestion reasons reference user's profile"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/suggestions?token={mike7_token}")
        data = response.json()
        
        suggestions = data["suggestions"]
        reasons = [s["reason"] for s in suggestions]
        
        # At least some reasons should be personalized (not generic)
        personalized_keywords = ["Votre", "votre", "Basé sur", "Lié à", "Secteur", "Métier en"]
        has_personalized = any(
            any(kw in reason for kw in personalized_keywords)
            for reason in reasons
        )
        assert has_personalized, f"Suggestions should have personalized reasons: {reasons}"
    
    def test_explorer_suggestions_invalid_token(self):
        """Returns 401 for invalid token"""
        response = requests.get(f"{BASE_URL}/api/referentiel/explorer/suggestions?token=invalid_token_xyz")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    # ============== MARCHE CACHE DIAGNOSTIC ==============
    
    def test_marche_cache_diagnostic_returns_200(self, mike7_token):
        """POST /api/marche-cache/diagnostic returns 200"""
        response = requests.post(
            f"{BASE_URL}/api/marche-cache/diagnostic",
            json={"token": mike7_token},
            timeout=90  # AI takes ~30 seconds
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    def test_marche_cache_diagnostic_has_required_fields(self, mike7_token):
        """Response contains diagnostic with all required fields"""
        response = requests.post(
            f"{BASE_URL}/api/marche-cache/diagnostic",
            json={"token": mike7_token},
            timeout=90
        )
        data = response.json()
        
        assert "diagnostic" in data, "Missing diagnostic field"
        
        diag = data["diagnostic"]
        assert "score_acces" in diag, "Missing score_acces"
        assert "analyse" in diag, "Missing analyse"
        assert "forces_marche_cache" in diag, "Missing forces_marche_cache"
        assert "faiblesses" in diag, "Missing faiblesses"
        assert "recommandations" in diag, "Missing recommandations"
        assert "canaux_privilegier" in diag, "Missing canaux_privilegier"
        assert "types_entreprises" in diag, "Missing types_entreprises"
        assert "strategie_reseau" in diag, "Missing strategie_reseau"
    
    def test_marche_cache_diagnostic_score_valid(self, mike7_token):
        """Score is between 1-10"""
        response = requests.post(
            f"{BASE_URL}/api/marche-cache/diagnostic",
            json={"token": mike7_token},
            timeout=90
        )
        data = response.json()
        
        score = data["diagnostic"]["score_acces"]
        assert isinstance(score, int), "score_acces should be integer"
        assert 1 <= score <= 10, f"score_acces should be 1-10, got {score}"
    
    def test_marche_cache_diagnostic_recommandations_structure(self, mike7_token):
        """Recommandations have correct structure"""
        response = requests.post(
            f"{BASE_URL}/api/marche-cache/diagnostic",
            json={"token": mike7_token},
            timeout=90
        )
        data = response.json()
        
        recos = data["diagnostic"]["recommandations"]
        assert isinstance(recos, list), "recommandations should be a list"
        assert len(recos) > 0, "Should have at least one recommendation"
        
        for r in recos:
            assert "titre" in r, "Recommendation missing titre"
            assert "description" in r, "Recommendation missing description"
            assert "priorite" in r, "Recommendation missing priorite"
            assert r["priorite"] in ["haute", "moyenne", "basse"], f"Invalid priorite: {r['priorite']}"
    
    def test_marche_cache_diagnostic_invalid_token(self):
        """Returns 401 for invalid token"""
        response = requests.post(
            f"{BASE_URL}/api/marche-cache/diagnostic",
            json={"token": "invalid_token_xyz"},
            timeout=30
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
