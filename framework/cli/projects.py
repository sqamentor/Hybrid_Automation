"""
CLI Module - Project Management Commands
Modern multi-project CLI with project discovery and context awareness

Commands:
    automation projects list            - List all available projects
    automation projects info [name]     - Show detailed project information
    automation projects add             - Add a new project interactively
    automation projects detect [url]    - Detect project from URL

Author: Lokendra Singh
Email: lokendra.singh@centerforvein.com
Website: www.centerforvein.com
"""

import sys
from pathlib import Path
from typing import List, Optional
from framework.core.project_manager import get_project_manager, ProjectDetectionError


def print_banner():
    """Print projects CLI banner"""
    print("\n" + "="*80)
    print("📦 AUTOMATION FRAMEWORK - Project Management")
    print("="*80 + "\n")


def cmd_list(args: Optional[List[str]] = None):
    """List all available projects"""
    pm = get_project_manager()
    
    print_banner()
    print("📋 Available Projects:")
    print()
    
    projects = pm.get_available_projects()
    
    if not projects:
        print("  No projects configured.")
        return 0
    
    for project in projects:
        print(f"  📁 {project['name']}")
        print(f"     ID: {project['full_name']}")
        if project.get('description'):
            print(f"     Description: {project['description']}")
        if project.get('team'):
            print(f"     Team: {project['team']}")
        print()
    
    print(f"Total: {len(projects)} project(s)")
    print("="*80 + "\n")
    
    return 0


def cmd_info(args: Optional[List[str]] = None):
    """Show detailed information about a specific project"""
    pm = get_project_manager()
    
    # Parse project name
    if not args or len(args) == 0:
        print("\n❌ Error: Project name required")
        print("Usage: automation projects info <project-name>")
        print("\nAvailable projects:")
        for p in pm.get_available_projects():
            print(f"  - {p['name']}")
        return 1
    
    project_name = args[0]
    
    try:
        config = pm.get_project_config(project_name)
        paths = pm.get_project_paths(project_name)
        
        print_banner()
        print(f"📁 Project: {config.get('name', project_name)}")
        print("="*80)
        print()
        
        # Basic Info
        print("📝 Basic Information:")
        print(f"  ID: {project_name}")
        print(f"  Name: {config.get('name', 'N/A')}")
        print(f"  Description: {config.get('description', 'N/A')}")
        print(f"  Team: {config.get('team', 'N/A')}")
        print(f"  Contact: {config.get('contact', 'N/A')}")
        print()
        
        # URL Patterns
        print("🌐 URL Patterns (for auto-detection):")
        patterns = config.get('url_patterns', [])
        if patterns:
            for pattern in patterns:
                print(f"  - {pattern}")
        else:
            print("  (none)")
        print()
        
        # Environments
        print("🌍 Environments:")
        environments = config.get('environments', {})
        if environments:
            for env_name, env_config in environments.items():
                print(f"  {env_name}:")
                print(f"    UI URL: {env_config.get('ui_url', 'N/A')}")
                print(f"    API URL: {env_config.get('api_url', 'N/A')}")
        else:
            print("  (none)")
        print()
        
        # Paths
        print("📂 Directory Structure:")
        for path_type, path_obj in paths.items():
            exists = "✓" if path_obj.exists() else "✗"
            print(f"  {path_type}: {path_obj.relative_to(Path.cwd())} {exists}")
        print()
        
        # Settings
        print("⚙️  Settings:")
        settings = config.get('settings', {})
        if settings:
            for key, value in settings.items():
                print(f"  {key}: {value}")
        else:
            print("  (default settings)")
        print()
        
        print("="*80 + "\n")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        return 1


def cmd_detect(args: Optional[List[str]] = None):
    """Detect project from URL"""
    pm = get_project_manager()
    
    # Parse URL
    if not args or len(args) == 0:
        print("\n❌ Error: URL required")
        print("Usage: automation projects detect <url>")
        return 1
    
    url = args[0]
    
    try:
        project_info = pm.get_project_info(url=url)
        
        print_banner()
        print("🔍 Project Detection Results:")
        print("="*80)
        print()
        print(f"  URL: {url}")
        print(f"  Detected Project: {project_info['project']}")
        print(f"  Environment: {project_info['environment']}")
        print(f"  Full Name: {project_info['full_name']}")
        print()
        print("📂 Target Directories:")
        for path_name, path_obj in project_info['paths'].items():
            print(f"  {path_name}: {path_obj.relative_to(Path.cwd())}")
        print()
        print("="*80 + "\n")
        
        return 0
        
    except ProjectDetectionError as e:
        print(f"\n❌ Detection Failed: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        return 1


def cmd_add(args: Optional[List[str]] = None):
    """Add a new project interactively"""
    print_banner()
    print("🆕 Add New Project")
    print("="*80)
    print()
    print("This will guide you through adding a new project to the framework.")
    print()
    
    # TODO: Implement interactive project addition
    print("⚠️  Interactive project addition coming soon!")
    print()
    print("For now, manually edit: config/projects.yaml")
    print()
    print("Required fields:")
    print("  - name: Full project name")
    print("  - description: Project description")
    print("  - url_patterns: List of URL patterns for detection")
    print("  - environments: staging and production URLs")
    print("  - paths: pages, recorded_tests, test_data")
    print()
    
    return 0


def print_help():
    """Print projects subcommand help"""
    print_banner()
    print("Available Commands:")
    print()
    print("  list         List all available projects")
    print("               Example: automation projects list")
    print()
    print("  info         Show detailed project information")
    print("               Example: automation projects info bookslot")
    print()
    print("  detect       Detect project from URL")
    print("               Example: automation projects detect https://bookslot.example.com")
    print()
    print("  add          Add a new project interactively")
    print("               Example: automation projects add")
    print()
    print("="*80 + "\n")


def main(args: Optional[List[str]] = None):
    """
    Main entry point for projects subcommand
    Routes to appropriate project command
    """
    if args is None:
        args = sys.argv[1:]
    
    # No arguments or help requested
    if not args or args[0] in ['-h', '--help', 'help']:
        print_help()
        return 0
    
    # Get subcommand
    subcommand = args[0]
    remaining_args = args[1:]
    
    try:
        if subcommand == 'list':
            return cmd_list(remaining_args)
        elif subcommand == 'info':
            return cmd_info(remaining_args)
        elif subcommand == 'detect':
            return cmd_detect(remaining_args)
        elif subcommand == 'add':
            return cmd_add(remaining_args)
        else:
            print(f"\n❌ Unknown subcommand: {subcommand}")
            print("\nRun 'automation projects --help' to see available commands")
            return 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        return 130
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
