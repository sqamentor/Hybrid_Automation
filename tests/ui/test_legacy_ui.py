"""
Example: Legacy UI Tests (Auto-routed to Selenium)

These tests demonstrate legacy application testing.
Framework will automatically select Selenium based on markers.
"""

import pytest


@pytest.mark.selenium
@pytest.mark.regression
@pytest.mark.module("admin")
@pytest.mark.legacy_ui
@pytest.mark.auth_type("SSO")
class TestAdminPanel:
    """Test admin panel - uses Selenium for SSO and legacy UI"""

    def test_admin_login_sso(self, ui_engine, ui_url):
        """Test SSO login to admin panel - Selenium handles SSO better"""
        ui_engine.navigate(f"{ui_url}/admin")

        # SSO redirect handling
        # Selenium is more reliable for complex auth flows
        ui_engine.wait_for_element("#sso-username", timeout=15)
        ui_engine.fill("#sso-username", "admin@example.com")
        ui_engine.fill("#sso-password", "AdminPass123")
        ui_engine.click("#sso-submit")

        # Verify admin panel loaded
        ui_engine.wait_for_element("#admin-dashboard")
        assert ui_engine.is_visible("#admin-dashboard")

    def test_admin_iframe_navigation(self, ui_engine, ui_url):
        """Test navigation within iframes - Selenium handles iframes better"""
        ui_engine.navigate(f"{ui_url}/admin/reports")

        # Switch to iframe (common in legacy admin panels)
        # Note: This is simplified - real impl would use driver.switch_to.frame()
        ui_engine.wait_for_element("#reports-frame")

        # Verify content in iframe
        # Selenium's iframe handling is more mature
        pass


@pytest.mark.selenium
@pytest.mark.regression
@pytest.mark.module("backoffice")
@pytest.mark.legacy_ui
class TestBackofficeOperations:
    """Test back-office operations - Selenium for legacy JSP"""

    def test_user_management(self, ui_engine, ui_url):
        """Test user management page - legacy JSP application"""
        ui_engine.navigate(f"{ui_url}/backoffice/users")

        # Legacy form submission
        ui_engine.wait_for_element("#user-table")
        assert ui_engine.is_visible("#user-table")

    def test_long_running_report(self, ui_engine, ui_url):
        """Test long-running report generation - Selenium more stable for long sessions"""
        ui_engine.navigate(f"{ui_url}/backoffice/reports")

        # Generate report (takes time)
        ui_engine.click("#generate-report")

        # Wait for completion (long wait)
        # Selenium handles long sessions better
        ui_engine.wait_for_element("#report-complete", timeout=60)
        assert ui_engine.is_visible("#download-link")


@pytest.mark.selenium
@pytest.mark.critical
@pytest.mark.module("payment")
@pytest.mark.auth_type("MFA")
@pytest.mark.legacy_ui
class TestPaymentProcessing:
    """Payment tests - Selenium for MFA and security"""

    def test_payment_with_mfa(self, ui_engine, ui_url):
        """Test payment with MFA verification - Selenium for MFA support"""
        ui_engine.navigate(f"{ui_url}/payment")

        # Fill payment details
        ui_engine.fill("#card-number", "4111111111111111")
        ui_engine.fill("#expiry", "12/25")
        ui_engine.fill("#cvv", "123")
        ui_engine.click("#submit-payment")

        # MFA challenge
        ui_engine.wait_for_element("#mfa-code")
        ui_engine.fill("#mfa-code", "123456")
        ui_engine.click("#verify-mfa")

        # Verify payment processed
        ui_engine.wait_for_element("#payment-success")
        assert ui_engine.is_visible("#payment-success")
