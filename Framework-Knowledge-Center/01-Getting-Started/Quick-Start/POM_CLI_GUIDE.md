# POM Test Execution CLI - Quick Reference Guide

## 🚀 Quick Start

```powershell
# Interactive mode (Recommended)
python run_pom_tests_cli.py

# Or on Windows
.\run_pom_tests_cli.py
```

---

## 📋 What This CLI Does

The **POM Test Runner CLI** provides an **interactive, intelligent, and failure-proof** way to execute Page Object Model tests.

### ✨ Key Features

1. **Pre-Flight Validation** ✓
   - Checks Python version
   - Validates pytest installation
   - Verifies Playwright installation
   - Confirms configuration files exist
   - Validates page objects directory
   - Checks fixture availability

2. **Interactive Project Selection** 🎯
   - Bookslot
   - CallCenter
   - PatientIntake
   - Shows project descriptions
   - Validates project availability

3. **Dynamic Environment Selection** 🌍
   - Staging
   - Production
   - Shows base URLs
   - Validates environment configuration

4. **Browser Configuration** 🌐
   - Chromium (default)
   - Firefox
   - WebKit (Safari)
   - Chrome
   - Microsoft Edge
   - Headless/Headed mode selection

5. **Flexible Test Scope** 📝
   - Run ALL POM tests
   - Run SPECIFIC test file
   - Run SPECIFIC test function
   - Auto-discovery of POM tests

6. **Human Behavior Simulation** 🤖
   - Enable/disable realistic interactions
   - Typing delays
   - Mouse movements
   - Reading pauses

7. **Execution Options** ⚙️
   - Parallel execution (auto or custom workers)
   - Pytest markers (smoke, regression, integration)
   - Custom arguments support

8. **Report Generation** 📊
   - HTML reports (with timestamp)
   - Allure reports
   - Auto-open option

9. **Validation & Safety** 🔒
   - Pre-execution validation
   - Configuration checks
   - Clear error messages
   - Confirmation before execution

---

## 🎯 Interactive Flow

### Step-by-Step Execution

1. **Pre-Flight Validation**
   ```
   ✓ Python version check
   ✓ pytest installation
   ✓ Playwright installation
   ✓ Configuration files
   ✓ Page objects
   ✓ Fixtures
   ```

2. **Project Selection**
   ```
   [1] BOOKSLOT - Patient appointment booking
   [2] CALLCENTER - Call center operations
   [3] PATIENTINTAKE - Patient intake system
   [0] Exit
   
   Select project [1]:
   ```

3. **Environment Selection**
   ```
   [1] STAGING - Base URL: https://bookslot-staging...
   [2] PRODUCTION - Base URL: https://bookslots...
   [0] Back
   
   Select environment [1]:
   ```

4. **Browser Configuration**
   ```
   [1] CHROMIUM - Fast and reliable
   [2] FIREFOX - Good for cross-browser testing
   [3] WEBKIT - Safari engine
   [4] CHROME - Most popular
   [5] MSEDGE - Chromium-based
   
   Select browser [1]: 1
   Run in headless mode? [Y/n]: n
   ```

5. **Test Scope Selection**
   ```
   [1] Run ALL POM tests
   [2] Run SPECIFIC test file
   [3] Run SPECIFIC test function
   
   Select scope [1]:
   ```

6. **Human Behavior Configuration**
   ```
   Enable human behavior simulation? [Y/n]: y
   ✓ Human behavior: ENABLED
   ```

7. **Execution Options**
   ```
   Enable parallel execution? [y/N]: y
   Number of workers [auto]: 4
   Add pytest markers? [y/N]: y
   Enter markers: smoke, integration
   ```

8. **Report Configuration**
   ```
   Generate HTML report? [Y/n]: y
   Generate Allure report? [y/N]: n
   ```

9. **Execution Summary & Confirmation**
   ```
   Test Execution Configuration:
     🎯 Project: bookslot
     🌍 Environment: staging
     🌐 Browser: chromium (headed)
     🤖 Human Behavior: Enabled
     ⚡ Parallel: 4 workers
     📊 HTML Report: Yes
   
   Command to Execute:
   ────────────────────────────────────────────────
   pytest --project=bookslot --env=staging 
   --browser=chromium -m human_like -n 4 
   --html=reports/pom_test_report_20260129_143022.html 
   --self-contained-html -v tests/integration
   ────────────────────────────────────────────────
   
   Execute tests now? [Y/n]:
   ```

10. **Test Execution**
    ```
    🚀 Starting test execution...
    
    [Test output...]
    
    ✓ Tests completed successfully!
    ℹ HTML Report: reports/pom_test_report_20260129_143022.html
    Open HTML report? [y/N]:
    ```

---

## 📊 Example Usage Scenarios

### Scenario 1: Quick Smoke Test on Staging

```
1. Run: python run_pom_tests_cli.py
2. Select project: 1 (BookSlot)
3. Select environment: 1 (Staging)
4. Select browser: 1 (Chromium)
5. Headless: n
6. Scope: 1 (All tests)
7. Human behavior: y
8. Parallel: n
9. Markers: smoke
10. HTML report: y
11. Execute: y
```

**Result:** All BookSlot smoke tests run on staging with human behavior

---

### Scenario 2: Production Validation - Specific Test

```
1. Run: python run_pom_tests_cli.py
2. Select project: 1 (BookSlot)
3. Select environment: 2 (Production)
4. Select browser: 1 (Chromium)
5. Headless: y
6. Scope: 3 (Specific function)
7. Select file: test_bookslot_to_patientintake.py
8. Select function: test_book_appointment_and_verify_in_patientintake
9. Human behavior: n (faster)
10. Parallel: n
11. Markers: none
12. HTML report: y
13. Execute: y
```

**Result:** Single test runs on production, headless, fast execution

---

### Scenario 3: Full Regression - Parallel Execution

```
1. Run: python run_pom_tests_cli.py
2. Select project: 1 (BookSlot)
3. Select environment: 1 (Staging)
4. Select browser: 1 (Chromium)
5. Headless: y
6. Scope: 1 (All tests)
7. Human behavior: n
8. Parallel: y
9. Workers: auto
10. Markers: regression, integration
11. HTML report: y
12. Allure: y
13. Execute: y
```

**Result:** Full regression suite, parallel execution, both reports

---

### Scenario 4: Cross-Browser Testing

```
Run 3 times with different browsers:
- Browser: Chromium
- Browser: Firefox
- Browser: WebKit

Compare results across browsers
```

---

## 🛠️ Advanced Options

### Manual Command Building

If you need to bypass interactive mode, you can still use pytest directly:

```powershell
# Example: Run specific POM test
pytest tests/integration/test_bookslot_to_patientintake.py::test_book_appointment_and_verify_in_patientintake --project=bookslot --env=staging --browser=chromium -m human_like -v --html=reports/report.html --self-contained-html

# Example: Run all integration tests with parallel execution
pytest tests/integration --project=bookslot --env=staging --browser=chromium -m human_like -n 4 -v --html=reports/report.html --self-contained-html

# Example: Run with specific markers
pytest tests/integration -m "smoke and human_like" --project=bookslot --env=staging --browser=chromium -v
```

---

## 🔍 Pre-Flight Validation Details

The CLI automatically validates:

| Check | What It Does | Why It Matters |
|-------|-------------|----------------|
| Python Version | Ensures Python >= 3.8 | Framework compatibility |
| pytest | Checks pytest is installed | Required for test execution |
| Playwright | Verifies Playwright browsers | Browser automation |
| Config Files | Validates projects.yaml, environments.yaml | URL configuration |
| Page Objects | Checks pages/ directory exists | POM structure |
| Fixtures | Validates conftest.py has POM fixtures | Test dependencies |

---

## 📝 Configuration Files Used

The CLI reads from:

1. **config/projects.yaml**
   - Project definitions (bookslot, callcenter, patientintake)
   - Environment URLs (staging, production)
   - Project-specific settings

2. **config/environments.yaml**
   - Environment configurations
   - Browser settings
   - Timeout values

3. **tests/conftest.py**
   - POM fixtures (bookslot_page, etc.)
   - Test setup and teardown

---

## 🎨 Output Features

### Color-Coded Output

- 🟢 **Green**: Success messages, selected options
- 🔵 **Blue**: Information messages
- 🟡 **Yellow**: Warnings, prompts
- 🔴 **Red**: Errors, failures
- 🟣 **Cyan**: Section headers, commands

### Beautiful Formatting

- Box borders for sections
- Clear option numbering
- Command preview before execution
- Progress indicators
- Summary tables

---

## 🚨 Error Handling

The CLI handles errors gracefully:

1. **Missing Configuration**
   ```
   ✗ Config missing: projects.yaml
   Continue despite validation failures? [y/N]:
   ```

2. **No Tests Found**
   ```
   ⚠ No POM tests found for project: bookslot
   ℹ Found 3 integration tests
   ```

3. **Invalid Selection**
   ```
   ✗ Invalid selection
   Select project [1]:
   ```

4. **Execution Failure**
   ```
   ✗ Tests failed with exit code: 1
   ℹ HTML Report: reports/pom_test_report_20260129_143022.html
   ```

---

## 💡 Best Practices

1. **Always run pre-flight validation** - Catches issues early
2. **Use staging first** - Validate before production
3. **Enable human behavior for realistic tests** - Better mirrors user actions
4. **Use parallel execution for large suites** - Faster results
5. **Generate HTML reports** - Easy result analysis
6. **Start with specific tests** - Debug issues quickly
7. **Use markers effectively** - Run targeted test suites

---

## 🔧 Troubleshooting

### Issue: "pytest not found"

**Solution:**
```powershell
pip install pytest pytest-playwright pytest-html
```

---

### Issue: "Playwright not found"

**Solution:**
```powershell
pip install playwright
playwright install
```

---

### Issue: "No POM tests found"

**Solution:**
- Check tests use page object fixtures (bookslot_page, etc.)
- Verify tests are in tests/integration directory
- Ensure test files start with test_

---

### Issue: "Configuration file missing"

**Solution:**
- Check config/projects.yaml exists
- Check config/environments.yaml exists
- Verify YAML syntax is correct

---

## 📞 Support

For issues or questions:
- **Email**: qa.lokendra@gmail.com
- **Website**: www.sqamentor.com
- **Check logs**: Look for detailed error messages in console output

---

## 🎓 Learning Resources

### Understanding POM

The framework follows Page Object Model pattern:
- **pages/** - Page object classes
- **tests/** - Test implementations
- **fixtures** - Dependency injection via conftest.py

### Key Concepts

1. **Page Objects**: Encapsulate page elements and actions
2. **Fixtures**: Provide test dependencies (page instances)
3. **Markers**: Tag tests for selective execution
4. **Human Behavior**: Simulate realistic user interactions

---

## 🚀 Quick Command Reference

| Command | Description |
|---------|-------------|
| `python run_pom_tests_cli.py` | Start interactive CLI |
| Press `Ctrl+C` | Cancel execution anytime |
| Enter `0` | Go back to previous menu |
| Press `Enter` | Accept default option |

---

## ✅ Checklist Before Running

- [ ] Python >= 3.8 installed
- [ ] pytest installed
- [ ] Playwright installed and browsers setup
- [ ] Configuration files exist (projects.yaml, environments.yaml)
- [ ] Page objects exist in pages/ directory
- [ ] Fixtures defined in tests/conftest.py
- [ ] Test files exist in tests/ directory

---

**Happy Testing! 🎉**
