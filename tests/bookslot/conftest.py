"""
Bookslot Test Suite - Pytest Configuration & Fixtures

This conftest provides all fixtures needed for Bookslot testing including:
- Page preconditions (navigate to specific pages)
- Test data fixtures
- Browser/driver fixtures
- Common setup/teardown

Follows Test Design Matrix principles:
- Independent tests (no test-to-test dependencies)
- Reusable preconditions via fixtures
- Page Object Model integration
"""

import pytest
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.sync_api import Page, BrowserContext

# Import helpers
from tests.bookslot.helpers.navigation_helper import BookslotNavigator
from tests.bookslot.helpers.data_helper import BookslotDataHelper
from tests.bookslot.helpers.validation_helper import BookslotValidationHelper

# Import additional fixtures and test data modules
from tests.bookslot.fixtures import *  # Additional fixtures (boundaries, collections, API, cleanup)
from tests.bookslot import data  # Test data module (generators, validators, constants)


# ============================================================================
# NAVIGATION PRECONDITION FIXTURES (Per Test Design Matrix)
# ============================================================================

@pytest.fixture
def bookslot_nav(page: Page, smart_actions, fake_bookslot_data, multi_project_config) -> BookslotNavigator:
    """
    Provides navigation helper for Bookslot sequential flow.
    
    Usage:
        def test_something(bookslot_nav):
            bookslot_nav.navigate_to_scheduler()  # Navigates through P1→P2→P3
    """
    return BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)


@pytest.fixture
def navigation_helper(bookslot_nav: BookslotNavigator) -> BookslotNavigator:
    """
    Alias for bookslot_nav to maintain backward compatibility.

    Used in: e2e/test_complete_journeys.py
    Canonical name: bookslot_nav
    """
    return bookslot_nav


@pytest.fixture
def at_basic_info(page: Page, bookslot_nav: BookslotNavigator):
    """
    Precondition: User is at Basic Info page (P1).
    No navigation needed - this is the entry point.
    
    Usage:
        @pytest.mark.smoke
        def test_basic_info_load(at_basic_info):
            # Test P1 page components
    """
    bookslot_nav.navigate_to_basic_info()
    return bookslot_nav


@pytest.fixture
def at_event_type(page: Page, bookslot_nav: BookslotNavigator):
    """
    Precondition: User is at Event Type page (P2).
    Navigation: P1 (Basic Info) completed → Now at P2
    
    Usage:
        def test_event_type_selection(at_event_type):
            # Test P2 page components
    """
    bookslot_nav.navigate_to_event_type()
    return bookslot_nav


@pytest.fixture
def at_scheduler(page: Page, bookslot_nav: BookslotNavigator):
    """
    Precondition: User is at Scheduler page (P3).
    Navigation: P1 → P2 completed → Now at P3
    
    Usage:
        def test_scheduler_slots(at_scheduler):
            # Test P3 page components
    """
    bookslot_nav.navigate_to_scheduler()
    return bookslot_nav


@pytest.fixture
def at_personal_info(page: Page, bookslot_nav: BookslotNavigator):
    """
    Precondition: User is at Personal Info page (P4).
    Navigation: P1 → P2 → P3 completed → Now at P4
    
    Usage:
        def test_personal_info_validation(at_personal_info):
            # Test P4 page components
    """
    bookslot_nav.navigate_to_personal_info()
    return bookslot_nav


@pytest.fixture
def at_referral(page: Page, bookslot_nav: BookslotNavigator):
    """
    Precondition: User is at Referral page (P5).
    Navigation: P1 → P2 → P3 → P4 completed → Now at P5
    
    Usage:
        def test_referral_options(at_referral):
            # Test P5 page components
    """
    bookslot_nav.navigate_to_referral()
    return bookslot_nav


@pytest.fixture
def at_insurance(page: Page, bookslot_nav: BookslotNavigator):
    """
    Precondition: User is at Insurance page (P6).
    Navigation: P1 → P2 → P3 → P4 → P5 completed → Now at P6
    
    Usage:
        def test_insurance_validation(at_insurance):
            # Test P6 page components
    """
    bookslot_nav.navigate_to_insurance()
    return bookslot_nav


@pytest.fixture
def at_success(page: Page, bookslot_nav: BookslotNavigator):
    """
    Precondition: User is at Success page (P7).
    Navigation: P1 → P2 → P3 → P4 → P5 → P6 completed → Now at P7
    
    Usage:
        def test_success_confirmation(at_success):
            # Test P7 page components
    """
    bookslot_nav.navigate_to_success()
    return bookslot_nav


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
def test_data_helper() -> BookslotDataHelper:
    """Provides test data generation helper"""
    return BookslotDataHelper()


@pytest.fixture
def valid_basic_info(test_data_helper: BookslotDataHelper) -> Dict[str, str]:
    """
    Valid basic info data for P1.

    Schema provides BOTH split and combined name keys:
    - first_name, last_name: used by P1 page tests (selectors: [name='firstName'])
    - name: used by E2E tests (selectors: [name='name'])
    - email, phone: used by both
    """
    raw = test_data_helper.get_valid_basic_info()
    return {
        "first_name": raw["first_name"],
        "last_name": raw["last_name"],
        "name": f"{raw['first_name']} {raw['last_name']}",
        "email": raw["email"],
        "phone": raw["phone"],
    }


@pytest.fixture
def valid_personal_info(test_data_helper: BookslotDataHelper) -> Dict[str, str]:
    """
    Valid personal info data for P4.

    Schema provides BOTH zip key variants:
    - first_name, last_name: used by page tests and test_complete_journeys
    - dob, address, city, state: used by all consumers
    - zip_code: used by page tests (selector [name='zipCode']) and test_complete_journeys
    - zip: used by test_happy_path (selector [name='zip'])
    """
    raw = test_data_helper.get_valid_personal_info()
    raw_basic = test_data_helper.get_valid_basic_info()
    zip_val = raw.get("zip_code", raw.get("zip", "02101"))
    return {
        "first_name": raw_basic["first_name"],
        "last_name": raw_basic["last_name"],
        "dob": raw["dob"],
        "address": raw["address"],
        "city": raw["city"],
        "state": raw["state"],
        "zip_code": zip_val,
        "zip": zip_val,
    }


@pytest.fixture
def valid_insurance_info(test_data_helper: BookslotDataHelper) -> Dict[str, str]:
    """
    Valid insurance info data for P6.

    Schema: member_id, group_number, payer
    """
    raw = test_data_helper.get_valid_insurance_info()
    return {
        "member_id": raw["member_id"],
        "group_number": raw["group_number"],
        "payer": raw["payer"],
    }


@pytest.fixture(params=["AM", "PM"])
def time_slot_variant(request) -> str:
    """Parametrized fixture for AM/PM slot variants"""
    return request.param


@pytest.fixture(params=["web", "phone", "referral"])
def referral_source_variant(request) -> str:
    """Parametrized fixture for referral source variants"""
    return request.param


# ============================================================================
# VALIDATION HELPER FIXTURES
# ============================================================================

@pytest.fixture
def validation_helper(page: Page) -> BookslotValidationHelper:
    """Provides validation helper for common assertions"""
    return BookslotValidationHelper(page)


# ============================================================================
# ENVIRONMENT & CONFIGURATION
# ============================================================================

@pytest.fixture(scope="session")
def bookslot_base_url(env: str) -> str:
    """
    Get Bookslot base URL based on environment.
    
    Args:
        env: From framework config (staging, production)
    
    Returns:
        Base URL for Bookslot application
    """
    urls = {
        "staging": "https://bookslot-staging.centerforvein.com",
        "production": "https://bookslot.centerforvein.com",
    }
    return urls.get(env, urls["staging"])


@pytest.fixture(scope="session")
def bookslot_config() -> Dict[str, Any]:
    """
    Bookslot-specific configuration.
    
    Returns:
        Configuration dictionary with timeouts, settings, etc.
    """
    return {
        "page_load_timeout": 30000,
        "navigation_timeout": 60000,
        "slot_selection_timeout": 10000,
        "form_submission_timeout": 15000,
        "success_page_timeout": 10000,
        "enable_screenshots_on_failure": True,
        "enable_video_recording": True,
    }


# ============================================================================
# SETUP & TEARDOWN HOOKS
# ============================================================================

@pytest.fixture(autouse=True)
def bookslot_test_setup(page: Page, bookslot_base_url: str, bookslot_config: Dict[str, Any]):
    """
    Auto-used fixture for all Bookslot tests.
    Sets up page timeouts and configuration.
    """
    # Set timeouts
    page.set_default_timeout(bookslot_config["page_load_timeout"])
    page.set_default_navigation_timeout(bookslot_config["navigation_timeout"])
    
    # Yield control to test
    yield
    
    # Teardown (if needed)
    # Any cleanup logic here


# ============================================================================
# MARKERS CONFIGURATION (Can also be in pytest.ini)
# ============================================================================

def pytest_configure(config):
    """Register custom markers for Bookslot tests"""
    # Project markers
    config.addinivalue_line("markers", "bookslot: Bookslot project tests")
    config.addinivalue_line("markers", "modern_spa: Modern SPA application tests")
    
    # Test type markers
    config.addinivalue_line("markers", "smoke: Fast smoke tests for quick validation")
    config.addinivalue_line("markers", "validation: Component validation tests")
    config.addinivalue_line("markers", "regression: Full regression test suite")
    config.addinivalue_line("markers", "e2e: End-to-end sequential flow tests")
    
    # Priority markers
    config.addinivalue_line("markers", "critical: Critical/P0 tests that must pass")
    config.addinivalue_line("markers", "high: High priority/P1 tests")
    config.addinivalue_line("markers", "medium: Medium priority/P2 tests")
    
    # Execution markers
    config.addinivalue_line("markers", "ui_sequential: Tests that must run sequentially (not parallel)")
    config.addinivalue_line("markers", "parallel_safe: Tests safe for parallel execution")
    
    # Page markers
    config.addinivalue_line("markers", "p1_basic_info: Basic Info page (P1) tests")
    config.addinivalue_line("markers", "p2_event_type: Event Type page (P2) tests")
    config.addinivalue_line("markers", "p3_scheduler: Scheduler page (P3) tests")
    config.addinivalue_line("markers", "p4_personal_info: Personal Info page (P4) tests")
    config.addinivalue_line("markers", "p5_referral: Referral page (P5) tests")
    config.addinivalue_line("markers", "p6_insurance: Insurance page (P6) tests")
    config.addinivalue_line("markers", "p7_success: Success page (P7) tests")


# ============================================================================
# PYTEST COLLECTION HOOKS
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to ensure proper sequencing.
    ui_sequential tests will be marked appropriately.
    """
    for item in items:
        # Add bookslot marker to all tests in this directory
        if "bookslot" in str(item.fspath):
            item.add_marker(pytest.mark.bookslot)
        
        # Add parallel_safe marker by default unless ui_sequential
        if "ui_sequential" not in item.keywords:
            item.add_marker(pytest.mark.parallel_safe)
