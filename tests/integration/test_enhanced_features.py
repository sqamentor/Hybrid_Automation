"""
Enhanced Integration Example
Demonstrates using all new framework capabilities in a single test

This example shows:
1. Selenium Grid support for remote execution
2. API Interceptor with WebSocket and request/response modification
3. AI Validation Suggester with caching and confidence scoring
4. Playwright context pooling and error handling
"""

import pytest
from models.appointment import Appointment
from datetime import datetime, timedelta


@pytest.mark.integration
@pytest.mark.enhanced_features
class TestEnhancedIntegration:
    """Integration tests using all enhanced framework features"""
    
    def test_complete_flow_with_all_enhancements(
        self, 
        ui_engine, 
        api_interceptor, 
        ai_validator, 
        db_client, 
        test_context
    ):
        """
        Complete workflow demonstrating all enhancements:
        - UI automation with enhanced error handling
        - API interception with modification
        - WebSocket message capture
        - AI-driven validation with caching
        - Database verification with confidence scoring
        """
        
        # ===================================================================
        # STEP 1: UI Automation with Enhanced Error Handling
        # ===================================================================
        # Engine automatically selected (Playwright or Selenium with Grid)
        # Includes retry logic, context pooling, and automatic driver management
        
        ui_engine.navigate("https://example.com/appointments/new")
        
        # Create appointment data
        appointment = Appointment(
            patient_name="John Doe",
            appointment_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            appointment_time="10:00 AM",
            appointment_type="Consultation"
        )
        
        # Fill form
        ui_engine.fill_text("input[name='patientName']", appointment.patient_name)
        ui_engine.fill_text("input[name='appointmentDate']", appointment.appointment_date)
        ui_engine.fill_text("input[name='appointmentTime']", appointment.appointment_time)
        ui_engine.select_dropdown("select[name='appointmentType']", appointment.appointment_type)
        
        # Submit form
        ui_engine.click("button[type='submit']")
        ui_engine.wait_for_selector(".success-message")
        
        # ===================================================================
        # STEP 2: API Interception with Request Modification
        # ===================================================================
        # Interceptor automatically captures HTTP and WebSocket traffic
        
        # Get captured API calls
        api_calls = api_interceptor.get_captured_requests()
        
        # Find the appointment creation request
        create_request = None
        for call in api_calls:
            if call['url'].endswith('/api/appointments') and call['method'] == 'POST':
                create_request = call
                break
        
        assert create_request is not None, "Appointment creation API call not found"
        
        # Extract appointment ID from response
        appointment_id = create_request['response']['body'].get('appointmentId')
        test_context.appointment_id = appointment_id
        
        # Verify request payload
        assert create_request['request']['body']['patientName'] == appointment.patient_name
        
        # ===================================================================
        # STEP 3: WebSocket Message Capture (if applicable)
        # ===================================================================
        # Capture real-time notifications
        
        ws_messages = api_interceptor.get_websocket_messages()
        
        # Check for appointment confirmation notification
        confirmation_message = None
        for msg in ws_messages:
            if msg.type == 'text' and 'appointmentCreated' in msg.data:
                confirmation_message = msg
                break
        
        if confirmation_message:
            print(f"✓ Received WebSocket confirmation: {confirmation_message.data}")
        
        # ===================================================================
        # STEP 4: AI-Driven Database Validation with Caching
        # ===================================================================
        # AI suggests validations based on API context
        # Results are cached for performance
        
        # Get AI validation suggestions
        suggestions = ai_validator.suggest_validations(
            api_endpoint="/api/appointments",
            http_method="POST",
            request_payload=create_request['request']['body'],
            response_data=create_request['response']['body']
        )
        
        print(f"\n✓ AI suggested {len(suggestions)} validations")
        
        # Execute high-confidence validations
        for suggestion in suggestions:
            if suggestion['confidence_score'] >= 85:
                query = suggestion['suggested_query']
                expected_value = suggestion['expected_value']
                
                print(f"  • {suggestion['validation_type']}: {suggestion['reason']} "
                      f"(confidence: {suggestion['confidence_score']}%)")
                
                # Execute database query
                result = db_client.execute_query(query)
                
                # Verify result
                if result:
                    actual_value = result[0][list(result[0].keys())[0]]
                    assert actual_value == expected_value, \
                        f"Validation failed: expected {expected_value}, got {actual_value}"
        
        # ===================================================================
        # STEP 5: Pattern-Based Validation (Using Cache)
        # ===================================================================
        # Check if patterns were cached
        
        cache_stats = ai_validator.cache.get_stats()
        print(f"\n✓ Cache Statistics:")
        print(f"  • Total requests: {cache_stats['total_requests']}")
        print(f"  • Cache hits: {cache_stats['hits']}")
        print(f"  • Cache misses: {cache_stats['misses']}")
        print(f"  • Hit rate: {cache_stats['hit_rate']:.1f}%")
        
        # Verify appointment in database directly
        appointment_query = f"""
            SELECT AppointmentID, PatientName, AppointmentDate, AppointmentType, Status
            FROM Appointments
            WHERE AppointmentID = {appointment_id}
        """
        
        appointment_record = db_client.execute_query(appointment_query)
        assert len(appointment_record) == 1, "Appointment not found in database"
        
        record = appointment_record[0]
        assert record['PatientName'] == appointment.patient_name
        assert record['Status'] == 'Confirmed'
        
        print(f"\n✅ Complete workflow validated successfully!")
        print(f"   • UI: Appointment created")
        print(f"   • API: {len(api_calls)} requests captured")
        print(f"   • WebSocket: {len(ws_messages)} messages received")
        print(f"   • AI: {len(suggestions)} validations suggested")
        print(f"   • DB: Appointment verified (ID: {appointment_id})")
    
    
    def test_request_modification_feature(self, api_interceptor):
        """
        Test request modification capabilities
        Demonstrates modifying headers and body before sending
        """
        
        # Create request modifier
        from framework.api.api_interceptor import RequestModifier
        
        modifier = RequestModifier()
        
        # Add custom headers
        modifier.add_header("X-Custom-Header", "test-value")
        modifier.add_header("X-Request-ID", "12345")
        
        # Modify request body
        original_body = {"patientName": "John Doe"}
        modifier.set_body_field("patientName", "Jane Doe")
        modifier.set_body_field("source", "automated-test")
        
        # Apply modifications
        modified_request = modifier.apply({
            'method': 'POST',
            'url': '/api/appointments',
            'headers': {},
            'body': original_body
        })
        
        # Verify modifications
        assert modified_request['headers']['X-Custom-Header'] == "test-value"
        assert modified_request['body']['patientName'] == "Jane Doe"
        assert modified_request['body']['source'] == "automated-test"
        
        print("✅ Request modification working correctly")
    
    
    def test_response_mocking_feature(self, api_interceptor):
        """
        Test response mocking capabilities
        Demonstrates mocking API responses for testing
        """
        
        # Create response modifier
        from framework.api.api_interceptor import ResponseModifier
        
        modifier = ResponseModifier()
        
        # Create mock response
        mock_response = modifier.create_mock_response(
            status_code=200,
            body={"appointmentId": 999, "status": "Confirmed"},
            headers={"X-Mock": "true"}
        )
        
        # Verify mock structure
        assert mock_response['status_code'] == 200
        assert mock_response['body']['appointmentId'] == 999
        assert mock_response['headers']['X-Mock'] == "true"
        
        # Modify existing response
        original_response = {
            'status_code': 200,
            'body': {'appointmentId': 123},
            'headers': {}
        }
        
        modifier.set_body_field("status", "Cancelled")
        modifier.add_header("X-Modified", "true")
        
        modified_response = modifier.apply(original_response)
        
        assert modified_response['body']['status'] == "Cancelled"
        assert modified_response['headers']['X-Modified'] == "true"
        
        print("✅ Response mocking working correctly")
    
    
    def test_validation_pattern_caching(self, ai_validator):
        """
        Test validation pattern caching performance
        Demonstrates cache hit/miss behavior
        """
        
        # Clear cache to start fresh
        ai_validator.cache.clear()
        
        # First request - should be a cache miss
        suggestions1 = ai_validator.suggest_validations(
            api_endpoint="/api/appointments",
            http_method="POST",
            request_payload={"patientName": "John"},
            response_data={"appointmentId": 1}
        )
        
        stats1 = ai_validator.cache.get_stats()
        assert stats1['misses'] == 1, "Expected cache miss on first request"
        
        # Second request with same parameters - should be a cache hit
        suggestions2 = ai_validator.suggest_validations(
            api_endpoint="/api/appointments",
            http_method="POST",
            request_payload={"patientName": "John"},
            response_data={"appointmentId": 1}
        )
        
        stats2 = ai_validator.cache.get_stats()
        assert stats2['hits'] == 1, "Expected cache hit on second request"
        
        # Verify same suggestions returned
        assert len(suggestions1) == len(suggestions2)
        
        print("✅ Pattern caching working correctly")
        print(f"   • Cache hit rate: {stats2['hit_rate']:.1f}%")
    
    
    def test_confidence_scoring(self, ai_validator):
        """
        Test confidence scoring algorithm
        Demonstrates how confidence scores are calculated
        """
        
        # Test with comprehensive request data (should get high confidence)
        high_confidence_suggestions = ai_validator.suggest_validations(
            api_endpoint="/api/orders/process",
            http_method="POST",
            request_payload={
                "orderId": 123,
                "customerId": 456,
                "totalAmount": 99.99,
                "orderDate": "2026-01-26",
                "status": "Pending"
            },
            response_data={
                "success": True,
                "orderId": 123,
                "status": "Confirmed"
            }
        )
        
        # Check for high confidence scores
        high_confidence_count = sum(
            1 for s in high_confidence_suggestions 
            if s['confidence_score'] >= 85
        )
        
        print(f"\n✓ High confidence validations: {high_confidence_count}/{len(high_confidence_suggestions)}")
        
        for suggestion in high_confidence_suggestions[:3]:
            print(f"  • {suggestion['validation_type']}: {suggestion['confidence_score']}% confidence")
            print(f"    Reason: {suggestion['reason']}")
        
        assert high_confidence_count > 0, "Expected at least one high-confidence validation"
        
        print("✅ Confidence scoring working correctly")


# ===================================================================
# SELENIUM GRID INTEGRATION EXAMPLE
# ===================================================================

@pytest.mark.selenium
@pytest.mark.grid
def test_selenium_grid_execution():
    """
    Test Selenium Grid remote execution
    Demonstrates running tests on remote Selenium Grid
    """
    from framework.ui.selenium_engine import SeleniumEngine
    
    # Configure for Grid execution
    engine = SeleniumEngine(
        browser_type="chrome",
        headless=False,
        use_grid=True,
        grid_url="http://selenium-hub:4444/wd/hub"
    )
    
    try:
        # Start engine (will use Grid)
        engine.start()
        
        # Perform actions
        engine.navigate("https://example.com")
        assert "Example Domain" in engine.get_page_title()
        
        print("✅ Selenium Grid execution successful")
        
    finally:
        engine.stop()


# ===================================================================
# PLAYWRIGHT CONTEXT POOLING EXAMPLE
# ===================================================================

@pytest.mark.playwright
@pytest.mark.pooling
def test_playwright_context_pooling():
    """
    Test Playwright context pooling
    Demonstrates reusing browser contexts for performance
    """
    from framework.ui.playwright_engine import PlaywrightEngine, ContextPool
    
    # Create context pool
    pool = ContextPool(max_size=5)
    
    # Create multiple engines sharing the pool
    engines = []
    for i in range(3):
        engine = PlaywrightEngine(browser_type="chromium", headless=True)
        engine.context_pool = pool
        engines.append(engine)
    
    try:
        # Execute parallel tasks
        for i, engine in enumerate(engines):
            engine.start()
            engine.navigate(f"https://example.com?task={i}")
            print(f"✓ Task {i} completed")
        
        # Check pool statistics
        print(f"\n✅ Context pooling test complete")
        print(f"   • Contexts created: {pool.current_size}")
        print(f"   • Max pool size: {pool.max_size}")
        
    finally:
        for engine in engines:
            engine.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
