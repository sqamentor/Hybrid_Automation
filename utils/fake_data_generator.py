"""
Fake Data Generator Utility for Bookslot Testing
================================================
This utility generates realistic fake data for bookslot testing using Faker library.
Data is saved to both JSON and YAML formats in the test_data/bookslot directory.

Usage:
    # Generate data programmatically
    from utils.fake_data_generator import generate_bookslot_payload, generate_and_save_bookslot_data
    
    # Generate single payload
    data = generate_bookslot_payload()
    
    # Generate and save multiple payloads
    data_list = generate_and_save_bookslot_data(count=10)
    
    # Run from command line
    python utils/fake_data_generator.py
"""

from faker import Faker
import random
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any

# Initialize Faker
fake = Faker()

# Define paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "test_data" / "bookslot"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Configuration constants
PAYER_LIST = [
    "Aetna Health",
    "Blue Cross Blue Shield",
    "UnitedHealthcare",
    "Cigna",
    "Humana"
]

ALLOWED_EMAIL_DOMAINS = ["mailinator.com", "yopmail.com"]
STATIC_PHONE = "1234567890"
STATIC_VERIFICATION_CODE = "123456"
STATIC_ZIP = ["20678","20678","20678","20678","20678"][random.randint(0,4)]
CONTACT_METHODS = ["Text", "Email", "Call"]
ZIP_DISTANCES = ["5","25", "50", "75", "100"]


def generate_custom_email() -> str:
    """
    Generate a custom email using allowed temporary email domains.
    
    Returns:
        str: Email address with mailinator.com or yopmail.com domain
    """
    username = fake.user_name()
    domain = random.choice(ALLOWED_EMAIL_DOMAINS)
    return f"{username}@{domain}"


def generate_bookslot_payload() -> Dict[str, Any]:
    """
    Generate a single bookslot test data payload with all required fields.
    
    Returns:
        dict: Complete bookslot payload with personal info and insurance details
    """
    return {
        # Personal Information
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": generate_custom_email(),
        "phone_number": STATIC_PHONE,
        "zip": STATIC_ZIP,
        "contact_method": random.choice(["Text"]),  # Primarily Text, can be expanded
        "verification_code": STATIC_VERIFICATION_CODE,
        "zip_distance": random.choice(ZIP_DISTANCES),
        "dob": fake.date_of_birth(minimum_age=18, maximum_age=85).strftime("%m/%d/%Y"),
        
        # Insurance Information
        "MemberName": fake.name(),
        "idNumber": f"INS-{random.randint(10000, 99999)}",
        "GroupNumber": f"GRP-{random.randint(1000, 9999)}",
        "PayerName": random.choice(PAYER_LIST)
    }


def generate_bookslot_payload_with_options(
    use_dynamic_zip: bool = False,
    use_all_contact_methods: bool = False,
    state: str = "MD"
) -> Dict[str, Any]:
    """
    Generate a bookslot payload with configurable options.
    
    Args:
        use_dynamic_zip: If True, generates random ZIP code for the specified state
        use_all_contact_methods: If True, allows all contact methods instead of just "Text"
        state: State code for ZIP generation (default: "MD")
        
    Returns:
        dict: Bookslot payload with custom configuration
    """
    payload = generate_bookslot_payload()
    
    if use_dynamic_zip:
        payload["zip"] = fake.zipcode_in_state(state)
    
    if use_all_contact_methods:
        payload["contact_method"] = random.choice(CONTACT_METHODS)
    
    return payload


def generate_and_save_bookslot_data(count: int = 5, filename_prefix: str = "bookslot_data") -> List[Dict[str, Any]]:
    """
    Generate multiple bookslot payloads and save to JSON and YAML files.
    
    Args:
        count: Number of bookslot payloads to generate (default: 5)
        filename_prefix: Prefix for output files (default: "bookslot_data")
        
    Returns:
        list: List of generated bookslot payloads
    """
    data_list = [generate_bookslot_payload() for _ in range(count)]
    
    # Save to JSON
    json_path = OUTPUT_DIR / f"{filename_prefix}.json"
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(data_list, jf, indent=4, ensure_ascii=False)
    print(f"✅ Bookslot JSON saved to: {json_path}")
    
    # Save to YAML
    yaml_path = OUTPUT_DIR / f"{filename_prefix}.yaml"
    with open(yaml_path, "w", encoding="utf-8") as yf:
        yaml.dump(data_list, yf, default_flow_style=False, allow_unicode=True)
    print(f"✅ Bookslot YAML saved to: {yaml_path}")
    
    return data_list


def generate_and_save_with_options(
    count: int = 5,
    filename_prefix: str = "bookslot_data_custom",
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Generate multiple bookslot payloads with custom options and save to files.
    
    Args:
        count: Number of bookslot payloads to generate
        filename_prefix: Prefix for output files
        **kwargs: Options to pass to generate_bookslot_payload_with_options
        
    Returns:
        list: List of generated bookslot payloads
    """
    data_list = [generate_bookslot_payload_with_options(**kwargs) for _ in range(count)]
    
    # Save to JSON
    json_path = OUTPUT_DIR / f"{filename_prefix}.json"
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(data_list, jf, indent=4, ensure_ascii=False)
    print(f"✅ Bookslot JSON (custom) saved to: {json_path}")
    
    # Save to YAML
    yaml_path = OUTPUT_DIR / f"{filename_prefix}.yaml"
    with open(yaml_path, "w", encoding="utf-8") as yf:
        yaml.dump(data_list, yf, default_flow_style=False, allow_unicode=True)
    print(f"✅ Bookslot YAML (custom) saved to: {yaml_path}")
    
    return data_list


def load_bookslot_data(filename: str = "bookslot_data.json") -> List[Dict[str, Any]]:
    """
    Load bookslot data from a JSON file.
    
    Args:
        filename: Name of the JSON file to load (default: "bookslot_data.json")
        
    Returns:
        list: List of bookslot payloads
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    """
    Main function for command-line usage.
    Generates 5 bookslot payloads and saves them to JSON and YAML.
    """
    print("\n" + "=" * 60)
    print("📝 Bookslot Fake Data Generator")
    print("=" * 60 + "\n")
    
    # Generate default data
    print("Generating 5 default bookslot payloads...")
    default_data = generate_and_save_bookslot_data(count=5)
    
    print(f"\n📊 Generated {len(default_data)} records")
    print("\n✨ Sample record:")
    print(json.dumps(default_data[0], indent=2))
    
    # Generate custom data with dynamic zips
    print("\n" + "-" * 60)
    print("\nGenerating 3 custom bookslot payloads with dynamic ZIP codes...")
    custom_data = generate_and_save_with_options(
        count=3,
        filename_prefix="bookslot_data_dynamic_zip",
        use_dynamic_zip=True,
        use_all_contact_methods=True
    )
    
    print(f"\n📊 Generated {len(custom_data)} custom records")
    print("\n" + "=" * 60)
    print("✅ Data generation complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
