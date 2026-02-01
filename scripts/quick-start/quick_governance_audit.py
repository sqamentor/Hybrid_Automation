#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════
QUICK GOVERNANCE AUDIT
════════════════════════════════════════════════════════════════════════════

Fast audit for quick checks before committing.

USAGE:
    python scripts/quick-start/quick_governance_audit.py
    
    # Specific category
    python scripts/quick-start/quick_governance_audit.py --category engine-mix
    
    # With report
    python scripts/quick-start/quick_governance_audit.py --report

Author: Principal QA Architect
Date: February 1, 2026
════════════════════════════════════════════════════════════════════════════
"""

import sys
import subprocess
from pathlib import Path
import argparse


def main():
    parser = argparse.ArgumentParser(
        description='Quick governance audit'
    )
    parser.add_argument(
        '--category',
        type=str,
        help='Audit specific category only'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate markdown report'
    )
    args = parser.parse_args()
    
    print("=" * 80)
    print("🏗️  QUICK GOVERNANCE AUDIT")
    print("=" * 80)
    print()
    
    # Build pytest command
    cmd = ['pytest', '--arch-audit']
    
    if args.category:
        cmd.extend(['--audit-category', args.category])
    
    if args.report:
        cmd.extend(['--audit-report', 'quick_audit_report.md'])
    
    # Always show fixes in quick audit
    cmd.append('--audit-show-fixes')
    
    print(f"Running: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("❌ pytest not found - ensure you're in virtual environment")
        print("   Run: python -m pytest --arch-audit")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
