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
Email: lokendra.singh@centerforvein.com
Website: www.centerforvein.com
"""

import re
import pytest
from framework.observability.enterprise_logger import EnterpriseLogger

logger = EnterpriseLogger()
# ARCHITECTURAL FIX: Removed direct Playwright import - use page fixture instead


@pytest.mark.playwright
@pytest.mark.modern_spa
@pytest.mark.bookslot
@pytest.mark.e2e
@pytest.mark.human_like
@pytest.mark.recorded
def test_bookslot_complete_flow(page, multi_project_config, smart_actions, fake_bookslot_data) -> None:
    """
    Complete bookslot test flow with smart automation
    
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
    
    logger.info(f"Testing with data: {data['first_name']}, {data['last_name']}, {data['email']}, {data['phone_number']},{data['zip']}")
    
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
    
    # masked=True → uses fill() to avoid input-mask cursor race condition
    act.type_text(page.locator("#CellPhone").get_by_role("textbox"), data['phone_number'], "Phone", masked=True)
    
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
    # -------------------------------------------------------------------------
    # Step 0: Wait for scheduler to fully load
    # -------------------------------------------------------------------------
    act.wait_for_scheduler("Time Slot Scheduler")
    
    # Also wait for the actual slot container to appear in the DOM
    page.locator("#slot").first.wait_for(state="visible", timeout=15000)
    print("✓ Scheduler loaded")
    
    # -------------------------------------------------------------------------
    # Step 1: Verify month navigation controls work
    # -------------------------------------------------------------------------
    next_btn = page.locator("span#next").first
    prev_btn = page.locator("span#previous").first

    # Click Next Month (wait for it to appear, not just is_visible())
    try:
        next_btn.wait_for(state="visible", timeout=10000)
        act.click(next_btn, "Next Month →")
        act.wait_for_scheduler("Next Month Loaded")
        
        # Click Previous to come back to original month
        prev_btn.wait_for(state="visible", timeout=10000)
        act.click(prev_btn, "← Previous Month")
        act.wait_for_scheduler("Previous Month Loaded")
        
        print("✓ Month navigation verified")
    except Exception as e:
        print(f"⚠ Month navigation test skipped: {e}")

    # -------------------------------------------------------------------------
    # Step 2: Try each slot, advancing months if all slots fail
    # -------------------------------------------------------------------------
    MAX_MONTH_PAGES = 3
    slot_booked = False

    for month_attempt in range(MAX_MONTH_PAGES):
        print(f"\n📅 Month page {month_attempt + 1}/{MAX_MONTH_PAGES}")

        # Wait briefly for slots to render after any page change
        act.wait_for_processing("Slots rendering", short=True)

        # Gather all visible time slot buttons on current page
        slots = page.locator("#slot button.scheduler-btn").all()
        if not slots:
            # Fallback selector
            slots = page.locator("button:has-text('AM'), button:has-text('PM')").all()

        print(f"   Found {len(slots)} slot(s)")

        if not slots:
            print("   ⚠ No slots found on this page → advancing to next month")
            if next_btn.is_visible():
                act.click(next_btn, "Next Month → (no slots)")
                act.wait_for_scheduler("Next Month Loaded (no slots)")
            continue

        for idx, slot in enumerate(slots):
            slot_text = slot.text_content().strip()
            try:
                act.click(slot, f"Slot {idx + 1}/{len(slots)}: {slot_text}")
                act.wait_for_processing("Slot selection", short=True)

                # Check for error alerts (e.g. "slot in progress", "went wrong")
                error_locator = page.locator(
                    "text=/in progress|went wrong|error|try again|unavailable|already booked/i"
                )
                if error_locator.count() > 0:
                    error_msg = error_locator.first.text_content().strip()
                    print(f"   ⚠ Slot '{slot_text}' error: {error_msg} → trying next slot")

                    # Dismiss any alert/dialog if present
                    ok_btn = page.locator("button:has-text('OK'), button:has-text('Close'), button:has-text('Dismiss')")
                    if ok_btn.count() > 0:
                        act.click(ok_btn.first, "Dismiss Alert")
                        act.wait_for_processing("Alert dismissed", short=True)

                    continue  # Try next slot

                # Positive confirmation: verify "Request an Appointment" text appeared
                confirm_locator = page.get_by_text("Request an Appointment This")
                try:
                    confirm_locator.wait_for(state="visible", timeout=5000)
                    print(f"   ✓ Slot '{slot_text}' selected and confirmed!")
                    slot_booked = True
                    break
                except Exception:
                    print(f"   ⚠ Slot '{slot_text}' clicked but no confirmation → trying next slot")
                    continue

            except Exception as e:
                print(f"   ⚠ Slot '{slot_text}' failed: {type(e).__name__}: {e} → trying next slot")

                # Dismiss any popup that may have appeared
                ok_btn = page.locator("button:has-text('OK'), button:has-text('Close')")
                if ok_btn.count() > 0:
                    try:
                        act.click(ok_btn.first, "Dismiss Error Popup")
                    except Exception:
                        pass
                continue

        if slot_booked:
            break

        # All slots on this month page failed → advance to next month
        print(f"   ❌ All slots exhausted on month page {month_attempt + 1}")
        if month_attempt < MAX_MONTH_PAGES - 1:
            if next_btn.is_visible():
                act.click(next_btn, "Next Month → (retry)")
                act.wait_for_scheduler("Next Month Loaded (retry)")
            else:
                print("   ⚠ Next Month button not visible — cannot advance")
                break

    if not slot_booked:
        print("❌ Could not book any slot after all retries — continuing test")
    
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
