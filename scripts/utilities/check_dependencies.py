"""
Dependency Checker for Test Automation Framework
Checks all required and optional dependencies and provides installation guidance.
"""

import importlib.util
import sys
from typing import Dict, List, Tuple

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Define dependencies
CRITICAL_DEPENDENCIES = [
    ('playwright', 'playwright', 'Playwright UI automation engine'),
    ('anthropic', 'anthropic', 'Claude AI provider support'),
    ('loguru', 'loguru', 'Advanced logging framework'),
]

CORE_DEPENDENCIES = [
    ('pytest', 'pytest', 'Testing framework'),
    ('selenium', 'selenium', 'Selenium UI automation'),
    ('requests', 'requests', 'HTTP client for API testing'),
    ('httpx', 'httpx', 'Modern async HTTP client'),
    ('SQLAlchemy', 'sqlalchemy', 'Database abstraction'),
    ('openai', 'openai', 'OpenAI/ChatGPT API'),
    ('PyYAML', 'yaml', 'YAML configuration'),
    ('pydantic', 'pydantic', 'Data validation'),
    ('Faker', 'faker', 'Test data generation'),
    ('Pillow', 'PIL', 'Image processing'),
    ('websockets', 'websockets', 'WebSocket testing'),
]

OPTIONAL_DEPENDENCIES = [
    ('pytest-playwright', 'pytest_playwright', 'Pytest Playwright integration'),
    ('pytest-timeout', 'pytest_timeout', 'Test timeout support'),
    ('pytest-xdist', 'xdist', 'Parallel test execution'),
    ('pytest-html', 'pytest_html', 'HTML test reports'),
    ('imagehash', 'imagehash', 'Visual regression testing'),
    ('pymysql', 'pymysql', 'MySQL database driver'),
    ('psycopg2-binary', 'psycopg2', 'PostgreSQL database driver'),
    ('pyodbc', 'pyodbc', 'SQL Server database driver'),
    ('mimesis', 'mimesis', 'Alternative data generator'),
    ('webdriver-manager', 'webdriver_manager', 'Auto WebDriver management'),
]


def check_dependency(module_name: str) -> bool:
    """Check if a Python module is installed"""
    return importlib.util.find_spec(module_name) is not None


def check_all_dependencies() -> Tuple[Dict, Dict, Dict]:
    """Check all dependencies and return status"""
    critical_status = {}
    core_status = {}
    optional_status = {}
    
    for pkg_name, module_name, description in CRITICAL_DEPENDENCIES:
        critical_status[pkg_name] = {
            'installed': check_dependency(module_name),
            'description': description,
            'module': module_name
        }
    
    for pkg_name, module_name, description in CORE_DEPENDENCIES:
        core_status[pkg_name] = {
            'installed': check_dependency(module_name),
            'description': description,
            'module': module_name
        }
    
    for pkg_name, module_name, description in OPTIONAL_DEPENDENCIES:
        optional_status[pkg_name] = {
            'installed': check_dependency(module_name),
            'description': description,
            'module': module_name
        }
    
    return critical_status, core_status, optional_status


def print_section(title: str, status_dict: Dict, show_installed: bool = False):
    """Print a section of dependency status"""
    print(f"\n{Colors.BOLD}{title}{Colors.RESET}")
    print("=" * 80)
    
    missing_count = sum(1 for v in status_dict.values() if not v['installed'])
    installed_count = len(status_dict) - missing_count
    
    # Print missing dependencies first
    if missing_count > 0:
        print(f"{Colors.RED}✗ MISSING ({missing_count}):{Colors.RESET}")
        for pkg, info in status_dict.items():
            if not info['installed']:
                print(f"  {Colors.RED}✗{Colors.RESET} {pkg:<25} - {info['description']}")
    
    # Print installed dependencies if requested
    if show_installed and installed_count > 0:
        print(f"\n{Colors.GREEN}✓ INSTALLED ({installed_count}):{Colors.RESET}")
        for pkg, info in status_dict.items():
            if info['installed']:
                print(f"  {Colors.GREEN}✓{Colors.RESET} {pkg:<25} - {info['description']}")
    elif installed_count > 0 and not show_installed:
        print(f"\n{Colors.GREEN}✓ INSTALLED: {installed_count}/{len(status_dict)}{Colors.RESET}")


def print_installation_commands(critical_status: Dict, optional_status: Dict):
    """Print installation commands for missing packages"""
    critical_missing = [pkg for pkg, info in critical_status.items() if not info['installed']]
    optional_missing = [pkg for pkg, info in optional_status.items() if not info['installed']]
    
    if not critical_missing and not optional_missing:
        return
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}INSTALLATION COMMANDS{Colors.RESET}")
    print("=" * 80)
    
    if critical_missing:
        print(f"\n{Colors.YELLOW}Install CRITICAL dependencies (required):{Colors.RESET}")
        cmd = "pip install " + " ".join(critical_missing)
        print(f"  {cmd}")
        
        if 'playwright' in critical_missing:
            print(f"\n{Colors.YELLOW}After installing Playwright, install browsers:{Colors.RESET}")
            print(f"  playwright install")
    
    if optional_missing:
        print(f"\n{Colors.YELLOW}Install OPTIONAL dependencies (recommended):{Colors.RESET}")
        cmd = "pip install " + " ".join(optional_missing)
        print(f"  {cmd}")
    
    print(f"\n{Colors.YELLOW}Or install ALL from requirements.txt:{Colors.RESET}")
    print(f"  pip install -r requirements.txt")
    print(f"  playwright install")


def print_framework_status(critical_status: Dict, core_status: Dict):
    """Print framework functionality status"""
    critical_ok = all(info['installed'] for info in critical_status.values())
    core_ok = all(info['installed'] for info in core_status.values())
    
    playwright_installed = critical_status.get('playwright', {}).get('installed', False)
    anthropic_installed = critical_status.get('anthropic', {}).get('installed', False)
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}FRAMEWORK FUNCTIONALITY STATUS{Colors.RESET}")
    print("=" * 80)
    
    # API Testing
    api_status = "✓ READY" if core_status.get('requests', {}).get('installed', False) else "✗ NOT READY"
    color = Colors.GREEN if "READY" in api_status else Colors.RED
    print(f"  API Testing:              {color}{api_status}{Colors.RESET}")
    
    # Selenium UI
    selenium_status = "✓ READY" if core_status.get('selenium', {}).get('installed', False) else "✗ NOT READY"
    color = Colors.GREEN if "READY" in selenium_status else Colors.RED
    print(f"  Selenium UI Automation:   {color}{selenium_status}{Colors.RESET}")
    
    # Playwright UI
    playwright_status = "✓ READY" if playwright_installed else "✗ NOT INSTALLED"
    color = Colors.GREEN if playwright_installed else Colors.RED
    print(f"  Playwright UI Automation: {color}{playwright_status}{Colors.RESET}")
    
    # AI Features
    openai_ok = core_status.get('openai', {}).get('installed', False)
    if openai_ok and anthropic_installed:
        ai_status = "✓ FULL (OpenAI + Claude)"
        color = Colors.GREEN
    elif openai_ok:
        ai_status = "⚠ PARTIAL (OpenAI only, Claude missing)"
        color = Colors.YELLOW
    else:
        ai_status = "✗ NO AI (uses fallback)"
        color = Colors.RED
    print(f"  AI Features:              {color}{ai_status}{Colors.RESET}")
    
    # Database
    db_count = sum(1 for pkg in ['SQLAlchemy', 'pyodbc'] if core_status.get(pkg, {}).get('installed', False))
    db_status = f"✓ READY ({db_count} drivers)" if db_count >= 1 else "✗ NOT READY"
    color = Colors.GREEN if "READY" in db_status else Colors.RED
    print(f"  Database Testing:         {color}{db_status}{Colors.RESET}")
    
    # Overall
    if critical_ok and core_ok:
        overall = f"{Colors.GREEN}100% FUNCTIONAL{Colors.RESET}"
    elif core_ok:
        overall = f"{Colors.YELLOW}~80% FUNCTIONAL (missing optional){Colors.RESET}"
    else:
        overall = f"{Colors.RED}~50-70% FUNCTIONAL (missing critical){Colors.RESET}"
    
    print(f"\n  Overall Framework Status: {overall}")


def main():
    """Main function"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  TEST AUTOMATION FRAMEWORK - DEPENDENCY CHECKER{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}")
    
    print(f"\n{Colors.YELLOW}Checking dependencies...{Colors.RESET}")
    
    critical_status, core_status, optional_status = check_all_dependencies()
    
    # Print sections
    print_section("1. CRITICAL DEPENDENCIES (Required for Full Functionality)", critical_status, show_installed=True)
    print_section("2. CORE DEPENDENCIES (Framework Essentials)", core_status, show_installed=False)
    print_section("3. OPTIONAL DEPENDENCIES (Enhanced Features)", optional_status, show_installed=False)
    
    # Print framework status
    print_framework_status(critical_status, core_status)
    
    # Print installation commands
    print_installation_commands(critical_status, optional_status)
    
    # Summary
    total_critical = len(critical_status)
    missing_critical = sum(1 for v in critical_status.values() if not v['installed'])
    total_optional = len(optional_status)
    missing_optional = sum(1 for v in optional_status.values() if not v['installed'])
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}SUMMARY{Colors.RESET}")
    print("=" * 80)
    print(f"  Critical Missing: {Colors.RED if missing_critical > 0 else Colors.GREEN}{missing_critical}/{total_critical}{Colors.RESET}")
    print(f"  Optional Missing: {Colors.YELLOW if missing_optional > 0 else Colors.GREEN}{missing_optional}/{total_optional}{Colors.RESET}")
    
    if missing_critical > 0:
        print(f"\n{Colors.RED}{Colors.BOLD}ACTION REQUIRED:{Colors.RESET} Install critical dependencies to enable full framework functionality.")
        print(f"{Colors.YELLOW}Run:{Colors.RESET} python install_missing_dependencies.ps1")
        return 1
    elif missing_optional > 0:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}RECOMMENDED:{Colors.RESET} Install optional dependencies for enhanced features.")
        print(f"{Colors.YELLOW}Run:{Colors.RESET} python install_missing_dependencies.ps1")
        return 0
    else:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL DEPENDENCIES INSTALLED!{Colors.RESET} Framework is ready to use.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
