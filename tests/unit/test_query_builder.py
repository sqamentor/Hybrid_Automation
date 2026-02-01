"""Unit Tests for Query Builder.

Tests the QueryBuilder functionality.
"""

import pytest

from framework.database.query_builder import (
    JoinType,
    Operator,
    QueryBuilder,
    count_rows,
    exists,
    find_by_id,
    select_all,
)


@pytest.mark.modern_spa
@pytest.mark.unit
class TestQueryBuilder:
    """Test QueryBuilder class."""
    
    def test_simple_select(self):
        """Test basic SELECT query."""
        builder = QueryBuilder()
        query, params = builder.select("*").from_table("users").build()
        
        assert "SELECT *" in query
        assert "FROM dbo.users" in query
        assert params == {}
    
    def test_select_specific_columns(self):
        """Test SELECT with specific columns."""
        builder = QueryBuilder()
        query, params = builder.select("id", "name", "email").from_table("users").build()
        
        assert "SELECT id, name, email" in query
        assert "FROM dbo.users" in query
    
    def test_where_equals(self):
        """Test WHERE with equals operator."""
        builder = QueryBuilder()
        query, params = builder.select("*").from_table("users").where("id", 123).build()
        
        assert "WHERE id = :param_0" in query
        assert params["param_0"] == 123
    
    def test_where_operators(self):
        """Test different WHERE operators."""
        # Greater than
        builder = QueryBuilder()
        query, params = builder.select("*").from_table("orders").where("total", 100, Operator.GT).build()
        assert "total > :param_0" in query
        assert params["param_0"] == 100
        
        # LIKE
        builder = QueryBuilder()
        query, params = builder.select("*").from_table("users").where("email", "%@test.com", Operator.LIKE).build()
        assert "email LIKE :param_0" in query
    
    def test_where_in(self):
        """Test WHERE IN operator."""
        builder = QueryBuilder()
        query, params = builder.select("*").from_table("users").where("id", [1, 2, 3], Operator.IN).build()
        
        assert "id IN" in query
        # The implementation expands IN values to separate params
        assert params["param_1"] == 1
        assert params["param_2"] == 2
        assert params["param_3"] == 3
    
    def test_where_between(self):
        """Test WHERE BETWEEN operator."""
        builder = QueryBuilder()
        query, params = builder.select("*").from_table("orders").where("created_at", ["2024-01-01", "2024-12-31"], Operator.BETWEEN).build()
        
        assert "created_at BETWEEN" in query
        # The implementation expands BETWEEN values to separate params
        assert params["param_1"] == "2024-01-01"
        assert params["param_2"] == "2024-12-31"
    
    def test_multiple_where(self):
        """Test multiple WHERE conditions."""
        builder = QueryBuilder()
        query, params = (
            builder.select("*")
            .from_table("orders")
            .where("status", "completed")
            .where("total", 100, Operator.GT)
            .build()
        )
        
        assert "status = :param_0 AND total > :param_1" in query
        assert params["param_0"] == "completed"
        assert params["param_1"] == 100
    
    def test_join(self):
        """Test JOIN clause."""
        builder = QueryBuilder()
        query, params = (
            builder.select("users.name", "orders.total")
            .from_table("users")
            .join("orders", "users.id = orders.user_id")
            .build()
        )
        
        assert "INNER JOIN orders ON users.id = orders.user_id" in query
    
    def test_left_join(self):
        """Test LEFT JOIN."""
        builder = QueryBuilder()
        query, params = (
            builder.select("*")
            .from_table("users")
            .join("orders", "users.id = orders.user_id", JoinType.LEFT)
            .build()
        )
        
        assert "LEFT JOIN orders ON users.id = orders.user_id" in query
    
    def test_group_by(self):
        """Test GROUP BY clause."""
        builder = QueryBuilder()
        query, params = (
            builder.select("status", "COUNT(*) as cnt")
            .from_table("orders")
            .group_by("status")
            .build()
        )
        
        assert "GROUP BY status" in query
    
    def test_order_by(self):
        """Test ORDER BY clause."""
        builder = QueryBuilder()
        query, params = (
            builder.select("*")
            .from_table("users")
            .order_by("created_at", "DESC")
            .build()
        )
        
        assert "ORDER BY created_at DESC" in query
    
    def test_limit(self):
        """Test LIMIT clause."""
        builder = QueryBuilder()
        query, params = (
            builder.select("*")
            .from_table("users")
            .limit(10)
            .build()
        )
        
        assert "LIMIT 10" in query
    
    def test_offset(self):
        """Test OFFSET clause."""
        builder = QueryBuilder()
        query, params = (
            builder.select("*")
            .from_table("users")
            .limit(10)
            .offset(20)
            .build()
        )
        
        assert "LIMIT 10 OFFSET 20" in query
    
    def test_complex_query(self):
        """Test complex query with multiple clauses."""
        builder = QueryBuilder()
        query, params = (
            builder.select("users.name", "COUNT(orders.id) as order_count")
            .from_table("users")
            .join("orders", "users.id = orders.user_id", JoinType.LEFT)
            .where("users.status", "active")
            .group_by("users.id", "users.name")
            .having("COUNT(orders.id) > 5")
            .order_by("order_count", "DESC")
            .limit(10)
            .build()
        )
        
        assert "SELECT users.name, COUNT(orders.id) as order_count" in query
        assert "FROM dbo.users" in query
        assert "LEFT JOIN orders" in query
        assert "WHERE users.status = :param_0" in query
        assert "GROUP BY users.id, users.name" in query
        assert "HAVING COUNT(orders.id) > 5" in query
        assert "ORDER BY order_count DESC" in query
        assert "LIMIT 10" in query


@pytest.mark.modern_spa
@pytest.mark.unit
class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_select_all(self):
        """Test select_all function."""
        builder = select_all("users")
        query, params = builder.build()
        
        assert "SELECT *" in query
        assert "FROM dbo.users" in query
    
    def test_count_rows(self):
        """Test count_rows function."""
        builder = count_rows("users", where={"status": "active"})
        query, params = builder.build()
        
        assert "SELECT COUNT(*) as cnt" in query
        assert "WHERE status = :param_0" in query
        assert params["param_0"] == "active"
    
    def test_find_by_id(self):
        """Test find_by_id function."""
        builder = find_by_id("users", "id", 123)
        query, params = builder.build()
        
        assert "SELECT *" in query
        assert "WHERE id = :param_0" in query
        assert "LIMIT 1" in query
        assert params["param_0"] == 123
    
    def test_exists(self):
        """Test exists function."""
        builder = exists("users", {"email": "test@example.com"})
        query, params = builder.build()
        
        assert "SELECT 1" in query
        assert "WHERE email = :param_0" in query
        assert "LIMIT 1" in query


@pytest.mark.modern_spa
@pytest.mark.unit
class TestQueryBuilderReset:
    """Test QueryBuilder reset functionality."""
    
    def test_reset(self):
        """Test reset clears all state."""
        builder = QueryBuilder()
        builder.select("*").from_table("users").where("id", 123).limit(10)
        
        # Build first query
        query1, params1 = builder.build()
        assert "WHERE id = :param_0" in query1
        
        # Reset and build new query
        builder.reset()
        query2, params2 = builder.select("name").from_table("orders").build()
        
        assert "SELECT name" in query2
        assert "FROM dbo.orders" in query2
        assert "WHERE" not in query2
        assert "LIMIT" not in query2
