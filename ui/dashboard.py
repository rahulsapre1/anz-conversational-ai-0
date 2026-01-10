"""
KPI Dashboard UI for ContactIQ.

Implements dashboard with metrics from PRD Section 5, displaying overall usage,
resolution metrics, intent frequency, escalation analysis, confidence metrics, and performance metrics.
Uses ANZ branding with professional blue color scheme.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from ui.auth import check_authentication
from database.supabase_client import get_db_client
from utils.logger import get_logger
from config import Config

logger = get_logger(__name__)

# ANZ Brand Colors
ANZ_PRIMARY_BLUE = "#003D82"
ANZ_SECONDARY_BLUE = "#0052A5"
ANZ_ACCENT_BLUE = "#00A0E3"
ANZ_SUCCESS_GREEN = "#28A745"
ANZ_WARNING_ORANGE = "#FFC107"
ANZ_ERROR_RED = "#DC3545"
ANZ_LIGHT_GRAY = "#F5F5F5"
ANZ_DARK_GRAY = "#333333"

# Dark theme colors for infographics
DARK_BG = "#1a1a1a"  # Dark background
DARK_BG_LIGHT = "#2d2d2d"  # Slightly lighter dark background
LIGHT_TEXT = "#ffffff"  # White text
LIGHT_TEXT_SECONDARY = "#e0e0e0"  # Light gray text
DARK_GRID = "#404040"  # Dark grid lines

# Plotly color palette matching ANZ branding
ANZ_COLORS = [ANZ_PRIMARY_BLUE, ANZ_SECONDARY_BLUE, ANZ_ACCENT_BLUE, ANZ_SUCCESS_GREEN, ANZ_WARNING_ORANGE]


def get_dark_theme_layout(title: str = "") -> dict:
    """
    Get dark theme layout configuration for Plotly charts.
    
    Args:
        title: Chart title
    
    Returns:
        Dictionary with dark theme layout settings
    """
    return {
        "plot_bgcolor": DARK_BG,
        "paper_bgcolor": DARK_BG,
        "font": dict(size=12, color=LIGHT_TEXT),
        "title": dict(
            text=title,
            font=dict(size=16, color=LIGHT_TEXT),
            x=0.5,
            xanchor="center"
        ),
        "xaxis": dict(
            gridcolor=DARK_GRID,
            gridwidth=1,
            zeroline=False,
            showgrid=True,
            color=LIGHT_TEXT_SECONDARY,
            title_font=dict(color=LIGHT_TEXT),
            tickfont=dict(color=LIGHT_TEXT_SECONDARY)
        ),
        "yaxis": dict(
            gridcolor=DARK_GRID,
            gridwidth=1,
            zeroline=False,
            showgrid=True,
            color=LIGHT_TEXT_SECONDARY,
            title_font=dict(color=LIGHT_TEXT),
            tickfont=dict(color=LIGHT_TEXT_SECONDARY)
        ),
        "legend": dict(
            font=dict(color=LIGHT_TEXT),
            bgcolor=DARK_BG_LIGHT,
            bordercolor=DARK_GRID
        )
    }


def render_dashboard():
    """Render the KPI dashboard with ANZ branding."""
    # Check authentication
    check_authentication()
    
    # Apply ANZ styling
    apply_anz_styling()
    
    # Page header
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {ANZ_PRIMARY_BLUE} 0%, {ANZ_SECONDARY_BLUE} 100%); 
                padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0; font-size: 2.5rem;'>📊 ContactIQ KPI Dashboard</h1>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
            Analytics & Performance Metrics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filters
    filters = render_filters()
    
    # Display all metric sections
    display_overall_metrics(filters)
    st.markdown("---")
    display_mode_breakdown(filters)
    st.markdown("---")
    display_resolution_metrics(filters)
    st.markdown("---")
    display_intent_frequency(filters)
    st.markdown("---")
    display_escalation_analysis(filters)
    st.markdown("---")
    display_confidence_metrics(filters)
    st.markdown("---")
    display_performance_metrics(filters)
    st.markdown("---")
    display_intent_risk_value_matrix(filters)
    st.markdown("---")
    display_citation_coverage(filters)
    
    # Auto-refresh
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Refresh Data", type="primary", width='stretch', help="Refresh all dashboard data and charts"):
            st.rerun()


def apply_anz_styling():
    """Apply ANZ brand styling to the dashboard."""
    st.markdown(f"""
    <style>
        .main {{
            background-color: {ANZ_LIGHT_GRAY};
        }}
        .stMetric {{
            background-color: {DARK_BG} !important;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid {ANZ_ACCENT_BLUE};
            color: {LIGHT_TEXT} !important;
        }}
        .stMetric > div {{
            background-color: {DARK_BG} !important;
        }}
        .stMetric label {{
            color: {LIGHT_TEXT_SECONDARY} !important;
            font-size: 0.9rem;
        }}
        .stMetric [data-testid="stMetricValue"] {{
            color: {LIGHT_TEXT} !important;
            font-size: 2rem;
            font-weight: bold;
        }}
        .stMetric [data-testid="stMetricDelta"] {{
            color: {LIGHT_TEXT_SECONDARY} !important;
        }}
        .stMetric [data-testid="stMetricLabel"] {{
            color: {LIGHT_TEXT_SECONDARY} !important;
        }}
        .stMetric p {{
            color: {LIGHT_TEXT} !important;
        }}
        .stMetric div {{
            color: {LIGHT_TEXT} !important;
        }}
        h2 {{
            color: {ANZ_PRIMARY_BLUE};
            border-bottom: 2px solid {ANZ_ACCENT_BLUE};
            padding-bottom: 0.5rem;
        }}
        h3 {{
            color: {ANZ_SECONDARY_BLUE};
        }}
    </style>
    """, unsafe_allow_html=True)


def render_filters() -> Dict[str, Any]:
    """Render dashboard filters."""
    st.markdown("### 🔍 Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        mode_filter = st.selectbox(
            "Mode:",
            ["All", "Customer", "Banker"],
            key="mode_filter"
        )
    
    with col2:
        date_range = st.selectbox(
            "Date Range:",
            ["Last 7 days", "Last 30 days", "Last 90 days", "All time"],
            key="date_range_filter"
        )
    
    with col3:
        intents = get_available_intents()
        intent_filter = st.selectbox(
            "Intent:",
            ["All"] + intents,
            key="intent_filter"
        )
    
    # Calculate date range
    end_date = datetime.now()
    if date_range == "Last 7 days":
        start_date = end_date - timedelta(days=7)
    elif date_range == "Last 30 days":
        start_date = end_date - timedelta(days=30)
    elif date_range == "Last 90 days":
        start_date = end_date - timedelta(days=90)
    else:
        start_date = None  # All time
    
    return {
        "mode": mode_filter.lower() if mode_filter != "All" else None,
        "start_date": start_date,
        "end_date": end_date,
        "intent": intent_filter if intent_filter != "All" else None
    }


def get_available_intents() -> List[str]:
    """Get list of available intents from database."""
    try:
        db_client = get_db_client()
        return db_client.get_distinct_intents()
    except Exception as e:
        logger.error("error_getting_intents", error=str(e))
        return []


def get_interactions_data(filters: Dict[str, Any]) -> pd.DataFrame:
    """Get interactions data from Supabase with filters."""
    try:
        db_client = get_db_client()
        interactions = db_client.get_interactions(filters)
        
        if not interactions:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(interactions)
        
        # Convert timestamp to datetime if it's a string
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"])
        
        return df
    
    except Exception as e:
        logger.error("error_fetching_interactions", error=str(e), exc_info=True)
        return pd.DataFrame()


def get_escalations_data(filters: Dict[str, Any]) -> pd.DataFrame:
    """Get escalations data from Supabase with filters."""
    try:
        db_client = get_db_client()
        escalations = db_client.get_escalations(filters)
        
        if not escalations:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(escalations)
        
        # Convert timestamp to datetime if it's a string
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"])
        
        return df
    
    except Exception as e:
        logger.error("error_fetching_escalations", error=str(e), exc_info=True)
        return pd.DataFrame()


def display_overall_metrics(filters: Dict[str, Any]):
    """Display overall usage metrics."""
    st.header("📈 Overall Usage Metrics")

    with st.spinner("Loading usage metrics..."):
        df = get_interactions_data(filters)
    
    if df.empty:
        st.info("📊 **No interaction data found**\n\nTry adjusting your filters or check back after more user interactions. Data will appear here once conversations begin.")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_interactions = len(df)
        st.metric(
            "Total Interactions",
            f"{total_interactions:,}",
            help="Total number of user interactions"
        )
    
    with col2:
        # Count unique sessions/conversations
        if "session_id" in df.columns:
            total_conversations = df["session_id"].nunique()
        else:
            # Fallback: estimate conversations from unique timestamps
            total_conversations = df["timestamp"].dt.date.nunique() if "timestamp" in df.columns else total_interactions
        
        st.metric(
            "Total Conversations",
            f"{total_conversations:,}",
            help="Total number of conversation sessions"
        )
    
    with col3:
        avg_interactions = total_interactions / total_conversations if total_conversations > 0 else 0
        st.metric(
            "Avg Interactions/Conversation",
            f"{avg_interactions:.2f}",
            help="Average number of interactions per conversation"
        )


def display_mode_breakdown(filters: Dict[str, Any]):
    """Display mode breakdown metrics."""
    st.header("👥 Mode Breakdown")
    
    df = get_interactions_data(filters)
    
    if df.empty:
        st.info("ℹ️ No data available.")
        return
    
    if "assistant_mode" not in df.columns:
        st.info("ℹ️ Mode data not available.")
        return
    
    mode_counts = df["assistant_mode"].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Metrics
        customer_count = mode_counts.get("customer", 0)
        banker_count = mode_counts.get("banker", 0)
        total = customer_count + banker_count
        
        st.metric("Customer Mode", f"{customer_count:,}")
        st.metric("Banker Mode", f"{banker_count:,}")
    
    with col2:
        # Pie chart with ANZ colors
        if total > 0:
            fig = px.pie(
                values=[customer_count, banker_count],
                names=["Customer", "Banker"],
                title="Mode Distribution",
                color_discrete_sequence=[ANZ_PRIMARY_BLUE, ANZ_SECONDARY_BLUE]
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont=dict(color=LIGHT_TEXT, size=12),
                marker=dict(line=dict(color=DARK_GRID, width=2))
            )
            fig.update_layout(get_dark_theme_layout("Mode Distribution"))
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("ℹ️ No mode data available.")


def display_resolution_metrics(filters: Dict[str, Any]):
    """Display resolution metrics (containment/escalation rates)."""
    st.header("✅ Resolution Metrics")
    
    df = get_interactions_data(filters)
    
    if df.empty:
        st.info("ℹ️ No data available.")
        return
    
    # Calculate metrics
    total = len(df)
    resolved = len(df[df["outcome"] == "resolved"]) if "outcome" in df.columns else 0
    escalated = len(df[df["outcome"] == "escalated"]) if "outcome" in df.columns else 0
    
    containment_rate = (resolved / total * 100) if total > 0 else 0
    escalation_rate = (escalated / total * 100) if total > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Interactions", f"{total:,}")
    
    with col2:
        st.metric(
            "Resolved",
            f"{resolved:,}",
            delta=f"{containment_rate:.1f}%",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            "Escalated",
            f"{escalated:,}",
            delta=f"{escalation_rate:.1f}%",
            delta_color="inverse"
        )
    
    with col4:
        st.metric("Containment Rate", f"{containment_rate:.1f}%")
    
    # Bar chart with ANZ colors
    fig = px.bar(
        x=["Resolved", "Escalated"],
        y=[resolved, escalated],
        title="Resolution Breakdown",
        labels={"x": "Outcome", "y": "Count"},
        color=["Resolved", "Escalated"],
        color_discrete_map={"Resolved": ANZ_SUCCESS_GREEN, "Escalated": ANZ_ERROR_RED}
    )
    fig.update_layout(
        **get_dark_theme_layout("Resolution Breakdown"),
        showlegend=False
    )
    st.plotly_chart(fig, width='stretch')


def display_intent_frequency(filters: Dict[str, Any]):
    """Display intent frequency distribution."""
    st.header("🎯 Intent Frequency")

    with st.spinner("Loading intent data..."):
        df = get_interactions_data(filters)
    
    if df.empty or "intent_name" not in df.columns:
        st.info("🎯 **No intent classification data found**\n\nIntent data will appear once users start conversations with the AI assistant. Try different date ranges or check back later.")
        return
    
    # Filter out None/null intents
    intent_df = df[df["intent_name"].notna()]
    
    if intent_df.empty:
        st.info("ℹ️ No intent data available.")
        return
    
    # Intent frequency
    intent_counts = intent_df["intent_name"].value_counts().head(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 intents table
        st.subheader("Top 10 Intents")
        top_intents_df = intent_counts.reset_index()
        top_intents_df.columns = ["Intent", "Count"]
        top_intents_df["Rank"] = range(1, len(top_intents_df) + 1)
        top_intents_df = top_intents_df[["Rank", "Intent", "Count"]]
        st.dataframe(
            top_intents_df,
            width='stretch',
            hide_index=True
        )
    
    with col2:
        # Bar chart
        fig = px.bar(
            x=intent_counts.values,
            y=intent_counts.index,
            orientation='h',
            title="Intent Frequency Distribution",
            labels={"x": "Count", "y": "Intent"},
            color=intent_counts.values,
            color_continuous_scale=[ANZ_LIGHT_GRAY, ANZ_PRIMARY_BLUE]
        )
        # Merge the dark theme layout with custom yaxis settings
        layout_config = get_dark_theme_layout("Intent Frequency Distribution")
        layout_config["yaxis"].update({'categoryorder': 'total ascending'})
        layout_config["showlegend"] = False
        fig.update_layout(**layout_config)
        st.plotly_chart(fig, width='stretch')
    
    # Intent category breakdown
    if "intent_category" in intent_df.columns:
        st.subheader("Intent Category Breakdown")
        category_counts = intent_df["intent_category"].value_counts()
        
        fig = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="Intent Category Distribution",
            color_discrete_sequence=ANZ_COLORS
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont=dict(color=LIGHT_TEXT, size=12),
            marker=dict(line=dict(color=DARK_GRID, width=2))
        )
        fig.update_layout(get_dark_theme_layout("Intent Category Distribution"))
        st.plotly_chart(fig, width='stretch')


def display_escalation_analysis(filters: Dict[str, Any]):
    """Display escalation analysis."""
    st.header("⚠️ Escalation Analysis")
    
    escalations_df = get_escalations_data(filters)
    interactions_df = get_interactions_data(filters)
    
    if escalations_df.empty:
        st.info("ℹ️ No escalation data available.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Escalation reason frequency
        if "trigger_type" in escalations_df.columns:
            st.subheader("Escalation Reasons")
            reason_counts = escalations_df["trigger_type"].value_counts()
            
            fig = px.bar(
                x=reason_counts.values,
                y=reason_counts.index,
                orientation='h',
                title="Escalation Reason Frequency",
                labels={"x": "Count", "y": "Reason"},
                color=reason_counts.values,
                color_continuous_scale=[ANZ_LIGHT_GRAY, ANZ_ERROR_RED]
            )
            # Merge the dark theme layout with custom yaxis settings
            layout_config = get_dark_theme_layout("Escalation Reason Frequency")
            layout_config["yaxis"].update({'categoryorder': 'total ascending'})
            layout_config["showlegend"] = False
            fig.update_layout(**layout_config)
            st.plotly_chart(fig, width='stretch')
    
    with col2:
        # Escalation by mode
        if "assistant_mode" in escalations_df.columns:
            st.subheader("Escalation by Mode")
            mode_escalations = escalations_df["assistant_mode"].value_counts()
            
            fig = px.pie(
                values=mode_escalations.values,
                names=mode_escalations.index,
                title="Escalations by Mode",
                color_discrete_sequence=[ANZ_PRIMARY_BLUE, ANZ_SECONDARY_BLUE]
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont=dict(color=LIGHT_TEXT, size=12),
                marker=dict(line=dict(color=DARK_GRID, width=2))
            )
            fig.update_layout(get_dark_theme_layout("Escalations by Mode"))
            st.plotly_chart(fig, width='stretch')
    
    # Escalation by intent
    if "intent_name" in escalations_df.columns:
        st.subheader("Escalation by Intent")
        escalation_intents = escalations_df["intent_name"].value_counts().head(10)
        
        if not escalation_intents.empty:
            fig = px.bar(
                x=escalation_intents.values,
                y=escalation_intents.index,
                orientation='h',
                title="Top 10 Intents by Escalation Count",
                labels={"x": "Escalation Count", "y": "Intent"},
                color=escalation_intents.values,
                color_continuous_scale=[ANZ_LIGHT_GRAY, ANZ_ERROR_RED]
            )
            # Merge the dark theme layout with custom yaxis settings
            layout_config = get_dark_theme_layout("Top 10 Intents by Escalation Count")
            layout_config["yaxis"].update({'categoryorder': 'total ascending'})
            layout_config["showlegend"] = False
            fig.update_layout(**layout_config)
            st.plotly_chart(fig, width='stretch')


def display_confidence_metrics(filters: Dict[str, Any]):
    """Display confidence metrics."""
    st.header("📊 Confidence Metrics")

    with st.spinner("Loading confidence data..."):
        df = get_interactions_data(filters)
    
    if df.empty or "confidence_score" not in df.columns:
        st.info("ℹ️ No confidence data available.")
        return
    
    # Filter out None/null confidence scores
    confidence_df = df[df["confidence_score"].notna()]
    
    if confidence_df.empty:
        st.info("📊 **No confidence score data found**\n\nConfidence scores will appear once the AI assistant processes user queries. This data helps measure response reliability.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Average confidence
        avg_confidence = confidence_df["confidence_score"].mean()
        st.metric("Average Confidence", f"{avg_confidence:.2%}")
        
        # Confidence by intent
        if "intent_name" in confidence_df.columns:
            st.subheader("Average Confidence by Intent")
            intent_confidence = confidence_df.groupby("intent_name")["confidence_score"].mean().sort_values(ascending=False).head(10)
            
            if not intent_confidence.empty:
                fig = px.bar(
                    x=intent_confidence.values,
                    y=intent_confidence.index,
                    orientation='h',
                    title="Average Confidence by Intent",
                    labels={"x": "Average Confidence", "y": "Intent"},
                    color=intent_confidence.values,
                    color_continuous_scale=[ANZ_ERROR_RED, ANZ_WARNING_ORANGE, ANZ_SUCCESS_GREEN]
                )
                # Merge the dark theme layout with custom axis settings
                layout_config = get_dark_theme_layout("Average Confidence by Intent")
                layout_config["yaxis"].update({'categoryorder': 'total ascending'})
                layout_config["xaxis"].update(dict(tickformat='.0%', gridcolor=DARK_GRID, color=LIGHT_TEXT_SECONDARY))
                layout_config["showlegend"] = False
                fig.update_layout(**layout_config)
                st.plotly_chart(fig, width='stretch')
    
    with col2:
        # Confidence distribution histogram
        st.subheader("Confidence Distribution")
        fig = px.histogram(
            confidence_df,
            x="confidence_score",
            nbins=20,
            title="Confidence Score Distribution",
            labels={"confidence_score": "Confidence Score", "count": "Frequency"},
            color_discrete_sequence=[ANZ_PRIMARY_BLUE]
        )
        # Merge the dark theme layout with custom xaxis settings
        layout_config = get_dark_theme_layout("Confidence Score Distribution")
        layout_config["xaxis"].update(dict(tickformat='.0%', gridcolor=DARK_GRID, color=LIGHT_TEXT_SECONDARY))
        fig.update_layout(**layout_config)
        st.plotly_chart(fig, width='stretch')


def display_performance_metrics(filters: Dict[str, Any]):
    """Display performance metrics."""
    st.header("⚡ Performance Metrics")

    with st.spinner("Loading performance data..."):
        df = get_interactions_data(filters)

    if df.empty:
        st.info("⚡ **No performance data found**\n\nPerformance metrics will be available once the system processes user interactions. This includes response times and system efficiency.")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Average processing time
        if "processing_time_ms" in df.columns:
            processing_df = df[df["processing_time_ms"].notna()]
            if not processing_df.empty:
                avg_time = processing_df["processing_time_ms"].mean() / 1000  # Convert to seconds
                st.metric("Average Processing Time", f"{avg_time:.2f}s")
            else:
                st.info("ℹ️ Processing time data not available.")
        else:
            st.info("ℹ️ Processing time data not available.")

    with col2:
        # Intents with lowest resolution rates
        if "intent_name" in df.columns and "outcome" in df.columns:
            st.subheader("Intents with Lowest Resolution Rates")

            intent_df = df[df["intent_name"].notna()]
            if not intent_df.empty:
                intent_resolution = intent_df.groupby("intent_name").agg({
                    "outcome": lambda x: (x == "resolved").sum() / len(x) * 100 if len(x) > 0 else 0
                }).rename(columns={"outcome": "resolution_rate"})

                lowest_resolution = intent_resolution.sort_values("resolution_rate").head(10)

                if not lowest_resolution.empty:
                    fig = px.bar(
                        x=lowest_resolution.values.flatten(),
                        y=lowest_resolution.index,
                        orientation='h',
                        title="Lowest Resolution Rates by Intent",
                        labels={"x": "Resolution Rate (%)", "y": "Intent"},
                        color=lowest_resolution.values.flatten(),
                        color_continuous_scale=[ANZ_ERROR_RED, ANZ_WARNING_ORANGE]
                    )
                    # Merge the dark theme layout with custom yaxis settings
                    layout_config = get_dark_theme_layout("Lowest Resolution Rates by Intent")
                    layout_config["yaxis"].update({'categoryorder': 'total ascending'})
                    layout_config["showlegend"] = False
                    fig.update_layout(**layout_config)
                    st.plotly_chart(fig, width='stretch')


def display_intent_risk_value_matrix(filters: Dict[str, Any]):
    """Display Intent Risk × Value Matrix bubble chart."""
    st.header("🎯 Intent Risk × Value Matrix")

    try:
        with st.spinner("Loading risk-value matrix..."):
            db_client = get_db_client()
            matrix_data = db_client.get_intent_risk_value_matrix(filters)

        if not matrix_data:
            st.info("🎯 **No intent risk-value data found**\n\nThis analysis requires both intent classification data and risk/value assessments. Data will appear once more conversations are processed.")
            return

        # Convert to DataFrame for plotting
        df = pd.DataFrame(matrix_data)

        # Create bubble chart
        fig = px.scatter(
            df,
            x="containment_rate",
            y="escalation_rate",
            size="volume",
            text="intent_name",
            title="Intent Risk × Value Matrix",
            labels={
                "containment_rate": "Containment Rate (Value) %",
                "escalation_rate": "Escalation Rate (Risk) %",
                "volume": "Volume"
            },
            color="volume",
            color_continuous_scale=[ANZ_LIGHT_GRAY, ANZ_PRIMARY_BLUE],
            size_max=50
        )

        # Update layout for dark theme with custom axis ranges
        layout_config = get_dark_theme_layout("Intent Risk × Value Matrix")
        layout_config["xaxis"].update(dict(range=[-5, 105], gridcolor=DARK_GRID))
        layout_config["yaxis"].update(dict(range=[-5, 105], gridcolor=DARK_GRID))
        layout_config["showlegend"] = False
        fig.update_layout(**layout_config)

        # Update text positioning
        fig.update_traces(
            textposition="top center",
            textfont=dict(size=10, color=LIGHT_TEXT),
            marker=dict(
                line=dict(width=2, color=DARK_GRID),
                sizemode='area',
                sizeref=2.*max(df['volume'])/(50.**2),
                sizemin=4
            )
        )

        # Add quadrant lines and labels
        fig.add_hline(y=50, line_dash="dash", line_color=DARK_GRID, opacity=0.7)
        fig.add_vline(x=50, line_dash="dash", line_color=DARK_GRID, opacity=0.7)

        # Add quadrant labels
        fig.add_annotation(
            x=25, y=25, text="High Risk<br>Low Value<br><strong>Block</strong>",
            showarrow=False, font=dict(color=ANZ_ERROR_RED, size=12)
        )
        fig.add_annotation(
            x=75, y=25, text="Low Risk<br>High Value<br><strong>Scale</strong>",
            showarrow=False, font=dict(color=ANZ_SUCCESS_GREEN, size=12)
        )
        fig.add_annotation(
            x=25, y=75, text="High Risk<br>Low Value<br><strong>Block</strong>",
            showarrow=False, font=dict(color=ANZ_ERROR_RED, size=12)
        )
        fig.add_annotation(
            x=75, y=75, text="High Risk<br>High Value<br><strong>Redesign</strong>",
            showarrow=False, font=dict(color=ANZ_WARNING_ORANGE, size=12)
        )

        st.plotly_chart(fig, width='stretch')

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_intents = len(df)
            st.metric("Total Intents", f"{total_intents:,}")

        with col2:
            high_value_intents = len(df[df["containment_rate"] > 70])
            st.metric("High Value (>70%)", f"{high_value_intents:,}")

        with col3:
            high_risk_intents = len(df[df["escalation_rate"] > 30])
            st.metric("High Risk (>30%)", f"{high_risk_intents:,}")

        with col4:
            critical_intents = len(df[(df["escalation_rate"] > 30) & (df["volume"] > df["volume"].quantile(0.75))])
            st.metric("High Risk + High Volume", f"{critical_intents:,}")

    except Exception as e:
        logger.error("error_displaying_intent_matrix", error=str(e))
        st.error("❌ Failed to load intent risk-value matrix.")


def display_citation_coverage(filters: Dict[str, Any]):
    """Display Citation Coverage & Source Health metrics."""
    st.header("📚 Citation Coverage & Source Health")

    try:
        with st.spinner("Loading citation data..."):
            db_client = get_db_client()
            citation_data = db_client.get_citation_coverage_data(filters)

        if not citation_data:
            st.info("📚 **No citation data found**\n\nCitation metrics will be available once the AI assistant starts providing sources and references in its responses.")
            return

        col1, col2, col3 = st.columns(3)

        with col1:
            coverage_rate = citation_data.get("citation_coverage_rate", 0)
            color = ANZ_SUCCESS_GREEN if coverage_rate >= 95 else ANZ_WARNING_ORANGE if coverage_rate >= 80 else ANZ_ERROR_RED
            st.metric(
                "Citation Coverage",
                f"{coverage_rate:.1f}%",
                help="Percentage of responses with citations (target: ~100%)"
            )

        with col2:
            failed_rate = citation_data.get("failed_retrieval_rate", 0)
            color = ANZ_SUCCESS_GREEN if failed_rate <= 5 else ANZ_WARNING_ORANGE if failed_rate <= 15 else ANZ_ERROR_RED
            st.metric(
                "Failed Retrieval Rate",
                f"{failed_rate:.1f}%",
                help="Percentage of responses with no retrieved chunks"
            )

        with col3:
            total_responses = citation_data.get("total_responses", 0)
            st.metric("Total Responses", f"{total_responses:,}")

        # Top source pages
        top_sources = citation_data.get("top_sources", [])
        if top_sources:
            st.subheader("Top Cited Sources")

            # Create horizontal bar chart
            sources_df = pd.DataFrame(top_sources)
            fig = px.bar(
                sources_df,
                x="count",
                y="source",
                orientation='h',
                title="Most Frequently Cited Sources",
                labels={"count": "Citation Count", "source": "Source"},
                color="count",
                color_continuous_scale=[ANZ_LIGHT_GRAY, ANZ_ACCENT_BLUE]
            )
            # Merge the dark theme layout with custom yaxis settings
            layout_config = get_dark_theme_layout("Most Frequently Cited Sources")
            layout_config["yaxis"].update({'categoryorder': 'total ascending'})
            layout_config["showlegend"] = False
            fig.update_layout(**layout_config)
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("ℹ️ No citation sources found.")

    except Exception as e:
        logger.error("error_displaying_citation_coverage", error=str(e))
        st.error("❌ Failed to load citation coverage data.")
