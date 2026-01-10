"""Tests for structured logging."""
import pytest
import asyncio
from unittest.mock import patch, Mock
from utils.logger import get_logger, setup_logging
from services.logger import InteractionLogger


def test_structured_logging_setup():
    """Test structured logging setup."""
    setup_logging()
    logger = get_logger(__name__)
    
    # Should not raise exception
    logger.info("test_message", key="value")
    logger.warn("test_warning", key="value")
    logger.error("test_error", key="value")


@pytest.mark.asyncio
async def test_logger_service_async(mock_supabase_client):
    """Test async logging service."""
    logger_service = InteractionLogger()
    logger_service.db_client = mock_supabase_client
    
    # Mock Supabase insert
    mock_supabase_client.insert_interaction = Mock(return_value="test-id")
    
    interaction_data = {
        "assistant_mode": "customer",
        "user_query": "Test query",
        "intent_name": "test_intent",
        "outcome": "resolved"
    }
    
    result = await logger_service._insert_interaction_async(interaction_data)
    
    # Verify insert was called
    assert result == "test-id"
    mock_supabase_client.insert_interaction.assert_called_once()


def test_logger_info_level():
    """Test INFO level logging."""
    setup_logging()
    logger = get_logger(__name__)
    
    # Should not raise exception
    logger.info(
        "test_info",
        key1="value1",
        key2="value2"
    )


def test_logger_warn_level():
    """Test WARN level logging."""
    setup_logging()
    logger = get_logger(__name__)
    
    # Should not raise exception
    logger.warn(
        "test_warning",
        warning_type="test",
        message="Test warning message"
    )


def test_logger_error_level():
    """Test ERROR level logging."""
    setup_logging()
    logger = get_logger(__name__)
    
    # Should not raise exception
    logger.error(
        "test_error",
        error_type="test",
        error_message="Test error message"
    )


@pytest.mark.asyncio
async def test_logger_escalation_async(mock_supabase_client):
    """Test async escalation logging."""
    logger_service = InteractionLogger()
    logger_service.db_client = mock_supabase_client
    
    # Mock Supabase insert
    mock_supabase_client.insert_escalation = Mock(return_value="test-escalation-id")
    
    escalation_data = {
        "interaction_id": "test-interaction-id",
        "trigger_type": "low_confidence",
        "escalation_reason": "Confidence below threshold"
    }
    
    result = await logger_service._insert_escalation_async(escalation_data)
    
    assert result == "test-escalation-id"
    mock_supabase_client.insert_escalation.assert_called_once()
