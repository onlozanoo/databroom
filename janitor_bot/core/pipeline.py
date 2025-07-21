# pipeline.py

from janitor_bot.core.history_tracker import CleaningCommand
from janitor_bot.core import cleaning_ops
import inspect

# Obtener los nombres de las funciones en cleaning_ops
avaiable_functions = [name for name, obj in inspect.getmembers(cleaning_ops, inspect.isfunction)]

class CleaningPipeline:
    def __init__(self, df):
        self.df = df
        self.df_original = df.copy() # Store the original DataFrame
        self.operations = avaiable_functions
        self.history_list = []
    
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
        if operation not in self.operations:
            raise ValueError(f"Operation '{operation}' is not available in the pipeline.")
        else:
            # Get the actual function from cleaning_ops
            operation_func = getattr(cleaning_ops, operation)
            
            # Apply the CleaningCommand decorator with our history list
            decorated_func = CleaningCommand(function=operation_func, history_list=self.history_list)
            
            # Execute the decorated function and update our DataFrame
            self.df = decorated_func(self.df, *args, **kwargs)
        
        return self.df