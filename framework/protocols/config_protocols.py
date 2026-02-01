"""
Configuration Protocol Interfaces

Protocol classes for configuration and environment management.
"""

from typing import Any, Dict, Optional, Protocol, runtime_checkable

from framework.models.config_models import (
    EnvironmentConfig,
    FrameworkConfig,
    ProjectConfig,
)


@runtime_checkable
class ConfigProvider(Protocol):
    """Protocol for configuration providers"""
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        ...
    
    def get_project_config(self, project_name: str) -> Optional[ProjectConfig]:
        """Get project configuration"""
        ...
    
    def get_environment_config(
        self,
        project_name: str,
        env_name: Optional[str] = None
    ) -> Optional[EnvironmentConfig]:
        """Get environment configuration"""
        ...
    
    def reload_config(self) -> None:
        """Reload configuration from sources"""
        ...
    
    def validate_config(self) -> bool:
        """Validate configuration integrity"""
        ...


@runtime_checkable
class EnvironmentProvider(Protocol):
    """Protocol for environment variable management"""
    
    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable"""
        ...
    
    def set_env(self, key: str, value: str) -> None:
        """Set environment variable"""
        ...
    
    def get_current_environment(self) -> str:
        """Get current test environment name"""
        ...
    
    def switch_environment(self, env_name: str) -> None:
        """Switch to different environment"""
        ...
    
    def get_all_environments(self) -> Dict[str, Any]:
        """Get all available environments"""
        ...


@runtime_checkable
class SecretProvider(Protocol):
    """Protocol for secure secret management"""
    
    def get_secret(self, key: str) -> Optional[str]:
        """Get secret value by key"""
        ...
    
    def set_secret(self, key: str, value: str) -> None:
        """Set secret value"""
        ...
    
    def delete_secret(self, key: str) -> None:
        """Delete secret"""
        ...
    
    def has_secret(self, key: str) -> bool:
        """Check if secret exists"""
        ...
    
    def list_secret_keys(self) -> list[str]:
        """List all secret keys (not values)"""
        ...
