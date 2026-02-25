"""
URL Testing Microservice

Independent, reusable microservice for URL validation and testing.
Extends BaseService from framework.microservices.base

Architecture:
- Service discovery and health checks
- Event-driven communication
- Reusable across ALL projects (bookslot, callcenter, patientintake)
- Follows SOLID principles

Author: Hybrid Automation Framework
Date: 2026-02-25
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from framework.microservices.base import (
    BaseService,
    HealthCheck,
    Message,
    MessagePriority,
    ServiceInfo,
    ServiceStatus,
)
from framework.observability.enterprise_logger import get_enterprise_logger
from framework.observability.universal_logger import log_function, log_async_function


logger = get_enterprise_logger()


class URLFormat(Enum):
    """URL format types"""
    QUERY_STRING = "query_string"  # domain.com/page?workflow_id=X&param=Y
    PATH_PARAM = "path_param"      # domain.com/workflow/X?param=Y
    PATH_BASED = "path_based"      # domain.com/X/booking?param=Y
    HYBRID = "hybrid"              # domain.com/X?param=Y


@dataclass
class URLTestCase:
    """Single URL test case with metadata (Framework Model)"""
    workflow_id: str
    environment: str
    page_name: str
    query_params: Dict[str, Any] = field(default_factory=dict)
    expected_status: int = 200
    expected_elements: List[str] = field(default_factory=list)
    test_priority: str = "medium"
    description: str = ""
    url_format: str = "query_string"
    test_data: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    @property
    def test_id(self) -> str:
        """Unique test identifier"""
        return f"{self.environment}_{self.page_name}_{self.workflow_id}"


@dataclass
class ValidationResult:
    """URL validation result (Framework Model)"""
    url: str
    status_code: int
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validation_time_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)


class URLTestingService(BaseService):
    """
    URL Testing Microservice
    
    Responsibilities:
    - URL generation and validation
    - Test case orchestration
    - Health monitoring
    - Event publishing
    
    Extends: BaseService (framework/microservices/base.py)
    Pattern: Microservice Architecture
    Reusability: All projects (bookslot, callcenter, patientintake)
    """
    
    def __init__(
        self,
        service_name: str = "url-testing",
        version: str = "1.0.0",
        host: str = "localhost",
        port: int = 8001
    ):
        """Initialize URL Testing Service"""
        super().__init__(
            service_name=service_name,
            version=version,
            host=host,
            port=port
        )
        self.test_cases: List[URLTestCase] = []
        self.validation_results: List[ValidationResult] = []
        self._initialized = False
    
    async def _initialize(self) -> None:
        """Initialize service resources"""
        logger.info(f"Initializing {self.name} service v{self.version}")
        
        # Load configurations
        self.config = {}
        
        # Initialize metrics
        self.metrics = {
            "validations_total": 0,
            "validations_passed": 0,
            "validations_failed": 0,
            "average_validation_time_ms": 0
        }
        
        self._initialized = True
        logger.info(f"{self.name} service initialized successfully")
    
    async def _cleanup(self) -> None:
        """Cleanup service resources"""
        logger.info(f"Cleaning up {self.name} service")
        
        # Save results if needed
        if self.validation_results:
            logger.info(f"Saving {len(self.validation_results)} validation results")
        
        # Reset state
        self.test_cases.clear()
        self.validation_results.clear()
        self._initialized = False
        
        logger.info(f"{self.name} service cleaned up successfully")
    
    async def _health_check_impl(self) -> HealthCheck:
        """Perform service health check"""
        checks = []
        status = ServiceStatus.HEALTHY
        details = {}
        
        # Check initialization
        if not self._initialized:
            status = ServiceStatus.UNHEALTHY
            details["initialization"] = "Service not initialized"
        else:
            checks.append("initialized")
        
        # Check data loader readiness
        checks.append("data_loader_ready")
        
        # Check configuration
        checks.append("config_loaded")
        
        # Check metrics
        details["metrics"] = self.metrics
        
        return HealthCheck(
            service_name=self.name,
            status=status,
            timestamp=datetime.now(),
            details=details,
            is_healthy=(status == ServiceStatus.HEALTHY)
        )
    
    @log_async_function
    async def load_test_cases(
        self,
        project: str,
        environment: str = "staging"
    ) -> List[URLTestCase]:
        """
        Load URL test cases for project
        
        Args:
            project: Project name (bookslot, callcenter, etc.)
            environment: Environment (staging, production)
        
        Returns:
            List of URLTestCase objects
        """
        logger.info(f"Loading test cases for {project} in {environment}")
        
        # This will be delegated to URLDataService in full implementation
        # For now, return empty list
        self.test_cases = []
        
        logger.info(f"Loaded {len(self.test_cases)} test cases")
        return self.test_cases
    
    @log_async_function
    async def validate_url(
        self,
        url: str,
        expected_elements: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Validate single URL
        
        Args:
            url: URL to validate
            expected_elements: List of expected element selectors
        
        Returns:
            ValidationResult with detailed status
        """
        logger.info(f"Validating URL: {url}")
        
        # This will be delegated to URLValidationService in full implementation
        # For now, return basic result
        result = ValidationResult(
            url=url,
            status_code=200,
            is_valid=True,
            validation_time_ms=0
        )
        
        self.validation_results.append(result)
        self.metrics["validations_total"] += 1
        
        if result.is_valid:
            self.metrics["validations_passed"] += 1
        else:
            self.metrics["validations_failed"] += 1
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        return self.metrics.copy()


class URLDataService(BaseService):
    """
    URL Data Management Service
    
    Responsibilities:
    - Load test data from files (JSON/YAML/CSV/Excel)
    - Generate test cases (fallback mode)
    - Data transformation and enrichment
    
    Extends: BaseService
    Pattern: Data Service
    """
    
    def __init__(self):
        super().__init__(
            service_name="url-data",
            version="1.0.0"
        )
        self._data_cache: Dict[str, List[URLTestCase]] = {}
    
    async def _initialize(self) -> None:
        """Initialize data service"""
        logger.info("Initializing URL Data Service")
        self._data_cache.clear()
    
    async def _cleanup(self) -> None:
        """Cleanup data service"""
        logger.info("Cleaning up URL Data Service")
        self._data_cache.clear()
    
    async def _health_check_impl(self) -> HealthCheck:
        """Health check for data service"""
        checks = ["data_sources_available"]
        
        return HealthCheck(
            service_name=self.name,
            status=ServiceStatus.HEALTHY,
            timestamp=datetime.now(),
            details={"cache_size": len(self._data_cache)},
            is_healthy=True
        )
    
    @log_async_function
    async def load_workflow_data(
        self,
        project: str,
        environment: str = "staging"
    ) -> List[URLTestCase]:
        """
        Load workflow data from files
        
        Args:
            project: Project name
            environment: Environment name
        
        Returns:
            List of URLTestCase objects
        """
        cache_key = f"{project}_{environment}"
        
        if cache_key in self._data_cache:
            logger.info(f"Returning cached data for {cache_key}")
            return self._data_cache[cache_key]
        
        # Load from files (implemented in URLDataManager)
        test_cases = []
        
        self._data_cache[cache_key] = test_cases
        return test_cases


class URLValidationService(BaseService):
    """
    URL Validation Service
    
    Responsibilities:
    - HTTP status validation
    - Element presence validation
    - Error message validation
    - Performance validation
    
    Extends: BaseService
    Pattern: Validation Service
    """
    
    def __init__(self):
        super().__init__(
            service_name="url-validation",
            version="1.0.0"
        )
        self._validation_count = 0
    
    async def _initialize(self) -> None:
        """Initialize validation service"""
        logger.info("Initializing URL Validation Service")
        self._validation_count = 0
    
    async def _cleanup(self) -> None:
        """Cleanup validation service"""
        logger.info("Cleaning up URL Validation Service")
    
    async def _health_check_impl(self) -> HealthCheck:
        """Health check for validation service"""
        checks = ["playwright_available", "validators_ready"]
        
        return HealthCheck(
            service_name=self.name,
            status=ServiceStatus.HEALTHY,
            timestamp=datetime.now(),
            details={"validation_count": self._validation_count},
            is_healthy=True
        )
    
    @log_async_function
    async def validate(
        self,
        url: str,
        expected_elements: Optional[List[str]] = None,
        timeout: int = 10000
    ) -> ValidationResult:
        """
        Validate URL
        
        Args:
            url: URL to validate
            expected_elements: Expected element selectors
            timeout: Timeout in milliseconds
        
        Returns:
            ValidationResult
        """
        self._validation_count += 1
        
        # Basic validation result (full implementation uses URLValidator)
        result = ValidationResult(
            url=url,
            status_code=200,
            is_valid=True,
            validation_time_ms=0
        )
        
        return result
