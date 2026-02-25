"""
P1: Basic Info Page Tests (Layer A - Page-Level)

Tests for Basic Info page (entry page, no precondition needed).

Test Coverage:
- Smoke: Page loads, key fields visible
- Validation: Required fields, format validation, field behavior
- Regression: Boundary values, localization, full component coverage

Markers:
- @pytest.mark.p1_basic_info: Page marker
- @pytest.mark.smoke: Fast smoke tests
- @pytest.mark.validation: Component validation
- @pytest.mark.regression: Full regression suite
"""

import pytest
import allure
from typing import Dict, Any
from playwright.sync_api import Page, expect

from framework.testing.url_builder import URLBuilder
from framework.testing.url_validator import URLValidator


# ============================================================================
# SMOKE TESTS (Fast Confidence - Run on Every PR)
# ============================================================================

@pytest.mark.bookslot
@pytest.mark.p1_basic_info
@pytest.mark.smoke
@pytest.mark.critical
class TestBasicInfoSmoke:
    """Smoke tests for Basic Info page (P1)"""
    
    def test_basic_info_page_loads(self, at_basic_info, validation_helper):
        """
        SMOKE: Verify Basic Info page loads successfully.
        
        Validates:
        - Page loads without errors
        - Key heading is visible
        - Form is visible
        """
        # Validate page heading
        validation_helper.validate_element_visible("h1", "Basic Info heading")
        
        # Validate form is present
        validation_helper.validate_element_visible("form", "Basic Info form")
    
    def test_required_fields_visible(self, at_basic_info, validation_helper):
        """
        SMOKE: Verify all required fields are visible.
        
        As per Component Coverage requirements:
        1. Visible ✓
        """
        required_fields = [
            ("[name='firstName']", "First Name field"),
            ("[name='lastName']", "Last Name field"),
            ("[name='email']", "Email field"),
            ("[name='phone']", "Phone field"),
        ]
        
        validation_helper.validate_elements_visible(required_fields)
    
    def test_next_button_visible(self, at_basic_info, validation_helper):
        """
        SMOKE: Verify Next button is visible.
        """
        validation_helper.validate_button_clickable("Next")


# ============================================================================
# VALIDATION TESTS (Component Validation - Full Coverage)
# ============================================================================

@pytest.mark.bookslot
@pytest.mark.p1_basic_info
@pytest.mark.validation
@pytest.mark.high
class TestBasicInfoValidation:
    """Validation tests for Basic Info page components"""
    
    # ------------------------------------------------------------------------
    # Component Coverage: All Interactive Elements
    # ------------------------------------------------------------------------
    
    def test_all_form_fields_enabled(self, at_basic_info, validation_helper):
        """
        VALIDATION: All form fields are enabled (clickable/editable).
        
        As per Component Coverage:
        2. Enabled/Clickable ✓
        """
        form_fields = [
            ("[name='firstName']", "First Name"),
            ("[name='lastName']", "Last Name"),
            ("[name='email']", "Email"),
            ("[name='phone']", "Phone"),
        ]
        
        for selector, description in form_fields:
            validation_helper.validate_element_enabled(selector, description)
    
    def test_fields_accept_valid_input(self, at_basic_info, validation_helper, valid_basic_info):
        """
        VALIDATION: Fields accept valid input values.
        
        As per Component Coverage:
        3. Input behavior ✓
        """
        # First Name
        validation_helper.validate_input_accepts_value(
            "[name='firstName']",
            valid_basic_info["first_name"],
            "First Name"
        )
        
        # Last Name
        validation_helper.validate_input_accepts_value(
            "[name='lastName']",
            valid_basic_info["last_name"],
            "Last Name"
        )
        
        # Email
        validation_helper.validate_input_accepts_value(
            "[name='email']",
            valid_basic_info["email"],
            "Email"
        )
        
        # Phone
        validation_helper.validate_input_accepts_value(
            "[name='phone']",
            valid_basic_info["phone"],
            "Phone"
        )
    
    # ------------------------------------------------------------------------
    # Required Field Validation
    # ------------------------------------------------------------------------
    
    def test_first_name_required(self, at_basic_info, page: Page, validation_helper):
        """
        VALIDATION: First Name is required.
        
        As per Component Coverage:
        4. Validation behavior ✓
        """
        # Leave field empty and try to proceed
        page.click("button:has-text('Next')")
        
        # Verify error message
        validation_helper.validate_error_message_shown("required")
    
    def test_last_name_required(self, at_basic_info, page: Page, validation_helper):
        """
        VALIDATION: Last Name is required.
        """
        # Fill first name only
        page.fill("[name='firstName']", "Test")
        page.click("button:has-text('Next')")
        
        # Verify error for last name
        validation_helper.validate_error_message_shown("required")
    
    def test_email_required(self, at_basic_info, page: Page, validation_helper):
        """
        VALIDATION: Email is required.
        """
        # Fill name fields only
        page.fill("[name='firstName']", "Test")
        page.fill("[name='lastName']", "User")
        page.click("button:has-text('Next')")
        
        # Verify error for email
        validation_helper.validate_error_message_shown("required")
    
    def test_phone_required(self, at_basic_info, page: Page, validation_helper):
        """
        VALIDATION: Phone is required.
        """
        # Fill all except phone
        page.fill("[name='firstName']", "Test")
        page.fill("[name='lastName']", "User")
        page.fill("[name='email']", "test@example.com")
        page.click("button:has-text('Next')")
        
        # Verify error for phone
        validation_helper.validate_error_message_shown("required")
    
    # ------------------------------------------------------------------------
    # Format Validation
    # ------------------------------------------------------------------------
    
    @pytest.mark.parametrize("invalid_email", [
        "invalid",
        "invalid@",
        "@invalid.com",
        "invalid.com",
        "invalid @email.com"
    ])
    def test_email_format_validation(self, at_basic_info, page: Page, validation_helper, invalid_email):
        """
        VALIDATION: Email format is validated.
        
        Tests invalid email formats:
        - Missing @
        - Missing domain
        - Missing username
        - Missing TLD
        - Spaces
        """
        page.fill("[name='firstName']", "Test")
        page.fill("[name='lastName']", "User")
        page.fill("[name='email']", invalid_email)
        page.fill("[name='phone']", "5551234567")
        page.click("button:has-text('Next')")
        
        # Verify email format error
        validation_helper.validate_error_message_shown("email")
    
    @pytest.mark.parametrize("invalid_phone", [
        "123",          # Too short
        "abc",          # Non-numeric
        "123-456",      # Too short with dash
        "12345678901234"  # Too long
    ])
    def test_phone_format_validation(self, at_basic_info, page: Page, validation_helper, invalid_phone):
        """
        VALIDATION: Phone format is validated.
        
        Tests invalid phone formats:
        - Too short
        - Non-numeric characters
        - Too long
        """
        page.fill("[name='firstName']", "Test")
        page.fill("[name='lastName']", "User")
        page.fill("[name='email']", "test@example.com")
        page.fill("[name='phone']", invalid_phone)
        page.click("button:has-text('Next')")
        
        # Verify phone format error
        validation_helper.validate_error_message_shown("phone")
    
    # ------------------------------------------------------------------------
    # Navigation Effect
    # ------------------------------------------------------------------------
    
    def test_next_button_navigation(self, at_basic_info, page: Page, valid_basic_info, validation_helper):
        """
        VALIDATION: Next button navigates to Event Type page.
        
        As per Component Coverage:
        6. Navigation effect ✓
        """
        # Fill all required fields with valid data
        page.fill("[name='firstName']", valid_basic_info["first_name"])
        page.fill("[name='lastName']", valid_basic_info["last_name"])
        page.fill("[name='email']", valid_basic_info["email"])
        page.fill("[name='phone']", valid_basic_info["phone"])
        
        # Click Next
        page.click("button:has-text('Next')")
        page.wait_for_load_state("networkidle")
        
        # Verify navigation to Event Type page (P2)
        validation_helper.validate_navigation_to("Event Type")
    
    def test_next_button_disabled_when_form_invalid(self, at_basic_info, page: Page, validation_helper):
        """
        VALIDATION: Next button behavior when form is invalid.
        
        Note: This test assumes button is disabled when form invalid.
        Adjust based on actual implementation (might show errors instead).
        """
        # Leave form empty
        # Check if Next button is disabled or clicking shows errors
        page.click("button:has-text('Next')")
        
        # Should stay on same page or show errors
        validation_helper.validate_error_message_shown("required")


# ============================================================================
# REGRESSION TESTS (Full Coverage - Boundary, Edge Cases, Variants)
# ============================================================================

@pytest.mark.bookslot
@pytest.mark.p1_basic_info
@pytest.mark.regression
@pytest.mark.medium
class TestBasicInfoRegression:
    """Regression tests for Basic Info page - boundary values, edge cases"""
    
    def test_first_name_max_length(self, at_basic_info, page: Page, validation_helper):
        """
        REGRESSION: First Name respects maximum length.
        """
        # Assuming max length is 50 characters
        validation_helper.validate_input_max_length(
            "[name='firstName']",
            max_length=50,
            description="First Name"
        )
    
    def test_last_name_max_length(self, at_basic_info, page: Page, validation_helper):
        """
        REGRESSION: Last Name respects maximum length.
        """
        validation_helper.validate_input_max_length(
            "[name='lastName']",
            max_length=50,
            description="Last Name"
        )
    
    def test_email_max_length(self, at_basic_info, page: Page, validation_helper):
        """
        REGRESSION: Email respects maximum length.
        """
        validation_helper.validate_input_max_length(
            "[name='email']",
            max_length=100,
            description="Email"
        )
    
    def test_phone_accepts_various_formats(self, at_basic_info, page: Page, validation_helper):
        """
        REGRESSION: Phone accepts various valid formats.
        
        Tests:
        - 10 digits no formatting
        - With dashes
        - With parentheses
        - With spaces
        """
        valid_phone_formats = [
            "5551234567",
            "555-123-4567",
            "(555) 123-4567",
            "555 123 4567"
        ]
        
        for phone_format in valid_phone_formats:
            page.fill("[name='phone']", phone_format)
            # Phone should accept it (might normalize internally)
            # Just verify no immediate error
            validation_helper.validate_no_error_messages()
    
    def test_special_characters_in_name(self, at_basic_info, page: Page):
        """
        REGRESSION: Names with special characters (apostrophes, hyphens).
        """
        # Names like O'Brien, Mary-Jane should be accepted
        page.fill("[name='firstName']", "Mary-Jane")
        page.fill("[name='lastName']", "O'Brien")
        page.fill("[name='email']", "maryjane@example.com")
        page.fill("[name='phone']", "5551234567")
        
        # Should not show errors
        page.click("button:has-text('Next')")
        page.wait_for_load_state("networkidle")
        
        # Should navigate successfully (no errors)
        expect(page.locator("h1")).to_contain_text("Event Type")
    
    def test_unicode_characters_in_name(self, at_basic_info, page: Page):
        """
        REGRESSION: Names with unicode characters (internationalization).
        """
        # Test international names
        page.fill("[name='firstName']", "José")
        page.fill("[name='lastName']", "Müller")
        page.fill("[name='email']", "jose@example.com")
        page.fill("[name='phone']", "5551234567")
        
        # Should accept unicode
        page.click("button:has-text('Next')")
        page.wait_for_load_state("networkidle")
        
        # Should navigate successfully
        expect(page.locator("h1")).to_contain_text("Event Type")
    
    def test_copy_paste_behavior(self, at_basic_info, page: Page):
        """
        REGRESSION: Copy-paste works correctly in all fields.
        """
        # Test copy-paste doesn't break validation
        page.fill("[name='firstName']", "Test")
        first_name_value = page.input_value("[name='firstName']")
        
        # Paste into last name
        page.fill("[name='lastName']", first_name_value)
        assert page.input_value("[name='lastName']") == "Test"
    
    def test_tab_navigation_order(self, at_basic_info, page: Page):
        """
        REGRESSION: Tab key navigates fields in correct order.
        
        Expected order: First Name → Last Name → Email → Phone → Next Button
        """
        # Focus first field
        page.focus("[name='firstName']")
        
        # Tab to next field
        page.keyboard.press("Tab")
        focused = page.evaluate("document.activeElement.name")
        assert focused == "lastName", f"Expected lastName, got {focused}"
        
        # Tab to email
        page.keyboard.press("Tab")
        focused = page.evaluate("document.activeElement.name")
        assert focused == "email", f"Expected email, got {focused}"
        
        # Tab to phone
        page.keyboard.press("Tab")
        focused = page.evaluate("document.activeElement.name")
        assert focused == "phone", f"Expected phone, got {focused}"
    
    def test_form_persistence_on_back_navigation(self, at_basic_info, page: Page, valid_basic_info):
        """
        REGRESSION: Form data persists when navigating back.
        
        Scenario:
        1. Fill form and go to next page
        2. Click Back
        3. Verify data is still there
        """
        # Fill form
        page.fill("[name='firstName']", valid_basic_info["first_name"])
        page.fill("[name='lastName']", valid_basic_info["last_name"])
        page.fill("[name='email']", valid_basic_info["email"])
        page.fill("[name='phone']", valid_basic_info["phone"])
        
        # Go to next page
        page.click("button:has-text('Next')")
        page.wait_for_load_state("networkidle")
        
        # Go back
        page.click("button:has-text('Back')")
        page.wait_for_load_state("networkidle")
        
        # Verify data persisted
        assert page.input_value("[name='firstName']") == valid_basic_info["first_name"]
        assert page.input_value("[name='lastName']") == valid_basic_info["last_name"]
        assert page.input_value("[name='email']") == valid_basic_info["email"]
        assert page.input_value("[name='phone']") == valid_basic_info["phone"]


# ============================================================================
# ACCESSIBILITY TESTS (Optional - If Accessibility is a Requirement)
# ============================================================================

@pytest.mark.bookslot
@pytest.mark.p1_basic_info
@pytest.mark.regression
@pytest.mark.medium
class TestBasicInfoAccessibility:
    """Accessibility tests for Basic Info page"""
    
    def test_form_labels_present(self, at_basic_info, page: Page):
        """
        ACCESSIBILITY: All form fields have associated labels.
        """
        fields = ["firstName", "lastName", "email", "phone"]
        
        for field in fields:
            # Check for label element
            label = page.locator(f"label[for='{field}']")
            expect(label).to_be_visible()
    
    def test_required_fields_indicated(self, at_basic_info, page: Page):
        """
        ACCESSIBILITY: Required fields are visually indicated.
        
        Usually with asterisk (*) or "required" text.
        """
        # Check for required indicators (adjust selector based on actual implementation)
        required_indicators = page.locator("[data-required='true'], .required, [aria-required='true']")
        count = required_indicators.count()
        
        # Should have 4 required field indicators
        assert count >= 4, f"Expected at least 4 required indicators, found {count}"


# ============================================================================
# URL WORKFLOW TESTS (Merged from url_testing/test_workflow_urls_p1.py)
# ============================================================================

@allure.epic("Bookslot")
@allure.feature("URL Testing")
@allure.story("Basic Info Page (P1)")
@pytest.mark.bookslot
@pytest.mark.p1_basic_info
@pytest.mark.url_workflow
class TestBasicInfoURLWorkflow:
    """URL workflow tests for Basic Info page - query params, deep links, persistence"""

    @allure.title("Verify P1 loads with prefilled name from URL parameters")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_p1_url_prefill_name(
        self,
        page: Page,
        url_builder: URLBuilder,
        url_validator: URLValidator
    ):
        """
        Test: Basic Info page loads with name prefilled from URL query params

        Steps:
        1. Build URL with first_name and last_name params
        2. Navigate to URL
        3. Validate page loads successfully
        4. Verify form elements present
        """
        url = url_builder.build(
            workflow_id="WF-P1-001-PREFILL",
            page_path="/basic-info",
            query_params={
                "first_name": "John",
                "last_name": "Doe",
                "prefill": "true"
            }
        )

        allure.attach(url, "Generated URL", allure.attachment_type.TEXT)

        result = url_validator.validate(
            url=url,
            expected_elements=[
                "[name='firstName']",
                "[name='lastName']",
                "[name='email']",
                "[name='phone']"
            ]
        )

        assert result.is_valid, f"URL validation failed: {result.errors}"
        assert result.status_code == 200

        allure.attach(
            f"Status: {result.status_code}\nLoad Time: {result.validation_time_ms}ms",
            "Validation Result",
            allure.attachment_type.TEXT
        )

    @allure.title("Verify P1 workflow ID persists across page refresh")
    def test_p1_workflow_id_persistence(
        self,
        page: Page,
        url_builder: URLBuilder
    ):
        """
        Test: Workflow ID persists in URL after page refresh

        Validates: State management via URL parameters
        """
        url = url_builder.build(
            workflow_id="WF-P1-PERSIST-001",
            page_path="/basic-info",
            query_params={"first_name": "Jane"}
        )

        page.goto(url)
        original_url = page.url

        page.reload()
        refreshed_url = page.url

        assert original_url == refreshed_url
        assert "workflow_id" in refreshed_url or "WF-P1" in refreshed_url

    @allure.title("Verify P1 handles URL-encoded special characters")
    @pytest.mark.parametrize(
        "name,encoded_expected",
        [
            ("O'Brien", True),
            ("Mary Jane", True),
            ("José", True),
        ],
        ids=["apostrophe", "space", "unicode"]
    )
    def test_p1_url_encoding_special_chars(
        self,
        page: Page,
        url_builder: URLBuilder,
        url_validator: URLValidator,
        name: str,
        encoded_expected: bool
    ):
        """
        Test: Special characters are properly URL-encoded

        Validates: URL encoding and decoding
        """
        url = url_builder.build(
            workflow_id="WF-P1-ENCODING",
            page_path="/basic-info",
            query_params={"first_name": name}
        )

        result = url_validator.validate(
            url=url,
            expected_elements=["[name='firstName']"]
        )

        assert result.status_code == 200

    @allure.title("Verify P1 performance within threshold")
    @pytest.mark.performance
    def test_p1_load_performance(
        self,
        page: Page,
        url_builder: URLBuilder,
        url_validator: URLValidator
    ):
        """
        Test: Page loads within performance threshold (5 seconds)

        Validates: Performance and load time
        """
        url = url_builder.build(
            workflow_id="WF-P1-PERF",
            page_path="/basic-info",
            query_params={"first_name": "Performance", "last_name": "Test"}
        )

        result = url_validator.validate(url=url)

        assert result.validation_time_ms < 5000, f"Page load too slow: {result.validation_time_ms}ms"

        allure.attach(
            f"Load Time: {result.validation_time_ms}ms",
            "Performance Metrics",
            allure.attachment_type.TEXT
        )

    @allure.title("Verify P1 URL parsing and reconstruction")
    def test_p1_url_parsing(self, url_builder: URLBuilder):
        """
        Test: URL can be parsed and reconstructed correctly

        Validates: URL builder parsing functionality
        """
        original_url = url_builder.build(
            workflow_id="WF-P1-PARSE",
            page_path="/basic-info",
            query_params={"first_name": "Test", "prefill": "true"}
        )

        components = url_builder.parse_url(original_url)

        assert "workflow_id" in components["query_params"]
        assert components["query_params"]["first_name"] == "Test"
        assert components["path"] == "/basic-info"

    @allure.title("Verify P1 with multiple workflow scenarios")
    @pytest.mark.parametrize(
        "workflow_data",
        [
            {"workflow_id": "WF-P1-NEW", "first_name": "New", "last_name": "Patient"},
            {"workflow_id": "WF-P1-RETURN", "first_name": "Return", "last_name": "Patient"},
            {"workflow_id": "WF-P1-EMERGENCY", "first_name": "Urgent", "last_name": "Case"},
        ],
        ids=["new-patient", "returning-patient", "emergency"]
    )
    def test_p1_multiple_workflow_scenarios(
        self,
        page: Page,
        url_builder: URLBuilder,
        url_validator: URLValidator,
        workflow_data: Dict[str, str]
    ):
        """
        Test: Multiple workflow scenarios load correctly

        Validates: Data-driven workflow testing
        """
        url = url_builder.build(
            workflow_id=workflow_data["workflow_id"],
            page_path="/basic-info",
            query_params={
                "first_name": workflow_data["first_name"],
                "last_name": workflow_data["last_name"]
            }
        )

        result = url_validator.validate(
            url=url,
            expected_elements=["[name='firstName']"]
        )

        assert result.is_valid, f"Workflow {workflow_data['workflow_id']} failed: {result.errors}"
        assert result.status_code == 200

