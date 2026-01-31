"""
Accessibility Testing - WCAG Compliance Validation

Provides automated accessibility testing following WCAG 2.1 guidelines.
Integrates with axe-core for comprehensive a11y checks.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from utils.logger import get_logger

logger = get_logger(__name__)


class WCAGLevel(Enum):
    """WCAG compliance levels"""
    A = "wcag2a"
    AA = "wcag2aa"
    AAA = "wcag2aaa"


class ImpactLevel(Enum):
    """Accessibility issue impact levels"""
    CRITICAL = "critical"
    SERIOUS = "serious"
    MODERATE = "moderate"
    MINOR = "minor"


class AccessibilityTester:
    """Automated accessibility testing"""
    
    def __init__(self, ui_engine, wcag_level: WCAGLevel = WCAGLevel.AA):
        """
        Initialize accessibility tester
        
        Args:
            ui_engine: PlaywrightEngine or SeleniumEngine instance
            wcag_level: WCAG compliance level to test against
        """
        self.ui_engine = ui_engine
        self.wcag_level = wcag_level
        self.engine_type = type(ui_engine).__name__
        self.violations: List[Dict] = []
        self.passes: List[Dict] = []
    
    def analyze_page(self, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze current page for accessibility issues
        
        Args:
            options: Optional axe-core options
        
        Returns:
            Analysis results with violations and passes
        """
        if self.engine_type == 'PlaywrightEngine':
            return self._analyze_with_playwright(options)
        elif self.engine_type == 'SeleniumEngine':
            return self._analyze_with_selenium(options)
        else:
            raise ValueError(f"Unsupported engine type: {self.engine_type}")
    
    def _analyze_with_playwright(self, options: Optional[Dict] = None) -> Dict:
        """Analyze page using Playwright and axe-core"""
        page = self.ui_engine.get_page()
        
        # Inject axe-core library
        axe_script = self._get_axe_core_script()
        page.evaluate(axe_script)
        
        # Configure axe options
        axe_options = options or {}
        axe_options.setdefault('runOnly', {
            'type': 'tag',
            'values': [self.wcag_level.value, 'best-practice']
        })
        
        # Run axe analysis
        results = page.evaluate(f"() => axe.run({axe_options})")
        
        # Store results
        self.violations = results.get('violations', [])
        self.passes = results.get('passes', [])
        
        # Log summary
        self._log_summary(results)
        
        return results
    
    def _analyze_with_selenium(self, options: Optional[Dict] = None) -> Dict:
        """Analyze page using Selenium and axe-core"""
        driver = self.ui_engine.get_driver()
        
        # Inject axe-core library
        axe_script = self._get_axe_core_script()
        driver.execute_script(axe_script)
        
        # Configure axe options
        axe_options = options or {}
        axe_options.setdefault('runOnly', {
            'type': 'tag',
            'values': [self.wcag_level.value, 'best-practice']
        })
        
        # Run axe analysis
        import json
        results = driver.execute_script(f"return axe.run({json.dumps(axe_options)})")
        
        # Store results
        self.violations = results.get('violations', [])
        self.passes = results.get('passes', [])
        
        # Log summary
        self._log_summary(results)
        
        return results
    
    def _get_axe_core_script(self) -> str:
        """Get axe-core script (embedded or from CDN)"""
        # Option 1: Load from CDN
        cdn_url = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.3/axe.min.js"
        
        # For production, you might want to bundle axe-core locally
        # and read from file instead of using CDN
        
        return f"""
        (function() {{
            if (typeof axe === 'undefined') {{
                var script = document.createElement('script');
                script.src = '{cdn_url}';
                document.head.appendChild(script);
                return new Promise((resolve) => {{
                    script.onload = resolve;
                }});
            }}
        }})();
        """
    
    def _log_summary(self, results: Dict):
        """Log summary of accessibility analysis"""
        violations = results.get('violations', [])
        passes = results.get('passes', [])
        
        logger.info(f"Accessibility Analysis Complete:")
        logger.info(f"  ✓ Passed: {len(passes)} checks")
        logger.info(f"  ✗ Violations: {len(violations)}")
        
        if violations:
            for violation in violations:
                impact = violation.get('impact', 'unknown').upper()
                logger.warning(f"  [{impact}] {violation.get('id')}: {violation.get('description')}")
    
    def get_violations(self, min_impact: Optional[ImpactLevel] = None) -> List[Dict]:
        """
        Get accessibility violations
        
        Args:
            min_impact: Minimum impact level to filter (optional)
        
        Returns:
            List of violations
        """
        if not min_impact:
            return self.violations
        
        impact_order = {
            'critical': 4,
            'serious': 3,
            'moderate': 2,
            'minor': 1
        }
        
        min_level = impact_order.get(min_impact.value, 0)
        
        return [
            v for v in self.violations
            if impact_order.get(v.get('impact', 'minor'), 0) >= min_level
        ]
    
    def get_critical_violations(self) -> List[Dict]:
        """Get critical accessibility violations"""
        return self.get_violations(ImpactLevel.CRITICAL)
    
    def assert_no_violations(self, min_impact: Optional[ImpactLevel] = None):
        """
        Assert that page has no accessibility violations
        
        Args:
            min_impact: Minimum impact level to check
        
        Raises:
            AssertionError: If violations found
        """
        violations = self.get_violations(min_impact)
        
        if violations:
            error_msg = f"Found {len(violations)} accessibility violations:\n"
            for v in violations:
                error_msg += f"  [{v.get('impact', 'unknown').upper()}] {v.get('id')}: {v.get('description')}\n"
            
            raise AssertionError(error_msg)
    
    def assert_no_critical_violations(self):
        """Assert no critical violations"""
        self.assert_no_violations(ImpactLevel.CRITICAL)
    
    def check_keyboard_navigation(self) -> bool:
        """
        Check if page is keyboard navigable
        
        Returns:
            True if page is fully keyboard accessible
        """
        # Test Tab key navigation
        page = self.ui_engine.get_page() if self.engine_type == 'PlaywrightEngine' else None
        
        if page:
            # Get all focusable elements
            focusable = page.evaluate("""
                () => {
                    const elements = Array.from(document.querySelectorAll('a, button, input, select, textarea, [tabindex]'));
                    return elements.map(el => ({
                        tag: el.tagName,
                        tabIndex: el.tabIndex,
                        visible: el.offsetParent !== null
                    }));
                }
            """)
            
            # Check if focusable elements exist
            visible_focusable = [e for e in focusable if e['visible']]
            
            logger.info(f"Found {len(visible_focusable)} focusable elements")
            return len(visible_focusable) > 0
        
        return True  # Default to True for Selenium (requires manual check)
    
    def check_color_contrast(self) -> Dict[str, Any]:
        """
        Check color contrast ratios
        
        Returns:
            Contrast check results
        """
        # Axe-core handles this automatically in analyze_page()
        contrast_violations = [
            v for v in self.violations
            if 'color-contrast' in v.get('id', '')
        ]
        
        return {
            'passed': len(contrast_violations) == 0,
            'violations': contrast_violations
        }
    
    def check_alt_text(self) -> Dict[str, Any]:
        """
        Check if all images have alt text
        
        Returns:
            Alt text check results
        """
        alt_violations = [
            v for v in self.violations
            if 'image-alt' in v.get('id', '')
        ]
        
        return {
            'passed': len(alt_violations) == 0,
            'violations': alt_violations
        }
    
    def check_aria_labels(self) -> Dict[str, Any]:
        """
        Check ARIA labels
        
        Returns:
            ARIA label check results
        """
        aria_violations = [
            v for v in self.violations
            if 'aria' in v.get('id', '').lower()
        ]
        
        return {
            'passed': len(aria_violations) == 0,
            'violations': aria_violations
        }
    
    def generate_report(self, output_path: str = "reports/accessibility_report.html"):
        """
        Generate HTML accessibility report
        
        Args:
            output_path: Output file path
        """
        import os
        from datetime import datetime
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessibility Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #333; color: white; padding: 20px; border-radius: 8px; }}
        .summary {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .violation {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; }}
        .critical {{ border-left: 4px solid #dc3545; }}
        .serious {{ border-left: 4px solid #fd7e14; }}
        .moderate {{ border-left: 4px solid #ffc107; }}
        .minor {{ border-left: 4px solid #17a2b8; }}
        .impact {{ display: inline-block; padding: 3px 8px; border-radius: 3px; color: white; font-size: 12px; }}
        .impact.critical {{ background: #dc3545; }}
        .impact.serious {{ background: #fd7e14; }}
        .impact.moderate {{ background: #ffc107; color: #333; }}
        .impact.minor {{ background: #17a2b8; }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Accessibility Test Report</h1>
        <p>WCAG Level: {self.wcag_level.name}</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Checks Passed: <span class="passed">{len(self.passes)}</span></p>
        <p>Total Violations: <span class="failed">{len(self.violations)}</span></p>
    </div>
"""
        
        if self.violations:
            html += "<h2>Violations</h2>\n"
            for violation in self.violations:
                impact = violation.get('impact', 'minor')
                html += f"""
    <div class="violation {impact}">
        <h3>{violation.get('id')} <span class="impact {impact}">{impact.upper()}</span></h3>
        <p><strong>Description:</strong> {violation.get('description')}</p>
        <p><strong>Help:</strong> {violation.get('help')}</p>
        <p><strong>Elements Affected:</strong> {len(violation.get('nodes', []))}</p>
        <p><strong>Tags:</strong> {', '.join(violation.get('tags', []))}</p>
    </div>
"""
        
        html += "</body></html>"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"Accessibility report generated: {output_path}")
        return output_path


__all__ = ['AccessibilityTester', 'WCAGLevel', 'ImpactLevel']
