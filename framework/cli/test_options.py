"""
Test Execution Options - Modular Configuration Classes
Reusable, dynamic, and microservice-style option handlers

These classes provide configuration for different aspects of test execution:
- Browser configuration (browser type, headless/headed mode)
- Human behavior simulation
- Execution options (parallel, markers)
- Report generation
- Test scope selection

Author: Lokendra Singh
Email: lokendra.singh@centerforvein.com
Website: www.centerforvein.com
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class BrowserType(str, Enum):
    """Supported browser types"""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"
    CHROME = "chrome"
    MSEDGE = "msedge"


class BrowserMode(str, Enum):
    """Browser execution modes"""
    HEADLESS = "headless"
    HEADED = "headed"


class TestEngine(str, Enum):
    """Test automation engines"""
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    HYBRID = "hybrid"


@dataclass
class BrowserConfig:
    """Browser configuration"""
    browser: BrowserType = BrowserType.CHROMIUM
    mode: BrowserMode = BrowserMode.HEADED
    engine: TestEngine = TestEngine.PLAYWRIGHT
    
    @property
    def is_headless(self) -> bool:
        """Check if running in headless mode"""
        return self.mode == BrowserMode.HEADLESS
    
    @property
    def is_headed(self) -> bool:
        """Check if running in headed mode"""
        return self.mode == BrowserMode.HEADED
    
    def to_pytest_args(self) -> List[str]:
        """Convert to pytest command line arguments"""
        args = [f"--test-browser={self.browser.value}"]
        
        # Map our browser type to Playwright's --browser flag
        # Playwright only supports: chromium, firefox, webkit
        # Chrome and MSEdge use Chromium engine with --browser-channel
        playwright_browser_map = {
            BrowserType.CHROMIUM: "chromium",
            BrowserType.FIREFOX: "firefox",
            BrowserType.WEBKIT: "webkit",
            BrowserType.CHROME: "chromium",
            BrowserType.MSEDGE: "chromium",
        }
        
        playwright_browser = playwright_browser_map.get(self.browser, "chromium")
        args.append(f"--browser={playwright_browser}")
        
        # For Chrome and Edge, use browser channel
        if self.browser == BrowserType.CHROME:
            args.append("--browser-channel=chrome")
        elif self.browser == BrowserType.MSEDGE:
            args.append("--browser-channel=msedge")
        
        if self.is_headless:
            args.append("--headless")
        else:
            args.append("--headed")
        
        return args

    
    def get_description(self) -> str:
        """Get human-readable description"""
        return f"{self.browser.value.title()} ({self.mode.value})"
    
    @classmethod
    def get_browser_choices(cls) -> List[Dict[str, Any]]:
        """Get list of browser choices for interactive selection"""
        return [
            {
                'browser': BrowserType.CHROMIUM,
                'name': 'Chromium',
                'description': 'Fast and reliable, good for most tests',
                'icon': '🚀',
                'recommended': True
            },
            {
                'browser': BrowserType.FIREFOX,
                'name': 'Firefox',
                'description': 'Good for cross-browser testing',
                'icon': '🦊'
            },
            {
                'browser': BrowserType.WEBKIT,
                'name': 'WebKit (Safari)',
                'description': 'Safari engine, good for Mac users',
                'icon': '🧭'
            },
            {
                'browser': BrowserType.CHROME,
                'name': 'Google Chrome',
                'description': 'Most popular browser, real Chrome',
                'icon': '💚'
            },
            {
                'browser': BrowserType.MSEDGE,
                'name': 'Microsoft Edge',
                'description': 'Chromium-based, good for Windows',
                'icon': '🔷'
            }
        ]


@dataclass
class HumanBehaviorConfig:
    """Human behavior simulation configuration"""
    enabled: bool = True
    intensity: str = "normal"  # minimal, normal, high
    typing_delay: bool = True
    mouse_movement: bool = True
    reading_pauses: bool = True
    natural_scrolling: bool = True
    
    def to_pytest_args(self) -> List[str]:
        """Convert to pytest command line arguments"""
        args = []
        
        if self.enabled:
            # Pass --enable-human-behavior flag to conftest.py
            args.append("--enable-human-behavior")
            
            # Pass intensity level
            if self.intensity:
                args.append(f"--human-behavior-intensity={self.intensity}")
        else:
            # Explicitly disable if configured as disabled
            args.append("--disable-human-behavior")
        
        return args
    
    def get_markers(self) -> List[str]:
        """
        Get pytest markers for human behavior.
        
        Note: Returns empty list because human behavior is controlled by:
        1. The @pytest.mark.human_like marker on tests (detected by fixture)
        2. Command-line flags like --enable-human-behavior
        
        We don't filter tests by marker; the fixture auto-applies to marked tests.
        """
        # Don't filter by marker - let the fixture handle it
        return []
    
    def get_description(self) -> str:
        """Get human-readable description"""
        if not self.enabled:
            return "Disabled (faster execution)"
        
        features = []
        if self.typing_delay:
            features.append("typing delays")
        if self.mouse_movement:
            features.append("mouse movements")
        if self.reading_pauses:
            features.append("reading pauses")
        if self.natural_scrolling:
            features.append("natural scrolling")
        
        return f"Enabled ({self.intensity}) - {', '.join(features)}"
    
    @classmethod
    def get_intensity_choices(cls) -> List[Dict[str, Any]]:
        """Get intensity level choices"""
        return [
            {
                'value': 'minimal',
                'name': 'Minimal',
                'description': 'Basic delays, faster execution (1-2s overhead)',
                'icon': '⚡'
            },
            {
                'value': 'normal',
                'name': 'Normal',
                'description': 'Balanced realism and speed (3-5s overhead)',
                'icon': '⚖️',
                'recommended': True
            },
            {
                'value': 'high',
                'name': 'High',
                'description': 'Very realistic, slower execution (5-10s overhead)',
                'icon': '🎭'
            }
        ]


@dataclass
class ExecutionConfig:
    """Test execution configuration"""
    parallel: bool = False
    num_workers: Optional[int] = None  # None means auto
    markers: List[str] = field(default_factory=list)
    verbose: bool = True
    capture_output: bool = False  # pytest -s flag
    stop_on_failure: bool = False  # pytest -x flag
    
    def to_pytest_args(self) -> List[str]:
        """Convert to pytest command line arguments"""
        args = []
        
        # Parallel execution
        if self.parallel:
            if self.num_workers:
                args.extend(["-n", str(self.num_workers)])
            else:
                args.extend(["-n", "auto"])
        
        # Verbosity
        if self.verbose:
            args.append("-v")
        else:
            args.append("-q")
        
        # Capture output
        if self.capture_output:
            args.append("-s")
        
        # Stop on failure
        if self.stop_on_failure:
            args.append("-x")
        
        # Markers (added separately in command builder)
        
        return args
    
    def get_marker_expression(self) -> Optional[str]:
        """Get combined marker expression"""
        if not self.markers:
            return None
        
        return " or ".join(self.markers)
    
    def get_description(self) -> str:
        """Get human-readable description"""
        parts = []
        
        if self.parallel:
            workers = self.num_workers or "auto"
            parts.append(f"Parallel: {workers} workers")
        else:
            parts.append("Sequential execution")
        
        if self.markers:
            parts.append(f"Markers: {', '.join(self.markers)}")
        
        if self.verbose:
            parts.append("Verbose output")
        
        if self.stop_on_failure:
            parts.append("Stop on first failure")
        
        return " | ".join(parts) if parts else "Default settings"


@dataclass
class ReportConfig:
    """Report generation configuration"""
    html: bool = True
    allure: bool = False
    junit: bool = False
    self_contained_html: bool = True
    html_path: Optional[str] = None
    allure_path: str = "allure-results"
    junit_path: str = "junit.xml"
    
    def to_pytest_args(self) -> List[str]:
        """Convert to pytest command line arguments"""
        args = []
        
        # HTML report
        # Note: Use default 'report.html' to trigger conftest.py dynamic naming
        # The conftest.py pytest_configure hook will generate dynamic name:
        # Format: projectname_EnvironmentName_DDMMYYYY_HHMMSS.html
        if self.html:
            if self.html_path:
                # Only use custom path if explicitly provided by user
                args.append(f"--html={self.html_path}")
            else:
                # Use default name to trigger dynamic naming in conftest.py
                args.append("--html=report.html")
            
            if self.self_contained_html:
                args.append("--self-contained-html")
        
        # Allure report
        if self.allure:
            args.append(f"--alluredir={self.allure_path}")
        
        # JUnit XML
        if self.junit:
            args.append(f"--junit-xml={self.junit_path}")
        
        return args
    
    def get_description(self) -> str:
        """Get human-readable description"""
        enabled = []
        
        if self.html:
            enabled.append("HTML")
        if self.allure:
            enabled.append("Allure")
        if self.junit:
            enabled.append("JUnit XML")
        
        return ", ".join(enabled) if enabled else "No reports"


@dataclass
@dataclass
class TestScopeConfig:
    """Test scope configuration"""
    scope_type: str = "all"  # all, file, function, marker
    test_file: Optional[str] = None
    test_function: Optional[str] = None
    test_class: Optional[str] = None
    
    def to_pytest_args(self) -> List[str]:
        """Convert to pytest command line arguments - path part"""
        args = []
        
        if self.scope_type == "file" and self.test_file:
            args.append(self.test_file)
        
        elif self.scope_type == "function" and self.test_file and self.test_function:
            args.append(f"{self.test_file}::{self.test_function}")
        
        elif self.scope_type == "class" and self.test_file and self.test_class:
            if self.test_function:
                args.append(f"{self.test_file}::{self.test_class}::{self.test_function}")
            else:
                args.append(f"{self.test_file}::{self.test_class}")
        
        # For "all", we don't add any specific path arguments
        
        return args
    
    def get_description(self) -> str:
        """Get human-readable description"""
        if self.scope_type == "all":
            return "All tests"
        elif self.scope_type == "file":
            from pathlib import Path
            return f"File: {Path(self.test_file).name if self.test_file else 'Unknown'}"
        elif self.scope_type == "function":
            return f"Function: {self.test_function}"
        elif self.scope_type == "class":
            return f"Class: {self.test_class}"
        return "Custom scope"


@dataclass
class FullTestConfig:
    """Complete test configuration combining all options"""
    project: str
    environment: str
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    human_behavior: HumanBehaviorConfig = field(default_factory=HumanBehaviorConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    reports: ReportConfig = field(default_factory=ReportConfig)
    test_scope: TestScopeConfig = field(default_factory=TestScopeConfig)
    
    def to_pytest_command(self, base_path: Optional[str] = None) -> List[str]:
        """Build complete pytest command"""
        import sys
        
        # Start with python -m pytest
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add project and environment
        cmd.extend([
            f"--project={self.project}",
            f"--env={self.environment}"
        ])
        
        # Add test scope (paths)
        if base_path and self.test_scope.scope_type == "all":
            cmd.append(base_path)
        else:
            cmd.extend(self.test_scope.to_pytest_args())
        
        # Add browser config
        cmd.extend(self.browser.to_pytest_args())
        
        # Add execution config
        cmd.extend(self.execution.to_pytest_args())
        
        # Add human behavior flags
        cmd.extend(self.human_behavior.to_pytest_args())
        
        # Add report config
        cmd.extend(self.reports.to_pytest_args())
        
        # Add markers (combined: human behavior + custom markers)
        all_markers = []
        all_markers.extend(self.human_behavior.get_markers())
        if self.execution.markers:
            all_markers.extend(self.execution.markers)
        
        if all_markers:
            marker_expr = " or ".join(all_markers)
            cmd.extend(["-m", marker_expr])
        
        # Disable pytest-asyncio plugin (for Playwright sync API)
        cmd.extend(["-p", "no:asyncio"])
        
        return cmd
    
    def get_summary(self) -> Dict[str, str]:
        """Get human-readable summary of all configurations"""
        return {
            'Project': self.project.upper(),
            'Environment': self.environment.upper(),
            'Browser': self.browser.get_description(),
            'Human Behavior': self.human_behavior.get_description(),
            'Execution': self.execution.get_description(),
            'Reports': self.reports.get_description(),
            'Test Scope': self.test_scope.get_description()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'project': self.project,
            'environment': self.environment,
            'browser': {
                'browser': self.browser.browser.value,
                'mode': self.browser.mode.value,
                'engine': self.browser.engine.value
            },
            'human_behavior': {
                'enabled': self.human_behavior.enabled,
                'intensity': self.human_behavior.intensity
            },
            'execution': {
                'parallel': self.execution.parallel,
                'num_workers': self.execution.num_workers,
                'markers': self.execution.markers,
                'verbose': self.execution.verbose
            },
            'reports': {
                'html': self.reports.html,
                'allure': self.reports.allure
            },
            'test_scope': {
                'scope_type': self.test_scope.scope_type,
                'test_file': self.test_scope.test_file,
                'test_function': self.test_scope.test_function
            }
        }


# ============================================================================
# CONFIGURATION PRESETS
# ============================================================================

class ConfigPresets:
    """Common configuration presets for different scenarios"""
    
    @staticmethod
    def quick_smoke_test(project: str, environment: str) -> FullTestConfig:
        """Quick smoke test configuration - fast and minimal"""
        return FullTestConfig(
            project=project,
            environment=environment,
            browser=BrowserConfig(
                browser=BrowserType.CHROMIUM,
                mode=BrowserMode.HEADLESS
            ),
            human_behavior=HumanBehaviorConfig(enabled=False),
            execution=ExecutionConfig(
                parallel=False,
                verbose=True,
                markers=["smoke"]
            ),
            reports=ReportConfig(html=True, allure=False)
        )
    
    @staticmethod
    def full_regression(project: str, environment: str) -> FullTestConfig:
        """Full regression test configuration"""
        return FullTestConfig(
            project=project,
            environment=environment,
            browser=BrowserConfig(
                browser=BrowserType.CHROMIUM,
                mode=BrowserMode.HEADLESS
            ),
            human_behavior=HumanBehaviorConfig(enabled=True, intensity="normal"),
            execution=ExecutionConfig(
                parallel=False,  # Avoid issues with sync fixtures
                verbose=True,
                markers=["regression"]
            ),
            reports=ReportConfig(html=True, allure=True)
        )
    
    @staticmethod
    def debug_single_test(project: str, environment: str,
                         test_file: str, test_function: str = None) -> FullTestConfig:
        """Debug single test configuration - visible browser, verbose"""
        return FullTestConfig(
            project=project,
            environment=environment,
            browser=BrowserConfig(
                browser=BrowserType.CHROMIUM,
                mode=BrowserMode.HEADED  # Visible for debugging
            ),
            human_behavior=HumanBehaviorConfig(enabled=True, intensity="normal"),
            execution=ExecutionConfig(
                parallel=False,
                verbose=True,
                capture_output=True  # Show print statements
            ),
            reports=ReportConfig(html=False, allure=False),
            test_scope=TestScopeConfig(
                scope_type="function" if test_function else "file",
                test_file=test_file,
                test_function=test_function
            )
        )
    
    @staticmethod
    def ci_cd_pipeline(project: str, environment: str) -> FullTestConfig:
        """CI/CD pipeline configuration - headless, fast, comprehensive reports"""
        return FullTestConfig(
            project=project,
            environment=environment,
            browser=BrowserConfig(
                browser=BrowserType.CHROMIUM,
                mode=BrowserMode.HEADLESS
            ),
            human_behavior=HumanBehaviorConfig(enabled=False),
            execution=ExecutionConfig(
                parallel=False,
                verbose=True,
                stop_on_failure=False  # Run all tests
            ),
            reports=ReportConfig(html=True, allure=True, junit=True)
        )
