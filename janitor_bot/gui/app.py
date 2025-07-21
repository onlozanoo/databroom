import streamlit as st
import pandas as pd
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from janitor_bot.core.janitor import Janitor
from janitor_bot.core.debug_logger import debug_log, get_current_log_file

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
            
            # Reset button
            if st.button("🔄 Reset to Original", help="Reset DataFrame to original state", use_container_width=True):
                debug_log("Reset button clicked", "GUI")
                debug_log(f"Before reset - History length: {len(st.session_state.cleaning_history)}", "GUI")
                st.session_state.janitor.reset()
                st.session_state.cleaning_history = []
                debug_log("Reset completed - DataFrame and history cleared", "GUI")
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
                    debug_log(
                        f"Before operation - Columns: {list(st.session_state.janitor.get_df().columns)}",
                        "GUI",
                    )
                    st.session_state.janitor.standarize_column_names()
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
                    debug_log(
                        f"Before operation - Sample values: {st.session_state.janitor.get_df().iloc[0].to_dict() if len(st.session_state.janitor.get_df()) > 0 else 'No data'}",
                        "GUI",
                    )
                    st.session_state.janitor.standarize_values()
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
        tab1, tab2, tab3 = st.tabs(["📊 Current Data", "📝 History", "🔍 Data Info"])
        
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
