# 🚀 Enterprise Hybrid Automation Framework

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-1.40+-green.svg)](https://playwright.dev/)
[![Selenium](https://img.shields.io/badge/selenium-4.x-yellow.svg)](https://www.selenium.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Architectural Compliance](https://img.shields.io/badge/compliance-100%25-brightgreen.svg)](#architectural-compliance)

**Next-generation, AI-powered, hybrid automation framework achieving 100% architectural compliance.**

> **Built for the next 30 years** - Modern architecture, strict governance, zero-tolerance enforcement.

---

## ✨ What's New - January 2026

### 🎯 **100% Architectural Compliance Achieved**
- ✅ **Engine Isolation**: 100% (0 direct imports in 39 test files)
- ✅ **Engine Selection**: 100% (304/304 classes with markers)
- ✅ **Engine Abstraction**: 100% (duck typing throughout)
- ✅ **Layer Boundaries**: 100% (0 assertions in Page Objects)
- ✅ **POM Compliance**: Verified with enforcement tools

### 🛡️ **Governance & Enforcement**
- ✅ **3 Enforcement Tools**: Markers, Abstraction, POM validation
- ✅ **CI/CD Ready**: Exit codes for automated checks
- ✅ **Pre-commit Hooks**: Optional strict validation
- ✅ **Zero Tolerance**: No architectural violations

### 📁 **Organized Structure**
- ✅ **Framework-Knowledge-Center**: All docs organized by category
- ✅ **Scripts Directory**: Enforcement, validation, CLI separated
- ✅ **Clean Root**: Essential files only

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                pytest (Orchestrator)                     │
├──────────────────┬──────────────────────────────────────┤
│  modern_spa      │  legacy_ui                           │
│       ↓          │       ↓                              │
│  Playwright      │  Selenium                            │
├──────────────────┴──────────────────────────────────────┤
│           ui_engine Fixture (Abstraction)               │
├─────────────────────────────────────────────────────────┤
│              Page Object Model (POM)                    │
│         Tests = INTENT │ Pages = CAPABILITY             │
└─────────────────────────────────────────────────────────┘
```

**Core Principles:**
1. **Engine Isolation** - No direct engine imports
2. **Engine Selection** - Markers control routing
3. **Abstraction** - Duck typing throughout
4. **POM Boundaries** - Pages return data, tests assert
5. **Session Transfer** - SSO → Playwright workflows

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/sqamentor/Hybrid_Automation.git
cd Hybrid_Automation
pip install -e .
playwright install chromium
python scripts/validation/verify_installation.py
```

### Run Tests

```bash
# Interactive CLI
python scripts/cli/run_tests_cli.py

# With markers
pytest -m modern_spa -v
pytest tests/bookslot/ -v

# With enforcement
python scripts/enforcement/enforce_markers.py && pytest tests/
```

---

## ✨ Features

### 🎯 **Hybrid UI Automation**
- **Playwright** - Modern SPAs (React, Vue, Angular)
- **Selenium** - Legacy UI, iframes, SSO
- **Auto-routing** - Marker-based engine selection
- **Session Transfer** - Seamless Selenium → Playwright

### 🧪 **Multi-Layer Testing**
- **UI + API + DB** - Validate all layers in one test
- **Cross-Engine** - SSO (Selenium) → Apps (Playwright)
- **Workflow Orchestrator** - Multi-step scenarios

### 🤖 **AI-Powered**
- **GPT-4 & Claude** - Test generation, validation
- **Self-Healing** - Auto element recovery
- **Smart Validation** - AI-suggested checks

### 👤 **Human Behavior**
- Realistic mouse movements
- Variable typing delays
- Natural think time

### 📊 **Enterprise Reporting**
- Allure reports
- HTML reports with screenshots/videos
- Structured logging

---

## 📁 Project Structure

```
Hybrid_Automation/
├── 📄 README.md                    # This file
├── 📄 conftest.py                  # pytest config
├── 📄 pytest.ini, pyproject.toml   # Settings
│
├── 📂 config/                      # Configurations
├── 📂 framework/                   # Core framework
├── 📂 pages/                       # Page Objects
├── 📂 tests/                       # Test files
│
├── 📂 scripts/                     # Organized scripts
│   ├── enforcement/               # Compliance tools
│   ├── validation/                # Validation scripts
│   ├── cli/                       # CLI tools
│   ├── utilities/                 # Utilities
│   └── quick-start/               # Quick start
│
└── 📂 Framework-Knowledge-Center/  # Documentation
    ├── 00-Quick-Reference/
    ├── 01-Getting-Started/
    ├── 02-Architecture/
    ├── 03-Features/
    ├── 04-Advanced-Topics/
    ├── 05-Examples/
    ├── 06-Project-Status/
    ├── 07-Documentation-Meta/
    └── 08-Audit-Reports/
```

---

## 🎯 Writing Tests

### Basic Test

```python
import pytest
from pages.bookslot.bookslots_basicinfo_page1 import BookslotBasicInfoPage

@pytest.mark.modern_spa  # Required: Engine marker
@pytest.mark.bookslot
class TestBooking:
    def test_fill_form(self, ui_engine, fake_bookslot_data):
        page = BookslotBasicInfoPage(ui_engine, url)
        page.fill_first_name(fake_bookslot_data['first_name'])
        page.click_next()
```

### Legacy UI Test

```python
@pytest.mark.legacy_ui  # Selenium for SSO
@pytest.mark.auth_type("SSO")
class TestAdmin:
    def test_sso_login(self, ui_engine):
        ui_engine.navigate("https://admin.example.com")
```

### Cross-Engine Workflow

```python
@pytest.mark.workflow
def test_sso_to_app(workflow_orchestrator):
    # Step 1: SSO via Selenium
    workflow_orchestrator.add_step(
        name="SSO Login",
        engine_type=EngineType.SELENIUM,
        action=sso_action
    )
    # Step 2: App via Playwright (session transferred)
    workflow_orchestrator.add_step(
        name="App Operations",
        engine_type=EngineType.PLAYWRIGHT,
        action=app_action,
        requires_session=True
    )
    workflow_orchestrator.execute()
```

---

## 🛡️ Enforcement & Compliance

### Run Checks

```bash
python scripts/enforcement/enforce_markers.py
python scripts/enforcement/enforce_abstraction.py
python scripts/enforcement/enforce_pom.py
```

### CI/CD Integration

```yaml
- name: Compliance
  run: |
    python scripts/enforcement/enforce_markers.py || exit 1
    python scripts/enforcement/enforce_abstraction.py || exit 1
- name: Tests
  run: pytest tests/ -v
```

### Metrics

| Metric | Status |
|--------|--------|
| Engine Isolation | ✅ 100% |
| Engine Selection | ✅ 100% |
| Engine Abstraction | ✅ 100% |
| Layer Boundaries | ✅ 100% |

---

## 🏆 Best Practices

### 1. Engine Markers (Required)

```python
# ✅ CORRECT
@pytest.mark.modern_spa
class TestBooking: pass

# ❌ WRONG - No marker
class TestBooking: pass
```

### 2. Use ui_engine Fixture

```python
# ✅ CORRECT
def test(ui_engine):
    ui_engine.navigate("...")

# ❌ WRONG - Direct import
from playwright.sync_api import Page
def test(page: Page): pass
```

### 3. Page Objects Return Data

```python
# ✅ CORRECT - Page Object
def get_status(self) -> str:
    return self.page.locator("status").text()

# ✅ CORRECT - Test
def test_status(page_obj):
    assert page_obj.get_status() == "Active"

# ❌ WRONG - Assert in Page
def verify_status(self):
    assert self.get_status() == "Active"
```

---

## 📚 Documentation

**Framework-Knowledge-Center:**
- [Quick Reference](Framework-Knowledge-Center/00-Quick-Reference/)
- [Getting Started](Framework-Knowledge-Center/01-Getting-Started/)
- [Architecture](Framework-Knowledge-Center/02-Architecture/)
- [Audit Reports](Framework-Knowledge-Center/08-Audit-Reports/)

**Key Documents:**
- [Architectural Audit](Framework-Knowledge-Center/08-Audit-Reports/Architectural/ARCHITECTURAL_AUDIT_REPORT_FINAL.md)
- [Implementation Complete](Framework-Knowledge-Center/06-Project-Status/Implementation/IMPLEMENTATION_COMPLETE.md)
- [POM Compliance](Framework-Knowledge-Center/08-Audit-Reports/POM-Compliance/POM_COMPLIANCE_ACHIEVEMENT_REPORT.md)

---

## 🧪 Testing

```bash
# By marker
pytest -m modern_spa
pytest -m legacy_ui
pytest -m bookslot

# By type
pytest tests/unit/
pytest tests/integration/
pytest tests/workflows/

# Parallel
pytest -n 4
pytest -n auto
```

---

## 📊 Reporting

```bash
# Allure
pytest --alluredir=allure-results
allure serve allure-results

# HTML
pytest --html=reports/report.html

# Video
pytest --video=retain-on-failure
```

---

## 🗺️ Roadmap

**✅ v1.0 (Complete - Jan 2026)**
- Hybrid architecture
- 100% compliance
- POM enforcement
- AI-powered testing

**🚧 v1.1 (In Progress)**
- Enhanced CI/CD
- Performance testing
- Visual regression
- Mobile expansion

**🔮 v2.0 (Future)**
- GraphQL testing
- gRPC support
- Kubernetes runners
- Analytics dashboard

---

## 👤 Author

**Lokendra Singh**  
📧 qa.lokendra@gmail.com  
🌐 [www.sqamentor.com](https://www.sqamentor.com)  
🐙 [@sqamentor](https://github.com/sqamentor)

---

## 📞 Support

📧 qa.lokendra@gmail.com  
🐛 [GitHub Issues](https://github.com/sqamentor/Hybrid_Automation/issues)  
📖 [Documentation](Framework-Knowledge-Center/INDEX.md)  
💬 [Discussions](https://github.com/sqamentor/Hybrid_Automation/discussions)

---

<div align="center">
  <strong>⭐ Star this repo if you find it useful! ⭐</strong>
  <br><br>
  <sub>Built for the next 30 years of software testing excellence.</sub>
  <br>
  <sub>100% Compliance | Zero Tolerance | Production Ready</sub>
</div>
