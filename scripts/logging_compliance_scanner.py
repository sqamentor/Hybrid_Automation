"""
Logging Compliance Scanner
==========================

Analyzes codebase to verify enterprise logging implementation compliance.

Features:
- Scans all Python files for logging decorator usage
- Identifies silent exception handlers
- Reports on logging coverage per module
- Generates compliance scores
- Creates actionable recommendations

Author: Lokendra Singh
Email: lokendra.singh@centerforvein.com
Website: www.centerforvein.com
"""

import ast
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class FileAnalysis:
    """Analysis results for a single file"""

    file_path: str
    total_functions: int
    logged_functions: int
    async_functions: int
    logged_async_functions: int
    exception_handlers: int
    logged_exceptions: int
    silent_exceptions: List[int]  # Line numbers
    missing_decorators: List[str]  # Function names
    compliance_score: float


@dataclass
class ModuleAnalysis:
    """Analysis results for a module/directory"""

    module_name: str
    total_files: int
    total_functions: int
    logged_functions: int
    exception_handlers: int
    logged_exceptions: int
    compliance_score: float
    files: List[FileAnalysis]


class LoggingComplianceScanner:
    """Scanner for analyzing logging compliance across codebase"""

    def __init__(self, root_dir: str, exclude_dirs: List[str] = None):
        """
        Initialize scanner

        Args:
            root_dir: Root directory to scan
            exclude_dirs: List of directory names to exclude
        """
        self.root_dir = Path(root_dir)
        self.exclude_dirs = exclude_dirs or [
            "__pycache__",
            ".git",
            "venv",
            ".venv",
            "node_modules",
            ".pytest_cache",
            "allure-results",
            "reports",
            "logs",
        ]

        self.logging_decorators = {
            "log_function",
            "log_async_function",
            "log_state_transition",
            "log_retry_operation",
        }

        self.logger_methods = {
            "logger.debug",
            "logger.info",
            "logger.warning",
            "logger.error",
            "logger.critical",
            "logger.exception",
        }

    def scan(self) -> Dict[str, ModuleAnalysis]:
        """
        Scan entire codebase

        Returns:
            Dictionary mapping module name to ModuleAnalysis
        """
        results = {}

        # Scan key directories
        key_dirs = ["framework", "pages", "tests", "utils"]

        for dir_name in key_dirs:
            dir_path = self.root_dir / dir_name
            if dir_path.exists():
                analysis = self.scan_module(dir_path)
                results[dir_name] = analysis

        return results

    def scan_module(self, module_path: Path) -> ModuleAnalysis:
        """Scan a module directory"""
        file_analyses = []

        for py_file in module_path.rglob("*.py"):
            # Skip excluded directories
            if any(excluded in str(py_file) for excluded in self.exclude_dirs):
                continue

            # Skip __init__.py files
            if py_file.name == "__init__.py":
                continue

            try:
                analysis = self.analyze_file(py_file)
                file_analyses.append(analysis)
            except Exception as e:
                print(f"Error analyzing {py_file}: {e}")

        # Calculate module metrics
        total_functions = sum(f.total_functions for f in file_analyses)
        logged_functions = sum(f.logged_functions for f in file_analyses)
        exception_handlers = sum(f.exception_handlers for f in file_analyses)
        logged_exceptions = sum(f.logged_exceptions for f in file_analyses)

        compliance_score = 0.0
        if total_functions > 0:
            function_coverage = (logged_functions / total_functions) * 60
            exception_coverage = (
                (logged_exceptions / exception_handlers) * 40
                if exception_handlers > 0
                else 40
            )
            compliance_score = function_coverage + exception_coverage

        return ModuleAnalysis(
            module_name=module_path.name,
            total_files=len(file_analyses),
            total_functions=total_functions,
            logged_functions=logged_functions,
            exception_handlers=exception_handlers,
            logged_exceptions=logged_exceptions,
            compliance_score=compliance_score,
            files=file_analyses,
        )

    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a single Python file"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            # Return empty analysis for unparseable files
            return FileAnalysis(
                file_path=str(file_path),
                total_functions=0,
                logged_functions=0,
                async_functions=0,
                logged_async_functions=0,
                exception_handlers=0,
                logged_exceptions=0,
                silent_exceptions=[],
                missing_decorators=[],
                compliance_score=0.0,
            )

        visitor = FunctionVisitor()
        visitor.visit(tree)

        # Analyze exception handlers
        exception_info = self.analyze_exceptions(content)

        # Calculate compliance
        total_funcs = len(visitor.functions)
        logged_funcs = len(visitor.decorated_functions)
        async_funcs = len(visitor.async_functions)
        logged_async = len(visitor.decorated_async_functions)

        function_score = (logged_funcs / total_funcs * 100) if total_funcs > 0 else 100
        exception_score = (
            (exception_info["logged"] / exception_info["total"] * 100)
            if exception_info["total"] > 0
            else 100
        )

        compliance_score = (function_score * 0.6) + (exception_score * 0.4)

        # Find missing decorators
        missing_decorators = [
            func
            for func in visitor.functions
            if func not in visitor.decorated_functions
        ]

        return FileAnalysis(
            file_path=str(file_path.relative_to(self.root_dir)),
            total_functions=total_funcs,
            logged_functions=logged_funcs,
            async_functions=async_funcs,
            logged_async_functions=logged_async,
            exception_handlers=exception_info["total"],
            logged_exceptions=exception_info["logged"],
            silent_exceptions=exception_info["silent_lines"],
            missing_decorators=missing_decorators,
            compliance_score=compliance_score,
        )

    def analyze_exceptions(self, content: str) -> Dict:
        """Analyze exception handling in code"""
        lines = content.split("\n")
        total_handlers = 0
        logged_handlers = 0
        silent_lines = []

        for i, line in enumerate(lines, start=1):
            # Find except blocks
            if re.match(r"\s*except", line):
                total_handlers += 1

                # Check if logging exists in next 10 lines
                has_logging = False
                for j in range(i, min(i + 10, len(lines))):
                    if any(method in lines[j] for method in self.logger_methods):
                        has_logging = True
                        break
                    if re.match(r"\s*except", lines[j]) and j != i:
                        # Reached next except block
                        break
                    if re.match(r"\s*def ", lines[j]):
                        # Reached next function
                        break

                if has_logging:
                    logged_handlers += 1
                else:
                    silent_lines.append(i)

        return {
            "total": total_handlers,
            "logged": logged_handlers,
            "silent_lines": silent_lines,
        }

    def generate_report(self, results: Dict[str, ModuleAnalysis]) -> str:
        """Generate compliance report"""
        report = []
        report.append("=" * 80)
        report.append("ENTERPRISE LOGGING COMPLIANCE REPORT")
        report.append("=" * 80)
        report.append("")

        # Overall statistics
        total_funcs = sum(m.total_functions for m in results.values())
        logged_funcs = sum(m.logged_functions for m in results.values())
        total_exceptions = sum(m.exception_handlers for m in results.values())
        logged_exceptions = sum(m.logged_exceptions for m in results.values())

        overall_score = (
            (logged_funcs / total_funcs * 60 + logged_exceptions / total_exceptions * 40)
            if total_funcs > 0
            else 0
        )

        report.append(f"Overall Compliance Score: {overall_score:.1f}%")
        report.append(f"Total Functions: {total_funcs}")
        report.append(f"Logged Functions: {logged_funcs} ({logged_funcs/total_funcs*100:.1f}%)")
        report.append(f"Total Exception Handlers: {total_exceptions}")
        report.append(
            f"Logged Exception Handlers: {logged_exceptions} "
            f"({logged_exceptions/total_exceptions*100:.1f}% if total_exceptions > 0 else 100)"
        )
        report.append("")

        # Module breakdown
        report.append("-" * 80)
        report.append("MODULE BREAKDOWN")
        report.append("-" * 80)
        report.append("")

        for module_name, analysis in sorted(results.items()):
            report.append(f"📁 {module_name}/")
            report.append(f"   Compliance: {analysis.compliance_score:.1f}%")
            report.append(f"   Files: {analysis.total_files}")
            report.append(
                f"   Functions: {analysis.logged_functions}/{analysis.total_functions}"
            )
            report.append(
                f"   Exception Handlers: {analysis.logged_exceptions}/{analysis.exception_handlers}"
            )
            report.append("")

            # Top 5 files needing attention
            files_need_work = sorted(
                [f for f in analysis.files if f.compliance_score < 80],
                key=lambda x: x.compliance_score,
            )[:5]

            if files_need_work:
                report.append(f"   ⚠️  Files Needing Attention:")
                for file in files_need_work:
                    report.append(
                        f"      • {file.file_path} ({file.compliance_score:.1f}%)"
                    )
                    if file.missing_decorators:
                        report.append(
                            f"        Missing decorators: {len(file.missing_decorators)} functions"
                        )
                    if file.silent_exceptions:
                        report.append(
                            f"        Silent exceptions: {len(file.silent_exceptions)} handlers"
                        )
                report.append("")

        # Recommendations
        report.append("-" * 80)
        report.append("RECOMMENDATIONS")
        report.append("-" * 80)
        report.append("")

        if overall_score < 60:
            report.append("🔴 CRITICAL: Logging coverage is below 60%")
            report.append("   Action: Immediate decorator rollout required")
        elif overall_score < 80:
            report.append("🟡 WARNING: Logging coverage is below 80%")
            report.append("   Action: Prioritize high-traffic modules")
        else:
            report.append("🟢 GOOD: Logging coverage is above 80%")
            report.append("   Action: Focus on remaining gaps")

        report.append("")
        report.append("Next Steps:")
        report.append("1. Add @log_function to all public methods in low-coverage files")
        report.append("2. Add @log_async_function to async methods")
        report.append("3. Add logging to all silent exception handlers")
        report.append("4. Run scanner weekly to track progress")
        report.append("")

        return "\n".join(report)


class FunctionVisitor(ast.NodeVisitor):
    """AST visitor to find functions and their decorators"""

    def __init__(self):
        self.functions = []
        self.decorated_functions = []
        self.async_functions = []
        self.decorated_async_functions = []

    def visit_FunctionDef(self, node):
        """Visit function definition"""
        # Skip private methods (starting with _)
        if not node.name.startswith("_"):
            self.functions.append(node.name)

            # Check for logging decorators
            for decorator in node.decorator_list:
                decorator_name = self._get_decorator_name(decorator)
                if any(
                    log_dec in decorator_name
                    for log_dec in ["log_function", "log_async", "log_state", "log_retry"]
                ):
                    self.decorated_functions.append(node.name)
                    break

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Visit async function definition"""
        if not node.name.startswith("_"):
            self.async_functions.append(node.name)

            # Check for logging decorators
            for decorator in node.decorator_list:
                decorator_name = self._get_decorator_name(decorator)
                if "log_async" in decorator_name or "log_function" in decorator_name:
                    self.decorated_async_functions.append(node.name)
                    break

        self.generic_visit(node)

    def _get_decorator_name(self, decorator) -> str:
        """Extract decorator name from AST node"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr
        return ""


def main():
    """Run compliance scanner"""
    scanner = LoggingComplianceScanner(
        root_dir=Path(__file__).parent.parent,
        exclude_dirs=[
            "__pycache__",
            ".git",
            "venv",
            ".venv",
            "allure-results",
            "reports",
            "logs",
            "artifacts",
            "recorded_tests",
            "traces",
            "screenshots",
            "videos",
        ],
    )

    print("🔍 Scanning codebase for logging compliance...")
    print()

    results = scanner.scan()
    report = scanner.generate_report(results)

    print(report)

    # Save report to file
    report_file = Path(__file__).parent.parent / "LOGGING_COMPLIANCE_REPORT.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print()
    print(f"📄 Report saved to: {report_file}")


if __name__ == "__main__":
    main()
