"""
Base Protocol Interfaces

Fundamental protocols that define common contracts across the framework.
"""

from typing import Any, Dict, List, Protocol, runtime_checkable


@runtime_checkable
class Configurable(Protocol):
    """Protocol for objects that can be configured"""

    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the object with given configuration"""
        ...

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        ...


@runtime_checkable
class Executable(Protocol):
    """Protocol for objects that can be executed"""

    def execute(self, *args, **kwargs) -> Any:
        """Execute the object's main operation"""
        ...


@runtime_checkable
class AsyncExecutable(Protocol):
    """Protocol for objects that can be executed asynchronously"""

    async def execute(self, *args, **kwargs) -> Any:
        """Execute the object's main operation asynchronously"""
        ...


@runtime_checkable
class Reportable(Protocol):
    """Protocol for objects that can generate reports"""

    def generate_report(self) -> Dict[str, Any]:
        """Generate a report of current state"""
        ...


@runtime_checkable
class Validatable(Protocol):
    """Protocol for objects that can be validated"""

    def validate(self) -> bool:
        """Validate the object's state"""
        ...

    def get_errors(self) -> List[str]:
        """Get validation errors"""
        ...


@runtime_checkable
class LifecycleManaged(Protocol):
    """Protocol for objects with lifecycle management"""

    def initialize(self) -> None:
        """Initialize the object"""
        ...

    def start(self) -> None:
        """Start the object"""
        ...

    def stop(self) -> None:
        """Stop the object"""
        ...

    def cleanup(self) -> None:
        """Cleanup resources"""
        ...
