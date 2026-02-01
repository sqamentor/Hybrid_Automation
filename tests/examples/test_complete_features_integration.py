"""
Complete Feature Integration Examples

Demonstrates how to use all framework features together.
"""

import pytest

from framework.accessibility.accessibility_tester import AccessibilityTester, WCAGLevel
from framework.api.api_interceptor import APIInterceptor
from framework.database.query_builder import Operator, QueryBuilder
from framework.mobile.mobile_tester import DeviceType, MobileTester
from framework.performance.performance_metrics import PerformanceMetrics
from framework.security.security_tester import SecurityTester
from framework.ui.self_healing_locators import SelfHealingLocators
from framework.visual.visual_regression import VisualRegression


@pytest.mark.complete_flow
def test_complete_ecommerce_flow_with_all_features(ui_engine, api_client, db_client, ai_validator):
    """
    Complete E2E test demonstrating ALL framework features:
    - UI automation with self-healing locators
    - API interception and correlation
    - Database validation with query builder
    - AI-driven validation suggestions
    - Visual regression testing
    - Accessibility testing
    - Performance monitoring
    - Mobile emulation
    """
    
    # ========================================================================
    # SETUP: Initialize all feature modules
    # ========================================================================
    
    # API Interception
    interceptor = APIInterceptor(ui_engine)
    interceptor.filter_api_only()  # Only capture API calls
    
    # Self-healing locators
    self_healing = SelfHealingLocators(ui_engine)
    
    # Visual regression
    visual = VisualRegression()
    
    # Accessibility testing
    a11y = AccessibilityTester(ui_engine, WCAGLevel.AA)
    
    # Mobile testing
    mobile = MobileTester(ui_engine)
    mobile.emulate_device(DeviceType.IPHONE_13_PRO)
    
    # Performance monitoring
    perf = PerformanceMetrics(ui_engine)
    
    # ========================================================================
    # STEP 1: Navigate and check performance
    # ========================================================================
    perf.start_performance_mark("page_load")
    
    ui_engine.navigate("https://example-shop.com")
    
    load_time = perf.end_performance_mark("page_load")
    assert load_time < 3000, f"Page load too slow: {load_time}ms"
    
    # Collect performance metrics
    metrics = perf.collect_metrics()
    perf.assert_load_time(3.0, metric='load_complete')
    perf.assert_web_vitals(lcp_ms=2500, fid_ms=100, cls=0.1)
    
    # ========================================================================
    # STEP 2: Accessibility check
    # ========================================================================
    a11y_results = a11y.analyze_page()
    a11y.assert_no_critical_violations()
    
    # Check specific accessibility features
    keyboard_ok = a11y.check_keyboard_navigation()
    assert keyboard_ok, "Page not fully keyboard accessible"
    
    contrast_check = a11y.check_color_contrast()
    assert contrast_check['passed'], "Color contrast issues found"
    
    # ========================================================================
    # STEP 3: Visual regression baseline (mobile)
    # ========================================================================
    screenshot_path = ui_engine.take_screenshot("homepage_mobile.png")
    visual_result = visual.compare(screenshot_path, "homepage", viewport=(390, 844))
    assert visual_result['passed'], f"Visual regression failed: {visual_result['difference_percentage']:.2%}"
    
    # ========================================================================
    # STEP 4: Product search with self-healing locators
    # ========================================================================
    try:
        # Primary locator might fail, self-healing will find alternative
        search_box = self_healing.find_element("input#search")
    except:
        # Fallback with context
        search_box = self_healing.find_element(
            "input[name='q']",
            context={'type': 'search', 'label': 'Search products'}
        )
    
    ui_engine.fill("input#search", "laptop")
    ui_engine.click("button[type='submit']")
    
    # ========================================================================
    # STEP 5: Capture and validate API calls
    # ========================================================================
    
    # Wait for API call
    ui_engine.wait_for_timeout(2000)
    
    # Get captured API calls
    api_calls = interceptor.find_api_calls()
    assert len(api_calls) > 0, "No API calls captured"
    
    search_api = next((c for c in api_calls if '/api/search' in c['url']), None)
    assert search_api, "Search API call not found"
    
    # Get correlation data from API response
    correlation_data = interceptor.get_correlation_data()
    search_id = correlation_data.get('search_id')
    assert search_id, "Search ID not found in API response"
    
    # ========================================================================
    # STEP 6: AI-driven database validation
    # ========================================================================
    
    # Get API response for AI analysis
    search_response = interceptor.get_response_by_url(search_api['url'])
    
    if search_response:
        # AI suggests database validations
        suggestions = ai_validator.suggest_validations(
            api_response=search_response['body'],
            endpoint="/api/search"
        )
        
        # Execute suggested validations
        for suggestion in suggestions:
            if suggestion['priority'] in ['Critical', 'High']:
                query_result = db_client.execute_query(suggestion['sql'])
                assert query_result, f"Validation failed: {suggestion['description']}"
    
    # ========================================================================
    # STEP 7: Manual database validation with Query Builder
    # ========================================================================
    
    # Build complex query with fluent API
    query_builder = QueryBuilder()
    query, params = (
        query_builder
        .select("id", "name", "price", "stock")
        .from_table("products")
        .where("name", "%laptop%", Operator.LIKE)
        .where("stock", 0, Operator.GT)
        .where("price", [500, 2000], Operator.BETWEEN)
        .order_by("price", "ASC")
        .limit(10)
        .build()
    )
    
    products = db_client.execute_query(query, params)
    assert len(products) > 0, "No products found matching criteria"
    
    # ========================================================================
    # STEP 8: Add to cart and checkout
    # ========================================================================
    
    ui_engine.click("button.add-to-cart:first-child")
    ui_engine.wait_for_selector("div.cart-notification")
    
    # Mobile gesture: swipe to see cart
    mobile.swipe("up")
    
    ui_engine.click("a.checkout-button")
    
    # ========================================================================
    # STEP 9: Responsive testing - test on tablet
    # ========================================================================
    
    mobile.emulate_device(DeviceType.IPAD_PRO)
    ui_engine.refresh()
    
    # Take screenshot for different viewport
    tablet_screenshot = ui_engine.take_screenshot("checkout_tablet.png")
    tablet_visual = visual.compare(tablet_screenshot, "checkout", viewport=(1024, 1366))
    
    # ========================================================================
    # STEP 10: Performance mark for checkout flow
    # ========================================================================
    
    perf.start_performance_mark("checkout_flow")
    
    # Fill checkout form
    ui_engine.fill("input[name='name']", "John Doe")
    ui_engine.fill("input[name='email']", "john@example.com")
    ui_engine.fill("input[name='address']", "123 Main St")
    
    ui_engine.click("button.submit-order")
    
    checkout_duration = perf.end_performance_mark("checkout_flow")
    assert checkout_duration < 5000, f"Checkout too slow: {checkout_duration}ms"
    
    # ========================================================================
    # STEP 11: Verify order in database
    # ========================================================================
    
    # Get order ID from API interception
    order_api = next((c for c in interceptor.find_api_calls() if '/api/orders' in c['url']), None)
    
    if order_api:
        order_response = interceptor.get_response_by_url(order_api['url'])
        order_id = order_response['body'].get('order_id')
        
        # Query order from database
        order_query = (
            QueryBuilder()
            .select("*")
            .from_table("orders")
            .where("id", order_id)
            .limit(1)
        )
        
        order_data = db_client.execute_query(*order_query.build())
        assert len(order_data) == 1, "Order not found in database"
        assert order_data[0]['status'] == 'pending', "Order status incorrect"
    
    # ========================================================================
    # STEP 12: Generate comprehensive reports
    # ========================================================================
    
    # Performance report
    perf.generate_report("reports/performance_report.html")
    
    # Visual regression report
    visual.generate_html_report("reports/visual_report.html")
    
    # Accessibility report
    a11y.generate_report("reports/accessibility_report.html")
    
    # Self-healing report
    healing_stats = self_healing.get_healing_report()
    if healing_stats['total_heals'] > 0:
        print(f"Self-healing activated {healing_stats['total_heals']} times")
    
    # API interception summary
    api_summary = interceptor.get_summary()
    print(f"Captured {api_summary['total_requests']} API requests")


@pytest.mark.security
def test_security_scan_with_owasp_zap():
    """Security testing with OWASP ZAP"""
    
    security = SecurityTester("http://localhost:8080")
    security.set_api_key("your-zap-api-key")
    
    target_url = "https://example-shop.com"
    
    # Start security scan
    security.start_zap_session("security_test")
    
    # Spider the site
    security.spider_url(target_url, max_children=10)
    
    # Run active scan
    security.active_scan(target_url)
    
    # Get alerts
    alerts = security.get_alerts(target_url)
    
    # Assert no high-risk vulnerabilities
    security.assert_no_high_risk_vulnerabilities()
    
    # Generate security report
    security.generate_report("reports/security_report.html")


@pytest.mark.ml_optimization
def test_ml_test_optimization():
    """ML-based test optimization"""
    from framework.ml.ml_test_optimizer import MLTestOptimizer
    
    optimizer = MLTestOptimizer()
    
    # Analyze failure patterns
    patterns = optimizer.analyze_failure_patterns()
    
    # Get flaky tests
    flaky_tests = optimizer.get_flaky_tests(threshold=0.3)
    print(f"Flaky tests detected: {flaky_tests}")
    
    # Get optimal test order
    test_list = [
        "test_login",
        "test_checkout",
        "test_search",
        "test_profile"
    ]
    
    changed_files = ["checkout.py", "payment.py"]
    optimal_order = optimizer.get_optimal_test_order(test_list, changed_files)
    
    print("Optimal test execution order:")
    for test, probability in optimal_order:
        print(f"  {test}: {probability:.2%} failure probability")
    
    # Generate insights report
    optimizer.generate_insights_report()


@pytest.mark.nl_generation
def test_natural_language_test_generation():
    """Generate tests from natural language"""
    from framework.ai.nl_test_generator import NaturalLanguageTestGenerator
    
    generator = NaturalLanguageTestGenerator()
    
    # Generate single test
    description = """
    User logs in with valid credentials,
    navigates to profile page,
    updates their email address,
    and sees a success message
    """
    
    test_code = generator.generate_test(description, test_type="ui")
    print("Generated test code:")
    print(test_code)
    
    # Save to file
    generator.save_generated_test(test_code, "tests/generated/test_profile_update.py")


@pytest.mark.graphql
def test_graphql_api():
    """GraphQL API testing"""
    from framework.api.graphql_client import GraphQLClient
    
    client = GraphQLClient("https://api.example.com/graphql")
    
    # Introspect schema
    schema = client.introspect_schema()
    
    # List available queries
    queries = client.get_queries()
    print(f"Available queries: {queries}")
    
    # Execute query
    query = """
    query GetUser($id: ID!) {
        user(id: $id) {
            id
            name
            email
        }
    }
    """
    
    result = client.query(query, variables={"id": "123"})
    
    # Assertions
    client.assert_response_has_field(result, "user.email")
    client.assert_field_type(result, "user.name", str)


@pytest.mark.websocket
def test_websocket_realtime():
    """WebSocket real-time testing"""
    from framework.api.websocket_tester import SyncWebSocketTester
    
    with SyncWebSocketTester("wss://echo.websocket.org") as ws:
        # Send message
        ws.send_message({"type": "ping", "data": "Hello"})
        
        # Wait for response
        message = ws.wait_for_message(timeout=5)
        assert message is not None
        
        # Assert specific message type
        ws.send_message({"type": "subscribe", "channel": "orders"})
        ws.assert_message_type_received("subscription_confirmed", timeout=5)


@pytest.mark.multilanguage
def test_multilanguage_support(ui_engine):
    """Multi-language testing"""
    from framework.i18n.multi_language import MultiLanguageSupport, RTLTesting
    
    i18n = MultiLanguageSupport()
    
    # Test in multiple languages
    for lang_code in ['en', 'es', 'fr', 'de']:
        i18n.set_language(lang_code)
        i18n.set_browser_language(ui_engine, lang_code)
        
        ui_engine.navigate("https://example.com")
        
        # Generate language-specific test data
        name = i18n.generate_test_data('name', lang_code)
        email = i18n.generate_test_data('email', lang_code)
        
        # Verify translations
        title_text = ui_engine.get_text("h1.page-title")
        expected_title = i18n.get_text('app.title')
        
        assert title_text == expected_title, f"Translation mismatch for {lang_code}"
    
    # RTL language testing
    i18n.set_language('ar')
    i18n.set_browser_language(ui_engine, 'ar')
    ui_engine.navigate("https://example.com")
    
    rtl_correct = RTLTesting.verify_rtl_layout(ui_engine, 'ar')
    assert rtl_correct, "RTL layout not properly applied for Arabic"
