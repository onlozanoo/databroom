"""
Data display tabs component for Databroom GUI.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import streamlit.components.v1 as components

try:
    from ydata_profiling import ProfileReport
except ImportError:
    ProfileReport = None

from databroom.core.debug_logger import debug_log
from databroom.generators.base import CodeGenerator

def _format_operation_summary(operation) -> str:
    """Format a history operation entry into a human-readable summary.
    
    Args:
        operation: Dictionary containing operation metadata or string (legacy format)
        
    Returns:
        Formatted string summary of the operation
    """
    # Handle legacy string format
    if isinstance(operation, str):
        return f"✓ {operation}"
    
    # Handle dictionary format
    if not isinstance(operation, dict):
        return f"✓ {str(operation)}"
    
    func_name = operation.get('function', 'Unknown')
    timestamp = operation.get('timestamp', '')
    time_only = timestamp.split(' ')[-1] if timestamp else ''
    
    # Format function name to be more readable
    readable_name = func_name.replace('_', ' ').title()
    
    # Build parameter string
    params = []
    if operation.get('args'):
        for arg in operation['args']:
            params.append(str(arg))
    
    if operation.get('kwargs'):
        for key, value in operation['kwargs'].items():
            if isinstance(value, bool):
                if value:
                    params.append(key)
            elif isinstance(value, (int, float)):
                params.append(f"{key}: {value}")
            elif isinstance(value, str):
                params.append(f"'{value}'")
            elif isinstance(value, list):
                if len(value) <= 3:
                    params.append(f"{key}: {value}")
                else:
                    params.append(f"{key}: [{len(value)} items]")
    
    param_str = f" ({', '.join(params)})" if params else ""
    
    # Format shape change
    shape_change = operation.get('shape_change', {})
    before = shape_change.get('before')
    after = shape_change.get('after')
    
    if before and after:
        shape_str = f" - {before[0]}×{before[1]} → {after[0]}×{after[1]}"
    else:
        shape_str = ""
    
    # Build final summary
    summary = f"✓ {readable_name}{param_str}{shape_str}"
    if time_only:
        summary += f" - {time_only}"
    
    return summary

def render_data_tabs():
    """Render all data display tabs."""
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Current Data", "📝 History & Pipeline", "🔍 Data Info", "💾 Export Code"])
    
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

    # Pipeline upload and run section
    st.markdown("---")
    st.subheader("Run Saved Pipeline")

    # File uploader for pipeline JSON
    pipeline_file = st.file_uploader(
        "Upload Pipeline JSON File",
        type=['json'],
        help="Upload a saved pipeline JSON file to run on current data",
        key="pipeline_uploader"
    )

    if pipeline_file is not None:
        # Store pipeline content in session state
        if 'uploaded_pipeline' not in st.session_state or st.session_state.uploaded_pipeline_name != pipeline_file.name:
            try:
                import json
                pipeline_data = json.load(pipeline_file)
                st.session_state.uploaded_pipeline = pipeline_data
                st.session_state.uploaded_pipeline_name = pipeline_file.name
                st.success(f"✅ Pipeline loaded: {pipeline_file.name}")
                st.info(f"Contains {len(pipeline_data)} operations")
            except Exception as e:
                st.error(f"Error loading pipeline: {e}")
                st.session_state.uploaded_pipeline = None
                st.session_state.uploaded_pipeline_name = None

    # Run Pipeline button
    if st.session_state.get('uploaded_pipeline') and st.session_state.broom:
        if st.button(
            "🚀 Run Pipeline",
            help="Execute the loaded pipeline on current data",
            use_container_width=True,
            type="primary",
            key="run_pipeline_btn"
        ):
            try:
                # Execute pipeline
                loaded_history = st.session_state.uploaded_pipeline
                st.session_state.broom.pipeline.run_pipeline(None, loaded_history)

                # Sync session state
                from databroom.gui.utils.session import sync_history
                sync_history()

                st.success("✅ Pipeline executed successfully!")
                st.info(f"Applied {len(loaded_history)} operations")
                st.rerun()

            except Exception as e:
                st.error(f"Error executing pipeline: {e}")
    elif st.session_state.get('uploaded_pipeline') and not st.session_state.broom:
        st.warning("Load data first before running a pipeline")
    elif not st.session_state.get('uploaded_pipeline'):
        st.info("Upload a pipeline JSON file to run it")

    st.markdown("---")

    # Save Pipeline section
    st.markdown("---")
    st.subheader("💾 Save Current Pipeline")

    # Save pipeline button
    if st.session_state.broom and len(st.session_state.cleaning_history) > 0:
        col1, col2 = st.columns([3, 1])

        with col1:
            pipeline_filename = st.text_input(
                "Pipeline filename:",
                value="cleaning_pipeline.json",
                help="Name for the pipeline JSON file",
                key="pipeline_filename"
            )

        with col2:
            if st.button(
                "💾 Save Pipeline",
                help="Save the current cleaning operations as a reusable pipeline",
                use_container_width=True,
                type="secondary",
                key="save_pipeline_btn"
            ):
                try:
                    # Save the pipeline
                    success = st.session_state.broom.save_pipeline(pipeline_filename)

                    if success:
                        st.success(f"✅ Pipeline saved as: {pipeline_filename}")
                        st.info(f"Contains {len(st.session_state.cleaning_history)} operations")

                        # Provide download link
                        try:
                            with open(pipeline_filename, 'r') as f:
                                pipeline_content = f.read()
                            st.download_button(
                                label="📥 Download Pipeline File",
                                data=pipeline_content,
                                file_name=pipeline_filename,
                                mime="application/json",
                                help="Download the pipeline JSON file"
                            )
                        except Exception as e:
                            st.warning(f"Pipeline saved but download preparation failed: {e}")
                    else:
                        st.error(f"❌ Failed to save pipeline to: {pipeline_filename}")

                except Exception as e:
                    st.error(f"Error saving pipeline: {e}")
    elif not st.session_state.broom:
        st.info("Load data first before saving a pipeline")
    else:
        st.info("Perform some cleaning operations first to save a pipeline")

    st.markdown("---")
    st.markdown("---")

    # Current cleaning history
    st.subheader("Current Session History")
    if st.session_state.cleaning_history:
        # Display simplified summaries
        for operation in st.session_state.cleaning_history:
            summary = _format_operation_summary(operation)
            st.markdown(f"- {summary}")

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
    
    if ProfileReport is None:
        st.warning("⚠️ `ydata-profiling` is not installed. Please install it to use automatic EDA features.")
        st.code("pip install ydata-profiling", language="bash")
        return

    # Check if report already exists in session
    if st.session_state.profiling_report:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success("✅ EDA Report Generated")
        with col2:
            if st.button("🔄 Regenerate Report"):
                 st.session_state.profiling_report = None
                 st.rerun()
             
        components.html(st.session_state.profiling_report, height=1000, scrolling=True)
        
    else:

        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("Generate Data Info", type="primary"):
                with st.spinner("Generating... This may take a minute for large datasets."):
                    try:
                        pr = ProfileReport(current_df, explorative=True,
                        )#minimal=True)
                        
                        pr.config.html.navbar_show=False
                        #pr.config.html.style.theme="flatly"
                        
                        st.session_state.profiling_report = pr.to_html()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating report: {e}")
                        debug_log(f"Profiling error: {e}", "GUI")

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
