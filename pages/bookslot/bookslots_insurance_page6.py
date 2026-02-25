"""
Page Object: Bookslot Insurance Information Page
Represents what a user can do on the Insurance page

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

Project: BookSlot
Module: Insurance Information (Coverage Details)

Responsibilities:
✔ Locators for insurance fields
✔ Actions (fill insurance info, submit)
✔ Page-level checks
✔ Navigation

Does NOT contain:
❌ Test data
❌ Business rule assertions
❌ API/DB validation
❌ pytest markers
❌ Complete test flows
"""

import logging

from framework.ui.base_page import BasePage
from framework.observability import log_function, log_async_function

logger = logging.getLogger(__name__)


class BookslotInsurancePage(BasePage):
    """
    Page Object for Bookslot Insurance Information
    
    What a user can do on this page:
    - Navigate to insurance page
    - Fill member name, ID number, group number
    - Fill insurance company name
    - Submit to clinic
    """

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
        self.path = "/insurance"
    
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
    def textbox_member_name(self):
        """Member Name field"""
        return self.page.get_by_role("textbox", name="Member Name *")
    
    @property
    def textbox_id_number(self):
        """ID Number field"""
        return self.page.get_by_role("textbox", name="ID Number *")
    
    @property
    def textbox_group_number(self):
        """Group number field"""
        return self.page.get_by_role("textbox", name="Group number *")
    
    @property
    def textbox_insurance_company(self):
        """Insurance Company Name field"""
        return self.page.get_by_role("textbox", name="Insurance Company Name *")
    
    @property
    def button_send_to_clinic(self):
        """Send to clinic button"""
        return self.page.get_by_role("button", name="Send to clinic")
    
    @property
    def button_next(self):
        """Next button (alternative submit)"""
        return self.page.get_by_role("button", name="Next")
    
    # ===================================================================
    # NAVIGATION
    # ===================================================================
    
    @log_function(log_timing=True)
    def navigate(self, url: str = None):
        """Navigate to the insurance page"""
        if url is None:
            url = f"{self.base_url}{self.path}"
        self.page.goto(url)
        return self
    
    # ===================================================================
    # ACTIONS
    # ===================================================================
    
    @log_function(log_timing=True)
    def fill_member_name(self, member_name: str):
        """Fill Member Name field"""
        self.textbox_member_name.click()
        self.textbox_member_name.fill(member_name)
        return self
    
    @log_function(log_timing=True)
    def fill_id_number(self, id_number: str):
        """Fill ID Number field"""
        self.textbox_id_number.click()
        self.textbox_id_number.fill(id_number)
        return self
    
    @log_function(log_timing=True)
    def fill_group_number(self, group_number: str):
        """Fill Group number field"""
        self.textbox_group_number.click()
        self.textbox_group_number.fill(group_number)
        return self
    
    @log_function(log_timing=True)
    def fill_insurance_company(self, company_name: str):
        """Fill Insurance Company Name field"""
        self.textbox_insurance_company.click()
        self.textbox_insurance_company.fill(company_name)
        return self
    
    @log_function(log_timing=True)
    def get_member_name_value(self) -> str:
        """Get current value of member name field"""
        return self.textbox_member_name.input_value()
    
    @log_function(log_timing=True)
    def get_id_number_value(self) -> str:
        """Get current value of ID number field"""
        return self.textbox_id_number.input_value()
    
    @log_function(log_timing=True)
    def get_group_number_value(self) -> str:
        """Get current value of group number field"""
        return self.textbox_group_number.input_value()
    
    @log_function(log_timing=True)
    def get_insurance_company_value(self) -> str:
        """Get current value of insurance company field"""
        return self.textbox_insurance_company.input_value()
    
    @log_function(log_timing=True)
    def clear_group_number(self):
        """Clear group number field"""
        self.textbox_group_number.clear()
        return self
    
    @log_function(log_timing=True)
    def submit_to_clinic(self):
        """Click Send to clinic button"""
        self.button_send_to_clinic.click()
        return self
    
    @log_function(log_timing=True)
    def proceed_to_next(self):
        """Click Next button"""
        self.button_next.click()
        return self
    
    # ===================================================================
    # PAGE-LEVEL CHECKS
    # ===================================================================
    
    @log_function(log_timing=True)
    def is_page_loaded(self) -> bool:
        """Check if page is loaded"""
        try:
            return self.textbox_member_name.is_visible()
        except Exception as e:
            logger.error(f"Error checking if insurance page is loaded: {e}")
            return False
    
    @log_function(log_timing=True)
    def is_member_name_visible(self) -> bool:
        """Check if member name field is visible (no wait logic)"""
        try:
            return self.textbox_member_name.is_visible()
        except Exception as e:
            logger.error(f"Error checking member name visibility: {e}")
            return False


