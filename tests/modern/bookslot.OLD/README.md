"""
Modern SPA Tests - Bookslot Application

All Playwright-based tests for the Bookslot application.

## Marker Requirements

All test classes MUST use:
```python
@pytest.mark.playwright
@pytest.mark.modern_spa
@pytest.mark.bookslot
class TestBookslotFeature:
    pass
```

## Test Organization

- Feature-specific tests: test_bookslot_<feature>_*.py
- Page-specific tests: test_bookslot_<page>_page*.py
- E2E flows: test_bookslot_complete_flows.py
"""
