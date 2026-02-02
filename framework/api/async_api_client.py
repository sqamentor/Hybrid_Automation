"""
Async HTTP API Client using httpx

High-performance async API client for 5-10x faster API testing.

Features:
- Full async/await support with httpx
- Request/response interceptors
- Retry logic with exponential backoff
- Request/response logging
- Session management
- OAuth/JWT authentication support

Author: Lokendra Singh
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

try:
    import httpx
except ImportError:
    raise ImportError("httpx is required for AsyncAPIClient. Install with: pip install httpx")


class HTTPMethod(str, Enum):
    """HTTP methods"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class APIResponse:
    """API response wrapper"""

    status_code: int
    headers: Dict[str, str]
    body: Any
    duration: float
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_success(self) -> bool:
        """Check if response is successful (2xx)"""
        return 200 <= self.status_code < 300

    @property
    def is_client_error(self) -> bool:
        """Check if response is client error (4xx)"""
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        """Check if response is server error (5xx)"""
        return 500 <= self.status_code < 600


class AsyncAPIClient:
    """
    High-performance async HTTP API client.

    Example:
        >>> async with AsyncAPIClient("https://api.example.com") as client:
        ...     response = await client.get("/users")
        ...     print(response.status_code)
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        headers: Optional[Dict[str, str]] = None,
        retry_count: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize async API client.

        Args:
            base_url: Base URL for all requests
            timeout: Request timeout in seconds
            verify_ssl: Verify SSL certificates
            headers: Default headers for all requests
            retry_count: Number of retries on failure
            retry_delay: Initial delay between retries
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.default_headers = headers or {}
        self.retry_count = retry_count
        self.retry_delay = retry_delay

        self.client: Optional[httpx.AsyncClient] = None
        self.logger = logging.getLogger(__name__)

        # Interceptors
        self._request_interceptors: List[Callable] = []
        self._response_interceptors: List[Callable] = []

        # Metrics
        self.request_count = 0
        self.total_duration = 0.0

    async def __aenter__(self) -> AsyncAPIClient:
        """Enter async context manager"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager"""
        await self.close()

    async def start(self) -> None:
        """Start the HTTP client"""
        if self.client is None:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                verify=self.verify_ssl,
                headers=self.default_headers,
                follow_redirects=True,
            )
            self.logger.info(f"AsyncAPIClient started for {self.base_url}")

    async def close(self) -> None:
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()
            self.client = None
            self.logger.info("AsyncAPIClient closed")

    def add_request_interceptor(self, interceptor: Callable) -> None:
        """Add request interceptor (called before request)"""
        self._request_interceptors.append(interceptor)

    def add_response_interceptor(self, interceptor: Callable) -> None:
        """Add response interceptor (called after response)"""
        self._response_interceptors.append(interceptor)

    async def _execute_request_interceptors(
        self, method: str, url: str, **kwargs
    ) -> Dict[str, Any]:
        """Execute all request interceptors"""
        request_data = {"method": method, "url": url, **kwargs}

        for interceptor in self._request_interceptors:
            if asyncio.iscoroutinefunction(interceptor):
                request_data = await interceptor(request_data)
            else:
                request_data = interceptor(request_data)

        return request_data

    async def _execute_response_interceptors(self, response: APIResponse) -> APIResponse:
        """Execute all response interceptors"""
        for interceptor in self._response_interceptors:
            if asyncio.iscoroutinefunction(interceptor):
                response = await interceptor(response)
            else:
                response = interceptor(response)

        return response

    async def request(
        self,
        method: HTTPMethod,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> APIResponse:
        """
        Make async HTTP request with retry logic.

        Args:
            method: HTTP method
            endpoint: API endpoint (relative to base_url)
            headers: Request headers
            params: Query parameters
            json: JSON body
            data: Form data
            files: Files to upload
            **kwargs: Additional httpx parameters

        Returns:
            APIResponse object
        """
        if not self.client:
            await self.start()

        # Apply request interceptors
        request_data = await self._execute_request_interceptors(
            method=method.value,
            endpoint=endpoint,
            headers=headers,
            params=params,
            json=json,
            data=data,
            files=files,
            **kwargs,
        )

        # Extract modified data
        headers = request_data.get("headers", headers)
        params = request_data.get("params", params)
        json_body = request_data.get("json", json)
        data_body = request_data.get("data", data)

        # Retry logic
        last_exception = None

        for attempt in range(self.retry_count + 1):
            try:
                start_time = datetime.now()

                # Make request
                response = await self.client.request(
                    method=method.value,
                    url=endpoint,
                    headers=headers,
                    params=params,
                    json=json_body,
                    data=data_body,
                    files=files,
                    **kwargs,
                )

                duration = (datetime.now() - start_time).total_seconds()

                # Update metrics
                self.request_count += 1
                self.total_duration += duration

                # Parse response
                try:
                    body = response.json()
                except Exception:
                    body = response.text

                api_response = APIResponse(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=body,
                    duration=duration,
                )

                # Apply response interceptors
                api_response = await self._execute_response_interceptors(api_response)

                # Log request
                self.logger.info(
                    f"{method.value} {endpoint} - {response.status_code} ({duration:.3f}s)"
                )

                return api_response

            except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as e:
                last_exception = e

                if attempt < self.retry_count:
                    delay = self.retry_delay * (2**attempt)  # Exponential backoff
                    self.logger.warning(
                        f"Request failed (attempt {attempt + 1}/{self.retry_count + 1}). "
                        f"Retrying in {delay}s... Error: {e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(f"Request failed after {self.retry_count + 1} attempts")
                    raise

        # Should not reach here
        raise last_exception or Exception("Request failed")

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> APIResponse:
        """Make GET request"""
        return await self.request(
            HTTPMethod.GET, endpoint, params=params, headers=headers, **kwargs
        )

    async def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> APIResponse:
        """Make POST request"""
        return await self.request(
            HTTPMethod.POST, endpoint, json=json, data=data, headers=headers, **kwargs
        )

    async def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> APIResponse:
        """Make PUT request"""
        return await self.request(
            HTTPMethod.PUT, endpoint, json=json, data=data, headers=headers, **kwargs
        )

    async def patch(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> APIResponse:
        """Make PATCH request"""
        return await self.request(
            HTTPMethod.PATCH, endpoint, json=json, data=data, headers=headers, **kwargs
        )

    async def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> APIResponse:
        """Make DELETE request"""
        return await self.request(HTTPMethod.DELETE, endpoint, headers=headers, **kwargs)

    async def parallel_requests(self, requests: List[Dict[str, Any]]) -> List[APIResponse]:
        """
        Execute multiple requests in parallel.

        Args:
            requests: List of request configs, each with 'method', 'endpoint', etc.

        Returns:
            List of APIResponse objects

        Example:
            >>> requests = [
            ...     {"method": HTTPMethod.GET, "endpoint": "/users/1"},
            ...     {"method": HTTPMethod.GET, "endpoint": "/users/2"},
            ... ]
            >>> responses = await client.parallel_requests(requests)
        """
        tasks = [
            self.request(
                method=req.get("method", HTTPMethod.GET),
                endpoint=req.get("endpoint"),
                **{k: v for k, v in req.items() if k not in ["method", "endpoint"]},
            )
            for req in requests
        ]

        return await asyncio.gather(*tasks)

    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics"""
        avg_duration = self.total_duration / self.request_count if self.request_count > 0 else 0

        return {
            "request_count": self.request_count,
            "total_duration": self.total_duration,
            "average_duration": avg_duration,
        }


# ==================== Authentication Helpers ====================


class BearerAuth:
    """Bearer token authentication helper"""

    def __init__(self, token: str):
        self.token = token

    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.token}"}


class BasicAuth:
    """Basic authentication helper"""

    def __init__(self, username: str, password: str):
        import base64

        credentials = f"{username}:{password}".encode()
        self.encoded = base64.b64encode(credentials).decode()

    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {"Authorization": f"Basic {self.encoded}"}


# ==================== Example Usage ====================


async def example_usage():
    """Example usage of AsyncAPIClient"""

    # Initialize client
    async with AsyncAPIClient(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=10.0,
        retry_count=3,
    ) as client:
        # Add request logging interceptor
        def log_request(request_data):
            print(f"Making request: {request_data['method']} {request_data['endpoint']}")
            return request_data

        client.add_request_interceptor(log_request)

        # Single request
        response = await client.get("/posts/1")
        print(f"Status: {response.status_code}")
        print(f"Body: {response.body}")

        # Parallel requests
        requests = [{"method": HTTPMethod.GET, "endpoint": f"/posts/{i}"} for i in range(1, 6)]

        responses = await client.parallel_requests(requests)
        print(f"Completed {len(responses)} requests in parallel")

        # Check metrics
        metrics = client.get_metrics()
        print(f"Metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(example_usage())
