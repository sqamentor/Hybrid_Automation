"""
Playwright Context Pooling Example
Demonstrates Playwright context pooling for performance

This example shows:
1. Playwright context pooling and reuse
"""

import pytest


# ===================================================================
# PLAYWRIGHT CONTEXT POOLING EXAMPLE
# ===================================================================

@pytest.mark.playwright
@pytest.mark.pooling
@pytest.mark.modern_spa
def test_playwright_context_pooling():
    """
    Test Playwright context pooling
    Demonstrates reusing browser contexts for performance
    """
    from framework.ui.playwright_engine import PlaywrightEngine, ContextPool
    
    # Create context pool
    pool = ContextPool(max_size=5)
    
    # Create multiple engines sharing the pool
    engines = []
    for i in range(3):
        engine = PlaywrightEngine(browser_type="chromium", headless=True)
        engine.context_pool = pool
        engines.append(engine)
    
    try:
        # Execute parallel tasks
        for i, engine in enumerate(engines):
            engine.start()
            engine.navigate(f"https://example.com?task={i}")
            print(f"✓ Task {i} completed")
        
        # Check pool statistics
        print(f"\n✅ Context pooling test complete")
        print(f"   • Contexts created: {pool.current_size}")
        print(f"   • Max pool size: {pool.max_size}")
        
    finally:
        for engine in engines:
            engine.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
