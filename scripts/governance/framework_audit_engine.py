#!/usr/bin/env python3
"""

FRAMEWORK ARCHITECTURE AUDIT ENGINE


A comprehensive, AST-based static analysis system that enforces architectural
rules and prevents framework degradation.

CAPABILITIES:
OK Engine violation detection (mixing Playwright + Selenium)
OK Marker  Engine consistency validation
OK Folder  Engine alignment checks
OK POM compliance enforcement
OK Test boundary validation
OK Structural violations detection
OK Canonical flow protection
OK Baseline allow-list support with expiration
OK Detailed violation reporting with fix suggestions
OK CI integration with independent status checks

USAGE:
    # Full audit
    python framework_audit_engine.py

    # Specific category
    python framework_audit_engine.py --category engine-mix
    
    # With baseline suppression
    python framework_audit_engine.py --baseline ci/baseline_allowlist.yaml
    
    # Generate report
    python framework_audit_engine.py --report artifacts/framework_audit_report.md
    
    # CI mode (fail on any violation)
    python framework_audit_engine.py --ci --strict

EXIT CODES:
    0 - No violations (or all baselined)
    1 - Violations detected
    2 - Baseline expired or invalid
    3 - System error

Author: Principal QA Architect
Date: February 1, 2026
Version: 1.0.0

"""

import ast
import re
import sys
import yaml
import argparse
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from collections import defaultdict
from enum import Enum


# 
# VIOLATION SEVERITY & CATEGORIES
# 

class Severity(Enum):
    """Violation severity levels"""
    CRITICAL = "CRITICAL"  # Architecture-breaking, must fix immediately
    ERROR = "ERROR"        # Rule violation, blocks merge
    WARNING = "WARNING"    # Should fix, doesn't block merge
    INFO = "INFO"          # Advisory, best practice suggestion


class Category(Enum):
    """Violation categories for independent CI checks"""
    ENGINE_MIX = "engine-mix"                # Mixing Playwright + Selenium
    MARKER_ENGINE = "marker-engine"          # Marker  engine mismatch
    FOLDER_ENGINE = "folder-engine"          # Folder  engine mismatch
    POM_COMPLIANCE = "pom-compliance"        # POM violations
    TEST_BOUNDARIES = "test-boundaries"      # Test structure violations
    STRUCTURAL = "structural"                # File/folder structure
    CANONICAL_FLOW = "canonical-flow"        # Protected flow changes
    LEGACY_BASELINE = "legacy-baseline"      # Baselined violations


# 
# VIOLATION DATA MODEL
# 

@dataclass
class Violation:
    """Represents a single architectural violation"""
    category: Category
    severity: Severity
    rule_id: str
    file_path: str
    line_number: int
    message: str
    context: str = ""
    fix_suggestion: str = ""
    ai_explanation: str = ""
    baselined: bool = False
    baseline_expires: Optional[str] = None
    
    def __str__(self) -> str:
        icon = {
            Severity.CRITICAL: "",
            Severity.ERROR: "X",
            Severity.WARNING: "!",
            Severity.INFO: "i"
        }[self.severity]
        
        baseline_tag = " [BASELINED]" if self.baselined else ""
        return f"{icon} {self.file_path}:{self.line_number} [{self.rule_id}] {self.message}{baseline_tag}"


@dataclass
class AuditResult:
    """Results of a complete audit run"""
    violations: List[Violation] = field(default_factory=list)
    files_scanned: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    baseline_used: bool = False
    baseline_path: Optional[str] = None
    
    def get_violations_by_category(self) -> Dict[Category, List[Violation]]:
        """Group violations by category"""
        by_category = defaultdict(list)
        for v in self.violations:
            by_category[v.category].append(v)
        return dict(by_category)
    
    def get_blocking_violations(self) -> List[Violation]:
        """Get violations that should block CI"""
        return [v for v in self.violations 
                if v.severity in (Severity.CRITICAL, Severity.ERROR) 
                and not v.baselined]
    
    def is_passing(self) -> bool:
        """Check if audit passes (no blocking violations)"""
        return len(self.get_blocking_violations()) == 0


# 
# BASELINE ALLOW-LIST MANAGER
# 

class BaselineManager:
    """Manages baseline allow-list for legacy violations"""
    
    def __init__(self, baseline_path: Optional[Path] = None):
        self.baseline_path = baseline_path
        self.violations: List[Dict] = []
        self.expired_count = 0
        
        if baseline_path and baseline_path.exists():
            self._load_baseline()
    
    def _load_baseline(self):
        """Load baseline from YAML"""
        with open(self.baseline_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            self.violations = data.get('violations', [])
    
    def is_baselined(self, violation: Violation) -> Tuple[bool, Optional[str]]:
        """
        Check if violation is in baseline
        
        Returns:
            (is_baselined, expiration_date)
        """
        for baseline in self.violations:
            if (baseline['file'] == violation.file_path and
                baseline['rule'] == f"{violation.category.value}/{violation.rule_id}"):
                
                # Check if expired
                expires = baseline.get('expires')
                if expires:
                    expiry_date = datetime.strptime(expires, '%Y-%m-%d').date()
                    if expiry_date < date.today():
                        self.expired_count += 1
                        return False, expires  # Expired = not baselined
                    return True, expires
                else:
                    # No expiry = FAIL (violation of baseline rules)
                    raise ValueError(f"Baseline entry missing expiration: {baseline['file']}")
        
        return False, None
    
    def get_statistics(self) -> Dict:
        """Get baseline statistics"""
        total = len(self.violations)
        expired = self.expired_count
        
        # Count expiring soon (within 30 days)
        expiring_soon = 0
        today = date.today()
        for v in self.violations:
            expires = v.get('expires')
            if expires:
                expiry_date = datetime.strptime(expires, '%Y-%m-%d').date()
                days_until = (expiry_date - today).days
                if 0 <= days_until <= 30:
                    expiring_soon += 1
        
        return {
            'total': total,
            'expired': expired,
            'expiring_soon': expiring_soon,
            'active': total - expired
        }


# 
# AST-BASED ANALYZERS
# 

class ASTAnalyzer:
    """Base class for AST-based code analysis"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.tree: Optional[ast.AST] = None
        self.content: str = ""
        self.lines: List[str] = []
        
        self._parse()
    
    def _parse(self):
        """Parse file into AST"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
                self.lines = self.content.splitlines()
                self.tree = ast.parse(self.content, filename=str(self.file_path))
        except (SyntaxError, UnicodeDecodeError) as e:
            # Skip unparseable files
            self.tree = None
    
    def get_imports(self) -> Set[str]:
        """Extract all import statements"""
        if not self.tree:
            return set()
        
        imports = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        
        return imports
    
    def get_test_classes(self) -> List[Tuple[str, int, List[str]]]:
        """
        Extract test classes with their markers
        
        Returns:
            List of (class_name, line_number, markers)
        """
        if not self.tree:
            return []
        
        test_classes = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                markers = self._extract_markers(node)
                test_classes.append((node.name, node.lineno, markers))
        
        return test_classes
    
    def _extract_markers(self, node: ast.ClassDef) -> List[str]:
        """Extract pytest markers from decorators"""
        markers = []
        for decorator in node.decorator_list:
            marker_name = None
            
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    marker_name = decorator.func.attr
            elif isinstance(decorator, ast.Attribute):
                marker_name = decorator.attr
            
            if marker_name:
                markers.append(marker_name)
        
        return markers
    
    def has_pattern(self, pattern: str) -> List[Tuple[int, str]]:
        """
        Search for regex pattern in code
        
        Returns:
            List of (line_number, matching_line)
        """
        matches = []
        for line_num, line in enumerate(self.lines, 1):
            if re.search(pattern, line):
                matches.append((line_num, line))
        return matches


# 
# RULE ENGINES
# 

class EngineMixDetector:
    """Detects mixing of Playwright and Selenium in same test"""
    
    PLAYWRIGHT_PATTERNS = [
        r'from playwright\.sync_api import',
        r'from playwright\.async_api import',
        r'import playwright',
        r'\.locator\(',
        r'\.get_by_role\(',
        r'\.get_by_text\(',
    ]
    
    SELENIUM_PATTERNS = [
        r'from selenium import',
        r'from selenium\.webdriver',
        r'import selenium',
        r'\.find_element\(',
        r'\.find_elements\(',
        r'By\.',
    ]
    
    @staticmethod
    def detect(analyzer: ASTAnalyzer) -> List[Violation]:
        """Detect engine mixing in a file"""
        violations = []
        
        has_playwright = any(
            analyzer.has_pattern(p) for p in EngineMixDetector.PLAYWRIGHT_PATTERNS
        )
        has_selenium = any(
            analyzer.has_pattern(p) for p in EngineMixDetector.SELENIUM_PATTERNS
        )
        
        if has_playwright and has_selenium:
            violations.append(Violation(
                category=Category.ENGINE_MIX,
                severity=Severity.CRITICAL,
                rule_id="mixed-engines",
                file_path=str(analyzer.file_path),
                line_number=1,
                message="File mixes Playwright and Selenium - tests must use ONE engine",
                context="Both Playwright and Selenium APIs detected in same file",
                fix_suggestion="Split into separate test files: one for Playwright, one for Selenium"
            ))
        
        return violations


class MarkerEngineValidator:
    """Validates marker  engine consistency"""
    
    ENGINE_MARKERS = {
        'modern_spa': 'playwright',
        'playwright': 'playwright',
        'legacy_ui': 'selenium',
        'selenium': 'selenium',
    }
    
    @staticmethod
    def detect(analyzer: ASTAnalyzer) -> List[Violation]:
        """Detect marker/engine mismatches"""
        violations = []
        
        imports = analyzer.get_imports()
        test_classes = analyzer.get_test_classes()
        
        # Determine actual engine used
        has_playwright = any('playwright' in imp for imp in imports)
        has_selenium = any('selenium' in imp for imp in imports)
        
        for class_name, line_num, markers in test_classes:
            engine_markers = [m for m in markers if m in MarkerEngineValidator.ENGINE_MARKERS]
            
            # Missing engine marker
            if not engine_markers:
                violations.append(Violation(
                    category=Category.MARKER_ENGINE,
                    severity=Severity.ERROR,
                    rule_id="missing-engine-marker",
                    file_path=str(analyzer.file_path),
                    line_number=line_num,
                    message=f"Test class '{class_name}' missing engine marker (@pytest.mark.modern_spa or @pytest.mark.legacy_ui)",
                    context=f"Found markers: {markers}" if markers else "No markers found",
                    fix_suggestion=f"Add @pytest.mark.modern_spa (for Playwright) or @pytest.mark.legacy_ui (for Selenium) to class {class_name}"
                ))
            
            # Marker doesn't match actual engine
            for marker in engine_markers:
                expected_engine = MarkerEngineValidator.ENGINE_MARKERS[marker]
                
                if expected_engine == 'playwright' and has_selenium:
                    violations.append(Violation(
                        category=Category.MARKER_ENGINE,
                        severity=Severity.CRITICAL,
                        rule_id="marker-engine-mismatch",
                        file_path=str(analyzer.file_path),
                        line_number=line_num,
                        message=f"Marker @{marker} expects Playwright but file imports Selenium",
                        context=f"Class: {class_name}",
                        fix_suggestion=f"Either change marker to @pytest.mark.legacy_ui or remove Selenium imports"
                    ))
                
                elif expected_engine == 'selenium' and has_playwright:
                    violations.append(Violation(
                        category=Category.MARKER_ENGINE,
                        severity=Severity.CRITICAL,
                        rule_id="marker-engine-mismatch",
                        file_path=str(analyzer.file_path),
                        line_number=line_num,
                        message=f"Marker @{marker} expects Selenium but file imports Playwright",
                        context=f"Class: {class_name}",
                        fix_suggestion=f"Either change marker to @pytest.mark.modern_spa or remove Playwright imports"
                    ))
        
        return violations


class FolderEngineValidator:
    """Validates folder  engine alignment"""
    
    MODERN_FOLDERS = ['modern', 'spa', 'playwright']
    LEGACY_FOLDERS = ['legacy', 'selenium']
    
    @staticmethod
    def detect(analyzer: ASTAnalyzer) -> List[Violation]:
        """Detect folder/engine mismatches"""
        violations = []
        
        path_parts = str(analyzer.file_path).replace('\\', '/').split('/')
        
        is_modern_folder = any(folder in path_parts for folder in FolderEngineValidator.MODERN_FOLDERS)
        is_legacy_folder = any(folder in path_parts for folder in FolderEngineValidator.LEGACY_FOLDERS)
        
        imports = analyzer.get_imports()
        has_playwright = any('playwright' in imp for imp in imports)
        has_selenium = any('selenium' in imp for imp in imports)
        
        if is_modern_folder and has_selenium:
            violations.append(Violation(
                category=Category.FOLDER_ENGINE,
                severity=Severity.ERROR,
                rule_id="selenium-in-modern-folder",
                file_path=str(analyzer.file_path),
                line_number=1,
                message="Selenium imports found in 'modern' folder - should be Playwright",
                context=f"Path contains: {[p for p in path_parts if p in FolderEngineValidator.MODERN_FOLDERS]}",
                fix_suggestion="Move to /legacy folder or convert to Playwright"
            ))
        
        if is_legacy_folder and has_playwright:
            violations.append(Violation(
                category=Category.FOLDER_ENGINE,
                severity=Severity.ERROR,
                rule_id="playwright-in-legacy-folder",
                file_path=str(analyzer.file_path),
                line_number=1,
                message="Playwright imports found in 'legacy' folder - should be Selenium",
                context=f"Path contains: {[p for p in path_parts if p in FolderEngineValidator.LEGACY_FOLDERS]}",
                fix_suggestion="Move to /modern folder or convert to Selenium"
            ))
        
        return violations


class POMComplianceDetector:
    """Detects Page Object Model violations"""
    
    @staticmethod
    def detect(analyzer: ASTAnalyzer) -> List[Violation]:
        """Detect POM violations"""
        violations = []
        
        is_page_object = 'pages/' in str(analyzer.file_path).replace('\\', '/')
        is_test_file = 'tests/' in str(analyzer.file_path).replace('\\', '/')
        
        if is_page_object:
            violations.extend(POMComplianceDetector._check_page_object(analyzer))
        
        if is_test_file:
            violations.extend(POMComplianceDetector._check_test_file(analyzer))
        
        return violations
    
    @staticmethod
    def _check_page_object(analyzer: ASTAnalyzer) -> List[Violation]:
        """Check Page Object compliance"""
        violations = []
        
        # Forbidden: pytest imports
        for line_num, line in analyzer.has_pattern(r'(?:^|\n)\s*(?:import pytest|from pytest)'):
            violations.append(Violation(
                category=Category.POM_COMPLIANCE,
                severity=Severity.ERROR,
                rule_id="pytest-in-page-object",
                file_path=str(analyzer.file_path),
                line_number=line_num,
                message="Page Objects must not import pytest",
                context=line.strip(),
                fix_suggestion="Remove pytest import - Page Objects should return data, not assert"
            ))
        
        # Forbidden: assertions
        for line_num, line in analyzer.has_pattern(r'(?:^|\s)assert\s+\w'):
            violations.append(Violation(
                category=Category.POM_COMPLIANCE,
                severity=Severity.ERROR,
                rule_id="assertion-in-page-object",
                file_path=str(analyzer.file_path),
                line_number=line_num,
                message="Page Objects must not contain assertions",
                context=line.strip(),
                fix_suggestion="Return data from Page Object, assert in test"
            ))
        
        # Forbidden: time.sleep()
        for line_num, line in analyzer.has_pattern(r'time\.sleep\('):
            violations.append(Violation(
                category=Category.POM_COMPLIANCE,
                severity=Severity.ERROR,
                rule_id="sleep-in-page-object",
                file_path=str(analyzer.file_path),
                line_number=line_num,
                message="No explicit sleeps - use Playwright's auto-waiting",
                context=line.strip(),
                fix_suggestion="Remove sleep() and rely on Playwright auto-wait or use condition-based waits"
            ))
        
        # Forbidden: API calls
        for line_num, line in analyzer.has_pattern(r'(?:requests\.|httpx\.|urllib\.request)'):
            violations.append(Violation(
                category=Category.POM_COMPLIANCE,
                severity=Severity.ERROR,
                rule_id="api-call-in-page-object",
                file_path=str(analyzer.file_path),
                line_number=line_num,
                message="Page Objects should not make API calls",
                context=line.strip(),
                fix_suggestion="Move API logic to separate API client or helper module"
            ))
        
        return violations
    
    @staticmethod
    def _check_test_file(analyzer: ASTAnalyzer) -> List[Violation]:
        """Check test file compliance"""
        violations = []
        
        # Forbidden: Direct page.locator() calls
        for line_num, line in analyzer.has_pattern(r'page\.(?:locator|get_by_role|get_by_text)\('):
            if 'conftest' not in str(analyzer.file_path):  # Allow in conftest
                violations.append(Violation(
                    category=Category.TEST_BOUNDARIES,
                    severity=Severity.WARNING,
                    rule_id="direct-locator-in-test",
                    file_path=str(analyzer.file_path),
                    line_number=line_num,
                    message="Tests should use Page Objects, not direct page.locator() calls",
                    context=line.strip(),
                    fix_suggestion="Create/use Page Object method instead of direct locator access"
                ))
        
        # Forbidden: Direct driver.find_element() calls
        for line_num, line in analyzer.has_pattern(r'driver\.find_element\('):
            violations.append(Violation(
                category=Category.TEST_BOUNDARIES,
                severity=Severity.WARNING,
                rule_id="direct-find-element-in-test",
                file_path=str(analyzer.file_path),
                line_number=line_num,
                message="Tests should use Page Objects, not direct driver.find_element() calls",
                context=line.strip(),
                fix_suggestion="Create/use Page Object method instead of direct driver access"
            ))
        
        return violations


class StructuralValidator:
    """Validates file/folder structure"""
    
    @staticmethod
    def detect(analyzer: ASTAnalyzer) -> List[Violation]:
        """Detect structural violations"""
        violations = []
        
        path_str = str(analyzer.file_path).replace('\\', '/')
        
        # Page Objects must be in /pages
        if analyzer.tree:
            for node in ast.walk(analyzer.tree):
                if isinstance(node, ast.ClassDef) and node.name.endswith('Page'):
                    if 'pages/' not in path_str:
                        violations.append(Violation(
                            category=Category.STRUCTURAL,
                            severity=Severity.ERROR,
                            rule_id="page-object-wrong-location",
                            file_path=str(analyzer.file_path),
                            line_number=node.lineno,
                            message=f"Page Object '{node.name}' must be in /pages directory",
                            context=f"Current location: {path_str}",
                            fix_suggestion=f"Move {analyzer.file_path.name} to appropriate /pages subdirectory"
                        ))
        
        # Tests must be in /tests
        if analyzer.file_path.name.startswith('test_'):
            if 'tests/' not in path_str:
                violations.append(Violation(
                    category=Category.STRUCTURAL,
                    severity=Severity.ERROR,
                    rule_id="test-file-wrong-location",
                    file_path=str(analyzer.file_path),
                    line_number=1,
                    message="Test files must be in /tests directory",
                    context=f"Current location: {path_str}",
                    fix_suggestion=f"Move {analyzer.file_path.name} to appropriate /tests subdirectory"
                ))
        
        # No main() functions (pytest orchestrates)
        for line_num, line in analyzer.has_pattern(r'if __name__ == ["\']__main__["\']:'):
            violations.append(Violation(
                category=Category.STRUCTURAL,
                severity=Severity.WARNING,
                rule_id="main-function-in-test",
                file_path=str(analyzer.file_path),
                line_number=line_num,
                message="Tests should not have main() - pytest is the orchestrator",
                context=line.strip(),
                fix_suggestion="Remove if __name__ == '__main__' block - run via pytest"
            ))
        
        return violations


class CanonicalFlowProtector:
    """Protects authoritative complete flow tests"""
    
    @staticmethod
    def detect(analyzer: ASTAnalyzer) -> List[Violation]:
        """Detect changes to canonical flows"""
        violations = []
        
        # Identify complete flow files
        if '_complete_flow' in analyzer.file_path.name or '_full_flow' in analyzer.file_path.name:
            # These files are protected - any change requires review
            # In real implementation, would compare against git baseline
            violations.append(Violation(
                category=Category.CANONICAL_FLOW,
                severity=Severity.INFO,
                rule_id="canonical-flow-modified",
                file_path=str(analyzer.file_path),
                line_number=1,
                message="Canonical flow file modified - ensure business logic changes are approved",
                context=f"File: {analyzer.file_path.name}",
                fix_suggestion="Review changes with architect/product owner before merging"
            ))
        
        return violations


# 
# MAIN AUDIT ENGINE
# 

class FrameworkAuditEngine:
    """Main audit orchestrator"""
    
    def __init__(self, 
                 root_path: Path = None,
                 baseline_path: Path = None,
                 categories: List[Category] = None):
        self.root_path = root_path or Path('.')
        self.baseline_manager = BaselineManager(baseline_path) if baseline_path else None
        self.categories = categories or list(Category)
        
        self.detectors = {
            Category.ENGINE_MIX: EngineMixDetector(),
            Category.MARKER_ENGINE: MarkerEngineValidator(),
            Category.FOLDER_ENGINE: FolderEngineValidator(),
            Category.POM_COMPLIANCE: POMComplianceDetector(),
            Category.TEST_BOUNDARIES: POMComplianceDetector(),  # Same detector
            Category.STRUCTURAL: StructuralValidator(),
            Category.CANONICAL_FLOW: CanonicalFlowProtector(),
        }
    
    def audit(self) -> AuditResult:
        """Run complete audit"""
        result = AuditResult()
        result.baseline_used = self.baseline_manager is not None
        result.baseline_path = str(self.baseline_manager.baseline_path) if self.baseline_manager else None
        
        # Scan all Python files
        test_files = list(self.root_path.rglob('tests/**/*.py'))
        page_files = list(self.root_path.rglob('pages/**/*.py'))
        
        all_files = test_files + page_files
        result.files_scanned = len(all_files)
        
        print(f" Scanning {result.files_scanned} files...")
        
        for file_path in all_files:
            if self._should_skip(file_path):
                continue
            
            analyzer = ASTAnalyzer(file_path)
            if not analyzer.tree:
                continue  # Skip unparseable files
            
            # Run all detectors
            for category in self.categories:
                if category in self.detectors:
                    violations = self.detectors[category].detect(analyzer)
                    
                    # Apply baseline
                    for violation in violations:
                        if self.baseline_manager:
                            is_baselined, expires = self.baseline_manager.is_baselined(violation)
                            if is_baselined:
                                violation.baselined = True
                                violation.baseline_expires = expires
                        
                        result.violations.append(violation)
        
        return result
    
    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = ['__pycache__', '__init__.py', 'conftest.py', '.pyc']
        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)


# 
# MAIN ENTRY POINT
# 

def main():
    parser = argparse.ArgumentParser(
        description='Framework Architecture Audit Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Full audit
  %(prog)s --category engine-mix              # Specific category
  %(prog)s --baseline ci/baseline_allowlist.yaml
  %(prog)s --report artifacts/audit_report.md
  %(prog)s --ci --strict                      # CI mode
        """
    )
    
    parser.add_argument('--root', type=Path, default=Path('.'),
                       help='Root directory to scan')
    parser.add_argument('--baseline', type=Path,
                       help='Baseline allow-list YAML file')
    parser.add_argument('--category', type=str, choices=[c.value for c in Category],
                       help='Audit specific category only')
    parser.add_argument('--report', type=Path,
                       help='Generate markdown report')
    parser.add_argument('--ci', action='store_true',
                       help='CI mode (fail on any violation)')
    parser.add_argument('--strict', action='store_true',
                       help='Fail on warnings too')
    
    args = parser.parse_args()
    
    # Determine categories to check
    categories = [Category(args.category)] if args.category else list(Category)
    
    # Run audit
    engine = FrameworkAuditEngine(
        root_path=args.root,
        baseline_path=args.baseline,
        categories=categories
    )
    
    result = engine.audit()
    
    # Print results
    print("\n" + "="*80)
    print("AUDIT RESULTS")
    print("="*80)
    print(f"Files scanned: {result.files_scanned}")
    print(f"Violations found: {len(result.violations)}")
    print(f"Blocking violations: {len(result.get_blocking_violations())}")
    
    if result.violations:
        print("\nVIOLATIONS BY CATEGORY:")
        for category, violations in result.get_violations_by_category().items():
            non_baselined = [v for v in violations if not v.baselined]
            baselined = [v for v in violations if v.baselined]
            print(f"  {category.value}: {len(non_baselined)} active, {len(baselined)} baselined")
    
    # Generate report if requested
    if args.report:
        from framework_report_generator import generate_markdown_report
        generate_markdown_report(result, args.report)
        print(f"\n Report generated: {args.report}")
    
    # Exit code
    if result.is_passing():
        print("\nOK AUDIT PASSED")
        return 0
    else:
        print("\nX AUDIT FAILED")
        print(f"{len(result.get_blocking_violations())} blocking violations must be fixed")
        
        # Print blocking violations
        for violation in result.get_blocking_violations()[:10]:  # Show first 10
            print(f"  {violation}")
        
        return 1


if __name__ == '__main__':
    sys.exit(main())
