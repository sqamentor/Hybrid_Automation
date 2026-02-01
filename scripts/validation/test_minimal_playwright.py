"""Minimal Playwright sync test to isolate the issue."""
import pytest

def test_sync_playwright():
    """Test Playwright sync API in pytest."""
    from playwright.sync_api import sync_playwright
    
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    page.goto("https://example.com")
    assert "Example Domain" in page.title()
    
    context.close()
    browser.close()
    playwright.stop()
    print("SUCCESS: Playwright sync API works!")
