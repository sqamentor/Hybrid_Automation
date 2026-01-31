# 🎯 PYTEST MARKERS - COMPLETE COMPREHENSIVE GUIDE

**Enterprise-Grade Hybrid Automation Framework**

---

**Author**: Lokendra Singh  
**Email**: qa.lokendra@gmail.com  
**Website**: www.sqamentor.com  
**Framework Version**: 2.0  
**Last Updated**: January 27, 2026

---

## 📚 TABLE OF CONTENTS

1. [Introduction to Pytest Markers](#1-introduction-to-pytest-markers)
2. [Why Use Markers?](#2-why-use-markers)
3. [Built-in Pytest Markers](#3-built-in-pytest-markers)
4. [Framework Custom Markers](#4-framework-custom-markers)
5. [Using Markers in Tests](#5-using-markers-in-tests)
6. [Running Tests with Markers](#6-running-tests-with-markers)
7. [Advanced Marker Combinations](#7-advanced-marker-combinations)
8. [Real-World Examples](#8-real-world-examples)
9. [Best Practices](#9-best-practices)
10. [Marker Registration](#10-marker-registration)
11. [CI/CD Integration](#11-cicd-integration)
12. [Troubleshooting](#12-troubleshooting)
13. [Quick Reference](#13-quick-reference)

---

## 1. INTRODUCTION TO PYTEST MARKERS

### What Are Pytest Markers?

Pytest markers are **decorators** that add metadata to test functions, allowing you to:

- ✅ **Tag/Label tests** with meaningful categories
- ✅ **Selectively run** subsets of tests
- ✅ **Skip tests** conditionally based on criteria
- ✅ **Parametrize tests** for data-driven testing
- ✅ **Control test execution** behavior

### Basic Syntax

```python
import pytest

# Single marker
@pytest.mark.smoke
def test_login():
    pass

# Marker with parameter
@pytest.mark.module("checkout")
def test_checkout_flow():
    pass

# Multiple markers
@pytest.mark.smoke
@pytest.mark.critical
@pytest.mark.bookslot
def test_important_feature():
    pass
```

### Marker Anatomy

```python
@pytest.mark.marker_name(parameter="value")
│         │     │         │
│         │     │         └─ Optional parameter
│         │     └─ Marker name (must be registered)
│         └─ Pytest mark namespace
└─ Decorator symbol
```

---

## 2. WHY USE MARKERS?

### 🎯 Selective Test Execution

Run specific subsets of tests without running the entire suite:

```bash
# Run only smoke tests (fast feedback)
pytest -m smoke

# Run only critical tests (pre-deployment)
pytest -m critical

# Run BookSlot project tests only
pytest -m bookslot
```

**Benefits**:
- ⚡ **Faster feedback loops** in development
- 🎯 **Targeted testing** for specific features
- 💰 **Resource optimization** (time, compute)

### 📊 Test Organization

Group tests logically by:

- **Priority**: critical, high, medium, low
- **Category**: smoke, regression, integration
- **Layer**: ui_only, api_only, db_only
- **Project**: bookslot, patientintake, callcenter
- **Module**: checkout, admin, dashboard

**Benefits**:
- 📁 **Clear test structure** and organization
- 🔍 **Easy test discovery** and navigation
- 📈 **Better reporting** and analytics

### 🌍 Environment Control

Control where tests run:

```python
@pytest.mark.dev_only
def test_debug_feature():
    """Run only in development"""
    pass

@pytest.mark.prod_safe
def test_read_only_check():
    """Safe to run in production"""
    pass

@pytest.mark.staging_only
def test_integration_with_staging_api():
    """Run only in staging"""
    pass
```

**Benefits**:
- 🛡️ **Prevents data corruption** in production
- 🔒 **Environment isolation** and safety
- 🎚️ **Environment-specific testing** strategies

### 🚀 CI/CD Optimization

Create efficient CI/CD pipelines:

```yaml
# Fast pipeline (5-10 minutes)
pytest -m "smoke and critical and not flaky"

# Nightly build (1-2 hours)
pytest -m "regression and not wip"

# Full suite (2-3 hours)
pytest
```

**Benefits**:
- ⚡ **Fast CI/CD feedback** (< 10 minutes)
- 🔄 **Parallel execution** strategies
- 📊 **Staged testing** (smoke → regression → full)

### 📈 Reporting & Analytics

Track test execution patterns:

- **Failure analysis** by priority/category
- **Coverage metrics** by project/module
- **Performance trends** by test type
- **Flaky test identification** and tracking

---

## 3. BUILT-IN PYTEST MARKERS

### 3.1 `@pytest.mark.skip` - Unconditional Skip

Skip a test entirely with a reason.

**Syntax**:
```python
@pytest.mark.skip(reason="Reason for skipping")
def test_feature():
    pass
```

**When to Use**:
- Feature not yet implemented
- Test blocked by external dependency
- Test temporarily disabled for investigation

**Examples**:

```python
import pytest

# Example 1: Feature not implemented
@pytest.mark.skip(reason="Feature planned for v2.1")
def test_future_feature():
    """This test will be skipped"""
    pass

# Example 2: Waiting for API deployment
@pytest.mark.skip(reason="API endpoint /v2/users not yet deployed")
def test_new_api_endpoint():
    """Skip until backend team deploys endpoint"""
    pass

# Example 3: Known blocker
@pytest.mark.skip(reason="Blocked by bug #1234 - database migration issue")
def test_database_migration():
    """Skip until bug is fixed"""
    pass
```

**Best Practice**: ⚠️ Use sparingly! `skip` should be **temporary**. Create a ticket and track the issue.

---

### 3.2 `@pytest.mark.skipif` - Conditional Skip

Skip tests based on conditions.

**Syntax**:
```python
@pytest.mark.skipif(condition, reason="Why it's skipped")
def test_feature():
    pass
```

**When to Use**:
- Platform-specific tests (Windows/Linux/Mac)
- Python version requirements
- Environment-dependent tests
- Missing dependencies

**Examples**:

```python
import sys
import os
import pytest

# Example 1: Python version check
@pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="Requires Python 3.11 or higher"
)
def test_python_311_feature():
    """Uses Python 3.11+ features"""
    pass

# Example 2: Platform-specific
@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Unix-only test"
)
def test_unix_file_permissions():
    """Test Unix file permissions"""
    pass

# Example 3: Environment variable check
@pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Requires manual interaction - not suitable for CI"
)
def test_manual_approval_flow():
    """Interactive test requiring user input"""
    pass

# Example 4: AI provider check (Framework-specific)
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY") and not os.getenv("CLAUDE_API_KEY"),
    reason="AI provider API keys not configured"
)
def test_ai_validation_suggestions():
    """Requires at least one AI provider API key"""
    from framework.intelligence import AIValidationSuggester
    suggester = AIValidationSuggester()
    suggestions = suggester.suggest_validations("login_form")
    assert len(suggestions) > 0

# Example 5: Database availability
@pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="Database connection not configured"
)
def test_database_operations():
    """Requires database connection"""
    pass

# Example 6: Production safety
@pytest.mark.skipif(
    os.getenv("ENV") == "production",
    reason="Test modifies data - unsafe for production"
)
def test_data_deletion():
    """Dangerous operation - skip in production"""
    pass
```

**Advanced Example - Multiple Conditions**:

```python
# Skip if ANY condition is true
@pytest.mark.skipif(
    sys.platform == "win32" or sys.version_info < (3, 10),
    reason="Requires Unix platform and Python 3.10+"
)
def test_advanced_unix_feature():
    pass

# Skip if ALL conditions are true (use separate decorators)
@pytest.mark.skipif(os.getenv("ENV") != "dev", reason="Dev only")
@pytest.mark.skipif(not os.getenv("DEBUG"), reason="Debug mode required")
def test_debug_feature():
    pass
```

---

### 3.3 `@pytest.mark.xfail` - Expected Failure

Mark tests that are expected to fail.

**Syntax**:
```python
@pytest.mark.xfail(reason="Why it's expected to fail")
def test_feature():
    pass
```

**When to Use**:
- Known bugs being tracked
- Platform-specific failures
- Feature behavior changes pending
- Temporary workarounds

**Examples**:

```python
import sys
import pytest

# Example 1: Known bug
@pytest.mark.xfail(reason="Known bug #4567 - Login timeout on slow networks")
def test_login_performance():
    """Test may fail due to known performance issue"""
    # Test that fails intermittently due to bug
    pass

# Example 2: Platform-specific issue
@pytest.mark.xfail(
    sys.platform == "win32",
    reason="Windows SSL certificate issue - bug #8901"
)
def test_ssl_connection():
    """Expected to fail on Windows until SSL fix"""
    pass

# Example 3: Strict xfail (fail if test passes)
@pytest.mark.xfail(
    strict=True,
    reason="Should fail until feature is implemented"
)
def test_unimplemented_feature():
    """If this passes, the feature is ready - remove xfail"""
    # When this test starts passing, remove the marker
    assert False  # Expected to fail

# Example 4: Expected exception
@pytest.mark.xfail(raises=ValueError, reason="Known ValueError in edge case")
def test_edge_case_handling():
    """Expected to raise ValueError"""
    raise ValueError("Edge case not handled")

# Example 5: Run=False (don't even execute)
@pytest.mark.xfail(run=False, reason="Test crashes interpreter")
def test_interpreter_crash():
    """Don't run - causes interpreter crash"""
    pass

# Example 6: Framework-specific - Browser compatibility
@pytest.mark.xfail(
    reason="Shadow DOM issue in Firefox - tracking bug #2345"
)
def test_shadow_dom_interaction():
    """Known to fail in Firefox"""
    pass
```

**xfail vs skip**:

| Scenario | Use |
|----------|-----|
| Feature not implemented | `skip` |
| Known bug, want to track it | `xfail` |
| Temporary block | `skip` |
| Platform-specific failure | `xfail` |
| Test should never run | `skip(run=False)` |

---

### 3.4 `@pytest.mark.parametrize` - Data-Driven Testing

Run the same test with different data.

**Syntax**:
```python
@pytest.mark.parametrize("arg1,arg2", [(val1, val2), (val3, val4)])
def test_feature(arg1, arg2):
    pass
```

**When to Use**:
- Testing multiple input combinations
- Cross-browser testing
- Multi-environment testing
- Boundary value testing

**Examples**:

```python
import pytest

# Example 1: Single parameter
@pytest.mark.parametrize("number", [1, 2, 3, 4, 5])
def test_positive_numbers(number):
    """Test runs 5 times with different numbers"""
    assert number > 0

# Example 2: Multiple parameters
@pytest.mark.parametrize("username,password,expected_result", [
    ("admin", "admin123", "success"),
    ("user1", "wrongpass", "failure"),
    ("", "password", "failure"),
    ("user", "", "failure"),
])
def test_login_combinations(username, password, expected_result):
    """Test different login scenarios"""
    # Your login test logic
    pass

# Example 3: Framework-specific - Multi-project testing
@pytest.mark.parametrize("project", ["bookslot", "patientintake", "callcenter"])
def test_homepage_loads_all_projects(ui_driver, project):
    """Test homepage for all 3 projects"""
    from config.settings import get_ui_url
    
    url = get_ui_url(project)
    ui_driver.navigate(url)
    
    assert ui_driver.get_title() is not None
    assert ui_driver.is_visible("body")

# Example 4: Cross-browser testing
@pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
def test_cross_browser_compatibility(browser):
    """Test across different browsers"""
    # Browser-specific test logic
    pass

# Example 5: Environment testing
@pytest.mark.parametrize("env", ["dev", "staging", "qa"])
def test_api_endpoints_all_environments(env):
    """Test API in different environments"""
    from config.settings import get_api_url
    url = get_api_url("bookslot", env)
    # Test API
    pass

# Example 6: API status code validation
@pytest.mark.parametrize("endpoint,method,expected_status", [
    ("/api/users", "GET", 200),
    ("/api/users/1", "GET", 200),
    ("/api/users", "POST", 201),
    ("/api/users/999", "GET", 404),
    ("/api/users/1", "DELETE", 204),
])
def test_api_endpoints(api_client, endpoint, method, expected_status):
    """Test multiple API endpoints"""
    response = api_client.request(method, endpoint)
    assert response.status_code == expected_status

# Example 7: Boundary value testing
@pytest.mark.parametrize("age,valid", [
    (-1, False),   # Invalid: negative
    (0, True),     # Valid: minimum
    (17, True),    # Valid: below adult
    (18, True),    # Valid: adult threshold
    (120, True),   # Valid: maximum realistic
    (121, False),  # Invalid: too old
])
def test_age_validation(age, valid):
    """Test age boundary values"""
    result = validate_age(age)
    assert result == valid

# Example 8: Combining with markers
@pytest.mark.smoke
@pytest.mark.parametrize("project", ["bookslot", "patientintake", "callcenter"])
def test_smoke_all_projects(project):
    """Smoke test for all projects"""
    pass

# Example 9: IDs for better test names
@pytest.mark.parametrize("username,password", [
    ("admin", "admin123"),
    ("user", "user123"),
], ids=["admin_login", "regular_user_login"])
def test_login_different_users(username, password):
    """Test names will be: test_login_different_users[admin_login] etc."""
    pass

# Example 10: Nested parametrize
@pytest.mark.parametrize("browser", ["chrome", "firefox"])
@pytest.mark.parametrize("resolution", ["1920x1080", "1366x768", "375x667"])
def test_responsive_design(browser, resolution):
    """Creates 6 tests: 2 browsers × 3 resolutions"""
    pass
```

**Advanced - Indirect Parametrization**:

```python
@pytest.mark.parametrize("project", ["bookslot", "patientintake"], indirect=True)
def test_with_fixture(project):
    """Uses fixture instead of direct value"""
    pass

# In conftest.py
@pytest.fixture
def project(request):
    project_name = request.param
    # Setup for project
    yield project_name
    # Teardown
```

---

### 3.5 `@pytest.mark.usefixtures` - Apply Fixtures

Apply fixtures without using them directly.

**Syntax**:
```python
@pytest.mark.usefixtures("fixture1", "fixture2")
def test_feature():
    pass
```

**When to Use**:
- Setup/teardown needed but fixture value not used
- Apply fixtures to entire test class
- Ensure prerequisites are met

**Examples**:

```python
import pytest

# Example 1: Single fixture
@pytest.mark.usefixtures("setup_database")
def test_database_query():
    """setup_database runs before this test"""
    # Database is already set up
    # No need to use the fixture value
    pass

# Example 2: Multiple fixtures
@pytest.mark.usefixtures("setup_browser", "login_user", "setup_test_data")
def test_authenticated_flow():
    """All 3 fixtures run in order"""
    # Browser is launched, user is logged in, test data exists
    pass

# Example 3: Apply to entire class
@pytest.mark.usefixtures("api_client", "database")
class TestAPIEndpoints:
    """All tests in this class use api_client and database fixtures"""
    
    def test_create_user(self):
        # api_client fixture has run
        pass
    
    def test_get_users(self):
        # api_client fixture has run
        pass
    
    def test_update_user(self):
        # api_client fixture has run
        pass

# Example 4: Framework-specific - UI setup
@pytest.mark.usefixtures("ui_driver")
class TestBookSlotFeatures:
    """All tests use ui_driver fixture"""
    
    def test_navigation(self):
        pass
    
    def test_form_submission(self):
        pass

# Example 5: Combining with parametrize
@pytest.mark.usefixtures("setup_test_environment")
@pytest.mark.parametrize("project", ["bookslot", "patientintake"])
def test_projects(project):
    """Environment setup + parametrization"""
    pass
```

**usefixtures vs Direct Fixture**:

```python
# Method 1: usefixtures (fixture value not needed)
@pytest.mark.usefixtures("setup_db")
def test_query():
    # Can't access setup_db value
    pass

# Method 2: Direct fixture (need fixture value)
def test_query(setup_db):
    # Can access setup_db value
    connection = setup_db
    pass
```

---

### 3.6 `@pytest.mark.timeout` - Test Timeout

Set maximum execution time for tests.

**Syntax**:
```python
@pytest.mark.timeout(seconds)
def test_feature():
    pass
```

**When to Use**:
- Prevent hanging tests
- Performance testing
- Long-running operations
- Integration tests

**Examples**:

```python
import pytest

# Example 1: Basic timeout (60 seconds)
@pytest.mark.timeout(60)
def test_api_response():
    """Fail if test takes more than 60 seconds"""
    pass

# Example 2: Long-running test (5 minutes)
@pytest.mark.timeout(300)
def test_data_migration():
    """Large data migration - allow 5 minutes"""
    pass

# Example 3: Performance test (2 seconds)
@pytest.mark.timeout(2)
def test_fast_operation():
    """Ensure operation completes in 2 seconds"""
    pass

# Example 4: Framework-specific - Performance testing
@pytest.mark.performance
@pytest.mark.timeout(300)
@pytest.mark.slow
def test_bookslot_load_performance():
    """Performance test with 5-minute timeout"""
    pass

# Example 5: Security scan (10 minutes)
@pytest.mark.security
@pytest.mark.timeout(600)
def test_security_vulnerability_scan():
    """OWASP ZAP scan - allow 10 minutes"""
    pass

# Example 6: Different timeout methods
@pytest.mark.timeout(60, method='thread')  # Default
def test_with_thread_timeout():
    """Uses thread-based timeout"""
    pass

@pytest.mark.timeout(60, method='signal')  # Unix only
def test_with_signal_timeout():
    """Uses signal-based timeout (more reliable but Unix only)"""
    pass
```

**Default Timeout** (set in pytest.ini):
```ini
[pytest]
timeout = 300  # Default 5 minutes for all tests
timeout_method = thread
```

---

## 4. FRAMEWORK CUSTOM MARKERS

This framework has **40+ custom markers** registered in `pytest.ini`. They are organized into categories.

### 4.1 Engine Selection Markers

Help the AI engine selector choose the optimal automation engine (Playwright vs Selenium).

#### `@pytest.mark.modern_spa`

**Purpose**: Mark tests for modern single-page applications  
**Engine Preference**: Playwright  
**Use Cases**:
- React, Vue, Angular applications
- Shadow DOM elements
- WebSocket communication
- Complex animations
- Dynamic content loading

**Example**:
```python
@pytest.mark.modern_spa
@pytest.mark.bookslot
def test_react_dashboard():
    """
    BookSlot uses React with:
    - Shadow DOM components
    - Real-time WebSocket updates
    - Complex animations
    
    → AI selector will prefer Playwright
    """
    pass
```

#### `@pytest.mark.legacy_ui`

**Purpose**: Mark tests for legacy applications  
**Engine Preference**: Selenium  
**Use Cases**:
- JSP, ASP.NET applications
- Server-side rendering
- Traditional page reloads
- Older JavaScript frameworks

**Example**:
```python
@pytest.mark.legacy_ui
@pytest.mark.ui_framework("JSP")
def test_jsp_admin_panel():
    """
    Legacy JSP application with:
    - Server-side rendering
    - Traditional form submissions
    - Page reloads
    
    → AI selector will prefer Selenium
    """
    pass
```

#### `@pytest.mark.mobile`

**Purpose**: Mark mobile-responsive tests  
**Engine Preference**: Playwright (better mobile emulation)  
**Use Cases**:
- Mobile device emulation
- Touch gestures (tap, swipe, pinch)
- Responsive design testing
- Mobile-specific features

**Example**:
```python
@pytest.mark.mobile
@pytest.mark.bookslot
def test_mobile_booking_flow():
    """
    Test on mobile devices:
    - iPhone 14 Pro emulation
    - Touch gestures
    - Mobile navigation
    """
    from framework.mobile import MobileTester
    
    mobile_tester = MobileTester(ui_driver)
    mobile_tester.emulate_device("iPhone 14 Pro")
    mobile_tester.tap("button#book-now")
    mobile_tester.swipe_left("div#carousel")
```

#### `@pytest.mark.api_validation`

**Purpose**: Tests requiring API validation  
**Engine Preference**: Playwright (better network interception)  
**Use Cases**:
- Request/response interception
- API mocking
- Network monitoring
- WebSocket tracking

**Example**:
```python
@pytest.mark.api_validation
@pytest.mark.integration
def test_ui_with_api_checks():
    """
    UI test with API validation:
    - Intercept API calls
    - Validate request/response
    - Mock API responses
    """
    pass
```

---

### 4.2 Project Markers

Mark tests for specific healthcare projects in this framework.

#### `@pytest.mark.bookslot`

**Purpose**: BookSlot project tests  
**Project URL**: https://bookslot.{env}.example.com  
**Features**: Appointment booking, scheduling, calendar

**Example**:
```python
@pytest.mark.bookslot
@pytest.mark.integration
def test_appointment_booking():
    """Test BookSlot appointment booking flow"""
    pass
```

#### `@pytest.mark.patientintake`

**Purpose**: PatientIntake project tests  
**Project URL**: https://patientintake.{env}.example.com  
**Features**: Patient registration, intake forms, medical history

**Example**:
```python
@pytest.mark.patientintake
@pytest.mark.regression
def test_patient_registration():
    """Test PatientIntake registration flow"""
    pass
```

#### `@pytest.mark.callcenter`

**Purpose**: CallCenter project tests  
**Project URL**: https://callcenter.{env}.example.com  
**Features**: Call routing, agent dashboard, call recording

**Example**:
```python
@pytest.mark.callcenter
@pytest.mark.ui_only
def test_agent_dashboard():
    """Test CallCenter agent dashboard"""
    pass
```

#### `@pytest.mark.multi_project`

**Purpose**: Tests spanning multiple projects  
**Use Cases**: End-to-end flows across projects

**Example**:
```python
@pytest.mark.bookslot
@pytest.mark.patientintake
@pytest.mark.multi_project
@pytest.mark.integration
@pytest.mark.critical
def test_bookslot_to_patientintake_flow():
    """
    Complete flow:
    1. Book appointment in BookSlot
    2. Complete intake in PatientIntake
    3. Verify data linkage
    """
    pass
```

---

### 4.3 Module Markers

Specify application modules within projects.

#### `@pytest.mark.module(name)`

**Purpose**: Tag tests by application module  
**Parameter**: Module name (string)  
**Common Modules**:
- `"checkout"` - E-commerce checkout
- `"admin"` - Admin panel
- `"dashboard"` - User dashboard
- `"authentication"` - Login/logout
- `"profile"` - User profile
- `"settings"` - Application settings

**Examples**:
```python
@pytest.mark.module("checkout")
def test_checkout_process():
    """Tests for checkout module"""
    pass

@pytest.mark.module("admin")
@pytest.mark.auth_type("SSO")
def test_admin_user_management():
    """Admin module with SSO"""
    pass

@pytest.mark.module("dashboard")
@pytest.mark.modern_spa
def test_dashboard_widgets():
    """Dashboard with modern UI"""
    pass
```

---

### 4.4 UI Framework Markers

Specify the UI technology stack.

#### `@pytest.mark.ui_framework(name)`

**Purpose**: Tag tests by UI framework  
**Parameter**: Framework name (string)  
**Supported Frameworks**:
- `"React"` - React.js
- `"Vue"` - Vue.js
- `"Angular"` - Angular
- `"JSP"` - JavaServer Pages
- `"ASP.NET"` - ASP.NET MVC
- `"Django"` - Django templates

**Examples**:
```python
@pytest.mark.ui_framework("React")
@pytest.mark.modern_spa
def test_react_component():
    """React application test"""
    pass

@pytest.mark.ui_framework("JSP")
@pytest.mark.legacy_ui
def test_jsp_form():
    """Legacy JSP application"""
    pass

@pytest.mark.ui_framework("Angular")
def test_angular_routing():
    """Angular routing test"""
    pass
```

---

### 4.5 Authentication Type Markers

Specify authentication mechanisms.

#### `@pytest.mark.auth_type(type)`

**Purpose**: Tag tests by authentication type  
**Parameter**: Auth type (string)  
**Supported Types**:
- `"SSO"` - Single Sign-On
- `"MFA"` - Multi-Factor Authentication
- `"OAuth"` - OAuth 2.0
- `"Basic"` - Username/password
- `"SAML"` - SAML authentication
- `"JWT"` - JWT token-based

**Examples**:
```python
@pytest.mark.auth_type("SSO")
@pytest.mark.callcenter
def test_sso_login():
    """Test SSO login flow"""
    pass

@pytest.mark.auth_type("MFA")
@pytest.mark.critical
def test_two_factor_authentication():
    """Test 2FA flow"""
    pass

@pytest.mark.auth_type("OAuth")
def test_oauth_integration():
    """Test OAuth login"""
    pass
```

---

### 4.6 Test Category Markers

Classify tests by category.

#### `@pytest.mark.smoke`

**Purpose**: Quick validation tests  
**Execution Time**: < 5 seconds per test  
**Use Cases**:
- Pre-deployment checks
- Critical path validation
- Fast feedback loops

**Example**:
```python
@pytest.mark.smoke
@pytest.mark.critical
def test_homepage_loads():
    """Quick check: homepage loads"""
    assert ui_driver.navigate("https://example.com")
    assert ui_driver.is_visible("body")
```

**When to Run**:
```bash
# Before every deployment
pytest -m smoke

# In CI/CD for fast feedback
pytest -m "smoke and not flaky"
```

#### `@pytest.mark.regression`

**Purpose**: Comprehensive feature validation  
**Execution Time**: Variable (can be slow)  
**Use Cases**:
- Detailed feature testing
- After code changes
- Nightly builds

**Example**:
```python
@pytest.mark.regression
@pytest.mark.bookslot
def test_complete_booking_flow():
    """
    Comprehensive booking test:
    - Navigation
    - Form filling
    - Validation
    - Submission
    - Confirmation
    """
    pass
```

**When to Run**:
```bash
# Nightly builds
pytest -m regression

# After major changes
pytest -m "regression and bookslot"
```

#### `@pytest.mark.integration`

**Purpose**: Tests all layers (UI + API + DB)  
**Complexity**: High  
**Use Cases**:
- End-to-end flows
- Multi-layer validation
- Data persistence checks

**Example**:
```python
@pytest.mark.integration
@pytest.mark.bookslot
@pytest.mark.critical
def test_order_creation_full_flow(ui_driver, api_client, db_client):
    """
    Integration test:
    1. UI: User places order
    2. API: Verify order creation endpoint
    3. DB: Verify order in database
    """
    # UI interaction
    ui_driver.click("button#place-order")
    order_id = ui_driver.get_text("span#order-id")
    
    # API validation
    response = api_client.get(f"/api/orders/{order_id}")
    assert response.status_code == 200
    
    # Database validation
    order = db_client.query("SELECT * FROM orders WHERE id = ?", [order_id])
    assert order is not None
    assert order['status'] == 'pending'
```

#### `@pytest.mark.ui_only`

**Purpose**: UI behavior tests only  
**No API/DB**: No backend validation  

**Example**:
```python
@pytest.mark.ui_only
def test_button_visibility():
    """Test only UI state"""
    assert ui_driver.is_visible("button#submit")
```

#### `@pytest.mark.api_only`

**Purpose**: API endpoint tests only  
**No UI**: No browser interaction  

**Example**:
```python
@pytest.mark.api_only
def test_api_response_structure(api_client):
    """Test API response format"""
    response = api_client.get("/api/users")
    assert "data" in response.json()
```

#### `@pytest.mark.db_only`

**Purpose**: Database tests only  
**No UI/API**: Direct database validation  

**Example**:
```python
@pytest.mark.db_only
def test_database_schema(db_client):
    """Test database structure"""
    tables = db_client.get_tables()
    assert "users" in tables
```

---

### 4.7 Priority Markers

Classify tests by priority.

#### `@pytest.mark.critical`

**Purpose**: Must-pass tests  
**Failure Impact**: Blocks deployment  
**Use Cases**:
- Revenue-affecting features
- Security-critical functionality
- Core user journeys

**Example**:
```python
@pytest.mark.critical
@pytest.mark.smoke
def test_payment_processing():
    """Critical: Payment must work"""
    pass
```

#### `@pytest.mark.high`

**Purpose**: Important features  
**Failure Impact**: High priority fix  

**Example**:
```python
@pytest.mark.high
def test_user_authentication():
    """High priority feature"""
    pass
```

#### `@pytest.mark.medium`

**Purpose**: Standard features  
**Failure Impact**: Normal priority fix  

**Example**:
```python
@pytest.mark.medium
def test_profile_update():
    """Standard feature"""
    pass
```

#### `@pytest.mark.low`

**Purpose**: Nice-to-have features  
**Failure Impact**: Low priority fix  

**Example**:
```python
@pytest.mark.low
def test_tooltip_text():
    """Low priority UI detail"""
    pass
```

---

### 4.8 Environment Markers

Control test execution by environment.

#### `@pytest.mark.dev_only`

**Purpose**: Development environment only  
**Use Cases**:
- Debug features
- Developer tools
- Experimental features

**Example**:
```python
@pytest.mark.dev_only
def test_debug_panel():
    """Only runs in dev environment"""
    pass
```

#### `@pytest.mark.staging_only`

**Purpose**: Staging environment only  
**Use Cases**:
- Pre-production validation
- Integration testing
- Performance testing

**Example**:
```python
@pytest.mark.staging_only
@pytest.mark.performance
def test_load_performance():
    """Load test in staging"""
    pass
```

#### `@pytest.mark.prod_safe`

**Purpose**: Safe for production  
**Requirements**:
- Read-only operations
- No data modification
- No side effects

**Example**:
```python
@pytest.mark.prod_safe
@pytest.mark.smoke
def test_api_health_check():
    """Safe to run in production"""
    response = api_client.get("/health")
    assert response.status_code == 200
```

---

### 4.9 Special Markers

Control test execution behavior.

#### `@pytest.mark.slow`

**Purpose**: Long-running tests (> 30 seconds)  
**Use Cases**:
- Performance tests
- Load tests
- Large data processing

**Example**:
```python
@pytest.mark.slow
@pytest.mark.timeout(600)
def test_bulk_data_import():
    """Takes 5-10 minutes"""
    pass
```

**Skip in fast runs**:
```bash
pytest -m "not slow"
```

#### `@pytest.mark.skip_ci`

**Purpose**: Skip in CI/CD pipeline  
**Use Cases**:
- Manual interaction required
- Interactive testing
- Local development only

**Example**:
```python
@pytest.mark.skip_ci
def test_manual_approval():
    """Requires human interaction"""
    approval = input("Approve? (y/n): ")
    assert approval == "y"
```

#### `@pytest.mark.flaky`

**Purpose**: Known intermittent failures  
**Use Cases**:
- Tests under investigation
- Timing-sensitive tests
- External dependency issues

**Example**:
```python
@pytest.mark.flaky
def test_websocket_connection():
    """
    Known to fail intermittently
    Issue: #1234 - WebSocket connection drops
    """
    pass
```

**Exclude flaky tests**:
```bash
pytest -m "not flaky"
```

#### `@pytest.mark.wip`

**Purpose**: Work in progress  
**Use Cases**:
- Tests under development
- Incomplete features
- Not ready for CI/CD

**Example**:
```python
@pytest.mark.wip
def test_new_feature():
    """Feature not complete yet"""
    pass
```

**Exclude WIP tests**:
```bash
pytest -m "not wip"
```

---

### 4.10 Framework Capability Markers

Tag tests using advanced framework features.

#### `@pytest.mark.ai_validation`

**Purpose**: Uses AI validation suggestions  
**Framework Feature**: AIValidationSuggester  

**Example**:
```python
@pytest.mark.ai_validation
@pytest.mark.bookslot
def test_with_ai_suggestions(request):
    """AI suggests additional validations"""
    from framework.intelligence import AIValidationSuggester
    from tests.comprehensive_report_enhancements import comprehensive_collector
    
    suggester = AIValidationSuggester()
    suggestions = suggester.suggest_validations("booking_form")
    
    for suggestion in suggestions:
        if suggestion.confidence > 0.8:
            comprehensive_collector.add_ai_validation(
                request.node.nodeid,
                suggestion.type,
                suggestion.confidence,
                suggestion.provider,
                applied=True
            )
```

#### `@pytest.mark.performance`

**Purpose**: Performance testing  
**Framework Feature**: PerformanceMetrics  
**Metrics**: Web Vitals, load times, resources  

**Example**:
```python
@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.bookslot
def test_page_load_performance(ui_driver, request):
    """Measure page performance"""
    from tests.comprehensive_report_enhancements import comprehensive_collector
    
    ui_driver.navigate("https://bookslot.dev.example.com")
    metrics = ui_driver.get_performance_metrics()
    
    comprehensive_collector.add_performance_metrics(
        request.node.nodeid,
        metrics
    )
    
    # Assertions
    assert metrics['load_complete'] < 2000  # < 2 seconds
    assert metrics['web_vitals']['lcp'] < 2500  # Good LCP
```

#### `@pytest.mark.visual`

**Purpose**: Visual regression testing  
**Framework Feature**: VisualRegression  

**Example**:
```python
@pytest.mark.visual
@pytest.mark.regression
def test_homepage_visual_regression(ui_driver, request):
    """Compare screenshots"""
    from framework.visual import VisualRegression
    from tests.comprehensive_report_enhancements import comprehensive_collector
    
    visual = VisualRegression(ui_driver)
    ui_driver.navigate("https://example.com")
    
    result = visual.compare(
        baseline="baseline_home.png",
        current="current_home.png",
        threshold=0.1  # 10% difference allowed
    )
    
    comprehensive_collector.add_visual_comparison(
        request.node.nodeid,
        baseline=result['baseline_path'],
        current=result['current_path'],
        diff=result['diff_path'],
        difference_pct=result['difference'],
        passed=result['passed']
    )
```

#### `@pytest.mark.accessibility`

**Purpose**: Accessibility (WCAG) testing  
**Framework Feature**: AccessibilityTester  
**Standards**: WCAG 2.1 A, AA, AAA  

**Example**:
```python
@pytest.mark.accessibility
@pytest.mark.regression
def test_wcag_compliance(ui_driver, request):
    """Test WCAG 2.1 AA compliance"""
    from framework.accessibility import AccessibilityTester
    from tests.comprehensive_report_enhancements import comprehensive_collector
    
    a11y = AccessibilityTester(ui_driver)
    violations = a11y.analyze_page(wcag_level="AA")
    
    comprehensive_collector.add_accessibility_results(
        request.node.nodeid,
        violations=violations,
        wcag_level="AA",
        score=a11y.calculate_score(violations)
    )
    
    # Assert no critical violations
    critical = [v for v in violations if v['impact'] == 'critical']
    assert len(critical) == 0
```

#### `@pytest.mark.security`

**Purpose**: Security vulnerability scanning  
**Framework Feature**: SecurityTester  
**Tool**: OWASP ZAP integration  

**Example**:
```python
@pytest.mark.security
@pytest.mark.slow
@pytest.mark.staging_only
@pytest.mark.timeout(600)
def test_security_scan(request):
    """OWASP ZAP security scan"""
    from framework.security import SecurityTester
    from tests.comprehensive_report_enhancements import comprehensive_collector
    
    security = SecurityTester()
    security.start_zap_session()
    
    vulnerabilities = security.scan_url("https://staging.example.com")
    
    comprehensive_collector.add_security_scan_results(
        request.node.nodeid,
        {'vulnerabilities': vulnerabilities}
    )
    
    # Assert no high-risk vulnerabilities
    high_risk = [v for v in vulnerabilities if v['severity'] == 'high']
    assert len(high_risk) == 0
```

#### `@pytest.mark.mobile_testing`

**Purpose**: Mobile device testing  
**Framework Feature**: MobileTester  
**Devices**: iPhone, Pixel, Galaxy, iPad  

**Example**:
```python
@pytest.mark.mobile_testing
@pytest.mark.bookslot
def test_mobile_responsive(ui_driver, request):
    """Test mobile responsiveness"""
    from framework.mobile import MobileTester
    from tests.comprehensive_report_enhancements import comprehensive_collector
    
    mobile = MobileTester(ui_driver)
    mobile.emulate_device("iPhone 14 Pro")
    
    comprehensive_collector.add_mobile_info(
        request.node.nodeid,
        "iPhone 14 Pro",
        "portrait"
    )
    
    # Test mobile interactions
    mobile.tap("button#menu")
    comprehensive_collector.add_mobile_gesture(
        request.node.nodeid,
        "tap",
        "button#menu"
    )
```

#### `@pytest.mark.recording`

**Purpose**: Auto-generated recorded tests  
**Framework Feature**: RecordingWorkflow  

**Example**:
```python
@pytest.mark.recording
@pytest.mark.bookslot
def test_recorded_booking_flow():
    """Auto-generated from recording"""
    # Generated by: python record_cli.py record bookslot
    pass
```

#### `@pytest.mark.websocket`

**Purpose**: WebSocket communication testing  
**Framework Feature**: APIInterceptor WebSocket  

**Example**:
```python
@pytest.mark.websocket
@pytest.mark.integration
def test_websocket_messages(ui_driver, request):
    """Capture WebSocket messages"""
    from tests.comprehensive_report_enhancements import comprehensive_collector
    
    # WebSocket messages captured automatically
    comprehensive_collector.add_websocket_message(
        request.node.nodeid,
        direction="sent",
        data={"type": "subscribe", "channel": "orders"}
    )
```

---

## 5. USING MARKERS IN TESTS

### 5.1 Single Marker

```python
@pytest.mark.smoke
def test_login():
    """Single marker applied"""
    pass
```

### 5.2 Multiple Markers

```python
@pytest.mark.smoke
@pytest.mark.critical
@pytest.mark.bookslot
@pytest.mark.integration
def test_important_flow():
    """Multiple markers for precise categorization"""
    pass
```

**Order doesn't matter**, but by convention:
1. Test category (smoke, regression)
2. Priority (critical, high)
3. Project (bookslot, patientintake)
4. Other metadata

### 5.3 Markers with Parameters

```python
@pytest.mark.module("checkout")
@pytest.mark.ui_framework("React")
@pytest.mark.auth_type("SSO")
def test_checkout():
    """Markers with parameter values"""
    pass
```

### 5.4 Apply to Test Class

All methods inherit class markers:

```python
@pytest.mark.regression
@pytest.mark.bookslot
class TestBookSlotFeatures:
    """All tests get regression + bookslot markers"""
    
    def test_booking(self):
        """Has regression + bookslot"""
        pass
    
    def test_cancellation(self):
        """Has regression + bookslot"""
        pass
    
    @pytest.mark.critical
    def test_payment(self):
        """Has regression + bookslot + critical"""
        pass
```

### 5.5 Apply to Module

At the top of your test file:

```python
# test_callcenter.py
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.callcenter]

def test_call_routing():
    """Automatically has integration + callcenter"""
    pass

def test_call_recording():
    """Automatically has integration + callcenter"""
    pass
```

### 5.6 Combining Markers and Parametrize

```python
@pytest.mark.smoke
@pytest.mark.parametrize("project", ["bookslot", "patientintake", "callcenter"])
def test_homepage_all_projects(project):
    """
    Creates 3 tests:
    - test_homepage_all_projects[bookslot]
    - test_homepage_all_projects[patientintake]
    - test_homepage_all_projects[callcenter]
    
    All have smoke marker
    """
    from config.settings import get_ui_url
    url = get_ui_url(project)
    # Test the homepage
    pass
```

---

## 6. RUNNING TESTS WITH MARKERS

### 6.1 Basic Marker Selection

Run tests with a specific marker:

```bash
# Run all smoke tests
pytest -m smoke

# Run all critical tests
pytest -m critical

# Run all BookSlot tests
pytest -m bookslot

# Run all integration tests
pytest -m integration
```

### 6.2 AND Logic (Both Markers Required)

Run tests that have BOTH markers:

```bash
# Tests that are BOTH smoke AND critical
pytest -m "smoke and critical"

# Tests that are BOTH bookslot AND integration
pytest -m "bookslot and integration"

# Tests that are BOTH ui_only AND regression
pytest -m "ui_only and regression"

# Complex AND
pytest -m "smoke and critical and bookslot"
```

### 6.3 OR Logic (Either Marker)

Run tests that have EITHER marker:

```bash
# Tests that are EITHER smoke OR critical
pytest -m "smoke or critical"

# Tests for ANY project
pytest -m "bookslot or patientintake or callcenter"

# Tests that are EITHER ui_only OR api_only
pytest -m "ui_only or api_only"
```

### 6.4 NOT Logic (Exclude Marker)

Run tests that DON'T have a marker:

```bash
# All tests EXCEPT slow tests
pytest -m "not slow"

# All tests EXCEPT flaky tests
pytest -m "not flaky"

# All tests EXCEPT work in progress
pytest -m "not wip"

# All tests EXCEPT those that skip in CI
pytest -m "not skip_ci"
```

### 6.5 Complex Expressions

Combine AND, OR, NOT with parentheses:

```bash
# Smoke OR critical, but NOT flaky
pytest -m "(smoke or critical) and not flaky"

# BookSlot integration tests, but NOT slow
pytest -m "bookslot and integration and not slow"

# UI or API tests, but only if they're smoke tests
pytest -m "(ui_only or api_only) and smoke"

# Critical tests for any project, but not WIP
pytest -m "critical and (bookslot or patientintake or callcenter) and not wip"

# All tests except slow and flaky
pytest -m "not (slow or flaky)"

# High or critical priority, any project, not WIP
pytest -m "(high or critical) and (bookslot or patientintake or callcenter) and not wip"
```

### 6.6 Common Use Cases

#### Pre-Deployment Check (Fast)
```bash
pytest -m "(smoke or critical) and not (flaky or wip)"
```
**Runs**: Smoke + critical tests, excludes unstable tests  
**Time**: 5-10 minutes

#### Full Project Regression
```bash
pytest -m "bookslot and regression and not slow"
```
**Runs**: All BookSlot regression tests, excludes slow tests  
**Time**: 30-45 minutes

#### API Layer Testing
```bash
pytest -m "api_only or api_validation"
```
**Runs**: All API-focused tests  
**Time**: 10-15 minutes

#### Production Monitoring
```bash
pytest -m "prod_safe and smoke"
```
**Runs**: Safe read-only smoke tests  
**Time**: 5 minutes

#### CI/CD Fast Feedback
```bash
pytest -m "(smoke or critical) and not (slow or flaky or skip_ci)"
```
**Runs**: Fast, stable, critical tests  
**Time**: 10-15 minutes

#### Nightly Build
```bash
pytest -m "regression and not (flaky or wip)"
```
**Runs**: Complete regression suite, stable tests  
**Time**: 1-3 hours

### 6.7 Additional Options

#### Verbose Output
```bash
pytest -m smoke -v
```

#### With HTML Report
```bash
pytest -m smoke --html=reports/smoke_report.html --self-contained-html
```

#### Dry Run (Show Which Tests)
```bash
pytest -m smoke --collect-only
```

#### Parallel Execution
```bash
pytest -m regression -n auto  # Use all CPUs
pytest -m regression -n 4     # Use 4 workers
```

#### Stop on First Failure
```bash
pytest -m critical -x
```

#### Run Last Failed Tests
```bash
pytest -m smoke --lf
```

---

## 7. ADVANCED MARKER COMBINATIONS

Real-world scenarios with complex marker expressions.

### Scenario 1: Pre-Deployment Quick Check

**Goal**: Fast validation before deployment  
**Time**: 5-10 minutes  
**Command**:
```bash
pytest -m "smoke and critical and not flaky" --html=reports/pre_deploy.html
```

**What runs**:
- ✅ Smoke tests (quick)
- ✅ Critical functionality
- ❌ Excludes flaky tests (unstable)

**Use in CI/CD**:
```yaml
# .github/workflows/pre-deploy.yml
- name: Pre-deployment tests
  run: pytest -m "smoke and critical and not flaky"
```

---

### Scenario 2: Full BookSlot Regression

**Goal**: Complete BookSlot feature validation  
**Time**: 30-45 minutes  
**Command**:
```bash
pytest -m "bookslot and regression and not slow" -n auto --html=reports/bookslot_regression.html
```

**What runs**:
- ✅ All BookSlot tests
- ✅ Regression-level detail
- ❌ Excludes slow performance tests
- 🚀 Parallel execution

---

### Scenario 3: API Layer Testing Only

**Goal**: API contract and integration validation  
**Time**: 10-15 minutes  
**Command**:
```bash
pytest -m "api_only or api_validation" --html=reports/api_tests.html
```

**What runs**:
- ✅ API-only tests (no UI)
- ✅ Tests requiring API validation
- 🔍 API contract testing

---

### Scenario 4: Production-Safe Monitoring

**Goal**: Safe production environment monitoring  
**Time**: 5 minutes  
**Command**:
```bash
pytest -m "prod_safe and smoke" --html=reports/prod_monitoring.html
```

**What runs**:
- ✅ Production-safe tests (read-only)
- ✅ Smoke-level checks
- 🛡️ No data modification

**Schedule**:
```cron
# Run every hour in production
0 * * * * pytest -m "prod_safe and smoke"
```

---

### Scenario 5: Multi-Project Integration

**Goal**: End-to-end cross-project validation  
**Time**: 45-60 minutes  
**Command**:
```bash
pytest -m "multi_project and integration and not wip" --html=reports/multi_project.html
```

**What runs**:
- ✅ Cross-project flows
- ✅ Full integration (UI+API+DB)
- ❌ Excludes work in progress

---

### Scenario 6: Nightly Build - Full Suite

**Goal**: Comprehensive nightly validation  
**Time**: 2-3 hours  
**Command**:
```bash
pytest -m "regression and not (flaky or wip)" -n auto --html=reports/nightly.html
```

**What runs**:
- ✅ All regression tests
- ✅ Includes slow tests
- ❌ Excludes flaky and WIP
- 🚀 Parallel execution

**Schedule**:
```cron
# Run nightly at 2 AM
0 2 * * * pytest -m "regression and not (flaky or wip)" -n auto
```

---

### Scenario 7: CI/CD Fast Feedback

**Goal**: Fast CI/CD feedback loop  
**Time**: 10-15 minutes  
**Command**:
```bash
pytest -m "(smoke or critical) and not (slow or flaky or skip_ci)" -n auto
```

**What runs**:
- ✅ Smoke and critical tests
- ✅ Fast execution
- ❌ Excludes slow, flaky, and CI-skip tests
- 🚀 Parallel execution

**Use in CI/CD**:
```yaml
# .github/workflows/ci.yml
- name: Fast CI tests
  run: pytest -m "(smoke or critical) and not (slow or flaky or skip_ci)" -n auto
```

---

### Scenario 8: Mobile Testing

**Goal**: Test mobile responsiveness across projects  
**Time**: 20-30 minutes  
**Command**:
```bash
pytest -m "mobile and not slow" --html=reports/mobile_tests.html
```

**What runs**:
- ✅ Mobile device emulation tests
- ✅ Touch gesture tests
- ❌ Excludes slow tests

---

### Scenario 9: Security & Performance

**Goal**: Non-functional testing  
**Time**: 1-2 hours  
**Command**:
```bash
pytest -m "(security or performance or accessibility) and staging_only" --html=reports/nonfunctional.html
```

**What runs**:
- ✅ Security scans
- ✅ Performance tests
- ✅ Accessibility checks
- 🎯 Only in staging environment

---

### Scenario 10: Critical Path - Any Project

**Goal**: Critical tests across all projects  
**Time**: 15-20 minutes  
**Command**:
```bash
pytest -m "critical and (bookslot or patientintake or callcenter) and not flaky" -n auto
```

**What runs**:
- ✅ Critical tests only
- ✅ All three projects
- ❌ Excludes flaky tests
- 🚀 Parallel execution

---

## 8. REAL-WORLD EXAMPLES

Complete test examples from this framework showing marker usage.

### Example 1: BookSlot Appointment Booking (Full Integration)

```python
import pytest
from tests.comprehensive_report_enhancements import comprehensive_collector

@pytest.mark.smoke
@pytest.mark.critical
@pytest.mark.bookslot
@pytest.mark.integration
@pytest.mark.modern_spa
@pytest.mark.ui_framework("React")
@pytest.mark.module("booking")
def test_bookslot_appointment_booking_complete(ui_driver, api_client, db_client, request):
    """
    Complete appointment booking flow with UI + API + DB validation
    
    Flow:
    1. UI: Navigate to BookSlot, fill form, submit
    2. API: Validate appointment creation endpoint called
    3. DB: Verify appointment saved in database
    
    Markers:
    - smoke: Quick critical path validation
    - critical: Must pass before deployment
    - bookslot: BookSlot project
    - integration: Tests all layers
    - modern_spa: React application (Playwright preferred)
    - ui_framework: React-specific handling
    - module: Booking module
    """
    test_id = request.node.nodeid
    
    # UI Interaction
    comprehensive_collector.add_log(test_id, "Starting BookSlot appointment booking", "INFO")
    comprehensive_collector.add_execution_flow_step(test_id, "Navigate to BookSlot", "UI")
    
    ui_driver.navigate("https://bookslot.dev.example.com")
    ui_driver.click("button[data-testid='book-appointment']")
    ui_driver.fill("input#patient-name", "John Doe")
    ui_driver.fill("input#phone", "555-1234")
    ui_driver.select("select#appointment-type", "Consultation")
    ui_driver.click("button#submit-booking")
    
    # Get appointment ID from UI
    appointment_id = ui_driver.get_text("span#appointment-id")
    comprehensive_collector.add_log(test_id, f"Appointment created: {appointment_id}", "INFO")
    
    # API Validation
    comprehensive_collector.add_execution_flow_step(test_id, "Validate via API", "API")
    response = api_client.get(f"/api/appointments/{appointment_id}")
    
    comprehensive_collector.add_api_call(
        test_id,
        method="GET",
        url=f"/api/appointments/{appointment_id}",
        status_code=response.status_code,
        response_time=response.elapsed.total_seconds() * 1000,
        response_data=response.json()
    )
    
    assert response.status_code == 200
    comprehensive_collector.add_assertion(
        test_id,
        "API Response Status",
        "200",
        str(response.status_code),
        True,
        "API returned appointment successfully"
    )
    
    # Database Validation
    comprehensive_collector.add_execution_flow_step(test_id, "Verify in database", "Database")
    appointment = db_client.query(
        "SELECT * FROM appointments WHERE id = ?",
        [appointment_id]
    )
    
    comprehensive_collector.add_db_query(
        test_id,
        query=f"SELECT * FROM appointments WHERE id = '{appointment_id}'",
        execution_time=12.5,
        rows_affected=1
    )
    
    assert appointment is not None
    comprehensive_collector.add_assertion(
        test_id,
        "Database Record",
        "Record exists",
        "Record found",
        True,
        "Appointment saved in database"
    )
    
    comprehensive_collector.add_log(test_id, "Test completed successfully", "INFO")
```

**Run this test**:
```bash
# Run just this test
pytest -m "bookslot and integration and critical"

# Run with full reporting
pytest -m "bookslot and integration" --html=reports/bookslot.html
```

---

### Example 2: PatientIntake Registration (API-First)

```python
@pytest.mark.patientintake
@pytest.mark.api_validation
@pytest.mark.regression
@pytest.mark.high
@pytest.mark.module("registration")
def test_patient_registration_api_validation(api_client, request):
    """
    Patient registration with API-first validation
    
    Markers:
    - patientintake: PatientIntake project
    - api_validation: Focuses on API validation
    - regression: Detailed feature validation
    - high: High priority test
    - module: Registration module
    """
    test_id = request.node.nodeid
    
    # Create patient via API
    patient_data = {
        "first_name": "John",
        "last_name": "Doe",
        "dob": "1990-01-01",
        "email": "john.doe@example.com",
        "phone": "555-1234"
    }
    
    comprehensive_collector.add_log(test_id, "Creating patient via API", "INFO")
    
    response = api_client.post("/api/patients", json=patient_data)
    
    comprehensive_collector.add_api_call(
        test_id,
        method="POST",
        url="/api/patients",
        status_code=response.status_code,
        response_time=response.elapsed.total_seconds() * 1000,
        request_data=patient_data,
        response_data=response.json()
    )
    
    assert response.status_code == 201
    comprehensive_collector.add_assertion(
        test_id,
        "Patient Creation",
        "201 Created",
        f"{response.status_code} Created",
        True,
        "Patient successfully created"
    )
    
    patient_id = response.json()["patient_id"]
    assert patient_id is not None
    comprehensive_collector.add_log(test_id, f"Patient created: {patient_id}", "INFO")
```

---

### Example 3: CallCenter Dashboard (Legacy UI + SSO)

```python
@pytest.mark.callcenter
@pytest.mark.legacy_ui
@pytest.mark.ui_framework("JSP")
@pytest.mark.auth_type("SSO")
@pytest.mark.module("dashboard")
@pytest.mark.regression
def test_callcenter_dashboard_sso_login(ui_driver, request):
    """
    CallCenter dashboard access with SSO authentication
    
    Markers:
    - callcenter: CallCenter project
    - legacy_ui: JSP-based legacy application (Selenium preferred)
    - ui_framework: JSP framework
    - auth_type: SSO authentication
    - module: Dashboard module
    - regression: Comprehensive validation
    """
    test_id = request.node.nodeid
    
    # SSO Login flow
    comprehensive_collector.add_log(test_id, "Starting SSO login", "INFO")
    comprehensive_collector.add_execution_flow_step(test_id, "Initiate SSO login", "UI")
    
    ui_driver.navigate("https://callcenter.dev.example.com")
    ui_driver.click("button#sso-login")
    
    # SSO provider (simulated)
    ui_driver.wait_for_url_contains("sso.example.com")
    ui_driver.fill("input#username", "agent1")
    ui_driver.fill("input#password", "SecurePass123!")
    ui_driver.click("button#sso-submit")
    
    # Back to CallCenter
    ui_driver.wait_for_url_contains("callcenter.dev.example.com")
    
    comprehensive_collector.add_log(test_id, "SSO login successful", "INFO")
    
    # Verify dashboard elements
    assert ui_driver.is_visible("div#dashboard-header")
    comprehensive_collector.add_assertion(
        test_id,
        "Dashboard Header",
        "Visible",
        "Visible",
        True,
        "Dashboard loaded successfully"
    )
    
    assert ui_driver.get_text("h1.title") == "Call Center Dashboard"
    comprehensive_collector.add_assertion(
        test_id,
        "Dashboard Title",
        "Call Center Dashboard",
        ui_driver.get_text("h1.title"),
        True,
        "Correct dashboard title displayed"
    )
```

---

### Example 4: Performance Testing

```python
@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.bookslot
@pytest.mark.timeout(300)
@pytest.mark.staging_only
def test_bookslot_homepage_performance(ui_driver, request):
    """
    Performance testing for BookSlot homepage
    
    Markers:
    - performance: Performance-focused test
    - slow: Takes > 30 seconds
    - bookslot: BookSlot project
    - timeout: 5-minute timeout
    - staging_only: Performance testing in staging
    
    Validates:
    - Page load time < 2 seconds
    - LCP < 2.5 seconds (Good)
    - FID < 100ms (Good)
    - CLS < 0.1 (Good)
    """
    test_id = request.node.nodeid
    
    comprehensive_collector.add_log(test_id, "Starting performance test", "INFO")
    
    # Navigate and collect metrics
    ui_driver.navigate("https://bookslot.staging.example.com")
    
    # Get performance metrics (framework feature)
    metrics = {
        'load_complete': 1234,
        'time_to_first_byte': 245,
        'dom_interactive': 892,
        'web_vitals': {
            'lcp': 2100,  # Good - under 2500ms
            'fid': 85,     # Good - under 100ms
            'cls': 0.08    # Good - under 0.1
        },
        'resources': {
            'scripts': {'count': 15, 'size': 524288, 'time': 450},
            'images': {'count': 22, 'size': 1048576, 'time': 680}
        }
    }
    
    comprehensive_collector.add_performance_metrics(test_id, metrics)
    comprehensive_collector.add_log(test_id, "Performance metrics collected", "INFO")
    
    # Assertions
    assert metrics['load_complete'] < 2000
    comprehensive_collector.add_assertion(
        test_id,
        "Page Load Time",
        "< 2000ms",
        f"{metrics['load_complete']}ms",
        True,
        "Page loaded within 2 seconds"
    )
    
    assert metrics['web_vitals']['lcp'] < 2500
    comprehensive_collector.add_assertion(
        test_id,
        "LCP (Largest Contentful Paint)",
        "< 2500ms (Good)",
        f"{metrics['web_vitals']['lcp']}ms",
        True,
        "LCP meets Good threshold"
    )
    
    assert metrics['web_vitals']['fid'] < 100
    assert metrics['web_vitals']['cls'] < 0.1
```

---

### Example 5: Accessibility Testing (WCAG AA)

```python
@pytest.mark.accessibility
@pytest.mark.bookslot
@pytest.mark.regression
@pytest.mark.prod_safe
def test_bookslot_accessibility_wcag_aa(ui_driver, request):
    """
    WCAG 2.1 AA compliance testing for BookSlot
    
    Markers:
    - accessibility: Accessibility-focused
    - bookslot: BookSlot project
    - regression: Comprehensive checks
    - prod_safe: Read-only, safe for production
    
    Validates:
    - WCAG 2.1 Level AA compliance
    - No critical violations
    - Accessibility score > 80
    """
    test_id = request.node.nodeid
    
    comprehensive_collector.add_log(test_id, "Starting WCAG AA accessibility audit", "INFO")
    
    ui_driver.navigate("https://bookslot.dev.example.com")
    
    # Simulate accessibility violations
    violations = [
        {
            'impact': 'serious',
            'description': 'Form elements must have labels',
            'target': 'input#email',
            'fix': 'Add <label> element for input'
        },
        {
            'impact': 'moderate',
            'description': 'Links must have discernible text',
            'target': 'a.icon-link',
            'fix': 'Add aria-label or visible text'
        }
    ]
    
    comprehensive_collector.add_accessibility_results(
        test_id,
        violations=violations,
        wcag_level="AA",
        score=85.5
    )
    
    comprehensive_collector.add_accessibility_check(
        test_id,
        "Color Contrast",
        passed=True,
        details="All text meets WCAG AA contrast (4.5:1)"
    )
    
    comprehensive_collector.add_accessibility_check(
        test_id,
        "Keyboard Navigation",
        passed=True,
        details="All interactive elements keyboard accessible"
    )
    
    # Assert no critical violations
    critical_violations = [v for v in violations if v['impact'] == 'critical']
    assert len(critical_violations) == 0
    
    comprehensive_collector.add_assertion(
        test_id,
        "Critical A11y Violations",
        "0",
        str(len(critical_violations)),
        True,
        "No critical accessibility violations"
    )
```

---

### Example 6: Multi-Project Flow

```python
@pytest.mark.bookslot
@pytest.mark.patientintake
@pytest.mark.multi_project
@pytest.mark.integration
@pytest.mark.critical
@pytest.mark.slow
@pytest.mark.timeout(600)
def test_bookslot_to_patientintake_complete_flow(ui_driver, api_client, db_client, request):
    """
    End-to-end flow spanning BookSlot and PatientIntake
    
    Flow:
    1. BookSlot: Book appointment
    2. BookSlot: Receive confirmation
    3. PatientIntake: Complete patient intake form
    4. PatientIntake: Verify appointment linked to patient
    
    Markers:
    - bookslot: First project
    - patientintake: Second project
    - multi_project: Spans multiple projects
    - integration: All layers (UI+API+DB)
    - critical: Must pass
    - slow: Extended execution time
    - timeout: 10-minute timeout
    """
    test_id = request.node.nodeid
    
    # Step 1: BookSlot - Book appointment
    comprehensive_collector.add_log(test_id, "Step 1: Booking appointment in BookSlot", "INFO")
    comprehensive_collector.add_execution_flow_step(test_id, "Book appointment", "BookSlot-UI")
    
    ui_driver.navigate("https://bookslot.dev.example.com")
    ui_driver.click("button#new-appointment")
    ui_driver.fill("input#patient-name", "John Doe")
    ui_driver.click("button#submit")
    
    appointment_id = ui_driver.get_text("span#confirmation-id")
    comprehensive_collector.add_log(test_id, f"Appointment booked: {appointment_id}", "INFO")
    
    # Step 2: Verify in BookSlot API
    comprehensive_collector.add_execution_flow_step(test_id, "Verify booking via API", "BookSlot-API")
    response = api_client.get(f"/api/bookslot/appointments/{appointment_id}")
    assert response.status_code == 200
    
    comprehensive_collector.add_api_call(
        test_id,
        method="GET",
        url=f"/api/bookslot/appointments/{appointment_id}",
        status_code=200,
        response_time=150.5
    )
    
    # Step 3: PatientIntake - Complete intake
    comprehensive_collector.add_log(test_id, "Step 2: Completing intake in PatientIntake", "INFO")
    comprehensive_collector.add_execution_flow_step(test_id, "Navigate to intake", "PatientIntake-UI")
    
    ui_driver.navigate(f"https://patientintake.dev.example.com/intake?apt={appointment_id}")
    ui_driver.fill("input#medical-history", "No known allergies")
    ui_driver.click("button#submit-intake")
    
    comprehensive_collector.add_log(test_id, "Intake form submitted", "INFO")
    
    # Step 4: Verify linkage in database
    comprehensive_collector.add_execution_flow_step(test_id, "Verify data linkage", "Database")
    record = db_client.query(
        "SELECT * FROM patient_appointments WHERE appointment_id = ?",
        [appointment_id]
    )
    
    comprehensive_collector.add_db_query(
        test_id,
        query=f"SELECT * FROM patient_appointments WHERE appointment_id = '{appointment_id}'",
        execution_time=8.3,
        rows_affected=1
    )
    
    assert record is not None
    assert record['status'] == 'completed'
    
    comprehensive_collector.add_assertion(
        test_id,
        "Multi-Project Flow",
        "Completed",
        "Completed",
        True,
        "BookSlot → PatientIntake flow successful"
    )
```

---

### Example 7: Security Testing (OWASP ZAP)

```python
@pytest.mark.security
@pytest.mark.slow
@pytest.mark.bookslot
@pytest.mark.staging_only
@pytest.mark.timeout(600)
def test_bookslot_security_scan(request):
    """
    OWASP security vulnerability scan for BookSlot
    
    Markers:
    - security: Security-focused test
    - slow: Takes ~10 minutes
    - bookslot: BookSlot project
    - staging_only: Too intrusive for dev/prod
    - timeout: 10-minute timeout
    
    Scans for:
    - SQL Injection
    - XSS vulnerabilities
    - CSRF issues
    - Security headers
    """
    test_id = request.node.nodeid
    
    comprehensive_collector.add_log(test_id, "Starting OWASP ZAP security scan", "INFO")
    
    # Simulate security vulnerabilities
    vulnerabilities = [
        {
            'type': 'SQL Injection',
            'severity': 'high',
            'url': '/api/users?id=1',
            'description': 'Possible SQL injection in id parameter'
        },
        {
            'type': 'XSS',
            'severity': 'medium',
            'url': '/search?q=<script>',
            'description': 'Input not sanitized'
        }
    ]
    
    for vuln in vulnerabilities:
        comprehensive_collector.add_security_vulnerability(
            test_id,
            vuln_type=vuln['type'],
            severity=vuln['severity'],
            url=vuln['url'],
            description=vuln['description']
        )
    
    comprehensive_collector.add_security_scan_results(test_id, {
        'timestamp': '2026-01-27T10:00:00',
        'scan_duration': 580.5,
        'urls_scanned': 127,
        'total_vulnerabilities': len(vulnerabilities)
    })
    
    # Assert no high-risk vulnerabilities
    high_risk = [v for v in vulnerabilities if v['severity'] == 'high']
    assert len(high_risk) == 0, f"Found {len(high_risk)} high-risk vulnerabilities"
```

---

### Example 8: Mobile Testing

```python
@pytest.mark.mobile
@pytest.mark.mobile_testing
@pytest.mark.bookslot
@pytest.mark.regression
def test_bookslot_mobile_responsive(ui_driver, request):
    """
    Mobile responsive design testing
    
    Markers:
    - mobile: Mobile-specific test
    - mobile_testing: Uses mobile testing features
    - bookslot: BookSlot project
    - regression: Detailed validation
    
    Tests:
    - iPhone 14 Pro viewport
    - Touch gestures
    - Mobile navigation
    - Responsive layout
    """
    test_id = request.node.nodeid
    
    comprehensive_collector.add_log(test_id, "Starting mobile testing on iPhone 14 Pro", "INFO")
    
    # Set mobile device info
    comprehensive_collector.add_mobile_info(test_id, "iPhone 14 Pro", "portrait")
    comprehensive_collector.add_network_throttling(test_id, "4G - LTE")
    
    # Navigate
    ui_driver.navigate("https://bookslot.dev.example.com")
    
    # Test touch gestures
    comprehensive_collector.add_mobile_gesture(
        test_id,
        gesture_type='tap',
        target='button#book-now',
        details={'x': 195, 'y': 422}
    )
    
    comprehensive_collector.add_mobile_gesture(
        test_id,
        gesture_type='swipe',
        target='div#carousel',
        details={'from': (100, 300), 'to': (300, 300)}
    )
    
    # Verify responsive elements
    assert ui_driver.is_visible("button.mobile-menu")
    comprehensive_collector.add_assertion(
        test_id,
        "Mobile Menu",
        "Visible",
        "Visible",
        True,
        "Mobile menu displays correctly"
    )
```

---

### Example 9: Parametrized Cross-Project Testing

```python
@pytest.mark.smoke
@pytest.mark.prod_safe
@pytest.mark.parametrize("project,expected_title", [
    ("bookslot", "Book Appointment"),
    ("patientintake", "Patient Intake"),
    ("callcenter", "Call Center")
])
def test_homepage_all_projects(ui_driver, project, expected_title, request):
    """
    Smoke test: Verify homepage loads for all projects
    
    Markers:
    - smoke: Quick validation
    - prod_safe: Read-only test
    - parametrize: Runs for each project
    
    Creates 3 tests:
    - test_homepage_all_projects[bookslot-Book Appointment]
    - test_homepage_all_projects[patientintake-Patient Intake]
    - test_homepage_all_projects[callcenter-Call Center]
    """
    test_id = request.node.nodeid
    
    from config.settings import get_ui_url
    
    comprehensive_collector.add_log(test_id, f"Testing {project} homepage", "INFO")
    
    url = get_ui_url(project)
    ui_driver.navigate(url)
    
    # Verify page loaded
    assert ui_driver.get_title() is not None
    assert ui_driver.is_visible("body")
    
    # Verify correct project
    title = ui_driver.get_text("h1")
    assert expected_title in title
    
    comprehensive_collector.add_assertion(
        test_id,
        f"{project.capitalize()} Homepage",
        f"Contains '{expected_title}'",
        title,
        True,
        f"{project} homepage loaded successfully"
    )
```

---

### Example 10: AI Validation Testing

```python
import os

@pytest.mark.ai_validation
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY") and not os.getenv("CLAUDE_API_KEY"),
    reason="AI provider API keys not configured"
)
@pytest.mark.bookslot
@pytest.mark.regression
def test_ai_validation_suggestions(ui_driver, request):
    """
    Test AI validation suggestions
    
    Markers:
    - ai_validation: Uses AI features
    - skipif: Skips if no API key
    - bookslot: BookSlot project
    - regression: Detailed validation
    
    Uses framework's AI intelligence to suggest additional validations
    """
    test_id = request.node.nodeid
    
    from framework.intelligence import AIValidationSuggester
    
    comprehensive_collector.add_log(test_id, "Requesting AI validation suggestions", "INFO")
    
    suggester = AIValidationSuggester()
    suggestions = suggester.suggest_validations("booking_form")
    
    comprehensive_collector.add_log(
        test_id,
        f"AI suggested {len(suggestions)} validations",
        "INFO"
    )
    
    # Apply high-confidence suggestions
    for suggestion in suggestions:
        if suggestion.confidence > 0.8:
            comprehensive_collector.add_ai_validation(
                test_id,
                validation_type=suggestion.type,
                confidence=suggestion.confidence,
                suggested_by=suggestion.provider,
                applied=True
            )
    
    assert len(suggestions) > 0
    comprehensive_collector.add_assertion(
        test_id,
        "AI Suggestions",
        "> 0",
        str(len(suggestions)),
        True,
        "AI provided validation suggestions"
    )
```

---

## 9. BEST PRACTICES

### ✅ DO's

#### 1. Always Register Custom Markers

**Register in pytest.ini**:
```ini
[pytest]
markers =
    custom_marker: Description of custom marker
```

**Why**: Prevents "unknown marker" warnings and provides documentation.

---

#### 2. Use Descriptive Marker Names

**Good**:
```python
@pytest.mark.bookslot_appointment_flow
@pytest.mark.payment_processing
```

**Bad**:
```python
@pytest.mark.test1
@pytest.mark.x
```

---

#### 3. Combine Markers for Precise Selection

**Example**:
```python
@pytest.mark.smoke          # Quick test
@pytest.mark.critical       # Must pass
@pytest.mark.bookslot       # Project
@pytest.mark.integration    # Test type
def test_important_feature():
    pass
```

**Benefits**: Allows precise test selection in CI/CD.

---

#### 4. Use Consistent Marker Order

**Convention**:
```python
# 1. Category (smoke, regression)
@pytest.mark.smoke

# 2. Priority (critical, high)
@pytest.mark.critical

# 3. Project (bookslot, patientintake)
@pytest.mark.bookslot

# 4. Type (integration, ui_only)
@pytest.mark.integration

# 5. Other metadata
@pytest.mark.modern_spa
@pytest.mark.module("checkout")

def test_feature():
    pass
```

---

#### 5. Add Markers to CI/CD Pipelines

**Fast Pipeline** (5-10 minutes):
```yaml
- name: Fast tests
  run: pytest -m "smoke and critical and not flaky"
```

**Nightly Pipeline** (1-2 hours):
```yaml
- name: Full regression
  run: pytest -m "regression and not wip"
```

---

#### 6. Mark Flaky Tests Explicitly

```python
@pytest.mark.flaky
def test_intermittent_issue():
    """
    Known to fail intermittently
    Issue: #1234 - WebSocket connection drops
    """
    pass
```

**Then exclude from CI**:
```bash
pytest -m "not flaky"
```

**Action**: Investigate and fix, don't ignore!

---

#### 7. Use Priority Markers for Test Triage

```python
@pytest.mark.critical  # Revenue-affecting
def test_payment():
    pass

@pytest.mark.high      # Important features
def test_authentication():
    pass

@pytest.mark.medium    # Standard features
def test_profile_update():
    pass

@pytest.mark.low       # Nice-to-have
def test_tooltip():
    pass
```

---

#### 8. Mark Environment-Specific Tests

```python
@pytest.mark.dev_only
def test_debug_feature():
    """Development only - has debugging code"""
    pass

@pytest.mark.prod_safe
def test_health_check():
    """Safe for production - read-only"""
    pass

@pytest.mark.staging_only
def test_performance_load():
    """Staging only - generates load"""
    pass
```

---

#### 9. Document Marker Usage

**In test docstring**:
```python
@pytest.mark.integration
@pytest.mark.bookslot
def test_booking_flow():
    """
    Complete booking flow test
    
    Markers:
    - integration: Tests UI + API + DB
    - bookslot: BookSlot project
    
    Flow:
    1. UI: Fill booking form
    2. API: Verify creation
    3. DB: Verify persistence
    """
    pass
```

---

#### 10. Review Markers in Code Reviews

**Check**:
- ✅ Markers are registered
- ✅ Markers are appropriate
- ✅ Priority markers are correct
- ✅ Project markers are accurate

---

### ❌ DON'Ts

#### 1. Don't Use Markers Without Registration

**Bad**:
```python
@pytest.mark.my_custom_marker  # Not registered!
def test_something():
    pass
```

**Result**: Warning in pytest output.

**Fix**: Add to pytest.ini first.

---

#### 2. Don't Over-Mark Tests

**Bad** (too many markers):
```python
@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.integration
@pytest.mark.ui_only
@pytest.mark.critical
@pytest.mark.high
@pytest.mark.bookslot
@pytest.mark.patientintake
@pytest.mark.modern_spa
@pytest.mark.legacy_ui
def test_something():
    pass
```

**Guideline**: Max 3-5 markers per test.

---

#### 3. Don't Create Redundant Markers

**Bad**:
```python
@pytest.mark.ui_test
@pytest.mark.ui_only  # Redundant!
```

**Pick one naming convention** and stick to it.

---

#### 4. Don't Skip Tests Permanently

**Bad**:
```python
@pytest.mark.skip(reason="Broken")
def test_feature():
    pass
```

**Better**:
```python
@pytest.mark.skip(reason="Bug #1234 - Fix ETA: 2026-02-01")
def test_feature():
    pass
```

**Best**: Fix the issue or use `xfail` if tracking a known bug.

---

#### 5. Don't Use Markers as TODO Lists

**Bad**:
```python
@pytest.mark.fix_later
@pytest.mark.needs_work
@pytest.mark.todo
```

**Better**: Use your issue tracker (Jira, GitHub Issues).

---

#### 6. Don't Mark Tests Without Documentation

**Bad**:
```python
@pytest.mark.special_test
def test_something():
    pass  # What makes this special?
```

**Good**:
```python
@pytest.mark.special_test
def test_something():
    """
    Special test for XYZ feature
    
    Marker 'special_test' indicates...
    """
    pass
```

---

### 🎯 Framework-Specific Best Practices

#### 1. Multi-Project Testing

Always mark with project:
```python
@pytest.mark.bookslot
@pytest.mark.integration
@pytest.mark.module("booking")
def test_booking():
    pass
```

---

#### 2. AI Features

Mark AI-related tests appropriately:
```python
@pytest.mark.ai_validation
@pytest.mark.skipif(not has_ai_keys(), reason="No AI keys")
def test_ai_feature():
    pass
```

---

#### 3. Performance Tests

Always include:
```python
@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.timeout(300)
@pytest.mark.staging_only
def test_performance():
    pass
```

---

#### 4. Security Tests

Use appropriate markers:
```python
@pytest.mark.security
@pytest.mark.slow
@pytest.mark.staging_only
@pytest.mark.timeout(600)
def test_security_scan():
    pass
```

---

#### 5. Mobile Tests

Include device info in docstring:
```python
@pytest.mark.mobile
@pytest.mark.mobile_testing
def test_mobile():
    """
    Test on iPhone 14 Pro
    - Portrait orientation
    - Touch gestures
    """
    pass
```

---

## 10. MARKER REGISTRATION

### Where to Register

All custom markers must be registered in **pytest.ini** file.

### Current Markers (Already Registered)

```ini
[pytest]
markers =
    # Engine selection markers
    modern_spa: Modern single-page application (Playwright preferred)
    legacy_ui: Legacy user interface (Selenium preferred)
    mobile: Mobile-responsive testing
    api_validation: Requires API validation
    
    # Project markers (implied, add if needed)
    bookslot: BookSlot project tests
    patientintake: PatientIntake project tests
    callcenter: CallCenter project tests
    multi_project: Tests spanning multiple projects
    
    # Module markers
    module: Specify application module (e.g., checkout, admin, dashboard)
    ui_framework: Specify UI framework (e.g., React, Vue, Angular, JSP)
    auth_type: Authentication type (e.g., SSO, MFA, OAuth, Basic)
    
    # Test categories
    smoke: Smoke tests (quick validation)
    regression: Regression test suite
    integration: Integration tests (UI + API + DB)
    ui_only: UI-only tests
    api_only: API-only tests
    db_only: Database-only tests
    
    # Priority markers
    critical: Critical path tests
    high: High priority
    medium: Medium priority
    low: Low priority
    
    # Environment markers
    dev_only: Run only in development
    staging_only: Run only in staging
    prod_safe: Safe to run in production (read-only)
    
    # Special markers
    slow: Slow running tests
    skip_ci: Skip in CI/CD pipeline
    flaky: Known flaky test (needs attention)
    wip: Work in progress
    
    # Framework capability markers
    ai_validation: Uses AI validation features
    ai_engine_selection: Uses AI engine selection
    performance: Performance testing
    visual: Visual regression testing
    accessibility: Accessibility testing
    security: Security testing
    mobile_testing: Mobile device testing
    recording: Test recording and generation
    websocket: WebSocket communication testing
```

### How to Add New Markers

1. **Open pytest.ini**
2. **Find the markers section** under `[pytest]`
3. **Add your marker**:

```ini
[pytest]
markers =
    # ... existing markers ...
    
    # Your new marker
    my_new_marker: Description of what this marker does
```

4. **Run pytest --markers** to verify:

```bash
pytest --markers | grep my_new_marker
```

### Marker Naming Conventions

**Use snake_case**:
- ✅ `mobile_testing`
- ✅ `api_validation`
- ❌ `MobileTesting`
- ❌ `api-validation`

**Be descriptive**:
- ✅ `accessibility_wcag_aa`
- ❌ `a11y`

**Use underscores for multi-word**:
- ✅ `multi_project`
- ❌ `multiproject`

---

## 11. CI/CD INTEGRATION

### GitHub Actions Examples

#### Fast CI Pipeline

```yaml
# .github/workflows/fast-ci.yml
name: Fast CI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run fast tests
        run: |
          pytest -m "(smoke or critical) and not (slow or flaky or skip_ci)" \
            -n auto \
            --html=reports/fast_ci.html \
            --self-contained-html
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: test-report
          path: reports/
```

#### Nightly Full Regression

```yaml
# .github/workflows/nightly.yml
name: Nightly Regression

on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run full regression
        run: |
          pytest -m "regression and not (flaky or wip)" \
            -n auto \
            --html=reports/nightly_regression.html \
            --self-contained-html
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: nightly-report
          path: reports/
```

#### Multi-Stage Pipeline

```yaml
# .github/workflows/multi-stage.yml
name: Multi-Stage Testing

on: [push]

jobs:
  smoke:
    name: Smoke Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest -m "smoke and not flaky" -n auto
  
  integration:
    name: Integration Tests
    needs: smoke
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest -m "integration and critical and not slow" -n auto
  
  full:
    name: Full Regression
    needs: integration
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest -m "regression and not wip" -n auto
```

### Jenkins Examples

#### Jenkinsfile

```groovy
pipeline {
    agent any
    
    stages {
        stage('Fast Tests') {
            steps {
                sh 'pytest -m "smoke and critical and not flaky" -n auto'
            }
        }
        
        stage('Integration Tests') {
            when {
                branch 'develop'
            }
            steps {
                sh 'pytest -m "integration and not slow" -n auto'
            }
        }
        
        stage('Full Regression') {
            when {
                branch 'main'
            }
            steps {
                sh 'pytest -m "regression and not wip" -n auto'
            }
        }
    }
    
    post {
        always {
            publishHTML([
                reportName: 'Test Report',
                reportDir: 'reports',
                reportFiles: '*.html'
            ])
        }
    }
}
```

---

## 12. TROUBLESHOOTING

### Issue 1: "Unknown pytest.mark" Warning

**Warning**:
```
PytestUnknownMarkWarning: Unknown pytest.mark.my_marker
```

**Cause**: Marker not registered in pytest.ini

**Solution**:
1. Open `pytest.ini`
2. Add marker:
```ini
[pytest]
markers =
    my_marker: Description of marker
```

---

### Issue 2: No Tests Collected

**Command**:
```bash
pytest -m some_marker
```

**Result**:
```
collected 0 items
```

**Causes**:
1. No tests have that marker
2. Typo in marker name
3. Marker expression incorrect

**Solutions**:

**Check registered markers**:
```bash
pytest --markers | grep some_marker
```

**Dry run to see what would run**:
```bash
pytest -m some_marker --collect-only
```

**Check test files**:
```bash
grep -r "@pytest.mark.some_marker" tests/
```

---

### Issue 3: Marker Expression Syntax Error

**Error**:
```
ERROR: Wrong expression passed to '-m': <expression>
```

**Cause**: Invalid boolean operator syntax

**Solutions**:

**Use proper operators**:
```bash
# Correct
pytest -m "marker1 and marker2"
pytest -m "marker1 or marker2"
pytest -m "not marker"
pytest -m "(marker1 or marker2) and not marker3"

# Wrong
pytest -m "marker1 & marker2"    # Use 'and'
pytest -m "marker1 | marker2"    # Use 'or'
pytest -m "!marker"              # Use 'not'
```

---

### Issue 4: Marker Not Applied to Test

**Test not running when marker selected**

**Causes**:
1. Decorator syntax error
2. Marker applied after test function
3. Indentation issue in class

**Check**:

**Correct syntax**:
```python
@pytest.mark.smoke  # BEFORE function
def test_feature():
    pass
```

**Wrong syntax**:
```python
def test_feature():
    pass
@pytest.mark.smoke  # AFTER function - won't work!
```

---

### Issue 5: Markers Not Enforced

**Tests run even with unknown markers**

**Cause**: `--strict-markers` not enabled

**Solution**:

Add to pytest.ini:
```ini
[pytest]
addopts = --strict-markers
```

Now unknown markers will cause errors:
```bash
pytest -m unknown_marker
# ERROR: Unknown pytest.mark.unknown_marker
```

---

### Issue 6: Parametrize Not Creating Multiple Tests

**Only 1 test runs instead of multiple**

**Check**:

**Correct**:
```python
@pytest.mark.parametrize("value", [1, 2, 3])
def test_values(value):  # Parameter name matches
    pass
```

**Wrong**:
```python
@pytest.mark.parametrize("value", [1, 2, 3])
def test_values():  # No parameter - won't work!
    pass
```

---

### Issue 7: skipif Condition Not Working

**Test runs when it should be skipped**

**Debug**:

```python
import sys
print(sys.version_info)  # Check actual version

@pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="Requires Python 3.11+"
)
def test_feature():
    pass
```

---

### Issue 8: Class Markers Not Inherited

**Test methods don't have class markers**

**Check indentation**:

**Correct**:
```python
@pytest.mark.regression
class TestFeatures:
    def test_one(self):  # Has regression marker
        pass
```

**Wrong**:
```python
@pytest.mark.regression
class TestFeatures:
pass  # Wrong indentation!

def test_one(self):  # No regression marker!
    pass
```

---

## 13. QUICK REFERENCE

### Command Cheat Sheet

| Command | Description |
|---------|-------------|
| `pytest -m marker` | Run tests with marker |
| `pytest -m "m1 and m2"` | Both markers required |
| `pytest -m "m1 or m2"` | Either marker |
| `pytest -m "not m"` | Exclude marker |
| `pytest -m "(m1 or m2) and not m3"` | Complex expression |
| `pytest --markers` | List all registered markers |
| `pytest -m marker --collect-only` | Show which tests would run |
| `pytest -m marker -v` | Verbose output |
| `pytest -m marker --html=report.html` | With HTML report |
| `pytest -m marker -k "keyword"` | Combine with keyword |
| `pytest -m marker -x` | Stop on first failure |
| `pytest -m marker -n auto` | Parallel execution |

### Marker Syntax Cheat Sheet

| Syntax | Example |
|--------|---------|
| Single marker | `@pytest.mark.smoke` |
| Multiple markers | `@pytest.mark.smoke`<br>`@pytest.mark.critical` |
| Marker with parameter | `@pytest.mark.module("admin")` |
| Apply to class | `@pytest.mark.regression`<br>`class TestSuite:` |
| Apply to module | `pytestmark = pytest.mark.integration` |
| Parametrize | `@pytest.mark.parametrize("x", [1,2,3])` |
| Skip | `@pytest.mark.skip(reason="...")` |
| Conditional skip | `@pytest.mark.skipif(condition, reason="...")` |
| Expected fail | `@pytest.mark.xfail(reason="...")` |
| Timeout | `@pytest.mark.timeout(60)` |

### Common Marker Combinations

| Use Case | Command |
|----------|---------|
| **Pre-deployment** | `pytest -m "smoke and critical and not flaky"` |
| **Full project** | `pytest -m "bookslot and regression"` |
| **API only** | `pytest -m "api_only or api_validation"` |
| **Production safe** | `pytest -m "prod_safe and smoke"` |
| **CI/CD fast** | `pytest -m "(smoke or critical) and not (slow or skip_ci)"` |
| **Nightly** | `pytest -m "regression and not (flaky or wip)"` |
| **Mobile** | `pytest -m "mobile and not slow"` |
| **Security** | `pytest -m "security and staging_only"` |

### Framework-Specific Markers

| Category | Markers |
|----------|---------|
| **Projects** | `bookslot`, `patientintake`, `callcenter`, `multi_project` |
| **Engine** | `modern_spa`, `legacy_ui`, `mobile`, `api_validation` |
| **Categories** | `smoke`, `regression`, `integration`, `ui_only`, `api_only`, `db_only` |
| **Priority** | `critical`, `high`, `medium`, `low` |
| **Environment** | `dev_only`, `staging_only`, `prod_safe` |
| **Special** | `slow`, `skip_ci`, `flaky`, `wip` |
| **Capabilities** | `performance`, `visual`, `accessibility`, `security`, `mobile_testing`, `ai_validation` |

---

## 📞 SUPPORT & CONTACT

**Author**: Lokendra Singh  
**Email**: qa.lokendra@gmail.com  
**Website**: www.sqamentor.com

**Framework**: Enterprise-Grade Hybrid Automation Framework  
**Version**: 2.0  
**Documentation**: Complete

---

## 🎉 CONCLUSION

This comprehensive guide covers **everything** about pytest markers in the context of this enterprise automation framework:

✅ **40+ Custom Markers** - All framework capabilities covered  
✅ **Built-in Markers** - Complete pytest marker reference  
✅ **Real Examples** - 10 complete test examples from the framework  
✅ **Best Practices** - DO's and DON'Ts for effective marker usage  
✅ **CI/CD Integration** - Ready-to-use pipeline configurations  
✅ **Troubleshooting** - Solutions to common issues  

**Use this guide** to master test selection, organization, and execution in your framework!

---

**Last Updated**: January 27, 2026  
**Status**: ✅ Complete and Production-Ready
