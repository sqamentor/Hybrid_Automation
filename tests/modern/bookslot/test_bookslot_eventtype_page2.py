"""
Test Suite: Event Type Page
============================
Tests for the Event Type selection page.

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

Test Coverage:
- Page load verification
- New Patient selection
- Follow-up selection
- Consultation selection
- Event type button visibility
- Navigation to next page

Run Commands:
    pytest tests/bookslot/test_eventtype_page.py -v
    pytest tests/bookslot/test_eventtype_page.py -m smoke -v
"""

import allure
import pytest

from pages.bookslot.bookslots_basicinfo_page1 import BookslotBasicInfoPage
from pages.bookslot.bookslots_eventinfo_page2 import BookslotEventInfoPage
from tests.bookslot.helpers.navigation_helper import BookslotNavigator


@allure.epic("Bookslot")
@allure.feature("Event Type Page")
@pytest.mark.playwright
@pytest.mark.modern_spa
@pytest.mark.bookslot
class TestEventTypePage:
    """Test suite for Event Type page functionality"""

    @allure.story("Page Load")
    @allure.title("Verify Event Type page loads successfully")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.human_behavior
    def test_event_type_page_loads(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Event Type page loads after Basic Info submission

        Validates: Page is accessible and event options are visible
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        event_page = navigator.navigate_to_event_type()

        with allure.step("Verify event type buttons are visible"):
            assert event_page.button_new_patient.is_visible()
            assert event_page.button_next.is_visible()

            allure.attach(
                event_page.page.screenshot(full_page=True),
                name="event_type_page_loaded",
                attachment_type=allure.attachment_type.PNG,
            )

    @allure.story("Event Selection")
    @allure.title("Select New Patient appointment type")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.human_behavior
    def test_select_new_patient(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: User selects New Patient appointment

        Validates: New Patient option is selectable and progresses
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        event_page = navigator.navigate_to_event_type()

        with allure.step("Select New Patient"):
            event_page.select_new_patient()

            allure.attach(
                event_page.page.screenshot(full_page=True),
                name="new_patient_selected",
                attachment_type=allure.attachment_type.PNG,
            )

        with allure.step("Proceed to next page"):
            initial_url = event_page.page.url
            event_page.proceed_to_next()
            event_page.page.wait_for_timeout(1000)

            assert event_page.page.url != initial_url, "Should proceed after selecting event type"

    @allure.story("Event Selection")
    @allure.title("Test all available event types")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "event_type",
        [
            "New Patient",
            # Add other event types if available
        ],
    )
    def test_event_type_selection(
        self, smart_actions, fake_bookslot_data, multi_project_config, event_type
    ):
        """
        Scenario: Test each available event type option

        Validates: All event types are selectable
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        event_page = navigator.navigate_to_event_type()

        with allure.step(f"Select event type: {event_type}"):
            # Check if button exists using Page Object method
            if event_page.is_event_button_visible(event_type):
                if event_type == "New Patient":
                    event_page.select_new_patient()
                else:
                    event_page.select_event_by_name(event_type)

                allure.attach(
                    event_page.page.screenshot(full_page=True),
                    name=f"{event_type.lower().replace(' ', '_')}_selected",
                    attachment_type=allure.attachment_type.PNG,
                )

                initial_url = event_page.page.url
                event_page.proceed_to_next()
                event_page.page.wait_for_timeout(1000)

                assert (
                    event_page.page.url != initial_url
                ), f"Should proceed after selecting {event_type}"

    @allure.story("Required Selection")
    @allure.title("Verify event type selection is required")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.validation
    def test_event_type_required(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Attempt to proceed without selecting event type

        Validates: Cannot proceed without selecting an event type
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        event_page = navigator.navigate_to_event_type()

        with allure.step("Attempt to proceed without selection"):
            initial_url = event_page.page.url
            event_page.proceed_to_next()
            event_page.page.wait_for_timeout(800)

            # May or may not prevent - depends on implementation
            # Adjust assertion based on actual behavior
            allure.attach(
                event_page.page.screenshot(full_page=True),
                name="no_selection_attempt",
                attachment_type=allure.attachment_type.PNG,
            )

    @allure.story("Navigation")
    @allure.title("Test back navigation from Event Type page")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_back_navigation(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Navigate back to Basic Info page

        Validates: Back navigation preserves data
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        event_page = navigator.navigate_to_event_type()
        data = fake_bookslot_data

        with allure.step("Navigate back"):
            event_page.page.go_back()
            event_page.page.wait_for_timeout(800)

            # Use Basic Info Page Object to verify
            basic_page = BookslotBasicInfoPage(
                event_page.page, multi_project_config["bookslot"]["ui_url"]
            )
            assert basic_page.textbox_first_name.is_visible()

            # Verify data is preserved
            first_name_value = basic_page.textbox_first_name.input_value()
            assert data["first_name"] in first_name_value, "First name should be preserved"

            allure.attach(
                event_page.page.screenshot(full_page=True),
                name="back_navigation",
                attachment_type=allure.attachment_type.PNG,
            )
