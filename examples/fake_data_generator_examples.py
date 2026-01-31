"""
Example: Using Fake Data Generator for Bookslot Tests
======================================================

This file demonstrates how to use the fake_data_generator utility
in your bookslot test automation.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from utils.fake_data_generator import (
    generate_bookslot_payload,
    generate_and_save_bookslot_data,
    load_bookslot_data,
    generate_bookslot_payload_with_options
)


# ============================================================================
# Example 1: Generate a single payload dynamically during test execution
# ============================================================================
def example_single_payload():
    """Generate a single bookslot payload on-the-fly"""
    print("\n=== Example 1: Single Payload ===")
    
    # Generate fresh data for each test run
    bookslot_data = generate_bookslot_payload()
    
    print(f"First Name: {bookslot_data['first_name']}")
    print(f"Last Name: {bookslot_data['last_name']}")
    print(f"Email: {bookslot_data['email']}")
    print(f"Phone: {bookslot_data['phone_number']}")
    print(f"DOB: {bookslot_data['dob']}")
    print(f"Insurance: {bookslot_data['PayerName']}")
    print(f"Member ID: {bookslot_data['idNumber']}")
    
    return bookslot_data


# ============================================================================
# Example 2: Generate and save multiple payloads to files
# ============================================================================
def example_batch_generation():
    """Generate multiple payloads and save to JSON/YAML files"""
    print("\n=== Example 2: Batch Generation ===")
    
    # Generate 10 bookslot records
    data_list = generate_and_save_bookslot_data(count=10)
    
    print(f"Generated {len(data_list)} bookslot records")
    print("Files saved to: test_data/bookslot/")
    
    return data_list


# ============================================================================
# Example 3: Load pre-generated data from file
# ============================================================================
def example_load_from_file():
    """Load previously generated data from JSON file"""
    print("\n=== Example 3: Load from File ===")
    
    try:
        # Load data from file
        data_list = load_bookslot_data("bookslot_data.json")
        
        print(f"Loaded {len(data_list)} records from file")
        print(f"First record email: {data_list[0]['email']}")
        
        return data_list
    except FileNotFoundError:
        print("No data file found. Run example_batch_generation() first!")
        return None


# ============================================================================
# Example 4: Generate payload with custom options
# ============================================================================
def example_custom_options():
    """Generate payload with custom configuration"""
    print("\n=== Example 4: Custom Options ===")
    
    # Generate with dynamic ZIP code from Maryland
    custom_data = generate_bookslot_payload_with_options(
        use_dynamic_zip=True,
        use_all_contact_methods=True,
        state="MD"
    )
    
    print(f"ZIP Code: {custom_data['zip']}")
    print(f"Contact Method: {custom_data['contact_method']}")
    
    return custom_data


# ============================================================================
# Example 5: Integration with Pytest Test
# ============================================================================
def example_pytest_usage():
    """
    Example of how to use in pytest tests
    
    In your actual test file:
    
    import pytest
    from utils.fake_data_generator import generate_bookslot_payload
    
    @pytest.fixture
    def bookslot_data():
        '''Generate fresh fake data for each test'''
        return generate_bookslot_payload()
    
    def test_bookslot_form_submission(bookslot_data, page):
        '''Test bookslot form with fake data'''
        # Navigate to bookslot page
        page.goto("https://yourapp.com/bookslot")
        
        # Fill form with fake data
        page.fill("#first_name", bookslot_data["first_name"])
        page.fill("#last_name", bookslot_data["last_name"])
        page.fill("#email", bookslot_data["email"])
        page.fill("#phone", bookslot_data["phone_number"])
        page.fill("#dob", bookslot_data["dob"])
        
        # Fill insurance fields
        page.fill("#member_name", bookslot_data["MemberName"])
        page.fill("#id_number", bookslot_data["idNumber"])
        page.select_option("#payer_name", bookslot_data["PayerName"])
        
        # Submit and verify
        page.click("#submit_button")
        assert page.is_visible(".success_message")
    
    def test_multiple_bookslots(page):
        '''Test multiple bookslot submissions'''
        # Load batch data
        from utils.fake_data_generator import load_bookslot_data
        data_list = load_bookslot_data("bookslot_data.json")
        
        for data in data_list[:3]:  # Test first 3 records
            # Use data in your test
            page.fill("#email", data["email"])
            # ... rest of the test
    """
    print("\n=== Example 5: Pytest Usage ===")
    print("See docstring for pytest integration examples")


# ============================================================================
# Example 6: Data-Driven Testing with Multiple Scenarios
# ============================================================================
def example_data_driven_testing():
    """Generate data for different test scenarios"""
    print("\n=== Example 6: Data-Driven Testing ===")
    
    scenarios = {
        "scenario_young_patient": generate_and_save_bookslot_data(
            count=5,
            filename_prefix="bookslot_young_patients"
        ),
        "scenario_senior_patient": generate_and_save_bookslot_data(
            count=5,
            filename_prefix="bookslot_senior_patients"
        ),
        "scenario_dynamic_location": generate_and_save_bookslot_data(
            count=5,
            filename_prefix="bookslot_dynamic_locations"
        )
    }
    
    print(f"Generated {len(scenarios)} test scenarios")
    for scenario_name, data in scenarios.items():
        print(f"  - {scenario_name}: {len(data)} records")
    
    return scenarios


# ============================================================================
# Main execution
# ============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎯 Bookslot Fake Data Generator - Usage Examples")
    print("=" * 70)
    
    # Run all examples
    example_single_payload()
    example_batch_generation()
    example_load_from_file()
    example_custom_options()
    example_pytest_usage()
    example_data_driven_testing()
    
    print("\n" + "=" * 70)
    print("✅ All examples completed!")
    print("=" * 70 + "\n")
