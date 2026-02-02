"""
GraphQL Testing Support - Schema Validation & Query Testing

Provides comprehensive GraphQL API testing with schema introspection,
query validation, and response assertions.
"""

import json
from typing import Any, Dict, List, Optional

import requests

from utils.logger import get_logger

logger = get_logger(__name__)


class GraphQLClient:
    """GraphQL API testing client"""

    def __init__(self, endpoint: str, headers: Optional[Dict] = None):
        """
        Initialize GraphQL client

        Args:
            endpoint: GraphQL endpoint URL
            headers: Optional HTTP headers (e.g., authorization)
        """
        self.endpoint = endpoint
        self.headers = headers or {}
        self.headers.setdefault("Content-Type", "application/json")
        self.schema: Optional[Dict] = None

    def query(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute GraphQL query

        Args:
            query: GraphQL query string
            variables: Optional query variables

        Returns:
            Response data
        """
        payload = {"query": query, "variables": variables or {}}

        logger.info(f"Executing GraphQL query: {query[:100]}...")

        response = requests.post(self.endpoint, json=payload, headers=self.headers)

        response.raise_for_status()
        result = response.json()

        # Check for GraphQL errors
        if "errors" in result:
            logger.error(f"GraphQL errors: {result['errors']}")
            raise GraphQLError(result["errors"])

        return result.get("data", {})

    def mutate(self, mutation: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute GraphQL mutation

        Args:
            mutation: GraphQL mutation string
            variables: Optional mutation variables

        Returns:
            Mutation result
        """
        return self.query(mutation, variables)

    def introspect_schema(self) -> Dict:
        """
        Introspect GraphQL schema

        Returns:
            Schema definition
        """
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                queryType { name }
                mutationType { name }
                subscriptionType { name }
                types {
                    ...FullType
                }
                directives {
                    name
                    description
                    locations
                    args {
                        ...InputValue
                    }
                }
            }
        }
        
        fragment FullType on __Type {
            kind
            name
            description
            fields(includeDeprecated: true) {
                name
                description
                args {
                    ...InputValue
                }
                type {
                    ...TypeRef
                }
                isDeprecated
                deprecationReason
            }
            inputFields {
                ...InputValue
            }
            interfaces {
                ...TypeRef
            }
            enumValues(includeDeprecated: true) {
                name
                description
                isDeprecated
                deprecationReason
            }
            possibleTypes {
                ...TypeRef
            }
        }
        
        fragment InputValue on __InputValue {
            name
            description
            type { ...TypeRef }
            defaultValue
        }
        
        fragment TypeRef on __Type {
            kind
            name
            ofType {
                kind
                name
                ofType {
                    kind
                    name
                    ofType {
                        kind
                        name
                    }
                }
            }
        }
        """

        self.schema = self.query(introspection_query)
        logger.info("Schema introspected successfully")
        return self.schema

    def get_queries(self) -> List[str]:
        """Get available queries from schema"""
        if not self.schema:
            self.introspect_schema()

        query_type = next(
            (
                t
                for t in self.schema["__schema"]["types"]
                if t["name"] == self.schema["__schema"]["queryType"]["name"]
            ),
            None,
        )

        if query_type and query_type.get("fields"):
            return [field["name"] for field in query_type["fields"]]

        return []

    def get_mutations(self) -> List[str]:
        """Get available mutations from schema"""
        if not self.schema:
            self.introspect_schema()

        mutation_type_name = self.schema["__schema"].get("mutationType", {}).get("name")
        if not mutation_type_name:
            return []

        mutation_type = next(
            (t for t in self.schema["__schema"]["types"] if t["name"] == mutation_type_name), None
        )

        if mutation_type and mutation_type.get("fields"):
            return [field["name"] for field in mutation_type["fields"]]

        return []

    def validate_query(self, query: str) -> bool:
        """
        Validate GraphQL query syntax

        Args:
            query: Query string

        Returns:
            True if valid
        """
        try:
            # Basic validation - check for balanced braces
            if query.count("{") != query.count("}"):
                raise ValueError("Unbalanced braces")

            # Try to execute query (will fail fast if invalid)
            payload = {"query": query}
            response = requests.post(self.endpoint, json=payload, headers=self.headers)

            result = response.json()

            # Check for syntax errors
            if "errors" in result:
                errors = result["errors"]
                syntax_errors = [e for e in errors if "Syntax Error" in e.get("message", "")]
                if syntax_errors:
                    logger.error(f"Query validation failed: {syntax_errors}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Query validation error: {e}")
            return False

    def assert_response_has_field(self, response: Dict, field_path: str):
        """
        Assert response contains field at path

        Args:
            response: GraphQL response
            field_path: Dot-separated field path (e.g., 'user.email')
        """
        parts = field_path.split(".")
        current = response

        for part in parts:
            if not isinstance(current, dict) or part not in current:
                raise AssertionError(f"Field '{field_path}' not found in response")
            current = current[part]

        logger.info(f"✓ Field '{field_path}' found in response")

    def assert_field_type(self, response: Dict, field_path: str, expected_type: type):
        """
        Assert field has expected type

        Args:
            response: GraphQL response
            field_path: Dot-separated field path
            expected_type: Expected Python type
        """
        self.assert_response_has_field(response, field_path)

        parts = field_path.split(".")
        current = response
        for part in parts:
            current = current[part]

        if not isinstance(current, expected_type):
            raise AssertionError(
                f"Field '{field_path}' has type {type(current).__name__}, "
                f"expected {expected_type.__name__}"
            )

        logger.info(f"✓ Field '{field_path}' has correct type: {expected_type.__name__}")

    def assert_no_errors(self, response: Dict):
        """Assert GraphQL response has no errors"""
        if "errors" in response:
            raise AssertionError(f"GraphQL errors found: {response['errors']}")

        logger.info("✓ No GraphQL errors in response")


class GraphQLError(Exception):
    """GraphQL error exception"""

    def __init__(self, errors: List[Dict]):
        self.errors = errors
        messages = [e.get("message", "Unknown error") for e in errors]
        super().__init__(f"GraphQL errors: {', '.join(messages)}")


class GraphQLQueryBuilder:
    """Fluent GraphQL query builder"""

    def __init__(self, operation: str = "query"):
        """
        Initialize query builder

        Args:
            operation: 'query' or 'mutation'
        """
        self.operation = operation
        self.name: Optional[str] = None
        self.variables: Dict[str, str] = {}
        self.fields: List[str] = []

    def with_name(self, name: str) -> "GraphQLQueryBuilder":
        """Set operation name"""
        self.name = name
        return self

    def with_variable(self, name: str, var_type: str) -> "GraphQLQueryBuilder":
        """
        Add variable definition

        Args:
            name: Variable name (without $)
            var_type: Variable type (e.g., 'String!', 'Int')
        """
        self.variables[name] = var_type
        return self

    def select(self, *fields: str) -> "GraphQLQueryBuilder":
        """
        Select fields

        Args:
            fields: Field names or nested selections
        """
        self.fields.extend(fields)
        return self

    def build(self) -> str:
        """Build GraphQL query string"""
        # Operation line
        query_parts = [self.operation]

        if self.name:
            query_parts.append(f" {self.name}")

        # Variables
        if self.variables:
            var_defs = [f"${name}: {var_type}" for name, var_type in self.variables.items()]
            query_parts.append(f"({', '.join(var_defs)})")

        query_parts.append(" {\n")

        # Fields
        for field in self.fields:
            query_parts.append(f"  {field}\n")

        query_parts.append("}")

        return "".join(query_parts)


# ========================================================================
# CONVENIENCE FUNCTIONS
# ========================================================================


def build_query(name: str, fields: List[str], variables: Optional[Dict[str, str]] = None) -> str:
    """
    Build a simple GraphQL query

    Args:
        name: Query name
        fields: List of fields to select
        variables: Optional variable definitions

    Returns:
        GraphQL query string
    """
    builder = GraphQLQueryBuilder("query").with_name(name)

    if variables:
        for var_name, var_type in variables.items():
            builder.with_variable(var_name, var_type)

    builder.select(*fields)

    return builder.build()


def build_mutation(name: str, fields: List[str], variables: Optional[Dict[str, str]] = None) -> str:
    """
    Build a simple GraphQL mutation

    Args:
        name: Mutation name
        fields: List of fields to return
        variables: Optional variable definitions

    Returns:
        GraphQL mutation string
    """
    builder = GraphQLQueryBuilder("mutation").with_name(name)

    if variables:
        for var_name, var_type in variables.items():
            builder.with_variable(var_name, var_type)

    builder.select(*fields)

    return builder.build()


__all__ = ["GraphQLClient", "GraphQLError", "GraphQLQueryBuilder", "build_query", "build_mutation"]
