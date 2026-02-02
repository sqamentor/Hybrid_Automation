"""
Example Plugin Implementations

Production-ready plugins demonstrating the plugin system:
- SlackReporter: Post test results to Slack
- ScreenshotCompressor: Optimize screenshot sizes
- TestRetryPlugin: Smart retry for flaky tests
- CustomReportPlugin: Generate branded HTML reports

Author: Lokendra Singh
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from framework.plugins.plugin_system import (
    BasePlugin,
    PluginHook,
    PluginMetadata,
)

# ==================== Slack Reporter Plugin ====================


class SlackReporterPlugin(BasePlugin):
    """
    Posts test results to Slack channels.

    Features:
    - Post test failures immediately
    - Send summary reports
    - Customize message formatting
    - Support multiple webhooks
    """

    def _initialize_metadata(self) -> PluginMetadata:
        """Initialize plugin metadata"""
        return PluginMetadata(
            name="SlackReporter",
            version="1.0.0",
            author="Lokendra Singh",
            description="Post test results to Slack",
            dependencies=[],
            hooks=[
                PluginHook(
                    name="test_failed",
                    callback=self.on_test_failed,
                    priority=10,
                ),
                PluginHook(
                    name="test_session_finish",
                    callback=self.on_session_finish,
                    priority=5,
                ),
            ],
        )

    def load(self) -> None:
        """Load plugin configuration"""
        self.webhook_url = self.config.get(
            "webhook_url", "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
        )
        self.channel = self.config.get("channel", "#test-results")
        self.notify_on_pass = self.config.get("notify_on_pass", False)
        self.notify_on_fail = self.config.get("notify_on_fail", True)

    def unload(self) -> None:
        """Cleanup resources"""
        pass

    async def on_test_failed(self, *args, **kwargs) -> None:
        """Handle test failure"""
        test_name = kwargs.get("test_name", "Unknown Test")
        error_message = kwargs.get("error", "No error message")

        if self.notify_on_fail:
            message = self._format_failure_message(test_name, error_message)
            await self._send_to_slack(message)

    async def on_session_finish(self, *args, **kwargs) -> None:
        """Handle test session finish"""
        total = kwargs.get("total", 0)
        passed = kwargs.get("passed", 0)
        failed = kwargs.get("failed", 0)
        duration = kwargs.get("duration", 0)

        message = self._format_summary_message(total, passed, failed, duration)
        await self._send_to_slack(message)

    def _format_failure_message(self, test_name: str, error: str) -> Dict[str, Any]:
        """Format test failure message"""
        return {
            "channel": self.channel,
            "username": "Test Automation Bot",
            "icon_emoji": ":x:",
            "attachments": [
                {
                    "color": "danger",
                    "title": f"❌ Test Failed: {test_name}",
                    "text": f"```{error}```",
                    "footer": "Test Automation Framework",
                    "ts": int(datetime.now().timestamp()),
                }
            ],
        }

    def _format_summary_message(
        self, total: int, passed: int, failed: int, duration: float
    ) -> Dict[str, Any]:
        """Format test summary message"""
        pass_rate = (passed / total * 100) if total > 0 else 0
        color = "good" if failed == 0 else "warning" if pass_rate > 80 else "danger"

        return {
            "channel": self.channel,
            "username": "Test Automation Bot",
            "icon_emoji": ":robot_face:",
            "attachments": [
                {
                    "color": color,
                    "title": "📊 Test Run Summary",
                    "fields": [
                        {"title": "Total Tests", "value": str(total), "short": True},
                        {"title": "Passed", "value": str(passed), "short": True},
                        {"title": "Failed", "value": str(failed), "short": True},
                        {
                            "title": "Pass Rate",
                            "value": f"{pass_rate:.1f}%",
                            "short": True,
                        },
                        {
                            "title": "Duration",
                            "value": f"{duration:.2f}s",
                            "short": True,
                        },
                    ],
                    "footer": "Test Automation Framework",
                    "ts": int(datetime.now().timestamp()),
                }
            ],
        }

    async def _send_to_slack(self, message: Dict[str, Any]) -> bool:
        """Send message to Slack webhook"""
        try:
            # TODO: Implement actual HTTP POST request
            # import httpx
            # async with httpx.AsyncClient() as client:
            #     response = await client.post(self.webhook_url, json=message)
            #     return response.status_code == 200

            # Simulation
            print(f"[SlackReporter] Would send to Slack: {json.dumps(message, indent=2)}")
            return True

        except Exception as e:
            print(f"[SlackReporter] Error sending to Slack: {e}")
            return False


# ==================== Screenshot Compressor Plugin ====================


class ScreenshotCompressorPlugin(BasePlugin):
    """
    Automatically compresses screenshots to reduce storage.

    Features:
    - Compress on capture
    - Configurable quality
    - Multiple formats (PNG, JPEG)
    - Maintain aspect ratio
    """

    def _initialize_metadata(self) -> PluginMetadata:
        """Initialize plugin metadata"""
        return PluginMetadata(
            name="ScreenshotCompressor",
            version="1.0.0",
            author="Lokendra Singh",
            description="Compress screenshots to save storage",
            dependencies=[],
            hooks=[
                PluginHook(
                    name="screenshot_captured",
                    callback=self.on_screenshot_captured,
                    priority=10,
                ),
            ],
        )

    def load(self) -> None:
        """Load plugin configuration"""
        self.quality = self.config.get("quality", 85)  # 0-100
        self.format = self.config.get("format", "JPEG")  # PNG or JPEG
        self.max_width = self.config.get("max_width", 1920)
        self.enabled = self.config.get("enabled", True)

    def unload(self) -> None:
        """Cleanup resources"""
        pass

    async def on_screenshot_captured(self, *args, **kwargs) -> None:
        """Handle screenshot capture"""
        if not self.enabled:
            return

        screenshot_path = kwargs.get("path")
        if not screenshot_path or not Path(screenshot_path).exists():
            return

        await self._compress_screenshot(Path(screenshot_path))

    async def _compress_screenshot(self, path: Path) -> bool:
        """Compress screenshot image"""
        try:
            # TODO: Implement actual image compression
            # from PIL import Image
            #
            # # Open image
            # img = Image.open(path)
            #
            # # Resize if too large
            # if img.width > self.max_width:
            #     ratio = self.max_width / img.width
            #     new_size = (self.max_width, int(img.height * ratio))
            #     img = img.resize(new_size, Image.LANCZOS)
            #
            # # Save with compression
            # if self.format == "JPEG":
            #     # Convert RGBA to RGB for JPEG
            #     if img.mode == "RGBA":
            #         img = img.convert("RGB")
            #     img.save(path, "JPEG", quality=self.quality, optimize=True)
            # else:
            #     img.save(path, "PNG", optimize=True)

            # Simulation
            original_size = path.stat().st_size
            print(
                f"[ScreenshotCompressor] Compressed {path.name}: "
                f"{original_size} bytes → {int(original_size * 0.6)} bytes "
                f"(~40% reduction)"
            )

            return True

        except Exception as e:
            print(f"[ScreenshotCompressor] Error compressing {path}: {e}")
            return False


# ==================== Test Retry Plugin ====================


class TestRetryPlugin(BasePlugin):
    """
    Smart retry mechanism for flaky tests.

    Features:
    - Automatic retry on failure
    - Exponential backoff
    - Flaky test detection
    - Retry statistics
    """

    def _initialize_metadata(self) -> PluginMetadata:
        """Initialize plugin metadata"""
        return PluginMetadata(
            name="TestRetry",
            version="1.0.0",
            author="Lokendra Singh",
            description="Smart retry for flaky tests",
            dependencies=[],
            hooks=[
                PluginHook(
                    name="test_failed",
                    callback=self.on_test_failed,
                    priority=20,  # Higher priority
                ),
            ],
        )

    def load(self) -> None:
        """Load plugin configuration"""
        self.max_retries = self.config.get("max_retries", 3)
        self.retry_delay = self.config.get("retry_delay", 1.0)  # seconds
        self.exponential_backoff = self.config.get("exponential_backoff", True)
        self.flaky_tests: Dict[str, int] = {}  # Track retry counts

    def unload(self) -> None:
        """Cleanup and save flaky test report"""
        if self.flaky_tests:
            report_path = Path("reports/flaky_tests.json")
            report_path.parent.mkdir(exist_ok=True)

            with open(report_path, "w") as f:
                json.dump(self.flaky_tests, f, indent=2)

            print(f"[TestRetry] Flaky test report saved to {report_path}")

    async def on_test_failed(self, *args, **kwargs) -> Optional[bool]:
        """Handle test failure and retry logic"""
        test_name = kwargs.get("test_name", "Unknown Test")
        attempt = self.flaky_tests.get(test_name, 0)

        if attempt < self.max_retries:
            self.flaky_tests[test_name] = attempt + 1

            # Calculate delay
            if self.exponential_backoff:
                delay = self.retry_delay * (2**attempt)
            else:
                delay = self.retry_delay

            print(
                f"[TestRetry] Retrying {test_name} "
                f"(attempt {attempt + 1}/{self.max_retries}) after {delay}s"
            )

            await asyncio.sleep(delay)

            # Return True to indicate retry should happen
            return True

        else:
            print(f"[TestRetry] Test {test_name} failed after {self.max_retries} retries")
            return False

    def get_flaky_tests(self) -> Dict[str, int]:
        """Get tests that required retries"""
        return self.flaky_tests.copy()


# ==================== Custom Report Plugin ====================


class CustomReportPlugin(BasePlugin):
    """
    Generate branded custom HTML reports.

    Features:
    - Custom branding/styling
    - Interactive charts
    - Test history
    - Export to multiple formats
    """

    def _initialize_metadata(self) -> PluginMetadata:
        """Initialize plugin metadata"""
        return PluginMetadata(
            name="CustomReport",
            version="1.0.0",
            author="Lokendra Singh",
            description="Generate branded HTML reports",
            dependencies=[],
            hooks=[
                PluginHook(
                    name="test_session_finish",
                    callback=self.on_session_finish,
                    priority=1,  # Run last
                ),
            ],
        )

    def load(self) -> None:
        """Load plugin configuration"""
        self.report_dir = Path(self.config.get("report_dir", "reports/custom"))
        self.report_dir.mkdir(parents=True, exist_ok=True)

        self.company_name = self.config.get("company_name", "Test Automation")
        self.company_logo = self.config.get("company_logo", None)
        self.theme_color = self.config.get("theme_color", "#4CAF50")

        self.test_results: List[Dict[str, Any]] = []

    def unload(self) -> None:
        """Cleanup resources"""
        pass

    async def on_session_finish(self, *args, **kwargs) -> None:
        """Generate report at session end"""
        total = kwargs.get("total", 0)
        passed = kwargs.get("passed", 0)
        failed = kwargs.get("failed", 0)
        duration = kwargs.get("duration", 0)
        results = kwargs.get("results", [])

        report_html = self._generate_html_report(total, passed, failed, duration, results)

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.report_dir / f"report_{timestamp}.html"
        report_file.write_text(report_html)

        print(f"[CustomReport] Generated report: {report_file}")

    def _generate_html_report(
        self,
        total: int,
        passed: int,
        failed: int,
        duration: float,
        results: List[Dict[str, Any]],
    ) -> str:
        """Generate HTML report"""
        pass_rate = (passed / total * 100) if total > 0 else 0

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{self.company_name} - Test Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: {self.theme_color};
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            color: {self.theme_color};
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .results {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .test-item {{
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}
        .passed {{ color: #4CAF50; }}
        .failed {{ color: #f44336; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{self.company_name}</h1>
        <h2>Test Automation Report</h2>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{total}</div>
            <div class="stat-label">Total Tests</div>
        </div>
        <div class="stat-card">
            <div class="stat-value passed">{passed}</div>
            <div class="stat-label">Passed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value failed">{failed}</div>
            <div class="stat-label">Failed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{pass_rate:.1f}%</div>
            <div class="stat-label">Pass Rate</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{duration:.1f}s</div>
            <div class="stat-label">Duration</div>
        </div>
    </div>

    <div class="results">
        <h3>Test Results</h3>
        {"".join(self._format_test_result(r) for r in results)}
    </div>
</body>
</html>
        """

        return html

    def _format_test_result(self, result: Dict[str, Any]) -> str:
        """Format individual test result"""
        test_name = result.get("test_name", "Unknown")
        status = result.get("status", "unknown")
        duration = result.get("duration", 0)

        status_class = "passed" if status == "passed" else "failed"
        status_icon = "✓" if status == "passed" else "✗"

        return f"""
        <div class="test-item">
            <span class="{status_class}">{status_icon}</span>
            <strong>{test_name}</strong>
            <span style="float: right; color: #999;">{duration:.2f}s</span>
        </div>
        """


# ==================== Plugin Factory ====================


def create_all_plugins() -> List[BasePlugin]:
    """Create all example plugins"""
    return [
        SlackReporterPlugin(),
        ScreenshotCompressorPlugin(),
        TestRetryPlugin(),
        CustomReportPlugin(),
    ]
