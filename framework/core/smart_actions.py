"""
Smart Actions - Context-Aware Automation Layer
===============================================
Reusable intelligent action wrappers that automatically apply
context-aware delays based on action type.

This eliminates manual delay calls throughout test code!

Usage:
    from framework.core.smart_actions import SmartActions
    
    actions = SmartActions(page, enable_human=True)
    actions.type_text(element, "text", "Field Name")
    actions.click(element, "Button Name")

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com
"""

import random
import time
from typing import Any, Callable, Optional, Tuple, TypeVar

from playwright.sync_api import Locator, Page

T = TypeVar("T")


class SmartActions:
    """Intelligent action wrappers with automatic context-aware delays.

    All delays are automatically applied based on action context:
    - Click: 0.3-0.7s before, 0.2-0.4s after
    - Type: 0.3-0.6s before, 0.2-0.5s after
    - Button: 0.4-0.9s before, 0.3-0.6s after
    - Navigate: 0.4-0.8s before, 0.5-1.0s after
    """
    
    def __init__(self, page: Page, enable_human: bool = False, verbose: bool = False):
        """Initialize SmartActions.

        Args:
            page: Playwright Page object
            enable_human: Enable human-like delays
            verbose: Print delay information
        """
        self.page = page
        self.enable_human = enable_human
        self.verbose = verbose
    
    def _delay(self, min_sec: float, max_sec: float, context: str = "") -> None:
        """Internal delay with optional logging."""
        if self.enable_human:
            delay_time = random.uniform(min_sec, max_sec)
            time.sleep(delay_time)
            if self.verbose and context:
                print(f"   ⏱️  {context}: {delay_time:.2f}s")
    
    def click(self, element: Locator, description: str = "") -> None:
        """Click element with automatic delays.

        Auto-applies:
        - 0.3-0.7s before (thinking)
        - 0.2-0.4s after (confirmation)
        """
        self._delay(0.3, 0.7, f"Before click: {description}")
        element.click()
        self._delay(0.2, 0.4, f"After click: {description}")
    
    def type_text(self, element: Locator, text: str, field_name: str = "") -> None:
        """Type text with context-aware speed.

        Auto-applies:
        - 0.3-0.6s before (preparation)
        - Context-aware typing speed:
          * Numbers: 0.08-0.18s per char
          * Email: 0.12-0.25s per char
          * Dates: 0.10-0.22s per char
          * Text: 0.10-0.23s per char
        - 0.2-0.5s after (review)
        """
        self._delay(0.3, 0.6, f"Before type: {field_name}")
        
        # Wait for element to be visible and enabled
        try:
            element.wait_for(state="visible", timeout=10000)
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Warning: Element not immediately visible for '{field_name}', retrying...")
            time.sleep(0.5)
            element.wait_for(state="visible", timeout=10000)
        
        if self.enable_human:
            text_str = str(text)
            is_numeric = text_str.replace('-', '').replace(' ', '').replace('.', '').isdigit()
            is_email = '@' in text_str
            is_date = '/' in text_str and len(text_str.split('/')) == 3
            
            # Determine typing speed based on content type
            if is_numeric:
                delay_ms = random.uniform(80, 180)
            elif is_email:
                delay_ms = random.uniform(120, 250)
            elif is_date:
                delay_ms = random.uniform(100, 220)
            else:
                delay_ms = random.uniform(100, 230)
            
            # Use press_sequentially for more reliable character-by-character typing
            # This is more stable than element.type() in a loop as it handles element state better
            element.press_sequentially(text_str, delay=delay_ms)
        else:
            element.fill(str(text))
        
        self._delay(0.2, 0.5, f"After type: {field_name}")
    
    def button_click(self, element: Locator, button_name: str = "", wait_processing: bool = False) -> None:
        """Button click with extra consideration time.

        Auto-applies:
        - 0.4-0.9s before (considering)
        - 0.3-0.6s after (confirmation)
        - 1.5-2.5s after if wait_processing=True (for Submit, Send Code, Verify buttons)

        Args:
            element: Button locator
            button_name: Description of button
            wait_processing: Add extra delay for processing (Submit, Verify, Send Code)
        """
        self._delay(0.4, 0.9, f"Before button: {button_name}")
        element.click()
        
        # Context-aware post-click delay
        if wait_processing or any(keyword in button_name.lower() for keyword in ['send', 'verify', 'submit', 'code']):
            self._delay(1.5, 2.5, f"Processing: {button_name}")
        else:
            self._delay(0.3, 0.6, f"After button: {button_name}")
    
    def navigate(self, url: str, page_name: str = "", wait_transition: bool = False) -> None:
        """Navigate with page observation.

        Auto-applies:
        - 0.4-0.8s before (decision)
        - 0.5-1.0s after (observation)
        - 0.8-1.5s after if wait_transition=True (for page transitions)

        Args:
            url: URL to navigate to
            page_name: Description of page
            wait_transition: Add extra delay for page transition
        """
        self._delay(0.4, 0.8, f"Navigating to: {page_name}")
        self.page.goto(url)
        
        if wait_transition:
            self._delay(0.8, 1.5, f"Page transition: {page_name}")
        else:
            self._delay(0.5, 1.0, f"Observing: {page_name}")
    
    def wait_for_page_ready(self, context: str = "") -> None:
        """Wait for page to be ready with network idle check.

        Auto-applies:
        - Network idle wait (15s timeout)
        - 0.8-1.5s observation delay

        Args:
            context: Description for logging
        """
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
        except:
            pass
        self._delay(0.8, 1.5, f"Page ready: {context}")
    
    def select_option(self, dropdown: Locator, option: Locator, field_name: str = "") -> None:
        """Select dropdown option with delays.

        Auto-applies:
        - 0.3-0.6s before opening
        - 0.2-0.4s reviewing options
        - 0.2-0.4s after selection
        """
        self._delay(0.3, 0.6, f"Opening dropdown: {field_name}")
        dropdown.click()
        self._delay(0.2, 0.4, "Reviewing options")
        option.click()
        self._delay(0.2, 0.4, f"Selected: {field_name}")
    
    def wait_autocomplete(self, pattern: str, description: str = "", timeout: int = 6000) -> bool:
        """Smart autocomplete handling with timeout.

        Args:
            pattern: Locator pattern for autocomplete
            description: Description for logging
            timeout: Timeout in milliseconds (default 6000)

        Returns:
            True if autocomplete found and clicked, False otherwise
        """
        try:
            element = self.page.locator(pattern).first
            element.wait_for(state="visible", timeout=timeout)
            self._delay(0.3, 0.6, f"Reviewing autocomplete: {description}")
            element.click()
            print(f"✓ Autocomplete selected: {description}")
            return True
        except:
            print(f"⚠ Autocomplete timeout ({timeout/1000}s) - continuing")
            self._delay(0.2, 0.3)
            return False
    
    def wait_and_click(self, locator: Locator, description: str = "", timeout: int = 30000) -> bool:
        """Wait for element and click with smart delays.

        Args:
            locator: Playwright locator
            description: Description for logging
            timeout: Timeout in milliseconds
        """
        try:
            locator.wait_for(state="visible", timeout=timeout)
            self.click(locator, description)
            return True
        except Exception as e:
            print(f"⚠ Element not found: {description} - {type(e).__name__}")
            return False
    
    def wait_for_scheduler(self, context: str = "Scheduler") -> None:
        """Wait for scheduler/calendar to load.

        Auto-applies:
        - 1.5-2.5s loading delay (for dynamic content like time slots)

        Args:
            context: Description for logging
        """
        self._delay(1.5, 2.5, f"{context} loading")
    
    def wait_for_processing(self, context: str = "Processing", short: bool = False) -> None:
        """Wait for processing operations.

        Auto-applies:
        - 1.0-2.0s for verification/processing (short=True)
        - 1.5-2.5s for submission/heavy processing (short=False)

        Args:
            context: Description for logging
            short: Use shorter delay for lighter operations
        """
        if short:
            self._delay(1.0, 2.0, f"{context}")
        else:
            self._delay(1.5, 2.5, f"{context}")
    
    def smart_retry(
        self,
        action_func: Callable[[], T],
        max_retries: int = 3,
        delay_between: Tuple[float, float] = (1.0, 2.0)
    ) -> Optional[T]:
        """Retry an action with smart delays.

        Args:
            action_func: Function to retry
            max_retries: Maximum retry attempts
            delay_between: Delay range between retries

        Returns:
            Result of action_func or None if all retries fail
        """
        for attempt in range(max_retries):
            try:
                result = action_func()
                print(f"✓ Action succeeded on attempt {attempt + 1}")
                return result
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠ Attempt {attempt + 1} failed: {type(e).__name__} - Retrying...")
                    self._delay(delay_between[0], delay_between[1], "Retry delay")
                else:
                    print(f"❌ All {max_retries} attempts failed")
                    raise
        return None
