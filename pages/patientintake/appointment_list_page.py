"""
PatientIntake Appointment List Page Object
Handles appointment verification and search in PatientIntake system
"""
from typing import Optional, List
from playwright.sync_api import Page, expect
from models.appointment import Appointment


class PatientIntakeAppointmentListPage:
    """Page object for PatientIntake Appointment List"""
    
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip('/')
    
    # URL
    @property
    def url(self) -> str:
        return f"{self.base_url}/appointments"
    
    # Locators
    @property
    def search_input(self):
        """Search box for filtering appointments"""
        return self.page.get_by_placeholder("Search by name, email")
    
    @property
    def appointment_rows(self):
        """All appointment rows in the table/list"""
        return self.page.locator("[data-testid='appointment-row']")
    
    def appointment_by_name(self, full_name: str):
        """Get appointment row by patient name"""
        return self.page.locator(f"[data-testid='appointment-row']:has-text('{full_name}')")
    
    def appointment_by_email(self, email: str):
        """Get appointment row by email"""
        return self.page.locator(f"[data-testid='appointment-row']:has-text('{email}')")
    
    @property
    def no_results_message(self):
        """No results message"""
        return self.page.get_by_text("No appointments found")
    
    # Actions
    def navigate(self) -> 'PatientIntakeAppointmentListPage':
        """Navigate to appointments list page"""
        self.page.goto(self.url)
        return self
    
    def search_by_name(self, first_name: str, last_name: str) -> 'PatientIntakeAppointmentListPage':
        """Search appointments by patient name"""
        full_name = f"{first_name} {last_name}"
        self.search_input.fill(full_name)
        # Playwright auto-waits for search results to load
        return self
    
    def search_by_email(self, email: str) -> 'PatientIntakeAppointmentListPage':
        """Search appointments by email"""
        self.search_input.fill(email)
        # Playwright auto-waits for search results to load
        return self
    
    def search_appointment(self, appointment: Appointment) -> 'PatientIntakeAppointmentListPage':
        """Search for appointment using Appointment object"""
        # Try searching by email first (more unique)
        self.search_by_email(appointment.email)
        return self
    
    def get_appointment_details(self, email: str) -> dict:
        """
        Extract appointment details from the UI
        
        Returns:
            dict with keys: name, email, date, location, status
        """
        row = self.appointment_by_email(email)
        
        if not row.count():
            return {}
        
        # Extract details from row
        # Adjust selectors based on actual UI structure
        details = {
            'name': row.locator("[data-testid='patient-name']").inner_text(),
            'email': row.locator("[data-testid='patient-email']").inner_text(),
            'date': row.locator("[data-testid='appointment-date']").inner_text(),
            'location': row.locator("[data-testid='location']").inner_text(),
            'status': row.locator("[data-testid='status']").inner_text()
        }
        
        return details
    
    def click_appointment(self, email: str) -> 'PatientIntakeAppointmentListPage':
        """Click on appointment to view details"""
        self.appointment_by_email(email).click()
        return self
    
    # Assertions
    def should_show_appointment(self, appointment: Appointment):
        """Verify appointment exists in the list"""
        row = self.appointment_by_email(appointment.email)
        expect(row).to_be_visible(timeout=10000)
        return self
    
    def should_not_show_appointment(self, email: str):
        """Verify appointment does not exist"""
        row = self.appointment_by_email(email)
        expect(row).not_to_be_visible()
        return self
    
    def verify_appointment_details(self, appointment: Appointment):
        """
        Verify all appointment details match
        
        Verifies:
        - Patient name (first + last)
        - Email
        - Date (if provided)
        - Location (if provided)
        """
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
        
        # Verify date if provided
        if appointment.appointment_date:
            # Format date based on UI display format
            expected_date = appointment.appointment_date.strftime("%m/%d/%Y")
            expect(row.locator("[data-testid='appointment-date']")).to_contain_text(expected_date)
        
        return self
    
    def verify_patient_name(self, first_name: str, last_name: str):
        """Verify patient name appears in list"""
        full_name = f"{first_name} {last_name}"
        row = self.appointment_by_name(full_name)
        expect(row).to_be_visible()
        return self
    
    def should_be_visible(self):
        """Verify page is loaded"""
        expect(self.search_input).to_be_visible()
        return self


class PatientIntakeAppointmentDetailsPage:
    """Page object for detailed appointment view"""
    
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
