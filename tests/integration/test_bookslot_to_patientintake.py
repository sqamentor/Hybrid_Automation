"""
Integration Test: Bookslot to PatientIntake
Tests cross-application data flow: Book appointment in Bookslot, verify in PatientIntake
"""
from datetime import datetime

import pytest

from models import Appointment


@pytest.mark.modern_spa
class TestBookslotToPatientIntake:
    """Test suite for Bookslot → PatientIntake integration"""
    
    @pytest.mark.human_like
    def test_book_appointment_and_verify_in_patientintake(
        self, 
        test_context, 
        bookslot_page, 
        patientintake_page
    ):
        """
        Test: Book appointment in Bookslot and verify it appears in PatientIntake
        
        Flow:
        1. Create appointment data
        2. Navigate to Bookslot and fill patient info
        3. Submit appointment
        4. Navigate to PatientIntake
        5. Search for appointment by email
        6. Verify all details match (name, email, date, location)
        """
        
        # Step 1: Create appointment with test data
        appointment = Appointment(
            first_name="Lokendra",
            last_name="Singh",
            email=f"test.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
            phone="1234567890",
            zip_code="20678",
            location="Center for Vein - Main",
            appointment_date=datetime.now()
        )
        
        # Store in context
        test_context.add_appointment(appointment)
        
        # Step 2: Book appointment in Bookslot
        bookslot_page.navigate() \
            .should_be_visible() \
            .fill_patient_info(appointment) \
            .send_verification_code() \
            .should_show_verification_sent()
        
        # Note: In real scenario, you would get verification code from email/SMS
        # For testing, you might skip verification or use a test code
        # bookslot_page.enter_verification_code("123456").verify_code()
        
        # bookslot_page.click_book_now()
        
        # Step 3: Navigate to PatientIntake and verify appointment exists
        patientintake_page.navigate() \
            .should_be_visible() \
            .search_appointment(appointment) \
            .should_show_appointment(appointment)
        
        # Step 4: Verify all appointment details
        patientintake_page.verify_appointment_details(appointment)
        
        # Step 5: Verify patient name specifically
        patientintake_page.verify_patient_name(
            appointment.first_name, 
            appointment.last_name
        )
    
    
    @pytest.mark.human_like
    def test_multiple_appointments_data_consistency(
        self,
        test_context,
        bookslot_page,
        patientintake_page
    ):
        """
        Test: Book multiple appointments and verify data consistency
        
        Tests:
        - Multiple appointments can be created
        - Each appointment maintains unique data
        - All appointments appear in PatientIntake
        """
        
        appointments = [
            Appointment(
                first_name="John",
                last_name="Doe",
                email=f"john.doe.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
                location="Center for Vein - Main"
            ),
            Appointment(
                first_name="Jane",
                last_name="Smith",
                email=f"jane.smith.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
                location="Center for Vein - Branch"
            )
        ]
        
        # Book all appointments in Bookslot
        for appointment in appointments:
            test_context.add_appointment(appointment)
            
            bookslot_page.navigate() \
                .fill_patient_info(appointment) \
                .send_verification_code()
            
            # Skip verification for testing
            # bookslot_page.click_book_now()
        
        # Verify all appointments in PatientIntake
        for appointment in appointments:
            patientintake_page.navigate() \
                .search_appointment(appointment) \
                .should_show_appointment(appointment) \
                .verify_appointment_details(appointment)
    
    
    @pytest.mark.human_like
    def test_appointment_with_full_details(
        self,
        test_context,
        bookslot_page,
        patientintake_page
    ):
        """
        Test: Book appointment with complete details and verify
        
        Verifies:
        - First Name
        - Last Name
        - Email
        - Phone
        - Zip Code
        - Appointment Date
        - Location
        """
        
        appointment = Appointment(
            first_name="Michael",
            last_name="Johnson",
            email=f"michael.j.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
            phone="5551234567",
            zip_code="12345",
            appointment_date=datetime(2024, 12, 15, 10, 30),
            location="Center for Vein - Downtown",
            reason="Initial Consultation"
        )
        
        test_context.add_appointment(appointment)
        
        # Book in Bookslot with all details
        bookslot_page.navigate() \
            .fill_first_name(appointment.first_name) \
            .fill_last_name(appointment.last_name) \
            .fill_email(appointment.email) \
            .fill_phone(appointment.phone) \
            .fill_zip_code(appointment.zip_code) \
            .send_verification_code()
        
        # Verify in PatientIntake
        patientintake_page.navigate() \
            .search_by_email(appointment.email) \
            .should_show_appointment(appointment)
        
        # Get appointment details from UI and verify
        ui_details = patientintake_page.get_appointment_details(appointment.email)
        
        assert ui_details['name'] == appointment.get_full_name(), \
            f"Name mismatch: expected {appointment.get_full_name()}, got {ui_details['name']}"
        
        assert ui_details['email'] == appointment.email, \
            f"Email mismatch: expected {appointment.email}, got {ui_details['email']}"
        
        if appointment.location:
            assert ui_details['location'] == appointment.location, \
                f"Location mismatch: expected {appointment.location}, got {ui_details['location']}"


@pytest.mark.integration
@pytest.mark.multi_project
@pytest.mark.modern_spa
class TestCrossApplicationWorkflow:
    """Advanced cross-application workflow tests"""
    
    @pytest.mark.human_like
    def test_end_to_end_patient_journey(
        self,
        test_context,
        bookslot_page,
        patientintake_page
    ):
        """
        Complete patient journey across both systems
        
        Journey:
        1. Patient books appointment (Bookslot)
        2. Appointment appears in PatientIntake
        3. Staff verifies appointment details (PatientIntake)
        4. Patient information is consistent across systems
        """
        
        # Create patient
        appointment = Appointment(
            first_name="Sarah",
            last_name="Williams",
            email=f"sarah.w.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
            phone="5559876543",
            zip_code="98765",
            appointment_date=datetime.now(),
            location="Center for Vein - Main",
            reason="Follow-up Appointment"
        )
        
        test_context.add_appointment(appointment)
        
        # Patient books appointment
        bookslot_page.navigate() \
            .complete_form(appointment) \
            .should_show_verification_sent()
        
        # Staff searches for appointment in PatientIntake
        patientintake_page.navigate() \
            .search_by_name(appointment.first_name, appointment.last_name) \
            .should_show_appointment(appointment)
        
        # Verify all details match
        patientintake_page.verify_appointment_details(appointment)
        
        # Click to view full details
        patientintake_page.click_appointment(appointment.email)
        
        # Verify on details page
        from pages.patientintake import PatientIntakeAppointmentDetailsPage
        details_page = PatientIntakeAppointmentDetailsPage(
            patientintake_page.page,
            patientintake_page.base_url
        )
        details_page.verify_all_details(appointment)
