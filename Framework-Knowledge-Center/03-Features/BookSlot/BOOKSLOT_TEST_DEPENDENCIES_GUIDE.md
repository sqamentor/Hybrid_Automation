# Bookslot Test Dependencies - Quick Reference

## Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    BOOKSLOT TEST FLOW                        │
└──────────────────────────────────────────────────────────────┘

Page 1: Basic Info ✓ (Entry Point - No Dependencies)
    │
    ├─► Fill First Name
    ├─► Fill Last Name  
    ├─► Fill Email
    ├─► Fill Phone
    └─► Click Next
        │
        ▼
Page 2: Event Type ✓ (Requires: Page 1)
    │
    ├─► Select "New Patient"
    └─► Click Next
        │
        ▼
Page 3: Scheduler ✓ (Requires: Pages 1-2)
    │
    ├─► Wait for scheduler load
    ├─► Select AM/PM time slot
    └─► Click Next
        │
        ▼
Page 4: Personal Info ✓ (Requires: Pages 1-3)
    │
    ├─► Fill Date of Birth
    ├─► Fill Address ("123 Main St")
    ├─► Fill City ("New York")
    ├─► Fill State ("NY")
    ├─► Fill Zip Code
    └─► Click Next
        │
        ▼
Page 5: Referral ✓ (Requires: Pages 1-4)
    │
    ├─► Select referral source (radio button)
    └─► Click Next
        │
        ▼
Page 6: Insurance ✓ (Requires: Pages 1-5)
    │
    ├─► Fill Member Name
    ├─► Fill ID Number
    ├─► Fill Group Number (optional)
    ├─► Fill Payer Name
    └─► Click Next
        │
        ▼
Page 7: Success ✓ (Complete Flow)
```

---

## Test File Dependencies

### test_bookslot_basicinfo_page1.py
**Page**: 1  
**Prerequisites**: None  
**Flow**: Direct navigation to `/basic-info`

```python
navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
page = navigator.navigate_to_basic_info()
# Test basic info page directly
```

---

### test_bookslot_eventtype_page2.py
**Page**: 2  
**Prerequisites**: Page 1 (Basic Info)  
**Flow**: Fill Basic Info → Arrive at Event Type

```python
navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
page = navigator.navigate_to_event_type()
# Automatically completed:
# ✓ Basic Info filled (Page 1)
# Now at: Event Type (Page 2)
```

**Prerequisite Steps Executed**:
1. Navigate to `/basic-info`
2. Fill First Name
3. Fill Last Name
4. Fill Email
5. Fill Phone
6. Click Next → Event Type page

---

### test_bookslot_scheduler_page3.py
**Page**: 3  
**Prerequisites**: Pages 1-2 (Basic Info → Event Type)  
**Flow**: Fill Basic Info → Select Event Type → Arrive at Scheduler

```python
navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
page = navigator.navigate_to_scheduler()
# Automatically completed:
# ✓ Basic Info filled (Page 1)
# ✓ Event Type selected (Page 2)
# Now at: Scheduler (Page 3)
```

**Prerequisite Steps Executed**:
1. Navigate to `/basic-info`
2. Fill First Name
3. Fill Last Name
4. Fill Email
5. Fill Phone
6. Click Next
7. Select "New Patient"
8. Click Next
9. Wait for scheduler → Scheduler page

---

### test_bookslot_personalinfo_page4.py
**Page**: 4  
**Prerequisites**: Pages 1-3 (Basic Info → Event Type → Scheduler)  
**Flow**: Complete 3-page flow → Arrive at Personal Info

```python
navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
page = navigator.navigate_to_personal_info()
# Automatically completed:
# ✓ Basic Info filled (Page 1)
# ✓ Event Type selected (Page 2)
# ✓ Time slot selected (Page 3)
# Now at: Personal Info (Page 4)
```

**Prerequisite Steps Executed**:
1. Navigate to `/basic-info`
2. Fill First Name
3. Fill Last Name
4. Fill Email
5. Fill Phone
6. Click Next
7. Select "New Patient"
8. Click Next
9. Wait for scheduler
10. Select AM time slot
11. Click Next → Personal Info page

---

### test_bookslot_referral_page5.py
**Page**: 5  
**Prerequisites**: Pages 1-4 (Basic Info → Event Type → Scheduler → Personal Info)  
**Flow**: Complete 4-page flow → Arrive at Referral

```python
navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
page = navigator.navigate_to_referral()
# Automatically completed:
# ✓ Basic Info filled (Page 1)
# ✓ Event Type selected (Page 2)
# ✓ Time slot selected (Page 3)
# ✓ Personal Info filled (Page 4)
# Now at: Referral (Page 5)
```

**Prerequisite Steps Executed**:
1. Navigate to `/basic-info`
2. Fill First Name
3. Fill Last Name
4. Fill Email
5. Fill Phone
6. Click Next
7. Select "New Patient"
8. Click Next
9. Wait for scheduler
10. Select AM time slot
11. Click Next
12. Fill Date of Birth
13. Fill Address ("123 Main St")
14. Fill City ("New York")
15. Fill State ("NY")
16. Fill Zip Code
17. Click Next → Referral page

---

### test_bookslot_insurance_page6.py
**Page**: 6  
**Prerequisites**: Pages 1-5 (Complete flow except insurance)  
**Flow**: Complete 5-page flow → Arrive at Insurance

```python
navigator = BookslotNavigator(smart_actions, fake_bookslot_data)
page = navigator.navigate_to_insurance()
# Automatically completed:
# ✓ Basic Info filled (Page 1)
# ✓ Event Type selected (Page 2)
# ✓ Time slot selected (Page 3)
# ✓ Personal Info filled (Page 4)
# ✓ Referral source selected (Page 5)
# Now at: Insurance (Page 6)
```

**Prerequisite Steps Executed**:
1. Navigate to `/basic-info`
2. Fill First Name
3. Fill Last Name
4. Fill Email
5. Fill Phone
6. Click Next
7. Select "New Patient"
8. Click Next
9. Wait for scheduler
10. Select AM time slot
11. Click Next
12. Fill Date of Birth
13. Fill Address ("123 Main St")
14. Fill City ("New York")
15. Fill State ("NY")
16. Fill Zip Code
17. Click Next
18. Select "Online search" referral
19. Click Next → Insurance page

---

## Run Commands

### Individual Page Tests
```bash
# Page 1 - No prerequisites
pytest tests/bookslot/test_bookslot_basicinfo_page1.py -v

# Page 2 - Requires Page 1
pytest tests/bookslot/test_bookslot_eventtype_page2.py -v

# Page 3 - Requires Pages 1-2
pytest tests/bookslot/test_bookslot_scheduler_page3.py -v

# Page 4 - Requires Pages 1-3
pytest tests/bookslot/test_bookslot_personalinfo_page4.py -v

# Page 5 - Requires Pages 1-4
pytest tests/bookslot/test_bookslot_referral_page5.py -v

# Page 6 - Requires Pages 1-5
pytest tests/bookslot/test_bookslot_insurance_page6.py -v
```

### All Page Tests
```bash
pytest tests/bookslot/test_bookslot_*page*.py -v
```

### Smoke Tests Only
```bash
pytest tests/bookslot/test_bookslot_*page*.py -m smoke -v
```

### Validation Tests Only
```bash
pytest tests/bookslot/test_bookslot_*page*.py -m validation -v
```

---

## Data Sources

All tests use the `fake_bookslot_data` fixture which provides:

```python
{
    'first_name': 'Generated Name',
    'last_name': 'Generated Surname',
    'email': 'generated@email.com',
    'phone': '5551234567',
    'zip': '12345',
    'dob': '01/01/1990',
    'MemberName': 'Generated Member',
    'idNumber': '123456789',
    'GroupNumber': 'GRP123',
    'PayerName': 'Generated Payer'
}
```

---

## Key Points

### ✅ All Tests Are Independent
- Each test file can be run individually
- Navigator helper handles all prerequisites automatically
- No manual setup required

### ✅ Uses Exact Working Logic
- All navigation methods use exact code from `test_bookslot_complete_flows.py`
- Proven to work perfectly in production
- Consistent across all test files

### ✅ Maintainable
- Update once in `navigation_helper.py`
- All 6 test files automatically inherit changes
- Single source of truth for flow logic

### ✅ Readable
- Clear dependency chain
- Self-documenting code
- Easy to understand which pages are visited

---

## Troubleshooting

### Test Fails at Page X
**Check**: All prerequisites (Pages 1 to X-1) are executing correctly

### Navigation Takes Long Time
**Reason**: Each navigation includes full prerequisite flow
**Solution**: This is expected - ensures test isolation and reliability

### Test Fails with "Element not found"
**Check**: 
1. Is the application URL correct?
2. Are field selectors matching the application?
3. Is the application in the correct state?

---

## Summary

**Every test now follows this pattern:**

1. Create navigator
2. Call appropriate navigate method
3. Navigator executes complete prerequisite flow
4. Test starts at the correct page with all setup done
5. Test focuses on testing its specific page only

**Result**: Reliable, maintainable, and easy-to-understand test suite!

---

Author: Lokendra Singh (qa.lokendra@gmail.com)  
Website: www.sqamentor.com  
Date: January 29, 2026
