"""
Fixtures Module for Bookslot Tests

Centralized fixtures for test data, page preconditions, and helpers.
Imported by conftest.py.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any


# ==================== TEST DATA FIXTURES ====================
# NOTE: valid_basic_info, valid_personal_info, and valid_insurance_info
# are defined in conftest.py (via BookslotDataHelper). Do NOT redefine here
# to avoid pytest fixture collision from `from tests.bookslot.fixtures import *`.


@pytest.fixture
def invalid_basic_info_email() -> Dict[str, str]:
    """Invalid basic info test data - bad email"""
    return {
        "name": "Test User",
        "email": "invalid-email",
        "phone": "5555551234"
    }


@pytest.fixture
def invalid_basic_info_phone() -> Dict[str, str]:
    """Invalid basic info test data - bad phone"""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "123"
    }


@pytest.fixture
def valid_personal_info_special_chars() -> Dict[str, str]:
    """Valid personal info with special characters"""
    dob = (datetime.now() - timedelta(days=365*25)).strftime("%Y-%m-%d")
    return {
        "first_name": "Mary-Jane",
        "last_name": "O'Brien",
        "dob": dob,
        "address": "456 Oak Avenue",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001"
    }


@pytest.fixture
def valid_insurance_info_aetna() -> Dict[str, str]:
    """Valid insurance info for Aetna"""
    timestamp = datetime.now().strftime("%H%M%S")
    return {
        "member_id": f"AET{timestamp}",
        "group_number": f"GRP{timestamp}",
        "payer": "Aetna"
    }


@pytest.fixture
def valid_insurance_info_uhc() -> Dict[str, str]:
    """Valid insurance info for UnitedHealthcare"""
    timestamp = datetime.now().strftime("%H%M%S")
    return {
        "member_id": f"UHC{timestamp}",
        "group_number": f"GRP{timestamp}",
        "payer": "UnitedHealthcare"
    }


# ==================== BOUNDARY/EDGE CASE FIXTURES ====================

@pytest.fixture
def max_length_names() -> Dict[str, str]:
    """Maximum length names for boundary testing"""
    return {
        "first_name": "A" * 50,
        "last_name": "B" * 50
    }


@pytest.fixture
def max_length_address() -> str:
    """Maximum length address for boundary testing"""
    return "123 Main Street, Apartment 4567, Building C" * 4  # ~200 chars


@pytest.fixture
def special_char_names() -> Dict[str, tuple]:
    """Names with special characters for testing"""
    return {
        "hyphens": ("Mary-Jane", "Smith-Jones"),
        "apostrophes": ("Patrick", "O'Brien"),
        "accents": ("José", "García"),
        "spaces": ("Mary Ann", "Van Der Berg")
    }


@pytest.fixture
def edge_case_dates() -> Dict[str, str]:
    """Edge case dates for testing"""
    today = datetime.now()
    return {
        "18_years_ago": (today - timedelta(days=365*18)).strftime("%Y-%m-%d"),
        "100_years_ago": (today - timedelta(days=365*100)).strftime("%Y-%m-%d"),
        "yesterday": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
        "tomorrow": (today + timedelta(days=1)).strftime("%Y-%m-%d")
    }


# ==================== COLLECTION FIXTURES ====================

@pytest.fixture
def all_us_states() -> list:
    """All US states for dropdown validation"""
    return [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]


@pytest.fixture
def valid_zip_codes() -> list:
    """Valid zip code formats"""
    return [
        "12345",
        "12345-6789",
        "02101",
        "90210",
        "10001"
    ]


@pytest.fixture
def invalid_zip_codes() -> list:
    """Invalid zip code formats"""
    return [
        "123",
        "ABCDE",
        "12345678",
        "12-345",
        ""
    ]


@pytest.fixture
def insurance_payers() -> list:
    """Common insurance payers for testing"""
    return [
        "Blue Cross Blue Shield",
        "Aetna",
        "UnitedHealthcare",
        "Cigna",
        "Humana",
        "Kaiser Permanente"
    ]


@pytest.fixture
def referral_sources() -> list:
    """Referral sources for testing"""
    return [
        "doctor",
        "online",
        "insurance",
        "friend",
        "advertisement",
        "other"
    ]


# ==================== ENVIRONMENT FIXTURES ====================

@pytest.fixture(scope="session")
def base_url(request) -> str:
    """Base URL for Bookslot application"""
    env = request.config.getoption("--env", default="staging")
    
    urls = {
        "staging": "https://bookslot-staging.centerforvein.com",
        "production": "https://bookslot.centerforvein.com",
        "local": "http://localhost:3000"
    }
    
    return urls.get(env, urls["staging"])


@pytest.fixture(scope="session")
def workflow_id(request) -> str:
    """Workflow ID for URL testing"""
    env = request.config.getoption("--env", default="staging")
    
    workflow_ids = {
        "staging": "WF_STAGE_001",
        "production": "PROD_WF_001",
        "local": "LOCAL_WF_001"
    }
    
    return workflow_ids.get(env, workflow_ids["staging"])


# ==================== TIMEOUT FIXTURES ====================

@pytest.fixture
def short_timeout() -> int:
    """Short timeout for fast operations (5 seconds)"""
    return 5000


@pytest.fixture
def medium_timeout() -> int:
    """Medium timeout for standard operations (10 seconds)"""
    return 10000


@pytest.fixture
def long_timeout() -> int:
    """Long timeout for slow operations (30 seconds)"""
    return 30000


# ==================== API FIXTURES ====================

@pytest.fixture(scope="session")
def api_base_url(request) -> str:
    """API base URL for API testing"""
    env = request.config.getoption("--env", default="staging")
    
    api_urls = {
        "staging": "https://api-staging.centerforvein.com",
        "production": "https://api.centerforvein.com",
        "local": "http://localhost:8000"
    }
    
    return api_urls.get(env, api_urls["staging"])


@pytest.fixture
def api_headers() -> Dict[str, str]:
    """API headers for requests"""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Test-Run": "true"
    }


# ==================== CLEANUP FIXTURES ====================

@pytest.fixture
def cleanup_test_bookings():
    """Cleanup fixture to delete test bookings after test"""
    created_booking_ids = []
    
    yield created_booking_ids
    
    # Cleanup logic here (call API to delete test bookings)
    # This runs after test completion
    if created_booking_ids:
        # TODO: Implement cleanup API calls
        pass


# ==================== URL TESTING FIXTURES ====================
# Added: 2026-02-25
# Purpose: URL workflow testing support
# Pattern: Follows existing fixture organization
# ================================================================

import asyncio
from framework.microservices.url_testing_service import URLTestingService, URLDataService, URLValidationService
from framework.testing.url_data_manager import URLDataManager
from framework.testing.url_builder import URLBuilder, URLFormat
from framework.testing.url_validator import URLValidator


@pytest.fixture(scope="session")
def url_testing_service():
    """
    URL Testing Microservice instance
    
    Extends: BaseService from framework.microservices.base
    Lifecycle: Session-scoped (initialize once)
    """
    service = URLTestingService()
    
    # Start service
    asyncio.run(service.start())
    
    yield service
    
    # Stop service
    asyncio.run(service.stop())


@pytest.fixture(scope="session")
def url_data_service():
    """
    URL Data Service instance
    
    Extends: BaseService
    Lifecycle: Session-scoped
    """
    service = URLDataService()
    
    # Start service
    asyncio.run(service.start())
    
    yield service
    
    # Stop service
    asyncio.run(service.stop())


@pytest.fixture(scope="session")
def url_validation_service():
    """
    URL Validation Service instance
    
    Extends: BaseService
    Lifecycle: Session-scoped
    """
    service = URLValidationService()
    
    # Start service
    asyncio.run(service.start())
    
    yield service
    
    # Stop service
    asyncio.run(service.stop())


@pytest.fixture(scope="session")
def url_data_manager():
    """
    URL Data Manager instance
    
    Pattern: Manager (follows ProjectManager, SessionManager)
    Lifecycle: Session-scoped (shared across tests)
    """
    return URLDataManager(project="bookslot")


@pytest.fixture
def url_builder(base_url: str):
    """
    URL Builder instance
    
    Pattern: Builder (follows QueryBuilder, CommandBuilder)
    Lifecycle: Function-scoped (fresh per test)
    Dependencies: Uses base_url fixture
    """
    return URLBuilder(base_url=base_url, url_format=URLFormat.QUERY_STRING)


@pytest.fixture
def url_validator(page):
    """
    URL Validator instance
    
    Pattern: Validator (follows DBValidator, PreFlightValidator)
    Lifecycle: Function-scoped (per test)
    Dependencies: Uses page fixture (Playwright)
    """
    return URLValidator(page=page)


@pytest.fixture
def workflow_test_cases(url_data_manager, environment: str):
    """
    Load workflow test cases for environment
    
    Data Source: test_data/bookslot/bookslot_workflows.json
    Pattern: Data fixture (follows existing test data fixtures)
    """
    return url_data_manager.load_test_cases(environment=environment)


@pytest.fixture(params=["staging"])
def environment(request):
    """
    Parameterized environment fixture
    
    Generates tests for staging (can be extended to production)
    Pattern: Parametrization fixture
    """
    return request.param


@pytest.fixture
def url_test_case(workflow_test_cases, request):
    """
    Single URL test case from test data
    
    Pattern: Parametrized test case fixture
    Usage: @pytest.mark.parametrize with indirect=True
    """
    if hasattr(request, 'param'):
        workflow_id = request.param
        for test_case in workflow_test_cases:
            if test_case.workflow_id == workflow_id:
                return test_case
        
        pytest.skip(f"Workflow not found: {workflow_id}")
    else:
        # Return first test case if no param specified
        if workflow_test_cases:
            return workflow_test_cases[0]
        pytest.skip("No workflow test cases available")


@pytest.fixture
def url_workflow_p1_cases(url_data_manager):
    """Get all P1 (Basic Info) workflow test cases"""
    return url_data_manager.get_test_cases_by_page("P1", environment="staging")


@pytest.fixture
def url_workflow_p2_cases(url_data_manager):
    """Get all P2 (Insurance) workflow test cases"""
    return url_data_manager.get_test_cases_by_page("P2", environment="staging")


@pytest.fixture
def url_workflow_p3_cases(url_data_manager):
    """Get all P3 (Schedule) workflow test cases"""
    return url_data_manager.get_test_cases_by_page("P3", environment="staging")


@pytest.fixture
def url_workflow_p4_cases(url_data_manager):
    """Get all P4 (Reason) workflow test cases"""
    return url_data_manager.get_test_cases_by_page("P4", environment="staging")


@pytest.fixture
def url_workflow_p5_cases(url_data_manager):
    """Get all P5 (Confirmation) workflow test cases"""
    return url_data_manager.get_test_cases_by_page("P5", environment="staging")


@pytest.fixture
def url_workflow_p6_cases(url_data_manager):
    """Get all P6 (Review) workflow test cases"""
    return url_data_manager.get_test_cases_by_page("P6", environment="staging")


@pytest.fixture
def url_workflow_p7_cases(url_data_manager):
    """Get all P7 (Thank You) workflow test cases"""
    return url_data_manager.get_test_cases_by_page("P7", environment="staging")
