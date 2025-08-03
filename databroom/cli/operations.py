# databroom/cli/operations.py

from typing import Dict, List, Any, Tuple
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from databroom.core.broom import Broom
from .config import CLEANING_OPERATIONS, MESSAGES

console = Console()

class OperationApplier:
    """Maneja la aplicación dinámica de operaciones de limpieza"""
    
    def __init__(self, broom: Broom, verbose: bool = False):
        self.broom = broom
        self.verbose = verbose
        self.operations_applied = []
        self.df_before = broom.get_df().copy()
    
    def apply_operations(self, operation_flags: Dict[str, bool], 
                        operation_params: Dict[str, Any]) -> List[str]:
        """Aplica operaciones seleccionadas con sus parámetros"""
        
        # Filtrar operaciones habilitadas
        selected_operations = [op for op, enabled in operation_flags.items() if enabled]
        
        if not selected_operations:
            console.print(MESSAGES['no_operations'], style="yellow")
            return []
        
        if self.verbose:
            console.print(f"Operations to apply: {', '.join(selected_operations)}")
        
        # Aplicar operaciones con progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            
            for op_name in selected_operations:
                if op_name not in CLEANING_OPERATIONS:
                    console.print(f"Unknown operation: {op_name}", style="yellow")
                    continue
                
                # Mostrar progreso
                task = progress.add_task(
                    MESSAGES['processing'].format(operation=op_name), 
                    total=1
                )
                
                # Aplicar operación
                success = self._apply_single_operation(op_name, operation_params)
                
                if success:
                    self.operations_applied.append(op_name)
                    if self.verbose:
                        console.print(f"{op_name} completed", style="green")
                else:
                    console.print(f"{op_name} failed", style="red")
                
                progress.update(task, completed=1)
        
        return self.operations_applied
    
    def _apply_single_operation(self, op_name: str, operation_params: Dict[str, Any]) -> bool:
        """Aplica una sola operación con manejo de errores"""
        try:
            op_config = CLEANING_OPERATIONS[op_name]
            method = getattr(self.broom, op_config['method'])
            
            # Construir argumentos para la llamada
            method_kwargs = self._build_method_kwargs(op_name, operation_params)
            
            # Llamar método
            if method_kwargs:
                method(**method_kwargs)
            else:
                method()
            
            return True
            
        except Exception as e:
            if self.verbose:
                console.print(f"Error in {op_name}: {str(e)}", style="red")
            return False
    
    def _build_method_kwargs(self, op_name: str, operation_params: Dict[str, Any]) -> Dict[str, Any]:
        """Construye argumentos para llamada a método basado en parámetros CLI"""
        op_config = CLEANING_OPERATIONS[op_name]
        method_kwargs = {}
        
        for param_name, param_info in op_config['params'].items():
            # Buscar parámetro en diferentes formatos posibles
            param_keys = [
                f"{op_name}_{param_name}",  # remove_empty_cols_threshold
                f"{op_name.replace('_', '-')}_{param_name}",  # remove-empty-cols_threshold
                param_name  # threshold (fallback)
            ]
            
            param_value = None
            for key in param_keys:
                if key in operation_params and operation_params[key] is not None:
                    param_value = operation_params[key]
                    break
            
            # Usar valor por defecto si no se especificó
            if param_value is None and param_info['default'] is not None:
                param_value = param_info['default']
            
            # Agregar parámetro si tiene valor
            if param_value is not None:
                method_kwargs[param_name] = self._convert_param_type(
                    param_value, param_info['type']
                )
        
        return method_kwargs
    
    def _convert_param_type(self, value: Any, target_type: type) -> Any:
        """Convierte valor a tipo requerido"""
        if target_type == float:
            return float(value)
        elif target_type == int:
            return int(value)
        elif target_type == bool:
            return bool(value)
        elif target_type == list:
            if isinstance(value, str):
                return value.split(',')
            return value
        else:
            return str(value)
    
    def get_summary(self) -> Dict[str, Any]:
        """Genera resumen de cambios aplicados"""
        df_after = self.broom.get_df()
        
        return {
            'operations_applied': self.operations_applied,
            'shape_before': self.df_before.shape,
            'shape_after': df_after.shape,
            'rows_changed': self.df_before.shape[0] - df_after.shape[0],
            'cols_changed': self.df_before.shape[1] - df_after.shape[1],
            'memory_before': self.df_before.memory_usage(deep=True).sum(),
            'memory_after': df_after.memory_usage(deep=True).sum()
        }

def parse_operation_flags_and_params(cli_args: Dict[str, Any]) -> Tuple[Dict[str, bool], Dict[str, Any]]:
    """Separa flags de operaciones de sus parámetros"""
    operation_flags = {}
    operation_params = {}
    
    # Identificar operation flags
    for op_name in CLEANING_OPERATIONS:
        if op_name in cli_args:
            operation_flags[op_name] = cli_args[op_name]
    
    # Identificar parámetros de operaciones
    for key, value in cli_args.items():
        if key not in operation_flags and '_' in key:
            # Podría ser un parámetro de operación (ej: remove_empty_cols_threshold)
            operation_params[key] = value
        elif key not in CLEANING_OPERATIONS:
            # Otros parámetros generales
            operation_params[key] = value
    
    return operation_flags, operation_params