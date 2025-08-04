"""
Main Databroom GUI Application - Modularized Version
"""

import streamlit as st

# Development path setup (only when run directly)
if __name__ == "__main__" and __package__ is None:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from databroom.core.debug_logger import debug_log

# Import modular components
from databroom.gui.utils.styles import setup_page_config, apply_custom_styles
from databroom.gui.utils.session import initialize_session_state, is_data_loaded
from databroom.gui.components.file_upload import render_file_upload
from databroom.gui.components.operations import render_operations
from databroom.gui.components.controls import render_controls
from databroom.gui.components.tabs import render_data_tabs

def main():
    """Main application entry point."""
    debug_log("Starting Databroom application", "GUI")
    
    # Setup page configuration
    setup_page_config()
    debug_log("Streamlit page config set", "GUI")
    
    # Apply custom styles
    apply_custom_styles()
    
    # Page header
    st.title("🧹 Databroom")
    st.markdown("*DataFrame cleaning assistant with one-click code export*")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar for file upload and operations
    with st.sidebar:
        render_file_upload()
        
        # Show operations if file is loaded
        if is_data_loaded():
            render_operations()
            
            st.markdown("---")
            render_controls()
    
    # Main content area
    if is_data_loaded():
        render_data_tabs()
    else:
        _render_welcome_screen()

def _render_welcome_screen():
    """Render the welcome screen when no data is loaded."""
    st.markdown("""
    ## Welcome to Databroom! 🧹
    
    Upload a data file using the sidebar to get started with cleaning your DataFrame.
    
    ### Supported Operations:
    - **Structure Operations** - Fix data format issues (promote headers, etc.)
    - **Column Operations** - Clean column names and remove empty columns
    - **Row Operations** - Clean row data and remove empty rows
    - **Complete Cleaning** - Apply all operations with one click
    
    ### Supported File Types:
    - CSV files (`.csv`)
    - Excel files (`.xlsx`, `.xls`)
    - JSON files (`.json`)
    
    ### Features:
    - **Interactive GUI** - Visual data cleaning with live preview
    - **Code Generation** - Export reproducible Python/pandas and R/tidyverse code
    - **History Tracking** - Undo operations and track cleaning steps
    - **One-click Export** - Download cleaned data and generated scripts
    """)

if __name__ == "__main__":
    main()