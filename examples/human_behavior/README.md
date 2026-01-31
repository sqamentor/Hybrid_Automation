# Human Behavior Simulation - Examples

This directory contains practical examples demonstrating the Human Behavior Simulation module.

## 📂 Examples Overview

### Example 1: Basic Usage
**File**: `example_01_basic_usage.py`

Demonstrates the simplest usage with pytest fixtures and markers.

**Run**:
```bash
# With pytest
pytest examples/human_behavior/example_01_basic_usage.py --enable-human-behavior

# Standalone
python examples/human_behavior/example_01_basic_usage.py
```

**Features**:
- Basic typing simulation
- Mouse movements
- Scrolling
- Idle pauses
- Comparison with/without human behavior

---

### Example 2: Form Filling
**File**: `example_02_form_filling.py`

Realistic form filling scenarios with complex fields.

**Run**:
```bash
# With pytest
pytest examples/human_behavior/example_02_form_filling.py -v --enable-human-behavior

# Standalone
python examples/human_behavior/example_02_form_filling.py
```

**Features**:
- Text input with natural typing
- Password fields with thinking pauses
- Dropdown selections
- Checkbox interactions
- Multi-step forms
- Performance comparison

---

### Example 3: Framework Integration
**File**: `example_03_framework_integration.py`

Integration with existing framework components.

**Run**:
```bash
# With pytest
pytest examples/human_behavior/example_03_framework_integration.py -v

# Standalone
python examples/human_behavior/example_03_framework_integration.py
```

**Features**:
- Selenium Engine integration
- Playwright Engine integration
- Page Object Pattern
- Configuration-based behavior
- Standalone functions

---

### Example 4: Advanced E-commerce
**File**: `example_04_advanced_ecommerce.py`

Complete e-commerce user journey with realistic behavior.

**Run**:
```bash
# With pytest
pytest examples/human_behavior/example_04_advanced_ecommerce.py -v --enable-human-behavior --human-behavior-intensity normal

# Standalone
python examples/human_behavior/example_04_advanced_ecommerce.py
```

**Features**:
- Complete shopping journey (10 phases)
- Product browsing and comparison
- Cart management
- Checkout process
- Realistic user hesitations and decisions

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install required packages
pip install selenium pytest pyyaml

# Optional: Install Playwright
pip install playwright
playwright install chromium
```

### Run All Examples

```bash
# Run all examples with pytest
pytest examples/human_behavior/ -v --enable-human-behavior

# Run specific example
pytest examples/human_behavior/example_01_basic_usage.py::test_saucedemo_login_with_human_behavior -v
```

### Run Standalone

```bash
# Each example can run standalone
python examples/human_behavior/example_01_basic_usage.py
python examples/human_behavior/example_02_form_filling.py
python examples/human_behavior/example_03_framework_integration.py
python examples/human_behavior/example_04_advanced_ecommerce.py
```

---

## ⚙️ Configuration

### Command Line Options

```bash
# Enable human behavior
pytest examples/human_behavior/ --enable-human-behavior

# Set intensity
pytest examples/human_behavior/ --human-behavior-intensity minimal
pytest examples/human_behavior/ --human-behavior-intensity normal
pytest examples/human_behavior/ --human-behavior-intensity high

# Disable for specific runs
pytest examples/human_behavior/ --disable-human-behavior

# Combine with other options
pytest examples/human_behavior/ --env staging --test-browser chrome --enable-human-behavior
```

### Using Markers

```python
import pytest

# Enable for specific test
@pytest.mark.human_like
def test_with_behavior():
    pass

# Disable for specific test
@pytest.mark.no_human_behavior
def test_without_behavior():
    pass
```

---

## 📊 Performance Comparison

Run the comparison test to see the difference:

```bash
python examples/human_behavior/example_02_form_filling.py
```

**Typical Results**:
```
⏱️  Execution Time Comparison:
   Normal: 3.45s
   Human-like: 8.72s
   Difference: +5.27s (152.8% slower)
```

The human-like behavior adds realism at the cost of execution time.

---

## 🎯 Use Cases

### When to Use Human Behavior

✅ **Recommended**:
- Security testing (bypass bot detection)
- Demo recordings
- Visual regression testing
- Load testing with realistic patterns
- End-to-end critical flows
- Production-like testing

❌ **Not Recommended**:
- Unit tests
- CI/CD smoke tests (prefer speed)
- Regression suites (unless needed)
- API-only tests

---

## 🔧 Customization

### Modify Timing

Edit `config/human_behavior.yaml`:

```yaml
typing:
  min_delay: 0.05  # Faster typing
  max_delay: 0.15

mouse:
  movement_steps: 4  # Fewer steps = faster

scrolling:
  increment_min: 200  # Larger scrolls
  increment_max: 500
```

### Programmatic Control

```python
from framework.core.utils.human_actions import HumanBehaviorSimulator

# Create simulator with custom settings
simulator = HumanBehaviorSimulator(driver, enabled=True)

# Access config
config = simulator.config
config._config['typing']['min_delay'] = 0.05

# Or disable specific categories
config._config['scrolling']['enabled'] = False
```

---

## 📝 Test Sites Used

All examples use publicly available test sites:

1. **SauceDemo**: https://www.saucedemo.com/
   - E-commerce demo site
   - Credentials: `standard_user` / `secret_sauce`

2. **Selenium Web Form**: https://www.selenium.dev/selenium/web/web-form.html
   - Form testing demo
   - No authentication required

---

## 🐛 Troubleshooting

### Issue: ChromeDriver not found

```bash
# Install webdriver-manager
pip install webdriver-manager

# Or download manually and set path
export PATH=$PATH:/path/to/chromedriver
```

### Issue: Human behavior not working

```python
# Check if enabled
from framework.core.utils.human_actions import get_behavior_config
config = get_behavior_config()
print(f"Enabled: {config.is_enabled()}")

# Force enable
simulator = HumanBehaviorSimulator(driver, enabled=True)
```

### Issue: Tests too slow

```bash
# Use minimal intensity
pytest --human-behavior-intensity minimal

# Or disable completely
pytest --disable-human-behavior
```

---

## 📚 Documentation

For complete documentation, see:
- [Full Guide](../../docs/HUMAN_BEHAVIOR_GUIDE.md)
- [Configuration](../../config/human_behavior.yaml)
- [Source Code](../../framework/core/utils/human_actions.py)

---

## 🆘 Support

**Author**: Lokendra Singh  
**Email**: qa.lokendra@gmail.com  
**Website**: www.sqamentor.com

---

## 📝 Notes

- Examples use Chrome by default (change to Firefox if needed)
- All examples are self-contained and can run independently
- Configuration changes affect all tests
- Use markers for fine-grained control

---

**Happy Testing! 🎉**
