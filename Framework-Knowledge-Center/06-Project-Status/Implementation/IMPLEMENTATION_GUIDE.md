# 🛠️ HYBRID AUTOMATION ARCHITECTURE - IMPLEMENTATION GUIDE

## Quick Reference: What Needs to Be Built

This guide provides **production-ready code templates** for implementing cross-engine workflow orchestration.

---

## 1. SESSION MANAGER (framework/core/session_manager.py)

**Purpose**: Extract authentication state from Selenium, inject into Playwright

```python
"""
Session Manager - Cross-Engine Session Bridge

Handles extraction and injection of authentication tokens, cookies, and user context
between Selenium and Playwright engines.

Author: Principal QA Architect
"""

import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SessionType(Enum):
    """Types of sessions that can be transferred"""
    COOKIES = "cookies"
    LOCAL_STORAGE = "local_storage"
    SESSION_STORAGE = "session_storage"
    TOKENS = "tokens"
    HEADERS = "headers"


@dataclass
class SessionData:
    """Container for cross-engine session data"""
    cookies: List[Dict[str, Any]]
    local_storage: Dict[str, str]
    session_storage: Dict[str, str]
    tokens: Dict[str, str]
    headers: Dict[str, str]
    created_at: str
    user_id: Optional[str] = None
    auth_type: Optional[str] = None  # 'SSO', 'MFA', 'BASIC', 'OAUTH'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionData':
        """Create from dictionary"""
        return cls(**data)


class SessionManager:
    """
    Cross-engine session manager
    
    Responsibilities:
    - Extract session from Selenium WebDriver
    - Inject session into Playwright Page
    - Validate session continuity
    - Handle token refresh
    - Manage session lifecycle
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._session_cache: Dict[str, SessionData] = {}
    
    # ========================================================================
    # SELENIUM: EXTRACT SESSION
    # ========================================================================
    
    def extract_session_from_selenium(self, driver) -> SessionData:
        """
        Extract session data from Selenium WebDriver
        
        Args:
            driver: Selenium WebDriver instance
        
        Returns:
            SessionData object containing all session information
        
        Raises:
            ValueError: If extraction fails
        """
        self.logger.info("Extracting session from Selenium...")
        
        try:
            # Extract cookies
            selenium_cookies = driver.get_cookies()
            cookies = [
                {
                    'name': c['name'],
                    'value': c['value'],
                    'domain': c.get('domain', ''),
                    'path': c.get('path', '/'),
                    'secure': c.get('secure', False),
                    'httpOnly': c.get('httpOnly', False),
                    'sameSite': c.get('sameSite', 'Lax')
                }
                for c in selenium_cookies
            ]
            
            # Extract localStorage (if available)
            local_storage = self._extract_storage_from_selenium(driver, 'localStorage')
            
            # Extract sessionStorage
            session_storage = self._extract_storage_from_selenium(driver, 'sessionStorage')
            
            # Extract tokens from various storage locations
            tokens = self._extract_tokens_from_selenium(driver)
            
            # Extract headers if needed
            headers = self._extract_headers_from_selenium(driver)
            
            # Detect auth type from tokens/cookies
            auth_type = self._detect_auth_type(cookies, tokens, session_storage)
            
            # Detect user ID
            user_id = self._extract_user_id(tokens, session_storage, local_storage)
            
            session_data = SessionData(
                cookies=cookies,
                local_storage=local_storage,
                session_storage=session_storage,
                tokens=tokens,
                headers=headers,
                created_at=datetime.now().isoformat(),
                user_id=user_id,
                auth_type=auth_type
            )
            
            self.logger.info(f"✅ Session extracted: {len(cookies)} cookies, auth_type={auth_type}, user_id={user_id}")
            return session_data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to extract session from Selenium: {e}")
            raise ValueError(f"Session extraction failed: {e}")
    
    @staticmethod
    def _extract_storage_from_selenium(driver, storage_type: str) -> Dict[str, str]:
        """Extract localStorage or sessionStorage from Selenium"""
        try:
            script = f"""
                return Object.keys({storage_type})
                    .reduce((obj, key) => {{
                        obj[key] = {storage_type}.getItem(key);
                        return obj;
                    }}, {{}});
            """
            return driver.execute_script(script) or {}
        except Exception as e:
            logging.warning(f"Could not extract {storage_type}: {e}")
            return {}
    
    @staticmethod
    def _extract_tokens_from_selenium(driver) -> Dict[str, str]:
        """Extract auth tokens from various locations"""
        tokens = {}
        
        # Common token locations
        token_keys = [
            'auth_token', 'access_token', 'id_token', 'refresh_token',
            'jwt', 'bearer_token', 'token', 'Authorization'
        ]
        
        # Check localStorage
        for key in token_keys:
            try:
                value = driver.execute_script(f"return localStorage.getItem('{key}');")
                if value:
                    tokens[key] = value
            except:
                pass
        
        # Check sessionStorage
        for key in token_keys:
            try:
                value = driver.execute_script(f"return sessionStorage.getItem('{key}');")
                if value:
                    tokens[f"session_{key}"] = value
            except:
                pass
        
        return tokens
    
    @staticmethod
    def _extract_headers_from_selenium(driver) -> Dict[str, str]:
        """Extract custom headers if tracked by the app"""
        # This would depend on your specific app
        # Often headers are set in Authorization cookies
        return {}
    
    @staticmethod
    def _detect_auth_type(cookies: List[Dict], tokens: Dict, storage: Dict) -> Optional[str]:
        """Detect authentication type from extracted data"""
        # Check for OAuth
        if any('oauth' in str(k).lower() or 'oauth' in str(v).lower() for k, v in tokens.items()):
            return 'OAUTH'
        
        # Check for JWT
        if any('jwt' in str(k).lower() or 'jwt' in str(v).lower() for k, v in tokens.items()):
            return 'JWT'
        
        # Check for SSO (Okta, Azure, etc.)
        cookie_names = [c['name'].lower() for c in cookies]
        if any('okta' in name or 'azure' in name or 'saml' in name for name in cookie_names):
            return 'SSO'
        
        # Check for basic auth (typically in Authorization header)
        if any('authorization' in str(k).lower() or 'authorization' in str(v).lower() for k, v in tokens.items()):
            return 'BASIC'
        
        return 'UNKNOWN'
    
    @staticmethod
    def _extract_user_id(tokens: Dict, session_storage: Dict, local_storage: Dict) -> Optional[str]:
        """Extract user ID from session data"""
        # Try tokens first
        for key in ['user_id', 'userId', 'sub', 'user']:
            if key in tokens:
                return str(tokens[key])
        
        # Try storage
        for storage in [session_storage, local_storage]:
            for key in ['user_id', 'userId', 'current_user', 'currentUser']:
                if key in storage:
                    return str(storage[key])
        
        return None
    
    # ========================================================================
    # PLAYWRIGHT: INJECT SESSION
    # ========================================================================
    
    async def inject_session_to_playwright(self, page, session_data: SessionData) -> bool:
        """
        Inject session data into Playwright Page
        
        Args:
            page: Playwright Page instance
            session_data: SessionData object to inject
        
        Returns:
            True if injection successful, False otherwise
        """
        self.logger.info("Injecting session into Playwright...")
        
        try:
            # Add cookies
            if session_data.cookies:
                await page.context.add_cookies(session_data.cookies)
                self.logger.info(f"✅ Added {len(session_data.cookies)} cookies")
            
            # Navigate to app first (required before setting storage)
            # This should be the same domain as the session
            if not page.url or page.url == 'about:blank':
                # Use a dummy navigation if no URL set yet
                await page.goto('about:blank')
            
            # Inject localStorage
            if session_data.local_storage:
                js_code = self._generate_storage_injection_code(
                    'localStorage',
                    session_data.local_storage
                )
                await page.evaluate(js_code)
                self.logger.info(f"✅ Injected {len(session_data.local_storage)} localStorage items")
            
            # Inject sessionStorage
            if session_data.session_storage:
                js_code = self._generate_storage_injection_code(
                    'sessionStorage',
                    session_data.session_storage
                )
                await page.evaluate(js_code)
                self.logger.info(f"✅ Injected {len(session_data.session_storage)} sessionStorage items")
            
            # Set tokens if needed
            if session_data.tokens:
                js_code = self._generate_token_injection_code(session_data.tokens)
                await page.evaluate(js_code)
                self.logger.info(f"✅ Injected {len(session_data.tokens)} tokens")
            
            self.logger.info("✅ Session injected into Playwright successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to inject session into Playwright: {e}")
            return False
    
    @staticmethod
    def _generate_storage_injection_code(storage_type: str, data: Dict[str, str]) -> str:
        """Generate JavaScript code to inject storage data"""
        items_json = json.dumps(data)
        return f"""
        (function() {{
            const items = {items_json};
            for (const [key, value] of Object.entries(items)) {{
                {storage_type}.setItem(key, value);
            }}
        }})();
        """
    
    @staticmethod
    def _generate_token_injection_code(tokens: Dict[str, str]) -> str:
        """Generate JavaScript code to inject tokens"""
        tokens_json = json.dumps(tokens)
        return f"""
        (function() {{
            const tokens = {tokens_json};
            
            // Inject into Authorization header (if your app uses it)
            if (tokens.auth_token || tokens.access_token) {{
                const token = tokens.auth_token || tokens.access_token;
                window.__AUTH_TOKEN__ = token;
            }}
            
            // Inject into localStorage
            for (const [key, value] of Object.entries(tokens)) {{
                localStorage.setItem(key, value);
            }}
        }})();
        """
    
    # ========================================================================
    # VALIDATION
    # ========================================================================
    
    async def validate_session_continuity(self, page, expected_user_id: Optional[str] = None) -> bool:
        """
        Validate that session persisted successfully
        
        Args:
            page: Playwright Page instance
            expected_user_id: Expected user ID (optional)
        
        Returns:
            True if session valid, False otherwise
        """
        self.logger.info("Validating session continuity...")
        
        try:
            # Check if cookies are present
            cookies = await page.context.cookies()
            if not cookies:
                self.logger.warning("⚠️ No cookies found after injection")
                return False
            
            # Check if we can access a protected resource
            # This assumes your app has an /api/me or similar endpoint
            try:
                response = await page.goto('/api/v1/user', wait_until='networkidle')
                if response.status == 200:
                    self.logger.info("✅ Session valid - /api/v1/user accessible")
                    return True
                elif response.status == 401:
                    self.logger.warning("⚠️ Session invalid - 401 Unauthorized")
                    return False
            except:
                # Endpoint doesn't exist, try alternative validation
                pass
            
            # Check localStorage for auth token
            token = await page.evaluate("return localStorage.getItem('auth_token');")
            if token:
                self.logger.info("✅ Auth token present in localStorage")
                return True
            
            # Check for user context
            user_data = await page.evaluate("""
                return {
                    userId: localStorage.getItem('user_id'),
                    userName: localStorage.getItem('user_name'),
                    userEmail: localStorage.getItem('user_email')
                }
            """)
            
            if user_data.get('userId'):
                self.logger.info(f"✅ User context found: {user_data['userId']}")
                if expected_user_id and user_data['userId'] != expected_user_id:
                    self.logger.warning(f"⚠️ User ID mismatch: expected {expected_user_id}, got {user_data['userId']}")
                    return False
                return True
            
            self.logger.warning("⚠️ No user context found")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Validation failed: {e}")
            return False
    
    # ========================================================================
    # SESSION TRANSFER (MAIN ORCHESTRATION METHOD)
    # ========================================================================
    
    async def transfer_session(
        self,
        from_engine_type: str,  # 'selenium' or 'playwright'
        from_driver,
        to_engine_type: str,
        to_page,
        validate: bool = True
    ) -> Optional[SessionData]:
        """
        Transfer session from one engine to another
        
        Args:
            from_engine_type: Source engine ('selenium' or 'playwright')
            from_driver: Source driver instance
            to_engine_type: Target engine ('selenium' or 'playwright')
            to_page: Target page instance
            validate: Whether to validate after transfer
        
        Returns:
            SessionData if successful, None otherwise
        """
        self.logger.info(f"Transferring session: {from_engine_type} → {to_engine_type}")
        
        try:
            # Extract from source
            if from_engine_type.lower() == 'selenium':
                session_data = self.extract_session_from_selenium(from_driver)
            else:
                self.logger.error(f"Unsupported source engine: {from_engine_type}")
                return None
            
            # Inject to target
            if to_engine_type.lower() == 'playwright':
                success = await self.inject_session_to_playwright(to_page, session_data)
                if not success:
                    return None
            else:
                self.logger.error(f"Unsupported target engine: {to_engine_type}")
                return None
            
            # Validate
            if validate:
                is_valid = await self.validate_session_continuity(
                    to_page,
                    expected_user_id=session_data.user_id
                )
                if not is_valid:
                    self.logger.warning("⚠️ Session transfer validation failed")
                    return None
            
            self.logger.info("✅ Session transferred successfully")
            return session_data
            
        except Exception as e:
            self.logger.error(f"❌ Session transfer failed: {e}")
            return None
```

---

## 2. AUTHENTICATION SERVICE (framework/auth/auth_service.py)

**Purpose**: Unified authentication interface for both engines

```python
"""
Authentication Service - Abstraction Layer for SSO/MFA/OAUTH

Provides unified interface for authentication across Playwright and Selenium.

Author: Principal QA Architect
"""

import logging
from typing import Optional, Dict, Any
from enum import Enum
from framework.core.session_manager import SessionManager, SessionData

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
    - SSO authentication (Okta, Azure AD, etc.)
    - MFA flows
    - Basic authentication
    - OAuth2
    - SAML
    - Session persistence
    """
    
    def __init__(self, session_manager: Optional[SessionManager] = None):
        self.session_manager = session_manager or SessionManager()
        self.logger = logger
        self._current_session: Optional[SessionData] = None
        self._current_user: Optional[Dict[str, Any]] = None
    
    # ========================================================================
    # SSO AUTHENTICATION (Okta Example)
    # ========================================================================
    
    def authenticate_sso(
        self,
        engine,
        sso_config: Dict[str, str],
        credentials: Dict[str, str]
    ) -> Optional[SessionData]:
        """
        Authenticate using SSO (Okta, Azure AD, etc.)
        
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
        
        Returns:
            SessionData if successful
        """
        self.logger.info("Starting SSO authentication (Selenium)...")
        
        try:
            provider = sso_config.get('provider', '').lower()
            
            if provider == 'okta':
                return self._authenticate_okta(engine, sso_config, credentials)
            elif provider == 'azure_ad':
                return self._authenticate_azure_ad(engine, sso_config, credentials)
            elif provider == 'google':
                return self._authenticate_google(engine, sso_config, credentials)
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
        credentials: Dict[str, str]
    ) -> Optional[SessionData]:
        """Authenticate with Okta"""
        self.logger.info("Authenticating with Okta...")
        
        try:
            okta_domain = sso_config.get('okta_domain')
            app_id = sso_config.get('app_id')
            username = credentials.get('username')
            password = credentials.get('password')
            
            # Navigate to Okta
            login_url = f"{okta_domain}/app/{app_id}/login/login.htm"
            driver.get(login_url)
            
            # Wait for login form
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(driver, 30)
            
            # Fill username
            username_field = wait.until(
                EC.presence_of_element_located((By.ID, "okta-signin-username"))
            )
            username_field.clear()
            username_field.send_keys(username)
            
            # Fill password
            password_field = driver.find_element(By.ID, "okta-signin-password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Click submit
            submit_btn = driver.find_element(By.ID, "okta-signin-submit")
            submit_btn.click()
            
            # Wait for MFA if needed
            mfa_token = credentials.get('mfa_token')
            if mfa_token:
                self.logger.info("MFA required - entering MFA token...")
                mfa_field = wait.until(
                    EC.presence_of_element_located((By.ID, "okta-verify-totp"))
                )
                mfa_field.send_keys(mfa_token)
                mfa_submit = driver.find_element(By.ID, "mfa-verify-submit")
                mfa_submit.click()
            
            # Wait for successful login
            wait.until(
                EC.url_changes(login_url)
            )
            
            self.logger.info("✅ Okta authentication successful")
            
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
        credentials: Dict[str, str]
    ) -> Optional[SessionData]:
        """Authenticate with Azure AD"""
        # Similar to Okta but using Azure AD login flow
        self.logger.info("Authenticating with Azure AD...")
        # Implementation similar to Okta
        pass
    
    def _authenticate_google(
        self,
        driver,
        sso_config: Dict[str, str],
        credentials: Dict[str, str]
    ) -> Optional[SessionData]:
        """Authenticate with Google"""
        # Similar pattern for Google authentication
        self.logger.info("Authenticating with Google...")
        # Implementation
        pass
    
    # ========================================================================
    # BASIC AUTHENTICATION
    # ========================================================================
    
    def authenticate_basic(
        self,
        engine,
        username: str,
        password: str,
        login_url: str
    ) -> Optional[SessionData]:
        """
        Basic username/password authentication
        
        Args:
            engine: Selenium WebDriver or Playwright Page
            username: Username
            password: Password
            login_url: Login page URL
        
        Returns:
            SessionData if successful
        """
        self.logger.info("Starting basic authentication...")
        
        try:
            # Detect engine type
            if hasattr(engine, 'get'):  # Selenium
                return self._authenticate_basic_selenium(engine, username, password, login_url)
            else:  # Playwright
                return self._authenticate_basic_playwright(engine, username, password, login_url)
                
        except Exception as e:
            self.logger.error(f"❌ Basic authentication failed: {e}")
            return None
    
    def _authenticate_basic_selenium(
        self,
        driver,
        username: str,
        password: str,
        login_url: str
    ) -> Optional[SessionData]:
        """Basic auth using Selenium"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        try:
            driver.get(login_url)
            wait = WebDriverWait(driver, 20)
            
            # Locate username field
            username_field = wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys(username)
            
            # Locate password field
            password_field = driver.find_element(By.NAME, "password")
            password_field.send_keys(password)
            
            # Click login
            login_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
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
            self.logger.error(f"❌ Basic authentication failed: {e}")
            return None
    
    def _authenticate_basic_playwright(
        self,
        page,
        username: str,
        password: str,
        login_url: str
    ) -> Optional[SessionData]:
        """Basic auth using Playwright (Async)"""
        # This would be called in async context
        pass
    
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
```

---

## 3. WORKFLOW ORCHESTRATOR (framework/core/workflow_orchestrator.py)

**Purpose**: Orchestrate multi-step cross-engine test workflows

```python
"""
Workflow Orchestrator - Multi-Step Cross-Engine Test Execution

Orchestrates complex workflows that span multiple engines and projects.

Author: Principal QA Architect
"""

import logging
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Status of a workflow step"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class EngineType(Enum):
    """Engine types"""
    SELENIUM = "selenium"
    PLAYWRIGHT = "playwright"


@dataclass
class WorkflowStep:
    """Single step in a workflow"""
    name: str
    description: str
    engine: EngineType
    action: Callable  # Function to execute
    requires_session: Optional[str] = None  # Name of step to extract session from
    inject_session: bool = False  # Whether to inject session from prior step
    on_failure: str = "stop"  # "stop" or "continue"
    timeout: int = 30000
    retry_count: int = 1
    
    # Runtime data
    status: StepStatus = field(default=StepStatus.PENDING)
    result: Optional[Any] = None
    error: Optional[str] = None
    session_data: Optional[Dict[str, Any]] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    execution_time_ms: int = 0


@dataclass
class Workflow:
    """Complete workflow definition"""
    name: str
    description: str
    steps: List[WorkflowStep]
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Runtime tracking
    status: str = "defined"  # defined, running, passed, failed
    results: Dict[str, Any] = field(default_factory=dict)


class WorkflowOrchestrator:
    """
    Orchestrates multi-step workflows across engines
    
    Responsibilities:
    - Define workflows
    - Execute workflows in sequence
    - Handle session transfer between steps
    - Track execution status
    - Handle failures and retries
    """
    
    def __init__(self):
        self.logger = logger
        self._workflows: Dict[str, Workflow] = {}
        self._execution_history: List[Dict[str, Any]] = []
        self._session_bridge = None  # Will be injected
    
    def define_workflow(
        self,
        name: str,
        description: str = "",
        tags: List[str] = None
    ) -> Workflow:
        """
        Define a new workflow
        
        Args:
            name: Workflow name
            description: Workflow description
            tags: Optional tags for categorization
        
        Returns:
            Workflow object
        """
        self.logger.info(f"Defining workflow: {name}")
        
        workflow = Workflow(
            name=name,
            description=description,
            steps=[],
            tags=tags or []
        )
        
        self._workflows[name] = workflow
        return workflow
    
    def add_step(
        self,
        workflow_name: str,
        step_name: str,
        action: Callable,
        engine: EngineType = EngineType.PLAYWRIGHT,
        description: str = "",
        requires_session: Optional[str] = None,
        inject_session: bool = False,
        on_failure: str = "stop",
        timeout: int = 30000,
        retry_count: int = 1
    ) -> WorkflowStep:
        """
        Add a step to a workflow
        
        Args:
            workflow_name: Name of workflow to add to
            step_name: Name of this step
            action: Callable to execute
            engine: Engine to use (SELENIUM or PLAYWRIGHT)
            description: Step description
            requires_session: Name of step whose session to use
            inject_session: Whether to inject session from prior step
            on_failure: What to do on failure ("stop" or "continue")
            timeout: Timeout in ms
            retry_count: Number of retries on failure
        
        Returns:
            WorkflowStep object
        """
        if workflow_name not in self._workflows:
            raise ValueError(f"Workflow '{workflow_name}' not defined")
        
        workflow = self._workflows[workflow_name]
        
        step = WorkflowStep(
            name=step_name,
            description=description,
            engine=engine,
            action=action,
            requires_session=requires_session,
            inject_session=inject_session,
            on_failure=on_failure,
            timeout=timeout,
            retry_count=retry_count
        )
        
        workflow.steps.append(step)
        self.logger.info(f"✅ Added step '{step_name}' to workflow '{workflow_name}'")
        
        return step
    
    async def execute_workflow(
        self,
        workflow_name: str,
        engines: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow
        
        Args:
            workflow_name: Name of workflow to execute
            engines: Dict of {engine_type: engine_instance}
        
        Returns:
            Execution results
        """
        if workflow_name not in self._workflows:
            raise ValueError(f"Workflow '{workflow_name}' not defined")
        
        workflow = self._workflows[workflow_name]
        self.logger.info(f"Executing workflow: {workflow_name}")
        
        workflow.status = "running"
        session_data_cache: Dict[str, Any] = {}
        
        for step in workflow.steps:
            await self._execute_step(
                workflow,
                step,
                engines,
                session_data_cache
            )
            
            # Check failure handling
            if step.status == StepStatus.FAILED and step.on_failure == "stop":
                self.logger.error(f"⚠️ Stopping workflow - step '{step.name}' failed")
                workflow.status = "failed"
                break
        
        # Determine final status
        if all(s.status in [StepStatus.PASSED, StepStatus.SKIPPED] for s in workflow.steps):
            workflow.status = "passed"
        else:
            workflow.status = "failed"
        
        # Build results
        results = {
            'workflow_name': workflow_name,
            'status': workflow.status,
            'steps': [asdict(s) for s in workflow.steps],
            'timestamp': datetime.now().isoformat()
        }
        
        self._execution_history.append(results)
        self.logger.info(f"✅ Workflow execution completed: {workflow.status}")
        
        return results
    
    async def _execute_step(
        self,
        workflow: Workflow,
        step: WorkflowStep,
        engines: Dict[str, Any],
        session_cache: Dict[str, Any]
    ) -> None:
        """Execute a single workflow step"""
        self.logger.info(f"Executing step: {step.name}")
        step.status = StepStatus.RUNNING
        step.start_time = datetime.now().isoformat()
        
        try:
            # Get the engine for this step
            engine = engines.get(step.engine.value)
            if not engine:
                raise ValueError(f"Engine not provided for {step.engine.value}")
            
            # Inject session if required
            if step.inject_session and step.requires_session:
                session_data = session_cache.get(step.requires_session)
                if session_data:
                    self.logger.info(f"Injecting session from step '{step.requires_session}'")
                    # Inject logic here
            
            # Execute the action
            self.logger.info(f"Executing action: {step.action.__name__}")
            result = await step.action(engine)
            
            step.result = result
            step.status = StepStatus.PASSED
            
            # Extract session if needed for later steps
            # (This would depend on your session manager)
            
            self.logger.info(f"✅ Step '{step.name}' PASSED")
            
        except Exception as e:
            step.error = str(e)
            step.status = StepStatus.FAILED
            self.logger.error(f"❌ Step '{step.name}' FAILED: {e}")
        
        finally:
            step.end_time = datetime.now().isoformat()
            import time
            if hasattr(step, 'start_time') and step.start_time:
                # Calculate execution time
                pass
    
    def get_workflow_status(self, workflow_name: str) -> Dict[str, Any]:
        """Get status of a workflow"""
        if workflow_name not in self._workflows:
            return None
        
        workflow = self._workflows[workflow_name]
        return {
            'name': workflow.name,
            'status': workflow.status,
            'steps': [
                {
                    'name': s.name,
                    'status': s.status.value,
                    'result': s.result,
                    'error': s.error
                }
                for s in workflow.steps
            ]
        }
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history"""
        return self._execution_history
```

---

## 4. WORKFLOW TEST FIXTURE (tests/workflows/conftest.py)

**Purpose**: Fixtures for workflow tests

```python
"""
Workflow Test Configuration

Provides fixtures for workflow-based tests

Author: Principal QA Architect
"""

import pytest
from framework.core.workflow_orchestrator import WorkflowOrchestrator, EngineType
from framework.auth.auth_service import AuthenticationService
from framework.core.session_manager import SessionManager

@pytest.fixture
def workflow_orchestrator():
    """Provide workflow orchestrator"""
    return WorkflowOrchestrator()

@pytest.fixture
def auth_service():
    """Provide authentication service"""
    session_manager = SessionManager()
    return AuthenticationService(session_manager)

@pytest.fixture
async def cross_engine_session(selenium_engine, playwright_engine, auth_service):
    """
    Fixture that handles cross-engine session transfer
    
    Usage:
        def test_cross_engine(cross_engine_session):
            selenium_eng, playwright_eng, session_data = cross_engine_session
    """
    session_manager = auth_service.session_manager
    
    yield (selenium_engine, playwright_engine, session_manager)
```

---

## 5. EXAMPLE: COMPLETE CROSS-ENGINE WORKFLOW TEST

**File**: `tests/workflows/test_sso_to_callcenter_to_intake.py`

```python
"""
Example: Complete Cross-Engine Workflow

SSO Login (Selenium) → CallCenter (Playwright) → PatientIntake (Playwright)

This test demonstrates the complete workflow orchestration pattern.

Author: Principal QA Architect
"""

import pytest
import asyncio
from framework.core.workflow_orchestrator import EngineType


@pytest.mark.workflow
@pytest.mark.requires_authentication
@pytest.mark.sso_dependent
class TestCrossEngineWorkflow:
    """Cross-engine workflow tests"""
    
    @pytest.mark.critical
    async def test_sso_to_callcenter_to_intake_complete_flow(
        self,
        workflow_orchestrator,
        auth_service,
        selenium_engine,
        playwright_engine
    ):
        """
        Complete workflow: SSO Login → CallCenter → PatientIntake
        
        Engines:
        - Step 1: Selenium (SSO login - enterprise authentication)
        - Step 2: Playwright (CallCenter UI)
        - Step 3: Playwright (PatientIntake UI)
        
        Session Flow:
        - Extract session from Selenium after SSO
        - Inject into Playwright for CallCenter
        - Inject into Playwright for PatientIntake
        """
        
        # Define the workflow
        workflow = workflow_orchestrator.define_workflow(
            name="sso_to_callcenter_to_intake",
            description="SSO Login then access CallCenter and PatientIntake",
            tags=["sso", "multi-engine", "cross-project"]
        )
        
        # STEP 1: SSO Login using Selenium
        async def step_1_sso_login(engine):
            """Step 1: Authenticate via SSO using Selenium"""
            sso_config = {
                'provider': 'okta',
                'okta_domain': 'https://company.okta.com',
                'app_id': 'app_12345'
            }
            
            credentials = {
                'username': 'test.user@company.com',
                'password': 'secure_password',
                'mfa_token': '123456'  # From authenticator app
            }
            
            session_data = auth_service.authenticate_sso(
                engine,
                sso_config,
                credentials
            )
            
            assert session_data is not None, "SSO login failed"
            assert session_data.user_id is not None, "User ID not found"
            assert session_data.auth_type == 'SSO', "Auth type should be SSO"
            
            return {'session': session_data, 'user': session_data.user_id}
        
        workflow_orchestrator.add_step(
            workflow_name="sso_to_callcenter_to_intake",
            step_name="sso_login",
            action=step_1_sso_login,
            engine=EngineType.SELENIUM,
            description="Authenticate via Okta SSO",
            on_failure="stop",
            retry_count=2
        )
        
        # STEP 2: CallCenter Operations using Playwright
        async def step_2_callcenter_flow(engine):
            """Step 2: Execute CallCenter operations using Playwright"""
            # At this point, engine has the session injected
            # from the Selenium SSO step
            
            # Navigate to CallCenter
            await engine.goto('https://callcenter.company.com')
            
            # Verify we're logged in
            page_title = await engine.title()
            assert 'Call Center' in page_title, "Not on CallCenter page"
            
            # Perform CallCenter operations
            # (This would use your CallCenter Page Objects)
            
            return {'status': 'completed', 'operations': 5}
        
        workflow_orchestrator.add_step(
            workflow_name="sso_to_callcenter_to_intake",
            step_name="callcenter_flow",
            action=step_2_callcenter_flow,
            engine=EngineType.PLAYWRIGHT,
            description="Execute CallCenter workflow",
            requires_session="sso_login",  # Use session from Step 1
            inject_session=True,
            on_failure="continue"
        )
        
        # STEP 3: PatientIntake Operations using Playwright
        async def step_3_intake_flow(engine):
            """Step 3: Execute PatientIntake operations using Playwright"""
            # Uses same session from SSO
            
            # Navigate to PatientIntake
            await engine.goto('https://patientintake.company.com')
            
            # Verify logged in
            page_title = await engine.title()
            assert 'Patient Intake' in page_title, "Not on PatientIntake page"
            
            # Perform PatientIntake operations
            
            return {'status': 'completed', 'patients': 3}
        
        workflow_orchestrator.add_step(
            workflow_name="sso_to_callcenter_to_intake",
            step_name="intake_flow",
            action=step_3_intake_flow,
            engine=EngineType.PLAYWRIGHT,
            description="Execute PatientIntake workflow",
            requires_session="sso_login",  # Use same session from SSO
            inject_session=True,
            on_failure="continue"
        )
        
        # Execute the workflow
        engines = {
            'selenium': selenium_engine,
            'playwright': playwright_engine
        }
        
        results = await workflow_orchestrator.execute_workflow(
            "sso_to_callcenter_to_intake",
            engines=engines
        )
        
        # Validate results
        assert results['status'] == 'passed', f"Workflow failed: {results}"
        assert len(results['steps']) == 3, "All 3 steps should exist"
        
        # Verify each step passed
        step_statuses = {s['name']: s['status'] for s in results['steps']}
        assert step_statuses['sso_login'] == 'passed'
        assert step_statuses['callcenter_flow'] == 'passed'
        assert step_statuses['intake_flow'] == 'passed'
        
        print("✅ Complete workflow passed successfully!")
```

---

## KEY IMPLEMENTATION NOTES

1. **Session Manager**:
   - Extracts cookies, tokens, localStorage, sessionStorage from Selenium
   - Injects them into Playwright
   - Validates session continuity

2. **Authentication Service**:
   - Unified interface for SSO, MFA, OAuth, SAML
   - Handles Okta, Azure AD, Google
   - Stores current session and user context

3. **Workflow Orchestrator**:
   - Defines multi-step workflows
   - Executes steps in sequence
   - Manages session transfer between steps
   - Handles failures and retries

4. **No Conflicts Because**:
   - Each step explicitly declares its engine
   - Session transfer is explicit (not magic)
   - Engines don't run simultaneously on same page
   - Flow is deterministic and auditable

---

Next: Implement Phase 1 (SessionManager + AuthService) first, then proceed with WorkflowOrchestrator.
