"""
Bookslot Navigation Helper
==========================
Helper functions to navigate to specific pages in the bookslot flow using Page Objects.

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

Purpose:
- Reusable navigation logic to reach any page in the bookslot flow
- Uses Page Objects for all interactions (POM compliant)
- Eliminates code duplication across tests
- Makes it easy to test specific pages in isolation

Usage:
    from tests.bookslot.helpers.navigation_helper import BookslotNavigator

    navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
    navigator.navigate_to_insurance_page()
    # Now you're at insurance page - test your scenarios
"""

from pages.bookslot.bookslots_basicinfo_page1 import BookslotBasicInfoPage
from pages.bookslot.bookslot_eventtype_page2 import BookslotEventInfoPage
from pages.bookslot.bookslots_insurance_page6 import BookslotInsurancePage
from pages.bookslot.bookslots_personalInfo_page4 import BookslotPersonalInfoPage
from pages.bookslot.bookslots_referral_page5 import BookslotReferralPage
from pages.bookslot.bookslot_scheduler_page3 import BookslotWebSchedulerPage


class BookslotNavigator:
    """Helper class to navigate through bookslot pages"""

    def __init__(self, smart_actions, fake_bookslot_data, multi_project_config=None):
        """
        Initialize navigator with required fixtures

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

    def navigate_to_basic_info(self):
        """
        Navigate to Basic Info page (entry point)

        Returns:
            BookslotBasicInfoPage: Page Object at Basic Info
        """
        basic_info_page = BookslotBasicInfoPage(self.page, self.base_url)
        basic_info_page.navigate()

        # Handle language selection if present
        try:
            if basic_info_page.button_english.is_visible():
                basic_info_page.select_language_english()
        except:
            pass  # Language already selected or not present

        return basic_info_page

    def navigate_to_event_type(self):
        """
        Navigate to Event Type page

        Steps: Basic Info → Event Type
        Uses Page Objects for all interactions

        Returns:
            BookslotEventInfoPage: Page Object at Event Type
        """
        # Step 1: Fill Basic Info using Page Object
        basic_info_page = BookslotBasicInfoPage(self.page, self.base_url)
        basic_info_page.navigate()
        basic_info_page.fill_first_name(self.data["first_name"])
        basic_info_page.fill_last_name(self.data["last_name"])
        basic_info_page.fill_email(self.data["email"])
        basic_info_page.fill_phone(self.data["phone_number"])
        basic_info_page.proceed_to_next()

        # Return Event Type Page Object
        return BookslotEventInfoPage(self.page, self.base_url)

    def navigate_to_scheduler(self, event_type="New Patient"):
        """
        Navigate to Scheduler page

        Steps: Basic Info → Event Type → Scheduler
        Uses Page Objects for all interactions

        Args:
            event_type: Type of appointment (default: "New Patient")

        Returns:
            BookslotWebSchedulerPage: Page Object at Scheduler
        """
        # Step 1: Fill Basic Info using Page Object
        basic_info_page = BookslotBasicInfoPage(self.page, self.base_url)
        basic_info_page.navigate()
        basic_info_page.fill_first_name(self.data["first_name"])
        basic_info_page.fill_last_name(self.data["last_name"])
        basic_info_page.fill_email(self.data["email"])
        basic_info_page.fill_phone(self.data["phone_number"])
        basic_info_page.proceed_to_next()

        # Step 2: Select Event Type using Page Object
        event_page = BookslotEventInfoPage(self.page, self.base_url)
        if event_type == "New Patient":
            event_page.select_new_patient()
        event_page.proceed_to_next()

        # Wait for scheduler to load
        self.act.wait_for_scheduler(self.page)

        # Return Scheduler Page Object
        return BookslotWebSchedulerPage(self.page, self.base_url)

    def navigate_to_personal_info(self, event_type="New Patient", time_slot="AM"):
        """
        Navigate to Personal Info page

        Steps: Basic Info → Event Type → Scheduler → Personal Info
        Uses Page Objects for all interactions

        Args:
            event_type: Type of appointment (default: "New Patient")
            time_slot: Time slot selection - "AM" or "PM" (default: "AM")

        Returns:
            BookslotPersonalInfoPage: Page Object at Personal Info
        """
        # Step 1: Fill Basic Info using Page Object
        basic_info_page = BookslotBasicInfoPage(self.page, self.base_url)
        basic_info_page.navigate()
        basic_info_page.fill_first_name(self.data["first_name"])
        basic_info_page.fill_last_name(self.data["last_name"])
        basic_info_page.fill_email(self.data["email"])
        basic_info_page.fill_phone(self.data["phone_number"])
        basic_info_page.proceed_to_next()

        # Step 2: Select Event Type using Page Object
        event_page = BookslotEventInfoPage(self.page, self.base_url)
        if event_type == "New Patient":
            event_page.select_new_patient()
        event_page.proceed_to_next()

        # Step 3: Select Time Slot using Page Object
        self.act.wait_for_scheduler(self.page)
        scheduler_page = BookslotWebSchedulerPage(self.page, self.base_url)
        # Use Page Object method for time slot selection
        if time_slot == "AM":
            scheduler_page.select_specific_slot("06:00 AM")
        else:
            scheduler_page.select_am_or_pm_slot(time_slot)
        scheduler_page.proceed_to_next()

        # Return Personal Info Page Object
        return BookslotPersonalInfoPage(self.page, self.base_url)

    def navigate_to_referral(self, event_type="New Patient", time_slot="AM"):
        """
        Navigate to Referral page

        Steps: Basic Info → Event Type → Scheduler → Personal Info → Referral
        Uses Page Objects for all interactions

        Args:
            event_type: Type of appointment (default: "New Patient")
            time_slot: Time slot selection - "AM" or "PM" (default: "AM")

        Returns:
            BookslotReferralPage: Page Object at Referral
        """
        # Step 1: Fill Basic Info using Page Object
        basic_info_page = BookslotBasicInfoPage(self.page, self.base_url)
        basic_info_page.navigate()
        basic_info_page.fill_first_name(self.data["first_name"])
        basic_info_page.fill_last_name(self.data["last_name"])
        basic_info_page.fill_email(self.data["email"])
        basic_info_page.fill_phone(self.data["phone_number"])
        basic_info_page.proceed_to_next()

        # Step 2: Select Event Type using Page Object
        event_page = BookslotEventInfoPage(self.page, self.base_url)
        if event_type == "New Patient":
            event_page.select_new_patient()
        event_page.proceed_to_next()

        # Step 3: Select Time Slot using Page Object
        self.act.wait_for_scheduler(self.page)
        scheduler_page = BookslotWebSchedulerPage(self.page, self.base_url)
        if time_slot == "AM":
            scheduler_page.select_specific_slot("06:00 AM")
        else:
            scheduler_page.select_am_or_pm_slot(time_slot)
        scheduler_page.proceed_to_next()

        # Step 4: Fill Personal Info using Page Object
        personal_page = BookslotPersonalInfoPage(self.page, self.base_url)
        personal_page.fill_dob(self.data["dob"])
        personal_page.fill_address("123 Main St")
        personal_page.fill_city("New York")
        personal_page.fill_state("NY")
        personal_page.fill_zip(self.data["zip"])
        personal_page.proceed_to_next()

        # Return Referral Page Object
        return BookslotReferralPage(self.page, self.base_url)

    def navigate_to_insurance(
        self, event_type="New Patient", time_slot="AM", referral_source="Online search"
    ):
        """
        Navigate to Insurance page

        Steps: Basic Info → Event Type → Scheduler → Personal Info → Referral → Insurance
        Uses Page Objects for all interactions

        Args:
            event_type: Type of appointment (default: "New Patient")
            time_slot: Time slot selection - "AM" or "PM" (default: "AM")
            referral_source: Referral source (default: "Online search")

        Returns:
            BookslotInsurancePage: Page Object at Insurance
        """
        # Step 1: Fill Basic Info using Page Object
        basic_info_page = BookslotBasicInfoPage(self.page, self.base_url)
        basic_info_page.navigate()
        basic_info_page.fill_first_name(self.data["first_name"])
        basic_info_page.fill_last_name(self.data["last_name"])
        basic_info_page.fill_email(self.data["email"])
        basic_info_page.fill_phone(self.data["phone_number"])
        basic_info_page.proceed_to_next()

        # Step 2: Select Event Type using Page Object
        event_page = BookslotEventInfoPage(self.page, self.base_url)
        if event_type == "New Patient":
            event_page.select_new_patient()
        event_page.proceed_to_next()

        # Step 3: Select Time Slot using Page Object
        self.act.wait_for_scheduler(self.page)
        scheduler_page = BookslotWebSchedulerPage(self.page, self.base_url)
        if time_slot == "AM":
            scheduler_page.select_specific_slot("06:00 AM")
        else:
            scheduler_page.select_am_or_pm_slot(time_slot)
        scheduler_page.proceed_to_next()

        # Step 4: Fill Personal Info using Page Object
        personal_page = BookslotPersonalInfoPage(self.page, self.base_url)
        personal_page.fill_dob(self.data["dob"])
        personal_page.fill_address("123 Main St")
        personal_page.fill_city("New York")
        personal_page.fill_state("NY")
        personal_page.fill_zip(self.data["zip"])
        personal_page.proceed_to_next()

        # Step 5: Select Referral using Page Object
        referral_page = BookslotReferralPage(self.page, self.base_url)
        if referral_source == "Online search":
            referral_page.select_online()
        referral_page.proceed_to_next()

        # Return Insurance Page Object
        return BookslotInsurancePage(self.page, self.base_url)

    def navigate_to_success(
        self,
        event_type="New Patient",
        time_slot="AM",
        referral_source="Online search",
        insurance_data=None,
    ):
        """
        Navigate to Success page (complete flow)

        Steps: Basic Info → Event Type → Scheduler → Personal Info → Referral → Insurance → Success
        Uses Page Objects for all interactions

        Args:
            event_type: Type of appointment (default: "New Patient")
            time_slot: Time slot selection - "AM" or "PM" (default: "AM")
            referral_source: Referral source (default: "Online search")
            insurance_data: Custom insurance data (default: uses fake_bookslot_data)

        Returns:
            BookslotSuccessPage: Page Object at Success
        """
        # Step 1: Fill Basic Info using Page Object
        basic_info_page = BookslotBasicInfoPage(self.page, self.base_url)
        basic_info_page.navigate()
        basic_info_page.fill_first_name(self.data["first_name"])
        basic_info_page.fill_last_name(self.data["last_name"])
        basic_info_page.fill_email(self.data["email"])
        basic_info_page.fill_phone(self.data["phone_number"])
        basic_info_page.proceed_to_next()

        # Step 2: Select Event Type using Page Object
        event_page = BookslotEventInfoPage(self.page, self.base_url)
        if event_type == "New Patient":
            event_page.select_new_patient()
        event_page.proceed_to_next()

        # Step 3: Select Time Slot using Page Object
        self.act.wait_for_scheduler(self.page)
        scheduler_page = BookslotWebSchedulerPage(self.page, self.base_url)
        if time_slot == "AM":
            scheduler_page.select_specific_slot("06:00 AM")
        else:
            scheduler_page.select_am_or_pm_slot(time_slot)
        scheduler_page.proceed_to_next()

        # Step 4: Fill Personal Info using Page Object
        personal_page = BookslotPersonalInfoPage(self.page, self.base_url)
        personal_page.fill_dob(self.data["dob"])
        personal_page.fill_address("123 Main St")
        personal_page.fill_city("New York")
        personal_page.fill_state("NY")
        personal_page.fill_zip(self.data["zip"])
        personal_page.proceed_to_next()

        # Step 5: Select Referral using Page Object
        referral_page = BookslotReferralPage(self.page, self.base_url)
        if referral_source == "Online search":
            referral_page.select_online()
        referral_page.proceed_to_next()

        # Step 6: Fill Insurance using Page Object
        insurance_page = BookslotInsurancePage(self.page, self.base_url)
        insurance = insurance_data or self.data
        insurance_page.fill_member_name(insurance["MemberName"])
        insurance_page.fill_id_number(insurance["idNumber"])
        if "GroupNumber" in insurance:
            insurance_page.fill_group_number(insurance["GroupNumber"])
        insurance_page.fill_insurance_company(insurance["PayerName"])
        insurance_page.proceed_to_next()

        # Return Success Page Object
        from pages.bookslot.bookslots_success_page7 import BookslotSuccessPage

        return BookslotSuccessPage(self.page, self.base_url)


# ============================================================================
# CONVENIENCE FUNCTIONS (Optional - use class or these functions)
# ============================================================================


def quick_navigate_to_insurance(smart_actions, fake_bookslot_data):
    """
    Quick function to navigate directly to insurance page

    Usage:
        from tests.bookslot.helpers.navigation_helper import quick_navigate_to_insurance

        page = quick_navigate_to_insurance(smart_actions, fake_bookslot_data)
        # Now test insurance page
    """
    navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
    return navigator.navigate_to_insurance()


def quick_navigate_to_personal_info(smart_actions, fake_bookslot_data):
    """
    Quick function to navigate directly to personal info page

    Usage:
        from tests.bookslot.helpers.navigation_helper import quick_navigate_to_personal_info

        page = quick_navigate_to_personal_info(smart_actions, fake_bookslot_data)
        # Now test personal info page
    """
    navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
    return navigator.navigate_to_personal_info()


def quick_navigate_to_referral(smart_actions, fake_bookslot_data):
    """
    Quick function to navigate directly to referral page

    Usage:
        from tests.bookslot.helpers.navigation_helper import quick_navigate_to_referral

        page = quick_navigate_to_referral(smart_actions, fake_bookslot_data)
        # Now test referral page
    """
    navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
    return navigator.navigate_to_referral()
