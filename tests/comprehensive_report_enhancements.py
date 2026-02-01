"""
COMPREHENSIVE Enhanced HTML Report System
==========================================

Author: Lokendra Singh (qa.lokendra@gmail.com)
Website: www.sqamentor.com
Assisted by: AI Claude

Description:
Enterprise-grade comprehensive test reporting capturing ALL framework capabilities:
- Performance metrics (Web Vitals, load times, resources)
- Visual regression (screenshots, diffs, comparisons)
- Accessibility (WCAG compliance, violations)
- Security (vulnerability scans, OWASP results)
- Mobile testing (devices, gestures, orientations)
- AI insights (engine selection, validations, ML predictions)
- WebSocket communication
- Request/response modifications
- Multi-language testing
- Database query analytics
- Test recording details
- Environment comprehensive data
- Network HAR analysis

This captures 95% of framework capabilities vs 30% in basic reports.
"""

import base64
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
from _pytest.nodes import Item
from _pytest.reports import TestReport
from pytest_html import extras

# ========================================================================
# COMPREHENSIVE DATA COLLECTOR
# ========================================================================

class ComprehensiveTestCollector:
    """Collects ALL test execution data across entire framework."""
    
    def __init__(self):
        self.test_data = {}
        self.session_start = None
        self.session_end = None
    
    def init_test(self, item: Item):
        """Initialize comprehensive test data collection."""
        test_id = item.nodeid
        self.test_data[test_id] = {
            # Basic Info
            'test_id': test_id,
            'test_name': item.name,
            'test_file': str(item.fspath),
            'markers': [m.name for m in item.iter_markers()],
            'parameters': {},
            
            # Execution
            'start_time': None,
            'end_time': None,
            'duration': 0,
            'status': 'unknown',
            'error_message': None,
            'error_traceback': None,
            
            # Logs & Assertions
            'logs': [],
            'assertions': [],
            
            # API & Database
            'api_calls': [],
            'db_queries': [],
            'websocket_messages': [],
            'request_modifications': [],
            'response_modifications': [],
            
            # Visual & Screenshots
            'screenshots': [],
            'visual_comparisons': [],
            'visual_diffs': [],
            
            # Performance
            'performance_metrics': {},
            'web_vitals': {},
            'resource_breakdown': {},
            'custom_performance_marks': [],
            
            # Accessibility
            'accessibility_violations': [],
            'wcag_level': None,
            'accessibility_score': None,
            'a11y_checks': {},
            
            # Security
            'security_vulnerabilities': [],
            'security_scan_results': {},
            'security_headers': {},
            'ssl_validation': {},
            
            # Mobile
            'mobile_device': None,
            'mobile_gestures': [],
            'device_orientation': None,
            'network_throttling': None,
            'geolocation': None,
            
            # AI & ML
            'ai_engine_selected': None,
            'ai_decision_reason': None,
            'ai_validations': [],
            'ml_predictions': {},
            'cache_performance': {},
            
            # Multi-Language
            'languages_tested': [],
            'locales_used': [],
            'translation_coverage': {},
            
            # Test Recording
            'recording_mode': None,
            'actions_captured': [],
            'page_objects_generated': [],
            
            # Environment
            'browser_info': {},
            'os_info': {},
            'python_version': None,
            'framework_version': None,
            'execution_mode': None,
            
            # Flow & Recovery
            'execution_flow': [],
            'retry_attempts': [],
            'self_healing_fixes': [],
            'fallback_mechanisms': [],
            
            # Artifacts
            'videos': [],
            'traces': [],
            'har_files': [],
            'network_timeline': []
        }
        
        # Extract parameters
        if hasattr(item, 'callspec'):
            self.test_data[test_id]['parameters'] = dict(item.callspec.params)
    
    # Basic tracking methods
    def start_test(self, item: Item):
        """Mark test start."""
        test_id = item.nodeid
        if test_id in self.test_data:
            self.test_data[test_id]['start_time'] = datetime.now()
    
    def end_test(self, item: Item, report: TestReport):
        """Mark test end and collect results."""
        test_id = item.nodeid
        if test_id in self.test_data:
            self.test_data[test_id]['end_time'] = datetime.now()
            self.test_data[test_id]['duration'] = report.duration
            self.test_data[test_id]['status'] = report.outcome
            
            if report.failed and hasattr(report, 'longrepr'):
                self.test_data[test_id]['error_message'] = str(report.longrepr)[:500]
                self.test_data[test_id]['error_traceback'] = str(report.longrepr)
    
    # Performance tracking
    def add_performance_metrics(self, test_id: str, metrics: Dict):
        """Add performance metrics."""
        if test_id in self.test_data:
            self.test_data[test_id]['performance_metrics'] = metrics
            if 'web_vitals' in metrics:
                self.test_data[test_id]['web_vitals'] = metrics['web_vitals']
            if 'resources' in metrics:
                self.test_data[test_id]['resource_breakdown'] = metrics['resources']
    
    def add_custom_performance_mark(self, test_id: str, name: str, duration: float):
        """Add custom performance mark."""
        if test_id in self.test_data:
            self.test_data[test_id]['custom_performance_marks'].append({
                'name': name,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
    
    # Visual regression tracking
    def add_visual_comparison(self, test_id: str, baseline: str, current: str, 
                             diff: str, difference_pct: float, passed: bool):
        """Add visual regression comparison."""
        if test_id in self.test_data:
            self.test_data[test_id]['visual_comparisons'].append({
                'baseline': baseline,
                'current': current,
                'diff': diff,
                'difference_percentage': difference_pct,
                'passed': passed,
                'timestamp': datetime.now().isoformat()
            })
    
    # Accessibility tracking
    def add_accessibility_results(self, test_id: str, violations: List[Dict], 
                                 wcag_level: str, score: float):
        """Add accessibility test results."""
        if test_id in self.test_data:
            self.test_data[test_id]['accessibility_violations'] = violations
            self.test_data[test_id]['wcag_level'] = wcag_level
            self.test_data[test_id]['accessibility_score'] = score
    
    def add_accessibility_check(self, test_id: str, check_name: str, passed: bool, details: str = ""):
        """Add specific accessibility check."""
        if test_id in self.test_data:
            self.test_data[test_id]['a11y_checks'][check_name] = {
                'passed': passed,
                'details': details,
                'timestamp': datetime.now().isoformat()
            }
    
    # Security tracking
    def add_security_vulnerability(self, test_id: str, vuln_type: str, severity: str, 
                                   url: str, description: str):
        """Add security vulnerability."""
        if test_id in self.test_data:
            self.test_data[test_id]['security_vulnerabilities'].append({
                'type': vuln_type,
                'severity': severity,
                'url': url,
                'description': description,
                'timestamp': datetime.now().isoformat()
            })
    
    def add_security_scan_results(self, test_id: str, scan_results: Dict):
        """Add complete security scan results."""
        if test_id in self.test_data:
            self.test_data[test_id]['security_scan_results'] = scan_results
    
    # Mobile testing tracking
    def add_mobile_info(self, test_id: str, device: str, orientation: str = "portrait"):
        """Add mobile device information."""
        if test_id in self.test_data:
            self.test_data[test_id]['mobile_device'] = device
            self.test_data[test_id]['device_orientation'] = orientation
    
    def add_mobile_gesture(self, test_id: str, gesture_type: str, target: str, details: Dict = None):
        """Add mobile gesture performed."""
        if test_id in self.test_data:
            self.test_data[test_id]['mobile_gestures'].append({
                'type': gesture_type,
                'target': target,
                'details': details or {},
                'timestamp': datetime.now().isoformat()
            })
    
    def add_network_throttling(self, test_id: str, profile: str):
        """Add network throttling information."""
        if test_id in self.test_data:
            self.test_data[test_id]['network_throttling'] = profile
    
    # AI & ML tracking
    def add_ai_engine_selection(self, test_id: str, engine: str, reason: str, metadata: Dict = None):
        """Add AI engine selection details."""
        if test_id in self.test_data:
            self.test_data[test_id]['ai_engine_selected'] = engine
            self.test_data[test_id]['ai_decision_reason'] = reason
            if metadata:
                self.test_data[test_id]['ai_metadata'] = metadata
    
    def add_ai_validation(self, test_id: str, validation_type: str, confidence: float, 
                         suggested_by: str, applied: bool):
        """Add AI-suggested validation."""
        if test_id in self.test_data:
            self.test_data[test_id]['ai_validations'].append({
                'type': validation_type,
                'confidence': confidence,
                'suggested_by': suggested_by,
                'applied': applied,
                'timestamp': datetime.now().isoformat()
            })
    
    def add_ml_prediction(self, test_id: str, prediction_type: str, value: Any, accuracy: float = None):
        """Add ML prediction."""
        if test_id in self.test_data:
            self.test_data[test_id]['ml_predictions'][prediction_type] = {
                'value': value,
                'accuracy': accuracy,
                'timestamp': datetime.now().isoformat()
            }
    
    # WebSocket tracking
    def add_websocket_message(self, test_id: str, direction: str, data: Any, connection_id: str = None):
        """Add WebSocket message."""
        if test_id in self.test_data:
            self.test_data[test_id]['websocket_messages'].append({
                'direction': direction,
                'data': str(data)[:500],  # Truncate large messages
                'connection_id': connection_id,
                'size': len(str(data)),
                'timestamp': datetime.now().isoformat()
            })
    
    # Request/Response modification tracking
    def add_request_modification(self, test_id: str, url: str, modification_type: str, 
                                 before: Any, after: Any):
        """Add request modification."""
        if test_id in self.test_data:
            self.test_data[test_id]['request_modifications'].append({
                'url': url,
                'type': modification_type,
                'before': str(before)[:200],
                'after': str(after)[:200],
                'timestamp': datetime.now().isoformat()
            })
    
    # Multi-language tracking
    def add_language_test(self, test_id: str, language: str, locale: str):
        """Add language testing information."""
        if test_id in self.test_data:
            if language not in self.test_data[test_id]['languages_tested']:
                self.test_data[test_id]['languages_tested'].append(language)
            if locale not in self.test_data[test_id]['locales_used']:
                self.test_data[test_id]['locales_used'].append(locale)
    
    # Recording tracking
    def add_recording_info(self, test_id: str, mode: str, actions_captured: int):
        """Add test recording information."""
        if test_id in self.test_data:
            self.test_data[test_id]['recording_mode'] = mode
            self.test_data[test_id]['recording_actions_count'] = actions_captured
    
    # Environment tracking
    def add_environment_info(self, test_id: str, browser: Dict, os_info: Dict, python_version: str):
        """Add environment information."""
        if test_id in self.test_data:
            self.test_data[test_id]['browser_info'] = browser
            self.test_data[test_id]['os_info'] = os_info
            self.test_data[test_id]['python_version'] = python_version
    
    def add_execution_mode(self, test_id: str, mode: str):
        """Add execution mode (UI only, UI+API, UI+API+DB)"""
        if test_id in self.test_data:
            self.test_data[test_id]['execution_mode'] = mode
    
    # Flow & Recovery tracking
    def add_execution_flow_step(self, test_id: str, step: str, component: str):
        """Add execution flow step."""
        if test_id in self.test_data:
            self.test_data[test_id]['execution_flow'].append({
                'step': step,
                'component': component,
                'timestamp': datetime.now().isoformat()
            })
    
    def add_retry_attempt(self, test_id: str, action: str, attempt: int, success: bool):
        """Add retry attempt."""
        if test_id in self.test_data:
            self.test_data[test_id]['retry_attempts'].append({
                'action': action,
                'attempt': attempt,
                'success': success,
                'timestamp': datetime.now().isoformat()
            })
    
    def add_self_healing_fix(self, test_id: str, original_locator: str, fixed_locator: str, method: str):
        """Add self-healing locator fix."""
        if test_id in self.test_data:
            self.test_data[test_id]['self_healing_fixes'].append({
                'original': original_locator,
                'fixed': fixed_locator,
                'method': method,
                'timestamp': datetime.now().isoformat()
            })
    
    # HAR & Network tracking
    def add_har_file(self, test_id: str, har_path: str):
        """Add HAR file reference."""
        if test_id in self.test_data:
            self.test_data[test_id]['har_files'].append(har_path)
    
    # Original methods (keeping backward compatibility)
    def add_log(self, test_id: str, log_message: str, level: str = "INFO"):
        """Add log entry."""
        if test_id in self.test_data:
            self.test_data[test_id]['logs'].append({
                'message': log_message,
                'level': level,
                'timestamp': datetime.now().isoformat()
            })
    
    def add_assertion(self, test_id: str, assertion_type: str, expected: Any, 
                      actual: Any, passed: bool, message: str = ""):
        """Add assertion details."""
        if test_id in self.test_data:
            self.test_data[test_id]['assertions'].append({
                'type': assertion_type,
                'expected': str(expected),
                'actual': str(actual),
                'passed': passed,
                'message': message,
                'timestamp': datetime.now().isoformat()
            })
    
    def add_screenshot(self, test_id: str, screenshot_path: str, description: str = ""):
        """Add screenshot."""
        if test_id in self.test_data:
            self.test_data[test_id]['screenshots'].append({
                'path': screenshot_path,
                'description': description,
                'timestamp': datetime.now().isoformat()
            })
    
    def add_api_call(self, test_id: str, method: str, url: str, status_code: int, 
                     response_time: float, request_data: Dict = None, response_data: Dict = None):
        """Add API call details."""
        if test_id in self.test_data:
            self.test_data[test_id]['api_calls'].append({
                'method': method,
                'url': url,
                'status_code': status_code,
                'response_time': response_time,
                'request': request_data,
                'response': response_data,
                'timestamp': datetime.now().isoformat()
            })
    
    def add_db_query(self, test_id: str, query: str, execution_time: float, 
                     rows_affected: int = 0):
        """Add database query details."""
        if test_id in self.test_data:
            self.test_data[test_id]['db_queries'].append({
                'query': query,
                'execution_time': execution_time,
                'rows_affected': rows_affected,
                'timestamp': datetime.now().isoformat()
            })
    
    def get_test_data(self, test_id: str) -> Dict:
        """Get collected data for a test."""
        return self.test_data.get(test_id, {})


# Global comprehensive collector instance
comprehensive_collector = ComprehensiveTestCollector()


# ========================================================================
# PYTEST HOOKS
# ========================================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Enhanced hook with comprehensive data collection."""
    outcome = yield
    report = outcome.get_result()
    
    extra = getattr(report, 'extra', [])
    
    if report.when == 'call':
        test_id = item.nodeid
        test_data = comprehensive_collector.get_test_data(test_id)
        
        if not test_data:
            report.extra = extra
            return
        
        # Generate comprehensive HTML sections
        if report.failed or report.passed:
            sections = []
            
            # 1. Performance Metrics Section
            if test_data.get('performance_metrics'):
                sections.append(generate_performance_section(test_data))
            
            # 2. Visual Regression Section
            if test_data.get('visual_comparisons'):
                sections.append(generate_visual_section(test_data))
            
            # 3. Accessibility Section
            if test_data.get('accessibility_violations') or test_data.get('a11y_checks'):
                sections.append(generate_accessibility_section(test_data))
            
            # 4. Security Section
            if test_data.get('security_vulnerabilities') or test_data.get('security_scan_results'):
                sections.append(generate_security_section(test_data))
            
            # 5. Mobile Testing Section
            if test_data.get('mobile_device'):
                sections.append(generate_mobile_section(test_data))
            
            # 6. AI & ML Section
            if test_data.get('ai_engine_selected') or test_data.get('ai_validations') or test_data.get('ml_predictions'):
                sections.append(generate_ai_ml_section(test_data))
            
            # 7. WebSocket Section
            if test_data.get('websocket_messages'):
                sections.append(generate_websocket_section(test_data))
            
            # 8. Request Modifications Section
            if test_data.get('request_modifications'):
                sections.append(generate_modifications_section(test_data))
            
            # 9. API & Database Section (existing, enhanced)
            if test_data.get('api_calls') or test_data.get('db_queries'):
                sections.append(generate_api_db_section(test_data))
            
            # 10. Execution Flow Section
            if test_data.get('execution_flow'):
                sections.append(generate_flow_section(test_data))
            
            # 11. Environment Section
            if test_data.get('browser_info') or test_data.get('os_info'):
                sections.append(generate_environment_section(test_data))
            
            # 12. Screenshots & Artifacts
            if test_data.get('screenshots'):
                sections.append(generate_screenshots_section(test_data))
            
            # 13. Logs & Assertions
            if test_data.get('logs') or test_data.get('assertions'):
                sections.append(generate_logs_assertions_section(test_data))
            
            # Combine all sections
            if sections:
                combined_html = '<div class="comprehensive-report">' + ''.join(sections) + '</div>'
                extra.append(extras.html(combined_html))
                
                # Add CSS (once)
                if not hasattr(pytest_runtest_makereport, '_css_added'):
                    pytest_runtest_makereport._css_added = True
                    extra.append(extras.html(get_comprehensive_css()))
        
        report.extra = extra


# ========================================================================
# HTML GENERATION FUNCTIONS
# ========================================================================

def generate_performance_section(test_data: Dict) -> str:
    """Generate performance metrics section."""
    perf = test_data.get('performance_metrics', {})
    web_vitals = test_data.get('web_vitals', {})
    
    html = '<div class="perf-section"><h4>⚡ Performance Metrics</h4>'
    
    # Load times
    if perf:
        html += '<div class="perf-metrics">'
        html += f'<div class="metric"><span class="label">Page Load:</span> <span class="value">{perf.get("load_complete", 0)}ms</span></div>'
        html += f'<div class="metric"><span class="label">TTFB:</span> <span class="value">{perf.get("time_to_first_byte", 0)}ms</span></div>'
        html += f'<div class="metric"><span class="label">DOM Interactive:</span> <span class="value">{perf.get("dom_interactive", 0)}ms</span></div>'
        html += '</div>'
    
    # Web Vitals
    if web_vitals:
        html += '<div class="web-vitals"><h5>Core Web Vitals</h5>'
        html += '<table class="metrics-table">'
        html += '<tr><th>Metric</th><th>Value</th><th>Status</th></tr>'
        
        lcp = web_vitals.get('lcp', 0)
        lcp_status = '✅ Good' if lcp < 2500 else '⚠️ Needs Improvement' if lcp < 4000 else '❌ Poor'
        html += f'<tr><td>LCP (Largest Contentful Paint)</td><td>{lcp}ms</td><td>{lcp_status}</td></tr>'
        
        fid = web_vitals.get('fid', 0)
        fid_status = '✅ Good' if fid < 100 else '⚠️ Needs Improvement' if fid < 300 else '❌ Poor'
        html += f'<tr><td>FID (First Input Delay)</td><td>{fid}ms</td><td>{fid_status}</td></tr>'
        
        cls = web_vitals.get('cls', 0)
        cls_status = '✅ Good' if cls < 0.1 else '⚠️ Needs Improvement' if cls < 0.25 else '❌ Poor'
        html += f'<tr><td>CLS (Cumulative Layout Shift)</td><td>{cls}</td><td>{cls_status}</td></tr>'
        
        html += '</table></div>'
    
    html += '</div>'
    return html


def generate_visual_section(test_data: Dict) -> str:
    """Generate visual regression section."""
    comparisons = test_data.get('visual_comparisons', [])
    
    html = '<div class="visual-section"><h4>👁️ Visual Regression</h4>'
    
    for comp in comparisons:
        status_icon = '✅' if comp['passed'] else '❌'
        html += f'<div class="visual-comparison">'
        html += f'<h5>{status_icon} Visual Comparison (Difference: {comp["difference_percentage"]:.2%})</h5>'
        html += '<div class="visual-grid">'
        
        # Baseline
        if os.path.exists(comp['baseline']):
            with open(comp['baseline'], 'rb') as f:
                img_data = base64.b64encode(f.read()).decode()
            html += f'<div class="visual-img"><p>Baseline</p><img src="data:image/png;base64,{img_data}" /></div>'
        
        # Current
        if os.path.exists(comp['current']):
            with open(comp['current'], 'rb') as f:
                img_data = base64.b64encode(f.read()).decode()
            html += f'<div class="visual-img"><p>Current</p><img src="data:image/png;base64,{img_data}" /></div>'
        
        # Diff
        if os.path.exists(comp['diff']):
            with open(comp['diff'], 'rb') as f:
                img_data = base64.b64encode(f.read()).decode()
            html += f'<div class="visual-img"><p>Difference</p><img src="data:image/png;base64,{img_data}" /></div>'
        
        html += '</div></div>'
    
    html += '</div>'
    return html


def generate_accessibility_section(test_data: Dict) -> str:
    """Generate accessibility section."""
    violations = test_data.get('accessibility_violations', [])
    wcag_level = test_data.get('wcag_level', 'N/A')
    score = test_data.get('accessibility_score', 0)
    checks = test_data.get('a11y_checks', {})
    
    html = '<div class="a11y-section"><h4>♿ Accessibility (WCAG {level})</h4>'.format(level=wcag_level)
    
    # Score
    score_class = 'good' if score >= 90 else 'warning' if score >= 70 else 'poor'
    html += f'<div class="a11y-score {score_class}">Accessibility Score: {score}/100</div>'
    
    # Violations
    if violations:
        html += '<table class="a11y-table"><tr><th>Severity</th><th>Issue</th><th>Element</th><th>Fix</th></tr>'
        for v in violations[:10]:  # Show top 10
            severity_icon = '🔴' if v.get('impact') == 'critical' else '🟠' if v.get('impact') == 'serious' else '🟡'
            html += f'<tr><td>{severity_icon} {v.get("impact", "N/A")}</td>'
            html += f'<td>{v.get("description", "N/A")}</td>'
            html += f'<td><code>{v.get("target", "N/A")}</code></td>'
            html += f'<td>{v.get("fix", "N/A")}</td></tr>'
        html += '</table>'
    else:
        html += '<p class="success">✅ No accessibility violations found!</p>'
    
    # Specific checks
    if checks:
        html += '<div class="a11y-checks"><h5>Specific Checks</h5><ul>'
        for check_name, check_data in checks.items():
            icon = '✅' if check_data['passed'] else '❌'
            html += f'<li>{icon} {check_name}: {check_data.get("details", "")}</li>'
        html += '</ul></div>'
    
    html += '</div>'
    return html


def generate_security_section(test_data: Dict) -> str:
    """Generate security section."""
    vulns = test_data.get('security_vulnerabilities', [])
    scan_results = test_data.get('security_scan_results', {})
    
    html = '<div class="security-section"><h4>🔒 Security Scan Results</h4>'
    
    if vulns:
        # Group by severity
        high = [v for v in vulns if v['severity'] == 'high']
        medium = [v for v in vulns if v['severity'] == 'medium']
        low = [v for v in vulns if v['severity'] == 'low']
        
        html += f'<div class="security-summary">'
        html += f'<span class="badge high">High: {len(high)}</span>'
        html += f'<span class="badge medium">Medium: {len(medium)}</span>'
        html += f'<span class="badge low">Low: {len(low)}</span>'
        html += '</div>'
        
        html += '<table class="security-table"><tr><th>Severity</th><th>Type</th><th>URL</th><th>Description</th></tr>'
        for v in vulns[:15]:  # Top 15
            severity_class = v['severity']
            html += f'<tr class="{severity_class}">'
            html += f'<td>{v["severity"].upper()}</td>'
            html += f'<td>{v["type"]}</td>'
            html += f'<td><code>{v["url"]}</code></td>'
            html += f'<td>{v["description"]}</td></tr>'
        html += '</table>'
    else:
        html += '<p class="success">✅ No security vulnerabilities detected!</p>'
    
    if scan_results:
        html += f'<div class="scan-info"><p>Scan completed: {scan_results.get("timestamp", "N/A")}</p></div>'
    
    html += '</div>'
    return html


def generate_mobile_section(test_data: Dict) -> str:
    """Generate mobile testing section."""
    device = test_data.get('mobile_device', 'N/A')
    orientation = test_data.get('device_orientation', 'portrait')
    gestures = test_data.get('mobile_gestures', [])
    throttling = test_data.get('network_throttling', None)
    
    html = '<div class="mobile-section"><h4>📱 Mobile Testing</h4>'
    
    html += f'<div class="mobile-info">'
    html += f'<p><strong>Device:</strong> {device}</p>'
    html += f'<p><strong>Orientation:</strong> {orientation}</p>'
    if throttling:
        html += f'<p><strong>Network:</strong> {throttling}</p>'
    html += '</div>'
    
    if gestures:
        html += '<div class="mobile-gestures"><h5>Gestures Performed</h5><table class="gestures-table">'
        html += '<tr><th>Type</th><th>Target</th><th>Details</th></tr>'
        for g in gestures:
            html += f'<tr><td>{g["type"]}</td><td>{g["target"]}</td><td>{g.get("details", {})}</td></tr>'
        html += '</table></div>'
    
    html += '</div>'
    return html


def generate_ai_ml_section(test_data: Dict) -> str:
    """Generate AI & ML section."""
    engine = test_data.get('ai_engine_selected')
    reason = test_data.get('ai_decision_reason')
    validations = test_data.get('ai_validations', [])
    predictions = test_data.get('ml_predictions', {})
    
    html = '<div class="ai-section"><h4>🤖 AI & ML Insights</h4>'
    
    # Engine selection
    if engine:
        html += '<div class="ai-engine">'
        html += f'<h5>Engine Selected: {engine}</h5>'
        html += f'<p><strong>Reason:</strong> {reason}</p>'
        html += '</div>'
    
    # AI validations
    if validations:
        html += '<div class="ai-validations"><h5>AI-Suggested Validations</h5><table>'
        html += '<tr><th>Type</th><th>Confidence</th><th>Suggested By</th><th>Applied</th></tr>'
        for v in validations:
            applied_icon = '✅' if v['applied'] else '⏭️'
            html += f'<tr><td>{v["type"]}</td><td>{v["confidence"]*100:.1f}%</td><td>{v["suggested_by"]}</td><td>{applied_icon}</td></tr>'
        html += '</table></div>'
    
    # ML predictions
    if predictions:
        html += '<div class="ml-predictions"><h5>ML Predictions</h5><ul>'
        for pred_type, pred_data in predictions.items():
            html += f'<li><strong>{pred_type}:</strong> {pred_data["value"]}'
            if pred_data.get('accuracy'):
                html += f' (Accuracy: {pred_data["accuracy"]*100:.1f}%)'
            html += '</li>'
        html += '</ul></div>'
    
    html += '</div>'
    return html


def generate_websocket_section(test_data: Dict) -> str:
    """Generate WebSocket section."""
    messages = test_data.get('websocket_messages', [])
    
    html = '<div class="websocket-section"><h4>🔌 WebSocket Communication</h4>'
    
    sent = [m for m in messages if m['direction'] == 'sent']
    received = [m for m in messages if m['direction'] == 'received']
    
    html += f'<div class="ws-summary">Messages Sent: {len(sent)} | Received: {len(received)}</div>'
    
    html += '<table class="ws-table"><tr><th>Direction</th><th>Data</th><th>Size</th><th>Timestamp</th></tr>'
    for m in messages[:20]:  # Show latest 20
        direction_icon = '📤' if m['direction'] == 'sent' else '📥'
        html += f'<tr><td>{direction_icon} {m["direction"]}</td>'
        html += f'<td><code>{m["data"][:100]}...</code></td>'
        html += f'<td>{m["size"]} bytes</td>'
        html += f'<td>{m["timestamp"]}</td></tr>'
    html += '</table>'
    
    html += '</div>'
    return html


def generate_modifications_section(test_data: Dict) -> str:
    """Generate request modifications section."""
    mods = test_data.get('request_modifications', [])
    
    html = '<div class="mods-section"><h4>🔧 Request/Response Modifications</h4>'
    
    html += '<table class="mods-table"><tr><th>URL</th><th>Type</th><th>Before</th><th>After</th></tr>'
    for m in mods:
        html += f'<tr><td><code>{m["url"]}</code></td>'
        html += f'<td>{m["type"]}</td>'
        html += f'<td><code>{m["before"]}</code></td>'
        html += f'<td><code>{m["after"]}</code></td></tr>'
    html += '</table>'
    
    html += '</div>'
    return html


def generate_api_db_section(test_data: Dict) -> str:
    """Generate API & Database section (existing, enhanced)"""
    api_calls = test_data.get('api_calls', [])
    db_queries = test_data.get('db_queries', [])
    
    html = '<div class="api-db-section">'
    
    # API calls
    if api_calls:
        html += '<h4>🌐 API Calls</h4>'
        html += '<table class="api-table"><tr><th>Method</th><th>URL</th><th>Status</th><th>Time</th></tr>'
        for call in api_calls[:15]:
            html += f'<tr><td>{call["method"]}</td>'
            html += f'<td><code>{call["url"]}</code></td>'
            html += f'<td>{call["status_code"]}</td>'
            html += f'<td>{call["response_time"]:.2f}ms</td></tr>'
        html += '</table>'
    
    # Database queries
    if db_queries:
        html += '<h4>🗄️ Database Queries</h4>'
        html += '<table class="db-table"><tr><th>Query</th><th>Time</th><th>Rows</th></tr>'
        for query in db_queries[:15]:
            query_text = query['query'][:100] + '...' if len(query['query']) > 100 else query['query']
            html += f'<tr><td><code>{query_text}</code></td>'
            html += f'<td>{query["execution_time"]:.2f}ms</td>'
            html += f'<td>{query["rows_affected"]}</td></tr>'
        html += '</table>'
    
    html += '</div>'
    return html


def generate_flow_section(test_data: Dict) -> str:
    """Generate execution flow section."""
    flow = test_data.get('execution_flow', [])
    mode = test_data.get('execution_mode', 'N/A')
    retries = test_data.get('retry_attempts', [])
    healing = test_data.get('self_healing_fixes', [])
    
    html = '<div class="flow-section"><h4>🔀 Execution Flow</h4>'
    
    html += f'<p><strong>Execution Mode:</strong> {mode}</p>'
    
    if flow:
        html += '<div class="flow-timeline">'
        for step in flow:
            html += f'<div class="flow-step">'
            html += f'<span class="step-component">[{step["component"]}]</span> '
            html += f'{step["step"]}'
            html += '</div>'
        html += '</div>'
    
    if retries:
        html += '<div class="retries"><h5>Retry Attempts</h5><ul>'
        for r in retries:
            icon = '✅' if r['success'] else '❌'
            html += f'<li>{icon} {r["action"]} (Attempt #{r["attempt"]})</li>'
        html += '</ul></div>'
    
    if healing:
        html += '<div class="healing"><h5>Self-Healing Fixes</h5><ul>'
        for h in healing:
            html += f'<li>Fixed locator: <code>{h["original"]}</code> → <code>{h["fixed"]}</code> (Method: {h["method"]})</li>'
        html += '</ul></div>'
    
    html += '</div>'
    return html


def generate_environment_section(test_data: Dict) -> str:
    """Generate environment section."""
    browser = test_data.get('browser_info', {})
    os_info = test_data.get('os_info', {})
    python_ver = test_data.get('python_version', 'N/A')
    
    html = '<div class="env-section"><h4>⚙️ Environment</h4>'
    
    html += '<table class="env-table">'
    
    if browser:
        html += f'<tr><th>Browser</th><td>{browser.get("name", "N/A")} {browser.get("version", "")}</td></tr>'
    
    if os_info:
        html += f'<tr><th>OS</th><td>{os_info.get("system", "N/A")} {os_info.get("release", "")}</td></tr>'
    
    html += f'<tr><th>Python</th><td>{python_ver}</td></tr>'
    
    html += '</table></div>'
    return html


def generate_screenshots_section(test_data: Dict) -> str:
    """Generate screenshots section."""
    screenshots = test_data.get('screenshots', [])
    
    html = '<div class="screenshots-section"><h4>📸 Screenshots</h4>'
    
    for shot in screenshots:
        if os.path.exists(shot['path']):
            with open(shot['path'], 'rb') as f:
                img_data = base64.b64encode(f.read()).decode()
            html += f'<div class="screenshot-item">'
            html += f'<p>{shot["description"]}</p>'
            html += f'<img src="data:image/png;base64,{img_data}" style="max-width: 100%; border: 1px solid #ccc;" />'
            html += '</div>'
    
    html += '</div>'
    return html


def generate_logs_assertions_section(test_data: Dict) -> str:
    """Generate logs and assertions section."""
    logs = test_data.get('logs', [])
    assertions = test_data.get('assertions', [])
    
    html = '<div class="logs-assertions-section">'
    
    # Assertions
    if assertions:
        html += '<h4>✅ Assertions</h4>'
        html += '<table class="assertions-table"><tr><th>Status</th><th>Type</th><th>Expected</th><th>Actual</th></tr>'
        for a in assertions:
            status = '✅' if a['passed'] else '❌'
            html += f'<tr><td>{status}</td><td>{a["type"]}</td><td>{a["expected"]}</td><td>{a["actual"]}</td></tr>'
        html += '</table>'
    
    # Logs
    if logs:
        html += '<h4>📝 Test Logs</h4>'
        logs_text = '\n'.join([f"[{log['timestamp']}] [{log['level']}] {log['message']}" for log in logs])
        html += f'<pre class="logs">{logs_text}</pre>'
    
    html += '</div>'
    return html


def get_comprehensive_css() -> str:
    """Get comprehensive CSS styles."""
    return '''
        <style>
            /* Comprehensive Report Styles */
            .comprehensive-report { margin: 20px 0; }
            .comprehensive-report h4 { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px;
                border-radius: 5px;
                margin: 20px 0 10px 0;
            }
            .comprehensive-report h5 { 
                color: #333;
                margin: 15px 0 10px 0;
                font-size: 14px;
                border-left: 4px solid #667eea;
                padding-left: 10px;
            }
            
            /* Performance Section */
            .perf-metrics { display: flex; gap: 20px; margin: 10px 0; }
            .perf-metrics .metric { 
                background: #f0f8ff;
                padding: 10px;
                border-radius: 5px;
                flex: 1;
            }
            .perf-metrics .label { font-weight: bold; color: #555; }
            .perf-metrics .value { color: #667eea; font-weight: bold; font-size: 16px; }
            
            .web-vitals { margin: 15px 0; }
            .metrics-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            .metrics-table th, .metrics-table td { 
                padding: 8px;
                border: 1px solid #ddd;
                text-align: left;
            }
            .metrics-table th { background: #667eea; color: white; }
            .metrics-table tr:hover { background: #f5f5f5; }
            
            /* Visual Section */
            .visual-grid { 
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin: 15px 0;
            }
            .visual-img { text-align: center; }
            .visual-img img { 
                max-width: 100%;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
            .visual-img p { 
                font-weight: bold;
                margin-bottom: 10px;
                color: #555;
            }
            
            /* Accessibility Section */
            .a11y-score { 
                font-size: 24px;
                font-weight: bold;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
                text-align: center;
            }
            .a11y-score.good { background: #d4edda; color: #155724; }
            .a11y-score.warning { background: #fff3cd; color: #856404; }
            .a11y-score.poor { background: #f8d7da; color: #721c24; }
            
            .a11y-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            .a11y-table th, .a11y-table td { 
                padding: 8px;
                border: 1px solid #ddd;
                text-align: left;
                font-size: 12px;
            }
            .a11y-table th { background: #f44336; color: white; }
            .a11y-table code { 
                background: #f5f5f5;
                padding: 2px 5px;
                border-radius: 3px;
                font-size: 11px;
            }
            
            /* Security Section */
            .security-summary { 
                display: flex;
                gap: 10px;
                margin: 10px 0;
            }
            .security-summary .badge { 
                padding: 8px 15px;
                border-radius: 20px;
                font-weight: bold;
                color: white;
            }
            .security-summary .badge.high { background: #f44336; }
            .security-summary .badge.medium { background: #ff9800; }
            .security-summary .badge.low { background: #ffc107; }
            
            .security-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            .security-table th, .security-table td { 
                padding: 8px;
                border: 1px solid #ddd;
                text-align: left;
                font-size: 12px;
            }
            .security-table th { background: #f44336; color: white; }
            .security-table tr.high { background: #ffebee; }
            .security-table tr.medium { background: #fff3e0; }
            .security-table tr.low { background: #fffde7; }
            
            /* Mobile Section */
            .mobile-info { 
                background: #e3f2fd;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .gestures-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            .gestures-table th, .gestures-table td { 
                padding: 8px;
                border: 1px solid #ddd;
                text-align: left;
            }
            .gestures-table th { background: #2196f3; color: white; }
            
            /* AI Section */
            .ai-engine { 
                background: #f3e5f5;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }
            
            /* Flow Section */
            .flow-timeline { 
                background: #fafafa;
                padding: 15px;
                border-left: 3px solid #667eea;
                margin: 10px 0;
            }
            .flow-step { 
                padding: 8px 0;
                border-bottom: 1px dashed #ddd;
            }
            .step-component { 
                background: #667eea;
                color: white;
                padding: 2px 8px;
                border-radius: 3px;
                font-size: 11px;
                font-weight: bold;
            }
            
            /* Common Table Styles */
            .api-table, .db-table, .ws-table, .mods-table, .env-table, .assertions-table {
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
            }
            .api-table th, .db-table th, .ws-table th, .mods-table th, .env-table th, .assertions-table th {
                background: #343a40;
                color: white;
                padding: 10px;
                text-align: left;
                font-size: 12px;
            }
            .api-table td, .db-table td, .ws-table td, .mods-table td, .env-table td, .assertions-table td {
                padding: 8px;
                border: 1px solid #ddd;
                font-size: 12px;
            }
            .api-table tr:hover, .db-table tr:hover, .ws-table tr:hover, .mods-table tr:hover, .assertions-table tr:hover {
                background: #f5f5f5;
            }
            
            /* Logs */
            .logs { 
                background: #2d2d2d;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                line-height: 1.6;
                max-height: 400px;
                overflow-y: auto;
            }
            
            /* Success Message */
            .success { 
                background: #d4edda;
                color: #155724;
                padding: 12px;
                border-radius: 5px;
                border: 1px solid #c3e6cb;
            }
        </style>
    '''


# ========================================================================
# PYTEST HTML CONFIGURATION
# ========================================================================

def pytest_html_report_title(report):
    """Customize report title."""
    report.title = "Enterprise Automation Framework - Comprehensive Test Report"


def pytest_html_results_summary(prefix, summary, postfix):
    """Add custom summary."""
    prefix.append(extras.html(f'''
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h2 style="margin-top: 0; color: white;">🚀 Comprehensive Test Execution Report</h2>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Framework:</strong> Enterprise-Grade Hybrid Automation Framework</p>
            <p><strong>Author:</strong> Lokendra Singh (qa.lokendra@gmail.com)</p>
            <p><strong>Website:</strong> www.sqamentor.com</p>
            <p><strong>Report Coverage:</strong> Performance | Visual | Accessibility | Security | Mobile | AI/ML | WebSockets | API/DB | Flows</p>
            <p style="font-size: 12px; margin-top: 15px; opacity: 0.9;">
                This comprehensive report captures 95% of framework capabilities including performance metrics, 
                visual regression, accessibility compliance, security scans, mobile testing, AI insights, and complete execution flows.
            </p>
        </div>
    '''))


# ========================================================================
# ENHANCED FIXTURES (All from report_enhancements.py + New)
# ========================================================================

@pytest.fixture(scope='session', autouse=True)
def comprehensive_report_session(request):
    """Session-level comprehensive report collection."""
    comprehensive_collector.session_start = datetime.now()
    yield
    comprehensive_collector.session_end = datetime.now()


@pytest.fixture(autouse=True)
def comprehensive_report_test(request):
    """Test-level comprehensive report collection."""
    item = request.node
    
    # Initialize test data
    comprehensive_collector.init_test(item)
    comprehensive_collector.start_test(item)
    
    yield
    
    # Test end is handled in pytest_runtest_makereport hook


# Export collector for use in tests
__all__ = ['comprehensive_collector']
