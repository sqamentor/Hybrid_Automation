"""
Page Object: Bookslot Web Scheduler Page
Represents what a user can do on the Scheduler page

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

Project: BookSlot
Module: Web Scheduler (Date/Time Selection)

Responsibilities:
✔ Locators for calendar and time slots
✔ Actions (select date, select time, navigate)
✔ Page-level checks
✔ Navigation

Does NOT contain:
❌ Test data
❌ Business rule assertions
❌ API/DB validation
❌ pytest markers
❌ Complete test flows
"""

from playwright.sync_api import Page, Locator
from framework.core.smart_actions import SmartActions


class BookslotWebSchedulerPage:
    """
    Page Object for Bookslot Web Scheduler

    What a user can do on this page:
    - Navigate to scheduler
    - Wait for calendar to load
    - Select available time slot (AM/PM)
    - Confirm slot selection
    - Proceed to next page
    """

    def __init__(self, page: Page, base_url: str):
        """
        Initialize page object

        Args:
            page: Playwright Page instance
            base_url: Base URL from multi_project_config
        """
        self.page = page
        self.actions = SmartActions(page)
        if not base_url:
            raise ValueError("base_url is required from multi_project_config")
        self.base_url = base_url
        self.path = "/scheduler"

    # ===================================================================
    # LOCATORS
    # ===================================================================

    @property
    def calendar_container(self):
        """Calendar container element"""
        return self.page.locator(".calendar, [class*='calendar'], [class*='scheduler']").first

    @property
    def time_slots_am_pm(self):
        """All AM/PM time slot buttons"""
        return self.page.locator(
            "button[role='button']:has-text('AM'), button[role='button']:has-text('PM')"
        )

    @property
    def time_slots_any(self):
        """Any time slot button with colon (:)"""
        return self.page.locator("button:has-text(':')")

    @property
    def specific_slot_6am(self):
        """6:00 AM specific slot"""
        return self.page.get_by_role("button", name="06:00 AM")

    @property
    def text_request_appointment(self):
        """Request an Appointment confirmation text"""
        return self.page.get_by_text("Request an Appointment This")

    @property
    def button_next(self):
        """Next button"""
        return self.page.get_by_role("button", name="Next")

    @property
    def loader(self):
        """Loading spinner"""
        return self.page.locator(".loader, .spinner, [class*='loading']")

    # ===================================================================
    # NAVIGATION
    # ===================================================================

    def navigate(self):
        """Navigate to the scheduler page"""
        url = f"{self.base_url}{self.path}"
        self.page.goto(url)
        return self

    # ===================================================================
    # ACTIONS
    # ===================================================================

    def wait_for_scheduler_ready(self):
        """Wait for scheduler to be ready for interaction"""
        self.actions.wait_for_scheduler(self.page)
        return self

    def select_first_available_slot(self):
        """Select first available AM/PM slot using SmartActions"""
        slots = self.time_slots_am_pm.all()
        if slots and len(slots) > 0:
            self.actions.button_click(slots[0], "First Available Slot")
        else:
            # Fallback to any slot with time format
            self.actions.button_click(self.time_slots_any.first, "Time Slot")
        return self

    def select_am_slot(self):
        """Select the first available AM time slot"""
        self.actions.button_click(self.page.locator("button:has-text('AM')").first, "AM Slot")
        return self

    def select_pm_slot(self):
        """Select the first available PM time slot"""
        self.actions.button_click(self.page.locator("button:has-text('PM')").first, "PM Slot")
        return self

    def select_specific_slot(self, slot_text: str):
        """Select a specific time slot by text (e.g., '06:00 AM')"""
        self.actions.button_click(
            self.page.get_by_role("button", name=slot_text), f"Time Slot: {slot_text}"
        )
        return self

    def select_6am_slot(self):
        """Select 6:00 AM slot specifically"""
        self.actions.button_click(self.specific_slot_6am, "6:00 AM Slot")
        return self

    def select_am_or_pm_slot(self, slot_type: str):
        """
        Select first available AM or PM slot

        Args:
            slot_type: "AM" or "PM"
        """
        self.actions.button_click(
            self.page.locator(f"button:has-text('{slot_type}')").first, f"{slot_type} Slot"
        )
        return self

    def is_am_or_pm_slot_visible(self, slot_type: str) -> bool:
        """
        Check if AM or PM slot is visible

        Args:
            slot_type: "AM" or "PM"

        Returns:
            bool: True if visible, False otherwise
        """
        try:
            return self.page.locator(f"button:has-text('{slot_type}')").first.is_visible()
        except:
            return False

    def get_am_slots_count(self) -> int:
        """Get count of AM slots"""
        return self.page.locator("button:has-text('AM')").count()

    def get_pm_slots_count(self) -> int:
        """Get count of PM slots"""
        return self.page.locator("button:has-text('PM')").count()

    def confirm_slot(self):
        """Confirm the selected time slot"""
        self.actions.button_click(self.text_request_appointment, "Confirm Slot")
        return self

    def proceed_to_next(self):
        """Click Next button"""
        self.actions.button_click(self.button_next, "Next")
        return self

    def click_next(self):
        """Click Next button to proceed after selecting time slot (alias for proceed_to_next)"""
        return self.proceed_to_next()

    # ===================================================================
    # PAGE-LEVEL CHECKS
    # ===================================================================

    def is_scheduler_loaded(self) -> bool:
        """Check if scheduler calendar is loaded (no wait logic)"""
        try:
            return self.time_slots_am_pm.is_visible()
        except:
            return False

    def are_slots_available(self) -> bool:
        """Check if time slots are available"""
        try:
            return self.time_slots_am_pm.count() > 0 or self.time_slots_any.count() > 0
        except:
            return False
