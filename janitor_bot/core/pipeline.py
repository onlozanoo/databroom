# pipeline.py

from janitor_bot.core.history_tracker import CleaningCommand
from janitor_bot.core.debug_logger import debug_log
from janitor_bot.core import cleaning_ops
import inspect

# Get the function names in cleaning_ops
available_functions = [name for name, obj in inspect.getmembers(cleaning_ops, inspect.isfunction)]

class CleaningPipeline:
    def __init__(self, df):
        debug_log(f"Initializing CleaningPipeline with DataFrame shape: {df.shape}", "PIPELINE")
        self.df = df
        self.df_original = df.copy() # Store the original DataFrame
        self.operations = available_functions
        self.history_list = []
        self.df_snapshots = [df.copy()]  # Store DataFrame snapshots for step back
        debug_log(f"Pipeline initialized with {len(self.operations)} operations: {self.operations}", "PIPELINE")
        debug_log(f"Original DataFrame stored - Shape: {self.df_original.shape}", "PIPELINE")
        debug_log(f"Initial snapshot stored - Total snapshots: {len(self.df_snapshots)}", "PIPELINE")
    
    def get_current_dataframe(self):
        """Return the current state of the DataFrame."""
        return self.df
    
    def get_history(self):
        """Return the complete history of operations performed."""
        return self.history_list.copy()
    
    def get_operation_count(self):
        """Return the number of operations performed."""
        return len(self.history_list)
    
    def can_step_back(self):
        """Check if step back is possible."""
        return len(self.df_snapshots) > 1
    
    def step_back(self):
        """
        Step back to the previous DataFrame state.
        
        Returns:
            pd.DataFrame: The DataFrame state after stepping back
            
        Raises:
            ValueError: If no previous state is available to step back to
        """
        debug_log(f"Step back requested - Current snapshots: {len(self.df_snapshots)}, history: {len(self.history_list)}", "PIPELINE")
        
        if not self.can_step_back():
            debug_log("Step back failed - No previous state available", "PIPELINE")
            raise ValueError("No previous state available to step back to")
        
        # Remove current snapshot and history entry
        self.df_snapshots.pop()
        if self.history_list:
            removed_operation = self.history_list.pop()
            debug_log(f"Removed operation from history: {removed_operation}", "PIPELINE")
        
        # Restore previous DataFrame state
        self.df = self.df_snapshots[-1].copy()
        debug_log(f"Stepped back - New shape: {self.df.shape}, snapshots: {len(self.df_snapshots)}, history: {len(self.history_list)}", "PIPELINE")
        
        return self.df
        
    def execute_operation(self, operation, *args, **kwargs):
        """
        Execute a cleaning operation on the DataFrame.
        
        Args:
            operation (callable): The cleaning function to execute.
            *args: Positional arguments for the operation.
            **kwargs: Keyword arguments for the operation.
        
        Returns:
            pd.DataFrame: The cleaned DataFrame after applying the operation.
        """
        debug_log(f"Pipeline executing operation: {operation}", "PIPELINE")
        debug_log(f"Operation args: {args}, kwargs: {kwargs}", "PIPELINE")
        
        if operation not in self.operations:
            debug_log(f"Operation '{operation}' not found in available operations: {self.operations}", "PIPELINE")
            raise ValueError(f"Operation '{operation}' is not available in the pipeline.")
        else:
            debug_log(f"Operation '{operation}' found in pipeline", "PIPELINE")
            # Get the actual function from cleaning_ops
            operation_func = getattr(cleaning_ops, operation)
            debug_log(f"Retrieved function: {operation_func}", "PIPELINE")
            
            # Apply the CleaningCommand decorator with our history list
            debug_log(f"Applying CleaningCommand decorator with history list (length: {len(self.history_list)})", "PIPELINE")
            decorated_func = CleaningCommand(function=operation_func, history_list=self.history_list)
            
            # Execute the decorated function and update our DataFrame
            debug_log(f"Before operation - DataFrame shape: {self.df.shape}", "PIPELINE")
            self.df = decorated_func(self.df, *args, **kwargs)
            debug_log(f"After operation - DataFrame shape: {self.df.shape}", "PIPELINE")
            debug_log(f"History list now has {len(self.history_list)} entries", "PIPELINE")
            
            # Store snapshot after successful operation for step back functionality
            self.df_snapshots.append(self.df.copy())
            debug_log(f"Snapshot stored - Total snapshots: {len(self.df_snapshots)}", "PIPELINE")
        
        return self.df