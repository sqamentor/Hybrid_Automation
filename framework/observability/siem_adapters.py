"""
SIEM Integration Adapters
==========================

Integrations for popular SIEM/observability platforms:
- Elasticsearch/ELK Stack
- Datadog
- Splunk
- Grafana Loki
- AWS CloudWatch
- Azure Monitor

Supports batching, retry logic, and circuit breaker patterns.
"""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests


# Constants
CONTENT_TYPE_JSON = "application/json"


class SIEMConnectionError(Exception):
    """Custom exception for SIEM connection failures"""
    pass


class SIEMProvider(Enum):
    """Supported SIEM providers"""
    ELK = "elk"
    DATADOG = "datadog"
    SPLUNK = "splunk"
    GRAFANA_LOKI = "grafana_loki"
    AWS_CLOUDWATCH = "aws_cloudwatch"
    AZURE_MONITOR = "azure_monitor"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failure threshold exceeded
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreaker:
    """Circuit breaker for SIEM integration resilience"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise SIEMConnectionError("Circuit breaker is OPEN - SIEM endpoint unavailable")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            import logging
            logging.getLogger(__name__).error(f"Circuit breaker failure: {e}", exc_info=True)
            raise
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.success_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.success_count = 0
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.recovery_timeout


class BaseSIEMAdapter(ABC):
    """Base class for SIEM adapters"""
    
    def __init__(
        self,
        endpoint: str,
        api_key: Optional[str] = None,
        batch_size: int = 100,
        flush_interval: float = 10.0,
        max_retries: int = 3
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.max_retries = max_retries
        
        self.buffer: deque = deque(maxlen=10000)  # Max 10k events in buffer
        self.last_flush = time.time()
        self.circuit_breaker = CircuitBreaker()
        
        # Start background flush task
        self._flush_task = None
    
    @abstractmethod
    def format_log(self, log_data: Dict) -> Dict:
        """Format log for specific SIEM platform"""
        pass
    
    @abstractmethod
    def send_batch(self, logs: List[Dict]) -> bool:
        """Send batch of logs to SIEM"""
        pass
    
    def add_log(self, log_data: Dict):
        """Add log to buffer"""
        formatted_log = self.format_log(log_data)
        self.buffer.append(formatted_log)
        
        # Flush if buffer is full
        if len(self.buffer) >= self.batch_size:
            self.flush()
    
    def flush(self):
        """Flush buffered logs to SIEM"""
        if not self.buffer:
            return
        
        batch = []
        while self.buffer and len(batch) < self.batch_size:
            batch.append(self.buffer.popleft())
        
        if batch:
            try:
                self.circuit_breaker.call(self.send_batch, batch)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.exception(f"Failed to send logs to SIEM: {e}")
                # Re-add to buffer for retry
                self.buffer.extendleft(reversed(batch))
        
        self.last_flush = time.time()
    
    def should_flush(self) -> bool:
        """Check if it's time to flush"""
        return (time.time() - self.last_flush) >= self.flush_interval
    
    async def auto_flush(self):
        """Background task to periodically flush logs"""
        while True:
            await asyncio.sleep(self.flush_interval)
            if self.buffer:
                self.flush()


class ElasticsearchAdapter(BaseSIEMAdapter):
    """Elasticsearch/ELK Stack adapter"""
    
    def __init__(
        self,
        endpoint: str,
        index_name: str = "test-automation",
        api_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(endpoint, api_key, **kwargs)
        self.index_name = index_name
        self.bulk_endpoint = urljoin(endpoint, f"/{index_name}/_bulk")
    
    def format_log(self, log_data: Dict) -> Dict:
        """Format for Elasticsearch"""
        # Elasticsearch expects @timestamp for time-series data
        if 'timestamp' in log_data:
            log_data['@timestamp'] = log_data['timestamp']
        return log_data
    
    def send_batch(self, logs: List[Dict]) -> bool:
        """Send batch using Elasticsearch bulk API"""
        # Elasticsearch bulk format: action line, then document
        bulk_data = []
        for log in logs:
            action = {"index": {"_index": self.index_name}}
            bulk_data.append(json.dumps(action))
            bulk_data.append(json.dumps(log))
        
        payload = "\n".join(bulk_data) + "\n"
        
        headers = {
            "Content-Type": "application/x-ndjson"
        }
        if self.api_key:
            headers["Authorization"] = f"ApiKey {self.api_key}"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.bulk_endpoint,
                    data=payload,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                return True
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Elasticsearch send attempt {attempt + 1} failed: {e}", exc_info=True)
                if attempt == self.max_retries - 1:
                    logger.error(f"All retry attempts exhausted for Elasticsearch: {e}", exc_info=True)
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return False


class DatadogAdapter(BaseSIEMAdapter):
    """Datadog adapter"""
    
    def __init__(
        self,
        api_key: str,
        site: str = "datadoghq.com",
        service: str = "test-automation",
        **kwargs
    ):
        endpoint = f"https://http-intake.logs.{site}/api/v2/logs"
        super().__init__(endpoint, api_key, **kwargs)
        self.service = service
    
    def format_log(self, log_data: Dict) -> Dict:
        """Format for Datadog"""
        # Datadog format
        return {
            "ddsource": "test-automation",
            "ddtags": f"env:{log_data.get('environment', 'unknown')},service:{self.service}",
            "hostname": log_data.get('hostname', 'unknown'),
            "message": log_data.get('message', ''),
            "service": self.service,
            **log_data
        }
    
    def send_batch(self, logs: List[Dict]) -> bool:
        """Send batch to Datadog"""
        headers = {
            "Content-Type": CONTENT_TYPE_JSON,
            "DD-API-KEY": self.api_key
        }
        
        payload = logs  # Datadog accepts JSON array
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.endpoint,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                return True
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Datadog send attempt {attempt + 1} failed: {e}", exc_info=True)
                if attempt == self.max_retries - 1:
                    logger.error(f"All retry attempts exhausted for Datadog: {e}", exc_info=True)
                    raise
                time.sleep(2 ** attempt)
        
        return False


class SplunkAdapter(BaseSIEMAdapter):
    """Splunk HEC (HTTP Event Collector) adapter"""
    
    def __init__(
        self,
        endpoint: str,
        hec_token: str,
        index: str = "main",
        source: str = "test-automation",
        **kwargs
    ):
        super().__init__(endpoint, hec_token, **kwargs)
        self.index = index
        self.source = source
        self.hec_endpoint = urljoin(endpoint, "/services/collector/event")
    
    def format_log(self, log_data: Dict) -> Dict:
        """Format for Splunk HEC"""
        return {
            "time": log_data.get('timestamp_ms', int(time.time() * 1000)) / 1000,
            "host": log_data.get('hostname', 'unknown'),
            "source": self.source,
            "sourcetype": "_json",
            "index": self.index,
            "event": log_data
        }
    
    def send_batch(self, logs: List[Dict]) -> bool:
        """Send batch to Splunk HEC"""
        headers = {
            "Authorization": f"Splunk {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Splunk HEC can accept multiple events in one request
        # Each event should be on its own line (not a JSON array)
        payload = "\n".join(json.dumps(log) for log in logs)
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.hec_endpoint,
                    data=payload,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                return True
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Splunk send attempt {attempt + 1} failed: {e}", exc_info=True)
                if attempt == self.max_retries - 1:
                    logger.error(f"All retry attempts exhausted for Splunk: {e}", exc_info=True)
                    raise
                time.sleep(2 ** attempt)
        
        return False


class GrafanaLokiAdapter(BaseSIEMAdapter):
    """Grafana Loki adapter"""
    
    def __init__(
        self,
        endpoint: str,
        labels: Optional[Dict] = None,
        **kwargs
    ):
        super().__init__(endpoint, **kwargs)
        self.push_endpoint = urljoin(endpoint, "/loki/api/v1/push")
        self.labels = labels or {"job": "test-automation"}
    
    def format_log(self, log_data: Dict) -> Dict:
        """Format for Loki"""
        # Loki stores logs as streams with labels
        timestamp_ns = str(int(log_data.get('timestamp_ms', time.time() * 1000) * 1000000))
        
        return {
            "stream": self.labels,
            "values": [[timestamp_ns, json.dumps(log_data)]]
        }
    
    def send_batch(self, logs: List[Dict]) -> bool:
        """Send batch to Loki"""
        # Combine logs into streams
        payload = {"streams": logs}
        
        headers = {"Content-Type": CONTENT_TYPE_JSON}
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.push_endpoint,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                return True
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Grafana Loki send attempt {attempt + 1} failed: {e}", exc_info=True)
                if attempt == self.max_retries - 1:
                    logger.error(f"All retry attempts exhausted for Grafana Loki: {e}", exc_info=True)
                    raise
                time.sleep(2 ** attempt)
        
        return False


class SIEMAdapterFactory:
    """Factory for creating SIEM adapters"""
    
    @staticmethod
    def create_adapter(
        provider: SIEMProvider,
        config: Dict[str, Any]
    ) -> BaseSIEMAdapter:
        """Create appropriate SIEM adapter"""
        
        if provider == SIEMProvider.ELK:
            return ElasticsearchAdapter(
                endpoint=config.get('endpoint', 'http://localhost:9200'),
                index_name=config.get('index_name', 'test-automation'),
                api_key=config.get('api_key'),
                batch_size=config.get('batch_size', 100),
                flush_interval=config.get('flush_interval', 10.0)
            )
        
        elif provider == SIEMProvider.DATADOG:
            return DatadogAdapter(
                api_key=config['api_key'],
                site=config.get('site', 'datadoghq.com'),
                service=config.get('service', 'test-automation'),
                batch_size=config.get('batch_size', 100),
                flush_interval=config.get('flush_interval', 10.0)
            )
        
        elif provider == SIEMProvider.SPLUNK:
            return SplunkAdapter(
                endpoint=config['endpoint'],
                hec_token=config['hec_token'],
                index=config.get('index', 'main'),
                source=config.get('source', 'test-automation'),
                batch_size=config.get('batch_size', 100),
                flush_interval=config.get('flush_interval', 10.0)
            )
        
        elif provider == SIEMProvider.GRAFANA_LOKI:
            return GrafanaLokiAdapter(
                endpoint=config['endpoint'],
                labels=config.get('labels', {"job": "test-automation"}),
                batch_size=config.get('batch_size', 100),
                flush_interval=config.get('flush_interval', 10.0)
            )
        
        else:
            raise ValueError(f"Unsupported SIEM provider: {provider}")


__all__ = [
    'SIEMProvider',
    'BaseSIEMAdapter',
    'ElasticsearchAdapter',
    'DatadogAdapter',
    'SplunkAdapter',
    'GrafanaLokiAdapter',
    'SIEMAdapterFactory',
    'CircuitBreaker'
]
