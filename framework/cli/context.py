"""
CLI Utilities - Context Detection and Helper Functions
Provides context-aware functionality for multi-project execution

Features:
- Current directory project detection
- Workspace root detection
- Path resolution from any location
- Context information gathering

Author: Lokendra Singh
Email: lokendra.singh@centerforvein.com
Website: www.centerforvein.com
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from framework.core.project_manager import get_project_manager


class WorkspaceContext:
    """
    Detects and provides context about the current workspace location
    Enables running commands from any directory within the project
    """
    
    def __init__(self):
        self.cwd = Path.cwd()
        self.workspace_root = self._find_workspace_root()
        self.current_project = self._detect_current_project()
        self.relative_path = self._get_relative_path()
    
    def _find_workspace_root(self) -> Optional[Path]:
        """
        Find the workspace root by looking for marker files
        Searches upward from current directory
        """
        markers = [
            'pyproject.toml',
            'pytest.ini',
            'setup.py',
            '.git',
            'framework',  # Framework directory
        ]
        
        current = self.cwd
        
        # Search up to 10 levels
        for _ in range(10):
            # Check if any marker exists
            for marker in markers:
                marker_path = current / marker
                if marker_path.exists():
                    return current
            
            # Move up one level
            parent = current.parent
            if parent == current:  # Reached root
                break
            current = parent
        
        return None
    
    def _detect_current_project(self) -> Optional[str]:
        """
        Detect which project we're currently in based on directory structure
        Returns project name if inside a project directory
        """
        if not self.workspace_root:
            return None
        
        # Get relative path from workspace root
        try:
            rel_path = self.cwd.relative_to(self.workspace_root)
        except ValueError:
            return None
        
        # Check if we're inside a project-specific directory
        parts = rel_path.parts
        
        if not parts:
            return None
        
        # Check common project directories
        project_dirs = ['pages', 'recorded_tests', 'test_data', 'tests']
        
        if parts[0] in project_dirs and len(parts) > 1:
            # Second part is likely the project name
            potential_project = parts[1]
            
            # Validate against known projects
            try:
                pm = get_project_manager()
                if potential_project in pm.projects:
                    return potential_project
            except Exception:
                pass
        
        return None
    
    def _get_relative_path(self) -> Optional[Path]:
        """Get current directory relative to workspace root"""
        if not self.workspace_root:
            return None
        
        try:
            return self.cwd.relative_to(self.workspace_root)
        except ValueError:
            return None
    
    def is_in_workspace(self) -> bool:
        """Check if current directory is inside the workspace"""
        return self.workspace_root is not None
    
    def get_info(self) -> Dict[str, Any]:
        """Get complete context information"""
        return {
            'in_workspace': self.is_in_workspace(),
            'workspace_root': str(self.workspace_root) if self.workspace_root else None,
            'current_directory': str(self.cwd),
            'relative_path': str(self.relative_path) if self.relative_path else None,
            'detected_project': self.current_project,
        }
    
    def print_context(self):
        """Print current context information"""
        info = self.get_info()
        
        print("\n📍 Current Context:")
        print("="*80)
        
        if info['in_workspace']:
            print(f"  ✓ Inside workspace")
            print(f"  📁 Workspace Root: {info['workspace_root']}")
            print(f"  📂 Current Dir: {info['relative_path']}")
            
            if info['detected_project']:
                print(f"  🎯 Detected Project: {info['detected_project']}")
            else:
                print(f"  ⚠️  No project detected (not in project-specific directory)")
        else:
            print(f"  ✗ Not inside workspace")
            print(f"  📂 Current Dir: {info['current_directory']}")
            print(f"  ⚠️  Run from workspace root or project directory")
        
        print("="*80 + "\n")


def get_context() -> WorkspaceContext:
    """Get current workspace context"""
    return WorkspaceContext()


def ensure_workspace() -> Path:
    """
    Ensure we're in a workspace and return workspace root
    Raises error if not in workspace
    """
    context = get_context()
    
    if not context.is_in_workspace():
        print("\n❌ Error: Not inside automation workspace")
        print("\nPlease run this command from:")
        print("  - Workspace root directory")
        print("  - Any project directory (pages/, tests/, etc.)")
        print()
        raise RuntimeError("Not inside automation workspace")
    
    return context.workspace_root


def detect_project_context() -> Tuple[Optional[str], WorkspaceContext]:
    """
    Detect project from current context
    Returns (project_name, context) or (None, context)
    """
    context = get_context()
    return (context.current_project, context)


def resolve_workspace_path(relative_path: str) -> Path:
    """
    Resolve a path relative to workspace root
    Works from any directory in the workspace
    """
    workspace_root = ensure_workspace()
    return workspace_root / relative_path


def find_project_tests(project: str) -> Path:
    """Find test directory for a specific project"""
    workspace_root = ensure_workspace()
    
    # Try multiple possible locations
    possible_paths = [
        workspace_root / 'recorded_tests' / project,
        workspace_root / 'tests' / project,
        workspace_root / 'pages' / project,
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    # Return first option as default (might need creation)
    return possible_paths[0]


def print_workspace_info():
    """Print detailed workspace information"""
    context = get_context()
    
    if not context.is_in_workspace():
        print("\n❌ Not inside automation workspace\n")
        return
    
    context.print_context()
    
    # Load project manager and show available projects
    try:
        pm = get_project_manager()
        projects = pm.get_available_projects()
        
        print("📦 Available Projects:")
        print("="*80)
        for project in projects:
            current = "← current" if project['name'] == context.current_project else ""
            print(f"  • {project['name']:<20} {project['full_name']} {current}")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"⚠️  Could not load projects: {e}\n")


if __name__ == "__main__":
    # Test context detection
    print_workspace_info()
