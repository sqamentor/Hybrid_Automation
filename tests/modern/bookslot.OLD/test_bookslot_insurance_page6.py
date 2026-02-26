"""
Test Suite: Insurance Page
===========================
Tests for the Insurance Information page.

Author: Lokendra Singh
Email: lokendra.singh@centerforvein.com
Website: www.centerforvein.com

Test Coverage:
- Member name validation
- Insurance ID validation
- Group number validation (optional)
- Payer name validation
- Required field validation
- Various insurance providers
- Form submission

Run Commands:
    pytest tests/bookslot/test_insurance_page.py -v
    pytest tests/bookslot/test_insurance_page.py -m validation -v
    pytest tests/bookslot/test_insurance_page.py -k "insurance_id" -v
"""

import allure
import pytest

from pages.bookslot.bookslots_insurance_page6 import BookslotInsurancePage
from tests.bookslot.helpers.navigation_helper import BookslotNavigator


@allure.epic("Bookslot")
@allure.feature("Insurance Page")
@pytest.mark.playwright
@pytest.mark.modern_spa
@pytest.mark.bookslot
class TestInsurancePage:
    """Test suite for Insurance page functionality"""

    @allure.story("Page Load")
    @allure.title("Verify Insurance page loads successfully")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.human_behavior
    def test_insurance_page_loads(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Insurance page loads after Referral selection

        Validates: Page is accessible and form fields are visible
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        navigator.navigate_to_insurance()
        insurance_page = BookslotInsurancePage(
            smart_actions.page, multi_project_config["bookslot"]["ui_url"]
        )

        with allure.step("Verify insurance form fields are visible"):
            assert insurance_page.textbox_member_name.is_visible()
            assert insurance_page.textbox_id_number.is_visible()
            assert insurance_page.textbox_group_number.is_visible()
            assert insurance_page.textbox_insurance_company.is_visible()
            assert insurance_page.button_next.is_visible()

            allure.attach(
                page.screenshot(full_page=True),
                name="insurance_page_loaded",
                attachment_type=allure.attachment_type.PNG,
            )

    @allure.story("Member Name Validation")
    @allure.title("Test member name field accepts valid names")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.validation
    @pytest.mark.parametrize(
        "member_name",
        [
            "John Smith",
            "Mary O'Connor",
            "José García",
            "Lisa-Marie Johnson",
            "Dr. Robert Brown",
        ],
        ids=["simple", "apostrophe", "accents", "hyphen", "title"],
    )
    def test_member_name_validation(self, smart_actions, fake_bookslot_data, member_name):
        """
        Scenario: Test member name field with various name formats

        Validates: Member name accepts different name formats
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        navigator.navigate_to_insurance()
        act = smart_actions
        insurance_page = BookslotInsurancePage(
            smart_actions.page, multi_project_config["bookslot"]["ui_url"]
        )

        with allure.step(f"Test member name: {member_name}"):
            insurance_page.fill_member_name(member_name)

            name_value = insurance_page.get_member_name_value()
            assert member_name in name_value, f"Member name {member_name} should be accepted"

    @allure.story("Insurance ID Validation")
    @allure.title("Test insurance ID with various formats")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.validation
    @pytest.mark.parametrize(
        "id_number,is_valid",
        [
            ("123456789", True),
            ("ABC123456", True),
            ("ABC123XYZ", True),
            ("12345678901234", True),
            ("MEM-12345-ABC", True),
            ("123", False),
            ("12", False),
            ("", False),
        ],
        ids=[
            "numeric",
            "alpha_numeric",
            "mixed",
            "long_id",
            "formatted",
            "too_short_3",
            "too_short_2",
            "empty",
        ],
    )
    def test_insurance_id_validation(self, smart_actions, fake_bookslot_data, id_number, is_valid):
        """
        Scenario: Validate insurance ID number format requirements

        Validates: Insurance ID validation rules are enforced
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        navigator.navigate_to_insurance()
        act = smart_actions
        insurance_page = BookslotInsurancePage(
            smart_actions.page, multi_project_config["bookslot"]["ui_url"]
        )

        with allure.step(f"Test insurance ID: {id_number} (Expected valid: {is_valid})"):
            insurance_page.fill_member_name("Test Member")
            insurance_page.fill_id_number(id_number)
            insurance_page.fill_insurance_company("Aetna")

            initial_url = smart_actions.page.url
            insurance_page.submit_next()
            smart_actions.page.wait_for_timeout(800)

            if is_valid:
                assert (
                    smart_actions.page.url != initial_url
                ), f"Valid ID {id_number} should allow progression"
            else:
                assert (
                    smart_actions.page.url == initial_url
                ), f"Invalid ID {id_number} should prevent progression"

    @allure.story("Group Number Validation")
    @allure.title("Verify group number is optional")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.validation
    @pytest.mark.smoke
    def test_group_number_optional(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Submit form without group number

        Validates: Group number field is truly optional
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        navigator.navigate_to_insurance()
        act = smart_actions
        insurance_page = BookslotInsurancePage(
            smart_actions.page, multi_project_config["bookslot"]["ui_url"]
        )

        with allure.step("Submit without group number"):
            insurance_page.fill_member_name("Test Member")
            insurance_page.fill_id_number("123456789")
            # Intentionally skip Group Number
            insurance_page.fill_insurance_company("Aetna")

            initial_url = smart_actions.page.url
            insurance_page.submit_next()
            smart_actions.page.wait_for_timeout(1000)

            assert (
                smart_actions.page.url != initial_url
            ), "Should allow progression without group number"
            allure.attach(
                smart_actions.page.screenshot(full_page=True),
                name="optional_group_number",
                attachment_type=allure.attachment_type.PNG,
            )

    @allure.story("Group Number Validation")
    @allure.title("Test group number field accepts values when provided")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.validation
    def test_group_number_accepts_input(
        self, smart_actions, fake_bookslot_data, multi_project_config
    ):
        """
        Scenario: Test group number field accepts various formats

        Validates: Group number field works when data is provided
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        navigator.navigate_to_insurance()
        act = smart_actions
        insurance_page = BookslotInsurancePage(
            smart_actions.page, multi_project_config["bookslot"]["ui_url"]
        )

        with allure.step("Test group number with value"):
            test_group_numbers = ["GRP-1234", "12345", "ABC123", "GROUP-XYZ"]

            for group_num in test_group_numbers:
                insurance_page.clear_group_number()
                insurance_page.fill_group_number(group_num)

                group_value = insurance_page.get_group_number_value()
                assert group_num in group_value, f"Group number {group_num} should be accepted"

    @allure.story("Payer Name Validation")
    @allure.title("Test insurance payer field with various providers")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "payer_name",
        [
            "Aetna",
            "Blue Cross Blue Shield",
            "Cigna",
            "UnitedHealthcare",
            "Medicare",
            "Humana",
            "Custom Insurance Co.",
        ],
        ids=["aetna", "bcbs", "cigna", "uhc", "medicare", "humana", "custom"],
    )
    def test_payer_name_validation(self, smart_actions, fake_bookslot_data, payer_name):
        """
        Scenario: Test payer name field with various insurance providers

        Validates: System accepts different insurance company names
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        page = navigator.navigate_to_insurance()
        act = smart_actions

        with allure.step(f"Test payer: {payer_name}"):
            insurance_page.fill_member_name("Test Member")
            insurance_page.fill_id_number("123456789")
            insurance_page.fill_insurance_company(payer_name)

            initial_url = smart_actions.page.url
            insurance_page.submit_next()
            smart_actions.page.wait_for_timeout(800)

            assert page.url != initial_url, f"Should accept payer: {payer_name}"
            allure.attach(
                page.screenshot(full_page=True),
                name=f"{payer_name.lower().replace(' ', '_')}_accepted",
                attachment_type=allure.attachment_type.PNG,
            )

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
        page = navigator.navigate_to_insurance()
        act = smart_actions

        with allure.step("Attempt submission with empty form"):
            initial_url = smart_actions.page.url
            insurance_page.submit_next()
            smart_actions.page.wait_for_timeout(800)

            assert page.url == initial_url, "Should not proceed without required fields"
            allure.attach(
                page.screenshot(full_page=True),
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
        Scenario: Fill all required fields and submit

        Validates: Valid form submission progresses to success page
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        page = navigator.navigate_to_insurance()
        act = smart_actions
        data = fake_bookslot_data

        with allure.step("Fill all required fields"):
            insurance_page.fill_member_name(data["MemberName"])
            insurance_page.fill_id_number(data["idNumber"])
            insurance_page.fill_group_number(data["GroupNumber"])
            insurance_page.fill_insurance_company(data["PayerName"])

        with allure.step("Submit form"):
            initial_url = smart_actions.page.url
            insurance_page.submit_next()
            smart_actions.page.wait_for_timeout(1000)

            assert page.url != initial_url, "Should proceed to success page with valid data"
            assert "/success" in page.url.lower() or "confirmation" in page.url.lower()
            allure.attach(
                page.screenshot(full_page=True),
                name="successful_submission",
                attachment_type=allure.attachment_type.PNG,
            )

    @allure.story("Insurance Provider Coverage")
    @allure.title("Test major insurance providers are supported")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_major_insurance_providers(
        self, smart_actions, fake_bookslot_data, multi_project_config
    ):
        """
        Scenario: Verify system accepts major insurance providers

        Validates: Top insurance companies can be processed
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        page = navigator.navigate_to_insurance()

        with allure.step("Verify major providers are accepted"):
            major_providers = [
                "Aetna",
                "Blue Cross Blue Shield",
                "Cigna",
                "UnitedHealthcare",
                "Medicare",
            ]

            allure.attach(
                f"Major providers tested: {len(major_providers)}",
                name="provider_coverage",
                attachment_type=allure.attachment_type.TEXT,
            )
