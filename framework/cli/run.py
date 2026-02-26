"""
Interactive Test Runner CLI - Beautiful Test Execution Interface
PROJECT-AWARE test execution with automatic configuration and guided selection
INTERACTIVE MODE with comprehensive options and scenarios

Author: Lokendra Singh
Email: lokendra.singh@centerforvein.com
Website: www.centerforvein.com
Assisted by: AI Claude (Anthropic)
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict
import subprocess
from datetime import datetime
import yaml

# Add project root to path (go up three levels from framework/cli/)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


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
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header():
    """Print beautiful header"""
    print("\n" + "="*80)
    print("🚀  INTELLIGENT TEST EXECUTION SYSTEM")
    print("    Interactive Test Runner - All Options at Your Fingertips")
    print("="*80 + "\n")


def print_section(title: str):
    """Print section header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_option(number: str, text: str, highlight: bool = False):
    """Print menu option"""
    if highlight:
        print(f"{Colors.GREEN}{Colors.BOLD}  {number}. {text}{Colors.ENDC}")
    else:
        print(f"{Colors.YELLOW}  {number}. {Colors.ENDC}{text}")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")


def print_command(command: str):
    """Print command to be executed"""
    print(f"\n{Colors.BOLD}📝 Command to Execute:{Colors.ENDC}")
    print(f"{Colors.CYAN}{'─'*80}{Colors.ENDC}")
    print(f"{Colors.GREEN}{command}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'─'*80}{Colors.ENDC}\n")


# ============================================================================
# TEST DISCOVERY
# ============================================================================

class TestDiscovery:
    """Discover available tests in the project"""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.tests_dir = root_dir / "tests"
        self.recorded_tests_dir = root_dir / "recorded_tests"
        
    def discover_all_tests(self) -> Dict[str, List[Path]]:
        """Discover all test files"""
        test_files = {
            'Integration Tests': [],
            'Recorded Tests - Bookslot': [],
            'Recorded Tests - CallCenter': [],
            'Recorded Tests - PatientIntake': [],
            'Unit Tests': [],
            'UI Tests': []
        }
        
        # Integration tests
        integration_dir = self.tests_dir / "integration"
        if integration_dir.exists():
            test_files['Integration Tests'] = list(integration_dir.glob("test_*.py"))
        
        # Recorded tests
        for project in ['bookslot', 'callcenter', 'patientintake']:
            project_dir = self.recorded_tests_dir / project
            if project_dir.exists():
                key = f'Recorded Tests - {project.title()}'
                test_files[key] = [
                    f for f in project_dir.glob("test_*.py")
                    if not f.name.startswith('__')
                ]
        
        # Unit tests
        unit_dir = self.tests_dir / "unit"
        if unit_dir.exists():
            test_files['Unit Tests'] = list(unit_dir.glob("test_*.py"))
        
        # UI tests
        ui_dir = self.tests_dir / "ui"
        if ui_dir.exists():
            test_files['UI Tests'] = list(ui_dir.glob("test_*.py"))
        
        # Remove empty categories
        return {k: v for k, v in test_files.items() if v}
    
    def get_test_categories(self) -> List[str]:
        """Get list of test categories"""
        tests = self.discover_all_tests()
        return list(tests.keys())


# ============================================================================
# COMMAND BUILDER
# ============================================================================

class CommandBuilder:
    """Build pytest command with options"""
    
    def __init__(self):
        self.base_command = "python -m pytest"
        self.test_path = None
        self.options = []
        
    def set_test_path(self, path: str):
        """Set test file or directory path"""
        self.test_path = path
        return self
    
    def add_option(self, option: str):
        """Add pytest option"""
        if option and option not in self.options:
            self.options.append(option)
        return self
    
    def add_verbose(self):
        """Add verbose output"""
        return self.add_option("-v")
    
    def add_show_output(self):
        """Add show output option"""
        return self.add_option("-s")
    
    def add_stop_on_failure(self):
        """Add stop on first failure"""
        return self.add_option("-x")
    
    def add_headed_mode(self):
        """Add headed browser mode"""
        return self.add_option("--headed")
    
    def add_slow_motion(self, milliseconds: int = 1000):
        """Add slow motion"""
        return self.add_option(f"--slowmo={milliseconds}")
    
    def add_browser(self, browser: str):
        """Add browser selection"""
        if browser in ['chromium', 'chrome', 'firefox', 'webkit', 'safari']:
            return self.add_option(f"--browser={browser}")
        return self
    
    def add_html_report(self, filename: str = None, project: str = None, environment: str = None):
        """
        Add HTML report generation with dynamic naming support.
        
        If filename is not provided, generates dynamic name:
        projectname_EnvironmentName_DDMMYYYY_HHMMSS.html
        
        Args:
            filename: Custom report filename (optional)
            project: Project name for dynamic naming (optional)
            environment: Environment name for dynamic naming (optional)
        """
        if filename:
            # User provided custom filename
            self.add_option(f"--html={filename}")
        else:
            # Note: Dynamic naming will be handled by conftest.py pytest_configure hook
            # We just need to ensure --self-contained-html is added
            # The report name will be automatically generated based on --project and --env options
            pass
        
        return self.add_option("--self-contained-html")
    
    def add_markers(self, markers: str):
        """Add marker filtering"""
        return self.add_option(f"-m '{markers}'")
    
    def add_keyword(self, keyword: str):
        """Add keyword filtering"""
        return self.add_option(f"-k '{keyword}'")
    
    def add_parallel(self, workers: int = 4):
        """Add parallel execution"""
        return self.add_option(f"-n {workers}")
    
    def add_environment(self, env: str):
        """Add environment selection (staging/production)"""
        if env.lower() in ['staging', 'production', 'prod']:
            return self.add_option(f"--env={env.lower()}")
        return self
    
    def add_human_behavior(self, enabled: bool = True):
        """Add human behavior simulation"""
        if enabled:
            return self.add_option("--enable-human-behavior")
        else:
            return self.add_option("--disable-human-behavior")
        return self
    
    def add_human_behavior_intensity(self, intensity: str = 'normal'):
        """Add human behavior intensity level"""
        if intensity in ['minimal', 'normal', 'high']:
            return self.add_option(f"--human-behavior-intensity {intensity}")
        return self
    
    def build(self) -> str:
        """Build final command"""
        parts = [self.base_command]
        if self.test_path:
            parts.append(self.test_path)
        parts.extend(self.options)
        return " ".join(parts)


# ============================================================================
# INTERACTIVE MENU SYSTEM
# ============================================================================

class InteractiveTestRunner:
    """Interactive test runner with guided options"""
    
    def __init__(self):
        self.root_dir = Path.cwd()
        self.discovery = TestDiscovery(self.root_dir)
        self.builder = CommandBuilder()
        self._load_project_urls()
    
    def _load_project_urls(self):
        """Load project URLs from projects.yaml for dynamic display"""
        try:
            # Use root_dir (project root) instead of __file__.parent (scripts/cli/)
            config_path = self.root_dir / "config" / "projects.yaml"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    data = yaml.safe_load(f)
                    projects = data.get('projects', {})
                    bookslot = projects.get('bookslot', {}).get('environments', {})
                    self.staging_url = bookslot.get('staging', {}).get('ui_url', 'staging-url-not-configured')
                    self.production_url = bookslot.get('production', {}).get('ui_url', 'production-url-not-configured')
            else:
                self.staging_url = f'projects.yaml not found at {config_path}'
                self.production_url = f'projects.yaml not found at {config_path}'
        except Exception as e:
            print(f"Warning: Could not load URLs from projects.yaml: {e}")
            self.staging_url = 'error loading config'
            self.production_url = 'error loading config'
        
    def run(self):
        """Run interactive test runner"""
        print_header()
        
        while True:
            choice = self.show_main_menu()
            
            if choice == '1':
                self.quick_run_mode()
            elif choice == '2':
                self.custom_run_mode()
            elif choice == '3':
                self.scenario_based_mode()
            elif choice == '4':
                self.show_all_tests()
            elif choice == '5':
                self.show_help()
            elif choice == '6':
                self.show_examples()
            elif choice == 'q':
                print_success("Thank you for using Interactive Test Runner!")
                break
            else:
                print_error("Invalid choice. Please try again.")
            
            input("\n\nPress Enter to continue...")
    
    def show_main_menu(self) -> str:
        """Show main menu"""
        print_section("🎯 MAIN MENU - Choose Your Test Execution Mode")
        
        print_option("1", "Quick Run - Run tests with recommended settings", highlight=True)
        print_option("2", "Custom Run - Build your own command with all options")
        print_option("3", "Scenario-Based - Pre-configured scenarios for common tasks")
        print_option("4", "Browse Tests - View all available tests")
        print_option("5", "Help & Documentation - Learn about options")
        print_option("6", "Examples - See command examples")
        print_option("q", "Quit")
        
        return input(f"\n{Colors.BOLD}Enter your choice: {Colors.ENDC}").strip().lower()
    
    def quick_run_mode(self):
        """Quick run with recommended settings"""
        print_section("⚡ QUICK RUN MODE")
        
        # Select test category
        tests = self.discovery.discover_all_tests()
        if not tests:
            print_error("No tests found!")
            return
        
        print("📂 Available Test Categories:\n")
        categories = list(tests.keys())
        for i, category in enumerate(categories, 1):
            count = len(tests[category])
            print_option(str(i), f"{category} ({count} tests)")
        
        choice = input(f"\n{Colors.BOLD}Select category (1-{len(categories)}): {Colors.ENDC}").strip()
        
        try:
            category_idx = int(choice) - 1
            if 0 <= category_idx < len(categories):
                category = categories[category_idx]
                test_files = tests[category]
                
                # Select specific test or all
                print(f"\n📝 Tests in {category}:\n")
                print_option("0", "Run ALL tests in this category", highlight=True)
                for i, test_file in enumerate(test_files, 1):
                    print_option(str(i), test_file.name)
                
                test_choice = input(f"\n{Colors.BOLD}Select test (0-{len(test_files)}): {Colors.ENDC}").strip()
                
                if test_choice == '0':
                    test_path = str(test_files[0].parent)
                else:
                    test_idx = int(test_choice) - 1
                    if 0 <= test_idx < len(test_files):
                        test_path = str(test_files[test_idx].relative_to(self.root_dir))
                    else:
                        print_error("Invalid test selection!")
                        return
                
                # Quick options
                print("\n⚙️ Quick Options:\n")
                print_option("1", "Headless (fast, no visible browser)", highlight=True)
                print_option("2", "Headed (visible browser)")
                print_option("3", "Headed + Slow Motion (watch it happen)")
                
                mode = input(f"\n{Colors.BOLD}Select mode (1-3): {Colors.ENDC}").strip()
                
                self.builder.set_test_path(test_path).add_verbose()
                
                if mode == '2':
                    self.builder.add_headed_mode()
                elif mode == '3':
                    self.builder.add_headed_mode().add_slow_motion(1000)
                
                # Ask for environment selection
                print("\n🌍 Environment Selection:\n")
                print_option("1", f"Staging ({self.staging_url})", highlight=True)
                print_option("2", f"Production ({self.production_url})")
                
                env_choice = input(f"\n{Colors.BOLD}Select environment (1-2, default=1): {Colors.ENDC}").strip()
                
                if env_choice == '2':
                    self.builder.add_environment('production')
                    print_info(f"✓ Selected: Production ({self.production_url})")
                else:
                    self.builder.add_environment('staging')
                    print_info(f"✓ Selected: Staging ({self.staging_url})")
                
                # Ask for human behavior
                print("\n🎭 Human Behavior Simulation:\n")
                print(f"  {Colors.CYAN}Makes automation look realistic (5-8x slower){Colors.ENDC}")
                print_option("1", "Disabled (Fast Mode - Recommended for Quick Run)", highlight=True)
                print_option("2", "Enabled (Realistic timing)")
                
                human_choice = input(f"\n{Colors.BOLD}Enable human behavior? (1-2, default=1): {Colors.ENDC}").strip()
                
                if human_choice == '2':
                    self.builder.add_human_behavior(True)
                    print_info("✓ Human behavior ENABLED")
                else:
                    print_info("✓ Human behavior DISABLED (fast mode)")
                
                self.execute_command()
        
        except (ValueError, IndexError):
            print_error("Invalid selection!")
    
    def custom_run_mode(self):
        """Custom run with all options"""
        print_section("🛠️ CUSTOM RUN MODE - Build Your Command")
        
        # Step 1: Select test
        tests = self.discovery.discover_all_tests()
        if not tests:
            print_error("No tests found!")
            return
        
        print("📂 Step 1: Select Test Category\n")
        categories = list(tests.keys())
        for i, category in enumerate(categories, 1):
            print_option(str(i), f"{category} ({len(tests[category])} tests)")
        
        cat_choice = input(f"\n{Colors.BOLD}Select category: {Colors.ENDC}").strip()
        
        try:
            category = categories[int(cat_choice) - 1]
            test_files = tests[category]
            
            print(f"\n📝 Step 2: Select Test File\n")
            print_option("0", "Run ALL tests in this category")
            for i, test_file in enumerate(test_files, 1):
                print_option(str(i), test_file.name)
            
            file_choice = input(f"\n{Colors.BOLD}Select test: {Colors.ENDC}").strip()
            
            if file_choice == '0':
                test_path = str(test_files[0].parent)
            else:
                test_file = test_files[int(file_choice) - 1]
                test_path = str(test_file.relative_to(self.root_dir))
            
            self.builder.set_test_path(test_path)
            
            # Step 3: Output options
            print("\n📊 Step 3: Output Options\n")
            if self.yes_no("Add verbose output (-v)?", default=True):
                self.builder.add_verbose()
            if self.yes_no("Show print statements (-s)?"):
                self.builder.add_show_output()
            if self.yes_no("Stop on first failure (-x)?"):
                self.builder.add_stop_on_failure()
            
            # Step 4: Browser options
            print("\n🌐 Step 4: Browser Options\n")
            if self.yes_no("Run in headed mode (visible browser)?"):
                self.builder.add_headed_mode()
                
                if self.yes_no("Add slow motion?"):
                    speed = input(f"{Colors.BOLD}Slow motion speed (ms, default=1000): {Colors.ENDC}").strip()
                    self.builder.add_slow_motion(int(speed) if speed else 1000)
                
                browser = input(f"{Colors.BOLD}Browser (chromium/firefox/webkit, default=chromium): {Colors.ENDC}").strip()
                if browser:
                    self.builder.add_browser(browser)
            
            # Step 5: Reporting
            print("\n📈 Step 5: Reporting Options\n")
            if self.yes_no("Generate HTML report?"):
                filename = input(f"{Colors.BOLD}Report filename (press Enter for dynamic naming): {Colors.ENDC}").strip()
                if filename:
                    # User provided custom filename
                    self.builder.add_html_report(filename=filename)
                else:
                    # Use dynamic naming (will be handled by conftest.py)
                    self.builder.add_html_report()
            
            # Step 6: Filtering
            print("\n🔍 Step 6: Filtering Options\n")
            if self.yes_no("Filter by keyword?"):
                keyword = input(f"{Colors.BOLD}Keyword: {Colors.ENDC}").strip()
                if keyword:
                    self.builder.add_keyword(keyword)
            
            # Step 7: Performance
            print("\n⚡ Step 7: Performance Options\n")
            if self.yes_no("Run tests in parallel?"):
                workers = input(f"{Colors.BOLD}Number of workers (default=4): {Colors.ENDC}").strip()
                self.builder.add_parallel(int(workers) if workers else 4)
            
            # Step 8: Environment Selection
            print("\n🌍 Step 8: Environment Selection\n")
            print("📍 Available Environments:")
            print(f"  {Colors.GREEN}• Staging{Colors.ENDC} - {self.staging_url}")
            print(f"  {Colors.YELLOW}• Production{Colors.ENDC} - {self.production_url}")
            
            env = input(f"\n{Colors.BOLD}Environment (staging/production, default=staging): {Colors.ENDC}").strip().lower()
            if not env or env == 'staging':
                self.builder.add_environment('staging')
                print_info("Selected: Staging Environment")
            elif env in ['production', 'prod']:
                self.builder.add_environment('production')
                print_info("Selected: Production Environment")
            else:
                self.builder.add_environment('staging')
                print_warning(f"Invalid environment '{env}', defaulting to Staging")
            
            # Step 9: Human Behavior Simulation
            print("\n🎭 Step 9: Human Behavior Simulation\n")
            print(f"  {Colors.CYAN}Human behavior mimics natural user interactions:{Colors.ENDC}")
            print(f"  • Character-by-character typing (0.08-0.25s per char)")
            print(f"  • Thinking pauses between actions (0.3-2.5s)")
            print(f"  • Realistic mouse movements and scrolling")
            print(f"  {Colors.YELLOW}⚠ Tests will run 5-8x slower but look realistic{Colors.ENDC}")
            
            if self.yes_no("\nEnable human behavior simulation?", default=False):
                self.builder.add_human_behavior(True)
                print_info("✓ Human behavior ENABLED")
                
                print("\n  Intensity levels:")
                print(f"  {Colors.GREEN}• minimal{Colors.ENDC} - Quick validation (2-3x slower)")
                print(f"  {Colors.YELLOW}• normal{Colors.ENDC}  - Standard timing (5-6x slower)")
                print(f"  {Colors.RED}• high{Colors.ENDC}    - Maximum realism (8-10x slower)")
                
                intensity = input(f"\n{Colors.BOLD}Intensity (minimal/normal/high, default=normal): {Colors.ENDC}").strip().lower()
                if intensity in ['minimal', 'normal', 'high']:
                    self.builder.add_human_behavior_intensity(intensity)
                    print_info(f"Intensity: {intensity}")
                else:
                    self.builder.add_human_behavior_intensity('normal')
                    print_info("Intensity: normal (default)")
            else:
                print_info("✗ Human behavior DISABLED (fast mode)")
            
            self.execute_command()
            
        except (ValueError, IndexError) as e:
            print_error(f"Invalid selection: {e}")
    
    def scenario_based_mode(self):
        """Pre-configured scenarios"""
        print_section("🎬 SCENARIO-BASED MODE")
        
        print("Choose a common scenario:\n")
        
        scenarios = {
            '1': {
                'name': '🚀 First Time Running - See What Happens',
                'desc': 'Visible browser, verbose output, stop on error',
                'options': ['-v', '-x', '--headed']
            },
            '2': {
                'name': '🐛 Debugging Issues',
                'desc': 'Visible browser, show prints, slow motion',
                'options': ['-v', '-s', '--headed', '--slowmo=1500']
            },
            '3': {
                'name': '🎥 Demo to Team',
                'desc': 'Visible browser, very slow, clear output',
                'options': ['-v', '--headed', '--slowmo=2000']
            },
            '3b': {
                'name': '🎭 Demo with Human Behavior',
                'desc': 'Realistic human-like automation for presentations',
                'options': ['-v', '--headed', '--enable-human-behavior', '--human-behavior-intensity high']
            },
            '4': {
                'name': '⚡ Quick Validation',
                'desc': 'Headless, verbose, stop on first failure',
                'options': ['-v', '-x']
            },
            '5': {
                'name': '📊 Generate Report',
                'desc': 'Headless, HTML report (dynamic naming), all tests',
                'options': ['-v', '--self-contained-html']
            },
            '6': {
                'name': '🔧 CI/CD Pipeline',
                'desc': 'Headless, verbose, JUnit XML output',
                'options': ['-v', '-x', '--junitxml=results.xml']
            },
            '7': {
                'name': '🏃 Parallel Execution',
                'desc': 'Run tests in parallel (4 workers)',
                'options': ['-v', '-n', '4']
            },
            '8': {
                'name': '📸 Capture Everything',
                'desc': 'Headed, screenshots on failure, video recording',
                'options': ['-v', '--headed', '--screenshot=on', '--video=retain-on-failure']
            }
        }
        
        for key, scenario in scenarios.items():
            print_option(key, f"{scenario['name']}")
            print(f"    {Colors.CYAN}└─ {scenario['desc']}{Colors.ENDC}")
            print()
        
        choice = input(f"\n{Colors.BOLD}Select scenario (1-{len(scenarios)}): {Colors.ENDC}").strip()
        
        if choice in scenarios:
            scenario = scenarios[choice]
            print_info(f"Selected: {scenario['name']}")
            
            # Select test
            tests = self.discovery.discover_all_tests()
            if not tests:
                print_error("No tests found!")
                return
            
            print("\n📂 Select Test Category:\n")
            categories = list(tests.keys())
            for i, category in enumerate(categories, 1):
                print_option(str(i), f"{category} ({len(tests[category])} tests)")
            
            cat_choice = input(f"\n{Colors.BOLD}Select category: {Colors.ENDC}").strip()
            
            try:
                category = categories[int(cat_choice) - 1]
                test_files = tests[category]
                
                print(f"\n📝 Select Test:\n")
                print_option("0", "Run ALL tests in category")
                for i, test_file in enumerate(test_files, 1):
                    print_option(str(i), test_file.name)
                
                file_choice = input(f"\n{Colors.BOLD}Select test: {Colors.ENDC}").strip()
                
                if file_choice == '0':
                    test_path = str(test_files[0].parent)
                else:
                    test_file = test_files[int(file_choice) - 1]
                    test_path = str(test_file.relative_to(self.root_dir))
                
                # Build command with scenario options
                self.builder = CommandBuilder()
                self.builder.set_test_path(test_path)
                for option in scenario['options']:
                    self.builder.add_option(option)
                
                # Ask for environment
                print("\n🌍 Select Environment:\n")
                print_option("1", f"Staging ({self.staging_url})", highlight=True)
                print_option("2", f"Production ({self.production_url})")
                
                env_choice = input(f"\n{Colors.BOLD}Environment (1-2, default=1): {Colors.ENDC}").strip()
                if env_choice == '2':
                    self.builder.add_environment('production')
                    print_info(f"Running on Production environment ({self.production_url})")
                else:
                    self.builder.add_environment('staging')
                    print_info(f"Running on Staging environment ({self.staging_url})")
                
                self.execute_command()
                
            except (ValueError, IndexError):
                print_error("Invalid selection!")
        else:
            print_error("Invalid scenario!")
    
    def show_all_tests(self):
        """Show all available tests"""
        print_section("📋 ALL AVAILABLE TESTS")
        
        tests = self.discovery.discover_all_tests()
        
        if not tests:
            print_error("No tests found!")
            return
        
        total = 0
        for category, test_files in tests.items():
            print(f"\n{Colors.GREEN}{Colors.BOLD}{category}{Colors.ENDC}")
            print(f"{Colors.CYAN}{'─'*80}{Colors.ENDC}")
            for test_file in test_files:
                print(f"  📄 {test_file.relative_to(self.root_dir)}")
                total += 1
        
        print(f"\n{Colors.BOLD}Total: {total} test files{Colors.ENDC}")
    
    def show_help(self):
        """Show help and documentation"""
        print_section("📚 HELP & DOCUMENTATION")
        
        help_text = """
🔧 PYTEST OPTIONS EXPLAINED:

OUTPUT OPTIONS:
  -v, --verbose          Verbose output (show test names)
  -s                     Show print statements and logging
  -q, --quiet            Quiet mode (less output)
  --tb=short             Shorter traceback format

EXECUTION CONTROL:
  -x, --exitfirst        Stop on first failure
  --maxfail=N            Stop after N failures
  -k EXPRESSION          Run tests matching keyword expression
  -m MARKERS             Run tests matching given mark expression

BROWSER OPTIONS (Playwright):
  --headed               Run browser in visible mode
  --headless             Run browser in headless mode (default)
  --browser=NAME         Browser to use (chromium/firefox/webkit)
  --slowmo=MS            Slow down operations by MS milliseconds

ENVIRONMENT:
  --env=staging          Run tests on staging environment (default)
  --env=production       Run tests on production environment

REPORTING:
  --html=FILE            Generate HTML report
  --junitxml=FILE        Generate JUnit XML report
  --alluredir=DIR        Generate Allure report data

PARALLEL EXECUTION:
  -n NUM                 Run tests in parallel with NUM workers
  --dist=loadscope       Distribute tests by scope

DEBUGGING:
  --pdb                  Drop into debugger on failures
  --trace                Drop into debugger at start of each test
  --lf, --last-failed    Rerun only failed tests from last run
  --ff, --failed-first   Run failed tests first, then others

PLAYWRIGHT SPECIFIC:
  --screenshot=on/off    Take screenshots (only-on-failure/on/off)
  --video=on/off         Record video (on/off/retain-on-failure)
  --tracing=on/off       Record traces (on/off/retain-on-failure)
        """
        
        print(help_text)
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}💡 TIPS:{Colors.ENDC}")
        print("  • Always use -v for better visibility")
        print("  • Use --headed first time to see what happens")
        print("  • Use -x to fail fast during debugging")
        print("  • Use -n for parallel execution on large test suites")
        print("  • Generate reports for documentation and sharing")
    
    def show_examples(self):
        """Show command examples"""
        print_section("💡 COMMAND EXAMPLES")
        
        examples = [
            ("Quick test with visible browser on staging",
             "python -m pytest tests/integration/test_example.py -v --headed --env=staging"),
            
            ("Debug mode with slow motion on production",
             "python -m pytest tests/integration/test_example.py -v -s --headed --slowmo=2000 --env=production"),
            
            ("Run specific test function",
             "python -m pytest tests/integration/test_example.py::test_function_name -v"),
            
            ("Run all tests in directory",
             "python -m pytest tests/integration/ -v"),
            
            ("Run tests matching keyword",
             "python -m pytest tests/ -v -k 'booking'"),
            
            ("Parallel execution",
             "python -m pytest tests/integration/ -v -n 4"),
            
            ("Generate HTML report (dynamic naming)",
             "python -m pytest tests/integration/ -v --self-contained-html"),
            
            ("CI/CD mode",
             "python -m pytest tests/integration/ -v -x --junitxml=results.xml"),
            
            ("Rerun only failed tests",
             "python -m pytest tests/integration/ -v --lf"),
            
            ("Run with screenshots and video",
             "python -m pytest tests/ -v --headed --screenshot=only-on-failure --video=retain-on-failure")
        ]
        
        for i, (desc, cmd) in enumerate(examples, 1):
            print(f"\n{Colors.YELLOW}{Colors.BOLD}{i}. {desc}{Colors.ENDC}")
            print(f"{Colors.CYAN}   {cmd}{Colors.ENDC}")
    
    def yes_no(self, question: str, default: bool = False) -> bool:
        """Ask yes/no question"""
        default_str = "Y/n" if default else "y/N"
        response = input(f"{Colors.BOLD}{question} [{default_str}]: {Colors.ENDC}").strip().lower()
        
        if not response:
            return default
        return response in ['y', 'yes']
    
    def execute_command(self):
        """Execute the built command"""
        command = self.builder.build()
        
        print_command(command)
        
        execute = self.yes_no("Execute this command now?", default=True)
        
        if execute:
            print_info("Executing test...")
            print(f"{Colors.CYAN}{'='*80}{Colors.ENDC}\n")
            
            try:
                result = subprocess.run(command, shell=True, cwd=str(self.root_dir))
                
                print(f"\n{Colors.CYAN}{'='*80}{Colors.ENDC}")
                if result.returncode == 0:
                    print_success("Tests completed successfully!")
                else:
                    print_error(f"Tests failed with exit code: {result.returncode}")
                    
            except Exception as e:
                print_error(f"Error executing command: {e}")
        else:
            print_info("Command not executed. You can copy and run it manually.")
        
        # Reset builder
        self.builder = CommandBuilder()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main(args: Optional[List[str]] = None):
    """Main entry point - can be called from unified CLI or standalone"""
    try:
        runner = InteractiveTestRunner()
        runner.run()
        return 0
    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print_info("Test runner interrupted by user")
        print("="*80)
        return 130
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
