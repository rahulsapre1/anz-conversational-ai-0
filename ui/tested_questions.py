"""
Tested Questions & Example Queries UI for ContactIQ.

Displays all tested questions organized by mode and intent, allowing users
to filter and find example queries they can use with the assistant.
"""
import streamlit as st
import pandas as pd

# ANZ Brand Colors
ANZ_PRIMARY_BLUE = "#003D82"
ANZ_SECONDARY_BLUE = "#0052A5"
ANZ_ACCENT_BLUE = "#00A0E3"


def get_tested_questions_data():
    """Return DataFrame with all tested questions organized by mode and intent."""
    data = [
        # Customer Mode Questions
        ("customer", "greeting", "Hello, can you help me with my ANZ account?"),
        ("customer", "general_conversation", "Can you tell me what the ANZ app can do?"),
        ("customer", "transaction_explanation", "What does a cash advance transaction mean?"),
        ("customer", "fee_inquiry", "What are the annual fees for ANZ credit cards?"),
        ("customer", "account_limits", "What's the daily limit for cash advances on my credit card?"),
        ("customer", "card_dispute_process", "How do I dispute a transaction on my credit card?"),
        ("customer", "application_process", "How do I apply for a new credit card with ANZ?"),
        ("customer", "account_balance", "What's my current account balance?"),
        ("customer", "transaction_history", "Show me my recent transactions"),
        ("customer", "password_reset", "I forgot my online banking password, how do I reset it?"),
        ("customer", "financial_advice", "Should I invest in shares or keep my money in savings?"),
        ("customer", "complaint", "I'm unhappy with the service I received from your call center"),
        ("customer", "hardship", "I'm having trouble making my loan payments, can you help?"),
        ("customer", "fraud_alert", "I think someone hacked my account"),
        
        # Banker Mode Questions
        ("banker", "greeting", "Hello, I'm calling about a customer inquiry"),
        ("banker", "general_conversation", "What are the current interest rates for home loans?"),
        ("banker", "policy_lookup", "What's the bank's policy on fee waivers?"),
        ("banker", "process_clarification", "How do customers apply for hardship assistance?"),
        ("banker", "product_comparison", "What's the difference between ANZ credit cards?"),
        ("banker", "compliance_phrasing", "How should I phrase information about credit card fees?"),
        ("banker", "fee_structure", "What fees apply to international transactions?"),
        ("banker", "eligibility_criteria", "Who qualifies for hardship assistance?"),
        ("banker", "documentation_requirements", "What documents do customers need for account opening?"),
        ("banker", "customer_specific_query", "Can you check this customer's account balance?"),
        ("banker", "complex_case", "This customer has multiple accounts and complex financial issues"),
        ("banker", "complaint_handling", "A customer is complaining about unfair treatment"),
        ("banker", "regulatory_question", "How do we handle AML compliance for this transaction?"),
    ]
    df = pd.DataFrame(data, columns=["Mode", "Intent", "Question"])
    return df


def render_tested_questions():
    """Render the tested questions and example queries page."""
    # Page header
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {ANZ_PRIMARY_BLUE} 0%, {ANZ_SECONDARY_BLUE} 100%); 
                padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0; font-size: 2.5rem;'>📋 Tested Questions & Example Queries</h1>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
            Pre-validated questions you can use with ContactIQ
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    The following questions have been **tested and validated** with ContactIQ. 
    You can use these as examples when interacting with the assistant in Chat mode.
    Filter by Mode (Customer/Banker) or Intent to find relevant queries for your needs.
    """)
    
    # Get tested questions data
    questions_df = get_tested_questions_data()
    
    # Filter controls
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        mode_filter = st.selectbox(
            "Filter by Mode:",
            ["All"] + sorted(questions_df["Mode"].unique().tolist()),
            key="tested_questions_mode_filter"
        )
    with col2:
        intent_filter = st.selectbox(
            "Filter by Intent:",
            ["All"] + sorted(questions_df["Intent"].unique().tolist()),
            key="tested_questions_intent_filter"
        )
    with col3:
        search_query = st.text_input(
            "Search questions:",
            key="tested_questions_search",
            placeholder="Type to search in questions..."
        )
    
    # Apply filters
    filtered_df = questions_df.copy()
    if mode_filter != "All":
        filtered_df = filtered_df[filtered_df["Mode"] == mode_filter]
    if intent_filter != "All":
        filtered_df = filtered_df[filtered_df["Intent"] == intent_filter]
    if search_query:
        filtered_df = filtered_df[
            filtered_df["Question"].str.contains(search_query, case=False, na=False)
        ]
    
    # Display summary stats with consistent styling
    customer_count = len(filtered_df[filtered_df["Mode"] == "customer"]) if not filtered_df.empty else 0
    banker_count = len(filtered_df[filtered_df["Mode"] == "banker"]) if not filtered_df.empty else 0
    
    col1, col2, col3 = st.columns([1, 1, 1.2])
    with col1:
        st.metric("Total Tested Questions", f"{len(questions_df)}")
    with col2:
        st.metric("Filtered Results", f"{len(filtered_df)}")
    with col3:
        # Use custom styling to match st.metric appearance with compact alignment
        st.markdown(f"""
        <div style='background-color: transparent; padding: 0.5rem 0;'>
            <div style='font-size: 0.875rem; color: rgb(49, 51, 63); opacity: 0.6; margin-bottom: 0.25rem; font-weight: 400; line-height: 1.4;'>
                Mode Split
            </div>
            <div style='font-size: 1.875rem; font-weight: 600; color: rgb(49, 51, 63); line-height: 1.2; white-space: nowrap; display: inline-block;'>
                Customer: {customer_count} <span style='margin: 0 0.15rem;'>|</span> Banker: {banker_count}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display table
    if not filtered_df.empty:
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            height=500
        )
        
        # Instructions for using the questions
        st.info("""
        💡 **How to use these questions:**
        1. Copy a question from the table above
        2. Go to the **Chat** page from the sidebar
        3. Select the appropriate **Assistant Mode** (Customer or Banker) matching the question
        4. Paste the question into the chat input and send it
        """)
    else:
        st.warning("No questions match your filters. Try adjusting your search criteria.")
        if st.button("Clear All Filters"):
            st.rerun()
