"""
Data cleaning operations component for Databroom GUI.
"""

import streamlit as st
from databroom.core.debug_logger import debug_log
from databroom.gui.utils.session import sync_history

def render_operations():
    """Render all cleaning operations in organized sections."""
    st.header("🧹 Cleaning Operations")
    
    # Quick access - most common operation
    _render_quick_access()
    
    st.markdown("---")
    
    # Organized operations by category
    st.subheader("🎯 Targeted Operations")
    st.caption("Choose specific cleaning operations by category")
    
    _render_structure_operations()
    _render_column_operations()
    _render_row_operations()

def _render_quick_access():
    """Render the Clean All quick access button."""
    if st.button(
        "🧹 Clean All",
        help="Applies all cleaning operations to both columns and rows",
        use_container_width=True,
        type="primary"
    ):
        debug_log("Clean All clicked", "GUI")
        st.session_state.last_interaction = 'clean_all'
        debug_log(f"Before operation - Shape: {st.session_state.broom.get_df().shape}", "GUI")
        
        st.session_state.broom.clean_all()
        
        debug_log(f"After operation - Shape: {st.session_state.broom.get_df().shape}", "GUI")
        sync_history()
        st.session_state.cleaning_history.append("GUI: Applied complete cleaning (clean_all)")
        debug_log(f"Synced history - Total operations: {len(st.session_state.cleaning_history)}", "GUI")
        st.success("🧹 Complete cleaning applied!")
        st.rerun()

def _render_structure_operations():
    """Render structure operations like promote_headers."""
    with st.expander("📋 **Structure Operations**", expanded=False):
        st.caption("Fix data structure and format issues")
        
        _render_promote_headers()

def _render_promote_headers():
    """Render promote headers operation."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button(
            "📌 Promote Headers",
            help="Convert a data row to column headers",
            use_container_width=True,
            key="promote_headers_btn"
        ):
            debug_log("Promote Headers clicked", "GUI")
            st.session_state.last_interaction = 'promote_headers'
            
            # Check if promote_headers method exists (defensive programming)
            if not hasattr(st.session_state.broom, 'promote_headers'):
                st.error("🔄 Please refresh the page - the promote_headers operation requires a page reload.")
                st.info("💡 Tip: Press F5 or refresh your browser to reload the latest code.")
                return
            
            # Get parameters from session state
            row_index = st.session_state.get('promote_headers_row_index', 0)
            drop_row = st.session_state.get('promote_headers_drop_row', True)
            
            # Validate row_index
            max_rows = len(st.session_state.broom.get_df())
            if row_index >= max_rows:
                st.error(f"❌ Row index {row_index} is out of range. Maximum row index is {max_rows - 1}")
                return
            
            debug_log(f"Before operation - Columns: {list(st.session_state.broom.get_df().columns)}", "GUI")
            st.session_state.broom.promote_headers(
                row_index=row_index,
                drop_promoted_row=drop_row
            )
            debug_log(f"After operation - Columns: {list(st.session_state.broom.get_df().columns)}", "GUI")
            sync_history()
            st.session_state.cleaning_history.append(f"GUI: Promoted row {row_index} to headers (promote_headers)")
            debug_log(f"Synced history - Total operations: {len(st.session_state.cleaning_history)}", "GUI")
            st.success(f"📌 Row {row_index} promoted to headers!")
            st.rerun()
    
    with col2:
        if st.button("⚙️", help="Configure promote headers options", key="config_promote_headers"):
            st.session_state['show_promote_headers_config'] = not st.session_state.get('show_promote_headers_config', False)
            st.rerun()
    
    # Configuration for promote headers
    if st.session_state.get('show_promote_headers_config', False):
        st.markdown("**Promote Headers Configuration:**")
        st.session_state['promote_headers_row_index'] = st.number_input(
            "Row index to promote (0 = first row)", 
            min_value=0, 
            max_value=max(0, len(st.session_state.broom.get_df()) - 1),
            value=st.session_state.get('promote_headers_row_index', 0),
            help="Which row to use as column headers"
        )
        st.session_state['promote_headers_drop_row'] = st.checkbox(
            "Remove promoted row after setting as headers", 
            value=st.session_state.get('promote_headers_drop_row', True),
            help="Delete the row after promoting it to headers"
        )

def _render_column_operations():
    """Render column cleaning operations."""
    with st.expander("📝 **Column Operations**", expanded=False):
        st.caption("Clean and standardize column names")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button(
                "📝 Clean Columns",
                help="Clean column names: snake_case + remove accents + remove empty",
                use_container_width=True,
                key="clean_columns_btn"
            ):
                debug_log("Clean Columns clicked", "GUI")
                st.session_state.last_interaction = 'clean_columns'
                
                # Advanced options
                empty_threshold = st.session_state.get('clean_cols_threshold', 0.9)
                no_snake_case = st.session_state.get('no_snake_case_cols', False)
                no_remove_accents = st.session_state.get('no_remove_accents_cols', False)
                no_remove_empty = st.session_state.get('no_remove_empty_cols', False)
                
                debug_log(f"Before operation - Columns: {list(st.session_state.broom.get_df().columns)}", "GUI")
                st.session_state.broom.clean_columns(
                    remove_empty=not no_remove_empty,
                    empty_threshold=empty_threshold,
                    snake_case=not no_snake_case,
                    remove_accents=not no_remove_accents
                )
                debug_log(f"After operation - Columns: {list(st.session_state.broom.get_df().columns)}", "GUI")
                sync_history()
                st.session_state.cleaning_history.append("GUI: Cleaned column names (clean_columns)")
                debug_log(f"Synced history - Total operations: {len(st.session_state.cleaning_history)}", "GUI")
                st.success("📝 Column names cleaned!")
                st.rerun()
        
        with col2:
            if st.button("⚙️", help="Configure column cleaning options", key="config_clean_columns"):
                st.session_state['show_column_advanced'] = not st.session_state.get('show_column_advanced', False)
                st.rerun()
        
        # Advanced column options
        if st.session_state.get('show_column_advanced', False):
            st.markdown("**Column Cleaning Configuration:**")
            st.session_state['clean_cols_threshold'] = st.slider(
                "Empty threshold", 0.0, 1.0, 
                value=st.session_state.get('clean_cols_threshold', 0.9), 
                step=0.1,
                help="Columns with more missing values will be removed",
                key="col_threshold_slider"
            )
            st.session_state['no_snake_case_cols'] = st.checkbox(
                "Keep original column case", 
                value=st.session_state.get('no_snake_case_cols', False),
                help="Don't convert to snake_case",
                key="no_snake_cols_check"
            )
            st.session_state['no_remove_accents_cols'] = st.checkbox(
                "Keep accents in columns", 
                value=st.session_state.get('no_remove_accents_cols', False),
                help="Don't remove accents from column names",
                key="no_accents_cols_check"
            )
            st.session_state['no_remove_empty_cols'] = st.checkbox(
                "Keep empty columns", 
                value=st.session_state.get('no_remove_empty_cols', False),
                help="Don't remove empty columns",
                key="no_empty_cols_check"
            )

def _render_row_operations():
    """Render row cleaning operations."""
    with st.expander("📄 **Row Operations**", expanded=False):
        st.caption("Clean and standardize row data")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button(
                "📄 Clean Rows",
                help="Clean row data: snake_case + remove accents + remove empty",
                use_container_width=True,
                key="clean_rows_btn"
            ):
                debug_log("Clean Rows clicked", "GUI")
                st.session_state.last_interaction = 'clean_rows'
                
                # Advanced options
                no_snakecase = st.session_state.get('no_snakecase_vals', False)
                no_remove_accents = st.session_state.get('no_remove_accents_vals', False)
                no_clean_text = st.session_state.get('no_clean_text', False)
                no_remove_empty = st.session_state.get('no_remove_empty_rows', False)
                
                debug_log(f"Before operation - Sample values: {st.session_state.broom.get_df().iloc[0].to_dict() if len(st.session_state.broom.get_df()) > 0 else 'No data'}", "GUI")
                st.session_state.broom.clean_rows(
                    remove_empty=not no_remove_empty,
                    clean_text=not no_clean_text,
                    remove_accents=not no_remove_accents,
                    snakecase=not no_snakecase
                )
                debug_log(f"After operation - Sample values: {st.session_state.broom.get_df().iloc[0].to_dict() if len(st.session_state.broom.get_df()) > 0 else 'No data'}", "GUI")
                sync_history()
                st.session_state.cleaning_history.append("GUI: Cleaned row data (clean_rows)")
                debug_log(f"Synced history - Total operations: {len(st.session_state.cleaning_history)}", "GUI")
                st.success("📄 Row data cleaned!")
                st.rerun()
        
        with col2:
            if st.button("⚙️", help="Configure row cleaning options", key="config_clean_rows"):
                st.session_state['show_row_advanced'] = not st.session_state.get('show_row_advanced', False)
                st.rerun()
        
        # Advanced row options
        if st.session_state.get('show_row_advanced', False):
            st.markdown("**Row Cleaning Configuration:**")
            st.session_state['no_snakecase_vals'] = st.checkbox(
                "Keep original text case", 
                value=st.session_state.get('no_snakecase_vals', False),
                help="Don't convert values to snake_case",
                key="no_snake_vals_check"
            )
            st.session_state['no_remove_accents_vals'] = st.checkbox(
                "Keep accents in values", 
                value=st.session_state.get('no_remove_accents_vals', False),
                help="Don't remove accents from text values",
                key="no_accents_vals_check"
            )
            st.session_state['no_clean_text'] = st.checkbox(
                "Skip text cleaning", 
                value=st.session_state.get('no_clean_text', False),
                help="Don't clean text values at all",
                key="no_clean_text_check"
            )
            st.session_state['no_remove_empty_rows'] = st.checkbox(
                "Keep empty rows", 
                value=st.session_state.get('no_remove_empty_rows', False),
                help="Don't remove empty rows",
                key="no_empty_rows_check"
            )