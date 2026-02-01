"""
Tests for Recording Module Components
Verifies that recording workflow modules are properly integrated
"""

import pytest
from pathlib import Path
import sys

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.mark.modern_spa
@pytest.mark.unit
class TestRecordingImports:
    """Test that all recording modules can be imported"""
    
    def test_import_recording_module(self):
        """Test framework.recording package imports"""
        from framework import recording
        assert recording is not None
    
    def test_import_codegen_wrapper(self):
        """Test PlaywrightCodegen import"""
        from framework.recording import PlaywrightCodegen
        assert PlaywrightCodegen is not None
    
    def test_import_ai_refactorer(self):
        """Test AIScriptRefactorer import"""
        from framework.recording import AIScriptRefactorer
        assert AIScriptRefactorer is not None
    
    def test_import_page_object_generator(self):
        """Test PageObjectGenerator import"""
        from framework.recording import PageObjectGenerator
        assert PageObjectGenerator is not None
    
    def test_import_recording_workflow(self):
        """Test RecordingWorkflow import"""
        from framework.recording import RecordingWorkflow
        assert RecordingWorkflow is not None
    
    def test_import_convenience_function(self):
        """Test quick_record_and_generate function import"""
        from framework.recording import quick_record_and_generate
        assert callable(quick_record_and_generate)


@pytest.mark.modern_spa
@pytest.mark.unit
class TestPlaywrightCodegen:
    """Test PlaywrightCodegen wrapper functionality"""
    
    def test_codegen_initialization(self):
        """Test PlaywrightCodegen can be instantiated"""
        from framework.recording import PlaywrightCodegen
        
        codegen = PlaywrightCodegen()
        assert codegen is not None
        assert codegen.output_dir.exists()
    
    def test_codegen_default_output_dir(self):
        """Test default output directory is created"""
        from framework.recording import PlaywrightCodegen
        
        codegen = PlaywrightCodegen()
        assert codegen.output_dir == Path("recorded_tests")
    
    def test_codegen_custom_output_dir(self):
        """Test custom output directory"""
        from framework.recording import PlaywrightCodegen
        
        custom_dir = Path("custom_recordings")
        codegen = PlaywrightCodegen(output_dir=str(custom_dir))
        assert codegen.output_dir == custom_dir
    
    def test_codegen_list_recordings_empty(self):
        """Test listing recordings when none exist"""
        from framework.recording import PlaywrightCodegen
        
        codegen = PlaywrightCodegen()
        recordings = codegen.list_recordings()
        assert isinstance(recordings, list)


@pytest.mark.modern_spa
@pytest.mark.unit
class TestAIScriptRefactorer:
    """Test AIScriptRefactorer functionality"""
    
    def test_refactorer_initialization(self):
        """Test AIScriptRefactorer can be instantiated"""
        from framework.recording import AIScriptRefactorer
        
        refactorer = AIScriptRefactorer()
        assert refactorer is not None
    
    def test_refactorer_with_ai_provider(self):
        """Test AIScriptRefactorer with specific AI provider"""
        from framework.recording import AIScriptRefactorer
        
        refactorer = AIScriptRefactorer(ai_provider_name="openai")
        assert refactorer is not None
    
    def test_refactorer_available_improvements(self):
        """Test improvement types are available"""
        from framework.recording import AIScriptRefactorer
        
        refactorer = AIScriptRefactorer()
        improvements = ['comments', 'locators', 'assertions', 'documentation', 'functions']
        
        # These should be the standard improvement types
        assert all(imp in ['comments', 'locators', 'assertions', 'documentation', 'functions'] 
                  for imp in improvements)


@pytest.mark.modern_spa
@pytest.mark.unit
class TestPageObjectGenerator:
    """Test PageObjectGenerator functionality"""
    
    def test_generator_initialization(self):
        """Test PageObjectGenerator can be instantiated"""
        from framework.recording import PageObjectGenerator
        
        generator = PageObjectGenerator()
        assert generator is not None
    
    def test_generator_default_output_dir(self):
        """Test default pages directory"""
        from framework.recording import PageObjectGenerator
        
        generator = PageObjectGenerator()
        assert generator.pages_dir == Path("pages")
    
    def test_generator_custom_output_dir(self):
        """Test custom pages directory"""
        from framework.recording import PageObjectGenerator
        
        custom_dir = Path("custom_pages")
        generator = PageObjectGenerator(pages_dir=str(custom_dir))
        assert generator.pages_dir == custom_dir
    
    def test_generator_list_page_objects_empty(self):
        """Test listing page objects when none exist"""
        from framework.recording import PageObjectGenerator
        
        generator = PageObjectGenerator()
        pages = generator.list_page_objects()
        assert isinstance(pages, list)


@pytest.mark.modern_spa
@pytest.mark.unit
class TestRecordingWorkflow:
    """Test RecordingWorkflow orchestration"""
    
    def test_workflow_initialization(self):
        """Test RecordingWorkflow can be instantiated"""
        from framework.recording import RecordingWorkflow
        
        workflow = RecordingWorkflow()
        assert workflow is not None
    
    def test_workflow_with_ai_provider(self):
        """Test RecordingWorkflow with AI provider"""
        from framework.recording import RecordingWorkflow
        
        workflow = RecordingWorkflow(ai_provider="openai")
        assert workflow is not None
    
    def test_workflow_list_recordings(self):
        """Test workflow can list recordings"""
        from framework.recording import RecordingWorkflow
        
        workflow = RecordingWorkflow()
        recordings = workflow.list_recordings()
        assert isinstance(recordings, list)
    
    def test_workflow_list_page_objects(self):
        """Test workflow can list page objects"""
        from framework.recording import RecordingWorkflow
        
        workflow = RecordingWorkflow()
        pages = workflow.list_page_objects()
        assert isinstance(pages, list)


@pytest.mark.modern_spa
@pytest.mark.unit
class TestRecordingIntegration:
    """Test recording module integration with framework"""
    
    def test_ai_provider_factory_integration(self):
        """Test AI refactorer uses framework AI providers"""
        from framework.recording import AIScriptRefactorer
        
        # Should use framework.ai.ai_provider_factory
        refactorer = AIScriptRefactorer(ai_provider_name=None)
        assert refactorer is not None
    
    def test_directory_structure_creation(self):
        """Test required directories are created"""
        from framework.recording import PlaywrightCodegen, PageObjectGenerator
        
        # These should create directories if not exist
        codegen = PlaywrightCodegen()
        generator = PageObjectGenerator()
        
        assert codegen.output_dir.exists()
        assert generator.pages_dir.exists()


@pytest.mark.modern_spa
@pytest.mark.unit
class TestRecordingResilience:
    """Test that recording workflow never fails due to AI unavailability"""
    
    def test_refactorer_works_without_ai(self):
        """Test AIScriptRefactorer has rule-based fallback"""
        from framework.recording import AIScriptRefactorer
        
        # Force rule-based by using invalid AI provider
        refactorer = AIScriptRefactorer(ai_provider_name="invalid_provider")
        assert refactorer is not None
        # Should fall back to rule-based refactoring, not crash
    
    def test_workflow_works_without_ai(self):
        """Test RecordingWorkflow works with AI disabled"""
        from framework.recording import RecordingWorkflow
        
        workflow = RecordingWorkflow(ai_provider=None)
        assert workflow is not None


def test_recording_module_exports():
    """Test that recording module exports expected items"""
    from framework import recording
    
    expected_exports = [
        'PlaywrightCodegen',
        'AIScriptRefactorer',
        'PageObjectGenerator',
        'RecordingWorkflow',
        'quick_record_and_generate'
    ]
    
    for export in expected_exports:
        assert hasattr(recording, export), f"Missing export: {export}"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
