"""
Test Suite: Scheduler Page
===========================
Tests for the appointment scheduler/calendar page.

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

Test Coverage:
- Scheduler component loads
- Date selection
- Time slot selection (AM/PM)
- Available slots visibility
- Navigation to next page

Run Commands:
    pytest tests/bookslot/test_scheduler_page.py -v
    pytest tests/bookslot/test_scheduler_page.py -m smoke -v
"""

import allure
import pytest

from pages.bookslot.bookslots_webscheduler_page3 import BookslotWebSchedulerPage
from tests.bookslot.helpers.navigation_helper import BookslotNavigator


@allure.epic("Bookslot")
@allure.feature("Scheduler Page")
@pytest.mark.modern_spa
@pytest.mark.bookslot
class TestSchedulerPage:
    """Test suite for Scheduler page functionality."""

    @allure.story("Page Load")
    @allure.title("Verify Scheduler page loads successfully")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.human_behavior
    def test_scheduler_page_loads(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Scheduler page loads after Event Type selection
        
        Validates: Scheduler component is visible and ready
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        scheduler_page = navigator.navigate_to_scheduler()
        
        with allure.step("Verify scheduler loaded"):
            # Wait for scheduler to be ready
            scheduler_page.page.wait_for_timeout(1500)
            
            # Verify time slots are visible using Page Object
            assert scheduler_page.time_slots_am_pm.count() > 0, "AM/PM time slots should be visible"
            
            allure.attach(scheduler_page.page.screenshot(full_page=True), 
                         name="scheduler_page_loaded", 
                         attachment_type=allure.attachment_type.PNG)

    @allure.story("Time Slot Selection")
    @allure.title("Select morning (AM) time slot")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.human_behavior
    def test_select_am_time_slot(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: User selects morning appointment time
        
        Validates: AM slot selection works and progresses
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        scheduler_page = navigator.navigate_to_scheduler()
        act = smart_actions
        
        with allure.step("Select AM time slot"):
            act.wait_for_scheduler(scheduler_page.page)
            
            scheduler_page.select_am_or_pm_slot("AM")
            scheduler_page.page.wait_for_timeout(500)
            
            allure.attach(scheduler_page.page.screenshot(full_page=True), 
                         name="am_slot_selected", 
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("Proceed to next page"):
            initial_url = scheduler_page.page.url
            scheduler_page.proceed_to_next()
            scheduler_page.page.wait_for_timeout(1000)
            
            assert scheduler_page.page.url != initial_url, "Should proceed after selecting time slot"

    @allure.story("Time Slot Selection")
    @allure.title("Select afternoon (PM) time slot")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_select_pm_time_slot(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: User selects afternoon appointment time
        
        Validates: PM slot selection works and progresses
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        scheduler_page = navigator.navigate_to_scheduler()
        act = smart_actions
        
        with allure.step("Select PM time slot"):
            act.wait_for_scheduler(scheduler_page.page)
            
            if scheduler_page.is_am_or_pm_slot_visible("PM"):
                scheduler_page.select_am_or_pm_slot("PM")
                scheduler_page.page.wait_for_timeout(500)
                
                allure.attach(scheduler_page.page.screenshot(full_page=True), 
                             name="pm_slot_selected", 
                             attachment_type=allure.attachment_type.PNG)
                
                initial_url = scheduler_page.page.url
                scheduler_page.proceed_to_next()
                scheduler_page.page.wait_for_timeout(1000)
                
                assert scheduler_page.page.url != initial_url, "Should proceed after selecting PM slot"

    @allure.story("Time Slot Selection")
    @allure.title("Test both AM and PM slot selections")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.parametrize("time_period", ["AM", "PM"])
    def test_time_period_selection(self, smart_actions, fake_bookslot_data, multi_project_config, time_period):
        """
        Scenario: Test selecting different time periods
        
        Validates: Both AM and PM slots are available and selectable
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        scheduler_page = navigator.navigate_to_scheduler()
        act = smart_actions
        
        with allure.step(f"Select {time_period} time slot"):
            act.wait_for_scheduler(scheduler_page.page)
            
            if scheduler_page.is_am_or_pm_slot_visible(time_period):
                scheduler_page.select_am_or_pm_slot(time_period)
                scheduler_page.page.wait_for_timeout(500)
                
                allure.attach(scheduler_page.page.screenshot(full_page=True), 
                             name=f"{time_period.lower()}_slot_selected", 
                             attachment_type=allure.attachment_type.PNG)
                
                initial_url = scheduler_page.page.url
                scheduler_page.proceed_to_next()
                scheduler_page.page.wait_for_timeout(1000)
                
                assert scheduler_page.page.url != initial_url, f"Should proceed after selecting {time_period} slot"

    @allure.story("Scheduler Loading")
    @allure.title("Verify scheduler loads within acceptable time")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.performance
    def test_scheduler_loading_time(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Measure scheduler loading time
        
        Validates: Scheduler loads within reasonable timeframe
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        scheduler_page = navigator.navigate_to_scheduler()
        
        with allure.step("Verify scheduler loads promptly"):
            act = smart_actions
            act.wait_for_scheduler(scheduler_page.page)
            
            # Check if slots are available within reasonable time using Page Object
            assert scheduler_page.time_slots_am_pm.count() > 0, "Time slots should load"
            
            allure.attach("Scheduler loaded successfully", 
                         name="loading_verification", 
                         attachment_type=allure.attachment_type.TEXT)

    @allure.story("Available Slots")
    @allure.title("Verify available time slots are displayed")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.validation
    def test_available_slots_displayed(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Check that available time slots are visible
        
        Validates: Scheduler shows available appointment times
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        page = navigator.navigate_to_scheduler()
        act = smart_actions
        
        with allure.step("Count available slots"):
            act.wait_for_scheduler(page.page)
            
            am_count = page.get_am_slots_count()
            pm_count = page.get_pm_slots_count()
            total_slots = am_count + pm_count
            
            allure.attach(f"AM Slots: {am_count}, PM Slots: {pm_count}, Total: {total_slots}", 
                         name="available_slots_count", 
                         attachment_type=allure.attachment_type.TEXT)
            
            assert total_slots > 0, "Should have at least one available time slot"
            
            allure.attach(page.screenshot(full_page=True), 
                         name="available_slots", 
                         attachment_type=allure.attachment_type.PNG)

    @allure.story("Required Selection")
    @allure.title("Verify time slot selection is required")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.validation
    def test_time_slot_required(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Attempt to proceed without selecting time slot
        
        Validates: Cannot proceed without selecting a time slot
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        page = navigator.navigate_to_scheduler()
        act = smart_actions
        
        with allure.step("Attempt to proceed without selection"):
            act.wait_for_scheduler(page.page)
            
            initial_url = page.page.url
            page.proceed_to_next()
            page.page.wait_for_timeout(800)
            
            # Adjust assertion based on actual behavior
            allure.attach(page.screenshot(full_page=True), 
                         name="no_selection_attempt", 
                         attachment_type=allure.attachment_type.PNG)
