"""
PatientIntake Verification Page Object

This Page Object provides methods for verifying authenticated access
to the PatientIntake application during cross-engine workflows.

Author: Principal QA Architect
Date: January 31, 2026
"""

from framework.ui.base_page import BasePage


class PatientIntakeVerificationPage(BasePage):
    """Page Object for PatientIntake verification in workflows"""
    
    def __init__(self, page):
        """
        Initialize PatientIntake verification page
        
        Args:
            page: Playwright Page or Selenium WebDriver instance
        """
        super().__init__(page)
        self.page = self.driver  # Compatibility alias
        self.base_url = None
        
        # Selectors
        self.user_menu_selector = "[data-testid='user-menu'], .user-profile, #user-menu"
    
    def navigate_to(self, url: str) -> 'PatientIntakeVerificationPage':
        """
        Navigate to PatientIntake URL
        
        Args:
            url: PatientIntake application URL
            
        Returns:
            Self for method chaining
        """
        self.base_url = url
        self.page.goto(url, wait_until='networkidle')
        return self
    
    def get_current_url(self) -> str:
        """
        Get current page URL
        
        Returns:
            Current URL as string
        """
        return self.page.url
    
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated (not redirected to login)
        
        Returns:
            True if authenticated, False if redirected to login
        """
        current_url = self.get_current_url()
        return 'login' not in current_url.lower()
    
    def has_user_menu(self) -> bool:
        """
        Check if user menu is visible (authentication indicator)
        
        Returns:
            True if user menu found, False otherwise
        """
        try:
            user_element = self.page.query_selector(self.user_menu_selector)
            return user_element is not None
        except Exception:
            return False
    
    def get_page_title(self) -> str:
        """
        Get current page title
        
        Returns:
            Page title as string
        """
        return self.page.title()
    
    def verify_authenticated_access(self) -> bool:
        """
        Verify authenticated access to PatientIntake application
        
        Checks:
        - Not redirected to login page
        - User menu is visible
        
        Returns:
            True if all checks pass, False otherwise
        """
        if not self.is_authenticated():
            return False
        
        # Give a moment for UI to load
        try:
            self.page.wait_for_selector(self.user_menu_selector, timeout=5000)
            return True
        except Exception:
            return False
    
    def get_verification_details(self) -> dict:
        """
        Get comprehensive verification details
        
        Returns:
            Dict with verification status, URL, title, and indicators
        """
        return {
            'is_authenticated': self.is_authenticated(),
            'has_user_menu': self.has_user_menu(),
            'current_url': self.get_current_url(),
            'page_title': self.get_page_title()
        }
