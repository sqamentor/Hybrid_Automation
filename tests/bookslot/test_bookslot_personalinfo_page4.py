"""
Test Suite: Personal Info Page
===============================
Tests for the Personal Info page (demographics and address).

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

Test Coverage:
- Date of Birth validation
- Address field validation
- City field validation
- State field validation
- Zip code validation
- Required field validation
- Form submission

Run Commands:
    pytest tests/bookslot/test_personalinfo_page.py -v
    pytest tests/bookslot/test_personalinfo_page.py -m validation -v
    pytest tests/bookslot/test_personalinfo_page.py -k "zip" -v
"""

import allure
import pytest

from pages.bookslot.bookslots_personalInfo_page4 import BookslotPersonalInfoPage
from tests.bookslot.helpers.navigation_helper import BookslotNavigator


@allure.epic("Bookslot")
@allure.feature("Personal Info Page")
@pytest.mark.modern_spa
@pytest.mark.bookslot
class TestPersonalInfoPage:
    """Test suite for Personal Info page functionality"""

    @allure.story("Page Load")
    @allure.title("Verify Personal Info page loads successfully")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.human_behavior
    def test_personal_info_page_loads(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Personal Info page loads after Scheduler selection
        
        Validates: Page is accessible and form fields are visible
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        page = navigator.navigate_to_personal_info()
        
        with allure.step("Verify page elements are visible"):
            assert page.combobox_dob.is_visible()
            assert page.textbox_address.is_visible()
            assert page.textbox_city.is_visible()
            assert page.textbox_zip.is_visible()
            assert page.button_next.is_visible()
            
            allure.attach(page.screenshot(full_page=True), 
                         name="personal_info_page_loaded", 
                         attachment_type=allure.attachment_type.PNG)

    @allure.story("Date of Birth Validation")
    @allure.title("Test DOB field with valid dates")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.validation
    @pytest.mark.parametrize("dob", [
        "01/01/2000",
        "12/31/1990",
        "06/15/1985",
        "03/20/1995",
        "08/08/1988",
    ], ids=["jan_2000", "dec_1990", "jun_1985", "mar_1995", "aug_1988"])
    def test_dob_valid_formats(self, smart_actions, fake_bookslot_data, dob):
        """
        Scenario: Test DOB field accepts valid date formats
        
        Validates: DOB field accepts properly formatted dates
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        navigator.navigate_to_personal_info()
        act = smart_actions
        personal_page = BookslotPersonalInfoPage(smart_actions.page, multi_project_config['bookslot']['ui_url'])
        
        with allure.step(f"Test DOB: {dob}"):
            personal_page.fill_dob(dob)
            
            dob_value = personal_page.get_dob_value()
            assert len(dob_value) > 0, f"DOB {dob} should be accepted"
            
            allure.attach(f"DOB entered: {dob}", 
                         name="dob_validation", 
                         attachment_type=allure.attachment_type.TEXT)

    @allure.story("Zip Code Validation")
    @allure.title("Test zip code field with various formats")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.validation
    @pytest.mark.parametrize("zip_code,is_valid", [
        ("12345", True),
        ("90210", True),
        ("20678", True),
        ("12345-6789", True),
        ("123", False),
        ("ABCDE", False),
        ("123456", False),
        ("1234", False),
    ], ids=["valid_5", "valid_90210", "valid_20678", "valid_9", "too_short", "letters", "too_long", "4_digits"])
    def test_zip_code_validation(self, smart_actions, fake_bookslot_data, zip_code, is_valid):
        """
        Scenario: Validate zip code field accepts/rejects various formats
        
        Validates: Zip code validation rules are enforced
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        navigator.navigate_to_personal_info()
        act = smart_actions
        data = fake_bookslot_data
        personal_page = BookslotPersonalInfoPage(smart_actions.page, multi_project_config['bookslot']['ui_url'])
        
        with allure.step(f"Test zip code: {zip_code} (Expected valid: {is_valid})"):
            personal_page.fill_dob(data['dob'])
            personal_page.fill_address("123 Test St")
            personal_page.fill_city("Test City")
            personal_page.fill_state("NY")
            personal_page.fill_zip(zip_code)
            
            initial_url = smart_actions.page.url
            personal_page.proceed_to_next()
            smart_actions.page.wait_for_timeout(800)
            
            if is_valid:
                assert smart_actions.page.url != initial_url, f"Valid zip {zip_code} should allow progression"
            else:
                assert smart_actions.page.url == initial_url, f"Invalid zip {zip_code} should prevent progression"

    @allure.story("Address Validation")
    @allure.title("Test address field accepts various formats")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.validation
    def test_address_field(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Test address field with different address formats
        
        Validates: Address field accepts various address formats
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        page = navigator.navigate_to_personal_info()
        act = smart_actions
        
        with allure.step("Test various address formats"):
            test_addresses = [
                "123 Main Street",
                "456 Oak Avenue Apt 2B",
                "789 Elm St, Unit 5",
                "P.O. Box 12345",
                "1000 W. Sunset Blvd",
            ]
            
            for address in test_addresses:
                personal_page.clear_address()
                personal_page.fill_address(address)
                
                address_value = personal_page.get_address_value()
                assert address in address_value, f"Address {address} should be accepted"

    @allure.story("City Validation")
    @allure.title("Test city field accepts various city names")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.validation
    def test_city_field(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Test city field with different city names
        
        Validates: City field accepts various formats
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        page = navigator.navigate_to_personal_info()
        act = smart_actions
        
        with allure.step("Test various city names"):
            test_cities = [
                "New York",
                "San Francisco",
                "Los Angeles",
                "St. Louis",
                "Washington D.C.",
            ]
            
            for city in test_cities:
                personal_page.clear_city()
                personal_page.fill_city(city)
                
                city_value = personal_page.get_city_value()
                assert city in city_value, f"City {city} should be accepted"

    @allure.story("State Validation")
    @allure.title("Test state field accepts valid state codes")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.validation
    @pytest.mark.parametrize("state", ["NY", "CA", "TX", "FL", "IL", "WA", "PA"])
    def test_state_field(self, smart_actions, fake_bookslot_data, state):
        """
        Scenario: Test state field with different state codes
        
        Validates: State field accepts valid state abbreviations
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        page = navigator.navigate_to_personal_info()
        act = smart_actions
        
        with allure.step(f"Test state: {state}"):
            personal_page.fill_state(state)
            
            state_value = personal_page.get_state_value()
            assert state in state_value, f"State {state} should be accepted"

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
        navigator.navigate_to_personal_info()
        act = smart_actions
        personal_page = BookslotPersonalInfoPage(smart_actions.page, multi_project_config['bookslot']['ui_url'])
        
        with allure.step("Attempt submission with empty form"):
            initial_url = smart_actions.page.url
            personal_page.proceed_to_next()
            smart_actions.page.wait_for_timeout(800)
            
            assert smart_actions.page.url == initial_url, "Should not proceed without required fields"
            allure.attach(smart_actions.page.screenshot(full_page=True), 
                         name="required_fields_validation", 
                         attachment_type=allure.attachment_type.PNG)

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
        navigator.navigate_to_personal_info()
        act = smart_actions
        data = fake_bookslot_data
        personal_page = BookslotPersonalInfoPage(smart_actions.page, multi_project_config['bookslot']['ui_url'])
        
        with allure.step("Fill all required fields"):
            personal_page.fill_dob(data['dob'])
            personal_page.fill_address("123 Main St")
            personal_page.fill_city("New York")
            personal_page.fill_state("NY")
            personal_page.fill_zip(data['zip'])
        
        with allure.step("Submit form"):
            initial_url = smart_actions.page.url
            personal_page.proceed_to_next()
            smart_actions.page.wait_for_timeout(1000)
            
            assert smart_actions.page.url != initial_url, "Should proceed to next page with valid data"
            allure.attach(smart_actions.page.screenshot(full_page=True), 
                         name="successful_submission", 
                         attachment_type=allure.attachment_type.PNG)
