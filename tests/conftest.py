"""Pytest configuration and fixtures for ContactIQ tests."""
import pytest
import asyncio
import os
from unittest.mock import Mock, AsyncMock, patch
from config import Config

# Set test environment variables
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"
os.environ["SESSION_PASSWORD"] = "test-password"
os.environ["API_TIMEOUT"] = "5"  # Shorter timeout for tests
os.environ["CONFIDENCE_THRESHOLD"] = "0.68"

# Async test fixture
@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch('utils.openai_client.get_openai_client') as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    with patch('database.supabase_client.get_db_client') as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def sample_intent_result():
    """Sample intent classification result."""
    return {
        "intent_name": "fee_inquiry",
        "intent_category": "automatable",
        "classification_reason": "User is asking about fees",
        "assistant_mode": "customer"
    }


@pytest.fixture
def sample_retrieved_chunks():
    """Sample retrieved chunks."""
    return [
        {
            "content": "ANZ monthly account fee is $5.00 for standard accounts.",
            "source": "ANZ Fee Schedule",
            "url": "https://www.anz.com.au/support/legal/rates-fees-terms/"
        },
        {
            "content": "Standard personal accounts include basic transaction features.",
            "source": "ANZ Terms",
            "url": "https://www.anz.com.au/support/legal/rates-fees-terms/fees-terms-conditions/bank-accounts/"
        }
    ]


@pytest.fixture
def sample_response_text():
    """Sample response text."""
    return "The ANZ monthly account fee is $5.00 for standard accounts. This includes basic transaction features."


@pytest.fixture
def sample_citations():
    """Sample citations."""
    return [
        {
            "number": 1,
            "file_id": "file-abc123",
            "quote": "ANZ monthly account fee is $5.00",
            "source": "ANZ Fee Schedule"
        }
    ]
