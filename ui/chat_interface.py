"""
Chat Interface UI for ContactIQ.

Implements Streamlit chat interface with mode selection, chat history,
message input, and response display with citations, confidence scores, and escalation messages.
"""
import streamlit as st
import asyncio
import time
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from ui.auth import check_authentication
from utils.logger import get_logger
from config import Config
from database.supabase_client import get_db_client

# Import pipeline services
from services.intent_classifier import IntentClassifier
from services.router import Router
from services.retrieval_service import RetrievalService
from services.response_generator import ResponseGenerator
from services.confidence_scorer import ConfidenceScorer
from services.escalation_handler import EscalationHandler
from services.logger import get_interaction_logger

logger = get_logger(__name__)
db_client = get_db_client()

# ANZ Brand Colors
ANZ_PRIMARY_BLUE = "#003D82"
ANZ_SECONDARY_BLUE = "#0052A5"
ANZ_ACCENT_BLUE = "#00A0E3"


def render_chat_interface():
    """
    Render the main chat interface.
    
    This function handles:
    - Authentication check
    - Mode selection
    - Chat history display
    - Message input
    - Response display
    - Pipeline execution
    """
    # Check authentication
    check_authentication()

    # Initialize session state
    initialize_session_state()

    # Add custom CSS for better message styling and sidebar
    st.markdown("""
    <style>
    .stChatMessage {
        margin-bottom: 1rem !important;
        padding: 1rem !important;
        border-radius: 10px !important;
    }
    .stChatMessage[data-testid="chat-message-user"] {
        background-color: #f0f8ff !important;
        border-left: 4px solid #003d82 !important;
    }
    .stChatMessage[data-testid="chat-message-assistant"] {
        background-color: #f8f9fa !important;
        border-left: 4px solid #0052a5 !important;
    }
    .message-timestamp {
        font-size: 0.8em;
        color: #666;
        margin-bottom: 0.5rem;
    }
    .message-actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    .message-action-btn {
        font-size: 0.8em;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
    }
    /* Sidebar text styling - ensure black text */
    [data-testid="stSidebar"] {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] h3 {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] label {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] p {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] .stRadio label p {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] .stButton button {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] .stMetric {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] .stMetric label {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] .stMetric [data-testid="stMetricValue"] {
        color: #000000 !important;
    }
    [data-testid="stSidebar"] .stMetric [data-testid="stMetricLabel"] {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Page header with ANZ logo
    col_logo, col_title = st.columns([1, 10])
    
    with col_logo:
        # Try to load ANZ logo from common locations
        # If logo file exists, it will be displayed; otherwise, show styled text
        logo_paths = [
            "anz_logo.png",
            "anz_logo.svg",
            "assets/anz_logo.png",
            "assets/anz_logo.svg",
            "ui/anz_logo.png",
            "ui/anz_logo.svg"
        ]
        logo_found = False
        for path in logo_paths:
            if os.path.exists(path):
                st.image(path, width=120)
                logo_found = True
                break
        
        if not logo_found:
            # Fallback: Styled ANZ text logo matching ANZ branding
            st.markdown(f"""
            <div style='background-color: {ANZ_PRIMARY_BLUE}; color: white; padding: 0.5rem 1rem; border-radius: 4px; font-weight: bold; font-size: 1.2rem; letter-spacing: 1px; text-align: center; width: fit-content;'>
                ANZ
            </div>
            """, unsafe_allow_html=True)
    
    with col_title:
        st.markdown(f"<h1 style='color: {ANZ_PRIMARY_BLUE}; margin: 0; font-size: 2rem; font-weight: 600; padding-top: 0.5rem;'>ContactIQ Chat</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: white; background-color: {ANZ_ACCENT_BLUE}; padding: 0.3rem 0.8rem; border-radius: 4px; margin: 0.5rem 0 0 0; display: inline-block; font-size: 0.9rem;'>ANZ Conversational AI</p>", unsafe_allow_html=True)
    
    st.markdown("---")

    # Sidebar for mode selection and controls
    with st.sidebar:
        # ANZ Logo at top left of sidebar
        logo_paths = [
            "anz_logo.png",
            "anz_logo.svg",
            "assets/anz_logo.png",
            "assets/anz_logo.svg",
            "ui/anz_logo.png",
            "ui/anz_logo.svg"
        ]
        logo_found = False
        for path in logo_paths:
            if os.path.exists(path):
                st.markdown(f"""
                <div style='text-align: left; margin-bottom: 1rem;'>
                    <img src='{path}' alt='ANZ Logo' style='height: 40px; width: auto;' />
                </div>
                """, unsafe_allow_html=True)
                logo_found = True
                break
        
        if not logo_found:
            # Fallback: Styled ANZ text logo matching ANZ branding (left-aligned)
            st.markdown(f"""
            <div style='background-color: {ANZ_PRIMARY_BLUE}; color: white; padding: 0.5rem 1rem; border-radius: 4px; font-weight: bold; font-size: 1rem; letter-spacing: 1px; text-align: left; width: fit-content; margin-bottom: 1rem;'>
                ANZ
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")

        st.header("Settings")

        # Clear chat button with confirmation
        if "confirm_clear_chat" not in st.session_state:
            st.session_state.confirm_clear_chat = False

        if st.button("Clear Chat History", type="secondary", help="Clear all messages in the current chat session"):
            st.session_state.confirm_clear_chat = True

        # Show confirmation dialog
        if st.session_state.confirm_clear_chat:
            st.warning("⚠️ **Are you sure you want to clear the chat history?**\n\nThis action cannot be undone. All messages in this conversation will be permanently deleted.")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("❌ Cancel", type="secondary", use_container_width=True):
                    st.session_state.confirm_clear_chat = False
                    st.rerun()
            with col2:
                if st.button("🗑️ Yes, Clear Chat", type="primary", use_container_width=True):
                    # Clear local chat history
                    st.session_state.chat_history = []

                    # Start a new conversation
                    initialize_conversation(st.session_state.assistant_mode)

                    st.session_state.confirm_clear_chat = False
                    st.success("✅ Chat history cleared successfully!")
                    st.rerun()

        # Show conversation stats (always visible)
        st.markdown("### Conversation Stats")
        user_messages = sum(1 for msg in st.session_state.chat_history if msg["role"] == "user")
        assistant_messages = sum(1 for msg in st.session_state.chat_history if msg["role"] == "assistant")
        st.metric("User Messages", user_messages)
        st.metric("Assistant Messages", assistant_messages)
    
    # Main chat area
    st.markdown("### Chat")
    
    # Display chat history
    display_chat_history()
    
    # Message input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Process message
        process_user_message(user_input, st.session_state.assistant_mode)


def generate_conversation_id() -> str:
    """Generate a unique conversation ID."""
    return f"conv_{uuid.uuid4().hex[:16]}"


def initialize_conversation(assistant_mode: str):
    """Initialize a new conversation in database and session state."""
    conversation_id = generate_conversation_id()

    # Create conversation in database
    conversation_uuid = db_client.create_conversation(
        conversation_id=conversation_id,
        assistant_mode=assistant_mode
    )

    if conversation_uuid:
        st.session_state.conversation_uuid = conversation_uuid
        st.session_state.conversation_id = conversation_id
        st.session_state.chat_history = []
        logger.info(f"New conversation initialized: {conversation_id}")
        return True
    else:
        logger.error("Failed to create conversation in database")
        return False


def load_conversation_history(conversation_uuid: str) -> List[Dict[str, Any]]:
    """Load conversation history from database."""
    try:
        messages = db_client.load_conversation_history(conversation_uuid)
        chat_history = []

        for msg in messages:
            message = {
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg["timestamp"]
            }

            # Add assistant-specific fields
            if msg["role"] == "assistant":
                message.update({
                    "citations": msg.get("citations", []),
                    "confidence_score": msg.get("confidence_score"),
                    "escalated": msg.get("escalated", False),
                    "escalation_message": msg.get("escalation_message"),
                    "trigger_type": msg.get("trigger_type")
                })

            chat_history.append(message)

        logger.info(f"Loaded {len(chat_history)} messages from conversation {conversation_uuid}")
        return chat_history
    except Exception as e:
        logger.error(f"Failed to load conversation history: {e}")
        return []


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    logger.info(f"Initializing session state. Current keys: {list(st.session_state.keys())}")

    if "assistant_mode" not in st.session_state:
        st.session_state.assistant_mode = "customer"
        logger.info("Set default assistant_mode to customer")

    if "confirm_clear_chat" not in st.session_state:
        st.session_state.confirm_clear_chat = False

    # Initialize or load conversation
    if "conversation_uuid" not in st.session_state:
        logger.info("No conversation_uuid in session state")
        # Try to load existing conversation or create new one
        if "conversation_id" in st.session_state and st.session_state.conversation_id:
            logger.info(f"Found conversation_id in session: {st.session_state.conversation_id}")
            # Try to find existing conversation
            existing_conversation = db_client.get_conversation_by_id(st.session_state.conversation_id)
            if existing_conversation and existing_conversation["is_active"]:
                st.session_state.conversation_uuid = existing_conversation["id"]
                # Only load from database if we don't already have chat history
                if "chat_history" not in st.session_state:
                    st.session_state.chat_history = load_conversation_history(existing_conversation["id"])
                    logger.info(f"Loaded existing conversation: {existing_conversation['id']}")
                else:
                    logger.info(f"Using existing chat history: {len(st.session_state.chat_history)} messages")
            else:
                # Conversation not found or inactive, create new one
                logger.info("Existing conversation not found or inactive, creating new one")
                initialize_conversation(st.session_state.assistant_mode)
        else:
            # No existing conversation, create new one
            logger.info("No existing conversation_id, creating new conversation")
            initialize_conversation(st.session_state.assistant_mode)
    else:
        logger.info(f"Conversation_uuid exists: {st.session_state.conversation_uuid}")
        # Always load conversation history from database to ensure it's up to date
        logger.info("Loading conversation history from database")
        loaded_history = load_conversation_history(st.session_state.conversation_uuid)
        if loaded_history:
            st.session_state.chat_history = loaded_history
            logger.info(f"Loaded {len(loaded_history)} messages from database")
        else:
            # If no history loaded, initialize empty
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
                logger.info("Initialized empty chat history")


def display_chat_history():
    """Display chat history from session state."""
    if not st.session_state.chat_history:
        st.info("💬 **Welcome to ContactIQ Chat!**\n\n👋 Start a conversation by typing a message below. You can ask questions about ANZ banking services, accounts, or general inquiries.")
        return
    
    # Display each message
    for i, message in enumerate(st.session_state.chat_history):
        if message["role"] == "user":
            with st.chat_message("user"):
                # Timestamp
                timestamp = message.get("timestamp", datetime.now())
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                st.markdown(f'<div class="message-timestamp">{timestamp.strftime("%H:%M")}</div>', unsafe_allow_html=True)

                st.write(message["content"])

        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                # Timestamp
                timestamp = message.get("timestamp", datetime.now())
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                st.markdown(f'<div class="message-timestamp">{timestamp.strftime("%H:%M")}</div>', unsafe_allow_html=True)

                # Check if this is an escalated message
                if message.get("escalated"):
                    # For escalated messages, show escalation message (which is already in content)
                    st.info(f"🚨 {message.get('content', message.get('escalation_message', 'Escalated to human support'))}")
                else:
                    # Response text (non-escalated)
                    # Use st.markdown() for proper markdown rendering control
                    # This ensures consistent formatting and prevents unexpected markdown interpretation
                    st.markdown(message["content"])

                    # Citations (only for non-escalated messages)
                    if message.get("citations"):
                        citation_count = len(message["citations"])
                        with st.expander(f"📚 {citation_count} Source{'s' if citation_count != 1 else ''}", expanded=False):
                            for citation in message["citations"]:
                                if citation.get("url"):
                                    st.markdown(f"[{citation['number']}] [{citation['source']}]({citation['url']})")
                                else:
                                    st.markdown(f"[{citation['number']}] {citation['source']}")

                    # Confidence score (only for non-escalated messages)
                    if message.get("confidence_score") is not None:
                        confidence = message["confidence_score"]
                        if confidence >= 0.68:
                            st.success(f"✅ Confidence: {confidence:.2%}")
                        elif confidence >= 0.5:
                            st.warning(f"⚠️ Confidence: {confidence:.2%}")
                        else:
                            st.error(f"❌ Confidence: {confidence:.2%}")

        elif message["role"] == "system":
            st.error(message["content"])


def process_user_message(user_query: str, assistant_mode: str):
    """Process user message through the pipeline."""
    # Prepare conversation history (exclude system messages, format for pipeline)
    conversation_history = []
    for msg in st.session_state.chat_history:
        if msg.get("role") in ["user", "assistant"]:
            conversation_history.append({
                "role": msg["role"],
                "content": msg.get("content", "")
            })

    # Debug: Log conversation history being passed to pipeline
    logger.info(f"Conversation history for pipeline: {len(conversation_history)} messages")
    for i, msg in enumerate(conversation_history):
        logger.info(f"History {i+1}: {msg['role']} - {msg['content'][:50]}...")
    logger.info(f"Current query: {user_query}")

    # Add user message to history and database
    user_message = {
        "role": "user",
        "content": user_query,
        "timestamp": datetime.now()
    }
    st.session_state.chat_history.append(user_message)

    # Save user message to database
    if "conversation_uuid" in st.session_state:
        db_client.save_message(
            conversation_uuid=st.session_state.conversation_uuid,
            role="user",
            content=user_query
        )

    # Show loading indicator
    with st.spinner("🤔 Thinking..."):
        result = asyncio.run(run_pipeline_async(user_query, assistant_mode, conversation_history))

    # Add response to history and database
    if result:
        if result.get("escalated"):
            assistant_message = {
                "role": "assistant",
                "content": result.get("escalation_message", "Escalated to human support"),
                "escalated": True,
                "escalation_message": result.get("escalation_message"),
                "trigger_type": result.get("trigger_type"),
                "timestamp": datetime.now()
            }
            st.session_state.chat_history.append(assistant_message)

            # Save escalated message to database
            if "conversation_uuid" in st.session_state:
                db_client.save_message(
                    conversation_uuid=st.session_state.conversation_uuid,
                    role="assistant",
                    content=assistant_message["content"],
                    escalated=True,
                    escalation_message=result.get("escalation_message"),
                    trigger_type=result.get("trigger_type")
                )
        else:
            assistant_message = {
                "role": "assistant",
                "content": result.get("response_text", ""),
                "citations": result.get("citations", []),
                "confidence_score": result.get("confidence_score"),
                "escalated": False,
                "timestamp": datetime.now()
            }
            st.session_state.chat_history.append(assistant_message)

            # Save assistant message to database
            if "conversation_uuid" in st.session_state:
                db_client.save_message(
                    conversation_uuid=st.session_state.conversation_uuid,
                    role="assistant",
                    content=result.get("response_text", ""),
                    citations=result.get("citations", []),
                    confidence_score=result.get("confidence_score")
                )
    else:
        error_message = {
            "role": "system",
            "content": "Sorry, I encountered an error. Please try again.",
            "timestamp": datetime.now()
        }
        st.session_state.chat_history.append(error_message)

        # Save error message to database
        if "conversation_uuid" in st.session_state:
            db_client.save_message(
                conversation_uuid=st.session_state.conversation_uuid,
                role="system",
                content=error_message["content"]
            )

    st.rerun()


async def run_pipeline_async(
    user_query: str, 
    assistant_mode: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Optional[Dict[str, Any]]:
    """
    Run the full pipeline asynchronously.
    
    Args:
        user_query: User's query
        assistant_mode: 'customer' or 'banker'
        conversation_history: Optional list of previous messages
    
    Returns:
        Result dictionary with response or escalation
    """
    logger.info("pipeline_started", assistant_mode=assistant_mode, query_length=len(user_query))
    
    # Initialize logger and start timer
    interaction_logger = get_interaction_logger()
    interaction_logger.start_timer()
    
    try:
        # Initialize services
        intent_classifier = IntentClassifier()
        router = Router()
        retrieval_service = RetrievalService()
        response_generator = ResponseGenerator()
        confidence_scorer = ConfidenceScorer()
        escalation_handler = EscalationHandler()
        
        # Step 1: Intent Classification (with conversation history)
        intent_result = await intent_classifier.classify(user_query, assistant_mode, conversation_history)
        if not intent_result:
            logger.error("intent_classification_failed")
            escalation_result = await escalation_handler.handle_escalation(
                trigger_type="insufficient_evidence",
                assistant_mode=assistant_mode,
                escalation_reason="Intent classification failed",
                user_query=user_query
            )
            
            # Log interaction
            interaction_logger.log_interaction(
                assistant_mode=assistant_mode,
                user_query=user_query,
                outcome="escalated",
                escalation_reason=escalation_result["escalation_reason"],
                step_1_intent_completed=False,
                step_6_escalation_triggered=True
            )
            
            return escalation_result
        
        # Step 2: Router
        routing_decision = router.route(
            intent_category=intent_result["intent_category"],
            intent_name=intent_result["intent_name"],
            assistant_mode=assistant_mode
        )
        
        # If escalate, skip to escalation handler
        if routing_decision["route"] == "escalate":
            escalation_result = await escalation_handler.handle_escalation(
                trigger_type="human_only",
                assistant_mode=assistant_mode,
                intent_name=intent_result["intent_name"],
                escalation_reason=f"Intent category: {intent_result['intent_category']}",
                user_query=user_query
            )
            
            # Log interaction
            interaction_logger.log_interaction(
                assistant_mode=assistant_mode,
                user_query=user_query,
                session_id=st.session_state.get("conversation_id"),
                intent_name=intent_result["intent_name"],
                intent_category=intent_result["intent_category"],
                classification_reason=intent_result["classification_reason"],
                step_1_intent_completed=True,
                step_2_routing_decision=routing_decision["route"],
                step_6_escalation_triggered=True,
                outcome="escalated",
                escalation_reason=escalation_result["escalation_reason"]
            )
            
            return escalation_result
        
        # Check if intent needs retrieval (greeting, unknown, general_conversation don't need retrieval)
        intent_name = intent_result.get("intent_name", "")
        skip_retrieval = intent_name in ["greeting", "unknown", "general_conversation"]
        
        # Step 3: Retrieval (skip for conversational intents)
        if skip_retrieval:
            retrieval_result = {
                "retrieved_chunks": [],
                "citations": [],
                "success": True,
                "retrieved_chunks_count": 0
            }
        else:
            retrieval_result = await retrieval_service.retrieve(
                user_query=user_query,
                assistant_mode=assistant_mode
            )
            
            if not retrieval_result or not retrieval_result.get("retrieved_chunks"):
                # No results - escalate (but allow unknown/general_conversation to continue)
                if intent_name in ["unknown", "general_conversation"]:
                    # For unknown/general_conversation, continue without retrieval
                    retrieval_result = {
                        "retrieved_chunks": [],
                        "citations": [],
                        "success": True,
                        "retrieved_chunks_count": 0
                    }
                else:
                    # For other intents, escalate if no retrieval results
                    escalation_result = await escalation_handler.handle_escalation(
                        trigger_type="insufficient_evidence",
                        assistant_mode=assistant_mode,
                        escalation_reason="No retrieval results",
                        user_query=user_query
                    )
                    
                    interaction_logger.log_interaction(
                        assistant_mode=assistant_mode,
                        user_query=user_query,
                        session_id=st.session_state.get("conversation_id"),
                        intent_name=intent_result["intent_name"],
                        intent_category=intent_result["intent_category"],
                        classification_reason=intent_result["classification_reason"],
                        step_1_intent_completed=True,
                        step_2_routing_decision=routing_decision["route"],
                        step_3_retrieval_performed=True,
                        step_6_escalation_triggered=True,
                        outcome="escalated",
                        escalation_reason=escalation_result["escalation_reason"],
                        retrieved_chunks_count=0
                    )
                    
                    return escalation_result
        
        # Step 4: Response Generation (with conversation history)
        response_result = await response_generator.generate(
            user_query=user_query,
            retrieved_chunks=retrieval_result.get("retrieved_chunks", []),
            assistant_mode=assistant_mode,
            intent_name=intent_result["intent_name"],
            citations=retrieval_result.get("citations", []),
            conversation_history=conversation_history
        )
        
        if not response_result:
            # Generation failed - escalate
            escalation_result = await escalation_handler.handle_escalation(
                trigger_type="insufficient_evidence",
                assistant_mode=assistant_mode,
                escalation_reason="Response generation failed",
                user_query=user_query
            )
            
            interaction_logger.log_interaction(
                assistant_mode=assistant_mode,
                user_query=user_query,
                session_id=st.session_state.get("conversation_id"),
                intent_name=intent_result["intent_name"],
                intent_category=intent_result["intent_category"],
                classification_reason=intent_result["classification_reason"],
                step_1_intent_completed=True,
                step_2_routing_decision=routing_decision["route"],
                step_3_retrieval_performed=True,
                step_4_response_generated=False,
                step_6_escalation_triggered=True,
                outcome="escalated",
                escalation_reason=escalation_result["escalation_reason"],
                retrieved_chunks_count=len(retrieval_result.get("retrieved_chunks", [])) if retrieval_result else 0
            )
            
            return escalation_result
        
        # Step 5: Confidence Scoring (skip for greeting/unknown - they have deterministic responses)
        if skip_retrieval or intent_name in ["greeting", "unknown", "general_conversation"]:
            # For conversational intents, give high confidence (they're deterministic responses)
            confidence_result = {
                "confidence_score": 0.95,  # High confidence for deterministic responses
                "meets_threshold": True,
                "reason": "Conversational intent - deterministic response"
            }
        else:
            confidence_result = await confidence_scorer.score(
                response_text=response_result["response_text"],
                retrieved_chunks=retrieval_result.get("retrieved_chunks", []),
                user_query=user_query,
                assistant_mode=assistant_mode
            )
        
        if not confidence_result["meets_threshold"]:
            # Low confidence - escalate
            escalation_result = await escalation_handler.handle_escalation(
                trigger_type="low_confidence",
                assistant_mode=assistant_mode,
                confidence_score=confidence_result["confidence_score"],
                escalation_reason=f"Confidence {confidence_result['confidence_score']:.2f} below threshold {Config.CONFIDENCE_THRESHOLD}",
                user_query=user_query
            )
            
            interaction_logger.log_interaction(
                assistant_mode=assistant_mode,
                user_query=user_query,
                session_id=st.session_state.get("conversation_id"),
                intent_name=intent_result["intent_name"],
                intent_category=intent_result["intent_category"],
                classification_reason=intent_result["classification_reason"],
                step_1_intent_completed=True,
                step_2_routing_decision=routing_decision["route"],
                step_3_retrieval_performed=True,
                step_4_response_generated=True,
                step_5_confidence_score=confidence_result["confidence_score"],
                step_6_escalation_triggered=True,
                outcome="escalated",
                confidence_score=confidence_result["confidence_score"],
                escalation_reason=escalation_result["escalation_reason"],
                response_text=response_result["response_text"],
                citations=response_result.get("citations", []),
                retrieved_chunks_count=len(retrieval_result.get("retrieved_chunks", [])) if retrieval_result else 0
            )
            
            return escalation_result
        
        # Step 6: Success - log resolved interaction
        interaction_logger.log_interaction(
            assistant_mode=assistant_mode,
            user_query=user_query,
            session_id=st.session_state.get("conversation_id"),
            intent_name=intent_result["intent_name"],
            intent_category=intent_result["intent_category"],
            classification_reason=intent_result["classification_reason"],
            step_1_intent_completed=True,
            step_2_routing_decision=routing_decision["route"],
            step_3_retrieval_performed=True,
            step_4_response_generated=True,
            step_5_confidence_score=confidence_result["confidence_score"],
            step_6_escalation_triggered=False,
            outcome="resolved",
            confidence_score=confidence_result["confidence_score"],
            response_text=response_result["response_text"],
            citations=response_result.get("citations", []),
            retrieved_chunks_count=len(retrieval_result.get("retrieved_chunks", [])) if retrieval_result else 0,
            response_generation_time_ms=response_result.get("response_generation_time_ms")
        )
        
        # Return successful response
        return {
            "response_text": response_result["response_text"],
            "citations": response_result.get("citations", []),
            "confidence_score": confidence_result["confidence_score"],
            "has_synthetic_content": response_result.get("has_synthetic_content", False),
            "escalated": False
        }
    
    except Exception as e:
        logger.error("pipeline_error", error=str(e), exc_info=True)
        escalation_result = {
            "response_text": "I encountered an error processing your request. Please try again or contact support.",
            "escalated": True,
            "escalation_message": f"Pipeline error: {str(e)}"
        }
        
        # Log error
        interaction_logger.log_interaction(
            assistant_mode=assistant_mode,
            user_query=user_query,
            outcome="escalated",
            escalation_reason=f"Pipeline error: {str(e)}"
        )
        
        return escalation_result
