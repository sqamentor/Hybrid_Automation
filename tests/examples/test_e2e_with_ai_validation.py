"""
Complete End-to-End Example: AI-Driven Validation

This example demonstrates the full workflow from UI interaction to AI-suggested
database validations in a real-world e-commerce order placement scenario.
"""

import pytest
from framework.intelligence import AIValidationSuggester, suggest_and_validate
from framework.core.execution_flow import execution_flow


@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.module("checkout")
class TestE2EOrderWithAIValidation:
    """
    Complete end-to-end test with AI-driven validation
    
    Flow:
    1. UI: User browses product catalog and adds items to cart
    2. UI: User proceeds to checkout and submits order
    3. API: Framework captures order submission API call
    4. AI: Analyzes API response and suggests DB validations
    5. DB: Executes suggested validations
    6. Evidence: Collects all artifacts (screenshots, queries, results)
    """
    
    def test_complete_order_flow_with_ai(
        self,
        ui_engine,
        api_client,
        db_client,
        ui_url
    ):
        """
        Complete order placement with AI-suggested validations
        """
        
        # ================================================================
        # STEP 1: UI INTERACTIONS
        # ================================================================
        
        execution_flow.start_test("E2E Order Placement with AI Validation")
        
        # Navigate to product catalog
        ui_engine.navigate(f"{ui_url}/products")
        execution_flow.record_ui_action("Navigate to product catalog")
        
        # Add first product
        ui_engine.wait_for_element('[data-product-id="PROD456"]')
        ui_engine.click('[data-product-id="PROD456"] .add-to-cart')
        execution_flow.record_ui_action("Added Product PROD456 to cart")
        
        # Add second product
        ui_engine.click('[data-product-id="PROD789"] .add-to-cart')
        execution_flow.record_ui_action("Added Product PROD789 to cart")
        
        # Verify cart count
        cart_count = ui_engine.get_text('.cart-count')
        assert cart_count == '2', f"Expected 2 items in cart, got {cart_count}"
        
        # Navigate to checkout
        ui_engine.click('.checkout-button')
        ui_engine.wait_for_url(f"{ui_url}/checkout")
        execution_flow.record_ui_action("Navigated to checkout")
        
        # Fill shipping information
        ui_engine.fill('#shipping_address', '123 Main Street')
        ui_engine.fill('#shipping_city', 'San Francisco')
        ui_engine.fill('#shipping_zip', '94102')
        execution_flow.record_ui_action("Filled shipping information")
        
        # Take screenshot before submission
        ui_engine.take_screenshot("screenshots/before_order_submit.png")
        
        # Submit order
        ui_engine.click('#submit_order_button')
        execution_flow.record_ui_action("Clicked submit order")
        
        # Wait for confirmation
        ui_engine.wait_for_element('.order-confirmation')
        
        # ================================================================
        # STEP 2: API VALIDATION
        # ================================================================
        
        # Get order confirmation number from UI
        order_id = ui_engine.get_text('.order-id')
        execution_flow.record_ui_action(f"Order ID displayed: {order_id}")
        
        # Fetch order details via API
        order_response = api_client.get(f"/api/orders/{order_id}")
        api_client.assert_status_code(200)
        
        order_data = order_response.json()
        execution_flow.record_api_call(
            method="GET",
            endpoint=f"/api/orders/{order_id}",
            response=order_data,
            status_code=200
        )
        
        # Validate order response structure
        assert 'order_id' in order_data, "Order ID missing in response"
        assert 'transaction_id' in order_data, "Transaction ID missing"
        assert 'status' in order_data, "Order status missing"
        assert order_data['status'] == 'PENDING', f"Expected PENDING, got {order_data['status']}"
        
        # ================================================================
        # STEP 3: AI-DRIVEN DATABASE VALIDATION
        # ================================================================
        
        print("\n" + "="*80)
        print("AI ANALYZING API RESPONSE AND SUGGESTING DB VALIDATIONS")
        print("="*80)
        
        suggester = AIValidationSuggester()
        
        # AI analyzes the order creation and suggests validations
        strategy = suggester.suggest_validations(
            api_endpoint="/api/orders/submit",
            api_method="POST",
            api_request={
                "customer_id": order_data.get('customer_id'),
                "items": order_data.get('items', []),
                "shipping_address": "123 Main Street, San Francisco, 94102"
            },
            api_response=order_data
        )
        
        # Print AI-generated validation report
        report = suggester.generate_validation_report(strategy)
        print(report)
        
        # ================================================================
        # STEP 4: EXECUTE AI-SUGGESTED VALIDATIONS
        # ================================================================
        
        print("\n" + "="*80)
        print("EXECUTING AI-SUGGESTED VALIDATIONS")
        print("="*80)
        
        validation_results = []
        
        for idx, suggestion in enumerate(strategy.suggestions, 1):
            
            # Execute all critical and high priority validations
            if suggestion.priority in ['critical', 'high']:
                
                print(f"\n[{suggestion.priority.upper()}] {suggestion.reason}")
                print(f"Confidence: {suggestion.confidence}%")
                
                # Apply correlation values from API response
                query = suggester.apply_correlations(
                    suggestion,
                    strategy.correlation_context
                )
                
                print(f"Query: {query}")
                
                try:
                    # Execute validation query
                    result = db_client.execute_query(query)
                    
                    # Check expected result
                    passed = True
                    if 'row_count' in suggestion.expected_result:
                        expected_count = suggestion.expected_result['row_count']
                        actual_count = len(result)
                        passed = actual_count == expected_count
                        
                        if passed:
                            print(f"✓ PASSED: Found {actual_count} row(s) as expected")
                        else:
                            print(f"✗ FAILED: Expected {expected_count} rows, got {actual_count}")
                    
                    elif 'row_count_gte' in suggestion.expected_result:
                        min_count = suggestion.expected_result['row_count_gte']
                        actual_count = len(result)
                        passed = actual_count >= min_count
                        
                        if passed:
                            print(f"✓ PASSED: Found {actual_count} row(s) (>= {min_count})")
                        else:
                            print(f"✗ FAILED: Expected >= {min_count} rows, got {actual_count}")
                    
                    else:
                        # Just check that query executed successfully
                        print(f"✓ PASSED: Query executed successfully, {len(result)} row(s) returned")
                    
                    # Record validation in execution flow
                    execution_flow.record_db_validation(
                        query=query,
                        result=result,
                        assertion=f"AI-suggested: {suggestion.reason}"
                    )
                    
                    validation_results.append({
                        'suggestion': suggestion.reason,
                        'priority': suggestion.priority,
                        'confidence': suggestion.confidence,
                        'query': query,
                        'result': result,
                        'passed': passed
                    })
                
                except Exception as e:
                    print(f"✗ FAILED: {str(e)}")
                    validation_results.append({
                        'suggestion': suggestion.reason,
                        'priority': suggestion.priority,
                        'confidence': suggestion.confidence,
                        'query': query,
                        'error': str(e),
                        'passed': False
                    })
        
        # ================================================================
        # STEP 5: VALIDATION SUMMARY
        # ================================================================
        
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)
        
        passed_count = sum(1 for v in validation_results if v['passed'])
        total_count = len(validation_results)
        
        print(f"\nTotal Validations: {total_count}")
        print(f"Passed: {passed_count}")
        print(f"Failed: {total_count - passed_count}")
        print(f"Success Rate: {(passed_count/total_count)*100:.1f}%")
        
        # Assert all critical validations passed
        critical_failures = [
            v for v in validation_results 
            if v['priority'] == 'critical' and not v['passed']
        ]
        
        assert len(critical_failures) == 0, \
            f"Critical validations failed: {[v['suggestion'] for v in critical_failures]}"
        
        print("\n✓ All critical validations passed!")
        
        # ================================================================
        # STEP 6: EVIDENCE COLLECTION
        # ================================================================
        
        # Take final screenshot
        ui_engine.take_screenshot("screenshots/order_confirmed.png")
        
        # Generate execution summary
        summary = execution_flow.generate_summary()
        print("\n" + "="*80)
        print("EXECUTION SUMMARY")
        print("="*80)
        print(summary)
        
        execution_flow.end_test()


@pytest.mark.integration
@pytest.mark.module("checkout")
class TestConvenienceFunctionApproach:
    """
    Same test using the convenience function for simpler code
    """
    
    def test_order_with_auto_validation(
        self,
        ui_engine,
        api_client,
        db_client,
        ui_url
    ):
        """
        Simplified approach using suggest_and_validate()
        """
        
        # UI interactions (same as above)
        ui_engine.navigate(f"{ui_url}/products")
        ui_engine.click('[data-product-id="PROD456"] .add-to-cart')
        ui_engine.click('.checkout-button')
        ui_engine.fill('#shipping_address', '123 Main Street')
        ui_engine.click('#submit_order_button')
        ui_engine.wait_for_element('.order-confirmation')
        
        # Get order ID
        order_id = ui_engine.get_text('.order-id')
        
        # Fetch order details
        order_response = api_client.get(f"/api/orders/{order_id}")
        order_data = order_response.json()
        
        # AI suggests and executes validations automatically
        results = suggest_and_validate(
            api_endpoint="/api/orders/submit",
            api_method="POST",
            api_request={},
            api_response=order_data,
            db_client=db_client,
            auto_execute=True  # AI does everything!
        )
        
        # Print report
        print(results['report'])
        
        # Assert all validations passed
        passed = sum(1 for v in results['validations_executed'] if v.get('passed', False))
        total = len(results['validations_executed'])
        
        print(f"\n✓ {passed}/{total} validations passed")
        
        assert passed == total, "Some validations failed"


@pytest.mark.integration
@pytest.mark.module("payments")
class TestPaymentValidation:
    """
    Payment processing with AI validation
    """
    
    def test_payment_processing(
        self,
        ui_engine,
        api_client,
        db_client,
        ai_validator,
        ui_url
    ):
        """
        Test payment processing with AI-suggested validations
        """
        
        # Place order (prerequisite)
        order_id = "ORD-12345"  # From previous test or setup
        
        # Navigate to payment page
        ui_engine.navigate(f"{ui_url}/payment/{order_id}")
        
        # Fill payment details
        ui_engine.fill('#card_number', '4111111111111111')
        ui_engine.fill('#card_expiry', '12/28')
        ui_engine.fill('#card_cvv', '123')
        ui_engine.fill('#card_name', 'John Doe')
        
        # Submit payment
        ui_engine.click('#submit_payment')
        ui_engine.wait_for_element('.payment-success')
        
        # Get payment confirmation
        payment_id = ui_engine.get_text('.payment-id')
        
        # Fetch payment details via API
        payment_response = api_client.get(f"/api/payments/{payment_id}")
        payment_data = payment_response.json()
        
        # AI suggests validations
        strategy = ai_validator.suggest_validations(
            api_endpoint="/api/payments/process",
            api_method="POST",
            api_request={"order_id": order_id, "amount": payment_data.get('amount')},
            api_response=payment_data
        )
        
        # Execute high priority validations
        for suggestion in strategy.suggestions:
            if suggestion.priority in ['critical', 'high']:
                query = ai_validator.apply_correlations(
                    suggestion,
                    strategy.correlation_context
                )
                
                result = db_client.execute_query(query)
                
                # AI should suggest:
                # - Payment record created
                # - Order status updated to PAID
                # - Transaction log entry
                # - Customer balance updated
                
                print(f"✓ {suggestion.reason}: {len(result)} rows")
                assert len(result) > 0, f"Validation failed: {suggestion.reason}"


# ================================================================
# HELPER: Custom Assertions
# ================================================================

def assert_ai_suggested_validations_passed(validation_results, priority_level='critical'):
    """
    Custom assertion for AI-suggested validations
    
    Args:
        validation_results: List of validation results
        priority_level: Minimum priority level to check
    """
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    min_priority = priority_order[priority_level]
    
    relevant_validations = [
        v for v in validation_results
        if priority_order.get(v['priority'], 4) <= min_priority
    ]
    
    failed = [v for v in relevant_validations if not v['passed']]
    
    if failed:
        error_msg = f"AI-suggested validations failed:\n"
        for v in failed:
            error_msg += f"  - [{v['priority'].upper()}] {v['suggestion']}\n"
            if 'error' in v:
                error_msg += f"    Error: {v['error']}\n"
        raise AssertionError(error_msg)
    
    print(f"✓ All {priority_level}+ validations passed ({len(relevant_validations)} total)")


# ================================================================
# RUN INSTRUCTIONS
# ================================================================

"""
To run this example:

1. Set environment variables:
   $env:OPENAI_API_KEY = "sk-your-api-key"
   $env:TEST_ENV = "dev"

2. Run specific test:
   pytest tests/examples/test_e2e_with_ai_validation.py::TestE2EOrderWithAIValidation::test_complete_order_flow_with_ai -v

3. Run all examples:
   pytest tests/examples/test_e2e_with_ai_validation.py -v

4. Run with detailed output:
   pytest tests/examples/test_e2e_with_ai_validation.py -v -s

Expected output:
================================================================================
AI ANALYZING API RESPONSE AND SUGGESTING DB VALIDATIONS
================================================================================

[AI generates validation report with 6-7 suggestions]

================================================================================
EXECUTING AI-SUGGESTED VALIDATIONS
================================================================================

[CRITICAL] Verify order record was created
Confidence: 98%
Query: SELECT * FROM orders WHERE transaction_id = 'TXN-001'
✓ PASSED: Found 1 row(s) as expected

[CRITICAL] Verify order items were inserted
Confidence: 95%
Query: SELECT COUNT(*) FROM order_items WHERE order_id = 'ORD-12345'
✓ PASSED: Found 2 row(s) (>= 1)

[HIGH] Verify inventory was decremented
Confidence: 92%
Query: SELECT product_id, quantity_available FROM inventory WHERE...
✓ PASSED: Query executed successfully, 2 row(s) returned

================================================================================
VALIDATION SUMMARY
================================================================================

Total Validations: 6
Passed: 6
Failed: 0
Success Rate: 100.0%

✓ All critical validations passed!
"""
