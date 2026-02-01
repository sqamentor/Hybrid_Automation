#!/usr/bin/env python3
"""
Framework Fix Suggestion Engine
================================

Provides intelligent, context-aware fix suggestions for violations.
NEVER auto-fixes code - suggestions only.

Usage:
    from framework_fix_suggestions import FixSuggestionEngine
    fix = FixSuggestionEngine.generate_suggestion(violation)
"""

from typing import Optional
from framework_audit_engine import Violation, Category, Severity


class FixSuggestionEngine:
    """Generates context-aware fix suggestions for violations."""
    
    # Fix suggestion templates
    FIX_TEMPLATES = {
        'mixed-engines': """
**Fix: Separate engines into different files**

1. Create two separate test files:
   - test_<feature>_playwright.py (for modern SPA tests)
   - test_<feature>_selenium.py (for legacy UI tests)

2. Add appropriate markers:
```python
# In Playwright file
import pytest
from playwright.sync_api import Page

@pytest.mark.modern_spa
@pytest.mark.playwright
def test_feature(page: Page):
    # Your test code
    pass
```

```python
# In Selenium file
import pytest
from selenium import webdriver

@pytest.mark.legacy_ui
@pytest.mark.selenium
def test_feature(driver: webdriver.Remote):
    # Your test code
    pass
```
""",
        
        'missing-engine-marker': """
**Fix: Add pytest marker for engine type**

Add the appropriate marker at the test function level:

```python
import pytest

# For Playwright tests (modern SPAs)
@pytest.mark.modern_spa
@pytest.mark.playwright
def test_feature():
    pass

# OR for Selenium tests (legacy UIs)
@pytest.mark.legacy_ui
@pytest.mark.selenium
def test_feature():
    pass
```

**Important:** Marker must match the imports and engine used in the test.
""",
        
        'folder-engine-mismatch': """
**Fix: Move test to correct folder**

Option 1 - Move file:
```bash
# If using Playwright, move to modern folder
git mv tests/legacy/test_file.py tests/modern/

# If using Selenium, move to legacy folder
git mv tests/modern/test_file.py tests/legacy/
```

Option 2 - Convert engine:
- If in /modern folder: Convert Selenium → Playwright
- If in /legacy folder: Convert Playwright → Selenium
""",
        
        'pom-has-assertion': """
**Fix: Move assertion from Page Object to test**

BEFORE (Wrong):
```python
# pages/login_page.py
class LoginPage:
    def verify_login_success(self):
        assert self.page.locator("#welcome").is_visible()  # ❌
```

AFTER (Correct):
```python
# pages/login_page.py
class LoginPage:
    def is_logged_in(self) -> bool:
        return self.page.locator("#welcome").is_visible()  # ✅ Return data

# tests/test_login.py
def test_successful_login(ui_engine):
    page = LoginPage(ui_engine)
    page.login("user", "pass")
    assert page.is_logged_in()  # ✅ Assert in test
```

**Rule:** Page Objects RETURN data, Tests ASSERT on data.
""",
        
        'pom-has-pytest-import': """
**Fix: Remove pytest import from Page Object**

Page Objects should NOT import pytest - they are data providers only.

BEFORE (Wrong):
```python
# pages/page.py
import pytest  # ❌

class MyPage:
    pass
```

AFTER (Correct):
```python
# pages/page.py
# No pytest import ✅

class MyPage:
    def get_title(self) -> str:
        return self.page.title()  # Return data
```

Import pytest only in test files.
""",
        
        'test-has-direct-locator': """
**Fix: Extract locator to Page Object**

BEFORE (Wrong):
```python
# tests/test_feature.py
def test_something(page: Page):
    page.locator("#username").fill("user")  # ❌ Direct locator
```

AFTER (Correct):
```python
# pages/login_page.py
class LoginPage:
    def enter_username(self, username: str):
        self.page.locator("#username").fill(username)  # ✅ Encapsulated

# tests/test_feature.py
def test_something(page: Page):
    login = LoginPage(page)
    login.enter_username("user")  # ✅ Use Page Object
```

**Rule:** Tests use Page Objects, not direct locators.
""",
        
        'baseline-expired': """
**Fix: Remove or update expired baseline**

Option 1 - Fix the violation:
Fix the actual code issue and remove the baseline entry from:
`ci/baseline_allowlist.yaml`

Option 2 - Extend baseline (if still needed):
Update the expiration date in `ci/baseline_allowlist.yaml`:

```yaml
violations:
  - file: "path/to/file.py"
    rule_id: "rule-name"
    expires: "2026-03-01"  # Extend date
    reason: "Still working on fix - needs more time"
```

**Note:** Expired baselines are treated as active violations.
""",
        
        'canonical-flow-missing-comment': """
**Fix: Add protected flow marker comment**

For complete end-to-end tests, add this marker at the top:

```python
# CANONICAL FLOW PROTECTED - DO NOT MODIFY WITHOUT APPROVAL

import pytest

@pytest.mark.e2e
@pytest.mark.complete_flow
def test_complete_booking_flow():
    \"\"\"Complete end-to-end booking flow - authoritative test\"\"\"
    # Your comprehensive test
    pass
```

This marks the test as a protected canonical flow that requires explicit approval to modify.
"""
    }
    
    @classmethod
    def generate_suggestion(cls, violation: Violation) -> str:
        """Generate fix suggestion for a violation.

        Args:
            violation: Violation object

        Returns:
            Formatted fix suggestion string
        """
        # Check if violation already has a fix suggestion
        if violation.fix_suggestion:
            return violation.fix_suggestion
        
        # Get template for rule ID
        template = cls.FIX_TEMPLATES.get(violation.rule_id)
        
        if template:
            return template.strip()
        
        # Generic fix suggestion
        return cls._generate_generic_fix(violation)
    
    @classmethod
    def _generate_generic_fix(cls, violation: Violation) -> str:
        """Generate generic fix suggestion when no template exists."""
        
        if violation.severity == Severity.CRITICAL:
            priority = "IMMEDIATE ACTION REQUIRED"
        elif violation.severity == Severity.ERROR:
            priority = "Must fix before merge"
        elif violation.severity == Severity.WARNING:
            priority = "Should fix soon"
        else:
            priority = "Consider fixing"
        
        return f"""
**Fix Suggestion: {violation.rule_id}**

**Priority:** {priority}

**Issue:** {violation.message}

**Location:** {violation.file_path}:{violation.line_number}

**Category:** {violation.category.value}

**General Guidance:**
1. Review the violation context
2. Check documentation for rule: {violation.rule_id}
3. Consult GOVERNANCE_SYSTEM.md for detailed rules
4. Run `pytest --arch-audit` locally to verify fix

**Need Help?**
- Review: docs/GOVERNANCE_SYSTEM.md
- Check examples in: examples/
- Ask team for clarification on rule: {violation.rule_id}
"""
    
    @classmethod
    def get_all_templates(cls) -> dict:
        """Get all fix templates."""
        return cls.FIX_TEMPLATES.copy()
    
    @classmethod
    def has_template(cls, rule_id: str) -> bool:
        """Check if template exists for rule_id."""
        return rule_id in cls.FIX_TEMPLATES


if __name__ == '__main__':
    print("framework_fix_suggestions.py - Fix suggestion generator")
    print("Import this module to use FixSuggestionEngine")
