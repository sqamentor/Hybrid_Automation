# Architecture Governance System - Automated Enforcement & Audit

## 1. Purpose
- **Why this component exists**: Automatically enforces architectural rules, prevents framework degradation, and maintains code quality without manual reviews
- **What problem it solves**: Eliminates manual code review burden, catches violations early, prevents technical debt, ensures consistent architecture

## 2. Scope

### What is Included
- **AST-Based Static Analysis Engine** - Scans Python code for violations
- **Pre-Commit Hooks** - Blocks commits with violations
- **File Watcher** - Real-time audit on file changes
- **CI/CD Integration** - 7 independent GitHub Actions status checks
- **Baseline Allow-List** - Managed technical debt with expiration
- **Fix Suggestions Engine** - Actionable remediation guidance
- **AI Explainer** - Educational violation explanations
- **Audit Dashboard** - Visual trends and metrics
- **Pytest Plugin** - Manual audit command (`pytest --arch-audit`)

### What is Excluded
- Code formatting (use Black/Ruff)
- Type checking (use Mypy)
- Unit test coverage (use pytest-cov)
- Linting (use Ruff)
- Security scanning (use Bandit/Safety)

## 3. Current Implementation

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GOVERNANCE SYSTEM                        │
│                                                             │
│  ┌─────────────┐   ┌──────────────┐   ┌────────────────┐ │
│  │   Layer 1   │   │   Layer 2    │   │    Layer 3     │ │
│  │ Pre-Commit  │   │ File Watcher │   │    CI/CD       │ │
│  │   Hooks     │   │  (Real-time) │   │  (GitHub)      │ │
│  └──────┬──────┘   └──────┬───────┘   └───────┬────────┘ │
│         │                  │                    │          │
│         └──────────────────┼────────────────────┘          │
│                            │                                │
│                    ┌───────▼────────┐                      │
│                    │  AUDIT ENGINE  │                      │
│                    │  (AST Analysis)│                      │
│                    └───────┬────────┘                      │
│                            │                                │
│         ┌──────────────────┼──────────────────┐            │
│         │                  │                  │            │
│  ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐    │
│  │   Rules     │   │  Baseline   │   │   Report    │    │
│  │   Engine    │   │  Manager    │   │  Generator  │    │
│  └─────────────┘   └─────────────┘   └─────────────┘    │
│                                                             │
│  ┌─────────────┐   ┌──────────────┐   ┌────────────────┐ │
│  │Fix Suggest. │   │ AI Explainer │   │   Dashboard    │ │
│  │   Engine    │   │  (Optional)  │   │   (Metrics)    │ │
│  └─────────────┘   └──────────────┘   └────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. **Audit Engine** (`scripts/governance/framework_audit_engine.py`)
- **AST-based analysis** - Parses Python code into Abstract Syntax Tree
- **Rule evaluation** - Checks code against 50+ architectural rules
- **Violation detection** - Identifies anti-patterns and rule breaches
- **Baseline checking** - Applies allow-list suppressions
- **Exit codes** - 0 (pass), 1 (violations), 2 (baseline expired), 3 (error)

#### 2. **Pre-Commit Hook** (`scripts/governance/pre_commit_hook_enhanced.py`)
- **Automatic installation** - Installed via setup script
- **Staged files only** - Fast (< 2 seconds)
- **Commit blocking** - Prevents commits with ERROR-level violations
- **Bypass option** - `git commit --no-verify` (emergency only)

#### 3. **File Watcher** (`scripts/governance/file_watcher_audit.py`)
- **Real-time monitoring** - Watches tests/, pages/, framework/, utils/
- **Auto-triggers** - Runs audit 2 seconds after last change
- **Strict mode** - Optional fail-fast behavior
- **History tracking** - Maintains audit trend data

#### 4. **CI/CD Integration** (`.github/workflows/architecture-audit.yml`)
- **7 Independent Checks** - Each audit category runs separately
  1. POM Compliance
  2. Engine Mixing
  3. Test Structure
  4. Marker Consistency
  5. Import Validation
  6. Naming Conventions
  7. Full Audit
- **PR Blocking** - Merge requires all checks to pass
- **Artifact Upload** - Audit reports saved for 30 days

#### 5. **Baseline Allow-List** (`ci/baseline_allowlist.yaml`)
- **Technical debt management** - Suppress known violations temporarily
- **Expiration tracking** - Every entry MUST have expiration date
- **Expired = Build Fail** - Expired entries cause build failure
- **Audit trail** - All suppressions logged

#### 6. **Fix Suggestions** (`scripts/governance/framework_fix_suggestions.py`)
- **Actionable guidance** - Specific fix instructions for each violation
- **Code examples** - Shows before/after code
- **Priority scoring** - Critical fixes first
- **Auto-fix support** - Some violations can be auto-fixed

#### 7. **Pytest Plugin** (`scripts/governance/pytest_arch_audit_plugin.py`)
- **Manual audit** - `pytest --arch-audit`
- **Category filter** - `pytest --arch-audit --audit-category=pom-compliance`
- **Report generation** - `pytest --arch-audit --audit-report=report.md`
- **Strict mode** - `pytest --arch-audit --audit-strict`

## 4. Audit Rules Categories

### 1. **POM Compliance** (Page Object Model)
- ❌ Direct locators in tests
- ❌ Pytest imports in page objects
- ❌ Assertions in page objects
- ❌ No method chaining (missing return self)
- ❌ Inline locators (not @property)

### 2. **Engine Mixing**
- ❌ Mixing Playwright and Selenium in same test
- ❌ Engine marker mismatch (marker doesn't match imports)
- ❌ Missing engine markers

### 3. **Test Structure**
- ❌ God tests (too many assertions)
- ❌ Poor test naming
- ❌ Missing docstrings
- ❌ AAA pattern violations

### 4. **Marker Consistency**
- ❌ Missing project markers
- ❌ Missing engine markers
- ❌ Invalid marker combinations

### 5. **Import Validation**
- ❌ Forbidden imports in page objects
- ❌ Wildcard imports
- ❌ Circular dependencies
- ❌ Import order violations

### 6. **Naming Conventions**
- ❌ Non-descriptive test names
- ❌ CamelCase file names (should be snake_case)
- ❌ Incorrect file suffixes (_page.py, test_*.py)

### 7. **Delay Management**
- ❌ Manual time.sleep() calls in tests
- ❌ Arbitrary wait times

### 8. **Data Management**
- ❌ Hardcoded test data
- ❌ Secrets in code
- ❌ Shared mutable data

## 5. Execution Flow

### Pre-Commit Hook Flow

```
Developer runs: git commit -m "message"
    │
    ├─> Pre-commit hook triggers
    │
    ├─> Get staged Python files
    │       └─> tests/*.py, pages/*.py, framework/*.py
    │
    ├─> Run Audit Engine on staged files only
    │       │
    │       ├─> Parse files to AST
    │       ├─> Evaluate rules
    │       ├─> Apply baseline suppressions
    │       └─> Collect violations
    │
    ├─> Check for violations
    │       │
    │       ├─> No violations → ✅ COMMIT ALLOWED
    │       │
    │       └─> Violations found → ❌ COMMIT BLOCKED
    │               │
    │               ├─> Display violations
    │               ├─> Show fix suggestions
    │               └─> Exit code 1
    │
    └─> Bypass option: git commit --no-verify
```

### CI/CD Flow

```
Developer pushes to GitHub or opens PR
    │
    ├─> GitHub Actions trigger
    │
    ├─> Run 7 independent status checks in parallel:
    │       ├─> Check 1: POM Compliance
    │       ├─> Check 2: Engine Mixing
    │       ├─> Check 3: Test Structure
    │       ├─> Check 4: Marker Consistency
    │       ├─> Check 5: Import Validation
    │       ├─> Check 6: Naming Conventions
    │       └─> Check 7: Full Audit
    │
    ├─> Each check:
    │       ├─> Runs audit with category filter
    │       ├─> Generates report
    │       ├─> Uploads artifacts
    │       └─> Returns pass/fail
    │
    ├─> Aggregate results
    │       │
    │       ├─> All pass → ✅ PR MERGE ALLOWED
    │       │
    │       └─> Any fail → ❌ PR MERGE BLOCKED
    │               ├─> Comment on PR with violations
    │               ├─> Link to audit reports
    │               └─> Require fixes before merge
```

## 6. Inputs & Outputs

### Audit Engine Inputs

**Command Line:**
```bash
python scripts/governance/framework_audit_engine.py \
    --category pom-compliance \
    --baseline ci/baseline_allowlist.yaml \
    --report artifacts/audit_report.md \
    --strict
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--category` | `str` | No | Audit specific category only |
| `--baseline` | `Path` | No | Baseline allow-list file |
| `--report` | `Path` | No | Output report path |
| `--strict` | `bool` | No | Fail on warnings too |
| `--ci` | `bool` | No | CI mode (stricter) |

### Audit Engine Outputs

**Exit Codes:**
- `0` - No violations (or all baselined)
- `1` - Violations detected
- `2` - Baseline expired or invalid
- `3` - System error (file not found, parse error, etc.)

**Return Object:**
```python
@dataclass
class AuditResult:
    files_scanned: int
    violations: List[Violation]
    warnings: List[Violation]
    errors: List[Violation]
    baselined_count: int
    passed: bool
    execution_time: float
```

**Violation Object:**
```python
@dataclass
class Violation:
    file_path: str
    line_number: int
    rule_id: str
    category: Category  # Enum
    severity: Severity  # ERROR, WARNING, INFO
    message: str
    context: str  # Code snippet
    fix_suggestion: str
    baselined: bool
```

## 7. Design Decisions

### Why AST-Based Analysis?

**Decision:** Use Python's `ast` module for code analysis

**Why:**
- **Accurate** - Understands Python syntax, not just regex
- **Comprehensive** - Can analyze imports, function calls, inheritance
- **Reliable** - Doesn't produce false positives from comments/strings
- **Fast** - Efficient parsing (~10ms per file)

**Alternative Considered:**
- Regex-based scanning (too brittle, false positives)
- Linters like Pylint (focus on style, not architecture)

### Why Multiple Enforcement Layers?

**Decision:** Pre-commit + File Watcher + CI/CD (3 layers)

**Why:**
- **Defense in depth** - Multiple opportunities to catch violations
- **Shift left** - Catch early (pre-commit) rather than late (CI)
- **Developer freedom** - Can bypass pre-commit if needed, but CI catches it
- **Real-time feedback** - File watcher provides instant feedback during development

### Why Baseline Allow-List?

**Decision:** Allow temporary suppression with mandatory expiration

**Why:**
- **Pragmatic** - Can't fix all violations immediately
- **Transparent** - All suppressions logged and audited
- **Time-bound** - Expiration forces eventual fix
- **Prevents abuse** - Can't suppress violations indefinitely

**Alternative Considered:**
- No suppressions (too strict, blocks progress)
- Permanent suppressions (technical debt accumulates)

### Why 7 Independent CI Checks?

**Decision:** Split into 7 separate GitHub Actions jobs

**Why:**
- **Parallelization** - All run simultaneously (faster)
- **Clear visibility** - PR shows which specific check failed
- **Granular control** - Can require specific checks for merge
- **Better UX** - See "POM Compliance: ❌" vs "Architecture Audit: ❌"

## 8. Rules & Constraints

### Hard Rules

#### ✅ MUST DO:

1. **All commits MUST pass pre-commit audit**
   - Bypass only for emergencies
   - Document bypass reason

2. **All PRs MUST pass CI/CD audit**
   - No exceptions
   - Merge blocked until fixed

3. **Baseline entries MUST have expiration**
   ```yaml
   violations:
     - file: test.py
       expires: 2026-03-31  # ✅ MANDATORY
   ```

4. **Expired baseline entries FAIL builds**
   - Automatic enforcement
   - No grace period

#### ❌ MUST NOT DO:

1. **Don't commit --no-verify habitually**
   - Emergency use only
   - Document why

2. **Don't add violations to baseline without plan to fix**
   - Set realistic expiration
   - Track in issue tracker

3. **Don't modify audit engine to reduce strictness**
   - Weakens governance
   - Defeats purpose

## 9. Error Handling & Edge Cases

### Baseline Expiration

```yaml
# Scenario: Baseline entry expired
violations:
  - file: tests/legacy/test_old.py
    expires: 2026-01-01  # ❌ Already expired
```

**Behavior:**
- Audit engine detects expiration
- Logs error: "Baseline entry expired for tests/legacy/test_old.py"
- Exit code: 2 (baseline error)
- Build fails

**Mitigation:**
- Extend expiration (if more time needed)
- Fix violation (preferred)
- Remove from baseline (if fixed)

### Parse Errors

```python
# Scenario: Invalid Python syntax
def test_broken(page:  # ❌ Syntax error
    pass
```

**Behavior:**
- AST parser fails
- Logs error: "Failed to parse file: SyntaxError"
- Skips file
- Continues with other files
- Final result: Error if any file unparsable

### False Positives

```python
# Scenario: Comment contains violation pattern
def test_valid(page: Page):
    # Don't use page.locator() directly  # ← Just a comment
    login_page = LoginPage(page)  # ✅ Correct usage
```

**Behavior:**
- AST analysis ignores comments
- No false positive
- Test passes

### Very Large Codebase

```
# Scenario: 10,000 Python files
pytest --arch-audit
```

**Behavior:**
- Parallel processing (uses multiprocessing)
- ~1000 files/second
- 10,000 files = ~10 seconds
- Caching for repeated runs

## 10. Extensibility & Customization

### Add New Audit Rule

```python
# scripts/governance/custom_rules.py

from framework_audit_engine import Rule, Violation, Severity, Category

class CustomRule(Rule):
    """Custom audit rule"""
    
    rule_id = "custom/my-rule"
    category = Category.TEST_STRUCTURE
    severity = Severity.WARNING
    
    def check(self, node, context):
        """Check for violation"""
        if self._is_violation(node):
            return Violation(
                file_path=context['file_path'],
                line_number=node.lineno,
                rule_id=self.rule_id,
                category=self.category,
                severity=self.severity,
                message="Custom rule violated",
                context=self._get_context(node),
                fix_suggestion="Fix it like this..."
            )
        return None

# Register rule
from framework_audit_engine import register_rule
register_rule(CustomRule())
```

### Custom Baseline Validator

```python
class CustomBaselineValidator:
    """Custom baseline validation logic"""
    
    def validate_entry(self, entry):
        """Validate baseline entry"""
        # Custom validation logic
        if entry['expires'] < datetime.now():
            raise BaselineExpiredError()
        
        # Check custom fields
        if 'owner' not in entry:
            raise ValueError("Baseline entry must have owner")
```

## 11. Anti-Patterns

### ❌ Bypassing Governance

**DON'T:**
```bash
# ❌ Habitually bypass
git commit --no-verify  # Every commit
```

**DO:**
```bash
# ✅ Fix violations
pytest --arch-audit
# Fix issues
git commit  # Normal commit
```

### ❌ Ignoring CI Failures

**DON'T:**
- Merge PRs with failing audits
- Disable status checks
- Force push

**DO:**
- Fix violations
- Update baseline (with expiration)
- Get approval for exception

### ❌ Permanent Baselines

**DON'T:**
```yaml
violations:
  - file: test.py
    expires: 2099-12-31  # ❌ Effectively permanent
```

**DO:**
```yaml
violations:
  - file: test.py
    expires: 2026-03-31  # ✅ Realistic deadline
    owner: qa-team
    reason: Legacy test pending rewrite
```

## 12. Related Components

### Dependencies
- `ast` - Python AST parsing
- `pathlib` - File path handling
- `yaml` - Configuration parsing
- `pytest` - Test framework integration
- `watchdog` - File system monitoring

### Integration Points
- **Git Hooks** - Pre-commit integration
- **GitHub Actions** - CI/CD integration
- **Pytest** - Plugin system
- **Allure** - Report integration

---

## 📊 Usage Statistics

### Typical Performance
- **Pre-commit audit:** < 2 seconds (staged files only)
- **Full audit:** 5-10 seconds (all files)
- **File watcher:** < 1 second (single file)
- **CI/CD:** 30-60 seconds (7 parallel checks)

### Violation Detection Rate
- **Average violations per commit:** 0.2 (1 in 5 commits)
- **Most common violations:**
  1. Direct locators in tests (40%)
  2. Manual time.sleep() (25%)
  3. Missing markers (20%)
  4. Poor naming (15%)

---

## 📚 Related Documentation

- [Strict Rules](../10-Rules-And-Standards/Strict-Rules.md)
- [Anti-Patterns](../10-Rules-And-Standards/Anti-Patterns.md)
- [Baseline Allow-List](Baseline-Allow-List.md)
- [Pre-Commit Hooks](Pre-Commit-Hooks.md)
- [CI/CD Integration](CICD-Integration.md)

---

**Last Updated:** February 1, 2026  
**Component Version:** 1.0.0

---

**"Automated Governance for Consistent Architecture"**
