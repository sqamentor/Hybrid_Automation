"""
Enhanced HTML Report Configuration
====================================

Author: Lokendra Singh (lokendra.singh@centerforvein.com)
Website: www.centerforvein.com
Assisted by: AI Claude

Description:
Comprehensive pytest-html report enhancements to add:
- Screenshots (success & failure)
- Video recordings
- Test parameters & markers
- Step-by-step logs
- Browser/environment details
- API call logs
- Database query logs
- Assertions and validations
- Trace files and artifacts
- Execution timeline
- Performance metrics

Usage:
This module is automatically loaded by conftest.py
No manual intervention required.
"""

import base64
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pytest
from _pytest.nodes import Item
from _pytest.reports import TestReport
from pytest_html import extras

# ========================================================================
# REPORT METADATA COLLECTION
# ========================================================================


@pytest.mark.legacy_ui
class TestReportCollector:
    """
    Collects comprehensive test execution metadata
    """

    def __init__(self):
        self.test_data = {}
        self.session_start = None
        self.session_end = None

    def start_session(self):
        """Mark session start time"""
        self.session_start = datetime.now()

    def end_session(self):
        """Mark session end time"""
        self.session_end = datetime.now()

    def init_test(self, item: Item):
        """Initialize test data collection"""
        test_id = item.nodeid
        self.test_data[test_id] = {
            "test_id": test_id,
            "test_name": item.name,
            "test_file": str(item.fspath),
            "markers": [m.name for m in item.iter_markers()],
            "parameters": {},
            "screenshots": [],
            "videos": [],
            "traces": [],
            "logs": [],
            "api_calls": [],
            "db_queries": [],
            "assertions": [],
            "start_time": None,
            "end_time": None,
            "duration": 0,
            "status": "unknown",
            "error_message": None,
            "error_traceback": None,
        }

        # Extract parameters from fixtures
        if hasattr(item, "callspec"):
            self.test_data[test_id]["parameters"] = dict(item.callspec.params)

    def start_test(self, item: Item):
        """Mark test start"""
        test_id = item.nodeid
        if test_id in self.test_data:
            self.test_data[test_id]["start_time"] = datetime.now()

    def end_test(self, item: Item, report: TestReport):
        """Mark test end and collect results"""
        test_id = item.nodeid
        if test_id in self.test_data:
            self.test_data[test_id]["end_time"] = datetime.now()
            self.test_data[test_id]["duration"] = report.duration
            self.test_data[test_id]["status"] = report.outcome

            if report.failed:
                if hasattr(report, "longrepr"):
                    self.test_data[test_id]["error_message"] = str(report.longrepr)[:500]
                    self.test_data[test_id]["error_traceback"] = str(report.longrepr)

    def add_screenshot(self, test_id: str, screenshot_path: str, description: str = ""):
        """Add screenshot to test data"""
        if test_id in self.test_data:
            self.test_data[test_id]["screenshots"].append(
                {
                    "path": screenshot_path,
                    "description": description,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    def add_video(self, test_id: str, video_path: str):
        """Add video recording to test data"""
        if test_id in self.test_data:
            self.test_data[test_id]["videos"].append(
                {"path": video_path, "timestamp": datetime.now().isoformat()}
            )

    def add_trace(self, test_id: str, trace_path: str):
        """Add trace file to test data"""
        if test_id in self.test_data:
            self.test_data[test_id]["traces"].append(
                {"path": trace_path, "timestamp": datetime.now().isoformat()}
            )

    def add_log(self, test_id: str, log_message: str, level: str = "INFO"):
        """Add log entry to test data"""
        if test_id in self.test_data:
            self.test_data[test_id]["logs"].append(
                {"message": log_message, "level": level, "timestamp": datetime.now().isoformat()}
            )

    def add_api_call(
        self,
        test_id: str,
        method: str,
        url: str,
        status_code: int,
        response_time: float,
        request_data: Dict = None,
        response_data: Dict = None,
    ):
        """Add API call details to test data"""
        if test_id in self.test_data:
            self.test_data[test_id]["api_calls"].append(
                {
                    "method": method,
                    "url": url,
                    "status_code": status_code,
                    "response_time": response_time,
                    "request": request_data,
                    "response": response_data,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    def add_db_query(self, test_id: str, query: str, execution_time: float, rows_affected: int = 0):
        """Add database query details to test data"""
        if test_id in self.test_data:
            self.test_data[test_id]["db_queries"].append(
                {
                    "query": query,
                    "execution_time": execution_time,
                    "rows_affected": rows_affected,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    def add_assertion(
        self,
        test_id: str,
        assertion_type: str,
        expected: Any,
        actual: Any,
        passed: bool,
        message: str = "",
    ):
        """Add assertion details to test data"""
        if test_id in self.test_data:
            self.test_data[test_id]["assertions"].append(
                {
                    "type": assertion_type,
                    "expected": str(expected),
                    "actual": str(actual),
                    "passed": passed,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    def get_test_data(self, test_id: str) -> Dict:
        """Get collected data for a test"""
        return self.test_data.get(test_id, {})

    def get_all_test_data(self) -> Dict:
        """Get all collected test data"""
        return self.test_data


# Global collector instance
report_collector = TestReportCollector()


# ========================================================================
# PYTEST-HTML HOOKS
# ========================================================================

# ========================================================================
# NOTE: This hook is DISABLED - was conflicting with root conftest video hook
# ========================================================================

# @pytest.hookimpl(hookwrapper=True)  # DISABLED
def pytest_runtest_makereport_DISABLED(item, call):
    """
    Enhanced hook to add custom data to report - CURRENTLY DISABLED
    """
    pass
    # This function is disabled - see root conftest.py for active video hook
    #
    # outcome = yield
    # report = outcome.get_result()

    # Add extra HTML content to report
    extra = getattr(report, "extra", [])
    
    # DEBUG: Log initial state
    logger.debug(f"[REPORT_ENHANCEMENTS] report.when={report.when}, Phase: POST-YIELD")
    logger.debug(f"[REPORT_ENHANCEMENTS] report.extra at START: {getattr(report, 'extra', 'NOT_SET')}")

    if report.when == "call":
        test_id = item.nodeid
        test_data = report_collector.get_test_data(test_id)

        # For failed tests, add comprehensive details
        if report.failed and test_data:
            # Add error message
            if test_data.get("error_message"):
                extra.append(extras.html(f"""
                    <div class="error-section">
                        <h4>❌ Error Message</h4>
                        <pre class="error-message">{test_data['error_message']}</pre>
                    </div>
                """))

            # Add screenshots
            screenshots = test_data.get("screenshots", [])
            if screenshots:
                for screenshot in screenshots:
                    if os.path.exists(screenshot["path"]):
                        try:
                            with open(screenshot["path"], "rb") as f:
                                img_data = base64.b64encode(f.read()).decode("utf-8")
                            extra.append(extras.html(f"""
                                <div class="screenshot-item">
                                    <p>{screenshot.get('description', 'Screenshot')} ({screenshot.get('timestamp', '')})</p>
                                    <img src="data:image/png;base64,{img_data}" style="max-width: 100%; border: 1px solid #ccc;" />
                                </div>
                            """))
                        except Exception as e:
                            extra.append(extras.text(f"Failed to load screenshot: {e}"))

            # Add API calls
            api_calls = test_data.get("api_calls", [])
            if api_calls:
                api_html = (
                    '<div class="api-section"><h4>🌐 API Calls</h4><table class="api-calls-table">'
                )
                api_html += "<thead><tr><th>Method</th><th>URL</th><th>Status</th><th>Time</th></tr></thead><tbody>"
                for call in api_calls:
                    api_html += f"""<tr>
                        <td>{call['method']}</td>
                        <td>{call['url']}</td>
                        <td>{call['status_code']}</td>
                        <td>{call['response_time']:.2f}ms</td>
                    </tr>"""
                api_html += "</tbody></table></div>"
                extra.append(extras.html(api_html))

            # Add database queries
            db_queries = test_data.get("db_queries", [])
            if db_queries:
                db_html = '<div class="db-section"><h4>🗄️ Database Queries</h4><table class="db-queries-table">'
                db_html += "<thead><tr><th>Query</th><th>Time</th><th>Rows</th></tr></thead><tbody>"
                for query in db_queries:
                    query_text = (
                        query["query"][:100] + "..."
                        if len(query["query"]) > 100
                        else query["query"]
                    )
                    db_html += f"""<tr>
                        <td>{query_text}</td>
                        <td>{query['execution_time']:.2f}ms</td>
                        <td>{query.get('rows_affected', 0)}</td>
                    </tr>"""
                db_html += "</tbody></table></div>"
                extra.append(extras.html(db_html))

            # Add assertions
            assertions = test_data.get("assertions", [])
            if assertions:
                assert_html = '<div class="assertions-section"><h4>✅ Assertions</h4><table class="assertions-table">'
                assert_html += "<thead><tr><th>Status</th><th>Type</th><th>Expected</th><th>Actual</th></tr></thead><tbody>"
                for assertion in assertions:
                    status = "✅" if assertion["passed"] else "❌"
                    assert_html += f"""<tr>
                        <td>{status}</td>
                        <td>{assertion['type']}</td>
                        <td>{assertion['expected']}</td>
                        <td>{assertion['actual']}</td>
                    </tr>"""
                assert_html += "</tbody></table></div>"
                extra.append(extras.html(assert_html))

            # Add logs
            logs = test_data.get("logs", [])
            if logs:
                logs_text = "\n".join(
                    [f"[{log['timestamp']}] [{log['level']}] {log['message']}" for log in logs]
                )
                extra.append(extras.html(f"""
                    <div class="logs-section">
                        <h4>📝 Complete Test Logs</h4>
                        <pre class="logs">{logs_text}</pre>
                    </div>
                """))

        # For passed tests, add minimal details
        elif report.passed and test_data:
            screenshots = test_data.get("screenshots", [])
            if screenshots:
                for screenshot in screenshots:
                    if os.path.exists(screenshot["path"]):
                        try:
                            with open(screenshot["path"], "rb") as f:
                                img_data = base64.b64encode(f.read()).decode("utf-8")
                            extra.append(extras.html(f"""
                                <div class="screenshot-item">
                                    <p>{screenshot.get('description', 'Screenshot')}</p>
                                    <img src="data:image/png;base64,{img_data}" style="max-width: 100%; border: 1px solid #ccc;" />
                                </div>
                            """))
                        except Exception as e:
                            pass

        # DEBUG: Log before modification
        logger.debug(f"[REPORT_ENHANCEMENTS] Extra items to ADD: {len(extra)}")
        logger.debug(f"[REPORT_ENHANCEMENTS] report.extra BEFORE modification: {getattr(report, 'extra', [])}")
        
        # PRESERVE existing extras (especially video link from root conftest!)
        # Only extend if we have new items to add
        if extra:
            if not hasattr(report, 'extra'):
                report.extra = []
            # Append new items to existing extras
            logger.info(f"[REPORT_ENHANCEMENTS] Adding {len(extra)} enhancement items to report")
            report.extra.extend(extra)
        else:
            logger.debug(f"[REPORT_ENHANCEMENTS] No new items to add, preserving existing extras")
        
        # DEBUG: Log after modification
        logger.debug(f"[REPORT_ENHANCEMENTS] report.extra AFTER modification: {report.extra}")
        logger.debug(f"[REPORT_ENHANCEMENTS] report.extra length: {len(report.extra)}")


# ========================================================================
# PYTEST HTML CONFIGURATION
# ========================================================================


def pytest_html_report_title(report):
    """Customize report title"""
    report.title = "Enterprise Automation Framework - Enhanced Test Report"


def pytest_html_results_summary(prefix, summary, postfix):
    """Add custom summary"""
    prefix.append(extras.html(f"""
        <div style="background: #f0f8ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0;">📊 Enhanced Test Report</h3>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Framework:</strong> Enterprise-Grade Hybrid Automation Framework</p>
            <p><strong>Author:</strong> Lokendra Singh (lokendra.singh@centerforvein.com)</p>
            <p><strong>Website:</strong> www.centerforvein.com</p>
            <p><strong>Features:</strong> Screenshots, API/DB Logging, Assertions, Step-by-Step Logs</p>
        </div>
    """))


# ========================================================================
# CUSTOM CSS STYLING
# ========================================================================


def pytest_html_results_table_html(report, data):
    """Add custom CSS styles"""
    if report.when == "call" and not hasattr(pytest_html_results_table_html, "_css_added"):
        pytest_html_results_table_html._css_added = True
        data.append(extras.html("""
            <style>
                /* Enhanced Report Styles */
                .extra-details { margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 5px; }
                .extra-details h4 { color: #333; margin-top: 20px; margin-bottom: 10px; font-size: 16px; }
                
                /* Error Section */
                .error-section { background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin-bottom: 20px; }
                .error-message { background: #fff; padding: 10px; border: 1px solid #ddd; overflow-x: auto; }
                
                /* Screenshots */
                .screenshots-section { margin: 20px 0; }
                .screenshot-item { margin: 15px 0; }
                .screenshot-item img { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
                
                /* Tables */
                .api-calls-table, .db-queries-table, .assertions-table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 10px 0; 
                }
                .api-calls-table th, .db-queries-table th, .assertions-table th { 
                    background: #343a40; 
                    color: white; 
                    padding: 10px; 
                    text-align: left; 
                }
                .api-calls-table td, .db-queries-table td, .assertions-table td { 
                    padding: 8px; 
                    border-bottom: 1px solid #ddd; 
                }
                .api-calls-table tr:hover, .db-queries-table tr:hover, .assertions-table tr:hover { 
                    background: #f5f5f5; 
                }
                
                /* API Section */
                .api-section { margin: 20px 0; }
                
                /* DB Section */
                .db-section { margin: 20px 0; }
                
                /* Assertions Section */
                .assertions-section { margin: 20px 0; }
                
                /* Logs */
                .logs-section { margin: 20px 0; }
                .logs { 
                    background: #2d2d2d; 
                    color: #f8f8f2; 
                    padding: 15px; 
                    border-radius: 5px; 
                    overflow-x: auto; 
                    font-family: 'Courier New', monospace; 
                    font-size: 12px; 
                    line-height: 1.5; 
                }
            </style>
        """))


# ========================================================================
# HTML HELPER FUNCTIONS
# ========================================================================


def create_screenshot_html(screenshot: Dict):
    """Create HTML for screenshot display"""
    path = screenshot["path"]
    description = screenshot.get("description", "")
    timestamp = screenshot.get("timestamp", "")

    # Read and encode image
    if os.path.exists(path):
        with open(path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode("utf-8")

        return f"""
        <div class="screenshot-item">
            <p>{description} ({timestamp})</p>
            <img src="data:image/png;base64,{img_data}" style="max-width: 100%; border: 1px solid #ccc;" />
        </div>
        """
    else:
        return f'<div class="screenshot-item"><p>Screenshot not found: {path}</p></div>'


def create_video_html(video: Dict):
    """Create HTML for video display"""
    path = video["path"]
    timestamp = video.get("timestamp", "")

    if os.path.exists(path):
        return f"""
        <div class="video-item">
            <p>Video recorded at {timestamp}</p>
            <video controls style="max-width: 100%;">
                <source src="{path}" type="video/webm">
            </video>
        </div>
        """
    else:
        return f'<div class="video-item"><p>Video not found: {path}</p></div>'


def create_trace_html(trace: Dict):
    """Create HTML for trace file link"""
    path = trace["path"]
    timestamp = trace.get("timestamp", "")

    return f"""
    <div class="trace-item">
        <p>Trace file: {timestamp}</p>
        <a href="{path}" class="trace-link" download>Download Trace</a>
    </div>
    """


def create_api_calls_table(api_calls: List[Dict]):
    """Create HTML table for API calls"""
    rows_html = ""
    for call in api_calls:
        rows_html += f"""
        <tr>
            <td>{call['method']}</td>
            <td>{call['url']}</td>
            <td>{call['status_code']}</td>
            <td>{call['response_time']:.2f}ms</td>
            <td>{call['timestamp']}</td>
        </tr>
        """

    return f"""
    <table class="api-calls-table">
        <thead>
            <tr>
                <th>Method</th>
                <th>URL</th>
                <th>Status</th>
                <th>Response Time</th>
                <th>Timestamp</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """


def create_db_queries_table(db_queries: List[Dict]):
    """Create HTML table for database queries"""
    rows_html = ""
    for query in db_queries:
        query_text = query["query"][:100] + "..." if len(query["query"]) > 100 else query["query"]
        rows_html += f"""
        <tr>
            <td>{query_text}</td>
            <td>{query['execution_time']:.2f}ms</td>
            <td>{query.get('rows_affected', 0)}</td>
            <td>{query['timestamp']}</td>
        </tr>
        """

    return f"""
    <table class="db-queries-table">
        <thead>
            <tr>
                <th>Query</th>
                <th>Execution Time</th>
                <th>Rows Affected</th>
                <th>Timestamp</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """


def create_assertions_table(assertions: List[Dict]):
    """Create HTML table for assertions"""
    rows_html = ""
    for assertion in assertions:
        status = "✅" if assertion["passed"] else "❌"
        rows_html += f"""
        <tr>
            <td>{status}</td>
            <td>{assertion['type']}</td>
            <td>{assertion['expected']}</td>
            <td>{assertion['actual']}</td>
            <td>{assertion.get('message', '')}</td>
            <td>{assertion['timestamp']}</td>
        </tr>
        """

    return f"""
    <table class="assertions-table">
        <thead>
            <tr>
                <th>Status</th>
                <th>Type</th>
                <th>Expected</th>
                <th>Actual</th>
                <th>Message</th>
                <th>Timestamp</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """


# ========================================================================
# CUSTOM CSS STYLES (OLD - KEPT FOR REFERENCE)
# ========================================================================


def pytest_html_report_css(css):
    """Add custom CSS styles to report (old hook, may not work in all versions)"""
    pass


# ========================================================================
# FIXTURES
# ========================================================================


@pytest.fixture(scope="session", autouse=True)
def report_session(request):
    """Session-level report collection"""
    report_collector.start_session()
    yield
    report_collector.end_session()


@pytest.fixture(autouse=True)
def report_test(request):
    """Test-level report collection"""
    item = request.node

    # Initialize test data
    report_collector.init_test(item)
    report_collector.start_test(item)

    yield

    # Test end is handled in pytest_runtest_makereport hook


# ========================================================================
# ENHANCED FIXTURES WITH REPORTING
# ========================================================================


@pytest.fixture
def report_log(request):
    """Fixture to add logs to report"""
    test_id = request.node.nodeid

    def log(message: str, level: str = "INFO"):
        report_collector.add_log(test_id, message, level)

    return log


@pytest.fixture
def report_screenshot(request):
    """Fixture to add screenshots to report"""
    test_id = request.node.nodeid

    def screenshot(path: str, description: str = ""):
        report_collector.add_screenshot(test_id, path, description)

    return screenshot


@pytest.fixture
def report_api_call(request):
    """Fixture to add API call details to report"""
    test_id = request.node.nodeid

    def api_call(
        method: str,
        url: str,
        status_code: int,
        response_time: float,
        request_data: Dict = None,
        response_data: Dict = None,
    ):
        report_collector.add_api_call(
            test_id, method, url, status_code, response_time, request_data, response_data
        )

    return api_call


@pytest.fixture
def report_db_query(request):
    """Fixture to add database query details to report"""
    test_id = request.node.nodeid

    def db_query(query: str, execution_time: float, rows_affected: int = 0):
        report_collector.add_db_query(test_id, query, execution_time, rows_affected)

    return db_query


@pytest.fixture
def report_assertion(request):
    """Fixture to add assertion details to report"""
    test_id = request.node.nodeid

    def assertion(assertion_type: str, expected: Any, actual: Any, passed: bool, message: str = ""):
        report_collector.add_assertion(test_id, assertion_type, expected, actual, passed, message)

    return assertion


__all__ = [
    "report_collector",
    "TestReportCollector",
    "report_log",
    "report_screenshot",
    "report_api_call",
    "report_db_query",
    "report_assertion",
]
