# 🚀 QUICK START GUIDE
## Test Automation Framework - Complete Setup

**Framework Version:** 3.0 (Production Ready)  
**Date:** January 28, 2026

---

## ⚡ 5-MINUTE QUICK START

### 1. Installation (2 minutes)
```bash
# Clone repository
git clone <your-repo-url>
cd Automation

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium firefox webkit

# Verify installation
python verify_installation.py
```

### 2. Run Your First Test (1 minute)
```bash
# Run a single test
pytest tests/unit/test_config_models.py -v

# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/ --cov=framework --cov-report=html
```

### 3. View Results (1 minute)
```bash
# Open coverage report
start htmlcov/index.html  # Windows
# or
open htmlcov/index.html   # Mac/Linux

# Generate Allure report
allure serve allure-results
```

### 4. Try Advanced Features (1 minute)
```bash
# Distributed testing (use all CPU cores)
pytest tests/ -n auto

# Visual regression testing
pytest tests/visual/ --update-baselines  # First run
pytest tests/visual/                     # Compare with baseline

# Performance testing
pytest tests/ --benchmark-only
```

---

## 📚 FEATURE WALKTHROUGHS

### Feature 1: Using OpenTelemetry Tracing

**File:** `examples/telemetry_example.py`
```python
from framework.observability import initialize_telemetry, TelemetryConfig, get_telemetry

# Initialize once in conftest.py or main
config = TelemetryConfig(
    service_name="my-test-suite",
    environment="staging",
    enable_console=True,  # Debug mode
    enable_otlp=False     # Production mode (needs OTLP collector)
)
telemetry = initialize_telemetry(config)

# Use in your tests
def test_user_login():
    telemetry = get_telemetry()
    
    with telemetry.span("login_operation", {"user": "admin"}):
        # Your test code here
        login_page.navigate()
        login_page.fill_credentials("admin", "password")
        login_page.click_submit()
        
        telemetry.add_event("credentials_filled")
        
    # Span automatically closed, duration recorded
```

**Benefits:**
- ✅ Distributed tracing across services
- ✅ Performance bottleneck identification
- ✅ Request correlation
- ✅ Production debugging

---

### Feature 2: Structured Logging

**File:** `examples/logging_example.py`
```python
from framework.observability.logging import get_logger, TestLogger, LogContext

# Basic logging
logger = get_logger(__name__)
logger.info("test_started", test_name="test_login", user="admin")
logger.error("test_failed", test_name="test_login", error="timeout", duration=30.5)

# Test-specific logging
with TestLogger("test_checkout") as log:
    log.test_started()
    
    log.step("add_to_cart", product_id=123, quantity=2)
    log.step("proceed_to_checkout")
    
    log.api_request("POST", "/api/orders", status_code=201, duration=0.45)
    
    log.assertion("Order created successfully", result=True)
    log.test_passed(duration=5.67)

# Context-aware logging
with LogContext(user_id=123, session_id="abc-123"):
    logger.info("user_action", action="click", element="buy_button")
    # All logs in this context will include user_id and session_id
```

**Benefits:**
- ✅ JSON-formatted logs (easy to parse)
- ✅ Structured data (not just strings)
- ✅ Context variables
- ✅ ELK/Splunk ready

---

### Feature 3: Async Database Client

**File:** `examples/database_example.py`
```python
from framework.database.async_client import (
    AsyncDatabaseClient,
    DatabaseConfig,
    DatabaseType
)

# Configure database
config = DatabaseConfig(
    db_type=DatabaseType.POSTGRESQL,
    host="localhost",
    port=5432,
    database="testdb",
    user="testuser",
    password="testpass",
    min_pool_size=5,
    max_pool_size=20
)

# Use in async tests
@pytest.mark.asyncio
async def test_user_crud():
    async with AsyncDatabaseClient(config) as db:
        # Create user
        await db.execute(
            "INSERT INTO users (name, email) VALUES ($1, $2)",
            "John Doe",
            "john@example.com"
        )
        
        # Query user
        user = await db.fetch_one(
            "SELECT * FROM users WHERE email = $1",
            "john@example.com"
        )
        assert user["name"] == "John Doe"
        
        # Transaction
        async with db.transaction():
            await db.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
            await db.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
            # Auto-commit on success, rollback on exception
```

**Benefits:**
- ✅ 4-6x faster than synchronous
- ✅ Connection pooling
- ✅ Transaction support
- ✅ PostgreSQL & MySQL support

---

### Feature 4: Visual Regression Testing

**File:** `examples/visual_testing_example.py`
```python
from framework.testing.visual import VisualTester, VisualConfig

# Configure
config = VisualConfig(
    baseline_dir="tests/visual/baselines",
    diff_dir="tests/visual/diffs",
    threshold=0.1  # 10% difference allowed
)

tester = VisualTester(config)

@pytest.mark.asyncio
async def test_homepage_visual(page):
    await page.goto("https://example.com")
    
    # First run: create baseline
    # await tester.compare_page(page, "homepage", update_baseline=True)
    
    # Subsequent runs: compare with baseline
    is_match = await tester.compare_page(page, "homepage")
    
    if not is_match:
        # Diff image saved to: tests/visual/diffs/homepage-diff.png
        pytest.fail("Visual regression detected!")
    
    assert is_match

# Compare specific elements
@pytest.mark.asyncio
async def test_login_form_visual(page):
    await page.goto("https://example.com/login")
    
    login_form = page.locator("#login-form")
    is_match = await tester.compare_element(login_form, "login_form")
    
    assert is_match
```

**Benefits:**
- ✅ Pixel-perfect comparison
- ✅ Automatic diff generation
- ✅ Baseline management
- ✅ Element-specific comparison

---

### Feature 5: Distributed Test Execution

**File:** `examples/distributed_testing_example.py`
```python
from framework.testing.distributed import (
    run_distributed_tests,
    DistributedTestConfig,
    WorkerManager
)

# Configure distributed execution
config = DistributedTestConfig(
    num_workers="auto",        # Use all CPU cores
    dist_mode="loadscope",     # Balance by test scope
    max_worker_restart=2,      # Restart workers on failure
    timeout=300                # 5 minute timeout per test
)

# Run tests
exit_code = run_distributed_tests(
    "tests/",
    config,
    additional_args=["-v", "--tb=short"]
)

# Or use pytest directly
# pytest tests/ -n auto --dist=loadscope

# In your tests, check if running in worker
def test_something():
    worker_info = WorkerManager.get_worker_info()
    
    if worker_info["is_worker"]:
        print(f"Running in worker: {worker_info['worker_id']}")
    else:
        print("Running in main process")
```

**Benefits:**
- ✅ Nx faster (N = CPU cores)
- ✅ Automatic load balancing
- ✅ Worker isolation
- ✅ Result aggregation

---

### Feature 6: Constructor Injection

**File:** `examples/constructor_injection.py` (already created)
```python
from framework.di_container import DIContainer, Lifetime
from unittest.mock import Mock

# Production code - real dependencies
browser = PlaywrightBrowser()
logger = StructuredLogger()
login_page = LoginPage(browser, logger)
login_page.login("admin", "password123")

# Test code - mock dependencies
mock_browser = Mock(spec=IBrowser)
mock_logger = Mock(spec=ILogger)

login_page = LoginPage(mock_browser, mock_logger)
login_page.login("test", "test123")

# Verify mocks called
mock_browser.navigate.assert_called_with("/login")
mock_browser.fill.assert_called()
mock_logger.info.assert_called()

# Even better - use DI container
container = DIContainer()
container.register(IBrowser, PlaywrightBrowser, Lifetime.SINGLETON)
container.register(ILogger, StructuredLogger, Lifetime.SINGLETON)
container.register(LoginPage, LoginPage, Lifetime.TRANSIENT)

# Resolve with auto-injection
login_page = container.resolve(LoginPage)
login_page.login("admin", "password")
```

**Benefits:**
- ✅ Easy to test (inject mocks)
- ✅ Loose coupling
- ✅ SOLID principles
- ✅ No service locator anti-pattern

---

## 🎯 COMMON TASKS

### Task 1: Add a New Test File
```bash
# Create test file
touch tests/unit/test_my_feature.py

# Add imports and tests
cat > tests/unit/test_my_feature.py << 'EOF'
import pytest
from framework.my_module import MyClass

class TestMyClass:
    def test_basic_functionality(self):
        obj = MyClass()
        result = obj.do_something()
        assert result == expected_value
    
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        obj = MyClass()
        result = await obj.do_something_async()
        assert result == expected_value
EOF

# Run new tests
pytest tests/unit/test_my_feature.py -v
```

### Task 2: Create a New Plugin
```python
# Create file: framework/plugins/my_custom_plugin.py
from framework.plugins.plugin_system import BasePlugin, PluginMetadata, PluginHook

class MyCustomPlugin(BasePlugin):
    def __init__(self):
        metadata = PluginMetadata(
            name="my-custom-plugin",
            version="1.0.0",
            author="Your Name",
            description="Does something awesome"
        )
        super().__init__(metadata)
    
    def load(self):
        self.logger = get_logger(__name__)
        self.logger.info("Plugin loaded")
    
    def unload(self):
        self.logger.info("Plugin unloaded")
    
    @PluginHook(name="test_started", priority=100)
    async def on_test_started(self, test_name: str):
        self.logger.info(f"Test starting: {test_name}")
    
    @PluginHook(name="test_completed", priority=100)
    async def on_test_completed(self, test_name: str, result: dict):
        self.logger.info(f"Test completed: {test_name}, result: {result}")

# Use plugin
from framework.plugins.plugin_system import PluginManager

manager = PluginManager()
plugin = MyCustomPlugin()
manager.load_plugin_instance(plugin)

# Execute hooks
await manager.execute_hook("test_started", test_name="test_login")
```

### Task 3: Setup CI/CD on GitHub
```bash
# 1. Push workflows to GitHub
git add .github/workflows/
git commit -m "Add CI/CD workflows"
git push

# 2. Add secrets in GitHub repository settings:
# Settings -> Secrets and variables -> Actions -> New repository secret

# Required secrets:
# - SLACK_WEBHOOK: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
# - PYPI_API_TOKEN: pypi-... (from PyPI account settings)
# - TEST_PYPI_API_TOKEN: pypi-... (from Test PyPI)

# 3. Workflows will run automatically on:
# - Every push to main/develop
# - Every pull request
# - Manual trigger (workflow_dispatch)
# - Git tags for releases (v*.*.*)
```

### Task 4: Generate Documentation
```bash
# Generate HTML documentation
pdoc --html framework -o docs/

# Or use Sphinx
sphinx-quickstart docs/
sphinx-apidoc -o docs/ framework/
cd docs && make html

# View documentation
start docs/_build/html/index.html  # Windows
```

### Task 5: Performance Profiling
```python
# Install profiler
pip install pytest-profiling

# Run with profiling
pytest tests/ --profile --profile-svg

# View SVG profile
start prof/combined.svg  # Windows

# Or use built-in performance logger
from framework.observability.logging import PerformanceLogger

perf_logger = PerformanceLogger()

with perf_logger.measure("database_query"):
    result = await db.fetch_all("SELECT * FROM large_table")

# Logs: {"operation": "database_query", "duration": 2.345}
```

---

## 🐛 TROUBLESHOOTING

### Issue 1: Playwright Browser Not Found
```bash
# Solution: Install browsers
playwright install chromium firefox webkit

# Or specific browser
playwright install chromium
```

### Issue 2: Import Errors
```bash
# Solution: Install all dependencies
pip install -r requirements.txt

# Or specific package
pip install asyncpg  # For PostgreSQL
pip install aiomysql  # For MySQL
```

### Issue 3: Tests Failing with "Module not found"
```bash
# Solution: Ensure package structure
touch framework/__init__.py
touch framework/observability/__init__.py
touch framework/testing/__init__.py

# Or reinstall in development mode
pip install -e .
```

### Issue 4: OpenTelemetry Not Working
```python
# Solution: Initialize telemetry first
from framework.observability import initialize_telemetry, TelemetryConfig

# In conftest.py
@pytest.fixture(scope="session", autouse=True)
def setup_telemetry():
    config = TelemetryConfig(enable_console=True)
    initialize_telemetry(config)
    yield
    shutdown_telemetry()
```

### Issue 5: Visual Tests Always Failing
```bash
# Solution: Update baselines first
pytest tests/visual/ --update-baselines

# Then run comparison
pytest tests/visual/
```

---

## 📖 ADDITIONAL RESOURCES

### Documentation Files
- `README.md` - Main documentation
- `COMPREHENSIVE_RATING_ALL_AREAS.md` - Complete feature analysis
- `PHASE_3_IMPLEMENTATION_COMPLETE.md` - Implementation details
- `ALL_PHASES_COMPLETE_FINAL_SUMMARY.md` - Final summary
- `HOW_TO_RUN_BOOKSLOT_TESTS.md` - BookSlot-specific guide

### Example Files
- `examples/constructor_injection.py` - DI examples
- `examples/modern_features_quickstart.py` - Feature overview
- `quick_start.py` - Basic setup
- `quick_start_enhanced.py` - Advanced setup

### Test Files
- `tests/unit/` - Unit tests (8 files, 4500+ lines)
- `tests/integration/` - Integration tests
- `tests/visual/` - Visual regression tests

### Configuration Files
- `pytest.ini` - Pytest configuration
- `requirements.txt` - Python dependencies
- `.github/workflows/` - CI/CD pipelines

---

## 🎓 LEARNING PATH

### Beginner (Day 1-2)
1. ✅ Install framework and dependencies
2. ✅ Run existing tests
3. ✅ Write your first test
4. ✅ Use basic logging

### Intermediate (Week 1)
1. ✅ Use constructor injection
2. ✅ Create custom plugins
3. ✅ Add visual regression tests
4. ✅ Setup distributed testing

### Advanced (Month 1)
1. ✅ Implement OpenTelemetry tracing
2. ✅ Create custom microservices
3. ✅ Setup CI/CD pipelines
4. ✅ Optimize test performance

### Expert (Month 2+)
1. ✅ Design complex test architectures
2. ✅ Build custom frameworks on top
3. ✅ Contribute to core framework
4. ✅ Mentor team members

---

## ✨ NEXT STEPS

1. **Explore Examples** - Check `examples/` directory
2. **Run Tests** - `pytest tests/ -v --cov=framework`
3. **Read Documentation** - Review all .md files
4. **Setup CI/CD** - Add GitHub secrets and enable Actions
5. **Start Building** - Create your first test suite!

---

## 💬 SUPPORT

### Getting Help
- Read documentation files
- Check examples directory
- Review test files for patterns
- Run `pytest --help` for options

### Reporting Issues
- Check existing tests for similar scenarios
- Verify installation: `python verify_installation.py`
- Check logs: `logs/` directory

---

**Framework Status:** 🟢 **PRODUCTION READY**  
**Documentation Status:** ✅ **COMPLETE**  
**Support Status:** 💚 **AVAILABLE**

**Happy Testing! 🚀**
