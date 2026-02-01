# Governance System - Developer Quick Reference

**Last Updated:** February 1, 2026

---

## Quick Start

```bash
# Run full audit before committing
pytest --arch-audit

# Audit specific category
pytest --arch-audit --audit-category=pom-compliance

# Show fix suggestions
pytest --arch-audit --audit-show-fixes

# Generate markdown report
pytest --arch-audit --audit-report=artifacts/audit.md

# Strict mode (fail on warnings too)
pytest --arch-audit --audit-strict
```

---

## Common Commands

### Local Development

```bash
# Quick check before commit (recommended)
pytest --arch-audit

# Check only critical issues
pytest --arch-audit --audit-category=engine-mix
pytest --arch-audit --audit-category=marker-engine

# Get help for a specific violation
pytest --arch-audit --audit-category=pom-compliance --audit-show-fixes
```

### CI/CD

```bash
# Run all CI checks locally (requires artifacts/ dir)
python ci/ci_audit_runner.py --artifacts-dir artifacts/

# Run specific CI check
python ci/ci_audit_runner.py --check engine-mix

# Dry-run PR comment (doesn't actually post)
python ci/github_pr_commenter.py --pr-number 123 --dry-run
```

---

## Rule Categories (7 Total)

| Category | Severity | Blocks CI | Description |
|----------|----------|-----------|-------------|
| `engine-mix` | CRITICAL | Yes | Mixing Playwright + Selenium in same file |
| `marker-engine` | CRITICAL | Yes | Missing markers or marker/engine mismatch |
| `folder-engine` | ERROR | Yes | Folder doesn't match engine type |
| `pom-compliance` | ERROR | Yes | POM violations (assertions, pytest imports) |
| `test-boundaries` | WARNING | No | Direct locator calls in tests |
| `structural` | ERROR | Yes | Files in wrong directories |
| `canonical-flow` | INFO | No | Changes to protected flow files |

---

## Most Common Violations & Fixes

### 1. Missing Engine Marker

**Violation:**
```
X MARKER-ENGINE: Test class missing engine marker
```

**Fix:**
```python
import pytest

@pytest.mark.modern_spa  # For Playwright
# OR
@pytest.mark.legacy_ui   # For Selenium
class TestMyFeature:
    def test_something(self, page):
        pass
```

### 2. Assertion in Page Object

**Violation:**
```
X POM-COMPLIANCE: Assertions not allowed in Page Objects
```

**Fix:**
```python
# BEFORE (wrong)
def verify_login_success(self):
    assert self.page.locator("#user").is_visible()

# AFTER (correct)
def is_logged_in(self) -> bool:
    return self.page.locator("#user").is_visible()
    
# In test:
assert page_object.is_logged_in()
```

### 3. pytest Import in Page Object

**Violation:**
```
X POM-COMPLIANCE: Page Objects must not import pytest
```

**Fix:**
```python
# BEFORE (wrong)
import pytest
from playwright.sync_api import Page

# AFTER (correct)
from playwright.sync_api import Page
# No pytest import needed in Page Objects
```

### 4. Marker/Engine Mismatch

**Violation:**
```
X MARKER-ENGINE: @modern_spa marker but file imports Selenium
```

**Fix:**
```python
# BEFORE (wrong)
import pytest
from selenium import webdriver

@pytest.mark.modern_spa  # WRONG - using Selenium
class TestFeature:
    pass

# AFTER (correct) - Option 1: Fix marker
@pytest.mark.legacy_ui  # Correct for Selenium
class TestFeature:
    pass

# AFTER (correct) - Option 2: Fix imports
from playwright.sync_api import Page

@pytest.mark.modern_spa  # Correct for Playwright
class TestFeature:
    pass
```

### 5. Direct Locator in Test

**Violation:**
```
! TEST-BOUNDARIES: Use Page Objects instead of direct locators
```

**Fix:**
```python
# BEFORE (discouraged)
def test_login(self, page):
    page.locator("#username").fill("user")
    page.locator("#password").fill("pass")

# AFTER (recommended)
def test_login(self, page, login_page):
    login_page.enter_username("user")
    login_page.enter_password("pass")
```

---

## Baseline Management

### Add to Baseline (Technical Debt)

```bash
# Edit ci/baseline_allowlist.yaml
violations:
  - file: tests/legacy/test_old_feature.py
    rule: marker-engine/missing-engine-marker
    reason: Legacy test pending migration (JIRA-123)
    owner: qa-team
    created: 2026-02-01
    expires: 2026-03-31  # MANDATORY - must have expiration!
```

**Rules:**
- Every baseline entry MUST have `expires` date
- Expired entries = violations (build fails)
- Use baseline for legitimate technical debt only
- Track with JIRA/ticket number

### Check Baseline Status

```bash
# Audit will show baselined violations
pytest --arch-audit

# Look for "Baselined violations: X" in output
```

---

## Pre-commit Hook (Optional)

Enable automatic audit before every commit:

```bash
# Copy pre-commit hook
cp scripts/hooks/pre-commit.template .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit  # Linux/Mac only

# Or use PowerShell version (Windows)
cp scripts/hooks/pre-commit-windows.ps1 .git/hooks/pre-commit.ps1
```

Bypass (emergency only):
```bash
git commit --no-verify
```

---

## GitHub Actions (CI/CD)

### Status Checks in PR

Every PR shows 7 independent status checks:
- `audit/engine-mix` (blocking)
- `audit/marker-engine` (blocking)
- `audit/folder-engine` (blocking)
- `audit/pom-compliance` (blocking)
- `audit/test-boundaries` (non-blocking)
- `audit/structural` (blocking)
- `audit/canonical-flow` (non-blocking)

**PR can only merge if all blocking checks pass.**

### PR Comments

If violations detected, bot automatically comments with:
- Summary of violations
- Detailed violation locations
- Fix suggestions for each violation
- Links to documentation

---

## Troubleshooting

### "Can't import audit engine"

**Cause:** Missing dependencies or wrong directory

**Fix:**
```bash
# Ensure in project root
cd /path/to/project

# Install/update dependencies
pip install -r requirements.txt
```

### "Baseline violations still showing"

**Cause:** Baseline file not found or syntax error

**Fix:**
```bash
# Check baseline file exists
ls ci/baseline_allowlist.yaml

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('ci/baseline_allowlist.yaml'))"
```

### "Audit too slow"

**Normal:** First run parses all files (~2 seconds for 300 files)

**If slower:**
- Check for very large files
- Ensure SSD (not network drive)
- Run specific category: `--audit-category=engine-mix`

---

## Best Practices

1. **Run audit before committing**
   ```bash
   pytest --arch-audit
   ```

2. **Fix violations immediately**
   - Don't accumulate technical debt
   - Use fix suggestions provided

3. **Use baseline sparingly**
   - Only for legitimate technical debt
   - Always set expiration date
   - Track with ticket number

4. **Keep tests clean**
   - Use Page Objects
   - Add proper markers
   - Follow POM rules

5. **Review PR comments**
   - Bot provides helpful fix suggestions
   - Follow the guidance
   - Ask team if unclear

---

## Getting Help

**Documentation:**
- Full Guide: `docs/GOVERNANCE_SYSTEM.md`
- Implementation Details: `docs/ENFORCEMENT_SUMMARY.md`
- This Cheat Sheet: `docs/GOVERNANCE_QUICK_REF.md`

**Command Help:**
```bash
pytest --help | grep audit
python ci/ci_audit_runner.py --help
```

**Questions:**
- Ask in team Slack channel
- Reach out to QA Architect
- Check documentation first

---

## Summary

**Before every commit:**
```bash
pytest --arch-audit
```

**If violations found:**
1. Read the violation message
2. Apply suggested fix
3. Re-run audit
4. Commit when clean

**If you disagree with a rule:**
- Discuss with team
- Rules protect architecture
- Never bypass without discussion

---

**Remember:** The governance system protects framework quality. Follow the rules, and the framework stays healthy!
