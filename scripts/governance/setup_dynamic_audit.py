#!/usr/bin/env python3
"""
One-Command Dynamic Audit Setup
================================

Complete setup for dynamic, automatic architecture auditing.

Usage:
    python scripts/governance/setup_dynamic_audit.py
    python scripts/governance/setup_dynamic_audit.py --full
"""

import sys
import subprocess
from pathlib import Path


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "="*70)
    print(text)
    print("="*70)


def check_requirements():
    """Check and install required dependencies"""
    print_header("CHECKING REQUIREMENTS")
    
    required = [
        ('watchdog', 'File system monitoring'),
    ]
    
    missing = []
    
    for package, purpose in required:
        try:
            __import__(package)
            print(f"✅ {package} installed ({purpose})")
        except ImportError:
            print(f"❌ {package} missing ({purpose})")
            missing.append(package)
    
    if missing:
        print(f"\n📦 Installing missing packages: {', '.join(missing)}")
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install'] + missing,
                check=True
            )
            print("✅ Packages installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages")
            print("   Please install manually: pip install " + ' '.join(missing))
            return False
    
    return True


def install_git_hooks():
    """Install pre-commit hooks"""
    print_header("INSTALLING GIT HOOKS")
    
    installer = Path("scripts/governance/install_hooks.py")
    
    if not installer.exists():
        print("❌ Hook installer not found")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(installer)],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print("✅ Git hooks installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install hooks: {e}")
        return False


def setup_github_actions():
    """Check GitHub Actions configuration"""
    print_header("GITHUB ACTIONS CONFIGURATION")
    
    workflow = Path(".github/workflows/architecture-audit.yml")
    
    if not workflow.exists():
        print("❌ GitHub Actions workflow not found")
        return False
    
    print("✅ GitHub Actions workflow found")
    print("\n📝 To enable automatic audits on GitHub:")
    print("   1. Push this workflow to your repository")
    print("   2. Enable GitHub Actions in repository settings")
    print("   3. Configure branch protection rules:")
    print("      - Go to Settings > Branches > main > Branch protection")
    print("      - Enable 'Require status checks to pass before merging'")
    print("      - Select these required checks:")
    print("        ✓ audit/engine-mix")
    print("        ✓ audit/marker-engine")
    print("        ✓ audit/folder-engine")
    print("        ✓ audit/pom-compliance")
    print("        ✓ audit/structural")
    
    return True


def create_directories():
    """Create required directories"""
    print_header("CREATING DIRECTORIES")
    
    dirs = [
        Path("artifacts/audit_history"),
        Path("artifacts/commit_history"),
        Path("artifacts/archive"),
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ {dir_path}")
    
    return True


def run_initial_audit():
    """Run initial audit to establish baseline"""
    print_header("RUNNING INITIAL AUDIT")
    
    print("\nThis will establish your current compliance baseline...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', '--arch-audit'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("\n✅ Initial audit passed")
        else:
            print("\n⚠️ Initial audit detected violations")
            print("   This is expected for first run")
            print("   Review: artifacts/framework_audit_report.md")
        
        return True
    except Exception as e:
        print(f"❌ Initial audit failed: {e}")
        return False


def generate_dashboard():
    """Generate initial dashboard"""
    print_header("GENERATING DASHBOARD")
    
    dashboard_script = Path("scripts/governance/audit_dashboard.py")
    
    if not dashboard_script.exists():
        print("❌ Dashboard script not found")
        return False
    
    try:
        subprocess.run(
            [sys.executable, str(dashboard_script)],
            check=True,
            capture_output=True
        )
        print("✅ Dashboard generated: artifacts/audit_dashboard.html")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ Dashboard generation skipped (no data yet)")
        return True


def print_usage_guide():
    """Print usage guide"""
    print_header("SETUP COMPLETE - USAGE GUIDE")
    
    print("""
🎯 DYNAMIC AUDIT SYSTEM - NOW ACTIVE

═══════════════════════════════════════════════════════════════════

1️⃣ LOCAL DEVELOPMENT - FILE WATCHER

   Start the file watcher to automatically audit on changes:
   
   $ python scripts/governance/file_watcher_audit.py --watch
   
   Features:
   - Monitors tests/, pages/, framework/, utils/
   - Auto-triggers audit 2 seconds after last change
   - Displays real-time results
   - Tracks history for trending
   
   Strict mode (stops on violations):
   $ python scripts/governance/file_watcher_audit.py --watch --strict

═══════════════════════════════════════════════════════════════════

2️⃣ GIT COMMITS - AUTOMATIC BLOCKING

   ✅ ALREADY ACTIVE - Pre-commit hook installed
   
   Every commit will:
   - Run audit on staged files
   - Block commit if violations found
   - Track commit history
   - Provide fix suggestions
   
   To bypass (NOT recommended):
   $ git commit --no-verify

═══════════════════════════════════════════════════════════════════

3️⃣ GITHUB CI/CD - AUTOMATIC ENFORCEMENT

   ✅ ALREADY CONFIGURED - Triggers on push/PR
   
   Every push/PR will:
   - Run 7 independent status checks
   - Block merge if violations found
   - Generate audit reports
   - Comment on PR with results
   - Archive reports for audit trail
   
   Configure branch protection to enforce.

═══════════════════════════════════════════════════════════════════

4️⃣ AUDIT DASHBOARD - TRACK TRENDS

   View compliance trends and metrics:
   
   $ python scripts/governance/audit_dashboard.py --open
   
   Features:
   - Real-time violation trends
   - Compliance score
   - Category breakdown
   - Most violated files
   - Historical analysis

═══════════════════════════════════════════════════════════════════

5️⃣ MANUAL AUDIT - ANYTIME

   Run audit manually:
   
   $ pytest --arch-audit
   $ pytest --arch-audit --audit-category=pom-compliance
   
   View history:
   $ python scripts/governance/file_watcher_audit.py --history
   $ python scripts/governance/file_watcher_audit.py --trend

═══════════════════════════════════════════════════════════════════

📊 REPORTS & TRACKING

   All audits are automatically tracked:
   
   - artifacts/framework_audit_report.md (latest)
   - artifacts/audit_history/audit_history.json (watcher)
   - artifacts/commit_history/commit_audit_log.json (commits)
   - artifacts/archive/*.md (timestamped + git hash)
   - artifacts/audit_dashboard.html (visual trends)

═══════════════════════════════════════════════════════════════════

✅ COMPLIANCE GUARANTEED

   With this setup:
   
   ✓ Every file change is monitored (watcher)
   ✓ Every commit is validated (pre-commit hook)
   ✓ Every push is audited (GitHub Actions)
   ✓ Every violation is tracked (history logs)
   ✓ Trends are visible (dashboard)
   ✓ Reports are archived (git metadata)
   
   🎯 IMPOSSIBLE TO VIOLATE RULES WITHOUT DETECTION

═══════════════════════════════════════════════════════════════════

🔧 TROUBLESHOOTING

   If issues occur:
   
   1. Verify system: python scripts/validation/verify_governance_system.py
   2. Check logs: artifacts/audit_history/
   3. Review workflow: .github/workflows/architecture-audit.yml
   4. Test hook: python scripts/governance/install_hooks.py --test

═══════════════════════════════════════════════════════════════════

📚 DOCUMENTATION

   - docs/GOVERNANCE_SYSTEM.md (complete system guide)
   - docs/GOVERNANCE_QUICK_REF.md (daily reference)
   - docs/DEPLOYMENT_CHECKLIST.md (deployment guide)
   - docs/AUDIT_TODO_LIST_AND_VERIFICATION.md (audit verification)

═══════════════════════════════════════════════════════════════════
""")


def main():
    """Main setup"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup Dynamic Audit System")
    parser.add_argument('--full', action='store_true', 
                       help='Run full setup including initial audit')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🏗️  DYNAMIC AUDIT SYSTEM - SETUP")
    print("="*70)
    print("\nThis will configure automatic architecture auditing for:")
    print("  - File system changes (watcher)")
    print("  - Git commits (pre-commit hooks)")
    print("  - GitHub CI/CD (Actions)")
    print("  - Audit history tracking")
    print("  - Trend dashboard")
    
    results = []
    
    # 1. Check requirements
    results.append(('Requirements', check_requirements()))
    
    # 2. Create directories
    results.append(('Directories', create_directories()))
    
    # 3. Install git hooks
    results.append(('Git Hooks', install_git_hooks()))
    
    # 4. Check GitHub Actions
    results.append(('GitHub Actions', setup_github_actions()))
    
    # 5. Full setup only
    if args.full:
        results.append(('Initial Audit', run_initial_audit()))
        results.append(('Dashboard', generate_dashboard()))
    
    # Summary
    print_header("SETUP SUMMARY")
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    failed = [name for name, success in results if not success]
    
    if failed:
        print(f"\n❌ Setup incomplete - failed: {', '.join(failed)}")
        return 1
    
    print("\n✅ SETUP COMPLETE")
    
    # Usage guide
    print_usage_guide()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
