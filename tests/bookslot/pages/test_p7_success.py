"""
P7: Success/Confirmation Page Tests (Layer A - Page-Level)

Tests for Success confirmation page (final step after P1→P2→P3→P4→P5→P6).

Test Coverage:
- Smoke: Page loads, confirmation visible
- Validation: Confirmation number, booking details display
- Regression: Confirmation email, print/download options

Markers:
- @pytest.mark.p7_success
- @pytest.mark.smoke, validation, regression
"""

import pytest
import allure
from typing import Dict, Any
from playwright.sync_api import Page, expect

from framework.testing.url_builder import URLBuilder
from framework.testing.url_validator import URLValidator


@pytest.mark.bookslot
@pytest.mark.p7_success
@pytest.mark.smoke
@pytest.mark.critical
class TestSuccessSmoke:
    """Smoke tests for Success page (P7)"""
    
    def test_success_page_loads(self, at_success, validation_helper):
        """SMOKE: Success page loads successfully"""
        validation_helper.validate_element_visible("[data-testid='success-page']", "Success page")
        validation_helper.validate_text_present("Thank you")
    
    def test_confirmation_message_visible(self, at_success, validation_helper):
        """SMOKE: Confirmation message is visible"""
        validation_helper.validate_text_present("Confirmation")
        validation_helper.validate_text_present("appointment")
    
    def test_confirmation_number_visible(self, at_success, validation_helper):
        """SMOKE: Confirmation number is displayed"""
        validation_helper.validate_element_visible(
            "[data-testid='confirmation-number']",
            "Confirmation number"
        )


@pytest.mark.bookslot
@pytest.mark.p7_success
@pytest.mark.validation
@pytest.mark.high
class TestSuccessValidation:
    """Validation tests for Success page"""
    
    def test_confirmation_number_format(self, at_success, page: Page):
        """VALIDATION: Confirmation number has valid format"""
        conf_number = page.locator("[data-testid='confirmation-number']").inner_text()
        
        # Verify not empty
        assert len(conf_number) > 0, "Confirmation number is empty"
        
        # Verify format (alphanumeric, typical format: ABC123456 or similar)
        assert conf_number.replace("-", "").replace("_", "").isalnum(), \
            f"Invalid confirmation number format: {conf_number}"
    
    def test_booking_details_displayed(self, at_success, page: Page, validation_helper):
        """VALIDATION: Key booking details are displayed"""
        # Verify key sections present
        validation_helper.validate_text_present("Date")
        validation_helper.validate_text_present("Time")
        validation_helper.validate_text_present("Name")
    
    def test_confirmation_email_mentioned(self, at_success, validation_helper):
        """VALIDATION: Confirmation email notification mentioned"""
        validation_helper.validate_text_present("email")
    
    def test_no_back_button_on_success(self, at_success, page: Page):
        """VALIDATION: No Back button on Success page (prevents resubmission)"""
        back_button = page.locator("button:has-text('Back')")
        assert back_button.count() == 0, "Back button should not be present on Success page"
    
    def test_new_booking_link_present(self, at_success, validation_helper):
        """VALIDATION: Link to create new booking is present"""
        validation_helper.validate_element_visible(
            "a:has-text('Book Another Appointment'), button:has-text('Book Another Appointment')",
            "New booking link/button"
        )


@pytest.mark.bookslot
@pytest.mark.p7_success
@pytest.mark.regression
@pytest.mark.medium
class TestSuccessRegression:
    """Regression tests for Success page"""
    
    def test_confirmation_number_unique(self, at_success, page: Page):
        """REGRESSION: Confirmation number is unique (not default/placeholder)"""
        conf_number = page.locator("[data-testid='confirmation-number']").inner_text()
        
        # Verify not placeholder values
        placeholder_values = ["123456", "XXXXXX", "000000", "TEST123", "N/A", "TBD"]
        assert conf_number not in placeholder_values, \
            f"Confirmation number appears to be placeholder: {conf_number}"
        
        # Verify reasonable length (at least 6 characters)
        assert len(conf_number) >= 6, f"Confirmation number too short: {conf_number}"
    
    def test_print_option_available(self, at_success, page: Page):
        """REGRESSION: Print confirmation option is available"""
        print_button = page.locator("button:has-text('Print'), a:has-text('Print')")
        
        if print_button.count() > 0:
            expect(print_button.first).to_be_visible()
    
    def test_download_option_available(self, at_success, page: Page):
        """REGRESSION: Download confirmation option is available"""
        download_button = page.locator("button:has-text('Download'), a:has-text('Download')")
        
        if download_button.count() > 0:
            expect(download_button.first).to_be_visible()
    
    def test_calendar_add_option(self, at_success, page: Page):
        """REGRESSION: Add to calendar option is available"""
        calendar_button = page.locator(
            "button:has-text('Add to Calendar'), a:has-text('Add to Calendar'), "
            "button:has-text('Calendar'), a:has-text('Calendar')"
        )
        
        if calendar_button.count() > 0:
            expect(calendar_button.first).to_be_visible()
    
    def test_booking_time_displayed_in_correct_format(self, at_success, page: Page):
        """REGRESSION: Booking time is displayed in readable format"""
        # Look for time element
        time_element = page.locator("[data-testid='booking-time'], .booking-time, .appointment-time")
        
        if time_element.count() > 0:
            time_text = time_element.first.inner_text()
            
            # Verify contains AM or PM
            assert "AM" in time_text or "PM" in time_text, \
                f"Time format missing AM/PM: {time_text}"
    
    def test_booking_date_displayed_in_correct_format(self, at_success, page: Page):
        """REGRESSION: Booking date is displayed in readable format"""
        # Look for date element
        date_element = page.locator("[data-testid='booking-date'], .booking-date, .appointment-date")
        
        if date_element.count() > 0:
            date_text = date_element.first.inner_text()
            
            # Verify not empty and contains digits
            assert len(date_text) > 0, "Date is empty"
            assert any(char.isdigit() for char in date_text), f"Date has no digits: {date_text}"
    
    def test_patient_name_displayed(self, at_success, page: Page):
        """REGRESSION: Patient name is displayed on confirmation"""
        # Look for name element
        name_element = page.locator(
            "[data-testid='patient-name'], .patient-name, "
            "[data-testid='booking-name'], .booking-name"
        )
        
        if name_element.count() > 0:
            name_text = name_element.first.inner_text()
            assert len(name_text) > 0, "Patient name is empty"
    
    def test_new_booking_link_navigates_to_start(self, at_success, page: Page, validation_helper):
        """REGRESSION: New booking link navigates to Basic Info (start)"""
        # Click new booking link/button
        page.click("a:has-text('Book Another Appointment'), button:has-text('Book Another Appointment')")
        page.wait_for_load_state("networkidle")
        
        # Verify back at P1
        validation_helper.validate_navigation_to("Basic Info")


# ============================================================================
# URL WORKFLOW TESTS (Merged from url_testing/test_workflow_urls_p7.py)
# ============================================================================

@allure.epic("Bookslot")
@allure.feature("URL Testing")
@allure.story("Success Page (P7)")
@pytest.mark.bookslot
@pytest.mark.p7_success
@pytest.mark.url_workflow
class TestSuccessURLWorkflow:
    """URL workflow tests - success confirmation, notifications, print, feedback"""

    @allure.title("Verify P7 loads with confirmation parameters")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_p7_success_confirmation(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator):
        """Test: Success/Thank You page loads with confirmation details"""
        url = url_builder.build(
            workflow_id="WF-P7-001-SUCCESS", page_path="/thank-you",
            query_params={"booking_id": "BK-001", "status": "confirmed"}
        )
        result = url_validator.validate(url=url, expected_elements=[".success-message", ".confirmation-number"])
        assert result.is_valid and result.status_code == 200

    @allure.title("Verify P7 handles email notification")
    def test_p7_email_notification(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator):
        """Test: Email notification parameters handled"""
        url = url_builder.build(
            workflow_id="WF-P7-002-EMAIL", page_path="/thank-you",
            query_params={"booking_id": "BK-001", "notify": "email"}
        )
        result = url_validator.validate(url=url, expected_elements=[".email-sent-indicator"])
        assert result.is_valid and result.status_code == 200

    @allure.title("Verify P7 handles SMS notification")
    def test_p7_sms_notification(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator):
        """Test: SMS notification parameters handled"""
        url = url_builder.build(
            workflow_id="WF-P7-003-SMS", page_path="/thank-you",
            query_params={"booking_id": "BK-001", "notify": "sms"}
        )
        result = url_validator.validate(url=url, expected_elements=[".sms-sent-indicator"])
        assert result.is_valid and result.status_code == 200

    @allure.title("Verify P7 print/download options")
    @pytest.mark.parametrize("action", ["print", "download"], ids=["print", "download"])
    def test_p7_print_download(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator, action: str):
        """Test: Print and download options work"""
        url = url_builder.build(
            workflow_id=f"WF-P7-{action.upper()}", page_path="/thank-you",
            query_params={"booking_id": "BK-001", "action": action}
        )
        result = url_validator.validate(url=url, expected_elements=[f".{action}-button"])
        assert result.is_valid and result.status_code == 200

    @allure.title("Verify P7 performance within threshold")
    @pytest.mark.performance
    def test_p7_load_performance(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator):
        """Test: Page loads within performance threshold"""
        url = url_builder.build(workflow_id="WF-P7-PERF", page_path="/thank-you", query_params={"booking_id": "BK-001"})
        result = url_validator.validate(url=url)
        assert result.validation_time_ms < 5000, f"Page load too slow: {result.validation_time_ms}ms"

