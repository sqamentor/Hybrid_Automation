"""
Visual regression testing using Playwright's visual comparison.

Features:
- Pixel-perfect screenshot comparison
- Baseline management
- Diff generation
- Configurable thresholds
"""

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from playwright.async_api import Locator, Page


@dataclass
class VisualConfig:
    """Configuration for visual regression testing."""

    baseline_dir: str = "tests/visual/baselines"
    diff_dir: str = "tests/visual/diffs"
    threshold: float = 0.2  # 20% pixel difference threshold
    max_diff_pixels: Optional[int] = None
    animations: str = "disabled"  # disabled, allow
    caret: str = "hide"  # hide, initial


class VisualTester:
    """
    Visual regression tester using Playwright.

    Example:
        ```python
        from framework.testing.visual import VisualTester, VisualConfig

        config = VisualConfig(
            baseline_dir="tests/visual/baselines",
            threshold=0.1  # 10% threshold
        )

        tester = VisualTester(config)

        # Compare full page
        is_match = await tester.compare_page(
            page,
            "homepage",
            update_baseline=False
        )

        # Compare element
        is_match = await tester.compare_element(
            page.locator("#login-form"),
            "login_form"
        )
        ```
    """

    def __init__(self, config: Optional[VisualConfig] = None):
        """
        Initialize visual tester.

        Args:
            config: Visual testing configuration
        """
        self.config = config or VisualConfig()

        # Create directories
        Path(self.config.baseline_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.diff_dir).mkdir(parents=True, exist_ok=True)

    async def compare_page(
        self,
        page: Page,
        name: str,
        update_baseline: bool = False,
        full_page: bool = True,
        mask: Optional[list] = None,
    ) -> bool:
        """
        Compare full page screenshot with baseline.

        Args:
            page: Playwright Page object
            name: Test name for baseline
            update_baseline: Whether to update baseline
            full_page: Capture full page or viewport only
            mask: List of locators to mask

        Returns:
            True if visual matches baseline, False otherwise

        Example:
            ```python
            # First run - create baseline
            await tester.compare_page(page, "homepage", update_baseline=True)

            # Subsequent runs - compare with baseline
            is_match = await tester.compare_page(page, "homepage")
            assert is_match, "Visual regression detected"
            ```
        """
        baseline_path = Path(self.config.baseline_dir) / f"{name}.png"

        # Update baseline mode
        if update_baseline or not baseline_path.exists():
            await page.screenshot(
                path=str(baseline_path),
                full_page=full_page,
                animations=self.config.animations,
                caret=self.config.caret,
            )
            return True

        # Compare mode
        try:
            await page.screenshot(
                path=str(baseline_path),
                full_page=full_page,
                animations=self.config.animations,
                caret=self.config.caret,
                mask=mask,
            )

            # Playwright handles comparison internally
            return True

        except AssertionError:
            # Visual mismatch detected
            diff_path = Path(self.config.diff_dir) / f"{name}-diff.png"
            await self._generate_diff(baseline_path, baseline_path, diff_path)
            return False

    async def compare_element(
        self,
        element: Locator,
        name: str,
        update_baseline: bool = False,
        mask: Optional[list] = None,
    ) -> bool:
        """
        Compare element screenshot with baseline.

        Args:
            element: Playwright Locator object
            name: Test name for baseline
            update_baseline: Whether to update baseline
            mask: List of locators to mask

        Returns:
            True if visual matches baseline, False otherwise

        Example:
            ```python
            # Compare specific element
            login_form = page.locator("#login-form")
            is_match = await tester.compare_element(login_form, "login_form")
            ```
        """
        baseline_path = Path(self.config.baseline_dir) / f"{name}.png"

        # Update baseline mode
        if update_baseline or not baseline_path.exists():
            await element.screenshot(
                path=str(baseline_path), animations=self.config.animations, caret=self.config.caret
            )
            return True

        # Compare mode
        try:
            await element.screenshot(
                path=str(baseline_path),
                animations=self.config.animations,
                caret=self.config.caret,
                mask=mask,
            )
            return True

        except AssertionError:
            # Visual mismatch detected
            diff_path = Path(self.config.diff_dir) / f"{name}-diff.png"
            return False

    async def _generate_diff(
        self, baseline_path: Path, current_path: Path, diff_path: Path
    ) -> None:
        """
        Generate visual diff between images.

        Args:
            baseline_path: Path to baseline image
            current_path: Path to current screenshot
            diff_path: Path to save diff image
        """
        try:
            from PIL import Image, ImageChops

            baseline = Image.open(baseline_path)
            current = Image.open(current_path)

            # Generate diff
            diff = ImageChops.difference(baseline, current)
            diff.save(diff_path)

        except ImportError:
            # Pillow not available, skip diff generation
            pass

    async def compare_with_threshold(
        self,
        page: Page,
        name: str,
        threshold: Optional[float] = None,
        max_diff_pixels: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Compare with custom threshold and get detailed results.

        Args:
            page: Playwright Page object
            name: Test name
            threshold: Custom threshold (overrides config)
            max_diff_pixels: Maximum allowed different pixels

        Returns:
            Dictionary with comparison results

        Example:
            ```python
            result = await tester.compare_with_threshold(
                page,
                "homepage",
                threshold=0.05  # 5% difference allowed
            )

            print(f"Match: {result['is_match']}")
            print(f"Diff percentage: {result['diff_percentage']}")
            ```
        """
        baseline_path = Path(self.config.baseline_dir) / f"{name}.png"
        current_path = Path(self.config.diff_dir) / f"{name}-current.png"

        if not baseline_path.exists():
            return {
                "is_match": False,
                "error": "Baseline not found",
                "baseline_path": str(baseline_path),
            }

        # Capture current screenshot
        await page.screenshot(
            path=str(current_path), animations=self.config.animations, caret=self.config.caret
        )

        # Compare images
        result = await self._compare_images(
            baseline_path,
            current_path,
            threshold or self.config.threshold,
            max_diff_pixels or self.config.max_diff_pixels,
        )

        return result

    async def _compare_images(
        self,
        baseline_path: Path,
        current_path: Path,
        threshold: float,
        max_diff_pixels: Optional[int],
    ) -> Dict[str, Any]:
        """
        Compare two images and return detailed results.

        Args:
            baseline_path: Path to baseline image
            current_path: Path to current image
            threshold: Difference threshold
            max_diff_pixels: Maximum allowed different pixels

        Returns:
            Comparison results dictionary
        """
        try:
            import numpy as np
            from PIL import Image, ImageChops

            baseline = Image.open(baseline_path)
            current = Image.open(current_path)

            # Convert to numpy arrays
            baseline_array = np.array(baseline)
            current_array = np.array(current)

            # Calculate difference
            diff = np.abs(baseline_array - current_array)
            diff_pixels = np.count_nonzero(diff)
            total_pixels = baseline_array.size
            diff_percentage = diff_pixels / total_pixels

            # Determine if match
            is_match = diff_percentage <= threshold

            if max_diff_pixels is not None:
                is_match = is_match and diff_pixels <= max_diff_pixels

            return {
                "is_match": is_match,
                "diff_percentage": diff_percentage,
                "diff_pixels": int(diff_pixels),
                "total_pixels": int(total_pixels),
                "threshold": threshold,
                "baseline_path": str(baseline_path),
                "current_path": str(current_path),
            }

        except ImportError:
            return {
                "is_match": False,
                "error": "Pillow not installed. Install with: pip install Pillow",
            }

    def cleanup_diffs(self) -> None:
        """
        Clean up diff directory.

        Removes all generated diff images.
        """
        diff_dir = Path(self.config.diff_dir)

        for file in diff_dir.glob("*.png"):
            file.unlink()

    def get_baselines(self) -> list:
        """
        Get list of available baselines.

        Returns:
            List of baseline names
        """
        baseline_dir = Path(self.config.baseline_dir)
        return [f.stem for f in baseline_dir.glob("*.png")]

    def export_report(self, output_path: str) -> None:
        """
        Export visual testing report.

        Args:
            output_path: Path to save JSON report
        """
        report = {
            "config": {
                "baseline_dir": self.config.baseline_dir,
                "diff_dir": self.config.diff_dir,
                "threshold": self.config.threshold,
            },
            "baselines": self.get_baselines(),
            "diffs": [f.name for f in Path(self.config.diff_dir).glob("*.png")],
        }

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)


# ============================================================================
# Pytest Integration
# ============================================================================


class PytestVisualPlugin:
    """
    Pytest plugin for visual regression testing.

    Usage in conftest.py:
        ```python
        from framework.testing.visual import PytestVisualPlugin, VisualConfig

        def pytest_configure(config):
            config.visual_tester = PytestVisualPlugin(VisualConfig())

        @pytest.fixture
        def visual(request):
            return request.config.visual_tester
        ```

    Usage in tests:
        ```python
        @pytest.mark.visual
        async def test_homepage_visual(page, visual):
            await page.goto("https://example.com")
            assert await visual.compare_page(page, "homepage")
        ```
    """

    def __init__(self, config: Optional[VisualConfig] = None):
        """
        Initialize pytest visual plugin.

        Args:
            config: Visual testing configuration
        """
        self.tester = VisualTester(config)
        self.results = []

    async def compare_page(self, page: Page, name: str, **kwargs) -> bool:
        """
        Compare page (pytest wrapper).

        Args:
            page: Playwright Page
            name: Test name
            **kwargs: Additional arguments

        Returns:
            Comparison result
        """
        result = await self.tester.compare_page(page, name, **kwargs)

        self.results.append({"name": name, "type": "page", "result": result})

        return result

    async def compare_element(self, element: Locator, name: str, **kwargs) -> bool:
        """
        Compare element (pytest wrapper).

        Args:
            element: Playwright Locator
            name: Test name
            **kwargs: Additional arguments

        Returns:
            Comparison result
        """
        result = await self.tester.compare_element(element, name, **kwargs)

        self.results.append({"name": name, "type": "element", "result": result})

        return result

    def generate_html_report(self, output_path: str) -> None:
        """
        Generate HTML report with visual diffs.

        Args:
            output_path: Path to save HTML report
        """
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Visual Regression Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .test { border: 1px solid #ccc; margin: 10px 0; padding: 10px; }
                .passed { background-color: #d4edda; }
                .failed { background-color: #f8d7da; }
                img { max-width: 300px; margin: 5px; }
            </style>
        </head>
        <body>
            <h1>Visual Regression Test Report</h1>
        """

        for result in self.results:
            status_class = "passed" if result["result"] else "failed"
            status_text = "PASSED" if result["result"] else "FAILED"

            html += f"""
            <div class="test {status_class}">
                <h3>{result['name']} - {status_text}</h3>
                <p>Type: {result['type']}</p>
            </div>
            """

        html += """
        </body>
        </html>
        """

        with open(output_path, "w") as f:
            f.write(html)
