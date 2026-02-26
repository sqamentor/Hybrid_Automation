"""
Interactive CLI Launcher - Modern, User-Friendly Test Execution
Guides users through project and test selection with beautiful UI

Features:
- 🎯 Project selection (bookslot, callcenter, patientintake)
- 📦 Test suite detection and selection
- � Browser selection (Chromium, Firefox, WebKit, Chrome, Edge)
- 🎭 Headless/Headed mode selection
- 🤖 Human behavior simulation toggle
- 🌍 Environment selection (staging, production)
- ⚙️ Execution options (parallel, markers)
- 📊 Report generation options
- 🎨 Beautiful, colorful interface
- 👤 Non-technical user friendly

Author: Lokendra Singh
Email: lokendra.singh@centerforvein.com
Website: www.centerforvein.com
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich import print as rprint
    import questionary
    from questionary import Style
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Installing required packages for interactive mode...")
    print("   Run: pip install rich questionary")

# Import configuration classes
try:
    from framework.cli.test_options import (
        BrowserConfig, BrowserType, BrowserMode,
        HumanBehaviorConfig,
        ExecutionConfig,
        ReportConfig,
        TestScopeConfig,
        FullTestConfig,
        ConfigPresets
    )
except ImportError:
    # Fallback if not available
    BrowserConfig = None


# Initialize console for rich output
console = Console()

# Custom style for questionary prompts
custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),       # Question mark - purple
    ('question', 'bold'),                 # Question text
    ('answer', 'fg:#f44336 bold'),       # Selected answer - red
    ('pointer', 'fg:#673ab7 bold'),      # Pointer - purple
    ('highlighted', 'fg:#673ab7 bold'),  # Highlighted option - purple
    ('selected', 'fg:#cc5454'),          # Selected option - red
    ('separator', 'fg:#cc5454'),         # Separator - red
    ('instruction', ''),                  # Instruction text
    ('text', ''),                         # Normal text
    ('disabled', 'fg:#858585 italic')    # Disabled options
])


def ask_yes_no(message: str, default: bool = True) -> bool:
    """Arrow-key selectable Yes/No prompt using questionary."""
    if default:
        choices = [
            questionary.Choice(title="✅ Yes", value=True),
            questionary.Choice(title="❌ No", value=False),
        ]
    else:
        choices = [
            questionary.Choice(title="❌ No", value=False),
            questionary.Choice(title="✅ Yes", value=True),
        ]
    result = questionary.select(
        message,
        choices=choices,
        style=custom_style,
        use_shortcuts=True
    ).ask()
    return result if result is not None else default


class InteractiveLauncher:
    """Interactive CLI launcher for test execution"""
    
    def __init__(self):
        """Initialize the interactive launcher"""
        self.workspace_root = self._find_workspace_root()
        self.projects_config = self._load_projects_config()
        self.selected_project = None
        self.selected_test_suite = None
        self.selected_environment = None
    
    def _find_workspace_root(self) -> Path:
        """Find the workspace root directory"""
        current = Path.cwd()
        
        # Look for workspace markers
        markers = ['pyproject.toml', 'pytest.ini', '.git']
        
        while current != current.parent:
            if any((current / marker).exists() for marker in markers):
                return current
            current = current.parent
        
        # Default to current directory
        return Path.cwd()
    
    def _load_projects_config(self) -> Dict:
        """Load projects configuration from YAML"""
        config_path = self.workspace_root / 'config' / 'projects.yaml'
        
        if not config_path.exists():
            return {'projects': {}}
        
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {'projects': {}}
        except Exception as e:
            console.print(f"[yellow]⚠️  Warning: Could not load projects config: {e}[/yellow]")
            return {'projects': {}}
    
    def show_welcome_banner(self):
        """Display welcome banner with rich formatting"""
        console.clear()
        
        banner = Panel.fit(
            "[bold cyan]🚀 AUTOMATION FRAMEWORK[/bold cyan]\n"
            "[white]Interactive Test Launcher[/white]\n\n"
            "[dim]Modern • Multi-Project • User-Friendly[/dim]",
            border_style="cyan",
            padding=(1, 2)
        )
        
        console.print(banner)
        console.print()
    
    def get_available_projects(self) -> List[Dict]:
        """Get list of available projects with metadata"""
        projects = []
        
        for project_id, config in self.projects_config.get('projects', {}).items():
            # Check if project has test files
            recorded_tests_path = self.workspace_root / 'recorded_tests' / project_id
            pages_path = self.workspace_root / 'pages' / project_id
            
            has_tests = recorded_tests_path.exists() and any(recorded_tests_path.glob('test_*.py'))
            has_pages = pages_path.exists() and any(pages_path.glob('*.py'))
            
            projects.append({
                'id': project_id,
                'name': config.get('name', project_id.title()),
                'description': config.get('description', 'No description'),
                'has_tests': has_tests,
                'has_pages': has_pages,
                'team': config.get('team', 'Unknown'),
                'environments': list(config.get('environments', {}).keys())
            })
        
        return projects
    
    def select_project(self) -> Optional[str]:
        """Interactive project selection"""
        projects = self.get_available_projects()
        
        if not projects:
            console.print("[red]❌ No projects found in configuration[/red]")
            return None
        
        # Create project options
        choices = []
        for project in projects:
            status = "✅" if project['has_tests'] else "⚠️"
            label = f"{status} {project['name']}"
            description = f"{project['description']} (Team: {project['team']})"
            choices.append(
                questionary.Choice(
                    title=f"{label}\n   [dim]{description}[/dim]",
                    value=project['id']
                )
            )
        
        # Add exit option
        choices.append(questionary.Choice(title="❌ Exit", value="exit"))
        
        console.print("[bold cyan]📋 Select a Project:[/bold cyan]\n")
        
        selected = questionary.select(
            "",
            choices=choices,
            style=custom_style,
            use_shortcuts=True
        ).ask()
        
        if selected == "exit" or selected is None:
            return None
        
        self.selected_project = selected
        return selected
    
    def detect_test_suites(self, project_id: str) -> List[Dict]:
        """Detect available test suites for a project"""
        test_suites = []
        
        # Check for direct project folder (new structure: tests/{project_id}/)
        direct_project_path = self.workspace_root / 'tests' / project_id
        if direct_project_path.exists() and direct_project_path.is_dir():
            # Count all test files recursively (pages/, e2e/, etc.)
            test_files = list(direct_project_path.rglob('test_*.py'))
            if test_files:
                test_suites.append({
                    'id': f'project_{project_id}',
                    'name': f'🎯 {project_id.title()} Test Suite',
                    'description': f'Complete test suite with organized structure ({len(test_files)} tests)',
                    'path': str(direct_project_path),
                    'type': 'project',
                    'count': len(test_files),
                    'files': [f.name for f in test_files]
                })
        
        # Check for recorded tests
        recorded_tests_path = self.workspace_root / 'recorded_tests' / project_id
        if recorded_tests_path.exists():
            test_files = list(recorded_tests_path.glob('test_*.py'))
            if test_files:
                test_suites.append({
                    'id': f'recorded_{project_id}',
                    'name': '📹 Recorded Tests',
                    'description': f'Recorded test workflows ({len(test_files)} tests)',
                    'path': str(recorded_tests_path),
                    'type': 'recorded',
                    'count': len(test_files),
                    'files': [f.name for f in test_files]
                })
        
        # Check for modern tests (Playwright)
        modern_tests_path = self.workspace_root / 'tests' / 'modern' / project_id
        if modern_tests_path.exists():
            test_files = list(modern_tests_path.glob('test_*.py'))
            if test_files:
                test_suites.append({
                    'id': f'modern_{project_id}',
                    'name': '🎭 Modern Tests (Playwright)',
                    'description': f'Playwright-based modern tests ({len(test_files)} tests)',
                    'path': str(modern_tests_path),
                    'type': 'modern',
                    'count': len(test_files),
                    'files': [f.name for f in test_files]
                })
        
        # Check for legacy tests (Selenium)
        legacy_tests_path = self.workspace_root / 'tests' / 'legacy' / project_id
        if legacy_tests_path.exists():
            test_files = list(legacy_tests_path.glob('test_*.py'))
            if test_files:
                test_suites.append({
                    'id': f'legacy_{project_id}',
                    'name': '🌐 Legacy Tests (Selenium)',
                    'description': f'Selenium-based legacy tests ({len(test_files)} tests)',
                    'path': str(legacy_tests_path),
                    'type': 'legacy',
                    'count': len(test_files),
                    'files': [f.name for f in test_files]
                })
        
        # Check for workflow tests
        workflow_tests_path = self.workspace_root / 'tests' / 'workflows'
        if workflow_tests_path.exists():
            test_files = [f for f in workflow_tests_path.glob('test_*.py') 
                         if project_id in f.name.lower()]
            if test_files:
                test_suites.append({
                    'id': f'workflow_{project_id}',
                    'name': '🔄 Workflow Tests (E2E)',
                    'description': f'End-to-end workflow tests ({len(test_files)} tests)',
                    'path': str(workflow_tests_path),
                    'type': 'workflow',
                    'count': len(test_files),
                    'files': [f.name for f in test_files]
                })
        
        return test_suites
    
    def select_action(self) -> Optional[str]:
        """Interactive action selection: Record or Run"""
        console.print(f"\n[bold cyan]🎯 What would you like to do?[/bold cyan]\n")
        
        choices = [
            questionary.Choice(
                title="🏃 Run Test Cases\n   [dim]Execute existing test suites and test files[/dim]",
                value="run"
            ),
            questionary.Choice(
                title="🎬 Record New Test\n   [dim]Record browser interactions to generate test scripts[/dim]",
                value="record"
            ),
            questionary.Choice(title="⬅️ Back to environment selection", value="back"),
            questionary.Choice(title="❌ Exit", value="exit")
        ]
        
        selected = questionary.select(
            "",
            choices=choices,
            style=custom_style,
            use_shortcuts=True
        ).ask()
        
        if selected == "exit" or selected is None:
            return None
        
        return selected
    
    def launch_recording(self, project_id: str, environment: str) -> int:
        """Launch the recording workflow with pre-selected project and environment"""
        try:
            from framework.cli.record import interactive_recording_for_project
            return interactive_recording_for_project(project_id, environment)
        except ImportError as e:
            console.print(f"[red]❌ Recording module not available: {e}[/red]")
            console.print("[yellow]   Make sure framework.cli.record is installed correctly[/yellow]")
            return 1
        except Exception as e:
            console.print(f"[red]❌ Recording failed: {e}[/red]")
            return 1
    
    def select_test_suite(self, project_id: str) -> Optional[Dict]:
        """Interactive test suite selection"""
        test_suites = self.detect_test_suites(project_id)
        
        if not test_suites:
            console.print(f"[red]❌ No test suites found for project '{project_id}'[/red]")
            return None
        
        console.print(f"\n[bold cyan]📦 Available Test Suites for {project_id.title()}:[/bold cyan]\n")
        
        # Create choices
        choices = []
        for suite in test_suites:
            choices.append(
                questionary.Choice(
                    title=f"{suite['name']}\n   [dim]{suite['description']}[/dim]",
                    value=suite
                )
            )
        
        # Add back and exit options
        choices.append(questionary.Choice(title="⬅️ Back to project selection", value="back"))
        choices.append(questionary.Choice(title="❌ Exit", value="exit"))
        
        selected = questionary.select(
            "",
            choices=choices,
            style=custom_style,
            use_shortcuts=True
        ).ask()
        
        if selected in ["exit", "back"] or selected is None:
            return None if selected == "exit" else "back"
        
        self.selected_test_suite = selected
        return selected
    
    def select_specific_test(self, test_suite: Dict) -> Optional[str]:
        """Select a specific test file from the suite"""
        
        # For project-type suites with organized structure, show categories
        if test_suite['type'] == 'project':
            return self.select_test_by_category(test_suite)
        
        # For other types, show flat list
        console.print(f"\n[bold cyan]🎯 Select a test file:[/bold cyan]\n")
        
        # Create choices for each test file
        choices = [
            questionary.Choice(title="🚀 Run All Tests", value="all")
        ]
        
        for test_file in test_suite['files']:
            choices.append(
                questionary.Choice(
                    title=f"📄 {test_file}",
                    value=test_file
                )
            )
        
        # Add back option
        choices.append(questionary.Choice(title="⬅️ Back to suite selection", value="back"))
        
        selected = questionary.select(
            "",
            choices=choices,
            style=custom_style,
            use_shortcuts=True
        ).ask()
        
        return selected
    
    def select_test_by_category(self, test_suite: Dict) -> Optional[str]:
        """Select tests by category for organized project structure"""
        from pathlib import Path
        
        console.print(f"\n[bold cyan]📂 Select Test Category:[/bold cyan]\n")
        
        # Organize tests by folder
        test_path = Path(test_suite['path'])
        categories = {}
        
        # Scan for test categories (subfolders)
        for test_file in test_path.rglob('test_*.py'):
            relative_path = test_file.relative_to(test_path)
            if len(relative_path.parts) > 1:
                category = relative_path.parts[0]
                if category not in categories:
                    categories[category] = []
                categories[category].append(test_file.name)
        
        # Build choices
        choices = [
            questionary.Choice(title="🚀 Run All Tests", value="all")
        ]
        
        # Add category-based options
        category_icons = {
            'pages': '📄',
            'e2e': '🔄',
            'integration': '🔗',
            'helpers': '🛠️',
            'fixtures': '📦',
            'data': '📊'
        }
        
        for category, files in sorted(categories.items()):
            icon = category_icons.get(category, '📁')
            count = len(files)
            choices.append(
                questionary.Choice(
                    title=f"{icon} {category.upper()} Tests\n   [dim]{count} test files[/dim]",
                    value=f"category:{category}"
                )
            )
        
        # Add back option
        choices.append(questionary.Choice(title="⬅️ Back to suite selection", value="back"))
        
        selected = questionary.select(
            "",
            choices=choices,
            style=custom_style,
            use_shortcuts=True
        ).ask()
        
        if selected and selected.startswith("category:"):
            # User selected a category, show files in that category
            category = selected.split(":", 1)[1]
            return self.select_test_from_category(test_suite, category, categories[category])
        
        return selected
    
    def select_test_from_category(self, test_suite: Dict, category: str, files: List[str]) -> Optional[str]:
        """Select a specific test file from a category"""
        console.print(f"\n[bold cyan]📄 Select Test from {category.upper()}:[/bold cyan]\n")
        
        choices = [
            questionary.Choice(
                title=f"🚀 Run All {category.upper()} Tests",
                value=f"{category}/*"
            )
        ]
        
        for test_file in sorted(files):
            choices.append(
                questionary.Choice(
                    title=f"  {test_file}",
                    value=f"{category}/{test_file}"
                )
            )
        
        # Add back option
        choices.append(questionary.Choice(title="⬅️ Back to categories", value="back"))
        
        selected = questionary.select(
            "",
            choices=choices,
            style=custom_style,
            use_shortcuts=True
        ).ask()
        
        if selected == "back":
            return self.select_test_by_category(test_suite)
        
        return selected
    
    def select_environment(self, project_id: str) -> Optional[str]:
        """Interactive environment selection"""
        project_config = self.projects_config.get('projects', {}).get(project_id, {})
        environments = list(project_config.get('environments', {}).keys())
        
        if not environments:
            console.print("[yellow]⚠️  No environments configured, using default[/yellow]")
            return "staging"
        
        console.print(f"\n[bold cyan]🌍 Select Environment:[/bold cyan]\n")
        
        # Create choices
        choices = []
        for env in environments:
            icon = "🎭" if env == "staging" else "🚀"
            env_config = project_config['environments'][env]
            ui_url = env_config.get('ui_url', 'N/A')
            choices.append(
                questionary.Choice(
                    title=f"{icon} {env.upper()}\n   [dim]{ui_url}[/dim]",
                    value=env
                )
            )
        
        # Add back option
        choices.append(questionary.Choice(title="⬅️ Back to test selection", value="back"))
        
        selected = questionary.select(
            "",
            choices=choices,
            style=custom_style,
            use_shortcuts=True
        ).ask()
        
        if selected == "back" or selected is None:
            return None
        
        self.selected_environment = selected
        return selected
    
    def select_browser_config(self) -> Optional[BrowserConfig]:
        """Interactive browser configuration selection"""
        console.print(f"\n[bold cyan]🌐 Select Browser:[/bold cyan]\n")
        
        if not BrowserConfig:
            console.print("[yellow]⚠️  Browser configuration not available[/yellow]")
            return None
        
        # Browser type selection
        browser_choices = BrowserConfig.get_browser_choices()
        choices = []
        
        for browser_info in browser_choices:
            icon = browser_info['icon']
            name = browser_info['name']
            desc = browser_info['description']
            recommended = browser_info.get('recommended', False)
            
            if recommended:
                title = f"{icon} {name} [bold green](Recommended)[/bold green]\n   [dim]{desc}[/dim]"
            else:
                title = f"{icon} {name}\n   [dim]{desc}[/dim]"
            
            choices.append(
                questionary.Choice(
                    title=title,
                    value=browser_info['browser']
                )
            )
        
        # Add back option
        choices.append(questionary.Choice(title="⬅️  Back", value="back"))
        
        selected_browser = questionary.select(
            "",
            choices=choices,
            style=custom_style,
            use_shortcuts=True
        ).ask()
        
        if selected_browser == "back" or selected_browser is None:
            return None
        
        # Browser mode selection (headless/headed)
        console.print(f"\n[bold cyan]🎭 Select Browser Mode:[/bold cyan]\n")
        
        mode_choices = [
            questionary.Choice(
                title="👁️  Headed (Visible)\n   [dim]Show browser window - good for debugging and development[/dim]",
                value=BrowserMode.HEADED
            ),
            questionary.Choice(
                title="🔇 Headless (Hidden)\n   [dim]Run browser in background - faster and suitable for CI/CD[/dim]",
                value=BrowserMode.HEADLESS
            ),
            questionary.Choice(title="⬅️  Back", value="back")
        ]
        
        selected_mode = questionary.select(
            "",
            choices=mode_choices,
            style=custom_style,
            use_shortcuts=True
        ).ask()
        
        if selected_mode == "back" or selected_mode is None:
            return None
        
        browser_config = BrowserConfig(
            browser=selected_browser,
            mode=selected_mode
        )
        
        console.print(f"[green]✅ Browser: {browser_config.get_description()}[/green]")
        return browser_config
    
    def select_human_behavior(self) -> Optional[HumanBehaviorConfig]:
        """Interactive human behavior configuration"""
        console.print(f"\n[bold cyan]🤖 Configure Human Behavior Simulation:[/bold cyan]\n")
        
        if not HumanBehaviorConfig:
            console.print("[yellow]⚠️  Human behavior configuration not available[/yellow]")
            return HumanBehaviorConfig(enabled=False)
        
        # Show information about human behavior
        info_panel = Panel(
            "[white]Human behavior simulation adds realistic delays and interactions:[/white]\n\n"
            "  • [cyan]Typing delays[/cyan] - Variable speed for different content types\n"
            "  • [cyan]Mouse movements[/cyan] - Bezier curves with acceleration/deceleration\n"
            "  • [cyan]Reading pauses[/cyan] - Realistic thinking time\n"
            "  • [cyan]Natural scrolling[/cyan] - Eased scrolling with variations\n\n"
            "[dim]Makes tests more realistic but adds execution time[/dim]",
            border_style="cyan",
            title="ℹ️  About Human Behavior"
        )
        console.print(info_panel)
        console.print()
        
        # Enable/disable selection
        enable_choices = [
            questionary.Choice(
                title="✅ Enable\n   [dim]Realistic interactions with natural delays (recommended for production-like testing)[/dim]",
                value=True
            ),
            questionary.Choice(
                title="⚡ Disable\n   [dim]Fast execution without delays (good for quick validation)[/dim]",
                value=False
            ),
            questionary.Choice(title="⬅️  Back", value="back")
        ]
        
        enabled = questionary.select(
            "Enable human behavior simulation?",
            choices=enable_choices,
            style=custom_style,
            use_shortcuts=True
        ).ask()
        
        if enabled == "back" or enabled is None:
            return None
        
        intensity = "normal"
        
        # If enabled, select intensity
        if enabled:
            console.print(f"\n[bold cyan]🎚️  Select Intensity Level:[/bold cyan]\n")
            
            intensity_choices = []
            for intensity_info in HumanBehaviorConfig.get_intensity_choices():
                icon = intensity_info['icon']
                name = intensity_info['name']
                desc = intensity_info['description']
                recommended = intensity_info.get('recommended', False)
                
                if recommended:
                    title = f"{icon} {name} [bold green](Recommended)[/bold green]\n   [dim]{desc}[/dim]"
                else:
                    title = f"{icon} {name}\n   [dim]{desc}[/dim]"
                
                intensity_choices.append(
                    questionary.Choice(
                        title=title,
                        value=intensity_info['value']
                    )
                )
            
            intensity_choices.append(questionary.Choice(title="⬅️  Back", value="back"))
            
            intensity = questionary.select(
                "",
                choices=intensity_choices,
                style=custom_style,
                use_shortcuts=True
            ).ask()
            
            if intensity == "back" or intensity is None:
                return None
        
        behavior_config = HumanBehaviorConfig(enabled=enabled, intensity=intensity)
        console.print(f"[green]✅ Human Behavior: {behavior_config.get_description()}[/green]")
        return behavior_config
    
    def select_execution_options(self) -> Optional[ExecutionConfig]:
        """Interactive execution options configuration"""
        console.print(f"\n[bold cyan]⚙️  Configure Execution Options:[/bold cyan]\n")
        
        if not ExecutionConfig:
            console.print("[yellow]⚠️  Execution configuration not available[/yellow]")
            return ExecutionConfig()
        
        # Parallel execution
        console.print("[bold]Parallel Execution:[/bold]")
        console.print("[yellow]⚠️  Warning:[/yellow] Parallel execution may cause issues with sync Playwright fixtures")
        console.print("[dim]Recommended: Disable parallel for POM tests with sync fixtures[/dim]\n")
        
        parallel = ask_yes_no(
            "Enable parallel execution?",
            default=False
        )
        
        num_workers = None
        if parallel:
            workers_input = Prompt.ask(
                "[cyan]Number of workers[/cyan]",
                default="auto"
            )
            if workers_input.lower() not in ["auto", ""]:
                try:
                    num_workers = int(workers_input)
                except ValueError:
                    console.print("[yellow]Invalid number, using auto[/yellow]")
                    num_workers = None
        
        # Markers
        console.print(f"\n[bold]Pytest Markers:[/bold]")
        console.print("[dim]Common markers: smoke, regression, integration, critical[/dim]\n")
        
        add_markers = ask_yes_no(
            "Add pytest markers?",
            default=False
        )
        
        markers = []
        if add_markers:
            markers_input = Prompt.ask(
                "[cyan]Enter markers (comma-separated)[/cyan]",
                default=""
            )
            if markers_input:
                markers = [m.strip() for m in markers_input.split(',')]
        
        # Verbosity
        verbose = ask_yes_no(
            "Verbose output?",
            default=True
        )
        
        exec_config = ExecutionConfig(
            parallel=parallel,
            num_workers=num_workers,
            markers=markers,
            verbose=verbose
        )
        
        console.print(f"[green]✅ Execution: {exec_config.get_description()}[/green]")
        return exec_config
    
    def select_report_options(self) -> Optional[ReportConfig]:
        """Interactive report options configuration"""
        console.print(f"\n[bold cyan]📊 Configure Report Generation:[/bold cyan]\n")
        
        if not ReportConfig:
            console.print("[yellow]⚠️  Report configuration not available[/yellow]")
            return ReportConfig()
        
        html = ask_yes_no(
            "Generate HTML report?",
            default=True
        )
        
        allure = ask_yes_no(
            "Generate Allure report?",
            default=False
        )
        
        report_config = ReportConfig(html=html, allure=allure)
        console.print(f"[green]✅ Reports: {report_config.get_description()}[/green]")
        return report_config
    
    def show_execution_summary(self, config: FullTestConfig, test_suite: Dict, 
                              test_file: str):
        """Display execution summary before running tests"""
        console.print()
        
        table = Table(title="📋 Test Execution Summary", 
                     border_style="cyan", 
                     show_header=False)
        table.add_column("Property", style="cyan bold", width=25)
        table.add_column("Value", style="white")
        
        # Basic info
        table.add_row("Project", config.project.upper())
        table.add_row("Test Suite", test_suite['name'])
        table.add_row("Test File", test_file if test_file != "all" else "All tests")
        table.add_row("Environment", config.environment.upper())
        
        # Browser config
        if config.browser:
            table.add_row("Browser", config.browser.get_description())
        
        # Human behavior
        if config.human_behavior:
            table.add_row("Human Behavior", config.human_behavior.get_description())
        
        # Execution options
        if config.execution:
            if config.execution.parallel:
                workers_str = f"{config.execution.num_workers} workers" if config.execution.num_workers else "auto"
                table.add_row("Parallel Execution", f"Yes ({workers_str})")
            else:
                table.add_row("Parallel Execution", "No")
            
            if config.execution.markers:
                table.add_row("Markers", ", ".join(config.execution.markers))
        
        # Reports
        if config.reports:
            reports_list = []
            if config.reports.html:
                reports_list.append("HTML")
            if config.reports.allure:
                reports_list.append("Allure")
            if reports_list:
                table.add_row("Reports", ", ".join(reports_list))
        
        table.add_row("Test Path", test_suite['path'])
        
        console.print(table)
        console.print()
    
    def execute_tests(self, config: FullTestConfig, test_suite: Dict, 
                     test_file: str) -> int:
        """Execute the selected tests"""
        # Determine test path
        if test_file == "all":
            test_path = test_suite['path']
        elif "/" in test_file and test_file.endswith("/*"):
            # Category pattern like "pages/*" - run all tests in that folder
            category = test_file.rstrip("/*")
            test_path = str(Path(test_suite['path']) / category)
        else:
            test_path = str(Path(test_suite['path']) / test_file)
        
        # Update config with test scope
        config.test_scope = TestScopeConfig(
            scope_type="file" if test_file != "all" else "all",
            test_file=test_path
        )
        
        # Generate pytest command
        cmd = config.to_pytest_command()
        
        console.print(f"[bold green]🚀 Executing tests...[/bold green]\n")
        console.print(f"[dim]Command: {' '.join(cmd)}[/dim]\n")
        console.print("="*80 + "\n")
        
        # Execute pytest
        try:
            result = subprocess.run(cmd, cwd=str(self.workspace_root))
            return result.returncode
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️  Test execution interrupted by user[/yellow]")
            return 1
        except Exception as e:
            console.print(f"\n[red]❌ Error executing tests: {e}[/red]")
            return 1
    
    def validate_configuration(self, config: FullTestConfig, test_suite: Dict, 
                              test_file: str) -> bool:
        """Validate configuration before execution"""
        console.print(f"\n[bold cyan]🔍 Validating Configuration...[/bold cyan]\n")
        
        validation_passed = True
        
        # Check if test path exists
        if test_file != "all":
            from pathlib import Path
            
            # Handle category patterns like "pages/*"
            if "/" in test_file and test_file.endswith("/*"):
                category = test_file.rstrip("/*")
                test_path = Path(test_suite['path']) / category
                if not test_path.exists() or not test_path.is_dir():
                    console.print(f"[red]❌ Test category not found: {category}[/red]")
                    validation_passed = False
                else:
                    console.print(f"[green]✅ Test category: {category}/[/green]")
            else:
                test_path = Path(test_suite['path']) / test_file
                if not test_path.exists():
                    console.print(f"[red]❌ Test file not found: {test_path}[/red]")
                    validation_passed = False
                else:
                    console.print(f"[green]✅ Test file exists: {test_file}[/green]")
        else:
            console.print(f"[green]✅ Test suite path: {test_suite['path']}[/green]")
        
        # Check environment
        console.print(f"[green]✅ Environment: {config.environment}[/green]")
        
        # Check browser configuration
        console.print(f"[green]✅ Browser: {config.browser.get_description()}[/green]")
        
        # Warn about parallel execution if enabled
        if config.execution.parallel:
            console.print("[yellow]⚠️  Parallel execution enabled - may cause issues with sync fixtures[/yellow]")
        
        console.print()
        return validation_passed
    
    def post_process_results(self, exit_code: int, config: FullTestConfig):
        """Post-processing after test execution"""
        import glob
        from pathlib import Path
        
        console.print("\n" + "="*80)
        console.print(f"[bold cyan]📊 Post-Processing Results...[/bold cyan]")
        console.print("="*80 + "\n")
        
        # Debug: Show exit code
        console.print(f"[dim]Exit code: {exit_code}[/dim]\n")
        
        # Show execution result based on pytest exit codes
        # https://docs.pytest.org/en/latest/reference/exit-codes.html
        if exit_code == 0:
            console.print("[bold green]✅ Tests completed successfully![/bold green]\n")
        elif exit_code == 5:
            console.print("[yellow]⚠️  No tests were collected/selected to run[/yellow]\n")
            console.print("[dim]Tip: Check your marker selection or test filters[/dim]\n")
        elif exit_code == 2:
            console.print("[yellow]⚠️  Test execution interrupted by user[/yellow]\n")
        elif exit_code == 3:
            console.print("[red]❌ Internal pytest error occurred[/red]\n")
        elif exit_code == 4:
            console.print("[red]❌ Pytest usage error - check command syntax[/red]\n")
        else:
            console.print("[bold red]❌ Tests failed![/bold red]\n")
        
        # Show report locations
        if config.reports.html:
            # Find the most recent HTML report
            html_reports = sorted(glob.glob("reports/*.html"), key=lambda x: Path(x).stat().st_mtime, reverse=True)
            if html_reports:
                latest_report = Path(html_reports[0])
                console.print(f"[cyan]📄 HTML Report:[/cyan] {latest_report}")
            else:
                console.print("[cyan]📄 HTML Report:[/cyan] reports/ (no reports found)")
        
        if config.reports.allure:
            console.print("[cyan]📊 Allure Results:[/cyan] allure-results/")
            console.print("[dim]   Generate report: allure serve allure-results[/dim]")
        
        # Show logs location - find latest log file
        log_files = sorted(glob.glob("logs/*.log"), key=lambda x: Path(x).stat().st_mtime, reverse=True)
        if log_files:
            latest_log = Path(log_files[0])
            console.print(f"[cyan]📝 Logs:[/cyan] {latest_log}")
        else:
            console.print(f"[cyan]📝 Logs:[/cyan] logs/ (no logs found)")
        
        # Show screenshots if any
        screenshot_files = sorted(glob.glob("screenshots/**/*.png", recursive=True), key=lambda x: Path(x).stat().st_mtime, reverse=True)
        if screenshot_files:
            latest_screenshot = Path(screenshot_files[0])
            screenshot_count = len(screenshot_files)
            console.print(f"[cyan]📸 Screenshots:[/cyan] {latest_screenshot} (+{screenshot_count-1} more)" if screenshot_count > 1 else f"[cyan]📸 Screenshots:[/cyan] {latest_screenshot}")
        else:
            console.print(f"[cyan]📸 Screenshots:[/cyan] screenshots/ (no screenshots)")
        
        # Show videos if any - check project-specific folder first
        video_pattern = f"videos/{config.project}/*.webm" if hasattr(config, 'project') else "videos/**/*.webm"
        video_files = sorted(glob.glob(video_pattern, recursive=True), key=lambda x: Path(x).stat().st_mtime, reverse=True)
        if video_files:
            latest_video = Path(video_files[0])
            console.print(f"[cyan]🎥 Videos:[/cyan] {latest_video}")
        else:
            console.print(f"[cyan]🎥 Videos:[/cyan] videos/ (no videos found)")
        
        console.print()
    
    def run(self) -> int:
        """
        Main interactive flow:
        1. Project
        2. Environment
        3. Suite
        4. Specific Tests
        5. Browser Config
        6. Execution Options
        7. Human Behavior
        8. Report Options
        9. Validate
        10. Show Summary
        11. Confirm
        12. Execute
        13. Post-Processing
        """
        if not RICH_AVAILABLE:
            print("❌ Interactive mode requires 'rich' and 'questionary' packages")
            print("   Install them with: pip install rich questionary")
            return 1
        
        try:
            while True:
                # Show welcome banner
                self.show_welcome_banner()
                
                # Step 1: Select Project
                project = self.select_project()
                if not project:
                    console.print("\n[yellow]👋 Goodbye![/yellow]\n")
                    return 0
                
                # Step 2: Select Environment (moved earlier)
                environment = self.select_environment(project)
                if not environment:
                    continue  # Go back to project selection
                
                # Step 3: Select Action (Record or Run)
                action = self.select_action()
                
                if action is None:
                    console.print("\n[yellow]👋 Goodbye![/yellow]\n")
                    return 0
                
                if action == "back":
                    continue  # Go back to project/environment selection
                
                if action == "record":
                    # Launch recording workflow
                    self.launch_recording(project, environment)
                    
                    # After recording, ask to continue
                    run_more = ask_yes_no(
                        "Would you like to continue?",
                        default=True
                    )
                    if not run_more:
                        console.print("\n[yellow]👋 Goodbye![/yellow]\n")
                        return 0
                    continue  # Go back to action selection
                
                # action == "run" → proceed to test suite selection
                # Step 4: Select Test Suite
                while True:
                    test_suite = self.select_test_suite(project)
                    
                    if test_suite is None:
                        console.print("\n[yellow]👋 Goodbye![/yellow]\n")
                        return 0
                    
                    if test_suite == "back":
                        break  # Go back to project/environment selection
                    
                    # Step 4: Select Specific Tests
                    test_file = self.select_specific_test(test_suite)
                    
                    if test_file == "back" or test_file is None:
                        continue  # Go back to suite selection
                    
                    # Step 5: Select Browser Configuration
                    browser_config = self.select_browser_config()
                    
                    if browser_config is None:
                        continue  # Go back to test selection
                    
                    # Step 6: Select Execution Options
                    execution_config = self.select_execution_options()
                    
                    if execution_config is None:
                        continue  # Go back
                    
                    # Step 7: Select Human Behavior Configuration
                    human_behavior_config = self.select_human_behavior()
                    
                    if human_behavior_config is None:
                        continue  # Go back
                    
                    # Step 8: Select Report Options
                    report_config = self.select_report_options()
                    
                    if report_config is None:
                        continue  # Go back
                    
                    # Build FullTestConfig
                    full_config = FullTestConfig(
                        project=project,
                        environment=environment,
                        browser=browser_config,
                        human_behavior=human_behavior_config,
                        execution=execution_config,
                        reports=report_config
                    )
                    
                    # Step 9: Validate Configuration
                    if not self.validate_configuration(full_config, test_suite, test_file):
                        console.print("[yellow]⚠️  Validation failed. Please review configuration.[/yellow]")
                        retry = ask_yes_no("Do you want to retry?", default=True)
                        if retry:
                            continue
                        else:
                            break
                    
                    # Step 10: Show Summary
                    self.show_execution_summary(full_config, test_suite, test_file)
                    
                    # Step 11: Confirm
                    proceed = ask_yes_no(
                        "🚀 Ready to execute tests?",
                        default=True
                    )
                    
                    if not proceed:
                        console.print("[yellow]Execution cancelled[/yellow]")
                        continue
                    
                    # Step 12: Execute Tests
                    exit_code = self.execute_tests(full_config, test_suite, test_file)
                    
                    # Step 13: Post-Processing
                    self.post_process_results(exit_code, full_config)
                    
                    # Ask to run more tests
                    run_more = ask_yes_no(
                        "Would you like to run more tests?",
                        default=True
                    )
                    
                    if not run_more:
                        console.print("\n[yellow]👋 Goodbye![/yellow]\n")
                        return exit_code
                    
                    # Ask if they want same project or different
                    same_project = ask_yes_no(
                        "Continue with the same project?",
                        default=True
                    )
                    
                    if not same_project:
                        break  # Go back to project selection
        
        except KeyboardInterrupt:
            console.print("\n\n[yellow]👋 Interrupted by user. Goodbye![/yellow]\n")
            return 0
        except Exception as e:
            console.print(f"\n[red]❌ Unexpected error: {e}[/red]\n")
            import traceback
            console.print("[dim]" + traceback.format_exc() + "[/dim]")
            return 1


def main(args: Optional[List[str]] = None) -> int:
    """Entry point for interactive CLI"""
    # Clear Python cache for fresh imports
    try:
        import shutil
        import os
        cache_dirs_removed = 0
        for root, dirs, files in os.walk('.'):
            if '__pycache__' in dirs:
                cache_path = os.path.join(root, '__pycache__')
                try:
                    shutil.rmtree(cache_path)
                    cache_dirs_removed += 1
                except Exception:
                    pass
        if cache_dirs_removed > 0:
            console.print(f"[dim]✅ Cache cleared ({cache_dirs_removed} directories)[/dim]")
    except Exception:
        pass
    
    launcher = InteractiveLauncher()
    return launcher.run()


if __name__ == '__main__':
    sys.exit(main())
