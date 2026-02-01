#!/usr/bin/env python3
"""════════════════════════════════════════════════════════════════════════════ GOVERNANCE SYSTEM
VERIFICATION ════════════════════════════════════════════════════════════════════════════

Verifies that the complete governance system is properly installed and functional.

USAGE:
    python scripts/validation/verify_governance_system.py

Author: Principal QA Architect
Date: February 1, 2026
════════════════════════════════════════════════════════════════════════════
"""

import sys
from pathlib import Path
import importlib.util


def check_file_exists(file_path: Path, description: str) -> bool:
    """Check if file exists."""
    if file_path.exists():
        print(f"  ✅ {description}: {file_path.name}")
        return True
    else:
        print(f"  ❌ {description}: MISSING - {file_path}")
        return False


def check_module_imports(module_path: Path, module_name: str) -> bool:
    """Check if module can be imported."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"  ✅ {module_name} imports successfully")
            return True
    except Exception as e:
        print(f"  ❌ {module_name} import failed: {e}")
        return False
    return False


def main():
    print("\n" + "="*80)
    print("🏗️  GOVERNANCE SYSTEM VERIFICATION")
    print("="*80)
    print()
    
    root = Path('.')
    all_checks = []
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Core Governance Scripts
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("📦 Core Governance Scripts")
    print("-" * 80)
    
    core_files = {
        'scripts/governance/framework_audit_engine.py': 'AST-Based Audit Engine',
        'scripts/governance/framework_report_generator.py': 'Report Generator',
        'scripts/governance/framework_fix_suggestions.py': 'Fix Suggestion Engine',
        'scripts/governance/pytest_arch_audit_plugin.py': 'Pytest Plugin',
        'scripts/governance/ai_explainer.py': 'AI Explainer',
    }
    
    for file_path, description in core_files.items():
        all_checks.append(check_file_exists(root / file_path, description))
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CI Integration
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("🔄 CI Integration Scripts")
    print("-" * 80)
    
    ci_files = {
        'ci/ci_audit_runner.py': 'CI Audit Runner',
        'ci/github_pr_commenter.py': 'PR Comment Generator',
        'ci/baseline_allowlist.yaml': 'Baseline Allow-List',
    }
    
    for file_path, description in ci_files.items():
        all_checks.append(check_file_exists(root / file_path, description))
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # GitHub Actions Workflow
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("⚙️  GitHub Actions Workflows")
    print("-" * 80)
    
    workflow_files = {
        '.github/workflows/architecture-audit.yml': 'Architecture Audit Workflow',
    }
    
    for file_path, description in workflow_files.items():
        all_checks.append(check_file_exists(root / file_path, description))
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Documentation
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("📚 Documentation")
    print("-" * 80)
    
    doc_files = {
        'docs/GOVERNANCE_SYSTEM.md': 'Governance System Guide',
        'docs/ENFORCEMENT_SUMMARY.md': 'Enforcement Summary',
    }
    
    for file_path, description in doc_files.items():
        all_checks.append(check_file_exists(root / file_path, description))
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Quick Start Scripts
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("🚀 Quick Start Scripts")
    print("-" * 80)
    
    quick_start_files = {
        'scripts/quick-start/quick_governance_audit.py': 'Quick Governance Audit',
    }
    
    for file_path, description in quick_start_files.items():
        all_checks.append(check_file_exists(root / file_path, description))
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Import Checks
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("🔍 Module Import Checks")
    print("-" * 80)
    
    # Check core audit engine imports
    audit_engine_path = root / 'scripts/governance/framework_audit_engine.py'
    if audit_engine_path.exists():
        all_checks.append(check_module_imports(audit_engine_path, 'framework_audit_engine'))
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Conftest Registration
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("🔧 Pytest Configuration")
    print("-" * 80)
    
    conftest_path = root / 'conftest.py'
    if conftest_path.exists():
        with open(conftest_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'pytest_arch_audit_plugin' in content:
                print("  ✅ Audit plugin registered in conftest.py")
                all_checks.append(True)
            else:
                print("  ❌ Audit plugin NOT registered in conftest.py")
                all_checks.append(False)
    else:
        print("  ❌ conftest.py not found")
        all_checks.append(False)
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Directory Structure
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("📁 Directory Structure")
    print("-" * 80)
    
    required_dirs = [
        'scripts/governance',
        'scripts/enforcement',
        'ci',
        '.github/workflows',
    ]
    
    for dir_path in required_dirs:
        full_path = root / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"  ✅ {dir_path}/")
            all_checks.append(True)
        else:
            print(f"  ❌ {dir_path}/ - MISSING")
            all_checks.append(False)
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════════════════════════════════════════
    
    print("="*80)
    print("📊 VERIFICATION SUMMARY")
    print("="*80)
    
    passed = sum(all_checks)
    total = len(all_checks)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\nChecks passed: {passed}/{total} ({percentage:.1f}%)")
    
    if all(all_checks):
        print("\n✅ GOVERNANCE SYSTEM FULLY OPERATIONAL")
        print("\nNext steps:")
        print("  1. Run local audit: pytest --arch-audit")
        print("  2. Review documentation: docs/GOVERNANCE_SYSTEM.md")
        print("  3. Enable GitHub Actions workflow")
        print()
        return 0
    else:
        print("\n❌ GOVERNANCE SYSTEM INCOMPLETE")
        print("\nSome components are missing. Review errors above.")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
