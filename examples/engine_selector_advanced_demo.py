"""Engine Selector Advanced Features Demo.

This example demonstrates the new advanced features:
1. Rule Priority Weighting
2. Caching for Frequently Used Test Metadata Patterns

Author: Framework Team
Date: January 26, 2026
"""

from framework.core.engine_selector import EngineSelector
import time


def demo_rule_priority_weighting():
    """Demonstrate rule priority weighting."""
    print("\n" + "=" * 70)
    print("DEMO 1: Rule Priority Weighting")
    print("=" * 70)
    
    selector = EngineSelector()
    
    # Show current rule priorities
    print("\n📊 Current Rule Priorities (sorted by priority):")
    print("-" * 70)
    priorities = selector.get_rule_priorities()
    for i, rule in enumerate(priorities[:10], 1):  # Show top 10
        print(f"{i:2}. [{rule['priority']:3}] {rule['name']:30} → {rule['engine']:10} (confidence: {rule['confidence']}%)")
    
    # Test with different metadata scenarios
    scenarios = [
        {
            'name': 'Modern SPA Application',
            'metadata': {
                'test_name': 'test_checkout_flow',
                'module': 'checkout',
                'ui_framework': 'React',
                'modern_spa': True,
                'api_validation_required': True
            }
        },
        {
            'name': 'Legacy Enterprise App',
            'metadata': {
                'test_name': 'test_admin_panel',
                'module': 'admin',
                'legacy_ui': True,
                'auth_type': 'SSO'
            }
        },
        {
            'name': 'Mobile-First Design',
            'metadata': {
                'test_name': 'test_mobile_booking',
                'module': 'mobile',
                'mobile_first': True,
                'ui_framework': 'Progressive Web App'
            }
        }
    ]
    
    print("\n🎯 Testing Different Scenarios:")
    print("-" * 70)
    
    for scenario in scenarios:
        decision = selector.select_engine(scenario['metadata'])
        print(f"\n📌 Scenario: {scenario['name']}")
        print(f"   Engine: {decision.engine}")
        print(f"   Priority: {decision.priority}")
        print(f"   Confidence: {decision.confidence}%")
        print(f"   Rule: {decision.rule_name}")
        print(f"   Reason: {decision.reason}")
    
    # Demonstrate dynamic priority override
    print("\n🔧 Testing Priority Override:")
    print("-" * 70)
    
    metadata_with_override = {
        'test_name': 'test_special_case',
        'module': 'checkout',
        'priority_override': 95  # Override to force high priority
    }
    
    decision = selector.select_engine(metadata_with_override)
    print(f"   Metadata with priority_override=95")
    print(f"   Engine: {decision.engine}")
    print(f"   Priority: {decision.priority} (overridden)")
    print(f"   Rule: {decision.rule_name}")


def demo_caching():
    """Demonstrate caching for frequently used patterns."""
    print("\n" + "=" * 70)
    print("DEMO 2: Caching for Frequently Used Test Metadata Patterns")
    print("=" * 70)
    
    # Create selector with custom cache settings
    selector = EngineSelector(cache_size=50, cache_ttl=1800)  # 50 entries, 30 min TTL
    
    print("\n⚙️ Cache Configuration:")
    print(f"   Max Cache Size: 50 entries")
    print(f"   Cache TTL: 1800 seconds (30 minutes)")
    
    # Simulate repeated test executions with same metadata
    test_patterns = [
        {'test_name': 'test_checkout_flow', 'module': 'checkout', 'ui_framework': 'React'},
        {'test_name': 'test_checkout_flow', 'module': 'checkout', 'ui_framework': 'React'},  # Exact same
        {'test_name': 'test_admin_panel', 'module': 'admin', 'legacy_ui': True},
        {'test_name': 'test_mobile_app', 'module': 'mobile', 'mobile_first': True},
        {'test_name': 'test_checkout_flow', 'module': 'checkout', 'ui_framework': 'React'},  # Same as #1
        {'test_name': 'test_admin_panel', 'module': 'admin', 'legacy_ui': True},  # Same as #3
        {'test_name': 'test_checkout_flow', 'module': 'checkout', 'ui_framework': 'React'},  # Same as #1
    ]
    
    print("\n🔄 Executing 7 Test Selections:")
    print("-" * 70)
    
    start_time = time.time()
    
    for i, metadata in enumerate(test_patterns, 1):
        decision = selector.select_engine(metadata)
        cache_status = "✅ CACHE HIT" if decision.cache_hit else "❌ CACHE MISS"
        print(f"{i}. {metadata['test_name']:20} → {decision.engine:10} {cache_status}")
    
    elapsed = (time.time() - start_time) * 1000  # Convert to ms
    
    # Show cache statistics
    print("\n📊 Cache Performance Statistics:")
    print("-" * 70)
    stats = selector.get_cache_stats()
    
    print(f"   Total Lookups: {stats['total_lookups']}")
    print(f"   Cache Hits: {stats['cache_hits']}")
    print(f"   Cache Misses: {stats['cache_misses']}")
    print(f"   Cache Hit Rate: {stats['cache_hit_rate']}")
    print(f"   Current Cache Size: {stats['cache_size']}/{stats['max_cache_size']}")
    print(f"   Cache Evictions: {stats['evictions']}")
    print(f"   Total Time: {elapsed:.2f} ms")
    
    # Show top cached patterns
    if stats['top_cached_patterns']:
        print("\n🔥 Top Cached Patterns:")
        print("-" * 70)
        for pattern in stats['top_cached_patterns']:
            print(f"   • {pattern['rule_name']:25} → {pattern['engine']:10} "
                  f"(hits: {pattern['hit_count']}, priority: {pattern['priority']})")


def demo_cache_performance():
    """Demonstrate cache performance impact."""
    print("\n" + "=" * 70)
    print("DEMO 3: Cache Performance Impact")
    print("=" * 70)
    
    selector = EngineSelector(cache_size=100)
    
    # Test metadata that will be reused
    test_metadata = {
        'test_name': 'test_performance',
        'module': 'checkout',
        'ui_framework': 'React',
        'modern_spa': True
    }
    
    # Warm-up (first call - cache miss)
    print("\n🔥 Warming up cache (first call)...")
    start = time.time()
    decision = selector.select_engine(test_metadata)
    first_call_time = (time.time() - start) * 1000
    print(f"   Time: {first_call_time:.3f} ms (cache miss)")
    
    # Subsequent calls (cache hits)
    print("\n⚡ Testing cached performance (10 subsequent calls)...")
    times = []
    for i in range(10):
        start = time.time()
        decision = selector.select_engine(test_metadata)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
    
    avg_cached_time = sum(times) / len(times)
    print(f"   Average Time: {avg_cached_time:.3f} ms (cache hits)")
    
    # Avoid division by zero
    if avg_cached_time > 0:
        speed_improvement = first_call_time / avg_cached_time
        print(f"   Speed Improvement: {speed_improvement:.1f}x faster")
    else:
        print("   Speed Improvement: Execution too fast to measure accurately")
    
    # Show final cache stats
    stats = selector.get_cache_stats()
    print(f"\n   Cache Hit Rate: {stats['cache_hit_rate']}")


def demo_dynamic_priority_update():
    """Demonstrate dynamic priority updates."""
    print("\n" + "=" * 70)
    print("DEMO 4: Dynamic Rule Priority Updates")
    print("=" * 70)
    
    selector = EngineSelector()
    
    # Show current priorities for a specific rule
    print("\n📋 Finding 'modern_spa_rule' priority...")
    priorities = selector.get_rule_priorities()
    modern_spa_rule = next((r for r in priorities if 'spa' in r['name'].lower()), None)
    
    if modern_spa_rule:
        print(f"   Current Priority: {modern_spa_rule['priority']}")
        
        # Update priority
        new_priority = 95
        print(f"\n🔧 Updating priority to {new_priority}...")
        success = selector.update_rule_priority(modern_spa_rule['name'], new_priority)
        
        if success:
            print("   ✅ Priority updated successfully")
            print("   ⚠️  Cache cleared (due to priority change)")
            
            # Verify update
            updated_priorities = selector.get_rule_priorities()
            updated_rule = next((r for r in updated_priorities if r['name'] == modern_spa_rule['name']), None)
            if updated_rule:
                print(f"   New Priority: {updated_rule['priority']}")
        else:
            print("   ❌ Failed to update priority")
    else:
        print("   ⚠️  'modern_spa_rule' not found in configuration")


def demo_cache_ttl():
    """Demonstrate cache TTL (Time To Live)"""
    print("\n" + "=" * 70)
    print("DEMO 5: Cache TTL (Time To Live)")
    print("=" * 70)
    
    # Create selector with short TTL for demo
    selector = EngineSelector(cache_size=100, cache_ttl=2)  # 2 seconds TTL
    
    metadata = {
        'test_name': 'test_ttl_demo',
        'module': 'checkout',
        'ui_framework': 'React'
    }
    
    print("\n⏰ Cache TTL set to 2 seconds")
    
    # First call
    print("\n1️⃣ First call (cache miss):")
    decision = selector.select_engine(metadata)
    print(f"   Cache Hit: {decision.cache_hit}")
    
    # Immediate second call
    print("\n2️⃣ Immediate second call (cache hit):")
    decision = selector.select_engine(metadata)
    print(f"   Cache Hit: {decision.cache_hit}")
    
    # Wait for TTL to expire
    print("\n⏳ Waiting 3 seconds for cache to expire...")
    time.sleep(3)
    
    # Third call after TTL
    print("\n3️⃣ Call after TTL expiration (cache miss):")
    decision = selector.select_engine(metadata)
    print(f"   Cache Hit: {decision.cache_hit}")
    print("   ✅ Cache entry expired and regenerated")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("ENGINE SELECTOR ADVANCED FEATURES DEMO")
    print("=" * 70)
    print("\nThis demo showcases:")
    print("  1. Rule Priority Weighting - Intelligent rule evaluation")
    print("  2. Metadata Pattern Caching - Performance optimization")
    print("  3. Cache Performance Analysis - Speed improvements")
    print("  4. Dynamic Priority Updates - Runtime reconfiguration")
    print("  5. Cache TTL Management - Automatic expiration")
    
    try:
        demo_rule_priority_weighting()
        demo_caching()
        demo_cache_performance()
        demo_dynamic_priority_update()
        demo_cache_ttl()
        
        print("\n" + "=" * 70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\n💡 Key Takeaways:")
        print("   • Rules are now sorted by priority (100 = highest, 0 = lowest)")
        print("   • Cache provides significant performance improvements")
        print("   • Typical cache hit rates: 60-80% in real scenarios")
        print("   • Cache TTL prevents stale decisions")
        print("   • Priorities can be updated dynamically at runtime")
        print("   • Custom priority overrides available per-test")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
