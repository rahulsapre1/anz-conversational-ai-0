"""Unit tests for Escalation Handler service."""
import pytest
import asyncio
from services.escalation_handler import EscalationHandler


@pytest.mark.asyncio
async def test_escalation_human_only():
    """Test escalation for human_only trigger."""
    handler = EscalationHandler()
    
    result = await handler.handle_escalation(
        trigger_type="human_only",
        assistant_mode="customer",
        intent_name="financial_advice",
        escalation_reason="Intent requires human handling"
    )
    
    assert result["escalated"] == True
    assert result["trigger_type"] == "human_only"
    assert "escalation_message" in result


@pytest.mark.asyncio
async def test_escalation_low_confidence():
    """Test escalation for low_confidence trigger."""
    handler = EscalationHandler()
    
    result = await handler.handle_escalation(
        trigger_type="low_confidence",
        assistant_mode="customer",
        confidence_score=0.5,
        escalation_reason="Confidence below threshold"
    )
    
    assert result["escalated"] == True
    assert result["trigger_type"] == "low_confidence"


@pytest.mark.asyncio
async def test_escalation_insufficient_evidence():
    """Test escalation for insufficient_evidence trigger."""
    handler = EscalationHandler()
    
    result = await handler.handle_escalation(
        trigger_type="insufficient_evidence",
        assistant_mode="customer",
        escalation_reason="No retrieval results"
    )
    
    assert result["escalated"] == True
    assert result["trigger_type"] == "insufficient_evidence"


def test_detect_escalation_triggers():
    """Test escalation trigger detection."""
    handler = EscalationHandler()
    
    # Test account-specific trigger
    triggers = handler.detect_escalation_triggers(
        user_query="I need to check my account balance",
        intent_category="sensitive",
        confidence_score=0.7,
        retrieved_chunks=["test"]
    )
    
    assert "account_specific" in triggers
    
    # Test explicit human request
    triggers = handler.detect_escalation_triggers(
        user_query="I want to speak to a human",
        intent_category="automatable",
        confidence_score=0.8,
        retrieved_chunks=["test"]
    )
    
    assert "explicit_human_request" in triggers


def test_detect_escalation_triggers_human_only():
    """Test detection of human_only trigger."""
    handler = EscalationHandler()
    
    triggers = handler.detect_escalation_triggers(
        user_query="Test query",
        intent_category="human_only",
        confidence_score=0.8,
        retrieved_chunks=["test"]
    )
    
    assert "human_only" in triggers


def test_detect_escalation_triggers_low_confidence():
    """Test detection of low_confidence trigger."""
    handler = EscalationHandler()
    
    triggers = handler.detect_escalation_triggers(
        user_query="Test query",
        intent_category="automatable",
        confidence_score=0.5,  # Below threshold
        retrieved_chunks=["test"]
    )
    
    assert "low_confidence" in triggers


def test_detect_escalation_triggers_security_fraud():
    """Test detection of security/fraud trigger."""
    handler = EscalationHandler()
    
    triggers = handler.detect_escalation_triggers(
        user_query="I think my card was stolen",
        intent_category="automatable",
        confidence_score=0.8,
        retrieved_chunks=["test"]
    )
    
    assert "security_fraud" in triggers
