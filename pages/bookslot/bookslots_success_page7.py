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
        self.page = self.driver  # Compatibility alias
        if not base_url:
            raise ValueError("base_url is required from multi_project_config")
        self.base_url = base_url
        self.path = "/success"
    
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
    def navigate(self):
        """Navigate to the success page"""
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


