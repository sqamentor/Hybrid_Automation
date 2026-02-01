"""AI-Enhanced Three-System Workflow Test Example.

This demonstrates how to use AI capabilities during test execution:
- AI-powered engine selection
- Intelligent validation suggestions
- Automatic failure analysis
- Smart test data generation
"""

import logging
from datetime import datetime, timedelta

import pytest

from models import Appointment, TestContext

logger = logging.getLogger(__name__)


@pytest.mark.modern_spa
@pytest.mark.integration
@pytest.mark.ai_enhanced
class TestAIEnhancedWorkflow:
    """Three-system workflow with AI capabilities."""
    
    def test_ai_powered_booking_and_cancellation(
        self,
        test_context: TestContext,
        bookslot_page,
        patientintake_page,
        callcenter_page
    ):
        """
        AI-Enhanced Test: Book, verify, and cancel appointment
        
        AI Features Used:
        1. AI generates optimal test data
        2. AI suggests validations after booking
        3. AI analyzes if cancellation synced correctly
        """
        
        # ==========================================
        # AI FEATURE 1: Generate Optimal Test Data
        # ==========================================
        try:
            from framework.intelligence import generate_test_data
            
            logger.info("🤖 AI: Generating optimal test data...")
            appointment = generate_test_data(
                model="Appointment",
                constraints={
                    "date_range": "next_7_days",
                    "business_hours": True,
                    "avoid_holidays": True,
                    "realistic_names": True
                }
            )
            logger.info(f"✅ AI generated: {appointment.email}")
            
        except ImportError:
            # Fallback to manual data if AI not available
            logger.info("ℹ️  AI not available, using manual test data")
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
        
        test_context.set_data('appointment', appointment)
        
        # ==========================================
        # STEP 1: Book Appointment
        # ==========================================
        logger.info("Step 1: Booking appointment in Bookslot...")
        bookslot_page.navigate() \
            .fill_patient_info(appointment) \
            .submit()
        
        bookslot_page.should_see_confirmation()
        logger.info("✓ Appointment booked successfully")
        
        # ==========================================
        # AI FEATURE 2: Suggest Additional Validations
        # ==========================================
        try:
            from framework.intelligence import AIValidationSuggester
            
            logger.info("🤖 AI: Analyzing booking and suggesting validations...")
            suggester = AIValidationSuggester()
            
            # AI analyzes what should be verified
            suggestions = suggester.suggest_validations(
                api_endpoint="/appointments",
                api_method="POST",
                api_request=appointment.to_dict(),
                api_response={"status": "created", "id": appointment.bookslot_id}
            )
            
            logger.info(f"✅ AI suggested {len(suggestions.suggestions)} validations")
            for suggestion in suggestions.suggestions:
                logger.info(f"   Priority {suggestion.priority}: {suggestion.reason}")
            
        except Exception as e:
            logger.info(f"ℹ️  AI validation suggester not available: {e}")
        
        # ==========================================
        # STEP 2: Verify in PatientIntake
        # ==========================================
        logger.info("Step 2: Verifying in PatientIntake...")
        patientintake_page.navigate() \
            .search_appointment(appointment) \
            .verify_appointment_exists(appointment)
        
        logger.info("✓ Appointment verified in PatientIntake")
        
        # ==========================================
        # STEP 3: Verify and Cancel in CallCenter
        # ==========================================
        logger.info("Step 3: Verifying and cancelling in CallCenter...")
        callcenter_page.navigate() \
            .search_appointment(appointment) \
            .verify_appointment_exists(appointment)
        
        logger.info("✓ Appointment verified in CallCenter")
        
        # Cancel appointment
        cancellation_reason = "Patient requested cancellation via phone"
        callcenter_page.cancel_appointment(
            email=appointment.email,
            reason=cancellation_reason
        )
        
        logger.info("✓ Cancellation initiated")
        
        # ==========================================
        # STEP 4: Verify Cancellation
        # ==========================================
        callcenter_page.verify_appointment_cancelled(appointment.email)
        logger.info("✓ Cancellation confirmed in CallCenter")
        
        # Verify in PatientIntake
        patientintake_page.navigate() \
            .search_appointment(appointment)
        assert patientintake_page.should_have_status(appointment.email, "Cancelled"), \
            f"Expected appointment status 'Cancelled' for {appointment.email}"
        
        logger.info("✓ Cancellation reflected in PatientIntake")
        
        # ==========================================
        # AI FEATURE 3: Cross-System Sync Analysis
        # ==========================================
        try:
            from framework.intelligence import analyze_cross_system_sync
            
            logger.info("🤖 AI: Analyzing cross-system synchronization...")
            sync_analysis = analyze_cross_system_sync(
                appointment=appointment,
                systems=["bookslot", "patientintake", "callcenter"],
                expected_status="Cancelled"
            )
            
            if sync_analysis.is_synced:
                logger.info(f"✅ AI confirms: Data synced correctly in {sync_analysis.sync_time}ms")
            else:
                logger.warning(f"⚠️  AI detected sync issue: {sync_analysis.issue}")
            
        except Exception as e:
            logger.info(f"ℹ️  AI sync analysis not available: {e}")
        
        logger.info("✅ Test complete - AI-enhanced workflow successful")
    
    
    def test_ai_failure_recovery(
        self,
        test_context: TestContext,
        callcenter_page
    ):
        """
        AI Feature: Automatic failure recovery and locator healing
        
        When a locator fails, AI suggests alternatives
        """
        appointment = Appointment(
            email=f"test.{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
            first_name="Test",
            last_name="User"
        )
        
        logger.info("Testing AI-powered locator healing...")
        
        try:
            # Try primary locator
            callcenter_page.navigate()
            callcenter_page.search_by_email(appointment.email)
            
        except Exception as e:
            logger.warning(f"Primary locator failed: {e}")
            
            try:
                from framework.ui.ai_locator_healer import heal_locator
                
                logger.info("🤖 AI: Attempting to heal failed locator...")
                
                # AI finds alternative locator
                healed_locator = heal_locator(
                    page=callcenter_page.page,
                    failed_locator="[data-testid='search-input']",
                    context="appointment search input field",
                    element_type="input"
                )
                
                logger.info(f"✅ AI found alternative: {healed_locator}")
                
                # Use healed locator via Page Object method
                callcenter_page.fill_healed_locator(healed_locator, appointment.email)
                
            except Exception as heal_error:
                logger.error(f"AI healing failed: {heal_error}")
                raise


@pytest.mark.modern_spa
class TestAIEngineSelection:
    """Demonstrate AI-powered engine selection."""
    
    def test_ai_chooses_optimal_engine(self):
        """AI analyzes test requirements and chooses best engine."""
        from framework.core.ai_engine_selector import AIEngineSelector
        
        logger.info("Testing AI engine selection...")
        
        selector = AIEngineSelector()
        
        if not selector.enabled:
            logger.info("ℹ️  AI engine selector not enabled")
            pytest.skip("AI selector requires OPENAI_API_KEY")
        
        # AI analyzes and recommends
        recommendation = selector.recommend_engine(
            url="https://bookslot-staging.centerforvein.com",
            test_metadata={
                "test_type": "appointment_booking",
                "has_ajax": True,
                "has_websockets": False,
                "complexity": "medium",
                "requires_auth": False
            }
        )
        
        logger.info(f"🤖 AI Recommendation:")
        logger.info(f"   Engine: {recommendation.engine}")
        logger.info(f"   Confidence: {recommendation.confidence}%")
        logger.info(f"   Reasoning: {recommendation.reasoning}")
        
        # Use recommended engine
        assert recommendation.engine in ["playwright", "selenium"]
        assert recommendation.confidence >= 50
        
        logger.info("✅ AI engine selection working correctly")


@pytest.mark.modern_spa
class TestAIValidationSuggester:
    """Demonstrate AI validation suggestions."""
    
    def test_ai_suggests_database_validations(self):
        """AI analyzes API response and suggests DB checks."""
        from framework.intelligence import AIValidationSuggester
        
        logger.info("Testing AI validation suggester...")
        
        suggester = AIValidationSuggester()
        
        if not suggester.enabled:
            logger.info("ℹ️  AI validation suggester not enabled")
            pytest.skip("AI suggester requires API key")
        
        # Simulate API response
        api_response = {
            "appointment_id": "APT-12345",
            "patient_email": "john.doe@test.com",
            "status": "confirmed",
            "appointment_date": "2026-02-01",
            "created_at": "2026-01-25T10:30:00Z"
        }
        
        # AI suggests validations
        logger.info("🤖 AI: Analyzing API response...")
        suggestions = suggester.suggest_validations(
            api_endpoint="/appointments",
            api_method="POST",
            api_request={"email": "john.doe@test.com"},
            api_response=api_response
        )
        
        logger.info(f"✅ AI suggested {len(suggestions.suggestions)} validations:")
        
        for i, suggestion in enumerate(suggestions.suggestions, 1):
            logger.info(f"\n   Validation {i}:")
            logger.info(f"   Priority: {suggestion.priority}")
            logger.info(f"   Query: {suggestion.query}")
            logger.info(f"   Reason: {suggestion.reason}")
            logger.info(f"   Confidence: {suggestion.confidence}%")
        
        # Verify AI made reasonable suggestions
        assert len(suggestions.suggestions) > 0
        assert all(s.confidence > 60 for s in suggestions.suggestions)
        
        logger.info("✅ AI validation suggester working correctly")


# ========================================================================
# AI HELPER FUNCTIONS (Available for all tests)
# ========================================================================

def get_ai_test_analysis():
    """Get AI analysis of current test execution Can be called anytime during test."""
    from framework.intelligence import analyze_current_test
    
    return analyze_current_test()


def ask_ai(question: str) -> str:
    """Ask AI a question during test execution.

    Example:
        answer = ask_ai("What's the best way to verify this appointment was cancelled?")
    """
    from framework.intelligence import query_ai
    
    return query_ai(question)


def ai_debug(error_message: str, context: dict) -> dict:
    """Use AI to debug test failure.

    Returns:
        {
            "root_cause": "...",
            "fix_suggestion": "...",
            "confidence": 85
        }
    """
    from framework.intelligence import debug_with_ai
    
    return debug_with_ai(error_message, context)
