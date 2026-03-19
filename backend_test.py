import requests
import sys
import json
from datetime import datetime

class ReActifProAPITester:
    def __init__(self):
        self.base_url = "https://ats-engine.preview.emergentagent.com/api"
        self.token = None
        self.profile_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        # Add token to params if available
        if self.token and params:
            params['token'] = self.token
        elif self.token and not params:
            params = {'token': self.token}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {method} {url}")
        if params:
            print(f"   Params: {params}")
        if data:
            print(f"   Data: {data}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, params=params)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict):
                        print(f"   Response keys: {list(response_data.keys())}")
                    elif isinstance(response_data, list):
                        print(f"   Response: list with {len(response_data)} items")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                self.failed_tests.append({
                    "test": name,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "endpoint": endpoint,
                    "error": response.text[:200]
                })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Network/Request Error: {str(e)}")
            self.failed_tests.append({
                "test": name,
                "expected": expected_status,
                "actual": "ERROR",
                "endpoint": endpoint,
                "error": str(e)
            })
            return False, {}

    def test_root_endpoint(self):
        """Test API root endpoint"""
        return self.run_test("Root API", "GET", "", 200)

    def test_create_anonymous_token(self, role="particulier"):
        """Test anonymous token creation"""
        success, response = self.run_test(
            f"Create anonymous token ({role})",
            "POST",
            "auth/anonymous",
            200,
            data={"role": role}
        )
        if success and 'token' in response:
            self.token = response['token']
            self.profile_id = response.get('profile_id')
            print(f"   Got token: {self.token[:20]}...")
            return True
        return False

    def test_verify_token(self):
        """Test token verification"""
        if not self.token:
            print("❌ No token available for verification")
            return False
        return self.run_test(
            "Verify token",
            "GET",
            "auth/verify",
            200,
            params={"token": self.token}
        )[0]

    def test_switch_role(self, new_role):
        """Test role switching"""
        if not self.token:
            print("❌ No token available for role switch")
            return False
        return self.run_test(
            f"Switch role to {new_role}",
            "POST",
            f"auth/switch-role",
            200,
            params={"token": self.token, "new_role": new_role}
        )[0]

    def test_seed_database(self):
        """Test database seeding"""
        return self.run_test(
            "Seed database",
            "POST",
            "seed",
            200
        )[0]

    def test_get_profile(self):
        """Test getting user profile"""
        if not self.token:
            print("❌ No token available for profile")
            return False
        return self.run_test(
            "Get profile",
            "GET",
            "profile",
            200,
            params={"token": self.token}
        )[0]

    def test_update_profile(self):
        """Test profile update"""
        if not self.token:
            print("❌ No token available for profile update")
            return False
        return self.run_test(
            "Update profile",
            "PUT",
            "profile",
            200,
            data={
                "name": "Test User",
                "skills": [{"name": "Test Skill", "level": 75}],
                "experience_years": 3
            },
            params={"token": self.token}
        )[0]

    def test_get_jobs(self):
        """Test getting job offers"""
        if not self.token:
            print("❌ No token available for jobs")
            return False
        return self.run_test(
            "Get jobs",
            "GET",
            "jobs",
            200,
            params={"token": self.token}
        )[0]

    def test_get_learning(self):
        """Test getting learning modules"""
        if not self.token:
            print("❌ No token available for learning")
            return False
        return self.run_test(
            "Get learning modules",
            "GET",
            "learning",
            200,
            params={"token": self.token}
        )[0]

    def test_create_job(self):
        """Test job creation (requires entreprise role)"""
        if not self.token:
            print("❌ No token available for job creation")
            return False
        return self.run_test(
            "Create job offer",
            "POST",
            "jobs",
            200,  # Will be 403 if not entreprise role
            data={
                "title": "Test Developer",
                "company": "Test Company",
                "location": "Paris, France",
                "contract_type": "CDI",
                "salary_range": "40000€ - 50000€",
                "required_skills": ["JavaScript", "Python"],
                "description": "Test job description",
                "sector": "Informatique"
            },
            params={"token": self.token}
        )

    def test_get_metrics(self):
        """Test platform metrics"""
        return self.run_test(
            "Get metrics",
            "GET",
            "metrics",
            200
        )[0]

    def test_rh_candidates(self):
        """Test RH candidates endpoint"""
        if not self.token:
            print("❌ No token available for RH candidates")
            return False
        return self.run_test(
            "Get RH candidates",
            "GET",
            "rh/candidates",
            200,
            params={"token": self.token}
        )[0]

    def test_partenaires_beneficiaires(self):
        """Test partenaires beneficiaires endpoint"""
        if not self.token:
            print("❌ No token available for partenaires")
            return False
        return self.run_test(
            "Get beneficiaires",
            "GET",
            "partenaires/beneficiaires",
            200,
            params={"token": self.token}
        )[0]

    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print(f"📊 Test Summary")
        print(f"{'='*60}")
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {len(self.failed_tests)}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"   - {test['test']}: {test['expected']} -> {test['actual']}")
                print(f"     Endpoint: {test['endpoint']}")
                print(f"     Error: {test['error']}")
                print()

def main():
    print("🚀 Starting Ré'Actif Pro Backend API Tests")
    print(f"Testing backend at: https://ats-engine.preview.emergentagent.com/api")
    
    tester = ReActifProAPITester()
    
    # Test sequence
    print("\n" + "="*60)
    print("Phase 1: Basic API Tests")
    print("="*60)
    
    # Basic API test
    tester.test_root_endpoint()
    
    # Seed database first
    tester.test_seed_database()
    
    print("\n" + "="*60)
    print("Phase 2: Authentication Tests")
    print("="*60)
    
    # Test authentication flow for particulier
    if tester.test_create_anonymous_token("particulier"):
        tester.test_verify_token()
    
    print("\n" + "="*60)
    print("Phase 3: Profile & Data Tests")
    print("="*60)
    
    # Test profile operations
    tester.test_get_profile()
    tester.test_update_profile()
    
    # Test data endpoints
    tester.test_get_jobs()
    tester.test_get_learning()
    tester.test_get_metrics()
    
    print("\n" + "="*60)
    print("Phase 4: Role-specific Tests")
    print("="*60)
    
    # Test role switching and role-specific endpoints
    tester.test_switch_role("entreprise")
    tester.test_create_job()  # Should work now
    tester.test_rh_candidates()
    
    tester.test_switch_role("partenaire")
    tester.test_partenaires_beneficiaires()
    
    # Test other roles
    print("\n" + "="*60)
    print("Phase 5: Additional Role Tests")
    print("="*60)
    
    # Test new token creation for each role
    for role in ["entreprise", "partenaire"]:
        print(f"\n--- Testing {role} role from fresh token ---")
        if tester.test_create_anonymous_token(role):
            tester.test_verify_token()
            if role == "entreprise":
                tester.test_rh_candidates()
            elif role == "partenaire":
                tester.test_partenaires_beneficiaires()
    
    tester.print_summary()
    
    return 0 if len(tester.failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())