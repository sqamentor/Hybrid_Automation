"""
Logger - Centralized Logging Configuration with Audit Trail

Provides consistent logging across the framework with:
- Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Separate audit trail for compliance
- Log rotation for disk management
- Structured logging with contextual information
- Action and event tracking
"""

import logging
import sys
import json
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional, Dict, Any


class _SafeAuditJsonFormatter(logging.Formatter):
    """Flat, safe JSON formatter for the audit log.

    When the log message is itself a JSON object (as produced by
    ``log_action``), its fields are merged into the root JSON document so that
    ELK / Grafana / Splunk can index ``action_type``, ``correlation_id``, etc.
    directly without a secondary ``message``-field parse step.

    For plain-text messages the ``message`` key is kept as a string.
    """

    def format(self, record: logging.LogRecord) -> str:
        base = {
            "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
        }

        raw = record.getMessage()
        try:
            payload = json.loads(raw)
            if isinstance(payload, dict):
                # Merge event fields into root — action_type, correlation_id, etc.
                # Fields in ``base`` (timestamp, level, logger) take precedence.
                return json.dumps({**payload, **base}, default=str)
        except (json.JSONDecodeError, TypeError):
            pass

        # Plain-text message: wrap safely with json.dumps to escape special chars.
        base["message"] = raw
        return json.dumps(base, default=str)

# Self-instrumentation for utils.logger module
try:
    from framework.observability.universal_logger import log_function
except ImportError:
    def log_function(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


# Global configuration
LOG_DIR = Path("logs")
AUDIT_DIR = LOG_DIR / "audit"
WARNINGS_DIR = LOG_DIR / "warnings"
LOG_DIR.mkdir(exist_ok=True)
AUDIT_DIR.mkdir(exist_ok=True)
WARNINGS_DIR.mkdir(exist_ok=True)

# Redirect Python warnings.warn() calls into the logging system so they
# are captured to file even when pytest --disable-warnings is not used.
logging.captureWarnings(True)


@log_function(log_timing=True)
def _setup_warnings_file_handler() -> None:
    """
    Route the 'py.warnings' logger (fed by logging.captureWarnings) to a
    dedicated daily-named rotating file under logs/warnings/.

    This ensures every Python warning (DeprecationWarning, ResourceWarning,
    UserWarning, etc.) is persisted to disk even when pytest filterwarnings
    is set to 'ignore'.
    """
    warnings_logger = logging.getLogger('py.warnings')
    if not warnings_logger.handlers:
        warnings_logger.setLevel(logging.WARNING)
        # Use TimedRotatingFileHandler for proper midnight rotation
        wf = WARNINGS_DIR / "warnings.log"
        h = TimedRotatingFileHandler(
            wf, 
            when='midnight',
            interval=1,
            backupCount=30,  # Keep 30 days of warnings
            encoding='utf-8'
        )
        h.suffix = "%Y%m%d"  # Add date suffix to rotated files
        h.setLevel(logging.WARNING)
        h.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)8s] py.warnings - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        warnings_logger.addHandler(h)
        warnings_logger.propagate = False  # prevent double-logging to root


_setup_warnings_file_handler()


class TestAuditLogger:
    """
    Specialized logger for audit trail in test automation
    Captures all test actions, API calls, DB operations, and framework events
    
    Note: Renamed from AuditLogger to avoid confusion with
    framework.observability.enterprise_logger.AuditLogger which is for
    SOC2/ISO27001 compliance logging.
    """
    
    @log_function()
    def __init__(self):
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
        
        # Only configure once
        if not self.logger.handlers:
            # Daily rotating audit log
            audit_file = AUDIT_DIR / "audit.log"
            audit_handler = TimedRotatingFileHandler(
                audit_file,
                when='midnight',
                interval=1,
                backupCount=90,  # Keep 90 days of audit logs
                encoding='utf-8'
            )
            audit_handler.suffix = "%Y%m%d"  # Add date suffix to rotated files
            audit_handler.setLevel(logging.INFO)
            
            # JSON format for easy parsing and compliance tools
            # Use safe JSON formatter to prevent malformed JSON from message content
            audit_format = _SafeAuditJsonFormatter(datefmt='%Y-%m-%d %H:%M:%S')
            audit_handler.setFormatter(audit_format)
            self.logger.addHandler(audit_handler)
    
    @log_function(log_args=True)
    def log_action(self, action_type: str, details: Dict[str, Any], status: str = "success"):
        """
        Log test action with structured data.

        Automatically enriches each entry with correlation_id, trace_id, and
        request_id from the enterprise CorrelationContext (set per-test by the
        pytest_enterprise_logging plugin) so every audit entry is traceable
        across the ELK / SIEM pipeline.

        Args:
            action_type: Type of action (ui_click, api_call, db_query, etc.)
            details: Action details as dictionary
            status: Action status (success, failure, warning)
        """
        # Lazily resolve distributed-trace context variables — avoids circular
        # import at module load time while still carrying IDs in every entry.
        correlation_id: Optional[str] = None
        trace_id: Optional[str] = None
        request_id: Optional[str] = None
        try:
            from framework.observability.enterprise_logger import CorrelationContext
            correlation_id = CorrelationContext.get_correlation_id()
            trace_id = CorrelationContext.get_trace_id()
            request_id = CorrelationContext.get_request_id()
        except Exception:
            # Enterprise logger not available — IDs remain None.
            # This is expected before the enterprise plugin initialises; no
            # logging here to avoid recursion or noisy startup stderr output.
            pass

        event = {
            "action_type": action_type,
            "status": status,
            "details": details,
            "timestamp_ms": datetime.now().timestamp() * 1000,
            "correlation_id": correlation_id,
            "trace_id": trace_id,
            "request_id": request_id,
        }
        self.logger.info(json.dumps(event))
    
    @log_function(log_args=True)
    def log_test_start(self, test_name: str, test_file: str):
        """Log test execution start"""
        self.log_action("test_start", {
            "test_name": test_name,
            "test_file": test_file
        })
    
    @log_function(log_args=True)
    def log_test_end(self, test_name: str, status: str, duration: float):
        """Log test execution end"""
        self.log_action("test_end", {
            "test_name": test_name,
            "duration_seconds": duration,
            "result": status
        }, status=status)
    
    @log_function(log_args=True)
    def log_ui_action(self, action: str, element: str, value: Optional[str] = None):
        """Log UI interaction"""
        details = {"action": action, "element": element}
        if value:
            details["value"] = value
        self.log_action("ui_action", details)
    
    @log_function(log_args=True)
    def log_api_call(self, method: str, url: str, status_code: int, 
                     duration_ms: float, request_body: Optional[Dict] = None,
                     response_body: Optional[Dict] = None):
        """Log API call with request/response"""
        details = {
            "method": method,
            "url": url,
            "status_code": status_code,
            "duration_ms": duration_ms
        }
        if request_body:
            details["request"] = request_body
        if response_body:
            details["response"] = response_body
        
        status = "success" if 200 <= status_code < 300 else "failure"
        self.log_action("api_call", details, status=status)
    
    @log_function(log_args=True)
    def log_db_operation(self, operation: str, table: str, query: str, 
                        rows_affected: int = 0, duration_ms: float = 0):
        """Log database operation"""
        self.log_action("db_operation", {
            "operation": operation,
            "table": table,
            "query": query,
            "rows_affected": rows_affected,
            "duration_ms": duration_ms
        })
    
    @log_function(log_args=True)
    def log_error(self, error_type: str, error_message: str, stack_trace: Optional[str] = None):
        """Log error with details"""
        details = {
            "error_type": error_type,
            "error_message": error_message
        }
        if stack_trace:
            details["stack_trace"] = stack_trace
        self.log_action("error", details, status="failure")

    @log_function(log_args=True)
    def log_warning(self, warning_category: str, warning_message: str,
                    source_file: Optional[str] = None, source_line: Optional[int] = None):
        """
        Log a Python/pytest warning to the audit trail.

        Called from the pytest_warning_recorded hook so every warning is
        persisted as a structured JSON entry in the audit log regardless of
        whether the terminal summary is suppressed.

        Args:
            warning_category: Warning class name (e.g. 'DeprecationWarning')
            warning_message: The warning message text
            source_file: Source file where the warning originated
            source_line: Line number in source file
        """
        details: Dict[str, Any] = {
            "warning_category": warning_category,
            "warning_message": warning_message,
        }
        if source_file:
            details["source_file"] = source_file
        if source_line is not None:
            details["source_line"] = source_line
        self.log_action("warning", details, status="warning")

    @log_function(log_args=True)
    def log_step(self, step_description: str, step_number: Optional[int] = None,
                 test_name: Optional[str] = None):
        """
        Log an individual named test step.

        Provides granular step-by-step audit trail within a single test so
        it is possible to see exactly which step failed in a multi-step flow.

        Args:
            step_description: Human-readable description of the step
            step_number: Optional sequential step number
            test_name: Test node id for correlation
        """
        details: Dict[str, Any] = {"step_description": step_description}
        if step_number is not None:
            details["step_number"] = step_number
        if test_name:
            details["test_name"] = test_name
        self.log_action("test_step", details, status="success")

    @log_function(log_args=True)
    def log_fixture_event(self, fixture_name: str, event: str,
                          scope: str = "function", test_name: Optional[str] = None):
        """
        Log fixture setup and teardown lifecycle events.

        Args:
            fixture_name: Name of the fixture (e.g. 'bookslot_page')
            event: 'setup' or 'teardown'
            scope: Fixture scope ('function', 'session', 'module', 'class')
            test_name: Test node id this fixture serves
        """
        details: Dict[str, Any] = {
            "fixture_name": fixture_name,
            "event": event,
            "scope": scope,
        }
        if test_name:
            details["test_name"] = test_name
        self.log_action("fixture_event", details, status="success")

    @log_function(log_args=True)
    def log_page_load(self, page_name: str, url: str, load_time_ms: float = 0):
        """
        Log page load/navigation event.
        
        Args:
            page_name: Name/identifier of the page
            url: Full URL that was loaded
            load_time_ms: Page load time in milliseconds
        """
        self.log_action("page_load", {
            "page_name": page_name,
            "url": url,
            "load_time_ms": load_time_ms
        }, status="success")

    @log_function(log_args=True)
    def log_element_interaction(self, action: str, element: str, page: str = "",
                                value: Optional[str] = None, success: bool = True):
        """
        Log element interaction with detailed context.
        
        Args:
            action: Interaction type (click, fill, select, hover, etc.)
            element: Element identifier/description
            page: Page where interaction occurred
            value: Value entered/selected (if applicable)
            success: Whether interaction succeeded
        """
        details: Dict[str, Any] = {
            "action": action,
            "element": element
        }
        if page:
            details["page"] = page
        if value is not None:
            details["value"] = str(value)[:200]  # Limit value length
        
        self.log_action("element_interaction", details,
                       status="success" if success else "failure")

    @log_function(log_args=True)
    def log_validation(self, validation_type: str, expected: Any, actual: Any,
                      passed: bool, message: str = ""):
        """
        Log validation/assertion result.
        
        Args:
            validation_type: Type of validation (equality, visibility, text_match, etc.)
            expected: Expected value
            actual: Actual value
            passed: Whether validation passed
            message: Additional context message
        """
        details: Dict[str, Any] = {
            "validation_type": validation_type,
            "expected": str(expected)[:200],
            "actual": str(actual)[:200],
            "passed": passed
        }
        if message:
            details["message"] = message
        
        self.log_action("validation", details,
                       status="success" if passed else "failure")

    @log_function(log_args=True)
    def log_wait_event(self, wait_type: str, condition: str, timeout_ms: int,
                      success: bool, elapsed_ms: float = 0):
        """
        Log explicit wait events.
        
        Args:
            wait_type: Type of wait (element_visible, element_clickable, url_change, etc.)
            condition: Condition being waited for
            timeout_ms: Timeout in milliseconds
            success: Whether wait succeeded
            elapsed_ms: Actual time elapsed in milliseconds
        """
        self.log_action("wait_event", {
            "wait_type": wait_type,
            "condition": condition,
            "timeout_ms": timeout_ms,
            "elapsed_ms": elapsed_ms,
            "success": success
        }, status="success" if success else "failure")

    @log_function(log_args=True)
    def log_screenshot(self, screenshot_path: str, reason: str = "capture",
                      test_name: Optional[str] = None):
        """
        Log screenshot capture event.
        
        Args:
            screenshot_path: Path where screenshot was saved
            reason: Reason for screenshot (failure, success, checkpoint, etc.)
            test_name: Test that triggered screenshot
        """
        details: Dict[str, Any] = {
            "screenshot_path": screenshot_path,
            "reason": reason
        }
        if test_name:
            details["test_name"] = test_name
        
        self.log_action("screenshot", details, status="success")

    @log_function(log_args=True)
    def log_config_change(self, config_name: str, old_value: Any, new_value: Any,
                         source: str = "runtime"):
        """
        Log configuration changes.
        
        Args:
            config_name: Name of configuration parameter
            old_value: Previous value
            new_value: New value
            source: Source of change (runtime, environment, user, etc.)
        """
        self.log_action("config_change", {
            "config_name": config_name,
            "old_value": str(old_value),
            "new_value": str(new_value),
            "source": source
        }, status="success")

    @log_function(log_args=True)
    def log_network_request(self, url: str, method: str, status_code: int,
                           duration_ms: float, request_type: str = "XHR"):
        """
        Log network requests captured during test execution.
        
        Args:
            url: Request URL
            method: HTTP method
            status_code: Response status code
            duration_ms: Request duration
            request_type: Type (XHR, Fetch, Document, etc.)
        """
        self.log_action("network_request", {
            "url": url,
            "method": method,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "request_type": request_type
        }, status="success" if 200 <= status_code < 400 else "failure")


# Singleton audit logger instance
_audit_logger = None

@log_function(log_result=True)
def get_audit_logger() -> TestAuditLogger:
    """Get the global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = TestAuditLogger()
    return _audit_logger


@log_function(log_args=True, log_result=True)
def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger instance
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance with console and rotating file handlers
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Console handler - INFO level for clean output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # Daily rotating file handler for application logs
        log_file = LOG_DIR / "framework.log"
        file_handler = TimedRotatingFileHandler(
            log_file,
            when='midnight',
            interval=1,
            backupCount=30,  # Keep 30 days
            encoding='utf-8'
        )
        file_handler.suffix = "%Y%m%d"  # Add date suffix to rotated files
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
        # Error file handler - Separate daily file for errors only
        error_log_file = LOG_DIR / "errors.log"
        error_handler = TimedRotatingFileHandler(
            error_log_file,
            when='midnight',
            interval=1,
            backupCount=30,  # Keep 30 days
            encoding='utf-8'
        )
        error_handler.suffix = "%Y%m%d"  # Add date suffix to rotated files
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        logger.addHandler(error_handler)
    
    return logger


# Backward compatibility alias
AuditLogger = TestAuditLogger


__all__ = ['get_logger', 'get_audit_logger', 'TestAuditLogger', 'AuditLogger']  # AuditLogger kept for backward compatibility
