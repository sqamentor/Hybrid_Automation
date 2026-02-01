# DYNAMIC AUDIT SYSTEM - COMPLETE GUIDE

**Status:** ✅ FULLY OPERATIONAL  
**Version:** 2.0 (Dynamic + Automatic)  
**Last Updated:** February 1, 2026

---

## 🎯 OVERVIEW

This system provides **100% automatic architecture enforcement** through:

1. **Real-time File Monitoring** - Audits trigger automatically on file changes
2. **Commit Blocking** - Invalid code cannot be committed
3. **CI/CD Integration** - Every push/PR is validated before merge
4. **Complete Audit Trail** - Every change is tracked and archived
5. **Trend Dashboards** - Visual monitoring of compliance over time

### Key Principle

**IMPOSSIBLE TO VIOLATE RULES WITHOUT IMMEDIATE DETECTION**

Every code change is validated through multiple enforcement layers:
- Local development (file watcher)
- Git commits (pre-commit hooks)
- GitHub pushes (CI/CD)
- Historical tracking (audit trail)

---

## 📦 COMPONENTS

### 1. File System Watcher

**File:** `scripts/governance/file_watcher_audit.py`

Monitors specified directories and auto-triggers audits when Python files change.

**Features:**
- Debounced audit triggering (2 seconds after last change)
- Real-time violation detection
- Change context in reports
- Audit history tracking
- Trend analysis
- Strict mode (stops on first violation)

**Usage:**
```bash
# Start watching
python scripts/governance/file_watcher_audit.py --watch

# Strict mode (exits on violation)
python scripts/governance/file_watcher_audit.py --watch --strict

# View history
python scripts/governance/file_watcher_audit.py --history

# View trends
python scripts/governance/file_watcher_audit.py --trend
```

**What it monitors:**
- `tests/` - Test files
- `pages/` - Page Object files
- `framework/` - Framework code
- `utils/` - Utility code

**Output:**
- Real-time terminal output
- `artifacts/audit_history/audit_*.md` - Timestamped reports
- `artifacts/audit_history/audit_history.json` - Complete history log

---

### 2. Enhanced Pre-Commit Hooks

**Files:**
- `scripts/governance/pre_commit_hook_enhanced.py` - Hook logic
- `scripts/governance/install_hooks.py` - Installer

Blocks commits that violate architecture rules.

**Features:**
- Runs audit on staged files only (fast)
- Blocks commit on CRITICAL/ERROR violations
- Allows commit with WARNINGS (developer discretion)
- Tracks commit history
- Provides actionable fix suggestions
- Separates staged vs non-staged violations

**Installation:**
```bash
# Install hook
python scripts/governance/install_hooks.py

# Test hook
python scripts/governance/install_hooks.py --test

# Uninstall
python scripts/governance/install_hooks.py --uninstall
```

**Behavior:**
```bash
$ git commit -m "Add feature"
🔍 Running architecture audit on staged files...
Checking 3 staged Python file(s)...

❌ AUDIT FAILED - Commit BLOCKED

VIOLATIONS IN STAGED FILES:
  tests/new_test.py:25
  Rule: marker-engine/missing-marker
  Test class missing engine marker
  💡 Add @pytest.mark.modern_spa or @pytest.mark.legacy_ui

TO FIX:
  1. Review violations above
  2. Fix the issues in your staged files
  3. Run: pytest --arch-audit (to verify)
  4. Try commit again
```

**Bypass (NOT RECOMMENDED):**
```bash
git commit --no-verify
```

**Output:**
- Terminal display (real-time)
- `artifacts/commit_history/commit_audit_log.json` - Complete log

---

### 3. GitHub Actions Integration

**File:** `.github/workflows/architecture-audit.yml`

Runs comprehensive audits on every push and pull request.

**Enhanced Features:**
- Auto-triggers on Python file changes in any branch
- Runs on `push` to: main, develop, feature/*, bugfix/*
- Runs on `pull_request` to: main, develop
- 7 independent status checks (parallel execution)
- Archives reports with git commit hash + timestamp
- Retention: 90 days

**Status Checks:**
1. `audit/engine-mix` (BLOCKING)
2. `audit/marker-engine` (BLOCKING)
3. `audit/folder-engine` (BLOCKING)
4. `audit/pom-compliance` (BLOCKING)
5. `audit/test-boundaries` (WARNING)
6. `audit/structural` (BLOCKING)
7. `audit/canonical-flow` (INFO)

**Automatic Archival:**
Every push creates archived report:
```
artifacts/archive/audit_20260201_143022_main_a3f4c1d.md
                        ^^^^^^^^  ^^^^    ^^^^^^^^
                        timestamp branch  commit hash
```

**Branch Protection Setup:**
```
Repository Settings → Branches → main → Branch protection rules
☑ Require status checks to pass before merging
☑ Require branches to be up to date before merging

Required status checks:
  ☑ audit/engine-mix
  ☑ audit/marker-engine
  ☑ audit/folder-engine
  ☑ audit/pom-compliance
  ☑ audit/structural
```

---

### 4. Audit History Tracking

**Files:**
- `artifacts/audit_history/audit_history.json` - Watcher audits
- `artifacts/commit_history/commit_audit_log.json` - Commit audits
- `artifacts/archive/*.md` - Archived reports

Maintains complete audit trail for compliance tracking.

**Data Tracked:**
```json
{
  "timestamp": "2026-02-01T14:30:22",
  "files_changed": ["tests/test_new.py"],
  "files_scanned": 325,
  "total_violations": 5,
  "blocking_violations": 2,
  "warning_violations": 3,
  "passed": false,
  "violations_by_category": {
    "marker-engine": 2,
    "test-boundaries": 3
  }
}
```

**Retention:**
- Watcher history: Last 1,000 audits
- Commit history: Last 500 commits
- Archived reports: 90 days (CI), unlimited (local)

---

### 5. Visual Dashboard

**File:** `scripts/governance/audit_dashboard.py`

Interactive HTML dashboard showing trends and metrics.

**Features:**
- Real-time compliance score
- Violation trends (last 30 days)
- Category breakdown (pie chart)
- Daily activity chart
- Most violated files
- Overall trend analysis (improving/stable/degrading)

**Usage:**
```bash
# Generate dashboard
python scripts/governance/audit_dashboard.py

# Generate and open in browser
python scripts/governance/audit_dashboard.py --open
```

**Output:**
- `artifacts/audit_dashboard.html` - Interactive dashboard
- Charts powered by Chart.js
- Auto-refreshes on every generation

**Metrics Displayed:**
- Total audits run
- Compliance score (% passing)
- Average violations per audit
- Trend direction
- Commits checked
- Blocked commits
- Top violated files
- Category distribution

---

## 🚀 QUICK START

### One-Command Setup

```bash
python scripts/governance/setup_dynamic_audit.py --full
```

This will:
1. ✅ Install required dependencies (watchdog)
2. ✅ Create necessary directories
3. ✅ Install pre-commit hooks
4. ✅ Verify GitHub Actions workflow
5. ✅ Run initial audit (baseline)
6. ✅ Generate initial dashboard

---

## 📋 DAILY WORKFLOWS

### For Developers

**1. Start Development Session**
```bash
# Terminal 1: Start file watcher
python scripts/governance/file_watcher_audit.py --watch

# Terminal 2: Your normal development
code .
```

**2. Make Changes**
- Edit files normally
- Audit runs automatically 2 seconds after saving
- See results in watcher terminal

**3. Commit Changes**
```bash
git add .
git commit -m "Your message"
# Pre-commit hook runs automatically
# Commit blocked if violations found
```

**4. Push Changes**
```bash
git push origin feature/your-branch
# GitHub Actions runs automatically
# 7 status checks must pass
```

**5. Review Trends** (weekly)
```bash
python scripts/governance/audit_dashboard.py --open
# Review compliance trends
# Identify problem areas
```

### For QA/Architects

**1. Monitor Compliance**
```bash
# View recent audit history
python scripts/governance/file_watcher_audit.py --history

# View trend analysis
python scripts/governance/file_watcher_audit.py --trend

# Generate dashboard
python scripts/governance/audit_dashboard.py --open
```

**2. Review Violations**
```bash
# Latest report
cat artifacts/framework_audit_report.md

# Specific category
pytest --arch-audit --audit-category=pom-compliance
```

**3. Track Changes**
```bash
# Review commit history
cat artifacts/commit_history/commit_audit_log.json | jq '.[-10:]'

# Review archived reports
ls -lt artifacts/archive/
```

### For CI/CD

**1. Verify Workflow**
```bash
# Check workflow file
cat .github/workflows/architecture-audit.yml

# Test locally (if using act)
act pull_request
```

**2. Configure Branch Protection**
```
GitHub → Settings → Branches → main
→ Add rule
→ Require status checks
→ Select all audit/* checks
→ Save
```

**3. Review CI Results**
- Check Actions tab in GitHub
- Download artifacts from workflow runs
- Review PR comments

---

## 📊 ENFORCEMENT LEVELS

### Level 1: Real-Time (File Watcher)

**Trigger:** File save  
**Delay:** 2 seconds (debounce)  
**Action:** Display violations, update history  
**Blocking:** No (informational)  
**Best For:** Active development, immediate feedback

### Level 2: Commit (Pre-Commit Hook)

**Trigger:** `git commit`  
**Delay:** Immediate  
**Action:** Audit staged files, block commit  
**Blocking:** Yes (CRITICAL/ERROR only)  
**Best For:** Preventing bad code from entering git history

### Level 3: CI/CD (GitHub Actions)

**Trigger:** `git push`, Pull Request  
**Delay:** ~2-3 minutes  
**Action:** Full audit, block merge  
**Blocking:** Yes (configurable via branch protection)  
**Best For:** Final gatekeeper before main branch

---

## 🔍 AUDIT TRAIL

Every audit creates a complete trail for compliance:

### 1. Watcher Audits

**Location:** `artifacts/audit_history/`

**Files:**
- `audit_history.json` - Complete history log
- `audit_YYYYMMDD_HHMMSS.md` - Individual reports

**What's Tracked:**
- Timestamp (ISO 8601)
- Files changed
- Files scanned
- Violation counts by category
- Pass/fail status

### 2. Commit Audits

**Location:** `artifacts/commit_history/`

**Files:**
- `commit_audit_log.json` - Complete log

**What's Tracked:**
- Timestamp
- Branch name
- Author name/email
- Staged files
- Violations (with details)
- Pass/fail status

### 3. CI Archives

**Location:** `artifacts/archive/`

**Files:**
- `audit_YYYYMMDD_HHMMSS_<branch>_<commit>.md`

**What's Tracked:**
- Full audit report
- Git metadata (commit hash, branch, author)
- Timestamp
- All violations with context

---

## 🎯 COMPLIANCE METRICS

### Compliance Score

```
Compliance Score = (Passing Audits / Total Audits) × 100
```

**Target:** 90%+  
**Excellent:** 95%+  
**Needs Attention:** <85%

### Trend Analysis

**Improving:** Recent avg violations < Previous avg × 0.9  
**Stable:** Recent avg within ±10% of previous  
**Degrading:** Recent avg violations > Previous avg × 1.1

### Category Health

Track violations by category:
- `engine-mix` - Should be 0
- `marker-engine` - Should be 0
- `pom-compliance` - Should be 0
- `test-boundaries` - Can have warnings
- Others - Minimize over time

---

## 🔧 CONFIGURATION

### File Watcher

**Debounce Time:** 2 seconds (hardcoded)  
**Directories:** tests/, pages/, framework/, utils/  
**File Types:** .py only  
**History Limit:** 1,000 audits

**To customize:**
Edit `scripts/governance/file_watcher_audit.py`:
```python
# Line ~90
self.debounce_seconds: float = 2.0  # Change here
```

### Pre-Commit Hook

**Severity Blocking:** CRITICAL, ERROR  
**Severity Allowing:** WARNING, INFO  
**History Limit:** 500 commits

**To customize:**
Edit `scripts/governance/pre_commit_hook_enhanced.py`:
```python
# Line ~175
blocking_in_staged = any(
    v.severity in (Severity.CRITICAL, Severity.ERROR)  # Change here
    for v in staged_violations
)
```

### GitHub Actions

**Trigger Paths:**
```yaml
paths:
  - '**.py'
  - 'tests/**'
  - 'pages/**'
  - 'framework/**'
  - 'utils/**'
```

**Archive Retention:** 90 days

**To customize:**
Edit `.github/workflows/architecture-audit.yml`

---

## 🐛 TROUBLESHOOTING

### Issue: File watcher not detecting changes

**Solution:**
```bash
# Check if watchdog installed
python -m pip show watchdog

# Install if missing
python -m pip install watchdog

# Verify paths exist
ls tests/ pages/ framework/ utils/
```

### Issue: Pre-commit hook not running

**Solution:**
```bash
# Reinstall hook
python scripts/governance/install_hooks.py

# Check if .git/hooks/pre-commit exists
cat .git/hooks/pre-commit

# Make executable (Unix/Mac)
chmod +x .git/hooks/pre-commit

# Test hook manually
python scripts/governance/pre_commit_hook_enhanced.py
```

### Issue: GitHub Actions not triggering

**Solution:**
```bash
# Check workflow exists
cat .github/workflows/architecture-audit.yml

# Verify Actions enabled
# GitHub → Settings → Actions → Allow all actions

# Check trigger conditions match your branch
# Edit workflow if needed
```

### Issue: Dashboard shows no data

**Solution:**
```bash
# Run some audits first
python scripts/governance/file_watcher_audit.py --watch
# Make a change and wait for audit

# Then regenerate dashboard
python scripts/governance/audit_dashboard.py --open
```

---

## 📚 ADDITIONAL RESOURCES

- [GOVERNANCE_SYSTEM.md](GOVERNANCE_SYSTEM.md) - Complete rule reference
- [GOVERNANCE_QUICK_REF.md](GOVERNANCE_QUICK_REF.md) - Daily cheat sheet
- [AUDIT_TODO_LIST_AND_VERIFICATION.md](AUDIT_TODO_LIST_AND_VERIFICATION.md) - Audit verification
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Deployment guide

---

## ✅ VERIFICATION

To verify the dynamic audit system is operational:

```bash
# 1. Verify all components
python scripts/validation/verify_governance_system.py
# Should show 18/18 checks passed

# 2. Test file watcher
python scripts/governance/file_watcher_audit.py --watch
# Make a change to test file
# Should see audit trigger

# 3. Test pre-commit hook
python scripts/governance/install_hooks.py --test
# Should run audit on staged files

# 4. View dashboard
python scripts/governance/audit_dashboard.py --open
# Should show metrics and charts

# 5. Check GitHub Actions
cat .github/workflows/architecture-audit.yml
# Should have enhanced triggers
```

---

## 🎉 SUCCESS CRITERIA

✅ **File watcher running** - Audits trigger on file saves  
✅ **Pre-commit hook active** - Commits blocked on violations  
✅ **GitHub Actions configured** - CI runs on every push/PR  
✅ **Audit history tracked** - Complete trail maintained  
✅ **Dashboard accessible** - Visual metrics available  
✅ **Reports archived** - Git metadata preserved  
✅ **Branch protection enabled** - Merge blocked on failures

**When all criteria met:**

🎯 **ZERO-TOLERANCE ARCHITECTURE ENFORCEMENT ACHIEVED**

Every code change is validated through multiple layers. Violations are detected immediately, tracked completely, and archived permanently. Compliance trends are visible and actionable.

---

**Document Version:** 2.0  
**Last Updated:** February 1, 2026  
**Status:** ✅ Production Ready
