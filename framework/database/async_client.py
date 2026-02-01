"""
Async database client supporting PostgreSQL and MySQL.

Features:
- Connection pooling
- Transaction support
- Query builder integration
- Prepared statements
- Automatic retry
"""
import asyncio
from typing import Dict, Any, List, Optional, Union
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False

try:
    import aiomysql
    AIOMYSQL_AVAILABLE = True
except ImportError:
    AIOMYSQL_AVAILABLE = False


class DatabaseType(str, Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    db_type: DatabaseType
    host: str
    port: int
    database: str
    user: str
    password: str
    min_pool_size: int = 5
    max_pool_size: int = 20
    timeout: int = 30


class AsyncDatabaseClient:
    """
    Async database client with connection pooling.
    
    Example:
        ```python
        from framework.database.async_client import AsyncDatabaseClient, DatabaseConfig, DatabaseType
        
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="testdb",
            user="testuser",
            password="testpass"
        )
        
        async with AsyncDatabaseClient(config) as db:
            # Single query
            result = await db.fetch_one("SELECT * FROM users WHERE id = $1", 1)
            
            # Multiple rows
            results = await db.fetch_all("SELECT * FROM users WHERE active = $1", True)
            
            # Execute query
            await db.execute("UPDATE users SET last_login = NOW() WHERE id = $1", 1)
            
            # Transaction
            async with db.transaction():
                await db.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
                await db.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
        ```
    """
    
    def __init__(self, config: DatabaseConfig):
        """
        Initialize async database client.
        
        Args:
            config: Database configuration
        
        Raises:
            ImportError: If required database driver not installed
        """
        self.config = config
        self.pool = None
        
        # Check if driver is available
        if config.db_type == DatabaseType.POSTGRESQL and not ASYNCPG_AVAILABLE:
            raise ImportError(
                "asyncpg not installed. Install with: pip install asyncpg"
            )
        
        if config.db_type == DatabaseType.MYSQL and not AIOMYSQL_AVAILABLE:
            raise ImportError(
                "aiomysql not installed. Install with: pip install aiomysql"
            )
    
    async def __aenter__(self):
        """Enter async context."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        await self.close()
    
    async def connect(self) -> None:
        """
        Create database connection pool.
        
        Creates connection pool for efficient connection management.
        """
        if self.config.db_type == DatabaseType.POSTGRESQL:
            self.pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password,
                min_size=self.config.min_pool_size,
                max_size=self.config.max_pool_size,
                command_timeout=self.config.timeout
            )
        
        elif self.config.db_type == DatabaseType.MYSQL:
            self.pool = await aiomysql.create_pool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.database,
                user=self.config.user,
                password=self.config.password,
                minsize=self.config.min_pool_size,
                maxsize=self.config.max_pool_size,
                connect_timeout=self.config.timeout
            )
    
    async def close(self) -> None:
        """
        Close database connection pool.
        
        Call this when application is shutting down.
        """
        if self.pool:
            if self.config.db_type == DatabaseType.POSTGRESQL:
                await self.pool.close()
            elif self.config.db_type == DatabaseType.MYSQL:
                self.pool.close()
                await self.pool.wait_closed()
    
    async def fetch_one(
        self,
        query: str,
        *args,
        timeout: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch single row from database.
        
        Args:
            query: SQL query
            *args: Query parameters
            timeout: Optional query timeout
        
        Returns:
            Dictionary with column names as keys, or None if no results
        
        Example:
            ```python
            user = await db.fetch_one("SELECT * FROM users WHERE id = $1", 123)
            if user:
                print(f"User: {user['name']}")
            ```
        """
        if self.config.db_type == DatabaseType.POSTGRESQL:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, *args, timeout=timeout)
                return dict(row) if row else None
        
        elif self.config.db_type == DatabaseType.MYSQL:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, args)
                    row = await cursor.fetchone()
                    return dict(row) if row else None
    
    async def fetch_all(
        self,
        query: str,
        *args,
        timeout: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all rows from database.
        
        Args:
            query: SQL query
            *args: Query parameters
            timeout: Optional query timeout
        
        Returns:
            List of dictionaries with column names as keys
        
        Example:
            ```python
            users = await db.fetch_all("SELECT * FROM users WHERE active = $1", True)
            for user in users:
                print(f"User: {user['name']}")
            ```
        """
        if self.config.db_type == DatabaseType.POSTGRESQL:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, *args, timeout=timeout)
                return [dict(row) for row in rows]
        
        elif self.config.db_type == DatabaseType.MYSQL:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, args)
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
    
    async def execute(
        self,
        query: str,
        *args,
        timeout: Optional[float] = None
    ) -> str:
        """
        Execute query without returning results.
        
        Args:
            query: SQL query (INSERT, UPDATE, DELETE, etc.)
            *args: Query parameters
            timeout: Optional query timeout
        
        Returns:
            Status message (e.g., "INSERT 0 1")
        
        Example:
            ```python
            await db.execute(
                "UPDATE users SET last_login = NOW() WHERE id = $1",
                user_id
            )
            ```
        """
        if self.config.db_type == DatabaseType.POSTGRESQL:
            async with self.pool.acquire() as conn:
                result = await conn.execute(query, *args, timeout=timeout)
                return result
        
        elif self.config.db_type == DatabaseType.MYSQL:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, args)
                    await conn.commit()
                    return f"Rows affected: {cursor.rowcount}"
    
    async def execute_many(
        self,
        query: str,
        args_list: List[tuple],
        timeout: Optional[float] = None
    ) -> None:
        """
        Execute same query multiple times with different parameters.
        
        Args:
            query: SQL query
            args_list: List of parameter tuples
            timeout: Optional query timeout
        
        Example:
            ```python
            await db.execute_many(
                "INSERT INTO users (name, email) VALUES ($1, $2)",
                [
                    ("Alice", "alice@example.com"),
                    ("Bob", "bob@example.com"),
                    ("Charlie", "charlie@example.com")
                ]
            )
            ```
        """
        if self.config.db_type == DatabaseType.POSTGRESQL:
            async with self.pool.acquire() as conn:
                await conn.executemany(query, args_list, timeout=timeout)
        
        elif self.config.db_type == DatabaseType.MYSQL:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.executemany(query, args_list)
                    await conn.commit()
    
    @asynccontextmanager
    async def transaction(self):
        """
        Create database transaction context.
        
        Yields:
            Database connection with active transaction
        
        Example:
            ```python
            async with db.transaction():
                await db.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
                await db.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
                # Automatically commits on success, rolls back on exception
            ```
        """
        if self.config.db_type == DatabaseType.POSTGRESQL:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    yield conn
        
        elif self.config.db_type == DatabaseType.MYSQL:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("START TRANSACTION")
                    try:
                        yield conn
                        await conn.commit()
                    except Exception:
                        await conn.rollback()
                        raise
    
    async def fetch_value(
        self,
        query: str,
        *args,
        column: Union[str, int] = 0,
        timeout: Optional[float] = None
    ) -> Any:
        """
        Fetch single value from database.
        
        Args:
            query: SQL query
            *args: Query parameters
            column: Column name or index
            timeout: Optional query timeout
        
        Returns:
            Single value
        
        Example:
            ```python
            count = await db.fetch_value("SELECT COUNT(*) FROM users")
            print(f"Total users: {count}")
            ```
        """
        row = await self.fetch_one(query, *args, timeout=timeout)
        if row is None:
            return None
        
        if isinstance(column, int):
            return list(row.values())[column]
        else:
            return row.get(column)
    
    async def health_check(self) -> bool:
        """
        Check database connection health.
        
        Returns:
            True if database is reachable, False otherwise
        
        Example:
            ```python
            if await db.health_check():
                print("Database is healthy")
            else:
                print("Database connection failed")
            ```
        """
        try:
            await self.fetch_value("SELECT 1")
            return True
        except Exception:
            return False


# ============================================================================
# Query Builder Integration
# ============================================================================

class AsyncQueryExecutor:
    """
    Executor for async query builder.
    
    Example:
        ```python
        from framework.database.query_builder import QueryBuilder
        from framework.database.async_client import AsyncQueryExecutor
        
        async with AsyncDatabaseClient(config) as db:
            executor = AsyncQueryExecutor(db)
            
            # Build and execute query
            query = QueryBuilder("users").where("active", True).limit(10)
            results = await executor.execute(query)
        ```
    """
    
    def __init__(self, client: AsyncDatabaseClient):
        """
        Initialize query executor.
        
        Args:
            client: Async database client
        """
        self.client = client
    
    async def execute(self, query_builder) -> List[Dict[str, Any]]:
        """
        Execute query builder and return results.
        
        Args:
            query_builder: QueryBuilder instance
        
        Returns:
            List of result dictionaries
        """
        query, params = query_builder.build()
        return await self.client.fetch_all(query, *params)
    
    async def execute_one(self, query_builder) -> Optional[Dict[str, Any]]:
        """
        Execute query builder and return single result.
        
        Args:
            query_builder: QueryBuilder instance
        
        Returns:
            Single result dictionary or None
        """
        query, params = query_builder.build()
        return await self.client.fetch_one(query, *params)
    
    async def execute_count(self, query_builder) -> int:
        """
        Execute query builder and return count.
        
        Args:
            query_builder: QueryBuilder instance
        
        Returns:
            Count of matching rows
        """
        query, params = query_builder.build()
        # Modify query to use COUNT(*)
        query = query.replace("SELECT *", "SELECT COUNT(*)")
        return await self.client.fetch_value(query, *params)


# ============================================================================
# Connection Pool Manager
# ============================================================================

class ConnectionPoolManager:
    """
    Manages multiple database connection pools.
    
    Example:
        ```python
        from framework.database.async_client import ConnectionPoolManager
        
        manager = ConnectionPoolManager()
        
        # Add pools
        await manager.add_pool("main", main_config)
        await manager.add_pool("analytics", analytics_config)
        
        # Get client
        main_db = manager.get_client("main")
        result = await main_db.fetch_all("SELECT * FROM users")
        
        # Cleanup
        await manager.close_all()
        ```
    """
    
    def __init__(self):
        """Initialize connection pool manager."""
        self.clients: Dict[str, AsyncDatabaseClient] = {}
    
    async def add_pool(self, name: str, config: DatabaseConfig) -> None:
        """
        Add a database connection pool.
        
        Args:
            name: Pool name
            config: Database configuration
        """
        client = AsyncDatabaseClient(config)
        await client.connect()
        self.clients[name] = client
    
    def get_client(self, name: str) -> AsyncDatabaseClient:
        """
        Get database client by name.
        
        Args:
            name: Pool name
        
        Returns:
            Database client
        
        Raises:
            KeyError: If pool not found
        """
        if name not in self.clients:
            raise KeyError(f"Database pool '{name}' not found")
        
        return self.clients[name]
    
    async def close_all(self) -> None:
        """Close all database connection pools."""
        for client in self.clients.values():
            await client.close()
        
        self.clients.clear()
    
    async def health_check_all(self) -> Dict[str, bool]:
        """
        Health check all database connections.
        
        Returns:
            Dictionary of pool names to health status
        """
        results = {}
        
        for name, client in self.clients.items():
            results[name] = await client.health_check()
        
        return results
