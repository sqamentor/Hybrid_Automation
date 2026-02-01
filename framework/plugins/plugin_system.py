"""
Plugin System Architecture

Extensible plugin system for framework extensibility and customization.
Supports dynamic plugin loading, lifecycle management, and dependency resolution.
"""

from __future__ import annotations

import asyncio
import importlib.util
import inspect
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type


class PluginStatus(str, Enum):
    """Plugin lifecycle status"""
    UNLOADED = "unloaded"
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


class PluginPriority(int, Enum):
    """Plugin execution priority"""
    LOWEST = 0
    LOW = 25
    NORMAL = 50
    HIGH = 75
    HIGHEST = 100


# Plugin Exceptions
class PluginError(Exception):
    """Base exception for plugin errors"""
    pass


class PluginLoadError(PluginError):
    """Error loading plugin"""
    pass


class PluginDependencyError(PluginError):
    """Error with plugin dependencies"""
    pass


@dataclass
class PluginMetadata:
    """Plugin metadata"""
    name: str
    version: str
    author: str
    description: str
    priority: PluginPriority = PluginPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PluginHookData:
    """Plugin hook point data"""
    name: str
    description: str
    callback: Callable
    priority: PluginPriority = PluginPriority.NORMAL
    plugin_name: str = ""


def PluginHook(name: str, priority: int = 100, description: str = ""):
    """
    Decorator to mark a function as a plugin hook.
    
    Args:
        name: Hook name
        priority: Hook priority (default 100)
        description: Hook description
    """
    def decorator(func):
        func._hook_name = name
        func._hook_priority = priority
        func._hook_description = description
        return func
    return decorator


class IPlugin(ABC):
    """
    Plugin interface that all plugins must implement.
    
    Plugins extend framework functionality without modifying core code.
    """
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata"""
        pass
    
    @abstractmethod
    def on_load(self) -> None:
        """Called when plugin is loaded"""
        pass
    
    @abstractmethod
    def on_enable(self) -> None:
        """Called when plugin is enabled"""
        pass
    
    @abstractmethod
    def on_disable(self) -> None:
        """Called when plugin is disabled"""
        pass
    
    @abstractmethod
    def on_unload(self) -> None:
        """Called when plugin is unloaded"""
        pass


class BasePlugin(IPlugin):
    """
    Base plugin implementation with common functionality.
    
    Subclass this for easier plugin development.
    """
    
    def __init__(self, metadata: PluginMetadata, config: Optional[Dict[str, Any]] = None):
        self._metadata = metadata
        self._status = PluginStatus.UNLOADED
        self._hooks: List[PluginHookData] = []
        self._config: Dict[str, Any] = config or {}
    
    @property
    def status(self) -> PluginStatus:
        """Get plugin status"""
        return self._status
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata"""
        return self._metadata
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get plugin configuration"""
        return self._config
    
    def on_load(self) -> None:
        """Default load implementation"""
        self._status = PluginStatus.LOADED
        # Call child class load() if it exists
        if hasattr(self, 'load') and callable(getattr(self, 'load')):
            self.load()
    
    def on_enable(self) -> None:
        """Default enable implementation"""
        self._status = PluginStatus.ENABLED
    
    def on_disable(self) -> None:
        """Default disable implementation"""
        self._status = PluginStatus.DISABLED
    
    def on_unload(self) -> None:
        """Default unload implementation"""
        self._status = PluginStatus.UNLOADED
        # Call child class unload() if it exists
        if hasattr(self, 'unload') and callable(getattr(self, 'unload')):
            self.unload()
    
    def register_hook(
        self,
        hook_name: str,
        callback: Callable,
        description: str = "",
        priority: PluginPriority = PluginPriority.NORMAL
    ) -> None:
        """Register a hook point"""
        hook = PluginHookData(
            name=hook_name,
            description=description,
            callback=callback,
            priority=priority,
            plugin_name=self.metadata.name
        )
        self._hooks.append(hook)
    
    def get_hooks(self) -> List[PluginHookData]:
        """Get all registered hooks"""
        return self._hooks


class PluginManager:
    """
    Plugin manager for loading, managing, and executing plugins.
    
    Features:
    - Dynamic plugin loading from directory
    - Dependency resolution
    - Priority-based execution
    - Hook system for extension points
    """
    
    def __init__(self, plugin_dir: Optional[Path] = None):
        self._plugins: Dict[str, IPlugin] = {}
        self._plugin_dir = plugin_dir or Path.cwd() / "plugins"
        self._hooks: Dict[str, List[PluginHookData]] = {}
        self._execution_order: List[str] = []
    
    def discover_plugins(self, directory: Optional[str] = None) -> List[Path]:
        """
        Discover plugin files in plugin directory.
        
        Args:
            directory: Optional directory to search for plugins
        
        Returns:
            List of plugin file paths
        """
        plugin_dir = Path(directory) if directory else self._plugin_dir
        
        if not plugin_dir.exists():
            return []
        
        plugin_files = []
        for file in plugin_dir.glob("*.py"):
            if file.name != "__init__.py":
                plugin_files.append(file)
        
        return plugin_files
    
    def load_plugin(self, plugin_path: Path) -> Optional[IPlugin]:
        """
        Load plugin from file.
        
        Args:
            plugin_path: Path to plugin file
        
        Returns:
            Loaded plugin instance or None if failed
        """
        try:
            # Load module dynamically
            spec = importlib.util.spec_from_file_location(
                plugin_path.stem,
                plugin_path
            )
            if not spec or not spec.loader:
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_path.stem] = module
            spec.loader.exec_module(module)
            
            # Find plugin class
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, IPlugin) and obj is not IPlugin and obj is not BasePlugin:
                    plugin = obj()
                    plugin.on_load()
                    self._plugins[plugin.metadata.name] = plugin
                    return plugin
            
        except Exception as e:
            print(f"Failed to load plugin from {plugin_path}: {e}")
        
        return None
    
    def load_all_plugins(self) -> int:
        """
        Load all plugins from plugin directory.
        
        Returns:
            Number of successfully loaded plugins
        """
        plugin_files = self.discover_plugins()
        loaded_count = 0
        
        for plugin_file in plugin_files:
            if self.load_plugin(plugin_file):
                loaded_count += 1
        
        # Resolve dependencies and determine execution order
        self._resolve_dependencies()
        
        return loaded_count
    
    def load_plugin_instance(self, plugin: IPlugin) -> None:
        """
        Load a plugin instance directly.
        
        Args:
            plugin: Plugin instance to load
        
        Raises:
            PluginError: If plugin with same name already loaded
            PluginDependencyError: If plugin dependencies are not met
            PluginLoadError: If plugin.load() raises an exception
        """
        # Check for duplicate plugin name
        if plugin.metadata.name in self._plugins:
            raise PluginError(f"Plugin '{plugin.metadata.name}' is already loaded")
        
        # Validate dependencies
        if plugin.metadata.dependencies:
            for dep_name in plugin.metadata.dependencies:
                if dep_name not in self._plugins:
                    raise PluginDependencyError(f"Missing dependency: {dep_name}")
        
        # Try to load plugin
        try:
            plugin.on_load()
        except Exception as e:
            raise PluginLoadError(f"Failed to load plugin '{plugin.metadata.name}': {e}") from e
        
        self._plugins[plugin.metadata.name] = plugin
        
        # Discover and register hooks from plugin methods
        if isinstance(plugin, BasePlugin):
            self._discover_plugin_hooks(plugin)
    
    def _discover_plugin_hooks(self, plugin: BasePlugin) -> None:
        """Discover hooks decorated with @PluginHook in plugin methods"""
        for attr_name in dir(plugin):
            attr = getattr(plugin, attr_name)
            if callable(attr) and hasattr(attr, '_hook_name'):
                # Create hook data from decorated method
                # Keep priority as raw value for consistent sorting
                hook_data = PluginHookData(
                    name=attr._hook_name,
                    description=getattr(attr, '_hook_description', ''),
                    callback=attr,
                    priority=attr._hook_priority,  # Use raw priority value
                    plugin_name=plugin.metadata.name
                )
                self.register_hook(hook_data)
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_name: Name of plugin to unload
        
        Returns:
            True if successful, False otherwise
        """
        plugin = self._plugins.get(plugin_name)
        if not plugin:
            return False
        
        # Call plugin's unload method
        plugin.on_unload()
        
        # Remove plugin from loaded plugins
        del self._plugins[plugin_name]
        
        # Remove plugin's hooks
        for hook_name in list(self._hooks.keys()):
            self._hooks[hook_name] = [
                h for h in self._hooks[hook_name]
                if h.plugin_name != plugin_name
            ]
        
        return True
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a loaded plugin.
        
        Args:
            plugin_name: Name of plugin to enable
        
        Returns:
            True if successful, False otherwise
        """
        plugin = self._plugins.get(plugin_name)
        if not plugin:
            return False
        
        try:
            plugin.on_enable()
            
            # Register plugin hooks
            if isinstance(plugin, BasePlugin):
                for hook in plugin.get_hooks():
                    self.register_hook(hook)
            
            return True
        except Exception as e:
            print(f"Failed to enable plugin {plugin_name}: {e}")
            return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable an enabled plugin.
        
        Args:
            plugin_name: Name of plugin to disable
        
        Returns:
            True if successful, False otherwise
        """
        plugin = self._plugins.get(plugin_name)
        if not plugin:
            return False
        
        try:
            plugin.on_disable()
            
            # Unregister plugin hooks
            for hook_name, hooks in self._hooks.items():
                self._hooks[hook_name] = [
                    h for h in hooks if h.plugin_name != plugin_name
                ]
            
            return True
        except Exception as e:
            print(f"Failed to disable plugin {plugin_name}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_name: Name of plugin to unload
        
        Returns:
            True if successful, False otherwise
        """
        plugin = self._plugins.get(plugin_name)
        if not plugin:
            return False
        
        try:
            # Disable first if enabled
            if plugin.status == PluginStatus.ENABLED:
                self.disable_plugin(plugin_name)
            
            plugin.on_unload()
            del self._plugins[plugin_name]
            return True
        except Exception as e:
            print(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def register_hook(self, hook: PluginHookData) -> None:
        """Register a hook point"""
        if hook.name not in self._hooks:
            self._hooks[hook.name] = []
        self._hooks[hook.name].append(hook)
        
        # Sort hooks by priority (highest first)
        self._hooks[hook.name].sort(key=lambda h: h.priority.value if isinstance(h.priority, PluginPriority) else h.priority, reverse=True)
    
    async def execute_hooks(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Execute all registered hooks for a hook point.
        Hooks are executed in priority order (lower value = higher priority).
        
        Args:
            hook_name: Name of hook point
            *args, **kwargs: Arguments to pass to hook callbacks
        
        Returns:
            List of results from each hook callback
        """
        hooks = self._hooks.get(hook_name, [])
        
        # Sort hooks by priority (lower value = higher priority = execute first)
        # Convert enum to int for consistent sorting
        def get_priority_value(h):
            if isinstance(h.priority, PluginPriority):
                return int(h.priority.value)
            return int(h.priority)
        
        hooks = sorted(hooks, key=get_priority_value)
        
        results = []
        
        for hook in hooks:
            try:
                if asyncio.iscoroutinefunction(hook.callback):
                    result = await hook.callback(*args, **kwargs)
                else:
                    result = hook.callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"Error executing hook {hook_name} from plugin {hook.plugin_name}: {e}")
        
        return results
    
    async def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Alias for execute_hooks"""
        return await self.execute_hooks(hook_name, *args, **kwargs)
    
    def get_plugin(self, plugin_name: str) -> Optional[IPlugin]:
        """Get plugin by name"""
        return self._plugins.get(plugin_name)
    
    def get_all_plugins(self) -> List[IPlugin]:
        """Get all loaded plugins"""
        return list(self._plugins.values())
    
    def get_loaded_plugins(self) -> List[IPlugin]:
        """Alias for get_all_plugins"""
        return self.get_all_plugins()
    
    def get_enabled_plugins(self) -> List[IPlugin]:
        """Get all enabled plugins"""
        return [
            plugin for plugin in self._plugins.values()
            if plugin.status == PluginStatus.ENABLED
        ]
    
    def _resolve_dependencies(self) -> None:
        """Resolve plugin dependencies and determine execution order"""
        # Simple topological sort for dependency resolution
        visited = set()
        order = []
        
        def visit(plugin_name: str):
            if plugin_name in visited:
                return
            
            plugin = self._plugins.get(plugin_name)
            if not plugin:
                return
            
            visited.add(plugin_name)
            
            # Visit dependencies first
            for dep in plugin.metadata.dependencies:
                if dep in self._plugins:
                    visit(dep)
            
            order.append(plugin_name)
        
        for plugin_name in self._plugins:
            visit(plugin_name)
        
        self._execution_order = order


# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager(plugin_dir: Optional[Path] = None) -> PluginManager:
    """Get global plugin manager instance"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager(plugin_dir)
    return _plugin_manager
