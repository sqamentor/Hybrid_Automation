"""
Test Dynamic HTML Report Naming - Verification Script
======================================================

This script verifies that the dynamic HTML report naming system works correctly.

Expected Behavior:
- Report names follow format: projectname_EnvironmentName_DDMMYYYY_HHMMSS.html
- If file exists, appends _1, _2, etc.
- Custom filenames via --html=custom.html are respected

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import generate_unique_report_filename


def test_dynamic_report_naming():
    """Test dynamic report name generation"""
    print("\n" + "="*80)
    print("🧪 TESTING DYNAMIC HTML REPORT NAMING")
    print("="*80 + "\n")
    
    # Test 1: Basic naming
    print("📝 Test 1: Basic report name generation")
    report_name = generate_unique_report_filename("bookslot", "staging")
    print(f"   Generated: {report_name}")