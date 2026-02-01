"""
Self-Healing Locators - AI-Powered Locator Recovery

Automatically finds alternative locators when elements can't be found,
using multiple strategies and AI-powered similarity matching.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import difflib
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class LocatorStrategy:
    """Locator strategy definition"""
    type: str  # 'css', 'xpath', 'id', 'name', 'text', 'aria-label'
    value: str
    confidence: float = 0.0


class SelfHealingLocators:
    """Self-healing locator engine"""
    
    def __init__(self, ui_engine):
        """
        Initialize self-healing locators
        
        Args:
            ui_engine: PlaywrightEngine or SeleniumEngine instance
        """
        self.ui_engine = ui_engine
        self.engine_type = type(ui_engine).__name__
        self.locator_cache: Dict[str, List[LocatorStrategy]] = {}
        self.healing_history: List[Dict] = []
    
    def find_element(self, primary_locator: str, context: Optional[Dict] = None) -> Any:
        """
        Find element with self-healing
        
        Args:
            primary_locator: Primary locator to try first
            context: Optional context (element type, label, nearby text)
        
        Returns:
            Found element
        
        Raises:
            ElementNotFoundException: If element can't be found with any strategy
        """
        # Try primary locator first
        try:
            element = self._find_with_locator(primary_locator)
            logger.debug(f"Element found with primary locator: {primary_locator}")
            return element
        except Exception as e:
            logger.warning(f"Primary locator failed: {primary_locator}. Attempting self-heal...")
        
        # Generate alternative locators
        alternatives = self._generate_alternative_locators(primary_locator, context)
        
        # Try alternative locators
        for strategy in alternatives:
            try:
                element = self._find_with_locator(strategy.value)
                logger.info(f"✓ Self-healed! Found element with {strategy.type}: {strategy.value}")
                
                # Update locator cache
                self._update_cache(primary_locator, strategy)
                
                # Record healing
                self.healing_history.append({
                    'original_locator': primary_locator,
                    'healed_locator': strategy.value,
                    'strategy_type': strategy.type,
                    'confidence': strategy.confidence
                })
                
                return element
            except:
                continue
        
        # If still not found, raise exception
        raise ElementNotFoundException(f"Element not found even with self-healing: {primary_locator}")
    
    def _find_with_locator(self, locator: str) -> Any:
        """Find element using locator"""
        if self.engine_type == 'PlaywrightEngine':
            page = self.ui_engine.get_page()
            element = page.locator(locator)
            element.wait_for(state='visible', timeout=5000)
            return element
        elif self.engine_type == 'SeleniumEngine':
            driver = self.ui_engine.get_driver()
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Determine locator type
            if locator.startswith('//'):
                by = By.XPATH
            elif locator.startswith('#'):
                by = By.CSS_SELECTOR
            else:
                by = By.CSS_SELECTOR
            
            element = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((by, locator))
            )
            return element
    
    def _generate_alternative_locators(self, primary_locator: str, 
                                      context: Optional[Dict] = None) -> List[LocatorStrategy]:
        """
        Generate alternative locators using multiple strategies
        
        Args:
            primary_locator: Original locator that failed
            context: Optional context information
        
        Returns:
            List of alternative locator strategies
        """
        alternatives = []
        
        # Check cache first
        if primary_locator in self.locator_cache:
            cached = self.locator_cache[primary_locator]
            alternatives.extend(cached)
            logger.debug(f"Using {len(cached)} cached alternative locators")
        
        # Generate new alternatives based on page analysis
        page_alternatives = self._analyze_page_elements(primary_locator, context)
        alternatives.extend(page_alternatives)
        
        # Sort by confidence
        alternatives.sort(key=lambda x: x.confidence, reverse=True)
        
        return alternatives
    
    def _analyze_page_elements(self, primary_locator: str, 
                               context: Optional[Dict] = None) -> List[LocatorStrategy]:
        """Analyze page to find similar elements"""
        alternatives = []
        
        if self.engine_type != 'PlaywrightEngine':
            return alternatives  # Only supported for Playwright currently
        
        page = self.ui_engine.get_page()
        
        # Get all interactive elements
        all_elements = page.evaluate("""
            () => {
                const elements = Array.from(document.querySelectorAll('button, input, a, select, textarea, [role="button"]'));
                return elements.map(el => ({
                    tag: el.tagName,
                    id: el.id,
                    class: el.className,
                    name: el.name,
                    text: el.textContent?.trim(),
                    type: el.type,
                    ariaLabel: el.getAttribute('aria-label'),
                    placeholder: el.placeholder,
                    role: el.getAttribute('role'),
                    xpath: getXPath(el)
                }));
                
                function getXPath(element) {
                    if (element.id) return `//*[@id="${element.id}"]`;
                    if (element === document.body) return '/html/body';
                    
                    let ix = 0;
                    const siblings = element.parentNode?.children || [];
                    for (let i = 0; i < siblings.length; i++) {
                        const sibling = siblings[i];
                        if (sibling === element) {
                            return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                        }
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) ix++;
                    }
                }
            }
        """)
        
        # Extract key from primary locator
        primary_text = self._extract_text_from_locator(primary_locator)
        
        # Find similar elements
        for element in all_elements:
            confidence = 0.0
            locator = None
            strategy_type = None
            
            # Strategy 1: Match by text similarity
            if element.get('text') and primary_text:
                similarity = difflib.SequenceMatcher(None, element['text'].lower(), primary_text.lower()).ratio()
                if similarity > 0.7:
                    confidence = similarity
                    locator = f"text={element['text']}"
                    strategy_type = 'text'
            
            # Strategy 2: Match by ID
            if element.get('id'):
                if primary_text and primary_text.lower() in element['id'].lower():
                    confidence = max(confidence, 0.9)
                    locator = f"#{element['id']}"
                    strategy_type = 'id'
            
            # Strategy 3: Match by aria-label
            if element.get('ariaLabel'):
                if primary_text and difflib.SequenceMatcher(None, element['ariaLabel'].lower(), primary_text.lower()).ratio() > 0.7:
                    confidence = max(confidence, 0.85)
                    locator = f"[aria-label='{element['ariaLabel']}']"
                    strategy_type = 'aria-label'
            
            # Strategy 4: Match by name attribute
            if element.get('name'):
                if primary_text and primary_text.lower() in element['name'].lower():
                    confidence = max(confidence, 0.8)
                    locator = f"[name='{element['name']}']"
                    strategy_type = 'name'
            
            # Strategy 5: Match by placeholder
            if element.get('placeholder'):
                if primary_text and difflib.SequenceMatcher(None, element['placeholder'].lower(), primary_text.lower()).ratio() > 0.7:
                    confidence = max(confidence, 0.75)
                    locator = f"[placeholder='{element['placeholder']}']"
                    strategy_type = 'placeholder'
            
            # Strategy 6: Use XPath as fallback
            if confidence > 0 and not locator and element.get('xpath'):
                locator = element['xpath']
                strategy_type = 'xpath'
                confidence *= 0.6  # Lower confidence for XPath
            
            if locator and confidence > 0.6:
                alternatives.append(LocatorStrategy(
                    type=strategy_type,
                    value=locator,
                    confidence=confidence
                ))
        
        logger.debug(f"Generated {len(alternatives)} alternative locators")
        return alternatives
    
    def _extract_text_from_locator(self, locator: str) -> str:
        """Extract searchable text from locator"""
        # Handle common locator patterns
        if 'text=' in locator:
            return locator.split('text=')[1].strip('"\'')
        elif '[' in locator and ']' in locator:
            # Extract attribute value
            import re
            match = re.search(r'["\']([^"\']+)["\']', locator)
            if match:
                return match.group(1)
        elif '#' in locator:
            return locator.replace('#', '')
        
        return locator
    
    def _update_cache(self, primary_locator: str, successful_strategy: LocatorStrategy):
        """Update locator cache with successful alternative"""
        if primary_locator not in self.locator_cache:
            self.locator_cache[primary_locator] = []
        
        # Add to cache if not already present
        existing = [s for s in self.locator_cache[primary_locator] if s.value == successful_strategy.value]
        if not existing:
            self.locator_cache[primary_locator].insert(0, successful_strategy)
        
        # Keep only top 5 alternatives
        self.locator_cache[primary_locator] = self.locator_cache[primary_locator][:5]
    
    def get_healing_report(self) -> Dict[str, Any]:
        """Get self-healing statistics"""
        total_heals = len(self.healing_history)
        
        if total_heals == 0:
            return {
                'total_heals': 0,
                'success_rate': 0,
                'most_common_strategy': None
            }
        
        # Count strategy usage
        strategy_counts = {}
        for heal in self.healing_history:
            strategy = heal['strategy_type']
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        most_common = max(strategy_counts.items(), key=lambda x: x[1]) if strategy_counts else (None, 0)
        
        return {
            'total_heals': total_heals,
            'cached_locators': len(self.locator_cache),
            'strategy_usage': strategy_counts,
            'most_common_strategy': most_common[0],
            'healing_history': self.healing_history
        }
    
    def clear_cache(self):
        """Clear locator cache"""
        self.locator_cache.clear()
        logger.info("Locator cache cleared")


class ElementNotFoundException(Exception):
    """Element not found exception"""
    pass


__all__ = ['SelfHealingLocators', 'LocatorStrategy', 'ElementNotFoundException']
