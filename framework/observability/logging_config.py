"""
Enterprise Logging Configuration
=================================

Environment-aware logging configuration for:
- Development: Verbose logging, console output
- Testing/QA: Moderate logging, file output
- Staging: Production-like, reduced verbosity
- Production: Minimal logging, emergency alerts only

Configuration includes:
- Log levels per environment
- Retention policies
- Sampling rates
- Alert thresholds
- SIEM integration settings
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import yaml

# Self-instrumentation for logging_config module
try:
    from framework.observability.universal_logger import log_function
except ImportError:
    def log_function(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

_config_log = logging.getLogger(__name__)


class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class RetentionPolicy:
    """Log retention configuration"""
    app_logs_days: int = 30
    audit_logs_days: int = 365  # 1 year for compliance
    security_logs_days: int = 180  # 6 months
    performance_logs_days: int = 30
    max_file_size_mb: int = 100
    backup_count: int = 10


@dataclass
class SamplingConfig:
    """Log sampling configuration for high-volume scenarios"""
    enabled: bool = False
    sample_rate: float = 1.0  # 1.0 = log everything, 0.1 = log 10%
    debug_sample_rate: float = 0.1  # Sample DEBUG logs more aggressively
    always_log_errors: bool = True  # Always log errors regardless of sampling


@dataclass
class SIEMConfig:
    """SIEM integration configuration"""
    enabled: bool = False
    provider: str = "elk"  # elk, datadog, splunk, grafana
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    index_name: str = "test-automation"
    batch_size: int = 100
    flush_interval_seconds: int = 10


@dataclass
class AlertConfig:
    """Alert thresholds for monitoring"""
    error_rate_threshold: int = 10  # Errors per minute
    critical_alert_enabled: bool = True
    alert_webhook_url: Optional[str] = None
    alert_email: Optional[str] = None


@dataclass
class SecurityConfig:
    """Security logging configuration"""
    log_auth_attempts: bool = True
    log_auth_failures: bool = True
    log_privilege_escalation: bool = True
    log_data_access: bool = True
    mask_sensitive_data: bool = True
    sensitive_fields: List[str] = field(default_factory=lambda: [
        'password', 'token', 'api_key', 'secret', 'credit_card', 'ssn'
    ])


@dataclass
class PerformanceConfig:
    """Performance logging configuration"""
    log_slow_operations: bool = True
    slow_operation_threshold_ms: float = 1000.0  # 1 second
    log_all_operations: bool = False  # Only log in dev/testing
    track_memory_usage: bool = False
    track_cpu_usage: bool = False


@dataclass
class EnvironmentConfig:
    """Complete logging configuration for an environment"""
    environment: Environment
    log_level: LogLevel
    console_output: bool
    file_output: bool
    json_format: bool
    retention: RetentionPolicy
    sampling: SamplingConfig
    siem: SIEMConfig
    alerts: AlertConfig
    security: SecurityConfig
    performance: PerformanceConfig


class LoggingConfigManager:
    """Manages logging configuration across environments"""
    
    DEFAULT_CONFIGS = {
        Environment.DEVELOPMENT: EnvironmentConfig(
            environment=Environment.DEVELOPMENT,
            log_level=LogLevel.DEBUG,
            console_output=True,
            file_output=True,
            json_format=False,  # Human-readable for dev
            retention=RetentionPolicy(
                app_logs_days=7,
                audit_logs_days=30,
                security_logs_days=30,
                performance_logs_days=7,
                max_file_size_mb=50,
                backup_count=5
            ),
            sampling=SamplingConfig(
                enabled=False,  # Log everything in dev
                sample_rate=1.0
            ),
            siem=SIEMConfig(enabled=False),
            alerts=AlertConfig(
                error_rate_threshold=100,  # Higher threshold in dev
                critical_alert_enabled=False
            ),
            security=SecurityConfig(
                log_auth_attempts=True,
                log_auth_failures=True,
                mask_sensitive_data=True
            ),
            performance=PerformanceConfig(
                log_slow_operations=True,
                slow_operation_threshold_ms=500.0,
                log_all_operations=True,  # Log all operations in dev
                track_memory_usage=True,
                track_cpu_usage=True
            )
        ),
        
        Environment.TESTING: EnvironmentConfig(
            environment=Environment.TESTING,
            log_level=LogLevel.DEBUG,
            console_output=True,
            file_output=True,
            json_format=True,  # Structured for analysis
            retention=RetentionPolicy(
                app_logs_days=14,
                audit_logs_days=90,
                security_logs_days=60,
                performance_logs_days=14,
                max_file_size_mb=75,
                backup_count=10
            ),
            sampling=SamplingConfig(
                enabled=False,  # Log everything in testing
                sample_rate=1.0
            ),
            siem=SIEMConfig(
                enabled=True,
                provider="elk",
                index_name="test-automation-qa"
            ),
            alerts=AlertConfig(
                error_rate_threshold=50,
                critical_alert_enabled=True
            ),
            security=SecurityConfig(
                log_auth_attempts=True,
                log_auth_failures=True,
                log_privilege_escalation=True,
                mask_sensitive_data=True
            ),
            performance=PerformanceConfig(
                log_slow_operations=True,
                slow_operation_threshold_ms=1000.0,
                log_all_operations=True,
                track_memory_usage=True
            )
        ),
        
        Environment.STAGING: EnvironmentConfig(
            environment=Environment.STAGING,
            log_level=LogLevel.INFO,
            console_output=False,
            file_output=True,
            json_format=True,
            retention=RetentionPolicy(
                app_logs_days=30,
                audit_logs_days=365,
                security_logs_days=180,
                performance_logs_days=30,
                max_file_size_mb=100,
                backup_count=15
            ),
            sampling=SamplingConfig(
                enabled=True,
                sample_rate=0.5,  # Sample 50% in staging
                debug_sample_rate=0.1,
                always_log_errors=True
            ),
            siem=SIEMConfig(
                enabled=True,
                provider="elk",
                index_name="test-automation-staging"
            ),
            alerts=AlertConfig(
                error_rate_threshold=20,
                critical_alert_enabled=True
            ),
            security=SecurityConfig(
                log_auth_attempts=True,
                log_auth_failures=True,
                log_privilege_escalation=True,
                log_data_access=True,
                mask_sensitive_data=True
            ),
            performance=PerformanceConfig(
                log_slow_operations=True,
                slow_operation_threshold_ms=1500.0,
                log_all_operations=False
            )
        ),
        
        Environment.PRODUCTION: EnvironmentConfig(
            environment=Environment.PRODUCTION,
            log_level=LogLevel.WARNING,
            console_output=False,
            file_output=True,
            json_format=True,
            retention=RetentionPolicy(
                app_logs_days=90,
                audit_logs_days=365,  # 1 year for compliance
                security_logs_days=365,
                performance_logs_days=30,
                max_file_size_mb=100,
                backup_count=30
            ),
            sampling=SamplingConfig(
                enabled=True,
                sample_rate=0.1,  # Sample 10% in production
                debug_sample_rate=0.01,  # 1% for debug
                always_log_errors=True
            ),
            siem=SIEMConfig(
                enabled=True,
                provider="datadog",  # or elk, splunk
                index_name="test-automation-prod"
            ),
            alerts=AlertConfig(
                error_rate_threshold=10,
                critical_alert_enabled=True
            ),
            security=SecurityConfig(
                log_auth_attempts=True,
                log_auth_failures=True,
                log_privilege_escalation=True,
                log_data_access=True,
                mask_sensitive_data=True
            ),
            performance=PerformanceConfig(
                log_slow_operations=True,
                slow_operation_threshold_ms=2000.0,
                log_all_operations=False,  # Only log slow operations
                track_memory_usage=False,
                track_cpu_usage=False
            )
        )
    }
    
    @log_function(log_args=True)
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize configuration manager"""
        self.config_file = config_file or Path("config/logging_config.yaml")
        self.configs = self._load_configs()
    
    @log_function(log_timing=True)
    def _load_configs(self) -> Dict[Environment, EnvironmentConfig]:
        """Load configurations from file or use defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                if not data or 'environments' not in data:
                    _config_log.warning(f"No 'environments' key in {self.config_file}, using defaults")
                    return self.DEFAULT_CONFIGS
                
                # Parse YAML into EnvironmentConfig objects
                configs = {}
                for env_name, env_data in data.get('environments', {}).items():
                    try:
                        env_enum = self._parse_environment(env_name)
                        config = self._parse_environment_config(env_enum, env_data)
                        configs[env_enum] = config
                        _config_log.info(f"Loaded config for {env_enum.value} from YAML")
                    except Exception as parse_err:
                        _config_log.warning(
                            f"Failed to parse config for {env_name}: {parse_err}, using default"
                        )
                        configs[env_enum] = self.DEFAULT_CONFIGS.get(
                            env_enum, 
                            self.DEFAULT_CONFIGS[Environment.DEVELOPMENT]
                        )
                
                # Fill in missing environments with defaults
                for env in Environment:
                    if env not in configs:
                        configs[env] = self.DEFAULT_CONFIGS.get(env, self.DEFAULT_CONFIGS[Environment.DEVELOPMENT])
                
                return configs
                
            except Exception as e:
                _config_log.warning(f"Failed to load logging config from {self.config_file}: {e}")
                _config_log.exception("Exception details:")  # Log full traceback
                return self.DEFAULT_CONFIGS
        return self.DEFAULT_CONFIGS
    
    @log_function(log_args=True)
    def _parse_environment_config(self, env: Environment, data: Dict) -> EnvironmentConfig:
        """Parse YAML data into EnvironmentConfig object"""
        # Start with defaults for this environment
        default_config = self.DEFAULT_CONFIGS.get(env, self.DEFAULT_CONFIGS[Environment.DEVELOPMENT])
        
        # Parse log level
        log_level_str = data.get('log_level', default_config.log_level.value)
        log_level = LogLevel[log_level_str.upper()] if hasattr(LogLevel, log_level_str.upper()) else default_config.log_level
        
        # Parse retention policy
        retention_data = data.get('retention', {})
        retention = RetentionPolicy(
            app_logs_days=retention_data.get('app_logs_days', default_config.retention.app_logs_days),
            audit_logs_days=retention_data.get('audit_logs_days', default_config.retention.audit_logs_days),
            security_logs_days=retention_data.get('security_logs_days', default_config.retention.security_logs_days),
            performance_logs_days=retention_data.get('performance_logs_days', default_config.retention.performance_logs_days),
            max_file_size_mb=retention_data.get('max_file_size_mb', default_config.retention.max_file_size_mb),
            backup_count=retention_data.get('backup_count', default_config.retention.backup_count)
        )
        
        # Parse sampling config
        sampling_data = data.get('sampling', {})
        sampling = SamplingConfig(
            enabled=sampling_data.get('enabled', default_config.sampling.enabled),
            sample_rate=sampling_data.get('sample_rate', default_config.sampling.sample_rate),
            debug_sample_rate=sampling_data.get('debug_sample_rate', default_config.sampling.debug_sample_rate),
            always_log_errors=sampling_data.get('always_log_errors', default_config.sampling.always_log_errors)
        )
        
        # Parse SIEM config
        siem_data = data.get('siem', {})
        siem = SIEMConfig(
            enabled=siem_data.get('enabled', default_config.siem.enabled),
            provider=siem_data.get('provider', default_config.siem.provider),
            endpoint=siem_data.get('endpoint', default_config.siem.endpoint),
            api_key=siem_data.get('api_key', default_config.siem.api_key),
            index_name=siem_data.get('index_name', default_config.siem.index_name),
            batch_size=siem_data.get('batch_size', default_config.siem.batch_size),
            flush_interval_seconds=siem_data.get('flush_interval_seconds', default_config.siem.flush_interval_seconds)
        )
        
        # Parse alert config
        alert_data = data.get('alerts', {})
        alerts = AlertConfig(
            error_rate_threshold=alert_data.get('error_rate_threshold', default_config.alerts.error_rate_threshold),
            critical_alert_enabled=alert_data.get('critical_alert_enabled', default_config.alerts.critical_alert_enabled),
            alert_webhook_url=alert_data.get('alert_webhook_url', default_config.alerts.alert_webhook_url),
            alert_email=alert_data.get('alert_email', default_config.alerts.alert_email)
        )
        
        # Parse security config
        security_data = data.get('security', {})
        security = SecurityConfig(
            log_auth_attempts=security_data.get('log_auth_attempts', default_config.security.log_auth_attempts),
            log_auth_failures=security_data.get('log_auth_failures', default_config.security.log_auth_failures),
            log_privilege_escalation=security_data.get('log_privilege_escalation', default_config.security.log_privilege_escalation),
            log_data_access=security_data.get('log_data_access', default_config.security.log_data_access),
            mask_sensitive_data=security_data.get('mask_sensitive_data', default_config.security.mask_sensitive_data),
            sensitive_fields=security_data.get('sensitive_fields', default_config.security.sensitive_fields)
        )
        
        # Parse performance config
        perf_data = data.get('performance', {})
        performance = PerformanceConfig(
            log_slow_operations=perf_data.get('log_slow_operations', default_config.performance.log_slow_operations),
            slow_operation_threshold_ms=perf_data.get('slow_operation_threshold_ms', default_config.performance.slow_operation_threshold_ms),
            log_all_operations=perf_data.get('log_all_operations', default_config.performance.log_all_operations),
            track_memory_usage=perf_data.get('track_memory_usage', default_config.performance.track_memory_usage),
            track_cpu_usage=perf_data.get('track_cpu_usage', default_config.performance.track_cpu_usage)
        )
        
        # Construct final config
        return EnvironmentConfig(
            environment=env,
            log_level=log_level,
            console_output=data.get('console_output', default_config.console_output),
            file_output=data.get('file_output', default_config.file_output),
            json_format=data.get('json_format', default_config.json_format),
            retention=retention,
            sampling=sampling,
            siem=siem,
            alerts=alerts,
            security=security,
            performance=performance
        )
    
    @log_function(log_args=True, log_result=True)
    def get_config(self, environment: Optional[str] = None) -> EnvironmentConfig:
        """Get configuration for specific environment"""
        if environment is None:
            environment = os.getenv('TEST_ENV', 'development')
        
        # Handle both Environment enum and string
        if isinstance(environment, Environment):
            env_enum = environment
        else:
            env_enum = self._parse_environment(environment)
        
        return self.configs.get(env_enum, self.DEFAULT_CONFIGS[Environment.DEVELOPMENT])
    
    @log_function(log_args=True, log_result=True)
    def _parse_environment(self, env_str: str) -> Environment:
        """Parse environment string to enum"""
        env_map = {
            'dev': Environment.DEVELOPMENT,
            'development': Environment.DEVELOPMENT,
            'test': Environment.TESTING,
            'testing': Environment.TESTING,
            'qa': Environment.TESTING,
            'stage': Environment.STAGING,
            'staging': Environment.STAGING,
            'prod': Environment.PRODUCTION,
            'production': Environment.PRODUCTION
        }
        return env_map.get(env_str.lower(), Environment.DEVELOPMENT)
    
    @log_function(log_args=True, log_timing=True)
    def save_config_template(self, output_path: Optional[Path] = None):
        """Save configuration template to YAML"""
        output_path = output_path or Path("config/logging_config.template.yaml")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        template = {
            'environments': {
                'development': {
                    'log_level': 'DEBUG',
                    'console_output': True,
                    'file_output': True,
                    'json_format': False,
                    'retention': {
                        'app_logs_days': 7,
                        'audit_logs_days': 30,
                        'max_file_size_mb': 50
                    },
                    'sampling': {
                        'enabled': False,
                        'sample_rate': 1.0
                    },
                    'siem': {
                        'enabled': False,
                        'provider': 'elk'
                    },
                    'security': {
                        'mask_sensitive_data': True,
                        'log_auth_attempts': True
                    }
                },
                'production': {
                    'log_level': 'WARNING',
                    'console_output': False,
                    'file_output': True,
                    'json_format': True,
                    'retention': {
                        'app_logs_days': 90,
                        'audit_logs_days': 365,
                        'max_file_size_mb': 100
                    },
                    'sampling': {
                        'enabled': True,
                        'sample_rate': 0.1
                    },
                    'siem': {
                        'enabled': True,
                        'provider': 'datadog',
                        'endpoint': 'https://your-siem-endpoint.com'
                    }
                }
            }
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(template, f, default_flow_style=False)
        
        _config_log.info(f"Configuration template saved to: {output_path}")


# Singleton instance
_config_manager = None

@log_function(log_args=True, log_result=True)
def get_logging_config(environment: Optional[str] = None) -> EnvironmentConfig:
    """Get logging configuration for environment"""
    global _config_manager
    if _config_manager is None:
        _config_manager = LoggingConfigManager()
    return _config_manager.get_config(environment)


__all__ = [
    'Environment',
    'LogLevel',
    'EnvironmentConfig',
    'LoggingConfigManager',
    'get_logging_config',
    'RetentionPolicy',
    'SamplingConfig',
    'SIEMConfig',
    'AlertConfig',
    'SecurityConfig',
    'PerformanceConfig'
]
