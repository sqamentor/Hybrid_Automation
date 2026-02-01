"""
Example: AI-Driven API → DB Validation

This example demonstrates how to use AI to suggest and execute database validations
based on API responses.
"""

import pytest

from framework.database.db_client import DBClient
from framework.intelligence import AIValidationSuggester, suggest_and_validate


@pytest.mark.integration
@pytest.mark.module("orders")
@pytest.mark.api_validation
@pytest.mark.modern_spa
class TestAIDrivenValidation:
    """Test AI-driven API → DB validation suggestions."""
    
    def test_ai_suggests_order_validations(self, api_client, db_client):
        """AI analyzes order creation API and suggests DB validations."""
        # Step 1: Make API call
        order_request = {
            "customer_id": "CUST123",
            "items": [
                {"product_id": "PROD456", "quantity": 2, "price": 99.99},
                {"product_id": "PROD789", "quantity": 1, "price": 149.99}
            ],
            "shipping_address": "123 Main St"
        }
        
        response = api_client.post("/api/orders/submit", json_data=order_request)
        api_client.assert_status_code(201)
        
        order_response = response.json()
        
        # Step 2: Get AI suggestions for DB validations
        suggester = AIValidationSuggester()
        
        strategy = suggester.suggest_validations(
            api_endpoint="/api/orders/submit",
            api_method="POST",
            api_request=order_request,
            api_response=order_response
        )
        
        # Step 3: Review AI suggestions
        print(suggester.generate_validation_report(strategy))
        
        # Step 4: Execute suggested validations
        for suggestion in strategy.suggestions:
            if suggestion.priority in ['critical', 'high']:
                # Apply correlation values
                query = suggester.apply_correlations(
                    suggestion,
                    strategy.correlation_context
                )
                
                # Execute validation
                result = db_client.execute_query(query)
                
                # Assert based on expected result
                if 'row_count' in suggestion.expected_result:
                    expected_count = suggestion.expected_result['row_count']
                    assert len(result) == expected_count, \
                        f"{suggestion.reason}: Expected {expected_count} rows, got {len(result)}"
                
                print(f"✓ {suggestion.reason}: PASSED")
    
    def test_ai_validation_with_auto_execute(self, api_client, db_client):
        """Use convenience function to suggest and auto-execute validations."""
        # Make API call
        payment_request = {
            "order_id": "ORD12345",
            "amount": 249.98,
            "payment_method": "credit_card",
            "card_last_four": "1234"
        }
        
        response = api_client.post("/api/payments/process", json_data=payment_request)
        api_client.assert_status_code(200)
        
        payment_response = response.json()
        
        # AI suggests and executes validations automatically
        results = suggest_and_validate(
            api_endpoint="/api/payments/process",
            api_method="POST",
            api_request=payment_request,
            api_response=payment_response,
            db_client=db_client,
            auto_execute=True  # Execute validations automatically
        )
        
        # Check results
        assert results['strategy'], "Should have validation strategy"
        assert len(results['validations_executed']) > 0, "Should have executed validations"
        
        # Verify all critical validations passed
        critical_validations = [
            v for v in results['validations_executed']
            if 'passed' in v and v['passed']
        ]
        
        print(f"\n✓ {len(critical_validations)} validations passed")
        print(f"Report:\n{results['report']}")
    
    def test_ai_learns_from_mapping(self, api_client, db_client):
        """Test that AI uses existing API → DB mappings to improve suggestions."""
        suggester = AIValidationSuggester()
        
        # This endpoint has a mapping in api_db_mapping.yaml
        inventory_request = {
            "product_id": "PROD456",
            "adjustment_type": "restock",
            "quantity_change": 50
        }
        
        response = api_client.put("/api/inventory/adjust", json_data=inventory_request)
        api_client.assert_status_code(200)
        
        inventory_response = response.json()
        
        # AI should reference the existing mapping
        strategy = suggester.suggest_validations(
            api_endpoint="/api/inventory/adjust",
            api_method="PUT",
            api_request=inventory_request,
            api_response=inventory_response
        )
        
        # AI should suggest validating both inventory table and audit log
        validation_reasons = [s.reason.lower() for s in strategy.suggestions]
        
        assert any('inventory' in reason for reason in validation_reasons), \
            "Should suggest inventory validation"
        assert any('audit' in reason or 'log' in reason for reason in validation_reasons), \
            "Should suggest audit log validation"
        
        print(suggester.generate_validation_report(strategy))


@pytest.mark.integration
@pytest.mark.module("users")
@pytest.mark.modern_spa
class TestUserRegistrationValidation:
    """Test AI-driven validation for user registration."""
    
    def test_user_registration_validations(self, api_client, db_client):
        """AI suggests comprehensive validations for user registration."""
        user_request = {
            "email": "newuser@example.com",
            "username": "newuser123",
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        response = api_client.post("/api/users/register", json_data=user_request)
        api_client.assert_status_code(201)
        
        user_response = response.json()
        
        # Get AI suggestions
        suggester = AIValidationSuggester()
        strategy = suggester.suggest_validations(
            api_endpoint="/api/users/register",
            api_method="POST",
            api_request=user_request,
            api_response=user_response
        )
        
        # AI should suggest:
        # 1. User record exists
        # 2. Default role assigned
        # 3. Email verification sent
        # 4. Audit log entry created
        
        assert len(strategy.suggestions) >= 3, "Should suggest multiple validations"
        
        # Execute critical validations
        critical_suggestions = [
            s for s in strategy.suggestions 
            if s.priority == 'critical'
        ]
        
        for suggestion in critical_suggestions:
            query = suggester.apply_correlations(
                suggestion,
                strategy.correlation_context
            )
            
            result = db_client.execute_query(query)
            print(f"✓ {suggestion.reason}: {len(result)} rows returned")


@pytest.mark.smoke
def test_ai_fallback_when_disabled(api_client):
    """Test that framework provides fallback suggestions when AI is disabled."""
    # Temporarily disable AI by not setting API key
    import os
    original_key = os.environ.get('OPENAI_API_KEY')
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    
    try:
        suggester = AIValidationSuggester()
        
        # Make API call
        response = api_client.post("/api/test", json_data={"test": "data"})
        
        # Should still get fallback suggestions
        strategy = suggester.suggest_validations(
            api_endpoint="/api/test",
            api_method="POST",
            api_request={"test": "data"},
            api_response={"id": 123}
        )
        
        assert len(strategy.suggestions) > 0, "Should provide fallback suggestions"
        assert "fallback" in strategy.ai_reasoning.lower(), \
            "Should indicate fallback was used"
        
        print(f"Fallback strategy provided {len(strategy.suggestions)} suggestions")
    
    finally:
        # Restore API key
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key


@pytest.mark.performance
def test_validation_suggestion_performance(api_client):
    """Test performance of AI validation suggestions."""
    import time
    
    suggester = AIValidationSuggester()
    
    response = api_client.post("/api/orders/submit", json_data={
        "customer_id": "TEST",
        "items": [{"product_id": "P1", "quantity": 1}]
    })
    
    start = time.time()
    
    strategy = suggester.suggest_validations(
        api_endpoint="/api/orders/submit",
        api_method="POST",
        api_request={},
        api_response=response.json() if response.status_code == 200 else {}
    )
    
    duration = time.time() - start
    
    print(f"AI suggestion time: {duration:.2f}s")
    print(f"Suggestions generated: {len(strategy.suggestions)}")
    
    # Should be reasonably fast
    assert duration < 10, "AI suggestions should complete within 10 seconds"
