"""
BOOKSLOT TEST SUITE
===================

This folder contains automated tests for the Bookslot application following
the Test Design Matrix principles.

## Test Structure

### Layer A: Page-Level Tests (`pages/`)
Independent tests for each page (P1-P7). Each test:
- Uses precondition fixture to reach target page
- Validates one page's components and behaviors
- Runs independently (no test-to-test dependencies)
- Supports parallel execution

**Pages:**
- P1: Basic Info (entry page, no precondition)
- P2: Event Type (precondition: P1 completed)
- P3: Scheduler (precondition: P1→P2 completed)
- P4: Personal Info (precondition: P1→P2→P3 completed)
- P5: Referral (precondition: P1→P2→P3→P4 completed)
- P6: Insurance (precondition: P1→P2→P3→P4→P5 completed)
- P7: Success (precondition: P1→P2→P3→P4→P5→P6 completed)

### Layer B: End-to-End Tests (`e2e/`)
Sequential flow tests covering complete user journeys (P1→P7).
- Small set of critical paths
- Happy path + key variants
- Run sequentially (marked with `@pytest.mark.ui_sequential`)

## Test Types by Marker

### Smoke Tests (`@pytest.mark.smoke`)
Fast confidence checks - run on every PR:
```bash
pytest tests/bookslot -m smoke
```

### Validation Tests (`@pytest.mark.validation`)
Component validation - full page coverage:
```bash
pytest tests/bookslot -m validation
```

### Regression Tests (`@pytest.mark.regression`)
Full regression suite - nightly runs:
```bash
pytest tests/bookslot -m regression
```

### E2E Tests (`@pytest.mark.e2e`)
Complete user journeys:
```bash
pytest tests/bookslot -m "e2e and critical" --dist no
```

## Running Tests

### Quick PR Check
```bash
# Smoke tests + 1 critical E2E
pytest tests/bookslot -m "smoke or (e2e and critical)" -n 4
```

### Full Page Validation
```bash
# All page validations (parallel)
pytest tests/bookslot/pages -m validation -n 8
```

### Nightly Regression
```bash
# All validations + E2E variants
pytest tests/bookslot -m "validation or regression" -n 8
pytest tests/bookslot -m "e2e" --dist no  # Sequential
```

### Specific Page Testing
```bash
# Test only P4 (Personal Info)
pytest tests/bookslot/pages/test_p4_personal_info.py -v
```

## Marker Reference

| Marker | Purpose | Execution |
|--------|---------|-----------|
| `bookslot` | Bookslot project | All tests |
| `smoke` | Fast confidence | Parallel |
| `validation` | Component validation | Parallel |
| `regression` | Full regression | Parallel |
| `e2e` | End-to-end flow | Sequential |
| `critical` | P0 tests | Any |
| `high` | P1 tests | Any |
| `medium` | P2 tests | Any |
| `ui_sequential` | Must run serial | Sequential |
| `parallel_safe` | Safe for parallel | Parallel |

## Component Validation Checklist

For every interactive component on a page, validate:

1. **Visible**: Element is rendered and visible
2. **Enabled/Clickable**: User can interact with it
3. **Input Behavior**: Accepts valid values
4. **Validation Behavior**: Rejects invalid/empty when required
5. **State Behavior**: Selected/unselected, checked/unchecked
6. **Navigation Effect**: Next/Back causes expected transition

## Precondition Fixtures

Use these fixtures to navigate to specific pages:

- `at_basic_info` - User at P1 (Basic Info)
- `at_event_type` - User at P2 (Event Type)
- `at_scheduler` - User at P3 (Scheduler)
- `at_personal_info` - User at P4 (Personal Info)
- `at_referral` - User at P5 (Referral)
- `at_insurance` - User at P6 (Insurance)
- `at_success` - User at P7 (Success)

## Helpers

- **BookslotNavigationHelper**: Navigate to any page via preconditions
- **BookslotDataHelper**: Generate test data (valid, invalid, variants)
- **BookslotValidationHelper**: Reusable validation methods

## Anti-Patterns to Avoid

❌ One giant test for all 7 pages
❌ Test-to-test dependencies (P2 test depends on P1 test passing)
❌ Repeating navigation logic in every test
❌ Too many E2E variants (causes flakiness)
❌ Assertions in page objects (keep in tests)

## Best Practices

✅ Independent tests (use fixtures for navigation)
✅ Small, focused E2E set
✅ Parallel execution for page tests
✅ Sequential execution for E2E tests
✅ Reuse helpers for navigation and validation
✅ Data-driven approach for variants
✅ Clear test names and markers

## File Organization

```
bookslot/
├── README.md                    # This file
├── conftest.py                  # Fixtures and markers
├── pages/                       # Layer A: Page-level tests
│   ├── test_p1_basic_info.py
│   ├── test_p2_event_type.py
│   ├── test_p3_scheduler.py
│   ├── test_p4_personal_info.py
│   ├── test_p5_referral.py
│   ├── test_p6_insurance.py
│   └── test_p7_success.py
├── e2e/                         # Layer B: E2E flow tests
│   ├── test_happy_path.py
│   ├── test_complete_journeys.py  # Comprehensive E2E scenarios
│   ├── test_am_slot_booking.py
│   ├── test_pm_slot_booking.py
│   └── test_variants.py
├── fixtures/                    # Additional fixtures module
│   └── __init__.py              # Boundary, collection, API, cleanup fixtures
├── data/                        # Test data management module
│   └── __init__.py              # Generators, validators, constants, preset data
├── helpers/                     # Helper modules
│   ├── navigation_helper.py     # (legacy - preserved)
│   ├── data_helper.py
│   └── validation_helper.py
└── examples/                    # Reference examples
    └── test_specific_pages_example.py
```

## Fixtures & Test Data

### Navigation Fixtures (in conftest.py)

Page precondition fixtures for isolated testing:

```python
def test_personal_info_fields(at_personal_info):
    """User is already at P4 - test only this page"""
    # at_personal_info has navigated through P1→P2→P3
    # Now test P4 components
```

Available fixtures:
- `at_basic_info` - Navigate to P1 (entry page)
- `at_event_type` - Navigate to P2 (via P1)
- `at_scheduler` - Navigate to P3 (via P1→P2)
- `at_personal_info` - Navigate to P4 (via P1→P2→P3)
- `at_referral` - Navigate to P5 (via P1→P2→P3→P4)
- `at_insurance` - Navigate to P6 (via P1→P2→P3→P4→P5)
- `at_success` - Navigate to P7 (via complete flow)

### Data Fixtures (in fixtures/__init__.py)

#### Valid Test Data
- `valid_basic_info` - Complete valid P1 data (name, email, phone)
- `valid_personal_info` - Complete valid P4 data (address, DOB, state, zip)
- `valid_insurance_info` - Complete valid P6 data (payer, member ID, group #)

#### Invalid Data (for negative testing)
- `invalid_basic_info_email` - Invalid email formats
- `invalid_basic_info_phone` - Invalid phone formats
- `invalid_personal_info_zip` - Invalid zip codes
- `invalid_insurance_member_id` - Invalid member ID formats

#### Boundary & Edge Cases
- `max_length_names` - 50-character first/last names
- `max_length_address` - 200-character addresses
- `edge_case_dates` - 18-year-old (minimum age)
- `special_char_names` - Names with hyphens, apostrophes, spaces

#### Collection Fixtures
- `all_us_states` - Dict of all 50 US states (code → name)
- `valid_zip_codes` - List of valid 5-digit zip codes
- `invalid_zip_codes` - List of invalid zip codes for negative testing
- `insurance_payers` - List of 10 major insurance providers
- `referral_sources` - Dict of 8 referral source types

#### Environment Fixtures
- `base_url` - Bookslot application base URL
- `workflow_id` - Unique workflow ID for test run
- `short_timeout` - 5 seconds (button clicks, visibility)
- `medium_timeout` - 15 seconds (form submissions, page transitions)
- `long_timeout` - 30 seconds (API calls, complex operations)

#### API Fixtures
- `api_base_url` - API endpoint base URL
- `api_headers` - Standard API headers with auth token

#### Cleanup Fixtures
- `cleanup_test_bookings` - Auto-cleanup test bookings after test run

### Test Data Module (data/__init__.py)

Centralized test data management with generators, validators, and constants.

#### Constants

```python
from tests.bookslot.data import MAX_NAME_LENGTH, MAX_ADDRESS_LENGTH, MIN_AGE

assert len(first_name) <= MAX_NAME_LENGTH  # 50 characters
assert age >= MIN_AGE  # 18 years old
```

Available constants:
- `MAX_NAME_LENGTH = 50` - Maximum characters for first/last name
- `MAX_ADDRESS_LENGTH = 200` - Maximum characters for address
- `MIN_AGE = 18` - Minimum age to book appointment
- `EMAIL_PATTERN` - Regex pattern for email validation
- `PHONE_PATTERN` - Regex pattern for phone validation
- `ZIP_CODE_PATTERN` - Regex pattern for zip code validation

#### Data Generators

Generate unique, valid test data dynamically:

```python
from tests.bookslot.data import (
    generate_test_email,
    generate_test_phone,
    generate_member_id,
    generate_date_of_birth
)

# Generate unique test email
email = generate_test_email()  # test_a1b2c3@example.com

# Generate unique test phone
phone = generate_test_phone()  # 555-0123

# Generate random member ID
member_id = generate_member_id()  # MBR1234567890

# Generate date of birth (18-80 years old)
dob = generate_date_of_birth()  # 1985-03-15
```

Available generators:
- `generate_test_email()` - Unique emails with timestamp
- `generate_test_phone()` - Valid 10-digit phone numbers
- `generate_member_id()` - 13-character member IDs (MBR + 10 digits)
- `generate_group_number()` - 8-character group numbers (GRP + 5 digits)
- `generate_date_of_birth(min_age=18, max_age=80)` - Valid DOB strings
- `generate_random_zip_code()` - Valid 5-digit zip codes

#### Data Validators

Validate data formats programmatically:

```python
from tests.bookslot.data import (
    validate_email_format,
    validate_phone_format,
    validate_zip_code_format,
    calculate_age_from_dob
)

# Validate email format
assert validate_email_format("test@example.com") is True
assert validate_email_format("invalid-email") is False

# Validate phone format
assert validate_phone_format("5551234567") is True  # 10 digits
assert validate_phone_format("555-123-4567") is True  # With dashes
assert validate_phone_format("123") is False  # Too short

# Validate zip code
assert validate_zip_code_format("12345") is True
assert validate_zip_code_format("ABCDE") is False

# Calculate age from date of birth
age = calculate_age_from_dob("1990-01-15")  # Returns current age
```

#### Collections (US States, Insurance Payers, Referral Sources)

```python
from tests.bookslot.data import US_STATES, INSURANCE_PAYERS, REFERRAL_SOURCES

# Get all US states
for state_code, state_name in US_STATES.items():
    print(f"{state_code}: {state_name}")  # NY: New York, CA: California, ...

# Get insurance payers list
payers = INSURANCE_PAYERS  # ['Blue Cross Blue Shield', 'UnitedHealthcare', ...]

# Get referral sources
sources = REFERRAL_SOURCES  # {'web': 'Internet Search', 'doctor': 'Doctor Referral', ...}
```

#### Sample Data (Names, Addresses, Cities)

```python
from tests.bookslot.data import FIRST_NAMES, LAST_NAMES, STREET_ADDRESSES, CITIES

# Pick random first/last name
import random
first_name = random.choice(FIRST_NAMES)  # John, Jane, Michael, ...
last_name = random.choice(LAST_NAMES)  # Smith, Johnson, Williams, ...

# Pick random address
address = random.choice(STREET_ADDRESSES)  # 123 Main St, 456 Oak Avenue, ...

# Pick random city by state
city = random.choice(CITIES["NY"])  # New York, Brooklyn, Queens, ...
```

#### Preset Data Sets (TestDataSets Class)

Pre-configured complete data sets for quick test setup:

```python
from tests.bookslot.data import TestDataSets

datasets = TestDataSets()

# Get complete valid basic info
basic_info = datasets.get_valid_basic_info()
# Returns: {'first_name': 'John', 'last_name': 'Smith', 'email': '...', 'phone': '...'}

# Get complete valid personal info
personal_info = datasets.get_valid_personal_info()
# Returns: {'address': '...', 'city': '...', 'state': 'NY', 'zip': '...', 'dob': '...'}

# Get complete valid insurance info
insurance_info = datasets.get_valid_insurance_info()
# Returns: {'payer': 'Blue Cross', 'member_id': '...', 'group_number': '...'}

# Get list of invalid emails for negative testing
invalid_emails = datasets.get_invalid_emails()
# Returns: ['invalid', 'test@', '@example.com', 'test..test@example.com', ...]

# Get list of invalid phone numbers
invalid_phones = datasets.get_invalid_phones()
# Returns: ['123', '12345', 'abcdefghij', '555-', ...]

# Get boundary dates (edge cases)
boundary_dates = datasets.get_boundary_dates()
# Returns: {'min_age': '2006-...', 'max_age': '1944-...', 'today': '...', 'future': '...'}
```

## Test Coverage

Total test count: **~115+ tests** covering all Bookslot functionality.

### Page-Level Tests (Layer A) - ~100 tests
- **P1 (Basic Info)**: 15 tests (5 smoke + 6 validation + 4 regression)
- **P2 (Event Type)**: 12 tests (4 smoke + 5 validation + 3 regression)
- **P3 (Scheduler)**: 18 tests (6 smoke + 8 validation + 4 regression)
- **P4 (Personal Info)**: 17 tests (3 smoke + 8 validation + 6 regression)
- **P5 (Referral)**: 14 tests (4 smoke + 6 validation + 4 regression)
- **P6 (Insurance)**: 16 tests (4 smoke + 7 validation + 5 regression)
- **P7 (Success)**: 10 tests (4 smoke + 4 validation + 2 regression)

### E2E Tests (Layer B) - ~15+ tests
- **Happy Path**: 2 tests (AM slot, PM slot)
- **Referral Variants**: 3-4 tests (web, doctor, insurance, other)
- **Insurance Variants**: 4 tests (major payers)
- **Edge Cases**: 3-4 tests (max length, special chars, boundary data)
- **Back Navigation**: 2 tests (data preservation across pages)

## Usage Examples

### Example 1: Test P4 with Boundary Data

```python
@pytest.mark.validation
@pytest.mark.p4_personal_info
def test_p4_max_length_names(at_personal_info, max_length_names):
    """Test P4 accepts maximum length names (50 characters)"""
    page_obj = PersonalInfoPage(at_personal_info.page)
    
    # Fill with max length names
    page_obj.fill_first_name(max_length_names['first_name'])
    page_obj.fill_last_name(max_length_names['last_name'])
    
    # Verify Accepted
    page_obj.click_next()
    assert page_obj.is_at_next_page()
```

### Example 2: Test with Generated Data

```python
from tests.bookslot.data import generate_test_email, generate_test_phone

@pytest.mark.smoke
@pytest.mark.p1_basic_info
def test_p1_unique_user_entry(at_basic_info):
    """Test P1 with dynamically generated unique data"""
    page_obj = BasicInfoPage(at_basic_info.page)
    
    # Generate unique test data
    email = generate_test_email()
    phone = generate_test_phone()
    
    # Fill form
    page_obj.fill_email(email)
    page_obj.fill_phone(phone)
    page_obj.click_next()
    
    assert page_obj.is_at_event_type_page()
```

### Example 3: Parametrized Test with Collection Fixtures

```python
@pytest.mark.validation
@pytest.mark.p4_personal_info
@pytest.mark.parametrize("state_code", US_STATES.keys())
def test_p4_all_us_states(at_personal_info, state_code):
    """Test P4 accepts all 50 US states"""
    page_obj = PersonalInfoPage(at_personal_info.page)
    
    page_obj.select_state(state_code)
    assert page_obj.get_selected_state() == state_code
```

### Example 4: E2E Test with Complete Data Sets

```python
from tests.bookslot.data import TestDataSets

@pytest.mark.e2e
@pytest.mark.critical
@pytest.mark.ui_sequential
def test_e2e_complete_booking():
    """Complete E2E booking with preset data"""
    datasets = TestDataSets()
    
    # Get complete data sets
    basic_info = datasets.get_valid_basic_info()
    personal_info = datasets.get_valid_personal_info()
    insurance_info = datasets.get_valid_insurance_info()
    
    # Execute complete flow P1→P7
    # ... test implementation ...
```

## Troubleshooting

### Common Issues

**Issue**: Tests fail with "fixture not found" error
```
E       fixture 'at_personal_info' not found
```
**Solution**: Verify conftest.py imports fixtures module:
```python
from tests.bookslot.fixtures import *
```

**Issue**: Data validation fails with "invalid email format"
**Solution**: Use data generators instead of hardcoded values:
```python
from tests.bookslot.data import generate_test_email
email = generate_test_email()  # Unique, valid email
```

**Issue**: E2E tests fail due to parallel execution
**Solution**: Mark E2E tests with `@pytest.mark.ui_sequential`:
```python
@pytest.mark.e2e
@pytest.mark.ui_sequential  # Forces sequential execution
def test_e2e_booking():
    ...
```

**Issue**: Page navigation timeout
**Solution**: Use appropriate timeout fixtures:
```python
def test_slow_page_load(at_scheduler, long_timeout):
    # long_timeout = 30 seconds for complex operations
    page_obj.wait_for_slots(timeout=long_timeout)
```

**Issue**: Test data conflicts (duplicate emails, phones)
**Solution**: Use unique data generators instead of fixtures:
```python
# ❌ BAD: Reuses same email across tests
def test_with_fixture(valid_basic_info):
    email = valid_basic_info['email']  # Same email every time

# ✅ GOOD: Generates unique email per test
def test_with_generator():
    from tests.bookslot.data import generate_test_email
    email = generate_test_email()  # Unique every time
```

### Debug Mode

Run tests with verbose output for debugging:

```bash
# Verbose output with live logs
pytest tests/bookslot/ -v -s --log-cli-level=DEBUG

# Run specific test with full output
pytest tests/bookslot/pages/test_p4_personal_info.py::test_p4_all_fields_required -vv -s

# Run with Playwright traces (for visual debugging)
pytest tests/bookslot/ -v --tracing=on
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Bookslot Tests

on: [push, pull_request]

jobs:
  smoke-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      
      - name: Run smoke tests
        run: pytest tests/bookslot/ -m smoke -n 4 --html=reports/smoke.html
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: smoke-test-report
          path: reports/

  e2e-tests:
    runs-on: ubuntu-latest
    needs: smoke-tests
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      
      - name: Run E2E tests (sequential)
        run: pytest tests/bookslot/e2e/ -m "e2e and critical" --dist no --html=reports/e2e.html
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-test-report
          path: reports/
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'playwright install chromium'
            }
        }
        
        stage('Smoke Tests') {
            steps {
                sh 'pytest tests/bookslot/ -m smoke -n 4 --junitxml=reports/smoke.xml'
            }
        }
        
        stage('Page Validation Tests') {
            when {
                branch 'develop'
            }
            steps {
                sh 'pytest tests/bookslot/pages/ -m validation -n 8 --junitxml=reports/validation.xml'
            }
        }
        
        stage('E2E Tests') {
            when {
                branch 'main'
            }
            steps {
                sh 'pytest tests/bookslot/e2e/ -m "e2e and critical" --dist no --junitxml=reports/e2e.xml'
            }
        }
    }
    
    post {
        always {
            junit 'reports/*.xml'
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
    }
}
```

### Azure DevOps Example

```yaml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'

- script: |
    pip install -r requirements.txt
    playwright install chromium
  displayName: 'Install dependencies'

- script: |
    pytest tests/bookslot/ -m smoke -n 4 --junitxml=reports/smoke.xml
  displayName: 'Run smoke tests'
  continueOnError: false

- script: |
    pytest tests/bookslot/e2e/ -m "e2e and critical" --dist no --junitxml=reports/e2e.xml
  displayName: 'Run E2E tests'
  condition: eq(variables['Build.SourceBranch'], 'refs/heads/main')

- task: PublishTestResults@2
  inputs:
    testResultsFormat: 'JUnit'
    testResultsFiles: 'reports/*.xml'
  condition: always()
```

## Performance Optimization

### Parallel Execution Best Practices

```bash
# ✅ GOOD: Page tests in parallel (independent)
pytest tests/bookslot/pages/ -n 8

# ✅ GOOD: Smoke tests in parallel (fast, independent)
pytest tests/bookslot/ -m smoke -n 4

# ❌ BAD: E2E tests in parallel (causes conflicts)
pytest tests/bookslot/e2e/ -n 4  # Don't do this!

# ✅ GOOD: E2E tests sequential
pytest tests/bookslot/e2e/ --dist no
```

### Test Execution Strategy

**PR/Commit Check (2-3 minutes)**:
```bash
pytest tests/bookslot/ -m "smoke or (e2e and critical)" -n 4
```

**Nightly Regression (15-20 minutes)**:
```bash
# Phase 1: Page validations (parallel)
pytest tests/bookslot/pages/ -m "smoke or validation" -n 8

# Phase 2: E2E tests (sequential)
pytest tests/bookslot/e2e/ -m e2e --dist no
```

**Full Suite (30-40 minutes)**:
```bash
# All page tests
pytest tests/bookslot/pages/ -n 8

# All E2E tests
pytest tests/bookslot/e2e/ --dist no
```

## Contact & Support

For questions or issues with this test suite:
- Review Test Design Matrix: `docs/BOOKSLOT_TEST_DESIGN_MATRIX.md`
- Check Framework docs: `Framework-Knowledge-Center/`
- Contact QA Lead

---

**Last Updated**: February 20, 2026
**Framework Version**: 2.x
**Test Design Matrix Version**: 1.0
