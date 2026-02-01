"""
Quick Start Script - First Time Setup Helper

This script guides you through the initial setup after installing dependencies.

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com
Assisted by: AI Claude (Anthropic)
"""

import os
from pathlib import Path


def create_env_file():
    """Create .env file with template"""
    print("=" * 80)
    print("CREATING .env FILE")
    print("=" * 80)
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠ .env file already exists")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Skipping .env creation")
            return
    
    env_template = """# Automation Framework Environment Variables

# AI Configuration
OPENAI_API_KEY=sk-your-api-key-here
# OPENAI_API_TYPE=azure  # Uncomment for Azure OpenAI
# AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com
# AZURE_OPENAI_KEY=your-azure-key
# AZURE_OPENAI_DEPLOYMENT=your-deployment-name

# Environment Selection
TEST_ENV=dev  # dev, staging, production

# Database Configuration (optional - can be in environments.yaml)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=testdb
DB_USER=testuser
DB_PASSWORD=testpass

# Browser Configuration
BROWSER=chromium  # chromium, firefox, webkit
HEADLESS=false  # true for headless mode

# Reporting
ALLURE_RESULTS_DIR=allure-results
SCREENSHOTS_DIR=screenshots
VIDEOS_DIR=videos
TRACES_DIR=traces

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE=true

# Optional: Cloud Grid
# BROWSERSTACK_USERNAME=your_username
# BROWSERSTACK_ACCESS_KEY=your_key
# LAMBDATEST_USERNAME=your_username
# LAMBDATEST_ACCESS_KEY=your_key
"""
    
    env_file.write_text(env_template)
    print(f"✓ Created {env_file.absolute()}")
    print("\n⚠ IMPORTANT: Update the values in .env file before running tests")


def show_quick_start_guide():
    """Show quick start guide"""
    print("\n" + "=" * 80)
    print("QUICK START GUIDE")
    print("=" * 80)
    
    guide = """
1. CONFIGURE ENVIRONMENT
   ✓ Edit .env file with your API keys and configuration
   ✓ Update config/environments.yaml with your application URLs

2. VERIFY INSTALLATION
   Run: python verify_installation.py

3. RUN YOUR FIRST TEST
   
   Option A - Run example tests:
   pytest tests/integration/test_ui_api_db_flow.py -v
   
   Option B - Run smoke tests:
   pytest -m smoke -v
   
   Option C - Run with AI validation:
   pytest tests/integration/test_ai_validation_suggestions.py -v -s

4. VIEW REPORTS
   - HTML Report: pytest tests/ --html=reports/report.html
   - Allure Report: 
     pytest tests/ --alluredir=allure-results
     allure serve allure-results

5. EXPLORE EXAMPLES
   - tests/examples/test_e2e_with_ai_validation.py - Complete E2E example
   - examples/ai_validation_quick_reference.py - AI validation patterns
   - tests/ui/test_modern_spa.py - Playwright examples
   - tests/ui/test_legacy_ui.py - Selenium examples

6. READ DOCUMENTATION
   - docs/getting_started.md - Getting started guide
   - docs/architecture.md - Architecture overview
   - docs/ai_validation_suggestions.md - AI validation guide
   - README.md - Project overview

7. COMMON COMMANDS

   # Run all tests
   pytest
   
   # Run specific markers
   pytest -m smoke
   pytest -m integration
   
   # Run with parallel execution
   pytest -n 4
   
   # Run with detailed output
   pytest -v -s
   
   # Run specific test file
   pytest tests/integration/test_ui_api_db_flow.py
   
   # Generate HTML report
   pytest --html=reports/report.html --self-contained-html

8. NEXT STEPS
   
   ✓ Write your first test following the examples
   ✓ Configure API → DB mappings in config/api_db_mapping.yaml
   ✓ Customize engine selection rules in config/engine_decision_matrix.yaml
   ✓ Set up CI/CD using .github/workflows/test_execution.yml

NEED HELP?
- Check INSTALLATION_COMPLETE.md for detailed information
- Review docs/ folder for comprehensive guides
- Run: python verify_installation.py to check setup
"""
    
    print(guide)


def check_prerequisites():
    """Check if prerequisites are met"""
    print("\n" + "=" * 80)
    print("CHECKING PREREQUISITES")
    print("=" * 80)
    
    checks = []
    
    # Check Python packages
    try:
        import pytest
        print("✓ pytest installed")
        checks.append(True)
    except ImportError:
        print("✗ pytest not installed")
        checks.append(False)
    
    try:
        import playwright
        print("✓ playwright installed")
        checks.append(True)
    except ImportError:
        print("✗ playwright not installed")
        checks.append(False)
    
    try:
        import selenium
        print("✓ selenium installed")
        checks.append(True)
    except ImportError:
        print("✗ selenium not installed")
        checks.append(False)
    
    # Check framework structure
    required_dirs = ['framework', 'config', 'tests', 'docs']
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✓ {dir_name}/ directory exists")
            checks.append(True)
        else:
            print(f"✗ {dir_name}/ directory missing")
            checks.append(False)
    
    return all(checks)


def main():
    """Main setup function"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "QUICK START - FIRST TIME SETUP" + " " * 28 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n✗ Prerequisites not met. Please run:")
        print("  pip install -r requirements.txt")
        print("  python -m playwright install")
        return 1
    
    print("\n✓ All prerequisites met!")
    
    # Create .env file
    print("\n")
    create_response = input("Create .env file? (Y/n): ").strip().lower()
    if create_response != 'n':
        create_env_file()
    
    # Show guide
    show_quick_start_guide()
    
    print("\n" + "=" * 80)
    print("✅ SETUP COMPLETE - You're ready to start testing!")
    print("=" * 80)
    print()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
