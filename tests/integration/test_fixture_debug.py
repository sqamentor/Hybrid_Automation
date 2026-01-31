"""Test to isolate fixture issue"""
import pytest

def test_with_bookslot_page_fixture(bookslot_page):
    """Test using bookslot_page fixture"""
    print("SUCCESS: bookslot_page fixture works!")
    assert bookslot_page is not None
