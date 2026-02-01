# 🛡️ Framework Enforcement & Governance

## Complete Implementation Summary

**Date:** February 1, 2026  
**Status:** ✅ FULLY OPERATIONAL  
**Version:** 1.0.0

---

## Executive Summary

The Enterprise Hybrid Automation Framework now includes a **complete self-defending governance system** that automatically enforces architectural rules, prevents degradation, and guides developers to correct solutions.

### What Was Implemented

✅ **AST-Based Audit Engine** - Static analysis of all Python code  
✅ **7 Independent Rule Categories** - Each with own CI status check  
✅ **Baseline Allow-List System** - Managed technical debt with expiration  
✅ **Intelligent Fix Suggestions** - Context-aware guidance for every violation  
✅ **Pytest Plugin** - Local audit via `pytest --arch-audit`  
✅ **CI Integration** - Automated checks on every PR  
✅ **PR Comment Automation** - Detailed violation reports in PRs  
✅ **AI Explanation System** - Optional educational explanations  
✅ **Canonical Flow Protection** - Guards critical business flows  
✅ **Comprehensive Documentation** - Complete usage guides

---

## System Architecture

```
┌────────────────────────────────────────────────────────────┐
│           Framework Governance System                       │
│                  (Zero-Tolerance)                           │
└────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
   ┌────▼─────┐                      ┌──────▼──────┐
   │  LOCAL   │                      │   CI/CD     │
   │  AUDIT   │                      │  PIPELINE   │
   └────┬─────┘                      └──────┬──────┘
        │                                   │
        │  pytest --arch-audit              │
        │                                   │
   ┌────▼───────────────────────────────────▼─────┐
   │     Framework Audit Engine                   │
   │     (AST-based Python Analysis)              │
   │                                              │
   │  Components:                                 │
   │  • EngineMixDetector                        │
   │  • MarkerEngineValidator                    │
   │  • FolderEngineValidator                    │
   │  • POMComplianceDetector                    │
   │  • StructuralValidator                      │
   │  • CanonicalFlowProtector                   │
   │  • BaselineManager                          │
   └──────────────────┬───────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
    ┌────▼─────┐            ┌──────▼────┐
    │Violations│            │ Baseline  │
    │ Detected │            │ Check     │
    └────┬─────┘            └──────┬────┘
         │                         │
         └─────────────┬───────────┘
                       │
         ┌─────────────▼─────────────┐
         │   Violation Processing    │
         │   • Severity Assignment   │
         │   • Context Extraction    │
         │   • Fix Suggestion        │
         └─────────────┬─────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
  ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
  │ Markdown│    │   PR    │    │   CI    │
  │ Report  │    │ Comment │    │ Status  │
  │         │    │         │    │ Checks  │
  └─────────┘    └─────────┘    └─────────┘
```

---

## Rule Categories & Detection

### 1. Engine Mixing (`engine-mix`) 🔴 CRITICAL

**What it detects:**
- Files importing both Playwright and Selenium
- Tests using both `page` and `driver`
- Mixed engine API calls

**Why it matters:**
Each engine has different behaviors, waiting mechanisms, and failure modes. Mixing them creates unpredictable tests.

**CI Status Check:** `audit/engine-mix`

---

### 2. Marker ↔ Engine (`marker-engine`) 🔴 CRITICAL

**What it detects:**
- Missing `@pytest.mark.modern_spa` or `@pytest.mark.legacy_ui`
- `@modern_spa` marker with Selenium imports
- `@legacy_ui` marker with Playwright imports

**Why it matters:**
Markers enable automatic engine routing. Mismatches cause wrong engine to be used.

**CI Status Check:** `audit/marker-engine`

---

### 3. Folder ↔ Engine (`folder-engine`) ❌ ERROR

**What it detects:**
- Playwright tests in `legacy/` folders
- Selenium tests in `modern/` folders

**Why it matters:**
Folder structure provides visual organization and quick identification of engine type.

**CI Status Check:** `audit/folder-engine`

---

### 4. POM Compliance (`pom-compliance`) ❌ ERROR

**What it detects:**
- `pytest` imports in Page Objects
- Assertions in Page Objects
- `time.sleep()` in Page Objects
- API/DB calls in Page Objects

**Why it matters:**
Page Objects are reusable UI models. Violations make them single-use and brittle.

**CI Status Check:** `audit/pom-compliance`

---

### 5. Test Boundaries (`test-boundaries`) ⚠️ WARNING

**What it detects:**
- Direct `page.locator()` calls in tests
- Direct `driver.find_element()` calls in tests

**Why it matters:**
UI logic scattered across tests is hard to maintain when UI changes.

**CI Status Check:** `audit/test-boundaries`

---

### 6. Structural (`structural`) ❌ ERROR

**What it detects:**
- Page Objects outside `/pages`
- Test files outside `/tests`
- `if __name__ == '__main__'` in test files

**Why it matters:**
Consistent structure makes codebase navigable and maintainable.

**CI Status Check:** `audit/structural`

---

### 7. Canonical Flow (`canonical-flow`) ℹ️ INFO

**What it detects:**
- Changes to `*_complete_flow*.py` files

**Why it matters:**
Complete flow tests define single source of truth for business logic.

**CI Status Check:** `audit/canonical-flow`

---

## Usage Examples

### Local Development

```bash
# Quick audit before committing
pytest --arch-audit

# Audit specific category
pytest --arch-audit --audit-category=pom-compliance

# Generate report
pytest --arch-audit --audit-report=my_audit.md

# Strict mode (fail on warnings)
pytest --arch-audit --audit-strict

# Show detailed fix suggestions
pytest --arch-audit --audit-show-fixes
```

### CI/CD

```bash
# Run all checks (from GitHub Actions)
python ci/ci_audit_runner.py --artifacts-dir artifacts/

# Run specific check
python ci/ci_audit_runner.py --check engine-mix

# With baseline suppression
python ci/ci_audit_runner.py --baseline ci/baseline_allowlist.yaml
```

### PR Comments

```bash
# Auto-comment on PR (from GitHub Actions)
export GITHUB_TOKEN="..."
python ci/github_pr_commenter.py --pr-number 123

# Dry run (preview comment)
python ci/github_pr_commenter.py --pr-number 123 --dry-run
```

---

## Baseline Management

### Purpose

Baseline allows temporary suppression of violations during gradual remediation of legacy code.

### Rules

1. **Every entry MUST have expiration date**
2. **Expired entries FAIL the build**
3. **Baseline usage is always reported**

### Example

```yaml
# ci/baseline_allowlist.yaml
violations:
  - file: tests/legacy/test_old_system.py
    rule: marker-engine/missing-engine-marker
    reason: Legacy suite pending migration to markers
    owner: qa-team
    created: 2026-02-01
    expires: 2026-03-31  # MANDATORY

  - file: pages/old_page.py
    rule: pom-compliance/assertion-in-page-object
    reason: Refactoring in progress
    owner: dev-team
    created: 2026-02-01
    expires: 2026-02-15
```

### Managing Baselines

```bash
# Check baseline status
cat ci/baseline_allowlist.yaml

# Audit will report:
# - Total baselined violations
# - Expired violations (treated as violations)
# - Violations expiring soon (within 30 days)
```

---

## Fix Suggestions

Every violation includes intelligent fix suggestions:

### Example: Missing Marker

**Violation:**
```python
class TestBooking:  # Missing marker
    def test_search(self, ui_engine):
        pass
```

**Fix Suggestion:**
```python
@pytest.mark.modern_spa  # For Playwright
# or
@pytest.mark.legacy_ui   # For Selenium

class TestBooking:
    def test_search(self, ui_engine):
        pass
```

### Example: POM Assertion

**Violation:**
```python
# Page Object
class LoginPage:
    def verify_login(self):
        assert self.is_logged_in()  # ❌ Assertion in POM
```

**Fix Suggestion:**
```python
# Page Object - Return data
class LoginPage:
    def is_logged_in(self) -> bool:
        return self.page.locator("#user-menu").is_visible()

# Test - Assert there
def test_login(ui_engine):
    page = LoginPage(ui_engine)
    page.login("user", "pass")
    assert page.is_logged_in()  # ✅ Assert in test
```

---

## CI Status Checks

Each rule category creates independent PR status check:

| Check | Status | Blocking |
|-------|--------|----------|
| `audit/engine-mix` | ✅ or ❌ | Yes |
| `audit/marker-engine` | ✅ or ❌ | Yes |
| `audit/folder-engine` | ✅ or ❌ | Yes |
| `audit/pom-compliance` | ✅ or ❌ | Yes |
| `audit/test-boundaries` | ✅ or ⚠️ | No (warnings) |
| `audit/structural` | ✅ or ❌ | Yes |
| `audit/canonical-flow` | ℹ️ | No (info) |

**Blocking checks must pass to merge PR.**

---

## Artifacts Generated

### Local Audit

- Terminal output with violations
- Optional: `audit_report.md`

### CI Pipeline

Per-check artifacts:
- `artifacts/<category>/summary.json`
- `artifacts/<category>/violations.md`

Combined artifacts:
- `artifacts/framework_audit_report.md` (comprehensive)

All artifacts uploaded to GitHub Actions for download.

---

## Integration Points

### 1. pytest conftest.py

Plugin registered automatically:
```python
pytest_plugins = ['scripts.governance.pytest_arch_audit_plugin']
```

### 2. GitHub Actions

Workflow: `.github/workflows/architecture-audit.yml`

Runs on:
- Pull requests
- Push to main
- Manual trigger

### 3. Pre-commit Hook (Optional)

```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest --arch-audit || exit 1
```

---

## Enforcement Levels

### CRITICAL 🔴
- **Engine mixing** - Absolutely forbidden
- **Marker/engine mismatch** - Framework won't work correctly

→ **Action:** Block CI, require immediate fix

### ERROR ❌
- **POM violations** - Breaks maintainability
- **Structural issues** - Breaks consistency

→ **Action:** Block CI, require fix before merge

### WARNING ⚠️
- **Test boundaries** - Should fix but not blocking
- **Best practices** - Recommendations

→ **Action:** Report but don't block

### INFO ℹ️
- **Canonical flow changes** - Flag for review
- **Documentation** - Advisory

→ **Action:** Notify only

---

## Performance

### Local Audit
- **Speed:** <2 seconds for full codebase
- **Method:** AST parsing (no imports/execution)
- **Files:** ~300+ files scanned

### CI Audit
- **Parallelization:** Independent checks run in parallel
- **Duration:** ~1-2 minutes total (parallelized)
- **Efficiency:** Category-specific checks for faster feedback

---

## Troubleshooting

### "Cannot import audit engine"

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/scripts/governance"
```

### "Baseline expired"

Edit `ci/baseline_allowlist.yaml` and update expiration or fix violation.

### "False positive"

1. Review rule definition in docs
2. If legitimate exception, add to baseline with justification
3. Set reasonable expiration date

### "Too many violations"

1. Use baseline for legacy code: add to `ci/baseline_allowlist.yaml`
2. Fix incrementally by category: `pytest --arch-audit --audit-category=<cat>`
3. Set realistic expiration dates

---

## Files Created

### Core Engine
- `scripts/governance/framework_audit_engine.py` (870 lines)
- `scripts/governance/framework_report_generator.py` (240 lines)
- `scripts/governance/framework_fix_suggestions.py` (480 lines)

### CI Integration
- `ci/ci_audit_runner.py` (360 lines)
- `ci/github_pr_commenter.py` (380 lines)
- `ci/baseline_allowlist.yaml` (structure + docs)

### Plugins
- `scripts/governance/pytest_arch_audit_plugin.py` (360 lines)

### AI System
- `scripts/governance/ai_explainer.py` (340 lines)

### Workflows
- `.github/workflows/architecture-audit.yml` (full CI/CD)

### Documentation
- `docs/GOVERNANCE_SYSTEM.md` (comprehensive guide)

**Total:** ~3,000 lines of enforcement code + documentation

---

## Success Criteria Met

✅ **Self-defending** - Architecture enforces itself  
✅ **Zero-tolerance** - No silent violations  
✅ **Deterministic** - All rules explicit  
✅ **Auditable** - Every decision explained  
✅ **Scalable** - Multi-project ready  
✅ **Maintainable** - Clear separation  

---

## Next Steps

### For Developers
1. Run `pytest --arch-audit` before committing
2. Review PR comments when audit fails
3. Apply fix suggestions
4. Ask questions if rules unclear

### For Architects
1. Monitor baseline entries and expiration
2. Review canonical flow changes
3. Adjust rules if false positives emerge
4. Educate team on governance system

### For CI/CD
1. Ensure GitHub Actions workflow is enabled
2. Set up `GITHUB_TOKEN` for PR comments
3. Monitor audit artifacts
4. Address baseline expirations proactively

---

## Contact

**Principal QA Architect:** Lokendra Singh  
**Email:** qa.lokendra@gmail.com  
**Website:** www.sqamentor.com

---

<div align="center">
  <strong>🛡️ Framework Governance System v1.0.0</strong><br>
  <sub>Self-defending • Zero-tolerance • Fully operational</sub><br><br>
  <sub>Implemented: February 1, 2026</sub>
</div>
