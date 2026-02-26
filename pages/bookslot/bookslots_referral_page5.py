"""
Page Object: Bookslot Referral Source Page
Represents what a user can do on the Referral page

Author: Lokendra Singh
Email: lokendra.singh@centerforvein.com
Website: www.centerforvein.com

Project: BookSlot
Module: Referral Source (Marketing Attribution)

Responsibilities:
✔ Locators for referral source options
✔ Actions (select referral source)
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


class BookslotReferralPage(BasePage):
    """
    Page Object for Bookslot Referral Source
    
    What a user can do on this page:
    - Navigate to referral page
    - Read "How did you hear about us?" question
    - Select referral source (Physician, Online, Social Media, etc.)
    - Proceed to next page
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
        self.path = "/referral"
    
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
    def heading_question(self):
        """How did you hear about us heading"""
        return self.page.get_by_role("heading", name="How did you hear about us?")
    
    @property
    def button_physician(self):
        """Referred by physician button"""
        return self.page.get_by_role("button", name="Referred by physician")
    
    @property
    def radio_online(self):
        """Online search radio button"""
        return self.page.get_by_role("radio", name="Online search")
    
    @property
    def radio_social_media(self):
        """Social media radio button"""
        return self.page.get_by_role("radio", name="Social media")
    
    @property
    def radio_friend_family(self):
        """Friend or family radio button"""
        return self.page.get_by_role("radio", name="Friend or family")
    
    @property
    def radio_advertisement(self):
        """Advertisement radio button"""
        return self.page.get_by_role("radio", name="Advertisement")
    
    @property
    def button_next(self):
        """Next button"""
        return self.page.get_by_role("button", name="Next")
    
    # ===================================================================
    # NAVIGATION
    # ===================================================================
    
    @log_function(log_timing=True)
    def navigate(self, url: str = None):
        """Navigate to the referral page"""
        if url is None:
            url = f"{self.base_url}{self.path}"
        self.page.goto(url)
        return self
    
    # ===================================================================
    # ACTIONS
    # ===================================================================
    
    @log_function(log_timing=True)
    def select_physician(self):
        """Select Referred by physician"""
        self.heading_question.click()
        self.button_physician.click()
        return self
    
    @log_function(log_timing=True)
    def select_online(self):
        """Select Online search"""
        self.radio_online.click()
        return self
    
    @log_function(log_timing=True)
    def select_social_media(self):
        """Select Social media"""
        self.radio_social_media.click()
        return self
    
    @log_function(log_timing=True)
    def select_friend_family(self):
        """Select Friend or family"""
        self.radio_friend_family.click()
        return self
    
    @log_function(log_timing=True)
    def select_advertisement(self):
        """Select Advertisement"""
        self.radio_advertisement.click()
        return self
    
    @log_function(log_timing=True)
    def proceed_to_next(self):
        """Click Next button"""
        self.button_next.click()
        return self
    
    @log_function(log_timing=True)
    def is_online_checked(self) -> bool:
        """Check if online search radio is checked"""
        try:
            return self.radio_online.is_checked()
        except Exception as e:
            logger.error(f"Error checking online radio state: {e}")
            return False
    
    @log_function(log_timing=True)
    def is_physician_checked(self) -> bool:
        """Check if physician radio is checked"""
        try:
            return self.button_physician.is_checked()
        except Exception as e:
            logger.error(f"Error checking physician radio state: {e}")
            return False
    
    @log_function(log_timing=True)
    def is_social_media_checked(self) -> bool:
        """Check if social media radio is checked"""
        try:
            return self.radio_social_media.is_checked()
        except Exception as e:
            logger.error(f"Error checking social media radio state: {e}")
            return False
    
    @log_function(log_timing=True)
    def is_friend_family_checked(self) -> bool:
        """Check if friend/family radio is checked"""
        try:
            return self.radio_friend_family.is_checked()
        except Exception as e:
            logger.error(f"Error checking friend/family radio state: {e}")
            return False
    
    # ===================================================================
    # PAGE-LEVEL CHECKS
    # ===================================================================
    
    @log_function(log_timing=True)
    def is_page_loaded(self) -> bool:
        """Check if page is loaded"""
        try:
            return self.heading_question.is_visible()
        except Exception as e:
            logger.error(f"Error checking if referral page is loaded: {e}")
            return False
    
    @log_function(log_timing=True)
    def is_question_visible(self) -> bool:
        """Check if referral question is visible (no wait logic)"""
        try:
            return self.heading_question.is_visible()
        except Exception as e:
            logger.error(f"Error checking referral question visibility: {e}")
            return False


