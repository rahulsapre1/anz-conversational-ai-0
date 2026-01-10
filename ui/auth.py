"""
Authentication module for ContactIQ.

Implements simple password-based authentication at session start.
"""
import streamlit as st
from config import Config

# ANZ Brand Colors
ANZ_PRIMARY_BLUE = "#003D82"
ANZ_SECONDARY_BLUE = "#0052A5"
ANZ_ACCENT_BLUE = "#00A0E3"


def _render_one_pager_case_study():
    """Render the ContactIQ one-page case study on the login screen."""
    st.markdown("## ContactIQ: One-Page Case Study")
    st.caption("by Rahul Sapre (`rahulsapre1@gmail.com`)")
    
    # Table of Contents with anchor links
    st.markdown("### 📑 Table of Contents")
    toc_links = [
        ("1. Context / Problem", "context-problem"),
        ("2. Goal (SMART)", "goal"),
        ("3. Jobs To Be Done (JTBD)", "jtbd"),
        ("4. Core Assumptions", "assumptions"),
        ("5. Solution Overview", "solution"),
        ("6. Feature Prioritisation & MVP Scope", "features"),
        ("7. How It Works (User Flow)", "user-flow"),
        ("8. Metrics & Evals", "metrics"),
        ("9. Launch & Adoption Plan", "launch"),
        ("10. Risks & Controls", "risks")
    ]
    toc_html = " | ".join([f'<a href="#{anchor}" style="color: {ANZ_ACCENT_BLUE}; text-decoration: none; font-weight: bold;">{title}</a>' 
                           for title, anchor in toc_links])
    st.markdown(toc_html, unsafe_allow_html=True)
    st.markdown("---")
    
    # Section 1
    st.markdown('<div id="context-problem"></div>', unsafe_allow_html=True)
    st.markdown("### 1. Context / Problem")
    st.markdown(
        "- **What problem exists today**: High-volume banking queries (fees, processes, security) are handled repeatedly by humans; "
        "policy knowledge is fragmented; “AI answers” risk hallucination and non-compliant wording.\n"
        "- **Who experiences it (user + business)**:\n"
        "  - **Customers** need fast, clear, non-advisory answers.\n"
        "  - **Frontline staff** need policy-backed guidance and compliant phrasing.\n"
        "  - **Business** needs safe self-serve resolution + auditability in a regulated setting.\n"
        "- **Why it matters now**: Cost pressure + rising expectations for self-service, while regulatory risk makes “generic chatbots” unacceptable."
    )
    st.markdown("---")
    
    # Section 2
    st.markdown('<div id="goal"></div>', unsafe_allow_html=True)
    st.markdown("### 2. Goal (SMART)")
    st.markdown(
        "- **Primary goal**: In 2 days, ship an MVP conversational assistant that answers a bounded set of ANZ public-policy queries with citations, "
        "confidence scoring, and escalation-by-default when uncertain.\n"
        "- **Success looks like**: Measurable **self-serve resolution** (resolved interactions) with high citation coverage, predictable escalations, "
        "and clear intent distribution to guide roadmap.\n"
        "- **Failure looks like**: Uncited/hallucinated outputs, low-confidence answers not escalating, or inability to measure outcomes from real interactions."
    )
    st.markdown("---")
    
    # Section 3
    st.markdown('<div id="jtbd"></div>', unsafe_allow_html=True)
    st.markdown("### 3. Jobs To Be Done (JTBD)")
    st.markdown(
        "- **Primary (Customer)**: When a retail customer needs to understand account/product information, so they can take the right next step without "
        "receiving personal financial advice.\n"
        "- **Secondary (Banker/Agent)**: When a frontline banker/agent needs to confirm policy/process steps and compliant phrasing, so they can resolve the "
        "customer issue quickly and safely."
    )
    st.markdown("---")
    
    # Section 4
    st.markdown('<div id="assumptions"></div>', unsafe_allow_html=True)
    st.markdown("### 4. Core Assumptions")
    st.markdown(
        "- **Key assumptions**:\n"
        "  - Public ANZ content is sufficient for common queries when retrieved and cited.\n"
        "  - Confidence scoring + escalation logic reduces risk more than “prompting harder.”\n"
        "- **Constraints / guardrails**:\n"
        "  - No personalised financial advice; default to escalation on ambiguity/low confidence.\n"
        "  - Evidence must come from retrieved sources (RAG), not model memory."
    )
    st.markdown("---")
    
    # Section 5
    st.markdown('<div id="solution"></div>', unsafe_allow_html=True)
    st.markdown("### 5. Solution Overview")
    st.markdown(
        "- **What it is**: A dual-mode (Customer/Banker) conversational AI that answers with citations + confidence, logs every interaction, and escalates across "
        "multiple risk triggers.\n"
        "- **Who it serves**: Customers seeking general info; staff needing policy-backed guidance.\n"
        "- **High-level approach**: Intent → route → retrieve evidence → generate answer with citations → score confidence → escalate or resolve → log and visualize KPIs."
    )
    st.markdown("---")
    
    # Section 6
    st.markdown('<div id="features"></div>', unsafe_allow_html=True)
    st.markdown("### 6. Feature Prioritisation & MVP Scope")
    st.markdown(
        "**P0 — Must Have**\n"
        "- Dual assistant modes (Customer vs Banker) with different thresholds/tone\n"
        "- Intent classification + routing into automatable/sensitive/human_only\n"
        "- RAG with citations (only retrieved content informs responses)\n"
        "- Confidence scoring + escalation (multiple trigger types)\n"
        "- Interaction + escalation logging and a KPI dashboard\n\n"
        "**Explicitly Out of Scope**\n"
        "- Production-grade auth (OAuth/SSO/JWT), CRM/case creation, personalised recommendations, voice/IVR, multilingual, proactive outreach"
    )
    st.markdown("---")
    
    # Section 7
    st.markdown('<div id="user-flow"></div>', unsafe_allow_html=True)
    st.markdown("### 7. How It Works (User Flow)")
    st.markdown(
        "1. User logs in (MVP password auth) and selects Customer or Banker mode\n"
        "2. User submits a query\n"
        "3. System classifies intent + category\n"
        "4. If human_only → immediate escalation; else proceed\n"
        "5. Retrieve evidence from the appropriate knowledge store\n"
        "6. Generate response with citations + disclaimers as needed\n"
        "7. Compute confidence; resolve vs escalate; log outcome and metrics"
    )
    st.markdown("---")
    
    # Section 8
    st.markdown('<div id="metrics"></div>', unsafe_allow_html=True)
    st.markdown("### 8. Metrics & Evals (all present in dashboard)")
    st.markdown(
        "**Core outcome metrics**\n"
        "- Total conversations (unique session_id)\n"
        "- Self-serve resolution rate (% resolved) and escalation rate (% escalated)\n"
        "- Usage split (Customer vs Banker)\n\n"
        "**Diagnostic / learning metrics**\n"
        "- Intent frequency distribution + intent category breakdown\n"
        "- Escalation reason frequency (by trigger_type) + escalation by intent/mode\n"
        "- Average confidence + average confidence by intent + confidence distribution\n"
        "- Intents with lowest resolution rates\n"
        "- Performance: avg server processing time, response generation time by intent\n"
        "- Time-based trends: interactions, escalations, and resolution rates over time\n"
        "- Retrieval/citation health: citation coverage, failed retrieval rate, top cited sources\n\n"
        "**How metrics inform decisions**\n"
        "- Scale intents with high volume + high self-serve resolution, redesign high-value/high-risk intents, and prioritize doc gaps where failed retrievals cluster."
    )
    st.markdown("---")
    
    # Section 9
    st.markdown('<div id="launch"></div>', unsafe_allow_html=True)
    st.markdown("### 9. Launch & Adoption Plan")
    st.markdown(
        "- **Who sees it first**: Internal demo users (bankers/agents) + controlled customer-like testing.\n"
        "- **How risk is managed**: Conservative thresholds, mandatory citations, and escalation triggers for high-risk language.\n"
        "- **How learning happens**: Review dashboard weekly to decide which intents to expand, which docs to ingest, and where escalation logic needs tuning."
    )
    st.markdown("---")
    
    # Section 10
    st.markdown('<div id="risks"></div>', unsafe_allow_html=True)
    st.markdown("### 10. Risks & Controls")
    st.markdown(
        "- **Hallucinations** → RAG-only evidence + citations + “insufficient evidence” escalation\n"
        "- **Non-compliant/advisory outputs** → intent gating + advice/fraud/account-specific escalation triggers\n"
        "- **Overconfidence** → conservative confidence threshold + outcome logging\n"
        "- **Low trust** → visible citations + transparent escalation reasons"
    )


def check_authentication():
    """
    Check if user is authenticated, show password prompt if not.
    
    Returns:
        bool: True if authenticated, False otherwise (and shows prompt)
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        # Header with title on left, login on right
        col_title, col_login = st.columns([2, 1])
        
        with col_title:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, {ANZ_PRIMARY_BLUE} 0%, {ANZ_SECONDARY_BLUE} 100%); 
                        padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;'>
                <h1 style='color: white; margin: 0; font-size: 2rem;'>💬 ContactIQ</h1>
                <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
                    ANZ Conversational AI
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_login:
            st.markdown("### 🔐 Login")
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
        
        st.markdown("---")
        
        # One-pager case study (shown on the login screen)
        _render_one_pager_case_study()
        
        st.stop()
    
    return True


def logout():
    """Clear authentication state and rerun app."""
    if "authenticated" in st.session_state:
        del st.session_state.authenticated
    st.rerun()
