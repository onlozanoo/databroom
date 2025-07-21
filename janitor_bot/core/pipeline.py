# pipeline.py

from janitor_bot.core.history_tracker import CleaningCommand
from janitor_bot.core.debug_logger import debug_log
from janitor_bot.core import cleaning_ops
import inspect

# Obtener los nombres de las funciones en cleaning_ops
avaiable_functions = [name for name, obj in inspect.getmembers(cleaning_ops, inspect.isfunction)]

class CleaningPipeline:
    def __init__(self, df):
        debug_log(f"Initializing CleaningPipeline with DataFrame shape: {df.shape}", "PIPELINE")
        self.df = df
        self.df_original = df.copy() # Store the original DataFrame
        self.operations = avaiable_functions
        self.history_list = []
        debug_log(f"Pipeline initialized with {len(self.operations)} operations: {self.operations}", "PIPELINE")
        debug_log(f"Original DataFrame stored - Shape: {self.df_original.shape}", "PIPELINE")
    
    def get_current_dataframe(self):
        """Return the current state of the DataFrame."""
        return self.df
    
    def get_history(self):
        """Return the complete history of operations performed."""
        return self.history_list.copy()
    
    def get_operation_count(self):
        """Return the number of operations performed."""
        return len(self.history_list)
        
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
        
        return self.df