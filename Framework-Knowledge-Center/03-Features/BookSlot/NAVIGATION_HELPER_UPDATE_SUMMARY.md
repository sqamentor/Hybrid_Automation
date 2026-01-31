# Navigation Helper Update Summary

## Date: January 29, 2026

## Overview
Updated the `BookslotNavigator` helper class to use **EXACT logic** from `test_bookslot_complete_flows.py` for all navigation methods. This ensures that every test file follows the same proven, working flow.

---

## Changes Made

### Updated File
- **File**: `tests/bookslot/helpers/navigation_helper.py`
- **Purpose**: Centralized navigation logic for all bookslot test files

### Key Updates

#### 1. `navigate_to_event_type()`
**Dependency**: Basic Info (Page 1)

```python
# Now uses direct navigation logic instead of calling navigate_to_basic_info()
self.act.navigate(f"{self.base_url}/basic-info", "Basic Info")
self.act.type_text(self.page.get_by_role("textbox", name="First Name *"), self.data['first_name'], "First Name")
self.act.type_text(self.page.get_by_role("textbox", name="Last Name *"), self.data['last_name'], "Last Name")
self.act.type_text(self.page.get_by_role("textbox", name="Email *"), self.data['email'], "Email")
self.act.type_text(self.page.get_by_role("textbox", name="Phone *"), self.data['phone'], "Phone")
self.act.button_click(self.page.get_by_role("button", name="Next"), "Next")
```

#### 2. `navigate_to_scheduler()`
**Dependency**: Basic Info → Event Type (Pages 1-2)

```python
# Implements complete flow from basic info through event type
# Uses exact field selectors from test_bookslot_complete_flows.py
```

#### 3. `navigate_to_personal_info()`
**Dependency**: Basic Info → Event Type → Scheduler (Pages 1-3)

```python
# Adds scheduler time slot selection with exact logic
self.act.wait_for_scheduler(self.page)
self.page.locator(f"button:has-text('{time_slot}')").first.click()
```

#### 4. `navigate_to_referral()`
**Dependency**: Basic Info → Event Type → Scheduler → Personal Info (Pages 1-4)

```python
# Adds personal info form filling with exact field values
# Uses: "123 Main St", "New York", "NY" matching complete_flows
```

#### 5. `navigate_to_insurance()`
**Dependency**: Basic Info → Event Type → Scheduler → Personal Info → Referral (Pages 1-5)

```python
# Adds referral source selection with exact logic
self.page.get_by_role("radio", name=referral_source).click()
```

#### 6. `navigate_to_success()`
**Dependency**: Complete Flow (Pages 1-6)

```python
# Implements full booking flow through insurance submission
# Handles optional GroupNumber field properly
```

---

## Dependency Chain

### Visual Flow
```
Page 1: Basic Info
    ↓
Page 2: Event Type (requires Page 1)
    ↓
Page 3: Scheduler (requires Pages 1-2)
    ↓
Page 4: Personal Info (requires Pages 1-3)
    ↓
Page 5: Referral (requires Pages 1-4)
    ↓
Page 6: Insurance (requires Pages 1-5)
    ↓
Page 7: Success (complete flow)
```

### Test File Dependencies

| Test File | Prerequisites | Navigation Method |
|-----------|--------------|-------------------|
| `test_bookslot_basicinfo_page1.py` | None | Direct navigation |
| `test_bookslot_eventtype_page2.py` | Basic Info | `navigate_to_event_type()` |
| `test_bookslot_scheduler_page3.py` | Basic Info → Event Type | `navigate_to_scheduler()` |
| `test_bookslot_personalinfo_page4.py` | Basic Info → Event Type → Scheduler | `navigate_to_personal_info()` |
| `test_bookslot_referral_page5.py` | Basic Info → Event Type → Scheduler → Personal Info | `navigate_to_referral()` |
| `test_bookslot_insurance_page6.py` | Complete flow (Pages 1-5) | `navigate_to_insurance()` |

---

## Benefits

### 1. **Consistency**
All test files now use the exact same logic from `test_bookslot_complete_flows.py` which is proven to work perfectly.

### 2. **Maintainability**
When the booking flow changes, only the `navigation_helper.py` needs to be updated.

### 3. **Reliability**
Each navigation method implements the complete prerequisite flow, ensuring tests don't fail due to missing setup.

### 4. **Isolation**
Individual page tests can run independently while still respecting the required flow sequence.

---

## How Tests Work Now

### Example: Testing Personal Info Page (Page 4)

```python
def test_personal_info_page_loads(self, smart_actions, fake_bookslot_data):
    navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
    page = navigator.navigate_to_personal_info()
    
    # Page now automatically:
    # 1. Filled Basic Info (Page 1)
    # 2. Selected Event Type (Page 2)
    # 3. Selected Time Slot (Page 3)
    # 4. Now at Personal Info (Page 4) - ready to test
```

### Example: Testing Insurance Page (Page 6)

```python
def test_insurance_page_loads(self, smart_actions, fake_bookslot_data):
    navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
    page = navigator.navigate_to_insurance()
    
    # Page now automatically:
    # 1. Filled Basic Info (Page 1)
    # 2. Selected Event Type (Page 2)
    # 3. Selected Time Slot (Page 3)
    # 4. Filled Personal Info (Page 4)
    # 5. Selected Referral Source (Page 5)
    # 6. Now at Insurance (Page 6) - ready to test
```

---

## Testing the Updates

### Run Individual Page Tests
```bash
# Test Page 1 (no dependencies)
pytest tests/bookslot/test_bookslot_basicinfo_page1.py -v

# Test Page 2 (requires Page 1)
pytest tests/bookslot/test_bookslot_eventtype_page2.py -v

# Test Page 3 (requires Pages 1-2)
pytest tests/bookslot/test_bookslot_scheduler_page3.py -v

# Test Page 4 (requires Pages 1-3)
pytest tests/bookslot/test_bookslot_personalinfo_page4.py -v

# Test Page 5 (requires Pages 1-4)
pytest tests/bookslot/test_bookslot_referral_page5.py -v

# Test Page 6 (requires Pages 1-5)
pytest tests/bookslot/test_bookslot_insurance_page6.py -v
```

### Run All Page Tests
```bash
pytest tests/bookslot/test_bookslot_*page*.py -v
```

### Verify Complete Flow Still Works
```bash
pytest tests/bookslot/test_bookslot_complete_flows.py -v
```

---

## Technical Details

### Data Used
All navigation methods use `fake_bookslot_data` fixture which provides:
- `first_name`, `last_name`, `email`, `phone`
- `dob` (Date of Birth)
- `zip` (Zip Code)
- `MemberName`, `idNumber`, `GroupNumber`, `PayerName`

### Smart Actions Used
- `act.navigate()` - Navigate to URL
- `act.type_text()` - Type with human behavior simulation
- `act.button_click()` - Click with retries
- `act.wait_for_scheduler()` - Wait for scheduler to load

### Field Selectors (from complete_flows)
- First Name: `page.get_by_role("textbox", name="First Name *")`
- Last Name: `page.get_by_role("textbox", name="Last Name *")`
- Email: `page.get_by_role("textbox", name="Email *")`
- Phone: `page.get_by_role("textbox", name="Phone *")`
- Event Type: `page.get_by_role("button", name="New Patient")`
- Time Slot: `page.locator("button:has-text('AM')").first`
- Date of Birth: `page.get_by_role("textbox", name="Date of Birth *")`
- Address: `page.get_by_role("textbox", name="Address *")`
- City: `page.get_by_role("textbox", name="City *")`
- State: `page.get_by_role("textbox", name="State *")`
- Zip Code: `page.get_by_role("textbox", name="Zip Code *")`
- Referral: `page.get_by_role("radio", name="Online search")`
- Member Name: `page.get_by_role("textbox", name="Member Name *")`
- ID Number: `page.get_by_role("textbox", name="ID Number *")`
- Group Number: `page.get_by_role("textbox", name="Group Number")`
- Payer Name: `page.get_by_role("textbox", name="Payer Name *")`
- Next Button: `page.get_by_role("button", name="Next")`

---

## Verification Checklist

- [x] Updated `navigate_to_event_type()` with exact logic
- [x] Updated `navigate_to_scheduler()` with exact logic
- [x] Updated `navigate_to_personal_info()` with exact logic
- [x] Updated `navigate_to_referral()` with exact logic
- [x] Updated `navigate_to_insurance()` with exact logic
- [x] Updated `navigate_to_success()` with exact logic
- [x] All methods use field selectors from `test_bookslot_complete_flows.py`
- [x] All methods use data from `fake_bookslot_data` fixture
- [x] All methods use `smart_actions` for interactions
- [x] Dependency chain properly implemented
- [x] Documentation updated

---

## Summary

**What Changed**: Navigation helper now uses exact logic from working complete flow test

**Why**: Ensures all individual page tests follow the proven working pattern

**Impact**: All 6 page test files automatically inherit the correct prerequisite flow

**Result**: Tests are more reliable and maintainable with centralized navigation logic

---

## Author
Updated by: Lokendra Singh (qa.lokendra@gmail.com)
Website: www.sqamentor.com
Date: January 29, 2026
