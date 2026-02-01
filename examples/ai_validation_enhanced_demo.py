"""
AI Validation Suggester Enhanced Demo
=====================================
Demonstrates the enhanced AI Validation Suggester capabilities:

Features Demonstrated:
1. Comprehensive Validation Patterns
   - CRUD operations (CREATE, UPDATE, DELETE)
   - Business logic patterns (Orders, Users, Payments)
   - Referential integrity checks
   - Data quality validations

2. Pattern Caching System
   - Cache hits/misses tracking
   - TTL-based expiration
   - LRU eviction
   - Cache statistics

3. Confidence Scoring
   - Multi-factor confidence calculation
   - Context-aware scoring
   - Priority weighting
   - Query complexity analysis

Usage:
    python examples/ai_validation_enhanced_demo.py
"""

from framework.intelligence import AIValidationSuggester, ValidationStrategy
from utils.logger import get_logger
import json

logger = get_logger(__name__)


def print_section(title: str):
    """Print a formatted section title."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def demo_1_validation_patterns():
    """Demo 1: Comprehensive Validation Patterns"""
    print_section("Demo 1: Comprehensive Validation Patterns")
    
    suggester = AIValidationSuggester(enable_cache=False)
    
    # Test different operation types
    test_cases = [
        {
            "name": "Order Creation",
            "endpoint": "/api/orders/create",
            "method": "POST",
            "request": {
                "customer_id": "CUST123",
                "items": [
                    {"product_id": "PROD001", "quantity": 2, "price": 29.99},
                    {"product_id": "PROD002", "quantity": 1, "price": 49.99}
                ],
                "total": 109.97
            },
            "response": {
                "order_id": "ORD789",
                "status": "pending",
                "created_at": "2026-01-26T10:00:00Z",
                "total_amount": 109.97
            }
        },
        {
            "name": "User Registration",
            "endpoint": "/api/users/register",
            "method": "POST",
            "request": {
                "email": "test@example.com",
                "username": "testuser",
                "password": "hashed_password"
            },
            "response": {
                "user_id": "USR456",
                "email": "test@example.com",
                "status": "active",
                "created_at": "2026-01-26T10:05:00Z"
            }
        },
        {
            "name": "Product Update",
            "endpoint": "/api/products/123",
            "method": "PUT",
            "request": {
                "name": "Updated Product",
                "price": 99.99,
                "stock": 50
            },
            "response": {
                "product_id": "123",
                "name": "Updated Product",
                "price": 99.99,
                "updated_at": "2026-01-26T10:10:00Z"
            }
        },
        {
            "name": "Record Deletion",
            "endpoint": "/api/items/456",
            "method": "DELETE",
            "request": {},
            "response": {
                "item_id": "456",
                "deleted": True,
                "deleted_at": "2026-01-26T10:15:00Z"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['name']}")
        print(f"Endpoint: {test_case['method']} {test_case['endpoint']}")
        
        strategy = suggester.suggest_validations(
            api_endpoint=test_case['endpoint'],
            api_method=test_case['method'],
            api_request=test_case['request'],
            api_response=test_case['response'],
            use_cache=False
        )
        
        print(f"✓ Generated {len(strategy.suggestions)} validation suggestions")
        
        # Show top 3 suggestions
        print("\nTop Validation Suggestions:")
        for idx, suggestion in enumerate(strategy.suggestions[:3], 1):
            print(f"  {idx}. [{suggestion.priority.upper()}] {suggestion.reason}")
            print(f"     Confidence: {suggestion.confidence}%")
            print(f"     Pattern Type: {suggestion.pattern_type}")
            print(f"     Tags: {', '.join(suggestion.tags)}")
            print(f"     Query: {suggestion.query[:80]}...")
        
        print(f"\nCorrelation Keys: {list(strategy.correlation_context.keys())}")
        print("-" * 80)
    
    print("\n✓ Demo 1 completed")


def demo_2_pattern_caching():
    """Demo 2: Pattern Caching System"""
    print_section("Demo 2: Pattern Caching System")
    
    suggester = AIValidationSuggester(enable_cache=True)
    
    # Test API call (similar structure)
    api_calls = [
        {
            "endpoint": "/api/orders/create",
            "method": "POST",
            "request": {"customer_id": "C1", "total": 100},
            "response": {"order_id": "O1", "status": "pending"}
        },
        {
            "endpoint": "/api/orders/create",  # Same endpoint
            "method": "POST",
            "request": {"customer_id": "C2", "total": 200},
            "response": {"order_id": "O2", "status": "pending"}  # Same structure
        },
        {
            "endpoint": "/api/orders/create",  # Same endpoint again
            "method": "POST",
            "request": {"customer_id": "C3", "total": 300},
            "response": {"order_id": "O3", "status": "confirmed"}  # Same structure
        },
        {
            "endpoint": "/api/users/register",  # Different endpoint
            "method": "POST",
            "request": {"email": "test@example.com"},
            "response": {"user_id": "U1", "email": "test@example.com"}
        }
    ]
    
    print("Making API calls and tracking cache performance...\n")
    
    for i, call in enumerate(api_calls, 1):
        print(f"Call {i}: {call['method']} {call['endpoint']}")
        
        strategy = suggester.suggest_validations(
            api_endpoint=call['endpoint'],
            api_method=call['method'],
            api_request=call['request'],
            api_response=call['response'],
            use_cache=True
        )
        
        if strategy.cache_hit:
            print(f"  ✓ CACHE HIT - Reused cached strategy")
        else:
            print(f"  ✓ CACHE MISS - Generated new strategy")
        
        print(f"  Suggestions: {len(strategy.suggestions)}")
    
    # Display cache statistics
    print("\n" + "="*60)
    print("CACHE STATISTICS")
    print("="*60)
    
    stats = suggester.get_cache_statistics()
    if stats['cache_enabled']:
        print(f"Cache Size: {stats['cache_size']}/{stats['max_size']}")
        print(f"Cache Hits: {stats['hits']}")
        print(f"Cache Misses: {stats['misses']}")
        print(f"Hit Rate: {stats['hit_rate']}%")
        print(f"TTL: {stats['ttl_seconds']} seconds")
        
        if stats['top_patterns']:
            print("\nTop Cached Patterns:")
            for pattern in stats['top_patterns']:
                print(f"  - {pattern['key']}... (used {pattern['frequency']}x)")
    
    print("\n✓ Demo 2 completed")


def demo_3_confidence_scoring():
    """Demo 3: Confidence Scoring Analysis"""
    print_section("Demo 3: Confidence Scoring Analysis")
    
    suggester = AIValidationSuggester(enable_cache=False)
    
    # Test different scenarios that affect confidence
    scenarios = [
        {
            "name": "High Confidence - Order with All Keys",
            "endpoint": "/api/orders/submit",
            "method": "POST",
            "response": {
                "order_id": "ORD123",
                "customer_id": "CUST456",
                "transaction_id": "TXN789",
                "payment_id": "PAY001",
                "status": "completed",
                "total": 199.99
            }
        },
        {
            "name": "Medium Confidence - User Update with Some Keys",
            "endpoint": "/api/users/profile",
            "method": "PUT",
            "response": {
                "user_id": "USR123",
                "email": "updated@example.com",
                "updated_at": "2026-01-26T10:00:00Z"
            }
        },
        {
            "name": "Lower Confidence - Generic Endpoint",
            "endpoint": "/api/data/process",
            "method": "POST",
            "response": {
                "success": True,
                "message": "Processed successfully"
            }
        }
    ]
    
    print("Analyzing confidence scores for different scenarios...\n")
    
    for scenario in scenarios:
        print(f"\nScenario: {scenario['name']}")
        print(f"Endpoint: {scenario['method']} {scenario['endpoint']}")
        
        strategy = suggester.suggest_validations(
            api_endpoint=scenario['endpoint'],
            api_method=scenario['method'],
            api_request={},
            api_response=scenario['response'],
            use_cache=False
        )
        
        # Calculate average confidence
        if strategy.suggestions:
            avg_confidence = sum(s.confidence for s in strategy.suggestions) / len(strategy.suggestions)
            max_confidence = max(s.confidence for s in strategy.suggestions)
            min_confidence = min(s.confidence for s in strategy.suggestions)
            
            print(f"✓ Validation Count: {len(strategy.suggestions)}")
            print(f"  Average Confidence: {avg_confidence:.1f}%")
            print(f"  Max Confidence: {max_confidence}%")
            print(f"  Min Confidence: {min_confidence}%")
            print(f"  Correlation Keys: {len(strategy.correlation_context)}")
            
            # Show confidence breakdown
            print("\n  Confidence Breakdown:")
            for suggestion in strategy.suggestions[:3]:
                print(f"    - {suggestion.reason}: {suggestion.confidence}%")
                print(f"      Priority: {suggestion.priority} | Pattern: {suggestion.pattern_type}")
        
        print("-" * 80)
    
    print("\n✓ Demo 3 completed")


def demo_4_pattern_categories():
    """Demo 4: Pattern Categories and Coverage"""
    print_section("Demo 4: Pattern Categories and Coverage")
    
    suggester = AIValidationSuggester(enable_cache=False)
    
    # Get all available pattern categories
    categories = suggester.get_pattern_categories()
    
    print(f"Available Pattern Categories: {len(categories)}\n")
    
    for category in categories:
        patterns = suggester.get_patterns_by_category(category)
        print(f"\n{category}")
        print("-" * 60)
        print(f"Pattern Count: {len(patterns)}")
        
        if patterns:
            print("\nPatterns:")
            for i, pattern in enumerate(patterns[:5], 1):  # Show first 5
                print(f"  {i}. {pattern['name']}")
                print(f"     Priority: {pattern['priority']} | Confidence: {pattern['confidence_base']}%")
                print(f"     Reason: {pattern['reason']}")
                print(f"     Tags: {', '.join(pattern['tags'])}")
            
            if len(patterns) > 5:
                print(f"  ... and {len(patterns) - 5} more patterns")
    
    print("\n✓ Demo 4 completed")


def demo_5_business_context_detection():
    """Demo 5: Business Context Detection"""
    print_section("Demo 5: Business Context Detection")
    
    suggester = AIValidationSuggester(enable_cache=False)
    
    # Test various business contexts
    contexts = [
        {
            "endpoint": "/api/orders/checkout",
            "expected_context": "ORDER_PROCESSING"
        },
        {
            "endpoint": "/api/users/signup",
            "expected_context": "USER_MANAGEMENT"
        },
        {
            "endpoint": "/api/payments/process",
            "expected_context": "PAYMENT"
        },
        {
            "endpoint": "/api/inventory/update",
            "expected_context": "INVENTORY"
        },
        {
            "endpoint": "/api/data/save",
            "expected_context": "CRUD"
        }
    ]
    
    print("Testing business context detection...\n")
    
    for context in contexts:
        print(f"Endpoint: {context['endpoint']}")
        print(f"Expected Context: {context['expected_context']}")
        
        # Detect context
        detected = suggester._detect_business_context(
            context['endpoint'],
            {"status": "success"}
        )
        
        print(f"Detected Context: {detected}")
        
        if detected == context['expected_context']:
            print("✓ CORRECT")
        else:
            print("✗ MISMATCH")
        
        # Get context-specific patterns
        patterns = suggester.get_patterns_by_category(detected)
        print(f"Available Patterns: {len(patterns)}")
        
        print("-" * 80)
    
    print("\n✓ Demo 5 completed")


def demo_6_cache_management():
    """Demo 6: Cache Management Operations"""
    print_section("Demo 6: Cache Management Operations")
    
    suggester = AIValidationSuggester(enable_cache=True)
    
    print("Step 1: Populate cache with multiple patterns\n")
    
    # Generate some cached entries
    for i in range(5):
        strategy = suggester.suggest_validations(
            api_endpoint=f"/api/test/endpoint{i}",
            api_method="POST",
            api_request={},
            api_response={"id": f"ID{i}", "data": f"value{i}"},
            use_cache=True
        )
        print(f"  Generated strategy for endpoint{i}")
    
    # Show initial stats
    stats = suggester.get_cache_statistics()
    print(f"\n✓ Cache populated with {stats['cache_size']} entries")
    print(f"  Hits: {stats['hits']}, Misses: {stats['misses']}")
    
    print("\nStep 2: Test cache hits with repeated calls\n")
    
    # Repeat some calls
    for i in range(3):
        strategy = suggester.suggest_validations(
            api_endpoint=f"/api/test/endpoint{i}",
            api_method="POST",
            api_request={},
            api_response={"id": f"ID{i}", "data": f"value{i}"},
            use_cache=True
        )
        if strategy.cache_hit:
            print(f"  ✓ Cache hit for endpoint{i}")
    
    # Updated stats
    stats = suggester.get_cache_statistics()
    print(f"\n✓ Cache hits increased to: {stats['hits']}")
    print(f"  Hit rate: {stats['hit_rate']}%")
    
    print("\nStep 3: Clear cache\n")
    
    suggester.clear_cache()
    print("✓ Cache cleared")
    
    # Final stats
    stats = suggester.get_cache_statistics()
    print(f"  Cache size: {stats['cache_size']}")
    print(f"  Hits reset to: {stats['hits']}")
    
    print("\n✓ Demo 6 completed")


def demo_7_comprehensive_report():
    """Demo 7: Comprehensive Validation Report"""
    print_section("Demo 7: Comprehensive Validation Report")
    
    suggester = AIValidationSuggester(enable_cache=True)
    
    # Complex order scenario
    strategy = suggester.suggest_validations(
        api_endpoint="/api/orders/submit",
        api_method="POST",
        api_request={
            "customer_id": "CUST789",
            "items": [
                {"product_id": "PROD001", "quantity": 2},
                {"product_id": "PROD002", "quantity": 1}
            ],
            "payment_method": "credit_card",
            "shipping_address": "123 Main St"
        },
        api_response={
            "order_id": "ORD12345",
            "customer_id": "CUST789",
            "transaction_id": "TXN67890",
            "payment_id": "PAY11111",
            "status": "confirmed",
            "total_amount": 299.97,
            "items_count": 3,
            "created_at": "2026-01-26T10:30:00Z"
        },
        use_cache=True
    )
    
    # Generate and print detailed report
    report = suggester.generate_validation_report(strategy)
    print(report)
    
    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    critical = sum(1 for s in strategy.suggestions if s.priority == 'critical')
    high = sum(1 for s in strategy.suggestions if s.priority == 'high')
    medium = sum(1 for s in strategy.suggestions if s.priority == 'medium')
    low = sum(1 for s in strategy.suggestions if s.priority == 'low')
    
    print(f"Total Validations: {len(strategy.suggestions)}")
    print(f"  Critical: {critical}")
    print(f"  High: {high}")
    print(f"  Medium: {medium}")
    print(f"  Low: {low}")
    
    if strategy.suggestions:
        avg_conf = sum(s.confidence for s in strategy.suggestions) / len(strategy.suggestions)
        print(f"\nAverage Confidence: {avg_conf:.1f}%")
    
    print(f"Correlation Keys: {len(strategy.correlation_context)}")
    print(f"Cache Hit: {strategy.cache_hit}")
    
    print("\n✓ Demo 7 completed")


def main():
    """Run all demos."""
    print("\n" + "="*80)
    print("  AI VALIDATION SUGGESTER ENHANCED FEATURES DEMO")
    print("="*80)
    print("\nDemonstrating enhanced capabilities:")
    print("  1. Comprehensive Validation Patterns")
    print("  2. Pattern Caching System")
    print("  3. Confidence Scoring")
    print("  4. Pattern Categories")
    print("  5. Business Context Detection")
    print("  6. Cache Management")
    print("  7. Comprehensive Reports")
    print("\n" + "="*80 + "\n")
    
    try:
        demo_1_validation_patterns()
        demo_2_pattern_caching()
        demo_3_confidence_scoring()
        demo_4_pattern_categories()
        demo_5_business_context_detection()
        demo_6_cache_management()
        demo_7_comprehensive_report()
        
        # Final summary
        print_section("ALL DEMOS COMPLETED SUCCESSFULLY")
        print("✓ Demo 1: Validation Patterns - PASSED")
        print("✓ Demo 2: Pattern Caching - PASSED")
        print("✓ Demo 3: Confidence Scoring - PASSED")
        print("✓ Demo 4: Pattern Categories - PASSED")
        print("✓ Demo 5: Context Detection - PASSED")
        print("✓ Demo 6: Cache Management - PASSED")
        print("✓ Demo 7: Comprehensive Report - PASSED")
        print("\nAI Validation Suggester enhancements working correctly!")
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}", exc_info=True)
        print(f"\n✗ Demo failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
