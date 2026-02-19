# URL Query String Testing - Quick Reference

**For:** Bookslot Project & All Projects  
**Pattern:** Data-Driven Hybrid Approach (Manual + Auto)  
**Date:** February 19, 2026  
**Version:** 2.0 (REVISED)

---

## 🎯 TL;DR - Recommended Approach (UPDATED)

**For Bookslot & Most Projects:** Use **Data-Driven Hybrid Approach**

### Primary Mode: Manual Test Data (Recommended for most tests)
```
1. Create Excel/CSV file with test data (workflow IDs, query params)
2. QA team adds test cases (no coding needed)
3. System loads test data and builds URLs
4. Run pytest with actual test data
```

### Secondary Mode: Auto-Generation (Fallback when needed)
```
1. Create YAML config with workflow IDs and query params
2. Load config in pytest fixture
3. Generate combinations automatically
4. Run parametrized tests with generated combinations
```

**Benefits:**
- ✅ QA team can create tests using Excel (no coding)
- ✅ Supports 4 data formats (Excel, CSV, JSON, YAML)
- ✅ Flexible: Use manual data OR auto-generate
- ✅ Future-proof: Supports multiple URL formats
- ✅ Comprehensive validation (HTTP 200 + elements + no errors)

---

## 🚀 Quick Start (3 Steps)

### For QA Team (Manual Mode - Excel)

**Step 1:** Create test data file `test_data/bookslot/bookslot_testdata.xlsx`

| workflow_id | environment | language | source | patient_type | expected_result |
|-------------|-------------|----------|--------|--------------|-----------------|
| WF001       | staging     | en       | web    | new          | success         |
| WF002       | staging     | es       | mobile | returning    | success         |

**Step 2:** Write test (pytest will auto-load data)

```python
# tests/bookslot/test_bookslot_urls.py

def test_booking_workflows(url_test_case):
    """Test all booking workflows from Excel"""
    # url_test_case is auto-loaded from Excel
    # url_test_case.final_url is already built
    # Just navigate and test
    page.goto(url_test_case.final_url)
    assert page.is_visible("h1")
```

**Step 3:** Run tests

```bash
pytest tests/bookslot/ --env=staging
```

**That's it!** No YAML config needed. QA team can add more rows to Excel anytime.

---

### For Developers (Auto Mode - YAML Config)

**Step 1:** Create config file `config/url_testing/bookslot_urls.yaml`

```yaml
project: bookslot
environments:
  staging:
    base_url: "https://bookslot-staging.centerforvein.com"
    workflow_ids:
      - WF001
      - WF002
    query_parameters:
      language:
        values: [en, es]
      source:
        values: [web, mobile]
```

**Step 2:** Write test

```python
# tests/bookslot/test_bookslot_auto.py

@pytest.mark.url_mode("auto")  # Force auto-generation
def test_all_combinations(url_test_case):
    """Test all generated combinations"""
    page.goto(url_test_case.final_url)
    assert page.is_visible("h1")
```

**Step 3:** Run tests

```bash
pytest tests/bookslot/ --env=staging --mode=auto
```

---

## 📁 Recommended Directory Structure (Updated)

```
Hybrid_Automation/
├── test_data/                           ← PRIMARY DATA SOURCE
│   └── bookslot/
│       ├── bookslot_testdata.xlsx       # Excel (QA team edits this)
│       ├── bookslot_testdata.csv        # CSV alternative
│       ├── bookslot_testdata.json       # JSON alternative
│       └── bookslot_testdata.yaml       # YAML alternative
│
├── config/
│   └── url_testing/                     ← SECONDARY (FALLBACK)
│       ├── bookslot_urls.yaml           # Auto-generation config
│       └── other_project_urls.yaml
│
├── framework/
│   └── core/
│       └── url_testing/
│           ├── __init__.py
│           ├── models.py                # URLTestCase, ValidationResult
│           ├── data_manager.py          # Mode detection & routing (NEW)
│           ├── test_data_loader.py      # Load Excel/CSV/JSON/YAML (NEW)
│           ├── config_generator.py      # Auto-generation (fallback)
│           ├── url_builder.py           # Build URLs
│           └── url_validator.py         # Comprehensive validation
│
├── tests/
│   └── bookslot/
│       ├── test_bookslot_urls.py        # Tests using manual data
│       ├── test_bookslot_auto.py        # Tests using auto-generation
│       └── conftest.py                  # Fixtures
│
└── test_data/
    └── templates/
        ├── url_testdata_template.xlsx   # Empty template for QA
        ├── url_testdata_template.csv
        └── url_testdata_template.yaml
```

---

## 📊 Test Data File Formats (Manual Mode)

### Excel Format (.xlsx) - RECOMMENDED FOR QA TEAM

```excel
# test_data/bookslot/bookslot_testdata.xlsx

| workflow_id | environment | language | source | patient_type | insurance_verified | utm_campaign | expected_result | description              |
|-------------|-------------|----------|--------|--------------|-------------------|--------------|-----------------|--------------------------|
| WF001       | staging     | en       | web    | new          | true              | summer_promo | success         | New patient summer promo |
| WF002       | staging     | es       | mobile | returning    | false             | default      | success         | Returning mobile user    |
| WF003       | staging     | en       | tablet | vip          | true              | urgent_care  | success         | VIP urgent care          |
| WF004       | production  | en       | web    | new          | true              | default      | success         | Prod new patient         |
| WF005       | production  | es       | referral| returning   | false             | wellness    | success         | Prod referral patient    |
```

**How to Create:**
1. Open Excel
2. Create headers: `workflow_id`, `environment`, `language`, `source`, etc.
3. Add one row per test case
4. Save as `bookslot_testdata.xlsx` in `test_data/bookslot/`
5. Done! System auto-loads it

---

### CSV Format (.csv) - GOOD FOR VERSION CONTROL

```csv
# test_data/bookslot/bookslot_testdata.csv

workflow_id,environment,language,source,patient_type,insurance_verified,utm_campaign,expected_result,description
WF001,staging,en,web,new,true,summer_promo,success,"New patient summer promo"
WF002,staging,es,mobile,returning,false,default,success,"Returning mobile user"
WF003,staging,en,tablet,vip,true,urgent_care,success,"VIP urgent care"
WF004,production,en,web,new,true,default,success,"Prod new patient"
WF005,production,es,referral,returning,false,wellness,success,"Prod referral patient"
```

**Advantages:**
- Easy to track changes in Git
- Can edit in any text editor
- Opens in Excel too

---

### JSON Format (.json) - FOR API-DRIVEN TEST DATA

```json
{
  "test_cases": [
    {
      "workflow_id": "WF001",
      "environment": "staging",
      "query_params": {
        "language": "en",
        "source": "web",
        "patient_type": "new",
        "insurance_verified": "true",
        "utm_campaign": "summer_promo"
      },
      "expected_result": "success",
      "description": "New patient summer promo"
    },
    {
      "workflow_id": "WF002",
      "environment": "staging",
      "query_params": {
        "language": "es",
        "source": "mobile",
        "patient_type": "returning",
        "insurance_verified": "false",
        "utm_campaign": "default"
      },
      "expected_result": "success",
      "description": "Returning mobile user"
    }
  ]
}
```

**Advantages:**
- Structured data
- API-friendly
- Easy to parse programmatically

---

### YAML Format (.yaml) - FOR HUMAN-READABLE TEST DATA

```yaml
# test_data/bookslot/bookslot_testdata.yaml

test_cases:
  - workflow_id: WF001
    environment: staging
    query_params:
      language: en
      source: web
      patient_type: new
      insurance_verified: true
      utm_campaign: summer_promo
    expected_result: success
    description: "New patient summer promo"
    
  - workflow_id: WF002
    environment: staging
    query_params:
      language: es
      source: mobile
      patient_type: returning
      insurance_verified: false
      utm_campaign: default
    expected_result: success
    description: "Returning mobile user"
```

**Advantages:**
- Human-readable
- Supports comments
- Clean syntax

---

## 📋 YAML Config Format (Auto Mode - Fallback)

### Minimal Example (Start Here)

```yaml
# config/url_testing/bookslot_urls.yaml

project: bookslot

environments:
  staging:
    base_url: "https://bookslot-staging.centerforvein.com"
    
    # Define your workflow IDs
    workflow_ids:
      - WF_STAGE_001
      - WF_STAGE_002
      - WF_STAGE_003
    
    # Define your query parameters
    query_parameters:
      language:
        values: [en, es]
      
      source:
        values: [web, mobile]
      
      patient_type:
        values: [new, returning]

# Optional: Strategy (default is all combinations)
combination_rules:
  strategy: cartesian_product
  max_combinations: 1000

# This generates: 3 workflows × 2 languages × 2 sources × 2 patient_types = 24 URLs
```

### Full Example (With All Features)

```yaml
# config/url_testing/bookslot_urls.yaml

project: bookslot
version: "2.0"

environments:
  staging:

# 6 Workflow IDs (as required)
workflow_ids:
  - id: WF_STAGE_001
    name: "New Patient Consultation"
    enabled: true
    
  - id: WF_STAGE_002
    name: "Follow-up Appointment"
    enabled: true
    
  - id: WF_STAGE_003
    name: "Emergency Consultation"
    enabled: true
    
  - id: WF_STAGE_004
    name: "Video Consultation"
    enabled: true
    
  - id: WF_STAGE_005
    name: "Lab Results Review"
    enabled: false  # Skip this one
    
  - id: WF_STAGE_006
    name: "Prescription Renewal"
    enabled: true

# Query Parameters (4+ as required)
query_parameters:
  language:
    values: [en, es, fr]
    required: false
    description: "UI language"
    
  source:
    values: [web, mobile, tablet, referral]
    required: false
    
  patient_type:
    values: [new, returning, vip]
    required: true
    
  insurance_verified:
    values: ["true", "false"]
    required: false
    
  utm_campaign:
    values: [summer_promo, default, urgent_care, wellness_check]
    required: false
    
  appointment_priority:
    values: [normal, urgent, emergency]
    required: false

# Advanced: Dependencies
dependencies:
  - if: "appointment_priority=emergency"
    then: "source=web"
    reason: "Emergency must be web-initiated"
    
  - if: "patient_type=vip"
    then: "insurance_verified=true"
    reason: "VIP patients pre-verified"

# Advanced: Exclusions
exclusions:
  - parameters: ["source=mobile", "patient_type=vip"]
    reason: "VIP patients use desktop only"
    
  - parameters: ["utm_campaign=default", "appointment_priority=emergency"]
    reason: "Emergency appointments not from default campaign"

# Limits (optional)
max_combinations: 500
strategy: cartesian_product

# Test configuration
test_config:
  timeout_per_test: 30
  retry_failed: true
  retry_count: 2
  parallel: true
  max_workers: 4
```

---

## 🐍 Python Implementation Examples

### Example 1: Simple Test with All Combinations

```python
# tests/bookslot/test_all_workflow_urls.py

import pytest
import yaml
from pathlib import Path
from itertools import product

def load_url_config(environment="staging"):
    """Load URL configuration for given environment"""
    config_file = Path(f"config/url_configs/bookslot_{environment}.yaml")
    with open(config_file) as f:
        return yaml.safe_load(f)

def generate_url_combinations(config):
    """Generate all URL combinations from config"""
    base_url = config['base_url']
    workflow_ids = [wf if isinstance(wf, str) else wf['id'] 
                    for wf in config['workflow_ids']
                    if isinstance(wf, str) or wf.get('enabled', True)]
    
    # Extract parameter values
    params = {}
    for param_name, param_config in config['query_parameters'].items():
        if isinstance(param_config, list):
            params[param_name] = param_config
        else:
            params[param_name] = param_config['values']
    
    # Generate all combinations
    urls = []
    param_names = list(params.keys())
    param_values = [params[name] for name in param_names]
    
    for workflow_id in workflow_ids:
        for combination in product(*param_values):
            query_string = "&".join(
                f"{name}={value}" 
                for name, value in zip(param_names, combination)
            )
            url = f"{base_url}?workflow_id={workflow_id}&{query_string}"
            test_id = f"wf={workflow_id}_" + "_".join(
                f"{name}={value}" 
                for name, value in zip(param_names, combination)
            )
            urls.append((url, test_id))
    
    return urls

@pytest.fixture(scope="module")
def url_combinations(environment):
    """Generate all URL combinations for testing"""
    config = load_url_config(environment)
    return generate_url_combinations(config)

@pytest.mark.parametrize("url,test_id", 
    pytest.lazy_fixture("url_combinations"),
    ids=lambda x: x[1])  # Use test_id for reporting
def test_workflow_url_loads(url, test_id, page):
    """Test that workflow URL loads successfully"""
    print(f"\n🔗 Testing: {url}")
    
    # Navigate to URL
    response = page.goto(url)
    
    # Validate
    assert response.status == 200, f"Failed to load: {url}"
    assert page.is_visible("h1"), "Page content not loaded"
    
    print(f"✅ Passed: {test_id}")
```

### Example 2: Filtered Tests (Emergency Only)

```python
# tests/bookslot/test_emergency_workflows.py

import pytest

@pytest.fixture(scope="module")
def emergency_url_combinations(environment):
    """Generate only emergency priority URL combinations"""
    config = load_url_config(environment)
    all_urls = generate_url_combinations(config)
    
    # Filter for emergency only
    return [
        (url, test_id) 
        for url, test_id in all_urls 
        if "appointment_priority=emergency" in url
    ]

@pytest.mark.parametrize("url,test_id", 
    pytest.lazy_fixture("emergency_url_combinations"),
    ids=lambda x: x[1])
def test_emergency_workflow_performance(url, test_id, page):
    """Emergency workflows must load in < 2 seconds"""
    import time
    
    start = time.time()
    page.goto(url)
    load_time = time.time() - start
    
    assert load_time < 2.0, f"Emergency workflow too slow: {load_time:.2f}s"
    print(f"✅ Emergency workflow loaded in {load_time:.2f}s")
```

### Example 3: Custom URL Builder (No Config)

```python
# tests/bookslot/test_custom_urls.py

def build_custom_url(base_url, workflow_id, **params):
    """Build URL with query parameters"""
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{base_url}?workflow_id={workflow_id}&{query_string}"

def test_vip_patient_flow(page, base_url):
    """Test VIP patient with specific parameters"""
    url = build_custom_url(
        base_url,
        workflow_id="WF_STAGE_002",
        patient_type="vip",
        insurance_verified="true",
        language="en",
        source="web"
    )
    
    page.goto(url)
    assert page.is_visible("text=VIP Fast Track")
```

---

## 🚀 Quick Start Guide

### Step 1: Create Configuration File

```bash
# Create directory
mkdir -p config/url_configs

# Create staging config
cat > config/url_configs/bookslot_staging.yaml << 'EOF'
project: bookslot
environment: staging
base_url: "https://bookslot-staging.centerforvein.com"

workflow_ids:
  - WF_STAGE_001
  - WF_STAGE_002

query_parameters:
  language: [en, es]
  source: [web, mobile]

strategy: cartesian_product
EOF
```

### Step 2: Create Test File

```bash
# Create test file
cat > tests/bookslot/test_workflow_urls.py << 'EOF'
import pytest
import yaml
from pathlib import Path
from itertools import product

def load_url_config(environment="staging"):
    config_file = Path(f"config/url_configs/bookslot_{environment}.yaml")
    with open(config_file) as f:
        return yaml.safe_load(f)

def generate_url_combinations(config):
    base_url = config['base_url']
    workflow_ids = config['workflow_ids']
    params = config['query_parameters']
    
    urls = []
    for workflow_id in workflow_ids:
        param_names = list(params.keys())
        param_values = [params[name] for name in param_names]
        
        for combination in product(*param_values):
            query_string = "&".join(
                f"{name}={value}" 
                for name, value in zip(param_names, combination)
            )
            url = f"{base_url}?workflow_id={workflow_id}&{query_string}"
            test_id = f"wf={workflow_id}_" + "_".join(combination)
            urls.append((url, test_id))
    
    return urls

@pytest.fixture(scope="module")
def url_combinations():
    config = load_url_config("staging")
    return generate_url_combinations(config)

@pytest.mark.parametrize("url,test_id", 
    pytest.lazy_fixture("url_combinations"),
    ids=lambda x: x[1])
def test_url_loads(url, test_id, page):
    response = page.goto(url)
    assert response.status == 200
EOF
```

### Step 3: Run Tests

```bash
# Run all URL combination tests
pytest tests/bookslot/test_workflow_urls.py --env=staging -v

# Expected output:
# test_url_loads[wf=WF_STAGE_001_en_web] PASSED
# test_url_loads[wf=WF_STAGE_001_en_mobile] PASSED
# test_url_loads[wf=WF_STAGE_001_es_web] PASSED
# test_url_loads[wf=WF_STAGE_001_es_mobile] PASSED
# test_url_loads[wf=WF_STAGE_002_en_web] PASSED
# test_url_loads[wf=WF_STAGE_002_en_mobile] PASSED
# test_url_loads[wf=WF_STAGE_002_es_web] PASSED
# test_url_loads[wf=WF_STAGE_002_es_mobile] PASSED
# ======================== 8 passed in 2.5s ========================
```

---

## 📊 Comparison Matrix

| Approach | Pros | Cons | When to Use |
|----------|------|------|-------------|
| **Hardcoded Loops** | Simple, quick | Not maintainable | Never (anti-pattern) |
| **Pytest Parametrize** | Easy to understand | Limited flexibility | Simple cases (< 3 params) |
| **Config-Driven (YAML)** | ✅ Maintainable<br>✅ Environment-aware<br>✅ Reusable | Requires setup | ✅ **Recommended for Bookslot** |
| **Factory Pattern** | ✅ Highly scalable<br>✅ Advanced features | More complex | Large projects (> 100 combinations) |
| **Builder Pattern** | ✅ Fluent API<br>✅ Dynamic | More code | Custom/dynamic scenarios |

---

## 🎯 Recommendations by Scenario

### For Bookslot (Your Case)

**Scenario:** 6 workflow IDs × 4+ query params × 2 environments = 500+ combinations

**Recommended:** **Config-Driven Factory Pattern**

**Rationale:**
- ✅ Handles 500+ combinations easily
- ✅ Environment-specific configs (staging vs production)
- ✅ Easy to add/remove parameters (just edit YAML)
- ✅ Reusable for future projects
- ✅ Team-friendly (non-coders can edit YAML)

**Implementation Time:** 1-2 days

---

## 📈 Scalability Analysis

### Combination Explosion

```
Scenario 1: Basic
- 2 workflow IDs
- 2 languages
- 2 sources
= 2 × 2 × 2 = 8 URLs ✅ Manageable

Scenario 2: Bookslot Current
- 6 workflow IDs
- 4 query params with 2-3 values each
= 6 × 3 × 3 × 3 × 3 = 486 URLs ⚠️ Need smart approach

Scenario 3: Bookslot Full
- 6 workflow IDs
- 6 query params with 3-4 values each
= 6 × 4 × 4 × 4 × 3 × 3 × 3 = 41,472 URLs ❌ Too many!

Solution: Use pairwise testing or dependencies to reduce
```

### Optimization Strategies

1. **Dependencies**: Reduce invalid combinations
2. **Exclusions**: Skip known invalid states
3. **Pairwise Testing**: Test parameter pairs, not all combinations
4. **Risk-Based**: Test high-risk combinations first

---

## ✅ Final Recommendation

### For Bookslot Project

**Use:** Config-Driven Factory Pattern with YAML

**Steps:**
1. Create `config/url_configs/bookslot_staging.yaml`
2. Define 6 workflow IDs
3. Define 4+ query parameters
4. Add dependencies/exclusions as needed
5. Generate combinations in pytest fixture
6. Run parametrized tests

**Timeline:**
- Day 1: Create YAML configs
- Day 2: Implement generator function
- Day 3: Write parametrized tests
- Day 4: Validate all combinations
- Day 5: Optimize and document

**Expected Result:**
- 500-1000 URL combinations tested automatically
- Easy to maintain (edit YAML, not code)
- Environment-aware (staging vs production)
- Reusable for other projects

---

## 📞 Next Steps

1. **Review** the full design document: `URL_QUERY_STRING_TESTING_DESIGN.md`
2. **Decide** on approach (Config-Driven Factory recommended)
3. **Create** sample YAML config for Bookslot
4. **Implement** basic URL generator
5. **Validate** with 2-3 workflow IDs first
6. **Scale** to full 6 workflow IDs + all params

---

**Questions?** This is the foundation. Let's discuss which approach fits best before implementation.
