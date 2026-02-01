"""
Distributed test execution configuration using pytest-xdist.

Features:
- Parallel test execution across multiple CPUs
- Load balancing
- Worker management
- Result aggregation
"""
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import pytest


class DistributedTestConfig:
    """Configuration for distributed test execution."""
    
    def __init__(
        self,
        num_workers: str = "auto",
        dist_mode: str = "loadscope",  # loadscope, loadfile, loadgroup
        max_worker_restart: int = 0,
        timeout: Optional[int] = None,
        rsync_dirs: Optional[list] = None
    ):
        """
        Initialize distributed test configuration.
        
        Args:
            num_workers: Number of workers ("auto", "logical", or integer)
            dist_mode: Distribution mode:
                - loadscope: balance by test scope (class/module)
                - loadfile: balance by test file
                - loadgroup: balance by custom groups
            max_worker_restart: Max worker restarts before failing
            timeout: Test timeout in seconds
            rsync_dirs: Directories to sync to workers
        """
        self.num_workers = num_workers
        self.dist_mode = dist_mode
        self.max_worker_restart = max_worker_restart
        self.timeout = timeout
        self.rsync_dirs = rsync_dirs or []


def get_pytest_args(config: DistributedTestConfig) -> list:
    """
    Get pytest arguments for distributed execution.
    
    Args:
        config: Distributed test configuration
    
    Returns:
        List of pytest arguments
    
    Example:
        ```python
        config = DistributedTestConfig(
            num_workers="4",
            dist_mode="loadscope"
        )
        
        args = get_pytest_args(config)
        pytest.main(args)
        ```
    """
    args = [
        "-n", str(config.num_workers),
        f"--dist={config.dist_mode}",
        f"--maxfail={config.max_worker_restart}"
    ]
    
    if config.timeout:
        args.extend(["--timeout", str(config.timeout)])
    
    for rsync_dir in config.rsync_dirs:
        args.extend(["--rsyncdir", str(rsync_dir)])
    
    return args


def run_distributed_tests(
    test_path: str,
    config: Optional[DistributedTestConfig] = None,
    additional_args: Optional[list] = None
) -> int:
    """
    Run tests in distributed mode.
    
    Args:
        test_path: Path to tests directory or specific test file
        config: Distributed test configuration
        additional_args: Additional pytest arguments
    
    Returns:
        Exit code (0 = success, >0 = failures)
    
    Example:
        ```python
        from framework.testing.distributed import run_distributed_tests, DistributedTestConfig
        
        # Run all tests with 4 workers
        config = DistributedTestConfig(num_workers="4")
        exit_code = run_distributed_tests("tests/", config)
        
        # Run specific tests with auto workers
        config = DistributedTestConfig(num_workers="auto")
        exit_code = run_distributed_tests(
            "tests/unit/",
            config,
            additional_args=["-v", "--tb=short"]
        )
        ```
    """
    config = config or DistributedTestConfig()
    additional_args = additional_args or []
    
    args = get_pytest_args(config)
    args.extend(additional_args)
    args.append(test_path)
    
    return pytest.main(args)


# ============================================================================
# Worker Management
# ============================================================================

class WorkerManager:
    """
    Manages distributed test workers.
    
    Example:
        ```python
        manager = WorkerManager()
        
        # Get worker info
        info = manager.get_worker_info()
        print(f"Worker ID: {info['worker_id']}")
        
        # Check if running in worker
        if manager.is_worker():
            print("Running in distributed worker")
        ```
    """
    
    @staticmethod
    def is_worker() -> bool:
        """
        Check if running in a pytest-xdist worker.
        
        Returns:
            True if running in worker, False if main process
        """
        return hasattr(sys, "_pytest_xdist_worker_id")
    
    @staticmethod
    def get_worker_id() -> Optional[str]:
        """
        Get current worker ID.
        
        Returns:
            Worker ID (e.g., "gw0", "gw1") or None if not in worker
        """
        if WorkerManager.is_worker():
            return getattr(sys, "_pytest_xdist_worker_id", None)
        return None
    
    @staticmethod
    def get_worker_info() -> Dict[str, Any]:
        """
        Get worker information.
        
        Returns:
            Dictionary with worker details
        """
        return {
            "is_worker": WorkerManager.is_worker(),
            "worker_id": WorkerManager.get_worker_id(),
            "is_main": not WorkerManager.is_worker()
        }


# ============================================================================
# Test Grouping
# ============================================================================

def pytest_configure(config):
    """
    Configure pytest for distributed execution.
    
    Add custom markers and configure xdist.
    """
    config.addinivalue_line(
        "markers",
        "distributed: mark test to run in distributed mode only"
    )
    config.addinivalue_line(
        "markers",
        "group(name): assign test to a distribution group"
    )


def pytest_collection_modifyitems(items):
    """
    Modify test collection for distributed execution.
    
    Group tests by custom markers.
    """
    for item in items:
        # Add group marker based on test file
        if "test_api" in item.nodeid:
            item.add_marker(pytest.mark.group("api"))
        elif "test_ui" in item.nodeid:
            item.add_marker(pytest.mark.group("ui"))
        elif "test_unit" in item.nodeid:
            item.add_marker(pytest.mark.group("unit"))


# ============================================================================
# Load Balancing Strategies
# ============================================================================

class LoadBalancer:
    """
    Custom load balancing strategies for distributed testing.
    
    Example:
        ```python
        balancer = LoadBalancer()
        
        # Group tests by estimated duration
        groups = balancer.balance_by_duration(test_items, num_workers=4)
        
        # Group tests by complexity
        groups = balancer.balance_by_complexity(test_items, num_workers=4)
        ```
    """
    
    @staticmethod
    def balance_by_duration(test_items: list, num_workers: int) -> Dict[int, list]:
        """
        Balance tests by estimated duration.
        
        Args:
            test_items: List of test items
            num_workers: Number of workers
        
        Returns:
            Dictionary mapping worker ID to test items
        """
        # Sort tests by estimated duration (longest first)
        sorted_items = sorted(
            test_items,
            key=lambda item: getattr(item, "estimated_duration", 1.0),
            reverse=True
        )
        
        # Distribute to workers
        worker_loads = {i: [] for i in range(num_workers)}
        worker_times = {i: 0.0 for i in range(num_workers)}
        
        for item in sorted_items:
            # Assign to worker with least load
            min_worker = min(worker_times, key=worker_times.get)
            worker_loads[min_worker].append(item)
            worker_times[min_worker] += getattr(item, "estimated_duration", 1.0)
        
        return worker_loads
    
    @staticmethod
    def balance_by_complexity(test_items: list, num_workers: int) -> Dict[int, list]:
        """
        Balance tests by complexity score.
        
        Args:
            test_items: List of test items
            num_workers: Number of workers
        
        Returns:
            Dictionary mapping worker ID to test items
        """
        # Sort tests by complexity (high first)
        sorted_items = sorted(
            test_items,
            key=lambda item: getattr(item, "complexity_score", 1),
            reverse=True
        )
        
        # Round-robin distribution
        worker_loads = {i: [] for i in range(num_workers)}
        
        for idx, item in enumerate(sorted_items):
            worker_id = idx % num_workers
            worker_loads[worker_id].append(item)
        
        return worker_loads


# ============================================================================
# Result Aggregation
# ============================================================================

class DistributedResultAggregator:
    """
    Aggregates test results from distributed workers.
    
    Example:
        ```python
        aggregator = DistributedResultAggregator()
        
        # Add worker results
        aggregator.add_worker_result("gw0", {
            "passed": 10,
            "failed": 2,
            "skipped": 1
        })
        aggregator.add_worker_result("gw1", {
            "passed": 8,
            "failed": 1,
            "skipped": 0
        })
        
        # Get summary
        summary = aggregator.get_summary()
        print(f"Total passed: {summary['total_passed']}")
        ```
    """
    
    def __init__(self):
        """Initialize result aggregator."""
        self.worker_results: Dict[str, Dict[str, Any]] = {}
    
    def add_worker_result(self, worker_id: str, result: Dict[str, Any]) -> None:
        """
        Add result from a worker.
        
        Args:
            worker_id: Worker ID
            result: Result dictionary
        """
        self.worker_results[worker_id] = result
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get aggregated summary of all worker results.
        
        Returns:
            Summary dictionary with totals
        """
        summary = {
            "total_passed": 0,
            "total_failed": 0,
            "total_skipped": 0,
            "total_tests": 0,
            "num_workers": len(self.worker_results),
            "workers": list(self.worker_results.keys())
        }
        
        for worker_id, result in self.worker_results.items():
            summary["total_passed"] += result.get("passed", 0)
            summary["total_failed"] += result.get("failed", 0)
            summary["total_skipped"] += result.get("skipped", 0)
        
        summary["total_tests"] = (
            summary["total_passed"] +
            summary["total_failed"] +
            summary["total_skipped"]
        )
        
        return summary
    
    def get_worker_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for each worker.
        
        Returns:
            Dictionary mapping worker ID to statistics
        """
        stats = {}
        
        for worker_id, result in self.worker_results.items():
            total = (
                result.get("passed", 0) +
                result.get("failed", 0) +
                result.get("skipped", 0)
            )
            
            stats[worker_id] = {
                "total_tests": total,
                "passed": result.get("passed", 0),
                "failed": result.get("failed", 0),
                "skipped": result.get("skipped", 0),
                "pass_rate": (result.get("passed", 0) / total * 100) if total > 0 else 0
            }
        
        return stats


# ============================================================================
# Conftest Hooks for Distributed Testing
# ============================================================================

# Example conftest.py configuration:
"""
# conftest.py

from framework.testing.distributed import WorkerManager, DistributedResultAggregator

# Initialize aggregator
result_aggregator = DistributedResultAggregator()


def pytest_configure(config):
    '''Configure distributed testing.'''
    config.worker_manager = WorkerManager()
    config.result_aggregator = result_aggregator


@pytest.fixture(scope="session", autouse=True)
def setup_worker(request):
    '''Setup worker environment.'''
    worker_id = WorkerManager.get_worker_id()
    
    if worker_id:
        print(f"Setting up worker: {worker_id}")
        
        # Worker-specific setup
        # e.g., separate database, separate log files
        
        yield
        
        print(f"Tearing down worker: {worker_id}")
    else:
        yield


@pytest.fixture
def worker_info():
    '''Get worker information in tests.'''
    return WorkerManager.get_worker_info()


def pytest_sessionfinish(session, exitstatus):
    '''Aggregate results at session end.'''
    if hasattr(session.config, 'workerinput'):
        # Running in worker
        worker_id = WorkerManager.get_worker_id()
        
        result = {
            "passed": session.testscollected - session.testsfailed,
            "failed": session.testsfailed,
            "skipped": 0  # Add skipped count if needed
        }
        
        result_aggregator.add_worker_result(worker_id, result)
    else:
        # Main process
        summary = result_aggregator.get_summary()
        print(f"\\nDistributed Test Summary:")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['total_passed']}")
        print(f"Failed: {summary['total_failed']}")
        print(f"Workers: {summary['num_workers']}")
"""
