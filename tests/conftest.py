"""
Test Configuration - pytest conftest.py

Central configuration for pytest, fixtures, and hooks.
Includes comprehensive audit trail logging for compliance.

Author: Lokendra Singh (qa.lokendra@gmail.com)
Website: www.sqamentor.com
Assisted by: AI Claude
"""

import pytest
import os
import time
from pathlib import Path
from framework.core.engine_selector import extract_test_metadata
from framework.ui.ui_factory import ui_factory
from framework.api.api_client import APIClient
from framework.api.api_interceptor import APIInterceptor
from framework.database.db_client import DBClient
from framework.intelligence import AIValidationSuggester, ValidationPatternCache
from config.settings import settings, get_ui_url, get_api_url
from utils.logger import get_logger, get_audit_logger

# Import COMPREHENSIVE enhanced report collection
# Using the new comprehensive_report_enhancements module for full framework coverage
from tests.comprehensive_report_enhancements import comprehensive_collector

# Create convenience aliases for backward compatibility
report_collector = comprehensive_collector
report_log = lambda test_id, message, level="INFO": comprehensive_collector.add_log(test_id, message, level)
report_screenshot = lambda test_id, path, description="": comprehensive_collector.add_screenshot(test_id, path, description)
report_api_call = lambda test_id, method, url, status, time, req=None, resp=None: comprehensive_collector.add_api_call(test_id, method, url, status, time, req, resp)
report_db_query = lambda test_id, query, time, rows=0: comprehensive_collector.add_db_query(test_id, query, time, rows)
report_assertion = lambda test_id, type, expected, actual, passed, message="": comprehensive_collector.add_assertion(test_id, type, expected, actual, passed, message)

logger = get_logger(__name__)
audit_logger = get_audit_logger()


# ========================================================================
# COMMAND LINE OPTIONS
# ========================================================================
# NOTE: Command line options are registered in root conftest.py
# This avoids duplicate registration and ensures consistent defaults across all tests

# ========================================================================
# SESSION SCOPE FIXTURES
# ========================================================================

@pytest.fixture(scope="session")
def env(request):
    """Get test environment"""
    env_name = request.config.getoption("--env")
    settings.current_environment = env_name
    logger.info(f"Running tests in environment: {env_name}")
    return env_name


@pytest.fixture(scope="session")
def browser_config(request):
    """Get browser configuration"""
    return {
        "browser_type": request.config.getoption("--test-browser"),
        "headless": request.config.getoption("--headless")
    }


@pytest.fixture(scope="session")
def validation_cache():
    """Session-scoped validation pattern cache for performance"""
    ttl_seconds = 3600  # 1 hour TTL
    max_size = 500  # Cache up to 500 patterns
    
    cache = ValidationPatternCache(
        ttl_seconds=ttl_seconds,
        max_size=max_size
    )
    logger.info(f"Validation pattern cache initialized (TTL: {ttl_seconds}s, Max: {max_size})")
    yield cache
    # Log cache statistics at session end
    stats = cache.get_stats()
    logger.info(f"Cache statistics: {stats}")


# ========================================================================
# FUNCTION SCOPE FIXTURES
# ========================================================================

@pytest.fixture
def ui_engine(request, browser_config):
    """
    Create UI engine based on test metadata
    Uses auto-routing (Playwright or Selenium)
    """
    # Extract test metadata
    metadata = extract_test_metadata(request.node)
    
    # Create engine using factory
    engine, decision = ui_factory.create_engine(
        metadata,
        browser_type=browser_config["browser_type"],
        headless=browser_config["headless"]
    )
    
    logger.info(f"Test '{metadata['test_name']}' using {decision.engine} (reason: {decision.reason})")
    
    yield engine
    
    # Cleanup
    try:
        engine.stop()
    except (AttributeError, RuntimeError) as e:
        logger.warning(f"Error stopping engine: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during engine cleanup: {e}")


@pytest.fixture
def api_client(env):
    """Create API client"""
    base_url = get_api_url(env)
    client = APIClient(base_url)
    yield client


@pytest.fixture
def api_interceptor(api_client):
    """Create API interceptor with WebSocket and modification support"""
    interceptor = APIInterceptor(api_client)
    
    # Enable interception by default
    interceptor.enable()
    logger.info("API Interceptor enabled (HTTP + WebSocket support)")
    
    yield interceptor
    
    # Cleanup and log statistics
    try:
        captured = interceptor.get_captured_requests()
        ws_messages = interceptor.get_websocket_messages()
        logger.info(f"API Interceptor stats - HTTP: {len(captured)}, WebSocket: {len(ws_messages)} messages")
    except (AttributeError, KeyError, TypeError) as e:
        logger.warning(f"Error collecting interceptor stats: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in interceptor cleanup: {e}")
    
    try:
        interceptor.disable()
    except Exception as e:
        logger.error(f"Error disabling interceptor: {e}")


@pytest.fixture
def db_client(env):
    """Create database client"""
    client = DBClient(db_name='primary', env=env)
    yield client
    client.close()


@pytest.fixture
def ai_validator(validation_cache):
    """Create AI validation suggester with caching"""
    suggester = AIValidationSuggester()
    
    # Inject cache into suggester
    suggester.cache = validation_cache
    logger.info("AI Validation Suggester initialized with session cache")
    
    return suggester


@pytest.fixture
def ui_url(env):
    """Get UI base URL"""
    return get_ui_url(env)


@pytest.fixture(autouse=True)
def log_test_execution(request):
    """
    Automatically log test execution to audit trail
    Runs before/after every test
    """
    test_name = request.node.nodeid
    test_file = str(request.fspath)
    
    # Log test start
    audit_logger.log_test_start(test_name=test_name, test_file=test_file)
    
    yield
    
    # Test end is logged in pytest_runtest_makereport hook


# ========================================================================
# MULTI-PROJECT FIXTURES (for cross-application testing)
# ========================================================================

@pytest.fixture
def test_context():
    """
    Shared test context for multi-project testing
    Used to pass data between different applications
    """
    from models import TestContext
    context = TestContext()
    yield context
    context.clear()


@pytest.fixture
def multi_project_config(request, env):
    """
    Multi-project configuration - Dynamically loads from projects.yaml
    Returns URLs for different projects in current environment
    Supports: staging, production
    
    NOTE: Only loads configuration for the selected project (via --project option)
    to avoid unnecessary initialization of other projects
    """
    # Get selected project from command line
    selected_project = request.config.getoption('--project', default=None)
    
    # Load projects from projects.yaml
    projects_config = settings.get_projects_config()
    
    # Build project URLs dictionary for current environment
    result = {}
    
    # Determine which projects to load
    if selected_project:
        # Load ONLY the selected project
        projects_to_load = [selected_project]
        logger.info(f"Loading configuration for selected project: {selected_project}")
    else:
        # Load all projects (for cross-application tests)
        projects_to_load = ['bookslot', 'patientintake', 'callcenter']
        logger.info("Loading configuration for all projects (cross-application test mode)")
    
    for project_name in projects_to_load:
        if project_name in projects_config:
            project = projects_config[project_name]
            env_config = project.get('environments', {}).get(env, {})
            if env_config:
                result[project_name] = env_config
                logger.info(f"Loaded {project_name} config for {env}: {env_config.get('ui_url')}")
    
    if not result:
        # Fallback to hardcoded values if projects.yaml not found
        logger.warning(f"projects.yaml not loaded, using fallback configuration for env: {env}")
        if selected_project == 'bookslot' or not selected_project:
            result['bookslot'] = {
                'staging': {
                    'ui_url': 'https://bookslot-staging.centerforvein.com',
                    'api_url': 'https://api-bookslot-staging.centerforvein.com'
                },
                'production': {
                    'ui_url': 'https://bookslots.centerforvein.com',
                    'api_url': 'https://api-bookslot.centerforvein.com'
                }
            }.get(env, {})
    
    return result


@pytest.fixture(scope="session")
def playwright_instance():
    """
    Session-scoped Playwright instance
    Shared across all tests to avoid event loop conflicts
    """
    from playwright.sync_api import sync_playwright
    
    playwright = sync_playwright().start()
    yield playwright
    playwright.stop()


@pytest.fixture(scope="session")
def shared_browser(playwright_instance, browser_config):
    """
    Session-scoped browser instance
    Shared across all tests for better performance
    """
    browser = playwright_instance.chromium.launch(
        headless=browser_config["headless"]
    )
    yield browser
    browser.close()


@pytest.fixture
def bookslot_page(request, shared_browser, multi_project_config):
    """
    Bookslot page object fixture
    Creates a Playwright page for Bookslot application
    """
    from pages.bookslot import BookslotBasicInfoPage
    
    context = shared_browser.new_context()
    page = context.new_page()
    
    # Create page object
    bookslot_config = multi_project_config['bookslot']
    bookslot_po = BookslotBasicInfoPage(page, bookslot_config['ui_url'])
    
    yield bookslot_po
    
    # Cleanup
    context.close()


@pytest.fixture
def patientintake_page(request, shared_browser, multi_project_config):
    """
    PatientIntake page object fixture
    Creates a Playwright page for PatientIntake application
    """
    from pages.patientintake import PatientIntakeAppointmentListPage
    
    context = shared_browser.new_context()
    page = context.new_page()
    
    # Create page object
    patientintake_config = multi_project_config['patientintake']
    patientintake_po = PatientIntakeAppointmentListPage(page, patientintake_config['ui_url'])
    
    yield patientintake_po
    
    # Cleanup
    context.close()


@pytest.fixture
def callcenter_page(request, browser_config, multi_project_config):
    """
    CallCenter page object fixture
    Creates a Playwright page for CallCenter application
    """
    from playwright.sync_api import sync_playwright
    from pages.callcenter import CallCenterAppointmentManagementPage
    
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=browser_config["headless"]
    )
    context = browser.new_context()
    page = context.new_page()
    
    # Create page object
    callcenter_config = multi_project_config['callcenter']
    callcenter_po = CallCenterAppointmentManagementPage(page, callcenter_config['ui_url'])
    
    yield callcenter_po
    
    # Cleanup
    context.close()
    browser.close()
    playwright.stop()


# ========================================================================
# HOOKS
# ========================================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test results, take screenshots on failure, and log to audit trail
    Enhanced with comprehensive report collection
    """
    outcome = yield
    report = outcome.get_result()
    
    # Only process test execution phase (not setup/teardown)
    if report.when == "call":
        # Update report collector with test results
        report_collector.end_test(item, report)
        
        # Log test completion to audit trail
        test_name = item.nodeid
        
        if report.passed:
            audit_logger.log_test_end(
                test_name=test_name,
                status="passed",
                duration=report.duration
            )
            
            # Take success screenshot if any fixture has screenshot capability
            screenshot_engine = None
            for fixture_value in item.funcargs.values():
                if hasattr(fixture_value, 'take_screenshot'):
                    screenshot_engine = fixture_value
                    break
            
            if screenshot_engine:
                try:
                    screenshot_dir = Path("screenshots")
                    screenshot_dir.mkdir(exist_ok=True)
                    
                    screenshot_path = screenshot_dir / f"{item.name}_success.png"
                    screenshot_engine.take_screenshot(str(screenshot_path))
                    
                    # Add to report collector
                    report_collector.add_screenshot(test_name, str(screenshot_path), "Test Passed - Success Screenshot")
                    
                    logger.info(f"Success screenshot saved: {screenshot_path}")
                except Exception as e:
                    logger.error(f"Failed to take success screenshot: {e}")
        
        elif report.failed:
            audit_logger.log_test_end(
                test_name=test_name,
                status="failed",
                duration=report.duration
            )
            
            # Log failure details
            if hasattr(report, 'longrepr'):
                audit_logger.log_error(
                    error_type="test_failure",
                    error_message=str(report.longrepr)[:500],
                    stack_trace=test_name
                )
            
            # Take failure screenshot if any fixture has screenshot capability
            screenshot_engine = None
            for fixture_value in item.funcargs.values():
                if hasattr(fixture_value, 'take_screenshot'):
                    screenshot_engine = fixture_value
                    break
            
            if screenshot_engine:
                try:
                    screenshot_dir = Path("screenshots")
                    screenshot_dir.mkdir(exist_ok=True)
                    
                    screenshot_path = screenshot_dir / f"{item.name}_failure.png"
                    screenshot_engine.take_screenshot(str(screenshot_path))
                    
                    # Add to report collector
                    report_collector.add_screenshot(test_name, str(screenshot_path), "Test Failed - Failure Screenshot")
                    
                    logger.info(f"Failure screenshot saved: {screenshot_path}")
                except Exception as e:
                    logger.error(f"Failed to take failure screenshot: {e}")


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection
    Can be used to reorder tests, add markers dynamically, etc.
    """
    for item in items:
        # Add env marker based on selected environment
        env = config.getoption("--env")
        item.add_marker(pytest.mark.env(env))


# ========================================================================
# REPORTING
# ========================================================================

def pytest_html_report_title(report):
    """Customize HTML report title"""
    report.title = "Test Automation Execution Report"


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    """
    Configure pytest - runs after pytest-metadata
    Apply nest_asyncio to allow Playwright sync API in async context
    """
    # Apply nest_asyncio at session level to allow sync Playwright in async context
    import nest_asyncio
    nest_asyncio.apply()
    logger.info("Applied nest_asyncio for Playwright sync API support")
    
    # Create directories
    Path("logs").mkdir(exist_ok=True)
    Path("screenshots").mkdir(exist_ok=True)
    Path("videos").mkdir(exist_ok=True)
    Path("traces").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)
    Path("allure-results").mkdir(exist_ok=True)
    
    # Add custom metadata for HTML report
    # This runs after pytest-metadata plugin initializes config._metadata
    import platform
    import socket
    from datetime import datetime
    
    # Ensure metadata exists (pytest-metadata creates it)
    if not hasattr(config, '_metadata'):
        config._metadata = {}
    
    # Get configuration options
    env = config.getoption("--env")
    browser = config.getoption("--test-browser")
    headless = config.getoption("--headless")
    execution_mode = config.getoption("--execution-mode")
    human_behavior = config.getoption("--enable-human-behavior")
    
    # Normalize environment
    if env == "prod":
        env = "production"
    
    # Determine Base URL from projects.yaml
    from config.settings import SettingsManager
    settings = SettingsManager()
    bookslot_config = settings.get_project_config('bookslot', env)
    base_url = bookslot_config.get('ui_url', 'N/A')
    
    # Get system information
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
    except:
        ip_address = "N/A"
    
    # Add custom metadata (will appear in HTML report Environment section)
    config._metadata["Test Environment"] = env.upper()
    config._metadata["Base URL"] = base_url
    config._metadata["Browser"] = browser.upper()
    config._metadata["Headless Mode"] = "Yes" if headless else "No"
    config._metadata["Execution Mode"] = execution_mode.upper() if execution_mode else "Default"
    config._metadata["Human Behavior"] = "Enabled" if human_behavior else "Disabled"
    config._metadata["Test Execution Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    config._metadata["Operating System"] = platform.system()
    config._metadata["OS Version"] = platform.version()
    config._metadata["Architecture"] = platform.machine()
    config._metadata["Processor"] = platform.processor()
    config._metadata["Hostname"] = socket.gethostname()
    config._metadata["IP Address"] = ip_address
    
    logger.info(f"CUSTOM METADATA SET: Test Environment={env.upper()}, Base URL={base_url}")
    logger.info("Pytest configuration complete with custom metadata")


def pytest_sessionstart(session):
    """Called before test session starts"""
    config = session.config
    
    # Get configuration for logging
    env = config.getoption("--env")
    if env == "prod":
        env = "production"
    
    base_urls = {
        "dev": "https://bookslot-dev.centerforvein.com",
        "staging": "https://bookslot-staging.centerforvein.com",
        "production": "https://bookslots.centerforvein.com"
    }
    base_url = base_urls.get(env, "N/A")
    browser = config.getoption("--test-browser")
    headless = config.getoption("--headless")
    
    logger.info("=" * 80)
    logger.info("TEST SESSION STARTED")
    logger.info(f"Environment: {env.upper()} | Base URL: {base_url}")
    logger.info(f"Browser: {browser.upper()} | Headless: {headless}")
    logger.info("=" * 80)


def pytest_sessionfinish(session, exitstatus):
    """Called after test session finishes"""
    logger.info("=" * 80)
    logger.info(f"TEST SESSION FINISHED (exit status: {exitstatus})")
    logger.info("=" * 80)


def pytest_collection_modifyitems(config, items):
    """
    Mark sync Playwright tests to skip asyncio auto-wrapping.
    This prevents the error: "Using Playwright Sync API inside asyncio loop"
    """
    for item in items:
        # Check if test uses sync Playwright fixtures
        sync_playwright_fixtures = [
            "bookslot_page", "patientintake_page", "browser_manager", 
            "context_manager", "page"
        ]
        
        # If test uses any sync Playwright fixture, mark it to skip asyncio
        if any(fixture in getattr(item, "fixturenames", []) for fixture in sync_playwright_fixtures):
            # Add no_asyncio marker to prevent pytest-asyncio from wrapping
            item.add_marker(pytest.mark.no_asyncio)


