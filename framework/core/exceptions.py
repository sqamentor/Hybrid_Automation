"""
Custom Exceptions - Framework-Specific Exception Classes

Provides structured exception handling with actionable error messages.
"""

from typing import Any, Dict, Optional


class AutomationFrameworkException(Exception):
    """Base exception for all framework errors."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        hint: Optional[str] = None,
    ) -> None:
        """Initialize exception.

        Args:
            message: Error message
            details: Additional error details
            hint: Hint for resolution
        """
        self.message = message
        self.details: Dict[str, Any] = details or {}
        self.hint = hint
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format error message with details and hint."""
        msg = self.message
        
        if self.details:
            msg += f"\n\nDetails: {self.details}"
        
        if self.hint:
            msg += f"\n\nHint: {self.hint}"
        
        return msg


# ========================================================================
# ENGINE EXCEPTIONS
# ========================================================================

class EngineException(AutomationFrameworkException):
    """Base exception for UI engine errors."""
    pass


class EngineStartupException(EngineException):
    """Engine failed to start."""
    
    def __init__(self, engine_type: str, reason: str):
        super().__init__(
            message=f"Failed to start {engine_type} engine",
            details={'engine': engine_type, 'reason': reason},
            hint="Check browser installation and driver compatibility"
        )


class EngineFailureException(EngineException):
    """Engine encountered fatal error during execution."""
    
    def __init__(self, engine_type: str, action: str, reason: str):
        super().__init__(
            message=f"{engine_type} engine failed during {action}",
            details={'engine': engine_type, 'action': action, 'reason': reason},
            hint="This may trigger fallback to alternative engine"
        )


class BrowserCrashException(EngineException):
    """Browser process crashed."""
    
    def __init__(self, engine_type: str):
        super().__init__(
            message=f"Browser crashed during execution",
            details={'engine': engine_type},
            hint="Will attempt fallback to Selenium if using Playwright"
        )


class NavigationTimeoutException(EngineException):
    """Page navigation timed out."""
    
    def __init__(self, url: str, timeout: int):
        super().__init__(
            message=f"Navigation to {url} timed out after {timeout}s",
            details={'url': url, 'timeout': timeout},
            hint="Check network connectivity and increase timeout if needed"
        )


class ElementNotFoundException(EngineException):
    """Element not found on page."""
    
    def __init__(self, locator: str, timeout: Optional[int] = None):
        msg = f"Element not found: {locator}"
        if timeout:
            msg += f" (waited {timeout}s)"
        
        super().__init__(
            message=msg,
            details={'locator': locator},
            hint="Check if locator is correct and element is visible"
        )


class ContextCorruptionException(EngineException):
    """Browser context corrupted."""
    
    def __init__(self, engine_type: str):
        super().__init__(
            message="Browser context is corrupted and cannot be recovered",
            details={'engine': engine_type},
            hint="Will attempt to create new session with fallback engine"
        )


# ========================================================================
# API EXCEPTIONS
# ========================================================================

class APIException(AutomationFrameworkException):
    """Base exception for API errors."""
    pass


class APIRequestException(APIException):
    """API request failed."""
    
    def __init__(
        self,
        method: str,
        endpoint: str,
        status_code: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> None:
        super().__init__(
            message=f"API request failed: {method} {endpoint}",
            details={
                'method': method,
                'endpoint': endpoint,
                'status_code': status_code,
                'reason': reason
            },
            hint="Check API endpoint, authentication, and network connectivity"
        )


class APIValidationException(APIException):
    """API response validation failed."""
    
    def __init__(self, endpoint: str, validation_type: str, expected: Any, actual: Any) -> None:
        super().__init__(
            message=f"API validation failed for {endpoint}",
            details={
                'endpoint': endpoint,
                'validation_type': validation_type,
                'expected': expected,
                'actual': actual
            },
            hint="Check API contract and expected response structure"
        )


class APITimeoutException(APIException):
    """API request timed out."""
    
    def __init__(self, endpoint: str, timeout: int):
        super().__init__(
            message=f"API request timed out: {endpoint}",
            details={'endpoint': endpoint, 'timeout': timeout},
            hint="Increase timeout or check API server performance"
        )


# ========================================================================
# DATABASE EXCEPTIONS
# ========================================================================

class DatabaseException(AutomationFrameworkException):
    """Base exception for database errors."""
    pass


class DatabaseConnectionException(DatabaseException):
    """Failed to connect to database."""
    
    def __init__(self, db_name: str, reason: str):
        super().__init__(
            message=f"Failed to connect to database: {db_name}",
            details={'database': db_name, 'reason': reason},
            hint="Check connection string, credentials, and database availability"
        )


class DatabaseQueryException(DatabaseException):
    """Database query execution failed."""
    
    def __init__(self, query: str, reason: str):
        super().__init__(
            message="Database query execution failed",
            details={'query': query, 'reason': reason},
            hint="Check query syntax and database schema"
        )


class DatabaseValidationException(DatabaseException):
    """Database validation assertion failed."""
    
    def __init__(
        self,
        validation_type: str,
        expected: Any,
        actual: Any,
        query: Optional[str] = None,
    ) -> None:
        super().__init__(
            message=f"Database validation failed: {validation_type}",
            details={
                'validation_type': validation_type,
                'expected': expected,
                'actual': actual,
                'query': query
            },
            hint="Check database state and expected values"
        )


class ReadOnlyViolationException(DatabaseException):
    """Attempted write operation on read-only connection."""
    
    def __init__(self, query: str):
        super().__init__(
            message="Attempted write operation on read-only database connection",
            details={'query': query},
            hint="Framework only supports SELECT queries for safety. Check query."
        )


# ========================================================================
# CONFIGURATION EXCEPTIONS
# ========================================================================

class ConfigurationException(AutomationFrameworkException):
    """Base exception for configuration errors."""
    pass


class MissingConfigurationException(ConfigurationException):
    """Required configuration is missing."""
    
    def __init__(self, config_key: str):
        super().__init__(
            message=f"Required configuration missing: {config_key}",
            details={'config_key': config_key},
            hint="Check config/environments.yaml and environment variables"
        )


class InvalidConfigurationException(ConfigurationException):
    """Configuration value is invalid."""
    
    def __init__(self, config_key: str, value: Any, reason: str):
        super().__init__(
            message=f"Invalid configuration: {config_key}",
            details={'config_key': config_key, 'value': value, 'reason': reason},
            hint="Check configuration file format and valid values"
        )


# ========================================================================
# AI EXCEPTIONS
# ========================================================================

class AIException(AutomationFrameworkException):
    """Base exception for AI-related errors."""
    pass


class AIServiceUnavailableException(AIException):
    """AI service is not available."""
    
    def __init__(self, service: str, reason: str):
        super().__init__(
            message=f"AI service unavailable: {service}",
            details={'service': service, 'reason': reason},
            hint="Check OPENAI_API_KEY environment variable and API quota"
        )


class AIValidationException(AIException):
    """AI validation suggestion failed."""
    
    def __init__(self, reason: str):
        super().__init__(
            message="AI validation suggestion failed",
            details={'reason': reason},
            hint="Framework will fall back to rule-based suggestions"
        )


# ========================================================================
# TEST EXCEPTIONS
# ========================================================================

class TestDataException(AutomationFrameworkException):
    """Test data generation or validation failed."""
    
    def __init__(self, data_type: str, reason: str):
        super().__init__(
            message=f"Test data error: {data_type}",
            details={'data_type': data_type, 'reason': reason},
            hint="Check test data configuration and generators"
        )


class CorrelationException(AutomationFrameworkException):
    """Failed to correlate data between layers."""
    
    def __init__(self, layer_from: str, layer_to: str, key: str):
        super().__init__(
            message=f"Failed to correlate {key} from {layer_from} to {layer_to}",
            details={'from': layer_from, 'to': layer_to, 'key': key},
            hint="Check if correlation key is present in API response or database"
        )


__all__ = [
    'AutomationFrameworkException',
    'EngineException',
    'EngineStartupException',
    'EngineFailureException',
    'BrowserCrashException',
    'NavigationTimeoutException',
    'ElementNotFoundException',
    'ContextCorruptionException',
    'APIException',
    'APIRequestException',
    'APIValidationException',
    'APITimeoutException',
    'DatabaseException',
    'DatabaseConnectionException',
    'DatabaseQueryException',
    'DatabaseValidationException',
    'ReadOnlyViolationException',
    'ConfigurationException',
    'MissingConfigurationException',
    'InvalidConfigurationException',
    'AIException',
    'AIServiceUnavailableException',
    'AIValidationException',
    'TestDataException',
    'CorrelationException'
]
