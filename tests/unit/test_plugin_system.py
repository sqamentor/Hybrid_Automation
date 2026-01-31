"""
Unit tests for framework.plugins.plugin_system module.

Tests plugin loading, hooks, dependency resolution, and plugin lifecycle.
"""
import pytest
from typing import Dict, Any, List
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

from framework.plugins.plugin_system import (
    BasePlugin,
    PluginManager,
    PluginMetadata,
    PluginHook,
    PluginError,
    PluginLoadError,
    PluginDependencyError
)


# ============================================================================
# Test PluginMetadata
# ============================================================================

class TestPluginMetadata:
    """Test PluginMetadata dataclass."""
    
    def test_metadata_creation(self):
        """Test creating plugin metadata."""
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test Author",
            description="A test plugin"
        )
        
        assert metadata.name == "test-plugin"
        assert metadata.version == "1.0.0"
        assert metadata.author == "Test Author"
        assert metadata.description == "A test plugin"
        assert metadata.dependencies == []
    
    def test_metadata_with_dependencies(self):
        """Test metadata with dependencies."""
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test Author",
            description="Test",
            dependencies=["plugin-a", "plugin-b"]
        )
        
        assert len(metadata.dependencies) == 2
        assert "plugin-a" in metadata.dependencies
        assert "plugin-b" in metadata.dependencies


# ============================================================================
# Test PluginHook
# ============================================================================

class TestPluginHook:
    """Test PluginHook decorator and functionality."""
    
    def test_hook_decorator(self):
        """Test hook decorator adds metadata."""
        
        @PluginHook(name="test_hook", priority=10)
        def test_function():
            pass
        
        assert hasattr(test_function, '_hook_name')
        assert hasattr(test_function, '_hook_priority')
        assert test_function._hook_name == "test_hook"
        assert test_function._hook_priority == 10
    
    def test_hook_default_priority(self):
        """Test hook with default priority."""
        
        @PluginHook(name="test_hook")
        def test_function():
            pass
        
        assert test_function._hook_priority == 100  # Default
    
    def test_hook_on_method(self):
        """Test hook decorator on class methods."""
        
        class TestPlugin(BasePlugin):
            def __init__(self):
                super().__init__(PluginMetadata(
                    name="test",
                    version="1.0.0",
                    author="Test",
                    description="Test"
                ))
            
            @PluginHook(name="before_test", priority=50)
            async def my_hook(self, test_name: str):
                return f"Hook executed for {test_name}"
            
            def load(self):
                pass
            
            def unload(self):
                pass
        
        plugin = TestPlugin()
        assert hasattr(plugin.my_hook, '_hook_name')
        assert plugin.my_hook._hook_name == "before_test"
        assert plugin.my_hook._hook_priority == 50


# ============================================================================
# Test BasePlugin
# ============================================================================

class TestBasePlugin:
    """Test BasePlugin abstract base class."""
    
    def test_plugin_creation(self):
        """Test creating a plugin with metadata."""
        
        class TestPlugin(BasePlugin):
            def load(self):
                self.loaded = True
            
            def unload(self):
                self.loaded = False
        
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test plugin"
        )
        
        plugin = TestPlugin(metadata)
        assert plugin.metadata == metadata
        assert plugin.config == {}
    
    def test_plugin_with_config(self):
        """Test plugin with configuration."""
        
        class TestPlugin(BasePlugin):
            def load(self):
                pass
            
            def unload(self):
                pass
        
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test"
        )
        
        config = {"api_key": "secret", "enabled": True}
        plugin = TestPlugin(metadata, config)
        
        assert plugin.config == config
        assert plugin.config["api_key"] == "secret"
    
    def test_plugin_load_unload(self):
        """Test plugin load and unload lifecycle."""
        
        class TestPlugin(BasePlugin):
            def __init__(self, metadata: PluginMetadata, config: Dict[str, Any] = None):
                super().__init__(metadata, config)
                self.is_loaded = False
            
            def load(self):
                self.is_loaded = True
            
            def unload(self):
                self.is_loaded = False
        
        metadata = PluginMetadata(
            name="test",
            version="1.0.0",
            author="Test",
            description="Test"
        )
        
        plugin = TestPlugin(metadata)
        assert plugin.is_loaded is False
        
        plugin.load()
        assert plugin.is_loaded is True
        
        plugin.unload()
        assert plugin.is_loaded is False


# ============================================================================
# Test PluginManager
# ============================================================================

class TestPluginManager:
    """Test PluginManager for plugin lifecycle and execution."""
    
    def test_manager_creation(self):
        """Test creating a plugin manager."""
        manager = PluginManager()
        assert len(manager.get_loaded_plugins()) == 0
    
    def test_load_plugin_instance(self):
        """Test loading a plugin instance."""
        
        class TestPlugin(BasePlugin):
            def load(self):
                self.loaded = True
            
            def unload(self):
                self.loaded = False
        
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test"
        )
        
        manager = PluginManager()
        plugin = TestPlugin(metadata)
        
        manager.load_plugin_instance(plugin)
        
        loaded_plugins = manager.get_loaded_plugins()
        assert len(loaded_plugins) == 1
        assert loaded_plugins[0].metadata.name == "test-plugin"
    
    def test_unload_plugin(self):
        """Test unloading a plugin."""
        
        class TestPlugin(BasePlugin):
            def __init__(self, metadata: PluginMetadata):
                super().__init__(metadata)
                self.is_loaded = False
            
            def load(self):
                self.is_loaded = True
            
            def unload(self):
                self.is_loaded = False
        
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test"
        )
        
        manager = PluginManager()
        plugin = TestPlugin(metadata)
        
        manager.load_plugin_instance(plugin)
        assert len(manager.get_loaded_plugins()) == 1
        assert plugin.is_loaded is True
        
        manager.unload_plugin("test-plugin")
        assert len(manager.get_loaded_plugins()) == 0
        assert plugin.is_loaded is False
    
    @pytest.mark.asyncio
    async def test_execute_hook_no_plugins(self):
        """Test executing hook with no plugins."""
        manager = PluginManager()
        
        # Should not raise exception
        result = await manager.execute_hook("test_hook")
        assert result == []
    
    @pytest.mark.asyncio
    async def test_execute_hook_single_plugin(self):
        """Test executing hook with single plugin."""
        
        class TestPlugin(BasePlugin):
            def __init__(self, metadata: PluginMetadata):
                super().__init__(metadata)
                self.hook_called = False
            
            def load(self):
                pass
            
            def unload(self):
                pass
            
            @PluginHook(name="test_hook", priority=100)
            async def my_hook(self, test_name: str):
                self.hook_called = True
                return f"Processed {test_name}"
        
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test"
        )
        
        manager = PluginManager()
        plugin = TestPlugin(metadata)
        manager.load_plugin_instance(plugin)
        
        results = await manager.execute_hook("test_hook", test_name="test_case_1")
        
        assert plugin.hook_called is True
        assert len(results) == 1
        assert results[0] == "Processed test_case_1"
    
    @pytest.mark.asyncio
    async def test_execute_hook_multiple_plugins(self):
        """Test executing hook with multiple plugins."""
        
        class Plugin1(BasePlugin):
            def load(self):
                pass
            
            def unload(self):
                pass
            
            @PluginHook(name="test_hook", priority=10)
            async def hook1(self, value: int):
                return value + 1
        
        class Plugin2(BasePlugin):
            def load(self):
                pass
            
            def unload(self):
                pass
            
            @PluginHook(name="test_hook", priority=20)
            async def hook2(self, value: int):
                return value * 2
        
        manager = PluginManager()
        
        plugin1 = Plugin1(PluginMetadata("plugin1", "1.0.0", "Test", "Test"))
        plugin2 = Plugin2(PluginMetadata("plugin2", "1.0.0", "Test", "Test"))
        
        manager.load_plugin_instance(plugin1)
        manager.load_plugin_instance(plugin2)
        
        results = await manager.execute_hook("test_hook", value=10)
        
        # Plugins should execute in priority order (10, 20)
        assert len(results) == 2
        assert results[0] == 11  # plugin1: 10 + 1
        assert results[1] == 20  # plugin2: 10 * 2
    
    @pytest.mark.asyncio

    async def test_hook_priority_ordering(self):
        """Test hooks execute in priority order."""
        
        execution_order = []
        
        class HighPriorityPlugin(BasePlugin):
            def load(self):
                pass
            
            def unload(self):
                pass
            
            @PluginHook(name="test_hook", priority=1)
            async def hook(self):
                execution_order.append("high")
        
        class MediumPriorityPlugin(BasePlugin):
            def load(self):
                pass
            
            def unload(self):
                pass
            
            @PluginHook(name="test_hook", priority=50)
            async def hook(self):
                execution_order.append("medium")
        
        class LowPriorityPlugin(BasePlugin):
            def load(self):
                pass
            
            def unload(self):
                pass
            
            @PluginHook(name="test_hook", priority=100)
            async def hook(self):
                execution_order.append("low")
        
        manager = PluginManager()
        
        # Load in random order
        manager.load_plugin_instance(MediumPriorityPlugin(
            PluginMetadata("medium", "1.0.0", "Test", "Test")
        ))
        manager.load_plugin_instance(LowPriorityPlugin(
            PluginMetadata("low", "1.0.0", "Test", "Test")
        ))
        manager.load_plugin_instance(HighPriorityPlugin(
            PluginMetadata("high", "1.0.0", "Test", "Test")
        ))
        
        await manager.execute_hook("test_hook")
        
        # Should execute in priority order: 1(high), 50(medium), 100(low)
        assert execution_order == ["high", "medium", "low"]
    
    def test_get_plugin_by_name(self):
        """Test getting plugin by name."""
        
        class TestPlugin(BasePlugin):
            def load(self):
                pass
            
            def unload(self):
                pass
        
        metadata = PluginMetadata(
            name="my-plugin",
            version="1.0.0",
            author="Test",
            description="Test"
        )
        
        manager = PluginManager()
        plugin = TestPlugin(metadata)
        manager.load_plugin_instance(plugin)
        
        retrieved = manager.get_plugin("my-plugin")
        assert retrieved is plugin
    
    def test_get_nonexistent_plugin(self):
        """Test getting plugin that doesn't exist."""
        manager = PluginManager()
        
        result = manager.get_plugin("nonexistent")
        assert result is None


# ============================================================================
# Test Plugin Dependencies
# ============================================================================

class TestPluginDependencies:
    """Test plugin dependency resolution."""
    
    def test_load_with_dependencies(self):
        """Test loading plugins with dependencies."""
        
        class PluginA(BasePlugin):
            def load(self):
                self.loaded = True
            
            def unload(self):
                self.loaded = False
        
        class PluginB(BasePlugin):
            def load(self):
                self.loaded = True
            
            def unload(self):
                self.loaded = False
        
        metadata_a = PluginMetadata(
            name="plugin-a",
            version="1.0.0",
            author="Test",
            description="Test"
        )
        
        metadata_b = PluginMetadata(
            name="plugin-b",
            version="1.0.0",
            author="Test",
            description="Test",
            dependencies=["plugin-a"]
        )
        
        manager = PluginManager()
        
        plugin_a = PluginA(metadata_a)
        plugin_b = PluginB(metadata_b)
        
        # Load plugin-a first
        manager.load_plugin_instance(plugin_a)
        
        # Load plugin-b (depends on plugin-a)
        manager.load_plugin_instance(plugin_b)
        
        assert len(manager.get_loaded_plugins()) == 2
    
    def test_missing_dependency_error(self):
        """Test error when dependency is missing."""
        
        class PluginB(BasePlugin):
            def load(self):
                pass
            
            def unload(self):
                pass
        
        metadata_b = PluginMetadata(
            name="plugin-b",
            version="1.0.0",
            author="Test",
            description="Test",
            dependencies=["plugin-a"]  # Missing dependency
        )
        
        manager = PluginManager()
        plugin_b = PluginB(metadata_b)
        
        # Should raise PluginDependencyError
        with pytest.raises(PluginDependencyError, match="Missing dependency: plugin-a"):
            manager.load_plugin_instance(plugin_b)


# ============================================================================
# Test Plugin Discovery
# ============================================================================

class TestPluginDiscovery:
    """Test automatic plugin discovery."""
    
    @patch('pathlib.Path.glob')
    @patch('importlib.import_module')
    def test_discover_plugins_from_directory(self, mock_import, mock_glob):
        """Test discovering plugins from directory."""
        
        class TestPlugin(BasePlugin):
            def load(self):
                pass
            
            def unload(self):
                pass
        
        # Mock plugin files
        mock_glob.return_value = [
            Path("plugins/test_plugin.py"),
            Path("plugins/another_plugin.py")
        ]
        
        # Mock imported modules
        mock_module = MagicMock()
        mock_module.TestPlugin = TestPlugin
        mock_module.plugin_metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test"
        )
        mock_import.return_value = mock_module
        
        manager = PluginManager()
        discovered = manager.discover_plugins("plugins/")
        
        # discover_plugins returns list of file paths
        assert isinstance(discovered, list)


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestPluginErrors:
    """Test plugin error handling."""
    
    def test_plugin_load_error(self):
        """Test handling plugin load errors."""
        
        class FailingPlugin(BasePlugin):
            def load(self):
                raise RuntimeError("Failed to load")
            
            def unload(self):
                pass
        
        metadata = PluginMetadata(
            name="failing-plugin",
            version="1.0.0",
            author="Test",
            description="Test"
        )
        
        manager = PluginManager()
        plugin = FailingPlugin(metadata)
        
        with pytest.raises(PluginLoadError):
            manager.load_plugin_instance(plugin)
    
    @pytest.mark.asyncio
    async def test_hook_execution_error(self):
        """Test handling errors in hook execution."""
        
        class ErrorPlugin(BasePlugin):
            def load(self):
                pass
            
            def unload(self):
                pass
            
            @PluginHook(name="test_hook", priority=100)
            async def failing_hook(self):
                raise ValueError("Hook error")
        
        class WorkingPlugin(BasePlugin):
            def __init__(self, metadata: PluginMetadata):
                super().__init__(metadata)
                self.executed = False
            
            def load(self):
                pass
            
            def unload(self):
                pass
            
            @PluginHook(name="test_hook", priority=50)
            async def working_hook(self):
                self.executed = True
                return "success"
        
        manager = PluginManager()
        
        error_plugin = ErrorPlugin(PluginMetadata("error", "1.0.0", "Test", "Test"))
        working_plugin = WorkingPlugin(PluginMetadata("working", "1.0.0", "Test", "Test"))
        
        manager.load_plugin_instance(error_plugin)
        manager.load_plugin_instance(working_plugin)
        
        # Should not crash, working plugin should still execute
        results = await manager.execute_hook("test_hook")
        
        # Only working plugin should return result
        assert working_plugin.executed is True
        assert "success" in results
    
    def test_duplicate_plugin_name(self):
        """Test loading plugins with duplicate names."""
        
        class Plugin1(BasePlugin):
            def load(self):
                pass
            
            def unload(self):
                pass
        
        metadata = PluginMetadata(
            name="duplicate-name",
            version="1.0.0",
            author="Test",
            description="Test"
        )
        
        manager = PluginManager()
        
        plugin1 = Plugin1(metadata)
        plugin2 = Plugin1(metadata)
        
        manager.load_plugin_instance(plugin1)
        
        # Should raise error for duplicate name
        with pytest.raises(PluginError, match="already loaded"):
            manager.load_plugin_instance(plugin2)
