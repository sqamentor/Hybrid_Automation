"""Observability package for telemetry, monitoring, and enterprise logging."""

# Telemetry imports (optional dependency)
try:
    from framework.observability.telemetry import (
        TelemetryConfig,
        TelemetryManager,
        TestTracer,
        get_telemetry,
        initialize_telemetry,
        shutdown_telemetry,
        trace_async_test_execution,
        trace_test_execution,
    )
    TELEMETRY_AVAILABLE = True
except ImportError as e:
    # Use a structured logger instead of root logger
    import logging
    _observability_logger = logging.getLogger('framework.observability')
    _observability_logger.warning(f"Telemetry not available (OpenTelemetry not installed): {e}")
    TELEMETRY_AVAILABLE = False
    TelemetryConfig = None
    TelemetryManager = None
    TestTracer = None
    
    def get_telemetry():
        return None
    
    def initialize_telemetry(*args, **kwargs):
        pass
    
    def shutdown_telemetry(*args, **kwargs):
        pass
    
    def trace_test_execution(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def trace_async_test_execution(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Enterprise Logging imports
from framework.observability.enterprise_logger import (
    EnterpriseLogger,
    get_enterprise_logger,
    CorrelationContext,
    SensitiveDataMasker,
    AuditLogger,
    SecurityLogger,
    PerformanceLogger,
    with_correlation,
    with_trace,
    with_async_trace,
)

# Configuration imports
from framework.observability.logging_config import (
    Environment,
    LogLevel,
    EnvironmentConfig,
    LoggingConfigManager,
    get_logging_config,
    RetentionPolicy,
    SamplingConfig,
    SIEMConfig,
    AlertConfig,
    SecurityConfig,
    PerformanceConfig,
)

# SIEM Adapters imports (optional dependency)
try:
    from framework.observability.siem_adapters import (
        SIEMProvider,
        BaseSIEMAdapter,
        ElasticsearchAdapter,
        DatadogAdapter,
        SplunkAdapter,
        GrafanaLokiAdapter,
        SIEMAdapterFactory,
        CircuitBreaker,
    )
    SIEM_AVAILABLE = True
except ImportError:
    SIEM_AVAILABLE = False
    SIEMProvider = None
    BaseSIEMAdapter = None
    ElasticsearchAdapter = None
    DatadogAdapter = None
    SplunkAdapter = None
    GrafanaLokiAdapter = None
    SIEMAdapterFactory = None
    CircuitBreaker = None

# Universal Logger Decorators imports
from framework.observability.universal_logger import (
    log_function,
    log_async_function,
    log_state_transition,
    log_retry_operation,
    log_operation,
    OperationLogger,
)

__all__ = [
    # Telemetry (optional)
    "TelemetryConfig",
    "TelemetryManager",
    "TestTracer",
    "get_telemetry",
    "initialize_telemetry",
    "shutdown_telemetry",
    "trace_test_execution",
    "trace_async_test_execution",
    "TELEMETRY_AVAILABLE",
    # Enterprise Logging
    "EnterpriseLogger",
    "get_enterprise_logger",
    "CorrelationContext",
    "SensitiveDataMasker",
    "AuditLogger",
    "SecurityLogger",
    "PerformanceLogger",
    "with_correlation",
    "with_trace",
    "with_async_trace",
    # Configuration
    "Environment",
    "LogLevel",
    "EnvironmentConfig",
    "LoggingConfigManager",
    "get_logging_config",
    "RetentionPolicy",
    "SamplingConfig",
    "SIEMConfig",
    "AlertConfig",
    "SecurityConfig",
    "PerformanceConfig",
    # SIEM Adapters (optional)
    "SIEMProvider",
    "BaseSIEMAdapter",
    "ElasticsearchAdapter",
    "DatadogAdapter",
    "SplunkAdapter",
    "GrafanaLokiAdapter",
    "SIEMAdapterFactory",
    "CircuitBreaker",
    "SIEM_AVAILABLE",
    # Universal Logger Decorators
    "log_function",
    "log_async_function",
    "log_state_transition",
    "log_retry_operation",
    "log_operation",
    "OperationLogger",
]
