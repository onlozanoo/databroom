"""
File upload component for Databroom GUI.
"""

import streamlit as st
from databroom.core.broom import Broom
from databroom.core.debug_logger import debug_log
from databroom.gui.utils.session import sync_history

def render_file_upload():
    """Render the file upload section in the sidebar."""
    st.header("📁 Data Upload")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'xls', 'json'],
        help="Upload CSV, Excel, or JSON files"
    )
    
    if uploaded_file is not None:
        debug_log(f"File uploaded - Name: {uploaded_file.name}, Type: {uploaded_file.type}, "
                  f"Size: {uploaded_file.size} bytes", "GUI")
        
        # Only process if it's a new file or no broom exists
        if (_is_new_file(uploaded_file) or st.session_state.broom is None):
            debug_log(f"Processing new file: {uploaded_file.name} "
                      f"(previous: {st.session_state.uploaded_file_name})", "GUI")
            
            _process_uploaded_file(uploaded_file)
        else:
            debug_log(f"File {uploaded_file.name} already processed, skipping re-creation", "GUI")

def _is_new_file(uploaded_file):
    """Check if the uploaded file is different from the current one."""
    return st.session_state.uploaded_file_name != uploaded_file.name

def _process_uploaded_file(uploaded_file):
    """Process the uploaded file and create a Broom instance."""
    try:
        debug_log("Creating broom instance from uploaded file...", "GUI")
        
        # Create broom instance
        broom = Broom.from_file(uploaded_file)
        debug_log("Broom instance created successfully", "GUI")
        
        # Store in session state
        debug_log("Storing in session state...", "GUI")
        st.session_state.broom = broom
        st.session_state.original_df = broom.get_df().copy()
        st.session_state.uploaded_file_name = uploaded_file.name
        
        # Sync history
        sync_history()
        debug_log(f"DataFrame stored - Shape: {broom.get_df().shape}", "GUI")
        
        # Show success message
        st.success(f"✅ File loaded: {uploaded_file.name}")
        st.info(f"Shape: {broom.get_df().shape[0]} rows × {broom.get_df().shape[1]} columns")
        
    except Exception as e:
        debug_log(f"Error loading file - {str(e)}", "GUI")
        st.error(f"Error loading file: {str(e)}")
        return