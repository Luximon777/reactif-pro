"""
Job Dating API Tests
Tests for the Job Dating feature including:
- GET /api/jobdating/events - Get events sorted by match_score
- GET /api/jobdating/recommended - Get recommended events (score>=25) with ai_summary
- GET /api/jobdating/sectors - Get list of sectors (13 sectors)
- POST /api/jobdating/events/{event_id}/save - Save an event
- DELETE /api/jobdating/events/{event_id}/save - Unsave an event
- GET /api/jobdating/saved - Get saved events
- POST /api/jobdating/events/{event_id}/register - Register for an event
- GET /api/jobdating/registrations - Get registrations
- GET /api/jobdating/history - Get history
- Score relevance tests for mike7 and fanny95
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test tokens from test_credentials.md
MIKE7_TOKEN = "UHrqIUZvfNQnUf6SJYFNdUDlBSg_LobaMY3sKXo6EoQ"
FANNY95_TOKEN = "J3IYR6zGDSK6qCA40U4aC2ishnu5Zsyd3CPrlFW8INI"


class TestJobDatingSectors:
    """Test /api/jobdating/sectors endpoint"""
    
    def test_get_sectors_returns_13_sectors(self):
        """GET /api/jobdating/sectors should return 13 sectors"""
        response = requests.get(f"{BASE_URL}/api/jobdating/sectors", timeout=15)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "sectors" in data, "Response should contain 'sectors' key"
        
        sectors = data["sectors"]
        assert len(sectors) == 13, f"Expected 13 sectors, got {len(sectors)}"
        
        # Verify each sector has name and count
        for sector in sectors:
            assert "name" in sector, "Each sector should have 'name'"
            assert "count" in sector, "Each sector should have 'count'"
            assert isinstance(sector["count"], int), "Count should be integer"


class TestJobDatingEvents:
    """Test /api/jobdating/events endpoint"""
    
    def test_get_events_with_mike7_token(self):
        """GET /api/jobdating/events with mike7 token returns events sorted by match_score"""
        response = requests.get(
            f"{BASE_URL}/api/jobdating/events",
            params={"token": MIKE7_TOKEN},
            timeout=15
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "events" in data, "Response should contain 'events' key"
        assert "total" in data, "Response should contain 'total' key"
        
        events = data["events"]
        assert len(events) > 0, "Should return at least one event"
        
        # Verify events are sorted by match_score descending
        scores = [e.get("match_score", 0) for e in events]
        assert scores == sorted(scores, reverse=True), "Events should be sorted by match_score descending"
        
        # Verify each event has required fields
        for event in events:
            assert "id" in event, "Event should have 'id'"
            assert "title" in event, "Event should have 'title'"
            assert "match_score" in event, "Event should have 'match_score'"
            assert "ai_reason" in event, "Event should have 'ai_reason'"
            assert isinstance(event["match_score"], int), "match_score should be integer"
    
    def test_get_events_with_fanny95_token(self):
        """GET /api/jobdating/events with fanny95 token returns events"""
        response = requests.get(
            f"{BASE_URL}/api/jobdating/events",
            params={"token": FANNY95_TOKEN},
            timeout=15
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "events" in data
        events = data["events"]
        assert len(events) > 0, "Should return events for fanny95"
    
    def test_get_events_invalid_token(self):
        """GET /api/jobdating/events with invalid token returns 401"""
        response = requests.get(
            f"{BASE_URL}/api/jobdating/events",
            params={"token": "invalid_token_12345"},
            timeout=15
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestJobDatingRecommended:
    """Test /api/jobdating/recommended endpoint"""
    
    def test_get_recommended_mike7(self):
        """GET /api/jobdating/recommended returns events with score>=25 and ai_summary"""
        response = requests.get(
            f"{BASE_URL}/api/jobdating/recommended",
            params={"token": MIKE7_TOKEN},
            timeout=30
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "events" in data, "Response should contain 'events'"
        assert "ai_summary" in data, "Response should contain 'ai_summary'"
        
        # Verify ai_summary is not empty
        ai_summary = data.get("ai_summary", "")
        assert ai_summary and len(ai_summary) > 0, "ai_summary should not be empty"
        
        # Verify all events have score >= 25
        events = data["events"]
        for event in events:
            score = event.get("match_score", 0)
            assert score >= 25, f"Recommended event should have score >= 25, got {score}"
    
    def test_get_recommended_fanny95(self):
        """GET /api/jobdating/recommended for fanny95 returns petite enfance events"""
        response = requests.get(
            f"{BASE_URL}/api/jobdating/recommended",
            params={"token": FANNY95_TOKEN},
            timeout=30
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "events" in data
        assert "ai_summary" in data


class TestJobDatingSaveEvents:
    """Test save/unsave event endpoints"""
    
    def test_save_and_unsave_event(self):
        """POST and DELETE /api/jobdating/events/{event_id}/save"""
        # First get events to get a valid event_id
        events_response = requests.get(
            f"{BASE_URL}/api/jobdating/events",
            params={"token": MIKE7_TOKEN},
            timeout=15
        )
        assert events_response.status_code == 200
        events = events_response.json().get("events", [])
        assert len(events) > 0, "Need at least one event to test save"
        
        event_id = events[0]["id"]
        
        # Save the event
        save_response = requests.post(
            f"{BASE_URL}/api/jobdating/events/{event_id}/save",
            params={"token": MIKE7_TOKEN},
            timeout=15
        )
        assert save_response.status_code == 200, f"Save failed: {save_response.status_code}"
        assert save_response.json().get("success") == True
        
        # Verify it's in saved list
        saved_response = requests.get(
            f"{BASE_URL}/api/jobdating/saved",
            params={"token": MIKE7_TOKEN},
            timeout=15
        )
        assert saved_response.status_code == 200
        saved_events = saved_response.json().get("events", [])
        saved_ids = [e.get("event_id") for e in saved_events]
        assert event_id in saved_ids, f"Event {event_id} should be in saved list"
        
        # Unsave the event
        unsave_response = requests.delete(
            f"{BASE_URL}/api/jobdating/events/{event_id}/save",
            params={"token": MIKE7_TOKEN},
            timeout=15
        )
        assert unsave_response.status_code == 200, f"Unsave failed: {unsave_response.status_code}"
        
        # Verify it's removed from saved list
        saved_response2 = requests.get(
            f"{BASE_URL}/api/jobdating/saved",
            params={"token": MIKE7_TOKEN},
            timeout=15
        )
        saved_events2 = saved_response2.json().get("events", [])
        saved_ids2 = [e.get("event_id") for e in saved_events2]
        assert event_id not in saved_ids2, f"Event {event_id} should be removed from saved list"


class TestJobDatingRegistrations:
    """Test registration endpoints"""
    
    def test_register_for_event(self):
        """POST /api/jobdating/events/{event_id}/register"""
        # Get events
        events_response = requests.get(
            f"{BASE_URL}/api/jobdating/events",
            params={"token": MIKE7_TOKEN},
            timeout=15
        )
        events = events_response.json().get("events", [])
        assert len(events) > 0
        
        event_id = events[0]["id"]
        
        # Register for event
        register_response = requests.post(
            f"{BASE_URL}/api/jobdating/events/{event_id}/register",
            params={"token": MIKE7_TOKEN},
            timeout=15
        )
        assert register_response.status_code == 200
        assert register_response.json().get("success") == True
        
        # Verify in registrations
        regs_response = requests.get(
            f"{BASE_URL}/api/jobdating/registrations",
            params={"token": MIKE7_TOKEN},
            timeout=15
        )
        assert regs_response.status_code == 200
        registrations = regs_response.json().get("registrations", [])
        reg_ids = [r.get("event_id") for r in registrations]
        assert event_id in reg_ids, f"Event {event_id} should be in registrations"


class TestJobDatingHistory:
    """Test history endpoint"""
    
    def test_get_history(self):
        """GET /api/jobdating/history returns upcoming and past events"""
        response = requests.get(
            f"{BASE_URL}/api/jobdating/history",
            params={"token": MIKE7_TOKEN},
            timeout=15
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "upcoming" in data, "Response should contain 'upcoming'"
        assert "past" in data, "Response should contain 'past'"
        assert isinstance(data["upcoming"], list)
        assert isinstance(data["past"], list)


class TestScoreRelevance:
    """Test that match scores are relevant to user profiles"""
    
    def test_mike7_scores_high_for_restauration_logistique_proprete(self):
        """
        Mike7 has experiences in:
        - Agent d'entretien (Propreté)
        - Employé polyvalent restauration (Restauration)
        - Second de cuisine (Restauration)
        - Employé de restauration Buffalo Grill (Restauration)
        - Magasinier / Préparateur de commande (Logistique)
        
        Should have high scores for Restauration, Logistique, Propreté events
        """
        response = requests.get(
            f"{BASE_URL}/api/jobdating/events",
            params={"token": MIKE7_TOKEN},
            timeout=15
        )
        assert response.status_code == 200
        
        events = response.json().get("events", [])
        
        # Find events for mike7's sectors
        restauration_events = [e for e in events if any("Restauration" in s for s in e.get("sectors", []))]
        logistique_events = [e for e in events if any("Logistique" in s for s in e.get("sectors", []))]
        proprete_events = [e for e in events if any("Propreté" in s for s in e.get("sectors", []))]
        
        # Check that at least some of these events have high scores
        high_score_threshold = 25  # At least "moyen" level
        
        if restauration_events:
            max_resto_score = max(e.get("match_score", 0) for e in restauration_events)
            print(f"Mike7 max Restauration score: {max_resto_score}")
            assert max_resto_score >= high_score_threshold, f"Mike7 should have high score for Restauration events, got {max_resto_score}"
        
        if logistique_events:
            max_logi_score = max(e.get("match_score", 0) for e in logistique_events)
            print(f"Mike7 max Logistique score: {max_logi_score}")
            assert max_logi_score >= high_score_threshold, f"Mike7 should have high score for Logistique events, got {max_logi_score}"
        
        if proprete_events:
            max_prop_score = max(e.get("match_score", 0) for e in proprete_events)
            print(f"Mike7 max Propreté score: {max_prop_score}")
            assert max_prop_score >= high_score_threshold, f"Mike7 should have high score for Propreté events, got {max_prop_score}"
    
    def test_fanny95_scores_high_for_petite_enfance(self):
        """
        Fanny95 has skills related to:
        - Accompagnement de l'enfant (repas, jeux, sieste, change)
        - Observation des besoins de l'enfant
        - Garde d'enfants à domicile
        
        Should have high scores for Petite Enfance & Social events
        """
        response = requests.get(
            f"{BASE_URL}/api/jobdating/events",
            params={"token": FANNY95_TOKEN},
            timeout=15
        )
        assert response.status_code == 200
        
        events = response.json().get("events", [])
        
        # Find petite enfance events
        enfance_events = [e for e in events if any("Petite Enfance" in s or "Social" in s for s in e.get("sectors", []))]
        
        if enfance_events:
            max_enfance_score = max(e.get("match_score", 0) for e in enfance_events)
            print(f"Fanny95 max Petite Enfance score: {max_enfance_score}")
            assert max_enfance_score >= 25, f"Fanny95 should have high score for Petite Enfance events, got {max_enfance_score}"
    
    def test_mike7_top_events_are_relevant(self):
        """Mike7's top 3 events should be from his sectors"""
        response = requests.get(
            f"{BASE_URL}/api/jobdating/events",
            params={"token": MIKE7_TOKEN},
            timeout=15
        )
        events = response.json().get("events", [])
        
        # Top 3 events (already sorted by score)
        top_3 = events[:3]
        
        mike7_sectors = ["Restauration", "Logistique", "Propreté", "Hôtellerie"]
        
        relevant_count = 0
        for event in top_3:
            event_sectors = event.get("sectors", [])
            for sector in event_sectors:
                if any(ms.lower() in sector.lower() for ms in mike7_sectors):
                    relevant_count += 1
                    break
        
        print(f"Mike7 top 3 events: {[e.get('title', '')[:50] for e in top_3]}")
        print(f"Relevant count: {relevant_count}/3")
        
        # At least 2 of top 3 should be relevant
        assert relevant_count >= 2, f"At least 2 of top 3 events should be relevant to mike7's profile, got {relevant_count}"


class TestEventStructure:
    """Test event data structure"""
    
    def test_event_has_all_required_fields(self):
        """Each event should have all required fields"""
        response = requests.get(
            f"{BASE_URL}/api/jobdating/events",
            params={"token": MIKE7_TOKEN},
            timeout=15
        )
        events = response.json().get("events", [])
        
        required_fields = [
            "id", "title", "city", "event_type", "mode", "source",
            "sectors", "jobs_targeted", "match_score", "match_level",
            "ai_reason", "start_datetime", "end_datetime"
        ]
        
        for event in events[:5]:  # Check first 5 events
            for field in required_fields:
                assert field in event, f"Event missing required field: {field}"
            
            # Verify match_level is valid
            assert event["match_level"] in ["fort", "moyen", "faible"], f"Invalid match_level: {event['match_level']}"
            
            # Verify match_score is in valid range
            assert 0 <= event["match_score"] <= 100, f"match_score out of range: {event['match_score']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
