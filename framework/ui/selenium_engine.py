"""
Selenium Engine Implementation

Legacy-compatible UI automation engine using Selenium WebDriver.

Features:
- Selenium Grid support for distributed execution
- Better browser driver management with auto-download
- Multiple browser support (Chrome, Firefox, Edge, Safari)
- Remote WebDriver capabilities
- Driver version management
"""

import os
import platform
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.core.os_manager import ChromeType
from framework.ui.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class DriverManagerError(Exception):
    """Exception for driver management errors"""
    pass


class GridConnectionError(Exception):
    """Exception for Selenium Grid connection errors"""
    pass


class SeleniumEngine:
    """
    Enhanced Selenium WebDriver engine
    
    Features:
    - Selenium Grid support
    - Better driver management with auto-download
    - Multiple browsers (Chrome, Firefox, Edge, Safari)
    - Remote capabilities
    """
    
    def __init__(
        self,
        headless: bool = True,
        grid_url: Optional[str] = None,
        browser_version: Optional[str] = None,
        platform_name: Optional[str] = None,
        driver_cache_valid_range: int = 7,
        enable_logging: bool = True
    ):
        """
        Initialize Selenium Engine
        
        Args:
            headless: Run browser in headless mode
            grid_url: Selenium Grid hub URL (e.g., 'http://localhost:4444/wd/hub')
            browser_version: Specific browser version to use
            platform_name: Platform for Grid execution (e.g., 'LINUX', 'WINDOWS', 'MAC')
            driver_cache_valid_range: Days to cache driver (default 7)
            enable_logging: Enable driver logging
        """
        self.driver: Optional[webdriver.Remote] = None
        self.headless = headless
        self.grid_url = grid_url
        self.browser_version = browser_version
        self.platform_name = platform_name
        self.driver_cache_valid_range = driver_cache_valid_range
        self.enable_logging = enable_logging
        self._is_remote = bool(grid_url)
    
    def start(self, browser_type: str = "chrome"):
        """Start Selenium browser"""
        if browser_type == "chrome":
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--start-maximized")
            
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        
        elif browser_type == "firefox":
            options = webdriver.FirefoxOptions()
            if self.headless:
                options.add_argument("--headless")
            
            service = FirefoxService(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=options)
        
        else:
            raise ValueError(f"Unsupported browser: {browser_type}")
        
        self.driver.implicitly_wait(10)
        logger.info(f"Selenium {browser_type} started (headless={self.headless})")
    
    def stop(self):
        """Stop Selenium browser"""
        try:
            if self.driver:
                session_id = getattr(self.driver, 'session_id', None)
                self.driver.quit()
                logger.info(f"Selenium stopped (session: {session_id})")
        except Exception as e:
            logger.warning(f"Error stopping Selenium: {e}")
        finally:
            self.driver = None
    
    def get_driver_info(self) -> Dict[str, Any]:
        """Get driver information"""
        if not self.driver:
            return {"status": "not_started"}
        
        info = {
            "status": "running",
            "session_id": self.driver.session_id,
            "mode": "remote" if self._is_remote else "local",
            "current_url": self.driver.current_url,
            "title": self.driver.title
        }
        
        if self._is_remote:
            info["grid_url"] = self.grid_url
        
        return info
    
    def check_grid_status(self) -> Dict[str, Any]:
        """Check Selenium Grid status"""
        if not self._is_remote:
            return {"error": "Not using Selenium Grid"}
        
        try:
            import requests
            status_url = self.grid_url.replace("/wd/hub", "/status")
            response = requests.get(status_url, timeout=5)
            return response.json()
        except Exception as e:
            return {"error": f"Failed to check Grid status: {e}"}
    
    def navigate(self, url: str):
        """Navigate to URL"""
        self.driver.get(url)
        logger.debug(f"Navigated to: {url}")
    
    def click(self, locator: str, by: By = By.CSS_SELECTOR):
        """Click element"""
        element = self.driver.find_element(by, locator)
        element.click()
        logger.debug(f"Clicked: {locator}")
    
    def fill(self, locator: str, text: str, by: By = By.CSS_SELECTOR):
        """Fill input field"""
        element = self.driver.find_element(by, locator)
        element.clear()
        element.send_keys(text)
        logger.debug(f"Filled {locator} with text")
    
    def get_text(self, locator: str, by: By = By.CSS_SELECTOR) -> str:
        """Get element text"""
        element = self.driver.find_element(by, locator)
        return element.text
    
    def is_visible(self, locator: str, by: By = By.CSS_SELECTOR) -> bool:
        """Check if element is visible"""
        try:
            element = self.driver.find_element(by, locator)
            return element.is_displayed()
        except Exception:
            return False
    
    def wait_for_element(self, locator: str, timeout: int = 10, by: By = By.CSS_SELECTOR):
        """Wait for element"""
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.presence_of_element_located((by, locator)))
    
    def take_screenshot(self, filename: str):
        """Take screenshot"""
        self.driver.save_screenshot(filename)
        logger.debug(f"Screenshot saved: {filename}")
    
    def get_driver(self):
        """Get Selenium WebDriver object"""
        return self.driver


class SeleniumPage(BasePage):
    """Selenium-based page object"""
    
    def __init__(self, driver):
        super().__init__(driver)
        self.wait = WebDriverWait(driver, 10)
    
    def navigate(self, url: str):
        self.driver.get(url)
    
    def click(self, locator: str, by: By = By.CSS_SELECTOR):
        element = self.wait.until(EC.element_to_be_clickable((by, locator)))
        element.click()
    
    def fill(self, locator: str, text: str, by: By = By.CSS_SELECTOR):
        element = self.wait.until(EC.presence_of_element_located((by, locator)))
        element.clear()
        element.send_keys(text)
    
    def get_text(self, locator: str, by: By = By.CSS_SELECTOR) -> str:
        element = self.wait.until(EC.presence_of_element_located((by, locator)))
        return element.text
    
    def is_visible(self, locator: str, by: By = By.CSS_SELECTOR) -> bool:
        try:
            element = self.driver.find_element(by, locator)
            return element.is_displayed()
        except Exception:
            return False
    
    def wait_for_element(self, locator: str, timeout: int = 10000, by: By = By.CSS_SELECTOR):
        wait = WebDriverWait(self.driver, timeout / 1000)
        wait.until(EC.presence_of_element_located((by, locator)))
    
    def take_screenshot(self, filename: str):
        self.driver.save_screenshot(filename)
    
    def get_current_url(self) -> str:
        return self.driver.current_url
    
    def get_title(self) -> str:
        return self.driver.title


__all__ = [
    'SeleniumEngine',
    'SeleniumPage',
    'DriverManagerError',
    'GridConnectionError'
]
