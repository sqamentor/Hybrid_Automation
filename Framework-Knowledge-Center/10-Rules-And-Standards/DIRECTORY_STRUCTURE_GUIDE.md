# Modern Automation Framework - Directory Structure

## Overview

This document describes the modern, organized directory structure of the Hybrid Automation Framework, optimized for multi-project testing with Playwright and Selenium.

---

## 📁 Root Directory Structure

```
Hybrid_Automation/
├── 📦 Core Framework Components
├── 🎯 Multi-Project Test Organization
├── ⚙️ Configuration Management
├── 🛠️ Organized Scripts & Tools
├── 📊 Test Artifacts & Outputs
├── 📚 Documentation Hub
├── 🐳 DevOps & CI/CD
└── 🔧 Project Configuration Files
```

---

## 📦 Core Framework Components

### `framework/` - Core Framework Code

**Purpose**: All framework source code organized by functionality

```
framework/
├── cli/                    # Modern unified CLI
│   ├── __init__.py        # Main router (automation command)
│   ├── projects.py        # Project management commands
│   ├── context.py         # Workspace context detection
│   ├── run.py             # General test runner
│   ├── run_pom.py         # POM test runner
│   ├── record.py          # Test recording CLI
│   └── simulate.py        # Test simulation CLI
│
├── core/                   # Core framework logic
│   ├── actions.py         # Smart actions (engine-agnostic)
│   ├── engine_selector.py # Intelligent engine selection
│   ├── workflow_orchestrator.py
│   └── project_manager.py # Multi-project management
│
├── ui/                     # UI automation engines
│   ├── playwright_engine.py
│   ├── selenium_engine.py
│   ├── base_page.py       # BasePage for POM
│   └── self_healing.py    # Self-healing locators
│
├── api/                    # API testing
│   ├── api_client.py
│   ├── interceptor.py
│   ├── graphql_client.py
│   └── websocket_client.py
│
├── database/               # Database testing
│   ├── db_validator.py
│   ├── query_builder.py
│   └── async_connection.py
│
├── ai/                     # AI capabilities
│   ├── providers/         # OpenAI, Anthropic, etc.
│   ├── nl_test_generator.py
│   └── validation_generator.py
│
├── intelligence/           # ML & intelligent features
│   ├── self_healing.py
│   ├── ml_optimizer.py
│   └── pattern_recognition.py
│
├── visual/                 # Visual testing
│   └── visual_regression.py
│
├── accessibility/          # Accessibility testing
│   └── wcag_validator.py
│
├── security/               # Security testing
│   └── owasp_scanner.py
│
├── performance/            # Performance testing
│   └── metrics_collector.py
│
└── observability/          # Enterprise logging
    ├── logger.py
    ├── tracer.py
    └── monitor.py
```

**Standards**:
- All imports use absolute paths: `from framework.core.actions import SmartActions`
- Each module has `__init__.py` for proper package structure
- Type hints required for all public APIs
- Comprehensive docstrings following Google style

---

## 🎯 Multi-Project Test Organization

### Projects

This framework supports **three projects**:

1. **bookslot** - Appointment booking system (SPA, Playwright-first)
2. **callcenter** - Call center management (hybrid UI)
3. **patientintake** - Patient intake system (hybrid UI)

### `pages/` - Page Object Model

**Purpose**: Page objects organized by project (engine-agnostic)

```
pages/
├── bookslot/
│   ├── __init__.py
│   ├── appointment_page.py
│   ├── calendar_page.py
│   └── confirmation_page.py
│
├── callcenter/
│   ├── __init__.py
│   ├── dashboard_page.py
│   └── appointment_search_page.py
│
└── patientintake/
    ├── __init__.py
    ├── patient_verification_page.py
    └── appointment_list_page.py
```

**Standards**:
- All pages extend `BasePage` from `framework.ui.base_page`
- Use smart actions for engine abstraction
- Include docstrings with usage examples

### `tests/` - Test Suites

**Purpose**: Tests organized by type and project

```
tests/
├── modern/                 # Playwright tests (SPAs)
│   ├── bookslot/
│   ├── callcenter/
│   └── patientintake/
│
├── legacy/                 # Selenium tests (legacy UI)
│
├── workflows/              # Cross-engine E2E tests
│   └── test_three_system_workflow.py
│
├── integration/            # Integration tests
│   └── test_three_system_workflow.py
│
├── unit/                   # Unit tests (no engine)
│   ├── test_engine_selector.py
│   ├── test_smart_actions.py
│   └── test_config_models.py
│
├── examples/               # Example implementations
│   └── test_complete_features_integration.py
│
└── conftest.py            # Test fixtures
```

**Standards**:
- Use pytest markers: `@pytest.mark.playwright`, `@pytest.mark.selenium`
- Project-specific markers: `@pytest.mark.bookslot`
- Follow naming: `test_<feature>_<scenario>.py`

### `recorded_tests/` - Recorded Test Suites

**Purpose**: Tests generated from recording CLI

```
recorded_tests/
├── bookslot/
│   ├── test_bookslot_complete_workflow.py
│   └── README.md
│
├── callcenter/
│   └── __init__.py
│
├── patientintake/
│   └── __init__.py
│
└── _archived/              # Old/deprecated tests
```

### `test_data/` - Test Data

**Purpose**: Test data organized by project

```
test_data/
├── bookslot/
│   ├── bookslot_data.yaml
│   ├── bookslot_data.json
│   ├── bookslot_young_patients.yaml
│   └── bookslot_senior_patients.yaml
│
├── callcenter/
│   └── __init__.py
│
└── patientintake/
    └── __init__.py
```

**Standards**:
- Support both YAML and JSON formats
- Environment-specific data in subdirectories
- Use Faker for dynamic data generation

---

## ⚙️ Configuration Management

### `config/` - Configuration Files

**Purpose**: All framework configuration in one place

```
config/
├── engine_decision_matrix.yaml  # Engine selection rules
├── environments.yaml            # Environment configs (staging, prod)
├── projects.yaml                # Multi-project definitions
├── human_behavior.yaml          # Behavior simulation settings
├── logging_config.yaml          # Enterprise logging config
├── api_db_mapping.yaml          # API-DB validation mappings
└── settings.py                  # Framework settings manager
```

### Root Configuration Files

```
├── pyproject.toml              # Python project config, dependencies, CLI entries
├── pytest.ini                  # Pytest configuration
├── conftest.py                 # Root pytest fixtures
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── .editorconfig               # Editor settings
├── .pre-commit-config.yaml     # Pre-commit hooks
└── .yamllint.yaml              # YAML linting rules
```

---

## 🛠️ Organized Scripts & Tools

### `scripts/` - Utility Scripts (Categorized)

**Purpose**: All scripts organized by purpose

```
scripts/
├── setup/                  # Installation & Setup
│   ├── install_missing_dependencies.ps1
│   ├── setup_ai.py
│   └── firstrun
│
├── runners/                # Test Execution Scripts
│   ├── run_pom.bat
│   └── run_pom.ps1
│
├── validation/             # Validation & Verification
│   ├── verify_installation.py
│   ├── verify_complete.py
│   ├── validate_video_naming.py
│   ├── verify_media_capture.py
│   ├── verify_governance_system.py
│   └── test_minimal_playwright.py
│
├── audit/                  # Architecture Audit
│   └── deep_audit.py
│
├── cli/                    # Legacy CLI (deprecated)
│   └── (old CLI scripts - use framework/cli/ instead)
│
├── governance/             # Governance Enforcement
│   └── architecture_enforcer.py
│
├── quick-start/            # Quick Start Utilities
│   ├── quick_start.py
│   ├── quick_test_config.py
│   └── quick_governance_audit.py
│
└── utilities/              # Miscellaneous Utilities
    ├── debug_fixture.py
    ├── cleanup_pages.py
    ├── check_dependencies.py
    └── visual_proof_test.py
```

**Standards**:
- Category-based organization (not flat structure)
- Clear naming: `verb_noun.py` (e.g., `verify_installation.py`)
- Include docstrings and usage instructions
- Support both Python and PowerShell where needed

---

## 📊 Test Artifacts & Outputs

### `artifacts/` - Organized Test Outputs

**Purpose**: All test execution outputs in one location

```
artifacts/
├── screenshots/            # Test screenshots (organized by test run)
├── videos/                 # Test recordings (dynamic naming)
├── traces/                 # Playwright traces
├── logs/                   # Execution logs (per test run)
├── reports/                # Audit & compliance reports
│   ├── PROJECT_AUDIT_REPORT.json
│   └── LOGGING_COMPLIANCE_REPORT.txt
└── temp/                   # Temporary files (temp test files, etc.)
```

### Other Output Directories

```
├── reports/                # HTML/Allure test reports
├── allure-results/         # Allure test results (JSON)
└── log/                    # Legacy log directory (for compatibility)
```

**Standards**:
- Dynamic naming: `{project}_{env}_{timestamp}`
- Organized by test run/session
- Automatic cleanup of old artifacts
- `.gitignore` excludes all artifacts (keeps structure)

---

## 📚 Documentation Hub

### `Framework-Knowledge-Center/` - Complete Documentation

**Purpose**: Comprehensive framework documentation

```
Framework-Knowledge-Center/
├── INDEX.md                        # Documentation index
├── 02-Core-Concepts/
│   ├── Engine-Selection-System.md
│   └── Smart-Actions.md
├── 03-Page-Object-Model/
├── 05-Observability-And-Logging/
│   └── Enterprise-Logging-System.md
├── 07-Governance/
│   ├── Architecture-Governance.md
│   └── DYNAMIC_REPORT_NAMING_IMPLEMENTATION.md
├── 08-Media-Capture/
│   ├── Screenshot-Video-Implementation.md
│   ├── DYNAMIC_VIDEO_NAMING_IMPLEMENTATION.md
│   └── VIDEO_NAMING_AUDIT_REPORT.md
└── 10-Rules-And-Standards/
    ├── CLI_MODERNIZATION_IMPLEMENTATION.md
    └── MODERN_MULTI_PROJECT_CLI.md
```

### `docs/` - Documentation Symlink

**Purpose**: Standard `docs/` location (links to Knowledge Center)

```
docs/
└── README.md               # Links to Framework-Knowledge-Center
```

### Root Documentation

```
├── README.md               # Main documentation (comprehensive)
└── LICENSE                 # MIT License
```

---

## 🐳 DevOps & CI/CD

### DevOps Structure

```
├── .github/                # GitHub specific
│   ├── workflows/         # GitHub Actions
│   └── ISSUE_TEMPLATE/
│
├── ci/                     # CI/CD configurations
│   └── (CI configs)
│
├── docker/                 # Docker configurations
│   └── (Dockerfiles)
│
└── examples/               # Example configurations
    └── (various examples)
```

---

## 🔧 Supporting Directories

### `models/` - Data Models

**Purpose**: Shared data models and fixtures

```
models/
├── __init__.py
├── appointment.py
├── patient.py
└── test_context.py
```

### `utils/` - Shared Utilities

**Purpose**: Framework-level utilities (not in framework/)

```
utils/
├── __init__.py
├── fake_data_generator.py
├── logger.py               # Utility logger config
└── file_utils.py
```

---

## 📊 Directory Access Patterns

### From Root

```bash
# Run tests from root
automation test bookslot --env staging

# Check context
automation context

# List projects
automation projects list
```

### From Project Directory

```bash
# Navigate to project
cd pages/bookslot

# Context-aware execution
automation context
# Shows: Detected Project: bookslot

# Run tests
automation test bookslot --env staging
```

### From Subdirectory

```bash
# Navigate deep
cd recorded_tests/bookslot/tests

# Still works - auto-detects workspace root
automation projects list
```

---

## 🎯 Organization Benefits

### 1. **Multi-Project Support**
- Clear separation by project (bookslot, callcenter, patientintake)
- Consistent structure across projects
- Easy to add new projects

### 2. **Artifact Separation**
- All outputs in `artifacts/` directory
- Clean root directory
- Easy cleanup and backup

### 3. **Script Organization**
- Categorized by purpose (setup, validation, audit)
- No flat script directory
- Easy to find what you need

### 4. **Modern CLI**
- Unified `automation` command
- Project-aware execution
- Context detection from any directory

### 5. **Documentation Hub**
- Centralized documentation
- Easy to navigate
- Comprehensive coverage

---

## 🚀 Migration from Old Structure

### What Changed

| Old Location | New Location | Reason |
|-------------|--------------|--------|
| `root/deep_audit.py` | `scripts/audit/` | Categorization |
| `root/setup_ai.py` | `scripts/setup/` | Setup scripts together |
| `root/verify_*.py` | `scripts/validation/` | Validation together |
| `root/run_pom.*` | `scripts/runners/` | Execution scripts |
| `root/screenshots/` | `artifacts/screenshots/` | Artifact organization |
| `root/videos/` | `artifacts/videos/` | Artifact organization |
| `root/PROJECT_AUDIT_REPORT.json` | `artifacts/reports/` | Reports together |

### Backward Compatibility

- Old paths still work via symbolic links (if created)
- Legacy scripts updated with new paths
- `.gitignore` updated for new structure

---

## 📝 Maintenance Guidelines

### Adding New Projects

1. Add project to `config/projects.yaml`
2. Create directories: `pages/<project>/`, `tests/modern/<project>/`, etc.
3. Update documentation

### Adding New Scripts

1. Determine category (setup/validation/audit/utilities)
2. Place in appropriate `scripts/<category>/`
3. Name clearly: `verb_noun.py`
4. Add docstring and usage instructions

###Organizing Artifacts

1. All outputs go to `artifacts/`
2. Use dynamic naming with timestamps
3. Organize by test run/session
4. Configure `.gitignore` to exclude content

---

## 🔗 Related Documentation

- [Modern Multi-Project CLI](../Framework-Knowledge-Center/10-Rules-And-Standards/MODERN_MULTI_PROJECT_CLI.md)
- [CLI Modernization](../Framework-Knowledge-Center/10-Rules-And-Standards/CLI_MODERNIZATION_IMPLEMENTATION.md)
- [Main README](../README.md)

---

**Status**: ✅ Complete - Modern Organization Implemented (Feb 2026)
