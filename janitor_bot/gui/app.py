import streamlit as st
import pandas as pd

# Development path setup (only when run directly)
if __name__ == "__main__" and __package__ is None:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from janitor_bot.core.janitor import Janitor
from janitor_bot.core.debug_logger import debug_log, get_current_log_file
from janitor_bot.generators.base import CodeGenerator

def main():
    debug_log("Starting Janitor Bot application", "GUI")
    
    st.set_page_config(
        page_title="🧹 Janitor Bot",
        page_icon="🧹",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    debug_log("Streamlit page config set", "GUI")
    
    st.title("🧹 Janitor Bot")
    st.markdown("*DataFrame cleaning assistant with one-click code export*")

    # Style buttons to be full-width and rectangular
    st.markdown(
        """
        <style>
        div.stButton > button {
            width: 100%;
            border-radius: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Initialize session state
    debug_log("Checking session state...", "GUI")
    if 'janitor' not in st.session_state:
        st.session_state.janitor = None
        debug_log("Initialized janitor in session state", "GUI")
    if 'original_df' not in st.session_state:
        st.session_state.original_df = None
        debug_log("Initialized original_df in session state", "GUI")
    if 'cleaning_history' not in st.session_state:
        st.session_state.cleaning_history = []
        debug_log("Initialized cleaning_history in session state", "GUI")
    if 'uploaded_file_name' not in st.session_state:
        st.session_state.uploaded_file_name = None
        debug_log("Initialized uploaded_file_name in session state", "GUI")
    if 'last_interaction' not in st.session_state:
        st.session_state.last_interaction = None
        debug_log("Initialized last_interaction in session state", "GUI")
    
    debug_log(f"Current session state - janitor: {st.session_state.janitor is not None}, history_length: {len(st.session_state.cleaning_history)}", "GUI")
    
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
            
            # Only process if it's a new file or no janitor exists
            if (st.session_state.uploaded_file_name != uploaded_file.name or 
                st.session_state.janitor is None):
                debug_log(f"Processing new file: {uploaded_file.name} (previous: {st.session_state.uploaded_file_name})", "GUI")
                
                try:
                    debug_log("Creating Janitor instance from uploaded file...", "GUI")
                    # Create Janitor instance
                    janitor = Janitor.from_file(uploaded_file)
                    debug_log("Janitor instance created successfully", "GUI")
                    
                    debug_log("Storing in session state...", "GUI")
                    st.session_state.janitor = janitor
                    st.session_state.original_df = janitor.get_df().copy()
                    st.session_state.uploaded_file_name = uploaded_file.name
                    # Sync session state cleaning history with pipeline history
                    st.session_state.cleaning_history = janitor.get_history().copy()
                    debug_log(f"DataFrame stored - Shape: {janitor.get_df().shape}", "GUI")
                    
                    st.success(f"✅ File loaded: {uploaded_file.name}")
                    st.info(f"Shape: {janitor.get_df().shape[0]} rows × {janitor.get_df().shape[1]} columns")
                    
                except Exception as e:
                    debug_log(f"Error loading file - {str(e)}", "GUI")
                    st.error(f"Error loading file: {str(e)}")
                    return
            else:
                debug_log(f"File {uploaded_file.name} already processed, skipping re-creation", "GUI")
        
        # Show cleaning operations if file is loaded
        if st.session_state.janitor is not None:
            st.header("🧹 Cleaning Operations")
            
            # Control buttons
            col1, col2 = st.columns(2)
            
            with col1:
                # Step back button
                can_step_back = st.session_state.janitor.can_step_back()
                confirm_step_back = st.session_state.get('confirm_step_back', False)
                
                # Reset confirmation if user interacted with something else
                if st.session_state.last_interaction not in [None, 'step_back'] and confirm_step_back:
                    st.session_state.confirm_step_back = False
                    confirm_step_back = False
                
                button_text = "⚠️ Press again to confirm" if confirm_step_back else "↶ Step Back"
                button_help = "Press again to confirm step back" if confirm_step_back else "Undo last operation"
                
                if st.button(button_text, help=button_help, use_container_width=True, disabled=not can_step_back):
                    debug_log("Step back button clicked", "GUI")
                    st.session_state.last_interaction = 'step_back'
                    
                    if confirm_step_back:
                        # Execute step back
                        debug_log(f"Before step back - History length: {len(st.session_state.cleaning_history)}", "GUI")
                        try:
                            st.session_state.janitor.step_back()
                            # Sync session state with pipeline
                            st.session_state.cleaning_history = st.session_state.janitor.get_history().copy()
                            debug_log(f"Step back completed - New history length: {len(st.session_state.cleaning_history)}", "GUI")
                            st.success("↶ Stepped back to previous state")
                            st.session_state.confirm_step_back = False
                            st.session_state.last_interaction = None
                            st.rerun()
                        except ValueError as e:
                            debug_log(f"Step back failed: {e}", "GUI")
                            st.error(f"Cannot step back: {e}")
                            st.session_state.confirm_step_back = False
                            st.session_state.last_interaction = None
                    else:
                        # Set confirmation flag
                        st.session_state.confirm_step_back = True
                        st.rerun()
            
            with col2:
                # Reset button
                confirm_reset = st.session_state.get('confirm_reset', False)
                
                # Reset confirmation if user interacted with something else
                if st.session_state.last_interaction not in [None, 'reset'] and confirm_reset:
                    st.session_state.confirm_reset = False
                    confirm_reset = False
                
                button_text = "⚠️ Press again to confirm" if confirm_reset else "🔄 Reset to Original"
                button_help = "Press again to confirm reset" if confirm_reset else "Reset DataFrame to original state"
                
                if st.button(button_text, help=button_help, use_container_width=True):
                    debug_log("Reset button clicked", "GUI")
                    st.session_state.last_interaction = 'reset'
                    
                    if confirm_reset:
                        # Execute reset
                        debug_log(f"Before reset - History length: {len(st.session_state.cleaning_history)}", "GUI")
                        st.session_state.janitor.reset()
                        st.session_state.cleaning_history = []
                        debug_log("Reset completed - DataFrame and history cleared", "GUI")
                        st.success("🔄 Reset to original state")
                        st.session_state.confirm_reset = False
                        st.session_state.last_interaction = None
                        st.rerun()
                    else:
                        # Set confirmation flag
                        st.session_state.confirm_reset = True
                        st.rerun()
            
            st.markdown("---")

            # Cleaning operations grouped in dropdowns
            with st.expander("Missing Data"):
                # Threshold slider for empty columns (always visible)
                threshold = st.slider(
                    "Empty Cols Threshold",
                    0.0,
                    1.0,
                    0.9,
                    0.1,
                    key="empty_cols_threshold",
                    help="Columns with missing values above this ratio will be removed",
                )

                if st.button(
                    "Remove Empty Cols",
                    help="Remove columns with high missing values",
                    use_container_width=True,
                ):
                    debug_log(f"Remove Empty Cols clicked - Threshold: {threshold}", "GUI")
                    st.session_state.last_interaction = 'remove_empty_cols'
                    debug_log(
                        f"Before operation - Shape: {st.session_state.janitor.get_df().shape}",
                        "GUI",
                    )
                    st.session_state.janitor.remove_empty_cols(threshold=threshold)
                    debug_log(
                        f"After operation - Shape: {st.session_state.janitor.get_df().shape}",
                        "GUI",
                    )
                    # Sync with pipeline history instead of maintaining separate history
                    st.session_state.cleaning_history = st.session_state.janitor.get_history().copy()
                    st.session_state.cleaning_history.append(
                        f"GUI: Removed empty columns (threshold: {threshold})"
                    )
                    debug_log(
                        f"Synced history - Total operations: {len(st.session_state.cleaning_history)}",
                        "GUI",
                    )
                    st.rerun()

                if st.button(
                    "Remove Empty Rows",
                    help="Remove completely empty rows",
                    use_container_width=True,
                ):
                    debug_log("Remove Empty Rows clicked", "GUI")
                    st.session_state.last_interaction = 'remove_empty_rows'
                    debug_log(
                        f"Before operation - Shape: {st.session_state.janitor.get_df().shape}",
                        "GUI",
                    )
                    st.session_state.janitor.remove_empty_rows()
                    debug_log(
                        f"After operation - Shape: {st.session_state.janitor.get_df().shape}",
                        "GUI",
                    )
                    st.session_state.cleaning_history = st.session_state.janitor.get_history().copy()
                    st.session_state.cleaning_history.append("GUI: Removed empty rows")
                    debug_log(
                        f"Synced history - Total operations: {len(st.session_state.cleaning_history)}",
                        "GUI",
                    )
                    st.rerun()

            with st.expander("Column Names"):
                if st.button(
                    "Standardize Names",
                    help="Convert column names to lowercase with underscores",
                    use_container_width=True,
                ):
                    debug_log("Standardize Names clicked", "GUI")
                    st.session_state.last_interaction = 'standardize_names'
                    debug_log(
                        f"Before operation - Columns: {list(st.session_state.janitor.get_df().columns)}",
                        "GUI",
                    )
                    st.session_state.janitor.standardize_column_names()
                    debug_log(
                        f"After operation - Columns: {list(st.session_state.janitor.get_df().columns)}",
                        "GUI",
                    )
                    st.session_state.cleaning_history = st.session_state.janitor.get_history().copy()
                    st.session_state.cleaning_history.append("GUI: Standardized column names")
                    debug_log(
                        f"Synced history - Total operations: {len(st.session_state.cleaning_history)}",
                        "GUI",
                    )
                    st.rerun()

                if st.button(
                    "Normalize Names",
                    help="Remove accents from column names",
                    use_container_width=True,
                ):
                    debug_log("Normalize Names clicked", "GUI")
                    st.session_state.last_interaction = 'normalize_names'
                    debug_log(
                        f"Before operation - Columns: {list(st.session_state.janitor.get_df().columns)}",
                        "GUI",
                    )
                    st.session_state.janitor.normalize_column_names()
                    debug_log(
                        f"After operation - Columns: {list(st.session_state.janitor.get_df().columns)}",
                        "GUI",
                    )
                    st.session_state.cleaning_history = st.session_state.janitor.get_history().copy()
                    st.session_state.cleaning_history.append("GUI: Normalized column names")
                    debug_log(
                        f"Synced history - Total operations: {len(st.session_state.cleaning_history)}",
                        "GUI",
                    )
                    st.rerun()

            with st.expander("Values"):
                if st.button(
                    "Normalize Values",
                    help="Remove accents from all text values",
                    use_container_width=True,
                ):
                    debug_log("Normalize Values clicked", "GUI")
                    st.session_state.last_interaction = 'normalize_values'
                    debug_log(
                        f"Before operation - Sample values: {st.session_state.janitor.get_df().iloc[0].to_dict() if len(st.session_state.janitor.get_df()) > 0 else 'No data'}",
                        "GUI",
                    )
                    st.session_state.janitor.normalize_values()
                    debug_log(
                        f"After operation - Sample values: {st.session_state.janitor.get_df().iloc[0].to_dict() if len(st.session_state.janitor.get_df()) > 0 else 'No data'}",
                        "GUI",
                    )
                    st.session_state.cleaning_history = st.session_state.janitor.get_history().copy()
                    st.session_state.cleaning_history.append("GUI: Normalized values")
                    debug_log(
                        f"Synced history - Total operations: {len(st.session_state.cleaning_history)}",
                        "GUI",
                    )
                    st.rerun()

                if st.button(
                    "Standardize Values",
                    help="Lowercase + underscore replacement for values",
                    use_container_width=True,
                ):
                    debug_log("Standardize Values clicked", "GUI")
                    st.session_state.last_interaction = 'standardize_values'
                    debug_log(
                        f"Before operation - Sample values: {st.session_state.janitor.get_df().iloc[0].to_dict() if len(st.session_state.janitor.get_df()) > 0 else 'No data'}",
                        "GUI",
                    )
                    st.session_state.janitor.standardize_values()
                    debug_log(
                        f"After operation - Sample values: {st.session_state.janitor.get_df().iloc[0].to_dict() if len(st.session_state.janitor.get_df()) > 0 else 'No data'}",
                        "GUI",
                    )
                    st.session_state.cleaning_history = st.session_state.janitor.get_history().copy()
                    st.session_state.cleaning_history.append("GUI: Standardized values")
                    debug_log(
                        f"Synced history - Total operations: {len(st.session_state.cleaning_history)}",
                        "GUI",
                    )
                    st.rerun()
    
    # Main content area
    if st.session_state.janitor is not None:
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Current Data", "📝 History", "🔍 Data Info", "💾 Export Code"])
        
        # Track tab interactions
        if st.session_state.get('current_tab') != tab1:
            st.session_state.last_interaction = 'tab_change'
        
        with tab1:
            st.subheader("Current DataFrame")
            current_df = st.session_state.janitor.get_df()
            
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
                
                # Show technical history from Janitor
                with st.expander("Technical Details"):
                    history = st.session_state.janitor.get_history()
                    for entry in history:
                        st.code(entry, language="text")
            else:
                st.info("No cleaning operations performed yet.")
        
        with tab3:
            st.subheader("Data Information")
            current_df = st.session_state.janitor.get_df()
            
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
                    history = st.session_state.janitor.get_history()
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
                        file_name=f"janitor_cleaning_pipeline{file_extension}",
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
        ## Welcome to Janitor Bot! 🧹
        
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
