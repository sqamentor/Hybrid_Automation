"""
Selenium Engine Enhanced Features Demo

Demonstrates:
1. Better browser driver management with auto-download
2. Multiple browser support (Chrome, Firefox, Edge)
3. Selenium Grid support for distributed execution

Note: For Grid demo, you need a running Selenium Grid instance.
Start Grid with: docker-compose up -d
"""

import time
from framework.ui.selenium_engine import SeleniumEngine, DriverManagerError, GridConnectionError
from utils.logger import get_logger

logger = get_logger(__name__)


def demo_driver_management():
    """Demo 1: Better driver management with auto-download"""
    print("\n" + "="*70)
    print("DEMO 1: BETTER BROWSER DRIVER MANAGEMENT")
    print("="*70)
    
    # Test 1: Chrome with auto-driver management
    print("\n[Test 1] Chrome driver auto-management")
    engine = SeleniumEngine(
        headless=True,
        driver_cache_valid_range=7,  # Cache for 7 days
        enable_logging=False  # Suppress driver logs
    )
    
    try:
        engine.start(browser_type="chrome")
        print("✓ Chrome driver automatically downloaded and managed")
        
        # Get driver info
        info = engine.get_driver_info()
        print(f"  Session ID: {info['session_id']}")
        print(f"  Mode: {info['mode']}")
        
        # Test navigation
        engine.navigate("https://example.com")
        print(f"✓ Navigated to: {engine.driver.current_url}")
        print(f"  Page title: {engine.driver.title}")
        
        engine.stop()
        print("✓ Chrome engine stopped")
    except DriverManagerError as e:
        print(f"✗ Driver management failed: {e}")
    
    # Test 2: Firefox with auto-driver management
    print("\n[Test 2] Firefox driver auto-management")
    engine2 = SeleniumEngine(headless=True)
    
    try:
        engine2.start(browser_type="firefox")
        print("✓ Firefox driver automatically downloaded and managed")
        
        engine2.navigate("https://www.iana.org/domains/reserved")
        print(f"✓ Navigated to: {engine2.driver.title[:50]}")
        
        engine2.stop()
        print("✓ Firefox engine stopped")
    except DriverManagerError as e:
        print(f"✗ Driver management failed: {e}")
    except Exception as e:
        print(f"✗ Firefox test failed (may not be installed): {str(e)[:80]}")
    
    # Test 3: Edge with auto-driver management (Windows only)
    print("\n[Test 3] Edge driver auto-management")
    engine3 = SeleniumEngine(headless=True)
    
    try:
        engine3.start(browser_type="edge")
        print("✓ Edge driver automatically downloaded and managed")
        
        engine3.navigate("https://example.org")
        print(f"✓ Navigated to: {engine3.driver.title}")
        
        engine3.stop()
        print("✓ Edge engine stopped")
    except DriverManagerError as e:
        print(f"✗ Edge test skipped: {str(e)[:80]}")
    except Exception as e:
        print(f"✗ Edge test failed (may not be available): {str(e)[:80]}")


def demo_driver_caching():
    """Demo 2: Driver caching mechanism"""
    print("\n" + "="*70)
    print("DEMO 2: DRIVER CACHING MECHANISM")
    print("="*70)
    
    print("\n[Test] Multiple instances using cached driver")
    
    # First instance - downloads driver
    print("\n  Instance 1: Initial download")
    start_time = time.time()
    engine1 = SeleniumEngine(headless=True, driver_cache_valid_range=7)
    engine1.start(browser_type="chrome")
    elapsed1 = time.time() - start_time
    print(f"  ✓ Started in {elapsed1:.2f}s (includes download)")
    engine1.stop()
    
    # Second instance - uses cached driver
    print("\n  Instance 2: Using cached driver")
    start_time = time.time()
    engine2 = SeleniumEngine(headless=True, driver_cache_valid_range=7)
    engine2.start(browser_type="chrome")
    elapsed2 = time.time() - start_time
    print(f"  ✓ Started in {elapsed2:.2f}s (cached)")
    engine2.stop()
    
    # Third instance - uses cached driver
    print("\n  Instance 3: Using cached driver")
    start_time = time.time()
    engine3 = SeleniumEngine(headless=True, driver_cache_valid_range=7)
    engine3.start(browser_type="chrome")
    elapsed3 = time.time() - start_time
    print(f"  ✓ Started in {elapsed3:.2f}s (cached)")
    engine3.stop()
    
    print(f"\n  Summary:")
    print(f"  - Instance 1: {elapsed1:.2f}s (download)")
    print(f"  - Instance 2: {elapsed2:.2f}s (cached)")
    print(f"  - Instance 3: {elapsed3:.2f}s (cached)")
    print(f"  - Speedup: ~{elapsed1/elapsed2:.1f}x faster with caching")


def demo_grid_support():
    """Demo 3: Selenium Grid support"""
    print("\n" + "="*70)
    print("DEMO 3: SELENIUM GRID SUPPORT")
    print("="*70)
    
    # Test 1: Check if Grid is available
    print("\n[Test 1] Check Grid availability")
    grid_url = "http://localhost:4444/wd/hub"
    
    try:
        import requests
        status_url = "http://localhost:4444/status"
        response = requests.get(status_url, timeout=2)
        grid_available = response.status_code == 200
        
        if grid_available:
            print(f"✓ Selenium Grid is available at {grid_url}")
            grid_status = response.json()
            print(f"  Ready: {grid_status.get('value', {}).get('ready', False)}")
        else:
            print(f"✗ Grid not available at {grid_url}")
            print("  To start Grid: docker-compose up -d")
            return
    except Exception as e:
        print(f"✗ Grid not available: {e}")
        print("  To start Grid: docker-compose up -d")
        return
    
    # Test 2: Remote Chrome execution
    print("\n[Test 2] Remote Chrome execution on Grid")
    engine = SeleniumEngine(
        headless=True,
        grid_url=grid_url
    )
    
    try:
        engine.start(browser_type="chrome")
        print("✓ Connected to Grid (Chrome)")
        
        # Get driver info
        info = engine.get_driver_info()
        print(f"  Session ID: {info['session_id']}")
        print(f"  Mode: {info['mode']}")
        print(f"  Grid URL: {info['grid_url']}")
        
        # Navigate
        engine.navigate("https://example.com")
        print(f"✓ Navigated to: {engine.driver.title}")
        
        # Check Grid status
        status = engine.check_grid_status()
        if 'error' not in status:
            print(f"✓ Grid status checked successfully")
        
        engine.stop()
        print("✓ Remote session closed")
        
    except GridConnectionError as e:
        print(f"✗ Grid connection failed: {e}")
    except Exception as e:
        print(f"✗ Test failed: {e}")
    
    # Test 3: Remote Firefox execution
    print("\n[Test 3] Remote Firefox execution on Grid")
    engine2 = SeleniumEngine(
        headless=True,
        grid_url=grid_url,
        browser_version="latest"
    )
    
    try:
        engine2.start(browser_type="firefox")
        print("✓ Connected to Grid (Firefox)")
        
        info = engine2.get_driver_info()
        print(f"  Session ID: {info['session_id']}")
        
        engine2.navigate("https://example.org")
        print(f"✓ Navigated to: {engine2.driver.title}")
        
        engine2.stop()
        print("✓ Remote session closed")
        
    except Exception as e:
        print(f"✗ Firefox test failed: {str(e)[:80]}")
    
    # Test 4: Custom capabilities
    print("\n[Test 4] Grid with custom capabilities")
    engine3 = SeleniumEngine(
        headless=False,  # Visible browser on Grid node
        grid_url=grid_url,
        platform_name="ANY"
    )
    
    try:
        custom_caps = {
            "goog:loggingPrefs": {"browser": "ALL"},
            "pageLoadStrategy": "eager"
        }
        
        engine3.start(browser_type="chrome", capabilities=custom_caps)
        print("✓ Connected with custom capabilities")
        
        engine3.navigate("https://example.net")
        print(f"✓ Page loaded: {engine3.driver.title}")
        
        engine3.stop()
        print("✓ Session closed")
        
    except Exception as e:
        print(f"✗ Custom capabilities test failed: {str(e)[:80]}")


def demo_combined_features():
    """Demo 4: Combined features demonstration"""
    print("\n" + "="*70)
    print("DEMO 4: COMBINED FEATURES")
    print("="*70)
    
    print("\n[Scenario] Sequential test execution with different browsers")
    
    browsers = ["chrome", "firefox", "edge"]
    test_urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net"
    ]
    
    results = []
    
    for browser in browsers:
        try:
            engine = SeleniumEngine(
                headless=True,
                driver_cache_valid_range=7
            )
            
            engine.start(browser_type=browser)
            
            for url in test_urls:
                try:
                    engine.navigate(url)
                    title = engine.driver.title
                    results.append({
                        'browser': browser,
                        'url': url,
                        'title': title,
                        'success': True
                    })
                    print(f"  ✓ {browser.capitalize()}: {title[:40]}")
                except Exception as e:
                    results.append({
                        'browser': browser,
                        'url': url,
                        'success': False,
                        'error': str(e)[:50]
                    })
                    print(f"  ✗ {browser.capitalize()}: {str(e)[:50]}")
            
            engine.stop()
            
        except DriverManagerError as e:
            print(f"  ✗ {browser.capitalize()} skipped: {str(e)[:60]}")
        except Exception as e:
            print(f"  ✗ {browser.capitalize()} failed: {str(e)[:60]}")
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    print(f"\n  Summary:")
    print(f"  - Total tests: {len(results)}")
    print(f"  - Successful: {successful}")
    print(f"  - Failed: {len(results) - successful}")


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("SELENIUM ENGINE ENHANCED FEATURES DEMO")
    print("="*70)
    print("\nFeatures:")
    print("1. Better browser driver management with auto-download")
    print("2. Driver caching for faster startup")
    print("3. Multiple browser support (Chrome, Firefox, Edge)")
    print("4. Selenium Grid support for distributed execution")
    
    # Run demos
    demo_driver_management()
    demo_driver_caching()
    demo_grid_support()
    demo_combined_features()
    
    print("\n" + "="*70)
    print("DEMO COMPLETED")
    print("="*70)
    print("\nSummary:")
    print("✓ Driver management is automatic with webdriver-manager")
    print("✓ Driver caching speeds up subsequent launches")
    print("✓ Multiple browsers supported with unified API")
    print("✓ Selenium Grid enables distributed test execution")


if __name__ == "__main__":
    main()
