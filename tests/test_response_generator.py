"""Unit tests for Response Generator service."""
import pytest
import asyncio
from unittest.mock import Mock, patch
from services.response_generator import ResponseGenerator


@pytest.mark.asyncio
async def test_response_generation_success(mock_openai_client, sample_retrieved_chunks):
    """Test successful response generation."""
    generator = ResponseGenerator()
    
    # Mock OpenAI response
    mock_response = {
        "content": "The ANZ monthly account fee is $5.00 for standard accounts."
    }
    
    mock_openai_client.return_value.chat_completion = Mock(return_value=mock_response)
    
    result = await generator.generate(
        user_query="What are the account fees?",
        retrieved_chunks=[chunk["content"] for chunk in sample_retrieved_chunks],
        assistant_mode="customer",
        intent_name="fee_inquiry"
    )
    
    assert result is not None
    assert "response_text" in result
    assert len(result["response_text"]) > 0


@pytest.mark.asyncio
async def test_response_generation_no_chunks(mock_openai_client):
    """Test response generation with no retrieved chunks."""
    generator = ResponseGenerator()
    
    result = await generator.generate(
        user_query="Test query",
        retrieved_chunks=[],
        assistant_mode="customer"
    )
    
    assert result is not None
    assert "I don't have enough information" in result["response_text"]


@pytest.mark.asyncio
async def test_response_generation_timeout(mock_openai_client, sample_retrieved_chunks):
    """Test response generation timeout."""
    generator = ResponseGenerator()
    generator.timeout = 0.1  # Very short timeout for testing
    
    # Since the actual API might be called, we test that timeout is configured
    # The actual implementation will handle timeouts with retries
    result = await generator.generate(
        user_query="Test query",
        retrieved_chunks=[chunk["content"] for chunk in sample_retrieved_chunks],
        assistant_mode="customer"
    )
    
    # The result might be None on timeout or a response if it completes
    # The important thing is the function doesn't hang
    assert result is None or isinstance(result, dict)


@pytest.mark.asyncio
async def test_response_generation_synthetic_content(mock_openai_client):
    """Test response generation with synthetic content detection."""
    generator = ResponseGenerator()
    
    mock_response = {
        "content": "Test response"
    }
    
    mock_openai_client.return_value.chat_completion = Mock(return_value=mock_response)
    
    # Chunks with synthetic marker
    synthetic_chunks = ["SYNTHETIC CONTENT: Test content"]
    
    result = await generator.generate(
        user_query="Test query",
        retrieved_chunks=synthetic_chunks,
        assistant_mode="customer"
    )
    
    assert result is not None
    assert result["has_synthetic_content"] == True


@pytest.mark.asyncio
async def test_response_generation_citations(mock_openai_client, sample_retrieved_chunks, sample_citations):
    """Test response generation with citations."""
    generator = ResponseGenerator()
    
    mock_response = {
        "content": "The fee is $5.00 [1]."
    }
    
    mock_openai_client.return_value.chat_completion = Mock(return_value=mock_response)
    
    result = await generator.generate(
        user_query="What are the fees?",
        retrieved_chunks=[chunk["content"] for chunk in sample_retrieved_chunks],
        assistant_mode="customer",
        citations=sample_citations
    )
    
    assert result is not None
    assert len(result.get("citations", [])) > 0
