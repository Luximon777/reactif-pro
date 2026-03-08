"""
Test ESTP Vertu Mapping - MBTI_TO_VERTU_FALLBACK
==================================================
This test verifies that when VV (Vertus/Valeurs) questions are NOT answered,
the system correctly uses MBTI type to determine the dominant vertu via fallback.

Bug Fix: Before, all MBTI profiles were getting 'Sagesse' by default.
Now: ESTP should get 'Courage', INTJ should get 'Sagesse', etc.

Test Profile: ESTP (Extraversion, Sensing, Thinking, Perceiving)
Expected Vertu: Courage (not Sagesse)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# ESTP profile answers - NO vv1-vv6 questions to test fallback
ESTP_ANSWERS = {
    # MBTI Questions - answers to produce ESTP
    "v1": "E",   # energie: Extraversion
    "v2": "E",   # energie: Extraversion  
    "v3": "S",   # perception: Sensing
    "v4": "S1,S2,N1,N2",  # perception ranking - S dominant
    "v5": "T",   # decision: Thinking
    "v6": "T",   # decision: Thinking
    "v7": "P",   # structure: Perceiving
    "v8": "P",   # structure: Perceiving
    
    # DISC Questions
    "v9": "D,I,S,C",
    "v10": "D,I,C,S",
    
    # Ennéagramme Questions
    "v11": "7,8,3,6",
    "v12": "7,8,6,3",
    
    # RIASEC Questions
    "r1": "R",
    "r2": "A",
    "r3": "E",
    "r4": "R,E,A,S",
    "r5": "I",
    "r6": "R,E,I,C",
    "r7": "R",
    "r8": "I,A,S,C"
    
    # Note: vv1-vv6 are INTENTIONALLY NOT included to test the fallback
}

# INTJ profile answers - for comparison (should get Sagesse)
INTJ_ANSWERS = {
    "v1": "I",
    "v2": "I",
    "v3": "N",
    "v4": "N1,N2,S1,S2",
    "v5": "T",
    "v6": "T",
    "v7": "J",
    "v8": "J",
    "v9": "C,D,S,I",
    "v10": "C,D,S,I",
    "v11": "5,1,3,6",
    "v12": "5,1,6,3",
    "r1": "I",
    "r2": "A",
    "r3": "C",
    "r4": "I,C,A,R",
    "r5": "I",
    "r6": "I,C,R,E",
    "r7": "R",
    "r8": "I,C,A,S"
    # Note: vv1-vv6 NOT included
}


class TestESTPVertuMapping:
    """Tests for MBTI→Vertu fallback mapping when VV questions not answered"""
    
    def test_01_api_health(self):
        """Test API is accessible"""
        response = requests.get(f"{BASE_URL}/api")
        assert response.status_code == 200
        print("✓ API is healthy")
    
    def test_02_estp_profile_gets_courage_vertu(self):
        """
        CRITICAL TEST: ESTP profile should get 'Courage' as dominant vertu
        when VV questions are NOT answered (fallback mechanism)
        """
        payload = {
            "answers": ESTP_ANSWERS,
            "job_query": "Commercial",
            "birth_date": "1990-05-15"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/job-match",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify MBTI is ESTP
        profile_summary = data.get("profile_summary", {})
        mbti = profile_summary.get("mbti", "")
        print(f"Profile MBTI: {mbti}")
        assert mbti == "ESTP", f"Expected ESTP, got {mbti}"
        
        # Get vertus from profile_summary.vertus (correct path)
        vertus = profile_summary.get("vertus", {})
        dominant_vertu = vertus.get("dominant", "")
        dominant_name = vertus.get("dominant_name", "")
        secondary_vertu = vertus.get("secondary", "")
        
        print(f"Dominant Vertu: {dominant_vertu} ({dominant_name})")
        print(f"Secondary Vertu: {secondary_vertu}")
        
        # CRITICAL ASSERTION: ESTP should have 'courage' as dominant vertu
        assert dominant_vertu.lower() == "courage", \
            f"ESTP should have 'Courage' as dominant vertu, but got '{dominant_vertu}'"
        
        # Secondary vertu should be 'temperance' for ESTP
        assert secondary_vertu.lower() == "temperance", \
            f"ESTP secondary vertu should be 'Tempérance', got '{secondary_vertu}'"
        
        print("✓ ESTP correctly mapped to 'Courage' vertu (bug fixed!)")
    
    def test_03_intj_profile_gets_sagesse_vertu(self):
        """
        COMPARISON TEST: INTJ profile should get 'Sagesse' as dominant vertu
        """
        payload = {
            "answers": INTJ_ANSWERS,
            "job_query": "Architecte système",
            "birth_date": "1985-03-20"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/job-match",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        profile_summary = data.get("profile_summary", {})
        mbti = profile_summary.get("mbti", "")
        print(f"Profile MBTI: {mbti}")
        assert mbti == "INTJ", f"Expected INTJ, got {mbti}"
        
        vertus = profile_summary.get("vertus", {})
        dominant_vertu = vertus.get("dominant", "")
        dominant_name = vertus.get("dominant_name", "")
        
        print(f"Dominant Vertu: {dominant_vertu} ({dominant_name})")
        
        # INTJ should have 'sagesse' as dominant vertu
        assert dominant_vertu.lower() == "sagesse", \
            f"INTJ should have 'Sagesse' as dominant vertu, but got '{dominant_vertu}'"
        
        print("✓ INTJ correctly mapped to 'Sagesse' vertu")
    
    def test_04_access_code_generated(self):
        """Test that access code is generated at the end of test"""
        payload = {
            "answers": ESTP_ANSWERS,
            "job_query": "Commercial terrain",
            "birth_date": "1992-08-10"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/job-match",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        access_code = data.get("access_code")
        assert access_code is not None, "Access code should be generated"
        assert len(access_code) == 9, f"Access code should be 9 chars (XXXX-XXXX), got {access_code}"
        assert "-" in access_code, "Access code should contain hyphen"
        
        print(f"✓ Access code generated: {access_code}")
    
    def test_05_profile_contains_all_expected_sections(self):
        """Test that profile response contains all expected sections"""
        payload = {
            "answers": ESTP_ANSWERS,
            "job_query": "Vendeur automobile",
            "birth_date": "1995-12-01"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/job-match",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check all expected sections are present
        expected_sections = [
            "profile_summary",
            "best_match",
            "access_code",
            "cross_analysis"
        ]
        
        for section in expected_sections:
            assert section in data, f"Missing section: {section}"
            print(f"✓ Section '{section}' present")
        
        # Verify profile_summary structure
        profile_summary = data.get("profile_summary", {})
        assert "mbti" in profile_summary, "Missing MBTI in profile_summary"
        assert "disc_dominant" in profile_summary, "Missing DISC in profile_summary"
        assert "ennea_dominant" in profile_summary, "Missing Ennéagramme in profile_summary"
        assert "vertus" in profile_summary, "Missing vertus in profile_summary"
        
        print(f"✓ Profile Summary: MBTI={profile_summary.get('mbti')}, "
              f"DISC={profile_summary.get('disc_dominant')}, "
              f"Ennéa={profile_summary.get('ennea_dominant')}, "
              f"Vertu={profile_summary.get('vertus', {}).get('dominant')}")
    
    def test_06_explore_endpoint_also_uses_vertu_fallback(self):
        """Test that /api/explore endpoint also correctly uses MBTI→Vertu fallback"""
        payload = {
            "answers": ESTP_ANSWERS,
            "birth_date": "1988-07-25"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/explore",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        profile_summary = data.get("profile_summary", {})
        vertus = profile_summary.get("vertus", {})
        dominant_vertu = vertus.get("dominant", "")
        
        assert dominant_vertu.lower() == "courage", \
            f"ESTP should have 'Courage' in explore endpoint too, got '{dominant_vertu}'"
        
        print(f"✓ /api/explore also returns 'Courage' for ESTP profile")
    
    def test_07_vertu_scores_are_zero_when_no_vv_questions(self):
        """Verify that vertus_raw scores are all zero when VV questions not answered"""
        payload = {
            "answers": ESTP_ANSWERS,
            "job_query": "Manager",
            "birth_date": "1990-01-01"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/job-match",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        vertus = data.get("profile_summary", {}).get("vertus", {})
        vertus_raw = vertus.get("vertus_raw", {})
        
        # All raw scores should be 0 since no VV questions were answered
        total_score = sum(vertus_raw.values())
        assert total_score == 0, f"Vertus raw scores should be 0, got total {total_score}"
        
        # But dominant vertu should still be set via fallback
        dominant = vertus.get("dominant", "")
        assert dominant.lower() == "courage", f"Dominant should be 'courage' via fallback"
        
        print(f"✓ Vertus raw scores are 0, but fallback correctly applied: {dominant}")


class TestDifferentMBTIProfiles:
    """Test various MBTI profiles to verify correct vertu mapping"""
    
    def test_enfp_gets_transcendance(self):
        """ENFP should get Transcendance as dominant vertu"""
        answers = {
            "v1": "E", "v2": "E",
            "v3": "N", "v4": "N1,N2,S1,S2",
            "v5": "F", "v6": "F",
            "v7": "P", "v8": "P",
            "v9": "I,D,S,C", "v10": "I,D,S,C",
            "v11": "7,4,2,9", "v12": "7,4,2,9",
            "r1": "A", "r2": "S", "r3": "E", "r4": "A,S,E,R",
            "r5": "A", "r6": "A,S,E,I", "r7": "S", "r8": "A,S,E,C"
        }
        
        payload = {
            "answers": answers,
            "job_query": "Animateur",
            "birth_date": "1993-06-15"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/job-match",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        mbti = data.get("profile_summary", {}).get("mbti", "")
        vertus = data.get("profile_summary", {}).get("vertus", {})
        dominant = vertus.get("dominant", "")
        
        print(f"ENFP profile - MBTI: {mbti}, Dominant Vertu: {dominant}")
        assert dominant.lower() == "transcendance", f"ENFP should get transcendance, got {dominant}"
        print("✓ ENFP correctly mapped to 'Transcendance'")
    
    def test_istj_gets_justice(self):
        """ISTJ should get Justice as dominant vertu"""
        answers = {
            "v1": "I", "v2": "I",
            "v3": "S", "v4": "S1,S2,N1,N2",
            "v5": "T", "v6": "T",
            "v7": "J", "v8": "J",
            "v9": "C,S,D,I", "v10": "C,S,D,I",
            "v11": "1,6,5,3", "v12": "1,6,5,3",
            "r1": "R", "r2": "S", "r3": "C", "r4": "C,R,S,I",
            "r5": "I", "r6": "C,R,I,E", "r7": "R", "r8": "C,I,R,S"
        }
        
        payload = {
            "answers": answers,
            "job_query": "Comptable",
            "birth_date": "1980-11-20"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/job-match",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        mbti = data.get("profile_summary", {}).get("mbti", "")
        vertus = data.get("profile_summary", {}).get("vertus", {})
        dominant = vertus.get("dominant", "")
        
        print(f"ISTJ profile - MBTI: {mbti}, Dominant Vertu: {dominant}")
        assert dominant.lower() == "justice", f"ISTJ should get justice, got {dominant}"
        print("✓ ISTJ correctly mapped to 'Justice'")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
