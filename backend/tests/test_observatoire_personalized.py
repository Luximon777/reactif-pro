"""
Test Observatoire Personalized Features
- Tab 'Prédictions' personalized predictions
- Tab 'Détectées CV' personalized emerging skills
- GET /api/emerging/observatory endpoint
- GET /api/observatoire/personalized endpoint
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestObservatoirePersonalized:
    """Test personalized observatoire features for testboost user"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get token for testboost user"""
        # Login with testboost user (pseudo auth)
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"pseudo": "testboost", "password": "Solerys777!"},
            timeout=30
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        data = login_response.json()
        self.token = data.get("token")
        assert self.token, "No token returned from login"
        print(f"Logged in as testboost, token: {self.token[:20]}...")
    
    def test_01_observatoire_dashboard_loads(self):
        """Test that observatoire dashboard loads with global data"""
        response = requests.get(
            f"{BASE_URL}/api/observatoire/dashboard",
            timeout=30
        )
        assert response.status_code == 200, f"Dashboard failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "emerging_skills" in data, "Missing emerging_skills"
        assert "sector_trends" in data, "Missing sector_trends"
        assert "indicators" in data, "Missing indicators"
        
        print(f"Dashboard loaded: {len(data['emerging_skills'])} emerging skills, {len(data['sector_trends'])} sector trends")
        print(f"Indicators: {data['indicators']}")
    
    def test_02_emerging_observatory_endpoint(self):
        """Test GET /api/emerging/observatory - CV detected emerging skills"""
        response = requests.get(
            f"{BASE_URL}/api/emerging/observatory?token={self.token}",
            timeout=60  # Long timeout for AI analysis
        )
        assert response.status_code == 200, f"Emerging observatory failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "top_emerging" in data, "Missing top_emerging"
        assert "by_category" in data, "Missing by_category"
        assert "by_level" in data, "Missing by_level"
        
        print(f"CV Detected emerging skills: {len(data['top_emerging'])} skills")
        if data['top_emerging']:
            for skill in data['top_emerging'][:5]:
                print(f"  - {skill.get('name')}: score={skill.get('score_emergence')}, category={skill.get('category')}")
        
        print(f"By category: {data['by_category']}")
        print(f"By level: {data['by_level']}")
        
        # For testboost user, should have some emerging skills detected
        # (based on context: "4 for testboost")
        assert isinstance(data['top_emerging'], list), "top_emerging should be a list"
    
    def test_03_observatoire_personalized_endpoint(self):
        """Test GET /api/observatoire/personalized - personalized predictions"""
        response = requests.get(
            f"{BASE_URL}/api/observatoire/personalized?token={self.token}",
            timeout=90  # Very long timeout for GPT-5.2 analysis
        )
        assert response.status_code == 200, f"Personalized observatoire failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "has_cv" in data, "Missing has_cv field"
        
        if data.get("has_cv"):
            # User has CV data - should have personalized results
            assert "matches" in data, "Missing matches"
            assert "skill_gaps" in data, "Missing skill_gaps"
            assert "sector_relevance" in data, "Missing sector_relevance"
            assert "summary" in data, "Missing summary"
            
            print(f"Personalized data for user with CV:")
            print(f"  - User skills count: {data.get('user_skills_count', 0)}")
            print(f"  - Matches: {len(data.get('matches', []))}")
            print(f"  - Skill gaps: {len(data.get('skill_gaps', []))}")
            print(f"  - Sector relevance: {len(data.get('sector_relevance', []))}")
            print(f"  - Summary: {data.get('summary', {})}")
            
            # Check sector_relevance structure (for Predictions tab)
            if data.get('sector_relevance'):
                for sr in data['sector_relevance'][:3]:
                    print(f"  Sector: {sr.get('sector')}")
                    print(f"    - Hiring trend: {sr.get('hiring_trend')}")
                    print(f"    - Your emerging skills: {sr.get('your_emerging_skills', [])}")
                    print(f"    - Your declining skills: {sr.get('your_declining_skills', [])}")
        else:
            # User doesn't have CV - should get message
            print(f"User has no CV: {data.get('message', 'No message')}")
            assert "message" in data, "Should have message for users without CV"
    
    def test_04_observatoire_predictions_global(self):
        """Test GET /api/observatoire/predictions - global predictions"""
        response = requests.get(
            f"{BASE_URL}/api/observatoire/predictions",
            timeout=30
        )
        assert response.status_code == 200, f"Predictions failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Predictions should be a list"
        print(f"Global predictions: {len(data)} items")
        if data:
            for pred in data[:3]:
                print(f"  - {pred.get('skill')} in {pred.get('sector')}: {pred.get('demand_change')} by {pred.get('horizon')}")
    
    def test_05_sector_trends(self):
        """Test GET /api/observatoire/sector-trends"""
        response = requests.get(
            f"{BASE_URL}/api/observatoire/sector-trends",
            timeout=30
        )
        assert response.status_code == 200, f"Sector trends failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Sector trends should be a list"
        print(f"Sector trends: {len(data)} sectors")
        if data:
            for trend in data[:3]:
                print(f"  - {trend.get('sector_name')}: transformation={trend.get('transformation_index')}, hiring={trend.get('hiring_trend')}")
                print(f"    Emerging: {trend.get('emerging_skills', [])[:3]}")
                print(f"    Declining: {trend.get('declining_skills', [])[:3]}")


class TestObservatoireWithBob30:
    """Test with bob30 user who has CV uploaded"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get token for bob30 user"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"pseudo": "bob30", "password": "Solerys777!"},
            timeout=30
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        data = login_response.json()
        self.token = data.get("token")
        assert self.token, "No token returned from login"
        print(f"Logged in as bob30, token: {self.token[:20]}...")
    
    def test_01_emerging_observatory_bob30(self):
        """Test CV detected emerging skills for bob30 (has CV)"""
        response = requests.get(
            f"{BASE_URL}/api/emerging/observatory?token={self.token}",
            timeout=60
        )
        assert response.status_code == 200, f"Emerging observatory failed: {response.text}"
        data = response.json()
        
        print(f"Bob30 CV Detected: {len(data.get('top_emerging', []))} emerging skills")
        if data.get('top_emerging'):
            for skill in data['top_emerging'][:5]:
                print(f"  - {skill.get('name')}: score={skill.get('score_emergence')}")
    
    def test_02_personalized_observatoire_bob30(self):
        """Test personalized observatoire for bob30"""
        response = requests.get(
            f"{BASE_URL}/api/observatoire/personalized?token={self.token}",
            timeout=90
        )
        assert response.status_code == 200, f"Personalized failed: {response.text}"
        data = response.json()
        
        print(f"Bob30 has_cv: {data.get('has_cv')}")
        if data.get('has_cv'):
            print(f"  - Matches: {len(data.get('matches', []))}")
            print(f"  - Sector relevance: {len(data.get('sector_relevance', []))}")
            
            # Verify sector_relevance has the expected structure for Predictions tab
            for sr in data.get('sector_relevance', [])[:2]:
                assert 'sector' in sr, "sector_relevance should have 'sector' field"
                assert 'hiring_trend' in sr, "sector_relevance should have 'hiring_trend' field"
                print(f"  Sector: {sr.get('sector')} - {sr.get('hiring_trend')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
