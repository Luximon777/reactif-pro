import requests
import sys
import json
from datetime import datetime

class DecliProAPITester:
    def __init__(self, base_url="https://career-path-qa.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.profile_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            print(f"   Status: {response.status_code}")
            
            # Try to parse JSON response
            try:
                response_data = response.json()
                print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
            except:
                print(f"   Response (text): {response.text[:200]}...")

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Expected {expected_status}, got {response.status_code}")
                return True, response.json() if response.content else {}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                return False, {}

        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_create_profile(self):
        """Test creating a new profile"""
        profile_data = {
            "soft_skills": ["Esprit analytique", "Communication orale", "Organisation"],
            "values": ["Impact social", "Développement personnel", "Autonomie"],
            "potentials": ["Gestion du stress", "Proactivité", "Vision stratégique"],
            "answers": {
                "1": {"value": "analytical", "trait": "Esprit analytique", "category": "soft_skills"},
                "2": {"value": "verbal", "trait": "Communication orale", "category": "soft_skills"},
                "3": {"value": "impact", "trait": "Impact social", "category": "values"}
            }
        }
        
        success, response = self.run_test(
            "Create Profile", 
            "POST", 
            "profile", 
            200,  # Expected status according to server.py
            data=profile_data
        )
        
        if success and 'id' in response:
            self.profile_id = response['id']
            print(f"   Profile ID: {self.profile_id}")
            return True
        return False

    def test_get_profile(self):
        """Test retrieving a profile by ID"""
        if not self.profile_id:
            print("❌ SKIPPED - No profile ID available")
            return False
            
        return self.run_test(
            "Get Profile", 
            "GET", 
            f"profile/{self.profile_id}", 
            200
        )[0]

    def test_matching_jobs(self):
        """Test getting matching jobs"""
        job_request = {
            "soft_skills": ["Esprit analytique", "Communication orale", "Organisation"],
            "values": ["Impact social", "Développement personnel", "Autonomie"],
            "potentials": ["Gestion du stress", "Proactivité", "Vision stratégique"]
        }
        
        success, response = self.run_test(
            "Get Matching Jobs", 
            "POST", 
            "matching-jobs", 
            200,
            data=job_request
        )
        
        if success and 'jobs' in response:
            jobs = response['jobs']
            print(f"   Found {len(jobs)} matching jobs")
            for job in jobs[:3]:  # Show first 3
                print(f"   - {job['title']}: {job['compatibility']}% match")
            return True
        return False

    def test_get_all_jobs(self):
        """Test getting all available jobs"""
        success, response = self.run_test(
            "Get All Jobs", 
            "GET", 
            "jobs", 
            200
        )
        
        if success and 'jobs' in response:
            print(f"   Found {len(response['jobs'])} total jobs available")
            return True
        return False

    def run_all_tests(self):
        """Run all API tests"""
        print("=" * 60)
        print("🚀 Starting DE'CLIC PRO API Tests")
        print("=" * 60)
        
        # Test API availability first
        print(f"\n📍 Testing API base URL: {self.api_url}")
        
        # Run tests in logical order
        tests = [
            ("Root Endpoint", self.test_root_endpoint),
            ("Create Profile", self.test_create_profile),
            ("Get Profile", self.test_get_profile),
            ("Matching Jobs", self.test_matching_jobs),
            ("Get All Jobs", self.test_get_all_jobs)
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"❌ FAILED - {test_name}: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 All tests passed! Backend API is working correctly.")
            return 0
        else:
            print(f"\n⚠️  {self.tests_run - self.tests_passed} test(s) failed. Check the issues above.")
            return 1

def main():
    tester = DecliProAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())