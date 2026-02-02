"""
AI-Assisted Script Refactorer
Uses AI to improve recorded Playwright scripts:
- Add comments and documentation
- Improve locator strategies
- Extract reusable functions
- Add assertions
- Improve code quality
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger


class AIScriptRefactorer:
    """
    AI-assisted refactoring of recorded Playwright scripts
    Improves code quality, adds documentation, and enhances maintainability
    """

    def __init__(self, ai_provider_name: Optional[str] = None):
        """
        Initialize AI Script Refactorer

        Args:
            ai_provider_name: AI provider to use ('openai', 'claude', etc.)
        """
        self.ai_provider_name = ai_provider_name
        self.ai_provider = None
        self.enabled = False

        # Initialize AI provider
        self._initialize_ai()

    def _initialize_ai(self):
        """Initialize AI provider"""
        try:
            from framework.ai.ai_provider_factory import get_ai_provider

            self.ai_provider = get_ai_provider(self.ai_provider_name)
            if self.ai_provider:
                self.enabled = True
                logger.info(
                    f"AI Refactorer initialized with {self.ai_provider.get_provider_name()}"
                )
            else:
                logger.warning(
                    "AI provider not available. Refactorer will use rule-based improvements only."
                )
                self.enabled = False
        except Exception as e:
            logger.warning(f"Could not initialize AI provider: {e}")
            self.enabled = False

    def refactor_script(
        self, script_path: str, improvements: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Refactor a recorded Playwright script

        Args:
            script_path: Path to the recorded script
            improvements: List of improvement types to apply
                         ['comments', 'locators', 'assertions', 'functions', 'documentation']

        Returns:
            Dict with refactored code and metadata
        """
        script_file = Path(script_path)

        if not script_file.exists():
            return {"status": "error", "message": f"Script not found: {script_path}"}

        # Read original script
        with open(script_file, "r", encoding="utf-8") as f:
            original_code = f.read()

        logger.info(f"Refactoring script: {script_file.name}")

        # Default improvements
        if improvements is None:
            improvements = ["comments", "locators", "assertions", "documentation"]

        # Apply AI refactoring if available
        if self.enabled:
            refactored_code = self._ai_refactor(original_code, improvements)
        else:
            # Fallback to rule-based refactoring
            logger.info("Using rule-based refactoring (AI not available)")
            refactored_code = self._rule_based_refactor(original_code, improvements)

        # Save refactored version
        refactored_file = script_file.parent / f"{script_file.stem}_refactored.py"
        with open(refactored_file, "w", encoding="utf-8") as f:
            f.write(refactored_code)

        logger.info(f"✓ Refactored script saved: {refactored_file}")

        return {
            "status": "success",
            "original_file": str(script_file),
            "refactored_file": str(refactored_file),
            "original_size": len(original_code),
            "refactored_size": len(refactored_code),
            "improvements_applied": improvements,
            "ai_used": self.enabled,
        }

    def _ai_refactor(self, code: str, improvements: List[str]) -> str:
        """Use AI to refactor the script"""
        if not self.ai_provider:
            return self._rule_based_refactor(code, improvements)

        try:
            prompt = self._build_refactoring_prompt(code, improvements)

            logger.info("Requesting AI refactoring...")
            refactored = self.ai_provider.generate_completion(
                prompt=prompt,
                system_prompt="You are an expert test automation engineer specializing in Playwright test refactoring.",
                temperature=0.3,
                timeout=60,
            )

            # Extract code from AI response
            refactored_code = self._extract_code_from_response(refactored)

            logger.info("✓ AI refactoring completed")
            return refactored_code

        except Exception as e:
            logger.warning(f"AI refactoring failed: {e}. Falling back to rule-based.")
            return self._rule_based_refactor(code, improvements)

    def _build_refactoring_prompt(self, code: str, improvements: List[str]) -> str:
        """Build prompt for AI refactoring"""
        improvements_desc = ", ".join(improvements)

        prompt = f"""Refactor this Playwright test script with the following improvements: {improvements_desc}

Original Script:
```python
{code}
```

Refactoring Guidelines:
1. PRESERVE ALL FUNCTIONALITY - Do not change test behavior
2. Add clear comments explaining what each section does
3. Improve locator strategies (prefer data-testid, role, text over CSS)
4. Add meaningful assertions (not just clicks)
5. Extract repeated patterns into helper functions
6. Add proper test documentation (docstrings)
7. Use Page Object pattern where beneficial
8. Add proper error handling
9. Keep the script executable and valid Python/Pytest code

Return ONLY the refactored Python code, no explanations."""

        return prompt

    def _extract_code_from_response(self, response: str) -> str:
        """Extract code from AI response"""
        # Try to extract code from markdown code blocks
        code_blocks = re.findall(r"```python\n(.*?)\n```", response, re.DOTALL)
        if code_blocks:
            return code_blocks[0]

        # Try without language specifier
        code_blocks = re.findall(r"```\n(.*?)\n```", response, re.DOTALL)
        if code_blocks:
            return code_blocks[0]

        # Return full response if no code blocks found
        return response.strip()

    def _rule_based_refactor(self, code: str, improvements: List[str]) -> str:
        """Rule-based refactoring when AI is not available"""
        refactored = code

        # Add module docstring if not present
        if "documentation" in improvements and not code.strip().startswith('"""'):
            refactored = '"""Generated Playwright test - Refactored"""\n\n' + refactored

        # Improve imports
        if "imports" in improvements or "documentation" in improvements:
            refactored = self._improve_imports(refactored)

        # Add comments to major sections
        if "comments" in improvements:
            refactored = self._add_section_comments(refactored)

        # Suggest better locators (as comments)
        if "locators" in improvements:
            refactored = self._suggest_locator_improvements(refactored)

        # Add assertion suggestions
        if "assertions" in improvements:
            refactored = self._add_assertion_hints(refactored)

        return refactored

    def _improve_imports(self, code: str) -> str:
        """Add organized imports"""
        if "import pytest" not in code and "import re" not in code:
            imports = """import pytest
from playwright.sync_api import Page, expect

"""
            # Find where to insert (after module docstring if present)
            if code.strip().startswith('"""'):
                # Find end of docstring
                parts = code.split('"""', 2)
                if len(parts) >= 3:
                    return f'"""{parts[1]}"""\n\n{imports}{parts[2]}'

            return imports + code
        return code

    def _add_section_comments(self, code: str) -> str:
        """Add comments to identify test sections"""
        lines = code.split("\n")
        enhanced = []

        for i, line in enumerate(lines):
            # Add comment before navigation
            if "page.goto(" in line and i > 0 and not lines[i - 1].strip().startswith("#"):
                enhanced.append("    # Navigate to application")

            # Add comment before form interactions
            elif "page.fill(" in line and i > 0 and not lines[i - 1].strip().startswith("#"):
                enhanced.append("    # Fill form field")

            # Add comment before clicks
            elif "page.click(" in line and i > 0 and not lines[i - 1].strip().startswith("#"):
                enhanced.append("    # Click element")

            enhanced.append(line)

        return "\n".join(enhanced)

    def _suggest_locator_improvements(self, code: str) -> str:
        """Add comments suggesting better locators"""
        # Find CSS selectors and suggest alternatives
        css_patterns = [
            (r'page\.locator\("([^"]+)"\)', "CSS selector"),
            (r'page\.query_selector\("([^"]+)"\)', "CSS selector"),
        ]

        suggestions = []
        for pattern, selector_type in css_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                selector = match.group(1)
                if selector.startswith(".") or selector.startswith("#"):
                    suggestions.append(
                        f"# TODO: Consider using data-testid or role-based locator instead of: {selector}"
                    )

        if suggestions:
            # Add suggestions at the top
            suggestion_block = "\n".join(suggestions) + "\n\n"
            return suggestion_block + code

        return code

    def _add_assertion_hints(self, code: str) -> str:
        """Add hints for assertions"""
        if "expect(" not in code and "assert " not in code:
            # Add comment suggesting assertions
            lines = code.split("\n")
            for i, line in enumerate(lines):
                if "page.goto(" in line:
                    lines.insert(i + 1, "    # TODO: Add assertion to verify page loaded correctly")
                elif "page.click(" in line and "submit" in line.lower():
                    lines.insert(i + 1, "    # TODO: Add assertion to verify action completed")

            return "\n".join(lines)

        return code

    def preview_improvements(self, script_path: str) -> Dict[str, Any]:
        """
        Preview what improvements would be made without saving

        Args:
            script_path: Path to script

        Returns:
            Dict with improvement suggestions
        """
        script_file = Path(script_path)

        if not script_file.exists():
            return {"error": "Script not found"}

        with open(script_file, "r", encoding="utf-8") as f:
            code = f.read()

        suggestions = []

        # Check for missing imports
        if "import pytest" not in code:
            suggestions.append("Add pytest import")

        # Check for assertions
        if "expect(" not in code and "assert " not in code:
            suggestions.append("Add test assertions")

        # Check for comments
        comment_ratio = len([l for l in code.split("\n") if l.strip().startswith("#")]) / len(
            code.split("\n")
        )
        if comment_ratio < 0.1:
            suggestions.append("Add code comments")

        # Check for docstrings
        if not code.strip().startswith('"""'):
            suggestions.append("Add module documentation")

        return {
            "script": str(script_file),
            "suggestions": suggestions,
            "ai_available": self.enabled,
        }
