import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os

@pytest.fixture
def sample_clean_data():
    """DataFrame limpio para pruebas."""
    return pd.DataFrame({
        'id': [1, 2, 3, 4],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'age': [25, 30, 35, 28],
        'city': ['New York', 'London', 'Paris', 'Tokyo']
    })

@pytest.fixture
def sample_dirty_data():
    """DataFrame con problemas comunes para testing."""
    return pd.DataFrame({
        'Column Name': [1, 2, None, 4],
        'Año Niño': ['2020', '2021', None, '2023'],
        'Empty Col': [None, None, None, None],
        'Mixed Data': [1, 'text', None, 4.5],
        'Accented Names': ['José', 'François', 'Müller', 'Øystein'],
        'Messy Strings': [' UPPER case ', 'MiXeD CaSe', '  whitespace  ', 'normal']
    })

@pytest.fixture
def sample_csv_content():
    """Content for a sample CSV file."""
    return """name,age,city,salary
Alice,25,New York,50000
Bob,30,London,
Charlie,,Paris,75000
Diana,28,Tokyo,65000
,35,Berlin,55000"""

@pytest.fixture
def temp_csv_file(sample_csv_content):
    """Create a temporary CSV file for testing file operations."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(sample_csv_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)

@pytest.fixture
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / 'test_data'

@pytest.fixture
def mock_history():
    """Mock history data for code generation tests."""
    return [
        "remove_empty_cols called with Parameters: {'threshold': 0.9}. Operation completed successfully.",
        "standardize_column_names called with Parameters: {}. Operation completed successfully.",
        "normalize_column_names called with Parameters: {}. Operation completed successfully."
    ]

@pytest.fixture
def empty_dataframe():
    """Completely empty DataFrame."""
    return pd.DataFrame()

@pytest.fixture
def single_row_data():
    """DataFrame with single row for edge case testing."""
    return pd.DataFrame({
        'col1': [1],
        'col2': ['test'],
        'empty_col': [None]
    })