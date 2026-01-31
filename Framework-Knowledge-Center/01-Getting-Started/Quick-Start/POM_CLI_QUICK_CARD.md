# 🎯 POM CLI Quick Start Card

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│           🚀 POM TEST EXECUTION SYSTEM                          │
│              Quick Reference Card                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

## 🚀 Launch Options

### Windows
```cmd
run_pom.bat                    ← Double-click
.\run_pom.ps1                  ← PowerShell
.\run_pom.ps1 -Quick           ← Quick mode
python run_pom_tests_cli.py    ← Python
```

### Linux/Mac
```bash
python3 run_pom_tests_cli.py
```

---

## 📋 10-Step Interactive Flow

```
1. Pre-Flight Validation     → Auto-checks environment
2. Project Selection          → BookSlot / CallCenter / PatientIntake
3. Environment Selection      → Staging / Production
4. Browser Configuration      → Chromium / Firefox / WebKit / Chrome / Edge
5. Test Scope Selection       → All / Specific File / Specific Function
6. Human Behavior             → Enable / Disable
7. Execution Options          → Parallel / Markers
8. Report Configuration       → HTML / Allure
9. Execution Summary          → Review & Confirm
10. Test Execution            → Run & View Results
```

---

## ⚡ Quick Commands

### Interactive Mode (Recommended)
```bash
python run_pom_tests_cli.py
```

### Quick Mode (Defaults)
```powershell
.\run_pom.ps1 -Quick
```

### Direct pytest (Advanced)
```bash
# Run all BookSlot tests on staging
pytest tests/integration --project=bookslot --env=staging --browser=chromium -v

# Run specific test with human behavior
pytest tests/integration/test_bookslot_to_patientintake.py::test_book_appointment_and_verify_in_patientintake --project=bookslot --env=staging --browser=chromium -m human_like -v

# Parallel execution with HTML report
pytest tests/integration --project=bookslot --env=staging --browser=chromium -n 4 --html=reports/report.html --self-contained-html -v
```

---

## 🎯 Common Scenarios

### Scenario 1: Quick Smoke Test
```
Project: 1 (BookSlot)
Environment: 1 (Staging)
Browser: 1 (Chromium, headed)
Scope: 1 (All tests)
Human Behavior: n
Parallel: y, auto
Markers: smoke
Reports: HTML

→ Fast smoke tests on staging
```

### Scenario 2: Production Validation
```
Project: 1 (BookSlot)
Environment: 2 (Production)
Browser: 1 (Chromium, headless)
Scope: 3 (Specific function)
Human Behavior: y
Parallel: n
Markers: critical
Reports: HTML + Allure

→ Critical test on production
```

### Scenario 3: Full Regression
```
Project: 1 (BookSlot)
Environment: 1 (Staging)
Browser: 1 (Chromium, headless)
Scope: 1 (All tests)
Human Behavior: n
Parallel: y, 4
Markers: regression
Reports: HTML + Allure

→ Complete test suite, parallel
```

---

## ✅ Pre-Flight Checks

The CLI automatically validates:

✓ Python >= 3.8
✓ pytest installation
✓ Playwright installation
✓ Configuration files (projects.yaml, environments.yaml)
✓ Page objects directory
✓ POM fixtures in conftest.py

---

## 🌐 Supported Browsers

| Browser | Code | Use Case |
|---------|------|----------|
| Chromium | chromium | Default, fast |
| Firefox | firefox | Cross-browser |
| WebKit | webkit | Safari testing |
| Chrome | chrome | Google Chrome |
| Edge | msedge | MS Edge |

---

## 🎨 Options Reference

### Project Options
- [1] BookSlot - Patient appointment booking
- [2] CallCenter - Call center operations
- [3] PatientIntake - Patient intake system

### Environment Options
- [1] Staging - Pre-production (safe for testing)
- [2] Production - Live environment (use with caution)

### Test Scope Options
- [1] All Tests - Run complete suite
- [2] Specific File - Choose single test file
- [3] Specific Function - Choose single test

### Execution Options
- Parallel: Yes/No (default: No)
- Workers: auto or number (default: auto)
- Markers: smoke, regression, integration, critical

### Report Options
- HTML: Yes/No (default: Yes)
- Allure: Yes/No (default: No)

---

## 🚨 Troubleshooting

### "pytest not found"
```bash
pip install pytest pytest-playwright pytest-html pytest-xdist
```

### "Playwright not found"
```bash
pip install playwright
playwright install
```

### "No POM tests found"
→ Ensure tests use fixtures: bookslot_page, etc.

### "Configuration file missing"
→ Check: config/projects.yaml, config/environments.yaml

---

## 📊 Report Locations

### HTML Reports
```
reports/pom_test_report_YYYYMMDD_HHMMSS.html
```

### Allure Reports
```
allure-results/
(View with: allure serve allure-results)
```

---

## 💡 Pro Tips

1. ✓ **Always start with staging** - Test before production
2. ✓ **Use pre-flight validation** - Catches issues early
3. ✓ **Enable human behavior for demos** - Looks realistic
4. ✓ **Disable for CI/CD** - Faster execution
5. ✓ **Use parallel for large suites** - Speed boost
6. ✓ **Start with specific tests** - Debug faster
7. ✓ **Use markers** - Run targeted suites
8. ✓ **Generate HTML reports** - Easy to share

---

## 📚 Documentation Links

| Document | Purpose |
|----------|---------|
| [POM_TEST_RUNNER_README.md](Framework-Knowledge-Center/01-Getting-Started/Quick-Start/POM_TEST_RUNNER_README.md) | Complete guide |
| [POM_CLI_GUIDE.md](Framework-Knowledge-Center/01-Getting-Started/Quick-Start/POM_CLI_GUIDE.md) | Quick reference |
| [POM_CLI_FLOW.md](Framework-Knowledge-Center/01-Getting-Started/Quick-Start/POM_CLI_FLOW.md) | Visual diagrams |

---

## 🔑 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Accept default |
| `0` | Go back / Exit |
| `Ctrl+C` | Cancel execution |
| `y` | Yes |
| `n` | No |

---

## 📞 Support

**Author:** Lokendra Singh
**Email:** qa.lokendra@gmail.com
**Website:** www.sqamentor.com

---

## ✅ Quick Checklist

Before running tests:

- [ ] Python >= 3.8 installed
- [ ] pytest installed
- [ ] Playwright installed
- [ ] Browsers installed (playwright install)
- [ ] Configuration files exist
- [ ] Page objects exist
- [ ] Test files exist

---

## 🎊 Remember

**The POM CLI handles everything for you:**
- ✓ No manual command construction
- ✓ Automatic validation
- ✓ Clear error messages
- ✓ Guided workflow
- ✓ Safe execution

**Just launch and follow the prompts!**

---

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                     Happy Testing! 🎉                           │
│                                                                 │
│             Keep this card handy for quick reference            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
