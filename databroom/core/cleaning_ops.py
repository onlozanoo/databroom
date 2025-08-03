# databroom/core/cleaning_ops.py

import pandas as pd
import unicodedata
import re

def remove_empty_cols(df: pd.DataFrame, threshold: float = 0.9) -> pd.DataFrame:
    """Remove empty columns from a DataFrame based on a threshold of non-null values."""
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    # Calculate the threshold for non-null values
    thresh = int(threshold * len(df))
    
    # Drop columns with less than the threshold of non-null values
    cleaned_df = df.dropna(axis=1, thresh=thresh)
    
    return cleaned_df



def remove_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Remove empty rows from a DataFrame."""
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    # Drop rows that are completely empty
    cleaned_df = df.dropna(axis=0, how='all')
    
    return cleaned_df


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Legacy function - Use clean_columns() instead."""
    return clean_columns(df, remove_empty=False, snake_case=True, remove_accents=False)

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Legacy function - Use clean_columns() instead."""
    return clean_columns(df, remove_empty=False, snake_case=False, remove_accents=True)

def normalize_values(df: pd.DataFrame) -> pd.DataFrame:
    """Legacy function - Use clean_rows() instead."""
    return clean_rows(df, remove_empty=False, clean_text=True, remove_accents=True, snakecase=False)

def clean_columns(df: pd.DataFrame, 
                 remove_empty: bool = True,
                 empty_threshold: float = 0.9, 
                 snake_case: bool = True,
                 remove_accents: bool = True) -> pd.DataFrame:
    """Comprehensive column cleaning with all operations enabled by default."""
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    result_df = df.copy()
    
    # Remove empty columns first
    if remove_empty:
        result_df = remove_empty_cols(result_df, threshold=empty_threshold)
    
    # Remove accents from column names
    if remove_accents:
        def remove_accents_func(val):
            if isinstance(val, str):
                normalized = unicodedata.normalize('NFKD', val)
                return normalized.encode('ASCII', 'ignore').decode('utf-8')
            return val
        result_df.columns = result_df.columns.map(remove_accents_func)
    
    # Convert to snake_case
    if snake_case:
        result_df.columns = result_df.columns.str.lower().str.replace(' ', '_').str.replace(r'[^a-z0-9_]', '', regex=True)
    
    return result_df


def clean_rows(df: pd.DataFrame,
              remove_empty: bool = True, 
              clean_text: bool = True,
              remove_accents: bool = True,
              snakecase: bool = True) -> pd.DataFrame:
    """Comprehensive row cleaning with all operations enabled by default."""
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    result_df = df.copy()
    
    # Remove completely empty rows
    if remove_empty:
        result_df = remove_empty_rows(result_df)
    
    # Apply text cleaning if enabled
    if clean_text:
        def clean_text_value(val):
            if not isinstance(val, str):
                return val
            
            # Remove accents
            if remove_accents:
                normalized = unicodedata.normalize('NFKD', val)
                val = normalized.encode('ASCII', 'ignore').decode('utf-8')
            
            # Apply snake_case transformation (lowercase + standardize spaces)
            if snakecase:
                val = val.lower()
                val = re.sub(r'\s+', '_', val.strip())  # Multiple spaces -> single underscore
            
            return val
        
        # Apply to all string columns
        result_df = result_df.map(clean_text_value)
    
    return result_df


def clean_all(df: pd.DataFrame) -> pd.DataFrame:
    """Ultimate cleaning function - applies both column and row cleaning with all defaults."""
    
    result_df = clean_columns(df)
    result_df = clean_rows(result_df)
    
    return result_df


def promote_headers(df: pd.DataFrame, row_index: int = 0, drop_promoted_row: bool = True) -> pd.DataFrame:
    """Promote a specific row to become the column headers."""
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    if row_index < 0 or row_index >= len(df):
        raise ValueError(f"row_index must be between 0 and {len(df)-1}")
    
    result_df = df.copy()
    
    # Get the row to promote as headers
    new_headers = result_df.iloc[row_index].astype(str).tolist()
    
    # Set new column names
    result_df.columns = new_headers
    
    # Drop the promoted row if requested
    if drop_promoted_row:
        result_df = result_df.drop(result_df.index[row_index]).reset_index(drop=True)
    
    return result_df


# Legacy functions for backward compatibility
def standardize_values(df: pd.DataFrame, columns: list = None) -> pd.DataFrame:
    """Legacy function - Use clean_rows() instead."""
    return clean_rows(df, clean_text=True, remove_accents=True, snakecase=True)