# URL Testing Implementation Roadmap - Framework-Aligned

**Project:** Hybrid_Automation - URL Testing Microservice  
**Purpose:** Implement URL query string testing following existing framework architecture  
**Date:** February 25, 2026  
**Status:** Ready for Implementation  
**Architecture:** Microservice-based, Reusable, Framework-Compliant  

---

## 📋 EXECUTIVE SUMMARY

### Existing Framework Analysis (CRITICAL - Read First)

**✅ EXISTING FRAMEWORK PATTERNS WE MUST FOLLOW:**

```
Framework Architecture Discovery:
├── Microservices Pattern:  BaseService (framework/microservices/base.py)
├── Manager Pattern:        ProjectManager, SessionManager, ConfigManager
├── Builder Pattern:        QueryBuilder, CommandBuilder, POMCommandBuilder
├── Validator Pattern:      DBValidator, PreFlightValidator
├── Service Pattern:        Health checks, service discovery, event-driven
├── Test Data:              JSON/YAML files in test_data/{project}/
├── Fixtures:               tests/{project}/fixtures/__init__.py
├── Config:                 config/*.yaml (projects.yaml, environments.yaml)
└── Utils:                  Data loaders in utils/ (load_bookslot_data)
```

**✅ EXISTING FILE STRUCTURE WE BUILD UPON:**

```
Hybrid_Automation/
├── framework/
│   ├── microservices/          ← WE USE: BaseService here
│   │   ├── base.py             ← EXTEND: Our URLTestingService
│   │   └── services.py          ← ADD: Register URL testing service
│   ├── core/
│   │   ├── project_manager.py   ← INTEGRATE: Project detection
│   │   ├── session_manager.py   ← No changes
│   │   └── [OTHER MANAGERS]     ← Follow same pattern
│   ├── config/                  ← Use existing ConfigManager
│   ├── testing/                 ← ADD: URL testing utilities
│   └── [OTHER MODULES]          ← No changes
├── test_data/
│   └── bookslot/                ← EXTEND: Add workflow data files
│       ├── bookslot_data.json   ← EXISTING: Keep as-is
│       └── [NEW FILES]          ← ADD: Workflow URLs
├── tests/
│   └── bookslot/
│       ├── fixtures/             ← EXTEND: Add URL fixtures
│       │   └── __init__.py      ← ADD: New fixtures here
│       ├── pages/               ← KEEP AS-IS: 139 existing tests
│       └── [NEW FOLDERS]        ← ADD: url_testing/
├── config/
│   ├── projects.yaml            ← INTEGRATE: Add URL configs
│   ├── environments.yaml        ← USE: Environment settings
│   └── [NEW FILES]              ← ADD: URL-specific configs
└── utils/
    ├── fake_data_generator.py   ← INTEGRATE: Use existing loaders
    └── [NEW FILES]              ← ADD: URL data utilities
```

---

## 🎯 IMPLEMENTATION STRATEGY

### Design Principle: Framework-Compliant Microservice

```
┌─────────────────────────────────────────────────────────────┐
│          URL TESTING MICROSERVICE (NEW SERVICE)             │
│         Built on Existing Framework Patterns                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📦 Service Layer (framework/microservices/)               │
│  ├── URLTestingService(BaseService)  ← Extends existing   │
│  ├── URLDataService(BaseService)     ← Data management    │
│  └── URLValidationService(BaseService) ← Validation       │
│                                                             │
│  🔧 Manager Layer (framework/testing/)                     │
│  ├── URLDataManager       ← Follows Manager pattern       │
│  ├── URLBuilder           ← Follows Builder pattern       │
│  └── URLValidator         ← Follows Validator pattern     │
│                                                             │
│  📊 Data Layer (test_data/bookslot/)                       │
│  ├── Uses existing JSON/YAML structure                     │
│  ├── Extends bookslot_data.json with workflow_id          │
│  └── Uses existing load_bookslot_data() utility           │
│                                                             │
│  🧪 Test Layer (tests/bookslot/)                           │
│  ├── Extends fixtures/__init__.py with URL fixtures       │
│  ├── New url_testing/ folder (no impact on existing)      │
│  └── Uses existing conftest.py patterns                    │
│                                                             │
│  ⚙️ Config Layer (config/)                                 │
│  ├── Uses existing projects.yaml structure                 │
│  ├── Uses existing environments.yaml                       │
│  └── New url_testing.yaml (service-specific config)       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 DETAILED FILE STRUCTURE (Framework-Aligned)

### Phase 1: Microservice Foundation (Days 1-2)

#### 1.1 Create URL Testing Service (Framework Pattern)

**File: `framework/microservices/url_testing_service.py`** (NEW)

```python
"""
URL Testing Microservice

Independent, reusable microservice for URL validation and testing.
Extends BaseService from framework.microservices.base

Architecture:
- Service discovery and health checks
- Event-driven communication
- Reusable across ALL projects (bookslot, callcenter, patientintake)
- follows SOLID principles
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from framework.microservices.base import (
    BaseService,
    HealthCheck,
    Message,
    MessagePriority,
    ServiceInfo,
    ServiceStatus,
)
from framework.observability.universal_logger import log_function, log_async_function


class URLFormat(Enum):
    """URL format types"""
    QUERY_STRING = "query_string"  # domain.com/page?workflow_id=X&param=Y
    PATH_PARAM = "path_param"      # domain.com/workflow/X?param=Y
    PATH_BASED = "path_based"      # domain.com/X/booking?param=Y
    HYBRID = "hybrid"              # domain.com/X?param=Y


@dataclass
class URLTestCase:
    """Single URL test case with metadata (Framework Model)"""
    workflow_id: str
    environment: str
    page_name: str
    query_params: Dict[str, Any]
    expected_status: int = 200
    expected_elements: List[str] = field(default_factory=list)
    test_priority: str = "medium"
    description: str = ""
    
    @property
    def test_id(self) -> str:
        """Unique test identifier"""
        return f"{self.environment}_{self.page_name}_{self.workflow_id}"


@dataclass
class ValidationResult:
    """URL validation result (Framework Model)"""
    url: str
    status_code: int
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validation_time_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


class URLTestingService(BaseService):
    """
    URL Testing Microservice
    
    Responsibilities:
    - URL generation and validation
    - Test case orchestration
    - Health monitoring
    - Event publishing
    
    Extends: BaseService (framework/microservices/base.py)
    Pattern: Microservice Architecture
    Reusability: All projects (bookslot, callcenter, patientintake)
    """
    
    def __init__(
        self,
        service_name: str = "url-testing",
        version: str = "1.0.0",
        host: str = "localhost",
        port: int = 8001
    ):
        """Initialize URL Testing Service"""
        super().__init__(
            service_name=service_name,
            version=version,
            host=host,
            port=port
        )
        self.test_cases: List[URLTestCase] = []
        self.validation_results: List[ValidationResult] = []
    
    async def _initialize(self) -> None:
        """Initialize service resources"""
        self.logger.info(f"Initializing {self.name} service v{self.version}")
        # Load configurations
        # Initialize data manager
        # Set up event listeners
    
    async def _cleanup(self) -> None:
        """Cleanup service resources"""
        self.logger.info(f"Cleaning up {self.name} service")
        # Save results
        # Close connections
    
    async def _health_check_impl(self) -> HealthCheck:
        """Perform service health check"""
        checks = []
        status = ServiceStatus.HEALTHY
        
        # Check data loader
        checks.append("data_loader_ready")
        
        # Check configuration
        checks.append("config_loaded")
        
        return HealthCheck(
            service_name=self.name,
            status=status,
            timestamp=datetime.now(),
            checks=checks
        )
    
    @log_async_function
    async def load_test_cases(
        self,
        project: str,
        environment: str = "staging"
    ) -> List[URLTestCase]:
        """Load URL test cases for project"""
        # Delegate to URLDataService
        pass
    
    @log_async_function
    async def validate_url(
        self,
        url: str,
        expected_elements: List[str]
    ) -> ValidationResult:
        """Validate single URL"""
        # Delegate to URLValidationService
        pass


class URLDataService(BaseService):
    """
    URL Data Management Service
    
    Responsibilities:
    - Load test data from files (JSON/YAML/CSV/Excel)
    - Generate test cases (fallback mode)
    - Data transformation and enrichment
    
    Extends: BaseService
    Pattern: Data Service
    """
    
    def __init__(self):
        super().__init__(
            service_name="url-data",
            version="1.0.0"
        )
    
    async def _initialize(self) -> None:
        """Initialize data service"""
        self.logger.info("Initializing URL Data Service")
    
    async def _cleanup(self) -> None:
        """Cleanup data service"""
        pass
    
    async def _health_check_impl(self) -> HealthCheck:
        """Health check for data service"""
        return HealthCheck(
            service_name=self.name,
            status=ServiceStatus.HEALTHY,
            timestamp=datetime.now(),
            checks=["data_sources_available"]
        )


class URLValidationService(BaseService):
    """
    URL Validation Service
    
    Responsibilities:
    - HTTP status validation
    - Element presence validation
    - Performance validation
    - Multi-level validation strategy
    
    Extends: BaseService
    Pattern: Validation Service
    """
    
    def __init__(self):
        super().__init__(
            service_name="url-validation",
            version="1.0.0"
        )
    
    async def _initialize(self) -> None:
        """Initialize validation service"""
        self.logger.info("Initializing URL Validation Service")
    
    async def _cleanup(self) -> None:
        """Cleanup validation service"""
        pass
    
    async def _health_check_impl(self) -> HealthCheck:
        """Health check for validation service"""
        return HealthCheck(
            service_name=self.name,
            status=ServiceStatus.HEALTHY,
            timestamp=datetime.now(),
            checks=["playwright_available", "validators_ready"]
        )
```

**Why This Design?**
✅ Extends existing `BaseService` - follows framework pattern  
✅ Service discovery and health checks - built-in  
✅ Event-driven - can publish/subscribe to framework events  
✅ Reusable - works for bookslot, callcenter, patientintake  
✅ Microservice architecture - independent, scalable  

---

#### 1.2 Register Service in Framework

**File: `framework/microservices/services.py`** (ENHANCE - ADD NEW SERVICE)

```python
# EXISTING CODE - DO NOT MODIFY
# ... existing service imports ...

# NEW: Import URL Testing Service
from framework.microservices.url_testing_service import (
    URLTestingService,
    URLDataService,
    URLValidationService
)


# EXISTING CODE - ADD TO EXISTING REGISTRY
def get_available_services() -> Dict[str, type]:
    """Get all available services"""
    return {
        # ... existing services ...
        "url-testing": URLTestingService,  # NEW
        "url-data": URLDataService,        # NEW
        "url-validation": URLValidationService  # NEW
    }
```

---

### Phase 2: Manager/Builder/Validator Layer (Days 2-3)

#### 2.1 URL Data Manager (Follows Manager Pattern)

**File: `framework/testing/url_data_manager.py`** (NEW)

```python
"""
URL Data Manager

Orchestrator for URL test data loading and generation.
Follows Manager pattern from framework (ProjectManager, SessionManager, etc.)

Pattern: Manager (Orchestrator)
Extends: None (Pure manager)
Dependencies: Uses URLDataService
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from enum import Enum

from framework.microservices.url_testing_service import URLTestCase
from framework.observability.universal_logger import log_function


class LoadMode(Enum):
    """Data loading mode"""
    MANUAL = "manual"  # Load from test data files
    AUTO = "auto"      # Generate from config
    CLI = "cli"        # Specified via CLI


class URLDataManager:
    """
    URL Data Manager - Orchestrates test data loading
    
    Responsibilities:
    - Detect data source (manual vs auto)
    - Route to appropriate loader
    - Transform data to URLTestCase objects
    - Cache and optimize
    
    Pattern: Manager (Orchestrator)
    Used By: URLTestingService, pytest fixtures
    """
    
    def __init__(self, project: str = "bookslot"):
        self.project = project
        self.test_data_dir = Path(__file__).parent.parent.parent / "test_data" / project
        self.config_dir = Path(__file__).parent.parent.parent / "config"
        self._cache: Dict[str, List[URLTestCase]] = {}
    
    @log_function
    def load_test_cases(
        self,
        environment: str = "staging",
        mode: Optional[LoadMode] = None
    ) -> List[URLTestCase]:
        """
        Load URL test cases
        
        Strategy:
        1. Check if manual test data exists (PRIMARY)
        2. If not, fall back to auto-generation (SECONDARY)
        3. Cache results for performance
        
        Args:
            environment: Target environment (staging, production)
            mode: Force specific mode (optional)
        
        Returns:
            List of URLTestCase objects
        """
        cache_key = f"{self.project}_{environment}_{mode}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Detect mode if not specified
        if mode is None:
            mode = self._detect_mode()
        
        if mode == LoadMode.MANUAL:
            test_cases = self._load_from_files(environment)
        elif mode == LoadMode.AUTO:
            test_cases = self._generate_from_config(environment)
        else:
            test_cases = []
        
        self._cache[cache_key] = test_cases
        return test_cases
    
    def _detect_mode(self) -> LoadMode:
        """Detect which mode to use (manual vs auto)"""
        # Check if manual test data files exist
        for ext in [".xlsx", ".csv", ".json", ".yaml"]:
            if (self.test_data_dir / f"{self.project}_workflows{ext}").exists():
                return LoadMode.MANUAL
        
        # Fall back to auto-generation
        return LoadMode.AUTO
    
    def _load_from_files(self, environment: str) -> List[URLTestCase]:
        """Load test cases from data files (PRIMARY MODE)"""
        # Use existing framework utilities
        from utils.fake_data_generator import load_bookslot_data
        
        # Load data using existing framework function
        data_list = load_bookslot_data(f"{self.project}_workflows.json")
        
        # Transform to URLTestCase objects
        test_cases = []
        for data in data_list:
            if data.get("environment") == environment:
                test_case = URLTestCase(
                    workflow_id=data["workflow_id"],
                    environment=data["environment"],
                    page_name=data.get("page_name", "P1"),
                    query_params={
                        k: v for k, v in data.items()
                        if k not in ["workflow_id", "environment", "page_name"]
                    }
                )
                test_cases.append(test_case)
        
        return test_cases
    
    def _generate_from_config(self, environment: str) -> List[URLTestCase]:
        """Generate test cases from config (FALLBACK MODE)"""
        # Load from config/url_testing.yaml
        # Generate combinations
        # Return test cases
        pass
```

**Why This Design?**
✅ Follows Manager pattern (like ProjectManager, SessionManager)  
✅ Uses existing utilities (`load_bookslot_data`)  
✅ Caching for performance  
✅ Flexible mode detection  
✅ Framework-compliant structure  

---

#### 2.2 URL Builder (Follows Builder Pattern)

**File: `framework/testing/url_builder.py`** (NEW)

```python
"""
URL Builder

Constructs URLs with query parameters and path segments.
Follows Builder pattern from framework (QueryBuilder, CommandBuilder, etc.)

Pattern: Builder
Extends: None
Dependencies: URLFormat enum
"""

from typing import Dict, Optional, Any
from urllib.parse import urlencode, quote
from framework.microservices.url_testing_service import URLFormat
from framework.observability.universal_logger import log_function


class URLBuilder:
    """
    URL Builder - Constructs URLs from templates
    
    Responsibilities:
    - Apply URL templates (query string, path-based)
    - Inject workflow_id and parameters
    - Support multiple URL formats
    - URL encoding and validation
    
    Pattern: Builder
    Used By: URLTestingService, page objects, fixtures
    """
    
    def __init__(self, base_url: str, url_format: URLFormat = URLFormat.QUERY_STRING):
        self.base_url = base_url.rstrip("/")
        self.url_format = url_format
    
    @log_function(log_args=False, log_result=True)
    def build(
        self,
        workflow_id: str,
        page_path: str = "",
        query_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build complete URL from components
        
        Args:
            workflow_id: Workflow ID to inject
            page_path: Page path (e.g., /booking, /schedule)
            query_params: Additional query parameters
        
        Returns:
            Complete URL string
        """
        query_params = query_params or {}
        
        if self.url_format == URLFormat.QUERY_STRING:
            return self._build_query_string(workflow_id, page_path, query_params)
        elif self.url_format == URLFormat.PATH_PARAM:
            return self._build_path_param(workflow_id, page_path, query_params)
        elif self.url_format == URLFormat.PATH_BASED:
            return self._build_path_based(workflow_id, page_path, query_params)
        else:
            return self._build_hybrid(workflow_id, page_path, query_params)
    
    def _build_query_string(
        self,
        workflow_id: str,
        page_path: str,
        query_params: Dict[str, Any]
    ) -> str:
        """Build query string URL: domain.com/page?workflow_id=X&param=Y"""
        url = f"{self.base_url}{page_path}"
        
        # Add workflow_id as first parameter
        all_params = {"workflow_id": workflow_id, **query_params}
        
        if all_params:
            query_string = urlencode(all_params)
            url = f"{url}?{query_string}"
        
        return url
    
    def _build_path_param(
        self,
        workflow_id: str,
        page_path: str,
        query_params: Dict[str, Any]
    ) -> str:
        """Build path param URL: domain.com/workflow/X/page?param=Y"""
        url = f"{self.base_url}/workflow/{workflow_id}{page_path}"
        
        if query_params:
            query_string = urlencode(query_params)
            url = f"{url}?{query_string}"
        
        return url
    
    def _build_path_based(
        self,
        workflow_id: str,
        page_path: str,
        query_params: Dict[str, Any]
    ) -> str:
        """Build path-based URL: domain.com/X/booking?param=Y"""
        url = f"{self.base_url}/{workflow_id}{page_path}"
        
        if query_params:
            query_string = urlencode(query_params)
            url = f"{url}?{query_string}"
        
        return url
    
    def _build_hybrid(
        self,
        workflow_id: str,
        page_path: str,
        query_params: Dict[str, Any]
    ) -> str:
        """Build hybrid URL: domain.com/X?param=Y"""
        url = f"{self.base_url}/{workflow_id}"
        
        if query_params:
            query_string = urlencode(query_params)
            url = f"{url}?{query_string}"
        
        return url
```

**Why This Design?**
✅ Follows Builder pattern (like QueryBuilder, CommandBuilder)  
✅ Supports multiple URL formats  
✅ Proper URL encoding  
✅ Logging integration  
✅ Reusable across all projects  

---

#### 2.3 URL Validator (Follows Validator Pattern)

**File: `framework/testing/url_validator.py`** (NEW)

```python
"""
URL Validator

Multi-level URL validation with Playwright integration.
Follows Validator pattern from framework (DBValidator, PreFlightValidator, etc.)

Pattern: Validator
Extends: None
Dependencies: Playwright, ValidationResult
"""

from typing import Optional, List
import time
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from framework.microservices.url_testing_service import ValidationResult
from framework.observability.universal_logger import log_function


class URLValidator:
    """
    URL Validator - Multi-level URL validation
    
    Validation Levels:
    1. HTTP Status Check (200 OK)
    2. Element Presence Check (h1, form, etc.)
    3. Error Message Check (no errors on page)
    4. Performance Check (load time < threshold)
    
    Pattern: Validator
    Used By: URLValidationService, test fixtures
    """
    
    def __init__(self, page: Page):
        self.page = page
    
    @log_function(log_timing=True)
    def validate(
        self,
        url: str,
        expected_elements: Optional[List[str]] = None,
        timeout: int = 10000
    ) -> ValidationResult:
        """
        Perform comprehensive URL validation
        
        Args:
            url: URL to validate
            expected_elements: List of element selectors to check
            timeout: Timeout in milliseconds
        
        Returns:
            ValidationResult with detailed status
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            # Level 1: HTTP Status Check
            response = self.page.goto(url, wait_until="networkidle", timeout=timeout)
            
            if response.status !=  200:
                errors.append(f"HTTP {response.status}: Expected 200")
            
            # Level 2: Element Presence Check
            if expected_elements:
                for selector in expected_elements:
                    try:
                        self.page.wait_for_selector(selector, timeout=5000)
                    except PlaywrightTimeoutError:
                        errors.append(f"Element not found: {selector}")
            
            # Level 3: Error Message Check
            error_selectors = [
                ".error",
                "[class*='error']",
                "[role='alert']",
                ".alert-danger"
            ]
            for selector in error_selectors:
                if self.page.locator(selector).count() > 0:
                    warnings.append(f"Error element found: {selector}")
            
            # Level 4: Performance Check
            load_time = int((time.time() - start_time) * 1000)
            if load_time > timeout:
                warnings.append(f"Slow load time: {load_time}ms")
            
            is_valid = len(errors) == 0
            
            return ValidationResult(
                url=url,
                status_code=response.status,
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                validation_time_ms=load_time
            )
        
        except Exception as e:
            return ValidationResult(
                url=url,
                status_code=0,
                is_valid=False,
                errors=[f"Validation failed: {str(e)}"],
                validation_time_ms=int((time.time() - start_time) * 1000)
            )
```

**Why This Design?**
✅ Follows Validator pattern (like DBValidator, PreFlightValidator)  
✅ Multi-level validation strategy  
✅ Playwright integrated  
✅ Performance monitoring  
✅ Comprehensive error reporting  

---

---

### Phase 3: Test Data Structure (Day 3)

#### 3.1 Extend Existing Test Data Files

**File: `test_data/bookslot/bookslot_workflows.json`** (NEW - Extends existing structure)

```json
{
  "metadata": {
    "version": "1.0",
    "created": "2026-02-25",
    "description": "URL workflow test data for Bookslot pages P1-P7",
    "total_workflows": 35,
    "environments": ["staging", "production"]
  },
  "workflows": [
    {
      "workflow_id": "WF-001-BASIC",
      "environment": "staging",
      "page_name": "P1",
      "description": "Basic info page - happy path",
      "url_format": "query_string",
      "query_params": {
        "zip": "20678",
        "contact_method": "Phone",
        "debug": "true"
      },
      "expected_elements": [
        "input[name='first_name']",
        "input[name='last_name']",
        "input[name='email']",
        "button[type='submit']"
      ],
      "test_data": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "1234567890"
      },
      "test_priority": "high",
      "tags": ["smoke", "p1", "basic"]
    },
    {
      "workflow_id": "WF-002-ZIP-VALIDATION",
      "environment": "staging",
      "page_name": "P1",
      "description": "Basic info page - invalid zip code",
      "url_format": "query_string",
      "query_params": {
        "zip": "99999",
        "contact_method": "Email"
      },
      "expected_elements": [
        "input[name='first_name']",
        ".error-message"
      ],
      "test_data": {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com"
      },
      "test_priority": "medium",
      "tags": ["validation", "p1", "negative"]
    },
    {
      "workflow_id": "WF-003-INSURANCE-HUMANA",
      "environment": "staging",
      "page_name": "P2",
      "description": "Insurance page - Humana workflow",
      "url_format": "query_string",
      "query_params": {
        "payer": "Humana",
        "prefill": "true"
      },
      "expected_elements": [
        "input[name='member_id']",
        "input[name='group_number']",
        "select[name='payer']"
      ],
      "test_data": {
        "member_id": "HUM123456",
        "group_number": "GRP789",
        "payer": "Humana"
      },
      "test_priority": "high",
      "tags": ["insurance", "p2", "humana"]
    },
    {
      "workflow_id": "WF-004-SCHEDULE-DATETIME",
      "environment": "staging",
      "page_name": "P3",
      "description": "Schedule page - date/time selection",
      "url_format": "query_string",
      "query_params": {
        "preferred_date": "2026-03-01",
        "preferred_time": "10:00"
      },
      "expected_elements": [
        ".date-picker",
        ".time-selector",
        "button.confirm-schedule"
      ],
      "test_data": {},
      "test_priority": "high",
      "tags": ["schedule", "p3", "datetime"]
    }
  ]
}
```

**Why This Structure?**
✅ Follows existing JSON pattern from `bookslot_data.json`  
✅ Comprehensive metadata tracking  
✅ Workflow-centric design  
✅ Flexible query parameters  
✅ Expected elements for validation  
✅ Test data embedded (optional)  
✅ Tags for filtering  

---

#### 3.2 Update Existing Data Loader

**File: `utils/fake_data_generator.py`** (ENHANCE - ADD NEW FUNCTION)

```python
# EXISTING CODE - DO NOT MODIFY
# ... existing load_bookslot_data function ...

# NEW: Add workflow data loader (follows existing pattern)
def load_workflow_data(
    project: str = "bookslot",
    filename: str = "workflows.json",
    environment: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Load workflow test data from JSON/YAML files
    
    Follows existing load_bookslot_data() pattern.
    Extends framework data loading utilities.
    
    Args:
        project: Project name (bookslot, callcenter, etc.)
        filename: Data filename (workflows.json, workflows.yaml)
        environment: Filter by environment (staging, production)
    
    Returns:
        List of workflow dictionaries
    """
    test_data_dir = Path(__file__).parent.parent / "test_data" / project
    file_path = test_data_dir / f"{project}_{filename}"
    
    if not file_path.exists():
        logger.warning(f"Workflow data file not found: {file_path}")
        return []
    
    # Load data (JSON or YAML)
    if file_path.suffix == ".json":
        with open(file_path, "r") as f:
            data = json.load(f)
    elif file_path.suffix in [".yaml", ".yml"]:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    workflows = data.get("workflows", [])
    
    # Filter by environment if specified
    if environment:
        workflows = [w for w in workflows if w.get("environment") == environment]
    
    logger.info(f"Loaded {len(workflows)} workflows from {file_path}")
    return workflows
```

---

### Phase 4: Fixtures Integration (Day 4)

#### 4.1 Add URL Fixtures to Existing Fixture Module

**File: `tests/bookslot/fixtures/__init__.py`** (ENHANCE - ADD NEW FIXTURES)

```python
# EXISTING CODE - DO NOT MODIFY (Keep all existing fixtures)
# ... existing fixtures (valid_basic_info, valid_personal_info, etc.) ...


# ========================================================================
# NEW SECTION: URL Testing Fixtures (Framework-Compliant)
# ========================================================================
# Pattern: Follows existing fixture organization
# Added: 2026-02-25
# Purpose: URL workflow testing support
# ========================================================================

@pytest.fixture(scope="session")
def url_testing_service():
    """
    URL Testing Microservice instance
    
    Extends: BaseService from framework.microservices.base
    Lifecycle: Session-scoped (initialize once)
    """
    from framework.microservices.url_testing_service import URLTestingService
    
    service = URLTestingService()
    asyncio.run(service.start())
    
    yield service
    
    asyncio.run(service.stop())


@pytest.fixture(scope="session")
def url_data_manager():
    """
    URL Data Manager instance
    
    Pattern: Manager (follows ProjectManager, SessionManager)
    Lifecycle: Session-scoped (shared across tests)
    """
    from framework.testing.url_data_manager import URLDataManager
    
    return URLDataManager(project="bookslot")


@pytest.fixture
def url_builder(base_url: str):
    """
    URL Builder instance
    
    Pattern: Builder (follows QueryBuilder, CommandBuilder)
    Lifecycle: Function-scoped (fresh per test)
    Dependencies: Uses base_url fixture
    """
    from framework.testing.url_builder import URLBuilder, URLFormat
    
    return URLBuilder(base_url=base_url, url_format=URLFormat.QUERY_STRING)


@pytest.fixture
def url_validator(page: Page):
    """
    URL Validator instance
    
    Pattern: Validator (follows DBValidator, PreFlightValidator)
    Lifecycle: Function-scoped (per test)
    Dependencies: Uses page fixture (Playwright)
    """
    from framework.testing.url_validator import URLValidator
    
    return URLValidator(page=page)


@pytest.fixture
def workflow_test_cases(url_data_manager, environment: str):
    """
    Load workflow test cases for environment
    
    Data Source: test_data/bookslot/bookslot_workflows.json
    Pattern: Data fixture (follows existing test data fixtures)
    """
    return url_data_manager.load_test_cases(environment=environment)


@pytest.fixture(params=["staging", "production"])
def environment(request):
    """
    Parameterized environment fixture
    
    Generates tests for both staging and production
    Pattern: Parametrization fixture
    """
    return request.param


@pytest.fixture
def url_test_case(workflow_test_cases, request):
    """
    Single URL test case from test data
    
    Pattern: Parametrized test case fixture
    Usage: @pytest.mark.parametrize indirectly
    """
    workflow_id = request.param
    for test_case in workflow_test_cases:
        if test_case.workflow_id == workflow_id:
            return test_case
    
    pytest.skip(f"Workflow not found: {workflow_id}")


# END NEW SECTION: URL Testing Fixtures
```

**Why This Design?**
✅ Added to EXISTING fixtures/__init__.py (not new conftest)  
✅ Follows existing fixture patterns and naming  
✅ Session-scoped for services (performance)  
✅ Function-scoped for builders/validators (isolation)  
✅ Clear documentation inline  
✅ Zero impact on existing fixtures  

---

### Phase 5: Test Suite Structure (Days 4-5)

#### 5.1 Create URL Testing Module

**File: `tests/bookslot/url_testing/__init__.py`** (NEW)

```python
"""
URL Testing Module for Bookslot

Test Suite: URL workflow validation across P1-P7
Architecture: Microservice-based, data-driven
Pattern: Follows existing test structure from tests/bookslot/pages/

Organization:
- test_workflow_urls_p1.py: Basic Info Page (P1) URL tests
- test_workflow_urls_p2.py: Insurance Page (P2) URL tests
- test_workflow_urls_p3.py: Schedule Page (P3) URL tests
- test_workflow_urls_p4.py: Reason Page (P4) URL tests
- test_workflow_urls_p5.py: Confirmation Page (P5) URL tests
- test_workflow_urls_p6.py: Review Page (P6) URL tests
- test_workflow_urls_p7.py: Thank You Page (P7) URL tests

Fixtures: Uses tests/bookslot/fixtures/__init__.py (centralized)
Data: Uses test_data/bookslot/bookslot_workflows.json
"""

__all__ = [
    "test_workflow_urls_p1",
    "test_workflow_urls_p2",
    "test_workflow_urls_p3",
    "test_workflow_urls_p4",
    "test_workflow_urls_p5",
    "test_workflow_urls_p6",
    "test_workflow_urls_p7",
]
```

---

#### 5.2 Create Test File Template (P1 Example)

**File: `tests/bookslot/url_testing/test_workflow_urls_p1.py`** (NEW)

```python
"""
URL Workflow Tests - Basic Info Page (P1)

Test Coverage:
- Query string parameter validation
- Workflow persistence across page refreshes
- Dynamic form prefilling from URL parameters
- Error handling for invalid parameters
- Multi-environment testing (staging, production)

Architecture:
- Uses URLTestingService microservice
- Data-driven from test_data/bookslot/bookslot_workflows.json
- Fixtures from tests/bookslot/fixtures/__init__.py
"""

import pytest
import allure
from typing import Dict, Any

from framework.microservices.url_testing_service import URLTestCase
from framework.testing.url_builder import URLBuilder
from framework.testing.url_validator import URLValidator


@allure.epic("Bookslot")
@allure.feature("URL Testing")
@allure.story("Basic Info Page (P1)")
class TestWorkflowURLsP1:
    """URL workflow tests for Basic Info Page"""
    
    @allure.title("Verify P1 loads with workflow_id in query string")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_p1_query_string_workflow_id(
        self,
        page,
        url_builder: URLBuilder,
        url_validator: URLValidator,
        base_url: str
    ):
        """
        Test: Basic Info Page loads with workflow_id parameter
        
        Steps:
        1. Build URL with workflow_id=WF-001-BASIC
        2. Navigate to URL
        3. Validate page loads successfully
        4. Verify expected elements present
        5. Verify workflow ID persists
        """
        # Build URL
        url = url_builder.build(
            workflow_id="WF-001-BASIC",
            page_path="/basic-info",
            query_params={"zip": "20678", "contact_method": "Phone"}
        )
        
        allure.attach(url, "Generated URL", allure.attachment_type.TEXT)
        
        # Validate URL
        result = url_validator.validate(
            url=url,
            expected_elements=[
                "input[name='first_name']",
                "input[name='last_name']",
                "input[name='email']",
                "button[type='submit']"
            ]
        )
        
        # Assertions
        assert result.is_valid, f"URL validation failed: {result.errors}"
        assert result.status_code == 200, f"Expected HTTP 200, got {result.status_code}"
        assert len(result.errors) == 0, f"Validation errors: {result.errors}"
        
        allure.attach(
            f"Status: {result.status_code}\nLoad Time: {result.validation_time_ms}ms",
            "Validation Result",
            allure.attachment_type.TEXT
        )
    
    @allure.title("Verify P1 prefills form data from URL parameters")
    @pytest.mark.parametrize(
        "query_params,expected_prefill",
        [
            ({"zip": "20678"}, {"zip": "20678"}),
            ({"zip": "20678", "contact_method": "Email"}, {"zip": "20678", "contact_method": "Email"}),
            ({}, {}),  # No prefill
        ],
        ids=["zip-only", "zip-and-contact", "no-prefill"]
    )
    def test_p1_form_prefill_from_url(
        self,
        page,
        url_builder: URLBuilder,
        query_params: Dict[str, Any],
        expected_prefill: Dict[str, Any]
    ):
        """
        Test: Form fields prefill from URL query parameters
        
        Validates: Dynamic form population from query string
        """
        url = url_builder.build(
            workflow_id="WF-PREFILL-TEST",
            page_path="/basic-info",
            query_params=query_params
        )
        
        page.goto(url)
        
        # Verify prefilled values
        if "zip" in expected_prefill:
            zip_value = page.locator("input[name='zip']").input_value()
            assert zip_value == expected_prefill["zip"], "Zip code not prefilled"
        
        if "contact_method" in expected_prefill:
            contact_value = page.locator("select[name='contact_method']").input_value()
            assert contact_value == expected_prefill["contact_method"], "Contact method not selected"
    
    @allure.title("Verify workflow persists after page refresh")
    @pytest.mark.workflow_persistence
    def test_p1_workflow_persists_after_refresh(
        self,
        page,
        url_builder: URLBuilder
    ):
        """
        Test: Workflow ID persists in URL after page refresh
        
        Validates: State management and URL persistence
        """
        workflow_id = "WF-PERSIST-TEST"
        url = url_builder.build(
            workflow_id=workflow_id,
            page_path="/basic-info"
        )
        
        # Load page
        page.goto(url)
        original_url = page.url
        
        # Refresh page
        page.reload()
        refreshed_url = page.url
        
        # Verify workflow ID still in URL
        assert workflow_id in refreshed_url, "Workflow ID lost after refresh"
        assert original_url == refreshed_url, "URL changed after refresh"


# Similar structure for test_workflow_urls_p2.py through test_workflow_urls_p7.py
```

**Why This Design?**
✅ Follows existing test structure from `tests/bookslot/pages/`  
✅ Uses centralized fixtures (no local conftest)  
✅ Allure integration for reporting  
✅ Parametrized tests for data-driven approach  
✅ Clear test documentation  
✅ Pytest markers for filtering  

---

### Phase 6: Configuration Files (Day 5)

#### 6.1 Extend Existing Projects Config

**File: `config/projects.yaml`** (ENHANCE - ADD URL TESTING SECTION)

```yaml
# EXISTING PROJECT CONFIGS - DO NOT MODIFY
# ... existing bookslot, callcenter, patientintake configs ...

# NEW: URL Testing Configuration (Per-Project)
projects:
  bookslot:
    # ... existing bookslot config ...
    
    # NEW: URL testing specific config
    url_testing:
      enabled: true
      url_format: query_string  # query_string | path_param | path_based | hybrid
      
      environments:
        staging:
          base_url: "https://staging.bookslot.com"
          workflows_file: "bookslot_workflows.json"
          test_data_mode: "manual"  # manual | auto
        
        production:
          base_url: "https://www.bookslot.com"
          workflows_file: "bookslot_workflows_prod.json"
          test_data_mode: "manual"
      
      validation:
        timeout_ms: 10000
        retry_count: 3
        expected_status: 200
        check_elements: true
        check_performance: true
      
      reporting:
        allure_enabled: true
        screenshot_on_failure: true
        video_on_failure: false
      
      pages:
        P1:
          name: "Basic Info"
          path: "/basic-info"
          expected_elements:
            - "input[name='first_name']"
            - "input[name='last_name']"
            - "input[name='email']"
        P2:
          name: "Insurance"
          path: "/insurance"
          expected_elements:
            - "input[name='member_id']"
            - "select[name='payer']"
        # P3-P7 similar structure
```

---

#### 6.2 Create URL Testing Service Config

**File: `config/url_testing.yaml`** (NEW)

```yaml
# URL Testing Service Configuration
# Service: URLTestingService, URLDataService, URLValidationService
# Pattern: Microservice configuration

service:
  name: "url-testing"
  version: "1.0.0"
  host: "localhost"
  port: 8001

data_service:
  name: "url-data"
  version: "1.0.0"
  load_mode: "auto"  # auto | manual | cli
  cache_enabled: true
  cache_ttl_seconds: 300

validation_service:
  name: "url-validation"
  version: "1.0.0"
  
  levels:
    - "http_status"      # Check HTTP 200
    - "element_presence" # Check expected elements
    - "error_messages"   # Check for error elements
    - "performance"      # Check load time
  
  thresholds:
    max_load_time_ms: 5000
    max_retry_count: 3
    element_timeout_ms: 5000

fallback:
  # Auto-generation config when manual data files don't exist
  enabled: true
  workflow_id_pattern: "WF-{page}-{index:03d}"
  default_query_params:
    - "zip"
    - "contact_method"
    - "debug"
  
  page_combinations:
    P1:
      zip: ["20678", "90210", "10001"]
      contact_method: ["Phone", "Email"]
    P2:
      payer: ["Humana", "Aetna", "Blue Cross"]
      prefill: ["true", "false"]

logging:
  level: "INFO"
  format: "json"
  file: "logs/url_testing_service.log"
  rotation: "daily"

telemetry:
  enabled: true
  export_interval_seconds: 60
  metrics:
    - "url_validation_count"
    - "url_validation_duration"
    - "url_validation_failures"
```

---

## 📅 IMPLEMENTATION TIMELINE

### Day 1-2: Microservice Foundation
- ✅ Create `framework/microservices/url_testing_service.py`
- ✅ Create `framework/testing/url_data_manager.py`
- ✅ Create `framework/testing/url_builder.py`
- ✅ Create `framework/testing/url_validator.py`
- ✅ Register services in `framework/microservices/services.py`
- ✅ Unit tests for all classes

### Day 3: Data Integration
- ✅ Create `test_data/bookslot/bookslot_workflows.json`
- ✅ Extend `utils/fake_data_generator.py` with `load_workflow_data()`
- ✅ Create sample workflow data (35 test cases covering P1-P7)
- ✅ Validate data loading

### Day 4: Fixtures & Configuration
- ✅ Extend `tests/bookslot/fixtures/__init__.py` with URL fixtures
- ✅ Create `config/url_testing.yaml`
- ✅ Extend `config/projects.yaml` with URL testing section
- ✅ Test fixture integration

### Day 5: Test Suite - P1, P2, P3
- ✅ Create `tests/bookslot/url_testing/__init__.py`
- ✅ Create `test_workflow_urls_p1.py` (10 tests)
- ✅ Create `test_workflow_urls_p2.py` (10 tests)
- ✅ Create `test_workflow_urls_p3.py` (10 tests)
- ✅ Run subset validation

### Day 6: Test Suite - P4, P5, P6, P7
- ✅ Create `test_workflow_urls_p4.py` (5 tests)
- ✅ Create `test_workflow_urls_p5.py` (5 tests)
- ✅ Create `test_workflow_urls_p6.py` (5 tests)
- ✅ Create `test_workflow_urls_p7.py` (5 tests)
- ✅ Full test suite run (50+ new tests)

### Day 7: Documentation & Validation
- ✅ Update `BOOKSLOT_TEST_DESIGN_MATRIX.md`
- ✅ Create QA guide for adding workflow data
- ✅ Run full regression (existing 139 + new 50+)
- ✅ Performance benchmarks
- ✅ Code review

---

## 📊 DELIVERABLES

### Code Deliverables
1. **3 Microservices** (URLTestingService, URLDataService, URLValidationService)
2. **3 Utilities** (URLDataManager, URLBuilder, URLValidator)
3. **6 Fixtures** (url_testing_service, url_data_manager, url_builder, etc.)
4. **7 Test Files** (test_workflow_urls_p1.py through p7.py)
5. **2 Config Files** (url_testing.yaml, extended projects.yaml)
6. **1 Data File** (bookslot_workflows.json with 35+ test cases)

### Test Coverage
- **50+ new URL tests** across P1-P7
- **Zero impact** on existing 139 tests
- **Multi-environment** (staging, production)
- **Data-driven** (JSON-based test cases)

### Documentation
- Implementation roadmap ✅ (this document)
- Updated test design matrix
- QA workflow guide
- Architecture diagrams

---

## ✅ VALIDATION CHECKLIST

### Pre-Implementation
- [x] Existing framework architecture analyzed
- [x] Zero-conflict strategy confirmed
- [x] Microservice pattern validated
- [x] Data structure finalized

### Post-Implementation
- [ ] All 3 microservices passing health checks
- [ ] All 50+ URL tests passing
- [ ] Existing 139 tests still passing
- [ ] Allure reporting working
- [ ] Performance benchmarks met (<5s per URL test)
- [ ] Documentation updated

---

## 🚀 READY TO IMPLEMENT

This roadmap provides:
✅ **Framework-compliant architecture** - Extends BaseService, follows existing patterns  
✅ **Microservice design** - Independent, reusable, scalable  
✅ **Zero conflicts** - No impact on existing 139 tests  
✅ **Data-driven approach** - JSON-based workflow definitions  
✅ **Reusable components** - Works for all projects (bookslot, callcenter, patientintake)  
✅ **Modern patterns** - Manager/Builder/Validator, SOLID principles  
✅ **Comprehensive coverage** - 50+ tests across P1-P7  

**Next Step:** Begin Day 1 implementation - Create URL Testing Service microservice.

---

**Document Version:** 1.0  
**Last Updated:** February 25, 2026  
**Status:** Ready for Implementation  
**Estimated Effort:** 7 days (1 engineer)
