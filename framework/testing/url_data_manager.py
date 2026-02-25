"""
URL Data Manager

Orchestrator for URL test data loading and generation.
Follows Manager pattern from framework (ProjectManager, SessionManager, etc.)

Pattern: Manager (Orchestrator)
Extends: None (Pure manager)
Dependencies: Uses URLDataService

Author: Hybrid Automation Framework
Date: 2026-02-25
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from enum import Enum

from framework.microservices.url_testing_service import URLTestCase
from framework.observability.enterprise_logger import get_enterprise_logger
from framework.observability.universal_logger import log_function


logger = get_enterprise_logger()


class LoadMode(Enum):
    """Data loading mode"""
    MANUAL = "manual"  # Load from test data files
    AUTO = "auto"      # Generate from config
    CLI = "cli"        # Specified via CLI


class URLDataManager:
    """
    URL Data Manager - Orchestrates test data loading
    
    Responsibilities:
    - Detect data source (manual vs auto)
    - Route to appropriate loader
    - Transform data to URLTestCase objects
    - Cache and optimize
    
    Pattern: Manager (Orchestrator)
    Used By: URLTestingService, pytest fixtures
    """
    
    def __init__(self, project: str = "bookslot"):
        self.project = project
        self.test_data_dir = Path(__file__).parent.parent.parent / "test_data" / project
        self.config_dir = Path(__file__).parent.parent.parent / "config"
        self._cache: Dict[str, List[URLTestCase]] = {}
        
        logger.info(f"URLDataManager initialized for project: {project}")
        logger.debug(f"Test data directory: {self.test_data_dir}")
    
    @log_function
    def load_test_cases(
        self,
        environment: str = "staging",
        mode: Optional[LoadMode] = None
    ) -> List[URLTestCase]:
        """
        Load URL test cases
        
        Strategy:
        1. Check if manual test data exists (PRIMARY)
        2. If not, fall back to auto-generation (SECONDARY)
        3. Cache results for performance
        
        Args:
            environment: Target environment (staging, production)
            mode: Force specific mode (optional)
        
        Returns:
            List of URLTestCase objects
        """
        cache_key = f"{self.project}_{environment}_{mode}"
        
        if cache_key in self._cache:
            logger.info(f"Returning cached test cases for {cache_key}")
            return self._cache[cache_key]
        
        # Detect mode if not specified
        if mode is None:
            mode = self._detect_mode()
        
        logger.info(f"Loading test cases in {mode.value} mode for {environment}")
        
        if mode == LoadMode.MANUAL:
            test_cases = self._load_from_files(environment)
        elif mode == LoadMode.AUTO:
            test_cases = self._generate_from_config(environment)
        else:
            test_cases = []
        
        self._cache[cache_key] = test_cases
        logger.info(f"Loaded {len(test_cases)} test cases for {environment}")
        
        return test_cases
    
    def _detect_mode(self) -> LoadMode:
        """Detect which mode to use (manual vs auto)"""
        # Check if manual test data files exist
        for ext in [".json", ".yaml", ".yml", ".csv", ".xlsx"]:
            file_path = self.test_data_dir / f"{self.project}_workflows{ext}"
            if file_path.exists():
                logger.info(f"Found manual test data file: {file_path}")
                return LoadMode.MANUAL
        
        # Fall back to auto-generation
        logger.info("No manual test data found, using auto-generation mode")
        return LoadMode.AUTO
    
    def _load_from_files(self, environment: str) -> List[URLTestCase]:
        """Load test cases from data files (PRIMARY MODE)"""
        # Use existing framework utilities
        try:
            from utils.fake_data_generator import load_workflow_data
            
            # Load data using framework function
            data_list = load_workflow_data(
                project=self.project,
                filename="workflows.json",
                environment=environment
            )
            
            # Transform to URLTestCase objects
            test_cases = []
            for data in data_list:
                test_case = URLTestCase(
                    workflow_id=data.get("workflow_id", ""),
                    environment=data.get("environment", environment),
                    page_name=data.get("page_name", "P1"),
                    query_params=data.get("query_params", {}),
                    expected_status=data.get("expected_status", 200),
                    expected_elements=data.get("expected_elements", []),
                    test_priority=data.get("test_priority", "medium"),
                    description=data.get("description", ""),
                    url_format=data.get("url_format", "query_string"),
                    test_data=data.get("test_data", {}),
                    tags=data.get("tags", [])
                )
                test_cases.append(test_case)
            
            logger.info(f"Loaded {len(test_cases)} test cases from files")
            return test_cases
            
        except ImportError as e:
            logger.warning(f"Could not import load_workflow_data: {e}")
            return []
        except Exception as e:
            logger.error(f"Error loading workflow data: {e}")
            return []
    
    def _generate_from_config(self, environment: str) -> List[URLTestCase]:
        """Generate test cases from config (FALLBACK MODE)"""
        logger.info(f"Generating test cases from config for {environment}")
        
        # Load from config/url_testing.yaml
        # Generate combinations based on configuration
        # This is a fallback when no manual data exists
        
        # For now, return empty list
        # Full implementation would read config and generate combinations
        test_cases = []
        
        logger.info(f"Generated {len(test_cases)} test cases from config")
        return test_cases
    
    def clear_cache(self) -> None:
        """Clear the test case cache"""
        logger.info(f"Clearing URLDataManager cache ({len(self._cache)} entries)")
        self._cache.clear()
    
    def get_test_case_by_id(self, test_id: str, environment: str = "staging") -> Optional[URLTestCase]:
        """
        Get a specific test case by ID
        
        Args:
            test_id: Test case ID
            environment: Environment
        
        Returns:
            URLTestCase if found, None otherwise
        """
        test_cases = self.load_test_cases(environment=environment)
        
        for test_case in test_cases:
            if test_case.test_id == test_id or test_case.workflow_id == test_id:
                return test_case
        
        logger.warning(f"Test case not found: {test_id}")
        return None
    
    def get_test_cases_by_page(self, page_name: str, environment: str = "staging") -> List[URLTestCase]:
        """
        Get all test cases for a specific page
        
        Args:
            page_name: Page name (P1, P2, etc.)
            environment: Environment
        
        Returns:
            List of URLTestCase objects for the page
        """
        all_test_cases = self.load_test_cases(environment=environment)
        page_test_cases = [tc for tc in all_test_cases if tc.page_name == page_name]
        
        logger.info(f"Found {len(page_test_cases)} test cases for {page_name}")
        return page_test_cases
    
    def get_test_cases_by_tags(self, tags: List[str], environment: str = "staging") -> List[URLTestCase]:
        """
        Get test cases matching specific tags
        
        Args:
            tags: List of tags to filter by
            environment: Environment
        
        Returns:
            List of URLTestCase objects matching tags
        """
        all_test_cases = self.load_test_cases(environment=environment)
        
        matching_test_cases = []
        for tc in all_test_cases:
            if any(tag in tc.tags for tag in tags):
                matching_test_cases.append(tc)
        
        logger.info(f"Found {len(matching_test_cases)} test cases matching tags: {tags}")
        return matching_test_cases
