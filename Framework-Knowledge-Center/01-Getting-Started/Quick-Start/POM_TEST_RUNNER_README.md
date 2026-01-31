# 🎯 POM Test Execution System - README

## Overview

The **POM Test Execution CLI** is an interactive, intelligent, and failure-proof command-line interface designed specifically for executing **Page Object Model (POM) based tests** in this automation framework.

This CLI eliminates the complexity of manual pytest command construction and provides a guided, validated, and safe way to run your POM tests.

---

## 🚀 Quick Start

### Windows Users

**Option 1: Double-Click (Easiest)**
```
Double-click: run_pom.bat
```

**Option 2: PowerShell**
```powershell
.\run_pom.ps1
```

**Option 3: Python Direct**
```powershell
python run_pom_tests_cli.py
```

### Linux/Mac Users

```bash
python3 run_pom_tests_cli.py
```

---

## ✨ Key Features

### 1. **Pre-Flight Validation** ✓
Automatically validates your environment before execution:
- Python version (>= 3.8)
- pytest installation
- Playwright installation & browsers
- Configuration files (projects.yaml, environments.yaml)
- Page objects directory structure
- Test fixtures availability

### 2. **Interactive Project Selection** 🎯
- **BookSlot** - Patient appointment booking system
- **CallCenter** - Call center operations management
- **PatientIntake** - Patient intake system
- Shows project descriptions and URLs

### 3. **Dynamic Environment Selection** 🌍
- **Staging** - Pre-production testing environment
- **Production** - Live production environment
- Displays base URLs for verification
- Validates environment configuration

### 4. **Flexible Browser Configuration** 🌐
Supports multiple browsers:
- Chromium (default, recommended)
- Firefox
- WebKit (Safari engine)
- Google Chrome
- Microsoft Edge

**Modes:**
- Headed (visible browser)
- Headless (background execution)

### 5. **Smart Test Discovery** 📝
Automatically discovers POM tests:
- Scans tests that use page object fixtures
- Groups by project
- Extracts test functions
- Shows relative paths

**Scope Options:**
- Run ALL POM tests
- Run SPECIFIC test file
- Run SPECIFIC test function

### 6. **Human Behavior Simulation** 🤖
Toggle realistic user interactions:
- Typing delays
- Mouse movements
- Reading pauses
- Natural scrolling

Perfect for:
- Demo recordings
- Client presentations
- Realistic load testing

### 7. **Advanced Execution Options** ⚙️

**Parallel Execution:**
- Auto-detect CPU cores
- Custom worker count
- Faster test execution

**Pytest Markers:**
- smoke
- regression
- integration
- critical
- custom markers

### 8. **Comprehensive Reporting** 📊

**HTML Reports:**
- Self-contained HTML file
- Timestamped filenames
- Screenshots on failure
- Test duration metrics
- Environment metadata

**Allure Reports:**
- Rich test reports
- Trend analysis
- Categories and suites
- Historical data

### 9. **Safety & Validation** 🔒
- Configuration validation
- URL verification
- Dependency checks
- Clear error messages
- Confirmation before execution
- Graceful error handling

---

## 📋 Interactive Flow

### Complete Step-by-Step Guide

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: Pre-Flight Validation                           │
├─────────────────────────────────────────────────────────┤
│ ✓ Python 3.11.5                                         │
│ ✓ pytest installed: pytest 7.4.0                        │
│ ✓ Playwright installed: Version 1.40.0                  │
│ ✓ Config found: projects.yaml                           │
│ ✓ Config found: environments.yaml                       │
│ ✓ Page Objects found: bookslot, callcenter, patientintake│
│ ✓ POM fixtures found: bookslot_page, patientintake_page │
│ ✓ All pre-flight checks passed!                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Step 2: Project Selection                               │
├─────────────────────────────────────────────────────────┤
│ [1] BOOKSLOT                                            │
│     Patient appointment booking and slot management     │
│ [2] CALLCENTER                                          │
│     Call center operations and appointment management   │
│ [3] PATIENTINTAKE                                       │
│     Patient intake and appointment management           │
│ [0] Exit                                                │
│                                                         │
│ ❯ Select project [1]: 1                                │
│ ✓ Selected: bookslot                                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Step 3: Environment Selection                           │
├─────────────────────────────────────────────────────────┤
│ [1] STAGING                                             │
│     Base URL: https://bookslot-staging.centerforvein.com│
│ [2] PRODUCTION                                          │
│     Base URL: https://bookslots.centerforvein.com       │
│ [0] Back                                                │
│                                                         │
│ ❯ Select environment [1]: 1                             │
│ ✓ Selected: staging                                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Step 4: Browser Configuration                           │
├─────────────────────────────────────────────────────────┤
│ [1] CHROMIUM - Fast and reliable                        │
│ [2] FIREFOX - Good for cross-browser testing            │
│ [3] WEBKIT - Safari engine                              │
│ [4] CHROME - Most popular                               │
│ [5] MSEDGE - Chromium-based                             │
│                                                         │
│ ❯ Select browser [1]: 1                                 │
│ ❯ Run in headless mode? [y/N]: n                        │
│ ✓ Browser: chromium (headed)                            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Step 5: Test Scope Selection                            │
├─────────────────────────────────────────────────────────┤
│ [1] Run ALL POM tests                                   │
│     Execute all tests for bookslot                      │
│ [2] Run SPECIFIC test file                              │
│     Choose a single test file                           │
│ [3] Run SPECIFIC test function                          │
│     Choose a single test function                       │
│                                                         │
│ ❯ Select scope [1]: 2                                   │
│                                                         │
│ Available test files:                                   │
│ [1] test_bookslot_to_patientintake.py                   │
│     tests/integration/test_bookslot_to_patientintake.py │
│ [2] test_three_system_workflow.py                       │
│     tests/integration/test_three_system_workflow.py     │
│                                                         │
│ ❯ Select test file [1]: 1                               │
│ ✓ Selected: test_bookslot_to_patientintake.py          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Step 6: Human Behavior Simulation                       │
├─────────────────────────────────────────────────────────┤
│ Human behavior simulation adds realistic delays         │
│   • Typing delays                                       │
│   • Mouse movements                                     │
│   • Reading pauses                                      │
│   • Natural scrolling                                   │
│                                                         │
│ ❯ Enable human behavior simulation? [Y/n]: y           │
│ ✓ Human behavior: ENABLED                               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Step 7: Execution Options                               │
├─────────────────────────────────────────────────────────┤
│ ❯ Enable parallel execution? [y/N]: y                   │
│ ❯ Number of workers [auto]: 4                           │
│ ✓ Parallel: 4 workers                                   │
│                                                         │
│ ❯ Add pytest markers? [y/N]: y                          │
│ Common markers: smoke, regression, integration, critical│
│ ❯ Enter markers (comma-separated): integration          │
│ ✓ Markers: integration                                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Step 8: Report Configuration                            │
├─────────────────────────────────────────────────────────┤
│ ❯ Generate HTML report? [Y/n]: y                        │
│ ✓ HTML report: ENABLED                                  │
│                                                         │
│ ❯ Generate Allure report? [y/N]: n                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Step 9: Execution Summary                               │
├─────────────────────────────────────────────────────────┤
│ Test Execution Configuration:                           │
│                                                         │
│   🎯 Project: bookslot                                  │
│   🌍 Environment: staging                               │
│   🌐 Browser: chromium (headed)                         │
│   🤖 Human Behavior: Enabled                            │
│   📄 Test File: test_bookslot_to_patientintake.py       │
│   ⚡ Parallel: 4 workers                                │
│   📊 HTML Report: Yes                                   │
│                                                         │
│ 📝 Command to Execute:                                  │
│ ────────────────────────────────────────────────────────│
│ pytest tests/integration/test_bookslot_to_patientintake.py│
│ --project=bookslot --env=staging --browser=chromium    │
│ -m human_like -n 4 --html=reports/pom_test_report_     │
│ 20260129_143022.html --self-contained-html -v           │
│ ────────────────────────────────────────────────────────│
│                                                         │
│ ❯ Execute tests now? [Y/n]: y                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Step 10: Test Execution                                 │
├─────────────────────────────────────────────────────────┤
│ 🚀 Starting test execution...                           │
│                                                         │
│ ===================== test session starts ===============│
│ platform win32 -- Python 3.11.5, pytest-7.4.0          │
│ collected 3 items                                        │
│                                                         │
│ test_bookslot_to_patientintake.py::test_book... PASSED │
│ test_bookslot_to_patientintake.py::test_cros... PASSED │
│                                                         │
│ ==================== 3 passed in 45.23s =================│
│                                                         │
│ ✓ Tests completed successfully!                         │
│ ℹ HTML Report: reports/pom_test_report_20260129_143022.html│
│                                                         │
│ ❯ Open HTML report? [y/N]: y                            │
│ [Browser opens with report]                             │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Usage Examples

### Example 1: Quick Smoke Test

**Scenario:** Run smoke tests on staging before deployment

```powershell
# Launch CLI
python run_pom_tests_cli.py

# Selections:
# - Project: bookslot
# - Environment: staging
# - Browser: chromium (headed)
# - Scope: All tests
# - Human behavior: No (faster)
# - Parallel: Yes (auto)
# - Markers: smoke
# - HTML report: Yes
```

**Result:** All smoke tests execute in parallel, HTML report generated

---

### Example 2: Production Validation

**Scenario:** Validate critical functionality on production

```powershell
# Launch CLI
python run_pom_tests_cli.py

# Selections:
# - Project: bookslot
# - Environment: production
# - Browser: chromium (headless)
# - Scope: Specific function
#   - File: test_bookslot_to_patientintake.py
#   - Function: test_book_appointment_and_verify_in_patientintake
# - Human behavior: Yes (realistic)
# - Parallel: No (single test)
# - Markers: critical
# - HTML report: Yes
# - Allure: Yes
```

**Result:** Single critical test runs on production with full reporting

---

### Example 3: Cross-Browser Testing

**Scenario:** Test BookSlot on multiple browsers

```powershell
# Run 1: Chromium
python run_pom_tests_cli.py
# Select: bookslot, staging, chromium, all tests

# Run 2: Firefox
python run_pom_tests_cli.py
# Select: bookslot, staging, firefox, all tests

# Run 3: WebKit
python run_pom_tests_cli.py
# Select: bookslot, staging, webkit, all tests
```

**Result:** Compare results across three browsers

---

### Example 4: Regression Suite

**Scenario:** Full regression testing before release

```powershell
# Launch CLI
python run_pom_tests_cli.py

# Selections:
# - Project: bookslot
# - Environment: staging
# - Browser: chromium (headless)
# - Scope: All tests
# - Human behavior: No (faster)
# - Parallel: Yes (auto)
# - Markers: regression, integration
# - HTML report: Yes
# - Allure: Yes
```

**Result:** Complete regression suite with comprehensive reports

---

## 🔧 Configuration

The CLI reads from these configuration files:

### 1. config/projects.yaml
```yaml
projects:
  bookslot:
    name: "BookSlot Appointment System"
    environments:
      staging:
        ui_url: "https://bookslot-staging.centerforvein.com"
      production:
        ui_url: "https://bookslots.centerforvein.com"
```

### 2. config/environments.yaml
```yaml
environments:
  staging:
    base_url: "https://staging.centerforvein.com"
    browser:
      headless: false
      timeout: 30000
  production:
    base_url: "https://centerforvein.com"
    browser:
      headless: true
      timeout: 30000
```

### 3. tests/conftest.py
```python
@pytest.fixture
def bookslot_page(page, bookslot_config):
    from pages.bookslot import BookslotBasicInfoPage
    return BookslotBasicInfoPage(page, bookslot_config['ui_url'])
```

---

## 📊 Reports

### HTML Reports

Generated at: `reports/pom_test_report_YYYYMMDD_HHMMSS.html`

**Contents:**
- Test results summary
- Individual test details
- Screenshots on failure
- Execution duration
- Environment metadata
- Browser information

**Features:**
- Self-contained (no external dependencies)
- Can be shared via email
- Opens in any browser
- Searchable and filterable

### Allure Reports

Generated at: `allure-results/`

**View Report:**
```powershell
allure serve allure-results
```

**Features:**
- Trend analysis
- Categories
- Suites and packages
- Historical data
- Timeline view

---

## 🛠️ Troubleshooting

### Issue: "pytest not found"

**Solution:**
```powershell
pip install pytest pytest-playwright pytest-html pytest-xdist
```

---

### Issue: "Playwright not found"

**Solution:**
```powershell
pip install playwright
playwright install
playwright install-deps
```

---

### Issue: "No POM tests found"

**Cause:** Tests don't use page object fixtures

**Solution:** Ensure tests use fixtures:
```python
def test_example(bookslot_page):  # ← Uses POM fixture
    bookslot_page.navigate()
```

---

### Issue: "Configuration file missing"

**Solution:** Verify files exist:
- `config/projects.yaml`
- `config/environments.yaml`

---

### Issue: "Python version incompatible"

**Solution:** Upgrade Python:
```powershell
# Check version
python --version

# Requires Python >= 3.8
```

---

## 💡 Best Practices

1. **Always start with staging** - Test on staging before production
2. **Use pre-flight validation** - Let the CLI check your environment
3. **Enable human behavior for demos** - Makes tests look realistic
4. **Disable human behavior for CI/CD** - Faster execution
5. **Use parallel execution** - Speed up large test suites
6. **Generate HTML reports** - Easy to share and archive
7. **Use markers effectively** - Run targeted test suites
8. **Start with specific tests** - Debug issues on single tests first
9. **Use headless for CI/CD** - Background execution on servers
10. **Use headed for debugging** - See what's happening

---

## 📚 Additional Resources

- **[POM_CLI_GUIDE.md](POM_CLI_GUIDE.md)** - Comprehensive guide with scenarios
- **[HOW_TO_RUN_BOOKSLOT_TESTS.md](Framework-Knowledge-Center/01-Getting-Started/Quick-Start/HOW_TO_RUN_BOOKSLOT_TESTS.md)** - BookSlot-specific guide
- **[QUICK_START_GUIDE.md](Framework-Knowledge-Center/01-Getting-Started/Quick-Start/QUICK_START_GUIDE.md)** - General quick start

---

## 🎓 Understanding POM

This CLI is designed for **Page Object Model (POM)** tests:

**What is POM?**
- Design pattern for test automation
- Separates page structure from test logic
- Improves maintainability

**Framework Structure:**
```
pages/              ← Page Object classes
├── bookslot/
├── callcenter/
└── patientintake/

tests/              ← Test implementations
├── integration/
└── conftest.py     ← POM fixtures
```

**How POM Works:**
```python
# Page Object (pages/bookslot/bookslots_basicinfo.py)
class BookslotBasicInfoPage:
    def navigate(self): ...
    def fill_patient_info(self, data): ...

# Test (tests/integration/test_bookslot.py)
def test_booking(bookslot_page):
    bookslot_page.navigate()
    bookslot_page.fill_patient_info(data)
```

---

## 🚀 Advanced Usage

### Run Specific Test with Custom Options

While the CLI is interactive, you can also use pytest directly:

```powershell
pytest tests/integration/test_bookslot_to_patientintake.py::test_book_appointment_and_verify_in_patientintake --project=bookslot --env=staging --browser=chromium -m human_like -v --html=reports/custom_report.html --self-contained-html
```

### Parallel Execution Tips

```powershell
# Auto-detect cores
-n auto

# Specific worker count
-n 4

# With test isolation
-n 4 --dist loadscope
```

### Marker Combinations

```powershell
# Run smoke AND integration tests
-m "smoke and integration"

# Run critical OR high priority
-m "critical or high"

# Run everything except slow tests
-m "not slow"
```

---

## 📞 Support

**Author:** Lokendra Singh  
**Email:** qa.lokendra@gmail.com  
**Website:** www.sqamentor.com

**For Issues:**
1. Check pre-flight validation output
2. Review error messages in console
3. Verify configuration files
4. Check [POM_CLI_GUIDE.md](POM_CLI_GUIDE.md)
5. Contact support

---

## 📝 Changelog

### Version 1.0.0 (2026-01-29)
- Initial release
- Interactive CLI for POM test execution
- Pre-flight validation system
- Project/environment selection
- Browser configuration
- Test discovery and selection
- Human behavior toggle
- Parallel execution support
- HTML and Allure reporting
- Windows launcher scripts (PowerShell, Batch)

---

## ✅ Quick Checklist

Before running tests, ensure:

- [ ] Python >= 3.8 installed
- [ ] pytest installed (`pip install pytest`)
- [ ] Playwright installed (`pip install playwright`)
- [ ] Playwright browsers installed (`playwright install`)
- [ ] Configuration files exist (projects.yaml, environments.yaml)
- [ ] Page objects exist in pages/ directory
- [ ] Test fixtures defined in tests/conftest.py
- [ ] Test files exist in tests/integration directory

---

**Happy Testing! 🎉**

*This CLI makes POM test execution simple, safe, and efficient.*
