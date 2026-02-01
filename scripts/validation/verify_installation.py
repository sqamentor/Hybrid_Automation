"""Dependency Installation Verification Script.

This script verifies that all required dependencies are installed correctly. Run this after
installing requirements.txt to ensure the framework is ready.
"""

import sys
from pathlib import Path


def check_python_version():
    """Check Python version."""
    print("=" * 80)
    print("CHECKING PYTHON VERSION")
    print("=" * 80)
    
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 11:
        print("✓ Python version is compatible (3.11+)")
        return True
    else:
        print("✗ Python version must be 3.11 or higher")
        return False


def check_core_packages():
    """Check core framework packages."""
    print("\n" + "=" * 80)
    print("CHECKING CORE PACKAGES")
    print("=" * 80)
    
    packages = {
        'pytest': 'pytest',
        'playwright': 'playwright',
        'selenium': 'selenium',
        'requests': 'requests',
        'sqlalchemy': 'SQLAlchemy',
        'openai': 'openai',
        'yaml': 'PyYAML',
        'dotenv': 'python-dotenv',
        'pydantic': 'pydantic',
        'allure_pytest': 'allure-pytest',
        'loguru': 'loguru',
    }
    
    results = {}
    for import_name, package_name in packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
            results[package_name] = True
        except ImportError as e:
            print(f"✗ {package_name} - NOT INSTALLED")
            results[package_name] = False
    
    return all(results.values())


def check_database_drivers():
    """Check database driver packages."""
    print("\n" + "=" * 80)
    print("CHECKING DATABASE DRIVERS")
    print("=" * 80)
    
    drivers = {
        'pyodbc': 'SQL Server (pyodbc)',
        'psycopg2': 'PostgreSQL (psycopg2)',
        'pymysql': 'MySQL (pymysql)',
    }
    
    results = {}
    for module, description in drivers.items():
        try:
            __import__(module)
            print(f"✓ {description}")
            results[module] = True
        except ImportError:
            print(f"⚠ {description} - NOT INSTALLED (optional)")
            results[module] = False
    
    # At least one driver should be installed
    return any(results.values())


def check_playwright_browsers():
    """Check if Playwright browsers are installed."""
    print("\n" + "=" * 80)
    print("CHECKING PLAYWRIGHT BROWSERS")
    print("=" * 80)
    
    try:
        from playwright.sync_api import sync_playwright
        
        browsers_found = []
        with sync_playwright() as p:
            # Check each browser
            browser_types = {
                'chromium': p.chromium,
                'firefox': p.firefox,
                'webkit': p.webkit
            }
            
            for name, browser_type in browser_types.items():
                try:
                    # Try to get browser path
                    browser = browser_type.launch(headless=True)
                    browser.close()
                    print(f"✓ {name.capitalize()}")
                    browsers_found.append(name)
                except Exception as e:
                    print(f"✗ {name.capitalize()} - NOT INSTALLED")
        
        if browsers_found:
            print(f"\nInstalled browsers: {', '.join(browsers_found)}")
            return True
        else:
            print("\n⚠ No Playwright browsers found. Run: playwright install")
            return False
            
    except Exception as e:
        print(f"✗ Error checking Playwright browsers: {e}")
        print("  Run: playwright install chromium firefox webkit")
        return False


def check_optional_packages():
    """Check optional packages."""
    print("\n" + "=" * 80)
    print("CHECKING OPTIONAL PACKAGES")
    print("=" * 80)
    
    optional = {
        'faker': 'Faker (test data generation)',
        'mimesis': 'Mimesis (test data generation)',
        'tenacity': 'Tenacity (retry logic)',
        'httpx': 'httpx (modern HTTP client)',
    }
    
    for module, description in optional.items():
        try:
            __import__(module)
            print(f"✓ {description}")
        except ImportError:
            print(f"⚠ {description} - NOT INSTALLED (optional)")


def check_framework_structure():
    """Check if framework directories exist."""
    print("\n" + "=" * 80)
    print("CHECKING FRAMEWORK STRUCTURE")
    print("=" * 80)
    
    base_path = Path(__file__).parent
    required_dirs = [
        'framework',
        'framework/core',
        'framework/ui',
        'framework/api',
        'framework/database',
        'framework/intelligence',
        'config',
        'tests',
        'docs',
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if full_path.exists():
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ - NOT FOUND")
            all_exist = False
    
    return all_exist


def check_configuration_files():
    """Check if configuration files exist."""
    print("\n" + "=" * 80)
    print("CHECKING CONFIGURATION FILES")
    print("=" * 80)
    
    base_path = Path(__file__).parent
    config_files = [
        'config/settings.py',
        'config/engine_decision_matrix.yaml',
        'config/api_db_mapping.yaml',
        'config/environments.yaml',
        'requirements.txt',
        'pytest.ini',
    ]
    
    all_exist = True
    for file_path in config_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - NOT FOUND")
            all_exist = False
    
    return all_exist


def main():
    """Run all verification checks."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "AUTOMATION FRAMEWORK VERIFICATION" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    results = {}
    
    # Run all checks
    results['Python Version'] = check_python_version()
    results['Core Packages'] = check_core_packages()
    results['Database Drivers'] = check_database_drivers()
    results['Playwright Browsers'] = check_playwright_browsers()
    check_optional_packages()  # Informational only
    results['Framework Structure'] = check_framework_structure()
    results['Configuration Files'] = check_configuration_files()
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    for check, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{check:.<50} {status}")
    
    print("\n" + "=" * 80)
    
    if all(results.values()):
        print("✓ ALL CHECKS PASSED - Framework is ready to use!")
        print("\nNext steps:")
        print("  1. Set environment variables (OPENAI_API_KEY, etc.)")
        print("  2. Update config/environments.yaml with your environment details")
        print("  3. Run example tests: pytest tests/examples/ -v")
        return 0
    else:
        print("✗ SOME CHECKS FAILED - Please review the output above")
        print("\nTo fix issues:")
        print("  1. Install missing packages: pip install -r requirements.txt")
        print("  2. Install Playwright browsers: playwright install")
        print("  3. Verify framework structure is complete")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
