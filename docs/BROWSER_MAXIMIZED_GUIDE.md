# 🎯 Browser Maximized Window - Implementation Guide

## ✅ IMPLEMENTED SOLUTION

**Status:** ✅ Complete  
**Location:** `conftest.py` (Root level)  
**Approach:** Modern, Dynamic, Reusable, Optimized  

---

## 📋 What Was Changed

### File: `conftest.py`

Added two **session-scoped fixtures** that override pytest-playwright defaults:

1. **`browser_context_args`** - Sets viewport to `None` (uses full window)
2. **`browser_type_launch_args`** - Adds `--start-maximized` launch argument

---

## 🏆 Why This is the BEST Approach

### ✅ **Modern Framework Standards**
- Uses **pytest-playwright's official extension pattern**
- Follows **Playwright best practices**
- Aligns with **pytest fixture override mechanism**

### ✅ **Dynamic & Flexible**
```python
# Works globally for all tests
def test_example(page):
    # Browser automatically maximized ✅

# Can be overridden per test if needed
@pytest.fixture
def browser_context_args():
    return {"viewport": {"width": 1920, "height": 1080}}
```

### ✅ **Reusable & DRY**
- **Zero code duplication** - Configured once, works everywhere
- **Applies to ALL tests** using `page` fixture
- **Session-scoped** - Browser configured once per test session

### ✅ **Highest Optimization**
- **Session scope** - Configuration happens once, not per test
- **No performance overhead** - Native browser feature
- **Cross-browser compatible** - Works with Chromium, Firefox, WebKit

### ✅ **Maintainable**
- **Single source of truth** - One place to change browser settings
- **Clear documentation** - Well-commented for future developers
- **Easy to extend** - Can add more browser args as needed

---

## 🔧 Technical Details

### How It Works

#### 1. `viewport=None` (browser_context_args)
```python
return {
    **browser_context_args,
    "viewport": None,  # Uses full browser window
    "no_viewport": True,  # Disables viewport emulation
}
```

**Default behavior (without this):**
- pytest-playwright uses **1280x720 fixed viewport**
- Good for consistent screenshots, but not maximized

**With viewport=None:**
- Browser uses **actual window size**
- Enables **responsive testing**
- Window adapts to screen resolution

#### 2. `--start-maximized` (browser_type_launch_args)
```python
return {
    **browser_type_launch_args,
    "args": ["--start-maximized"],
}
```

**What it does:**
- Tells Chrome/Chromium to start in maximized state
- Native browser feature (not Playwright simulation)
- Works on Windows, macOS, Linux

**Browser compatibility:**
- ✅ **Chromium/Chrome** - Full support
- ✅ **Firefox** - Uses viewport=None instead
- ✅ **WebKit** - Uses viewport=None instead

---

## 📖 Usage Examples

### Basic Usage (Automatic)
```python
@pytest.mark.bookslot
def test_bookslot(page):
    # Browser automatically opens maximized ✅
    page.goto("https://example.com")
    # Window is already maximized, no extra code needed!
```

### Override Per Test (Custom Viewport)
```python
@pytest.fixture
def browser_context_args():
    """Custom viewport for this specific test"""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "device_scale_factor": 2,
    }

def test_specific_resolution(page, browser_context_args):
    # Uses custom viewport instead of maximized
    page.goto("https://example.com")
```

### Mobile Testing (Override)
```python
@pytest.fixture
def browser_context_args():
    """Simulate iPhone 12"""
    return {
        "viewport": {"width": 390, "height": 844},
        "user_agent": "Mozilla/5.0 (iPhone...)",
        "is_mobile": True,
    }

def test_mobile_view(page, browser_context_args):
    # Uses mobile viewport
    page.goto("https://example.com")
```

---

## 🎨 Configuration Hierarchy

```
┌─────────────────────────────────────────────────┐
│ Global (conftest.py - Session Scope)            │
│ ✅ browser_context_args → viewport=None         │
│ ✅ browser_type_launch_args → --start-maximized │
└─────────────────────────────────────────────────┘
                    ↓ (Can be overridden)
┌─────────────────────────────────────────────────┐
│ Test-specific (Per Test Override)               │
│ @pytest.fixture                                 │
│ def browser_context_args(): ...                 │
└─────────────────────────────────────────────────┘
```

**Result:** Maximum flexibility with sensible defaults!

---

## 🚀 Testing Different Screen Sizes

### While keeping global maximized as default:

```python
# Test Suite: tests/test_responsive.py

@pytest.fixture
def desktop_hd():
    return {"viewport": {"width": 1920, "height": 1080}}

@pytest.fixture
def desktop_4k():
    return {"viewport": {"width": 3840, "height": 2160}}

@pytest.fixture  
def tablet():
    return {"viewport": {"width": 768, "height": 1024}}

@pytest.fixture
def mobile():
    return {"viewport": {"width": 375, "height": 667}}


@pytest.mark.parametrize("device", [
    "desktop_hd", "desktop_4k", "tablet", "mobile"
])
def test_responsive_layout(page, device, request):
    """Test layout across different screen sizes"""
    viewport = request.getfixturevalue(device)
    page.set_viewport_size(**viewport["viewport"])
    page.goto("https://example.com")
    # Test responsive behavior
```

---

## 🔍 Comparison with Other Approaches

### ❌ OLD WAY (Not Recommended)
```python
# In every test file - CODE DUPLICATION!
def test_example(page):
    page.set_viewport_size(1920, 1080)  # Manual, repeated
    page.goto("...")
```

### ❌ SELENIUM WAY (Not Applicable)
```python
# Selenium approach (doesn't work with Playwright)
driver.maximize_window()  # Wrong tool!
```

### ✅ OUR WAY (Best Practice)
```python
# In conftest.py ONCE - Global configuration
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": None}

# In tests - NOTHING needed, works automatically
def test_example(page):
    page.goto("...")  # Already maximized! ✅
```

---

## 📊 Performance Impact

| Approach | Configuration Time | Per-Test Overhead | Memory Impact |
|----------|-------------------|-------------------|---------------|
| **Session-scoped fixtures** | **Once** | **None** | **Minimal** |
| Per-test viewport setting | Every test | High | Moderate |
| Manual resize in test | Every test | Very high | High |

**Winner:** Session-scoped fixtures (Our approach) ✅

---

## 🎓 Advanced Customization

### Add More Browser Arguments
```python
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "args": [
            "--start-maximized",
            "--disable-extensions",      # Faster startup
            "--disable-blink-features=AutomationControlled",  # Stealth
            "--no-sandbox",              # CI/CD environments
        ],
    }
```

### Environment-Based Configuration
```python
import os

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Dynamic based on environment"""
    
    if os.getenv("CI") == "true":
        # Fixed viewport for CI (consistent screenshots)
        return {
            **browser_context_args,
            "viewport": {"width": 1920, "height": 1080},
        }
    else:
        # Maximized for local development
        return {
            **browser_context_args,
            "viewport": None,
        }
```

### Device Emulation (Mobile/Tablet)
```python
from playwright.sync_api import devices

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, request):
    """Use device emulation when requested"""
    
    device_name = request.config.getoption("--device", None)
    
    if device_name:
        device = devices[device_name]
        return {**browser_context_args, **device}
    
    # Default: maximized
    return {**browser_context_args, "viewport": None}
```

---

## 🧪 Verification

### Test It Works
```bash
# Run your test
pytest recorded_tests/bookslot/test_bookslot_complete_workflow.py -v

# Expected: Browser opens in MAXIMIZED window ✅
```

### Check Effective Viewport
```python
def test_check_viewport(page):
    """Verify viewport is not fixed"""
    page.goto("https://example.com")
    viewport = page.viewport_size
    print(f"Viewport: {viewport}")
    # Output: {'width': <screen_width>, 'height': <screen_height>}
```

---

## 📚 Further Reading

- [Playwright Browser Context Docs](https://playwright.dev/python/docs/browser-contexts)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-pytest)
- [Viewport vs Window Size](https://playwright.dev/python/docs/emulation#viewport)
- [Chromium Command Line Switches](https://peter.sh/experiments/chromium-command-line-switches/)

---

## 🎉 Summary

### What You Got:
✅ **Maximized browser** by default for all tests  
✅ **Session-scoped** configuration (optimal performance)  
✅ **Modern pytest-playwright** patterns  
✅ **Flexible** - Can override per test when needed  
✅ **Cross-browser** compatible (Chromium, Firefox, WebKit)  
✅ **Zero code duplication** - DRY principle  
✅ **Industry best practice** - Matches Playwright recommendations  

### Next Steps:
1. ✅ Run your tests - Browser should be maximized
2. ✅ Keep this configuration as your default
3. ✅ Override only when testing specific viewports/devices
4. ✅ Share this pattern across your team

---

**Questions?** Check the comments in `conftest.py` or refer to Playwright docs!
