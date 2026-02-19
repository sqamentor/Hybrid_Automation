"""
Test script to verify Interactive CLI functionality
This script tests the interactive CLI components without requiring user input
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_interactive_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing Interactive CLI Imports...")
    
    try:
        from framework.cli.interactive import InteractiveLauncher
        print("  ✅ InteractiveLauncher imported successfully")
        
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        print("  ✅ Rich components imported successfully")
        
        import questionary
        print("  ✅ Questionary imported successfully")
        
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_launcher_initialization():
    """Test that launcher can be initialized"""
    print("\n🧪 Testing Launcher Initialization...")
    
    try:
        from framework.cli.interactive import InteractiveLauncher
        
        launcher = InteractiveLauncher()
        print(f"  ✅ Launcher initialized")
        print(f"  📁 Workspace root: {launcher.workspace_root}")
        print(f"  📦 Projects loaded: {len(launcher.projects_config.get('projects', {}))}")
        
        return True
    except Exception as e:
        print(f"  ❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_project_detection():
    """Test project detection functionality"""
    print("\n🧪 Testing Project Detection...")
    
    try:
        from framework.cli.interactive import InteractiveLauncher
        
        launcher = InteractiveLauncher()
        projects = launcher.get_available_projects()
        
        print(f"  ✅ Found {len(projects)} projects")
        
        for project in projects:
            status = "✅" if project['has_tests'] else "⚠️"
            print(f"  {status} {project['name']}")
            print(f"     ID: {project['id']}")
            print(f"     Tests: {project['has_tests']}")
            print(f"     Pages: {project['has_pages']}")
            print(f"     Environments: {', '.join(project['environments'])}")
        
        return len(projects) > 0
    except Exception as e:
        print(f"  ❌ Project detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_test_suite_detection():
    """Test test suite detection for each project"""
    print("\n🧪 Testing Test Suite Detection...")
    
    try:
        from framework.cli.interactive import InteractiveLauncher
        
        launcher = InteractiveLauncher()
        projects = launcher.get_available_projects()
        
        for project in projects:
            print(f"\n  📦 Project: {project['name']}")
            test_suites = launcher.detect_test_suites(project['id'])
            
            if test_suites:
                print(f"     Found {len(test_suites)} test suites:")
                for suite in test_suites:
                    print(f"     {suite['name']}")
                    print(f"       Type: {suite['type']}")
                    print(f"       Count: {suite['count']} tests")
                    print(f"       Path: {suite['path']}")
            else:
                print(f"     ⚠️ No test suites found")
        
        return True
    except Exception as e:
        print(f"  ❌ Test suite detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cli_help():
    """Test CLI help display"""
    print("\n🧪 Testing CLI Help Display...")
    
    try:
        from framework.cli import print_help
        
        print("  📄 Displaying help:")
        print("  " + "="*70)
        print_help()
        print("  " + "="*70)
        
        return True
    except Exception as e:
        print(f"  ❌ Help display failed: {e}")
        return False


def test_workspace_detection():
    """Test workspace root detection"""
    print("\n🧪 Testing Workspace Detection...")
    
    try:
        from framework.cli.interactive import InteractiveLauncher
        
        launcher = InteractiveLauncher()
        workspace_root = launcher._find_workspace_root()
        
        print(f"  ✅ Workspace root: {workspace_root}")
        
        # Check for expected files
        expected_files = ['pyproject.toml', 'pytest.ini', 'conftest.py']
        for file in expected_files:
            file_path = workspace_root / file
            if file_path.exists():
                print(f"     ✅ Found: {file}")
            else:
                print(f"     ⚠️ Missing: {file}")
        
        return True
    except Exception as e:
        print(f"  ❌ Workspace detection failed: {e}")
        return False


def test_config_loading():
    """Test configuration loading"""
    print("\n🧪 Testing Configuration Loading...")
    
    try:
        from framework.cli.interactive import InteractiveLauncher
        
        launcher = InteractiveLauncher()
        config = launcher._load_projects_config()
        
        print(f"  ✅ Configuration loaded")
        print(f"  📦 Projects in config: {len(config.get('projects', {}))}")
        
        for project_id, project_config in config.get('projects', {}).items():
            print(f"\n     Project: {project_id}")
            print(f"       Name: {project_config.get('name', 'N/A')}")
            print(f"       Environments: {list(project_config.get('environments', {}).keys())}")
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests"""
    print("\n" + "="*80)
    print("🚀 INTERACTIVE CLI - VERIFICATION TEST SUITE")
    print("="*80 + "\n")
    
    tests = [
        ("Imports", test_interactive_imports),
        ("Launcher Init", test_launcher_initialization),
        ("Project Detection", test_project_detection),
        ("Test Suite Detection", test_test_suite_detection),
        ("Workspace Detection", test_workspace_detection),
        ("Config Loading", test_config_loading),
        ("CLI Help", test_cli_help),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    print("\n" + "-"*80)
    print(f"  Total: {passed}/{total} tests passed")
    print("-"*80 + "\n")
    
    if passed == total:
        print("🎉 All tests passed! Interactive CLI is ready to use.")
        print("\n💡 To launch interactive mode, run:")
        print("   automation")
        print("\n📚 See documentation:")
        print("   Framework-Knowledge-Center/10-Rules-And-Standards/INTERACTIVE_CLI_GUIDE.md")
        return 0
    else:
        print("⚠️ Some tests failed. Please fix issues before using interactive mode.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
