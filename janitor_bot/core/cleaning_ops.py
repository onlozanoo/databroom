# janitor_bot/core/cleaning_ops.py

import pandas as pd


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


def standarize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names by converting to lowercase and replacing spaces with underscores."""
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    # Standardize column names
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    return df