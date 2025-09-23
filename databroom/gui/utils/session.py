"""
Session state management for Databroom GUI.
"""

import streamlit as st
from databroom.core.debug_logger import debug_log

def initialize_session_state():
    """Initialize all session state variables for the GUI."""
    debug_log("Checking session state...", "GUI")
    
    # Core broom instance
    if 'broom' not in st.session_state:
        st.session_state.broom = None
        debug_log("Initialized broom in session state", "GUI")
    
    # Original DataFrame backup
    if 'original_df' not in st.session_state:
        st.session_state.original_df = None
        debug_log("Initialized original_df in session state", "GUI")
    
    # Cleaning history for GUI display
    if 'cleaning_history' not in st.session_state:
        st.session_state.cleaning_history = []
        debug_log("Initialized cleaning_history in session state", "GUI")
    
    # Uploaded file tracking
    if 'uploaded_file_name' not in st.session_state:
        st.session_state.uploaded_file_name = None
        debug_log("Initialized uploaded_file_name in session state", "GUI")
    
    # Last interaction tracking
    if 'last_interaction' not in st.session_state:
        st.session_state.last_interaction = None
        debug_log("Initialized last_interaction in session state", "GUI")

    # Pipeline upload tracking
    if 'uploaded_pipeline' not in st.session_state:
        st.session_state.uploaded_pipeline = None
        debug_log("Initialized uploaded_pipeline in session state", "GUI")

    if 'uploaded_pipeline_name' not in st.session_state:
        st.session_state.uploaded_pipeline_name = None
        debug_log("Initialized uploaded_pipeline_name in session state", "GUI")
    
    debug_log(f"Session state summary - Broom: {st.session_state.broom is not None}, "
              f"History length: {len(st.session_state.cleaning_history)}", "GUI")

def is_data_loaded():
    """Check if data is loaded and ready for operations."""
    return st.session_state.broom is not None

def sync_history():
    """Sync session state history with broom pipeline history."""
    if st.session_state.broom:
        st.session_state.cleaning_history = st.session_state.broom.get_history().copy()
        debug_log(f"Synced history - Total operations: {len(st.session_state.cleaning_history)}", "GUI")

def reset_data():
    """Reset all data-related session state."""
    st.session_state.broom = None
    st.session_state.original_df = None
    st.session_state.cleaning_history = []
    st.session_state.uploaded_file_name = None
    st.session_state.uploaded_pipeline = None
    st.session_state.uploaded_pipeline_name = None
    debug_log("Reset all data in session state", "GUI")