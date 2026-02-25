"""
Test Data Module for Bookslot

Centralized test data management.
Contains constants, data sets, and data generation utilities.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import random
import string


# ==================== CONSTANTS ====================

# Field Constraints
MAX_NAME_LENGTH = 50
MAX_ADDRESS_LENGTH = 200
MAX_CITY_LENGTH = 50
MIN_AGE = 18
MAX_AGE = 120

# Format Patterns
EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
PHONE_PATTERN = r"^\d{10}$"
ZIP_CODE_PATTERN_5 = r"^\d{5}$"
ZIP_CODE_PATTERN_9 = r"^\d{5}-\d{4}$"


# ==================== US STATES ====================

US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming"
}


# ==================== INSURANCE PROVIDERS ====================

INSURANCE_PAYERS = [
    "Blue Cross Blue Shield",
    "Aetna",
    "UnitedHealthcare",
    "Cigna",
    "Humana",
    "Kaiser Permanente",
    "Anthem",
    "WellCare",
    "Molina Healthcare",
    "Centene"
]


# ==================== REFERRAL SOURCES ====================

REFERRAL_SOURCES = {
    "doctor": "Primary Care Doctor",
    "specialist": "Specialist Referral",
    "online": "Online Search",
    "insurance": "Insurance Provider",
    "friend": "Friend/Family",
    "advertisement": "Advertisement",
    "social_media": "Social Media",
    "other": "Other"
}


# ==================== SAMPLE NAMES ====================

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Barbara", "David", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris"
]

NAMES_WITH_SPECIAL_CHARS = [
    ("Mary-Jane", "Smith-Jones"),
    ("Jean-Paul", "Dubois"),
    ("Patrick", "O'Brien"),
    ("Sinéad", "O'Connor"),
    ("José", "García"),
    ("François", "Beaumont")
]


# ==================== SAMPLE ADDRESSES ====================

STREET_ADDRESSES = [
    "123 Main Street",
    "456 Oak Avenue",
    "789 Pine Road",
    "321 Elm Boulevard",
    "654 Maple Drive",
    "987 Cedar Lane",
    "147 Birch Court",
    "258 Ash Way"
]

CITIES = {
    "MA": ["Boston", "Cambridge", "Worcester", "Springfield", "Lowell"],
    "NY": ["New York", "Buffalo", "Rochester", "Albany", "Syracuse"],
    "CA": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "San Jose"],
    "TX": ["Houston", "Dallas", "Austin", "San Antonio", "Fort Worth"],
    "FL": ["Miami", "Orlando", "Tampa", "Jacksonville", "Tallahassee"]
}


# ==================== DATA GENERATORS ====================

def generate_test_email(prefix: str = "test") -> str:
    """Generate unique test email address"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=4))
    return f"{prefix}_{timestamp}_{random_suffix}@example.com"


def generate_test_phone() -> str:
    """Generate valid test phone number"""
    # Format: 555-XXX-XXXX (555 is test prefix)
    return f"555{random.randint(1000000, 9999999)}"


def generate_member_id() -> str:
    """Generate test insurance member ID"""
    prefix = ''.join(random.choices(string.ascii_uppercase, k=3))
    numbers = ''.join(random.choices(string.digits, k=8))
    return f"{prefix}{numbers}"


def generate_group_number() -> str:
    """Generate test insurance group number"""
    prefix = "GRP"
    numbers = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}{numbers}"


def generate_confirmation_number() -> str:
    """Generate booking confirmation number format"""
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=8))
    return f"{letters}{numbers}"


def generate_date_of_birth(age: int = 30) -> str:
    """Generate date of birth for specific age (in YYYY-MM-DD format)"""
    today = datetime.now()
    dob = today - timedelta(days=365 * age)
    return dob.strftime("%Y-%m-%d")


def generate_random_zip_code() -> str:
    """Generate random 5-digit zip code"""
    return ''.join(random.choices(string.digits, k=5))


# ==================== PRESET DATA SETS ====================

class TestDataSets:
    """Predefined data sets for testing"""
    
    @staticmethod
    def get_valid_basic_info() -> Dict[str, str]:
        """Get valid basic info data"""
        return {
            "name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            "email": generate_test_email(),
            "phone": generate_test_phone()
        }
    
    @staticmethod
    def get_valid_personal_info(state: str = "MA") -> Dict[str, str]:
        """Get valid personal info data"""
        return {
            "first_name": random.choice(FIRST_NAMES),
            "last_name": random.choice(LAST_NAMES),
            "dob": generate_date_of_birth(30),
            "address": random.choice(STREET_ADDRESSES),
            "city": random.choice(CITIES.get(state, ["Boston"])),
            "state": state,
            "zip_code": generate_random_zip_code()
        }
    
    @staticmethod
    def get_valid_insurance_info(payer: str = None) -> Dict[str, str]:
        """Get valid insurance info data"""
        return {
            "member_id": generate_member_id(),
            "group_number": generate_group_number(),
            "payer": payer or random.choice(INSURANCE_PAYERS)
        }
    
    @staticmethod
    def get_invalid_emails() -> List[str]:
        """Get list of invalid email formats"""
        return [
            "invalid",
            "invalid@",
            "@invalid.com",
            "invalid@.com",
            "invalid..test@example.com",
            "invalid @example.com",
            "invalid@exam ple.com"
        ]
    
    @staticmethod
    def get_invalid_phones() -> List[str]:
        """Get list of invalid phone formats"""
        return [
            "123",
            "ABCDEFGHIJ",
            "123-456-7890",  # Wrong format
            "12345",
            "(555) 555-5555"  # Wrong format if expecting 10 digits only
        ]
    
    @staticmethod
    def get_invalid_zip_codes() -> List[str]:
        """Get list of invalid zip code formats"""
        return [
            "123",
            "ABCDE",
            "12345678",
            "12-345",
            "1234A"
        ]
    
    @staticmethod
    def get_boundary_dates() -> Dict[str, str]:
        """Get boundary date test cases"""
        today = datetime.now()
        return {
            "today": today.strftime("%Y-%m-%d"),
            "tomorrow": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
            "yesterday": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
            "min_age": generate_date_of_birth(MIN_AGE),
            "max_age": generate_date_of_birth(MAX_AGE),
            "under_min_age": generate_date_of_birth(MIN_AGE - 1)
        }


# ==================== DATA VALIDATION UTILITIES ====================

def validate_email_format(email: str) -> bool:
    """Validate email format"""
    import re
    return bool(re.match(EMAIL_PATTERN, email))


def validate_phone_format(phone: str) -> bool:
    """Validate phone format (10 digits)"""
    import re
    return bool(re.match(PHONE_PATTERN, phone))


def validate_zip_code_format(zip_code: str) -> bool:
    """Validate zip code format"""
    import re
    return bool(re.match(ZIP_CODE_PATTERN_5, zip_code)) or \
           bool(re.match(ZIP_CODE_PATTERN_9, zip_code))


def calculate_age_from_dob(dob: str) -> int:
    """Calculate age from date of birth"""
    try:
        dob_date = datetime.strptime(dob, "%Y-%m-%d")
        today = datetime.now()
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
        return age
    except:
        return -1


# ==================== EXPORT CONVENIENCE ====================

__all__ = [
    # Constants
    "US_STATES",
    "INSURANCE_PAYERS",
    "REFERRAL_SOURCES",
    "FIRST_NAMES",
    "LAST_NAMES",
    "STREET_ADDRESSES",
    "CITIES",
    
    # Generators
    "generate_test_email",
    "generate_test_phone",
    "generate_member_id",
    "generate_group_number",
    "generate_confirmation_number",
    "generate_date_of_birth",
    "generate_random_zip_code",
    
    # Data Sets
    "TestDataSets",
    
    # Validators
    "validate_email_format",
    "validate_phone_format",
    "validate_zip_code_format",
    "calculate_age_from_dob"
]
