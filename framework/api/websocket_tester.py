"""
WebSocket Testing Support - Real-time Communication Testing

Provides WebSocket connection testing, message validation,
and event handling for real-time applications.
"""

import asyncio
import inspect
import json
import threading
import time
from datetime import datetime
from types import TracebackType
from typing import Any, Awaitable, Callable, Dict, List, Optional, TYPE_CHECKING, Type, cast

from utils.logger import get_logger

logger = get_logger(__name__)

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.warning("websockets library not installed. Run: pip install websockets")

if TYPE_CHECKING:
    from websockets.legacy.client import WebSocketClientProtocol  # pragma: no cover
else:
    WebSocketClientProtocol = Any  # type: ignore[misc]

EventHandler = Callable[[Any], Awaitable[Any] | Any]
MessageRecord = Dict[str, Any]
MessageFilter = Callable[[MessageRecord], bool]


class WebSocketTester:
    """WebSocket testing client."""
    
    def __init__(self, url: str, headers: Optional[Dict] = None):
        """Initialize WebSocket tester.

        Args:
            url: WebSocket URL (ws:// or wss://)
            headers: Optional headers
        """
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets library not installed")
        
        self.url = url
        self.headers = headers or {}
        self.connection: Optional[WebSocketClientProtocol] = None
        self.received_messages: List[MessageRecord] = []
        self.event_handlers: Dict[str, List[EventHandler]] = {}
        self.is_connected = False
        self._listener_task: Optional[asyncio.Task[None]] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
    
    async def connect(self) -> None:
        """Establish WebSocket connection."""
        try:
            connection = await websockets.connect(
                self.url,
                extra_headers=self.headers
            )
            self.connection = cast(WebSocketClientProtocol, connection)
            self.is_connected = True
            logger.info(f"WebSocket connected: {self.url}")
            
            # Start listening for messages
            self._listener_task = asyncio.create_task(self._listen())
        
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close WebSocket connection."""
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.is_connected = False
            logger.info("WebSocket disconnected")
    
    async def send_message(self, message: Any) -> None:
        """Send message to WebSocket server.

        Args:
            message: Message to send (dict will be JSON-encoded)
        """
        if not self.is_connected or self.connection is None:
            raise RuntimeError("WebSocket not connected")
        
        # Convert dict to JSON
        if isinstance(message, dict):
            message = json.dumps(message)
        
        await self.connection.send(message)
        logger.debug(f"Sent message: {message}")
    
    async def _listen(self) -> None:
        """Listen for incoming messages."""
        try:
            connection = self.connection
            if connection is None:
                return

            async for message in connection:
                timestamp = datetime.now().isoformat()
                
                # Try to parse as JSON
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    data = message
                
                message_obj = {
                    'timestamp': timestamp,
                    'data': data,
                    'raw': message
                }
                
                self.received_messages.append(message_obj)
                safe_message = (
                    message.decode('utf-8', errors='replace')
                    if isinstance(message, (bytes, bytearray))
                    else str(message)
                )
                logger.debug(f"Received message: {safe_message}")
                
                # Trigger event handlers
                await self._trigger_handlers(data)
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"WebSocket listener error: {e}")
    
    async def _trigger_handlers(self, data: Any) -> None:
        """Trigger registered event handlers."""
        # Check for event type in data
        event_type = None
        if isinstance(data, dict):
            event_type = data.get('type') or data.get('event') or data.get('action')
        
        # Trigger specific handlers
        if event_type and event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                await self._invoke_handler(handler, data)
        
        # Trigger wildcard handlers
        if '*' in self.event_handlers:
            for handler in self.event_handlers['*']:
                await self._invoke_handler(handler, data)

    async def _invoke_handler(self, handler: EventHandler, data: Any) -> None:
        """Call handler and await if necessary."""
        try:
            result = handler(data)
            if inspect.isawaitable(result):
                await result
        except Exception as exc:  # pragma: no cover - handler failures logged
            logger.error(f"Error in event handler: {exc}")
    
    def on(self, event_type: str, handler: EventHandler) -> None:
        """Register event handler.

        Args:
            event_type: Event type to listen for (use '*' for all events)
            handler: Callback function
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.debug(f"Registered handler for event: {event_type}")
    
    def get_messages(self, filter_func: Optional[MessageFilter] = None) -> List[MessageRecord]:
        """Get received messages.

        Args:
            filter_func: Optional filter function

        Returns:
            List of messages
        """
        if filter_func:
            return [m for m in self.received_messages if filter_func(m)]
        return self.received_messages.copy()
    
    def get_messages_by_type(self, event_type: str) -> List[MessageRecord]:
        """Get messages of specific type."""
        return self.get_messages(
            lambda m: isinstance(m['data'], dict) and m['data'].get('type') == event_type
        )
    
    def wait_for_message(
        self,
        timeout: float = 10,
        condition: Optional[MessageFilter] = None
    ) -> Optional[MessageRecord]:
        """Wait for message matching condition.

        Args:
            timeout: Maximum wait time in seconds
            condition: Optional condition function

        Returns:
            Matching message or None if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            messages = self.get_messages(condition) if condition else self.received_messages
            if messages:
                return messages[-1]
            
            time.sleep(0.1)
        
        logger.warning(f"Timeout waiting for message (waited {timeout}s)")
        return None
    
    def assert_message_received(self, condition: MessageFilter, timeout: float = 10) -> None:
        """Assert message matching condition is received.

        Args:
            condition: Condition function
            timeout: Maximum wait time

        Raises:
            AssertionError: If message not received
        """
        message = self.wait_for_message(timeout, condition)
        
        if not message:
            raise AssertionError(f"Expected message not received within {timeout}s")
        
        logger.info("✓ Expected message received")
    
    def assert_message_type_received(self, event_type: str, timeout: float = 10) -> None:
        """Assert message of specific type is received.

        Args:
            event_type: Expected event type
            timeout: Maximum wait time
        """
        def condition(msg: MessageRecord) -> bool:
            return isinstance(msg['data'], dict) and msg['data'].get('type') == event_type
        
        self.assert_message_received(condition, timeout)
    
    def clear_messages(self) -> None:
        """Clear received messages."""
        self.received_messages.clear()
        logger.debug("Cleared received messages")
    
    def get_connection_state(self) -> Dict[str, Any]:
        """Get connection state information."""
        return {
            'connected': self.is_connected,
            'url': self.url,
            'messages_received': len(self.received_messages),
            'event_handlers': {k: len(v) for k, v in self.event_handlers.items()}
        }


class SyncWebSocketTester:
    """Synchronous wrapper for WebSocketTester."""
    
    def __init__(self, url: str, headers: Optional[Dict[str, Any]] = None):
        """Initialize synchronous WebSocket tester.

        Args:
            url: WebSocket URL
            headers: Optional headers
        """
        self.tester = WebSocketTester(url, headers)
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[threading.Thread] = None
    
    def connect(self) -> None:
        """Connect (synchronous)"""
        def run_loop():
            loop = asyncio.new_event_loop()
            self.loop = loop
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.tester.connect())
            loop.run_forever()
        
        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()
        
        # Wait for connection
        timeout = 10
        start = time.time()
        while not self.tester.is_connected and time.time() - start < timeout:
            time.sleep(0.1)
        
        if not self.tester.is_connected:
            raise TimeoutError("WebSocket connection timeout")
    
    def disconnect(self) -> None:
        """Disconnect (synchronous)"""
        loop = self.loop
        if loop:
            asyncio.run_coroutine_threadsafe(self.tester.disconnect(), loop)
            loop.call_soon_threadsafe(loop.stop)
    
    def send_message(self, message: Any) -> None:
        """Send message (synchronous)"""
        if not self.loop:
            raise RuntimeError("Not connected")
        
        future = asyncio.run_coroutine_threadsafe(
            self.tester.send_message(message),
            self.loop
        )
        future.result(timeout=5)
    
    def on(self, event_type: str, handler: EventHandler) -> None:
        """Register event handler."""
        self.tester.on(event_type, handler)
    
    def get_messages(self, filter_func: Optional[MessageFilter] = None) -> List[MessageRecord]:
        """Get received messages."""
        return self.tester.get_messages(filter_func)
    
    def wait_for_message(
        self,
        timeout: float = 10,
        condition: Optional[MessageFilter] = None
    ) -> Optional[MessageRecord]:
        """Wait for message."""
        return self.tester.wait_for_message(timeout, condition)
    
    def assert_message_received(self, condition: MessageFilter, timeout: float = 10) -> None:
        """Assert message received."""
        self.tester.assert_message_received(condition, timeout)
    
    def assert_message_type_received(self, event_type: str, timeout: float = 10) -> None:
        """Assert message type received."""
        self.tester.assert_message_type_received(event_type, timeout)
    
    def clear_messages(self) -> None:
        """Clear messages."""
        self.tester.clear_messages()
    
    def __enter__(self) -> "SyncWebSocketTester":
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        """Context manager exit."""
        self.disconnect()


__all__ = ['WebSocketTester', 'SyncWebSocketTester']
