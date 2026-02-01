"""
Example 3: Integration with Framework Engines

Shows how to use human behavior with Selenium and Playwright engines
from the existing framework.

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
"""

import pytest
from framework.ui.selenium_engine import SeleniumEngine
from framework.core.utils.human_actions import HumanBehaviorSimulator


def test_selenium_engine_integration():
    """Using human behavior with Selenium Engine from framework."""
    print("🎯 Testing with Selenium Engine...")
    
    # Initialize Selenium engine
    engine = SeleniumEngine(headless=False)
    engine.start("chrome")
    
    try:
        # Navigate to test site
        engine.driver.get("https://www.saucedemo.com/")
        
        # Create human behavior simulator
        simulator = HumanBehaviorSimulator(engine.driver, enabled=True)
        
        # Login with human-like behavior
        from selenium.webdriver.common.by import By
        username = engine.driver.find_element(By.ID, "user-name")
        password = engine.driver.find_element(By.ID, "password")
        login_btn = engine.driver.find_element(By.ID, "login-button")
        
        # Human-like typing
        print("  → Typing username...")
        simulator.type_text(username, "standard_user")
        
        print("  → Thinking...")
        simulator.simulate_idle((0.5, 1.2))
        
        print("  → Typing password...")
        simulator.type_text(password, "secret_sauce")
        
        print("  → Random mouse movements...")
        simulator.random_mouse_movements(steps=6)
        
        print("  → Clicking login...")
        simulator.click_element(login_btn)
        
        print("  → Waiting for page load...")
        simulator.simulate_idle((2.0, 3.0))
        
        # Verify
        assert "inventory" in engine.driver.current_url
        print("✅ Selenium Engine + Human Behavior: SUCCESS")
        
    finally:
        engine.stop()


def test_playwright_engine_integration():
    """Using human behavior with Playwright Engine from framework."""
    print("\n🎯 Testing with Playwright Engine...")
    
    try:
        from framework.ui.playwright_engine import PlaywrightEngine
        
        # Initialize Playwright engine
        engine = PlaywrightEngine(headless=False, slow_mo=0)
        engine.start("chromium")
        
        try:
            # Navigate to test site
            engine.page.goto("https://www.saucedemo.com/")
            
            # Create human behavior simulator
            simulator = HumanBehaviorSimulator(engine.page, enabled=True)
            
            # Login with human-like behavior
            print("  → Typing username...")
            simulator.type_text("#user-name", "standard_user")
            
            print("  → Thinking...")
            simulator.simulate_idle((0.5, 1.2))
            
            print("  → Typing password...")
            simulator.type_text("#password", "secret_sauce")
            
            print("  → Scrolling...")
            simulator.scroll_page('down', distance=200)
            
            print("  → Clicking login...")
            simulator.click_element("#login-button")
            
            print("  → Waiting for navigation...")
            simulator.simulate_idle((2.0, 3.0))
            
            # Verify
            assert "inventory" in engine.page.url
            print("✅ Playwright Engine + Human Behavior: SUCCESS")
            
        finally:
            engine.stop()
            
    except ImportError:
        print("⚠️  Playwright not available, skipping...")


def test_page_object_integration():
    """Using human behavior with Page Object pattern."""
    print("\n🎯 Testing with Page Object Pattern...")
    
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    
    class LoginPage:
        """Example Page Object with human behavior."""
        
        def __init__(self, driver, use_human_behavior=True):
            self.driver = driver
            self.human = HumanBehaviorSimulator(driver, enabled=use_human_behavior)
        
        def navigate(self):
            self.driver.get("https://www.saucedemo.com/")
            self.human.simulate_idle((1.0, 2.0))
        
        def login(self, username, password):
            """Login with human-like behavior."""
            print(f"  → Logging in as {username}...")
            
            # Type username
            username_field = self.driver.find_element(By.ID, "user-name")
            self.human.type_text(username_field, username)
            
            # Think
            self.human.simulate_idle((0.4, 1.0))
            
            # Type password
            password_field = self.driver.find_element(By.ID, "password")
            self.human.type_text(password_field, password)
            
            # Random interactions
            self.human.random_mouse_movements(steps=4)
            
            # Click login
            login_btn = self.driver.find_element(By.ID, "login-button")
            self.human.click_element(login_btn)
            
            # Wait
            self.human.simulate_idle((2.0, 3.0))
        
        def verify_logged_in(self):
            return "inventory" in self.driver.current_url
    
    # Test with Page Object
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    try:
        login_page = LoginPage(driver, use_human_behavior=True)
        login_page.navigate()
        login_page.login("standard_user", "secret_sauce")
        
        assert login_page.verify_logged_in()
        print("✅ Page Object + Human Behavior: SUCCESS")
        
    finally:
        driver.quit()


def test_configuration_based_behavior():
    """Demonstrate configuration-based behavior control."""
    print("\n🎯 Testing Configuration-Based Behavior...")
    
    from framework.core.utils.human_actions import get_behavior_config
    
    # Get global config
    config = get_behavior_config()
    
    print(f"  → Global enabled: {config.is_enabled()}")
    print(f"  → Typing enabled: {config.is_category_enabled('typing')}")
    print(f"  → Mouse enabled: {config.is_category_enabled('mouse')}")
    print(f"  → Scrolling enabled: {config.is_category_enabled('scrolling')}")
    
    # Get specific settings
    min_delay = config.get('typing.min_delay', 0.1)
    max_delay = config.get('typing.max_delay', 0.3)
    print(f"  → Typing delay: {min_delay}-{max_delay}s")
    
    # Test with different configs
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    
    driver = webdriver.Chrome()
    driver.get("https://www.selenium.dev/selenium/web/web-form.html")
    
    try:
        # Test 1: Enabled
        simulator = HumanBehaviorSimulator(driver, enabled=True)
        field = driver.find_element(By.ID, "my-text-id")
        print("  → Testing with enabled=True...")
        simulator.type_text(field, "Test with behavior")
        
        # Clear field
        field.clear()
        
        # Test 2: Disabled (faster)
        simulator = HumanBehaviorSimulator(driver, enabled=False)
        print("  → Testing with enabled=False...")
        simulator.type_text(field, "Test without behavior")
        
        print("✅ Configuration-Based Behavior: SUCCESS")
        
    finally:
        driver.quit()


def test_standalone_functions():
    """Using standalone helper functions."""
    print("\n🎯 Testing Standalone Functions...")
    
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from framework.core.utils.human_actions import (
        human_type, human_click, human_scroll_behavior,
        random_mouse_movement, simulate_idle
    )
    
    driver = webdriver.Chrome()
    driver.get("https://www.saucedemo.com/")
    
    try:
        print("  → Using standalone functions...")
        
        # Get elements
        username = driver.find_element(By.ID, "user-name")
        password = driver.find_element(By.ID, "password")
        login_btn = driver.find_element(By.ID, "login-button")
        
        # Use standalone functions
        human_type(username, "standard_user", driver)
        simulate_idle(driver, (0.5, 1.0))
        human_type(password, "secret_sauce", driver)
        random_mouse_movement(driver, steps=5)
        human_click(driver, login_btn)
        simulate_idle(driver, (2.0, 3.0))
        
        assert "inventory" in driver.current_url
        print("✅ Standalone Functions: SUCCESS")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    """Run all integration examples."""
    
    print("="*70)
    print("HUMAN BEHAVIOR INTEGRATION EXAMPLES")
    print("="*70)
    
    # Test 1: Selenium Engine
    test_selenium_engine_integration()
    
    # Test 2: Playwright Engine
    test_playwright_engine_integration()
    
    # Test 3: Page Object Pattern
    test_page_object_integration()
    
    # Test 4: Configuration-based
    test_configuration_based_behavior()
    
    # Test 5: Standalone functions
    test_standalone_functions()
    
    print("\n" + "="*70)
    print("✅ ALL INTEGRATION TESTS COMPLETED!")
    print("="*70)
