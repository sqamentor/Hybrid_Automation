"""
Base Page Object

Abstract base class for all page objects.
Provides common methods and structure for both Playwright and Selenium.
Includes optional human behavior simulation for realistic interactions.

ARCHITECTURAL FIX: Enhanced to support true engine-agnostic Page Objects
while maintaining backward compatibility with existing Playwright-specific code.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from framework.core.utils.human_actions import HumanBehaviorSimulator, get_behavior_config
from utils.logger import get_logger, get_audit_logger

logger = get_logger(__name__)
audit_logger = get_audit_logger()


class BasePage(ABC):
    """Abstract base class for page objects with human behavior support"""

    def __init__(self, driver_or_page: Any, enable_human_behavior: Optional[bool] = None):
        self.driver = driver_or_page
        self._human_simulator = None
        self._human_enabled = enable_human_behavior
        
        # Engine detection for hybrid support
        self.engine_type = self._detect_engine()
        logger.info(f"BasePage initialized with engine: {self.engine_type}")

        # Initialize human behavior simulator if enabled
        if self._should_enable_human_behavior():
            self._init_human_behavior()
            logger.debug(f"Human behavior simulation enabled for {self.__class__.__name__}")
    
    def _detect_engine(self) -> str:
        """
        Detect which automation engine is being used.
        
        Returns:
            'playwright' if Playwright Page object
            'selenium' if Selenium WebDriver instance
        """
        driver_class = type(self.driver).__name__
        
        # Playwright detection
        if 'Page' in driver_class or hasattr(self.driver, 'goto'):
            return 'playwright'
        # Selenium detection
        elif hasattr(self.driver, 'get') and hasattr(self.driver, 'find_element'):
            return 'selenium'
        else:
            # Default to playwright for backward compatibility
            return 'playwright'
    
    @property
    def page(self):
        """
        Compatibility property for existing code using .page attribute.
        
        Returns:
            The underlying driver (Playwright Page or Selenium WebDriver)
        """
        return self.driver

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
            logger.debug("Human behavior simulator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize human behavior: {e}")
            self._human_simulator = None

    def enable_human_behavior(self, enabled: bool = True):
        """Enable or disable human behavior for this page instance"""
        self._human_enabled = enabled
        logger.info(f"Human behavior {'enabled' if enabled else 'disabled'} for {self.__class__.__name__}")
        if enabled and self._human_simulator is None:
            self._init_human_behavior()
        elif self._human_simulator:
            self._human_simulator._enabled = enabled

    def human_type(self, locator: str, text: str, clear_first: bool = True) -> bool:
        """Type text with human-like behavior if enabled, otherwise normal typing"""
        logger.debug(f"Typing text into {locator} with human behavior: {self._human_enabled}")
        if self._human_simulator and self._human_enabled:
            result = self._human_simulator.type_text(locator, text, clear_first)
            audit_logger.log_element_interaction("human_type", locator, value=text[:50], success=result)
            return result
        else:
            # Fallback to normal fill
            self.fill(locator, text)
            audit_logger.log_element_interaction("type", locator, value=text[:50])
            return True

    def human_click(self, locator: str) -> bool:
        """Click with human-like behavior if enabled, otherwise normal click"""
        logger.debug(f"Clicking {locator} with human behavior: {self._human_enabled}")
        if self._human_simulator and self._human_enabled:
            result = self._human_simulator.click_element(locator)
            audit_logger.log_element_interaction("human_click", locator, success=result)
            return result
        else:
            # Fallback to normal click
            self.click(locator)
            audit_logger.log_element_interaction("click", locator)
            return True

    def human_scroll(self, direction: str = "down", distance: Optional[int] = None) -> bool:
        """Scroll with human-like behavior if enabled"""
        logger.debug(f"Scrolling {direction} with human behavior: {self._human_enabled}")
        if self._human_simulator and self._human_enabled:
            result = self._human_simulator.scroll_page(direction, distance)
            audit_logger.log_ui_action("human_scroll", f"direction={direction}, distance={distance}")
            return result
        logger.debug("Human behavior not enabled, scroll not performed")
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
