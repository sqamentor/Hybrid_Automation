"""
Dependency Injection Container

Modern DI container using Python 3.12+ features for clean microservices architecture.
Supports singleton, transient, and scoped lifetimes with lazy initialization.
"""

from __future__ import annotations

import inspect
import logging
from contextvars import ContextVar
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Generic, Optional, Type, TypeVar, cast

from framework.observability.universal_logger import log_function

logger = logging.getLogger(__name__)
T = TypeVar("T")


class Lifetime(str, Enum):
    """Service lifetime options"""

    SINGLETON = "singleton"  # Single instance for application lifetime
    TRANSIENT = "transient"  # New instance every time
    SCOPED = "scoped"  # Single instance per scope (e.g., per test)


class ServiceDescriptor(Generic[T]):
    """Describes a registered service"""

    def __init__(
        self,
        service_type: Type[T],
        implementation: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
        instance: Optional[T] = None,
        lifetime: Lifetime = Lifetime.SINGLETON,
    ):
        self.service_type = service_type
        self.implementation = implementation
        self.factory = factory
        self.instance = instance
        self.lifetime = lifetime

        if not any([implementation, factory, instance]):
            raise ValueError("Must provide implementation, factory, or instance")


class DIContainer:
    """
    Dependency Injection Container with microservices support.

    Features:
    - Constructor injection with type hints
    - Multiple lifetime management (singleton, transient, scoped)
    - Lazy initialization
    - Protocol-based interfaces
    - Scope management for isolated contexts
    """

    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scope_context: ContextVar[Dict[Type, Any]] = ContextVar("scope_context", default={})

    @log_function(log_args=True)
    def register(
        self,
        service_type: Type[T],
        implementation: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
        instance: Optional[T] = None,
        lifetime: Lifetime = Lifetime.SINGLETON,
    ) -> DIContainer:
        """
        Register a service in the container.

        Args:
            service_type: Interface or base class
            implementation: Concrete implementation class
            factory: Factory function to create instances
            instance: Pre-created instance
            lifetime: Service lifetime (singleton/transient/scoped)

        Returns:
            Self for method chaining
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=implementation,
            factory=factory,
            instance=instance,
            lifetime=lifetime,
        )
        self._services[service_type] = descriptor

        # Store singleton instance if provided
        if instance is not None and lifetime == Lifetime.SINGLETON:
            self._singletons[service_type] = instance

        return self

    @log_function(log_args=True)
    def register_singleton(
        self,
        service_type: Type[T],
        implementation: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
        instance: Optional[T] = None,
    ) -> DIContainer:
        """Register a singleton service"""
        return self.register(
            service_type,
            implementation=implementation,
            factory=factory,
            instance=instance,
            lifetime=Lifetime.SINGLETON,
        )

    @log_function(log_args=True)
    def register_transient(
        self,
        service_type: Type[T],
        implementation: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
    ) -> DIContainer:
        """Register a transient service (new instance each time)"""
        return self.register(
            service_type,
            implementation=implementation,
            factory=factory,
            lifetime=Lifetime.TRANSIENT,
        )

    @log_function(log_args=True)
    def register_scoped(
        self,
        service_type: Type[T],
        implementation: Optional[Type[T]] = None,
        factory: Optional[Callable[..., T]] = None,
    ) -> DIContainer:
        """Register a scoped service (one instance per scope)"""
        return self.register(
            service_type,
            implementation=implementation,
            factory=factory,
            lifetime=Lifetime.SCOPED,
        )

    @log_function(log_args=True, log_result=True, log_timing=True)
    def resolve(self, service_type: Type[T]) -> T:
        """
        Resolve a service from the container.

        Args:
            service_type: Type to resolve

        Returns:
            Instance of the requested type

        Raises:
            ValueError: If service not registered
        """
        if service_type not in self._services:
            raise ValueError(f"Service {service_type.__name__} not registered")

        descriptor = self._services[service_type]

        # Handle based on lifetime
        match descriptor.lifetime:
            case Lifetime.SINGLETON:
                return self._resolve_singleton(descriptor)
            case Lifetime.TRANSIENT:
                return self._create_instance(descriptor)
            case Lifetime.SCOPED:
                return self._resolve_scoped(descriptor)
            case _:
                raise ValueError(f"Unknown lifetime: {descriptor.lifetime}")

    @log_function(log_timing=True)
    def _resolve_singleton(self, descriptor: ServiceDescriptor[T]) -> T:
        """Resolve singleton instance"""
        if descriptor.service_type in self._singletons:
            return cast(T, self._singletons[descriptor.service_type])

        # Create and cache singleton
        instance = self._create_instance(descriptor)
        self._singletons[descriptor.service_type] = instance
        return instance

    @log_function(log_timing=True)
    def _resolve_scoped(self, descriptor: ServiceDescriptor[T]) -> T:
        """Resolve scoped instance"""
        scope = self._scope_context.get()

        if descriptor.service_type in scope:
            return cast(T, scope[descriptor.service_type])

        # Create and cache in scope
        instance = self._create_instance(descriptor)
        scope[descriptor.service_type] = instance
        return instance

    @log_function(log_timing=True)
    def _create_instance(self, descriptor: ServiceDescriptor[T]) -> T:
        """Create new instance using factory or constructor"""
        # If instance provided, return it
        if descriptor.instance is not None:
            return descriptor.instance

        # If factory provided, use it
        if descriptor.factory is not None:
            return self._invoke_factory(descriptor.factory)

        # Otherwise use constructor
        if descriptor.implementation is not None:
            return self._invoke_constructor(descriptor.implementation)

        raise ValueError(f"Cannot create instance of {descriptor.service_type}")

    @log_function(log_timing=True)
    def _invoke_factory(self, factory: Callable[..., T]) -> T:
        """Invoke factory with dependency injection"""
        sig = inspect.signature(factory)
        kwargs = {}

        for param_name, param in sig.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                # Resolve dependency
                dependency = self.resolve(param.annotation)
                kwargs[param_name] = dependency

        return factory(**kwargs)

    @log_function(log_timing=True)
    def _invoke_constructor(self, cls: Type[T]) -> T:
        """Invoke constructor with dependency injection"""
        sig = inspect.signature(cls.__init__)
        kwargs = {}

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            if param.annotation != inspect.Parameter.empty:
                # Resolve dependency
                try:
                    dependency = self.resolve(param.annotation)
                    kwargs[param_name] = dependency
                except ValueError:
                    # If dependency not registered, skip if has default
                    if param.default == inspect.Parameter.empty:
                        raise

        return cls(**kwargs)

    @log_function()
    def create_scope(self) -> DIScope:
        """Create a new dependency scope"""
        return DIScope(self)

    @log_function(log_args=True, log_result=True)
    def is_registered(self, service_type: Type) -> bool:
        """Check if service is registered"""
        return service_type in self._services

    @log_function()
    def clear(self) -> None:
        """Clear all registrations and cached instances"""
        self._services.clear()
        self._singletons.clear()


class DIScope:
    """
    Dependency injection scope context manager.
    Services with SCOPED lifetime will be cached within this scope.
    """

    def __init__(self, container: DIContainer):
        self.container = container
        self._scope_storage: Dict[Type, Any] = {}
        self._token = None

    @log_function()
    def __enter__(self) -> DIScope:
        """Enter scope context"""
        self._token = self.container._scope_context.set(self._scope_storage)
        return self

    @log_function()
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit scope context and cleanup"""
        if self._token:
            self.container._scope_context.reset(self._token)
        self._scope_storage.clear()


# Decorator for automatic dependency injection
def inject(container: DIContainer):
    """
    Decorator to automatically inject dependencies into function.

    Usage:
        @inject(container)
        def my_function(service: MyService):
            service.do_something()
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            injected_kwargs = {}

            for param_name, param in sig.parameters.items():
                if param_name in kwargs:
                    continue

                if param.annotation != inspect.Parameter.empty:
                    try:
                        dependency = container.resolve(param.annotation)
                        injected_kwargs[param_name] = dependency
                    except ValueError:
                        if param.default == inspect.Parameter.empty:
                            raise

            return func(*args, **kwargs, **injected_kwargs)

        return wrapper

    return decorator


# Global container instance
_global_container: Optional[DIContainer] = None


@log_function(log_result=True)
def get_container() -> DIContainer:
    """Get global DI container instance"""
    global _global_container
    if _global_container is None:
        _global_container = DIContainer()
    return _global_container


@log_function()
def reset_container() -> None:
    """Reset global container (useful for testing)"""
    global _global_container
    if _global_container:
        _global_container.clear()
    _global_container = None
