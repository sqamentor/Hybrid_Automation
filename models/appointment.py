"""Shared data model for Appointment Used across multiple projects (Bookslot, PatientIntake,
etc.)"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Appointment:
    """Appointment data shared between projects.

    This model ensures data consistency when testing across:
    - Bookslot (appointment creation)
    - PatientIntake (appointment verification)
    - Other related systems
    """
    
    # Patient Information
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    zip_code: Optional[str] = None
    
    # Appointment Details
    appointment_date: Optional[datetime] = None
    appointment_time: Optional[str] = None
    location: Optional[str] = None
    doctor: Optional[str] = None
    reason: Optional[str] = None
    
    # System IDs (populated after creation)
    bookslot_id: Optional[str] = None
    patientintake_id: Optional[str] = None
    callcenter_id: Optional[str] = None
    confirmation_code: Optional[str] = None
    verification_code: Optional[str] = None
    
    # Cancellation Information
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    cancelled_by: Optional[str] = None  # 'callcenter', 'patient', 'admin', etc.
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: str = "pending"  # pending, confirmed, completed, cancelled
    
    # Additional data
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_full_name(self) -> str:
        """Get patient's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'email': self.email,
            'phone': self.phone,
            'zip_code': self.zip_code,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time,
            'location': self.location,
            'doctor': self.doctor,
            'reason': self.reason,
            'bookslot_id': self.bookslot_id,
            'patientintake_id': self.patientintake_id,
            'callcenter_id': self.callcenter_id,
            'confirmation_code': self.confirmation_code,
            'verification_code': self.verification_code,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'cancellation_reason': self.cancellation_reason,
            'cancelled_by': self.cancelled_by,
            'status': self.status,
            'metadata': self.metadata
        }
    
    def is_cancelled(self) -> bool:
        """Check if appointment is cancelled."""
        return self.status == "cancelled" or self.cancelled_at is not None
    
    def cancel(self, reason: str = None, cancelled_by: str = "callcenter"):
        """Mark appointment as cancelled."""
        self.status = "cancelled"
        self.cancelled_at = datetime.now()
        self.cancellation_reason = reason
        self.cancelled_by = cancelled_by
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        """String representation."""
        status_str = f" [{self.status}]" if self.status != "pending" else ""
        return f"Appointment({self.get_full_name()}, {self.email}, {self.location}{status_str})"


@dataclass
class TestContext:
    """Context shared across test execution Used to pass data between test steps and across
    projects."""
    appointment: Optional[Appointment] = None
    appointments: list = field(default_factory=list)
    test_data: Dict[str, Any] = field(default_factory=dict)
    
    # Project-specific data
    bookslot_data: Dict[str, Any] = field(default_factory=dict)
    patientintake_data: Dict[str, Any] = field(default_factory=dict)
    callcenter_data: Dict[str, Any] = field(default_factory=dict)
    
    def add_appointment(self, appointment: Appointment):
        """Add appointment to context."""
        self.appointments.append(appointment)
        if self.appointment is None:
            self.appointment = appointment
    
    def get_appointment_by_email(self, email: str) -> Optional[Appointment]:
        """Get appointment by email."""
        for appt in self.appointments:
            if appt.email == email:
                return appt
        return None
    
    def set_data(self, key: str, value: Any):
        """Set arbitrary test data."""
        self.test_data[key] = value
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Get test data by key."""
        return self.test_data.get(key, default)
    
    def clear(self):
        """Clear all context data."""
        self.appointment = None
        self.appointments.clear()
        self.test_data.clear()
        self.bookslot_data.clear()
        self.patientintake_data.clear()
