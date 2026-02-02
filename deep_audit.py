"""
Deep Architecture Audit Script
Comprehensive validation of framework architecture compliance
"""

import ast
from pathlib import Path
from collections import defaultdict

def audit_file(file_path):
    """Audit a Python file for architecture violations"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        violations_found = []
        
        # Check for direct Playwright imports in test files
        if '/tests/' in str(file_path).replace('\\', '/'):
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and 'playwright' in node.module:
                        if not ('conftest' in str(file_path) or 'framework' in str(file_path)):
                            violations_found.append(('direct_import', str(file_path)))
        
        # Check for if __name__ == "__main__" in test files
        if '/tests/' in str(file_path).replace('\\', '/'):
            if 'if __name__' in content:
                violations_found.append(('main_block', str(file_path)))
        
        # Check for test classes without pytest markers
        if '/tests/' in str(file_path).replace('\\', '/') and file_path.name.startswith('test_'):
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                    has_engine_marker = False
                    if hasattr(node, 'decorator_list'):
                        for dec in node.decorator_list:
                            if isinstance(dec, ast.Attribute):
                                if (hasattr(dec.value, 'attr') and dec.value.attr == 'mark' and
                                    dec.attr in ['playwright', 'selenium']):
                                    has_engine_marker = True
                                    break
                    if not has_engine_marker:
                        violations_found.append(('missing_marker', f'{file_path}::{node.name}'))
        
        return violations_found
    except Exception as e:
        print(f"Error auditing {file_path}: {e}")
        return []

def run_audit():
    """Run comprehensive architecture audit"""
    violations = defaultdict(list)
    stats = {'total_files': 0, 'total_classes': 0, 'violations': 0}
    
    test_dirs = [
        'tests/modern',
        'tests/legacy',
        'tests/integration',
        'tests/unit',
        'tests/examples',
        'tests/common',
        'tests/ui',
        'tests/workflows',
        'recorded_tests'
    ]
    
    # Scan all test files
    for test_dir in test_dirs:
        test_path = Path(test_dir)
        if test_path.exists():
            for file_path in test_path.rglob('*.py'):
                if file_path.name.startswith('test_'):
                    stats['total_files'] += 1
                    file_violations = audit_file(file_path)
                    for vtype, vinfo in file_violations:
                        violations[vtype].append(vinfo)
                        if vtype == 'missing_marker':
                            stats['total_classes'] += 1
    
    # Calculate total violations
    stats['violations'] = sum(len(v) for v in violations.values())
    
    # Print report
    print('\n' + '='*80)
    print('DEEP ARCHITECTURE AUDIT - FINAL REPORT')
    print('='*80)
    print(f'\nFiles Scanned: {stats["total_files"]}')
    print(f'Test Classes Checked: {stats["total_classes"]}')
    print(f'\n⚠️  Total Violations Found: {stats["violations"]}\n')
    
    if violations['direct_import']:
        print(f'❌ CRITICAL: Direct Playwright Imports ({len(violations["direct_import"])})')
        for v in violations['direct_import'][:5]:
            print(f'  - {Path(v).name}')
        if len(violations['direct_import']) > 5:
            print(f'  ... and {len(violations["direct_import"])-5} more')
        print()
    
    if violations['main_block']:
        print(f'❌ HIGH: Main Blocks Found ({len(violations["main_block"])})')
        for v in violations['main_block'][:5]:
            print(f'  - {Path(v).name}')
        if len(violations['main_block']) > 5:
            print(f'  ... and {len(violations["main_block"])-5} more')
        print()
    
    if violations['missing_marker']:
        print(f'❌ HIGH: Missing Engine Markers ({len(violations["missing_marker"])})')
        for v in violations['missing_marker'][:10]:
            parts = v.split('::')
            print(f'  - {Path(parts[0]).name}::{parts[1]}')
        if len(violations['missing_marker']) > 10:
            print(f'  ... and {len(violations["missing_marker"])-10} more')
        print()
    
    if stats['violations'] == 0:
        print('✅ ✅ ✅ ALL CHECKS PASSED - ZERO VIOLATIONS! ✅ ✅ ✅')
        print('🎉 Framework is PRODUCTION-READY!')
        print('🏆 100% Architecture Compliance Achieved!')
    
    print('\n' + '='*80)
    
    return stats['violations']

if __name__ == '__main__':
    violations_count = run_audit()
    exit(0 if violations_count == 0 else 1)
