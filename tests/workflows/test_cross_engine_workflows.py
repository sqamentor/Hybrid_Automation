"""Cross-Engine Workflow Tests.

Tests for multi-step workflows that span Selenium and Playwright engines.
Implements the user's use case: SSO (Selenium) → CallCenter (Playwright) → PatientIntake (Playwright)

Author: Principal QA Architect
Date: January 31, 2026
"""

import logging

import pytest

from framework.core.workflow_orchestrator import EngineType, OnFailureStrategy

logger = logging.getLogger(__name__)


@pytest.mark.workflow
@pytest.mark.requires_authentication
@pytest.mark.sso_dependent
@pytest.mark.ui_sequential
def test_sso_to_callcenter_to_patientintake(
    workflow_orchestrator,
    workflow_engines,
    auth_service,
    sso_config,
    sso_credentials,
    config
):
    """
    Complete cross-engine workflow: SSO Login → CallCenter → PatientIntake
    
    This test implements the user's exact use case:
    1. Login using legacy SSO system (Selenium)
    2. Execute CallCenter tests (Playwright with session transfer)
    3. Execute PatientIntake tests (Playwright reusing session)
    
    Expected behavior:
    - SSO authentication completes successfully via Selenium
    - Session is extracted from Selenium after auth
    - Session is injected into Playwright for CallCenter operations
    - Same session is reused for PatientIntake operations
    - No re-authentication needed between steps
    """
    logger.info("🚀 Starting SSO → CallCenter → PatientIntake workflow")
    
    # Get project URLs from config
    callcenter_url = config.get('projects', {}).get('callcenter', {}).get('url', 'https://callcenter.example.com')
    patientintake_url = config.get('projects', {}).get('patientintake', {}).get('url', 'https://patientintake.example.com')
    
    # Define workflow
    workflow = workflow_orchestrator.define_workflow(
        name="SSO to CallCenter to PatientIntake",
        description="Login via SSO (Selenium), then test CallCenter and PatientIntake (Playwright)",
        metadata={
            'sso_provider': sso_config.get('provider'),
            'test_type': 'cross_engine_workflow',
            'projects': ['callcenter', 'patientintake']
        }
    )
    
    # ============================================================================
    # STEP 1: SSO AUTHENTICATION (SELENIUM)
    # ============================================================================
    
    def step1_sso_login(driver):
        """Step 1: Authenticate using SSO (Okta/Azure/Google)"""
        logger.info("📝 STEP 1: SSO Authentication")
        
        session_data = auth_service.authenticate_sso(
            engine=driver,
            sso_config=sso_config,
            credentials=sso_credentials,
            timeout=60
        )
        
        if not session_data:
            raise ValueError("SSO authentication failed")
        
        logger.info(f"✅ SSO login successful - User: {session_data.user_id}")
        logger.info(f"   Auth Type: {session_data.auth_type}")
        logger.info(f"   Cookies: {len(session_data.cookies)}")
        logger.info(f"   Tokens: {len(session_data.tokens)}")
        
        return session_data
    
    workflow_orchestrator.add_step(
        workflow=workflow,
        name="SSO Login (Selenium)",
        engine_type=EngineType.SELENIUM,
        action=step1_sso_login,
        requires_session=False,  # This is the auth step
        on_failure=OnFailureStrategy.STOP,
        timeout=60,
        metadata={'step_type': 'authentication', 'provider': sso_config.get('provider')}
    )
    
    # ============================================================================
    # STEP 2: CALLCENTER OPERATIONS (PLAYWRIGHT)
    # ============================================================================
    
    def step2_callcenter_operations(page):
        """Step 2: Navigate to CallCenter and verify authenticated access"""
        logger.info("📝 STEP 2: CallCenter Operations")
        
        # Use Page Object for verification
        from pages.callcenter.dashboard_verification_page import CallCenterDashboardVerificationPage
        
        verification_page = CallCenterDashboardVerificationPage(page)
        
        # Navigate to CallCenter
        logger.info(f"   Navigating to: {callcenter_url}")
        verification_page.navigate_to(callcenter_url)
        
        # Verify we're authenticated (not redirected to login)
        if not verification_page.is_authenticated():
            raise ValueError("Session not transferred - redirected to login")
        
        logger.info(f"   ✅ Loaded: {verification_page.get_current_url()}")
        
        # Verify page loaded correctly
        title = verification_page.get_page_title()
        logger.info(f"   Page Title: {title}")
        
        # Verify authentication indicators
        if verification_page.has_user_menu():
            logger.info("   ✅ User menu found - authenticated session verified")
        else:
            logger.warning("   ⚠️ User menu not found - session may not be fully active")
        
        # Get comprehensive verification details
        details = verification_page.get_verification_details()
        logger.info(f"   Verification Details: {details}")
        
        # Example: Perform CallCenter-specific operations
        # Uncomment and customize based on your CallCenter pages
        """
        # Import your CallCenter page objects
        from pages.callcenter.dashboard_page import DashboardPage
        
        dashboard = DashboardPage(page)
        dashboard.verify_page_loaded()
        dashboard.navigate_to_appointments()
        
        # Verify can access data
        appointments = dashboard.get_appointments_list()
        logger.info(f"   ✅ Loaded {len(appointments)} appointments")
        """
        
        logger.info("   ✅ CallCenter operations completed")
        return True
    
    workflow_orchestrator.add_step(
        workflow=workflow,
        name="CallCenter Operations (Playwright)",
        engine_type=EngineType.PLAYWRIGHT,
        action=step2_callcenter_operations,
        requires_session=True,  # Transfer session from Step 1
        on_failure=OnFailureStrategy.STOP,
        timeout=60,
        metadata={'step_type': 'business_operations', 'project': 'callcenter'}
    )
    
    # ============================================================================
    # STEP 3: PATIENTINTAKE OPERATIONS (PLAYWRIGHT)
    # ============================================================================
    
    def step3_patientintake_operations(page):
        """Step 3: Navigate to PatientIntake and verify authenticated access"""
        logger.info("📝 STEP 3: PatientIntake Operations")
        
        # Use Page Object for verification
        from pages.patientintake.patient_verification_page import PatientIntakeVerificationPage
        
        verification_page = PatientIntakeVerificationPage(page)
        
        # Navigate to PatientIntake
        logger.info(f"   Navigating to: {patientintake_url}")
        verification_page.navigate_to(patientintake_url)
        
        # Verify we're authenticated
        if not verification_page.is_authenticated():
            raise ValueError("Session not preserved - redirected to login")
        
        logger.info(f"   ✅ Loaded: {verification_page.get_current_url()}")
        
        # Verify page loaded
        title = verification_page.get_page_title()
        logger.info(f"   Page Title: {title}")
        
        # Verify authentication indicators
        if verification_page.has_user_menu():
            logger.info("   ✅ User menu found - authenticated session verified")
        else:
            logger.warning("   ⚠️ User menu not found - session may not be fully active")
        
        # Get comprehensive verification details
        details = verification_page.get_verification_details()
        logger.info(f"   Verification Details: {details}")
        
        # Example: Perform PatientIntake-specific operations
        # Uncomment and customize based on your PatientIntake pages
        """
        # Import your PatientIntake page objects
        from pages.patientintake.intake_form_page import IntakeFormPage
        
        intake_form = IntakeFormPage(page)
        intake_form.verify_page_loaded()
        intake_form.fill_patient_information(...)
        intake_form.submit_form()
        
        logger.info("   ✅ Patient intake form submitted")
        """
        
        logger.info("   ✅ PatientIntake operations completed")
        return True
    
    workflow_orchestrator.add_step(
        workflow=workflow,
        name="PatientIntake Operations (Playwright)",
        engine_type=EngineType.PLAYWRIGHT,
        action=step3_patientintake_operations,
        requires_session=True,  # Reuse session from Step 1
        on_failure=OnFailureStrategy.STOP,
        timeout=60,
        metadata={'step_type': 'business_operations', 'project': 'patientintake'}
    )
    
    # ============================================================================
    # EXECUTE WORKFLOW
    # ============================================================================
    
    logger.info("\n🎬 Executing workflow...")
    success = workflow_orchestrator.execute_workflow_sync(workflow, workflow_engines)
    
    # Verify workflow completed
    assert success, "Workflow execution failed"
    
    # Get workflow status
    status = workflow_orchestrator.get_workflow_status(workflow)
    logger.info(f"\n📊 Workflow Status:")
    logger.info(f"   Total Steps: {status['total_steps']}")
    logger.info(f"   Completed: {status['completed_steps']}")
    logger.info(f"   Failed: {status['failed_steps']}")
    logger.info(f"   Success Rate: {status['success_rate']:.1f}%")
    
    # Verify all steps succeeded
    assert status['completed_steps'] == status['total_steps'], "Not all steps completed"
    assert status['failed_steps'] == 0, "Some steps failed"
    
    logger.info("\n✅ Complete workflow executed successfully!")


@pytest.mark.workflow
@pytest.mark.requires_authentication
def test_sso_authentication_only(
    workflow_orchestrator,
    workflow_engines,
    auth_service,
    sso_config,
    sso_credentials
):
    """Test SSO authentication step only.

    Validates that SSO authentication works correctly and session is captured.
    """
    logger.info("🚀 Testing SSO authentication only")
    
    workflow = workflow_orchestrator.define_workflow(
        name="SSO Authentication Test",
        description="Validate SSO authentication and session capture"
    )
    
    def authenticate(driver):
        session_data = auth_service.authenticate_sso(
            engine=driver,
            sso_config=sso_config,
            credentials=sso_credentials,
            timeout=60
        )
        
        assert session_data is not None, "Authentication returned no session"
        assert len(session_data.cookies) > 0, "No cookies captured"
        assert session_data.user_id, "No user_id captured"
        
        logger.info(f"✅ Authentication successful - User: {session_data.user_id}")
        return session_data
    
    workflow_orchestrator.add_step(
        workflow,
        name="SSO Authentication",
        engine_type=EngineType.SELENIUM,
        action=authenticate,
        requires_session=False
    )
    
    success = workflow_orchestrator.execute_workflow_sync(workflow, workflow_engines)
    assert success, "SSO authentication workflow failed"


@pytest.mark.workflow
@pytest.mark.requires_authentication
def test_session_transfer_selenium_to_playwright(
    workflow_orchestrator,
    workflow_engines,
    auth_service,
    sso_config,
    sso_credentials,
    config
):
    """Test session transfer from Selenium to Playwright.

    Validates that session extracted from Selenium can be successfully injected into Playwright and
    remain valid.
    """
    logger.info("🚀 Testing Selenium → Playwright session transfer")
    
    workflow = workflow_orchestrator.define_workflow(
        name="Session Transfer Test",
        description="Authenticate with Selenium, transfer to Playwright"
    )
    
    # Step 1: Authenticate with Selenium
    def authenticate_selenium(driver):
        session_data = auth_service.authenticate_sso(
            engine=driver,
            sso_config=sso_config,
            credentials=sso_credentials,
            timeout=60
        )
        assert session_data is not None
        logger.info(f"✅ Selenium authentication complete - {len(session_data.cookies)} cookies")
        return session_data
    
    workflow_orchestrator.add_step(
        workflow,
        name="Authenticate (Selenium)",
        engine_type=EngineType.SELENIUM,
        action=authenticate_selenium,
        requires_session=False
    )
    
    # Step 2: Verify session in Playwright
    def verify_playwright_session(page):
        # Get any project URL
        test_url = config.get('projects', {}).get('callcenter', {}).get('url', 'https://example.com')
        
        logger.info(f"   Navigating with transferred session: {test_url}")
        page.goto(test_url, wait_until='networkidle')
        
        # Verify not redirected to login
        current_url = page.url
        assert 'login' not in current_url.lower(), "Session not transferred - redirected to login"
        
        logger.info("   ✅ Playwright session verified - no login redirect")
        return True
    
    workflow_orchestrator.add_step(
        workflow,
        name="Verify Session (Playwright)",
        engine_type=EngineType.PLAYWRIGHT,
        action=verify_playwright_session,
        requires_session=True
    )
    
    success = workflow_orchestrator.execute_workflow_sync(workflow, workflow_engines)
    assert success, "Session transfer workflow failed"


# ============================================================================
# EXAMPLE: Workflow with Error Recovery
# ============================================================================

@pytest.mark.workflow
@pytest.mark.skip(reason="Example implementation - customize for your needs")
def test_workflow_with_retry_logic(workflow_orchestrator, workflow_engines):
    """
    Example: Workflow with retry logic for flaky operations
    """
    workflow = workflow_orchestrator.define_workflow(
        name="Workflow with Retries",
        description="Demonstrates retry and continue-on-failure strategies"
    )
    
    # Step that might fail but should retry
    def flaky_operation(page):
        # Simulated flaky operation
        import random
        if random.random() < 0.5:
            raise ValueError("Simulated failure")
        return True
    
    workflow_orchestrator.add_step(
        workflow,
        name="Flaky Operation",
        engine_type=EngineType.PLAYWRIGHT,
        action=flaky_operation,
        requires_session=False,
        on_failure=OnFailureStrategy.RETRY,
        retry_count=3  # Retry up to 3 times
    )
    
    # Step that should continue even if it fails
    def optional_operation(page):
        # Optional operation that shouldn't stop workflow
        logger.info("   Executing optional operation")
        return True
    
    workflow_orchestrator.add_step(
        workflow,
        name="Optional Operation",
        engine_type=EngineType.PLAYWRIGHT,
        action=optional_operation,
        requires_session=False,
        on_failure=OnFailureStrategy.CONTINUE
    )
    
    success = workflow_orchestrator.execute_workflow_sync(workflow, workflow_engines)
    assert success
