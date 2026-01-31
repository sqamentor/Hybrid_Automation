"""
Scheduler Page Object
Handles time slot selection for appointments
"""
from playwright.sync_api import Page, Locator
from utils.smart_actions import SmartActions


class BookslotSchedulerPage:
    """Scheduler Page Object for time slot selection"""
    
    def __init__(self, page: Page):
        """Initialize the scheduler page
        
        Args:
            page: Playwright Page instance
        """
        self.page = page
        self.actions = SmartActions(page)
    
    def wait_for_scheduler_ready(self) -> None:
        """Wait for scheduler to be ready for interaction"""
        self.actions.wait_for_scheduler(self.page)
    
    def select_am_slot(self) -> None:
        """Select the first available AM time slot"""
        self.actions.button_click(
            self.page.locator("button:has-text('AM')").first,
            "AM Slot"
        )
    
    def select_pm_slot(self) -> None:
        """Select the first available PM time slot"""
        self.actions.button_click(
            self.page.locator("button:has-text('PM')").first,
            "PM Slot"
        )
    
    def select_first_available_slot(self) -> None:
        """Select the first available time slot (AM or PM)"""
        # Try AM first
        am_slots = self.page.locator("button:has-text('AM')")
        if am_slots.count() > 0:
            self.select_am_slot()
        else:
            self.select_pm_slot()
    
    def click_next(self) -> None:
        """Click Next button to proceed after selecting time slot"""
        self.actions.button_click(
            self.page.get_by_role("button", name="Next"),
            "Next"
        )
