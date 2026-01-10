"""
Authentication module for ContactIQ.

Implements simple password-based authentication at session start.
"""
import streamlit as st
from config import Config


def check_authentication():
    """
    Check if user is authenticated, show password prompt if not.
    
    Returns:
        bool: True if authenticated, False otherwise (and shows prompt)
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        # Show authentication UI
        st.title("🔐 ContactIQ - Authentication Required")
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Please enter the password to continue")
            password = st.text_input(
                "Password:",
                type="password",
                key="password_input",
                label_visibility="visible"
            )
            
            if st.button("Login", type="primary", use_container_width=True):
                if password == Config.SESSION_PASSWORD:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect password. Please try again.")
        
        st.stop()
    
    return True


def logout():
    """Clear authentication state and rerun app."""
    if "authenticated" in st.session_state:
        del st.session_state.authenticated
    st.rerun()
