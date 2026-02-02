"""
Unit Tests for API Interceptor

Tests the APIInterceptor functionality.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from framework.api.api_interceptor import APIInterceptor


@pytest.mark.modern_spa
@pytest.mark.unit
class TestAPIInterceptor:
    """Test APIInterceptor class"""

    def test_initialization(self):
        """Test interceptor initialization"""
        ui_engine = Mock()
        ui_engine.__class__.__name__ = "PlaywrightEngine"

        interceptor = APIInterceptor(ui_engine)

        assert interceptor.ui_engine == ui_engine
        assert interceptor.enabled == True
        assert len(interceptor.captured_requests) == 0
        assert len(interceptor.captured_responses) == 0

    def test_add_filter(self):
        """Test adding URL filter"""
        ui_engine = Mock()
        ui_engine.__class__.__name__ = "PlaywrightEngine"

        interceptor = APIInterceptor(ui_engine)
        interceptor.add_filter(lambda url: "/api/" in url)

        assert len(interceptor.filters) == 1

    def test_filter_by_pattern(self):
        """Test pattern-based filtering"""
        ui_engine = Mock()
        ui_engine.__class__.__name__ = "PlaywrightEngine"

        interceptor = APIInterceptor(ui_engine)
        interceptor.filter_by_pattern("/api/v1/")

        assert interceptor._should_capture("https://example.com/api/v1/users") == True
        assert interceptor._should_capture("https://example.com/page.html") == False

    def test_should_capture_no_filters(self):
        """Test capture logic with no filters"""
        ui_engine = Mock()
        ui_engine.__class__.__name__ = "PlaywrightEngine"

        interceptor = APIInterceptor(ui_engine)

        # Without filters, should capture all
        assert interceptor._should_capture("https://example.com/any-url") == True

    def test_should_capture_with_filters(self):
        """Test capture logic with filters"""
        ui_engine = Mock()
        ui_engine.__class__.__name__ = "PlaywrightEngine"

        interceptor = APIInterceptor(ui_engine)
        interceptor.add_filter(lambda url: "/api/" in url)
        interceptor.add_filter(lambda url: ".json" in url)

        # Should capture if ANY filter matches
        assert interceptor._should_capture("https://example.com/api/users") == True
        assert interceptor._should_capture("https://example.com/data.json") == True
        assert interceptor._should_capture("https://example.com/page.html") == False

    def test_get_captured_requests(self):
        """Test retrieving captured requests"""
        ui_engine = Mock()
        ui_engine.__class__.__name__ = "PlaywrightEngine"

        interceptor = APIInterceptor(ui_engine)
        interceptor.captured_requests = [
            {"method": "GET", "url": "https://api.example.com/users"},
            {"method": "POST", "url": "https://api.example.com/orders"},
        ]

        requests = interceptor.get_captured_requests()
        assert len(requests) == 2
        assert requests[0]["method"] == "GET"

    def test_get_requests_by_method(self):
        """Test filtering requests by method"""
        ui_engine = Mock()
        ui_engine.__class__.__name__ = "PlaywrightEngine"

        interceptor = APIInterceptor(ui_engine)
        interceptor.captured_requests = [
            {"method": "GET", "url": "https://api.example.com/users"},
            {"method": "POST", "url": "https://api.example.com/orders"},
            {"method": "GET", "url": "https://api.example.com/products"},
        ]

        get_requests = interceptor.get_requests_by_method("GET")
        assert len(get_requests) == 2
        assert all(r["method"] == "GET" for r in get_requests)

    def test_get_requests_by_url_pattern(self):
        """Test filtering requests by URL pattern"""
        ui_engine = Mock()
        ui_engine.__class__.__name__ = "PlaywrightEngine"

        interceptor = APIInterceptor(ui_engine)
        interceptor.captured_requests = [
            {"method": "GET", "url": "https://api.example.com/users"},
            {"method": "GET", "url": "https://api.example.com/orders"},
            {"method": "GET", "url": "https://example.com/page.html"},
        ]

        api_requests = interceptor.get_requests_by_url_pattern("api.example.com")
        assert len(api_requests) == 2

    def test_find_api_calls(self):
        """Test finding API calls"""
        ui_engine = Mock()
        ui_engine.__class__.__name__ = "PlaywrightEngine"

        interceptor = APIInterceptor(ui_engine)
        interceptor.captured_requests = [
            {"method": "GET", "url": "https://example.com/api/users"},
            {"method": "GET", "url": "https://example.com/page.html"},
        ]

        api_calls = interceptor.find_api_calls()
        assert len(api_calls) == 1
        assert "/api/" in api_calls[0]["url"]

    def test_get_correlation_data(self):
        """Test extracting correlation data"""
        ui_engine = Mock()
        ui_engine.__class__.__name__ = "PlaywrightEngine"

        interceptor = APIInterceptor(ui_engine)
        interceptor.captured_responses = [
            {
                "url": "https://api.example.com/orders",
                "body": {
                    "order_id": "ORD-12345",
                    "transaction_id": "TXN-67890",
                    "customer_id": "CUST-111",
                },
            }
        ]

        correlation_data = interceptor.get_correlation_data()
        assert correlation_data["order_id"] == "ORD-12345"
        assert correlation_data["transaction_id"] == "TXN-67890"
        assert correlation_data["customer_id"] == "CUST-111"

    def test_clear(self):
        """Test clearing captured data"""
        ui_engine = Mock()
        ui_engine.__class__.__name__ = "PlaywrightEngine"

        interceptor = APIInterceptor(ui_engine)
        interceptor.captured_requests = [{"method": "GET"}]
        interceptor.captured_responses = [{"status": 200}]

        interceptor.clear()

        assert len(interceptor.captured_requests) == 0
        assert len(interceptor.captured_responses) == 0

    def test_enable_disable(self):
        """Test enabling/disabling interception"""
        ui_engine = Mock()
        ui_engine.__class__.__name__ = "PlaywrightEngine"

        interceptor = APIInterceptor(ui_engine)

        assert interceptor.enabled == True

        interceptor.disable()
        assert interceptor.enabled == False

        interceptor.enable()
        assert interceptor.enabled == True

    def test_get_summary(self):
        """Test getting summary of captured data"""
        ui_engine = Mock()
        ui_engine.__class__.__name__ = "PlaywrightEngine"

        interceptor = APIInterceptor(ui_engine)
        interceptor.captured_requests = [
            {"method": "GET", "url": "https://api.example.com/users"},
            {"method": "POST", "url": "https://api.example.com/orders"},
            {"method": "GET", "url": "https://api.example.com/products"},
        ]
        interceptor.captured_responses = [
            {"status": 200, "url": "https://api.example.com/users"},
            {"status": 201, "url": "https://api.example.com/orders"},
            {"status": 200, "url": "https://api.example.com/products"},
        ]

        summary = interceptor.get_summary()

        assert summary["total_requests"] == 3
        assert summary["total_responses"] == 3
        assert summary["methods"]["GET"] == 2
        assert summary["methods"]["POST"] == 1
        assert summary["status_codes"][200] == 2
        assert summary["status_codes"][201] == 1
