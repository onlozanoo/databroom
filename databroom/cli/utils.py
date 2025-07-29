# databroom/cli/utils.py

import os
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from databroom.core.broom import Broom
from databroom.generators.base import CodeGenerator
from .config import (
    FILE_TYPE_MAPPING, 
    SUPPORTED_INPUT_FORMATS, 
    SUPPORTED_OUTPUT_FORMATS,
    SUPPORTED_LANGUAGES,
    MESSAGES
)

console = Console()

def validate_input_file(file_path: str) -> bool:
    """Valida que el archivo de entrada exista y tenga formato soportado"""
    if not os.path.exists(file_path):
        console.print(MESSAGES['file_not_found'].format(path=file_path), style="red")
        return False
    
    ext = Path(file_path).suffix.lower()
    if ext not in SUPPORTED_INPUT_FORMATS:
        console.print(
            MESSAGES['invalid_format'].format(
                ext=ext, 
                formats=', '.join(SUPPORTED_INPUT_FORMATS)
            ), 
            style="red"
        )
        return False
    
    return True

def validate_output_file(file_path: str) -> bool:
    """Valida que el archivo de salida tenga formato soportado"""
    ext = Path(file_path).suffix.lower()
    if ext not in SUPPORTED_OUTPUT_FORMATS:
        console.print(
            MESSAGES['invalid_format'].format(
                ext=ext, 
                formats=', '.join(SUPPORTED_OUTPUT_FORMATS)
            ), 
            style="red"
        )
        return False
    
    # Verificar que el directorio padre exista
    parent_dir = Path(file_path).parent
    if not parent_dir.exists():
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            console.print(f"Cannot create output directory: {e}", style="red")
            return False
    
    return True

def load_dataframe(file_path: str, **kwargs) -> Optional[Broom]:
    """Carga DataFrame usando factory methods de Broom"""
    try:
        # Auto-detección usando el método from_file de Broom
        broom = Broom.from_file(file_path, **kwargs)
        return broom
    except Exception as e:
        console.print(f"Error loading file: {e}", style="red")
        return None

def save_dataframe(df: pd.DataFrame, output_path: str) -> bool:
    """Guarda DataFrame según la extensión del archivo"""
    try:
        ext = Path(output_path).suffix.lower()
        
        if ext == '.csv':
            df.to_csv(output_path, index=False)
        elif ext in ['.xlsx', '.xls']:
            df.to_excel(output_path, index=False)
        elif ext == '.json':
            df.to_json(output_path, orient='records', indent=2)
        else:
            console.print(f"Unsupported output format: {ext}", style="red")
            return False
        
        console.print(MESSAGES['saved_data'].format(path=output_path), style="green")
        return True
        
    except Exception as e:
        console.print(f"Error saving file: {e}", style="red")
        return False

def generate_and_save_code(broom: Broom, output_path: str, language: str) -> bool:
    """Genera y guarda código usando CodeGenerator"""
    try:
        # Normalizar idioma
        lang_map = {'py': 'python', 'python': 'python', 'r': 'r'}
        lang = lang_map.get(language.lower(), 'python')
        
        if lang not in SUPPORTED_LANGUAGES:
            console.print(f"Unsupported language: {language}", style="red")
            return False
        
        # Generar código usando plantillas Jinja2
        generator = CodeGenerator(language=lang)
        generator.load_history(broom.get_history())
        generator.export_code(output_path)
        
        console.print(MESSAGES['saved_code'].format(path=output_path), style="green")
        return True
        
    except Exception as e:
        console.print(f"Error generating code: {e}", style="red")
        return False

def show_dataframe_info(df: pd.DataFrame, title: str = "DataFrame Info"):
    """Muestra información del DataFrame en formato tabla"""
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    
    # Información básica
    table.add_row("Shape", f"{df.shape[0]:,} rows × {df.shape[1]:,} columns")
    table.add_row("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    table.add_row("Null Values", f"{df.isnull().sum().sum():,}")
    table.add_row("Duplicate Rows", f"{df.duplicated().sum():,}")
    
    # Tipos de datos
    dtype_counts = df.dtypes.value_counts()
    dtype_str = ", ".join([f"{count} {dtype}" for dtype, count in dtype_counts.items()])
    table.add_row("Data Types", dtype_str)
    
    console.print(table)

def show_processing_summary(summary: Dict[str, Any]):
    """Muestra resumen de procesamiento"""
    if not summary['operations_applied']:
        return
    
    # Panel principal
    summary_text = f"""
[bold green]Operations Applied:[/bold green] {len(summary['operations_applied'])}
{', '.join(summary['operations_applied'])}

[bold blue]Data Changes:[/bold blue]
Shape: {summary['shape_before']} -> {summary['shape_after']}
Rows: {summary['rows_changed']:+d} ({'+' if summary['rows_changed'] >= 0 else ''}{summary['rows_changed']})
Columns: {summary['cols_changed']:+d} ({'+' if summary['cols_changed'] >= 0 else ''}{summary['cols_changed']})

[bold yellow]Memory:[/bold yellow]
Before: {summary['memory_before'] / 1024**2:.2f} MB
After: {summary['memory_after'] / 1024**2:.2f} MB
Saved: {(summary['memory_before'] - summary['memory_after']) / 1024**2:.2f} MB
    """.strip()
    
    console.print(Panel(
        summary_text,
        title=MESSAGES['summary_title'],
        border_style="green",
        padding=(1, 2)
    ))

def detect_file_type(file_path: str) -> Optional[str]:
    """Detecta tipo de archivo por extensión"""
    ext = Path(file_path).suffix.lower()
    return FILE_TYPE_MAPPING.get(ext)

def format_size(size_bytes: int) -> str:
    """Formatea tamaño de archivo en formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"