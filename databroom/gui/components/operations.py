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
    """Render the Clean All quick access button with confirmation."""
    if st.session_state.get('confirm_clean_all', False):
        st.warning("⚠️ Are you sure you want to apply all cleaning operations? This will clean both columns and rows.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Clean All", use_container_width=True, type="primary"):
                debug_log("Clean All confirmed", "GUI")
                st.session_state.last_interaction = 'clean_all'
                debug_log(f"Before operation - Shape: {st.session_state.broom.get_df().shape}", "GUI")

                st.session_state.broom.clean_all()

                debug_log(f"After operation - Shape: {st.session_state.broom.get_df().shape}", "GUI")
                sync_history()
                st.session_state.cleaning_history.append("Applied full clean on columns and rows")
                debug_log(f"Synced history - Total operations: {len(st.session_state.cleaning_history)}", "GUI")
                st.success("🧹 Complete cleaning applied!")
                st.session_state['confirm_clean_all'] = False
                st.rerun()
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state['confirm_clean_all'] = False
                st.rerun()
    else:
        if st.button(
            "🧹 Clean All",
            help="Applies all cleaning operations to both columns and rows",
            use_container_width=True,
            type="primary"
        ):
            st.session_state['confirm_clean_all'] = True
            st.rerun()

def _render_structure_operations():
    """Render structure operations like promote_headers."""
    with st.expander("📋 **Structure Operations**", expanded=False):
        st.caption("Fix data structure and format issues")
        
        _render_promote_headers()
        _render_rename_column()
        _render_reorder_columns()
        _render_drop_columns()
        _render_keep_columns()

def _render_promote_headers():
    """Render promote headers operation."""
    with st.expander("📌 Promote Headers", expanded=False):
        df = st.session_state.broom.get_df()
        if df.empty:
            st.info("Load data before promoting headers.")
            return

        max_rows = len(df) - 1
        default_row = st.session_state.get('promote_headers_row_index', 0)
        default_row = min(max(default_row, 0), max_rows)

        row_index = st.number_input(
            "Row index to promote (0 = first row)",
            min_value=0,
            max_value=max_rows,
            value=default_row,
            help="Select which row will become the new header row",
            key="promote_headers_row_index_input",
        )
        st.session_state['promote_headers_row_index'] = row_index

        drop_row = st.checkbox(
            "Remove promoted row after setting as headers",
            value=st.session_state.get('promote_headers_drop_row', True),
            help="Uncheck if you want to keep the original row in the dataset",
            key="promote_headers_drop_row_checkbox",
        )
        st.session_state['promote_headers_drop_row'] = drop_row

        if st.button(
            "Apply Promote Headers",
            use_container_width=True,
            key="promote_headers_apply_btn"
        ):
            debug_log("Promote Headers confirmed", "GUI")
            st.session_state.last_interaction = 'promote_headers'

            if not hasattr(st.session_state.broom, 'promote_headers'):
                st.error("🔄 Please refresh the page - the promote_headers operation requires a page reload.")
                st.info("💡 Tip: Press F5 or refresh your browser to reload the latest code.")
                return

            debug_log(f"Before operation - Columns: {list(df.columns)}", "GUI")
            st.session_state.broom.promote_headers(
                row_index=int(row_index),
                drop_promoted_row=bool(drop_row)
            )
            debug_log(f"After operation - Columns: {list(st.session_state.broom.get_df().columns)}", "GUI")
            sync_history()
            st.session_state.cleaning_history.append(f"Promoted row {int(row_index)} to column headers")
            st.success(f"📌 Row {int(row_index)} promoted to headers!")
            st.rerun()

def _render_rename_column():
    """Render rename column operation."""
    df = st.session_state.broom.get_df()
    columns = list(df.columns)

    with st.expander("✏️ Rename Column", expanded=False):
        if not columns:
            st.info("Load data to enable column rename.")
            return

        default_old = st.session_state.get('rename_column_old', columns[0])
        if default_old not in columns:
            default_old = columns[0]

        old = st.selectbox(
            "Column to rename",
            options=columns,
            index=columns.index(default_old),
            key="rename_column_old_select"
        )
        st.session_state['rename_column_old'] = old

        new_value = st.text_input(
            "New column name",
            value=st.session_state.get('rename_column_new', ""),
            help="Provide a unique name for the column",
            key="rename_column_new_input"
        ).strip()
        st.session_state['rename_column_new'] = new_value

        if st.button(
            "Apply Rename",
            use_container_width=True,
            key="rename_column_apply_btn"
        ):
            debug_log("Rename Column confirmed", "GUI")
            st.session_state.last_interaction = 'rename_column'

            if not new_value:
                st.error("❌ Provide a new column name.")
                return

            try:
                st.session_state.broom.rename_column(old=old, new=new_value)
            except ValueError as exc:
                st.error(f"❌ {exc}")
                return

            sync_history()
            st.session_state.cleaning_history.append(f"Renamed column '{old}' to '{new_value}'")
            st.success(f"✏️ Column '{old}' renamed to '{new_value}'")
            st.rerun()

def _render_reorder_columns():
    """Render reorder columns operation."""
    df = st.session_state.broom.get_df()
    columns = list(df.columns)

    with st.expander("🔀 Reorder Columns", expanded=False):
        if not columns:
            st.info("Load data to reorder columns.")
            return

        preset = [
            col for col in st.session_state.get('reorder_columns_selection', columns)
            if col in columns
        ]
        if not preset:
            preset = columns

        selection = st.multiselect(
            "Select columns in the desired leading order",
            options=columns,
            default=preset,
            help="Choose the columns that should appear first; other columns keep their relative order",
            key="reorder_columns_multiselect"
        )
        st.session_state['reorder_columns_selection'] = selection

        if st.button(
            "Apply Reorder",
            use_container_width=True,
            key="reorder_columns_apply_btn"
        ):
            debug_log("Reorder Columns confirmed", "GUI")
            st.session_state.last_interaction = 'reorder_columns'

            if not selection:
                st.error("❌ Select at least one column to reorder.")
                return

            try:
                st.session_state.broom.reorder_columns(columns=selection)
            except ValueError as exc:
                st.error(f"❌ {exc}")
                return

            sync_history()
            if selection:
                lead = ", ".join(selection)
                st.session_state.cleaning_history.append(f"Reordered columns; moved {lead} to the front")
            else:
                st.session_state.cleaning_history.append("Reordered columns")
            st.success("🔀 Columns reordered")
            st.rerun()

def _render_drop_columns():
    """Render drop columns operation."""
    df = st.session_state.broom.get_df()
    columns = list(df.columns)

    with st.expander("🗑️ Drop Columns", expanded=False):
        if not columns:
            st.info("Load data to drop columns.")
            return

        preset = [
            col for col in st.session_state.get('drop_columns_selection', [])
            if col in columns
        ]

        selection = st.multiselect(
            "Columns to drop",
            options=columns,
            default=preset,
            help="Choose the columns that should be removed from the dataset",
            key="drop_columns_multiselect"
        )
        st.session_state['drop_columns_selection'] = selection

        if st.button(
            "Apply Drop Columns",
            use_container_width=True,
            key="drop_columns_apply_btn"
        ):
            debug_log("Drop Columns confirmed", "GUI")
            st.session_state.last_interaction = 'drop_columns'

            if not selection:
                st.error("❌ Select at least one column to drop.")
                return

            try:
                st.session_state.broom.drop_columns(columns=selection)
            except ValueError as exc:
                st.error(f"❌ {exc}")
                return

            sync_history()
            joined = ", ".join(selection)
            st.session_state.cleaning_history.append(f"Dropped columns {joined}")
            st.success(f"🗑️ Dropped columns: {joined}")
            st.rerun()

def _render_keep_columns():
    """Render keep columns operation."""
    df = st.session_state.broom.get_df()
    columns = list(df.columns)

    with st.expander("📌 Keep Columns", expanded=False):
        if not columns:
            st.info("Load data to select columns to keep.")
            return

        preset = [
            col for col in st.session_state.get('keep_columns_selection', columns)
            if col in columns
        ]
        if not preset:
            preset = columns

        selection = st.multiselect(
            "Columns to keep (order matters)",
            options=columns,
            default=preset,
            help="Only the selected columns will remain; order is preserved as chosen",
            key="keep_columns_multiselect"
        )
        st.session_state['keep_columns_selection'] = selection

        if st.button(
            "Apply Keep Columns",
            use_container_width=True,
            key="keep_columns_apply_btn"
        ):
            debug_log("Keep Columns confirmed", "GUI")
            st.session_state.last_interaction = 'keep_columns'

            if not selection:
                st.error("❌ Select at least one column to keep.")
                return

            try:
                st.session_state.broom.keep_columns(columns=selection)
            except ValueError as exc:
                st.error(f"❌ {exc}")
                return

            sync_history()
            joined = ", ".join(selection)
            st.session_state.cleaning_history.append(f"Kept columns {joined}")
            st.success(f"📌 Retained columns: {joined}")
            st.rerun()

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
                st.session_state.cleaning_history.append("Tidied column names")
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
        
        _render_remove_empty_rows()

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
                st.session_state.cleaning_history.append("Tidied row values")
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

def _render_remove_empty_rows():
    """Render remove empty rows operation."""
    with st.expander("🗑️ Remove Empty Rows", expanded=False):
        
        # Threshold slider
        threshold = st.slider(
            "Empty Row Threshold",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.get('remove_empty_rows_threshold', 0.9),
            step=0.05,
            help="Keep rows properly populated (0.9 = keep dense rows, drop sparse ones)",
            key="remove_empty_rows_slider"
        )
        st.session_state['remove_empty_rows_threshold'] = threshold

        if st.button(
            "Apply Remove Empty Rows",
            use_container_width=True,
            key="remove_empty_rows_btn"
        ):
            debug_log("Remove Empty Rows clicked", "GUI")
            st.session_state.last_interaction = 'remove_empty_rows'
            
            # Use threshold
            st.session_state.broom.remove_empty_rows(threshold=threshold)
            
            sync_history()
            st.session_state.cleaning_history.append(f"Removed empty rows (threshold={threshold})")
            st.success("🗑️ Empty rows removed!")
            st.rerun()
