"""
Structured logging with structlog for better observability.

Provides:
- JSON-formatted logs
- Context variables
- Correlation IDs
- Log aggregation support (ELK, Splunk, etc.)
"""
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import structlog


class LogConfig:
    """Configuration for structured logging."""
    
    def __init__(
        self,
        level: str = "INFO",
        format: str = "json",  # json or console
        log_file: Optional[str] = None,
        include_timestamp: bool = True,
        include_caller: bool = True,
        include_thread: bool = False
    ):
        """
        Initialize logging configuration.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format: Output format (json or console)
            log_file: Optional log file path
            include_timestamp: Include timestamp in logs
            include_caller: Include caller information
            include_thread: Include thread information
        """
        self.level = level
        self.format = format
        self.log_file = log_file
        self.include_timestamp = include_timestamp
        self.include_caller = include_caller
        self.include_thread = include_thread


def configure_logging(config: LogConfig) -> None:
    """
    Configure structlog with the specified configuration.
    
    Args:
        config: Logging configuration
    
    Example:
        ```python
        from framework.observability.logging import configure_logging, LogConfig
        
        config = LogConfig(
            level="DEBUG",
            format="json",
            log_file="logs/test.log"
        )
        configure_logging(config)
        ```
    """
    # Convert string level to logging constant
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    log_level = level_map.get(config.level.upper(), logging.INFO)
    
    # Setup processors
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
    ]
    
    if config.include_timestamp:
        processors.append(structlog.processors.TimeStamper(fmt="iso"))
    
    if config.include_caller:
        processors.append(structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ))
    
    if config.include_thread:
        processors.append(structlog.processors.add_thread_info)
    
    # Add stack info for exceptions
    processors.append(structlog.processors.StackInfoRenderer())
    processors.append(structlog.processors.format_exc_info)
    
    # Choose output format
    if config.format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        stream=sys.stdout
    )
    
    # Add file handler if specified
    if config.log_file:
        log_path = Path(config.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(config.log_file)
        file_handler.setLevel(log_level)
        logging.root.addHandler(file_handler)


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Optional logger name (defaults to module name)
    
    Returns:
        Configured structlog logger
    
    Example:
        ```python
        from framework.observability.logging import get_logger
        
        logger = get_logger(__name__)
        logger.info("test_started", test_name="test_login", user="admin")
        logger.error("test_failed", test_name="test_login", error="timeout")
        ```
    """
    return structlog.get_logger(name)


class LogContext:
    """
    Context manager for adding context to logs.
    
    Example:
        ```python
        from framework.observability.logging import LogContext, get_logger
        
        logger = get_logger(__name__)
        
        with LogContext(test_id="test_001", user="admin"):
            logger.info("operation_started")
            # All logs in this context will include test_id and user
            logger.info("operation_completed")
        ```
    """
    
    def __init__(self, **context):
        """
        Initialize log context.
        
        Args:
            **context: Context key-value pairs
        """
        self.context = context
        self.token = None
    
    def __enter__(self):
        """Enter context."""
        self.token = structlog.contextvars.bind_contextvars(**self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        structlog.contextvars.unbind_contextvars(*self.context.keys())


class TestLogger:
    """
    Specialized logger for test execution.
    
    Example:
        ```python
        from framework.observability.logging import TestLogger
        
        test_logger = TestLogger("test_login")
        test_logger.test_started()
        test_logger.step("enter_username", username="admin")
        test_logger.test_passed(duration=1.23)
        ```
    """
    
    def __init__(self, test_name: str):
        """
        Initialize test logger.
        
        Args:
            test_name: Name of the test
        """
        self.test_name = test_name
        self.logger = get_logger("test")
        self.context = LogContext(test_name=test_name)
    
    def __enter__(self):
        """Enter test context."""
        self.context.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit test context."""
        self.context.__exit__(exc_type, exc_val, exc_tb)
    
    def test_started(self, **kwargs) -> None:
        """
        Log test start.
        
        Args:
            **kwargs: Additional context
        """
        self.logger.info("test_started", **kwargs)
    
    def test_passed(self, duration: Optional[float] = None, **kwargs) -> None:
        """
        Log test pass.
        
        Args:
            duration: Test duration in seconds
            **kwargs: Additional context
        """
        if duration is not None:
            kwargs["duration"] = duration
        self.logger.info("test_passed", **kwargs)
    
    def test_failed(self, error: str, **kwargs) -> None:
        """
        Log test failure.
        
        Args:
            error: Error message
            **kwargs: Additional context
        """
        self.logger.error("test_failed", error=error, **kwargs)
    
    def test_skipped(self, reason: str, **kwargs) -> None:
        """
        Log test skip.
        
        Args:
            reason: Skip reason
            **kwargs: Additional context
        """
        self.logger.warning("test_skipped", reason=reason, **kwargs)
    
    def step(self, step_name: str, **kwargs) -> None:
        """
        Log test step.
        
        Args:
            step_name: Name of the step
            **kwargs: Additional context
        """
        self.logger.info("test_step", step=step_name, **kwargs)
    
    def assertion(self, assertion: str, result: bool, **kwargs) -> None:
        """
        Log assertion result.
        
        Args:
            assertion: Assertion description
            result: Assertion result (True/False)
            **kwargs: Additional context
        """
        level = "info" if result else "error"
        getattr(self.logger, level)(
            "assertion",
            assertion=assertion,
            result=result,
            **kwargs
        )
    
    def screenshot(self, path: str, **kwargs) -> None:
        """
        Log screenshot capture.
        
        Args:
            path: Screenshot file path
            **kwargs: Additional context
        """
        self.logger.info("screenshot_captured", screenshot_path=path, **kwargs)
    
    def api_request(
        self,
        method: str,
        url: str,
        status_code: Optional[int] = None,
        duration: Optional[float] = None,
        **kwargs
    ) -> None:
        """
        Log API request.
        
        Args:
            method: HTTP method
            url: Request URL
            status_code: Response status code
            duration: Request duration in seconds
            **kwargs: Additional context
        """
        self.logger.info(
            "api_request",
            method=method,
            url=url,
            status_code=status_code,
            duration=duration,
            **kwargs
        )
    
    def database_query(
        self,
        query: str,
        rows_affected: Optional[int] = None,
        duration: Optional[float] = None,
        **kwargs
    ) -> None:
        """
        Log database query.
        
        Args:
            query: SQL query
            rows_affected: Number of rows affected
            duration: Query duration in seconds
            **kwargs: Additional context
        """
        self.logger.info(
            "database_query",
            query=query[:100],  # Truncate long queries
            rows_affected=rows_affected,
            duration=duration,
            **kwargs
        )


class PerformanceLogger:
    """
    Logger for performance metrics.
    
    Example:
        ```python
        from framework.observability.logging import PerformanceLogger
        
        perf_logger = PerformanceLogger()
        
        with perf_logger.measure("page_load"):
            # Code to measure
            page.load()
        ```
    """
    
    def __init__(self):
        """Initialize performance logger."""
        self.logger = get_logger("performance")
    
    def measure(self, operation: str, **context):
        """
        Context manager for measuring operation duration.
        
        Args:
            operation: Name of the operation
            **context: Additional context
        
        Returns:
            Performance measurement context
        """
        return PerformanceMeasurement(self.logger, operation, context)


class PerformanceMeasurement:
    """Context manager for performance measurements."""
    
    def __init__(self, logger, operation: str, context: Dict[str, Any]):
        """
        Initialize performance measurement.
        
        Args:
            logger: Logger instance
            operation: Operation name
            context: Additional context
        """
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        """Start measurement."""
        import time
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End measurement and log."""
        import time
        duration = time.time() - self.start_time
        
        self.logger.info(
            "performance_metric",
            operation=self.operation,
            duration=duration,
            **self.context
        )


# ============================================================================
# Convenience Functions
# ============================================================================

def log_test_execution(test_name: str):
    """
    Decorator for logging test execution.
    
    Args:
        test_name: Name of the test
    
    Returns:
        Decorated test function
    
    Example:
        ```python
        @log_test_execution("test_user_login")
        def test_user_login():
            # Test code
            pass
        ```
    """
    import time
    from functools import wraps
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            test_logger = TestLogger(test_name)
            
            with test_logger:
                test_logger.test_started()
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    test_logger.test_passed(duration=duration)
                    return result
                except Exception as e:
                    test_logger.test_failed(error=str(e))
                    raise
        
        return wrapper
    
    return decorator


def log_async_test_execution(test_name: str):
    """
    Decorator for logging async test execution.
    
    Args:
        test_name: Name of the test
    
    Returns:
        Decorated async test function
    
    Example:
        ```python
        @log_async_test_execution("test_async_api_call")
        async def test_async_api_call():
            # Async test code
            pass
        ```
    """
    import time
    from functools import wraps
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            test_logger = TestLogger(test_name)
            
            with test_logger:
                test_logger.test_started()
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    test_logger.test_passed(duration=duration)
                    return result
                except Exception as e:
                    test_logger.test_failed(error=str(e))
                    raise
        
        return wrapper
    
    return decorator


# ============================================================================
# Initialize Default Logging
# ============================================================================

# Configure default logging (can be overridden by calling configure_logging)
default_config = LogConfig(
    level="INFO",
    format="console",
    include_timestamp=True,
    include_caller=False
)

configure_logging(default_config)
