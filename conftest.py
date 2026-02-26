"""
Root-level pytest configuration
This conftest.py registers command-line options for all tests in the project

Author: Lokendra Singh
Email: lokendra.singh@centerforvein.com
Website: www.centerforvein.com
"""

import pytest
import platform
import socket
import os
from datetime import datetime
from pathlib import Path
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


# ════════════════════════════════════════════════════════════════════════════
# DYNAMIC HTML REPORT GENERATION
# ════════════════════════════════════════════════════════════════════════════

def generate_unique_report_filename(project: str, environment: str, reports_dir: str = "reports") -> str:
    """
    Generate unique HTML report filename with format:
    projectname_EnvironmentName_DDMMYYYY_HHMMSS.html
    
    If file exists, append incremental number: _1, _2, etc.
    
    Args:
        project: Project name (e.g., 'bookslot', 'patientintake', 'callcenter')
        environment: Environment name (e.g., 'staging', 'production')
        reports_dir: Directory where reports are stored (default: 'reports')
    
    Returns:
        str: Unique report filename path (e.g., 'reports/bookslot_Staging_19022026_143052.html')
    
    Examples:
        >>> generate_unique_report_filename('bookslot', 'staging')
        'reports/bookslot_Staging_19022026_143052.html'
        
        >>> # If above file exists, returns:
        'reports/bookslot_Staging_19022026_143052_1.html'
    """
    # Ensure reports directory exists
    reports_path = Path(reports_dir)
    reports_path.mkdir(parents=True, exist_ok=True)
    
    # Normalize environment name (capitalize first letter)
    env_capitalized = environment.capitalize()
    
    # Generate timestamp in DDMMYYYY_HHMMSS format
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    
    # Create base filename: projectname_EnvironmentName_DDMMYYYY_HHMMSS.html
    base_filename = f"{project}_{env_capitalized}_{timestamp}.html"
    full_path = reports_path / base_filename
    
    # Check if file exists and add increment if needed
    if full_path.exists():
        increment = 1
        while True:
            # Create incremented filename: projectname_EnvironmentName_DDMMYYYY_HHMMSS_1.html
            incremented_filename = f"{project}_{env_capitalized}_{timestamp}_{increment}.html"
            incremented_path = reports_path / incremented_filename
            
            if not incremented_path.exists():
                full_path = incremented_path
                break
            
            increment += 1
            
            # Safety limit to prevent infinite loop
            if increment > 100:
                logger.warning(f"Too many report files with same timestamp. Using: {incremented_path}")
                full_path = incremented_path
                break
    
    # Return path as string
    return str(full_path)


def generate_unique_video_filename(project: str, environment: str, videos_dir: str, extension: str = "webm") -> Path:
    """
    Generate unique video filename with format:
    projectname_EnvironmentName_DDMMYYYY_HHMMSS.webm
    
    If file exists, append incremental number: _1, _2, etc.
    
    Args:
        project: Project name (e.g., 'bookslot', 'patientintake', 'callcenter')
        environment: Environment name (e.g., 'staging', 'production')
        videos_dir: Directory where videos are stored
        extension: File extension (default: 'webm')
    
    Returns:
        Path: Unique video filename path (e.g., Path('videos/bookslot/bookslot_Staging_19022026_143052.webm'))
    
    Examples:
        >>> generate_unique_video_filename('bookslot', 'staging', 'videos/bookslot')
        Path('videos/bookslot/bookslot_Staging_19022026_143052.webm')
        
        >>> # If above file exists, returns:
        Path('videos/bookslot/bookslot_Staging_19022026_143052_1.webm')
    """
    # Ensure videos directory exists
    videos_path = Path(videos_dir)
    videos_path.mkdir(parents=True, exist_ok=True)
    
    # Normalize environment name (capitalize first letter)
    env_capitalized = environment.capitalize()
    
    # Generate timestamp in DDMMYYYY_HHMMSS format (no colons for Windows compatibility)
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    
    # Create base filename: projectname_EnvironmentName_DDMMYYYY_HHMMSS.webm
    base_filename = f"{project}_{env_capitalized}_{timestamp}.{extension}"
    full_path = videos_path / base_filename
    
    # Check if file exists and add increment if needed
    if full_path.exists():
        increment = 1
        while True:
            # Create incremented filename: projectname_EnvironmentName_DDMMYYYY_HHMMSS_1.webm
            incremented_filename = f"{project}_{env_capitalized}_{timestamp}_{increment}.{extension}"
            incremented_path = videos_path / incremented_filename
            
            if not incremented_path.exists():
                full_path = incremented_path
                break
            
            increment += 1
            
            # Safety limit to prevent infinite loop
            if increment > 100:
                logger.warning(f"Too many video files with same timestamp. Using: {incremented_path}")
                full_path = incremented_path
                break
    
    return full_path


def pytest_configure(config):
    """
    Configure pytest with dynamic HTML report naming.
    
    Generates report name format: projectname_EnvironmentName_DDMMYYYY_HHMMSS.html
    If file exists, appends incremental number: _1, _2, etc.
    
    This hook runs before test collection, allowing us to dynamically set
    the HTML report path based on project, environment, and timestamp.
    """
    # Get project and environment from command line options
    project = config.getoption("--project", default="bookslot")
    environment = config.getoption("--env", default="staging")
    
    # Normalize 'prod' to 'production'
    if environment == "prod":
        environment = "production"
    
    # Check if HTML report is enabled (check if pytest-html plugin is active)
    if config.pluginmanager.hasplugin('html'):
        # Get current htmlpath option
        htmlpath = config.getoption('htmlpath')
        
        # Only generate dynamic name if default/static name is being used
        # This allows users to override with custom --html=custom_name.html
        if htmlpath in [None, 'reports/test_report.html', 'test_report.html', 'report.html']:
            # Generate unique report filename
            dynamic_report_path = generate_unique_report_filename(project, environment)
            
            # Update pytest config with new htmlpath
            config.option.htmlpath = dynamic_report_path
            
            logger.info(f"📊 HTML Report will be generated at: {dynamic_report_path}")
            audit_logger.log_action("html_report_configured", {
                "report_path": dynamic_report_path,
                "project": project,
                "environment": environment,
                "timestamp": datetime.now().isoformat()
            })
        else:
            # User provided custom report name, respect it
            logger.info(f"📊 Using custom HTML report path: {htmlpath}")
    else:
        logger.debug("pytest-html plugin not active, skipping dynamic report generation")


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

    # TEARDOWN: Get video path before closing context
    _test_name = request.node.nodeid
    video_path = None
    
    # Get all pages from context to find video path
    try:
        pages = context.pages
        if pages:
            # Get video path from first page (typically only one page per test)
            video_path = pages[0].video.path() if pages[0].video else None
            logger.debug(f"[context teardown] Retrieved video path: {video_path}")
    except Exception as e:
        logger.warning(f"[context teardown] Could not get video path: {e}")
    
    # Close context (finalizes video recording)
    context.close()
    logger.info(f"context TEARDOWN: video finalized [{_test_name}]")
    
    # RENAME VIDEO to dynamic format: projectname_EnvironmentName_DDMMYYYY_HHMMSS.webm
    if video_path:
        from pathlib import Path
        try:
            video_path_obj = Path(video_path)
            
            # Small delay to ensure file is fully written
            import time
            time.sleep(0.5)
            
            if video_path_obj.exists():
                # Get environment from pytest config
                env = request.config.getoption("--env", default="staging")
                
                # Generate unique video filename
                new_video_path = generate_unique_video_filename(
                    project=project,
                    environment=env,
                    videos_dir=str(videos_dir),
                    extension="webm"
                )
                
                # Rename video file
                video_path_obj.rename(new_video_path)
                logger.info(f"[context teardown] Video renamed: {new_video_path.name}")
                
                # Attach to Allure report
                try:
                    import allure
                    with open(new_video_path, "rb") as video_file:
                        allure.attach(
                            video_file.read(),
                            name=f"{request.node.name}_video",
                            attachment_type=allure.attachment_type.WEBM
                        )
                    logger.info(f"[context teardown] Video attached to Allure: {new_video_path.name}")
                except Exception as e:
                    logger.warning(f"[context teardown] Could not attach video to Allure: {e}")
                
                # Store video info in cache for pytest-html hooks
                relative_video_path = f"../videos/{project}/{new_video_path.name}"
                _video_info_cache[request.node.nodeid] = {
                    'video_path': relative_video_path,
                    'video_name': new_video_path.name
                }
                logger.info(f"[context teardown] Video info stored in cache: {new_video_path.name}")
                
                audit_logger.log_action("video_recording", {
                    "event": "renamed", "fixture": "context", "project": project,
                    "video_path": str(new_video_path), "test_name": _test_name,
                })
            else:
                logger.warning(f"[context teardown] Video file does not exist: {video_path_obj}")
                
        except Exception as e:
            logger.error(f"[context teardown] Error processing video: {e}")
            import traceback
            logger.debug(traceback.format_exc())
    
    # Log completion
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
    
    # Store all reports on the item for later access (needed for video attachment in teardown)
    if not hasattr(item, '_test_reports'):
        item._test_reports = []
    item._test_reports.append(report)
    
    # DEBUG: Log which phase we're in
    logger.debug(f"[ROOT CONFTEST] pytest_runtest_makereport called: report.when={report.when}, outcome={report.outcome}")
    
    # Initialize extras list if it doesn't exist
    if not hasattr(report, 'extra'):
        report.extra = []
    
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
    
    # Add video link to HTML report (after teardown when video is ready)
    # IMPORTANT: We need to add the extra to the CALL report, not the TEARDOWN report
    # because pytest-html only displays extras from the call phase
    if report.when == "teardown":
        if item.nodeid in _video_info_cache:
            from pytest_html import extras as pytest_extras
            
            video_info = _video_info_cache[item.nodeid]
            video_path = video_info['video_path']
            video_name = video_info['video_name']
            
            # Find the CALL report stored earlier and add the extra to it
            if hasattr(item, '_test_reports'):
                for stored_report in item._test_reports:
                    if stored_report.when == "call":
                        # Create clickable HTML link
                        video_link_html = f'<div class="video-link" style="margin: 10px 0;"><a href="{video_path}" target="_blank" style="color: #0066cc; text-decoration: none; font-weight: bold;">🎥 {video_name}</a></div>'
                        
                        # Add to call report's extras
                        if not hasattr(stored_report, 'extra'):
                            stored_report.extra = []
                        stored_report.extra.append(pytest_extras.html(video_link_html))
                        
                        logger.info(f"[pytest_runtest_makereport] ✓ Video link added to CALL report: {video_name}")
                        break
    
    # Video recording and attachment is handled by page fixtures (see tests/conftest.py)
    # Fixtures (bookslot_page, patientintake_page) handle:
    #   1. Video recording configuration
    #   2. Video renaming to dynamic format (project_Env_DDMMYYYY_HHMMSS.webm)
    #   3. Allure video attachment
    #   4. Storing video info on item._video_path and item._video_name
    # The pytest-html hooks below will inject video links into HTML reports


# ========================================================================
# VIDEO INFO CACHE - Store video paths for HTML report
# ========================================================================
_video_info_cache = {}  # Maps test nodeid -> {video_path, video_name}


def pytest_html_results_table_row(report, cells):
    """
    Hook to modify the HTML table row cells.
    This injects video links directly into the Links column.
    """
    if report.when == "call" and report.nodeid in _video_info_cache:
        video_info = _video_info_cache[report.nodeid]
        video_path = video_info['video_path']
        video_name = video_info['video_name']
        
        # Create clickable video link HTML
        video_link_html = f'<a href="{video_path}" target="_blank" style="color: #0066cc; text-decoration: none; font-weight: bold;">🎥 {video_name}</a>'
        
        # Find the Links column cell (usually the last one) and inject the video link
        try:
            # The cells list typically has: Result, Test, Duration, Links
            # We need to modify the Links cell (index -1 or 3)
            if len(cells) >= 4:
                # Links column is the 4th cell (index 3)
                links_cell = cells[3]
                # Check if it's an empty or existing links cell
                cells[3] = f'<td class="col-links">{video_link_html}</td>'
                logger.info(f"[pytest_html_results_table_row] ✓ Video link injected: {video_name}")
            else:
                logger.warning(f"[pytest_html_results_table_row] Unexpected cell count: {len(cells)}")
        except Exception as e:
            logger.warning(f"[pytest_html_results_table_row] Error: {e}")


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
    """Hook called at test session end - post-process HTML to inject video links"""
    logger.info("="*80)
    logger.info(f"TEST SESSION FINISHED (exit status: {exitstatus})")
    logger.info("="*80)
    audit_logger.log_action("session_end", {
        "exit_status": exitstatus,
        "total_collected": len(session.items) if hasattr(session, 'items') else 0
    })
    
    # Post-process HTML report to inject video links
    if _video_info_cache:
        logger.info(f"[sessionfinish] Found {len(_video_info_cache)} videos in cache")
        logger.info(f"[sessionfinish] Video links feature is working - videos attached to Allure reports")
        logger.info(f"[sessionfinish] Note: pytest-html extras injection requires additional integration")


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
