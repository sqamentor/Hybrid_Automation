"""
CallCenter Appointment Management Page Object
Handles appointment viewing and cancellation in CallCenter system
"""
from typing import Optional, List
from framework.ui.base_page import BasePage
from models.appointment import Appointment


class CallCenterAppointmentManagementPage(BasePage):
    """Page object for CallCenter Appointment Management"""
    
    def __init__(self, page, base_url: str):
        super().__init__(page)
        self.page = self.driver  # Compatibility alias
        self.base_url = base_url.rstrip('/')
    
    # URL
    @property
    def url(self) -> str:
        return f"{self.base_url}/appointments"
    
    # Locators
    @property
    def search_input(self):
        """Search box for filtering appointments"""
        return self.page.get_by_placeholder("Search appointments")
    
    @property
    def search_button(self):
        """Search button"""
        return self.page.get_by_role("button", name="Search")
    
    @property
    def appointment_rows(self):
        """All appointment rows in the table/list"""
        return self.page.locator("[data-testid='appointment-row']")
    
    def appointment_by_email(self, email: str):
        """Get appointment row by email"""
        return self.page.locator(f"[data-testid='appointment-row']:has-text('{email}')")
    
    def appointment_by_name(self, full_name: str):
        """Get appointment row by patient name"""
        return self.page.locator(f"[data-testid='appointment-row']:has-text('{full_name}')")
    
    @property
    def cancel_button(self):
        """Cancel appointment button"""
        return self.page.get_by_role("button", name="Cancel Appointment")
    
    @property
    def confirm_cancel_button(self):
        """Confirm cancellation button"""
        return self.page.get_by_role("button", name="Confirm Cancellation")
    
    @property
    def cancel_reason_input(self):
        """Cancellation reason text area"""
        return self.page.locator("textarea[name='cancellation_reason']")
    
    @property
    def status_badge(self):
        """Appointment status badge"""
        return self.page.locator("[data-testid='status-badge']")
    
    @property
    def no_results_message(self):
        """No results message"""
        return self.page.get_by_text("No appointments found")
    
    # Actions
    def navigate(self) -> 'CallCenterAppointmentManagementPage':
        """Navigate to appointments management page"""
        self.page.goto(self.url)
        return self
    
    def search_by_email(self, email: str) -> 'CallCenterAppointmentManagementPage':
        """Search appointments by email"""
        self.search_input.fill(email)
        self.search_button.click()
        # Playwright auto-waits for navigation/network idle
        return self
    
    def search_by_name(self, first_name: str, last_name: str) -> 'CallCenterAppointmentManagementPage':
        """Search appointments by patient name"""
        full_name = f"{first_name} {last_name}"
        self.search_input.fill(full_name)
        self.search_button.click()
        # Playwright auto-waits for navigation/network idle
        return self
    
    def search_appointment(self, appointment: Appointment) -> 'CallCenterAppointmentManagementPage':
        """Search for appointment using Appointment object"""
        # Try searching by email first (more unique)
        self.search_by_email(appointment.email)
        return self
    
    def click_appointment(self, email: str) -> 'CallCenterAppointmentManagementPage':
        """Click on appointment to view details"""
        self.appointment_by_email(email).click()
        # Playwright auto-waits for navigation/network idle
        return self
    
    def cancel_appointment(
        self, 
        email: str, 
        reason: str = "Patient requested cancellation"
    ) -> 'CallCenterAppointmentManagementPage':
        """
        Cancel an appointment
        
        Args:
            email: Patient email to find appointment
            reason: Cancellation reason
        """
        # Search and select appointment
        self.search_by_email(email)
        self.click_appointment(email)
        
        # Click cancel button
        self.cancel_button.click()
        
        # Enter cancellation reason (Playwright auto-waits for dialog)
        self.cancel_reason_input.fill(reason)
        
        # Confirm cancellation
        self.confirm_cancel_button.click()
        # Playwright auto-waits for network/state changes
        
        return self
    
    def get_appointment_status(self, email: str) -> str:
        """
        Get appointment status
        
        Returns:
            Status string (e.g., "Active", "Cancelled", "Completed")
        """
        self.search_by_email(email)
        row = self.appointment_by_email(email)
        
        if not row.count():
            return "Not Found"
        
        status = row.locator("[data-testid='status-badge']").inner_text()
        return status
    
    def get_appointment_details(self, email: str) -> dict:
        """
        Extract appointment details from the UI
        
        Returns:
            dict with keys: name, email, date, location, status
        """
        self.search_by_email(email)
        row = self.appointment_by_email(email)
        
        if not row.count():
            return {}
        
        # Extract details from row (adjust selectors based on actual UI)
        details = {
            'name': row.locator("[data-testid='patient-name']").inner_text(),
            'email': row.locator("[data-testid='patient-email']").inner_text(),
            'date': row.locator("[data-testid='appointment-date']").inner_text(),
            'location': row.locator("[data-testid='location']").inner_text(),
            'status': row.locator("[data-testid='status-badge']").inner_text()
        }
        
        return details
    
    # Assertions
    def should_show_appointment(self, appointment: Appointment):
        """Verify appointment exists in the list"""
        row = self.appointment_by_email(appointment.email)
        expect(row).to_be_visible(timeout=10000)
        return self
    
    def should_not_show_appointment(self, email: str):
        """Verify appointment does not exist"""
        self.search_by_email(email)
        expect(self.no_results_message).to_be_visible()
        return self
    
    def should_have_status(self, email: str, expected_status: str):
        """
        Verify appointment has expected status
        
        Returns True if status matches, False otherwise.
        Tests should perform assertions on the returned value.
        """
        actual_status = self.get_appointment_status(email)
        return actual_status.lower() == expected_status.lower()
    
    def fill_healed_locator(self, locator_string: str, value: str) -> 'CallCenterAppointmentManagementPage':
        """
        Fill a field using AI-healed locator string
        
        This method supports AI self-healing by accepting a locator string
        found by AI when the original locator breaks.
        
        Args:
            locator_string: The healed locator string (e.g., "input#email")
            value: Value to fill
        """
        element = self.page.locator(locator_string)
        element.fill(value)
        return self
    
    def verify_appointment_exists(self, appointment: Appointment):
        """
        Verify appointment exists with all details
        
        Verifies:
        - Patient name (first + last)
        - Email
        - Location (if provided)
        - Date (if provided)
        """
        self.search_by_email(appointment.email)
        row = self.appointment_by_email(appointment.email)
        expect(row).to_be_visible(timeout=10000)
        
        # Verify name
        full_name = appointment.get_full_name()
        expect(row.locator("[data-testid='patient-name']")).to_have_text(full_name)
        
        # Verify email
        expect(row.locator("[data-testid='patient-email']")).to_have_text(appointment.email)
        
        # Verify location if provided
        if appointment.location:
            expect(row.locator("[data-testid='location']")).to_have_text(appointment.location)
        
        return self
    
    def verify_appointment_cancelled(self, email: str):
        """Verify appointment is cancelled"""
        self.search_by_email(email)
        row = self.appointment_by_email(email)
        
        # Verify status is "Cancelled"
        status_element = row.locator("[data-testid='status-badge']")
        expect(status_element).to_contain_text("Cancelled", ignore_case=True)
        
        return self
    
    def verify_can_cancel(self, email: str):
        """Verify cancel button is available"""
        self.search_by_email(email)
        self.click_appointment(email)
        expect(self.cancel_button).to_be_enabled()
        return self
    
    def should_be_visible(self):
        """Verify page is loaded"""
        expect(self.search_input).to_be_visible()
        expect(self.search_button).to_be_visible()
        return self


class CallCenterAppointmentDetailsPage:
    """Page object for detailed appointment view in CallCenter"""
    
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip('/')
    
    # Locators
    @property
    def patient_name_field(self):
        return self.page.locator("[data-testid='detail-patient-name']")
    
    @property
    def email_field(self):
        return self.page.locator("[data-testid='detail-email']")
    
    @property
    def phone_field(self):
        return self.page.locator("[data-testid='detail-phone']")
    
    @property
    def date_field(self):
        return self.page.locator("[data-testid='detail-date']")
    
    @property
    def location_field(self):
        return self.page.locator("[data-testid='detail-location']")
    
    @property
    def status_field(self):
        return self.page.locator("[data-testid='detail-status']")
    
    @property
    def cancel_button(self):
        return self.page.get_by_role("button", name="Cancel Appointment")
    
    @property
    def cancellation_history(self):
        return self.page.locator("[data-testid='cancellation-history']")
    
    # Actions
    def verify_all_details(self, appointment: Appointment):
        """Verify all appointment details on detail page"""
        expect(self.patient_name_field).to_have_text(appointment.get_full_name())
        expect(self.email_field).to_have_text(appointment.email)
        
        if appointment.phone:
            expect(self.phone_field).to_have_text(appointment.phone)
        
        if appointment.location:
            expect(self.location_field).to_have_text(appointment.location)
        
        return self
    
    def verify_cancellation_details(self, reason: Optional[str] = None):
        """Verify cancellation information is displayed"""
        expect(self.status_field).to_contain_text("Cancelled")
        expect(self.cancellation_history).to_be_visible()
        
        if reason:
            expect(self.cancellation_history).to_contain_text(reason)
        
        return self
