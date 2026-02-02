"""
ML Test Optimization - Machine Learning for Test Selection & Prioritization

Uses historical test data to predict test failures and optimize test execution order.
"""

import json
import os
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from utils.logger import get_logger

logger = get_logger(__name__)


class MLTestOptimizer:
    """ML-based test optimization engine"""

    def __init__(self, history_file: str = "reports/test_history.json"):
        """
        Initialize ML test optimizer

        Args:
            history_file: Path to test history file
        """
        self.history_file = history_file
        self.test_history: List[Dict] = []
        self.failure_patterns: Dict[str, Any] = {}
        self.load_history()

    def load_history(self):
        """Load test execution history"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    self.test_history = json.load(f)
                logger.info(f"Loaded {len(self.test_history)} historical test runs")
            except Exception as e:
                logger.warning(f"Could not load history: {e}")
                self.test_history = []
        else:
            self.test_history = []

    def save_history(self):
        """Save test execution history"""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, "w") as f:
            json.dump(self.test_history, f, indent=2)
        logger.debug("Test history saved")

    def record_test_result(
        self,
        test_name: str,
        passed: bool,
        duration: float,
        error: Optional[str] = None,
        changed_files: Optional[List[str]] = None,
    ):
        """
        Record test execution result

        Args:
            test_name: Test name
            passed: Whether test passed
            duration: Test duration in seconds
            error: Error message if failed
            changed_files: List of changed files since last run
        """
        result = {
            "test_name": test_name,
            "passed": passed,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "changed_files": changed_files or [],
        }

        self.test_history.append(result)
        self.save_history()

    def analyze_failure_patterns(self):
        """Analyze historical data to find failure patterns"""
        failure_counts = defaultdict(int)
        total_runs = defaultdict(int)
        failure_context = defaultdict(list)

        for result in self.test_history:
            test_name = result["test_name"]
            total_runs[test_name] += 1

            if not result["passed"]:
                failure_counts[test_name] += 1
                failure_context[test_name].append(
                    {
                        "timestamp": result["timestamp"],
                        "error": result.get("error"),
                        "changed_files": result.get("changed_files", []),
                    }
                )

        # Calculate failure rates
        self.failure_patterns = {}
        for test_name in total_runs:
            failure_rate = failure_counts[test_name] / total_runs[test_name]
            self.failure_patterns[test_name] = {
                "failure_rate": failure_rate,
                "total_runs": total_runs[test_name],
                "total_failures": failure_counts[test_name],
                "recent_failures": failure_context[test_name][-5:],  # Last 5 failures
                "flakiness_score": self._calculate_flakiness(test_name),
            }

        logger.info(f"Analyzed {len(self.failure_patterns)} test patterns")
        return self.failure_patterns

    def _calculate_flakiness(self, test_name: str) -> float:
        """
        Calculate test flakiness score (0-1)

        A flaky test alternates between pass/fail without code changes.
        """
        recent_results = [
            r for r in self.test_history[-20:] if r["test_name"] == test_name  # Last 20 runs
        ]

        if len(recent_results) < 5:
            return 0.0

        # Count transitions between pass/fail
        transitions = 0
        for i in range(1, len(recent_results)):
            if recent_results[i]["passed"] != recent_results[i - 1]["passed"]:
                transitions += 1

        # Normalize: more transitions = more flaky
        flakiness = transitions / (len(recent_results) - 1)
        return flakiness

    def predict_failure_probability(
        self, test_name: str, changed_files: Optional[List[str]] = None
    ) -> float:
        """
        Predict probability of test failure (0-1)

        Args:
            test_name: Test name
            changed_files: Files changed since last run

        Returns:
            Failure probability
        """
        if not self.failure_patterns:
            self.analyze_failure_patterns()

        if test_name not in self.failure_patterns:
            return 0.5  # Unknown test, assume moderate risk

        pattern = self.failure_patterns[test_name]

        # Base probability from historical failure rate
        base_prob = pattern["failure_rate"]

        # Adjust for flakiness
        flakiness_weight = pattern["flakiness_score"] * 0.3

        # Adjust for changed files
        file_impact = 0.0
        if changed_files:
            # Check if any changed files were involved in previous failures
            recent_failures = pattern["recent_failures"]
            for failure in recent_failures:
                failed_with_files = failure.get("changed_files", [])
                if any(f in failed_with_files for f in changed_files):
                    file_impact += 0.2

        # Combine factors
        probability = min(1.0, base_prob + flakiness_weight + file_impact)

        return probability

    def get_optimal_test_order(
        self, test_names: List[str], changed_files: Optional[List[str]] = None
    ) -> List[Tuple[str, float]]:
        """
        Get optimal test execution order

        Strategy: Run tests most likely to fail first (fail-fast)

        Args:
            test_names: List of tests to order
            changed_files: Files changed since last run

        Returns:
            List of (test_name, failure_probability) tuples, sorted by priority
        """
        test_priorities = []

        for test_name in test_names:
            probability = self.predict_failure_probability(test_name, changed_files)
            test_priorities.append((test_name, probability))

        # Sort by failure probability (descending)
        test_priorities.sort(key=lambda x: x[1], reverse=True)

        logger.info(f"Optimized test order for {len(test_names)} tests")
        return test_priorities

    def get_recommended_tests(self, changed_files: List[str], max_tests: int = 10) -> List[str]:
        """
        Get recommended tests to run based on changed files

        Args:
            changed_files: List of changed files
            max_tests: Maximum number of tests to recommend

        Returns:
            List of recommended test names
        """
        if not self.failure_patterns:
            self.analyze_failure_patterns()

        # Find tests that historically failed with these files
        relevant_tests = []

        for test_name, pattern in self.failure_patterns.items():
            relevance_score = 0.0

            for failure in pattern["recent_failures"]:
                failed_with_files = failure.get("changed_files", [])
                # Check file overlap
                overlap = len(set(changed_files) & set(failed_with_files))
                if overlap > 0:
                    relevance_score += overlap / len(changed_files)

            if relevance_score > 0:
                relevant_tests.append((test_name, relevance_score))

        # Sort by relevance
        relevant_tests.sort(key=lambda x: x[1], reverse=True)

        recommended = [test for test, score in relevant_tests[:max_tests]]

        logger.info(f"Recommended {len(recommended)} tests based on changed files")
        return recommended

    def get_flaky_tests(self, threshold: float = 0.3) -> List[str]:
        """
        Get list of flaky tests

        Args:
            threshold: Flakiness score threshold (0-1)

        Returns:
            List of flaky test names
        """
        if not self.failure_patterns:
            self.analyze_failure_patterns()

        flaky = [
            test_name
            for test_name, pattern in self.failure_patterns.items()
            if pattern["flakiness_score"] >= threshold
        ]

        logger.info(f"Found {len(flaky)} flaky tests (threshold: {threshold})")
        return flaky

    def get_slow_tests(self, percentile: int = 90) -> List[Tuple[str, float]]:
        """
        Get slowest tests

        Args:
            percentile: Percentile threshold

        Returns:
            List of (test_name, avg_duration) tuples
        """
        test_durations = defaultdict(list)

        for result in self.test_history:
            test_durations[result["test_name"]].append(result["duration"])

        # Calculate average duration
        avg_durations = []
        for test_name, durations in test_durations.items():
            avg_duration = sum(durations) / len(durations)
            avg_durations.append((test_name, avg_duration))

        # Sort by duration
        avg_durations.sort(key=lambda x: x[1], reverse=True)

        # Get top percentile
        cutoff = int(len(avg_durations) * (100 - percentile) / 100)
        slow_tests = avg_durations[:cutoff] if cutoff > 0 else avg_durations

        logger.info(f"Found {len(slow_tests)} slow tests (>{percentile}th percentile)")
        return slow_tests

    def generate_insights_report(self, output_path: str = "reports/ml_insights.json"):
        """Generate ML insights report"""
        if not self.failure_patterns:
            self.analyze_failure_patterns()

        insights = {
            "total_test_history": len(self.test_history),
            "unique_tests": len(self.failure_patterns),
            "flaky_tests": len(self.get_flaky_tests()),
            "high_failure_rate_tests": [
                {"test": name, "rate": pattern["failure_rate"]}
                for name, pattern in self.failure_patterns.items()
                if pattern["failure_rate"] > 0.2
            ],
            "flaky_test_details": [
                {"test": name, "flakiness": pattern["flakiness_score"]}
                for name, pattern in self.failure_patterns.items()
                if pattern["flakiness_score"] > 0.3
            ],
            "slow_tests": [
                {"test": name, "avg_duration": duration}
                for name, duration in self.get_slow_tests(90)
            ],
            "generated_at": datetime.now().isoformat(),
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(insights, f, indent=2)

        logger.info(f"ML insights report generated: {output_path}")
        return insights


__all__ = ["MLTestOptimizer"]
