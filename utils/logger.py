"""
Logger - Centralized Logging Configuration with Audit Trail

Provides consistent logging across the framework with:
- Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Separate audit trail for compliance
- Log rotation for disk management
- Structured logging with contextual information
- Action and event tracking
"""

import logging
import sys
import json
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional, Dict, Any


# Global configuration
LOG_DIR = Path("logs")
AUDIT_DIR = LOG_DIR / "audit"
LOG_DIR.mkdir(exist_ok=True)
AUDIT_DIR.mkdir(exist_ok=True)


class AuditLogger:
    """
    Specialized logger for audit trail
    Captures all test actions, API calls, DB operations, and framework events
    """
    
    def __init__(self):
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
        
        # Only configure once
        if not self.logger.handlers:
            # Daily rotating audit log
            audit_file = AUDIT_DIR / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
            audit_handler = TimedRotatingFileHandler(
                audit_file,
                when='midnight',
                interval=1,
                backupCount=90,  # Keep 90 days of audit logs
                encoding='utf-8'
            )
            audit_handler.setLevel(logging.INFO)
            
            # JSON format for easy parsing and compliance tools
            audit_format = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"event_type": "%(name)s", "message": %(message)s}',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            audit_handler.setFormatter(audit_format)
            self.logger.addHandler(audit_handler)
    
    def log_action(self, action_type: str, details: Dict[str, Any], status: str = "success"):
        """
        Log test action with structured data
        
        Args:
            action_type: Type of action (ui_click, api_call, db_query, etc.)
            details: Action details as dictionary
            status: Action status (success, failure, warning)
        """
        event = {
            "action_type": action_type,
            "status": status,
            "details": details,
            "timestamp_ms": datetime.now().timestamp() * 1000
        }
        self.logger.info(json.dumps(event))
    
    def log_test_start(self, test_name: str, test_file: str):
        """Log test execution start"""
        self.log_action("test_start", {
            "test_name": test_name,
            "test_file": test_file
        })
    
    def log_test_end(self, test_name: str, status: str, duration: float):
        """Log test execution end"""
        self.log_action("test_end", {
            "test_name": test_name,
            "duration_seconds": duration,
            "result": status
        }, status=status)
    
    def log_ui_action(self, action: str, element: str, value: Optional[str] = None):
        """Log UI interaction"""
        details = {"action": action, "element": element}
        if value:
            details["value"] = value
        self.log_action("ui_action", details)
    
    def log_api_call(self, method: str, url: str, status_code: int, 
                     duration_ms: float, request_body: Optional[Dict] = None,
                     response_body: Optional[Dict] = None):
        """Log API call with request/response"""
        details = {
            "method": method,
            "url": url,
            "status_code": status_code,
            "duration_ms": duration_ms
        }
        if request_body:
            details["request"] = request_body
        if response_body:
            details["response"] = response_body
        
        status = "success" if 200 <= status_code < 300 else "failure"
        self.log_action("api_call", details, status=status)
    
    def log_db_operation(self, operation: str, table: str, query: str, 
                        rows_affected: int = 0, duration_ms: float = 0):
        """Log database operation"""
        self.log_action("db_operation", {
            "operation": operation,
            "table": table,
            "query": query,
            "rows_affected": rows_affected,
            "duration_ms": duration_ms
        })
    
    def log_error(self, error_type: str, error_message: str, stack_trace: Optional[str] = None):
        """Log error with details"""
        details = {
            "error_type": error_type,
            "error_message": error_message
        }
        if stack_trace:
            details["stack_trace"] = stack_trace
        self.log_action("error", details, status="failure")


# Singleton audit logger instance
_audit_logger = None

def get_audit_logger() -> AuditLogger:
    """Get the global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger instance
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance with console and rotating file handlers
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Console handler - INFO level for clean output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # Rotating file handler - DEBUG level with 50MB rotation
        log_file = LOG_DIR / f"framework_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=50 * 1024 * 1024,  # 50 MB
            backupCount=10,  # Keep 10 backup files
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
        # Error file handler - Separate file for errors only
        error_log_file = LOG_DIR / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        logger.addHandler(error_handler)
    
    return logger


__all__ = ['get_logger', 'get_audit_logger', 'AuditLogger']
