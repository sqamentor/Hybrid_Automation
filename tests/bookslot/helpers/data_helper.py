"""
Bookslot Test Data Helper

Provides test data generation for all 7 pages of Bookslot flow.
Supports:
- Valid data generation
- Invalid data generation (for negative tests)
- Boundary value data
- Data variants (AM/PM, referral sources, payers, etc.)

Usage:
    data_helper = BookslotDataHelper()
    basic_info = data_helper.get_valid_basic_info()
    invalid_email = data_helper.get_invalid_basic_info(field="email")
"""

from typing import Dict, List, Any
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()


class BookslotDataHelper:
    """
    Test data generation helper for Bookslot project.
    Provides deterministic and randomized test data.
    """
    
    def __init__(self, seed: int = None):
        """
        Initialize data helper.
        
        Args:
            seed: Random seed for reproducible data (optional)
        """
        if seed:
            Faker.seed(seed)
            random.seed(seed)
        
        self.fake = Faker()
    
    # ========================================================================
    # P1: BASIC INFO DATA
    # ========================================================================
    
    def get_valid_basic_info(self, **overrides) -> Dict[str, str]:
        """
        Get valid basic info data for P1.
        
        Args:
            **overrides: Override specific fields
        
        Returns:
            Dict with first_name, last_name, email, phone
        """
        data = {
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "email": self.fake.email(),
            "phone": self.fake.numerify(text="##########")  # 10 digits
        }
        data.update(overrides)
        return data
    
    def get_invalid_basic_info(self, field: str) -> Dict[str, str]:
        """
        Get basic info with one invalid field (for negative testing).
        
        Args:
            field: Field to make invalid (email, phone, first_name, last_name)
        
        Returns:
            Dict with one invalid field
        """
        data = self.get_valid_basic_info()
        
        invalid_values = {
            "email": "invalid-email",  # Missing @ and domain
            "phone": "12345",  # Too short
            "first_name": "",  # Empty (if required)
            "last_name": "",  # Empty (if required)
        }
        
        if field in invalid_values:
            data[field] = invalid_values[field]
        
        return data
    
    # ========================================================================
    # P2: EVENT TYPE DATA
    # ========================================================================
    
    def get_event_type_options(self) -> List[str]:
        """Get available event type options"""
        return [
            "New Patient Consultation",
            "Follow-up Appointment",
            "Emergency Consultation",
            "Video Consultation",
            "Lab Results Review",
            "Prescription Renewal"
        ]
    
    def get_random_event_type(self) -> str:
        """Get a random event type"""
        return random.choice(self.get_event_type_options())
    
    # ========================================================================
    # P3: SCHEDULER DATA
    # ========================================================================
    
    def get_scheduler_data(self, time_preference: str = "AM", **overrides) -> Dict[str, Any]:
        """
        Get scheduler data for P3.
        
        Args:
            time_preference: "AM" or "PM"
            **overrides: Override specific fields
        
        Returns:
            Dict with slot_strategy, time_preference, date (optional)
        """
        data = {
            "slot_strategy": "first_available",
            "time_preference": time_preference,
            "date": None  # Use default date (usually today or tomorrow)
        }
        data.update(overrides)
        return data
    
    def get_specific_date(self, days_from_now: int = 7) -> str:
        """
        Get a specific date N days from now.
        
        Args:
            days_from_now: Number of days to add to today
        
        Returns:
            Date string in format MM/DD/YYYY
        """
        target_date = datetime.now() + timedelta(days=days_from_now)
        return target_date.strftime("%m/%d/%Y")
    
    # ========================================================================
    # P4: PERSONAL INFO DATA
    # ========================================================================
    
    def get_valid_personal_info(self, **overrides) -> Dict[str, str]:
        """
        Get valid personal info data for P4.
        
        Args:
            **overrides: Override specific fields
        
        Returns:
            Dict with dob, address, city, state, zip
        """
        data = {
            "dob": self.fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%m/%d/%Y"),
            "address": self.fake.street_address(),
            "city": self.fake.city(),
            "state": random.choice(["MA", "NY", "CA", "TX", "FL"]),
            "zip": self.fake.zipcode()
        }
        data.update(overrides)
        return data
    
    def get_invalid_personal_info(self, field: str) -> Dict[str, str]:
        """
        Get personal info with one invalid field.
        
        Args:
            field: Field to make invalid
        
        Returns:
            Dict with one invalid field
        """
        data = self.get_valid_personal_info()
        
        invalid_values = {
            "dob": "13/32/2025",  # Invalid date
            "zip": "123",  # Too short
            "city": "",  # Empty
            "state": "XX",  # Invalid state
        }
        
        if field in invalid_values:
            data[field] = invalid_values[field]
        
        return data
    
    def get_boundary_dob_data(self) -> List[Dict[str, str]]:
        """
        Get boundary value test data for date of birth.
        
        Returns:
            List of test data dicts with boundary dates
        """
        today = datetime.now()
        
        return [
            {"description": "Exactly 18 years old", "dob": (today - timedelta(days=365*18)).strftime("%m/%d/%Y")},
            {"description": "17 years old (underage)", "dob": (today - timedelta(days=365*17)).strftime("%m/%d/%Y")},
            {"description": "100 years old", "dob": (today - timedelta(days=365*100)).strftime("%m/%d/%Y")},
            {"description": "Future date", "dob": (today + timedelta(days=365)).strftime("%m/%d/%Y")},
        ]
    
    # ========================================================================
    # P5: REFERRAL DATA
    # ========================================================================
    
    def get_referral_sources(self) -> List[str]:
        """Get available referral sources"""
        return ["web", "phone", "referral", "walk-in", "email"]
    
    def get_referral_data(self, source: str = "web", **overrides) -> Dict[str, str]:
        """
        Get referral data for P5.
        
        Args:
            source: Referral source (web, phone, referral, etc.)
            **overrides: Override specific fields
        
        Returns:
            Dict with source and optional details
        """
        data = {
            "source": source
        }
        
        # Add source-specific fields if needed
        if source == "referral":
            data["referral_name"] = self.fake.name()
            data["referral_phone"] = self.fake.numerify(text="##########")
        
        data.update(overrides)
        return data
    
    def get_random_referral_source(self) -> str:
        """Get a random referral source"""
        return random.choice(self.get_referral_sources())
    
    # ========================================================================
    # P6: INSURANCE DATA
    # ========================================================================
    
    def get_valid_insurance_info(self, **overrides) -> Dict[str, str]:
        """
        Get valid insurance info data for P6.
        
        Args:
            **overrides: Override specific fields
        
        Returns:
            Dict with member_id, group_number, payer, etc.
        """
        data = {
            "member_id": self.fake.numerify(text="INS########"),
            "group_number": self.fake.numerify(text="GRP####"),
            "payer": random.choice(self.get_insurance_payers()),
            "policy_holder": "self"  # or "spouse", "parent", "other"
        }
        data.update(overrides)
        return data
    
    def get_insurance_payers(self) -> List[str]:
        """Get available insurance payers"""
        return [
            "Blue Cross Blue Shield",
            "Aetna",
            "UnitedHealthcare",
            "Cigna",
            "Humana",
            "Medicare",
            "Medicaid"
        ]
    
    def get_invalid_insurance_info(self, field: str) -> Dict[str, str]:
        """
        Get insurance info with one invalid field.
        
        Args:
            field: Field to make invalid
        
        Returns:
            Dict with one invalid field
        """
        data = self.get_valid_insurance_info()
        
        invalid_values = {
            "member_id": "",  # Empty
            "group_number": "12",  # Too short
            "payer": "",  # Not selected
        }
        
        if field in invalid_values:
            data[field] = invalid_values[field]
        
        return data
    
    # ========================================================================
    # COMBINED DATA (Full Flow)
    # ========================================================================
    
    def get_complete_booking_data(
        self,
        time_preference: str = "AM",
        referral_source: str = "web"
    ) -> Dict[str, Dict]:
        """
        Get complete data for entire booking flow (P1-P6).
        
        Args:
            time_preference: "AM" or "PM" for scheduler
            referral_source: Referral source for P5
        
        Returns:
            Dict with data for all 6 pages
        """
        return {
            "basic_info": self.get_valid_basic_info(),
            "event_type": {"selection": self.get_random_event_type()},
            "scheduler": self.get_scheduler_data(time_preference),
            "personal_info": self.get_valid_personal_info(),
            "referral": self.get_referral_data(referral_source),
            "insurance": self.get_valid_insurance_info()
        }
    
    # ========================================================================
    # DATA VARIANTS (For Parametrized Tests)
    # ========================================================================
    
    def get_time_preference_variants(self) -> List[str]:
        """Get time preference variants for scheduler"""
        return ["AM", "PM"]
    
    def get_referral_source_variants(self) -> List[str]:
        """Get referral source variants"""
        return self.get_referral_sources()
    
    def get_insurance_payer_variants(self) -> List[str]:
        """Get insurance payer variants"""
        return self.get_insurance_payers()
    
    def get_all_variants(self) -> Dict[str, List[str]]:
        """
        Get all data variants for parametrized testing.
        
        Returns:
            Dict mapping variant type to list of values
        """
        return {
            "time_preference": self.get_time_preference_variants(),
            "referral_source": self.get_referral_source_variants(),
            "insurance_payer": self.get_insurance_payer_variants()
        }
