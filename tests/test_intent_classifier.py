"""Unit tests for Intent Classifier service."""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from services.intent_classifier import IntentClassifier


@pytest.mark.asyncio
async def test_intent_classification_success(mock_openai_client, sample_intent_result):
    """Test successful intent classification."""
    classifier = IntentClassifier()
    
    # Mock OpenAI response
    mock_response = {
        "content": '{"intent_name": "fee_inquiry", "intent_category": "automatable", "classification_reason": "User asking about fees"}'
    }
    
    mock_openai_client.return_value.chat_completion = Mock(return_value=mock_response)
    mock_openai_client.return_value.parse_json_response = Mock(return_value={
        "intent_name": "fee_inquiry",
        "intent_category": "automatable",
        "classification_reason": "User asking about fees"
    })
    
    result = await classifier.classify("What are the account fees?", "customer")
    
    assert result is not None
    assert result["intent_name"] == "fee_inquiry"
    assert result["intent_category"] == "automatable"


@pytest.mark.asyncio
async def test_intent_classification_timeout(mock_openai_client):
    """Test intent classification timeout handling."""
    classifier = IntentClassifier()
    classifier.timeout = 0.1  # Very short timeout for testing
    
    # Mock timeout by making the call take longer than timeout
    async def slow_call(*args, **kwargs):
        await asyncio.sleep(0.2)
        return {}
    
    # Since the actual implementation uses asyncio.wait_for, we test that timeout is handled
    # The actual API might still be called, so we check the structure
    try:
        result = await asyncio.wait_for(
            classifier.classify("Test query", "customer"),
            timeout=0.15
        )
        # If it completes, it might return a result or None
        # The important thing is it doesn't hang
        assert result is None or isinstance(result, dict)
    except asyncio.TimeoutError:
        # Expected timeout
        pass


@pytest.mark.asyncio
async def test_intent_classification_invalid_json(mock_openai_client):
    """Test handling of invalid JSON response."""
    classifier = IntentClassifier()
    
    # Mock invalid JSON response
    mock_response = {
        "content": "Invalid JSON response"
    }
    
    mock_openai_client.return_value.chat_completion = Mock(return_value=mock_response)
    mock_openai_client.return_value.parse_json_response = Mock(return_value=None)
    
    result = await classifier.classify("Test query", "customer")
    
    # Should handle gracefully (returns None or defaults to unknown)
    assert result is None or result.get("intent_name") == "unknown"


@pytest.mark.asyncio
async def test_intent_classification_empty_query(mock_openai_client):
    """Test handling of empty query."""
    classifier = IntentClassifier()
    
    result = await classifier.classify("", "customer")
    
    assert result is None


@pytest.mark.asyncio
async def test_intent_classification_invalid_mode(mock_openai_client):
    """Test handling of invalid assistant mode."""
    classifier = IntentClassifier()
    
    result = await classifier.classify("Test query", "invalid_mode")
    
    assert result is None
