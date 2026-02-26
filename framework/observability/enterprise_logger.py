"""
Enterprise-Grade Structured Logging System
==========================================

Production-ready logging with:
- Structured JSON logging
- Distributed tracing with correlation IDs
- Request lifecycle tracking
- PII/sensitive data masking
- Async logging support
- SIEM compatibility (ELK, Datadog, Splunk)
- SOC2/ISO27001 compliance ready
- Performance optimized

Author: Lokendra Singh
Email: lokendra.singh@centerforvein.com
Website: www.centerforvein.com
"""

import asyncio
import atexit
import json
import logging
import os
import re
import socket
import sys
import threading
import time
import traceback
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from functools import wraps
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener
from pathlib import Path
from queue import Queue
from typing import Any, Dict, List, Optional, Callable, Union

# Context variables for distributed tracing
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
user_context_var: ContextVar[Optional[Dict]] = ContextVar('user_context', default=None)

# Global configuration
LOG_DIR = Path("logs")
ENTERPRISE_LOG_DIR = LOG_DIR / "enterprise"
AUDIT_LOG_DIR = LOG_DIR / "audit"
SECURITY_LOG_DIR = LOG_DIR / "security"
PERFORMANCE_LOG_DIR = LOG_DIR / "performance"

# Ensure directories exist
for directory in [ENTERPRISE_LOG_DIR, AUDIT_LOG_DIR, SECURITY_LOG_DIR, PERFORMANCE_LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


class SensitiveDataMasker:
    """Masks sensitive data in logs for security compliance"""
    
    SENSITIVE_KEYS = {
        'password', 'passwd', 'pwd', 'secret', 'api_key', 'apikey', 
        'token', 'access_token', 'refresh_token', 'authorization',
        'credit_card', 'card_number', 'cvv', 'ssn', 'social_security',
        'private_key', 'encryption_key', 'auth', 'credential'
    }
    
    SENSITIVE_PATTERNS = [
        # Email patterns - GDPR/HIPAA compliant: mask username and most of domain
        # Example: john.doe@company.com -> j***@c*****.com
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
         lambda m: f"{m.group(0)[0]}***@{m.group(0).split('@')[1][0]}*****{m.group(0).split('@')[1].split('.')[-1]}"),
        # Credit card patterns
        (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '****-****-****-****'),
        # SSN patterns
        (r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****'),
        # Phone patterns (10+ digits)
        (r'\b\d{10,}\b', '**********'),
    ]
    
    @classmethod
    def mask_dict(cls, data: Dict[str, Any], mask_value: str = "***MASKED***") -> Dict[str, Any]:
        """Recursively mask sensitive data in dictionaries"""
        if not isinstance(data, dict):
            return data
        
        masked = {}
        for key, value in data.items():
            # Convert key to string for comparison
            key_str = str(key)
            key_lower = key_str.lower()
            
            # Check if key is exactly a sensitive key (not just contains it)
            # This prevents "credentials" from matching "credential"
            is_sensitive = key_lower in cls.SENSITIVE_KEYS
            
            if is_sensitive:
                masked[key] = mask_value
            elif isinstance(value, dict):
                # Recursively mask nested dictionaries
                masked[key] = cls.mask_dict(value, mask_value)
            elif isinstance(value, list):
                # Recursively mask items in lists
                masked[key] = [
                    cls.mask_dict(item, mask_value) if isinstance(item, dict)
                    else cls.mask_string(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            elif isinstance(value, str):
                # Apply pattern-based masking to strings
                masked[key] = cls.mask_string(value)
            else:
                # Keep other types as-is (int, float, bool, None, etc.)
                masked[key] = value
        
        return masked
    
    @classmethod
    def mask_sensitive_data(cls, data: Any) -> Any:
        """Recursively mask sensitive data in any structure (dict/list/str)"""
        if isinstance(data, dict):
            return cls.mask_dict(data)
        elif isinstance(data, list):
            return [cls.mask_sensitive_data(item) for item in data]
        elif isinstance(data, str):
            return cls.mask_string(data)
        else:
            return data
    
    @classmethod
    def mask_string(cls, text: str, mask_value: str = "***") -> str:
        """Mask sensitive patterns in strings"""
        if not isinstance(text, str):
            return text
        
        masked = text
        for pattern, replacement in cls.SENSITIVE_PATTERNS:
            if isinstance(replacement, str):
                masked = re.sub(pattern, replacement, masked)
            else:
                masked = re.sub(pattern, replacement, masked)
        return masked


class CorrelationContext:
    """Manages correlation IDs and request context for distributed tracing"""
    
    @staticmethod
    def generate_correlation_id() -> str:
        """Generate unique correlation ID"""
        return f"corr-{uuid.uuid4().hex[:16]}"
    
    @staticmethod
    def generate_request_id() -> str:
        """Generate unique request ID"""
        return f"req-{uuid.uuid4().hex[:16]}"
    
    @staticmethod
    def generate_trace_id() -> str:
        """Generate unique trace ID for distributed tracing"""
        return f"trace-{uuid.uuid4().hex[:24]}"
    
    @staticmethod
    def set_correlation_id(corr_id: str):
        """Set correlation ID in context"""
        correlation_id_var.set(corr_id)
    
    @staticmethod
    def get_correlation_id() -> Optional[str]:
        """Get correlation ID from context"""
        return correlation_id_var.get()
    
    @staticmethod
    def set_request_id(req_id: str):
        """Set request ID in context"""
        request_id_var.set(req_id)
    
    @staticmethod
    def get_request_id() -> Optional[str]:
        """Get request ID from context"""
        return request_id_var.get()
    
    @staticmethod
    def set_trace_id(trace_id: str):
        """Set trace ID in context"""
        trace_id_var.set(trace_id)
    
    @staticmethod
    def get_trace_id() -> Optional[str]:
        """Get trace ID from context"""
        return trace_id_var.get()
    
    @staticmethod
    def set_user_context(user_data: Dict):
        """Set user context"""
        user_context_var.set(user_data)
    
    @staticmethod
    def get_user_context() -> Optional[Dict]:
        """Get user context"""
        return user_context_var.get()
    
    @staticmethod
    def clear_context():
        """Clear all context variables"""
        correlation_id_var.set(None)
        request_id_var.set(None)
        trace_id_var.set(None)
        user_context_var.set(None)


class StructuredJSONFormatter(logging.Formatter):
    """Formats logs as structured JSON with all required metadata"""
    
    def __init__(self, environment: str = "development"):
        super().__init__()
        self.environment = environment
        self.hostname = socket.gethostname()
        self.process_id = os.getpid()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        
        # Base log structure
        log_data = {
            # Timestamp in UTC ISO format
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "timestamp_ms": int(record.created * 1000),
            
            # Severity
            "level": record.levelname,
            "severity": self._map_severity(record.levelname),
            
            # Source information
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "file": record.pathname,
            "line": record.lineno,
            "thread": record.thread,
            "thread_name": record.threadName,
            
            # Message
            "message": record.getMessage(),
            
            # Environment & System
            "environment": self.environment,
            "hostname": self.hostname,
            "process_id": self.process_id,
            
            # Distributed tracing
            "correlation_id": CorrelationContext.get_correlation_id(),
            "request_id": CorrelationContext.get_request_id(),
            "trace_id": CorrelationContext.get_trace_id(),
            
            # User context
            "user_context": CorrelationContext.get_user_context(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "stacktrace": self._format_stacktrace(record.exc_info)
            }
        
        # Add custom fields from extra
        if hasattr(record, 'extra_fields'):
            log_data["extra"] = SensitiveDataMasker.mask_dict(record.extra_fields)
        
        # Add execution timing if available
        if hasattr(record, 'execution_time_ms'):
            log_data["execution_time_ms"] = record.execution_time_ms
        
        # Mask sensitive data
        log_data = SensitiveDataMasker.mask_dict(log_data)
        
        return json.dumps(log_data, default=str)
    
    def _map_severity(self, level: str) -> int:
        """Map log level to numeric severity for SIEM systems"""
        severity_map = {
            'DEBUG': 7,      # Informational
            'INFO': 6,       # Informational
            'WARNING': 4,    # Warning
            'ERROR': 3,      # Error
            'CRITICAL': 2    # Critical
        }
        return severity_map.get(level, 6)
    
    def _format_stacktrace(self, exc_info) -> List[str]:
        """Format exception stack trace"""
        return traceback.format_exception(*exc_info)


class EnterpriseLogger:
    """
    Enterprise-grade logger with full observability, traceability, and compliance
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        # Double-checked locking pattern with proper thread safety
        if cls._instance is None:
            with cls._lock:
                # Check again inside lock to prevent race condition
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.environment = os.getenv('TEST_ENV', 'development')
        self.log_level = self._get_log_level()
        
        # Initialize loggers
        self.app_logger = self._setup_application_logger()
        self.audit_logger = self._setup_audit_logger()
        self.security_logger = self._setup_security_logger()
        self.performance_logger = self._setup_performance_logger()
        
        # Async logging queue with bounded size to prevent OOM under high load
        self.log_queue = Queue(maxsize=50_000)
        self.queue_listener = None
        self._shutdown_called = False
        self._setup_async_logging()
        
        # Register atexit handler to ensure graceful shutdown on crashes
        atexit.register(self.shutdown)
        
        # Log system initialization
        self.app_logger.info(
            "Enterprise logging system initialized",
            extra={'extra_fields': {
                'environment': self.environment,
                'log_level': self.log_level,
                'async_logging': True
            }}
        )
    
    def _get_log_level(self) -> int:
        """Determine log level based on environment"""
        level_map = {
            'development': logging.DEBUG,
            'dev': logging.DEBUG,
            'testing': logging.DEBUG,
            'staging': logging.INFO,
            'production': logging.WARNING,
            'prod': logging.WARNING
        }
        return level_map.get(self.environment.lower(), logging.INFO)
    
    def _setup_application_logger(self) -> logging.Logger:
        """Setup main application logger with structured JSON"""
        logger = logging.getLogger('enterprise.app')
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        
        if not logger.handlers:
            # JSON formatted file handler
            json_handler = RotatingFileHandler(
                ENTERPRISE_LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.json",
                maxBytes=100 * 1024 * 1024,  # 100MB
                backupCount=30,
                encoding='utf-8'
            )
            json_handler.setLevel(logging.DEBUG)
            json_handler.setFormatter(StructuredJSONFormatter(self.environment))
            logger.addHandler(json_handler)
            
            # Console handler for development
            if self.environment in ['development', 'dev', 'testing']:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(logging.INFO)
                console_handler.setFormatter(logging.Formatter(
                    '%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                ))
                logger.addHandler(console_handler)
        
        return logger
    
    def _setup_audit_logger(self) -> logging.Logger:
        """Setup audit logger for compliance (SOC2/ISO27001)"""
        logger = logging.getLogger('enterprise.audit')
        logger.setLevel(logging.INFO)
        logger.propagate = False
        
        if not logger.handlers:
            audit_handler = RotatingFileHandler(
                AUDIT_LOG_DIR / f"audit_{datetime.now().strftime('%Y%m%d')}.json",
                maxBytes=50 * 1024 * 1024,  # 50MB
                backupCount=365,  # 1 year retention for compliance
                encoding='utf-8'
            )
            audit_handler.setLevel(logging.INFO)
            audit_handler.setFormatter(StructuredJSONFormatter(self.environment))
            logger.addHandler(audit_handler)
        
        return logger
    
    def _setup_security_logger(self) -> logging.Logger:
        """Setup security logger for auth/authz events"""
        logger = logging.getLogger('enterprise.security')
        logger.setLevel(logging.INFO)
        logger.propagate = False
        
        if not logger.handlers:
            security_handler = RotatingFileHandler(
                SECURITY_LOG_DIR / f"security_{datetime.now().strftime('%Y%m%d')}.json",
                maxBytes=50 * 1024 * 1024,
                backupCount=180,  # 6 months retention
                encoding='utf-8'
            )
            security_handler.setLevel(logging.INFO)
            security_handler.setFormatter(StructuredJSONFormatter(self.environment))
            logger.addHandler(security_handler)
        
        return logger
    
    def _setup_performance_logger(self) -> logging.Logger:
        """Setup performance logger for metrics and timing"""
        logger = logging.getLogger('enterprise.performance')
        logger.setLevel(logging.INFO)
        logger.propagate = False
        
        if not logger.handlers:
            perf_handler = RotatingFileHandler(
                PERFORMANCE_LOG_DIR / f"performance_{datetime.now().strftime('%Y%m%d')}.json",
                maxBytes=50 * 1024 * 1024,
                backupCount=30,
                encoding='utf-8'
            )
            perf_handler.setLevel(logging.INFO)
            perf_handler.setFormatter(StructuredJSONFormatter(self.environment))
            logger.addHandler(perf_handler)
        
        return logger
    
    def _setup_async_logging(self):
        """Setup async logging to prevent blocking"""
        queue_handler = QueueHandler(self.log_queue)
        
        # Get handlers from all loggers
        handlers = []
        for logger in [self.app_logger, self.audit_logger, self.security_logger, self.performance_logger]:
            handlers.extend(logger.handlers[:])
            logger.handlers.clear()
            logger.addHandler(queue_handler)
        
        # Start queue listener
        self.queue_listener = QueueListener(self.log_queue, *handlers, respect_handler_level=True)
        self.queue_listener.start()
    
    def log(self, level: int, message: str, extra: Optional[Dict] = None, **kwargs):
        """Log message with extra metadata"""
        extra_fields = extra or {}
        extra_fields.update(kwargs)
        
        self.app_logger.log(
            level,
            message,
            extra={'extra_fields': extra_fields}
        )
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log error message"""
        self.app_logger.error(
            message,
            exc_info=exc_info,
            extra={'extra_fields': kwargs}
        )
    
    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """Log critical message"""
        self.app_logger.critical(
            message,
            exc_info=exc_info,
            extra={'extra_fields': kwargs}
        )
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback (convenience method)"""
        self.error(message, exc_info=True, **kwargs)
    
    @property
    def level(self) -> int:
        """Get current log level"""
        return self.app_logger.level
    
    @level.setter
    def level(self, level: int):
        """Set log level"""
        self.app_logger.setLevel(level)
    
    def setLevel(self, level: int):
        """Set log level (standard logging interface)"""
        self.app_logger.setLevel(level)
    
    def audit(self, event_type: str, details: Dict, status: str = "success"):
        """Log audit event for compliance"""
        self.audit_logger.info(
            f"Audit: {event_type}",
            extra={'extra_fields': {
                'event_type': event_type,
                'status': status,
                'details': details,
                'audit': True
            }}
        )
    
    def security(self, event_type: str, details: Dict, severity: str = "info"):
        """Log security event"""
        level_map = {
            'info': logging.INFO,
            'warning': logging.WARNING,
            'critical': logging.CRITICAL
        }
        
        self.security_logger.log(
            level_map.get(severity, logging.INFO),
            f"Security: {event_type}",
            extra={'extra_fields': {
                'security_event': event_type,
                'details': details
            }}
        )
    
    def performance(self, operation: str, duration_ms: float, details: Optional[Dict] = None):
        """Log performance metric"""
        perf_data = {
            'operation': operation,
            'duration_ms': duration_ms,
            'details': details or {}
        }
        
        self.performance_logger.info(
            f"Performance: {operation}",
            extra={'extra_fields': perf_data}
        )
    
    def shutdown(self):
        """Gracefully shutdown async logging (idempotent - safe to call multiple times)"""
        # Prevent multiple shutdown calls
        if self._shutdown_called:
            return
        
        self._shutdown_called = True
        
        # Safely stop queue listener if it exists and has a valid thread
        if self.queue_listener and hasattr(self.queue_listener, '_thread'):
            if self.queue_listener._thread is not None:
                try:
                    self.queue_listener.stop()
                except Exception as e:
                    # Log error but don't raise during shutdown
                    import logging
                    logging.getLogger(__name__).warning(
                        f"Error stopping queue listener: {e}", 
                        exc_info=True
                    )


# Singleton instance
_enterprise_logger = None

def get_enterprise_logger(name: Optional[str] = None) -> EnterpriseLogger:
    """Get enterprise logger singleton
    
    Args:
        name: Optional logger name (currently unused, returns singleton)
    
    Returns:
        EnterpriseLogger singleton instance
    """
    global _enterprise_logger
    if _enterprise_logger is None:
        _enterprise_logger = EnterpriseLogger()
    return _enterprise_logger


# Decorators for automatic tracing and logging

def with_correlation(func: Callable) -> Callable:
    """Decorator to add correlation context"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Set correlation ID if not present
        if CorrelationContext.get_correlation_id() is None:
            CorrelationContext.set_correlation_id(CorrelationContext.generate_correlation_id())
        
        if CorrelationContext.get_request_id() is None:
            CorrelationContext.set_request_id(CorrelationContext.generate_request_id())
        
        return func(*args, **kwargs)
    return wrapper


def with_trace(operation_name: str = None):
    """Decorator for distributed tracing with execution timing"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_enterprise_logger()
            op_name = operation_name or func.__name__
            
            # Set trace ID if not present
            if CorrelationContext.get_trace_id() is None:
                CorrelationContext.set_trace_id(CorrelationContext.generate_trace_id())
            
            start_time = time.time()
            
            try:
                logger.debug(
                    f"Starting operation: {op_name}",
                    operation=op_name,
                    function=func.__name__,
                    module=func.__module__
                )
                
                result = func(*args, **kwargs)
                
                execution_time = (time.time() - start_time) * 1000  # ms
                
                logger.info(
                    f"✓ Completed operation: {op_name}",
                    operation=op_name,
                    execution_time_ms=execution_time,
                    status="success"
                )
                
                logger.performance(op_name, execution_time)
                
                return result
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                
                logger.error(
                    f"✗ Failed operation: {op_name}",
                    exc_info=True,
                    operation=op_name,
                    execution_time_ms=execution_time,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                
                raise
        
        return wrapper
    return decorator


def with_async_trace(operation_name: str = None):
    """Decorator for async function tracing"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_enterprise_logger()
            op_name = operation_name or func.__name__
            
            if CorrelationContext.get_trace_id() is None:
                CorrelationContext.set_trace_id(CorrelationContext.generate_trace_id())
            
            start_time = time.time()
            
            try:
                logger.debug(f"Starting async operation: {op_name}", operation=op_name)
                
                result = await func(*args, **kwargs)
                
                execution_time = (time.time() - start_time) * 1000
                logger.info(
                    f"✓ Completed async operation: {op_name}",
                    operation=op_name,
                    execution_time_ms=execution_time
                )
                
                return result
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logger.error(
                    f"✗ Failed async operation: {op_name}",
                    exc_info=True,
                    operation=op_name,
                    execution_time_ms=execution_time,
                    error_type=type(e).__name__
                )
                raise
        
        return wrapper
    return decorator


# Specialized Loggers for Compliance and Security
class AuditLogger:
    """SOC2/ISO27001 compliant audit logger for tracking user actions"""
    
    def __init__(self, logger_name: str = "enterprise.audit"):
        self.logger = logging.getLogger(logger_name)
    
    def log_action(
        self,
        action: str,
        actor: str,
        resource: str,
        status: str,
        changes: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """Log audit trail event
        
        Args:
            action: Action performed (e.g., 'user_login', 'data_export')
            actor: Who performed the action (user ID, username)
            resource: Resource affected (table name, file path)
            status: success/failure/denied
            changes: Before/after values for data changes
        """
        self.logger.info(
            f"AUDIT: {action}",
            extra={
                'audit_action': action,
                'actor': actor,
                'resource': resource,
                'status': status,
                'changes': changes or {},
                **kwargs
            }
        )


class SecurityLogger:
    """Security event logger for incident tracking and alerting"""
    
    def __init__(self, logger_name: str = "enterprise.security"):
        self.logger = logging.getLogger(logger_name)
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        source_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log security event
        
        Args:
            event_type: Type of security event (unauthorized_access, brute_force, etc.)
            severity: LOW/MEDIUM/HIGH/CRITICAL
            description: Human-readable description
            source_ip: IP address of request
            user_agent: User agent string
        """
        log_method = getattr(self.logger, severity.lower(), self.logger.warning)
        log_method(
            f"SECURITY [{severity}]: {event_type}",
            extra={
                'security_event': event_type,
                'severity': severity,
                'description': description,
                'source_ip': source_ip,
                'user_agent': user_agent,
                **kwargs
            }
        )


class PerformanceLogger:
    """Performance metrics logger for monitoring and optimization"""
    
    def __init__(self, logger_name: str = "enterprise.performance"):
        self.logger = logging.getLogger(logger_name)
    
    def log_metric(
        self,
        metric_name: str,
        value: Union[int, float],
        unit: str,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> None:
        """Log performance metric
        
        Args:
            metric_name: Name of metric (api_response_time, db_query_duration)
            value: Numeric value
            unit: Unit of measurement (ms, seconds, count)
            tags: Additional tags for filtering (endpoint, environment)
        """
        self.logger.info(
            f"METRIC: {metric_name}={value}{unit}",
            extra={
                'metric_name': metric_name,
                'metric_value': value,
                'metric_unit': unit,
                'tags': tags or {},
                **kwargs
            }
        )
    
    def log_threshold_violation(
        self,
        metric_name: str,
        value: Union[int, float],
        threshold: Union[int, float],
        **kwargs
    ) -> None:
        """Log when metric exceeds threshold"""
        self.logger.warning(
            f"THRESHOLD VIOLATION: {metric_name}={value} exceeds {threshold}",
            extra={
                'metric_name': metric_name,
                'metric_value': value,
                'threshold': threshold,
                **kwargs
            }
        )


__all__ = [
    'EnterpriseLogger',
    'get_enterprise_logger',
    'CorrelationContext',
    'SensitiveDataMasker',
    'AuditLogger',
    'SecurityLogger',
    'PerformanceLogger',
    'with_correlation',
    'with_trace',
    'with_async_trace'
]
