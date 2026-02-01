"""
AI-Driven API → DB Validation Suggester

This module uses AI to analyze API responses and suggest appropriate database validations.
It learns from API → DB mappings and generates intelligent validation queries.
"""

import json
import os
import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationSuggestion:
    """AI-suggested database validation"""
    query: str
    reason: str
    priority: str  # 'critical', 'high', 'medium', 'low'
    expected_result: Dict[str, Any]
    correlation_keys: List[str]
    confidence: int  # 0-100
    pattern_type: str = "generic"  # Pattern category
    complexity: str = "simple"  # simple, moderate, complex
    estimated_execution_time: float = 0.1  # seconds
    tags: List[str] = field(default_factory=list)  # Categorization tags


@dataclass
class ValidationStrategy:
    """Complete validation strategy for an API endpoint"""
    endpoint: str
    method: str
    suggestions: List[ValidationSuggestion]
    correlation_context: Dict[str, Any]
    ai_reasoning: str
    cache_hit: bool = False
    cache_key: Optional[str] = None


class ValidationPatternCache:
    """Cache for common API validation patterns"""
    
    def __init__(self, ttl_seconds: int = 3600, max_size: int = 100):
        """
        Initialize pattern cache
        
        Args:
            ttl_seconds: Time-to-live for cached entries (default: 1 hour)
            max_size: Maximum cache size (default: 100 patterns)
        """
        self.cache: Dict[str, Tuple[ValidationStrategy, float]] = {}
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        self.pattern_frequency: Dict[str, int] = defaultdict(int)
        logger.info(f"Initialized validation cache (TTL={ttl_seconds}s, max_size={max_size})")
    
    def generate_cache_key(self, endpoint: str, method: str, response_structure: Dict) -> str:
        """
        Generate cache key based on endpoint, method, and response structure
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            response_structure: Structure of response (keys only, no values)
        """
        # Normalize endpoint (remove IDs)
        normalized_endpoint = self._normalize_endpoint(endpoint)
        
        # Get response schema (keys only)
        response_keys = sorted(self._extract_keys(response_structure))
        
        # Create composite key
        key_data = f"{method}:{normalized_endpoint}:{':'.join(response_keys)}"
        cache_key = hashlib.md5(key_data.encode()).hexdigest()
        
        return cache_key
    
    def _normalize_endpoint(self, endpoint: str) -> str:
        """Normalize endpoint by replacing IDs with placeholders"""
        import re
        # Replace numeric IDs
        normalized = re.sub(r'/\d+', '/{id}', endpoint)
        # Replace UUID patterns
        normalized = re.sub(r'/[a-f0-9\-]{36}', '/{uuid}', normalized)
        # Replace other ID-like patterns
        normalized = re.sub(r'/[a-zA-Z0-9]{20,}', '/{token}', normalized)
        return normalized
    
    def _extract_keys(self, data: Any, prefix: str = "") -> List[str]:
        """Recursively extract all keys from nested structure"""
        keys = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                keys.append(full_key)
                if isinstance(value, (dict, list)):
                    keys.extend(self._extract_keys(value, full_key))
        elif isinstance(data, list) and data:
            keys.extend(self._extract_keys(data[0], f"{prefix}[]"))
        
        return keys
    
    def get(self, cache_key: str) -> Optional[ValidationStrategy]:
        """Get cached strategy if available and not expired"""
        if cache_key in self.cache:
            strategy, timestamp = self.cache[cache_key]
            
            # Check if expired
            if time.time() - timestamp < self.ttl_seconds:
                self.hits += 1
                self.pattern_frequency[cache_key] += 1
                logger.info(f"Cache HIT for key {cache_key[:8]}...")
                
                # Mark as cache hit
                strategy.cache_hit = True
                strategy.cache_key = cache_key
                return strategy
            else:
                # Expired, remove from cache
                del self.cache[cache_key]
                logger.debug(f"Cache entry expired: {cache_key[:8]}...")
        
        self.misses += 1
        logger.debug(f"Cache MISS for key {cache_key[:8]}...")
        return None
    
    def put(self, cache_key: str, strategy: ValidationStrategy):
        """Store strategy in cache"""
        # Enforce max size (LRU eviction)
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
            logger.debug(f"Cache eviction: {oldest_key[:8]}...")
        
        self.cache[cache_key] = (strategy, time.time())
        logger.info(f"Cached strategy for key {cache_key[:8]}...")
    
    def clear(self):
        """Clear all cached entries"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        self.pattern_frequency.clear()
        logger.info("Validation cache cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        # Top patterns
        top_patterns = sorted(
            self.pattern_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2),
            "ttl_seconds": self.ttl_seconds,
            "top_patterns": [
                {"key": key[:8], "frequency": freq}
                for key, freq in top_patterns
            ]
        }


class AIValidationSuggester:
    """AI-powered API → DB validation suggester"""
    
    def __init__(self, provider_name: Optional[str] = None, enable_cache: bool = True):
        """
        Initialize AI Validation Suggester
        
        Args:
            provider_name: AI provider to use ('openai', 'claude', 'azure', 'ollama')
                          If None, uses default from configuration
            enable_cache: Enable pattern caching (default: True)
        """
        self.provider_name = provider_name
        self.enabled = False
        self.ai_provider = None
        self.api_db_mappings = settings.get_api_db_mapping()
        
        # Initialize cache
        self.cache_enabled = enable_cache
        self.cache = ValidationPatternCache(ttl_seconds=3600, max_size=100) if enable_cache else None
        
        # Enhanced validation patterns
        self.validation_patterns = self._initialize_validation_patterns()
        
        self._initialize_client()
    
    def _initialize_validation_patterns(self) -> Dict[str, List[Dict]]:
        """Initialize comprehensive validation patterns"""
        return {
            # CRUD Operation Patterns
            "CREATE": [
                {
                    "name": "record_existence",
                    "query": "SELECT COUNT(*) as cnt FROM {table} WHERE {primary_key} = '{key_value}'",
                    "reason": "Verify record was created",
                    "priority": "critical",
                    "confidence_base": 95,
                    "tags": ["crud", "create", "existence"]
                },
                {
                    "name": "column_values",
                    "query": "SELECT * FROM {table} WHERE {primary_key} = '{key_value}'",
                    "reason": "Verify all column values match request",
                    "priority": "high",
                    "confidence_base": 90,
                    "tags": ["crud", "create", "data_integrity"]
                },
                {
                    "name": "audit_trail",
                    "query": "SELECT * FROM audit_log WHERE entity_type = '{entity}' AND entity_id = '{key_value}' AND action = 'CREATE'",
                    "reason": "Verify audit trail entry for creation",
                    "priority": "medium",
                    "confidence_base": 85,
                    "tags": ["audit", "create", "compliance"]
                },
                {
                    "name": "timestamp_validation",
                    "query": "SELECT created_at, updated_at FROM {table} WHERE {primary_key} = '{key_value}'",
                    "reason": "Verify creation timestamp is recent",
                    "priority": "low",
                    "confidence_base": 80,
                    "tags": ["timestamp", "create"]
                }
            ],
            
            "UPDATE": [
                {
                    "name": "record_modified",
                    "query": "SELECT * FROM {table} WHERE {primary_key} = '{key_value}'",
                    "reason": "Verify record was updated with correct values",
                    "priority": "critical",
                    "confidence_base": 95,
                    "tags": ["crud", "update", "data_integrity"]
                },
                {
                    "name": "version_increment",
                    "query": "SELECT version FROM {table} WHERE {primary_key} = '{key_value}'",
                    "reason": "Verify version number incremented",
                    "priority": "high",
                    "confidence_base": 88,
                    "tags": ["versioning", "update", "concurrency"]
                },
                {
                    "name": "update_timestamp",
                    "query": "SELECT updated_at FROM {table} WHERE {primary_key} = '{key_value}' AND updated_at > '{timestamp}'",
                    "reason": "Verify updated_at timestamp changed",
                    "priority": "medium",
                    "confidence_base": 85,
                    "tags": ["timestamp", "update"]
                },
                {
                    "name": "audit_update",
                    "query": "SELECT * FROM audit_log WHERE entity_id = '{key_value}' AND action = 'UPDATE' ORDER BY created_at DESC LIMIT 1",
                    "reason": "Verify audit trail for update",
                    "priority": "medium",
                    "confidence_base": 82,
                    "tags": ["audit", "update", "compliance"]
                }
            ],
            
            "DELETE": [
                {
                    "name": "record_deleted",
                    "query": "SELECT COUNT(*) as cnt FROM {table} WHERE {primary_key} = '{key_value}'",
                    "reason": "Verify record was deleted (hard delete)",
                    "priority": "critical",
                    "confidence_base": 95,
                    "tags": ["crud", "delete", "hard_delete"]
                },
                {
                    "name": "soft_delete",
                    "query": "SELECT deleted_at, is_deleted FROM {table} WHERE {primary_key} = '{key_value}'",
                    "reason": "Verify soft delete flag set",
                    "priority": "critical",
                    "confidence_base": 93,
                    "tags": ["crud", "delete", "soft_delete"]
                },
                {
                    "name": "cascade_delete",
                    "query": "SELECT COUNT(*) FROM {related_table} WHERE {foreign_key} = '{key_value}'",
                    "reason": "Verify related records were deleted",
                    "priority": "high",
                    "confidence_base": 88,
                    "tags": ["referential_integrity", "delete", "cascade"]
                },
                {
                    "name": "audit_delete",
                    "query": "SELECT * FROM audit_log WHERE entity_id = '{key_value}' AND action = 'DELETE'",
                    "reason": "Verify audit trail for deletion",
                    "priority": "medium",
                    "confidence_base": 85,
                    "tags": ["audit", "delete", "compliance"]
                }
            ],
            
            # Business Logic Patterns
            "ORDER_PROCESSING": [
                {
                    "name": "order_status",
                    "query": "SELECT status, total_amount FROM orders WHERE order_id = '{order_id}'",
                    "reason": "Verify order status transitioned correctly",
                    "priority": "critical",
                    "confidence_base": 95,
                    "tags": ["business_logic", "order", "status"]
                },
                {
                    "name": "order_items",
                    "query": "SELECT COUNT(*) as item_count FROM order_items WHERE order_id = '{order_id}'",
                    "reason": "Verify all order items were created",
                    "priority": "high",
                    "confidence_base": 92,
                    "tags": ["business_logic", "order", "items"]
                },
                {
                    "name": "inventory_update",
                    "query": "SELECT quantity FROM inventory WHERE product_id = '{product_id}'",
                    "reason": "Verify inventory was decremented",
                    "priority": "high",
                    "confidence_base": 90,
                    "tags": ["business_logic", "inventory", "stock"]
                },
                {
                    "name": "payment_record",
                    "query": "SELECT status, amount FROM payments WHERE order_id = '{order_id}'",
                    "reason": "Verify payment record created",
                    "priority": "critical",
                    "confidence_base": 95,
                    "tags": ["business_logic", "payment", "financial"]
                }
            ],
            
            "USER_MANAGEMENT": [
                {
                    "name": "user_created",
                    "query": "SELECT email, status FROM users WHERE user_id = '{user_id}'",
                    "reason": "Verify user account created",
                    "priority": "critical",
                    "confidence_base": 95,
                    "tags": ["user", "create", "account"]
                },
                {
                    "name": "user_roles",
                    "query": "SELECT role_name FROM user_roles WHERE user_id = '{user_id}'",
                    "reason": "Verify user roles assigned",
                    "priority": "high",
                    "confidence_base": 90,
                    "tags": ["user", "authorization", "rbac"]
                },
                {
                    "name": "user_permissions",
                    "query": "SELECT permission FROM user_permissions WHERE user_id = '{user_id}'",
                    "reason": "Verify user permissions granted",
                    "priority": "high",
                    "confidence_base": 88,
                    "tags": ["user", "authorization", "permissions"]
                },
                {
                    "name": "password_hash",
                    "query": "SELECT password_hash FROM users WHERE user_id = '{user_id}'",
                    "reason": "Verify password is hashed (not plaintext)",
                    "priority": "critical",
                    "confidence_base": 98,
                    "tags": ["security", "user", "password"]
                }
            ],
            
            # Referential Integrity Patterns
            "REFERENTIAL_INTEGRITY": [
                {
                    "name": "foreign_key_exists",
                    "query": "SELECT COUNT(*) FROM {parent_table} WHERE {parent_key} = '{parent_value}'",
                    "reason": "Verify foreign key reference exists",
                    "priority": "critical",
                    "confidence_base": 95,
                    "tags": ["referential_integrity", "foreign_key"]
                },
                {
                    "name": "child_records",
                    "query": "SELECT COUNT(*) FROM {child_table} WHERE {foreign_key} = '{parent_value}'",
                    "reason": "Verify child records linked correctly",
                    "priority": "high",
                    "confidence_base": 90,
                    "tags": ["referential_integrity", "child_records"]
                }
            ],
            
            # Data Quality Patterns
            "DATA_QUALITY": [
                {
                    "name": "no_nulls",
                    "query": "SELECT COUNT(*) FROM {table} WHERE {primary_key} = '{key_value}' AND ({required_column} IS NULL OR {required_column} = '')",
                    "reason": "Verify required fields are not null",
                    "priority": "high",
                    "confidence_base": 92,
                    "tags": ["data_quality", "null_check"]
                },
                {
                    "name": "data_format",
                    "query": "SELECT {column} FROM {table} WHERE {primary_key} = '{key_value}'",
                    "reason": "Verify data format/pattern is correct",
                    "priority": "medium",
                    "confidence_base": 85,
                    "tags": ["data_quality", "format"]
                },
                {
                    "name": "range_check",
                    "query": "SELECT {column} FROM {table} WHERE {primary_key} = '{key_value}' AND {column} BETWEEN {min} AND {max}",
                    "reason": "Verify value within expected range",
                    "priority": "medium",
                    "confidence_base": 87,
                    "tags": ["data_quality", "range", "constraints"]
                }
            ]
        }
    
    def _initialize_client(self):
        """Initialize AI client using multi-provider factory"""
        try:
            from framework.ai.ai_provider_factory import get_ai_provider
            
            # Get AI provider
            self.ai_provider = get_ai_provider(self.provider_name)
            self.enabled = True
            
            logger.info(f"AI Validation Suggester initialized with provider: {self.ai_provider.get_provider_name()}")
        
        except Exception as e:
            logger.warning(f"AI provider not available: {e}. Using fallback suggestions.")
            self.enabled = False
    
    def suggest_validations(
        self,
        api_endpoint: str,
        api_method: str,
        api_request: Dict[str, Any],
        api_response: Dict[str, Any],
        use_cache: bool = True
    ) -> ValidationStrategy:
        """
        Analyze API call and suggest database validations
        
        NEVER FAILS: Always returns suggestions using fallback if AI unavailable
        
        Args:
            api_endpoint: API endpoint (e.g., /api/orders/submit)
            api_method: HTTP method (POST, GET, etc.)
            api_request: Request payload
            api_response: Response data
            use_cache: Use cached patterns if available (default: True)
        
        Returns:
            ValidationStrategy with suggested DB validations (AI or rule-based)
        """
        # Check cache first
        if use_cache and self.cache_enabled and self.cache:
            cache_key = self.cache.generate_cache_key(api_endpoint, api_method, api_response)
            cached_strategy = self.cache.get(cache_key)
            if cached_strategy:
                logger.info(f"✓ Using cached validation strategy for {api_endpoint}")
                return cached_strategy
        
        # Use fallback immediately if AI not enabled
        if not self.enabled or not self.ai_provider:
            logger.warning(f"AI helper not available for validation suggestions. Skipping AI analysis, using rule-based fallback. Continuing to next step.")
            logger.info(f"Using rule-based validations for {api_endpoint}")
            return self._fallback_suggestions(api_endpoint, api_method, api_response)
        
        try:
            # Get existing mapping if available
            existing_mapping = self._get_existing_mapping(api_endpoint, api_method)
            
            # Build AI prompt
            prompt = self._build_validation_prompt(
                api_endpoint,
                api_method,
                api_request,
                api_response,
                existing_mapping
            )
            
            # Query AI with timeout protection
            ai_response = self._query_ai(prompt)
            
            # Parse and structure suggestions
            strategy = self._parse_ai_response(
                ai_response,
                api_endpoint,
                api_method,
                api_response
            )
            
            # Cache the strategy
            if self.cache_enabled and self.cache:
                cache_key = self.cache.generate_cache_key(api_endpoint, api_method, api_response)
                self.cache.put(cache_key, strategy)
            
            logger.info(f"✓ AI suggested {len(strategy.suggestions)} validations for {api_endpoint}")
            return strategy
        
        except Exception as e:
            # NEVER FAIL - Always fallback to rule-based suggestions
            logger.warning(f"AI validation failed ({e}), using rule-based fallback")
            return self._fallback_suggestions(api_endpoint, api_method, api_response)
    
    def _build_validation_prompt(
        self,
        endpoint: str,
        method: str,
        request: Dict,
        response: Dict,
        existing_mapping: Optional[Dict]
    ) -> str:
        """Build prompt for AI"""
        
        prompt = f"""You are a QA database validation expert. Analyze this API call and suggest database validations.

API Endpoint: {method} {endpoint}

Request Payload:
{json.dumps(request, indent=2)}

Response Data:
{json.dumps(response, indent=2)}

"""
        
        if existing_mapping:
            prompt += f"""
Known Database Mapping:
- Stored Procedures: {', '.join([p['name'] for p in existing_mapping.get('stored_procedures', [])])}
- Tables Affected: {', '.join([t['table'] for t in existing_mapping.get('tables_affected', [])])}
- Correlation Keys: {', '.join(existing_mapping.get('correlation_keys', {}).values())}

"""
        
        prompt += """
Your task:
1. Identify what data changes should have occurred in the database
2. Suggest specific SQL queries to validate these changes
3. Determine correlation keys from the API response
4. Prioritize validations (critical, high, medium, low)
5. Explain the reasoning for each validation

Respond in JSON format:
{
  "validations": [
    {
      "query": "SELECT ... FROM table WHERE ...",
      "reason": "Verify order was created",
      "priority": "critical",
      "expected_result": {"row_count": 1, "column_values": {}},
      "correlation_keys": ["order_id", "transaction_id"],
      "confidence": 95
    }
  ],
  "correlation_context": {
    "primary_key": "order_id",
    "transaction_id": "abc123",
    "business_keys": []
  },
  "reasoning": "Overall strategy explanation"
}

Guidelines:
- Use parameterized queries with {{key}} placeholders
- Suggest 3-7 validations per endpoint
- Critical: Data integrity, business rules
- High: Related records, referential integrity
- Medium: Audit logs, timestamps
- Low: Optional metadata

Focus on:
- Row existence checks
- Column value validations
- Row count assertions
- Referential integrity
- Business rule compliance
- Audit trail verification
"""
        
        return prompt
    
    def _query_ai(self, prompt: str) -> str:
        """Query AI provider with timeout and error protection"""
        if not self.enabled or not self.ai_provider:
            raise RuntimeError("AI provider not available")
        
        try:
            import signal
            
            # Set timeout for AI request (30 seconds max)
            def timeout_handler(signum, frame):
                raise TimeoutError("AI request timed out")
            
            # Note: signal.alarm only works on Unix, use alternative for Windows
            system_prompt = "You are an expert QA engineer specializing in database validation strategies."
            
            # Try with timeout protection
            response = self.ai_provider.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=2000
            )
            
            if not response or len(response.strip()) == 0:
                raise ValueError("Empty response from AI provider")
            
            return response
        
        except TimeoutError:
            logger.error("AI request timed out (30s limit)")
            raise
        except Exception as e:
            logger.error(f"AI query failed: {e}")
            raise
    
    def _parse_ai_response(
        self,
        ai_response: str,
        endpoint: str,
        method: str,
        api_response: Dict
    ) -> ValidationStrategy:
        """Parse AI response into ValidationStrategy"""
        
        try:
            # Extract JSON from response
            if '{' in ai_response and '}' in ai_response:
                start = ai_response.index('{')
                end = ai_response.rindex('}') + 1
                json_str = ai_response[start:end]
                data = json.loads(json_str)
            else:
                raise ValueError("No JSON found in AI response")
            
            # Parse validations
            suggestions = []
            for val in data.get('validations', []):
                suggestion = ValidationSuggestion(
                    query=val.get('query', ''),
                    reason=val.get('reason', ''),
                    priority=val.get('priority', 'medium'),
                    expected_result=val.get('expected_result', {}),
                    correlation_keys=val.get('correlation_keys', []),
                    confidence=val.get('confidence', 70)
                )
                suggestions.append(suggestion)
            
            # Sort by priority
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            suggestions.sort(key=lambda x: priority_order.get(x.priority, 4))
            
            return ValidationStrategy(
                endpoint=endpoint,
                method=method,
                suggestions=suggestions,
                correlation_context=data.get('correlation_context', {}),
                ai_reasoning=data.get('reasoning', '')
            )
        
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            raise
    
    def _get_existing_mapping(self, endpoint: str, method: str) -> Optional[Dict]:
        """Get existing API → DB mapping if available"""
        mappings = self.api_db_mappings.get('api_db_mappings', {})
        key = f"{method} {endpoint}"
        return mappings.get(key)
    
    def _fallback_suggestions(
        self,
        endpoint: str,
        method: str,
        response: Dict
    ) -> ValidationStrategy:
        """Enhanced fallback suggestions using pattern matching"""
        
        logger.info("Using enhanced pattern-based validation suggestions")
        
        # Extract potential keys from response
        correlation_keys = self._extract_keys_from_response(response)
        
        # Detect business context
        context = self._detect_business_context(endpoint, response)
        
        # Get pattern-based suggestions
        suggestions = self._generate_pattern_based_suggestions(
            method,
            context,
            correlation_keys,
            response
        )
        
        # Calculate confidence scores
        for suggestion in suggestions:
            suggestion.confidence = self._calculate_confidence_score(
                suggestion,
                correlation_keys,
                context
            )
        
        # Sort by priority and confidence
        suggestions.sort(key=lambda x: (
            {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.priority, 4),
            -x.confidence
        ))
        
        return ValidationStrategy(
            endpoint=endpoint,
            method=method,
            suggestions=suggestions,
            correlation_context=correlation_keys,
            ai_reasoning=f"Pattern-based strategy for {context} operations using {method} method"
        )
    
    def _detect_business_context(self, endpoint: str, response: Dict) -> str:
        """Detect business context from endpoint and response"""
        endpoint_lower = endpoint.lower()
        response_str = json.dumps(response).lower()
        
        # Order processing
        if any(word in endpoint_lower for word in ['order', 'cart', 'checkout', 'purchase']):
            return 'ORDER_PROCESSING'
        
        # User management
        if any(word in endpoint_lower for word in ['user', 'account', 'profile', 'register', 'signup']):
            return 'USER_MANAGEMENT'
        
        # Payment
        if any(word in endpoint_lower for word in ['payment', 'transaction', 'invoice', 'billing']):
            return 'PAYMENT'
        
        # Inventory
        if any(word in endpoint_lower for word in ['inventory', 'stock', 'product', 'item']):
            return 'INVENTORY'
        
        # Generic CRUD based on method
        return 'CRUD'
    
    def _generate_pattern_based_suggestions(
        self,
        method: str,
        context: str,
        correlation_keys: Dict,
        response: Dict
    ) -> List[ValidationSuggestion]:
        """Generate suggestions based on patterns"""
        suggestions = []
        
        # Map HTTP method to pattern category
        method_to_pattern = {
            'POST': 'CREATE',
            'PUT': 'UPDATE',
            'PATCH': 'UPDATE',
            'DELETE': 'DELETE',
            'GET': 'READ'
        }
        
        crud_pattern = method_to_pattern.get(method, 'CREATE')
        
        # Get CRUD patterns
        if crud_pattern in self.validation_patterns:
            for pattern in self.validation_patterns[crud_pattern]:
                suggestion = ValidationSuggestion(
                    query=pattern['query'],
                    reason=pattern['reason'],
                    priority=pattern['priority'],
                    expected_result={},
                    correlation_keys=list(correlation_keys.keys()),
                    confidence=pattern['confidence_base'],
                    pattern_type=crud_pattern,
                    tags=pattern['tags']
                )
                suggestions.append(suggestion)
        
        # Add context-specific patterns
        if context in self.validation_patterns:
            for pattern in self.validation_patterns[context][:3]:  # Limit to top 3
                suggestion = ValidationSuggestion(
                    query=pattern['query'],
                    reason=pattern['reason'],
                    priority=pattern['priority'],
                    expected_result={},
                    correlation_keys=list(correlation_keys.keys()),
                    confidence=pattern['confidence_base'],
                    pattern_type=context,
                    tags=pattern['tags']
                )
                suggestions.append(suggestion)
        
        # Add referential integrity checks if foreign keys detected
        if self._has_foreign_keys(response):
            for pattern in self.validation_patterns.get('REFERENTIAL_INTEGRITY', []):
                suggestion = ValidationSuggestion(
                    query=pattern['query'],
                    reason=pattern['reason'],
                    priority=pattern['priority'],
                    expected_result={},
                    correlation_keys=list(correlation_keys.keys()),
                    confidence=pattern['confidence_base'],
                    pattern_type='REFERENTIAL_INTEGRITY',
                    tags=pattern['tags']
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _has_foreign_keys(self, response: Dict) -> bool:
        """Detect if response contains foreign key references"""
        fk_patterns = ['_id', 'Id', 'user_id', 'customer_id', 'product_id', 'order_id']
        response_str = str(response)
        return any(pattern in response_str for pattern in fk_patterns)
    
    def _calculate_confidence_score(
        self,
        suggestion: ValidationSuggestion,
        correlation_keys: Dict,
        context: str
    ) -> int:
        """
        Calculate confidence score for validation suggestion
        
        Factors:
        - Base confidence from pattern
        - Availability of correlation keys (0-15 points)
        - Context match (0-10 points)
        - Query complexity (-5 to +5 points)
        
        Returns:
            Confidence score (0-100)
        """
        score = suggestion.confidence  # Start with base confidence
        
        # Correlation keys availability
        if correlation_keys:
            key_score = min(len(correlation_keys) * 5, 15)
            score += key_score
        
        # Context matching bonus
        if context in suggestion.tags:
            score += 10
        elif context.lower() in suggestion.reason.lower():
            score += 5
        
        # Priority weighting
        priority_bonus = {
            'critical': 5,
            'high': 3,
            'medium': 0,
            'low': -2
        }
        score += priority_bonus.get(suggestion.priority, 0)
        
        # Query complexity adjustment
        query_lower = suggestion.query.lower()
        if 'join' in query_lower:
            score -= 3  # Joins are harder to parameterize
        if 'count(*)' in query_lower:
            score += 2  # Simple count queries are reliable
        
        # Cap at 0-100 range
        return max(0, min(100, score))
    
    def _extract_keys_from_response(self, response: Dict) -> Dict[str, Any]:
        """Extract potential correlation keys from API response"""
        keys = {}
        
        # Common key patterns
        key_patterns = [
            'id', 'order_id', 'user_id', 'transaction_id', 
            'request_id', 'customer_id', 'product_id',
            'invoice_id', 'payment_id', 'session_id'
        ]
        
        for key_pattern in key_patterns:
            if key_pattern in response:
                keys[key_pattern] = response[key_pattern]
        
        return keys
    
    def generate_validation_report(self, strategy: ValidationStrategy) -> str:
        """Generate human-readable validation report"""
        
        report = f"""
{'='*80}
AI-SUGGESTED DATABASE VALIDATIONS
{'='*80}

Endpoint: {strategy.method} {strategy.endpoint}

AI Reasoning:
{strategy.ai_reasoning}

Correlation Context:
{json.dumps(strategy.correlation_context, indent=2)}

{'='*80}
SUGGESTED VALIDATIONS ({len(strategy.suggestions)} total)
{'='*80}

"""
        
        for i, suggestion in enumerate(strategy.suggestions, 1):
            report += f"""
{i}. [{suggestion.priority.upper()}] {suggestion.reason}
   Confidence: {suggestion.confidence}%
   
   Query:
   {suggestion.query}
   
   Expected Result:
   {json.dumps(suggestion.expected_result, indent=2)}
   
   Correlation Keys: {', '.join(suggestion.correlation_keys)}
   
   {'-'*80}
"""
        
        return report
    
    def apply_correlations(
        self,
        suggestion: ValidationSuggestion,
        correlation_values: Dict[str, Any]
    ) -> str:
        """Apply correlation values to query template"""
        
        query = suggestion.query
        
        # Replace placeholders
        for key, value in correlation_values.items():
            placeholder = f"{{{{{key}}}}}"
            query = query.replace(placeholder, str(value))
        
        return query
    
    def learn_from_execution(
        self,
        strategy: ValidationStrategy,
        execution_results: List[Dict[str, Any]]
    ):
        """
        Learn from validation execution results (for future enhancement)
        This can be used to improve suggestions over time
        """
        # Placeholder for learning mechanism
        # Could store in a database or file for analysis
        logger.info(f"Learning from {len(execution_results)} validation executions")
        pass
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.cache_enabled or not self.cache:
            return {"cache_enabled": False}
        
        return {
            "cache_enabled": True,
            **self.cache.get_statistics()
        }
    
    def clear_cache(self):
        """Clear validation pattern cache"""
        if self.cache_enabled and self.cache:
            self.cache.clear()
            logger.info("Validation cache cleared")
        else:
            logger.warning("Cache not enabled")
    
    def get_pattern_categories(self) -> List[str]:
        """Get list of available pattern categories"""
        return list(self.validation_patterns.keys())
    
    def get_patterns_by_category(self, category: str) -> List[Dict]:
        """Get all patterns in a specific category"""
        return self.validation_patterns.get(category, [])


# ========================================================================
# HELPER FUNCTIONS
# ========================================================================

def suggest_and_validate(
    api_endpoint: str,
    api_method: str,
    api_request: Dict,
    api_response: Dict,
    db_client,
    auto_execute: bool = False
) -> Dict[str, Any]:
    """
    Complete workflow: Suggest validations and optionally execute them
    
    Args:
        api_endpoint: API endpoint
        api_method: HTTP method
        api_request: Request payload
        api_response: Response data
        db_client: Database client instance
        auto_execute: Execute validations automatically
    
    Returns:
        Results dictionary
    """
    suggester = AIValidationSuggester()
    
    # Get suggestions
    strategy = suggester.suggest_validations(
        api_endpoint,
        api_method,
        api_request,
        api_response
    )
    
    # Print report
    report = suggester.generate_validation_report(strategy)
    print(report)
    
    results = {
        "strategy": strategy,
        "report": report,
        "validations_executed": []
    }
    
    # Execute if requested
    if auto_execute and db_client:
        logger.info("Auto-executing suggested validations...")
        
        for suggestion in strategy.suggestions:
            try:
                # Apply correlations
                query = suggester.apply_correlations(
                    suggestion,
                    strategy.correlation_context
                )
                
                # Execute query
                result = db_client.execute_query(query)
                
                execution_result = {
                    "suggestion": suggestion.reason,
                    "query": query,
                    "result": result,
                    "passed": len(result) > 0 if suggestion.expected_result.get('row_count') else True
                }
                
                results["validations_executed"].append(execution_result)
                
                logger.info(f"✓ Validation passed: {suggestion.reason}")
            
            except Exception as e:
                logger.error(f"✗ Validation failed: {suggestion.reason} - {e}")
                results["validations_executed"].append({
                    "suggestion": suggestion.reason,
                    "query": query,
                    "error": str(e),
                    "passed": False
                })
    
    return results


__all__ = [
    'AIValidationSuggester',
    'ValidationSuggestion',
    'ValidationStrategy',
    'suggest_and_validate'
]
