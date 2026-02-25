"""
Bookslot Validation Helper

Provides common validation methods for all pages.
Implements component validation checks as per Test Design Matrix:

For every interactive component:
1. Visible: element is rendered and visible
2. Enabled/Clickable: user can click/select/focus
3. Input behavior: accepts valid values
4. Validation behavior: rejects invalid/empty when required
5. State behavior: selected/unselected, checked/unchecked
6. Navigation effect: Next/Back causes expected transition

Usage:
    validator = BookslotValidationHelper(page)
    validator.validate_element_visible("button", "Next")
    validator.validate_required_field("email", "Email is required")
"""

from playwright.sync_api import Page, expect, Locator
from typing import List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class BookslotValidationHelper:
    """
    Validation helper for common assertions across Bookslot pages.
    Provides reusable validation methods to reduce code duplication.
    """
    
    def __init__(self, page: Page):
        """
        Initialize validation helper.
        
        Args:
            page: Playwright Page object
        """
        self.page = page
    
    # ========================================================================
    # VISIBILITY VALIDATIONS
    # ========================================================================
    
    def validate_element_visible(
        self, 
        selector: str, 
        description: str = None,
        timeout: int = 10000
    ) -> None:
        """
        Validate that element is visible.
        
        Args:
            selector: CSS selector or text selector
            description: Human-readable description for logging
            timeout: Timeout in milliseconds
        
        Raises:
            AssertionError if element not visible
        """
        desc = description or selector
        logger.debug(f"Validating '{desc}' is visible")
        expect(self.page.locator(selector).first).to_be_visible(timeout=timeout)
        logger.debug(f"✓ '{desc}' is visible")
    
    def validate_elements_visible(self, elements: List[tuple]) -> None:
        """
        Validate multiple elements are visible.
        
        Args:
            elements: List of (selector, description) tuples
        
        Example:
            validate_elements_visible([
                ("[name='firstName']", "First Name field"),
                ("[name='lastName']", "Last Name field"),
            ])
        """
        for selector, description in elements:
            self.validate_element_visible(selector, description)
    
    def validate_element_not_visible(
        self, 
        selector: str, 
        description: str = None,
        timeout: int = 5000
    ) -> None:
        """
        Validate that element is NOT visible.
        
        Args:
            selector: CSS selector
            description: Human-readable description
            timeout: Timeout in milliseconds
        """
        desc = description or selector
        logger.debug(f"Validating '{desc}' is NOT visible")
        expect(self.page.locator(selector)).to_be_hidden(timeout=timeout)
        logger.debug(f"✓ '{desc}' is NOT visible")
    
    # ========================================================================
    # ENABLED/CLICKABLE VALIDATIONS
    # ========================================================================
    
    def validate_element_enabled(
        self, 
        selector: str, 
        description: str = None
    ) -> None:
        """
        Validate that element is enabled (not disabled).
        
        Args:
            selector: CSS selector
            description: Human-readable description
        """
        desc = description or selector
        logger.debug(f"Validating '{desc}' is enabled")
        expect(self.page.locator(selector)).to_be_enabled()
        logger.debug(f"✓ '{desc}' is enabled")
    
    def validate_element_disabled(
        self, 
        selector: str, 
        description: str = None
    ) -> None:
        """
        Validate that element is disabled.
        
        Args:
            selector: CSS selector
            description: Human-readable description
        """
        desc = description or selector
        logger.debug(f"Validating '{desc}' is disabled")
        expect(self.page.locator(selector)).to_be_disabled()
        logger.debug(f"✓ '{desc}' is disabled")
    
    def validate_button_clickable(
        self, 
        button_text: str
    ) -> None:
        """
        Validate that button is visible and enabled (clickable).
        
        Args:
            button_text: Text on button
        """
        selector = f"button:has-text('{button_text}')"
        self.validate_element_visible(selector, f"{button_text} button")
        self.validate_element_enabled(selector, f"{button_text} button")
    
    # ========================================================================
    # INPUT BEHAVIOR VALIDATIONS
    # ========================================================================
    
    def validate_input_accepts_value(
        self, 
        selector: str, 
        value: str,
        description: str = None
    ) -> None:
        """
        Validate that input field accepts a value.
        
        Args:
            selector: CSS selector for input
            value: Value to enter
            description: Human-readable description
        """
        desc = description or selector
        logger.debug(f"Validating '{desc}' accepts value: {value}")
        
        self.page.fill(selector, value)
        actual_value = self.page.input_value(selector)
        
        assert actual_value == value, f"{desc} did not accept value. Expected: {value}, Got: {actual_value}"
        logger.debug(f"✓ '{desc}' accepted value: {value}")
    
    def validate_input_max_length(
        self, 
        selector: str, 
        max_length: int,
        description: str = None
    ) -> None:
        """
        Validate that input field respects max length.
        
        Args:
            selector: CSS selector for input
            max_length: Expected maximum length
            description: Human-readable description
        """
        desc = description or selector
        logger.debug(f"Validating '{desc}' max length: {max_length}")
        
        # Try to enter more characters than max_length
        test_value = "A" * (max_length + 10)
        self.page.fill(selector, test_value)
        actual_value = self.page.input_value(selector)
        
        assert len(actual_value) <= max_length, \
            f"{desc} exceeded max length. Max: {max_length}, Got: {len(actual_value)}"
        logger.debug(f"✓ '{desc}' respects max length: {max_length}")
    
    # ========================================================================
    # VALIDATION MESSAGE CHECKS
    # ========================================================================
    
    def validate_error_message_shown(
        self, 
        expected_message: str,
        selector: str = None
    ) -> None:
        """
        Validate that error message is shown.
        
        Args:
            expected_message: Expected error message text (partial match)
            selector: Optional specific selector for error message
        """
        logger.debug(f"Validating error message contains: '{expected_message}'")
        
        if selector:
            error_locator = self.page.locator(selector)
        else:
            # Look for common error message patterns
            error_locator = self.page.locator(
                "[class*='error'], [class*='invalid'], [role='alert']"
            )
        
        expect(error_locator).to_contain_text(expected_message, timeout=5000)
        logger.debug(f"✓ Error message shown: '{expected_message}'")
    
    def validate_no_error_messages(self) -> None:
        """
        Validate that no error messages are displayed.
        """
        logger.debug("Validating no error messages are shown")
        
        error_selectors = [
            "[class*='error']:visible",
            "[class*='invalid']:visible",
            "[role='alert']:visible"
        ]
        
        for selector in error_selectors:
            error_elements = self.page.locator(selector).count()
            assert error_elements == 0, f"Found {error_elements} error messages when none expected"
        
        logger.debug("✓ No error messages shown")
    
    def validate_required_field_error(
        self, 
        field_name: str,
        error_message: str = "required"
    ) -> None:
        """
        Validate that required field shows error when empty.
        
        Args:
            field_name: Name attribute or label of field
            error_message: Expected error message (partial match)
        """
        logger.debug(f"Validating required field error for: {field_name}")
        self.validate_error_message_shown(error_message)
    
    # ========================================================================
    # STATE VALIDATIONS (Radio, Checkbox, Select)
    # ========================================================================
    
    def validate_radio_selected(
        self, 
        selector: str,
        description: str = None
    ) -> None:
        """
        Validate that radio button is selected.
        
        Args:
            selector: CSS selector for radio button
            description: Human-readable description
        """
        desc = description or selector
        logger.debug(f"Validating '{desc}' is selected")
        expect(self.page.locator(selector)).to_be_checked()
        logger.debug(f"✓ '{desc}' is selected")
    
    def validate_radio_not_selected(
        self, 
        selector: str,
        description: str = None
    ) -> None:
        """
        Validate that radio button is NOT selected.
        
        Args:
            selector: CSS selector for radio button
            description: Human-readable description
        """
        desc = description or selector
        logger.debug(f"Validating '{desc}' is NOT selected")
        expect(self.page.locator(selector)).not_to_be_checked()
        logger.debug(f"✓ '{desc}' is NOT selected")
    
    def validate_checkbox_checked(
        self, 
        selector: str,
        description: str = None
    ) -> None:
        """
        Validate that checkbox is checked.
        
        Args:
            selector: CSS selector for checkbox
            description: Human-readable description
        """
        desc = description or selector
        logger.debug(f"Validating '{desc}' is checked")
        expect(self.page.locator(selector)).to_be_checked()
        logger.debug(f"✓ '{desc}' is checked")
    
    def validate_dropdown_value(
        self, 
        selector: str, 
        expected_value: str,
        description: str = None
    ) -> None:
        """
        Validate that dropdown has expected value selected.
        
        Args:
            selector: CSS selector for dropdown
            expected_value: Expected selected value
            description: Human-readable description
        """
        desc = description or selector
        logger.debug(f"Validating '{desc}' has value: {expected_value}")
        
        actual_value = self.page.locator(selector).input_value()
        assert actual_value == expected_value, \
            f"{desc} value mismatch. Expected: {expected_value}, Got: {actual_value}"
        logger.debug(f"✓ '{desc}' has correct value: {expected_value}")
    
    def validate_radio_group_single_selection(
        self, 
        radio_group_selector: str,
        description: str = None
    ) -> None:
        """
        Validate that radio group allows only single selection.
        
        Args:
            radio_group_selector: Selector for all radios in group
            description: Human-readable description
        """
        desc = description or "radio group"
        logger.debug(f"Validating '{desc}' single-select behavior")
        
        # Count how many are checked
        checked_count = self.page.locator(f"{radio_group_selector}:checked").count()
        
        assert checked_count <= 1, \
            f"{desc} has {checked_count} selected, expected 0 or 1"
        logger.debug(f"✓ '{desc}' has single-select behavior")
    
    # ========================================================================
    # NAVIGATION VALIDATIONS
    # ========================================================================
    
    def validate_page_url(
        self, 
        expected_url_part: str,
        description: str = None
    ) -> None:
        """
        Validate that current URL contains expected part.
        
        Args:
            expected_url_part: Expected substring in URL
            description: Human-readable description
        """
        desc = description or expected_url_part
        logger.debug(f"Validating URL contains: '{desc}'")
        
        current_url = self.page.url
        assert expected_url_part in current_url, \
            f"URL does not contain '{expected_url_part}'. Current URL: {current_url}"
        logger.debug(f"✓ URL contains: '{desc}'")
    
    def validate_page_title(
        self, 
        expected_title: str
    ) -> None:
        """
        Validate page title (partial match).
        
        Args:
            expected_title: Expected title text (partial match)
        """
        logger.debug(f"Validating page title contains: '{expected_title}'")
        expect(self.page).to_have_title(expected_title)
        logger.debug(f"✓ Page title contains: '{expected_title}'")
    
    def validate_navigation_to(
        self, 
        page_identifier: str
    ) -> None:
        """
        Validate successful navigation to a specific page.
        
        Args:
            page_identifier: Unique identifier for page (h1 text, URL part, etc.)
        """
        logger.debug(f"Validating navigation to: '{page_identifier}'")
        
        # Check for page heading
        heading = self.page.locator("h1").first
        expect(heading).to_contain_text(page_identifier, timeout=10000)
        logger.debug(f"✓ Navigated to: '{page_identifier}'")
    
    # ========================================================================
    # TEXT & CONTENT VALIDATIONS
    # ========================================================================
    
    def validate_text_present(
        self, 
        text: str,
        description: str = None
    ) -> None:
        """
        Validate that text is present on page.
        
        Args:
            text: Text to find
            description: Human-readable description
        """
        desc = description or text
        logger.debug(f"Validating text present: '{desc}'")
        expect(self.page.locator(f"text={text}")).to_be_visible()
        logger.debug(f"✓ Text present: '{desc}'")
    
    def validate_text_not_present(
        self, 
        text: str,
        description: str = None
    ) -> None:
        """
        Validate that text is NOT present on page.
        
        Args:
            text: Text that should not be present
            description: Human-readable description
        """
        desc = description or text
        logger.debug(f"Validating text NOT present: '{desc}'")
        expect(self.page.locator(f"text={text}")).to_be_hidden()
        logger.debug(f"✓ Text NOT present: '{desc}'")
    
    # ========================================================================
    # COMPONENT COUNT VALIDATIONS
    # ========================================================================
    
    def validate_element_count(
        self, 
        selector: str, 
        expected_count: int,
        description: str = None
    ) -> None:
        """
        Validate that exactly N elements match selector.
        
        Args:
            selector: CSS selector
            expected_count: Expected number of elements
            description: Human-readable description
        """
        desc = description or selector
        logger.debug(f"Validating '{desc}' count: {expected_count}")
        
        expect(self.page.locator(selector)).to_have_count(expected_count)
        logger.debug(f"✓ '{desc}' count is {expected_count}")
    
    def validate_minimum_element_count(
        self, 
        selector: str, 
        minimum_count: int,
        description: str = None
    ) -> None:
        """
        Validate that at least N elements match selector.
        
        Args:
            selector: CSS selector
            minimum_count: Minimum expected count
            description: Human-readable description
        """
        desc = description or selector
        logger.debug(f"Validating '{desc}' minimum count: {minimum_count}")
        
        actual_count = self.page.locator(selector).count()
        assert actual_count >= minimum_count, \
            f"{desc} count too low. Expected >= {minimum_count}, Got: {actual_count}"
        logger.debug(f"✓ '{desc}' count ({actual_count}) meets minimum: {minimum_count}")
