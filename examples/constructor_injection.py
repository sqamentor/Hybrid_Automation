"""Constructor injection examples demonstrating SOLID principles.

Examples:
- Pure constructor injection (no service locator)
- Interface segregation
- Dependency inversion
- Easy testing with mocks
"""
from typing import Protocol, Optional, Dict, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass


# ============================================================================
# Example 1: Page Object with Constructor Injection
# ============================================================================

class IBrowser(Protocol):
    """Browser interface (dependency inversion)."""
    
    def navigate(self, url: str) -> None: ...
    def click(self, selector: str) -> None: ...
    def fill(self, selector: str, value: str) -> None: ...
    def get_text(self, selector: str) -> str: ...


class ILogger(Protocol):
    """Logger interface."""
    
    def info(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...


class LoginPage:
    """Login page with pure constructor injection.

    Example:
        ```python
        # Production code
        browser = PlaywrightBrowser()
        logger = StructuredLogger()

        login_page = LoginPage(browser, logger)
        login_page.login("admin", "password123")

        # Test code with mocks
        mock_browser = Mock(spec=IBrowser)
        mock_logger = Mock(spec=ILogger)

        login_page = LoginPage(mock_browser, mock_logger)
        login_page.login("test", "test123")

        mock_browser.fill.assert_called()
        mock_logger.info.assert_called()
        ```
    """
    
    def __init__(self, browser: IBrowser, logger: ILogger):
        """Initialize login page with dependencies.

        Args:
            browser: Browser implementation
            logger: Logger implementation
        """
        self._browser = browser
        self._logger = logger
    
    def login(self, username: str, password: str) -> None:
        """Perform login action.

        Args:
            username: Username
            password: Password
        """
        self._logger.info(f"Logging in as {username}")
        
        self._browser.navigate("/login")
        self._browser.fill("#username", username)
        self._browser.fill("#password", password)
        self._browser.click("#login-button")
        
        self._logger.info("Login completed")
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in.

        Returns:
            True if logged in, False otherwise
        """
        try:
            welcome_text = self._browser.get_text("#welcome-message")
            return "Welcome" in welcome_text
        except Exception:
            return False


# ============================================================================
# Example 2: Test Runner with Multiple Dependencies
# ============================================================================

class ITestExecutor(Protocol):
    """Test executor interface."""
    
    def execute_test(self, test_name: str) -> Dict[str, Any]: ...


class IReporter(Protocol):
    """Reporter interface."""
    
    def report_result(self, test_name: str, result: Dict[str, Any]) -> None: ...


class INotifier(Protocol):
    """Notifier interface."""
    
    def notify(self, message: str) -> None: ...


class TestRunner:
    """Test runner with constructor injection.

    Example:
        ```python
        # Production
        executor = PlaywrightExecutor()
        reporter = AllureReporter()
        notifier = SlackNotifier()

        runner = TestRunner(executor, reporter, notifier)
        runner.run_test("test_login")

        # Testing
        mock_executor = Mock(spec=ITestExecutor)
        mock_executor.execute_test.return_value = {"status": "passed"}

        runner = TestRunner(mock_executor, Mock(), Mock())
        result = runner.run_test("test_mock")

        assert result["status"] == "passed"
        ```
    """
    
    def __init__(
        self,
        executor: ITestExecutor,
        reporter: IReporter,
        notifier: Optional[INotifier] = None
    ):
        """Initialize test runner with dependencies.

        Args:
            executor: Test executor
            reporter: Test reporter
            notifier: Optional notifier
        """
        self._executor = executor
        self._reporter = reporter
        self._notifier = notifier
    
    def run_test(self, test_name: str) -> Dict[str, Any]:
        """Run a test and report results.

        Args:
            test_name: Name of the test

        Returns:
            Test result dictionary
        """
        # Execute test
        result = self._executor.execute_test(test_name)
        
        # Report result
        self._reporter.report_result(test_name, result)
        
        # Notify if test failed
        if self._notifier and result.get("status") == "failed":
            self._notifier.notify(f"Test {test_name} failed")
        
        return result


# ============================================================================
# Example 3: API Client with Configuration Injection
# ============================================================================

@dataclass
class APIConfig:
    """API configuration."""
    base_url: str
    timeout: int = 30
    api_key: Optional[str] = None


class IHTTPClient(Protocol):
    """HTTP client interface."""
    
    def get(self, url: str, headers: Dict[str, str]) -> Dict[str, Any]: ...
    def post(self, url: str, data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]: ...


class APIClient:
    """API client with constructor injection.

    Example:
        ```python
        # Production
        config = APIConfig(
            base_url="https://api.example.com",
            api_key="secret123"
        )
        http_client = HTTPXClient()

        api_client = APIClient(config, http_client)
        users = api_client.get_users()

        # Testing
        mock_http = Mock(spec=IHTTPClient)
        mock_http.get.return_value = {"users": [{"id": 1, "name": "Test"}]}

        api_client = APIClient(APIConfig("http://test"), mock_http)
        users = api_client.get_users()

        assert len(users) == 1
        ```
    """
    
    def __init__(self, config: APIConfig, http_client: IHTTPClient):
        """Initialize API client with dependencies.

        Args:
            config: API configuration
            http_client: HTTP client implementation
        """
        self._config = config
        self._http_client = http_client
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        
        if self._config.api_key:
            headers["Authorization"] = f"Bearer {self._config.api_key}"
        
        return headers
    
    def get_users(self) -> list:
        """Get list of users.

        Returns:
            List of user dictionaries
        """
        url = f"{self._config.base_url}/users"
        response = self._http_client.get(url, self._get_headers())
        return response.get("users", [])
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user.

        Args:
            user_data: User data dictionary

        Returns:
            Created user dictionary
        """
        url = f"{self._config.base_url}/users"
        response = self._http_client.post(url, user_data, self._get_headers())
        return response


# ============================================================================
# Example 4: Factory Pattern with Constructor Injection
# ============================================================================

class IDatabase(Protocol):
    """Database interface."""
    
    def query(self, sql: str) -> list: ...
    def execute(self, sql: str) -> None: ...


class UserRepository:
    """User repository with database injection.

    Example:
        ```python
        # Production
        database = PostgreSQLDatabase()
        repo = UserRepository(database)
        users = repo.get_all_users()

        # Testing
        mock_db = Mock(spec=IDatabase)
        mock_db.query.return_value = [{"id": 1, "name": "Test"}]

        repo = UserRepository(mock_db)
        users = repo.get_all_users()

        assert len(users) == 1
        mock_db.query.assert_called_with("SELECT * FROM users")
        ```
    """
    
    def __init__(self, database: IDatabase):
        """Initialize repository with database.

        Args:
            database: Database implementation
        """
        self._db = database
    
    def get_all_users(self) -> list:
        """Get all users."""
        return self._db.query("SELECT * FROM users")
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        results = self._db.query(f"SELECT * FROM users WHERE id = {user_id}")
        return results[0] if results else None
    
    def create_user(self, name: str, email: str) -> None:
        """Create new user."""
        self._db.execute(f"INSERT INTO users (name, email) VALUES ('{name}', '{email}')")


class RepositoryFactory:
    """Factory for creating repositories with constructor injection.

    Example:
        ```python
        # Setup
        factory = RepositoryFactory(database)

        # Get repositories
        user_repo = factory.create_user_repository()
        order_repo = factory.create_order_repository()

        # All repositories share same database instance
        users = user_repo.get_all_users()
        orders = order_repo.get_all_orders()
        ```
    """
    
    def __init__(self, database: IDatabase):
        """Initialize factory with database.

        Args:
            database: Database implementation
        """
        self._database = database
    
    def create_user_repository(self) -> UserRepository:
        """Create user repository."""
        return UserRepository(self._database)
    
    def create_order_repository(self):
        """Create order repository (example)."""
        # Return OrderRepository with same database
        pass


# ============================================================================
# Example 5: Composite Pattern with Constructor Injection
# ============================================================================

class IValidator(Protocol):
    """Validator interface."""
    
    def validate(self, value: Any) -> bool: ...
    def get_errors(self) -> list: ...


class CompositeValidator:
    """Composite validator with multiple validators injected.

    Example:
        ```python
        # Create validators
        length_validator = LengthValidator(min_length=8)
        pattern_validator = PatternValidator(r"^[a-zA-Z0-9]+$")
        strength_validator = PasswordStrengthValidator()

        # Compose validators
        password_validator = CompositeValidator([
            length_validator,
            pattern_validator,
            strength_validator
        ])

        # Validate
        is_valid = password_validator.validate("MyPassword123")
        errors = password_validator.get_errors()
        ```
    """
    
    def __init__(self, validators: list):
        """Initialize composite validator.

        Args:
            validators: List of validator instances
        """
        self._validators = validators
        self._errors = []
    
    def validate(self, value: Any) -> bool:
        """Validate value with all validators.

        Args:
            value: Value to validate

        Returns:
            True if all validators pass, False otherwise
        """
        self._errors = []
        all_valid = True
        
        for validator in self._validators:
            if not validator.validate(value):
                all_valid = False
                self._errors.extend(validator.get_errors())
        
        return all_valid
    
    def get_errors(self) -> list:
        """Get all validation errors."""
        return self._errors


# ============================================================================
# Testing Utilities
# ============================================================================

def create_mock_dependencies() -> Dict[str, Any]:
    """Create mock dependencies for testing.

    Returns:
        Dictionary of mock objects

    Example:
        ```python
        from unittest.mock import Mock

        mocks = create_mock_dependencies()

        # Use mocks in tests
        login_page = LoginPage(mocks["browser"], mocks["logger"])
        ```
    """
    from unittest.mock import Mock
    
    return {
        "browser": Mock(spec=IBrowser),
        "logger": Mock(spec=ILogger),
        "executor": Mock(spec=ITestExecutor),
        "reporter": Mock(spec=IReporter),
        "notifier": Mock(spec=INotifier),
        "http_client": Mock(spec=IHTTPClient),
        "database": Mock(spec=IDatabase)
    }
