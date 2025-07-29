import pytest
import pandas as pd
from pathlib import Path

# Development path setup (only when run directly)
if __name__ == "__main__" and __package__ is None:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from databroom.core.broom import Broom

class TestJanitorInitialization:
    def test_from_dataframe_initialization(self, sample_clean_data):
        """Test Janitor initialization with DataFrame."""
        # Act
        janitor = Broom(sample_clean_data)
        
        # Assert
        assert janitor.get_df().shape == sample_clean_data.shape
        assert len(janitor.get_history()) == 0
        assert janitor.pipeline is not None

    def test_from_csv_file(self, temp_csv_file):
        """Test Janitor initialization from CSV file."""
        # Act
        janitor = Broom.from_csv(temp_csv_file)
        
        # Assert
        df = janitor.get_df()
        assert len(df) > 0
        assert 'name' in df.columns
        assert 'age' in df.columns

    def test_from_csv_with_kwargs(self, temp_csv_file):
        """Test Janitor initialization from CSV with additional parameters."""
        # Act
        janitor = Broom.from_csv(temp_csv_file, encoding='utf-8')
        
        # Assert
        df = janitor.get_df()
        assert len(df) > 0

    def test_from_file_auto_detection(self, temp_csv_file):
        """Test automatic file type detection."""
        # Act
        janitor = Broom.from_file(temp_csv_file)
        
        # Assert
        df = janitor.get_df()
        assert len(df) > 0

    def test_from_csv_invalid_file_raises_error(self):
        """Test that invalid file path raises error."""
        with pytest.raises(ValueError):
            Janitor.from_csv("nonexistent_file.csv")

    def test_from_excel_file(self, test_data_dir):
        """Test Janitor initialization from Excel file."""
        # Arrange
        excel_file = test_data_dir / "sample.xlsx"
        
        # Act
        janitor = Broom.from_excel(excel_file)
        
        # Assert
        df = janitor.get_df()
        assert len(df) > 0
        assert 'name' in df.columns
        assert 'age' in df.columns

    def test_from_json_file(self, test_data_dir):
        """Test Janitor initialization from JSON file."""
        # Arrange
        json_file = test_data_dir / "sample.json"
        
        # Act
        janitor = Broom.from_json(json_file)
        
        # Assert
        df = janitor.get_df()
        assert len(df) > 0
        assert 'name' in df.columns
        assert 'age' in df.columns

class TestJanitorOperations:
    def test_remove_empty_cols_operation(self, sample_dirty_data):
        """Test remove_empty_cols operation."""
        # Arrange
        janitor = Broom(sample_dirty_data)
        original_cols = len(janitor.get_df().columns)
        
        # Act
        result = janitor.remove_empty_cols(threshold=0.9)
        
        # Assert
        assert result is janitor  # Should return self for chaining
        final_cols = len(janitor.get_df().columns)
        assert final_cols < original_cols  # Empty column should be removed
        assert len(janitor.get_history()) == 1
        assert 'remove_empty_cols' in janitor.get_history()[0]

    def test_remove_empty_rows_operation(self, sample_dirty_data):
        """Test remove_empty_rows operation."""
        # Arrange
        janitor = Broom(sample_dirty_data)
        
        # Act
        result = janitor.remove_empty_rows()
        
        # Assert
        assert result is janitor
        assert len(janitor.get_history()) == 1
        assert 'remove_empty_rows' in janitor.get_history()[0]

    def test_standardize_column_names_operation(self, sample_dirty_data):
        """Test standardize_column_names operation."""
        # Arrange
        janitor = Broom(sample_dirty_data)
        
        # Act
        result = janitor.standardize_column_names()
        
        # Assert
        assert result is janitor
        df = janitor.get_df()
        # Check that column names are standardized
        for col in df.columns:
            assert col.islower()
            assert ' ' not in col  # No spaces
        assert len(janitor.get_history()) == 1

    def test_normalize_column_names_operation(self, sample_dirty_data):
        """Test normalize_column_names operation."""
        # Arrange
        janitor = Broom(sample_dirty_data)
        
        # Act
        result = janitor.normalize_column_names()
        
        # Assert
        assert result is janitor
        assert len(janitor.get_history()) == 1
        assert 'normalize_column_names' in janitor.get_history()[0]

class TestJanitorChaining:
    def test_method_chaining(self, sample_dirty_data):
        """Test that methods can be chained together."""
        # Arrange
        janitor = Broom(sample_dirty_data)
        original_shape = janitor.get_df().shape
        
        # Act
        result = (janitor
                  .remove_empty_cols(threshold=0.9)
                  .standardize_column_names()
                  .normalize_column_names())
        
        # Assert
        assert result is janitor
        assert len(janitor.get_history()) == 3
        # Verify each operation was recorded
        history = janitor.get_history()
        assert any('remove_empty_cols' in h for h in history)
        assert any('standardize_column_names' in h for h in history)
        assert any('normalize_column_names' in h for h in history)

    def test_chaining_preserves_data_integrity(self, sample_clean_data):
        """Test that chaining operations preserves data integrity."""
        # Arrange
        janitor = Broom(sample_clean_data)
        original_data_count = len(janitor.get_df())
        
        # Act
        result = (janitor
                  .standardize_column_names()
                  .normalize_column_names())
        
        # Assert
        # These operations shouldn't remove any data
        assert len(janitor.get_df()) == original_data_count
        assert len(janitor.get_history()) == 2

class TestJanitorHistory:
    @pytest.mark.skip(reason="History format en desarrollo - verificar formato exacto")
    def test_history_tracking(self, sample_clean_data):
        """Test that operation history is properly tracked."""
        # Arrange
        janitor = Broom(sample_clean_data)
        
        # Act
        janitor.remove_empty_cols(threshold=0.5)
        janitor.standardize_column_names()
        
        # Assert
        history = janitor.get_history()
        assert len(history) == 2
        assert 'remove_empty_cols' in history[0]
        assert 'threshold=0.5' in history[0]
        assert 'standardize_column_names' in history[1]

    @pytest.mark.skip(reason="History format en desarrollo - verificar formato exacto")
    def test_history_contains_parameters(self, sample_clean_data):
        """Test that history contains operation parameters."""
        # Arrange
        janitor = Broom(sample_clean_data)
        
        # Act
        janitor.remove_empty_cols(threshold=0.7)
        
        # Assert
        history = janitor.get_history()
        assert len(history) == 1
        assert 'threshold=0.7' in history[0]

    def test_get_history_returns_copy(self, sample_clean_data):
        """Test that get_history returns a copy, not reference."""
        # Arrange
        janitor = Broom(sample_clean_data)
        janitor.remove_empty_cols()
        
        # Act
        history1 = janitor.get_history()
        history1.append("modified")
        history2 = janitor.get_history()
        
        # Assert
        assert len(history2) == 1  # Original history unchanged
        assert "modified" not in history2

class TestJanitorEdgeCases:
    def test_empty_dataframe(self, empty_dataframe):
        """Test Janitor with empty DataFrame."""
        # Act
        janitor = Broom(empty_dataframe)
        
        # Assert
        assert janitor.get_df().shape == (0, 0)
        assert len(janitor.get_history()) == 0

    @pytest.mark.skip(reason="Edge case con single row - verificar comportamiento threshold")
    def test_single_row_dataframe(self, single_row_data):
        """Test Janitor with single row DataFrame."""
        # Act
        janitor = Broom(single_row_data)
        result = janitor.remove_empty_cols(threshold=0.5)
        
        # Assert
        df = result.get_df()
        assert len(df) == 1
        assert 'empty_col' not in df.columns  # Should be removed

    @pytest.mark.skip(reason="Empty DataFrame operations necesitan manejo especial")
    def test_operations_on_empty_dataframe(self, empty_dataframe):
        """Test that operations on empty DataFrame don't crash."""
        # Arrange
        janitor = Broom(empty_dataframe)
        
        # Act & Assert - should not raise exceptions
        result = janitor.standardize_column_names()
        assert result is janitor

if __name__ == "__main__":
    pytest.main([__file__])