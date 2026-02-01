#!/usr/bin/env python3
"""

PYTEST PLUGIN FOR ARCHITECTURE AUDIT


Enables developers to run architecture audits locally via pytest.

USAGE:
    # Run architecture audit
    pytest --arch-audit
    
    # Audit specific category
    pytest --arch-audit --audit-category=engine-mix
    
    # With baseline
    pytest --arch-audit --audit-baseline=ci/baseline_allowlist.yaml
    
    # Generate report
    pytest --arch-audit --audit-report=audit_report.md
    
    # Strict mode (fail on warnings)
    pytest --arch-audit --audit-strict

FEATURES:
OK Same rules as CI
OK Same failure behavior
OK Fast execution (<2 seconds)
OK No browser execution
OK Detailed violation output

Author: Principal QA Architect
Date: February 1, 2026

"""

import pytest
import sys
from pathlib import Path
from typing import List

# Add scripts/governance to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'governance'))

try:
    from framework_audit_engine import (
        FrameworkAuditEngine, 
        Category, 
        Severity,
        AuditResult,
        Violation
    )
    from framework_report_generator import generate_markdown_report
    from framework_fix_suggestions import FixSuggestionEngine
except ImportError as e:
    print(f"ERROR: Cannot import audit engine: {e}")
    print("Ensure framework_audit_engine.py is in scripts/governance/")
    sys.exit(1)


# 
# PYTEST PLUGIN HOOKS
# 

def pytest_addoption(parser):
    """Add custom command-line options"""
    group = parser.getgroup('arch-audit', 'Architecture Audit')
    
    group.addoption(
        '--arch-audit',
        action='store_true',
        default=False,
        help='Run architecture audit (no browser execution)'
    )
    
    group.addoption(
        '--audit-category',
        type=str,
        default=None,
        choices=[c.value for c in Category],
        help='Audit specific category only'
    )
    
    group.addoption(
        '--audit-baseline',
        type=str,
        default='ci/baseline_allowlist.yaml',
        help='Path to baseline allow-list YAML'
    )
    
    group.addoption(
        '--audit-report',
        type=str,
        default=None,
        help='Generate markdown report at specified path'
    )
    
    group.addoption(
        '--audit-strict',
        action='store_true',
        default=False,
        help='Fail on warnings too (not just errors)'
    )
    
    group.addoption(
        '--audit-show-fixes',
        action='store_true',
        default=True,
        help='Show fix suggestions for violations'
    )


def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", 
        "arch_audit: Mark test as architecture audit test"
    )


def pytest_collection_modifyitems(session, config, items):
    """Modify test collection if audit mode is enabled"""
    if config.getoption('--arch-audit'):
        # In audit mode, we don't collect regular tests
        # We'll run the audit in pytest_sessionstart instead
        items.clear()


def pytest_sessionstart(session):
    """Run architecture audit at session start if enabled"""
    config = session.config
    
    if not config.getoption('--arch-audit'):
        return
    
    print("\n" + "="*80)
    print("ARCHITECTURE AUDIT MODE")
    print("="*80)
    print("Running static analysis (no browser execution)...\n")
    
    # Get options
    category_str = config.getoption('--audit-category')
    baseline_path = config.getoption('--audit-baseline')
    report_path = config.getoption('--audit-report')
    strict = config.getoption('--audit-strict')
    show_fixes = config.getoption('--audit-show-fixes')
    
    # Parse category
    categories = [Category(category_str)] if category_str else list(Category)
    
    # Parse baseline path
    baseline = Path(baseline_path) if baseline_path and Path(baseline_path).exists() else None
    
    # Run audit
    engine = FrameworkAuditEngine(
        root_path=Path('.'),
        baseline_path=baseline,
        categories=categories
    )
    
    result = engine.audit()
    
    # Display results
    _display_audit_results(result, show_fixes)
    
    # Generate report if requested
    if report_path:
        generate_markdown_report(result, Path(report_path))
        print(f"\n Report generated: {report_path}")
    
    # Store result in config for pytest_sessionfinish
    config._audit_result = result
    config._audit_strict = strict


def pytest_sessionfinish(session, exitstatus):
    """Determine exit status based on audit results"""
    config = session.config
    
    if not config.getoption('--arch-audit'):
        return
    
    result: AuditResult = getattr(config, '_audit_result', None)
    strict = getattr(config, '_audit_strict', False)
    
    if not result:
        return
    
    # Determine if audit passed
    if strict:
        # Strict mode: fail on any non-baselined violation
        non_baselined = [v for v in result.violations if not v.baselined]
        passed = len(non_baselined) == 0
    else:
        # Normal mode: fail on blocking violations only
        passed = result.is_passing()
    
    if passed:
        print("\n" + "="*80)
        print("OK ARCHITECTURE AUDIT PASSED")
        print("="*80)
        print(f"Files scanned: {result.files_scanned}")
        print(f"Violations found: {len(result.violations)}")
        print(f"Baselined: {len([v for v in result.violations if v.baselined])}")
        print("\nFramework maintains architectural compliance! ")
        
        session.exitstatus = 0
    else:
        print("\n" + "="*80)
        print("X ARCHITECTURE AUDIT FAILED")
        print("="*80)
        
        if strict:
            print("Running in STRICT mode - all violations must be fixed")
        
        blocking = result.get_blocking_violations()
        print(f"\n{len(blocking)} blocking violations detected")
        print("\nRun with --audit-show-fixes to see detailed fix suggestions")
        
        session.exitstatus = 1


# 
# DISPLAY HELPERS
# 

def _display_audit_results(result: AuditResult, show_fixes: bool = True):
    """Display audit results in terminal"""
    
    print(f" Files scanned: {result.files_scanned}")
    print(f" Total violations: {len(result.violations)}")
    
    if result.baseline_used:
        baselined = len([v for v in result.violations if v.baselined])
        print(f" Baselined violations: {baselined}")
    
    print()
    
    # Group by category
    by_category = result.get_violations_by_category()
    
    for category, violations in sorted(by_category.items(), key=lambda x: x[0].value):
        active = [v for v in violations if not v.baselined]
        
        if not active:
            print(f"OK {category.value.upper()}: No violations")
            continue
        
        print(f"\n{'='*80}")
        print(f"X {category.value.upper()}: {len(active)} violations")
        print(f"{'='*80}")
        
        # Group by severity
        by_severity = {}
        for v in active:
            if v.severity not in by_severity:
                by_severity[v.severity] = []
            by_severity[v.severity].append(v)
        
        # Display by severity
        for severity in [Severity.CRITICAL, Severity.ERROR, Severity.WARNING, Severity.INFO]:
            if severity not in by_severity:
                continue
            
            severity_violations = by_severity[severity]
            icon = {
                Severity.CRITICAL: "",
                Severity.ERROR: "X",
                Severity.WARNING: "!",
                Severity.INFO: "i"
            }[severity]
            
            print(f"\n{icon} {severity.value} ({len(severity_violations)})")
            print("-" * 80)
            
            for v in severity_violations[:5]:  # Show first 5 per severity
                print(f"\n {Path(v.file_path).name}:{v.line_number}")
                print(f"   Rule: {v.rule_id}")
                print(f"   {v.message}")
                
                if v.context:
                    print(f"   Context: {v.context[:100]}...")
                
                if show_fixes and v.fix_suggestion:
                    print(f"\n   * Fix: {v.fix_suggestion}")
                elif show_fixes:
                    # Generate fix on the fly
                    fix = FixSuggestionEngine.generate_suggestion(v)
                    if fix:
                        # Show first few lines of fix
                        fix_lines = fix.split('\n')[:3]
                        print(f"\n   * Fix suggestion:")
                        for line in fix_lines:
                            print(f"      {line}")
            
            if len(severity_violations) > 5:
                print(f"\n   ... and {len(severity_violations) - 5} more {severity.value} violations")


# 
# PLUGIN REGISTRATION
# 

# This module is automatically discovered by pytest if:
# 1. Named pytest_*.py or *_plugin.py
# 2. Located in conftest.py's directory or
# 3. Registered in setup.py/pyproject.toml


if __name__ == '__main__':
    print("Pytest Architecture Audit Plugin")
    print("=" * 80)
    print("\nThis is a pytest plugin. Use via pytest command:")
    print("\n  pytest --arch-audit")
    print("  pytest --arch-audit --audit-category=engine-mix")
    print("  pytest --arch-audit --audit-report=report.md")
    print("\nFor more options, run:")
    print("  pytest --help | grep -A 20 'arch-audit'")
