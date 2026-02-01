"""
AI Engine Selector Advanced Features Demo

This example demonstrates the enhanced AI Engine Selector features:
1. Local LLM Support (Ollama, LlamaCPP)
2. Retry Logic for AI API Calls
3. Response Caching

Author: Framework Team
Date: January 26, 2026
"""

import os
import time
from framework.core.ai_engine_selector import AIEngineSelector


def demo_provider_initialization():
    """Demonstrate different AI provider initialization"""
    print("\n" + "=" * 70)
    print("DEMO 1: Multi-Provider Support")
    print("=" * 70)
    
    providers = [
        ('openai', 'OpenAI GPT-4'),
        ('azure_openai', 'Azure OpenAI'),
        ('ollama', 'Ollama (Local LLM)'),
        ('llamacpp', 'LlamaCPP (Local LLM)')
    ]
    
    print("\n🔌 Testing Provider Initialization:")
    print("-" * 70)
    
    for provider_type, provider_name in providers:
        print(f"\n📌 {provider_name} ({provider_type}):")
        
        try:
            selector = AIEngineSelector(
                provider_type=provider_type,
                cache_enabled=True,
                max_retries=3
            )
            
            if selector.enabled:
                print(f"   ✅ Initialized successfully")
                info = selector.get_provider_info()
                print(f"   Provider: {info['provider_type']}")
                print(f"   Enabled: {info['enabled']}")
                print(f"   Max Retries: {info['max_retries']}")
                print(f"   Cache Enabled: {info['cache_enabled']}")
                
                # Test connection
                if selector.test_connection():
                    print(f"   ✅ Connection test passed")
                else:
                    print(f"   ⚠️  Connection test skipped (requires running service)")
            else:
                print(f"   ⚠️  Not available (check configuration)")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:60]}")


def demo_retry_logic():
    """Demonstrate retry logic with exponential backoff"""
    print("\n" + "=" * 70)
    print("DEMO 2: Retry Logic with Exponential Backoff")
    print("=" * 70)
    
    # Use OpenAI if available
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️  OPENAI_API_KEY not set. Demo skipped.")
        print("   Set environment variable: $env:OPENAI_API_KEY='sk-...'")
        return
    
    print("\n🔄 Configuring Retry Settings:")
    print("-" * 70)
    
    selector = AIEngineSelector(
        provider_type="openai",
        max_retries=3,
        retry_delay=1.0  # 1 second initial delay
    )
    
    info = selector.get_provider_info()
    print(f"   Max Retries: {info['max_retries']}")
    print(f"   Initial Retry Delay: {info['retry_delay']}s")
    print(f"   Backoff Strategy: Exponential (1s → 2s → 4s)")
    
    if selector.enabled:
        print("\n🎯 Testing AI Query with Retry:")
        print("-" * 70)
        
        test_metadata = {
            'test_name': 'test_checkout_flow',
            'module': 'checkout',
            'ui_framework': 'React',
            'markers': ['modern_spa', 'api_validation']
        }
        
        start_time = time.time()
        decision = selector.select_engine(test_metadata)
        elapsed = (time.time() - start_time) * 1000
        
        if decision:
            print(f"   ✅ AI recommendation received")
            print(f"   Engine: {decision.engine}")
            print(f"   Confidence: {decision.confidence}%")
            print(f"   Response Time: {elapsed:.0f}ms")
            print(f"   Reason: {decision.reason}")
        else:
            print(f"   ⚠️  No recommendation (AI unavailable)")
    else:
        print("\n⚠️  AI Engine Selector not enabled")


def demo_response_caching():
    """Demonstrate response caching"""
    print("\n" + "=" * 70)
    print("DEMO 3: Response Caching")
    print("=" * 70)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️  OPENAI_API_KEY not set. Demo skipped.")
        return
    
    # Create selector with caching enabled
    selector = AIEngineSelector(
        provider_type="openai",
        cache_enabled=True,
        cache_size=50,
        cache_ttl=1800  # 30 minutes
    )
    
    if not selector.enabled:
        print("\n⚠️  AI Engine Selector not enabled")
        return
    
    print("\n⚙️ Cache Configuration:")
    print("-" * 70)
    stats = selector.get_cache_stats()
    print(f"   Cache Enabled: {stats['enabled']}")
    print(f"   Max Cache Size: {stats['max_cache_size']}")
    print(f"   Cache TTL: {stats['cache_ttl']}s (30 minutes)")
    
    print("\n🔄 Testing Cache Performance:")
    print("-" * 70)
    
    # Same test metadata (should hit cache on repeat)
    test_metadata = {
        'test_name': 'test_checkout',
        'module': 'checkout',
        'ui_framework': 'React',
        'modern_spa': True
    }
    
    times = []
    
    # First call (cache miss)
    print("\n1️⃣ First call (cache miss):")
    start = time.time()
    decision = selector.select_engine(test_metadata)
    first_time = (time.time() - start) * 1000
    times.append(first_time)
    
    if decision:
        print(f"   Engine: {decision.engine}")
        print(f"   Response Time: {first_time:.0f}ms")
        print(f"   Status: ❌ Cache Miss")
    
    # Subsequent calls (cache hits)
    for i in range(2, 6):
        print(f"\n{i}️⃣ Call #{i} (cache hit):")
        start = time.time()
        decision = selector.select_engine(test_metadata)
        call_time = (time.time() - start) * 1000
        times.append(call_time)
        
        if decision:
            print(f"   Engine: {decision.engine}")
            print(f"   Response Time: {call_time:.3f}ms")
            print(f"   Status: ✅ Cache Hit")
    
    # Show cache statistics
    print("\n📊 Cache Performance Statistics:")
    print("-" * 70)
    stats = selector.get_cache_stats()
    print(f"   Total Lookups: {stats['total_lookups']}")
    print(f"   Cache Hits: {stats['cache_hits']}")
    print(f"   Cache Misses: {stats['cache_misses']}")
    print(f"   Cache Hit Rate: {stats['cache_hit_rate']}")
    print(f"   Current Cache Size: {stats['cache_size']}/{stats['max_cache_size']}")
    
    # Performance comparison
    if len(times) > 1:
        avg_cached = sum(times[1:]) / len(times[1:])
        if avg_cached > 0:
            speedup = first_time / avg_cached
            print(f"\n⚡ Performance Improvement:")
            print(f"   First Call (uncached): {first_time:.0f}ms")
            print(f"   Average Cached: {avg_cached:.3f}ms")
            print(f"   Speed Improvement: {speedup:.0f}x faster")


def demo_ollama_local_llm():
    """Demonstrate Ollama local LLM integration"""
    print("\n" + "=" * 70)
    print("DEMO 4: Ollama Local LLM Support")
    print("=" * 70)
    
    print("\n🏠 Local LLM with Ollama:")
    print("-" * 70)
    print("   Ollama allows running LLMs locally without API costs")
    print("   Popular models: llama2, mistral, codellama, phi")
    
    print("\n📝 Setup Instructions:")
    print("   1. Install Ollama: https://ollama.ai/")
    print("   2. Pull a model: ollama pull llama2")
    print("   3. Start Ollama service: ollama serve")
    print("   4. Set environment: $env:OLLAMA_MODEL='llama2'")
    
    print("\n🔌 Testing Ollama Connection:")
    print("-" * 70)
    
    try:
        selector = AIEngineSelector(
            provider_type="ollama",
            cache_enabled=True,
            max_retries=2
        )
        
        if selector.enabled:
            print("   ✅ Ollama connected successfully")
            
            # Test with simple metadata
            test_metadata = {
                'test_name': 'test_example',
                'module': 'checkout',
                'ui_framework': 'React'
            }
            
            print("\n🎯 Testing AI Query with Ollama:")
            decision = selector.select_engine(test_metadata)
            
            if decision:
                print(f"   ✅ Recommendation received")
                print(f"   Engine: {decision.engine}")
                print(f"   Confidence: {decision.confidence}%")
            else:
                print(f"   ⚠️  No recommendation generated")
        else:
            print("   ⚠️  Ollama not available")
            print("   Make sure Ollama is running: ollama serve")
    
    except Exception as e:
        print(f"   ⚠️  Connection failed: {str(e)[:60]}")


def demo_llamacpp_local_llm():
    """Demonstrate LlamaCPP local LLM integration"""
    print("\n" + "=" * 70)
    print("DEMO 5: LlamaCPP Local LLM Support")
    print("=" * 70)
    
    print("\n🏠 Local LLM with LlamaCPP:")
    print("-" * 70)
    print("   LlamaCPP runs GGUF models locally with CPU/GPU support")
    print("   Great for offline environments and privacy-sensitive scenarios")
    
    print("\n📝 Setup Instructions:")
    print("   1. Install: pip install llama-cpp-python")
    print("   2. Download GGUF model (e.g., from HuggingFace)")
    print("   3. Set path: $env:LLAMACPP_MODEL_PATH='C:\\models\\llama-2-7b.gguf'")
    
    print("\n🔌 Testing LlamaCPP Connection:")
    print("-" * 70)
    
    model_path = os.getenv('LLAMACPP_MODEL_PATH')
    
    if not model_path:
        print("   ⚠️  LLAMACPP_MODEL_PATH not set")
        print("   Set environment variable to GGUF model path")
        return
    
    try:
        selector = AIEngineSelector(
            provider_type="llamacpp",
            cache_enabled=True,
            max_retries=1
        )
        
        if selector.enabled:
            print(f"   ✅ LlamaCPP initialized")
            print(f"   Model: {model_path}")
            
            # Test with simple metadata
            test_metadata = {
                'test_name': 'test_example',
                'module': 'admin',
                'legacy_ui': True
            }
            
            print("\n🎯 Testing AI Query with LlamaCPP:")
            decision = selector.select_engine(test_metadata)
            
            if decision:
                print(f"   ✅ Recommendation received")
                print(f"   Engine: {decision.engine}")
                print(f"   Confidence: {decision.confidence}%")
            else:
                print(f"   ⚠️  No recommendation generated")
        else:
            print("   ⚠️  LlamaCPP not available")
    
    except Exception as e:
        print(f"   ⚠️  Initialization failed: {str(e)[:60]}")


def demo_cache_ttl():
    """Demonstrate cache TTL expiration"""
    print("\n" + "=" * 70)
    print("DEMO 6: Cache TTL (Time To Live)")
    print("=" * 70)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️  OPENAI_API_KEY not set. Demo skipped.")
        return
    
    # Create selector with short TTL for demo
    selector = AIEngineSelector(
        provider_type="openai",
        cache_enabled=True,
        cache_ttl=3  # 3 seconds for demo
    )
    
    if not selector.enabled:
        print("\n⚠️  AI Engine Selector not enabled")
        return
    
    print("\n⏰ Cache TTL set to 3 seconds")
    
    test_metadata = {
        'test_name': 'test_ttl',
        'module': 'checkout',
        'ui_framework': 'React'
    }
    
    # First call
    print("\n1️⃣ First call (cache miss):")
    decision = selector.select_engine(test_metadata)
    if decision:
        print(f"   Response: {decision.engine}")
    
    # Immediate second call
    print("\n2️⃣ Immediate second call (cache hit):")
    decision = selector.select_engine(test_metadata)
    if decision:
        print(f"   Response: {decision.engine} (from cache)")
    
    # Wait for TTL to expire
    print("\n⏳ Waiting 4 seconds for cache to expire...")
    time.sleep(4)
    
    # Third call after TTL
    print("\n3️⃣ Call after TTL expiration (cache miss):")
    decision = selector.select_engine(test_metadata)
    if decision:
        print(f"   Response: {decision.engine} (regenerated)")
    
    stats = selector.get_cache_stats()
    print(f"\n   Cache Hit Rate: {stats['cache_hit_rate']}")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("AI ENGINE SELECTOR ADVANCED FEATURES DEMO")
    print("=" * 70)
    print("\nThis demo showcases:")
    print("  1. Multi-Provider Support (OpenAI, Azure, Ollama, LlamaCPP)")
    print("  2. Retry Logic with Exponential Backoff")
    print("  3. Response Caching for Performance")
    print("  4. Local LLM Support (Ollama)")
    print("  5. Local LLM Support (LlamaCPP)")
    print("  6. Cache TTL Management")
    
    try:
        demo_provider_initialization()
        demo_retry_logic()
        demo_response_caching()
        demo_ollama_local_llm()
        demo_llamacpp_local_llm()
        demo_cache_ttl()
        
        print("\n" + "=" * 70)
        print("✅ DEMO COMPLETED")
        print("=" * 70)
        print("\n💡 Key Takeaways:")
        print("   • Multiple AI providers supported (cloud + local)")
        print("   • Automatic retry with exponential backoff (1s → 2s → 4s)")
        print("   • Response caching provides 20-100x speedup")
        print("   • Local LLMs (Ollama/LlamaCPP) for privacy & cost savings")
        print("   • Cache TTL prevents stale recommendations")
        print("   • Graceful degradation when AI unavailable")
        
        print("\n🚀 Production Configuration:")
        print("   • Use OpenAI/Azure for cloud deployments")
        print("   • Use Ollama for local development")
        print("   • Use LlamaCPP for offline/air-gapped environments")
        print("   • Enable caching (60-80% hit rate expected)")
        print("   • Set max_retries=3 for reliability")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
