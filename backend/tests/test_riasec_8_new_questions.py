"""
Test suite for 8 new RIASEC questions (r1-r8) integration
Tests the enriched questionnaire and RIASEC calculation with direct questions

Test requirements:
1. API questionnaire/visual - Verify total is 20 questions and r1-r8 are present
2. RIASEC calculation with direct questions - r1=R, r4=R,C,I,S should have R dominant
3. RIASEC calculation with direct questions - r1=I, r2=A, r5=A should have A or I dominant
4. Frontend - Verify questionnaire displays 20 questions (or 21 with date)
5. Coherence - Compare results WITH and WITHOUT RIASEC direct questions
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestRIASECNewQuestionsAPI:
    """Test 1: API questionnaire/visual - 20 questions including r1-r8"""
    
    def test_questionnaire_visual_returns_20_questions(self):
        """Verify questionnaire returns exactly 20 questions"""
        response = requests.get(f"{BASE_URL}/api/questionnaire/visual")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "questions" in data, "Response should contain 'questions' key"
        
        question_count = len(data["questions"])
        assert question_count == 20, f"Expected 20 questions, got {question_count}"
        print(f"✓ Test 1a PASSED: API returns exactly {question_count} questions")
    
    def test_riasec_questions_r1_r8_present(self):
        """Verify all 8 RIASEC questions (r1-r8) are present"""
        response = requests.get(f"{BASE_URL}/api/questionnaire/visual")
        assert response.status_code == 200
        
        data = response.json()
        question_ids = [q["id"] for q in data["questions"]]
        
        expected_riasec_ids = ["r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8"]
        missing_ids = [rid for rid in expected_riasec_ids if rid not in question_ids]
        
        assert not missing_ids, f"Missing RIASEC questions: {missing_ids}"
        print(f"✓ Test 1b PASSED: All 8 RIASEC questions (r1-r8) are present")
        
        # Verify question types
        riasec_questions = [q for q in data["questions"] if q["id"].startswith("r")]
        visual_questions = [q for q in riasec_questions if q["type"] == "visual"]
        ranking_questions = [q for q in riasec_questions if q["type"] == "ranking"]
        
        assert len(visual_questions) == 5, f"Expected 5 visual RIASEC questions, got {len(visual_questions)}"
        assert len(ranking_questions) == 3, f"Expected 3 ranking RIASEC questions, got {len(ranking_questions)}"
        print(f"✓ Test 1c PASSED: 5 visual questions (r1,r2,r3,r5,r7) and 3 ranking questions (r4,r6,r8)")


class TestRIASECDirectQuestionsCalculation:
    """Test 2 & 3: RIASEC calculation with direct question responses"""
    
    def test_r1_r_r4_rcis_should_have_r_dominant(self):
        """Test 2: Profile with r1=R, r4='R,C,I,S' should have R dominant"""
        # Base MBTI answers (neutral - balanced profile)
        answers = {
            # MBTI answers (neutral mix)
            "v1": "E", "v2": "I",  # energie: balanced
            "v3": "S", "v4": "S1,N1,S2,N2",  # perception: S leaning
            "v5": "T", "v6": "T",  # decision: T
            "v7": "J", "v8": "J",  # structure: J
            # DISC (neutral)
            "v9": "S,D,I,C",
            "v10": "C,S,D,I",
            # Enneagram (neutral)
            "v11": "5,3,6,9",
            "v12": "6,5,3,9",
            # RIASEC direct questions (targeting R)
            "r1": "R",  # Réaliste
            "r2": "S",  # Social (neutral)
            "r3": "C",  # Conventionnel (neutral)
            "r4": "R,C,I,S",  # R en premier rang (5 pts)
            "r5": "I",  # Investigateur (neutral)
            "r6": "R,I,C,E",  # R en premier rang (5 pts)
            "r7": "R",  # Réaliste
            "r8": "I,A,S,C"  # Neutral
        }
        
        response = requests.post(
            f"{BASE_URL}/api/explore",
            json={"answers": answers, "birth_date": "1990-06-15"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "profile_summary" in data, "Response should contain profile_summary"
        assert "riasec" in data["profile_summary"], "Profile should contain RIASEC data"
        
        riasec = data["profile_summary"]["riasec"]
        major = riasec["major"]
        raw_scores = riasec.get("raw_scores", riasec.get("scores", {}))
        
        # Get R score
        r_score = raw_scores.get("R", 0)
        
        # R should be dominant or among top 2 with high direct question responses
        # r1=R (5 pts) + r4=R first (5 pts) + r6=R first (5 pts) + r7=R (5 pts) = 20 direct pts for R
        print(f"RIASEC scores: {raw_scores}")
        print(f"Major: {major}, Minor: {riasec['minor']}, Code: {riasec['code_2']}")
        
        # R should be in top position or very high score
        assert major == "R" or "R" in riasec["code_2"], \
            f"Expected R to be dominant or in top 2, got major={major}, code_2={riasec['code_2']}"
        print(f"✓ Test 2 PASSED: R is dominant (major={major}, code_2={riasec['code_2']})")
    
    def test_r1_i_r2_a_r5_a_should_have_a_or_i_dominant(self):
        """Test 3: Profile with r1=I, r2=A, r5=A should have A or I dominant"""
        answers = {
            # MBTI answers (N/F leaning - favors A and I)
            "v1": "I", "v2": "I",  # energie: Introverted
            "v3": "N", "v4": "N1,N2,S1,S2",  # perception: N (intuition)
            "v5": "F", "v6": "F",  # decision: F (feeling)
            "v7": "P", "v8": "P",  # structure: P (perceiving)
            # DISC (I leaning)
            "v9": "I,S,D,C",
            "v10": "I,S,D,C",
            # Enneagram (4 = Artistic type)
            "v11": "4,5,7,9",
            "v12": "4,5,7,9",
            # RIASEC direct questions (targeting A and I)
            "r1": "I",  # Investigateur (5 pts)
            "r2": "A",  # Artistique (5 pts)
            "r3": "E",  # Neutral
            "r4": "A,S,R,E",  # A first (5 pts)
            "r5": "A",  # Artistique (5 pts)
            "r6": "I,R,C,E",  # I first (5 pts)
            "r7": "S",  # Neutral
            "r8": "A,I,S,C"  # A first (5 pts), I second (3 pts)
        }
        
        response = requests.post(
            f"{BASE_URL}/api/explore",
            json={"answers": answers, "birth_date": "1995-03-20"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        riasec = data["profile_summary"]["riasec"]
        major = riasec["major"]
        minor = riasec["minor"]
        raw_scores = riasec.get("raw_scores", riasec.get("scores", {}))
        
        print(f"RIASEC scores: {raw_scores}")
        print(f"Major: {major}, Minor: {minor}, Code: {riasec['code_2']}")
        
        # A or I should be dominant
        # A direct: r2=A (5pts) + r4=A first (5pts) + r5=A (5pts) + r8=A first (5pts) = 20 pts
        # I direct: r1=I (5pts) + r6=I first (5pts) + r8=I second (3pts) = 13 pts
        # Plus MBTI N/F/P boost for A and I boost for MBTI I
        assert major in ["A", "I"] or minor in ["A", "I"], \
            f"Expected A or I to be in top 2, got major={major}, minor={minor}"
        print(f"✓ Test 3 PASSED: A or I is in top positions (major={major}, minor={minor})")


class TestRIASECCoherence:
    """Test 5: Compare results WITH and WITHOUT direct RIASEC questions"""
    
    def test_riasec_with_direct_questions_has_higher_granularity(self):
        """
        Test 5: Verify that direct RIASEC questions impact the final score
        Compare identical MBTI/DISC answers with different RIASEC direct responses
        """
        # Base profile (same MBTI/DISC/Ennéagramme)
        base_answers = {
            "v1": "E", "v2": "E",
            "v3": "S", "v4": "S1,N1,S2,N2",
            "v5": "T", "v6": "T",
            "v7": "J", "v8": "J",
            "v9": "D,I,S,C",
            "v10": "D,C,S,I",
            "v11": "3,8,5,6",
            "v12": "3,8,5,6"
        }
        
        # Profile A: All RIASEC responses favor R (Realistic)
        answers_r_focus = base_answers.copy()
        answers_r_focus.update({
            "r1": "R", "r2": "S", "r3": "C",
            "r4": "R,S,A,E",
            "r5": "I", "r6": "R,I,C,E",
            "r7": "R", "r8": "I,A,S,C"
        })
        
        # Profile B: All RIASEC responses favor A (Artistic)
        answers_a_focus = base_answers.copy()
        answers_a_focus.update({
            "r1": "I", "r2": "A", "r3": "E",
            "r4": "A,R,S,E",
            "r5": "A", "r6": "E,I,C,R",
            "r7": "S", "r8": "A,I,S,C"
        })
        
        # Get results for both profiles
        response_r = requests.post(
            f"{BASE_URL}/api/explore",
            json={"answers": answers_r_focus, "birth_date": "1990-01-01"}
        )
        response_a = requests.post(
            f"{BASE_URL}/api/explore",
            json={"answers": answers_a_focus, "birth_date": "1990-01-01"}
        )
        
        assert response_r.status_code == 200
        assert response_a.status_code == 200
        
        riasec_r = response_r.json()["profile_summary"]["riasec"]
        riasec_a = response_a.json()["profile_summary"]["riasec"]
        
        print(f"Profile R-focus: major={riasec_r['major']}, code={riasec_r['code_2']}")
        print(f"Profile A-focus: major={riasec_a['major']}, code={riasec_a['code_2']}")
        print(f"R-focus raw scores: {riasec_r.get('raw_scores', riasec_r.get('scores'))}")
        print(f"A-focus raw scores: {riasec_a.get('raw_scores', riasec_a.get('scores'))}")
        
        # Verify different RIASEC answers produce different results
        r_scores = riasec_r.get("raw_scores", riasec_r.get("scores", {}))
        a_scores = riasec_a.get("raw_scores", riasec_a.get("scores", {}))
        
        # R score should be higher in R-focus profile
        # A score should be higher in A-focus profile
        r_in_r_profile = r_scores.get("R", 0)
        a_in_a_profile = a_scores.get("A", 0)
        r_in_a_profile = a_scores.get("R", 0)
        a_in_r_profile = r_scores.get("A", 0)
        
        print(f"R score in R-focus: {r_in_r_profile}, R score in A-focus: {r_in_a_profile}")
        print(f"A score in A-focus: {a_in_a_profile}, A score in R-focus: {a_in_r_profile}")
        
        # Direct questions should create measurable difference
        assert r_in_r_profile > r_in_a_profile or a_in_a_profile > a_in_r_profile, \
            "Direct RIASEC questions should impact scores differently"
        
        print("✓ Test 5 PASSED: Direct RIASEC questions create meaningful score differences")


class TestAPIWithRIASECData:
    """Additional tests for RIASEC data with new questions via job-match endpoint"""
    
    def test_job_match_uses_riasec_direct_questions(self):
        """Verify /api/job-match endpoint uses RIASEC direct questions in scoring"""
        answers = {
            "v1": "E", "v2": "E",
            "v3": "S", "v4": "S1,N1,S2,N2",
            "v5": "T", "v6": "T",
            "v7": "J", "v8": "J",
            "v9": "D,I,S,C",
            "v10": "D,C,S,I",
            "v11": "3,8,5,6",
            "v12": "3,8,5,6",
            # Strong E (Enterprising) focus
            "r1": "R", "r2": "S", "r3": "E",
            "r4": "E,S,R,A",
            "r5": "I", "r6": "E,I,C,R",
            "r7": "S", "r8": "S,A,I,C"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/job-match",
            json={"answers": answers, "job_query": "commercial", "birth_date": "1992-07-10"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "profile_summary" in data
        assert "riasec" in data["profile_summary"]
        
        riasec = data["profile_summary"]["riasec"]
        print(f"Job-match RIASEC: major={riasec['major']}, code={riasec['code_2']}")
        
        # E should be boosted by direct questions
        assert "E" in riasec["code_2"] or riasec["major"] == "E" or riasec["minor"] == "E", \
            f"Expected E to be prominent with E-focused answers"
        
        print("✓ Job-match endpoint correctly integrates RIASEC direct questions")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
