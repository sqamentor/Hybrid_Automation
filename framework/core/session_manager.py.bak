"""
Session Manager - Cross-Engine Session Bridge

Handles extraction and injection of authentication tokens, cookies, and user context
between Selenium and Playwright engines.

Author: Principal QA Architect
Date: January 31, 2026
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

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
    def from_dict(cls, data: Dict[str, Any]) -> "SessionData":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class CacheEntry:
    """Cache entry for session data"""

    session_data: SessionData
    timestamp: float
    hit_count: int = 0


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

    def __init__(self, logger_instance: Optional[logging.Logger] = None):
        self.logger = logger_instance or logging.getLogger(__name__)
        self._session_cache: Dict[str, CacheEntry] = {}

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
                    "name": c["name"],
                    "value": c["value"],
                    "domain": c.get("domain", ""),
                    "path": c.get("path", "/"),
                    "secure": c.get("secure", False),
                    "httpOnly": c.get("httpOnly", False),
                    "sameSite": c.get("sameSite", "Lax"),
                }
                for c in selenium_cookies
            ]

            # Extract localStorage (if available)
            local_storage = self._extract_storage_from_selenium(driver, "localStorage")

            # Extract sessionStorage
            session_storage = self._extract_storage_from_selenium(driver, "sessionStorage")

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
                auth_type=auth_type,
            )

            self.logger.info(
                f"✅ Session extracted: {len(cookies)} cookies, auth_type={auth_type}, user_id={user_id}"
            )
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
            "auth_token",
            "access_token",
            "id_token",
            "refresh_token",
            "jwt",
            "bearer_token",
            "token",
            "Authorization",
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
        if any("oauth" in str(k).lower() or "oauth" in str(v).lower() for k, v in tokens.items()):
            return "OAUTH"

        # Check for JWT
        if any("jwt" in str(k).lower() or "jwt" in str(v).lower() for k, v in tokens.items()):
            return "JWT"

        # Check for SSO (Okta, Azure, etc.)
        cookie_names = [c["name"].lower() for c in cookies]
        if any("okta" in name or "azure" in name or "saml" in name for name in cookie_names):
            return "SSO"

        # Check for basic auth (typically in Authorization header)
        if any(
            "authorization" in str(k).lower() or "authorization" in str(v).lower()
            for k, v in tokens.items()
        ):
            return "BASIC"

        return "UNKNOWN"

    @staticmethod
    def _extract_user_id(tokens: Dict, session_storage: Dict, local_storage: Dict) -> Optional[str]:
        """Extract user ID from session data"""
        # Try tokens first
        for key in ["user_id", "userId", "sub", "user"]:
            if key in tokens:
                return str(tokens[key])

        # Try storage
        for storage in [session_storage, local_storage]:
            for key in ["user_id", "userId", "current_user", "currentUser"]:
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
            if not page.url or page.url == "about:blank":
                # Use a dummy navigation if no URL set yet
                self.logger.info("Page not yet navigated, waiting for navigation...")

            # Inject localStorage
            if session_data.local_storage:
                js_code = self._generate_storage_injection_code(
                    "localStorage", session_data.local_storage
                )
                await page.evaluate(js_code)
                self.logger.info(
                    f"✅ Injected {len(session_data.local_storage)} localStorage items"
                )

            # Inject sessionStorage
            if session_data.session_storage:
                js_code = self._generate_storage_injection_code(
                    "sessionStorage", session_data.session_storage
                )
                await page.evaluate(js_code)
                self.logger.info(
                    f"✅ Injected {len(session_data.session_storage)} sessionStorage items"
                )

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

    def inject_session_to_playwright_sync(self, page, session_data: SessionData) -> bool:
        """
        Inject session data into Playwright Page (Sync version)

        Args:
            page: Playwright Page instance (sync)
            session_data: SessionData object to inject

        Returns:
            True if injection successful, False otherwise
        """
        self.logger.info("Injecting session into Playwright (sync)...")

        try:
            # Add cookies
            if session_data.cookies:
                page.context.add_cookies(session_data.cookies)
                self.logger.info(f"✅ Added {len(session_data.cookies)} cookies")

            # Inject localStorage
            if session_data.local_storage:
                js_code = self._generate_storage_injection_code(
                    "localStorage", session_data.local_storage
                )
                page.evaluate(js_code)
                self.logger.info(
                    f"✅ Injected {len(session_data.local_storage)} localStorage items"
                )

            # Inject sessionStorage
            if session_data.session_storage:
                js_code = self._generate_storage_injection_code(
                    "sessionStorage", session_data.session_storage
                )
                page.evaluate(js_code)
                self.logger.info(
                    f"✅ Injected {len(session_data.session_storage)} sessionStorage items"
                )

            # Set tokens if needed
            if session_data.tokens:
                js_code = self._generate_token_injection_code(session_data.tokens)
                page.evaluate(js_code)
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

    async def validate_session_continuity(
        self, page, expected_user_id: Optional[str] = None
    ) -> bool:
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

            if user_data.get("userId"):
                self.logger.info(f"✅ User context found: {user_data['userId']}")
                if expected_user_id and user_data["userId"] != expected_user_id:
                    self.logger.warning(
                        f"⚠️ User ID mismatch: expected {expected_user_id}, got {user_data['userId']}"
                    )
                    return False
                return True

            self.logger.warning("⚠️ No user context found")
            return False

        except Exception as e:
            self.logger.error(f"❌ Validation failed: {e}")
            return False

    def validate_session_continuity_sync(
        self, page, expected_user_id: Optional[str] = None
    ) -> bool:
        """
        Validate that session persisted successfully (Sync version)

        Args:
            page: Playwright Page instance (sync)
            expected_user_id: Expected user ID (optional)

        Returns:
            True if session valid, False otherwise
        """
        self.logger.info("Validating session continuity (sync)...")

        try:
            # Check if cookies are present
            cookies = page.context.cookies()
            if not cookies:
                self.logger.warning("⚠️ No cookies found after injection")
                return False

            # Check localStorage for auth token
            token = page.evaluate("return localStorage.getItem('auth_token');")
            if token:
                self.logger.info("✅ Auth token present in localStorage")
                return True

            # Check for user context
            user_data = page.evaluate("""
                return {
                    userId: localStorage.getItem('user_id'),
                    userName: localStorage.getItem('user_name'),
                    userEmail: localStorage.getItem('user_email')
                }
            """)

            if user_data and user_data.get("userId"):
                self.logger.info(f"✅ User context found: {user_data['userId']}")
                if expected_user_id and user_data["userId"] != expected_user_id:
                    self.logger.warning(
                        f"⚠️ User ID mismatch: expected {expected_user_id}, got {user_data['userId']}"
                    )
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
        validate: bool = True,
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
            if from_engine_type.lower() == "selenium":
                session_data = self.extract_session_from_selenium(from_driver)
            else:
                self.logger.error(f"Unsupported source engine: {from_engine_type}")
                return None

            # Inject to target
            if to_engine_type.lower() == "playwright":
                success = await self.inject_session_to_playwright(to_page, session_data)
                if not success:
                    return None
            else:
                self.logger.error(f"Unsupported target engine: {to_engine_type}")
                return None

            # Validate
            if validate:
                is_valid = await self.validate_session_continuity(
                    to_page, expected_user_id=session_data.user_id
                )
                if not is_valid:
                    self.logger.warning("⚠️ Session transfer validation failed")
                    return None

            self.logger.info("✅ Session transferred successfully")
            return session_data

        except Exception as e:
            self.logger.error(f"❌ Session transfer failed: {e}")
            return None

    def transfer_session_sync(
        self,
        from_engine_type: str,  # 'selenium' or 'playwright'
        from_driver,
        to_engine_type: str,
        to_page,
        validate: bool = True,
    ) -> Optional[SessionData]:
        """
        Transfer session from one engine to another (Sync version)

        Args:
            from_engine_type: Source engine ('selenium' or 'playwright')
            from_driver: Source driver instance
            to_engine_type: Target engine ('selenium' or 'playwright')
            to_page: Target page instance
            validate: Whether to validate after transfer

        Returns:
            SessionData if successful, None otherwise
        """
        self.logger.info(f"Transferring session (sync): {from_engine_type} → {to_engine_type}")

        try:
            # Extract from source
            if from_engine_type.lower() == "selenium":
                session_data = self.extract_session_from_selenium(from_driver)
            else:
                self.logger.error(f"Unsupported source engine: {from_engine_type}")
                return None

            # Inject to target
            if to_engine_type.lower() == "playwright":
                success = self.inject_session_to_playwright_sync(to_page, session_data)
                if not success:
                    return None
            else:
                self.logger.error(f"Unsupported target engine: {to_engine_type}")
                return None

            # Validate
            if validate:
                is_valid = self.validate_session_continuity_sync(
                    to_page, expected_user_id=session_data.user_id
                )
                if not is_valid:
                    self.logger.warning("⚠️ Session transfer validation failed")
                    return None

            self.logger.info("✅ Session transferred successfully")
            return session_data

        except Exception as e:
            self.logger.error(f"❌ Session transfer failed: {e}")
            return None

    # ========================================================================
    # SESSION CACHE MANAGEMENT
    # ========================================================================

    def cache_session(self, session_id: str, session_data: SessionData) -> None:
        """Cache session data for later use"""
        self._session_cache[session_id] = CacheEntry(
            session_data=session_data, timestamp=datetime.now().timestamp()
        )
        self.logger.info(f"✅ Session cached: {session_id}")

    def get_cached_session(self, session_id: str) -> Optional[SessionData]:
        """Retrieve cached session data"""
        entry = self._session_cache.get(session_id)
        if entry:
            entry.hit_count += 1
            self.logger.info(f"✅ Session retrieved from cache: {session_id}")
            return entry.session_data
        return None

    def clear_cache(self) -> None:
        """Clear all cached sessions"""
        self._session_cache.clear()
        self.logger.info("✅ Session cache cleared")
