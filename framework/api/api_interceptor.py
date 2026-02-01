"""
API Interceptor - Automatic API Call Capture

Captures API calls made during UI automation for correlation and validation.
Supports both Playwright and Selenium engines.

Enhanced Features:
- WebSocket interception and message capture
- Request/response modification
- Pattern-based request/response mocking
- Real-time message monitoring
"""

import json
import re
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

from utils.logger import get_logger

logger = get_logger(__name__)


class WebSocketMessage:
    """Represents a captured WebSocket message"""
    
    def __init__(self, direction: str, data: Any, timestamp: datetime = None):
        self.direction = direction  # 'sent' or 'received'
        self.data = data
        self.timestamp = timestamp or datetime.now()
        self.parsed_data = self._parse_data(data)
    
    def _parse_data(self, data: Any) -> Any:
        """Try to parse message data as JSON"""
        if isinstance(data, str):
            try:
                return json.loads(data)
            except (json.JSONDecodeError, ValueError):
                return data
        return data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'direction': self.direction,
            'data': self.data,
            'parsed_data': self.parsed_data,
            'timestamp': self.timestamp.isoformat(),
            'size': len(str(self.data))
        }


class RequestModifier:
    """Handles request modification based on patterns"""
    
    def __init__(self):
        self.modifications: List[Dict[str, Any]] = []
    
    def add_header_modification(self, pattern: str, headers: Dict[str, str]):
        """Add header modification rule"""
        self.modifications.append({
            'type': 'headers',
            'pattern': pattern,
            'headers': headers
        })
    
    def add_body_modification(self, pattern: str, body_modifier: Callable):
        """Add body modification rule"""
        self.modifications.append({
            'type': 'body',
            'pattern': pattern,
            'modifier': body_modifier
        })
    
    def add_url_modification(self, pattern: str, url_modifier: Callable):
        """Add URL modification rule"""
        self.modifications.append({
            'type': 'url',
            'pattern': pattern,
            'modifier': url_modifier
        })
    
    def apply_modifications(self, url: str, headers: Dict, post_data: Optional[str]) -> tuple:
        """Apply all matching modifications"""
        modified_headers = headers.copy() if headers else {}
        modified_url = url
        modified_body = post_data
        
        for mod in self.modifications:
            if not re.search(mod['pattern'], url):
                continue
            
            if mod['type'] == 'headers':
                modified_headers.update(mod['headers'])
            elif mod['type'] == 'url' and 'modifier' in mod:
                modified_url = mod['modifier'](modified_url)
            elif mod['type'] == 'body' and 'modifier' in mod and post_data:
                modified_body = mod['modifier'](post_data)
        
        return modified_url, modified_headers, modified_body


class ResponseModifier:
    """Handles response modification and mocking"""
    
    def __init__(self):
        self.mocks: List[Dict[str, Any]] = []
        self.modifications: List[Dict[str, Any]] = []
    
    def add_mock_response(self, pattern: str, status: int, body: Any, headers: Optional[Dict] = None):
        """Add mock response for matching URLs"""
        self.mocks.append({
            'pattern': pattern,
            'status': status,
            'body': body,
            'headers': headers or {'Content-Type': 'application/json'}
        })
    
    def add_response_modification(self, pattern: str, body_modifier: Callable):
        """Add response body modification rule"""
        self.modifications.append({
            'pattern': pattern,
            'modifier': body_modifier
        })
    
    def get_mock_response(self, url: str) -> Optional[Dict[str, Any]]:
        """Get mock response if pattern matches"""
        for mock in self.mocks:
            if re.search(mock['pattern'], url):
                return mock
        return None
    
    def apply_modifications(self, url: str, response_body: Any) -> Any:
        """Apply response modifications"""
        modified_body = response_body
        
        for mod in self.modifications:
            if re.search(mod['pattern'], url):
                modified_body = mod['modifier'](modified_body)
        
        return modified_body


class APIInterceptor:
    """
    Enhanced API Interceptor with WebSocket support and request/response modification
    
    Features:
    - HTTP request/response interception
    - WebSocket message capture
    - Request modification (headers, body, URL)
    - Response mocking and modification
    - Pattern-based filtering
    """
    
    def __init__(self, ui_engine):
        """
        Initialize API interceptor
        
        Args:
            ui_engine: PlaywrightEngine or SeleniumEngine instance
        """
        self.ui_engine = ui_engine
        self.captured_requests: List[Dict[str, Any]] = []
        self.captured_responses: List[Dict[str, Any]] = []
        self.captured_websockets: List[Dict[str, Any]] = []
        self.websocket_messages: List[WebSocketMessage] = []
        self.filters: List[Callable] = []
        self.enabled = True
        
        # Modification handlers
        self.request_modifier = RequestModifier()
        self.response_modifier = ResponseModifier()
        
        # WebSocket tracking
        self.active_websockets: List[Any] = []
        
        self._setup_interception()
    
    def _setup_interception(self):
        """Setup interception based on engine type"""
        engine_type = type(self.ui_engine).__name__
        
        if engine_type == 'PlaywrightEngine':
            self._setup_playwright_interception()
        elif engine_type == 'SeleniumEngine':
            self._setup_selenium_interception()
        else:
            logger.warning(f"Unknown engine type: {engine_type}. Interception not configured.")
    
    def _setup_playwright_interception(self):
        """Setup Playwright network interception with WebSocket support"""
        try:
            page = self.ui_engine.get_page()
            
            def handle_request(route, request):
                """Handle outgoing request with modification support"""
                if not self.enabled:
                    route.continue_()
                    return
                
                # Check filters
                if not self._should_capture(request.url):
                    route.continue_()
                    return
                
                # Capture request data
                request_data = {
                    'timestamp': datetime.now().isoformat(),
                    'method': request.method,
                    'url': request.url,
                    'headers': dict(request.headers),
                    'post_data': request.post_data if request.method in ['POST', 'PUT', 'PATCH'] else None,
                    'resource_type': request.resource_type
                }
                
                self.captured_requests.append(request_data)
                logger.debug(f"Captured request: {request.method} {request.url}")
                
                # Check for mock response
                mock_response = self.response_modifier.get_mock_response(request.url)
                if mock_response:
                    logger.info(f"Using mock response for: {request.url}")
                    route.fulfill(
                        status=mock_response['status'],
                        body=json.dumps(mock_response['body']) if isinstance(mock_response['body'], dict) else str(mock_response['body']),
                        headers=mock_response['headers']
                    )
                    return
                
                # Apply request modifications
                modified_url, modified_headers, modified_body = self.request_modifier.apply_modifications(
                    request.url,
                    dict(request.headers),
                    request.post_data
                )
                
                # Continue with modifications if any
                if modified_url != request.url or modified_headers != dict(request.headers) or modified_body != request.post_data:
                    logger.debug(f"Modifying request: {request.url}")
                    route.continue_(
                        url=modified_url if modified_url != request.url else None,
                        headers=modified_headers if modified_headers != dict(request.headers) else None,
                        post_data=modified_body if modified_body != request.post_data else None
                    )
                else:
                    route.continue_()
            
            def handle_response(response):
                """Handle incoming response with modification support"""
                if not self.enabled:
                    return
                
                if not self._should_capture(response.url):
                    return
                
                try:
                    body = None
                    if response.status != 204:  # No content
                        try:
                            body = response.json()
                        except Exception:
                            try:
                                body = response.text()
                            except Exception:
                                body = None
                    
                    # Apply response modifications
                    modified_body = self.response_modifier.apply_modifications(response.url, body)
                    
                    response_data = {
                        'timestamp': datetime.now().isoformat(),
                        'method': response.request.method,
                        'url': response.url,
                        'status': response.status,
                        'status_text': response.status_text,
                        'headers': dict(response.headers),
                        'body': modified_body,
                        'original_body': body if modified_body != body else None
                    }
                    
                    self.captured_responses.append(response_data)
                    logger.debug(f"Captured response: {response.status} {response.url}")
                
                except Exception as e:
                    logger.error(f"Error capturing response: {e}")
            
            def handle_websocket(ws):
                """Handle WebSocket connection"""
                try:
                    ws_data = {
                        'url': ws.url,
                        'timestamp': datetime.now().isoformat(),
                        'messages': []
                    }
                    
                    self.captured_websockets.append(ws_data)
                    self.active_websockets.append(ws)
                    logger.info(f"WebSocket connected: {ws.url}")
                    
                    # Listen for sent messages (framesent)
                    def on_frame_sent(payload):
                        try:
                            message = WebSocketMessage('sent', payload)
                            self.websocket_messages.append(message)
                            ws_data['messages'].append(message.to_dict())
                            logger.debug(f"WebSocket sent: {payload[:100] if isinstance(payload, str) else 'binary'}")
                        except Exception as e:
                            logger.error(f"Error capturing WebSocket sent message: {e}")
                    
                    # Listen for received messages (framereceived)
                    def on_frame_received(payload):
                        try:
                            message = WebSocketMessage('received', payload)
                            self.websocket_messages.append(message)
                            ws_data['messages'].append(message.to_dict())
                            logger.debug(f"WebSocket received: {payload[:100] if isinstance(payload, str) else 'binary'}")
                        except Exception as e:
                            logger.error(f"Error capturing WebSocket received message: {e}")
                    
                    # Listen for close
                    def on_close():
                        logger.info(f"WebSocket closed: {ws.url}")
                        if ws in self.active_websockets:
                            self.active_websockets.remove(ws)
                    
                    # Listen for errors
                    def on_socket_error(error):
                        logger.error(f"WebSocket error: {error}")
                    
                    # Register event handlers
                    ws.on("framesent", on_frame_sent)
                    ws.on("framereceived", on_frame_received)
                    ws.on("close", on_close)
                    ws.on("socketerror", on_socket_error)
                    
                except Exception as e:
                    logger.error(f"Error setting up WebSocket handlers: {e}")
            
            # Enable route interception
            page.route("**/*", handle_request)
            page.on("response", handle_response)
            page.on("websocket", handle_websocket)
            
            logger.info("Playwright API interception enabled (HTTP + WebSocket)")
        
        except Exception as e:
            logger.error(f"Failed to setup Playwright interception: {e}")
    
    def _setup_selenium_interception(self):
        """Setup Selenium network interception (using BrowserMob Proxy or Chrome DevTools)"""
        # Note: Selenium doesn't have native network interception like Playwright
        # Options: 1) BrowserMob Proxy, 2) Chrome DevTools Protocol, 3) Browser extensions
        # For now, we'll log a message and provide ChromeDevTools implementation
        
        try:
            driver = self.ui_engine.get_driver()
            
            # Check if Chrome/Edge (supports DevTools)
            if 'chrome' in driver.capabilities.get('browserName', '').lower():
                self._setup_chrome_devtools()
            else:
                logger.warning(
                    "Selenium API interception requires Chrome/Edge with DevTools. "
                    "For other browsers, consider using BrowserMob Proxy."
                )
        
        except Exception as e:
            logger.error(f"Failed to setup Selenium interception: {e}")
    
    def _setup_chrome_devtools(self):
        """Setup Chrome DevTools Protocol for network interception"""
        try:
            driver = self.ui_engine.get_driver()
            
            # Enable Network domain
            driver.execute_cdp_cmd('Network.enable', {})
            
            # Note: Full implementation would require selenium-wire or custom CDP listener
            logger.info("Chrome DevTools network monitoring enabled (basic)")
            logger.warning("For full Selenium interception, install: pip install selenium-wire")
        
        except Exception as e:
            logger.error(f"Chrome DevTools setup failed: {e}")
    
    def add_filter(self, filter_func: Callable[[str], bool]):
        """
        Add URL filter for selective capture
        
        Args:
            filter_func: Function that takes URL string and returns True to capture
        
        Example:
            interceptor.add_filter(lambda url: '/api/' in url)
        """
        self.filters.append(filter_func)
    
    def filter_by_pattern(self, pattern: str):
        """
        Add simple pattern filter
        
        Args:
            pattern: String pattern to match in URL
        """
        self.add_filter(lambda url: pattern in url)
    
    def filter_api_only(self):
        """Capture only API calls (URLs containing /api/)"""
        self.filter_by_pattern('/api/')
    
    # ========================================================================
    # REQUEST/RESPONSE MODIFICATION METHODS
    # ========================================================================
    
    def modify_request_headers(self, url_pattern: str, headers: Dict[str, str]):
        """
        Modify request headers for matching URLs
        
        Args:
            url_pattern: Regex pattern to match URLs
            headers: Dictionary of headers to add/modify
        
        Example:
            interceptor.modify_request_headers(
                r'/api/.*',
                {'Authorization': 'Bearer token', 'X-Custom': 'value'}
            )
        """
        self.request_modifier.add_header_modification(url_pattern, headers)
        logger.info(f"Added request header modification for pattern: {url_pattern}")
    
    def modify_request_url(self, url_pattern: str, url_modifier: Callable[[str], str]):
        """
        Modify request URL for matching patterns
        
        Args:
            url_pattern: Regex pattern to match URLs
            url_modifier: Function that takes URL and returns modified URL
        
        Example:
            interceptor.modify_request_url(r'/api/v1/', lambda url: url.replace('/v1/', '/v2/'))
        """
        self.request_modifier.add_url_modification(url_pattern, url_modifier)
        logger.info(f"Added request URL modification for pattern: {url_pattern}")
    
    def modify_request_body(self, url_pattern: str, body_modifier: Callable[[Any], Any]):
        """
        Modify request body for matching URLs
        
        Args:
            url_pattern: Regex pattern to match URLs
            body_modifier: Function that takes body (dict/str) and returns modified body
        
        Example:
            def add_field(body):
                if isinstance(body, dict):
                    return {**body, 'extra': 'value'}
                return body
            interceptor.modify_request_body(r'/api/orders', add_field)
        """
        self.request_modifier.add_body_modification(url_pattern, body_modifier)
        logger.info(f"Added request body modification for pattern: {url_pattern}")
    
    def mock_response(self, url_pattern: str, status: int = 200, body: Any = None, headers: Optional[Dict] = None):
        """
        Mock response for matching URLs
        
        Args:
            url_pattern: Regex pattern to match URLs
            status: HTTP status code
            body: Response body (dict will be JSON-encoded)
            headers: Response headers
        
        Example:
            interceptor.mock_response(
                r'/api/users/\d+',
                status=200,
                body={'id': 123, 'name': 'Test User'},
                headers={'Content-Type': 'application/json'}
            )
        """
        self.response_modifier.add_mock_response(url_pattern, status, body or {}, headers)
        logger.info(f"Added mock response for pattern: {url_pattern}")
    
    def modify_response_body(self, url_pattern: str, body_modifier: Callable[[Any], Any]):
        """
        Modify response body for matching URLs
        
        Args:
            url_pattern: Regex pattern to match URLs
            body_modifier: Function that takes body and returns modified body
        
        Example:
            def mask_email(body):
                if isinstance(body, dict) and 'email' in body:
                    body['email'] = 'masked@example.com'
                return body
            interceptor.modify_response_body(r'/api/users', mask_email)
        """
        self.response_modifier.add_response_modification(url_pattern, body_modifier)
        logger.info(f"Added response body modification for pattern: {url_pattern}")
    
    # ========================================================================
    # WEBSOCKET METHODS
    # ========================================================================
    
    def get_websocket_connections(self) -> List[Dict[str, Any]]:
        """Get all captured WebSocket connections"""
        return self.captured_websockets.copy()
    
    def get_websocket_messages(
        self,
        direction: Optional[str] = None,
        url_pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get WebSocket messages with optional filtering
        
        Args:
            direction: Filter by 'sent' or 'received'
            url_pattern: Filter by WebSocket URL pattern
        
        Returns:
            List of WebSocket message dictionaries
        """
        messages = [msg.to_dict() for msg in self.websocket_messages]
        
        if direction:
            messages = [m for m in messages if m['direction'] == direction]
        
        if url_pattern:
            # Match against WebSocket URLs
            filtered = []
            for ws in self.captured_websockets:
                if re.search(url_pattern, ws['url']):
                    ws_messages = ws.get('messages', [])
                    filtered.extend([m for m in messages if m in ws_messages])
            return filtered
        
        return messages
    
    def get_websocket_sent_messages(self) -> List[Dict[str, Any]]:
        """Get all sent WebSocket messages"""
        return self.get_websocket_messages(direction='sent')
    
    def get_websocket_received_messages(self) -> List[Dict[str, Any]]:
        """Get all received WebSocket messages"""
        return self.get_websocket_messages(direction='received')
    
    def get_websocket_message_count(self) -> Dict[str, int]:
        """Get count of WebSocket messages by direction"""
        return {
            'total': len(self.websocket_messages),
            'sent': len(self.get_websocket_sent_messages()),
            'received': len(self.get_websocket_received_messages()),
            'connections': len(self.captured_websockets)
        }
    
    def wait_for_websocket_message(
        self,
        predicate: Callable[[Dict], bool],
        timeout: float = 10.0
    ) -> Optional[Dict[str, Any]]:
        """
        Wait for WebSocket message matching predicate
        
        Args:
            predicate: Function that returns True for matching message
            timeout: Timeout in seconds
        
        Returns:
            Matching message dict or None if timeout
        
        Example:
            msg = interceptor.wait_for_websocket_message(
                lambda m: m['direction'] == 'received' and 'order_id' in str(m['data']),
                timeout=5.0
            )
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            for msg in self.websocket_messages:
                if predicate(msg.to_dict()):
                    return msg.to_dict()
            time.sleep(0.1)
        
        logger.warning(f"WebSocket message wait timed out after {timeout}s")
        return None
    
    # ========================================================================
    # EXISTING METHODS (ENHANCED)
    # ========================================================================
    
    def _should_capture(self, url: str) -> bool:
        """Check if URL should be captured based on filters"""
        # If no filters, capture all
        if not self.filters:
            return True
        
        # Check all filters
        return any(filter_func(url) for filter_func in self.filters)
    
    def add_filter(self, filter_func: Callable[[str], bool]):
        """
        Add URL filter for selective capture
        
        Args:
            filter_func: Function that takes URL string and returns True to capture
        
        Example:
            interceptor.add_filter(lambda url: '/api/' in url)
        """
        self.filters.append(filter_func)
    
    def filter_by_pattern(self, pattern: str):
        """
        Add simple pattern filter
        
        Args:
            pattern: String pattern to match in URL
        """
        self.add_filter(lambda url: pattern in url)
    
    def filter_api_only(self):
        """Capture only API calls (URLs containing /api/)"""
        self.filter_by_pattern('/api/')
    
    def get_captured_requests(self, filter_func: Optional[Callable] = None) -> List[Dict]:
        """
        Get captured requests
        
        Args:
            filter_func: Optional filter function
        
        Returns:
            List of captured request dictionaries
        """
        if filter_func:
            return [r for r in self.captured_requests if filter_func(r)]
        return self.captured_requests.copy()
    
    def get_captured_responses(self, filter_func: Optional[Callable] = None) -> List[Dict]:
        """
        Get captured responses
        
        Args:
            filter_func: Optional filter function
        
        Returns:
            List of captured response dictionaries
        """
        if filter_func:
            return [r for r in self.captured_responses if filter_func(r)]
        return self.captured_responses.copy()
    
    def get_requests_by_method(self, method: str) -> List[Dict]:
        """Get requests by HTTP method"""
        return self.get_captured_requests(lambda r: r['method'].upper() == method.upper())
    
    def get_requests_by_url_pattern(self, pattern: str) -> List[Dict]:
        """Get requests matching URL pattern"""
        return self.get_captured_requests(lambda r: pattern in r['url'])
    
    def get_response_by_url(self, url: str) -> Optional[Dict]:
        """Get first response matching exact URL"""
        responses = self.get_captured_responses(lambda r: r['url'] == url)
        return responses[0] if responses else None
    
    def find_api_calls(self) -> List[Dict]:
        """Find all API calls (URLs containing /api/)"""
        return self.get_captured_requests(lambda r: '/api/' in r['url'])
    
    def get_correlation_data(self) -> Dict[str, Any]:
        """
        Extract correlation data from captured API calls
        
        Returns:
            Dictionary with correlation keys (order_id, transaction_id, etc.)
        """
        correlation_data = {}
        
        # Common correlation key patterns
        key_patterns = [
            'order_id', 'orderId', 'transaction_id', 'transactionId',
            'request_id', 'requestId', 'session_id', 'sessionId',
            'user_id', 'userId', 'customer_id', 'customerId',
            'payment_id', 'paymentId', 'invoice_id', 'invoiceId'
        ]
        
        # Search in response bodies
        for response in self.captured_responses:
            body = response.get('body')
            if isinstance(body, dict):
                for key in key_patterns:
                    if key in body:
                        correlation_data[key] = body[key]
        
        return correlation_data
    
    def clear(self):
        """Clear all captured data"""
        self.captured_requests.clear()
        self.captured_responses.clear()
        logger.info("Cleared all captured API data")
    
    def enable(self):
        """Enable interception"""
        self.enabled = True
        logger.info("API interception enabled")
    
    def disable(self):
        """Disable interception"""
        self.enabled = False
        logger.info("API interception disabled")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of captured data"""
        return {
            'total_requests': len(self.captured_requests),
            'total_responses': len(self.captured_responses),
            'methods': self._get_method_summary(),
            'status_codes': self._get_status_summary(),
            'websockets': {
                'connections': len(self.captured_websockets),
                'total_messages': len(self.websocket_messages),
                'sent_messages': len(self.get_websocket_sent_messages()),
                'received_messages': len(self.get_websocket_received_messages())
            },
            'modifications': {
                'request_modifications': len(self.request_modifier.modifications),
                'response_mocks': len(self.response_modifier.mocks),
                'response_modifications': len(self.response_modifier.modifications)
            },
            'api_calls': len(self.find_api_calls()),
            'correlation_keys': list(self.get_correlation_data().keys())
        }
    
    def _get_method_summary(self) -> Dict[str, int]:
        """Get count by HTTP method"""
        methods = {}
        for request in self.captured_requests:
            method = request['method']
            methods[method] = methods.get(method, 0) + 1
        return methods
    
    def _get_status_summary(self) -> Dict[int, int]:
        """Get count by status code"""
        statuses = {}
        for response in self.captured_responses:
            status = response['status']
            statuses[status] = statuses.get(status, 0) + 1
        return statuses
    
    def export_to_har(self, filename: str):
        """
        Export captured data to HAR (HTTP Archive) format
        
        Args:
            filename: Output filename
        """
        import json
        
        har_data = {
            'log': {
                'version': '1.2',
                'creator': {
                    'name': 'Automation Framework API Interceptor',
                    'version': '1.0'
                },
                'entries': []
            }
        }
        
        # Combine requests and responses
        for i, request in enumerate(self.captured_requests):
            entry = {
                'startedDateTime': request['timestamp'],
                'request': {
                    'method': request['method'],
                    'url': request['url'],
                    'headers': [{'name': k, 'value': v} for k, v in request['headers'].items()],
                    'postData': {'text': request.get('post_data', '')} if request.get('post_data') else {}
                },
                'response': {},
                'cache': {},
                'timings': {}
            }
            
            # Find matching response
            matching_responses = [r for r in self.captured_responses if r['url'] == request['url']]
            if matching_responses:
                response = matching_responses[0]
                entry['response'] = {
                    'status': response['status'],
                    'statusText': response['status_text'],
                    'headers': [{'name': k, 'value': v} for k, v in response['headers'].items()],
                    'content': {'text': str(response.get('body', ''))}
                }
            
            har_data['log']['entries'].append(entry)
        
        with open(filename, 'w') as f:
            json.dump(har_data, f, indent=2)
        
        logger.info(f"Exported HAR data to {filename}")


__all__ = [
    'APIInterceptor',
    'WebSocketMessage',
    'RequestModifier',
    'ResponseModifier'
]
