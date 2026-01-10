"""
Main Application Entry Point for ContactIQ.

Integrates all components: authentication, chat interface, dashboard,
with full error handling and ANZ branding.
"""
import streamlit as st
import sys
import traceback
from config import Config
from ui.auth import check_authentication, logout
from ui.chat_interface import render_chat_interface
from ui.dashboard import render_dashboard
from utils.logger import setup_logging, get_logger

# Setup structured logging
setup_logging()
logger = get_logger(__name__)

# ANZ Brand Colors
ANZ_PRIMARY_BLUE = "#003D82"
ANZ_SECONDARY_BLUE = "#0052A5"

# Streamlit page configuration
st.set_page_config(
    page_title="ContactIQ - ANZ Conversational AI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)


def apply_anz_styling():
    """Apply ANZ brand styling to the application."""
    st.markdown(f"""
    <style>
        .main {{
            background-color: #F5F5F5;
        }}
        .sidebar .sidebar-content {{
            background: linear-gradient(180deg, {ANZ_PRIMARY_BLUE} 0%, {ANZ_SECONDARY_BLUE} 100%);
        }}
        .stRadio label {{
            color: white;
        }}
        /* Make "Navigate" label text black */
        [data-testid="stSidebar"] .stRadio label {{
            color: #000000 !important;
        }}
        [data-testid="stSidebar"] .stRadio label p {{
            color: #000000 !important;
        }}
        [data-testid="stSidebar"] .stRadio > div > label {{
            color: #000000 !important;
        }}
        [data-testid="stSidebar"] .stRadio > label {{
            color: #000000 !important;
        }}
        h1, h2, h3 {{
            color: {ANZ_PRIMARY_BLUE};
        }}
        .stSuccess {{
            background-color: #d4edda;
            border-color: #c3e6cb;
        }}
        .stError {{
            background-color: #f8d7da;
            border-color: #f5c6cb;
        }}
    </style>
    """, unsafe_allow_html=True)


def handle_global_error(e: Exception, context: str = ""):
    """
    Handle global errors with logging and user messaging.
    
    Args:
        e: Exception object
        context: Context where error occurred
    """
    error_msg = str(e)
    error_trace = traceback.format_exc()
    
    logger.error(
        "global_error",
        error=error_msg,
        context=context,
        traceback=error_trace
    )
    
    # User-friendly error message
    st.error(f"❌ An error occurred: {error_msg}")
    st.write("Please try again or contact support if the issue persists.")
    
    # Optionally show details in expander for debugging
    with st.expander("🔍 Error Details (for debugging)"):
        st.code(error_trace)


def main():
    """
    Main application entry point.
    
    Handles:
    - Authentication check
    - Configuration validation
    - Page routing
    - Error handling
    """
    # Apply ANZ styling
    apply_anz_styling()
    
    # Check authentication (required for all pages)
    check_authentication()
    
    # Check configuration
    if not Config.validate():
        st.error("❌ Configuration Error")
        st.write(f"Missing required configuration: {', '.join(Config.get_missing_config())}")
        st.write("Please check your `.env` file and ensure all required variables are set.")
        logger.error("configuration_missing", missing=Config.get_missing_config())
        st.stop()
    
    logger.info("app_started")
    
    # Sidebar navigation with ANZ branding
    with st.sidebar:
        # ANZ branded header
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, {ANZ_PRIMARY_BLUE} 0%, {ANZ_SECONDARY_BLUE} 100%); 
                    padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;'>
            <h1 style='color: white; margin: 0; font-size: 1.8rem; text-align: center;'>💬 ContactIQ</h1>
            <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.9rem; text-align: center;'>
                ANZ Conversational AI
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")

        # Navigation
        st.markdown("### Navigate")
        page = st.radio(
            "",
            ["💬 Chat", "📊 Dashboard"],
            key="page_selector",
            label_visibility="collapsed"
        )

        st.markdown("---")

        # Assistant Mode (only show on Chat page)
        if page == "💬 Chat":
            st.markdown("### 🤖 Assistant Mode")
            if "assistant_mode" not in st.session_state:
                st.session_state.assistant_mode = "customer"
            mode = st.radio(
                "",
                ["Customer", "Banker"],
                index=0 if st.session_state.assistant_mode == "customer" else 1,
                key="main_mode_selector",
                label_visibility="collapsed",
                help="Choose Customer mode for general inquiries or Banker mode for financial advice"
            )
            st.session_state.assistant_mode = mode.lower()
            st.markdown("---")

        # System status
        st.markdown("### System Status")
        if Config.validate():
            st.success("✅ System Ready")
        else:
            st.error("❌ Configuration Error")
        
        # Configuration info (collapsible)
        with st.expander("⚙️ Configuration"):
            st.write(f"**Model:** {Config.OPENAI_MODEL}")
            st.write(f"**Confidence Threshold:** {Config.CONFIDENCE_THRESHOLD}")
            st.write(f"**API Timeout:** {Config.API_TIMEOUT}s")
            st.write(f"**Log Level:** {Config.LOG_LEVEL}")
            if Config.OPENAI_VECTOR_STORE_ID_CUSTOMER:
                st.write(f"**Customer Vector Store:** Configured")
            if Config.OPENAI_VECTOR_STORE_ID_BANKER:
                st.write(f"**Banker Vector Store:** Configured")
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            logout()
            logger.info("user_logged_out")
    
    # Route to selected page with error handling
    try:
        if page == "💬 Chat":
            render_chat_interface()
        elif page == "📊 Dashboard":
            render_dashboard()
    except Exception as e:
        logger.error("page_render_error", page=page, error=str(e), exc_info=True)
        handle_global_error(e, context=f"Rendering {page} page")
        st.stop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("fatal_error", error=str(e), exc_info=True)
        st.error(f"❌ A fatal error occurred: {str(e)}")
        st.write("Please refresh the page or contact support if the issue persists.")
        
        # Show error details in expander
        with st.expander("🔍 Error Details (for debugging)"):
            st.code(traceback.format_exc())
        
        st.stop()
