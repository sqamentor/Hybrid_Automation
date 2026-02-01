"""Unit Tests for Custom Exceptions.

Tests the custom exception classes.
"""

import pytest

from framework.core.exceptions import *


@pytest.mark.modern_spa
@pytest.mark.unit
class TestBaseException:
    """Test base AutomationFrameworkException."""
    
    def test_basic_exception(self):
        """Test basic exception creation."""
        exc = AutomationFrameworkException("Test error")
        assert str(exc) == "Test error"
    
    def test_exception_with_details(self):
        """Test exception with details."""
        exc = AutomationFrameworkException(
            "Test error",
            details={'key': 'value'}
        )
        assert "Test error" in str(exc)
        assert "Details:" in str(exc)
        assert "'key': 'value'" in str(exc)
    
    def test_exception_with_hint(self):
        """Test exception with hint."""
        exc = AutomationFrameworkException(
            "Test error",
            hint="Try this solution"
        )
        assert "Test error" in str(exc)
        assert "Hint: Try this solution" in str(exc)


@pytest.mark.modern_spa
@pytest.mark.unit
class TestEngineExceptions:
    """Test engine-related exceptions."""
    
    def test_engine_startup_exception(self):
        """Test EngineStartupException."""
        exc = EngineStartupException("Playwright", "Driver not found")
        assert "Playwright" in str(exc)
        assert "Driver not found" in str(exc)
        assert "browser installation" in str(exc).lower()
    
    def test_engine_failure_exception(self):
        """Test EngineFailureException."""
        exc = EngineFailureException("Selenium", "click", "Element not clickable")
        assert "Selenium" in str(exc)
        assert "click" in str(exc)
        assert "fallback" in str(exc).lower()
    
    def test_navigation_timeout_exception(self):
        """Test NavigationTimeoutException."""
        exc = NavigationTimeoutException("https://example.com", 30)
        assert "https://example.com" in str(exc)
        assert "30s" in str(exc)
    
    def test_element_not_found_exception(self):
        """Test ElementNotFoundException."""
        exc = ElementNotFoundException("button#submit", timeout=10)
        assert "button#submit" in str(exc)
        assert "10s" in str(exc)


@pytest.mark.modern_spa
@pytest.mark.unit
class TestAPIExceptions:
    """Test API-related exceptions."""
    
    def test_api_request_exception(self):
        """Test APIRequestException."""
        exc = APIRequestException("POST", "/api/users", status_code=500, reason="Server error")
        assert "POST" in str(exc)
        assert "/api/users" in str(exc)
        assert "500" in str(exc)
    
    def test_api_validation_exception(self):
        """Test APIValidationException."""
        exc = APIValidationException(
            "/api/users",
            "status_code",
            expected=200,
            actual=404
        )
        assert "/api/users" in str(exc)
        assert "status_code" in str(exc)
    
    def test_api_timeout_exception(self):
        """Test APITimeoutException."""
        exc = APITimeoutException("/api/users", 30)
        assert "/api/users" in str(exc)
        assert "30" in str(exc)


@pytest.mark.modern_spa
@pytest.mark.unit
class TestDatabaseExceptions:
    """Test database-related exceptions."""
    
    def test_database_connection_exception(self):
        """Test DatabaseConnectionException."""
        exc = DatabaseConnectionException("TestDB", "Authentication failed")
        assert "TestDB" in str(exc)
        assert "Authentication failed" in str(exc)
    
    def test_database_query_exception(self):
        """Test DatabaseQueryException."""
        exc = DatabaseQueryException("SELECT * FROM users", "Table not found")
        assert "SELECT" in str(exc)
        assert "Table not found" in str(exc)
    
    def test_database_validation_exception(self):
        """Test DatabaseValidationException."""
        exc = DatabaseValidationException(
            "row_count",
            expected=10,
            actual=5,
            query="SELECT COUNT(*) FROM orders"
        )
        assert "row_count" in str(exc)
        assert "expected" in str(exc).lower()
    
    def test_readonly_violation_exception(self):
        """Test ReadOnlyViolationException."""
        exc = ReadOnlyViolationException("UPDATE users SET status = 'active'")
        assert "UPDATE" in str(exc)
        assert "read-only" in str(exc).lower()


@pytest.mark.modern_spa
@pytest.mark.unit
class TestConfigurationExceptions:
    """Test configuration-related exceptions."""
    
    def test_missing_configuration_exception(self):
        """Test MissingConfigurationException."""
        exc = MissingConfigurationException("DATABASE_URL")
        assert "DATABASE_URL" in str(exc)
        assert "environments.yaml" in str(exc)
    
    def test_invalid_configuration_exception(self):
        """Test InvalidConfigurationException."""
        exc = InvalidConfigurationException("timeout", -1, "Must be positive")
        assert "timeout" in str(exc)
        assert "-1" in str(exc)
        assert "Must be positive" in str(exc)


@pytest.mark.modern_spa
@pytest.mark.unit
class TestAIExceptions:
    """Test AI-related exceptions."""
    
    def test_ai_service_unavailable_exception(self):
        """Test AIServiceUnavailableException."""
        exc = AIServiceUnavailableException("OpenAI", "API key invalid")
        assert "OpenAI" in str(exc)
        assert "API key invalid" in str(exc)
        assert "OPENAI_API_KEY" in str(exc)
    
    def test_ai_validation_exception(self):
        """Test AIValidationException."""
        exc = AIValidationException("Model timeout")
        assert "Model timeout" in str(exc)
        assert "fall back" in str(exc).lower()


@pytest.mark.modern_spa
@pytest.mark.unit
class TestOtherExceptions:
    """Test other exception types."""
    
    def test_test_data_exception(self):
        """Test TestDataException."""
        exc = TestDataException("user", "Invalid format")
        assert "user" in str(exc)
        assert "Invalid format" in str(exc)
    
    def test_correlation_exception(self):
        """Test CorrelationException."""
        exc = CorrelationException("API", "Database", "order_id")
        assert "API" in str(exc)
        assert "Database" in str(exc)
        assert "order_id" in str(exc)
