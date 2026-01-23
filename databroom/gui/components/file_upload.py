"""
File upload component for Databroom GUI with Import Preview.
"""
import streamlit as st
import pandas as pd
from databroom.core.broom import Broom
from databroom.core.debug_logger import debug_log
from databroom.gui.utils.session import sync_history

def render_file_upload():
    """Render the file upload section in the sidebar with preview logic."""
    st.header("📁 Data Upload")
    
    # 1. File Uploader Widget
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'xls', 'json'],
        help="Upload CSV, Excel, or JSON files"
    )
    
    # 2. Handle File State
    if uploaded_file is not None:
        # Check for new file
        if _is_new_file(uploaded_file):
            _initialize_import_state(uploaded_file)
        
        # 3. Render Preview/Config OR Success State
        if st.session_state.get('show_preview', False):
            _render_preview_screen(uploaded_file)
        else:
            # File loaded and accepted
            if st.session_state.broom:
                st.success(f"✅ Loaded: {uploaded_file.name}")
                st.info(f"{st.session_state.broom.get_df().shape[0]} rows × {st.session_state.broom.get_df().shape[1]} cols")
                
                # Option to reload config
                if st.button("🔄 Re-configure Import"):
                    st.session_state['show_preview'] = True
                    st.rerun()

def _is_new_file(uploaded_file):
    """Check if the uploaded file is different from the current one."""
    current = st.session_state.get('uploaded_file_name')
    return current != uploaded_file.name

def _initialize_import_state(uploaded_file):
    """Initialize session state for specific file type."""
    debug_log(f"Initializing import state for {uploaded_file.name}", "GUI")
    st.session_state['uploaded_file_name'] = uploaded_file.name
    st.session_state['show_preview'] = True
    
    # Reset broom to avoid carrying over old data
    st.session_state.broom = None
    
    # Default params based on extension
    params = {}
    if uploaded_file.name.lower().endswith('.csv'):
        params = {'sep': ',', 'encoding': 'utf-8', 'header': 0}
    elif uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
        params = {'header': 0}
    
    st.session_state['import_params'] = params

def _render_preview_screen(uploaded_file):
    """Render the configuration options and data preview."""
    st.markdown("---")
    st.subheader("⚙️ Import Settings")
    
    # render options based on file type
    params = st.session_state.get('import_params', {})
    
    if uploaded_file.name.lower().endswith('.csv'):
        params = _render_csv_options(params)
    elif uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
        params = _render_excel_options(params, uploaded_file)
        
    st.session_state['import_params'] = params
    
    # Preview Data
    st.markdown("### 👁️ Data Preview (First 50 rows)")
    try:
        # CRITICAL: Reset file pointer before reading
        uploaded_file.seek(0)
        
        # Determine strict kwargs for preview (avoid reading whole file)
        preview_kwargs = params.copy()
        if uploaded_file.name.lower().endswith('.csv'):
            preview_kwargs['nrows'] = 50
        elif uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
            preview_kwargs['nrows'] = 50
            
        # Use Broom to read file (it handles various formats via pandas)
        # Note: Broom.from_file creates a Broom instance. We just want the DF for preview.
        # But for robustness, we use Broom factory, then extract DF.
        
        # We need to handle 'nrows' which passed to read_csv/excel.
        # Broom.from_file passes kwargs to pandas read functions.
        preview_broom = Broom.from_file(uploaded_file, **preview_kwargs)
        st.dataframe(preview_broom.get_df())
        
        # Load Button
        if st.button("✅ Load Data", type="primary", use_container_width=True):
            _finalize_load(uploaded_file, params)
            
    except Exception as e:
        st.error(f"❌ Error generating preview: {e}")
        st.caption("Tip: Try changing the Separator or Encoding options above.")

def _render_csv_options(params):
    """Render CSV specific options."""
    col1, col2 = st.columns(2)
    with col1:
        sep = st.selectbox(
            "Separator", 
            options=[',', ';', '\t', '|'], 
            index=[',', ';', '\t', '|'].index(params.get('sep', ',')),
            key='csv_sep'
        )
    with col2:
        encoding = st.selectbox(
            "Encoding", 
            options=['utf-8', 'latin-1', 'cp1252'], 
            index=['utf-8', 'latin-1', 'cp1252'].index(params.get('encoding', 'utf-8')),
            key='csv_encoding'
        )
    
    params['sep'] = sep
    params['encoding'] = encoding
    return params

def _render_excel_options(params, uploaded_file):
    """Render Excel specific options."""
    # For Excel, we might want to select sheets.
    # This requires reading the file once to get sheet names, which might be slow for huge files.
    # For now, we'll stick to simple header config or sheet_name text input if needed.
    # To properly implement sheet selection, we'd need to pd.ExcelFile(uploaded_file).sheet_names
    
    try:
        uploaded_file.seek(0)
        xl = pd.ExcelFile(uploaded_file)
        sheet_names = xl.sheet_names
        
        sheet = st.selectbox(
            "Sheet",
            options=sheet_names,
            index=0,
            key='excel_sheet'
        )
        params['sheet_name'] = sheet
    except Exception:
        # Fallback if ExcelFile fails (though preview will likely fail too)
        pass
        
    return params

def _finalize_load(uploaded_file, params):
    """Finalize the data loading process."""
    try:
        debug_log("Finalizing data load...", "GUI")
        uploaded_file.seek(0)
        
        broom = Broom.from_file(uploaded_file, **params)
        
        st.session_state.broom = broom
        st.session_state.original_df = broom.get_df().copy()
        st.session_state.show_preview = False
        
        sync_history()
        st.session_state.cleaning_history = [] # Reset history on new load
        
        st.success("Data loaded successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error loading final data: {e}")