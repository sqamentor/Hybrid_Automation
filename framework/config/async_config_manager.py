"""
Async Configuration Manager with Pydantic V2

Modern async configuration management using Pydantic models for validation
and async I/O for performance.
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from framework.models.config_models import (
    EngineDecisionMatrix,
    EnvironmentConfig,
    FrameworkConfig,
    GlobalSettings,
    ProjectConfig,
)
from framework.protocols.config_protocols import ConfigProvider
from framework.observability.universal_logger import log_function, log_async_function

logger = logging.getLogger(__name__)


class AsyncConfigManager(ConfigProvider):
    """
    Async configuration manager with Pydantic validation.

    Features:
    - Async file I/O for performance
    - Pydantic V2 validation
    - Hot-reload support
    - Environment variable overrides
    - Type-safe configuration access
    """

    _instance: Optional[AsyncConfigManager] = None
    _lock = asyncio.Lock()

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.cwd() / "config"

        # Validate config directory exists
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Configuration directory does not exist: {self.config_dir}")

        self._settings: Optional[GlobalSettings] = None
        self._framework_config: Optional[FrameworkConfig] = None

    @classmethod
    @log_async_function(log_timing=True)
    async def get_instance(cls, config_dir: Optional[Path] = None) -> AsyncConfigManager:
        """Get singleton instance (async)"""
        async with cls._lock:
            if cls._instance is None:
                cls._instance = cls(config_dir)
                await cls._instance.load_all_configs()
            return cls._instance

    @log_async_function(log_timing=True)
    async def load_all_configs(self) -> GlobalSettings:
        """Load all configuration files asynchronously"""
        # Return cached settings if already loaded
        if self._settings is not None:
            return self._settings

        # Load configurations in parallel for performance
        tasks = [
            self._load_framework_config(),
            self._load_projects_config(),
            self._load_engine_matrix(),
            self._load_browser_config(),
            self._load_api_config(),
            self._load_database_config(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        browser_config, api_config, db_config = None, None, None

        # Extract results from tasks (last 3 are browser, api, db)
        if len(results) >= 6:
            if not isinstance(results[3], Exception):
                browser_config = results[3]
            if not isinstance(results[4], Exception):
                api_config = results[4]
            if not isinstance(results[5], Exception):
                db_config = results[5]

        # Build global settings
        self._settings = GlobalSettings(
            framework=self._framework_config or FrameworkConfig(),
            projects={},
            engine_matrix=EngineDecisionMatrix(),
            browser=browser_config,
            api=api_config,
            database=db_config,
        )

        # Process results - re-raise ValueError from YAML parsing
        for result in results:
            if isinstance(result, ValueError):
                raise result  # Re-raise ValueError (e.g., from corrupted YAML)
            elif isinstance(result, Exception):
                print(f"Error loading config: {result}")

        return self._settings

    @log_async_function(log_timing=True)
    async def _load_framework_config(self) -> None:
        """Load framework configuration"""
        self._framework_config = FrameworkConfig()

    @log_async_function(log_timing=True)
    async def _load_projects_config(self) -> None:
        """Load projects configuration from YAML"""
        projects_file = self.config_dir / "projects.yaml"
        if not projects_file.exists():
            return

        data = await self._read_yaml_async(projects_file)

        # Parse projects into Pydantic models
        projects_data = data.get("projects", {})
        for project_name, project_data in projects_data.items():
            try:
                # Convert to ProjectConfig
                environments = {}
                for env_name, env_data in project_data.get("environments", {}).items():
                    environments[env_name] = EnvironmentConfig(name=env_name, **env_data)

                project_config = ProjectConfig(
                    name=project_name,
                    description=project_data.get("description"),
                    environments=environments,
                    default_environment=project_data.get("default_environment", "dev"),
                )

                if self._settings:
                    self._settings.projects[project_name] = project_config

            except Exception as e:
                print(f"Error parsing project {project_name}: {e}")

    @log_async_function(log_timing=True)
    async def _load_engine_matrix(self) -> None:
        """Load engine decision matrix"""
        matrix_file = self.config_dir / "engine_decision_matrix.yaml"
        if not matrix_file.exists():
            return

        data = await self._read_yaml_async(matrix_file)

        try:
            if self._settings:
                self._settings.engine_matrix = EngineDecisionMatrix(
                    rules=data.get("engine_selection_rules", []),
                    default_engine=data.get("default_engine", "playwright"),
                )
        except Exception as e:
            print(f"Error parsing engine matrix: {e}")

    @log_async_function(log_timing=True)
    async def _load_browser_config(self):
        """Load browser configuration from framework config"""
        from framework.models.config_models import BrowserConfig

        config_file = self.config_dir / "browser.yaml"
        if config_file.exists():
            data = await self._read_yaml_async(config_file)
            return BrowserConfig(**data)

        # Return default config
        return BrowserConfig()

    @log_async_function(log_timing=True)
    async def _load_api_config(self):
        """Load API configuration"""
        from framework.models.config_models import APIConfig

        # Try YAML first
        config_file = self.config_dir / "api.yaml"
        if config_file.exists():
            data = await self._read_yaml_async(config_file)
            if data:
                return APIConfig(**data)

        # Try JSON
        config_file = self.config_dir / "api.json"
        if config_file.exists():
            data = await self._read_json_async(config_file)
            if data:
                return APIConfig(**data)

        # Return default with required base_url
        return APIConfig(base_url="http://localhost:8000")

    @log_async_function(log_timing=True)
    async def _load_database_config(self):
        """Load database configuration"""
        from framework.models.config_models import DatabaseConfig

        config_file = self.config_dir / "database.yaml"
        if config_file.exists():
            data = await self._read_yaml_async(config_file)
            if data:
                return DatabaseConfig(**data)

        # Return default with required fields
        return DatabaseConfig(
            host="localhost", port=5432, database="testdb", username="user", password="pass"
        )

    @log_async_function(log_timing=True)
    async def _read_yaml_async(self, file_path: Path) -> Dict[str, Any]:
        """Read YAML file asynchronously"""
        loop = asyncio.get_event_loop()

        def _read():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    result = yaml.safe_load(f)
                    return result if result is not None else {}
            except yaml.YAMLError as e:
                raise ValueError(f"Failed to parse YAML file {file_path}: {e}")

        return await loop.run_in_executor(None, _read)

    @log_async_function(log_timing=True)
    async def _read_json_async(self, file_path: Path) -> Dict[str, Any]:
        """Read JSON file asynchronously"""
        loop = asyncio.get_event_loop()

        def _read():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)

        return await loop.run_in_executor(None, _read)

    # ConfigProvider protocol implementation

    @log_function(log_args=True, log_result=True)
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        if not self._settings:
            return default

        # Support dot notation for nested keys
        keys = key.split(".")
        value = self._settings

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            elif hasattr(value, k):
                value = getattr(value, k)
            else:
                return default

        return value

    @log_function(log_args=True, log_result=True)
    def get_project_config(self, project_name: str) -> Optional[ProjectConfig]:
        """Get project configuration"""
        if not self._settings:
            return None
        return self._settings.get_project(project_name)

    @log_function(log_args=True, log_result=True)
    def get_environment_config(
        self, project_name: str, env_name: Optional[str] = None
    ) -> Optional[EnvironmentConfig]:
        """Get environment configuration"""
        if not self._settings:
            return None
        return self._settings.get_environment(project_name, env_name)

    @log_function(log_timing=True)
    def reload_config(self) -> None:
        """Reload configuration (sync wrapper)"""
        asyncio.run(self.load_all_configs())

    @log_async_function(log_timing=True)
    async def reload_config_async(self) -> None:
        """Reload configuration asynchronously"""
        await self.load_all_configs()

    @log_function(log_result=True)
    def validate_config(self) -> bool:
        """Validate configuration integrity"""
        if not self._settings:
            return False

        try:
            # Pydantic validation happens automatically
            # Just check if we have valid settings
            return isinstance(self._settings, GlobalSettings)
        except Exception:
            return False

    @property
    def settings(self) -> Optional[GlobalSettings]:
        """Get global settings"""
        return self._settings

    @property
    def framework_config(self) -> Optional[FrameworkConfig]:
        """Get framework configuration"""
        return self._framework_config


# Async helper function for easy usage
@log_async_function(log_timing=True)
async def get_config_manager(config_dir: Optional[Path] = None) -> AsyncConfigManager:
    """
    Get async config manager instance.

    Usage:
        config = await get_config_manager()
        project_config = config.get_project_config("my_project")
    """
    return await AsyncConfigManager.get_instance(config_dir)
