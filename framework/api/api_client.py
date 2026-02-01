"""
API Client - HTTP Request Wrapper

Provides a unified interface for making API requests with logging and validation.
"""

import requests
import time
from typing import Dict, Any, Optional
from utils.logger import get_logger, get_audit_logger

logger = get_logger(__name__)
audit_logger = get_audit_logger()


class APIClient:
    """HTTP API client with logging, audit trail and validation"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.last_response: Optional[requests.Response] = None
    
    def request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        data: Optional[Any] = None,
        timeout: int = 30
    ) -> requests.Response:
        """Make HTTP request with comprehensive logging"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        logger.info(f"API Request: {method} {url}")
        if json_data:
            logger.debug(f"Request Body: {json_data}")
        
        # Track timing for audit
        start_time = time.time()
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                data=data,
                timeout=timeout
            )
            
            duration_ms = (time.time() - start_time) * 1000
            self.last_response = response
            
            logger.info(f"API Response: {response.status_code} ({duration_ms:.2f}ms)")
            
            # Audit log with full details
            response_body = None
            try:
                response_body = response.json() if response.content else None
            except:
                response_body = response.text[:500]  # First 500 chars if not JSON
            
            audit_logger.log_api_call(
                method=method,
                url=url,
                status_code=response.status_code,
                duration_ms=duration_ms,
                request_body=json_data,
                response_body=response_body
            )
            
            return response
            
        except requests.exceptions.RequestException as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"API Request Failed: {method} {url} - {str(e)}")
            
            # Log failure to audit trail
            audit_logger.log_error(
                error_type="api_request_failed",
                error_message=f"{method} {url}: {str(e)}",
                stack_trace=str(e)
            )
            raise
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """GET request"""
        return self.request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """POST request"""
        return self.request("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """PUT request"""
        return self.request("PUT", endpoint, **kwargs)
    
    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        """PATCH request"""
        return self.request("PATCH", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """DELETE request"""
        return self.request("DELETE", endpoint, **kwargs)
    
    def assert_status_code(self, expected: int):
        """Assert last response status code"""
        actual = self.last_response.status_code
        logger.info(f"Asserting status code: expected={expected}, actual={actual}")
        assert actual == expected, \
            f"Expected {expected}, got {actual}"
    
    def get_json(self) -> Dict:
        """Get JSON from last response"""
        return self.last_response.json()


__all__ = ['APIClient']
