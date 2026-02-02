"""
Modern Tests Configuration (Playwright-based)

This conftest.py provides fixtures and configuration for modern web application tests
using Playwright. All tests under tests/modern/ should use these fixtures.

Engine: Playwright
Target: Modern SPAs (React, Vue, Angular, etc.)
"""

import pytest
from typing import Generator
from playwright.sync_api import Page


# Marker registration is done in root conftest.py
# All test classes here should use @pytest.mark.playwright or @pytest.mark.modern_spa


# Additional modern-specific fixtures can be added here
# For now, inherits from root conftest.py
