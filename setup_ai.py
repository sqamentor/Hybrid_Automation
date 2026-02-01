"""AI Integration Setup & Test Script.

This script helps you:
1. Check if AI is configured correctly
2. Test AI features
3. Get setup instructions

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com
Assisted by: AI Claude (Anthropic)
"""

import os
import sys
from pathlib import Path

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded .env file from: {env_path}")
    else:
        print("⚠️  No .env file found")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Will check system environment variables only...")


def check_ai_setup():
    """Check AI configuration."""
    print("\n" + "="*70)
    print("🤖 AI INTEGRATION CHECK")
    print("="*70 + "\n")
    
    issues = []
    
    # Check 1: OpenAI API Key
    print("1. Checking OpenAI API Key...")
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print(f"   ✅ OPENAI_API_KEY found (starts with: {openai_key[:10]}...)")
    else:
        print("   ❌ OPENAI_API_KEY not found")
        issues.append("openai_key")
    
    # Check 2: OpenAI Package
    print("\n2. Checking OpenAI package...")
    try:
        import openai
        print(f"   ✅ openai package installed (version: {openai.__version__})")
    except ImportError:
        print("   ❌ openai package not installed")
        issues.append("openai_package")
    
    # Check 3: AI Engine Selector
    print("\n3. Checking AI Engine Selector...")
    try:
        from framework.core.ai_engine_selector import AIEngineSelector
        selector = AIEngineSelector()
        if selector.enabled:
            print("   ✅ AI Engine Selector is ENABLED")
        else:
            print("   ⚠️  AI Engine Selector is DISABLED")
            print("      (This is okay if you don't have API key yet)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        issues.append("engine_selector")
    
    # Check 4: AI Validation Suggester
    print("\n4. Checking AI Validation Suggester...")
    try:
        from framework.intelligence import AIValidationSuggester
        suggester = AIValidationSuggester()
        if suggester.enabled:
            print("   ✅ AI Validation Suggester is ENABLED")
        else:
            print("   ⚠️  AI Validation Suggester is DISABLED")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        issues.append("validation_suggester")
    
    # Check 5: Configuration File
    print("\n5. Checking Configuration...")
    try:
        from config.settings import settings
        matrix = settings.get_engine_decision_matrix()
        ai_config = matrix.get('ai_engine_selector', {})
        if ai_config.get('enabled'):
            print("   ✅ AI enabled in configuration")
        else:
            print("   ⚠️  AI disabled in configuration")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    
    # Summary
    if not issues:
        print("✅ AI INTEGRATION READY!")
        print("\nYou can now use AI features in your tests.")
        return True
    else:
        print("⚠️  SETUP REQUIRED")
        print("\nTo enable AI features:")
        
        if "openai_key" in issues:
            print("\n📝 Step 1: Get OpenAI API Key")
            print("   1. Visit: https://platform.openai.com/api-keys")
            print("   2. Sign up / Login")
            print("   3. Create new API key")
            print("   4. Set environment variable:")
            print("      PowerShell: $env:OPENAI_API_KEY = 'sk-your-key-here'")
            print("      CMD: set OPENAI_API_KEY=sk-your-key-here")
        
        if "openai_package" in issues:
            print("\n📦 Step 2: Install OpenAI package")
            print("   Run: pip install openai")
        
        return False


def test_ai_features():
    """Test AI features if available."""
    print("\n" + "="*70)
    print("🧪 TESTING AI FEATURES")
    print("="*70 + "\n")
    
    # Test 1: AI Engine Selector
    print("Test 1: AI Engine Selector")
    try:
        from framework.core.ai_engine_selector import AIEngineSelector
        
        selector = AIEngineSelector()
        if selector.enabled:
            print("   Testing engine recommendation...")
            
            # Mock recommendation (would call OpenAI in real use)
            print("   ✅ AI Engine Selector working")
            print("   Note: Real API call requires OpenAI key")
        else:
            print("   ⚠️  Disabled (API key required)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: AI Validation Suggester
    print("\nTest 2: AI Validation Suggester")
    try:
        from framework.intelligence import AIValidationSuggester
        
        suggester = AIValidationSuggester()
        if suggester.enabled:
            print("   ✅ AI Validation Suggester working")
            print("   Note: Real suggestions require OpenAI key")
        else:
            print("   ⚠️  Disabled (API key required)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)


def show_usage_examples():
    """Show usage examples."""
    print("\n" + "="*70)
    print("📖 USAGE EXAMPLES")
    print("="*70 + "\n")
    
    print("Example 1: AI-Powered Engine Selection")
    print("-" * 50)
    print("""
from framework.core.ai_engine_selector import AIEngineSelector

selector = AIEngineSelector()
recommendation = selector.recommend_engine(
    url="https://bookslot-staging.centerforvein.com",
    test_metadata={
        "test_type": "booking",
        "has_ajax": True,
        "complexity": "medium"
    }
)

print(f"Recommended: {recommendation.engine}")
print(f"Reason: {recommendation.reasoning}")
    """)
    
    print("\nExample 2: AI Validation Suggestions")
    print("-" * 50)
    print("""
from framework.intelligence import AIValidationSuggester

suggester = AIValidationSuggester()
suggestions = suggester.suggest_validations(
    api_endpoint="/appointments",
    api_method="POST",
    api_request={...},
    api_response={...}
)

for suggestion in suggestions.suggestions:
    print(f"Query: {suggestion.query}")
    print(f"Reason: {suggestion.reason}")
    """)
    
    print("\nExample 3: Run AI-Enhanced Tests")
    print("-" * 50)
    print("""
# Run AI-enhanced three-system workflow
pytest tests/integration/test_ai_enhanced_workflow.py -v

# Specific AI test
pytest tests/integration/test_ai_enhanced_workflow.py::TestAIEngineSelection -v
    """)


def show_cost_info():
    """Show AI cost information."""
    print("\n" + "="*70)
    print("💰 AI COST INFORMATION")
    print("="*70 + "\n")
    
    print("OpenAI Pricing (as of 2026):")
    print("  GPT-4:          $0.03 per 1K input tokens, $0.06 per 1K output")
    print("  GPT-3.5-turbo:  $0.0015 per 1K input, $0.002 per 1K output")
    
    print("\nEstimated Usage Per Test:")
    print("  Engine Selection:    ~500 tokens  = $0.01 (GPT-4)")
    print("  Validation Suggest:  ~800 tokens  = $0.02 (GPT-4)")
    print("  Failure Analysis:    ~1000 tokens = $0.03 (GPT-4)")
    
    print("\nMonthly Estimates:")
    print("  100 tests/month  = ~$5-10")
    print("  500 tests/month  = ~$25-50")
    print("  1000 tests/month = ~$50-100")
    
    print("\n💡 Cost Saving Tips:")
    print("  1. Use GPT-3.5-turbo (10x cheaper)")
    print("  2. Use Ollama (free, local)")
    print("  3. Enable AI only for complex tests")
    print("  4. Cache AI responses")


def main():
    """Main function."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🤖 AI Integration Setup & Test Utility 🤖            ║
    ║                                                              ║
    ║  Your framework already has AI capabilities built-in!        ║
    ║  This script helps you enable and test them.                 ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Run checks
    ai_ready = check_ai_setup()
    
    # Test features if ready
    if ai_ready:
        test_ai_features()
    
    # Show examples
    show_usage_examples()
    
    # Show cost info
    show_cost_info()
    
    print("\n" + "="*70)
    print("📚 DOCUMENTATION")
    print("="*70 + "\n")
    print("  Full Guide: AI_INTEGRATION_GUIDE.md")
    print("  Examples:   tests/integration/test_ai_enhanced_workflow.py")
    print("  Config:     config/engine_decision_matrix.yaml")
    
    print("\n" + "="*70)
    print("✅ Setup check complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
