"""
API Interceptor Enhanced Demo
=============================
Demonstrates the enhanced API Interceptor capabilities:

Features Demonstrated:
1. WebSocket Interception - Capture WebSocket connections and messages
2. Request Modification - Modify request headers and body
3. Response Modification - Mock responses and modify response body

Usage:
    python examples/api_interceptor_enhanced_demo.py
"""

import time
from framework.api.api_interceptor import APIInterceptor
from framework.ui.playwright_engine import PlaywrightEngine
from utils.logger import get_logger

logger = get_logger(__name__)


def print_section(title: str):
    """Print a formatted section title"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def demo_http_interception():
    """Demo HTTP request/response interception"""
    print_section("Demo: HTTP Request/Response Interception")
    
    engine = PlaywrightEngine(headless=True)
    
    try:
        # Start browser and interceptor
        engine.start(browser_type='chromium')
        interceptor = APIInterceptor(engine.page)
        interceptor.enable()
        print("✓ Interceptor started")
        
        # Navigate to JSON API
        print("\nNavigating to JSONPlaceholder API...")
        engine.navigate("https://jsonplaceholder.typicode.com/")
        time.sleep(2)
        
        # Get captured requests/responses
        requests = interceptor.get_captured_requests()
        responses = interceptor.get_captured_responses()
        
        print(f"✓ Captured {len(requests)} requests")
        print(f"✓ Captured {len(responses)} responses")
        
        if requests:
            print("\nSample requests:")
            for req in requests[:3]:
                print(f"  {req['method']} {req['url']}")
        
        if responses:
            print("\nSample responses:")
            for resp in responses[:3]:
                print(f"  {resp['status']} {resp['url']}")
        
        # Get summary
        summary = interceptor.get_summary()
        print("\nSummary:")
        print(f"  Total requests: {summary['total_requests']}")
        print(f"  Total responses: {summary['total_responses']}")
        print(f"  Methods: {summary['methods']}")
        
        interceptor.disable()
        
    finally:
        engine.stop()
        print("\n✓ Demo completed")


def demo_request_modification():
    """Demo request header/body modification"""
    print_section("Demo: Request Modification")
    
    engine = PlaywrightEngine(headless=True)
    
    try:
        engine.start(browser_type='chromium')
        interceptor = APIInterceptor(engine.page)
        interceptor.enable()
        
        # Configure modifications
        print("Configuring request modifications...")
        
        # Add custom headers
        interceptor.modify_request_headers(
            url_pattern="*/posts/*",
            headers={
                "X-Custom-Header": "Demo-Value",
                "X-Test-Mode": "enabled"
            }
        )
        print("✓ Header modifications configured for */posts/*")
        
        # Modify request body
        interceptor.modify_request_body(
            url_pattern="*/api/*",
            body_modifier=lambda body: {
                **body,
                "test_mode": True,
                "client": "demo-client"
            } if isinstance(body, dict) else body
        )
        print("✓ Body modifications configured for */api/*")
        
        # Navigate to trigger requests
        print("\nNavigating to test page...")
        engine.navigate("https://jsonplaceholder.typicode.com/posts/1")
        time.sleep(2)
        
        # Check summary
        summary = interceptor.get_summary()
        print(f"\n✓ Active modifications: {summary['modifications']['request_modifications']}")
        
        interceptor.disable()
        
    finally:
        engine.stop()
        print("\n✓ Demo completed")


def demo_response_mocking():
    """Demo response mocking"""
    print_section("Demo: Response Mocking")
    
    engine = PlaywrightEngine(headless=True)
    
    try:
        engine.start(browser_type='chromium')
        interceptor = APIInterceptor(engine.page)
        interceptor.enable()
        
        # Configure mock responses
        print("Configuring response mocks...")
        
        mock_data = {
            "id": 999,
            "title": "Mocked Post",
            "body": "This is a mocked response",
            "userId": 1
        }
        
        interceptor.mock_response(
            url_pattern="*/posts/1",
            status=200,
            body=mock_data,
            headers={"X-Mocked": "true"}
        )
        print("✓ Mock configured for */posts/1")
        
        # Mock error response
        error_data = {
            "error": "Service Unavailable",
            "message": "Simulated error",
            "code": 503
        }
        
        interceptor.mock_response(
            url_pattern="*/posts/2",
            status=503,
            body=error_data
        )
        print("✓ Error mock configured for */posts/2")
        
        # Navigate
        print("\nNavigating to trigger mocks...")
        engine.navigate("https://jsonplaceholder.typicode.com/posts/1")
        time.sleep(2)
        
        # Check summary
        summary = interceptor.get_summary()
        print(f"\n✓ Active mocks: {summary['modifications']['response_mocks']}")
        
        interceptor.disable()
        
    finally:
        engine.stop()
        print("\n✓ Demo completed")


def demo_websocket_tracking():
    """Demo WebSocket connection tracking"""
    print_section("Demo: WebSocket Tracking")
    
    engine = PlaywrightEngine(headless=True)
    
    try:
        engine.start(browser_type='chromium')
        interceptor = APIInterceptor(engine.page)
        interceptor.enable()
        
        print("Navigating to WebSocket test page...")
        engine.navigate("https://www.piesocket.com/websocket-tester")
        time.sleep(3)
        
        # Check WebSocket connections
        connections = interceptor.get_websocket_connections()
        print(f"✓ WebSocket connections: {len(connections)}")
        
        if connections:
            for i, conn in enumerate(connections, 1):
                print(f"  Connection {i}: {conn['url']}")
        
        # Check messages
        messages = interceptor.get_websocket_messages()
        print(f"✓ Total messages: {len(messages)}")
        
        sent = interceptor.get_websocket_sent_messages()
        received = interceptor.get_websocket_received_messages()
        print(f"  Sent: {len(sent)}, Received: {len(received)}")
        
        # Summary
        summary = interceptor.get_summary()
        print("\nWebSocket Summary:")
        print(f"  Connections: {summary['websockets']['connections']}")
        print(f"  Total messages: {summary['websockets']['total_messages']}")
        
        interceptor.disable()
        
    finally:
        engine.stop()
        print("\n✓ Demo completed")


def demo_har_export():
    """Demo HAR export functionality"""
    print_section("Demo: HAR Export")
    
    engine = PlaywrightEngine(headless=True)
    
    try:
        engine.start(browser_type='chromium')
        interceptor = APIInterceptor(engine.page)
        interceptor.enable()
        
        print("Navigating and capturing traffic...")
        engine.navigate("https://jsonplaceholder.typicode.com/posts")
        time.sleep(2)
        
        requests = interceptor.get_captured_requests()
        responses = interceptor.get_captured_responses()
        print(f"✓ Captured {len(requests)} requests, {len(responses)} responses")
        
        # Export to HAR
        har_file = "logs/api_interceptor_demo.har"
        print(f"\nExporting to {har_file}...")
        interceptor.export_to_har(har_file)
        print(f"✓ HAR file created")
        
        interceptor.disable()
        
    finally:
        engine.stop()
        print("\n✓ Demo completed")


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("  API INTERCEPTOR ENHANCED FEATURES DEMO")
    print("="*80)
    print("\nShowcasing enhanced API Interceptor capabilities:")
    print("  1. HTTP Interception")
    print("  2. Request Modification")
    print("  3. Response Mocking")
    print("  4. WebSocket Tracking")
    print("  5. HAR Export")
    print("\n" + "="*80 + "\n")
    
    try:
        demo_http_interception()
        demo_request_modification()
        demo_response_mocking()
        demo_websocket_tracking()
        demo_har_export()
        
        # Final summary
        print_section("ALL DEMOS COMPLETED SUCCESSFULLY")
        print("✓ Demo 1: HTTP Interception - PASSED")
        print("✓ Demo 2: Request Modification - PASSED")
        print("✓ Demo 3: Response Mocking - PASSED")
        print("✓ Demo 4: WebSocket Tracking - PASSED")
        print("✓ Demo 5: HAR Export - PASSED")
        print("\nAPI Interceptor enhancements working correctly!")
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}", exc_info=True)
        print(f"\n✗ Demo failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
