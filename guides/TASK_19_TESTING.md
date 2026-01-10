# Task 19: Testing & Documentation

## Overview
Create comprehensive test suite for all services and update documentation (README, deployment guide). Includes unit tests, integration tests, async tests, authentication tests, timeout tests, and structured logging tests.

## Prerequisites
- All previous tasks completed (Tasks 1-18)
- All services implemented
- Virtual environment activated
- pytest installed

## Deliverables

### 1. Test Suite (tests/ directory)

Create comprehensive test suite with:
- Unit tests for all services
- Integration tests for pipeline
- Async tests
- Authentication tests
- Timeout handling tests
- Structured logging tests

### 2. Documentation Updates

- README.md updates
- DEPLOYMENT.md guide
- Error handling validation

## Implementation

### Step 1: Test Setup

Create test directory structure:

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── test_intent_classifier.py
├── test_router.py
├── test_retrieval_service.py
├── test_response_generator.py
├── test_confidence_scorer.py
├── test_escalation_handler.py
├── test_logger.py
├── test_auth.py
├── test_pipeline_integration.py
├── test_timeout_handling.py
└── test_chat_interface.py
```

### Step 2: Pytest Configuration

```python
# tests/conftest.py
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
```

### Step 3: Unit Tests - Intent Classifier

```python
# tests/test_intent_classifier.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from services.intent_classifier import IntentClassifier


@pytest.mark.asyncio
async def test_intent_classification_success(mock_openai_client, sample_intent_result):
    """Test successful intent classification."""
    classifier = IntentClassifier()
    
    # Mock OpenAI response
    mock_openai_client().chat.completions.create = AsyncMock(return_value=Mock(
        choices=[Mock(message=Mock(content='{"intent_name": "fee_inquiry", "intent_category": "automatable", "classification_reason": "User asking about fees"}'))]
    ))
    
    result = await classifier.classify_async("What are the account fees?", "customer")
    
    assert result is not None
    assert result["intent_name"] == "fee_inquiry"
    assert result["intent_category"] == "automatable"


@pytest.mark.asyncio
async def test_intent_classification_timeout(mock_openai_client):
    """Test intent classification timeout handling."""
    classifier = IntentClassifier()
    
    # Mock timeout
    mock_openai_client().chat.completions.create = AsyncMock(side_effect=asyncio.TimeoutError())
    
    result = await classifier.classify_async("Test query", "customer")
    
    assert result is None


@pytest.mark.asyncio
async def test_intent_classification_invalid_json(mock_openai_client):
    """Test handling of invalid JSON response."""
    classifier = IntentClassifier()
    
    # Mock invalid JSON response
    mock_openai_client().chat.completions.create = AsyncMock(return_value=Mock(
        choices=[Mock(message=Mock(content="Invalid JSON response"))]
    ))
    
    result = await classifier.classify_async("Test query", "customer")
    
    # Should handle gracefully (returns None or defaults to unknown)
    assert result is None or result.get("intent_name") == "unknown"
```

### Step 4: Unit Tests - Router

```python
# tests/test_router.py
import pytest
from services.router import Router, route


def test_route_human_only():
    """Test routing for human_only category."""
    result = route("human_only", "financial_advice", "customer")
    
    assert result["route"] == "escalate"
    assert result["next_step"] == 6
    assert result["skip_to_step"] == 6


def test_route_automatable():
    """Test routing for automatable category."""
    result = route("automatable", "fee_inquiry", "customer")
    
    assert result["route"] == "continue"
    assert result["next_step"] == 3


def test_route_sensitive():
    """Test routing for sensitive category."""
    result = route("sensitive", "account_balance", "customer")
    
    assert result["route"] == "continue"
    assert result["next_step"] == 3


def test_route_invalid_category():
    """Test routing for invalid category."""
    result = route("invalid_category", None, None)
    
    # Should default to escalate
    assert result["route"] == "escalate"
    assert result["next_step"] == 6


def test_router_class():
    """Test Router class methods."""
    router = Router()
    
    assert router.should_escalate("human_only") == True
    assert router.should_escalate("automatable") == False
    
    assert router.get_next_step("human_only") == 6
    assert router.get_next_step("automatable") == 3
```

### Step 5: Unit Tests - Confidence Scorer

```python
# tests/test_confidence_scorer.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from services.confidence_scorer import ConfidenceScorer


@pytest.mark.asyncio
async def test_confidence_scoring_success(mock_openai_client):
    """Test successful confidence scoring."""
    scorer = ConfidenceScorer()
    
    # Mock OpenAI response
    mock_openai_client().chat.completions.create = AsyncMock(return_value=Mock(
        choices=[Mock(message=Mock(content='{"confidence": 0.85, "reasoning": "High confidence"}'))]
    ))
    
    result = await scorer.score_async(
        response_text="Test response",
        retrieved_chunks=[{"content": "Test chunk"}],
        user_query="Test query",
        assistant_mode="customer"
    )
    
    assert result is not None
    assert result["confidence_score"] == 0.85
    assert result["meets_threshold"] == True


@pytest.mark.asyncio
async def test_confidence_scoring_low_confidence(mock_openai_client):
    """Test low confidence scoring."""
    scorer = ConfidenceScorer()
    
    # Mock low confidence response
    mock_openai_client().chat.completions.create = AsyncMock(return_value=Mock(
        choices=[Mock(message=Mock(content='{"confidence": 0.5, "reasoning": "Low confidence"}'))]
    ))
    
    result = await scorer.score_async(
        response_text="Test response",
        retrieved_chunks=[{"content": "Test chunk"}],
        user_query="Test query",
        assistant_mode="customer"
    )
    
    assert result["confidence_score"] == 0.5
    assert result["meets_threshold"] == False


@pytest.mark.asyncio
async def test_confidence_scoring_timeout(mock_openai_client):
    """Test confidence scoring timeout."""
    scorer = ConfidenceScorer()
    
    # Mock timeout
    mock_openai_client().chat.completions.create = AsyncMock(side_effect=asyncio.TimeoutError())
    
    result = await scorer.score_async(
        response_text="Test response",
        retrieved_chunks=[],
        user_query="Test query",
        assistant_mode="customer"
    )
    
    # Should default to low confidence
    assert result["meets_threshold"] == False
    assert result["confidence_score"] == 0.0
```

### Step 6: Unit Tests - Escalation Handler

```python
# tests/test_escalation_handler.py
import pytest
import asyncio
from services.escalation_handler import EscalationHandler


@pytest.mark.asyncio
async def test_escalation_human_only():
    """Test escalation for human_only trigger."""
    handler = EscalationHandler()
    
    result = await handler.handle_escalation_async(
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
    
    result = await handler.handle_escalation_async(
        trigger_type="low_confidence",
        assistant_mode="customer",
        confidence_score=0.5,
        escalation_reason="Confidence below threshold"
    )
    
    assert result["escalated"] == True
    assert result["trigger_type"] == "low_confidence"


def test_detect_escalation_triggers():
    """Test escalation trigger detection."""
    handler = EscalationHandler()
    
    # Test account-specific trigger
    triggers = handler.detect_escalation_triggers(
        user_query="I need to check my account balance",
        intent_category="sensitive",
        confidence_score=0.7,
        retrieved_chunks=[{"content": "test"}]
    )
    
    assert "account_specific" in triggers
    
    # Test explicit human request
    triggers = handler.detect_escalation_triggers(
        user_query="I want to speak to a human",
        intent_category="automatable",
        confidence_score=0.8,
        retrieved_chunks=[{"content": "test"}]
    )
    
    assert "explicit_human_request" in triggers
```

### Step 7: Unit Tests - Authentication

```python
# tests/test_auth.py
import pytest
import streamlit as st
from unittest.mock import patch, Mock
from ui.auth import check_authentication


def test_authentication_success():
    """Test successful authentication."""
    with patch('streamlit.session_state', {'authenticated': True}):
        with patch('streamlit.title'), patch('streamlit.stop'):
            result = check_authentication()
            assert result == True


def test_authentication_failure():
    """Test failed authentication."""
    with patch('streamlit.session_state', {'authenticated': False}):
        with patch('streamlit.title'), patch('streamlit.text_input'), patch('streamlit.button'), patch('streamlit.stop'):
            # Should show password prompt
            check_authentication()
            # Test would need to verify UI elements shown
```

### Step 8: Integration Tests - Pipeline

```python
# tests/test_pipeline_integration.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from services.pipeline import PipelineOrchestrator


@pytest.mark.asyncio
async def test_full_pipeline_happy_path(mock_openai_client, mock_supabase_client):
    """Test full pipeline execution (happy path)."""
    orchestrator = PipelineOrchestrator()
    
    # Mock all service responses
    # Intent classification
    mock_openai_client().chat.completions.create = AsyncMock(return_value=Mock(
        choices=[Mock(message=Mock(content='{"intent_name": "fee_inquiry", "intent_category": "automatable", "classification_reason": "..."}'))]
    ))
    
    # Retrieval (simplified - adjust based on actual implementation)
    # Response generation
    # Confidence scoring
    
    result = await orchestrator.execute_pipeline_async(
        user_query="What are the account fees?",
        assistant_mode="customer"
    )
    
    assert result is not None
    assert "outcome" in result


@pytest.mark.asyncio
async def test_pipeline_escalation_human_only(mock_openai_client, mock_supabase_client):
    """Test pipeline escalation for human_only intent."""
    orchestrator = PipelineOrchestrator()
    
    # Mock intent classification returning human_only
    mock_openai_client().chat.completions.create = AsyncMock(return_value=Mock(
        choices=[Mock(message=Mock(content='{"intent_name": "financial_advice", "intent_category": "human_only", "classification_reason": "..."}'))]
    ))
    
    result = await orchestrator.execute_pipeline_async(
        user_query="Should I invest in stocks?",
        assistant_mode="customer"
    )
    
    assert result["escalated"] == True
    assert result["outcome"] == "escalated"
    assert result["trigger_type"] == "human_only"


@pytest.mark.asyncio
async def test_pipeline_escalation_low_confidence(mock_openai_client, mock_supabase_client):
    """Test pipeline escalation for low confidence."""
    orchestrator = PipelineOrchestrator()
    
    # Mock responses for each step
    # ... (mock intent, retrieval, response, low confidence)
    
    result = await orchestrator.execute_pipeline_async(
        user_query="Test query",
        assistant_mode="customer"
    )
    
    assert result["escalated"] == True
    assert result["trigger_type"] == "low_confidence"
```

### Step 9: Timeout Handling Tests

```python
# tests/test_timeout_handling.py
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from config import Config
from services.intent_classifier import IntentClassifier


@pytest.mark.asyncio
async def test_timeout_handling_intent_classifier(mock_openai_client):
    """Test timeout handling in intent classifier."""
    classifier = IntentClassifier()
    
    # Mock slow response that times out
    async def slow_response(*args, **kwargs):
        await asyncio.sleep(Config.API_TIMEOUT + 1)  # Longer than timeout
        return Mock()
    
    mock_openai_client().chat.completions.create = slow_response
    
    result = await classifier.classify_async("Test query", "customer")
    
    # Should handle timeout gracefully
    assert result is None or "timeout" in str(result).lower()


@pytest.mark.asyncio
async def test_timeout_handling_pipeline(mock_openai_client):
    """Test timeout handling in full pipeline."""
    from services.pipeline import PipelineOrchestrator
    
    orchestrator = PipelineOrchestrator()
    
    # Mock timeout at any step
    async def timeout_response(*args, **kwargs):
        await asyncio.sleep(Config.API_TIMEOUT + 1)
        return Mock()
    
    mock_openai_client().chat.completions.create = timeout_response
    
    result = await orchestrator.execute_pipeline_async(
        user_query="Test query",
        assistant_mode="customer"
    )
    
    # Should escalate on timeout
    assert result["escalated"] == True
```

### Step 10: Structured Logging Tests

```python
# tests/test_logger.py
import pytest
import asyncio
from unittest.mock import patch, Mock
from utils.logger import get_logger, setup_logging
from services.logger import Logger


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
    logger_service = Logger()
    
    # Mock Supabase insert
    mock_supabase_client().insert_interaction = AsyncMock(return_value="test-id")
    
    await logger_service.log_interaction_async(
        user_query="Test query",
        assistant_mode="customer",
        intent_name="test_intent",
        outcome="resolved"
    )
    
    # Verify insert was called
    mock_supabase_client().insert_interaction.assert_called_once()
```

### Step 11: Update README.md

```markdown
# ContactIQ - Conversational AI for Banking (MVP)

**Conversational AI for Banking (MVP)**

## Introduction

ContactIQ is a conversational AI system designed to explore how banking organisations can responsibly use AI to handle common queries and support frontline staff while maintaining safety, transparency, and measurable outcomes.

## Features

- **Dual Assistant Modes**: Customer and Banker assistants with distinct behaviors
- **Intent-First Pipeline**: Classify → Route → Retrieve → Generate → Confidence Check → Escalate
- **Retrieval-Augmented Generation**: Uses OpenAI Vector Store for knowledge retrieval
- **Transparent Responses**: Citations, confidence scores, and escalation reasons
- **Live KPI Dashboard**: Real-time metrics and analytics
- **Authentication**: Simple password protection
- **Async Architecture**: Concurrent operations with timeout handling
- **Structured Logging**: Enhanced observability with ERROR, WARN, INFO levels

## Prerequisites

- Python 3.12 or 3.13
- OpenAI API account with access to:
  - Chat Completions API
  - Vector Store API
  - Files API
  - Conversations API (optional)
- Supabase account (free tier is fine)
- Virtual environment (venv)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd contactiq
   ```

2. **Create virtual environment**:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual keys
   ```

5. **Set up Supabase**:
   - Create Supabase project
   - Run migrations: `python database/run_migrations.py`
   - Or manually run `database/schema.sql` in Supabase SQL Editor

6. **Set up Vector Stores**:
   - Run knowledge ingestion: `python knowledge/ingestor.py`
   - Upload to Vector Stores: `python knowledge/vector_store_setup.py`
   - Add Vector Store IDs to `.env`

## Configuration

Required environment variables (see `.env.example`):

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_VECTOR_STORE_ID_CUSTOMER=vs_...
OPENAI_VECTOR_STORE_ID_BANKER=vs_...

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...

# Application
CONFIDENCE_THRESHOLD=0.68
LOG_LEVEL=INFO
SESSION_PASSWORD=rahul
API_TIMEOUT=30
```

## Usage

1. **Start the application**:
   ```bash
   streamlit run main.py
   ```

2. **Access the application**:
   - Open browser to `http://localhost:8501`
   - Enter password: "rahul" (or your configured password)
   - Select mode (Customer or Banker)
   - Start chatting!

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_intent_classifier.py

# Run with coverage
pytest --cov=services --cov=utils tests/
```

## Project Structure

```
contactiq/
├── main.py                 # Streamlit app entry point
├── config.py              # Configuration management
├── services/              # Pipeline services
│   ├── intent_classifier.py
│   ├── router.py
│   ├── retrieval_service.py
│   ├── response_generator.py
│   ├── confidence_scorer.py
│   ├── escalation_handler.py
│   ├── logger.py
│   └── pipeline.py       # Pipeline orchestrator
├── knowledge/             # Knowledge base management
│   ├── ingestor.py
│   ├── vector_store_setup.py
│   └── synthetic_generator.py
├── database/             # Database schema and client
│   ├── schema.sql
│   └── supabase_client.py
├── ui/                   # UI components
│   ├── auth.py
│   ├── chat_interface.py
│   └── dashboard.py
├── utils/                # Utilities
│   ├── openai_client.py
│   ├── logger.py
│   ├── constants.py
│   └── validators.py
└── tests/               # Test suite
    ├── test_*.py
    └── conftest.py
```

## Architecture

- **Frontend**: Streamlit
- **Backend**: Python (async/await)
- **AI/ML**: OpenAI gpt-4o-mini, Vector Store, Chat Completions API
- **Database**: Supabase PostgreSQL
- **Logging**: Structured logging with structlog

## Pipeline Flow

1. **Intent Classification**: Classify user query into intent
2. **Router**: Route based on intent category
3. **Retrieval**: Retrieve relevant chunks from Vector Store
4. **Response Generation**: Generate response with citations
5. **Confidence Scoring**: Score response confidence
6. **Escalation Handler**: Handle escalations if needed
7. **Logging**: Log all interactions

## Safety & Escalation

The system escalates to human support when:
- Intent category is HumanOnly
- Confidence score < 0.68
- Insufficient or conflicting evidence
- Account-specific or security/fraud requests
- Financial advice framing
- Legal/hardship signals
- Emotional distress
- Explicit human request

## Metrics & Dashboard

The KPI dashboard displays:
- Overall usage metrics
- Mode breakdown
- Resolution metrics (containment/escalation rates)
- Intent frequency distribution
- Escalation analysis
- Confidence metrics
- Performance metrics

## Development

See `IMPLEMENTATION_GUIDE.md` for step-by-step implementation instructions.

See `guides/MASTER_INDEX.md` for task guides.

## License

[Your License Here]

## Support

For issues or questions, please [contact method].
```

### Step 12: Create Deployment Guide

```markdown
# ContactIQ - Deployment Guide

## Local Development

### Prerequisites
- Python 3.12 or 3.13
- Virtual environment
- All API keys configured

### Steps

1. **Set up environment**:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Fill in all required values

3. **Set up database**:
   - Create Supabase project
   - Run `database/schema.sql` in Supabase SQL Editor

4. **Ingest knowledge base**:
   ```bash
   python knowledge/ingestor.py
   python knowledge/vector_store_setup.py
   ```

5. **Run application**:
   ```bash
   streamlit run main.py
   ```

## Production Deployment (Future)

### Streamlit Cloud

1. **Prepare repository**:
   - Ensure all code is committed
   - Create `requirements.txt`
   - Create `.streamlit/config.toml` if needed

2. **Deploy to Streamlit Cloud**:
   - Connect GitHub repository
   - Set environment variables in Streamlit Cloud dashboard
   - Deploy

3. **Environment Variables**:
   - Set all variables from `.env.example`
   - Keep secrets secure (use Streamlit Cloud secrets)

### Other Platforms

- **Docker**: Create Dockerfile for containerized deployment
- **Cloud Platforms**: Adapt for AWS, GCP, Azure as needed

## Post-Deployment

1. **Verify**:
   - Authentication works
   - Pipeline executes
   - Logging works
   - Dashboard displays metrics

2. **Monitor**:
   - Check logs for errors
   - Monitor API usage
   - Review dashboard metrics
```

## Success Criteria

- [ ] Unit tests pass for all services (including async)
- [ ] Integration tests validate full pipeline (async)
- [ ] Authentication tests pass
- [ ] Timeout handling tests pass (30s timeout scenarios)
- [ ] Structured logging tests pass
- [ ] README.md updated with complete information
- [ ] DEPLOYMENT.md created with deployment instructions
- [ ] Error scenarios tested (API failures, timeouts, invalid inputs)
- [ ] Test coverage > 70% (optional but recommended)

## Additional Dependencies

Add to `requirements.txt`:
```python
# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
```

## Running Tests

```bash
# Install pytest and coverage
pip install -r requirements.txt

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=services --cov=utils --cov=ui tests/

# Run specific test file
pytest tests/test_intent_classifier.py

# Run with verbose output
pytest -v tests/

# Run with output
pytest -s tests/
```

## Test Coverage Goals

- **Services**: > 80% coverage
- **Utils**: > 70% coverage
- **UI**: > 60% coverage (UI testing is harder)

## Reference

- **DETAILED_PLAN.md** Section 12 (Testing Strategy)
- **TASK_BREAKDOWN.md** Task 19
- **pytest Documentation**: https://docs.pytest.org/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
