"""
Simple test to verify video links in HTML reports.
This test is designed to complete quickly for verification purposes.
"""
import pytest
import time
from playwright.sync_api import Page


@pytest.mark.ui
def test_video_link_simple(context, multi_project_config, env, project):
    """
    Simple test that navigates to a URL and passes.
    Used to verify video links appear in HTML reports.
    """
    # Use the shared context fixture (video recording enabled)
    page = context.new_page()
    
    # Get URL from config
    url = multi_project_config[project]["ui_url"]
    
    # Navigate and wait a bit
    page.goto(url, wait_until="domcontentloaded", timeout=10000)
    time.sleep(2)
    
    # Simple assertion
    assert page.title(), "Page should have a title"
    
    # Don't close page explicitly - let context teardown handle it
    # This ensures video is properly captured and renamed
