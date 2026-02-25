"""
P4: Personal Info Page Tests (Layer A - Page-Level)

Tests for Personal Info page (requires P1→P2→P3 completed as precondition).

Test Coverage:
- Smoke: Page loads, key fields visible
- Validation: Field behavior, required fields, format validation
- Regression: Boundary values, special characters, max length

Markers:
- @pytest.mark.p4_personal_info
- @pytest.mark.smoke, validation, regression
"""

import pytest
import allure
from typing import Dict, Any
from playwright.sync_api import Page, expect
from datetime import datetime, timedelta

from framework.testing.url_builder import URLBuilder
from framework.testing.url_validator import URLValidator


@pytest.mark.bookslot
@pytest.mark.p4_personal_info
@pytest.mark.smoke
@pytest.mark.critical
class TestPersonalInfoSmoke:
    """Smoke tests for Personal Info page (P4)"""
    
    def test_personal_info_page_loads(self, at_personal_info, validation_helper):
        """SMOKE: Personal Info page loads successfully"""
        validation_helper.validate_element_visible("h1", "Personal Info heading")
        validation_helper.validate_element_visible("form", "Personal info form")
    
    def test_personal_info_fields_visible(self, at_personal_info, validation_helper):
        """SMOKE: All personal info fields are visible"""
        validation_helper.validate_elements_visible([
            "[name='firstName']",
            "[name='lastName']",
            "[name='dateOfBirth']",
            "[name='address']",
            "[name='city']",
            "[name='state']",
            "[name='zipCode']"
        ])
    
    def test_next_button_visible(self, at_personal_info, validation_helper):
        """SMOKE: Next button is visible"""
        validation_helper.validate_element_visible("button:has-text('Next')", "Next button")


@pytest.mark.bookslot
@pytest.mark.p4_personal_info
@pytest.mark.validation
@pytest.mark.high
class TestPersonalInfoValidation:
    """Validation tests for Personal Info page"""
    
    def test_personal_info_fields_enabled(self, at_personal_info, validation_helper):
        """VALIDATION: All personal info fields are enabled and editable"""
        validation_helper.validate_elements_enabled([
            "[name='firstName']",
            "[name='lastName']",
            "[name='dateOfBirth']",
            "[name='address']",
            "[name='city']",
            "[name='state']",
            "[name='zipCode']"
        ])
    
    def test_first_name_required(self, at_personal_info, page: Page, validation_helper, valid_personal_info):
        """VALIDATION: First name is required"""
        # Fill all fields except first name
        page.fill("[name='lastName']", valid_personal_info["last_name"])
        page.fill("[name='dateOfBirth']", valid_personal_info["dob"])
        page.fill("[name='address']", valid_personal_info["address"])
        page.fill("[name='city']", valid_personal_info["city"])
        page.select_option("[name='state']", valid_personal_info["state"])
        page.fill("[name='zipCode']", valid_personal_info["zip_code"])
        
        # Try to proceed
        page.click("button:has-text('Next')")
        
        # Verify error
        validation_helper.validate_required_field_error("[name='firstName']")
    
    def test_date_of_birth_required(self, at_personal_info, page: Page, validation_helper, valid_personal_info):
        """VALIDATION: Date of birth is required"""
        # Fill all fields except DOB
        page.fill("[name='firstName']", valid_personal_info["first_name"])
        page.fill("[name='lastName']", valid_personal_info["last_name"])
        page.fill("[name='address']", valid_personal_info["address"])
        page.fill("[name='city']", valid_personal_info["city"])
        page.select_option("[name='state']", valid_personal_info["state"])
        page.fill("[name='zipCode']", valid_personal_info["zip_code"])
        
        # Try to proceed
        page.click("button:has-text('Next')")
        
        # Verify error
        validation_helper.validate_required_field_error("[name='dateOfBirth']")
    
    def test_zip_code_format_validation(self, at_personal_info, page: Page, validation_helper):
        """VALIDATION: Zip code format is validated"""
        invalid_zip_codes = ["123", "ABCDE", "12345678"]
        
        for invalid_zip in invalid_zip_codes:
            page.fill("[name='zipCode']", invalid_zip)
            page.click("button:has-text('Next')")
            validation_helper.validate_required_field_error("[name='zipCode']")
            page.fill("[name='zipCode']", "")
    
    def test_valid_personal_info_navigation_to_referral(self, at_personal_info, page: Page, valid_personal_info):
        """VALIDATION: Valid personal info navigates to Referral page"""
        # Fill all required fields with valid data
        page.fill("[name='firstName']", valid_personal_info["first_name"])
        page.fill("[name='lastName']", valid_personal_info["last_name"])
        page.fill("[name='dateOfBirth']", valid_personal_info["dob"])
        page.fill("[name='address']", valid_personal_info["address"])
        page.fill("[name='city']", valid_personal_info["city"])
        page.select_option("[name='state']", valid_personal_info["state"])
        page.fill("[name='zipCode']", valid_personal_info["zip_code"])
        
        # Click Next
        page.click("button:has-text('Next')")
        
        # Verify navigation to Referral page
        expect(page).to_have_url(page.url + "/referral", timeout=10000)


@pytest.mark.bookslot
@pytest.mark.p4_personal_info
@pytest.mark.regression
@pytest.mark.medium
class TestPersonalInfoRegression:
    """Regression tests for Personal Info page"""
    
    def test_first_name_max_length(self, at_personal_info, page: Page):
        """REGRESSION: First name respects max length"""
        long_name = "A" * 100
        page.fill("[name='firstName']", long_name)
        
        actual_value = page.input_value("[name='firstName']")
        assert len(actual_value) <= 50, f"First name exceeds max length: {len(actual_value)}"
    
    def test_special_characters_in_name(self, at_personal_info, page: Page, validation_helper):
        """REGRESSION: Names with special characters (hyphens, apostrophes) are accepted"""
        special_names = [
            ("Mary-Jane", "O'Brien"),
            ("Jean-Paul", "D'Angelo"),
        ]
        
        for first, last in special_names:
            page.fill("[name='firstName']", first)
            page.fill("[name='lastName']", last)
            
            # Verify accepted
            assert page.input_value("[name='firstName']") == first
            assert page.input_value("[name='lastName']") == last
    
    def test_state_dropdown_complete(self, at_personal_info, page: Page):
        """REGRESSION: State dropdown contains all 50 US states"""
        state_options = page.locator("[name='state'] option")
        count = state_options.count()
        
        # Should have 50 states + 1 placeholder option
        assert count >= 50, f"Expected at least 50 states, found {count - 1}"


# ============================================================================
# URL WORKFLOW TESTS (Merged from url_testing/test_workflow_urls_p4.py)
# ============================================================================

@allure.epic("Bookslot")
@allure.feature("URL Testing")
@allure.story("Personal Info Page (P4)")
@pytest.mark.bookslot
@pytest.mark.p4_personal_info
@pytest.mark.url_workflow
class TestPersonalInfoURLWorkflow:
    """URL workflow tests - visit reasons, emergency flags, persistence"""

    @allure.title("Verify P4 loads with visit reason parameter")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_p4_visit_reason(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator):
        """Test: Reason page loads with visit reason parameter"""
        url = url_builder.build(
            workflow_id="WF-P4-001-REASON", page_path="/reason",
            query_params={"visit_reason": "routine_checkup"}
        )
        result = url_validator.validate(url=url, expected_elements=[".reason-selector", ".reason-description"])
        assert result.is_valid, f"URL validation failed: {result.errors}"
        assert result.status_code == 200

    @allure.title("Verify P4 handles emergency visit flag")
    @pytest.mark.critical
    def test_p4_emergency_visit(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator):
        """Test: Emergency flag handled correctly"""
        url = url_builder.build(
            workflow_id="WF-P4-002-EMERGENCY", page_path="/reason",
            query_params={"visit_reason": "emergency", "is_emergency": "true"}
        )
        result = url_validator.validate(url=url, expected_elements=[".reason-selector", ".emergency-indicator"])
        assert result.is_valid and result.status_code == 200

    @allure.title("Verify P4 with multiple visit reasons")
    @pytest.mark.parametrize("reason", ["routine_checkup", "consultation", "vaccination", "lab_work"],
                             ids=["routine", "consultation", "vaccination", "lab"])
    def test_p4_multiple_visit_reasons(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator, reason: str):
        """Test: Various visit reasons load correctly"""
        url = url_builder.build(workflow_id=f"WF-P4-{reason.upper()}", page_path="/reason", query_params={"visit_reason": reason})
        result = url_validator.validate(url=url, expected_elements=[".reason-selector"])
        assert result.is_valid and result.status_code == 200

    @allure.title("Verify P4 reason persistence after refresh")
    def test_p4_reason_persistence(self, page: Page, url_builder: URLBuilder):
        """Test: Reason parameters persist after page refresh"""
        url = url_builder.build(workflow_id="WF-P4-PERSIST", page_path="/reason", query_params={"visit_reason": "routine_checkup"})
        page.goto(url)
        original_url = page.url
        page.reload()
        assert original_url == page.url and "visit_reason" in page.url

    @allure.title("Verify P4 performance within threshold")
    @pytest.mark.performance
    def test_p4_load_performance(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator):
        """Test: Page loads within performance threshold"""
        url = url_builder.build(workflow_id="WF-P4-PERF", page_path="/reason", query_params={"visit_reason": "routine_checkup"})
        result = url_validator.validate(url=url)
        assert result.validation_time_ms < 5000, f"Page load too slow: {result.validation_time_ms}ms"

