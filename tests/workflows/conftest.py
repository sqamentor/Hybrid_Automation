"""
Workflow Test Fixtures

Provides pytest fixtures for cross-engine workflow testing.
Integrates SessionManager, AuthenticationService, and WorkflowOrchestrator.

Author: Principal QA Architect
Date: January 31, 2026
"""

import logging
from typing import Any, Dict, Tuple

import pytest

from framework.auth.auth_service import AuthenticationService
from framework.core.session_manager import SessionManager
from framework.core.workflow_orchestrator import WorkflowOrchestrator

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def session_manager() -> SessionManager:
    """
    Provides SessionManager instance for session bridging

    Usage:
        def test_example(session_manager):
            session = session_manager.extract_session_from_selenium(driver)
    """
    logger.info("🔧 Initializing SessionManager fixture")
    return SessionManager()


@pytest.fixture(scope="session")
def auth_service(session_manager: SessionManager) -> AuthenticationService:
    """
    Provides AuthenticationService with SessionManager

    Usage:
        def test_example(auth_service):
            session = auth_service.authenticate_sso(driver, sso_config, credentials)
    """
    logger.info("🔧 Initializing AuthenticationService fixture")
    return AuthenticationService(session_manager=session_manager)


@pytest.fixture(scope="function")
def workflow_orchestrator(
    auth_service: AuthenticationService, session_manager: SessionManager
) -> WorkflowOrchestrator:
    """
    Provides WorkflowOrchestrator for multi-step workflows

    Usage:
        def test_workflow(workflow_orchestrator):
            workflow = workflow_orchestrator.define_workflow("My Workflow")
            workflow_orchestrator.add_step(workflow, ...)
            success = workflow_orchestrator.execute_workflow_sync(workflow, engines)
    """
    logger.info("🔧 Initializing WorkflowOrchestrator fixture")
    return WorkflowOrchestrator(auth_service=auth_service, session_manager=session_manager)


@pytest.fixture(scope="function")
def cross_engine_session(
    selenium_driver, playwright_page_sync, session_manager: SessionManager
) -> Tuple[Any, Any, SessionManager]:
    """
    Provides pre-configured cross-engine session setup

    Returns:
        (selenium_driver, playwright_page, session_manager)

    Usage:
        def test_cross_engine(cross_engine_session):
            selenium_driver, playwright_page, session_mgr = cross_engine_session
            # Use both engines with shared session
    """
    logger.info("🔧 Setting up cross-engine session")

    # Ensure both engines are ready
    assert selenium_driver is not None, "Selenium driver not initialized"
    assert playwright_page_sync is not None, "Playwright page not initialized"

    yield (selenium_driver, playwright_page_sync, session_manager)

    logger.info("🧹 Cleaning up cross-engine session")


@pytest.fixture(scope="function")
def workflow_engines(selenium_driver, playwright_page_sync) -> Dict[str, Any]:
    """
    Provides engines dict for workflow orchestrator

    Returns:
        {
            'selenium': WebDriver instance,
            'playwright': Playwright Page instance (sync)
        }

    Usage:
        def test_workflow(workflow_orchestrator, workflow_engines):
            workflow = workflow_orchestrator.define_workflow("Test")
            success = workflow_orchestrator.execute_workflow_sync(workflow, workflow_engines)
    """
    logger.info("🔧 Preparing workflow engines")

    engines = {"selenium": selenium_driver, "playwright": playwright_page_sync}

    yield engines

    logger.info("🧹 Workflow engines cleanup complete")


@pytest.fixture(scope="function")
def sso_config(config) -> Dict[str, str]:
    """
    Provides SSO configuration from config

    Expected in config YAML:
        sso:
          provider: okta
          okta_domain: https://company.okta.com
          app_id: xxxxx

    Returns:
        SSO configuration dict

    Usage:
        def test_sso(auth_service, sso_config):
            session = auth_service.authenticate_sso(driver, sso_config, credentials)
    """
    sso_data = config.get("sso", {})

    if not sso_data:
        logger.warning("⚠️ SSO configuration not found in config")
        pytest.skip("SSO configuration not available")

    logger.info(f"🔧 SSO config loaded: provider={sso_data.get('provider')}")
    return sso_data


@pytest.fixture(scope="function")
def sso_credentials(config) -> Dict[str, str]:
    """
    Provides SSO credentials from config or environment

    Expected in config YAML:
        credentials:
          sso_username: user@company.com
          sso_password: xxx
          mfa_token: xxx (optional)

    Returns:
        Credentials dict

    Usage:
        def test_sso(auth_service, sso_credentials):
            session = auth_service.authenticate_sso(driver, sso_config, sso_credentials)
    """
    import os

    # Try to get from config first
    creds_data = config.get("credentials", {})

    # Override with environment variables if available
    credentials = {
        "username": os.getenv("SSO_USERNAME", creds_data.get("sso_username")),
        "password": os.getenv("SSO_PASSWORD", creds_data.get("sso_password")),
        "mfa_token": os.getenv("MFA_TOKEN", creds_data.get("mfa_token")),
    }

    if not credentials.get("username") or not credentials.get("password"):
        logger.warning("⚠️ SSO credentials not configured")
        pytest.skip("SSO credentials not available")

    logger.info(f"🔧 SSO credentials loaded for user: {credentials['username']}")
    return credentials


@pytest.fixture(scope="function")
def authenticated_selenium(
    selenium_driver,
    auth_service: AuthenticationService,
    sso_config: Dict[str, str],
    sso_credentials: Dict[str, str],
) -> Tuple[Any, Any]:
    """
    Provides pre-authenticated Selenium driver with session

    Returns:
        (selenium_driver, session_data)

    Usage:
        def test_with_auth(authenticated_selenium):
            driver, session = authenticated_selenium
            # Driver is already authenticated
    """
    logger.info("🔐 Authenticating Selenium driver via SSO...")

    session_data = auth_service.authenticate_sso(
        engine=selenium_driver, sso_config=sso_config, credentials=sso_credentials, timeout=60
    )

    if not session_data:
        pytest.fail("SSO authentication failed")

    logger.info("✅ Selenium driver authenticated successfully")

    yield (selenium_driver, session_data)

    logger.info("🧹 Authenticated session cleanup")


@pytest.fixture(scope="function")
def authenticated_workflow(
    workflow_orchestrator: WorkflowOrchestrator,
    workflow_engines: Dict[str, Any],
    auth_service: AuthenticationService,
    sso_config: Dict[str, str],
    sso_credentials: Dict[str, str],
) -> Tuple[WorkflowOrchestrator, Dict[str, Any], Any]:
    """
    Provides workflow orchestrator with pre-authenticated Selenium session

    Returns:
        (workflow_orchestrator, workflow_engines, session_data)

    Usage:
        def test_workflow(authenticated_workflow):
            orchestrator, engines, session = authenticated_workflow
            # Selenium is authenticated, session available

            workflow = orchestrator.define_workflow("Test")
            # Add steps that use session
            orchestrator.execute_workflow_sync(workflow, engines)
    """
    logger.info("🔐 Pre-authenticating for workflow...")

    # Authenticate using Selenium
    session_data = auth_service.authenticate_sso(
        engine=workflow_engines["selenium"],
        sso_config=sso_config,
        credentials=sso_credentials,
        timeout=60,
    )

    if not session_data:
        pytest.fail("SSO authentication failed for workflow")

    logger.info("✅ Workflow pre-authentication successful")

    yield (workflow_orchestrator, workflow_engines, session_data)

    logger.info("🧹 Authenticated workflow cleanup")


@pytest.fixture(autouse=True, scope="function")
def workflow_test_logging(request):
    """
    Automatically log workflow test execution
    """
    test_name = request.node.name
    logger.info(f"\n{'='*100}")
    logger.info(f"WORKFLOW TEST: {test_name}")
    logger.info(f"{'='*100}")

    yield

    logger.info(f"\n{'='*100}")
    logger.info(f"WORKFLOW TEST COMPLETE: {test_name}")
    logger.info(f"{'='*100}\n")
