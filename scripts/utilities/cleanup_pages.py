"""Clean up page files to follow proper POM standards."""

# Personal Info Page
personal_info_content = '''"""
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

from playwright.sync_api import Page, expect


class BookslotPersonalInfoPage:
    """
    Page Object for Bookslot Personal Info
    
    What a user can do on this page:
    - Navigate to personal info page
    - Select gender
    - Fill date of birth
    - Fill address with autocomplete
    - Proceed to next page
    """

    def __init__(self, page: Page, base_url: str):
        """
        Initialize page object
        
        Args:
            page: Playwright Page instance
            base_url: Base URL from multi_project_config
        """
        self.page = page
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
    
    def select_address_autocomplete(self):
        """Click first address autocomplete suggestion"""
        self.autocomplete_suggestions.first.click()
        return self
    
    def fill_address_with_autocomplete(self, zip_code: str, timeout: int = 6000):
        """
        Fill address using zip code and wait for autocomplete
        
        Args:
            zip_code: Zip code to trigger autocomplete
            timeout: How long to wait for suggestions
        """
        self.fill_address(zip_code)
        try:
            self.autocomplete_suggestions.wait_for(state="visible", timeout=timeout)
            self.select_address_autocomplete()
        except:
            pass  # Autocomplete might not appear
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
            self.combobox_gender.wait_for(state="visible", timeout=5000)
            return True
        except:
            return False
    
    def wait_for_page_ready(self, timeout: int = 10000):
        """Wait for page to be ready"""
        self.combobox_gender.wait_for(state="visible", timeout=timeout)
        return self
    
    def is_autocomplete_visible(self) -> bool:
        """Check if address autocomplete suggestions are visible"""
        try:
            expect(self.autocomplete_suggestions).to_be_visible()
            return True
        except:
            return False
'''

# Write the file
with open(r"C:\Users\LokendraSingh\Documents\GitHub\Automation\pages\bookslot\bookslots_personalInfo_page4.py", "w", encoding="utf-8") as f:
    f.write(personal_info_content)

print("✓ bookslots_personalInfo_page4.py cleaned")
