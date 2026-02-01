#!/usr/bin/env python3
"""
Enhanced Pre-Commit Hook - Mandatory Architecture Audit
========================================================

This pre-commit hook BLOCKS commits that violate architecture rules.
Runs automatically on every commit attempt.

Installation:
    python scripts/governance/install_hooks.py

Features:
    - Runs audit on staged files only (fast)
    - Blocks commit on violations
    - Generates audit report
    - Tracks commit history
    - Provides fix suggestions
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import List, Set

# Add governance to path
sys.path.insert(0, str(Path(__file__).parent))

from framework_audit_engine import FrameworkAuditEngine, AuditResult, Severity


def get_staged_python_files() -> List[Path]:
    """Get list of staged Python files."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True,
            text=True,
            check=True
        )
        
        files = result.stdout.strip().split('\n')
        python_files = [
            Path(f) for f in files 
            if f.endswith('.py') and Path(f).exists()
        ]
        
        return python_files
    
    except subprocess.CalledProcessError:
        return []


def get_current_commit_info() -> dict:
    """Get current commit information."""
    try:
        branch = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        
        author = subprocess.run(
            ['git', 'config', 'user.name'],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        
        email = subprocess.run(
            ['git', 'config', 'user.email'],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        
        return {
            'branch': branch,
            'author': author,
            'email': email,
            'timestamp': datetime.now().isoformat()
        }
    except:
        return {
            'branch': 'unknown',
            'author': 'unknown',
            'email': 'unknown',
            'timestamp': datetime.now().isoformat()
        }


def save_commit_audit_history(staged_files: List[Path], result: AuditResult, 
                              commit_info: dict):
    """Save audit history for this commit attempt."""
    history_dir = Path("artifacts/commit_history")
    history_dir.mkdir(parents=True, exist_ok=True)
    
    history_file = history_dir / "commit_audit_log.json"
    
    # Load existing history
    history = []
    if history_file.exists():
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
    
    # Calculate counts from violations
    blocking_count = len([v for v in result.violations if v.severity in (Severity.CRITICAL, Severity.ERROR)])
    warning_count = len([v for v in result.violations if v.severity == Severity.WARNING])
    info_count = len([v for v in result.violations if v.severity == Severity.INFO])
    passed = result.is_passing()
    
    # Add this commit attempt
    entry = {
        'timestamp': commit_info['timestamp'],
        'branch': commit_info['branch'],
        'author': commit_info['author'],
        'email': commit_info['email'],
        'files_staged': [str(f) for f in staged_files],
        'files_scanned': result.files_scanned,
        'total_violations': len(result.violations),
        'blocking_violations': blocking_count,
        'passed': passed,
        'violations': [
            {
                'file': v.file_path,
                'rule': v.rule_id,
                'severity': v.severity.value,
                'message': v.message,
                'line': v.line_number
            }
            for v in result.violations[:50]  # Limit to 50 violations
        ]
    }
    
    history.append(entry)
    
    # Keep last 500 commits
    if len(history) > 500:
        history = history[-500:]
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)


def display_violations(result: AuditResult, staged_files: Set[str]):
    """Display violations in terminal."""
    print("\n" + "="*70)
    print("ARCHITECTURE AUDIT - PRE-COMMIT CHECK")
    print("="*70)
    
    # Calculate counts
    blocking_count = len([v for v in result.violations if v.severity in (Severity.CRITICAL, Severity.ERROR)])
    warning_count = len([v for v in result.violations if v.severity == Severity.WARNING])
    info_count = len([v for v in result.violations if v.severity == Severity.INFO])
    passed = result.is_passing()
    
    if passed:
        print("\n[PASS] AUDIT PASSED - Commit allowed")
        print(f"\nFiles scanned: {result.files_scanned}")
        print(f"No violations detected")
        return True
    
    print("\n[FAIL] AUDIT FAILED - Commit BLOCKED")
    print(f"\nFiles scanned: {result.files_scanned}")
    print(f"Total violations: {len(result.violations)}")
    print(f"  - Blocking: {blocking_count}")
    print(f"  - Warnings: {warning_count}")
    print(f"  - Info: {info_count}")
    
    # Separate violations in staged files vs rest
    staged_violations = [v for v in result.violations if v.file_path in staged_files]
    other_violations = [v for v in result.violations if v.file_path not in staged_files]
    
    if staged_violations:
        print("\n" + "-"*70)
        print("VIOLATIONS IN STAGED FILES (Must fix to commit):")
        print("-"*70)
        
        # Group by severity
        critical = [v for v in staged_violations if v.severity == Severity.CRITICAL]
        errors = [v for v in staged_violations if v.severity == Severity.ERROR]
        warnings = [v for v in staged_violations if v.severity == Severity.WARNING]
        
        for severity_name, violations in [
            ('CRITICAL', critical),
            ('ERROR', errors),
            ('WARNING', warnings)
        ]:
            if violations:
                print(f"\n{severity_name} ({len(violations)}):")
                for v in violations[:10]:  # Show first 10
                    print(f"\n  {v.file_path}:{v.line_number}")
                    print(f"  Rule: {v.rule_id}")
                    print(f"  {v.message}")
                    if v.fix_suggestion:
                        print(f"  FIX: {v.fix_suggestion}")
                
                if len(violations) > 10:
                    print(f"\n  ... and {len(violations) - 10} more")
    
    if other_violations:
        print("\n" + "-"*70)
        print(f"OTHER VIOLATIONS (Not in staged files): {len(other_violations)}")
        print("-"*70)
        print("Fix these to improve codebase health")
    
    print("\n" + "="*70)
    print("TO FIX:")
    print("  1. Review violations above")
    print("  2. Fix the issues in your staged files")
    print("  3. Run: pytest --arch-audit (to verify)")
    print("  4. Try commit again")
    print("\nTO BYPASS (NOT RECOMMENDED):")
    print("  git commit --no-verify")
    print("="*70)
    
    return False


def main():
    """Main pre-commit hook logic."""
    print("\n[AUDIT] Running architecture audit on staged files...")
    
    # Get staged files
    staged_files = get_staged_python_files()
    
    if not staged_files:
        print("No Python files staged - skipping audit")
        return 0
    
    print(f"Checking {len(staged_files)} staged Python file(s)...")
    
    # Get commit info
    commit_info = get_current_commit_info()
    
    # Run audit
    engine = FrameworkAuditEngine()
    result = engine.audit()
    
    # Save history
    save_commit_audit_history(staged_files, result, commit_info)
    
    # Display results
    staged_set = {str(f) for f in staged_files}
    passed = display_violations(result, staged_set)
    
    # Check if any blocking violations in staged files
    staged_violations = [v for v in result.violations if v.file_path in staged_set]
    blocking_in_staged = any(
        v.severity in (Severity.CRITICAL, Severity.ERROR) 
        for v in staged_violations
    )
    
    if blocking_in_staged:
        print("\n[BLOCKED] COMMIT BLOCKED due to violations in staged files")
        return 1
    
    if passed:
        print("\n[ALLOWED] COMMIT ALLOWED")
        return 0
    else:
        print("\n[WARNING] COMMIT ALLOWED with warnings")
        return 0


if __name__ == '__main__':
    sys.exit(main())
