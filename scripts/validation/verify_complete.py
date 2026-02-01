"""Complete End-to-End Verification Script This simulates the exact CLI flow and shows all URLs."""
import subprocess
import sys

print("="*80)
print("COMPLETE ENVIRONMENT VERIFICATION")
print("="*80)

# Test 1: Verify CommandBuilder builds correct command
print("\n[TEST 1] Command Builder Test")
print("-" * 80)
from run_tests_cli import CommandBuilder

builder = CommandBuilder()
builder.set_test_path('pages/bookslot/bookslots_basicinfo.py')
builder.add_verbose()
builder.add_headed_mode()
builder.add_environment('production')

cmd = builder.build()
print(f"Built command: {cmd}")

if '--env=production' in cmd:
    print("✅ Command contains --env=production")
else:
    print("❌ ERROR: --env=production NOT in command!")
    sys.exit(1)

# Test 2: Verify pytest receives the environment
print("\n[TEST 2] Pytest Environment Reception Test")
print("-" * 80)
print("Running: python -m pytest pages/bookslot/bookslots_basicinfo.py --env=production --co")

result = subprocess.run(
    "python -m pytest pages/bookslot/bookslots_basicinfo.py --env=production --co -v",
    shell=True,
    capture_output=True,
    text=True
)

if 'collected 1 item' in result.stdout:
    print("✅ Test collected successfully")
else:
    print("❌ Test collection failed")

# Test 3: Verify fixture loads correct URL
print("\n[TEST 3] Fixture URL Loading Test")  
print("-" * 80)
print("Checking conftest output for URL...")

result = subprocess.run(
    "python -m pytest pages/bookslot/bookslots_basicinfo.py::test_bookslot_basic_info_form_validation --env=production --co -v -s",
    shell=True,
    capture_output=True,
    text=True
)

output = result.stdout + result.stderr
if 'bookslots.centerforvein.com' in output:
    print("✅ Production URL (bookslots.centerforvein.com) found in output")
elif 'bookslot-staging.centerforvein.com' in output:
    print("❌ ERROR: Staging URL found instead of production!")
else:
    print("⚠️  Could not verify URL in output")

print(f"\nSearching output for URL...")
for line in output.split('\n'):
    if 'bookslot' in line.lower() and ('url' in line.lower() or 'http' in line.lower()):
        print(f"  {line.strip()}")

print("\n" + "="*80)
print("VERIFICATION COMPLETE")
print("="*80)
print("\nIf all tests show ✅, the framework is working correctly.")
print("The browser should open: https://bookslots.centerforvein.com/basic-info")
print("\nIf you see a different URL in the browser, the WEBSITE is redirecting.")
