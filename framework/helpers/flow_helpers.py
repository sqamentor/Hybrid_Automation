"""
Flow Helpers - Execution Flow Control Utilities

Provides decorators and helper functions for conditional execution of
API and database validation based on configuration.
"""

from functools import wraps
from types import TracebackType
from typing import Any, Callable, List, Optional, ParamSpec, TypeVar, Literal

from utils.logger import get_logger

P = ParamSpec('P')
R = TypeVar('R')

try:
    from config.settings import (
        get_enabled_components,
        get_execution_mode,
        should_run_api_validation,
        should_run_db_validation,
    )
except ImportError:
    # Fallback if settings not available
    def should_run_api_validation() -> bool:
        return True
    def should_run_db_validation() -> bool:
        return True
    def get_enabled_components() -> List[str]:
        return ['ui', 'api', 'database']
    def get_execution_mode() -> str:
        return 'ui_api_db'

logger = get_logger(__name__)


def run_api_validation(func: Callable[P, R]) -> Callable[P, Optional[R]]:
    """Decorator to conditionally run API validation.

    Usage:
        @run_api_validation
        def validate_api():
            # API validation code
            pass
    """
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Optional[R]:
        if should_run_api_validation():
            return func(*args, **kwargs)
        else:
            logger.info(f"Skipping API validation: {func.__name__} (execution mode: {get_execution_mode()})")
            return None
    return wrapper


def run_db_validation(func: Callable[P, R]) -> Callable[P, Optional[R]]:
    """Decorator to conditionally run database validation.

    Usage:
        @run_db_validation
        def validate_database():
            # Database validation code
            pass
    """
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Optional[R]:
        if should_run_db_validation():
            return func(*args, **kwargs)
        else:
            logger.info(f"Skipping database validation: {func.__name__} (execution mode: {get_execution_mode()})")
            return None
    return wrapper


def skip_if_api_disabled(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator to skip entire test if API validation is disabled.

    Usage:
        @skip_if_api_disabled
        def test_api_flow():
            # Test code
            pass
    """
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if not should_run_api_validation():
            import pytest
            pytest.skip(f"API validation disabled (mode: {get_execution_mode()})")
        return func(*args, **kwargs)
    return wrapper


def skip_if_db_disabled(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator to skip entire test if database validation is disabled.

    Usage:
        @skip_if_db_disabled
        def test_db_flow():
            # Test code
            pass
    """
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if not should_run_db_validation():
            import pytest
            pytest.skip(f"Database validation disabled (mode: {get_execution_mode()})")
        return func(*args, **kwargs)
    return wrapper


def is_component_enabled(component: str) -> bool:
    """Check if a specific component is enabled.

    Args:
        component: Component name ('ui', 'api', or 'database')

    Returns:
        True if component is enabled
    """
    return component in get_enabled_components()


def get_active_components() -> str:
    """Get a formatted string of active components.

    Returns:
        String like "UI + API + DB" or "UI only"
    """
    components = get_enabled_components()
    
    if components == ['ui']:
        return "UI only"
    elif components == ['ui', 'api']:
        return "UI + API"
    elif components == ['ui', 'api', 'database']:
        return "UI + API + DB"
    else:
        return " + ".join([c.upper() for c in components])


def log_execution_mode() -> None:
    """Log current execution mode."""
    mode = get_execution_mode()
    components = get_active_components()
    logger.info(f"Execution Mode: {mode} ({components})")


# Context manager for conditional execution
class ConditionalExecution:
    """Context manager for conditional execution blocks.

    Usage:
        with ConditionalExecution('api') as should_run:
            if should_run:
                # API validation code
                pass
    """
    
    def __init__(self, component: str):
        """Initialize conditional execution.

        Args:
            component: Component name ('api' or 'database')
        """
        self.component = component
        self.should_run = False
    
    def __enter__(self) -> bool:
        """Enter context - return True if component should run"""
        if self.component == 'api':
            self.should_run = should_run_api_validation()
        elif self.component == 'database':
            self.should_run = should_run_db_validation()
        else:
            self.should_run = True
        
        if not self.should_run:
            logger.debug(f"Skipping {self.component} validation (mode: {get_execution_mode()})")
        
        return self.should_run
    
    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> Literal[False]:
        """Exit context."""
        return False


# Convenience functions for test code
def api_enabled() -> bool:
    """Check if API validation is enabled (shorter alias)"""
    return should_run_api_validation()


def db_enabled() -> bool:
    """Check if database validation is enabled (shorter alias)"""
    return should_run_db_validation()


__all__ = [
    'run_api_validation',
    'run_db_validation',
    'skip_if_api_disabled',
    'skip_if_db_disabled',
    'is_component_enabled',
    'get_active_components',
    'log_execution_mode',
    'ConditionalExecution',
    'api_enabled',
    'db_enabled',
    'should_run_api_validation',
    'should_run_db_validation'
]
