"""BookSlot Human Behavior Integration Example Demonstrates realistic form filling with human-like
delays and interactions.

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

Purpose:
    Show how to use human behavior simulation in BookSlot automation
    to mimic natural user interactions during appointment booking

Usage:
    # Run with human behavior enabled
    pytest examples/bookslot_human_behavior_example.py --enable-human-behavior

    # Run with specific intensity
    pytest examples/bookslot_human_behavior_example.py --enable-human-behavior --human-behavior-intensity high

    # Run fast (no human behavior)
    pytest examples/bookslot_human_behavior_example.py

Features Demonstrated:
    ✓ Character-by-character typing (0.08-0.25s per character)
    ✓ Thinking pauses between actions (0.3-2.5s)
    ✓ Reading delays for content review (0.5-2.0s)
    ✓ Navigation waits (0.5-1.5s)
    ✓ Form field consideration time
    ✓ Realistic appointment booking flow
"""

import pytest
from playwright.sync_api import Page
from pages.bookslot.bookslots_basicinfo import BookslotBasicInfoPage
from pages.bookslot.bookslots_eventinfo import BookslotEventInfoPage
from pages.bookslot.bookslots_webscheduler import BookslotWebSchedulerPage
from pages.bookslot.bookslots_personalInfo import BookslotPersonalInfoPage
from pages.bookslot.bookslots_referral import BookslotReferralPage
from pages.bookslot.bookslots_insurance import BookslotInsurancePage
from pages.bookslot.bookslots_success import BookslotSuccessPage


@pytest.mark.bookslot
@pytest.mark.human_like
@pytest.mark.example
def test_bookslot_with_human_behavior(page: Page, multi_project_config, human_behavior):
    """Complete BookSlot workflow with human behavior simulation.

    This example demonstrates:
    - Natural typing speed (realistic character-by-character input)
    - Thinking pauses before actions
    - Reading delays for content review
    - Realistic navigation timing
    - Human-like form filling patterns

    Run Options:
        Fast Mode (CI/CD):
            pytest examples/bookslot_human_behavior_example.py
            (Completes in ~10 seconds)

        Human Mode (Demo/Visual Proof):
            pytest examples/bookslot_human_behavior_example.py --enable-human-behavior
            (Completes in ~45-60 seconds with realistic delays)

        High Intensity (Maximum Realism):
            pytest examples/bookslot_human_behavior_example.py --enable-human-behavior --human-behavior-intensity high
            (Completes in ~90-120 seconds with extended delays)
    """
    
    # Get configuration
    base_url = multi_project_config['bookslot']['ui_url']
    enable_human = human_behavior is not None
    
    print(f"\n{'='*70}")
    print(f"🎭 BookSlot Human Behavior Example")
    print(f"{'='*70}")
    print(f"Base URL: {base_url}")
    print(f"Human Behavior: {'✓ ENABLED' if enable_human else '✗ DISABLED (Fast Mode)'}")
    print(f"{'='*70}\n")
    
    # ========================================================================
    # STEP 1: Basic Information (Patient Registration)
    # ========================================================================
    print("📝 Step 1: Filling Basic Information...")
    basic_info = BookslotBasicInfoPage(page, base_url, enable_human_behavior=enable_human)
    basic_info.navigate()
    
    # Fill patient details with human-like typing
    basic_info.fill_field("First Name *", "John")
    basic_info.fill_field("Last Name *", "Doe")
    basic_info.fill_field("Email *", "john.doe@example.com")
    basic_info.fill_field("Confirm Email *", "john.doe@example.com")
    basic_info.fill_field("Phone *", "1234567890")
    basic_info.fill_field("Zip Code *", "20678")
    
    # Select location with human-like pause
    basic_info.click_element('button[name="location-select"]')
    
    print("   ✓ Basic information completed\n")
    
    # ========================================================================
    # STEP 2: Event Type Selection (Appointment Type)
    # ========================================================================
    print("📅 Step 2: Selecting Appointment Type...")
    event_info = BookslotEventInfoPage(page, base_url, enable_human_behavior=enable_human)
    
    # Review options and select with realistic timing
    event_info.select_new_patient_appointment()
    
    print("   ✓ Appointment type selected\n")
    
    # ========================================================================
    # STEP 3: Web Scheduler (Date and Time Selection)
    # ========================================================================
    print("🕐 Step 3: Selecting Date and Time...")
    scheduler = BookslotWebSchedulerPage(page, base_url, enable_human_behavior=enable_human)
    
    # Browse calendar and select time slot with human-like delays
    scheduler.select_time_slot("06:00 AM")
    scheduler.proceed_to_next()
    
    print("   ✓ Time slot selected\n")
    
    # ========================================================================
    # STEP 4: Personal Information (Demographics)
    # ========================================================================
    print("👤 Step 4: Filling Personal Information...")
    personal_info = BookslotPersonalInfoPage(page, base_url, enable_human_behavior=enable_human)
    
    # Fill demographics with thinking pauses
    personal_info.select_gender("MALE")
    personal_info.fill_date_of_birth("01/01/2000")
    personal_info.fill_address("20678")  # Will show suggestions
    personal_info.proceed_to_next()
    
    print("   ✓ Personal information completed\n")
    
    # ========================================================================
    # STEP 5: Referral Source (Marketing Attribution)
    # ========================================================================
    print("🔍 Step 5: Selecting Referral Source...")
    referral = BookslotReferralPage(page, base_url, enable_human_behavior=enable_human)
    
    # Consider and select referral source
    referral.select_referral_source("Referred by physician")
    referral.proceed_to_next()
    
    print("   ✓ Referral source selected\n")
    
    # ========================================================================
    # STEP 6: Insurance Information (Coverage Details)
    # ========================================================================
    print("💳 Step 6: Filling Insurance Information...")
    insurance = BookslotInsurancePage(page, base_url, enable_human_behavior=enable_human)
    
    # Fill insurance details with realistic typing
    insurance.fill_insurance_info(
        member_name="John Doe",
        id_number="123456",
        group_number="123456",
        company_name="Aetna"
    )
    insurance.submit_to_clinic()
    
    print("   ✓ Insurance information submitted\n")
    
    # ========================================================================
    # FINAL: Success Page (Confirmation)
    # ========================================================================
    print("✅ Step 7: Verifying Success...")
    success = BookslotSuccessPage(page, base_url, enable_human_behavior=enable_human)
    
    # Verify confirmation with human-like observation time
    success.verify_redirect_message()
    success.verify_confirmation_displayed()
    
    print("   ✓ Booking confirmed!\n")
    
    print(f"{'='*70}")
    print(f"🎉 Complete! Appointment booked successfully")
    if enable_human:
        print(f"⏱️  Execution included realistic human-like delays")
    else:
        print(f"⚡ Execution completed in fast mode")
    print(f"{'='*70}\n")


@pytest.mark.bookslot
@pytest.mark.human_like
@pytest.mark.example
@pytest.mark.smoke
def test_bookslot_partial_workflow_with_human_behavior(page: Page, multi_project_config, human_behavior):
    """Partial BookSlot workflow demonstrating human behavior in specific sections.

    This example shows:
    - How to enable human behavior for specific pages only
    - Mixed mode (some pages fast, some pages human-like)
    - Selective human behavior usage
    """
    
    base_url = multi_project_config['bookslot']['ui_url']
    
    print(f"\n{'='*70}")
    print(f"🎭 Partial Workflow with Selective Human Behavior")
    print(f"{'='*70}\n")
    
    # Fast mode for basic info (no human behavior)
    print("⚡ Step 1: Basic Info (Fast Mode)...")
    basic_info = BookslotBasicInfoPage(page, base_url, enable_human_behavior=False)
    basic_info.navigate()
    basic_info.fill_field("First Name *", "Jane")
    basic_info.fill_field("Last Name *", "Smith")
    basic_info.fill_field("Email *", "jane.smith@example.com")
    print("   ✓ Completed (fast)\n")
    
    # Human mode for personal info (with human behavior)
    print("🎭 Step 2: Personal Info (Human Mode)...")
    personal_info = BookslotPersonalInfoPage(page, base_url, enable_human_behavior=True)
    personal_info.select_gender("FEMALE")
    personal_info.fill_date_of_birth("05/15/1990")
    print("   ✓ Completed (with realistic delays)\n")
    
    # Fast mode for insurance (no human behavior)
    print("⚡ Step 3: Insurance (Fast Mode)...")
    insurance = BookslotInsurancePage(page, base_url, enable_human_behavior=False)
    insurance.fill_insurance_info()
    print("   ✓ Completed (fast)\n")
    
    print(f"{'='*70}")
    print(f"✅ Mixed mode execution completed")
    print(f"{'='*70}\n")


@pytest.mark.bookslot
@pytest.mark.human_like
@pytest.mark.example
@pytest.mark.performance
def test_bookslot_performance_comparison(page: Page, multi_project_config, benchmark):
    """
    Compare execution time: Fast mode vs Human behavior mode
    
    This test demonstrates the performance difference between:
    - Fast automation (no delays)
    - Human-like automation (realistic delays)
    """
    
    base_url = multi_project_config['bookslot']['ui_url']
    
    print(f"\n{'='*70}")
    print(f"⏱️  Performance Comparison")
    print(f"{'='*70}\n")
    
    # Measure fast mode
    import time
    
    print("⚡ Testing Fast Mode...")
    start_fast = time.time()
    basic_fast = BookslotBasicInfoPage(page, base_url, enable_human_behavior=False)
    basic_fast.navigate()
    basic_fast.fill_field("First Name *", "Speed")
    basic_fast.fill_field("Last Name *", "Test")
    end_fast = time.time()
    fast_duration = end_fast - start_fast
    
    print(f"   Fast Mode Duration: {fast_duration:.2f} seconds\n")
    
    # Refresh page for clean state
    page.reload()
    
    print("🎭 Testing Human Behavior Mode...")
    start_human = time.time()
    basic_human = BookslotBasicInfoPage(page, base_url, enable_human_behavior=True)
    basic_human.navigate()
    basic_human.fill_field("First Name *", "Human")
    basic_human.fill_field("Last Name *", "Test")
    end_human = time.time()
    human_duration = end_human - start_human
    
    print(f"   Human Mode Duration: {human_duration:.2f} seconds\n")
    
    # Calculate difference
    time_difference = human_duration - fast_duration
    percentage_slower = ((human_duration / fast_duration) - 1) * 100
    
    print(f"{'='*70}")
    print(f"📊 Results:")
    print(f"   Fast Mode:    {fast_duration:.2f}s")
    print(f"   Human Mode:   {human_duration:.2f}s")
    print(f"   Difference:   +{time_difference:.2f}s ({percentage_slower:.1f}% slower)")
    print(f"   Trade-off:    More realistic behavior for {percentage_slower:.1f}% time increase")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    """
    Run examples directly:
    
    python examples/bookslot_human_behavior_example.py
    
    Or use pytest:
    
    # Full human behavior
    pytest examples/bookslot_human_behavior_example.py --enable-human-behavior -v
    
    # Fast mode
    pytest examples/bookslot_human_behavior_example.py -v
    
    # Specific test
    pytest examples/bookslot_human_behavior_example.py::test_bookslot_with_human_behavior --enable-human-behavior
    """
    pytest.main([__file__, "-v", "--enable-human-behavior"])
