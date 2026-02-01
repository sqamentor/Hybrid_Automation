"""Test Execution Models.

Pydantic models for test context, results, and metadata.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TestStatus(str, Enum):
    """Test execution status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"
    IN_PROGRESS = "in_progress"


class TestPriority(str, Enum):
    """Test priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestContext(BaseModel):
    """Test execution context with all runtime information."""
    
    model_config = ConfigDict(
        frozen=False,
        extra="allow",
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )
    
    # Test identification
    test_id: str = Field(..., description="Unique test identifier")
    test_name: str = Field(..., description="Test name")
    test_suite: str = Field(..., description="Test suite name")
    
    # Environment context
    environment: str = Field(..., description="Test environment")
    project_name: str = Field(..., description="Project name")
    
    # Execution metadata
    start_time: datetime = Field(default_factory=datetime.now, description="Test start time")
    end_time: Optional[datetime] = Field(default=None, description="Test end time")
    duration_ms: Optional[int] = Field(default=None, description="Test duration in milliseconds")
    
    # Browser context
    browser_type: str = Field(default="chromium", description="Browser type")
    browser_version: Optional[str] = Field(default=None, description="Browser version")
    
    # Test data
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Test input data")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Runtime variables")
    
    # Artifacts
    screenshot_path: Optional[Path] = Field(default=None, description="Screenshot path")
    video_path: Optional[Path] = Field(default=None, description="Video path")
    trace_path: Optional[Path] = Field(default=None, description="Trace path")
    log_path: Optional[Path] = Field(default=None, description="Log path")
    
    # Test steps (for logging)
    steps: List[str] = Field(default_factory=list, description="Test execution steps")
    
    def add_step(self, step: str) -> None:
        """Add a step to the test execution log."""
        self.steps.append(step)
    
    def mark_completed(self, duration_ms: int) -> None:
        """Mark test as completed."""
        self.end_time = datetime.now()
        self.duration_ms = duration_ms


class TestResult(BaseModel):
    """Test execution result with detailed outcome."""
    
    model_config = ConfigDict(
        frozen=False,
        extra="allow",
        validate_assignment=True,
    )
    
    # Result status
    status: TestStatus = Field(..., description="Test execution status")
    
    # Test context
    context: TestContext = Field(..., description="Test execution context")
    
    # Outcome details
    passed: bool = Field(..., description="Whether test passed")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    error_trace: Optional[str] = Field(default=None, description="Full error trace")
    
    # Assertions
    assertions_passed: int = Field(default=0, description="Number of passed assertions")
    assertions_failed: int = Field(default=0, description="Number of failed assertions")
    assertion_details: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Detailed assertion results"
    )
    
    # Performance metrics
    page_load_time_ms: Optional[int] = Field(default=None, description="Page load time")
    api_response_time_ms: Optional[int] = Field(default=None, description="API response time")
    total_duration_ms: int = Field(..., description="Total test duration")
    
    # Artifacts
    artifacts: Dict[str, Path] = Field(default_factory=dict, description="Test artifacts")
    
    @property
    def pass_rate(self) -> float:
        """Calculate assertion pass rate."""
        total = self.assertions_passed + self.assertions_failed
        if total == 0:
            return 100.0
        return (self.assertions_passed / total) * 100.0


class TestMetadata(BaseModel):
    """Test metadata for reporting and analytics."""
    
    model_config = ConfigDict(
        frozen=False,
        extra="allow",
        validate_assignment=True,
    )
    
    # Test classification
    test_id: str = Field(..., description="Unique test identifier")
    test_name: str = Field(..., description="Test name")
    description: Optional[str] = Field(default=None, description="Test description")
    
    # Categorization
    tags: List[str] = Field(default_factory=list, description="Test tags")
    priority: TestPriority = Field(default=TestPriority.MEDIUM, description="Test priority")
    category: str = Field(default="functional", description="Test category")
    
    # Ownership
    author: Optional[str] = Field(default=None, description="Test author")
    team: Optional[str] = Field(default=None, description="Owning team")
    
    # Requirements traceability
    requirement_ids: List[str] = Field(default_factory=list, description="Linked requirement IDs")
    jira_tickets: List[str] = Field(default_factory=list, description="Linked JIRA tickets")
    
    # Test characteristics
    estimated_duration_ms: Optional[int] = Field(default=None, description="Estimated duration")
    is_flaky: bool = Field(default=False, description="Whether test is known to be flaky")
    retry_count: int = Field(default=0, ge=0, le=5, description="Number of retries allowed")
    
    # Dependencies
    depends_on: List[str] = Field(default_factory=list, description="Test dependencies")
    test_data_files: List[Path] = Field(default_factory=list, description="Required test data files")
