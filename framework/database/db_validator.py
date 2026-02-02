"""
Database Validator - Database Assertion Engine

Provides validation methods for verifying database state.
"""

from typing import Any, Dict, List, Optional

from framework.database.db_client import DBClient
from utils.logger import get_logger

logger = get_logger(__name__)


class DBValidator:
    """Database validation and assertion engine"""

    def __init__(self, db_client: DBClient):
        self.db_client = db_client

    def verify_row_exists(
        self, table: str, conditions: Dict[str, Any], schema: str = "dbo"
    ) -> bool:
        """Verify that a row exists matching conditions"""
        where_clause = " AND ".join([f"{k} = :{k}" for k in conditions.keys()])
        query = f"SELECT COUNT(*) as cnt FROM {schema}.{table} WHERE {where_clause}"

        count = self.db_client.execute_scalar(query, conditions)
        exists = count > 0

        logger.info(f"Row exists in {table}: {exists}")
        return exists

    def verify_row_count(
        self,
        table: str,
        expected_count: int,
        conditions: Optional[Dict[str, Any]] = None,
        schema: str = "dbo",
    ) -> bool:
        """Verify row count in table"""
        query = f"SELECT COUNT(*) as cnt FROM {schema}.{table}"

        if conditions:
            where_clause = " AND ".join([f"{k} = :{k}" for k in conditions.keys()])
            query += f" WHERE {where_clause}"

        actual_count = self.db_client.execute_scalar(query, conditions or {})

        logger.info(f"Row count in {table}: expected={expected_count}, actual={actual_count}")
        return actual_count == expected_count

    def verify_column_value(
        self,
        table: str,
        column: str,
        expected_value: Any,
        conditions: Dict[str, Any],
        schema: str = "dbo",
    ) -> bool:
        """Verify specific column value"""
        where_clause = " AND ".join([f"{k} = :{k}" for k in conditions.keys()])
        query = f"SELECT {column} FROM {schema}.{table} WHERE {where_clause}"

        actual_value = self.db_client.execute_scalar(query, conditions)

        logger.info(f"{column} value: expected={expected_value}, actual={actual_value}")
        return actual_value == expected_value

    def assert_row_exists(self, table: str, conditions: Dict[str, Any], schema: str = "dbo"):
        """Assert row exists (raises AssertionError if not)"""
        assert self.verify_row_exists(
            table, conditions, schema
        ), f"Expected row not found in {schema}.{table} with conditions: {conditions}"

    def assert_column_value(
        self,
        table: str,
        column: str,
        expected_value: Any,
        conditions: Dict[str, Any],
        schema: str = "dbo",
    ):
        """Assert column value (raises AssertionError if mismatch)"""
        assert self.verify_column_value(
            table, column, expected_value, conditions, schema
        ), f"Column {column} value mismatch in {schema}.{table}"


__all__ = ["DBValidator"]
