"""
Modern Engine Selector with Pattern Matching

Python 3.12+ pattern matching for engine selection with structural pattern matching,
Pydantic models, and dependency injection support.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

from framework.models.config_models import EngineType
from framework.protocols.config_protocols import ConfigProvider


class TestComplexity(str, Enum):
    """Test complexity levels"""
    LOW = "low"
    SIMPLE = "simple"
    MODERATE = "moderate"
    MEDIUM = "medium"
    COMPLEX = "complex"
    HIGH = "high"
    VERY_COMPLEX = "very_complex"


class UIFramework(str, Enum):
    """UI framework types"""
    UNKNOWN = "unknown"
    REACT = "react"
    ANGULAR = "angular"
    VUE = "vue"
    JSP = "jsp"
    LEGACY = "legacy"
    MODERN_SPA = "modern_spa"


@dataclass(frozen=True)
class EngineDecision:
    """Immutable engine selection decision"""
    engine: EngineType
    confidence: int  # 0-100
    reason: str
    rule_name: str
    fallback_engine: Optional[EngineType] = None
    priority: int = 0
    cache_hit: bool = False


@dataclass(frozen=True)
class TestMetadata:
    """Test metadata for engine selection"""
    module: str = ""
    ui_framework: Optional[UIFramework] = None
    complexity: Optional[TestComplexity] = None
    markers: Optional[tuple] = None  # Changed from List to tuple for hashability
    auth_type: Optional[str] = None
    api_validation_needed: bool = False
    legacy_system: bool = False
    test_name: Optional[str] = None
    is_spa: bool = False
    is_legacy_ui: bool = False
    requires_mobile: bool = False
    requires_javascript: bool = True
    
    def __post_init__(self):
        if self.markers is None:
            object.__setattr__(self, 'markers', ())


class ModernEngineSelector:
    """
    Engine selector using Python 3.12+ structural pattern matching.
    
    Features:
    - Structural pattern matching for readable decision logic
    - Pydantic models for type safety
    - LRU caching for performance
    - Dependency injection support
    - Immutable decisions
    """
    
    def __init__(
        self,
        config_provider: Optional[ConfigProvider] = None,
        cache_size: int = 100,
        cache_ttl: int = 3600
    ):
        self.config_provider = config_provider
        self.cache_ttl = cache_ttl
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'total_lookups': 0
        }
    
    @lru_cache(maxsize=100)
    def select_engine(self, metadata: TestMetadata) -> EngineDecision:
        """
        Select engine using modern pattern matching.
        
        Args:
            metadata: Test metadata for selection
        
        Returns:
            Immutable EngineDecision
        """
        self._cache_stats['total_lookups'] += 1
        
        # Pattern match on test characteristics
        match (metadata.ui_framework, metadata.complexity, metadata.legacy_system):
            
            # Modern SPA with simple/moderate complexity -> Playwright
            case (UIFramework.REACT | UIFramework.VUE | UIFramework.ANGULAR, 
                  TestComplexity.SIMPLE | TestComplexity.MODERATE, False):
                return EngineDecision(
                    engine=EngineType.PLAYWRIGHT,
                    confidence=95,
                    reason="Modern SPA framework with moderate complexity - Playwright optimal",
                    rule_name="modern_spa_playwright",
                    priority=90
                )
            
            # Modern SPA with high complexity -> Hybrid
            case (UIFramework.REACT | UIFramework.VUE | UIFramework.ANGULAR,
                  TestComplexity.COMPLEX | TestComplexity.VERY_COMPLEX, False):
                return EngineDecision(
                    engine=EngineType.HYBRID,
                    confidence=85,
                    reason="Complex modern SPA - hybrid approach for comprehensive coverage",
                    rule_name="complex_spa_hybrid",
                    fallback_engine=EngineType.PLAYWRIGHT,
                    priority=85
                )
            
            # Legacy systems -> Selenium
            case (UIFramework.JSP | UIFramework.LEGACY, _, True) | (_, _, True):
                return EngineDecision(
                    engine=EngineType.SELENIUM,
                    confidence=90,
                    reason="Legacy system detected - Selenium more stable",
                    rule_name="legacy_selenium",
                    fallback_engine=EngineType.PLAYWRIGHT,
                    priority=88
                )
            
            # JSP/Legacy frameworks (non-legacy system) -> Selenium preferred
            case (UIFramework.JSP | UIFramework.LEGACY, _, False):
                return EngineDecision(
                    engine=EngineType.SELENIUM,
                    confidence=80,
                    reason="JSP/Legacy framework - Selenium compatibility preferred",
                    rule_name="jsp_selenium",
                    fallback_engine=EngineType.PLAYWRIGHT,
                    priority=75
                )
            
            # Default case -> Playwright
            case _:
                return self._evaluate_additional_criteria(metadata)
    
    def _evaluate_additional_criteria(self, metadata: TestMetadata) -> EngineDecision:
        """Evaluate additional criteria using pattern matching"""
        
        # Match on markers
        match metadata.markers:
            case markers if "api_validation" in markers:
                return EngineDecision(
                    engine=EngineType.HYBRID,
                    confidence=85,
                    reason="API validation required - hybrid approach recommended",
                    rule_name="api_validation_hybrid",
                    priority=80
                )
            
            case markers if "modern_spa" in markers:
                return EngineDecision(
                    engine=EngineType.PLAYWRIGHT,
                    confidence=90,
                    reason="Modern SPA marker detected - Playwright optimal",
                    rule_name="marker_modern_spa",
                    priority=85
                )
            
            case markers if "legacy_support" in markers or "ie11" in markers:
                return EngineDecision(
                    engine=EngineType.SELENIUM,
                    confidence=95,
                    reason="Legacy browser support required - Selenium necessary",
                    rule_name="marker_legacy_support",
                    priority=90
                )
        
        # Match on auth type
        match metadata.auth_type:
            case "SSO" | "SAML" | "OAuth2":
                return EngineDecision(
                    engine=EngineType.PLAYWRIGHT,
                    confidence=85,
                    reason="Modern auth protocol - Playwright handles well",
                    rule_name="modern_auth",
                    priority=75
                )
            
            case "NTLM" | "Kerberos":
                return EngineDecision(
                    engine=EngineType.SELENIUM,
                    confidence=80,
                    reason="Enterprise auth protocol - Selenium more stable",
                    rule_name="enterprise_auth",
                    priority=75
                )
        
        # Match on module name patterns
        match metadata.module:
            case module if "admin" in module.lower() or "dashboard" in module.lower():
                return EngineDecision(
                    engine=EngineType.PLAYWRIGHT,
                    confidence=85,
                    reason="Admin/Dashboard module - Playwright speed beneficial",
                    rule_name="admin_module",
                    priority=70
                )
            
            case module if "checkout" in module.lower() or "payment" in module.lower():
                return EngineDecision(
                    engine=EngineType.HYBRID,
                    confidence=90,
                    reason="Critical payment flow - hybrid approach for reliability",
                    rule_name="critical_checkout",
                    fallback_engine=EngineType.SELENIUM,
                    priority=95
                )
        
        # Default fallback
        return EngineDecision(
            engine=EngineType.PLAYWRIGHT,
            confidence=70,
            reason="No specific pattern matched - default to Playwright",
            rule_name="default_playwright",
            fallback_engine=EngineType.SELENIUM,
            priority=50
        )
    
    def select_engine_from_dict(self, metadata_dict: Dict[str, Any]) -> EngineDecision:
        """
        Convenience method to select engine from dictionary.
        
        Args:
            metadata_dict: Dictionary with test metadata
        
        Returns:
            EngineDecision
        """
        # Convert dict to TestMetadata
        ui_framework_str = metadata_dict.get('ui_framework')
        ui_framework = None
        if ui_framework_str:
            try:
                ui_framework = UIFramework(ui_framework_str.lower())
            except ValueError:
                pass
        
        complexity_str = metadata_dict.get('complexity')
        complexity = None
        if complexity_str:
            try:
                complexity = TestComplexity(complexity_str.lower())
            except ValueError:
                pass
        
        metadata = TestMetadata(
            module=metadata_dict.get('module', 'unknown'),
            ui_framework=ui_framework,
            complexity=complexity,
            markers=metadata_dict.get('markers', []),
            auth_type=metadata_dict.get('auth_type'),
            api_validation_needed=metadata_dict.get('api_validation_needed', False),
            legacy_system=metadata_dict.get('legacy_system', False),
            test_name=metadata_dict.get('test_name'),
        )
        
        return self.select_engine(metadata)
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        hit_rate = 0.0
        if self._cache_stats['total_lookups'] > 0:
            hit_rate = (self._cache_stats['hits'] / self._cache_stats['total_lookups']) * 100
        
        return {
            **self._cache_stats,
            'hit_rate_percent': round(hit_rate, 2),
            'cache_info': self.select_engine.cache_info()._asdict()
        }
    
    def clear_cache(self) -> None:
        """Clear engine selection cache"""
        self.select_engine.cache_clear()
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'total_lookups': 0
        }
