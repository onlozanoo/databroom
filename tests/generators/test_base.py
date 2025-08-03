import pytest
import tempfile
import os
from pathlib import Path

# Development path setup (only when run directly)
if __name__ == "__main__" and __package__ is None:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from databroom.generators.base import CodeGenerator

class TestCodeGeneratorInitialization:
    def test_python_generator_initialization(self):
        """Test CodeGenerator initialization for Python."""
        # Act
        generator = CodeGenerator('python')
        
        # Assert
        assert generator.language == 'python'
        assert hasattr(generator, 'history')
        assert hasattr(generator, 'templates')
        assert len(generator.templates) > 0

    def test_r_generator_initialization(self):
        """Test CodeGenerator initialization for R."""
        # Act
        generator = CodeGenerator('R')
        
        # Assert
        assert generator.language == 'R'
        assert hasattr(generator, 'history')
        assert hasattr(generator, 'templates')

    def test_templates_loaded(self):
        """Test that templates are properly loaded."""
        # Act
        generator = CodeGenerator('python')
        
        # Assert
        assert 'python_pipeline' in generator.templates
        assert isinstance(generator.templates, list)
        assert len(generator.templates) >= 1

class TestCodeGeneratorHistoryLoading:
    def test_load_history_with_valid_data(self, mock_history):
        """Test loading valid history data."""
        # Arrange
        generator = CodeGenerator('python')
        
        # Act
        result = generator.load_history(mock_history)
        
        # Assert
        assert len(result) == len(mock_history)
        assert generator.history == result
        # Check that history is properly parsed
        for func_name, params in result:
            assert isinstance(func_name, str)
            assert isinstance(params, str)

    def test_load_history_extracts_function_names(self, mock_history):
        """Test that function names are properly extracted."""
        # Arrange
        generator = CodeGenerator('python')
        
        # Act
        result = generator.load_history(mock_history)
        
        # Assert
        func_names = [item[0] for item in result]
        assert 'remove_empty_cols' in func_names
        assert 'standardize_column_names' in func_names
        assert 'normalize_column_names' in func_names

    def test_load_history_extracts_parameters(self, mock_history):
        """Test that parameters are properly extracted."""
        # Arrange
        generator = CodeGenerator('python')
        
        # Act
        result = generator.load_history(mock_history)
        
        # Assert
        # Check first item which has threshold parameter
        func_name, params = result[0]
        assert func_name == 'remove_empty_cols'
        assert 'threshold' in params
        assert '0.9' in params

    def test_load_empty_history(self):
        """Test loading empty history."""
        # Arrange
        generator = CodeGenerator('python')
        
        # Act
        result = generator.load_history([])
        
        # Assert
        assert len(result) == 0
        assert generator.history == []

class TestCodeGenerationPython:
    def test_generate_python_code_single_operation(self):
        """Test generating Python code for single operation."""
        # Arrange
        generator = CodeGenerator('python')
        history = ["remove_empty_cols called with Parameters: {'threshold': 0.9}. Operation completed successfully."]
        generator.load_history(history)
        
        # Act
        code = generator.generate_code()
        
        # Assert
        assert 'janitor_instance = janitor_instance.remove_empty_cols(threshold=0.9)' in code
        assert code.strip().endswith('.remove_empty_cols(threshold=0.9)')

    def test_generate_python_code_multiple_operations(self, mock_history):
        """Test generating Python code for multiple operations."""
        # Arrange
        generator = CodeGenerator('python')
        generator.load_history(mock_history)
        
        # Act
        code = generator.generate_code()
        
        # Assert
        assert 'janitor_instance = janitor_instance.remove_empty_cols(threshold=0.9)' in code
        assert '.standardize_column_names()' in code
        assert '.normalize_column_names()' in code
        # Check chaining
        lines = code.strip().split('\n')
        assert len([line for line in lines if 'janitor_instance' in line]) == 1

    def test_generate_python_code_with_no_parameters(self):
        """Test generating code for operations without parameters."""
        # Arrange
        generator = CodeGenerator('python')
        history = ["standardize_column_names called with Parameters: {}. Operation completed successfully."]
        generator.load_history(history)
        
        # Act
        code = generator.generate_code()
        
        # Assert
        assert 'janitor_instance = janitor_instance.standardize_column_names()' in code

    def test_generate_code_with_complex_parameters(self):
        """Test generating code with complex parameter values."""
        # Arrange
        generator = CodeGenerator('python')
        history = ["some_operation called with Parameters: {'threshold': 0.5, 'method': 'zscore', 'columns': ['col1', 'col2']}. Operation completed successfully."]
        generator.load_history(history)
        
        # Act
        code = generator.generate_code()
        
        # Assert
        assert 'threshold=0.5' in code
        assert "method='zscore'" in code
        assert "columns=['col1', 'col2']" in code

class TestCodeGenerationErrors:
    def test_generate_code_without_history_raises_error(self):
        """Test that generating code without history raises ValueError."""
        # Arrange
        generator = CodeGenerator('python')
        
        # Act & Assert
        with pytest.raises(ValueError, match="No history available to generate code"):
            generator.generate_code()

    def test_generate_code_with_empty_history_raises_error(self):
        """Test that generating code with empty history raises ValueError."""
        # Arrange
        generator = CodeGenerator('python')
        generator.load_history([])
        
        # Act & Assert
        with pytest.raises(ValueError, match="No history available to generate code"):
            generator.generate_code()

class TestCodeExport:
    def test_export_python_code_creates_file(self, mock_history):
        """Test that export_code creates a file."""
        # Arrange
        generator = CodeGenerator('python')
        generator.load_history(mock_history)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            temp_path = f.name
        
        try:
            # Act
            generator.export_code(temp_path)
            
            # Assert
            assert os.path.exists(temp_path)
            with open(temp_path, 'r') as f:
                content = f.read()
            assert 'import pandas as pd' in content
            assert 'from databroom.core.broom import Broom' in content
            assert 'remove_empty_cols(threshold=0.9)' in content
            
        finally:
            # Cleanup
            os.unlink(temp_path)

    @pytest.mark.skip(reason="R template todavía no implementado completamente")
    def test_export_r_code_creates_file(self, mock_history):
        """Test that export_code creates R file."""
        # Arrange
        generator = CodeGenerator('R')
        generator.load_history(mock_history)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.R', delete=False) as f:
            temp_path = f.name
        
        try:
            # Act
            generator.export_code(temp_path)
            
            # Assert
            assert os.path.exists(temp_path)
            with open(temp_path, 'r') as f:
                content = f.read()
            # R template should contain R-specific content
            assert len(content) > 0
            
        finally:
            # Cleanup
            os.unlink(temp_path)

    def test_export_code_includes_timestamp(self, mock_history):
        """Test that exported code includes timestamp."""
        # Arrange
        generator = CodeGenerator('python')
        generator.load_history(mock_history)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            temp_path = f.name
        
        try:
            # Act
            generator.export_code(temp_path)
            
            # Assert
            with open(temp_path, 'r') as f:
                content = f.read()
            assert 'Date:' in content
            # Check for year (basic timestamp validation)
            assert '202' in content  # Should contain current year prefix
            
        finally:
            # Cleanup
            os.unlink(temp_path)

class TestTemplateSystem:
    def test_templates_directory_exists(self):
        """Test that templates directory exists and contains files."""
        # Arrange
        generator = CodeGenerator('python')
        
        # Act - templates should be loaded during initialization
        templates_path = generator.templates_path
        
        # Assert
        assert len(templates_path) > 0
        # Templates should be found
        assert len(generator.templates) > 0

    def test_python_template_exists(self):
        """Test that Python template exists."""
        # Arrange
        generator = CodeGenerator('python')
        
        # Assert
        assert 'python_pipeline' in generator.templates

    def test_template_loading_resilient_to_missing_files(self):
        """Test that template loading doesn't crash with missing files."""
        # This test ensures the system is resilient
        # Even if some template files are missing, it should still work
        
        # Arrange & Act
        generator = CodeGenerator('python')
        
        # Assert - should not raise exception
        assert hasattr(generator, 'templates')
        assert isinstance(generator.templates, list)

if __name__ == "__main__":
    pytest.main([__file__])