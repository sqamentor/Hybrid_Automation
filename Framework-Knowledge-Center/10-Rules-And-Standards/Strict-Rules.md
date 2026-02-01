# Strict Rules - MUST FOLLOW

## ⚠️ CRITICAL NOTICE

**These rules are MANDATORY and AUTOMATICALLY ENFORCED by the framework's governance system.**

Violations will:
- ❌ **BLOCK git commits** (pre-commit hooks)
- ❌ **FAIL CI/CD builds** (GitHub Actions)
- ❌ **BLOCK pull request merges** (status checks)
- ❌ **Trigger audit reports** (file watcher)

**There are NO EXCEPTIONS unless explicitly baselined with expiration date.**

---

## 📋 Table of Contents

1. [Page Object Model (POM) Rules](#1-page-object-model-pom-rules)
2. [Engine Mixing Rules](#2-engine-mixing-rules)
3. [Test Structure Rules](#3-test-structure-rules)
4. [Human Behavior Rules](#4-human-behavior-rules)
5. [Data Management Rules](#5-data-management-rules)
6. [Import Rules](#6-import-rules)
7. [Naming Conventions](#7-naming-conventions)
8. [Marker Rules](#8-marker-rules)
9. [Execution Flow Rules](#9-execution-flow-rules)
10. [Configuration Rules](#10-configuration-rules)

---

## 1. Page Object Model (POM) Rules

### Rule 1.1: All UI Interactions MUST Use Page Objects

✅ **CORRECT:**
```python
# Test file: tests/bookslot/test_booking.py
from pages.bookslot.bookslots_basicinfo_page1 import BookslotBasicInfoPage

def test_fill_basic_info(page: Page, fake_bookslot_data):
    basic_info_page = BookslotBasicInfoPage(page)
    basic_info_page.fill_first_name(fake_bookslot_data['first_name'])
    basic_info_page.fill_email(fake_bookslot_data['email'])
    basic_info_page.click_next()
```

❌ **WRONG:**
```python
# Direct locators in test - FORBIDDEN
def test_fill_basic_info(page: Page, fake_bookslot_data):
    page.locator("#firstName").fill(fake_bookslot_data['first_name'])  # ❌ VIOLATION
    page.locator("#email").fill(fake_bookslot_data['email'])  # ❌ VIOLATION
    page.locator("#nextBtn").click()  # ❌ VIOLATION
```

**Enforcement:**
- **Rule ID:** `pom/direct-locator-in-test`
- **Severity:** ERROR
- **Detection:** AST analysis, regex pattern matching
- **Auto-fix:** Not available (requires manual POM creation)

---

### Rule 1.2: Page Objects MUST NOT Import pytest

✅ **CORRECT:**
```python
# pages/bookslot/bookslots_basicinfo_page1.py
from playwright.sync_api import Page

class BookslotBasicInfoPage:
    def __init__(self, page: Page):
        self.page = page
    
    def fill_first_name(self, name: str):
        self.page.locator("#firstName").fill(name)
```

❌ **WRONG:**
```python
# Page object with pytest import - FORBIDDEN
import pytest  # ❌ VIOLATION

class BookslotBasicInfoPage:
    def __init__(self, page: Page):
        self.page = page
    
    @pytest.fixture  # ❌ Page objects should not have fixtures
    def some_method(self):
        pass
```

**Enforcement:**
- **Rule ID:** `pom/forbidden-import`
- **Severity:** ERROR
- **Detection:** Import statement analysis
- **Auto-fix:** Remove import statement

**Why:** Page objects are pure interaction models, not test logic. Pytest is test framework, belongs only in test files.

---

### Rule 1.3: Page Objects MUST NOT Contain Assertions

✅ **CORRECT:**
```python
# Page Object - Actions only
class BookslotBasicInfoPage:
    def is_error_displayed(self) -> bool:
        """Return boolean, let test assert"""
        return self.page.locator(".error-message").is_visible()

# Test - Assertions here
def test_validation_error(page: Page):
    basic_info_page = BookslotBasicInfoPage(page)
    assert basic_info_page.is_error_displayed()  # ✅ Assert in test
```

❌ **WRONG:**
```python
# Page Object with assertion - FORBIDDEN
class BookslotBasicInfoPage:
    def verify_error_displayed(self):
        assert self.page.locator(".error-message").is_visible()  # ❌ VIOLATION
```

**Enforcement:**
- **Rule ID:** `pom/assertion-in-page`
- **Severity:** ERROR
- **Detection:** `assert` keyword in page object methods
- **Auto-fix:** Not available (requires refactoring)

**Why:** Separation of concerns. Page objects = interactions. Tests = assertions.

---

### Rule 1.4: Locators MUST Be Defined as Properties

✅ **CORRECT:**
```python
class BookslotBasicInfoPage:
    @property
    def first_name_field(self):
        return self.page.locator("#firstName")
    
    @property
    def email_field(self):
        return self.page.locator("#email")
    
    def fill_first_name(self, name: str):
        self.first_name_field.fill(name)  # Uses property
```

❌ **WRONG:**
```python
class BookslotBasicInfoPage:
    def fill_first_name(self, name: str):
        self.page.locator("#firstName").fill(name)  # ❌ Inline locator
```

**Enforcement:**
- **Rule ID:** `pom/locator-not-property`
- **Severity:** WARNING
- **Detection:** Locator calls not wrapped in @property
- **Auto-fix:** Not available (requires refactoring)

**Why:** Centralized locator management, easier maintenance, DRY principle.

---

### Rule 1.5: Page Object Methods MUST Return `self` for Chaining

✅ **CORRECT:**
```python
class BookslotBasicInfoPage:
    def fill_first_name(self, name: str):
        self.first_name_field.fill(name)
        return self  # ✅ Enable chaining
    
    def fill_email(self, email: str):
        self.email_field.fill(email)
        return self  # ✅ Enable chaining

# Usage - Method chaining
basic_info_page.fill_first_name("John").fill_email("john@example.com")
```

❌ **WRONG:**
```python
class BookslotBasicInfoPage:
    def fill_first_name(self, name: str):
        self.first_name_field.fill(name)
        # ❌ No return self

# Usage - Verbose
basic_info_page.fill_first_name("John")
basic_info_page.fill_email("john@example.com")
```

**Enforcement:**
- **Rule ID:** `pom/no-method-chaining`
- **Severity:** WARNING
- **Detection:** Methods not returning `self`
- **Auto-fix:** Add `return self` statement

---

## 2. Engine Mixing Rules

### Rule 2.1: ONE Engine Per Test

✅ **CORRECT:**
```python
# Playwright test
from playwright.sync_api import Page

@pytest.mark.playwright
def test_booking_playwright(page: Page):
    page.goto("https://bookslot.com")
    # ... Playwright code only
```

```python
# Selenium test (separate file or clearly separated)
from selenium.webdriver import Remote

@pytest.mark.selenium
def test_booking_selenium(driver: Remote):
    driver.get("https://bookslot.com")
    # ... Selenium code only
```

❌ **WRONG:**
```python
# Mixing engines in same test - FORBIDDEN
from playwright.sync_api import Page
from selenium.webdriver import Remote  # ❌ VIOLATION

def test_booking_mixed(page: Page, driver: Remote):
    page.goto("https://bookslot.com")  # Playwright
    driver.get("https://bookslot.com")  # ❌ Selenium (VIOLATION)
```

**Enforcement:**
- **Rule ID:** `engine/mixing-in-test`
- **Severity:** ERROR
- **Detection:** Import analysis, AST scanning
- **Auto-fix:** Not available (requires test refactoring)

**Why:** Engine mixing causes conflicts, performance issues, and unpredictable behavior.

---

### Rule 2.2: Test Markers MUST Match Engine

✅ **CORRECT:**
```python
@pytest.mark.playwright  # ✅ Marker matches engine
def test_with_playwright(page: Page):
    # Uses Playwright
    pass

@pytest.mark.selenium  # ✅ Marker matches engine
def test_with_selenium(driver: Remote):
    # Uses Selenium
    pass
```

❌ **WRONG:**
```python
@pytest.mark.selenium  # ❌ Wrong marker
def test_with_playwright(page: Page):
    # Actually uses Playwright - VIOLATION
    pass
```

**Enforcement:**
- **Rule ID:** `engine/marker-mismatch`
- **Severity:** ERROR
- **Detection:** Marker vs import analysis
- **Auto-fix:** Suggest correct marker

---

### Rule 2.3: Folder Structure MUST Reflect Engine

```
tests/
├── bookslot/
│   ├── playwright/         # ✅ Playwright tests here
│   │   └── test_modern_booking.py
│   └── selenium/           # ✅ Selenium tests here
│       └── test_legacy_booking.py
```

❌ **WRONG:**
```
tests/
├── bookslot/
│   └── test_booking.py     # ❌ Engine unclear from path
```

**Enforcement:**
- **Rule ID:** `folder/engine-separation`
- **Severity:** WARNING
- **Detection:** File path analysis
- **Auto-fix:** Not available (requires file move)

---

## 3. Test Structure Rules

### Rule 3.1: Follow AAA Pattern (Arrange, Act, Assert)

✅ **CORRECT:**
```python
def test_booking_flow(page: Page, fake_bookslot_data):
    # ARRANGE - Setup
    basic_info_page = BookslotBasicInfoPage(page)
    test_data = fake_bookslot_data
    
    # ACT - Execute
    basic_info_page.fill_basic_info(
        test_data['first_name'],
        test_data['email']
    )
    basic_info_page.click_next()
    
    # ASSERT - Verify
    assert page.locator(".event-info-page").is_visible()
```

❌ **WRONG:**
```python
def test_booking_flow(page: Page, fake_bookslot_data):
    # ❌ Mixed arrange/act/assert - Hard to read
    basic_info_page = BookslotBasicInfoPage(page)
    basic_info_page.fill_first_name(fake_bookslot_data['first_name'])
    assert page.locator("#firstName").input_value() == fake_bookslot_data['first_name']
    basic_info_page.fill_email(fake_bookslot_data['email'])
    basic_info_page.click_next()
    assert page.locator(".event-info-page").is_visible()
```

**Enforcement:**
- **Rule ID:** `test/aaa-pattern`
- **Severity:** WARNING
- **Detection:** Heuristic analysis (assertions mixed with actions)
- **Auto-fix:** Not available

---

### Rule 3.2: Test Names MUST Be Descriptive

✅ **CORRECT:**
```python
def test_booking_flow_with_valid_data_shows_success_page(page: Page):
    """Test that completing booking with valid data shows success page"""
    pass

def test_booking_flow_with_invalid_email_shows_error(page: Page):
    """Test that invalid email shows error message"""
    pass
```

❌ **WRONG:**
```python
def test_1(page: Page):  # ❌ Non-descriptive
    pass

def test_booking(page: Page):  # ❌ Too vague
    pass

def test(page: Page):  # ❌ Extremely vague
    pass
```

**Enforcement:**
- **Rule ID:** `test/naming-convention`
- **Severity:** WARNING
- **Detection:** Test name length, keyword analysis
- **Auto-fix:** Not available

**Pattern:** `test_<action>_<condition>_<expected_result>`

---

### Rule 3.3: One Logical Assertion Per Test (or Grouped)

✅ **CORRECT:**
```python
def test_successful_booking_shows_confirmation(page: Page):
    """Test single logical outcome"""
    # ... booking flow ...
    
    # Grouped related assertions
    assert page.locator(".success-message").is_visible()
    assert "Booking Confirmed" in page.locator(".success-message").text_content()
    assert page.locator(".confirmation-id").is_visible()
```

❌ **WRONG:**
```python
def test_entire_booking_flow(page: Page):
    """God test - tests everything"""
    # ... basic info page ...
    assert page.locator(".basic-info-page").is_visible()  # ❌
    
    # ... event info page ...
    assert page.locator(".event-info-page").is_visible()  # ❌
    
    # ... insurance page ...
    assert page.locator(".insurance-page").is_visible()  # ❌
    
    # ... success page ...
    assert page.locator(".success-page").is_visible()  # ❌
    # ❌ Too many unrelated assertions - split into multiple tests
```

**Enforcement:**
- **Rule ID:** `test/too-many-assertions`
- **Severity:** WARNING
- **Detection:** Assert count > 5
- **Auto-fix:** Not available

---

## 4. Human Behavior Rules

### Rule 4.1: Use SmartActions, Never Manual time.sleep()

✅ **CORRECT:**
```python
def test_booking(page: Page, smart_actions):
    smart_actions.type_text(page.locator("#email"), "test@example.com")
    smart_actions.button_click(page.locator("#submit"), "Submit")
    # ✅ Delays automatic
```

❌ **WRONG:**
```python
import time

def test_booking(page: Page):
    page.locator("#email").fill("test@example.com")
    time.sleep(2)  # ❌ VIOLATION - Manual delay
    page.locator("#submit").click()
    time.sleep(3)  # ❌ VIOLATION - Manual delay
```

**Enforcement:**
- **Rule ID:** `delay/manual-sleep`
- **Severity:** ERROR
- **Detection:** `time.sleep()` in test files
- **Auto-fix:** Suggest SmartActions usage

**Exceptions:**
- Allowed in `conftest.py` for fixture setup
- Allowed in `framework/` internals
- NOT allowed in `tests/` or `pages/`

---

### Rule 4.2: Human Behavior Config via YAML/CLI, Not Code

✅ **CORRECT:**
```bash
# Via CLI
pytest --enable-human-behavior --human-behavior-intensity=high

# Via config (config/human_behavior.yaml)
human_behavior:
  enabled: true
  intensity: "high"
```

❌ **WRONG:**
```python
# Hardcoded in test - FORBIDDEN
def test_booking(page: Page):
    smart_actions = SmartActions(page, enable_human=True)  # ❌ Hardcoded
    # Should use fixture instead
```

**Enforcement:**
- **Rule ID:** `config/hardcoded-behavior`
- **Severity:** WARNING
- **Detection:** SmartActions instantiation in tests
- **Auto-fix:** Use `smart_actions` fixture

---

## 5. Data Management Rules

### Rule 5.1: Use Fixtures for Test Data, Never Hardcode

✅ **CORRECT:**
```python
def test_booking(page: Page, fake_bookslot_data):
    # Use fixture data
    email = fake_bookslot_data['email']  # ✅ Dynamic
    name = fake_bookslot_data['first_name']  # ✅ Dynamic
```

❌ **WRONG:**
```python
def test_booking(page: Page):
    email = "test@example.com"  # ❌ Hardcoded
    name = "John Doe"  # ❌ Hardcoded
```

**Enforcement:**
- **Rule ID:** `data/hardcoded-test-data`
- **Severity:** WARNING
- **Detection:** String literal pattern matching (emails, names, etc.)
- **Auto-fix:** Not available

---

### Rule 5.2: Test Data MUST Be In test_data/ Directory

```
test_data/
├── bookslot/
│   ├── booking_data_1.json    # ✅ Correct location
│   └── booking_data_2.yaml    # ✅ Correct location
```

❌ **WRONG:**
```python
# Hardcoded in test file - FORBIDDEN
TEST_DATA = {
    "email": "test@example.com",  # ❌ In test file
    "name": "John Doe"
}
```

**Enforcement:**
- **Rule ID:** `data/location`
- **Severity:** WARNING
- **Detection:** Large dict/list constants in test files
- **Auto-fix:** Not available

---

## 6. Import Rules

### Rule 6.1: Import Order MUST Follow PEP 8

✅ **CORRECT:**
```python
# Standard library
import time
from pathlib import Path
from typing import Dict, List

# Third-party
import pytest
from playwright.sync_api import Page

# Local
from framework.core.smart_actions import SmartActions
from pages.bookslot.bookslots_basicinfo_page1 import BookslotBasicInfoPage
from utils.fake_data_generator import generate_bookslot_payload
```

❌ **WRONG:**
```python
# ❌ Random order
from pages.bookslot.bookslots_basicinfo_page1 import BookslotBasicInfoPage
import time
from playwright.sync_api import Page
from utils.fake_data_generator import generate_bookslot_payload
import pytest
```

**Enforcement:**
- **Rule ID:** `imports/ordering`
- **Severity:** INFO
- **Detection:** Import statement order analysis
- **Auto-fix:** Yes (reorder imports)

---

### Rule 6.2: No Wildcard Imports

✅ **CORRECT:**
```python
from playwright.sync_api import Page, Locator, expect
```

❌ **WRONG:**
```python
from playwright.sync_api import *  # ❌ VIOLATION
```

**Enforcement:**
- **Rule ID:** `imports/wildcard`
- **Severity:** WARNING
- **Detection:** `import *` pattern
- **Auto-fix:** Not available (requires explicit imports)

---

## 7. Naming Conventions

### Rule 7.1: File Names

**Tests:**
```python
test_booking_flow.py          # ✅
test_bookslot_complete.py     # ✅
test_checkout.py              # ✅

booking_test.py               # ❌ Wrong pattern
bookingTest.py                # ❌ CamelCase
test.py                       # ❌ Too generic
```

**Page Objects:**
```python
bookslots_basicinfo_page1.py  # ✅
checkout_page.py              # ✅

BasicInfoPage.py              # ❌ CamelCase file name
page1.py                      # ❌ Non-descriptive
```

**Pattern:** `lowercase_with_underscores.py`

---

### Rule 7.2: Class Names

✅ **CORRECT:**
```python
class BookslotBasicInfoPage:     # ✅ PascalCase
    pass

class SmartActions:              # ✅ PascalCase
    pass
```

❌ **WRONG:**
```python
class bookslot_basic_info_page:  # ❌ snake_case
    pass

class smartActions:              # ❌ camelCase
    pass
```

**Pattern:** `PascalCase` (CapWords)

---

### Rule 7.3: Method/Function Names

✅ **CORRECT:**
```python
def fill_first_name(self, name: str):  # ✅ snake_case
    pass

def click_next_button(self):           # ✅ snake_case
    pass
```

❌ **WRONG:**
```python
def fillFirstName(self, name: str):    # ❌ camelCase
    pass

def ClickNextButton(self):             # ❌ PascalCase
    pass
```

**Pattern:** `lowercase_with_underscores` (snake_case)

---

## 8. Marker Rules

### Rule 8.1: Project Markers Are Mandatory

✅ **CORRECT:**
```python
@pytest.mark.bookslot
def test_booking(page: Page):
    pass

@pytest.mark.callcenter
def test_appointment_list(page: Page):
    pass
```

❌ **WRONG:**
```python
# ❌ No project marker
def test_booking(page: Page):
    pass
```

**Enforcement:**
- **Rule ID:** `marker/missing-project`
- **Severity:** ERROR
- **Detection:** Missing `@pytest.mark.<project>` decorator
- **Auto-fix:** Suggest marker based on file path

---

### Rule 8.2: Engine Markers Are Mandatory

✅ **CORRECT:**
```python
@pytest.mark.playwright
@pytest.mark.bookslot
def test_booking_playwright(page: Page):
    pass

@pytest.mark.selenium
@pytest.mark.bookslot
def test_booking_selenium(driver: Remote):
    pass
```

❌ **WRONG:**
```python
@pytest.mark.bookslot
def test_booking(page: Page):  # ❌ Missing engine marker
    pass
```

**Enforcement:**
- **Rule ID:** `marker/missing-engine`
- **Severity:** ERROR
- **Detection:** Missing `@pytest.mark.playwright` or `@pytest.mark.selenium`
- **Auto-fix:** Suggest marker based on imports

---

## 9. Execution Flow Rules

### Rule 9.1: UI → API → DB Flow Sequence

✅ **CORRECT:**
```python
@pytest.mark.integration
def test_complete_flow(page, api_client, db_validator):
    # 1. UI Action
    appointment_id = create_appointment_via_ui(page)
    
    # 2. API Validation
    api_response = api_client.get(f"/appointments/{appointment_id}")
    assert api_response.status_code == 200
    
    # 3. DB Validation
    db_record = db_validator.query("SELECT * FROM appointments WHERE id = ?", appointment_id)
    assert db_record is not None
```

❌ **WRONG:**
```python
def test_wrong_flow(page, api_client, db_validator):
    # ❌ DB before UI
    db_record = db_validator.query("SELECT * FROM appointments")
    
    # ❌ API before UI
    api_response = api_client.get("/appointments")
    
    # UI last (wrong order)
    appointment_id = create_appointment_via_ui(page)
```

**Enforcement:**
- **Rule ID:** `flow/wrong-sequence`
- **Severity:** WARNING
- **Detection:** Heuristic analysis of fixture usage order
- **Auto-fix:** Not available

---

## 10. Configuration Rules

### Rule 10.1: Secrets MUST Be In .env, Not Code

✅ **CORRECT:**
```python
# .env file
OPENAI_API_KEY=sk-xxx
DATABASE_PASSWORD=xxx

# In code
import os
api_key = os.getenv("OPENAI_API_KEY")  # ✅
```

❌ **WRONG:**
```python
# Hardcoded secret - FORBIDDEN
api_key = "sk-1234567890abcdef"  # ❌ VIOLATION
db_password = "my_secret_password"  # ❌ VIOLATION
```

**Enforcement:**
- **Rule ID:** `security/hardcoded-secret`
- **Severity:** CRITICAL
- **Detection:** Pattern matching (api_key, password, token, etc.)
- **Auto-fix:** Not available (security issue)

---

### Rule 10.2: Environment Selection via CLI/Config, Not Code

✅ **CORRECT:**
```bash
pytest --env=production
pytest --env=staging
```

❌ **WRONG:**
```python
# Hardcoded environment - FORBIDDEN
ENV = "production"  # ❌ Should use config
```

**Enforcement:**
- **Rule ID:** `config/hardcoded-env`
- **Severity:** WARNING
- **Detection:** Environment string patterns
- **Auto-fix:** Not available

---

## 🔥 Critical Violations Summary

| Rule | Severity | Blocks Commit | Blocks Merge |
|------|----------|---------------|--------------|
| Direct locators in tests | ERROR | ✅ Yes | ✅ Yes |
| Engine mixing | ERROR | ✅ Yes | ✅ Yes |
| Pytest in page objects | ERROR | ✅ Yes | ✅ Yes |
| Assertions in page objects | ERROR | ✅ Yes | ✅ Yes |
| Manual time.sleep() | ERROR | ✅ Yes | ✅ Yes |
| Missing markers | ERROR | ✅ Yes | ✅ Yes |
| Hardcoded secrets | CRITICAL | ✅ Yes | ✅ Yes |
| Hardcoded test data | WARNING | ❌ No | ⚠️ Maybe |
| Naming conventions | WARNING | ❌ No | ❌ No |
| Import order | INFO | ❌ No | ❌ No |

---

## 🛡️ Enforcement Layers

### Layer 1: Pre-Commit Hook (Local)
- Runs before commit
- Blocks commits with violations
- Instant feedback

### Layer 2: File Watcher (Real-time)
- Monitors file changes
- Auto-audits on save
- Strict mode available

### Layer 3: CI/CD (GitHub Actions)
- Runs on every push/PR
- 7 independent status checks
- Blocks merge

### Layer 4: Manual Audit
```bash
pytest --arch-audit
pytest --arch-audit --audit-strict
```

---

## 📝 Baseline Allow-List

For **legitimate technical debt only**:

```yaml
# ci/baseline_allowlist.yaml
violations:
  - file: tests/legacy/test_old_system.py
    rule: pom/direct-locator-in-test
    reason: Legacy test pending migration
    owner: qa-team
    created: 2026-01-15
    expires: 2026-03-31  # ⚠️ MANDATORY
```

**Rules:**
- Every entry MUST have expiration
- Expired entries FAIL builds
- All usage is logged and audited

---

## 🔧 How to Fix Violations

### 1. Read Audit Report
```bash
pytest --arch-audit --audit-report=report.md
```

### 2. View Fix Suggestions
Report includes:
- Exact violation location
- Why it's wrong
- How to fix (with code examples)
- Related documentation links

### 3. Apply Fixes
```bash
# Some auto-fixes available
pytest --arch-audit --audit-fix

# Most require manual refactoring
```

### 4. Verify Fix
```bash
pytest --arch-audit
# Should show: ✅ No violations
```

---

## 📖 Related Documentation

- [Anti-Patterns](Anti-Patterns.md) - What NOT to do
- [Common Mistakes](Common-Mistakes.md) - Frequent errors
- [Best Practices](Best-Practices.md) - Recommended approaches
- [Governance System](../07-Governance/Governance-System-Overview.md) - How enforcement works

---

## 📞 Questions?

**Before asking:**
1. Read this guide completely
2. Check [Anti-Patterns](Anti-Patterns.md)
3. Review [Common Mistakes](Common-Mistakes.md)
4. Search GitHub issues

**Still stuck?**
- Open GitHub issue
- Tag: `question`, `governance`
- Include violation details

---

**Last Updated:** February 1, 2026  
**Framework Version:** 1.0.0  
**Enforcement Version:** 1.0.0

---

**⚠️ REMEMBER: These rules exist to maintain framework quality, consistency, and maintainability. They are NOT optional.**

**"Strict Rules, Flexible Framework"**
