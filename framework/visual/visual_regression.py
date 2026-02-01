"""
Visual Regression Testing - Pixel-Perfect Screenshot Comparison

Provides automated visual regression testing with baseline management.
Supports full page, element-level, and responsive screenshots.
"""

from typing import Optional, Dict, List, Tuple
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
import imagehash
import os
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class VisualRegression:
    """Visual regression testing engine"""
    
    def __init__(self, baseline_dir: str = "tests/visual_baselines", 
                 report_dir: str = "reports/visual"):
        """
        Initialize visual regression tester
        
        Args:
            baseline_dir: Directory to store baseline images
            report_dir: Directory for visual diff reports
        """
        self.baseline_dir = Path(baseline_dir)
        self.report_dir = Path(report_dir)
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.threshold = 0.1  # 10% difference threshold
        self.results: List[Dict] = []
    
    def capture_baseline(self, screenshot_path: str, name: str, 
                        viewport: Optional[Tuple[int, int]] = None):
        """
        Capture and save baseline screenshot
        
        Args:
            screenshot_path: Path to current screenshot
            name: Baseline name identifier
            viewport: Optional viewport size (width, height)
        """
        baseline_name = self._get_baseline_name(name, viewport)
        baseline_path = self.baseline_dir / baseline_name
        
        # Copy screenshot to baseline
        import shutil
        shutil.copy(screenshot_path, baseline_path)
        
        logger.info(f"Baseline captured: {baseline_name}")
        
        return baseline_path
    
    def compare(self, screenshot_path: str, name: str, 
                viewport: Optional[Tuple[int, int]] = None,
                threshold: Optional[float] = None) -> Dict:
        """
        Compare screenshot against baseline
        
        Args:
            screenshot_path: Path to current screenshot
            name: Baseline name identifier
            viewport: Optional viewport size
            threshold: Custom threshold (overrides default)
        
        Returns:
            Comparison result dictionary
        """
        baseline_name = self._get_baseline_name(name, viewport)
        baseline_path = self.baseline_dir / baseline_name
        
        # Check if baseline exists
        if not baseline_path.exists():
            logger.warning(f"No baseline found: {baseline_name}. Creating new baseline.")
            self.capture_baseline(screenshot_path, name, viewport)
            return {
                'name': name,
                'status': 'baseline_created',
                'difference_percentage': 0.0,
                'passed': True
            }
        
        # Compare images
        current_img = Image.open(screenshot_path)
        baseline_img = Image.open(baseline_path)
        
        # Ensure same size
        if current_img.size != baseline_img.size:
            logger.warning(f"Size mismatch: current={current_img.size}, baseline={baseline_img.size}")
            baseline_img = baseline_img.resize(current_img.size, Image.Resampling.LANCZOS)
        
        # Calculate difference
        diff_percentage = self._calculate_difference(current_img, baseline_img)
        
        # Generate diff image
        diff_image_path = self._generate_diff_image(current_img, baseline_img, name, viewport)
        
        # Determine pass/fail
        threshold_value = threshold if threshold is not None else self.threshold
        passed = diff_percentage <= threshold_value
        
        result = {
            'name': name,
            'viewport': viewport,
            'status': 'passed' if passed else 'failed',
            'difference_percentage': diff_percentage,
            'threshold': threshold_value,
            'passed': passed,
            'baseline_path': str(baseline_path),
            'current_path': screenshot_path,
            'diff_path': str(diff_image_path) if diff_image_path else None,
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        
        if passed:
            logger.info(f"✓ Visual test passed: {name} ({diff_percentage:.2%} difference)")
        else:
            logger.error(f"✗ Visual test failed: {name} ({diff_percentage:.2%} difference, threshold: {threshold_value:.2%})")
        
        return result
    
    def _calculate_difference(self, img1: Image.Image, img2: Image.Image) -> float:
        """
        Calculate pixel difference percentage between images
        
        Args:
            img1: First image
            img2: Second image
        
        Returns:
            Difference percentage (0.0 to 1.0)
        """
        # Method 1: Pixel-by-pixel comparison
        diff = ImageChops.difference(img1.convert('RGB'), img2.convert('RGB'))
        diff_array = list(diff.getdata())
        
        # Calculate percentage of different pixels
        total_pixels = len(diff_array)
        different_pixels = sum(1 for pixel in diff_array if sum(pixel) > 30)  # Threshold for "different"
        
        pixel_diff_percentage = different_pixels / total_pixels
        
        # Method 2: Perceptual hash (for major differences)
        hash1 = imagehash.average_hash(img1)
        hash2 = imagehash.average_hash(img2)
        hash_diff = (hash1 - hash2) / 64.0  # Normalize to 0-1
        
        # Combine both methods (weighted average)
        final_diff = (pixel_diff_percentage * 0.7) + (hash_diff * 0.3)
        
        return final_diff
    
    def _generate_diff_image(self, current: Image.Image, baseline: Image.Image,
                            name: str, viewport: Optional[Tuple[int, int]]) -> Optional[Path]:
        """
        Generate visual diff image highlighting differences
        
        Args:
            current: Current screenshot
            baseline: Baseline screenshot
            name: Test name
            viewport: Viewport size
        
        Returns:
            Path to diff image
        """
        try:
            # Create difference image
            diff = ImageChops.difference(current.convert('RGB'), baseline.convert('RGB'))
            
            # Highlight differences in red
            diff_highlighted = Image.new('RGB', current.size)
            diff_pixels = diff.load()
            highlight_pixels = diff_highlighted.load()
            
            for y in range(diff.height):
                for x in range(diff.width):
                    pixel = diff_pixels[x, y]
                    if sum(pixel) > 30:  # Different pixel
                        highlight_pixels[x, y] = (255, 0, 0)  # Red
                    else:
                        highlight_pixels[x, y] = (0, 0, 0)  # Black
            
            # Create side-by-side comparison
            comparison = Image.new('RGB', (current.width * 3, current.height))
            comparison.paste(baseline, (0, 0))
            comparison.paste(current, (current.width, 0))
            comparison.paste(diff_highlighted, (current.width * 2, 0))
            
            # Add labels
            draw = ImageDraw.Draw(comparison)
            draw.text((10, 10), "BASELINE", fill=(255, 255, 255))
            draw.text((current.width + 10, 10), "CURRENT", fill=(255, 255, 255))
            draw.text((current.width * 2 + 10, 10), "DIFF", fill=(255, 255, 255))
            
            # Save diff image
            diff_name = self._get_baseline_name(name, viewport).replace('.png', '_diff.png')
            diff_path = self.report_dir / diff_name
            comparison.save(diff_path)
            
            return diff_path
        
        except Exception as e:
            logger.error(f"Failed to generate diff image: {e}")
            return None
    
    def _get_baseline_name(self, name: str, viewport: Optional[Tuple[int, int]]) -> str:
        """Generate baseline filename"""
        clean_name = name.replace(' ', '_').replace('/', '_')
        if viewport:
            return f"{clean_name}_{viewport[0]}x{viewport[1]}.png"
        return f"{clean_name}.png"
    
    def update_baseline(self, screenshot_path: str, name: str,
                       viewport: Optional[Tuple[int, int]] = None):
        """
        Update existing baseline with new screenshot
        
        Args:
            screenshot_path: Path to new screenshot
            name: Baseline name
            viewport: Viewport size
        """
        self.capture_baseline(screenshot_path, name, viewport)
        logger.info(f"Baseline updated: {name}")
    
    def get_results_summary(self) -> Dict:
        """Get summary of all visual tests"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': (passed / total * 100) if total > 0 else 0,
            'results': self.results
        }
    
    def generate_html_report(self, output_path: str = "reports/visual/report.html"):
        """Generate HTML report with visual diffs"""
        summary = self.get_results_summary()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Visual Regression Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .summary {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .passed {{ color: #28a745; font-weight: bold; }}
        .failed {{ color: #dc3545; font-weight: bold; }}
        .test-result {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; }}
        .test-result.failed {{ border-left: 4px solid #dc3545; }}
        .test-result.passed {{ border-left: 4px solid #28a745; }}
        .comparison-images {{ display: flex; gap: 10px; margin-top: 10px; }}
        .comparison-images img {{ max-width: 300px; border: 1px solid #ddd; }}
        h1 {{ color: #333; }}
        h2 {{ color: #555; }}
    </style>
</head>
<body>
    <h1>Visual Regression Test Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Tests: {summary['total']}</p>
        <p class="passed">Passed: {summary['passed']}</p>
        <p class="failed">Failed: {summary['failed']}</p>
        <p>Pass Rate: {summary['pass_rate']:.1f}%</p>
    </div>
    <h2>Test Results</h2>
"""
        
        for result in self.results:
            status_class = 'passed' if result['passed'] else 'failed'
            html += f"""
    <div class="test-result {status_class}">
        <h3>{result['name']}</h3>
        <p>Status: <span class="{status_class}">{result['status'].upper()}</span></p>
        <p>Difference: {result['difference_percentage']:.2%} (Threshold: {result.get('threshold', self.threshold):.2%})</p>
"""
            if result.get('diff_path'):
                html += f"""
        <div class="comparison-images">
            <div>
                <p>Baseline</p>
                <img src="{os.path.relpath(result['baseline_path'], os.path.dirname(output_path))}" alt="Baseline">
            </div>
            <div>
                <p>Current</p>
                <img src="{os.path.relpath(result['current_path'], os.path.dirname(output_path))}" alt="Current">
            </div>
            <div>
                <p>Diff</p>
                <img src="{os.path.relpath(result['diff_path'], os.path.dirname(output_path))}" alt="Diff">
            </div>
        </div>
"""
            html += "    </div>\n"
        
        html += """
</body>
</html>
"""
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(html)
        
        logger.info(f"Visual regression report generated: {output_path}")
        return output_path


__all__ = ['VisualRegression']
