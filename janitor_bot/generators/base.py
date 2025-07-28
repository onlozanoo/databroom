import pandas as pd
import os
import sys
from pathlib import Path
import ast
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# Development path setup (only when run directly)
if __name__ == "__main__" and __package__ is None:
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

from janitor_bot.core.janitor import Janitor 

class CodeGenerator:
    def __init__(self, language):
        self.language = language
        self.history = {}
        self.templates, self.templates_path = self._load_templates()
        
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
    
    def load_history(self, history):
        
        """
        Load the history of generated code.
        
        Returns:
            list: A list of generated code snippets.
        """
        
        # Filter the history to include only code snippets
        history_funcs = [snippet.split('called')[0].split()[-1] for snippet in history]
        history_params = [snippet.split('Parameters: ')[1].split(". ")[0] for snippet in history]
        self.history = list(zip(history_funcs, history_params))
        
        
        return self.history
    
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
            for func, params_str in self.history:
                # Convert the string to a real dict (safe with ast.literal_eval)
                params_dict = ast.literal_eval(params_str)
                
                # Convert dict to string format key=value, separated by comma
                params_formatted = ', '.join(f"{k}={repr(v)}" for k, v in params_dict.items())
                
                # Build the code line
                if code == "":
                    code = f"janitor_instance = janitor_instance.{func}({params_formatted})"
                else:
                    code += f".{func}({params_formatted})"
                        
                    
        return code
    
    def export_code(self, filename):
        """
        Export the generated code to a file.
        
        Args:
            filename (str): The name of the file to export the code to.
        """
        
        templates_dir = Path(__file__).parent / "templates"
        env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        trim_blocks=True,     # elimina líneas en blanco significativas
        lstrip_blocks=True    # recorta espacios iniciales de bloques
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
    # Assuming Janitor class and its methods are defined in janitor_bot.core.janitor
    test_df = Janitor.from_csv('F:\Documentos\Econometria\Econometria en R\Talleres\Bases\pib_real.csv', sep=',')
    test_df = test_df.remove_empty_cols(threshold=0.9).standarize_column_names().normalize_column_names().standarize_values()
    code = CodeGenerator('python')
    #print(test_df.get_history())
    print(code.templates)
    history = code.load_history(test_df.get_history())
    #print(history)

    print(code.generate_code())
    code.export_code(r'F:\Documentos\Proyectos DS\Janitor\janitor_bot\tests\generators\test_generated_pipeline.py')
