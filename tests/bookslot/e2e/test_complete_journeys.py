"""
Comprehensive E2E Tests for Bookslot (Layer B)

Full journey tests (P1→P2→P3→P4→P5→P6→P7) for critical business scenarios.

Test Coverage:
- Happy path (successful booking with valid data)
- AM slot booking
- PM slot booking
- Different referral sources
- Different insurance providers
- Edge cases and variants

Markers:
- @pytest.mark.e2e
- @pytest.mark.ui_sequential (must run serially)
- @pytest.mark.critical, high
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.bookslot
@pytest.mark.e2e
@pytest.mark.ui_sequential
@pytest.mark.critical
class TestE2EHappyPath:
    """Critical E2E journey tests (must pass for release)"""
    
    def test_complete_booking_happy_path_am_slot(
        self, 
        page: Page, 
        navigation_helper, 
        valid_basic_info,
        valid_personal_info,
        valid_insurance_info
    ):
        """E2E: Complete booking flow with AM slot - HAPPY PATH"""
        # P1: Basic Info
        navigation_helper.navigate_to_basic_info()
        page.fill("[name='name']", valid_basic_info["name"])
        page.fill("[name='email']", valid_basic_info["email"])
        page.fill("[name='phone']", valid_basic_info["phone"])
        page.click("button:has-text('Next')")
        
        # P2: Event Type
        expect(page).to_have_url(page.url + "/event-type", timeout=10000)
        page.click("[data-testid='event-type-option']:first-child")
        page.click("button:has-text('Next')")
        
        # P3: Scheduler - Select AM slot
        expect(page).to_have_url(page.url + "/scheduler", timeout=10000)
        page.click("[data-testid='am-filter']")  # Filter AM slots
        page.click("[data-testid='time-slot']:first-child")
        page.click("button:has-text('Next')")
        
        # P4: Personal Info
        expect(page).to_have_url(page.url + "/personal-info", timeout=10000)
        page.fill("[name='firstName']", valid_personal_info["first_name"])
        page.fill("[name='lastName']", valid_personal_info["last_name"])
        page.fill("[name='dateOfBirth']", valid_personal_info["dob"])
        page.fill("[name='address']", valid_personal_info["address"])
        page.fill("[name='city']", valid_personal_info["city"])
        page.select_option("[name='state']", valid_personal_info["state"])
        page.fill("[name='zipCode']", valid_personal_info["zip_code"])
        page.click("button:has-text('Next')")
        
        # P5: Referral
        expect(page).to_have_url(page.url + "/referral", timeout=10000)
        page.click("[data-testid='referral-source-doctor']")
        page.click("button:has-text('Next')")
        
        # P6: Insurance
        expect(page).to_have_url(page.url + "/insurance", timeout=10000)
        page.fill("[name='memberId']", valid_insurance_info["member_id"])
        page.fill("[name='groupNumber']", valid_insurance_info["group_number"])
        page.fill("[name='payer']", valid_insurance_info["payer"])
        page.click("button:has-text('Submit')")
        
        # P7: Success
        expect(page).to_have_url(page.url + "/success", timeout=15000)
        expect(page.locator("[data-testid='confirmation-number']")).to_be_visible()
        
        # Verify confirmation number is not empty
        conf_number = page.locator("[data-testid='confirmation-number']").inner_text()
        assert len(conf_number) > 0, "Confirmation number is empty"
    
    def test_complete_booking_happy_path_pm_slot(
        self, 
        page: Page, 
        navigation_helper, 
        valid_basic_info,
        valid_personal_info,
        valid_insurance_info
    ):
        """E2E: Complete booking flow with PM slot"""
        # P1: Basic Info
        navigation_helper.navigate_to_basic_info()
        page.fill("[name='name']", valid_basic_info["name"])
        page.fill("[name='email']", valid_basic_info["email"])
        page.fill("[name='phone']", valid_basic_info["phone"])
        page.click("button:has-text('Next')")
        
        # P2: Event Type
        page.click("[data-testid='event-type-option']:first-child")
        page.click("button:has-text('Next')")
        
        # P3: Scheduler - Select PM slot
        page.click("[data-testid='pm-filter']")  # Filter PM slots
        page.click("[data-testid='time-slot']:first-child")
        page.click("button:has-text('Next')")
        
        # P4: Personal Info
        page.fill("[name='firstName']", valid_personal_info["first_name"])
        page.fill("[name='lastName']", valid_personal_info["last_name"])
        page.fill("[name='dateOfBirth']", valid_personal_info["dob"])
        page.fill("[name='address']", valid_personal_info["address"])
        page.fill("[name='city']", valid_personal_info["city"])
        page.select_option("[name='state']", valid_personal_info["state"])
        page.fill("[name='zipCode']", valid_personal_info["zip_code"])
        page.click("button:has-text('Next')")
        
        # P5: Referral
        page.click("[data-testid='referral-source-online']")
        page.click("button:has-text('Next')")
        
        # P6: Insurance
        page.fill("[name='memberId']", valid_insurance_info["member_id"])
        page.fill("[name='groupNumber']", valid_insurance_info["group_number"])
        page.fill("[name='payer']", valid_insurance_info["payer"])
        page.click("button:has-text('Submit')")
        
        # P7: Success
        expect(page).to_have_url(page.url + "/success", timeout=15000)
        expect(page.locator("[data-testid='success-page']")).to_be_visible()


@pytest.mark.bookslot
@pytest.mark.e2e
@pytest.mark.ui_sequential
@pytest.mark.high
class TestE2EReferralVariants:
    """E2E tests for different referral sources"""
    
    def test_booking_with_referral_other(
        self, 
        page: Page, 
        navigation_helper, 
        valid_basic_info,
        valid_personal_info,
        valid_insurance_info
    ):
        """E2E: Complete booking with 'Other' referral source"""
        # Navigate through P1-P4 using helper
        navigation_helper.complete_basic_to_scheduler(valid_basic_info)
        navigation_helper.complete_scheduler_to_personal_info()
        navigation_helper.complete_personal_info_to_referral(valid_personal_info)
        
        # P5: Referral - Select "Other"
        page.click("[data-testid='referral-source-other']")
        page.fill("[name='referralOther']", "Friend recommendation")
        page.click("button:has-text('Next')")
        
        # P6: Insurance
        page.fill("[name='memberId']", valid_insurance_info["member_id"])
        page.fill("[name='groupNumber']", valid_insurance_info["group_number"])
        page.fill("[name='payer']", valid_insurance_info["payer"])
        page.click("button:has-text('Submit')")
        
        # P7: Success
        expect(page).to_have_url(page.url + "/success", timeout=15000)
    
    def test_booking_with_referral_insurance(
        self, 
        page: Page, 
        navigation_helper, 
        valid_basic_info,
        valid_personal_info,
        valid_insurance_info
    ):
        """E2E: Complete booking with 'Insurance Provider' referral"""
        # Navigate through P1-P4
        navigation_helper.complete_basic_to_scheduler(valid_basic_info)
        navigation_helper.complete_scheduler_to_personal_info()
        navigation_helper.complete_personal_info_to_referral(valid_personal_info)
        
        # P5: Referral - Select "Insurance"
        page.click("[data-testid='referral-source-insurance']")
        page.click("button:has-text('Next')")
        
        # P6: Insurance
        page.fill("[name='memberId']", valid_insurance_info["member_id"])
        page.fill("[name='groupNumber']", valid_insurance_info["group_number"])
        page.fill("[name='payer']", valid_insurance_info["payer"])
        page.click("button:has-text('Submit')")
        
        # P7: Success
        expect(page).to_have_url(page.url + "/success", timeout=15000)


@pytest.mark.bookslot
@pytest.mark.e2e
@pytest.mark.ui_sequential
@pytest.mark.high
class TestE2EInsuranceVariants:
    """E2E tests for different insurance providers"""
    
    @pytest.mark.parametrize("payer", [
        "Blue Cross Blue Shield",
        "Aetna",
        "UnitedHealthcare",
        "Cigna"
    ])
    def test_booking_with_different_payers(
        self, 
        page: Page, 
        navigation_helper, 
        valid_basic_info,
        valid_personal_info,
        payer: str
    ):
        """E2E: Complete booking with different insurance payers"""
        # Navigate through P1-P5 using helper
        navigation_helper.complete_basic_to_scheduler(valid_basic_info)
        navigation_helper.complete_scheduler_to_personal_info()
        navigation_helper.complete_personal_info_to_referral(valid_personal_info)
        navigation_helper.complete_referral_to_insurance()
        
        # P6: Insurance - Use specific payer
        page.fill("[name='memberId']", "TEST123456")
        page.fill("[name='groupNumber']", "GRP789")
        page.fill("[name='payer']", payer)
        page.click("button:has-text('Submit')")
        
        # P7: Success
        expect(page).to_have_url(page.url + "/success", timeout=15000)
        expect(page.locator("[data-testid='success-page']")).to_be_visible()


@pytest.mark.bookslot
@pytest.mark.e2e
@pytest.mark.ui_sequential
@pytest.mark.medium
class TestE2EEdgeCases:
    """E2E tests for edge cases and boundary conditions"""
    
    def test_booking_with_max_length_names(
        self, 
        page: Page, 
        navigation_helper, 
        valid_basic_info,
        valid_insurance_info
    ):
        """E2E: Complete booking with maximum length names"""
        # Navigate through P1-P3
        navigation_helper.complete_basic_to_scheduler(valid_basic_info)
        navigation_helper.complete_scheduler_to_personal_info()
        
        # P4: Personal Info - Use max length names
        max_first_name = "A" * 50
        max_last_name = "B" * 50
        
        page.fill("[name='firstName']", max_first_name)
        page.fill("[name='lastName']", max_last_name)
        page.fill("[name='dateOfBirth']", "1990-01-15")
        page.fill("[name='address']", "123 Main St")
        page.fill("[name='city']", "Boston")
        page.select_option("[name='state']", "MA")
        page.fill("[name='zipCode']", "02101")
        page.click("button:has-text('Next')")
        
        # Continue through P5-P7
        page.click("[data-testid='referral-source-online']")
        page.click("button:has-text('Next')")
        
        page.fill("[name='memberId']", valid_insurance_info["member_id"])
        page.fill("[name='groupNumber']", valid_insurance_info["group_number"])
        page.fill("[name='payer']", valid_insurance_info["payer"])
        page.click("button:has-text('Submit')")
        
        # P7: Success
        expect(page).to_have_url(page.url + "/success", timeout=15000)
    
    def test_booking_with_special_characters_in_names(
        self, 
        page: Page, 
        navigation_helper, 
        valid_basic_info,
        valid_insurance_info
    ):
        """E2E: Complete booking with special characters in names"""
        # Navigate through P1-P3
        navigation_helper.complete_basic_to_scheduler(valid_basic_info)
        navigation_helper.complete_scheduler_to_personal_info()
        
        # P4: Personal Info - Use names with special characters
        page.fill("[name='firstName']", "Mary-Jane")
        page.fill("[name='lastName']", "O'Brien")
        page.fill("[name='dateOfBirth']", "1985-05-20")
        page.fill("[name='address']", "456 Oak Ave")
        page.fill("[name='city']", "New York")
        page.select_option("[name='state']", "NY")
        page.fill("[name='zipCode']", "10001")
        page.click("button:has-text('Next')")
        
        # Continue through P5-P7
        page.click("[data-testid='referral-source-doctor']")
        page.click("button:has-text('Next')")
        
        page.fill("[name='memberId']", valid_insurance_info["member_id"])
        page.fill("[name='groupNumber']", valid_insurance_info["group_number"])
        page.fill("[name='payer']", valid_insurance_info["payer"])
        page.click("button:has-text('Submit')")
        
        # P7: Success
        expect(page).to_have_url(page.url + "/success", timeout=15000)


@pytest.mark.bookslot
@pytest.mark.e2e
@pytest.mark.ui_sequential
@pytest.mark.medium
class TestE2EBackNavigation:
    """E2E tests for back navigation behavior"""
    
    def test_back_navigation_preserves_data(
        self, 
        page: Page, 
        navigation_helper, 
        valid_basic_info,
        valid_personal_info
    ):
        """E2E: Back navigation preserves entered data"""
        # P1: Basic Info
        navigation_helper.navigate_to_basic_info()
        page.fill("[name='name']", valid_basic_info["name"])
        page.fill("[name='email']", valid_basic_info["email"])
        page.fill("[name='phone']", valid_basic_info["phone"])
        page.click("button:has-text('Next')")
        
        # P2: Event Type
        page.click("[data-testid='event-type-option']:first-child")
        page.click("button:has-text('Next')")
        
        # P3: Scheduler
        page.click("[data-testid='time-slot']:first-child")
        page.click("button:has-text('Next')")
        
        # P4: Personal Info
        page.fill("[name='firstName']", valid_personal_info["first_name"])
        page.fill("[name='lastName']", valid_personal_info["last_name"])
        
        # Go back to P3
        page.click("button:has-text('Back')")
        expect(page).to_have_url(page.url + "/scheduler", timeout=10000)
        
        # Go forward to P4 again
        page.click("button:has-text('Next')")
        expect(page).to_have_url(page.url + "/personal-info", timeout=10000)
        
        # Verify data preserved
        first_name = page.input_value("[name='firstName']")
        last_name = page.input_value("[name='lastName']")
        
        assert first_name == valid_personal_info["first_name"], "First name not preserved"
        assert last_name == valid_personal_info["last_name"], "Last name not preserved"
