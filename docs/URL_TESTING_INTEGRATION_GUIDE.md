# URL Testing Integration Guide

**Purpose:** Visual guide showing how URL testing components integrate with existing framework  
**Audience:** Developers implementing URL testing  
**Status:** Reference Guide  

---

## 📊 BEFORE vs AFTER

### BEFORE: Existing Framework Structure

```
Hybrid_Automation/
├── framework/
│   ├── microservices/
│   │   ├── base.py                  ✅ KEEP: BaseService, ServiceStatus, HealthCheck
│   │   └── services.py              ✅ KEEP: Service registry
│   ├── core/
│   │   ├── project_manager.py       ✅ USE: Project detection from URLs
│   │   ├── session_manager.py       ✅ KEEP: Session management
│   │   └── smart_actions.py         ✅ KEEP: Smart actions
│   ├── testing/
│   │   ├── distributed.py           ✅ KEEP: Distributed testing
│   │   └── visual.py                ✅ KEEP: Visual testing
│   └── config/
│       └── config_manager.py        ✅ USE: Configuration loading
├── test_data/
│   └── bookslot/
│       ├── bookslot_data.json       ✅ KEEP: Existing test data
│       ├── bookslot_data.yaml       ✅ KEEP: Alternative format
│       └── ...                      ✅ KEEP: Other data files
├── tests/
│   └── bookslot/
│       ├── fixtures/
│       │   └── __init__.py          ✅ EXTEND: Add URL fixtures here
│       ├── pages/
│       │   ├── test_page_p1.py      ✅ KEEP: 139 existing tests
│       │   └── ...                  ✅ KEEP: All page tests
│       └── conftest.py              ✅ KEEP: Existing fixtures
├── config/
│   ├── projects.yaml                ✅ EXTEND: Add URL testing config
│   └── environments.yaml            ✅ KEEP: Environment settings
└── utils/
    └── fake_data_generator.py       ✅ EXTEND: Add workflow loader
```

### AFTER: With URL Testing Integration

```
Hybrid_Automation/
├── framework/
│   ├── microservices/
│   │   ├── base.py                  ✅ UNCHANGED
│   │   ├── services.py              ➕ ENHANCED: Register URL services
│   │   └── url_testing_service.py   ➕ NEW: 3 microservices (URLTesting, URLData, URLValidation)
│   ├── core/
│   │   ├── project_manager.py       ✅ UNCHANGED (but used by URL services)
│   │   ├── session_manager.py       ✅ UNCHANGED
│   │   └── smart_actions.py         ✅ UNCHANGED
│   ├── testing/
│   │   ├── distributed.py           ✅ UNCHANGED
│   │   ├── visual.py                ✅ UNCHANGED
│   │   ├── url_data_manager.py      ➕ NEW: Data orchestrator (Manager pattern)
│   │   ├── url_builder.py           ➕ NEW: URL construction (Builder pattern)
│   │   └── url_validator.py         ➕ NEW: URL validation (Validator pattern)
│   └── config/
│       └── config_manager.py        ✅ UNCHANGED
├── test_data/
│   └── bookslot/
│       ├── bookslot_data.json       ✅ UNCHANGED
│       ├── bookslot_data.yaml       ✅ UNCHANGED
│       ├── bookslot_workflows.json  ➕ NEW: Workflow test data (35+ cases)
│       └── ...                      ✅ UNCHANGED
├── tests/
│   └── bookslot/
│       ├── fixtures/
│       │   └── __init__.py          ➕ ENHANCED: Add 6 URL fixtures
│       ├── pages/
│       │   ├── test_page_p1.py      ✅ UNCHANGED (139 tests unaffected)
│       │   └── ...                  ✅ UNCHANGED
│       ├── url_testing/             ➕ NEW FOLDER: URL test suite
│       │   ├── __init__.py          ➕ NEW: Module init
│       │   ├── test_workflow_urls_p1.py  ➕ NEW: P1 URL tests (10 tests)
│       │   ├── test_workflow_urls_p2.py  ➕ NEW: P2 URL tests (10 tests)
│       │   ├── test_workflow_urls_p3.py  ➕ NEW: P3 URL tests (10 tests)
│       │   ├── test_workflow_urls_p4.py  ➕ NEW: P4 URL tests (5 tests)
│       │   ├── test_workflow_urls_p5.py  ➕ NEW: P5 URL tests (5 tests)
│       │   ├── test_workflow_urls_p6.py  ➕ NEW: P6 URL tests (5 tests)
│       │   └── test_workflow_urls_p7.py  ➕ NEW: P7 URL tests (5 tests)
│       └── conftest.py              ✅ UNCHANGED
├── config/
│   ├── projects.yaml                ➕ ENHANCED: Add url_testing section
│   ├── url_testing.yaml             ➕ NEW: Service configuration
│   └── environments.yaml            ✅ UNCHANGED
└── utils/
    └── fake_data_generator.py       ➕ ENHANCED: Add load_workflow_data()

LEGEND:
✅ UNCHANGED = Keep as-is, zero modifications
➕ NEW = New file/folder created
➕ ENHANCED = Existing file extended with new content
```

---

## 🔌 INTEGRATION POINTS

### Integration Point 1: Microservices

**Location:** `framework/microservices/`

**What Exists:**
```python
# framework/microservices/base.py
class BaseService(ABC):
    """Abstract base class for all microservices"""
    @abstractmethod
    async def _initialize(self) -> None: pass
    @abstractmethod
    async def _cleanup(self) -> None: pass
    @abstractmethod
    async def _health_check_impl(self) -> HealthCheck: pass
```

**What We Add:**
```python
# framework/microservices/url_testing_service.py
class URLTestingService(BaseService):  # ← Extends existing BaseService
    """URL Testing Microservice"""
    
    async def _initialize(self) -> None:
        # Initialize service resources
        pass
    
    async def _cleanup(self) -> None:
        # Cleanup resources
        pass
    
    async def _health_check_impl(self) -> HealthCheck:
        # Health check implementation
        pass
```

**How They Connect:**
- URLTestingService **inherits** from BaseService
- Uses existing BaseService lifecycle methods
- Registers with existing service discovery
- Publishes events to existing message bus

---

### Integration Point 2: Manager Pattern

**Location:** `framework/testing/`

**What Exists:**
```python
# framework/core/project_manager.py
class ProjectManager:
    """Manages multi-project structure"""
    def detect_project_from_url(self, url: str) -> Tuple[str, str]:
        # Returns (project_name, environment)
        pass

# framework/core/session_manager.py
class SessionManager:
    """Manages test sessions"""
    pass
```

**What We Add:**
```python
# framework/testing/url_data_manager.py
class URLDataManager:  # ← Follows same Manager pattern
    """Manages URL test data loading and generation"""
    
    def __init__(self, project: str = "bookslot"):
        self.project = project
    
    def load_test_cases(self, environment: str) -> List[URLTestCase]:
        # Load from test_data/bookslot/bookslot_workflows.json
        pass
```

**How They Connect:**
- URLDataManager follows **exact same pattern** as ProjectManager/SessionManager
- Uses ProjectManager for project detection (doesn't duplicate logic)
- Consistent API design across all managers
- Same initialization and lifecycle patterns

---

### Integration Point 3: Data Loading

**Location:** `utils/fake_data_generator.py`

**What Exists:**
```python
# utils/fake_data_generator.py (line 224)
def load_bookslot_data(filename: str = "bookslot_data.json") -> List[Dict[str, Any]]:
    """Load bookslot test data from JSON/YAML"""
    test_data_dir = Path(__file__).parent.parent / "test_data" / "bookslot"
    file_path = test_data_dir / filename
    
    if file_path.suffix == ".json":
        with open(file_path, "r") as f:
            return json.load(f)
    elif file_path.suffix in [".yaml", ".yml"]:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
```

**What We Add:**
```python
# utils/fake_data_generator.py (NEW FUNCTION - same pattern)
def load_workflow_data(
    project: str = "bookslot",
    filename: str = "workflows.json",
    environment: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Load workflow test data from JSON/YAML"""
    # ← SAME PATTERN as load_bookslot_data
    test_data_dir = Path(__file__).parent.parent / "test_data" / project
    file_path = test_data_dir / f"{project}_{filename}"
    
    # Same loading logic...
    if file_path.suffix == ".json":
        with open(file_path, "r") as f:
            data = json.load(f)
    
    workflows = data.get("workflows", [])
    
    # Filter by environment
    if environment:
        workflows = [w for w in workflows if w.get("environment") == environment]
    
    return workflows
```

**How They Connect:**
- Same file structure pattern (`test_data/{project}/{filename}`)
- Same loading mechanism (JSON/YAML)
- Same error handling
- Same return type (List[Dict])
- URLDataManager **calls** this function (reuses existing pattern)

---

### Integration Point 4: Fixtures

**Location:** `tests/bookslot/fixtures/__init__.py`

**What Exists:**
```python
# tests/bookslot/fixtures/__init__.py (303 lines)
@pytest.fixture
def valid_basic_info() -> Dict[str, str]:
    """Valid basic info test data"""
    timestamp = datetime.now().strftime("%H%M%S")
    return {
        "name": f"Test User {timestamp}",
        "email": f"testuser{timestamp}@example.com",
        "phone": "5555551234"
    }

@pytest.fixture
def valid_insurance_info() -> Dict[str, str]:
    """Valid insurance info test data"""
    # ... existing fixture ...
```

**What We Add:**
```python
# tests/bookslot/fixtures/__init__.py (APPEND TO SAME FILE)

# ========================================================================
# NEW SECTION: URL Testing Fixtures
# ========================================================================

@pytest.fixture(scope="session")
def url_testing_service():
    """URL Testing Microservice instance"""
    from framework.microservices.url_testing_service import URLTestingService
    service = URLTestingService()
    asyncio.run(service.start())
    yield service
    asyncio.run(service.stop())

@pytest.fixture(scope="session")
def url_data_manager():
    """URL Data Manager instance"""
    from framework.testing.url_data_manager import URLDataManager
    return URLDataManager(project="bookslot")

@pytest.fixture
def url_builder(base_url: str):
    """URL Builder instance"""
    from framework.testing.url_builder import URLBuilder
    return URLBuilder(base_url=base_url)

@pytest.fixture
def url_validator(page: Page):
    """URL Validator instance"""
    from framework.testing.url_validator import URLValidator
    return URLValidator(page=page)
```

**How They Connect:**
- Added to **SAME FILE** as existing fixtures (not new conftest.py)
- Same scope patterns (session for services, function for utilities)
- Same naming convention (component_name pattern)
- Same documentation style
- Tests can use both old and new fixtures together

**Anti-Pattern (What We DON'T Do):**
```python
# ❌ WRONG: Creating new conftest.py
# tests/bookslot/url_testing/conftest.py  ← DON'T DO THIS

# This would:
# - Break centralized fixture pattern
# - Create fixture conflicts
# - Make maintenance harder
# - Violate existing structure
```

---

### Integration Point 5: Configuration

**Location:** `config/projects.yaml`

**What Exists:**
```yaml
# config/projects.yaml
projects:
  bookslot:
    name: "Bookslot"
    environments:
      staging:
        base_url: "https://staging.bookslot.com"
        database:
          host: "staging-db.bookslot.com"
      production:
        base_url: "https://www.bookslot.com"
        database:
          host: "prod-db.bookslot.com"
    
    pages:
      P1: "/basic-info"
      P2: "/insurance"
      P3: "/schedule"
      # ... P4-P7 ...
```

**What We Add:**
```yaml
# config/projects.yaml (EXTEND EXISTING STRUCTURE)
projects:
  bookslot:
    name: "Bookslot"
    environments:
      staging:
        base_url: "https://staging.bookslot.com"
        database:
          host: "staging-db.bookslot.com"
      production:
        base_url: "https://www.bookslot.com"
        database:
          host: "prod-db.bookslot.com"
    
    pages:
      P1: "/basic-info"
      P2: "/insurance"
      P3: "/schedule"
      # ... P4-P7 ...
    
    # ========================================================================
    # NEW SECTION: URL Testing Configuration
    # ========================================================================
    url_testing:  # ← NEW nested section
      enabled: true
      url_format: "query_string"
      
      environments:
        staging:
          workflows_file: "bookslot_workflows.json"
          test_data_mode: "manual"
        production:
          workflows_file: "bookslot_workflows_prod.json"
          test_data_mode: "manual"
      
      validation:
        timeout_ms: 10000
        expected_status: 200
```

**How They Connect:**
- Nested under existing `bookslot` project
- Uses existing environment names (staging, production)
- Leverages existing base_url from parent config
- Same YAML structure pattern
- ConfigManager loads it automatically

---

### Integration Point 6: Test Structure

**Location:** `tests/bookslot/`

**What Exists:**
```
tests/bookslot/
├── __init__.py
├── conftest.py                       ← Uses fixtures from fixtures/__init__.py
├── fixtures/
│   └── __init__.py                   ← Centralized fixtures (20+ existing)
└── pages/
    ├── __init__.py
    ├── test_page_p1.py                ← 20 tests for P1
    ├── test_page_p2.py                ← 20 tests for P2
    ├── test_page_p3.py                ← 20 tests for P3
    ├── test_page_p4.py                ← 20 tests for P4
    ├── test_page_p5.py                ← 20 tests for P5
    ├── test_page_p6.py                ← 20 tests for P6
    └── test_page_p7.py                ← 19 tests for P7
    TOTAL: 139 existing tests ✅
```

**What We Add:**
```
tests/bookslot/
├── __init__.py                       ✅ UNCHANGED
├── conftest.py                       ✅ UNCHANGED
├── fixtures/
│   └── __init__.py                   ➕ ENHANCED: Add 6 URL fixtures
├── pages/
│   └── ...                           ✅ UNCHANGED (all 139 tests untouched)
└── url_testing/                      ➕ NEW FOLDER
    ├── __init__.py                   ➕ NEW
    ├── test_workflow_urls_p1.py      ➕ NEW: 10 URL tests for P1
    ├── test_workflow_urls_p2.py      ➕ NEW: 10 URL tests for P2
    ├── test_workflow_urls_p3.py      ➕ NEW: 10 URL tests for P3
    ├── test_workflow_urls_p4.py      ➕ NEW: 5 URL tests for P4
    ├── test_workflow_urls_p5.py      ➕ NEW: 5 URL tests for P5
    ├── test_workflow_urls_p6.py      ➕ NEW: 5 URL tests for P6
    └── test_workflow_urls_p7.py      ➕ NEW: 5 URL tests for P7
    TOTAL: 50 new URL tests ➕

GRAND TOTAL: 139 (existing) + 50 (new) = 189 tests
```

**How They Connect:**
- New `url_testing/` folder is **sibling** to `pages/` (parallel structure)
- URL tests use fixtures from `tests/bookslot/fixtures/__init__.py` (same as page tests)
- URL tests use conftest.py (same as page tests)
- Zero modifications to existing page tests
- Both test suites coexist independently

**Anti-Pattern (What We DON'T Do):**
```
# ❌ WRONG: Creating separate fixture files
tests/bookslot/url_testing/
├── conftest.py              ← DON'T CREATE THIS
├── fixtures.py              ← DON'T CREATE THIS
└── test_workflow_urls_p1.py

# This would:
# - Break centralized fixture pattern
# - Create duplicate fixture logic
# - Increase maintenance burden
# - Violate framework conventions
```

---

## 🔄 DATA FLOW DIAGRAM

### How URL Testing Integrates With Existing Framework

```
┌─────────────────────────────────────────────────────────────────────┐
│                        TEST EXECUTION FLOW                          │
└─────────────────────────────────────────────────────────────────────┘

1. TEST INVOCATION (pytest)
   │
   ├─→ tests/bookslot/url_testing/test_workflow_urls_p1.py
   │   └─→ Uses fixtures from tests/bookslot/fixtures/__init__.py
   │       ├─→ url_testing_service  (session scope)
   │       ├─→ url_data_manager     (session scope)
   │       ├─→ url_builder          (function scope)
   │       └─→ url_validator        (function scope)
   │
2. FIXTURE INITIALIZATION
   │
   ├─→ url_testing_service fixture
   │   └─→ Creates URLTestingService(BaseService)  ← Extends framework BaseService
   │       ├─→ Registers with service discovery
   │       ├─→ Starts health check monitoring
   │       └─→ Connects to event bus
   │
   ├─→ url_data_manager fixture
   │   └─→ Creates URLDataManager("bookslot")
   │       └─→ Loads test_data/bookslot/bookslot_workflows.json
   │           └─→ Uses load_workflow_data() from utils/fake_data_generator.py
   │               ← REUSES existing data loading pattern
   │
   ├─→ url_builder fixture
   │   └─→ Creates URLBuilder(base_url)  ← Uses existing base_url fixture
   │       └─→ Uses URLFormat enum
   │
   └─→ url_validator fixture
       └─→ Creates URLValidator(page)  ← Uses existing page fixture (Playwright)
           └─→ Integrates with smart_actions
   │
3. TEST EXECUTION
   │
   ├─→ Load workflow test case from data
   │   └─→ URLDataManager.load_test_cases("staging")
   │       └─→ Returns List[URLTestCase] from JSON data
   │
   ├─→ Build URL with parameters
   │   └─→ URLBuilder.build(workflow_id="WF-001", query_params={...})
   │       └─→ Returns complete URL string
   │
   ├─→ Navigate to URL
   │   └─→ page.goto(url)  ← Uses existing Playwright page fixture
   │
   ├─→ Validate URL
   │   └─→ URLValidator.validate(url, expected_elements=[...])
   │       ├─→ Check HTTP status
   │       ├─→ Check element presence
   │       ├─→ Check error messages
   │       └─→ Check performance
   │
   └─→ Assert results
       └─→ assert result.is_valid
       └─→ assert result.status_code == 200
   │
4. REPORTING
   │
   ├─→ Allure reporting (existing integration)
   │   ├─→ Test results
   │   ├─→ Screenshots
   │   └─→ Logs
   │
   └─→ Service telemetry
       └─→ URLTestingService publishes metrics
           ├─→ url_validation_count
           ├─→ url_validation_duration
           └─→ url_validation_failures


┌─────────────────────────────────────────────────────────────────────┐
│                      MICROSERVICE INTERACTION                       │
└─────────────────────────────────────────────────────────────────────┘

URLTestingService (NEW)
  │
  ├─→ INHERITS FROM → BaseService (EXISTING)
  │   └─→ Uses existing lifecycle methods
  │       ├─→ _initialize()
  │       ├─→ _cleanup()
  │       └─→ _health_check_impl()
  │
  ├─→ USES → ProjectManager (EXISTING)
  │   └─→ detect_project_from_url(url)  ← Reuses project detection
  │
  ├─→ USES → ConfigManager (EXISTING)
  │   └─→ Loads config/url_testing.yaml
  │
  ├─→ DELEGATES TO → URLDataService (NEW)
  │   └─→ Manages test data loading
  │
  └─→ DELEGATES TO → URLValidationService (NEW)
      └─→ Performs URL validation

All services register with existing service discovery system
All services use existing observability framework (logging, metrics)
All services communicate via existing event bus
```

---

## ✅ ZERO-CONFLICT VALIDATION

### How We Ensure Zero Impact on Existing Tests

| Component | Existing | New | Integration Strategy | Conflict Risk |
|-----------|----------|-----|---------------------|---------------|
| **Microservices** | BaseService (base.py) | URLTestingService | Inheritance | ✅ ZERO - Different service names |
| **Managers** | ProjectManager, SessionManager | URLDataManager | Same pattern | ✅ ZERO - Different responsibilities |
| **Builders** | QueryBuilder, CommandBuilder | URLBuilder | Same pattern | ✅ ZERO - Different domains |
| **Validators** | DBValidator, PreFlightValidator | URLValidator | Same pattern | ✅ ZERO - Different validation targets |
| **Fixtures** | 20+ in fixtures/__init__.py | 6 new in same file | Append to file | ✅ ZERO - Different fixture names |
| **Test Data** | bookslot_data.json | bookslot_workflows.json | New file | ✅ ZERO - Separate files |
| **Config** | projects.yaml | Extended projects.yaml | Add section | ✅ ZERO - Nested under url_testing key |
| **Tests** | pages/ (139 tests) | url_testing/ (50 tests) | New folder | ✅ ZERO - Separate test modules |

**Validation Strategy:**
1. Run existing 139 tests BEFORE implementation → Baseline
2. Implement URL testing components
3. Run existing 139 tests AFTER implementation → Should be identical to baseline
4. Run new 50 URL tests → Should pass independently
5. Run ALL 189 tests together → Should all pass

---

## 📝 IMPLEMENTATION CHECKLIST

### Phase 1: Foundation (Days 1-2)
- [ ] Create `framework/microservices/url_testing_service.py`
  - [ ] URLTestingService(BaseService)
  - [ ] URLDataService(BaseService)
  - [ ] URLValidationService(BaseService)
  - [ ] Unit tests for all services
- [ ] Create `framework/testing/url_data_manager.py`
  - [ ] URLDataManager class
  - [ ] Integration with existing data loaders
  - [ ] Unit tests
- [ ] Create `framework/testing/url_builder.py`
  - [ ] URLBuilder class
  - [ ] Support all URL formats
  - [ ] Unit tests
- [ ] Create `framework/testing/url_validator.py`
  - [ ] URLValidator class
  - [ ] Multi-level validation
  - [ ] Unit tests
- [ ] Register services in `framework/microservices/services.py`
  - [ ] Add to get_available_services()

### Phase 2: Data Integration (Day 3)
- [ ] Create `test_data/bookslot/bookslot_workflows.json`
  - [ ] Define 35+ workflow test cases (P1-P7)
  - [ ] Include staging and production data
  - [ ] Validate JSON structure
- [ ] Extend `utils/fake_data_generator.py`
  - [ ] Add load_workflow_data() function
  - [ ] Follow existing load_bookslot_data() pattern
  - [ ] Unit tests

### Phase 3: Fixtures (Day 4)
- [ ] Extend `tests/bookslot/fixtures/__init__.py`
  - [ ] Add url_testing_service fixture (session scope)
  - [ ] Add url_data_manager fixture (session scope)
  - [ ] Add url_builder fixture (function scope)
  - [ ] Add url_validator fixture (function scope)
  - [ ] Add workflow_test_cases fixture
  - [ ] Add environment fixture (parametrized)
  - [ ] Test fixture isolation

### Phase 4: Configuration (Day 4)
- [ ] Extend `config/projects.yaml`
  - [ ] Add url_testing section under bookslot
  - [ ] Configure environments
  - [ ] Configure validation settings
- [ ] Create `config/url_testing.yaml`
  - [ ] Service configuration
  - [ ] Data service configuration
  - [ ] Validation service configuration
  - [ ] Fallback configuration

### Phase 5: Test Suite - Part 1 (Day 5)
- [ ] Create `tests/bookslot/url_testing/__init__.py`
- [ ] Create `tests/bookslot/url_testing/test_workflow_urls_p1.py`
  - [ ] 10 URL tests for Basic Info Page
  - [ ] Parametrized tests
  - [ ] Allure integration
- [ ] Create `tests/bookslot/url_testing/test_workflow_urls_p2.py`
  - [ ] 10 URL tests for Insurance Page
- [ ] Create `tests/bookslot/url_testing/test_workflow_urls_p3.py`
  - [ ] 10 URL tests for Schedule Page
- [ ] Run and validate P1-P3 tests

### Phase 6: Test Suite - Part 2 (Day 6)
- [ ] Create `tests/bookslot/url_testing/test_workflow_urls_p4.py` (5 tests)
- [ ] Create `tests/bookslot/url_testing/test_workflow_urls_p5.py` (5 tests)
- [ ] Create `tests/bookslot/url_testing/test_workflow_urls_p6.py` (5 tests)
- [ ] Create `tests/bookslot/url_testing/test_workflow_urls_p7.py` (5 tests)
- [ ] Run full URL test suite (50 tests)

### Phase 7: Validation (Day 7)
- [ ] Run existing 139 tests → Should all pass
- [ ] Run new 50 URL tests → Should all pass
- [ ] Run ALL 189 tests → Should all pass
- [ ] Performance benchmarks (<5s per URL test)
- [ ] Generate Allure report
- [ ] Code review
- [ ] Update `BOOKSLOT_TEST_DESIGN_MATRIX.md`

---

## 🎯 SUCCESS CRITERIA

### Technical
✅ All 3 microservices passing health checks  
✅ All 6 fixtures working correctly  
✅ All 50 URL tests passing  
✅ Existing 139 tests still passing (zero regression)  
✅ Performance within limits (<5s per URL test)  

### Architectural
✅ Follows BaseService pattern  
✅ Follows Manager/Builder/Validator patterns  
✅ Uses existing data loading utilities  
✅ Centralized fixture structure maintained  
✅ No code duplication  

### Documentation
✅ Implementation roadmap complete  
✅ Integration guide complete  
✅ Test design matrix updated  
✅ QA workflow guide created  

---

**Ready to implement:** All integration points mapped, zero conflicts confirmed, patterns validated.

**Next Step:** Begin Phase 1 - Create URLTestingService microservice extending BaseService.
