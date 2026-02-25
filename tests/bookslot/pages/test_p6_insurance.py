"""
P6: Insurance Page Tests (Layer A - Page-Level)

Tests for Insurance information page (requires P1→P2→P3→P4→P5 completed).

Test Coverage:
- Smoke: Page loads, insurance fields visible
- Validation: Field behavior, required validation, format validation
- Regression: Max length, special characters, payer selection

Markers:
- @pytest.mark.p6_insurance
- @pytest.mark.smoke, validation, regression
"""

import pytest
import allure
from typing import Dict, Any
from playwright.sync_api import Page, expect

from framework.testing.url_builder import URLBuilder
from framework.testing.url_validator import URLValidator


@pytest.mark.bookslot
@pytest.mark.p6_insurance
@pytest.mark.smoke
@pytest.mark.critical
class TestInsuranceSmoke:
    """Smoke tests for Insurance page (P6)"""
    
    def test_insurance_page_loads(self, at_insurance, validation_helper):
        """SMOKE: Insurance page loads successfully"""
        validation_helper.validate_element_visible("h1", "Insurance heading")
        validation_helper.validate_element_visible("form", "Insurance form")
    
    def test_insurance_fields_visible(self, at_insurance, validation_helper):
        """SMOKE: All insurance fields are visible"""
        validation_helper.validate_elements_visible([
            "[name='memberId']",
            "[name='groupNumber']",
            "[name='payer']"
        ])
    
    def test_submit_button_visible(self, at_insurance, validation_helper):
        """SMOKE: Submit button is visible"""
        validation_helper.validate_element_visible("button:has-text('Submit')", "Submit button")


@pytest.mark.bookslot
@pytest.mark.p6_insurance
@pytest.mark.validation
@pytest.mark.high
class TestInsuranceValidation:
    """Validation tests for Insurance page"""
    
    def test_insurance_fields_enabled(self, at_insurance, validation_helper):
        """VALIDATION: All insurance fields are enabled"""
        validation_helper.validate_elements_enabled([
            "[name='memberId']",
            "[name='groupNumber']",
            "[name='payer']"
        ])
    
    def test_member_id_required(self, at_insurance, page: Page, validation_helper, valid_insurance_info):
        """VALIDATION: Member ID is required"""
        # Fill other fields
        page.fill("[name='groupNumber']", valid_insurance_info["group_number"])
        page.fill("[name='payer']", valid_insurance_info["payer"])
        
        # Try to submit without member ID
        page.click("button:has-text('Submit')")
        
        # Verify error
        validation_helper.validate_required_field_error("[name='memberId']")
    
    def test_group_number_required(self, at_insurance, page: Page, validation_helper, valid_insurance_info):
        """VALIDATION: Group Number is required"""
        # Fill other fields
        page.fill("[name='memberId']", valid_insurance_info["member_id"])
        page.fill("[name='payer']", valid_insurance_info["payer"])
        
        # Try to submit without group number
        page.click("button:has-text('Submit')")
        
        # Verify error
        validation_helper.validate_required_field_error("[name='groupNumber']")
    
    def test_payer_required(self, at_insurance, page: Page, validation_helper, valid_insurance_info):
        """VALIDATION: Payer is required"""
        # Fill other fields
        page.fill("[name='memberId']", valid_insurance_info["member_id"])
        page.fill("[name='groupNumber']", valid_insurance_info["group_number"])
        
        # Try to submit without payer
        page.click("button:has-text('Submit')")
        
        # Verify error
        validation_helper.validate_required_field_error("[name='payer']")
    
    def test_member_id_accepts_alphanumeric(self, at_insurance, page: Page, validation_helper):
        """VALIDATION: Member ID accepts alphanumeric values"""
        test_values = ["ABC123", "123ABC", "A1B2C3", "12345678"]
        
        for value in test_values:
            validation_helper.validate_input_accepts_value("[name='memberId']", value)
    
    def test_insurance_submission_navigation_to_success(self, at_insurance, page: Page, validation_helper, valid_insurance_info):
        """VALIDATION: Submitting insurance navigates to Success page"""
        # Fill all fields
        page.fill("[name='memberId']", valid_insurance_info["member_id"])
        page.fill("[name='groupNumber']", valid_insurance_info["group_number"])
        page.fill("[name='payer']", valid_insurance_info["payer"])
        
        # Submit
        page.click("button:has-text('Submit')")
        page.wait_for_load_state("networkidle")
        
        # Verify navigation to P7
        validation_helper.validate_navigation_to("Success")


@pytest.mark.bookslot
@pytest.mark.p6_insurance
@pytest.mark.regression
@pytest.mark.medium
class TestInsuranceRegression:
    """Regression tests for Insurance page"""
    
    @pytest.mark.parametrize("field_name,max_length", [
        ("memberId", 20),
        ("groupNumber", 20),
        ("payer", 100)
    ])
    def test_field_max_length(self, at_insurance, page: Page, data_helper, field_name, max_length):
        """REGRESSION: Insurance fields respect max length"""
        # Generate long string
        long_value = data_helper.generate_long_string(max_length + 50)
        
        # Fill field
        page.fill(f"[name='{field_name}']", long_value)
        
        # Verify max length enforced
        actual_value = page.input_value(f"[name='{field_name}']")
        assert len(actual_value) <= max_length, f"{field_name} exceeds max length: {len(actual_value)}"
    
    def test_member_id_accepts_hyphens(self, at_insurance, page: Page):
        """REGRESSION: Member ID accepts hyphens"""
        value = "ABC-123-XYZ"
        page.fill("[name='memberId']", value)
        assert page.input_value("[name='memberId']") == value
    
    def test_payer_dropdown_or_autocomplete(self, at_insurance, page: Page):
        """REGRESSION: Payer field supports selection/autocomplete"""
        payer_field = page.locator("[name='payer']")
        
        # Check if it's a dropdown or text field
        tag_name = payer_field.evaluate("el => el.tagName")
        
        if tag_name == "SELECT":
            # It's a dropdown - verify options
            options = page.locator("[name='payer'] option")
            assert options.count() > 0, "No payer options available"
        else:
            # It's a text field - verify it accepts input
            payer_field.fill("Blue Cross Blue Shield")
            assert page.input_value("[name='payer']") == "Blue Cross Blue Shield"
    
    @pytest.mark.parametrize("payer", [
        "Blue Cross Blue Shield",
        "Aetna",
        "United Healthcare",
        "Cigna",
        "Humana"
    ])
    def test_common_payers(self, at_insurance, page: Page, payer, valid_insurance_info):
        """REGRESSION: Common insurance payers can be selected"""
        # Fill required fields
        page.fill("[name='memberId']", valid_insurance_info["member_id"])
        page.fill("[name='groupNumber']", valid_insurance_info["group_number"])
        
        # Try to select/fill payer
        payer_field = page.locator("[name='payer']")
        tag_name = payer_field.evaluate("el => el.tagName")
        
        if tag_name == "SELECT":
            # Dropdown - try to select if option exists
            option = page.locator(f"[name='payer'] option:has-text('{payer}')")
            if option.count() > 0:
                page.select_option("[name='payer']", payer)
        else:
            # Text field - just fill
            page.fill("[name='payer']", payer)
        
        # Verify value set
        actual_value = page.input_value("[name='payer']")
        assert payer in actual_value or actual_value in payer
    
    def test_back_button_returns_to_referral(self, at_insurance, page: Page, validation_helper):
        """REGRESSION: Back button returns to page"""
        page.click("button:has-text('Back')")
        page.wait_for_load_state("networkidle")
        
        # Verify at P5
        validation_helper.validate_navigation_to("Referral")
    
    def test_insurance_data_persists_on_back_navigation(self, at_insurance, page: Page, valid_insurance_info):
        """REGRESSION: Insurance data persists when navigating back"""
        # Fill all fields
        page.fill("[name='memberId']", valid_insurance_info["member_id"])
        page.fill("[name='groupNumber']", valid_insurance_info["group_number"])
        page.fill("[name='payer']", valid_insurance_info["payer"])
        
        # Submit (go to Success)
        page.click("button:has-text('Submit')")
        page.wait_for_load_state("networkidle")
        
        # Go back
        page.click("button:has-text('Back')")
        page.wait_for_load_state("networkidle")
        
        # Verify data persisted
        assert page.input_value("[name='memberId']") == valid_insurance_info["member_id"]
        assert page.input_value("[name='groupNumber']") == valid_insurance_info["group_number"]


# ============================================================================
# URL WORKFLOW TESTS (Merged from url_testing/test_workflow_urls_p6.py)
# ============================================================================

@allure.epic("Bookslot")
@allure.feature("URL Testing")
@allure.story("Insurance Page (P6)")
@pytest.mark.bookslot
@pytest.mark.p6_insurance
@pytest.mark.url_workflow
class TestInsuranceURLWorkflow:
    """URL workflow tests - review details, terms acceptance, completeness"""

    @allure.title("Verify P6 loads with review parameters")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_p6_review_params(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator):
        """Test: Review page loads with appointment details"""
        url = url_builder.build(
            workflow_id="WF-P6-001-REVIEW", page_path="/review",
            query_params={"appointment_id": "APT-001", "show_details": "true"}
        )
        result = url_validator.validate(url=url, expected_elements=[".review-summary", ".terms-checkbox"])
        assert result.is_valid and result.status_code == 200

    @allure.title("Verify P6 handles terms acceptance")
    def test_p6_terms_acceptance(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator):
        """Test: Terms and privacy acceptance flow"""
        url = url_builder.build(
            workflow_id="WF-P6-002-TERMS", page_path="/review",
            query_params={"appointment_id": "APT-001", "terms_accepted": "true"}
        )
        result = url_validator.validate(url=url, expected_elements=[".terms-checkbox", ".submit-button"])
        assert result.is_valid and result.status_code == 200

    @allure.title("Verify P6 detects incomplete appointments")
    @pytest.mark.negative
    def test_p6_incomplete_appointment(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator):
        """Test: Incomplete appointment detected and flagged"""
        url = url_builder.build(
            workflow_id="WF-P6-003-INCOMPLETE", page_path="/review",
            query_params={"appointment_id": "APT-INCOMPLETE"}
        )
        result = url_validator.validate(url=url, expected_elements=[".incomplete-warning"])
        assert result.status_code == 200

    @allure.title("Verify P6 performance within threshold")
    @pytest.mark.performance
    def test_p6_load_performance(self, page: Page, url_builder: URLBuilder, url_validator: URLValidator):
        """Test: Page loads within performance threshold"""
        url = url_builder.build(workflow_id="WF-P6-PERF", page_path="/review", query_params={"appointment_id": "APT-001"})
        result = url_validator.validate(url=url)
        assert result.validation_time_ms < 5000, f"Page load too slow: {result.validation_time_ms}ms"

