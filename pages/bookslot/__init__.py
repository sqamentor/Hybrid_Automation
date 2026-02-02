"""
BookSlot Page Objects Module
Provides page objects for the complete BookSlot appointment booking workflow

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

Project: BookSlot
Workflow: 6-step appointment booking process
"""

# Import all page objects
from .bookslots_basicinfo_page1 import BookslotBasicInfoPage
from .bookslot_eventtype_page2 import BookslotEventInfoPage
from .bookslot_scheduler_page3 import BookslotWebSchedulerPage
from .bookslots_personalInfo_page4 import BookslotPersonalInfoPage
from .bookslots_referral_page5 import BookslotReferralPage
from .bookslots_insurance_page6 import BookslotInsurancePage
from .bookslots_success_page7 import BookslotSuccessPage

# Export all page objects
__all__ = [
    'BookslotBasicInfoPage',
    'BookslotEventInfoPage',
    'BookslotWebSchedulerPage',
    'BookslotPersonalInfoPage',
    'BookslotReferralPage',
    'BookslotInsurancePage',
    'BookslotSuccessPage',
]

# Workflow order reference
WORKFLOW_STEPS = {
    1: 'BookslotBasicInfoPage',      # /basic-info - Patient registration
    2: 'BookslotEventInfoPage',      # /eventtype - Appointment type selection
    3: 'BookslotWebSchedulerPage',   # /scheduler - Date/time selection
    4: 'BookslotPersonalInfoPage',   # Demographics collection
    5: 'BookslotReferralPage',       # Referral source
    6: 'BookslotInsurancePage',      # Insurance information
    7: 'BookslotSuccessPage',        # /success - Confirmation
}

# Usage example in documentation
"""
Example Usage in Tests:

    from pages.bookslot import BookslotBasicInfoPage, BookslotEventInfoPage
    
    # In your test file (tests/bookslot/test_*.py):
    base_url = multi_project_config['bookslot']['ui_url']
    
    # Step 1: Basic Info
    basic_info = BookslotBasicInfoPage(page, base_url)
    basic_info.navigate()
    basic_info.fill_basic_info(first_name, last_name, email, phone, zip)
    basic_info.submit_for_otp()
    
    # Step 2: Event Selection
    event_page = BookslotEventInfoPage(page, base_url)
    event_page.navigate()
    event_page.select_new_patient_appointment()
    event_page.proceed_to_scheduler()
    
    # Continue with remaining steps...
"""

