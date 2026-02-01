"""
Example 4: Advanced Usage - E-commerce Scenario

Realistic e-commerce flow with comprehensive human behavior simulation.

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from framework.core.utils.human_actions import HumanBehaviorSimulator


@pytest.mark.human_like
def test_ecommerce_shopping_journey():
    """
    Complete e-commerce shopping journey with realistic human behavior
    """
    print("\n🛒 Starting E-commerce Shopping Journey...")
    
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    try:
        simulator = HumanBehaviorSimulator(driver, enabled=True)
        
        # ===== Phase 1: Homepage Exploration =====
        print("\n📍 Phase 1: Homepage Exploration")
        driver.get("https://www.saucedemo.com/")
        
        # Initial page load - user reads homepage
        print("  → Reading homepage...")
        simulator.simulate_idle((2.5, 4.0))
        
        # Random mouse movements (browsing)
        print("  → Browsing homepage...")
        simulator.random_mouse_movements(steps=10)
        
        # ===== Phase 2: Login =====
        print("\n📍 Phase 2: Login")
        
        # Type username
        username_field = driver.find_element(By.ID, "user-name")
        print("  → Entering username...")
        simulator.type_text(username_field, "standard_user")
        
        # Think before password
        simulator.simulate_idle((0.8, 1.5))
        
        # Type password
        password_field = driver.find_element(By.ID, "password")
        print("  → Entering password...")
        simulator.type_text(password_field, "secret_sauce")
        
        # Review credentials
        simulator.simulate_idle((0.5, 1.2))
        
        # Click login
        login_btn = driver.find_element(By.ID, "login-button")
        print("  → Clicking login...")
        simulator.click_element(login_btn, with_hover=True)
        
        # Wait for products page
        simulator.simulate_idle((2.0, 3.5))
        
        # ===== Phase 3: Browse Products =====
        print("\n📍 Phase 3: Browse Products")
        
        # Scroll through products
        print("  → Scrolling through products...")
        simulator.scroll_page('down', distance=300)
        simulator.simulate_idle((1.5, 2.5))  # Reading product details
        
        simulator.scroll_page('down', distance=300)
        simulator.simulate_idle((2.0, 3.0))  # More reading
        
        # Scroll back up to see earlier products
        simulator.scroll_page('up', distance=200)
        simulator.simulate_idle((1.0, 2.0))
        
        # Random mouse movements over products
        print("  → Hovering over products...")
        simulator.random_mouse_movements(steps=15)
        
        # ===== Phase 4: Filter/Sort Products =====
        print("\n📍 Phase 4: Filter/Sort Products")
        
        # Find and use sort dropdown
        try:
            sort_dropdown = driver.find_element(By.CLASS_NAME, "product_sort_container")
            print("  → Changing sort order...")
            simulator.click_element(sort_dropdown)
            simulator.simulate_idle((0.3, 0.8))
            
            from selenium.webdriver.support.ui import Select
            Select(sort_dropdown).select_by_value("lohi")  # Low to High
            simulator.simulate_idle((1.0, 2.0))  # Wait for re-sort
        except:
            print("  → Sort dropdown not found, continuing...")
        
        # ===== Phase 5: Add Products to Cart =====
        print("\n📍 Phase 5: Add Products to Cart")
        
        # Find "Add to cart" buttons
        add_to_cart_buttons = driver.find_elements(By.CSS_SELECTOR, "button[id^='add-to-cart']")
        
        if len(add_to_cart_buttons) >= 2:
            # Add first product
            print("  → Adding product 1 to cart...")
            simulator.scroll_to_element(add_to_cart_buttons[0])
            simulator.simulate_idle((1.0, 2.0))  # Read product details
            simulator.click_element(add_to_cart_buttons[0])
            simulator.simulate_idle((0.5, 1.0))
            
            # Browse more products
            simulator.scroll_page('down', distance=200)
            simulator.random_mouse_movements(steps=8)
            
            # Add second product
            print("  → Adding product 2 to cart...")
            simulator.simulate_idle((1.5, 2.5))  # Compare products
            simulator.click_element(add_to_cart_buttons[1])
            simulator.simulate_idle((0.5, 1.0))
        
        # ===== Phase 6: View Cart =====
        print("\n📍 Phase 6: View Cart")
        
        # Click cart icon
        cart_icon = driver.find_element(By.CLASS_NAME, "shopping_cart_link")
        print("  → Viewing cart...")
        simulator.click_element(cart_icon, with_hover=True)
        simulator.simulate_idle((2.0, 3.0))  # Review cart items
        
        # Scroll through cart
        simulator.scroll_page('down', distance=300)
        simulator.simulate_idle((1.5, 2.5))
        
        # Random mouse movements over cart items
        simulator.random_mouse_movements(steps=8)
        
        # ===== Phase 7: Checkout =====
        print("\n📍 Phase 7: Checkout")
        
        # Click checkout
        checkout_btn = driver.find_element(By.ID, "checkout")
        print("  → Proceeding to checkout...")
        simulator.click_element(checkout_btn)
        simulator.simulate_idle((1.5, 2.5))
        
        # Fill checkout form
        print("  → Filling checkout form...")
        
        # First name
        first_name = driver.find_element(By.ID, "first-name")
        simulator.type_text(first_name, "John")
        simulator.simulate_idle((0.4, 0.9))
        
        # Last name
        last_name = driver.find_element(By.ID, "last-name")
        simulator.type_text(last_name, "Doe")
        simulator.simulate_idle((0.4, 0.9))
        
        # Postal code
        postal_code = driver.find_element(By.ID, "postal-code")
        simulator.type_text(postal_code, "12345")
        simulator.simulate_idle((0.5, 1.2))
        
        # Random mouse movements
        simulator.random_mouse_movements(steps=6)
        
        # Continue
        continue_btn = driver.find_element(By.ID, "continue")
        print("  → Continuing to overview...")
        simulator.click_element(continue_btn)
        simulator.simulate_idle((2.0, 3.0))
        
        # ===== Phase 8: Review Order =====
        print("\n📍 Phase 8: Review Order")
        
        # Scroll through order summary
        simulator.scroll_page('down', distance=400)
        simulator.simulate_idle((2.5, 4.0))  # Read order details carefully
        
        simulator.scroll_page('down', distance=300)
        simulator.simulate_idle((1.5, 2.5))
        
        # Random interactions
        simulator.random_mouse_movements(steps=10)
        
        # ===== Phase 9: Complete Purchase =====
        print("\n📍 Phase 9: Complete Purchase")
        
        # Final decision pause
        simulator.simulate_idle((2.0, 3.5))
        
        # Click finish
        finish_btn = driver.find_element(By.ID, "finish")
        print("  → Completing purchase...")
        simulator.click_element(finish_btn, with_hover=True)
        simulator.simulate_idle((2.0, 3.0))
        
        # ===== Phase 10: Confirmation =====
        print("\n📍 Phase 10: Confirmation")
        
        # Read confirmation message
        simulator.simulate_idle((3.0, 5.0))
        simulator.scroll_page('down', distance=200)
        simulator.simulate_idle((2.0, 3.0))
        
        # Verify success
        success_message = driver.find_element(By.CLASS_NAME, "complete-header")
        assert "THANK YOU" in success_message.text.upper()
        
        print("\n✅ E-commerce Journey Completed Successfully!")
        print(f"   Total realistic user behavior simulated!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
    
    finally:
        # Final idle before closing
        simulator.simulate_idle((2.0, 3.0))
        driver.quit()


@pytest.mark.human_like
def test_product_comparison_behavior():
    """
    Realistic product comparison behavior
    """
    print("\n🔍 Testing Product Comparison Behavior...")
    
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    try:
        simulator = HumanBehaviorSimulator(driver, enabled=True)
        
        # Login quickly
        driver.get("https://www.saucedemo.com/")
        driver.find_element(By.ID, "user-name").send_keys("standard_user")
        driver.find_element(By.ID, "password").send_keys("secret_sauce")
        driver.find_element(By.ID, "login-button").click()
        simulator.simulate_idle((2.0, 3.0))
        
        # Compare multiple products
        product_cards = driver.find_elements(By.CLASS_NAME, "inventory_item")
        
        for i, product in enumerate(product_cards[:3], 1):  # Compare first 3
            print(f"\n  → Examining product {i}...")
            
            # Scroll to product
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", product)
            simulator.simulate_idle((0.5, 1.0))
            
            # Hover over product
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            actions.move_to_element(product).perform()
            
            # Read details
            simulator.simulate_idle((2.0, 4.0))
            
            # Random mouse movements over product
            try:
                product_name = product.find_element(By.CLASS_NAME, "inventory_item_name")
                product_price = product.find_element(By.CLASS_NAME, "inventory_item_price")
                
                actions.move_to_element(product_name).perform()
                simulator.simulate_idle((0.5, 1.0))
                
                actions.move_to_element(product_price).perform()
                simulator.simulate_idle((0.8, 1.5))
            except:
                pass
            
            # Scroll to see more
            simulator.scroll_page('down', distance=150)
        
        # Decision pause
        print("\n  → Making decision...")
        simulator.simulate_idle((3.0, 5.0))
        
        # Select product
        add_button = driver.find_element(By.CSS_SELECTOR, "button[id^='add-to-cart']")
        simulator.click_element(add_button, with_hover=True)
        
        print("✅ Product Comparison: Complete")
        
    finally:
        driver.quit()


@pytest.mark.human_like
def test_cart_modification_behavior():
    """
    Realistic cart modification - adding, removing items
    """
    print("\n🛒 Testing Cart Modification Behavior...")
    
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    try:
        simulator = HumanBehaviorSimulator(driver, enabled=True)
        
        # Quick login
        driver.get("https://www.saucedemo.com/")
        driver.find_element(By.ID, "user-name").send_keys("standard_user")
        driver.find_element(By.ID, "password").send_keys("secret_sauce")
        driver.find_element(By.ID, "login-button").click()
        simulator.simulate_idle((2.0, 3.0))
        
        # Add multiple items
        add_buttons = driver.find_elements(By.CSS_SELECTOR, "button[id^='add-to-cart']")
        
        for i in range(min(3, len(add_buttons))):
            print(f"  → Adding item {i+1}...")
            simulator.click_element(add_buttons[i])
            simulator.simulate_idle((0.5, 1.2))
        
        # View cart
        cart_icon = driver.find_element(By.CLASS_NAME, "shopping_cart_link")
        simulator.click_element(cart_icon)
        simulator.simulate_idle((2.0, 3.0))
        
        # Review cart items
        simulator.scroll_page('down', distance=300)
        simulator.simulate_idle((2.5, 4.0))
        
        # Change mind - remove an item
        print("  → Reconsidering... removing an item")
        simulator.simulate_idle((1.5, 2.5))
        
        remove_buttons = driver.find_elements(By.CSS_SELECTOR, "button[id^='remove']")
        if remove_buttons:
            simulator.click_element(remove_buttons[0])
            simulator.simulate_idle((1.0, 2.0))
        
        # Review again
        simulator.scroll_page('up', distance=200)
        simulator.simulate_idle((1.5, 2.5))
        
        print("✅ Cart Modification: Complete")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    """Run advanced e-commerce scenarios"""
    
    print("\n" + "="*70)
    print("ADVANCED E-COMMERCE SCENARIOS WITH HUMAN BEHAVIOR")
    print("="*70)
    
    # Scenario 1: Complete shopping journey
    test_ecommerce_shopping_journey()
    
    # Scenario 2: Product comparison
    test_product_comparison_behavior()
    
    # Scenario 3: Cart modification
    test_cart_modification_behavior()
    
    print("\n" + "="*70)
    print("✅ ALL ADVANCED SCENARIOS COMPLETED!")
    print("="*70)
