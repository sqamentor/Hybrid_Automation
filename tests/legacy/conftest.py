"""
Legacy Tests Configuration (Selenium-based)

This conftest.py provides fixtures and configuration for legacy web application tests
using Selenium WebDriver. All tests under tests/legacy/ should use these fixtures.

Engine: Selenium WebDriver
Target: Legacy UIs (JSP, ASP.NET, iframes, etc.)
"""

import pytest


# Marker registration is done in root conftest.py
# All test classes here should use @pytest.mark.selenium or @pytest.mark.legacy_ui


# Selenium-specific fixtures would be added here when legacy tests are created
