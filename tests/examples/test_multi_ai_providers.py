"""
Example: Multi-AI Provider Usage in Tests

Demonstrates how to use different AI providers (OpenAI, Claude, Azure, Ollama)
for various AI-powered features in the framework.
"""

import pytest

from framework.ai.ai_provider_factory import ai_factory, get_ai_provider
from framework.ai.nl_test_generator import NaturalLanguageTestGenerator
from framework.intelligence import AIValidationSuggester

# ============================================================================
# EXAMPLE 1: Use Default AI Provider
# ============================================================================


def test_default_ai_provider(api_client, db_client):
    """
    Uses default provider from config (usually OpenAI)

    To run: pytest tests/examples/test_multi_ai_providers.py::test_default_ai_provider -v -s
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Using Default AI Provider")
    print("=" * 80)

    # Make API call
    response = api_client.post(
        "/api/orders",
        json={"customer_id": 123, "items": [{"product_id": 456, "quantity": 2, "price": 99.99}]},
    )

    # AI suggests database validations (uses default provider)
    suggester = AIValidationSuggester()

    print(f"\nAI Provider: {suggester.ai_provider.get_provider_name()}")

    strategy = suggester.suggest_validations(
        api_endpoint="/api/orders",
        api_method="POST",
        api_request={"customer_id": 123},
        api_response=response.json(),
    )

    print(suggester.generate_validation_report(strategy))


# ============================================================================
# EXAMPLE 2: Use OpenAI Specifically (ChatGPT / GPT-4)
# ============================================================================


def test_use_openai_provider():
    """
    Explicitly use OpenAI (ChatGPT / GPT-4)

    Best for: General purpose, high quality
    To run: pytest tests/examples/test_multi_ai_providers.py::test_use_openai_provider -v -s
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Using OpenAI Provider (ChatGPT / GPT-4)")
    print("=" * 80)

    # Use OpenAI for validation suggestions
    suggester = AIValidationSuggester(provider_name="openai")

    print(f"\nProvider: {suggester.ai_provider.get_provider_name()}")
    print(f"Model: {suggester.ai_provider.config.model}")

    # Generate validation report
    mock_response = {
        "order_id": "ORD-12345",
        "customer_id": 123,
        "total": 199.98,
        "status": "PENDING",
    }

    strategy = suggester.suggest_validations(
        api_endpoint="/api/orders", api_method="POST", api_request={}, api_response=mock_response
    )

    print(f"\nSuggested {len(strategy.suggestions)} validations:")
    for i, suggestion in enumerate(strategy.suggestions, 1):
        print(f"{i}. [{suggestion.priority.upper()}] {suggestion.reason}")


# ============================================================================
# EXAMPLE 3: Use Claude (Anthropic)
# ============================================================================


def test_use_claude_provider():
    """
    Explicitly use Claude (Anthropic)

    Best for: Code generation, long context
    To run: pytest tests/examples/test_multi_ai_providers.py::test_use_claude_provider -v -s
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Using Claude Provider (Anthropic)")
    print("=" * 80)

    try:
        # Use Claude for test generation (often better at code)
        generator = NaturalLanguageTestGenerator(provider_name="claude")

        print(f"\nProvider: {generator.ai_provider.get_provider_name()}")
        print(f"Model: {generator.ai_provider.config.model}")

        description = """
        Test user login flow:
        1. Navigate to login page
        2. Enter username 'test@example.com'
        3. Enter password 'Test@123'
        4. Click login button
        5. Verify dashboard is displayed
        """

        print(f"\nGenerating test code...")
        test_code = generator.generate_test(description, test_type="ui")

        print("\n" + "-" * 80)
        print("Generated Test Code:")
        print("-" * 80)
        print(test_code)

    except RuntimeError as e:
        pytest.skip(f"Claude provider not available: {e}")


# ============================================================================
# EXAMPLE 4: Use Azure OpenAI
# ============================================================================


def test_use_azure_provider():
    """
    Explicitly use Azure OpenAI

    Best for: Enterprise compliance, Azure ecosystem
    To run: pytest tests/examples/test_multi_ai_providers.py::test_use_azure_provider -v -s
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Using Azure OpenAI Provider")
    print("=" * 80)

    try:
        # Use Azure OpenAI
        suggester = AIValidationSuggester(provider_name="azure")

        print(f"\nProvider: {suggester.ai_provider.get_provider_name()}")
        print(f"Deployment: {suggester.ai_provider.config.model}")

        mock_response = {"user_id": "USR-456", "email": "new.user@example.com", "status": "ACTIVE"}

        strategy = suggester.suggest_validations(
            api_endpoint="/api/users", api_method="POST", api_request={}, api_response=mock_response
        )

        print(f"\nGenerated {len(strategy.suggestions)} validations")

    except RuntimeError as e:
        pytest.skip(f"Azure provider not available: {e}")


# ============================================================================
# EXAMPLE 5: Use Ollama (Local/Free)
# ============================================================================


def test_use_ollama_provider():
    """
    Explicitly use Ollama (local LLMs - FREE)

    Best for: Privacy, cost savings, no internet
    Requires: Ollama running locally (ollama serve)
    To run: pytest tests/examples/test_multi_ai_providers.py::test_use_ollama_provider -v -s
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Using Ollama Provider (Local/Free)")
    print("=" * 80)

    try:
        # Use Ollama (local)
        suggester = AIValidationSuggester(provider_name="ollama")

        print(f"\nProvider: {suggester.ai_provider.get_provider_name()}")
        print(f"Model: {suggester.ai_provider.config.model}")
        print(f"Endpoint: {suggester.ai_provider.api_base}")

        mock_response = {"product_id": "PRD-789", "name": "Widget", "price": 49.99, "stock": 100}

        strategy = suggester.suggest_validations(
            api_endpoint="/api/products",
            api_method="POST",
            api_request={},
            api_response=mock_response,
        )

        print(f"\nGenerated {len(strategy.suggestions)} validations (using local AI)")

    except RuntimeError as e:
        pytest.skip(f"Ollama provider not available. Start with: ollama serve")


# ============================================================================
# EXAMPLE 6: Switch Providers Dynamically
# ============================================================================


def test_switch_providers_dynamically():
    """
    Switch between providers based on task

    To run: pytest tests/examples/test_multi_ai_providers.py::test_switch_providers_dynamically -v -s
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Switching Providers Dynamically")
    print("=" * 80)

    # Task 1: Use OpenAI for validation (best quality)
    print("\n--- Task 1: Validation Suggestions (OpenAI) ---")
    try:
        suggester_openai = AIValidationSuggester(provider_name="openai")
        print(f"Provider: {suggester_openai.ai_provider.get_provider_name()}")
    except RuntimeError:
        print("OpenAI not available")

    # Task 2: Use Claude for code generation (often better)
    print("\n--- Task 2: Test Code Generation (Claude) ---")
    try:
        generator_claude = NaturalLanguageTestGenerator(provider_name="claude")
        print(f"Provider: {generator_claude.ai_provider.get_provider_name()}")
    except RuntimeError:
        print("Claude not available")

    # Task 3: Use Ollama for development (free)
    print("\n--- Task 3: Local Development (Ollama) ---")
    try:
        suggester_local = AIValidationSuggester(provider_name="ollama")
        print(f"Provider: {suggester_local.ai_provider.get_provider_name()}")
    except RuntimeError:
        print("Ollama not available (run: ollama serve)")


# ============================================================================
# EXAMPLE 7: Check Available Providers
# ============================================================================


def test_check_available_providers():
    """
    Check which AI providers are currently available

    To run: pytest tests/examples/test_multi_ai_providers.py::test_check_available_providers -v -s
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Available AI Providers")
    print("=" * 80)

    available = ai_factory.get_available_providers()

    print(f"\nAvailable providers: {', '.join(available)}")
    print(f"\nTotal: {len(available)} provider(s)")

    if not available:
        print("\n⚠️  No AI providers available!")
        print("Please configure at least one provider:")
        print("  - OpenAI: Set OPENAI_API_KEY")
        print("  - Claude: Set ANTHROPIC_API_KEY")
        print("  - Azure: Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT")
        print("  - Ollama: Run 'ollama serve'")

    print("\n" + "-" * 80)
    print("Provider Details:")
    print("-" * 80)

    for provider_name in ["openai", "claude", "azure", "ollama"]:
        try:
            provider = get_ai_provider(provider_name)
            print(f"✓ {provider_name}: {provider.config.model} (available)")
        except:
            print(f"✗ {provider_name}: Not configured")


# ============================================================================
# EXAMPLE 8: Automatic Fallback
# ============================================================================


def test_automatic_fallback():
    """
    Demonstrates automatic fallback to available provider

    If default provider fails, tries next priority provider automatically
    To run: pytest tests/examples/test_multi_ai_providers.py::test_automatic_fallback -v -s
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Automatic Provider Fallback")
    print("=" * 80)

    # This will try providers in priority order:
    # 1. OpenAI (priority 1)
    # 2. Claude (priority 2)
    # 3. Azure (priority 3)
    # 4. Ollama (priority 4)

    suggester = AIValidationSuggester()  # Uses default with fallback

    print(f"\nUsing provider: {suggester.ai_provider.get_provider_name()}")
    print(f"Model: {suggester.ai_provider.config.model}")
    print(f"Priority: {suggester.ai_provider.config.priority}")

    mock_response = {"id": 1, "name": "Test", "status": "OK"}

    strategy = suggester.suggest_validations(
        api_endpoint="/api/test", api_method="GET", api_request={}, api_response=mock_response
    )

    print(f"\nGenerated {len(strategy.suggestions)} validations")
    print("\nFallback ensures tests never fail due to one provider being down!")


# ============================================================================
# EXAMPLE 9: Direct Provider API Usage
# ============================================================================


def test_direct_provider_usage():
    """
    Use AI provider directly for custom prompts

    To run: pytest tests/examples/test_multi_ai_providers.py::test_direct_provider_usage -v -s
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 9: Direct Provider API Usage")
    print("=" * 80)

    try:
        # Get provider directly
        provider = get_ai_provider()  # Uses default

        print(f"\nProvider: {provider.get_provider_name()}")

        # Custom prompt
        prompt = "Generate a SQL query to find all orders created in the last 7 days"
        system_prompt = "You are a SQL expert. Generate only SQL code, no explanations."

        print(f"\nPrompt: {prompt}")
        print("\nGenerating response...")

        response = provider.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1,  # Low temperature for precise code
        )

        print("\n" + "-" * 80)
        print("Generated SQL:")
        print("-" * 80)
        print(response)

    except RuntimeError as e:
        pytest.skip(f"AI provider not available: {e}")


# ============================================================================
# EXAMPLE 10: Environment-Based Provider Selection
# ============================================================================


def test_environment_based_provider(request):
    """
    Select provider based on environment

    To run: pytest tests/examples/test_multi_ai_providers.py::test_environment_based_provider -v -s --env=dev
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 10: Environment-Based Provider Selection")
    print("=" * 80)

    # Get environment from pytest
    env = request.config.getoption("--env", default="dev")

    # Select provider based on environment
    if env == "production":
        provider_name = "azure"  # Enterprise compliance for production
    elif env == "dev" or env == "local":
        provider_name = "ollama"  # Free local for development
    else:
        provider_name = "openai"  # Default for staging

    print(f"\nEnvironment: {env}")
    print(f"Selected provider: {provider_name}")

    try:
        suggester = AIValidationSuggester(provider_name=provider_name)
        print(f"Using: {suggester.ai_provider.get_provider_name()}")
    except RuntimeError as e:
        print(f"Provider '{provider_name}' not available: {e}")
        print("Trying default...")
        suggester = AIValidationSuggester()
        print(f"Fallback to: {suggester.ai_provider.get_provider_name()}")
# ARCHITECTURAL FIX: Removed executable pattern - use pytest runner instead
# Run individual examples:
# - Default: pytest tests/examples/test_multi_ai_providers.py::test_default_ai_provider -v -s
# - OpenAI: pytest tests/examples/test_multi_ai_providers.py::test_use_openai_provider -v -s
# - Claude: pytest tests/examples/test_multi_ai_providers.py::test_use_claude_provider -v -s
# - All: pytest tests/examples/test_multi_ai_providers.py -v -s
