"""
Verification script for Interactive CLI V2.1 - Flow Order Update
Ensures the execution flow matches the required order:
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

import sys
from pathlib import Path
import inspect

# Add framework to path
workspace_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(workspace_root))

def test_flow_order():
    """Test that the flow order is correct"""
    print("✓ Testing Interactive CLI Flow Order...\n")
    
    try:
        from framework.cli.interactive import InteractiveLauncher
        
        launcher = InteractiveLauncher()
        
        # Get the run method source code
        run_method = inspect.getsource(launcher.run)
        
        # Define expected steps in order
        expected_steps = [
            ("Step 1: Select Project", "select_project"),
            ("Step 2: Select Environment", "select_environment"),
            ("Step 3: Select Test Suite", "select_test_suite"),
            ("Step 4: Select Specific Tests", "select_specific_test"),
            ("Step 5: Select Browser Configuration", "select_browser_config"),
            ("Step 6: Select Execution Options", "select_execution_options"),
            ("Step 7: Select Human Behavior", "select_human_behavior"),
            ("Step 8: Select Report Options", "select_report_options"),
            ("Step 9: Validate", "validate_configuration"),
            ("Step 10: Show Summary", "show_execution_summary"),
            ("Step 11: Confirm", "Ready to execute tests?"),  # More specific
            ("Step 12: Execute", "execute_tests"),
            ("Step 13: Post-Processing", "post_process_results"),
        ]
        
        # Check docstring has correct flow
        run_docstring = launcher.run.__doc__
        if run_docstring:
            print("📝 Run Method Docstring:")
            print(run_docstring)
            print()
            
            # Verify docstring contains all 13 steps
            for step_num in range(1, 14):
                if f"{step_num}." in run_docstring:
                    print(f"  ✅ Step {step_num} documented")
                else:
                    print(f"  ❌ Step {step_num} NOT documented")
                    return False
        
        print("\n🔍 Verifying Method Calls in Flow...\n")
        
        # Find positions of each method call in the source
        positions = []
        for step_name, method_name in expected_steps:
            if method_name in run_method:
                pos = run_method.find(method_name)
                positions.append((step_name, method_name, pos))
                print(f"  ✅ Found: {step_name} ({method_name})")
            else:
                print(f"  ❌ Missing: {step_name} ({method_name})")
                return False
        
        print("\n📊 Verifying Order...\n")
        
        # Check if positions are in ascending order
        prev_pos = -1
        for step_name, method_name, pos in positions:
            if pos > prev_pos:
                print(f"  ✅ {step_name} is in correct position")
                prev_pos = pos
            else:
                print(f"  ❌ {step_name} is out of order!")
                return False
        
        # Verify specific order requirements
        print("\n🎯 Verifying Specific Order Requirements...\n")
        
        # Environment should come before Suite
        env_pos = next((p for n, m, p in positions if m == "select_environment"), None)
        suite_pos = next((p for n, m, p in positions if m == "select_test_suite"), None)
        
        if env_pos and suite_pos:
            if env_pos < suite_pos:
                print("  ✅ Environment selection comes before Suite (correct)")
            else:
                print("  ❌ Environment selection should come before Suite")
                return False
        
        # Execution Options should come before Human Behavior
        exec_pos = next((p for n, m, p in positions if m == "select_execution_options"), None)
        human_pos = next((p for n, m, p in positions if m == "select_human_behavior"), None)
        
        if exec_pos and human_pos:
            if exec_pos < human_pos:
                print("  ✅ Execution Options comes before Human Behavior (correct)")
            else:
                print("  ❌ Execution Options should come before Human Behavior")
                return False
        
        # Validate should come before Show Summary
        validate_pos = next((p for n, m, p in positions if m == "validate_configuration"), None)
        summary_pos = next((p for n, m, p in positions if m == "show_execution_summary"), None)
        
        if validate_pos and summary_pos:
            if validate_pos < summary_pos:
                print("  ✅ Validate comes before Show Summary (correct)")
            else:
                print("  ❌ Validate should come before Show Summary")
                return False
        
        # Post-processing should come after Execute
        execute_pos = next((p for n, m, p in positions if m == "execute_tests"), None)
        post_pos = next((p for n, m, p in positions if m == "post_process_results"), None)
        
        if execute_pos and post_pos:
            if post_pos > execute_pos:
                print("  ✅ Post-Processing comes after Execute (correct)")
            else:
                print("  ❌ Post-Processing should come after Execute")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Flow order test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_new_methods_exist():
    """Test that validate and post-process methods exist"""
    print("\n✓ Testing New Methods Exist...\n")
    
    try:
        from framework.cli.interactive import InteractiveLauncher
        
        launcher = InteractiveLauncher()
        
        # Check validate_configuration exists
        if hasattr(launcher, 'validate_configuration'):
            print("  ✅ validate_configuration() method exists")
            
            # Check signature
            sig = inspect.signature(launcher.validate_configuration)
            params = list(sig.parameters.keys())
            if 'config' in params and 'test_suite' in params and 'test_file' in params:
                print("     Parameters: config, test_suite, test_file ✅")
            else:
                print("     ❌ Wrong parameters")
                return False
        else:
            print("  ❌ validate_configuration() method NOT found")
            return False
        
        # Check post_process_results exists
        if hasattr(launcher, 'post_process_results'):
            print("  ✅ post_process_results() method exists")
            
            # Check signature
            sig = inspect.signature(launcher.post_process_results)
            params = list(sig.parameters.keys())
            if 'exit_code' in params and 'config' in params:
                print("     Parameters: exit_code, config ✅")
            else:
                print("     ❌ Wrong parameters")
                return False
        else:
            print("  ❌ post_process_results() method NOT found")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Method existence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 80)
    print("INTERACTIVE CLI V2.1 VERIFICATION - FLOW ORDER UPDATE")
    print("=" * 80)
    print()
    print("Expected Flow:")
    print("  1. Project")
    print("  2. Environment (moved earlier)")
    print("  3. Suite")
    print("  4. Specific Tests")
    print("  5. Browser Config")
    print("  6. Execution Options")
    print("  7. Human Behavior")
    print("  8. Report Options")
    print("  9. Validate (new)")
    print("  10. Show Summary")
    print("  11. Confirm")
    print("  12. Execute")
    print("  13. Post-Processing (new)")
    print()
    print("=" * 80)
    print()
    
    tests = [
        ("New Methods Exist", test_new_methods_exist),
        ("Flow Order Correct", test_flow_order),
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
        print("\n🎉 All tests passed! Flow order is correct!")
        print("\n📝 Changes Verified:")
        print("   • Environment moved to step 2 (after Project)")
        print("   • Execution Options moved before Human Behavior")
        print("   • Validation step added (step 9)")
        print("   • Post-Processing step added (step 13)")
        print("\n✨ The new flow is:")
        print("   Project → Environment → Suite → Tests →")
        print("   Browser → Execution → Human Behavior → Reports →")
        print("   Validate → Summary → Confirm → Execute → Post-Process")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
