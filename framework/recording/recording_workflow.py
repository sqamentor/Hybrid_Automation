"""
Recording Workflow Orchestrator
Manages the complete recording → refactoring → page object → API integration workflow
WITH PROJECT-AWARE ORGANIZATION AND ENVIRONMENT DETECTION
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from framework.core.project_manager import ProjectManager, get_project_manager

from .ai_refactorer import AIScriptRefactorer
from .codegen_wrapper import PlaywrightCodegen
from .page_object_generator import PageObjectGenerator


class RecordingWorkflow:
    """
    Orchestrates the complete test recording workflow with project awareness:
    1. Detect project from URL (auto or manual)
    2. Detect environment (dev/staging/prod)
    3. Record with Playwright Codegen in project-specific directory
    4. Human review (pause)
    5. AI-assisted refactoring
    6. Generate Page Objects in project-specific directory
    7. Add API/DB orchestration hooks
    """

    def __init__(
        self,
        recordings_dir: str = "recorded_tests",
        pages_dir: str = "pages",
        ai_provider: Optional[str] = None,
        project_manager: Optional[ProjectManager] = None,
    ):
        """
        Initialize Recording Workflow

        Args:
            recordings_dir: Base directory for recorded scripts
            pages_dir: Base directory for page objects
            ai_provider: AI provider for refactoring
            project_manager: ProjectManager instance (default: singleton)
        """
        self.codegen = PlaywrightCodegen(output_dir=recordings_dir)
        self.refactorer = AIScriptRefactorer(ai_provider_name=ai_provider)
        self.page_generator = PageObjectGenerator(output_dir=pages_dir)

        self.recordings_dir = Path(recordings_dir)
        self.pages_dir = Path(pages_dir)

        # Project management
        self.project_manager = project_manager or get_project_manager()

        logger.info("Recording Workflow initialized (Project-Aware)")
        logger.info(f"  Base Recordings Dir: {self.recordings_dir}")
        logger.info(f"  Base Pages Dir: {self.pages_dir}")
        logger.info(f"  AI Enabled: {self.refactorer.enabled}")
        logger.info(f"  Projects Available: {len(self.project_manager.projects)}")

    def quick_workflow(
        self,
        url: str,
        test_name: str,
        browser: str = "chromium",
        auto_refactor: bool = True,
        generate_page_object: bool = True,
        mobile: bool = False,
        manual_project: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Quick complete workflow with PROJECT AWARENESS

        Args:
            url: Starting URL
            test_name: Name for the test (or feature description)
            browser: Browser to use
            auto_refactor: Automatically refactor after recording
            generate_page_object: Generate page object
            mobile: Use mobile device
            manual_project: Manual project override (auto-detect if None)
            environment: Manual environment override (auto-detect if None)

        Returns:
            Dict with workflow results including project info
        """
        logger.info(f"Starting quick workflow for: {test_name}")
        logger.info(f"  URL: {url}")

        # ===============================================================
        # PROJECT DETECTION & SETUP
        # ===============================================================
        try:
            project_info = self.project_manager.get_project_info(
                url=url, manual_project=manual_project, environment=environment
            )

            project_name = project_info["project"]
            env_name = project_info["environment"]
            paths = project_info["paths"]

            print("\n" + "=" * 80)
            print("🎯 PROJECT & ENVIRONMENT DETECTED")
            print("=" * 80)
            print(f"  Project:     {project_name.upper()}")
            print(f"  Environment: {env_name.upper()}")
            print(f"  Recordings:  {paths['recorded_tests']}")
            print(f"  Pages:       {paths['pages']}")
            print("=" * 80)

            # Ensure project structure exists
            self.project_manager.create_project_structure(project_name)

        except Exception as e:
            logger.error(f"Project detection failed: {e}")
            logger.warning("Falling back to default organization")
            project_name = "default"
            env_name = environment or "unknown"
            paths = {"recorded_tests": self.recordings_dir, "pages": self.pages_dir}

        workflow_results = {
            "test_name": test_name,
            "project": project_name,
            "environment": env_name,
            "paths": {k: str(v) for k, v in paths.items()},
            "steps": {},
            "status": "in_progress",
        }

        # ===============================================================
        # STEP 1: RECORD WITH PROJECT-SPECIFIC PATHS
        # ===============================================================
        print("\n" + "=" * 80)
        print("STEP 1: RECORDING WITH PLAYWRIGHT CODEGEN")
        print("=" * 80)

        # Generate intelligent filename
        recording_filename = self.project_manager.generate_recording_filename(
            project=project_name, feature=test_name
        )
        recording_path = Path(paths["recorded_tests"]) / recording_filename

        # Update codegen output directory temporarily
        original_output_dir = self.codegen.output_dir
        self.codegen.output_dir = Path(paths["recorded_tests"])

        # Use test_name parameter (quick_record doesn't accept output_file)
        recording_result = self.codegen.quick_record(
            url=url, test_name=recording_filename.replace(".py", ""), mobile=mobile
        )

        # Restore original
        self.codegen.output_dir = original_output_dir

        workflow_results["steps"]["recording"] = recording_result

        if recording_result.get("status") != "success":
            workflow_results["status"] = "failed_at_recording"
            return workflow_results

        recorded_file = recording_result.get("output_file", str(recording_path))

        # ===============================================================
        # STEP 2: HUMAN REVIEW
        # ===============================================================
        print("\n" + "=" * 80)
        print("STEP 2: HUMAN REVIEW")
        print("=" * 80)
        print(f"📝 Recorded script: {recorded_file}")
        print(f"📁 Project folder: {paths['recorded_tests']}")
        print("Review the generated script before proceeding.")
        print("You can edit it manually if needed.")

        # ===============================================================
        # STEP 3: AI REFACTORING (PROJECT-AWARE)
        # ===============================================================
        if auto_refactor:
            print("\n" + "=" * 80)
            print("STEP 3: AI-ASSISTED REFACTORING")
            print("=" * 80)

            refactor_result = self.refactorer.refactor_script(recorded_file)
            workflow_results["steps"]["refactoring"] = refactor_result

            if refactor_result.get("status") == "success":
                recorded_file = refactor_result["refactored_file"]

        # ===============================================================
        # STEP 4: GENERATE PAGE OBJECT (PROJECT-SPECIFIC)
        # ===============================================================
        if generate_page_object:
            print("\n" + "=" * 80)
            print("STEP 4: GENERATE PAGE OBJECT")
            print("=" * 80)

            # Generate page object filename
            page_filename = self.project_manager.generate_page_object_filename(test_name)
            page_path = Path(paths["pages"]) / page_filename

            # Temporarily update page generator output directory
            original_pages_dir = self.page_generator.output_dir
            self.page_generator.output_dir = Path(paths["pages"])

            page_result = self.page_generator.generate_from_script(recorded_file)

            # Restore original
            self.page_generator.output_dir = original_pages_dir

            workflow_results["steps"]["page_object"] = page_result
            workflow_results["page_object_path"] = str(page_path)

        # ===============================================================
        # STEP 5: API/DB ORCHESTRATION INFO
        # ===============================================================
        print("\n" + "=" * 80)
        print("STEP 5: API/DB ORCHESTRATION")
        print("=" * 80)
        print("To add API capture and DB validation:")
        print(f"1. Enable API interceptor in your test")
        print(f"2. Use AIValidationSuggester for API → DB mapping")
        print(f"3. See: framework/api/api_interceptor.py")

        workflow_results["status"] = "success"

        # ===============================================================
        # SUMMARY
        # ===============================================================
        self._print_workflow_summary(workflow_results)

        return workflow_results

    def full_workflow(
        self,
        url: str,
        test_name: str,
        browser: str = "chromium",
        device: Optional[str] = None,
        save_auth: bool = False,
        refactor_improvements: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Full workflow with all customization options

        Args:
            url: Starting URL
            test_name: Test name
            browser: Browser to use
            device: Device to emulate
            save_auth: Save authentication state
            refactor_improvements: List of improvements to apply

        Returns:
            Dict with workflow results
        """
        logger.info(f"Starting full workflow for: {test_name}")

        workflow_results = {
            "test_name": test_name,
            "steps": {},
            "status": "in_progress",
            "start_time": time.time(),
        }

        # Step 1: Record
        print("\n" + "=" * 80)
        print("WORKFLOW STEP 1/5: RECORDING")
        print("=" * 80)

        if save_auth:
            recording_result = self.codegen.record_with_auth(url, test_name)
        else:
            recording_result = self.codegen.start_recording(
                url=url, test_name=test_name, browser=browser, device=device
            )

        workflow_results["steps"]["recording"] = recording_result

        if recording_result.get("status") != "success":
            workflow_results["status"] = "failed_at_recording"
            workflow_results["end_time"] = time.time()
            return workflow_results

        recorded_file = recording_result["output_file"]

        # Step 2: Preview improvements
        print("\n" + "=" * 80)
        print("WORKFLOW STEP 2/5: ANALYZING SCRIPT")
        print("=" * 80)

        preview = self.refactorer.preview_improvements(recorded_file)
        workflow_results["steps"]["analysis"] = preview

        if preview.get("suggestions"):
            print("\nSuggested improvements:")
            for i, suggestion in enumerate(preview["suggestions"], 1):
                print(f"  {i}. {suggestion}")

        # Step 3: Refactor
        print("\n" + "=" * 80)
        print("WORKFLOW STEP 3/5: AI-ASSISTED REFACTORING")
        print("=" * 80)

        refactor_result = self.refactorer.refactor_script(
            recorded_file, improvements=refactor_improvements
        )
        workflow_results["steps"]["refactoring"] = refactor_result

        if refactor_result.get("status") == "success":
            recorded_file = refactor_result["refactored_file"]
            print(f"✓ Refactored script: {recorded_file}")

        # Step 4: Generate Page Object
        print("\n" + "=" * 80)
        print("WORKFLOW STEP 4/5: GENERATING PAGE OBJECT")
        print("=" * 80)

        page_result = self.page_generator.generate_from_script(recorded_file)
        workflow_results["steps"]["page_object"] = page_result

        if page_result.get("status") == "success":
            print(f"✓ Page Object: {page_result['page_class']}")
            print(f"✓ File: {page_result['page_file']}")
            print(f"\n{page_result['usage_example']}")

        # Step 5: Integration guidance
        print("\n" + "=" * 80)
        print("WORKFLOW STEP 5/5: API/DB INTEGRATION")
        print("=" * 80)

        integration_guide = self._generate_integration_guide(
            test_name, page_result.get("page_file", ""), page_result.get("page_class", "")
        )
        workflow_results["steps"]["integration"] = integration_guide
        print(integration_guide["instructions"])

        workflow_results["status"] = "success"
        workflow_results["end_time"] = time.time()
        workflow_results["duration"] = workflow_results["end_time"] - workflow_results["start_time"]

        # Final summary
        self._print_workflow_summary(workflow_results)

        return workflow_results

    def _generate_integration_guide(
        self, test_name: str, page_file: str, page_class: str
    ) -> Dict[str, str]:
        """Generate API/DB integration guide"""

        instructions = f"""
API/DB Integration Steps:

1. Enable API Interceptor in your test:
   
   from framework.api.api_interceptor import APIInterceptor
   
   def test_{test_name}(page):
       # Initialize API interceptor
       interceptor = APIInterceptor(ui_engine_type="playwright")
       interceptor.setup_interception(page)
       
       # Your test code here
       # API calls will be automatically captured

2. Add AI-powered validation suggestions:
   
   from framework.intelligence import AIValidationSuggester
   
   # After test completes
   suggester = AIValidationSuggester()
   for request in interceptor.captured_requests:
       # Get AI suggestions for DB validations
       strategy = suggester.suggest_validations(
           api_endpoint=request['url'],
           api_method=request['method'],
           api_request=request,
           api_response=interceptor.get_response(request['url'])
       )
       
       # Apply suggested validations
       for validation in strategy.suggestions:
           # Implement DB checks here
           pass

3. Use Page Object with API orchestration:
   
   from {Path(page_file).stem} import {page_class}
   
   def test_{test_name}_with_validation(page, db_connection):
       page_obj = {page_class}(page)
       interceptor = APIInterceptor(ui_engine_type="playwright")
       
       # Navigate and perform actions
       page_obj.navigate()
       # ... your test steps
       
       # Verify API → DB consistency
       # Implementation based on your DB schema

4. See examples:
   - tests/examples/test_multi_ai_providers.py
   - docs/MULTI_AI_PROVIDER_GUIDE.md
"""

        return {
            "instructions": instructions,
            "test_name": test_name,
            "page_file": page_file,
            "page_class": page_class,
        }

    def _print_workflow_summary(self, results: Dict[str, Any]):
        """Print workflow summary"""
        print("\n" + "=" * 80)
        print("WORKFLOW SUMMARY")
        print("=" * 80)
        print(f"Status: {results['status']}")
        print(f"\nCompleted Steps:")

        for step_name, step_result in results.get("steps", {}).items():
            status_icon = "✓" if step_result.get("status") == "success" else "⚠"
            print(f"  {status_icon} {step_name.title()}")

            # Print key details
            if step_name == "recording" and "output_file" in step_result:
                print(f"      File: {step_result['output_file']}")
            elif step_name == "refactoring" and "refactored_file" in step_result:
                print(f"      File: {step_result['refactored_file']}")
            elif step_name == "page_object" and "page_class" in step_result:
                print(f"      Class: {step_result['page_class']}")
                print(f"      File: {step_result['page_file']}")

        if "duration" in results:
            print(f"\nTotal Duration: {results['duration']:.2f} seconds")

        print("=" * 80 + "\n")

    def list_recordings(self) -> List[Dict[str, Any]]:
        """List all recorded tests"""
        return self.codegen.list_recordings()

    def list_page_objects(self) -> List[Dict[str, Any]]:
        """List all generated page objects"""
        return self.page_generator.list_page_objects()


# Convenience function
def quick_record_and_generate(url: str, test_name: str, mobile: bool = False) -> Dict[str, Any]:
    """
    Quick function to record and generate complete test setup

    Args:
        url: Starting URL
        test_name: Test name
        mobile: Use mobile device

    Returns:
        Workflow results
    """
    workflow = RecordingWorkflow()
    return workflow.quick_workflow(url, test_name, mobile=mobile)
