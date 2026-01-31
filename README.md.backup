# 🚀 Enterprise Automation Framework

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**Next-generation, AI-powered, hybrid automation framework for modern software testing.**

---

## ✨ Features

### 🎯 **Core Capabilities**
- ✅ **Hybrid UI Automation** - Playwright (modern) + Selenium (legacy) with intelligent auto-routing
- ✅ **Multi-Layer Testing** - UI + API + Database validation in single test
- ✅ **AI-Powered** - OpenAI GPT-4, Anthropic Claude integration for intelligent testing
- ✅ **Human Behavior Simulation** - Realistic mouse movements, typing delays, and interactions
- ✅ **Self-Healing Locators** - Automatic element location recovery
- ✅ **Visual Regression** - Pixel-perfect UI comparison with diff reports
- ✅ **Security Testing** - OWASP ZAP integration, vulnerability scanning
- ✅ **Accessibility Testing** - WCAG 2.1 AA/AAA compliance checks
- ✅ **Performance Monitoring** - Page load metrics, resource timing
- ✅ **Mobile Testing** - Device emulation, responsive testing
- ✅ **Test Recording** - Auto-generate tests from browser interactions

### 🏗️ **Architecture**
- ✅ **Page Object Model (POM)** - Clean, maintainable test code
- ✅ **Smart Actions Layer** - Context-aware, auto-delay actions
- ✅ **Fixture-Based Design** - Pytest fixtures for maximum reusability
- ✅ **Multi-Project Support** - Manage multiple applications from single framework
- ✅ **Environment Management** - Dev, Staging, Production configurations
- ✅ **Plug-and-Play** - Minimal setup, maximum productivity

### 📊 **Reporting & Observability**
- ✅ **Allure Reports** - Beautiful, interactive test reports
- ✅ **HTML Reports** - Pytest-HTML with screenshots and videos
- ✅ **Comprehensive Logging** - Structured logging with Loguru
- ✅ **Video Recording** - Full test execution capture
- ✅ **Screenshot on Failure** - Automatic failure diagnostics

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/lokendrasingh/automation.git
cd automation

# Install framework (one command!)
make install

# Or manually
pip install -e .
playwright install chromium
```

### Run Your First Test

```bash
# Option 1: Interactive POM CLI (Recommended) ⭐
python run_pom_tests_cli.py
# or double-click: run_pom.bat

# Option 2: Make commands
make run-bookslot

# Option 3: Direct pytest
pytest recorded_tests/bookslot/test_bookslot_complete_workflow.py -v --headed
```

### 🎯 Interactive POM Test Execution (NEW!)

The framework includes an **intelligent, interactive CLI** for executing Page Object Model tests:

```bash
# Launch interactive CLI
python run_pom_tests_cli.py
```

**Features:**
- ✅ Pre-flight validation (Python, pytest, Playwright, configs)
- ✅ Project selection (BookSlot, CallCenter, PatientIntake)
- ✅ Environment selection (Staging, Production)
- ✅ Browser configuration (Chromium, Firefox, WebKit, Chrome, Edge)
- ✅ Test scope selection (All tests, specific file, specific function)
- ✅ Human behavior toggle
- ✅ Parallel execution options
- ✅ HTML & Allure report generation
- ✅ Beautiful color-coded interface

**Quick Launch Options:**
```powershell
# Windows: PowerShell
.\run_pom.ps1              # Interactive mode
.\run_pom.ps1 -Quick       # Quick mode with defaults

# Windows: Batch (double-click)
run_pom.bat

# All platforms: Python
python run_pom_tests_cli.py
```

📖 **Documentation:**
- [Complete POM CLI Guide](Framework-Knowledge-Center/01-Getting-Started/Quick-Start/POM_TEST_RUNNER_README.md)
- [Quick Reference](Framework-Knowledge-Center/01-Getting-Started/Quick-Start/POM_CLI_GUIDE.md)
- [Visual Flow Diagrams](Framework-Knowledge-Center/01-Getting-Started/Quick-Start/POM_CLI_FLOW.md)

### 30-Second Example

```python
import pytest
from playwright.sync_api import Page

@pytest.mark.bookslot
def test_booking(page: Page, smart_actions, fake_bookslot_data):
    """Book appointment with auto-generated data and smart delays"""
    
    # Navigate
    smart_actions.navigate("https://bookslot.com", "Home Page")
    
    # Fill form (with human-like behavior)
    smart_actions.type_text(page.locator("#name"), fake_bookslot_data['first_name'])
    smart_actions.type_text(page.locator("#email"), fake_bookslot_data['email'])
    
    # Submit
    smart_actions.button_click(page.locator("#submit"), "Submit Form")
    
    # Assert
    assert page.locator(".success-message").is_visible()
```

**That's it!** No manual delays, no hardcoded data, human behavior included automatically.

---

## 📦 Installation Options

### Standard Installation
```bash
pip install -e .
```

### With AI Features
```bash
pip install -e ".[ai]"
```

### With Security Testing
```bash
pip install -e ".[security]"
```

### Full Installation (All Features)
```bash
pip install -e ".[all]"
```

### Development Setup
```bash
# Install with dev dependencies
make install-dev

# Or manually
pip install -e ".[dev]"
pre-commit install
```

---

## 🎯 Usage Examples

### Basic UI Test
```python
def test_login(page: Page):
    page.goto("https://example.com/login")
    page.fill("#username", "user@example.com")
    page.fill("#password", "password123")
    page.click("#login-button")
    assert page.locator(".dashboard").is_visible()
```

### With Smart Actions (Recommended)
```python
def test_login(page: Page, smart_actions):
    smart_actions.navigate("https://example.com/login", "Login Page")
    smart_actions.type_text(page.locator("#username"), "user@example.com")
    smart_actions.type_text(page.locator("#password"), "password123")
    smart_actions.button_click(page.locator("#login-button"), "Login")
    assert page.locator(".dashboard").is_visible()
```

### With Fake Data
```python
def test_registration(page: Page, smart_actions, fake_bookslot_data):
    """Uses auto-generated realistic test data"""
    smart_actions.navigate("https://example.com/register", "Registration")
    smart_actions.type_text(page.locator("#name"), fake_bookslot_data['first_name'])
    smart_actions.type_text(page.locator("#email"), fake_bookslot_data['email'])
    smart_actions.type_text(page.locator("#phone"), fake_bookslot_data['phone_number'])
    smart_actions.button_click(page.locator("#register"), "Register")
```

### Multi-Layer Testing (UI + API + DB)
```python
@pytest.mark.integration
def test_complete_workflow(page, api_client, db_validator):
    """Tests UI, validates via API, verifies in database"""
    
    # 1. UI: Create appointment
    page.goto("https://bookslot.com/book")
    page.fill("#date", "2026-02-01")
    page.click("#submit")
    appointment_id = page.locator(".confirmation-id").text_content()
    
    # 2. API: Verify creation
    response = api_client.get(f"/appointments/{appointment_id}")
    assert response.status_code == 200
    
    # 3. Database: Confirm persistence
    result = db_validator.query("SELECT * FROM appointments WHERE id = ?", appointment_id)
    assert result is not None
```

---

## 🔧 Configuration

### Environment Selection
```bash
# Run against staging (default)
pytest -v

# Run against production
pytest -v --env=production

# Run against dev
pytest -v --env=dev
```

### Browser Selection
```bash
# Chromium (default)
pytest -v

# Firefox
pytest -v --test-browser=firefox

# WebKit (Safari)
pytest -v --test-browser=webkit
```

### Human Behavior
```bash
# Enable human-like behavior
pytest -v --enable-human-behavior

# Disable for speed
pytest -v --disable-human-behavior
```

### Headless Mode
```bash
# Visible browser (default for development)
pytest -v --headed

# Headless (CI/CD)
pytest -v --headless
```

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
```

### Using Pytest Directly
```bash
# All tests
pytest -v

# Specific test
pytest recorded_tests/bookslot/test_bookslot_complete_workflow.py -v

# By marker
pytest -m bookslot -v
pytest -m smoke -v
pytest -m integration -v

# Parallel execution
pytest -v -n auto

# With Allure report
pytest --alluredir=allure-results
allure serve allure-results
```

---

## 🏗️ Project Structure

```
enterprise-automation-framework/
├── 📁 framework/              # Core framework code
│   ├── api/                   # API testing modules
│   ├── core/                  # Core utilities
│   │   ├── smart_actions.py   # Context-aware actions
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── utils/             # Helper functions
│   ├── ui/                    # UI automation engines
│   │   ├── playwright_engine.py
│   │   └── selenium_engine.py
│   ├── database/              # DB validation
│   ├── ai/                    # AI integration
│   ├── visual/                # Visual testing
│   ├── security/              # Security testing
│   ├── accessibility/         # A11y testing
│   └── mobile/                # Mobile testing
│
├── 📁 pages/                  # Page Objects
│   ├── bookslot/              # Bookslot app pages
│   ├── patientintake/         # Patient intake pages
│   └── callcenter/            # Call center pages
│
├── 📁 tests/                  # Core test suites
│   ├── integration/           # Integration tests
│   ├── ui/                    # UI tests
│   └── unit/                  # Unit tests
│
├── 📁 recorded_tests/         # Auto-generated tests
│   ├── bookslot/              # Bookslot tests
│   ├── patientintake/         # Patient intake tests
│   └── callcenter/            # Call center tests
│
├── 📁 config/                 # Configuration files
│   ├── projects.yaml          # Project URLs
│   ├── environments.yaml      # Environment configs
│   └── settings.py            # Settings manager
│
├── 📁 utils/                  # Utilities
│   ├── logger.py              # Logging setup
│   └── fake_data_generator.py # Test data generation
│
├── 📁 docs/                   # Documentation
├── 📁 examples/               # Example tests
├── conftest.py                # Pytest fixtures
├── pyproject.toml             # Modern Python config
├── Makefile                   # Task automation
└── README.md                  # This file
```

---

## 🎨 Code Quality

### Formatting
```bash
make format          # Format code with black + ruff
make format-check    # Check formatting only
```

### Linting
```bash
make lint            # Run ruff linter
make lint-fix        # Auto-fix issues
```

### Type Checking
```bash
make type-check      # Run mypy
```

### Security
```bash
make security        # Run bandit security scanner
```

### Pre-commit Hooks
```bash
make pre-commit      # Run all hooks manually
```

### Complete Quality Check
```bash
make quality         # Run all checks (lint + type + security)
```

---

## 🧪 Features in Detail

### Smart Actions Layer
Eliminates manual `time.sleep()` calls with intelligent, context-aware delays:

```python
# ❌ Old way (manual delays)
page.click("#button")
time.sleep(2)
page.fill("#input", "text")
time.sleep(1)

# ✅ New way (automatic delays)
smart_actions.click(page.locator("#button"))
smart_actions.type_text(page.locator("#input"), "text")
```

### Fake Data Generation
```python
def test_with_fake_data(fake_bookslot_data):
    """Auto-generates realistic data for each test run"""
    print(fake_bookslot_data)
    # Output:
    # {
    #   'first_name': 'John',
    #   'last_name': 'Smith',
    #   'email': 'john.smith.gq48e@example.com',
    #   'phone_number': '(555) 123-4567',
    #   'zip': '10001',
    #   'verification_code': '123456'
    # }
```

### Human Behavior Simulation
```python
@pytest.mark.human_like
def test_realistic_interaction(page):
    """Automatic human-like behavior when marker is present"""
    # Mouse movements, scroll, typing delays all automatic
    page.goto("https://example.com")
    page.click("#button")  # Includes realistic delays and movements
```

### Self-Healing Locators
```python
# If primary locator fails, automatically tries alternatives
element = page.locator("#submit-button")  # Primary
# Automatically falls back to:
# - text="Submit"
# - role="button"[name="Submit"]
# - [type="submit"]
```

---

## 🤖 AI Features

### AI-Powered Test Generation
```python
from framework.ai import NLTestGenerator

generator = NLTestGenerator(provider="openai")
test_code = generator.generate_test(
    "Test login with valid credentials and verify dashboard appears"
)
```

### AI Test Analysis
```python
from framework.ai import AIValidator

validator = AIValidator(provider="anthropic")
suggestions = validator.analyze_test_failure(
    test_name="test_checkout",
    error_message="Element not found: #submit-btn",
    screenshot_path="screenshots/failure.png"
)
```

---

## 📚 Documentation

- [Getting Started Guide](docs/getting_started.md)
- [Architecture Overview](docs/architecture.md)
- [API Documentation](docs/api/)
- [Browser Maximized Guide](docs/BROWSER_MAXIMIZED_GUIDE.md)
- [Project Audit Report](COMPREHENSIVE_PROJECT_AUDIT_2026.md)

---

## 🛠️ Development

### Setup Development Environment
```bash
# Install development dependencies
make install-dev

# Run tests
make test

# Check code quality
make quality

# Format code
make format
```

### Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 🐛 Troubleshooting

### Browser Not Maximized?
✅ **Fixed!** The framework now automatically maximizes browser windows. See [docs/BROWSER_MAXIMIZED_GUIDE.md](docs/BROWSER_MAXIMIZED_GUIDE.md)

### Import Errors?
```bash
# Reinstall in editable mode
pip install -e .
```

### Playwright Not Working?
```bash
# Install browsers
playwright install chromium
```

### Type Errors?
```bash
# Install type stubs
pip install types-PyYAML types-requests
```

---

## 📈 Roadmap

### ✅ Completed (v1.0.0)
- Hybrid Playwright + Selenium framework
- Multi-layer testing (UI + API + DB)
- Smart actions with auto-delays
- Human behavior simulation
- AI integration (OpenAI, Anthropic)
- Visual regression testing
- Security testing
- Modern Python packaging (pyproject.toml)

### 🚧 In Progress (v1.1.0)
- [ ] Async/await architecture migration
- [ ] Pydantic V2 configuration models
- [ ] Protocol classes for interfaces
- [ ] Enhanced CI/CD pipelines

### 🔮 Future (v2.0.0+)
- [ ] GraphQL testing support
- [ ] gRPC API testing
- [ ] Kubernetes test runners
- [ ] Distributed tracing
- [ ] Real-time test analytics dashboard
- [ ] GPT-5 integration (when available)

---

## 🏆 Best Practices

### 1. Use Smart Actions
```python
# ✅ Good
smart_actions.click(element)
smart_actions.type_text(element, text)

# ❌ Avoid
element.click()
time.sleep(2)
```

### 2. Use Fake Data
```python
# ✅ Good
def test_form(fake_bookslot_data):
    email = fake_bookslot_data['email']

# ❌ Avoid
email = "hardcoded@example.com"
```

### 3. Use Markers
```python
# ✅ Good
@pytest.mark.bookslot
@pytest.mark.integration
def test_workflow():
    ...
```

### 4. Use Page Objects
```python
# ✅ Good
from pages.bookslot import BookslotBasicInfoPage

page_obj = BookslotBasicInfoPage(page, url)
page_obj.fill_first_name("John")

# ❌ Avoid
page.fill("#firstName", "John")
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Lokendra Singh**
- Email: qa.lokendra@gmail.com
- Website: [www.sqamentor.com](https://www.sqamentor.com)
- GitHub: [@lokendrasingh](https://github.com/lokendrasingh)

---

## 🙏 Acknowledgments

- Built with ❤️ using Python 3.12
- Powered by [Playwright](https://playwright.dev/)
- Enhanced by [Pytest](https://pytest.org/)
- Assisted by AI (Claude Sonnet 4.5)

---

## 📞 Support

- 📧 Email: qa.lokendra@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/lokendrasingh/automation/issues)
- 📖 Docs: [Documentation Site](https://www.sqamentor.com/docs)

---

<div align="center">
  <strong>⭐ Star this repo if you find it useful! ⭐</strong>
  <br><br>
  <sub>Built for the next 30 years of software testing excellence.</sub>
</div>
