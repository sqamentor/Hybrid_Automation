#!/usr/bin/env python3
"""
GitHub Actions Configuration Helper
====================================
Helps set up GitHub Actions for the governance system.

Run: python scripts/ci/setup_github_actions.py
"""

import os
import sys
from pathlib import Path


def check_workflow_file():
    """Check if workflow file exists."""
    workflow_path = Path(".github/workflows/architecture-audit.yml")
    
    if workflow_path.exists():
        print("OK Workflow file exists: .github/workflows/architecture-audit.yml")
        return True
    else:
        print("X Workflow file not found!")
        print("  Expected: .github/workflows/architecture-audit.yml")
        return False


def check_github_token():
    """Check if GITHUB_TOKEN is available (in CI)"""
    if os.getenv("GITHUB_TOKEN"):
        print("OK GITHUB_TOKEN is available")
        return True
    else:
        print("i GITHUB_TOKEN not found (normal for local environment)")
        print("  In GitHub Actions, GITHUB_TOKEN is automatic")
        return True  # Not an error locally


def print_setup_instructions():
    """Print setup instructions."""
    print("\n" + "="*70)
    print("GITHUB ACTIONS SETUP INSTRUCTIONS")
    print("="*70)
    print()
    print("Step 1: Ensure workflow file is committed")
    print("  git add .github/workflows/architecture-audit.yml")
    print("  git commit -m 'Add architecture audit workflow'")
    print("  git push")
    print()
    print("Step 2: Verify workflow in GitHub")
    print("  1. Go to your repository on GitHub")
    print("  2. Click 'Actions' tab")
    print("  3. You should see 'Architecture Audit' workflow")
    print()
    print("Step 3: Test with a PR")
    print("  1. Create a branch: git checkout -b test-audit")
    print("  2. Make a change: echo '# test' >> README.md")
    print("  3. Commit: git commit -am 'Test audit'")
    print("  4. Push: git push origin test-audit")
    print("  5. Create PR on GitHub")
    print("  6. Watch for 7 status checks (one per rule category)")
    print()
    print("Step 4: Review PR Comments")
    print("  - If violations detected, bot will comment on PR")
    print("  - Comments include fix suggestions")
    print("  - Fix violations and push again")
    print()
    print("="*70)
    print("OPTIONAL: PR Comment Permissions")
    print("="*70)
    print()
    print("To enable PR comments, ensure workflow has write permissions:")
    print("  Repository Settings > Actions > General > Workflow permissions")
    print("  Select: 'Read and write permissions'")
    print("  Save")
    print()
    print("="*70)
    print("TROUBLESHOOTING")
    print("="*70)
    print()
    print("Q: Workflow not appearing in Actions tab?")
    print("A: Ensure workflow file is in .github/workflows/ and committed to main")
    print()
    print("Q: Status checks not appearing in PR?")
    print("A: Check Actions tab for errors. Ensure pytest is installed in CI.")
    print()
    print("Q: PR comments not being posted?")
    print("A: Check workflow permissions (read and write required)")
    print()


def main():
    """Main setup helper."""
    print("\n" + "="*70)
    print("GOVERNANCE SYSTEM - GITHUB ACTIONS SETUP HELPER")
    print("="*70)
    print()
    
    workflow_ok = check_workflow_file()
    token_ok = check_github_token()
    
    print()
    
    if workflow_ok:
        print_setup_instructions()
        print()
        print("OK Setup helper complete!")
        print("   Follow instructions above to enable CI/CD")
        return 0
    else:
        print()
        print("X Workflow file missing!")
        print("  This should not happen - workflow was created during setup")
        print("  Check: .github/workflows/architecture-audit.yml")
        return 1


if __name__ == "__main__":
    sys.exit(main())
