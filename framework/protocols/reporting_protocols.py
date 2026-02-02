"""
Reporting Protocol Interfaces

Protocol classes for reporting, metrics, and artifact management.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from framework.models.test_models import TestMetadata, TestResult


@runtime_checkable
class ReportGenerator(Protocol):
    """Protocol for report generation implementations"""

    def generate_report(
        self, results: List[TestResult], output_path: Path, format: str = "html"
    ) -> Path:
        """Generate test report"""
        ...

    def add_result(self, result: TestResult) -> None:
        """Add test result to report"""
        ...

    def finalize_report(self) -> None:
        """Finalize and save report"""
        ...

    def get_summary(self) -> Dict[str, Any]:
        """Get report summary statistics"""
        ...


@runtime_checkable
class MetricsCollector(Protocol):
    """Protocol for metrics collection implementations"""

    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a metric value"""
        ...

    def increment_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric"""
        ...

    def record_duration(
        self, name: str, duration_ms: int, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record duration metric"""
        ...

    def get_metric(self, name: str) -> Optional[float]:
        """Get current metric value"""
        ...

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        ...

    def export_metrics(self, output_path: Path) -> None:
        """Export metrics to file"""
        ...


@runtime_checkable
class ArtifactStorage(Protocol):
    """Protocol for test artifact storage implementations"""

    def store_screenshot(self, test_id: str, image_data: bytes) -> Path:
        """Store screenshot artifact"""
        ...

    def store_video(self, test_id: str, video_path: Path) -> Path:
        """Store video artifact"""
        ...

    def store_trace(self, test_id: str, trace_path: Path) -> Path:
        """Store trace artifact"""
        ...

    def store_log(self, test_id: str, log_content: str) -> Path:
        """Store log artifact"""
        ...

    def get_artifact(self, test_id: str, artifact_type: str) -> Optional[Path]:
        """Retrieve artifact by test ID and type"""
        ...

    def list_artifacts(self, test_id: str) -> List[Path]:
        """List all artifacts for a test"""
        ...

    def cleanup_old_artifacts(self, days: int = 7) -> int:
        """Clean up artifacts older than specified days"""
        ...
