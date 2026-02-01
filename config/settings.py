"""Framework Settings and Configuration Manager.

This module provides centralized configuration management for the entire framework. It loads
environment-specific settings and provides a singleton interface.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import yaml  # type: ignore[import-untyped]
from dataclasses import dataclass


class SettingsManager:
    """Singleton configuration manager."""
    
    _instance = None
    _config: Dict[str, Any] = {}
    _environment: str = "dev"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_configuration()
        return cls._instance
    
    def _load_configuration(self):
        """Load all configuration files."""
        config_dir = Path(__file__).parent
        
        # Load environments.yaml
        env_file = config_dir / "environments.yaml"
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_data = yaml.safe_load(f)
                # Extract the 'environments' key if it exists, otherwise use the whole structure
                self._config['environments'] = env_data.get('environments', env_data) if isinstance(env_data, dict) else {}
        
        # Load engine_decision_matrix.yaml
        matrix_file = config_dir / "engine_decision_matrix.yaml"
        if matrix_file.exists():
            with open(matrix_file, 'r') as f:
                self._config['engine_matrix'] = yaml.safe_load(f)
        
        # Load api_db_mapping.yaml
        mapping_file = config_dir / "api_db_mapping.yaml"
        if mapping_file.exists():
            with open(mapping_file, 'r') as f:
                self._config['api_db_mapping'] = yaml.safe_load(f)
        
        # Load projects.yaml
        projects_file = config_dir / "projects.yaml"
        if projects_file.exists():
            with open(projects_file, 'r') as f:
                self._config['projects'] = yaml.safe_load(f)
        
        # Set environment from environment variable or default to 'dev'
        self._environment = os.getenv('TEST_ENV', 'dev')

    @staticmethod
    def _ensure_dict(value: Any) -> Dict[str, Any]:
        """Ensure value is a dictionary for type-safe access."""
        return value if isinstance(value, dict) else {}
    
    def get_environment_config(self, env: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for a specific environment."""
        env = env or self._environment
        environments = self._ensure_dict(self._config.get('environments', {}))
        return self._ensure_dict(environments.get(env, {}))
    
    def get_engine_decision_matrix(self) -> Dict[str, Any]:
        """Get engine selection decision matrix."""
        return self._ensure_dict(self._config.get('engine_matrix', {}))
    
    def get_api_db_mapping(self) -> Dict[str, Any]:
        """Get API to database mapping registry."""
        return self._ensure_dict(self._config.get('api_db_mapping', {}))
    
    def get_projects_config(self) -> Dict[str, Any]:
        """Get projects configuration from projects.yaml."""
        projects = self._ensure_dict(self._config.get('projects', {}))
        return self._ensure_dict(projects.get('projects', {}))
    
    def get_project_config(self, project_name: str, env: Optional[str] = None) -> Dict[str, Any]:
        """Get specific project configuration for given environment."""
        env = env or self._environment
        projects = self.get_projects_config()
        project = self._ensure_dict(projects.get(project_name, {}))
        environments = self._ensure_dict(project.get('environments', {}))
        return self._ensure_dict(environments.get(env, {}))
    
    def get_global_config(self) -> Dict[str, Any]:
        """Get global configuration."""
        environments = self._ensure_dict(self._config.get('environments', {}))
        return self._ensure_dict(environments.get('global', {}))
    
    @property
    def current_environment(self) -> str:
        """Get current environment name."""
        return self._environment
    
    @current_environment.setter
    def current_environment(self, env: str) -> None:
        """Set current environment."""
        environments = self._ensure_dict(self._config.get('environments', {}))
        if env in environments:
            self._environment = env
        else:
            raise ValueError(f"Unknown environment: {env}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        Example: settings.get('dev.database.primary.host')
        """
        keys = key_path.split('.')
        value: Any = self._config
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            
            if value is None:
                return default
        
        return value


# ========================================================================
# CONFIGURATION DATACLASSES
# ========================================================================

@dataclass
class BrowserConfig:
    """Browser configuration."""
    headless: bool = True
    slow_mo: int = 0
    video: bool = False
    tracing: bool = False
    timeout: int = 30000


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str
    port: int
    name: str
    type: str
    username: str
    password: str
    read_only: bool = True


@dataclass
class TimeoutConfig:
    """Timeout configuration."""
    page_load: int = 30000
    element_wait: int = 10000
    api_response: int = 15000
    database_query: int = 10000


@dataclass
class RetryConfig:
    """Retry configuration."""
    max_attempts: int = 2
    delay_ms: int = 1000


# ========================================================================
# SINGLETON INSTANCE
# ========================================================================

# Global settings instance
settings = SettingsManager()


# ========================================================================
# HELPER FUNCTIONS
# ========================================================================

def get_ui_url(env: Optional[str] = None) -> str:
    """Get UI base URL for environment."""
    config = settings.get_environment_config(env)
    return cast(str, config.get('ui_url', ''))


def get_api_url(env: Optional[str] = None) -> str:
    """Get API base URL for environment."""
    config = settings.get_environment_config(env)
    return cast(str, config.get('api_base_url', ''))


def get_database_config(env: Optional[str] = None, db_name: str = 'primary') -> DatabaseConfig:
    """Get database configuration."""
    config = settings.get_environment_config(env)
    database_group = settings._ensure_dict(config.get('database', {}))
    db_config = settings._ensure_dict(database_group.get(db_name, {}))
    
    # Replace environment variables in password
    password = db_config.get('password', '')
    if password.startswith('${') and password.endswith('}'):
        env_var = password[2:-1]
        password = os.getenv(env_var, '')
    
    return DatabaseConfig(
        host=db_config.get('host', ''),
        port=db_config.get('port', 1433),
        name=db_config.get('name', ''),
        type=db_config.get('type', 'sql_server'),
        username=db_config.get('username', ''),
        password=password,
        read_only=db_config.get('read_only', True)
    )


def get_test_user(role: str = 'standard_user', env: Optional[str] = None) -> Dict[str, str]:
    """Get test user credentials."""
    config = settings.get_environment_config(env)
    test_users = settings._ensure_dict(config.get('test_users', {}))
    return cast(Dict[str, str], settings._ensure_dict(test_users.get(role, {})))


def get_browser_config(env: Optional[str] = None) -> BrowserConfig:
    """Get browser configuration."""
    config = settings.get_environment_config(env)
    browser_cfg = settings._ensure_dict(config.get('browser', {}))
    
    return BrowserConfig(
        headless=browser_cfg.get('headless', True),
        slow_mo=browser_cfg.get('slow_mo', 0),
        video=browser_cfg.get('video', False),
        tracing=browser_cfg.get('tracing', False),
        timeout=config.get('timeouts', {}).get('page_load', 30000)
    )


def get_timeout_config(env: Optional[str] = None) -> TimeoutConfig:
    """Get timeout configuration."""
    config = settings.get_environment_config(env)
    timeouts = settings._ensure_dict(config.get('timeouts', {}))
    
    return TimeoutConfig(
        page_load=timeouts.get('page_load', 30000),
        element_wait=timeouts.get('element_wait', 10000),
        api_response=timeouts.get('api_response', 15000),
        database_query=timeouts.get('database_query', 10000)
    )


def is_ai_enabled() -> bool:
    """Check if AI engine selector is enabled."""
    global_config = settings.get_global_config()
    ai_engine = settings._ensure_dict(global_config.get('ai_engine', {}))
    return bool(ai_engine.get('enabled', False))


def is_cloud_grid_enabled() -> bool:
    """Check if cloud grid execution is enabled."""
    global_config = settings.get_global_config()
    cloud_grid = settings._ensure_dict(global_config.get('cloud_grid', {}))
    return bool(cloud_grid.get('enabled', False))


def get_execution_mode() -> str:
    """Get execution flow mode (ui_only, ui_api, ui_api_db)"""
    global_config = settings.get_global_config()
    flow_config = settings._ensure_dict(global_config.get('execution_flow', {}))
    return cast(str, flow_config.get('mode', 'ui_api_db'))


def get_enabled_components() -> List[str]:
    """Get list of enabled execution components.

    Returns:
        List of enabled components: ['ui'], ['ui', 'api'], or ['ui', 'api', 'database']
    """
    global_config = settings.get_global_config()
    flow_config = global_config.get('execution_flow', {})
    
    # Check if mode is set
    mode = flow_config.get('mode', 'ui_api_db')
    
    if mode == 'ui_only':
        return ['ui']
    elif mode == 'ui_api':
        return ['ui', 'api']
    elif mode == 'ui_api_db':
        return ['ui', 'api', 'database']
    else:
        # Fallback to component flags
        components = flow_config.get('components', {})
        enabled = ['ui']  # UI always enabled
        if components.get('api', True):
            enabled.append('api')
        if components.get('database', True):
            enabled.append('database')
        return enabled


def should_run_api_validation() -> bool:
    """Check if API validation is enabled."""
    return 'api' in get_enabled_components()


def should_run_db_validation() -> bool:
    """Check if database validation is enabled."""
    return 'database' in get_enabled_components()


def should_skip_component(component: str) -> bool:
    """Check if a component should be skipped.

    Args:
        component: Component name ('api' or 'database')

    Returns:
        True if component should be skipped
    """
    return component not in get_enabled_components()


# ========================================================================
# ENVIRONMENT VARIABLE HELPERS
# ========================================================================

def expand_env_vars(value: Any) -> Any:
    """Expand environment variables in format ${VAR_NAME}

    Args:
        value: String potentially containing ${VAR_NAME} patterns

    Returns:
        String with environment variables expanded
    """
    if not isinstance(value, str):
        return value
    
    if value.startswith('${') and value.endswith('}'):
        env_var = value[2:-1]
        return os.getenv(env_var, value)
    
    return value


# ========================================================================
# EXPORT
# ========================================================================

__all__ = [
    'settings',
    'SettingsManager',
    'BrowserConfig',
    'DatabaseConfig',
    'TimeoutConfig',
    'RetryConfig',
    'get_ui_url',
    'get_api_url',
    'get_database_config',
    'get_test_user',
    'get_browser_config',
    'get_timeout_config',
    'is_ai_enabled',
    'is_cloud_grid_enabled',
    'get_execution_mode',
    'get_enabled_components',
    'should_run_api_validation',
    'should_run_db_validation',
    'should_skip_component',
    'expand_env_vars'
]
