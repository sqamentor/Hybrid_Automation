"""
Page Object: Bookslot Referral Source Page
Represents what a user can do on the Referral page

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

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

from playwright.sync_api import Page


class BookslotReferralPage:
    """Page Object for Bookslot Referral Source.

    What a user can do on this page:
    - Navigate to referral page
    - Read "How did you hear about us?" question
    - Select referral source (Physician, Online, Social Media, etc.)
    - Proceed to next page
    """

    def __init__(self, page: Page, base_url: str):
        """Initialize page object.

        Args:
            page: Playwright Page instance
            base_url: Base URL from multi_project_config
        """
        self.page = page
        if not base_url:
            raise ValueError("base_url is required from multi_project_config")
        self.base_url = base_url
        self.path = "/referral"
    
    # ===================================================================
    # LOCATORS
    # ===================================================================
    
    @property
    def heading_question(self):
        """How did you hear about us heading."""
        return self.page.get_by_role("heading", name="How did you hear about us?")
    
    @property
    def button_physician(self):
        """Referred by physician button."""
        return self.page.get_by_role("button", name="Referred by physician")
    
    @property
    def radio_online(self):
        """Online search radio button."""
        return self.page.get_by_role("radio", name="Online search")
    
    @property
    def radio_social_media(self):
        """Social media radio button."""
        return self.page.get_by_role("radio", name="Social media")
    
    @property
    def radio_friend_family(self):
        """Friend or family radio button."""
        return self.page.get_by_role("radio", name="Friend or family")
    
    @property
    def radio_advertisement(self):
        """Advertisement radio button."""
        return self.page.get_by_role("radio", name="Advertisement")
    
    @property
    def button_next(self):
        """Next button."""
        return self.page.get_by_role("button", name="Next")
    
    # ===================================================================
    # NAVIGATION
    # ===================================================================
    
    def navigate(self):
        """Navigate to the referral page."""
        url = f"{self.base_url}{self.path}"
        self.page.goto(url)
        return self
    
    # ===================================================================
    # ACTIONS
    # ===================================================================
    
    def select_physician(self):
        """Select Referred by physician."""
        self.heading_question.click()
        self.button_physician.click()
        return self
    
    def select_online(self):
        """Select Online search."""
        self.radio_online.click()
        return self
    
    def select_social_media(self):
        """Select Social media."""
        self.radio_social_media.click()
        return self
    
    def select_friend_family(self):
        """Select Friend or family."""
        self.radio_friend_family.click()
        return self
    
    def select_advertisement(self):
        """Select Advertisement."""
        self.radio_advertisement.click()
        return self
    
    def proceed_to_next(self):
        """Click Next button."""
        self.button_next.click()
        return self
    
    def is_online_checked(self) -> bool:
        """Check if online search radio is checked."""
        try:
            return self.radio_online.is_checked()
        except:
            return False
    
    def is_physician_checked(self) -> bool:
        """Check if physician radio is checked."""
        try:
            return self.button_physician.is_checked()
        except:
            return False
    
    def is_social_media_checked(self) -> bool:
        """Check if social media radio is checked."""
        try:
            return self.radio_social_media.is_checked()
        except:
            return False
    
    def is_friend_family_checked(self) -> bool:
        """Check if friend/family radio is checked."""
        try:
            return self.radio_friend_family.is_checked()
        except:
            return False
    
    # ===================================================================
    # PAGE-LEVEL CHECKS
    # ===================================================================
    
    def is_page_loaded(self) -> bool:
        """Check if page is loaded."""
        try:
            return self.heading_question.is_visible()
        except:
            return False
    
    def is_question_visible(self) -> bool:
        """Check if referral question is visible (no wait logic)"""
        try:
            return self.heading_question.is_visible()
        except:
            return False


