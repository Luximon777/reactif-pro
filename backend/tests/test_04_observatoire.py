"""Tests de régression — Observatoire, Evolution, Job Matching"""
import requests
import pytest


class TestEvolutionIndex:
    """Evolution Index dashboard."""

    def test_dashboard_returns_data(self, api):
        r = requests.get(f"{api}/evolution-index/dashboard")
        assert r.status_code == 200
        data = r.json()
        assert "sectors" in data
        assert "top_transforming_jobs" in data
        assert "most_stable_jobs" in data
        assert len(data["sectors"]) > 0, "Should have at least 1 sector"
        assert len(data["top_transforming_jobs"]) > 0, "Should have transforming jobs"
        assert len(data["most_stable_jobs"]) > 0, "Should have stable jobs"

    def test_user_profile_no_crash(self, api, user_token):
        """User profile endpoint should not 500 even with empty profile."""
        r = requests.get(f"{api}/evolution-index/user-profile", params={"token": user_token})
        assert r.status_code == 200
        data = r.json()
        assert "has_cv" in data
        assert "relevant_jobs" in data
        assert "evolution_exposure" in data


class TestDclicJobMatch:
    """D'CLIC PRO job matching."""

    def test_job_match(self, api):
        r = requests.post(f"{api}/dclic/job-match", json={
            "answers": {
                "v1": "E", "v2": "I", "v3": "N", "v4": "N1,N2,S1,S2",
                "v5": "F", "v6": "T", "v7": "J", "v8": "P",
                "v9": "I,D,S,C", "v10": "S,C,D,I",
                "v11": "2,5,7,9", "v12": "1,3,6,8",
                "r1": "S", "r2": "A", "r3": "I",
                "r4": "S,A,I,R", "r5": "E", "r6": "A,S,I,C",
                "r7": "I", "r8": "S,A,R,E",
                "vv1": "sagesse", "vv2": "humanite", "vv3": "temperance",
                "vv4": "bienveillance,autonomie,securite,reussite",
                "vv5": "creativite",
                "vv6": "ecoute,initiative,rigueur,leadership"
            }
        }, timeout=120)
        # May take time due to LLM calls
        assert r.status_code == 200
        data = r.json()
        assert "best_match" in data or "profile_summary" in data

    def test_filieres_endpoint(self, api):
        r = requests.get(f"{api}/dclic/filieres")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, (list, dict))

    def test_metiers_endpoint(self, api):
        r = requests.get(f"{api}/dclic/metiers")
        assert r.status_code == 200

    def test_vertus_endpoint(self, api):
        r = requests.get(f"{api}/dclic/vertus")
        assert r.status_code == 200
