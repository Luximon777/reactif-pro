"""
Test suite for Ubuntoo Community API endpoints
Tests GET/POST /api/ubuntoo/community/exchanges and dashboard integration
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://talent-insights-hub-1.preview.emergentagent.com').rstrip('/')


class TestUbuntooCommunityExchanges:
    """Tests for GET /api/ubuntoo/community/exchanges endpoint"""
    
    def test_get_exchanges_returns_list(self):
        """GET /api/ubuntoo/community/exchanges returns a list of exchanges"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/community/exchanges")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET exchanges returned {len(data)} exchanges")
    
    def test_exchanges_have_required_fields(self):
        """Each exchange has required fields including group"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/community/exchanges")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0, "Should have at least one exchange"
        
        required_fields = ['id', 'exchange_type', 'group', 'content_summary', 'author', 'timestamp']
        for exchange in data[:3]:  # Check first 3
            for field in required_fields:
                assert field in exchange, f"Exchange missing field: {field}"
        print(f"✓ Exchanges have all required fields including 'group'")
    
    def test_filter_by_group(self):
        """GET /api/ubuntoo/community/exchanges?group=numerique filters correctly"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/community/exchanges?group=numerique")
        assert response.status_code == 200
        data = response.json()
        for exchange in data:
            assert exchange.get('group') == 'numerique', f"Expected group 'numerique', got '{exchange.get('group')}'"
        print(f"✓ Filter by group=numerique returned {len(data)} exchanges")
    
    def test_filter_by_exchange_type(self):
        """GET /api/ubuntoo/community/exchanges?exchange_type=question filters correctly"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/community/exchanges?exchange_type=question")
        assert response.status_code == 200
        data = response.json()
        for exchange in data:
            assert exchange.get('exchange_type') == 'question', f"Expected type 'question', got '{exchange.get('exchange_type')}'"
        print(f"✓ Filter by exchange_type=question returned {len(data)} exchanges")


class TestUbuntooPostExchange:
    """Tests for POST /api/ubuntoo/community/exchanges endpoint"""
    
    def test_post_exchange_success(self):
        """POST /api/ubuntoo/community/exchanges creates new exchange with AI detection"""
        payload = {
            "title": "Test Pytest - Compétences IA",
            "content": "Je travaille avec Python et TensorFlow pour créer des modèles de machine learning.",
            "exchange_type": "discussion",
            "group": "numerique",
            "author": "PytestUser"
        }
        response = requests.post(
            f"{BASE_URL}/api/ubuntoo/community/exchanges",
            json=payload,
            timeout=30  # AI analysis may take time
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert 'exchange' in data
        assert 'signals_detected' in data
        assert 'message' in data
        
        # Verify exchange data
        exchange = data['exchange']
        assert exchange['title'] == payload['title']
        assert exchange['group'] == payload['group']
        assert exchange['author'] == payload['author']
        assert 'detected_skills' in exchange
        assert 'detected_tools' in exchange
        assert 'id' in exchange
        
        print(f"✓ POST exchange created successfully with {data['signals_detected']} signals detected")
        print(f"  Detected skills: {exchange.get('detected_skills', [])}")
        print(f"  Detected tools: {exchange.get('detected_tools', [])}")
    
    def test_post_exchange_missing_title_fails(self):
        """POST without title returns 400"""
        payload = {
            "content": "Some content without title",
            "exchange_type": "discussion",
            "group": "reconversion"
        }
        response = requests.post(
            f"{BASE_URL}/api/ubuntoo/community/exchanges",
            json=payload
        )
        assert response.status_code == 400
        print("✓ POST without title correctly returns 400")
    
    def test_post_exchange_missing_content_fails(self):
        """POST without content returns 400"""
        payload = {
            "title": "Title without content",
            "exchange_type": "discussion",
            "group": "reconversion"
        }
        response = requests.post(
            f"{BASE_URL}/api/ubuntoo/community/exchanges",
            json=payload
        )
        assert response.status_code == 400
        print("✓ POST without content correctly returns 400")
    
    def test_post_exchange_appears_in_get(self):
        """New exchange appears in GET after POST"""
        unique_title = f"Pytest Unique Test {int(time.time())}"
        payload = {
            "title": unique_title,
            "content": "Testing that new exchanges appear in the list after posting.",
            "exchange_type": "question",
            "group": "reconversion",
            "author": "PytestVerify"
        }
        
        # POST new exchange
        post_response = requests.post(
            f"{BASE_URL}/api/ubuntoo/community/exchanges",
            json=payload,
            timeout=30
        )
        assert post_response.status_code == 200
        new_id = post_response.json()['exchange']['id']
        
        # GET and verify it appears
        get_response = requests.get(f"{BASE_URL}/api/ubuntoo/community/exchanges")
        assert get_response.status_code == 200
        exchanges = get_response.json()
        
        found = any(e['id'] == new_id for e in exchanges)
        assert found, f"New exchange {new_id} not found in GET response"
        print(f"✓ New exchange {new_id} appears in GET after POST")


class TestUbuntooDashboard:
    """Tests for GET /api/ubuntoo/dashboard endpoint"""
    
    def test_dashboard_returns_stats(self):
        """GET /api/ubuntoo/dashboard returns stats object"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/dashboard")
        assert response.status_code == 200
        data = response.json()
        
        assert 'stats' in data
        stats = data['stats']
        assert 'total_exchanges_analyzed' in stats
        assert 'total_signals_detected' in stats
        print(f"✓ Dashboard stats: {stats['total_exchanges_analyzed']} exchanges, {stats['total_signals_detected']} signals")
    
    def test_dashboard_has_signals_breakdown(self):
        """Dashboard includes signal type breakdown"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/dashboard")
        assert response.status_code == 200
        data = response.json()
        
        assert 'by_type' in data
        assert 'top_signals' in data
        assert 'recent_exchanges' in data
        print(f"✓ Dashboard has by_type, top_signals, recent_exchanges")
    
    def test_dashboard_updates_after_post(self):
        """Dashboard stats update after posting new exchange"""
        # Get initial stats
        initial = requests.get(f"{BASE_URL}/api/ubuntoo/dashboard").json()
        initial_count = initial['stats']['total_exchanges_analyzed']
        
        # Post new exchange
        payload = {
            "title": "Dashboard Update Test",
            "content": "Testing that dashboard updates with new data analytics skills.",
            "exchange_type": "discussion",
            "group": "numerique",
            "author": "DashboardTest"
        }
        post_response = requests.post(
            f"{BASE_URL}/api/ubuntoo/community/exchanges",
            json=payload,
            timeout=30
        )
        assert post_response.status_code == 200
        
        # Get updated stats
        updated = requests.get(f"{BASE_URL}/api/ubuntoo/dashboard").json()
        updated_count = updated['stats']['total_exchanges_analyzed']
        
        assert updated_count > initial_count, f"Expected count to increase from {initial_count}"
        print(f"✓ Dashboard updated: {initial_count} → {updated_count} exchanges")


class TestUbuntooSignals:
    """Tests for GET /api/ubuntoo/signals endpoint"""
    
    def test_get_signals_returns_list(self):
        """GET /api/ubuntoo/signals returns list of signals"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/signals")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET signals returned {len(data)} signals")
    
    def test_signals_have_required_fields(self):
        """Signals have required fields"""
        response = requests.get(f"{BASE_URL}/api/ubuntoo/signals")
        assert response.status_code == 200
        data = response.json()
        
        if len(data) > 0:
            required_fields = ['id', 'signal_type', 'name', 'mention_count', 'validation_status']
            for field in required_fields:
                assert field in data[0], f"Signal missing field: {field}"
            print(f"✓ Signals have all required fields")
        else:
            print("⚠ No signals to verify fields")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
