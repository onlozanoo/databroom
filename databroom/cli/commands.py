# databroom/cli/commands.py

import typer
from typing import Optional, Dict, Any, Annotated
from rich.console import Console
from .config import CLEANING_OPERATIONS, MESSAGES
from .operations import OperationApplier, parse_operation_flags_and_params
from .utils import (
    validate_input_file, 
    validate_output_file,
    load_dataframe,
    save_dataframe,
    generate_and_save_code,
    show_dataframe_info,
    show_processing_summary
)

console = Console()

def clean_command(
    # Input
    input_file: Annotated[str, typer.Argument(help="[bold cyan]Input file path[/bold cyan] ([green]CSV, Excel, JSON[/green])")],
    
    # Output Options
    output_file: Annotated[Optional[str], typer.Option("--output-file", "-o", 
                                                      help=r"[bold blue]\[OUTPUT][/bold blue] Output file path for cleaned data")] = None,
    output_code: Annotated[Optional[str], typer.Option("--output-code", "-c", 
                                                      help=r"[bold blue]\[OUTPUT][/bold blue] Output file path for generated code")] = None,
    lang: Annotated[str, typer.Option("--lang", "-l", 
                                     help=r"[bold blue]\[OUTPUT][/bold blue] Code generation language ([green]py, python, r[/green])")] = "py",
    
    # Behavior Options  
    verbose: Annotated[bool, typer.Option("--verbose", "-v", 
                                         help=r"[bold yellow]\[BEHAVIOR][/bold yellow] Show detailed processing information")] = False,
    quiet: Annotated[bool, typer.Option("--quiet", "-q", 
                                       help=r"[bold yellow]\[BEHAVIOR][/bold yellow] Suppress non-essential output")] = False,
    show_info: Annotated[bool, typer.Option("--info", 
                                           help=r"[bold yellow]\[BEHAVIOR][/bold yellow] Show DataFrame information before and after processing")] = False,
    
    # NEW SIMPLIFIED CLEANING OPERATIONS
    clean_all: Annotated[bool, typer.Option("--clean-all", 
                                           help=r"[bold green]\[SMART CLEAN][/bold green] Clean everything: columns + rows with all operations enabled")] = False,
    clean_columns: Annotated[bool, typer.Option("--clean-columns", 
                                               help=r"[bold green]\[SMART CLEAN][/bold green] Clean column names: snake_case + remove accents + remove empty")] = False,
    clean_rows: Annotated[bool, typer.Option("--clean-rows", 
                                            help=r"[bold green]\[SMART CLEAN][/bold green] Clean row data: snake_case + remove accents + remove empty")] = False,
    
    # ADVANCED COLUMN OPTIONS
    no_snakecase_cols: Annotated[bool, typer.Option("--no-snakecase-cols", 
                                                    help=r"[bold red]\[ADVANCED][/bold red] Disable snake_case conversion for column names")] = False,
    no_remove_accents_cols: Annotated[bool, typer.Option("--no-remove-accents-cols", 
                                                        help=r"[bold red]\[ADVANCED][/bold red] Keep accents in column names")] = False,
    no_remove_empty_cols: Annotated[bool, typer.Option("--no-remove-empty-cols", 
                                                      help=r"[bold red]\[ADVANCED][/bold red] Keep empty columns")] = False,
    
    # ADVANCED ROW OPTIONS  
    no_clean_text: Annotated[bool, typer.Option("--no-clean-text", 
                                               help=r"[bold red]\[ADVANCED][/bold red] Disable text cleaning in row values")] = False,
    no_remove_accents_vals: Annotated[bool, typer.Option("--no-remove-accents-vals", 
                                                        help=r"[bold red]\[ADVANCED][/bold red] Keep accents in text values")] = False,
    no_snakecase: Annotated[bool, typer.Option("--no-snakecase", 
                                              help=r"[bold red]\[ADVANCED][/bold red] Keep original text case and spaces (no snake_case)")] = False,
    no_remove_empty_rows: Annotated[bool, typer.Option("--no-remove-empty-rows", 
                                                      help=r"[bold red]\[ADVANCED][/bold red] Keep empty rows")] = False,
    
    # LEGACY OPERATIONS (for backward compatibility)
    remove_empty_cols: Annotated[bool, typer.Option("--remove-empty-cols", 
                                                   help=r"[bold yellow]\[LEGACY][/bold yellow] Legacy: Remove empty columns (use --clean-columns instead)")] = False,
    remove_empty_rows: Annotated[bool, typer.Option("--remove-empty-rows", 
                                                   help=r"[bold yellow]\[LEGACY][/bold yellow] Legacy: Remove empty rows (use --clean-rows instead)")] = False,
    standardize_column_names: Annotated[bool, typer.Option("--standardize-column-names", 
                                                          help=r"[bold yellow]\[LEGACY][/bold yellow] Legacy: snake_case columns (use --clean-columns instead)")] = False,
    normalize_column_names: Annotated[bool, typer.Option("--normalize-column-names", 
                                                        help=r"[bold yellow]\[LEGACY][/bold yellow] Legacy: Remove accents from columns (use --clean-columns instead)")] = False,
    normalize_values: Annotated[bool, typer.Option("--normalize-values", 
                                                  help=r"[bold yellow]\[LEGACY][/bold yellow] Legacy: Remove accents from values (use --clean-rows instead)")] = False,
    standardize_values: Annotated[bool, typer.Option("--standardize-values", 
                                                    help=r"[bold yellow]\[LEGACY][/bold yellow] Legacy: Clean text values (use --clean-rows instead)")] = False,
    promote_headers: Annotated[bool, typer.Option("--promote-headers", 
                                                 help=r"[bold green]\[NEW][/bold green] Promote first row to become column headers and remove it")] = False,
    
    # PARAMETERS
    empty_threshold: Annotated[float, typer.Option("--empty-threshold", 
                                                  help=r"[bold blue]\[PARAMS][/bold blue] Threshold for removing empty columns (0.9 = 90% missing) [dim]default: 0.9[/dim]")] = 0.9,
    remove_empty_cols_threshold: Annotated[float, typer.Option("--remove-empty-cols-threshold", 
                                                              help=r"[bold yellow]\[LEGACY PARAMS][/bold yellow] Legacy parameter (use --empty-threshold instead)")] = 0.9,
    promote_headers_row_index: Annotated[int, typer.Option("--promote-headers-row-index", 
                                                          help=r"[bold blue]\[PARAMS][/bold blue] Row index to promote as headers (0=first row) [dim]default: 0[/dim]")] = 0,
    promote_headers_drop_row: Annotated[bool, typer.Option("--promote-headers-drop-row/--promote-headers-keep-row", 
                                                          help=r"[bold blue]\[PARAMS][/bold blue] Drop the promoted row after setting as headers [dim]default: drop (True)[/dim]")] = True
):
    """
    [bold]Clean DataFrame with smart operations and generate executable code.[/bold]
    
    [green]QUICK START:[/green]
    • [blue]--clean-all[/blue]     → Does everything (recommended for most cases)
    • [blue]--clean-columns[/blue] → Only clean column names (snake_case + remove accents + remove empty)  
    • [blue]--clean-rows[/blue]    → Only clean row data (snake_case + remove accents + remove empty)
    
    [green]ADVANCED:[/green] Use --no-* flags to disable specific operations:
    • [red]--no-snakecase[/red]         → Keep original text case and spaces (rows)
    • [red]--no-snakecase-cols[/red]    → Keep original column name case and spaces  
    • [red]--no-remove-accents-vals[/red] → Keep accents in text values
    • [red]--no-remove-empty-cols[/red]   → Keep empty columns
    
    [green]OUTPUT:[/green] Use [blue]--output-file[/blue] to save cleaned data and [blue]--output-code[/blue] 
    to generate Python/R scripts that reproduce the cleaning pipeline.
    
    [dim]Legacy individual operations (--remove-empty-cols, etc.) still work but --clean-* is recommended.[/dim]
    """
    
    # Validaciones iniciales
    if not validate_input_file(input_file):
        raise typer.Exit(1)
    
    if output_file and not validate_output_file(output_file):
        raise typer.Exit(1)
    
    if not output_file and not output_code:
        console.print("No output specified. Use --output-file or --output-code", style="yellow")
        console.print("Processing will continue but results won't be saved.", style="dim")
    
    # Cargar datos
    if verbose:
        console.print(f"Loading data from: {input_file}")
    
    janitor = load_dataframe(input_file)
    if janitor is None:
        raise typer.Exit(1)
    
    # Mostrar info inicial si se solicita
    if show_info and not quiet:
        show_dataframe_info(janitor.get_df(), "Original DataFrame")
    
    # Handle new smart operations first
    if clean_all or clean_columns or clean_rows:
        # Use new smart operations
        if verbose:
            selected_ops = []
            if clean_all: selected_ops.append('clean_all')
            if clean_columns: selected_ops.append('clean_columns')
            if clean_rows: selected_ops.append('clean_rows')
            console.print(f"Smart operations: {selected_ops}")
            console.print(f"Parameters: empty_threshold={empty_threshold}")
        
        # Apply smart operations
        if clean_all:
            janitor.clean_all()
        else:
            if clean_columns:
                janitor.clean_columns(
                    remove_empty=not no_remove_empty_cols,
                    empty_threshold=empty_threshold,
                    snake_case=not no_snakecase_cols,
                    remove_accents=not no_remove_accents_cols
                )
            if clean_rows:
                janitor.clean_rows(
                    remove_empty=not no_remove_empty_rows,
                    clean_text=not no_clean_text,
                    remove_accents=not no_remove_accents_vals,
                    snakecase=not no_snakecase
                )
        
        operations_applied = True
        
    else:
        # Fallback to legacy operations
        operation_flags = {
            'remove_empty_cols': remove_empty_cols,
            'remove_empty_rows': remove_empty_rows,
            'standardize_column_names': standardize_column_names,
            'normalize_column_names': normalize_column_names,
            'normalize_values': normalize_values,
            'standardize_values': standardize_values,
            'promote_headers': promote_headers
        }
        
        operation_params = {
            'remove_empty_cols_threshold': remove_empty_cols_threshold,
            'threshold': remove_empty_cols_threshold,
            'promote_headers_row_index': promote_headers_row_index,
            'promote_headers_drop_promoted_row': promote_headers_drop_row
        }
        
        if verbose:
            selected_ops = [op for op, enabled in operation_flags.items() if enabled]
            console.print(f"Legacy operations: {selected_ops}")
            if operation_params:
                console.print(f"Parameters: {operation_params}")
        
        # Aplicar operaciones legacy
        applier = OperationApplier(janitor, verbose=verbose)
        operations_applied = applier.apply_operations(operation_flags, operation_params)
    
    if not operations_applied and not quiet:
        console.print(MESSAGES['no_operations'], style="yellow")
    
    # Mostrar info final si se solicita
    if show_info and not quiet:
        show_dataframe_info(janitor.get_df(), "Cleaned DataFrame")
    
    # Guardar resultados
    success = True
    
    # Guardar datos limpios
    if output_file:
        if not save_dataframe(janitor.get_df(), output_file):
            success = False
    
    # Generar y guardar código
    if output_code and operations_applied:
        if not generate_and_save_code(janitor, output_code, lang):
            success = False
    
    # Mostrar resumen
    if operations_applied and not quiet:
        if 'applier' in locals():
            summary = applier.get_summary()
            show_processing_summary(summary)
        else:
            console.print("Operations completed successfully", style="green")
    
    # Mensaje final
    if not quiet:
        if success and (output_file or output_code):
            console.print(MESSAGES['success'], style="green bold")
        elif operations_applied:
            console.print("Processing completed (no output files specified)", style="green")
    
    # Exit code
    raise typer.Exit(0 if success else 1)

# Comando adicional para mostrar operaciones disponibles
def list_operations():
    """[bold green]List all available cleaning operations grouped by category[/bold green]"""
    from rich.table import Table
    from rich.panel import Panel
    from rich.columns import Columns
    
    # Tabla principal de operaciones
    operations_table = Table(title="[bold magenta]Available Cleaning Operations[/bold magenta]", show_header=True)
    operations_table.add_column("[bold]Operation[/bold]", style="cyan", no_wrap=True)
    operations_table.add_column("[bold]CLI Flag[/bold]", style="green")
    operations_table.add_column("[bold]Parameters[/bold]", style="yellow")
    operations_table.add_column("[bold]Description[/bold]", style="white")
    
    for op_name, op_config in CLEANING_OPERATIONS.items():
        params = list(op_config['params'].keys()) if op_config['params'] else []
        param_str = ", ".join(params) if params else "None"
        
        operations_table.add_row(
            op_name,
            f"--{op_config['cli_flag']}",
            param_str,
            op_config['help']
        )
    
    # Tablas por grupos
    output_options = Table(title=r"[bold blue]\[OUTPUT] Options[/bold blue]", show_header=True, border_style="blue")
    output_options.add_column("[bold]Flag[/bold]", style="green")
    output_options.add_column("[bold]Description[/bold]", style="white")
    output_options.add_row("[green]--output-file, -o[/green]", "Save cleaned DataFrame")
    output_options.add_row("[green]--output-code, -c[/green]", "Generate executable code")
    output_options.add_row("[green]--lang, -l[/green]", "Code language ([cyan]py, r[/cyan])")
    
    behavior_options = Table(title=r"[bold yellow]\[BEHAVIOR] Options[/bold yellow]", show_header=True, border_style="yellow")
    behavior_options.add_column("[bold]Flag[/bold]", style="green")
    behavior_options.add_column("[bold]Description[/bold]", style="white")
    behavior_options.add_row("[green]--verbose, -v[/green]", "Show detailed information")
    behavior_options.add_row("[green]--quiet, -q[/green]", "Suppress output")
    behavior_options.add_row("[green]--info[/green]", "Show DataFrame statistics")
    
    params_options = Table(title=r"[bold red]\[PARAMS] Options[/bold red]", show_header=True, border_style="red")
    params_options.add_column("[bold]Flag[/bold]", style="green")
    params_options.add_column("[bold]Description[/bold]", style="white")
    params_options.add_row("[green]--remove-empty-cols-threshold[/green]", "Threshold for column removal ([dim]0.0-1.0[/dim])")
    
    # Mostrar todo
    console.print(operations_table)
    console.print("\n")
    
    # Mostrar opciones en columnas
    console.print(Columns([output_options, behavior_options, params_options]))
    
    console.print(f"\n[bold magenta]Total operations available:[/bold magenta] [green]{len(CLEANING_OPERATIONS)}[/green]")
    console.print("[bold yellow]Use multiple flags to chain operations together![/bold yellow]")
    console.print("\n[bold cyan]Quick Examples:[/bold cyan]")
    console.print("  [dim]# Smart clean everything (recommended)[/dim]")
    console.print("  [green]databroom clean[/green] [cyan]data.csv[/cyan] [blue]--clean-all --output-file clean.csv[/blue]")
    console.print()
    console.print("  [dim]# Column cleaning with code generation[/dim]")
    console.print("  [green]databroom clean[/green] [cyan]messy.xlsx[/cyan] [blue]--clean-columns[/blue] \\")
    console.print("                    [blue]--output-code script.py --verbose[/blue]")
    console.print()
    console.print("  [dim]# Advanced options with R output[/dim]")
    console.print("  [green]databroom clean[/green] [cyan]dataset.json[/cyan] [blue]--clean-rows[/blue] [red]--empty-threshold 0.7 --no-snakecase[/red] \\")
    console.print("                    [blue]--output-code analysis.R --lang r[/blue]")
    console.print()
    console.print("[bold green]Tip:[/bold green] Use [yellow]--help[/yellow] on any command for detailed examples and documentation!")

# Función para testing y debugging
def show_available_operations():
    """Debug function to show loaded operations"""
    console.print("Loaded Operations:")
    for op_name, config in CLEANING_OPERATIONS.items():
        console.print(f"  {op_name}: {config['help']}")
        if config['params']:
            for param, info in config['params'].items():
                console.print(f"    - {param}: {info['type'].__name__} = {info['default']}")

def gui_command(
    port: Annotated[Optional[int], typer.Option("--port", "-p", help="Port number for Streamlit server (default: 8501)")] = None,
    no_browser: Annotated[bool, typer.Option("--no-browser", help="Don't automatically open browser")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show detailed server output")] = False
):
    """
    [bold magenta]Launch Streamlit GUI[/bold magenta] for interactive data cleaning.
    
    The GUI provides a user-friendly interface where you can:
    
    [bold cyan]Features:[/bold cyan]
    • [green]Drag & drop file upload[/green] (CSV, Excel, JSON)
    • [blue]Live preview[/blue] of cleaning operations
    • [yellow]Interactive parameter tuning[/yellow] with sliders and inputs  
    • [magenta]Real-time code generation[/magenta] (Python/R)
    • [cyan]One-click download[/cyan] of cleaned data and generated code
    • [green]Operation history tracking[/green] with undo functionality
    
    [bold yellow]Supported Operations:[/bold yellow]
    • Remove empty rows/columns with custom thresholds
    • Standardize and normalize column names
    • Clean and normalize text values
    • Handle missing data with multiple strategies
    
    [bold red]Requirements:[/bold red]
    • Streamlit must be installed: [dim]pip install streamlit[/dim]
    • Web browser for interface access
    
    [bold green]Usage Tips:[/bold green]
    • The GUI runs on [link]http://localhost:8501[/link] by default
    • Use [bold]Ctrl+C[/bold] in terminal to stop the server
    • All operations are reversible through the interface
    • Generated code is immediately downloadable
    
    [bold cyan]Examples:[/bold cyan]
    
        [dim]# Launch GUI on default port[/dim]
        [green]databroom gui[/green]
        
        [dim]# Use custom port[/dim]
        [green]databroom gui[/green] [blue]--port 8502[/blue]
        
        [dim]# Launch without opening browser[/dim]
        [green]databroom gui[/green] [red]--no-browser[/red]
        
        [dim]# Show detailed server logs[/dim]
        [green]databroom gui[/green] [yellow]--verbose[/yellow]
    """
    import subprocess
    import sys
    import os
    from pathlib import Path
    
    # Configurar puerto
    server_port = port or 8501
    
    console.print("[bold magenta]Launching Databroom GUI...[/bold magenta]")
    
    # Encontrar la ruta del archivo GUI
    try:
        # Buscar el archivo de la GUI
        gui_path = Path(__file__).parent.parent / "gui" / "app.py"
        
        if not gui_path.exists():
            console.print("[red]GUI file not found![/red]")
            console.print(f"Expected path: {gui_path}")
            raise typer.Exit(1)
        
        console.print("[green]Starting Streamlit server...[/green]")
        if not no_browser:
            console.print("[dim]The GUI will open in your default web browser.[/dim]")
        else:
            console.print("[dim]Browser auto-open disabled. Navigate manually to the URL below.[/dim]")
        
        console.print(f"[yellow]URL:[/yellow] [link]http://localhost:{server_port}[/link]")
        console.print("[yellow]Tip:[/yellow] Use [bold]Ctrl+C[/bold] to stop the GUI server\n")
        
        # Configurar argumentos de streamlit
        streamlit_args = [
            sys.executable, "-m", "streamlit", "run", str(gui_path),
            "--server.port", str(server_port),
            "--server.headless", str(no_browser).lower(),
            "--server.runOnSave", "true",
            "--browser.gatherUsageStats", "false"
        ]
        
        # Ejecutar streamlit
        try:
            if verbose:
                console.print("[dim]Streamlit command:[/dim]")
                console.print("[dim]" + " ".join(streamlit_args) + "[/dim]\n")
                subprocess.run(streamlit_args, check=True)
            else:
                # Redirigir stdout si no es verbose para output limpio
                with open(os.devnull, 'w') as devnull:
                    subprocess.run(streamlit_args, check=True, stdout=devnull, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error launching GUI: {e}[/red]")
            raise typer.Exit(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]GUI server stopped by user[/yellow]")
            raise typer.Exit(0)
            
    except ImportError:
        console.print("[red]Streamlit not installed![/red]")
        console.print("Install with: [bold]pip install streamlit[/bold]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    # Para testing directo
    list_operations()