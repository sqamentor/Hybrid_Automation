"""
Modern Unified CLI - Automation Framework Command-Line Interface
Single entry point with subcommands following industry standards

Usage:
    automation              - Interactive mode (user-friendly, guided experience)
    automation interactive  - Interactive mode (explicit)
    automation run          - Execute general tests (interactive or direct)
    automation run-pom      - Execute Page Object Model tests
    automation record       - Record test interactions
    automation simulate     - Simulate test scenarios

Follows modern automation patterns:
    ✓ Playwright: playwright test, playwright codegen
    ✓ Cypress: cypress run, cypress open
    ✓ Angular: ng serve, ng build
    ✓ This Framework: automation run, automation record

Author: Lokendra Singh
Email: lokendra.singh@centerforvein.com
Website: www.centerforvein.com
"""

import sys
from typing import List, Optional
import shutil
from pathlib import Path


def clear_python_cache():
    """Clear all Python __pycache__ directories"""
    try:
        import os
        cache_dirs_removed = 0
        for root, dirs, files in os.walk('.'):
            if '__pycache__' in dirs:
                cache_path = os.path.join(root, '__pycache__')
                try:
                    shutil.rmtree(cache_path)
                    cache_dirs_removed += 1
                except Exception:
                    pass  # Silent fail if cache is locked
        if cache_dirs_removed > 0:
            print(f"✅ Python cache cleared ({cache_dirs_removed} directories)")
    except Exception:
        pass  # Silent fail - don't block CLI startup


def print_banner():
    """Print unified CLI banner"""
    print("\n" + "="*80)
    print("🚀  AUTOMATION FRAMEWORK - Unified Command-Line Interface")
    print("="*80)
    print("📦 Modern • 🎯 Project-Aware • 🚀 Production-Ready • 🎨 Interactive")
    print("="*80 + "\n")


def print_help():
    """Print help message with all available commands"""
    print_banner()
    print("🎯 INTERACTIVE MODE (Recommended for all users!):")
    print()
    print("  automation              Launch interactive test launcher (guided, user-friendly)")
    print("  automation interactive  Launch interactive mode (explicit)")
    print()
    print("="*80)
    print()
    print("📋 Direct Commands (For advanced users and automation):")
    print()
    print("  run          Execute general test suite (interactive or direct)")
    print("               Example: automation run")
    print("               Example: automation run --path tests/test_login.py")
    print()
    print("  run-pom      Execute Page Object Model tests (project-aware)")
    print("               Example: automation run-pom")
    print("               Example: automation run-pom --project bookslot --env staging")
    print()
    print("  test         Shorthand for running project tests (modern pattern)")
    print("               Example: automation test bookslot --env staging")
    print("               Example: automation test --all")
    print()
    print("  record       Record test interactions with AI-powered generation")
    print("               Example: automation record")
    print("               Example: automation record --project bookslot")
    print()
    print("  simulate     Simulate test scenarios")
    print("               Example: automation simulate")
    print()
    print("  projects     Manage and discover projects (multi-project support)")
    print("               Example: automation projects list")
    print("               Example: automation projects info bookslot")
    print()
    print("  context      Show current workspace context and location")
    print("               Example: automation context")
    print()
    print("="*80)
    print()
    print("💡 TIP: Just type 'automation' for an easy, interactive experience!")
    print("   Perfect for non-technical users and quick test execution.")
    print()
    print("="*80)


def main(args: Optional[List[str]] = None):
    """
    Main entry point for unified CLI
    Routes to appropriate subcommand
    
    Default behavior (no args): Launch interactive mode
    """
    # Clear Python cache before running any command
    clear_python_cache()
    
    if args is None:
        args = sys.argv[1:]
    
    # No arguments - launch interactive mode by default
    if not args:
        try:
            from framework.cli.interactive import main as interactive_main
            return interactive_main([])
        except ImportError as e:
            print("\n⚠️  Interactive mode requires additional packages.")
            print("   Install with: pip install rich questionary")
            print("\n   Showing help instead...\n")
            print_help()
            return 1
    
    # Help requested
    if args[0] in ['-h', '--help', 'help']:
        print_help()
        return 0
    
    # Get command
    command = args[0]
    remaining_args = args[1:]
    
    try:
        if command == 'interactive' or command == 'i':
            # Explicit interactive mode
            from framework.cli.interactive import main as interactive_main
            return interactive_main(remaining_args)
        
        elif command == 'run':
            # Import and execute general test runner
            from framework.cli.run import main as run_main
            return run_main(remaining_args)
        
        elif command == 'run-pom':
            # Import and execute POM test runner
            from framework.cli.run_pom import main as run_pom_main
            return run_pom_main(remaining_args)
        
        elif command == 'test':
            # Modern shorthand for project-specific test execution
            # Maps to run-pom for POM-based projects
            from framework.cli.run_pom import main as run_pom_main
            return run_pom_main(remaining_args)
        
        elif command == 'record':
            # Import and execute recording CLI
            from framework.cli.record import main as record_main
            return record_main(remaining_args)
        
        elif command == 'simulate':
            # Import and execute simulation CLI
            from framework.cli.simulate import main as simulate_main
            return simulate_main(remaining_args)
        
        elif command == 'projects':
            # Import and execute projects management CLI
            from framework.cli.projects import main as projects_main
            return projects_main(remaining_args)
        
        elif command == 'context':
            # Show current workspace context
            from framework.cli.context import print_workspace_info
            print_workspace_info()
            return 0
        
        else:
            print(f"\n❌ Unknown command: {command}")
            print("\n💡 TIP: Just run 'automation' for interactive mode!")
            print("   Or run 'automation --help' to see all available commands")
            return 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        return 130
    
    except Exception as e:
        print(f"\n❌ Error executing command '{command}': {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
