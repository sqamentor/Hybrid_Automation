"""Script to automatically add @pytest.mark.modern_spa and @pytest.mark.unit markers to all unit
test classes."""

import re
from pathlib import Path

UNIT_TEST_DIR = Path("tests/unit")


def add_markers_to_file(file_path: Path):
    """Add markers to all classes in a unit test file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, FileNotFoundError):
        print(f"❌ Could not read {file_path}")
        return 0
    
    # Pattern to find class definitions without the modern_spa marker
    # Look for class definitions that don't have @pytest.mark.modern_spa before them
    pattern = r'((?:@pytest\.mark\.\w+\n)*)class\s+(\w+)'
    
    def replace_func(match):
        existing_markers = match.group(1)
        class_name = match.group(2)
        
        # Check if modern_spa marker already exists
        if '@pytest.mark.modern_spa' in existing_markers:
            return match.group(0)  # Already has marker
        
        # Check if unit marker already exists
        has_unit = '@pytest.mark.unit' in existing_markers
        
        # Add markers
        if not has_unit:
            new_markers = '@pytest.mark.modern_spa\n@pytest.mark.unit\n'
        else:
            new_markers = '@pytest.mark.modern_spa\n'
        
        return existing_markers + new_markers + f'class {class_name}'
    
    new_content = re.sub(pattern, replace_func, content)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Count classes modified
        classes_modified = len(re.findall(r'@pytest\.mark\.modern_spa\n@pytest\.mark\.unit\nclass', new_content)) + \
                          len(re.findall(r'@pytest\.mark\.modern_spa\nclass', new_content))
        return classes_modified
    
    return 0


def main():
    """Process all unit test files."""
    print("🔍 Adding markers to unit tests...")
    print(f"📁 Scanning: {UNIT_TEST_DIR.absolute()}\n")
    
    total_files = 0
    total_classes = 0
    
    for test_file in UNIT_TEST_DIR.rglob('test_*.py'):
        classes_modified = add_markers_to_file(test_file)
        if classes_modified > 0:
            total_files += 1
            total_classes += classes_modified
            print(f"✅ {test_file.name}: Added markers to {classes_modified} classes")
    
    print(f"\n" + "=" * 70)
    print(f"✅ Modified {total_classes} classes in {total_files} files")


if __name__ == '__main__':
    main()
