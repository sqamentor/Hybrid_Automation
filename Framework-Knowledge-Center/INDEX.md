# Framework Knowledge Center — Index

**Enterprise Hybrid Automation Framework Documentation**

This Knowledge Center is the single source of truth for all framework documentation.
Structure is deduplicated, semantically organized, and maintained as canonical single-file-per-topic.

**Last Updated:** 2026-02-26
**Framework Version:** 1.0.0

---

## Quick Navigation

| # | Section | Files | Purpose |
|---|---------|-------|---------|
| 02 | [Core Concepts](#️-core-concepts) | 2 | Engine selection, Smart Actions |
| 03 | [Page Object Model](#-page-object-model) | 1 | POM architecture and rules |
| 04 | [Test Data Management](#-test-data-management) | 2 | URL testing, query strings |
| 05 | [Observability & Logging](#-observability--logging) | 3 | Enterprise logging system |
| 06 | [CLI & Tooling](#️-cli--tooling) | 2 | CLI guide, directory structure |
| 07 | [Governance](#️-governance) | 4 | Architecture audit, config fixes |
| 08 | [Media Capture](#-media-capture) | 1 | Screenshots, video, reports |
| 09 | [Rules & Standards](#-rules--standards) | 2 | Mandatory rules, anti-patterns |

---

## Core Concepts

### `02-Core-Concepts/`

- **[Engine-Selection-System.md](02-Core-Concepts/Engine-Selection-System.md)**
  - Playwright vs Selenium decision logic
  - 20+ decision rules with priority scoring
  - YAML configuration (`config/engine_decision_matrix.yaml`)
  - Custom overrides and decision caching

- **[Smart-Actions.md](02-Core-Concepts/Smart-Actions.md)**
  - Context-aware UI action wrappers
  - Automatic delays and human behavior integration
  - API reference for all SmartActions methods
  - Audit logging integration

---

## Page Object Model

### `03-Page-Object-Model/`

- **[POM-Architecture.md](03-Page-Object-Model/POM-Architecture.md)**
  - POM principles and class structure
  - Locator strategies using `@property`
  - Method organization and `return self` chaining
  - BasePage contract

---

## Test Data Management

### `04-Test-Data-Management/`

- **[URL_QUERY_STRING_TESTING_DESIGN.md](04-Test-Data-Management/URL_QUERY_STRING_TESTING_DESIGN.md)**
  - Design for URL and query string test coverage
  - Parametrized test patterns

- **[URL_TESTING_QUICK_REFERENCE.md](04-Test-Data-Management/URL_TESTING_QUICK_REFERENCE.md)**
  - Quick reference card for URL testing
  - Common patterns and examples

---

## Observability & Logging

### `05-Observability-And-Logging/`

Three canonical files covering the complete enterprise logging system:

- **[Enterprise-Logging-Architecture.md](05-Observability-And-Logging/Enterprise-Logging-Architecture.md)**
  - System architecture and design philosophy
  - Core components: `EnterpriseLogger`, `AuditLogger`, `CorrelationContext`
  - Dual-track pipeline (standard + enterprise JSON)
  - 25+ structured JSON fields, distributed tracing
  - SIEM integration: ELK, Datadog, Splunk, Grafana Loki
  - SOC2/ISO27001/GDPR/HIPAA compliance features
  - PII masking (email, password, SSN, credit card)
  - Log schema reference

- **[Enterprise-Logging-Implementation.md](05-Observability-And-Logging/Enterprise-Logging-Implementation.md)**
  - Step-by-step integration for every code layer
  - SmartActions, BasePage, SeleniumEngine, APIClient, test files
  - 8 canonical code integration patterns
  - Critical fixes applied (6 bugs resolved)
  - Validation checklist

- **[Enterprise-Logging-Deployment.md](05-Observability-And-Logging/Enterprise-Logging-Deployment.md)**
  - 100% production readiness (18/18 issues resolved)
  - 7-phase deployment plan with bash commands
  - Environment-specific configuration
  - Performance characteristics and monitoring
  - Troubleshooting guide and final deployment checklist

**Log files produced at runtime:**

| Path | Content |
|------|---------|
| `logs/framework_YYYYMMDD.log` | Human-readable; all `logger.*` calls |
| `logs/errors_YYYYMMDD.log` | ERROR+ only |
| `logs/audit/audit_YYYYMMDD.log` | Structured JSON; every SmartAction |
| `logs/enterprise/app_YYYYMMDD.json` | Full structured JSON via EnterpriseLogger |
| `logs/security/security_YYYYMMDD.json` | Auth/authz events |
| `logs/performance/performance_YYYYMMDD.json` | Timing metrics |

---

## CLI & Tooling

### `06-CLI-And-Tooling/`

- **[Interactive-CLI-Guide.md](06-CLI-And-Tooling/Interactive-CLI-Guide.md)**
  - Complete reference for the `automation` unified CLI
  - Interactive mode step-by-step walkthrough
  - All subcommands: `run`, `run-pom`, `test`, `record`, `projects`, `context`
  - Multi-project support (bookslot, callcenter, patientintake)
  - Root execution and workspace context detection
  - CI/CD integration examples
  - CLI architecture (`framework/cli/` layout, router logic)
  - Industry standards alignment (Nx, Turborepo, Playwright)
  - Troubleshooting guide

- **[Directory-Structure.md](06-CLI-And-Tooling/Directory-Structure.md)**
  - Complete project directory layout
  - Every major directory explained with purpose and standards
  - Migration map (old to new locations)
  - Maintenance guidelines for adding projects and scripts

---

## Governance

### `07-Governance/`

- **[Governance-System-Overview.md](07-Governance/Governance-System-Overview.md)**
  - Architecture governance system design
  - 4 enforcement layers: pre-commit, file watcher, CI/CD, manual audit
  - Audit workflow and violation lifecycle

- **[Framework-Architecture-Audit-Report.md](07-Governance/Framework-Architecture-Audit-Report.md)**
  - Complete framework audit results
  - Architecture analysis and code quality metrics
  - Compliance assessment, recommendations, action items

- **[Pending-Implementations-And-Fixes.md](07-Governance/Pending-Implementations-And-Fixes.md)**
  - Outstanding technical debt and known issues
  - Planned enhancements with priority tracking
  - Implementation roadmap

- **[Configuration-Fixes-Reference.md](07-Governance/Configuration-Fixes-Reference.md)**
  - 3 pytest configuration fixes (all verified)
  - Fix 1: Marker expression syntax error (`-m` quotes removed)
  - Fix 2: `asyncio_mode` config warning resolved
  - Fix 3: `human_behavior` marker registration added
  - Before/after command examples and verification commands

---

## Media Capture

### `08-Media-Capture/`

- **[Media-Capture-System.md](08-Media-Capture/Media-Capture-System.md)**
  - Complete screenshot, video, and HTML report capture system
  - Naming convention: `project_Env_DDMMYYYY_HHMMSS.{webm|html}`
  - Auto-increment collision handling
  - Video recording setup (Playwright context fixtures)
  - `generate_unique_video_filename()` function reference
  - Dynamic HTML report naming (`pytest_configure` hook)
  - pytest hook for auto-rename on all `page`-fixture tests
  - Allure report integration
  - Troubleshooting guide

---

## Rules & Standards

### `09-Rules-And-Standards/`

- **[Strict-Rules.md](09-Rules-And-Standards/Strict-Rules.md)**
  - **MANDATORY** — violations block git commits and CI/CD builds
  - 10 rule categories: POM, Engine Mixing, Test Structure, Human Behavior, Data, Imports, Naming, Markers, Execution Flow, Configuration
  - Every rule includes correct example, wrong example, and enforcement metadata
  - Critical violations table showing commit/merge blocking status
  - Baseline allow-list format for legitimate technical debt

- **[Anti-Patterns.md](09-Rules-And-Standards/Anti-Patterns.md)**
  - **FORBIDDEN** patterns that cause test failures and architecture violations
  - 8 categories: Page Object, Test Structure, Delay/Timing, Data Management, Engine Selection, Configuration, Error Handling, Performance
  - Every anti-pattern has bad code, explanation, and correct alternative
  - Quick-fix reference table

---

## Contact & Support

- **Email:** lokendra.singh@centerforvein.com
- **Website:** www.centerforvein.com
- **GitHub:** sqamentor/Hybrid_Automation

---

*All documentation is maintained as single canonical files per topic — zero duplication.*
