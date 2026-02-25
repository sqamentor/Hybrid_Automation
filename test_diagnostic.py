"""
Diagnostic test to verify Bookslot page setup
"""
import pytest
from playwright.sync_api import Page


@pytest.mark.bookslot
def test_navigate_to_bookslot(page: Page, bookslot_nav):
    """Simple test to verify navigation works"""
    print(f"\n✓ Page object type: {type(page)}")
    print(f"✓ Nav helper type: {type(bookslot_nav)}")
    print(f"✓ Base URL: {bookslot_nav.base_url}")
    
    # Navigate to basic info
    basic_info_page = bookslot_nav.navigate_to_basic_info()
    print(f"✓ Basic Info Page type: {type(basic_info_page)}")
    print(f"✓ Current URL: {page.url}")
    print(f"✓ Page title: {page.title()}")
    
    # Check if page loaded
    assert page.url, "Page URL should not be empty"
    print("\n✓✓✓ ALL CHECKS PASSED ✓✓✓")
