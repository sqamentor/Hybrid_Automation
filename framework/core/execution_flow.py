"""
Execution Flow Orchestrator

This module orchestrates the complete UI → API → DB execution flow.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from utils.logger import get_logger

try:
    from config.settings import should_run_api_validation, should_run_db_validation
except ImportError:
    # Fallback if settings not available
    def should_run_api_validation() -> bool:
        return True
    def should_run_db_validation() -> bool:
        return True

logger = get_logger(__name__)


@dataclass
class ExecutionContext:
    """Context for a single test execution"""
    test_name: str
    engine: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    ui_actions: List[Dict[str, Any]] = field(default_factory=list)
    api_calls: List[Dict[str, Any]] = field(default_factory=list)
    db_validations: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "in_progress"  # in_progress, passed, failed, error
    error: Optional[str] = None
    evidence: Dict[str, List[str]] = field(default_factory=lambda: {
        "screenshots": [],
        "videos": [],
        "traces": [],
        "api_logs": [],
        "db_logs": []
    })


class ExecutionFlow:
    """Orchestrates UI → API → DB execution flow"""
    
    def __init__(self):
        self.current_context: Optional[ExecutionContext] = None
        self.contexts: List[ExecutionContext] = []
    
    def start_execution(self, test_name: str, engine: str) -> ExecutionContext:
        """Start new test execution"""
        context = ExecutionContext(test_name=test_name, engine=engine)
        self.current_context = context
        self.contexts.append(context)
        
        logger.info(f"Started execution: {test_name} using {engine}")
        return context
    
    def record_ui_action(self, action: str, details: Dict[str, Any]):
        """Record UI action"""
        if self.current_context:
            self.current_context.ui_actions.append({
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "details": details
            })
            logger.debug(f"UI Action: {action}")
    
    def record_api_call(self, method: str, url: str, request: Dict, response: Dict):
        """Record API call (only if API validation enabled)"""
        if not should_run_api_validation():
            logger.debug("API validation disabled - skipping API call recording")
            return
        
        if self.current_context:
            self.current_context.api_calls.append({
                "timestamp": datetime.now().isoformat(),
                "method": method,
                "url": url,
                "request": request,
                "response": response
            })
            logger.debug(f"API Call: {method} {url}")
    
    def record_db_validation(self, query: str, result: Any, assertion: str):
        """Record database validation (only if DB validation enabled)"""
        if not should_run_db_validation():
            logger.debug("Database validation disabled - skipping DB validation recording")
            return
        
        if self.current_context:
            self.current_context.db_validations.append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "result": result,
                "assertion": assertion
            })
            logger.debug(f"DB Validation: {assertion}")
    
    def add_evidence(self, evidence_type: str, file_path: str):
        """Add evidence file"""
        if self.current_context:
            self.current_context.evidence[evidence_type].append(file_path)
            logger.debug(f"Evidence added: {evidence_type} -> {file_path}")
    
    def complete_execution(self, status: str, error: Optional[str] = None):
        """Complete test execution"""
        if self.current_context:
            self.current_context.end_time = datetime.now()
            self.current_context.status = status
            self.current_context.error = error
            
            duration = (self.current_context.end_time - self.current_context.start_time).total_seconds()
            logger.info(f"Completed execution: {self.current_context.test_name} - {status} ({duration:.2f}s)")
    
    def get_correlation_keys(self) -> Dict[str, Any]:
        """Extract correlation keys from API calls"""
        if not self.current_context:
            return {}
        
        keys = {}
        for api_call in self.current_context.api_calls:
            response = api_call.get('response', {})
            
            # Extract common correlation keys
            if 'transaction_id' in response:
                keys['transaction_id'] = response['transaction_id']
            if 'order_id' in response:
                keys['order_id'] = response['order_id']
            if 'request_id' in response:
                keys['request_id'] = response['request_id']
            
            # Extract from headers
            headers = api_call.get('request', {}).get('headers', {})
            if 'x-request-id' in headers:
                keys['x-request-id'] = headers['x-request-id']
        
        return keys
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate execution report"""
        if not self.current_context:
            return {}
        
        ctx = self.current_context
        
        return {
            "test_name": ctx.test_name,
            "engine": ctx.engine,
            "status": ctx.status,
            "start_time": ctx.start_time.isoformat(),
            "end_time": ctx.end_time.isoformat() if ctx.end_time else None,
            "duration_seconds": (ctx.end_time - ctx.start_time).total_seconds() if ctx.end_time else 0,
            "ui_actions_count": len(ctx.ui_actions),
            "api_calls_count": len(ctx.api_calls),
            "db_validations_count": len(ctx.db_validations),
            "evidence": ctx.evidence,
            "error": ctx.error
        }


# Global execution flow instance
execution_flow = ExecutionFlow()


__all__ = ['ExecutionFlow', 'ExecutionContext', 'execution_flow']
