"""
Patient Type Selection Page Object
Handles patient type selection (New Patient, Existing Patient)
"""
from playwright.sync_api import Page
from utils.smart_actions import SmartActions


class BookslotPatientTypePage:
    """Patient Type Selection Page Object"""
    
    def __init__(self, page: Page):
        """Initialize the patient type page
        
        Args:
            page: Playwright Page instance
        """
        self.page = page
        self.actions = SmartActions(page)
    
    def select_new_patient(self) -> None:
        """Select 'New Patient' option"""
        self.actions.button_click(
            self.page.get_by_role("button", name="New Patient"),
            "New Patient"
        )
    
    def select_existing_patient(self) -> None:
        """Select 'Existing Patient' option"""
        self.actions.button_click(
            self.page.get_by_role("button", name="Existing Patient"),
            "Existing Patient"
        )
    
    def click_next(self) -> None:
        """Click Next button to proceed to scheduler"""
        self.actions.button_click(
            self.page.get_by_role("button", name="Next"),
            "Next"
        )
