"""
Pytest Integration for Enterprise Logging
==========================================

Integrates enterprise-grade logging with pytest test execution:
- Automatic correlation ID generation per test
- Request lifecycle tracking
- Test phase logging (setup/call/teardown)
- Exception tracking with full context
- Performance metrics per test
- Security event logging
- Audit trail generation
"""

import pytest
import time
from pathlib import Path
from typing import Any, Dict

try:
    from framework.observability.enterprise_logger import (
        get_enterprise_logger,
        CorrelationContext,
        with_correlation
    )
    ENTERPRISE_LOGGING_AVAILABLE = True
except ImportError:
    ENTERPRISE_LOGGING_AVAILABLE = False

# Self-instrumentation for pytest plugin
try:
    from framework.observability.universal_logger import log_function
except ImportError:
    def log_function(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


if ENTERPRISE_LOGGING_AVAILABLE:
    enterprise_logger = get_enterprise_logger()


@log_function(log_args=True)
def pytest_configure(config):
    """Initialize enterprise logging at session start"""
    if not ENTERPRISE_LOGGING_AVAILABLE:
        return
    
    enterprise_logger.info(
        "🚀 Pytest session configured with enterprise logging",
        pytest_version=pytest.__version__,
        workers=config.getoption('numprocesses', default=1),
        verbosity=config.option.verbose
    )
    
    # Log configuration
    enterprise_logger.audit(
        "pytest_session_config",
        {
            "rootdir": str(config.rootdir),
            "inifile": str(config.inifile) if config.inifile else None,
            "args": config.args,
            "known_args": {k: getattr(config.option, k) for k in dir(config.option) if not k.startswith('_')}
        }
    )


@log_function(log_args=True)
def pytest_sessionstart(session):
    """Hook called at test session start"""
    if not ENTERPRISE_LOGGING_AVAILABLE:
        return
    
    # Generate session-level trace ID
    session_trace_id = CorrelationContext.generate_trace_id()
    CorrelationContext.set_trace_id(session_trace_id)
    
    enterprise_logger.info(
        "=" * 80 + "\n" +
        "📊 TEST SESSION STARTED\n" +
        "=" * 80,
        session_trace_id=session_trace_id,
        total_items=len(session.items) if hasattr(session, 'items') else 0
    )
    
    enterprise_logger.audit(
        "session_start",
        {
            "session_trace_id": session_trace_id,
            "total_tests": len(session.items) if hasattr(session, 'items') else 0
        }
    )


@log_function(log_args=True)
def pytest_sessionfinish(session, exitstatus):
    """Hook called at test session end"""
    if not ENTERPRISE_LOGGING_AVAILABLE:
        return
    
    # Calculate session metrics
    duration = time.time() - session.starttime if hasattr(session, 'starttime') else 0
    
    enterprise_logger.info(
        "=" * 80 + "\n" +
        f"✓ TEST SESSION FINISHED (exit status: {exitstatus})\n" +
        "=" * 80,
        exit_status=exitstatus,
        duration_seconds=duration
    )
    
    enterprise_logger.audit(
        "session_end",
        {
            "exit_status": exitstatus,
            "duration_seconds": duration,
            "session_trace_id": CorrelationContext.get_trace_id()
        }
    )
    
    # Flush all logs before exit
    enterprise_logger.shutdown()
    
    # Clear correlation context after everything is complete
    # This ensures fixture teardown (video rename, audit close) has access to
    # correlation_id throughout their execution
    CorrelationContext.clear_context()


@log_function(log_args=True)
def pytest_runtest_setup(item):
    """Hook called before each test setup"""
    if not ENTERPRISE_LOGGING_AVAILABLE:
        return
    
    # Generate unique correlation ID for this test
    corr_id = CorrelationContext.generate_correlation_id()
    req_id = CorrelationContext.generate_request_id()
    
    CorrelationContext.set_correlation_id(corr_id)
    CorrelationContext.set_request_id(req_id)
    
    # Store start time
    item.test_start_time = time.time()
    
    enterprise_logger.info(
        f"→ Setting up test: {item.nodeid}",
        test_id=item.nodeid,
        test_name=item.name,
        test_file=item.fspath.basename if hasattr(item, 'fspath') else None,
        markers=[m.name for m in item.iter_markers()],
        correlation_id=corr_id,
        request_id=req_id
    )
    
    enterprise_logger.audit(
        "test_setup_start",
        {
            "test_id": item.nodeid,
            "test_name": item.name,
            "markers": [m.name for m in item.iter_markers()],
            "fixtures": list(item.fixturenames) if hasattr(item, 'fixturenames') else []
        }
    )


@log_function(log_args=True)
def pytest_runtest_teardown(item, nextitem):
    """Hook called after each test teardown"""
    if not ENTERPRISE_LOGGING_AVAILABLE:
        return
    
    enterprise_logger.info(
        f"← Tearing down test: {item.nodeid}",
        test_id=item.nodeid
    )
    
    enterprise_logger.audit(
        "test_teardown",
        {
            "test_id": item.nodeid,
            "next_test": nextitem.nodeid if nextitem else None
        }
    )
    
    # Note: CorrelationContext.clear_context() moved to pytest_sessionfinish
    # to ensure fixture teardown (video rename, audit close) can still access
    # the correlation_id before it's cleared


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results and log them"""
    # Note: @log_function decorator removed as it conflicts with hookwrapper=True
    # which requires the function to be a generator
    outcome = yield
    report = outcome.get_result()
    
    if not ENTERPRISE_LOGGING_AVAILABLE:
        return
    
    # Only log the test execution phase (not setup/teardown)
    if report.when == "call":
        # Calculate test duration
        duration = report.duration if hasattr(report, 'duration') else 0
        duration_ms = duration * 1000
        
        # Log based on result
        if report.passed:
            enterprise_logger.info(
                f"✓ TEST PASSED: {item.nodeid}",
                test_id=item.nodeid,
                test_name=item.name,
                duration_seconds=duration,
                duration_ms=duration_ms,
                status="PASSED"
            )
            
            enterprise_logger.audit(
                "test_completed",
                {
                    "test_id": item.nodeid,
                    "test_name": item.name,
                    "status": "PASSED",
                    "duration_ms": duration_ms
                },
                status="success"
            )
            
            # Log performance
            enterprise_logger.performance(
                f"test_{item.name}",
                duration_ms,
                {"test_id": item.nodeid, "status": "passed"}
            )
        
        elif report.failed:
            # Extract exception info
            exc_type = None
            exc_message = None
            exc_traceback = None
            
            if call.excinfo:
                exc_type = call.excinfo.typename
                exc_message = str(call.excinfo.value)
                exc_traceback = str(call.excinfo.traceback)
            
            enterprise_logger.error(
                f"✗ TEST FAILED: {item.nodeid}",
                exc_info=True,
                test_id=item.nodeid,
                test_name=item.name,
                duration_seconds=duration,
                duration_ms=duration_ms,
                status="FAILED",
                exception_type=exc_type,
                exception_message=exc_message
            )
            
            enterprise_logger.audit(
                "test_completed",
                {
                    "test_id": item.nodeid,
                    "test_name": item.name,
                    "status": "FAILED",
                    "duration_ms": duration_ms,
                    "exception": {
                        "type": exc_type,
                        "message": exc_message,
                        "traceback": exc_traceback[:1000] if exc_traceback else None  # First 1000 chars
                    }
                },
                status="failure"
            )
            
            # Log as security event if auth/permission related
            if exc_type and any(keyword in exc_type.lower() for keyword in ['permission', 'auth', 'access', 'forbidden']):
                enterprise_logger.security(
                    "test_security_failure",
                    {
                        "test_id": item.nodeid,
                        "exception_type": exc_type,
                        "message": exc_message
                    },
                    severity="warning"
                )
        
        elif report.skipped:
            skip_reason = report.longrepr[2] if hasattr(report, 'longrepr') and len(report.longrepr) > 2 else "Unknown"
            
            enterprise_logger.warning(
                f"⊘ TEST SKIPPED: {item.nodeid}",
                test_id=item.nodeid,
                test_name=item.name,
                reason=skip_reason,
                status="SKIPPED"
            )
            
            enterprise_logger.audit(
                "test_skipped",
                {
                    "test_id": item.nodeid,
                    "test_name": item.name,
                    "reason": str(skip_reason)
                }
            )


@log_function(log_args=True)
def pytest_exception_interact(node, call, report):
    """Hook called when exception occurs during test"""
    if not ENTERPRISE_LOGGING_AVAILABLE:
        return
    
    if call.excinfo:
        enterprise_logger.critical(
            f"🔥 EXCEPTION DURING TEST: {node.nodeid}",
            exc_info=True,
            test_id=node.nodeid,
            phase=report.when,
            exception_type=call.excinfo.typename,
            exception_value=str(call.excinfo.value)
        )


@log_function(log_args=True)
def pytest_warning_recorded(warning_message, when, nodeid, location):
    """Hook called when warning is captured - ensures NO warnings are missed"""
    if not ENTERPRISE_LOGGING_AVAILABLE:
        return
    
    # Extract warning details
    category = warning_message.category.__name__ if hasattr(warning_message, 'category') else "Unknown"
    message = str(warning_message.message) if hasattr(warning_message, 'message') else str(warning_message)
    
    filename = location[0] if location else None
    lineno = location[1] if location and len(location) > 1 else None
    
    enterprise_logger.warning(
        f"⚠ {category}: {message}",
        warning_category=category,
        warning_message=message,
        source_file=filename,
        source_line=lineno,
        when=when,
        test_id=nodeid
    )
    
    enterprise_logger.audit(
        "warning_captured",
        {
            "category": category,
            "message": message,
            "source_file": filename,
            "source_line": lineno,
            "when": when,
            "test_id": nodeid
        },
        status="warning"
    )


@log_function(log_args=True)
@pytest.fixture(scope="function")
def enterprise_logging_context(request):
    """
    Fixture to provide enterprise logging context for tests
    
    Usage:
        def test_something(enterprise_logging_context):
            enterprise_logging_context.set_user({"user_id": "test_user"})
            enterprise_logging_context.log_action("user_login", {"method": "oauth"})
    """
    if not ENTERPRISE_LOGGING_AVAILABLE:
        yield None
        return
    
    class LoggingContext:
        @log_function(log_args=True)
        def __init__(self, test_name: str):
            self.test_name = test_name
            self.logger = get_enterprise_logger()
        
        @log_function(log_args=True)
        def set_user(self, user_data: Dict):
            """Set user context for this test"""
            CorrelationContext.set_user_context(user_data)
            self.logger.security(
                "user_context_set",
                {
                    "test": self.test_name,
                    "user": user_data
                }
            )
        
        @log_function(log_args=True)
        def log_action(self, action: str, details: Dict):
            """Log custom action"""
            self.logger.audit(action, details)
        
        @log_function(log_args=True)
        def log_security_event(self, event: str, details: Dict, severity: str = "info"):
            """Log security event"""
            self.logger.security(event, details, severity)
        
        @log_function(log_args=True)
        def log_performance(self, operation: str, duration_ms: float, details: Dict = None):
            """Log performance metric"""
            self.logger.performance(operation, duration_ms, details)
    
    context = LoggingContext(request.node.nodeid)
    yield context


__all__ = [
    'pytest_configure',
    'pytest_sessionstart',
    'pytest_sessionfinish',
    'pytest_runtest_setup',
    'pytest_runtest_teardown',
    'pytest_runtest_makereport',
    'pytest_exception_interact',
    'pytest_warning_recorded',
    'enterprise_logging_context'
]
