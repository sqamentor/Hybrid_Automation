"""
Engine Selector - YAML-Based Decision Logic

This module implements the YAML-based engine selection strategy.
It reads test metadata and determines whether to use Playwright or Selenium.

Features:
- Rule priority weighting for intelligent decision-making
- Caching for frequently used test metadata patterns
- Fallback policy management
"""

import hashlib
import time
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast

import yaml  # type: ignore[import-untyped]

from config.settings import settings


@dataclass
class EngineDecision:
    """Engine selection decision."""
    engine: str  # 'playwright' or 'selenium'
    confidence: int  # 0-100
    reason: str
    rule_name: str
    fallback_engine: Optional[str] = None
    priority: int = 0  # Rule priority weight
    cache_hit: bool = False  # Whether decision came from cache


@dataclass
class CacheEntry:
    """Cache entry for engine decisions."""
    decision: EngineDecision
    timestamp: float
    hit_count: int = 0
    metadata_hash: str = ""


class EngineSelector:
    """YAML-based engine selector with rule priority weighting and caching.

    Features:
    - Priority-based rule evaluation (higher priority rules evaluated first)
    - LRU cache for frequently used test metadata patterns
    - Cache statistics tracking
    """
    
    def __init__(self, cache_size: int = 100, cache_ttl: int = 3600):
        """Initialize Engine Selector.

        Args:
            cache_size: Maximum number of cached decisions (default: 100)
            cache_ttl: Cache time-to-live in seconds (default: 3600)
        """
        self.decision_matrix = settings.get_engine_decision_matrix()
        self.rules = cast(List[Dict[str, Any]], self.decision_matrix.get('engine_selection_rules', []))
        self.module_profiles = cast(Dict[str, Any], self.decision_matrix.get('module_profiles', {}))
        self.custom_overrides = cast(Dict[str, Any], self.decision_matrix.get('custom_overrides', {}))
        
        # Sort rules by priority (higher priority first)
        self._sort_rules_by_priority()
        
        # Cache configuration
        self.cache_size = cache_size
        self.cache_ttl = cache_ttl
        self._decision_cache: Dict[str, CacheEntry] = {}
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_lookups': 0
        }
    
    def _sort_rules_by_priority(self):
        """Sort rules by priority weight (highest first)"""
        # Add default priority if not specified
        for rule in self.rules:
            if 'priority' not in rule:
                rule['priority'] = 50  # Default medium priority
        
        # Sort rules by priority (descending)
        self.rules.sort(key=lambda r: r.get('priority', 50), reverse=True)
    
    def select_engine(self, test_metadata: Dict[str, Any]) -> EngineDecision:
        """Select UI engine based on test metadata with caching.

        Args:
            test_metadata: Dictionary containing test characteristics
                - module: str (e.g., 'checkout', 'admin')
                - markers: List[str] (e.g., ['modern_spa', 'api_validation'])
                - ui_framework: str (e.g., 'React', 'JSP')
                - auth_type: str (e.g., 'SSO', 'Basic')
                - priority_override: int (optional, override rule priorities)
                - etc.

        Returns:
            EngineDecision with selected engine and reasoning
        """
        # Check cache first
        cache_key = self._generate_cache_key(test_metadata)
        cached_decision = self._get_cached_decision(cache_key)
        
        if cached_decision:
            self._cache_stats['hits'] += 1
            self._cache_stats['total_lookups'] += 1
            cached_decision.cache_hit = True
            return cached_decision
        
        self._cache_stats['misses'] += 1
        self._cache_stats['total_lookups'] += 1
        
        # Perform engine selection
        decision = self._select_engine_internal(test_metadata)
        
        # Cache the decision
        self._cache_decision(cache_key, decision, test_metadata)
        
        return decision
    
    def _select_engine_internal(self, test_metadata: Dict[str, Any]) -> EngineDecision:
        """Internal engine selection logic (without caching)

        Args:
            test_metadata: Test metadata dictionary

        Returns:
            EngineDecision object
        """
        # Check custom overrides first (highest priority)
        test_name = test_metadata.get('test_name', '')
        for pattern, engine in self.custom_overrides.items():
            if self._matches_pattern(test_name, pattern):
                return EngineDecision(
                    engine=engine,
                    confidence=100,
                    reason=f"Custom override pattern matched: {pattern}",
                    rule_name="custom_override",
                    priority=100  # Highest priority
                )
        
        # Check module profiles
        module = test_metadata.get('module')
        if module and module in self.module_profiles:
            profile = self.module_profiles[module]
            return EngineDecision(
                engine=profile.get('recommended_engine', 'playwright'),
                confidence=85,
                reason=f"Module profile: {profile.get('description', '')}",
                rule_name=f"module_profile_{module}",
                priority=90  # High priority
            )
        
        # Evaluate decision matrix rules (sorted by priority, first match wins)
        priority_override = test_metadata.get('priority_override')
        
        for rule in self.rules:
            if self._evaluate_rule(rule, test_metadata):
                # Use priority override if provided, otherwise use rule priority
                priority = priority_override if priority_override is not None else rule.get('priority', 50)
                
                return EngineDecision(
                    engine=rule['engine'],
                    confidence=rule.get('confidence', 70),
                    reason=rule.get('reason', 'Rule matched'),
                    rule_name=rule.get('name', 'unnamed_rule'),
                    fallback_engine=rule.get('fallback_engine'),
                    priority=priority
                )
        
        # Default fallback
        return EngineDecision(
            engine='playwright',
            confidence=50,
            reason='No specific rule matched, using default',
            rule_name='default',
            fallback_engine='selenium',
            priority=0  # Lowest priority
        )
    
    def _evaluate_rule(self, rule: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Evaluate if a rule matches the test metadata.

        Args:
            rule: Rule from decision matrix
            metadata: Test metadata

        Returns:
            True if rule matches, False otherwise
        """
        condition = rule.get('condition', {})
        
        # Handle default rule
        if condition.get('default'):
            return True
        
        # Check all conditions (AND logic)
        for key, expected_value in condition.items():
            actual_value = metadata.get(key)
            
            # Handle list of acceptable values
            if isinstance(expected_value, list):
                if actual_value not in expected_value:
                    return False
            
            # Handle comparison operators (>= for numbers)
            elif isinstance(expected_value, str) and expected_value.startswith('>='):
                threshold_str = expected_value[2:].strip()
                try:
                    threshold = int(threshold_str)
                except ValueError:
                    return False
                try:
                    actual_int = int(str(actual_value))
                except (TypeError, ValueError):
                    return False
                if actual_int < threshold:
                    return False
            
            # Handle comparison operators (> for numbers)
            elif isinstance(expected_value, str) and expected_value.startswith('>'):
                threshold_str = expected_value[1:].strip()
                if any(suffix in threshold_str for suffix in ('m', 'h')):
                    expected_minutes = self._parse_duration(threshold_str)
                    actual_minutes = self._parse_duration(str(actual_value))
                    if expected_minutes is None or actual_minutes is None:
                        return False
                    if actual_minutes <= expected_minutes:
                        return False
                else:
                    try:
                        threshold_val = int(threshold_str)
                        actual_int = int(str(actual_value))
                    except (TypeError, ValueError):
                        return False
                    if actual_int <= threshold_val:
                        return False
            
            # Handle boolean values
            elif isinstance(expected_value, bool):
                if actual_value != expected_value:
                    return False
            
            # Handle exact match
            else:
                if actual_value != expected_value:
                    return False
        
        return True
    
    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Check if text matches a pattern with wildcards.

        Args:
            text: Text to check
            pattern: Pattern with * wildcard

        Returns:
            True if pattern matches
        """
        if '*' not in pattern:
            return text == pattern
        
        # Simple wildcard matching
        parts = pattern.split('*')
        if len(parts) == 2:
            start, end = parts
            if start and not text.startswith(start):
                return False
            if end and not text.endswith(end):
                return False
            return True
        
        # Multiple wildcards - more complex matching
        import re
        regex_pattern = pattern.replace('*', '.*')
        return bool(re.match(f"^{regex_pattern}$", text))
    
    def _parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse duration string to minutes.

        Args:
            duration_str: Duration like "30m", "1h", "90"

        Returns:
            Duration in minutes or None
        """
        try:
            if 'm' in duration_str:
                return int(duration_str.replace('m', ''))
            elif 'h' in duration_str:
                return int(duration_str.replace('h', '')) * 60
            else:
                return int(duration_str)
        except ValueError:
            return None
    
    def get_fallback_policy(self) -> Dict[str, Any]:
        """Get fallback policy configuration."""
        return cast(Dict[str, Any], self.decision_matrix.get('fallback_policy', {}))
    
    def should_fallback(self, error_type: str) -> bool:
        """Determine if error should trigger fallback.

        Args:
            error_type: Type of error encountered

        Returns:
            True if fallback should be triggered
        """
        policy = self.get_fallback_policy()
        
        if not policy.get('enabled', True):
            return False
        
        trigger_conditions = cast(List[str], policy.get('trigger_conditions', []))
        non_trigger_conditions = cast(List[str], policy.get('non_trigger_conditions', []))
        
        # Check if error is in non-trigger list (takes precedence)
        if error_type in non_trigger_conditions:
            return False
        
        # Check if error is in trigger list
        return error_type in trigger_conditions
    
    # ========================================================================
    # CACHING METHODS
    # ========================================================================
    
    def _generate_cache_key(self, test_metadata: Dict[str, Any]) -> str:
        """Generate unique cache key from test metadata.

        Args:
            test_metadata: Test metadata dictionary

        Returns:
            MD5 hash of normalized metadata
        """
        # Create normalized metadata for caching (exclude transient fields)
        cache_metadata = {
            k: v for k, v in test_metadata.items()
            if k not in ['timestamp', 'run_id', 'priority_override']
        }
        
        # Sort for consistent hashing
        metadata_str = str(sorted(cache_metadata.items()))
        return hashlib.md5(metadata_str.encode()).hexdigest()
    
    def _get_cached_decision(self, cache_key: str) -> Optional[EngineDecision]:
        """Retrieve cached decision if valid.

        Args:
            cache_key: Cache key

        Returns:
            Cached EngineDecision or None
        """
        if cache_key not in self._decision_cache:
            return None
        
        entry = self._decision_cache[cache_key]
        
        # Check if cache entry is expired
        if time.time() - entry.timestamp > self.cache_ttl:
            del self._decision_cache[cache_key]
            return None
        
        # Update hit count
        entry.hit_count += 1
        
        return entry.decision
    
    def _cache_decision(self, cache_key: str, decision: EngineDecision, 
                        test_metadata: Dict[str, Any]) -> None:
        """Cache an engine decision.

        Args:
            cache_key: Cache key
            decision: EngineDecision to cache
            test_metadata: Original test metadata
        """
        # Evict oldest entries if cache is full
        if len(self._decision_cache) >= self.cache_size:
            self._evict_oldest_entry()
        
        # Create cache entry
        entry = CacheEntry(
            decision=decision,
            timestamp=time.time(),
            hit_count=0,
            metadata_hash=cache_key
        )
        
        self._decision_cache[cache_key] = entry
    
    def _evict_oldest_entry(self):
        """Evict the oldest cache entry (LRU-like behavior)"""
        if not self._decision_cache:
            return
        
        # Find entry with oldest timestamp and lowest hit count
        oldest_key = min(
            self._decision_cache.keys(),
            key=lambda k: (self._decision_cache[k].hit_count, self._decision_cache[k].timestamp)
        )
        
        del self._decision_cache[oldest_key]
        self._cache_stats['evictions'] += 1
    
    def clear_cache(self):
        """Clear all cached decisions."""
        self._decision_cache.clear()
        self._cache_stats['evictions'] += len(self._decision_cache)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache performance metrics
        """
        total = self._cache_stats['total_lookups']
        hit_rate = (self._cache_stats['hits'] / total * 100) if total > 0 else 0
        
        return {
            'cache_size': len(self._decision_cache),
            'max_cache_size': self.cache_size,
            'cache_ttl': self.cache_ttl,
            'total_lookups': total,
            'cache_hits': self._cache_stats['hits'],
            'cache_misses': self._cache_stats['misses'],
            'cache_hit_rate': f"{hit_rate:.2f}%",
            'evictions': self._cache_stats['evictions'],
            'top_cached_patterns': self._get_top_cached_patterns()
        }
    
    def _get_top_cached_patterns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently accessed cache patterns.

        Args:
            limit: Maximum number of patterns to return

        Returns:
            List of top cache patterns with hit counts
        """
        sorted_entries = sorted(
            self._decision_cache.items(),
            key=lambda x: x[1].hit_count,
            reverse=True
        )[:limit]
        
        return [
            {
                'cache_key': key[:16] + '...',  # Truncated hash
                'engine': entry.decision.engine,
                'rule_name': entry.decision.rule_name,
                'priority': entry.decision.priority,
                'hit_count': entry.hit_count,
                'age_seconds': int(time.time() - entry.timestamp)
            }
            for key, entry in sorted_entries
        ]
    
    # ========================================================================
    # PRIORITY MANAGEMENT
    # ========================================================================
    
    def get_rule_priorities(self) -> List[Dict[str, Any]]:
        """Get all rules sorted by priority.

        Returns:
            List of rules with their priorities
        """
        return [
            {
                'name': rule.get('name', 'unnamed'),
                'priority': rule.get('priority', 50),
                'engine': rule.get('engine', 'unknown'),
                'confidence': rule.get('confidence', 70)
            }
            for rule in self.rules
            if 'engine' in rule  # Only include rules with engine specified
        ]
    
    def update_rule_priority(self, rule_name: str, new_priority: int) -> bool:
        """Update priority of a specific rule.

        Args:
            rule_name: Name of the rule to update
            new_priority: New priority value (0-100)

        Returns:
            True if rule was found and updated, False otherwise
        """
        for rule in self.rules:
            if rule.get('name') == rule_name:
                rule['priority'] = new_priority
                self._sort_rules_by_priority()
                self.clear_cache()  # Clear cache after priority change
                return True
        return False


# ========================================================================
# HELPER FUNCTIONS
# ========================================================================

def extract_test_metadata(test_item: Any) -> Dict[str, Any]:
    """Extract metadata from pytest test item.

    Args:
        test_item: pytest test item

    Returns:
        Dictionary of test metadata
    """
    metadata = {
        'test_name': test_item.name,
        'module': None,
        'markers': [],
        'ui_framework': None,
        'auth_type': None,
        'ui_type': None,
        'legacy_ui': False,
        'modern_spa': False,
        'mobile_first': False,
        'xhr_heavy': False,
        'api_validation_required': False
    }
    
    # Extract markers
    for marker in test_item.iter_markers():
        metadata['markers'].append(marker.name)
        
        # Special marker handling
        if marker.name == 'module' and marker.args:
            metadata['module'] = marker.args[0]
        elif marker.name == 'ui_framework' and marker.args:
            metadata['ui_framework'] = marker.args[0]
        elif marker.name == 'auth_type' and marker.args:
            metadata['auth_type'] = marker.args[0]
        elif marker.name == 'modern_spa':
            metadata['modern_spa'] = True
            metadata['ui_type'] = 'spa'
        elif marker.name == 'legacy_ui':
            metadata['legacy_ui'] = True
        elif marker.name == 'mobile':
            metadata['mobile_first'] = True
        elif marker.name == 'api_validation':
            metadata['api_validation_required'] = True
    
    # Infer characteristics from markers
    if 'React' in str(metadata['ui_framework']) or 'Vue' in str(metadata['ui_framework']) or 'Angular' in str(metadata['ui_framework']):
        metadata['xhr_heavy'] = True
        metadata['modern_spa'] = True
    
    return metadata


# ========================================================================
# EXPORT
# ========================================================================

__all__ = ['EngineSelector', 'EngineDecision', 'CacheEntry', 'extract_test_metadata']
