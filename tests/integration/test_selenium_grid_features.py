"""Selenium Grid Integration Example Demonstrates Selenium Grid remote execution capabilities.

This example shows:
1. Selenium Grid support for remote execution
"""

import pytest

# ===================================================================
# SELENIUM GRID INTEGRATION EXAMPLE
# ===================================================================

@pytest.mark.selenium
@pytest.mark.grid
@pytest.mark.legacy_ui
def test_selenium_grid_execution():
    """Test Selenium Grid remote execution Demonstrates running tests on remote Selenium Grid."""
    from framework.ui.selenium_engine import SeleniumEngine

    # Configure for Grid execution
    engine = SeleniumEngine(
        browser_type="chrome",
        headless=False,
        use_grid=True,
        grid_url="http://selenium-hub:4444/wd/hub"
    )
    
    try:
        # Start engine (will use Grid)
        engine.start()
        
        # Perform actions
        engine.navigate("https://example.com")
        assert "Example Domain" in engine.get_page_title()
        
        print("✅ Selenium Grid execution successful")
        
    finally:
        engine.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
