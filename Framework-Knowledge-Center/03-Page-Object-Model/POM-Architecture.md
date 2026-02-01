# Page Object Model (POM) - Architecture & Implementation Guide

## 1. Purpose
- **Why this component exists**: Provides a clean, maintainable abstraction layer between test code and UI elements, eliminating brittle tests
- **What problem it solves**: Reduces test maintenance, improves readability, enables reusability, centralizes locator management

## 2. Scope

### What is Included
- Page class definitions for all UI pages
- Locator definitions as properties
- Action methods (click, fill, select, etc.)
- Navigation methods
- State validation methods (returns boolean)
- Method chaining support (fluent API)

### What is Explicitly Excluded
- Test assertions (belong in test files)
- Test fixtures (belong in conftest.py)
- Test data generation (use utils/fake_data_generator.py)
- Business logic (keep pages pure UI interactions)
- API calls (use api_client)
- Database queries (use db_validator)

## 3. Current Implementation

### Summary
The POM architecture uses a class-based approach where each web page has a corresponding Python class. Locators are defined as `@property` methods, and interactions are exposed as action methods that return `self` for method chaining.

### Key Classes, Files, and Modules

**Base Class:** `framework/ui/base_page.py` → `BasePage`

**Project Pages:**
- **BookSlot:** `pages/bookslot/`
  - `bookslots_basicinfo_page1.py` → `BookslotBasicInfoPage`
  - `bookslots_eventinfo_page2.py` → `BookslotEventInfoPage`
  - `bookslots_webscheduler_page3.py` → `BookslotWebSchedulerPage`
  - `bookslots_personalInfo_page4.py` → `BookslotPersonalInfoPage`
  - `bookslots_referral_page5.py` → `BookslotReferralPage`
  - `bookslots_insurance_page6.py` → `BookslotInsurancePage`
  - `bookslots_success_page7.py` → `BookslotSuccessPage`

- **CallCenter:** `pages/callcenter/`
  - `appointment_management_page.py` → `CallCenterAppointmentManagementPage`
  - `dashboard_verification_page.py` → `CallCenterDashboardVerificationPage`

- **PatientIntake:** `pages/patientintake/`
  - `appointment_list_page.py` → `PatientIntakeAppointmentListPage`
  - `patient_verification_page.py` → `PatientIntakeVerificationPage`

## 4. File & Code Mapping

### Base Page: `framework/ui/base_page.py`

**Responsibilities:**
- Define abstract interface for all page objects
- Provide human behavior integration
- Common methods all pages must implement

**Key Methods:**
```python
@abstractmethod def navigate(self, url: str)
@abstractmethod def click(self, locator: str)
@abstractmethod def fill(self, locator: str, text: str)
@abstractmethod def get_text(self, locator: str) -> str
@abstractmethod def is_visible(self, locator: str) -> bool
```

### Example Page Object: `bookslots_basicinfo_page1.py`

**Structure:**
```python
class BookslotBasicInfoPage:
    """Page Object for BookSlot Basic Info page"""
    
    # Constructor
    def __init__(self, page: Page):
        self.page = page
    
    # Locators (as properties)
    @property
    def first_name_field(self):
        return self.page.locator("#firstName")
    
    @property
    def email_field(self):
        return self.page.locator("#email")
    
    @property
    def next_button(self):
        return self.page.locator("#nextBtn")
    
    # Actions (return self for chaining)
    def fill_first_name(self, name: str):
        """Fill first name field"""
        self.first_name_field.fill(name)
        return self
    
    def fill_email(self, email: str):
        """Fill email field"""
        self.email_field.fill(email)
        return self
    
    def click_next(self):
        """Click next button"""
        self.next_button.click()
        return self
    
    # Validation (return boolean)
    def is_error_displayed(self) -> bool:
        """Check if error message is visible"""
        return self.page.locator(".error-message").is_visible()
```

## 5. Execution Flow

### Step-by-Step Runtime Behavior

#### Example: Booking Flow Test

```python
def test_booking_flow(page: Page, fake_bookslot_data):
    # 1. Import page objects
    from pages.bookslot.bookslots_basicinfo_page1 import BookslotBasicInfoPage
    from pages.bookslot.bookslots_eventinfo_page2 import BookslotEventInfoPage
    
    # 2. Navigate to application
    page.goto("https://bookslot.com")
    
    # 3. Instantiate page object
    basic_info_page = BookslotBasicInfoPage(page)
    
    # 4. Use page object methods (with chaining)
    basic_info_page.fill_first_name(fake_bookslot_data['first_name'])\
                   .fill_email(fake_bookslot_data['email'])\
                   .click_next()
    
    # 5. Move to next page
    event_info_page = BookslotEventInfoPage(page)
    
    # 6. Continue workflow
    event_info_page.select_event_type("Consultation")\
                   .click_continue()
    
    # 7. Assert final state (in test, not page object)
    assert page.locator(".success-page").is_visible()
```

**Flow Diagram:**
```
Test File
    │
    ├─> Import Page Objects
    │
    ├─> Navigate to URL
    │
    ├─> Instantiate Page Object (passing page)
    │       │
    │       └─> Page Object receives Playwright Page
    │
    ├─> Call Action Methods
    │       │
    │       ├─> Method accesses locator via @property
    │       ├─> Performs action (fill, click, etc.)
    │       └─> Returns self (for chaining)
    │
    ├─> Call Validation Methods
    │       │
    │       ├─> Method checks element state
    │       └─> Returns boolean
    │
    └─> Assert Results (in test)
```

### Sync vs Async Behavior
- **Synchronous only** - All page object methods are synchronous
- Uses Playwright's sync_api (not async_api)
- No async/await in page objects

## 6. Inputs & Outputs

### Page Object Constructor

```python
def __init__(self, page: Page):
    """
    Initialize page object
    
    Args:
        page: Playwright Page object (from page fixture)
    """
    self.page = page
```

### Action Methods

**Pattern:**
```python
def action_name(self, param: type) -> 'PageClass':
    """
    Perform action
    
    Args:
        param: Parameter description
    
    Returns:
        self: For method chaining
    """
    # Perform action using locator
    self.locator_property.action(param)
    return self  # Enable chaining
```

**Example:**
```python
def fill_first_name(self, name: str) -> 'BookslotBasicInfoPage':
    """
    Fill first name field
    
    Args:
        name: First name to enter
    
    Returns:
        self: For method chaining
    """
    self.first_name_field.fill(name)
    return self
```

### Validation Methods

**Pattern:**
```python
def is_state_condition(self) -> bool:
    """
    Check if condition is met
    
    Returns:
        bool: True if condition met, False otherwise
    """
    return self.element_locator.is_visible()
```

**Example:**
```python
def is_success_message_displayed(self) -> bool:
    """
    Check if success message is visible
    
    Returns:
        bool: True if visible, False otherwise
    """
    return self.page.locator(".success-message").is_visible()
```

### Config Dependencies
- **None directly** - Page objects are independent of config
- May use human behavior if initialized via BasePage

## 7. Design Decisions

### Why This Approach Was Chosen

#### 1. **Properties for Locators vs Instance Variables**

**Decision:** Use `@property` decorators

✅ **CHOSEN:**
```python
@property
def first_name_field(self):
    return self.page.locator("#firstName")
```

❌ **NOT CHOSEN:**
```python
def __init__(self, page):
    self.first_name_field = page.locator("#firstName")  # Static
```

**Why:**
- Dynamic evaluation (handles SPA re-renders)
- Fresh locator on each access
- Prevents stale element references
- Supports self-healing locators

#### 2. **Method Chaining (Fluent API) vs Void Methods**

**Decision:** Return `self` from action methods

✅ **CHOSEN:**
```python
def fill_name(self, name: str):
    self.name_field.fill(name)
    return self  # Chaining

# Usage
page.fill_name("John").fill_email("john@test.com")
```

❌ **NOT CHOSEN:**
```python
def fill_name(self, name: str):
    self.name_field.fill(name)
    # No return

# Usage (verbose)
page.fill_name("John")
page.fill_email("john@test.com")
```

**Why:**
- More readable test code
- Encourages logical action grouping
- Industry standard (Selenium PageFactory pattern)

#### 3. **Validation Returns Boolean vs Assertions**

**Decision:** Validation methods return boolean, tests assert

✅ **CHOSEN:**
```python
# Page Object
def is_error_displayed(self) -> bool:
    return self.error_message.is_visible()

# Test
assert page.is_error_displayed()  # Assert in test
```

❌ **NOT CHOSEN:**
```python
# Page Object
def verify_error_displayed(self):
    assert self.error_message.is_visible()  # Assert in page

# Test
page.verify_error_displayed()  # No explicit assert
```

**Why:**
- Separation of concerns (pages = actions, tests = assertions)
- Reusability (boolean can be used in if/while)
- Flexibility (can negate, combine conditions)
- Testability (easier to mock/test)

#### 4. **Class-Based vs Function-Based**

**Decision:** Use classes for page objects

✅ **CHOSEN:**
```python
class BookslotBasicInfoPage:
    def __init__(self, page):
        self.page = page
```

❌ **NOT CHOSEN:**
```python
def fill_basic_info(page, name, email):
    page.locator("#name").fill(name)
    page.locator("#email").fill(email)
```

**Why:**
- Clear organization (all page methods in one class)
- State management (self.page)
- Inheritance support (BasePage)
- OOP principles (encapsulation)

### Trade-offs

| Pro | Con |
|-----|-----|
| ✅ Maintainable (locators centralized) | ❌ Initial setup overhead |
| ✅ Readable (descriptive method names) | ❌ More files to manage |
| ✅ Reusable (methods used across tests) | ❌ Learning curve for new developers |
| ✅ Testable (page objects can be unit tested) | ❌ Abstraction layer (one more concept) |
| ✅ DRY principle (no duplicate locators) | ❌ Can become bloated if not organized |

## 8. Rules & Constraints

### Hard Rules Enforced by Framework

#### ✅ MUST DO:

1. **All locators MUST be @property methods**
   ```python
   @property
   def element_locator(self):
       return self.page.locator("#element")  # ✅
   ```

2. **Action methods MUST return `self`**
   ```python
   def click_button(self):
       self.button.click()
       return self  # ✅ MANDATORY
   ```

3. **Page objects MUST be in `pages/<project>/` directory**
   ```
   pages/
   ├── bookslot/
   │   └── bookslots_basicinfo_page1.py  # ✅
   ├── callcenter/
   │   └── appointment_management_page.py  # ✅
   ```

4. **Page object files MUST end with `_page.py`**
   ```python
   bookslots_basicinfo_page1.py  # ✅
   basic_info.py  # ❌ WRONG
   ```

5. **Class names MUST end with `Page`**
   ```python
   class BookslotBasicInfoPage:  # ✅
   class BookslotBasicInfo:  # ❌ WRONG
   ```

#### ❌ MUST NOT DO:

1. **NO pytest imports in page objects**
   ```python
   import pytest  # ❌ FORBIDDEN
   ```

2. **NO assertions in page objects**
   ```python
   assert element.is_visible()  # ❌ FORBIDDEN
   ```

3. **NO test data generation in page objects**
   ```python
   def fill_form(self):
       name = fake.name()  # ❌ FORBIDDEN
       self.name_field.fill(name)
   ```

4. **NO API calls in page objects**
   ```python
   def submit_form(self):
       response = requests.post(...)  # ❌ FORBIDDEN
   ```

5. **NO database queries in page objects**
   ```python
   def verify_data(self):
       result = db.query(...)  # ❌ FORBIDDEN
   ```

### Assumptions Developers Must Not Violate

1. **Page object instantiation receives valid Playwright Page**
   - Page must be already initialized
   - Page must be on correct URL (or navigated)

2. **Locators are valid CSS/XPath selectors**
   - Page object doesn't validate selector syntax
   - Runtime error if invalid

3. **Single page per class**
   - One class per web page
   - Don't combine multiple pages in one class

4. **Synchronous execution**
   - No async methods in page objects
   - Use sync_api only

## 9. Error Handling & Edge Cases

### Known Failure Scenarios

#### 1. **Element Not Found**

```python
# Scenario: Locator doesn't match any element
page.first_name_field.fill("John")  # → TimeoutError

# Behavior:
# - Playwright waits up to default timeout (30s)
# - Raises TimeoutError if not found
# - Test fails
```

**Mitigation:**
```python
def is_first_name_field_visible(self) -> bool:
    """Check if field exists before interacting"""
    try:
        return self.first_name_field.is_visible(timeout=5000)
    except:
        return False
```

#### 2. **Stale Page Reference**

```python
# Scenario: Page navigates away during action
page = BookslotBasicInfoPage(page)
page.click_next()
# → Page changed
page.fill_first_name("John")  # ❌ Wrong page now

# Behavior:
# - May interact with wrong page
# - Unexpected results
```

**Mitigation:**
- Create new page object after navigation
- Don't reuse page objects across page transitions

#### 3. **Dynamic Elements (SPA)**

```python
# Scenario: Element re-rendered by React/Vue
@property
def dynamic_element(self):
    # ✅ Fresh locator on each access
    return self.page.locator("#dynamic")

# Works correctly even after re-render
```

#### 4. **Method Chaining After Navigation**

```python
# Scenario: Navigation breaks chain
page.fill_email("test@test.com")\
    .click_next()\  # → Navigates to new page
    .fill_phone("123")  # ❌ Still using old page object

# Behavior:
# - Still using BookslotBasicInfoPage instance
# - But page has changed to EventInfoPage
# - Locators won't match
```

**Mitigation:**
```python
# Don't chain across page transitions
basic_info_page.fill_email("test@test.com")\
                .click_next()

# Create new page object
event_info_page = BookslotEventInfoPage(page)
event_info_page.fill_phone("123")
```

### Edge Cases

#### 1. **Optional Elements**

```python
# Element may or may not exist
def click_optional_button(self):
    """Click button if it exists"""
    try:
        if self.optional_button.is_visible(timeout=2000):
            self.optional_button.click()
    except:
        pass  # Element doesn't exist, continue
    return self
```

#### 2. **Multiple Elements (Lists)**

```python
@property
def search_results(self):
    """Returns all matching elements"""
    return self.page.locator(".result-item").all()

def get_result_count(self) -> int:
    """Get number of results"""
    return len(self.search_results)

def click_result_by_index(self, index: int):
    """Click specific result"""
    self.search_results[index].click()
    return self
```

#### 3. **Conditional Logic**

```python
def submit_form(self):
    """Submit form, handling confirmation dialog"""
    self.submit_button.click()
    
    # Handle confirmation if present
    if self.is_confirmation_dialog_displayed():
        self.confirmation_ok_button.click()
    
    return self
```

## 10. Extensibility & Customization

### How This Can Be Extended Safely

#### 1. **Add New Page Object**

```python
# pages/bookslot/bookslots_new_page.py
from playwright.sync_api import Page

class BookslotNewPage:
    """Page Object for new page"""
    
    def __init__(self, page: Page):
        self.page = page
    
    @property
    def new_element(self):
        return self.page.locator("#newElement")
    
    def new_action(self):
        self.new_element.click()
        return self
```

#### 2. **Extend Base Page**

```python
# pages/bookslot/enhanced_page.py
from framework.ui.base_page import BasePage

class EnhancedBookslotPage(BasePage):
    """Page with human behavior and base methods"""
    
    def __init__(self, page):
        super().__init__(page, enable_human_behavior=True)
    
    # Inherit base methods: navigate, click, fill, etc.
    # Add custom methods
    
    def custom_action(self):
        self.human_click("#element")  # Uses human behavior
        return self
```

#### 3. **Page Object Mixins**

```python
# pages/mixins/form_mixin.py
class FormMixin:
    """Reusable form methods"""
    
    def fill_form_field(self, locator, value):
        """Generic form field fill"""
        self.page.locator(locator).fill(value)
        return self

# pages/bookslot/bookslots_basicinfo_page1.py
class BookslotBasicInfoPage(FormMixin):
    """Page with form mixin"""
    
    def fill_all_fields(self, data):
        self.fill_form_field("#name", data['name'])\
            .fill_form_field("#email", data['email'])
        return self
```

#### 4. **Generic Page Components**

```python
# pages/components/nav_component.py
class NavigationComponent:
    """Reusable navigation component"""
    
    def __init__(self, page):
        self.page = page
    
    @property
    def home_link(self):
        return self.page.locator("a[href='/home']")
    
    def go_home(self):
        self.home_link.click()

# pages/bookslot/bookslots_basicinfo_page1.py
class BookslotBasicInfoPage:
    def __init__(self, page):
        self.page = page
        self.nav = NavigationComponent(page)  # Composition
    
    def navigate_home(self):
        self.nav.go_home()
        return self
```

### Plugin or Override Points

#### 1. **Custom Locator Strategy**

```python
class CustomLocatorPage:
    """Page with custom locator logic"""
    
    def _get_locator(self, selector_type, selector):
        """Override locator creation"""
        if selector_type == "text":
            return self.page.get_by_text(selector)
        elif selector_type == "role":
            return self.page.get_by_role(selector)
        else:
            return self.page.locator(selector)
    
    @property
    def submit_button(self):
        return self._get_locator("role", "button")
```

#### 2. **Auto-Logging Actions**

```python
from utils.logger import get_logger

class LoggedPage:
    """Page with action logging"""
    
    def __init__(self, page):
        self.page = page
        self.logger = get_logger(__name__)
    
    def fill_field(self, locator, value):
        self.logger.info(f"Filling {locator} with {value}")
        self.page.locator(locator).fill(value)
        return self
```

## 11. Anti-Patterns & What NOT to Do

See [Anti-Patterns Documentation](../10-Rules-And-Standards/Anti-Patterns.md) for complete guide.

### Quick Reference

❌ **Direct locators in tests**
❌ **Assertions in page objects**
❌ **Pytest imports in page objects**
❌ **Hardcoded test data in pages**
❌ **No method chaining (not returning self)**
❌ **Business logic in page objects**

## 12. Related Components

### Dependencies
- `playwright.sync_api.Page` - Browser control
- `playwright.sync_api.Locator` - Element references
- `framework.ui.base_page.BasePage` - Optional base class

### Used By
- **Test files** (`tests/**/*.py`) - Primary consumers
- **Workflow orchestrator** - Test flow management
- **Recording system** - Auto-generates page objects

### Related Documentation
- [Base Page Class](Base-Page-Class.md)
- [Strict Rules - POM Section](../10-Rules-And-Standards/Strict-Rules.md#1-page-object-model-pom-rules)
- [Anti-Patterns](../10-Rules-And-Standards/Anti-Patterns.md)
- [Best Practices](../10-Rules-And-Standards/Best-Practices.md)

---

**Last Updated:** February 1, 2026  
**Version:** 1.0.0
