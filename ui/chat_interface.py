"""
Chat Interface UI for ContactIQ.

Implements Streamlit chat interface with mode selection, chat history,
message input, and response display with citations, confidence scores, and escalation messages.
"""
import streamlit as st
import asyncio
import time
from typing import Optional, Dict, Any, List
from ui.auth import check_authentication
from utils.logger import get_logger
from config import Config

# Import pipeline services
from services.intent_classifier import IntentClassifier
from services.router import Router
from services.retrieval_service import RetrievalService
from services.response_generator import ResponseGenerator
from services.confidence_scorer import ConfidenceScorer
from services.escalation_handler import EscalationHandler
from services.logger import get_interaction_logger

logger = get_logger(__name__)


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
    
    # Page header
    st.title("💬 ContactIQ Chat")
    st.markdown("---")
    
    # Sidebar for mode selection and controls
    with st.sidebar:
        st.header("Settings")
        
        # Mode selection
        mode = st.radio(
            "Select Mode:",
            ["Customer", "Banker"],
            index=0 if st.session_state.assistant_mode == "customer" else 1,
            key="mode_selector"
        )
        st.session_state.assistant_mode = mode.lower()
        
        st.markdown("---")
        
        # Clear chat button
        if st.button("Clear Chat History", type="secondary", help="Clear all messages in the current chat session"):
            st.session_state.chat_history = []
            st.session_state.conversation_id = None
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


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "assistant_mode" not in st.session_state:
        st.session_state.assistant_mode = "customer"


def display_chat_history():
    """Display chat history from session state."""
    if not st.session_state.chat_history:
        st.info("👋 Start a conversation by typing a message below.")
        return
    
    # Display each message
    for i, message in enumerate(st.session_state.chat_history):
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                # Check if this is an escalated message
                if message.get("escalated"):
                    # For escalated messages, show escalation message (which is already in content)
                    st.info(f"🚨 {message.get('content', message.get('escalation_message', 'Escalated to human support'))}")
                else:
                    # Response text (non-escalated)
                    st.write(message["content"])
                    
                    # Citations (only for non-escalated messages)
                    if message.get("citations"):
                        with st.expander("📚 Sources (Click to view citations)", expanded=False):
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
    
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_query
    })
    
    # Show loading indicator
    with st.spinner("🤔 Thinking..."):
        result = asyncio.run(run_pipeline_async(user_query, assistant_mode, conversation_history))
    
    # Add response to history
    if result:
        if result.get("escalated"):
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": result.get("escalation_message", "Escalated to human support"),
                "escalated": True,
                "escalation_message": result.get("escalation_message"),
                "trigger_type": result.get("trigger_type")
            })
        else:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": result.get("response_text", ""),
                "citations": result.get("citations", []),
                "confidence_score": result.get("confidence_score"),
                "escalated": False
            })
    else:
        st.session_state.chat_history.append({
            "role": "system",
            "content": "Sorry, I encountered an error. Please try again."
        })
    
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
            retrieved_chunks_count=len(retrieval_result.get("retrieved_chunks", [])) if retrieval_result else 0
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
