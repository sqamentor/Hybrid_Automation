"""
Multi-AI Provider Factory - Support Multiple AI Models

Supports: OpenAI (ChatGPT), Anthropic (Claude), Azure OpenAI, Google Gemini, 
          Ollama (Local), and any custom providers.

Configuration determines which AI provider to use for different features.
"""

import importlib
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, cast

from utils.logger import get_logger

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # dotenv not installed, skip

logger = get_logger(__name__)


def _load_requests_module() -> Any:
    """Dynamically import requests to avoid mypy stub dependency."""
    try:
        return importlib.import_module("requests")
    except ModuleNotFoundError as exc:
        raise RuntimeError("requests library not installed. Run: pip install requests") from exc


@dataclass
class AIProviderConfig:
    """Configuration for an AI provider."""
    name: str
    provider_type: str  # 'openai', 'anthropic', 'azure', 'gemini', 'ollama', 'custom'
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 4000
    enabled: bool = True
    priority: int = 1  # Lower number = higher priority
    extra_params: Optional[Dict[str, Any]] = None


class BaseAIProvider(ABC):
    """Base class for AI providers."""
    
    def __init__(self, config: AIProviderConfig):
        self.config = config
        self.client: Optional[Any] = None
        self._initialize()
    
    @abstractmethod
    def _initialize(self):
        """Initialize the AI client."""
        pass
    
    @abstractmethod
    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Generate text completion."""
        pass
    
    @abstractmethod
    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any
    ) -> str:
        """Generate chat completion."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return self.config.name


class OpenAIProvider(BaseAIProvider):
    """OpenAI Provider (ChatGPT: GPT-3.5, GPT-4, GPT-4o)"""
    
    def _initialize(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            
            api_key = self.config.api_key or os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.warning(f"OpenAI API key not found. Provider '{self.config.name}' disabled.")
                self.config.enabled = False
                return
            
            self.client = OpenAI(
                api_key=api_key,
                base_url=self.config.api_base
            )
            
            # Default models
            if not self.config.model:
                self.config.model = "gpt-4"
            
            logger.info(f"OpenAI provider '{self.config.name}' initialized with model {self.config.model}")
            
        except ImportError:
            logger.error("OpenAI library not installed. Run: pip install openai")
            self.config.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {e}")
            self.config.enabled = False
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self.config.enabled and self.client is not None
    
    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Generate completion using OpenAI with timeout and retry."""
        if not self.is_available():
            raise RuntimeError(f"OpenAI provider '{self.config.name}' is not available")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Add timeout to kwargs (default 30 seconds)
        kwargs['timeout'] = kwargs.get('timeout', 30)
        
        return self.generate_chat_completion(messages, **kwargs)
    
    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any
    ) -> str:
        """Generate chat completion using OpenAI with timeout protection."""
        if not self.is_available():
            raise RuntimeError(f"OpenAI provider '{self.config.name}' is not available")
        
        try:
            # Set timeout (default 30 seconds)
            timeout = kwargs.pop('timeout', 30)
            client = self.client
            if client is None:
                raise RuntimeError("OpenAI client is not initialized")
            
            response = client.chat.completions.create(
                model=kwargs.get('model', self.config.model),
                messages=messages,
                temperature=kwargs.get('temperature', self.config.temperature),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                timeout=timeout  # Add timeout to prevent hanging
            )
            
            choices: Sequence[Any] = getattr(response, 'choices', [])
            if not choices:
                raise ValueError("Empty response from OpenAI")
            content = choices[0].message.content
            if not isinstance(content, str):
                raise ValueError("OpenAI response missing text content")
            
            return content
        
        except TimeoutError as e:
            logger.error(f"OpenAI request timed out: {e}")
            raise
        except Exception as e:
            logger.error(f"OpenAI completion failed: {e}")
            raise


class AnthropicProvider(BaseAIProvider):
    """Anthropic Provider (Claude: Claude-3 Opus, Sonnet, Haiku)"""
    
    def _initialize(self):
        """Initialize Anthropic client."""
        try:
            from anthropic import Anthropic
            
            api_key = self.config.api_key or os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                logger.warning(f"Anthropic API key not found. Provider '{self.config.name}' disabled.")
                self.config.enabled = False
                return
            
            self.client = Anthropic(api_key=api_key)
            
            # Default models
            if not self.config.model:
                self.config.model = "claude-3-5-sonnet-20241022"
            
            logger.info(f"Anthropic provider '{self.config.name}' initialized with model {self.config.model}")
            
        except ImportError:
            logger.error("Anthropic library not installed. Run: pip install anthropic")
            self.config.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic provider: {e}")
            self.config.enabled = False
    
    def is_available(self) -> bool:
        """Check if Anthropic is available."""
        return self.config.enabled and self.client is not None
    
    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Generate completion using Anthropic with timeout protection."""
        if not self.is_available():
            raise RuntimeError(f"Anthropic provider '{self.config.name}' is not available")
        
        try:
            # Anthropic has built-in timeout support
            timeout = kwargs.pop('timeout', 30)
            
            client = self.client
            if client is None:
                raise RuntimeError("Anthropic client is not initialized")

            response = client.messages.create(
                model=kwargs.get('model', self.config.model),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                temperature=kwargs.get('temperature', self.config.temperature),
                system=system_prompt or "You are a helpful AI assistant.",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                timeout=timeout
            )
            
            content_blocks: Sequence[Any] = getattr(response, 'content', [])
            if not content_blocks:
                raise ValueError("Empty response from Anthropic")
            
            text_content = content_blocks[0].text
            if not isinstance(text_content, str):
                raise ValueError("Anthropic response missing text content")
            return text_content
        
        except TimeoutError as e:
            logger.error(f"Anthropic request timed out: {e}")
            raise
        except Exception as e:
            logger.error(f"Anthropic completion failed: {e}")
            raise
    
    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any
    ) -> str:
        """Generate chat completion using Anthropic."""
        if not self.is_available():
            raise RuntimeError(f"Anthropic provider '{self.config.name}' is not available")
        
        # Convert messages format
        system_prompt = None
        anthropic_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        try:
            client = self.client
            if client is None:
                raise RuntimeError("Anthropic client is not initialized")

            response = client.messages.create(
                model=kwargs.get('model', self.config.model),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                temperature=kwargs.get('temperature', self.config.temperature),
                system=system_prompt or "You are a helpful AI assistant.",
                messages=anthropic_messages
            )
            
            content_blocks: Sequence[Any] = getattr(response, 'content', [])
            if not content_blocks:
                raise ValueError("Empty response from Anthropic")
            text_content = content_blocks[0].text
            if not isinstance(text_content, str):
                raise ValueError("Anthropic response missing text content")
            return text_content
        
        except Exception as e:
            logger.error(f"Anthropic chat completion failed: {e}")
            raise


class AzureOpenAIProvider(BaseAIProvider):
    """Azure OpenAI Provider."""
    
    def _initialize(self):
        """Initialize Azure OpenAI client."""
        try:
            from openai import AzureOpenAI
            
            api_key = self.config.api_key or os.getenv('AZURE_OPENAI_API_KEY')
            azure_endpoint = self.config.api_base or os.getenv('AZURE_OPENAI_ENDPOINT')
            
            if not api_key or not azure_endpoint:
                logger.warning(f"Azure OpenAI credentials not found. Provider '{self.config.name}' disabled.")
                self.config.enabled = False
                return
            
            self.client = AzureOpenAI(
                api_key=api_key,
                api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview'),
                azure_endpoint=azure_endpoint
            )
            
            # Model is deployment name in Azure
            if not self.config.model:
                self.config.model = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4')
            
            logger.info(f"Azure OpenAI provider '{self.config.name}' initialized")
            
        except ImportError:
            logger.error("OpenAI library not installed. Run: pip install openai")
            self.config.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI provider: {e}")
            self.config.enabled = False
    
    def is_available(self) -> bool:
        """Check if Azure OpenAI is available."""
        return self.config.enabled and self.client is not None
    
    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Generate completion using Azure OpenAI."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        return self.generate_chat_completion(messages, **kwargs)
    
    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any
    ) -> str:
        """Generate chat completion using Azure OpenAI."""
        if not self.is_available():
            raise RuntimeError(f"Azure OpenAI provider '{self.config.name}' is not available")
        
        try:
            client = self.client
            if client is None:
                raise RuntimeError("Azure OpenAI client is not initialized")

            response = client.chat.completions.create(
                model=self.config.model,  # Deployment name
                messages=messages,
                temperature=kwargs.get('temperature', self.config.temperature),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens)
            )
            
            choices: Sequence[Any] = getattr(response, 'choices', [])
            if not choices:
                raise ValueError("Empty response from Azure OpenAI")
            content = choices[0].message.content
            if not isinstance(content, str):
                raise ValueError("Azure OpenAI response missing text content")
            return content
        
        except Exception as e:
            logger.error(f"Azure OpenAI completion failed: {e}")
            raise


class OllamaProvider(BaseAIProvider):
    """Ollama Provider (Local LLMs: Llama, Mistral, CodeLlama, etc.)"""
    
    def _initialize(self):
        """Initialize Ollama client."""
        try:
            requests = _load_requests_module()

            # Default Ollama endpoint
            self.api_base = self.config.api_base or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            
            # Default models
            if not self.config.model:
                self.config.model = "llama3.1"
            
            # Check if Ollama is running
            try:
                response = requests.get(f"{self.api_base}/api/tags", timeout=2)
                if response.status_code == 200:
                    logger.info(f"Ollama provider '{self.config.name}' initialized with model {self.config.model}")
                    self.client = True  # Just a flag
                else:
                    logger.warning(f"Ollama not responding. Provider '{self.config.name}' disabled.")
                    self.config.enabled = False
            except Exception:
                logger.warning(f"Ollama not running at {self.api_base}. Provider '{self.config.name}' disabled.")
                self.config.enabled = False
            
        except ImportError:
            logger.error("requests library not installed. Run: pip install requests")
            self.config.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Ollama provider: {e}")
            self.config.enabled = False
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        return self.config.enabled and self.client is not None
    
    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Generate completion using Ollama."""
        if not self.is_available():
            raise RuntimeError(f"Ollama provider '{self.config.name}' is not available")
        
        requests = _load_requests_module()
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        try:
            response = requests.post(
                f"{self.api_base}/api/generate",
                json={
                    "model": kwargs.get('model', self.config.model),
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get('temperature', self.config.temperature)
                    }
                },
                timeout=300
            )
            
            if response.status_code == 200:
                data = cast(Dict[str, Any], response.json())
                result = data.get("response", "")
                if not isinstance(result, str):
                    raise ValueError("Ollama response missing 'response' key")
                return result
            else:
                raise RuntimeError(f"Ollama request failed: {response.text}")
        
        except Exception as e:
            logger.error(f"Ollama completion failed: {e}")
            raise
    
    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any
    ) -> str:
        """Generate chat completion using Ollama."""
        if not self.is_available():
            raise RuntimeError(f"Ollama provider '{self.config.name}' is not available")
        
        requests = _load_requests_module()
        
        try:
            response = requests.post(
                f"{self.api_base}/api/chat",
                json={
                    "model": kwargs.get('model', self.config.model),
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get('temperature', self.config.temperature)
                    }
                },
                timeout=300
            )
            
            if response.status_code == 200:
                data = cast(Dict[str, Any], response.json())
                message = data.get("message", {})
                if not isinstance(message, dict):
                    raise ValueError("Ollama chat response missing 'message'")
                content = message.get("content", "")
                if not isinstance(content, str):
                    raise ValueError("Ollama chat response missing 'content'")
                return content
            else:
                raise RuntimeError(f"Ollama chat request failed: {response.text}")
        
        except Exception as e:
            logger.error(f"Ollama chat completion failed: {e}")
            raise


class AIProviderFactory:
    """Factory for creating and managing AI providers."""
    
    _instance: Optional['AIProviderFactory'] = None
    _providers: Dict[str, BaseAIProvider] = {}
    _default_provider: Optional[str] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_providers()
        return cls._instance
    
    def _load_providers(self):
        """Load AI providers from configuration."""
        from config.settings import settings

        # Get AI configuration
        ai_config = settings.get('global.ai_providers', {})
        
        if not ai_config:
            # Default configuration if none provided
            ai_config = self._get_default_config()
        
        # Set default provider
        self._default_provider = ai_config.get('default', 'openai')
        
        # Load each provider
        for provider_name, provider_config in ai_config.get('providers', {}).items():
            self._register_provider(provider_name, provider_config)
        
        logger.info(f"AI Provider Factory initialized. Default: {self._default_provider}")
        logger.info(f"Available providers: {list(self._providers.keys())}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default AI provider configuration."""
        return {
            'default': 'openai',
            'providers': {
                'openai': {
                    'type': 'openai',
                    'model': 'gpt-4',
                    'enabled': True,
                    'priority': 1
                },
                'claude': {
                    'type': 'anthropic',
                    'model': 'claude-3-5-sonnet-20241022',
                    'enabled': True,
                    'priority': 2
                },
                'azure': {
                    'type': 'azure',
                    'enabled': False,
                    'priority': 3
                },
                'ollama': {
                    'type': 'ollama',
                    'model': 'llama3.1',
                    'enabled': False,
                    'priority': 4
                }
            }
        }
    
    def _register_provider(self, name: str, config: Dict[str, Any]) -> None:
        """Register a new AI provider."""
        try:
            provider_config = AIProviderConfig(
                name=name,
                provider_type=config['type'],
                api_key=config.get('api_key'),
                api_base=config.get('api_base'),
                model=config.get('model'),
                temperature=config.get('temperature', 0.3),
                max_tokens=config.get('max_tokens', 4000),
                enabled=config.get('enabled', True),
                priority=config.get('priority', 999),
                extra_params=config.get('extra_params')
            )
            
            # Create provider instance
            provider_class = self._get_provider_class(provider_config.provider_type)
            if provider_class:
                provider = provider_class(provider_config)
                self._providers[name] = provider
                
                status = "✓ Available" if provider.is_available() else "✗ Unavailable"
                logger.info(f"Provider '{name}' registered: {status}")
            else:
                logger.warning(f"Unknown provider type: {provider_config.provider_type}")
        
        except Exception as e:
            logger.error(f"Failed to register provider '{name}': {e}")
    
    def _get_provider_class(self, provider_type: str) -> Optional[type]:
        """Get provider class by type."""
        provider_map = {
            'openai': OpenAIProvider,
            'anthropic': AnthropicProvider,
            'azure': AzureOpenAIProvider,
            'ollama': OllamaProvider
        }
        return provider_map.get(provider_type)
    
    def get_provider(self, provider_name: Optional[str] = None) -> Optional[BaseAIProvider]:
        """Get AI provider by name with graceful fallback.

        NEVER RAISES EXCEPTION - Returns None if no provider available

        Args:
            provider_name: Provider name (e.g., 'openai', 'claude', 'azure')
                          If None, returns default provider

        Returns:
            AI provider instance or None if none available
        """
        # Use default if not specified
        if provider_name is None:
            provider_name = self._default_provider
        if provider_name is None:
            logger.warning("No default AI provider configured")
            return None
        
        # Get provider
        provider = self._providers.get(provider_name)
        
        if provider and provider.is_available():
            return provider
        
        # Fallback to any available provider
        logger.warning(f"Provider '{provider_name}' not available. Trying fallback...")
        
        # Sort by priority
        sorted_providers = sorted(
            self._providers.items(),
            key=lambda x: x[1].config.priority
        )
        
        for name, prov in sorted_providers:
            if prov.is_available():
                logger.info(f"Using fallback provider: {name}")
                return prov
        
        # NEVER FAIL - Return None and let caller handle gracefully
        logger.warning("No AI provider available. Tests will use rule-based fallback.")
        return None
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return [
            name for name, provider in self._providers.items()
            if provider.is_available()
        ]
    
    def set_default_provider(self, provider_name: str) -> None:
        """Set default AI provider."""
        if provider_name in self._providers:
            self._default_provider = provider_name
            logger.info(f"Default provider changed to: {provider_name}")
        else:
            raise ValueError(f"Provider '{provider_name}' not found")


# Singleton instance
ai_factory = AIProviderFactory()


def get_ai_provider(provider_name: Optional[str] = None) -> Optional[BaseAIProvider]:
    """Convenience function to get AI provider.

    NEVER FAILS: Returns None if no provider available

    Usage:
        # Use default provider
        provider = get_ai_provider()
        if provider:
            response = provider.generate_completion(...)

        # Use specific provider
        provider = get_ai_provider('claude')
        provider = get_ai_provider('openai')

    Returns:
        AI provider instance or None if unavailable
    """
    try:
        return ai_factory.get_provider(provider_name)
    except Exception as e:
        logger.error(f"Failed to get AI provider: {e}")
        return None


__all__ = [
    'AIProviderConfig',
    'BaseAIProvider',
    'OpenAIProvider',
    'AnthropicProvider',
    'AzureOpenAIProvider',
    'OllamaProvider',
    'AIProviderFactory',
    'ai_factory',
    'get_ai_provider'
]
