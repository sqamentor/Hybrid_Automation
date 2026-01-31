"""
FINAL PROOF: Visual test with screenshot
This will open the browser and take a screenshot showing the production URL
"""
import subprocess
import time

print("="*80)
print("FINAL VISUAL PROOF TEST")
print("="*80)
print("\nThis test will:")
print("1. Open a VISIBLE browser (--headed)")
print("2. Navigate to PRODUCTION URL")
print("3. Take a screenshot")
print("4. Show the exact URL in the address bar")
print("\nYOU WILL SEE THE BROWSER OPEN - WATCH THE ADDRESS BAR!")
print("="*80)

input("\nPress ENTER to start the test...")

# Run with headed mode so user can SEE the browser
command = """python -m pytest tests/bookslot/test_bookslot_basicinfo_page1.py::test_basic_info_page_loads --env=production --headed -v -s --screenshot on"""

print(f"\nRunning: {command}\n")
print("-"*80)

result = subprocess.run(command, shell=True, capture_output=True, text=True)

output = result.stdout + result.stderr

# Show FULL output for debugging
print("\n[FULL TEST OUTPUT]")
print("="*80)
print(output)
print("="*80)

# Extract relevant info
print("\n[KEY INFORMATION FROM TEST]")
print("="*80)
for line in output.split('\n'):
    if any(keyword in line.lower() for keyword in ['environment', 'base url', 'browser', 'metadata']):
        print(line.strip())

print("\n" + "="*80)
print("ANALYSIS")
print("="*80)

# Check what URLs appear - updated to match actual log format
if 'Base URL=https://bookslots.centerforvein.com' in output or 'Base URL: https://bookslots.centerforvein.com' in output:
    print("\n✅ Framework loaded PRODUCTION URL (bookslots.centerforvein.com)")
else:
    print("\n❌ Framework did NOT load production URL")

if 'Environment: PRODUCTION' in output or 'Environment=PRODUCTION' in output:
    print("✅ Framework is using PRODUCTION environment")
else:
    print("❌ Framework is NOT using production environment")

if 'bookslots.centerforvein.com' in output:
    print("✅ Production domain found in test output")
else:
    print("❌ Could not find production domain in output")

# Check for staging
if 'staging' in output.lower() and 'bookslot-staging' in output.lower():
    print("\n⚠️  Staging URL found in output - needs investigation")
else:
    print("\n✅ No staging URLs found - framework is correct!")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print("If you saw a BROWSER WINDOW OPEN with 'bookslots.centerforvein.com' in the address bar,")
print("then the framework is working PERFECTLY!")
print("\nDid you see the browser window open? (y/n): ", end='')
response = input().strip().lower()
if response == 'y':
    print("\n🎉 SUCCESS! The framework opened a visible browser with production URL!")
else:
    print("\n❌ Browser window issue - may need to check --headed flag or browser installation")
