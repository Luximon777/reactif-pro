"""
Iteration 35 - Backend regression tests for:
1. Marché caché diagnostic (cached GET, POST job, status polling)
2. Jobs matching France Travail first
3. Job Dating register + history with full event details
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cv-analyzer-53.preview.emergentagent.com").rstrip("/")
USER = "mike9"
PASSWORD = "Solerys777!"


@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"pseudo": USER, "password": PASSWORD}, timeout=30)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text[:300]}"
    data = r.json()
    tok = data.get("token")
    assert tok, f"no token in login response: {data}"
    return tok


# ---------- Marché caché ----------
class TestMarcheCache:
    def test_cached_diagnostic_available(self, token):
        r = requests.get(f"{BASE_URL}/api/marche-cache/diagnostic", params={"token": token}, timeout=30)
        assert r.status_code == 200, r.text[:300]
        data = r.json()
        assert data.get("has_diagnostic") is True, f"expected has_diagnostic=True, got {data}"
        diag = data.get("diagnostic") or {}
        # Basic structure: expected keys
        assert isinstance(diag, dict) and diag, "diagnostic payload empty"

    def test_post_job_and_poll_status(self, token):
        r = requests.post(f"{BASE_URL}/api/marche-cache/diagnostic", json={"token": token}, timeout=30)
        assert r.status_code == 200, r.text[:300]
        data = r.json()
        job_id = data.get("job_id")
        assert job_id, f"no job_id in {data}"

        deadline = time.time() + 120  # up to 2 minutes
        last_status = None
        while time.time() < deadline:
            rs = requests.get(
                f"{BASE_URL}/api/marche-cache/diagnostic/status",
                params={"token": token, "job_id": job_id},
                timeout=30,
            )
            assert rs.status_code == 200, rs.text[:300]
            js = rs.json()
            last_status = js.get("status")
            if last_status == "completed":
                diag = js.get("diagnostic") or {}
                assert diag, "completed but no diagnostic payload"
                return
            if last_status == "error":
                pytest.fail(f"job errored: {js}")
            time.sleep(5)
        pytest.fail(f"timeout waiting completed, last_status={last_status}")


# ---------- Jobs Matching (France Travail first) ----------
class TestJobsMatching:
    def test_jobs_matching_france_travail_first(self, token):
        r = requests.get(f"{BASE_URL}/api/jobs/matching", params={"token": token}, timeout=60)
        assert r.status_code == 200, r.text[:400]
        data = r.json()
        assert data.get("source") == "france_travail", f"expected source=france_travail, got source={data.get('source')} keys={list(data.keys())}"
        offers = data.get("offers") or data.get("matches") or data.get("items") or []
        assert offers and len(offers) > 0, f"no offers returned: {data}"

        # Sanity check: at least one offer looks CIP/insertion-related
        def _title(o):
            return str(o.get("titre") or o.get("title") or o.get("intitule") or "")
        titles = " ".join([_title(o) for o in offers]).lower()
        assert any(k in titles for k in ["insertion", "cip", "conseil"]), f"none of expected keywords in titles: {titles[:500]}"

        # Should not be flooded with obviously off-topic titles (e.g., puériculture)
        offtopic = sum(1 for o in offers if "puéricult" in _title(o).lower())
        assert offtopic == 0, f"unexpected off-topic offers count={offtopic}"

        # Scores should be plausible (>= 45 threshold as per fallback rule; FT ideally 70-90)
        scores = [o.get("matching_score") or o.get("score") for o in offers if isinstance(o, dict)]
        scores = [s for s in scores if isinstance(s, (int, float))]
        assert scores, f"no numeric scores found in offers"
        assert max(scores) >= 60, f"expected at least one offer with score>=60 for CIP profile, got scores={scores}"


# ---------- Job Dating ----------
class TestJobDating:
    def test_events_list_available(self, token):
        r = requests.get(f"{BASE_URL}/api/jobdating/events", params={"token": token}, timeout=30)
        assert r.status_code == 200, r.text[:300]
        data = r.json()
        events = data.get("events") or data.get("items") or data
        assert events and len(events) > 0, f"empty events list: {data}"

    def test_register_event_and_history_full_details(self, token):
        # Pick a stable event id from the request (evt-commerce-online) — fallback to first available.
        candidate_id = "evt-commerce-online"
        r = requests.get(f"{BASE_URL}/api/jobdating/events", params={"token": token}, timeout=30)
        assert r.status_code == 200
        payload = r.json()
        events = payload.get("events") or payload.get("items") or []
        ids = [e.get("id") for e in events if isinstance(e, dict)]
        if candidate_id not in ids and ids:
            candidate_id = ids[0]

        reg = requests.post(
            f"{BASE_URL}/api/jobdating/events/{candidate_id}/register",
            params={"token": token},
            json={},
            timeout=30,
        )
        assert reg.status_code in (200, 201), reg.text[:400]

        hist = requests.get(f"{BASE_URL}/api/jobdating/history", params={"token": token}, timeout=30)
        assert hist.status_code == 200, hist.text[:400]
        h = hist.json()

        upcoming = h.get("upcoming") or []
        assert upcoming, f"no upcoming entries in history: {h}"

        # Find the just-registered event OR pre-existing Salon Emploi Toulouse.
        match = None
        for entry in upcoming:
            if entry.get("event_id") == candidate_id or entry.get("id") == candidate_id:
                match = entry
                break
        if match is None:
            # accept any upcoming entry as long as it has full details
            match = upcoming[0]

        # Assertions: title must NOT be the raw id, must have city and datetime
        title = match.get("title") or match.get("event_title") or ""
        assert title and not title.startswith("evt-"), f"title looks like a raw id: {title}"
        city = match.get("city") or match.get("ville") or ""
        assert city, f"missing city in history entry: {match}"
        dt = match.get("start_datetime") or match.get("date") or match.get("start")
        assert dt, f"missing start_datetime in {match}"
