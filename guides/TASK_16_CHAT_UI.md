# Task 16: Chat Interface UI

## Overview
Implement Streamlit chat interface with mode selection, chat history management using OpenAI Conversations API, message input, and response display with citations, confidence scores, and escalation messages.

## Prerequisites
- Task 1 completed (project structure, config, logging)
- Task 10 completed (Retrieval service - for Conversations API understanding)
- Task 14 completed (Logging service)
- Task 15 completed (Authentication module)
- Virtual environment activated

## Deliverables

### 1. Chat Interface (ui/chat_interface.py)

Create `ui/chat_interface.py` with full chat interface functionality.

**Key Requirements**:
- Authentication check (via auth.py)
- Mode selection (Customer/Banker toggle)
- Chat history display (from OpenAI Conversations API)
- Message input
- Response display with citations, confidence score, escalation messages
- Loading indicators
- Integration with pipeline services

## Implementation

### Step 1: Chat Interface Structure

```python
# ui/chat_interface.py
import streamlit as st
import asyncio
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
from services.logger import Logger

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
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "assistant_mode" not in st.session_state:
        st.session_state.assistant_mode = "customer"
    
    # Page header
    st.title("💬 ContactIQ Chat")
    st.markdown("---")
    
    # Mode selection
    mode = st.radio(
        "Select Mode:",
        ["Customer", "Banker"],
        horizontal=True,
        index=0 if st.session_state.assistant_mode == "customer" else 1,
        key="mode_selector"
    )
    st.session_state.assistant_mode = mode.lower()
    
    st.markdown("---")
    
    # Chat history display
    display_chat_history()
    
    # Message input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Process message
        process_user_message(user_input, st.session_state.assistant_mode)
```

### Step 2: Chat History Display

```python
def display_chat_history():
    """
    Display chat history from session state.
    """
    if not st.session_state.chat_history:
        st.info("👋 Start a conversation by typing a message below.")
        return
    
    # Display each message in chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                # Display response text
                st.write(message["content"])
                
                # Display citations if present
                if message.get("citations"):
                    st.markdown("**Sources:**")
                    for citation in message["citations"]:
                        citation_text = f"[{citation['number']}] {citation['source']}"
                        if citation.get("url"):
                            st.markdown(f"- {citation_text}: {citation['url']}")
                        else:
                            st.markdown(f"- {citation_text}")
                
                # Display confidence score if present
                if message.get("confidence_score") is not None:
                    confidence = message["confidence_score"]
                    confidence_color = "🟢" if confidence >= 0.68 else "🟡" if confidence >= 0.5 else "🔴"
                    st.markdown(f"{confidence_color} **Confidence:** {confidence:.2%}")
                
                # Display escalation message if escalated
                if message.get("escalated"):
                    st.warning(f"⚠️ {message.get('escalation_message', 'Escalated to human support')}")
        
        elif message["role"] == "system":
            # System messages (errors, etc.)
            st.error(message["content"])
```

### Step 3: Message Processing

```python
def process_user_message(user_query: str, assistant_mode: str):
    """
    Process user message through the pipeline.
    
    Args:
        user_query: User's message
        assistant_mode: 'customer' or 'banker'
    """
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_query,
        "timestamp": st.session_state.get("timestamp", 0)
    })
    
    # Show loading indicator
    with st.spinner("Processing your message..."):
        # Run pipeline asynchronously
        result = asyncio.run(run_pipeline_async(user_query, assistant_mode))
    
    # Add assistant response to history
    if result:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result.get("response_text", ""),
            "citations": result.get("citations", []),
            "confidence_score": result.get("confidence_score"),
            "escalated": result.get("escalated", False),
            "escalation_message": result.get("escalation_message"),
            "timestamp": st.session_state.get("timestamp", 0)
        })
    else:
        st.session_state.chat_history.append({
            "role": "system",
            "content": "Sorry, I encountered an error processing your message. Please try again."
        })
    
    # Rerun to update display
    st.rerun()
```

### Step 4: Pipeline Execution

```python
async def run_pipeline_async(user_query: str, assistant_mode: str) -> Optional[Dict[str, Any]]:
    """
    Run the full pipeline asynchronously.
    
    Args:
        user_query: User's query
        assistant_mode: 'customer' or 'banker'
    
    Returns:
        Result dictionary with response or escalation
    """
    logger.info("pipeline_started", assistant_mode=assistant_mode, query_length=len(user_query))
    
    try:
        # Initialize services
        intent_classifier = IntentClassifier()
        router = Router()
        retrieval_service = RetrievalService()
        response_generator = ResponseGenerator()
        confidence_scorer = ConfidenceScorer()
        escalation_handler = EscalationHandler()
        logger_service = Logger()
        
        # Step 1: Intent Classification
        intent_result = await intent_classifier.classify_async(user_query, assistant_mode)
        if not intent_result:
            logger.error("intent_classification_failed")
            return {
                "response_text": "I'm having trouble understanding your request. Please try rephrasing or contact support.",
                "escalated": True,
                "escalation_message": "Intent classification failed"
            }
        
        # Step 2: Router
        routing_decision = router.route(
            intent_category=intent_result["intent_category"],
            intent_name=intent_result["intent_name"],
            assistant_mode=assistant_mode
        )
        
        # If escalate, skip to escalation handler
        if routing_decision["route"] == "escalate":
            escalation_result = await escalation_handler.handle_escalation_async(
                trigger_type="human_only",
                assistant_mode=assistant_mode,
                intent_name=intent_result["intent_name"],
                escalation_reason=f"Intent category: {intent_result['intent_category']}"
            )
            
            # Log interaction
            await logger_service.log_interaction_async(
                user_query=user_query,
                assistant_mode=assistant_mode,
                intent_name=intent_result["intent_name"],
                intent_category=intent_result["intent_category"],
                outcome="escalated",
                escalation_reason=escalation_result["escalation_reason"],
                trigger_type="human_only"
            )
            
            return escalation_result
        
        # Step 3: Retrieval
        retrieval_result = await retrieval_service.retrieve_async(
            user_query=user_query,
            assistant_mode=assistant_mode,
            intent_name=intent_result["intent_name"]
        )
        
        if not retrieval_result or not retrieval_result.get("retrieved_chunks"):
            # No results - escalate
            escalation_result = await escalation_handler.handle_escalation_async(
                trigger_type="insufficient_evidence",
                assistant_mode=assistant_mode,
                escalation_reason="No retrieval results"
            )
            
            await logger_service.log_interaction_async(
                user_query=user_query,
                assistant_mode=assistant_mode,
                intent_name=intent_result["intent_name"],
                outcome="escalated",
                escalation_reason=escalation_result["escalation_reason"],
                trigger_type="insufficient_evidence"
            )
            
            return escalation_result
        
        # Step 4: Response Generation
        response_result = await response_generator.generate_async(
            user_query=user_query,
            retrieved_chunks=retrieval_result["retrieved_chunks"],
            assistant_mode=assistant_mode,
            intent_name=intent_result["intent_name"]
        )
        
        if not response_result:
            # Generation failed - escalate
            escalation_result = await escalation_handler.handle_escalation_async(
                trigger_type="insufficient_evidence",
                assistant_mode=assistant_mode,
                escalation_reason="Response generation failed"
            )
            
            await logger_service.log_interaction_async(
                user_query=user_query,
                assistant_mode=assistant_mode,
                intent_name=intent_result["intent_name"],
                outcome="escalated",
                escalation_reason=escalation_result["escalation_reason"],
                trigger_type="insufficient_evidence"
            )
            
            return escalation_result
        
        # Step 5: Confidence Scoring
        confidence_result = await confidence_scorer.score_async(
            response_text=response_result["response_text"],
            retrieved_chunks=retrieval_result["retrieved_chunks"],
            user_query=user_query,
            assistant_mode=assistant_mode
        )
        
        if not confidence_result["meets_threshold"]:
            # Low confidence - escalate
            escalation_result = await escalation_handler.handle_escalation_async(
                trigger_type="low_confidence",
                assistant_mode=assistant_mode,
                confidence_score=confidence_result["confidence_score"],
                escalation_reason=f"Confidence {confidence_result['confidence_score']:.2f} below threshold"
            )
            
            await logger_service.log_interaction_async(
                user_query=user_query,
                assistant_mode=assistant_mode,
                intent_name=intent_result["intent_name"],
                outcome="escalated",
                escalation_reason=escalation_result["escalation_reason"],
                trigger_type="low_confidence",
                confidence_score=confidence_result["confidence_score"]
            )
            
            return escalation_result
        
        # Step 6: Success - log resolved interaction
        await logger_service.log_interaction_async(
            user_query=user_query,
            assistant_mode=assistant_mode,
            intent_name=intent_result["intent_name"],
            intent_category=intent_result["intent_category"],
            outcome="resolved",
            response_text=response_result["response_text"],
            citations=response_result["citations"],
            confidence_score=confidence_result["confidence_score"]
        )
        
        # Return successful response
        return {
            "response_text": response_result["response_text"],
            "citations": response_result["citations"],
            "confidence_score": confidence_result["confidence_score"],
            "has_synthetic_content": response_result.get("has_synthetic_content", False),
            "escalated": False
        }
    
    except Exception as e:
        logger.error("pipeline_error", error=str(e))
        return {
            "response_text": "I encountered an error processing your request. Please try again or contact support.",
            "escalated": True,
            "escalation_message": f"Pipeline error: {str(e)}"
        }
```

### Step 5: Conversations API Integration (Optional)

For session management with OpenAI Conversations API:

```python
def initialize_conversation(assistant_mode: str) -> Optional[str]:
    """
    Initialize a new conversation using OpenAI Conversations API.
    
    Args:
        assistant_mode: 'customer' or 'banker'
    
    Returns:
        Conversation ID or None on failure
    """
    # Note: OpenAI Conversations API implementation depends on actual API structure
    # This is a placeholder - adjust based on actual API
    
    try:
        # Create conversation thread
        # conversation = openai_client.conversations.create(...)
        # return conversation.id
        
        # For now, use session-based conversation ID
        if "conversation_id" not in st.session_state:
            import uuid
            st.session_state.conversation_id = str(uuid.uuid4())
        
        return st.session_state.conversation_id
    
    except Exception as e:
        logger.error("conversation_initialization_error", error=str(e))
        return None


def get_conversation_history(conversation_id: str) -> List[Dict[str, Any]]:
    """
    Get conversation history from OpenAI Conversations API.
    
    Args:
        conversation_id: Conversation ID
    
    Returns:
        List of message dictionaries
    """
    # Note: Adjust based on actual OpenAI Conversations API structure
    # For now, use session state
    return st.session_state.get("chat_history", [])
```

### Step 6: Complete Chat Interface

```python
# ui/chat_interface.py (complete file)
import streamlit as st
import asyncio
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
from services.logger import Logger

logger = get_logger(__name__)


def render_chat_interface():
    """Render the main chat interface."""
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
        if st.button("Clear Chat History", type="secondary"):
            st.session_state.chat_history = []
            st.session_state.conversation_id = None
            st.rerun()
        
        # Show conversation stats
        if st.session_state.chat_history:
            st.markdown("### Conversation Stats")
            st.metric("Messages", len(st.session_state.chat_history))
    
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
                # Response text
                st.write(message["content"])
                
                # Citations
                if message.get("citations"):
                    with st.expander("📚 Sources", expanded=False):
                        for citation in message["citations"]:
                            if citation.get("url"):
                                st.markdown(f"[{citation['number']}] {citation['source']} - {citation['url']}")
                            else:
                                st.markdown(f"[{citation['number']}] {citation['source']}")
                
                # Confidence score
                if message.get("confidence_score") is not None:
                    confidence = message["confidence_score"]
                    if confidence >= 0.68:
                        st.success(f"✅ Confidence: {confidence:.2%}")
                    elif confidence >= 0.5:
                        st.warning(f"⚠️ Confidence: {confidence:.2%}")
                    else:
                        st.error(f"❌ Confidence: {confidence:.2%}")
                
                # Escalation message
                if message.get("escalated"):
                    st.error(f"🚨 {message.get('escalation_message', 'Escalated to human support')}")
        
        elif message["role"] == "system":
            st.error(message["content"])


def process_user_message(user_query: str, assistant_mode: str):
    """Process user message through the pipeline."""
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_query
    })
    
    # Show loading indicator
    with st.spinner("🤔 Thinking..."):
        result = asyncio.run(run_pipeline_async(user_query, assistant_mode))
    
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


async def run_pipeline_async(user_query: str, assistant_mode: str) -> Optional[Dict[str, Any]]:
    """Run the full pipeline asynchronously."""
    # Implementation from Step 4
    # ... (see Step 4 for full implementation)
    pass
```

## UI Components

### Mode Selection
- Radio button or toggle for Customer/Banker mode
- Stored in `st.session_state.assistant_mode`
- Persists for session

### Chat History Display
- Uses `st.chat_message()` for user/assistant messages
- Displays citations in expandable section
- Shows confidence score with color coding
- Displays escalation messages prominently

### Message Input
- Uses `st.chat_input()` for message input
- Triggers pipeline execution on submit

### Loading Indicators
- `st.spinner()` during pipeline execution
- Clear feedback to user

## Success Criteria

- [ ] Authentication check integrated (via auth.py)
- [ ] Mode selection works (Customer/Banker toggle)
- [ ] Chat history displayed correctly
- [ ] Message input functional
- [ ] Response display includes:
  - [ ] Response text
  - [ ] Numbered citations [1], [2], etc.
  - [ ] Confidence score (visible to user)
  - [ ] Escalation messages
- [ ] Loading indicators shown during processing
- [ ] Pipeline integration works end-to-end
- [ ] Error handling displays user-friendly messages
- [ ] Session state managed correctly

## Testing

### Manual Testing

1. **Test Authentication**:
   - Verify password prompt appears
   - Verify access after correct password
   - Verify main interface only accessible after auth

2. **Test Mode Selection**:
   - Switch between Customer and Banker modes
   - Verify mode persists for session
   - Verify pipeline uses correct mode

3. **Test Chat Flow**:
   - Send a message
   - Verify response appears
   - Verify citations displayed
   - Verify confidence score shown
   - Verify chat history maintained

4. **Test Escalation**:
   - Send query that triggers escalation
   - Verify escalation message displayed
   - Verify escalation reason logged

5. **Test Error Handling**:
   - Simulate API failure
   - Verify user-friendly error message
   - Verify error logged

## Integration Points

- **Task 15 (Authentication)**: Uses `check_authentication()` from `ui/auth.py`
- **Task 8 (Intent Classifier)**: Uses for intent classification
- **Task 9 (Router)**: Uses for routing decisions
- **Task 10 (Retrieval)**: Uses for knowledge retrieval
- **Task 11 (Response Generator)**: Uses for response generation
- **Task 12 (Confidence Scorer)**: Uses for confidence scoring
- **Task 13 (Escalation Handler)**: Uses for escalation handling
- **Task 14 (Logging)**: Uses for logging interactions
- **Task 18 (Main App)**: Integrated into main application

## Notes

- **Conversations API**: Implementation depends on actual OpenAI Conversations API structure. Adjust based on API documentation.
- **Session State**: Uses Streamlit session_state for chat history (can be enhanced with Conversations API)
- **Async Pipeline**: Pipeline runs asynchronously but Streamlit needs `asyncio.run()` wrapper
- **Error Handling**: All errors should show user-friendly messages
- **Performance**: Consider adding caching for repeated queries

## Reference

- **DETAILED_PLAN.md** Section 9.2 (Chat Interface)
- **TASK_BREAKDOWN.md** Task 16
- **Task 15 Guide**: For authentication integration
- **Streamlit Chat Components**: https://docs.streamlit.io/library/api-reference/chat
