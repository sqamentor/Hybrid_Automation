"""
Performance Metrics - Page Load & Runtime Performance Monitoring

Provides comprehensive performance metrics including load times,
resource sizes, Core Web Vitals, and custom performance marks.
"""

from datetime import datetime
from typing import Any, Dict, List, cast

from utils.logger import get_logger

logger = get_logger(__name__)


class PerformanceMetrics:
    """Performance monitoring and metrics collection."""
    
    def __init__(self, ui_engine: Any) -> None:
        """Initialize performance metrics collector.

        Args:
            ui_engine: PlaywrightEngine or SeleniumEngine instance
        """
        self.ui_engine = ui_engine
        self.engine_type = type(ui_engine).__name__
        self.metrics: List[Dict[str, Any]] = []
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics for current page.

        Returns:
            Performance metrics dictionary
        """
        if self.engine_type == 'PlaywrightEngine':
            return self._collect_playwright_metrics()
        elif self.engine_type == 'SeleniumEngine':
            return self._collect_selenium_metrics()
        else:
            raise ValueError(f"Unsupported engine type: {self.engine_type}")
    
    def _collect_playwright_metrics(self) -> Dict[str, Any]:
        """Collect metrics using Playwright."""
        page = self.ui_engine.get_page()
        
        # Navigation Timing API
        timing = page.evaluate("""
            () => {
                const perfData = window.performance.timing;
                const perfEntries = window.performance.getEntriesByType('navigation')[0];
                
                return {
                    // Basic timing
                    redirect: perfData.redirectEnd - perfData.redirectStart,
                    dns: perfData.domainLookupEnd - perfData.domainLookupStart,
                    tcp: perfData.connectEnd - perfData.connectStart,
                    request: perfData.responseStart - perfData.requestStart,
                    response: perfData.responseEnd - perfData.responseStart,
                    dom_processing: perfData.domComplete - perfData.domLoading,
                    load_event: perfData.loadEventEnd - perfData.loadEventStart,
                    
                    // Key metrics
                    dom_content_loaded: perfData.domContentLoadedEventEnd - perfData.navigationStart,
                    load_complete: perfData.loadEventEnd - perfData.navigationStart,
                    time_to_first_byte: perfData.responseStart - perfData.navigationStart,
                    dom_interactive: perfData.domInteractive - perfData.navigationStart,
                    
                    // Resource timing
                    transfer_size: perfEntries ? perfEntries.transferSize : 0,
                    encoded_body_size: perfEntries ? perfEntries.encodedBodySize : 0,
                    decoded_body_size: perfEntries ? perfEntries.decodedBodySize : 0
                };
            }
        """)
        
        # Core Web Vitals (if available)
        web_vitals = self._get_web_vitals()
        
        # Resource breakdown
        resources = page.evaluate("""
            () => {
                const entries = window.performance.getEntriesByType('resource');
                const breakdown = {
                    total: 0,
                    scripts: 0,
                    stylesheets: 0,
                    images: 0,
                    fonts: 0,
                    xhr: 0,
                    other: 0
                };
                
                entries.forEach(entry => {
                    breakdown.total += entry.transferSize || 0;
                    
                    if (entry.initiatorType === 'script') {
                        breakdown.scripts += entry.transferSize || 0;
                    } else if (entry.initiatorType === 'css') {
                        breakdown.stylesheets += entry.transferSize || 0;
                    } else if (entry.initiatorType === 'img') {
                        breakdown.images += entry.transferSize || 0;
                    } else if (entry.initiatorType === 'font') {
                        breakdown.fonts += entry.transferSize || 0;
                    } else if (entry.initiatorType === 'xmlhttprequest' || entry.initiatorType === 'fetch') {
                        breakdown.xhr += entry.transferSize || 0;
                    } else {
                        breakdown.other += entry.transferSize || 0;
                    }
                });
                
                return breakdown;
            }
        """)
        
        # Memory usage (if available)
        memory = page.evaluate("""
            () => {
                if (window.performance.memory) {
                    return {
                        used: window.performance.memory.usedJSHeapSize,
                        total: window.performance.memory.totalJSHeapSize,
                        limit: window.performance.memory.jsHeapSizeLimit
                    };
                }
                return null;
            }
        """)
        
        metrics = {
            'url': page.url,
            'timestamp': datetime.now().isoformat(),
            'timing': timing,
            'web_vitals': web_vitals,
            'resources': resources,
            'memory': memory
        }
        
        self.metrics.append(metrics)
        logger.info(f"Performance metrics collected for: {page.url}")
        
        return metrics
    
    def _collect_selenium_metrics(self) -> Dict[str, Any]:
        """Collect metrics using Selenium."""
        driver = self.ui_engine.get_driver()
        
        # Use Performance Timing API
        timing = driver.execute_script("""
            const perfData = window.performance.timing;
            return {
                dom_content_loaded: perfData.domContentLoadedEventEnd - perfData.navigationStart,
                load_complete: perfData.loadEventEnd - perfData.navigationStart,
                time_to_first_byte: perfData.responseStart - perfData.navigationStart,
                dom_interactive: perfData.domInteractive - perfData.navigationStart
            };
        """)
        
        metrics = {
            'url': driver.current_url,
            'timestamp': datetime.now().isoformat(),
            'timing': timing
        }
        
        self.metrics.append(metrics)
        return metrics
    
    def _get_web_vitals(self) -> Dict[str, Any]:
        """Get Core Web Vitals (LCP, FID, CLS)"""
        page = self.ui_engine.get_page() if self.engine_type == 'PlaywrightEngine' else None
        
        if not page:
            return {}
        
        # Inject web-vitals library
        web_vitals_script = """
            // Simplified Web Vitals measurement
            (() => {
                const vitals = {};
                
                // Largest Contentful Paint (LCP)
                try {
                    const lcpEntries = performance.getEntriesByType('largest-contentful-paint');
                    if (lcpEntries.length > 0) {
                        vitals.lcp = lcpEntries[lcpEntries.length - 1].renderTime || 
                                    lcpEntries[lcpEntries.length - 1].loadTime;
                    }
                } catch (e) {}
                
                // First Input Delay (FID) - approximation
                try {
                    const fidEntries = performance.getEntriesByType('first-input');
                    if (fidEntries.length > 0) {
                        vitals.fid = fidEntries[0].processingStart - fidEntries[0].startTime;
                    }
                } catch (e) {}
                
                // Cumulative Layout Shift (CLS)
                try {
                    let cls = 0;
                    const clsEntries = performance.getEntriesByType('layout-shift');
                    clsEntries.forEach(entry => {
                        if (!entry.hadRecentInput) {
                            cls += entry.value;
                        }
                    });
                    vitals.cls = cls;
                } catch (e) {}
                
                // First Contentful Paint (FCP)
                try {
                    const fcpEntry = performance.getEntriesByName('first-contentful-paint')[0];
                    if (fcpEntry) {
                        vitals.fcp = fcpEntry.startTime;
                    }
                } catch (e) {}
                
                return vitals;
            })();
        """
        
        try:
            web_vitals = cast(Dict[str, Any], page.evaluate(web_vitals_script))
            return web_vitals
        except Exception as e:
            logger.warning(f"Could not collect Web Vitals: {e}")
            return {}
    
    def assert_load_time(self, max_seconds: float, metric: str = 'load_complete') -> None:
        """Assert page load time is within threshold.

        Args:
            max_seconds: Maximum allowed seconds
            metric: Metric to check (load_complete, dom_content_loaded, etc.)

        Raises:
            AssertionError: If load time exceeds threshold
        """
        if not self.metrics:
            raise ValueError("No metrics collected. Call collect_metrics() first.")
        
        latest = self.metrics[-1]
        actual_time = latest['timing'].get(metric, 0) / 1000  # Convert to seconds
        
        if actual_time > max_seconds:
            raise AssertionError(
                f"Page load time ({metric}) exceeded threshold: "
                f"{actual_time:.2f}s > {max_seconds:.2f}s"
            )
        
        logger.info(f"✓ Load time check passed: {actual_time:.2f}s <= {max_seconds:.2f}s")
    
    def assert_resource_size(self, max_mb: float) -> None:
        """Assert total resource size is within limit.

        Args:
            max_mb: Maximum allowed size in megabytes

        Raises:
            AssertionError: If resource size exceeds limit
        """
        if not self.metrics:
            raise ValueError("No metrics collected.")
        
        latest = self.metrics[-1]
        total_bytes = latest.get('resources', {}).get('total', 0)
        total_mb = total_bytes / (1024 * 1024)
        
        if total_mb > max_mb:
            raise AssertionError(
                f"Total resource size exceeded limit: {total_mb:.2f}MB > {max_mb:.2f}MB"
            )
        
        logger.info(f"✓ Resource size check passed: {total_mb:.2f}MB <= {max_mb:.2f}MB")
    
    def assert_web_vitals(self, lcp_ms: float = 2500, fid_ms: float = 100, cls: float = 0.1) -> None:
        """Assert Core Web Vitals are within Google's thresholds.

        Args:
            lcp_ms: Max Largest Contentful Paint (default: 2500ms)
            fid_ms: Max First Input Delay (default: 100ms)
            cls: Max Cumulative Layout Shift (default: 0.1)

        Raises:
            AssertionError: If any vital exceeds threshold
        """
        if not self.metrics:
            raise ValueError("No metrics collected.")
        
        latest = self.metrics[-1]
        vitals = latest.get('web_vitals', {})
        
        errors = []
        
        if 'lcp' in vitals and vitals['lcp'] > lcp_ms:
            errors.append(f"LCP: {vitals['lcp']:.0f}ms > {lcp_ms}ms")
        
        if 'fid' in vitals and vitals['fid'] > fid_ms:
            errors.append(f"FID: {vitals['fid']:.0f}ms > {fid_ms}ms")
        
        if 'cls' in vitals and vitals['cls'] > cls:
            errors.append(f"CLS: {vitals['cls']:.3f} > {cls}")
        
        if errors:
            raise AssertionError("Core Web Vitals failed:\n  " + "\n  ".join(errors))
        
        logger.info("✓ Core Web Vitals check passed")
    
    def start_performance_mark(self, name: str) -> None:
        """Start a custom performance mark.

        Args:
            name: Mark name
        """
        page = self.ui_engine.get_page() if self.engine_type == 'PlaywrightEngine' else None
        
        if page:
            page.evaluate(f"window.performance.mark('{name}-start')")
            logger.debug(f"Performance mark started: {name}")
    
    def end_performance_mark(self, name: str) -> float:
        """End a performance mark and return duration.

        Args:
            name: Mark name

        Returns:
            Duration in milliseconds
        """
        page = self.ui_engine.get_page() if self.engine_type == 'PlaywrightEngine' else None
        
        if page:
            duration = cast(float, page.evaluate(f"""
                (() => {{
                    window.performance.mark('{name}-end');
                    const measure = window.performance.measure('{name}', '{name}-start', '{name}-end');
                    return measure.duration;
                }})()
            """))
            logger.info(f"Performance mark '{name}': {duration:.2f}ms")
            return duration
        
        return 0.0
    
    def generate_report(self, output_path: str = "reports/performance_report.html") -> str:
        """Generate HTML performance report.

        Args:
            output_path: Output file path
        """
        import os
        
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Performance Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .header { background: #333; color: white; padding: 20px; border-radius: 8px; }
        .metrics { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .metric { display: inline-block; margin: 10px 20px; }
        .metric-value { font-size: 24px; font-weight: bold; color: #007bff; }
        .metric-label { font-size: 14px; color: #666; }
        .good { color: #28a745; }
        .warning { color: #ffc107; }
        .bad { color: #dc3545; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Performance Report</h1>
        <p>Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
    </div>
"""
        
        for metric in self.metrics:
            timing = metric.get('timing', {})
            vitals = metric.get('web_vitals', {})
            resources = metric.get('resources', {})
            
            html += f"""
    <div class="metrics">
        <h2>{metric.get('url', 'Unknown')}</h2>
        
        <h3>Key Metrics</h3>
        <div class="metric">
            <div class="metric-value">{timing.get('load_complete', 0)/1000:.2f}s</div>
            <div class="metric-label">Load Complete</div>
        </div>
        <div class="metric">
            <div class="metric-value">{timing.get('dom_content_loaded', 0)/1000:.2f}s</div>
            <div class="metric-label">DOM Content Loaded</div>
        </div>
        <div class="metric">
            <div class="metric-value">{timing.get('time_to_first_byte', 0)/1000:.2f}s</div>
            <div class="metric-label">Time to First Byte</div>
        </div>
"""
            
            if vitals:
                html += """
        <h3>Core Web Vitals</h3>
"""
                if 'lcp' in vitals:
                    lcp_class = 'good' if vitals['lcp'] < 2500 else 'warning' if vitals['lcp'] < 4000 else 'bad'
                    html += f"""
        <div class="metric">
            <div class="metric-value {lcp_class}">{vitals['lcp']:.0f}ms</div>
            <div class="metric-label">LCP (Largest Contentful Paint)</div>
        </div>
"""
                if 'cls' in vitals:
                    cls_class = 'good' if vitals['cls'] < 0.1 else 'warning' if vitals['cls'] < 0.25 else 'bad'
                    html += f"""
        <div class="metric">
            <div class="metric-value {cls_class}">{vitals['cls']:.3f}</div>
            <div class="metric-label">CLS (Cumulative Layout Shift)</div>
        </div>
"""
            
            if resources:
                html += f"""
        <h3>Resource Breakdown</h3>
        <table>
            <tr><th>Type</th><th>Size</th></tr>
            <tr><td>Scripts</td><td>{resources.get('scripts', 0)/1024:.1f} KB</td></tr>
            <tr><td>Stylesheets</td><td>{resources.get('stylesheets', 0)/1024:.1f} KB</td></tr>
            <tr><td>Images</td><td>{resources.get('images', 0)/1024:.1f} KB</td></tr>
            <tr><td>Fonts</td><td>{resources.get('fonts', 0)/1024:.1f} KB</td></tr>
            <tr><td>XHR/Fetch</td><td>{resources.get('xhr', 0)/1024:.1f} KB</td></tr>
            <tr><td>Other</td><td>{resources.get('other', 0)/1024:.1f} KB</td></tr>
            <tr><th>Total</th><th>{resources.get('total', 0)/1024:.1f} KB</th></tr>
        </table>
"""
            
            html += "    </div>\n"
        
        html += "</body></html>"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(html)
        
        logger.info(f"Performance report generated: {output_path}")
        return output_path


__all__ = ['PerformanceMetrics']
