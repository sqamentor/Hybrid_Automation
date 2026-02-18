# Enterprise Logging Integration Guide
## Step-by-Step Migration & Integration Plan

**Version:** 1.0.0  
**Status:** Implementation Guide  
**Target:** Complete codebase coverage  

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Integration Priority](#integration-priority)
3. [Step-by-Step Integration](#step-by-step-integration)
4. [File-by-File Integration Examples](#file-by-file-integration-examples)
5. [Common Patterns](#common-patterns)
6. [Testing Integration](#testing-integration)
7. [Validation Checklist](#validation-checklist)

---

## 🎯 Overview

This guide provides **concrete, actionable steps** to integrate the enterprise logging system throughout the entire codebase. Each section includes:

- **Specific files** to modify
- **Exact code changes** required
- **Before/After** examples
- **Validation steps**

### Integration Goals

✅ Replace all standard `logging` with `EnterpriseLogger`  
✅ Add correlation IDs to all request flows  
✅ Integrate `@with_trace` decorators for critical operations  
✅ Ensure 100% log coverage  
✅ Enable audit logging for all user actions  
✅ Add security logging for authentication/authorization  
✅ Implement performance logging for slow operations  

---

## 📊 Integration Priority

### Phase 1: Critical Infrastructure (Week 1)
**Priority: HIGH** ⚡

1. **Root conftest.py** - Enable pytest plugin
2. **Framework core** - Base classes, engines
3. **Smart actions** - All UI interactions
4. **API clients** - Request/response logging

### Phase 2: Page Objects & Tests (Week 2)
**Priority: MEDIUM** 📋

5. **Page objects** - All page interactions
6. **Test files** - Test lifecycle logging
7. **Database operations** - Query logging

### Phase 3: Advanced Components (Week 3)
**Priority: LOW** 📝

8. **Plugin system** - Plugin lifecycle
9. **Microservices** - Service communication
10. **ML/AI components** - Model operations

---

## 🔧 Step-by-Step Integration

### Step 1: Enable Pytest Plugin

**File:** `conftest.py` (root level)

**Add this line:**
```python
# Add enterprise logging plugin
pytest_plugins = [
    'framework.observability.pytest_enterprise_logging',
    # ... existing plugins
]
```

**Validation:**
```bash
pytest --collect-only
# Should see: "plugin: pytest_enterprise_logging"
```

---

### Step 2: Update Framework Core Components

#### 2.1 Smart Actions (`framework/core/smart_actions.py`)

**Current imports:**
```python
import logging
logger = logging.getLogger(__name__)
```

**Replace with:**
```python
from framework.observability.enterprise_logger import (
    get_enterprise_logger,
    with_trace,
    CorrelationContext
)

logger = get_enterprise_logger()
```

**Update methods:**

**BEFORE:**
```python
def click(self, locator: str, timeout: int = 10):
    logger.info(f"Clicking element: {locator}")
    # ... implementation ...
    logger.info(f"✓ Clicked: {locator}")
```

**AFTER:**
```python
@with_trace(operation_name="ui_click")
def click(self, locator: str, timeout: int = 10):
    logger.info("Clicking element", locator=locator, timeout=timeout)
    # ... implementation ...
    logger.audit("element_clicked", {
        "locator": locator,
        "element_type": "button",
        "success": True
    }, status="success")
```

**Full integration for `SmartActions`:**

```python
class SmartActions:
    """Enterprise-logged smart actions for UI automation"""
    
    def __init__(self, driver_or_page, context=None):
        self.driver = driver_or_page
        self.context = context
        self.logger = get_enterprise_logger()
        
        # Set correlation context
        if not CorrelationContext.get_correlation_id():
            CorrelationContext.set_correlation_id(
                CorrelationContext.generate_correlation_id()
            )
        
        self.logger.info("SmartActions initialized", 
                        engine_type=type(driver_or_page).__name__)
    
    @with_trace(operation_name="ui_click")
    def click(self, locator: str, timeout: int = 10) -> bool:
        """Click with enterprise logging"""
        self.logger.info("Attempting click", locator=locator, timeout=timeout)
        
        try:
            # Implementation...
            element = self._find_element(locator, timeout)
            element.click()
            
            self.logger.audit("element_clicked", {
                "locator": locator,
                "element_type": self._get_element_type(element),
                "timestamp": datetime.now().isoformat()
            }, status="success")
            
            self.logger.info("✓ Click successful", locator=locator)
            return True
            
        except Exception as e:
            self.logger.error("Click failed", 
                            locator=locator, 
                            exc_info=True,
                            error_type=type(e).__name__)
            raise
    
    @with_trace(operation_name="ui_type_text")
    def type_text(self, locator: str, text: str, timeout: int = 10) -> bool:
        """Type text with enterprise logging"""
        # Mask sensitive input
        display_text = text if len(text) < 20 else f"{text[:10]}...{text[-5:]}"
        
        self.logger.info("Attempting to type text", 
                        locator=locator, 
                        text_length=len(text))
        
        try:
            element = self._find_element(locator, timeout)
            element.clear()
            element.send_keys(text)
            
            self.logger.audit("text_entered", {
                "locator": locator,
                "field_type": self._get_element_type(element),
                "text_length": len(text)
            }, status="success")
            
            self.logger.info("✓ Text entered successfully", locator=locator)
            return True
            
        except Exception as e:
            self.logger.error("Type text failed", 
                            locator=locator,
                            exc_info=True)
            raise
    
    @with_trace(operation_name="ui_navigate")
    def navigate(self, url: str) -> None:
        """Navigate with enterprise logging"""
        self.logger.info("Navigating to URL", url=url)
        
        start_time = time.time()
        
        try:
            self.driver.get(url)
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.performance("page_navigation", duration_ms, {
                "url": url,
                "load_time_ms": duration_ms
            })
            
            self.logger.audit("navigation", {
                "url": url,
                "timestamp": datetime.now().isoformat()
            }, status="success")
            
            if duration_ms > 5000:
                self.logger.warning("Slow page load detected", 
                                  url=url, 
                                  duration_ms=duration_ms)
            
        except Exception as e:
            self.logger.error("Navigation failed", url=url, exc_info=True)
            self.logger.security("navigation_failure", {
                "url": url,
                "error": str(e),
                "potential_issue": "Network or DNS problem"
            })
            raise
```

---

#### 2.2 Base Page (`framework/ui/base_page.py`)

**Integration:**

```python
from framework.observability.enterprise_logger import (
    get_enterprise_logger,
    with_trace,
    CorrelationContext
)

class BasePage(ABC):
    """Base page with enterprise logging"""
    
    def __init__(self, driver_or_page):
        self.driver = driver_or_page
        self.logger = get_enterprise_logger()
        
        # Ensure correlation context
        if not CorrelationContext.get_correlation_id():
            CorrelationContext.set_correlation_id(
                CorrelationContext.generate_correlation_id()
            )
        
        page_name = self.__class__.__name__
        self.logger.info("Page object initialized", page=page_name)
        self.logger.audit("page_load", {
            "page": page_name,
            "url": self.get_current_url() if hasattr(self, 'get_current_url') else "unknown"
        }, status="initialized")
    
    @with_trace(operation_name="page_wait_for_load")
    def wait_for_page_load(self, timeout: int = 30) -> bool:
        """Wait for page load with logging"""
        page_name = self.__class__.__name__
        self.logger.info("Waiting for page load", page=page_name, timeout=timeout)
        
        start_time = time.time()
        
        try:
            # Wait implementation...
            success = self._wait_implementation(timeout)
            
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.performance("page_load_wait", duration_ms, {
                "page": page_name,
                "timeout": timeout
            })
            
            if duration_ms > 10000:
                self.logger.warning("Slow page load", 
                                  page=page_name, 
                                  duration_ms=duration_ms)
            
            return success
            
        except TimeoutException as e:
            self.logger.error("Page load timeout", 
                            page=page_name, 
                            timeout=timeout,
                            exc_info=True)
            raise
    
    @with_trace(operation_name="page_screenshot")
    def take_screenshot(self, name: str = None) -> str:
        """Take screenshot with logging"""
        screenshot_name = name or f"{self.__class__.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info("Taking screenshot", name=screenshot_name)
        
        try:
            filepath = self._capture_screenshot(screenshot_name)
            
            self.logger.audit("screenshot_captured", {
                "name": screenshot_name,
                "filepath": filepath,
                "page": self.__class__.__name__
            }, status="success")
            
            return filepath
            
        except Exception as e:
            self.logger.error("Screenshot capture failed", 
                            name=screenshot_name,
                            exc_info=True)
            raise
```

---

#### 2.3 Selenium Engine (`framework/ui/selenium_engine.py`)

**Integration:**

```python
from framework.observability.enterprise_logger import (
    get_enterprise_logger,
    with_trace,
    CorrelationContext
)

class SeleniumEngine:
    """Selenium engine with enterprise logging"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.driver = None
        self.logger = get_enterprise_logger()
        
        self.logger.info("SeleniumEngine initializing", 
                        browser=config.get('browser', 'chrome'))
    
    @with_trace(operation_name="selenium_engine_start")
    def start(self) -> WebDriver:
        """Start Selenium driver with logging"""
        browser = self.config.get('browser', 'chrome')
        headless = self.config.get('headless', False)
        
        self.logger.info("Starting Selenium driver", 
                        browser=browser, 
                        headless=headless)
        
        # Generate correlation ID for this session
        session_id = CorrelationContext.generate_correlation_id()
        CorrelationContext.set_correlation_id(session_id)
        
        try:
            start_time = time.time()
            
            # Driver initialization logic...
            self.driver = self._initialize_driver(browser, headless)
            
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.performance("driver_startup", duration_ms, {
                "browser": browser,
                "headless": headless,
                "session_id": session_id
            })
            
            self.logger.audit("engine_started", {
                "engine": "selenium",
                "browser": browser,
                "session_id": session_id,
                "capabilities": self.driver.capabilities
            }, status="success")
            
            self.logger.info("✓ Selenium driver started successfully", 
                           browser=browser,
                           session_id=session_id)
            
            return self.driver
            
        except Exception as e:
            self.logger.error("Failed to start Selenium driver", 
                            browser=browser,
                            exc_info=True)
            self.logger.security("driver_startup_failure", {
                "browser": browser,
                "error": str(e),
                "potential_issue": "Missing driver or browser"
            })
            raise DriverManagerError(f"Failed to start driver: {str(e)}")
    
    @with_trace(operation_name="selenium_engine_stop")
    def stop(self) -> None:
        """Stop Selenium driver with logging"""
        if not self.driver:
            self.logger.warning("Attempted to stop non-existent driver")
            return
        
        session_id = CorrelationContext.get_correlation_id()
        
        self.logger.info("Stopping Selenium driver", session_id=session_id)
        
        try:
            self.driver.quit()
            
            self.logger.audit("engine_stopped", {
                "engine": "selenium",
                "session_id": session_id
            }, status="success")
            
            self.logger.info("✓ Selenium driver stopped", session_id=session_id)
            
        except Exception as e:
            self.logger.error("Error stopping driver", 
                            session_id=session_id,
                            exc_info=True)
        finally:
            self.driver = None
            CorrelationContext.clear_context()
```

---

### Step 3: Update Page Objects

#### 3.1 Example: Bookslot Basic Info Page

**File:** `pages/bookslot/bookslots_basicinfo_page1.py`

**Integration:**

```python
from framework.ui.base_page import BasePage
from framework.observability.enterprise_logger import (
    get_enterprise_logger,
    with_trace
)

class BookslotBasicInfoPage(BasePage):
    """Bookslot basic info page with enterprise logging"""
    
    def __init__(self, driver_or_page):
        super().__init__(driver_or_page)
        self.logger = get_enterprise_logger()
        
        self.logger.info("BookslotBasicInfoPage initialized")
        self.logger.audit("page_visit", {
            "page": "bookslot_basic_info",
            "step": 1,
            "workflow": "appointment_booking"
        }, status="initialized")
    
    @with_trace(operation_name="fill_basic_info")
    def fill_basic_information(self, data: Dict[str, Any]) -> bool:
        """Fill basic info with logging"""
        self.logger.info("Filling basic information", 
                        fields=list(data.keys()))
        
        try:
            # Fill first name
            if 'first_name' in data:
                self.logger.info("Filling first name")
                self.smart_actions.type_text("#firstName", data['first_name'])
            
            # Fill last name
            if 'last_name' in data:
                self.logger.info("Filling last name")
                self.smart_actions.type_text("#lastName", data['last_name'])
            
            # Fill email
            if 'email' in data:
                self.logger.info("Filling email")
                self.smart_actions.type_text("#email", data['email'])
            
            # Fill phone
            if 'phone' in data:
                self.logger.info("Filling phone")
                self.smart_actions.type_text("#phone", data['phone'])
            
            self.logger.audit("form_filled", {
                "form": "basic_info",
                "fields_filled": list(data.keys()),
                "workflow": "appointment_booking"
            }, status="success")
            
            self.logger.info("✓ Basic information filled successfully")
            return True
            
        except Exception as e:
            self.logger.error("Failed to fill basic information", 
                            exc_info=True,
                            fields_attempted=list(data.keys()))
            raise
    
    @with_trace(operation_name="select_date")
    def select_appointment_date(self, date: str) -> bool:
        """Select date with logging"""
        self.logger.info("Selecting appointment date", date=date)
        
        try:
            self.smart_actions.click("#dateSelector")
            self.smart_actions.click(f"[data-date='{date}']")
            
            self.logger.audit("date_selected", {
                "date": date,
                "form": "basic_info"
            }, status="success")
            
            self.logger.info("✓ Date selected", date=date)
            return True
            
        except Exception as e:
            self.logger.error("Failed to select date", 
                            date=date,
                            exc_info=True)
            raise
    
    @with_trace(operation_name="submit_basic_info")
    def submit_form(self) -> bool:
        """Submit form with logging"""
        self.logger.info("Submitting basic info form")
        
        try:
            start_time = time.time()
            
            self.smart_actions.click("#submitButton")
            
            # Wait for navigation
            self.wait_for_page_load()
            
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.performance("form_submission", duration_ms, {
                "form": "basic_info",
                "step": 1
            })
            
            self.logger.audit("form_submitted", {
                "form": "basic_info",
                "next_step": "event_info",
                "duration_ms": duration_ms
            }, status="success")
            
            self.logger.info("✓ Form submitted successfully")
            return True
            
        except Exception as e:
            self.logger.error("Form submission failed", exc_info=True)
            self.logger.security("form_submission_failure", {
                "form": "basic_info",
                "error": str(e)
            })
            raise
```

---

### Step 4: Update Test Files

#### 4.1 Example: Workflow Test

**File:** `tests/workflows/test_cross_engine_workflows.py`

**Integration:**

```python
import pytest
from framework.observability.enterprise_logger import (
    get_enterprise_logger,
    CorrelationContext
)

logger = get_enterprise_logger()

@pytest.mark.workflow
@pytest.mark.critical
def test_sso_to_callcenter_to_patientintake(
    workflow_orchestrator,
    workflow_engines,
    sso_config,
    sso_credentials,
    enterprise_logging_context  # Injected by pytest plugin
):
    """
    Complete workflow test with enterprise logging
    
    The enterprise_logging_context fixture automatically:
    - Sets correlation ID for the entire test
    - Logs test start/end
    - Captures exceptions
    - Logs performance metrics
    """
    
    # Set user context for audit trail
    enterprise_logging_context.set_user({
        "user_id": "test_user_01",
        "role": "tester",
        "test_type": "workflow"
    })
    
    logger.info("Starting SSO workflow test")
    logger.audit("test_started", {
        "test_name": "sso_to_callcenter_to_patientintake",
        "workflow_type": "cross_engine",
        "engines": ["selenium", "playwright"]
    }, status="started")
    
    # Step 1: SSO Authentication
    logger.info("Step 1: SSO Authentication")
    enterprise_logging_context.log_action("sso_login_attempt", {
        "username": sso_credentials['username']
    })
    
    try:
        auth_result = workflow_orchestrator.authenticate_sso(
            sso_config['url'],
            sso_credentials['username'],
            sso_credentials['password']
        )
        
        assert auth_result['success'], "SSO authentication failed"
        
        logger.audit("sso_authentication", {
            "status": "success",
            "session_token": auth_result.get('token', 'N/A')[:10] + "...",
            "user": sso_credentials['username']
        }, status="success")
        
        logger.info("✓ SSO authentication successful")
        
    except Exception as e:
        logger.error("SSO authentication failed", exc_info=True)
        enterprise_logging_context.log_security_event("auth_failure", {
            "username": sso_credentials['username'],
            "error": str(e)
        })
        raise
    
    # Step 2: Navigate to Call Center
    logger.info("Step 2: Navigate to Call Center")
    
    try:
        callcenter_page = workflow_orchestrator.navigate_to_module(
            "callcenter",
            engine="selenium"
        )
        
        assert callcenter_page.is_loaded(), "Call center page not loaded"
        
        logger.audit("module_navigation", {
            "module": "callcenter",
            "engine": "selenium",
            "url": callcenter_page.get_url()
        }, status="success")
        
        logger.info("✓ Call center module loaded")
        
    except Exception as e:
        logger.error("Call center navigation failed", exc_info=True)
        raise
    
    # Step 3: Create Appointment
    logger.info("Step 3: Create appointment")
    
    appointment_data = {
        "patient_name": "John Doe",
        "date": "2024-03-15",
        "time": "14:00",
        "reason": "Consultation"
    }
    
    try:
        appointment_id = callcenter_page.create_appointment(appointment_data)
        
        assert appointment_id, "Appointment creation failed"
        
        logger.audit("appointment_created", {
            "appointment_id": appointment_id,
            "patient": appointment_data['patient_name'],
            "date": appointment_data['date'],
            "module": "callcenter"
        }, status="success")
        
        logger.info("✓ Appointment created", appointment_id=appointment_id)
        
    except Exception as e:
        logger.error("Appointment creation failed", 
                    data=appointment_data,
                    exc_info=True)
        raise
    
    # Step 4: Switch to Patient Intake (Playwright)
    logger.info("Step 4: Switch to Patient Intake module")
    
    try:
        patientintake_page = workflow_orchestrator.navigate_to_module(
            "patientintake",
            engine="playwright"
        )
        
        assert patientintake_page.is_loaded(), "Patient intake page not loaded"
        
        logger.audit("engine_switch", {
            "from_engine": "selenium",
            "to_engine": "playwright",
            "module": "patientintake"
        }, status="success")
        
        logger.info("✓ Switched to Patient Intake (Playwright)")
        
    except Exception as e:
        logger.error("Engine switch failed", exc_info=True)
        raise
    
    # Step 5: Verify Appointment
    logger.info("Step 5: Verify appointment in Patient Intake")
    
    try:
        appointment_found = patientintake_page.find_appointment(appointment_id)
        
        assert appointment_found, f"Appointment {appointment_id} not found"
        
        logger.audit("appointment_verified", {
            "appointment_id": appointment_id,
            "module": "patientintake",
            "verification_success": True
        }, status="success")
        
        logger.info("✓ Appointment verified", appointment_id=appointment_id)
        
    except Exception as e:
        logger.error("Appointment verification failed", 
                    appointment_id=appointment_id,
                    exc_info=True)
        raise
    
    # Test completed
    logger.audit("test_completed", {
        "test_name": "sso_to_callcenter_to_patientintake",
        "result": "PASSED",
        "steps_completed": 5
    }, status="success")
    
    logger.info("✓ Workflow test completed successfully")
```

---

### Step 5: Update API Client

**File:** `framework/api/api_client.py` (if exists)

**Integration:**

```python
import httpx
from framework.observability.enterprise_logger import (
    get_enterprise_logger,
    with_trace,
    CorrelationContext
)

class APIClient:
    """API client with enterprise logging"""
    
    def __init__(self, base_url: str, headers: Dict = None):
        self.base_url = base_url
        self.headers = headers or {}
        self.logger = get_enterprise_logger()
        
        self.logger.info("APIClient initialized", base_url=base_url)
    
    @with_trace(operation_name="api_request")
    async def request(
        self, 
        method: str, 
        endpoint: str, 
        data: Dict = None,
        params: Dict = None
    ) -> Dict:
        """Make API request with logging"""
        
        url = f"{self.base_url}{endpoint}"
        correlation_id = CorrelationContext.get_correlation_id()
        
        # Add correlation ID to headers
        headers = {
            **self.headers,
            'X-Correlation-ID': correlation_id or 'no-correlation-id'
        }
        
        self.logger.info("API request", 
                        method=method, 
                        endpoint=endpoint,
                        correlation_id=correlation_id)
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method,
                    url,
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=30.0
                )
                
                duration_ms = (time.time() - start_time) * 1000
                
                # Log response
                self.logger.info("API response received", 
                               method=method,
                               endpoint=endpoint,
                               status_code=response.status_code,
                               duration_ms=duration_ms)
                
                # Performance logging
                self.logger.performance("api_call", duration_ms, {
                    "method": method,
                    "endpoint": endpoint,
                    "status_code": response.status_code
                })
                
                # Audit logging
                self.logger.audit("api_request_completed", {
                    "method": method,
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "correlation_id": correlation_id
                }, status="success" if response.status_code < 400 else "failed")
                
                # Check for errors
                if response.status_code >= 400:
                    self.logger.error("API request failed", 
                                    method=method,
                                    endpoint=endpoint,
                                    status_code=response.status_code,
                                    response_text=response.text[:200])
                    
                    if response.status_code in [401, 403]:
                        self.logger.security("api_auth_failure", {
                            "endpoint": endpoint,
                            "status_code": response.status_code
                        })
                
                # Slow API warning
                if duration_ms > 2000:
                    self.logger.warning("Slow API call detected", 
                                      endpoint=endpoint,
                                      duration_ms=duration_ms)
                
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException as e:
            self.logger.error("API request timeout", 
                            method=method,
                            endpoint=endpoint,
                            timeout=30.0,
                            exc_info=True)
            self.logger.security("api_timeout", {
                "endpoint": endpoint,
                "potential_issue": "Network or service degradation"
            })
            raise
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            self.logger.error("API request failed", 
                            method=method,
                            endpoint=endpoint,
                            exc_info=True,
                            duration_ms=duration_ms)
            raise
```

---

## 🔄 Common Patterns

### Pattern 1: Function with Trace Decorator

```python
@with_trace(operation_name="descriptive_operation_name")
def my_function(param1: str, param2: int) -> bool:
    """Function automatically traced"""
    logger = get_enterprise_logger()
    logger.info("Doing something", param1=param1, param2=param2)
    
    # ... implementation ...
    
    logger.info("✓ Operation successful")
    return True
```

### Pattern 2: Class Initialization with Context

```python
class MyClass:
    def __init__(self):
        self.logger = get_enterprise_logger()
        
        # Set correlation ID if not exists
        if not CorrelationContext.get_correlation_id():
            CorrelationContext.set_correlation_id(
                CorrelationContext.generate_correlation_id()
            )
        
        self.logger.info("MyClass initialized")
```

### Pattern 3: Audit Logging for User Actions

```python
def user_action(user_id: str, action: str):
    logger = get_enterprise_logger()
    
    logger.audit("user_action_performed", {
        "user_id": user_id,
        "action": action,
        "timestamp": datetime.now().isoformat(),
        "ip_address": request.client.host  # if web app
    }, status="success")
```

### Pattern 4: Security Logging

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

### Pattern 5: Performance Logging

```python
def slow_operation():
    logger = get_enterprise_logger()
    
    start_time = time.time()
    
    # ... operation ...
    
    duration_ms = (time.time() - start_time) * 1000
    
    logger.performance("operation_name", duration_ms, {
        "additional": "context"
    })
    
    if duration_ms > 2000:
        logger.warning("Slow operation", duration_ms=duration_ms)
```

---

## ✅ Validation Checklist

After integration, verify:

### Code Level
- [ ] All `import logging` replaced with enterprise logger
- [ ] All `logger.getLogger()` replaced with `get_enterprise_logger()`
- [ ] Critical functions have `@with_trace` decorator
- [ ] Correlation IDs set at request boundaries
- [ ] Sensitive data is automatically masked

### Functional Level
- [ ] Logs appear in `logs/enterprise/app.log`
- [ ] JSON format is correct and parsable
- [ ] Correlation IDs are consistent within a request
- [ ] Audit logs present in `logs/enterprise/audit.log`
- [ ] Security events in `logs/enterprise/security.log`
- [ ] Performance metrics in `logs/enterprise/performance.log`

### Test Execution
```bash
# Run tests and check logs
pytest tests/ -v

# Verify log files created
ls -lh logs/enterprise/

# Check JSON format
jq '.' logs/enterprise/app.log | head -20

# Search for correlation IDs
grep -o '"correlation_id":"[^"]*"' logs/enterprise/app.log | sort | uniq

# Check audit trail
jq 'select(.logger == "enterprise.audit")' logs/enterprise/audit.log
```

### SIEM Integration (if enabled)
- [ ] Logs appearing in Elasticsearch/Datadog/Splunk
- [ ] Circuit breaker functioning on SIEM failures
- [ ] Batch uploads working correctly
- [ ] No data loss during SIEM downtime

---

## 🎯 Quick Reference

### Import Statement
```python
from framework.observability.enterprise_logger import (
    get_enterprise_logger,
    with_trace,
    with_async_trace,
    CorrelationContext
)
```

### Basic Usage
```python
logger = get_enterprise_logger()
logger.info("Message", key="value")
logger.error("Error", exc_info=True)
logger.audit("event", {"data": "..."}, status="success")
logger.security("security_event", {"details": "..."})
logger.performance("operation", 123.45, {"context": "..."})
```

### Decorators
```python
@with_trace(operation_name="my_operation")
def my_function():
    pass

@with_async_trace(operation_name="async_operation")
async def my_async_function():
    pass
```

### Correlation Context
```python
# Set correlation ID
CorrelationContext.set_correlation_id(CorrelationContext.generate_correlation_id())

# Set user context
CorrelationContext.set_user_context({"user_id": "123", "role": "admin"})

# Get correlation ID
corr_id = CorrelationContext.get_correlation_id()

# Clear context
CorrelationContext.clear_context()
```

---

**Next Steps:**
1. Review this guide thoroughly
2. Start with Phase 1 (Critical Infrastructure)
3. Test each integration before moving to next file
4. Validate logs are appearing correctly
5. Proceed to Phase 2 and Phase 3

**For Support:** Refer to [ENTERPRISE_LOGGING_ARCHITECTURE.md](ENTERPRISE_LOGGING_ARCHITECTURE.md)

---

**Document Version:** 1.0.0  
**Last Updated:** February 18, 2026  
**Status:** ✅ Ready for Implementation
