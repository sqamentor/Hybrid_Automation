"""
Root-level pytest configuration
This conftest.py registers command-line options for all tests in the project

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com
"""

import pytest
import platform
import socket
from datetime import datetime
from framework.core.utils.human_actions import HumanBehaviorSimulator, get_behavior_config
from utils.fake_data_generator import generate_bookslot_payload, load_bookslot_data
from utils.logger import get_audit_logger, get_logger

logger = get_logger(__name__)
audit_logger = get_audit_logger()

# ════════════════════════════════════════════════════════════════════════════
# REGISTER PYTEST PLUGINS
# ════════════════════════════════════════════════════════════════════════════
pytest_plugins = [
    'scripts.governance.pytest_arch_audit_plugin',
    'framework.observability.pytest_enterprise_logging'  # Enterprise logging integration
]


def pytest_addoption(parser):
    """Add custom command line options available to all tests"""
    
    # Project selection
    parser.addoption(
        "--project",
        action="store",
        default="bookslot",
        choices=["bookslot", "callcenter", "patientintake"],
        help="Project to run tests for (bookslot, callcenter, patientintake). Default: bookslot"
    )
    
    # Environment selection
    parser.addoption(
        "--env",
        action="store",
        default="staging",
        choices=["staging", "production", "prod"],
        help="Environment to run tests against (staging, production). Default: staging"
    )
    
    # Browser selection
    parser.addoption(
        "--test-browser",
        action="store",
        default="chromium",
        choices=["chromium", "chrome", "firefox", "webkit", "safari", "msedge"],
        help="Browser to use for testing (chromium, chrome, firefox, webkit, safari, msedge). Default: chromium"
    )
    
    # Headless mode
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode (no visible browser window)"
    )
    
    # Execution mode
    parser.addoption(
        "--execution-mode",
        action="store",
        default=None,
        choices=["ui_only", "ui_api", "ui_api_db"],
        help="Execution flow mode: ui_only (UI tests only), ui_api (UI + API validation), ui_api_db (UI + API + DB validation)"
    )
    
    # Human behavior simulation
    parser.addoption(
        "--enable-human-behavior",
        action="store_true",
        default=None,
        help="Enable human-like behavior simulation (mouse movements, typing delays, etc.)"
    )
    
    parser.addoption(
        "--disable-human-behavior",
        action="store_true",
        default=False,
        help="Disable human-like behavior simulation for faster execution"
    )
    
    parser.addoption(
        "--human-behavior-intensity",
        action="store",
        default="normal",
        choices=["minimal", "normal", "high"],
        help="Intensity of human behavior simulation: minimal (fast), normal (balanced), high (very realistic)"
    )


@pytest.fixture(scope="session")
def project(request):
    """
    Project fixture - provides the project name
    
    Returns:
        str: Project name (bookslot, callcenter, patientintake)
    
    Usage:
        def test_example(project):
            print(f"Running tests for {project}")
    """
    return request.config.getoption("--project")


@pytest.fixture(scope="session")
def env(request):
    """
    Environment fixture - provides the environment name
    
    Returns:
        str: Environment name (dev, staging, production)
    
    Usage:
        def test_example(env):
            print(f"Running on {env}")
    """
    env_value = request.config.getoption("--env")
    # Normalize 'prod' to 'production'
    if env_value == "prod":
        env_value = "production"
    return env_value


@pytest.fixture(scope="session")
def browser_config(request):
    """
    Browser configuration fixture
    
    Returns:
        dict: Browser configuration with 'name' and 'headless' keys
    
    Usage:
        def test_example(browser_config):
            print(f"Browser: {browser_config['name']}")
            print(f"Headless: {browser_config['headless']}")
    """
    return {
        "name": request.config.getoption("--test-browser"),
        "headless": request.config.getoption("--headless")
    }


@pytest.fixture
def multi_project_config(env):
    """
    Multi-project configuration - Dynamically loads from projects.yaml
    Returns URLs for different projects in current environment
    Supports: staging, production
    
    Usage:
        def test_example(multi_project_config):
            bookslot_url = multi_project_config['bookslot']['ui_url']
            print(f"BookSlot URL: {bookslot_url}")
    """
    from pathlib import Path
    import yaml
    
    logger.debug(f"multi_project_config: env '{env}'")

    # Load projects.yaml directly
    config_path = Path(__file__).parent / "config" / "projects.yaml"

    if config_path.exists():
        with open(config_path, 'r') as f:
            projects_data = yaml.safe_load(f)
            projects_config = projects_data.get('projects', {})
        logger.debug("multi_project_config: loaded projects.yaml")
    else:
        projects_config = {}
        logger.warning(f"multi_project_config: projects.yaml not found at {config_path}")

    # Build project URLs dictionary for current environment
    result = {}
    for project_name in ['bookslot', 'patientintake', 'callcenter']:
        if project_name in projects_config:
            project = projects_config[project_name]
            env_config = project.get('environments', {}).get(env, {})
            if env_config:
                result[project_name] = env_config
                logger.debug(
                    f"multi_project_config: {project_name}.{env} -> {env_config.get('ui_url')}"
                )

    # Fail loudly if configuration is missing - no silent fallback to hardcoded values
    if not result:
        error_msg = (
            f"[CONFIG] ERROR: No configuration found for environment '{env}' in projects.yaml\n"
            f"Config file: {config_path}\n"
            f"Available environments in projects.yaml: staging, production\n"
            f"Please ensure projects.yaml exists and contains valid configuration."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.debug(
        f"multi_project_config: final bookslot url: "
        f"{result.get('bookslot', {}).get('ui_url', 'NOT FOUND')}"
    )
    return result


@pytest.fixture(scope="function")
def human_behavior(request):
    """
    Human Behavior Simulator fixture
    
    Provides human-like interaction simulation for tests.
    Automatically integrates with 'browser' or 'page' fixtures.
    
    Configuration:
        - Controlled via config/human_behavior.yaml
        - Command line: --enable-human-behavior / --disable-human-behavior
        - Intensity: --human-behavior-intensity [minimal|normal|high]
    
    Usage:
        def test_with_human_behavior(human_behavior):
            human_behavior.type_text(element, "Hello World")
            human_behavior.click_element(button)
            human_behavior.scroll_page('bottom')
    
    Or use pytest marker:
        @pytest.mark.human_like
        def test_example(browser):
            # Automatically applies human-like behavior
            pass
    """
    # Check for command-line overrides
    enable_cli = request.config.getoption("--enable-human-behavior")
    disable_cli = request.config.getoption("--disable-human-behavior")
    intensity = request.config.getoption("--human-behavior-intensity")
    
    # Determine if enabled
    if disable_cli:
        enabled = False
    elif enable_cli:
        enabled = True
    else:
        # Check if test has 'human_like' marker
        enabled = bool(request.node.get_closest_marker('human_like'))
        if not enabled:
            # Use config default
            config = get_behavior_config()
            enabled = config.is_enabled()
    
    # Get driver from available fixtures
    driver = None
    try:
        # Try Playwright first
        if 'page' in request.fixturenames:
            driver = request.getfixturevalue('page')
        elif 'browser' in request.fixturenames:
            driver = request.getfixturevalue('browser')
        elif 'driver' in request.fixturenames:
            driver = request.getfixturevalue('driver')
    except Exception as e:
        logger.warning(f"human_behavior: could not get driver fixture: {e}")

    if driver is None:
        logger.warning("human_behavior: no driver found - returning MockSimulator")
        # Return a mock object
        class MockSimulator:
            def type_text(self, *args, **kwargs): return True
            def click_element(self, *args, **kwargs): return True
            def scroll_page(self, *args, **kwargs): return True
            def random_mouse_movements(self, *args, **kwargs): return True
            def random_page_interactions(self, *args, **kwargs): return True
            def simulate_idle(self, *args, **kwargs): return True
        
        return MockSimulator()
    
    # Create simulator
    simulator = HumanBehaviorSimulator(driver, enabled=enabled)
    
    # Log status
    status = "ENABLED" if enabled else "DISABLED"
    logger.info(f"human_behavior: {status} (intensity: {intensity})")

    # Auto-execute initial behaviors if marker present
    if request.node.get_closest_marker('human_like') and enabled:
        try:
            simulator.random_mouse_movements(steps=5)
            simulator.scroll_page('down', distance=300)
        except Exception as e:
            logger.warning(f"human_behavior: initial behaviors failed: {e}")
    
    return simulator


@pytest.fixture(scope="function", autouse=True)
def auto_human_behavior_marker(request):
    """
    Auto-apply human behavior to tests marked with @pytest.mark.human_like
    
    This fixture runs automatically for all tests and checks for the marker.
    """
    if request.node.get_closest_marker('human_like'):
        logger.info(f"auto_human_behavior_marker: applying to test '{request.node.name}'")


# ============================================================================
# FAKE DATA GENERATOR FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def fake_bookslot_data():
    """
    Generate a fresh fake bookslot payload for each test.
    
    Usage:
        def test_bookslot(fake_bookslot_data):
            first_name = fake_bookslot_data['first_name']
            email = fake_bookslot_data['email']
    """
    return generate_bookslot_payload()


@pytest.fixture(scope="function")
def fake_bookslot_batch():
    """
    Generate a batch of 5 fake bookslot payloads for each test.
    
    Usage:
        def test_multiple_bookslots(fake_bookslot_batch):
            for data in fake_bookslot_batch:
                # Use each payload
                pass
    """
    return [generate_bookslot_payload() for _ in range(5)]


@pytest.fixture(scope="session")
def bookslot_data_file():
    """
    Load bookslot data from pre-generated file (session-scoped).
    
    Usage:
        def test_with_file_data(bookslot_data_file):
            for data in bookslot_data_file:
                # Use payload from file
                pass
    """
    try:
        return load_bookslot_data("bookslot_data.json")
    except FileNotFoundError:
        # Generate if file doesn't exist
        from utils.fake_data_generator import generate_and_save_bookslot_data
        return generate_and_save_bookslot_data(count=10)


# ============================================================================
# PLAYWRIGHT CONTEXT OVERRIDE - Enable Video Recording for ALL Tests
# ============================================================================

@pytest.fixture(scope="function")
def context(browser, browser_context_args, request):
    """
    Override pytest-playwright's context fixture to enable video recording.
    
    This enables video recording for ALL tests using the 'page' fixture.
    Videos are organized by project: videos/bookslot/, videos/patientintake/, etc.
    """
    from pathlib import Path
    
    # Determine project from test path or markers
    test_path = str(request.fspath)
    if "bookslot" in test_path.lower():
        project = "bookslot"
    elif "patientintake" in test_path.lower():
        project = "patientintake"
    elif "callcenter" in test_path.lower():
        project = "callcenter"
    else:
        project = "other"
    
    # Create project-specific videos directory
    videos_dir = Path("videos") / project
    videos_dir.mkdir(parents=True, exist_ok=True)
    
    # Add video recording to context args
    context_args = {
        **browser_context_args,
        "record_video_dir": str(videos_dir),
        "record_video_size": {"width": 1920, "height": 1080}
    }
    
    # Create context with video recording
    context = browser.new_context(**context_args)

    _test_name = request.node.nodeid
    logger.info(f"context SETUP: video recording started -> {videos_dir} [{_test_name}]")
    audit_logger.log_action("video_recording", {
        "event": "start", "fixture": "context", "project": project,
        "video_dir": str(videos_dir), "test_name": _test_name,
    })

    yield context

    # Close context (finalizes video recording)
    context.close()
    logger.info(f"context TEARDOWN: video finalized [{_test_name}]")
    audit_logger.log_action("video_recording", {
        "event": "stop", "fixture": "context", "project": project,
        "video_dir": str(videos_dir), "test_name": _test_name,
    })


# ============================================================================
# SMART ACTIONS FIXTURE
# ============================================================================

@pytest.fixture(scope="function")
def smart_actions(page, human_behavior):
    """
    Provides SmartActions instance with automatic context-aware delays.
    
    This eliminates manual delay calls throughout test code!
    
    Usage:
        def test_bookslot(smart_actions, fake_bookslot_data, page):
            smart_actions.type_text(page.locator("#name"), fake_bookslot_data['first_name'], "First Name")
            smart_actions.button_click(page.locator("#submit"), "Submit")
    """
    from framework.core.smart_actions import SmartActions
    
    enable_human = human_behavior is not None
    return SmartActions(page, enable_human=enable_human, verbose=enable_human)


# ============================================================================
# PLAYWRIGHT BROWSER CONFIGURATION (Modern & Optimized)
# ============================================================================

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    🎯 GLOBAL BROWSER CONTEXT CONFIGURATION
    
    Override pytest-playwright's default browser context to use maximized window.
    
    Why viewport=None?
    - Default: pytest-playwright uses 1280x720 fixed viewport
    - With None: Browser uses actual window size (responsive testing)
    - Best for: Modern responsive apps, real-world scenarios
    
    Scope: session (configured once, reused across all tests)
    Applies to: All tests using 'page', 'context' fixtures from pytest-playwright
    
    Can be overridden per test:
        @pytest.fixture
        def browser_context_args():
            return {"viewport": {"width": 1920, "height": 1080}}
    """
    return {
        **browser_context_args,
        "viewport": None,  # None = full window size (maximized/responsive)
        "no_viewport": True,  # Explicitly disable viewport emulation
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """
    🚀 GLOBAL BROWSER LAUNCH CONFIGURATION
    
    Override browser launch arguments for optimal testing experience.
    
    Why --start-maximized?
    - Ensures browser opens in full-screen mode
    - Better visibility during test execution
    - Matches real user experience
    
    Cross-browser notes:
    - Chromium/Chrome: --start-maximized works perfectly
    - Firefox: Uses viewport=None from browser_context_args
    - WebKit: Uses viewport=None from browser_context_args
    
    Scope: session (configured once, reused across all tests)
    
    Can be extended per test:
        @pytest.fixture
        def browser_type_launch_args():
            return {"args": ["--start-maximized", "--disable-extensions"]}
    """
    return {
        **browser_type_launch_args,
        "args": [
            "--start-maximized",  # Start browser in maximized window
        ],
    }


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


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to attach videos and screenshots to Allure reports.
    Runs after each test completes.
    """
    outcome = yield
    report = outcome.get_result()
    
    # Log test execution phase
    if report.when == "call":
        test_name = item.nodeid
        if report.passed:
            logger.info(f"✓ TEST PASSED: {test_name}")
            audit_logger.log_test_end(test_name, "passed", report.duration)
        elif report.failed:
            logger.error(f"✗ TEST FAILED: {test_name}")
            audit_logger.log_test_end(test_name, "failed", report.duration)
            if call.excinfo:
                audit_logger.log_error(
                    error_type=call.excinfo.typename,
                    error_message=str(call.excinfo.value),
                    stack_trace=str(call.excinfo.traceback)
                )
        elif report.skipped:
            logger.warning(f"⊘ TEST SKIPPED: {test_name}")
            audit_logger.log_test_end(test_name, "skipped", report.duration)
    
    # Only process test execution phase (not setup/teardown)
    if report.when == "call":
        # Try to attach video from page fixture
        if "page" in item.funcargs:
            page = item.funcargs["page"]
            try:
                from pathlib import Path
                import allure
                
                # Get video path from page
                video_path = page.video.path()
                if video_path and Path(video_path).exists():
                    # Close page to finalize video
                    page.context.close()
                    
                    # Attach video to Allure report
                    with open(video_path, "rb") as video_file:
                        allure.attach(
                            video_file.read(),
                            name=f"{item.name}_video",
                            attachment_type=allure.attachment_type.WEBM
                        )
                    logger.info(f"✓ Video recorded and attached to Allure: {video_path}")
                    audit_logger.log_screenshot(str(video_path), reason="video_capture", test_name=item.nodeid)
            except Exception as e:
                logger.warning(f"could not attach video to Allure report: {e}")


def pytest_sessionstart(session):
    """Hook called at test session start"""
    logger.info("="*80)
    logger.info("TEST SESSION STARTED")
    logger.info("="*80)
    audit_logger.log_action("session_start", {
        "platform": platform.system(),
        "hostname": socket.gethostname(),
        "python_version": platform.python_version(),
        "pytest_version": pytest.__version__
    })


def pytest_sessionfinish(session, exitstatus):
    """Hook called at test session end"""
    logger.info("="*80)
    logger.info(f"TEST SESSION FINISHED (exit status: {exitstatus})")
    logger.info("="*80)
    audit_logger.log_action("session_end", {
        "exit_status": exitstatus,
        "total_collected": len(session.items) if hasattr(session, 'items') else 0
    })


def pytest_runtest_setup(item):
    """Hook called before each test setup"""
    logger.info(f"→ Setting up test: {item.nodeid}")
    audit_logger.log_test_start(item.nodeid, item.fspath.basename)


def pytest_runtest_teardown(item, nextitem):
    """Hook called after each test teardown"""
    logger.info(f"← Tearing down test: {item.nodeid}")
    audit_logger.log_action("test_teardown", {"test": item.nodeid})


def pytest_warning_recorded(warning_message, when, nodeid, location):
    """
    Hook called when a warning is captured.
    Ensures all warnings are logged to audit trail.
    """
    import warnings
    
    # Extract warning details
    category = warning_message.category.__name__ if hasattr(warning_message, 'category') else "Unknown"
    message = str(warning_message.message) if hasattr(warning_message, 'message') else str(warning_message)
    
    # Get source location
    filename = location[0] if location else None
    lineno = location[1] if location and len(location) > 1 else None
    
    # Log to standard logger
    logger.warning(f"⚠ {category}: {message}")
    if filename:
        logger.warning(f"  Source: {filename}:{lineno}")
    
    # Log to audit trail
    audit_logger.log_warning(
        warning_category=category,
        warning_message=message,
        source_file=filename,
        source_line=lineno
    )
