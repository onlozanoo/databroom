"""
CSS styles and theming for Databroom GUI.
"""

import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to the Streamlit app."""
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

def setup_page_config():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="🧹 Databroom",
        page_icon="🧹",
        layout="wide",
        initial_sidebar_state="expanded"
    )