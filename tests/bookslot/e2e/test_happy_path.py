"""
E2E: Happy Path Test (Critical)

Complete booking journey with valid data:
P1 (Basic Info) → P2 (Event Type) → P3 (Scheduler) → P4 (Personal Info) → 
P5 (Referral) → P6 (Insurance) → P7 (Success)

This is the most critical test - if this fails, entire flow is broken.

Markers:
- @pytest.mark.e2e
- @pytest.mark.critical
- @pytest.mark.ui_sequential
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.bookslot
@pytest.mark.e2e
@pytest.mark.critical
@pytest.mark.ui_sequential
def test_complete_booking_happy_path(
    page: Page,
    bookslot_nav,
    valid_basic_info,
    valid_personal_info,
    valid_insurance_info,
    validation_helper
):
    """
    E2E: Complete booking flow with all valid data (Happy Path).
    
    Steps:
    1. Navigate to Basic Info (P1)
    2. Complete Basic Info → Event Type (P2)
    3. Complete Event Type → Scheduler (P3)
    4. Complete Scheduler → Personal Info (P4)
    5. Complete Personal Info → Referral (P5)
    6. Complete Referral → Insurance (P6)
    7. Complete Insurance → Success (P7)
    8. Verify Success page shows confirmation
    
    Expected Result: Booking completed successfully with confirmation number
    """
    
    # ========================================================================
    # P1: Basic Info
    # ========================================================================
    bookslot_nav.navigate_to_basic_info()
    
    page.fill("[name='firstName']", valid_basic_info["first_name"])
    page.fill("[name='lastName']", valid_basic_info["last_name"])
    page.fill("[name='email']", valid_basic_info["email"])
    page.fill("[name='phone']", valid_basic_info["phone"])
    
    page.click("button:has-text('Next')")
    page.wait_for_load_state("networkidle")
    
    # Verify at P2
    validation_helper.validate_navigation_to("Event Type")
    
    # ========================================================================
    # P2: Event Type
    # ========================================================================
    page.click("[data-testid='event-type-option']:first-child")
    page.click("button:has-text('Next')")
    page.wait_for_load_state("networkidle")
    
    # Verify at P3
    validation_helper.validate_navigation_to("Scheduler")
    
    # ========================================================================
    # P3: Scheduler
    # ========================================================================
    page.wait_for_selector("[data-testid='time-slot']", timeout=10000)
    page.click("[data-testid='time-slot']:not([disabled]):first-child")
    page.click("button:has-text('Next')")
    page.wait_for_load_state("networkidle")
    
    # Verify at P4
    validation_helper.validate_navigation_to("Personal Info")
    
    # ========================================================================
    # P4: Personal Info
    # ========================================================================
    page.fill("[name='dob']", valid_personal_info["dob"])
    page.fill("[name='address']", valid_personal_info["address"])
    page.fill("[name='city']", valid_personal_info["city"])
    page.select_option("[name='state']", valid_personal_info["state"])
    page.fill("[name='zip']", valid_personal_info["zip"])
    
    page.click("button:has-text('Next')")
    page.wait_for_load_state("networkidle")
    
    # Verify at P5
    validation_helper.validate_navigation_to("Referral")
    
    # ========================================================================
    # P5: Referral
    # ========================================================================
    page.click("[data-testid='referral-source-web']")
    page.click("button:has-text('Next')")
    page.wait_for_load_state("networkidle")
    
    # Verify at P6
    validation_helper.validate_navigation_to("Insurance")
    
    # ========================================================================
    # P6: Insurance
    # ========================================================================
    page.fill("[name='memberId']", valid_insurance_info["member_id"])
    page.fill("[name='groupNumber']", valid_insurance_info["group_number"])
    page.fill("[name='payer']", valid_insurance_info["payer"])
    
    page.click("button:has-text('Submit')")
    page.wait_for_load_state("networkidle")
    
    # Verify at P7
    validation_helper.validate_navigation_to("Success")
    
    # ========================================================================
    # P7: Success - Verify Confirmation
    # ========================================================================
    
    # Verify success message
    validation_helper.validate_text_present("Thank you")
    validation_helper.validate_text_present("Confirmation")
    
    # Verify confirmation number is displayed
    confirmation_number = page.locator("[data-testid='confirmation-number']")
    expect(confirmation_number).to_be_visible()
    
    # Verify key booking details are shown
    validation_helper.validate_text_present(valid_basic_info["first_name"])
    validation_helper.validate_text_present(valid_basic_info["email"])
    
    # Log success
    print(f"✅ E2E Happy Path completed successfully")
    print(f"   Confirmation visible for: {valid_basic_info['first_name']} {valid_basic_info['last_name']}")


@pytest.mark.bookslot
@pytest.mark.e2e
@pytest.mark.high
@pytest.mark.ui_sequential
@pytest.mark.parametrize("time_preference", ["AM", "PM"])
def test_complete_booking_with_time_preference(
    page: Page,
    bookslot_nav,
    valid_basic_info,
    valid_personal_info,
    valid_insurance_info,
    validation_helper,
    time_preference
):
    """
    E2E: Complete booking with specific time preference (AM or PM).
    
    This test validates that both AM and PM slots work end-to-end.
    """
    
    # P1: Basic Info
    bookslot_nav.navigate_to_basic_info()
    page.fill("[name='firstName']", valid_basic_info["first_name"])
    page.fill("[name='lastName']", valid_basic_info["last_name"])
    page.fill("[name='email']", valid_basic_info["email"])
    page.fill("[name='phone']", valid_basic_info["phone"])
    page.click("button:has-text('Next')")
    page.wait_for_load_state("networkidle")
    
    # P2: Event Type
    page.click("[data-testid='event-type-option']:first-child")
    page.click("button:has-text('Next')")
    page.wait_for_load_state("networkidle")
    
    # P3: Scheduler - Select based on time preference
    page.wait_for_selector("[data-testid='time-slot']", timeout=10000)
    
    # Filter by time preference
    page.click(f"[data-testid='filter-{time_preference.lower()}']")
    
    # Select first available slot
    page.click(f"[data-testid='time-slot-{time_preference.lower()}']:not([disabled]):first-child")
    page.click("button:has-text('Next')")
    page.wait_for_load_state("networkidle")
    
    # P4: Personal Info
    page.fill("[name='dob']", valid_personal_info["dob"])
    page.fill("[name='address']", valid_personal_info["address"])
    page.fill("[name='city']", valid_personal_info["city"])
    page.select_option("[name='state']", valid_personal_info["state"])
    page.fill("[name='zip']", valid_personal_info["zip"])
    page.click("button:has-text('Next')")
    page.wait_for_load_state("networkidle")
    
    # P5: Referral
    page.click("[data-testid='referral-source-web']")
    page.click("button:has-text('Next')")
    page.wait_for_load_state("networkidle")
    
    # P6: Insurance
    page.fill("[name='memberId']", valid_insurance_info["member_id"])
    page.fill("[name='groupNumber']", valid_insurance_info["group_number"])
    page.fill("[name='payer']", valid_insurance_info["payer"])
    page.click("button:has-text('Submit')")
    page.wait_for_load_state("networkidle")
    
    # P7: Success
    validation_helper.validate_navigation_to("Success")
    validation_helper.validate_text_present("Thank you")
    
    print(f"✅ E2E {time_preference} slot booking completed successfully")


@pytest.mark.bookslot
@pytest.mark.e2e
@pytest.mark.medium
@pytest.mark.ui_sequential
def test_booking_with_back_navigation(
    page: Page,
    bookslot_nav,
    valid_basic_info,
    validation_helper
):
    """
    E2E: Test back navigation throughout the flow.
    
    Validates that users can go back and change their selections.
    """
    
    # Complete P1
    bookslot_nav.navigate_to_basic_info()
    page.fill("[name='firstName']", valid_basic_info["first_name"])
    page.fill("[name='lastName']", valid_basic_info["last_name"])
    page.fill("[name='email']", valid_basic_info["email"])
    page.fill("[name='phone']", valid_basic_info["phone"])
    page.click("button:has-text('Next')")
    page.wait_for_load_state("networkidle")
    
    # At P2 - Go back to P1
    page.click("button:has-text('Back')")
    page.wait_for_load_state("networkidle")
    validation_helper.validate_navigation_to("Basic Info")
    
    # Verify data persisted
    assert page.input_value("[name='firstName']") == valid_basic_info["first_name"]
    
    # Go forward again
    page.click("button:has-text('Next')")
    page.wait_for_load_state("networkidle")
    
    # Complete P2
    page.click("[data-testid='event-type-option']:first-child")
    page.click("button:has-text('Next')")
    page.wait_for_load_state("networkidle")
    
    # At P3 - Go back to P2
    page.click("button:has-text('Back')")
    page.wait_for_load_state("networkidle")
    validation_helper.validate_navigation_to("Event Type")
    
    print("✅ E2E back navigation test completed successfully")
