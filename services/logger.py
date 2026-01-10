"""
Logging service for interaction and API call tracking.

Implements async, non-blocking logging to Supabase with retry queue.
"""
import asyncio
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
from database.supabase_client import get_db_client
from utils.validators import validate_confidence_score
from utils.logger import get_logger
from config import Config

logger = get_logger(__name__)


class InteractionLogger:
    """Log interactions to Supabase with async, non-blocking operations."""
    
    def __init__(self):
        """Initialize logger with retry queue."""
        self.db_client = get_db_client()
        self.start_time: Optional[float] = None
        self.retry_queue: Optional[asyncio.Queue] = None
        self.retry_task: Optional[asyncio.Task] = None
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        self.log_timeout = Config.API_TIMEOUT  # 30 seconds default
        self._retry_worker_started = False
    
    def _ensure_retry_queue(self):
        """Ensure retry queue and worker are initialized."""
        if self.retry_queue is None:
            try:
                loop = asyncio.get_event_loop()
                self.retry_queue = asyncio.Queue()
                if loop.is_running() and not self._retry_worker_started:
                    self.retry_task = asyncio.create_task(self._retry_worker())
                    self._retry_worker_started = True
            except RuntimeError:
                # No event loop, queue will be created when event loop is available
                # For now, create queue (it can exist without event loop)
                self.retry_queue = asyncio.Queue()
    
    async def _retry_worker(self):
        """Background worker to retry failed log operations."""
        logger.info("retry_worker_started")
        if self.retry_queue is None:
            self.retry_queue = asyncio.Queue()
        
        while True:
            try:
                # Wait for item in queue (with timeout to allow graceful shutdown)
                try:
                    item = await asyncio.wait_for(
                        self.retry_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                log_type, data, attempt = item
                
                if attempt >= self.max_retries:
                    logger.error(
                        "log_retry_exhausted",
                        log_type=log_type,
                        attempts=attempt
                    )
                    continue
                
                # Wait before retry (exponential backoff)
                wait_time = self.retry_delay * (2 ** attempt)
                await asyncio.sleep(wait_time)
                
                # Retry the operation
                success = False
                if log_type == "interaction":
                    success = await self._insert_interaction_async(data)
                elif log_type == "escalation":
                    success = await self._insert_escalation_async(data)
                elif log_type == "api_call":
                    # API calls are logged separately, skip retry for now
                    success = True
                
                if not success:
                    # Re-queue for another retry
                    await self.retry_queue.put((log_type, data, attempt + 1))
                else:
                    logger.info(
                        "log_retry_success",
                        log_type=log_type,
                        attempt=attempt + 1
                    )
                    
            except Exception as e:
                logger.error(
                    "retry_worker_error",
                    error=str(e),
                    exc_info=True
                )
                await asyncio.sleep(1)
    
    def start_timer(self):
        """Start processing timer."""
        self.start_time = time.time()
        logger.debug("processing_timer_started")
    
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
        retrieved_chunks_count: Optional[int] = None,
        response_generation_time_ms: Optional[int] = None
    ) -> Optional[str]:
        """
        Log interaction to Supabase (async, non-blocking).
        
        Returns:
            Interaction ID if successful, None otherwise (logging continues in background)
        """
        # Calculate processing time
        processing_time_ms = None
        if self.start_time:
            processing_time_ms = int((time.time() - self.start_time) * 1000)
        
        # Validate confidence score
        if confidence_score is not None and not validate_confidence_score(confidence_score):
            logger.warning(
                "invalid_confidence_score",
                score=confidence_score
            )
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
            "processing_time_ms": processing_time_ms,
            "response_generation_time_ms": response_generation_time_ms
        }
        
        # Ensure retry queue is initialized
        self._ensure_retry_queue()
        
        # Log interaction asynchronously (non-blocking)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Event loop is running, create task
                asyncio.create_task(
                    self._log_interaction_async(interaction_data, outcome, escalation_reason)
                )
                # Start retry worker if not started
                if not self._retry_worker_started:
                    self.retry_task = asyncio.create_task(self._retry_worker())
                    self._retry_worker_started = True
            else:
                # No event loop, run in new thread
                asyncio.run(
                    self._log_interaction_async(interaction_data, outcome, escalation_reason)
                )
        except RuntimeError:
            # No event loop available, create new one
            asyncio.run(
                self._log_interaction_async(interaction_data, outcome, escalation_reason)
            )
        
        # Return None immediately (non-blocking)
        # The actual interaction_id will be logged in the background
        logger.info(
            "interaction_logging_started",
            assistant_mode=assistant_mode,
            intent_name=intent_name,
            outcome=outcome
        )
        return None
    
    async def _log_interaction_async(
        self,
        interaction_data: Dict[str, Any],
        outcome: str,
        escalation_reason: Optional[str]
    ) -> Optional[str]:
        """Async helper to log interaction with timeout."""
        try:
            interaction_id = await asyncio.wait_for(
                self._insert_interaction_async(interaction_data),
                timeout=self.log_timeout
            )
            
            if interaction_id:
                logger.info(
                    "interaction_logged",
                    interaction_id=interaction_id,
                    outcome=outcome
                )
                
                # If escalated, log escalation separately
                if outcome == "escalated" and escalation_reason:
                    await self.log_escalation_async(
                        interaction_id=interaction_id,
                        trigger_type=self._extract_trigger_type(escalation_reason),
                        escalation_reason=escalation_reason
                    )
            else:
                # Queue for retry
                if self.retry_queue is not None:
                    await self.retry_queue.put(("interaction", interaction_data, 0))
                    logger.warning("interaction_logging_failed_queued_for_retry")
                else:
                    logger.error("interaction_logging_failed_no_retry_queue")
            
            return interaction_id
            
        except asyncio.TimeoutError:
            logger.error(
                "interaction_logging_timeout",
                timeout=self.log_timeout
            )
            # Queue for retry
            if self.retry_queue is not None:
                await self.retry_queue.put(("interaction", interaction_data, 0))
            return None
        except Exception as e:
            logger.error(
                "interaction_logging_error",
                error=str(e),
                exc_info=True
            )
            # Queue for retry
            if self.retry_queue is not None:
                await self.retry_queue.put(("interaction", interaction_data, 0))
            return None
    
    async def _insert_interaction_async(self, interaction_data: Dict[str, Any]) -> Optional[str]:
        """Insert interaction using thread pool (Supabase client is sync)."""
        try:
            loop = asyncio.get_event_loop()
            interaction_id = await loop.run_in_executor(
                None,
                self.db_client.insert_interaction,
                interaction_data
            )
            return interaction_id
        except Exception as e:
            logger.error(
                "insert_interaction_error",
                error=str(e),
                exc_info=True
            )
            return None
    
    def log_escalation(
        self,
        interaction_id: str,
        trigger_type: str,
        escalation_reason: str
    ) -> Optional[str]:
        """
        Log escalation separately for analytics (async, non-blocking).
        
        Returns:
            Escalation ID if successful, None otherwise
        """
        # Ensure retry queue is initialized
        self._ensure_retry_queue()
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(
                    self.log_escalation_async(interaction_id, trigger_type, escalation_reason)
                )
                # Start retry worker if not started
                if not self._retry_worker_started:
                    self.retry_task = asyncio.create_task(self._retry_worker())
                    self._retry_worker_started = True
            else:
                asyncio.run(
                    self.log_escalation_async(interaction_id, trigger_type, escalation_reason)
                )
        except RuntimeError:
            asyncio.run(
                self.log_escalation_async(interaction_id, trigger_type, escalation_reason)
            )
        
        logger.info(
            "escalation_logging_started",
            interaction_id=interaction_id,
            trigger_type=trigger_type
        )
        return None
    
    async def log_escalation_async(
        self,
        interaction_id: str,
        trigger_type: str,
        escalation_reason: str
    ) -> Optional[str]:
        """Async helper to log escalation with timeout."""
        escalation_data = {
            "interaction_id": interaction_id,
            "trigger_type": trigger_type,
            "escalation_reason": escalation_reason
        }
        
        try:
            escalation_id = await asyncio.wait_for(
                self._insert_escalation_async(escalation_data),
                timeout=self.log_timeout
            )
            
            if escalation_id:
                logger.info(
                    "escalation_logged",
                    escalation_id=escalation_id,
                    trigger_type=trigger_type
                )
            else:
                # Queue for retry
                if self.retry_queue is not None:
                    await self.retry_queue.put(("escalation", escalation_data, 0))
                    logger.warning("escalation_logging_failed_queued_for_retry")
                else:
                    logger.error("escalation_logging_failed_no_retry_queue")
            
            return escalation_id
            
        except asyncio.TimeoutError:
            logger.error(
                "escalation_logging_timeout",
                timeout=self.log_timeout
            )
            if self.retry_queue is not None:
                await self.retry_queue.put(("escalation", escalation_data, 0))
            return None
        except Exception as e:
            logger.error(
                "escalation_logging_error",
                error=str(e),
                exc_info=True
            )
            if self.retry_queue is not None:
                await self.retry_queue.put(("escalation", escalation_data, 0))
            return None
    
    async def _insert_escalation_async(self, escalation_data: Dict[str, Any]) -> Optional[str]:
        """Insert escalation using thread pool."""
        try:
            loop = asyncio.get_event_loop()
            escalation_id = await loop.run_in_executor(
                None,
                self.db_client.insert_escalation,
                escalation_data
            )
            return escalation_id
        except Exception as e:
            logger.error(
                "insert_escalation_error",
                error=str(e),
                exc_info=True
            )
            return None
    
    def log_api_call(
        self,
        api_name: str,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
        status_code: Optional[int] = None,
        error: Optional[str] = None,
        request_tokens: Optional[int] = None,
        response_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Log API call details (non-blocking, structured logging only).
        
        This logs to structured logs but doesn't persist to database
        (API calls are tracked via processing times in interactions).
        """
        log_data = {
            "api_name": api_name,
            "endpoint": endpoint,
            "method": method,
            "processing_time_ms": processing_time_ms,
            "status_code": status_code,
            "error": error,
            "request_tokens": request_tokens,
            "response_tokens": response_tokens,
            "total_tokens": total_tokens,
            "model": model,
            **kwargs
        }
        
        if error:
            logger.error(
                "api_call_error",
                **log_data
            )
        else:
            logger.info(
                "api_call_completed",
                **log_data
            )
    
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
_interaction_logger: Optional[InteractionLogger] = None

def get_interaction_logger() -> InteractionLogger:
    """Get singleton interaction logger instance."""
    global _interaction_logger
    if _interaction_logger is None:
        _interaction_logger = InteractionLogger()
    return _interaction_logger
