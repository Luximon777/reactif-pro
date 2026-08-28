"""Tests for job dating Strasbourg bug fix (iteration_50).

Validates:
- recommended?city=Strasbourg returns >=4 events, Transport in head, Propreté included
- web-search?city=Strasbourg returns 4 entries with francetravail links
- web-search with another city (Colmar) works
- web-search without city returns events=[]
- events endpoint returns 20 events
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cv-analyzer-53.preview.emergentagent.com").rstrip("/")


@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{BASE_URL}/api/auth/login",
                      json={"pseudo": "michel", "password": "Solerys777!"}, timeout=30)
    assert r.status_code == 200, r.text
    tok = r.json().get("token")
    assert tok
    return tok


def test_recommended_strasbourg(token):
    r = requests.get(f"{BASE_URL}/api/jobdating/recommended",
                     params={"token": token, "city": "Strasbourg"}, timeout=60)
    assert r.status_code == 200, r.text
    data = r.json()
    events = data.get("events") or data.get("recommended") or []
    print(f"[recommended?city=Strasbourg] total={len(events)}")
    for e in events[:8]:
        print(" -", e.get("match_score"), "|", e.get("title"), "|", e.get("city"))
    assert len(events) >= 4, f"Expected >=4 events, got {len(events)}"
    titles = [e.get("title", "") for e in events]
    transport = next((e for e in events if "Transport & Livraison" in e.get("title", "") and "Strasbourg" in e.get("title", "")), None)
    assert transport is not None, f"Transport Strasbourg missing. Titles={titles}"
    assert events[0].get("title") == transport.get("title"), f"Transport not first; first={events[0].get('title')}"
    assert (transport.get("match_score") or 0) >= 70, f"Transport score too low: {transport.get('match_score')}"
    proprete = next((e for e in events if "Propreté" in e.get("title", "") and "Strasbourg" in e.get("title", "")), None)
    assert proprete is not None, f"Propreté Strasbourg missing. Titles={titles}"
    assert (proprete.get("match_score") or 0) >= 60, f"Propreté score too low: {proprete.get('match_score')}"


def test_web_search_strasbourg(token):
    r = requests.get(f"{BASE_URL}/api/jobdating/web-search",
                     params={"token": token, "city": "Strasbourg"}, timeout=30)
    assert r.status_code == 200, r.text
    data = r.json()
    events = data.get("events", [])
    print(f"[web-search Strasbourg] total={len(events)} city={data.get('city')}")
    for e in events:
        print(" -", e.get("title"), "|", e.get("event_url"))
    assert len(events) == 4, f"Expected 4 entries, got {len(events)}"
    assert data.get("city") == "Strasbourg"
    for e in events:
        assert "mesevenementsemploi.francetravail.fr" in e.get("event_url", "")
        assert e.get("city") == "Strasbourg"


def test_web_search_colmar(token):
    r = requests.get(f"{BASE_URL}/api/jobdating/web-search",
                     params={"token": token, "city": "Colmar"}, timeout=30)
    assert r.status_code == 200
    data = r.json()
    events = data.get("events", [])
    assert len(events) >= 1
    for e in events:
        assert "Colmar" in e.get("event_url", "")
        assert e.get("city") == "Colmar"


def test_web_search_empty_city(token):
    r = requests.get(f"{BASE_URL}/api/jobdating/web-search",
                     params={"token": token, "city": ""}, timeout=30)
    assert r.status_code == 200
    assert r.json().get("events") == []


def test_events_count(token):
    r = requests.get(f"{BASE_URL}/api/jobdating/events",
                     params={"token": token}, timeout=30)
    assert r.status_code == 200
    data = r.json()
    events = data.get("events", data if isinstance(data, list) else [])
    print(f"[events] total={len(events)}")
    assert len(events) == 20, f"Expected 20, got {len(events)}"


def test_recommended_no_city_regression(token):
    r = requests.get(f"{BASE_URL}/api/jobdating/recommended",
                     params={"token": token}, timeout=60)
    assert r.status_code == 200
    data = r.json()
    events = data.get("events") or data.get("recommended") or []
    print(f"[recommended no city] total={len(events)}")
    for e in events[:8]:
        print(" -", e.get("score"), "|", e.get("title"))
    assert len(events) >= 1
