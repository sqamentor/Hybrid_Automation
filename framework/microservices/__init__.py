"""Microservices Package.

Modern microservices architecture for test automation framework.
"""

from framework.microservices.base import (
    BaseService,
    HealthCheck,
    IService,
    Message,
    MessageBus,
    MessagePriority,
    ServiceInfo,
    ServiceRegistry,
    ServiceStatus,
    get_message_bus,
    get_service_registry,
)

__all__ = [
    "BaseService",
    "IService",
    "ServiceRegistry",
    "MessageBus",
    "ServiceInfo",
    "HealthCheck",
    "Message",
    "ServiceStatus",
    "MessagePriority",
    "get_service_registry",
    "get_message_bus",
]
