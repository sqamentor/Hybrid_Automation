"""
Security Testing - OWASP ZAP Integration & Vulnerability Scanning

Integrates with OWASP ZAP for automated security testing including
SQL injection, XSS, CSRF, and other vulnerability scanning.
"""

import time
from typing import Any, Dict, List, Optional

import requests

from utils.logger import get_logger

logger = get_logger(__name__)


class SecurityTester:
    """Security testing and vulnerability scanning"""
    
    def __init__(self, zap_proxy_url: str = "http://localhost:8080"):
        """
        Initialize security tester
        
        Args:
            zap_proxy_url: OWASP ZAP proxy URL
        """
        self.zap_url = zap_proxy_url
        self.api_key: Optional[str] = None
        self.alerts: List[Dict] = []
    
    def set_api_key(self, api_key: str):
        """Set ZAP API key"""
        self.api_key = api_key
    
    def start_zap_session(self, session_name: str = "test_session"):
        """
        Start new ZAP session
        
        Args:
            session_name: Session name
        """
        url = f"{self.zap_url}/JSON/core/action/newSession/"
        params = {
            'name': session_name,
            'overwrite': 'true'
        }
        
        if self.api_key:
            params['apikey'] = self.api_key
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        logger.info(f"ZAP session started: {session_name}")
    
    def spider_url(self, target_url: str, max_children: int = 10) -> str:
        """
        Spider target URL to discover pages
        
        Args:
            target_url: URL to spider
            max_children: Max child nodes to spider
        
        Returns:
            Scan ID
        """
        url = f"{self.zap_url}/JSON/spider/action/scan/"
        params = {
            'url': target_url,
            'maxChildren': max_children
        }
        
        if self.api_key:
            params['apikey'] = self.api_key
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        scan_id = response.json()['scan']
        logger.info(f"Spider scan started: {scan_id}")
        
        # Wait for spider to complete
        self._wait_for_spider(scan_id)
        
        return scan_id
    
    def _wait_for_spider(self, scan_id: str, timeout: int = 300):
        """Wait for spider scan to complete"""
        url = f"{self.zap_url}/JSON/spider/view/status/"
        params = {'scanId': scan_id}
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = requests.get(url, params=params)
            status = int(response.json()['status'])
            
            logger.debug(f"Spider progress: {status}%")
            
            if status >= 100:
                logger.info("Spider scan completed")
                return
            
            time.sleep(2)
        
        logger.warning("Spider scan timeout")
    
    def active_scan(self, target_url: str) -> str:
        """
        Run active security scan
        
        Args:
            target_url: URL to scan
        
        Returns:
            Scan ID
        """
        url = f"{self.zap_url}/JSON/ascan/action/scan/"
        params = {'url': target_url}
        
        if self.api_key:
            params['apikey'] = self.api_key
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        scan_id = response.json()['scan']
        logger.info(f"Active scan started: {scan_id}")
        
        # Wait for scan to complete
        self._wait_for_active_scan(scan_id)
        
        return scan_id
    
    def _wait_for_active_scan(self, scan_id: str, timeout: int = 600):
        """Wait for active scan to complete"""
        url = f"{self.zap_url}/JSON/ascan/view/status/"
        params = {'scanId': scan_id}
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = requests.get(url, params=params)
            status = int(response.json()['status'])
            
            logger.debug(f"Active scan progress: {status}%")
            
            if status >= 100:
                logger.info("Active scan completed")
                return
            
            time.sleep(5)
        
        logger.warning("Active scan timeout")
    
    def get_alerts(self, base_url: Optional[str] = None) -> List[Dict]:
        """
        Get security alerts
        
        Args:
            base_url: Optional filter by base URL
        
        Returns:
            List of security alerts
        """
        url = f"{self.zap_url}/JSON/core/view/alerts/"
        params = {}
        
        if base_url:
            params['baseurl'] = base_url
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        self.alerts = response.json()['alerts']
        logger.info(f"Retrieved {len(self.alerts)} security alerts")
        
        return self.alerts
    
    def get_high_risk_alerts(self) -> List[Dict]:
        """Get high risk alerts"""
        return [a for a in self.alerts if a.get('risk') == 'High']
    
    def get_alerts_by_type(self, alert_type: str) -> List[Dict]:
        """
        Get alerts by type
        
        Args:
            alert_type: Alert type (e.g., 'SQL Injection', 'XSS', 'CSRF')
        """
        return [a for a in self.alerts if alert_type.lower() in a.get('alert', '').lower()]
    
    def test_sql_injection(self, target_url: str, parameters: List[str]) -> List[Dict]:
        """
        Test for SQL injection vulnerabilities
        
        Args:
            target_url: Target URL
            parameters: List of parameter names to test
        
        Returns:
            SQL injection alerts
        """
        # Run active scan focused on SQL injection
        self.active_scan(target_url)
        alerts = self.get_alerts(target_url)
        
        sql_alerts = self.get_alerts_by_type('SQL Injection')
        
        logger.info(f"Found {len(sql_alerts)} SQL injection alerts")
        return sql_alerts
    
    def test_xss(self, target_url: str) -> List[Dict]:
        """
        Test for Cross-Site Scripting (XSS) vulnerabilities
        
        Args:
            target_url: Target URL
        
        Returns:
            XSS alerts
        """
        self.active_scan(target_url)
        alerts = self.get_alerts(target_url)
        
        xss_alerts = self.get_alerts_by_type('Cross Site Scripting')
        
        logger.info(f"Found {len(xss_alerts)} XSS alerts")
        return xss_alerts
    
    def test_csrf(self, target_url: str) -> List[Dict]:
        """
        Test for CSRF vulnerabilities
        
        Args:
            target_url: Target URL
        
        Returns:
            CSRF alerts
        """
        self.active_scan(target_url)
        alerts = self.get_alerts(target_url)
        
        csrf_alerts = self.get_alerts_by_type('CSRF')
        
        logger.info(f"Found {len(csrf_alerts)} CSRF alerts")
        return csrf_alerts
    
    def assert_no_high_risk_vulnerabilities(self):
        """
        Assert no high risk vulnerabilities found
        
        Raises:
            AssertionError: If high risk vulnerabilities found
        """
        high_risk = self.get_high_risk_alerts()
        
        if high_risk:
            error_msg = f"Found {len(high_risk)} high risk vulnerabilities:\n"
            for alert in high_risk:
                error_msg += f"  - {alert.get('alert')}: {alert.get('url')}\n"
            
            raise AssertionError(error_msg)
        
        logger.info("✓ No high risk vulnerabilities found")
    
    def assert_no_sql_injection(self, target_url: str):
        """Assert no SQL injection vulnerabilities"""
        sql_alerts = self.test_sql_injection(target_url, [])
        
        if sql_alerts:
            raise AssertionError(f"Found {len(sql_alerts)} SQL injection vulnerabilities")
        
        logger.info("✓ No SQL injection vulnerabilities found")
    
    def assert_no_xss(self, target_url: str):
        """Assert no XSS vulnerabilities"""
        xss_alerts = self.test_xss(target_url)
        
        if xss_alerts:
            raise AssertionError(f"Found {len(xss_alerts)} XSS vulnerabilities")
        
        logger.info("✓ No XSS vulnerabilities found")
    
    def generate_report(self, output_path: str = "reports/security_report.html"):
        """
        Generate HTML security report
        
        Args:
            output_path: Output file path
        """
        import os
        from datetime import datetime

        # Group alerts by risk level
        high_risk = [a for a in self.alerts if a.get('risk') == 'High']
        medium_risk = [a for a in self.alerts if a.get('risk') == 'Medium']
        low_risk = [a for a in self.alerts if a.get('risk') == 'Low']
        info = [a for a in self.alerts if a.get('risk') == 'Informational']
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Security Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #333; color: white; padding: 20px; border-radius: 8px; }}
        .summary {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .alert {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; }}
        .high {{ border-left: 4px solid #dc3545; }}
        .medium {{ border-left: 4px solid #fd7e14; }}
        .low {{ border-left: 4px solid #ffc107; }}
        .info {{ border-left: 4px solid #17a2b8; }}
        .risk-badge {{ display: inline-block; padding: 3px 8px; border-radius: 3px; color: white; font-size: 12px; }}
        .risk-badge.high {{ background: #dc3545; }}
        .risk-badge.medium {{ background: #fd7e14; }}
        .risk-badge.low {{ background: #ffc107; color: #333; }}
        .risk-badge.info {{ background: #17a2b8; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Security Test Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Alerts: {len(self.alerts)}</p>
        <p style="color: #dc3545;">High Risk: {len(high_risk)}</p>
        <p style="color: #fd7e14;">Medium Risk: {len(medium_risk)}</p>
        <p style="color: #ffc107;">Low Risk: {len(low_risk)}</p>
        <p style="color: #17a2b8;">Informational: {len(info)}</p>
    </div>
"""
        
        # Add alerts
        for risk_level, alerts, css_class in [
            ('High', high_risk, 'high'),
            ('Medium', medium_risk, 'medium'),
            ('Low', low_risk, 'low'),
            ('Informational', info, 'info')
        ]:
            if alerts:
                html += f"<h2>{risk_level} Risk Alerts</h2>\n"
                for alert in alerts:
                    html += f"""
    <div class="alert {css_class}">
        <h3>{alert.get('alert')} <span class="risk-badge {css_class}">{risk_level.upper()}</span></h3>
        <p><strong>URL:</strong> {alert.get('url')}</p>
        <p><strong>Description:</strong> {alert.get('description', 'N/A')}</p>
        <p><strong>Solution:</strong> {alert.get('solution', 'N/A')}</p>
        <p><strong>CWE ID:</strong> {alert.get('cweid', 'N/A')}</p>
    </div>
"""
        
        html += "</body></html>"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"Security report generated: {output_path}")
        return output_path


class ManualSecurityChecks:
    """Manual security testing helpers"""
    
    @staticmethod
    def check_https(url: str) -> bool:
        """Check if URL uses HTTPS"""
        return url.startswith('https://')
    
    @staticmethod
    def check_security_headers(url: str) -> Dict[str, bool]:
        """
        Check for security headers
        
        Returns:
            Dictionary of header presence
        """
        response = requests.get(url)
        headers = response.headers
        
        return {
            'Strict-Transport-Security': 'Strict-Transport-Security' in headers,
            'X-Content-Type-Options': 'X-Content-Type-Options' in headers,
            'X-Frame-Options': 'X-Frame-Options' in headers,
            'X-XSS-Protection': 'X-XSS-Protection' in headers,
            'Content-Security-Policy': 'Content-Security-Policy' in headers
        }
    
    @staticmethod
    def check_password_strength(password: str) -> Dict[str, Any]:
        """
        Check password strength
        
        Returns:
            Strength analysis
        """
        import re
        
        checks = {
            'length': len(password) >= 12,
            'uppercase': bool(re.search(r'[A-Z]', password)),
            'lowercase': bool(re.search(r'[a-z]', password)),
            'digits': bool(re.search(r'\d', password)),
            'special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        }
        
        score = sum(checks.values())
        
        return {
            'checks': checks,
            'score': score,
            'strength': 'strong' if score >= 4 else 'medium' if score >= 3 else 'weak'
        }


__all__ = ['SecurityTester', 'ManualSecurityChecks']
