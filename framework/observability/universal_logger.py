"""
Universal Logging Decorators - Auto-Instrumentation
====================================================

Provides decorators for automatic, comprehensive logging of all functions,
methods, and operations across the entire framework.

Features:
- Automatic entry/exit logging
- Argument capture (with PII masking)
- Execution timing
- Exception capture with full stack traces
- Success/failure indicators
- State transition tracking
- Async/sync support

Usage:
    from framework.observability.universal_logger import log_function, log_async_function, log_state_transition
    
    @log_function()
    def my_function(arg1, arg2):
        return result
    
    @log_async_function()
    async def my_async_function():
        pass
    
    @log_state_transition(from_state='idle', to_state='active')
    def activate():
        pass

Author: Lokendra Singh
Email: qa.lokendra@gmail.com
Website: www.sqamentor.com
"""

import asyncio
import functools
import inspect
import time
import traceback
from typing import Any, Callable, Dict, List, Optional, Union
from framework.observability.enterprise_logger import get_enterprise_logger, SensitiveDataMasker

logger = get_enterprise_logger()


def log_function(
    log_args: bool = True,
    log_result: bool = True,
    log_timing: bool = True,
    mask_sensitive: bool = True,
    log_level: str = "DEBUG",
    include_caller: bool = False
):
    """
    Universal logging decorator for synchronous functions
    
    Args:
        log_args: Log function arguments
        log_result: Log return value
        log_timing: Log execution time
        mask_sensitive: Mask sensitive data in args/result
        log_level: Logging level (DEBUG/INFO/WARNING)
        include_caller: Include caller function info
    
    Example:
        @log_function(log_args=True, log_timing=True)
        def process_order(order_id, amount):
            return {"status": "success"}
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            module_name =func.__module__
            
            # Prepare context
            context = {
                "function": func_name,
                "module": module_name,
                "type": "sync_function"
            }
            
            # Add caller info if requested
            if include_caller:
                caller_frame = inspect.currentframe().f_back
                context["caller_file"] = caller_frame.f_code.co_filename
                context["caller_line"] = caller_frame.f_lineno
                context["caller_function"] = caller_frame.f_code.co_name
            
            # Log arguments
            if log_args and (args or kwargs):
                args_repr = [repr(a) for a in args]
                kwargs_repr = {k: repr(v) for k, v in kwargs.items()}
                
                if mask_sensitive:
                    kwargs_repr = SensitiveDataMasker.mask_dict(kwargs_repr)
                
                context["args"] = args_repr
                context["kwargs"] = kwargs_repr
            
            # Log function entry
            log_method = getattr(logger, log_level.lower(), logger.debug)
            log_method(f"→ ENTER: {module_name}.{func_name}", **context)
            
            start_time = time.time()
            exception_occurred = False
            result = None
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Log success
                success_context = context.copy()
                if log_timing:
                    execution_time = time.time() - start_time
                    success_context["execution_time_ms"] = round(execution_time * 1000, 2)
                
                if log_result and result is not None:
                    result_repr = repr(result)
                    if mask_sensitive and isinstance(result, dict):
                        result_repr = SensitiveDataMasker.mask_dict(result)
                    success_context["result"] = result_repr
                
                log_method(f"✓ EXIT: {module_name}.{func_name} - SUCCESS", **success_context)
                
                return result
                
            except Exception as exc:
                exception_occurred = True
                
                # Log failure
                error_context = context.copy()
                if log_timing:
                    execution_time = time.time() - start_time
                    error_context["execution_time_ms"] = round(execution_time * 1000, 2)
                
                error_context["exception_type"] = type(exc).__name__
                error_context["exception_message"] = str(exc)
                
                logger.error(
                    f"✗ EXIT: {module_name}.{func_name} - FAILED",
                    exc_info=True,
                    **error_context
                )
                
                # Re-raise the exception
                raise
        
        return wrapper
    return decorator


def log_async_function(
    log_args: bool = True,
    log_result: bool = True,
    log_timing: bool = True,
    mask_sensitive: bool = True,
    log_level: str = "DEBUG"
):
    """
    Universal logging decorator for asynchronous functions
    
    Args:
        log_args: Log function arguments
        log_result: Log return value
        log_timing: Log execution time
        mask_sensitive: Mask sensitive data in args/result
        log_level: Logging level (DEBUG/INFO/WARNING)
    
    Example:
        @log_async_function(log_args=True, log_timing=True)
        async def fetch_data(user_id):
            return await db.query(...)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            func_name = func.__name__
            module_name = func.__module__
            
            # Prepare context
            context = {
                "function": func_name,
                "module": module_name,
                "type": "async_function"
            }
            
            # Log arguments
            if log_args and (args or kwargs):
                args_repr = [repr(a) for a in args]
                kwargs_repr = {k: repr(v) for k, v in kwargs.items()}
                
                if mask_sensitive:
                    kwargs_repr = SensitiveDataMasker.mask_dict(kwargs_repr)
                
                context["args"] = args_repr
                context["kwargs"] = kwargs_repr
            
            # Log function entry
            log_method = getattr(logger, log_level.lower(), logger.debug)
            log_method(f"→ ENTER [ASYNC]: {module_name}.{func_name}", **context)
            
            start_time = time.time()
            result = None
            
            try:
                # Execute async function
                result = await func(*args, **kwargs)
                
                # Log success
                success_context = context.copy()
                if log_timing:
                    execution_time = time.time() - start_time
                    success_context["execution_time_ms"] = round(execution_time * 1000, 2)
                    success_context["await_duration"] = execution_time
                
                if log_result and result is not None:
                    result_repr = repr(result)
                    if mask_sensitive and isinstance(result, dict):
                        result_repr = SensitiveDataMasker.mask_dict(result)
                    success_context["result"] = result_repr
                
                log_method(f"✓ EXIT [ASYNC]: {module_name}.{func_name} - SUCCESS", **success_context)
                
                return result
                
            except Exception as exc:
                # Log failure
                error_context = context.copy()
                if log_timing:
                    execution_time = time.time() - start_time
                    error_context["execution_time_ms"] = round(execution_time * 1000, 2)
                
                error_context["exception_type"] = type(exc).__name__
                error_context["exception_message"] = str(exc)
                
                logger.error(
                    f"✗ EXIT [ASYNC]: {module_name}.{func_name} - FAILED",
                    exc_info=True,
                    **error_context
                )
                
                # Re-raise the exception
                raise
        
        return wrapper
    return decorator


def log_state_transition(
    state_field: str = "state",
    from_state: Optional[str] = None,
    to_state: Optional[str] = None,
    log_level: str = "INFO"
):
    """
    Decorator for logging state transitions
    
    Args:
        state_field: Name of state attribute/field
        from_state: Expected from state (None = any)
        to_state: Expected to state (None = not checked)
        log_level: Logging level
    
    Example:
        @log_state_transition(state_field='status', from_state='pending', to_state='completed')
        def complete_order(self):
            self.status = 'completed'
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            module_name = func.__module__
            
            # Get instance if it's a method
            instance = args[0] if args and hasattr(args[0], state_field) else None
            
            # Get current state if available
            current_state = getattr(instance, state_field, None) if instance else None
            
            # Validate from_state
            if from_state and current_state != from_state:
                logger.warning(
                    f"State transition validation failed: expected {from_state}, got {current_state}",
                    function=func_name,
                    module=module_name,
                    expected_state=from_state,
                    actual_state=current_state
                )
            
            # Log transition start
            context = {
                "function": func_name,
                "module": module_name,
                "state_field": state_field,
                "from_state": current_state,
                "to_state": to_state or "unknown"
            }
            
            log_method = getattr(logger, log_level.lower(), logger.info)
            log_method(f"STATE TRANSITION: {current_state} → {to_state}", **context)
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Get new state
                new_state = getattr(instance, state_field, None) if instance else None
                
                # Log transition success
                success_context = context.copy()
                success_context["actual_new_state"] = new_state
                success_context["transition_successful"] = (to_state is None or new_state == to_state)
                
                log_method(
                    f"✓ STATE TRANSITION COMPLETE: {current_state} → {new_state}",
                    **success_context
                )
                
                return result
                
            except Exception as exc:
                # Log transition failure
                logger.error(
                    f"✗ STATE TRANSITION FAILED: {current_state} → {to_state}",
                    exc_info=True,
                    exception_type=type(exc).__name__,
                    **context
                )
                raise
        
        return wrapper
    return decorator


def log_retry_operation(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    delay: Optional[float] = None,
    exceptions: tuple = (Exception,),
    log_level: str = "WARNING"
):
    """
    Decorator for logging retry operations with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier (if delay not specified)
        delay: Fixed delay between retries (overrides backoff_factor if provided)
        exceptions: Tuple of exceptions to catch and retry
        log_level: Logging level for retry attempts
    
    Example:
        @log_retry_operation(max_retries=3, backoff_factor=2.0)
        def flaky_api_call():
            return requests.get(url)
        
        @log_retry_operation(max_retries=3, delay=0.5)
        def flaky_with_fixed_delay():
            return requests.get(url)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            module_name = func.__module__
            
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    # Log attempt
                    if attempt > 0:
                        logger.warning(
                            f"🔄 RETRY ATTEMPT {attempt}/{max_retries}: {module_name}.{func_name}",
                            function=func_name,
                            module=module_name,
                            attempt=attempt,
                            max_retries=max_retries
                        )
                    
                    # Execute function
                    result = func(*args, **kwargs)
                    
                    # Log success
                    if attempt > 0:
                        logger.info(
                            f"✓ RETRY SUCCESSFUL on attempt {attempt}: {module_name}.{func_name}",
                            function=func_name,
                            module=module_name,
                            attempt=attempt,
                            total_attempts=attempt + 1
                        )
                    
                    return result
                    
                except exceptions as exc:
                    last_exception = exc
                    
                    if attempt < max_retries:
                        # Calculate backoff delay
                        retry_delay = delay if delay is not None else (backoff_factor ** attempt)
                        
                        logger.warning(
                            f"⚠️ RETRY: Attempt {attempt + 1} failed, retrying in {retry_delay}s",
                            function=func_name,
                            module=module_name,
                            attempt=attempt + 1,
                            max_retries=max_retries,
                            delay_seconds=retry_delay,
                            exception_type=type(exc).__name__,
                            exception_message=str(exc)
                        )
                        
                        time.sleep(retry_delay)
                    else:
                        # Final failure
                        logger.error(
                            f"✗ ALL RETRIES EXHAUSTED: {module_name}.{func_name} failed after {max_retries + 1} attempts",
                            function=func_name,
                            module=module_name,
                            total_attempts=max_retries + 1,
                            exception_type=type(exc).__name__,
                            exception_message=str(exc),
                            exc_info=True
                        )
                        raise
            
            # Should never reach here, but if it does, raise last exception
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


class OperationLogger:
    """Context manager for logging complex operations"""
    
    def __init__(
        self,
        operation_name: str,
        log_level: str = "INFO",
        **metadata
    ):
        self.operation_name = operation_name
        self.log_level = log_level
        self.metadata = metadata
        self.start_time = None
        self.success = False
    
    def __enter__(self):
        self.start_time = time.time()
        
        log_method = getattr(logger, self.log_level.lower(), logger.info)
        log_method(
            f"→ BEGIN OPERATION: {self.operation_name}",
            operation=self.operation_name,
            **self.metadata
        )
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = round((time.time() - self.start_time) * 1000, 2)
        
        context = {
            "operation": self.operation_name,
            "duration_ms": duration_ms,
            **self.metadata
        }
        
        if exc_type is None:
            # Success
            logger.info(
                f"✓ OPERATION COMPLETE: {self.operation_name}",
                status="SUCCESS",
                **context
            )
        else:
            # Failure
            context["exception_type"] = exc_type.__name__
            context["exception_message"] = str(exc_val)
            
            logger.error(
                f"✗ OPERATION FAILED: {self.operation_name}",
                status="FAILED",
                exc_info=True,
                **context
            )
        
        # Don't suppress exceptions
        return False


# Convenience function for manual operation logging
def log_operation(operation_name: str, log_level: str = "INFO", **metadata):
    """
    Creates an OperationLogger context manager
    
    Example:
        with log_operation("database_migration", version="1.2.3"):
            migrate_database()
    """
    return OperationLogger(operation_name, log_level, **metadata)


__all__ = [
    'log_function',
    'log_async_function',
    'log_state_transition',
    'log_retry_operation',
    'log_operation',
    'OperationLogger',
]
