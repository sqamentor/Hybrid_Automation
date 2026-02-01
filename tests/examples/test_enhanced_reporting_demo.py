"""
Enhanced Report Demo Test
=========================

Author: Lokendra Singh (qa.lokendra@gmail.com)
Website: www.sqamentor.com
Assisted by: AI Claude

Description:
Demonstrates all enhanced reporting features including:
- Screenshots (success & failure)
- Test parameters display
- Markers display
- API call logging
- Database query logging
- Assertion logging
- Step-by-step logs
- Custom metadata

This test file serves as an example and documentation
of how to use the enhanced reporting fixtures.
"""

import time
from pathlib import Path

import pytest


@pytest.mark.smoke
@pytest.mark.critical
@pytest.mark.ui_only
def test_enhanced_report_demo_success(report_log, report_assertion, ui_url):
    """
    Demo test showing enhanced reporting for PASSED tests
    
    This test demonstrates:
    - Custom logging with report_log
    - Assertion tracking with report_assertion
    - Screenshots automatically captured on success
    - Test markers displayed in report
    """
    
    # Step 1: Initialize
    report_log("Starting enhanced report demo test", "INFO")
    report_log(f"UI URL: {ui_url}", "DEBUG")
    
    # Step 2: Perform some validations
    report_log("Validating test data...", "INFO")
    
    expected_url = ui_url
    actual_url = ui_url
    report_assertion(
        assertion_type="URL Validation",
        expected=expected_url,
        actual=actual_url,
        passed=True,
        message="URL matches expected value"
    )
    
    # Step 3: More validations
    report_log("Checking application readiness...", "INFO")
    
    expected_status = "ready"
    actual_status = "ready"
    report_assertion(
        assertion_type="Status Check",
        expected=expected_status,
        actual=actual_status,
        passed=True,
        message="Application is ready"
    )
    
    # Step 4: Complete
    report_log("Test completed successfully", "INFO")
    
    assert True, "Demo test passed"


@pytest.mark.integration
@pytest.mark.high
def test_enhanced_report_with_api(report_log, report_api_call, report_assertion):
    """
    Demo test showing API call logging in reports
    
    This test demonstrates:
    - API call logging with response times
    - Request/response data capture
    - API status validation
    """
    
    report_log("Starting API integration test", "INFO")
    
    # Simulate API call
    report_log("Making API request to fetch user data", "INFO")
    
    # Log API call (simulated)
    report_api_call(
        method="GET",
        url="https://api.example.com/users/123",
        status_code=200,
        response_time=125.5,
        request_data={"user_id": 123},
        response_data={"id": 123, "name": "John Doe", "email": "john@example.com"}
    )
    
    # Validate API response
    expected_status = 200
    actual_status = 200
    report_assertion(
        assertion_type="API Status Code",
        expected=expected_status,
        actual=actual_status,
        passed=True,
        message="API returned successful response"
    )
    
    report_log("API call completed successfully", "INFO")
    
    assert True, "API integration test passed"


@pytest.mark.integration
@pytest.mark.db_only
@pytest.mark.medium
def test_enhanced_report_with_database(report_log, report_db_query, report_assertion):
    """
    Demo test showing database query logging in reports
    
    This test demonstrates:
    - Database query logging
    - Execution time tracking
    - Rows affected tracking
    - Query validation
    """
    
    report_log("Starting database integration test", "INFO")
    
    # Simulate database query
    report_log("Executing SELECT query on users table", "INFO")
    
    # Log database query (simulated)
    report_db_query(
        query="SELECT * FROM users WHERE active = 1 ORDER BY created_at DESC LIMIT 10",
        execution_time=45.2,
        rows_affected=10
    )
    
    # Validate query result
    expected_rows = 10
    actual_rows = 10
    report_assertion(
        assertion_type="Database Row Count",
        expected=expected_rows,
        actual=actual_rows,
        passed=True,
        message="Query returned expected number of rows"
    )
    
    # Simulate UPDATE query
    report_log("Executing UPDATE query to mark users as verified", "INFO")
    
    report_db_query(
        query="UPDATE users SET verified = 1 WHERE email_confirmed = 1",
        execution_time=102.8,
        rows_affected=5
    )
    
    report_log("Database operations completed successfully", "INFO")
    
    assert True, "Database integration test passed"


@pytest.mark.regression
@pytest.mark.low
@pytest.mark.parametrize("test_input,expected", [
    ("hello", 5),
    ("world", 5),
    ("python", 6),
])
def test_enhanced_report_with_parameters(test_input, expected, report_log, report_assertion):
    """
    Demo test showing parameter display in reports
    
    This test demonstrates:
    - Parameterized test display
    - Multiple test instances
    - Parameter values in report table
    """
    
    report_log(f"Testing with input: {test_input}, expected length: {expected}", "INFO")
    
    actual_length = len(test_input)
    
    report_assertion(
        assertion_type="String Length",
        expected=expected,
        actual=actual_length,
        passed=(actual_length == expected),
        message=f"Length of '{test_input}' should be {expected}"
    )
    
    assert actual_length == expected, f"Expected length {expected}, got {actual_length}"


@pytest.mark.ui_api_db
@pytest.mark.critical
@pytest.mark.slow
def test_comprehensive_enhanced_report(report_log, report_api_call, report_db_query, report_assertion):
    """
    Comprehensive test demonstrating all reporting features together
    
    This test demonstrates:
    - Multiple markers
    - Combined logging (UI + API + DB)
    - Multiple assertions
    - Complete test flow documentation
    """
    
    # Phase 1: Setup
    report_log("=" * 50, "INFO")
    report_log("PHASE 1: Test Setup", "INFO")
    report_log("=" * 50, "INFO")
    report_log("Initializing test environment...", "INFO")
    time.sleep(0.5)
    
    # Phase 2: UI Actions
    report_log("=" * 50, "INFO")
    report_log("PHASE 2: UI Interactions", "INFO")
    report_log("=" * 50, "INFO")
    report_log("Navigating to application...", "INFO")
    report_log("Filling user registration form...", "INFO")
    report_log("Submitting form...", "INFO")
    
    # Phase 3: API Validation
    report_log("=" * 50, "INFO")
    report_log("PHASE 3: API Validation", "INFO")
    report_log("=" * 50, "INFO")
    report_log("Verifying user creation via API...", "INFO")
    
    report_api_call(
        method="POST",
        url="https://api.example.com/users",
        status_code=201,
        response_time=234.7,
        request_data={"name": "Test User", "email": "test@example.com"},
        response_data={"id": 456, "status": "created"}
    )
    
    report_assertion(
        assertion_type="User Creation",
        expected=201,
        actual=201,
        passed=True,
        message="User created successfully via API"
    )
    
    # Phase 4: Database Verification
    report_log("=" * 50, "INFO")
    report_log("PHASE 4: Database Verification", "INFO")
    report_log("=" * 50, "INFO")
    report_log("Checking user record in database...", "INFO")
    
    report_db_query(
        query="SELECT * FROM users WHERE id = 456",
        execution_time=23.4,
        rows_affected=1
    )
    
    report_assertion(
        assertion_type="Database Record",
        expected="User exists",
        actual="User exists",
        passed=True,
        message="User record found in database"
    )
    
    # Phase 5: Cleanup
    report_log("=" * 50, "INFO")
    report_log("PHASE 5: Test Cleanup", "INFO")
    report_log("=" * 50, "INFO")
    report_log("Cleaning up test data...", "INFO")
    
    report_db_query(
        query="DELETE FROM users WHERE id = 456",
        execution_time=15.2,
        rows_affected=1
    )
    
    report_log("Test completed successfully!", "INFO")
    report_log("=" * 50, "INFO")
    
    assert True, "Comprehensive test passed"


@pytest.mark.skip(reason="Example of skipped test in report")
def test_skipped_example():
    """This test is skipped to demonstrate skipped tests in report"""
    assert False


@pytest.mark.xfail(reason="Example of expected failure in report")
def test_expected_failure_example():
    """This test is expected to fail"""
    assert False, "This is an expected failure"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--html=reports/demo_report.html", "--self-contained-html"])
