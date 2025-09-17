# broom.py

from databroom.core.pipeline import CleaningPipeline
from databroom.core.debug_logger import debug_log
import pandas as pd

class Broom:
    def __init__(self, df: pd.DataFrame):
        debug_log(f"Initializing Broom with DataFrame shape: {df.shape}", "BROOM")
        self.df = df
        self.pipeline = CleaningPipeline(self.df)
        debug_log(f"Broom initialized - Pipeline created with {len(self.pipeline.operations)} available operations", "BROOM")
        debug_log(f"Available operations: {self.pipeline.operations}", "BROOM")
    
    @classmethod
    def from_csv(cls, file_source, **csv_kwargs):
        """Create Broom from CSV file or uploaded file object."""
        debug_log(f"Loading CSV file - Type: {type(file_source)}", "BROOM")
        try:
            # Handle both file paths and uploaded file objects
            if hasattr(file_source, 'read'):  # Streamlit uploaded file
                debug_log("Detected Streamlit uploaded file object", "BROOM")
                df = pd.read_csv(file_source, **csv_kwargs)
            else:  # File path string
                debug_log(f"Detected file path: {file_source}", "BROOM")
                df = pd.read_csv(file_source, **csv_kwargs)
            debug_log(f"CSV loaded successfully - Shape: {df.shape}", "BROOM")
            return cls(df)
        except Exception as e:
            debug_log(f"Error loading CSV: {e}", "BROOM")
            raise ValueError(f"Error loading CSV: {e}")
    
    @classmethod
    def from_excel(cls, file_source, sheet_name=0, **excel_kwargs):
        """Create Broom from Excel file."""
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
        """Create Broom from JSON file."""
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
        debug_log(f"Auto-detecting file type for: {type(file_source)}", "BROOM")
        
        # Auto-detect file type if not provided
        if file_type is None:
            if hasattr(file_source, 'name'):  # Uploaded file
                filename = file_source.name.lower()
                debug_log(f"Uploaded file detected: {filename}", "BROOM")
            else:  # File path
                filename = str(file_source).lower()
                debug_log(f"File path detected: {filename}", "BROOM")
            
            if filename.endswith('.csv'):
                file_type = 'csv'
            elif filename.endswith(('.xlsx', '.xls')):
                file_type = 'excel'
            elif filename.endswith('.json'):
                file_type = 'json'
            else:
                debug_log(f"Unsupported file extension in: {filename}", "BROOM")
                raise ValueError(f"Unsupported file type: {filename}")
        
        debug_log(f"File type determined: {file_type}", "BROOM")
        
        # Delegate to specific factory method
        if file_type == 'csv':
            debug_log("Delegating to from_csv method", "BROOM")
            return cls.from_csv(file_source, **kwargs)
        elif file_type == 'excel':
            debug_log("Delegating to from_excel method", "BROOM")
            return cls.from_excel(file_source, **kwargs)
        elif file_type == 'json':
            debug_log("Delegating to from_json method", "BROOM")
            return cls.from_json(file_source, **kwargs)
        else:
            debug_log(f"Unsupported file type after detection: {file_type}", "BROOM")
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
        self.pipeline.history_list = []
        self.pipeline.df_snapshots = [self.pipeline.df_original.copy()]
        return self
    
    def can_step_back(self):
        """Check if step back is possible."""
        return self.pipeline.can_step_back()
    
    def step_back(self):
        """
        Step back to the previous DataFrame state.
        
        Returns:
            Broom: Self for method chaining
            
        Raises:
            ValueError: If no previous state is available to step back to
        """
        self.pipeline.step_back()
        return self
    
    def save_pipeline(self):
        """ Save the data pipeline from a Broom instance. Return True if successful."""
        return self.pipeline.save_pipeline()
         
    def load_pipeline(self):
        """ Load data into a Broom instance."""
        return self.pipeline.load_pipeline()
    
    def run_pipeline(self, loaded_history: bool = False, path: str = "pipeline.json"):
        """ Execute the saved pipeline on the current DataFrame."""
        return self.pipeline.run_pipeline(loaded_history, path)
    
    def remove_empty_cols(self, threshold: float = 0.9):
        """Remove empty columns based on a threshold of non-null values."""
        debug_log(f"Broom.remove_empty_cols called with threshold: {threshold}", "BROOM")
        self.pipeline.execute_operation('remove_empty_cols', threshold=threshold)
        debug_log("remove_empty_cols operation completed", "BROOM")
        
        return self
    
    def remove_empty_rows(self):
        """Remove empty rows based on a threshold of non-null values."""
        self.pipeline.execute_operation('remove_empty_rows')
    
        return self
    
    def standardize_column_names(self):
        """Standardize column names by converting to lowercase and replacing spaces with underscores."""
        self.pipeline.execute_operation('standardize_column_names')

        return self
    
    def normalize_column_names(self):
        """Normalize column names by removing accents and special characters."""
        self.pipeline.execute_operation('normalize_column_names')

        return self
    
    def normalize_values(self):
        """Normalize values in dataframe."""
        self.pipeline.execute_operation('normalize_values')

        return self
    
    def standardize_values(self):
        """Standardize values in a specific column."""
        self.pipeline.execute_operation('standardize_values')

        return self
    
    # New simplified cleaning methods
    def clean_columns(self, remove_empty=True, empty_threshold=0.9, snake_case=True, remove_accents=True):
        """Comprehensive column cleaning with all operations enabled by default."""
        debug_log(f"Broom.clean_columns called with params: remove_empty={remove_empty}, empty_threshold={empty_threshold}, snake_case={snake_case}, remove_accents={remove_accents}", "BROOM")
        self.pipeline.execute_operation('clean_columns', 
                                       remove_empty=remove_empty,
                                       empty_threshold=empty_threshold, 
                                       snake_case=snake_case,
                                       remove_accents=remove_accents)
        debug_log("clean_columns operation completed", "BROOM")
        return self
    
    def clean_rows(self, remove_empty=True, clean_text=True, remove_accents=True, snakecase=True):
        """Comprehensive row cleaning with all operations enabled by default."""
        debug_log(f"Broom.clean_rows called with params: remove_empty={remove_empty}, clean_text={clean_text}, remove_accents={remove_accents}, snakecase={snakecase}", "BROOM")
        self.pipeline.execute_operation('clean_rows',
                                       remove_empty=remove_empty,
                                       clean_text=clean_text,
                                       remove_accents=remove_accents,
                                       snakecase=snakecase)
        debug_log("clean_rows operation completed", "BROOM")
        return self
    
    def clean_all(self):
        """Ultimate cleaning function - applies both column and row cleaning with all defaults."""
        debug_log("Broom.clean_all called", "BROOM")
        self.pipeline.execute_operation('clean_all')
        debug_log("clean_all operation completed", "BROOM")
        return self
    
    def promote_headers(self, row_index=0, drop_promoted_row=True):
        """Promote a specific row to become the column headers."""
        debug_log(f"Broom.promote_headers called with params: row_index={row_index}, drop_promoted_row={drop_promoted_row}", "BROOM")
        self.pipeline.execute_operation('promote_headers', 
                                       row_index=row_index,
                                       drop_promoted_row=drop_promoted_row)
        debug_log("promote_headers operation completed", "BROOM")
        return self