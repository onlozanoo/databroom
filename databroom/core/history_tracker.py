"""
databroom/core/history_tracker.py

This module provides decorators for automatically tracking data cleaning operations.
The main decorator captures metadata about DataFrame transformations for reproducibility.
"""

from datetime import datetime
from databroom.core.debug_logger import debug_log
import pandas as pd


def CleaningCommand(function=None, history_list=None):
    """
    Decorator that automatically tracks DataFrame cleaning operations.
    
    This decorator captures metadata about data transformations including:
    - Function name and parameters used
    - DataFrame state before and after the operation
    - Timestamp of execution
    - Shape changes and missing value statistics
    
    Args:
        function: The function to be decorated (when used without parameters)
        history_list (list, optional): List to append operation logs to.
                                     If None, no logging occurs.
    
    Returns:
        function: Decorated function that executes original logic plus tracking
        
    Example:
        >>> history = []
        >>> @CleaningCommand(history_list=history)
        >>> def remove_empty_columns(df, threshold=0.8):
        >>>     return df.dropna(axis=1, thresh=int(threshold * len(df)))
        >>> 
        >>> cleaned_df = remove_empty_columns(dirty_df, threshold=0.9)
        >>> print(history[-1])  # Shows operation details
    
    Note:
        - Automatically detects DataFrame in first argument
        - Only captures state if input/output are pandas DataFrames
        - Thread-safe for individual function calls
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            debug_log(f"History tracker executing function: {func.__name__}", "HISTORY")
            debug_log(f"Function args: {len(args)} arguments, kwargs: {kwargs}", "HISTORY")
            
            # Initialize state tracking dictionary
            df_state = {}
            
            # Attempt to detect DataFrame from first argument
            input_df = None
            if args and isinstance(args[0], pd.DataFrame):
                input_df = args[0]
                debug_log(f"Input DataFrame detected - Shape: {input_df.shape}", "HISTORY")
                
                # Capture comprehensive state before operation
                df_state["shape_before"] = input_df.shape
                df_state["columns_before"] = list(input_df.columns)
                df_state["percent_missing_before"] = input_df.isnull().mean().mean() * 100
                debug_log(f"Before operation - Missing %: {df_state['percent_missing_before']:.2f}%", "HISTORY")
            
            # Execute the original cleaning function
            debug_log(f"Executing {func.__name__}...", "HISTORY")
            results = func(*args, **kwargs)
            debug_log(f"Function {func.__name__} executed successfully", "HISTORY")
            
            # Capture state after operation if result is also a DataFrame
            if isinstance(results, pd.DataFrame):
                df_state["shape_after"] = results.shape
                df_state["columns_after"] = list(results.columns)
                df_state["percent_missing_after"] = results.isnull().mean().mean() * 100
                debug_log(f"Output DataFrame - Shape: {df_state['shape_after']}", "HISTORY")
                debug_log(f"After operation - Missing %: {df_state['percent_missing_after']:.2f}%", "HISTORY")
            
            # Log operation details if history tracking is enabled
            if history_list is not None:
                debug_log("Adding entry to history list...", "HISTORY")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Format shape change information if available
                shape_info = ""
                if "shape_before" in df_state and "shape_after" in df_state:
                    shape_info = f". Shape from {df_state['shape_before']} to {df_state['shape_after']}"
                    debug_log(f"Shape change detected: {shape_info}", "HISTORY")
                
                # Create comprehensive log entry
                log_entry = (
                    f"{timestamp} - {func.__name__} called. "
                    f"Parameters: {kwargs}{shape_info}"
                )
                history_list.append(log_entry)
                debug_log(f"History entry added - Total entries: {len(history_list)}", "HISTORY")
                debug_log(f"Entry content: {log_entry}", "HISTORY")
            else:
                debug_log("No history list provided - skipping history tracking", "HISTORY")
            
            # Return original function results unchanged
            return results
        
        # Preserve original function metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    return decorator(function)