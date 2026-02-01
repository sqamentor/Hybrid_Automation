"""
Playwright Engine Implementation

Modern UI automation engine using Playwright for Python.

Features:
- Enhanced error handling for browser startup failures
- Browser context pooling for parallel execution
- Automatic retry on transient failures
- Resource cleanup and management
"""

import threading
import time
from queue import Empty, Queue
from typing import Any, Dict, List, Optional

from playwright.sync_api import Browser, BrowserContext
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, sync_playwright

from framework.ui.base_page import BasePage
from utils.logger import get_audit_logger, get_logger

logger = get_logger(__name__)
audit_logger = get_audit_logger()


class BrowserStartupError(Exception):
    """Custom exception for browser startup failures"""
    pass


class ContextPoolExhausted(Exception):
    """Exception when context pool has no available contexts"""
    pass


class PlaywrightEngine:
    """
    Playwright browser engine with enhanced error handling and context pooling
    
    Features:
    - Automatic retry on browser startup failures
    - Browser context pooling for parallel execution
    - Comprehensive error handling
    - Resource cleanup
    """
    
    def __init__(
        self,
        headless: bool = True,
        slow_mo: int = 0,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        enable_context_pool: bool = False,
        pool_size: int = 5
    ):
        """
        Initialize Playwright Engine
        
        Args:
            headless: Run browser in headless mode
            slow_mo: Slow down operations by milliseconds
            max_retries: Maximum retry attempts for browser startup
            retry_delay: Delay between retries in seconds
            enable_context_pool: Enable browser context pooling
            pool_size: Number of contexts in the pool
        """
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.headless = headless
        self.slow_mo = slow_mo
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Context pooling
        self.enable_context_pool = enable_context_pool
        self.pool_size = pool_size
        self.context_pool: Optional['ContextPool'] = None
        self._pool_context: Optional[BrowserContext] = None
    
    def start(self, browser_type: str = "chromium"):
        """
        Start Playwright browser with enhanced error handling
        
        Args:
            browser_type: Browser type ('chromium', 'firefox', 'webkit')
        
        Raises:
            BrowserStartupError: If browser fails to start after retries
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Starting Playwright {browser_type} (attempt {attempt + 1}/{self.max_retries})")
                
                # Start Playwright
                self.playwright = sync_playwright().start()
                logger.debug("Playwright runtime started")
                
                # Get browser launcher
                if not hasattr(self.playwright, browser_type):
                    raise BrowserStartupError(f"Unsupported browser type: {browser_type}")
                
                browser_launcher = getattr(self.playwright, browser_type)
                
                # Launch browser with timeout
                try:
                    self.browser = browser_launcher.launch(
                        headless=self.headless,
                        slow_mo=self.slow_mo,
                        timeout=30000  # 30 second timeout
                    )
                    logger.debug(f"Browser launched successfully")
                except PlaywrightError as e:
                    if "Executable doesn't exist" in str(e):
                        raise BrowserStartupError(
                            f"Browser not installed. Run: playwright install {browser_type}"
                        )
                    raise
                
                # Initialize context pool or single context
                if self.enable_context_pool:
                    self.context_pool = ContextPool(
                        browser=self.browser,
                        pool_size=self.pool_size,
                        headless=self.headless
                    )
                    # Get a context from pool for this instance
                    self._pool_context = self.context_pool.acquire_context()
                    self.context = self._pool_context
                    logger.info(f"Context pool initialized with {self.pool_size} contexts")
                else:
                    # Create single context
                    self.context = self._create_context()
                    logger.debug("Single browser context created")
                
                # Create page
                self.page = self.context.new_page()
                logger.debug("Page created")
                
                logger.info(f"Playwright {browser_type} started successfully (headless={self.headless})")
                return  # Success!
                
            except PlaywrightError as e:
                last_error = e
                logger.error(f"Playwright error on attempt {attempt + 1}: {str(e)}")
                
                # Clean up on failure
                self._cleanup_on_failure()
                
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                
                # Clean up on failure
                self._cleanup_on_failure()
                
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay
                    logger.warning(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
        
        # All retries exhausted
        error_msg = f"Failed to start browser after {self.max_retries} attempts: {last_error}"
        logger.error(error_msg)
        raise BrowserStartupError(error_msg)
    
    def _create_context(self) -> BrowserContext:
        """Create a new browser context with standard configuration"""
        try:
            context = self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                record_video_dir="videos/" if not self.headless else None,
                ignore_https_errors=True,
                java_script_enabled=True
            )
            
            # Enable request interception
            context.route("**/*", lambda route: route.continue_())
            
            return context
            
        except PlaywrightError as e:
            logger.error(f"Failed to create browser context: {e}")
            raise BrowserStartupError(f"Context creation failed: {e}")
    
    def _cleanup_on_failure(self):
        """Clean up resources on startup failure"""
        try:
            if self.context:
                self.context.close()
                self.context = None
        except Exception as e:
            logger.debug(f"Error closing context during cleanup: {e}")
        
        try:
            if self.browser:
                self.browser.close()
                self.browser = None
        except Exception as e:
            logger.debug(f"Error closing browser during cleanup: {e}")
        
        try:
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
        except Exception as e:
            logger.debug(f"Error stopping playwright during cleanup: {e}")
    
    def stop(self):
        """Stop Playwright browser with proper cleanup"""
        try:
            # Return context to pool if using pooling
            if self.enable_context_pool and self._pool_context:
                self.context_pool.release_context(self._pool_context)
                self._pool_context = None
                logger.debug("Context returned to pool")
            
            # Close context if not pooled
            elif self.context:
                try:
                    self.context.close()
                    logger.debug("Context closed")
                except Exception as e:
                    logger.warning(f"Error closing context: {e}")
                finally:
                    self.context = None
            
            # Close context pool
            if self.context_pool:
                try:
                    self.context_pool.close_all()
                    logger.debug("Context pool closed")
                except Exception as e:
                    logger.warning(f"Error closing context pool: {e}")
                finally:
                    self.context_pool = None
            
            # Close browser
            if self.browser:
                try:
                    self.browser.close()
                    logger.debug("Browser closed")
                except Exception as e:
                    logger.warning(f"Error closing browser: {e}")
                finally:
                    self.browser = None
            
            # Stop Playwright
            if self.playwright:
                try:
                    self.playwright.stop()
                    logger.debug("Playwright stopped")
                except Exception as e:
                    logger.warning(f"Error stopping Playwright: {e}")
                finally:
                    self.playwright = None
            
            logger.info("Playwright stopped successfully")
            
        except Exception as e:
            logger.error(f"Error during Playwright shutdown: {e}")
            # Ensure resources are cleared even on error
            self.context = None
            self.browser = None
            self.playwright = None
            self.context_pool = None
    
    # ========================================================================
    # PAGE INTERACTION METHODS
    # ========================================================================
    
    def navigate(self, url: str):
        """Navigate to URL"""
        self.page.goto(url)
        logger.info(f"Navigated to: {url}")
    
    def click(self, locator: str):
        """
        Click an element
        
        Args:
            locator: Playwright locator
        """
        self.page.locator(locator).click()
        logger.debug(f"Clicked: {locator}")
    
    def fill(self, locator: str, text: str):
        """
        Fill an input field
        
        Args:
            locator: Playwright locator
            text: Text to fill
        """
        self.page.locator(locator).fill(text)
        logger.debug(f"Filled {locator} with: {text}")
    
    def get_text(self, locator: str) -> str:
        """Get text content of element"""
        text = self.page.locator(locator).text_content()
        return text
    
    def is_visible(self, locator: str) -> bool:
        """Check if element is visible"""
        return self.page.locator(locator).is_visible()
    
    def wait_for_element(self, locator: str, timeout: int = 10000):
        """Wait for element to be visible"""
        self.page.locator(locator).wait_for(state="visible", timeout=timeout)
    
    def take_screenshot(self, filename: str):
        """Take screenshot"""
        self.page.screenshot(path=filename)
        logger.info(f"Screenshot saved: {filename}")
    
    # ========================================================================
    # TRACING METHODS
    # ========================================================================
    
    def start_tracing(self):
        """Start Playwright tracing"""
        self.context.tracing.start(screenshots=True, snapshots=True)
    
    def stop_tracing(self, filename: str = "trace.zip"):
        """Stop tracing and save"""
        self.context.tracing.stop(path=filename)
        logger.info(f"Trace saved: {filename}")
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_page(self) -> Page:
        """Get Playwright page object"""
        return self.page
    
    def get_context_pool_stats(self) -> Dict[str, Any]:
        """Get context pool statistics"""
        if not self.enable_context_pool or not self.context_pool:
            return {"enabled": False}
        
        return self.context_pool.get_stats()
    
    def acquire_pooled_context(self, timeout: float = 5.0) -> BrowserContext:
        """
        Acquire a context from the pool for parallel execution
        
        Args:
            timeout: Maximum time to wait for available context
        
        Returns:
            BrowserContext from the pool
        
        Raises:
            ContextPoolExhausted: If no context available within timeout
        """
        if not self.enable_context_pool or not self.context_pool:
            raise RuntimeError("Context pooling not enabled")
        
        return self.context_pool.acquire_context(timeout=timeout)
    
    def release_pooled_context(self, context: BrowserContext):
        """
        Release a context back to the pool
        
        Args:
            context: Context to release
        """
        if not self.enable_context_pool or not self.context_pool:
            raise RuntimeError("Context pooling not enabled")
        
        self.context_pool.release_context(context)

    'PlaywrightEngine',
    'PlaywrightPage',
    'ContextPool',
    'BrowserStartupError',
    'ContextPoolExhausted'


# ========================================================================
# CONTEXT POOL IMPLEMENTATION
# ========================================================================

class ContextPool:
    """
    Browser context pool for parallel test execution
    
    Features:
    - Reusable browser contexts
    - Thread-safe acquisition/release
    - Automatic context cleanup
    - Pool statistics
    """
    
    def __init__(self, browser: Browser, pool_size: int = 5, headless: bool = True):
        """
        Initialize context pool
        
        Args:
            browser: Playwright browser instance
            pool_size: Number of contexts to create
            headless: Whether browser is in headless mode
        """
        self.browser = browser
        self.pool_size = pool_size
        self.headless = headless
        
        # Thread-safe queue for available contexts
        self.available_contexts: Queue[BrowserContext] = Queue(maxsize=pool_size)
        self.all_contexts: List[BrowserContext] = []
        
        # Statistics
        self._lock = threading.Lock()
        self._stats = {
            'total_acquisitions': 0,
            'total_releases': 0,
            'contexts_in_use': 0,
            'contexts_available': 0,
            'wait_timeouts': 0
        }
        
        # Initialize pool
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Create initial pool of contexts"""
        logger.info(f"Initializing context pool with {self.pool_size} contexts")
        
        for i in range(self.pool_size):
            try:
                context = self.browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    record_video_dir=None,  # Disable video for pool contexts
                    ignore_https_errors=True,
                    java_script_enabled=True
                )
                
                # Enable request interception
                context.route("**/*", lambda route: route.continue_())
                
                self.all_contexts.append(context)
                self.available_contexts.put(context)
                
                logger.debug(f"Context {i + 1}/{self.pool_size} created")
                
            except Exception as e:
                logger.error(f"Failed to create context {i + 1}: {e}")
                # Continue creating remaining contexts
        
        with self._lock:
            self._stats['contexts_available'] = self.available_contexts.qsize()
        
        logger.info(f"Context pool initialized with {len(self.all_contexts)} contexts")
    
    def acquire_context(self, timeout: float = 5.0) -> BrowserContext:
        """
        Acquire a context from the pool
        
        Args:
            timeout: Maximum wait time in seconds
        
        Returns:
            BrowserContext from pool
        
        Raises:
            ContextPoolExhausted: If no context available
        """
        try:
            context = self.available_contexts.get(timeout=timeout)
            
            with self._lock:
                self._stats['total_acquisitions'] += 1
                self._stats['contexts_in_use'] += 1
                self._stats['contexts_available'] = self.available_contexts.qsize()
            
            logger.debug(f"Context acquired (available: {self.available_contexts.qsize()})")
            return context
            
        except Empty:
            with self._lock:
                self._stats['wait_timeouts'] += 1
            
            error_msg = f"No context available in pool after {timeout}s"
            logger.error(error_msg)
            raise ContextPoolExhausted(error_msg)
    
    def release_context(self, context: BrowserContext):
        """
        Release a context back to the pool
        
        Args:
            context: Context to release
        """
        if context not in self.all_contexts:
            logger.warning("Attempted to release context not from this pool")
            return
        
        try:
            # Clean up context before returning to pool
            pages = context.pages
            for page in pages:
                try:
                    page.close()
                except Exception as e:
                    logger.debug(f"Error closing page during cleanup: {e}")
            
            # Return to pool
            self.available_contexts.put(context)
            
            with self._lock:
                self._stats['total_releases'] += 1
                self._stats['contexts_in_use'] -= 1
                self._stats['contexts_available'] = self.available_contexts.qsize()
            
            logger.debug(f"Context released (available: {self.available_contexts.qsize()})")
            
        except Exception as e:
            logger.error(f"Error releasing context: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        with self._lock:
            return {
                'enabled': True,
                'pool_size': self.pool_size,
                'contexts_available': self._stats['contexts_available'],
                'contexts_in_use': self._stats['contexts_in_use'],
                'total_acquisitions': self._stats['total_acquisitions'],
                'total_releases': self._stats['total_releases'],
                'wait_timeouts': self._stats['wait_timeouts']
            }
    
    def close_all(self):
        """Close all contexts in the pool"""
        logger.info("Closing all contexts in pool")
        
        for context in self.all_contexts:
            try:
                context.close()
            except Exception as e:
                logger.debug(f"Error closing pooled context: {e}")
        
        self.all_contexts.clear()
        
        # Clear queue
        while not self.available_contexts.empty():
            try:
                self.available_contexts.get_nowait()
            except Empty:
                break
        
        logger.info("All pooled contexts closed")


# ========================================================================
# PLAYWRIGHT PAGE WRAPPER
# ========================================================================

class PlaywrightPage(BasePage):
    """Playwright-based page object"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
    
    def navigate(self, url: str):
        self.page.goto(url)
    
    def click(self, locator: str):
        self.page.click(locator)
    
    def fill(self, locator: str, text: str):
        self.page.fill(locator, text)
    
    def get_text(self, locator: str) -> str:
        return self.page.locator(locator).inner_text()
    
    def is_visible(self, locator: str) -> bool:
        return self.page.locator(locator).is_visible()
    
    def wait_for_element(self, locator: str, timeout: int = 10000):
        self.page.wait_for_selector(locator, timeout=timeout)
    
    def take_screenshot(self, filename: str):
        self.page.screenshot(path=filename)
    
    def get_current_url(self) -> str:
        return self.page.url
    
    def get_title(self) -> str:
        return self.page.title()


__all__ = ['PlaywrightEngine', 'PlaywrightPage']
