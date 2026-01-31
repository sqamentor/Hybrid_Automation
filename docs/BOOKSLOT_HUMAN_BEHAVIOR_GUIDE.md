# BookSlot Human Behavior Integration Guide

Complete guide for using human behavior simulation in BookSlot automation testing.

**Author:** Lokendra Singh  
**Email:** qa.lokendra@gmail.com  
**Website:** www.sqamentor.com  
**Date:** 2024

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Page Objects with Human Behavior](#page-objects-with-human-behavior)
4. [Usage Examples](#usage-examples)
5. [Configuration](#configuration)
6. [Best Practices](#best-practices)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### What is Human Behavior Simulation?

Human behavior simulation adds realistic delays and interactions to automated tests, making them:
- **Undetectable**: Mimics natural human typing and clicking patterns
- **Realistic**: Includes thinking pauses, reading time, and navigation delays
- **Configurable**: Adjustable intensity levels (minimal, normal, high)
- **Optional**: Can be toggled on/off for different environments

### Why Use Human Behavior in BookSlot?

BookSlot is a patient appointment booking system where realistic user simulation is crucial for:
- **Anti-bot Detection**: Some healthcare systems monitor for automated behavior
- **Performance Testing**: Realistic user patterns for load testing
- **Demo Videos**: Professional-looking automation recordings
- **Visual Proof**: Show stakeholders realistic test execution
- **UX Validation**: Experience the application as real users do

### Timing Patterns in BookSlot

| Action Type | Fast Mode | Human Mode | Purpose |
|-------------|-----------|------------|---------|
| **Typing** | Instant | 0.08-0.25s per char | Natural typing speed |
| **Field Navigation** | Instant | 0.3-0.8s | Locating next field |
| **Form Review** | Instant | 1.0-2.0s | Reading/checking data |
| **Button Click** | Instant | 0.3-0.7s | Hesitation before action |
| **Page Transition** | Instant | 0.5-1.5s | Waiting for load |
| **Reading Content** | Instant | 0.5-2.0s | Understanding info |

---

## Quick Start

### 1. Enable Human Behavior Globally

Run all BookSlot tests with human behavior:

```bash
# Enable for all tests
pytest tests/integration/test_bookslot*.py --enable-human-behavior

# Set intensity level
pytest tests/integration/test_bookslot*.py --enable-human-behavior --human-behavior-intensity high

# Run specific test with human behavior
pytest tests/integration/test_bookslot_to_patientintake.py::test_book_appointment_and_verify_in_patientintake --enable-human-behavior
```

### 2. Enable Human Behavior in Code

```python
from pages.bookslot.bookslots_basicinfo import BookslotBasicInfoPage

def test_bookslot_form(page, multi_project_config):
    base_url = multi_project_config['bookslot']['ui_url']
    
    # Enable human behavior for this page
    basic_info = BookslotBasicInfoPage(
        page, 
        base_url, 
        enable_human_behavior=True
    )
    
    # All interactions will now include human-like delays
    basic_info.fill_field("First Name *", "John")  # Types character-by-character
    basic_info.fill_field("Email *", "john@example.com")  # Realistic timing
```

### 3. Use Pytest Markers

All BookSlot integration tests already have the `@pytest.mark.human_like` marker:

```python
@pytest.mark.human_like
def test_book_appointment(page, multi_project_config, human_behavior):
    # human_behavior fixture is automatically available
    # when --enable-human-behavior flag is used
    pass
```

---

## Page Objects with Human Behavior

All BookSlot page objects now support human behavior simulation:

### Basic Information Page

```python
from pages.bookslot.bookslots_basicinfo import BookslotBasicInfoPage

# Initialize with human behavior
basic_info = BookslotBasicInfoPage(page, base_url, enable_human_behavior=True)

# Fill fields with realistic typing
basic_info.fill_field("First Name *", "John")
# Result: Types "J" (0.15s) "o" (0.12s) "h" (0.18s) "n" (0.11s)

basic_info.fill_field("Email *", "john.doe@example.com")
# Result: Character-by-character with 0.08-0.25s delays

# Click with hesitation
basic_info.click_element('button[name="next"]')
# Result: 0.3-0.7s pause before clicking, then 0.2-0.5s after
```

**Human Behavior Features:**
- ✅ Character-by-character typing (0.08-0.25s per character)
- ✅ Pre-click hesitation (0.3-0.7s)
- ✅ Post-click pause (0.2-0.5s)
- ✅ Field navigation delay (0.3-0.8s)

### Personal Information Page

```python
from pages.bookslot.bookslots_personalInfo import BookslotPersonalInfoPage

personal_info = BookslotPersonalInfoPage(page, base_url, enable_human_behavior=True)

# Select gender with thinking pause
personal_info.select_gender("MALE")
# Result: 0.3-0.7s thinking → click dropdown → 0.3-0.7s considering → select option

# Fill date of birth with realistic typing
personal_info.fill_date_of_birth("01/01/2000")
# Result: Each character typed at 0.08-0.20s intervals

# Fill address with suggestion wait
personal_info.fill_address("20678")
# Result: 0.5-1.0s thinking → type characters → 0.8-1.5s wait for suggestions → select
```

**Human Behavior Features:**
- ✅ Thinking pauses before selections (0.3-0.7s)
- ✅ Date typing with realistic speed (0.08-0.20s per char)
- ✅ Address suggestion wait time (0.8-1.5s)
- ✅ Review pause after selection (0.3-0.6s)

### Event Information Page

```python
from pages.bookslot.bookslots_eventinfo import BookslotEventInfoPage

event_info = BookslotEventInfoPage(page, base_url, enable_human_behavior=True)

# Select appointment type with content review
event_info.select_new_patient_appointment()
# Result:
#   1.0-2.0s reading appointment options
#   0.5-1.2s reading specific details
#   0.7-1.5s considering choice
#   Click "Book Now"
#   0.3-0.7s pause after clicking
```

**Human Behavior Features:**
- ✅ Reading time for options (1.0-2.0s)
- ✅ Detail review time (0.5-1.2s)
- ✅ Decision consideration (0.7-1.5s)
- ✅ Post-action pause (0.3-0.7s)

### Web Scheduler Page

```python
from pages.bookslot.bookslots_webscheduler import BookslotWebSchedulerPage

scheduler = BookslotWebSchedulerPage(page, base_url, enable_human_behavior=True)

# Select time slot with calendar browsing behavior
scheduler.select_time_slot("06:00 AM")
# Result:
#   1.5-2.5s browsing calendar
#   1.0-2.0s reviewing available slots
#   0.7-1.2s deciding on time
#   Click time slot
#   0.4-0.8s confirming selection

scheduler.proceed_to_next()
# Result: 0.5-1.0s pause → click Next → 0.5-1.0s wait for transition
```

**Human Behavior Features:**
- ✅ Calendar browsing time (1.5-2.5s)
- ✅ Time slot review (1.0-2.0s)
- ✅ Decision time (0.7-1.2s)
- ✅ Confirmation pause (0.4-0.8s)

### Referral Page

```python
from pages.bookslot.bookslots_referral import BookslotReferralPage

referral = BookslotReferralPage(page, base_url, enable_human_behavior=True)

# Select referral source with reading time
referral.select_referral_source("Referred by physician")
# Result:
#   0.5-1.2s reading question
#   Click heading
#   0.8-1.5s considering answer
#   Click referral option
#   0.3-0.6s pause after selection

referral.proceed_to_next()
# Result: 0.4-0.9s pause → click Next → 0.5-1.0s wait
```

**Human Behavior Features:**
- ✅ Question reading time (0.5-1.2s)
- ✅ Answer consideration (0.8-1.5s)
- ✅ Selection confirmation (0.3-0.6s)

### Insurance Page

```python
from pages.bookslot.bookslots_insurance import BookslotInsurancePage

insurance = BookslotInsurancePage(page, base_url, enable_human_behavior=True)

# Fill insurance form with realistic typing and pauses
insurance.fill_insurance_info(
    member_name="John Doe",
    id_number="123456",
    group_number="123456",
    company_name="Aetna"
)
# Result for each field:
#   0.3-0.8s locating field
#   Click field
#   Character-by-character typing (0.08-0.25s per char)
#   0.4-1.0s thinking before next field
#   Final: 1.0-2.0s reviewing entire form

insurance.submit_to_clinic()
# Result: 0.5-1.2s final review → click Send → 0.8-1.5s wait for submission
```

**Human Behavior Features:**
- ✅ Field location time (0.3-0.8s)
- ✅ Realistic typing (0.08-0.25s per character)
- ✅ Inter-field thinking (0.4-1.0s)
- ✅ Form review before submission (1.0-2.0s)
- ✅ Submission confirmation wait (0.8-1.5s)

### Success Page

```python
from pages.bookslot.bookslots_success import BookslotSuccessPage

success = BookslotSuccessPage(page, base_url, enable_human_behavior=True)

# Verify success with realistic observation time
success.verify_redirect_message()
# Result:
#   1.0-2.0s reading confirmation message
#   Verify redirect message visible
#   0.5-1.0s watching countdown

success.verify_confirmation_displayed()
# Result: Verify URL contains "/success"
```

**Human Behavior Features:**
- ✅ Confirmation reading time (1.0-2.0s)
- ✅ Countdown observation (0.5-1.0s)

---

## Usage Examples

### Example 1: Complete E2E Workflow with Human Behavior

```python
import pytest
from playwright.sync_api import Page

@pytest.mark.bookslot
@pytest.mark.human_like
def test_complete_booking_with_human_behavior(page: Page, multi_project_config, human_behavior):
    """Complete appointment booking with human-like interactions"""
    
    base_url = multi_project_config['bookslot']['ui_url']
    enable_human = human_behavior is not None
    
    # Step 1: Basic Information
    from pages.bookslot.bookslots_basicinfo import BookslotBasicInfoPage
    basic_info = BookslotBasicInfoPage(page, base_url, enable_human)
    basic_info.navigate()
    basic_info.fill_field("First Name *", "John")
    basic_info.fill_field("Last Name *", "Doe")
    basic_info.fill_field("Email *", "john.doe@example.com")
    
    # Step 2: Personal Information
    from pages.bookslot.bookslots_personalInfo import BookslotPersonalInfoPage
    personal_info = BookslotPersonalInfoPage(page, base_url, enable_human)
    personal_info.select_gender("MALE")
    personal_info.fill_date_of_birth("01/01/2000")
    
    # Step 3: Insurance
    from pages.bookslot.bookslots_insurance import BookslotInsurancePage
    insurance = BookslotInsurancePage(page, base_url, enable_human)
    insurance.fill_insurance_info(
        member_name="John Doe",
        id_number="123456",
        group_number="123456",
        company_name="Aetna"
    )
    insurance.submit_to_clinic()
    
    # Step 4: Verify Success
    from pages.bookslot.bookslots_success import BookslotSuccessPage
    success = BookslotSuccessPage(page, base_url, enable_human)
    success.verify_redirect_message()
```

**Execution Times:**
- **Fast Mode** (no human behavior): ~8-12 seconds
- **Human Mode** (with human behavior): ~45-65 seconds
- **High Intensity Mode**: ~90-120 seconds

### Example 2: Mixed Mode (Selective Human Behavior)

```python
@pytest.mark.bookslot
def test_mixed_mode_booking(page: Page, multi_project_config):
    """Use human behavior only for specific pages"""
    
    base_url = multi_project_config['bookslot']['ui_url']
    
    # Fast mode for basic info (CI/CD speed)
    basic_info = BookslotBasicInfoPage(page, base_url, enable_human_behavior=False)
    basic_info.fill_field("First Name *", "Jane")
    
    # Human mode for personal info (realistic for demo)
    personal_info = BookslotPersonalInfoPage(page, base_url, enable_human_behavior=True)
    personal_info.select_gender("FEMALE")
    
    # Fast mode for insurance (speed up completion)
    insurance = BookslotInsurancePage(page, base_url, enable_human_behavior=False)
    insurance.fill_insurance_info()
```

**Use Case:** Fast CI/CD tests with selective human behavior for demo recordings

### Example 3: Environment-Based Human Behavior

```python
@pytest.mark.bookslot
def test_environment_aware_booking(page: Page, multi_project_config, request):
    """Enable human behavior based on environment"""
    
    base_url = multi_project_config['bookslot']['ui_url']
    
    # Get environment from pytest config
    env = request.config.getoption("--env", default="staging")
    
    # Enable human behavior only in production
    enable_human = (env == "production")
    
    basic_info = BookslotBasicInfoPage(page, base_url, enable_human)
    basic_info.fill_field("Email *", "test@example.com")
```

**Use Case:** Production tests need human behavior, staging tests run fast

### Example 4: Human Behavior with Data-Driven Tests

```python
import pytest

@pytest.mark.bookslot
@pytest.mark.human_like
@pytest.mark.parametrize("patient_data", [
    {"first_name": "John", "last_name": "Doe", "gender": "MALE"},
    {"first_name": "Jane", "last_name": "Smith", "gender": "FEMALE"},
    {"first_name": "Alex", "last_name": "Johnson", "gender": "OTHER"},
])
def test_multiple_patients_with_human_behavior(page, multi_project_config, human_behavior, patient_data):
    """Test multiple patient bookings with realistic behavior"""
    
    base_url = multi_project_config['bookslot']['ui_url']
    enable_human = human_behavior is not None
    
    # Each iteration will have realistic human delays
    basic_info = BookslotBasicInfoPage(page, base_url, enable_human)
    basic_info.fill_field("First Name *", patient_data["first_name"])
    basic_info.fill_field("Last Name *", patient_data["last_name"])
    
    personal_info = BookslotPersonalInfoPage(page, base_url, enable_human)
    personal_info.select_gender(patient_data["gender"])
```

---

## Configuration

### Global Configuration (pytest.ini)

```ini
[pytest]
markers =
    human_like: Tests that benefit from human behavior simulation
    bookslot: BookSlot project tests

# Default human behavior intensity
human_behavior_intensity = normal
```

### YAML Configuration (config/human_behavior.yaml)

```yaml
# Typing speed configuration
typing:
  min_delay: 0.08  # Minimum delay between characters (seconds)
  max_delay: 0.25  # Maximum delay between characters (seconds)
  
# Click delays
clicking:
  pre_click_min: 0.3   # Minimum pause before clicking
  pre_click_max: 0.7   # Maximum pause before clicking
  post_click_min: 0.2  # Minimum pause after clicking
  post_click_max: 0.5  # Maximum pause after clicking

# Reading/thinking delays
thinking:
  short_min: 0.3    # Quick thinking (field navigation)
  short_max: 0.8
  medium_min: 0.8   # Medium thinking (reviewing options)
  medium_max: 1.5
  long_min: 1.0     # Long thinking (complex decisions)
  long_max: 2.5

# Environment overrides
environments:
  production:
    typing:
      min_delay: 0.10
      max_delay: 0.30
    intensity: high
    
  staging:
    intensity: normal
    
  dev:
    intensity: minimal
```

### Intensity Levels

| Intensity | Typing Speed | Pauses | Use Case |
|-----------|-------------|--------|----------|
| **minimal** | 0.05-0.15s | 0.2-0.5s | Quick validation |
| **normal** | 0.08-0.25s | 0.3-2.0s | Standard testing |
| **high** | 0.10-0.35s | 0.5-3.0s | Production/Demo |

---

## Best Practices

### ✅ DO: Use Human Behavior When

1. **Production Testing**
   ```python
   if env == "production":
       enable_human_behavior = True
   ```

2. **Demo Recordings**
   ```bash
   pytest --enable-human-behavior --headed --slowmo=50
   ```

3. **Anti-Bot Validation**
   ```python
   @pytest.mark.anti_bot
   @pytest.mark.human_like
   def test_bot_detection_evasion():
       pass
   ```

4. **UX Testing**
   ```python
   # Experience the application as users do
   enable_human_behavior = True
   ```

### ❌ DON'T: Avoid Human Behavior When

1. **CI/CD Pipelines** (unless specifically testing bot detection)
   ```bash
   # Fast mode for CI/CD
   pytest tests/ --disable-human-behavior
   ```

2. **Smoke Tests**
   ```python
   @pytest.mark.smoke
   def test_quick_validation():
       # Fast mode preferred
       enable_human_behavior = False
   ```

3. **Unit Tests**
   ```python
   # Human behavior not needed for unit tests
   def test_validation_logic():
       pass
   ```

### Performance Guidelines

| Test Type | Recommended Mode | Execution Time | Human Behavior |
|-----------|------------------|----------------|----------------|
| **Unit** | Fast | Seconds | ❌ No |
| **Integration** | Fast | Minutes | ❌ No |
| **E2E (CI/CD)** | Fast | 5-10 min | ❌ No |
| **E2E (Production)** | Human | 30-60 min | ✅ Yes |
| **Demo** | Human (High) | 60-120 min | ✅ Yes |
| **Load Testing** | Human | Variable | ✅ Yes |

### Code Organization

```python
# ✅ GOOD: Enable human behavior via parameter
def test_booking(page, multi_project_config, human_behavior):
    enable_human = human_behavior is not None
    page_obj = BookslotPage(page, url, enable_human)

# ✅ GOOD: Environment-based decision
def test_booking(page, multi_project_config, request):
    env = request.config.getoption("--env")
    enable_human = (env == "production")
    
# ❌ BAD: Hardcoded human behavior
def test_booking(page, multi_project_config):
    page_obj = BookslotPage(page, url, enable_human_behavior=True)  # Always slow!
```

---

## Performance Considerations

### Timing Analysis

**Complete BookSlot Workflow (6 pages):**

```
Fast Mode:
├─ Basic Info:      1-2s
├─ Event Info:      0.5-1s
├─ Web Scheduler:   1-2s
├─ Personal Info:   1-2s
├─ Referral:        0.5-1s
└─ Insurance:       1-2s
Total: ~8-12 seconds

Human Mode (Normal):
├─ Basic Info:      8-12s  (typing ~20 characters × 0.15s)
├─ Event Info:      3-5s   (reading + selecting)
├─ Web Scheduler:   5-8s   (browsing calendar)
├─ Personal Info:   8-12s  (typing + selecting)
├─ Referral:        2-4s   (reading + selecting)
└─ Insurance:       15-20s (typing ~30 characters)
Total: ~45-65 seconds

Human Mode (High):
├─ Basic Info:      12-18s
├─ Event Info:      5-8s
├─ Web Scheduler:   8-12s
├─ Personal Info:   12-18s
├─ Referral:        3-6s
└─ Insurance:       20-30s
Total: ~90-120 seconds
```

### Optimization Strategies

1. **Parallel Execution**
   ```bash
   # Run multiple tests in parallel (fast mode)
   pytest tests/ -n 4 --disable-human-behavior
   ```

2. **Selective Human Behavior**
   ```python
   # Only critical path with human behavior
   if step in ["insurance", "payment"]:
       enable_human_behavior = True
   ```

3. **Conditional Delays**
   ```python
   # Shorter delays for known-good fields
   if field_validated_before:
       delay_multiplier = 0.5
   ```

---

## Troubleshooting

### Issue 1: Tests Too Slow

**Symptoms:**
- Tests taking 2-3x longer than expected
- Human behavior enabled in CI/CD

**Solutions:**

```bash
# Check if human behavior is accidentally enabled
pytest tests/ --disable-human-behavior

# Verify intensity level
pytest tests/ --human-behavior-intensity minimal

# Check configuration
cat config/human_behavior.yaml
```

### Issue 2: Bot Detection Still Triggered

**Symptoms:**
- CAPTCHAs appearing
- "Suspicious activity" warnings

**Solutions:**

```yaml
# Increase delays in config/human_behavior.yaml
typing:
  min_delay: 0.15  # Slower typing
  max_delay: 0.35

thinking:
  long_min: 2.0    # More thinking time
  long_max: 4.0
```

```bash
# Use high intensity mode
pytest tests/ --enable-human-behavior --human-behavior-intensity high
```

### Issue 3: Inconsistent Timing

**Symptoms:**
- Sometimes fast, sometimes slow
- Human behavior not working

**Solutions:**

```python
# Check if human_behavior fixture is being used
def test_booking(page, multi_project_config, human_behavior):
    if human_behavior is None:
        print("Human behavior NOT enabled")
    else:
        print("Human behavior ENABLED")

# Verify page object initialization
page_obj = BookslotPage(page, url, enable_human_behavior=True)
print(f"Human enabled: {page_obj._human_enabled}")
```

### Issue 4: Timeouts with Human Behavior

**Symptoms:**
- Playwright timeout errors
- Element not found

**Solutions:**

```python
# Increase Playwright timeout
page.set_default_timeout(60000)  # 60 seconds

# Or in pytest.ini
[pytest]
timeout = 120  # seconds
```

---

## Additional Resources

### Related Documentation

- **[HUMAN_BEHAVIOR_INTEGRATION_GUIDE.md](HUMAN_BEHAVIOR_INTEGRATION_GUIDE.md)** - General framework guide
- **[HUMAN_BEHAVIOR_USAGE_GUIDE.md](HUMAN_BEHAVIOR_USAGE_GUIDE.md)** - Usage patterns and examples
- **[QUICK_REFERENCE_DYNAMIC_CONFIG.md](../QUICK_REFERENCE_DYNAMIC_CONFIG.md)** - Configuration reference

### Example Files

- **[bookslot_human_behavior_example.py](../examples/bookslot_human_behavior_example.py)** - Complete working examples
- **[verify_complete.py](../verify_complete.py)** - Validation script

### Configuration Files

- **[config/human_behavior.yaml](../config/human_behavior.yaml)** - Timing configuration
- **[pytest.ini](../pytest.ini)** - Pytest settings
- **[conftest.py](../conftest.py)** - Fixtures and hooks

---

## Support

For questions or issues:

**Author:** Lokendra Singh  
**Email:** qa.lokendra@gmail.com  
**Website:** www.sqamentor.com

---

*Last Updated: 2024*
*Version: 1.0*
