"""Tests de régression — D'CLIC PRO (submit, retrieve, claim, import)"""
import requests
import pytest

SAMPLE_ANSWERS = {
    "v1": "E", "v2": "I", "v3": "N",
    "v4": "N1,N2,S1,S2",
    "v5": "F", "v6": "T",
    "v7": "J", "v8": "P",
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


class TestDclicQuestionnaire:
    """D'CLIC PRO: questionnaire endpoints."""

    def test_get_visual_questions(self, api):
        r = requests.get(f"{api}/dclic/questionnaire/visual")
        assert r.status_code == 200
        data = r.json()
        assert "questions" in data
        assert len(data["questions"]) == 26, f"Expected 26 questions, got {len(data['questions'])}"

    def test_get_legacy_questions(self, api):
        r = requests.get(f"{api}/dclic/questionnaire")
        assert r.status_code == 200
        data = r.json()
        assert "questions" in data


class TestDclicSubmit:
    """D'CLIC PRO: submit and scoring."""

    def test_submit_returns_profile(self, api):
        r = requests.post(f"{api}/dclic/submit", json={"answers": SAMPLE_ANSWERS})
        assert r.status_code == 200
        data = r.json()
        assert "access_code" in data
        assert "profile" in data
        assert len(data["access_code"]) >= 6

    def test_submit_profile_has_all_fields(self, api):
        r = requests.post(f"{api}/dclic/submit", json={"answers": SAMPLE_ANSWERS})
        p = r.json()["profile"]
        required_fields = ["mbti", "disc", "disc_scores", "disc_label",
                           "ennea_dominant", "ennea_profile",
                           "riasec_profile", "vertus_profile",
                           "competences_fortes", "vigilances"]
        for field in required_fields:
            assert field in p, f"Missing field: {field}"

    def test_submit_disc_scores_valid(self, api):
        r = requests.post(f"{api}/dclic/submit", json={"answers": SAMPLE_ANSWERS})
        scores = r.json()["profile"]["disc_scores"]
        assert "D" in scores and "I" in scores and "S" in scores and "C" in scores
        assert all(isinstance(v, (int, float)) for v in scores.values())

    def test_submit_mbti_4_letters(self, api):
        r = requests.post(f"{api}/dclic/submit", json={"answers": SAMPLE_ANSWERS})
        mbti = r.json()["profile"]["mbti"]
        assert len(mbti) == 4, f"MBTI should be 4 letters, got: {mbti}"
        assert mbti[0] in "EI" and mbti[1] in "SN" and mbti[2] in "TF" and mbti[3] in "JP"


class TestDclicRetrieveClaimImport:
    """D'CLIC PRO: retrieve, claim, import flow."""

    @pytest.fixture
    def fresh_code(self, api):
        r = requests.post(f"{api}/dclic/submit", json={"answers": SAMPLE_ANSWERS})
        return r.json()["access_code"]

    def test_retrieve_with_valid_code(self, api, fresh_code):
        r = requests.post(f"{api}/dclic/retrieve", json={"access_code": fresh_code})
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "profile" in data
        # Check critical preview fields used by Dashboard
        p = data["profile"]
        assert "mbti" in p
        assert "disc_label" in p or "disc" in p
        assert "vertus_profile" in p
        assert "riasec_profile" in p

    def test_retrieve_with_invalid_code(self, api):
        r = requests.post(f"{api}/dclic/retrieve", json={"access_code": "XXXX-YYYY"})
        assert r.status_code == 404

    def test_claim_code(self, api, fresh_code):
        r = requests.post(f"{api}/dclic/claim", params={"access_code": fresh_code, "user_id": "test"})
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_import_dclic(self, api, user_token, fresh_code):
        # Retrieve the profile
        ret = requests.post(f"{api}/dclic/retrieve", json={"access_code": fresh_code})
        profile_data = ret.json()["profile"]

        # Import
        r = requests.post(f"{api}/profile/import-dclic", params={"token": user_token},
                          json={"dclic_profile": profile_data, "skills": [], "evidences": []})
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "profile_completion" in data
        assert isinstance(data["profile_completion"], int)

    def test_import_sets_dclic_imported_flag(self, api, user_token, fresh_code):
        ret = requests.post(f"{api}/dclic/retrieve", json={"access_code": fresh_code})
        profile_data = ret.json()["profile"]
        requests.post(f"{api}/profile/import-dclic", params={"token": user_token},
                      json={"dclic_profile": profile_data})

        # Verify flag
        r = requests.get(f"{api}/profile", params={"token": user_token})
        assert r.json().get("dclic_imported") is True
