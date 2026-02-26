# CLI & Tooling — Complete Reference Guide

**Canonical source for all CLI documentation.**
Merges: `INTERACTIVE_CLI_GUIDE.md` · `HOW_TO_USE_INTERACTIVE_CLI.md` · `MODERN_MULTI_PROJECT_CLI.md` · `CLI_MODERNIZATION_IMPLEMENTATION.md`

**Status:** ✅ Production Ready
**Version:** 2.0.0 (Modern Unified CLI)
**Last Updated:** 2026-02-19

---

## Overview

The `automation` command is a **unified, modern CLI** for the Hybrid Automation Framework. It supports an interactive guided mode for non-technical users and direct subcommands for power users and CI/CD pipelines.

**Before (legacy):**
```bash
automation-run          # Run tests
automation-run-pom      # Run POM tests
automation-record       # Record tests
automation-simulate     # Simulate tests
```

**After (current — unified):**
```bash
automation              # Interactive mode (default) or help
automation run          # Run tests
automation run-pom      # Run POM tests
automation record       # Record tests
automation simulate     # Simulate tests
automation test <proj>  # Modern shorthand for project tests
automation projects     # Multi-project management
automation context      # Workspace context detection
```

The single `automation` entry point is registered in `pyproject.toml`:
```toml
[project.scripts]
automation          = "framework.cli:main"            # Primary (unified)
automation-run      = "framework.cli.run:main"        # Legacy (deprecated)
automation-record   = "framework.cli.record:main"     # Legacy (deprecated)
automation-simulate = "framework.cli.simulate:main"   # Legacy (deprecated)
```

---

## Quick Start

### Method 1: Interactive Mode (Easiest)

Just type:
```bash
automation
```

The launcher guides you through:
1. **Project Selection** — Choose from available projects
2. **Test Suite Selection** — Recorded, Modern, or Workflow tests
3. **Test File Selection** — Run all or a specific file
4. **Environment Selection** — Staging or Production
5. **Execution** — Watch tests run with full output

**Welcome Screen:**
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   🚀 AUTOMATION FRAMEWORK                              │
│   Interactive Test Launcher                            │
│                                                         │
│   Modern • Multi-Project • User-Friendly               │
│                                                         │
└─────────────────────────────────────────────────────────┘

📋 Select a Project:
  ✅ BookSlot Appointment System
  ⚠️  Call Center Management System
  ⚠️  Patient Intake System
  ❌ Exit
```

### Method 2: Quick-Start Scripts (Windows)

```bash
# Double-click batch file:
START_INTERACTIVE_MODE.bat

# Or right-click PowerShell script:
.\START_INTERACTIVE_MODE.ps1
```

### Method 3: Direct Commands (Power Users / CI/CD)

```bash
automation test bookslot --env staging
automation run-pom --project bookslot --env production
automation projects list
automation context
automation --help
```

---

## Interactive Mode — Step-by-Step

### Step 1: Launch

```bash
C:\Hybrid_Automation> automation
```

### Step 2: Select Project

```
? Select a Project:
  ✅ BookSlot Appointment System
     Patient appointment booking and slot management system (Team: Booking Team)
  ⚠️  Call Center Management System
     Call center operations and appointment management (Team: Call Center Team)
  ⚠️  Patient Intake System
     Patient intake and appointment management system (Team: Intake Team)
  ❌ Exit
```

**Icons:** ✅ = tests available · ⚠️ = configured but no tests detected · ❌ = exit

### Step 3: Select Test Suite

```
? Available Test Suites for bookslot:
  📹 Recorded Tests              (4 tests)
  🎭 Modern Tests (Playwright)   (8 tests)
  ⬅️  Back to project selection
  ❌ Exit
```

### Step 4: Select Test File

```
? Select a test file:
  🚀 Run All Tests
  📄 test_bookslot_complete_workflow.py
  📄 test_bookslot_basicinfo_validation_20260202_180102.py
  📄 test_video_link_simple.py
  📄 test_bookslot_prod_Worklfow_Complete.py
  ⬅️  Back to suite selection
```

### Step 5: Select Environment

```
? Select Environment:
  🎭 STAGING      https://bookslot-staging.centerforvein.com
  🚀 PRODUCTION   https://bookslots.centerforvein.com
  ⬅️  Back to test selection
```

### Step 6: Review and Execute

```
┌─────────────────────────────────────────────────────────┐
│          📋 Test Execution Summary                      │
├─────────────────────────────────────────────────────────┤
│ Project     │ BOOKSLOT                                  │
│ Test Suite  │ 📹 Recorded Tests                         │
│ Test File   │ test_bookslot_complete_workflow.py        │
│ Environment │ STAGING                                   │
│ Path        │ recorded_tests/bookslot                   │
└─────────────────────────────────────────────────────────┘
? Ready to execute tests? (Y/n)
```

**Command generated:**
```bash
python -m pytest recorded_tests/bookslot/test_bookslot_complete_workflow.py \
  --env=staging -v --tb=short --color=yes
```

### Step 7: After Tests Complete

```
✅ Tests completed successfully!
? Would you like to run more tests? (Y/n)
? Continue with the same project? (Y/n)
```

---

## Available Commands

### `automation projects` — Multi-Project Management

```bash
automation projects list                   # List all projects
automation projects info bookslot          # Show project details
automation projects detect <url>           # Detect project from URL
```

**`projects list` output:**
```
📋 Available Projects:

  📁 bookslot
     ID: BookSlot Appointment System
     Description: Patient appointment booking and slot management system
     Team: Booking Team

  📁 callcenter
     ID: Call Center Management System
     Description: Call center operations and appointment management
     Team: Call Center Team

  📁 patientintake
     ID: Patient Intake System
     Description: Patient intake and appointment management system
     Team: Patient Services Team

Total: 3 project(s)
```

**`projects detect` output:**
```
🔍 Project Detection Results:
  URL: https://bookslot-staging.centerforvein.com
  Detected Project: bookslot
  Environment: staging
  Full Name: BookSlot Appointment System
```

### `automation context` — Workspace Context

```bash
automation context
```

**Output from root:**
```
📍 Current Context:
  ✓ Inside workspace
  📁 Workspace Root: C:\path\to\Hybrid_Automation
  📂 Current Dir: .
  ⚠️  No project detected (not in project-specific directory)

📦 Available Projects:
  • bookslot          BookSlot Appointment System
  • callcenter        Call Center Management System
  • patientintake     Patient Intake System
```

**Output from project directory:**
```
📍 Current Context:
  ✓ Inside workspace
  📁 Workspace Root: C:\path\to\Hybrid_Automation
  📂 Current Dir: pages/bookslot
  🎯 Detected Project: bookslot
```

### `automation test` — Project Test Shorthand

```bash
automation test bookslot --env staging     # Run bookslot tests
automation test                            # Interactive mode
```

Maps internally to `automation run-pom`.

---

## Root Execution (Context-Aware)

The CLI auto-detects the workspace root by searching upward for:
- `pyproject.toml`
- `pytest.ini`
- `framework/` directory
- `.git` directory

This enables running commands **from any subdirectory**:

```bash
# From root
automation projects list         # ✓

# From project directory
cd pages/bookslot
automation context               # ✓ Shows: Detected Project: bookslot

# From test directory
cd recorded_tests/callcenter
automation test callcenter       # ✓

# From nested subdirectory
cd pages/bookslot/components
automation context               # ✓ Still detects bookslot
```

---

## Available Projects

### BookSlot (✅ Most Tests Available)

| Property | Value |
|----------|-------|
| Key | `bookslot` |
| Name | BookSlot Appointment System |
| Team | Booking Team |
| Staging | https://bookslot-staging.centerforvein.com |
| Production | https://bookslots.centerforvein.com |
| Test Types | Recorded (4), Modern/Playwright (8) |

**Recommended first test:** `test_video_link_simple.py`

### Call Center (⚠️ Limited)

| Property | Value |
|----------|-------|
| Key | `callcenter` |
| Name | Call Center Management System |
| Team | Call Center Team |
| Staging | https://staging-callcenter.centerforvein.com |
| Production | https://callcenter.centerforvein.com |
| Test Types | Modern/Playwright (1) |
| Note | Requires SSO authentication |

### Patient Intake (⚠️ Limited)

| Property | Value |
|----------|-------|
| Key | `patientintake` |
| Name | Patient Intake System |
| Team | Intake Team |
| Staging | https://staging-patientintake.centerforvein.com |
| Production | https://patientintake.centerforvein.com |
| Test Types | Modern/Playwright (1) |

---

## Test Suite Types

| Suite | Location | Technology | Best For |
|-------|----------|------------|----------|
| 📹 Recorded Tests | `recorded_tests/<project>/` | Hybrid | Quick validation, regression |
| 🎭 Modern Tests | `tests/modern/<project>/` | Playwright | Modern SPAs |
| 🌐 Legacy Tests | `tests/legacy/<project>/` | Selenium | Legacy apps, browser compat |
| 🔄 Workflow Tests | `tests/workflows/` | Hybrid | Integration, user journeys |

---

## CLI Architecture

### File Layout

```
framework/
└── cli/
    ├── __init__.py       # Main router (unified entry point)
    ├── projects.py       # Project management commands
    ├── context.py        # Workspace context detection
    ├── run.py            # General test runner
    ├── run_pom.py        # POM test runner
    ├── record.py         # Test recording CLI
    └── simulate.py       # Test simulation CLI
```

### Router Logic (`framework/cli/__init__.py`)

```python
def main(args=None):
    if not args or args[0] in ['-h', '--help', 'help']:
        print_help(); return 0

    command = args[0]
    remaining_args = args[1:]

    if command == 'run':
        from framework.cli.run import main as run_main
        return run_main(remaining_args)
    elif command == 'run-pom':
        from framework.cli.run_pom import main as run_pom_main
        return run_pom_main(remaining_args)
    elif command == 'projects':
        from framework.cli.projects import main as projects_main
        return projects_main(remaining_args)
    elif command == 'context':
        from framework.cli.context import print_workspace_info
        print_workspace_info(); return 0
    elif command == 'test':
        from framework.cli.run_pom import main as run_pom_main
        return run_pom_main(remaining_args)
    elif command in ('interactive', 'i', ''):
        # Launch interactive mode
        ...
```

### Context Detection (`framework/cli/context.py`)

```python
class WorkspaceContext:
    def _find_workspace_root(self):
        """Search upward for workspace markers"""
        markers = ['pyproject.toml', 'pytest.ini', 'framework', '.git']
        # Search up to 10 levels

    def _detect_current_project(self):
        """Detect project from directory structure"""
        # Check if in pages/, recorded_tests/, test_data/
        # Extract project name from path
```

---

## Industry Standards Alignment

| Framework | CLI Pattern | Our Equivalent |
|-----------|-------------|----------------|
| **Nx** | `nx run project:target` | `automation test bookslot` |
| **Turborepo** | `turbo run test --filter=project` | `automation test bookslot --env staging` |
| **npm workspaces** | `npm run test -w project` | `automation test --project bookslot` |
| **Playwright** | `playwright test` | `automation run-pom` |
| **Cypress** | `cypress run` | `automation run` |

---

## CI/CD Integration

```bash
# Run specific project in CI
automation test bookslot --env staging --headless

# Run all projects sequentially
for project in bookslot callcenter patientintake; do
  automation test $project --env production
done

# Or use pytest directly
pytest recorded_tests/bookslot/ --env=staging -v --tb=short
```

---

## Navigation Guide

| Key | Action |
|-----|--------|
| ↑ / ↓ | Navigate between options |
| Enter | Select option |
| Ctrl+C | Exit immediately |

| Icon | Meaning |
|------|---------|
| ✅ | Available / Ready |
| ⚠️ | Warning / Limited |
| ❌ | Exit / Cancel |
| 🚀 | Production / Execute |
| 🎭 | Staging / Test |
| ⬅️ | Back / Previous |
| 📄 | Test file |
| 📋 | Menu / List |

---

## Tips & Best Practices

1. **Always use Staging first** — never test on Production without verifying in Staging
2. **Review the summary** before confirming execution
3. **"Continue with same project?"** — answer Yes to save time on repeat runs
4. **Read descriptions** — every menu option includes a description
5. **Use "Run All"** for regression; specific tests for debugging

---

## Troubleshooting

### `'automation' not found`
```bash
pip install -e .          # Reinstall package
python -m framework.cli   # Or use full path
```

### `Interactive mode requires additional packages`
```bash
pip install rich questionary
# Or:
pip install -r requirements.txt
```

### Tests fail with browser errors
```bash
playwright install chromium   # Install required browser
playwright install             # Install all browsers
```

### Colors not rendering
Use **Windows Terminal** or **PowerShell 7+**. Avoid legacy `cmd.exe`.

### `No projects found in configuration`
Check that `config/projects.yaml` exists and is correctly populated.

### `No test suites found`
Verify test files exist under `recorded_tests/<project>/test_*.py` or `tests/modern/<project>/test_*.py`.

---

## Verification

```bash
# Install package
pip install -e .

# Test all CLI commands
automation
automation --help
automation projects list
automation projects info bookslot
automation context
automation run --help
automation run-pom --help

# Check installed entry points
pip show -f enterprise-automation-framework | grep automation
```

---

## Future Enhancements

- [ ] Test scheduling and queuing
- [ ] Parallel execution across projects
- [ ] Execution history viewer
- [ ] Favorite configurations
- [ ] Custom test data selection
- [ ] In-terminal report viewer
- [ ] CI/CD configuration generator
- [ ] `automation init` — guided new-project wizard
- [ ] `automation doctor` — diagnose setup issues

---

## Contact

- **Email:** lokendra.singh@centerforvein.com
- **Website:** www.centerforvein.com
- **GitHub:** sqamentor/Hybrid_Automation
