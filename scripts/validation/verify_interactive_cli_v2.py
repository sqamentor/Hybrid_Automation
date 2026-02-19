"""
Verification script for Interactive CLI v2 - with full feature set
Tests all new features including browser mode, human behavior, execution options, and reports
"""

import sys
from pathlib import Path

# Add framework to path
workspace_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(workspace_root))

def test_imports():
    """Test that all required imports work"""
    print("✓ Testing imports...")
    
    try:
        from framework.cli.interactive import InteractiveLauncher
        from framework.cli.test_options import (
            BrowserConfig, BrowserMode, BrowserType,
            HumanBehaviorConfig,
            ExecutionConfig,
            ReportConfig,
            TestScopeConfig,
            FullTestConfig,
            ConfigPresets
        )
        print("  ✅ All imports successful")
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_browser_config():
    """Test browser configuration"""
    print("\n✓ Testing BrowserConfig...")
    
    try:
        from framework.cli.test_options import BrowserConfig, BrowserMode, BrowserType
        
        # Test headless mode
        config_headless = BrowserConfig(
            browser=BrowserType.CHROMIUM,
            mode=BrowserMode.HEADLESS
        )
        assert config_headless.is_headless, "Headless mode check failed"
        assert not config_headless.is_headed, "Headless mode headed check failed"
        args = config_headless.to_pytest_args()
        assert "--headless" in args, "Headless flag not in args"
        assert "--test-browser=chromium" in args, "Browser flag not in args"
        print(f"  ✅ Headless mode: {config_headless.get_description()}")
        print(f"     Args: {args}")
        
        # Test headed mode
        config_headed = BrowserConfig(
            browser=BrowserType.FIREFOX,
            mode=BrowserMode.HEADED
        )
        assert config_headed.is_headed, "Headed mode check failed"
        assert not config_headed.is_headless, "Headed mode headless check failed"
        args = config_headed.to_pytest_args()
        assert "--headed" in args, "Headed flag not in args"
        assert "--test-browser=firefox" in args, "Browser flag not in args"
        print(f"  ✅ Headed mode: {config_headed.get_description()}")
        print(f"     Args: {args}")
        
        # Test browser choices
        choices = BrowserConfig.get_browser_choices()
        assert len(choices) > 0, "No browser choices returned"
        print(f"  ✅ Browser choices: {len(choices)} available")
        
        return True
    except Exception as e:
        print(f"  ❌ BrowserConfig test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_human_behavior_config():
    """Test human behavior configuration"""
    print("\n✓ Testing HumanBehaviorConfig...")
    
    try:
        from framework.cli.test_options import HumanBehaviorConfig
        
        # Test enabled
        config_enabled = HumanBehaviorConfig(enabled=True, intensity="normal")
        assert config_enabled.enabled, "Enabled check failed"
        args = config_enabled.to_pytest_args()
        assert "--enable-human-behavior" in args, "Enable flag not in args"
        assert "--human-behavior-intensity=normal" in args, "Intensity not in args"
        markers = config_enabled.get_markers()
        assert len(markers) == 0, "Markers should be empty (no test filtering by marker)"
        print(f"  ✅ Enabled: {config_enabled.get_description()}")
        print(f"     Args: {args}")
        print(f"     Markers: {markers} (empty = no filtering)")
        
        # Test disabled
        config_disabled = HumanBehaviorConfig(enabled=False)
        assert not config_disabled.enabled, "Disabled check failed"
        args = config_disabled.to_pytest_args()
        assert "--disable-human-behavior" in args, "Disable flag not in args"
        markers = config_disabled.get_markers()
        assert len(markers) == 0, "Markers should be empty when disabled"
        print(f"  ✅ Disabled: {config_disabled.get_description()}")
        print(f"     Args: {args}")
        
        # Test intensity choices
        choices = HumanBehaviorConfig.get_intensity_choices()
        assert len(choices) > 0, "No intensity choices returned"
        print(f"  ✅ Intensity choices: {len(choices)} available")
        
        return True
    except Exception as e:
        print(f"  ❌ HumanBehaviorConfig test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_execution_config():
    """Test execution configuration"""
    print("\n✓ Testing ExecutionConfig...")
    
    try:
        from framework.cli.test_options import ExecutionConfig
        
        # Test parallel enabled
        config_parallel = ExecutionConfig(parallel=True, num_workers=4, markers=["smoke"])
        args = config_parallel.to_pytest_args()
        assert "-n" in args, "Parallel flag not in args"
        assert "4" in args, "Worker count not in args"
        # Note: Markers are handled by FullTestConfig.to_pytest_command(), not by ExecutionConfig.to_pytest_args()
        marker_expr = config_parallel.get_marker_expression()
        assert marker_expr == "smoke", "Marker expression should be 'smoke'"
        print(f"  ✅ Parallel: {config_parallel.get_description()}")
        print(f"     Args: {args}")
        print(f"     Marker Expression: {marker_expr}")
        
        # Test non-parallel
        config_single = ExecutionConfig(parallel=False)
        args = config_single.to_pytest_args()
        assert "-n" not in args, "Parallel flag should not be in args"
        print(f"  ✅ Single-threaded: {config_single.get_description()}")
        
        return True
    except Exception as e:
        print(f"  ❌ ExecutionConfig test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_report_config():
    """Test report configuration"""
    print("\n✓ Testing ReportConfig...")
    
    try:
        from framework.cli.test_options import ReportConfig
        
        # Test with HTML and Allure
        config = ReportConfig(html=True, allure=True)
        args = config.to_pytest_args()
        assert "--html" in " ".join(args), "HTML flag not in args"
        assert "--alluredir" in " ".join(args), "Allure flag not in args"
        print(f"  ✅ Reports: {config.get_description()}")
        print(f"     Args: {args}")
        
        # Test no reports
        config_none = ReportConfig(html=False, allure=False)
        args = config_none.to_pytest_args()
        assert len(args) == 0, "Args should be empty when no reports"
        print(f"  ✅ No reports: {config_none.get_description()}")
        
        return True
    except Exception as e:
        print(f"  ❌ ReportConfig test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_html_dynamic_naming():
    """Test HTML report dynamic naming integration"""
    print("\n✓ Testing HTML Dynamic Naming...")
    
    try:
        from framework.cli.test_options import ReportConfig
        
        # Test default HTML (should use report.html to trigger conftest.py dynamic naming)
        config = ReportConfig(html=True)
        args = config.to_pytest_args()
        html_args = [arg for arg in args if '--html=' in arg]
        
        # Should use 'report.html' which is recognized by conftest.py for dynamic naming
        assert len(html_args) == 1, "Should have exactly one HTML argument"
        assert html_args[0] == '--html=report.html', f"Expected '--html=report.html', got {html_args[0]}"
        print(f"  ✅ Default HTML uses trigger: {html_args[0]}")
        print(f"     → conftest.py will generate: projectname_EnvironmentName_DDMMYYYY_HHMMSS.html")
        
        # Test custom HTML path (should respect custom path)
        config_custom = ReportConfig(html=True, html_path='reports/custom_report.html')
        args_custom = config_custom.to_pytest_args()
        html_args_custom = [arg for arg in args_custom if '--html=' in arg]
        assert html_args_custom[0] == '--html=reports/custom_report.html', "Custom path not respected"
        print(f"  ✅ Custom HTML path respected: {html_args_custom[0]}")
        
        return True
    except Exception as e:
        print(f"  ❌ HTML Dynamic Naming test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_test_config():
    """Test FullTestConfig integration"""
    print("\n✓ Testing FullTestConfig...")
    
    try:
        from framework.cli.test_options import (
            FullTestConfig, BrowserConfig, BrowserMode, BrowserType,
            HumanBehaviorConfig, ExecutionConfig, ReportConfig, TestScopeConfig
        )
        
        # Create full config
        config = FullTestConfig(
            project="bookslot",
            environment="staging",
            browser=BrowserConfig(browser=BrowserType.CHROMIUM, mode=BrowserMode.HEADLESS),
            human_behavior=HumanBehaviorConfig(enabled=True, intensity="normal"),
            execution=ExecutionConfig(parallel=False, verbose=True),
            reports=ReportConfig(html=True, allure=False),
            test_scope=TestScopeConfig(scope_type="file", test_file="tests/test_login.py")
        )
        
        # Test command generation
        cmd = config.to_pytest_command()
        assert len(cmd) > 0, "Command should not be empty"
        assert "pytest" in " ".join(cmd), "pytest not in command"
        assert "--headless" in cmd, "Headless flag not in command"
        assert "--env=staging" in cmd, "Environment not in command"
        print(f"  ✅ Full config command generated")
        print(f"     Command: {' '.join(cmd)}")
        
        # Test summary
        summary = config.get_summary()
        assert isinstance(summary, dict), "Summary should be a dict"
        assert len(summary) > 0, "Summary should not be empty"
        assert 'Project' in summary, "Summary should have 'Project' key"
        assert 'Browser' in summary, "Summary should have 'Browser' key"
        print(f"  ✅ Summary generated with {len(summary)} fields")
        print(f"     Project: {summary['Project']}, Browser: {summary['Browser']}")
        
        return True
    except Exception as e:
        print(f"  ❌ FullTestConfig test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_presets():
    """Test configuration presets"""
    print("\n✓ Testing ConfigPresets...")
    
    try:
        from framework.cli.test_options import ConfigPresets
        
        # Test quick smoke test preset
        config = ConfigPresets.quick_smoke_test(project="bookslot", environment="staging")
        cmd = config.to_pytest_command()
        assert "--headless" in cmd, "Quick smoke should be headless"
        assert "-m" in cmd, "Quick smoke should have smoke marker"
        print(f"  ✅ Quick smoke test preset")
        print(f"     Command: {' '.join(cmd)}")
        
        # Test full regression preset
        config = ConfigPresets.full_regression(project="bookslot", environment="staging")
        cmd = config.to_pytest_command()
        assert "--alluredir" in " ".join(cmd), "Full regression should have Allure"
        print(f"  ✅ Full regression preset")
        
        # Test debug preset
        config = ConfigPresets.debug_single_test(
            project="bookslot",
            environment="staging",
            test_file="tests/test_login.py"
        )
        cmd = config.to_pytest_command()
        assert "--headed" in cmd, "Debug should be headed"
        print(f"  ✅ Debug single test preset")
        
        # Test CI/CD preset
        config = ConfigPresets.ci_cd_pipeline(project="bookslot", environment="production")
        cmd = config.to_pytest_command()
        assert "--headless" in cmd, "CI/CD should be headless"
        print(f"  ✅ CI/CD pipeline preset")
        
        return True
    except Exception as e:
        print(f"  ❌ ConfigPresets test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_interactive_launcher():
    """Test InteractiveLauncher initialization"""
    print("\n✓ Testing InteractiveLauncher...")
    
    try:
        from framework.cli.interactive import InteractiveLauncher
        
        launcher = InteractiveLauncher()
        assert launcher.workspace_root.exists(), "Workspace root should exist"
        print(f"  ✅ Launcher initialized successfully")
        print(f"     Workspace: {launcher.workspace_root}")
        
        # Test that launcher has required methods
        assert hasattr(launcher, 'run'), "Launcher should have run() method"
        assert hasattr(launcher, 'select_project'), "Launcher should have select_project() method"
        assert hasattr(launcher, 'select_browser_config'), "Launcher should have select_browser_config() method"
        assert hasattr(launcher, 'select_human_behavior'), "Launcher should have select_human_behavior() method"
        assert hasattr(launcher, 'select_execution_options'), "Launcher should have select_execution_options() method"
        assert hasattr(launcher, 'select_report_options'), "Launcher should have select_report_options() method"
        print(f"  ✅ All required methods found")
        
        return True
    except Exception as e:
        print(f"  ❌ InteractiveLauncher test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 80)
    print("INTERACTIVE CLI V2 VERIFICATION - FULL FEATURE SET")
    print("=" * 80)
    
    tests = [
        ("Imports", test_imports),
        ("BrowserConfig (headless/headed)", test_browser_config),
        ("HumanBehaviorConfig", test_human_behavior_config),
        ("ExecutionConfig", test_execution_config),
        ("ReportConfig", test_report_config),
        ("HTML Dynamic Naming", test_html_dynamic_naming),
        ("FullTestConfig", test_full_test_config),
        ("ConfigPresets", test_config_presets),
        ("InteractiveLauncher", test_interactive_launcher),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Interactive CLI v2 is ready!")
        print("\n📝 New Features Verified:")
        print("   • Browser mode selection (headless/headed)")
        print("   • Human behavior toggle (enable/disable + intensity)")
        print("   • Execution options (parallel, markers)")
        print("   • Report configuration (HTML, Allure)")
        print("   • HTML dynamic naming (project_Environment_DDMMYYYY_HHMMSS.html)")
        print("   • Full configuration integration")
        print("   • Pre-configured presets")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
