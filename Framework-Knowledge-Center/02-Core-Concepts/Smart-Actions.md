# Smart Actions - Context-Aware Automation Layer

## 1. Purpose
- **Why this component exists**: Eliminates the need for manual `time.sleep()` calls throughout test code by automatically applying context-aware delays
- **What problem it solves**: Makes tests more realistic (human-like), maintainable, and removes scattered delay logic from tests

## 2. Scope

### What is Included
- Intelligent action wrappers for click, type, navigate, button_click
- Automatic context-aware delays (pre-action and post-action)
- Integration with human behavior simulation system
- Verbose logging for debugging delays
- Context-specific typing speeds (numbers, emails, dates, text)

### What is Excluded
- Direct browser automation (delegates to Playwright/Selenium)
- Test assertions
- Page object creation
- Data generation

## 3. Current Implementation

### Summary
SmartActions is a wrapper class that sits between test code and the browser Page object. It automatically applies intelligent delays before and after each action based on the action context.

### Key Classes, Files, and Modules

**File:** `framework/core/smart_actions.py`

**Main Class:** `SmartActions`

**Key Methods:**
- `click(element, description)` - Click with auto-delays
- `type_text(element, text, field_name)` - Type with context-aware speed
- `button_click(element, description)` - Button click with longer delays
- `navigate(url, page_name)` - Navigation with page load waits
- `select_dropdown(element, value, description)` - Dropdown selection
- `checkbox_toggle(element, description)` - Checkbox interaction

## 4. File & Code Mapping

### File: `framework/core/smart_actions.py`

**Responsibilities:**
- Wrap Playwright/Selenium actions
- Apply context-aware delays
- Log action execution
- Integrate with human behavior configuration
- Handle element visibility waits

**Key Code Sections:**

```python
# Line 1-20: Imports and module documentation
# Line 25-46: SmartActions class initialization
# Line 48-55: Internal delay method with logging
# Line 57-67: Click action wrapper
# Line 69-140: Type text with context-aware speed
# Line 142-152: Button click wrapper
# Line 154-165: Navigate with delays
# Line 167-180: Dropdown selection
# Line 182-195: Checkbox toggle
# Line 197-210: Radio button selection
```

## 5. Execution Flow

### Step-by-Step Runtime Behavior

#### Example: Click Action
```python
smart_actions.click(page.locator("#submit"), "Submit Button")
```

**Flow:**
1. **Pre-Action Delay** (0.3-0.7s)
   - Simulates user "thinking time"
   - Random duration within range
   - Logs if verbose mode enabled

2. **Element Action**
   - Delegates to Playwright/Selenium
   - Native click() method called
   - Auto-waits for element (Playwright feature)

3. **Post-Action Delay** (0.2-0.4s)
   - Simulates confirmation/page load
   - Random duration within range
   - Logs if verbose mode enabled

#### Example: Type Text Action
```python
smart_actions.type_text(page.locator("#email"), "test@example.com", "Email Field")
```

**Flow:**
1. **Pre-Action Delay** (0.3-0.6s)
   - Preparation time

2. **Element Visibility Wait**
   - Waits up to 10 seconds for element
   - Retries once if not immediately visible

3. **Context Detection**
   - Detects if text is: numeric, email, date, or general text
   - Selects appropriate typing speed

4. **Character-by-Character Typing** (if human behavior enabled)
   - Numbers: 0.08-0.18s per char
   - Email: 0.12-0.25s per char
   - Dates: 0.10-0.22s per char
   - Text: 0.10-0.23s per char

5. **Post-Action Delay** (0.2-0.5s)
   - Review time

### Sync vs Async Behavior
- **Synchronous only** - All operations block until complete
- No async/await support currently
- Sequential execution of delays

## 6. Inputs & Outputs

### Initialization Parameters

```python
SmartActions(page: Page, enable_human: bool = False, verbose: bool = False)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | `Page` | Required | Playwright Page object |
| `enable_human` | `bool` | `False` | Enable human-like delays |
| `verbose` | `bool` | `False` | Print delay information |

### Method Inputs

#### click()
```python
click(element: Locator, description: str = "")
```
- `element`: Playwright Locator object
- `description`: Human-readable action description (for logging)

#### type_text()
```python
type_text(element: Locator, text: str, field_name: str = "")
```
- `element`: Playwright Locator object
- `text`: String to type (can be number, email, etc.)
- `field_name`: Human-readable field name (for logging)

#### button_click()
```python
button_click(element: Locator, description: str = "")
```
- `element`: Playwright Locator object
- `description`: Human-readable button description

#### navigate()
```python
navigate(url: str, page_name: str = "")
```
- `url`: Full URL to navigate to
- `page_name`: Human-readable page name (for logging)

### Config Dependencies

**Config File:** `config/human_behavior.yaml`

```yaml
human_behavior:
  enabled: true
  intensity: "normal"  # minimal, normal, high
  
  delays:
    click_before: [0.3, 0.7]
    click_after: [0.2, 0.4]
    type_before: [0.3, 0.6]
    type_after: [0.2, 0.5]
    button_before: [0.4, 0.9]
    button_after: [0.3, 0.6]
    navigate_before: [0.4, 0.8]
    navigate_after: [0.5, 1.0]
```

### Return Values / Side Effects

**Returns:** None (all methods are void)

**Side Effects:**
- Sleeps thread for delay durations
- Logs to console if verbose=True
- Interacts with browser (clicks, types, navigates)

## 7. Design Decisions

### Why This Approach Was Chosen

#### 1. **Wrapper Pattern vs Direct Modification**
**Decision:** Create wrapper methods instead of modifying Page class directly

**Why:**
- Separation of concerns (delays separate from browser control)
- Works with both Playwright and Selenium
- Easy to enable/disable
- No framework modification needed

#### 2. **Random Delay Ranges vs Fixed Delays**
**Decision:** Use random durations within min-max ranges

**Why:**
- More realistic human behavior
- Harder to detect as bot
- Prevents timing-based test flakiness

#### 3. **Context-Aware Typing Speeds**
**Decision:** Different typing speeds for numbers, emails, dates, text

**Why:**
- Humans type numbers faster than text
- Emails have predictable patterns (slower at @, .)
- More realistic simulation

#### 4. **Pre-Action AND Post-Action Delays**
**Decision:** Apply delays both before and after actions

**Why:**
- Pre-delay: Simulates decision-making
- Post-delay: Simulates confirmation/waiting for response
- More complete human behavior model

### Trade-offs

| Pro | Con |
|-----|-----|
| ✅ Realistic human behavior | ❌ Tests run slower |
| ✅ Centralized delay logic | ❌ Additional abstraction layer |
| ✅ Easy to configure | ❌ Requires understanding of action types |
| ✅ Reduces test flakiness | ❌ Can make debugging harder |
| ✅ Clean test code | ❌ One more API to learn |

## 8. Rules & Constraints

### Hard Rules Enforced by the Framework

#### ✅ MUST DO:
1. **Always pass Playwright/Selenium element objects**
   - Not string selectors
   - Not direct DOM elements

2. **Enable human behavior via configuration or constructor**
   - Don't modify delay logic in test code
   - Use centralized config

3. **Use descriptive action names**
   - Helps with debugging
   - Makes logs readable

#### ❌ MUST NOT DO:
1. **Never add manual `time.sleep()` calls after using SmartActions**
   - Delays are automatic
   - Manual delays interfere with calculated timing

2. **Don't mix SmartActions and direct page.click()**
   - Inconsistent behavior
   - Defeats purpose of automation

3. **Don't modify delay ranges in production tests**
   - Use config files
   - Keep test code clean

### Assumptions Developers Must Not Violate

1. **Playwright/Selenium is already initialized**
   - SmartActions doesn't create Page objects
   - Assumes page fixture is available

2. **Element locators are valid**
   - SmartActions doesn't validate selectors
   - Relies on Playwright/Selenium error handling

3. **Human behavior config exists**
   - Falls back to defaults if missing
   - But config should be present

4. **Single-threaded execution**
   - Delays use `time.sleep()` which blocks thread
   - Not designed for parallel action execution

## 9. Error Handling & Edge Cases

### Known Failure Scenarios

#### 1. **Element Not Visible**
```python
# Scenario: Element doesn't exist or not visible
smart_actions.type_text(page.locator("#missing"), "text")

# Behavior:
# - Waits up to 10 seconds
# - Retries once with 0.5s delay
# - If still fails, raises Playwright TimeoutError
```

**Fallback Logic:**
```python
try:
    element.wait_for(state="visible", timeout=10000)
except Exception:
    time.sleep(0.5)  # Brief wait
    element.wait_for(state="visible", timeout=10000)  # Retry
```

#### 2. **Non-Interactive Elements**
```python
# Scenario: Trying to click disabled element
smart_actions.click(page.locator("#disabledBtn"))

# Behavior:
# - Pre-delay still occurs
# - Playwright throws actionability error
# - Post-delay skipped (exception raised)
```

**Mitigation:** Check element state before action:
```python
if page.locator("#btn").is_enabled():
    smart_actions.click(page.locator("#btn"))
```

#### 3. **Very Long Text Typing**
```python
# Scenario: Typing 1000+ character text with human behavior
smart_actions.type_text(element, "A" * 1000, "Long Text")

# Behavior:
# - Can take 100-230 seconds (0.10-0.23s per char)
# - Test appears frozen
# - May timeout in CI environments
```

**Mitigation:**
- Disable human behavior for long text: `enable_human=False`
- Or use Playwright's fast fill(): `element.fill(text)`

#### 4. **Page Navigation During Action**
```python
# Scenario: Page navigates away during type action
smart_actions.type_text(element, "test")
# → Page redirects mid-typing

# Behavior:
# - Playwright loses element reference
# - Raises "Element is not attached to the DOM" error
# - Post-delay skipped
```

**Mitigation:** Wait for stable state before action

### Edge Cases

#### 1. **Empty Text**
```python
smart_actions.type_text(element, "", "Field")
# Still applies delays, but no typing occurs
```

#### 2. **Special Characters in Text**
```python
smart_actions.type_text(element, "test@#$%^&*()", "Field")
# Typed character-by-character, including special chars
```

#### 3. **Multiple Rapid Actions**
```python
smart_actions.click(btn1)  # 0.3-0.7s + action + 0.2-0.4s
smart_actions.click(btn2)  # 0.3-0.7s + action + 0.2-0.4s
# Cumulative delays can be significant
```

## 10. Extensibility & Customization

### How This Can Be Extended Safely

#### 1. **Add New Action Methods**

```python
# In smart_actions.py
def double_click(self, element: Locator, description: str = ""):
    """Double-click with smart delays"""
    self._delay(0.3, 0.7, f"Before double-click: {description}")
    element.dblclick()
    self._delay(0.2, 0.4, f"After double-click: {description}")
```

#### 2. **Custom Delay Profiles**

```python
# Create profile-based SmartActions
class AggressiveSmartActions(SmartActions):
    """Fast delays for CI/CD"""
    def _delay(self, min_sec, max_sec, context=""):
        if self.enable_human:
            delay_time = random.uniform(min_sec * 0.5, max_sec * 0.5)
            time.sleep(delay_time)
```

#### 3. **Action Hooks**

```python
class HookedSmartActions(SmartActions):
    """SmartActions with pre/post hooks"""
    
    def __init__(self, page, enable_human=False, verbose=False):
        super().__init__(page, enable_human, verbose)
        self.action_log = []
    
    def click(self, element, description=""):
        self.action_log.append(f"Clicking: {description}")
        super().click(element, description)
```

### Plugin or Override Points

#### 1. **Delay Calculation Override**

```python
class CustomSmartActions(SmartActions):
    def _delay(self, min_sec, max_sec, context=""):
        """Custom delay logic"""
        if self.enable_human:
            # Your custom calculation
            delay = calculate_my_delay(min_sec, max_sec, context)
            time.sleep(delay)
```

#### 2. **Context Detection Override**

```python
class ImprovedSmartActions(SmartActions):
    def type_text(self, element, text, field_name=""):
        # Add custom context detection
        if self._is_credit_card(text):
            typing_delay = (0.15, 0.30)  # Slower for credit cards
        else:
            # Use default logic
            super().type_text(element, text, field_name)
```

#### 3. **Logger Integration**

```python
from utils.logger import get_logger

class LoggedSmartActions(SmartActions):
    def __init__(self, page, enable_human=False, verbose=False):
        super().__init__(page, enable_human, verbose)
        self.logger = get_logger(__name__)
    
    def _delay(self, min_sec, max_sec, context=""):
        if self.enable_human:
            delay = random.uniform(min_sec, max_sec)
            self.logger.debug(f"Smart delay: {delay:.2f}s - {context}")
            time.sleep(delay)
```

## 11. Anti-Patterns & What NOT to Do

### Common Mistakes

#### ❌ **1. Mixing SmartActions with Manual Delays**

```python
# BAD - Redundant delays
smart_actions.click(button, "Submit")  # Already has delays
time.sleep(2)  # ❌ Unnecessary manual delay

# GOOD - Trust SmartActions
smart_actions.click(button, "Submit")  # ✅ Automatic delays
```

#### ❌ **2. Using Direct page.click() After SmartActions**

```python
# BAD - Inconsistent
smart_actions.click(button1, "Button 1")
page.locator("#button2").click()  # ❌ No delays

# GOOD - Consistent approach
smart_actions.click(button1, "Button 1")
smart_actions.click(button2, "Button 2")  # ✅ Both have delays
```

#### ❌ **3. Ignoring Action Descriptions**

```python
# BAD - No context in logs
smart_actions.click(page.locator("#btn"), "")  # ❌ Empty description

# GOOD - Descriptive
smart_actions.click(page.locator("#btn"), "Submit Form Button")  # ✅
```

#### ❌ **4. Passing String Selectors**

```python
# BAD - SmartActions expects Locator object
smart_actions.click("#button", "Click")  # ❌ TypeError

# GOOD - Pass Locator
smart_actions.click(page.locator("#button"), "Click")  # ✅
```

#### ❌ **5. Disabling Human Behavior Inconsistently**

```python
# BAD - Enable/disable randomly
smart_actions = SmartActions(page, enable_human=True)
smart_actions.enable_human = False  # ❌ Modifying mid-test

# GOOD - Set once at initialization
smart_actions = SmartActions(page, enable_human=True)  # ✅
# Or use config/fixture
```

#### ❌ **6. Not Handling Very Long Texts**

```python
# BAD - Will take forever with human behavior
long_text = "A" * 1000
smart_actions.type_text(element, long_text, "Field")  # ❌ 100-230 seconds

# GOOD - Use direct fill for long text
if len(text) > 100:
    element.fill(text)  # ✅ Fast fill
else:
    smart_actions.type_text(element, text, "Field")  # ✅ Human-like
```

### Dangerous Changes

#### ⚠️ **Modifying Delay Ranges Globally**

```python
# DANGEROUS - Affects all tests
# Don't modify in smart_actions.py
self._delay(0.001, 0.002)  # ❌ Too fast, defeats purpose

# SAFE - Use config or subclass
# In config/human_behavior.yaml
delays:
  click_before: [0.1, 0.2]  # ✅ Configure centrally
```

#### ⚠️ **Removing Delay Checks**

```python
# DANGEROUS - Breaks feature
def _delay(self, min_sec, max_sec, context=""):
    # if self.enable_human:  # ❌ Don't remove this check
    time.sleep(random.uniform(min_sec, max_sec))

# SAFE - Keep conditional
def _delay(self, min_sec, max_sec, context=""):
    if self.enable_human:  # ✅ Allows disabling
        time.sleep(random.uniform(min_sec, max_sec))
```

#### ⚠️ **Async Conversion Without Consideration**

```python
# DANGEROUS - Breaks synchronous tests
async def click(self, element, description=""):  # ❌ Now async
    await self._delay(0.3, 0.7)
    await element.click()

# SAFE - Keep synchronous or create separate AsyncSmartActions class
```

## 12. Related Components

### Dependencies

1. **`playwright.sync_api.Page`** - Browser control
2. **`playwright.sync_api.Locator`** - Element references
3. **`random`** - Delay randomization
4. **`time`** - Sleep functionality
5. **`typing`** - Type hints
6. **`config/human_behavior.yaml`** - Configuration

### Upstream Components (Call SmartActions)

1. **Test Files** (`tests/**/*.py`)
   - Use SmartActions via `smart_actions` fixture
   - Primary consumers

2. **Page Objects** (`pages/**/*.py`)
   - Can use SmartActions internally
   - Optional but recommended

3. **`conftest.py`**
   - Creates `smart_actions` fixture
   - Initializes with user config

### Downstream Links (Called by SmartActions)

1. **Playwright API**
   - `Page.locator()`, `Locator.click()`, `Locator.fill()`
   - Core browser automation

2. **Human Behavior System** (`framework/core/utils/human_actions.py`)
   - Advanced human simulation
   - Optional integration

3. **Logger** (`utils/logger.py`)
   - Can be integrated for action logging
   - Optional

### Integration Points

```
┌─────────────────┐
│   Test Files    │
└────────┬────────┘
         │ uses
         ▼
┌─────────────────┐
│  smart_actions  │ (pytest fixture)
│    (conftest)   │
└────────┬────────┘
         │ creates
         ▼
┌─────────────────┐         ┌──────────────────┐
│  SmartActions   │────────▶│ Playwright Page  │
└────────┬────────┘  calls  └──────────────────┘
         │
         │ reads
         ▼
┌─────────────────┐
│ human_behavior  │
│   .yaml config  │
└─────────────────┘
```

---

**Related Documentation:**
- [Human Behavior Simulation](Human-Behavior-Simulation.md)
- [Execution Flow](Execution-Flow-Orchestrator.md)
- [Configuration Guide](../05-Configuration/Human-Behavior-Configuration.md)
- [Strict Rules](../10-Rules-And-Standards/Strict-Rules.md)

---

**Last Updated:** February 1, 2026  
**Component Version:** 1.0.0
