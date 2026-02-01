"""
Simple Enhanced Report Demo Test (No Environment Dependency)
============================================================

Author: Lokendra Singh (qa.lokendra@gmail.com)
Website: www.sqamentor.com
Assisted by: AI Claude

Description:
Simple demo tests to show enhanced reporting without environment dependency.
Demonstrates: logs, assertions, API calls, database queries.
"""

import time

import pytest


@pytest.mark.smoke
def test_simple_with_logs(report_log, report_assertion):
    """Simple test with logs and assertions."""
    
    report_log("Starting simple test", "INFO")
    report_log("This is a debug message", "DEBUG")
    
    # Perform assertion
    expected = 10
    actual = 5 + 5
    
    report_assertion(
        assertion_type="Math Validation",
        expected=expected,
        actual=actual,
        passed=(expected == actual),
        message="5 + 5 should equal 10"
    )
    
    report_log("Test completed successfully", "INFO")
    
    assert expected == actual


@pytest.mark.integration
def test_with_api_calls(report_log, report_api_call):
    """Test showing API call logging."""
    
    report_log("Testing API integration", "INFO")
    
    # Simulate API GET request
    report_api_call(
        method="GET",
        url="https://api.example.com/users",
        status_code=200,
        response_time=125.5
    )
    
    # Simulate API POST request
    report_api_call(
        method="POST",
        url="https://api.example.com/users",
        status_code=201,
        response_time=234.7,
        request_data={"name": "John Doe", "email": "john@example.com"},
        response_data={"id": 123, "status": "created"}
    )
    
    report_log("API calls completed", "INFO")
    
    assert True


@pytest.mark.db_only
def test_with_database(report_log, report_db_query):
    """Test showing database query logging."""
    
    report_log("Testing database operations", "INFO")
    
    # Simulate SELECT query
    report_db_query(
        query="SELECT * FROM users WHERE active = 1",
        execution_time=45.2,
        rows_affected=10
    )
    
    # Simulate UPDATE query
    report_db_query(
        query="UPDATE users SET last_login = NOW() WHERE id = 1",
        execution_time=15.3,
        rows_affected=1
    )
    
    report_log("Database operations completed", "INFO")
    
    assert True


@pytest.mark.parametrize("x,y,expected", [
    (2, 3, 5),
    (10, 5, 15),
    (7, 8, 15),
])
def test_parametrized(x, y, expected, report_log, report_assertion):
    """Test with parameters."""
    
    report_log(f"Testing addition: {x} + {y} = {expected}", "INFO")
    
    actual = x + y
    
    report_assertion(
        assertion_type="Addition",
        expected=expected,
        actual=actual,
        passed=(actual == expected),
        message=f"{x} + {y} should equal {expected}"
    )
    
    assert actual == expected


@pytest.mark.regression
def test_comprehensive(report_log, report_api_call, report_db_query, report_assertion):
    """Comprehensive test with all features."""
    
    report_log("=" * 60, "INFO")
    report_log("COMPREHENSIVE TEST START", "INFO")
    report_log("=" * 60, "INFO")
    
    # Phase 1: API
    report_log("Phase 1: API Testing", "INFO")
    report_api_call(
        method="GET",
        url="https://api.example.com/health",
        status_code=200,
        response_time=50.0
    )
    
    # Phase 2: Database
    report_log("Phase 2: Database Testing", "INFO")
    report_db_query(
        query="SELECT COUNT(*) FROM users",
        execution_time=25.0,
        rows_affected=1
    )
    
    # Phase 3: Validation
    report_log("Phase 3: Validation", "INFO")
    report_assertion(
        assertion_type="System Health",
        expected="Healthy",
        actual="Healthy",
        passed=True,
        message="System is healthy"
    )
    
    report_log("=" * 60, "INFO")
    report_log("COMPREHENSIVE TEST END", "INFO")
    report_log("=" * 60, "INFO")
    
    assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--html=reports/simple_demo_report.html", "--self-contained-html"])
