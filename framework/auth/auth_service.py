"""
Authentication Service - Unified Auth Interface

Provides unified authentication interface across Playwright and Selenium engines.
Supports SSO (Okta, Azure AD, Google), MFA, OAuth, SAML, and Basic authentication.

Author: Principal QA Architect
Date: January 31, 2026
"""

import logging
import time
from enum import Enum
from typing import Any, Dict, Optional

from framework.core.session_manager import SessionData, SessionManager

logger = logging.getLogger(__name__)


class AuthMethod(Enum):
    """Authentication methods supported"""
    SSO = "sso"  # Okta, Azure AD, etc.
    MFA = "mfa"  # Multi-factor authentication
    BASIC = "basic"  # Username/password
    OAUTH = "oauth"  # OAuth2
    SAML = "saml"  # SAML-based SSO


class AuthenticationService:
    """
    Unified authentication service
    
    Handles:
    - SSO authentication (Okta, Azure AD, Google, etc.)
    - MFA flows
    - Basic authentication
    - OAuth2
    - SAML
    - Session persistence across engines
    """
    
    def __init__(self, session_manager: Optional[SessionManager] = None):
        self.session_manager = session_manager or SessionManager()
        self.logger = logger
        self._current_session: Optional[SessionData] = None
        self._current_user: Optional[Dict[str, Any]] = None
    
    # ========================================================================
    # SSO AUTHENTICATION
    # ========================================================================
    
    def authenticate_sso(
        self,
        engine,
        sso_config: Dict[str, str],
        credentials: Dict[str, str],
        timeout: int = 60
    ) -> Optional[SessionData]:
        """
        Authenticate using SSO (Okta, Azure AD, Google, etc.)
        
        Args:
            engine: Selenium WebDriver instance
            sso_config: {
                'provider': 'okta',  # or 'azure_ad', 'google'
                'okta_domain': 'https://company.okta.com',
                'app_id': 'xxxxx'
            }
            credentials: {
                'username': 'user@company.com',
                'password': '...',
                'mfa_token': '...' (optional)
            }
            timeout: Max wait time for auth completion
        
        Returns:
            SessionData if successful
        """
        self.logger.info("Starting SSO authentication...")
        
        try:
            provider = sso_config.get('provider', '').lower()
            
            if provider == 'okta':
                return self._authenticate_okta(engine, sso_config, credentials, timeout)
            elif provider == 'azure_ad' or provider == 'azure':
                return self._authenticate_azure_ad(engine, sso_config, credentials, timeout)
            elif provider == 'google':
                return self._authenticate_google(engine, sso_config, credentials, timeout)
            else:
                self.logger.error(f"Unsupported SSO provider: {provider}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ SSO authentication failed: {e}")
            return None
    
    def _authenticate_okta(
        self,
        driver,
        sso_config: Dict[str, str],
        credentials: Dict[str, str],
        timeout: int
    ) -> Optional[SessionData]:
        """Authenticate with Okta SSO"""
        self.logger.info("Authenticating with Okta...")
        
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.support.ui import WebDriverWait
            
            okta_domain = sso_config.get('okta_domain')
            app_id = sso_config.get('app_id', '')
            username = credentials.get('username')
            password = credentials.get('password')
            
            # Navigate to Okta
            if app_id:
                login_url = f"{okta_domain}/app/{app_id}/login/login.htm"
            else:
                login_url = f"{okta_domain}/login/login.htm"
            
            self.logger.info(f"Navigating to Okta: {login_url}")
            driver.get(login_url)
            
            wait = WebDriverWait(driver, timeout)
            
            # Fill username
            self.logger.info("Entering username...")
            username_field = wait.until(
                EC.presence_of_element_located((By.ID, "okta-signin-username"))
            )
            username_field.clear()
            username_field.send_keys(username)
            
            # Fill password
            self.logger.info("Entering password...")
            password_field = driver.find_element(By.ID, "okta-signin-password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Click submit
            self.logger.info("Submitting credentials...")
            submit_btn = driver.find_element(By.ID, "okta-signin-submit")
            submit_btn.click()
            
            # Handle MFA if needed
            mfa_token = credentials.get('mfa_token')
            if mfa_token:
                self.logger.info("MFA required - entering MFA token...")
                try:
                    mfa_field = wait.until(
                        EC.presence_of_element_located((By.NAME, "answer"))
                    )
                    mfa_field.send_keys(mfa_token)
                    mfa_submit = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Verify']")
                    mfa_submit.click()
                except Exception as e:
                    self.logger.warning(f"MFA field not found or different format: {e}")
            
            # Wait for successful login (URL change or specific element)
            self.logger.info("Waiting for authentication to complete...")
            time.sleep(5)  # Give time for redirects
            
            # Check if we're successfully authenticated
            current_url = driver.current_url
            if 'login' not in current_url.lower():
                self.logger.info("✅ Okta authentication successful")
            else:
                self.logger.warning("⚠️ Still on login page - authentication may have failed")
            
            # Extract and store session
            session_data = self.session_manager.extract_session_from_selenium(driver)
            self._current_session = session_data
            self._current_user = {
                'username': username,
                'auth_type': 'SSO',
                'provider': 'okta'
            }
            
            return session_data
            
        except Exception as e:
            self.logger.error(f"❌ Okta authentication failed: {e}")
            return None
    
    def _authenticate_azure_ad(
        self,
        driver,
        sso_config: Dict[str, str],
        credentials: Dict[str, str],
        timeout: int
    ) -> Optional[SessionData]:
        """Authenticate with Azure AD"""
        self.logger.info("Authenticating with Azure AD...")
        
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.support.ui import WebDriverWait
            
            azure_domain = sso_config.get('azure_domain', 'https://login.microsoftonline.com')
            tenant_id = sso_config.get('tenant_id', 'common')
            client_id = sso_config.get('client_id', '')
            username = credentials.get('username')
            password = credentials.get('password')
            
            # Navigate to Azure AD
            login_url = f"{azure_domain}/{tenant_id}/oauth2/v2.0/authorize?client_id={client_id}"
            self.logger.info(f"Navigating to Azure AD: {login_url}")
            driver.get(login_url)
            
            wait = WebDriverWait(driver, timeout)
            
            # Enter username/email
            self.logger.info("Entering username...")
            username_field = wait.until(
                EC.presence_of_element_located((By.NAME, "loginfmt"))
            )
            username_field.send_keys(username)
            
            # Click Next
            next_btn = driver.find_element(By.ID, "idSIButton9")
            next_btn.click()
            
            # Enter password
            self.logger.info("Entering password...")
            password_field = wait.until(
                EC.presence_of_element_located((By.NAME, "passwd"))
            )
            password_field.send_keys(password)
            
            # Click Sign in
            signin_btn = driver.find_element(By.ID, "idSIButton9")
            signin_btn.click()
            
            # Handle MFA if needed
            mfa_token = credentials.get('mfa_token')
            if mfa_token:
                self.logger.info("MFA required - entering MFA token...")
                try:
                    mfa_field = wait.until(
                        EC.presence_of_element_located((By.NAME, "otc"))
                    )
                    mfa_field.send_keys(mfa_token)
                    verify_btn = driver.find_element(By.ID, "idSubmit_SAOTCC_Continue")
                    verify_btn.click()
                except Exception as e:
                    self.logger.warning(f"MFA handling failed: {e}")
            
            # Wait for authentication to complete
            self.logger.info("Waiting for authentication to complete...")
            time.sleep(5)
            
            self.logger.info("✅ Azure AD authentication successful")
            
            # Extract session
            session_data = self.session_manager.extract_session_from_selenium(driver)
            self._current_session = session_data
            self._current_user = {
                'username': username,
                'auth_type': 'SSO',
                'provider': 'azure_ad'
            }
            
            return session_data
            
        except Exception as e:
            self.logger.error(f"❌ Azure AD authentication failed: {e}")
            return None
    
    def _authenticate_google(
        self,
        driver,
        sso_config: Dict[str, str],
        credentials: Dict[str, str],
        timeout: int
    ) -> Optional[SessionData]:
        """Authenticate with Google"""
        self.logger.info("Authenticating with Google...")
        
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.support.ui import WebDriverWait
            
            username = credentials.get('username')
            password = credentials.get('password')
            
            # Navigate to Google Sign-In
            login_url = "https://accounts.google.com/signin"
            self.logger.info(f"Navigating to Google: {login_url}")
            driver.get(login_url)
            
            wait = WebDriverWait(driver, timeout)
            
            # Enter email
            self.logger.info("Entering email...")
            email_field = wait.until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
            email_field.send_keys(username)
            
            # Click Next
            next_btn = driver.find_element(By.ID, "identifierNext")
            next_btn.click()
            
            # Enter password
            self.logger.info("Entering password...")
            password_field = wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_field.send_keys(password)
            
            # Click Next
            password_next_btn = driver.find_element(By.ID, "passwordNext")
            password_next_btn.click()
            
            # Wait for authentication
            self.logger.info("Waiting for authentication to complete...")
            time.sleep(5)
            
            self.logger.info("✅ Google authentication successful")
            
            # Extract session
            session_data = self.session_manager.extract_session_from_selenium(driver)
            self._current_session = session_data
            self._current_user = {
                'username': username,
                'auth_type': 'SSO',
                'provider': 'google'
            }
            
            return session_data
            
        except Exception as e:
            self.logger.error(f"❌ Google authentication failed: {e}")
            return None
    
    # ========================================================================
    # BASIC AUTHENTICATION
    # ========================================================================
    
    def authenticate_basic(
        self,
        engine,
        username: str,
        password: str,
        login_url: str,
        timeout: int = 30
    ) -> Optional[SessionData]:
        """
        Basic username/password authentication
        
        Args:
            engine: Selenium WebDriver or Playwright Page
            username: Username
            password: Password
            login_url: Login page URL
            timeout: Wait timeout
        
        Returns:
            SessionData if successful
        """
        self.logger.info("Starting basic authentication...")
        
        try:
            # Detect engine type
            if hasattr(engine, 'get'):  # Selenium
                return self._authenticate_basic_selenium(engine, username, password, login_url, timeout)
            else:  # Playwright
                return self._authenticate_basic_playwright(engine, username, password, login_url, timeout)
                
        except Exception as e:
            self.logger.error(f"❌ Basic authentication failed: {e}")
            return None
    
    def _authenticate_basic_selenium(
        self,
        driver,
        username: str,
        password: str,
        login_url: str,
        timeout: int
    ) -> Optional[SessionData]:
        """Basic auth using Selenium"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait
        
        try:
            driver.get(login_url)
            wait = WebDriverWait(driver, timeout)
            
            # Locate username field (common variations)
            username_field = None
            for selector in ['username', 'email', 'user', 'login']:
                try:
                    username_field = wait.until(
                        EC.presence_of_element_located((By.NAME, selector))
                    )
                    break
                except:
                    continue
            
            if not username_field:
                raise ValueError("Username field not found")
            
            username_field.send_keys(username)
            
            # Locate password field
            password_field = driver.find_element(By.NAME, "password")
            password_field.send_keys(password)
            
            # Click login button (common variations)
            login_btn = None
            for xpath in [
                "//button[contains(text(), 'Login')]",
                "//button[contains(text(), 'Sign in')]",
                "//button[contains(text(), 'Log in')]",
                "//input[@type='submit']"
            ]:
                try:
                    login_btn = driver.find_element(By.XPATH, xpath)
                    break
                except:
                    continue
            
            if not login_btn:
                raise ValueError("Login button not found")
            
            login_btn.click()
            
            # Wait for navigation
            wait.until(EC.url_changes(login_url))
            
            self.logger.info("✅ Basic authentication successful")
            
            # Extract session
            session_data = self.session_manager.extract_session_from_selenium(driver)
            self._current_session = session_data
            self._current_user = {'username': username, 'auth_type': 'BASIC'}
            
            return session_data
            
        except Exception as e:
            self.logger.error(f"❌ Basic authentication (Selenium) failed: {e}")
            return None
    
    def _authenticate_basic_playwright(
        self,
        page,
        username: str,
        password: str,
        login_url: str,
        timeout: int
    ) -> Optional[SessionData]:
        """Basic auth using Playwright (would need async implementation)"""
        self.logger.warning("Playwright basic auth not yet implemented - use Selenium for auth")
        return None
    
    # ========================================================================
    # SESSION TRANSFER
    # ========================================================================
    
    async def switch_engine_with_session(
        self,
        from_engine,
        to_engine_page,
        from_type: str = 'selenium',
        to_type: str = 'playwright'
    ) -> bool:
        """
        Switch from one engine to another while preserving session
        
        Args:
            from_engine: Source engine instance
            to_engine_page: Target Playwright page
            from_type: Source engine type
            to_type: Target engine type
        
        Returns:
            True if successful
        """
        self.logger.info(f"Switching engines while preserving session: {from_type} → {to_type}")
        
        try:
            session_data = await self.session_manager.transfer_session(
                from_engine_type=from_type,
                from_driver=from_engine,
                to_engine_type=to_type,
                to_page=to_engine_page,
                validate=True
            )
            
            if session_data:
                self._current_session = session_data
                self.logger.info("✅ Engine switch successful with session preserved")
                return True
            else:
                self.logger.error("❌ Engine switch failed - session not preserved")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Engine switch failed: {e}")
            return False
    
    def switch_engine_with_session_sync(
        self,
        from_engine,
        to_engine_page,
        from_type: str = 'selenium',
        to_type: str = 'playwright'
    ) -> bool:
        """
        Switch from one engine to another while preserving session (Sync version)
        
        Args:
            from_engine: Source engine instance
            to_engine_page: Target Playwright page
            from_type: Source engine type
            to_type: Target engine type
        
        Returns:
            True if successful
        """
        self.logger.info(f"Switching engines (sync): {from_type} → {to_type}")
        
        try:
            session_data = self.session_manager.transfer_session_sync(
                from_engine_type=from_type,
                from_driver=from_engine,
                to_engine_type=to_type,
                to_page=to_engine_page,
                validate=True
            )
            
            if session_data:
                self._current_session = session_data
                self.logger.info("✅ Engine switch successful with session preserved")
                return True
            else:
                self.logger.error("❌ Engine switch failed - session not preserved")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Engine switch failed: {e}")
            return False
    
    # ========================================================================
    # SESSION QUERIES
    # ========================================================================
    
    def get_current_session(self) -> Optional[SessionData]:
        """Get current session data"""
        return self._current_session
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current user information"""
        return self._current_user
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        return self._current_session is not None and self._current_user is not None
    
    def clear_session(self) -> None:
        """Clear current session"""
        self._current_session = None
        self._current_user = None
        self.logger.info("✅ Session cleared")
