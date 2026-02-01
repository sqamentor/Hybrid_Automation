"""
Page Object Generator
Automatically generates Page Object Model classes from recorded Playwright scripts
"""

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger


class PageObjectGenerator:
    """
    Generates Page Object Model classes from recorded Playwright scripts
    Extracts locators, actions, and creates reusable page classes
    """
    
    def __init__(self, output_dir: str = "pages"):
        """
        Initialize Page Object Generator
        
        Args:
            output_dir: Directory to save generated page objects
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Page Object Generator initialized. Output: {self.output_dir}")
    
    def generate_from_script(
        self,
        script_path: str,
        page_name: Optional[str] = None,
        extract_locators: bool = True,
        extract_actions: bool = True
    ) -> Dict[str, Any]:
        """
        Generate Page Object from recorded script
        
        Args:
            script_path: Path to recorded/refactored script
            page_name: Name for the page object class
            extract_locators: Extract locators as properties
            extract_actions: Extract actions as methods
        
        Returns:
            Dict with generation metadata
        """
        script_file = Path(script_path)
        
        if not script_file.exists():
            return {
                "status": "error",
                "message": f"Script not found: {script_path}"
            }
        
        # Read script
        with open(script_file, 'r', encoding='utf-8') as f:
            script_code = f.read()
        
        # Determine page name
        if page_name is None:
            page_name = script_file.stem.replace('_', ' ').title().replace(' ', '')
            if page_name.endswith('Page'):
                page_name = page_name
            else:
                page_name = page_name + 'Page'
        
        logger.info(f"Generating Page Object: {page_name}")
        
        # Extract elements from script
        locators = self._extract_locators(script_code) if extract_locators else []
        actions = self._extract_actions(script_code) if extract_actions else []
        url = self._extract_url(script_code)
        
        # Generate Page Object class
        page_object_code = self._generate_page_class(
            page_name,
            locators,
            actions,
            url
        )
        
        # Save Page Object
        page_file = self.output_dir / f"{self._to_snake_case(page_name)}.py"
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(page_object_code)
        
        logger.info(f"✓ Page Object generated: {page_file}")
        
        # Generate usage example
        usage_example = self._generate_usage_example(page_name, page_file.stem)
        
        return {
            "status": "success",
            "page_class": page_name,
            "page_file": str(page_file),
            "locators_count": len(locators),
            "actions_count": len(actions),
            "url": url,
            "usage_example": usage_example
        }
    
    def _extract_locators(self, code: str) -> List[Dict[str, str]]:
        """Extract locators from script"""
        locators = []
        
        # Patterns to match Playwright locators
        patterns = [
            (r'page\.locator\([\'"]([^\'"]+)[\'"]\)', 'css'),
            (r'page\.get_by_role\([\'"]([^\'"]+)[\'"]\)', 'role'),
            (r'page\.get_by_text\([\'"]([^\'"]+)[\'"]\)', 'text'),
            (r'page\.get_by_placeholder\([\'"]([^\'"]+)[\'"]\)', 'placeholder'),
            (r'page\.get_by_test_id\([\'"]([^\'"]+)[\'"]\)', 'testid'),
            (r'page\.get_by_label\([\'"]([^\'"]+)[\'"]\)', 'label'),
        ]
        
        seen_locators = set()
        
        for pattern, locator_type in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                selector = match.group(1)
                
                # Create unique identifier
                locator_key = f"{locator_type}:{selector}"
                if locator_key not in seen_locators:
                    seen_locators.add(locator_key)
                    
                    # Generate property name
                    prop_name = self._generate_property_name(selector, locator_type)
                    
                    locators.append({
                        "name": prop_name,
                        "type": locator_type,
                        "selector": selector,
                        "code": match.group(0)
                    })
        
        return locators
    
    def _extract_actions(self, code: str) -> List[Dict[str, Any]]:
        """Extract actions from script"""
        actions = []
        
        # Common Playwright actions
        action_patterns = {
            'click': r'page\.(?:locator|get_by_\w+)\([^\)]+\)\.click\(\)',
            'fill': r'page\.(?:locator|get_by_\w+)\([^\)]+\)\.fill\([^\)]+\)',
            'select': r'page\.(?:locator|get_by_\w+)\([^\)]+\)\.select_option\([^\)]+\)',
            'check': r'page\.(?:locator|get_by_\w+)\([^\)]+\)\.check\(\)',
            'uncheck': r'page\.(?:locator|get_by_\w+)\([^\)]+\)\.uncheck\(\)',
        }
        
        for action_type, pattern in action_patterns.items():
            matches = re.finditer(pattern, code)
            for match in matches:
                actions.append({
                    "type": action_type,
                    "code": match.group(0)
                })
        
        return actions
    
    def _extract_url(self, code: str) -> Optional[str]:
        """Extract URL from goto statement"""
        match = re.search(r'page\.goto\([\'"]([^\'"]+)[\'"]\)', code)
        if match:
            return match.group(1)
        return None
    
    def _generate_page_class(
        self,
        class_name: str,
        locators: List[Dict[str, str]],
        actions: List[Dict[str, Any]],
        url: Optional[str]
    ) -> str:
        """Generate Page Object class code"""
        
        # Build class code
        code_parts = []
        
        # Header
        code_parts.append('"""')
        code_parts.append(f'Page Object: {class_name}')
        code_parts.append('Auto-generated from recorded Playwright script')
        code_parts.append('"""')
        code_parts.append('')
        code_parts.append('from playwright.sync_api import Page, expect')
        code_parts.append('from typing import Optional')
        code_parts.append('')
        code_parts.append('')
        
        # Class definition
        code_parts.append(f'class {class_name}:')
        code_parts.append(f'    """Page Object for {class_name}"""')
        code_parts.append('')
        
        # Constructor
        if url:
            code_parts.append(f'    URL = "{url}"')
            code_parts.append('')
        
        code_parts.append('    def __init__(self, page: Page):')
        code_parts.append('        """')
        code_parts.append('        Initialize page object')
        code_parts.append('        ')
        code_parts.append('        Args:')
        code_parts.append('            page: Playwright Page instance')
        code_parts.append('        """')
        code_parts.append('        self.page = page')
        code_parts.append('')
        
        # Locator properties
        if locators:
            code_parts.append('    # Locators')
            for locator in locators:
                code_parts.append(f'    @property')
                code_parts.append(f'    def {locator["name"]}(self):')
                code_parts.append(f'        """Locator for {locator["selector"]}"""')
                
                # Generate appropriate locator code
                if locator["type"] == "css":
                    code_parts.append(f'        return self.page.locator("{locator["selector"]}")')
                elif locator["type"] == "role":
                    code_parts.append(f'        return self.page.get_by_role("{locator["selector"]}")')
                elif locator["type"] == "text":
                    code_parts.append(f'        return self.page.get_by_text("{locator["selector"]}")')
                elif locator["type"] == "testid":
                    code_parts.append(f'        return self.page.get_by_test_id("{locator["selector"]}")')
                elif locator["type"] == "placeholder":
                    code_parts.append(f'        return self.page.get_by_placeholder("{locator["selector"]}")')
                elif locator["type"] == "label":
                    code_parts.append(f'        return self.page.get_by_label("{locator["selector"]}")')
                
                code_parts.append('')
        
        # Navigation method
        if url:
            code_parts.append('    # Navigation')
            code_parts.append('    def navigate(self):')
            code_parts.append('        """Navigate to the page"""')
            code_parts.append(f'        self.page.goto(self.URL)')
            code_parts.append('        return self')
            code_parts.append('')
        
        # Action methods (template)
        code_parts.append('    # Actions')
        code_parts.append('    def fill_field(self, locator, value: str):')
        code_parts.append('        """Fill a form field"""')
        code_parts.append('        locator.fill(value)')
        code_parts.append('        return self')
        code_parts.append('')
        
        code_parts.append('    def click_element(self, locator):')
        code_parts.append('        """Click an element"""')
        code_parts.append('        locator.click()')
        code_parts.append('        return self')
        code_parts.append('')
        
        # Verification methods
        code_parts.append('    # Verifications')
        code_parts.append('    def verify_visible(self, locator):')
        code_parts.append('        """Verify element is visible"""')
        code_parts.append('        expect(locator).to_be_visible()')
        code_parts.append('        return self')
        code_parts.append('')
        
        code_parts.append('    def verify_text(self, locator, expected_text: str):')
        code_parts.append('        """Verify element contains text"""')
        code_parts.append('        expect(locator).to_contain_text(expected_text)')
        code_parts.append('        return self')
        code_parts.append('')
        
        return '\n'.join(code_parts)
    
    def _generate_property_name(self, selector: str, locator_type: str) -> str:
        """Generate a valid Python property name from selector"""
        # Remove special characters
        name = re.sub(r'[^\w\s-]', '', selector)
        # Replace spaces and hyphens with underscores
        name = re.sub(r'[-\s]+', '_', name)
        # Convert to lowercase
        name = name.lower().strip('_')
        # Ensure it doesn't start with number
        if name and name[0].isdigit():
            name = f'{locator_type}_{name}'
        # Default if empty
        if not name:
            name = f'{locator_type}_element'
        
        return name
    
    def _to_snake_case(self, name: str) -> str:
        """Convert PascalCase to snake_case"""
        # Insert underscore before uppercase letters
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _generate_usage_example(self, class_name: str, module_name: str) -> str:
        """Generate usage example"""
        return f"""# Usage Example:

from pages.{module_name} import {class_name}

def test_using_{module_name}(page):
    # Initialize page object
    page_obj = {class_name}(page)
    
    # Navigate to page
    page_obj.navigate()
    
    # Use page object methods
    page_obj.fill_field(page_obj.some_field, "test value")
    page_obj.click_element(page_obj.submit_button)
    page_obj.verify_visible(page_obj.success_message)
"""
    
    def list_page_objects(self) -> List[Dict[str, Any]]:
        """List all generated page objects"""
        page_objects = []
        
        for py_file in self.output_dir.glob("*.py"):
            if py_file.name != "__init__.py":
                page_objects.append({
                    "name": py_file.stem,
                    "path": str(py_file),
                    "size": py_file.stat().st_size
                })
        
        return page_objects
