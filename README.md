# 🚀 Enterprise Hybrid Automation Framework

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**Enterprise-grade, AI-powered, dual-engine test automation platform for healthcare web applications with intelligent engine selection, multi-layer validation, SOC2-ready audit logging, and automatic architecture governance.**

| Metadata | Value |
|---|---|
| **Version** | 1.0.0 (`enterprise-automation-framework`) |
| **Audit Date** | 26-Feb-2026 |
| **Python** | 3.12+ (strict minimum, leverages `match/case`) |
| **License** | MIT |
| **Owner** | Lokendra Singh (lokendra.singh@centerforvein.com) |

---

## 📋 Table of Contents

- [Executive Summary](#-executive-summary)
- [Product Overview & Purpose](#-product-overview--purpose)
- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Core Features](#-core-features)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [CLI Reference](#-cli-reference)
- [Running Tests](#-running-tests)
- [Page Object Model](#-page-object-model)
- [Test Suite Architecture](#-test-suite-architecture)
- [Observability & Logging](#-observability--logging)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Architecture Governance](#-architecture-governance)
- [Technology Stack](#-technology-stack)
- [Documentation Hub](#-documentation-hub)
- [Key Principles & Rules](#-key-principles--rules)
- [Known Gaps & Recommendations](#-known-gaps--recommendations)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)
- [Support & Contact](#-support--contact)

---

## 📝 Executive Summary

The Hybrid Automation Framework is an enterprise-grade, end-to-end test automation platform built for the **Center for Vein Care**'s digital ecosystem. It automates testing across **three interconnected web applications**:

| Application | Purpose | Auth |
|---|---|---|
| **BookSlot** | Patient appointment booking (7-step multi-page flow) | Public (OTP-based) |
| **CallCenter** | Back-office appointment management for agents | SSO required |
| **PatientIntake** | Patient-facing appointment list & intake management | SSO required |

### Audit Statistics (Feb 2026)

| Metric | Count |
|---|---|
| Total source files | ~260 Python + YAML/JSON/config |
| Test files | ~60 |
| Page Object classes | 11 (7 bookslot + 2 callcenter + 2 patientintake) |
| Framework modules | 40+ across 20+ packages |
| Configuration files | 10 YAML/INI/TOML |
| GitHub Actions workflows | 5 CI/CD pipelines |
| Log stream categories | 8 separate log file types |
| Pytest markers | 40+ registered markers |

---

## 🎯 Product Overview & Purpose

### Business Context

Center for Vein Care operates three interconnected portals for patient appointment scheduling and management. This framework automates:

1. **Full 7-step patient appointment booking** (BookSlot P1→P7)
2. **Appointment verification and cancellation** (CallCenter, PatientIntake)
3. **Cross-system data consistency validation** (all 3 systems simultaneously)

### Product Goals

| ID | Goal |
|---|---|
| G1 | Automate regression, smoke, and E2E test coverage for all 3 applications |
| G2 | Support both modern SPAs and legacy pages via dual-engine approach |
| G3 | Provide SOC2-ready audit logs for healthcare compliance (HIPAA context) |
| G4 | Enable AI-assisted test recording, refactoring, and engine selection |
| G5 | Allow human-like browser interactions to avoid bot detection |
| G6 | Record video evidence for every test execution automatically |
| G7 | Generate rich HTML + Allure reports with embedded video links |
| G8 | Support multi-environment testing (staging, production read-only) |

### Stakeholders

- **QA Engineers** — Primary users (write/run tests)
- **Developers** — Review test results, integrate into CI/CD
- **Product Managers** — View HTML/Allure reports
- **Compliance Team** — Review audit logs (SOC2, HIPAA context)
- **DevOps** — Maintain CI/CD pipelines, Docker execution

---

## 🏛️ System Architecture

### Dual-Engine Architecture

The framework uses a **DUAL-ENGINE** architecture:

- **Playwright** — Primary engine for modern SPAs (React/Vue/Angular)
- **Selenium** — Fallback engine for legacy systems, SSO/MFA, iframe-heavy pages

```
Test Metadata (module, markers, url, complexity)
       │
       ▼
[AI Engine Selector] → GPT-4 / Claude / Azure / Ollama / LlamaCPP
       │          (Confidence ≥ 80%, cached, retry with backoff)
       ▼
[YAML Engine Selector] ← Falls back if AI unavailable
       │          (18 priority-weighted rules, LRU cache)
       ▼
[Modern Engine Selector] ← Python 3.12 match/case pattern matching
       │          (Frozen dataclasses, @lru_cache, 6 main patterns)
       ▼
[UIFactory] → PlaywrightEngine | SeleniumEngine
       │
       ▼
[Fallback Logic] → Playwright → Selenium on engine-level failures only
```

### Architectural Layers

```
[TEST LAYER]         tests/ → bookslot, integration, modern, unit, workflows, examples
[PAGE OBJECT LAYER]  pages/ → bookslot (7 pages), callcenter (2), patientintake (2)
[FRAMEWORK CORE]     framework/ → core, ui, api, database, ai, observability, recording, security, etc.
[CONFIGURATION]      config/ → projects.yaml, environments.yaml, engine_decision_matrix.yaml, etc.
[UTILITY LAYER]      utils/ → logger.py, fake_data_generator.py
[TEST DATA LAYER]    test_data/ → bookslot (JSON/YAML datasets), callcenter, patientintake
[CI/CD LAYER]        .github/workflows/ → test, test_execution, lint, release, architecture-audit
```

### Architectural Patterns

| Pattern | Implementation | Purpose |
|---|---|---|
| **Factory** | `UIFactory`, `AIProviderFactory` | Creates engine/AI provider instances |
| **Strategy** | `EngineSelector`, `ExecutionFlow` | Selects optimal engine/validation strategy |
| **Abstract Base** | `BasePage` | Defines contract for all page objects |
| **Singleton** | `SettingsManager`, `AuditLogger` | Single source of configuration/audit |
| **Observer** | `APIInterceptor` | Monitors API requests/responses |
| **Fluent API** | `QueryBuilder`, `SmartActions` | Chainable method calls |
| **DI Container** | `di_container.py` | Singleton/transient/scoped lifetimes |

---

## 📁 Project Structure

```
Hybrid_Automation/
│
├── framework/                          # Core framework (40+ modules)
│   ├── core/                          # SmartActions, EngineSelectors, SessionManager
│   │   ├── smart_actions.py           # Human-like UI actions with audit logging
│   │   ├── async_smart_actions.py     # Async version (5-10x faster)
│   │   ├── engine_selector.py         # YAML rule-based engine selector (LRU cache)
│   │   ├── modern_engine_selector.py  # Python 3.12 match/case selector
│   │   ├── ai_engine_selector.py      # AI-powered selector (GPT-4/Azure/Ollama)
│   │   ├── exceptions.py             # 20+ custom exceptions with actionable hints
│   │   ├── session_manager.py         # Cross-engine session transfer (Sel↔PW)
│   │   ├── workflow_orchestrator.py   # Multi-step cross-engine workflows
│   │   └── utils/human_actions.py     # HumanBehaviorSimulator
│   ├── ui/                            # PlaywrightEngine, SeleniumEngine, BasePage, UIFactory
│   ├── api/                           # APIClient, AsyncAPIClient, GraphQL, WebSocket, Interceptor
│   ├── database/                      # DBClient, DBValidator, QueryBuilder, AsyncClient
│   ├── ai/                            # AIProviderFactory, NLTestGenerator
│   ├── observability/                 # EnterpriseLogger, SIEM adapters, OpenTelemetry
│   ├── recording/                     # RecordingWorkflow, Codegen, PageObjectGenerator
│   ├── security/                      # OWASP ZAP integration
│   ├── performance/                   # Web Vitals, Core metrics
│   ├── accessibility/                 # axe-core WCAG 2.1 testing
│   ├── cli/                           # Interactive CLI (`automation` command)
│   ├── models/                        # Pydantic V2 config/test models
│   ├── protocols/                     # Type protocol interfaces
│   ├── plugins/                       # Plugin architecture
│   ├── i18n/                          # Multi-language test support
│   ├── mobile/                        # Mobile device testing
│   ├── ml/                            # ML-based test optimization
│   ├── visual/                        # Visual regression testing
│   ├── microservices/                 # Microservice architecture support
│   └── di_container.py               # Dependency injection container
│
├── pages/                             # Page Object Model (POM) by project
│   ├── bookslot/                      # 7 page classes (P1-P7 booking flow)
│   ├── callcenter/                    # 2 page classes (management, dashboard)
│   └── patientintake/                 # 2 page classes (list, verification)
│
├── tests/                             # Test suites (~60 files)
│   ├── bookslot/                      # Page-level (P1-P7) + E2E tests
│   │   ├── pages/                     # 7 page test files (120+ tests)
│   │   ├── e2e/                       # End-to-end journey tests (12+ tests)
│   │   ├── helpers/                   # Data, navigation, validation helpers
│   │   └── conftest.py                # Navigation precondition fixtures (at_p1→at_p7)
│   ├── integration/                   # Cross-system 3-app workflow tests (20+ tests)
│   ├── unit/                          # Framework internal unit tests (~50 tests)
│   ├── modern/                        # Playwright tests for SPAs
│   ├── workflows/                     # Cross-engine E2E workflows
│   ├── examples/                      # Example test implementations
│   └── conftest.py                    # Session fixtures, engine factory
│
├── recorded_tests/                    # Recorded test suites by project
│   ├── bookslot/                      # Recorded workflows
│   ├── callcenter/                    # (placeholder)
│   └── patientintake/                 # (placeholder)
│
├── config/                            # All configuration files
│   ├── projects.yaml                  # 3 project definitions with URLs
│   ├── environments.yaml              # staging/production settings
│   ├── engine_decision_matrix.yaml    # 18 engine selection rules
│   ├── human_behavior.yaml            # Human simulation parameters
│   ├── url_testing.yaml               # URL testing service config
│   └── settings.py                    # SettingsManager singleton
│
├── test_data/                         # Test data by project
│   └── bookslot/                      # JSON + YAML patient datasets
│
├── utils/                             # Shared utilities
│   ├── logger.py                      # get_logger() + get_audit_logger()
│   └── fake_data_generator.py         # Faker-based test data generation
│
├── models/                            # Shared data models
│   └── appointment.py                 # Appointment + TestContext dataclasses
│
├── scripts/                           # 50+ automation scripts
│   ├── governance/                    # Architecture audit engine & tools
│   ├── validation/                    # Installation & behavior verification
│   ├── cli/                           # Legacy CLI launchers
│   ├── setup/                         # AI & dependency setup
│   └── utilities/                     # Misc utilities
│
├── .github/workflows/                 # 5 CI/CD pipelines
├── docker/                            # Docker configuration
├── ci/                                # CI support (allowlist, audit runner)
├── examples/                          # Example scripts & demos
├── Framework-Knowledge-Center/        # Complete documentation hub
├── docs/                              # Documentation (links to Knowledge Center)
│
├── conftest.py                        # Root pytest fixture hub
├── pytest.ini                         # 40+ markers, addopts, test paths
├── pyproject.toml                     # Build config (hatchling), tool settings
├── Makefile                           # 30+ automation targets
├── requirements.txt                   # ~80 core packages
├── requirements-dev.txt               # Dev-only extras
├── requirements_ai_optional.txt       # AI provider packages
├── .pre-commit-config.yaml            # Pre-commit hook chain
├── START_INTERACTIVE_MODE.bat         # Windows batch launcher
├── START_INTERACTIVE_MODE.ps1         # PowerShell launcher
└── README.md                          # This file
```

---

## ✨ Core Features

### 🎯 Hybrid Multi-Engine Architecture
- **Intelligent Engine Selection** — 3-tier selector: AI → YAML rules (18 priority-weighted) → Python 3.12 `match/case`
- **Priority-Based Decision Matrix** — YAML-configurable with confidence scoring (0-100%)
- **Modern & Legacy Support** — SPAs (React/Vue/Angular) + Legacy (JSP/ASP.NET/iframes)
- **Decision Caching** — LRU cache with TTL (100 entries, 3600s)
- **Cross-Engine Session Transfer** — Bidirectional Selenium ↔ Playwright session transfer (cookies, localStorage, tokens)

### 🏗️ Multi-Layer Testing
- **UI Testing** — Playwright (modern) + Selenium (legacy) with unified BasePage API
- **API Testing** — REST, GraphQL, WebSocket with request/response interception & mocking
- **Database Validation** — SQL Server, PostgreSQL, MySQL with read-only enforcement
- **Execution Flow** — UI → API → DB validation in single test with correlation IDs
- **Evidence Collection** — Screenshots, videos (auto-named `DDMMYYYY_HHMMSS.webm`), traces, logs

### 🤖 AI & Intelligence
- **Multi-Provider AI** — OpenAI GPT-4, Claude, Azure OpenAI, Ollama, LlamaCPP
- **AI Engine Selection** — 80% confidence threshold, exponential backoff retry, graceful degradation
- **Self-Healing Locators** — 6-strategy AI locator recovery with confidence scoring
- **Natural Language Test Generation** — Convert plain English to executable pytest code
- **ML Test Optimization** — Predictive test selection and smart retry logic
- **AI Script Refactoring** — Recorded tests auto-refactored into POM patterns

### 🎭 Human Behavior Simulation
- **Realistic Typing** — 80-250ms/char with 12% random thinking pauses, 5% error correction
- **Smart Mouse** — Bezier curves, ±5px offset variance, 25% hover probability
- **Natural Scrolling** — 100-350px increments, 30% correction probability
- **Anti-Detection** — Randomized viewport, navigator property injection, ±15% timing variance
- **Configurable Intensity** — `minimal` (fast) / `normal` (balanced) / `high` (very realistic)

### 🛡️ Quality & Security Testing
- **Visual Regression** — Pixel-perfect UI comparison with diff reports
- **Accessibility** — axe-core 4.8.3, WCAG 2.1 A/AA/AAA, keyboard nav, color contrast checks
- **Performance** — Core Web Vitals (LCP < 2500ms, FID < 100ms, CLS < 0.1), TTFB, resource breakdown
- **Security** — OWASP ZAP spider + active scan (SQL injection, XSS, CSRF), CWE-tagged HTML reports
- **Mobile** — Device emulation and responsive design validation

### 📊 Comprehensive Reporting
- **Allure Reports** — Interactive reports with history trends
- **HTML Reports** — pytest-HTML with embedded screenshots and videos
- **Structured Logging** — JSON audit logs (SOC2-ready, 1-year retention)
- **Video Recording** — Every test recorded, auto-named per convention

### 🏛️ Architecture Governance
- **4 Enforcement Layers** — Pre-commit hooks, file watcher, CI/CD (7 checks), manual audit
- **7 Audit Categories** — Engine mixing, POM compliance, test structure, markers, imports, naming, structural
- **Baseline Allow-List** — Time-boxed technical debt with mandatory expiration dates
- **Fix Suggestions** — Actionable remediation guidance for violations

---

## 🎯 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/sqamentor/Hybrid_Automation.git
cd Hybrid_Automation

# Install framework (editable mode)
pip install -e .

# Install Playwright browsers
playwright install chromium

# Verify installation
pytest --version
playwright --version
```

### Installation Options

```bash
# Standard
pip install -e .

# With AI features (set OPENAI_API_KEY / ANTHROPIC_API_KEY in .env)
pip install -e ".[ai]"

# With security testing (requires OWASP ZAP)
pip install -e ".[security]"

# Full installation (all features)
pip install -e ".[all]"

# Development setup
pip install -e ".[dev]"
pre-commit install
# OR: make install-dev
```

### 30-Second Example

```python
import pytest
from playwright.sync_api import Page

@pytest.mark.bookslot
def test_booking(page: Page, smart_actions, fake_bookslot_data):
    """Book appointment with auto-generated data and smart delays"""

    # Navigate (with automatic delay)
    smart_actions.navigate("https://bookslot.com", "Home Page")

    # Fill form (with human-like behavior)
    smart_actions.type_text(page.locator("#name"), fake_bookslot_data['first_name'])
    smart_actions.type_text(page.locator("#email"), fake_bookslot_data['email'])

    # Submit (with automatic post-click processing delay)
    smart_actions.button_click(page.locator("#submit"), "Submit Form")

    # Assert
    assert page.locator(".success-message").is_visible()
```

**No manual delays, no hardcoded data, human behavior included automatically.**

---

## 🔧 Configuration

### Multi-Project Environments

| Project | Staging URL | Production URL |
|---|---|---|
| bookslot | `bookslot-staging.centerforvein.com` | `bookslots.centerforvein.com` |
| callcenter | `staging-callcenter.centerforvein.com` | `callcenter.centerforvein.com` |
| patientintake | `staging-patientintake.centerforvein.com` | `patientintake.centerforvein.com` |

### Environment Selection

```bash
pytest -v                     # Staging (default)
pytest -v --env=production    # Production (read-only, smoke tests only)
```

### Browser Selection

```bash
pytest -v --test-browser=chromium   # Chromium (default)
pytest -v --test-browser=firefox    # Firefox
pytest -v --test-browser=webkit     # WebKit (Safari)
pytest -v --test-browser=chrome     # Chrome
pytest -v --test-browser=msedge     # Edge
```

### Human Behavior Configuration

```bash
pytest -v --enable-human-behavior                          # Enable
pytest -v --disable-human-behavior                         # Disable (fast)
pytest -v --enable-human-behavior --human-behavior-intensity=high  # High realism
```

### Execution Mode

```bash
pytest -v --execution-mode=ui_only     # UI only
pytest -v --execution-mode=ui_api      # UI + API validation
pytest -v --execution-mode=ui_api_db   # UI + API + DB (full)
```

### Engine Decision Matrix (Top Rules)

| Priority | Rule | Engine | Confidence |
|---|---|---|---|
| 100 | Legacy Browser Support | Selenium | 100% |
| 98 | Enterprise Authentication (SSO/MFA) | Selenium | 95% |
| 95 | Deep Iframe Structures (3+) | Selenium | 92% |
| 92 | Modern SPA + API Testing | Playwright | 95% |
| 87 | Mobile Responsive | Playwright | 90% |
| 85 | Modern Dashboards | Playwright | 88% |
| 10 | Default fallback | Playwright | — |

Full 18-rule matrix in [`config/engine_decision_matrix.yaml`](config/engine_decision_matrix.yaml).

### Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `TEST_ENV` | No | Logger verbosity (dev→DEBUG, staging→INFO, prod→WARNING) |
| `SSO_PASSWORD` | Staging | SSO authentication password |
| `OPENAI_API_KEY` | Optional | AI engine selector (GPT-4) |
| `AZURE_OPENAI_API_KEY` | Optional | Azure OpenAI provider |
| `DB_STAGING_USERNAME` | Optional | Database credentials (CI/CD) |
| `DB_STAGING_PASSWORD` | Optional | Database credentials (CI/CD) |
| `LLAMACPP_MODEL_PATH` | Optional | Local GGUF model file path |
| `OLLAMA_BASE_URL` | Optional | Custom Ollama server (default: localhost:11434) |

See [`env.example`](env.example) for the complete template.

---

## 💻 CLI Reference

### Interactive Mode (Recommended)

```bash
automation
```

Step-by-step guided experience:
1. 🎨 Welcome screen → 2. 📋 Select project → 3. 📦 Choose test suite → 4. 📄 Pick test → 5. 🌍 Select environment → 6. ✅ Confirm → 7. 🚀 Execute

**Windows Launchers:** `START_INTERACTIVE_MODE.bat` or `START_INTERACTIVE_MODE.ps1`

### CLI Subcommands

```bash
automation test bookslot --env staging       # Project-aware test execution
automation run-pom --project bookslot        # POM test runner
automation record --project bookslot         # Record new tests
automation projects                          # List projects
automation context                           # Show workspace context
```

### CLI Options Reference

| Option | Choices | Default |
|---|---|---|
| `--project` | bookslot, callcenter, patientintake | bookslot |
| `--env` | staging, production, prod | staging |
| `--test-browser` | chromium, chrome, firefox, webkit, safari, msedge | chromium |
| `--headless` | flag | False (headed) |
| `--execution-mode` | ui_only, ui_api, ui_api_db | None |
| `--enable-human-behavior` | flag | False |
| `--human-behavior-intensity` | minimal, normal, high | normal |

Full CLI Reference: [Interactive CLI Guide](Framework-Knowledge-Center/06-CLI-And-Tooling/Interactive-CLI-Guide.md)

---

## 📊 Running Tests

### Using Make (Recommended)

```bash
make test                  # Run all tests
make test-fast             # Without human behavior (faster)
make test-parallel         # Parallel execution
make test-bookslot         # Specific project
make test-coverage         # With coverage report
make test-headed           # Visible browser
make test-allure           # Generate Allure report
```

### Using Pytest Directly

```bash
# By marker
pytest -m bookslot -v
pytest -m smoke -v
pytest -m regression -v
pytest -m "e2e and bookslot" -v

# Specific file/function
pytest tests/bookslot/pages/test_p1_basic_info.py -v
pytest tests/bookslot/e2e/test_complete_journeys.py::test_complete_booking_happy_path_am_slot -v

# Parallel execution
pytest -n 4 -v

# With reports
pytest -v --html=reports/report.html --self-contained-html
pytest -v --alluredir=allure-results && allure serve allure-results
```

### Pytest Markers Inventory

| Category | Markers |
|---|---|
| **Project** | `bookslot`, `callcenter`, `patientintake` |
| **Engine** | `playwright`, `selenium`, `modern_spa`, `legacy_ui`, `mobile`, `pooling`, `grid` |
| **Test Type** | `smoke`, `regression`, `e2e`, `unit`, `integration`, `recorded`, `workflow` |
| **Human Behavior** | `human_behavior`, `human_like`, `no_human_behavior` |
| **Priority** | `critical`, `high`, `medium`, `low` |
| **Page-specific** | `p1_basic_info` through `p7_success` |
| **Environment** | `dev_only`, `staging_only`, `prod_safe` |
| **Special** | `slow`, `skip_ci`, `flaky`, `wip` |
| **Advanced** | `ai_enhanced`, `enhanced_features`, `multi_project` |

---

## 📄 Page Object Model

### BookSlot 7-Step Flow (P1 → P7)

| Page | Class | URL Path | Purpose | Key Methods |
|---|---|---|---|---|
| P1 | `BookslotBasicInfoPage` | `/basic-info` | Patient contact info | `fill_first_name`, `fill_email`, `fill_phone`, `fill_zip`, `submit_for_otp`, `verify_otp` |
| P2 | `BookslotEventInfoPage` | `/eventtype` | Appointment type selection | `select_new_patient_type`, `select_complimentary_consultation`, `request_callback` |
| P3 | `BookslotWebSchedulerPage` | `/scheduler` | Date/time slot selection | `select_first_available_slot`, `select_am_slot`, `select_pm_slot`, `confirm_slot` |
| P4 | `BookslotPersonalInfoPage` | `/personal-info` | Patient demographics | `select_gender_male`, `fill_dob`, `fill_address_with_autocomplete` |
| P5 | `BookslotReferralPage` | `/referral` | Marketing attribution | `select_physician`, `select_online`, `select_social_media` |
| P6 | `BookslotInsurancePage` | `/insurance` | Insurance collection | `fill_member_name`, `fill_id_number`, `fill_group_number`, `fill_insurance_company` |
| P7 | `BookslotSuccessPage` | `/success` | Confirmation page | `is_page_loaded`, `click_redirect_message` |

### CallCenter & PatientIntake

| Module | Class | Purpose |
|---|---|---|
| CallCenter | `CallCenterAppointmentManagementPage` | Search, cancel, verify appointments |
| CallCenter | `CallCenterDashboardVerificationPage` | Cross-engine auth verification |
| PatientIntake | `PatientIntakeAppointmentListPage` | Patient appointment list & search |
| PatientIntake | `PatientIntakeVerificationPage` | Cross-engine auth verification |

### POM Common Patterns

- All inherit from `BasePage` with `@log_function` decorator
- Sensitive methods marked `mask_sensitive=True` (PII protection)
- Methods return `self` for fluent API chaining
- Playwright role-based selectors (`get_by_role`, `get_by_text`)
- Cross-project data sharing via `Appointment` model

---

## 🧪 Test Suite Architecture

### Test Pyramid

| Layer | Files | Tests | Focus |
|---|---|---|---|
| Unit Tests | 11 | ~50 | Framework internals (DI, models, selectors) |
| Page Tests (L1) | 7 | 120+ | Individual page components (P1-P7) |
| E2E Tests (L2) | 2 | 12+ | Full 7-step booking flows |
| Integration (L3) | 9 | 20+ | Cross-system 3-app workflows |
| Recorded Tests | 3 | varies | Raw recorded + refactored flows |

### Conftest Hierarchy

```
conftest.py (root)              → video, smart_actions, fake_data, project, env
 └── tests/conftest.py          → engine factory, API/DB clients, AI validator
      └── tests/bookslot/conftest.py → navigation fixtures (at_p1 → at_p7)
```

### Critical Test Scenarios

- **Smoke:** Page load tests for P1-P7 + `test_all_systems_accessible`
- **E2E Happy Path:** `test_complete_booking_happy_path_am_slot`, `_pm_slot`
- **Cross-System:** `test_book_and_verify_in_all_systems` (3-app simultaneous)
- **Negative:** Email/phone/zip validation, required field errors (parametrized)
- **Parametrized:** 4 insurance payers, 6 event types, 6 referral sources, AM/PM time preferences

---

## 📡 Observability & Logging

### Dual-Track Logging Pipeline

**Standard Track:**
```
utils/logger.py → get_logger(__name__)   → logs/framework_YYYYMMDD.log
                → get_audit_logger()     → logs/audit/audit_YYYYMMDD.log (JSON)
```

**Enterprise Track:**
```
framework/observability/enterprise_logger.py → EnterpriseLogger (async QueueHandler)
  → logs/enterprise/app_YYYYMMDD.json          (Full structured JSON, 30 backups)
  → logs/audit/audit_YYYYMMDD.json             (SOC2, 365 backups = 1-year retention)
  → logs/security/security_YYYYMMDD.json       (Auth events, 180 backups = 6 months)
  → logs/performance/performance_YYYYMMDD.json (Timing metrics, 30 backups)
```

### Per-Test Correlation IDs

Every test gets **3 UUIDs** (generated in `pytest_runtest_setup()`):
- `correlation_id` — Links all actions in a single test
- `request_id` — HTTP request-level tracing
- `trace_id` — OpenTelemetry-compatible distributed tracing

### PII Masking

- **Key-based:** password, token, api_key, secret, credit_card, ssn, jwt, bearer
- **Pattern-based:** Email (`j***@c*****.com`), Credit Card (`****-****-****-****`), SSN (`***-**-****`), Phone (`(***) ***-****`)

### SIEM Integration

Supported providers: **ELK/Elasticsearch**, **Datadog**, **Splunk HEC**, **Grafana Loki**, **AWS CloudWatch**, **Azure Monitor** — with async batching, circuit breaker (5 failures/60s recovery), auto-flush.

### OpenTelemetry

Sync/async/decorator-based spans, Console + OTLP exporters, auto-attributes (`service.name`, `service.environment`, `service.version`).

---

## 🔄 CI/CD Pipeline

### 5 GitHub Actions Workflows

| Workflow | Trigger | Purpose |
|---|---|---|
| [`test.yml`](.github/workflows/test.yml) | Push/PR | Multi-OS matrix (Ubuntu/Windows/macOS × Python 3.12/3.13), unit + integration, coverage → Codecov |
| [`test_execution.yml`](.github/workflows/test_execution.yml) | Push to main/develop, PR, daily cron 02:00 UTC | Smoke → Regression → Integration → Docker → Allure → PR comment |
| [`lint.yml`](.github/workflows/lint.yml) | Push/PR | Black, isort, flake8, mypy, bandit, safety, radon, pylint, pre-commit |
| [`release.yml`](.github/workflows/release.yml) | Release tags | Automated release packaging |
| [`architecture-audit.yml`](.github/workflows/architecture-audit.yml) | PR | Architecture compliance via `framework_audit_engine.py` |

### CI Artifacts

- HTML reports, Allure results, screenshots (uploaded on failure)
- Security reports (bandit JSON), code quality reports (radon, pylint)
- Test execution: Chromium, Firefox, WebKit browsers installed via Playwright

---

## 🏛️ Architecture Governance

### 4 Enforcement Layers

| Layer | Enforcement Point | Description |
|---|---|---|
| **Pre-Commit Hooks** | Local development | Blocks commits violating architecture rules |
| **File Watcher** | Real-time | Auto-audit on code changes (`--watch --strict`) |
| **CI/CD** | Pull Requests | 7 independent status checks, blocks merge on violations |
| **Manual Audit** | On demand | `pytest --arch-audit [--audit-category=pom-compliance] [--audit-strict]` |

### 7 Audit Categories

1. **Engine Mixing** — Prevents Playwright + Selenium in same test
2. **POM Compliance** — Enforces Page Object Model patterns
3. **Test Structure** — Validates test organization and boundaries
4. **Marker Consistency** — Ensures correct test markers
5. **Import Validation** — Prevents forbidden imports in page objects
6. **Naming Conventions** — Enforces consistent naming patterns
7. **Structural Violations** — Detects architectural anti-patterns

### Baseline Allow-List

```yaml
# ci/baseline_allowlist.yaml
violations:
  - file: tests/legacy/test_old_system.py
    rule: engine/missing-marker
    reason: Legacy test suite pending migration
    owner: qa-team
    created: 2026-01-15
    expires: 2026-03-31  # MANDATORY — expired entries FAIL the build
```

---

## 📦 Technology Stack

| Category | Key Packages | Version |
|---|---|---|
| **Testing** | pytest, pytest-playwright, pytest-xdist, pytest-html, pytest-bdd, pytest-timeout, pytest-cov, pytest-asyncio, pytest-benchmark | ≥7.4.0+ |
| **Browser** | playwright, selenium, webdriver-manager | ≥1.40.0, ≥4.15.0 |
| **HTTP/API** | requests, httpx, schemathesis | ≥2.31.0, ≥0.27.0 |
| **Database** | pyodbc (SQL Server), psycopg2-binary (PostgreSQL), pymysql, asyncpg, aiomysql | ≥5.0.1 |
| **Config** | PyYAML, pydantic (V2), pydantic-settings, python-dotenv | ≥6.0.1, ≥2.5.0 |
| **Reporting** | allure-pytest, loguru, structlog | ≥2.13.2, ≥0.7.2 |
| **AI** | openai, anthropic | ≥1.6.0, ≥0.18.0 |
| **Data** | Faker, mimesis | ≥21.0.0 |
| **Visual** | Pillow, imagehash | ≥10.1.0 |
| **Observability** | opentelemetry-api, opentelemetry-sdk | ≥1.21.0 |
| **Utilities** | tenacity, rich, questionary, nest-asyncio | ≥8.2.3 |
| **Build** | hatchling | ≥1.21.0 |
| **Code Quality** | black (line-length=100), ruff, mypy, bandit, isort | Python 3.12 target |

---

## 📚 Documentation Hub

All documentation is maintained in the **[Framework-Knowledge-Center](Framework-Knowledge-Center/INDEX.md)** — single canonical file per topic, zero duplication.

| # | Section | Files | Topics |
|---|---|---|---|
| 02 | [Core Concepts](Framework-Knowledge-Center/02-Core-Concepts/) | 2 | Engine selection system, Smart Actions API |
| 03 | [Page Object Model](Framework-Knowledge-Center/03-Page-Object-Model/) | 1 | POM architecture, locator strategies, BasePage contract |
| 04 | [Test Data Management](Framework-Knowledge-Center/04-Test-Data-Management/) | 2 | URL testing design, query string patterns |
| 05 | [Observability & Logging](Framework-Knowledge-Center/05-Observability-And-Logging/) | 3 | Enterprise logging architecture, implementation, deployment |
| 06 | [CLI & Tooling](Framework-Knowledge-Center/06-CLI-And-Tooling/) | 2 | Interactive CLI guide, directory structure |
| 07 | [Governance](Framework-Knowledge-Center/07-Governance/) | 4 | Governance system, audit report, pending fixes, config fixes |
| 08 | [Media Capture](Framework-Knowledge-Center/08-Media-Capture/) | 1 | Screenshots, video naming, HTML report capture |
| 09 | [Rules & Standards](Framework-Knowledge-Center/09-Rules-And-Standards/) | 2 | Strict rules (10 categories), anti-patterns (8 categories) |

---

## 🔑 Key Principles & Rules

### Mandatory Rules

#### 1. Page Object Model (POM)
✅ Separate page classes per page, locators as `@property`, return `self` for chaining
❌ No direct `page.locator()` in tests, no assertions in page objects, no hardcoded test data

#### 2. Engine Mixing
✅ ONE engine per test, correct markers (`@pytest.mark.playwright` / `@pytest.mark.selenium`)
❌ Never mix Playwright + Selenium imports in same test

#### 3. Test Structure
✅ AAA pattern (Arrange, Act, Assert), descriptive names, appropriate markers
❌ No god tests, no duplicated data generation

#### 4. Human Behavior
✅ Use `smart_actions` fixture for automatic delays, configure via YAML/CLI
❌ No manual `time.sleep()`, no hardcoded delays

#### 5. Data Management
✅ Use `fake_bookslot_data` fixture, load from `test_data/`
❌ No hardcoded test data, no production data

### Common Anti-Patterns

```python
# ❌ BAD: Direct locator in test          # ✅ GOOD: POM pattern
page.locator("#email").fill("test@x.com")  login_page.fill_email("test@x.com")

# ❌ BAD: Manual delay                    # ✅ GOOD: Smart Actions
page.click("#submit"); time.sleep(2)       smart_actions.button_click(locator, "Submit")

# ❌ BAD: Hardcoded data                  # ✅ GOOD: Faker fixture
page.fill("#name", "John Doe")             page.fill("#name", fake_bookslot_data['first_name'])
```

Full rules: [Strict Rules](Framework-Knowledge-Center/09-Rules-And-Standards/Strict-Rules.md) | [Anti-Patterns](Framework-Knowledge-Center/09-Rules-And-Standards/Anti-Patterns.md)

---

## ⚠️ Known Gaps & Recommendations

### Critical Issues (from Feb 2026 Audit)

| ID | Issue | Impact |
|---|---|---|
| C-1 | CallCenter & PatientIntake tests are `assert True` placeholders only | Zero automated coverage for 2 of 3 apps |
| C-2 | 9+ `.bak` files committed to git | Pollutes codebase, confuses test discovery |
| C-3 | Hardcoded phone (`1234567890`) and OTP (`123456`) in fake data | Tests may fail if app validates uniqueness |
| C-4 | Empty `test_data/callcenter/` and `test_data/patientintake/` | Integration tests rely solely on bookslot data |

### Test Coverage Status

| Application | Coverage |
|---|---|
| BookSlot P1-P7 | **HIGH** — smoke + validation + regression + URL tests |
| BookSlot E2E | **MEDIUM** — 12 scenarios, missing error recovery |
| CallCenter | **LOW** — Placeholder only (page objects ready) |
| PatientIntake | **LOW** — Placeholder only (page objects ready) |
| Cross-System | **MEDIUM** — 3-app workflow exists, missing negative scenarios |
| Performance / Accessibility / Security / Visual | **LOW** — Modules built, no tests integrated |

For full issue list (4 Critical, 5 High, 7 Medium, 7 Low = **23 total issues**), see [PRD.txt](PRD.txt) Section 18.

---

## 🤝 Contributing

### Development Workflow

```bash
# 1. Fork and clone
git clone https://github.com/your-username/Hybrid_Automation.git && cd Hybrid_Automation

# 2. Create branch
git checkout -b feature/your-feature-name

# 3. Install dev dependencies
make install-dev

# 4. Make changes (write code, add tests, update docs)

# 5. Run architecture audit
pytest --arch-audit

# 6. Commit (pre-commit hook runs audit automatically)
git add . && git commit -m "feat: your feature description"

# 7. Push and create PR (CI runs full audit)
git push origin feature/your-feature-name
```

### Code Standards

- **Python 3.12+** required
- **Black** — line-length=100, target py312
- **Ruff** — select E/W/F/I/B/C4/UP/ARG/SIM
- **Mypy** — `check_untyped_defs=true`
- **Bandit** — Security scanning (excludes tests)
- **Docstrings** for all public methods

---

## 🌟 Roadmap

### Current (v1.0.0)
- ✅ Dual-engine Playwright/Selenium with intelligent selection
- ✅ SmartActions with human behavior simulation
- ✅ Multi-layer testing (UI/API/DB)
- ✅ SOC2-ready audit logging with PII masking
- ✅ Architecture governance (4 enforcement layers)
- ✅ 5 CI/CD pipelines
- ✅ BookSlot full 7-page POM + E2E coverage

### Planned (v1.1.0)
- 🔄 CallCenter & PatientIntake real test suites
- 🔄 Automated SSO login flow
- 🔄 Visual AI for element detection
- 🔄 Cloud test execution (BrowserStack/Sauce Labs)
- 🔄 Test data management portal

### Future (v2.0.0)
- 🔮 Autonomous test generation
- 🔮 Self-optimizing test suites
- 🔮 Predictive failure analysis
- 🔮 Cross-browser visual regression
- 🔮 Mobile app testing (Appium integration)

---

## 📞 Support & Contact

- **Author:** Lokendra Singh
- **Email:** lokendra.singh@centerforvein.com
- **Website:** [www.centerforvein.com](https://www.centerforvein.com)
- **GitHub:** [@sqamentor](https://github.com/sqamentor)

### Getting Help

1. **Documentation** — Check [Framework-Knowledge-Center](Framework-Knowledge-Center/INDEX.md)
2. **Issues** — Open a [GitHub Issue](https://github.com/sqamentor/Hybrid_Automation/issues)
3. **Discussions** — Use [GitHub Discussions](https://github.com/sqamentor/Hybrid_Automation/discussions)
4. **Email** — For private inquiries

---

## 📄 License

MIT License — See [LICENSE](LICENSE) file for details.

---

**Built with ❤️ by the SQA Mentor Team**

**"Intelligent Testing for Modern Healthcare Applications"**
