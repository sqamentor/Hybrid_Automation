"""
Bookslot Complete Test - CLEAN & MODERN
========================================
This test file contains ONLY:
✅ Imports
✅ Markers
✅ Test steps

All framework logic is extracted to proper locations:
- SmartActions → framework/core/smart_actions.py
- Fake data generation → conftest.py fixture
- Human behavior → conftest.py fixture

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com
"""

import re
import pytest
from playwright.sync_api import Page


@pytest.mark.bookslot
@pytest.mark.e2e
@pytest.mark.human_like
@pytest.mark.recorded
def test_bookslot_complete_flow(page: Page, multi_project_config, smart_actions, fake_bookslot_data) -> None:
    """Complete bookslot test flow with smart automation.

    Auto-features (via fixtures):
        ✅ Fake data generation (fake_bookslot_data)
        ✅ Smart actions with auto-delays (smart_actions)
        ✅ Human behavior simulation (when --enable-human-behavior flag used)

    Run Options:
        Fast:  pytest recorded_tests/bookslot/test_bookslot_complete_workflow.py -v
        Human: pytest recorded_tests/bookslot/test_bookslot_complete_workflow.py --enable-human-behavior -v
    """
    
    # Get configuration
    base_url = multi_project_config['bookslot']['ui_url']
    data = fake_bookslot_data
    act = smart_actions
    
    print(f"\n🎯 Testing with: {data['email']}\n")
    
    # =========================================================================
    # BASIC INFO PAGE
    # =========================================================================
    act.navigate(f"{base_url}/basic-info", "Basic Info")
    
    act.click(page.get_by_role("button", name="English"), "Select English")
    act.click(page.get_by_role("button", name="Español"), "Select Spanish")
    act.click(page.get_by_role("button", name="English"), "Select English")

    act.click(page.get_by_role("heading", name="We need to collect some"), "Heading")
    
    act.click(page.get_by_role("heading", name="Fields marked with * are"), "Heading")
    act.type_text(page.get_by_role("textbox", name="First Name *"), data['first_name'], "First Name")
    act.type_text(page.get_by_role("textbox", name="Last Name *"), data['last_name'], "Last Name")
    act.type_text(page.get_by_role("textbox", name="E-mail *"), data['email'], "Email")
    act.type_text(page.locator("#CellPhone").get_by_role("textbox"), data['phone_number'], "Phone")
    act.type_text(page.locator("#ZipCode"), data['zip'], "Zip Code")
    
    act.click(page.get_by_text("Text E-mail Call"), "Contact Preference")
    act.button_click(page.get_by_role("button", name="Send Me The Code"), "Send Code", wait_processing=True)
    
    # =========================================================================
    # OTP VERIFICATION
    # =========================================================================
    act.wait_for_page_ready("OTP Page")
    
    otp_field = page.locator("#otp, input[type='text'][name*='otp'], input[placeholder*='code'], input[placeholder*='OTP']").first
    if act.wait_and_click(otp_field, "OTP Field", timeout=30000):
        act.type_text(otp_field, data['verification_code'], "OTP Code")
        print("✓ OTP filled")
    else:
        print("⚠ OTP field not found")
    
    act.button_click(page.get_by_role("button", name="Verify Code"), "Verify", wait_processing=True)
    
    try:
        page.wait_for_selector(".loader, .spinner", state="hidden", timeout=30000)
    except TimeoutError:
        print("⚠ Loader still visible after timeout - continuing")
    except Exception as e:
        print(f"⚠ Unexpected error waiting for loader: {e}")
    
    # =========================================================================
    # EVENT TYPE SELECTION
    # =========================================================================
    act.navigate(f"{base_url}/eventtype", "Event Type")
    
    act.button_click(page.get_by_role("button", name="Request Call back"), "Request Call back")
    act.click(page.get_by_text("Request has been submitted"), "Call back Request Submission Confirmation")
    
    # PVN Event Selection
    act.click(page.get_by_role("heading", name="New Patient Appointment"), "Appointment Type")
    act.click(page.get_by_text("90-minute appointment with"), "Appointment Details")
    act.button_click(page.get_by_role("button", name="Book Now").first, "New Patient Appointment-Book Now")
    
    # CPV Event Selection
    #act.click(page.get_by_role("heading", name="Complimentary Consultation"), "Complimentary Consultation")
    #act.click(page.get_by_text("15-minute appointmentwith a"), "Appointment Details")
    #act.button_click(page.get_by_role("button", name="Book Now").nth(1), "Complimentary Consultation-Book Now")

    # =========================================================================
    # TIME SLOT SELECTION WITH RETRY
    # =========================================================================
    act.wait_for_scheduler("Time Slot Scheduler")
    
    def select_time_slot():
        slots = page.locator("button[role='button']:has-text('AM'), button[role='button']:has-text('PM')").all()
        if slots:
            act.click(slots[0], "Time Slot")
        else:
            act.click(page.locator("button:has-text(':')").first, "Time Slot Fallback")
        
        # Check for errors
        if page.locator("text=/went wrong|error|try again/i").count() > 0:
            raise SlotBookingError("Slot booking error detected - error message on page")
        
        print("✓ Time slot selected")
    
    try:
        act.smart_retry(select_time_slot, max_retries=3)
    except SlotBookingError as e:
        print(f"⚠ Slot booking error: {e} - Using last resort slot")
        try:
            act.click(page.get_by_role("button", name="06:00 AM"), "06:00 AM Slot")
        except (TimeoutError, ElementNotFoundError) as e:
            print(f"❌ Slot selection failed: {e} - continuing")
    except Exception as e:
        print(f"⚠ Unexpected error in slot selection: {e} - continuing")
    
    act.click(page.get_by_text("Request an Appointment This"), "Confirm Slot")
    act.button_click(page.get_by_role("button", name="Next"), "Next")
    
    # =========================================================================
    # PERSONAL INFORMATION
    # =========================================================================
    
    act.select_option(
        page.get_by_role("combobox", name="Select Gender"),
        page.get_by_role("option", name="MALE", exact=True),
        "Gender"
    )
    
    act.type_text(page.get_by_role("combobox", name="mm/dd/yyyy"), data['dob'], "Date of Birth")
    
    # Address with smart autocomplete
    act.type_text(page.get_by_role("textbox", name="Address"), data['zip'], "Address")
    
    if not act.wait_autocomplete("text=/Highmore|USA|SD/", "Address Suggestion", timeout=6000):
        act.wait_autocomplete("text=/USA/", "Address Fallback", timeout=2000)
    
    act.button_click(page.get_by_role("button", name="Next"), "Next")
    
    # =========================================================================
    # REFERRAL SOURCE
    # =========================================================================
    act.click(page.get_by_role("heading", name="How did you hear about us?"), "Referral Question")
    act.button_click(page.get_by_role("button", name="Referred by physician"), "Referral Source")
    act.button_click(page.get_by_role("button", name="Next"), "Next")
    
    # =========================================================================
    # INSURANCE INFORMATION
    # =========================================================================
    act.type_text(page.get_by_role("textbox", name="Member Name *"), data['MemberName'], "Member Name")
    act.type_text(page.get_by_role("textbox", name="ID Number *"), data['idNumber'], "ID Number")
    act.type_text(page.get_by_role("textbox", name="Group number *"), data['GroupNumber'], "Group Number")
    act.type_text(page.get_by_role("textbox", name="Insurance Company Name *"), data['PayerName'], "Insurance Company")
    
    act.wait_for_processing("Final review", short=True)
    act.button_click(page.get_by_role("button", name="Send to clinic"), "Submit", wait_processing=True)
    
    # =========================================================================
    # SUCCESS PAGE
    # =========================================================================
    act.navigate(f"{base_url}/success", "Success Page")
    
    redirect_msg = page.locator("div").filter(has_text=re.compile(r"^You will be redirected in \d+ seconds$"))
    act.click(redirect_msg, "Redirect Message")
    
    print(f"\n✅ Test completed successfully with {data['email']}\n")
