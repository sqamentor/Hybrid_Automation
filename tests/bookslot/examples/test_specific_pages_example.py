"""
Example: Testing Specific Pages in Isolation
============================================
Demonstrates how to test insurance page, personal info page, or any intermediate page.

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

Key Concept:
- Use navigation helper to reach target page
- Then test only that page's functionality
- No need to repeat navigation code

Run Commands:
    # Test only insurance page scenarios
    pytest tests/bookslot/examples/test_specific_pages_example.py::TestInsurancePageOnly -v
    
    # Test only personal info page scenarios
    pytest tests/bookslot/examples/test_specific_pages_example.py::TestPersonalInfoPageOnly -v
"""

import pytest
import allure
from playwright.sync_api import Page
from tests.bookslot.helpers.navigation_helper import BookslotNavigator, quick_navigate_to_insurance


@allure.epic("Bookslot")
@allure.feature("Insurance Page Testing")
@pytest.mark.bookslot
class TestInsurancePageOnly:
    """
    Example: Test ONLY the insurance page
    
    Uses navigation helper to reach insurance page, then tests insurance-specific functionality
    """
    
    @allure.story("Insurance Field Validation")
    @allure.title("Test insurance member name accepts valid input")
    @pytest.mark.validation
    def test_insurance_member_name_valid(
        self, page: Page, smart_actions, fake_bookslot_data
    ):
        """
        Scenario: Test insurance member name field accepts valid names
        """
        # Navigate to insurance page (all previous steps handled by navigator)
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
        navigator.navigate_to_insurance()
        
        # NOW you're at insurance page - test your scenarios
        with allure.step("Test member name field"):
            smart_actions.type_text(
                page.get_by_role("textbox", name="Member Name *"), 
                "John Smith", 
                "Member Name"
            )
            
            # Verify field accepts input
            member_value = page.get_by_role("textbox", name="Member Name *").input_value()
            assert member_value == "John Smith"
            
            allure.attach(
                page.screenshot(full_page=True), 
                name="insurance_member_name", 
                attachment_type=allure.attachment_type.PNG
            )
    
    @allure.story("Insurance ID Validation")
    @allure.title("Test insurance ID with various formats")
    @pytest.mark.validation
    @pytest.mark.parametrize("id_format,should_accept", [
        ("ABC123456", True),
        ("123456789", True),
        ("MEM-12345-XYZ", True),
        ("12", False),  # Too short
        ("", False),    # Empty
    ], ids=["alphanumeric", "numeric", "formatted", "too_short", "empty"])
    def test_insurance_id_formats(
        self, page: Page, smart_actions, fake_bookslot_data, id_format, should_accept
    ):
        """
        Scenario: Test insurance ID field with various formats
        """
        # Quick navigation to insurance page
        page = quick_navigate_to_insurance(smart_actions, fake_bookslot_data)
        
        with allure.step(f"Test ID format: {id_format}"):
            smart_actions.type_text(
                page.get_by_role("textbox", name="Member Name *"), 
                "Test Member", 
                "Member"
            )
            smart_actions.type_text(
                page.get_by_role("textbox", name="ID Number *"), 
                id_format, 
                "ID"
            )
            smart_actions.type_text(
                page.get_by_role("textbox", name="Payer Name *"), 
                "Aetna", 
                "Payer"
            )
            
            initial_url = page.url
            smart_actions.button_click(page.get_by_role("button", name="Next"), "Next")
            page.wait_for_timeout(800)
            
            if should_accept:
                assert page.url != initial_url, f"Should accept ID format: {id_format}"
            else:
                assert page.url == initial_url, f"Should reject ID format: {id_format}"
    
    @allure.story("Insurance Payer Selection")
    @allure.title("Test multiple insurance payers")
    @pytest.mark.regression
    @pytest.mark.parametrize("payer_name", [
        "Aetna",
        "Blue Cross Blue Shield",
        "Cigna",
        "UnitedHealthcare",
        "Medicare",
        "Custom Insurance Co."
    ])
    def test_insurance_payer_options(
        self, page: Page, smart_actions, fake_bookslot_data, payer_name
    ):
        """
        Scenario: Test insurance page accepts various payer names
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
        navigator.navigate_to_insurance()
        
        with allure.step(f"Test payer: {payer_name}"):
            smart_actions.type_text(
                page.get_by_role("textbox", name="Member Name *"), 
                fake_bookslot_data['MemberName'], 
                "Member"
            )
            smart_actions.type_text(
                page.get_by_role("textbox", name="ID Number *"), 
                "123456789", 
                "ID"
            )
            smart_actions.type_text(
                page.get_by_role("textbox", name="Payer Name *"), 
                payer_name, 
                "Payer"
            )
            
            initial_url = page.url
            smart_actions.button_click(page.get_by_role("button", name="Next"), "Next")
            page.wait_for_timeout(1000)
            
            assert page.url != initial_url, f"Should accept payer: {payer_name}"
    
    @allure.story("Group Number Optional")
    @allure.title("Test group number can be empty or filled")
    @pytest.mark.validation
    def test_group_number_optional(
        self, page: Page, smart_actions, fake_bookslot_data
    ):
        """
        Scenario: Verify group number is truly optional
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
        navigator.navigate_to_insurance()
        
        with allure.step("Submit without group number"):
            smart_actions.type_text(
                page.get_by_role("textbox", name="Member Name *"), 
                "Test Member", 
                "Member"
            )
            smart_actions.type_text(
                page.get_by_role("textbox", name="ID Number *"), 
                "987654321", 
                "ID"
            )
            # Skip group number intentionally
            smart_actions.type_text(
                page.get_by_role("textbox", name="Payer Name *"), 
                "Aetna", 
                "Payer"
            )
            
            initial_url = page.url
            smart_actions.button_click(page.get_by_role("button", name="Next"), "Next")
            page.wait_for_timeout(1000)
            
            assert page.url != initial_url, "Should proceed without group number"


@allure.epic("Bookslot")
@allure.feature("Personal Info Page Testing")
@pytest.mark.bookslot
class TestPersonalInfoPageOnly:
    """
    Example: Test ONLY the personal info page
    
    Uses navigation helper to reach personal info page, then tests personal info fields
    """
    
    @allure.story("Address Validation")
    @allure.title("Test address field accepts valid input")
    @pytest.mark.validation
    def test_personal_info_address_field(
        self, page: Page, smart_actions, fake_bookslot_data
    ):
        """
        Scenario: Test address field on personal info page
        """
        # Navigate to personal info page
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
        navigator.navigate_to_personal_info()
        
        with allure.step("Test address field"):
            test_addresses = [
                "123 Main Street",
                "456 Oak Avenue Apt 2B",
                "789 Elm St, Unit 5",
                "P.O. Box 12345"
            ]
            
            for address in test_addresses:
                page.get_by_role("textbox", name="Address *").clear()
                smart_actions.type_text(
                    page.get_by_role("textbox", name="Address *"), 
                    address, 
                    "Address"
                )
                
                value = page.get_by_role("textbox", name="Address *").input_value()
                assert value == address, f"Address field should accept: {address}"
    
    @allure.story("Zip Code Validation")
    @allure.title("Test zip code format validation")
    @pytest.mark.validation
    @pytest.mark.parametrize("zip_code,is_valid", [
        ("12345", True),
        ("12345-6789", True),
        ("90210", True),
        ("123", False),
        ("ABCDE", False),
        ("123456", False),
    ])
    def test_personal_info_zip_validation(
        self, page: Page, smart_actions, fake_bookslot_data, zip_code, is_valid
    ):
        """
        Scenario: Test zip code validation on personal info page
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
        navigator.navigate_to_personal_info()
        
        with allure.step(f"Test zip code: {zip_code}"):
            smart_actions.type_text(
                page.get_by_role("textbox", name="Date of Birth *"), 
                fake_bookslot_data['dob'], 
                "DOB"
            )
            smart_actions.type_text(
                page.get_by_role("textbox", name="Address *"), 
                "123 Test St", 
                "Address"
            )
            smart_actions.type_text(
                page.get_by_role("textbox", name="City *"), 
                "Test City", 
                "City"
            )
            smart_actions.type_text(
                page.get_by_role("textbox", name="State *"), 
                "NY", 
                "State"
            )
            smart_actions.type_text(
                page.get_by_role("textbox", name="Zip Code *"), 
                zip_code, 
                "Zip"
            )
            
            initial_url = page.url
            smart_actions.button_click(page.get_by_role("button", name="Next"), "Next")
            page.wait_for_timeout(800)
            
            if is_valid:
                assert page.url != initial_url, f"Valid zip {zip_code} should allow progression"
            else:
                assert page.url == initial_url, f"Invalid zip {zip_code} should prevent progression"
    
    @allure.story("Date of Birth Validation")
    @allure.title("Test DOB field with various formats")
    @pytest.mark.validation
    def test_personal_info_dob_field(
        self, page: Page, smart_actions, fake_bookslot_data
    ):
        """
        Scenario: Test DOB field accepts valid dates
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
        navigator.navigate_to_personal_info()
        
        with allure.step("Test DOB field"):
            dob_field = page.get_by_role("textbox", name="Date of Birth *")
            
            # Test valid DOB
            smart_actions.type_text(dob_field, "01/15/1990", "DOB")
            
            value = dob_field.input_value()
            assert "1990" in value, "DOB should accept valid date"
            
            allure.attach(
                page.screenshot(full_page=True), 
                name="personal_info_dob", 
                attachment_type=allure.attachment_type.PNG
            )


@allure.epic("Bookslot")
@allure.feature("Referral Page Testing")
@pytest.mark.bookslot
class TestReferralPageOnly:
    """
    Example: Test ONLY the referral page
    """
    
    @allure.story("Referral Source Selection")
    @allure.title("Test all referral source options")
    @pytest.mark.regression
    @pytest.mark.parametrize("referral_option", [
        "Referred by physician",
        "Online search",
        "Social media",
        "Friend or family",
        "Advertisement"
    ])
    def test_referral_source_options(
        self, page: Page, smart_actions, fake_bookslot_data, referral_option
    ):
        """
        Scenario: Test each referral source option is selectable
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
        navigator.navigate_to_referral()
        
        with allure.step(f"Select referral source: {referral_option}"):
            page.get_by_role("radio", name=referral_option).click()
            
            # Verify selection
            is_checked = page.get_by_role("radio", name=referral_option).is_checked()
            assert is_checked, f"Should be able to select: {referral_option}"
            
            # Verify can proceed
            initial_url = page.url
            smart_actions.button_click(page.get_by_role("button", name="Next"), "Next")
            page.wait_for_timeout(800)
            
            assert page.url != initial_url, f"Should proceed with: {referral_option}"


# ============================================================================
# USAGE SUMMARY
# ============================================================================

"""
HOW TO TEST SPECIFIC PAGES:
============================

1. For Insurance Page:
   -----------------
   navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
   navigator.navigate_to_insurance()
   # Now test insurance page scenarios
   
   OR use quick function:
   page = quick_navigate_to_insurance(smart_actions, fake_bookslot_data)

2. For Personal Info Page:
   ----------------------
   navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
   navigator.navigate_to_personal_info()
   # Now test personal info page scenarios

3. For Referral Page:
   -----------------
   navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
   navigator.navigate_to_referral()
   # Now test referral page scenarios

4. For Any Page:
   ------------
   navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
   
   # Choose the method matching your target page:
   navigator.navigate_to_basic_info()      # Entry point
   navigator.navigate_to_event_type()      # After basic info
   navigator.navigate_to_scheduler()       # After event type
   navigator.navigate_to_personal_info()   # After scheduler
   navigator.navigate_to_referral()        # After personal info
   navigator.navigate_to_insurance()       # After referral
   navigator.navigate_to_success()         # Complete flow

BENEFITS:
=========
✅ No code duplication - navigation logic in one place
✅ Test specific pages without repeating setup
✅ Easy to maintain - update navigation in one file
✅ Flexible - customize event type, time slot, etc.
✅ Clean tests - focus on what you're testing, not navigation
"""
