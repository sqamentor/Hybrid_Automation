"""
Comprehensive tests for framework.core.async_smart_actions

Tests async Playwright operations, human behavior simulation,
pattern matching for browser-specific logic, and performance.

Author: Lokendra Singh
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio
from playwright.async_api import Browser, Locator, Page

from framework.core.async_smart_actions import (
    AsyncPageFactory,
    AsyncSmartActions,
)
from framework.models.config_models import BrowserEngine
from framework.models.test_models import TestContext


@pytest_asyncio.fixture
async def mock_page():
    """Create mock Playwright async page"""
    page = AsyncMock(spec=Page)
    page.url = "https://example.com"
    page.title = AsyncMock(return_value="Example Page")

    # Mock locator
    mock_locator = AsyncMock(spec=Locator)
    mock_locator.click = AsyncMock()
    mock_locator.fill = AsyncMock()
    mock_locator.type = AsyncMock()
    mock_locator.clear = AsyncMock()
    mock_locator.select_option = AsyncMock()
    mock_locator.is_visible = AsyncMock(return_value=True)
    mock_locator.text_content = AsyncMock(return_value="Sample Text")
    mock_locator.input_value = AsyncMock(return_value="Sample Value")
    mock_locator.wait_for = AsyncMock()
    mock_locator.hover = AsyncMock()
    mock_locator.get_attribute = AsyncMock(return_value="text")
    page.locator = Mock(return_value=mock_locator)

    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.wait_for_selector = AsyncMock()
    page.screenshot = AsyncMock(return_value=b"fake_screenshot")

    return page


@pytest.fixture
def test_context():
    """Create test context"""
    return TestContext(
        test_name="test_async_actions",
        test_id="async_001",
        test_suite="unit",
        project_name="automation_framework",
        browser_type=BrowserEngine.CHROMIUM,
        environment="qa",
    )


@pytest.mark.modern_spa
@pytest.mark.unit
class TestAsyncSmartActionsInit:
    """Test AsyncSmartActions initialization"""

    @pytest.mark.asyncio
    async def test_create_async_smart_actions(self, mock_page, test_context):
        """Test creating AsyncSmartActions"""
        actions = AsyncSmartActions(mock_page, test_context)
        assert actions.page == mock_page
        assert actions.context == test_context
        assert actions.enable_human is False

    @pytest.mark.asyncio
    async def test_enable_human_behavior(self, mock_page, test_context):
        """Test enabling human behavior"""
        actions = AsyncSmartActions(mock_page, test_context, enable_human=True)
        assert actions.enable_human is True


@pytest.mark.modern_spa
@pytest.mark.unit
class TestAsyncSmartActionsClick:
    """Test async click operations"""

    @pytest.mark.asyncio
    async def test_click_basic(self, mock_page, test_context):
        """Test basic async click"""
        actions = AsyncSmartActions(mock_page, test_context)

        await actions.click("button#submit", "Submit Button")

        mock_page.locator.assert_called_once_with("button#submit")
        mock_page.locator.return_value.click.assert_called_once()

    @pytest.mark.asyncio
    async def test_click_with_human_delay(self, mock_page, test_context):
        """Test click with human behavior delay"""
        actions = AsyncSmartActions(mock_page, test_context, enable_human=True)

        import time

        start = time.time()
        await actions.click("button#submit", "Submit Button")
        duration = time.time() - start

        # Should have some delay (human behavior)
        assert duration > 0.01  # At least some delay

    @pytest.mark.asyncio
    async def test_click_pattern_matching_chromium(self, mock_page, test_context):
        """Test click with pattern matching for Chromium"""
        test_context.browser_type = BrowserEngine.CHROMIUM

        actions = AsyncSmartActions(mock_page, test_context)
        await actions.click("button#submit")

        # Pattern matching should use force=False for Chromium
        mock_page.locator.return_value.click.assert_called()

    @pytest.mark.asyncio
    async def test_click_pattern_matching_firefox(self, mock_page, test_context):
        """Test click with pattern matching for Firefox"""
        test_context.browser_type = BrowserEngine.FIREFOX

        actions = AsyncSmartActions(mock_page, test_context)
        await actions.click("button#submit")

        mock_page.locator.return_value.click.assert_called()


@pytest.mark.modern_spa
@pytest.mark.unit
class TestAsyncSmartActionsFill:
    """Test async fill/type operations"""

    @pytest.mark.asyncio
    async def test_fill_basic(self, mock_page, test_context):
        """Test basic async fill"""
        actions = AsyncSmartActions(mock_page, test_context)

        await actions.fill("input#username", "testuser", "Username Field")

        mock_page.locator.assert_called_with("input#username")
        # Short text uses .type() for human-like behavior
        mock_page.locator.return_value.type.assert_called_once()

    @pytest.mark.asyncio
    async def test_fill_with_clear(self, mock_page, test_context):
        """Test fill with clear first"""
        actions = AsyncSmartActions(mock_page, test_context)

        mock_locator = mock_page.locator.return_value
        mock_locator.clear = AsyncMock()

        await actions.fill(mock_locator, "test@example.com", clear_first=True)

        # Should clear before filling
        mock_locator.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_fill_with_human_typing(self, mock_page, test_context):
        """Test fill with human-like typing delay"""
        actions = AsyncSmartActions(mock_page, test_context, enable_human=True)

        import time

        start = time.time()
        await actions.fill("input#username", "test", "Username")
        duration = time.time() - start

        # Should have delay for human typing
        assert duration > 0.01


@pytest.mark.modern_spa
@pytest.mark.unit
class TestAsyncSmartActionsSelect:
    """Test async select dropdown operations"""

    @pytest.mark.asyncio
    async def test_select_by_value(self, mock_page, test_context):
        """Test selecting option by value"""
        actions = AsyncSmartActions(mock_page, test_context)

        await actions.select("select#country", "US", "Country Dropdown")

        mock_page.locator.assert_called_with("select#country")
        mock_page.locator.return_value.select_option.assert_called_once()

    @pytest.mark.asyncio
    async def test_select_with_delay(self, mock_page, test_context):
        """Test select with human delay"""
        actions = AsyncSmartActions(mock_page, test_context, enable_human=True)

        await actions.select("select#country", "US")

        mock_page.locator.return_value.select_option.assert_called_once()


@pytest.mark.modern_spa
@pytest.mark.unit
class TestAsyncSmartActionsNavigate:
    """Test async navigation operations"""

    @pytest.mark.asyncio
    async def test_navigate_basic(self, mock_page, test_context):
        """Test basic async navigation"""
        actions = AsyncSmartActions(mock_page, test_context)

        await actions.navigate("https://example.com")

        mock_page.goto.assert_called_once_with("https://example.com", wait_until="load")

    @pytest.mark.asyncio
    async def test_navigate_with_wait_until(self, mock_page, test_context):
        """Test navigation with custom wait_until"""
        actions = AsyncSmartActions(mock_page, test_context)

        await actions.navigate("https://example.com", wait_until="networkidle")

        mock_page.goto.assert_called()


@pytest.mark.modern_spa
@pytest.mark.unit
class TestAsyncSmartActionsWait:
    """Test async wait operations"""

    @pytest.mark.asyncio
    async def test_wait_for_selector(self, mock_page, test_context):
        """Test waiting for selector"""
        actions = AsyncSmartActions(mock_page, test_context)

        mock_page.wait_for_selector = AsyncMock()

        await actions.wait_for_selector("div.loaded", timeout=5000)

        mock_page.wait_for_selector.assert_called_once_with(
            "div.loaded", timeout=5000, state="visible"
        )

    @pytest.mark.asyncio
    async def test_wait_for_element_visible(self, mock_page, test_context):
        """Test waiting for element to be visible"""
        actions = AsyncSmartActions(mock_page, test_context)

        mock_locator = mock_page.locator.return_value
        mock_locator.is_visible = AsyncMock(return_value=True)

        result = await actions.is_visible("div.content")

        assert result is True


@pytest.mark.modern_spa
@pytest.mark.unit
class TestAsyncSmartActionsGetters:
    """Test async getter operations"""

    @pytest.mark.asyncio
    async def test_get_text(self, mock_page, test_context):
        """Test getting element text"""
        actions = AsyncSmartActions(mock_page, test_context)

        mock_locator = mock_page.locator.return_value
        mock_locator.text_content = AsyncMock(return_value="Hello World")

        text = await actions.get_text("h1.title")

        assert text == "Hello World"

    @pytest.mark.asyncio
    async def test_get_attribute(self, mock_page, test_context):
        """Test getting element attribute"""
        actions = AsyncSmartActions(mock_page, test_context)

        mock_locator = mock_page.locator.return_value
        mock_locator.get_attribute = AsyncMock(return_value="button")

        attr = await actions.get_attribute("input", "type")

        assert attr == "button"


@pytest.mark.modern_spa
@pytest.mark.unit
class TestAsyncSmartActionsScreenshot:
    """Test async screenshot operations"""

    @pytest.mark.asyncio
    async def test_take_screenshot(self, mock_page, test_context):
        """Test taking screenshot"""
        actions = AsyncSmartActions(mock_page, test_context)

        mock_page.screenshot = AsyncMock()

        await actions.screenshot(path="test.png")

        mock_page.screenshot.assert_called_once()

    @pytest.mark.asyncio
    async def test_screenshot_full_page(self, mock_page, test_context):
        """Test taking full page screenshot"""
        actions = AsyncSmartActions(mock_page, test_context)

        mock_page.screenshot = AsyncMock()

        await actions.screenshot(path="test.png", full_page=True)

        mock_page.screenshot.assert_called()


@pytest.mark.modern_spa
@pytest.mark.unit
class TestAsyncPageFactory:
    """Test AsyncPageFactory context manager"""

    @pytest.mark.asyncio
    async def test_async_page_factory_context_manager(self):
        """Test AsyncPageFactory as async context manager"""
        mock_browser = AsyncMock(spec=Browser)
        mock_context = AsyncMock()
        mock_page = AsyncMock(spec=Page)

        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.close = AsyncMock()

        async with AsyncPageFactory(mock_browser) as page:
            assert page == mock_page

        # Should close context on exit
        mock_context.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_page_factory_with_options(self):
        """Test AsyncPageFactory with browser context options"""
        mock_browser = AsyncMock(spec=Browser)
        mock_context = AsyncMock()
        mock_page = AsyncMock(spec=Page)

        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.close = AsyncMock()

        viewport = {"width": 1920, "height": 1080}

        async with AsyncPageFactory(mock_browser, viewport=viewport) as page:
            assert page == mock_page

        mock_browser.new_context.assert_called()


@pytest.mark.modern_spa
@pytest.mark.unit
class TestAsyncSmartActionsHumanBehavior:
    """Test human behavior simulation"""

    @pytest.mark.asyncio
    async def test_human_delay_range(self, mock_page, test_context):
        """Test human delay is within expected range"""
        actions = AsyncSmartActions(mock_page, test_context, enable_human=True)

        import time

        # Test multiple delays to check randomness
        delays = []
        for _ in range(5):
            start = time.time()
            await actions._human_delay("before_click")
            delays.append(time.time() - start)

        # All delays should be > 0
        assert all(d > 0 for d in delays)

        # Should have some variance (not all identical)
        assert len(set([round(d, 2) for d in delays])) > 1

    @pytest.mark.asyncio
    async def test_no_delay_when_disabled(self, mock_page, test_context):
        """Test no delay when human behavior disabled"""
        actions = AsyncSmartActions(mock_page, test_context, enable_human=False)

        import time

        start = time.time()
        await actions._human_delay("before_click")
        duration = time.time() - start

        # Should be minimal delay (< 10ms)
        assert duration < 0.01


@pytest.mark.modern_spa
@pytest.mark.unit
class TestAsyncSmartActionsPerformance:
    """Test async performance characteristics"""

    @pytest.mark.asyncio
    async def test_parallel_operations(self, mock_page, test_context):
        """Test multiple async operations in parallel"""
        actions = AsyncSmartActions(mock_page, test_context)

        import time

        start = time.time()

        # Run multiple operations concurrently
        await asyncio.gather(
            actions.click("button#submit1"),
            actions.click("button#submit2"),
            actions.click("button#submit3"),
        )

        duration = time.time() - start

        # Should complete quickly (parallel execution)
        assert duration < 1.0  # Much faster than sequential

    @pytest.mark.asyncio
    async def test_async_vs_sync_benefit(self, mock_page, test_context):
        """Test async operations are faster than sync equivalent"""
        actions = AsyncSmartActions(mock_page, test_context)

        # Create mock locators with delayed clicks
        mock_locator1 = AsyncMock()
        mock_locator2 = AsyncMock()

        async def delayed_click1():
            await asyncio.sleep(0.1)

        async def delayed_click2():
            await asyncio.sleep(0.1)

        mock_locator1.click = delayed_click1
        mock_locator2.click = delayed_click2

        # Mock locator() to return different locators for different selectors
        def get_locator(selector):
            if selector == "button#1":
                return mock_locator1
            else:
                return mock_locator2

        mock_page.locator = get_locator

        import time

        start = time.time()

        # Multiple async calls should overlap
        await asyncio.gather(
            actions.click("button#1"),
            actions.click("button#2"),
        )

        duration = time.time() - start

        # Should be ~0.1s (parallel), not 0.2s (sequential)
        assert duration < 0.15


@pytest.mark.modern_spa
@pytest.mark.unit
class TestAsyncSmartActionsIntegration:
    """Integration tests for real-world scenarios"""

    @pytest.mark.asyncio
    async def test_complete_form_fill_flow(self, mock_page, test_context):
        """Test complete form filling workflow"""
        actions = AsyncSmartActions(mock_page, test_context)

        # Fill form
        await actions.fill("input#username", "testuser")
        await actions.fill("input#email", "test@example.com")
        await actions.select("select#country", "US")
        await actions.click("button#submit")

        # Verify all operations called
        assert mock_page.locator.call_count >= 4

    @pytest.mark.asyncio
    async def test_navigation_with_interactions(self, mock_page, test_context):
        """Test navigation followed by interactions"""
        actions = AsyncSmartActions(mock_page, test_context)

        # Navigate
        await actions.navigate("https://example.com")

        # Interact
        await actions.click("a#login")
        await actions.fill("input#username", "user")
        await actions.click("button#submit")

        # Verify navigation and interactions
        mock_page.goto.assert_called_once()
        assert mock_page.locator.call_count >= 3


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
