# Configuration Structure Guide

## 📁 Configuration Files Overview

Your automation framework uses **TWO main configuration files** with distinct purposes:

### 1. **`config/environments.yaml`** - Framework-Level Settings
**Purpose:** Global framework configuration for different environments

**Contains:**
- ✅ **Database configurations** (host, port, credentials)
- ✅ **Test user accounts** (credentials per environment)
- ✅ **Browser settings** (headless, slow_mo, video, tracing)
- ✅ **Timeouts** (page_load, element_wait, API, database)
- ✅ **Retry configuration** (max_attempts, delay)
- ✅ **Logging settings** (level, file paths)
- ✅ **Global settings** (reporting, screenshots, AI providers)

**Environments:** `staging`, `production` only

**When to modify:**
- Change database credentials
- Update timeout values
- Modify browser behavior
- Configure AI providers
- Adjust logging levels

---

### 2. **`config/projects.yaml`** - Application URLs
**Purpose:** Project-specific URLs and settings for multi-application support

**Contains:**
- ✅ **Application URLs** per project (bookslot, callcenter, patientintake)
- ✅ **Environment-specific URLs** (staging, production)
- ✅ **API URLs** per project
- ✅ **Project metadata** (team, contact, description)
- ✅ **URL pattern matching** (for auto-detection)

**Projects:** `bookslot`, `callcenter`, `patientintake`

**When to modify:**
- Add new applications/projects
- Update production/staging URLs
- Add new environments for specific projects
- Change team ownership

---

## 🔄 How They Work Together

```
┌─────────────────────────────────┐
│   environments.yaml             │
│   (Framework Settings)          │
│                                 │
│   ├─ staging                   │
│   │   ├─ database config       │
│   │   ├─ browser settings      │
│   │   ├─ timeouts             │
│   │   └─ logging               │
│   │                             │
│   └─ production                 │
│       ├─ database config       │
│       ├─ browser settings      │
│       ├─ timeouts              │
│       └─ logging               │
└─────────────────────────────────┘
                ▼
┌─────────────────────────────────┐
│   projects.yaml                 │
│   (Application URLs)            │
│                                 │
│   ├─ bookslot                  │
│   │   ├─ staging:              │
│   │   │   └─ ui_url: https://bookslot-staging...
│   │   └─ production:           │
│   │       └─ ui_url: https://bookslots...
│   │                             │
│   ├─ callcenter                │
│   └─ patientintake             │
└─────────────────────────────────┘
```

---

## 🎯 Configuration Priority

```python
Test Execution
    ↓
1. Load framework settings from environments.yaml (database, timeouts, etc.)
    ↓
2. Load project URLs from projects.yaml (UI/API URLs)
    ↓
3. Apply command-line overrides (--env, --headless, etc.)
    ↓
4. Execute tests with merged configuration
```

---

## 📝 Examples

### Running Tests with Configuration

```bash
# Staging environment (bookslot project)
pytest tests/ --env=staging

# Production with specific browser
pytest tests/ --env=production --test-browser=firefox

# Staging with headless mode
pytest tests/ --env=staging --headless
```

### Accessing Configuration in Code

```python
from config.settings import SettingsManager

settings = SettingsManager()

# Get project URL
bookslot_config = settings.get_project_config('bookslot', 'staging')
ui_url = bookslot_config['ui_url']
# Result: https://bookslot-staging.centerforvein.com

# Get environment settings
env_config = settings.get_environment_config('staging')
db_host = env_config['database']['primary']['host']
timeout = env_config['timeouts']['page_load']
```

---

## ✅ Current Configuration Status

| Environment | Status | Usage |
|------------|--------|-------|
| `staging` | ✅ Active | Pre-production testing |
| `production` | ✅ Active | Read-only smoke tests |
| ~~`dev`~~ | ❌ Removed | Not needed |
| ~~`ci`~~ | ❌ Removed | Not needed |

| Project | Staging URL | Production URL |
|---------|-------------|----------------|
| `bookslot` | https://bookslot-staging.centerforvein.com | https://bookslots.centerforvein.com |
| `callcenter` | https://staging-callcenter.centerforvein.com | https://callcenter.centerforvein.com |
| `patientintake` | https://staging-patientintake.centerforvein.com | https://patientintake.centerforvein.com |

---

## 🔧 Maintenance

### Adding a New Project

Edit `config/projects.yaml`:

```yaml
projects:
  newproject:
    name: "New Project Name"
    description: "Project description"
    
    environments:
      staging:
        ui_url: "https://staging-newproject.example.com"
        api_url: "https://api-staging-newproject.example.com"
      production:
        ui_url: "https://newproject.example.com"
        api_url: "https://api-newproject.example.com"
    
    paths:
      pages: "pages/newproject"
      recorded_tests: "recorded_tests/newproject"
      test_data: "test_data/newproject"
```

### Updating Database Credentials

Edit `config/environments.yaml`:

```yaml
environments:
  staging:
    database:
      primary:
        host: "new-staging-db.example.com"
        username: "${DB_STAGING_USERNAME}"
        password: "${DB_STAGING_PASSWORD}"
```

### Modifying Timeouts

Edit `config/environments.yaml`:

```yaml
environments:
  staging:
    timeouts:
      page_load: 45000  # Increase to 45 seconds
      element_wait: 15000
```

---

## 🚨 Important Notes

1. **Never hardcode URLs in test code** - Always use `projects.yaml`
2. **Database credentials use environment variables** - Set in `.env` file
3. **Production is read-only** - Write operations are blocked
4. **Both files are required** - Framework won't work with just one
5. **HTML reports read from projects.yaml** - Automatic URL detection

---

## 📊 Benefits of This Structure

✅ **Separation of Concerns**
   - Framework settings (timeouts, DB) separate from app URLs
   
✅ **Multi-Project Support**
   - Single framework tests multiple applications
   
✅ **Environment Flexibility**
   - Easy switching between staging and production
   
✅ **No URL Hardcoding**
   - All URLs centrally managed
   
✅ **Team Scalability**
   - Each project has team ownership info

---

**Last Updated:** January 29, 2026  
**Author:** QA Automation Framework Team
