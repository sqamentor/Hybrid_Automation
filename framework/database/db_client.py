"""
Database Client - Universal Database Connection Manager

Provides read-only database access with support for multiple database types.
Includes comprehensive audit logging for compliance.
"""

import time
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config.settings import get_database_config
from utils.logger import get_audit_logger, get_logger

logger = get_logger(__name__)
audit_logger = get_audit_logger()


class DBClient:
    """Universal database client (read-only) with audit trail"""
    
    def __init__(self, db_name: str = 'primary', env: Optional[str] = None):
        self.config = get_database_config(env, db_name)
        self.engine: Optional[Engine] = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        connection_string = self._build_connection_string()
        self.engine = create_engine(connection_string, pool_pre_ping=True)
        logger.info(f"Connected to database: {self.config.name}")
        
        # Audit log connection
        audit_logger.log_action("db_connect", {
            "database": self.config.name,
            "host": self.config.host,
            "port": self.config.port
        })
    
    def _build_connection_string(self) -> str:
        """Build SQLAlchemy connection string"""
        if self.config.type == "sql_server":
            return (
                f"mssql+pyodbc://{self.config.username}:{self.config.password}"
                f"@{self.config.host}:{self.config.port}/{self.config.name}"
                f"?driver=ODBC+Driver+17+for+SQL+Server"
            )
        
        elif self.config.type == "postgresql":
            return (
                f"postgresql+psycopg2://{self.config.username}:{self.config.password}"
                f"@{self.config.host}:{self.config.port}/{self.config.name}"
            )
        
        elif self.config.type == "mysql":
            return (
                f"mysql+pymysql://{self.config.username}:{self.config.password}"
                f"@{self.config.host}:{self.config.port}/{self.config.name}"
            )
        
        else:
            raise ValueError(f"Unsupported database type: {self.config.type}")
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Execute SELECT query (read-only enforced)
        
        Args:
            query: SQL query (SELECT only)
            params: Query parameters
        
        Returns:
            List of result rows as dictionaries
        """
        # Enforce read-only
        if not self._is_read_only_query(query):
            error_msg = f"Only SELECT queries are allowed. Query: {query[:100]}"
            logger.error(error_msg)
            audit_logger.log_error(
                error_type="db_query_blocked",
                error_message=error_msg
            )
            raise ValueError("Only SELECT queries are allowed")
        
        logger.debug(f"Executing query: {query[:100]}...")
        start_time = time.time()
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                columns = result.keys()
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
                
                duration_ms = (time.time() - start_time) * 1000
                logger.debug(f"Query returned {len(rows)} rows in {duration_ms:.2f}ms")
                
                # Audit log query execution
                audit_logger.log_db_operation(
                    operation="SELECT",
                    table=self._extract_table_name(query),
                    query=query[:500],  # First 500 chars
                    rows_affected=len(rows),
                    duration_ms=duration_ms
                )
                
                return rows
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Query execution failed: {str(e)}")
            
            # Audit log failure
            audit_logger.log_error(
                error_type="db_query_failed",
                error_message=f"Query failed: {str(e)}",
                stack_trace=query[:500]
            )
            raise
    
    def execute_scalar(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute query and return single value"""
        results = self.execute_query(query, params)
        if results and len(results) > 0:
            return list(results[0].values())[0]
        return None
    
    def _is_read_only_query(self, query: str) -> bool:
        """Verify query is read-only"""
        query_upper = query.strip().upper()
        
        # Blocked keywords
        blocked = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE', 'ALTER', 'CREATE']
        for keyword in blocked:
            if keyword in query_upper:
                logger.error(f"Blocked keyword detected: {keyword}")
                return False
        
        # Must start with SELECT or WITH (for CTEs)
        if not (query_upper.startswith('SELECT') or query_upper.startswith('WITH')):
            return False
        
        return True
    
    def _extract_table_name(self, query: str) -> str:
        """Extract table name from query for audit logging"""
        try:
            query_upper = query.upper()
            if 'FROM' in query_upper:
                from_index = query_upper.index('FROM') + 5
                after_from = query[from_index:].strip()
                table_name = after_from.split()[0].strip('`"\'\\"')
                return table_name
        except:
            pass
        return "unknown"
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
            
            # Audit log disconnection
            audit_logger.log_action("db_disconnect", {
                "database": self.config.name
            })


__all__ = ['DBClient']
