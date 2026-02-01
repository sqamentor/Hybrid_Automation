"""
Comprehensive tests for framework.core.modern_engine_selector

Tests pattern matching engine selection, decision matrix,
caching, and UI framework detection.

Author: Lokendra Singh
"""

import pytest
from unittest.mock import Mock, patch
from dataclasses import dataclass
from framework.core.modern_engine_selector import (
    ModernEngineSelector,
    TestMetadata,
    UIFramework,
    TestComplexity,
)
from framework.models.config_models import EngineType
from framework.protocols.config_protocols import ConfigProvider


@pytest.fixture
def mock_config_provider():
    """Create mock ConfigProvider"""
    provider = Mock(spec=ConfigProvider)
    provider.get_browser_config = Mock(return_value=Mock(engine="chromium"))
    return provider


@pytest.mark.modern_spa
@pytest.mark.unit
class TestUIFrameworkEnum:
    """Test UIFramework enum"""

    def test_ui_framework_values(self):
        """Test UIFramework enum values"""
        assert UIFramework.REACT.value == "react"
        assert UIFramework.VUE.value == "vue"
        assert UIFramework.ANGULAR.value == "angular"
        assert UIFramework.JSP.value == "jsp"
        assert UIFramework.LEGACY.value == "legacy"
        assert UIFramework.UNKNOWN.value == "unknown"

    def test_ui_framework_members(self):
        """Test all UIFramework enum members"""
        frameworks = list(UIFramework)
        assert len(frameworks) == 7  # UNKNOWN, REACT, ANGULAR, VUE, JSP, LEGACY, MODERN_SPA
        assert UIFramework.REACT in frameworks


@pytest.mark.modern_spa
@pytest.mark.unit
class TestTestComplexityEnum:
    """Test TestComplexity enum"""

    def test_complexity_values(self):
        """Test TestComplexity enum values"""
        assert TestComplexity.LOW.value == "low"
        assert TestComplexity.MEDIUM.value == "medium"
        assert TestComplexity.HIGH.value == "high"

    def test_complexity_ordering(self):
        """Test complexity levels can be compared"""
        assert TestComplexity.LOW != TestComplexity.HIGH
        assert TestComplexity.MEDIUM != TestComplexity.LOW


@pytest.mark.modern_spa
@pytest.mark.unit
class TestTestMetadata:
    """Test TestMetadata dataclass"""

    def test_create_test_metadata(self):
        """Test creating TestMetadata"""
        metadata = TestMetadata(
            test_name="test_login",
            ui_framework=UIFramework.REACT,
            is_spa=True,
            requires_javascript=True,
            complexity=TestComplexity.HIGH,
        )
        assert metadata.test_name == "test_login"
        assert metadata.ui_framework == UIFramework.REACT
        assert metadata.is_spa is True

    def test_test_metadata_defaults(self):
        """Test TestMetadata default values"""
        metadata = TestMetadata(test_name="test_basic")
        assert metadata.ui_framework is None  # Default is None
        assert metadata.is_spa is False
        assert metadata.requires_javascript is True
        assert metadata.complexity is None  # Default is None
        assert metadata.is_legacy_ui is False
        assert metadata.requires_mobile is False


@pytest.mark.modern_spa
@pytest.mark.unit
class TestModernEngineSelectorInit:
    """Test ModernEngineSelector initialization"""

    def test_create_selector(self, mock_config_provider):
        """Test creating ModernEngineSelector"""
        selector = ModernEngineSelector(mock_config_provider)
        assert selector.config_provider == mock_config_provider

    def test_selector_without_config(self):
        """Test selector can work without config provider"""
        selector = ModernEngineSelector()
        assert selector.config_provider is None


@pytest.mark.modern_spa
@pytest.mark.unit
class TestModernEngineSelectorPatternMatching:
    """Test pattern matching in select_engine"""

    def test_select_engine_react_high_complexity(self, mock_config_provider):
        """Test React + High Complexity → Playwright"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata = TestMetadata(
            test_name="test_react",
            ui_framework=UIFramework.REACT,
            complexity=TestComplexity.HIGH,
        )

        engine = selector.select_engine(metadata)
        assert engine.engine == EngineType.PLAYWRIGHT

    def test_select_engine_vue_high_complexity(self, mock_config_provider):
        """Test Vue + High Complexity → Playwright"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata = TestMetadata(
            test_name="test_vue",
            ui_framework=UIFramework.VUE,
            complexity=TestComplexity.HIGH,
        )

        engine = selector.select_engine(metadata)
        assert engine.engine == EngineType.PLAYWRIGHT

    def test_select_engine_angular_high_complexity(self, mock_config_provider):
        """Test Angular + High Complexity → Playwright"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata = TestMetadata(
            test_name="test_angular",
            ui_framework=UIFramework.ANGULAR,
            complexity=TestComplexity.HIGH,
        )

        engine = selector.select_engine(metadata)
        assert engine.engine == EngineType.PLAYWRIGHT

    def test_select_engine_jsp_legacy(self, mock_config_provider):
        """Test JSP/Legacy → Selenium"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata = TestMetadata(
            test_name="test_jsp",
            ui_framework=UIFramework.JSP,
            is_legacy_ui=True,
        )

        engine = selector.select_engine(metadata)
        assert engine.engine == EngineType.SELENIUM

    def test_select_engine_legacy_any_complexity(self, mock_config_provider):
        """Test Legacy UI always uses Selenium"""
        selector = ModernEngineSelector(mock_config_provider)

        for complexity in [
            TestComplexity.LOW,
            TestComplexity.MEDIUM,
            TestComplexity.HIGH,
        ]:
            metadata = TestMetadata(
                test_name="test_legacy",
                ui_framework=UIFramework.LEGACY,
                complexity=complexity,
            )

            engine = selector.select_engine(metadata)
            assert engine.engine == EngineType.SELENIUM

    def test_select_engine_low_complexity_any_framework(
        self, mock_config_provider
    ):
        """Test Low Complexity → Playwright (fastest)"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata = TestMetadata(
            test_name="test_simple",
            ui_framework=UIFramework.UNKNOWN,
            complexity=TestComplexity.LOW,
        )

        engine = selector.select_engine(metadata)
        assert engine.engine == EngineType.PLAYWRIGHT

    def test_select_engine_spa_always_playwright(self, mock_config_provider):
        """Test SPA applications prefer Playwright"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata = TestMetadata(
            test_name="test_spa",
            ui_framework=UIFramework.REACT,
            is_spa=True,
        )

        engine = selector.select_engine(metadata)
        assert engine.engine == EngineType.PLAYWRIGHT


@pytest.mark.modern_spa
@pytest.mark.unit
class TestModernEngineSelectorCaching:
    """Test caching functionality with @lru_cache"""

    def test_select_engine_cached(self, mock_config_provider):
        """Test select_engine uses caching"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata = TestMetadata(
            test_name="test_cached",
            ui_framework=UIFramework.REACT,
            complexity=TestComplexity.HIGH,
        )

        # Call twice
        engine1 = selector.select_engine(metadata)
        engine2 = selector.select_engine(metadata)

        # Should return same result (cached)
        assert engine1 == engine2
        assert engine1.engine == EngineType.PLAYWRIGHT

    def test_cache_different_metadata(self, mock_config_provider):
        """Test cache stores different metadata separately"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata1 = TestMetadata(
            test_name="test1",
            ui_framework=UIFramework.REACT,
            complexity=TestComplexity.HIGH,
        )

        metadata2 = TestMetadata(
            test_name="test2",
            ui_framework=UIFramework.JSP,
            is_legacy_ui=True,
        )

        engine1 = selector.select_engine(metadata1)
        engine2 = selector.select_engine(metadata2)

        # Different metadata → different results
        assert engine1.engine == EngineType.PLAYWRIGHT
        assert engine2.engine == EngineType.SELENIUM


@pytest.mark.modern_spa
@pytest.mark.unit
class TestModernEngineSelectorAdvanced:
    """Test advanced engine selection scenarios"""

    def test_mobile_testing_preference(self, mock_config_provider):
        """Test mobile testing requirements"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata = TestMetadata(
            test_name="test_mobile",
            ui_framework=UIFramework.REACT,
            requires_mobile=True,
        )

        engine = selector.select_engine(metadata)
        # Mobile tests should use appropriate engine
        assert engine.engine in [EngineType.PLAYWRIGHT, EngineType.APPIUM]

    def test_javascript_required(self, mock_config_provider):
        """Test JavaScript requirement influences selection"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata = TestMetadata(
            test_name="test_js",
            ui_framework=UIFramework.UNKNOWN,
            requires_javascript=True,
            complexity=TestComplexity.HIGH,
        )

        engine = selector.select_engine(metadata)
        # JavaScript-heavy tests prefer Playwright
        assert engine.engine == EngineType.PLAYWRIGHT

    def test_no_javascript_simple_test(self, mock_config_provider):
        """Test simple tests without JS can use either engine"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata = TestMetadata(
            test_name="test_simple",
            ui_framework=UIFramework.UNKNOWN,
            requires_javascript=False,
            complexity=TestComplexity.LOW,
        )

        engine = selector.select_engine(metadata)
        assert engine.engine in [EngineType.PLAYWRIGHT, EngineType.SELENIUM]


@pytest.mark.modern_spa
@pytest.mark.unit
class TestModernEngineSelectorRealWorldScenarios:
    """Test real-world testing scenarios"""

    def test_react_dashboard_complex(self, mock_config_provider):
        """Test React dashboard (complex SPA)"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata = TestMetadata(
            test_name="test_react_dashboard",
            ui_framework=UIFramework.REACT,
            is_spa=True,
            requires_javascript=True,
            complexity=TestComplexity.HIGH,
        )

        engine = selector.select_engine(metadata)
        assert engine.engine == EngineType.PLAYWRIGHT

    def test_legacy_jsp_application(self, mock_config_provider):
        """Test legacy JSP application"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata = TestMetadata(
            test_name="test_legacy_jsp",
            ui_framework=UIFramework.JSP,
            is_spa=False,
            is_legacy_ui=True,
            requires_javascript=False,
        )

        engine = selector.select_engine(metadata)
        assert engine.engine == EngineType.SELENIUM

    def test_simple_landing_page(self, mock_config_provider):
        """Test simple landing page"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata = TestMetadata(
            test_name="test_landing",
            ui_framework=UIFramework.UNKNOWN,
            is_spa=False,
            complexity=TestComplexity.LOW,
        )

        engine = selector.select_engine(metadata)
        # Simple tests use fastest engine
        assert engine.engine == EngineType.PLAYWRIGHT

    def test_vue_ecommerce_app(self, mock_config_provider):
        """Test Vue.js e-commerce application"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata = TestMetadata(
            test_name="test_vue_shop",
            ui_framework=UIFramework.VUE,
            is_spa=True,
            requires_javascript=True,
            complexity=TestComplexity.HIGH,
        )

        engine = selector.select_engine(metadata)
        assert engine.engine == EngineType.PLAYWRIGHT

    def test_angular_enterprise_app(self, mock_config_provider):
        """Test Angular enterprise application"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata = TestMetadata(
            test_name="test_angular_enterprise",
            ui_framework=UIFramework.ANGULAR,
            is_spa=True,
            requires_javascript=True,
            complexity=TestComplexity.HIGH,
        )

        engine = selector.select_engine(metadata)
        assert engine.engine == EngineType.PLAYWRIGHT


@pytest.mark.modern_spa
@pytest.mark.unit
class TestModernEngineSelectorEdgeCases:
    """Test edge cases and error handling"""

    def test_unknown_framework_defaults(self, mock_config_provider):
        """Test unknown framework uses intelligent default"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata = TestMetadata(
            test_name="test_unknown",
            ui_framework=UIFramework.UNKNOWN,
        )

        engine = selector.select_engine(metadata)
        # Should still return valid engine
        assert engine.engine in [
            EngineType.PLAYWRIGHT,
            EngineType.SELENIUM,
            EngineType.APPIUM,
        ]

    def test_conflicting_metadata(self, mock_config_provider):
        """Test handling conflicting metadata"""
        selector = ModernEngineSelector(mock_config_provider)

        # SPA + Legacy (conflicting)
        metadata = TestMetadata(
            test_name="test_conflict",
            ui_framework=UIFramework.REACT,
            is_spa=True,
            is_legacy_ui=True,  # Conflicting
        )

        engine = selector.select_engine(metadata)
        # Should still make a decision
        assert engine.engine in [EngineType.PLAYWRIGHT, EngineType.SELENIUM]


@pytest.mark.modern_spa
@pytest.mark.unit
class TestModernEngineSelectorIntegration:
    """Integration tests with full workflow"""

    def test_select_engine_for_multiple_tests(self, mock_config_provider):
        """Test selecting engines for multiple test scenarios"""
        selector = ModernEngineSelector(mock_config_provider)

        test_scenarios = [
            (
                TestMetadata(
                    test_name="test1",
                    ui_framework=UIFramework.REACT,
                    complexity=TestComplexity.HIGH,
                ),
                EngineType.PLAYWRIGHT,
            ),
            (
                TestMetadata(
                    test_name="test2",
                    ui_framework=UIFramework.JSP,
                    is_legacy_ui=True,
                ),
                EngineType.SELENIUM,
            ),
            (
                TestMetadata(
                    test_name="test3",
                    ui_framework=UIFramework.VUE,
                    complexity=TestComplexity.HIGH,
                ),
                EngineType.PLAYWRIGHT,
            ),
        ]

        for metadata, expected_engine in test_scenarios:
            engine = selector.select_engine(metadata)
            assert engine.engine == expected_engine

    def test_caching_performance(self, mock_config_provider):
        """Test caching improves performance"""
        selector = ModernEngineSelector(mock_config_provider)

        metadata = TestMetadata(
            test_name="test_cache",
            ui_framework=UIFramework.REACT,
            complexity=TestComplexity.HIGH,
        )

        import time

        # First call (not cached)
        start = time.time()
        for _ in range(100):
            selector.select_engine(metadata)
        duration_cached = time.time() - start

        # Should be very fast due to caching
        assert duration_cached < 0.1  # 100 calls in < 100ms


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
