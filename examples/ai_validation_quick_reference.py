"""
Quick Reference: AI-Driven API → DB Validation Suggestions

This module demonstrates common usage patterns for AI-powered validation suggestions.
"""

# ========================================================================
# BASIC USAGE
# ========================================================================

from framework.intelligence import AIValidationSuggester, suggest_and_validate

# ========================================================================
# Pattern 1: Review Suggestions Before Executing
# ========================================================================

def pattern_1_review_suggestions(api_client, db_client):
    """Get AI suggestions and review before executing"""
    
    # Make API call
    response = api_client.post("/api/orders/submit", json_data={
        "customer_id": "CUST123",
        "items": [{"product_id": "PROD456", "quantity": 2}]
    })
    
    # Get AI suggestions
    suggester = AIValidationSuggester()
    strategy = suggester.suggest_validations(
        api_endpoint="/api/orders/submit",
        api_method="POST",
        api_request={"customer_id": "CUST123"},
        api_response=response.json()
    )
    
    # Review suggestions
    print(suggester.generate_validation_report(strategy))
    
    # Execute only critical validations
    for suggestion in strategy.suggestions:
        if suggestion.priority == 'critical':
            query = suggester.apply_correlations(
                suggestion,
                strategy.correlation_context
            )
            result = db_client.execute_query(query)
            print(f"✓ {suggestion.reason}: {len(result)} rows")


# ========================================================================
# Pattern 2: Auto-Execute All Suggestions
# ========================================================================

def pattern_2_auto_execute(api_client, db_client):
    """Use convenience function to auto-execute all validations"""
    
    # Make API call
    response = api_client.post("/api/payments/process", json_data={
        "order_id": "ORD123",
        "amount": 99.99
    })
    
    # AI suggests AND executes automatically
    results = suggest_and_validate(
        api_endpoint="/api/payments/process",
        api_method="POST",
        api_request={"order_id": "ORD123", "amount": 99.99},
        api_response=response.json(),
        db_client=db_client,
        auto_execute=True  # Execute all suggestions
    )
    
    # Check results
    print(results['report'])
    
    # Verify all passed
    passed = sum(1 for v in results['validations_executed'] if v['passed'])
    total = len(results['validations_executed'])
    print(f"✓ {passed}/{total} validations passed")


# ========================================================================
# Pattern 3: Integration Test with AI Validation
# ========================================================================

def pattern_3_integration_test(ui_engine, api_client, db_client, ui_url):
    """Complete UI → API → DB flow with AI validation"""
    
    # 1. UI Action
    ui_engine.navigate(f"{ui_url}/checkout")
    ui_engine.fill("#quantity", "2")
    ui_engine.click("#place-order")
    
    # 2. Capture API call
    response = api_client.get("/api/orders/recent")
    order = response.json()[0]
    
    # 3. AI suggests and executes validations
    results = suggest_and_validate(
        api_endpoint="/api/orders/submit",
        api_method="POST",
        api_request={},
        api_response=order,
        db_client=db_client,
        auto_execute=True
    )
    
    # 4. Assert all validations passed
    assert all(v['passed'] for v in results['validations_executed']), \
        "Some validations failed"
    
    print(f"✓ Complete flow validated: {len(results['validations_executed'])} checks")


# ========================================================================
# Pattern 4: Selective Execution by Priority
# ========================================================================

def pattern_4_selective_execution(api_client, db_client):
    """Execute only specific priority levels"""
    
    response = api_client.put("/api/inventory/adjust", json_data={
        "product_id": "PROD123",
        "quantity_change": 50
    })
    
    suggester = AIValidationSuggester()
    strategy = suggester.suggest_validations(
        api_endpoint="/api/inventory/adjust",
        api_method="PUT",
        api_request={"product_id": "PROD123"},
        api_response=response.json()
    )
    
    # Execute critical and high priority only
    for suggestion in strategy.suggestions:
        if suggestion.priority in ['critical', 'high']:
            query = suggester.apply_correlations(
                suggestion,
                strategy.correlation_context
            )
            
            result = db_client.execute_query(query)
            
            # Check expected result
            if 'row_count' in suggestion.expected_result:
                expected = suggestion.expected_result['row_count']
                actual = len(result)
                assert actual == expected, \
                    f"{suggestion.reason}: Expected {expected} rows, got {actual}"
            
            print(f"✓ [{suggestion.priority.upper()}] {suggestion.reason}")


# ========================================================================
# Pattern 5: Confidence Threshold Filtering
# ========================================================================

def pattern_5_confidence_filtering(api_client, db_client):
    """Execute only high-confidence suggestions"""
    
    response = api_client.post("/api/users/register", json_data={
        "email": "newuser@example.com",
        "username": "newuser"
    })
    
    suggester = AIValidationSuggester()
    strategy = suggester.suggest_validations(
        api_endpoint="/api/users/register",
        api_method="POST",
        api_request={},
        api_response=response.json()
    )
    
    # Execute only suggestions with confidence >= 90%
    high_confidence = [
        s for s in strategy.suggestions 
        if s.confidence >= 90
    ]
    
    print(f"Executing {len(high_confidence)} high-confidence validations")
    
    for suggestion in high_confidence:
        query = suggester.apply_correlations(
            suggestion,
            strategy.correlation_context
        )
        result = db_client.execute_query(query)
        print(f"✓ {suggestion.reason} (confidence: {suggestion.confidence}%)")


# ========================================================================
# Pattern 6: Fallback When AI Unavailable
# ========================================================================

def pattern_6_fallback_mode():
    """Test that fallback works when AI is disabled"""
    
    import os
    
    # Temporarily disable AI
    original_key = os.environ.get('OPENAI_API_KEY')
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    
    try:
        suggester = AIValidationSuggester()
        
        # Should still provide rule-based suggestions
        strategy = suggester.suggest_validations(
            api_endpoint="/api/test",
            api_method="POST",
            api_request={},
            api_response={"id": 123}
        )
        
        assert len(strategy.suggestions) > 0, "Should provide fallback suggestions"
        print(f"Fallback mode: {len(strategy.suggestions)} suggestions provided")
        print(f"Reasoning: {strategy.ai_reasoning}")
    
    finally:
        # Restore API key
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key


# ========================================================================
# Pattern 7: pytest Fixture Integration
# ========================================================================

import pytest

@pytest.fixture
def ai_validator(db_client):
    """Fixture for AI validation suggester"""
    return AIValidationSuggester()


@pytest.mark.api_validation
def test_with_ai_fixture(api_client, db_client, ai_validator):
    """Use AI validator as a pytest fixture"""
    
    response = api_client.post("/api/orders/submit", json_data={})
    
    strategy = ai_validator.suggest_validations(
        api_endpoint="/api/orders/submit",
        api_method="POST",
        api_request={},
        api_response=response.json()
    )
    
    # Execute and assert
    for suggestion in strategy.suggestions:
        if suggestion.priority == 'critical':
            query = ai_validator.apply_correlations(
                suggestion,
                strategy.correlation_context
            )
            result = db_client.execute_query(query)
            assert len(result) > 0, f"Failed: {suggestion.reason}"


# ========================================================================
# CONFIGURATION EXAMPLES
# ========================================================================

# Set OpenAI API key
# Windows PowerShell:
#   $env:OPENAI_API_KEY = "sk-your-key"
# Linux/Mac:
#   export OPENAI_API_KEY="sk-your-key"
# Or in .env file:
#   OPENAI_API_KEY=sk-your-key

# Use Azure OpenAI (if preferred):
#   OPENAI_API_TYPE=azure
#   AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com
#   AZURE_OPENAI_KEY=your-azure-key
#   AZURE_OPENAI_DEPLOYMENT=your-deployment-name

# ========================================================================
# COMMON SCENARIOS
# ========================================================================

"""
Scenario 1: Order Creation
- AI suggests: order record check, order items check, inventory decrement,
  order total validation, audit log entry

Scenario 2: Payment Processing
- AI suggests: payment record check, order status update, transaction log,
  customer balance update

Scenario 3: User Registration
- AI suggests: user record check, default role assignment, email verification,
  audit trail, profile creation

Scenario 4: Inventory Adjustment
- AI suggests: inventory quantity check, audit log, product availability update,
  warehouse sync

Scenario 5: Product Update
- AI suggests: product record update, search index refresh, cache invalidation,
  change history log
"""

# ========================================================================
# BEST PRACTICES
# ========================================================================

"""
1. REVIEW BEFORE AUTO-EXECUTE
   - Always review AI suggestions in development
   - Use auto_execute=False initially
   - Build confidence before enabling auto-execution

2. START WITH CRITICAL PRIORITY
   - Execute critical validations first
   - Add high/medium as needed
   - Low priority is optional

3. USE EXISTING MAPPINGS
   - Maintain api_db_mapping.yaml
   - AI learns from existing mappings
   - Better accuracy with more context

4. MONITOR CONFIDENCE SCORES
   - 90-100%: High confidence, safe to auto-execute
   - 80-89%: Review query before executing
   - 70-79%: Validate logic manually
   - <70%: Consider fallback or manual validation

5. COMBINE WITH MANUAL VALIDATIONS
   - AI suggestions supplement, not replace
   - Critical business rules should be explicit
   - Use AI for comprehensive coverage
"""

# ========================================================================
# TROUBLESHOOTING
# ========================================================================

"""
Issue: AI not providing suggestions
Solution:
  1. Check OPENAI_API_KEY is set
  2. Verify network connectivity
  3. Check OpenAI API quota
  4. Framework falls back to rule-based logic

Issue: Low confidence scores
Solution:
  1. Add more context to api_db_mapping.yaml
  2. Provide detailed API response structure
  3. Review AI reasoning in report

Issue: Incorrect query suggestions
Solution:
  1. Review and adjust manually
  2. Update api_db_mapping.yaml for better context
  3. Filter by confidence threshold
  4. Use as guidance, not absolute truth

Issue: Slow suggestion generation
Solution:
  1. AI queries take 2-5 seconds (normal)
  2. Cache strategies for repeated endpoints
  3. Use fallback mode for performance tests
"""
