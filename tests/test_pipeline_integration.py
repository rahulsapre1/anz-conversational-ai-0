"""Integration tests for full pipeline."""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from services.intent_classifier import IntentClassifier
from services.router import Router
from services.retrieval_service import RetrievalService
from services.response_generator import ResponseGenerator
from services.confidence_scorer import ConfidenceScorer
from services.escalation_handler import EscalationHandler


@pytest.mark.asyncio
async def test_full_pipeline_happy_path(mock_openai_client, mock_supabase_client):
    """Test full pipeline execution (happy path)."""
    # Mock intent classification
    intent_classifier = IntentClassifier()
    with patch.object(intent_classifier, 'classify', new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = {
            "intent_name": "fee_inquiry",
            "intent_category": "automatable",
            "classification_reason": "User asking about fees",
            "assistant_mode": "customer"
        }
        
        # Mock retrieval
        retrieval_service = RetrievalService()
        with patch.object(retrieval_service, 'retrieve', new_callable=AsyncMock) as mock_retrieve:
            mock_retrieve.return_value = {
                "retrieved_chunks": ["ANZ monthly account fee is $5.00"],
                "citations": [{"number": 1, "source": "ANZ Fee Schedule"}],
                "success": True
            }
            
            # Mock response generation
            response_generator = ResponseGenerator()
            with patch.object(response_generator, 'generate', new_callable=AsyncMock) as mock_generate:
                mock_generate.return_value = {
                    "response_text": "The ANZ monthly account fee is $5.00.",
                    "citations": [{"number": 1, "source": "ANZ Fee Schedule"}],
                    "has_synthetic_content": False
                }
                
                # Mock confidence scoring
                confidence_scorer = ConfidenceScorer()
                with patch.object(confidence_scorer, 'score', new_callable=AsyncMock) as mock_score:
                    mock_score.return_value = {
                        "confidence_score": 0.85,
                        "meets_threshold": True,
                        "threshold_value": 0.68,
                        "reasoning": "High confidence"
                    }
                    
                    # Execute pipeline steps
                    intent_result = await intent_classifier.classify("What are the fees?", "customer")
                    assert intent_result is not None
                    
                    router = Router()
                    routing_decision = router.route(
                        intent_category=intent_result["intent_category"],
                        intent_name=intent_result["intent_name"],
                        assistant_mode="customer"
                    )
                    assert routing_decision["route"] == "continue"
                    
                    retrieval_result = await retrieval_service.retrieve("What are the fees?", "customer")
                    assert retrieval_result["success"] == True
                    
                    response_result = await response_generator.generate(
                        user_query="What are the fees?",
                        retrieved_chunks=retrieval_result["retrieved_chunks"],
                        assistant_mode="customer"
                    )
                    assert response_result is not None
                    
                    confidence_result = await confidence_scorer.score(
                        response_text=response_result["response_text"],
                        retrieved_chunks=retrieval_result["retrieved_chunks"],
                        user_query="What are the fees?",
                        assistant_mode="customer"
                    )
                    assert confidence_result["meets_threshold"] == True


@pytest.mark.asyncio
async def test_pipeline_escalation_human_only(mock_openai_client, mock_supabase_client):
    """Test pipeline escalation for human_only intent."""
    intent_classifier = IntentClassifier()
    with patch.object(intent_classifier, 'classify', new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = {
            "intent_name": "financial_advice",
            "intent_category": "human_only",
            "classification_reason": "Requires human handling",
            "assistant_mode": "customer"
        }
        
        router = Router()
        routing_decision = router.route(
            intent_category="human_only",
            intent_name="financial_advice",
            assistant_mode="customer"
        )
        
        assert routing_decision["route"] == "escalate"
        
        escalation_handler = EscalationHandler()
        escalation_result = await escalation_handler.handle_escalation(
            trigger_type="human_only",
            assistant_mode="customer",
            intent_name="financial_advice",
            escalation_reason="Intent requires human handling"
        )
        
        assert escalation_result["escalated"] == True
        assert escalation_result["trigger_type"] == "human_only"


@pytest.mark.asyncio
async def test_pipeline_escalation_low_confidence(mock_openai_client, mock_supabase_client):
    """Test pipeline escalation for low confidence."""
    # Mock all services to return low confidence
    intent_classifier = IntentClassifier()
    with patch.object(intent_classifier, 'classify', new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = {
            "intent_name": "fee_inquiry",
            "intent_category": "automatable",
            "classification_reason": "User asking about fees",
            "assistant_mode": "customer"
        }
        
        retrieval_service = RetrievalService()
        with patch.object(retrieval_service, 'retrieve', new_callable=AsyncMock) as mock_retrieve:
            mock_retrieve.return_value = {
                "retrieved_chunks": ["Some content"],
                "citations": [],
                "success": True
            }
            
            response_generator = ResponseGenerator()
            with patch.object(response_generator, 'generate', new_callable=AsyncMock) as mock_generate:
                mock_generate.return_value = {
                    "response_text": "Test response",
                    "citations": [],
                    "has_synthetic_content": False
                }
                
                confidence_scorer = ConfidenceScorer()
                with patch.object(confidence_scorer, 'score', new_callable=AsyncMock) as mock_score:
                    mock_score.return_value = {
                        "confidence_score": 0.5,  # Below threshold
                        "meets_threshold": False,
                        "threshold_value": 0.68,
                        "reasoning": "Low confidence"
                    }
                    
                    # Execute pipeline
                    intent_result = await intent_classifier.classify("Test query", "customer")
                    router = Router()
                    routing_decision = router.route(
                        intent_category=intent_result["intent_category"],
                        intent_name=intent_result["intent_name"],
                        assistant_mode="customer"
                    )
                    
                    if routing_decision["route"] == "continue":
                        retrieval_result = await retrieval_service.retrieve("Test query", "customer")
                        response_result = await response_generator.generate(
                            user_query="Test query",
                            retrieved_chunks=retrieval_result["retrieved_chunks"],
                            assistant_mode="customer"
                        )
                        confidence_result = await confidence_scorer.score(
                            response_text=response_result["response_text"],
                            retrieved_chunks=retrieval_result["retrieved_chunks"],
                            user_query="Test query",
                            assistant_mode="customer"
                        )
                        
                        if not confidence_result["meets_threshold"]:
                            escalation_handler = EscalationHandler()
                            escalation_result = await escalation_handler.handle_escalation(
                                trigger_type="low_confidence",
                                assistant_mode="customer",
                                confidence_score=confidence_result["confidence_score"],
                                escalation_reason=f"Confidence {confidence_result['confidence_score']:.2f} below threshold"
                            )
                            
                            assert escalation_result["escalated"] == True
                            assert escalation_result["trigger_type"] == "low_confidence"
