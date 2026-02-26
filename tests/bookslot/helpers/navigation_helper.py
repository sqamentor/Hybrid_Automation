"""
Bookslot Navigation Helper
==========================
Helper functions to navigate to specific pages in the bookslot flow using Page Objects.

Author: Lokendra Singh
Email: lokendra.singh@centerforvein.com
Website: www.centerforvein.com

Purpose:
- Reusable navigation logic to reach any page in the bookslot flow
- Uses Page Objects for all interactions (POM compliant)
- Eliminates code duplication via method chaining
- Makes it easy to test specific pages in isolation

Usage:
    from tests.bookslot.helpers.navigation_helper import BookslotNavigator

    navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
    navigator.navigate_to_insurance()
    # Now you're at insurance page - test your scenarios
"""

from pages.bookslot.bookslots_basicinfo_page1 import BookslotBasicInfoPage
from pages.bookslot.bookslot_eventtype_page2 import BookslotEventInfoPage
from pages.bookslot.bookslots_insurance_page6 import BookslotInsurancePage
from pages.bookslot.bookslots_personalInfo_page4 import BookslotPersonalInfoPage
from pages.bookslot.bookslots_referral_page5 import BookslotReferralPage
from pages.bookslot.bookslot_scheduler_page3 import BookslotWebSchedulerPage


class BookslotNavigator:
    """Helper class to navigate through bookslot pages using chained method calls."""

    def __init__(self, smart_actions, fake_bookslot_data, multi_project_config=None):
        """
        Initialize navigator with required fixtures.

        Args:
            smart_actions: Smart actions fixture
            fake_bookslot_data: Fake data fixture
            multi_project_config: Config dict (REQUIRED). Must contain bookslot.ui_url
        """
        self.act = smart_actions
        self.page = smart_actions.page

        # Get base_url from config - MUST be provided
        if not multi_project_config or "bookslot" not in multi_project_config:
            raise ValueError("multi_project_config with 'bookslot' key is required")

        self.base_url = multi_project_config["bookslot"]["ui_url"]
        self.data = fake_bookslot_data

    # ========================================================================
    # STEP 1: Basic Info (Entry Point)
    # ========================================================================

    def navigate_to_basic_info(self):
        """
        Navigate to Basic Info page (entry point).

        Returns:
            BookslotBasicInfoPage: Page Object at Basic Info
        """
        basic_info_page = BookslotBasicInfoPage(self.page, self.base_url)
        basic_info_page.navigate()

        # Handle language selection if present
        try:
            if basic_info_page.button_english.is_visible():
                basic_info_page.select_language_english()
        except Exception:
            pass  # Language already selected or not present

        return basic_info_page

    # ========================================================================
    # STEP 2: Event Type (chains from Basic Info)
    # ========================================================================

    def navigate_to_event_type(self):
        """
        Navigate to Event Type page.

        Steps: Basic Info → Event Type (chains navigate_to_basic_info)

        Returns:
            BookslotEventInfoPage: Page Object at Event Type
        """
        basic_info_page = self.navigate_to_basic_info()
        basic_info_page.fill_first_name(self.data["first_name"])
        basic_info_page.fill_last_name(self.data["last_name"])
        basic_info_page.fill_email(self.data["email"])
        basic_info_page.fill_phone(self.data["phone_number"])
        basic_info_page.proceed_to_next()

        return BookslotEventInfoPage(self.page, self.base_url)

    # ========================================================================
    # STEP 3: Scheduler (chains from Event Type)
    # ========================================================================

    def navigate_to_scheduler(self, event_type="New Patient"):
        """
        Navigate to Scheduler page.

        Steps: Basic Info → Event Type → Scheduler (chains navigate_to_event_type)

        Args:
            event_type: Type of appointment (default: "New Patient")

        Returns:
            BookslotWebSchedulerPage: Page Object at Scheduler
        """
        event_page = self.navigate_to_event_type()
        if event_type == "New Patient":
            event_page.select_new_patient()
        event_page.proceed_to_next()

        self.act.wait_for_scheduler(self.page)
        return BookslotWebSchedulerPage(self.page, self.base_url)

    # ========================================================================
    # STEP 4: Personal Info (chains from Scheduler)
    # ========================================================================

    def navigate_to_personal_info(self, event_type="New Patient", time_slot="AM"):
        """
        Navigate to Personal Info page.

        Steps: Basic Info → Event Type → Scheduler → Personal Info

        Args:
            event_type: Type of appointment (default: "New Patient")
            time_slot: Time slot selection - "AM" or "PM" (default: "AM")

        Returns:
            BookslotPersonalInfoPage: Page Object at Personal Info
        """
        scheduler_page = self.navigate_to_scheduler(event_type)
        if time_slot == "AM":
            scheduler_page.select_specific_slot("06:00 AM")
        else:
            scheduler_page.select_am_or_pm_slot(time_slot)
        scheduler_page.proceed_to_next()

        return BookslotPersonalInfoPage(self.page, self.base_url)

    # ========================================================================
    # STEP 5: Referral (chains from Personal Info)
    # ========================================================================

    def navigate_to_referral(self, event_type="New Patient", time_slot="AM"):
        """
        Navigate to Referral page.

        Steps: Basic Info → Event Type → Scheduler → Personal Info → Referral

        Args:
            event_type: Type of appointment (default: "New Patient")
            time_slot: Time slot selection - "AM" or "PM" (default: "AM")

        Returns:
            BookslotReferralPage: Page Object at Referral
        """
        personal_page = self.navigate_to_personal_info(event_type, time_slot)
        personal_page.fill_dob(self.data["dob"])
        personal_page.fill_address("123 Main St")
        personal_page.fill_city("New York")
        personal_page.fill_state("NY")
        personal_page.fill_zip(self.data["zip"])
        personal_page.proceed_to_next()

        return BookslotReferralPage(self.page, self.base_url)

    # ========================================================================
    # STEP 6: Insurance (chains from Referral)
    # ========================================================================

    def navigate_to_insurance(
        self, event_type="New Patient", time_slot="AM", referral_source="Online search"
    ):
        """
        Navigate to Insurance page.

        Steps: Basic Info → Event Type → Scheduler → Personal Info → Referral → Insurance

        Args:
            event_type: Type of appointment (default: "New Patient")
            time_slot: Time slot selection - "AM" or "PM" (default: "AM")
            referral_source: Referral source (default: "Online search")

        Returns:
            BookslotInsurancePage: Page Object at Insurance
        """
        referral_page = self.navigate_to_referral(event_type, time_slot)
        if referral_source == "Online search":
            referral_page.select_online()
        referral_page.proceed_to_next()

        return BookslotInsurancePage(self.page, self.base_url)

    # ========================================================================
    # STEP 7: Success (chains from Insurance)
    # ========================================================================

    def navigate_to_success(
        self,
        event_type="New Patient",
        time_slot="AM",
        referral_source="Online search",
        insurance_data=None,
    ):
        """
        Navigate to Success page (complete flow).

        Steps: Basic Info → Event Type → Scheduler → Personal Info → Referral → Insurance → Success

        Args:
            event_type: Type of appointment (default: "New Patient")
            time_slot: Time slot selection - "AM" or "PM" (default: "AM")
            referral_source: Referral source (default: "Online search")
            insurance_data: Custom insurance data (default: uses fake_bookslot_data)

        Returns:
            BookslotSuccessPage: Page Object at Success
        """
        insurance_page = self.navigate_to_insurance(event_type, time_slot, referral_source)
        insurance = insurance_data or self.data
        insurance_page.fill_member_name(insurance["MemberName"])
        insurance_page.fill_id_number(insurance["idNumber"])
        if "GroupNumber" in insurance:
            insurance_page.fill_group_number(insurance["GroupNumber"])
        insurance_page.fill_insurance_company(insurance["PayerName"])
        insurance_page.proceed_to_next()

        from pages.bookslot.bookslots_success_page7 import BookslotSuccessPage

        return BookslotSuccessPage(self.page, self.base_url)

    # ========================================================================
    # SINGLE-STEP TRANSITIONS (used by E2E tests with external data)
    # ========================================================================

    def complete_basic_to_scheduler(self, basic_info):
        """
        Complete P1 (Basic Info) → P2 (Event Type) → arrive at P3 (Scheduler).

        Unlike navigate_to_scheduler(), this accepts external data from test fixtures
        instead of using self.data, making it suitable for data-driven E2E tests.

        Args:
            basic_info: Dict with keys: name, email, phone
        """
        basic_info_page = self.navigate_to_basic_info()
        self.page.fill("[name='name']", basic_info["name"])
        self.page.fill("[name='email']", basic_info["email"])
        self.page.fill("[name='phone']", basic_info["phone"])
        self.page.click("button:has-text('Next')")

        # P2: Event Type — select first option and proceed
        self.page.click("[data-testid='event-type-option']:first-child")
        self.page.click("button:has-text('Next')")

    def complete_scheduler_to_personal_info(self, time_filter="am"):
        """
        Complete P3 (Scheduler) → arrive at P4 (Personal Info).

        Selects first available time slot and proceeds.

        Args:
            time_filter: "am" or "pm" (default: "am")
        """
        self.page.click(f"[data-testid='{time_filter}-filter']")
        self.page.click("[data-testid='time-slot']:first-child")
        self.page.click("button:has-text('Next')")

    def complete_personal_info_to_referral(self, personal_info):
        """
        Complete P4 (Personal Info) → arrive at P5 (Referral).

        Args:
            personal_info: Dict with keys: first_name, last_name, dob, address, city, state, zip_code
        """
        self.page.fill("[name='firstName']", personal_info["first_name"])
        self.page.fill("[name='lastName']", personal_info["last_name"])
        self.page.fill("[name='dateOfBirth']", personal_info["dob"])
        self.page.fill("[name='address']", personal_info["address"])
        self.page.fill("[name='city']", personal_info["city"])
        self.page.select_option("[name='state']", personal_info["state"])
        self.page.fill("[name='zipCode']", personal_info["zip_code"])
        self.page.click("button:has-text('Next')")

    def complete_referral_to_insurance(self, referral_source="doctor"):
        """
        Complete P5 (Referral) → arrive at P6 (Insurance).

        Args:
            referral_source: Referral source testid suffix (default: "doctor")
        """
        self.page.click(f"[data-testid='referral-source-{referral_source}']")
        self.page.click("button:has-text('Next')")


# ============================================================================
# CONVENIENCE FUNCTIONS (Optional - use class or these functions)
# ============================================================================


def quick_navigate_to_insurance(smart_actions, fake_bookslot_data, multi_project_config):
    """
    Quick function to navigate directly to insurance page.

    Usage:
        from tests.bookslot.helpers.navigation_helper import quick_navigate_to_insurance

        page = quick_navigate_to_insurance(smart_actions, fake_bookslot_data, multi_project_config)
        # Now test insurance page
    """
    navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
    return navigator.navigate_to_insurance()


def quick_navigate_to_personal_info(smart_actions, fake_bookslot_data, multi_project_config):
    """
    Quick function to navigate directly to personal info page.

    Usage:
        from tests.bookslot.helpers.navigation_helper import quick_navigate_to_personal_info

        page = quick_navigate_to_personal_info(smart_actions, fake_bookslot_data, multi_project_config)
        # Now test personal info page
    """
    navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
    return navigator.navigate_to_personal_info()


def quick_navigate_to_referral(smart_actions, fake_bookslot_data, multi_project_config):
    """
    Quick function to navigate directly to referral page.

    Usage:
        from tests.bookslot.helpers.navigation_helper import quick_navigate_to_referral

        page = quick_navigate_to_referral(smart_actions, fake_bookslot_data, multi_project_config)
        # Now test referral page
    """
    navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
    return navigator.navigate_to_referral()

