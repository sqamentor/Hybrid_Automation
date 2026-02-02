"""
Page Object: Bookslot Event Type Selection Page
Represents what a user can do on the Event Type page

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

Project: BookSlot
Module: Event Type Selection (Appointment Type) & Patient Type Selection

Responsibilities:
✔ Locators for event type elements
✔ Locators for patient type elements
✔ Actions (select event, select patient type, book appointment)
✔ Page-level checks
✔ Navigation

Does NOT contain:
❌ Test data
❌ Business rule assertions
❌ API/DB validation
❌ pytest markers
❌ Complete test flows
"""

from playwright.sync_api import Page
from framework.core.smart_actions import SmartActions


class BookslotEventInfoPage:
    """
    Page Object for Bookslot Event Type Selection Page

    What a user can do on this page:
    - Navigate to event type page
    - Request callback
    - Select patient type (New Patient, Existing Patient)
    - Select appointment type (New Patient, Complimentary Consultation, etc.)
    - Book appointment
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
        self.path = "/eventtype"

    # ===================================================================
    # LOCATORS - PATIENT TYPE
    # ===================================================================

    @property
    def button_new_patient_type(self):
        """New Patient type selection button"""
        return self.page.get_by_role("button", name="New Patient")

    @property
    def button_existing_patient_type(self):
        """Existing Patient type selection button"""
        return self.page.get_by_role("button", name="Existing Patient")

    # ===================================================================
    # LOCATORS - EVENT TYPE
    # ===================================================================

    @property
    def button_request_callback(self):
        """Request Call back button"""
        return self.page.get_by_role("button", name="Request Call back")

    @property
    def text_callback_confirmation(self):
        """Callback request submission confirmation"""
        return self.page.get_by_text("Request has been submitted")

    @property
    def heading_new_patient(self):
        """New Patient Appointment heading"""
        return self.page.get_by_role("heading", name="New Patient Appointment")

    @property
    def text_new_patient_details(self):
        """New Patient appointment details"""
        return self.page.get_by_text("90-minute appointment with")

    @property
    def button_new_patient_book(self):
        """Book Now button for New Patient"""
        return self.page.get_by_role("button", name="Book Now").first

    @property
    def heading_complimentary(self):
        """Complimentary Consultation heading"""
        return self.page.get_by_role("heading", name="Complimentary Consultation")

    @property
    def text_complimentary_details(self):
        """Complimentary Consultation details"""
        return self.page.get_by_text("15-minute appointmentwith a")

    @property
    def button_complimentary_book(self):
        """Book Now button for Complimentary Consultation"""
        return self.page.get_by_role("button", name="Book Now").nth(1)

    @property
    def button_next(self):
        """Next button to proceed"""
        return self.page.get_by_role("button", name="Next")

    # ===================================================================
    # NAVIGATION
    # ===================================================================

    def navigate(self):
        """Navigate to the event type page"""
        url = f"{self.base_url}{self.path}"
        self.page.goto(url)
        return self

    # ===================================================================
    # ACTIONS - PATIENT TYPE
    # ===================================================================

    def select_new_patient_type(self):
        """Select 'New Patient' patient type option"""
        self.actions.button_click(self.button_new_patient_type, "New Patient Type")
        return self

    def select_existing_patient_type(self):
        """Select 'Existing Patient' patient type option"""
        self.actions.button_click(self.button_existing_patient_type, "Existing Patient Type")
        return self

    # ===================================================================
    # ACTIONS - EVENT TYPE
    # ===================================================================

    def request_callback(self):
        """Request a callback from the clinic"""
        self.button_request_callback.click()
        return self

    def select_new_patient(self):
        """Select New Patient appointment type"""
        self.heading_new_patient.click()
        self.text_new_patient_details.click()
        self.button_new_patient_book.click()
        return self

    def select_complimentary_consultation(self):
        """Select Complimentary Consultation type"""
        self.heading_complimentary.click()
        self.text_complimentary_details.click()
        self.button_complimentary_book.click()
        return self

    def select_event_by_name(self, event_name: str):
        """
        Select any event type by button name

        Args:
            event_name: Name of the event button (e.g., "New Patient", "Complimentary Consultation")
        """
        self.page.get_by_role("button", name=event_name).click()
        return self

    def is_event_button_visible(self, event_name: str) -> bool:
        """
        Check if an event button is visible

        Args:
            event_name: Name of the event button

        Returns:
            bool: True if visible, False otherwise
        """
        try:
            return self.page.get_by_role("button", name=event_name).is_visible()
        except:
            return False

    def proceed_to_next(self):
        """Click Next button"""
        self.button_next.click()
        return self

    # ===================================================================
    # PAGE-LEVEL CHECKS
    # ===================================================================

    def is_page_loaded(self) -> bool:
        """Check if page is loaded"""
        try:
            return self.heading_new_patient.is_visible()
        except:
            return False

    def is_callback_confirmed(self) -> bool:
        """Check if callback request was confirmed"""
        try:
            return self.text_callback_confirmation.is_visible()
        except:
            return False
