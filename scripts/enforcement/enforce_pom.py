#!/usr/bin/env python3
"""
POM Enforcement Linter
Automated detection of Page Object Model violations

Usage:
    python enforce_pom.py                 # Check all files
    python enforce_pom.py pages/bookslot  # Check specific directory
    python enforce_pom.py --fix           # Auto-fix violations (where possible)
    python enforce_pom.py --strict        # Fail on warnings too
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class POMViolation:
    """Represents a POM compliance violation"""
    file: str
    line: int
    rule: str
    message: str
    severity: str  # ERROR, WARNING, INFO
    
    def __str__(self):
        icon = "❌" if self.severity == "ERROR" else "⚠️" if self.severity == "WARNING" else "ℹ️"
        return f"{icon} {self.file}:{self.line} [{self.rule}] {self.message}"


class POMEnforcer:
    """Enforces Page Object Model architectural rules"""
    
    # Patterns forbidden in Page Objects
    FORBIDDEN_IN_PAGES = {
        'pytest_import': (
            r'(?:^|\n)\s*(?:import pytest|from pytest)',
            "Page Objects must not import pytest"
        ),
        'assert_statement': (
            r'(?:^|\s)assert\s+\w',
            "Page Objects must not contain assertions - return data instead"
        ),
        'time_sleep': (
            r'time\.sleep\(',
            "No explicit sleeps - use Playwright's auto-waiting"
        ),
        'hardcoded_wait': (
            r'wait_for_timeout\(\d+\)',
            "No magic wait numbers - use condition-based waits or Playwright auto-wait"
        ),
        'api_call': (
            r'(?:requests\.|httpx\.|urllib\.request)',
            "Page Objects should not make API calls"
        ),
        'db_call': (
            r'(?:cursor\.execute|conn\.execute|session\.query)',
            "Page Objects should not make database calls"
        ),
    }
    
    # Patterns required in Page Objects
    REQUIRED_IN_PAGES = {
        'class_definition': (
            r'class\s+\w+Page',
            "Page Object must have a class ending with 'Page'"
        ),
        'constructor_with_page': (
            r'def __init__\(self,\s*(?:page|driver)',
            "Constructor must accept page/driver as parameter"
        ),
    }
    
    # Patterns forbidden in Tests
    FORBIDDEN_IN_TESTS = {
        'direct_page_locator': (
            r'page\.(?:locator|get_by_role|get_by_text|get_by_label|get_by_placeholder)\(',
            "Tests must use Page Objects, not direct page.locator() calls"
        ),
        'direct_driver_find': (
            r'driver\.find_element',
            "Tests must use Page Objects, not direct driver.find_element() calls"
        ),
    }
    
    # Patterns required in Tests
    REQUIRED_IN_TESTS = {
        'page_import': (
            r'from pages\.\w+',
            "Tests should import Page Objects from pages/"
        ),
        'pytest_marker': (
            r'@pytest\.mark\.\w+',
            "Tests should have pytest markers (project, module, etc.)"
        ),
    }
    
    def __init__(self, strict: bool = False, fix: bool = False):
        self.strict = strict
        self.fix = fix
        self.violations: List[POMViolation] = []
    
    def check_page_object(self, file_path: Path) -> List[POMViolation]:
        """Check a page object file for violations"""
        violations = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check for forbidden patterns
            for rule_name, (pattern, message) in self.FORBIDDEN_IN_PAGES.items():
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line):
                        if not self._is_in_comment(line) and not self._is_in_docstring(lines, i):
                            violations.append(POMViolation(
                                file=str(file_path.relative_to(Path.cwd())),
                                line=i,
                                rule=rule_name,
                                message=message,
                                severity="ERROR"
                            ))
            
            # Check for required patterns
            for rule_name, (pattern, message) in self.REQUIRED_IN_PAGES.items():
                if not re.search(pattern, content, re.MULTILINE):
                    violations.append(POMViolation(
                        file=str(file_path.relative_to(Path.cwd())),
                        line=1,
                        rule=rule_name,
                        message=message,
                        severity="WARNING"
                    ))
        
        except Exception as e:
            print(f"⚠️  Error checking {file_path}: {e}")
        
        return violations
    
    def check_test_file(self, file_path: Path) -> List[POMViolation]:
        """Check a test file for violations"""
        violations = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check for forbidden patterns
            for rule_name, (pattern, message) in self.FORBIDDEN_IN_TESTS.items():
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line):
                        # Skip if in comment, fixture, or conftest
                        if (not self._is_in_comment(line) and 
                            not self._is_in_fixture(lines, i) and
                            'conftest.py' not in str(file_path)):
                            violations.append(POMViolation(
                                file=str(file_path.relative_to(Path.cwd())),
                                line=i,
                                rule=rule_name,
                                message=message,
                                severity="ERROR"
                            ))
            
            # Check for required patterns (warnings only)
            for rule_name, (pattern, message) in self.REQUIRED_IN_TESTS.items():
                if not re.search(pattern, content, re.MULTILINE):
                    violations.append(POMViolation(
                        file=str(file_path.relative_to(Path.cwd())),
                        line=1,
                        rule=rule_name,
                        message=message,
                        severity="INFO"
                    ))
        
        except Exception as e:
            print(f"⚠️  Error checking {file_path}: {e}")
        
        return violations
    
    def _is_in_comment(self, line: str) -> bool:
        """Check if line is a comment"""
        stripped = line.strip()
        return stripped.startswith('#') or stripped.startswith('//')
    
    def _is_in_docstring(self, lines: List[str], line_num: int) -> bool:
        """Check if line is inside a docstring"""
        # Simple check: look for triple quotes
        in_docstring = False
        for i in range(0, line_num):
            if '"""' in lines[i] or "'''" in lines[i]:
                in_docstring = not in_docstring
        return in_docstring
    
    def _is_in_fixture(self, lines: List[str], line_num: int) -> bool:
        """Check if line is inside a pytest fixture"""
        # Look backwards for @pytest.fixture
        for i in range(max(0, line_num - 30), line_num):
            if '@pytest.fixture' in lines[i]:
                return True
        return False
    
    def check_directory(self, directory: Path) -> None:
        """Check all Python files in directory"""
        print(f"🔍 Checking directory: {directory}")
        
        # Check page objects
        page_files = list(directory.glob('pages/**/*.py'))
        page_files = [f for f in page_files if f.name != '__init__.py']
        
        if page_files:
            print(f"\n📄 Checking {len(page_files)} page object files...")
            for page_file in page_files:
                violations = self.check_page_object(page_file)
                self.violations.extend(violations)
        
        # Check tests
        test_files = list(directory.glob('tests/**/*.py'))
        test_files = [f for f in test_files if f.name.startswith('test_') or f.name.endswith('_test.py')]
        
        if test_files:
            print(f"📄 Checking {len(test_files)} test files...")
            for test_file in test_files:
                violations = self.check_test_file(test_file)
                self.violations.extend(violations)
    
    def report(self) -> int:
        """Print violations and return error count"""
        if not self.violations:
            print("\n✅ No POM violations detected!")
            print("✅ Framework is POM compliant")
            return 0
        
        # Group by severity
        errors = [v for v in self.violations if v.severity == "ERROR"]
        warnings = [v for v in self.violations if v.severity == "WARNING"]
        infos = [v for v in self.violations if v.severity == "INFO"]
        
        print(f"\n{'='*80}")
        print(f"🚨 POM VIOLATIONS DETECTED")
        print(f"{'='*80}\n")
        print(f"Errors:   {len(errors)}")
        print(f"Warnings: {len(warnings)}")
        print(f"Info:     {len(infos)}\n")
        
        if errors:
            print("❌ ERRORS (Must Fix Before Commit):")
            print("-" * 80)
            for v in errors:
                print(f"  {v}")
            print()
        
        if warnings:
            print("⚠️  WARNINGS (Should Fix):")
            print("-" * 80)
            for v in warnings:
                print(f"  {v}")
            print()
        
        if infos:
            print("ℹ️  INFO (Best Practice Suggestions):")
            print("-" * 80)
            for v in infos:
                print(f"  {v}")
            print()
        
        # Return error count (or include warnings if strict)
        fail_count = len(errors)
        if self.strict:
            fail_count += len(warnings)
        
        if fail_count > 0:
            print(f"{'='*80}")
            print(f"❌ FAIL: {fail_count} violations must be fixed")
            print(f"{'='*80}\n")
        
        return fail_count


def main():
    parser = argparse.ArgumentParser(description="POM Enforcement Linter")
    parser.add_argument('directory', nargs='?', default='.', help='Directory to check (default: current)')
    parser.add_argument('--strict', action='store_true', help='Fail on warnings too')
    parser.add_argument('--fix', action='store_true', help='Auto-fix violations where possible (not implemented yet)')
    
    args = parser.parse_args()
    
    directory = Path(args.directory).resolve()
    if not directory.exists():
        print(f"❌ Error: Directory not found: {directory}")
        sys.exit(1)
    
    print("=" * 80)
    print("🛡️  POM ENFORCEMENT LINTER")
    print("=" * 80)
    
    enforcer = POMEnforcer(strict=args.strict, fix=args.fix)
    enforcer.check_directory(directory)
    
    error_count = enforcer.report()
    
    if error_count > 0:
        print("💡 See POM_ENFORCEMENT_CHECKLIST.md for correct patterns")
        sys.exit(1)
    else:
        print("🎉 All checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
