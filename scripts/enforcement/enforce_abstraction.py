#!/usr/bin/env python3
"""Engine Abstraction Enforcement Tool.

Detects direct Playwright/Selenium imports in test files.
Tests should use the ui_engine fixture, not import engines directly.

Usage:
    python enforce_abstraction.py
    python enforce_abstraction.py --strict

Exit Codes:
    0 - No forbidden imports found
    1 - Forbidden imports detected

Author: Principal QA Architect
Date: January 31, 2026
"""

import re
import sys
from pathlib import Path
from typing import List, Dict

# Patterns to detect direct engine imports
FORBIDDEN_IMPORT_PATTERNS = [
    (r'from playwright\.sync_api import', 'Playwright Sync API'),
    (r'from playwright\.async_api import', 'Playwright Async API'),
    (r'from selenium import', 'Selenium'),
    (r'from selenium\.webdriver', 'Selenium WebDriver'),
    (r'import playwright', 'Playwright module'),
    (r'import selenium', 'Selenium module'),
]

# Files that are ALLOWED to import engines (they test the engines directly)
ALLOWED_FILES = [
    'tests/unit/test_async_smart_actions.py',
    'tests/unit/test_playwright',
    'tests/unit/test_selenium',
    'tests/unit/test_modern_engine_selector.py',
    'framework/',  # Framework code can import engines
    'conftest.py',  # Conftest sets up fixtures
]


def is_allowed_file(file_path: Path) -> bool:
    """Check if file is allowed to import engines."""
    # Normalize path to use forward slashes for comparison
    file_str = str(file_path).replace('\\', '/')
    return any(allowed in file_str for allowed in ALLOWED_FILES)


def check_test_file(file_path: Path) -> List[Dict]:
    """Check for forbidden engine imports.

    Args:
        file_path: Path to test file

    Returns:
        List of violations found
    """
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except (UnicodeDecodeError, FileNotFoundError):
        return []
    
    for line_num, line in enumerate(lines, 1):
        for pattern, engine_name in FORBIDDEN_IMPORT_PATTERNS:
            if re.search(pattern, line):
                violations.append({
                    'file': str(file_path),
                    'line': line_num,
                    'code': line.strip(),
                    'engine': engine_name,
                    'message': f'Direct {engine_name} import in test file'
                })
    
    return violations


def main():
    """Main execution."""
    test_dir = Path('tests')
    all_violations = []
    files_checked = 0
    
    print("🔍 Engine Abstraction Enforcement Check")
    print("=" * 70)
    print(f"📁 Scanning: {test_dir.absolute()}")
    print(f"🚫 Forbidden: Direct Playwright/Selenium imports")
    print(f"✅ Allowed: ui_engine fixture usage")
    print()
    
    # Find all test files
    for test_file in test_dir.rglob('test_*.py'):
        # Skip allowed files
        if is_allowed_file(test_file):
            continue
        
        files_checked += 1
        violations = check_test_file(test_file)
        all_violations.extend(violations)
    
    print(f"✓ Checked {files_checked} test files\n")
    
    if all_violations:
        print(f"❌ Found {len(all_violations)} forbidden engine imports:\n")
        
        # Group by file
        by_file = {}
        for v in all_violations:
            if v['file'] not in by_file:
                by_file[v['file']] = []
            by_file[v['file']].append(v)
        
        for file_path, violations in sorted(by_file.items()):
            print(f"📄 {file_path}")
            for v in violations:
                print(f"   Line {v['line']:4d}: {v['code']}")
                print(f"              ❌ {v['message']}")
            print()
        
        print("=" * 70)
        print(f"❌ FAIL: {len(all_violations)} violations found")
        print()
        print("💡 Fix: Remove direct imports and use ui_engine fixture:")
        print()
        print("   # ❌ WRONG")
        print("   from playwright.sync_api import Page")
        print("   def test_something(page: Page):")
        print("       page.goto('...')")
        print()
        print("   # ✅ CORRECT")
        print("   def test_something(page):  # No import, no type hint")
        print("       page.goto('...')  # Uses abstracted page via fixture")
        print()
        sys.exit(1)
    else:
        print("=" * 70)
        print("✅ PASS: No direct engine imports found in test files")
        print()
        sys.exit(0)


if __name__ == '__main__':
    main()
