# 🎯 QUICK REFERENCE - DYNAMIC CONFIGURATION GUIDE

## 🔍 Where Configuration Lives

| Type | Location | Purpose |
|------|----------|---------|
| **URLs & Endpoints** | `config/projects.yaml` | All environment-specific URLs |
| **Settings & Features** | `config/environments.yaml` | Framework behavior settings |
| **Secrets & Keys** | `.env` (create from `env.example`) | API keys, passwords |
| **Database Config** | `config/projects.yaml` or `.env` | DB connections |

---

## ✅ HOW TO RUN TESTS

### Basic Commands
```bash
# Staging (default)
pytest pages/bookslot/bookslots_basicinfo.py

# Production
pytest --env=production pages/bookslot/bookslots_basicinfo.py

# Recorded tests
pytest recorded_tests/bookslot/ --env=staging
pytest recorded_tests/bookslot/ --env=production
```

### Interactive CLI
```bash
python run_tests_cli.py

# Then select:
# 1. Quick Run → pick test → pick environment
# 2. Custom Run → advanced options → pick environment  
# 3. Scenario → pre-configured → pick environment
```

---

## 📝 HOW TO WRITE TESTS

### Page Object (uses fixture)
```python
import pytest

@pytest.mark.bookslot
def test_bookslot_page(page, multi_project_config):
    # Get URL from fixture
    bookslot_url = multi_project_config['bookslot']['ui_url']
    
    # Navigate
    page.goto(f"{bookslot_url}/basic-info")
    
    # Test your logic
    # ...
```

### Page Object Class (requires parameter)
```python
from pages.bookslot.bookslots_basicinfo import BookSlotBasicInfoPage

def test_with_page_object(page, multi_project_config):
    # CORRECT: Pass URL explicitly
    base_url = multi_project_config['bookslot']['ui_url']
    bookslot_page = BookSlotBasicInfoPage(page, base_url)
    
    # Use page object
    bookslot_page.navigate()
```

### Recorded Test (add fixture)
```python
def test_example(page: Page, multi_project_config) -> None:
    """Add multi_project_config to any recorded test"""
    base_url = multi_project_config['bookslot']['ui_url']
    
    # Replace all hardcoded URLs
    page.goto(f"{base_url}/basic-info")
    page.goto(f"{base_url}/eventtype")
    page.goto(f"{base_url}/success")
```

---

## 🔧 HOW TO ADD NEW ENVIRONMENTS

### 1. Edit projects.yaml
```yaml
projects:
  bookslot:
    environments:
      staging:
        ui_url: "https://bookslot-staging.centerforvein.com"
      production:
        ui_url: "https://bookslots.centerforvein.com"
      qa:  # NEW ENVIRONMENT
        ui_url: "https://bookslot-qa.centerforvein.com"
        api_url: "https://api-qa.centerforvein.com"
```

### 2. Update conftest.py (if new choice needed)
```python
def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="staging",
        choices=["dev", "staging", "production", "qa", "prod"],  # Add "qa"
        help="Environment to run tests against"
    )
```

### 3. Run tests
```bash
pytest --env=qa pages/bookslot/bookslots_basicinfo.py
```

---

## 🆕 HOW TO ADD NEW PROJECTS

### 1. Add to projects.yaml
```yaml
projects:
  # ... existing projects ...
  
  newproject:  # NEW PROJECT
    name: "New Project Name"
    description: "Project description"
    
    url_patterns:
      - "newproject.*"
      - ".*newproject.*"
    
    environments:
      staging:
        ui_url: "https://newproject-staging.example.com"
        api_url: "https://api-staging-newproject.example.com"
      production:
        ui_url: "https://newproject.example.com"
        api_url: "https://api-newproject.example.com"
    
    paths:
      pages: "pages/newproject"
      test_data: "test_data/newproject"
```

### 2. Create test using fixture
```python
def test_new_project(page, multi_project_config):
    # Access new project config
    newproject_url = multi_project_config['newproject']['ui_url']
    page.goto(newproject_url)
```

---

## ❌ WHAT NOT TO DO

### ❌ DON'T Hardcode URLs
```python
# BAD - Hardcoded
page.goto("https://bookslot-staging.centerforvein.com")

# GOOD - Dynamic
base_url = multi_project_config['bookslot']['ui_url']
page.goto(base_url)
```

### ❌ DON'T Use Fallbacks
```python
# BAD - Silent fallback
base_url = base_url or "https://hardcoded-url.com"

# GOOD - Explicit error
if not base_url:
    raise ValueError("base_url is required!")
```

### ❌ DON'T Commit Secrets
```bash
# Add to .gitignore
.env
.env.local
*.env
!env.example  # Keep template
```

---

## 🔑 ENVIRONMENT VARIABLES (.env)

### Create your .env file
```bash
# Copy template
cp env.example .env

# Edit .env with your values
# NOTE: .env is in .gitignore - never commit it!
```

### What goes in .env
```env
# AI Keys (optional)
OPENAI_API_KEY=sk-your-actual-key
ANTHROPIC_API_KEY=sk-ant-your-key

# Override environment
TEST_ENV=production  # Override default

# Database (if needed)
DB_PASSWORD=your-db-password

# Feature flags
ENABLE_AI_VALIDATION=true
ENABLE_DB_VALIDATION=false
```

---

## 🐛 TROUBLESHOOTING

### Error: "No configuration found for environment"
**Problem:** projects.yaml missing or environment not configured  
**Solution:** 
1. Check `config/projects.yaml` exists
2. Verify environment section exists (staging, production)
3. Check YAML syntax is correct

### Error: "base_url is required"
**Problem:** Page object created without URL  
**Solution:**
```python
# Add multi_project_config fixture
def test_example(page, multi_project_config):
    base_url = multi_project_config['bookslot']['ui_url']
    page_obj = BookSlotBasicInfoPage(page, base_url)
```

### Tests ignore --env parameter
**Problem:** Hardcoded URLs in test  
**Solution:** Replace all `page.goto("https://...")` with dynamic URLs

### CLI shows wrong URLs
**Problem:** Cached old version  
**Solution:** Restart Python terminal, run `python run_tests_cli.py` again

---

## 📚 KEY FILES

| File | Purpose |
|------|---------|
| `config/projects.yaml` | **All environment URLs** |
| `conftest.py` | Loads config, provides `multi_project_config` fixture |
| `env.example` | Template for secrets |
| `.env` | Your actual secrets (don't commit!) |
| `run_tests_cli.py` | Interactive test runner |
| `DEEP_AUDIT_REPORT.md` | Detailed audit findings |
| `AUDIT_COMPLETE_SUMMARY.md` | Complete summary of changes |
| `validate_no_hardcoding.py` | Validation script |

---

## 🎯 COMMON WORKFLOWS

### Recording a New Test
```bash
# 1. Record test (will save with hardcoded URLs)
python record_cli.py workflow --url https://bookslot-staging.centerforvein.com --name my_test

# 2. Edit recorded test to add fixture
# Change: def test_example(page: Page) -> None:
# To:     def test_example(page: Page, multi_project_config) -> None:

# 3. Replace hardcoded URLs
# Change: page.goto("https://bookslot-staging.centerforvein.com/basic-info")
# To:     base_url = multi_project_config['bookslot']['ui_url']
#         page.goto(f"{base_url}/basic-info")

# 4. Run on any environment
pytest recorded_tests/bookslot/my_test.py --env=production
```

### Updating URLs (One Place Only!)
```yaml
# Edit config/projects.yaml
projects:
  bookslot:
    environments:
      staging:
        ui_url: "https://NEW-staging-url.com"  # Change here
      production:
        ui_url: "https://NEW-production-url.com"  # Change here

# That's it! All tests, CLI, everything updates automatically
```

---

## ✅ VERIFICATION

```bash
# Quick check everything works
python validate_no_hardcoding.py

# Expected: All checks pass ✅
```

---

**Need Help?** Check `DEEP_AUDIT_REPORT.md` or `AUDIT_COMPLETE_SUMMARY.md` for details.
