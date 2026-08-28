"""Backend tests for job dating ranking after RCA fix (best sector rank, GENERIC_WORDS filter, cap 20)."""
import os
import pytest
import requests

def _load_backend_url():
    url = os.environ.get("REACT_APP_BACKEND_URL")
    if not url:
        try:
            with open("/app/frontend/.env") as f:
                for line in f:
                    if line.startswith("REACT_APP_BACKEND_URL="):
                        url = line.split("=", 1)[1].strip()
                        break
        except Exception:
            pass
    assert url, "REACT_APP_BACKEND_URL not set"
    return url.rstrip("/")


BASE_URL = _load_backend_url()


def _login(pseudo: str, password: str = "Solerys777!"):
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"pseudo": pseudo, "password": password}, timeout=30)
    assert r.status_code == 200, f"login failed for {pseudo}: {r.status_code} {r.text}"
    data = r.json()
    tok = data.get("token") or data.get("access_token")
    assert tok, f"no token in login response: {data}"
    return tok


@pytest.fixture(scope="module")
def token_michel():
    return _login("michel")


@pytest.fixture(scope="module")
def token_mike():
    return _login("mike")


def _check_ranking(events, who):
    assert len(events) > 0, f"{who}: no events returned"
    # Top event must be Logistique/Transport or Propreté/Services (NOT IT)
    top = events[0]
    top_title_lower = top["title"].lower()
    assert "numérique" not in top_title_lower and "it" not in top_title_lower.split(), \
        f"{who}: IT event at top! {top['title']} score={top['match_score']}"
    assert any(k in top_title_lower for k in ["logistique", "transport", "propreté", "services", "multi-services"]), \
        f"{who}: unexpected top event: {top['title']} score={top['match_score']}"
    assert top["match_score"] >= 50, f"{who}: top score too low ({top['match_score']}) — {top['title']}"
    assert top.get("match_level") in ("fort", "moyen"), f"{who}: top match_level={top.get('match_level')}"
    assert top.get("ai_reason"), f"{who}: top ai_reason missing"

    # IT event must be relegated with score <= 35
    it_evt = next((e for e in events if "numérique & it" in e["title"].lower()), None)
    assert it_evt is not None, f"{who}: IT event not found in list"
    assert it_evt["match_score"] <= 35, f"{who}: IT score too high: {it_evt['match_score']}"


def test_recommended_michel_relevance(token_michel):
    r = requests.get(f"{BASE_URL}/api/jobdating/recommended", params={"token": token_michel}, timeout=30)
    assert r.status_code == 200, r.text
    data = r.json()
    events = data.get("events", [])
    print("\nMICHEL recommended top scores:")
    for e in events[:8]:
        print(f"  {e['match_score']:>3} [{e.get('match_level')}] {e['title']}")
    _check_ranking(events, "michel")
    assert data.get("ai_summary")


def test_recommended_mike_relevance(token_mike):
    r = requests.get(f"{BASE_URL}/api/jobdating/recommended", params={"token": token_mike}, timeout=30)
    assert r.status_code == 200, r.text
    data = r.json()
    events = data.get("events", [])
    print("\nMIKE recommended top scores:")
    for e in events[:8]:
        print(f"  {e['match_score']:>3} [{e.get('match_level')}] {e['title']}")
    _check_ranking(events, "mike")


def test_events_endpoint_regression(token_michel):
    r = requests.get(f"{BASE_URL}/api/jobdating/events", params={"token": token_michel}, timeout=30)
    assert r.status_code == 200, r.text
    data = r.json()
    events = data.get("events", [])
    assert len(events) >= 15, f"expected ≥15 events, got {len(events)}"
    # Same relevance sorting: top should NOT be IT
    top = events[0]
    assert "numérique & it" not in top["title"].lower(), f"events top is IT: {top['title']}"
    # IT should be present but low
    it_evt = next((e for e in events if "numérique & it" in e["title"].lower()), None)
    assert it_evt is not None
    assert it_evt["match_score"] <= 35


def test_sectors_endpoint():
    r = requests.get(f"{BASE_URL}/api/jobdating/sectors", timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data.get("sectors"), list) and len(data["sectors"]) >= 10


def test_save_flow(token_michel):
    # pick top event
    r = requests.get(f"{BASE_URL}/api/jobdating/recommended", params={"token": token_michel}, timeout=30)
    top = r.json()["events"][0]
    eid = top["id"]

    r = requests.post(f"{BASE_URL}/api/jobdating/events/{eid}/save", params={"token": token_michel}, timeout=15)
    assert r.status_code == 200 and r.json().get("success")

    r = requests.get(f"{BASE_URL}/api/jobdating/saved", params={"token": token_michel}, timeout=15)
    assert r.status_code == 200
    saved_ids = [s.get("event_id") for s in r.json().get("events", [])]
    assert eid in saved_ids, f"event {eid} not in saved: {saved_ids}"

    r = requests.delete(f"{BASE_URL}/api/jobdating/events/{eid}/save", params={"token": token_michel}, timeout=15)
    assert r.status_code == 200
    r = requests.get(f"{BASE_URL}/api/jobdating/saved", params={"token": token_michel}, timeout=15)
    saved_ids = [s.get("event_id") for s in r.json().get("events", [])]
    assert eid not in saved_ids


def test_register_flow(token_michel):
    r = requests.get(f"{BASE_URL}/api/jobdating/recommended", params={"token": token_michel}, timeout=30)
    top = r.json()["events"][0]
    eid = top["id"]

    r = requests.post(f"{BASE_URL}/api/jobdating/events/{eid}/register", params={"token": token_michel}, timeout=15)
    assert r.status_code == 200 and r.json().get("success")

    r = requests.get(f"{BASE_URL}/api/jobdating/registrations", params={"token": token_michel}, timeout=15)
    assert r.status_code == 200
    reg_ids = [x.get("event_id") for x in r.json().get("registrations", [])]
    assert eid in reg_ids
