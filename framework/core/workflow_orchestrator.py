"""
Workflow Orchestrator - Cross-Engine Test Workflow Management

Sequences multi-step workflows across Selenium and Playwright engines.
Handles automatic session transfer, error recovery, and workflow state management.

Author: Principal QA Architect
Date: January 31, 2026
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from framework.auth.auth_service import AuthenticationService
from framework.core.session_manager import SessionData, SessionManager
from framework.observability import log_function, log_async_function

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Workflow step execution status"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class EngineType(Enum):
    """Engine types"""

    SELENIUM = "selenium"
    PLAYWRIGHT = "playwright"
    PLAYWRIGHT_ASYNC = "playwright_async"


class OnFailureStrategy(Enum):
    """What to do when a step fails"""

    STOP = "stop"  # Stop entire workflow
    CONTINUE = "continue"  # Continue to next step
    RETRY = "retry"  # Retry failed step


@dataclass
class WorkflowStep:
    """
    A single step in a workflow

    Attributes:
        name: Human-readable step name
        engine_type: Which engine to use (selenium/playwright)
        action: Callable to execute (receives engine instance)
        requires_session: Whether session must be transferred before this step
        on_failure: What to do if step fails
        timeout: Max execution time in seconds
        retry_count: How many times to retry on failure
        metadata: Additional step metadata
    """

    name: str
    engine_type: EngineType
    action: Callable[[Any], Any]  # Receives engine instance
    requires_session: bool = True
    on_failure: OnFailureStrategy = OnFailureStrategy.STOP
    timeout: int = 60
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Execution state (populated during execution)
    status: StepStatus = StepStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    result: Any = None


@dataclass
class Workflow:
    """
    Multi-step cross-engine workflow

    Attributes:
        name: Workflow name
        description: Workflow description
        steps: List of workflow steps
        session_data: Current session data (populated during execution)
        metadata: Additional workflow metadata
    """

    name: str
    description: str = ""
    steps: List[WorkflowStep] = field(default_factory=list)
    session_data: Optional[SessionData] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowOrchestrator:
    """
    Orchestrates multi-step workflows across engines

    Features:
    - Execute workflows with Selenium and Playwright steps
    - Automatic session transfer between engines
    - Error recovery and retry logic
    - Workflow state tracking
    - Detailed execution logging

    Example:
        orchestrator = WorkflowOrchestrator(auth_service, session_manager)

        workflow = orchestrator.define_workflow(
            name="SSO to CallCenter to PatientIntake",
            description="Complete cross-engine workflow"
        )

        orchestrator.add_step(
            workflow,
            name="SSO Login",
            engine_type=EngineType.SELENIUM,
            action=lambda driver: auth_service.authenticate_sso(...)
        )

        orchestrator.add_step(
            workflow,
            name="CallCenter Operations",
            engine_type=EngineType.PLAYWRIGHT,
            action=lambda page: callcenter_page.navigate_and_verify(...),
            requires_session=True
        )

        result = orchestrator.execute_workflow_sync(workflow, engines)
    """

    def __init__(
        self,
        auth_service: Optional[AuthenticationService] = None,
        session_manager: Optional[SessionManager] = None,
    ):
        self.auth_service = auth_service or AuthenticationService()
        self.session_manager = session_manager or SessionManager()
        self.logger = logger
        self._active_workflow: Optional[Workflow] = None

    # ========================================================================
    # WORKFLOW DEFINITION
    # ========================================================================

    @log_function(log_timing=True)
    def define_workflow(
        self, name: str, description: str = "", metadata: Optional[Dict[str, Any]] = None
    ) -> Workflow:
        """
        Create a new workflow definition

        Args:
            name: Workflow name
            description: Workflow description
            metadata: Additional metadata

        Returns:
            Workflow instance
        """
        workflow = Workflow(name=name, description=description, metadata=metadata or {})

        self.logger.info(f"📋 Workflow defined: {name}")
        return workflow

    @log_function(log_timing=True)
    def add_step(
        self,
        workflow: Workflow,
        name: str,
        engine_type: Union[EngineType, str],
        action: Callable,
        requires_session: bool = True,
        on_failure: Union[OnFailureStrategy, str] = OnFailureStrategy.STOP,
        timeout: int = 60,
        retry_count: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WorkflowStep:
        """
        Add a step to a workflow

        Args:
            workflow: Target workflow
            name: Step name
            engine_type: 'selenium', 'playwright', or EngineType enum
            action: Callable that receives engine instance
            requires_session: Whether to transfer session before step
            on_failure: What to do if step fails
            timeout: Max execution time
            retry_count: How many retries on failure
            metadata: Additional metadata

        Returns:
            Created WorkflowStep
        """
        # Convert string to enum if needed
        if isinstance(engine_type, str):
            engine_type = EngineType[engine_type.upper()]

        if isinstance(on_failure, str):
            on_failure = OnFailureStrategy[on_failure.upper()]

        step = WorkflowStep(
            name=name,
            engine_type=engine_type,
            action=action,
            requires_session=requires_session,
            on_failure=on_failure,
            timeout=timeout,
            retry_count=retry_count,
            metadata=metadata or {},
        )

        workflow.steps.append(step)
        self.logger.info(f"  ➕ Added step {len(workflow.steps)}: {name} ({engine_type.value})")

        return step

    # ========================================================================
    # WORKFLOW EXECUTION (SYNC)
    # ========================================================================

    @log_function(log_timing=True)
    def execute_workflow_sync(self, workflow: Workflow, engines: Dict[str, Any]) -> bool:
        """
        Execute workflow synchronously

        Args:
            workflow: Workflow to execute
            engines: {
                'selenium': WebDriver instance,
                'playwright': Playwright Page instance (sync)
            }

        Returns:
            True if workflow completed successfully
        """
        self.logger.info(f"🚀 Starting workflow: {workflow.name}")
        self.logger.info(f"   Description: {workflow.description}")
        self.logger.info(f"   Total steps: {len(workflow.steps)}")

        self._active_workflow = workflow

        try:
            for idx, step in enumerate(workflow.steps, 1):
                self.logger.info(f"\n{'='*80}")
                self.logger.info(f"STEP {idx}/{len(workflow.steps)}: {step.name}")
                self.logger.info(f"{'='*80}")

                success = self._execute_step_sync(step, workflow, engines)

                if not success:
                    if step.on_failure == OnFailureStrategy.STOP:
                        self.logger.error(f"❌ Workflow stopped at step {idx}: {step.name}")
                        return False
                    elif step.on_failure == OnFailureStrategy.CONTINUE:
                        self.logger.warning(f"⚠️ Step {idx} failed but continuing: {step.name}")
                        continue

            self.logger.info(f"\n{'='*80}")
            self.logger.info(f"✅ Workflow completed successfully: {workflow.name}")
            self.logger.info(f"{'='*80}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Workflow execution failed: {e}")
            return False

        finally:
            self._active_workflow = None

    def _execute_step_sync(
        self, step: WorkflowStep, workflow: Workflow, engines: Dict[str, Any]
    ) -> bool:
        """Execute a single step (sync)"""
        step.status = StepStatus.RUNNING
        step.start_time = time.time()

        try:
            # Get appropriate engine
            if step.engine_type == EngineType.SELENIUM:
                engine = engines.get("selenium")
                if not engine:
                    raise ValueError("Selenium engine not provided")
            elif step.engine_type == EngineType.PLAYWRIGHT:
                engine = engines.get("playwright")
                if not engine:
                    raise ValueError("Playwright engine not provided")
            else:
                raise ValueError(f"Unsupported engine type: {step.engine_type}")

            self.logger.info(f"   Engine: {step.engine_type.value}")
            self.logger.info(f"   Timeout: {step.timeout}s")
            self.logger.info(f"   Requires session: {step.requires_session}")

            # Transfer session if needed
            if step.requires_session and workflow.session_data:
                self.logger.info(f"   🔄 Transferring session to {step.engine_type.value}...")

                if step.engine_type == EngineType.SELENIUM:
                    # Inject to Selenium
                    success = self.session_manager.inject_session_to_selenium(
                        engine, workflow.session_data
                    )
                    if not success:
                        raise ValueError("Failed to inject session to Selenium")

                elif step.engine_type == EngineType.PLAYWRIGHT:
                    # Inject to Playwright (sync)
                    success = self.session_manager.inject_session_to_playwright_sync(
                        engine, workflow.session_data
                    )
                    if not success:
                        raise ValueError("Failed to inject session to Playwright")

                self.logger.info("   ✅ Session transferred successfully")

            # Execute step action
            self.logger.info(f"   ▶️ Executing step action...")
            result = step.action(engine)
            step.result = result

            # If this was an auth step, capture session
            if step.engine_type == EngineType.SELENIUM:
                # Try to extract session after execution
                try:
                    session_data = self.session_manager.extract_session_from_selenium(engine)
                    if session_data:
                        workflow.session_data = session_data
                        self.logger.info("   💾 Session captured from Selenium")
                except Exception as e:
                    self.logger.warning(f"   ⚠️ Could not extract session: {e}")

            step.status = StepStatus.SUCCESS
            step.end_time = time.time()
            duration = step.end_time - step.start_time

            self.logger.info(f"   ✅ Step completed successfully in {duration:.2f}s")
            return True

        except Exception as e:
            step.status = StepStatus.FAILED
            step.end_time = time.time()
            step.error_message = str(e)

            self.logger.error(f"   ❌ Step failed: {e}")

            # Retry logic
            if step.retry_count > 0:
                self.logger.info(f"   🔄 Retrying step (attempts remaining: {step.retry_count})...")
                step.retry_count -= 1
                time.sleep(2)  # Brief delay before retry
                return self._execute_step_sync(step, workflow, engines)

            return False

    # ========================================================================
    # WORKFLOW EXECUTION (ASYNC)
    # ========================================================================

    @log_async_function(log_timing=True)
    async def execute_workflow_async(self, workflow: Workflow, engines: Dict[str, Any]) -> bool:
        """
        Execute workflow asynchronously

        Args:
            workflow: Workflow to execute
            engines: {
                'selenium': WebDriver instance,
                'playwright': Playwright Page instance (async)
            }

        Returns:
            True if workflow completed successfully
        """
        self.logger.info(f"🚀 Starting workflow (async): {workflow.name}")
        self.logger.info(f"   Total steps: {len(workflow.steps)}")

        self._active_workflow = workflow

        try:
            for idx, step in enumerate(workflow.steps, 1):
                self.logger.info(f"\n{'='*80}")
                self.logger.info(f"STEP {idx}/{len(workflow.steps)}: {step.name}")
                self.logger.info(f"{'='*80}")

                success = await self._execute_step_async(step, workflow, engines)

                if not success:
                    if step.on_failure == OnFailureStrategy.STOP:
                        self.logger.error(f"❌ Workflow stopped at step {idx}")
                        return False
                    elif step.on_failure == OnFailureStrategy.CONTINUE:
                        self.logger.warning(f"⚠️ Step {idx} failed but continuing")
                        continue

            self.logger.info(f"✅ Workflow completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"❌ Workflow execution failed: {e}")
            return False

        finally:
            self._active_workflow = None

    async def _execute_step_async(
        self, step: WorkflowStep, workflow: Workflow, engines: Dict[str, Any]
    ) -> bool:
        """Execute a single step (async)"""
        step.status = StepStatus.RUNNING
        step.start_time = time.time()

        try:
            # Get engine
            if step.engine_type == EngineType.SELENIUM:
                engine = engines.get("selenium")
            elif step.engine_type == EngineType.PLAYWRIGHT_ASYNC:
                engine = engines.get("playwright")
            else:
                raise ValueError(f"Unsupported engine type: {step.engine_type}")

            # Transfer session if needed
            if step.requires_session and workflow.session_data:
                self.logger.info(f"   🔄 Transferring session...")

                if step.engine_type == EngineType.PLAYWRIGHT_ASYNC:
                    success = await self.session_manager.inject_session_to_playwright(
                        engine, workflow.session_data
                    )
                    if not success:
                        raise ValueError("Failed to inject session")

            # Execute step action
            self.logger.info(f"   ▶️ Executing...")

            if asyncio.iscoroutinefunction(step.action):
                result = await step.action(engine)
            else:
                result = step.action(engine)

            step.result = result
            step.status = StepStatus.SUCCESS
            step.end_time = time.time()

            self.logger.info(f"   ✅ Step completed")
            return True

        except Exception as e:
            step.status = StepStatus.FAILED
            step.end_time = time.time()
            step.error_message = str(e)
            self.logger.error(f"   ❌ Step failed: {e}")
            return False

    # ========================================================================
    # WORKFLOW QUERIES
    # ========================================================================

    @log_function(log_timing=True)
    def get_workflow_status(self, workflow: Workflow) -> Dict[str, Any]:
        """Get workflow execution status"""
        total_steps = len(workflow.steps)
        completed_steps = sum(1 for step in workflow.steps if step.status == StepStatus.SUCCESS)
        failed_steps = sum(1 for step in workflow.steps if step.status == StepStatus.FAILED)

        return {
            "name": workflow.name,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "in_progress": self._active_workflow == workflow,
            "success_rate": (completed_steps / total_steps * 100) if total_steps > 0 else 0,
        }

    @log_function(log_timing=True)
    def get_step_details(self, step: WorkflowStep) -> Dict[str, Any]:
        """Get detailed step information"""
        duration = None
        if step.start_time and step.end_time:
            duration = step.end_time - step.start_time

        return {
            "name": step.name,
            "status": step.status.value,
            "engine_type": step.engine_type.value,
            "duration": duration,
            "error_message": step.error_message,
            "metadata": step.metadata,
        }

    @log_function(log_timing=True)
    def reset_workflow(self, workflow: Workflow) -> None:
        """Reset workflow to initial state"""
        for step in workflow.steps:
            step.status = StepStatus.PENDING
            step.start_time = None
            step.end_time = None
            step.error_message = None
            step.result = None

        workflow.session_data = None
        self.logger.info(f"♻️ Workflow reset: {workflow.name}")
