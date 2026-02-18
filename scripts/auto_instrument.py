"""
Auto-Instrumentation Script
============================

Automatically adds logging decorators to Python files that need instrumentation.

Features:
- Detects functions without logging decorators
- Adds appropriate decorators (@log_function or @log_async_function)
- Preserves existing code structure and formatting
- Creates backup before modification
- Handles both sync and async functions

Usage:
    python scripts/auto_instrument.py --target pages/
    python scripts/auto_instrument.py --file pages/bookslot/specific_file.py
    python scripts/auto_instrument.py --all

Author: Lokendra Singh
"""

import argparse
import ast
import os
import re
import shutil
from pathlib import Path
from typing import List, Set, Tuple


class FunctionInstrumentor:
    """Automatically instrument Python files with logging decorators"""

    def __init__(self, dry_run: bool = False):
        """
        Initialize instrumentor

        Args:
            dry_run: If True, only show what would be done without actually modifying files
        """
        self.dry_run = dry_run
        self.files_modified = 0
        self.functions_instrumented = 0

    def instrument_file(self, file_path: Path) -> bool:
        """
        Instrument a single file

        Args:
            file_path: Path to Python file

        Returns:
            True if file was modified, False otherwise
        """
        print(f"\n📄 Analyzing: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if file already imports logging decorators
        has_log_import = "from framework.observability import" in content

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"   ⚠️  Syntax error, skipping: {e}")
            return False

        # Find functions that need decoration
        analyzer = FunctionAnalyzer()
        analyzer.visit(tree)

        if not analyzer.undecorated_functions and not analyzer.undecorated_async_functions:
            print("   ✓ All functions already decorated")
            return False

        print(
            f"   Found {len(analyzer.undecorated_functions)} sync "
            f"and {len(analyzer.undecorated_async_functions)} async functions to instrument"
        )

        if self.dry_run:
            print("   [DRY RUN] Would add decorators to:")
            for func_name in analyzer.undecorated_functions:
                print(f"      • {func_name} (@log_function)")
            for func_name in analyzer.undecorated_async_functions:
                print(f"      • {func_name} (@log_async_function)")
            return False

        # Backup original file
        backup_path = file_path.with_suffix(".py.bak")
        shutil.copy2(file_path, backup_path)
        print(f"   💾 Backup created: {backup_path}")

        # Add import if needed
        if not has_log_import:
            content = self._add_logging_import(content)
            print("   ✓ Added logging imports")

        # Add decorators to functions
        for func_name in analyzer.undecorated_functions:
            content = self._add_decorator(content, func_name, "@log_function(log_timing=True)")
            self.functions_instrumented += 1

        for func_name in analyzer.undecorated_async_functions:
            content = self._add_decorator(
                content, func_name, "@log_async_function(log_timing=True)"
            )
            self.functions_instrumented += 1

        # Write instrumented content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"   ✅ Instrumented {len(analyzer.undecorated_functions) + len(analyzer.undecorated_async_functions)} functions")
        self.files_modified += 1
        return True

    def _add_logging_import(self, content: str) -> str:
        """Add logging decorator imports to file"""
        lines = content.split("\n")

        # Find where to insert import (after existing imports)
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_index = i + 1
            elif line.strip() and insert_index > 0:
                # Found first non-import line after imports
                break

        # Insert the import
        lines.insert(
            insert_index,
            "from framework.observability import log_function, log_async_function",
        )

        return "\n".join(lines)

    def _add_decorator(self, content: str, func_name: str, decorator: str) -> str:
        """Add decorator to a specific function"""
        lines = content.split("\n")

        # Find function definition
        for i, line in enumerate(lines):
            # Match function definition (both def and async def)
            if re.match(rf"\s*(async\s+)?def\s+{re.escape(func_name)}\s*\(", line):
                # Get indentation
                indent = len(line) - len(line.lstrip())

                # Check if already has a decorator on previous line
                if i > 0 and "@" in lines[i - 1]:
                    continue

                # Add decorator with same indentation
                lines.insert(i, " " * indent + decorator)
                break

        return "\n".join(lines)

    def instrument_directory(self, dir_path: Path, recursive: bool = True) -> None:
        """
        Instrument all Python files in a directory

        Args:
            dir_path: Directory path
            recursive: If True, scan subdirectories recursively
        """
        pattern = "**/*.py" if recursive else "*.py"

        for py_file in dir_path.glob(pattern):
            # Skip __init__.py and __pycache__
            if py_file.name == "__init__.py" or "__pycache__" in str(py_file):
                continue

            self.instrument_file(py_file)

    def generate_summary(self) -> str:
        """Generate summary report"""
        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("AUTO-INSTRUMENTATION SUMMARY")
        lines.append("=" * 70)
        lines.append(f"Files Modified: {self.files_modified}")
        lines.append(f"Functions Instrumented: {self.functions_instrumented}")
        lines.append("=" * 70)
        return "\n".join(lines)


class FunctionAnalyzer(ast.NodeVisitor):
    """Analyze Python file to find undecorated functions"""

    def __init__(self):
        self.undecorated_functions = []
        self.undecorated_async_functions = []

    def visit_FunctionDef(self, node):
        """Visit function definition"""
        # Skip private methods and properties
        if node.name.startswith("_") or self._is_property(node):
            return

        # Check if already decorated with logging decorator
        if not self._has_logging_decorator(node):
            self.undecorated_functions.append(node.name)

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Visit async function definition"""
        # Skip private methods
        if node.name.startswith("_"):
            return

        # Check if already decorated with logging decorator
        if not self._has_logging_decorator(node):
            self.undecorated_async_functions.append(node.name)

        self.generic_visit(node)

    def _has_logging_decorator(self, node) -> bool:
        """Check if function has any logging decorator"""
        for decorator in node.decorator_list:
            decorator_name = self._get_decorator_name(decorator)
            if any(
                log_dec in decorator_name
                for log_dec in ["log_function", "log_async", "log_state", "log_retry"]
            ):
                return True
        return False

    def _is_property(self, node) -> bool:
        """Check if function is a property"""
        for decorator in node.decorator_list:
            decorator_name = self._get_decorator_name(decorator)
            if decorator_name == "property":
                return True
        return False

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
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Auto-instrument Python files with logging")
    parser.add_argument("--file", type=str, help="Instrument a specific file")
    parser.add_argument("--target", type=str, help="Instrument all files in directory")
    parser.add_argument(
        "--all", action="store_true", help="Instrument pages/, framework/, tests/"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without modifying files",
    )

    args = parser.parse_args()

    instrumentor = FunctionInstrumentor(dry_run=args.dry_run)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")

    if args.file:
        # Instrument single file
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return
        instrumentor.instrument_file(file_path)

    elif args.target:
        # Instrument directory
        dir_path = Path(args.target)
        if not dir_path.exists():
            print(f"❌ Directory not found: {dir_path}")
            return
        instrumentor.instrument_directory(dir_path, recursive=True)

    elif args.all:
        # Instrument key directories
        root = Path(__file__).parent.parent
        for target in ["pages", "framework/core", "framework/ui"]:
            target_path = root / target
            if target_path.exists():
                print(f"\n📁 Instrumenting {target}/")
                instrumentor.instrument_directory(target_path, recursive=True)

    else:
        parser.print_help()
        return

    # Print summary
    print(instrumentor.generate_summary())


if __name__ == "__main__":
    main()
