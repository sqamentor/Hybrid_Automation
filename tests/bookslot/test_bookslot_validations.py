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

import allure
import pytest

from pages.bookslot.bookslots_basicinfo_page1 import BookslotBasicInfoPage
from pages.bookslot.bookslots_insurance_page6 import BookslotInsurancePage
from pages.bookslot.bookslots_patient_type_page import BookslotPatientTypePage
from pages.bookslot.bookslots_personalInfo_page4 import BookslotPersonalInfoPage
from pages.bookslot.bookslots_referral_page5 import BookslotReferralPage
from pages.bookslot.bookslots_scheduler_page import BookslotSchedulerPage


@allure.epic("Bookslot")
@allure.feature("Form Validations")
@pytest.mark.modern_spa
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
        basic_info_page = BookslotBasicInfoPage(page, base_url)
        
        with allure.step(f"Test email: {email} (Expected valid: {should_be_valid})"):
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            
            # ✅ Use Page Object methods
            basic_info_page.fill_first_name("Test")
            basic_info_page.fill_last_name("User")
            basic_info_page.fill_email(email)
            basic_info_page.fill_phone("5551234567")
            
            initial_url = page.url
            basic_info_page.click_next()
            
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
        basic_info_page = BookslotBasicInfoPage(page, base_url)
        
        with allure.step(f"Test phone: {phone} (Expected valid: {should_be_valid})"):
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            
            # ✅ Use Page Object methods
            basic_info_page.fill_first_name(data['first_name'])
            basic_info_page.fill_last_name(data['last_name'])
            basic_info_page.fill_email(data['email'])
            basic_info_page.fill_phone(phone)
            
            initial_url = page.url
            basic_info_page.click_next()
            
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
        basic_info_page = BookslotBasicInfoPage(page, base_url)
        
        with allure.step("Attempt to proceed with empty form"):
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            initial_url = page.url
            
            # ✅ Use Page Object method
            basic_info_page.click_next()
            
            assert page.url == initial_url, "Should not proceed without required fields"
            allure.attach(page.screenshot(full_page=True), name="required_fields_error", 
                         attachment_type=allure.attachment_type.PNG)


@allure.epic("Bookslot")
@allure.feature("Form Validations")
@pytest.mark.modern_spa
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
        basic_info_page = BookslotBasicInfoPage(page, base_url)
        personal_info_page = BookslotPersonalInfoPage(page, base_url)
        
        with allure.step("Navigate to Personal Info page"):
            # ✅ Use Page Objects for navigation
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            basic_info_page.fill_first_name(data['first_name'])
            basic_info_page.fill_last_name(data['last_name'])
            basic_info_page.fill_email(data['email'])
            basic_info_page.fill_phone(data['phone'])
            basic_info_page.click_next()
            
            # Navigate through patient type and event selection
            patient_type_page = BookslotPatientTypePage(page)
            patient_type_page.select_new_patient()
            patient_type_page.click_next()
            
            scheduler_page = BookslotSchedulerPage(page)
            scheduler_page.wait_for_scheduler_ready()
            scheduler_page.select_am_slot()
            scheduler_page.click_next()
        
        with allure.step(f"Test zip code: {zip_code} (Expected valid: {should_be_valid})"):
            # ✅ Use Page Object methods
            personal_info_page.fill_dob(data['dob'])
            personal_info_page.fill_address("123 Test St")
            personal_info_page.fill_city("Test City")
            personal_info_page.fill_state("NY")
            personal_info_page.fill_zip_code(zip_code)
            
            initial_url = page.url
            personal_info_page.click_next()
            
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
        basic_info_page = BookslotBasicInfoPage(page, base_url)
        personal_info_page = BookslotPersonalInfoPage(page, base_url)
        
        with allure.step("Navigate to Personal Info page"):
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            
            # ✅ Use Page Object methods
            basic_info_page.fill_first_name(data['first_name'])
            basic_info_page.fill_last_name(data['last_name'])
            basic_info_page.fill_email(data['email'])
            basic_info_page.fill_phone(data['phone'])
            basic_info_page.click_next()
            
            patient_type_page = BookslotPatientTypePage(page)
            patient_type_page.select_new_patient()
            patient_type_page.click_next()
            
            scheduler_page = BookslotSchedulerPage(page)
            scheduler_page.wait_for_scheduler_ready()
            scheduler_page.select_am_slot()
            scheduler_page.click_next()
        
        with allure.step(f"Enter DOB: {dob}"):
            # ✅ Use Page Object method
            personal_info_page.fill_dob(dob)
            allure.attach(f"DOB: {dob}", name="dob_entered", attachment_type=allure.attachment_type.TEXT)


@allure.epic("Bookslot")
@allure.feature("Form Validations")
@pytest.mark.modern_spa
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
        basic_info_page = BookslotBasicInfoPage(page, base_url)
        personal_info_page = BookslotPersonalInfoPage(page, base_url)
        
        with allure.step("Navigate to Insurance page"):
            # ✅ Use Page Objects for navigation
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            basic_info_page.fill_first_name(data['first_name'])
            basic_info_page.fill_last_name(data['last_name'])
            basic_info_page.fill_email(data['email'])
            basic_info_page.fill_phone(data['phone'])
            basic_info_page.click_next()
            
            # Navigate through patient type and event selection
            patient_type_page = BookslotPatientTypePage(page)
            patient_type_page.select_new_patient()
            patient_type_page.click_next()
            
            scheduler_page = BookslotSchedulerPage(page)
            scheduler_page.wait_for_scheduler_ready()
            scheduler_page.select_am_slot()
            scheduler_page.click_next()
            
            # ✅ Use Page Object for personal info
            personal_info_page.fill_dob(data['dob'])
            personal_info_page.fill_address("123 Test St")
            personal_info_page.fill_city("Test City")
            personal_info_page.click_next()
            
            # ✅ Use Referral Page Object
            referral_page = BookslotReferralPage(page, base_url)
            referral_page.select_online()
            referral_page.click_next()
        
        with allure.step(f"Test insurance ID: {id_number} (Expected valid: {should_be_valid})"):
            # ✅ Use Insurance Page Object
            insurance_page = BookslotInsurancePage(page, base_url)
            insurance_page.fill_member_name("Test Member")
            insurance_page.fill_id_number(id_number)
            insurance_page.fill_insurance_company("Test Payer")
            
            initial_url = page.url
            insurance_page.proceed_to_next()
            
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
        basic_info_page = BookslotBasicInfoPage(page, base_url)
        personal_info_page = BookslotPersonalInfoPage(page, base_url)
        
        with allure.step("Navigate to Insurance page"):
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            
            # ✅ Use Page Objects
            basic_info_page.fill_first_name(data['first_name'])
            basic_info_page.fill_last_name(data['last_name'])
            basic_info_page.fill_email(data['email'])
            basic_info_page.fill_phone(data['phone'])
            basic_info_page.click_next()
            
            # Navigate through patient type and event selection
            patient_type_page = BookslotPatientTypePage(page)
            patient_type_page.select_new_patient()
            patient_type_page.click_next()
            
            scheduler_page = BookslotSchedulerPage(page)
            scheduler_page.wait_for_scheduler_ready()
            scheduler_page.select_am_slot()
            scheduler_page.click_next()
            
            personal_info_page.fill_dob(data['dob'])
            personal_info_page.fill_address("123 Test St")
            personal_info_page.fill_city("Test City")
            personal_info_page.click_next()
            
            # ✅ Use Referral Page Object
            referral_page = BookslotReferralPage(page, base_url)
            referral_page.select_online()
            referral_page.click_next()
        
        with allure.step("Submit insurance without group number"):
            # ✅ Use Insurance Page Object
            insurance_page = BookslotInsurancePage(page, base_url)
            insurance_page.fill_member_name("Test Member")
            insurance_page.fill_id_number("123456789")
            # Intentionally skip Group Number
            insurance_page.fill_insurance_company("Aetna")
            
            initial_url = page.url
            insurance_page.proceed_to_next()
            
            assert page.url != initial_url, "Should allow progression without group number"
            allure.attach("Group number optional validation passed", name="optional_field_test", 
                         attachment_type=allure.attachment_type.TEXT)
