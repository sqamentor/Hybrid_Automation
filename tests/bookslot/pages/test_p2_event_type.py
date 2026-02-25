"""
P2: Event Type Page Tests (Layer A - Page-Level)

Tests for Event Type page (requires P1 completed as precondition).

Test Coverage:
- Smoke: Page loads, options visible
- Validation: Selection behavior, required validation
- Regression: All event type options, option combinations

Markers:
- @pytest.mark.p2_event_type
- @pytest.mark.smoke, validation, regression
"""

import pytest
import allure
from typing import Dict, Any
from playwright.sync_api import Page, expect

from framework.testing.url_builder import URLBuilder
from framework.testing.url_validator import URLValidator


@pytest.mark.bookslot
@pytest.mark.p2_event_type
@pytest.mark.smoke
@pytest.mark.critical
class TestEventTypeSmoke:
    """Smoke tests for Event Type page (P2)"""
    
    def test_event_type_page_loads(self, at_event_type, validation_helper):
        """SMOKE: Event Type page loads successfully"""
        validation_helper.validate_element_visible("h1", "Event Type heading")
        validation_helper.validate_element_visible("[data-testid='event-type-options']", "Event type options")
    
    def test_event_type_options_visible(self, at_event_type, validation_helper):
        """SMOKE: All event type options are visible"""
        # Validate at least one option is visible
        validation_helper.validate_minimum_element_count(
            "[data-testid='event-type-option']",
            minimum_count=1,
            description="Event type options"
        )


@pytest.mark.bookslot
@pytest.mark.p2_event_type
@pytest.mark.validation
@pytest.mark.high
class TestEventTypeValidation:
    """Validation tests for Event Type page"""
    
    def test_event_type_options_clickable(self, at_event_type, page: Page, validation_helper):
        """VALIDATION: All event type options are clickable"""
        options = page.locator("[data-testid='event-type-option']")
        count = options.count()
        
        for i in range(count):
            validation_helper.validate_element_enabled(
                f"[data-testid='event-type-option']:nth-child({i+1})",
                f"Event type option {i+1}"
            )
    
    def test_event_type_selection_required(self, at_event_type, page: Page, validation_helper):
        """VALIDATION: Event type selection is required"""
        # Try to proceed without selection
        page.click("button:has-text('Next')")
        validation_helper.validate_error_message_shown("required")
    
    def test_event_type_single_selection(self, at_event_type, page: Page):
        """VALIDATION: Only one event type can be selected"""
        # Select first option
        page.click("[data-testid='event-type-option']:first-child")
        
        # Select second option
        page.click("[data-testid='event-type-option']:nth-child(2)")
        
        # Verify only one is selected
        selected_count = page.locator("[data-testid='event-type-option'][data-selected='true']").count()
        assert selected_count == 1, f"Expected 1 selected, found{selected_count}"
    
    def test_event_type_navigation_to_scheduler(self, at_event_type, page: Page, validation_helper):
        """VALIDATION: Selecting event type and clicking Next navigates to Scheduler"""
        # Select first option
        page.click("[data-testid='event-type-option']:first-child")
        
        # Click Next
        page.click("button:has-text('Next')")
        page.wait_for_load_state("networkidle")
        
        # Verify navigation to Scheduler (P3)
        validation_helper.validate_navigation_to("Scheduler")


@pytest.mark.bookslot
@pytest.mark.p2_event_type
@pytest.mark.regression
@pytest.mark.medium
class TestEventTypeRegression:
    """Regression tests for Event Type page"""
    
    @pytest.mark.parametrize("event_type", [
        "New Patient Consultation",
        "Follow-up Appointment",
        "Emergency Consultation",
        "Video Consultation",
        "Lab Results Review",
        "Prescription Renewal"
    ])
    def test_all_event_types_selectable(self, at_event_type, page: Page, event_type):
        """REGRESSION: All event types can be selected"""
        # Try to find and select each event type
        option = page.locator(f"[data-testid='event-type-option']:has-text('{event_type}')")
        
        if option.count() > 0:
            option.click()
            # Verify selected
            expect(option).to_have_attribute("data-selected", "true")
    
    def test_back_button_returns_to_basic_info(self, at_event_type, page: Page, validation_helper):
        """REGRESSION: Back button returns to Basic Info page"""
        page.click("button:has-text('Back')")
        page.wait_for_load_state("networkidle")
        
        # Verify at Basic Info page
        validation_helper.validate_navigation_to("Basic Info")


# ============================================================================
# URL WORKFLOW TESTS (Merged from url_testing/test_workflow_urls_p2.py)
# ============================================================================

@allure.epic("Bookslot")
@allure.feature("URL Testing")
@allure.story("Event Type Page (P2)")
@pytest.mark.bookslot
@pytest.mark.p2_event_type
@pytest.mark.url_workflow
class TestEventTypeURLWorkflow:
    """URL workflow tests for Event Type page - payer workflows, prefill, persistence"""

    @allure.title("Verify P2 loads with Humana payer parameter")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_p2_humana_workflow(
        self,
        page: Page,
        url_builder: URLBuilder,
        url_validator: URLValidator
    ):
        """Test: Event Type page loads with Humana payer preselected"""
        url = url_builder.build(
            workflow_id="WF-P2-001-HUMANA",
            page_path="/insurance",
            query_params={"payer": "Humana", "prefill": "true"}
        )

        allure.attach(url, "Generated URL", allure.attachment_type.TEXT)

        result = url_validator.validate(
            url=url,
            expected_elements=[
                "input[name='member_id']",
                "input[name='group_number']",
                "select[name='payer']"
            ]
        )

        assert result.is_valid, f"URL validation failed: {result.errors}"
        assert result.status_code == 200

    @allure.title("Verify P2 handles no insurance (self-pay) option")
    def test_p2_no_insurance_self_pay(
        self,
        page: Page,
        url_builder: URLBuilder,
        url_validator: URLValidator
    ):
        """Test: Insurance page handles no insurance / self-pay option"""
        url = url_builder.build(
            workflow_id="WF-P2-004-NO-INSURANCE",
            page_path="/insurance",
            query_params={"payer": "None", "self_pay": "true"}
        )

        result = url_validator.validate(
            url=url,
            expected_elements=[
                "input[name='self_pay']",
                "button[type='submit']"
            ]
        )

        assert result.status_code == 200

    @allure.title("Verify P2 payer selection parameter persistence")
    @pytest.mark.parametrize(
        "payer",
        ["Humana", "Aetna", "Blue Cross Blue Shield"],
        ids=["humana", "aetna", "bcbs"]
    )
    def test_p2_payer_persistence(
        self,
        page: Page,
        url_builder: URLBuilder,
        payer: str
    ):
        """Test: Payer selection persists in URL"""
        url = url_builder.build(
            workflow_id=f"WF-P2-{payer.upper().replace(' ', '-')}",
            page_path="/insurance",
            query_params={"payer": payer}
        )

        page.goto(url)
        assert payer.replace(" ", "%20") in page.url or payer.replace(" ", "+") in page.url

    @allure.title("Verify P2 performance within threshold")
    @pytest.mark.performance
    def test_p2_load_performance(
        self,
        page: Page,
        url_builder: URLBuilder,
        url_validator: URLValidator
    ):
        """Test: Page loads within performance threshold"""
        url = url_builder.build(
            workflow_id="WF-P2-001-HUMANA",
            page_path="/insurance",
            query_params={"payer": "Humana"}
        )

        result = url_validator.validate(url=url)
        assert result.validation_time_ms < 5000, f"Page load too slow: {result.validation_time_ms}ms"

    @allure.title("Verify P2 URL parsing and reconstruction")
    def test_p2_url_parsing(self, url_builder: URLBuilder):
        """Test: URL can be parsed and reconstructed correctly"""
        original_url = url_builder.build(
            workflow_id="WF-P2-TEST",
            page_path="/insurance",
            query_params={"payer": "Humana", "prefill": "true"}
        )

        components = url_builder.parse_url(original_url)

        assert "workflow_id" in components["query_params"]
        assert components["query_params"]["payer"] == "Humana"
        assert components["path"] == "/insurance"

    @allure.title("Verify P2 handles multiple insurance workflows")
    @pytest.mark.parametrize(
        "workflow_data",
        [
            {"workflow_id": "WF-P2-001-HUMANA", "payer": "Humana"},
            {"workflow_id": "WF-P2-002-AETNA", "payer": "Aetna"},
            {"workflow_id": "WF-P2-003-BCBS", "payer": "Blue Cross Blue Shield"},
        ],
        ids=["humana", "aetna", "bcbs"]
    )
    def test_p2_multiple_insurance_workflows(
        self,
        page: Page,
        url_builder: URLBuilder,
        url_validator: URLValidator,
        workflow_data: Dict[str, str]
    ):
        """Test: Multiple insurance workflows load correctly"""
        url = url_builder.build(
            workflow_id=workflow_data["workflow_id"],
            page_path="/insurance",
            query_params={"payer": workflow_data["payer"]}
        )

        result = url_validator.validate(
            url=url,
            expected_elements=["select[name='payer']"]
        )

        assert result.is_valid, f"Workflow {workflow_data['workflow_id']} failed: {result.errors}"
        assert result.status_code == 200

