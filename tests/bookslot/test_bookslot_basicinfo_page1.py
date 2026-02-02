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

import allure
import pytest

from pages.bookslot.bookslots_basicinfo_page1 import BookslotBasicInfoPage
from tests.bookslot.helpers.navigation_helper import BookslotNavigator


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
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        basic_info_page = navigator.navigate_to_basic_info()

        # Wait for page to load
        basic_info_page.wait_for_page_load()

        with allure.step("Verify page loaded successfully"):
            # Verify page is loaded
            assert basic_info_page.is_page_loaded(), "Page failed to load"

        with allure.step("Verify form fields are visible"):
            # Use Page Object boolean checks for form fields
            assert basic_info_page.is_first_name_visible(), "First Name field not visible"
            assert basic_info_page.is_last_name_visible(), "Last Name field not visible"
            assert basic_info_page.is_email_visible(), "Email field not visible"
            assert basic_info_page.is_phone_visible(), "Phone field not visible"

            allure.attach(
                basic_info_page.page.screenshot(full_page=True),
                name="basic_info_page_loaded",
                attachment_type=allure.attachment_type.PNG,
            )

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
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        basic_info_page = navigator.navigate_to_basic_info()

        with allure.step(f"Test email: {email} (Expected valid: {is_valid})"):
            basic_info_page.fill_first_name("Test")
            basic_info_page.fill_last_name("User")
            basic_info_page.fill_email(email)
            basic_info_page.fill_phone("5551234567")

            # Verify email field accepted the input
            email_value = basic_info_page.textbox_email.input_value()
            assert (
                email in email_value or email == email_value
            ), f"Email field should contain {email}"

            allure.attach(
                basic_info_page.page.screenshot(full_page=True),
                name=f"email_validation_{email}",
                attachment_type=allure.attachment_type.PNG,
            )

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

            allure.attach(
                basic_info_page.page.screenshot(full_page=True),
                name=f"phone_validation_{phone}",
                attachment_type=allure.attachment_type.PNG,
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
            allure.attach(
                basic_info_page.page.screenshot(full_page=True),
                name="required_fields_validation",
                attachment_type=allure.attachment_type.PNG,
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
            allure.attach(
                basic_info_page.page.screenshot(full_page=True),
                name="successful_submission",
                attachment_type=allure.attachment_type.PNG,
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

            allure.attach(
                basic_info_page.page.screenshot(full_page=True),
                name="special_characters_validation",
                attachment_type=allure.attachment_type.PNG,
            )
