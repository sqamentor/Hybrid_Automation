"""
Validation Script for Human Behavior Implementation

This script validates that the human behavior simulation module
has been properly integrated into the framework.

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
"""

import sys
import os
from pathlib import Path


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_status(check_name, passed, message=""):
    """Print check status"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {check_name}")
    if message:
        print(f"       {message}")


def validate_files():
    """Validate all required files exist"""
    print_header("FILE VALIDATION")
    
    required_files = [
        "config/human_behavior.yaml",
        "framework/core/utils/__init__.py",
        "framework/core/utils/human_actions.py",
        "docs/HUMAN_BEHAVIOR_GUIDE.md",
        "examples/human_behavior/example_01_basic_usage.py",
        "examples/human_behavior/example_02_form_filling.py",
        "examples/human_behavior/example_03_framework_integration.py",
        "examples/human_behavior/example_04_advanced_ecommerce.py",
        "examples/human_behavior/README.md",
        "HUMAN_BEHAVIOR_IMPLEMENTATION_SUMMARY.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        exists = Path(file_path).exists()
        print_status(f"File: {file_path}", exists)
        all_exist = all_exist and exists
    
    return all_exist


def validate_imports():
    """Validate module imports"""
    print_header("IMPORT VALIDATION")
    
    checks = []
    
    # Test 1: Import main module
    try:
        from framework.core.utils.human_actions import HumanBehaviorSimulator
        print_status("Import HumanBehaviorSimulator", True)
        checks.append(True)
    except Exception as e:
        print_status("Import HumanBehaviorSimulator", False, str(e))
        checks.append(False)
    
    # Test 2: Import config
    try:
        from framework.core.utils.human_actions import get_behavior_config
        print_status("Import get_behavior_config", True)
        checks.append(True)
    except Exception as e:
        print_status("Import get_behavior_config", False, str(e))
        checks.append(False)
    
    # Test 3: Import standalone functions
    try:
        from framework.core.utils.human_actions import (
            human_type, human_click, human_scroll_behavior,
            random_mouse_movement, simulate_idle
        )
        print_status("Import standalone functions", True)
        checks.append(True)
    except Exception as e:
        print_status("Import standalone functions", False, str(e))
        checks.append(False)
    
    # Test 4: Import from package
    try:
        from framework.core.utils import HumanBehaviorSimulator
        print_status("Import from package", True)
        checks.append(True)
    except Exception as e:
        print_status("Import from package", False, str(e))
        checks.append(False)
    
    return all(checks)


def validate_configuration():
    """Validate configuration loading"""
    print_header("CONFIGURATION VALIDATION")
    
    checks = []
    
    try:
        from framework.core.utils.human_actions import get_behavior_config
        
        # Test 1: Load config
        config = get_behavior_config()
        print_status("Load configuration", True)
        checks.append(True)
        
        # Test 2: Check enabled
        enabled = config.is_enabled()
        print_status("Check enabled status", True, f"Enabled: {enabled}")
        checks.append(True)
        
        # Test 3: Get typing config
        typing_config = config.get('typing')
        has_typing = typing_config is not None
        print_status("Get typing config", has_typing)
        checks.append(has_typing)
        
        # Test 4: Get mouse config
        mouse_config = config.get('mouse')
        has_mouse = mouse_config is not None
        print_status("Get mouse config", has_mouse)
        checks.append(has_mouse)
        
        # Test 5: Check category enabled
        typing_enabled = config.is_category_enabled('typing')
        print_status("Check category enabled", True, f"Typing: {typing_enabled}")
        checks.append(True)
        
    except Exception as e:
        print_status("Configuration validation", False, str(e))
        checks.append(False)
    
    return all(checks)


def validate_conftest():
    """Validate conftest.py integration"""
    print_header("CONFTEST.PY VALIDATION")
    
    checks = []
    
    try:
        with open("conftest.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check imports
        has_import = "from framework.core.utils.human_actions import" in content
        print_status("Has human_actions import", has_import)
        checks.append(has_import)
        
        # Check fixture
        has_fixture = "def human_behavior(request):" in content
        print_status("Has human_behavior fixture", has_fixture)
        checks.append(has_fixture)
        
        # Check CLI options
        has_enable_option = "--enable-human-behavior" in content
        print_status("Has --enable-human-behavior option", has_enable_option)
        checks.append(has_enable_option)
        
        has_disable_option = "--disable-human-behavior" in content
        print_status("Has --disable-human-behavior option", has_disable_option)
        checks.append(has_disable_option)
        
        has_intensity_option = "--human-behavior-intensity" in content
        print_status("Has --human-behavior-intensity option", has_intensity_option)
        checks.append(has_intensity_option)
        
    except Exception as e:
        print_status("Conftest validation", False, str(e))
        checks.append(False)
    
    return all(checks)


def validate_pytest_ini():
    """Validate pytest.ini markers"""
    print_header("PYTEST.INI VALIDATION")
    
    checks = []
    
    try:
        with open("pytest.ini", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check markers
        has_human_like = "human_like:" in content
        print_status("Has human_like marker", has_human_like)
        checks.append(has_human_like)
        
        has_no_behavior = "no_human_behavior:" in content
        print_status("Has no_human_behavior marker", has_no_behavior)
        checks.append(has_no_behavior)
        
    except Exception as e:
        print_status("pytest.ini validation", False, str(e))
        checks.append(False)
    
    return all(checks)


def validate_base_page():
    """Validate BasePage integration"""
    print_header("BASE PAGE VALIDATION")
    
    checks = []
    
    try:
        with open("framework/ui/base_page.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check import
        has_import = "from framework.core.utils.human_actions import" in content
        print_status("Has human_actions import", has_import)
        checks.append(has_import)
        
        # Check methods
        has_human_type = "def human_type(" in content
        print_status("Has human_type method", has_human_type)
        checks.append(has_human_type)
        
        has_human_click = "def human_click(" in content
        print_status("Has human_click method", has_human_click)
        checks.append(has_human_click)
        
        has_enable_method = "def enable_human_behavior(" in content
        print_status("Has enable_human_behavior method", has_enable_method)
        checks.append(has_enable_method)
        
    except Exception as e:
        print_status("BasePage validation", False, str(e))
        checks.append(False)
    
    return all(checks)


def validate_examples():
    """Validate examples are runnable"""
    print_header("EXAMPLES VALIDATION")
    
    examples_dir = Path("examples/human_behavior")
    
    if not examples_dir.exists():
        print_status("Examples directory", False, "Directory not found")
        return False
    
    example_files = list(examples_dir.glob("example_*.py"))
    
    if len(example_files) < 4:
        print_status("Example files count", False, f"Found {len(example_files)}, expected 4+")
        return False
    
    print_status("Example files count", True, f"Found {len(example_files)} examples")
    
    # Check each example has proper structure
    checks = []
    for example_file in example_files:
        try:
            with open(example_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_imports = "import" in content
            has_test = "def test_" in content or "def main" in content
            is_valid = has_imports and has_test
            
            print_status(f"  {example_file.name}", is_valid)
            checks.append(is_valid)
        except Exception as e:
            print_status(f"  {example_file.name}", False, str(e))
            checks.append(False)
    
    return all(checks)


def validate_documentation():
    """Validate documentation exists and is comprehensive"""
    print_header("DOCUMENTATION VALIDATION")
    
    checks = []
    
    # Main guide
    guide_path = Path("docs/HUMAN_BEHAVIOR_GUIDE.md")
    if guide_path.exists():
        size = guide_path.stat().st_size
        is_comprehensive = size > 10000  # At least 10KB
        print_status("HUMAN_BEHAVIOR_GUIDE.md", is_comprehensive, f"Size: {size} bytes")
        checks.append(is_comprehensive)
    else:
        print_status("HUMAN_BEHAVIOR_GUIDE.md", False, "Not found")
        checks.append(False)
    
    # Examples README
    examples_readme = Path("examples/human_behavior/README.md")
    if examples_readme.exists():
        print_status("Examples README.md", True)
        checks.append(True)
    else:
        print_status("Examples README.md", False, "Not found")
        checks.append(False)
    
    # Implementation summary
    summary_path = Path("HUMAN_BEHAVIOR_IMPLEMENTATION_SUMMARY.md")
    if summary_path.exists():
        size = summary_path.stat().st_size
        print_status("Implementation Summary", True, f"Size: {size} bytes")
        checks.append(True)
    else:
        print_status("Implementation Summary", False, "Not found")
        checks.append(False)
    
    return all(checks)


def main():
    """Main validation function"""
    print("\n" + "="*70)
    print("  HUMAN BEHAVIOR SIMULATION - VALIDATION SCRIPT")
    print("  Author: Lokendra Singh (qa.lokendra@gmail.com)")
    print("="*70)
    
    results = {}
    
    # Run all validations
    results['files'] = validate_files()
    results['imports'] = validate_imports()
    results['configuration'] = validate_configuration()
    results['conftest'] = validate_conftest()
    results['pytest_ini'] = validate_pytest_ini()
    results['base_page'] = validate_base_page()
    results['examples'] = validate_examples()
    results['documentation'] = validate_documentation()
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nTotal Checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    for category, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {category.upper()}")
    
    # Final result
    print("\n" + "="*70)
    if passed == total:
        print("  ✅ ALL VALIDATIONS PASSED!")
        print("  🎉 Human Behavior Simulation is ready to use!")
        print("="*70)
        print("\n📚 Next Steps:")
        print("  1. Run examples: pytest examples/human_behavior/ -v")
        print("  2. Read guide: docs/HUMAN_BEHAVIOR_GUIDE.md")
        print("  3. Add to tests: @pytest.mark.human_like")
        print("  4. Configure: config/human_behavior.yaml")
        return 0
    else:
        print("  ❌ SOME VALIDATIONS FAILED")
        print("  Please review the errors above and fix them.")
        print("="*70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
