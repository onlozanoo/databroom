import pandas as pd
import os
import re
import sys
from pathlib import Path
import ast
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# Development path setup (only when run directly)
if __name__ == "__main__":# and __package__ is None:
    # Dynamically find the project root
    def find_project_root():
        """Find the project root by searching for pyproject.toml upwards."""
        current_path = Path(__file__).resolve()
        for parent in current_path.parents:
            if (parent / 'pyproject.toml').exists():
                return parent
        # If pyproject.toml is not found, use the current directory
        return current_path.parent.parent.parent
    
    # Add the project root to the path
    project_root = find_project_root()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from databroom import Broom 

class CodeGenerator:
    def __init__(self, language):
        self.language = language
        self.history = {}
        self.templates, self.templates_path = self._load_templates()
        
        # Define default values for each function to omit them from generated code
        self.function_defaults = {
            'clean_columns': {
                'remove_empty': True,
                'empty_threshold': 0.9,
                'snake_case': True,
                'remove_accents': True
            },
            'clean_rows': {
                'remove_empty': True,
                'clean_text': True,
                'remove_accents': True,
                'snakecase': True
            },
            'remove_empty_cols': {
                'threshold': 0.9
            },
            'remove_empty_rows': {
                'threshold': 0.9
            },
            'standardize_column_names': {},
            'normalize_column_names': {},
            'normalize_values': {},
            'standardize_values': {},
            'promote_headers': {
                'row_index': 0,
                'drop_promoted_row': True
            },
            'rename_column': {},
            'reorder_columns': {},
            'drop_columns': {},
            'keep_columns': {}
        }

    def _format_r_identifier(self, name: str) -> str:
        """Format column names for safe use in tidyverse verbs."""
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name or ""):
            return name
        escaped = (name or "").replace("`", "``")
        return f"`{escaped}`"

    def _format_r_string(self, value: str) -> str:
        """Quote a string for R code."""
        escaped = (value or "").replace('"', '\\"')
        return f"\"{escaped}\""

    def _format_r_string_vector(self, items):
        quoted = ", ".join(self._format_r_string(item) for item in items)
        return f"c({quoted})"
        
    def _load_templates(self):
        """
        Load code templates based on the specified language.
        
        Returns:
            list: A list of code templates for the specified language.
        """
        
        current_dir = Path(__file__).parent
        templates_dir = current_dir / "templates"
        templates = os.listdir(templates_dir)
        templates_path = templates[1:]
        templates = [f.split('.')[0] for f in templates]
        templates = templates[1:]
        
        return templates, templates_path

    def _freeze_value(self, value):
        """Convert nested structures into hashable tuples for duplicate checks."""
        if isinstance(value, dict):
            return tuple(sorted((key, self._freeze_value(val)) for key, val in value.items()))
        if isinstance(value, (list, tuple)):
            return tuple(self._freeze_value(item) for item in value)
        return value

    def load_history(self, history):
        
        """
        Load the history of generated code.
        
        Returns:
            list: A list of generated code snippets.
        """
        
        # Filter the history to include only code snippets
        
        deduplicated_history = []
        seen_signatures = set()

        for snippet in history:
            func_name = snippet.get('function')
            if not func_name:
                continue

            kwargs = dict(snippet.get('kwargs') or {})
            args = snippet.get('args') or ()
            if not isinstance(args, (list, tuple)):
                args = (args,)

            signature = (
                func_name,
                self._freeze_value(tuple(args)),
                self._freeze_value(kwargs),
            )

            if signature in seen_signatures:
                continue

            deduplicated_history.append((func_name, kwargs))
            seen_signatures.add(signature)

        self.history = deduplicated_history
        
        return self.history
     
    def _filter_non_default_params(self, func_name, params_dict):
        """
        Filter out parameters that match default values to generate cleaner code.
        
        Args:
            func_name (str): Name of the function
            params_dict (dict): All parameters passed to the function
            
        Returns:
            dict: Parameters that differ from defaults
        """
        defaults = self.function_defaults.get(func_name, {})
        filtered_params = {}
        
        for key, value in params_dict.items():
            # Only include parameter if it's different from default or not in defaults
            if key not in defaults or defaults[key] != value:
                filtered_params[key] = value
                
        return filtered_params
    
    def generate_code(self):
        """
        Generate code based on the loaded history and templates.
        
        Returns:
            str: The generated code as a string.
        """
        code = ""
        
        if not self.history or self.history == {}:
            raise ValueError("No history available to generate code.")
        
        # Generate code based on the loaded history and templates
        if self.language == 'python':
            for func, params_dict in self.history:
                
                # Filter out default parameters for cleaner code
                filtered_params = self._filter_non_default_params(func, params_dict)
                
                # Convert dict to string format key=value, separated by comma
                params_formatted = ', '.join(f"{k}={repr(v)}" for k, v in filtered_params.items())
                
                # Build the code line
                if code == "":
                    code = f"df = df.{func}({params_formatted})"
                else:
                    code += f".{func}({params_formatted})"
        
        elif self.language == 'R':
            code_lines = []
            for func, params_dict in self.history:
                
                # Filter out default parameters for cleaner code
                filtered_params = self._filter_non_default_params(func, params_dict)
                
                # Convert Python cleaning operations to R/tidyverse equivalents
                r_line = self._python_to_r_operation(func, filtered_params)
                if r_line:
                    code_lines.append(r_line)
            
            # Join with pipe operator for tidyverse style
            if code_lines:
                code = " %>%\n  ".join(code_lines)
                        
        return code
    
    def _python_to_r_operation(self, func_name, params):
        """
        Convert Python cleaning operations to R/tidyverse equivalents.
        
        Args:
            func_name (str): Python function name
            params (dict): Function parameters
            
        Returns:
            str: R/tidyverse equivalent code
        """
        
        if func_name == 'remove_empty_cols':
            threshold = params.get('threshold', 0.9)
            # In R: remove columns where more than (1-threshold) of values are NA
            na_threshold = 1 - threshold
            return f"select_if(~ mean(is.na(.)) < {na_threshold})"
        
        elif func_name == 'remove_empty_rows':
            threshold = params.get('threshold', 0.9)
            if threshold == 1.0:
               return "filter(!if_all(everything(), is.na))"
            else:
               return f"filter(rowMeans(!is.na(.)) >= {threshold})"
        
        elif func_name == 'standardize_column_names':
            return "clean_names(case = 'snake')"
        
        elif func_name == 'normalize_column_names':
            return "rename_with(~ stri_trans_general(., 'Latin-ASCII'))"
        
        elif func_name == 'normalize_values':
            return "mutate(across(where(is.character), ~ stri_trans_general(., 'Latin-ASCII')))"
        
        elif func_name == 'standardize_values':
            return "mutate(across(where(is.character), ~ str_to_lower(str_replace_all(., ' ', '_'))))"
        
        elif func_name == 'clean_columns':
            # For clean_columns, we need to combine multiple operations
            operations = []
            if params.get('remove_empty', True):
                threshold = params.get('empty_threshold', 0.9)
                na_threshold = 1 - threshold
                operations.append(f"select_if(~ mean(is.na(.)) < {na_threshold})")
            if params.get('remove_accents', True):
                operations.append("rename_with(~ stri_trans_general(., 'Latin-ASCII'))")
            if params.get('snake_case', True):
                operations.append("clean_names(case = 'snake')")
            return " %>%\n  ".join(operations) if operations else "# No column operations needed"
        
        elif func_name == 'clean_rows':
            # For clean_rows, we need to combine multiple operations
            operations = []
            if params.get('remove_empty', True):
                operations.append("filter(!if_all(everything(), is.na))")
            if params.get('clean_text', True):
                if params.get('remove_accents', True):
                    operations.append("mutate(across(where(is.character), ~ stri_trans_general(., 'Latin-ASCII')))")
                if params.get('snakecase', True):
                    operations.append("mutate(across(where(is.character), ~ str_to_lower(str_replace_all(., ' ', '_'))))")
            return " %>%\n  ".join(operations) if operations else "# No row operations needed"
        
        elif func_name == 'clean_all':
            return "# clean_all() combines column and row operations - see individual operations above"
        
        elif func_name == 'promote_headers':
            row_index = params.get('row_index', 0)
            drop_promoted_row = params.get('drop_promoted_row', True)
            
            if row_index == 0 and drop_promoted_row:
                # Common case: promote first row and remove it
                return "row_to_names(row_number = 1, remove_row = TRUE)"
            elif row_index == 0 and not drop_promoted_row:
                # Promote first row but keep it
                return "row_to_names(row_number = 1, remove_row = FALSE)"
            else:
                # Custom row index
                r_row_num = row_index + 1  # R is 1-indexed
                remove_str = "TRUE" if drop_promoted_row else "FALSE"
                return f"row_to_names(row_number = {r_row_num}, remove_row = {remove_str})"
        
        elif func_name == 'rename_column':
            old_name = params.get('old')
            new_name = params.get('new')
            if old_name is None or new_name is None:
                return "# rename_column requires 'old' and 'new' parameters"
            return f"rename({self._format_r_identifier(new_name)} = {self._format_r_identifier(old_name)})"

        elif func_name == 'reorder_columns':
            columns = params.get('columns') or []
            if not columns:
                return "# reorder_columns requires a non-empty column list"
            ordered = ", ".join(self._format_r_identifier(col) for col in columns)
            return f"select({ordered}, everything())"

        elif func_name == 'drop_columns':
            columns = params.get('columns') or []
            if not columns:
                return "# drop_columns requires a non-empty column list"
            vector = self._format_r_string_vector(columns)
            return f"select(-all_of({vector}))"

        elif func_name == 'keep_columns':
            columns = params.get('columns') or []
            if not columns:
                return "# keep_columns requires a non-empty column list"
            vector = self._format_r_string_vector(columns)
            return f"select(all_of({vector}))"
        
        else:
            # For unknown operations, add a comment
            return f"# TODO: Implement R equivalent for {func_name}({params})"
    
    def export_code(self, filename):
        """
        Export the generated code to a file.
        
        Args:
            filename (str): The name of the file to export the code to.
        """
        
        templates_dir = Path(__file__).parent / "templates"
        env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        trim_blocks=True,     # removes significant blank lines
        lstrip_blocks=True    # trims leading whitespace from blocks
        )
        
        context = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "steps": self.generate_code()
            }
    
        if self.language == 'python':
            template = env.get_template("python_pipeline.py.j2")
            with open(filename, 'w') as f:
                f.write(template.render(context))
        elif self.language == 'R':
            template = env.get_template("R_pipeline.R.j2")
            with open(filename, 'w') as f:
                f.write(template.render(context))
        

if __name__ == "__main__":
    
    # Example usage
    # Assuming Broom class and its methods are defined in databroom.core.broom
    test_df = Broom.from_file('dataset.csv')
    test_df = test_df.remove_empty_cols(threshold=0.9).standardize_column_names().normalize_column_names().standardize_values()
    code = CodeGenerator('python')
    #print(test_df.get_history())
    print(code.templates)
    history = code.load_history(test_df.get_history())
    #print(history)

    print(code.generate_code())
    print(type(test_df))
    code.export_code(r'..\..\generated_code.py')
