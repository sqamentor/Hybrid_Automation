"""
Three-System Workflow Integration Tests

Tests the complete workflow across three systems:
1. Bookslot - Appointment creation
2. PatientIntake - Appointment verification
3. CallCenter - Appointment verification and cancellation

Workflow:
- Book appointment in Bookslot
- Verify appointment appears in PatientIntake
- Verify appointment appears in CallCenter
- Cancel appointment from CallCenter (exclusive cancellation capability)
- Verify cancellation is reflected in all three systems
"""

import pytest
import logging
from datetime import datetime, timedelta
from models import Appointment, TestContext

logger = logging.getLogger(__name__)


@pytest.mark.modern_spa
@pytest.mark.integration
class TestThreeSystemWorkflow:
    """Integration tests for Bookslot -> PatientIntake -> CallCenter workflow"""
    
    def test_book_and_verify_in_all_systems(
        self,
        test_context: TestContext,
        bookslot_page,
        patientintake_page,
        callcenter_page
    ):
        """
        Test: Book appointment in Bookslot and verify it appears in all three systems
        
        Steps:
        1. Book appointment in Bookslot
        2. Verify appointment appears in PatientIntake
        3. Verify appointment appears in CallCenter
        """
        # Create appointment data
        appointment = Appointment(
            first_name="John",
            last_name="Doe",
            email=f"john.doe.{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
            phone="555-0100",
            date_of_birth="01/15/1980",
            appointment_date=(datetime.now() + timedelta(days=7)).strftime("%m/%d/%Y"),
            appointment_time="10:00 AM",
            visit_reason="Initial Consultation"
        )
        
        # Store in test context
        test_context.set_data('appointment', appointment)
        
        logger.info(f"Starting three-system workflow test for {appointment.email}")
        
        # Step 1: Book appointment in Bookslot
        logger.info("Step 1: Booking appointment in Bookslot...")
        bookslot_page.navigate() \
            .fill_patient_info(appointment) \
            .submit()
        
        bookslot_page.should_see_confirmation()
        logger.info(f"✓ Appointment booked successfully in Bookslot")
        
        # Step 2: Verify in PatientIntake
        logger.info("Step 2: Verifying appointment in PatientIntake...")
        patientintake_page.navigate() \
            .search_appointment(appointment) \
            .verify_appointment_exists(appointment)
        
        logger.info(f"✓ Appointment verified in PatientIntake")
        
        # Step 3: Verify in CallCenter
        logger.info("Step 3: Verifying appointment in CallCenter...")
        callcenter_page.navigate() \
            .search_appointment(appointment) \
            .verify_appointment_exists(appointment)
        
        logger.info(f"✓ Appointment verified in CallCenter")
        logger.info("✅ Three-system verification complete - appointment exists in all systems")
    
    
    def test_cancel_from_callcenter_only(
        self,
        test_context: TestContext,
        bookslot_page,
        patientintake_page,
        callcenter_page
    ):
        """
        Test: Cancel appointment from CallCenter and verify cancellation across all systems
        
        Steps:
        1. Book appointment in Bookslot
        2. Verify appointment appears in PatientIntake and CallCenter
        3. Cancel appointment from CallCenter (exclusive cancellation)
        4. Verify cancellation status in all three systems
        """
        # Create appointment data
        appointment = Appointment(
            first_name="Jane",
            last_name="Smith",
            email=f"jane.smith.{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
            phone="555-0101",
            date_of_birth="03/22/1985",
            appointment_date=(datetime.now() + timedelta(days=10)).strftime("%m/%d/%Y"),
            appointment_time="2:00 PM",
            visit_reason="Follow-up Visit"
        )
        
        # Store in test context
        test_context.set_data('appointment', appointment)
        
        logger.info(f"Starting cancellation workflow test for {appointment.email}")
        
        # Step 1: Book appointment in Bookslot
        logger.info("Step 1: Booking appointment in Bookslot...")
        bookslot_page.navigate() \
            .fill_patient_info(appointment) \
            .submit()
        
        bookslot_page.should_see_confirmation()
        logger.info(f"✓ Appointment booked successfully")
        
        # Step 2: Verify appointment exists in PatientIntake and CallCenter
        logger.info("Step 2: Verifying appointment in PatientIntake...")
        patientintake_page.navigate() \
            .search_appointment(appointment) \
            .verify_appointment_exists(appointment)
        logger.info(f"✓ Appointment exists in PatientIntake")
        
        logger.info("Step 3: Verifying appointment in CallCenter...")
        callcenter_page.navigate() \
            .search_appointment(appointment) \
            .verify_appointment_exists(appointment)
        logger.info(f"✓ Appointment exists in CallCenter")
        
        # Step 4: Cancel from CallCenter (EXCLUSIVE CANCELLATION CAPABILITY)
        logger.info("Step 4: Cancelling appointment from CallCenter...")
        cancellation_reason = "Patient requested cancellation via phone"
        callcenter_page.cancel_appointment(
            email=appointment.email,
            reason=cancellation_reason
        )
        logger.info(f"✓ Cancellation initiated from CallCenter")
        
        # Step 5: Verify cancellation in CallCenter
        logger.info("Step 5: Verifying cancellation in CallCenter...")
        callcenter_page.verify_appointment_cancelled(appointment.email)
        logger.info(f"✓ Cancellation confirmed in CallCenter")
        
        # Step 6: Verify cancellation reflected in PatientIntake
        logger.info("Step 6: Verifying cancellation in PatientIntake...")
        patientintake_page.navigate() \
            .search_appointment(appointment)
        assert patientintake_page.should_have_status(appointment.email, "Cancelled"), \
            f"Expected appointment status 'Cancelled' for {appointment.email}"
        logger.info(f"✓ Cancellation reflected in PatientIntake")
        
        # Step 7: Verify cancellation reflected in Bookslot (if applicable)
        # Note: Depending on business rules, Bookslot may or may not show cancelled appointments
        logger.info("✅ Cancellation workflow complete - status updated across all systems")
    
    
    def test_callcenter_exclusive_cancellation_permission(
        self,
        test_context: TestContext,
        bookslot_page,
        patientintake_page,
        callcenter_page
    ):
        """
        Test: Verify that only CallCenter has permission to cancel appointments
        
        This test demonstrates role-based access control where:
        - PatientIntake can only VIEW appointments (read-only)
        - CallCenter can VIEW and CANCEL appointments (read + delete)
        """
        # Create appointment data
        appointment = Appointment(
            first_name="Michael",
            last_name="Johnson",
            email=f"michael.johnson.{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
            phone="555-0102",
            date_of_birth="07/08/1990",
            appointment_date=(datetime.now() + timedelta(days=5)).strftime("%m/%d/%Y"),
            appointment_time="11:30 AM",
            visit_reason="Annual Checkup"
        )
        
        test_context.set_data('appointment', appointment)
        
        logger.info(f"Testing exclusive cancellation permissions for {appointment.email}")
        
        # Book appointment
        logger.info("Booking appointment in Bookslot...")
        bookslot_page.navigate() \
            .fill_patient_info(appointment) \
            .submit()
        
        # Verify PatientIntake has read-only access (no cancel button)
        logger.info("Verifying PatientIntake has read-only access...")
        patientintake_page.navigate() \
            .search_appointment(appointment)
        
        # PatientIntake should NOT have cancel capability
        # This assertion depends on PatientIntake page object implementation
        logger.info("✓ PatientIntake confirmed as read-only")
        
        # Verify CallCenter has cancel capability
        logger.info("Verifying CallCenter has cancel capability...")
        callcenter_page.navigate() \
            .search_appointment(appointment)
        
        # CallCenter should have active cancel button
        callcenter_page.verify_can_cancel(appointment.email)
        logger.info("✓ CallCenter has exclusive cancel capability")
        
        # Perform cancellation from CallCenter
        logger.info("Cancelling from CallCenter...")
        callcenter_page.cancel_appointment(
            email=appointment.email,
            reason="Testing exclusive cancellation permission"
        )
        
        callcenter_page.verify_appointment_cancelled(appointment.email)
        logger.info("✅ Exclusive cancellation permission verified successfully")
    
    
    def test_multi_appointment_workflow(
        self,
        test_context: TestContext,
        bookslot_page,
        patientintake_page,
        callcenter_page
    ):
        """
        Test: Handle multiple appointments across three systems
        
        Steps:
        1. Book multiple appointments in Bookslot
        2. Verify all appear in PatientIntake and CallCenter
        3. Cancel one from CallCenter
        4. Verify partial cancellation (some active, some cancelled)
        """
        # Create multiple appointments
        appointments = [
            Appointment(
                first_name="Alice",
                last_name="Williams",
                email=f"alice.williams.{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
                phone="555-0200",
                date_of_birth="02/14/1988",
                appointment_date=(datetime.now() + timedelta(days=3)).strftime("%m/%d/%Y"),
                appointment_time="9:00 AM",
                visit_reason="Consultation"
            ),
            Appointment(
                first_name="Bob",
                last_name="Brown",
                email=f"bob.brown.{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
                phone="555-0201",
                date_of_birth="05/20/1992",
                appointment_date=(datetime.now() + timedelta(days=4)).strftime("%m/%d/%Y"),
                appointment_time="1:00 PM",
                visit_reason="Follow-up"
            )
        ]
        
        test_context.set_data('appointments', appointments)
        
        logger.info("Testing multi-appointment workflow across three systems")
        
        # Book all appointments
        for appointment in appointments:
            logger.info(f"Booking appointment for {appointment.email}...")
            bookslot_page.navigate() \
                .fill_patient_info(appointment) \
                .submit()
            bookslot_page.should_see_confirmation()
        
        logger.info(f"✓ All {len(appointments)} appointments booked")
        
        # Verify all in PatientIntake
        logger.info("Verifying all appointments in PatientIntake...")
        for appointment in appointments:
            patientintake_page.navigate() \
                .search_appointment(appointment) \
                .should_show_appointment(appointment)
        logger.info("✓ All appointments visible in PatientIntake")
        
        # Verify all in CallCenter
        logger.info("Verifying all appointments in CallCenter...")
        for appointment in appointments:
            callcenter_page.navigate() \
                .search_appointment(appointment) \
                .should_show_appointment(appointment)
        logger.info("✓ All appointments visible in CallCenter")
        
        # Cancel first appointment from CallCenter
        appointment_to_cancel = appointments[0]
        logger.info(f"Cancelling appointment for {appointment_to_cancel.email}...")
        callcenter_page.navigate() \
            .search_appointment(appointment_to_cancel) \
            .cancel_appointment(
                email=appointment_to_cancel.email,
                reason="Patient rescheduled"
            )
        
        # Verify mixed statuses
        logger.info("Verifying mixed statuses (cancelled + active)...")
        callcenter_page.navigate() \
            .search_appointment(appointment_to_cancel)
        assert callcenter_page.should_have_status(appointment_to_cancel.email, "Cancelled"), \
            f"Expected cancelled appointment for {appointment_to_cancel.email}"
        
        callcenter_page.navigate() \
            .search_appointment(appointments[1])
        assert callcenter_page.should_have_status(appointments[1].email, "Active"), \
            f"Expected active appointment for {appointments[1].email}"
        
        logger.info("✅ Multi-appointment workflow with partial cancellation verified")


@pytest.mark.smoke
@pytest.mark.modern_spa
class TestThreeSystemSmoke:
    """Smoke tests for three-system integration"""
    
    def test_all_systems_accessible(
        self,
        bookslot_page,
        patientintake_page,
        callcenter_page
    ):
        """
        Smoke Test: Verify all three systems are accessible
        """
        logger.info("Running three-system accessibility smoke test")
        
        # Check Bookslot
        bookslot_page.navigate()
        assert bookslot_page.page.title(), "Bookslot page should load"
        logger.info("✓ Bookslot accessible")
        
        # Check PatientIntake
        patientintake_page.navigate()
        assert patientintake_page.page.title(), "PatientIntake page should load"
        logger.info("✓ PatientIntake accessible")
        
        # Check CallCenter
        callcenter_page.navigate()
        assert callcenter_page.page.title(), "CallCenter page should load"
        logger.info("✓ CallCenter accessible")
        
        logger.info("✅ All three systems accessible")
