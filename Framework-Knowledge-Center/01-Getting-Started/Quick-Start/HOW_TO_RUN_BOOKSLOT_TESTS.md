# How to Run BookSlot Test Cases

**Quick Reference Guide for Running BookSlot Automation Tests**

---

## 📋 Available BookSlot Tests

### Test Files Location
```
tests/integration/
├── test_bookslot_to_patientintake.py  (4 test functions)
└── test_three_system_workflow.py      (includes BookSlot tests)

pages/bookslot/
└── bookslot_complete_worklfow.py      (1 E2E test)
```

---

## 🚀 Quick Start Commands

### 1. **Run ALL BookSlot Tests**

```bash
# Run all tests with 'bookslot' marker
pytest -m bookslot -v

# With human behavior simulation
pytest -m bookslot --enable-human-behavior -v

# With HTML report
pytest -m bookslot -v --html=reports/bookslot_report.html
```

### 2. **Run Integration Tests Only**

```bash
# Run BookSlot to PatientIntake integration tests
pytest tests/integration/test_bookslot_to_patientintake.py -v

# With human behavior
pytest tests/integration/test_bookslot_to_patientintake.py --enable-human-behavior -v

# Run specific test function
pytest tests/integration/test_bookslot_to_patientintake.py::TestBookslotToPatientIntake::test_book_appointment_and_verify_in_patientintake -v
```

### 3. **Run Complete E2E Workflow Test**

```bash
# Run the complete workflow test from page object
pytest pages/bookslot/bookslot_complete_worklfow.py -v

# With human behavior (realistic timing)
pytest pages/bookslot/bookslot_complete_worklfow.py --enable-human-behavior -v

# With headed browser (see execution)
pytest pages/bookslot/bookslot_complete_worklfow.py --headed -v
```

---

## 📊 Test Categories

### By Test Type

#### **Integration Tests** (Cross-Application)
```bash
# BookSlot → PatientIntake flow
pytest tests/integration/test_bookslot_to_patientintake.py -v

# BookSlot → PatientIntake → CallCenter flow
pytest tests/integration/test_three_system_workflow.py -v
```

#### **E2E Tests** (Complete Workflow)
```bash
# Complete booking flow (all 6 pages)
pytest -m "bookslot and e2e" -v

# Complete workflow with human behavior
pytest pages/bookslot/bookslot_complete_worklfow.py --enable-human-behavior -v
```

#### **Smoke Tests** (Critical Paths)
```bash
# Critical BookSlot functionality
pytest -m "bookslot and smoke" -v
```

---

## 🎯 Run Specific Test Functions

### Available Test Functions

1. **test_book_appointment_and_verify_in_patientintake**
   ```bash
   pytest tests/integration/test_bookslot_to_patientintake.py::TestBookslotToPatientIntake::test_book_appointment_and_verify_in_patientintake -v
   ```

2. **test_multiple_appointments_data_consistency**
   ```bash
   pytest tests/integration/test_bookslot_to_patientintake.py::TestBookslotToPatientIntake::test_multiple_appointments_data_consistency -v
   ```

3. **test_appointment_with_full_details**
   ```bash
   pytest tests/integration/test_bookslot_to_patientintake.py::TestBookslotToPatientIntake::test_appointment_with_full_details -v
   ```

4. **test_end_to_end_patient_journey**
   ```bash
   pytest tests/integration/test_bookslot_to_patientintake.py::TestCrossApplicationWorkflow::test_end_to_end_patient_journey -v
   ```

5. **test_bookslot_complete_workflow**
   ```bash
   pytest pages/bookslot/bookslot_complete_worklfow.py::test_bookslot_complete_workflow -v
   ```

---

## 🎭 Human Behavior Simulation

### Enable Human Behavior (Realistic User Simulation)

```bash
# Enable globally
pytest -m bookslot --enable-human-behavior -v

# Set intensity level
pytest -m bookslot --enable-human-behavior --human-behavior-intensity high -v

# Options:
#   - minimal  (quick validation)
#   - normal   (standard timing)
#   - high     (maximum realism)
```

### When to Use Human Behavior

✅ **Use Human Behavior:**
- Demo recordings
- Production testing
- Anti-bot validation
- UX testing
- Visual proof videos

❌ **Skip Human Behavior:**
- CI/CD pipelines (default)
- Smoke tests
- Quick validation
- Performance testing

---

## 🌍 Environment-Specific Testing

### Run on Different Environments

```bash
# Staging environment (default)
pytest -m bookslot --env=staging -v

# Production environment
pytest -m bookslot --env=production -v

# Development environment
pytest -m bookslot --env=dev -v
```

### Environment + Human Behavior

```bash
# Production with human behavior
pytest -m bookslot --env=production --enable-human-behavior -v

# Staging with high intensity
pytest -m bookslot --env=staging --enable-human-behavior --human-behavior-intensity high -v
```

---

## 🎨 Browser Options

### Headed vs Headless

```bash
# Headless (default - faster, no UI)
pytest -m bookslot -v

# Headed (see browser execution)
pytest -m bookslot --headed -v

# Headed with slow motion (watch execution)
pytest -m bookslot --headed --slowmo=500 -v
```

### Browser Selection

```bash
# Use Chromium (default)
pytest -m bookslot --browser=chromium -v

# Use Firefox
pytest -m bookslot --browser=firefox -v

# Use WebKit (Safari)
pytest -m bookslot --browser=webkit -v
```

---

## 📝 Reporting Options

### Generate Test Reports

```bash
# HTML Report
pytest -m bookslot -v --html=reports/bookslot_report.html --self-contained-html

# Allure Report
pytest -m bookslot -v --alluredir=allure-results
allure serve allure-results

# JUnit XML Report
pytest -m bookslot -v --junitxml=reports/bookslot_junit.xml

# JSON Report
pytest -m bookslot -v --json-report --json-report-file=reports/bookslot_report.json
```

---

## 🔍 Filtering Tests

### By Pytest Markers

```bash
# Critical tests only
pytest -m "bookslot and critical" -v

# Smoke tests
pytest -m "bookslot and smoke" -v

# E2E tests
pytest -m "bookslot and e2e" -v

# Human-like tests
pytest -m "bookslot and human_like" --enable-human-behavior -v

# Regression tests
pytest -m "bookslot and regression" -v

# Exclude slow tests
pytest -m "bookslot and not slow" -v
```

### By Module

```bash
# Basic info module
pytest -m "bookslot and module('basic_info')" -v

# Personal info module
pytest -m "bookslot and module('personal_info')" -v

# Complete workflow
pytest -m "bookslot and module('complete_workflow')" -v
```

---

## ⚡ Parallel Execution

### Run Tests in Parallel (Faster)

```bash
# Install pytest-xdist first
pip install pytest-xdist

# Run with 4 parallel workers
pytest -m bookslot -v -n 4

# Auto-detect CPU cores
pytest -m bookslot -v -n auto

# Parallel with human behavior (not recommended)
pytest -m bookslot --enable-human-behavior -v -n 2
```

---

## 🐛 Debug Mode

### Run with Debugging

```bash
# Show print statements
pytest -m bookslot -v -s

# Stop on first failure
pytest -m bookslot -v -x

# Drop to debugger on failure
pytest -m bookslot -v --pdb

# Show full traceback
pytest -m bookslot -v --tb=long

# Show local variables on failure
pytest -m bookslot -v -l
```

---

## 📹 Recording & Screenshots

### Capture Test Evidence

```bash
# Take screenshots on failure
pytest -m bookslot -v --screenshot=on

# Record video
pytest -m bookslot -v --video=on

# Record trace (Playwright inspector)
pytest -m bookslot -v --tracing=on

# Keep videos only on failure
pytest -m bookslot -v --video=retain-on-failure
```

---

## 🎬 Complete Example Commands

### Example 1: Quick Smoke Test (Fast)
```bash
pytest -m "bookslot and smoke" -v --html=reports/smoke.html
```
**Duration:** ~2-3 minutes  
**Use Case:** Quick validation before release

### Example 2: Complete E2E with Human Behavior (Demo)
```bash
pytest pages/bookslot/bookslot_complete_worklfow.py \
  --enable-human-behavior \
  --human-behavior-intensity high \
  --headed \
  --slowmo=500 \
  --video=on \
  -v
```
**Duration:** ~3-5 minutes  
**Use Case:** Demo recording, stakeholder presentation

### Example 3: Integration Tests on Production
```bash
pytest tests/integration/test_bookslot_to_patientintake.py \
  --env=production \
  --enable-human-behavior \
  --html=reports/production_integration.html \
  -v
```
**Duration:** ~5-8 minutes  
**Use Case:** Production validation

### Example 4: Full Regression Suite
```bash
pytest -m "bookslot and regression" \
  --env=staging \
  --html=reports/regression.html \
  --self-contained-html \
  -v \
  -n 4
```
**Duration:** ~10-15 minutes (parallel)  
**Use Case:** Release regression testing

### Example 5: CI/CD Pipeline (Fast)
```bash
pytest -m bookslot \
  --disable-human-behavior \
  --headless \
  --junitxml=reports/junit.xml \
  -v \
  -n auto
```
**Duration:** ~3-5 minutes  
**Use Case:** Automated CI/CD testing

---

## 📊 Test Execution Times

| Test Type | Fast Mode | Human Mode | Human (High) |
|-----------|-----------|------------|--------------|
| **Single Integration Test** | 30-45s | 2-3min | 4-6min |
| **All Integration Tests (4)** | 2-3min | 8-12min | 15-20min |
| **Complete E2E Workflow** | 45-60s | 3-5min | 6-8min |
| **Full BookSlot Suite** | 3-5min | 12-18min | 25-35min |

---

## 🔧 Configuration Files

### pytest.ini
```ini
[pytest]
markers =
    bookslot: BookSlot project tests
    human_like: Tests with human behavior simulation
    e2e: End-to-end tests
    smoke: Smoke tests
    critical: Critical path tests
    regression: Regression test suite
```

### Configuration Override
```bash
# Override pytest.ini settings
pytest -m bookslot -v --override-ini="markers=bookslot: Custom marker"
```

---

## 📚 Related Documentation

- **Human Behavior Guide:** [Framework-Knowledge-Center/03-Features/BookSlot/BOOKSLOT_HUMAN_BEHAVIOR_COMPLETE.md](../Framework-Knowledge-Center/03-Features/BookSlot/BOOKSLOT_HUMAN_BEHAVIOR_COMPLETE.md)
- **Quick Reference:** [Framework-Knowledge-Center/00-Quick-Reference/QUICK_REFERENCE_DYNAMIC_CONFIG.md](../Framework-Knowledge-Center/00-Quick-Reference/QUICK_REFERENCE_DYNAMIC_CONFIG.md)
- **Pytest Markers:** [Framework-Knowledge-Center/00-Quick-Reference/PYTEST_MARKERS_COMPLETE_GUIDE.md](../Framework-Knowledge-Center/00-Quick-Reference/PYTEST_MARKERS_COMPLETE_GUIDE.md)

---

## 🆘 Troubleshooting

### Common Issues

**Issue 1: Tests Not Found**
```bash
# Verify marker registration
pytest --markers | grep bookslot

# Collect tests without running
pytest -m bookslot --collect-only
```

**Issue 2: Import Errors**
```bash
# Verify PYTHONPATH
python -c "import sys; print('\n'.join(sys.path))"

# Run from project root
cd C:\Users\LokendraSingh\Documents\GitHub\Automation
pytest -m bookslot -v
```

**Issue 3: Configuration Not Found**
```bash
# Verify config file exists
ls config/projects.yaml
ls config/human_behavior.yaml

# Test configuration loading
python -c "import yaml; print(yaml.safe_load(open('config/projects.yaml')))"
```

**Issue 4: Browser Launch Failed**
```bash
# Install Playwright browsers
playwright install chromium

# Or install all browsers
playwright install
```

---

## 💡 Pro Tips

1. **Use markers for efficient filtering:**
   ```bash
   pytest -m "bookslot and critical and not slow" -v
   ```

2. **Combine human behavior with headed mode for demos:**
   ```bash
   pytest -m bookslot --enable-human-behavior --headed --slowmo=300 -v
   ```

3. **Run integration tests in parallel (without human behavior):**
   ```bash
   pytest tests/integration/test_bookslot_to_patientintake.py -n 2 -v
   ```

4. **Use collection-only to verify test discovery:**
   ```bash
   pytest -m bookslot --collect-only
   ```

5. **Generate comprehensive reports:**
   ```bash
   pytest -m bookslot -v \
     --html=reports/bookslot.html \
     --junitxml=reports/junit.xml \
     --alluredir=allure-results
   ```

---

## 📞 Support

**Author:** Lokendra Singh  
**Email:** qa.lokendra@gmail.com  
**Website:** www.sqamentor.com

---

**Last Updated:** January 27, 2026
