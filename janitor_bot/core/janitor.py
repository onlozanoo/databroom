# janitor.py

from janitor_bot.core.pipeline import CleaningPipeline
import pandas as pd

class Janitor:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.pipeline = CleaningPipeline(self.df)
        
        print("Janitor initialized")
    
    @classmethod
    def from_csv(cls, file_source, **csv_kwargs):
        """Create Janitor from CSV file or uploaded file object."""
        try:
            # Handle both file paths and uploaded file objects
            if hasattr(file_source, 'read'):  # Streamlit uploaded file
                df = pd.read_csv(file_source, **csv_kwargs)
            else:  # File path string
                df = pd.read_csv(file_source, **csv_kwargs)
            return cls(df)
        except Exception as e:
            raise ValueError(f"Error loading CSV: {e}")
    
    @classmethod
    def from_excel(cls, file_source, sheet_name=0, **excel_kwargs):
        """Create Janitor from Excel file."""
        try:
            if hasattr(file_source, 'read'):
                df = pd.read_excel(file_source, sheet_name=sheet_name, **excel_kwargs)
            else:
                df = pd.read_excel(file_source, sheet_name=sheet_name, **excel_kwargs)
            return cls(df)
        except Exception as e:
            raise ValueError(f"Error loading Excel: {e}")
    
    @classmethod
    def from_json(cls, file_source, **json_kwargs):
        """Create Janitor from JSON file."""
        try:
            if hasattr(file_source, 'read'):
                df = pd.read_json(file_source, **json_kwargs)
            else:
                df = pd.read_json(file_source, **json_kwargs)
            return cls(df)
        except Exception as e:
            raise ValueError(f"Error loading JSON: {e}")
    
    @classmethod
    def from_file(cls, file_source, file_type=None, **kwargs):
        """Smart factory method - auto-detects file type."""
        # Auto-detect file type if not provided
        if file_type is None:
            if hasattr(file_source, 'name'):  # Uploaded file
                filename = file_source.name
            else:  # File path
                filename = str(file_source)
            
            if filename.endswith('.csv'):
                file_type = 'csv'
            elif filename.endswith(('.xlsx', '.xls')):
                file_type = 'excel'
            elif filename.endswith('.json'):
                file_type = 'json'
            else:
                raise ValueError(f"Unsupported file type: {filename}")
        
        # Delegate to specific factory method
        if file_type == 'csv':
            return cls.from_csv(file_source, **kwargs)
        elif file_type == 'excel':
            return cls.from_excel(file_source, **kwargs)
        elif file_type == 'json':
            return cls.from_json(file_source, **kwargs)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
    def get_df(self) -> pd.DataFrame:
        """Return the current state of the DataFrame."""
        return self.pipeline.get_current_dataframe()

    def get_history(self):
        """Return the complete history of operations performed."""
        return self.pipeline.get_history()
    
    def reset(self):
        """Reset the DataFrame to its initial state."""
        self.pipeline.df = self.pipeline.df_original.copy()
        self.pipeline.history = []
        self.pipeline.current_operation = None
        return self
    
    def remove_empty_cols(self, threshold: float = 0.9):
        """Remove empty columns based on a threshold of non-null values."""
        self.pipeline.execute_operation('remove_empty_cols', threshold=threshold)
        
        return self
    
    def remove_empty_rows(self):
        """Remove empty rows based on a threshold of non-null values."""
        self.pipeline.execute_operation('remove_empty_rows')
    
        return self
    
    def standarize_column_names(self):
        """Standardize column names by converting to lowercase and replacing spaces with underscores."""
        self.pipeline.execute_operation('standarize_column_names')

        return self
    
    def normalize_column_names(self):
        """Normalize column names by removing accents and special characters."""
        self.pipeline.execute_operation('normalize_column_names')

        return self
    
    def normalize_values(self):
        """Normalize values in dataframe."""
        self.pipeline.execute_operation('normalize_values')

        return self
    
    def standarize_values(self):
        """Standardize values in a specific column."""
        self.pipeline.execute_operation('standarize_values')

        return self
