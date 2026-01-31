"""
Interactive POM Test Runner CLI - Page Object Model Test Execution
Dynamic, intelligent, and failure-proof test execution for POM-based tests

Features:
- Interactive project selection (bookslot, callcenter, patientintake)
- Dynamic environment selection (staging, production)
- Browser selection with validation
- Test discovery and selection
- Pre-flight validation checks
- Human behavior toggle
- Report generation
- Parallel execution options

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import subprocess
from datetime import datetime
import yaml
import json

# Fix encoding for Windows console - MUST BE FIRST
if sys.platform == 'win32':
    try:
        # Try to reconfigure stdout to use UTF-8
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        # If reconfigure fails, we'll fall back to ASCII characters
        pass

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent))


# ============================================================================
# BEAUTIFUL CLI INTERFACE
# ============================================================================

class Colors:
    """ANSI color codes for beautiful output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_banner():
    """Print beautiful POM CLI banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
+============================================================================+
|                                                                            |
|                     POM TEST EXECUTION SYSTEM                              |
|                                                                            |
|        Page Object Model - Interactive & Intelligent Test Runner          |
|                                                                            |
+============================================================================+
{Colors.ENDC}
    """
    print(banner)


def print_section(title: str, icon: str = "[*]"):
    """Print section header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{icon}  {title}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_option(number: str, text: str, description: str = "", highlight: bool = False):
    """Print menu option with description"""
    if highlight:
        print(f"{Colors.GREEN}{Colors.BOLD}  [{number}] {text}{Colors.ENDC}")
    else:
        print(f"{Colors.YELLOW}  [{number}]{Colors.ENDC} {Colors.BOLD}{text}{Colors.ENDC}")
    if description:
        print(f"       {Colors.BLUE}{description}{Colors.ENDC}")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}[OK] {message}{Colors.ENDC}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}[X] {message}{Colors.ENDC}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}[i] {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}[!] {message}{Colors.ENDC}")


def print_command(command: str):
    """Print command to be executed"""
    print(f"\n{Colors.BOLD}[*] Command to Execute:{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-'*80}{Colors.ENDC}")
    print(f"{Colors.GREEN}{command}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-'*80}{Colors.ENDC}\n")


def get_input(prompt: str, default: str = None) -> str:
    """Get user input with optional default"""
    if default:
        full_prompt = f"{Colors.YELLOW}> {prompt} [{Colors.GREEN}{default}{Colors.YELLOW}]{Colors.ENDC}: "
    else:
        full_prompt = f"{Colors.YELLOW}> {prompt}{Colors.ENDC}: "
    
    user_input = input(full_prompt).strip()
    return user_input if user_input else default


def confirm(prompt: str, default: bool = True) -> bool:
    """Ask for confirmation"""
    default_str = "Y/n" if default else "y/N"
    full_prompt = f"{Colors.YELLOW}> {prompt} [{default_str}]{Colors.ENDC}: "
    
    response = input(full_prompt).strip().lower()
    if not response:
        return default
    return response in ['y', 'yes']


# ============================================================================
# CONFIGURATION LOADER
# ============================================================================

class ConfigLoader:
    """Load and validate framework configuration"""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.config_dir = root_dir / "config"
        self.projects = {}
        self.environments = {}
        
    def load_projects(self) -> Dict:
        """Load projects configuration"""
        projects_file = self.config_dir / "projects.yaml"
        
        if not projects_file.exists():
            raise FileNotFoundError(f"Projects config not found: {projects_file}")
        
        with open(projects_file, 'r') as f:
            data = yaml.safe_load(f)
            self.projects = data.get('projects', {})
        
        return self.projects
    
    def load_environments(self) -> Dict:
        """Load environments configuration"""
        env_file = self.config_dir / "environments.yaml"
        
        if not env_file.exists():
            raise FileNotFoundError(f"Environments config not found: {env_file}")
        
        with open(env_file, 'r') as f:
            data = yaml.safe_load(f)
            self.environments = data.get('environments', {})
        
        return self.environments
    
    def get_project_url(self, project: str, environment: str) -> str:
        """Get project URL for specific environment"""
        try:
            return self.projects[project]['environments'][environment]['ui_url']
        except KeyError:
            raise ValueError(f"URL not found for project '{project}' in environment '{environment}'")
    
    def validate_project(self, project: str) -> bool:
        """Validate if project exists"""
        return project in self.projects
    
    def validate_environment(self, environment: str) -> bool:
        """Validate if environment exists"""
        return environment in self.environments


# ============================================================================
# POM TEST DISCOVERY
# ============================================================================

class POMTestDiscovery:
    """Discover POM tests across all projects"""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.tests_dir = root_dir / "tests"
        self.pages_dir = root_dir / "pages"
        
    def discover_pom_tests(self, project: str = None) -> Dict[str, List[Path]]:
        """
        Discover all tests for a specific project
        
        Strategy:
        1. Find tests with project name in filename (e.g., test_bookslot*.py)
        2. Find tests that use project's POM fixture (e.g., bookslot_page)
        3. Exclude cross-application tests (tests using multiple project fixtures)
        
        Returns:
            Dict[project_name, List[test_files]]
        """
        pom_tests = {
            'bookslot': [],
            'callcenter': [],
            'patientintake': [],
            'integration': []
        }
        
        # Define all project fixtures for cross-app detection
        all_fixtures = {
            'bookslot': 'bookslot_page',
            'callcenter': 'callcenter_page', 
            'patientintake': 'patientintake_page'
        }
        
        # Search in tests directory
        for test_file in self.tests_dir.rglob("test_*.py"):
            # Skip unit tests
            if 'unit' in str(test_file):
                continue
            
            # Read file content
            try:
                content = test_file.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            
            # Check for each project
            for proj_name, proj_fixture in all_fixtures.items():
                # Skip if not the requested project
                if project and proj_name != project:
                    continue
                
                # Check if test uses this project's fixture
                uses_project_fixture = proj_fixture in content
                
                # Check if test uses OTHER project fixtures (cross-app test)
                other_fixtures = [f for p, f in all_fixtures.items() if p != proj_name]
                uses_other_fixtures = any(other_fixture in content for other_fixture in other_fixtures)
                
                # Check if filename contains project name
                has_project_in_name = proj_name in test_file.name.lower()
                
                # Include test if:
                # - Has project name in filename AND doesn't use other fixtures, OR
                # - Uses project fixture AND doesn't use other fixtures
                if (has_project_in_name or uses_project_fixture) and not uses_other_fixtures:
                    # Avoid duplicates
                    if test_file not in pom_tests[proj_name]:
                        pom_tests[proj_name].append(test_file)
                # Categorize cross-app tests separately
                elif uses_project_fixture and uses_other_fixtures and 'integration' in str(test_file):
                    if test_file not in pom_tests['integration']:
                        pom_tests['integration'].append(test_file)
        
        # Filter by project if specified
        if project:
            return {project: pom_tests.get(project, []), 'integration': []}
        
        return pom_tests
    
    def list_page_objects(self, project: str) -> List[Path]:
        """List all page objects for a project"""
        page_objects = []
        project_pages = self.pages_dir / project
        
        if project_pages.exists():
            for po_file in project_pages.glob("*.py"):
                if po_file.name != "__init__.py":
                    page_objects.append(po_file)
        
        return page_objects
    
    def get_test_functions(self, test_file: Path) -> List[str]:
        """Extract test function names from test file"""
        test_functions = []
        
        try:
            content = test_file.read_text(encoding='utf-8')
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('def test_'):
                    # Extract function name
                    func_name = line.split('(')[0].replace('def ', '')
                    test_functions.append(func_name)
        except Exception as e:
            print_warning(f"Could not parse {test_file.name}: {e}")
        
        return test_functions


# ============================================================================
# PRE-FLIGHT VALIDATION
# ============================================================================

class PreFlightValidator:
    """Validate environment before test execution"""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.validation_results = {}
        
    def validate_all(self) -> Tuple[bool, List[str]]:
        """Run all validation checks"""
        issues = []
        
        print_section("Pre-Flight Validation", "[CHK]")
        
        # 1. Check Python version
        if not self._validate_python():
            issues.append("Python version incompatible")
        
        # 2. Check pytest installation
        if not self._validate_pytest():
            issues.append("pytest not installed")
        
        # 3. Check playwright installation
        if not self._validate_playwright():
            issues.append("Playwright not installed")
        
        # 4. Check configuration files
        if not self._validate_configs():
            issues.append("Configuration files missing")
        
        # 5. Check page objects exist
        if not self._validate_page_objects():
            issues.append("Page objects directory missing")
        
        # 6. Check fixtures
        if not self._validate_fixtures():
            issues.append("conftest.py missing or invalid")
        
        if issues:
            print_error(f"Validation failed with {len(issues)} issue(s)")
            for issue in issues:
                print(f"  - {issue}")
            return False, issues
        else:
            print_success("All pre-flight checks passed!")
            return True, []
    
    def _validate_python(self) -> bool:
        """Validate Python version"""
        version = sys.version_info
        required = (3, 8)
        
        if version >= required:
            print_success(f"Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            print_error(f"Python {version.major}.{version.minor} (requires >= 3.8)")
            return False
    
    def _validate_pytest(self) -> bool:
        """Validate pytest installation"""
        # Try multiple methods to detect pytest
        methods = [
            (["pytest", "--version"], "direct"),
            (["python", "-m", "pytest", "--version"], "python module"),
            ([sys.executable, "-m", "pytest", "--version"], "sys.executable")
        ]
        
        for cmd, method in methods:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    print_success(f"pytest installed: {version}")
                    return True
            except Exception:
                continue
        
        print_error("pytest not found")
        return False
    
    def _validate_playwright(self) -> bool:
        """Validate Playwright installation"""
        # Try multiple methods to detect playwright
        methods = [
            (["playwright", "--version"], "direct"),
            (["python", "-m", "playwright", "--version"], "python module"),
            ([sys.executable, "-m", "playwright", "--version"], "sys.executable")
        ]
        
        for cmd, method in methods:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    print_success(f"Playwright installed: {version}")
                    return True
            except Exception:
                continue
        
        print_error("Playwright not found")
        return False
    
    def _validate_configs(self) -> bool:
        """Validate configuration files exist"""
        config_dir = self.root_dir / "config"
        required_files = ["projects.yaml", "environments.yaml"]
        
        all_exist = True
        for file in required_files:
            file_path = config_dir / file
            if file_path.exists():
                print_success(f"Config found: {file}")
            else:
                print_error(f"Config missing: {file}")
                all_exist = False
        
        return all_exist
    
    def _validate_page_objects(self) -> bool:
        """Validate page objects directory exists"""
        pages_dir = self.root_dir / "pages"
        
        if pages_dir.exists():
            # Check for project subdirectories
            projects = ['bookslot', 'callcenter', 'patientintake']
            found = []
            
            for project in projects:
                if (pages_dir / project).exists():
                    found.append(project)
            
            if found:
                print_success(f"Page Objects found: {', '.join(found)}")
                return True
        
        print_error("Page objects directory not found")
        return False
    
    def _validate_fixtures(self) -> bool:
        """Validate conftest.py exists with POM fixtures"""
        conftest = self.root_dir / "tests" / "conftest.py"
        
        if not conftest.exists():
            print_error("conftest.py not found")
            return False
        
        # Check for POM fixtures
        content = conftest.read_text(encoding='utf-8')
        fixtures = ['bookslot_page', 'patientintake_page', 'callcenter_page']
        found_fixtures = [f for f in fixtures if f in content]
        
        if found_fixtures:
            print_success(f"POM fixtures found: {', '.join(found_fixtures)}")
            return True
        else:
            print_error("No POM fixtures found in conftest.py")
            return False


# ============================================================================
# COMMAND BUILDER
# ============================================================================

class POMCommandBuilder:
    """Build pytest command for POM test execution"""
    
    def __init__(self):
        # Use current Python interpreter to run pytest module
        self.command_parts = [f'"{sys.executable}"', "-m", "pytest"]
        self.options = {}
        self.markers = []  # Collect all markers to combine later
        
    def set_project(self, project: str, environment: str):
        """Set project and environment"""
        self.options['project'] = project
        self.options['env'] = environment
        self.command_parts.append(f"--project={project}")
        self.command_parts.append(f"--env={environment}")
        return self
    
    def set_browser(self, browser: str, headless: bool = False):
        """Set browser configuration"""
        self.options['browser'] = browser
        self.command_parts.append(f"--test-browser={browser}")
        
        if headless:
            # Use custom --headless flag (defined in conftest.py)
            self.command_parts.append("--headless")
            self.options['headless'] = True
        else:
            # Use playwright's --headed flag to show browser window
            # Note: We use --headed (playwright's flag) instead of omitting --headless
            # because playwright runs headless by default
            self.command_parts.append("--headed")
            self.options['headless'] = False
        
        return self
    
    def set_human_behavior(self, enabled: bool = True):
        """Enable/disable human behavior simulation"""
        if enabled:
            self.markers.append("human_behavior")
            self.options['human_behavior'] = True
        else:
            # Don't add a marker when disabled - just don't filter
            self.options['human_behavior'] = False
        
        return self
    
    def set_test_file(self, test_file: Path):
        """Set specific test file"""
        self.options['test_file'] = str(test_file)
        self.command_parts.append(str(test_file))
        return self
    
    def set_test_function(self, test_function: str):
        """Set specific test function"""
        self.options['test_function'] = test_function
        # Append to last test file
        if self.command_parts[-1].endswith('.py'):
            self.command_parts[-1] = f"{self.command_parts[-1]}::{test_function}"
        return self
    
    def set_markers(self, markers: List[str]):
        """Set pytest markers"""
        if markers:
            self.markers.extend(markers)
            self.options['markers'] = markers
        return self
    
    def set_parallel(self, num_workers: int = None):
        """Enable parallel execution"""
        if num_workers:
            self.command_parts.append(f"-n {num_workers}")
            self.options['parallel'] = num_workers
        else:
            self.command_parts.append("-n auto")
            self.options['parallel'] = 'auto'
        return self
    
    def set_reports(self, html: bool = True, allure: bool = False):
        """Configure report generation"""
        if html:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_report = f"reports/pom_test_report_{timestamp}.html"
            self.command_parts.append(f"--html={html_report}")
            self.command_parts.append("--self-contained-html")
            self.options['html_report'] = html_report
        
        if allure:
            self.command_parts.append("--alluredir=allure-results")
            self.options['allure'] = True
        
        return self
    
    def set_verbosity(self, verbose: bool = True):
        """Set output verbosity"""
        if verbose:
            self.command_parts.append("-v")
            self.options['verbose'] = True
        else:
            self.command_parts.append("-q")
            self.options['verbose'] = False
        return self
    
    def add_custom_args(self, args: List[str]):
        """Add custom pytest arguments"""
        self.command_parts.extend(args)
        return self
    
    def build(self) -> str:
        """Build final command string"""
        # Disable pytest-asyncio plugin (required for Playwright sync API)
        # Playwright sync API cannot run inside asyncio event loops
        self.command_parts.append("-p no:asyncio")
        
        # Add markers as a single expression with OR logic at the end
        if self.markers:
            marker_expr = " or ".join(self.markers)
            self.command_parts.append(f'-m "{marker_expr}"')
        
        return " ".join(self.command_parts)
    
    def get_summary(self) -> str:
        """Get human-readable summary of options"""
        lines = [
            f"{Colors.BOLD}Test Execution Configuration:{Colors.ENDC}",
            ""
        ]
        
        if 'project' in self.options:
            lines.append(f"  [PRJ] Project: {Colors.GREEN}{self.options['project']}{Colors.ENDC}")
        
        if 'env' in self.options:
            lines.append(f"  [ENV] Environment: {Colors.GREEN}{self.options['env']}{Colors.ENDC}")
        
        if 'browser' in self.options:
            mode = " (headless)" if self.options.get('headless') else " (headed)"
            lines.append(f"  [WEB] Browser: {Colors.GREEN}{self.options['browser']}{mode}{Colors.ENDC}")
        
        if 'human_behavior' in self.options:
            status = "Enabled" if self.options['human_behavior'] else "Disabled"
            lines.append(f"  [AI] Human Behavior: {Colors.GREEN}{status}{Colors.ENDC}")
        
        if 'test_file' in self.options:
            lines.append(f"  [FILE] Test File: {Colors.CYAN}{Path(self.options['test_file']).name}{Colors.ENDC}")
        
        if 'test_function' in self.options:
            lines.append(f"  [FN] Test Function: {Colors.CYAN}{self.options['test_function']}{Colors.ENDC}")
        
        if 'parallel' in self.options:
            lines.append(f"  [//] Parallel: {Colors.GREEN}{self.options['parallel']} workers{Colors.ENDC}")
        
        if 'html_report' in self.options:
            lines.append(f"  [RPT] HTML Report: {Colors.GREEN}Yes{Colors.ENDC}")
        
        return "\n".join(lines)


# ============================================================================
# INTERACTIVE MENU SYSTEM
# ============================================================================

class InteractivePOMRunner:
    """Interactive POM test runner"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.config_loader = ConfigLoader(self.root_dir)
        self.test_discovery = POMTestDiscovery(self.root_dir)
        self.validator = PreFlightValidator(self.root_dir)
        self.command_builder = POMCommandBuilder()
        
        # Load configurations
        try:
            self.projects = self.config_loader.load_projects()
            self.environments = self.config_loader.load_environments()
        except Exception as e:
            print_error(f"Failed to load configuration: {e}")
            sys.exit(1)
    
    def run(self):
        """Main interactive flow"""
        print_banner()
        
        # Step 1: Pre-flight validation
        if not self._run_preflight_check():
            return
        
        # Step 2: Select project
        project = self._select_project()
        if not project:
            return
        
        # Step 3: Select environment
        environment = self._select_environment(project)
        if not environment:
            return
        
        # Step 4: Select browser
        browser, headless = self._select_browser()
        
        # Step 5: Select test scope
        test_file, test_function, project_test_files = self._select_test_scope(project)
        
        # Step 6: Configure human behavior
        human_behavior = self._configure_human_behavior()
        
        # Step 7: Configure execution options
        parallel, markers = self._configure_execution_options()
        
        # Step 8: Configure reports
        html_report, allure_report = self._configure_reports()
        
        # Step 9: Build command
        self._build_command(
            project, environment, browser, headless,
            test_file, test_function, human_behavior,
            parallel, markers, html_report, allure_report,
            project_test_files
        )
        
        # Step 10: Show summary and confirm
        if not self._confirm_execution():
            print_info("Execution cancelled by user")
            return
        
        # Step 11: Execute tests
        self._execute_tests()
    
    def _run_preflight_check(self) -> bool:
        """Run pre-flight validation"""
        print_info("Running pre-flight validation checks...")
        valid, issues = self.validator.validate_all()
        
        if not valid:
            if not confirm("Continue despite validation failures?", default=False):
                return False
        
        return True
    
    def _select_project(self) -> Optional[str]:
        """Interactive project selection"""
        print_section("Project Selection", "[*]")
        
        available_projects = list(self.projects.keys())
        
        print_info("Available projects:")
        for i, project in enumerate(available_projects, 1):
            project_info = self.projects[project]
            print_option(
                str(i), 
                project.upper(),
                project_info.get('description', '')
            )
        
        print_option("0", "Exit", "Cancel execution")
        
        while True:
            choice = get_input("Select project", "1")
            
            if choice == "0":
                return None
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available_projects):
                    selected = available_projects[idx]
                    print_success(f"Selected: {selected}")
                    return selected
                else:
                    print_error("Invalid selection")
            except ValueError:
                print_error("Please enter a number")
    
    def _select_environment(self, project: str) -> Optional[str]:
        """Interactive environment selection"""
        print_section("Environment Selection", "[ENV]")
        
        # Get environments from the selected project
        project_envs = self.projects[project].get('environments', {})
        available_envs = list(project_envs.keys())
        
        if not available_envs:
            print_error(f"No environments configured for project: {project}")
            return None
        
        print_info("Available environments:")
        for i, env in enumerate(available_envs, 1):
            env_info = project_envs[env]
            ui_url = env_info.get('ui_url', 'N/A')
            print_option(
                str(i),
                env.upper(),
                f"UI URL: {ui_url}"
            )
        
        print_option("0", "Back", "Go back to project selection")
        
        while True:
            choice = get_input("Select environment", "1")
            
            if choice == "0":
                return None
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available_envs):
                    selected = available_envs[idx]
                    print_success(f"Selected: {selected}")
                    return selected
                else:
                    print_error("Invalid selection")
            except ValueError:
                print_error("Please enter a number")
    
    def _select_browser(self) -> Tuple[str, bool]:
        """Interactive browser selection"""
        print_section("Browser Configuration", "[WEB]")
        
        browsers = [
            ("chromium", "Chromium - Fast and reliable"),
            ("firefox", "Firefox - Good for cross-browser testing"),
            ("webkit", "WebKit - Safari engine"),
            ("chrome", "Google Chrome - Most popular"),
            ("msedge", "Microsoft Edge - Chromium-based")
        ]
        
        print_info("Available browsers:")
        for i, (browser, desc) in enumerate(browsers, 1):
            print_option(str(i), browser.upper(), desc)
        
        while True:
            choice = get_input("Select browser", "1")
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(browsers):
                    browser = browsers[idx][0]
                    break
                else:
                    print_error("Invalid selection")
            except ValueError:
                print_error("Please enter a number")
        
        headless = confirm("Run in headless mode?", default=False)
        
        mode = "headless" if headless else "headed"
        print_success(f"Browser: {browser} ({mode})")
        
        return browser, headless
    
    def _select_test_scope(self, project: str) -> Tuple[Optional[Path], Optional[str], Optional[List[Path]]]:
        """Select test scope (all tests, specific file, or specific function)"""
        print_section("Test Scope Selection", "[TEST]")
        
        # Discover POM tests for this specific project
        pom_tests = self.test_discovery.discover_pom_tests(project)
        project_tests = pom_tests.get(project, [])
        
        # Also filter integration tests that use this project's fixture
        integration_tests = pom_tests.get('integration', [])
        project_integration_tests = []
        
        # Define all project fixtures to check for exclusions
        all_project_fixtures = ['bookslot_page', 'patientintake_page', 'callcenter_page']
        selected_fixture = f'{project}_page'
        other_fixtures = [f for f in all_project_fixtures if f != selected_fixture]
        
        for test_file in integration_tests:
            try:
                content = test_file.read_text(encoding='utf-8', errors='ignore')
                
                # Check if test uses this project's page fixture
                has_selected_fixture = selected_fixture in content
                
                # Check if test uses OTHER project fixtures (cross-application tests)
                has_other_fixtures = any(other_fixture in content for other_fixture in other_fixtures)
                
                # Include only if:
                # - Has selected project fixture AND
                # - Does NOT have other project fixtures (exclude cross-app tests)
                if has_selected_fixture and not has_other_fixtures:
                    project_integration_tests.append(test_file)
            except Exception:
                pass
        
        # Combine all tests for this project
        all_project_tests = project_tests + project_integration_tests
        
        if not all_project_tests:
            print_warning(f"No tests found for {project} project")
            return None, None, None
        
        print_info(f"Found {len(all_project_tests)} test file(s) for {project.upper()} project")
        
        print_info("Test scope options:")
        print_option("1", "Run ALL tests", f"Execute all {len(all_project_tests)} test files for {project}")
        print_option("2", "Run SPECIFIC test file", f"Choose from {len(all_project_tests)} test files")
        print_option("3", "Run SPECIFIC test function", "Choose a single test function")
        
        scope_choice = get_input("Select scope", "1")
        
        if scope_choice == "1":
            # Run all tests
            print_success(f"Scope: All {len(all_project_tests)} test files for {project}")
            return None, None, all_project_tests
        
        elif scope_choice == "2":
            # Select specific file
            if not all_project_tests:
                print_error("No test files found")
                return None, None, None
            
            # Filter to show only tests from the project's dedicated folder (tests/{project}/)
            project_folder_tests = [t for t in all_project_tests if f"tests{os.sep}{project}{os.sep}" in str(t)]
            
            # If no dedicated folder tests, show all tests
            tests_to_display = project_folder_tests if project_folder_tests else all_project_tests
            
            print(f"\n{Colors.CYAN}{Colors.BOLD}Available test files for {project.upper()}:{Colors.ENDC}")
            print(f"{Colors.BLUE}Location: tests/{project}/{Colors.ENDC}\n")
            
            for i, test_file in enumerate(tests_to_display, 1):
                # Show only filename for cleaner display
                file_desc = str(test_file.relative_to(self.root_dir / "tests" / project)) if f"tests{os.sep}{project}{os.sep}" in str(test_file) else test_file.name
                print_option(str(i), test_file.name, file_desc if file_desc != test_file.name else "")
            
            while True:
                file_choice = get_input("Select test file", "1")
                try:
                    idx = int(file_choice) - 1
                    if 0 <= idx < len(tests_to_display):
                        selected_file = tests_to_display[idx]
                        print_success(f"Selected: {selected_file.name}")
                        return selected_file, None, None
                    else:
                        print_error("Invalid selection")
                except ValueError:
                    print_error("Please enter a number")
        
        elif scope_choice == "3":
            # Select specific function
            if not all_project_tests:
                print_error("No test files found")
                return None, None, None
            
            # Filter to show only tests from the project's dedicated folder (tests/{project}/)
            project_folder_tests = [t for t in all_project_tests if f"tests{os.sep}{project}{os.sep}" in str(t)]
            
            # If no dedicated folder tests, show all tests
            tests_to_display = project_folder_tests if project_folder_tests else all_project_tests
            
            # First select file
            print(f"\n{Colors.CYAN}{Colors.BOLD}Available test files for {project.upper()}:{Colors.ENDC}")
            print(f"{Colors.BLUE}Location: tests/{project}/{Colors.ENDC}\n")
            
            for i, test_file in enumerate(tests_to_display, 1):
                # Show only filename for cleaner display
                file_desc = str(test_file.relative_to(self.root_dir / "tests" / project)) if f"tests{os.sep}{project}{os.sep}" in str(test_file) else test_file.name
                print_option(str(i), test_file.name, file_desc if file_desc != test_file.name else "")
            
            while True:
                file_choice = get_input("Select test file", "1")
                try:
                    idx = int(file_choice) - 1
                    if 0 <= idx < len(tests_to_display):
                        selected_file = tests_to_display[idx]
                        break
                    else:
                        print_error("Invalid selection")
                except ValueError:
                    print_error("Please enter a number")
            
            # Get test functions from file
            test_functions = self.test_discovery.get_test_functions(selected_file)
            
            if not test_functions:
                print_warning("No test functions found in file")
                return selected_file, None
            
            print(f"\nTest functions in {selected_file.name}:")
            for i, func in enumerate(test_functions, 1):
                print_option(str(i), func)
            
            while True:
                func_choice = get_input("Select test function", "1")
                try:
                    idx = int(func_choice) - 1
                    if 0 <= idx < len(test_functions):
                        selected_func = test_functions[idx]
                        print_success(f"Selected: {selected_func}")
                        return selected_file, selected_func, None
                    else:
                        print_error("Invalid selection")
                except ValueError:
                    print_error("Please enter a number")
        
        return None, None, None
    
    def _configure_human_behavior(self) -> bool:
        """Configure human behavior simulation"""
        print_section("Human Behavior Simulation", "[AI]")
        
        print_info("Human behavior simulation adds realistic delays and interactions")
        print_info("  - Typing delays")
        print_info("  - Mouse movements")
        print_info("  - Reading pauses")
        print_info("  - Natural scrolling")
        
        enabled = confirm("Enable human behavior simulation?", default=True)
        
        if enabled:
            print_success("Human behavior: ENABLED")
        else:
            print_info("Human behavior: DISABLED (faster execution)")
        
        return enabled
    
    def _configure_execution_options(self) -> Tuple[Optional[int], List[str]]:
        """Configure execution options (parallel, markers)"""
        print_section("Execution Options", "[CFG]")
        
        # Parallel execution - Warn about sync Playwright compatibility
        parallel = None
        print_warning("Note: Parallel execution may cause issues with sync Playwright fixtures")
        print_info("Recommended: Disable parallel for POM tests with sync fixtures")
        
        if confirm("Enable parallel execution?", default=False):
            num_workers = get_input("Number of workers (leave empty for auto)", "auto")
            if num_workers.lower() == "auto":
                parallel = None
                print_success("Parallel: Auto-detect workers")
            else:
                try:
                    parallel = int(num_workers)
                    print_success(f"Parallel: {parallel} workers")
                except ValueError:
                    print_warning("Invalid number, using auto")
                    parallel = None
        
        # Markers
        markers = []
        if confirm("Add pytest markers?", default=False):
            print_info("Common markers: smoke, regression, integration, critical")
            marker_input = get_input("Enter markers (comma-separated)", "")
            if marker_input:
                markers = [m.strip() for m in marker_input.split(',')]
                print_success(f"Markers: {', '.join(markers)}")
        
        return parallel, markers
    
    def _configure_reports(self) -> Tuple[bool, bool]:
        """Configure report generation"""
        print_section("Report Configuration", "[RPT]")
        
        html_report = confirm("Generate HTML report?", default=True)
        allure_report = confirm("Generate Allure report?", default=False)
        
        if html_report:
            print_success("HTML report: ENABLED")
        if allure_report:
            print_success("Allure report: ENABLED")
        
        return html_report, allure_report
    
    def _build_command(
        self, project, environment, browser, headless,
        test_file, test_function, human_behavior,
        parallel, markers, html_report, allure_report,
        project_test_files=None
    ):
        """Build pytest command with all options"""
        self.command_builder.set_project(project, environment)
        self.command_builder.set_browser(browser, headless)
        
        if test_file:
            self.command_builder.set_test_file(test_file)
            if test_function:
                self.command_builder.set_test_function(test_function)
        else:
            # Run specific project test files instead of entire directory
            if project_test_files:
                # Add each test file for this project
                for tf in project_test_files:
                    self.command_builder.command_parts.append(str(tf))
            else:
                # Fallback: run integration tests directory
                self.command_builder.command_parts.append("tests/integration")
        
        self.command_builder.set_human_behavior(human_behavior)
        
        if markers:
            self.command_builder.set_markers(markers)
        
        if parallel:
            self.command_builder.set_parallel(parallel)
        
        self.command_builder.set_reports(html_report, allure_report)
        self.command_builder.set_verbosity(verbose=True)
    
    def _confirm_execution(self) -> bool:
        """Show summary and confirm execution"""
        print_section("Execution Summary", "[SUM]")
        
        print(self.command_builder.get_summary())
        print()
        print_command(self.command_builder.build())
        
        return confirm("Execute tests now?", default=True)
    
    def _execute_tests(self):
        """Execute the tests"""
        print_section("Test Execution", "[RUN]")
        
        command = self.command_builder.build()
        
        print_info("Starting test execution...")
        print()
        print(f"{Colors.CYAN}[CMD] {command}{Colors.ENDC}")
        print()
        
        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.root_dir)
            )
            
            print()
            if result.returncode == 0:
                print_success("Tests completed successfully!")
            else:
                print_error(f"Tests failed with exit code: {result.returncode}")
            
            # Show report location
            if 'html_report' in self.command_builder.options:
                report_path = self.root_dir / self.command_builder.options['html_report']
                print()
                print_info(f"HTML Report: {report_path}")
                
                if confirm("Open HTML report?", default=False):
                    import webbrowser
                    webbrowser.open(report_path.as_uri())
        
        except KeyboardInterrupt:
            print()
            print_warning("Test execution interrupted by user")
        except Exception as e:
            print_error(f"Execution failed: {e}")


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    try:
        runner = InteractivePOMRunner()
        runner.run()
    except KeyboardInterrupt:
        print()
        print_warning("Execution cancelled by user")
    except Exception as e:
        print_error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
