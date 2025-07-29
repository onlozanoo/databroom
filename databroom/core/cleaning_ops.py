# databroom/core/cleaning_ops.py

import pandas as pd
import unicodedata

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
    """Standardize column names by converting to lowercase and replacing spaces with underscores."""
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    # Standardize column names
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    return df

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names by removing accents and special characters.
    
    This function processes all column names in the DataFrame and converts characters like
    'é' → 'e', 'ñ' → 'n', and so on. It is useful for standardizing column names before analysis.
    
    Args:
        df (pd.DataFrame): The DataFrame to process.
    
    Returns:
        pd.DataFrame: A new DataFrame with normalized column names.
    """
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    def remove_accents(val):
        if isinstance(val, str):
            normalized = unicodedata.normalize('NFKD', val)
            return normalized.encode('ASCII', 'ignore').decode('utf-8')
        return val
    
    # Apply normalization to all column names
    df.columns = df.columns.map(remove_accents)
    
    return df

def normalize_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize text values in a DataFrame by removing accents and special characters.

    This function processes all string entries in the DataFrame and converts characters like
    'é' → 'e', 'ñ' → 'n', and so on. It is useful for standardizing textual data before analysis.

    Args:
        df (pd.DataFrame): The DataFrame to process.

    Returns:
        pd.DataFrame: A new DataFrame with normalized text.
    """
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    def remove_accents(val):
        if isinstance(val, str):
            normalized = unicodedata.normalize('NFKD', val)
            return normalized.encode('ASCII', 'ignore').decode('utf-8')
        return val

    # Apply normalization to all string cells
    cleaned_df = df.applymap(remove_accents)
    
    return cleaned_df

def standardize_values(df: pd.DataFrame, columns: list = None) -> pd.DataFrame:
    """
    Standardize text values in a DataFrame by converting to lowercase and replacing spaces with underscores.

    This function processes string entries in the DataFrame and converts them to lowercase,
    replacing spaces with underscores. It is useful for standardizing textual data before analysis.

    Args:
        df (pd.DataFrame): The DataFrame to process.
        columns (list, optional): Specific columns to standardize. If None, applies to all columns.

    Returns:
        pd.DataFrame: A new DataFrame with standardized text.
    """
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    # Start with normalized values (removes accents)
    cleaned_df = normalize_values(df)
    
    def standardize_text(x):
        return x.lower().replace(' ', '_') if isinstance(x, str) else x
    
    if columns is None:
        # Apply to all columns
        return cleaned_df.applymap(standardize_text)
    else:
        # Apply only to specified columns
        result_df = cleaned_df.copy()
        for col in columns:
            if col in result_df.columns:
                result_df[col] = result_df[col].apply(standardize_text)
        return result_df