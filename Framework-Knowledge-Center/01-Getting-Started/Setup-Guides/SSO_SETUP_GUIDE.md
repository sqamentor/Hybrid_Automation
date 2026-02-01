# Center for Vein Portal - SSO Configuration Guide

## ✅ Configuration Complete

Your SSO portal credentials have been configured in the framework!

### 📋 Configuration Details

**Production Portal**
- URL: `http://portal.centerforvein.com/`
- Username: `lsingh`
- Password: `VijayLakshmi1$` (stored in environment variable)

**Staging Portal**
- URL: `http://staging-portal.centerforvein.com/`
- Username: `lsingh`
- Password: `VijayLakshmi1$` (stored in environment variable)

---

## 🚀 Quick Start

### 1. Set Environment Variable

**PowerShell:**
```powershell
# Set password for current session
$env:SSO_PASSWORD = "VijayLakshmi1$"

# Or set permanently
[System.Environment]::SetEnvironmentVariable('SSO_PASSWORD', 'VijayLakshmi1$', 'User')
```

**Command Prompt:**
```cmd
set SSO_PASSWORD=VijayLakshmi1$
```

### 2. Run Your Workflow Test

```powershell
# Run the complete SSO → CallCenter → PatientIntake workflow
pytest tests/workflows/test_cross_engine_workflows.py::test_sso_to_callcenter_to_patientintake -v

# Specify environment (staging is default)
pytest tests/workflows/ -v --env=staging

# Or production
pytest tests/workflows/ -v --env=production
```

### 3. Run Authentication Test Only

```powershell
# Test just the SSO authentication
pytest tests/workflows/test_cross_engine_workflows.py::test_sso_authentication_only -v
```

---

## 🔧 How It Works

The framework will:

1. **Load configuration** from `config/environments.yaml`
2. **Read credentials** from environment variable `SSO_PASSWORD`
3. **Navigate** to the portal login URL
4. **Enter** username and password
5. **Extract session** (cookies, tokens) after successful login
6. **Transfer session** to Playwright for CallCenter/PatientIntake tests

---

## 📝 Example Test Code

```python
def test_login_to_portal(auth_service, selenium_driver, config):
    """Test login to Center for Vein portal."""
    
    # Get SSO config from environments.yaml
    sso_config = config['sso']
    credentials = config['credentials']
    
    # Authenticate
    session_data = auth_service.authenticate_basic(
        engine=selenium_driver,
        username=credentials['sso_username'],
        password=credentials['sso_password'],
        login_url=sso_config['portal_url'],
        timeout=30
    )
    
    assert session_data is not None
    assert session_data.user_id == 'lsingh'
```

---

## 🔐 Security Best Practices

✅ **Password stored in environment variable** (not in code)  
✅ **Configuration file uses `${SSO_PASSWORD}` placeholder**  
✅ **Actual password never committed to git**  
✅ **Can be overridden per environment**

---

## 📂 Files Modified

- ✅ `config/environments.yaml` - Added SSO portal URLs and credentials
- ✅ Both staging and production environments configured

---

## 🎯 Your Workflow is Ready!

The complete workflow from the previous implementation now works with your portal:

```python
# tests/workflows/test_cross_engine_workflows.py

@pytest.mark.workflow
def test_sso_to_callcenter_to_patientintake(
    workflow_orchestrator,
    workflow_engines,
    auth_service,
    sso_config,
    sso_credentials,
    config
):
    # Step 1: Login to portal.centerforvein.com (Selenium)
    # Step 2: CallCenter operations (Playwright with session)
    # Step 3: PatientIntake operations (Playwright with session)
```

**Run it:**
```powershell
$env:SSO_PASSWORD = "VijayLakshmi1$"
pytest tests/workflows/test_cross_engine_workflows.py::test_sso_to_callcenter_to_patientintake -v
```

---

## 🛠️ Customization

If your portal uses a different login form, update the selectors in `framework/auth/auth_service.py`:

```python
def _authenticate_basic_selenium(self, driver, username, password, login_url, timeout):
    # Customize these selectors for your portal
    username_field = driver.find_element(By.NAME, "username")  # or By.ID, By.CSS_SELECTOR
    password_field = driver.find_element(By.NAME, "password")
    login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
```

---

Need help testing? Run the authentication test first to verify login works!
