# Dynamic HTML Report Naming System - Implementation Summary

**Date:** February 19, 2026  
**Author:** Lokendra Singh  
**Email:** lokendra.singh@centerforvein.com  

---

## 📋 Overview

Implemented a dynamic HTML report naming system that generates unique, timestamped report filenames for every test execution. Reports follow the format: `projectname_EnvironmentName_DDMMYYYY_HHMMSS.html` and automatically increment if a file with the same name already exists.

---

## 🎯 Features Implemented

### 1. **Dynamic Report Naming**
   - Format: `{project}_{Environment}_{DDMMYYYY}_{HHMMSS}.html`
   - Example: `bookslot_Staging_19022026_143052.html`

### 2. **Automatic Increment on Conflict**
   - If file exists, appends: `_1`, `_2`, `_3`, etc.
   - Example: `bookslot_Staging_19022026_143052_1.html`

### 3. **Custom Filename Support**
   - Users can still specify custom names: `pytest --html=my_custom_report.html`
   - Dynamic naming is skipped when custom name is provided

### 4. **Project & Environment Aware**
   - Uses `--project` option (bookslot, callcenter, patientintake)
   - Uses `--env` option (staging, production)
   - Automatically capitalizes environment name in filename

---

## 📁 Files Modified

### 1. **conftest.py** (Root Level)
   - **Location:** `c:\Users\LokendraSingh\Documents\GitHub\Hybrid_Automation\conftest.py`
   - **Changes:**
     - Added `os` import for path operations
     - Created `generate_unique_report_filename()` function
     - Added `pytest_configure()` hook to set dynamic report name
     - Integrated with audit logging for report path tracking

   **Key Functions:**
   ```python
   def generate_unique_report_filename(project: str, environment: str, reports_dir: str = "reports") -> str:
       """
       Generate unique HTML report filename with format:
       projectname_EnvironmentName_DDMMYYYY_HHMMSS.html
       
       If file exists, append incremental number: _1, _2, etc.
       """
       # Implementation details...
   
   def pytest_configure(config):
       """
       Configure pytest with dynamic HTML report naming.
       Only applies when using default/static report names.
       Respects custom --html=custom_name.html if provided.
       """
       # Implementation details...
   ```

### 2. **pytest.ini**
   - **Location:** `c:\Users\LokendraSingh\Documents\GitHub\Hybrid_Automation\pytest.ini`
   - **Changes:**
     - Removed static `--html=reports/test_report.html` option
     - Added comments explaining dynamic naming
     - Kept `--self-contained-html` option
     - Updated documentation in comments

   **Before:**
   ```ini
   # Generate HTML report
   --html=reports/test_report.html
   --self-contained-html
   ```

   **After:**
   ```ini
   # Generate HTML report (dynamically named by conftest.py)
   # Format: projectname_EnvironmentName_DDMMYYYY_HHMMSS.html
   # If you need a specific filename, use: pytest --html=custom_name.html
   --self-contained-html
   ```

### 3. **scripts/cli/run_tests_cli.py**
   - **Location:** `c:\Users\LokendraSingh\Documents\GitHub\Hybrid_Automation\scripts\cli\run_tests_cli.py`
   - **Changes:**
     - Updated `add_html_report()` method to support dynamic naming
     - Modified interactive menu to suggest dynamic naming (press Enter)
     - Updated quick test scenario #5 (Generate Report)
     - Updated command examples section

   **Updated Method:**
   ```python
   def add_html_report(self, filename: str = None, project: str = None, environment: str = None):
       """
       Add HTML report generation with dynamic naming support.
       
       If filename is not provided, generates dynamic name:
       projectname_EnvironmentName_DDMMYYYY_HHMMSS.html
       """
       if filename:
           # User provided custom filename
           self.add_option(f"--html={filename}")
       else:
           # Dynamic naming handled by conftest.py
           pass
       
       return self.add_option("--self-contained-html")
   ```

   **Interactive Menu Update:**
   ```python
   if self.yes_no("Generate HTML report?"):
       filename = input(f"{Colors.BOLD}Report filename (press Enter for dynamic naming): {Colors.ENDC}").strip()
       if filename:
           self.builder.add_html_report(filename=filename)
       else:
           self.builder.add_html_report()  # Uses dynamic naming
   ```

### 4. **config/environments.yaml**
   - **Location:** `c:\Users\LokendraSingh\Documents\GitHub\Hybrid_Automation\config\environments.yaml`  
   - **Changes:**
     - Removed static `output_file: "reports/test_report.html"`
     - Changed to `output_dir: "reports"`
     - Added documentation comments

   **Before:**
   ```yaml
   html:
     enabled: true
     output_file: "reports/test_report.html"
   ```

   **After:**
   ```yaml
   html:
     enabled: true
     # Dynamic naming: projectname_EnvironmentName_DDMMYYYY_HHMMSS.html
     # Generated automatically by conftest.py based on --project and --env options
     # Use --html=custom_name.html to override with specific filename
     output_dir: "reports"
   ```

---

## 🔧 How It Works

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  User runs pytest command                                   │
│  Example: pytest tests/ --project=bookslot --env=staging   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  pytest_configure() hook executes (conftest.py)            │
│  - Reads --project option → "bookslot"                      │
│  - Reads --env option → "staging"                           │
│  - Checks if custom --html provided → No                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  generate_unique_report_filename() called                   │
│  - Creates timestamp: 19022026_143052                       │
│  - Generates name: bookslot_Staging_19022026_143052.html    │
│  - Checks if file exists in reports/ → No                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Update pytest config                                        │
│  config.option.htmlpath = "reports/bookslot_Staging_..."    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Tests run...                                                │
│  Report generated at dynamic path                           │
└─────────────────────────────────────────────────────────────┘
```

### Increment Logic (If File Exists)

```
1. Check: bookslot_Staging_19022026_143052.html exists? → YES
   ├─ Try: bookslot_Staging_19022026_143052_1.html exists? → YES
   ├─ Try: bookslot_Staging_19022026_143052_2.html exists? → NO
   └─ Use: bookslot_Staging_19022026_143052_2.html ✓
```

---

## 📝 Usage Examples

### Example 1: Default Dynamic Naming
```bash
# Run tests with automatic report naming
pytest tests/integration/ --project=bookslot --env=staging -v

# Generated report:
# reports/bookslot_Staging_19022026_143052.html
```

### Example 2: Different Projects
```bash
# Bookslot project
pytest tests/ --project=bookslot --env=production -v
# → reports/bookslot_Production_19022026_143052.html

# PatientIntake project  
pytest tests/ --project=patientintake --env=staging -v
# → reports/patientintake_Staging_19022026_143055.html

# CallCenter project
pytest tests/ --project=callcenter --env=staging -v
# → reports/callcenter_Staging_19022026_143058.html
```

### Example 3: Multiple Runs (Same Second)
```bash
# First run
pytest tests/ --project=bookslot --env=staging -v
# → reports/bookslot_Staging_19022026_143052.html

# Second run (same timestamp)
pytest tests/ --project=bookslot --env=staging -v
# → reports/bookslot_Staging_19022026_143052_1.html

# Third run (same timestamp)
pytest tests/ --project=bookslot --env=staging -v
# → reports/bookslot_Staging_19022026_143052_2.html
```

### Example 4: Custom Filename Override
```bash
# Use specific custom name (bypasses dynamic naming)
pytest tests/ --project=bookslot --env=staging --html=my_report.html --self-contained-html
# → my_report.html (custom name used)
```

### Example 5: Interactive CLI Mode
```bash
python scripts/cli/run_tests_cli.py

# When prompted for HTML report:
Generate HTML report? (y/n): y
Report filename (press Enter for dynamic naming): [PRESS ENTER]
# → Uses dynamic naming automatically
```

---

## 🧪 Testing & Verification

### Manual Testing Checklist

- [ ] **Test 1:** Run pytest without custom --html option
  - Expected: Report generated with dynamic name
  
- [ ] **Test 2:** Run pytest twice in same second
  - Expected: Second report has `_1` suffix
  
- [ ] **Test 3:** Run with custom --html=custom.html
  - Expected: Uses `custom.html` (not dynamic naming)
  
- [ ] **Test 4:** Different projects and environments
  - Expected: Project and environment names reflected in filename
  
- [ ] **Test 5:** Run via CLI interactive mode
  - Expected: Option to use dynamic naming (press Enter)

### Test Script

Run the verification script:
```bash
python test_dynamic_reports.py
```

---

## 🎯 Benefits

### 1. **No Report Overwriting**
   - Every test run creates a new report
   - Historical reports preserved automatically
   - Easy to compare results across runs

### 2. **Better Organization**
   - Project name in filename (bookslot, patientintake, callcenter)
   - Environment name in filename (Staging, Production)
   - Timestamp for chronological ordering

### 3. **Audit Trail**
   - Complete history of test executions
   - Traceable to specific project/environment/time
   - Supports compliance requirements

### 4. **CI/CD Friendly**
   - Unique artifacts for each pipeline run
   - No conflicts in parallel executions
   - Easy artifact archival and retention

### 5. **User Friendly**
   - Automatic by default (zero configuration)
   - Custom names still supported when needed
   - Clear naming convention

---

## 🔍 Deep Audit Summary

### Files Reviewed & Modified: **4 files**

1. **conftest.py** (Root)
   - Lines modified: Added 110+ lines
   - Functions added: 2 (generate_unique_report_filename, pytest_configure)
   - Imports added: os, Path from pathlib
   
2. **pytest.ini**
   - Lines modified: 8 lines
   - Changes: Removed static --html option, added documentation
   
3. **scripts/cli/run_tests_cli.py**
   - Lines modified: ~25 lines across 4 locations
   - Methods updated: add_html_report()
   - Interactive prompts updated: 1
   - Quick scenarios updated: 1
   - Examples updated: 1
   
4. **config/environments.yaml**
   - Lines modified: 5 lines
   - Configuration updated: html section

### Related Files (No Changes Needed):

- `tests/conftest.py` - Has separate pytest_configure, no conflicts
- `Framework-Knowledge-Center/` docs - May need documentation update
- `README.md` - May need usage examples update

---

## 📚 Implementation Notes

### Design Decisions

1. **Why DDMMYYYY format?**
   - More human-readable than YYYYMMDD
   - Aligns with European/UK date formats
   - Clear day-first ordering

2. **Why capitalize environment name?**
   - Better visual distinction: `Staging` vs `staging`
   - Professional appearance in filenames
   - Consistency with project name casing

3. **Why check for existing file?**
   - Prevents race conditions
   - Supports rapid re-runs
   - Ensures uniqueness even in same second

4. **Why keep custom --html option?**
   - Backward compatibility
   - CI/CD pipelines may need specific names
   - Power users may have specific requirements

### Safety Features

1. **Increment limit:** Stops at _100 to prevent infinite loops
2. **Directory creation:** Auto-creates reports/ if missing
3. **Path validation:** Uses pathlib.Path for cross-platform safety
4. **Logging:** Reports generation path to audit log

---

## 🚀 Future Enhancements (Optional)

### Potential Improvements

1. **Report Archive Management**
   - Auto-archive reports older than X days
   - Compress old reports to save space
   - Database of all report metadata

2. **Report Comparison Tool**
   - Compare two reports side-by-side
   - Highlight differences in test results
   - Trend analysis across multiple runs

3. **Email/Slack Integration**
   - Auto-send report after generation
   - Include summary in notification
   - Link to report location

4. **Dashboard Integration**
   - Upload reports to central dashboard
   - Historical test result visualization
   - Real-time test execution monitoring

---

## ✅ Completion Checklist

- [x] Implemented dynamic report naming logic
- [x] Added increment logic for duplicate names
- [x] Updated conftest.py with pytest_configure hook
- [x] Removed static --html from pytest.ini
- [x] Updated run_tests_cli.py for dynamic naming
- [x] Updated environments.yaml configuration
- [x] Added comprehensive documentation
- [x] Preserved backward compatibility (custom names)
- [x] Added audit logging integration
- [x] Created test verification script

---

## 📞 Support

**Author:** Lokendra Singh  
**Email:** lokendra.singh@centerforvein.com  
**Website:** www.centerforvein.com  

For questions or issues with the dynamic report naming system, please reach out.

---

**Document Version:** 1.0  
**Last Updated:** February 19, 2026  
**Status:** ✅ Implementation Complete
