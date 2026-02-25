"""
P3: Scheduler Page Tests (Layer A - Page-Level)

Tests for Scheduler/Time Slot Selection page (requires P1→P2 completed).

Test Coverage:
- Smoke: Page loads, calendar visible, slots visible
- Validation: Slot selection, disabled slots, required validation
- Regression: AM/PM filtering, date navigation, slot availability

Markers:
- @pytest.mark.p3_scheduler
- @pytest.mark.smoke, validation, regression
"""

import pytest
import allure
from typing import Dict, Any
from playwright.sync_api import Page, expect
from datetime import datetime, timedelta

from framework.testing.url_builder import URLBuilder
from framework.testing.url_validator import URLValidator


@pytest.mark.bookslot
@pytest.mark.p3_scheduler
@pytest.mark.smoke
@pytest.mark.critical
class TestSchedulerSmoke:
    """Smoke tests for Scheduler page (P3)"""
    
    def test_scheduler_page_loads(self, at_scheduler, validation_helper):
        """SMOKE: Scheduler page loads successfully"""
        validation_helper.validate_element_visible("[data-testid='scheduler']", "Scheduler component")
        validation_helper.validate_element_visible("button:has-text('Next')", "Next button")
    
    def test_time_slots_visible(self, at_scheduler, validation_helper):
        """SMOKE: Time slots are displayed"""
        validation_helper.validate_minimum_element_count(
            "[data-testid='time-slot']",
            minimum_count=1,
            description="Time slots"
        )
    
    def test_calendar_visible(self, at_scheduler, validation_helper):
        """SMOKE: Calendar/date selector is visible"""
        validation_helper.validate_element_visible("[data-testid='date-selector']", "Date selector")


@pytest.mark.bookslot
@pytest.mark.p3_scheduler
@pytest.mark.validation
@pytest.mark.high
class TestSchedulerValidation:
    """Validation tests for Scheduler page"""
    
    def test_available_slots_clickable(self, at_scheduler, page: Page, validation_helper):
        """VALIDATION: Available time slots are clickable"""
        # Wait for slots to load
        page.wait_for_selector("[data-testid='time-slot']:not([disabled])", timeout=10000)
        
        # Verify at least one available slot
        available_slots = page.locator("[data-testid='time-slot']:not([disabled])")
        assert available_slots.count() > 0, "No available time slots found"
        
        # Verify first available slot is clickable
        validation_helper.validate_element_enabled(
            "[data-testid='time-slot']:not([disabled]):first-child",
            "First available time slot"
        )
    
    def test_disabled_slots_not_clickable(self, at_scheduler, page: Page):
        """VALIDATION: Disabled time slots cannot be selected"""
        disabled_slots = page.locator("[data-testid='time-slot'][disabled]")
        
        if disabled_slots.count() > 0:
            # Try to click disabled slot
            disabled_slots.first.click(force=True)
            
            # Verify it's still not selected
            expect(disabled_slots.first).not_to_have_attribute("data-selected", "true")
    
    def test_time_slot_selection_required(self, at_scheduler, page: Page, validation_helper):
        """VALIDATION: Time slot selection is required"""
        # Try to proceed without selecting slot
        page.click("button:has-text('Next')")
        validation_helper.validate_error_message_shown("required")
    
    def test_single_slot_selection(self, at_scheduler, page: Page):
        """VALIDATION: Only one time slot can be selected"""
        # Wait for available slots
        page.wait_for_selector("[data-testid='time-slot']:not([disabled])", timeout=10000)
        
        # Select first slot
        page.locator("[data-testid='time-slot']:not([disabled])").nth(0).click()
        
        # Select second slot
        page.locator("[data-testid='time-slot']:not([disabled])").nth(1).click()
        
        # Verify only one selected
        selected = page.locator("[data-testid='time-slot'][data-selected='true']")
        assert selected.count() == 1, f"Expected 1 selected slot, found {selected.count()}"
    
    def test_slot_selection_navigation_to_personal_info(self, at_scheduler, page: Page, validation_helper):
        """VALIDATION: Selecting slot and clicking Next navigates to Personal Info"""
        # Wait and select slot
        page.wait_for_selector("[data-testid='time-slot']:not([disabled])", timeout=10000)
        page.locator("[data-testid='time-slot']:not([disabled])").first.click()
        
        # Click Next
        page.click("button:has-text('Next')")
        page.wait_for_load_state("networkidle")
        
        # Verify navigation to P4
        validation_helper.validate_navigation_to("Personal Info")
    
    def test_slot_selection_shows_selected_state(self, at_scheduler, page: Page):
        """VALIDATION: Selected slot shows visual selected state"""
        page.wait_for_selector("[data-testid='time-slot']:not([disabled])", timeout=10000)
        slot = page.locator("[data-testid='time-slot']:not([disabled])").first
        
        # Click slot
        slot.click()
        
        # Verify selected attribute
        expect(slot).to_have_attribute("data-selected", "true")


@pytest.mark.bookslot
@pytest.mark.p3_scheduler
@pytest.mark.regression
@pytest.mark.medium
class TestSchedulerRegression:
    """Regression tests for Scheduler page"""
    
    @pytest.mark.parametrize("time_filter", ["AM", "PM"])
    def test_time_filter_functionality(self, at_scheduler, page: Page, time_filter):
        """REGRESSION: AM/PM filters work correctly"""
        page.wait_for_selector("[data-testid='time-slot']", timeout=10000)
        
        # Click time filter
        page.click(f"[data-testid='filter-{time_filter.lower()}']")
        
        # Verify slots are filtered
        visible_slots = page.locator("[data-testid='time-slot']:visible")
        
        for i in range(visible_slots.count()):
            slot_text = visible_slots.nth(i).inner_text()
            
            if time_filter == "AM":
                assert "AM" in slot_text, f"Expected AM slot, got: {slot_text}"
            else:
                assert "PM" in slot_text, f"Expected PM slot, got: {slot_text}"
    
    def test_date_navigation_forward(self, at_scheduler, page: Page):
        """REGRESSION: Can navigate to future dates"""
        # Click next date button
        page.click("[data-testid='date-next']")
        page.wait_for_timeout(1000)  # Wait for slots to refresh
        
        # Verify new slots loaded
        page.wait_for_selector("[data-testid='time-slot']", timeout=10000)
        assert page.locator("[data-testid='time-slot']").count() > 0
    
    def test_date_navigation_backward(self, at_scheduler, page: Page):
        """REGRESSION: Can navigate to previous dates (if allowed)"""
        # Click previous date button
        prev_button = page.locator("[data-testid='date-prev']")
        
        if not prev_button.is_disabled():
            prev_button.click()
            page.wait_for_timeout(1000)
            
            # Verify slots updated
            page.wait_for_selector("[data-testid='time-slot']", timeout=10000)
    
    def test_selected_slot_persists_on_back_navigation(self, at_scheduler, page: Page):
        """REGRESSION: Selected slot is remembered when navigating back"""
        # Select slot
        page.wait_for_selector("[data-testid='time-slot']:not([disabled])", timeout=10000)
        slot = page.locator("[data-testid='time-slot']:not([disabled])").first
        slot_text = slot.inner_text()
        slot.click()
        
        # Go forward
        page.click("button:has-text('Next')")
        page.wait_for_load_state("networkidle")
        
        # Go back
        page.click("button:has-text('Back')")
        page.wait_for_load_state("networkidle")
        
        # Verify slot still selected
        selected_slot = page.locator("[data-testid='time-slot'][data-selected='true']")
        assert selected_slot.inner_text() == slot_text
    
    def test_back_button_returns_to_event_type(self, at_scheduler, page: Page, validation_helper):
        """REGRESSION: Back button returns to Event Type page"""
        page.click("button:has-text('Back')")
        page.wait_for_load_state("networkidle")
        
        # Verify at P2
        validation_helper.validate_navigation_to("Event Type")


# ============================================================================
# URL WORKFLOW TESTS (Merged from url_testing/test_workflow_urls_p3.py)
# ============================================================================

@allure.epic("Bookslot")
@allure.feature("URL Testing")
@allure.story("Scheduler Page (P3)")
@pytest.mark.bookslot
@pytest.mark.p3_scheduler
@pytest.mark.url_workflow
class TestSchedulerURLWorkflow:
    """URL workflow tests for Scheduler page - date/time params, preferences, persistence"""

    @allure.title("Verify P3 loads with date and time parameters")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_p3_date_time_params(
        self,
        page: Page,
        url_builder: URLBuilder,
        url_validator: URLValidator
    ):
        """Test: Scheduler page loads with date/time preselected from URL"""
        url = url_builder.build(
            workflow_id="WF-P3-001-DATETIME",
            page_path="/schedule",
            query_params={
                "preferred_date": "2026-03-15",
                "preferred_time": "morning"
            }
        )

        allure.attach(url, "Generated URL", allure.attachment_type.TEXT)

        result = url_validator.validate(
            url=url,
            expected_elements=[
                "[data-testid='date-selector']",
                "[data-testid='time-slot']"
            ]
        )

        assert result.is_valid, f"URL validation failed: {result.errors}"
        assert result.status_code == 200

    @allure.title("Verify P3 with time preference parameters")
    @pytest.mark.parametrize(
        "time_pref",
        ["morning", "afternoon", "evening"],
        ids=["morning", "afternoon", "evening"]
    )
    def test_p3_time_preferences(
        self,
        page: Page,
        url_builder: URLBuilder,
        url_validator: URLValidator,
        time_pref: str
    ):
        """Test: Time preference parameters filter available slots"""
        url = url_builder.build(
            workflow_id=f"WF-P3-{time_pref.upper()}",
            page_path="/schedule",
            query_params={"preferred_time": time_pref}
        )

        result = url_validator.validate(
            url=url,
            expected_elements=["[data-testid='time-slot']"]
        )

        assert result.is_valid, f"Time pref {time_pref} failed: {result.errors}"
        assert result.status_code == 200

    @allure.title("Verify P3 handles invalid date format")
    @pytest.mark.negative
    def test_p3_invalid_date_format(
        self,
        page: Page,
        url_builder: URLBuilder,
        url_validator: URLValidator
    ):
        """Test: Invalid date formats handled gracefully"""
        url = url_builder.build(
            workflow_id="WF-P3-INVALID-DATE",
            page_path="/schedule",
            query_params={"preferred_date": "invalid-date"}
        )

        result = url_validator.validate(
            url=url,
            expected_elements=["[data-testid='date-selector']"]
        )

        assert result.status_code == 200

    @allure.title("Verify P3 schedule persistence after refresh")
    def test_p3_schedule_persistence_after_refresh(
        self,
        page: Page,
        url_builder: URLBuilder
    ):
        """Test: Schedule parameters persist after page refresh"""
        url = url_builder.build(
            workflow_id="WF-P3-PERSIST",
            page_path="/schedule",
            query_params={"preferred_date": "2026-03-15", "preferred_time": "morning"}
        )

        page.goto(url)
        original_url = page.url

        page.reload()
        refreshed_url = page.url

        assert original_url == refreshed_url
        assert "preferred_date" in refreshed_url

    @allure.title("Verify P3 performance within threshold")
    @pytest.mark.performance
    def test_p3_load_performance(
        self,
        page: Page,
        url_builder: URLBuilder,
        url_validator: URLValidator
    ):
        """Test: Page loads within performance threshold"""
        url = url_builder.build(
            workflow_id="WF-P3-PERF",
            page_path="/schedule",
            query_params={"preferred_date": "2026-03-15"}
        )

        result = url_validator.validate(url=url)
        assert result.validation_time_ms < 5000, f"Page load too slow: {result.validation_time_ms}ms"

    @allure.title("Verify P3 URL parsing for schedule parameters")
    def test_p3_url_parsing(self, url_builder: URLBuilder):
        """Test: Schedule parameters parsed correctly from URL"""
        url = url_builder.build(
            workflow_id="WF-P3-PARSE",
            page_path="/schedule",
            query_params={"preferred_date": "2026-03-15", "preferred_time": "afternoon"}
        )

        components = url_builder.parse_url(url)

        assert components["query_params"]["preferred_date"] == "2026-03-15"
        assert components["query_params"]["preferred_time"] == "afternoon"
        assert components["path"] == "/schedule"
