"""
UI Factory - Engine Selection and Fallback Logic

This module provides the factory for creating UI engine instances
and implements the Playwright → Selenium fallback strategy.
"""

from typing import Optional, Any
from framework.ui.playwright_engine import PlaywrightEngine
from framework.ui.selenium_engine import SeleniumEngine
from framework.core.engine_selector import EngineSelector, EngineDecision
from framework.core.ai_engine_selector import AIEngineSelector
from utils.logger import get_logger
from config.settings import settings, is_ai_enabled

logger = get_logger(__name__)


class UIFactory:
    """Factory for creating UI engine instances"""
    
    def __init__(self):
        self.engine_selector = EngineSelector()
        self.ai_selector = None
        
        if is_ai_enabled():
            self.ai_selector = AIEngineSelector()
    
    def create_engine(
        self,
        test_metadata: dict,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> tuple[Any, EngineDecision]:
        """
        Create UI engine based on test metadata
        
        Args:
            test_metadata: Test characteristics
            browser_type: Browser to use (chromium, chrome, firefox)
            headless: Run in headless mode
        
        Returns:
            Tuple of (engine_instance, decision)
        """
        # Try AI selector first (if enabled)
        decision = None
        if self.ai_selector:
            decision = self.ai_selector.select_engine(test_metadata)
            if decision:
                logger.info(f"AI selected engine: {decision.engine} (confidence: {decision.confidence}%)")
        
        # Fallback to YAML selector
        if not decision:
            decision = self.engine_selector.select_engine(test_metadata)
            logger.info(f"YAML selected engine: {decision.engine} (reason: {decision.reason})")
        
        # Create engine instance
        if decision.engine == "playwright":
            engine = self._create_playwright(browser_type, headless)
        else:
            engine = self._create_selenium(browser_type, headless)
        
        return engine, decision
    
    def _create_playwright(self, browser_type: str = "chromium", headless: bool = True) -> PlaywrightEngine:
        """Create Playwright engine instance"""
        engine = PlaywrightEngine(headless=headless)
        engine.start(browser_type=browser_type)
        return engine
    
    def _create_selenium(self, browser_type: str = "chrome", headless: bool = True) -> SeleniumEngine:
        """Create Selenium engine instance"""
        engine = SeleniumEngine(headless=headless)
        engine.start(browser_type=browser_type)
        return engine
    
    def execute_with_fallback(
        self,
        test_func,
        test_metadata: dict,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> dict:
        """
        Execute test with automatic fallback from Playwright to Selenium
        
        Args:
            test_func: Test function to execute
            test_metadata: Test metadata
            browser_type: Browser type
            headless: Headless mode
        
        Returns:
            Execution result with engine and status
        """
        result = {
            "attempts": [],
            "final_status": "unknown",
            "fallback_triggered": False
        }
        
        # First attempt - use selected engine
        engine, decision = self.create_engine(test_metadata, browser_type, headless)
        
        try:
            logger.info(f"Attempt 1: Using {decision.engine}")
            test_func(engine)
            
            result["attempts"].append({
                "engine": decision.engine,
                "status": "passed",
                "error": None
            })
            result["final_status"] = "passed"
        
        except Exception as e:
            error_type = self._classify_error(e)
            logger.warning(f"Attempt 1 failed with {decision.engine}: {error_type}")
            
            result["attempts"].append({
                "engine": decision.engine,
                "status": "failed",
                "error": str(e),
                "error_type": error_type
            })
            
            # Check if fallback should be triggered
            should_fallback = (
                decision.engine == "playwright" and
                self.engine_selector.should_fallback(error_type)
            )
            
            if should_fallback:
                logger.info("Fallback triggered: Switching to Selenium")
                result["fallback_triggered"] = True
                
                try:
                    # Clean up failed engine
                    engine.stop()
                except:
                    pass
                
                # Create Selenium engine for fallback
                selenium_engine = self._create_selenium(browser_type="chrome", headless=headless)
                
                try:
                    logger.info("Attempt 2: Using selenium (fallback)")
                    test_func(selenium_engine)
                    
                    result["attempts"].append({
                        "engine": "selenium",
                        "status": "passed",
                        "error": None
                    })
                    result["final_status"] = "passed_with_fallback"
                
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {fallback_error}")
                    result["attempts"].append({
                        "engine": "selenium",
                        "status": "failed",
                        "error": str(fallback_error)
                    })
                    result["final_status"] = "failed"
                
                finally:
                    try:
                        selenium_engine.stop()
                    except:
                        pass
            else:
                result["final_status"] = "failed"
                raise
        
        finally:
            try:
                engine.stop()
            except:
                pass
        
        return result
    
    def _classify_error(self, exception: Exception) -> str:
        """
        Classify exception to determine if fallback should be triggered
        
        Args:
            exception: Exception that occurred
        
        Returns:
            Error type classification
        """
        error_msg = str(exception).lower()
        
        # Engine-level failures (trigger fallback)
        if "browser" in error_msg and "crash" in error_msg:
            return "browser_process_crash"
        if "context" in error_msg and "corrupt" in error_msg:
            return "browser_context_corruption"
        if "navigation" in error_msg and "timeout" in error_msg:
            return "navigation_timeout_exceeded"
        if "timeout" in error_msg and "page" in error_msg:
            return "page_load_timeout"
        if "webdriver" in error_msg or "protocol" in error_msg:
            return "webdriver_protocol_error"
        
        # Application failures (do NOT trigger fallback)
        if "element" in error_msg and "not found" in error_msg:
            return "element_not_found"
        if "assertion" in error_msg:
            return "assertion_failure"
        
        # Default
        return "unknown_error"


# Global factory instance
ui_factory = UIFactory()


__all__ = ['UIFactory', 'ui_factory']
