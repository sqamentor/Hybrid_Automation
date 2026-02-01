"""
Natural Language Test Generation - Convert Plain English to Test Code

Generates executable test code from natural language descriptions using AI.
Supports multiple AI providers: OpenAI, Claude, Azure OpenAI, Ollama.
"""

import json
import os
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from utils.logger import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from framework.ai.ai_provider_factory import BaseAIProvider


class NaturalLanguageTestGenerator:
    """Generate test code from natural language."""
    
    def __init__(self, provider_name: Optional[str] = None):
        """Initialize NL test generator.

        Args:
            provider_name: AI provider to use ('openai', 'claude', 'azure', 'ollama')
                          If None, uses default from configuration
        """
        self.provider_name = provider_name
        self.ai_provider: Optional['BaseAIProvider'] = None
        self.enabled = False
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize AI provider - never fails"""
        try:
            from framework.ai.ai_provider_factory import get_ai_provider
            
            self.ai_provider = get_ai_provider(self.provider_name)
            
            if self.ai_provider:
                self.enabled = True
                logger.info(f"NL Test Generator initialized with provider: {self.ai_provider.get_provider_name()}")
            else:
                logger.warning("No AI provider available. Test generation will return template code.")
                self.enabled = False
        
        except Exception as e:
            logger.warning(f"Failed to initialize AI provider: {e}. Test generation disabled.")
            self.enabled = False
    
    def generate_test(self, description: str, test_type: str = "ui") -> str:
        """Generate test code from description.

        NEVER FAILS: Returns template code if AI unavailable

        Args:
            description: Natural language test description
            test_type: Test type ('ui', 'api', 'e2e')

        Returns:
            Generated test code (AI-generated or template)
        """
        # Return template if AI not available
        if not self.enabled or not self.ai_provider:
            logger.warning(f"AI helper not available for test generation. Skipping AI code generation, using template instead. Continuing to next step.")
            logger.info(f"Generating template for {test_type} test")
            return self._generate_template(description, test_type)
        
        try:
            system_prompt = self._get_system_prompt(test_type)
            
            logger.info(f"Generating {test_type} test using {self.ai_provider.get_provider_name()}...")
            
            # Try AI generation with timeout
            test_code = self.ai_provider.generate_completion(
                prompt=description,
                system_prompt=system_prompt,
                temperature=0.3,
                timeout=30  # 30 second timeout
            )
            
            logger.info("✓ Test code generated successfully")
            return test_code
        
        except Exception as e:
            # NEVER FAIL - Return template on any error
            logger.warning(f"Test generation failed ({e}). Returning template code.")
            return self._generate_template(description, test_type)
    
    def _generate_template(self, description: str, test_type: str) -> str:
        """Generate basic template when AI unavailable."""
        if test_type == "ui":
            return f'''\"\"\"
Test generated from: {description}

TODO: AI unavailable - implement test manually
\"\"\"
import pytest

def test_ui_template(ui_engine):
    """Generated test template"""
    # TODO: Implement based on description:
    # {description}
    
    # Example:
    # ui_engine.navigate("https://example.com")
    # ui_engine.click("Submit")
    # assert ui_engine.is_visible("Success Message")
    
    pytest.skip("Template - needs implementation")
'''
        elif test_type == "api":
            return f'''\"\"\"
Test generated from: {description}

TODO: AI unavailable - implement test manually
\"\"\"
import pytest

def test_api_template(api_client):
    """Generated test template"""
    # TODO: Implement based on description:
    # {description}
    
    # Example:
    # response = api_client.get("/api/endpoint")
    # assert response.status_code == 200
    
    pytest.skip("Template - needs implementation")
'''
        else:  # e2e
            return f'''\"\"\"
Test generated from: {description}

TODO: AI unavailable - implement test manually
\"\"\"
import pytest

def test_e2e_template(ui_engine, api_client, db_client):
    """Generated test template"""
    # TODO: Implement based on description:
    # {description}
    
    # Example:
    # ui_engine.navigate("https://example.com")
    # response = api_client.get("/api/data")
    # result = db_client.query("SELECT * FROM table")
    
    pytest.skip("Template - needs implementation")
'''
    
    def _get_system_prompt(self, test_type: str) -> str:
        """Get system prompt for test generation."""
        base_prompt = """You are an expert QA automation engineer. Generate pytest test code from natural language descriptions.

Use this framework structure:
- UI tests: Use ui_engine fixture (PlaywrightEngine or SeleniumEngine)
- API tests: Use api_client fixture
- Database: Use db_client fixture
- AI validation: Use ai_validator fixture

Generate complete, runnable test functions with:
1. Proper imports
2. Clear test function name
3. Descriptive docstring
4. Proper assertions
5. Good error messages
6. Comments for clarity

Return ONLY the test code, no explanations."""
        
        if test_type == "ui":
            return base_prompt + """

Example UI test structure:
```python
import pytest

def test_user_login(ui_engine):
    \"\"\"Test user can log in successfully\"\"\"
    # Navigate to login page
    ui_engine.navigate("https://example.com/login")
    
    # Fill login form
    ui_engine.fill("input[name='email']", "user@example.com")
    ui_engine.fill("input[name='password']", "password123")
    ui_engine.click("button[type='submit']")
    
    # Verify login success
    assert ui_engine.is_visible("text=Welcome")
```
"""
        elif test_type == "api":
            return base_prompt + """

Example API test structure:
```python
import pytest

def test_get_users_api(api_client):
    \"\"\"Test GET /api/users returns user list\"\"\"
    # Send GET request
    response = api_client.get("/api/users")
    
    # Verify status code
    assert response.status_code == 200
    
    # Verify response structure
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'id' in data[0]
    assert 'email' in data[0]
```
"""
        elif test_type == "e2e":
            return base_prompt + """

Example E2E test structure:
```python
import pytest

def test_order_flow(ui_engine, api_client, db_client, ai_validator):
    \"\"\"Test complete order placement flow\"\"\"
    # UI: Place order
    ui_engine.navigate("https://example.com/products")
    ui_engine.click("button[data-product='123']")
    ui_engine.click("button.checkout")
    
    # API: Verify order created
    orders = api_client.get("/api/orders")
    order_id = orders.json()[0]['id']
    
    # AI: Get validation suggestions
    suggestions = ai_validator.suggest_validations(orders.json())
    
    # Database: Verify order in DB
    for validation in suggestions:
        result = db_client.execute_query(validation['sql'])
        assert result, f"{validation['description']} failed"
```
"""
        
        return base_prompt
    
    def generate_test_suite(self, feature_description: str, 
                           test_count: int = 5) -> List[Dict[str, str]]:
        """Generate multiple test cases for a feature.

        Args:
            feature_description: Feature description
            test_count: Number of tests to generate

        Returns:
            List of test cases with code
        """
        prompt = f"""Generate {test_count} test cases for this feature:

{feature_description}

Generate:
1. Happy path test
2. Negative test (invalid input)
3. Edge case test
4. Performance test
5. Error handling test

Return as JSON array with format:
[
  {{
    "name": "test_name",
    "description": "what it tests",
    "code": "complete test code"
  }}
]
"""
        if not self.enabled or not self.ai_provider:
            logger.warning("AI helper not available for test suite generation. Returning empty list.")
            return []

        try:
            response_text = self.ai_provider.generate_completion(
                prompt=prompt,
                system_prompt=self._get_system_prompt("ui"),
                temperature=0.5,
                timeout=60
            )
            tests = self._parse_suite_response(response_text)
            logger.info(f"Generated {len(tests)} test cases")
            return tests
        except Exception as exc:
            logger.error(f"Test suite generation failed: {exc}")
            raise

    def _parse_suite_response(self, payload: str) -> List[Dict[str, str]]:
        """Parse AI JSON payload into structured test cases."""
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError("AI response is not valid JSON") from exc

        if not isinstance(data, list):
            raise ValueError("AI response must be a JSON array")

        tests: List[Dict[str, str]] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            name = str(entry.get("name", "generated_test"))
            description = str(entry.get("description", ""))
            code = str(entry.get("code", ""))
            tests.append({
                "name": name,
                "description": description,
                "code": code
            })

        if not tests:
            raise ValueError("AI response did not contain any test cases")

        return tests
    
    def save_generated_test(self, test_code: str, output_path: str) -> None:
        """Save generated test to file.

        Args:
            test_code: Generated test code
            output_path: Output file path
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(test_code)
        
        logger.info(f"Test saved to: {output_path}")


class TestScenarioLibrary:
    """Library of common test scenarios."""
    
    SCENARIOS = {
        "login": "User navigates to login page, enters valid credentials, clicks login button, and sees dashboard",
        "registration": "User fills registration form with name, email, password, clicks sign up, and receives confirmation",
        "search": "User enters search term in search box, clicks search button, sees search results list",
        "checkout": "User adds item to cart, proceeds to checkout, enters shipping info, completes payment",
        "profile_update": "User navigates to profile page, updates name and email, saves changes, sees success message",
        "password_reset": "User clicks forgot password, enters email, receives reset link, sets new password",
        "filter_products": "User applies category and price filters, sees filtered product list",
        "pagination": "User navigates through paginated list using next/previous buttons",
        "sort_results": "User selects sort option, sees results reordered accordingly",
        "file_upload": "User clicks upload button, selects file, sees upload progress, gets success confirmation"
    }
    
    @classmethod
    def get_scenario(cls, scenario_name: str) -> Optional[str]:
        """Get predefined scenario description."""
        return cls.SCENARIOS.get(scenario_name.lower())
    
    @classmethod
    def list_scenarios(cls) -> List[str]:
        """List available scenarios."""
        return list(cls.SCENARIOS.keys())


__all__ = ['NaturalLanguageTestGenerator', 'TestScenarioLibrary']
