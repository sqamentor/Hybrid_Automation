"""Protocol Interfaces Package.

This module defines Protocol classes for interface contracts across the framework. Protocols enable
structural subtyping (duck typing) with type safety.
"""

from framework.protocols.automation_protocols import (
    ActionPerformer,
    AutomationEngine,
    PageObject,
    TestDataProvider,
)
from framework.protocols.base_protocols import (
    AsyncExecutable,
    Configurable,
    Executable,
    LifecycleManaged,
    Reportable,
    Validatable,
)
from framework.protocols.config_protocols import (
    ConfigProvider,
    EnvironmentProvider,
    SecretProvider,
)
from framework.protocols.reporting_protocols import (
    ArtifactStorage,
    MetricsCollector,
    ReportGenerator,
)

__all__ = [
    # Base protocols
    "Configurable",
    "Executable",
    "AsyncExecutable",
    "Reportable",
    "Validatable",
    "LifecycleManaged",
    # Automation protocols
    "AutomationEngine",
    "PageObject",
    "TestDataProvider",
    "ActionPerformer",
    # Config protocols
    "ConfigProvider",
    "EnvironmentProvider",
    "SecretProvider",
    # Reporting protocols
    "ReportGenerator",
    "MetricsCollector",
    "ArtifactStorage",
]
