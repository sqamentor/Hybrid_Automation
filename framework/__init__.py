"""Framework Core Module.

Enterprise-Grade Hybrid Automation Framework

This package provides a comprehensive, plug-and-play automation framework
combining Playwright, Selenium, API testing, database validation, AI capabilities,
and much more.

Quick Start:
    >>> from framework.core.smart_actions import SmartActions
    >>> from framework.ui.ui_factory import UIFactory
    >>> engine = UIFactory.create_engine("playwright")

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com
Assisted by: AI Claude (Anthropic)
"""

from typing import Any, List

__version__ = "1.0.0"
__author__ = "Lokendra Singh"
__email__ = "qa.lokendra@gmail.com"
__website__ = "www.sqamentor.com"
__credits__ = "Assisted by AI Claude (Anthropic)"

# Public API - Export commonly used classes and functions
__all__: List[str] = [
    # Version info
    "__version__",
    "__author__",
    
    # Core
    "SmartActions",
    "UIFactory",
    "EngineSelector",
    
    # Exceptions
    "AutomationFrameworkException",
    "EngineException",
    "ConfigurationException",
    
    # Configuration
    "SettingsManager",
]

# Lazy imports for better performance
def __getattr__(name: str) -> Any:
    """Lazy import for better startup performance."""
    
    if name == "SmartActions":
        from framework.core.smart_actions import SmartActions
        return SmartActions
    
    elif name == "UIFactory":
        from framework.ui.ui_factory import UIFactory
        return UIFactory
    
    elif name == "EngineSelector":
        from framework.core.engine_selector import EngineSelector
        return EngineSelector
    
    elif name == "AutomationFrameworkException":
        from framework.core.exceptions import AutomationFrameworkException
        return AutomationFrameworkException
    
    elif name == "EngineException":
        from framework.core.exceptions import EngineException
        return EngineException
    
    elif name == "ConfigurationException":
        from framework.core.exceptions import ConfigurationException
        return ConfigurationException
    
    elif name == "SettingsManager":
        from config.settings import SettingsManager
        return SettingsManager
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

