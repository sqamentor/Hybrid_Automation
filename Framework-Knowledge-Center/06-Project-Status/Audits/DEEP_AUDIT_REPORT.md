# DEEP AUDIT REPORT - Framework Hardcoded Values
**Date:** January 27, 2026  
**Auditor:** GitHub Copilot  
**Scope:** Complete framework analysis for hardcoded values

---

## EXECUTIVE SUMMARY

### ✅ **GOOD NEWS:**
- Projects.yaml is properly configured with environment-specific URLs
- Settings.py correctly loads configurations dynamically
- Database credentials NOT hardcoded in production code
- Most framework core files use dynamic configuration

### ❌ **CRITICAL ISSUES FOUND:**

#### 1. **RECORDED TESTS - HIGH PRIORITY**
**Location:** `recorded_tests/bookslot/test_bookslot_bookslots_complete.py`
- **Issue:** Hardcoded staging URLs in 3 places (lines 6, 23, 52)
- **Impact:** Tests always run on staging, ignoring environment selection
- **Fix:** Must use multi_project_config fixture

#### 2. **PAGE OBJECTS - MEDIUM PRIORITY**
**Location:** `pages/bookslot/bookslots_basicinfo.py`
- **Issue:** Fallback hardcoded URL on line 36: `"https://bookslot-staging.centerforvein.com"`
- **Impact:** If config fails, always falls back to staging
- **Fix:** Remove fallback or make it environment-aware

#### 3. **CLI DISPLAY TEXT - LOW PRIORITY**
**Location:** `run_tests_cli.py` (lines 341-342, 348, 351, 438-439)
- **Issue:** Hardcoded URLs in display messages only (not in execution)
- **Impact:** Display may show incorrect URL if projects.yaml changes
- **Fix:** Load URLs from projects.yaml for display

#### 4. **CONFTEST FALLBACK - MEDIUM PRIORITY**
**Location:** `conftest.py` (lines 136-141)
- **Issue:** Hardcoded fallback URLs if projects.yaml fails to load
- **Impact:** Silent failure with hardcoded values
- **Fix:** Should raise error instead of silent fallback

---

## DETAILED FINDINGS

### Category 1: RECORDED TESTS (CRITICAL)
**Files Affected:** 1
**Instances:** 3 hardcoded URLs

```python
# CURRENT (WRONG):
page.goto("https://bookslot-staging.centerforvein.com/basic-info")
page.goto("https://bookslot-staging.centerforvein.com/eventtype")
page.goto("https://bookslot-staging.centerforvein.com/success")

# SHOULD BE:
def test_example(page: Page, multi_project_config) -> None:
    base_url = multi_project_config['bookslot']['ui_url']
    page.goto(f"{base_url}/basic-info")
    page.goto(f"{base_url}/eventtype")
    page.goto(f"{base_url}/success")
```

### Category 2: PAGE OBJECTS
**Files Affected:** 1
**Instances:** 1 hardcoded fallback

```python
# CURRENT (line 36):
self.base_url = base_url or "https://bookslot-staging.centerforvein.com"

# SHOULD BE:
# No fallback - require explicit base_url parameter
# OR load from environment variable
```

### Category 3: CLI DISPLAY
**Files Affected:** 1  
**Instances:** 6 display strings

These are informational only but should be dynamic for accuracy.

### Category 4: CONFTEST FALLBACK
**Files Affected:** 1
**Instances:** 4 URLs in fallback dictionary

Should fail loudly instead of silently using hardcoded values.

---

## WHAT'S CORRECTLY CONFIGURED ✅

1. **config/projects.yaml** - All URLs properly structured
2. **config/settings.py** - Dynamic loading from YAML
3. **config/environments.yaml** - Proper environment structure
4. **Database credentials** - Not hardcoded anywhere
5. **API keys** - Properly read from environment variables
6. **Framework core** - All dynamic

---

## FILES REQUIRING NO CHANGES

- `/examples/*` - Demo files with example.com (intentional)
- `/docs/*` - Documentation
- `*.md` - Documentation files
- Test files in `/tests/*` - Use fixtures correctly

---

## PRIORITY FIX LIST

### Priority 1 (CRITICAL) - Breaks environment selection:
1. ✅ `recorded_tests/bookslot/test_bookslot_bookslots_complete.py`

### Priority 2 (HIGH) - Could cause issues:
2. ✅ `pages/bookslot/bookslots_basicinfo.py` (remove fallback)
3. ✅ `conftest.py` (remove hardcoded fallback)

### Priority 3 (MEDIUM) - Display accuracy:
4. ✅ `run_tests_cli.py` (dynamic URL display)

---

## RECOMMENDATION

**BEFORE:** Multiple hardcoded URLs scattered across files
**AFTER:** All URLs loaded from projects.yaml via multi_project_config fixture

**IMPLEMENTATION PLAN:**
1. Fix recorded tests to use fixture
2. Remove fallback URLs from page objects
3. Make CLI display load URLs from projects.yaml
4. Update conftest to fail loudly instead of silent fallback

---

## .ENV FILE STATUS

**Current:** No .env file found in repository (GOOD - sensitive data not committed)
**Expected Location:** Should be in `.gitignore`
**Usage:** AI API keys, database credentials (if needed)

**Recommended .env structure:**
```env
# AI Configuration (Optional)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=your-claude-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Environment Override (Optional)
TEST_ENV=staging

# Database (Optional - only if not in projects.yaml)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=testdb
DB_USER=testuser
DB_PASSWORD=testpass
```

---

## AUDIT CONCLUSION

**Overall Framework Health:** 🟢 **GOOD**

The framework architecture is solid with proper configuration management.
Only **4 files** need fixes, all identified and prioritized above.

**Main Issue:** Recorded tests bypass the configuration system.
**Solution:** Add fixture parameter to all recorded tests.

---

## NEXT STEPS

Execute the fixes in priority order (see implementations below).
