"""
WebSocket Testing Support - Real-time Communication Testing

Provides WebSocket connection testing, message validation,
and event handling for real-time applications.
"""

from typing import Dict, List, Optional, Callable, Any
import asyncio
import json
from datetime import datetime
import threading
import time
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    import websockets
    from websockets.client import WebSocketClientProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.warning("websockets library not installed. Run: pip install websockets")


class WebSocketTester:
    """WebSocket testing client"""
    
    def __init__(self, url: str, headers: Optional[Dict] = None):
        """
        Initialize WebSocket tester
        
        Args:
            url: WebSocket URL (ws:// or wss://)
            headers: Optional headers
        """
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets library not installed")
        
        self.url = url
        self.headers = headers or {}
        self.connection: Optional[WebSocketClientProtocol] = None
        self.received_messages: List[Dict] = []
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.is_connected = False
        self._listener_task = None
        self._loop = None
        self._thread = None
    
    async def connect(self):
        """Establish WebSocket connection"""
        try:
            self.connection = await websockets.connect(
                self.url,
                extra_headers=self.headers
            )
            self.is_connected = True
            logger.info(f"WebSocket connected: {self.url}")
            
            # Start listening for messages
            self._listener_task = asyncio.create_task(self._listen())
        
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Close WebSocket connection"""
        if self.connection:
            await self.connection.close()
            self.is_connected = False
            logger.info("WebSocket disconnected")
    
    async def send_message(self, message: Any):
        """
        Send message to WebSocket server
        
        Args:
            message: Message to send (dict will be JSON-encoded)
        """
        if not self.is_connected:
            raise RuntimeError("WebSocket not connected")
        
        # Convert dict to JSON
        if isinstance(message, dict):
            message = json.dumps(message)
        
        await self.connection.send(message)
        logger.debug(f"Sent message: {message}")
    
    async def _listen(self):
        """Listen for incoming messages"""
        try:
            async for message in self.connection:
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
                logger.debug(f"Received message: {message}")
                
                # Trigger event handlers
                await self._trigger_handlers(data)
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"WebSocket listener error: {e}")
    
    async def _trigger_handlers(self, data: Any):
        """Trigger registered event handlers"""
        # Check for event type in data
        event_type = None
        if isinstance(data, dict):
            event_type = data.get('type') or data.get('event') or data.get('action')
        
        # Trigger specific handlers
        if event_type and event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")
        
        # Trigger wildcard handlers
        if '*' in self.event_handlers:
            for handler in self.event_handlers['*']:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(f"Error in wildcard handler: {e}")
    
    def on(self, event_type: str, handler: Callable):
        """
        Register event handler
        
        Args:
            event_type: Event type to listen for (use '*' for all events)
            handler: Callback function
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.debug(f"Registered handler for event: {event_type}")
    
    def get_messages(self, filter_func: Optional[Callable] = None) -> List[Dict]:
        """
        Get received messages
        
        Args:
            filter_func: Optional filter function
        
        Returns:
            List of messages
        """
        if filter_func:
            return [m for m in self.received_messages if filter_func(m)]
        return self.received_messages.copy()
    
    def get_messages_by_type(self, event_type: str) -> List[Dict]:
        """Get messages of specific type"""
        return self.get_messages(
            lambda m: isinstance(m['data'], dict) and m['data'].get('type') == event_type
        )
    
    def wait_for_message(self, timeout: float = 10, 
                         condition: Optional[Callable] = None) -> Optional[Dict]:
        """
        Wait for message matching condition
        
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
    
    def assert_message_received(self, condition: Callable, timeout: float = 10):
        """
        Assert message matching condition is received
        
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
    
    def assert_message_type_received(self, event_type: str, timeout: float = 10):
        """
        Assert message of specific type is received
        
        Args:
            event_type: Expected event type
            timeout: Maximum wait time
        """
        def condition(msg):
            return isinstance(msg['data'], dict) and msg['data'].get('type') == event_type
        
        self.assert_message_received(condition, timeout)
    
    def clear_messages(self):
        """Clear received messages"""
        self.received_messages.clear()
        logger.debug("Cleared received messages")
    
    def get_connection_state(self) -> Dict[str, Any]:
        """Get connection state information"""
        return {
            'connected': self.is_connected,
            'url': self.url,
            'messages_received': len(self.received_messages),
            'event_handlers': {k: len(v) for k, v in self.event_handlers.items()}
        }


class SyncWebSocketTester:
    """Synchronous wrapper for WebSocketTester"""
    
    def __init__(self, url: str, headers: Optional[Dict] = None):
        """
        Initialize synchronous WebSocket tester
        
        Args:
            url: WebSocket URL
            headers: Optional headers
        """
        self.tester = WebSocketTester(url, headers)
        self.loop = None
        self.thread = None
    
    def connect(self):
        """Connect (synchronous)"""
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.tester.connect())
            self.loop.run_forever()
        
        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()
        
        # Wait for connection
        timeout = 10
        start = time.time()
        while not self.tester.is_connected and time.time() - start < timeout:
            time.sleep(0.1)
        
        if not self.tester.is_connected:
            raise TimeoutError("WebSocket connection timeout")
    
    def disconnect(self):
        """Disconnect (synchronous)"""
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.tester.disconnect(), self.loop)
            self.loop.call_soon_threadsafe(self.loop.stop)
    
    def send_message(self, message: Any):
        """Send message (synchronous)"""
        if not self.loop:
            raise RuntimeError("Not connected")
        
        future = asyncio.run_coroutine_threadsafe(
            self.tester.send_message(message),
            self.loop
        )
        future.result(timeout=5)
    
    def on(self, event_type: str, handler: Callable):
        """Register event handler"""
        self.tester.on(event_type, handler)
    
    def get_messages(self, filter_func: Optional[Callable] = None) -> List[Dict]:
        """Get received messages"""
        return self.tester.get_messages(filter_func)
    
    def wait_for_message(self, timeout: float = 10, 
                         condition: Optional[Callable] = None) -> Optional[Dict]:
        """Wait for message"""
        return self.tester.wait_for_message(timeout, condition)
    
    def assert_message_received(self, condition: Callable, timeout: float = 10):
        """Assert message received"""
        self.tester.assert_message_received(condition, timeout)
    
    def assert_message_type_received(self, event_type: str, timeout: float = 10):
        """Assert message type received"""
        self.tester.assert_message_type_received(event_type, timeout)
    
    def clear_messages(self):
        """Clear messages"""
        self.tester.clear_messages()
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


__all__ = ['WebSocketTester', 'SyncWebSocketTester']
