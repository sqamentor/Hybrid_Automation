"""
Automation Protocol Interfaces

Protocol classes defining interfaces for automation engines and components.
These enable structural subtyping and dependency injection.
"""

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from playwright.sync_api import Locator, Page


@runtime_checkable
class AutomationEngine(Protocol):
    """Protocol for automation engine implementations"""
    
    def navigate_to(self, url: str) -> None:
        """Navigate to URL"""
        ...
    
    def click(self, selector: str) -> None:
        """Click on element"""
        ...
    
    def fill(self, selector: str, value: str) -> None:
        """Fill input field"""
        ...
    
    def get_text(self, selector: str) -> str:
        """Get element text"""
        ...
    
    def is_visible(self, selector: str) -> bool:
        """Check if element is visible"""
        ...
    
    def wait_for_selector(self, selector: str, timeout: int = 30000) -> None:
        """Wait for element to appear"""
        ...
    
    def screenshot(self, path: str) -> None:
        """Take screenshot"""
        ...


@runtime_checkable
class PageObject(Protocol):
    """Protocol for Page Object implementations"""
    
    @property
    def page(self) -> Page:
        """Get Playwright page instance"""
        ...
    
    def wait_for_page_load(self) -> None:
        """Wait for page to fully load"""
        ...
    
    def is_page_loaded(self) -> bool:
        """Check if page is fully loaded"""
        ...
    
    def get_page_title(self) -> str:
        """Get page title"""
        ...
    
    def get_page_url(self) -> str:
        """Get current page URL"""
        ...


@runtime_checkable
class ActionPerformer(Protocol):
    """Protocol for action performer implementations"""
    
    def click(self, locator: Locator, description: Optional[str] = None) -> None:
        """Perform click action with human-like behavior"""
        ...
    
    def fill(self, locator: Locator, text: str, description: Optional[str] = None) -> None:
        """Fill text with optimized typing"""
        ...
    
    def select_dropdown(
        self,
        locator: Locator,
        value: str,
        by: str = "value",
        description: Optional[str] = None
    ) -> None:
        """Select dropdown option"""
        ...
    
    def hover(self, locator: Locator, description: Optional[str] = None) -> None:
        """Hover over element"""
        ...
    
    def wait_for_element(
        self,
        locator: Locator,
        state: str = "visible",
        timeout: Optional[int] = None
    ) -> None:
        """Wait for element state"""
        ...


@runtime_checkable
class TestDataProvider(Protocol):
    """Protocol for test data providers"""
    
    def get_test_data(self, test_name: str) -> Dict[str, Any]:
        """Get test data for specific test"""
        ...
    
    def get_user_data(self, user_type: str) -> Dict[str, Any]:
        """Get user data by type"""
        ...
    
    def get_environment_data(self, env: str) -> Dict[str, Any]:
        """Get environment-specific data"""
        ...
    
    def generate_fake_data(self, data_type: str) -> Any:
        """Generate fake data of specified type"""
        ...
    
    def validate_data(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate data against schema"""
        ...
