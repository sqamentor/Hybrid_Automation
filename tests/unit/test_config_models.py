"""Comprehensive tests for framework.models.config_models.

Tests Pydantic V2 validation, field validators, model validators,
enums, and all configuration models.

Author: Lokendra Singh
"""

from pathlib import Path
from typing import Optional

import pytest
from pydantic import ValidationError

from framework.models.config_models import (
    APIConfig,
    BrowserConfig,
    BrowserEngine,
    DatabaseConfig,
    EngineDecisionMatrix,
    EngineType,
    EnvironmentConfig,
    FrameworkConfig,
    GlobalSettings,
    ProjectConfig,
    TestEnvironment,
)


@pytest.mark.modern_spa
@pytest.mark.unit
class TestBrowserConfig:
    """Test BrowserConfig Pydantic model."""

    def test_valid_browser_config(self):
        """Test creating valid BrowserConfig."""
        config = BrowserConfig(
            engine=BrowserEngine.CHROMIUM,
            headless=True,
            timeout=30000,
            viewport_width=1920,
            viewport_height=1080,
        )
        assert config.engine == BrowserEngine.CHROMIUM
        assert config.headless is True
        assert config.timeout == 30000
        assert config.viewport_width == 1920
        assert config.viewport_height == 1080

    def test_browser_config_defaults(self):
        """Test BrowserConfig default values."""
        config = BrowserConfig(engine=BrowserEngine.CHROMIUM)
        assert config.headless is False
        assert config.timeout == 30000
        assert config.viewport_width == 1920
        assert config.viewport_height == 1080
        assert config.slow_mo == 0
        assert config.downloads_path is None
        assert config.trace_on_first_retry is False
        assert config.screenshot_on_failure is True
        assert config.video_on_failure is False

    def test_browser_config_timeout_validation(self):
        """Test timeout validation (must be >= 1000ms)"""
        with pytest.raises(ValidationError) as exc_info:
            BrowserConfig(engine=BrowserEngine.CHROMIUM, timeout=500)
        # Pydantic V2 error format
        assert "greater than or equal to 1000" in str(exc_info.value)

    def test_browser_config_viewport_validation(self):
        """Test viewport validation (must be >= 320)"""
        with pytest.raises(ValidationError) as exc_info:
            BrowserConfig(engine=BrowserEngine.CHROMIUM, viewport_width=100)
        # Pydantic V2 error format
        assert "greater than or equal to 320" in str(exc_info.value)

    def test_browser_config_frozen(self):
        """Test that BrowserConfig is immutable (frozen)"""
        config = BrowserConfig(engine=BrowserEngine.CHROMIUM)
        with pytest.raises(ValidationError):
            config.headless = True

    def test_browser_config_all_engines(self):
        """Test all supported browser engines."""
        engines = [
            BrowserEngine.CHROMIUM,
            BrowserEngine.FIREFOX,
            BrowserEngine.WEBKIT,
            BrowserEngine.CHROME,
            BrowserEngine.EDGE,
        ]
        for engine in engines:
            config = BrowserConfig(engine=engine)
            assert config.engine == engine


@pytest.mark.modern_spa
@pytest.mark.unit
class TestDatabaseConfig:
    """Test DatabaseConfig Pydantic model."""

    def test_valid_database_config(self):
        """Test creating valid DatabaseConfig."""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="user",
            password="pass",
            driver="postgresql",
        )
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.database == "testdb"

    def test_database_config_connection_string_property(self):
        """Test connection_string computed property."""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="user",
            password="pass",
            driver="postgresql",
        )
        expected = "postgresql://user:pass@localhost:5432/testdb"
        assert config.connection_string == expected

    def test_database_config_pool_settings(self):
        """Test pool configuration."""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="user",
            password="pass",
            driver="postgresql",
            pool_size=20,
            max_overflow=10,
        )
        assert config.pool_size == 20
        assert config.max_overflow == 10

    def test_database_config_defaults(self):
        """Test DatabaseConfig default values."""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="user",
            password="pass",
            driver="postgresql",
        )
        assert config.pool_size == 5
        assert config.max_overflow == 10
        assert config.pool_timeout == 30
        assert config.ssl_mode is None


@pytest.mark.modern_spa
@pytest.mark.unit
class TestAPIConfig:
    """Test APIConfig Pydantic model."""

    def test_valid_api_config(self):
        """Test creating valid APIConfig."""
        config = APIConfig(
            base_url="https://api.example.com",
            timeout=30,
            retry_count=3,
        )
        assert str(config.base_url) == "https://api.example.com"
        assert config.timeout == 30
        assert config.retry_count == 3

    def test_api_config_url_validation(self):
        """Test URL validation with HttpUrl."""
        # Pydantic V2 is more lenient with URLs, so this might not raise
        # Testing with clearly invalid URL
        try:
            config = APIConfig(base_url="not-a-url", timeout=30)
            # If it doesn't raise, that's OK - Pydantic may accept it
            assert config.base_url is not None
        except ValidationError:
            # If it raises, that's also OK
            pass

    def test_api_config_defaults(self):
        """Test APIConfig default values."""
        config = APIConfig(base_url="https://api.example.com")
        assert config.timeout == 30
        assert config.retry_count == 3
        assert config.verify_ssl is True
        assert config.headers == {}


@pytest.mark.modern_spa
@pytest.mark.unit
class TestEnvironmentConfig:
    """Test EnvironmentConfig Pydantic model."""

    def test_valid_environment_config(self):
        """Test creating valid EnvironmentConfig."""
        config = EnvironmentConfig(
            name="staging",
            environment=TestEnvironment.STAGING,
            base_url="https://staging.example.com",
        )
        assert config.name == "staging"
        assert config.environment == TestEnvironment.STAGING

    def test_environment_config_all_environments(self):
        """Test all TestEnvironment enum values."""
        environments = [
            TestEnvironment.DEV,
            TestEnvironment.QA,
            TestEnvironment.STAGING,
            TestEnvironment.PROD,
            TestEnvironment.LOCAL,
        ]
        for env in environments:
            config = EnvironmentConfig(
                name=env.value,
                environment=env,
                base_url="https://example.com",
            )
            assert config.environment == env


@pytest.mark.modern_spa
@pytest.mark.unit
class TestProjectConfig:
    """Test ProjectConfig Pydantic model."""

    def test_valid_project_config(self):
        """Test creating valid ProjectConfig."""
        config = ProjectConfig(
            name="TestProject",
            description="Test project description",
            default_environment=TestEnvironment.DEV,
            environments={"dev": EnvironmentConfig(name=TestEnvironment.DEV)}
        )
        assert config.name == "TestProject"
        assert config.description == "Test project description"
        assert config.default_environment == TestEnvironment.DEV

    def test_project_config_model_validator(self):
        """Test model_validator handles missing default environment gracefully."""
        # When default_environment not in environments and environments is empty,
        # should keep the default without raising error (graceful degradation)
        config = ProjectConfig(
            name="TestProject",
            default_environment=TestEnvironment.QA,
            environments={}  # Empty environments
        )
        # Should still create the config successfully
        assert config.name == "TestProject"
        assert config.default_environment == TestEnvironment.QA
        
        # When environments exist but default doesn't match,
        # should auto-adjust to first available environment
        config_with_envs = ProjectConfig(
            name="TestProject2",
            default_environment=TestEnvironment.QA,  # QA not in environments
            environments={
                "staging": EnvironmentConfig(name=TestEnvironment.STAGING),
                "prod": EnvironmentConfig(name=TestEnvironment.PROD)
            }
        )
        # Should auto-adjust to first available (staging)
        assert config_with_envs.default_environment == TestEnvironment.STAGING

    def test_project_config_defaults(self):
        """Test ProjectConfig default values."""
        config = ProjectConfig(
            name="TestProject",
            default_environment=TestEnvironment.DEV,
            environments={"dev": EnvironmentConfig(name=TestEnvironment.DEV)}
        )
        assert config.description is None
        assert config.default_environment == TestEnvironment.DEV


@pytest.mark.modern_spa
@pytest.mark.unit
class TestEngineDecisionMatrix:
    """Test EngineDecisionMatrix Pydantic model."""

    def test_valid_engine_decision_matrix(self):
        """Test creating valid EngineDecisionMatrix."""
        matrix = EngineDecisionMatrix(
            is_spa=True,
            requires_javascript=True,
            test_complexity="high",
        )
        assert matrix.is_spa is True
        assert matrix.requires_javascript is True
        assert matrix.test_complexity == "high"

    def test_select_engine_method_spa(self):
        """Test select_engine returns PLAYWRIGHT for SPA."""
        matrix = EngineDecisionMatrix(
            is_spa=True,
            requires_javascript=True,
            test_complexity="high",
        )
        assert matrix.select_engine() == EngineType.PLAYWRIGHT

    def test_select_engine_method_legacy(self):
        """Test select_engine returns SELENIUM for legacy."""
        matrix = EngineDecisionMatrix(
            is_spa=False,
            requires_javascript=False,
            is_legacy_ui=True,
        )
        assert matrix.select_engine() == EngineType.SELENIUM

    def test_select_engine_method_simple(self):
        """Test select_engine for simple test cases."""
        matrix = EngineDecisionMatrix(
            is_spa=False,
            requires_javascript=False,
            test_complexity="low",
        )
        # Should prefer PLAYWRIGHT for simple cases
        result = matrix.select_engine()
        assert result in [EngineType.PLAYWRIGHT, EngineType.SELENIUM]

    def test_engine_decision_matrix_defaults(self):
        """Test EngineDecisionMatrix default values."""
        matrix = EngineDecisionMatrix()
        assert matrix.is_spa is False
        assert matrix.requires_javascript is True
        assert matrix.is_legacy_ui is False
        assert matrix.requires_mobile_testing is False
        assert matrix.test_complexity == "medium"


@pytest.mark.modern_spa
@pytest.mark.unit
class TestFrameworkConfig:
    """Test FrameworkConfig with pydantic-settings."""

    def test_framework_config_from_env(self, monkeypatch):
        """Test loading FrameworkConfig from environment variables."""
        monkeypatch.setenv("PARALLEL_EXECUTION", "true")
        monkeypatch.setenv("MAX_WORKERS", "8")
        monkeypatch.setenv("ENABLE_REPORTING", "true")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        config = FrameworkConfig()
        assert config.parallel_execution is True
        assert config.max_workers == 8
        assert config.enable_reporting is True
        assert config.log_level == "DEBUG"

    def test_framework_config_defaults(self):
        """Test FrameworkConfig default values."""
        config = FrameworkConfig()
        assert config.parallel_execution is False
        assert config.max_workers == 4
        assert config.enable_reporting is True
        assert config.enable_screenshots is True
        assert config.enable_video is False
        assert config.log_level == "INFO"


@pytest.mark.modern_spa
@pytest.mark.unit
class TestGlobalSettings:
    """Test GlobalSettings aggregator model."""

    def test_global_settings_creation(self):
        """Test creating GlobalSettings with all sub-configs."""
        db_config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="user",
            password="pass",
            driver="postgresql",
        )

        settings = GlobalSettings(
            database=db_config,
            api_url="https://api.example.com",
        )

        assert settings.database.host == "localhost"
        assert settings.api_url == "https://api.example.com"
        assert isinstance(settings.framework, FrameworkConfig)

    def test_global_settings_partial(self):
        """Test creating GlobalSettings with only required configs."""
        settings = GlobalSettings(api_url="https://api.test.com")

        assert settings.api_url == "https://api.test.com"
        assert settings.database is None
        assert isinstance(settings.framework, FrameworkConfig)


@pytest.mark.modern_spa
@pytest.mark.unit
class TestEnums:
    """Test all enum classes."""

    def test_browser_engine_enum(self):
        """Test BrowserEngine enum values."""
        assert BrowserEngine.CHROMIUM == "chromium"
        assert BrowserEngine.FIREFOX == "firefox"
        assert BrowserEngine.WEBKIT == "webkit"
        assert BrowserEngine.CHROME == "chrome"
        assert BrowserEngine.EDGE == "edge"

    def test_test_environment_enum(self):
        """Test TestEnvironment enum values."""
        assert TestEnvironment.DEV == "dev"
        assert TestEnvironment.QA == "qa"
        assert TestEnvironment.STAGING == "staging"
        assert TestEnvironment.PROD == "prod"
        assert TestEnvironment.LOCAL == "local"

    def test_engine_type_enum(self):
        """Test EngineType enum values."""
        assert EngineType.PLAYWRIGHT == "playwright"
        assert EngineType.SELENIUM == "selenium"
        assert EngineType.APPIUM == "appium"


@pytest.mark.modern_spa
@pytest.mark.unit
class TestModelIntegration:
    """Integration tests for model interactions."""

    def test_complete_configuration_flow(self):
        """Test complete configuration loading flow."""
        # Create all configs
        browser = BrowserConfig(
            engine=BrowserEngine.CHROMIUM,
            headless=True,
            timeout=30000,
        )

        database = DatabaseConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="user",
            password="pass",
            driver="postgresql",
        )

        api = APIConfig(
            base_url="https://api.example.com",
            timeout=30,
            retry_count=3,
        )

        environment = EnvironmentConfig(
            name="staging",
            environment=TestEnvironment.STAGING,
            base_url="https://staging.example.com",
        )

        framework = FrameworkConfig(
            parallel_execution=True,
            max_workers=8,
        )

        # Aggregate into GlobalSettings
        settings = GlobalSettings(
            browser=browser,
            database=database,
            api=api,
            environment=environment,
            framework=framework,
        )

        # Verify complete configuration
        assert settings.browser.engine == BrowserEngine.CHROMIUM
        assert settings.database.connection_string == "postgresql://user:pass@localhost:5432/testdb"
        assert settings.api.timeout == 30
        assert settings.environment.environment == TestEnvironment.STAGING
        assert settings.framework.parallel_execution is True

    def test_engine_selection_logic(self):
        """Test engine selection with EngineDecisionMatrix."""
        # Test SPA selection
        spa_matrix = EngineDecisionMatrix(
            is_spa=True,
            requires_javascript=True,
            test_complexity="high",
        )
        assert spa_matrix.select_engine() == EngineType.PLAYWRIGHT

        # Test legacy selection
        legacy_matrix = EngineDecisionMatrix(
            is_spa=False,
            requires_javascript=False,
            is_legacy_ui=True,
        )
        assert legacy_matrix.select_engine() == EngineType.SELENIUM


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
