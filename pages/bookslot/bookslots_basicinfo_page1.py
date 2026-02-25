"""
Page Object: Bookslot Basic Info Page
Represents what a user can do on the Basic Info page

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

Project: BookSlot
Module: Basic Info (Patient Information Collection)

Responsibilities:
✔ Locators for page elements
✔ Actions (fill, click, select)
✔ Page-level checks (page loaded, fields visible)
✔ Navigation

Does NOT contain:
❌ Test data
❌ Business rule assertions
❌ API/DB validation
❌ pytest markers
❌ Complete test flows
"""

import logging

from framework.observability import log_function
from framework.ui.base_page import BasePage

logger = logging.getLogger(__name__)


class BookslotBasicInfoPage(BasePage):
    """
    Page Object for Bookslot Basic Info Page
    
    What a user can do on this page:
    - Navigate to the page
    - Select language (English/Spanish)
    - Fill first name, last name, email, phone, zip code
    - Select contact preferences
    - Submit form to get OTP code
    - Enter and verify OTP
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
        self.path = "/basic-info"

    # ===================================================================
    # LOCATORS
    # ===================================================================
    
    @property
    def heading_collect_info(self):
        """'We need to collect some' heading"""
        return self.page.get_by_role("heading", name="We need to collect some")
    
    @property
    def heading_required_fields(self):
        """'Fields marked with * are' heading"""
        return self.page.get_by_role("heading", name="Fields marked with * are")
    
    @property
    def button_english(self):
        """English language button"""
        return self.page.get_by_role("button", name="English")
    
    @property
    def button_spanish(self):
        """Spanish language button"""
        return self.page.get_by_role("button", name="Español")
    
    @property
    def textbox_first_name(self):
        """First Name input field"""
        return self.page.get_by_role("textbox", name="First Name *")
    
    @property
    def textbox_last_name(self):
        """Last Name input field"""
        return self.page.get_by_role("textbox", name="Last Name *")
    
    @property
    def textbox_email(self):
        """Email input field"""
        return self.page.get_by_role("textbox", name="E-mail *")
    
    @property
    def textbox_phone(self):
        """Phone number input field"""
        return self.page.locator("#CellPhone").get_by_role("textbox")
    
    @property
    def textbox_zip(self):
        """Zip code input field"""
        return self.page.locator("#ZipCode")
    
    @property
    def contact_preference(self):
        """Contact preference options (Text/Email/Call)"""
        return self.page.get_by_text("Text E-mail Call")
    
    @property
    def button_send_code(self):
        """Send Me The Code button"""
        return self.page.get_by_role("button", name="Send Me The Code")
    
    @property
    def textbox_otp(self):
        """OTP verification code input (handles PrimeNG p-inputmask)"""
        # Try PrimeNG component first, then fallback to regular input
        otp_component = self.page.locator("#otp input, p-inputmask#otp input, input[type='text'][name*='otp'], input[placeholder*='code'], input[placeholder*='OTP']").first
        return otp_component
    
    @property
    def button_verify_code(self):
        """Verify Code button"""
        return self.page.get_by_role("button", name="Verify Code")
    
    @property
    def button_next(self):
        """Next button to proceed"""
        return self.page.get_by_role("button", name="Next")

    # ===================================================================
    # NAVIGATION
    # ===================================================================
    
    @log_function(log_args=True, log_result=False, log_timing=True)
    def navigate(self, url: str = None):
        """
        Navigate to the basic info page
        
        Args:
            url: Optional URL to navigate to. If not provided, uses base_url + path
        """
        target_url = url if url else f"{self.base_url}{self.path}"
        self.page.goto(target_url, wait_until="networkidle")
        return self
    
    @log_function(log_timing=True)
    def wait_for_page_load(self):
        """Wait for page to fully load"""
        self.page.wait_for_load_state("networkidle")
        return self

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
    # ACTIONS
    # ===================================================================
    
    @log_function(log_timing=True)
    def select_language_english(self):
        """Select English language"""
        self.button_english.click()
        return self
    
    @log_function(log_timing=True)
    def select_language_spanish(self):
        """Select Spanish language"""
        self.button_spanish.click()
        return self
    
    @log_function(log_args=True, log_timing=True, mask_sensitive=True)
    def fill_first_name(self, first_name: str):
        """Fill first name field"""
        self.textbox_first_name.click()
        self.textbox_first_name.fill(first_name)
        return self
    
    @log_function(log_args=True, log_timing=True, mask_sensitive=True)
    def fill_last_name(self, last_name: str):
        """Fill last name field"""
        self.textbox_last_name.click()
        self.textbox_last_name.fill(last_name)
        return self
    
    @log_function(log_args=True, log_timing=True, mask_sensitive=True)
    def fill_email(self, email: str):
        """Fill email field"""
        self.textbox_email.click()
        self.textbox_email.fill(email)
        return self
    
    @log_function(log_args=True, log_timing=True, mask_sensitive=True)
    def fill_phone(self, phone: str):
        """Fill phone number field"""
        self.textbox_phone.click()
        self.textbox_phone.fill(phone)
        return self
    
    @log_function(log_args=True, log_timing=True)
    def fill_zip(self, zip_code: str):
        """Fill zip code field"""
        self.textbox_zip.click()
        self.textbox_zip.fill(zip_code)
        return self
    
    @log_function(log_timing=True)
    def select_contact_preference(self):
        """Click contact preference options"""
        self.contact_preference.click()
        return self
    
    @log_function(log_timing=True)
    def submit_for_otp(self):
        """Submit form to receive OTP code"""
        self.button_send_code.click()
        return self
    
    @log_function(log_args=True, log_timing=True, mask_sensitive=True)
    def fill_otp(self, otp_code: str):
        """Fill OTP verification code (handles PrimeNG p-inputmask)"""
        # For PrimeNG p-inputmask, we need to type instead of fill
        try:
            self.textbox_otp.click()
            self.textbox_otp.type(otp_code, delay=100)
        except Exception as e:
            logger.warning(f"OTP type method failed, using fallback: {e}")
            # Fallback: try filling directly
            self.textbox_otp.fill(otp_code)
        return self
    
    @log_function(log_timing=True)
    def verify_otp(self):
        """Click verify code button"""
        self.button_verify_code.click()
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
        """Check if page is loaded by verifying key element"""
        try:
            return self.textbox_first_name.is_visible()
        except Exception as e:
            logger.error(f"Error checking if page is loaded: {e}")
            return False
    
    @log_function(log_timing=True)
    def is_first_name_visible(self) -> bool:
        """Check if first name field is visible"""
        try:
            return self.textbox_first_name.is_visible()
        except Exception as e:
            logger.error(f"Error checking first name visibility: {e}")
            return False
    
    @log_function(log_timing=True)
    def is_last_name_visible(self) -> bool:
        """Check if last name field is visible"""
        try:
            return self.textbox_last_name.is_visible()
        except Exception as e:
            logger.error(f"Error checking last name visibility: {e}")
            return False
    
    @log_function(log_timing=True)
    def is_email_visible(self) -> bool:
        """Check if email field is visible"""
        try:
            return self.textbox_email.is_visible()
        except Exception as e:
            logger.error(f"Error checking email visibility: {e}")
            return False
    
    @log_function(log_timing=True)
    def is_phone_visible(self) -> bool:
        """Check if phone field is visible"""
        try:
            return self.textbox_phone.is_visible()
        except Exception as e:
            logger.error(f"Error checking phone visibility: {e}")
            return False
    
    @log_function(log_timing=True)
    def is_next_button_visible(self) -> bool:
        """Check if Next button is visible"""
        try:
            return self.button_next.is_visible()
        except Exception as e:
            logger.error(f"Error checking next button visibility: {e}")
            return False    
    @log_function(log_timing=True)
    def is_next_button_enabled(self) -> bool:
        """Check if next button is enabled (not disabled)"""
        try:
            return self.button_next.is_enabled()
        except Exception as e:
            logger.error(f"Error checking next button enabled state: {e}")
            return False