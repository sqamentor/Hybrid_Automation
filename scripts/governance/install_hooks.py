#!/usr/bin/env python3
"""
Git Hook Installer - Automatic Setup
====================================

Installs enhanced pre-commit hooks that enforce architecture rules.

Usage:
    python scripts/governance/install_hooks.py
    python scripts/governance/install_hooks.py --uninstall
"""

import sys
import shutil
import subprocess
from pathlib import Path


def install_git_hooks():
    """Install pre-commit hook"""
    git_dir = Path(".git")
    
    if not git_dir.exists():
        print("ERROR: Not a git repository")
        return False
    
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    pre_commit_hook = hooks_dir / "pre-commit"
    
    # Backup existing hook
    if pre_commit_hook.exists():
        backup = hooks_dir / "pre-commit.backup"
        shutil.copy(pre_commit_hook, backup)
        print(f"Backed up existing hook to: {backup}")
    
    # Write hook
    hook_content = """#!/usr/bin/env python3
# Auto-generated pre-commit hook - enforces architecture rules

import sys
from pathlib import Path

# Run the enhanced pre-commit audit
hook_script = Path("scripts/governance/pre_commit_hook_enhanced.py")

if not hook_script.exists():
    print("ERROR: Pre-commit audit script not found")
    sys.exit(1)

import subprocess
result = subprocess.run([sys.executable, str(hook_script)])
sys.exit(result.returncode)
"""
    
    pre_commit_hook.write_text(hook_content, encoding='utf-8')
    
    # Make executable (Unix)
    try:
        pre_commit_hook.chmod(0o755)
    except:
        pass
    
    print("\n" + "="*70)
    print("✅ PRE-COMMIT HOOK INSTALLED")
    print("="*70)
    print(f"\nLocation: {pre_commit_hook}")
    print("\nThe hook will:")
    print("  - Run architecture audit on every commit")
    print("  - Block commits with violations")
    print("  - Track commit history for audit trail")
    print("  - Provide fix suggestions")
    print("\nTo bypass (NOT recommended):")
    print("  git commit --no-verify")
    print("="*70)
    
    return True


def uninstall_git_hooks():
    """Uninstall pre-commit hook"""
    git_dir = Path(".git")
    
    if not git_dir.exists():
        print("ERROR: Not a git repository")
        return False
    
    pre_commit_hook = git_dir / "hooks" / "pre-commit"
    
    if pre_commit_hook.exists():
        # Check if it's our hook
        content = pre_commit_hook.read_text(encoding='utf-8')
        if "pre_commit_hook_enhanced.py" in content:
            pre_commit_hook.unlink()
            print("✅ Pre-commit hook uninstalled")
            
            # Restore backup if exists
            backup = git_dir / "hooks" / "pre-commit.backup"
            if backup.exists():
                shutil.copy(backup, pre_commit_hook)
                print("✅ Restored previous hook from backup")
        else:
            print("Hook exists but is not our auto-audit hook - not removing")
    else:
        print("No hook to uninstall")
    
    return True


def test_hook():
    """Test the installed hook"""
    print("\n" + "="*70)
    print("TESTING HOOK")
    print("="*70)
    
    hook_script = Path("scripts/governance/pre_commit_hook_enhanced.py")
    
    if not hook_script.exists():
        print("❌ Hook script not found")
        return False
    
    print("\nRunning hook test...")
    
    result = subprocess.run(
        [sys.executable, str(hook_script)],
        capture_output=False
    )
    
    if result.returncode == 0:
        print("\n✅ Hook test passed")
    else:
        print("\n❌ Hook test failed")
    
    return result.returncode == 0


def main():
    """Main installer"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Install Git Hooks")
    parser.add_argument('--uninstall', action='store_true', help='Uninstall hooks')
    parser.add_argument('--test', action='store_true', help='Test hook')
    
    args = parser.parse_args()
    
    if args.uninstall:
        uninstall_git_hooks()
    elif args.test:
        test_hook()
    else:
        install_git_hooks()


if __name__ == '__main__':
    main()
