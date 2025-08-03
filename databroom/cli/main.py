# databroom/cli/main.py

import typer
from rich.console import Console
from typing import Optional

from .commands import clean_command, list_operations, gui_command
from .config import MESSAGES

# Crear aplicacion principal
app = typer.Typer(
    name="databroom",
    help="[bold]DataFrame cleaning tool[/bold] with [green]code generation[/green]",
    add_completion=False,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]}
)

console = Console()

# Registrar comando principal
app.command(
    "clean", 
    help="[bold green]Clean DataFrame[/bold green] with specified operations and generate code",
    epilog="""
\033[1;33mEXAMPLES:\033[0m

  \033[2m# 1. Smart clean everything (recommended)\033[0m
  \033[32mdatabroom clean\033[0m \033[36mdata.csv\033[0m --clean-all\033[0m \033[34m-o clean.csv\033[0m

  \033[2m# 2. Only column cleaning + generate code\033[0m  
  \033[32mdatabroom clean\033[0m \033[36mmessy.xlsx\033[0m --clean-columns\033[0m \033[34m-c script.py\033[0m

  \033[2m# 3. Row cleaning with custom threshold + R output\033[0m
  \033[32mdatabroom clean\033[0m \033[36mdata.csv\033[0m --clean-rows \033[31m--empty-threshold 0.8\033[0m \033[34m-c script.R -l r\033[0m

  \033[2m# 4. Advanced: disable snake_case conversion\033[0m
  \033[32mdatabroom clean\033[0m \033[36msurvey.csv\033[0m --clean-all \033[31m--no-snakecase --no-snakecase-cols\033[0m \033[33m--verbose\033[0m

  \033[2m# 5. JSON processing with column-only cleaning\033[0m
  \033[32mdatabroom clean\033[0m \033[36mapi.json\033[0m --clean-columns\033[0m \033[34m-c cleaner.py\033[0m

  \033[2m# 6. Quick analysis with info\033[0m
  \033[32mdatabroom clean\033[0m \033[36mdataset.xlsx\033[0m --clean-all --verbose --info\033[0m \033[34m-o clean.csv\033[0m

  \033[2m# 7. Legacy operations still work\033[0m
  \033[32mdatabroom clean\033[0m \033[36mlegacy.csv\033[0m --standardize-column-names --normalize-values\033[0m \033[34m-c analysis.R -l r\033[0m

  \033[2m# 8. Silent comprehensive cleaning\033[0m
  \033[32mdatabroom clean\033[0m \033[36mbig_data.csv\033[0m --clean-all --quiet\033[0m \033[34m-o prod.csv\033[0m

\033[1;35mOPTIONS GROUPS:\033[0m
  \033[1;34m[INPUTS]\033[0m    - File input (csv, xlsx, json, etc.)  
  \033[1;36m[CLEANING]\033[0m  - Data cleaning operations to apply
  \033[1;33m[BEHAVIOR]\033[0m  - Control verbosity and information display
  \033[1;31m[PARAMS]\033[0m    - Arguments for configurable cleaning operations
  \033[34m[OUTPUTS]\033[0m  - File output and code generation options
"""
)(clean_command)

# Registrar comando de información
app.command(
    "list", 
    help="[bold blue]List all available[/bold blue] cleaning operations"
)(list_operations)

# Registrar comando GUI
app.command(
    "gui",
    help="[bold magenta]Launch Streamlit GUI[/bold magenta] for interactive data cleaning"
)(gui_command)

# Comando de versi�n
def version_callback(value: bool):
    """[bold cyan]Show version information[/bold cyan]"""
    if value:
        # Obtener versi�n del proyecto
        try:
            import importlib.metadata
            version = importlib.metadata.version("databroom")
        except:
            version = "0.3.0"  # Fallback
        
        console.print(f"[bold cyan]databroom[/bold cyan] version [green]{version}[/green]")
        console.print("[bold]DataFrame cleaning tool[/bold] with [green]code generation[/green]")
        console.print("[blue]Visit:[/blue] [link]https://github.com/onlozanoo/databroom[/link]")
        raise typer.Exit()

# Callback principal de la aplicaci�n
@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, 
        "--version", "-V",
        callback=version_callback,
        is_eager=True,
        help="[bold cyan]Show version information[/bold cyan]"
    )
):
    """
    [bold cyan]Databroom CLI[/bold cyan] - DataFrame cleaning tool with code generation
    
    Clean your data files with powerful operations and automatically generate
    executable [green]Python[/green] or [blue]R[/blue] code that reproduces your cleaning pipeline.
    
    [bold yellow]Examples:[/bold yellow]
    
        [dim]# Smart clean everything (recommended)[/dim]
        [green]databroom clean[/green] [cyan]data.csv[/cyan] [blue]--clean-all --output-file clean.csv[/blue]
        
        [dim]# Column cleaning and generate Python code[/dim]
        [green]databroom clean[/green] [cyan]messy.xlsx[/cyan] [blue]--clean-columns[/blue] \\
                     [blue]--output-file cleaned.csv --output-code cleaning_script.py[/blue]
        
        [dim]# Advanced cleaning with custom parameters[/dim]
        [green]databroom clean[/green] [cyan]data.csv[/cyan] [blue]--clean-all[/blue] [red]--empty-threshold 0.8 --no-snakecase[/red] \\
                     [blue]--lang r --output-code script.R[/blue]
        
        [dim]# Show available operations[/dim]
        [green]databroom list[/green]
    
    [bold magenta]Get started with:[/bold magenta] [green]databroom clean --help[/green]
    """
    pass

# Entry point para pyproject.toml
def cli_main():
    """[bold]Entry point function for CLI[/bold]"""
    try:
        app()
    except KeyboardInterrupt:
        console.print("Operation cancelled by user", style="yellow")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="red")
        raise typer.Exit(1)

# Para ejecutar directamente el m�dulo
if __name__ == "__main__":
    cli_main()