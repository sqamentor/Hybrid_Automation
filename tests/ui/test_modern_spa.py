"""
Example: Modern SPA Tests (Auto-routed to Playwright)

These tests demonstrate modern single-page application testing.
Framework will automatically select Playwright based on markers.
"""

import pytest


@pytest.mark.smoke
@pytest.mark.module("dashboard")
@pytest.mark.modern_spa
@pytest.mark.ui_framework("React")
class TestModernDashboard:
    """Test modern React dashboard - uses Playwright"""

    def test_user_dashboard_loads(self, ui_engine, ui_url):
        """Verify user dashboard loads correctly"""
        # Navigate
        ui_engine.navigate(f"{ui_url}/dashboard")

        # Verify page loaded
        assert ui_engine.is_visible("#dashboard-container")
        assert "Dashboard" in ui_engine.get_title()

    def test_dashboard_widgets_visible(self, ui_engine, ui_url):
        """Verify all dashboard widgets are visible"""
        ui_engine.navigate(f"{ui_url}/dashboard")

        # Check widgets
        assert ui_engine.is_visible("#sales-widget")
        assert ui_engine.is_visible("#orders-widget")
        assert ui_engine.is_visible("#analytics-widget")

    @pytest.mark.api_validation
    def test_dashboard_data_loads_from_api(self, ui_engine, api_client, ui_url):
        """Verify dashboard loads data from API"""
        # Navigate to dashboard
        ui_engine.navigate(f"{ui_url}/dashboard")

        # Verify API was called (in real impl, capture from network)
        response = api_client.get("/api/dashboard/summary")
        api_client.assert_status_code(200)

        data = response.json()
        assert "total_sales" in data
        assert "total_orders" in data


@pytest.mark.regression
@pytest.mark.module("catalog")
@pytest.mark.modern_spa
@pytest.mark.ui_framework("Vue")
class TestProductCatalog:
    """Test product catalog - uses Playwright for Vue SPA"""

    def test_product_search(self, ui_engine, ui_url):
        """Test product search functionality"""
        ui_engine.navigate(f"{ui_url}/products")

        # Search for product
        ui_engine.fill("#search-input", "laptop")
        ui_engine.click("#search-button")

        # Verify results
        ui_engine.wait_for_element(".product-card")
        assert ui_engine.is_visible(".product-card")

    @pytest.mark.mobile
    def test_mobile_product_view(self, ui_engine, ui_url):
        """Test product view on mobile (uses Playwright mobile emulation)"""
        # Mobile testing - Playwright handles this better
        ui_engine.navigate(f"{ui_url}/products/123")

        assert ui_engine.is_visible("#product-details")
        assert ui_engine.is_visible("#add-to-cart-mobile")


@pytest.mark.critical
@pytest.mark.module("checkout")
@pytest.mark.modern_spa
class TestCheckoutFlow:
    """Critical checkout tests - Playwright for speed"""

    def test_add_to_cart(self, ui_engine, ui_url):
        """Test adding product to cart"""
        ui_engine.navigate(f"{ui_url}/products/123")
        ui_engine.click("#add-to-cart")

        # Verify cart updated
        assert ui_engine.is_visible(".cart-notification")
        cart_count = ui_engine.get_text("#cart-count")
        assert int(cart_count) > 0

    def test_cart_checkout_navigation(self, ui_engine, ui_url):
        """Test navigation from cart to checkout"""
        ui_engine.navigate(f"{ui_url}/cart")
        ui_engine.click("#proceed-to-checkout")

        # Verify on checkout page
        assert "/checkout" in ui_engine.get_current_url()
        assert ui_engine.is_visible("#checkout-form")
