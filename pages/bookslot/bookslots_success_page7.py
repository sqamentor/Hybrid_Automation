"""
Page Object: Bookslot Success Page
Represents what a user can see on the Success/Confirmation page

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

Project: BookSlot
Module: Success/Confirmation (Completion)

Responsibilities:
✔ Locators for success page elements
✔ Page-level checks (confirmation visible)
✔ Navigation

Does NOT contain:
❌ Test data
❌ Business rule assertions
❌ API/DB validation
❌ pytest markers
❌ Complete test flows
"""

import logging
import re

from framework.ui.base_page import BasePage
from framework.observability import log_function, log_async_function

logger = logging.getLogger(__name__)


class BookslotSuccessPage(BasePage):
    """Page Object for Bookslot Success Page - Appointment Confirmation"""

    def __init__(self, page, base_url: str):
        """
        Initialize page object
        
        Args:
            page: Playwright Page or Selenium WebDriver instance
            base_url: Base URL from multi_project_config
        """
        super().__init__(page)
        if not base_url:
            raise ValueError("base_url is required from multi_project_config")
        self.base_url = base_url
        self.path = "/success"
    
    # ===================================================================
    # ABSTRACT METHOD IMPLEMENTATIONS (Required by BasePage)
    # ===================================================================
    
    def click(self, locator: str):
        """Click element by locator string"""
        self.page.locator(locator).click()
    
    def fill(self, locator: str, text: str):
        """Fill input field by locator string"""
        self.page.locator(locator).fill(text)
    
    def get_text(self, locator: str) -> str:
        """Get element text by locator string"""
        return self.page.locator(locator).inner_text()
    
    def is_visible(self, locator: str) -> bool:
        """Check if element is visible by locator string"""
        try:
            return self.page.locator(locator).is_visible()
        except:
            return False
    
    def wait_for_element(self, locator: str, timeout: int = 10000):
        """Wait for element to be visible by locator string"""
        self.page.locator(locator).wait_for(state="visible", timeout=timeout)
    
    def take_screenshot(self, filename: str):
        """Take screenshot and save to file"""
        self.page.screenshot(path=filename)
    
    def get_current_url(self) -> str:
        """Get current page URL"""
        return self.page.url
    
    def get_title(self) -> str:
        """Get page title"""
        return self.page.title()
    
    # ===================================================================
    # LOCATORS
    # ===================================================================
    
    @property
    def redirect_message(self):
        """Redirect countdown message"""
        return self.page.locator("div").filter(has_text=re.compile(r"^You will be redirected in \d+ seconds$"))
    
    # ===================================================================
    # NAVIGATION
    # ===================================================================

    @log_function(log_timing=True)
    def navigate(self, url: str = None):
        """Navigate to the success page"""
        if url is None:
            url = f"{self.base_url}{self.path}"
        self.page.goto(url)
        return self
    
    # ===================================================================
    # ACTIONS
    # ===================================================================
    
    @log_function(log_timing=True)
    def click_redirect_message(self):
        """Click redirect message"""
        self.redirect_message.click()
        return self

    # ===================================================================
    # PAGE-LEVEL CHECKS
    # ===================================================================
    
    @log_function(log_timing=True)
    def is_page_loaded(self) -> bool:
        """Check if success page is loaded"""
        try:
            return "/success" in self.page.url
        except Exception as e:
            logger.error(f"Error checking if success page is loaded: {e}")
            return False
    
    @log_function(log_timing=True)
    def is_redirect_message_visible(self) -> bool:
        """Check if redirect countdown is visible"""
        try:
            return self.redirect_message.is_visible()
        except Exception as e:
            logger.error(f"Error checking redirect message visibility: {e}")
            return False


