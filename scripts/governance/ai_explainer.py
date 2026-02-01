#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════
AI-POWERED VIOLATION EXPLANATION SYSTEM
════════════════════════════════════════════════════════════════════════════

Generates detailed, educational explanations for architectural violations.

CRITICAL RULES:
❌ AI NEVER modifies code
❌ AI NEVER changes logic
✅ AI only explains and educates
✅ AI output is advisory only
✅ System functions without AI

USAGE:
    # Generate explanation for a violation
    python ai_explainer.py --violation-file violations.json --output explained.md
    
    # Interactive mode
    python ai_explainer.py --interactive

Author: Principal QA Architect
Date: February 1, 2026
════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import asdict

# Add governance scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'governance'))

from framework_audit_engine import Violation, Category, Severity


# ════════════════════════════════════════════════════════════════════════════
# AI EXPLANATION ENGINE
# ════════════════════════════════════════════════════════════════════════════

class AIExplanationEngine:
    """
    Generates AI-powered explanations for violations
    
    IMPORTANT: This is EXPLAIN-ONLY, never auto-fix
    """
    
    # Fallback explanations if AI is disabled/unavailable
    FALLBACK_EXPLANATIONS = {
        'mixed-engines': """
**Why this is a problem:**
Mixing Playwright and Selenium in the same test file creates confusion and maintenance nightmares. 
Each engine has different APIs, different waiting mechanisms, and different failure modes.

**Risk introduced:**
- Developers don't know which engine to use
- Debugging becomes extremely difficult
- Framework can't optimize execution
- Tests become brittle and unpredictable

**Rule violated:**
Engine Isolation Principle - One test, one engine

**How to fix:**
Split the file into two separate test files:
1. One for Playwright tests (modern SPAs)
2. One for Selenium tests (legacy UIs)

Mark each with appropriate pytest markers.
""",
        
        'missing-engine-marker': """
**Why this is a problem:**
The framework uses markers to route tests to the correct engine automatically.
Without a marker, the framework doesn't know whether to use Playwright or Selenium.

**Risk introduced:**
- Test might use wrong engine for the UI type
- Framework can't optimize parallel execution
- CI/CD pipeline can't categorize tests properly
- Test intent is unclear to other developers

**Rule violated:**
Explicit Intent Declaration - Every test must declare its engine

**How to fix:**
Add @pytest.mark.modern_spa for Playwright or @pytest.mark.legacy_ui for Selenium
to your test class. Choose based on the UI characteristics, not personal preference.
""",
        
        'assertion-in-page-object': """
**Why this is a problem:**
Page Objects are reusable components that model UI behavior. If they contain
assertions, they can't be reused in different contexts where different assertions
are needed.

**Risk introduced:**
- Page Objects become tightly coupled to specific tests
- Can't reuse Page Object methods in different scenarios
- Assertions hide in Page Objects, making test intent unclear
- Difficult to maintain and debug

**Rule violated:**
Single Responsibility Principle - Page Objects model UI, tests verify behavior

**How to fix:**
Return data from Page Objects, assert in tests. This makes Page Objects reusable
and keeps test logic visible in test files where it belongs.
""",
        
        'direct-locator-in-test': """
**Why this is a problem:**
When test files contain direct locator calls (page.locator, driver.find_element),
the UI interaction logic is scattered across many test files instead of centralized
in Page Objects.

**Risk introduced:**
- UI changes require updating multiple test files
- Locators duplicated across tests
- Test files become long and hard to read
- No single source of truth for UI interactions

**Rule violated:**
DRY Principle + Page Object Pattern - Centralize UI logic

**How to fix:**
Extract locator logic into Page Object methods. Tests should call high-level
methods like login() or search(), not low-level locator manipulation.
""",
    }
    
    def __init__(self, ai_enabled: bool = False):
        """
        Initialize AI explainer
        
        Args:
            ai_enabled: If True, attempt to use AI. If False or unavailable, use fallbacks.
        """
        self.ai_enabled = ai_enabled
        self.ai_available = False
        
        if ai_enabled:
            self.ai_available = self._check_ai_availability()
    
    def _check_ai_availability(self) -> bool:
        """Check if AI service is available"""
        # In real implementation, would check for:
        # - OpenAI API key
        # - Azure OpenAI endpoint
        # - Local LLM availability
        # For now, return False (use fallbacks)
        return False
    
    def explain_violation(self, violation: Violation) -> str:
        """
        Generate explanation for a violation
        
        Args:
            violation: Violation to explain
            
        Returns:
            Detailed explanation as markdown
        """
        if self.ai_available:
            return self._generate_ai_explanation(violation)
        else:
            return self._generate_fallback_explanation(violation)
    
    def _generate_ai_explanation(self, violation: Violation) -> str:
        """
        Generate AI-powered explanation
        
        NOTE: This would call OpenAI/Azure/Local LLM
        For now, falls back to template
        """
        # In real implementation:
        # 1. Construct prompt with violation context
        # 2. Call AI service
        # 3. Parse and validate response
        # 4. Ensure response doesn't contain code changes
        # 5. Return explanation
        
        return self._generate_fallback_explanation(violation)
    
    def _generate_fallback_explanation(self, violation: Violation) -> str:
        """Generate template-based explanation"""
        
        template = self.FALLBACK_EXPLANATIONS.get(violation.rule_id)
        
        if template:
            explanation = f"""
# 📚 Understanding This Violation

## {violation.message}

{template}

## Violation Details

- **File:** {violation.file_path}
- **Line:** {violation.line_number}
- **Category:** {violation.category.value}
- **Severity:** {violation.severity.value}
- **Rule ID:** {violation.rule_id}

## Context

```python
{violation.context if violation.context else "No context available"}
```

## Suggested Fix

{violation.fix_suggestion if violation.fix_suggestion else "See fix suggestion in main report"}

---

*This explanation is provided to help understand architectural principles. 
The system will never auto-fix code - all changes must be intentional.*
"""
            return explanation.strip()
        
        # Generic explanation if no template
        return f"""
# 📚 Understanding This Violation

## {violation.message}

**Category:** {violation.category.value}
**Severity:** {violation.severity.value}
**Rule:** {violation.rule_id}

This violation indicates a departure from established architectural patterns.
Review the architectural guidelines for details on this rule.

**File:** {violation.file_path}:{violation.line_number}

**Context:**
```python
{violation.context if violation.context else "No context available"}
```
"""
    
    def explain_batch(self, violations: List[Violation], output_path: Path):
        """
        Generate explanations for multiple violations
        
        Args:
            violations: List of violations
            output_path: Where to save explanations
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 📚 Architectural Violation Explanations\n\n")
            f.write(f"**Total Violations:** {len(violations)}\n\n")
            f.write("---\n\n")
            
            for i, violation in enumerate(violations, 1):
                f.write(f"## Violation {i}/{len(violations)}\n\n")
                explanation = self.explain_violation(violation)
                f.write(explanation)
                f.write("\n\n---\n\n")
        
        print(f"✅ Explanations saved to: {output_path}")


# ════════════════════════════════════════════════════════════════════════════
# INTERACTIVE MODE
# ════════════════════════════════════════════════════════════════════════════

def interactive_mode():
    """Interactive violation explanation"""
    
    print("\n" + "="*80)
    print("🤖 AI VIOLATION EXPLAINER - Interactive Mode")
    print("="*80)
    print("\nEnter violation details to get an explanation.")
    print("Type 'quit' to exit.\n")
    
    explainer = AIExplanationEngine(ai_enabled=False)
    
    while True:
        print("\nAvailable rule IDs:")
        for rule_id in AIExplanationEngine.FALLBACK_EXPLANATIONS.keys():
            print(f"  - {rule_id}")
        
        rule_id = input("\nEnter rule ID (or 'quit'): ").strip()
        
        if rule_id.lower() == 'quit':
            break
        
        if rule_id not in AIExplanationEngine.FALLBACK_EXPLANATIONS:
            print(f"❌ Unknown rule ID: {rule_id}")
            continue
        
        # Create dummy violation for explanation
        violation = Violation(
            category=Category.ENGINE_MIX,
            severity=Severity.ERROR,
            rule_id=rule_id,
            file_path="example.py",
            line_number=42,
            message=f"Example violation: {rule_id}",
            context="# Example code context",
            fix_suggestion="See detailed explanation"
        )
        
        print("\n" + "="*80)
        explanation = explainer.explain_violation(violation)
        print(explanation)
        print("="*80)


# ════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='AI-Powered Violation Explainer (Explain-Only, Never Auto-Fix)'
    )
    
    parser.add_argument(
        '--violation-file',
        type=Path,
        help='JSON file containing violations'
    )
    
    parser.add_argument(
        '--output',
        type=Path,
        help='Output file for explanations'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interactive explanation mode'
    )
    
    parser.add_argument(
        '--enable-ai',
        action='store_true',
        help='Enable AI-powered explanations (requires API key)'
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
        return
    
    if not args.violation_file or not args.output:
        parser.print_help()
        print("\n❌ --violation-file and --output are required (or use --interactive)")
        sys.exit(1)
    
    # Load violations
    if not args.violation_file.exists():
        print(f"❌ Violation file not found: {args.violation_file}")
        sys.exit(1)
    
    with open(args.violation_file, 'r') as f:
        violation_data = json.load(f)
    
    # Convert to Violation objects
    # (In real implementation, would properly deserialize)
    print("⚠️  Violation deserialization not fully implemented")
    print("Use interactive mode or integrate with audit engine directly")
    
    sys.exit(0)


if __name__ == '__main__':
    main()
