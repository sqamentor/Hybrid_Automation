"""
Recording CLI - Command Line Interface for Test Recording Workflow
PROJECT-AWARE recording with automatic organization and environment detection
INTERACTIVE MODE with beautiful AI-powered interface

Author: Lokendra Singh
Email: lokendra.singh@centerforvein.com
Website: www.centerforvein.com
Assisted by: AI Claude (Anthropic)
"""

import sys
import argparse
from pathlib import Path
from loguru import logger
from typing import Optional, Dict, List, Tuple
import yaml
import os
from datetime import datetime

# Add project root to path (go up two levels from scripts/cli/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from framework.recording import RecordingWorkflow, PlaywrightCodegen, AIScriptRefactorer, PageObjectGenerator
from framework.core.project_manager import ProjectManager, get_project_manager


# ============================================================================
# INTERACTIVE CLI - BEAUTIFUL AI-POWERED INTERFACE
# ============================================================================

def print_header():
    """Print beautiful header"""
    print("\n" + "="*80)
    print("🎬  INTELLIGENT TEST RECORDING SYSTEM")
    print("="*80)
    print("✨ AI-Powered | 🎯 Project-Aware | 🚀 Production-Ready")
    print("="*80 + "\n")


def print_section(title: str, emoji: str = "📋"):
    """Print section header"""
    print(f"\n{emoji}  {title}")
    print("-" * 80)


def get_user_choice(prompt: str, options: List[str], show_details: bool = True) -> int:
    """Get user choice from list of options"""
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    
    while True:
        try:
            choice = input(f"\n👉 Enter your choice (1-{len(options)}): ").strip()
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                return choice_num
            else:
                print(f"❌ Invalid choice. Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\n👋 Recording cancelled by user.")
            sys.exit(0)


def get_text_input(prompt: str, default: str = None) -> str:
    """Get text input from user"""
    if default:
        full_prompt = f"\n👉 {prompt} [{default}]: "
    else:
        full_prompt = f"\n👉 {prompt}: "
    
    try:
        value = input(full_prompt).strip()
        return value if value else default
    except KeyboardInterrupt:
        print("\n\n👋 Recording cancelled by user.")
        sys.exit(0)


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Get yes/no confirmation"""
    default_str = "Y/n" if default else "y/N"
    try:
        response = input(f"\n👉 {prompt} [{default_str}]: ").strip().lower()
        if not response:
            return default
        return response in ['y', 'yes']
    except KeyboardInterrupt:
        print("\n\n👋 Recording cancelled by user.")
        sys.exit(0)


def interactive_recording():
    """
    Interactive recording mode with beautiful AI-powered interface
    Guides user through project selection, environment, options, and recording
    """
    print_header()
    
    pm = get_project_manager()
    
    # ========================================================================
    # STEP 1: PROJECT SELECTION
    # ========================================================================
    print_section("STEP 1: SELECT PROJECT", "🎯")
    
    projects = list(pm.projects.keys())
    project_display = []
    project_details = {}
    
    for proj_id in projects:
        config = pm.get_project_config(proj_id)
        display_name = config.get('name', proj_id.title())
        description = config.get('description', '')
        project_display.append(f"{display_name}")
        project_details[proj_id] = {
            'name': display_name,
            'description': description,
            'config': config
        }
    
    print("\n💡 Available Projects:")
    for i, (proj_id, details) in enumerate(zip(projects, project_details.values()), 1):
        print(f"\n  {i}. {details['name']}")
        print(f"     📝 {details['description']}")
    
    choice = get_user_choice("\n🎯 Which project do you want to record?", project_display)
    selected_project = projects[choice - 1]
    project_info = project_details[selected_project]
    
    print(f"\n✅ Selected: {project_info['name']}")
    
    # ========================================================================
    # STEP 2: ENVIRONMENT SELECTION
    # ========================================================================
    print_section("STEP 2: SELECT ENVIRONMENT", "🌍")
    
    environments = list(project_info['config'].get('environments', {}).keys())
    env_display = [env.upper() for env in environments]
    env_details = project_info['config'].get('environments', {})
    
    print("\n💡 Available Environments:")
    for i, env in enumerate(environments, 1):
        env_config = env_details[env]
        ui_url = env_config.get('ui_url', 'N/A') if isinstance(env_config, dict) else env_config
        print(f"\n  {i}. {env.upper()}")
        print(f"     🔗 {ui_url}")
    
    choice = get_user_choice("\n🌍 Which environment do you want to test?", env_display)
    selected_env = environments[choice - 1]
    env_url = env_details[selected_env]
    if isinstance(env_url, dict):
        env_url = env_url.get('ui_url', '')
    
    print(f"\n✅ Selected: {selected_env.upper()}")
    print(f"   🔗 URL: {env_url}")
    
    # ========================================================================
    # STEP 3: RECORDING NAME
    # ========================================================================
    print_section("STEP 3: NAME YOUR RECORDING", "📝")
    
    print("\n💡 Tips for naming:")
    print("   • Use descriptive names (e.g., login, book_appointment, search_patient)")
    print("   • Use underscores for spaces (e.g., create_new_booking)")
    print("   • Keep it concise and meaningful")
    
    recording_name = get_text_input("Enter recording name (e.g., login_flow)", "my_test")
    
    # Generate filename preview
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    preview_filename = f"test_{selected_project}_{recording_name}_{timestamp}.py"
    
    print(f"\n✅ Recording name: {recording_name}")
    print(f"   📄 Will be saved as: {preview_filename}")
    
    # ========================================================================
    # STEP 4: URL INPUT (Optional Override)
    # ========================================================================
    print_section("STEP 4: STARTING URL", "🔗")
    
    print(f"\n💡 Default URL: {env_url}")
    
    use_custom_url = get_yes_no("Do you want to use a different URL?", False)
    
    if use_custom_url:
        custom_url = get_text_input("Enter custom URL", env_url)
        final_url = custom_url
        print(f"\n✅ Using custom URL: {final_url}")
    else:
        final_url = env_url
        print(f"\n✅ Using default URL: {final_url}")
    
    # ========================================================================
    # STEP 5: RECORDING OPTIONS
    # ========================================================================
    print_section("STEP 5: RECORDING OPTIONS", "⚙️")
    
    print("\n💡 Configure your recording preferences:")
    
    # Browser selection
    print("\n🌐 Browser Options:")
    browsers = ["Chromium (Default - Fast & Reliable)", "Firefox (Alternative)", "WebKit (Safari-like)"]
    browser_choice = get_user_choice("Select browser", browsers)
    browser_map = {1: "chromium", 2: "firefox", 3: "webkit"}
    selected_browser = browser_map[browser_choice]
    
    # Mobile device
    use_mobile = get_yes_no("📱 Record on mobile device (iPhone 12)?", False)
    
    # AI refactoring
    print("\n✨ AI-Powered Features:")
    use_ai_refactor = get_yes_no("  🤖 Enable AI code refactoring (cleans & improves code)?", True)
    
    # Page object generation
    generate_page_obj = get_yes_no("  📦 Generate Page Object (reusable components)?", True)
    
    # Save authentication
    save_auth = get_yes_no("  🔐 Save authentication state (cookies/storage)?", False)
    
    print("\n✅ Options configured!")
    
    # ========================================================================
    # STEP 6: CONFIRMATION & SUMMARY
    # ========================================================================
    print_section("STEP 6: CONFIRM & START", "🚀")
    
    print("\n📋 RECORDING SUMMARY")
    print("=" * 80)
    print(f"  🎯 Project:        {project_info['name']}")
    print(f"  🌍 Environment:    {selected_env.upper()}")
    print(f"  📝 Test Name:      {recording_name}")
    print(f"  🔗 URL:            {final_url}")
    print(f"  🌐 Browser:        {selected_browser.title()}")
    print(f"  📱 Mobile:         {'Yes (iPhone 12)' if use_mobile else 'No (Desktop)'}")
    print(f"  🤖 AI Refactor:    {'Enabled ✨' if use_ai_refactor else 'Disabled'}")
    print(f"  📦 Page Object:    {'Yes 📄' if generate_page_obj else 'No'}")
    print(f"  🔐 Save Auth:      {'Yes 🔒' if save_auth else 'No'}")
    print(f"\n  💾 Save Location:")
    print(f"     Test:    recorded_tests/{selected_project}/{preview_filename}")
    print(f"     Page:    pages/{selected_project}/{recording_name}_page.py")
    print("=" * 80)
    
    print("\n💡 What will happen:")
    print("   1. 🌐 Playwright browser will open")
    print("   2. 👆 You perform your test actions (click, type, navigate)")
    print("   3. 💾 Recording saves automatically when you close browser")
    if use_ai_refactor:
        print("   4. ✨ AI will refactor and improve your code")
    if generate_page_obj:
        print("   5. 📦 Page object will be generated for reusability")
    print("   6. ✅ You're ready to run your test!")
    
    confirm = get_yes_no("\n🚀 Ready to start recording?", True)
    
    if not confirm:
        print("\n👋 Recording cancelled. No changes made.")
        return 0
    
    # ========================================================================
    # STEP 7: START RECORDING
    # ========================================================================
    print("\n" + "="*80)
    print("🎬  STARTING RECORDING...")
    print("="*80)
    print("\n⏳ Launching Playwright browser...")
    print("💡 TIP: Close the browser window when you're done recording\n")
    
    # Create workflow
    workflow = RecordingWorkflow()
    
    # Execute recording
    try:
        result = workflow.quick_workflow(
            url=final_url,
            test_name=recording_name,
            browser=selected_browser,
            mobile=use_mobile,
            auto_refactor=use_ai_refactor,
            generate_page_object=generate_page_obj,
            manual_project=selected_project,
            environment=selected_env
        )
        
        # ====================================================================
        # SUCCESS SUMMARY
        # ====================================================================
        if result.get("status") == "success":
            print("\n" + "="*80)
            print("✅  RECORDING COMPLETED SUCCESSFULLY!")
            print("="*80)
            
            print(f"\n📁 Your files:")
            if "steps" in result and "recording" in result["steps"]:
                rec_file = result["steps"]["recording"].get("output_file", "N/A")
                print(f"   📝 Test Script: {rec_file}")
            
            if "page_object_path" in result:
                print(f"   📦 Page Object: {result['page_object_path']}")
            
            print(f"\n🎯 Project: {result.get('project', 'N/A').upper()}")
            print(f"🌍 Environment: {result.get('environment', 'N/A').upper()}")
            
            print("\n✨ Next Steps:")
            print("   1. Review your recorded test file")
            print("   2. Run it: pytest <test_file_path>")
            print("   3. Customize if needed")
            print("   4. Integrate into your test suite")
            
            print("\n" + "="*80)
            print("🎉  Happy Testing!")
            print("="*80 + "\n")
            
            return 0
        else:
            print("\n" + "="*80)
            print("❌  RECORDING FAILED")
            print("="*80)
            print(f"\n⚠️  Status: {result.get('status', 'Unknown')}")
            if 'message' in result:
                print(f"📝 Message: {result['message']}")
            print()
            return 1
            
    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("⚠️   RECORDING INTERRUPTED")
        print("="*80)
        print("\n👋 Recording stopped by user. Partial files may have been saved.\n")
        return 1
    except Exception as e:
        print("\n" + "="*80)
        print("❌  ERROR OCCURRED")
        print("="*80)
        print(f"\n⚠️  {str(e)}\n")
        return 1


def cmd_record(args):
    """Record a new test"""
    codegen = PlaywrightCodegen()
    
    result = codegen.start_recording(
        url=args.url,
        test_name=args.name,
        browser=args.browser,
        device=args.device,
        capture_api=not args.no_api
    )
    
    if result.get("status") == "success":
        print(f"\n✓ Recording saved: {result['output_file']}")
        return 0
    else:
        print(f"\n✗ Recording failed: {result.get('message', 'Unknown error')}")
        return 1


def cmd_refactor(args):
    """Refactor a recorded script"""
    refactorer = AIScriptRefactorer(ai_provider_name=args.ai_provider)
    
    result = refactorer.refactor_script(
        script_path=args.script,
        improvements=args.improvements.split(',') if args.improvements else None
    )
    
    if result.get("status") == "success":
        print(f"\n✓ Refactored script: {result['refactored_file']}")
        print(f"  AI Used: {result['ai_used']}")
        print(f"  Improvements: {', '.join(result['improvements_applied'])}")
        return 0
    else:
        print(f"\n✗ Refactoring failed: {result.get('message', 'Unknown error')}")
        return 1


def cmd_generate_page(args):
    """Generate page object from script"""
    generator = PageObjectGenerator()
    
    result = generator.generate_from_script(
        script_path=args.script,
        page_name=args.page_name
    )
    
    if result.get("status") == "success":
        print(f"\n✓ Page Object generated: {result['page_class']}")
        print(f"  File: {result['page_file']}")
        print(f"  Locators: {result['locators_count']}")
        print(f"  Actions: {result['actions_count']}")
        print(f"\n{result['usage_example']}")
        return 0
    else:
        print(f"\n✗ Generation failed: {result.get('message', 'Unknown error')}")
        return 1


def cmd_workflow(args):
    """Run complete workflow with PROJECT AWARENESS"""
    workflow = RecordingWorkflow(ai_provider=args.ai_provider)
    
    if args.quick:
        result = workflow.quick_workflow(
            url=args.url,
            test_name=args.name,
            browser=args.browser,
            mobile=args.mobile,
            auto_refactor=not args.no_refactor,
            generate_page_object=not args.no_page,
            manual_project=args.project,  # NEW: Manual project override
            environment=args.environment   # NEW: Manual environment override
        )
    else:
        result = workflow.full_workflow(
            url=args.url,
            test_name=args.name,
            browser=args.browser,
            device=args.device,
            save_auth=args.save_auth,
            manual_project=args.project,   # NEW: Manual project override
            environment=args.environment    # NEW: Manual environment override
        )
    
    if result.get("status") == "success":
        print("\n✓ Workflow completed successfully!")
        print(f"  Project: {result.get('project', 'N/A')}")
        print(f"  Environment: {result.get('environment', 'N/A')}")
        return 0
    else:
        print(f"\n✗ Workflow failed at: {result.get('status', 'unknown')}")
        return 1


def cmd_list(args):
    """List recorded tests and page objects"""
    workflow = RecordingWorkflow()
    
    if args.type == "recordings" or args.type == "all":
        recordings = workflow.list_recordings()
        print(f"\n📹 Recorded Tests ({len(recordings)}):")
        for rec in recordings:
            print(f"  - {rec['name']}")
            print(f"    Path: {rec['path']}")
            print(f"    Size: {rec['size']} bytes")
    
    if args.type == "pages" or args.type == "all":
        pages = workflow.list_page_objects()
        print(f"\n📄 Page Objects ({len(pages)}):")
        for page in pages:
            print(f"  - {page['name']}")
            print(f"    Path: {page['path']}")
            print(f"    Size: {page['size']} bytes")
    
    return 0


def cmd_list_projects(args):
    """List all available projects"""
    pm = get_project_manager()
    
    print("\n🎯 AVAILABLE PROJECTS\n" + "="*80)
    
    for project_name, project_config in pm.projects.items():
        print(f"\n📁 {project_name.upper()}")
        print(f"  Name: {project_config.get('name', project_name)}")
        print(f"  Description: {project_config.get('description', 'No description')}")
        
        # URL Patterns
        patterns = project_config.get('url_patterns', [])
        print(f"  URL Patterns: {', '.join(patterns)}")
        
        # Environments
        envs = project_config.get('environments', {})
        print(f"  Environments:")
        for env_name, env_url in envs.items():
            print(f"    - {env_name}: {env_url}")
        
        # Paths
        paths = project_config.get('paths', {})
        print(f"  Directories:")
        for path_type, path_value in paths.items():
            print(f"    - {path_type}: {path_value}")
    
    print("\n" + "="*80)
    print(f"Total projects: {len(pm.projects)}\n")
    
    return 0


def cmd_project_info(args):
    """Show detailed project information"""
    pm = get_project_manager()
    
    try:
        # Detect from URL if provided
        if args.url:
            project_info = pm.get_project_info(url=args.url)
            project_name = project_info["project"]
        else:
            project_name = args.project
        
        config = pm.get_project_config(project_name)
        paths = pm.get_project_paths(project_name)
        
        print(f"\n🎯 PROJECT: {project_name.upper()}\n" + "="*80)
        print(f"Name: {config.get('name', project_name)}")
        print(f"Description: {config.get('description', 'No description')}")
        
        print(f"\n📌 URL PATTERNS:")
        for pattern in config.get('url_patterns', []):
            print(f"  - {pattern}")
        
        print(f"\n🌍 ENVIRONMENTS:")
        for env_name, env_url in config.get('environments', {}).items():
            print(f"  {env_name}: {env_url}")
        
        print(f"\n📁 DIRECTORIES:")
        for path_name, path_obj in paths.items():
            exists = path_obj.exists()
            status = "✓" if exists else "✗"
            print(f"  {status} {path_name}: {path_obj}")
        
        print(f"\n⚙️  SETTINGS:")
        settings = config.get('settings', {})
        for key, value in settings.items():
            print(f"  {key}: {value}")
        
        print("\n" + "="*80 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        return 1


def cmd_add_project(args):
    """Add a new project to the registry"""
    pm = get_project_manager()
    
    try:
        # Prepare environments (convert simple URLs to dictionaries with ui_url and api_url)
        environments = {}
        if args.dev_url:
            environments['dev'] = {
                'ui_url': args.dev_url,
                'api_url': args.dev_url.replace('://', '://api-').replace('://', '://api.')  # Simple API URL generation
            }
        if args.staging_url:
            environments['staging'] = {
                'ui_url': args.staging_url,
                'api_url': args.staging_url.replace('://', '://api-').replace('://', '://api.')
            }
        if args.prod_url:
            environments['prod'] = {
                'ui_url': args.prod_url,
                'api_url': args.prod_url.replace('://', '://api-').replace('://', '://api.')
            }
        
        # Register the project
        pm.register_new_project(
            project_name=args.project,
            full_name=args.name or args.project.title(),
            description=args.description or f"{args.name or args.project} project",
            url_patterns=args.patterns.split(',') if args.patterns else [f"{args.project}.*"],
            environments=environments,
            team=args.team or "Team",
            contact=args.contact or "team@example.com"
        )
        
        print(f"\n✓ Project '{args.project}' added successfully!")
        print(f"  URL Patterns: {args.patterns or f'{args.project}.*'}")
        print(f"  Environments: {', '.join(environments.keys())}")
        
        # Create directory structure
        if not args.no_create_dirs:
            pm.create_project_structure(args.project)
            print(f"  Directories created: recorded_tests/{args.project}/, pages/{args.project}/")
        
        print()
        return 0
        
    except Exception as e:
        print(f"\n✗ Error adding project: {e}\n")
        return 1


def cmd_detect_project(args):
    """Detect project from URL"""
    pm = get_project_manager()
    
    try:
        project_info = pm.get_project_info(
            url=args.url,
            manual_project=args.project,
            environment=args.environment
        )
        
        print(f"\n🎯 PROJECT DETECTION RESULTS\n" + "="*80)
        print(f"  URL: {args.url}")
        print(f"  Detected Project: {project_info['project'].upper()}")
        print(f"  Environment: {project_info['environment'].upper()}")
        print(f"  Detection Method: {'Manual' if args.project else 'Automatic'}")
        
        print(f"\n📁 TARGET DIRECTORIES:")
        for path_name, path_obj in project_info['paths'].items():
            print(f"  {path_name}: {path_obj}")
        
        print("\n" + "="*80 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Detection failed: {e}\n")
        return 1


def main():
    """Main CLI entry point with INTERACTIVE MODE"""
    
    # ========================================================================
    # INTERACTIVE MODE - When run without arguments
    # ========================================================================
    if len(sys.argv) == 1:
        # No arguments provided - launch interactive mode
        return interactive_recording()
    
    # ========================================================================
    # COMMAND-LINE MODE - When run with arguments
    # ========================================================================
    parser = argparse.ArgumentParser(
        description="🎬 Test Recording Workflow CLI - PROJECT-AWARE & INTERACTIVE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎯 INTERACTIVE MODE (Recommended for beginners):
  python record_cli.py
  
  Simply run without arguments to launch the guided interactive interface!
  It will walk you through:
    1. Project selection (BookSlots, CallCenter, PatientIntake)
    2. Environment selection (Staging, Production)
    3. Recording configuration (name, URL, browser, options)
    4. Confirmation and start recording

📋 COMMAND-LINE MODE Examples:
  # Quick recording (auto-detect project from URL)
  python record_cli.py workflow --url https://bookslot.example.com/login --name login_test --quick
  
  # Record with manual project override
  python record_cli.py workflow --url https://example.com --name test --project bookslot --quick
  
  # List all available projects
  python record_cli.py list-projects
  
  # Show project details
  python record_cli.py project-info --project bookslot
  
  # Detect project from URL
  python record_cli.py detect-project --url https://bookslot-staging.example.com
  
  # Add a new project
  python record_cli.py add-project --project myproject --name "My Project" \\
    --patterns "myproject.*,.*myproject.*" --staging-url https://staging.myproject.com
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Record command
    record_parser = subparsers.add_parser('record', help='Record a new test')
    record_parser.add_argument('--url', required=True, help='Starting URL')
    record_parser.add_argument('--name', required=True, help='Test name')
    record_parser.add_argument('--browser', default='chromium', choices=['chromium', 'firefox', 'webkit'], help='Browser')
    record_parser.add_argument('--device', help='Device to emulate (e.g., "iPhone 12")')
    record_parser.add_argument('--no-api', action='store_true', help='Disable API capture')
    record_parser.set_defaults(func=cmd_record)
    
    # Refactor command
    refactor_parser = subparsers.add_parser('refactor', help='Refactor a script')
    refactor_parser.add_argument('--script', required=True, help='Script path')
    refactor_parser.add_argument('--ai-provider', choices=['openai', 'claude', 'azure', 'ollama'], help='AI provider')
    refactor_parser.add_argument('--improvements', help='Comma-separated improvements (comments,locators,assertions,documentation)')
    refactor_parser.set_defaults(func=cmd_refactor)
    
    # Generate page command
    generate_parser = subparsers.add_parser('generate-page', help='Generate page object')
    generate_parser.add_argument('--script', required=True, help='Script path')
    generate_parser.add_argument('--page-name', help='Page object class name')
    generate_parser.set_defaults(func=cmd_generate_page)
    
    # Workflow command
    workflow_parser = subparsers.add_parser('workflow', help='Run complete workflow')
    workflow_parser.add_argument('--url', required=True, help='Starting URL')
    workflow_parser.add_argument('--name', required=True, help='Test name')
    workflow_parser.add_argument('--browser', default='chromium', choices=['chromium', 'firefox', 'webkit'], help='Browser')
    workflow_parser.add_argument('--device', help='Device to emulate')
    workflow_parser.add_argument('--ai-provider', choices=['openai', 'claude', 'azure', 'ollama'], help='AI provider')
    workflow_parser.add_argument('--quick', action='store_true', help='Quick workflow mode')
    workflow_parser.add_argument('--mobile', action='store_true', help='Use mobile device (iPhone 12)')
    workflow_parser.add_argument('--save-auth', action='store_true', help='Save authentication state')
    workflow_parser.add_argument('--no-refactor', action='store_true', help='Skip refactoring')
    workflow_parser.add_argument('--no-page', action='store_true', help='Skip page object generation')
    workflow_parser.add_argument('--project', help='Manual project override (auto-detect if not specified)')
    workflow_parser.add_argument('--environment', choices=['staging', 'prod'], help='Environment override (staging or prod only)')
    workflow_parser.set_defaults(func=cmd_workflow)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List recordings and page objects')
    list_parser.add_argument('--type', default='all', choices=['recordings', 'pages', 'all'], help='What to list')
    list_parser.set_defaults(func=cmd_list)
    
    # List projects command (NEW)
    projects_parser = subparsers.add_parser('list-projects', help='List all available projects')
    projects_parser.set_defaults(func=cmd_list_projects)
    
    # Project info command (NEW)
    project_info_parser = subparsers.add_parser('project-info', help='Show project details')
    project_info_parser.add_argument('--project', help='Project name')
    project_info_parser.add_argument('--url', help='URL to detect project from')
    project_info_parser.set_defaults(func=cmd_project_info)
    
    # Add project command (NEW)
    add_project_parser = subparsers.add_parser('add-project', help='Add new project')
    add_project_parser.add_argument('--project', required=True, help='Project ID (e.g., bookslot)')
    add_project_parser.add_argument('--name', help='Display name')
    add_project_parser.add_argument('--description', help='Project description')
    add_project_parser.add_argument('--patterns', required=True, help='Comma-separated URL patterns (regex)')
    add_project_parser.add_argument('--dev-url', help='Development URL')
    add_project_parser.add_argument('--staging-url', help='Staging URL')
    add_project_parser.add_argument('--prod-url', help='Production URL')
    add_project_parser.add_argument('--team', help='Team name (default: Team)')
    add_project_parser.add_argument('--contact', help='Team contact (default: team@example.com)')
    add_project_parser.add_argument('--no-create-dirs', action='store_true', help='Do not create directories')
    add_project_parser.set_defaults(func=cmd_add_project)
    
    # Detect project command (NEW)
    detect_parser = subparsers.add_parser('detect-project', help='Detect project from URL')
    detect_parser.add_argument('--url', required=True, help='URL to analyze')
    detect_parser.add_argument('--project', help='Manual project override')
    detect_parser.add_argument('--environment', help='Manual environment override')
    detect_parser.set_defaults(func=cmd_detect_project)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    try:
        return args.func(args)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"\n✗ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
