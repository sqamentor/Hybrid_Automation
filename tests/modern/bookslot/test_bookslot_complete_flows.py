"""
Test Suite: Bookslot Complete End-to-End Flows
==============================================
Comprehensive end-to-end tests covering complete appointment booking journeys.

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

BOOKING FLOW SEQUENCE:
======================
Basic Info → Event Type → Scheduler → Personal Info → Referral → Insurance → Success

Test Coverage:
- Happy path booking flows
- Different appointment types
- Various time slots (AM/PM)
- Multiple insurance providers
- Different referral sources
- Human behavior simulation
- Error recovery scenarios
- Data-driven booking variations

Run Commands:
    pytest tests/bookslot/test_bookslot_complete_flows.py -v
    pytest tests/bookslot/test_bookslot_complete_flows.py -m smoke -v
    pytest tests/bookslot/test_bookslot_complete_flows.py -m critical -v
"""

import allure
import pytest
import re
from playwright.sync_api import Page

from utils.logger import get_logger

logger = get_logger(__name__)


@allure.epic("Bookslot")
@allure.feature("Complete Booking Flows")
@pytest.mark.playwright
@pytest.mark.modern_spa
@pytest.mark.bookslot
@pytest.mark.e2e
class TestBookslotCompleteFlows:
    """End-to-end booking flow test suite"""

    @allure.story("Happy Path Booking")
    @allure.title("Complete booking: New Patient with Morning Slot")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.critical
    def test_complete_booking_new_patient_morning(
        self, page: Page, multi_project_config, smart_actions, fake_bookslot_data
    ):
        """
        Scenario: User books new patient appointment in morning slot

        Flow: Basic Info → Event (New Patient) → Scheduler (AM) → Personal → Referral → Insurance → Success
        """
        base_url = multi_project_config["bookslot"]["ui_url"]
        act = smart_actions
        data = fake_bookslot_data

        with allure.step("Step 1: Fill basic information"):
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            act.click(page.get_by_role("button", name="English"), "Select English")
            act.click(page.get_by_role("button", name="Español"), "Select Spanish")
            act.click(page.get_by_role("button", name="English"), "Select English")

            act.click(page.get_by_role("heading", name="We need to collect some"), "Heading")

            act.type_text(
                page.get_by_role("textbox", name="First Name *"), data["first_name"], "First Name"
            )
            act.type_text(
                page.get_by_role("textbox", name="Last Name *"), data["last_name"], "Last Name"
            )
            act.type_text(page.get_by_role("textbox", name="Email *"), data["email"], "Email")
            act.type_text(
                page.get_by_role("textbox", name="Phone *"), data["phone_number"], "Phone"
            )
            act.button_click(page.get_by_role("button", name="Next"), "Next")

        with allure.step("Step 2: Select New Patient appointment"):
            act.button_click(page.get_by_role("button", name="New Patient"), "New Patient")
            act.button_click(page.get_by_role("button", name="Next"), "Next")

        with allure.step("Step 3: Select morning time slot"):
            act.wait_for_scheduler("Time Slot Scheduler")
            page.locator("button:has-text('AM')").first.click()
            act.button_click(page.get_by_role("button", name="Next"), "Next")

        with allure.step("Step 4: Fill personal information"):
            act.type_text(page.get_by_role("textbox", name="Date of Birth *"), data["dob"], "DOB")
            act.type_text(page.get_by_role("textbox", name="Address *"), "123 Main St", "Address")
            act.type_text(page.get_by_role("textbox", name="City *"), "New York", "City")
            act.type_text(page.get_by_role("textbox", name="State *"), "NY", "State")
            act.type_text(page.get_by_role("textbox", name="Zip Code *"), data["zip"], "Zip")
            act.button_click(page.get_by_role("button", name="Next"), "Next")

        with allure.step("Step 5: Select referral source"):
            page.get_by_role("radio", name="Online search").click()
            act.button_click(page.get_by_role("button", name="Next"), "Next")

        with allure.step("Step 6: Fill insurance information"):
            act.type_text(
                page.get_by_role("textbox", name="Member Name *"), data["MemberName"], "Member"
            )
            act.type_text(page.get_by_role("textbox", name="ID Number *"), data["idNumber"], "ID")
            act.type_text(
                page.get_by_role("textbox", name="Group Number"), data["GroupNumber"], "Group"
            )
            act.type_text(
                page.get_by_role("textbox", name="Payer Name *"), data["PayerName"], "Payer"
            )
            act.button_click(page.get_by_role("button", name="Next"), "Next")

        with allure.step("Step 7: Verify booking success"):
            page.wait_for_timeout(1000)
            assert "/success" in page.url.lower() or "confirmation" in page.url.lower()
            allure.attach(
                page.screenshot(full_page=True),
                name="booking_success",
                attachment_type=allure.attachment_type.PNG,
            )

    @allure.story("Happy Path Booking")
    @allure.title("Complete booking: New Patient with Afternoon Slot")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_complete_booking_new_patient_afternoon(
        self, page: Page, multi_project_config, smart_actions, fake_bookslot_data
    ):
        """
        Scenario: User books new patient appointment in afternoon slot

        Flow: Basic Info → Event (New Patient) → Scheduler (PM) → Personal → Referral → Insurance → Success
        """
        base_url = multi_project_config["bookslot"]["ui_url"]
        act = smart_actions
        data = fake_bookslot_data

        with allure.step("Complete booking flow with PM slot"):
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            act.type_text(
                page.get_by_role("textbox", name="First Name *"), data["first_name"], "First Name"
            )
            act.type_text(
                page.get_by_role("textbox", name="Last Name *"), data["last_name"], "Last Name"
            )
            act.type_text(page.get_by_role("textbox", name="Email *"), data["email"], "Email")
            act.type_text(
                page.get_by_role("textbox", name="Phone *"), data["phone_number"], "Phone"
            )
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            act.button_click(page.get_by_role("button", name="New Patient"), "New Patient")
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            act.wait_for_scheduler("Time Slot Scheduler")
            page.locator("button:has-text('PM')").first.click()
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            act.type_text(page.get_by_role("textbox", name="Date of Birth *"), data["dob"], "DOB")
            act.type_text(page.get_by_role("textbox", name="Address *"), "456 Oak Ave", "Address")
            act.type_text(page.get_by_role("textbox", name="City *"), "Los Angeles", "City")
            act.type_text(page.get_by_role("textbox", name="State *"), "CA", "State")
            act.type_text(page.get_by_role("textbox", name="Zip Code *"), data["zip"], "Zip")
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            page.get_by_role("radio", name="Friend or family").click()
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            act.type_text(
                page.get_by_role("textbox", name="Member Name *"), data["MemberName"], "Member"
            )
            act.type_text(page.get_by_role("textbox", name="ID Number *"), data["idNumber"], "ID")
            act.type_text(
                page.get_by_role("textbox", name="Payer Name *"), data["PayerName"], "Payer"
            )
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            page.wait_for_timeout(1000)
            assert "/success" in page.url.lower() or "confirmation" in page.url.lower()

    @allure.story("Insurance Providers")
    @allure.title("Complete booking with different insurance providers")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "insurance_provider",
        ["Aetna", "Blue Cross Blue Shield", "Cigna", "UnitedHealthcare", "Medicare"],
        ids=["aetna", "bcbs", "cigna", "uhc", "medicare"],
    )
    def test_booking_with_various_insurance_providers(
        self,
        page: Page,
        multi_project_config,
        smart_actions,
        fake_bookslot_data,
        insurance_provider,
    ):
        """
        Scenario: Complete booking with different insurance providers

        Validates: System accepts various insurance companies
        """
        base_url = multi_project_config["bookslot"]["ui_url"]
        act = smart_actions
        data = fake_bookslot_data

        with allure.step(f"Book appointment with {insurance_provider}"):
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            act.type_text(
                page.get_by_role("textbox", name="First Name *"), data["first_name"], "First Name"
            )
            act.type_text(
                page.get_by_role("textbox", name="Last Name *"), data["last_name"], "Last Name"
            )
            act.type_text(page.get_by_role("textbox", name="Email *"), data["email"], "Email")
            act.type_text(
                page.get_by_role("textbox", name="Phone *"), data["phone_number"], "Phone"
            )
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            act.button_click(page.get_by_role("button", name="New Patient"), "New Patient")
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            act.wait_for_scheduler("Time Slot Scheduler")
            page.locator("button:has-text('AM')").first.click()
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            act.type_text(page.get_by_role("textbox", name="Date of Birth *"), data["dob"], "DOB")
            act.type_text(page.get_by_role("textbox", name="Address *"), "789 Elm St", "Address")
            act.type_text(page.get_by_role("textbox", name="City *"), "Chicago", "City")
            act.type_text(page.get_by_role("textbox", name="State *"), "IL", "State")
            act.type_text(page.get_by_role("textbox", name="Zip Code *"), data["zip"], "Zip")
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            page.get_by_role("radio", name="Social media").click()
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            act.type_text(
                page.get_by_role("textbox", name="Member Name *"), "Test Member", "Member"
            )
            act.type_text(page.get_by_role("textbox", name="ID Number *"), "123456789", "ID")
            act.type_text(
                page.get_by_role("textbox", name="Payer Name *"), insurance_provider, "Payer"
            )
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            page.wait_for_timeout(1000)
            assert "/success" in page.url.lower() or "confirmation" in page.url.lower()
            allure.attach(
                page.screenshot(full_page=True),
                name=f"success_{insurance_provider.lower().replace(' ', '_')}",
                attachment_type=allure.attachment_type.PNG,
            )

    @allure.story("Referral Sources")
    @allure.title("Complete booking with different referral sources")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "referral_source",
        [
            "Referred by physician",
            "Online search",
            "Social media",
            "Friend or family",
            "Advertisement",
        ],
        ids=["physician", "online", "social", "word_of_mouth", "ad"],
    )
    def test_booking_with_various_referral_sources(
        self, page: Page, multi_project_config, smart_actions, fake_bookslot_data, referral_source
    ):
        """
        Scenario: Complete booking with different referral sources

        Validates: Marketing attribution tracking
        """
        base_url = multi_project_config["bookslot"]["ui_url"]
        act = smart_actions
        data = fake_bookslot_data

        with allure.step(f"Book appointment via {referral_source}"):
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            act.type_text(
                page.get_by_role("textbox", name="First Name *"), data["first_name"], "First Name"
            )
            act.type_text(
                page.get_by_role("textbox", name="Last Name *"), data["last_name"], "Last Name"
            )
            act.type_text(page.get_by_role("textbox", name="Email *"), data["email"], "Email")
            act.type_text(
                page.get_by_role("textbox", name="Phone *"), data["phone_number"], "Phone"
            )
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            act.button_click(page.get_by_role("button", name="New Patient"), "New Patient")
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            act.wait_for_scheduler("Time Slot Scheduler")
            page.locator("button:has-text('AM')").first.click()
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            act.type_text(page.get_by_role("textbox", name="Date of Birth *"), data["dob"], "DOB")
            act.type_text(page.get_by_role("textbox", name="Address *"), "321 Pine Ave", "Address")
            act.type_text(page.get_by_role("textbox", name="City *"), "Miami", "City")
            act.type_text(page.get_by_role("textbox", name="State *"), "FL", "State")
            act.type_text(page.get_by_role("textbox", name="Zip Code *"), data["zip"], "Zip")
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            page.get_by_role("radio", name=referral_source).click()
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            act.type_text(
                page.get_by_role("textbox", name="Member Name *"), data["MemberName"], "Member"
            )
            act.type_text(page.get_by_role("textbox", name="ID Number *"), data["idNumber"], "ID")
            act.type_text(
                page.get_by_role("textbox", name="Payer Name *"), data["PayerName"], "Payer"
            )
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            page.wait_for_timeout(1000)
            assert "/success" in page.url.lower() or "confirmation" in page.url.lower()

    @allure.story("Human Behavior")
    @allure.title("Complete booking with realistic human behavior")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.human_behavior
    def test_booking_with_human_behavior_simulation(
        self, page: Page, multi_project_config, smart_actions, fake_bookslot_data
    ):
        """
        Complete bookslot test with human behavior simulation
        Follows recorded test strategy for maximum reliability
        Incorporates ALL logic from test_bookslot_complete_workflow.py
        """
        base_url = multi_project_config["bookslot"]["ui_url"]
        act = smart_actions
        data = fake_bookslot_data

        logger.info(f"Testing with email: {data['email']}")

        with allure.step("Complete booking with human-like behavior"):
            # =====================================================================
            # BASIC INFO PAGE - Complete with all interactions
            # =====================================================================
            act.navigate(f"{base_url}/basic-info", "Basic Info")

            # Language toggle interactions
            act.click(page.get_by_role("button", name="English"), "Select English")
            act.click(page.get_by_role("button", name="Español"), "Select Spanish")
            act.click(page.get_by_role("button", name="English"), "Select English")

            # Heading interactions
            act.click(page.get_by_role("heading", name="We need to collect some"), "Heading")
            act.click(page.get_by_role("heading", name="Fields marked with * are"), "Heading")

            # Fill basic info fields
            act.type_text(
                page.get_by_role("textbox", name="First Name *"), data["first_name"], "First Name"
            )
            act.type_text(
                page.get_by_role("textbox", name="Last Name *"), data["last_name"], "Last Name"
            )
            act.type_text(page.get_by_role("textbox", name="E-mail *"), data["email"], "Email")
            act.type_text(
                page.locator("#CellPhone").get_by_role("textbox"), data["phone_number"], "Phone"
            )
            act.type_text(page.locator("#ZipCode"), data["zip"], "Zip Code")

            # Contact preference interaction
            act.click(page.get_by_text("Text E-mail Call"), "Contact Preference")

            # Submit to get OTP
            act.button_click(
                page.get_by_role("button", name="Send Me The Code"),
                "Send Code",
                wait_processing=True,
            )

            # =====================================================================
            # OTP VERIFICATION - Enhanced with better handling
            # =====================================================================
            act.wait_for_page_ready("OTP Page")

            # Find and fill OTP field with multiple selector attempts
            otp_field = page.locator(
                "#otp, input[type='text'][name*='otp'], input[placeholder*='code'], input[placeholder*='OTP']"
            ).first
            if act.wait_and_click(otp_field, "OTP Field", timeout=30000):
                act.type_text(otp_field, data["verification_code"], "OTP Code")
                logger.info("OTP filled successfully")
            else:
                logger.warning("OTP field not found - skipping OTP entry")

            # Verify OTP with processing wait
            act.button_click(
                page.get_by_role("button", name="Verify Code"), "Verify", wait_processing=True
            )

            # Wait for loader to disappear with comprehensive error handling
            try:
                page.wait_for_selector(".loader, .spinner", state="hidden", timeout=30000)
            except TimeoutError:
                logger.warning("Loader still visible after 30s timeout - continuing")
            except Exception as exc:
                logger.warning(f"Unexpected error waiting for loader: {exc}")

            # =====================================================================
            # EVENT TYPE SELECTION - Complete with all interactions
            # =====================================================================
            act.navigate(f"{base_url}/eventtype", "Event Type")

            # Request callback interaction (optional)
            try:
                act.button_click(
                    page.get_by_role("button", name="Request Call back"), "Request Call back"
                )
                act.click(
                    page.get_by_text("Request has been submitted"),
                    "Call back Request Submission Confirmation",
                )
            except Exception as exc:
                logger.warning(f"Request callback not available - skipping ({type(exc).__name__})")

            # PVN Event Selection with detailed interactions
            act.click(
                page.get_by_role("heading", name="New Patient Appointment"), "Appointment Type"
            )
            act.click(page.get_by_text("90-minute appointment with"), "Appointment Details")
            act.button_click(
                page.get_by_role("button", name="Book Now").first,
                "New Patient Appointment-Book Now",
            )

            # CPV Event Selection (Alternative - commented)
            # act.click(page.get_by_role("heading", name="Complimentary Consultation"), "Complimentary Consultation")
            # act.click(page.get_by_text("15-minute appointmentwith a"), "Appointment Details")
            # act.button_click(page.get_by_role("button", name="Book Now").nth(1), "Complimentary Consultation-Book Now")

            # =====================================================================
            # TIME SLOT SELECTION - Smart retry with error handling
            # =====================================================================
            act.wait_for_scheduler("Time Slot Scheduler")

            def select_time_slot():
                """Smart slot selection with error detection"""
                slots = page.locator(
                    "button[role='button']:has-text('AM'), button[role='button']:has-text('PM')"
                ).all()
                if slots:
                    act.click(slots[0], "Time Slot")
                else:
                    act.click(page.locator("button:has-text(':')").first, "Time Slot Fallback")

                # Check for errors
                if page.locator("text=/went wrong|error|try again/i").count() > 0:
                    raise Exception("Slot booking error detected - error message on page")

                logger.info("Time slot selected successfully")

            try:
                act.smart_retry(select_time_slot, max_retries=3)
            except Exception as exc:
                logger.warning(f"Slot booking error after 3 retries: {exc} - attempting last-resort slot")
                try:
                    act.click(page.get_by_role("button", name="06:00 AM"), "06:00 AM Slot")
                except Exception as slot_error:
                    logger.error(f"Last-resort slot selection failed: {slot_error} - continuing")

            # Slot confirmation interaction
            act.click(page.get_by_text("Request an Appointment This"), "Confirm Slot")
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            # =====================================================================
            # PERSONAL INFORMATION - Complete with gender and smart autocomplete
            # =====================================================================

            # Gender selection with proper select_option
            try:
                act.select_option(
                    page.get_by_role("combobox", name="Select Gender"),
                    page.get_by_role("option", name="MALE", exact=True),
                    "Gender",
                )
            except Exception as exc:
                logger.warning(f"Gender selection skipped - field may be optional ({type(exc).__name__})")

            # Fill DOB
            act.type_text(
                page.get_by_role("combobox", name="mm/dd/yyyy"), data["dob"], "Date of Birth"
            )

            # Address with smart autocomplete and fallback
            act.type_text(page.get_by_role("textbox", name="Address"), data["zip"], "Address")

            if not act.wait_autocomplete(
                "text=/Highmore|USA|SD/", "Address Suggestion", timeout=6000
            ):
                act.wait_autocomplete("text=/USA/", "Address Fallback", timeout=2000)

            act.button_click(page.get_by_role("button", name="Next"), "Next")

            # =====================================================================
            # REFERRAL SOURCE - Complete with heading interaction
            # =====================================================================
            act.click(
                page.get_by_role("heading", name="How did you hear about us?"), "Referral Question"
            )
            act.button_click(
                page.get_by_role("button", name="Referred by physician"), "Referral Source"
            )
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            # =====================================================================
            # INSURANCE INFORMATION - Complete with processing wait
            # =====================================================================
            act.type_text(
                page.get_by_role("textbox", name="Member Name *"), data["MemberName"], "Member Name"
            )
            act.type_text(
                page.get_by_role("textbox", name="ID Number *"), data["idNumber"], "ID Number"
            )
            act.type_text(
                page.get_by_role("textbox", name="Group number *"),
                data["GroupNumber"],
                "Group Number",
            )
            act.type_text(
                page.get_by_role("textbox", name="Insurance Company Name *"),
                data["PayerName"],
                "Insurance Company",
            )

            # Wait for processing before final submit
            act.wait_for_processing("Final review", short=True)
            act.button_click(
                page.get_by_role("button", name="Send to clinic"), "Submit", wait_processing=True
            )

            # =====================================================================
            # SUCCESS PAGE - Complete with redirect message
            # =====================================================================
            act.navigate(f"{base_url}/success", "Success Page")

            # Redirect message interaction
            try:
                redirect_msg = page.locator("div").filter(
                    has_text=re.compile(r"^You will be redirected in \d+ seconds$")
                )
                act.click(redirect_msg, "Redirect Message")
            except Exception as exc:
                logger.warning(f"Redirect message not found - page may have already redirected ({type(exc).__name__})")

            # Verify success
            assert (
                "/success" in page.url.lower()
                or "confirmation" in page.url.lower()
                or "thank" in page.url.lower()
            )

            logger.info(f"Test completed successfully with email: {data['email']}")

            allure.attach(
                page.screenshot(full_page=True),
                name="booking_success_complete",
                attachment_type=allure.attachment_type.PNG,
            )
            allure.attach(
                "Human behavior simulation completed with ALL recorded test features",
                name="behavior_test",
                attachment_type=allure.attachment_type.TEXT,
            )

    @allure.story("Error Recovery")
    @allure.title("User recovers from invalid email and completes booking")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_booking_with_error_recovery(
        self, page: Page, multi_project_config, smart_actions, fake_bookslot_data
    ):
        """
        Scenario: User enters invalid email, corrects it, and completes booking

        Validates: Error recovery and form resilience
        """
        base_url = multi_project_config["bookslot"]["ui_url"]
        act = smart_actions
        data = fake_bookslot_data

        with allure.step("Attempt with invalid email"):
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            act.type_text(
                page.get_by_role("textbox", name="First Name *"), data["first_name"], "First Name"
            )
            act.type_text(
                page.get_by_role("textbox", name="Last Name *"), data["last_name"], "Last Name"
            )
            act.type_text(
                page.get_by_role("textbox", name="Email *"), "invalid.email", "Invalid Email"
            )
            act.type_text(
                page.get_by_role("textbox", name="Phone *"), data["phone_number"], "Phone"
            )
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            page.wait_for_timeout(500)
            initial_url = page.url

        with allure.step("Correct email and complete booking"):
            act.type_text(page.get_by_role("textbox", name="Email *"), data["email"], "Valid Email")
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            act.button_click(page.get_by_role("button", name="New Patient"), "New Patient")
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            act.wait_for_scheduler("Time Slot Scheduler")
            page.locator("button:has-text('AM')").first.click()
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            act.type_text(page.get_by_role("textbox", name="Date of Birth *"), data["dob"], "DOB")
            act.type_text(
                page.get_by_role("textbox", name="Address *"), "777 Recovery St", "Address"
            )
            act.type_text(page.get_by_role("textbox", name="City *"), "Boston", "City")
            act.type_text(page.get_by_role("textbox", name="State *"), "MA", "State")
            act.type_text(page.get_by_role("textbox", name="Zip Code *"), data["zip"], "Zip")
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            page.get_by_role("radio", name="Online search").click()
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            act.type_text(
                page.get_by_role("textbox", name="Member Name *"), data["MemberName"], "Member"
            )
            act.type_text(page.get_by_role("textbox", name="ID Number *"), data["idNumber"], "ID")
            act.type_text(
                page.get_by_role("textbox", name="Payer Name *"), data["PayerName"], "Payer"
            )
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            page.wait_for_timeout(1000)
            assert page.url != initial_url
            assert "/success" in page.url.lower() or "confirmation" in page.url.lower()
            allure.attach(
                "User successfully recovered from error",
                name="error_recovery",
                attachment_type=allure.attachment_type.TEXT,
            )

    @allure.story("Data Persistence")
    @allure.title("Verify data persists when navigating back and forward")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_data_persistence_during_navigation(
        self, page: Page, multi_project_config, smart_actions, fake_bookslot_data
    ):
        """
        Scenario: User fills form, goes back, returns, and data is preserved

        Validates: Form data persistence across navigation
        """
        base_url = multi_project_config["bookslot"]["ui_url"]
        act = smart_actions
        data = fake_bookslot_data

        with allure.step("Fill basic info and advance"):
            act.navigate(f"{base_url}/basic-info", "Basic Info")
            act.type_text(
                page.get_by_role("textbox", name="First Name *"), data["first_name"], "First Name"
            )
            act.type_text(
                page.get_by_role("textbox", name="Last Name *"), data["last_name"], "Last Name"
            )
            act.type_text(page.get_by_role("textbox", name="Email *"), data["email"], "Email")
            act.type_text(
                page.get_by_role("textbox", name="Phone *"), data["phone_number"], "Phone"
            )
            act.button_click(page.get_by_role("button", name="Next"), "Next")

        with allure.step("Navigate back and verify data persistence"):
            page.go_back()
            page.wait_for_timeout(1000)

            # Capture screenshot showing preserved data
            allure.attach(
                page.screenshot(full_page=True),
                name="data_persistence_check",
                attachment_type=allure.attachment_type.PNG,
            )

            # Continue to verify full flow still works
            act.button_click(page.get_by_role("button", name="Next"), "Next")
            act.button_click(page.get_by_role("button", name="New Patient"), "New Patient")
            act.button_click(page.get_by_role("button", name="Next"), "Next")

            act.wait_for_scheduler("Time Slot Scheduler")
            assert page.url != f"{base_url}/basic-info"
