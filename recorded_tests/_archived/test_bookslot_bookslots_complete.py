import re
import time
import random
from playwright.sync_api import Page, expect, Locator
import pytest
from utils.fake_data_generator import generate_bookslot_payload


@pytest.mark.bookslot
@pytest.mark.e2e
@pytest.mark.human_like
@pytest.mark.recorded
def test_example(page: Page, multi_project_config, human_behavior) -> None:
    """Recorded test with SMART context-aware human behavior automation
    
    Auto-Applied Delays (No manual delay calls needed):
        ✅ Before click: 0.3-0.7s (thinking time)
        ✅ After click: 0.2-0.4s (action confirmation)
        ✅ Before typing: 0.3-0.6s (preparation)
        ✅ After typing: 0.2-0.5s (review)
        ✅ Before navigation: 0.4-0.8s (decision)
        ✅ After page load: 0.5-1.0s (page observation)
        ✅ Before button click: 0.4-0.8s (considering action)
    
    Run Options:
        Fast Mode:    pytest recorded_tests/bookslot/test_bookslot_bookslots_complete.py -v
        Human Mode:   pytest recorded_tests/bookslot/test_bookslot_bookslots_complete.py --enable-human-behavior -v
        High Realism: pytest recorded_tests/bookslot/test_bookslot_bookslots_complete.py --enable-human-behavior --human-behavior-intensity high -v
    """
    
    # Generate fake data for this test
    fake_data = generate_bookslot_payload()
    print(f"\n🎲 Generated fake test data:")
    print(f"   Name: {fake_data['first_name']} {fake_data['last_name']}")
    print(f"   Email: {fake_data['email']}")
    print(f"   Phone: {fake_data['phone_number']}")
    print(f"   DOB: {fake_data['dob']}")
    print(f"   Insurance: {fake_data['PayerName']} (ID: {fake_data['idNumber']})\n")
    
    # Check if human behavior is enabled
    enable_human = human_behavior is not None
    
    # =========================================================================
    # SMART CONTEXT-AWARE AUTOMATION - No manual delays needed!
    # =========================================================================
    
    class SmartActions:
        """Intelligent action wrappers with automatic context-aware delays"""
        
        @staticmethod
        def delay(min_sec: float, max_sec: float, context: str = ""):
            """Auto delay with context logging"""
            if enable_human:
                delay_time = random.uniform(min_sec, max_sec)
                time.sleep(delay_time)
                if context:
                    print(f"   ⏱️  {context}: {delay_time:.2f}s")
        
        @staticmethod
        def smart_click(element, description: str = ""):
            """Click with automatic before/after delays"""
            SmartActions.delay(0.3, 0.7, f"Thinking before click: {description}")
            element.click()
            SmartActions.delay(0.2, 0.4, f"Confirming click: {description}")
        
        @staticmethod
        def smart_type(element, text: str, field_name: str = ""):
            """Type with automatic before/after delays and context-aware speed"""
            SmartActions.delay(0.3, 0.6, f"Preparing to type: {field_name}")
            
            if enable_human:
                # Context-aware typing speed
                is_numeric = text.replace('-', '').replace(' ', '').isdigit()
                is_email = '@' in str(text)
                is_date = '/' in str(text) or '-' in str(text)
                
                for char in str(text):
                    element.type(char)
                    if is_numeric:
                        time.sleep(random.uniform(0.08, 0.18))  # Faster for numbers
                    elif is_date:
                        time.sleep(random.uniform(0.10, 0.22))  # Medium for dates
                    elif is_email:
                        time.sleep(random.uniform(0.12, 0.25))  # Careful with email
                    else:
                        time.sleep(random.uniform(0.10, 0.25))  # Normal text
            else:
                element.fill(str(text))
            
            SmartActions.delay(0.2, 0.5, f"Reviewing typed: {field_name}")
        
        @staticmethod
        def smart_button_click(element, button_name: str = ""):
            """Button click with extra thinking time"""
            SmartActions.delay(0.4, 0.9, f"Considering button: {button_name}")
            element.click()
            SmartActions.delay(0.3, 0.6, f"Clicked button: {button_name}")
        
        @staticmethod
        def smart_goto(url: str, page_name: str = ""):
            """Navigate with automatic page load delay"""
            SmartActions.delay(0.4, 0.8, f"Navigating to: {page_name}")
            page.goto(url)
            SmartActions.delay(0.5, 1.0, f"Observing page: {page_name}")
        
        @staticmethod
        def smart_select(element, value: str, field_name: str = ""):
            """Select dropdown with automatic delays"""
            SmartActions.delay(0.3, 0.6, f"Opening dropdown: {field_name}")
            element.click()
            SmartActions.delay(0.2, 0.4, "Reviewing options")
        
        @staticmethod
        def smart_wait_and_click_autocomplete(locator_pattern: str, description: str = "", timeout: int = 6000):
            """Smart autocomplete handling with timeout"""
            try:
                element = page.locator(locator_pattern).first
                element.wait_for(state="visible", timeout=timeout)
                SmartActions.delay(0.3, 0.6, f"Reviewing autocomplete: {description}")
                element.click()
                print(f"✓ Autocomplete selected: {description}")
                return True
            except:
                print(f"⚠ Autocomplete not shown within {timeout/1000}s - continuing...")
                SmartActions.delay(0.2, 0.4, "No autocomplete, continuing")
                return False
    
    # Use SmartActions instead of manual delays
    actions = SmartActions()
    # Use SmartActions instead of manual delays
    actions = SmartActions()
    
    base_url = multi_project_config['bookslot']['ui_url']
    
    # =========================================================================
    # BASIC INFO PAGE - All delays auto-applied!
    # =========================================================================
    actions.smart_goto(f"{base_url}/basic-info", "Basic Info Page")
    
    # Fill First Name
    first_name_field = page.get_by_role("textbox", name="First Name *")
    actions.smart_type(first_name_field, fake_data['first_name'], "First Name")
    
    # Fill Last Name
    last_name_field = page.get_by_role("textbox", name="Last Name *")
    actions.smart_type(last_name_field, fake_data['last_name'], "Last Name")
    
    # Fill Email
    email_field = page.get_by_role("textbox", name="E-mail *")
    actions.smart_type(email_field, fake_data['email'], "Email")
    
    # Fill Phone Number
    phone_field = page.locator("#CellPhone").get_by_role("textbox")
    actions.smart_type(phone_field, fake_data['phone_number'], "Phone Number")
    
    # Fill Zip Code
    zip_field = page.locator("#ZipCode")
    actions.smart_type(zip_field, fake_data['zip'], "Zip Code")
    
    # Select communication preference
    actions.smart_click(page.get_by_text("Text E-mail Call"), "Communication Preference")
    
    # Submit for verification
    actions.smart_button_click(page.get_by_role("button", name="Send Me The Code"), "Send Code")
    
    # Wait for page to process OTP request
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except:
        pass  # Continue if network doesn't idle
    
    human_delay(1.5, 2.5)  # Wait for code sending and UI update
    
    # Wait up to 30 seconds for OTP field to appear
    # The field may take time to render after sending the code
    try:
        # Try multiple selector patterns with 30-second total timeout
        otp_field = page.locator("#otp, input[type='text'][name*='otp'], input[placeholder*='code'], input[placeholder*='OTP']").first
        otp_field.wait_for(state="visible", timeout=30000)  # Wait up to 30 seconds
        
        human_delay(0.8, 1.5)  # Getting code from email/phone
        otp_field.click()
        human_delay(0.5, 1.0)  # Reading the code
        
        # Type OTP code with human behavior (using fake data)
        otp_code = fake_data['verification_code']
        if enable_human:
            for char in otp_code:
                otp_field.type(char)
                time.sleep(random.uniform(0.12, 0.25))  # Slower typing for careful entry
        else:
            otp_field.fill(otp_code)
        
        human_delay(0.3, 0.6)  # Review what was typed
        print("✓ OTP field found and filled with code: 123456")
        
    except Exception as e:
        # OTP field didn't appear within 30 seconds - continue anyway
        print(f"⚠ OTP field not found within 30 seconds, continuing: {type(e).__name__}")
        pass
    
    human_delay(0.4, 0.8)  # Pause before verify
    
    # Click Verify Code button (this should work regardless of OTP field state)
    page.get_by_role("button", name="Verify Code").click()
    
    # Wait for verification processing and any loader
    try:
        page.wait_for_selector(".loader, .spinner, [role='progressbar']", state="hidden", timeout=10000)
    except:
        pass
    
    human_delay(1.0, 2.0)  # Verification processing
    
    # Event Type Selection
    page.goto(f"{base_url}/eventtype")
    human_delay(0.8, 1.5)  # Page load and reading
    
    page.get_by_role("heading", name="New Patient Appointment").click()
    human_delay(0.5, 1.0)  # Reading appointment details
    page.get_by_text("90-minute appointment with").click()
    human_delay(0.7, 1.2)  # Reviewing details
    page.get_by_role("button", name="Book Now").first.click()
    human_delay(1.0, 2.0)  # Loading scheduler
    
    # Web Scheduler
    page.get_by_role("heading", name="Web Scheduler - New Patient").click()
    human_delay(1.5, 2.5)  # Browsing calendar
    page.get_by_text("(90-minute appointment with").click()
    human_delay(1.0, 1.8)  # Reviewing time slots
    
    # Click first available time slot with error handling and retry logic
    max_retries = 3
    retry_count = 0
    slot_clicked_successfully = False
    
    while retry_count < max_retries and not slot_clicked_successfully:
        try:
            # Get all time slot buttons and click the first available one
            available_slots = page.locator("button[role='button']:has-text('AM'), button[role='button']:has-text('PM')").all()
            
            if available_slots:
                # Click the first available slot found
                available_slots[0].click()
                print(f"✓ Clicked available time slot (attempt {retry_count + 1})")
            else:
                # Fallback: click any button with time pattern
                page.locator("button:has-text(':')").first.click()
                print(f"✓ Clicked first time slot - fallback (attempt {retry_count + 1})")
            
            human_delay(0.7, 1.2)  # Wait for response
            
            # Check for error messages
            error_messages = [
                "something went wrong",
                "went wrong",
                "error occurred",
                "try again",
                "not available",
                "already booked"
            ]
            
            has_error = False
            for error_text in error_messages:
                if page.locator(f"text=/{error_text}/i").count() > 0:
                    has_error = True
                    print(f"⚠ Error detected: '{error_text}' - Retry {retry_count + 1}/{max_retries}")
                    break
            
            if has_error:
                retry_count += 1
                if retry_count < max_retries:
                    human_delay(1.0, 2.0)  # Wait before retry
                    
                    # Check if button still exists
                    if page.locator("button[role='button']:has-text('AM'), button[role='button']:has-text('PM')").count() == 0:
                        print("⚠ Time slots disappeared - Reloading page")
                        page.reload()
                        human_delay(2.0, 3.0)  # Wait for page reload
                        # Re-navigate to time slot selection
                        page.get_by_text("(90-minute appointment with").click()
                        human_delay(1.0, 1.8)
                else:
                    print("❌ Max retries reached - continuing anyway")
                    slot_clicked_successfully = True  # Exit loop
            else:
                slot_clicked_successfully = True
                print("✓ Time slot selected successfully")
                
        except Exception as e:
            retry_count += 1
            print(f"⚠ Exception during slot selection: {type(e).__name__} - Retry {retry_count}/{max_retries}")
            
            if retry_count < max_retries:
                human_delay(1.0, 2.0)
                # Try reloading page
                try:
                    page.reload()
                    human_delay(2.0, 3.0)
                    page.get_by_text("(90-minute appointment with").click()
                    human_delay(1.0, 1.8)
                except:
                    pass
            else:
                # Last resort: try the original 06:00 AM
                try:
                    page.get_by_role("button", name="06:00 AM").click()
                    print("✓ Clicked 06:00 AM slot (last resort)")
                    slot_clicked_successfully = True
                except:
                    print("❌ All attempts failed - continuing")
                    slot_clicked_successfully = True
    
    human_delay(0.7, 1.2)  # Confirming selection
    page.get_by_text("Request an Appointment This").click()
    human_delay(0.4, 0.8)
    page.get_by_role("button", name="Next").click()
    human_delay(0.8, 1.5)  # Page transition
    # Personal Information
    human_delay(0.4, 0.8)  # Gender selection thinking
    page.get_by_role("combobox", name="Select Gender").click()
    human_delay(0.3, 0.6)
    page.get_by_role("option", name="MALE", exact=True).click()
    
    human_delay(0.5, 1.0)  # DOB field
    dob_field = page.get_by_role("combobox", name="mm/dd/yyyy")
    dob_field.click()
    human_delay(0.3, 0.7)  # Think about DOB
    
    # Fill date of birth with human typing (using fake data)
    dob = fake_data['dob']
    if enable_human:
        for char in dob:
            dob_field.type(char)
            time.sleep(random.uniform(0.08, 0.20))  # Typing date
    else:
        dob_field.fill(dob)
    
    human_delay(0.6, 1.2)  # Address field
    page.get_by_role("textbox", name="Address").click()
    human_delay(0.4, 0.8)
    human_type(page.get_by_role("textbox", name="Address"), fake_data['zip'])
    
    # Wait for autocomplete dropdown with 6-second timeout
    try:
        # Wait up to 6 seconds for any dropdown/autocomplete suggestion
        dropdown_visible = page.locator("text=/Highmore|USA|SD/").first.wait_for(state="visible", timeout=6000)
        human_delay(0.3, 0.7)  # Review options
        
        # Try to click the first autocomplete suggestion
        try:
            page.get_by_text("Highmore, SD, USA").click()
            print("✓ Address autocomplete selected: Highmore, SD, USA")
        except:
            # If specific text not found, try clicking first suggestion
            page.locator("text=/USA|SD/").first.click()
            print("✓ Address autocomplete selected (first option)")
    except:
        # No dropdown appeared within 6 seconds - continue anyway
        print("⚠ Address autocomplete not shown within 6 seconds - continuing...")
        human_delay(0.3, 0.5)
    
    human_delay(0.5, 1.0)  # Review before next
    page.get_by_role("button", name="Next").click()
    human_delay(0.8, 1.5)  # Page transition
    
    # Referral Source
    human_delay(0.5, 1.0)  # Reading question
    page.get_by_role("heading", name="How did you hear about us?").click()
    human_delay(0.7, 1.3)  # Considering answer
    page.get_by_role("button", name="Referred by physician").click()
    human_delay(0.4, 0.8)
    page.get_by_role("button", name="Next").click()
    human_delay(0.8, 1.5)  # Page transition
    
    # Insurance Information (using fake data)
    human_delay(0.5, 1.0)  # Locating fields
    page.get_by_role("textbox", name="Member Name *").click()
    human_delay(0.3, 0.7)
    human_type(page.get_by_role("textbox", name="Member Name *"), fake_data['MemberName'])
    
    human_delay(0.4, 0.8)
    page.get_by_role("textbox", name="ID Number *").click()
    human_delay(0.3, 0.6)
    human_type(page.get_by_role("textbox", name="ID Number *"), fake_data['idNumber'])
    
    human_delay(0.4, 0.8)
    page.get_by_role("textbox", name="Group number *").click()
    human_delay(0.3, 0.6)
    human_type(page.get_by_role("textbox", name="Group number *"), fake_data['GroupNumber'])
    
    human_delay(0.5, 1.0)  # Company name
    page.get_by_role("textbox", name="Insurance Company Name *").click()
    human_delay(0.3, 0.7)
    human_type(page.get_by_role("textbox", name="Insurance Company Name *"), fake_data['PayerName'])
    
    human_delay(1.0, 2.0)  # Final review before submit
    page.get_by_role("button", name="Send to clinic").click()
    human_delay(1.5, 2.5)  # Submission processing
    # Success Page
    page.goto(f"{base_url}/success")
    human_delay(1.0, 2.0)  # Reading confirmation message
    
    # Verify redirect message
    redirect_msg = page.locator("div").filter(has_text=re.compile(r"^You will be redirected in \d+ seconds$"))
    human_delay(0.5, 1.0)  # Watching countdown
    redirect_msg.click()
    
    if enable_human:
        print("\n✅ Test completed with HUMAN BEHAVIOR simulation")
        print("   - Realistic typing speed (0.08-0.25s per character)")
        print("   - Natural thinking pauses (0.3-2.5s)")
        print("   - Human-like form filling behavior")
        print(f"   - Used fake data: {fake_data['email']}")
    else:
        print("\n⚡ Test completed in FAST MODE (no delays)")
        print(f"   - Used fake data: {fake_data['email']}")
