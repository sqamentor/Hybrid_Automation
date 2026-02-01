"""
Multi-Language Support - Internationalization (i18n) Testing

Provides multi-language test data generation and localization testing support.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class MultiLanguageSupport:
    """Multi-language testing support"""
    
    # Common languages with locale codes
    LANGUAGES = {
        'en': {'name': 'English', 'locale': 'en-US'},
        'es': {'name': 'Spanish', 'locale': 'es-ES'},
        'fr': {'name': 'French', 'locale': 'fr-FR'},
        'de': {'name': 'German', 'locale': 'de-DE'},
        'it': {'name': 'Italian', 'locale': 'it-IT'},
        'pt': {'name': 'Portuguese', 'locale': 'pt-BR'},
        'zh': {'name': 'Chinese', 'locale': 'zh-CN'},
        'ja': {'name': 'Japanese', 'locale': 'ja-JP'},
        'ko': {'name': 'Korean', 'locale': 'ko-KR'},
        'ar': {'name': 'Arabic', 'locale': 'ar-SA'},
        'hi': {'name': 'Hindi', 'locale': 'hi-IN'},
        'ru': {'name': 'Russian', 'locale': 'ru-RU'}
    }
    
    def __init__(self, translations_dir: str = "tests/data/translations"):
        """
        Initialize multi-language support
        
        Args:
            translations_dir: Directory containing translation files
        """
        self.translations_dir = Path(translations_dir)
        self.translations: Dict[str, Dict[str, str]] = {}
        self.current_language = 'en'
        self.load_translations()
    
    def load_translations(self):
        """Load translation files"""
        if not self.translations_dir.exists():
            logger.warning(f"Translations directory not found: {self.translations_dir}")
            return
        
        for lang_code in self.LANGUAGES.keys():
            lang_file = self.translations_dir / f"{lang_code}.json"
            if lang_file.exists():
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
                logger.debug(f"Loaded translations for: {lang_code}")
    
    def set_language(self, lang_code: str):
        """
        Set current language
        
        Args:
            lang_code: Language code (e.g., 'en', 'es', 'fr')
        """
        if lang_code not in self.LANGUAGES:
            raise ValueError(f"Unsupported language: {lang_code}")
        
        self.current_language = lang_code
        logger.info(f"Language set to: {self.LANGUAGES[lang_code]['name']}")
    
    def get_text(self, key: str, lang_code: Optional[str] = None) -> str:
        """
        Get translated text
        
        Args:
            key: Translation key
            lang_code: Language code (uses current if not specified)
        
        Returns:
            Translated text
        """
        lang = lang_code or self.current_language
        
        if lang not in self.translations:
            logger.warning(f"No translations loaded for: {lang}")
            return key
        
        return self.translations[lang].get(key, key)
    
    def get_all_translations(self, key: str) -> Dict[str, str]:
        """
        Get text in all languages
        
        Args:
            key: Translation key
        
        Returns:
            Dictionary of language_code: translated_text
        """
        return {
            lang: self.translations[lang].get(key, key)
            for lang in self.translations
        }
    
    def generate_test_data(self, data_type: str, lang_code: Optional[str] = None) -> Any:
        """
        Generate language-specific test data
        
        Args:
            data_type: Data type ('name', 'email', 'address', 'phone', 'text')
            lang_code: Language code
        
        Returns:
            Generated test data
        """
        lang = lang_code or self.current_language
        
        # Import faker for data generation
        try:
            from faker import Faker
            fake = Faker(self.LANGUAGES[lang]['locale'])
        except ImportError:
            logger.warning("Faker library not installed. Using default data.")
            return f"test_{data_type}"
        
        generators = {
            'name': fake.name,
            'email': fake.email,
            'address': fake.address,
            'phone': fake.phone_number,
            'text': fake.text,
            'company': fake.company,
            'city': fake.city,
            'country': fake.country,
            'postcode': fake.postcode
        }
        
        generator = generators.get(data_type)
        if generator:
            return generator()
        
        return f"test_{data_type}"
    
    def set_browser_language(self, ui_engine, lang_code: str):
        """
        Set browser language preference
        
        Args:
            ui_engine: UI engine instance
            lang_code: Language code
        """
        locale = self.LANGUAGES[lang_code]['locale']
        engine_type = type(ui_engine).__name__
        
        if engine_type == 'PlaywrightEngine':
            # For Playwright, set locale in browser context
            context = ui_engine.context
            if hasattr(context, 'set_extra_http_headers'):
                context.set_extra_http_headers({
                    'Accept-Language': locale
                })
            logger.info(f"Browser language set to: {locale}")
        
        elif engine_type == 'SeleniumEngine':
            # For Selenium, this should be set during browser initialization
            logger.warning("Browser language must be set during browser initialization for Selenium")
    
    def verify_translations_exist(self, keys: List[str], languages: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """
        Verify translation keys exist in specified languages
        
        Args:
            keys: List of translation keys to check
            languages: Languages to check (default: all)
        
        Returns:
            Dictionary of missing translations by language
        """
        check_langs = languages or list(self.translations.keys())
        missing = {}
        
        for lang in check_langs:
            if lang not in self.translations:
                missing[lang] = keys
                continue
            
            lang_missing = []
            for key in keys:
                if key not in self.translations[lang]:
                    lang_missing.append(key)
            
            if lang_missing:
                missing[lang] = lang_missing
        
        if missing:
            logger.warning(f"Missing translations found in {len(missing)} languages")
        else:
            logger.info("All translations verified")
        
        return missing
    
    def test_text_rendering(self, ui_engine, element_locator: str, expected_key: str) -> Dict[str, bool]:
        """
        Test text rendering in multiple languages
        
        Args:
            ui_engine: UI engine instance
            element_locator: Element locator
            expected_key: Expected translation key
        
        Returns:
            Dictionary of language: test_passed
        """
        results = {}
        
        for lang_code in self.translations.keys():
            # Set language
            self.set_language(lang_code)
            self.set_browser_language(ui_engine, lang_code)
            
            # Refresh page to apply language
            ui_engine.refresh()
            
            # Get expected text
            expected_text = self.get_text(expected_key)
            
            # Get actual text
            try:
                actual_text = ui_engine.get_text(element_locator)
                results[lang_code] = (actual_text == expected_text)
                
                if not results[lang_code]:
                    logger.warning(
                        f"Text mismatch in {lang_code}: "
                        f"expected '{expected_text}', got '{actual_text}'"
                    )
            except Exception as e:
                logger.error(f"Error testing {lang_code}: {e}")
                results[lang_code] = False
        
        return results
    
    def generate_sample_translations(self, output_dir: Optional[str] = None):
        """Generate sample translation files"""
        output_path = Path(output_dir) if output_dir else self.translations_dir
        output_path.mkdir(parents=True, exist_ok=True)
        
        sample_translations = {
            'app.title': 'Application Title',
            'login.button': 'Log In',
            'logout.button': 'Log Out',
            'search.placeholder': 'Search...',
            'save.button': 'Save',
            'cancel.button': 'Cancel',
            'welcome.message': 'Welcome!',
            'error.generic': 'An error occurred',
            'success.message': 'Operation completed successfully'
        }
        
        # Generate for each language (using sample data)
        for lang_code, lang_info in self.LANGUAGES.items():
            # In real scenario, these would be translated
            # For now, we'll just add language suffix
            lang_translations = {
                key: f"{value} [{lang_code.upper()}]"
                for key, value in sample_translations.items()
            }
            
            output_file = output_path / f"{lang_code}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(lang_translations, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Generated sample translations: {output_file}")


class RTLTesting:
    """Right-to-Left (RTL) language testing support"""
    
    RTL_LANGUAGES = ['ar', 'he', 'fa', 'ur']
    
    @staticmethod
    def is_rtl(lang_code: str) -> bool:
        """Check if language is RTL"""
        return lang_code in RTLTesting.RTL_LANGUAGES
    
    @staticmethod
    def verify_rtl_layout(ui_engine, lang_code: str) -> bool:
        """
        Verify page has RTL layout for RTL languages
        
        Args:
            ui_engine: UI engine instance
            lang_code: Language code
        
        Returns:
            True if layout is correct
        """
        if not RTLTesting.is_rtl(lang_code):
            return True  # Not RTL language
        
        # Check HTML dir attribute
        engine_type = type(ui_engine).__name__
        
        if engine_type == 'PlaywrightEngine':
            page = ui_engine.get_page()
            dir_attr = page.evaluate("document.documentElement.dir")
            has_rtl_dir = (dir_attr == 'rtl')
            
            if not has_rtl_dir:
                logger.warning(f"RTL language {lang_code} but HTML dir attribute is not 'rtl'")
            
            return has_rtl_dir
        
        return True  # Can't verify for other engines


__all__ = ['MultiLanguageSupport', 'RTLTesting']
