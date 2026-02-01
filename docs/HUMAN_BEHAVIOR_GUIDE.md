# Human Behavior Simulation - Complete Guide

## 🎯 Overview

The Human Behavior Simulation module provides realistic, human-like interactions for automation testing. It mimics natural human behavior including:

- **Typing delays** with random pauses and corrections
- **Mouse movements** with smooth transitions
- **Scrolling patterns** with natural variations
- **Random interactions** (hovering, clicking, dropdown selections)
- **Idle/thinking times** between actions

### Why Use Human Behavior Simulation?

1. **Anti-Bot Detection**: Bypass automated detection systems
2. **Realistic Testing**: More accurate representation of real user interactions
3. **Visual Verification**: Better for demo/recording purposes
4. **Timing Issues**: Helps identify race conditions and timing problems
5. **Load Testing**: More realistic user behavior patterns

---

## 📁 Project Structure

```
Automation/
├── config/
│   └── human_behavior.yaml          # Configuration file
├── framework/
│   ├── core/
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── human_actions.py     # Main implementation
│   └── ui/
│       └── base_page.py             # Integrated with BasePage
├── conftest.py                      # Pytest fixtures
└── pytest.ini                       # Markers configuration
```

---

## 🚀 Quick Start

### Method 1: Using Pytest Fixture

```python
import pytest

@pytest.mark.human_like
def test_login_with_human_behavior(human_behavior, browser):
    """Test with automatic human behavior."""
    # Human behavior is automatically applied
    human_behavior.type_text("#username", "test_user")
    human_behavior.type_text("#password", "secret123")
    human_behavior.click_element("#login-button")
    human_behavior.scroll_page('bottom')
```

### Method 2: Using Page Objects

```python
from framework.ui.selenium_engine import SeleniumEngine
from pages.login_page import LoginPage

def test_with_page_object():
    engine = SeleniumEngine()
    engine.start("chrome")
    
    # Enable human behavior in page object
    login_page = LoginPage(engine.driver, enable_human_behavior=True)
    
    # Use human-like methods
    login_page.human_type("#username", "test_user")
    login_page.human_click("#login-button")
    
    engine.stop()
```

### Method 3: Direct Simulator Usage

```python
from selenium import webdriver
from framework.core.utils.human_actions import HumanBehaviorSimulator

driver = webdriver.Chrome()
driver.get("https://example.com")

# Create simulator
simulator = HumanBehaviorSimulator(driver, enabled=True)

# Use simulator methods
simulator.type_text("#email", "user@example.com")
simulator.click_element("#submit")
simulator.scroll_page('bottom')
simulator.random_mouse_movements(steps=10)
simulator.random_page_interactions()
simulator.simulate_idle()

driver.quit()
```

### Method 4: Standalone Functions

```python
from selenium import webdriver
from framework.core.utils.human_actions import (
    human_type, human_click, human_scroll_behavior,
    random_mouse_movement, simulate_idle
)

driver = webdriver.Chrome()
driver.get("https://example.com")

# Use standalone functions
element = driver.find_element(By.ID, "username")
human_type(element, "test_user", driver)

button = driver.find_element(By.ID, "login")
human_click(driver, button)

human_scroll_behavior(driver, 'bottom')
random_mouse_movement(driver, steps=5)
simulate_idle(driver, (1.0, 2.0))

driver.quit()
```

---

## ⚙️ Configuration

### Configuration File: `config/human_behavior.yaml`

```yaml
# Global enable/disable
enabled: true

# Environment-specific settings
environments:
  dev:
    enabled: true
    intensity: "minimal"
  staging:
    enabled: true
    intensity: "normal"
  production:
    enabled: false
    intensity: "minimal"

# Typing settings
typing:
  enabled: true
  min_delay: 0.08
  max_delay: 0.25
  pause_probability: 0.12

# Mouse settings
mouse:
  enabled: true
  movement_steps: 8
  offset_variance: 5

# Scrolling settings
scrolling:
  enabled: true
  increment_min: 100
  increment_max: 350

# Performance presets
presets:
  minimal:   # Fast execution
    typing: { min_delay: 0.05, max_delay: 0.15 }
  normal:    # Balanced
    typing: { min_delay: 0.08, max_delay: 0.25 }
  high:      # Very realistic
    typing: { min_delay: 0.12, max_delay: 0.35 }
```

### Command Line Options

```bash
# Enable human behavior
pytest --enable-human-behavior

# Disable human behavior
pytest --disable-human-behavior

# Set intensity level
pytest --human-behavior-intensity minimal
pytest --human-behavior-intensity normal
pytest --human-behavior-intensity high

# Combine with other options
pytest --env staging --test-browser chrome --enable-human-behavior
```

### Pytest Markers

```python
# Enable for specific test
@pytest.mark.human_like
def test_with_human_behavior():
    pass

# Disable for specific test
@pytest.mark.no_human_behavior
def test_without_human_behavior():
    pass
```

---

## 📚 API Reference

### HumanBehaviorSimulator Class

#### Constructor

```python
HumanBehaviorSimulator(
    driver: Union[WebDriver, Page],
    config: Optional[HumanBehaviorConfig] = None,
    enabled: Optional[bool] = None
)
```

#### Methods

**type_text(element, text, clear_first=True)**
- Types text with human-like delays
- Includes random pauses and thinking time
- Parameters:
  - `element`: Element to type into (WebElement, ElementHandle, or locator)
  - `text`: Text to type
  - `clear_first`: Clear element before typing
- Returns: bool (success status)

**click_element(element, with_hover=True)**
- Clicks with mouse movement simulation
- Optional hover before clicking
- Parameters:
  - `element`: Element to click
  - `with_hover`: Hover before clicking
- Returns: bool (success status)

**scroll_page(direction='down', distance=None, smooth=True)**
- Scrolls with human-like behavior
- Parameters:
  - `direction`: 'down', 'up', 'bottom', 'top'
  - `distance`: Specific pixel distance
  - `smooth`: Use smooth scrolling
- Returns: bool (success status)

**random_mouse_movements(steps=10)**
- Performs random mouse movements
- Hovers over visible elements
- Parameters:
  - `steps`: Number of movements
- Returns: bool (success status)

**random_page_interactions(max_interactions=3)**
- Randomly interacts with page elements
- Clicks checkboxes, selects dropdowns, hovers links
- Parameters:
  - `max_interactions`: Maximum interactions
- Returns: bool (success status)

**simulate_idle(duration=None)**
- Simulates thinking/idle time
- Parameters:
  - `duration`: Tuple of (min, max) seconds
- Returns: bool (success status)

### Standalone Functions

```python
human_type(element, text, driver=None, min_delay=0.08, max_delay=0.25)
human_click(driver, element)
human_scroll_behavior(driver, direction='bottom')
random_mouse_movement(driver, steps=10, retry=3)
random_page_interaction(driver, max_interactions=3)
simulate_idle(driver, idle_time=(0.8, 2.5))
```

---

## 🎯 Usage Examples

### Example 1: Login Form

```python
import pytest

@pytest.mark.human_like
def test_login_form(human_behavior, browser):
    """Test login with human behavior."""
    browser.get("https://example.com/login")
    
    # Type username with delays
    human_behavior.type_text("#username", "john.doe@example.com")
    
    # Think before typing password
    human_behavior.simulate_idle((0.5, 1.5))
    
    # Type password
    human_behavior.type_text("#password", "SecurePass123!")
    
    # Hover and click login button
    human_behavior.click_element("#login-btn", with_hover=True)
    
    # Wait for page load
    human_behavior.simulate_idle((2.0, 3.0))
    
    # Verify success
    assert "Dashboard" in browser.title
```

### Example 2: Form Fill with Multiple Fields

```python
@pytest.mark.human_like
def test_registration_form(human_behavior, browser):
    """Test registration with realistic behavior."""
    browser.get("https://example.com/register")
    
    # Fill form fields with natural delays
    fields = {
        "#first-name": "John",
        "#last-name": "Doe",
        "#email": "john.doe@example.com",
        "#phone": "555-1234",
        "#address": "123 Main St"
    }
    
    for selector, value in fields.items():
        human_behavior.type_text(selector, value)
        human_behavior.simulate_idle((0.3, 0.8))  # Pause between fields
    
    # Scroll to view terms
    human_behavior.scroll_page('down', distance=300)
    
    # Random interaction
    human_behavior.random_page_interactions(max_interactions=2)
    
    # Accept terms and submit
    human_behavior.click_element("#terms-checkbox")
    human_behavior.simulate_idle((0.5, 1.0))
    human_behavior.click_element("#submit-btn")
```

### Example 3: E-commerce Product Search

```python
@pytest.mark.human_like
def test_product_search(human_behavior, browser):
    """Test product search with human behavior."""
    browser.get("https://example.com/shop")
    
    # Random mouse movements (browsing behavior)
    human_behavior.random_mouse_movements(steps=8)
    
    # Scroll down to explore
    human_behavior.scroll_page('down', distance=500)
    human_behavior.simulate_idle((1.0, 2.0))  # Reading products
    
    # Search for product
    human_behavior.click_element("#search-box")
    human_behavior.type_text("#search-box", "wireless headphones")
    human_behavior.simulate_idle((0.5, 1.0))
    human_behavior.click_element("#search-btn")
    
    # Browse results
    human_behavior.simulate_idle((1.5, 2.5))  # Page load
    human_behavior.scroll_page('bottom')
    
    # Click first product
    human_behavior.click_element(".product-card:first-child")
```

### Example 4: With Page Objects

```python
class LoginPage:
    def __init__(self, driver, enable_human_behavior=True):
        self.driver = driver
        self.human = HumanBehaviorSimulator(driver, enabled=enable_human_behavior)
    
    def login(self, username, password):
        """Login with human-like behavior."""
        self.human.type_text("#username", username)
        self.human.simulate_idle((0.3, 0.8))
        self.human.type_text("#password", password)
        self.human.simulate_idle((0.5, 1.0))
        self.human.click_element("#login-button")
        self.human.simulate_idle((2.0, 3.0))

# Usage
def test_with_page_object(browser):
    login_page = LoginPage(browser, enable_human_behavior=True)
    login_page.login("user@example.com", "password123")
```

### Example 5: Conditional Human Behavior

```python
def test_conditional_behavior(browser, env):
    """Use human behavior only in certain environments."""
    # Enable human behavior only in staging
    enable_human = (env == 'staging')
    
    simulator = HumanBehaviorSimulator(browser, enabled=enable_human)
    
    simulator.type_text("#field1", "value1")  # Human-like in staging, normal in production
    simulator.click_element("#submit")
```

### Example 6: Selenium with Human Behavior

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from framework.core.utils.human_actions import HumanBehaviorSimulator

def test_selenium_human_behavior():
    driver = webdriver.Chrome()
    driver.get("https://www.saucedemo.com/")
    
    # Initialize simulator
    simulator = HumanBehaviorSimulator(driver, enabled=True)
    
    # Login with human behavior
    username = driver.find_element(By.ID, "user-name")
    password = driver.find_element(By.ID, "password")
    login_btn = driver.find_element(By.ID, "login-button")
    
    simulator.type_text(username, "standard_user")
    simulator.type_text(password, "secret_sauce")
    simulator.click_element(login_btn)
    
    # Browse page
    simulator.random_mouse_movements(steps=10)
    simulator.scroll_page('bottom')
    simulator.simulate_idle((2.0, 4.0))
    
    driver.quit()
```

### Example 7: Playwright with Human Behavior

```python
from playwright.sync_api import sync_playwright
from framework.core.utils.human_actions import HumanBehaviorSimulator

def test_playwright_human_behavior():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.saucedemo.com/")
        
        # Initialize simulator
        simulator = HumanBehaviorSimulator(page, enabled=True)
        
        # Login with human behavior
        simulator.type_text("#user-name", "standard_user")
        simulator.type_text("#password", "secret_sauce")
        simulator.click_element("#login-button")
        
        # Browse
        simulator.scroll_page('down', distance=500)
        simulator.simulate_idle((1.5, 2.5))
        
        browser.close()
```

---

## 🎛️ Advanced Configuration

### Environment-Specific Behavior

```python
# In conftest.py or test file
import os
from framework.core.utils.human_actions import get_behavior_config

def pytest_configure(config):
    # Set environment
    os.environ['TEST_ENV'] = config.getoption('--env')
    
    # Reload config to apply environment settings
    behavior_config = get_behavior_config()
    behavior_config.reload_config()
```

### Custom Timing Configuration

```python
from framework.core.utils.human_actions import HumanBehaviorSimulator

# Create simulator with custom config
simulator = HumanBehaviorSimulator(driver, enabled=True)

# Access and modify config
config = simulator.config
config._config['typing']['min_delay'] = 0.05
config._config['typing']['max_delay'] = 0.15
```

### Performance Tuning

**For Fast Execution (CI/CD)**:
```bash
pytest --disable-human-behavior
# OR
pytest --human-behavior-intensity minimal
```

**For Demo/Recording**:
```bash
pytest --enable-human-behavior --human-behavior-intensity high
```

**For Normal Testing**:
```bash
pytest --human-behavior-intensity normal
```

---

## 🐛 Troubleshooting

### Issue: Human behavior not working

**Solution**:
1. Check if enabled in config: `config/human_behavior.yaml`
2. Verify command line options: `--enable-human-behavior`
3. Check test markers: `@pytest.mark.human_like`
4. Verify driver is available in fixture

### Issue: Tests too slow

**Solution**:
1. Disable human behavior: `--disable-human-behavior`
2. Use minimal intensity: `--human-behavior-intensity minimal`
3. Adjust config: reduce delays in `human_behavior.yaml`

### Issue: Elements not found during mouse movements

**Solution**:
- This is normal; simulator handles exceptions gracefully
- Reduce `mouse_movement.steps` in config
- Set `mouse_movement.retry_attempts` to lower value

### Issue: Config file not found

**Solution**:
```python
# Config path should be: config/human_behavior.yaml
# If missing, defaults are used
# Check path: framework/core/utils/human_actions.py line ~120
```

---

## 📊 Best Practices

### 1. Use Markers for Selective Tests

```python
# Only critical user flows need human behavior
@pytest.mark.human_like
@pytest.mark.critical
def test_checkout_flow():
    pass

# Fast smoke tests don't need it
@pytest.mark.smoke
@pytest.mark.no_human_behavior
def test_homepage_loads():
    pass
```

### 2. Environment-Based Configuration

```yaml
# human_behavior.yaml
environments:
  dev:
    enabled: true
    intensity: "minimal"
  staging:
    enabled: true
    intensity: "normal"
  production:
    enabled: false  # Fast execution in production
```

### 3. Combine with Assertions

```python
@pytest.mark.human_like
def test_form_validation(human_behavior, browser):
    human_behavior.type_text("#email", "invalid-email")
    human_behavior.click_element("#submit")
    
    # Assert validation message
    assert browser.find_element(By.CLASS_NAME, "error").is_displayed()
```

### 4. Use in Page Object Methods

```python
class BasePage:
    def fill_form(self, form_data):
        for field, value in form_data.items():
            self.human_type(field, value)
            self.human.simulate_idle((0.2, 0.5))
```

### 5. Gradual Adoption

Start with critical tests:
```python
# Phase 1: Add to login tests
@pytest.mark.human_like
def test_login(): pass

# Phase 2: Add to checkout flow
@pytest.mark.human_like
def test_checkout(): pass

# Phase 3: Expand to other flows
```

---

## 🔗 Integration with Existing Framework

### With Selenium Engine

```python
from framework.ui.selenium_engine import SeleniumEngine
from framework.core.utils.human_actions import HumanBehaviorSimulator

engine = SeleniumEngine(headless=False)
engine.start("chrome")

simulator = HumanBehaviorSimulator(engine.driver, enabled=True)
# Use simulator methods...

engine.stop()
```

### With Playwright Engine

```python
from framework.ui.playwright_engine import PlaywrightEngine
from framework.core.utils.human_actions import HumanBehaviorSimulator

engine = PlaywrightEngine(headless=False)
engine.start("chromium")

simulator = HumanBehaviorSimulator(engine.page, enabled=True)
# Use simulator methods...

engine.stop()
```

### With Existing Page Objects

All page objects inheriting from `BasePage` automatically support human behavior:

```python
class MyPage(BasePage):
    def login(self, username, password):
        # Use human-like methods
        self.human_type("#username", username)
        self.human_click("#login")
        
        # Or use normal methods (respects human behavior if enabled)
        self.fill("#password", password)
        self.click("#submit")
```

---

## 📈 Performance Impact

| Configuration | Execution Time | Realism | Use Case |
|--------------|----------------|---------|----------|
| Disabled | 1x (baseline) | Low | CI/CD, Fast feedback |
| Minimal | 1.2-1.5x | Medium | Quick testing with some realism |
| Normal | 1.5-2.5x | High | Regular testing, demos |
| High | 2-4x | Very High | Security testing, recordings |

---

## 🎓 Learning Resources

### Related Files

1. `framework/core/utils/human_actions.py` - Main implementation
2. `config/human_behavior.yaml` - Configuration
3. `conftest.py` - Pytest fixtures
4. `framework/ui/base_page.py` - Page object integration

### Example Tests

Check the `examples/` directory for complete test examples.

---

## 🆘 Support

**Author**: Lokendra Singh  
**Email**: qa.lokendra@gmail.com  
**Website**: www.sqamentor.com

For issues or questions:
1. Check this documentation
2. Review config file: `config/human_behavior.yaml`
3. Check logs for `[Human Behavior]` messages
4. Contact the author

---

## 📝 Changelog

### Version 1.0 (Current)

- ✅ Initial implementation
- ✅ Support for Selenium and Playwright
- ✅ Configurable timing and behavior
- ✅ Environment-aware configuration
- ✅ Integration with pytest fixtures
- ✅ Page object support
- ✅ Comprehensive error handling
- ✅ Allure reporting integration

---

## 🔜 Future Enhancements

- [ ] Machine learning-based behavior patterns
- [ ] Recording and replay of human patterns
- [ ] Browser fingerprinting avoidance
- [ ] Network throttling simulation
- [ ] Mobile gesture simulation
- [ ] Advanced anti-detection techniques

---

**Happy Testing! 🎉**
