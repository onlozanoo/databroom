import streamlit as st
import pandas as pd

# Development path setup (only when run directly)
if __name__ == "__main__" and __package__ is None:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from databroom.core.broom import Broom
from databroom.core.debug_logger import debug_log, get_current_log_file
from databroom.generators.base import CodeGenerator

def main():
    debug_log("Starting Databroom application", "GUI")
    
    st.set_page_config(
        page_title="🧹 Databroom",
        page_icon="🧹",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    debug_log("Streamlit page config set", "GUI")
    
    st.title("🧹 Databroom")
    st.markdown("*DataFrame cleaning assistant with one-click code export*")

    # Style buttons to be full-width and rectangular
    st.markdown(
        """
        <style>
        div.stButton > button {
            width: 100%;
            border-radius: 6px;
        }
        
        /* Warning buttons styling for step back and reset */
        .stButton > button[kind="secondary"] {
            background-color: #ff6b6b !important;
            color: white !important;
            border: 2px solid #ff5252 !important;
            font-weight: 600 !important;
        }
        
        .stButton > button[kind="secondary"]:hover {
            background-color: #ff5252 !important;
            border-color: #e53935 !important;
            box-shadow: 0 4px 8px rgba(255, 107, 107, 0.3) !important;
        }
        
        .stButton > button[kind="secondary"]:active {
            background-color: #e53935 !important;
            transform: translateY(1px) !important;
        }
        
        /* Specific styling for step back button (orange warning) */
        .stButton > button[data-testid="baseButton-secondary"]:has([data-testid*="step-back"]) {
            background-color: #ffa726 !important;
            color: white !important;
            border: 2px solid #ff9800 !important;
            font-weight: 600 !important;
        }
        
        /* Specific styling for reset button (red warning) */
        .stButton > button[data-testid="baseButton-secondary"]:has([data-testid*="reset"]) {
            background-color: #ef5350 !important;
            color: white !important;
            border: 2px solid #f44336 !important;
            font-weight: 600 !important;
        }
        
        /* Enhanced hover effects for warning buttons */
        .stButton > button[data-testid="baseButton-secondary"]:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
            transform: translateY(-1px) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Initialize session state
    debug_log("Checking session state...", "GUI")
    if 'broom' not in st.session_state:
        st.session_state.broom = None
        debug_log("Initialized Databroom in session state", "GUI")
    if 'original_df' not in st.session_state:
        st.session_state.original_df = None
        debug_log("Initialized original_df in session state", "GUI")
    if 'cleaning_history' not in st.session_state:
        st.session_state.cleaning_history = []
        debug_log("Initialized cleaning_history in session state", "GUI")
    if 'uploaded_file_name' not in st.session_state:
        st.session_state.uploaded_file_name = None
        debug_log("Initialized uploaded_file_name in session state", "GUI")
    
    debug_log(f"Current session state - Databroom: {st.session_state.broom is not None}, history_length: {len(st.session_state.cleaning_history)}", "GUI")
    
    # Sidebar for file upload and operations
    with st.sidebar:
        st.header("📁 Data Upload")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['csv', 'xlsx', 'xls', 'json'],
            help="Upload CSV, Excel, or JSON files"
        )
        
        if uploaded_file is not None:
            debug_log(f"File uploaded - Name: {uploaded_file.name}, Type: {uploaded_file.type}, Size: {uploaded_file.size} bytes", "GUI")
            
            # Only process if it's a new file or no broom exists
            if (st.session_state.uploaded_file_name != uploaded_file.name or 
                st.session_state.broom is None):
                debug_log(f"Processing new file: {uploaded_file.name} (previous: {st.session_state.uploaded_file_name})", "GUI")
                
                try:
                    debug_log("Creating broom instance from uploaded file...", "GUI")
                    # Create broom instance
                    broom = Broom.from_file(uploaded_file)
                    debug_log("broom instance created successfully", "GUI")
                    
                    debug_log("Storing in session state...", "GUI")
                    st.session_state.broom = broom
                    st.session_state.original_df = broom.get_df().copy()
                    st.session_state.uploaded_file_name = uploaded_file.name
                    # Sync session state cleaning history with pipeline history
                    st.session_state.cleaning_history = broom.get_history().copy()
                    debug_log(f"DataFrame stored - Shape: {broom.get_df().shape}", "GUI")
                    
                    st.success(f"✅ File loaded: {uploaded_file.name}")
                    st.info(f"Shape: {broom.get_df().shape[0]} rows × {broom.get_df().shape[1]} columns")
                    
                except Exception as e:
                    debug_log(f"Error loading file - {str(e)}", "GUI")
                    st.error(f"Error loading file: {str(e)}")
                    return
            else:
                debug_log(f"File {uploaded_file.name} already processed, skipping re-creation", "GUI")
        
        # Show cleaning operations if file is loaded
        if st.session_state.broom is not None:
            st.header("🧹 Cleaning Operations")
            
            # Control buttons
            col1, col2 = st.columns(2)
            
            with col1:
                # Step back button
                can_step_back = st.session_state.broom.can_step_back()
                
                if can_step_back:
                    st.caption("⚠️ Undo last operation")
                else:
                    st.caption("ℹ️ No operations to undo")
                
                if st.button("↶ Step Back", help="Undo last operation", use_container_width=True, disabled=not can_step_back, type="secondary", key="step-back-btn"):
                    try:
                        st.session_state.broom.step_back()
                        st.session_state.cleaning_history = st.session_state.broom.get_history().copy()
                        st.success("↶ Stepped back to previous state")
                        st.rerun()
                    except ValueError as e:
                        st.error(f"Cannot step back: {e}")
            
            with col2:
                # Reset button
                st.caption("⚠️ Reset all changes")
                
                if st.button("🔄 Reset to Original", help="Reset DataFrame to original state", use_container_width=True, type="secondary", key="reset-btn"):
                    st.session_state.broom.reset()
                    st.session_state.cleaning_history = []
                    st.success("🔄 Reset to original state")
                    st.rerun()

            st.markdown("---")
            
            # QUICK ACCESS - Most common operation
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
                st.session_state.cleaning_history = st.session_state.broom.get_history().copy()
                st.session_state.cleaning_history.append("GUI: Applied complete cleaning (clean_all)")
                debug_log(f"Synced history - Total operations: {len(st.session_state.cleaning_history)}", "GUI")
                st.success("🧹 Complete cleaning applied!")
                st.rerun()
            
            st.markdown("---")
            
            # ORGANIZED OPERATIONS BY CATEGORY
            st.subheader("🎯 Targeted Operations")
            st.caption("Choose specific cleaning operations by category")
            
            # 1. STRUCTURE OPERATIONS
            with st.expander("📋 **Structure Operations**", expanded=False):
                st.caption("Fix data structure and format issues")
                
                # Promote Headers
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
                            st.error("🔄 Please refresh the page - the promote_headers operation requires a page reload to be available.")
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
                        st.session_state.cleaning_history = st.session_state.broom.get_history().copy()
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
            
            # 2. COLUMN OPERATIONS
            with st.expander("📝 **Column Operations**", expanded=False):
                st.caption("Clean and standardize column names")
                
                # Column cleaning button
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
                        st.session_state.cleaning_history = st.session_state.broom.get_history().copy()
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
            
            # 3. ROW/DATA OPERATIONS
            with st.expander("📄 **Row Operations**", expanded=False):
                st.caption("Clean and standardize row data")
                
                # Row cleaning button
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
                        st.session_state.cleaning_history = st.session_state.broom.get_history().copy()
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
            
    
    # Main content area
    if st.session_state.broom is not None:
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Current Data", "📝 History", "🔍 Data Info", "💾 Export Code"])
        
        # Track tab interactions
        if st.session_state.get('current_tab') != tab1:
            st.session_state.last_interaction = 'tab_change'
        
        with tab1:
            st.subheader("Current DataFrame")
            current_df = st.session_state.broom.get_df()
            
            # Show basic stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rows", current_df.shape[0])
            with col2:
                st.metric("Columns", current_df.shape[1])
            with col3:
                st.metric("Missing %", f"{current_df.isnull().mean().mean()*100:.1f}%")
            with col4:
                st.metric("Memory Usage", f"{current_df.memory_usage(deep=True).sum()/1024:.1f} KB")
            
            # Display DataFrame
            st.dataframe(current_df, use_container_width=True, height=400)
            
            # Download cleaned data
            if len(st.session_state.cleaning_history) > 0:
                csv = current_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Cleaned CSV",
                    data=csv,
                    file_name="cleaned_data.csv",
                    mime="text/csv"
                )
        
        with tab2:
            st.subheader("Cleaning History")
            if st.session_state.cleaning_history:
                for i, operation in enumerate(st.session_state.cleaning_history, 1):
                    st.write(f"{i}. {operation}")
                
                # Show technical history from broom
                with st.expander("Technical Details"):
                    history = st.session_state.broom.get_history()
                    for entry in history:
                        st.code(entry, language="text")
            else:
                st.info("No cleaning operations performed yet.")
        
        with tab3:
            st.subheader("Data Information")
            current_df = st.session_state.broom.get_df()
            
            # Data types
            st.write("**Data Types:**")
            dtypes_df = pd.DataFrame({
                'Column': current_df.columns,
                'Type': current_df.dtypes.astype(str),
                'Non-Null Count': current_df.count(),
                'Missing Count': current_df.isnull().sum(),
                'Missing %': (current_df.isnull().sum() / len(current_df) * 100).round(2)
            })
            st.dataframe(dtypes_df, use_container_width=True)
            
            # Sample values
            st.write("**Sample Values:**")
            st.dataframe(current_df.head(10), use_container_width=True)
        
        with tab4:
            st.subheader("Export Cleaned Code")
            
            if len(st.session_state.cleaning_history) > 0:
                # Language selection dropdown
                selected_language = st.selectbox(
                    "Select programming language:",
                    options=["Python/Pandas", "R/Tidyverse"],
                    index=0,
                    help="Choose the programming language for code generation",
                    on_change=lambda: setattr(st.session_state, 'last_interaction', 'language_select')
                )
                
                st.markdown("---")
                
                # Generate code based on selection
                try:
                    if selected_language == "Python/Pandas":
                        debug_log("Generating Python code preview", "GUI")
                        generator = CodeGenerator('python')
                        template_name = "python_pipeline.py.j2"
                        file_extension = ".py"
                        code_language = 'python'
                        download_label = "📥 Download Python Script"
                    else:  # R/Tidyverse
                        debug_log("Generating R code preview", "GUI")
                        generator = CodeGenerator('R')
                        template_name = "R_pipeline.R.j2"
                        file_extension = ".R"
                        code_language = 'r'
                        download_label = "📥 Download R Script"
                    
                    # Generate code
                    history = st.session_state.broom.get_history()
                    generator.load_history(history)
                    code = generator.generate_code()
                    
                    # Generate complete code with imports and file loading
                    from datetime import datetime
                    from jinja2 import Environment, FileSystemLoader
                    from pathlib import Path
                    
                    templates_dir = Path(__file__).parent.parent / "generators" / "templates"
                    env = Environment(loader=FileSystemLoader(str(templates_dir)))
                    template = env.get_template(template_name)
                    
                    # Use actual filename if available
                    filename = st.session_state.uploaded_file_name or "your_data_file.csv"
                    
                    # For R, suggest CSV format for Excel files
                    if selected_language == "R/Tidyverse" and filename.endswith(('.xlsx', '.xls')):
                        filename_for_r = filename.replace('.xlsx', '.csv').replace('.xls', '.csv')
                        st.info("💡 Note: R script uses CSV format. Convert Excel file to CSV for best compatibility.")
                        filename = filename_for_r
                    
                    context = {
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "steps": code,
                        "filename": filename
                    }
                    
                    full_script = template.render(context)
                    
                    # Show preview
                    st.code(full_script, language=code_language)
                    
                    # Download button
                    st.download_button(
                        label=download_label,
                        data=full_script,
                        file_name=f"broom_cleaning_pipeline{file_extension}",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    debug_log(f"Error generating {selected_language} code: {e}", "GUI")
                    st.error(f"Error generating {selected_language} code: {e}")
                
                # Refresh button
                if st.button("🔄 Refresh Code", help="Regenerate the code preview"):
                    st.session_state.last_interaction = 'refresh_code'
                    st.rerun()
            else:
                st.info("Perform some cleaning operations first to generate exportable code.")
    
    else:
        # Welcome screen
        st.markdown("""
        ## Welcome to Databroom! 🧹
        
        Upload a data file using the sidebar to get started with cleaning your DataFrame.
        
        ### Supported Operations:
        - **Remove Empty Columns/Rows** - Clean up sparse data
        - **Standardize Names** - Convert to lowercase with underscores  
        - **Normalize Text** - Remove accents and special characters
        - **And more!** - Additional operations coming soon
        
        ### Supported File Types:
        - CSV files (`.csv`)
        - Excel files (`.xlsx`, `.xls`)
        - JSON files (`.json`)
        """)

if __name__ == "__main__":
    main()
