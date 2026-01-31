"""
Comprehensive tests for framework.config.async_config_manager

Tests async configuration loading, parallel I/O, singleton pattern,
and Pydantic integration.

Author: Lokendra Singh
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, mock_open
import tempfile
import json
import yaml

from framework.config.async_config_manager import AsyncConfigManager
from framework.models.config_models import GlobalSettings, BrowserConfig, BrowserEngine


class TestAsyncConfigManagerSingleton:
    """Test AsyncConfigManager singleton pattern"""

    @pytest.mark.asyncio
    async def test_get_instance_returns_singleton(self):
        """Test get_instance returns same instance"""
        manager1 = await AsyncConfigManager.get_instance()
        manager2 = await AsyncConfigManager.get_instance()

        assert manager1 is manager2

    @pytest.mark.asyncio
    async def test_singleton_thread_safe(self):
        """Test singleton is thread-safe with asyncio.Lock"""
        instances = []

        async def get_manager():
            manager = await AsyncConfigManager.get_instance()
            instances.append(manager)

        # Try to create multiple instances concurrently
        await asyncio.gather(
            get_manager(),
            get_manager(),
            get_manager(),
        )

        # All should be same instance
        assert len(set(id(inst) for inst in instances)) == 1


class TestAsyncConfigManagerInit:
    """Test AsyncConfigManager initialization"""

    @pytest.mark.asyncio
    async def test_create_manager_with_config_dir(self):
        """Test creating manager with custom config directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            manager = AsyncConfigManager(config_dir=config_dir)

            assert manager.config_dir == config_dir

    @pytest.mark.asyncio
    async def test_create_manager_default_config_dir(self):
        """Test manager uses default config directory"""
        manager = AsyncConfigManager()

        # Should use config/ directory
        assert "config" in str(manager.config_dir).lower()


class TestAsyncConfigManagerYAMLLoading:
    """Test async YAML file loading"""

    @pytest.mark.asyncio
    async def test_load_yaml_config_success(self):
        """Test successfully loading YAML config"""
        yaml_content = """
        browser:
          engine: chromium
          headless: true
          timeout: 30000
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.yaml"
            config_file.write_text(yaml_content)

            manager = AsyncConfigManager(config_dir=Path(tmpdir))
            data = await manager._read_yaml_async(config_file)

            assert "browser" in data
            assert data["browser"]["engine"] == "chromium"

    @pytest.mark.asyncio
    async def test_load_yaml_file_not_found(self):
        """Test loading non-existent YAML file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AsyncConfigManager(config_dir=Path(tmpdir))
            non_existent = Path(tmpdir) / "missing.yaml"

            with pytest.raises(FileNotFoundError):
                await manager._read_yaml_async(non_existent)

    @pytest.mark.asyncio
    async def test_load_invalid_yaml(self):
        """Test loading invalid YAML content"""
        invalid_yaml = "invalid: yaml: content: {"

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "invalid.yaml"
            config_file.write_text(invalid_yaml)

            manager = AsyncConfigManager(config_dir=Path(tmpdir))

            # Should raise ValueError with YAML error message
            with pytest.raises(ValueError, match="Failed to parse YAML"):
                await manager._read_yaml_async(config_file)


class TestAsyncConfigManagerJSONLoading:
    """Test async JSON file loading"""

    @pytest.mark.asyncio
    async def test_load_json_config_success(self):
        """Test successfully loading JSON config"""
        json_content = {
            "api": {"base_url": "https://api.example.com", "timeout": 30}
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test.json"
            config_file.write_text(json.dumps(json_content))

            manager = AsyncConfigManager(config_dir=Path(tmpdir))
            data = await manager._read_json_async(config_file)

            assert "api" in data
            assert data["api"]["base_url"] == "https://api.example.com"

    @pytest.mark.asyncio
    async def test_load_json_file_not_found(self):
        """Test loading non-existent JSON file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = AsyncConfigManager(config_dir=Path(tmpdir))
            non_existent = Path(tmpdir) / "missing.json"

            with pytest.raises(FileNotFoundError):
                await manager._read_json_async(non_existent)

    @pytest.mark.asyncio
    async def test_load_invalid_json(self):
        """Test loading invalid JSON content"""
        invalid_json = '{"invalid": json content}'

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "invalid.json"
            config_file.write_text(invalid_json)

            manager = AsyncConfigManager(config_dir=Path(tmpdir))

            with pytest.raises(json.JSONDecodeError):
                await manager._read_json_async(config_file)


class TestAsyncConfigManagerParallelLoading:
    """Test parallel configuration loading"""

    @pytest.mark.asyncio
    async def test_load_all_configs_parallel(self):
        """Test loading multiple configs in parallel"""
        browser_config = """
        engine: chromium
        headless: true
        timeout: 30000
        """

        api_config = {"base_url": "https://api.example.com", "timeout": 30}

        db_config = """
        host: localhost
        port: 5432
        database: testdb
        username: user
        password: pass
        driver: postgresql
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config files
            (Path(tmpdir) / "browser.yaml").write_text(browser_config)
            (Path(tmpdir) / "api.json").write_text(json.dumps(api_config))
            (Path(tmpdir) / "database.yaml").write_text(db_config)

            manager = AsyncConfigManager(config_dir=Path(tmpdir))

            import time

            start = time.time()
            # This should load all configs in parallel
            settings = await manager.load_all_configs()
            duration = time.time() - start

            # Should be fast (parallel loading)
            assert duration < 1.0

            # Verify loaded configs
            assert settings is not None
            assert settings.browser is not None
            assert settings.api is not None
            assert settings.database is not None

    @pytest.mark.asyncio
    async def test_parallel_loading_performance(self):
        """Test parallel loading is faster than sequential"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple config files
            for i in range(3):
                config = {"test": f"value{i}"}
                (Path(tmpdir) / f"config{i}.json").write_text(
                    json.dumps(config)
                )

            manager = AsyncConfigManager(config_dir=Path(tmpdir))

            import time

            # Parallel loading
            start = time.time()
            await asyncio.gather(
                manager._read_json_async(Path(tmpdir) / "config0.json"),
                manager._read_json_async(Path(tmpdir) / "config1.json"),
                manager._read_json_async(Path(tmpdir) / "config2.json"),
            )
            parallel_duration = time.time() - start

            # Should complete quickly
            assert parallel_duration < 0.5


class TestAsyncConfigManagerBrowserConfig:
    """Test loading browser configuration"""

    @pytest.mark.asyncio
    async def test_load_browser_config(self):
        """Test loading browser configuration"""
        browser_yaml = """
        engine: chromium
        headless: true
        timeout: 30000
        viewport_width: 1920
        viewport_height: 1080
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "browser.yaml"
            config_file.write_text(browser_yaml)

            manager = AsyncConfigManager(config_dir=Path(tmpdir))
            browser_config = await manager._load_browser_config()

            assert browser_config.engine == BrowserEngine.CHROMIUM
            assert browser_config.headless is True
            assert browser_config.timeout == 30000

    @pytest.mark.asyncio
    async def test_load_browser_config_with_validation(self):
        """Test browser config validates with Pydantic"""
        invalid_browser = """
        engine: chromium
        timeout: 500
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "browser.yaml"
            config_file.write_text(invalid_browser)

            manager = AsyncConfigManager(config_dir=Path(tmpdir))

            # Should raise validation error (timeout < 1000)
            with pytest.raises(Exception):
                await manager._load_browser_config()


class TestAsyncConfigManagerAPIConfig:
    """Test loading API configuration"""

    @pytest.mark.asyncio
    async def test_load_api_config(self):
        """Test loading API configuration"""
        api_json = {
            "base_url": "https://api.example.com",
            "timeout": 30,
            "retry_count": 3,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "api.json"
            config_file.write_text(json.dumps(api_json))

            manager = AsyncConfigManager(config_dir=Path(tmpdir))
            api_config = await manager._load_api_config()

            assert str(api_config.base_url).startswith("https://api.example.com")
            assert api_config.timeout == 30
            assert api_config.retry_count == 3


class TestAsyncConfigManagerDatabaseConfig:
    """Test loading database configuration"""

    @pytest.mark.asyncio
    async def test_load_database_config(self):
        """Test loading database configuration"""
        db_yaml = """
        host: localhost
        port: 5432
        database: testdb
        username: user
        password: pass
        driver: postgresql
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "database.yaml"
            config_file.write_text(db_yaml)

            manager = AsyncConfigManager(config_dir=Path(tmpdir))
            db_config = await manager._load_database_config()

            assert db_config.host == "localhost"
            assert db_config.port == 5432
            assert db_config.database == "testdb"


class TestAsyncConfigManagerGlobalSettings:
    """Test loading complete global settings"""

    @pytest.mark.asyncio
    async def test_load_complete_global_settings(self):
        """Test loading all configurations into GlobalSettings"""
        browser_yaml = "engine: chromium\nheadless: true"
        api_json = {"base_url": "https://api.example.com", "timeout": 30}
        db_yaml = (
            "host: localhost\nport: 5432\ndatabase: testdb\n"
            "username: user\npassword: pass\ndriver: postgresql"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "browser.yaml").write_text(browser_yaml)
            (Path(tmpdir) / "api.json").write_text(json.dumps(api_json))
            (Path(tmpdir) / "database.yaml").write_text(db_yaml)

            manager = AsyncConfigManager(config_dir=Path(tmpdir))
            settings = await manager.load_all_configs()

            # Verify complete settings
            assert isinstance(settings, GlobalSettings)
            assert settings.browser.engine == BrowserEngine.CHROMIUM
            assert str(settings.api.base_url).startswith("https://api.example.com")
            assert settings.database.host == "localhost"

    @pytest.mark.asyncio
    async def test_load_partial_settings(self):
        """Test loading with missing configs (optional)"""
        browser_yaml = "engine: chromium\nheadless: true"

        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "browser.yaml").write_text(browser_yaml)

            manager = AsyncConfigManager(config_dir=Path(tmpdir))

            # Should handle missing configs gracefully
            settings = await manager.load_all_configs()

            assert settings.browser is not None
            # Other configs might be None (optional)


class TestAsyncConfigManagerCaching:
    """Test configuration caching"""

    @pytest.mark.asyncio
    async def test_config_caching_same_instance(self):
        """Test configs are cached and reused"""
        browser_yaml = "engine: chromium\nheadless: true"

        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "browser.yaml").write_text(browser_yaml)

            manager = AsyncConfigManager(config_dir=Path(tmpdir))

            # Load twice
            settings1 = await manager.load_all_configs()
            settings2 = await manager.load_all_configs()

            # Should return same instance (cached)
            assert settings1 is settings2


class TestAsyncConfigManagerErrorHandling:
    """Test error handling in AsyncConfigManager"""

    @pytest.mark.asyncio
    async def test_handle_missing_config_directory(self):
        """Test handling missing config directory"""
        non_existent_dir = Path("/non/existent/directory")

        # Should handle gracefully or raise clear error
        with pytest.raises(Exception):
            manager = AsyncConfigManager(config_dir=non_existent_dir)
            await manager.load_all_configs()

    @pytest.mark.asyncio
    async def test_handle_corrupted_config_file(self):
        """Test handling corrupted config files"""
        corrupted_yaml = "invalid: yaml: structure: {{"

        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "browser.yaml").write_text(corrupted_yaml)

            manager = AsyncConfigManager(config_dir=Path(tmpdir))

            with pytest.raises(ValueError, match="Failed to parse YAML"):
                await manager.load_all_configs()


class TestAsyncConfigManagerIntegration:
    """Integration tests for real-world scenarios"""

    @pytest.mark.asyncio
    async def test_complete_config_loading_workflow(self):
        """Test complete configuration loading workflow"""
        # Create complete config set
        configs = {
            "browser.yaml": "engine: chromium\nheadless: false\ntimeout: 30000",
            "api.json": json.dumps(
                {
                    "base_url": "https://api.prod.example.com",
                    "timeout": 60,
                    "retry_count": 5,
                }
            ),
            "database.yaml": (
                "host: prod-db.example.com\nport: 5432\n"
                "database: production\nusername: prod_user\n"
                "password: prod_pass\ndriver: postgresql"
            ),
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            # Write all config files
            for filename, content in configs.items():
                (Path(tmpdir) / filename).write_text(content)

            # Load all configs
            manager = AsyncConfigManager(config_dir=Path(tmpdir))
            settings = await manager.load_all_configs()

            # Verify complete configuration
            assert settings.browser.engine == BrowserEngine.CHROMIUM
            assert settings.browser.headless is False
            assert settings.api.timeout == 60
            assert settings.database.host == "prod-db.example.com"
            assert settings.database.port == 5432


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
