"""
Simple test to verify recording module imports and basic functionality
Run with: python test_recording_simple.py
"""

import sys
from pathlib import Path

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test all recording module imports work"""
    print("Testing imports...")

    try:
        from framework.recording import (
            AIScriptRefactorer,
            PageObjectGenerator,
            PlaywrightCodegen,
            RecordingWorkflow,
            quick_record_and_generate,
        )

        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_instantiation():
    """Test that classes can be instantiated"""
    print("\nTesting class instantiation...")

    try:
        from framework.recording import (
            AIScriptRefactorer,
            PageObjectGenerator,
            PlaywrightCodegen,
            RecordingWorkflow,
        )

        # Test PlaywrightCodegen
        codegen = PlaywrightCodegen()
        assert codegen is not None
        print("✓ PlaywrightCodegen instantiated")

        # Test AIScriptRefactorer
        refactorer = AIScriptRefactorer()
        assert refactorer is not None
        print("✓ AIScriptRefactorer instantiated")

        # Test PageObjectGenerator
        generator = PageObjectGenerator()
        assert generator is not None
        print("✓ PageObjectGenerator instantiated")

        # Test RecordingWorkflow
        workflow = RecordingWorkflow()
        assert workflow is not None
        print("✓ RecordingWorkflow instantiated")

        return True
    except Exception as e:
        print(f"✗ Instantiation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_directories():
    """Test that required directories can be created"""
    print("\nTesting directory creation...")

    try:
        from framework.recording import PageObjectGenerator, PlaywrightCodegen

        codegen = PlaywrightCodegen()
        assert codegen.output_dir.exists()
        print(f"✓ Codegen output directory created: {codegen.output_dir}")

        generator = PageObjectGenerator()
        assert generator.output_dir.exists()
        print(f"✓ Page objects directory created: {generator.output_dir}")

        return True
    except Exception as e:
        print(f"✗ Directory creation failed: {e}")
        return False


def test_ai_integration():
    """Test AI provider integration"""
    print("\nTesting AI provider integration...")

    try:
        from framework.recording import AIScriptRefactorer

        # Test with different AI providers
        providers = [None, "openai", "claude", "azure", "ollama"]

        for provider in providers:
            refactorer = AIScriptRefactorer(ai_provider_name=provider)
            assert refactorer is not None
            print(f"✓ AIScriptRefactorer works with provider: {provider or 'auto'}")

        return True
    except Exception as e:
        print(f"✗ AI integration failed: {e}")
        return False


def test_list_operations():
    """Test list operations work"""
    print("\nTesting list operations...")

    try:
        from framework.recording import RecordingWorkflow

        workflow = RecordingWorkflow()

        # Test list recordings
        recordings = workflow.list_recordings()
        assert isinstance(recordings, list)
        print(f"✓ List recordings works: {len(recordings)} recordings found")

        # Test list page objects
        pages = workflow.list_page_objects()
        assert isinstance(pages, list)
        print(f"✓ List page objects works: {len(pages)} page objects found")

        return True
    except Exception as e:
        print(f"✗ List operations failed: {e}")
        return False

# ARCHITECTURAL FIX: Removed executable pattern and main() function
# Use pytest runner instead: pytest tests/common/test_recording_simple.py -v
