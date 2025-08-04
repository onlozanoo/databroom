"""
Control buttons component for Databroom GUI.
"""

import streamlit as st
from databroom.core.debug_logger import debug_log
from databroom.gui.utils.session import sync_history

def render_controls():
    """Render step back, reset, and reload control buttons."""
    col1, col2 = st.columns(2)
    
    with col1:
        _render_step_back_button()
    
    with col2:
        _render_reset_button()

def _render_step_back_button():
    """Render the step back button."""
    can_step_back = st.session_state.broom.can_step_back()
    
    if can_step_back:
        st.caption("⚠️ Undo last operation")
    else:
        st.caption("ℹ️ No operations to undo")
    
    if st.button(
        "↶ Step Back", 
        help="Undo last operation", 
        use_container_width=True, 
        disabled=not can_step_back, 
        type="secondary", 
        key="step-back-btn"
    ):
        try:
            st.session_state.broom.step_back()
            sync_history()
            st.success("↶ Stepped back to previous state")
            st.rerun()
        except ValueError as e:
            st.error(f"Cannot step back: {e}")

def _render_reset_button():
    """Render the reset to original button."""
    st.caption("⚠️ Reset all changes")
    
    if st.button(
        "🔄 Reset to Original", 
        help="Reset DataFrame to original state", 
        use_container_width=True, 
        type="secondary", 
        key="reset-btn"
    ):
        st.session_state.broom.reset()
        st.session_state.cleaning_history = []
        st.success("🔄 Reset to original state")
        st.rerun()

def render_reload_button():
    """Render the reload Broom button (for new operations)."""
    st.caption("🔄 Reload with latest code")
    
    if st.button(
        "⚡ Reload Broom", 
        help="Recreate Broom instance with latest operations", 
        use_container_width=True, 
        key="reload-broom-btn"
    ):
        try:
            # Store current DataFrame state
            current_df = st.session_state.broom.get_df()
            
            # Recreate Broom instance with current data (Broom is already imported at module level)
            from databroom.core.broom import Broom
            st.session_state.broom = Broom(current_df)
            st.session_state.cleaning_history = []
            
            st.success("⚡ Broom reloaded with latest operations!")
            st.info("💡 All new operations are now available")
            st.rerun()
        except Exception as e:
            st.error(f"Error reloading Broom: {e}")