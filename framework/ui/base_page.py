"""
Base Page Object

Abstract base class for all page objects.
Provides common methods and structure for both Playwright and Selenium.
Includes optional human behavior simulation for realistic interactions.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from framework.core.utils.human_actions import HumanBehaviorSimulator, get_behavior_config


class BasePage(ABC):
    """Abstract base class for page objects with human behavior support"""
    
    def __init__(self, driver_or_page: Any, enable_human_behavior: Optional[bool] = None):
        self.driver = driver_or_page
        self._human_simulator = None
        self._human_enabled = enable_human_behavior
        
        # Initialize human behavior simulator if enabled
        if self._should_enable_human_behavior():
            self._init_human_behavior()
    
    def _should_enable_human_behavior(self) -> bool:
        """Determine if human behavior should be enabled"""
        if self._human_enabled is not None:
            return self._human_enabled
        
        # Check config
        config = get_behavior_config()
        return config.is_enabled()
    
    def _init_human_behavior(self):
        """Initialize human behavior simulator"""
        try:
            self._human_simulator = HumanBehaviorSimulator(self.driver, enabled=self._human_enabled)
        except Exception as e:
            print(f"[BasePage] Failed to initialize human behavior: {e}")
            self._human_simulator = None
    
    def enable_human_behavior(self, enabled: bool = True):
        """Enable or disable human behavior for this page instance"""
        self._human_enabled = enabled
        if enabled and self._human_simulator is None:
            self._init_human_behavior()
        elif self._human_simulator:
            self._human_simulator._enabled = enabled
    
    def human_type(self, locator: str, text: str, clear_first: bool = True) -> bool:
        """Type text with human-like behavior if enabled, otherwise normal typing"""
        if self._human_simulator and self._human_enabled:
            return self._human_simulator.type_text(locator, text, clear_first)
        else:
            # Fallback to normal fill
            self.fill(locator, text)
            return True
    
    def human_click(self, locator: str) -> bool:
        """Click with human-like behavior if enabled, otherwise normal click"""
        if self._human_simulator and self._human_enabled:
            return self._human_simulator.click_element(locator)
        else:
            # Fallback to normal click
            self.click(locator)
            return True
    
    def human_scroll(self, direction: str = 'down', distance: Optional[int] = None) -> bool:
        """Scroll with human-like behavior if enabled"""
        if self._human_simulator and self._human_enabled:
            return self._human_simulator.scroll_page(direction, distance)
        return True
    
    @abstractmethod
    def navigate(self, url: str):
        """Navigate to URL"""
        pass
    
    @abstractmethod
    def click(self, locator: str):
        """Click element"""
        pass
    
    @abstractmethod
    def fill(self, locator: str, text: str):
        """Fill input field"""
        pass
    
    @abstractmethod
    def get_text(self, locator: str) -> str:
        """Get element text"""
        pass
    
    @abstractmethod
    def is_visible(self, locator: str) -> bool:
        """Check if element is visible"""
        pass
    
    @abstractmethod
    def wait_for_element(self, locator: str, timeout: int = 10000):
        """Wait for element to be visible"""
        pass
    
    @abstractmethod
    def take_screenshot(self, filename: str):
        """Take screenshot"""
        pass
    
    @abstractmethod
    def get_current_url(self) -> str:
        """Get current page URL"""
        pass
    
    @abstractmethod
    def get_title(self) -> str:
        """Get page title"""
        pass
