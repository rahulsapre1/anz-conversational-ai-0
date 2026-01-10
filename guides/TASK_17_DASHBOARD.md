# Task 17: KPI Dashboard UI

## Overview
Implement KPI dashboard with metrics from PRD Section 5, displaying overall usage, resolution metrics, intent frequency, escalation analysis, confidence metrics, and performance metrics. Includes visualizations, filters, and real-time updates.

## Prerequisites
- Task 1 completed (project structure, config, logging)
- Task 2 completed (Database schema and Supabase client)
- Task 14 completed (Logging service)
- Task 15 completed (Authentication module)
- Virtual environment activated

## Deliverables

### 1. KPI Dashboard (ui/dashboard.py)

Create `ui/dashboard.py` with dashboard functionality.

**Key Requirements**:
- Authentication check (via auth.py)
- Metrics calculation from Supabase
- Visualizations (bar, line, pie charts)
- Real-time updates
- Filters (mode, date range, intent)

## Metrics to Display

Based on PRD Section 5, display the following metrics:

### 1. Overall Usage Metrics
- Total conversations
- Total interactions
- Average interactions per conversation

### 2. Mode Breakdown
- Customer mode usage count
- Banker mode usage count
- Percentage split

### 3. Resolution Metrics
- Containment rate (resolved without escalation)
- Escalation rate
- Total resolved count
- Total escalated count

### 4. Intent Frequency
- Intent frequency distribution (chart)
- Top 10 intents
- Intent category breakdown

### 5. Escalation Analysis
- Escalation reason frequency
- Escalation by intent
- Escalation by mode

### 6. Confidence Metrics
- Average confidence score (overall)
- Average confidence by intent
- Confidence distribution histogram

### 7. Performance Metrics
- Average processing time
- Intents with lowest resolution rates

## Implementation

### Step 1: Dashboard Structure

```python
# ui/dashboard.py
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


def render_dashboard():
    """
    Render the KPI dashboard.
    
    This function handles:
    - Authentication check
    - Filters (mode, date range, intent)
    - Metrics calculation
    - Visualizations
    - Real-time updates
    """
    # Check authentication
    check_authentication()
    
    # Page header
    st.title("📊 ContactIQ KPI Dashboard")
    st.markdown("---")
    
    # Filters
    filters = render_filters()
    
    # Overall metrics
    st.header("Overall Metrics")
    display_overall_metrics(filters)
    
    st.markdown("---")
    
    # Mode breakdown
    st.header("Mode Breakdown")
    display_mode_breakdown(filters)
    
    st.markdown("---")
    
    # Resolution metrics
    st.header("Resolution Metrics")
    display_resolution_metrics(filters)
    
    st.markdown("---")
    
    # Intent frequency
    st.header("Intent Frequency")
    display_intent_frequency(filters)
    
    st.markdown("---")
    
    # Escalation analysis
    st.header("Escalation Analysis")
    display_escalation_analysis(filters)
    
    st.markdown("---")
    
    # Confidence metrics
    st.header("Confidence Metrics")
    display_confidence_metrics(filters)
    
    st.markdown("---")
    
    # Performance metrics
    st.header("Performance Metrics")
    display_performance_metrics(filters)
    
    # Auto-refresh option
    if st.button("🔄 Refresh Data"):
        st.rerun()
```

### Step 2: Filters

```python
def render_filters() -> Dict[str, Any]:
    """
    Render dashboard filters.
    
    Returns:
        Dictionary with filter values
    """
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
        intent_filter = st.selectbox(
            "Intent:",
            ["All"] + get_available_intents(),
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
        # Query distinct intents from interactions table
        # This is a placeholder - adjust based on your Supabase client implementation
        # intents = db_client.get_distinct_intents()
        # return intents
        return []  # Placeholder
    except Exception as e:
        logger.error("error_getting_intents", error=str(e))
        return []
```

### Step 3: Metrics Calculation

```python
def get_interactions_data(filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Get interactions data from Supabase with filters.
    
    Args:
        filters: Filter dictionary
    
    Returns:
        DataFrame with interactions data
    """
    try:
        db_client = get_db_client()
        
        # Build query with filters
        query_filters = {}
        if filters.get("mode"):
            query_filters["assistant_mode"] = filters["mode"]
        if filters.get("start_date"):
            query_filters["created_at__gte"] = filters["start_date"]
        if filters.get("end_date"):
            query_filters["created_at__lte"] = filters["end_date"]
        if filters.get("intent"):
            query_filters["intent_name"] = filters["intent"]
        
        # Fetch interactions
        # Adjust based on your Supabase client implementation
        interactions = db_client.get_interactions(**query_filters)
        
        # Convert to DataFrame
        df = pd.DataFrame(interactions)
        
        return df
    
    except Exception as e:
        logger.error("error_fetching_interactions", error=str(e))
        return pd.DataFrame()


def get_escalations_data(filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Get escalations data from Supabase with filters.
    
    Args:
        filters: Filter dictionary
    
    Returns:
        DataFrame with escalations data
    """
    try:
        db_client = get_db_client()
        
        # Build query with filters
        query_filters = {}
        if filters.get("mode"):
            query_filters["assistant_mode"] = filters["mode"]
        if filters.get("start_date"):
            query_filters["created_at__gte"] = filters["start_date"]
        if filters.get("end_date"):
            query_filters["created_at__lte"] = filters["end_date"]
        
        # Fetch escalations
        escalations = db_client.get_escalations(**query_filters)
        
        # Convert to DataFrame
        df = pd.DataFrame(escalations)
        
        return df
    
    except Exception as e:
        logger.error("error_fetching_escalations", error=str(e))
        return pd.DataFrame()
```

### Step 4: Overall Metrics Display

```python
def display_overall_metrics(filters: Dict[str, Any]):
    """
    Display overall usage metrics.
    
    Args:
        filters: Filter dictionary
    """
    df = get_interactions_data(filters)
    
    if df.empty:
        st.info("No data available for the selected filters.")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_interactions = len(df)
        st.metric("Total Interactions", total_interactions)
    
    with col2:
        total_conversations = df["conversation_id"].nunique() if "conversation_id" in df.columns else total_interactions
        st.metric("Total Conversations", total_conversations)
    
    with col3:
        avg_interactions = total_interactions / total_conversations if total_conversations > 0 else 0
        st.metric("Avg Interactions/Conversation", f"{avg_interactions:.2f}")
```

### Step 5: Mode Breakdown Display

```python
def display_mode_breakdown(filters: Dict[str, Any]):
    """
    Display mode breakdown metrics.
    
    Args:
        filters: Filter dictionary
    """
    df = get_interactions_data(filters)
    
    if df.empty:
        st.info("No data available.")
        return
    
    if "assistant_mode" in df.columns:
        mode_counts = df["assistant_mode"].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Metrics
            customer_count = mode_counts.get("customer", 0)
            banker_count = mode_counts.get("banker", 0)
            total = customer_count + banker_count
            
            st.metric("Customer Mode", customer_count)
            st.metric("Banker Mode", banker_count)
        
        with col2:
            # Pie chart
            if total > 0:
                fig = px.pie(
                    values=[customer_count, banker_count],
                    names=["Customer", "Banker"],
                    title="Mode Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No mode data available.")
    else:
        st.info("Mode data not available.")
```

### Step 6: Resolution Metrics Display

```python
def display_resolution_metrics(filters: Dict[str, Any]):
    """
    Display resolution metrics (containment/escalation rates).
    
    Args:
        filters: Filter dictionary
    """
    df = get_interactions_data(filters)
    
    if df.empty:
        st.info("No data available.")
        return
    
    # Calculate metrics
    total = len(df)
    resolved = len(df[df["outcome"] == "resolved"]) if "outcome" in df.columns else 0
    escalated = len(df[df["outcome"] == "escalated"]) if "outcome" in df.columns else 0
    
    containment_rate = (resolved / total * 100) if total > 0 else 0
    escalation_rate = (escalated / total * 100) if total > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Interactions", total)
    
    with col2:
        st.metric("Resolved", resolved, delta=f"{containment_rate:.1f}%")
    
    with col3:
        st.metric("Escalated", escalated, delta=f"{escalation_rate:.1f}%")
    
    with col4:
        st.metric("Containment Rate", f"{containment_rate:.1f}%")
    
    # Bar chart
    fig = px.bar(
        x=["Resolved", "Escalated"],
        y=[resolved, escalated],
        title="Resolution Breakdown",
        labels={"x": "Outcome", "y": "Count"}
    )
    st.plotly_chart(fig, use_container_width=True)
```

### Step 7: Intent Frequency Display

```python
def display_intent_frequency(filters: Dict[str, Any]):
    """
    Display intent frequency distribution.
    
    Args:
        filters: Filter dictionary
    """
    df = get_interactions_data(filters)
    
    if df.empty or "intent_name" not in df.columns:
        st.info("No intent data available.")
        return
    
    # Intent frequency
    intent_counts = df["intent_name"].value_counts().head(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 intents
        st.subheader("Top 10 Intents")
        st.dataframe(
            intent_counts.reset_index().rename(columns={"index": "Intent", "intent_name": "Count"}),
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        # Bar chart
        fig = px.bar(
            x=intent_counts.values,
            y=intent_counts.index,
            orientation='h',
            title="Intent Frequency Distribution",
            labels={"x": "Count", "y": "Intent"}
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Intent category breakdown
    if "intent_category" in df.columns:
        st.subheader("Intent Category Breakdown")
        category_counts = df["intent_category"].value_counts()
        
        fig = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="Intent Category Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
```

### Step 8: Escalation Analysis Display

```python
def display_escalation_analysis(filters: Dict[str, Any]):
    """
    Display escalation analysis.
    
    Args:
        filters: Filter dictionary
    """
    escalations_df = get_escalations_data(filters)
    interactions_df = get_interactions_data(filters)
    
    if escalations_df.empty:
        st.info("No escalation data available.")
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
                labels={"x": "Count", "y": "Reason"}
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Escalation by mode
        if "assistant_mode" in escalations_df.columns:
            st.subheader("Escalation by Mode")
            mode_escalations = escalations_df["assistant_mode"].value_counts()
            
            fig = px.pie(
                values=mode_escalations.values,
                names=mode_escalations.index,
                title="Escalations by Mode"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Escalation by intent
    if "intent_name" in escalations_df.columns and "intent_name" in interactions_df.columns:
        st.subheader("Escalation by Intent")
        escalation_intents = escalations_df["intent_name"].value_counts().head(10)
        
        fig = px.bar(
            x=escalation_intents.values,
            y=escalation_intents.index,
            orientation='h',
            title="Top 10 Intents by Escalation Count",
            labels={"x": "Escalation Count", "y": "Intent"}
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
```

### Step 9: Confidence Metrics Display

```python
def display_confidence_metrics(filters: Dict[str, Any]):
    """
    Display confidence metrics.
    
    Args:
        filters: Filter dictionary
    """
    df = get_interactions_data(filters)
    
    if df.empty or "confidence_score" not in df.columns:
        st.info("No confidence data available.")
        return
    
    # Filter out None/null confidence scores
    confidence_df = df[df["confidence_score"].notna()]
    
    if confidence_df.empty:
        st.info("No confidence scores available.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Average confidence
        avg_confidence = confidence_df["confidence_score"].mean()
        st.metric("Average Confidence", f"{avg_confidence:.2%}")
        
        # Confidence by intent
        if "intent_name" in confidence_df.columns:
            st.subheader("Average Confidence by Intent")
            intent_confidence = confidence_df.groupby("intent_name")["confidence_score"].mean().sort_values(ascending=False)
            
            fig = px.bar(
                x=intent_confidence.values,
                y=intent_confidence.index,
                orientation='h',
                title="Average Confidence by Intent",
                labels={"x": "Average Confidence", "y": "Intent"}
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Confidence distribution histogram
        st.subheader("Confidence Distribution")
        fig = px.histogram(
            confidence_df,
            x="confidence_score",
            nbins=20,
            title="Confidence Score Distribution",
            labels={"confidence_score": "Confidence Score", "count": "Frequency"}
        )
        st.plotly_chart(fig, use_container_width=True)
```

### Step 10: Performance Metrics Display

```python
def display_performance_metrics(filters: Dict[str, Any]):
    """
    Display performance metrics.
    
    Args:
        filters: Filter dictionary
    """
    df = get_interactions_data(filters)
    
    if df.empty:
        st.info("No data available.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Average processing time
        if "processing_time_ms" in df.columns:
            avg_time = df["processing_time_ms"].mean() / 1000  # Convert to seconds
            st.metric("Average Processing Time", f"{avg_time:.2f}s")
        else:
            st.info("Processing time data not available.")
    
    with col2:
        # Intents with lowest resolution rates
        if "intent_name" in df.columns and "outcome" in df.columns:
            st.subheader("Intents with Lowest Resolution Rates")
            
            intent_resolution = df.groupby("intent_name").agg({
                "outcome": lambda x: (x == "resolved").sum() / len(x) * 100
            }).rename(columns={"outcome": "resolution_rate"})
            
            lowest_resolution = intent_resolution.sort_values("resolution_rate").head(10)
            
            fig = px.bar(
                x=lowest_resolution.values.flatten(),
                y=lowest_resolution.index,
                orientation='h',
                title="Lowest Resolution Rates by Intent",
                labels={"x": "Resolution Rate (%)", "y": "Intent"}
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
```

### Step 11: Complete Dashboard

```python
# ui/dashboard.py (complete file)
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


def render_dashboard():
    """Render the KPI dashboard."""
    # Check authentication
    check_authentication()
    
    # Page header
    st.title("📊 ContactIQ KPI Dashboard")
    st.markdown("---")
    
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
    
    # Auto-refresh
    st.markdown("---")
    if st.button("🔄 Refresh Data", type="primary"):
        st.rerun()


# Include all helper functions from Steps 2-10
# ... (see steps above for implementation)
```

## Additional Dependencies

Add to `requirements.txt`:
```python
plotly>=5.18.0  # For interactive charts
pandas>=2.1.0   # For data manipulation (should already be present)
```

## Success Criteria

- [ ] Authentication required before accessing dashboard
- [ ] Overall usage metrics displayed correctly
- [ ] Mode breakdown displayed with charts
- [ ] Resolution metrics (containment/escalation rates) calculated correctly
- [ ] Intent frequency distribution displayed
- [ ] Escalation analysis displayed (reason frequency, by intent, by mode)
- [ ] Confidence metrics displayed (average, by intent, distribution)
- [ ] Performance metrics displayed (processing time, lowest resolution rates)
- [ ] Filters work correctly (mode, date range, intent)
- [ ] Charts render correctly (bar, line, pie)
- [ ] Real-time updates work (refresh button)
- [ ] Handles empty data gracefully

## Testing

### Manual Testing

1. **Test Authentication**:
   - Verify password prompt appears
   - Verify dashboard accessible after authentication

2. **Test Filters**:
   - Test mode filter (All, Customer, Banker)
   - Test date range filter
   - Test intent filter
   - Verify metrics update based on filters

3. **Test Metrics**:
   - Verify all metrics calculate correctly
   - Verify charts render
   - Verify data matches database

4. **Test Empty Data**:
   - Test with no interactions
   - Verify graceful handling (info messages)

5. **Test Real-time Updates**:
   - Add new interaction
   - Click refresh
   - Verify metrics update

## Integration Points

- **Task 2 (Database)**: Uses Supabase client to fetch data
- **Task 14 (Logging)**: Data comes from logged interactions
- **Task 15 (Authentication)**: Uses `check_authentication()` from `ui/auth.py`
- **Task 18 (Main App)**: Integrated into main application navigation

## Notes

- **Plotly Charts**: Uses Plotly for interactive charts (better than Streamlit native charts)
- **Data Caching**: Consider adding caching for expensive queries
- **Real-time**: Refresh button for now; can be enhanced with auto-refresh
- **Empty Data**: All sections handle empty data gracefully
- **Performance**: Consider pagination for large datasets

## Reference

- **DETAILED_PLAN.md** Section 9.3 (KPI Dashboard)
- **PRD.md** Section 5 (Success Metrics)
- **TASK_BREAKDOWN.md** Task 17
- **Task 2 Guide**: For Supabase client usage
- **Streamlit Charts**: https://docs.streamlit.io/library/api-reference/charts
- **Plotly Express**: https://plotly.com/python/plotly-express/
