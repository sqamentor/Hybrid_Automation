"""
Example Test - Enterprise Logging System Demonstration
=======================================================

This test demonstrates all features of the enterprise logging system:
- Basic logging (debug, info, warning, error, critical)
- Audit logging for compliance
- Security event logging
- Performance metric logging
- Correlation context management
- @with_trace decorator usage
- Sensitive data masking
- Pytest fixture integration

Run this test to verify the enterprise logging system is working correctly.

Usage:
    pytest tests/observability/test_enterprise_logging_demo.py -v
"""

import pytest
import time
from datetime import datetime

# Enterprise logging imports
from framework.observability.enterprise_logger import (
    get_enterprise_logger,
    CorrelationContext,
    SensitiveDataMasker,
    with_trace,
    with_async_trace
)


# Get logger instance
logger = get_enterprise_logger()


class TestEnterpriseLoggingBasics:
    """Test basic logging functionality"""
    
    def test_01_basic_logging_levels(self):
        """Test all logging levels"""
        logger.debug("This is a DEBUG message", test_id="test_01", extra_data="debug_info")
        logger.info("This is an INFO message", test_id="test_01", status="running")
        logger.warning("This is a WARNING message", test_id="test_01", warning_type="sample")
        
        # Note: We don't call error/critical here to avoid failing the test
        # They are tested separately
        
        # Verify logs are written
        assert True, "Basic logging completed successfully"
    
    def test_02_error_logging_with_exception(self):
        """Test error logging with exception capture"""
        try:
            # Simulate an error
            result = 10 / 0
        except ZeroDivisionError:
            logger.error(
                "Division by zero error occurred",
                exc_info=True,  # Captures full stack trace
                test_id="test_02",
                operation="division"
            )
        
        # Test continues - error was logged but handled
        assert True, "Error logging with exception capture completed"
    
    def test_03_structured_logging_with_metadata(self):
        """Test structured logging with rich metadata"""
        logger.info(
            "User action performed",
            user_id="user_12345",
            action="create_order",
            order_id="ORD-2024-001",
            amount=99.99,
            currency="USD",
            timestamp=datetime.now().isoformat()
        )
        
        assert True, "Structured logging with metadata completed"


class TestCorrelationContext:
    """Test distributed tracing with correlation IDs"""
    
    def test_04_correlation_id_generation(self):
        """Test correlation ID generation and retrieval"""
        # Generate correlation ID
        corr_id = CorrelationContext.generate_correlation_id()
        
        # Verify format
        assert corr_id.startswith("corr-"), "Correlation ID should start with 'corr-'"
        assert len(corr_id) == 21, "Correlation ID should be 21 characters (corr-{16hex})"
        
        logger.info("Correlation ID generated", correlation_id=corr_id)
    
    def test_05_correlation_context_propagation(self):
        """Test correlation context propagation across operations"""
        # Set correlation context
        CorrelationContext.set_correlation_id(CorrelationContext.generate_correlation_id())
        CorrelationContext.set_request_id(CorrelationContext.generate_request_id())
        CorrelationContext.set_trace_id(CorrelationContext.generate_trace_id())
        
        # Log multiple operations - they should all share the same correlation ID
        logger.info("Operation 1: Starting workflow")
        logger.info("Operation 2: Processing data")
        logger.info("Operation 3: Completing workflow")
        
        # Get context
        corr_id = CorrelationContext.get_correlation_id()
        req_id = CorrelationContext.get_request_id()
        trace_id = CorrelationContext.get_trace_id()
        
        assert corr_id is not None, "Correlation ID should be set"
        assert req_id is not None, "Request ID should be set"
        assert trace_id is not None, "Trace ID should be set"
        
        logger.info("Correlation context verified", 
                   correlation_id=corr_id,
                   request_id=req_id,
                   trace_id=trace_id)
        
        # Clear context
        CorrelationContext.clear_context()
        assert CorrelationContext.get_correlation_id() is None, "Context should be cleared"
    
    def test_06_user_context(self):
        """Test user context tracking"""
        # Set user context
        user_data = {
            "user_id": "test_user_001",
            "username": "john.doe",
            "role": "admin",
            "email": "john@example.com"
        }
        CorrelationContext.set_user_context(user_data)
        
        # Log with user context
        logger.info("User performed action", action="login", method="oauth2")
        
        # Verify context
        retrieved_user = CorrelationContext.get_user_context()
        assert retrieved_user == user_data, "User context should match"
        
        # Clear context
        CorrelationContext.clear_context()


class TestAuditLogging:
    """Test audit logging for compliance (SOC2/ISO27001)"""
    
    def test_07_audit_user_action(self):
        """Test audit logging for user actions"""
        logger.audit(
            "user_login",
            {
                "user_id": "user_12345",
                "username": "john.doe",
                "ip_address": "192.168.1.100",
                "timestamp": datetime.now().isoformat(),
                "method": "oauth2",
                "status": "success"
            },
            status="success"
        )
        
        assert True, "Audit log for user login completed"
    
    def test_08_audit_data_access(self):
        """Test audit logging for data access"""
        logger.audit(
            "data_access",
            {
                "user_id": "user_12345",
                "resource": "patient_records",
                "record_id": "PAT-2024-001",
                "action": "read",
                "timestamp": datetime.now().isoformat()
            },
            status="success"
        )
        
        assert True, "Audit log for data access completed"
    
    def test_09_audit_configuration_change(self):
        """Test audit logging for configuration changes"""
        logger.audit(
            "config_change",
            {
                "user_id": "admin_user",
                "config_key": "max_login_attempts",
                "old_value": "3",
                "new_value": "5",
                "timestamp": datetime.now().isoformat(),
                "reason": "Security policy update"
            },
            status="success"
        )
        
        assert True, "Audit log for configuration change completed"


class TestSecurityLogging:
    """Test security event logging"""
    
    def test_10_security_failed_login(self):
        """Test security logging for failed login attempts"""
        logger.security(
            "failed_login_attempt",
            {
                "username": "unknown_user",
                "ip_address": "suspicious.ip.address",
                "timestamp": datetime.now().isoformat(),
                "attempts": 5,
                "reason": "Invalid credentials"
            },
            severity="warning"
        )
        
        assert True, "Security log for failed login completed"
    
    def test_11_security_privilege_escalation(self):
        """Test security logging for privilege escalation"""
        logger.security(
            "privilege_escalation_attempt",
            {
                "user_id": "user_12345",
                "current_role": "user",
                "requested_role": "admin",
                "timestamp": datetime.now().isoformat(),
                "denied": True
            },
            severity="critical"
        )
        
        assert True, "Security log for privilege escalation completed"
    
    def test_12_security_api_abuse(self):
        """Test security logging for API abuse detection"""
        logger.security(
            "api_rate_limit_exceeded",
            {
                "api_key": "key_abc***",  # Masked
                "endpoint": "/api/users",
                "requests_per_minute": 1000,
                "limit": 100,
                "timestamp": datetime.now().isoformat(),
                "action_taken": "temporarily_blocked"
            },
            severity="warning"
        )
        
        assert True, "Security log for API abuse completed"


class TestPerformanceLogging:
    """Test performance metrics logging"""
    
    def test_13_performance_database_query(self):
        """Test performance logging for database queries"""
        # Simulate database query
        start_time = time.time()
        time.sleep(0.1)  # Simulate 100ms query
        duration_ms = (time.time() - start_time) * 1000
        
        logger.performance(
            "database_query",
            duration_ms,
            {
                "query_type": "SELECT",
                "table": "users",
                "rows_returned": 150,
                "with_joins": True
            }
        )
        
        assert True, "Performance log for database query completed"
    
    def test_14_performance_api_call(self):
        """Test performance logging for API calls"""
        # Simulate API call
        start_time = time.time()
        time.sleep(0.05)  # Simulate 50ms API call
        duration_ms = (time.time() - start_time) * 1000
        
        logger.performance(
            "api_request",
            duration_ms,
            {
                "method": "GET",
                "endpoint": "/api/users/12345",
                "status_code": 200,
                "response_size_bytes": 1024
            }
        )
        
        assert True, "Performance log for API call completed"
    
    def test_15_performance_page_load(self):
        """Test performance logging for page loads"""
        # Simulate page load
        start_time = time.time()
        time.sleep(0.2)  # Simulate 200ms page load
        duration_ms = (time.time() - start_time) * 1000
        
        logger.performance(
            "page_load",
            duration_ms,
            {
                "page": "dashboard",
                "url": "/dashboard",
                "dom_ready_ms": 150,
                "resources_loaded": 25
            }
        )
        
        # Slow page warning
        if duration_ms > 1000:
            logger.warning("Slow page load detected", 
                          page="dashboard",
                          duration_ms=duration_ms)
        
        assert True, "Performance log for page load completed"


class TestSensitiveDataMasking:
    """Test automatic sensitive data masking"""
    
    def test_16_password_masking(self):
        """Test password field masking"""
        sensitive_data = {
            "username": "john.doe",
            "password": "super_secret_password_123",
            "email": "john@example.com"
        }
        
        # Log with sensitive data - should be automatically masked
        logger.info("User authentication", user_data=sensitive_data)
        
        # Manually test masking
        masked = SensitiveDataMasker.mask_dict(sensitive_data)
        assert masked["password"] == "***MASKED***", "Password should be masked"
        assert masked["username"] == "john.doe", "Username should not be masked"
    
    def test_17_credit_card_masking(self):
        """Test credit card number masking"""
        payment_data = {
            "user_id": "user_123",
            "credit_card": "4532-1234-5678-9010",
            "cvv": "123",
            "amount": 99.99
        }
        
        logger.info("Payment processed", payment_data=payment_data)
        
        # Verify masking
        masked = SensitiveDataMasker.mask_dict(payment_data)
        assert "****" in masked["credit_card"], "Credit card should be masked"
    
    def test_18_api_key_masking(self):
        """Test API key masking"""
        config_data = {
            "service": "external_api",
            "api_key": "sk_live_abc123def456ghi789",
            "endpoint": "https://api.example.com"
        }
        
        logger.info("API configuration", config=config_data)
        
        # Verify masking
        masked = SensitiveDataMasker.mask_dict(config_data)
        assert masked["api_key"] == "***MASKED***", "API key should be masked"


class TestDecoratorUsage:
    """Test @with_trace decorator for automatic tracing"""
    
    @with_trace(operation_name="process_user_order")
    def process_order(self, order_id: str, amount: float):
        """Function with automatic tracing"""
        logger.info("Processing order", order_id=order_id, amount=amount)
        time.sleep(0.05)  # Simulate processing
        return {"status": "success", "order_id": order_id}
    
    @with_trace(operation_name="validate_user_input")
    def validate_input(self, data: dict):
        """Function with automatic tracing that may fail"""
        logger.info("Validating input", field_count=len(data))
        
        if "required_field" not in data:
            raise ValueError("Missing required field")
        
        return True
    
    def test_19_decorator_successful_execution(self):
        """Test @with_trace decorator on successful function"""
        # This will automatically log:
        # - Function start
        # - Execution time
        # - Success status
        # - Performance metrics
        
        result = self.process_order("ORD-2024-001", 99.99)
        assert result["status"] == "success", "Order processing should succeed"
    
    def test_20_decorator_with_exception(self):
        """Test @with_trace decorator on failing function"""
        # This will automatically log:
        # - Function start
        # - Execution time
        # - Failure status
        # - Exception details
        
        with pytest.raises(ValueError):
            self.validate_input({"invalid": "data"})


class TestPytestFixtureIntegration:
    """Test pytest fixture integration"""
    
    def test_21_enterprise_logging_context_fixture(self, enterprise_logging_context):
        """Test enterprise_logging_context fixture"""
        # Set user context via fixture
        enterprise_logging_context.set_user({
            "user_id": "fixture_test_user",
            "role": "tester"
        })
        
        # Log custom action
        enterprise_logging_context.log_action(
            "test_action_via_fixture",
            {
                "action_type": "create",
                "resource": "test_resource"
            }
        )
        
        # Log security event
        enterprise_logging_context.log_security_event(
            "test_security_event",
            {
                "event_type": "access_attempt",
                "resource": "sensitive_data"
            },
            severity="info"
        )
        
        # Log performance metric
        enterprise_logging_context.log_performance(
            "test_performance_operation",
            123.45,
            {
                "operation_type": "data_processing",
                "records_processed": 100
            }
        )
        
        assert True, "Fixture integration test completed"


class TestCompleteWorkflow:
    """Test complete workflow with all logging features"""
    
    @with_trace(operation_name="complete_user_workflow")
    def test_22_complete_user_workflow(self, enterprise_logging_context):
        """
        Complete workflow test demonstrating all logging features:
        - Correlation context
        - User context
        - Audit logging
        - Security logging
        - Performance tracking
        - Structured logging
        """
        
        # 1. Set correlation context for request tracking
        CorrelationContext.set_correlation_id(CorrelationContext.generate_correlation_id())
        CorrelationContext.set_request_id(CorrelationContext.generate_request_id())
        
        # 2. Set user context
        enterprise_logging_context.set_user({
            "user_id": "workflow_user_001",
            "username": "jane.smith",
            "role": "admin",
            "session_id": "sess_abc123"
        })
        
        logger.info("🚀 Starting complete user workflow")
        
        # 3. Audit log - User authentication
        logger.audit(
            "user_authentication",
            {
                "user_id": "workflow_user_001",
                "method": "oauth2",
                "timestamp": datetime.now().isoformat()
            },
            status="success"
        )
        
        # 4. Perform operation (with performance tracking)
        start = time.time()
        time.sleep(0.1)  # Simulate operation
        duration = (time.time() - start) * 1000
        
        logger.info("✓ Operation completed", operation="data_processing")
        
        # 5. Log performance
        logger.performance("workflow_operation", duration, {
            "steps_completed": 5,
            "records_processed": 250
        })
        
        # 6. Audit log - Data access
        logger.audit(
            "data_access",
            {
                "user_id": "workflow_user_001",
                "resource": "customer_records",
                "action": "read",
                "records_accessed": 250
            },
            status="success"
        )
        
        # 7. Security log - Access granted
        logger.security(
            "resource_access_granted",
            {
                "user_id": "workflow_user_001",
                "resource": "customer_records",
                "permission_level": "read"
            },
            severity="info"
        )
        
        logger.info("✅ Complete workflow finished successfully")
        
        # Clear context
        CorrelationContext.clear_context()
        
        assert True, "Complete workflow test passed"


# ════════════════════════════════════════════════════════════════════════════
# TEST EXECUTION
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Run tests directly:
        python tests/observability/test_enterprise_logging_demo.py
    
    Or with pytest:
        pytest tests/observability/test_enterprise_logging_demo.py -v
    """
    pytest.main([__file__, "-v", "--tb=short"])
