"""
Playwright Engine Enhanced Features Demo

Demonstrates:
1. Error handling for browser startup failures
2. Browser context pooling for parallel execution

Note: Playwright's sync API uses greenlets which are not thread-safe.
This demo shows the features without actual parallel threading.
For true parallel execution, use Playwright's async API or separate processes.
"""

import time
from framework.ui.playwright_engine import PlaywrightEngine, BrowserStartupError, ContextPoolExhausted
from utils.logger import get_logger

logger = get_logger(__name__)


def demo_error_handling():
    """Demo 1: Enhanced error handling for browser startup"""
    print("\n" + "="*70)
    print("DEMO 1: ERROR HANDLING FOR BROWSER STARTUP")
    print("="*70)
    
    # Test 1: Successful startup with retry capability
    print("\n[Test 1] Normal startup (should succeed)")
    engine = PlaywrightEngine(
        headless=True,
        max_retries=3,
        retry_delay=1.0
    )
    
    try:
        engine.start(browser_type="chromium")
        print("✓ Browser started successfully")
        engine.navigate("https://example.com")
        print(f"✓ Navigated to: {engine.page.url}")
        engine.stop()
        print("✓ Browser stopped cleanly")
    except BrowserStartupError as e:
        print(f"✗ Startup failed: {e}")
    
    # Test 2: Invalid browser type (should fail gracefully)
    print("\n[Test 2] Invalid browser type (should fail gracefully)")
    engine2 = PlaywrightEngine(max_retries=2, retry_delay=0.5)
    
    try:
        engine2.start(browser_type="invalid_browser")
        print("✗ Should not reach here")
    except BrowserStartupError as e:
        print(f"✓ Handled gracefully: {str(e)[:80]}...")
    
    # Test 3: Automatic cleanup on failure
    print("\n[Test 3] Automatic cleanup verification")
    engine3 = PlaywrightEngine(max_retries=1)
    try:
        # Simulate startup failure by using wrong browser
        engine3.start(browser_type="invalid")
    except BrowserStartupError:
        # Verify resources are cleaned up
        assert engine3.browser is None, "Browser should be None"
        assert engine3.context is None, "Context should be None"
        assert engine3.playwright is None, "Playwright should be None"
        print("✓ All resources cleaned up after failure")


def demo_context_pooling():
    """Demo 2: Browser context pooling for sequential execution"""
    print("\n" + "="*70)
    print("DEMO 2: BROWSER CONTEXT POOLING")
    print("="*70)
    
    # Test 1: Initialize pool
    print("\n[Test 1] Initialize context pool")
    engine = PlaywrightEngine(
        headless=True,
        enable_context_pool=True,
        pool_size=3
    )
    
    engine.start(browser_type="chromium")
    print("✓ Context pool created with size: 3")
    
    # Show initial stats
    stats = engine.get_context_pool_stats()
    print(f"  Pool Stats: {stats['contexts_available']} available, "
          f"{stats['contexts_in_use']} in use")
    
    # Test 2: Single context acquisition and release
    print("\n[Test 2] Single context acquisition and release")
    context1 = engine.acquire_pooled_context(timeout=2.0)
    print("✓ Context acquired from pool")
    
    stats = engine.get_context_pool_stats()
    print(f"  After acquire: {stats['contexts_available']} available, "
          f"{stats['contexts_in_use']} in use")
    
    engine.release_pooled_context(context1)
    print("✓ Context released back to pool")
    
    stats = engine.get_context_pool_stats()
    print(f"  After release: {stats['contexts_available']} available, "
          f"{stats['contexts_in_use']} in use")
    
    # Test 3: Sequential test execution demonstrating context reuse
    print("\n[Test 3] Sequential test execution with context reuse")
    
    test_urls = [
        "https://example.com",
        "https://www.iana.org/domains/reserved",
        "https://example.org",
        "https://example.net",
        "https://example.edu"
    ]
    
    print(f"  Running {len(test_urls)} sequential tests with context pool...")
    start_time = time.time()
    
    results = []
    for i, url in enumerate(test_urls):
        try:
            # Acquire context from pool
            context = engine.acquire_pooled_context(timeout=5.0)
            
            # Create page in this context
            page = context.new_page()
            
            # Navigate
            page.goto(url)
            title = page.title()
            
            # Cleanup
            page.close()
            engine.release_pooled_context(context)
            
            results.append({
                'test_id': i+1,
                'url': url,
                'title': title,
                'success': True
            })
            print(f"  ✓ Test {i+1}: {title[:50]}")
            
        except ContextPoolExhausted:
            results.append({
                'test_id': i+1,
                'url': url,
                'success': False,
                'error': 'Context pool exhausted'
            })
            print(f"  ✗ Test {i+1}: Context pool exhausted")
        except Exception as e:
            results.append({
                'test_id': i+1,
                'url': url,
                'success': False,
                'error': str(e)
            })
            print(f"  ✗ Test {i+1}: {str(e)[:50]}")
    
    elapsed = time.time() - start_time
    successful = sum(1 for r in results if r['success'])
    
    print(f"\n  Summary:")
    print(f"  - Total tests: {len(results)}")
    print(f"  - Successful: {successful}")
    print(f"  - Failed: {len(results) - successful}")
    print(f"  - Elapsed time: {elapsed:.2f}s")
    
    # Final stats
    stats = engine.get_context_pool_stats()
    print(f"\n  Final Pool Stats:")
    print(f"  - Total acquisitions: {stats['total_acquisitions']}")
    print(f"  - Total releases: {stats['total_releases']}")
    print(f"  - Wait timeouts: {stats['wait_timeouts']}")
    print(f"  - Contexts available: {stats['contexts_available']}")
    print(f"  - Contexts in use: {stats['contexts_in_use']}")
    
    # Cleanup
    engine.stop()
    print("\n✓ Engine stopped and pool closed")
    
    # Test 4: Pool exhaustion handling
    print("\n[Test 4] Pool exhaustion handling")
    engine2 = PlaywrightEngine(
        headless=True,
        enable_context_pool=True,
        pool_size=3  # Pool of 3 (engine takes 1, leaving 2)
    )
    engine2.start()
    
    # Acquire remaining contexts
    ctx1 = engine2.acquire_pooled_context(timeout=1.0)
    ctx2 = engine2.acquire_pooled_context(timeout=1.0)
    print("✓ Acquired 2 additional contexts (pool exhausted)")
    
    # Try to acquire when pool is empty
    try:
        ctx3 = engine2.acquire_pooled_context(timeout=1.0)
        print("✗ Should not reach here")
    except ContextPoolExhausted as e:
        print(f"✓ Pool exhaustion handled: {e}")
    
    # Release and verify recovery
    engine2.release_pooled_context(ctx1)
    print("✓ Released one context")
    
    ctx3 = engine2.acquire_pooled_context(timeout=1.0)
    print("✓ Successfully acquired after release")
    
    engine2.release_pooled_context(ctx2)
    engine2.release_pooled_context(ctx3)
    engine2.stop()


def demo_combined_features():
    """Demo 3: Combined features in realistic scenario"""
    print("\n" + "="*70)
    print("DEMO 3: COMBINED FEATURES (ERROR HANDLING + CONTEXT POOLING)")
    print("="*70)
    
    print("\n[Scenario] Start engine with error handling and context pooling")
    
    engine = PlaywrightEngine(
        headless=True,
        max_retries=3,
        retry_delay=1.0,
        enable_context_pool=True,
        pool_size=4
    )
    
    try:
        engine.start(browser_type="chromium")
        print("✓ Engine started with both features enabled")
        
        # Show configuration
        stats = engine.get_context_pool_stats()
        print("\n  Configuration:")
        print(f"  - Max retries: {engine.max_retries}")
        print(f"  - Retry delay: {engine.retry_delay}s")
        print(f"  - Context pooling: {stats['enabled']}")
        print(f"  - Pool size: {stats['pool_size']}")
        print(f"  - Contexts available: {stats['contexts_available']}")
        
        # Simulate sequential work with context reuse
        print("\n  Simulating sequential test execution with context reuse...")
        
        for i in range(10):
            context = engine.acquire_pooled_context()
            page = context.new_page()
            page.goto("https://example.com")
            time.sleep(0.1)
            page.close()
            engine.release_pooled_context(context)
        
        print(f"  ✓ Completed 10 sequential tests with context reuse")
        
        # Final stats
        stats = engine.get_context_pool_stats()
        print("\n  Final Stats:")
        print(f"  - Total acquisitions: {stats['total_acquisitions']}")
        print(f"  - Total releases: {stats['total_releases']}")
        print(f"  - All contexts returned: {stats['contexts_in_use'] == 0}")
        
        engine.stop()
        print("\n✓ Clean shutdown")
        
    except BrowserStartupError as e:
        print(f"✗ Failed to start: {e}")


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("PLAYWRIGHT ENGINE ENHANCED FEATURES DEMO")
    print("="*70)
    print("\nFeatures:")
    print("1. Error handling for browser startup failures")
    print("2. Browser context pooling for efficient context reuse")
    print("\nNote: Context pooling demonstrates resource reuse patterns.")
    print("For true parallel execution, use Playwright's async API or separate processes.")
    
    # Run demos
    demo_error_handling()
    demo_context_pooling()
    demo_combined_features()
    
    print("\n" + "="*70)
    print("DEMO COMPLETED")
    print("="*70)
    print("\nSummary:")
    print("✓ Error handling prevents crashes and enables automatic retry")
    print("✓ Context pooling enables efficient resource reuse")
    print("✓ Both features work together for production-ready testing")


if __name__ == "__main__":
    main()
