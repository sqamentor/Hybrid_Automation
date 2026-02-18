"""
Page Object: Bookslot Personal Info Page
Represents what a user can do on the Personal Info page

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

Project: BookSlot
Module: Personal Information (Demographics)

Responsibilities:
✔ Locators for personal info fields
✔ Actions (fill fields, select gender, address)
✔ Page-level checks
✔ Navigation

Does NOT contain:
❌ Test data
❌ Business rule assertions
❌ API/DB validation
❌ pytest markers
❌ Complete test flows
"""

from framework.ui.base_page import BasePage


class BookslotPersonalInfoPage(BasePage):
    """
    Page Object for Bookslot Personal Info
    
    What a user can do on this page:
    - Navigate to personal info page
    - Select gender
    - Fill date of birth
    - Fill address with autocomplete
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
        self.page = self.driver  # Compatibility alias
        if not base_url:
            raise ValueError("base_url is required from multi_project_config")
        self.base_url = base_url
        self.path = "/personal-info"

    # ===================================================================
    # LOCATORS
    # ===================================================================
    
    @property
    def combobox_gender(self):
        """Gender selection dropdown"""
        return self.page.get_by_role("combobox", name="Select Gender")
    
    @property
    def option_male(self):
        """Male gender option"""
        return self.page.get_by_role("option", name="MALE", exact=True)
    
    @property
    def option_female(self):
        """Female gender option"""
        return self.page.get_by_role("option", name="FEMALE", exact=True)
    
    @property
    def combobox_dob(self):
        """Date of Birth field"""
        return self.page.get_by_role("combobox", name="mm/dd/yyyy")
    
    @property
    def textbox_address(self):
        """Address input field"""
        return self.page.get_by_role("textbox", name="Address")
    
    @property
    def textbox_city(self):
        """City input field"""
        return self.page.get_by_role("textbox", name="City")
    
    @property
    def textbox_state(self):
        """State input field"""
        return self.page.get_by_role("textbox", name="State")
    
    @property
    def textbox_zip(self):
        """Zip Code input field"""
        return self.page.get_by_role("textbox", name="Zip Code")
    
    @property
    def autocomplete_suggestions(self):
        """Address autocomplete suggestions"""
        return self.page.locator("text=/Highmore|USA|SD/")
    
    @property
    def button_next(self):
        """Next button"""
        return self.page.get_by_role("button", name="Next")

    # ===================================================================
    # NAVIGATION
    # ===================================================================
    
    def navigate(self):
        """Navigate to the personal info page"""
        url = f"{self.base_url}{self.path}"
        self.page.goto(url)
        return self

    # ===================================================================
    # ACTIONS
    # ===================================================================
    
    def select_gender_male(self):
        """Select MALE gender"""
        self.combobox_gender.click()
        self.option_male.click()
        return self
    
    def select_gender_female(self):
        """Select FEMALE gender"""
        self.combobox_gender.click()
        self.option_female.click()
        return self
    
    def fill_dob(self, dob: str):
        """Fill date of birth (format: MM/DD/YYYY)"""
        self.combobox_dob.click()
        self.combobox_dob.fill(dob)
        return self
    
    def fill_address(self, address: str):
        """Fill address field"""
        self.textbox_address.click()
        self.textbox_address.fill(address)
        return self
    
    def fill_city(self, city: str):
        """Fill city field"""
        self.textbox_city.click()
        self.textbox_city.fill(city)
        return self
    
    def fill_state(self, state: str):
        """Fill state field"""
        self.textbox_state.click()
        self.textbox_state.fill(state)
        return self
    
    def fill_zip(self, zip_code: str):
        """Fill zip code field"""
        self.textbox_zip.click()
        self.textbox_zip.fill(zip_code)
        return self
    
    def select_address_autocomplete(self):
        """Click first address autocomplete suggestion"""
        self.autocomplete_suggestions.first.click()
        return self
    
    def fill_address_with_autocomplete(self, zip_code: str):
        """
        Fill address using zip code and select autocomplete
        
        Args:
            zip_code: Zip code to trigger autocomplete
        """
        self.fill_address(zip_code)
        if self.is_autocomplete_visible():
            self.select_address_autocomplete()
        return self
    
    def get_dob_value(self) -> str:
        """Get current DOB field value"""
        return self.combobox_dob.input_value()
    
    def get_address_value(self) -> str:
        """Get current address field value"""
        return self.textbox_address.input_value()
    
    def get_city_value(self) -> str:
        """Get current city field value"""
        return self.textbox_city.input_value()
    
    def get_state_value(self) -> str:
        """Get current state field value"""
        return self.textbox_state.input_value()
    
    def get_zip_value(self) -> str:
        """Get current zip field value"""
        return self.textbox_zip.input_value()
    
    def clear_address(self):
        """Clear address field"""
        self.textbox_address.clear()
        return self
    
    def clear_city(self):
        """Clear city field"""
        self.textbox_city.clear()
        return self
    
    def proceed_to_next(self):
        """Click Next button"""
        self.button_next.click()
        return self

    # ===================================================================
    # PAGE-LEVEL CHECKS
    # ===================================================================
    
    def is_page_loaded(self) -> bool:
        """Check if page is loaded"""
        try:
            return self.combobox_gender.is_visible()
        except:
            return False
    
    def is_gender_field_visible(self) -> bool:
        """Check if gender field is visible (no wait logic)"""
        try:
            return self.combobox_gender.is_visible()
        except:
            return False
    
    def is_autocomplete_visible(self) -> bool:
        """Check if address autocomplete suggestions are visible"""
        try:
            return self.autocomplete_suggestions.is_visible()
        except:
            return False
