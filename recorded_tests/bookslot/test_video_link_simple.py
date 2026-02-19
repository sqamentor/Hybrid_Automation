"""
Simple test to verify video links in HTML report
This test always passes so we can verify the video link feature works
"""
import pytest
import time

@pytest.mark.ui
def test_simple_video_link_verification(bookslot_page):
    """
    Simple test that just opens a page and passes.
    Used to verify that video links appear in HTML reports.
    """
    page = bookslot_page.page
    
    # Navigate to URL
    page.goto(bookslot_page.url)
    
    # Wait a bit so there's actual video content
    time.sleep(3)
    
    # Test passes
    assert True, "Test passed - check HTML report for video link"
