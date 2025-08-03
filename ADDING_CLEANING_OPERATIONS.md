# Guía para añadir nuevas operaciones de limpieza en Databroom

Esta guía explica paso a paso cómo añadir nuevas operaciones de limpieza (`cleaning_ops`) al proyecto Databroom.

## 📋 Resumen del proceso

Para añadir una nueva operación de limpieza a Databroom necesitas hacer cambios en **5 archivos principales**:

1. **`databroom/core/cleaning_ops.py`** - La función principal de limpieza
2. **`databroom/core/broom.py`** - El método wrapper para la API fluida
3. **`databroom/generators/base.py`** - La generación de código R + valores por defecto
4. **`databroom/cli/commands.py`** - Integración CLI (parámetros y flags)
5. **`databroom/gui/app.py`** - Integración GUI (botones y configuración)

## 🔧 Paso a paso detallado

### **Paso 1: Función principal (`cleaning_ops.py`)**

```python
def tu_operacion(df: pd.DataFrame, param1: tipo = default) -> pd.DataFrame:
    """Descripción que aparece en CLI/GUI."""
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    result_df = df.copy()
    # Tu lógica aquí
    return result_df
```

**Requisitos:** Validar entrada, trabajar sobre copia, retornar DataFrame.

### **Paso 2: Método wrapper (`broom.py`)**

```python
def tu_operacion(self, param1=default):
    """Descripción de la operación."""
    debug_log(f"tu_operacion called with params: param1={param1}", "BROOM")
    self.pipeline.execute_operation('tu_operacion', param1=param1)
    return self
```

**Requisitos:** Mismo nombre, llamar a `execute_operation()`, retornar `self`.

### **Paso 3: Código R y defaults (`base.py`)**

**Añadir defaults para código más limpio:**
```python
self.function_defaults = {
    'tu_operacion': {'param1': default_value}
}
```

**Añadir conversión R en `_python_to_r_operation()`:**
```python
elif func_name == 'tu_operacion':
    param1 = params.get('param1', default)
    return f"r_equivalent_function({param1})"
```

### **Paso 4: Integración CLI (`commands.py`)**

**Añadir parámetros:**
```python
@click.option('--tu-operacion', is_flag=True, help='Descripción')
@click.option('--param1', type=click.INT, default=default, help='Param help')
def clean(tu_operacion: bool, param1: int):
```

**Añadir lógica de ejecución:**
```python
if tu_operacion:
    console.print(f"🔧 Aplicando tu_operacion (param1={param1})")
    broom = broom.tu_operacion(param1=param1)
```

### **Paso 5: Integración GUI (`app.py`)**

**En la sección apropiada (Structure/Column/Row Operations):**
```python
# Botón principal
if st.button("🔧 Tu Operación", key="tu_operacion_btn"):
    param1 = st.session_state.get('tu_op_param1', default)
    
    # Validaciones
    if param1 < 0:
        st.error("❌ Parámetro inválido")
        return
    
    # Ejecutar operación
    st.session_state.broom.tu_operacion(param1=param1)
    st.session_state.cleaning_history = st.session_state.broom.get_history().copy()
    st.success("✅ Operación aplicada!")
    st.rerun()

# Configuración de parámetros
if st.session_state.get('show_config', False):
    st.session_state['tu_op_param1'] = st.number_input(
        "Parámetro 1", value=default, help="Descripción"
    )
```

## 🚀 Lo que funciona automáticamente

### ✅ **Automático:**
- **Pipeline**: Carga operaciones dinámicamente
- **Historial**: Se registra automáticamente
- **API programática**: Method chaining funciona inmediatamente

### ⚙️ **Manual:**
- **CLI**: Parámetros y lógica en `commands.py`
- **GUI**: Botones y configuración en `app.py`  
- **Código R**: Equivalente en `base.py`

## 📝 Ejemplo: `promote_headers`

### Implementación resumida:

**1. cleaning_ops.py:**
```python
def promote_headers(df: pd.DataFrame, row_index: int = 0, drop_promoted_row: bool = True) -> pd.DataFrame:
    """Promote a specific row to become the column headers."""
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    if row_index >= len(df):
        raise ValueError(f"row_index out of range")
    
    result_df = df.copy()
    result_df.columns = result_df.iloc[row_index].astype(str).tolist()
    if drop_promoted_row:
        result_df = result_df.drop(result_df.index[row_index]).reset_index(drop=True)
    return result_df
```

**2. broom.py:**
```python
def promote_headers(self, row_index=0, drop_promoted_row=True):
    self.pipeline.execute_operation('promote_headers', 
                                   row_index=row_index, 
                                   drop_promoted_row=drop_promoted_row)
    return self
```

**3. base.py:**
```python
# Defaults
'promote_headers': {'row_index': 0, 'drop_promoted_row': True}

# R conversion
elif func_name == 'promote_headers':
    row_index = params.get('row_index', 0)
    drop_row = params.get('drop_promoted_row', True)
    r_row = row_index + 1  # R is 1-indexed
    remove = "TRUE" if drop_row else "FALSE"
    return f"row_to_names(row_number = {r_row}, remove_row = {remove})"
```

**4. commands.py:**
```python
@click.option('--promote-headers', is_flag=True, help='Promote row to headers')
@click.option('--promote-row-index', type=click.INT, default=0, help='Row index')
def clean(promote_headers: bool, promote_row_index: int):
    if promote_headers:
        broom = broom.promote_headers(row_index=promote_row_index)
```

**5. app.py:**
```python
if st.button("📌 Promote Headers", key="promote_headers_btn"):
    row_index = st.session_state.get('promote_row_index', 0)
    if row_index >= len(st.session_state.broom.get_df()):
        st.error("❌ Row index out of range")
        return
    st.session_state.broom.promote_headers(row_index=row_index)
    st.success("📌 Headers promoted!")
    st.rerun()
```

## ✅ Checklist de verificación

### **Core Implementation:**
- [ ] Función en `cleaning_ops.py` con validaciones
- [ ] Método wrapper en `broom.py` 
- [ ] Equivalente R y defaults en `base.py`

### **Interfaces:**
- [ ] CLI: Parámetros y lógica en `commands.py`
- [ ] GUI: Botón y configuración en `app.py`

### **Testing:**
- [ ] API programática funciona
- [ ] CLI funciona con parámetros
- [ ] GUI responde correctamente
- [ ] Código Python/R se genera
- [ ] Aparece en `databroom list`

### **Problemas comunes:**
1. **Streamlit caching**: Reiniciar servidor tras añadir operaciones
2. **Nombres inconsistentes**: Mismo nombre en todos los archivos
3. **Defaults inconsistentes**: Valores por defecto deben coincidir
4. **Session state**: Usar `st.session_state` para parámetros GUI
5. **R conversion**: No olvidar equivalente R

## 🎯 Ejemplos de uso final

### Programático:
```python
from databroom.core.broom import Broom
broom = Broom.from_csv("data.csv")
result = broom.promote_headers(row_index=1).clean_columns()
```

### CLI:
```bash
databroom clean data.csv --promote-headers --promote-row-index 1 --output-file clean.csv
```

### GUI:
1. Cargar archivo
2. Ir a "Structure Operations" 
3. Configurar parámetros
4. Hacer clic en "📌 Promote Headers"

Con esta guía sistemática, añadir operaciones debería ser sencillo y completo. 🧹✨