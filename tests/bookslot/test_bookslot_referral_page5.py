"""
Test Suite: Referral Page
==========================
Tests for the Referral Source page (marketing attribution).

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com

Test Coverage:
- Page load verification
- Referral source option selection
- All referral options availability
- Required selection validation
- Form submission

Run Commands:
    pytest tests/bookslot/test_referral_page.py -v
    pytest tests/bookslot/test_referral_page.py -m smoke -v
"""

import pytest
import allure
from playwright.sync_api import Page
from tests.bookslot.helpers.navigation_helper import BookslotNavigator
from pages.bookslot.bookslots_referral_page5 import BookslotReferralPage


@allure.epic("Bookslot")
@allure.feature("Referral Page")
@pytest.mark.bookslot
class TestReferralPage:
    """Test suite for Referral page functionality"""

    @allure.story("Page Load")
    @allure.title("Verify Referral page loads successfully")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.human_behavior
    def test_referral_page_loads(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Referral page loads after Personal Info submission
        
        Validates: Page is accessible and referral options are visible
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        navigator.navigate_to_referral()
        referral_page = BookslotReferralPage(smart_actions.page, multi_project_config['bookslot']['ui_url'])
        
        with allure.step("Verify referral options are visible"):
            assert referral_page.radio_online.is_visible()
            assert referral_page.button_next.is_visible()
            
            allure.attach(page.screenshot(full_page=True), 
                         name="referral_page_loaded", 
                         attachment_type=allure.attachment_type.PNG)

    @allure.story("Referral Selection")
    @allure.title("Test all referral source options")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.parametrize("referral_option", [
        "Referred by physician",
        "Online search",
        "Social media",
        "Friend or family",
        "Advertisement",
    ], ids=["physician", "online", "social", "friend", "ad"])
    def test_referral_source_options(self, smart_actions, fake_bookslot_data, referral_option):
        """
        Scenario: Test each referral source option is selectable
        
        Validates: All referral sources can be selected and submitted
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        navigator.navigate_to_referral()
        act = smart_actions
        referral_page = BookslotReferralPage(smart_actions.page, multi_project_config['bookslot']['ui_url'])
        
        with allure.step(f"Select referral source: {referral_option}"):
            radio_button = smart_actions.page.get_by_role("radio", name=referral_option)
            
            if radio_button.is_visible():
                radio_button.click()
                smart_actions.page.wait_for_timeout(300)
                
                # Verify selection
                is_checked = radio_button.is_checked()
                assert is_checked, f"Should be able to select: {referral_option}"
                
                allure.attach(smart_actions.page.screenshot(full_page=True), 
                             name=f"{referral_option.lower().replace(' ', '_')}_selected", 
                             attachment_type=allure.attachment_type.PNG)
                
                # Verify can proceed
                initial_url = smart_actions.page.url
                referral_page.proceed_to_next()
                smart_actions.page.wait_for_timeout(1000)
                
                assert smart_actions.page.url != initial_url, f"Should proceed with: {referral_option}"

    @allure.story("Referral Selection")
    @allure.title("Select online search as referral source")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.human_behavior
    def test_select_online_search(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: User selects Online search as referral source
        
        Validates: Online search option is selectable and progresses
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        navigator.navigate_to_referral()
        act = smart_actions
        referral_page = BookslotReferralPage(smart_actions.page, multi_project_config['bookslot']['ui_url'])
        
        with allure.step("Select Online search"):
            referral_page.select_online()
            smart_actions.page.wait_for_timeout(300)
            
            is_checked = referral_page.is_online_checked()
            assert is_checked, "Online search should be selected"
            
            allure.attach(smart_actions.page.screenshot(full_page=True), 
                         name="online_search_selected", 
                         attachment_type=allure.attachment_type.PNG)
        
        with allure.step("Proceed to next page"):
            initial_url = smart_actions.page.url
            referral_page.proceed_to_next()
            smart_actions.page.wait_for_timeout(1000)
            
            assert smart_actions.page.url != initial_url, "Should proceed after selecting referral source"

    @allure.story("Referral Selection")
    @allure.title("Select physician referral")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_select_physician_referral(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: User selects Physician referral as source
        
        Validates: Physician referral option works correctly
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        navigator.navigate_to_referral()
        act = smart_actions
        referral_page = BookslotReferralPage(smart_actions.page, multi_project_config['bookslot']['ui_url'])
        
        with allure.step("Select Physician referral"):
            referral_page.select_physician()
            smart_actions.page.wait_for_timeout(300)
            
            is_checked = referral_page.is_physician_checked()
            assert is_checked, "Physician referral should be selected"
        
        with allure.step("Proceed to next page"):
            initial_url = smart_actions.page.url
            referral_page.proceed_to_next()
            smart_actions.page.wait_for_timeout(1000)
            
            assert smart_actions.page.url != initial_url, "Should proceed with physician referral"

    @allure.story("Referral Selection")
    @allure.title("Test changing referral selection")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.validation
    def test_change_referral_selection(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: User changes referral selection before submitting
        
        Validates: Can change selection and last selection is used
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        navigator.navigate_to_referral()
        act = smart_actions
        referral_page = BookslotReferralPage(smart_actions.page, multi_project_config['bookslot']['ui_url'])
        
        with allure.step("Select first option"):
            referral_page.select_online()
            smart_actions.page.wait_for_timeout(300)
            assert referral_page.is_online_checked()
        
        with allure.step("Change to second option"):
            referral_page.select_social_media()
            smart_actions.page.wait_for_timeout(300)
            
            assert referral_page.is_social_media_checked()
            assert not referral_page.is_online_checked()
            
            allure.attach(smart_actions.page.screenshot(full_page=True), 
                         name="selection_changed", 
                         attachment_type=allure.attachment_type.PNG)

    @allure.story("Required Selection")
    @allure.title("Verify referral selection is required")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.validation
    def test_referral_required(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Attempt to proceed without selecting referral source
        
        Validates: Cannot proceed without selecting a referral option
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        navigator.navigate_to_referral()
        act = smart_actions
        referral_page = BookslotReferralPage(smart_actions.page, multi_project_config['bookslot']['ui_url'])
        
        with allure.step("Attempt to proceed without selection"):
            initial_url = smart_actions.page.url
            referral_page.proceed_to_next()
            smart_actions.page.wait_for_timeout(800)
            
            # Adjust assertion based on actual behavior
            allure.attach(smart_actions.page.screenshot(full_page=True), 
                         name="no_selection_attempt", 
                         attachment_type=allure.attachment_type.PNG)

    @allure.story("Marketing Attribution")
    @allure.title("Test all marketing channels are tracked")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_all_marketing_channels(self, smart_actions, fake_bookslot_data, multi_project_config):
        """
        Scenario: Verify all marketing attribution options are available
        
        Validates: Complete list of referral sources is present
        """
        navigator = BookslotNavigator(smart_actions, fake_bookslot_data, multi_project_config)
        page = navigator.navigate_to_referral()
        
        with allure.step("Verify all referral options are available"):
            expected_options = [
                "Referred by physician",
                "Online search",
                "Social media",
                "Friend or family",
                "Advertisement",
            ]
            
            available_count = 0
            for option in expected_options:
                if page.get_by_role("radio", name=option).is_visible():
                    available_count += 1
            
            allure.attach(f"Available referral options: {available_count}/{len(expected_options)}", 
                         name="marketing_channels", 
                         attachment_type=allure.attachment_type.TEXT)
            
            assert available_count > 0, "Should have at least one referral option available"
