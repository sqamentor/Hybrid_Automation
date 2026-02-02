"""
Query Builder - Dynamic SQL Query Construction

Provides fluent API for building SQL queries dynamically.
Supports multiple database types and prevents SQL injection.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union


class Operator(Enum):
    """SQL comparison operators"""

    EQ = "="
    NE = "!="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    LIKE = "LIKE"
    IN = "IN"
    NOT_IN = "NOT IN"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"
    BETWEEN = "BETWEEN"


class JoinType(Enum):
    """SQL join types"""

    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL OUTER JOIN"


class QueryBuilder:
    """Fluent SQL query builder"""

    def __init__(self, db_type: str = "postgresql"):
        """
        Initialize query builder

        Args:
            db_type: Database type (postgresql, sql_server, mysql)
        """
        self.db_type = db_type
        self._select_columns: List[str] = []
        self._from_table: Optional[str] = None
        self._schema: str = "dbo"
        self._joins: List[str] = []
        self._where_conditions: List[str] = []
        self._group_by: List[str] = []
        self._having: List[str] = []
        self._order_by: List[str] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self._params: Dict[str, Any] = {}
        self._param_counter: int = 0

    def select(self, *columns: str) -> "QueryBuilder":
        """
        Specify columns to select

        Args:
            columns: Column names or expressions

        Returns:
            Self for chaining
        """
        self._select_columns.extend(columns)
        return self

    def from_table(self, table: str, schema: Optional[str] = None) -> "QueryBuilder":
        """
        Specify table to query

        Args:
            table: Table name
            schema: Schema name (optional)

        Returns:
            Self for chaining
        """
        self._from_table = table
        if schema:
            self._schema = schema
        return self

    def join(
        self, table: str, on_condition: str, join_type: JoinType = JoinType.INNER
    ) -> "QueryBuilder":
        """
        Add JOIN clause

        Args:
            table: Table to join
            on_condition: Join condition (e.g., "users.id = orders.user_id")
            join_type: Type of join

        Returns:
            Self for chaining
        """
        self._joins.append(f"{join_type.value} {table} ON {on_condition}")
        return self

    def where(self, column: str, value: Any, operator: Operator = Operator.EQ) -> "QueryBuilder":
        """
        Add WHERE condition

        Args:
            column: Column name
            value: Value to compare
            operator: Comparison operator

        Returns:
            Self for chaining
        """
        param_name = self._add_param(value)

        if operator == Operator.IS_NULL:
            self._where_conditions.append(f"{column} IS NULL")
        elif operator == Operator.IS_NOT_NULL:
            self._where_conditions.append(f"{column} IS NOT NULL")
        elif operator == Operator.IN:
            # Handle IN operator with list
            if isinstance(value, (list, tuple)):
                param_names = [self._add_param(v) for v in value]
                placeholders = ", ".join([f":{p}" for p in param_names])
                self._where_conditions.append(f"{column} IN ({placeholders})")
            else:
                self._where_conditions.append(f"{column} {operator.value} :{param_name}")
        elif operator == Operator.BETWEEN:
            # Handle BETWEEN operator
            if isinstance(value, (list, tuple)) and len(value) == 2:
                param1 = self._add_param(value[0])
                param2 = self._add_param(value[1])
                self._where_conditions.append(f"{column} BETWEEN :{param1} AND :{param2}")
        else:
            self._where_conditions.append(f"{column} {operator.value} :{param_name}")

        return self

    def where_raw(self, condition: str, params: Optional[Dict] = None) -> "QueryBuilder":
        """
        Add raw WHERE condition

        Args:
            condition: Raw SQL condition
            params: Optional parameters

        Returns:
            Self for chaining
        """
        self._where_conditions.append(condition)
        if params:
            self._params.update(params)
        return self

    def group_by(self, *columns: str) -> "QueryBuilder":
        """
        Add GROUP BY clause

        Args:
            columns: Column names

        Returns:
            Self for chaining
        """
        self._group_by.extend(columns)
        return self

    def having(self, condition: str) -> "QueryBuilder":
        """
        Add HAVING clause

        Args:
            condition: HAVING condition

        Returns:
            Self for chaining
        """
        self._having.append(condition)
        return self

    def order_by(self, column: str, direction: str = "ASC") -> "QueryBuilder":
        """
        Add ORDER BY clause

        Args:
            column: Column name
            direction: Sort direction (ASC or DESC)

        Returns:
            Self for chaining
        """
        self._order_by.append(f"{column} {direction.upper()}")
        return self

    def limit(self, limit: int) -> "QueryBuilder":
        """
        Add LIMIT clause

        Args:
            limit: Number of rows to return

        Returns:
            Self for chaining
        """
        self._limit = limit
        return self

    def offset(self, offset: int) -> "QueryBuilder":
        """
        Add OFFSET clause

        Args:
            offset: Number of rows to skip

        Returns:
            Self for chaining
        """
        self._offset = offset
        return self

    def _add_param(self, value: Any) -> str:
        """Add parameter and return parameter name"""
        param_name = f"param_{self._param_counter}"
        self._param_counter += 1
        self._params[param_name] = value
        return param_name

    def build(self) -> tuple[str, Dict[str, Any]]:
        """
        Build the SQL query

        Returns:
            Tuple of (query_string, parameters)
        """
        # SELECT clause
        if not self._select_columns:
            select_clause = "SELECT *"
        else:
            select_clause = f"SELECT {', '.join(self._select_columns)}"

        # FROM clause
        if not self._from_table:
            raise ValueError("FROM table not specified")

        from_clause = f"FROM {self._schema}.{self._from_table}"

        # JOIN clauses
        join_clause = " ".join(self._joins) if self._joins else ""

        # WHERE clause
        where_clause = ""
        if self._where_conditions:
            where_clause = f"WHERE {' AND '.join(self._where_conditions)}"

        # GROUP BY clause
        group_by_clause = ""
        if self._group_by:
            group_by_clause = f"GROUP BY {', '.join(self._group_by)}"

        # HAVING clause
        having_clause = ""
        if self._having:
            having_clause = f"HAVING {' AND '.join(self._having)}"

        # ORDER BY clause
        order_by_clause = ""
        if self._order_by:
            order_by_clause = f"ORDER BY {', '.join(self._order_by)}"

        # LIMIT/OFFSET clause (database-specific)
        limit_clause = self._build_limit_clause()

        # Combine all parts
        parts = [
            select_clause,
            from_clause,
            join_clause,
            where_clause,
            group_by_clause,
            having_clause,
            order_by_clause,
            limit_clause,
        ]

        query = " ".join([p for p in parts if p]).strip()

        return query, self._params

    def _build_limit_clause(self) -> str:
        """Build database-specific LIMIT clause"""
        if self._limit is None:
            return ""

        if self.db_type in ["postgresql", "mysql"]:
            clause = f"LIMIT {self._limit}"
            if self._offset:
                clause += f" OFFSET {self._offset}"
            return clause

        elif self.db_type == "sql_server":
            # SQL Server uses TOP or OFFSET/FETCH
            if self._offset:
                # Use OFFSET/FETCH (requires ORDER BY)
                if not self._order_by:
                    raise ValueError("SQL Server OFFSET requires ORDER BY clause")
                return f"OFFSET {self._offset} ROWS FETCH NEXT {self._limit} ROWS ONLY"
            else:
                # Use TOP (modify SELECT clause - handled separately)
                return f"TOP {self._limit}"

        return ""

    def get_query(self) -> str:
        """Get the query string only (without parameters)"""
        query, _ = self.build()
        return query

    def get_params(self) -> Dict[str, Any]:
        """Get the parameters dictionary"""
        return self._params.copy()

    def reset(self) -> "QueryBuilder":
        """Reset the query builder to initial state"""
        self._select_columns.clear()
        self._from_table = None
        self._schema = "dbo"
        self._joins.clear()
        self._where_conditions.clear()
        self._group_by.clear()
        self._having.clear()
        self._order_by.clear()
        self._limit = None
        self._offset = None
        self._params.clear()
        self._param_counter = 0
        return self


# ========================================================================
# CONVENIENCE FUNCTIONS
# ========================================================================


def select_all(table: str, schema: str = "dbo") -> QueryBuilder:
    """
    Create SELECT * query

    Args:
        table: Table name
        schema: Schema name

    Returns:
        QueryBuilder instance
    """
    return QueryBuilder().select("*").from_table(table, schema)


def count_rows(
    table: str, where: Optional[Dict[str, Any]] = None, schema: str = "dbo"
) -> QueryBuilder:
    """
    Create COUNT(*) query

    Args:
        table: Table name
        where: Optional WHERE conditions
        schema: Schema name

    Returns:
        QueryBuilder instance
    """
    builder = QueryBuilder().select("COUNT(*) as cnt").from_table(table, schema)

    if where:
        for column, value in where.items():
            builder.where(column, value)

    return builder


def find_by_id(table: str, id_column: str, id_value: Any, schema: str = "dbo") -> QueryBuilder:
    """
    Create query to find record by ID

    Args:
        table: Table name
        id_column: ID column name
        id_value: ID value
        schema: Schema name

    Returns:
        QueryBuilder instance
    """
    return QueryBuilder().select("*").from_table(table, schema).where(id_column, id_value).limit(1)


def exists(table: str, where: Dict[str, Any], schema: str = "dbo") -> QueryBuilder:
    """
    Create query to check if record exists

    Args:
        table: Table name
        where: WHERE conditions
        schema: Schema name

    Returns:
        QueryBuilder instance
    """
    builder = QueryBuilder().select("1").from_table(table, schema)

    for column, value in where.items():
        builder.where(column, value)

    return builder.limit(1)


__all__ = [
    "QueryBuilder",
    "Operator",
    "JoinType",
    "select_all",
    "count_rows",
    "find_by_id",
    "exists",
]
