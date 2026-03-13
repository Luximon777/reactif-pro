"""
Ubuntoo Intelligence API Tests
Tests the new Ubuntoo integration feature including:
- Ubuntoo dashboard with stats, signals, exchanges, insights
- Signal filtering and details with cross-references
- Signal validation flow
- AI analysis trigger
- Insights retrieval
- Cross-reference data
"""

import pytest
import requests
import os
import time

# Get base URL from environment - NO default value
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestUbuntooSetup:
    """Setup tests - ensure seed data is in place"""
    
    def test_seed_ubuntoo_data(self):
        """Seed database to ensure Ubuntoo data exists"""
        response = requests.post(f"{BASE_URL}/api/seed")
        assert response.status_code == 200
        data = response.json()
        
        # Verify Ubuntoo data was created
        assert "ubuntoo_exchanges" in data
        assert "ubuntoo_signals" in data
        assert "ubuntoo_insights" in data
        assert data["ubuntoo_exchanges"] == 10
        assert data["ubuntoo_signals"] == 8
        assert data["ubuntoo_insights"] == 4
        print(f"✓ Ubuntoo seed data created: {data['ubuntoo_exchanges']} exchanges, {data['ubuntoo_signals']} signals, {data['ubuntoo_insights']} insights")


class TestUbuntooDashboard:
    """Test GET /api/ubuntoo/dashboard - main dashboard endpoint"""
    
    def test_get_dashboard(self):
        """Get Ubuntoo dashboard with all stats"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/dashboard")
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "stats" in data
        assert "by_type" in data
        assert "top_signals" in data
        assert "recent_exchanges" in data
        assert "insights" in data
        
        # Verify stats structure
        stats = data["stats"]
        assert "total_exchanges_analyzed" in stats
        assert "total_signals_detected" in stats
        assert "signals_detected" in stats
        assert "signals_analyzed_ia" in stats
        assert "signals_validated_human" in stats
        assert "signals_integrated" in stats
        
        # Verify data was loaded
        assert stats["total_exchanges_analyzed"] >= 10
        assert stats["total_signals_detected"] >= 8
        
        # Verify top_signals is list with expected structure
        assert isinstance(data["top_signals"], list)
        if len(data["top_signals"]) > 0:
            signal = data["top_signals"][0]
            assert "id" in signal
            assert "name" in signal
            assert "signal_type" in signal
            assert "mention_count" in signal
        
        # Verify recent_exchanges is list
        assert isinstance(data["recent_exchanges"], list)
        if len(data["recent_exchanges"]) > 0:
            exchange = data["recent_exchanges"][0]
            assert "id" in exchange
            assert "exchange_type" in exchange
            assert "content_summary" in exchange
        
        # Verify insights is list
        assert isinstance(data["insights"], list)
        if len(data["insights"]) > 0:
            insight = data["insights"][0]
            assert "id" in insight
            assert "title" in insight
            assert "insight_type" in insight
        
        print(f"✓ Dashboard retrieved: {stats['total_exchanges_analyzed']} exchanges, {stats['total_signals_detected']} signals")


class TestUbuntooSignals:
    """Test /api/ubuntoo/signals endpoints"""
    
    def test_get_all_signals(self):
        """Get all Ubuntoo signals"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/signals")
        assert response.status_code == 200
        signals = response.json()
        
        assert isinstance(signals, list)
        assert len(signals) >= 8  # seeded 8 signals
        
        # Verify signal structure
        signal = signals[0]
        assert "id" in signal
        assert "signal_type" in signal
        assert "name" in signal
        assert "description" in signal
        assert "mention_count" in signal
        assert "validation_status" in signal
        assert "related_jobs" in signal
        assert "related_sectors" in signal
        
        print(f"✓ Retrieved {len(signals)} Ubuntoo signals")
    
    def test_filter_signals_by_type(self):
        """Filter signals by signal_type"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/signals?signal_type=competence_emergente")
        assert response.status_code == 200
        signals = response.json()
        
        # All returned signals should have matching type
        for signal in signals:
            assert signal["signal_type"] == "competence_emergente"
        
        print(f"✓ Filtered by type: {len(signals)} competence_emergente signals")
    
    def test_filter_signals_by_status(self):
        """Filter signals by validation_status"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/signals?status=detectee")
        assert response.status_code == 200
        signals = response.json()
        
        for signal in signals:
            assert signal["validation_status"] == "detectee"
        
        print(f"✓ Filtered by status: {len(signals)} detected signals")
    
    def test_filter_signals_by_sector(self):
        """Filter signals by sector"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/signals?sector=Informatique")
        assert response.status_code == 200
        signals = response.json()
        
        # Signals should have Informatique in related_sectors
        for signal in signals:
            assert "Informatique" in signal.get("related_sectors", [])
        
        print(f"✓ Filtered by sector: {len(signals)} Informatique signals")


class TestUbuntooSignalDetail:
    """Test GET /api/ubuntoo/signals/{id} - signal detail with cross-references"""
    
    def test_get_signal_detail(self):
        """Get detailed signal with cross-references"""
        # First get signals list to get an ID
        list_response = requests.get(f"{BASE_URL}/api/ubuntoo/signals")
        signals = list_response.json()
        assert len(signals) > 0, "No signals found"
        
        signal_id = signals[0]["id"]
        
        # Get detail
        response = requests.get(f"{BASE_URL}/api/ubuntoo/signals/{signal_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "signal" in data
        assert "linked_observatory_skills" in data
        assert "linked_evolution_jobs" in data
        assert "related_exchanges" in data
        
        # Verify signal data
        signal = data["signal"]
        assert signal["id"] == signal_id
        assert "name" in signal
        assert "description" in signal
        
        # Cross-references should be lists
        assert isinstance(data["linked_observatory_skills"], list)
        assert isinstance(data["linked_evolution_jobs"], list)
        assert isinstance(data["related_exchanges"], list)
        
        print(f"✓ Signal detail retrieved: {signal['name']} with {len(data['related_exchanges'])} related exchanges")
    
    def test_signal_not_found(self):
        """Test 404 for non-existent signal"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/signals/non_existent_id_12345")
        assert response.status_code == 404
        print(f"✓ Non-existent signal returns 404")


class TestUbuntooSignalValidation:
    """Test POST /api/ubuntoo/signals/{id}/validate - validation flow"""
    
    def test_validate_signal_approve(self):
        """Validate a signal (approve)"""
        # Get a signal to validate
        list_response = requests.get(f"{BASE_URL}/api/ubuntoo/signals")
        signals = list_response.json()
        
        # Find a signal that's not already integrated
        target_signal = None
        for s in signals:
            if s["validation_status"] not in ["integree", "rejetee"]:
                target_signal = s
                break
        
        if target_signal is None:
            pytest.skip("No signals available for validation")
        
        signal_id = target_signal["id"]
        
        # Validate with approval
        response = requests.post(
            f"{BASE_URL}/api/ubuntoo/signals/{signal_id}/validate?approved=true&notes=Test validation"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["status"] == "validee_humain"
        
        print(f"✓ Signal validated (approved): {signal_id}")
    
    def test_validate_signal_reject(self):
        """Validate a signal (reject)"""
        # Reseed to get fresh data
        requests.post(f"{BASE_URL}/api/seed")
        
        # Get a signal to reject
        list_response = requests.get(f"{BASE_URL}/api/ubuntoo/signals")
        signals = list_response.json()
        
        # Find a signal that's not already rejected
        target_signal = None
        for s in signals:
            if s["validation_status"] not in ["integree", "rejetee"]:
                target_signal = s
                break
        
        if target_signal is None:
            pytest.skip("No signals available for validation")
        
        signal_id = target_signal["id"]
        
        # Validate with rejection
        response = requests.post(
            f"{BASE_URL}/api/ubuntoo/signals/{signal_id}/validate?approved=false&notes=Not relevant"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejetee"
        
        print(f"✓ Signal validated (rejected): {signal_id}")


class TestUbuntooAnalyze:
    """Test POST /api/ubuntoo/analyze - AI analysis trigger"""
    
    def test_trigger_analysis(self):
        """Trigger AI analysis of Ubuntoo exchanges"""
        response = requests.post(f"{BASE_URL}/api/ubuntoo/analyze", timeout=60)
        assert response.status_code == 200
        data = response.json()
        
        # Response has analysis nested in 'analysis' key
        assert "message" in data
        assert "exchanges_analyzed" in data
        assert "analysis" in data
        
        analysis = data["analysis"]
        assert "detected_skills" in analysis
        assert "detected_tools" in analysis
        assert "detected_practices" in analysis
        assert "confidence" in analysis
        
        print(f"✓ AI analysis triggered: {len(analysis['detected_skills'])} skills, {len(analysis['detected_tools'])} tools detected")


class TestUbuntooInsights:
    """Test GET /api/ubuntoo/insights - cross-referenced insights"""
    
    def test_get_insights(self):
        """Get Ubuntoo insights"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/insights")
        assert response.status_code == 200
        insights = response.json()
        
        assert isinstance(insights, list)
        assert len(insights) >= 4  # seeded 4 insights
        
        # Verify insight structure
        if len(insights) > 0:
            insight = insights[0]
            assert "id" in insight
            assert "insight_type" in insight
            assert "title" in insight
            assert "description" in insight
            assert "priority" in insight
            assert "recommendation" in insight
        
        print(f"✓ Retrieved {len(insights)} insights")


class TestUbuntooCrossReference:
    """Test GET /api/ubuntoo/cross-reference - cross-reference data"""
    
    def test_get_cross_reference(self):
        """Get cross-reference data between Ubuntoo and Observatory"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/cross-reference")
        assert response.status_code == 200
        data = response.json()
        
        # Should return some cross-reference data structure
        assert isinstance(data, (dict, list))
        
        print(f"✓ Cross-reference data retrieved")


class TestUbuntooIntegrationFlow:
    """Test full integration flow: detection -> validation -> integration"""
    
    def test_full_validation_flow(self):
        """Test the complete signal validation pipeline"""
        # 1. Reseed to get fresh data
        seed_response = requests.post(f"{BASE_URL}/api/seed")
        assert seed_response.status_code == 200
        
        # 2. Get dashboard to see initial stats
        dashboard_response = requests.get(f"{BASE_URL}/api/ubuntoo/dashboard")
        initial_stats = dashboard_response.json()["stats"]
        
        # 3. Get a detected signal
        signals_response = requests.get(f"{BASE_URL}/api/ubuntoo/signals?status=detectee")
        signals = signals_response.json()
        
        if len(signals) == 0:
            signals_response = requests.get(f"{BASE_URL}/api/ubuntoo/signals")
            signals = signals_response.json()
            # Find any non-integrated signal
            signals = [s for s in signals if s["validation_status"] != "integree"]
        
        if len(signals) == 0:
            pytest.skip("No signals available for integration test")
        
        signal_id = signals[0]["id"]
        signal_name = signals[0]["name"]
        
        # 4. Validate the signal
        validate_response = requests.post(
            f"{BASE_URL}/api/ubuntoo/signals/{signal_id}/validate?approved=true&notes=Integration test"
        )
        assert validate_response.status_code == 200
        
        # 5. Verify signal status changed
        detail_response = requests.get(f"{BASE_URL}/api/ubuntoo/signals/{signal_id}")
        updated_signal = detail_response.json()["signal"]
        assert updated_signal["validation_status"] in ["validee_humain", "integree"]
        
        print(f"✓ Full validation flow completed for signal: {signal_name}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
