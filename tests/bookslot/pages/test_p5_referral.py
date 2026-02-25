"""
P5: Referral Source Page Tests (Layer A - Page-Level)

Tests for Referral Source selection page (requires P1→P2→P3→P4 completed).

Test Coverage:
- Smoke: Page loads, referral options visible
- Validation: Selection behavior, required validation, other field
- Regression: All referral sources, other field validation

Markers:
- @pytest.mark.p5_referral
- @pytest.mark.smoke, validation, regression
"""

import pytest
import allure
from typing import Dict, Any
from playwright.sync_api import Page, expect

from framework.testing.url_builder import URLBuilder
from framework.testing.url_validator import URLValidator


@pytest.mark.bookslot
@pytest.mark.p5_referral
@pytest.mark.smoke
@pytest.mark.critical
class TestReferralSmoke:
    """Smoke tests for Referral page (P5)"""
    
    def test_referral_page_loads(self, at_referral, validation_helper):
        """SMOKE: Referral page loads successfully"""
        validation_helper.validate_element_visible("h1", "Referral heading")
        validation_helper.validate_element_visible("[data-testid='referral-options']", "Referral options")
    
    def test_referral_sources_visible(self, at_referral, validation_helper):
        """SMOKE: All referral source options are visible"""
        validation_helper.validate_minimum_element_count(
            "[data-testid^='referral-source-']",
            minimum_count=1,
            description="Referral source options"
        )


@pytest.mark.bookslot
@pytest.mark.p5_referral
@pytest.mark.validation
@pytest.mark.high
class TestReferralValidation:
    """Validation tests for Referral page"""
    
    def test_referral_sources_clickable(self, at_referral, page: Page, validation_helper):
        """VALIDATION: All referral source options are clickable"""
        sources = page.locator("[data-testid^='referral-source-']")
        count = sources.count()
        
        for i in range(count):
            validation_helper.validate_element_enabled(
                f"[data-testid^='referral-source-']:nth-child({i+1})",
                f"Referral source {i+1}"
            )
    
    def test_referral_selection_required(self, at_referral, page: Page, validation_helper):
        """VALIDATION: Referral source selection is required"""
        # Try to proceed without selection
        page.click("button:has-text('Next')")
        validation_helper.validate_error_message_shown("required")
    
    def test_single_referral_selection(self, at_referral, page: Page):
        """VALIDATION: Only one referral source can be selected"""
        # Select first source
        page.click("[data-testid^='referral-source-']:first-child")
        
        # Select second source
        page.click("[data-testid^='referral-source-']:nth-child(2)")
        
        # Verify only one selected
        selected = page.locator("[data-testid^='referral-source-'][data-selected='true']")
        assert selected.count() == 1, f"Expected 1 selected, found {selected.count()}"
    
    def test_other_field_shows_when_other_selected(self, at_referral, page: Page, validation_helper):
        """VALIDATION: 'Other' field appears when 'Other' is selected"""
        # Select "Other" option
        page.click("[data-testid='referral-source-other']")
        
        # Verify "Other" text field is visible
        validation_helper.validate_element_visible(
            "[name='referralOther']",
            "Other referral source text field"
        )
    
    def test_other_field_required_when_other_selected(self, at_referral, page: Page, validation_helper):
        """VALIDATION: 'Other' field is required when 'Other' is selected"""
        # Select "Other"
        page.click("[data-testid='referral-source-other']")
        
        # Try to proceed without filling "Other" field
        page.click("button:has-text('Next')")
        
        # Verify error
        validation_helper.validate_required_field_error("[name='referralOther']")
    
    def test_referral_navigation_to_insurance(self, at_referral, page: Page, validation_helper):
        """VALIDATION: Selecting referral and clicking Next navigates to Insurance"""
        # Select first referral source
        page.click("[data-testid='referral-source-web']")
        
        # Click Next
        page.click("button:has-text('Next')")
        page.wait_for_load_state("networkidle")
        
        # Verify navigation to P6
        validation_helper.validate_navigation_to("Insurance")


@pytest.mark.bookslot
@pytest.mark.p5_referral
@pytest.mark.regression
@pytest.mark.medium
class TestReferralRegression:
    """Regression tests for Referral page"""
    
    @pytest.mark.parametrize("referral_source", [
        "Web Search",
        "Social Media",
        "Friend/Family",
        "Doctor Referral",
        "Advertisement",
        "Other"
    ])
    def test_all_referral_sources_selectable(self, at_referral, page: Page, referral_source):
        """REGRESSION: All referral sources can be selected"""
        # Try to find and select each source
        source_id = referral_source.lower().replace("/", "-").replace(" ", "-")
        option = page.locator(f"[data-testid='referral-source-{source_id}']")
        
        if option.count() > 0:
            option.click()
            expect(option).to_have_attribute("data-selected", "true")
    
    def test_other_field_max_length(self, at_referral, page: Page, data_helper):
        """REGRESSION: Other field respects max length"""
        # Select Other
        page.click("[data-testid='referral-source-other']")
        
        # Try to enter very long text
        long_text = data_helper.generate_long_string(300)
        page.fill("[name='referralOther']", long_text)
        
        # Verify max length enforced (assume 200 chars)
        actual_value = page.input_value("[name='referralOther']")
        assert len(actual_value) <= 200, f"Max length exceeded: {len(actual_value)}"
    
    def test_other_field_accepts_special_characters(self, at_referral, page: Page):
        """REGRESSION: Other field accepts special characters"""
        # Select Other
        page.click("[data-testid='referral-source-other']")
        
        # Enter special characters
        special_text = "Friend @ work (via email) - great experience!"
        page.fill("[name='referralOther']", special_text)
        
        # Verify value accepted
        assert page.input_value("[name='referralOther']") == special_text
    
    def test_back_button_returns_to_personal_info(self, at_referral, page: Page, validation_helper):
        """REGRESSION: Back button returns to Personal Info page"""
        page.click("button:has-text('Back')")
        page.wait_for_load_state("networkidle")
        
        # Verify at P4
        validation_helper.validate_navigation_to("Personal Info")


# ============================================================================
# URL WORKFLOW TESTS (Merged from url_testing/test_workflow_urls_p5.py)
# ============================================================================

@allure.epic("Bookslot")
@allure.feature("URL Testing")
@allure.story("Referral Page (P5)")
@pytest.mark.bookslot
@pytest.mark.p5_referral
@pytest.mark.url_workflow
class TestReferralURLWorkflow:
    """URL workflow tests - confirmation flows, edit/cancel, notification prefs"""

    @allure.title("Verify P5 loads with confirmation parameters")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_p5_confirmation_params(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator):
        """Test: Confirmation page loads with appointment details"""
        url = url_builder.build(
            workflow_id="WF-P5-001-CONFIRM", page_path="/confirmation",
            query_params={"appointment_id": "APT-001", "action": "confirm"}
        )
        result = url_validator.validate(url=url, expected_elements=[".appointment-summary", ".confirm-button"])
        assert result.is_valid and result.status_code == 200

    @allure.title("Verify P5 handles edit appointment flow")
    def test_p5_edit_flow(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator):
        """Test: Edit appointment flow via URL"""
        url = url_builder.build(
            workflow_id="WF-P5-002-EDIT", page_path="/confirmation",
            query_params={"appointment_id": "APT-001", "action": "edit"}
        )
        result = url_validator.validate(url=url, expected_elements=[".edit-form"])
        assert result.is_valid and result.status_code == 200

    @allure.title("Verify P5 handles cancel appointment flow")
    def test_p5_cancel_flow(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator):
        """Test: Cancel appointment flow via URL"""
        url = url_builder.build(
            workflow_id="WF-P5-003-CANCEL", page_path="/confirmation",
            query_params={"appointment_id": "APT-001", "action": "cancel"}
        )
        result = url_validator.validate(url=url, expected_elements=[".cancel-confirmation"])
        assert result.is_valid and result.status_code == 200

    @allure.title("Verify P5 notification preferences")
    @pytest.mark.parametrize("notify", ["email", "sms", "both"], ids=["email", "sms", "both"])
    def test_p5_notification_prefs(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator, notify: str):
        """Test: Notification preference parameters handled"""
        url = url_builder.build(
            workflow_id=f"WF-P5-NOTIFY-{notify.upper()}", page_path="/confirmation",
            query_params={"appointment_id": "APT-001", "notify": notify}
        )
        result = url_validator.validate(url=url, expected_elements=[".notification-prefs"])
        assert result.is_valid and result.status_code == 200

    @allure.title("Verify P5 performance within threshold")
    @pytest.mark.performance
    def test_p5_load_performance(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator):
        """Test: Page loads within performance threshold"""
        url = url_builder.build(workflow_id="WF-P5-PERF", page_path="/confirmation", query_params={"appointment_id": "APT-001"})
        result = url_validator.validate(url=url)
        assert result.validation_time_ms < 5000, f"Page load too slow: {result.validation_time_ms}ms"

