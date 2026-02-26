# Enterprise Logging — Implementation & Integration Guide

**Version:** 1.0.0
**Status:** ✅ Production-Ready
**Canonical Source:** This file supersedes `Enterprise-Logging-Integration-Guide.md`,
`Logging-System-Fixes.md`, and `Logging-Enhancements.md`

---

## Table of Contents

1. [Overview](#overview)
2. [Integration Priority & Phases](#integration-priority--phases)
3. [Code Integration Patterns](#code-integration-patterns)
4. [File-by-File Integration Examples](#file-by-file-integration-examples)
5. [Critical Fixes Applied](#critical-fixes-applied)
6. [Enhanced Components](#enhanced-components)
7. [Common Patterns Quick Reference](#common-patterns-quick-reference)
8. [Validation Checklist](#validation-checklist)

---

## Overview

This guide provides **concrete, actionable steps** to integrate the enterprise logging
system throughout the entire codebase. The enterprise logging system delivers:

- ✅ Replace all standard `logging` with `EnterpriseLogger`
- ✅ Add correlation IDs to all request flows
- ✅ Integrate `@with_trace` decorators for critical operations
- ✅ 100% log coverage across all modules
- ✅ Audit logging for all user actions
- ✅ Security logging for authentication/authorization
- ✅ Performance logging for slow operations

### Quick Import

```python
from framework.observability.enterprise_logger import (
    get_enterprise_logger,
    with_trace,
    with_async_trace,
    CorrelationContext,
    AuditLogger,
    SecurityLogger,
    PerformanceLogger
)
```

---

## Integration Priority & Phases

### Phase 1 — Critical Infrastructure (Week 1) ⚡

| Priority | File | Change |
|----------|------|--------|
| P1 | `conftest.py` (root) | Enable pytest plugin |
| P1 | `framework/core/smart_actions.py` | Full logging integration |
| P1 | `framework/ui/base_page.py` | Base class integration |
| P1 | `framework/ui/selenium_engine.py` | Engine lifecycle logging |
| P1 | `framework/ui/playwright_engine.py` | Engine lifecycle logging |

### Phase 2 — Page Objects & Tests (Week 2) 📋

| Priority | File | Change |
|----------|------|--------|
| P2 | `pages/bookslot/*.py` | Audit events per step |
| P2 | `pages/callcenter/*.py` | Audit events |
| P2 | `pages/patientintake/*.py` | Audit events |
| P2 | `tests/**/*.py` | Test lifecycle logging |

### Phase 3 — Advanced Components (Week 3) 📝

| Priority | File | Change |
|----------|------|--------|
| P3 | `framework/api/api_client.py` | Request/response logging |
| P3 | `framework/database/db_client.py` | Query logging |
| P3 | `framework/plugins/` | Plugin lifecycle |
| P3 | `framework/ml/`, `framework/ai/` | Model operations |

---

## Code Integration Patterns

### Pattern 1 — Enable Pytest Plugin

**File:** `conftest.py` (root)

```python
pytest_plugins = [
    'framework.observability.pytest_enterprise_logging',
    'scripts.governance.pytest_arch_audit_plugin',
]
```

Validation:
```bash
pytest --collect-only
# Should see: "plugin: pytest_enterprise_logging"
```

### Pattern 2 — Class Initialization

```python
from framework.observability.enterprise_logger import get_enterprise_logger, CorrelationContext

class MyClass:
    def __init__(self):
        self.logger = get_enterprise_logger()

        # Set correlation ID if not exists (typically done by pytest plugin)
        if not CorrelationContext.get_correlation_id():
            CorrelationContext.set_correlation_id(
                CorrelationContext.generate_correlation_id()
            )

        self.logger.info("MyClass initialized")
```

### Pattern 3 — Function with Trace Decorator

```python
@with_trace(operation_name="descriptive_operation_name")
def my_function(param1: str, param2: int) -> bool:
    logger = get_enterprise_logger()
    logger.info("Starting operation", param1=param1, param2=param2)
    # ... implementation ...
    logger.info("✓ Operation successful")
    return True
```

### Pattern 4 — Async Function with Trace

```python
@with_async_trace(operation_name="async_operation")
async def my_async_function(url: str) -> dict:
    logger = get_enterprise_logger()
    logger.info("Starting async operation", url=url)
    # ... implementation ...
    return result
```

### Pattern 5 — Audit Logging for User Actions

```python
logger.audit("user_action_performed", {
    "user_id": user_id,
    "action": action,
    "timestamp": datetime.now().isoformat(),
    "workflow": "appointment_booking"
}, status="success")
```

### Pattern 6 — Security Logging

```python
def login_attempt(username: str, success: bool):
    logger = get_enterprise_logger()
    if not success:
        logger.security("failed_login_attempt", {
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "attempts": get_attempt_count(username)
        })
```

### Pattern 7 — Performance Logging

```python
start_time = time.time()
# ... slow operation ...
duration_ms = (time.time() - start_time) * 1000

logger.performance("operation_name", duration_ms, {
    "page": "bookslot_scheduler",
    "slot_count": len(slots)
})

if duration_ms > 2000:
    logger.warning("Slow operation detected", duration_ms=duration_ms)
```

### Pattern 8 — Silent Exception Handler (FIXED pattern)

❌ BEFORE (forbidden):
```python
try:
    element.click()
except:
    pass
```

✅ AFTER (required):
```python
try:
    element.click()
except Exception as exc:
    logger.warning("Click failed, continuing", error=str(exc), locator=locator)
```

---

## File-by-File Integration Examples

### Smart Actions (`framework/core/smart_actions.py`)

```python
from framework.observability.enterprise_logger import get_enterprise_logger, with_trace, CorrelationContext

class SmartActions:
    def __init__(self, driver_or_page, context=None):
        self.driver = driver_or_page
        self.logger = get_enterprise_logger()
        self.logger.info("SmartActions initialized",
                        engine_type=type(driver_or_page).__name__)

    @with_trace(operation_name="ui_click")
    def click(self, locator, description: str = "") -> bool:
        self.logger.info("Clicking element", locator=str(locator), description=description)
        try:
            # ... implementation ...
            self.logger.audit("element_clicked", {
                "locator": str(locator),
                "description": description
            }, status="success")
            return True
        except Exception as e:
            self.logger.error("Click failed", locator=str(locator), exc_info=True)
            raise

    @with_trace(operation_name="ui_type_text")
    def type_text(self, locator, text: str, description: str = "") -> bool:
        self.logger.info("Typing text", locator=str(locator), text_length=len(text))
        try:
            # ... implementation ...
            self.logger.audit("text_entered", {
                "locator": str(locator),
                "field_type": "text",
                "text_length": len(text)
            }, status="success")
            return True
        except Exception as e:
            self.logger.error("Type text failed", locator=str(locator), exc_info=True)
            raise

    @with_trace(operation_name="ui_navigate")
    def navigate(self, url: str, description: str = "") -> None:
        self.logger.info("Navigating", url=url)
        start_time = time.time()
        try:
            self.driver.goto(url)
            duration_ms = (time.time() - start_time) * 1000
            self.logger.performance("page_navigation", duration_ms, {"url": url})
            self.logger.audit("navigation", {"url": url}, status="success")
            if duration_ms > 5000:
                self.logger.warning("Slow page load", url=url, duration_ms=duration_ms)
        except Exception as e:
            self.logger.error("Navigation failed", url=url, exc_info=True)
            raise
```

### Base Page (`framework/ui/base_page.py`)

```python
from framework.observability.enterprise_logger import get_enterprise_logger, with_trace

class BasePage(ABC):
    def __init__(self, driver_or_page):
        self.driver = driver_or_page
        self.logger = get_enterprise_logger()
        page_name = self.__class__.__name__
        self.logger.info("Page object initialized", page=page_name)
        self.logger.audit("page_load", {"page": page_name}, status="initialized")

    @with_trace(operation_name="page_wait_for_load")
    def wait_for_page_load(self, timeout: int = 30) -> bool:
        page_name = self.__class__.__name__
        start_time = time.time()
        try:
            success = self._wait_implementation(timeout)
            duration_ms = (time.time() - start_time) * 1000
            self.logger.performance("page_load_wait", duration_ms, {"page": page_name})
            if duration_ms > 10000:
                self.logger.warning("Slow page load", page=page_name, duration_ms=duration_ms)
            return success
        except TimeoutException:
            self.logger.error("Page load timeout", page=page_name, timeout=timeout)
            raise
```

### Selenium Engine (`framework/ui/selenium_engine.py`)

```python
@with_trace(operation_name="selenium_engine_start")
def start(self) -> WebDriver:
    browser = self.config.get('browser', 'chrome')
    self.logger.info("Starting Selenium driver", browser=browser)
    session_id = CorrelationContext.generate_correlation_id()
    CorrelationContext.set_correlation_id(session_id)
    try:
        start_time = time.time()
        self.driver = self._initialize_driver(browser)
        duration_ms = (time.time() - start_time) * 1000
        self.logger.performance("driver_startup", duration_ms, {
            "browser": browser, "session_id": session_id
        })
        self.logger.audit("engine_started", {
            "engine": "selenium", "browser": browser
        }, status="success")
        return self.driver
    except Exception as e:
        self.logger.error("Failed to start Selenium driver", browser=browser, exc_info=True)
        raise
```

### API Client (`framework/api/api_client.py`)

```python
@with_trace(operation_name="api_request")
def request(self, method: str, endpoint: str, data: dict = None) -> dict:
    url = f"{self.base_url}{endpoint}"
    correlation_id = CorrelationContext.get_correlation_id()
    headers = {**self.headers, 'X-Correlation-ID': correlation_id or ''}
    self.logger.info("API request", method=method, endpoint=endpoint)
    start_time = time.time()
    try:
        response = self.session.request(method, url, json=data, headers=headers)
        duration_ms = (time.time() - start_time) * 1000
        self.logger.performance("api_call", duration_ms, {
            "method": method, "endpoint": endpoint,
            "status_code": response.status_code
        })
        self.logger.audit("api_request_completed", {
            "method": method, "endpoint": endpoint,
            "status_code": response.status_code, "duration_ms": duration_ms
        }, status="success" if response.status_code < 400 else "failed")
        if response.status_code in [401, 403]:
            self.logger.security("api_auth_failure", {
                "endpoint": endpoint, "status_code": response.status_code
            })
        if duration_ms > 2000:
            self.logger.warning("Slow API call", endpoint=endpoint, duration_ms=duration_ms)
        return response.json()
    except Exception as e:
        self.logger.error("API request failed", method=method, endpoint=endpoint, exc_info=True)
        raise
```

### Test File Pattern

```python
import pytest
from framework.observability.enterprise_logger import get_enterprise_logger

logger = get_enterprise_logger()

@pytest.mark.bookslot
@pytest.mark.e2e
def test_complete_booking(page, enterprise_logging_context, multi_project_config, fake_bookslot_data):
    """The enterprise_logging_context fixture auto-provides correlation ID"""

    enterprise_logging_context.set_user({"user_id": "test_user", "role": "tester"})

    logger.info("Starting booking test")
    logger.audit("test_started", {"test": "complete_booking"}, status="started")

    # ... test steps ...

    logger.audit("test_completed", {"result": "PASSED"}, status="success")
```

---

## Critical Fixes Applied

These fixes were required for production-ready logging. All are now resolved.

### Fix 1 — OpenTelemetry Hard Dependency Removed

**Problem:** `from opentelemetry import ...` caused ImportError when opentelemetry
not installed, crashing the entire logging system.

**Fix:** Wrapped in try/except with graceful degradation:
```python
try:
    from opentelemetry import trace as otel_trace
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    # Logger works without OpenTelemetry
```

### Fix 2 — Environment Enum Handling

**Problem:** `Environment.from_string('testing')` raised `KeyError` for unknown
environment strings.

**Fix:**
```python
@classmethod
def from_string(cls, env_str: str) -> 'Environment':
    mapping = {
        'development': cls.DEVELOPMENT, 'dev': cls.DEVELOPMENT,
        'testing': cls.TESTING, 'test': cls.TESTING,
        'staging': cls.STAGING, 'stage': cls.STAGING,
        'production': cls.PRODUCTION, 'prod': cls.PRODUCTION
    }
    return mapping.get(env_str.lower(), cls.TESTING)  # default to TESTING
```

### Fix 3 — Export All Specialized Loggers

**Problem:** `AuditLogger`, `SecurityLogger`, `PerformanceLogger` not exported
from module `__init__.py`.

**Fix in `framework/observability/__init__.py`:**
```python
from .enterprise_logger import (
    EnterpriseLogger,
    get_enterprise_logger,
    AuditLogger,
    SecurityLogger,
    PerformanceLogger,
    CorrelationContext,
    with_trace,
    with_async_trace,
    with_correlation,
    SensitiveDataMasker,
)
```

### Fix 4 — Nested Data Masking Bug

**Problem:** `SensitiveDataMasker` only masked top-level dict keys, missed
nested dicts like `{"user": {"password": "secret"}}`.

**Fix:**
```python
def mask_dict(self, data: dict, depth: int = 0) -> dict:
    if depth > 10:  # Prevent infinite recursion
        return data
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = self.mask_dict(value, depth + 1)  # Recurse
        elif isinstance(value, list):
            result[key] = [
                self.mask_dict(item, depth + 1) if isinstance(item, dict) else item
                for item in value
            ]
        elif self._is_sensitive_key(key):
            result[key] = "***MASKED***"
        else:
            result[key] = self.mask_string(str(value)) if isinstance(value, str) else value
    return result
```

### Fix 5 — Export Advanced Decorators

**Problem:** `@with_trace`, `@with_async_trace`, `@with_correlation` not exported.

**Fix:** Added to `__all__` in `enterprise_logger.py`:
```python
__all__ = [
    'EnterpriseLogger', 'get_enterprise_logger',
    'CorrelationContext', 'SensitiveDataMasker',
    'with_trace', 'with_async_trace', 'with_correlation',
    'AuditLogger', 'SecurityLogger', 'PerformanceLogger',
]
```

### Fix 6 — Silent Exception Handlers (31 Fixed)

**Problem:** 31 `except: pass` blocks suppressed errors silently.

**Pattern applied across all 31 locations:**
```python
# BEFORE
except:
    pass

# AFTER
except Exception as exc:
    logger.warning("Operation failed, continuing", error=str(exc), exc_info=False)
```

---

## Enhanced Components

### Enhanced Core Logger (`utils/logger.py`)

- `get_logger(name)` returns logger with:
  - Console: INFO level, human-readable format
  - File: DEBUG level, 30-day daily rotation → `logs/framework_YYYYMMDD.log`
  - Error file: ERROR+ only → `logs/errors_YYYYMMDD.log`
  - Warnings file: `logs/warnings/warnings_YYYYMMDD.log`
- `get_audit_logger()` returns `TestAuditLogger` singleton with methods:
  - `log_action(action_type, details, status)` — stamps correlation/trace/request IDs
  - `log_ui_action(action, element, value)` — UI interaction
  - `log_api_call(method, url, status_code, duration_ms, ...)` — API
  - `log_db_operation(operation, table, query, ...)` — Database
  - `log_fixture_event(fixture_name, event, scope, test_name)` — Fixtures
  - `log_validation(validation_type, expected, actual, passed)` — Assertions
  - `log_screenshot(path, reason, test_name)` — Screenshots

### Enhanced BasePage Integration

All BasePage subclasses automatically log:
- Page initialization with `audit("page_load", ...)`
- Screenshot capture with `audit("screenshot_captured", ...)`
- All slow operations with `performance(...)` events

### Enhanced SmartActions Integration

All SmartActions methods automatically log:
- Before: `logger.info()` with locator + description
- After: `audit("element_clicked"/"text_entered"/...)` on success
- On failure: `logger.error()` with `exc_info=True`

### Enhanced Human Behavior Simulator

All behavior simulation logs:
- Typing: `log_element_interaction("type", element, page, value)`
- Clicking: `log_element_interaction("click", element, page)`
- Scrolling: `log_action("scroll", {"direction": dir, "distance": dist})`
- Idle: `log_action("idle", {"duration": duration})`

---

## Validation Checklist

### Code Level
- [ ] All `import logging` → `from framework.observability.enterprise_logger import get_enterprise_logger`
- [ ] All `logger.getLogger()` → `get_enterprise_logger()`
- [ ] Critical functions have `@with_trace` decorator
- [ ] Correlation IDs set at request/test boundaries
- [ ] No silent `except: pass` — all replaced with named `except Exception as exc:`
- [ ] Sensitive data masking works for nested dicts

### Functional Level
- [ ] `logs/enterprise/app_YYYYMMDD.json` created on test run
- [ ] `logs/audit/audit_YYYYMMDD.json` contains per-action entries
- [ ] `logs/security/security_YYYYMMDD.json` for auth events
- [ ] `logs/performance/performance_YYYYMMDD.json` for slow ops
- [ ] JSON format is valid and parseable
- [ ] Correlation IDs are consistent within a test

### Test Execution Validation
```bash
# Run tests and verify logs created
pytest tests/bookslot/ -v

# Check JSON format
python -c "import json; [json.loads(l) for l in open('logs/enterprise/app_$(date +%Y%m%d).json')]"

# Verify correlation IDs present
grep -o '"correlation_id":"[^"]*"' logs/audit/audit_$(date +%Y%m%d).json | head -5

# Check for any remaining silent handlers
grep -rn "except:" framework/ pages/ tests/ | grep -v ".bak"
```

### SIEM Integration (when enabled)
- [ ] Logs appearing in configured SIEM (ELK/Datadog/Splunk/Loki)
- [ ] Circuit breaker functioning on SIEM failures
- [ ] Batch uploads working, no data loss
- [ ] Correlation IDs visible in SIEM queries

---

> **See Also:**
> - [Enterprise-Logging-Architecture.md](Enterprise-Logging-Architecture.md) — System design, components, schema
> - [Enterprise-Logging-Deployment.md](Enterprise-Logging-Deployment.md) — Production deployment checklist

---

**Document Version:** 1.0.0
**Supersedes:** Enterprise-Logging-Integration-Guide.md, Logging-System-Fixes.md, Logging-Enhancements.md
**Last Updated:** February 26, 2026
