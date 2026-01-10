# Task 18: Main Application Integration

## Overview
Integrate all components into the main Streamlit application with authentication, async pipeline orchestration, error handling, timeout management, and page routing between Chat UI and Dashboard.

## Prerequisites
- All previous tasks completed (Tasks 1-17)
- All services implemented and tested
- Virtual environment activated

## Deliverables

### 1. Main Application (main.py)

Update `main.py` to integrate all components.

**Key Requirements**:
- Authentication integration (via auth.py)
- Async pipeline orchestration (all 7 steps)
- Integration of all services (async where applicable)
- Error handling across pipeline (with timeout handling)
- Streamlit page routing (Chat UI, Dashboard)
- Timeout handling throughout (30s default)
- Session management

## Implementation

### Step 1: Main Application Structure

```python
# main.py
import streamlit as st
import asyncio
import sys
from typing import Optional, Dict, Any
from config import Config
from ui.auth import check_authentication
from ui.chat_interface import render_chat_interface
from ui.dashboard import render_dashboard
from utils.logger import setup_logging, get_logger

# Setup structured logging
setup_logging()
logger = get_logger(__name__)

# Streamlit page configuration
st.set_page_config(
    page_title="ContactIQ",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """
    Main application entry point.
    
    Handles:
    - Authentication check
    - Configuration validation
    - Page routing
    - Error handling
    """
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
    
    # Sidebar navigation
    with st.sidebar:
        st.title("ContactIQ")
        st.markdown("---")
        
        page = st.radio(
            "Navigate",
            ["💬 Chat", "📊 Dashboard"],
            key="page_selector"
        )
        
        st.markdown("---")
        
        # System status
        st.markdown("### System Status")
        if Config.validate():
            st.success("✅ System Ready")
        else:
            st.error("❌ Configuration Error")
        
        # Logout button
        if st.button("🚪 Logout", type="secondary"):
            if "authenticated" in st.session_state:
                del st.session_state.authenticated
            st.rerun()
    
    # Route to selected page
    if page == "💬 Chat":
        render_chat_interface()
    elif page == "📊 Dashboard":
        render_dashboard()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("fatal_error", error=str(e), exc_info=True)
        st.error(f"❌ A fatal error occurred: {str(e)}")
        st.write("Please refresh the page or contact support if the issue persists.")
        st.stop()
```

### Step 2: Pipeline Orchestration Module (Optional)

You can create a separate pipeline orchestration module for better organization:

```python
# services/pipeline.py
import asyncio
import time
from typing import Optional, Dict, Any
from utils.logger import get_logger
from config import Config

# Import all services
from services.intent_classifier import IntentClassifier
from services.router import Router
from services.retrieval_service import RetrievalService
from services.response_generator import ResponseGenerator
from services.confidence_scorer import ConfidenceScorer
from services.escalation_handler import EscalationHandler
from services.logger import Logger

logger = get_logger(__name__)


class PipelineOrchestrator:
    """Orchestrates the full pipeline execution."""
    
    def __init__(self):
        """Initialize pipeline orchestrator with all services."""
        self.intent_classifier = IntentClassifier()
        self.router = Router()
        self.retrieval_service = RetrievalService()
        self.response_generator = ResponseGenerator()
        self.confidence_scorer = ConfidenceScorer()
        self.escalation_handler = EscalationHandler()
        self.logger_service = Logger()
    
    async def execute_pipeline_async(
        self,
        user_query: str,
        assistant_mode: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute the full pipeline asynchronously with timeout handling.
        
        Args:
            user_query: User's query
            assistant_mode: 'customer' or 'banker'
            session_id: Optional session ID for conversation tracking
        
        Returns:
            Result dictionary with response or escalation
        """
        pipeline_start_time = time.time()
        logger.info(
            "pipeline_execution_started",
            assistant_mode=assistant_mode,
            query_length=len(user_query),
            session_id=session_id
        )
        
        try:
            # Execute pipeline with overall timeout
            result = await asyncio.wait_for(
                self._execute_pipeline_steps(user_query, assistant_mode, session_id),
                timeout=Config.API_TIMEOUT * 2  # Allow 2x timeout for full pipeline
            )
            
            pipeline_time = (time.time() - pipeline_start_time) * 1000
            logger.info(
                "pipeline_execution_completed",
                assistant_mode=assistant_mode,
                outcome=result.get("outcome", "unknown"),
                escalated=result.get("escalated", False),
                processing_time_ms=pipeline_time
            )
            
            return result
        
        except asyncio.TimeoutError:
            pipeline_time = (time.time() - pipeline_start_time) * 1000
            logger.error(
                "pipeline_execution_timeout",
                timeout=Config.API_TIMEOUT * 2,
                processing_time_ms=pipeline_time
            )
            
            # Escalate on timeout
            escalation_result = await self.escalation_handler.handle_escalation_async(
                trigger_type="insufficient_evidence",
                assistant_mode=assistant_mode,
                escalation_reason="Pipeline execution timeout"
            )
            
            return escalation_result
        
        except Exception as e:
            pipeline_time = (time.time() - pipeline_start_time) * 1000
            logger.error(
                "pipeline_execution_error",
                error=str(e),
                processing_time_ms=pipeline_time,
                exc_info=True
            )
            
            # Escalate on error
            escalation_result = await self.escalation_handler.handle_escalation_async(
                trigger_type="insufficient_evidence",
                assistant_mode=assistant_mode,
                escalation_reason=f"Pipeline error: {str(e)}"
            )
            
            return escalation_result
    
    async def _execute_pipeline_steps(
        self,
        user_query: str,
        assistant_mode: str,
        session_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Execute all pipeline steps sequentially.
        
        Args:
            user_query: User's query
            assistant_mode: 'customer' or 'banker'
            session_id: Optional session ID
        
        Returns:
            Result dictionary
        """
        # Step 1: Intent Classification
        intent_result = await self.intent_classifier.classify_async(user_query, assistant_mode)
        if not intent_result:
            logger.error("intent_classification_failed")
            escalation_result = await self.escalation_handler.handle_escalation_async(
                trigger_type="insufficient_evidence",
                assistant_mode=assistant_mode,
                escalation_reason="Intent classification failed"
            )
            
            await self.logger_service.log_interaction_async(
                user_query=user_query,
                assistant_mode=assistant_mode,
                outcome="escalated",
                escalation_reason=escalation_result["escalation_reason"],
                trigger_type="insufficient_evidence",
                session_id=session_id
            )
            
            return escalation_result
        
        # Step 2: Router
        routing_decision = self.router.route(
            intent_category=intent_result["intent_category"],
            intent_name=intent_result["intent_name"],
            assistant_mode=assistant_mode
        )
        
        # If escalate, skip to escalation handler
        if routing_decision["route"] == "escalate":
            escalation_result = await self.escalation_handler.handle_escalation_async(
                trigger_type="human_only",
                assistant_mode=assistant_mode,
                intent_name=intent_result["intent_name"],
                escalation_reason=f"Intent category: {intent_result['intent_category']}"
            )
            
            await self.logger_service.log_interaction_async(
                user_query=user_query,
                assistant_mode=assistant_mode,
                intent_name=intent_result["intent_name"],
                intent_category=intent_result["intent_category"],
                outcome="escalated",
                escalation_reason=escalation_result["escalation_reason"],
                trigger_type="human_only",
                session_id=session_id
            )
            
            return {
                **escalation_result,
                "outcome": "escalated"
            }
        
        # Step 3: Retrieval
        retrieval_result = await self.retrieval_service.retrieve_async(
            user_query=user_query,
            assistant_mode=assistant_mode,
            intent_name=intent_result["intent_name"]
        )
        
        if not retrieval_result or not retrieval_result.get("retrieved_chunks"):
            escalation_result = await self.escalation_handler.handle_escalation_async(
                trigger_type="insufficient_evidence",
                assistant_mode=assistant_mode,
                escalation_reason="No retrieval results"
            )
            
            await self.logger_service.log_interaction_async(
                user_query=user_query,
                assistant_mode=assistant_mode,
                intent_name=intent_result["intent_name"],
                outcome="escalated",
                escalation_reason=escalation_result["escalation_reason"],
                trigger_type="insufficient_evidence",
                session_id=session_id
            )
            
            return {
                **escalation_result,
                "outcome": "escalated"
            }
        
        # Step 4: Response Generation
        response_result = await self.response_generator.generate_async(
            user_query=user_query,
            retrieved_chunks=retrieval_result["retrieved_chunks"],
            assistant_mode=assistant_mode,
            intent_name=intent_result["intent_name"]
        )
        
        if not response_result:
            escalation_result = await self.escalation_handler.handle_escalation_async(
                trigger_type="insufficient_evidence",
                assistant_mode=assistant_mode,
                escalation_reason="Response generation failed"
            )
            
            await self.logger_service.log_interaction_async(
                user_query=user_query,
                assistant_mode=assistant_mode,
                intent_name=intent_result["intent_name"],
                outcome="escalated",
                escalation_reason=escalation_result["escalation_reason"],
                trigger_type="insufficient_evidence",
                session_id=session_id
            )
            
            return {
                **escalation_result,
                "outcome": "escalated"
            }
        
        # Step 5: Confidence Scoring
        confidence_result = await self.confidence_scorer.score_async(
            response_text=response_result["response_text"],
            retrieved_chunks=retrieval_result["retrieved_chunks"],
            user_query=user_query,
            assistant_mode=assistant_mode
        )
        
        if not confidence_result["meets_threshold"]:
            escalation_result = await self.escalation_handler.handle_escalation_async(
                trigger_type="low_confidence",
                assistant_mode=assistant_mode,
                confidence_score=confidence_result["confidence_score"],
                escalation_reason=f"Confidence {confidence_result['confidence_score']:.2f} below threshold"
            )
            
            await self.logger_service.log_interaction_async(
                user_query=user_query,
                assistant_mode=assistant_mode,
                intent_name=intent_result["intent_name"],
                intent_category=intent_result["intent_category"],
                outcome="escalated",
                escalation_reason=escalation_result["escalation_reason"],
                trigger_type="low_confidence",
                confidence_score=confidence_result["confidence_score"],
                session_id=session_id
            )
            
            return {
                **escalation_result,
                "outcome": "escalated"
            }
        
        # Step 6: Success - Log resolved interaction
        await self.logger_service.log_interaction_async(
            user_query=user_query,
            assistant_mode=assistant_mode,
            intent_name=intent_result["intent_name"],
            intent_category=intent_result["intent_category"],
            outcome="resolved",
            response_text=response_result["response_text"],
            citations=response_result["citations"],
            confidence_score=confidence_result["confidence_score"],
            retrieved_chunks_count=len(retrieval_result["retrieved_chunks"]),
            session_id=session_id
        )
        
        # Return successful response
        return {
            "response_text": response_result["response_text"],
            "citations": response_result["citations"],
            "confidence_score": confidence_result["confidence_score"],
            "has_synthetic_content": response_result.get("has_synthetic_content", False),
            "escalated": False,
            "outcome": "resolved"
        }
```

### Step 3: Update Chat Interface to Use Pipeline Orchestrator

```python
# In ui/chat_interface.py, update run_pipeline_async:

from services.pipeline import PipelineOrchestrator

async def run_pipeline_async(user_query: str, assistant_mode: str) -> Optional[Dict[str, Any]]:
    """
    Run the full pipeline asynchronously using orchestrator.
    
    Args:
        user_query: User's query
        assistant_mode: 'customer' or 'banker'
    
    Returns:
        Result dictionary
    """
    orchestrator = PipelineOrchestrator()
    
    # Get or create session ID
    session_id = st.session_state.get("conversation_id")
    
    result = await orchestrator.execute_pipeline_async(
        user_query=user_query,
        assistant_mode=assistant_mode,
        session_id=session_id
    )
    
    return result
```

### Step 4: Complete Main Application

```python
# main.py (complete file)
import streamlit as st
import sys
from config import Config
from ui.auth import check_authentication
from ui.chat_interface import render_chat_interface
from ui.dashboard import render_dashboard
from utils.logger import setup_logging, get_logger

# Setup structured logging
setup_logging()
logger = get_logger(__name__)

# Streamlit page configuration
st.set_page_config(
    page_title="ContactIQ",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """
    Main application entry point.
    
    Handles:
    - Authentication check
    - Configuration validation
    - Page routing
    - Error handling
    """
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
    
    # Sidebar navigation
    with st.sidebar:
        st.title("💬 ContactIQ")
        st.markdown("---")
        
        page = st.radio(
            "Navigate",
            ["💬 Chat", "📊 Dashboard"],
            key="page_selector"
        )
        
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
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            if "authenticated" in st.session_state:
                del st.session_state.authenticated
                logger.info("user_logged_out")
            st.rerun()
    
    # Route to selected page
    try:
        if page == "💬 Chat":
            render_chat_interface()
        elif page == "📊 Dashboard":
            render_dashboard()
    except Exception as e:
        logger.error("page_render_error", page=page, error=str(e), exc_info=True)
        st.error(f"❌ Error loading {page}: {str(e)}")
        st.write("Please try refreshing the page or contact support if the issue persists.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("fatal_error", error=str(e), exc_info=True)
        st.error(f"❌ A fatal error occurred: {str(e)}")
        st.write("Please refresh the page or contact support if the issue persists.")
        st.stop()
```

## Error Handling Strategy

### Global Error Handling

```python
# Add to main.py
import traceback

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
```

### Timeout Handling

All async operations should use `asyncio.wait_for()` with `Config.API_TIMEOUT`:

```python
# Example timeout handling
try:
    result = await asyncio.wait_for(
        service.method_async(...),
        timeout=Config.API_TIMEOUT
    )
except asyncio.TimeoutError:
    logger.error("operation_timeout", service="service_name", timeout=Config.API_TIMEOUT)
    # Handle timeout (escalate or retry)
```

## Success Criteria

- [ ] Authentication required before accessing any features
- [ ] Full pipeline executes end-to-end (async)
- [ ] All 7 steps integrated correctly with async support
- [ ] Error handling works at each step (including timeouts)
- [ ] Timeout handling (30s) implemented throughout
- [ ] User can switch between Chat and Dashboard
- [ ] Session management works
- [ ] All interactions logged (async, non-blocking)
- [ ] Configuration validation on startup
- [ ] Global error handling works
- [ ] System status displayed in sidebar

## Testing

### End-to-End Testing

1. **Test Authentication Flow**:
   - Start application
   - Verify password prompt
   - Enter correct password
   - Verify access granted
   - Test logout

2. **Test Chat Flow**:
   - Navigate to Chat
   - Send a message
   - Verify full pipeline executes
   - Verify response displayed
   - Verify citations shown
   - Verify confidence score shown

3. **Test Dashboard Flow**:
   - Navigate to Dashboard
   - Verify metrics displayed
   - Test filters
   - Verify charts render

4. **Test Error Handling**:
   - Simulate API failure
   - Verify user-friendly error message
   - Verify error logged

5. **Test Timeout Handling**:
   - Simulate timeout
   - Verify timeout handled gracefully
   - Verify escalation on timeout

## Integration Checklist

- [ ] Authentication module integrated (`ui/auth.py`)
- [ ] Chat interface integrated (`ui/chat_interface.py`)
- [ ] Dashboard integrated (`ui/dashboard.py`)
- [ ] All pipeline services imported and initialized
- [ ] Pipeline orchestrator created (optional but recommended)
- [ ] Error handling at each step
- [ ] Timeout handling throughout
- [ ] Logging integrated at each step
- [ ] Configuration validation on startup
- [ ] Page routing works (Chat ↔ Dashboard)
- [ ] Session state managed correctly

## Notes

- **Pipeline Orchestrator**: Optional but recommended for better organization
- **Async Execution**: All async operations use `asyncio.wait_for()` with timeout
- **Error Recovery**: Errors at any step trigger escalation
- **Logging**: All operations logged with structured logging
- **Session Management**: Uses Streamlit session_state (can be enhanced with Conversations API)

## Reference

- **DETAILED_PLAN.md** Section 7 (Linear Pipeline Implementation)
- **TASK_BREAKDOWN.md** Task 18
- **Task 15 Guide**: For authentication integration
- **Task 16 Guide**: For chat interface integration
- **Task 17 Guide**: For dashboard integration
- **Streamlit Multi-Page Apps**: https://docs.streamlit.io/library/api-reference/utilities/st.set_page_config
