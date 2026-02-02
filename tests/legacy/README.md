"""
Legacy Tests README

This directory is reserved for Selenium WebDriver-based tests targeting legacy web applications.

## When to Place Tests Here

Tests should go in tests/legacy/ when testing:
- Legacy JSP applications
- ASP.NET WebForms applications  
- Applications with iframes
- Applications with Flash/Silverlight
- Non-SPA applications with full page reloads
- Applications that don't work well with Playwright

## Marker Requirements

All test classes in this directory MUST use:
```python
@pytest.mark.selenium
@pytest.mark.legacy_ui
class TestLegacyFeature:
    pass
```

## Execution

Run legacy tests only:
```bash
pytest tests/legacy/ -v
pytest -m legacy_ui -v
pytest -m selenium -v
```

## Current Status

No legacy tests currently exist. All current applications use modern SPAs with Playwright.
This structure is in place for future legacy application testing needs.
"""
