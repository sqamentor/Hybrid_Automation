#!/usr/bin/env python3
"""Engine Marker Enforcement Tool.

Detects test files missing @pytest.mark.modern_spa or @pytest.mark.legacy_ui markers.
This ensures the framework can automatically route tests to the correct engine.

Usage:
    python enforce_markers.py
    python enforce_markers.py --strict

Exit Codes:
    0 - All tests have engine markers
    1 - Missing markers detected

Author: Principal QA Architect
Date: January 31, 2026
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict

# Excluded paths (unit tests, helpers, etc.)
EXCLUDED_PATTERNS = [
    'tests/unit/',
    'tests/__pycache__/',
    'conftest.py',
    '__init__.py',
]

# Required engine markers
REQUIRED_MARKERS = ['modern_spa', 'legacy_ui', 'playwright', 'selenium']


def check_test_file(file_path: Path) -> List[Dict]:
    """Check if test file has required engine markers.

    Args:
        file_path: Path to test file

    Returns:
        List of violations found
    """
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content, filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError) as e:
        return []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
            has_engine_marker = False
            markers_found = []
            
            # Check decorators on class
            for decorator in node.decorator_list:
                marker_name = None
                
                if isinstance(decorator, ast.Call):
                    # @pytest.mark.modern_spa()
                    if isinstance(decorator.func, ast.Attribute):
                        marker_name = decorator.func.attr
                elif isinstance(decorator, ast.Attribute):
                    # @pytest.mark.modern_spa
                    marker_name = decorator.attr
                
                if marker_name:
                    markers_found.append(marker_name)
                    if marker_name in REQUIRED_MARKERS:
                        has_engine_marker = True
            
            if not has_engine_marker:
                violations.append({
                    'file': str(file_path),
                    'class': node.name,
                    'line': node.lineno,
                    'markers_found': markers_found,
                    'message': f'Test class missing engine marker (modern_spa or legacy_ui)'
                })
    
    return violations


def main():
    """Main execution."""
    test_dir = Path('tests')
    all_violations = []
    files_checked = 0
    
    print("🔍 Engine Marker Enforcement Check")
    print("=" * 70)
    print(f"📁 Scanning: {test_dir.absolute()}")
    print(f"🎯 Required markers: {', '.join(REQUIRED_MARKERS)}")
    print()
    
    # Find all test files
    for test_file in test_dir.rglob('test_*.py'):
        # Skip excluded patterns
        if any(pattern in str(test_file) for pattern in EXCLUDED_PATTERNS):
            continue
        
        files_checked += 1
        violations = check_test_file(test_file)
        all_violations.extend(violations)
    
    print(f"✓ Checked {files_checked} test files\n")
    
    if all_violations:
        print(f"❌ Found {len(all_violations)} test classes missing engine markers:\n")
        
        # Group by file
        by_file = {}
        for v in all_violations:
            if v['file'] not in by_file:
                by_file[v['file']] = []
            by_file[v['file']].append(v)
        
        for file_path, violations in sorted(by_file.items()):
            print(f"📄 {file_path}")
            for v in violations:
                print(f"   Line {v['line']:4d}: {v['class']}")
                if v['markers_found']:
                    print(f"              Has: {', '.join(v['markers_found'])}")
                print(f"              Need: @pytest.mark.modern_spa or @pytest.mark.legacy_ui")
            print()
        
        print("=" * 70)
        print(f"❌ FAIL: {len(all_violations)} violations found")
        print()
        print("💡 Add one of these markers to each test class:")
        print("   @pytest.mark.modern_spa  - For modern SPAs (React, Vue, Angular)")
        print("   @pytest.mark.legacy_ui   - For legacy apps (JSP, iframes, SSO)")
        print()
        sys.exit(1)
    else:
        print("=" * 70)
        print("✅ PASS: All test classes have engine markers")
        print()
        sys.exit(0)


if __name__ == '__main__':
    main()
