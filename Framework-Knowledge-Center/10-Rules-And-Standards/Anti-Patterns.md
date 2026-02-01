# Anti-Patterns - What NOT To Do

## ⚠️ WARNING

**These are FORBIDDEN patterns that will cause:**
- ❌ Pre-commit hook failures
- ❌ CI/CD build failures  
- ❌ PR merge blocks
- ❌ Architecture audit violations
- ❌ Technical debt accumulation

**Avoid these patterns at all costs!**

---

## 📋 Categories

1. [Page Object Anti-Patterns](#1-page-object-anti-patterns)
2. [Test Structure Anti-Patterns](#2-test-structure-anti-patterns)
3. [Delay & Timing Anti-Patterns](#3-delay--timing-anti-patterns)
4. [Data Management Anti-Patterns](#4-data-management-anti-patterns)
5. [Engine Selection Anti-Patterns](#5-engine-selection-anti-patterns)
6. [Configuration Anti-Patterns](#6-configuration-anti-patterns)
7. [Error Handling Anti-Patterns](#7-error-handling-anti-patterns)
8. [Performance Anti-Patterns](#8-performance-anti-patterns)

---

## 1. Page Object Anti-Patterns

### ❌ Anti-Pattern 1.1: Direct Locators in Tests

**DON'T DO THIS:**
```python
def test_login(page: Page):
    # ❌ Direct locator usage
    page.locator("#username").fill("test@example.com")
    page.locator("#password").fill("password123")
    page.locator("button[type='submit']").click()
    assert page.locator(".dashboard").is_visible()
```

**WHY IT'S BAD:**
- Locators scattered across multiple tests
- Hard to maintain (change one locator = update all tests)
- Violates DRY principle
- No abstraction layer
- Tests break when UI changes

**DO THIS INSTEAD:**
```python
def test_login(page: Page):
    # ✅ Use Page Object
    login_page = LoginPage(page)
    login_page.fill_username("test@example.com")\
              .fill_password("password123")\
              .click_submit()
    assert login_page.is_dashboard_visible()
```

---

### ❌ Anti-Pattern 1.2: Assertions in Page Objects

**DON'T DO THIS:**
```python
class LoginPage:
    def verify_login_success(self):
        # ❌ Assertion in page object
        assert self.page.locator(".dashboard").is_visible()
        assert "Dashboard" in self.page.title()
```

**WHY IT'S BAD:**
- Violates single responsibility principle
- Page objects should describe UI, not test logic
- Makes page objects less reusable
- Hard to use conditionally

**DO THIS INSTEAD:**
```python
class LoginPage:
    def is_login_successful(self) -> bool:
        # ✅ Return boolean
        return self.page.locator(".dashboard").is_visible()

# In test
def test_login(page: Page):
    login_page = LoginPage(page)
    # ... login ...
    assert login_page.is_login_successful()  # ✅ Assert in test
```

---

### ❌ Anti-Pattern 1.3: Pytest Imports in Page Objects

**DON'T DO THIS:**
```python
# pages/login_page.py
import pytest  # ❌ FORBIDDEN

class LoginPage:
    @pytest.fixture  # ❌ NO fixtures in pages
    def login_data(self):
        return {"user": "test"}
```

**WHY IT'S BAD:**
- Page objects are not test logic
- Violates separation of concerns
- Creates tight coupling to test framework
- Prevents page object reuse

**DO THIS INSTEAD:**
```python
# pages/login_page.py
# ✅ No pytest imports

class LoginPage:
    def __init__(self, page):
        self.page = page

# conftest.py
@pytest.fixture  # ✅ Fixtures belong here
def login_data():
    return {"user": "test"}
```

---

### ❌ Anti-Pattern 1.4: Inline Locators (Not Properties)

**DON'T DO THIS:**
```python
class LoginPage:
    def fill_username(self, username: str):
        # ❌ Inline locator
        self.page.locator("#username").fill(username)
    
    def fill_password(self, password: str):
        # ❌ Inline locator (duplicate)
        self.page.locator("#username").fill(password)  # Oops! Copy-paste error
```

**WHY IT'S BAD:**
- Locators duplicated across methods
- Easy copy-paste errors (as shown)
- Hard to maintain (update locator = update all methods)
- Can't reuse locators

**DO THIS INSTEAD:**
```python
class LoginPage:
    @property
    def username_field(self):
        # ✅ Centralized locator
        return self.page.locator("#username")
    
    @property
    def password_field(self):
        return self.page.locator("#password")
    
    def fill_username(self, username: str):
        self.username_field.fill(username)  # ✅ Uses property
    
    def fill_password(self, password: str):
        self.password_field.fill(password)  # ✅ Uses property
```

---

### ❌ Anti-Pattern 1.5: Not Returning self (No Method Chaining)

**DON'T DO THIS:**
```python
class LoginPage:
    def fill_username(self, username: str):
        self.username_field.fill(username)
        # ❌ No return self

# Usage - Verbose
login_page = LoginPage(page)
login_page.fill_username("test@example.com")
login_page.fill_password("password123")
login_page.click_submit()
```

**WHY IT'S BAD:**
- Verbose, repetitive code
- Doesn't support fluent API
- Less readable

**DO THIS INSTEAD:**
```python
class LoginPage:
    def fill_username(self, username: str):
        self.username_field.fill(username)
        return self  # ✅ Enable chaining
    
    def fill_password(self, password: str):
        self.password_field.fill(password)
        return self  # ✅ Enable chaining

# Usage - Clean chaining
login_page = LoginPage(page)
login_page.fill_username("test@example.com")\
          .fill_password("password123")\
          .click_submit()
```

---

## 2. Test Structure Anti-Patterns

### ❌ Anti-Pattern 2.1: God Tests (Testing Everything)

**DON'T DO THIS:**
```python
def test_entire_application(page: Page):
    """❌ Tests everything in one giant test"""
    # Login
    page.goto("/login")
    page.locator("#username").fill("test")
    page.locator("#password").fill("pass")
    page.locator("#submit").click()
    assert page.locator(".dashboard").is_visible()
    
    # Create item
    page.locator("#new-item").click()
    page.locator("#item-name").fill("Test Item")
    page.locator("#save").click()
    assert page.locator(".success").is_visible()
    
    # Edit item
    page.locator(".edit-btn").click()
    page.locator("#item-name").fill("Updated Item")
    page.locator("#save").click()
    assert page.locator(".success").is_visible()
    
    # Delete item
    page.locator(".delete-btn").click()
    page.locator("#confirm").click()
    assert page.locator(".item-deleted").is_visible()
    
    # Logout
    page.locator("#logout").click()
    assert page.url == "/login"
```

**WHY IT'S BAD:**
- Hard to debug (which part failed?)
- Long execution time
- Brittle (any failure fails entire test)
- Hard to maintain
- Poor test isolation

**DO THIS INSTEAD:**
```python
# ✅ Split into focused tests

def test_login_with_valid_credentials_shows_dashboard(page: Page):
    """Test login only"""
    login_page = LoginPage(page)
    login_page.login("test", "pass")
    assert login_page.is_dashboard_visible()

def test_create_item_with_valid_data_shows_success(page: Page):
    """Test item creation only"""
    # Setup: assume logged in
    item_page = ItemPage(page)
    item_page.create_item("Test Item")
    assert item_page.is_success_message_visible()

def test_edit_item_with_new_name_updates_item(page: Page):
    """Test item editing only"""
    # Setup: assume item exists
    item_page = ItemPage(page)
    item_page.edit_item("Updated Item")
    assert item_page.is_success_message_visible()
```

---

### ❌ Anti-Pattern 2.2: Poorly Named Tests

**DON'T DO THIS:**
```python
def test_1(page: Page):  # ❌ What does this test?
    pass

def test_booking(page: Page):  # ❌ Too vague
    pass

def test(page: Page):  # ❌ Extremely vague
    pass

def test_123(page: Page):  # ❌ Non-descriptive
    pass
```

**WHY IT'S BAD:**
- Impossible to understand what test does
- Hard to find related tests
- Poor documentation value
- Difficult test failure analysis

**DO THIS INSTEAD:**
```python
def test_booking_with_valid_data_creates_appointment(page: Page):
    """✅ Clear what test does"""
    pass

def test_booking_with_invalid_email_shows_error(page: Page):
    """✅ Clear test scenario"""
    pass

def test_booking_form_validates_required_fields(page: Page):
    """✅ Descriptive and specific"""
    pass
```

**Pattern:** `test_<action>_<condition>_<expected_result>`

---

### ❌ Anti-Pattern 2.3: Assertions Mixed with Actions

**DON'T DO THIS:**
```python
def test_booking_flow(page: Page):
    # ❌ Mixed arrange/act/assert
    page.goto("/booking")
    
    page.locator("#name").fill("John")
    assert page.locator("#name").input_value() == "John"  # ❌ Early assert
    
    page.locator("#email").fill("john@test.com")
    assert page.locator("#email").input_value() == "john@test.com"  # ❌ Early assert
    
    page.locator("#submit").click()
    assert page.locator(".success").is_visible()  # ❌ Mixed with actions
```

**WHY IT'S BAD:**
- Hard to read (what's being tested?)
- Violates AAA pattern
- Test fails early (doesn't complete flow)
- Poor test structure

**DO THIS INSTEAD:**
```python
def test_booking_flow(page: Page, fake_bookslot_data):
    # ✅ AAA Pattern
    
    # ARRANGE
    booking_page = BookingPage(page)
    test_data = fake_bookslot_data
    
    # ACT
    booking_page.fill_name(test_data['name'])\
                .fill_email(test_data['email'])\
                .click_submit()
    
    # ASSERT
    assert booking_page.is_success_message_visible()
    assert booking_page.get_confirmation_id() is not None
```

---

## 3. Delay & Timing Anti-Patterns

### ❌ Anti-Pattern 3.1: Manual time.sleep() Calls

**DON'T DO THIS:**
```python
import time

def test_booking(page: Page):
    page.locator("#submit").click()
    time.sleep(2)  # ❌ Manual delay
    
    page.locator("#name").fill("John")
    time.sleep(1)  # ❌ Manual delay
    
    page.locator("#next").click()
    time.sleep(3)  # ❌ Manual delay
```

**WHY IT'S BAD:**
- Brittle (fixed delays don't adapt to conditions)
- Slow (always waits full duration)
- Hard to maintain (delays scattered everywhere)
- No human behavior simulation

**DO THIS INSTEAD:**
```python
def test_booking(page: Page, smart_actions):
    # ✅ Use SmartActions (automatic delays)
    smart_actions.button_click(page.locator("#submit"), "Submit")
    smart_actions.type_text(page.locator("#name"), "John", "Name Field")
    smart_actions.click(page.locator("#next"), "Next Button")
    # Delays automatic and context-aware
```

---

### ❌ Anti-Pattern 3.2: Arbitrary Wait Times

**DON'T DO THIS:**
```python
import time

def test_page_load(page: Page):
    page.goto("https://example.com")
    time.sleep(5)  # ❌ Why 5? Why not 3 or 10?
    
    page.locator("#element").click()
    time.sleep(2)  # ❌ Arbitrary
```

**WHY IT'S BAD:**
- Magic numbers (no explanation)
- May be too short (flaky tests)
- May be too long (slow tests)
- Doesn't wait for actual condition

**DO THIS INSTEAD:**
```python
def test_page_load(page: Page):
    # ✅ Wait for specific condition
    page.goto("https://example.com")
    page.wait_for_load_state("networkidle")  # ✅ Explicit condition
    
    # ✅ Or use Playwright auto-waiting
    page.locator("#element").click()  # Auto-waits for element
```

---

## 4. Data Management Anti-Patterns

### ❌ Anti-Pattern 4.1: Hardcoded Test Data

**DON'T DO THIS:**
```python
def test_registration(page: Page):
    # ❌ Hardcoded data
    page.locator("#name").fill("John Doe")
    page.locator("#email").fill("john@example.com")
    page.locator("#phone").fill("1234567890")
    page.locator("#dob").fill("01/01/1990")
```

**WHY IT'S BAD:**
- Not reusable
- Data conflicts in parallel tests
- Hard to update
- No variety in test data

**DO THIS INSTEAD:**
```python
def test_registration(page: Page, fake_bookslot_data):
    # ✅ Use fixture data
    registration_page = RegistrationPage(page)
    registration_page.fill_name(fake_bookslot_data['first_name'])\
                     .fill_email(fake_bookslot_data['email'])\
                     .fill_phone(fake_bookslot_data['phone_number'])\
                     .fill_dob(fake_bookslot_data['dob'])
```

---

### ❌ Anti-Pattern 4.2: Shared Mutable Test Data

**DON'T DO THIS:**
```python
# ❌ Shared mutable data
SHARED_DATA = {
    "email": "test@example.com",
    "name": "John Doe"
}

def test_registration_1(page: Page):
    # Uses SHARED_DATA
    page.locator("#email").fill(SHARED_DATA["email"])
    SHARED_DATA["email"] = "modified@example.com"  # ❌ Mutates shared data

def test_registration_2(page: Page):
    # Uses modified data! ❌
    page.locator("#email").fill(SHARED_DATA["email"])
```

**WHY IT'S BAD:**
- Test order dependency
- Parallel test conflicts
- Unpredictable results
- Hard to debug

**DO THIS INSTEAD:**
```python
# ✅ Generate fresh data per test
@pytest.fixture
def registration_data():
    """Fresh data for each test"""
    return generate_bookslot_payload()  # New data each time

def test_registration_1(page: Page, registration_data):
    # Uses fresh data ✅
    page.locator("#email").fill(registration_data["email"])

def test_registration_2(page: Page, registration_data):
    # Uses fresh data ✅ (different from test_1)
    page.locator("#email").fill(registration_data["email"])
```

---

## 5. Engine Selection Anti-Patterns

### ❌ Anti-Pattern 5.1: Mixing Playwright and Selenium

**DON'T DO THIS:**
```python
from playwright.sync_api import Page
from selenium.webdriver import Remote

def test_booking_mixed(page: Page, driver: Remote):
    # ❌ Using both engines
    page.goto("https://bookslot.com")  # Playwright
    driver.get("https://bookslot.com")  # Selenium ❌ FORBIDDEN
```

**WHY IT'S BAD:**
- Engine conflicts
- Resource waste (two browsers)
- Performance issues
- Unpredictable behavior

**DO THIS INSTEAD:**
```python
# ✅ Use ONE engine per test

@pytest.mark.playwright
def test_booking_playwright(page: Page):
    # Playwright only
    page.goto("https://bookslot.com")

@pytest.mark.selenium  
def test_booking_selenium(driver: Remote):
    # Selenium only
    driver.get("https://bookslot.com")
```

---

### ❌ Anti-Pattern 5.2: Forcing Engine Without Markers

**DON'T DO THIS:**
```python
def test_booking(page: Page):
    # ❌ No marker - engine unclear
    page.goto("https://bookslot.com")
```

**WHY IT'S BAD:**
- Engine selector can't determine engine
- Test may use wrong engine
- Hard to filter tests by engine
- Poor organization

**DO THIS INSTEAD:**
```python
@pytest.mark.playwright  # ✅ Clear marker
@pytest.mark.bookslot
def test_booking(page: Page):
    page.goto("https://bookslot.com")
```

---

## 6. Configuration Anti-Patterns

### ❌ Anti-Pattern 6.1: Hardcoded Secrets

**DON'T DO THIS:**
```python
def test_api_call():
    # ❌ CRITICAL SECURITY VIOLATION
    api_key = "sk-1234567890abcdef"  # ❌ Hardcoded secret
    db_password = "my_secret_password"  # ❌ Hardcoded secret
```

**WHY IT'S BAD:**
- **SECURITY RISK** (secrets in git history)
- Can't change without code change
- Different secrets for different environments
- Compliance violations

**DO THIS INSTEAD:**
```python
import os

def test_api_call():
    # ✅ Load from environment
    api_key = os.getenv("OPENAI_API_KEY")
    db_password = os.getenv("DATABASE_PASSWORD")
    
    # Or use settings
    from config.settings import settings
    api_key = settings.openai_api_key
```

---

### ❌ Anti-Pattern 6.2: Hardcoded Environments

**DON'T DO THIS:**
```python
def test_booking(page: Page):
    # ❌ Hardcoded production URL
    page.goto("https://production.bookslot.com")
```

**WHY IT'S BAD:**
- Can't run against different environments
- Risk of hitting production in tests
- Hard to switch environments

**DO THIS INSTEAD:**
```python
def test_booking(page: Page, base_url):
    # ✅ Use fixture (configurable via CLI)
    page.goto(f"{base_url}/booking")

# Run with: pytest --env=staging
# Or:       pytest --env=production
```

---

## 7. Error Handling Anti-Patterns

### ❌ Anti-Pattern 7.1: Bare except Blocks

**DON'T DO THIS:**
```python
def test_booking(page: Page):
    try:
        page.locator("#submit").click()
    except:  # ❌ Catches everything, even KeyboardInterrupt
        pass  # ❌ Silently swallows error
```

**WHY IT'S BAD:**
- Hides real errors
- Catches system exceptions (KeyboardInterrupt, SystemExit)
- Makes debugging impossible
- Tests pass when they should fail

**DO THIS INSTEAD:**
```python
def test_booking(page: Page):
    try:
        page.locator("#submit").click()
    except TimeoutError as e:  # ✅ Specific exception
        pytest.fail(f"Submit button not found: {e}")  # ✅ Explicit failure
```

---

### ❌ Anti-Pattern 7.2: Ignoring Test Failures

**DON'T DO THIS:**
```python
@pytest.mark.xfail  # ❌ Marking test as expected to fail
def test_broken_feature(page: Page):
    # This test is broken but we don't want to fix it
    pass

@pytest.mark.skip(reason="Flaky test")  # ❌ Skipping without fixing
def test_flaky_test(page: Page):
    pass
```

**WHY IT'S BAD:**
- Tests rot (never get fixed)
- Real bugs hidden
- False sense of test coverage
- Technical debt accumulates

**DO THIS INSTEAD:**
```python
def test_feature(page: Page):
    # ✅ Fix the test or file issue
    # Don't mark as xfail/skip without plan to fix
    pass

# If genuinely flaky, add retry:
@pytest.mark.flaky(reruns=3)  # ✅ Retry instead of skip
def test_sometimes_flaky(page: Page):
    pass
```

---

## 8. Performance Anti-Patterns

### ❌ Anti-Pattern 8.1: No Parallelization

**DON'T DO THIS:**
```bash
# ❌ Run tests sequentially (slow)
pytest tests/

# 100 tests × 10 seconds each = 1000 seconds (16 minutes)
```

**WHY IT'S BAD:**
- Slow feedback
- Wastes CI/CD time
- Developer productivity loss

**DO THIS INSTEAD:**
```bash
# ✅ Run tests in parallel
pytest tests/ -n 4  # 4 workers

# 100 tests ÷ 4 workers = 250 seconds (4 minutes)
```

---

### ❌ Anti-Pattern 8.2: Full Browser for API Tests

**DON'T DO THIS:**
```python
def test_api_endpoint(page: Page):
    # ❌ Using full browser for API test
    page.goto("https://api.example.com/endpoint")
    response_text = page.locator("pre").text_content()
    assert "success" in response_text
```

**WHY IT'S BAD:**
- Slow (browser overhead)
- Unnecessary (API doesn't need browser)
- Resource waste

**DO THIS INSTEAD:**
```python
def test_api_endpoint(api_client):
    # ✅ Direct API call (fast)
    response = api_client.get("/endpoint")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

---

## 🔥 Most Dangerous Anti-Patterns

| Anti-Pattern | Severity | Impact |
|--------------|----------|--------|
| Hardcoded secrets | CRITICAL | Security breach |
| Bare except blocks | HIGH | Hides bugs |
| Mixing engines | HIGH | Test failures |
| God tests | HIGH | Maintenance nightmare |
| Manual sleeps | MEDIUM | Slow, flaky tests |
| Hardcoded data | MEDIUM | Data conflicts |
| Direct locators | MEDIUM | Brittle tests |

---

## ✅ Quick Fixes Reference

| Anti-Pattern | Quick Fix |
|--------------|-----------|
| Direct locators → | Use Page Objects |
| Manual sleeps → | Use SmartActions |
| Hardcoded data → | Use fixtures |
| God tests → | Split into focused tests |
| Bare except → | Catch specific exceptions |
| Mixing engines → | Use ONE engine per test |
| Hardcoded secrets → | Use .env file |

---

## 📚 Related Documentation

- [Strict Rules](Strict-Rules.md) - Mandatory rules
- [Common Mistakes](Common-Mistakes.md) - Frequent errors
- [Best Practices](Best-Practices.md) - Recommended patterns
- [POM Architecture](../03-Page-Object-Model/POM-Architecture.md)
- [Smart Actions](../02-Core-Concepts/Smart-Actions.md)

---

**Last Updated:** February 1, 2026  
**Version:** 1.0.0

---

**⚠️ "Learn from others' mistakes. Avoid these anti-patterns!"**
