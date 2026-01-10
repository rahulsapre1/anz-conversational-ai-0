# Task 14: Logging Service

## Overview
Implement logging service to log all interactions to Supabase with complete pipeline step tracking.

## Prerequisites
- Task 2 completed (Supabase database and client)

## Deliverables

### services/logger.py

```python
from typing import Optional, Dict, Any, List
from database.supabase_client import get_db_client
from utils.validators import validate_confidence_score
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class InteractionLogger:
    """Log interactions to Supabase."""
    
    def __init__(self):
        self.db_client = get_db_client()
        self.start_time: Optional[float] = None
    
    def start_timer(self):
        """Start processing timer."""
        self.start_time = time.time()
    
    def log_interaction(
        self,
        assistant_mode: str,
        user_query: str,
        session_id: Optional[str] = None,
        intent_name: Optional[str] = None,
        intent_category: Optional[str] = None,
        classification_reason: Optional[str] = None,
        step_1_intent_completed: bool = False,
        step_2_routing_decision: Optional[str] = None,
        step_3_retrieval_performed: bool = False,
        step_4_response_generated: bool = False,
        step_5_confidence_score: Optional[float] = None,
        step_6_escalation_triggered: bool = False,
        outcome: str = "resolved",
        confidence_score: Optional[float] = None,
        escalation_reason: Optional[str] = None,
        response_text: Optional[str] = None,
        citations: Optional[List[Dict[str, Any]]] = None,
        retrieved_chunks_count: Optional[int] = None
    ) -> Optional[str]:
        """
        Log interaction to Supabase.
        
        Returns:
            Interaction ID if successful, None otherwise
        """
        # Calculate processing time
        processing_time_ms = None
        if self.start_time:
            processing_time_ms = int((time.time() - self.start_time) * 1000)
        
        # Validate confidence score
        if confidence_score is not None and not validate_confidence_score(confidence_score):
            logger.warning(f"Invalid confidence score: {confidence_score}")
            confidence_score = None
        
        # Prepare interaction data
        interaction_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "assistant_mode": assistant_mode,
            "session_id": session_id,
            "user_query": user_query,
            "intent_name": intent_name,
            "intent_category": intent_category,
            "classification_reason": classification_reason,
            "step_1_intent_completed": step_1_intent_completed,
            "step_2_routing_decision": step_2_routing_decision,
            "step_3_retrieval_performed": step_3_retrieval_performed,
            "step_4_response_generated": step_4_response_generated,
            "step_5_confidence_score": step_5_confidence_score,
            "step_6_escalation_triggered": step_6_escalation_triggered,
            "outcome": outcome,
            "confidence_score": confidence_score,
            "escalation_reason": escalation_reason,
            "response_text": response_text,
            "citations": citations if citations else None,
            "retrieved_chunks_count": retrieved_chunks_count,
            "processing_time_ms": processing_time_ms
        }
        
        # Insert interaction
        interaction_id = self.db_client.insert_interaction(interaction_data)
        
        if interaction_id:
            logger.info(f"Interaction logged: {interaction_id}")
            
            # If escalated, log escalation separately
            if outcome == "escalated" and escalation_reason:
                self.log_escalation(
                    interaction_id=interaction_id,
                    trigger_type=self._extract_trigger_type(escalation_reason),
                    escalation_reason=escalation_reason
                )
        else:
            logger.error("Failed to log interaction")
        
        return interaction_id
    
    def log_escalation(
        self,
        interaction_id: str,
        trigger_type: str,
        escalation_reason: str
    ) -> Optional[str]:
        """
        Log escalation separately for analytics.
        
        Returns:
            Escalation ID if successful, None otherwise
        """
        escalation_data = {
            "interaction_id": interaction_id,
            "trigger_type": trigger_type,
            "escalation_reason": escalation_reason
        }
        
        escalation_id = self.db_client.insert_escalation(escalation_data)
        
        if escalation_id:
            logger.info(f"Escalation logged: {escalation_id}")
        else:
            logger.error("Failed to log escalation")
        
        return escalation_id
    
    def _extract_trigger_type(self, escalation_reason: str) -> str:
        """Extract trigger type from escalation reason."""
        reason_lower = escalation_reason.lower()
        
        trigger_mapping = {
            "human_only": "human_only",
            "confidence": "low_confidence",
            "insufficient": "insufficient_evidence",
            "conflicting": "conflicting_evidence",
            "account": "account_specific",
            "security": "security_fraud",
            "fraud": "security_fraud",
            "financial advice": "financial_advice",
            "advice": "financial_advice",
            "legal": "legal_hardship",
            "hardship": "legal_hardship",
            "emotional": "emotional_distress",
            "distress": "emotional_distress",
            "urgent": "emotional_distress",
            "repeated": "repeated_misunderstanding",
            "misunderstanding": "repeated_misunderstanding",
            "human": "explicit_human_request",
            "agent": "explicit_human_request"
        }
        
        for keyword, trigger in trigger_mapping.items():
            if keyword in reason_lower:
                return trigger
        
        return "unknown"

# Singleton instance
_logger: Optional[InteractionLogger] = None

def get_logger() -> InteractionLogger:
    """Get singleton logger instance."""
    global _logger
    if _logger is None:
        _logger = InteractionLogger()
    return _logger
```

## Usage Example

```python
from services.logger import get_logger

logger = get_logger()
logger.start_timer()

# Log interaction
interaction_id = logger.log_interaction(
    assistant_mode="customer",
    user_query="What are the fees for my account?",
    session_id="thread_xyz",
    intent_name="fee_inquiry",
    intent_category="automatable",
    classification_reason="User asking about standard fees",
    step_1_intent_completed=True,
    step_2_routing_decision="continue",
    step_3_retrieval_performed=True,
    step_4_response_generated=True,
    step_5_confidence_score=0.85,
    step_6_escalation_triggered=False,
    outcome="resolved",
    confidence_score=0.85,
    response_text="Based on ANZ's fee schedule...",
    citations=[{"number": 1, "source": "ANZ Fee Schedule", "url": "https://..."}],
    retrieved_chunks_count=3
)
```

## Validation Checklist

- [ ] Logs all interactions with complete fields
- [ ] Logs each pipeline step completion
- [ ] Logs escalations separately
- [ ] Handles database failures gracefully
- [ ] Calculates processing time correctly
- [ ] Validates confidence scores
- [ ] Extracts trigger types from escalation reasons

## Integration Points

- **All Pipeline Steps**: Will use logger to log step completion
- **Task 16**: Dashboard will read from interactions table
- **Task 15**: Chat UI will log interactions

## Notes

- Logs every step in the pipeline for debugging
- Processing time calculated automatically
- Escalations logged separately for analytics
- All fields from schema populated

## Success Criteria

✅ Logs all interactions to Supabase
✅ Logs all pipeline steps
✅ Logs escalations separately
✅ Handles errors gracefully
✅ All required fields populated
