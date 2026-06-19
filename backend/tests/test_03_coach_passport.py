"""Tests de régression — Coach, Passport, Reset"""
import requests
import pytest


class TestCoachProgress:
    """Coach RE'ACTIF: progress endpoint."""

    def test_coach_progress_returns_steps(self, api, user_token):
        r = requests.get(f"{api}/coach/progress", params={"token": user_token})
        assert r.status_code == 200
        data = r.json()
        assert "steps" in data
        assert "completed" in data
        assert "total" in data
        assert "progress_pct" in data
        assert isinstance(data["steps"], list)
        assert data["total"] == 4

    def test_coach_progress_detects_dclic(self, api, user_token):
        """After D'CLIC import, coach should detect it."""
        r = requests.get(f"{api}/coach/progress", params={"token": user_token})
        data = r.json()
        # Step 3 is D'CLIC
        dclic_step = next((s for s in data["steps"] if "CLIC" in s.get("title", "")), None)
        if dclic_step:
            assert dclic_step["complete"] is True, "D'CLIC step should be complete after import"

    def test_coach_message_no_doublon(self, api):
        """Ensure the welcome message doesn't duplicate the next step hint."""
        # Use anonymous token (no CV, no D'CLIC)
        anon = requests.post(f"{api}/auth/anonymous", json={"role": "particulier"})
        token = anon.json()["token"]
        r = requests.get(f"{api}/coach/progress", params={"token": token})
        data = r.json()
        message = data.get("message", "")
        hint = data.get("next_step", {}).get("hint", "") if data.get("next_step") else ""
        if hint:
            # Message should not contain the full hint text (was the doublon bug)
            assert hint not in message, f"Doublon detected: message contains the hint text"


class TestPassport:
    """Passport: read."""

    def test_get_passport(self, api, user_token):
        r = requests.get(f"{api}/passport", params={"token": user_token})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, dict)


class TestPassportReset:
    """Passport reset: all sections."""

    SECTIONS = ["competences", "experiences", "formations", "profile", "passerelles", "dclic"]

    @pytest.mark.parametrize("section", SECTIONS)
    def test_reset_section(self, api, user_token, section):
        r = requests.delete(f"{api}/passport/reset",
                            params={"token": user_token, "sections": section})
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert section in data["message"]

    def test_reset_all(self, api, user_token):
        r = requests.delete(f"{api}/passport/reset",
                            params={"token": user_token, "sections": "all"})
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_reset_invalid_section(self, api, user_token):
        r = requests.delete(f"{api}/passport/reset",
                            params={"token": user_token, "sections": "nonexistent"})
        assert r.status_code == 400

    def test_dclic_reset_clears_flag(self, api, user_token):
        """After D'CLIC reset, dclic_imported should be False."""
        requests.delete(f"{api}/passport/reset",
                        params={"token": user_token, "sections": "dclic"})
        r = requests.get(f"{api}/profile", params={"token": user_token})
        assert r.json().get("dclic_imported") is not True
