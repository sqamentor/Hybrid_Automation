"""
AI-Powered Engine Selector

This module implements AI-based engine selection using OpenAI/Azure OpenAI/Local LLMs.
It analyzes test metadata and historical data to recommend the optimal engine.

Features:
- Multi-provider support (OpenAI, Azure OpenAI, Ollama, LlamaCPP)
- Automatic retry logic with exponential backoff
- Response caching for performance optimization
- Graceful degradation when AI is unavailable
"""

import json
import os
import time
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from functools import wraps
from framework.core.engine_selector import EngineDecision
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AIEngineRecommendation:
    """AI engine recommendation"""
    engine: str
    confidence: int
    reasoning: str
    analysis: Dict[str, Any]
    cached: bool = False
    response_time_ms: float = 0.0


@dataclass
class CachedResponse:
    """Cached AI response"""
    response: str
    timestamp: float
    hit_count: int = 0
    metadata_hash: str = ""


class AIEngineSelector:
    """
    AI-powered engine selector with advanced features
    
    Features:
    - Multi-provider support (OpenAI, Azure OpenAI, Ollama, LlamaCPP)
    - Automatic retry with exponential backoff
    - Response caching for performance
    - Graceful degradation
    """
    
    def __init__(
        self, 
        provider_type: str = "openai",
        cache_enabled: bool = True,
        cache_size: int = 100,
        cache_ttl: int = 3600,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize AI Engine Selector
        
        Args:
            provider_type: 'openai', 'azure_openai', 'ollama', 'llamacpp'
            cache_enabled: Enable response caching
            cache_size: Maximum cached responses
            cache_ttl: Cache TTL in seconds (default: 1 hour)
            max_retries: Maximum retry attempts for API calls
            retry_delay: Initial retry delay in seconds (exponential backoff)
        """
        self.provider_type = provider_type
        self.enabled = self._check_enabled()
        self.client = None
        
        # Retry configuration
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Cache configuration
        self.cache_enabled = cache_enabled
        self.cache_size = cache_size
        self.cache_ttl = cache_ttl
        self._response_cache: Dict[str, CachedResponse] = {}
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_lookups': 0
        }
        
        if self.enabled:
            self._initialize_client()
    
    def _check_enabled(self) -> bool:
        """Check if AI engine is enabled and configured"""
        from config.settings import settings
        
        matrix = settings.get_engine_decision_matrix()
        ai_config = matrix.get('ai_engine_selector', {})
        
        if not ai_config.get('enabled', False):
            logger.info("AI engine selector is disabled")
            return False
        
        # Check for API key based on provider
        if self.provider_type == "openai":
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.warning("OPENAI_API_KEY not found, AI selector disabled")
                return False
        elif self.provider_type == "azure_openai":
            api_key = os.getenv('AZURE_OPENAI_API_KEY')
            if not api_key:
                logger.warning("AZURE_OPENAI_API_KEY not found, AI selector disabled")
                return False
        # Local LLMs don't require API keys
        
        return True
    
    def _initialize_client(self):
        """Initialize AI client based on provider type"""
        try:
            if self.provider_type == "openai":
                import openai
                self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                logger.info("OpenAI client initialized")
            
            elif self.provider_type == "azure_openai":
                import openai
                self.client = openai.AzureOpenAI(
                    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                    api_version="2024-02-01",
                    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
                )
                logger.info("Azure OpenAI client initialized")
            
            elif self.provider_type == "ollama":
                # Ollama local LLM support
                self.client = self._initialize_ollama()
                logger.info("Ollama client initialized")
            
            elif self.provider_type == "llamacpp":
                # LlamaCPP local LLM support
                self.client = self._initialize_llamacpp()
                logger.info("LlamaCPP client initialized")
            
            else:
                logger.error(f"Unknown provider type: {self.provider_type}")
                self.enabled = False
        
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {e}")
            self.enabled = False
    
    def _initialize_ollama(self):
        """Initialize Ollama client"""
        try:
            import requests
            
            # Check if Ollama is running
            ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
            response = requests.get(f"{ollama_host}/api/tags", timeout=5)
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                logger.info(f"Ollama available with {len(models)} models")
                return {'type': 'ollama', 'host': ollama_host}
            else:
                logger.warning("Ollama not responding")
                self.enabled = False
                return None
        
        except Exception as e:
            logger.error(f"Ollama initialization failed: {e}")
            self.enabled = False
            return None
    
    def _initialize_llamacpp(self):
        """Initialize LlamaCPP client"""
        try:
            from llama_cpp import Llama
            
            model_path = os.getenv('LLAMACPP_MODEL_PATH')
            if not model_path or not os.path.exists(model_path):
                logger.error(f"LlamaCPP model not found at {model_path}")
                self.enabled = False
                return None
            
            llm = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_threads=4,
                n_gpu_layers=0  # Set to > 0 for GPU acceleration
            )
            
            logger.info(f"LlamaCPP initialized with model: {model_path}")
            return {'type': 'llamacpp', 'llm': llm}
        
        except ImportError:
            logger.error("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
            self.enabled = False
            return None
        except Exception as e:
            logger.error(f"LlamaCPP initialization failed: {e}")
            self.enabled = False
            return None
    
    def select_engine(
        self,
        test_metadata: Dict[str, Any],
        historical_data: Optional[Dict[str, Any]] = None
    ) -> Optional[EngineDecision]:
        """
        Use AI to select the optimal engine with caching and retry
        
        Args:
            test_metadata: Test characteristics
            historical_data: Historical execution data (optional)
        
        Returns:
            EngineDecision or None if AI is unavailable
        """
        if not self.enabled or not self.client:
            logger.warning("AI helper not available for engine selection. Skipping AI-based engine recommendation. Continuing with default engine.")
            return None
        
        start_time = time.time()
        
        try:
            prompt = self._build_prompt(test_metadata, historical_data)
            
            # Check cache first
            cache_key = self._generate_cache_key(prompt)
            cached_response = self._get_cached_response(cache_key)
            
            if cached_response:
                self._cache_stats['hits'] += 1
                self._cache_stats['total_lookups'] += 1
                decision = self._parse_response(cached_response)
                if decision:
                    decision.reason += " (cached)"
                    logger.info(f"AI cache hit for test: {test_metadata.get('test_name')}")
                return decision
            
            self._cache_stats['misses'] += 1
            self._cache_stats['total_lookups'] += 1
            
            # Query AI with retry logic
            response = self._query_ai_with_retry(prompt)
            
            if response:
                # Cache the response
                self._cache_response(cache_key, response)
                
                decision = self._parse_response(response)
                if decision:
                    response_time = (time.time() - start_time) * 1000
                    logger.info(f"AI recommendation for {test_metadata.get('test_name')}: {decision.engine} ({response_time:.0f}ms)")
                return decision
            
        except Exception as e:
            logger.error(f"AI engine selection failed: {e}")
        
        return None
    
    def _build_prompt(
        self,
        test_metadata: Dict[str, Any],
        historical_data: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for AI engine selector"""
        from config.settings import settings
        
        matrix = settings.get_engine_decision_matrix()
        ai_config = matrix.get('ai_engine_selector', {})
        template = ai_config.get('prompt_template', '')
        
        # Build historical context
        historical_context = "No historical data available"
        if historical_data:
            failures = historical_data.get('failures', [])
            if failures:
                historical_context = f"Recent failures: {len(failures)}\n"
                historical_context += f"Playwright failures: {sum(1 for f in failures if f.get('engine') == 'playwright')}\n"
                historical_context += f"Selenium failures: {sum(1 for f in failures if f.get('engine') == 'selenium')}"
        
        # Format prompt
        prompt = template.format(
            test_name=test_metadata.get('test_name', 'unknown'),
            module=test_metadata.get('module', 'unknown'),
            markers=', '.join(test_metadata.get('markers', [])),
            historical_failures=historical_context
        )
        
        # Add capability context
        prompt += "\n\nCapability Summary:\n"
        prompt += "Playwright: Best for modern SPA, API interception, fast execution, mobile emulation\n"
        prompt += "Selenium: Best for legacy UI, SSO/MFA, deep iframes, long sessions, enterprise auth\n"
        
        return prompt
    
    def _query_ai_with_retry(self, prompt: str) -> Optional[str]:
        """Query AI model with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = self._query_ai(prompt)
                if response:
                    return response
                
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"AI query attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"AI query failed after {self.max_retries} attempts: {e}")
        
        if last_exception:
            raise last_exception
        
        return None
    
    def _query_ai(self, prompt: str) -> Optional[str]:
        """Query AI model (single attempt)"""
        try:
            from config.settings import settings
            
            matrix = settings.get_engine_decision_matrix()
            ai_config = matrix.get('ai_engine_selector', {})
            model = ai_config.get('provider', {}).get('model', 'gpt-4')
            
            if self.provider_type in ["openai", "azure_openai"]:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a QA automation expert who selects the optimal UI testing engine."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                return response.choices[0].message.content
            
            elif self.provider_type == "ollama":
                return self._query_ollama(prompt, model)
            
            elif self.provider_type == "llamacpp":
                return self._query_llamacpp(prompt)
        
        except Exception as e:
            logger.error(f"AI query failed: {e}")
            raise
        
        return None
    
    def _query_ollama(self, prompt: str, model: str = "llama2") -> Optional[str]:
        """Query Ollama local LLM"""
        try:
            import requests
            
            ollama_host = self.client['host']
            model = os.getenv('OLLAMA_MODEL', model)
            
            response = requests.post(
                f"{ollama_host}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 500
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                logger.error(f"Ollama request failed: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Ollama query failed: {e}")
            raise
    
    def _query_llamacpp(self, prompt: str) -> Optional[str]:
        """Query LlamaCPP local LLM"""
        try:
            llm = self.client['llm']
            
            system_prompt = "You are a QA automation expert who selects the optimal UI testing engine."
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = llm(
                full_prompt,
                max_tokens=500,
                temperature=0.3,
                stop=["</s>", "\n\n\n"],
                echo=False
            )
            
            return response['choices'][0]['text']
        
        except Exception as e:
            logger.error(f"LlamaCPP query failed: {e}")
            raise
    
    def _parse_response(self, response: str) -> Optional[EngineDecision]:
        """Parse AI response into EngineDecision"""
        try:
            # Try to extract JSON from response
            if '{' in response and '}' in response:
                start = response.index('{')
                end = response.rindex('}') + 1
                json_str = response[start:end]
                data = json.loads(json_str)
                
                engine = data.get('engine', 'playwright').lower()
                confidence = int(data.get('confidence', 70))
                reasoning = data.get('reasoning', 'AI recommendation')
                
                # Validate confidence threshold
                from config.settings import settings
                matrix = settings.get_engine_decision_matrix()
                ai_config = matrix.get('ai_engine_selector', {})
                threshold = ai_config.get('confidence_threshold', 80)
                
                if confidence < threshold:
                    logger.warning(f"AI confidence {confidence} below threshold {threshold}")
                    return None
                
                return EngineDecision(
                    engine=engine,
                    confidence=confidence,
                    reason=reasoning,
                    rule_name="ai_recommendation"
                )
        
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
        
        return None
    
    def analyze_test_suite(self, test_items: list) -> Dict[str, Any]:
        """
        Analyze entire test suite and provide recommendations
        
        Args:
            test_items: List of pytest test items
        
        Returns:
            Analysis with recommendations
        """
        if not self.enabled:
            logger.warning("AI helper not available for batch test analysis. Skipping AI analysis. Continuing without recommendations.")
            return {"error": "AI not enabled", "message": "AI helper not available, skipping this step"}
        
        analysis = {
            "total_tests": len(test_items),
            "playwright_recommended": 0,
            "selenium_recommended": 0,
            "recommendations": []
        }
        
        for item in test_items:
            from framework.core.engine_selector import extract_test_metadata
            metadata = extract_test_metadata(item)
            decision = self.select_engine(metadata)
            
            if decision:
                if decision.engine == "playwright":
                    analysis["playwright_recommended"] += 1
                else:
                    analysis["selenium_recommended"] += 1
                
                analysis["recommendations"].append({
                    "test": metadata['test_name'],
                    "engine": decision.engine,
                    "confidence": decision.confidence,
                    "reason": decision.reason
                })
        
        return analysis
    
    # ========================================================================
    # CACHING METHODS
    # ========================================================================
    
    def _generate_cache_key(self, prompt: str) -> str:
        """Generate cache key from prompt"""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Retrieve cached response if valid"""
        if not self.cache_enabled or cache_key not in self._response_cache:
            return None
        
        entry = self._response_cache[cache_key]
        
        # Check if cache entry is expired
        if time.time() - entry.timestamp > self.cache_ttl:
            del self._response_cache[cache_key]
            return None
        
        # Update hit count
        entry.hit_count += 1
        
        return entry.response
    
    def _cache_response(self, cache_key: str, response: str):
        """Cache an AI response"""
        if not self.cache_enabled:
            return
        
        # Evict oldest entries if cache is full
        if len(self._response_cache) >= self.cache_size:
            self._evict_oldest_cache_entry()
        
        # Create cache entry
        entry = CachedResponse(
            response=response,
            timestamp=time.time(),
            hit_count=0,
            metadata_hash=cache_key
        )
        
        self._response_cache[cache_key] = entry
    
    def _evict_oldest_cache_entry(self):
        """Evict the oldest cache entry (LRU-like)"""
        if not self._response_cache:
            return
        
        oldest_key = min(
            self._response_cache.keys(),
            key=lambda k: (self._response_cache[k].hit_count, self._response_cache[k].timestamp)
        )
        
        del self._response_cache[oldest_key]
        self._cache_stats['evictions'] += 1
    
    def clear_cache(self):
        """Clear all cached responses"""
        self._response_cache.clear()
        self._cache_stats['evictions'] += len(self._response_cache)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self._cache_stats['total_lookups']
        hit_rate = (self._cache_stats['hits'] / total * 100) if total > 0 else 0
        
        return {
            'enabled': self.cache_enabled,
            'cache_size': len(self._response_cache),
            'max_cache_size': self.cache_size,
            'cache_ttl': self.cache_ttl,
            'total_lookups': total,
            'cache_hits': self._cache_stats['hits'],
            'cache_misses': self._cache_stats['misses'],
            'cache_hit_rate': f"{hit_rate:.2f}%",
            'evictions': self._cache_stats['evictions']
        }
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the AI provider"""
        return {
            'provider_type': self.provider_type,
            'enabled': self.enabled,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'cache_enabled': self.cache_enabled,
            'cache_size': self.cache_size,
            'cache_ttl': self.cache_ttl
        }
    
    def test_connection(self) -> bool:
        """Test AI provider connection"""
        if not self.enabled or not self.client:
            return False
        
        try:
            test_prompt = "Respond with 'OK' if you can read this message."
            response = self._query_ai(test_prompt)
            return response is not None and len(response) > 0
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# ========================================================================
# EXPORT
# ========================================================================

__all__ = ['AIEngineSelector', 'AIEngineRecommendation', 'CachedResponse']
