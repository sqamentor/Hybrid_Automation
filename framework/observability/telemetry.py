"""OpenTelemetry integration for distributed tracing and observability.

Provides instrumentation for:
- HTTP requests (httpx)
- Database operations (asyncpg, aiomysql)
- Test execution
- Custom spans for business logic
"""
import asyncio
from contextlib import asynccontextmanager, contextmanager
from functools import wraps
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Iterator,
    Optional,
    ParamSpec,
    TypeVar,
)

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import Status, StatusCode


FuncParams = ParamSpec("FuncParams")
FuncReturn = TypeVar("FuncReturn")
AsyncFuncReturn = TypeVar("AsyncFuncReturn")
TestParams = ParamSpec("TestParams")
TestReturn = TypeVar("TestReturn")
AsyncTestReturn = TypeVar("AsyncTestReturn")


class TelemetryConfig:
    """Configuration for OpenTelemetry."""
    
    def __init__(
        self,
        service_name: str = "test-automation-framework",
        environment: str = "development",
        otlp_endpoint: Optional[str] = None,
        enable_console: bool = True,
        enable_otlp: bool = False
    ):
        """Initialize telemetry configuration.

        Args:
            service_name: Name of the service for tracing
            environment: Environment (dev, staging, prod)
            otlp_endpoint: OTLP collector endpoint (e.g., "http://localhost:4317")
            enable_console: Enable console exporter for debugging
            enable_otlp: Enable OTLP exporter for production
        """
        self.service_name = service_name
        self.environment = environment
        self.otlp_endpoint = otlp_endpoint or "http://localhost:4317"
        self.enable_console = enable_console
        self.enable_otlp = enable_otlp


class TelemetryManager:
    """Manages OpenTelemetry instrumentation and tracing.

    Example:
        ```python
        from framework.observability.telemetry import TelemetryManager, TelemetryConfig

        # Initialize
        config = TelemetryConfig(
            service_name="my-tests",
            environment="staging",
            enable_console=True
        )
        telemetry = TelemetryManager(config)
        telemetry.initialize()

        # Use in code
        with telemetry.span("test_execution", {"test_name": "test_login"}):
            # Your test code
            pass

        # Cleanup
        telemetry.shutdown()
        ```
    """
    
    def __init__(self, config: TelemetryConfig):
        """Initialize telemetry manager.

        Args:
            config: Telemetry configuration
        """
        self.config = config
        self.tracer_provider: Optional[TracerProvider] = None
        self.tracer: Optional[trace.Tracer] = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize OpenTelemetry with configured exporters.

        Sets up:
        - TracerProvider with service resource
        - Console exporter (if enabled)
        - OTLP exporter (if enabled)
        - HTTPX instrumentation
        """
        if self._initialized:
            return
        
        # Create resource with service information
        resource = Resource.create({
            "service.name": self.config.service_name,
            "service.environment": self.config.environment,
            "service.version": "1.0.0"
        })
        
        # Create tracer provider
        self.tracer_provider = TracerProvider(resource=resource)
        
        # Add console exporter
        if self.config.enable_console:
            console_exporter = ConsoleSpanExporter()
            console_processor = BatchSpanProcessor(console_exporter)
            self.tracer_provider.add_span_processor(console_processor)
        
        # Add OTLP exporter
        if self.config.enable_otlp:
            otlp_exporter = OTLPSpanExporter(endpoint=self.config.otlp_endpoint)
            otlp_processor = BatchSpanProcessor(otlp_exporter)
            self.tracer_provider.add_span_processor(otlp_processor)
        
        # Set global tracer provider
        trace.set_tracer_provider(self.tracer_provider)
        
        # Get tracer
        self.tracer = trace.get_tracer(__name__)
        
        # Instrument HTTPX
        HTTPXClientInstrumentor().instrument()
        
        self._initialized = True
    
    @contextmanager
    def span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        kind: trace.SpanKind = trace.SpanKind.INTERNAL
    ) -> Iterator[Optional[trace.Span]]:
        """Create a traced span context.

        Args:
            name: Name of the span
            attributes: Additional attributes for the span
            kind: Span kind (INTERNAL, CLIENT, SERVER, etc.)

        Yields:
            The created span

        Example:
            ```python
            with telemetry.span("database_query", {"table": "users"}):
                result = db.query("SELECT * FROM users")
            ```
        """
        if not self._initialized or not self.tracer:
            yield None
            return
        
        with self.tracer.start_as_current_span(name, kind=kind) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, str(value))
            
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR))
                span.record_exception(e)
                raise
    
    @asynccontextmanager
    async def async_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        kind: trace.SpanKind = trace.SpanKind.INTERNAL
    ) -> AsyncIterator[Optional[trace.Span]]:
        """Create an async traced span context.

        Args:
            name: Name of the span
            attributes: Additional attributes for the span
            kind: Span kind

        Yields:
            The created span

        Example:
            ```python
            async with telemetry.async_span("api_request", {"endpoint": "/api/users"}):
                response = await client.get("/api/users")
            ```
        """
        if not self._initialized or not self.tracer:
            yield None
            return
        
        with self.tracer.start_as_current_span(name, kind=kind) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, str(value))
            
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR))
                span.record_exception(e)
                raise
    
    def trace_function(
        self,
        span_name: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> Callable[[Callable[FuncParams, FuncReturn]], Callable[FuncParams, FuncReturn]]:
        """Decorator to automatically trace a function.

        Args:
            span_name: Optional span name (defaults to function name)
            attributes: Additional attributes for the span

        Returns:
            Decorated function

        Example:
            ```python
            @telemetry.trace_function(attributes={"component": "auth"})
            def login(username: str, password: str):
                # Function code
                pass
            ```
        """
        def decorator(func: Callable[FuncParams, FuncReturn]) -> Callable[FuncParams, FuncReturn]:
            name = span_name or func.__name__
            
            @wraps(func)
            def wrapper(*args: FuncParams.args, **kwargs: FuncParams.kwargs) -> FuncReturn:
                with self.span(name, attributes):
                    return func(*args, **kwargs)
            
            return wrapper
        
        return decorator
    
    def trace_async_function(
        self,
        span_name: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> Callable[[Callable[FuncParams, Awaitable[AsyncFuncReturn]]], Callable[FuncParams, Awaitable[AsyncFuncReturn]]]:
        """Decorator to automatically trace an async function.

        Args:
            span_name: Optional span name (defaults to function name)
            attributes: Additional attributes for the span

        Returns:
            Decorated async function

        Example:
            ```python
            @telemetry.trace_async_function(attributes={"component": "api"})
            async def fetch_user(user_id: int):
                # Async function code
                pass
            ```
        """
        def decorator(
            func: Callable[FuncParams, Awaitable[AsyncFuncReturn]]
        ) -> Callable[FuncParams, Awaitable[AsyncFuncReturn]]:
            name = span_name or func.__name__
            
            @wraps(func)
            async def wrapper(
                *args: FuncParams.args,
                **kwargs: FuncParams.kwargs,
            ) -> AsyncFuncReturn:
                async with self.async_span(name, attributes):
                    return await func(*args, **kwargs)
            
            return wrapper
        
        return decorator
    
    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add an event to the current span.

        Args:
            name: Event name
            attributes: Event attributes

        Example:
            ```python
            with telemetry.span("test_execution"):
                telemetry.add_event("test_started", {"test_id": "test_001"})
                # Run test
                telemetry.add_event("test_completed", {"result": "passed"})
            ```
        """
        current_span = trace.get_current_span()
        if current_span:
            current_span.add_event(name, attributes or {})
    
    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute on the current span.

        Args:
            key: Attribute key
            value: Attribute value
        """
        current_span = trace.get_current_span()
        if current_span:
            current_span.set_attribute(key, str(value))
    
    def record_exception(self, exception: Exception) -> None:
        """Record an exception in the current span.

        Args:
            exception: The exception to record
        """
        current_span = trace.get_current_span()
        if current_span:
            current_span.record_exception(exception)
            current_span.set_status(Status(StatusCode.ERROR))
    
    def shutdown(self) -> None:
        """Shutdown telemetry and flush all spans.

        Call this before application exit to ensure all spans are exported.
        """
        if self.tracer_provider:
            self.tracer_provider.shutdown()
        
        self._initialized = False


# ============================================================================
# Global Telemetry Instance
# ============================================================================

# Singleton telemetry manager
_global_telemetry: Optional[TelemetryManager] = None


def get_telemetry() -> TelemetryManager:
    """Get the global telemetry manager instance.

    Returns:
        Global TelemetryManager instance

    Raises:
        RuntimeError: If telemetry not initialized

    Example:
        ```python
        telemetry = get_telemetry()
        with telemetry.span("my_operation"):
            # Code
            pass
        ```
    """
    global _global_telemetry
    
    if _global_telemetry is None:
        raise RuntimeError(
            "Telemetry not initialized. Call initialize_telemetry() first."
        )
    
    return _global_telemetry


def initialize_telemetry(config: TelemetryConfig) -> TelemetryManager:
    """Initialize global telemetry manager.

    Args:
        config: Telemetry configuration

    Returns:
        Initialized TelemetryManager

    Example:
        ```python
        from framework.observability.telemetry import initialize_telemetry, TelemetryConfig

        config = TelemetryConfig(
            service_name="my-service",
            enable_console=True,
            enable_otlp=False
        )

        telemetry = initialize_telemetry(config)
        ```
    """
    global _global_telemetry
    
    _global_telemetry = TelemetryManager(config)
    _global_telemetry.initialize()
    
    return _global_telemetry


def shutdown_telemetry() -> None:
    """Shutdown global telemetry manager.

    Call this before application exit.

    Example:
        ```python
        from framework.observability.telemetry import shutdown_telemetry

        # At application exit
        shutdown_telemetry()
        ```
    """
    global _global_telemetry
    
    if _global_telemetry:
        _global_telemetry.shutdown()
        _global_telemetry = None


# ============================================================================
# Test Instrumentation Helpers
# ============================================================================

class TestTracer:
    """Helper class for instrumenting pytest tests with OpenTelemetry.

    Example:
        ```python
        # conftest.py
        from framework.observability.telemetry import TestTracer

        tracer = TestTracer()

        @pytest.fixture(autouse=True)
        def trace_test(request):
            tracer.start_test(request.node.name)
            yield
            tracer.end_test(request.node.name)
        ```
    """
    
    def __init__(self, telemetry: Optional[TelemetryManager] = None):
        """Initialize test tracer.

        Args:
            telemetry: Optional telemetry manager (uses global if not provided)
        """
        self.telemetry = telemetry
        self._test_spans: Dict[str, trace.Span] = {}
    
    def start_test(self, test_name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Start tracing a test.

        Args:
            test_name: Name of the test
            attributes: Additional test attributes
        """
        if not self.telemetry:
            try:
                self.telemetry = get_telemetry()
            except RuntimeError:
                return
        
        telemetry = self.telemetry
        tracer = telemetry.tracer if telemetry else None
        if telemetry is None or tracer is None:
            return

        attrs = attributes or {}
        attrs["test.name"] = test_name
        
        span = tracer.start_span(
            f"test:{test_name}",
            kind=trace.SpanKind.INTERNAL
        )
        
        for key, value in attrs.items():
            span.set_attribute(key, str(value))
        
        self._test_spans[test_name] = span
    
    def end_test(
        self,
        test_name: str,
        status: str = "passed",
        error: Optional[Exception] = None
    ) -> None:
        """End tracing a test.

        Args:
            test_name: Name of the test
            status: Test status (passed, failed, skipped)
            error: Optional exception if test failed
        """
        if test_name not in self._test_spans:
            return
        
        span = self._test_spans[test_name]
        span.set_attribute("test.status", status)
        
        if error:
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR))
        else:
            span.set_status(Status(StatusCode.OK))
        
        span.end()
        del self._test_spans[test_name]
    
    def add_test_event(self, test_name: str, event: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add an event to a test span.

        Args:
            test_name: Name of the test
            event: Event name
            attributes: Event attributes
        """
        if test_name in self._test_spans:
            span = self._test_spans[test_name]
            span.add_event(event, attributes or {})


# ============================================================================
# Convenience Functions
# ============================================================================

def trace_test_execution(test_name: str) -> Callable[[Callable[TestParams, TestReturn]], Callable[TestParams, TestReturn]]:
    """Decorator for tracing test execution.

    Args:
        test_name: Name of the test

    Returns:
        Decorated test function

    Example:
        ```python
        @trace_test_execution("test_user_login")
        def test_user_login():
            # Test code
            pass
        ```
    """
    def decorator(func: Callable[TestParams, TestReturn]) -> Callable[TestParams, TestReturn]:
        @wraps(func)
        def wrapper(*args: TestParams.args, **kwargs: TestParams.kwargs) -> TestReturn:
            try:
                telemetry = get_telemetry()
                with telemetry.span(f"test:{test_name}", {"test.name": test_name}):
                    return func(*args, **kwargs)
            except RuntimeError:
                # Telemetry not initialized, run without tracing
                return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def trace_async_test_execution(test_name: str) -> Callable[[Callable[TestParams, Awaitable[AsyncTestReturn]]], Callable[TestParams, Awaitable[AsyncTestReturn]]]:
    """Decorator for tracing async test execution.

    Args:
        test_name: Name of the test

    Returns:
        Decorated async test function

    Example:
        ```python
        @trace_async_test_execution("test_async_api_call")
        async def test_async_api_call():
            # Async test code
            pass
        ```
    """
    def decorator(
        func: Callable[TestParams, Awaitable[AsyncTestReturn]]
    ) -> Callable[TestParams, Awaitable[AsyncTestReturn]]:
        @wraps(func)
        async def wrapper(
            *args: TestParams.args,
            **kwargs: TestParams.kwargs,
        ) -> AsyncTestReturn:
            try:
                telemetry = get_telemetry()
                async with telemetry.async_span(f"test:{test_name}", {"test.name": test_name}):
                    return await func(*args, **kwargs)
            except RuntimeError:
                # Telemetry not initialized, run without tracing
                return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator
