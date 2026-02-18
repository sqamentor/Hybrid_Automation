"""
Pydantic V2 Configuration Models

Type-safe, validated configuration models for the entire framework.
All configs use Pydantic V2 for runtime validation and serialization.
"""

from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from framework.observability.universal_logger import log_function

logger = logging.getLogger(__name__)


class BrowserEngine(str, Enum):
    """Supported browser engines"""

    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"
    CHROME = "chrome"
    EDGE = "edge"


class TestEnvironment(str, Enum):
    """Test environment types"""

    DEV = "dev"
    QA = "qa"
    STAGING = "staging"
    PROD = "prod"
    PRODUCTION = "production"  # Alias for prod for backward compatibility
    LOCAL = "local"


class EngineType(str, Enum):
    """Automation engine types"""

    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    HYBRID = "hybrid"
    API = "api"
    APPIUM = "appium"


class BrowserConfig(BaseModel):
    """Browser configuration with validation"""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    engine: BrowserEngine = Field(
        default=BrowserEngine.CHROMIUM, description="Browser engine to use"
    )
    headless: bool = Field(default=False, description="Run browser in headless mode")
    viewport_width: int = Field(default=1920, ge=320, le=7680, description="Browser viewport width")
    viewport_height: int = Field(
        default=1080, ge=240, le=4320, description="Browser viewport height"
    )
    slow_mo: int = Field(
        default=0, ge=0, le=5000, description="Slow down operations by N milliseconds"
    )
    timeout: int = Field(
        default=30000, ge=1000, le=300000, description="Default timeout in milliseconds"
    )
    device_scale_factor: float = Field(
        default=1.0, ge=0.1, le=5.0, description="Device scale factor"
    )
    locale: str = Field(
        default="en-US", pattern=r"^[a-z]{2}-[A-Z]{2}$", description="Browser locale"
    )
    timezone_id: str = Field(default="America/New_York", description="Timezone ID")
    user_agent: Optional[str] = Field(default=None, description="Custom user agent string")
    args: List[str] = Field(
        default_factory=lambda: ["--start-maximized"], description="Browser launch arguments"
    )
    downloads_path: Optional[str] = Field(
        default=None, description="Custom downloads directory path"
    )
    trace_on_first_retry: bool = Field(default=False, description="Enable trace on first retry")
    screenshot_on_failure: bool = Field(default=True, description="Take screenshot on test failure")
    video_on_failure: bool = Field(default=False, description="Record video on test failure")

    @field_validator("timeout")
    @classmethod
    @log_function(log_args=True, log_result=True)
    def validate_timeout(cls, v: int) -> int:
        """Ensure timeout is reasonable"""
        if v < 1000:
            raise ValueError("Timeout must be at least 1000ms")
        return v

    @field_validator("viewport_width")
    @classmethod
    @log_function(log_args=True, log_result=True)
    def validate_viewport_width(cls, v: int) -> int:
        """Ensure viewport width is reasonable"""
        if v < 320:
            raise ValueError("Viewport width must be at least 320")
        return v


class DatabaseConfig(BaseModel):
    """Database configuration with validation"""

    model_config = ConfigDict(
        frozen=False,
        extra="allow",
        validate_assignment=True,
    )

    host: str = Field(..., description="Database host")
    port: int = Field(..., ge=1, le=65535, description="Database port")
    database: str = Field(..., min_length=1, description="Database name")
    username: str = Field(..., min_length=1, description="Database username")
    password: str = Field(..., description="Database password")
    driver: str = Field(default="postgresql", description="Database driver")
    pool_size: int = Field(default=5, ge=1, le=100, description="Connection pool size")
    max_overflow: int = Field(default=10, ge=0, le=100, description="Max pool overflow")
    pool_timeout: int = Field(
        default=30, ge=1, le=300, description="Connection pool timeout in seconds"
    )
    ssl_mode: Optional[str] = Field(default=None, description="SSL mode for connection")
    echo: bool = Field(default=False, description="Echo SQL statements")

    @property
    def connection_string(self) -> str:
        """Generate connection string"""
        return f"{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class APIConfig(BaseModel):
    """API configuration with validation"""

    model_config = ConfigDict(
        frozen=False,
        extra="allow",
        validate_assignment=True,
    )

    base_url: Union[HttpUrl, str] = Field(..., description="API base URL")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    headers: Dict[str, str] = Field(default_factory=dict, description="Default headers")
    auth_token: Optional[str] = Field(default=None, description="Authentication token")
    retry_attempts: int = Field(
        default=3, ge=0, le=10, description="Number of retry attempts", alias="retry_count"
    )
    retry_delay: float = Field(default=1.0, ge=0.1, le=60.0, description="Delay between retries")

    @property
    def retry_count(self) -> int:
        """Alias for retry_attempts for backward compatibility"""
        return self.retry_attempts

    @field_validator("base_url")
    @classmethod
    @log_function(log_args=True, log_result=True)
    def validate_base_url(cls, v: Union[HttpUrl, str]) -> str:
        """Ensure base_url is properly formatted"""
        url_str = str(v)
        return url_str.rstrip("/")


class EnvironmentConfig(BaseModel):
    """Environment-specific configuration"""

    model_config = ConfigDict(
        frozen=False,
        extra="allow",
        validate_assignment=True,
    )

    name: TestEnvironment = Field(..., description="Environment name")
    browser: BrowserConfig = Field(default_factory=BrowserConfig, description="Browser config")
    databases: Dict[str, DatabaseConfig] = Field(
        default_factory=dict, description="Database configs"
    )
    apis: Dict[str, APIConfig] = Field(default_factory=dict, description="API configs")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Environment variables")


class ProjectConfig(BaseModel):
    """Project-specific configuration"""

    model_config = ConfigDict(
        frozen=False,
        extra="allow",
        validate_assignment=True,
    )

    name: str = Field(..., min_length=1, description="Project name")
    description: Optional[str] = Field(default=None, description="Project description")
    environments: Dict[str, EnvironmentConfig] = Field(
        default_factory=dict, description="Environment configs"
    )
    default_environment: TestEnvironment = Field(
        default=TestEnvironment.DEV, description="Default environment"
    )

    @model_validator(mode="after")
    @log_function(log_timing=True)
    def validate_default_environment_exists(self) -> ProjectConfig:
        """Ensure default environment exists in environments dict (if environments are defined)"""
        # Only validate if environments are defined
        if self.environments:
            # Check if default environment exists in environments
            default_env_value = self.default_environment.value
            # Also check the enum name for aliases (e.g., 'production' or 'prod')
            env_keys = list(self.environments.keys())

            if default_env_value not in env_keys:
                # If default environment doesn't exist, use the first available environment
                if env_keys:
                    first_env = env_keys[0]
                    # Try to match the first environment to a TestEnvironment value
                    try:
                        self.default_environment = TestEnvironment(first_env)
                    except ValueError:
                        # If first env doesn't match any TestEnvironment, keep default
                        pass
        return self


class EngineDecisionMatrix(BaseModel):
    """Engine selection decision matrix with intelligent recommendations"""

    model_config = ConfigDict(
        frozen=False,
        extra="allow",
        validate_assignment=True,
    )

    # Test characteristics
    is_spa: bool = Field(default=False, description="Is this a Single Page Application")
    requires_javascript: bool = Field(
        default=True, description="Does the test require JavaScript execution"
    )
    is_legacy_ui: bool = Field(default=False, description="Is this a legacy UI (old HTML/CSS)")
    requires_mobile_testing: bool = Field(
        default=False, description="Does this require mobile testing"
    )
    test_complexity: str = Field(
        default="medium", description="Test complexity level (low/medium/high)"
    )

    # Legacy support for rules-based approach
    rules: List[Dict[str, Any]] = Field(
        default_factory=list, description="Optional custom decision rules"
    )
    default_engine: EngineType = Field(
        default=EngineType.PLAYWRIGHT, description="Default engine if no rules match"
    )

    def select_engine(self) -> EngineType:
        """
        Select appropriate engine based on test characteristics.

        Decision logic:
        - SPA + Modern: PLAYWRIGHT (best for modern apps)
        - Legacy UI: SELENIUM (better compatibility)
        - Mobile: PLAYWRIGHT (has mobile support)
        - Simple tests: PLAYWRIGHT (faster)
        - Complex tests: PLAYWRIGHT (more stable)

        Returns:
            Recommended EngineType
        """
        # Legacy UI always uses SELENIUM for compatibility
        if self.is_legacy_ui:
            return EngineType.SELENIUM

        # SPA with JavaScript requirements = PLAYWRIGHT
        if self.is_spa and self.requires_javascript:
            return EngineType.PLAYWRIGHT

        # Mobile testing = PLAYWRIGHT (better mobile support)
        if self.requires_mobile_testing:
            return EngineType.PLAYWRIGHT

        # For simple tests without JS, could use either
        if not self.requires_javascript and self.test_complexity == "low":
            return EngineType.SELENIUM

        # Default to PLAYWRIGHT for modern testing
        return self.default_engine


class FrameworkConfig(BaseSettings):
    """Global framework configuration with environment variable support"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",  # No prefix - read variables as-is
        case_sensitive=False,
        extra="allow",
    )

    # Core settings
    root_dir: Path = Field(
        default_factory=lambda: Path.cwd(), description="Framework root directory"
    )
    config_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "config", description="Configuration directory"
    )

    # Environment
    environment: TestEnvironment = Field(
        default=TestEnvironment.DEV, description="Current test environment"
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level",
    )
    log_dir: Path = Field(default_factory=lambda: Path.cwd() / "logs", description="Log directory")

    # Reporting
    report_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "reports", description="Report directory"
    )
    screenshot_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "screenshots", description="Screenshot directory"
    )
    video_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "videos", description="Video recording directory"
    )

    # Performance
    parallel_execution: bool = Field(default=False, description="Enable parallel test execution")
    max_workers: int = Field(
        default=4, ge=1, le=32, description="Maximum number of parallel workers"
    )
    parallel_workers: int = Field(
        default=4, ge=1, le=32, description="Number of parallel test workers"
    )

    # Feature flags
    enable_reporting: bool = Field(default=True, description="Enable test reporting")
    enable_screenshots: bool = Field(default=True, description="Enable screenshots")
    enable_video: bool = Field(default=False, description="Enable video recording")
    enable_video_recording: bool = Field(default=False, description="Enable video recording")
    enable_trace: bool = Field(default=False, description="Enable Playwright trace")
    enable_ai_features: bool = Field(default=False, description="Enable AI-powered features")

    @model_validator(mode="after")
    @log_function(log_timing=True)
    def create_directories(self) -> FrameworkConfig:
        """Ensure all required directories exist"""
        for dir_path in [self.log_dir, self.report_dir, self.screenshot_dir, self.video_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        return self


class GlobalSettings(BaseModel):
    """Global settings aggregating all configurations"""

    model_config = ConfigDict(
        frozen=False,
        extra="allow",
        validate_assignment=True,
    )

    framework: FrameworkConfig = Field(default_factory=FrameworkConfig)
    database: Optional[DatabaseConfig] = Field(
        default=None, description="Default database configuration"
    )
    api_url: Optional[str] = Field(default=None, description="Default API URL")
    projects: Dict[str, ProjectConfig] = Field(default_factory=dict)
    engine_matrix: EngineDecisionMatrix = Field(default_factory=EngineDecisionMatrix)

    @log_function(log_args=True, log_result=True)
    def get_project(self, name: str) -> Optional[ProjectConfig]:
        """Get project configuration by name"""
        return self.projects.get(name)

    @log_function(log_args=True, log_result=True)
    def get_environment(
        self, project_name: str, env_name: Optional[str] = None
    ) -> Optional[EnvironmentConfig]:
        """Get environment configuration for a project"""
        project = self.get_project(project_name)
        if not project:
            return None
        env = env_name or project.default_environment.value
        return project.environments.get(env)
