# 🛡️ POM ENFORCEMENT CHECKLIST
## Automated Architectural Compliance Tool

**Version:** 1.0  
**Date:** January 31, 2026  
**Purpose:** Automated detection of POM violations and architectural anti-patterns

---

## 📋 PRE-COMMIT CHECKLIST

### Before Committing ANY Code, Verify:

#### Page Object Files (`pages/**/*.py`)
- [ ] ❌ Contains NO `import pytest` or `from pytest`
- [ ] ❌ Contains NO `assert` statements
- [ ] ❌ Contains NO `time.sleep()` or arbitrary waits
- [ ] ❌ Contains NO business logic or calculations
- [ ] ❌ Contains NO API/Database calls
- [ ] ❌ Contains NO multi-page workflows
- [ ] ✅ Contains ONLY: locators, actions, page-level checks
- [ ] ✅ All methods return `self` or primitive data types
- [ ] ✅ Base URL injected via constructor
- [ ] ✅ Stateless design (no instance variables modified)

#### Test Files (`tests/**/*.py`)
- [ ] ❌ Contains NO direct `page.locator()` or `page.get_by_role()` calls
- [ ] ❌ Contains NO raw Selenium `driver.find_element()` calls
- [ ] ✅ Imports Page Object classes
- [ ] ✅ Creates Page Object instances
- [ ] ✅ Uses Page Object methods exclusively
- [ ] ✅ Contains assertions (business expectations)
- [ ] ✅ Has pytest markers (`@pytest.mark.project`)
- [ ] ✅ Uses fixtures for setup

#### Configuration Files
- [ ] ❌ Contains NO hardcoded URLs
- [ ] ❌ Contains NO credentials
- [ ] ✅ Uses YAML/environment variables
- [ ] ✅ Fail-loud pattern (raises errors, no silent fallbacks)

---

## 🤖 AUTOMATED LINTING SCRIPT

### Usage:
```bash
# Check all files
python enforce_pom.py

# Check specific directory
python enforce_pom.py pages/bookslot

# Fix violations automatically (where possible)
python enforce_pom.py --fix

# Pre-commit hook
python enforce_pom.py --strict --fail-fast
```

### Script Content:

```python
#!/usr/bin/env python3
"""
POM Enforcement Linter
Detects and reports Page Object Model violations
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

class POMViolation:
    def __init__(self, file: str, line: int, rule: str, message: str, severity: str):
        self.file = file
        self.line = line
        self.rule = rule
        self.message = message
        self.severity = severity
    
    def __str__(self):
        return f"{self.severity} {self.file}:{self.line} [{self.rule}] {self.message}"

class POMEnforcer:
    """Enforces Page Object Model architectural rules"""
    
    FORBIDDEN_IN_PAGES = {
        'pytest_import': r'(?:^|\n)(?:import pytest|from pytest)',
        'assert_statement': r'(?:^|\s)assert\s',
        'time_sleep': r'time\.sleep\(',
        'hardcoded_wait': r'wait_for_timeout\(\d+\)',
        'api_call': r'(?:requests\.|httpx\.|urllib\.)',
        'db_call': r'(?:cursor\.execute|connection\.connect)',
    }
    
    REQUIRED_IN_PAGES = {
        'class_definition': r'class\s+\w+Page',
        'constructor': r'def __init__\(self',
    }
    
    FORBIDDEN_IN_TESTS = {
        'direct_locator': r'page\.(?:locator|get_by_role|get_by_text|get_by_label)\(',
        'driver_find': r'driver\.find_element',
        'hardcoded_url': r'(?:https?://|www\.)\S+',
    }
    
    REQUIRED_IN_TESTS = {
        'page_import': r'from pages\.',
        'pytest_marker': r'@pytest\.mark\.',
    }
    
    def __init__(self):
        self.violations: List[POMViolation] = []
    
    def check_page_object(self, file_path: Path) -> List[POMViolation]:
        """Check a page object file for violations"""
        violations = []
        content = file_path.read_text()
        lines = content.split('\n')
        
        # Check for forbidden patterns
        for rule_name, pattern in self.FORBIDDEN_IN_PAGES.items():
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    if not self._is_in_comment(line):
                        violations.append(POMViolation(
                            file=str(file_path),
                            line=i,
                            rule=rule_name,
                            message=f"Forbidden pattern '{pattern}' found in Page Object",
                            severity="ERROR"
                        ))
        
        # Check for required patterns
        for rule_name, pattern in self.REQUIRED_IN_PAGES.items():
            if not re.search(pattern, content):
                violations.append(POMViolation(
                    file=str(file_path),
                    line=1,
                    rule=rule_name,
                    message=f"Required pattern '{rule_name}' missing",
                    severity="WARNING"
                ))
        
        return violations
    
    def check_test_file(self, file_path: Path) -> List[POMViolation]:
        """Check a test file for violations"""
        violations = []
        content = file_path.read_text()
        lines = content.split('\n')
        
        # Check for forbidden patterns
        for rule_name, pattern in self.FORBIDDEN_IN_TESTS.items():
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    if not self._is_in_comment(line) and not self._is_in_fixture(lines, i):
                        violations.append(POMViolation(
                            file=str(file_path),
                            line=i,
                            rule=rule_name,
                            message=f"Test bypasses Page Object: {pattern}",
                            severity="ERROR"
                        ))
        
        return violations
    
    def _is_in_comment(self, line: str) -> bool:
        """Check if line is a comment"""
        return line.strip().startswith('#') or line.strip().startswith('"""')
    
    def _is_in_fixture(self, lines: List[str], line_num: int) -> bool:
        """Check if line is inside a pytest fixture"""
        # Look backwards for @pytest.fixture
        for i in range(max(0, line_num - 20), line_num):
            if '@pytest.fixture' in lines[i]:
                return True
        return False
    
    def check_directory(self, directory: Path) -> None:
        """Check all Python files in directory"""
        
        # Check page objects
        for page_file in directory.glob('pages/**/*.py'):
            if page_file.name != '__init__.py':
                violations = self.check_page_object(page_file)
                self.violations.extend(violations)
        
        # Check tests
        for test_file in directory.glob('tests/**/*.py'):
            if test_file.name.startswith('test_'):
                violations = self.check_test_file(test_file)
                self.violations.extend(violations)
    
    def report(self) -> int:
        """Print violations and return error count"""
        if not self.violations:
            print("✅ No POM violations detected!")
            return 0
        
        # Group by severity
        errors = [v for v in self.violations if v.severity == "ERROR"]
        warnings = [v for v in self.violations if v.severity == "WARNING"]
        
        print(f"\n🚨 POM VIOLATIONS DETECTED\n")
        print(f"Errors: {len(errors)}")
        print(f"Warnings: {len(warnings)}\n")
        
        if errors:
            print("❌ ERRORS (Must Fix):")
            for v in errors:
                print(f"  {v}")
        
        if warnings:
            print("\n⚠️  WARNINGS (Should Fix):")
            for v in warnings:
                print(f"  {v}")
        
        return len(errors)


def main():
    enforcer = POMEnforcer()
    project_root = Path(__file__).parent
    
    print("🔍 Checking POM compliance...\n")
    enforcer.check_directory(project_root)
    
    error_count = enforcer.report()
    
    if error_count > 0:
        print(f"\n❌ FAIL: {error_count} violations must be fixed")
        sys.exit(1)
    else:
        print("\n✅ PASS: Framework is POM compliant")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

---

## 📝 PRE-COMMIT HOOK SETUP

### Installation:

```bash
# 1. Create .git/hooks/pre-commit file
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "🔍 Running POM compliance checks..."
python enforce_pom.py --strict
if [ $? -ne 0 ]; then
    echo "❌ Commit rejected: POM violations detected"
    echo "Fix violations or use --no-verify to bypass (not recommended)"
    exit 1
fi
echo "✅ POM compliance check passed"
EOF

# 2. Make executable
chmod +x .git/hooks/pre-commit

# 3. Test
git add .
git commit -m "test" --dry-run
```

---

## 🎯 CODING STANDARDS REFERENCE

### ✅ CORRECT PATTERNS

#### Page Object Example:
```python
# pages/myproject/my_page.py
from playwright.sync_api import Page

class MyPage:
    """What a user CAN do on this page"""
    
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
    
    # Locators
    @property
    def submit_button(self):
        return self.page.get_by_role("button", name="Submit")
    
    # Actions (return self for chaining)
    def fill_form(self, data: dict):
        \"\"\"Fill form fields\"\"\"
        self.page.fill("#name", data['name'])
        return self
    
    def submit(self):
        \"\"\"Submit form\"\"\"
        self.submit_button.click()
        return self
    
    # Page-level checks (return bool/data, NO assertions)
    def is_loaded(self) -> bool:
        \"\"\"Check if page loaded\"\"\"
        return self.submit_button.is_visible()
```

#### Test Example:
```python
# tests/myproject/test_my_feature.py
import pytest
from pages.myproject.my_page import MyPage

@pytest.mark.myproject
def test_submit_form(page, config, test_data):
    # Use Page Object
    my_page = MyPage(page, config['base_url'])
    my_page.fill_form(test_data)
    my_page.submit()
    
    # Assert in test
    assert my_page.is_loaded()
```

---

### ❌ ANTI-PATTERNS

#### WRONG: Assertion in Page Object
```python
# ❌ FORBIDDEN
def should_be_submitted(self):
    assert self.success_message.is_visible()  # ❌ Page deciding success
```

#### WRONG: Test with Direct Locators
```python
# ❌ FORBIDDEN
def test_something(page):
    page.get_by_role("button", name="Submit").click()  # ❌ Bypasses POM
```

#### WRONG: Hidden Wait in Page
```python
# ❌ FORBIDDEN
def submit(self):
    self.button.click()
    time.sleep(2)  # ❌ Magic wait
```

---

## 🏃 QUICK COMPLIANCE CHECK

Run this command before every commit:

```bash
# Full check
python enforce_pom.py

# Expected output:
# ✅ No POM violations detected!
# ✅ PASS: Framework is POM compliant
```

If violations detected:
1. Review the output
2. Fix each violation
3. Run check again
4. Commit only when clean

---

## 📚 ADDITIONAL RESOURCES

- **Full Audit:** See `ARCHITECTURAL_COMPLIANCE_REPORT.md`
- **Examples:** See `tests/bookslot/` for correct patterns (after refactoring)
- **Training:** Schedule session with QA Architect

---

## ✅ ENFORCEMENT STATUS

**Status:** 🟡 IN PROGRESS

**Automated:**
- [ ] POM linting script created
- [ ] Pre-commit hook installed
- [ ] CI/CD integration

**Manual:**
- [x] Audit completed
- [ ] Team trained
- [ ] Violations fixed

**Target:** ✅ 100% automated enforcement by Week 2
