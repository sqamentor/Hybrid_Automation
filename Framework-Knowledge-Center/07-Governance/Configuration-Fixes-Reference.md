# Configuration Fixes Reference

**Canonical source for pytest configuration fixes and known issues.**
Source: `PYTEST_CONFIG_FIXES.md`

**Status:** ✅ Fixed — Production Ready
**Version:** 2.1.1
**Date:** February 19, 2026

---

## Overview

This document records the three configuration fixes applied to `pytest.ini` and `framework/cli/test_options.py` to resolve pytest marker errors, config warnings, and missing marker registrations.

---

## Fix 1: Marker Expression Syntax Error

**Severity:** CRITICAL (tests would not run with marker filtering)

### Symptom

```
ERROR: Wrong expression passed to '-m': "human_behavior":
at column 1: expected not OR left parenthesis OR identifier; got string literal
```

### Root Cause

The marker expression was wrapped in extra quotes in the pytest command, making pytest treat it as a string literal instead of a marker name.

**Location:** `framework/cli/test_options.py` line ~397

### Before (broken)

```python
if all_markers:
    marker_expr = " or ".join(all_markers)
    cmd.extend(["-m", f'"{marker_expr}"'])  # ❌ Extra quotes cause error
```

### After (fixed)

```python
if all_markers:
    marker_expr = " or ".join(all_markers)
    cmd.extend(["-m", marker_expr])  # ✅ No extra quotes
```

### Verification

```bash
python -m pytest --collect-only -m "human_behavior"
# Result: collected 302 items / 301 deselected / 1 selected
# No "Wrong expression" error
```

### Multi-Marker Example

```bash
# Single marker (fixed)
python -m pytest ... -m human_behavior

# Complex expression (also works)
python -m pytest ... -m "human_behavior or smoke"
```

---

## Fix 2: `asyncio_mode` Config Warning

**Severity:** MEDIUM (warning noise in every test run)

### Symptom

```
PytestConfigWarning: Unknown config option: asyncio_mode
  C:\...\site-packages\_pytest\config\__init__.py:1474:
  PytestConfigWarning: Unknown config option: asyncio_mode
```

### Root Cause

`pytest.ini` had `asyncio_mode = strict` set, but pytest-asyncio was disabled via `-p no:asyncio` in `addopts`. When the plugin is disabled, pytest doesn't recognize its config option.

**Location:** `pytest.ini`

### Before (broken)

```ini
# Asyncio Configuration
asyncio_mode = strict  # ❌ Causes warning when plugin is disabled
```

### After (fixed)

```ini
# Asyncio Configuration
# Disabled via -p no:asyncio flag (for Playwright sync API compatibility)
# asyncio_mode = strict  # ✅ Commented out
```

### Why `-p no:asyncio`?

The framework uses Playwright's **synchronous API** (`playwright.sync_api`). The pytest-asyncio plugin interferes with sync test collection. Disabling it via `-p no:asyncio` in `pytest.ini addopts` allows sync tests to run normally.

### Verification

```bash
python -m pytest --collect-only --quiet 2>&1 | grep "asyncio_mode"
# No output — warning gone
```

---

## Fix 3: Missing `human_behavior` Marker Registration

**Severity:** LOW (marker unregistered, potential unknown-marker warnings)

### Symptom

Running `pytest --markers` did not show `human_behavior`, and using it without registration could trigger:
```
PytestUnknownMarkWarning: Unknown pytest.mark.human_behavior
```

### Root Cause

The `human_behavior` marker used by the interactive CLI was not registered in `pytest.ini`.

**Location:** `pytest.ini` markers section

### Before (incomplete)

```ini
# Human behavior markers
human_like: Apply human-like behavior simulation
no_human_behavior: Disable human behavior for this test
# ❌ Missing: human_behavior (used by CLI via --enable-human-behavior)
```

### After (fixed)

```ini
# Human behavior markers
human_behavior: Enable human behavior simulation (typing delays, mouse movements, etc.)
human_like: Apply human-like behavior simulation (typing delays, mouse movements, etc.)
no_human_behavior: Disable human behavior for this test (faster execution)
```

### Verification

```bash
python -m pytest --markers | grep "human_behavior"
# Output:
# @pytest.mark.human_behavior: Enable human behavior simulation...
# @pytest.mark.no_human_behavior: Disable human behavior for this test...
```

---

## All Verified Fixes (Summary)

| Fix | File | Status |
|-----|------|--------|
| Marker expression quotes removed | `framework/cli/test_options.py:397` | ✅ Fixed |
| `asyncio_mode` commented out | `pytest.ini:18` | ✅ Fixed |
| `human_behavior` marker added | `pytest.ini` markers section | ✅ Fixed |

---

## Generated Command Examples

### Before (all three bugs present)

```bash
python -m pytest --project=bookslot --env=staging \
  tests/test_login.py --test-browser=chromium --headless \
  -m "human_behavior" \      # ❌ Quoted — causes error
  -p no:asyncio
# Also: PytestConfigWarning: Unknown config option: asyncio_mode
# Also: PytestUnknownMarkWarning: Unknown pytest.mark.human_behavior
```

### After (all bugs fixed)

```bash
python -m pytest --project=bookslot --env=staging \
  tests/test_login.py --test-browser=chromium --headless \
  -m human_behavior \        # ✅ No quotes — works
  -p no:asyncio
# No config warnings. Marker filtering works.
```

---

## Interactive CLI Verification

All 8/8 interactive CLI tests pass after these fixes:

| Test | Status |
|------|--------|
| BrowserConfig | ✅ |
| HumanBehaviorConfig — markers work correctly | ✅ |
| ExecutionConfig | ✅ |
| ReportConfig | ✅ |
| FullTestConfig — command generation fixed | ✅ |
| ConfigPresets | ✅ |
| InteractiveLauncher | ✅ |
| Marker filtering (`-m human_behavior`) | ✅ |

---

## Current `pytest.ini` — Relevant Sections

```ini
[pytest]
# --- Core options ---
addopts =
    -p no:asyncio
    --self-contained-html
    --tb=short
    -v

# --- Markers ---
markers =
    playwright: Test uses Playwright engine
    selenium: Test uses Selenium engine
    bookslot: BookSlot project test
    callcenter: CallCenter project test
    patientintake: PatientIntake project test
    e2e: End-to-end test
    recorded: Recorded test
    modern_spa: Modern SPA test
    human_behavior: Enable human behavior simulation
    human_like: Apply human-like behavior simulation
    no_human_behavior: Disable human behavior for this test
    smoke: Smoke test (critical path only)
    regression: Regression test

# --- Asyncio (disabled) ---
# asyncio_mode = strict  # Commented out — plugin disabled via -p no:asyncio
```

---

## Related Files

| File | Role |
|------|------|
| `pytest.ini` | Marker registration, addopts, asyncio config |
| `framework/cli/test_options.py` | Marker expression building for pytest command |
| `conftest.py` (root) | Fixture definitions, pytest hooks |
| `Framework-Knowledge-Center/07-Governance/Architecture-Governance.md` | Full governance system |
