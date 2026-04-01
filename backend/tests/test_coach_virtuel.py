"""
Test Coach Virtuel API - GET /api/coach/progress
Tests the virtual coach progress endpoint that returns user journey steps
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCoachVirtuelAPI:
    """Tests for the Coach Virtuel progress endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures - login as testboost user"""
        # Login to get token
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"pseudo": "testboost", "password": "Solerys777!"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.token = login_response.json()["token"]
        self.role = login_response.json()["role"]
    
    def test_coach_progress_returns_required_fields(self):
        """Test that /api/coach/progress returns all required fields"""
        response = requests.get(f"{BASE_URL}/api/coach/progress?token={self.token}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Check all required top-level fields
        assert "steps" in data, "Missing 'steps' field"
        assert "completed" in data, "Missing 'completed' field"
        assert "total" in data, "Missing 'total' field"
        assert "current_step" in data, "Missing 'current_step' field"
        assert "progress_pct" in data, "Missing 'progress_pct' field"
        assert "message" in data, "Missing 'message' field"
        assert "emoji" in data, "Missing 'emoji' field"
        
        # Validate types
        assert isinstance(data["steps"], list), "steps should be a list"
        assert isinstance(data["completed"], int), "completed should be an int"
        assert isinstance(data["total"], int), "total should be an int"
        assert isinstance(data["current_step"], int), "current_step should be an int"
        assert isinstance(data["progress_pct"], (int, float)), "progress_pct should be numeric"
        assert isinstance(data["message"], str), "message should be a string"
        
    def test_coach_progress_has_4_steps(self):
        """Test that coach returns exactly 4 steps"""
        response = requests.get(f"{BASE_URL}/api/coach/progress?token={self.token}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["steps"]) == 4, f"Expected 4 steps, got {len(data['steps'])}"
        assert data["total"] == 4, f"Expected total=4, got {data['total']}"
        
    def test_coach_step_structure(self):
        """Test that each step has required fields"""
        response = requests.get(f"{BASE_URL}/api/coach/progress?token={self.token}")
        
        assert response.status_code == 200
        data = response.json()
        
        required_step_fields = ["id", "title", "description", "complete", "partial", 
                                "action_label", "action_path", "action_type", "details"]
        
        for step in data["steps"]:
            for field in required_step_fields:
                assert field in step, f"Step {step.get('id', '?')} missing field '{field}'"
            
            # Validate step id is 1-4
            assert step["id"] in [1, 2, 3, 4], f"Invalid step id: {step['id']}"
            
            # Validate complete and partial are booleans
            assert isinstance(step["complete"], bool), f"Step {step['id']} complete should be bool"
            assert isinstance(step["partial"], bool), f"Step {step['id']} partial should be bool"
    
    def test_testboost_step3_cv_complete(self):
        """Test that for testboost user, Step 3 (CV) is complete"""
        response = requests.get(f"{BASE_URL}/api/coach/progress?token={self.token}")
        
        assert response.status_code == 200
        data = response.json()
        
        step3 = next((s for s in data["steps"] if s["id"] == 3), None)
        assert step3 is not None, "Step 3 not found"
        assert step3["complete"] == True, f"Step 3 should be complete for testboost, got {step3['complete']}"
        assert step3["title"] == "Valoriser vos compétences", f"Step 3 title mismatch"
        assert step3["details"]["has_cv"] == True, "testboost should have CV"
        
    def test_testboost_step1_dclic_not_complete(self):
        """Test that for testboost user, Step 1 (D'CLIC) is NOT complete"""
        response = requests.get(f"{BASE_URL}/api/coach/progress?token={self.token}")
        
        assert response.status_code == 200
        data = response.json()
        
        step1 = next((s for s in data["steps"] if s["id"] == 1), None)
        assert step1 is not None, "Step 1 not found"
        assert step1["complete"] == False, f"Step 1 should NOT be complete for testboost, got {step1['complete']}"
        assert step1["title"] == "Découvrir votre personnalité", f"Step 1 title mismatch"
        assert step1["action_label"] == "Importer D'CLIC PRO", "Step 1 should have action label"
        assert step1["action_type"] == "dclic", "Step 1 action_type should be 'dclic'"
        
    def test_current_step_is_first_incomplete(self):
        """Test that current_step points to first incomplete step"""
        response = requests.get(f"{BASE_URL}/api/coach/progress?token={self.token}")
        
        assert response.status_code == 200
        data = response.json()
        
        # For testboost, step 1 is not complete, so current_step should be 1
        assert data["current_step"] == 1, f"Expected current_step=1, got {data['current_step']}"
        
        # Verify step 1 is indeed not complete
        step1 = next((s for s in data["steps"] if s["id"] == 1), None)
        assert step1["complete"] == False, "Step 1 should not be complete"
        
    def test_progress_percentage_calculation(self):
        """Test that progress_pct is correctly calculated"""
        response = requests.get(f"{BASE_URL}/api/coach/progress?token={self.token}")
        
        assert response.status_code == 200
        data = response.json()
        
        # For testboost: 1 step complete out of 4 = 25%
        expected_pct = round((data["completed"] / data["total"]) * 100)
        assert data["progress_pct"] == expected_pct, f"Expected {expected_pct}%, got {data['progress_pct']}%"
        
    def test_contextual_message_for_step1(self):
        """Test that message is contextual based on current step"""
        response = requests.get(f"{BASE_URL}/api/coach/progress?token={self.token}")
        
        assert response.status_code == 200
        data = response.json()
        
        # For testboost at step 1, message should mention D'CLIC PRO
        assert "D'CLIC PRO" in data["message"], f"Message should mention D'CLIC PRO for step 1"
        assert data["emoji"] == "wave", f"Expected emoji 'wave' for step 1, got {data['emoji']}"
        
    def test_step_titles_in_french(self):
        """Test that all step titles are in French as expected"""
        response = requests.get(f"{BASE_URL}/api/coach/progress?token={self.token}")
        
        assert response.status_code == 200
        data = response.json()
        
        expected_titles = [
            "Découvrir votre personnalité",
            "Ce qui fait sens pour vous",
            "Valoriser vos compétences",
            "Explorer le marché"
        ]
        
        for i, step in enumerate(data["steps"]):
            assert step["title"] == expected_titles[i], f"Step {i+1} title mismatch"


class TestCoachVirtuelWithDclic:
    """Tests for user with D'CLIC imported (bob23)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures - login as bob23 user who has D'CLIC"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"pseudo": "bob23", "password": "Solerys777!"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.token = login_response.json()["token"]
        
    def test_bob23_step1_dclic_complete(self):
        """Test that for bob23 user, Step 1 (D'CLIC) IS complete"""
        response = requests.get(f"{BASE_URL}/api/coach/progress?token={self.token}")
        
        assert response.status_code == 200
        data = response.json()
        
        step1 = next((s for s in data["steps"] if s["id"] == 1), None)
        assert step1 is not None, "Step 1 not found"
        assert step1["complete"] == True, f"Step 1 should be complete for bob23, got {step1['complete']}"
        
        # bob23 has D'CLIC details
        assert step1["details"]["disc"] is not None, "bob23 should have DISC label"


class TestCoachVirtuelInvalidToken:
    """Tests for invalid/missing token scenarios"""
    
    def test_invalid_token_returns_error(self):
        """Test that invalid token returns appropriate error"""
        response = requests.get(f"{BASE_URL}/api/coach/progress?token=invalid_token_12345")
        
        # Should return 404 or 401 for invalid token
        assert response.status_code in [401, 404], f"Expected 401/404 for invalid token, got {response.status_code}"
