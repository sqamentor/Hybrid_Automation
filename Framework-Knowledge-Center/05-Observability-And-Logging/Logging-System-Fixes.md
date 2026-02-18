# Enterprise Logging System - Critical Fixes Implementation Guide

**Status:** 6 critical fixes required to reach production-ready state  
**Estimated Time:** 2-3 hours  
**Target Grade:** B+ (85%+) → Current: C (67%)

---

## Fix #1: OpenTelemetry Hard Dependency (P0 - BLOCKER)

**Issue:** Cannot use logging without installing OpenTelemetry packages

**File:** `framework/observability/__init__.py`

**Current Code:**
```python
# This causes crash if opentelemetry not installed
from framework.observability.telemetry import TelemetryManager, get_telemetry
```

**Fixed Code:**
```python
# framework/observability/__init__.py

# Core logging (always available)
from framework.observability.enterprise_logger import (
    get_enterprise_logger,
    CorrelationContext,
    SensitiveDataMasker,
    AuditLogger,
    SecurityLogger,
    PerformanceLogger,
    StructuredJSONFormatter,
)

from framework.observability.universal_logger import (
    log_function,
    log_async_function,
    log_state_transition,
    log_retry_operation,
    log_operation,
    OperationLogger,
)

from framework.observability.logging_config import (
    LoggingConfigManager,
    Environment,
    RetentionPolicy,
    SamplingConfig,
)

# Optional telemetry (lazy load)
try:
    from framework.observability.telemetry import (
        TelemetryManager,
        get_telemetry,
    )
    TELEMETRY_AVAILABLE = True
except ImportError as e:
    TELEMETRY_AVAILABLE = False
    TelemetryManager = None
    
    def get_telemetry():
        """Fallback when telemetry not available"""
        import logging
        logging.warning("Telemetry requested but OpenTelemetry not installed")
        return None

# Optional SIEM adapters (lazy load)
try:
    from framework.observability.siem_adapters import (
        SIEMAdapterFactory,
        BaseSIEMAdapter,
    )
    SIEM_AVAILABLE = True
except ImportError:
    SIEM_AVAILABLE = False
    SIEMAdapterFactory = None
    BaseSIEMAdapter = None

__all__ = [
    # Core logging (always available)
    "get_enterprise_logger",
    "CorrelationContext",
    "SensitiveDataMasker",
    "AuditLogger",
    "SecurityLogger",
    "PerformanceLogger",
    "StructuredJSONFormatter",
    "log_function",
    "log_async_function",
    "log_state_transition",
    "log_retry_operation",
    "log_operation",
    "OperationLogger",
    "LoggingConfigManager",
    "Environment",
    "RetentionPolicy",
    "SamplingConfig",
    
    # Optional features (may be None)
    "TelemetryManager",
    "get_telemetry",
    "SIEMAdapterFactory",
    "BaseSIEMAdapter",
    
    # Availability flags
    "TELEMETRY_AVAILABLE",
    "SIEM_AVAILABLE",
]
```

**Validation:**
```python
# Should work without opentelemetry installed
from framework.observability import get_enterprise_logger, TELEMETRY_AVAILABLE

logger = get_enterprise_logger(__name__)
logger.info("This works without opentelemetry")

if TELEMETRY_AVAILABLE:
    from framework.observability import get_telemetry
    telemetry = get_telemetry()
else:
    print("Running without telemetry (OK)")
```

---

## Fix #2: Environment Enum Handling (P0 - BLOCKER)

**Issue:** `'Environment' object has no attribute 'lower'`

**File:** `framework/observability/logging_config.py`

**Current Code:**
```python
def get_config(self, environment: Union[Environment, str]) -> Dict[str, Any]:
    env = environment.lower()  # FAILS if Environment enum passed
    # ...
```

**Fixed Code:**
```python
def get_config(self, environment: Union[Environment, str]) -> Dict[str, Any]:
    """
    Get configuration for specified environment.
    
    Args:
        environment: Environment enum or string ('development', 'testing', 'staging', 'production')
    
    Returns:
        Configuration dictionary for the environment
    """
    # Normalize to lowercase string
    if isinstance(environment, Environment):
        env_str = environment.value.lower()  # Use .value for enum
    elif isinstance(environment, str):
        env_str = environment.lower()
    else:
        raise TypeError(f"environment must be Environment enum or string, got {type(environment)}")
    
    # Validate environment
    valid_envs = ['development', 'testing', 'staging', 'production']
    if env_str not in valid_envs:
        raise ValueError(f"Invalid environment: {env_str}. Must be one of {valid_envs}")
    
    # Load from cache or file
    if env_str in self._configs:
        return self._configs[env_str]
    
    # Generate default config
    config = self._get_default_config(env_str)
    self._configs[env_str] = config
    return config
```

**Validation:**
```python
from framework.observability import LoggingConfigManager, Environment

config_manager = LoggingConfigManager()

# Both should work now
config1 = config_manager.get_config(Environment.PRODUCTION)  # Enum
config2 = config_manager.get_config('production')             # String

assert config1 == config2
```

---

## Fix #3: Export Specialized Loggers (P0 - BLOCKER for Compliance)

**Issue:** AuditLogger, SecurityLogger, PerformanceLogger not accessible

**File:** `framework/observability/enterprise_logger.py`

**Add to bottom of file:**
```python
# At end of framework/observability/enterprise_logger.py

__all__ = [
    # Core logger
    'get_enterprise_logger',
    'setup_enterprise_logging',
    
    # Context and masking
    'CorrelationContext',
    'SensitiveDataMasker',
    
    # Formatters
    'StructuredJSONFormatter',
    
    # Specialized loggers
    'AuditLogger',
    'SecurityLogger',
    'PerformanceLogger',
    
    # Configuration
    'LoggingConfig',
]
```

**Also check initialization:**
```python
# Make sure these classes are properly defined and importable
class AuditLogger:
    """SOC2/ISO27001 compliant audit logger"""
    
    def __init__(self, logger_name: str = "audit"):
        self.logger = get_enterprise_logger(logger_name)
    
    def log_action(
        self,
        action: str,
        actor: str,
        resource: str,
        status: str,
        changes: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """Log audit trail event"""
        # Implementation should already exist
        pass


class SecurityLogger:
    """Security event logger for incident tracking"""
    
    def __init__(self, logger_name: str = "security"):
        self.logger = get_enterprise_logger(logger_name)
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        source_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log security event"""
        # Implementation should already exist
        pass


class PerformanceLogger:
    """Performance metrics logger"""
    
    def __init__(self, logger_name: str = "performance"):
        self.logger = get_enterprise_logger(logger_name)
    
    def log_metric(
        self,
        metric_name: str,
        value: Union[int, float],
        unit: str,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> None:
        """Log performance metric"""
        # Implementation should already exist
        pass
```

**Validation:**
```python
from framework.observability import (
    AuditLogger,
    SecurityLogger,
    PerformanceLogger
)

# Should create loggers successfully
audit = AuditLogger()
audit.log_action("user_login", actor="john", resource="admin_panel", status="success")

security = SecurityLogger()
security.log_security_event("unauthorized_access", severity="HIGH", description="Invalid token")

performance = PerformanceLogger()
performance.log_metric("api_response_time", 245, "ms", tags={"endpoint": "/api/users"})
```

---

## Fix #4: Nested Data Masking Bug (P1 - Security Issue)

**Issue:** `string indices must be integers, not 'str'` when masking nested structures

**File:** `framework/observability/enterprise_logger.py`

**Current Code (likely buggy):**
```python
def mask_sensitive_data(self, data: Any) -> Any:
    if isinstance(data, dict):
        return {k: self.mask_sensitive_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [self.mask_sensitive_data(item) for item in data]
    # Missing proper string handling
    for key in self.SENSITIVE_KEYS:
        if key in data:  # BUG: tries to use 'in' on string
            data[key] = "***REDACTED***"
    return data
```

**Fixed Code:**
```python
def mask_sensitive_data(self, data: Any) -> Any:
    """
    Recursively mask sensitive data in dictionaries, lists, and strings.
    
    Args:
        data: Data structure to mask (dict, list, str, or other)
    
    Returns:
        Masked copy of data structure
    """
    # Handle dictionaries (check keys and recurse values)
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            # Mask sensitive keys
            if key.lower() in [k.lower() for k in self.SENSITIVE_KEYS]:
                masked[key] = "***REDACTED***"
            else:
                # Recurse into value
                masked[key] = self.mask_sensitive_data(value)
        return masked
    
    # Handle lists (recurse each item)
    elif isinstance(data, list):
        return [self.mask_sensitive_data(item) for item in data]
    
    # Handle strings (apply regex patterns)
    elif isinstance(data, str):
        masked_str = data
        for pattern in self.SENSITIVE_PATTERNS:
            masked_str = pattern.sub(r'\1***REDACTED***', masked_str)
        return masked_str
    
    # Handle other types (numbers, bools, None) - return as-is
    else:
        return data
```

**Validation:**
```python
from framework.observability import SensitiveDataMasker

masker = SensitiveDataMasker()

# Test nested structure
data = {
    "user": {
        "email": "user@example.com",
        "profile": {
            "password": "secret123",
            "api_key": "sk-abc123",
            "bio": "Contact me at admin@example.com"
        }
    },
    "safe_data": "This is public"
}

masked = masker.mask_sensitive_data(data)

# Verify all sensitive data masked
assert "secret123" not in str(masked)
assert "sk-abc123" not in str(masked)
assert "user@example.com" not in str(masked)
assert "admin@example.com" not in str(masked)
assert "This is public" in str(masked)  # Safe data preserved
```

---

## Fix #5: Export Advanced Decorators (P1)

**Issue:** `log_state_transition`, `log_retry_operation` not exported

**File:** `framework/observability/universal_logger.py`

**Add to bottom of file:**
```python
# At end of framework/observability/universal_logger.py

__all__ = [
    'log_function',
    'log_async_function',
    'log_state_transition',
    'log_retry_operation',
    'log_operation',
    'OperationLogger',
]
```

**Ensure decorators are properly defined:**
```python
def log_state_transition(
    state_field: str = "state",
    log_args: bool = True,
    log_result: bool = True
):
    """
    Decorator for logging state machine transitions.
    
    Args:
        state_field: Name of attribute holding state
        log_args: Whether to log function arguments
        log_result: Whether to log return value
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Implementation should already exist
            pass
        return wrapper
    return decorator


def log_retry_operation(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    log_each_attempt: bool = True
):
    """
    Decorator for logging retry operations with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
        log_each_attempt: Whether to log each retry attempt
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Implementation should already exist
            pass
        return wrapper
    return decorator
```

**Validation:**
```python
from framework.observability import (
    log_state_transition,
    log_retry_operation
)

# Should work now
class StateMachine:
    def __init__(self):
        self.state = "idle"
    
    @log_state_transition(state_field="state")
    def transition_to_running(self):
        self.state = "running"
        return self.state

@log_retry_operation(max_retries=3, backoff_factor=2.0)
def flaky_api_call():
    import random
    if random.random() < 0.5:
        raise ConnectionError("Network error")
    return "success"
```

---

## Fix #6: Export Context Managers (P1)

**Issue:** `log_operation`, `OperationLogger` not exported

**File:** `framework/observability/universal_logger.py`

**Already covered in Fix #5** - ensure these are in `__all__`

**Ensure proper implementation:**
```python
class OperationLogger:
    """Context manager for logging complex operations"""
    
    def __init__(
        self,
        operation_name: str,
        logger: Optional[logging.Logger] = None,
        log_args: bool = True,
        **context
    ):
        self.operation_name = operation_name
        self.logger = logger or get_enterprise_logger(__name__)
        self.context = context
        self.start_time = None
        self.success = False
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(
            f"Starting operation: {self.operation_name}",
            extra={"context": self.context}
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        
        if exc_type is None:
            self.success = True
            self.logger.info(
                f"Completed operation: {self.operation_name}",
                extra={
                    "duration_ms": duration_ms,
                    "success": True,
                    "context": self.context
                }
            )
        else:
            self.logger.error(
                f"Failed operation: {self.operation_name}",
                extra={
                    "duration_ms": duration_ms,
                    "success": False,
                    "error": str(exc_val),
                    "context": self.context
                },
                exc_info=(exc_type, exc_val, exc_tb)
            )
        
        return False  # Don't suppress exceptions


def log_operation(operation_name: str, logger: Optional[logging.Logger] = None, **context):
    """
    Convenience function to create OperationLogger context manager.
    
    Usage:
        with log_operation("database_query", query_type="SELECT"):
            results = db.execute(query)
    """
    return OperationLogger(operation_name, logger, **context)
```

**Validation:**
```python
from framework.observability import log_operation, OperationLogger

# Method 1: Function-based
with log_operation("database_query", query_type="SELECT"):
    # Do complex operation
    result = perform_query()

# Method 2: Class-based
with OperationLogger("file_processing", file_name="data.csv"):
    # Process file
    process_file()
```

---

## Implementation Checklist

### Critical Fixes (Must complete all)

- [ ] **Fix #1:** OpenTelemetry lazy loading in `__init__.py`
  - [ ] Wrap telemetry import in try/except
  - [ ] Add TELEMETRY_AVAILABLE flag
  - [ ] Add fallback get_telemetry() function
  - [ ] Test import without opentelemetry installed

- [ ] **Fix #2:** Environment enum handling in `logging_config.py`
  - [ ] Add isinstance(environment, Environment) check
  - [ ] Use environment.value.lower() for enum
  - [ ] Add type validation
  - [ ] Test with both enum and string

- [ ] **Fix #3:** Export specialized loggers in `enterprise_logger.py`
  - [ ] Add __all__ list with AuditLogger, SecurityLogger, PerformanceLogger
  - [ ] Verify classes are properly defined
  - [ ] Test instantiation and log methods

- [ ] **Fix #4:** Nested data masking in `enterprise_logger.py`
  - [ ] Add isinstance(data, str) check
  - [ ] Fix recursive dict/list traversal
  - [ ] Test with nested structures

- [ ] **Fix #5:** Export advanced decorators in `universal_logger.py`
  - [ ] Add __all__ list with log_state_transition, log_retry_operation
  - [ ] Verify decorators are defined
  - [ ] Test decorator functionality

- [ ] **Fix #6:** Export context managers in `universal_logger.py`
  - [ ] Add log_operation, OperationLogger to __all__
  - [ ] Verify OperationLogger class implementation
  - [ ] Test with context manager

### Post-Fix Validation

- [ ] Re-run audit script: `python scripts/audit_logging_system.py`
  - [ ] Target: 15+/18 tests passing (85%+)
  - [ ] Target Grade: B+ or A

- [ ] Manual smoke tests:
  ```python
  # Test 1: Import without opentelemetry
  from framework.observability import get_enterprise_logger
  logger = get_enterprise_logger(__name__)
  logger.info("Basic logging works")
  
  # Test 2: Environment config
  from framework.observability import LoggingConfigManager, Environment
  config = LoggingConfigManager().get_config(Environment.PRODUCTION)
  
  # Test 3: Specialized loggers
  from framework.observability import AuditLogger, SecurityLogger, PerformanceLogger
  audit = AuditLogger()
  audit.log_action("test", actor="system", resource="test", status="success")
  
  # Test 4: Advanced decorators
  from framework.observability import log_state_transition, log_retry_operation
  
  # Test 5: Context managers
  from framework.observability import log_operation
  with log_operation("test_operation"):
      pass
  
  # Test 6: Nested masking
  from framework.observability import SensitiveDataMasker
  masker = SensitiveDataMasker()
  data = {"user": {"email": "test@example.com", "nested": {"password": "secret"}}}
  masked = masker.mask_sensitive_data(data)
  assert "secret" not in str(masked)
  ```

- [ ] Check for regressions:
  - [ ] Run existing pytest suite
  - [ ] Verify no circular import errors
  - [ ] Check log file generation

---

## Expected Results After Fixes

### Before Fixes (Current State)
- **Grade:** C (66.7%)
- **Functionality:** 63.6% (7/11)
- **Dynamic:** 66.7% (2/3)
- **Reusability:** 75.0% (3/4)
- **Production Ready:** ❌ NO

### After Fixes (Target State)
- **Grade:** B+ to A (85-95%)
- **Functionality:** 90%+ (10/11)
- **Dynamic:** 100% (3/3)
- **Reusability:** 100% (4/4)
- **Production Ready:** ✅ YES

### Remaining Known Issues (Low Priority)
- SIEM integration not tested (requires external services)
- Telemetry not tested (requires OpenTelemetry setup)
- Performance benchmarks not run
- Load testing not performed

---

## Time Estimates

| Fix | Priority | Estimated Time | Complexity |
|-----|----------|----------------|------------|
| #1 - OpenTelemetry lazy load | P0 | 30 minutes | Medium |
| #2 - Environment enum | P0 | 10 minutes | Easy |
| #3 - Export specialized loggers | P0 | 20 minutes | Easy |
| #4 - Nested data masking | P1 | 15 minutes | Medium |
| #5 - Export advanced decorators | P1 | 10 minutes | Easy |
| #6 - Export context managers | P1 | 10 minutes | Easy |
| **Testing & Validation** | - | 30 minutes | Medium |
| **TOTAL** | - | **2-3 hours** | - |

---

## Success Criteria

✅ **Minimum Viable (B grade):**
- All P0 fixes applied (OpenTelemetry, Environment, Specialized loggers)
- Audit passes 15+/18 tests (85%+)
- Can import and use without opentelemetry installed
- Environment switching works with enums
- Specialized loggers accessible

✅ **Production Ready (A grade):**
- All fixes applied (P0 + P1)
- Audit passes 16+/18 tests (90%+)
- All decorators and context managers working
- Nested data masking secure
- No blocking issues remaining

---

## Post-Fix Documentation

After completing fixes, update:

1. **README.md** - Add usage examples for all decorators and loggers
2. **examples/logging_examples.py** - Create comprehensive example file
3. **docs/LOGGING_GUIDE.md** - Full user guide
4. **CHANGELOG.md** - Document fixes with version bump

---

*Implementation guide created: February 18, 2026*  
*Based on audit results: Grade C (66.7%)*  
*Target after fixes: Grade B+ (85%+)*
