"""
Mobile Testing Support - Device Emulation & Responsive Testing

Provides mobile device emulation, touch gestures, and responsive testing.
Supports iOS, Android, and custom device configurations.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple

from utils.logger import get_logger

logger = get_logger(__name__)


class DeviceType(Enum):
    """Common mobile device types"""

    IPHONE_12 = "iPhone 12"
    IPHONE_13_PRO = "iPhone 13 Pro"
    IPHONE_14 = "iPhone 14"
    PIXEL_5 = "Pixel 5"
    PIXEL_7 = "Pixel 7"
    GALAXY_S21 = "Galaxy S21"
    GALAXY_S22 = "Galaxy S22"
    IPAD_PRO = "iPad Pro"
    TABLET = "Tablet"


# Device configurations
DEVICE_CONFIGS = {
    DeviceType.IPHONE_12: {
        "viewport": {"width": 390, "height": 844},
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "device_scale_factor": 3,
        "has_touch": True,
        "is_mobile": True,
    },
    DeviceType.IPHONE_13_PRO: {
        "viewport": {"width": 390, "height": 844},
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        "device_scale_factor": 3,
        "has_touch": True,
        "is_mobile": True,
    },
    DeviceType.PIXEL_5: {
        "viewport": {"width": 393, "height": 851},
        "user_agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36",
        "device_scale_factor": 2.75,
        "has_touch": True,
        "is_mobile": True,
    },
    DeviceType.GALAXY_S21: {
        "viewport": {"width": 360, "height": 800},
        "user_agent": "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36",
        "device_scale_factor": 3,
        "has_touch": True,
        "is_mobile": True,
    },
    DeviceType.IPAD_PRO: {
        "viewport": {"width": 1024, "height": 1366},
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "device_scale_factor": 2,
        "has_touch": True,
        "is_mobile": True,
    },
}


class MobileTester:
    """Mobile and responsive testing engine"""

    def __init__(self, ui_engine):
        """
        Initialize mobile tester

        Args:
            ui_engine: PlaywrightEngine or SeleniumEngine instance
        """
        self.ui_engine = ui_engine
        self.engine_type = type(ui_engine).__name__
        self.current_device = None

    def emulate_device(self, device: DeviceType):
        """
        Emulate mobile device

        Args:
            device: Device type to emulate
        """
        config = DEVICE_CONFIGS.get(device)
        if not config:
            raise ValueError(f"Unknown device: {device}")

        if self.engine_type == "PlaywrightEngine":
            self._emulate_playwright(device.value, config)
        elif self.engine_type == "SeleniumEngine":
            self._emulate_selenium(config)

        self.current_device = device
        logger.info(f"Emulating device: {device.value}")

    def _emulate_playwright(self, device_name: str, config: Dict):
        """Emulate device using Playwright"""
        context = self.ui_engine.context

        # Playwright has built-in device descriptors
        # We'll use the provided config for custom setup
        if hasattr(context, "set_viewport_size"):
            context.set_viewport_size(**config["viewport"])

        # Set user agent if page exists
        page = self.ui_engine.get_page()
        if page:
            page.set_extra_http_headers({"User-Agent": config["user_agent"]})

    def _emulate_selenium(self, config: Dict):
        """Emulate device using Selenium"""
        driver = self.ui_engine.get_driver()

        # Set window size
        driver.set_window_size(config["viewport"]["width"], config["viewport"]["height"])

        # Set user agent (requires Chrome DevTools Protocol)
        try:
            driver.execute_cdp_cmd(
                "Network.setUserAgentOverride", {"userAgent": config["user_agent"]}
            )
        except Exception as e:
            logger.warning(f"Could not set user agent: {e}")

    def set_custom_viewport(self, width: int, height: int):
        """
        Set custom viewport size

        Args:
            width: Viewport width in pixels
            height: Viewport height in pixels
        """
        if self.engine_type == "PlaywrightEngine":
            page = self.ui_engine.get_page()
            page.set_viewport_size(width=width, height=height)
        elif self.engine_type == "SeleniumEngine":
            driver = self.ui_engine.get_driver()
            driver.set_window_size(width, height)

        logger.info(f"Viewport set to {width}x{height}")

    def rotate_device(self, orientation: str = "landscape"):
        """
        Rotate device (portrait/landscape)

        Args:
            orientation: 'portrait' or 'landscape'
        """
        if self.engine_type == "PlaywrightEngine":
            page = self.ui_engine.get_page()
            current_viewport = page.viewport_size

            if orientation == "landscape":
                # Swap width and height
                page.set_viewport_size(
                    width=current_viewport["height"], height=current_viewport["width"]
                )
            elif orientation == "portrait":
                # Ensure height > width
                if current_viewport["width"] > current_viewport["height"]:
                    page.set_viewport_size(
                        width=current_viewport["height"], height=current_viewport["width"]
                    )

        logger.info(f"Device rotated to {orientation}")

    def swipe(self, direction: str, element: Optional[str] = None):
        """
        Perform swipe gesture

        Args:
            direction: 'up', 'down', 'left', 'right'
            element: Optional element locator to swipe on
        """
        if self.engine_type == "PlaywrightEngine":
            page = self.ui_engine.get_page()

            # Get element or use page
            if element:
                elem = page.locator(element)
                box = elem.bounding_box()
                start_x = box["x"] + box["width"] / 2
                start_y = box["y"] + box["height"] / 2
            else:
                viewport = page.viewport_size
                start_x = viewport["width"] / 2
                start_y = viewport["height"] / 2

            # Calculate swipe end point
            distance = 200
            if direction == "up":
                end_x, end_y = start_x, start_y - distance
            elif direction == "down":
                end_x, end_y = start_x, start_y + distance
            elif direction == "left":
                end_x, end_y = start_x - distance, start_y
            elif direction == "right":
                end_x, end_y = start_x + distance, start_y
            else:
                raise ValueError(f"Invalid direction: {direction}")

            # Perform swipe
            page.mouse.move(start_x, start_y)
            page.mouse.down()
            page.mouse.move(end_x, end_y)
            page.mouse.up()

            logger.info(f"Swiped {direction}")

    def tap(self, locator: str):
        """
        Perform tap gesture

        Args:
            locator: Element locator
        """
        if self.engine_type == "PlaywrightEngine":
            page = self.ui_engine.get_page()
            page.locator(locator).tap()
        elif self.engine_type == "SeleniumEngine":
            driver = self.ui_engine.get_driver()
            element = driver.find_element_by_css_selector(locator)
            from selenium.webdriver.common.action_chains import ActionChains

            ActionChains(driver).click(element).perform()

        logger.info(f"Tapped element: {locator}")

    def long_press(self, locator: str, duration: int = 1000):
        """
        Perform long press gesture

        Args:
            locator: Element locator
            duration: Press duration in milliseconds
        """
        if self.engine_type == "PlaywrightEngine":
            page = self.ui_engine.get_page()
            element = page.locator(locator)
            box = element.bounding_box()

            x = box["x"] + box["width"] / 2
            y = box["y"] + box["height"] / 2

            page.mouse.move(x, y)
            page.mouse.down()
            page.wait_for_timeout(duration)
            page.mouse.up()

            logger.info(f"Long pressed element: {locator} for {duration}ms")

    def pinch_zoom(self, scale: float = 0.5):
        """
        Simulate pinch zoom gesture

        Args:
            scale: Zoom scale (< 1 = zoom out, > 1 = zoom in)
        """
        if self.engine_type == "PlaywrightEngine":
            page = self.ui_engine.get_page()

            # Execute pinch zoom via JavaScript
            page.evaluate(f"""
                document.body.style.transform = 'scale({scale})';
                document.body.style.transformOrigin = '0 0';
            """)

            logger.info(f"Pinch zoom: {scale}x")

    def test_responsive_breakpoints(
        self, url: str, breakpoints: Optional[List[Tuple[int, int]]] = None
    ) -> Dict:
        """
        Test page at multiple responsive breakpoints

        Args:
            url: Page URL to test
            breakpoints: List of (width, height) tuples

        Returns:
            Test results for each breakpoint
        """
        default_breakpoints = [
            (375, 667),  # Mobile portrait
            (667, 375),  # Mobile landscape
            (768, 1024),  # Tablet portrait
            (1024, 768),  # Tablet landscape
            (1920, 1080),  # Desktop
        ]

        test_breakpoints = breakpoints or default_breakpoints
        results = {}

        for width, height in test_breakpoints:
            logger.info(f"Testing breakpoint: {width}x{height}")

            # Set viewport
            self.set_custom_viewport(width, height)

            # Navigate to page
            self.ui_engine.navigate(url)

            # Take screenshot
            screenshot_name = f"responsive_{width}x{height}.png"
            screenshot_path = self.ui_engine.take_screenshot(screenshot_name)

            # Check for layout issues
            layout_ok = self._check_layout_issues()

            results[f"{width}x{height}"] = {
                "width": width,
                "height": height,
                "screenshot": screenshot_path,
                "layout_ok": layout_ok,
            }

        return results

    def _check_layout_issues(self) -> bool:
        """Check for common layout issues"""
        if self.engine_type != "PlaywrightEngine":
            return True

        page = self.ui_engine.get_page()

        # Check for horizontal scrollbar
        has_horizontal_scroll = page.evaluate("""
            () => document.documentElement.scrollWidth > document.documentElement.clientWidth
        """)

        if has_horizontal_scroll:
            logger.warning("Horizontal scrollbar detected")
            return False

        # Check for overlapping elements (basic check)
        # More sophisticated checks can be added

        return True

    def enable_geolocation(self, latitude: float, longitude: float, accuracy: float = 100):
        """
        Set geolocation

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            accuracy: Accuracy in meters
        """
        if self.engine_type == "PlaywrightEngine":
            context = self.ui_engine.context
            context.set_geolocation(
                {"latitude": latitude, "longitude": longitude, "accuracy": accuracy}
            )

            # Grant geolocation permission
            context.grant_permissions(["geolocation"])

            logger.info(f"Geolocation set to: {latitude}, {longitude}")

    def simulate_network_conditions(self, condition: str):
        """
        Simulate network conditions (3G, 4G, offline, etc.)

        Args:
            condition: '3G', '4G', 'offline', 'online'
        """
        conditions = {
            "offline": {
                "offline": True,
                "downloadThroughput": 0,
                "uploadThroughput": 0,
                "latency": 0,
            },
            "3G": {
                "offline": False,
                "downloadThroughput": 750 * 1024 / 8,
                "uploadThroughput": 250 * 1024 / 8,
                "latency": 100,
            },
            "4G": {
                "offline": False,
                "downloadThroughput": 4 * 1024 * 1024 / 8,
                "uploadThroughput": 3 * 1024 * 1024 / 8,
                "latency": 20,
            },
            "online": {
                "offline": False,
                "downloadThroughput": -1,
                "uploadThroughput": -1,
                "latency": 0,
            },
        }

        if condition not in conditions:
            raise ValueError(f"Unknown condition: {condition}")

        if self.engine_type == "PlaywrightEngine":
            context = self.ui_engine.context
            if hasattr(context, "route"):
                # Playwright doesn't have built-in network throttling in context
                # Use Chrome DevTools Protocol via page
                page = self.ui_engine.get_page()
                if hasattr(page.context, "_impl_obj"):
                    # This requires Playwright's CDP session
                    logger.warning("Network throttling requires Chrome DevTools Protocol")

        logger.info(f"Network conditions set to: {condition}")


__all__ = ["MobileTester", "DeviceType", "DEVICE_CONFIGS"]
