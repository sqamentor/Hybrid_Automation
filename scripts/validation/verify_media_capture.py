#!/usr/bin/env python
"""
Quick Test Runner - Verify Screenshot and Video Recording
==========================================================

This script runs a single test to verify that:
1. Screenshots are saved to tests/bookslot/screenshots/
2. Videos are saved to videos/
3. Both appear in Allure reports

Usage:
    python verify_media_capture.py
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("SCREENSHOT & VIDEO RECORDING VERIFICATION")
print("=" * 80)
print()

# Get initial file counts
screenshots_dir = Path("tests/bookslot/screenshots")
videos_dir = Path("videos")
allure_dir = Path("allure-results")

screenshots_before = len(list(screenshots_dir.glob("*.png"))) if screenshots_dir.exists() else 0
videos_before = len(list(videos_dir.glob("*.webm"))) if videos_dir.exists() else 0

print(f"📊 Initial State:")
print(f"   Screenshots: {screenshots_before} files in {screenshots_dir}")
print(f"   Videos: {videos_before} files in {videos_dir}")
print()

# Run test
print("🚀 Running test: test_basic_info_page_loads")
print("-" * 80)
result = subprocess.run(
    [
        sys.executable, 
        "-m", 
        "pytest",
        "tests/bookslot/test_bookslot_basicinfo_page1.py::TestBasicInfoPage::test_basic_info_page_loads",
        "-v",
        "--alluredir=allure-results"
    ],
    capture_output=False
)
print("-" * 80)
print()

# Get final file counts
screenshots_after = len(list(screenshots_dir.glob("*.png"))) if screenshots_dir.exists() else 0
videos_after = len(list(videos_dir.glob("*.webm"))) if videos_dir.exists() else 0

screenshots_created = screenshots_after - screenshots_before
videos_created = videos_after - videos_before

# Report results
print("=" * 80)
print("📊 RESULTS:")
print("=" * 80)
print()

if screenshots_created > 0:
    print(f"✅ Screenshots: {screenshots_created} new file(s) created")
    print(f"   Location: {screenshots_dir}")
    newest_screenshot = max(screenshots_dir.glob("*.png"), key=lambda p: p.stat().st_mtime)
    print(f"   Latest: {newest_screenshot.name}")
else:
    print(f"❌ Screenshots: No new files created in {screenshots_dir}")

print()

if videos_created > 0:
    print(f"✅ Videos: {videos_created} new file(s) created")
    print(f"   Location: {videos_dir}")
    newest_video = max(videos_dir.glob("*.webm"), key=lambda p: p.stat().st_mtime)
    print(f"   Latest: {newest_video.name}")
    print(f"   Size: {newest_video.stat().st_size / (1024*1024):.2f} MB")
else:
    print(f"❌ Videos: No new files created in {videos_dir}")

print()

if allure_dir.exists():
    allure_files = list(allure_dir.glob("*-result.json"))
    print(f"📝 Allure: {len(allure_files)} result file(s) in {allure_dir}")
    print("   Run 'allure serve allure-results' to view HTML report")
else:
    print("⚠️  Allure: No results directory found")

print()
print("=" * 80)

if screenshots_created > 0 and videos_created > 0:
    print("✅ SUCCESS: Both screenshots and videos are working!")
    print()
    print("Next steps:")
    print("  1. Check screenshots: ls tests/bookslot/screenshots/")
    print("  2. Check videos: ls videos/")
    print("  3. View Allure report: allure serve allure-results")
elif screenshots_created > 0:
    print("⚠️  PARTIAL: Screenshots work, but videos not created")
    print("   Check Playwright installation and browser context configuration")
elif videos_created > 0:
    print("⚠️  PARTIAL: Videos work, but screenshots not created")
    print("   Check save_screenshot() function calls in test file")
else:
    print("❌ FAILED: Neither screenshots nor videos were created")
    print("   Check test execution logs for errors")

print("=" * 80)

sys.exit(0 if (screenshots_created > 0 and videos_created > 0) else 1)
