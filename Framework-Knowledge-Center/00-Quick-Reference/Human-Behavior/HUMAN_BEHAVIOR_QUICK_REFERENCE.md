# Human Behavior Simulation - Quick Reference

## 🚀 Quick Start (30 seconds)

### Option 1: Add Marker to Test
```python
import pytest

@pytest.mark.human_like
def test_login(browser):
    # Your test code - human behavior automatically applied
    pass
```

### Option 2: Use Fixture
```python
def test_form_fill(human_behavior, browser):
    human_behavior.type_text("#email", "user@example.com")
    human_behavior.click_element("#submit")
    human_behavior.scroll_page('bottom')
```

### Option 3: Direct Usage
```python
from framework.core.utils.human_actions import HumanBehaviorSimulator

simulator = HumanBehaviorSimulator(driver, enabled=True)
simulator.type_text(element, "text")
simulator.click_element(button)
```

---

## 📋 Command Line

```bash
# Enable human behavior
pytest --enable-human-behavior

# Set intensity (minimal/normal/high)
pytest --human-behavior-intensity normal

# Disable
pytest --disable-human-behavior

# Run with marker
pytest -m human_like

# Run examples
pytest examples/human_behavior/ -v
```

---

## 🎯 Main Methods

```python
# Typing with delays
simulator.type_text(element, "text", clear_first=True)

# Click with mouse movement
simulator.click_element(element, with_hover=True)

# Scroll
simulator.scroll_page('down', distance=300)
simulator.scroll_page('bottom')  # Scroll to bottom

# Random movements
simulator.random_mouse_movements(steps=10)

# Page interactions
simulator.random_page_interactions(max_interactions=3)

# Idle/thinking time
simulator.simulate_idle((1.0, 2.0))
```

---

## ⚙️ Configuration

**File**: `config/human_behavior.yaml`

```yaml
# Enable/disable globally
enabled: true

# Environment-specific
environments:
  dev:
    enabled: true
    intensity: "minimal"
  staging:
    enabled: true
    intensity: "normal"
  production:
    enabled: false

# Adjust timing
typing:
  min_delay: 0.08  # Fast: 0.05, Slow: 0.15
  max_delay: 0.25  # Fast: 0.15, Slow: 0.40

mouse:
  movement_steps: 8  # Fast: 4, Slow: 12

scrolling:
  increment_min: 100  # Fast: 200
  increment_max: 350  # Fast: 500
```

---

## 🎨 Markers

```python
# Enable for test
@pytest.mark.human_like
def test_with_behavior():
    pass

# Disable for test
@pytest.mark.no_human_behavior
def test_without_behavior():
    pass

# Combine markers
@pytest.mark.human_like
@pytest.mark.critical
def test_critical_flow():
    pass
```

---

## 📦 Page Objects

```python
from framework.ui.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, driver, enable_human_behavior=True):
        super().__init__(driver, enable_human_behavior)
    
    def login(self, username, password):
        # Use human methods
        self.human_type("#username", username)
        self.human_click("#login-btn")
        
        # Or use normal methods (respects config)
        self.fill("#password", password)
        self.click("#submit")
```

---

## 🔧 Common Patterns

### Login Flow
```python
@pytest.mark.human_like
def test_login(human_behavior, browser):
    browser.get("https://example.com/login")
    
    human_behavior.type_text("#username", "user")
    human_behavior.simulate_idle((0.5, 1.0))  # Think
    human_behavior.type_text("#password", "pass")
    human_behavior.click_element("#login", with_hover=True)
    human_behavior.simulate_idle((2.0, 3.0))  # Wait
```

### Form Filling
```python
fields = {
    "#first-name": "John",
    "#last-name": "Doe",
    "#email": "john@example.com"
}

for selector, value in fields.items():
    human_behavior.type_text(selector, value)
    human_behavior.simulate_idle((0.3, 0.7))
```

### Product Browsing
```python
# Browse products
human_behavior.scroll_page('down', distance=300)
human_behavior.simulate_idle((1.5, 2.5))  # Read
human_behavior.random_mouse_movements(steps=10)

# Select product
human_behavior.click_element(".product-card:first")
```

---

## 📊 Performance

| Intensity | Speed | Use Case |
|-----------|-------|----------|
| Disabled  | 1.0x  | CI/CD |
| Minimal   | 1.3x  | Quick tests |
| Normal    | 2.0x  | Regular testing |
| High      | 3.5x  | Demos/security |

---

## 🐛 Troubleshooting

### Not Working?
```python
# Check config
from framework.core.utils.human_actions import get_behavior_config
config = get_behavior_config()
print(f"Enabled: {config.is_enabled()}")

# Force enable
simulator = HumanBehaviorSimulator(driver, enabled=True)
```

### Too Slow?
```bash
# Use minimal intensity
pytest --human-behavior-intensity minimal

# Or disable
pytest --disable-human-behavior
```

### Config Not Loading?
```bash
# Verify file exists
ls config/human_behavior.yaml

# Check syntax
python -c "import yaml; yaml.safe_load(open('config/human_behavior.yaml'))"
```

---

## 📚 Documentation

- **Complete Guide**: [docs/HUMAN_BEHAVIOR_GUIDE.md](docs/HUMAN_BEHAVIOR_GUIDE.md)
- **Examples**: [examples/human_behavior/](examples/human_behavior/)
- **Implementation Summary**: [HUMAN_BEHAVIOR_IMPLEMENTATION_SUMMARY.md](HUMAN_BEHAVIOR_IMPLEMENTATION_SUMMARY.md)
- **Configuration**: [config/human_behavior.yaml](config/human_behavior.yaml)

---

## 🎓 Examples

Run examples to see it in action:

```bash
# All examples
pytest examples/human_behavior/ -v

# Specific example
pytest examples/human_behavior/example_01_basic_usage.py -v

# Standalone
python examples/human_behavior/example_01_basic_usage.py
```

---

## ✅ Validation

Test the implementation:

```bash
# Run validation script
python validate_human_behavior.py

# Should see: ✅ ALL VALIDATIONS PASSED!
```

---

## 💡 Best Practices

1. **Use markers for critical tests only**
   ```python
   @pytest.mark.human_like
   @pytest.mark.critical
   def test_checkout():
       pass
   ```

2. **Configure per environment**
   ```yaml
   production:
     enabled: false  # Fast in prod
   staging:
     enabled: true   # Realistic in staging
   ```

3. **Combine with assertions**
   ```python
   human_behavior.type_text("#email", "invalid")
   human_behavior.click_element("#submit")
   assert error_message_visible()
   ```

4. **Use in page objects**
   ```python
   class MyPage(BasePage):
       def fill_form(self, data):
           for field, value in data.items():
               self.human_type(field, value)
   ```

---

## 🔗 Key Files

```
Framework/
├── config/human_behavior.yaml          # Configuration
├── framework/core/utils/
│   └── human_actions.py                # Main module
├── conftest.py                         # Pytest fixtures
├── pytest.ini                          # Markers
└── examples/human_behavior/            # Examples
    ├── example_01_basic_usage.py
    ├── example_02_form_filling.py
    ├── example_03_framework_integration.py
    └── example_04_advanced_ecommerce.py
```

---

## 📞 Support

**Author**: Lokendra Singh  
**Email**: qa.lokendra@gmail.com  
**Website**: www.sqamentor.com

---

## 🎉 Summary

**3 Ways to Use**:
1. Add `@pytest.mark.human_like` to test
2. Use `human_behavior` fixture
3. Create `HumanBehaviorSimulator(driver)`

**Control**:
- Command line: `--enable-human-behavior`
- Config: `config/human_behavior.yaml`
- Code: `enabled=True/False`

**When to Use**:
- ✅ Critical flows
- ✅ Demos
- ✅ Security testing
- ❌ CI/CD (unless needed)

---

**Ready to Use! 🚀**
