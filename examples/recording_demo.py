"""
Example: Complete Recording Workflow Demo
==========================================

This example demonstrates the full 5-step recording workflow:
1. Record with Playwright Codegen
2. Human review (manual step)
3. AI-assisted refactoring
4. Page Object generation
5. API/DB orchestration integration

Run this to see the workflow in action!
"""

import sys
from pathlib import Path

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent))

from framework.recording import RecordingWorkflow


def demo_quick_workflow():
    """Demonstrate quick workflow (most common use case)"""
    print("\n" + "="*60)
    print("DEMO 1: Quick Workflow")
    print("="*60)
    
    workflow = RecordingWorkflow()
    
    # Quick workflow - all steps automated
    result = workflow.quick_workflow(
        url="https://playwright.dev",  # Example website
        test_name="playwright_demo",
        browser="chromium",
        mobile=False,
        auto_refactor=True,
        generate_page_object=True
    )
    
    print("\n✓ Quick Workflow Complete!")
    print(f"Status: {result['status']}")
    
    if result.get('summary'):
        print("\nSummary:")
        for step, status in result['summary'].items():
            icon = "✓" if status == "success" else "✗"
            print(f"  {icon} {step}: {status}")


def demo_full_workflow():
    """Demonstrate full workflow with all options"""
    print("\n" + "="*60)
    print("DEMO 2: Full Workflow with Custom Options")
    print("="*60)
    
    workflow = RecordingWorkflow(ai_provider="openai")
    
    # Full workflow with granular control
    result = workflow.full_workflow(
        url="https://playwright.dev/python",
        test_name="playwright_python_demo",
        browser="chromium",
        device="Desktop Chrome",  # Specific device
        save_auth=False,
        refactor_improvements=['comments', 'locators', 'assertions']
    )
    
    print("\n✓ Full Workflow Complete!")
    print(f"Status: {result['status']}")
    
    if result.get('files_created'):
        print("\nFiles Created:")
        for file in result['files_created']:
            print(f"  - {file}")


def demo_step_by_step():
    """Demonstrate step-by-step workflow for full control"""
    print("\n" + "="*60)
    print("DEMO 3: Step-by-Step Workflow (Advanced)")
    print("="*60)
    
    from framework.recording import (
        PlaywrightCodegen,
        AIScriptRefactorer,
        PageObjectGenerator
    )
    
    # Step 1: Record
    print("\nStep 1: Recording with Playwright Codegen...")
    codegen = PlaywrightCodegen()
    record_result = codegen.quick_record(
        url="https://playwright.dev",
        test_name="step_by_step_demo",
        mobile=False
    )
    
    if record_result['status'] == 'success':
        print(f"✓ Recording saved: {record_result['output_file']}")
        
        # Step 2: Human Review (simulated)
        print("\nStep 2: Human Review (manual step - skipped in demo)")
        
        # Step 3: AI Refactoring
        print("\nStep 3: AI-assisted refactoring...")
        refactorer = AIScriptRefactorer(ai_provider_name=None)  # Auto-detect
        refactor_result = refactorer.refactor_script(
            script_path=record_result['output_file']
        )
        
        if refactor_result['status'] == 'success':
            print(f"✓ Refactored: {refactor_result['refactored_file']}")
            print(f"  AI Used: {refactor_result['ai_used']}")
            
            # Step 4: Page Object Generation
            print("\nStep 4: Generating Page Object...")
            generator = PageObjectGenerator()
            page_result = generator.generate_from_script(
                script_path=refactor_result['refactored_file']
            )
            
            if page_result['status'] == 'success':
                print(f"✓ Page Object: {page_result['page_file']}")
                print(f"  Locators: {page_result['locators_count']}")
                print(f"  Actions: {page_result['actions_count']}")
                
                # Step 5: Integration Guidance
                print("\nStep 5: API/DB Integration (see RECORDING_GUIDE.md)")
                print("  → Use APIInterceptor for API capture")
                print("  → Use AIValidationSuggester for DB mapping")
                print("  → See complete examples in RECORDING_GUIDE.md")


def demo_python_api():
    """Demonstrate convenience Python API"""
    print("\n" + "="*60)
    print("DEMO 4: One-Line Python API")
    print("="*60)
    
    from framework.recording import quick_record_and_generate
    
    # One function call for complete workflow
    result = quick_record_and_generate(
        url="https://playwright.dev",
        test_name="one_line_demo",
        mobile=False
    )
    
    print("\n✓ One-Line Workflow Complete!")
    if result.get('status') == 'success':
        print(f"  Recorded: {result.get('recorded_file', 'N/A')}")
        print(f"  Refactored: {result.get('refactored_file', 'N/A')}")
        print(f"  Page Object: {result.get('page_object_file', 'N/A')}")


def demo_cli_commands():
    """Show CLI command examples"""
    print("\n" + "="*60)
    print("DEMO 5: CLI Commands Reference")
    print("="*60)
    
    print("\n📹 Recording Commands:\n")
    
    commands = [
        ("Quick Workflow", 
         "python record_cli.py workflow --url https://example.com --name test1 --quick"),
        
        ("Full Workflow", 
         "python record_cli.py workflow --url https://example.com --name test2 --browser chromium"),
        
        ("Mobile Recording", 
         "python record_cli.py workflow --url https://example.com --name mobile_test --quick --mobile"),
        
        ("Record Only", 
         "python record_cli.py record --url https://example.com --name record_only"),
        
        ("Refactor Existing", 
         "python record_cli.py refactor --script recorded_tests/test.py --ai-provider claude"),
        
        ("Generate Page Object", 
         "python record_cli.py generate-page --script recorded_tests/test_refactored.py"),
        
        ("List All", 
         "python record_cli.py list --type all"),
    ]
    
    for name, cmd in commands:
        print(f"{name}:")
        print(f"  {cmd}\n")


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print(" RECORDING WORKFLOW DEMONSTRATION")
    print("="*70)
    
    print("\nThis demo shows different ways to use the recording workflow:")
    print("  1. Quick Workflow (automated)")
    print("  2. Full Workflow (custom options)")
    print("  3. Step-by-Step (granular control)")
    print("  4. Python API (one-liner)")
    print("  5. CLI Commands (terminal usage)")
    
    print("\n⚠️  NOTE: This demo will open Playwright browsers for recording.")
    print("You'll need to interact with the browser to record actions.")
    print("Press Ctrl+C to stop recording when done.\n")
    
    choice = input("Run demos? (y/n): ").strip().lower()
    
    if choice == 'y':
        # Demo 1: Quick Workflow
        demo_quick_workflow()
        
        # Demo 2: Full Workflow
        demo_full_workflow()
        
        # Demo 3: Step-by-Step
        demo_step_by_step()
        
        # Demo 4: Python API
        demo_python_api()
        
        # Demo 5: CLI Commands (just shows commands, doesn't run)
        demo_cli_commands()
        
        print("\n" + "="*70)
        print("DEMOS COMPLETE!")
        print("="*70)
        print("\n📖 For detailed documentation, see: RECORDING_GUIDE.md")
        print("📹 Recorded tests are in: recorded_tests/")
        print("📄 Page Objects are in: pages/")
        print("\n🚀 Next Steps:")
        print("  1. Review recorded tests in recorded_tests/")
        print("  2. Check generated Page Objects in pages/")
        print("  3. Run tests: pytest recorded_tests/{test_name}_refactored.py")
        print("  4. Add API/DB validation (see RECORDING_GUIDE.md)")
    else:
        print("\nDemo cancelled. To run manually:")
        print("  python examples/recording_demo.py")
        print("\nOr use CLI directly:")
        print("  python record_cli.py workflow --url https://example.com --name my_test --quick")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
