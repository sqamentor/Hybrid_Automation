"""
Plugin System Package

Extensible plugin architecture for framework customization.
"""

from framework.plugins.plugin_system import (
    IPlugin,
    BasePlugin,
    PluginManager,
    PluginMetadata,
    PluginStatus,
    PluginPriority,
    PluginHook,
    get_plugin_manager,
)

__all__ = [
    "IPlugin",
    "BasePlugin",
    "PluginManager",
    "PluginMetadata",
    "PluginStatus",
    "PluginPriority",
    "PluginHook",
    "get_plugin_manager",
]
