"""
Example 2: Form Filling with Human Behavior

Demonstrates realistic form filling with natural pauses,
mouse movements, and random interactions.

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from framework.core.utils.human_actions import HumanBehaviorSimulator


@pytest.mark.human_like
def test_form_filling_human_like():
    """Fill a complex form with human-like behavior."""
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    # Navigate to a form (using a demo form site)
    driver.get("https://www.selenium.dev/selenium/web/web-form.html")
    
    try:
        # Initialize human behavior simulator
        simulator = HumanBehaviorSimulator(driver, enabled=True)
        
        print("🎯 Starting form fill with human behavior...")
        
        # 1. Text Input - with natural typing
        text_input = driver.find_element(By.ID, "my-text-id")
        simulator.type_text(text_input, "John Doe")
        simulator.simulate_idle((0.3, 0.8))
        
        # 2. Password - with thinking pause
        password_input = driver.find_element(By.NAME, "my-password")
        simulator.simulate_idle((0.5, 1.2))  # Think before entering password
        simulator.type_text(password_input, "SecurePass123!")
        
        # 3. Random mouse movement (user looking at form)
        simulator.random_mouse_movements(steps=8)
        
        # 4. Textarea - with slower typing
        textarea = driver.find_element(By.NAME, "my-textarea")
        simulator.scroll_page('down', distance=200)
        simulator.type_text(textarea, "This is a test message with human-like typing behavior.")
        simulator.simulate_idle((0.5, 1.0))
        
        # 5. Dropdown - with hover and selection
        dropdown = driver.find_element(By.NAME, "my-select")
        simulator.click_element(dropdown)
        simulator.simulate_idle((0.3, 0.7))
        Select(dropdown).select_by_index(2)
        
        # 6. Scroll to see more fields
        simulator.scroll_page('down', distance=300)
        simulator.simulate_idle((1.0, 2.0))  # Reading remaining fields
        
        # 7. Checkboxes - random interaction
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        if checkboxes:
            for checkbox in checkboxes[:2]:  # Check first 2
                simulator.click_element(checkbox)
                simulator.simulate_idle((0.4, 0.8))
        
        # 8. Random page interactions
        simulator.random_page_interactions(max_interactions=2)
        
        # 9. Submit with confirmation
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        simulator.simulate_idle((0.8, 1.5))  # Review before submit
        simulator.click_element(submit_button, with_hover=True)
        
        # 10. Wait for submission
        simulator.simulate_idle((2.0, 3.0))
        
        print("✅ Form filled successfully with human behavior!")
        
    finally:
        driver.quit()


@pytest.mark.human_like
def test_multi_step_form_realistic():
    """Multi-step form with very realistic human behavior."""
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://www.selenium.dev/selenium/web/web-form.html")
    
    try:
        simulator = HumanBehaviorSimulator(driver, enabled=True)
        
        # Step 1: Initial page load - user reads form
        simulator.simulate_idle((2.0, 3.5))
        simulator.scroll_page('down', distance=300)
        simulator.scroll_page('up', distance=150)  # Scroll back to top
        simulator.simulate_idle((1.0, 2.0))
        
        # Step 2: Start filling with hesitation
        form_data = {
            "my-text-id": "Jane Smith",
            "my-password": "MyP@ssw0rd!",
        }
        
        for field_id, value in form_data.items():
            # Find field
            field = driver.find_element(By.ID, field_id)
            
            # Click field (focus)
            simulator.click_element(field)
            
            # Think before typing
            simulator.simulate_idle((0.4, 1.0))
            
            # Type with natural delays
            simulator.type_text(field, value)
            
            # Random chance of correction (backspace)
            import random
            if random.random() < 0.15:  # 15% chance
                field.send_keys("\b\b")  # Delete 2 chars
                simulator.simulate_idle((0.2, 0.5))
                simulator.type_text(field, value[-2:])
            
            # Pause between fields
            simulator.simulate_idle((0.5, 1.5))
        
        # Step 3: Browse/explore form randomly
        simulator.random_mouse_movements(steps=12)
        
        # Step 4: Submit
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        simulator.scroll_to_element(submit_btn)
        simulator.simulate_idle((1.0, 2.0))
        simulator.click_element(submit_btn)
        
        print("✅ Multi-step form completed with realistic behavior!")
        
    finally:
        driver.quit()


def test_comparison_with_without_human_behavior():
    """Side-by-side comparison of execution time."""
    import time
    
    # Without human behavior
    start_time = time.time()
    driver = webdriver.Chrome()
    driver.get("https://www.selenium.dev/selenium/web/web-form.html")
    driver.find_element(By.ID, "my-text-id").send_keys("Test User")
    driver.find_element(By.NAME, "my-password").send_keys("password")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    driver.quit()
    normal_time = time.time() - start_time
    
    # With human behavior
    start_time = time.time()
    driver = webdriver.Chrome()
    driver.get("https://www.selenium.dev/selenium/web/web-form.html")
    simulator = HumanBehaviorSimulator(driver, enabled=True)
    text_field = driver.find_element(By.ID, "my-text-id")
    simulator.type_text(text_field, "Test User")
    password_field = driver.find_element(By.NAME, "my-password")
    simulator.type_text(password_field, "password")
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    simulator.click_element(submit_btn)
    driver.quit()
    human_time = time.time() - start_time
    
    print(f"\n⏱️  Execution Time Comparison:")
    print(f"   Normal: {normal_time:.2f}s")
    print(f"   Human-like: {human_time:.2f}s")
    print(f"   Difference: +{human_time - normal_time:.2f}s ({((human_time/normal_time - 1) * 100):.1f}% slower)")


if __name__ == "__main__":
    print("Example 1: Form filling with human behavior")
    test_form_filling_human_like()
    
    print("\n" + "="*60)
    print("Example 2: Multi-step realistic form")
    test_multi_step_form_realistic()
    
    print("\n" + "="*60)
    print("Example 3: Performance comparison")
    test_comparison_with_without_human_behavior()
