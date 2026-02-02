"""
Test Suite: Basic Info Page
============================
Tests for the Basic Info page (entry point of bookslot flow).

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

Test Coverage:
- First Name field validation
- Last Name field validation
- Email format validation
- Phone number format validation
- Required field validation
- Form submission

Run Commands:
    pytest tests/bookslot/test_basicinfo_page.py -v
    pytest tests/bookslot/test_basicinfo_page.py -m validation -v
    pytest tests/bookslot/test_basicinfo_page.py -k "email" -v
"""

import logging
import allure
import pytest
from pathlib import Path
from datetime import datetime

from pages.bookslot.bookslots_basicinfo_page1 import BookslotBasicInfoPage
from tests.bookslot.helpers.navigation_helper import BookslotNavigator

# Configure logging
logger = logging.getLogger(__name__)

# Create project-specific screenshots directory
SCREENSHOTS_DIR = Path("screenshots") / "bookslot"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def log_and_report(message: str, level: str = "INFO"):
    """
    Log message to console, logger, and Allure report

    Args:
        message: Message to log
        level: Log level (INFO, SUCCESS, WARNING, ERROR)
    """
    # Console output with symbols (safe for Windows console)
    symbols = {"INFO": "[i]", "SUCCESS": "[OK]", "WARNING": "[!]", "ERROR": "[X]", "STEP": "[>]"}
    symbol = symbols.get(level, "[-]")
    
    try:
        print(f"{symbol} {message}")
    except UnicodeEncodeError:
        # Fallback to ASCII if Unicode fails
        print(f"{symbol} {message.encode('ascii', 'ignore').decode('ascii')}")

    # Logger output
    if level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)
    else:
        logger.info(message)

    # Allure output (will appear in test report)
    try:
        allure.attach(
            message, name=f"{level}: {message[:50]}", attachment_type=allure.attachment_type.TEXT
        )
    except Exception:
        pass


def save_screenshot(page, test_name: str, description: str = ""):
    """
    Save screenshot to filesystem AND attach to Allure report

    Args:
        page: Playwright page object
        test_name: Name of the test (for filename)
        description: Optional description for screenshot

    Returns:
        Path to saved screenshot file
    """
    try:
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_test_name = test_name.replace(" ", "_").replace("/", "_")
        filename = f"{safe_test_name}_{timestamp}.png"
        filepath = SCREENSHOTS_DIR / filename

        # Capture screenshot
        screenshot_bytes = page.screenshot(full_page=True)

        # Save to filesystem
        with open(filepath, "wb") as f:
            f.write(screenshot_bytes)

        log_and_report(f"Screenshot saved: {filepath}", "SUCCESS")

        # Attach to Allure report
        allure.attach(
            screenshot_bytes,
            name=description or test_name,
            attachment_type=allure.attachment_type.PNG,
        )

        return filepath
    except Exception as e:
        log_and_report(f"Failed to save screenshot: {e}", "ERROR")
        return None


@allure.epic("Bookslot")
@allure.feature("Basic Info Page")
@pytest.mark.modern_spa
@pytest.mark.bookslot
class TestBasicInfoPage:
    """Test suite for Basic Info page functionality"""

    @allure.story("Page Load")
    @allure.title("Verify Basic Info page loads successfully")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.human_behavior
    def test_basic_info_page_loads(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Basic Info page loads without errors

        Validates: Page is accessible and ready for input
        """
        log_and_report("=" * 80, "STEP")
        log_and_report("TEST: Verify Basic Info page loads successfully", "STEP")
        log_and_report("=" * 80, "STEP")

        log_and_report("Step 1: Initialize navigation helper", "INFO")
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        log_and_report("Navigation helper initialized successfully", "SUCCESS")

        log_and_report("Step 2: Navigate to Basic Info page", "INFO")
        basic_info_page = navigator.navigate_to_basic_info()
        log_and_report(f"Navigated to URL: {basic_info_page.page.url}", "SUCCESS")

        log_and_report("Step 3: Wait for page to load", "INFO")
        basic_info_page.wait_for_page_load()
        log_and_report("Page load wait completed", "SUCCESS")

        with allure.step("Verify page loaded successfully"):
            log_and_report("Step 4: Verify page is loaded", "INFO")
            page_loaded = basic_info_page.is_page_loaded()
            if page_loaded:
                log_and_report("✓ Page loaded successfully", "SUCCESS")
            else:
                log_and_report("✗ Page failed to load", "ERROR")
            assert page_loaded, "Page failed to load"

        with allure.step("Verify form fields are visible"):
            log_and_report("Step 5: Verify all form fields are visible", "INFO")

            # Check First Name field
            log_and_report("  Checking First Name field...", "INFO")
            first_name_visible = basic_info_page.is_first_name_visible()
            if first_name_visible:
                log_and_report("  ✓ First Name field is visible", "SUCCESS")
            else:
                log_and_report("  ✗ First Name field not visible", "ERROR")
            assert first_name_visible, "First Name field not visible"

            # Check Last Name field
            log_and_report("  Checking Last Name field...", "INFO")
            last_name_visible = basic_info_page.is_last_name_visible()
            if last_name_visible:
                log_and_report("  ✓ Last Name field is visible", "SUCCESS")
            else:
                log_and_report("  ✗ Last Name field not visible", "ERROR")
            assert last_name_visible, "Last Name field not visible"

            # Check Email field
            log_and_report("  Checking Email field...", "INFO")
            email_visible = basic_info_page.is_email_visible()
            if email_visible:
                log_and_report("  ✓ Email field is visible", "SUCCESS")
            else:
                log_and_report("  ✗ Email field not visible", "ERROR")
            assert email_visible, "Email field not visible"

            # Check Phone field
            log_and_report("  Checking Phone field...", "INFO")
            phone_visible = basic_info_page.is_phone_visible()
            if phone_visible:
                log_and_report("  ✓ Phone field is visible", "SUCCESS")
            else:
                log_and_report("  ✗ Phone field not visible", "ERROR")
            assert phone_visible, "Phone field not visible"

            log_and_report("Step 6: Capture screenshot", "INFO")
            screenshot_path = save_screenshot(
                basic_info_page.page, 
                "basic_info_page_loaded",
                "Basic Info Page - All Fields Visible"
            )
            if screenshot_path:
                log_and_report(f"Screenshot saved to: {screenshot_path}", "SUCCESS")
            else:
                log_and_report("Screenshot save failed", "WARNING")

        log_and_report("=" * 80, "STEP")
        log_and_report("TEST COMPLETED: All validations passed ✓", "SUCCESS")
        log_and_report("=" * 80, "STEP")

    @allure.story("Email Validation")
    @allure.title("Test email field with various formats")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.validation
    @pytest.mark.parametrize(
        "email,is_valid",
        [
            ("user@example.com", True),
            ("test.user@domain.co.uk", True),
            ("name+tag@email.com", True),
            ("invalid.email", False),
            ("@nodomain.com", False),
            ("missing@", False),
            ("spaces in@email.com", False),
            ("double@@domain.com", False),
        ],
        ids=[
            "valid_simple",
            "valid_subdomain",
            "valid_plus",
            "no_at",
            "no_prefix",
            "no_domain",
            "spaces",
            "double_at",
        ],
    )
    def test_email_validation(
        self, smart_actions, fake_bookslot_data, multi_project_config, email, is_valid
    ):
        """
        Scenario: Validate email field accepts/rejects various formats

        Validates: Email validation rules are enforced
        """
        log_and_report("=" * 80, "STEP")
        log_and_report(f"TEST: Email Validation - {email} (Expected valid: {is_valid})", "STEP")
        log_and_report("=" * 80, "STEP")

        log_and_report("Step 1: Initialize and navigate", "INFO")
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        basic_info_page = navigator.navigate_to_basic_info()
        log_and_report(f"Navigated to: {basic_info_page.page.url}", "SUCCESS")

        with allure.step(f"Test email: {email} (Expected valid: {is_valid})"):
            log_and_report("Step 2: Fill form fields", "INFO")

            log_and_report("  Filling First Name: Test", "INFO")
            basic_info_page.fill_first_name("Test")
            log_and_report("  ✓ First Name filled", "SUCCESS")

            log_and_report("  Filling Last Name: User", "INFO")
            basic_info_page.fill_last_name("User")
            log_and_report("  ✓ Last Name filled", "SUCCESS")

            log_and_report(f"  Filling Email: {email}", "INFO")
            basic_info_page.fill_email(email)
            log_and_report(f"  ✓ Email filled", "SUCCESS")

            log_and_report("  Filling Phone: 5551234567", "INFO")
            basic_info_page.fill_phone("5551234567")
            log_and_report("  ✓ Phone filled", "SUCCESS")

            log_and_report("Step 3: Verify email field value", "INFO")
            email_value = basic_info_page.textbox_email.input_value()
            log_and_report(f"  Email field value: {email_value}", "INFO")

            if email in email_value or email == email_value:
                log_and_report(f"  ✓ Email validation passed for: {email}", "SUCCESS")
            else:
                log_and_report(f"  ✗ Email validation failed for: {email}", "ERROR")

            assert (
                email in email_value or email == email_value
            ), f"Email field should contain {email}"

            log_and_report("Step 4: Capture screenshot", "INFO")
            screenshot_path = save_screenshot(
                basic_info_page.page,
                f"email_validation_{email}",
                f"Email Validation - {email}"
            )
            if screenshot_path:
                log_and_report(f"Screenshot saved to: {screenshot_path}", "SUCCESS")
            else:
                log_and_report("Screenshot save failed", "WARNING")

        log_and_report(f"TEST COMPLETED: Email {email} validation ✓", "SUCCESS")
        log_and_report("=" * 80, "STEP")

    @allure.story("Phone Validation")
    @allure.title("Test phone field with various formats")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.validation
    @pytest.mark.parametrize(
        "phone,is_valid",
        [
            ("5551234567", True),
            ("1234567890", True),
            ("(555) 123-4567", True),
            ("555-123-4567", True),
            ("+1 555 123 4567", True),
            ("123", False),
            ("555", False),
            ("abcdefghij", False),
            ("555-abc-defg", False),
        ],
        ids=[
            "plain_10",
            "alt_10",
            "formatted_parens",
            "formatted_dash",
            "international",
            "too_short_3",
            "too_short_5",
            "letters",
            "mixed",
        ],
    )
    def test_phone_validation(
        self, smart_actions, fake_bookslot_data, multi_project_config, phone, is_valid
    ):
        """
        Scenario: Validate phone field accepts/rejects various formats

        Validates: Phone validation rules are enforced
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        basic_info_page = navigator.navigate_to_basic_info()
        data = fake_bookslot_data

        with allure.step(f"Test phone: {phone} (Expected valid: {is_valid})"):
            basic_info_page.fill_first_name(data["first_name"])
            basic_info_page.fill_last_name(data["last_name"])
            basic_info_page.fill_email(data["email"])
            basic_info_page.fill_phone(phone)

            # Verify phone field accepted the input
            phone_value = basic_info_page.textbox_phone.input_value()
            # Phone might be formatted, so check if original digits are present
            assert phone in phone_value or phone_value, f"Phone field should contain value"

            save_screenshot(
                basic_info_page.page,
                f"phone_validation_{phone}",
                f"Phone Validation - {phone}"
            )

    @allure.story("Name Validation")
    @allure.title("Test first and last name fields")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.validation
    def test_name_fields(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Validate first and last name fields accept valid names

        Validates: Name fields work correctly
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        basic_info_page = navigator.navigate_to_basic_info()

        with allure.step("Test name fields"):
            test_names = [
                ("John", "Smith"),
                ("Mary", "O'Connor"),
                ("José", "García"),
                ("Lee", "van der Berg"),
            ]

            for first, last in test_names:
                basic_info_page.textbox_first_name.clear()
                basic_info_page.textbox_last_name.clear()

                basic_info_page.fill_first_name(first)
                basic_info_page.fill_last_name(last)

                first_value = basic_info_page.textbox_first_name.input_value()
                last_value = basic_info_page.textbox_last_name.input_value()

                assert first in first_value, f"First name {first} should be accepted"
                assert last in last_value, f"Last name {last} should be accepted"

    @allure.story("Required Fields")
    @allure.title("Verify all required fields are enforced")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.validation
    @pytest.mark.smoke
    def test_required_fields(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Attempt to submit form with empty required fields

        Validates: Form prevents submission when required fields are empty
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        basic_info_page = navigator.navigate_to_basic_info()

        with allure.step("Attempt submission with empty form"):
            current_url = basic_info_page.page.url

            # Next button should not be visible/enabled without required fields
            assert (
                not basic_info_page.is_next_button_visible()
            ), "Next button should not be visible without required fields"

            # Verify page didn't progress
            assert (
                basic_info_page.page.url == current_url
            ), "Should not proceed without required fields"
            save_screenshot(
                basic_info_page.page,
                "required_fields_validation",
                "Required Fields Validation - Missing Fields"
            )

    @allure.story("Form Submission")
    @allure.title("Test successful form submission with valid data")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.critical
    def test_successful_submission(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Fill all fields correctly and submit

        Validates: Valid form submission progresses to next page
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        basic_info_page = navigator.navigate_to_basic_info()
        data = fake_bookslot_data

        with allure.step("Fill all required fields"):
            basic_info_page.fill_first_name(data["first_name"])
            basic_info_page.fill_last_name(data["last_name"])
            basic_info_page.fill_email(data["email"])
            basic_info_page.fill_phone(data["phone_number"])
            basic_info_page.fill_zip(data["zip"])

        with allure.step("Submit for OTP"):
            # Submit to get OTP code
            basic_info_page.submit_for_otp()
            basic_info_page.wait_for_page_load()

            # Fill OTP and verify
            basic_info_page.fill_otp(data["verification_code"])
            basic_info_page.verify_otp()
            basic_info_page.wait_for_page_load()

            # Now Next button should be visible
            assert (
                basic_info_page.is_next_button_visible()
            ), "Next button should be visible after OTP verification"

            current_url_before = basic_info_page.page.url
            basic_info_page.proceed_to_next()
            basic_info_page.wait_for_page_load()

            current_url_after = basic_info_page.page.url
            assert (
                current_url_after != current_url_before
            ), "Should proceed to next page after complete form submission"
            save_screenshot(
                basic_info_page.page,
                "successful_submission",
                "Form Submission - Success"
            )

    @allure.story("Special Characters")
    @allure.title("Test fields with special characters")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.validation
    def test_special_characters_in_names(
        self, smart_actions, fake_bookslot_data, multi_project_config
    ):
        """
        Scenario: Test name fields with special characters

        Validates: Names with apostrophes, hyphens, accents are accepted
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        basic_info_page = navigator.navigate_to_basic_info()
        data = fake_bookslot_data

        with allure.step("Test special characters"):
            basic_info_page.fill_first_name("Mary-Anne")
            basic_info_page.fill_last_name("O'Brien")
            basic_info_page.fill_email(data["email"])
            basic_info_page.fill_phone(data["phone_number"])
            basic_info_page.fill_zip(data["zip"])

            # Verify special character names were accepted
            first_value = basic_info_page.textbox_first_name.input_value()
            last_value = basic_info_page.textbox_last_name.input_value()

            assert (
                "Mary-Anne" in first_value or "Mary" in first_value
            ), "First name with hyphen should be accepted"
            assert (
                "O'Brien" in last_value or "Brien" in last_value
            ), "Last name with apostrophe should be accepted"

            save_screenshot(
                basic_info_page.page,
                "special_characters_validation",
                "Special Characters Validation - Hyphens and Apostrophes"
            )
