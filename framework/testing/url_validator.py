"""
URL Validator

Multi-level URL validation with Playwright integration.
Follows Validator pattern from framework (DBValidator, PreFlightValidator, etc.)

Pattern: Validator
Extends: None
Dependencies: Playwright, ValidationResult

Author: Hybrid Automation Framework
Date: 2026-02-25
"""

from typing import Optional, List, Dict
import time
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError

from framework.microservices.url_testing_service import ValidationResult
from framework.observability.enterprise_logger import get_enterprise_logger
from framework.observability.universal_logger import log_function


logger = get_enterprise_logger()


class URLValidator:
    """
    URL Validator - Multi-level URL validation
    
    Validation Levels:
    1. HTTP Status Check (200 OK)
    2. Element Presence Check (h1, form, etc.)
    3. Error Message Check (no errors on page)
    4. Performance Check (load time < threshold)
    
    Pattern: Validator
    Used By: URLValidationService, test fixtures
    """
    
    def __init__(self, page: Page):
        self.page = page
        logger.debug("URLValidator initialized with Playwright page")
    
    @log_function(log_timing=True)
    def validate(
        self,
        url: str,
        expected_elements: Optional[List[str]] = None,
        timeout: int = 10000
    ) -> ValidationResult:
        """
        Perform comprehensive URL validation
        
        Args:
            url: URL to validate
            expected_elements: List of element selectors to check
            timeout: Timeout in milliseconds
        
        Returns:
            ValidationResult with detailed status
        """
        logger.info(f"Validating URL: {url}")
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Level 1: HTTP Status Check
            logger.debug("Level 1: HTTP Status Check")
            response = self.page.goto(url, wait_until="networkidle", timeout=timeout)
            
            if response is None:
                errors.append("Failed to load page - no response received")
                status_code = 0
            else:
                status_code = response.status
                details["status_code"] = status_code
                
                if status_code != 200:
                    errors.append(f"HTTP {status_code}: Expected 200")
                    logger.warning(f"HTTP status mismatch: {status_code}")
            
            # Level 2: Element Presence Check
            if expected_elements:
                logger.debug(f"Level 2: Element Presence Check ({len(expected_elements)} elements)")
                missing_elements = []
                
                for selector in expected_elements:
                    try:
                        element_count = self.page.locator(selector).count()
                        if element_count == 0:
                            missing_elements.append(selector)
                            errors.append(f"Element not found: {selector}")
                        else:
                            logger.debug(f"Element found: {selector} (count: {element_count})")
                    except Exception as e:
                        missing_elements.append(selector)
                        errors.append(f"Element check failed for {selector}: {str(e)}")
                
                details["missing_elements"] = missing_elements
                details["expected_elements_count"] = len(expected_elements)
                details["found_elements_count"] = len(expected_elements) - len(missing_elements)
            
            # Level 3: Error Message Check
            logger.debug("Level 3: Error Message Check")
            error_selectors = [
                ".error",
                "[class*='error']",
                "[role='alert']",
                ".alert-danger",
                ".error-message"
            ]
            
            found_errors = []
            for selector in error_selectors:
                try:
                    count = self.page.locator(selector).count()
                    if count > 0:
                        # Get error text
                        for i in range(min(count, 3)):  # Limit to 3 errors
                            try:
                                error_text = self.page.locator(selector).nth(i).text_content()
                                if error_text and error_text.strip():
                                    found_errors.append(error_text.strip())
                            except:
                                pass
                        
                        warnings.append(f"Error element found: {selector} (count: {count})")
                except Exception as e:
                    logger.debug(f"Error checking selector {selector}: {e}")
            
            details["page_errors"] = found_errors
            
            # Level 4: Performance Check
            load_time = int((time.time() - start_time) * 1000)
            details["load_time_ms"] = load_time
            logger.debug(f"Level 4: Performance Check - Load time: {load_time}ms")
            
            if load_time > timeout:
                warnings.append(f"Slow load time: {load_time}ms (threshold: {timeout}ms)")
            elif load_time > (timeout * 0.8):
                warnings.append(f"Load time approaching threshold: {load_time}ms")
            
            # Additional checks
            logger.debug("Additional checks: Page title and URL")
            try:
                page_title = self.page.title()
                details["page_title"] = page_title
                logger.debug(f"Page title: {page_title}")
            except Exception as e:
                warnings.append(f"Could not get page title: {str(e)}")
            
            current_url = self.page.url
            details["final_url"] = current_url
            
            if current_url != url:
                warnings.append(f"URL changed after navigation: {url} -> {current_url}")
                logger.warning(f"URL redirect detected: {current_url}")
            
            # Determine overall validity
            is_valid = len(errors) == 0
            
            result = ValidationResult(
                url=url,
                status_code=status_code if 'status_code' in locals() else 0,
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                validation_time_ms=load_time,
                details=details
            )
            
            logger.info(f"Validation complete: valid={is_valid}, errors={len(errors)}, warnings={len(warnings)}")
            return result
        
        except PlaywrightTimeoutError as e:
            load_time = int((time.time() - start_time) * 1000)
            logger.error(f"Timeout during validation: {str(e)}")
            
            return ValidationResult(
                url=url,
                status_code=0,
                is_valid=False,
                errors=[f"Timeout: Page did not load within {timeout}ms"],
                warnings=[],
                validation_time_ms=load_time,
                details={"error_type": "timeout", "timeout_ms": timeout}
            )
        
        except PlaywrightError as e:
            load_time = int((time.time() - start_time) * 1000)
            logger.error(f"Playwright error during validation: {str(e)}")
            
            return ValidationResult(
                url=url,
                status_code=0,
                is_valid=False,
                errors=[f"Playwright error: {str(e)}"],
                warnings=[],
                validation_time_ms=load_time,
                details={"error_type": "playwright_error"}
            )
        
        except Exception as e:
            load_time = int((time.time() - start_time) * 1000)
            logger.error(f"Unexpected error during validation: {str(e)}")
            
            return ValidationResult(
                url=url,
                status_code=0,
                is_valid=False,
                errors=[f"Validation failed: {str(e)}"],
                warnings=[],
                validation_time_ms=load_time,
                details={"error_type": "unexpected_error"}
            )
    
    def validate_elements_only(
        self,
        selectors: List[str],
        timeout: int = 5000
    ) -> Dict[str, bool]:
        """
        Validate only element presence (quick check)
        
        Args:
            selectors: List of element selectors
            timeout: Timeout per element in milliseconds
        
        Returns:
            Dictionary mapping selector to found status
        """
        logger.debug(f"Quick element validation for {len(selectors)} selectors")
        results = {}
        
        for selector in selectors:
            try:
                self.page.wait_for_selector(selector, timeout=timeout)
                results[selector] = True
                logger.debug(f"Element found: {selector}")
            except PlaywrightTimeoutError:
                results[selector] = False
                logger.debug(f"Element not found: {selector}")
            except Exception as e:
                results[selector] = False
                logger.warning(f"Error checking element {selector}: {e}")
        
        return results
    
    def validate_status_only(self, url: str, timeout: int = 10000) -> int:
        """
        Validate only HTTP status (lightweight check)
        
        Args:
            url: URL to check
            timeout: Timeout in milliseconds
        
        Returns:
            HTTP status code
        """
        logger.debug(f"Quick status check for: {url}")
        try:
            response = self.page.goto(url, wait_until="commit", timeout=timeout)
            status = response.status if response else 0
            logger.debug(f"Status code: {status}")
            return status
        except Exception as e:
            logger.error(f"Error checking status: {e}")
            return 0
    
    def check_for_errors(self) -> List[str]:
        """
        Check current page for error messages
        
        Returns:
            List of error messages found
        """
        logger.debug("Checking current page for errors")
        error_selectors = [
            ".error",
            "[class*='error']",
            "[role='alert']",
            ".alert-danger",
            ".error-message"
        ]
        
        found_errors = []
        
        for selector in error_selectors:
            try:
                count = self.page.locator(selector).count()
                if count > 0:
                    for i in range(min(count, 3)):
                        try:
                            error_text = self.page.locator(selector).nth(i).text_content()
                            if error_text and error_text.strip():
                                found_errors.append(error_text.strip())
                        except:
                            pass
            except Exception as e:
                logger.debug(f"Error checking selector {selector}: {e}")
        
        logger.debug(f"Found {len(found_errors)} error messages")
        return found_errors
