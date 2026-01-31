"""
Integration Test Example - UI → API → DB Flow

This example demonstrates the complete execution flow:
1. UI Action (login, add to cart, checkout)
2. API Capture & Validation
3. Database Verification
4. Evidence Collection
"""

import pytest
from framework.core.execution_flow import execution_flow
from framework.database.db_validator import DBValidator


@pytest.mark.integration
@pytest.mark.module("checkout")
@pytest.mark.modern_spa
@pytest.mark.ui_framework("React")
class TestOrderPlacement:
    """Integration test for order placement flow"""
    
    def test_complete_order_flow(self, ui_engine, api_client, db_client, ui_url):
        """
        Test complete order placement:
        UI → Add to cart → Checkout → Verify API → Verify DB
        """
        # Start execution tracking
        ctx = execution_flow.start_execution("test_complete_order_flow", "playwright")
        
        try:
            # ============================================================
            # STEP 1: UI ACTIONS
            # ============================================================
            
            # Navigate to application
            ui_engine.navigate(ui_url)
            execution_flow.record_ui_action("navigate", {"url": ui_url})
            
            # Login
            ui_engine.fill("#email", "test.user@example.com")
            ui_engine.fill("#password", "SecurePassword123")
            ui_engine.click("#login-button")
            execution_flow.record_ui_action("login", {"user": "test.user@example.com"})
            
            # Add product to cart
            ui_engine.click("#product-123")
            ui_engine.click("#add-to-cart")
            execution_flow.record_ui_action("add_to_cart", {"product_id": "123"})
            
            # Proceed to checkout
            ui_engine.click("#checkout-button")
            execution_flow.record_ui_action("checkout", {})
            
            # ============================================================
            # STEP 2: API VALIDATION
            # ============================================================
            
            # Verify order was created via API
            # Note: In real implementation, capture this from network interception
            response = api_client.get("/api/orders/recent")
            api_client.assert_status_code(200)
            
            orders = response.json()
            assert len(orders) > 0, "No orders found"
            
            latest_order = orders[0]
            order_id = latest_order['order_id']
            transaction_id = latest_order['transaction_id']
            
            execution_flow.record_api_call(
                "GET",
                "/api/orders/recent",
                {},
                {"order_id": order_id, "status": "PENDING"}
            )
            
            # ============================================================
            # STEP 3: DATABASE VERIFICATION
            # ============================================================
            
            db_validator = DBValidator(db_client)
            
            # Verify order exists in database
            db_validator.assert_row_exists(
                table="orders",
                conditions={"order_id": order_id},
                schema="dbo"
            )
            
            execution_flow.record_db_validation(
                f"SELECT * FROM dbo.orders WHERE order_id = '{order_id}'",
                {"found": True},
                "Order exists in database"
            )
            
            # Verify order status
            db_validator.assert_column_value(
                table="orders",
                column="status",
                expected_value="PENDING",
                conditions={"order_id": order_id},
                schema="dbo"
            )
            
            execution_flow.record_db_validation(
                f"SELECT status FROM dbo.orders WHERE order_id = '{order_id}'",
                {"status": "PENDING"},
                "Order status is PENDING"
            )
            
            # Verify order items
            db_validator.assert_row_exists(
                table="order_items",
                conditions={"order_id": order_id, "product_id": "123"},
                schema="dbo"
            )
            
            execution_flow.record_db_validation(
                f"SELECT * FROM dbo.order_items WHERE order_id = '{order_id}'",
                {"found": True},
                "Order items exist in database"
            )
            
            # ============================================================
            # STEP 4: COMPLETION
            # ============================================================
            
            execution_flow.complete_execution("passed")
            
            # Generate and log report
            report = execution_flow.generate_report()
            print(f"\n{'='*80}")
            print("EXECUTION REPORT")
            print(f"{'='*80}")
            print(f"Test: {report['test_name']}")
            print(f"Engine: {report['engine']}")
            print(f"Status: {report['status']}")
            print(f"Duration: {report['duration_seconds']:.2f}s")
            print(f"UI Actions: {report['ui_actions_count']}")
            print(f"API Calls: {report['api_calls_count']}")
            print(f"DB Validations: {report['db_validations_count']}")
            print(f"{'='*80}\n")
        
        except Exception as e:
            execution_flow.complete_execution("failed", str(e))
            raise


@pytest.mark.integration
@pytest.mark.module("admin")
@pytest.mark.legacy_ui
@pytest.mark.auth_type("SSO")
class TestAdminPanel:
    """Integration test for admin panel (forces Selenium)"""
    
    def test_admin_login_and_report_generation(self, ui_engine, db_client):
        """
        Test admin panel access with SSO
        This test will be auto-routed to Selenium due to SSO marker
        """
        ctx = execution_flow.start_execution("test_admin_login_and_report_generation", "selenium")
        
        try:
            # Admin actions would go here
            # This is routed to Selenium due to SSO/legacy_ui markers
            
            execution_flow.complete_execution("passed")
        
        except Exception as e:
            execution_flow.complete_execution("failed", str(e))
            raise
