"""Unit tests for framework.microservices.base module.

Tests service lifecycle, MessageBus pub/sub, ServiceRegistry, and service health checks.
"""
import asyncio
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from framework.microservices.base import (
    BaseService,
    Message,
    MessageBus,
    ServiceRegistry,
    ServiceStatus,
)

# ============================================================================
# Test BaseService
# ============================================================================

@pytest.mark.modern_spa
@pytest.mark.unit
class TestBaseService:
    """Test BaseService abstract base class."""
    
    def test_service_creation(self):
        """Test service creation with name."""
        
        class DummyService(BaseService):
            async def start(self):
                pass
            
            async def stop(self):
                pass
            
            async def health_check(self) -> Dict[str, Any]:
                return {"status": "healthy"}
        
        service = DummyService("test-service")
        assert service.name == "test-service"
        assert service.status == ServiceStatus.STOPPED
    
    def test_service_status_enum(self):
        """Test ServiceStatus enum values."""
        assert ServiceStatus.STOPPED.value == "stopped"
        assert ServiceStatus.STARTING.value == "starting"
        assert ServiceStatus.RUNNING.value == "running"
        assert ServiceStatus.STOPPING.value == "stopping"
        assert ServiceStatus.ERROR.value == "error"
    
    @pytest.mark.asyncio
    async def test_service_lifecycle(self):
        """Test service start and stop lifecycle."""
        
        @pytest.mark.modern_spa
        class TestService(BaseService):
            def __init__(self, name: str):
                super().__init__(name)
                self.started = False
                self.stopped = False
            
            async def start(self):
                self.status = ServiceStatus.STARTING
                await asyncio.sleep(0.01)
                self.started = True
                self.status = ServiceStatus.RUNNING
            
            async def stop(self):
                self.status = ServiceStatus.STOPPING
                await asyncio.sleep(0.01)
                self.stopped = True
                self.status = ServiceStatus.STOPPED
            
            async def health_check(self) -> Dict[str, Any]:
                return {"status": "healthy", "started": self.started}
        
        service = TestService("test-service")
        
        # Initially stopped
        assert service.status == ServiceStatus.STOPPED
        
        # Start service
        await service.start()
        assert service.status == ServiceStatus.RUNNING
        assert service.started is True
        
        # Stop service
        await service.stop()
        assert service.status == ServiceStatus.STOPPED
        assert service.stopped is True
    
    @pytest.mark.asyncio
    async def test_service_health_check(self):
        """Test service health check."""
        
        class HealthyService(BaseService):
            async def start(self):
                self.status = ServiceStatus.RUNNING
            
            async def stop(self):
                self.status = ServiceStatus.STOPPED
            
            async def health_check(self) -> Dict[str, Any]:
                return {
                    "status": "healthy",
                    "uptime": 100,
                    "requests_processed": 42
                }
        
        service = HealthyService("healthy-service")
        await service.start()
        
        health = await service.health_check()
        assert health["status"] == "healthy"
        assert health["uptime"] == 100
        assert health["requests_processed"] == 42


# ============================================================================
# Test Message
# ============================================================================

@pytest.mark.modern_spa
@pytest.mark.unit
class TestMessage:
    """Test Message dataclass."""
    
    def test_message_creation(self):
        """Test message creation with event and data."""
        message = Message(event="test.event", data={"key": "value"})
        
        assert message.event == "test.event"
        assert message.data == {"key": "value"}
        assert message.timestamp is not None
    
    def test_message_no_data(self):
        """Test message creation without data."""
        message = Message(event="test.event")
        
        assert message.event == "test.event"
        assert message.data is None
    
    def test_message_timestamp(self):
        """Test message timestamp is set."""
        import time
        before = time.time()
        message = Message(event="test.event")
        after = time.time()
        
        assert before <= message.timestamp <= after


# ============================================================================
# Test MessageBus
# ============================================================================

@pytest.mark.modern_spa
@pytest.mark.unit
class TestMessageBus:
    """Test MessageBus pub/sub system."""
    
    @pytest.mark.asyncio
    async def test_messagebus_singleton(self):
        """Test MessageBus is a singleton."""
        bus1 = MessageBus()
        bus2 = MessageBus()
        
        assert bus1 is bus2
    
    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self):
        """Test subscribe and publish basic flow."""
        bus = MessageBus()
        bus._subscribers.clear()  # Clear any previous subscribers
        
        received_messages = []
        
        async def handler(message: Message):
            received_messages.append(message)
        
        # Subscribe to event
        bus.subscribe("test.event", handler)
        
        # Publish message
        await bus.publish("test.event", {"value": 42})
        
        # Wait for async processing
        await asyncio.sleep(0.1)
        
        assert len(received_messages) == 1
        assert received_messages[0].event == "test.event"
        assert received_messages[0].data == {"value": 42}
    
    @pytest.mark.asyncio
    async def test_multiple_subscribers(self):
        """Test multiple subscribers to same event."""
        bus = MessageBus()
        bus._subscribers.clear()
        
        handler1_called = []
        handler2_called = []
        
        async def handler1(message: Message):
            handler1_called.append(message)
        
        async def handler2(message: Message):
            handler2_called.append(message)
        
        # Subscribe both handlers
        bus.subscribe("test.event", handler1)
        bus.subscribe("test.event", handler2)
        
        # Publish message
        await bus.publish("test.event", {"value": 100})
        await asyncio.sleep(0.1)
        
        # Both handlers should receive the message
        assert len(handler1_called) == 1
        assert len(handler2_called) == 1
        assert handler1_called[0].data == {"value": 100}
        assert handler2_called[0].data == {"value": 100}
    
    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        """Test unsubscribe from event."""
        bus = MessageBus()
        bus._subscribers.clear()
        
        received_messages = []
        
        async def handler(message: Message):
            received_messages.append(message)
        
        # Subscribe
        bus.subscribe("test.event", handler)
        
        # Publish first message
        await bus.publish("test.event", {"count": 1})
        await asyncio.sleep(0.1)
        
        # Unsubscribe
        bus.unsubscribe("test.event", handler)
        
        # Publish second message (should not be received)
        await bus.publish("test.event", {"count": 2})
        await asyncio.sleep(0.1)
        
        # Only first message should be received
        assert len(received_messages) == 1
        assert received_messages[0].data == {"count": 1}
    
    @pytest.mark.asyncio
    async def test_publish_no_subscribers(self):
        """Test publish with no subscribers (should not error)."""
        bus = MessageBus()
        bus._subscribers.clear()
        
        # Should not raise exception
        await bus.publish("nonexistent.event", {"data": "test"})
    
    @pytest.mark.asyncio
    async def test_wildcard_subscription(self):
        """Test wildcard event subscription."""
        bus = MessageBus()
        bus._subscribers.clear()
        
        received_messages = []
        
        async def handler(message: Message):
            received_messages.append(message)
        
        # Subscribe to wildcard
        bus.subscribe("test.*", handler)
        
        # Publish multiple events
        await bus.publish("test.event1", {"id": 1})
        await bus.publish("test.event2", {"id": 2})
        await bus.publish("other.event", {"id": 3})  # Should not match
        
        await asyncio.sleep(0.1)
        
        # Should receive 2 messages (test.event1 and test.event2)
        assert len(received_messages) == 2
        assert received_messages[0].event == "test.event1"
        assert received_messages[1].event == "test.event2"


# ============================================================================
# Test ServiceRegistry
# ============================================================================

@pytest.mark.modern_spa
@pytest.mark.unit
class TestServiceRegistry:
    """Test ServiceRegistry for service management."""
    
    def test_registry_singleton(self):
        """Test ServiceRegistry is a singleton."""
        registry1 = ServiceRegistry()
        registry2 = ServiceRegistry()
        
        assert registry1 is registry2
    
    @pytest.mark.asyncio
    async def test_register_service(self):
        """Test registering a service."""
        registry = ServiceRegistry()
        registry._services.clear()
        
        class DummyService(BaseService):
            async def start(self):
                self.status = ServiceStatus.RUNNING
            
            async def stop(self):
                self.status = ServiceStatus.STOPPED
            
            async def health_check(self) -> Dict[str, Any]:
                return {"status": "healthy"}
        
        service = DummyService("test-service")
        registry.register(service)
        
        # Service should be registered
        assert registry.get("test-service") is service
    
    @pytest.mark.asyncio
    async def test_unregister_service(self):
        """Test unregistering a service."""
        registry = ServiceRegistry()
        registry._services.clear()
        
        class DummyService(BaseService):
            async def start(self):
                pass
            
            async def stop(self):
                pass
            
            async def health_check(self) -> Dict[str, Any]:
                return {"status": "healthy"}
        
        service = DummyService("test-service")
        registry.register(service)
        
        # Unregister service
        registry.unregister("test-service")
        
        # Service should not be found
        assert registry.get("test-service") is None
    
    @pytest.mark.asyncio
    async def test_get_all_services(self):
        """Test getting all registered services."""
        registry = ServiceRegistry()
        registry._services.clear()
        
        class DummyService(BaseService):
            async def start(self):
                pass
            
            async def stop(self):
                pass
            
            async def health_check(self) -> Dict[str, Any]:
                return {"status": "healthy"}
        
        service1 = DummyService("service1")
        service2 = DummyService("service2")
        
        registry.register(service1)
        registry.register(service2)
        
        all_services = registry.get_all()
        assert len(all_services) == 2
        assert "service1" in all_services
        assert "service2" in all_services
    
    @pytest.mark.asyncio
    async def test_start_all_services(self):
        """Test starting all registered services."""
        registry = ServiceRegistry()
        registry._services.clear()
        
        class DummyService(BaseService):
            def __init__(self, name: str):
                super().__init__(name)
                self.start_called = False
            
            async def start(self):
                self.start_called = True
                self.status = ServiceStatus.RUNNING
            
            async def stop(self):
                self.status = ServiceStatus.STOPPED
            
            async def health_check(self) -> Dict[str, Any]:
                return {"status": "healthy"}
        
        service1 = DummyService("service1")
        service2 = DummyService("service2")
        
        registry.register(service1)
        registry.register(service2)
        
        # Start all services
        await registry.start_all()
        
        assert service1.start_called is True
        assert service2.start_called is True
        assert service1.status == ServiceStatus.RUNNING
        assert service2.status == ServiceStatus.RUNNING
    
    @pytest.mark.asyncio
    async def test_stop_all_services(self):
        """Test stopping all registered services."""
        registry = ServiceRegistry()
        registry._services.clear()
        
        class DummyService(BaseService):
            def __init__(self, name: str):
                super().__init__(name)
                self.stop_called = False
            
            async def start(self):
                self.status = ServiceStatus.RUNNING
            
            async def stop(self):
                self.stop_called = True
                self.status = ServiceStatus.STOPPED
            
            async def health_check(self) -> Dict[str, Any]:
                return {"status": "healthy"}
        
        service1 = DummyService("service1")
        service2 = DummyService("service2")
        
        registry.register(service1)
        registry.register(service2)
        
        await registry.start_all()
        
        # Stop all services
        await registry.stop_all()
        
        assert service1.stop_called is True
        assert service2.stop_called is True
        assert service1.status == ServiceStatus.STOPPED
        assert service2.status == ServiceStatus.STOPPED
    
    @pytest.mark.asyncio
    async def test_health_check_all(self):
        """Test health check for all services."""
        registry = ServiceRegistry()
        registry._services.clear()
        
        class DummyService(BaseService):
            def __init__(self, name: str):
                super().__init__(name)
            
            async def start(self):
                self.status = ServiceStatus.RUNNING
            
            async def stop(self):
                self.status = ServiceStatus.STOPPED
            
            async def health_check(self) -> Dict[str, Any]:
                return {"status": "healthy", "service": self.name}
        
        service1 = DummyService("service1")
        service2 = DummyService("service2")
        
        registry.register(service1)
        registry.register(service2)
        
        await registry.start_all()
        
        # Check health of all services
        health_results = await registry.health_check_all()
        
        assert len(health_results) == 2
        assert "service1" in health_results
        assert "service2" in health_results
        assert health_results["service1"]["status"] == "healthy"
        assert health_results["service2"]["status"] == "healthy"


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.modern_spa
@pytest.mark.unit
class TestMicroservicesIntegration:
    """Test integration between MessageBus, ServiceRegistry, and services."""
    
    @pytest.mark.asyncio
    async def test_service_communication_via_messagebus(self):
        """Test services communicating via MessageBus."""
        bus = MessageBus()
        bus._subscribers.clear()
        
        registry = ServiceRegistry()
        registry._services.clear()
        
        class ProducerService(BaseService):
            def __init__(self, name: str, message_bus: MessageBus):
                super().__init__(name)
                self.bus = message_bus
            
            async def start(self):
                self.status = ServiceStatus.RUNNING
            
            async def stop(self):
                self.status = ServiceStatus.STOPPED
            
            async def produce_message(self, data: Dict[str, Any]):
                await self.bus.publish("data.produced", data)
            
            async def health_check(self) -> Dict[str, Any]:
                return {"status": "healthy"}
        
        class ConsumerService(BaseService):
            def __init__(self, name: str, message_bus: MessageBus):
                super().__init__(name)
                self.bus = message_bus
                self.received_messages = []
            
            async def start(self):
                self.status = ServiceStatus.RUNNING
                self.bus.subscribe("data.produced", self._handle_message)
            
            async def stop(self):
                self.status = ServiceStatus.STOPPED
            
            async def _handle_message(self, message: Message):
                self.received_messages.append(message)
            
            async def health_check(self) -> Dict[str, Any]:
                return {"status": "healthy", "messages_received": len(self.received_messages)}
        
        # Create services
        producer = ProducerService("producer", bus)
        consumer = ConsumerService("consumer", bus)
        
        # Register and start services
        registry.register(producer)
        registry.register(consumer)
        await registry.start_all()
        
        # Producer sends message
        await producer.produce_message({"value": 123})
        await asyncio.sleep(0.1)
        
        # Consumer should receive message
        assert len(consumer.received_messages) == 1
        assert consumer.received_messages[0].data == {"value": 123}
        
        # Health check should show message received
        health = await consumer.health_check()
        assert health["messages_received"] == 1
        
        # Cleanup
        await registry.stop_all()


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.modern_spa
@pytest.mark.unit
class TestErrorHandling:
    """Test error handling in microservices."""
    
    @pytest.mark.asyncio
    async def test_service_start_error(self):
        """Test handling service start errors."""
        
        class FailingService(BaseService):
            async def start(self):
                self.status = ServiceStatus.STARTING
                raise RuntimeError("Failed to start")
            
            async def stop(self):
                self.status = ServiceStatus.STOPPED
            
            async def health_check(self) -> Dict[str, Any]:
                return {"status": "unhealthy"}
        
        service = FailingService("failing-service")
        
        with pytest.raises(RuntimeError, match="Failed to start"):
            await service.start()
    
    @pytest.mark.asyncio
    async def test_handler_exception_in_messagebus(self):
        """Test exception in message handler doesn't crash system."""
        bus = MessageBus()
        bus._subscribers.clear()
        
        async def failing_handler(message: Message):
            raise ValueError("Handler error")
        
        async def working_handler(message: Message):
            working_handler.called = True
        
        working_handler.called = False
        
        # Subscribe both handlers
        bus.subscribe("test.event", failing_handler)
        bus.subscribe("test.event", working_handler)
        
        # Publish message - should not crash
        await bus.publish("test.event", {"data": "test"})
        await asyncio.sleep(0.1)
        
        # Working handler should still be called
        assert working_handler.called is True
