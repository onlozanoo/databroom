"""
Data display tabs component for Databroom GUI.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from databroom.core.debug_logger import debug_log
from databroom.generators.base import CodeGenerator

def render_data_tabs():
    """Render all data display tabs."""
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Current Data", "📝 History", "🔍 Data Info", "💾 Export Code"])
    
    # Track tab interactions
    if st.session_state.get('current_tab') != tab1:
        st.session_state.last_interaction = 'tab_change'
    
    with tab1:
        _render_current_data_tab()
    
    with tab2:
        _render_history_tab()
    
    with tab3:
        _render_data_info_tab()
    
    with tab4:
        _render_export_code_tab()

def _render_current_data_tab():
    """Render the current DataFrame display tab."""
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

def _render_history_tab():
    """Render the cleaning history tab."""
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

def _render_data_info_tab():
    """Render the data information tab."""
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

def _render_export_code_tab():
    """Render the code export tab."""
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
            code_info = _get_code_generation_info(selected_language)
            
            # Generate code
            history = st.session_state.broom.get_history()
            generator = CodeGenerator(code_info['language'])
            generator.load_history(history)
            code = generator.generate_code()
            
            # Generate complete code with template
            full_script = _generate_full_script(code_info, code)
            
            # Show preview
            st.code(full_script, language=code_info['code_language'])
            
            # Download button
            st.download_button(
                label=code_info['download_label'],
                data=full_script,
                file_name=f"broom_cleaning_pipeline{code_info['file_extension']}",
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

def _get_code_generation_info(selected_language):
    """Get code generation configuration based on selected language."""
    if selected_language == "Python/Pandas":
        debug_log("Generating Python code preview", "GUI")
        return {
            'language': 'python',
            'template_name': "python_pipeline.py.j2",
            'file_extension': ".py",
            'code_language': 'python',
            'download_label': "📥 Download Python Script"
        }
    else:  # R/Tidyverse
        debug_log("Generating R code preview", "GUI")
        return {
            'language': 'R',
            'template_name': "R_pipeline.R.j2",
            'file_extension': ".R",
            'code_language': 'r',
            'download_label': "📥 Download R Script"
        }

def _generate_full_script(code_info, code):
    """Generate complete script using Jinja2 template."""
    templates_dir = Path(__file__).parent.parent.parent / "generators" / "templates"
    env = Environment(loader=FileSystemLoader(str(templates_dir)))
    template = env.get_template(code_info['template_name'])
    
    # Use actual filename if available
    filename = st.session_state.uploaded_file_name or "your_data_file.csv"
    
    # For R, suggest CSV format for Excel files
    if code_info['language'] == 'R' and filename.endswith(('.xlsx', '.xls')):
        filename_for_r = filename.replace('.xlsx', '.csv').replace('.xls', '.csv')
        st.info("💡 Note: R script uses CSV format. Convert Excel file to CSV for best compatibility.")
        filename = filename_for_r
    
    context = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "steps": code,
        "filename": filename
    }
    
    return template.render(context)