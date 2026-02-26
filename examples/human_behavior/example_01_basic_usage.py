"""
Example 1: Basic Human Behavior with Pytest Fixture

This example demonstrates the simplest way to use human behavior
simulation with the pytest fixture.

Author: Lokendra Singh
Email: lokendra.singh@centerforvein.com
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By


@pytest.mark.human_like
def test_saucedemo_login_with_human_behavior(human_behavior):
    """
    Test login on SauceDemo with human-like behavior
    
    The @pytest.mark.human_like marker automatically enables
    human behavior simulation for this test.
    """
    # Setup driver
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://www.saucedemo.com/")
    
    try:
        # Create human behavior simulator
        from framework.core.utils.human_actions import HumanBehaviorSimulator
        simulator = HumanBehaviorSimulator(driver, enabled=True)
        
        # Type username with human-like delays
        username_field = driver.find_element(By.ID, "user-name")
        simulator.type_text(username_field, "standard_user")
        
        # Pause (thinking time)
        simulator.simulate_idle((0.5, 1.5))
        
        # Type password
        password_field = driver.find_element(By.ID, "password")
        simulator.type_text(password_field, "secret_sauce")
        
        # Random mouse movements (browsing)
        simulator.random_mouse_movements(steps=5)
        
        # Click login button with hover
        login_button = driver.find_element(By.ID, "login-button")
        simulator.click_element(login_button, with_hover=True)
        
        # Wait for page load
        simulator.simulate_idle((2.0, 3.0))
        
        # Scroll to explore products
        simulator.scroll_page('down', distance=400)
        simulator.simulate_idle((1.0, 2.0))
        
        # Verify login success
        assert "inventory" in driver.current_url
        print("✅ Login successful with human behavior!")
        
    finally:
        driver.quit()


def test_saucedemo_without_human_behavior():
    """
    Same test without human behavior for comparison
    This will run much faster
    """
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://www.saucedemo.com/")
    
    try:
        # Normal automation (fast but robotic)
        driver.find_element(By.ID, "user-name").send_keys("standard_user")
        driver.find_element(By.ID, "password").send_keys("secret_sauce")
        driver.find_element(By.ID, "login-button").click()
        
        # Verify
        assert "inventory" in driver.current_url
        print("✅ Login successful (normal speed)")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    # Run directly
    print("Running with human behavior...")
    test_saucedemo_login_with_human_behavior(None)
    
    print("\nRunning without human behavior...")
    test_saucedemo_without_human_behavior()
