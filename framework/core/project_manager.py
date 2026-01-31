"""
Project Manager - Multi-Project Recording and Organization

This module provides intelligent project detection, environment awareness,
and automatic organization of recorded tests and page objects.

Features:
- Automatic project detection from URLs
- Environment-aware URL matching (dev, staging, prod)
- Dynamic project structure creation
- Project registry management
- Future-proof project addition
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from urllib.parse import urlparse


class ProjectDetectionError(Exception):
    """Raised when project cannot be detected"""
    pass


class ProjectConfigError(Exception):
    """Raised when project configuration is invalid"""
    pass


class ProjectManager:
    """
    Manages multi-project recording organization with environment awareness
    
    Capabilities:
    - Auto-detect project from URL
    - Detect environment (dev/staging/prod) from URL
    - Create project-specific directory structure
    - Generate project-specific recordings and page objects
    - Register new projects dynamically
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ProjectManager
        
        Args:
            config_path: Path to projects.yaml (default: config/projects.yaml)
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "projects.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.projects = self.config.get('projects', {})
        self.global_settings = self.config.get('global_settings', {})
        self.workspace_root = Path(__file__).parent.parent.parent
    
    def _load_config(self) -> Dict[str, Any]:
        """Load projects configuration from YAML"""
        if not self.config_path.exists():
            raise ProjectConfigError(f"Project config not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def detect_project_from_url(self, url: str, manual_project: Optional[str] = None) -> str:
        """
        Detect project from URL with intelligent matching
        
        Args:
            url: URL being recorded
            manual_project: Manual project override
        
        Returns:
            Project name (e.g., 'bookslot', 'callcenter')
        
        Raises:
            ProjectDetectionError: If project cannot be detected
        """
        # Manual override takes precedence
        if manual_project:
            if manual_project in self.projects:
                return manual_project
            else:
                raise ProjectDetectionError(
                    f"Manual project '{manual_project}' not found. "
                    f"Available: {list(self.projects.keys())}"
                )
        
        # Parse URL
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        full_url = url.lower()
        
        # Try to match against each project's URL patterns
        for project_name, project_config in self.projects.items():
            url_patterns = project_config.get('url_patterns', [])
            
            for pattern in url_patterns:
                # Convert pattern to regex
                regex_pattern = pattern.replace('*', '.*')
                
                # Try matching hostname
                if re.search(regex_pattern, hostname, re.IGNORECASE):
                    return project_name
                
                # Try matching full URL
                if re.search(regex_pattern, full_url, re.IGNORECASE):
                    return project_name
        
        # No match found - use default or raise error
        default_project = self.global_settings.get('default_project')
        if default_project:
            print(f"⚠️  No project pattern matched for URL: {url}")
            print(f"    Using default project: {default_project}")
            return default_project
        
        raise ProjectDetectionError(
            f"Could not detect project from URL: {url}\n"
            f"Available projects: {list(self.projects.keys())}\n"
            f"Use --project parameter to specify manually."
        )
    
    def detect_environment_from_url(self, url: str, project: str) -> str:
        """
        Detect environment (staging/prod) from URL
        
        Args:
            url: URL being accessed
            project: Project name
        
        Returns:
            Environment name ('staging' or 'prod')
        """
        # Check if TEST_ENV is set (highest priority)
        env_from_var = os.getenv('TEST_ENV')
        if env_from_var and self.global_settings.get('environment_detection', {}).get('prefer_env_variable', True):
            env_lower = env_from_var.lower()
            if env_lower in ['staging', 'stage', 'uat', 'qa', 'test']:
                return 'staging'
            elif env_lower in ['prod', 'production']:
                return 'prod'
        
        # Auto-detect from URL
        if self.global_settings.get('environment_detection', {}).get('auto_detect', True):
            url_lower = url.lower()
            
            # Check for staging keywords in URL
            staging_keywords = self.global_settings.get('environment_detection', {}).get('staging_keywords', ['staging', 'stage', 'uat', 'qa', 'test'])
            for keyword in staging_keywords:
                if keyword in url_lower:
                    return 'staging'
            
            # Match against project's environment URLs
            project_config = self.projects.get(project, {})
            environments = project_config.get('environments', {})
            
            for env_name, env_config in environments.items():
                env_url = env_config.get('ui_url', '').lower()
                if env_url in url_lower or url_lower in env_url:
                    return env_name
        
        # Fallback to production (default)
        return self.global_settings.get('environment_detection', {}).get('fallback_env', 'prod')
    
    def get_project_config(self, project: str) -> Dict[str, Any]:
        """
        Get full configuration for a project
        
        Args:
            project: Project name
        
        Returns:
            Project configuration dictionary
        
        Raises:
            ProjectConfigError: If project not found
        """
        if project not in self.projects:
            raise ProjectConfigError(
                f"Project '{project}' not found. "
                f"Available: {list(self.projects.keys())}"
            )
        
        return self.projects[project]
    
    def get_project_paths(self, project: str) -> Dict[str, Path]:
        """
        Get absolute paths for project directories
        
        Args:
            project: Project name
        
        Returns:
            Dictionary with 'pages', 'recorded_tests', 'test_data' paths
        """
        config = self.get_project_config(project)
        paths = config.get('paths', {})
        
        return {
            'pages': self.workspace_root / paths.get('pages', f'pages/{project}'),
            'recorded_tests': self.workspace_root / paths.get('recorded_tests', f'recorded_tests/{project}'),
            'test_data': self.workspace_root / paths.get('test_data', f'test_data/{project}')
        }
    
    def create_project_structure(self, project: str) -> Dict[str, Path]:
        """
        Create directory structure for a project
        
        Args:
            project: Project name
        
        Returns:
            Dictionary of created paths
        """
        paths = self.get_project_paths(project)
        config = self.get_project_config(project)
        
        # Create directories
        for path_type, path in paths.items():
            path.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py
            init_file = path / "__init__.py"
            if not init_file.exists():
                template = self.global_settings.get('templates', {}).get('init_file', '')
                content = template.format(
                    project_name=config.get('name', project),
                    project_description=config.get('description', '')
                )
                init_file.write_text(content)
            
            # Create README.md for test directories
            if path_type == 'recorded_tests':
                readme_file = path / "README.md"
                if not readme_file.exists():
                    template = self.global_settings.get('templates', {}).get('readme_file', '')
                    content = template.format(
                        project_name=config.get('name', project),
                        project_description=config.get('description', ''),
                        team=config.get('team', 'Team'),
                        contact=config.get('contact', 'team@example.com')
                    )
                    readme_file.write_text(content)
        
        return paths
    
    def generate_recording_filename(self, project: str, feature: str = None, timestamp: datetime = None) -> str:
        """
        Generate filename for recorded test
        
        Args:
            project: Project name
            feature: Feature/page name (optional)
            timestamp: Timestamp (default: now)
        
        Returns:
            Filename (e.g., 'test_bookslot_basic_info_20260126_143022.py')
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        naming_config = self.global_settings.get('recording_naming', {})
        pattern = naming_config.get('pattern', 'test_{project}_{feature}_{timestamp}')
        ts_format = naming_config.get('timestamp_format', '%Y%m%d_%H%M%S')
        
        # Generate timestamp string
        ts_string = timestamp.strftime(ts_format)
        
        # Generate feature name
        if feature is None:
            feature = "recording"
        else:
            # Clean feature name
            feature = re.sub(r'[^a-zA-Z0-9_]', '_', feature.lower())
            feature = re.sub(r'_+', '_', feature).strip('_')
        
        # Build filename
        filename = pattern.format(
            project=project,
            feature=feature,
            timestamp=ts_string
        )
        
        return f"{filename}.py"
    
    def generate_page_object_filename(self, feature: str) -> str:
        """
        Generate filename for page object
        
        Args:
            feature: Feature/page name
        
        Returns:
            Filename (e.g., 'basic_info_page.py')
        """
        naming_config = self.global_settings.get('page_object_naming', {})
        pattern = naming_config.get('pattern', '{feature}_page')
        suffix = naming_config.get('suffix', '.py')
        
        # Clean feature name
        feature = re.sub(r'[^a-zA-Z0-9_]', '_', feature.lower())
        feature = re.sub(r'_+', '_', feature).strip('_')
        
        return f"{pattern.format(feature=feature)}{suffix}"
    
    def get_available_projects(self) -> List[Dict[str, str]]:
        """
        Get list of all available projects with metadata
        
        Returns:
            List of project dictionaries
        """
        projects = []
        for project_name, config in self.projects.items():
            projects.append({
                'name': project_name,
                'full_name': config.get('name', project_name),
                'description': config.get('description', ''),
                'team': config.get('team', ''),
                'contact': config.get('contact', '')
            })
        return projects
    
    def register_new_project(
        self,
        project_name: str,
        full_name: str,
        description: str,
        url_patterns: List[str],
        environments: Dict[str, Dict[str, str]],
        team: str = "Team",
        contact: str = "team@example.com"
    ) -> Dict[str, Any]:
        """
        Register a new project in the configuration
        
        Args:
            project_name: Short project identifier (e.g., 'pharmacy')
            full_name: Full project name
            description: Project description
            url_patterns: List of URL patterns for detection
            environments: Environment configurations (dev, staging, prod)
            team: Team name
            contact: Team contact
        
        Returns:
            New project configuration
        """
        # Validate project name doesn't exist
        if project_name in self.projects:
            raise ProjectConfigError(f"Project '{project_name}' already exists")
        
        # Create project configuration
        new_config = {
            'name': full_name,
            'description': description,
            'url_patterns': url_patterns,
            'environments': environments,
            'paths': {
                'pages': f'pages/{project_name}',
                'recorded_tests': f'recorded_tests/{project_name}',
                'test_data': f'test_data/{project_name}'
            },
            'settings': {
                'default_timeout': 30000
            },
            'team': team,
            'contact': contact
        }
        
        # Add to configuration
        self.projects[project_name] = new_config
        self.config['projects'][project_name] = new_config
        
        # Save configuration
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        
        # Create project structure
        self.create_project_structure(project_name)
        
        return new_config
    
    def get_project_info(
        self,
        url: str,
        manual_project: Optional[str] = None,
        environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get complete project information from URL
        
        Args:
            url: URL being recorded
            manual_project: Manual project override
            environment: Manual environment override (dev, staging, prod)
        
        Returns:
            Dictionary with project, environment, paths, and config
        """
        # Detect project
        project = self.detect_project_from_url(url, manual_project)
        
        # Detect environment (use manual override if provided)
        if environment:
            env = environment
        else:
            env = self.detect_environment_from_url(url, project)
        
        # Get configuration
        config = self.get_project_config(project)
        
        # Get paths
        paths = self.get_project_paths(project)
        
        # Ensure directories exist
        if self.global_settings.get('auto_create_directories', True):
            paths = self.create_project_structure(project)
        
        return {
            'project': project,
            'environment': env,
            'config': config,
            'paths': paths,
            'full_name': config.get('name', project),
            'description': config.get('description', ''),
            'team': config.get('team', ''),
            'url': url
        }


# Convenience function for quick access
def get_project_manager() -> ProjectManager:
    """Get singleton ProjectManager instance"""
    if not hasattr(get_project_manager, '_instance'):
        get_project_manager._instance = ProjectManager()
    return get_project_manager._instance
