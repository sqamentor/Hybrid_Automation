# Engine Selection System - Intelligent Playwright/Selenium Routing

## 1. Purpose
- **Why this component exists**: Automatically selects the optimal UI automation engine (Playwright or Selenium) based on test characteristics and application context
- **What problem it solves**: Eliminates manual engine selection, optimizes test execution, leverages strengths of each engine for specific scenarios

## 2. Scope

### What is Included
- Priority-based decision matrix with 20+ rules
- YAML-configurable decision logic
- Confidence scoring (0-100%)
- LRU caching for performance
- Module-level profiles
- Custom override support
- Fallback engine specification
- Decision logging and metrics

### What is Excluded
- Actual browser automation (delegated to engines)
- Test execution
- Page object creation
- Test data generation

## 3. Current Implementation

### Summary
The Engine Selector uses a priority-weighted rule evaluation system. Rules are defined in YAML, sorted by priority (0-100), and evaluated sequentially. The first matching rule with highest priority wins. Decisions are cached for performance.

### Key Classes, Files, and Modules

**File:** `framework/core/engine_selector.py`

**Main Class:** `EngineSelector`

**Config File:** `config/engine_decision_matrix.yaml`

**Key Classes:**
- `EngineDecision` - Dataclass holding decision result
- `CacheEntry` - Dataclass for cache management
- `EngineSelector` - Main selection logic

## 4. File & Code Mapping

### File: `framework/core/engine_selector.py` (577 lines)

**Responsibilities:**
- Load and parse YAML decision matrix
- Sort rules by priority
- Evaluate test metadata against rules
- Cache decisions for performance
- Provide cache statistics
- Handle fallback scenarios

**Key Code Sections:**

```python
# Lines 1-30: Imports, dataclass definitions
# Lines 32-76: EngineSelector.__init__() - Load config, sort rules, init cache
# Lines 78-93: _sort_rules_by_priority() - Priority-based sorting
# Lines 95-180: select_engine() - Main decision logic with caching
# Lines 182-250: _evaluate_rules() - Rule matching logic
# Lines 252-300: _match_condition() - Condition evaluation
# Lines 302-350: _apply_module_profile() - Module-based defaults
# Lines 352-400: _check_custom_overrides() - Manual overrides
# Lines 402-450: get_cache_stats() - Cache metrics
# Lines 452-500: clear_cache() - Cache management
# Lines 502-577: Helper methods
```

### File: `config/engine_decision_matrix.yaml` (250+ lines)

**Structure:**
```yaml
engine_selection_rules:
  - name: "Rule Name"
    priority: 95  # 0-100, higher = evaluated first
    condition:
      # Matching criteria
      auth_type: ["SSO", "MFA"]
      ui_framework: "React"
    engine: "playwright"  # or "selenium"
    confidence: 90  # 0-100
    reason: "Why this engine is better"
    tags: ["modern", "security"]
```

## 5. Execution Flow

### Step-by-Step Runtime Behavior

#### Example: Selecting Engine for Modern SPA Test

```python
metadata = {
    "test_name": "test_checkout_flow",
    "module": "checkout",
    "ui_framework": "React",
    "api_validation_required": True,
    "markers": ["modern_spa", "api_validation"]
}

decision = selector.select_engine(metadata)
# → Result: "playwright", confidence: 95%
```

**Flow:**

1. **Cache Lookup** (< 1ms)
   - Calculate metadata hash
   - Check if decision cached
   - Return cached decision if hit

2. **Rule Evaluation** (if cache miss)
   - Iterate rules by priority (highest first)
   - For each rule:
     - Check if condition matches metadata
     - If match found, create decision
     - Break loop (first match wins)

3. **Module Profile Application**
   - If no rule matched, check module profiles
   - Apply default engine for module type

4. **Custom Override Check**
   - Check for explicit overrides in config
   - Override previous decision if found

5. **Fallback Handling**
   - If still no decision, use default (Playwright)
   - Log warning

6. **Cache Storage**
   - Store decision in LRU cache
   - Update cache statistics

7. **Return Decision**
   - Return EngineDecision object with:
     - engine: "playwright" or "selenium"
     - confidence: 0-100
     - reason: explanation
     - rule_name: matched rule
     - priority: rule priority

### Sync vs Async Behavior
- **Fully synchronous** - All operations are blocking
- No async support currently
- Cache operations are instant (in-memory dict)

## 6. Inputs & Outputs

### Initialization Parameters

```python
EngineSelector(cache_size: int = 100, cache_ttl: int = 3600)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cache_size` | `int` | 100 | Max cached decisions (LRU eviction) |
| `cache_ttl` | `int` | 3600 | Cache TTL in seconds |

### Method Inputs

#### select_engine()

```python
select_engine(test_metadata: Dict[str, Any]) -> EngineDecision
```

**Expected Metadata Keys:**

| Key | Type | Required | Example |
|-----|------|----------|---------|
| `test_name` | `str` | No | `"test_login"` |
| `module` | `str` | No | `"checkout"`, `"admin"` |
| `ui_framework` | `str` | No | `"React"`, `"Angular"`, `"JSP"` |
| `auth_type` | `str/List` | No | `"SSO"`, `["MFA", "SAML"]` |
| `markers` | `List[str]` | No | `["smoke", "modern_spa"]` |
| `iframe_depth` | `int` | No | `3` (number of nested iframes) |
| `legacy_ui` | `bool` | No | `True/False` |
| `mobile_first` | `bool` | No | `True/False` |
| `xhr_heavy` | `bool` | No | `True/False` |
| `api_validation_required` | `bool` | No | `True/False` |

### Config Dependencies

**Config File:** `config/engine_decision_matrix.yaml`

```yaml
engine_selection_rules:
  # HIGH PRIORITY RULES (90-100)
  - name: "Enterprise Authentication"
    priority: 98
    condition:
      auth_type: ["SSO", "MFA", "SAML"]
    engine: "selenium"
    confidence: 95
    reason: "Selenium has better SSO/MFA support"
    
  - name: "Deep Iframe Structures"
    priority: 95
    condition:
      iframe_depth: ">= 3"
    engine: "selenium"
    confidence: 92
    reason: "Selenium handles nested iframes better"
    
  - name: "Modern SPA with API Testing"
    priority: 92
    condition:
      ui_framework: ["React", "Vue", "Angular"]
      api_validation_required: true
    engine: "playwright"
    confidence: 95
    reason: "Playwright has native network interception"

# Module Profiles (default engine per module)
module_profiles:
  checkout: "playwright"
  admin: "selenium"
  dashboard: "playwright"
  legacy: "selenium"

# Custom Overrides (force specific engine)
custom_overrides:
  "test_special_case": "selenium"
  "test_specific_flow": "playwright"
```

### Return Values

**Returns:** `EngineDecision` dataclass

```python
@dataclass
class EngineDecision:
    engine: str  # "playwright" or "selenium"
    confidence: int  # 0-100
    reason: str  # Explanation
    rule_name: str  # Matched rule name
    fallback_engine: Optional[str] = None  # Backup engine
    priority: int = 0  # Rule priority
    cache_hit: bool = False  # From cache?
```

**Example:**
```python
EngineDecision(
    engine="playwright",
    confidence=95,
    reason="Modern SPA with API validation needs",
    rule_name="Modern SPA with API Testing",
    fallback_engine="selenium",
    priority=92,
    cache_hit=False
)
```

## 7. Design Decisions

### Why This Approach Was Chosen

#### 1. **YAML Configuration vs Hardcoded Logic**

**Decision:** Use YAML for decision rules

**Why:**
- Non-developers can modify rules
- No code changes for new rules
- Easy to version control
- Clear, readable rule definitions
- Hot-reload possible (restart not needed)

**Trade-offs:**
- ✅ Flexibility, maintainability
- ❌ Additional file to manage
- ❌ YAML parsing overhead (mitigated by caching)

#### 2. **Priority-Based vs Sequential Evaluation**

**Decision:** Priority-weighted rules (0-100)

**Why:**
- Critical rules (SSO, security) evaluated first
- Prevents wrong engine selection
- Clear precedence ordering
- Easy to add high-priority rules without reordering entire file

**Trade-offs:**
- ✅ Predictable, explicit ordering
- ❌ Requires understanding priority system
- ❌ Potential for priority conflicts (manually resolved)

#### 3. **LRU Caching vs No Caching**

**Decision:** Implement LRU cache with TTL

**Why:**
- Tests often have similar metadata
- Avoid repeated YAML parsing and rule evaluation
- Significant performance improvement (1000x faster for cached decisions)
- TTL prevents stale decisions

**Trade-offs:**
- ✅ Performance (< 1ms vs ~10ms)
- ❌ Memory usage (small, ~100 entries = ~10KB)
- ❌ Potential stale decisions (mitigated by TTL)

#### 4. **First-Match-Wins vs Score-Based Selection**

**Decision:** First matching rule (by priority) wins

**Why:**
- Simple, deterministic
- Fast evaluation (stops at first match)
- Clear decision logic
- No ambiguity about which engine to use

**Alternative Considered:**
- Score all rules, pick highest score
- More complex, harder to predict, slower

## 8. Rules & Constraints

### Hard Rules Enforced by the Framework

#### ✅ MUST DO:

1. **Rule Priority Must Be 0-100**
   ```yaml
   priority: 95  # ✅ Valid
   priority: 150  # ❌ Invalid, ignored or clamped
   ```

2. **Engine Must Be "playwright" or "selenium"**
   ```yaml
   engine: "playwright"  # ✅ Valid
   engine: "cypress"  # ❌ Invalid, will cause error
   ```

3. **Confidence Must Be 0-100**
   ```yaml
   confidence: 95  # ✅ Valid
   confidence: 120  # ❌ Invalid, clamped to 100
   ```

4. **Condition Keys Must Match Metadata**
   ```yaml
   condition:
     ui_framework: "React"  # ✅ Matches metadata key
     ui_type: "React"  # ❌ Won't match (wrong key)
   ```

#### ❌ MUST NOT DO:

1. **Don't Modify engine_decision_matrix.yaml While Tests Running**
   - Changes not reflected until restart
   - Cache invalidation not automatic

2. **Don't Create Conflicting Rules at Same Priority**
   ```yaml
   # BAD - Both priority 95, ambiguous order
   - name: "Rule A"
     priority: 95
     condition: { module: "checkout" }
     engine: "playwright"
   
   - name: "Rule B"
     priority: 95
     condition: { module: "checkout" }
     engine: "selenium"
   ```

3. **Don't Use Complex Nested Conditions**
   - Condition evaluation is simple key-value matching
   - No AND/OR logic within single condition block

### Assumptions Developers Must Not Violate

1. **YAML File Must Exist**
   - Path: `config/engine_decision_matrix.yaml`
   - Framework will error if missing

2. **Test Metadata Should Include Key Fields**
   - At minimum: `module` or `test_name`
   - More metadata = better decisions

3. **Priority Values Are Unique (Recommended)**
   - While not enforced, unique priorities avoid ambiguity

4. **Cache Size Should Be >= 10**
   - Too small = excessive evictions
   - Recommended: 100-500

## 9. Error Handling & Edge Cases

### Known Failure Scenarios

#### 1. **YAML Parse Error**

```python
# Scenario: Invalid YAML syntax
selector = EngineSelector()
# → Raises yaml.YAMLError
```

**Fallback Logic:**
- Error raised, test execution stops
- No automatic fallback
- Fix YAML and restart

#### 2. **No Matching Rule**

```python
# Scenario: Metadata doesn't match any rule
metadata = {"unknown_key": "value"}
decision = selector.select_engine(metadata)

# Behavior:
# - Returns default engine (Playwright)
# - Confidence: 50 (low)
# - Reason: "No rule matched, using default"
# - Logs warning
```

#### 3. **Conflicting Custom Override**

```python
# Scenario: Custom override contradicts rule
# In YAML:
# custom_overrides:
#   test_checkout: "selenium"
# 
# But rule says: "playwright"

# Behavior:
# - Custom override wins (priority)
# - Warning logged about conflict
```

#### 4. **Cache Memory Exhaustion**

```python
# Scenario: cache_size=10000, 100000 unique test metadata
selector = EngineSelector(cache_size=10000)

# Behavior:
# - LRU eviction kicks in
# - Oldest cached decisions removed
# - No memory leak
# - Slight performance degradation for evicted entries
```

### Edge Cases

#### 1. **Empty Metadata**

```python
decision = selector.select_engine({})
# Returns default engine, low confidence
```

#### 2. **Partial Metadata Match**

```yaml
# Rule requires: ui_framework AND api_validation_required
condition:
  ui_framework: "React"
  api_validation_required: true

# Test metadata: { "ui_framework": "React" }
# → Rule does NOT match (missing api_validation_required)
```

#### 3. **List Conditions**

```yaml
# Condition with list of values
condition:
  auth_type: ["SSO", "MFA", "SAML"]

# Metadata: { "auth_type": "SSO" }
# → Matches (SSO in list)

# Metadata: { "auth_type": "Basic" }
# → Does NOT match (Basic not in list)
```

#### 4. **Numeric Comparisons**

```yaml
# Condition with comparison
condition:
  iframe_depth: ">= 3"

# Metadata: { "iframe_depth": 5 }
# → Matches (5 >= 3)

# Metadata: { "iframe_depth": 2 }
# → Does NOT match (2 < 3)
```

## 10. Extensibility & Customization

### How This Can Be Extended Safely

#### 1. **Add New Decision Rules**

**File:** `config/engine_decision_matrix.yaml`

```yaml
engine_selection_rules:
  # Add new rule with appropriate priority
  - name: "WebSocket Heavy Applications"
    priority: 88  # High priority
    condition:
      websocket_required: true
      real_time: true
    engine: "playwright"
    confidence: 92
    reason: "Playwright has better WebSocket support"
    tags: ["real-time", "websocket"]
```

#### 2. **Custom Metadata Keys**

```python
# In test file
metadata = {
    "test_name": "test_custom",
    "my_custom_key": "special_value",  # Custom key
    "requires_parallel": True
}

decision = selector.select_engine(metadata)
```

**In YAML:**
```yaml
- name: "Custom Rule"
  priority: 85
  condition:
    my_custom_key: "special_value"
  engine: "playwright"
  confidence: 90
  reason: "Custom logic"
```

#### 3. **Subclass EngineSelector**

```python
class CustomEngineSelector(EngineSelector):
    """Custom selector with additional logic"""
    
    def select_engine(self, metadata):
        # Pre-processing
        metadata = self._enrich_metadata(metadata)
        
        # Call parent
        decision = super().select_engine(metadata)
        
        # Post-processing
        decision = self._apply_business_rules(decision)
        
        return decision
    
    def _enrich_metadata(self, metadata):
        """Add computed metadata"""
        if "url" in metadata:
            metadata["is_mobile_url"] = "mobile" in metadata["url"]
        return metadata
```

#### 4. **Custom Condition Evaluators**

```python
class AdvancedEngineSelector(EngineSelector):
    def _match_condition(self, condition, metadata):
        """Override condition matching"""
        
        # Handle custom operators
        for key, expected in condition.items():
            if key.endswith("_regex"):
                # Regex matching
                import re
                if not re.match(expected, metadata.get(key[:-6], "")):
                    return False
            else:
                # Default matching
                if not self._default_match(key, expected, metadata):
                    return False
        return True
```

### Plugin or Override Points

#### 1. **Decision Post-Processor**

```python
class PostProcessedSelector(EngineSelector):
    def __init__(self, *args, post_processor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_processor = post_processor
    
    def select_engine(self, metadata):
        decision = super().select_engine(metadata)
        
        if self.post_processor:
            decision = self.post_processor(decision, metadata)
        
        return decision

# Usage
def my_post_processor(decision, metadata):
    # Override for specific tests
    if metadata.get("force_selenium"):
        decision.engine = "selenium"
    return decision

selector = PostProcessedSelector(post_processor=my_post_processor)
```

#### 2. **Cache Strategy Override**

```python
class RedisBackedSelector(EngineSelector):
    """Use Redis for distributed caching"""
    
    def __init__(self, *args, redis_client=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis = redis_client
    
    def _get_from_cache(self, metadata_hash):
        if self.redis:
            cached = self.redis.get(f"engine_decision:{metadata_hash}")
            return json.loads(cached) if cached else None
        return super()._get_from_cache(metadata_hash)
```

## 11. Anti-Patterns & What NOT to Do

### Common Mistakes

#### ❌ **1. Ignoring Priority**

```yaml
# BAD - All same priority, unpredictable order
- name: "Rule A"
  priority: 50
  engine: "playwright"

- name: "Rule B"
  priority: 50  # ❌ Same priority
  engine: "selenium"

# GOOD - Distinct priorities
- name: "Rule A"
  priority: 90  # ✅ Higher priority
  engine: "playwright"

- name: "Rule B"
  priority: 80  # ✅ Lower priority
  engine: "selenium"
```

#### ❌ **2. Overly Specific Rules**

```yaml
# BAD - Too specific, rarely matches
- name: "Ultra Specific Rule"
  priority: 95
  condition:
    test_name: "test_checkout_with_coupon_and_gift_card_on_tuesday"
    browser: "chrome"
    version: "119.0.6045.105"
  engine: "playwright"
  # ❌ Will almost never match

# GOOD - Broad, reusable
- name: "Checkout Module"
  priority: 85
  condition:
    module: "checkout"
  engine: "playwright"
  # ✅ Matches all checkout tests
```

#### ❌ **3. Not Using Confidence Scores**

```yaml
# BAD - No confidence differentiation
- name: "Rule A"
  confidence: 50  # ❌ Low confidence but no fallback
  engine: "playwright"

# GOOD - Provide fallback for low confidence
- name: "Rule A"
  confidence: 50
  engine: "playwright"
  fallback: "selenium"  # ✅ Fallback option
```

#### ❌ **4. Hardcoding Engine in Tests**

```python
# BAD - Defeats purpose of selector
from playwright.sync_api import sync_playwright
browser = sync_playwright().start().chromium.launch()
# ❌ Hardcoded Playwright

# GOOD - Let selector decide
from framework.core.engine_selector import EngineSelector
selector = EngineSelector()
decision = selector.select_engine(test_metadata)
# Use decision.engine
```

#### ❌ **5. Not Testing Decision Logic**

```python
# BAD - No validation of selector behavior
# Just assume it works

# GOOD - Test selector decisions
def test_engine_selector():
    selector = EngineSelector()
    
    # Test SSO rule
    metadata = {"auth_type": "SSO"}
    decision = selector.select_engine(metadata)
    assert decision.engine == "selenium"
    assert decision.confidence >= 90
```

### Dangerous Changes

#### ⚠️ **Removing Default Fallback**

```python
# DANGEROUS - Can cause NoneType errors
def select_engine(self, metadata):
    # ... rule evaluation ...
    if not decision:
        return None  # ❌ Don't return None

# SAFE - Always return valid decision
def select_engine(self, metadata):
    # ... rule evaluation ...
    if not decision:
        return EngineDecision(
            engine="playwright",  # ✅ Default
            confidence=50,
            reason="No rule matched"
        )
```

#### ⚠️ **Circular Dependencies in Conditions**

```yaml
# DANGEROUS - Circular logic
- name: "Rule A"
  condition:
    requires_rule_b: true
  engine: "playwright"

- name: "Rule B"
  condition:
    requires_rule_a: true  # ❌ Circular
  engine: "selenium"
```

#### ⚠️ **Ignoring Cache TTL**

```python
# DANGEROUS - Stale cached decisions
selector = EngineSelector(cache_ttl=999999)  # ❌ Extremely long TTL
# Rules change, but cached decisions persist forever

# SAFE - Reasonable TTL
selector = EngineSelector(cache_ttl=3600)  # ✅ 1 hour
```

## 12. Related Components

### Dependencies

1. **`yaml`** - YAML parsing
2. **`hashlib`** - Metadata hashing for caching
3. **`functools.lru_cache`** - LRU caching support
4. **`pathlib.Path`** - File path handling
5. **`config.settings`** - Settings manager
6. **`config/engine_decision_matrix.yaml`** - Decision rules

### Upstream Components (Call EngineSelector)

1. **Modern Engine Selector** (`framework/core/modern_engine_selector.py`)
   - Enhanced version with additional features
   - Uses EngineSelector as base

2. **AI Engine Selector** (`framework/core/ai_engine_selector.py`)
   - AI-powered decision enhancement
   - Calls EngineSelector, applies ML

3. **Workflow Orchestrator** (`framework/core/workflow_orchestrator.py`)
   - Coordinates test workflow
   - Uses engine selection for test setup

4. **conftest.py**
   - Creates engine selector instance
   - Provides as fixture to tests

### Downstream Links (Called by EngineSelector)

1. **Settings Manager** (`config/settings.py`)
   - Loads YAML configuration
   - Provides config access

2. **Playwright Engine** (`framework/ui/playwright_engine.py`)
   - Instantiated if "playwright" selected

3. **Selenium Engine** (`framework/ui/selenium_engine.py`)
   - Instantiated if "selenium" selected

4. **UI Factory** (`framework/ui/ui_factory.py`)
   - Creates engine instance based on decision

### Integration Points

```
┌──────────────────┐
│   Test File      │
└────────┬─────────┘
         │ provides metadata
         ▼
┌──────────────────┐         ┌─────────────────────┐
│ EngineSelector   │────────▶│ engine_decision    │
│                  │  reads  │ _matrix.yaml        │
└────────┬─────────┘         └─────────────────────┘
         │ returns decision
         ▼
┌──────────────────┐
│   UI Factory     │
│                  │
└────────┬─────────┘
         │ creates
         ▼
┌──────────────────┐    or    ┌──────────────────┐
│ Playwright       │          │ Selenium         │
│ Engine           │          │ Engine           │
└──────────────────┘          └──────────────────┘
```

---

**Related Documentation:**
- [UI Factory](../04-Testing-Features/UI-Testing/UI-Factory.md)
- [Playwright Engine](../04-Testing-Features/UI-Testing/Playwright-Engine.md)
- [Selenium Engine](../04-Testing-Features/UI-Testing/Selenium-Engine.md)
- [Configuration Guide](../05-Configuration/Engine-Decision-Matrix.md)

---

**Last Updated:** February 1, 2026  
**Component Version:** 1.0.0
