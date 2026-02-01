# 🏗️ Framework Governance System

## Complete Self-Defending Architecture

**Version:** 1.0.0  
**Date:** February 1, 2026  
**Status:** ✅ Fully Implemented

---

## Table of Contents

1. [Overview](#overview)
2. [Core Components](#core-components)
3. [Rule Categories](#rule-categories)
4. [Usage Guide](#usage-guide)
5. [CI/CD Integration](#cicd-integration)
6. [Developer Workflow](#developer-workflow)
7. [Baseline Management](#baseline-management)
8. [Fix Suggestions](#fix-suggestions)
9. [AI Explanations](#ai-explanations)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The Framework Governance System is a comprehensive, zero-tolerance enforcement platform that ensures architectural compliance and prevents framework degradation over time.

### Key Principles

✅ **Self-Defending** - Architecture enforces itself automatically  
✅ **Zero-Tolerance** - No silent violations allowed  
✅ **Deterministic** - No hidden magic, everything explicit  
✅ **Auditable** - Every decision explainable  
✅ **Scalable** - Multi-project ready  
✅ **Maintainable** - Strict separation of concerns

### What It Does

- **Detects** architectural violations automatically via AST analysis
- **Explains** violations clearly with context and fix suggestions
- **Blocks** CI/CD pipelines on violations
- **Guides** developers to correct solutions
- **Protects** canonical business flows from unintended changes
- **Reports** comprehensive audit results

---

## Core Components

### 1. Framework Audit Engine
**Location:** `scripts/governance/framework_audit_engine.py`

AST-based static analysis system that scans codebase for violations.

**Features:**
- Engine violation detection
- Marker validation
- POM compliance
- Structural validation
- Canonical flow protection
- Baseline support

### 2. Baseline Allow-List
**Location:** `ci/baseline_allowlist.yaml`

Manages temporary suppression of known violations during remediation.

**Rules:**
- Every entry MUST have expiration date
- Expired baselines FAIL the build
- All baseline usage is reported

### 3. Report Generator
**Location:** `scripts/governance/framework_report_generator.py`

Generates comprehensive markdown reports.

**Output:** `artifacts/framework_audit_report.md`

### 4. Fix Suggestion Engine
**Location:** `scripts/governance/framework_fix_suggestions.py`

Provides intelligent, context-aware fix suggestions for each violation type.

**Never** auto-modifies code - suggestions only.

### 5. Pytest Plugin
**Location:** `scripts/governance/pytest_arch_audit_plugin.py`

Enables local audits via pytest command.

**Usage:** `pytest --arch-audit`

### 6. CI Integration
**Location:** `ci/ci_audit_runner.py`

Runs independent CI status checks per category.

### 7. PR Comment Generator
**Location:** `ci/github_pr_commenter.py`

Automatically posts detailed PR comments on violations.

### 8. AI Explainer (Optional)
**Location:** `scripts/governance/ai_explainer.py`

Generates educational explanations for violations.

**CRITICAL:** Explain-only, never auto-fixes code.

---

## Rule Categories

### 1️⃣ Engine Violations (`engine-mix`)

**Detects:**
- ❌ Mixing Playwright + Selenium in same test
- ❌ Using both `page` and `driver`
- ❌ Importing both engines in one file

**Severity:** CRITICAL

**Example Violation:**
```python
# ❌ BAD: Mixed engines
from playwright.sync_api import Page
from selenium.webdriver import Chrome

class TestFeature:
    def test_something(self):
        # Uses both engines - VIOLATION
        pass
```

**Fix:**
```python
# ✅ GOOD: Separate files
# test_feature_playwright.py
from playwright.sync_api import Page

@pytest.mark.modern_spa
class TestFeature:
    def test_something(self, ui_engine):
        pass

# test_feature_selenium.py
from selenium.webdriver import Chrome

@pytest.mark.legacy_ui
class TestFeature:
    def test_something(self, ui_engine):
        pass
```

---

### 2️⃣ Marker ↔ Engine Violations (`marker-engine`)

**Detects:**
- ❌ Missing engine marker (@modern_spa or @legacy_ui)
- ❌ @modern_spa used with Selenium
- ❌ @legacy_ui used with Playwright

**Severity:** CRITICAL

**Example Violation:**
```python
# ❌ BAD: Missing marker
class TestFeature:
    def test_something(self, ui_engine):
        pass
```

**Fix:**
```python
# ✅ GOOD: Explicit marker
@pytest.mark.modern_spa
class TestFeature:
    def test_something(self, ui_engine):
        pass
```

---

### 3️⃣ Folder ↔ Engine Violations (`folder-engine`)

**Detects:**
- ❌ Playwright test in `legacy/` folder
- ❌ Selenium test in `modern/` folder

**Severity:** ERROR

**Example Violation:**
```
tests/modern/test_feature.py  # Contains Selenium code - VIOLATION
```

**Fix:**
Move to appropriate folder or convert engine.

---

### 4️⃣ POM Compliance (`pom-compliance`)

**Detects:**
- ❌ pytest imports in Page Objects
- ❌ Assertions in Page Objects
- ❌ Sleeps/waits in Page Objects
- ❌ API/DB calls in Page Objects

**Severity:** ERROR

**Example Violation:**
```python
# ❌ BAD: Page Object with assertion
class LoginPage:
    def verify_login(self):
        assert self.page.locator("#welcome").is_visible()
```

**Fix:**
```python
# ✅ GOOD: Page Object returns data
class LoginPage:
    def is_logged_in(self) -> bool:
        return self.page.locator("#welcome").is_visible()

# ✅ Test asserts
def test_login(ui_engine):
    page = LoginPage(ui_engine)
    page.login("user", "pass")
    assert page.is_logged_in()
```

---

### 5️⃣ Test Boundaries (`test-boundaries`)

**Detects:**
- ⚠️ Direct `page.locator()` in tests
- ⚠️ Direct `driver.find_element()` in tests

**Severity:** WARNING (non-blocking)

**Example Violation:**
```python
# ⚠️ WARNING: Direct locator in test
def test_login(page):
    page.locator("#username").fill("user")
```

**Fix:**
```python
# ✅ GOOD: Use Page Object
def test_login(ui_engine):
    page = LoginPage(ui_engine)
    page.login("user")
```

---

### 6️⃣ Structural Violations (`structural`)

**Detects:**
- ❌ Page Objects outside /pages
- ❌ Tests outside /tests
- ⚠️ main() functions in tests

**Severity:** ERROR

---

### 7️⃣ Canonical Flow Protection (`canonical-flow`)

**Detects:**
- ℹ️ Changes to `*_complete_flow*.py` files

**Severity:** INFO

**Purpose:** Flag changes to authoritative business flows for review.

---

## Usage Guide

### Local Development

#### Run Full Audit
```bash
pytest --arch-audit
```

#### Audit Specific Category
```bash
pytest --arch-audit --audit-category=engine-mix
```

#### With Baseline
```bash
pytest --arch-audit --audit-baseline=ci/baseline_allowlist.yaml
```

#### Generate Report
```bash
pytest --arch-audit --audit-report=my_audit.md
```

#### Strict Mode (fail on warnings)
```bash
pytest --arch-audit --audit-strict
```

---

### CI/CD Usage

#### Run All Checks
```bash
python ci/ci_audit_runner.py
```

#### Run Specific Check
```bash
python ci/ci_audit_runner.py --check engine-mix
```

#### With Artifacts
```bash
python ci/ci_audit_runner.py --artifacts-dir artifacts/
```

---

### PR Comment Generation

```bash
python ci/github_pr_commenter.py --pr-number 123
```

Requires `GITHUB_TOKEN` environment variable.

---

## CI/CD Integration

### GitHub Actions Workflow

Create `.github/workflows/architecture-audit.yml`:

```yaml
name: Architecture Audit

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  audit:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install pyyaml
      
      - name: Run Architecture Audit
        run: |
          python ci/ci_audit_runner.py --artifacts-dir artifacts/
      
      - name: Upload Audit Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: audit-report
          path: artifacts/
      
      - name: Comment on PR
        if: github.event_name == 'pull_request' && failure()
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python ci/github_pr_commenter.py --pr-number ${{ github.event.pull_request.number }}
```

### Independent Status Checks

Each rule category creates its own CI status check:

- `audit/engine-mix` ✅ or ❌
- `audit/marker-engine` ✅ or ❌
- `audit/folder-engine` ✅ or ❌
- `audit/pom-compliance` ✅ or ❌
- `audit/test-boundaries` ✅ or ❌
- `audit/structural` ✅ or ❌
- `audit/canonical-flow` ℹ️ (info only)

---

## Developer Workflow

### Before Committing

1. **Run local audit:**
   ```bash
   pytest --arch-audit
   ```

2. **Fix violations:**
   - Review detailed output
   - Apply suggested fixes
   - Re-run audit

3. **Commit when clean:**
   ```bash
   git add .
   git commit -m "feat: implement feature (audit clean)"
   ```

### When PR Fails

1. **Check PR comment** - Detailed violations posted automatically

2. **Run local audit:**
   ```bash
   pytest --arch-audit --audit-show-fixes
   ```

3. **Apply fixes** - Follow suggestions

4. **Verify:**
   ```bash
   pytest --arch-audit
   ```

5. **Push changes** - CI re-runs automatically

---

## Baseline Management

### When to Use Baseline

Use baseline for **legacy code** being brought into compliance gradually.

### Adding Baseline Entry

Edit `ci/baseline_allowlist.yaml`:

```yaml
violations:
  - file: tests/legacy/test_old_system.py
    rule: engine/missing-marker
    reason: Legacy test suite pending migration
    owner: qa-team
    created: 2026-02-01
    expires: 2026-03-31  # MANDATORY
```

### Baseline Rules

❌ **No expiration date** = Build fails  
❌ **Expired baseline** = Build fails  
✅ **Baseline usage reported** in logs and reports

### Managing Expiration

Set realistic expiration dates based on:
- Complexity of fix
- Team capacity
- Business priorities

**Expired baselines are treated as violations.**

---

## Fix Suggestions

Every violation includes:

1. **Context** - Code where violation occurs
2. **Explanation** - Why it's a problem
3. **Fix Suggestion** - How to resolve it
4. **Example** - Before/after code

### Accessing Fix Suggestions

#### In Terminal
```bash
pytest --arch-audit --audit-show-fixes
```

#### In Report
`artifacts/framework_audit_report.md`

#### In PR Comments
Automatically included in GitHub PR comments

---

## AI Explanations

### Optional Feature

AI explanations are **OPTIONAL** and **ADVISORY ONLY**.

### Rules

❌ AI NEVER modifies code  
❌ AI NEVER changes logic  
✅ AI only explains and educates  
✅ System functions fully without AI

### Usage

```bash
python scripts/governance/ai_explainer.py --interactive
```

---

## Troubleshooting

### "Cannot import audit engine"

**Solution:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/scripts/governance"
```

### "Baseline expired"

**Solution:**
Update expiration date in `ci/baseline_allowlist.yaml` or fix violation.

### "Too many violations"

**Solution:**
1. Use baseline for legacy code
2. Fix violations incrementally
3. Run `pytest --arch-audit --audit-category=<category>` to focus on one category

### "False positive"

**Solution:**
1. Review rule definition
2. If legitimate exception, add to baseline with justification
3. Set reasonable expiration date

---

## Architecture

```
┌─────────────────────────────────────────┐
│      Framework Governance System        │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
   ┌────▼────┐          ┌───────▼──────┐
   │  Local  │          │   CI/CD      │
   │  Audit  │          │   Pipeline   │
   └────┬────┘          └───────┬──────┘
        │                       │
        │   pytest --arch-audit │
        │                       │
   ┌────▼───────────────────────▼────┐
   │   Framework Audit Engine        │
   │   (AST-based Analysis)          │
   └────┬──────────┬──────────┬──────┘
        │          │          │
   ┌────▼──┐  ┌────▼──┐  ┌────▼──┐
   │Engine │  │ POM   │  │Struct │
   │Rules  │  │Rules  │  │Rules  │
   └───┬───┘  └───┬───┘  └───┬───┘
       │          │          │
       └──────────┴──────────┘
                  │
         ┌────────▼────────┐
         │   Violations    │
         │   Detected      │
         └────────┬────────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
  ┌───▼───┐  ┌────▼────┐  ┌──▼──┐
  │Report │  │  Fix    │  │ PR  │
  │  .md  │  │Suggest  │  │Comm │
  └───────┘  └─────────┘  └─────┘
```

---

## Contact & Support

**Maintainer:** Lokendra Singh  
**Email:** qa.lokendra@gmail.com  
**Website:** www.sqamentor.com

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-01 | Initial release - Complete governance system |

---

<div align="center">
  <strong>🛡️ Self-Defending Architecture</strong><br>
  <sub>Protecting framework integrity automatically</sub>
</div>
