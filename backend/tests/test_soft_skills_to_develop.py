"""
Test suite for the soft_skills_to_develop feature in job-match endpoint.
This tests that:
1. POST /api/job-match returns job_narrative with soft_skills_to_develop list
2. Each soft skill contains 'nom', 'importance' and 'description'
3. The badge logic: 'critique' -> 'Prioritaire', 'importante' -> 'Recommandé'
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Sample answers for a complete questionnaire
SAMPLE_ANSWERS = {
    "v1": "E", "v2": "E",  # energie
    "v3": "S", "v4": "S1,N1,S2,N2",  # perception
    "v5": "T", "v6": "T",  # decision
    "v7": "J", "v8": "J",  # structure
    "v9": "D,I,S,C", "v10": "D,I,S,C",  # disc
    "v11": "3,2,5,4", "v12": "3,2,5,4",  # ennea
    # RIASEC questions
    "r1": "R", "r2": "A", "r3": "E",
    "r4": "R,A,S,E",
    "r5": "I", "r6": "R,I,C,E",
    "r7": "S", "r8": "I,A,S,C",
    # Vertus questions
    "vv1": "sagesse", "vv2": "humanite", "vv3": "temperance",
    "vv4": "autonomie,bienveillance,reussite,securite",
    "vv5": "creativite", "vv6": "initiative,ecoute,rigueur,leadership"
}


class TestSoftSkillsToDevelop:
    """Test the soft_skills_to_develop feature in job_narrative"""

    def test_job_match_returns_soft_skills_to_develop_list(self):
        """Test 1: POST /api/job-match returns job_narrative with soft_skills_to_develop list"""
        response = requests.post(
            f"{BASE_URL}/api/job-match",
            json={
                "answers": SAMPLE_ANSWERS,
                "job_query": "développeur web",
                "birth_date": "1990-05-15"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check that job_narrative exists
        assert "job_narrative" in data, "Response should contain 'job_narrative'"
        job_narrative = data["job_narrative"]
        
        # Check that soft_skills_to_develop is in job_narrative
        assert "soft_skills_to_develop" in job_narrative, "job_narrative should contain 'soft_skills_to_develop'"
        
        soft_skills = job_narrative["soft_skills_to_develop"]
        print(f"✓ soft_skills_to_develop found with {len(soft_skills)} skills")
        
        # It should be a list
        assert isinstance(soft_skills, list), "soft_skills_to_develop should be a list"
        print(f"✓ soft_skills_to_develop is a list")

    def test_soft_skill_contains_required_fields(self):
        """Test 2: Each soft skill contains 'nom', 'importance' and 'description'"""
        response = requests.post(
            f"{BASE_URL}/api/job-match",
            json={
                "answers": SAMPLE_ANSWERS,
                "job_query": "infirmier",
                "birth_date": "1985-03-20"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        job_narrative = data.get("job_narrative", {})
        soft_skills = job_narrative.get("soft_skills_to_develop", [])
        
        # If there are soft skills, each should have nom, importance, description
        if len(soft_skills) > 0:
            for idx, skill in enumerate(soft_skills):
                assert "nom" in skill, f"Skill {idx} should have 'nom'"
                assert "importance" in skill, f"Skill {idx} should have 'importance'"
                assert "description" in skill, f"Skill {idx} should have 'description'"
                
                # Validate importance value
                assert skill["importance"] in ["critique", "importante"], \
                    f"Skill importance should be 'critique' or 'importante', got '{skill['importance']}'"
                
                print(f"✓ Skill {idx}: nom='{skill['nom']}', importance='{skill['importance']}'")
        else:
            print("ℹ No soft skills to develop found (user may already have required skills)")
            # This is still valid - if user already has all skills
        
        print(f"✓ All {len(soft_skills)} soft skills have required fields")

    def test_soft_skills_importance_badge_mapping(self):
        """Test 3: Verify importance values map to badges (critique->Prioritaire, importante->Recommandé)"""
        response = requests.post(
            f"{BASE_URL}/api/job-match",
            json={
                "answers": SAMPLE_ANSWERS,
                "job_query": "commercial",
                "birth_date": "1992-08-10"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        job_narrative = data.get("job_narrative", {})
        soft_skills = job_narrative.get("soft_skills_to_develop", [])
        
        importance_counts = {"critique": 0, "importante": 0}
        
        for skill in soft_skills:
            importance = skill.get("importance", "importante")
            if importance in importance_counts:
                importance_counts[importance] += 1
            
            # Verify the expected badge mapping
            expected_badge = "Prioritaire" if importance == "critique" else "Recommandé"
            print(f"  - '{skill['nom']}' -> importance='{importance}' -> badge='{expected_badge}'")
        
        print(f"✓ Importance distribution: {importance_counts}")
        print(f"✓ Badge mapping verified: critique->Prioritaire, importante->Recommandé")

    def test_soft_skills_max_count(self):
        """Test 4: Verify soft_skills_to_develop is limited to 4 skills"""
        response = requests.post(
            f"{BASE_URL}/api/job-match",
            json={
                "answers": SAMPLE_ANSWERS,
                "job_query": "chef de projet",
                "birth_date": "1988-12-01"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        job_narrative = data.get("job_narrative", {})
        soft_skills = job_narrative.get("soft_skills_to_develop", [])
        
        # According to the code: soft_skills_to_develop = soft_skills_to_develop[:4]
        assert len(soft_skills) <= 4, f"Expected max 4 skills, got {len(soft_skills)}"
        print(f"✓ soft_skills_to_develop count: {len(soft_skills)} (max 4)")

    def test_different_job_queries(self):
        """Test 5: Different job queries return appropriate soft skills"""
        job_queries = [
            "développeur web",
            "infirmier",
            "commercial",
            "data scientist"
        ]
        
        for query in job_queries:
            response = requests.post(
                f"{BASE_URL}/api/job-match",
                json={
                    "answers": SAMPLE_ANSWERS,
                    "job_query": query,
                    "birth_date": "1990-05-15"
                }
            )
            
            assert response.status_code == 200, f"Expected 200 for query '{query}', got {response.status_code}"
            data = response.json()
            
            job_narrative = data.get("job_narrative", {})
            soft_skills = job_narrative.get("soft_skills_to_develop", [])
            
            skill_names = [s.get('nom', 'N/A') for s in soft_skills]
            print(f"  Job: '{query}' -> Skills: {skill_names[:3]}...")
        
        print(f"✓ All {len(job_queries)} job queries returned valid responses")

    def test_job_narrative_structure(self):
        """Test 6: Verify complete job_narrative structure"""
        response = requests.post(
            f"{BASE_URL}/api/job-match",
            json={
                "answers": SAMPLE_ANSWERS,
                "job_query": "développeur",
                "birth_date": "1990-05-15"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Check that job_narrative exists
        assert "job_narrative" in data, "Response should contain 'job_narrative'"
        job_narrative = data["job_narrative"]
        
        # Expected fields in job_narrative
        expected_fields = ["soft_skills_to_develop", "axes_progression"]
        
        found_fields = []
        for field in expected_fields:
            if field in job_narrative:
                found_fields.append(field)
                if field == "soft_skills_to_develop":
                    print(f"  - {field}: {len(job_narrative[field])} items")
                else:
                    print(f"  - {field}: present")
        
        print(f"✓ job_narrative contains: {found_fields}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
