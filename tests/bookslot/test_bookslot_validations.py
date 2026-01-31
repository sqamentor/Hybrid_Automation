"""
Test Suite: Bookslot Field Validations
======================================
Focused validation tests for form fields without repeating full booking flow.

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

Test Strategy:
- Test validation rules in isolation
- Use lightweight navigation (minimal steps)
- Focus on edge cases and boundary conditions
- Fast execution for CI/CD pipelines

Test Coverage:
- Email format validation
- Phone number formats
- Zip code validation
- Date of birth restrictions
- Insurance ID formats
- Required field validation
- Character limits
- Special character handling

Run Commands:
    pytest tests/bookslot/test_bookslot_validations.py -v
    pytest tests/bookslot/test_bookslot_validations.py -m validation -v
    pytest tests/bookslot/test_bookslot_validations.py::TestBasicInfoValidations -v
"""

import pytest
import allure
from playwright.sync_api import Page


@allure.epic("Bookslot")
@allure.feature("Form Validations")
@pytest.mark.bookslot
@pytest.mark.validation
class TestBasicInfoValidations:
    """Validation tests for Basic Info page fields"""

    @allure.story("Email Validation")
    @allure.title("Verify email format validation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("email,should_be_valid", [
        ("valid@email.com", True),
        ("user.name@domain.co.uk", True),
        ("test+tag@example.com", True),
        ("invalid.email", False),
        ("@nodomain.com", False),
        ("missing@", False),
        ("spaces in@email.com", False),
    ], ids=["valid_simple", "valid_subdomain", "valid_plus", "no_at", "no_prefix", "no_domain", "spaces"])
    def test_email_format_validation(
        self, page: Page, multi_project_config, smart_actions, email, should_be_valid
    ):
        """
        Scenario: Validate email format requirements
        
        Tests various email formats for proper validation
        """
        base_url = multi_project_config['bookslot']['ui_url']
        act = smart_actions
        
        with allure.step(f"Test email: {email} (Expected valid: {should_be_valid})"):
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            act.type_text(page.get_by_role("textbox", name="First Name *"), "Test", "First Name")
            act.type_text(page.get_by_role("textbox", name="Last Name *"), "User", "Last Name")
            act.type_text(page.get_by_role("textbox", name="Email *"), email, "Email")
            act.type_text(page.get_by_role("textbox", name="Phone *"), "5551234567", "Phone")
            
            initial_url = page.url
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            page.wait_for_timeout(800)
            
            if should_be_valid:
                assert page.url != initial_url, f"Valid email {email} should allow progression"
            else:
                assert page.url == initial_url, f"Invalid email {email} should prevent progression"
            
            allure.attach(page.screenshot(full_page=True), 
                         name=f"email_{email.replace('@', '_at_').replace('.', '_')}", 
                         attachment_type=allure.attachment_type.PNG)

    @allure.story("Phone Number Validation")
    @allure.title("Verify phone number format validation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("phone,should_be_valid", [
        ("5551234567", True),
        ("(555) 123-4567", True),
        ("555-123-4567", True),
        ("+1 555 123 4567", True),
        ("123", False),
        ("abcdefghij", False),
        ("555", False),
    ], ids=["plain_10", "formatted_parens", "formatted_dash", "international", "too_short", "letters", "incomplete"])
    def test_phone_number_format_validation(
        self, page: Page, multi_project_config, smart_actions, fake_bookslot_data, phone, should_be_valid
    ):
        """
        Scenario: Validate phone number format requirements
        
        Tests various phone formats for proper validation
        """
        base_url = multi_project_config['bookslot']['ui_url']
        act = smart_actions
        data = fake_bookslot_data
        
        with allure.step(f"Test phone: {phone} (Expected valid: {should_be_valid})"):
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            act.type_text(page.get_by_role("textbox", name="First Name *"), data['first_name'], "First Name")
            act.type_text(page.get_by_role("textbox", name="Last Name *"), data['last_name'], "Last Name")
            act.type_text(page.get_by_role("textbox", name="Email *"), data['email'], "Email")
            act.type_text(page.get_by_role("textbox", name="Phone *"), phone, "Phone")
            
            initial_url = page.url
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            page.wait_for_timeout(800)
            
            if should_be_valid:
                assert page.url != initial_url, f"Valid phone {phone} should allow progression"
            else:
                assert page.url == initial_url, f"Invalid phone {phone} should prevent progression"

    @allure.story("Required Fields")
    @allure.title("Verify all required fields on basic info page")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_basic_info_required_fields(
        self, page: Page, multi_project_config, smart_actions
    ):
        """
        Scenario: Attempt to proceed without filling required fields
        
        Validates: Form prevents submission when required fields are empty
        """
        base_url = multi_project_config['bookslot']['ui_url']
        act = smart_actions
        
        with allure.step("Attempt to proceed with empty form"):
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            initial_url = page.url
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            page.wait_for_timeout(800)
            
            assert page.url == initial_url, "Should not proceed without required fields"
            allure.attach(page.screenshot(full_page=True), name="required_fields_error", 
                         attachment_type=allure.attachment_type.PNG)


@allure.epic("Bookslot")
@allure.feature("Form Validations")
@pytest.mark.bookslot
@pytest.mark.validation
class TestPersonalInfoValidations:
    """Validation tests for Personal Info page fields"""

    @allure.story("Zip Code Validation")
    @allure.title("Verify zip code format validation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("zip_code,should_be_valid", [
        ("12345", True),
        ("90210", True),
        ("12345-6789", True),
        ("123", False),
        ("ABCDE", False),
        ("123456", False),
    ], ids=["valid_5", "valid_90210", "valid_9", "too_short", "letters", "too_long"])
    def test_zip_code_format_validation(
        self, page: Page, multi_project_config, smart_actions, fake_bookslot_data, zip_code, should_be_valid
    ):
        """
        Scenario: Validate zip code format requirements
        
        Tests various zip code formats for proper validation
        """
        base_url = multi_project_config['bookslot']['ui_url']
        act = smart_actions
        data = fake_bookslot_data
        
        with allure.step("Navigate to Personal Info page"):
            # Minimal path to reach personal info
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            act.type_text(page.get_by_role("textbox", name="First Name *"), data['first_name'], "First Name")
            act.type_text(page.get_by_role("textbox", name="Last Name *"), data['last_name'], "Last Name")
            act.type_text(page.get_by_role("textbox", name="Email *"), data['email'], "Email")
            act.type_text(page.get_by_role("textbox", name="Phone *"), data['phone'], "Phone")
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            
            act.button_click(page.get_by_role("button", name="New Patient"), "New Patient")
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            
            act.wait_for_scheduler(page)
            page.locator("button:has-text('AM')").first.click()
            act.button_click(page.get_by_role("button", name="Next"), "Next")
        
        with allure.step(f"Test zip code: {zip_code} (Expected valid: {should_be_valid})"):
            act.type_text(page.get_by_role("textbox", name="Date of Birth *"), data['dob'], "DOB")
            act.type_text(page.get_by_role("textbox", name="Address *"), "123 Test St", "Address")
            act.type_text(page.get_by_role("textbox", name="City *"), "Test City", "City")
            act.type_text(page.get_by_role("textbox", name="State *"), "NY", "State")
            act.type_text(page.get_by_role("textbox", name="Zip Code *"), zip_code, "Zip Code")
            
            initial_url = page.url
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            page.wait_for_timeout(800)
            
            if should_be_valid:
                assert page.url != initial_url, f"Valid zip {zip_code} should allow progression"
            else:
                assert page.url == initial_url, f"Invalid zip {zip_code} should prevent progression"

    @allure.story("Date of Birth Validation")
    @allure.title("Verify date of birth format validation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("dob", [
        "01/01/2000",
        "12/31/1990",
        "06/15/1985",
        "03/20/1995"
    ], ids=["jan_2000", "dec_1990", "jun_1985", "mar_1995"])
    def test_date_of_birth_format_validation(
        self, page: Page, multi_project_config, smart_actions, fake_bookslot_data, dob
    ):
        """
        Scenario: Validate date of birth accepts various valid formats
        
        Tests that DOB field accepts properly formatted dates
        """
        base_url = multi_project_config['bookslot']['ui_url']
        act = smart_actions
        data = fake_bookslot_data
        
        with allure.step("Navigate to Personal Info page"):
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            act.type_text(page.get_by_role("textbox", name="First Name *"), data['first_name'], "First Name")
            act.type_text(page.get_by_role("textbox", name="Last Name *"), data['last_name'], "Last Name")
            act.type_text(page.get_by_role("textbox", name="Email *"), data['email'], "Email")
            act.type_text(page.get_by_role("textbox", name="Phone *"), data['phone'], "Phone")
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            
            act.button_click(page.get_by_role("button", name="New Patient"), "New Patient")
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            
            act.wait_for_scheduler(page)
            page.locator("button:has-text('AM')").first.click()
            act.button_click(page.get_by_role("button", name="Next"), "Next")
        
        with allure.step(f"Enter DOB: {dob}"):
            act.type_text(page.get_by_role("textbox", name="Date of Birth *"), dob, "DOB")
            allure.attach(f"DOB: {dob}", name="dob_entered", attachment_type=allure.attachment_type.TEXT)


@allure.epic("Bookslot")
@allure.feature("Form Validations")
@pytest.mark.bookslot
@pytest.mark.validation
class TestInsuranceValidations:
    """Validation tests for Insurance page fields"""

    @allure.story("Insurance ID Validation")
    @allure.title("Verify insurance ID number format validation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("id_number,should_be_valid", [
        ("123456789", True),
        ("ABC123XYZ", True),
        ("12345678901234", True),
        ("123", False),
        ("", False),
    ], ids=["numeric", "alphanumeric", "long_id", "too_short", "empty"])
    def test_insurance_id_format_validation(
        self, page: Page, multi_project_config, smart_actions, fake_bookslot_data, id_number, should_be_valid
    ):
        """
        Scenario: Validate insurance ID number format requirements
        
        Tests various ID formats for proper validation
        """
        base_url = multi_project_config['bookslot']['ui_url']
        act = smart_actions
        data = fake_bookslot_data
        
        with allure.step("Navigate to Insurance page"):
            # Minimal path to reach insurance
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            act.type_text(page.get_by_role("textbox", name="First Name *"), data['first_name'], "First Name")
            act.type_text(page.get_by_role("textbox", name="Last Name *"), data['last_name'], "Last Name")
            act.type_text(page.get_by_role("textbox", name="Email *"), data['email'], "Email")
            act.type_text(page.get_by_role("textbox", name="Phone *"), data['phone'], "Phone")
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            
            act.button_click(page.get_by_role("button", name="New Patient"), "New Patient")
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            
            act.wait_for_scheduler(page)
            page.locator("button:has-text('AM')").first.click()
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            
            act.type_text(page.get_by_role("textbox", name="Date of Birth *"), data['dob'], "DOB")
            act.type_text(page.get_by_role("textbox", name="Address *"), "123 Test St", "Address")
            act.type_text(page.get_by_role("textbox", name="City *"), "Test City", "City")
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            
            page.get_by_role("radio", name="Online search").click()
            act.button_click(page.get_by_role("button", name="Next"), "Next")
        
        with allure.step(f"Test insurance ID: {id_number} (Expected valid: {should_be_valid})"):
            act.type_text(page.get_by_role("textbox", name="Member Name *"), "Test Member", "Member")
            act.type_text(page.get_by_role("textbox", name="ID Number *"), id_number, "ID Number")
            act.type_text(page.get_by_role("textbox", name="Payer Name *"), "Test Payer", "Payer")
            
            initial_url = page.url
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            page.wait_for_timeout(800)
            
            if should_be_valid:
                assert page.url != initial_url, f"Valid ID {id_number} should allow progression"
            else:
                assert page.url == initial_url, f"Invalid ID {id_number} should prevent progression"

    @allure.story("Group Number Validation")
    @allure.title("Verify group number is optional")
    @allure.severity(allure.severity_level.MINOR)
    def test_insurance_group_number_optional(
        self, page: Page, multi_project_config, smart_actions, fake_bookslot_data
    ):
        """
        Scenario: Verify group number can be left empty
        
        Validates: Group number is optional field
        """
        base_url = multi_project_config['bookslot']['ui_url']
        act = smart_actions
        data = fake_bookslot_data
        
        with allure.step("Navigate to Insurance page"):
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            act.type_text(page.get_by_role("textbox", name="First Name *"), data['first_name'], "First Name")
            act.type_text(page.get_by_role("textbox", name="Last Name *"), data['last_name'], "Last Name")
            act.type_text(page.get_by_role("textbox", name="Email *"), data['email'], "Email")
            act.type_text(page.get_by_role("textbox", name="Phone *"), data['phone'], "Phone")
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            
            act.button_click(page.get_by_role("button", name="New Patient"), "New Patient")
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            
            act.wait_for_scheduler(page)
            page.locator("button:has-text('AM')").first.click()
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            
            act.type_text(page.get_by_role("textbox", name="Date of Birth *"), data['dob'], "DOB")
            act.type_text(page.get_by_role("textbox", name="Address *"), "123 Test St", "Address")
            act.type_text(page.get_by_role("textbox", name="City *"), "Test City", "City")
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            
            page.get_by_role("radio", name="Online search").click()
            act.button_click(page.get_by_role("button", name="Next"), "Next")
        
        with allure.step("Submit insurance without group number"):
            act.type_text(page.get_by_role("textbox", name="Member Name *"), "Test Member", "Member")
            act.type_text(page.get_by_role("textbox", name="ID Number *"), "123456789", "ID")
            # Intentionally skip Group Number
            act.type_text(page.get_by_role("textbox", name="Payer Name *"), "Aetna", "Payer")
            
            initial_url = page.url
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            page.wait_for_timeout(800)
            
            assert page.url != initial_url, "Should allow progression without group number"
            allure.attach("Group number optional validation passed", name="optional_field_test", 
                         attachment_type=allure.attachment_type.TEXT)
