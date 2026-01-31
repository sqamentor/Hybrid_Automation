"""
Microservices Architecture Base

Modern microservice foundation with service discovery, health checks,
and event-driven communication patterns.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol
from pathlib import Path
import asyncio
import json
import re


class ServiceList(list):
    """Custom list that supports 'in' operator with service names"""
    def __contains__(self, item):
        if isinstance(item, str):
            # Check by name
            return any(getattr(s, 'name', None) == item for s in self)
        # Default behavior for objects
        return super().__contains__(item)


class ServiceStatus(str, Enum):
    """Service health status"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class HealthCheck:
    """Service health check result"""
    service_name: str
    status: ServiceStatus
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    checks: List[str] = field(default_factory=list)
    
    @property
    def is_healthy(self) -> bool:
        """Check if service is healthy"""
        return self.status == ServiceStatus.HEALTHY


@dataclass
class ServiceInfo:
    """Service registration information"""
    name: str
    version: str
    host: str
    port: int
    endpoints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    @property
    def base_url(self) -> str:
        """Get service base URL"""
        return f"http://{self.host}:{self.port}"


@dataclass
class Message:
    """Event-driven message"""
    event: str  # Alias for topic to match test expectations
    data: Optional[Dict[str, Any]] = None  # Alias for payload
    sender: str = ""  # Make sender optional with default
    timestamp: float = field(default_factory=lambda: __import__('time').time())
    priority: MessagePriority = MessagePriority.NORMAL
    correlation_id: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    @property
    def topic(self) -> str:
        """Alias for event"""
        return self.event
    
    @property
    def payload(self) -> Optional[Dict[str, Any]]:
        """Alias for data"""
        return self.data


class IService(Protocol):
    """Service interface protocol"""
    
    @property
    def name(self) -> str:
        """Service name"""
        ...
    
    @property
    def version(self) -> str:
        """Service version"""
        ...
    
    async def start(self) -> None:
        """Start service"""
        ...
    
    async def stop(self) -> None:
        """Stop service"""
        ...
    
    async def health_check(self) -> HealthCheck:
        """Perform health check"""
        ...


class BaseService(ABC):
    """
    Base class for microservices.
    
    Provides:
    - Service lifecycle management
    - Health check framework
    - Event publishing/subscription
    - Dependency injection support
    """
    
    def __init__(self, name: str, version: str = "1.0.0", host: str = "localhost", port: int = 0):
        self._name = name
        self._version = version
        self._host = host
        self._port = port
        self._status = ServiceStatus.STOPPED
        self._message_handlers: Dict[str, List[Callable]] = {}
        self._health_checks: List[Callable[[], bool]] = []
    
    @property
    def name(self) -> str:
        """Get service name"""
        return self._name
    
    @property
    def version(self) -> str:
        """Get service version"""
        return self._version
    
    @property
    def status(self) -> ServiceStatus:
        """Get current service status"""
        return self._status
    
    @status.setter
    def status(self, value: ServiceStatus) -> None:
        """Set service status"""
        self._status = value
    
    @property
    def info(self) -> ServiceInfo:
        """Get service information"""
        return ServiceInfo(
            name=self._name,
            version=self._version,
            host=self._host,
            port=self._port,
            endpoints=self.get_endpoints(),
            metadata=self.get_metadata(),
            tags=self.get_tags(),
        )
    
    async def start(self) -> None:
        """Start the service"""
        self._status = ServiceStatus.STARTING
        await self.on_start()
        self._status = ServiceStatus.RUNNING
    
    async def stop(self) -> None:
        """Stop the service"""
        self._status = ServiceStatus.STOPPING
        await self.on_stop()
        self._status = ServiceStatus.STOPPED
    
    async def health_check(self) -> HealthCheck:
        """
        Perform comprehensive health check.
        
        Returns:
            HealthCheck result
        """
        checks_passed = []
        checks_failed = []
        
        for health_check_fn in self._health_checks:
            try:
                if await self._run_health_check(health_check_fn):
                    checks_passed.append(health_check_fn.__name__)
                else:
                    checks_failed.append(health_check_fn.__name__)
            except Exception as e:
                checks_failed.append(f"{health_check_fn.__name__}: {str(e)}")
        
        # Determine overall status
        if not checks_failed:
            status = ServiceStatus.HEALTHY
        elif len(checks_failed) < len(self._health_checks) / 2:
            status = ServiceStatus.DEGRADED
        else:
            status = ServiceStatus.UNHEALTHY
        
        return HealthCheck(
            service_name=self._name,
            status=status,
            timestamp=datetime.now(),
            details={
                'passed': checks_passed,
                'failed': checks_failed,
                'total': len(self._health_checks)
            },
            checks=checks_passed + checks_failed
        )
    
    async def _run_health_check(self, check_fn: Callable) -> bool:
        """Run a single health check function"""
        if asyncio.iscoroutinefunction(check_fn):
            return await check_fn()
        return check_fn()
    
    def register_health_check(self, check_fn: Callable[[], bool]) -> None:
        """Register a health check function"""
        self._health_checks.append(check_fn)
    
    def subscribe(self, topic: str, handler: Callable[[Message], None]) -> None:
        """
        Subscribe to message topic.
        
        Args:
            topic: Topic to subscribe to
            handler: Message handler function
        """
        if topic not in self._message_handlers:
            self._message_handlers[topic] = []
        self._message_handlers[topic].append(handler)
    
    async def publish(self, message: Message) -> None:
        """
        Publish message to subscribers.
        
        Args:
            message: Message to publish
        """
        handlers = self._message_handlers.get(message.topic, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                # Log error but continue processing other handlers
                await self.on_message_error(message, e)
    
    # Methods for subclasses to override
    
    async def on_start(self) -> None:
        """Service startup logic (override if needed)"""
        pass
    
    async def on_stop(self) -> None:
        """Service shutdown logic (override if needed)"""
        pass
    
    def get_endpoints(self) -> List[str]:
        """Get service endpoints (override if needed)"""
        return []
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get service metadata (override if needed)"""
        return {}
    
    def get_tags(self) -> List[str]:
        """Get service tags (override if needed)"""
        return []
    
    async def on_message_error(self, message: Message, error: Exception) -> None:
        """Handle message processing errors (override if needed)"""
        pass


class ServiceRegistry:
    """
    Service registry for service discovery.
    
    Features:
    - Service registration/deregistration
    - Service discovery by name or tags
    - Health check monitoring
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._services: Dict[str, ServiceInfo] = {}
        self._service_instances: Dict[str, BaseService] = {}  # Store actual service objects
        self._health_cache: Dict[str, HealthCheck] = {}
        self._initialized = True
    
    def register(self, service_or_info) -> None:
        """Register a service (accepts BaseService or ServiceInfo)"""
        if isinstance(service_or_info, BaseService):
            # Store the service instance
            service = service_or_info
            self._service_instances[service.name] = service
            # Create ServiceInfo from BaseService
            service_info = service.info
            self._services[service.name] = service_info
        else:
            # ServiceInfo object
            self._services[service_or_info.name] = service_or_info
    
    def deregister(self, service_name: str) -> None:
        """Deregister a service"""
        self._services.pop(service_name, None)
        self._service_instances.pop(service_name, None)
        self._health_cache.pop(service_name, None)
    
    def unregister(self, service_name: str) -> None:
        """Alias for deregister"""
        self.deregister(service_name)
    
    def discover(self, service_name: str) -> Optional[ServiceInfo]:
        """Discover service by name"""
        return self._services.get(service_name)
    
    def get(self, service_name: str) -> Optional[BaseService]:
        """Get service instance by name (alias for getting registered service instance)"""
        return self._service_instances.get(service_name)
    
    def discover_by_tag(self, tag: str) -> List[ServiceInfo]:
        """Discover services by tag"""
        return [
            service for service in self._services.values()
            if tag in service.tags
        ]
    
    def get_all_services(self) -> List[ServiceInfo]:
        """Get all registered services"""
        return list(self._services.values())
    
    def get_all(self) -> ServiceList:
        """Get all registered service instances (alias)"""
        return ServiceList(self._service_instances.values())
    
    def update_health(self, service_name: str, health: HealthCheck) -> None:
        """Update service health status"""
        self._health_cache[service_name] = health
    
    def get_healthy_services(self) -> List[ServiceInfo]:
        """Get all healthy services"""
        return [
            service for service in self._services.values()
            if service.name in self._health_cache
            and self._health_cache[service.name].is_healthy
        ]
    
    async def start_all(self) -> None:
        """Start all registered service instances"""
        for service in self._service_instances.values():
            await service.start()
    
    async def stop_all(self) -> None:
        """Stop all registered service instances"""
        for service in self._service_instances.values():
            await service.stop()
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all registered service instances"""
        results = {}
        for name, service in self._service_instances.items():
            results[name] = await service.health_check()
        return results


class MessageBus:
    """
    Simple in-memory message bus for event-driven communication.
    
    Features:
    - Topic-based pub/sub
    - Priority message queues
    - Message filtering
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._subscribers: Dict[str, List[Callable]] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._initialized = True
    
    def subscribe(self, topic: str, handler: Callable[[Message], None]) -> None:
        """Subscribe to topic"""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)
    
    def unsubscribe(self, topic: str, handler: Callable[[Message], None]) -> None:
        """Unsubscribe from topic"""
        if topic in self._subscribers:
            self._subscribers[topic].remove(handler)
    
    async def publish(self, event_or_message, data: Optional[Dict[str, Any]] = None) -> None:
        """Publish message to topic. Accepts either (event, data) or (Message object)"""
        if isinstance(event_or_message, Message):
            message = event_or_message
        else:
            # Create message from event and data
            message = Message(event=event_or_message, data=data)
        
        # Find matching handlers (exact match + wildcard patterns)
        handlers = []
        for topic_pattern, topic_handlers in self._subscribers.items():
            if self._matches_pattern(message.event, topic_pattern):
                handlers.extend(topic_handlers)
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                # Log error but continue
                print(f"Error in message handler: {e}")
    
    def _matches_pattern(self, event: str, pattern: str) -> bool:
        """Check if event matches pattern (supports * wildcard)"""
        if "*" not in pattern:
            return event == pattern
        
        # Simple wildcard matching
        import re
        regex_pattern = pattern.replace(".", r"\.").replace("*", ".*")
        return re.match(f"^{regex_pattern}$", event) is not None
    
    def get_subscriber_count(self, topic: str) -> int:
        """Get number of subscribers for topic"""
        return len(self._subscribers.get(topic, []))


# Global registry and message bus instances
_service_registry = ServiceRegistry()
_message_bus = MessageBus()


def get_service_registry() -> ServiceRegistry:
    """Get global service registry"""
    return _service_registry


def get_message_bus() -> MessageBus:
    """Get global message bus"""
    return _message_bus
