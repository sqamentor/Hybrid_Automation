"""
Authentication Service Package

Unified authentication interface for SSO, MFA, OAuth, and Basic authentication
across Selenium and Playwright engines.

Author: Principal QA Architect
Date: January 31, 2026
"""

from .auth_service import AuthenticationService, AuthMethod

__all__ = ["AuthenticationService", "AuthMethod"]
