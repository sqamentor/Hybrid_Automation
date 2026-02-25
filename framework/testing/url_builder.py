"""
URL Builder

Constructs URLs with query parameters and path segments.
Follows Builder pattern from framework (QueryBuilder, CommandBuilder, etc.)

Pattern: Builder
Extends: None
Dependencies: URLFormat enum

Author: Hybrid Automation Framework
Date: 2026-02-25
"""

from typing import Dict, Optional, Any, List
from urllib.parse import urlencode, quote, urlparse, parse_qs
from framework.microservices.url_testing_service import URLFormat
from framework.observability.enterprise_logger import get_enterprise_logger
from framework.observability.universal_logger import log_function


logger = get_enterprise_logger()


class URLBuilder:
    """
    URL Builder - Constructs URLs from templates
    
    Responsibilities:
    - Apply URL templates (query string, path-based)
    - Inject workflow_id and parameters
    - Support multiple URL formats
    - URL encoding and validation
    
    Pattern: Builder
    Used By: URLTestingService, page objects, fixtures
    """
    
    def __init__(self, base_url: str, url_format: URLFormat = URLFormat.QUERY_STRING):
        self.base_url = base_url.rstrip("/")
        self.url_format = url_format
        
        logger.debug(f"URLBuilder initialized: base_url={base_url}, format={url_format.value}")
    
    @log_function(log_args=False, log_result=True)
    def build(
        self,
        workflow_id: str,
        page_path: str = "",
        query_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build complete URL from components
        
        Args:
            workflow_id: Workflow ID to inject
            page_path: Page path (e.g., /booking, /schedule)
            query_params: Additional query parameters
        
        Returns:
            Complete URL string
        """
        query_params = query_params or {}
        
        logger.debug(f"Building URL: workflow_id={workflow_id}, page_path={page_path}, params={query_params}")
        
        if self.url_format == URLFormat.QUERY_STRING:
            url = self._build_query_string(workflow_id, page_path, query_params)
        elif self.url_format == URLFormat.PATH_PARAM:
            url = self._build_path_param(workflow_id, page_path, query_params)
        elif self.url_format == URLFormat.PATH_BASED:
            url = self._build_path_based(workflow_id, page_path, query_params)
        else:
            url = self._build_hybrid(workflow_id, page_path, query_params)
        
        logger.info(f"Built URL: {url}")
        return url
    
    def _build_query_string(
        self,
        workflow_id: str,
        page_path: str,
        query_params: Dict[str, Any]
    ) -> str:
        """Build query string URL: domain.com/page?workflow_id=X&param=Y"""
        url = f"{self.base_url}{page_path}"
        
        # Add workflow_id as first parameter
        all_params = {"workflow_id": workflow_id, **query_params}
        
        if all_params:
            query_string = urlencode(all_params, safe='', quote_via=quote)
            url = f"{url}?{query_string}"
        
        return url
    
    def _build_path_param(
        self,
        workflow_id: str,
        page_path: str,
        query_params: Dict[str, Any]
    ) -> str:
        """Build path param URL: domain.com/workflow/X/page?param=Y"""
        url = f"{self.base_url}/workflow/{workflow_id}{page_path}"
        
        if query_params:
            query_string = urlencode(query_params, safe='', quote_via=quote)
            url = f"{url}?{query_string}"
        
        return url
    
    def _build_path_based(
        self,
        workflow_id: str,
        page_path: str,
        query_params: Dict[str, Any]
    ) -> str:
        """Build path-based URL: domain.com/X/booking?param=Y"""
        url = f"{self.base_url}/{workflow_id}{page_path}"
        
        if query_params:
            query_string = urlencode(query_params, safe='', quote_via=quote)
            url = f"{url}?{query_string}"
        
        return url
    
    def _build_hybrid(
        self,
        workflow_id: str,
        page_path: str,
        query_params: Dict[str, Any]
    ) -> str:
        """Build hybrid URL: domain.com/X?param=Y"""
        url = f"{self.base_url}/{workflow_id}"
        
        if query_params:
            query_string = urlencode(query_params, safe='', quote_via=quote)
            url = f"{url}?{query_string}"
        
        return url
    
    def parse_url(self, url: str) -> Dict[str, Any]:
        """
        Parse URL into components
        
        Args:
            url: URL to parse
        
        Returns:
            Dictionary with URL components
        """
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Convert query params from list values to single values
        query_params_flat = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
        
        components = {
            "scheme": parsed.scheme,
            "netloc": parsed.netloc,
            "path": parsed.path,
            "query": parsed.query,
            "query_params": query_params_flat,
            "fragment": parsed.fragment,
            "base_url": f"{parsed.scheme}://{parsed.netloc}"
        }
        
        logger.debug(f"Parsed URL: {components}")
        return components
    
    def extract_workflow_id(self, url: str) -> Optional[str]:
        """
        Extract workflow ID from URL
        
        Args:
            url: URL to extract from
        
        Returns:
            Workflow ID if found, None otherwise
        """
        components = self.parse_url(url)
        
        # Check query parameters first
        workflow_id = components["query_params"].get("workflow_id")
        
        if workflow_id:
            logger.debug(f"Found workflow_id in query params: {workflow_id}")
            return workflow_id
        
        # Check path segments
        path_segments = components["path"].strip("/").split("/")
        
        # Look for workflow ID in path (common patterns)
        for i, segment in enumerate(path_segments):
            if segment == "workflow" and i + 1 < len(path_segments):
                workflow_id = path_segments[i + 1]
                logger.debug(f"Found workflow_id in path: {workflow_id}")
                return workflow_id
            
            # Check if segment looks like a workflow ID (starts with WF-)
            if segment.startswith("WF-"):
                logger.debug(f"Found workflow_id pattern in path: {segment}")
                return segment
        
        logger.warning(f"No workflow_id found in URL: {url}")
        return None
    
    def add_query_params(self, url: str, params: Dict[str, Any]) -> str:
        """
        Add query parameters to existing URL
        
        Args:
            url: Base URL
            params: Parameters to add
        
        Returns:
            URL with added parameters
        """
        if not params:
            return url
        
        parsed = urlparse(url)
        existing_params = parse_qs(parsed.query)
        
        # Flatten existing params
        existing_params_flat = {k: v[0] if len(v) == 1 else v for k, v in existing_params.items()}
        
        # Merge with new params (new params override existing)
        all_params = {**existing_params_flat, **params}
        
        # Rebuild URL
        query_string = urlencode(all_params, safe='', quote_via=quote)
        
        if parsed.query:
            # Replace existing query string
            new_url = url.replace(f"?{parsed.query}", f"?{query_string}")
        else:
            # Add query string
            new_url = f"{url}?{query_string}"
        
        logger.debug(f"Added params to URL: {new_url}")
        return new_url
    
    def remove_query_params(self, url: str, param_names: List[str]) -> str:
        """
        Remove specific query parameters from URL
        
        Args:
            url: URL with parameters
            param_names: Parameter names to remove
        
        Returns:
            URL with parameters removed
        """
        parsed = urlparse(url)
        existing_params = parse_qs(parsed.query)
        
        # Remove specified parameters
        filtered_params = {k: v for k, v in existing_params.items() if k not in param_names}
        
        # Flatten params
        filtered_params_flat = {k: v[0] if len(v) == 1 else v for k, v in filtered_params.items()}
        
        if filtered_params_flat:
            query_string = urlencode(filtered_params_flat, safe='', quote_via=quote)
            new_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{query_string}"
        else:
            new_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        logger.debug(f"Removed params from URL: {new_url}")
        return new_url
