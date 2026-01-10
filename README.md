# ContactIQ

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
- Supabase account (free tier is fine)
- Virtual environment (venv)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd anz-conversational-ai-0
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
   Create a `.env` file in the root directory:
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
   SESSION_PASSWORD=your-password
   API_TIMEOUT=30
   ```

5. **Set up Supabase**:
   - Create Supabase project
   - Run migrations: `python database/run_migrations.py`
   - Or manually run `database/schema.sql` in Supabase SQL Editor

6. **Set up Vector Stores**:
   - Run knowledge ingestion: `python knowledge/ingestor.py`
   - Upload to Vector Stores: `python knowledge/vector_store_setup.py`
   - Or use the setup script: `python setup_vector_stores.py`
   - Add Vector Store IDs to `.env`

## Configuration

Required environment variables (see `.env` example above):

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: Model to use (default: `gpt-4o-mini`)
- `OPENAI_VECTOR_STORE_ID_CUSTOMER`: Customer Vector Store ID
- `OPENAI_VECTOR_STORE_ID_BANKER`: Banker Vector Store ID
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase API key
- `CONFIDENCE_THRESHOLD`: Confidence threshold for escalation (default: `0.68`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `SESSION_PASSWORD`: Password for authentication
- `API_TIMEOUT`: API timeout in seconds (default: `30`)

## Usage

1. **Start the application**:
   ```bash
   streamlit run main.py
   ```

2. **Access the application**:
   - Open browser to `http://localhost:8501`
   - Enter password (configured in `.env`)
   - Select mode (Customer or Banker)
   - Start chatting!

## Testing

Comprehensive test suite with **56 tests** covering all services and integration scenarios. Test suite includes unit tests, integration tests, authentication tests, timeout handling tests, and structured logging tests.

### Test Coverage

- **Unit Tests**: All services (intent_classifier, router, retrieval, response_generator, confidence_scorer, escalation_handler, logger)
- **Integration Tests**: Full pipeline execution scenarios
- **Authentication Tests**: Password authentication and session management
- **Timeout Handling Tests**: API timeout scenarios across all services
- **Structured Logging Tests**: Logging functionality and structured output

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_intent_classifier.py

# Run with coverage report
pytest --cov=services --cov=utils --cov=ui --cov-report=html tests/

# Run with verbose output
pytest -v tests/

# Run with detailed output (show print statements)
pytest -s tests/

# Run only async tests
pytest -m asyncio tests/
```

### Test Files

- `test_intent_classifier.py` - Intent classification service tests
- `test_router.py` - Routing logic tests
- `test_retrieval_service.py` - Vector store retrieval tests
- `test_response_generator.py` - Response generation tests
- `test_confidence_scorer.py` - Confidence scoring tests
- `test_escalation_handler.py` - Escalation handling tests
- `test_logger.py` - Logging service tests
- `test_auth.py` - Authentication tests
- `test_pipeline_integration.py` - Full pipeline integration tests
- `test_timeout_handling.py` - Timeout handling tests
- `test_structured_logging.py` - Structured logging tests
- `conftest.py` - Pytest configuration and fixtures

## Project Structure

```
anz-conversational-ai-0/
├── main.py                      # Streamlit app entry point
├── config.py                    # Configuration management
├── requirements.txt             # Python dependencies
├── DEPLOYMENT.md                # Deployment guide
├── IMPLEMENTATION_GUIDE.md      # Step-by-step implementation guide
│
├── services/                    # Pipeline services (async)
│   ├── __init__.py
│   ├── intent_classifier.py    # Step 1: Intent classification
│   ├── router.py               # Step 2: Routing logic
│   ├── retrieval_service.py    # Step 3: Vector store retrieval
│   ├── response_generator.py   # Step 4: Response generation
│   ├── confidence_scorer.py    # Step 5: Confidence scoring
│   ├── escalation_handler.py   # Step 6: Escalation handling
│   └── logger.py               # Step 7: Interaction logging
│
├── knowledge/                   # Knowledge base management
│   ├── __init__.py
│   ├── ingestor.py             # Web scraping & ingestion
│   ├── vector_store_setup.py   # Vector store upload
│   ├── synthetic_generator.py  # Synthetic document generation
│   ├── cleaner.py              # Content cleaning utilities
│   └── hierarchical_extractor.py
│
├── database/                    # Database schema and client
│   ├── __init__.py
│   ├── schema.sql              # Supabase schema
│   ├── supabase_client.py      # Supabase client wrapper
│   ├── run_migrations.py       # Migration runner
│   └── migrations/             # SQL migration scripts
│
├── ui/                          # UI components (Streamlit)
│   ├── __init__.py
│   ├── auth.py                 # Authentication module
│   ├── chat_interface.py       # Chat UI
│   └── dashboard.py            # KPI dashboard
│
├── utils/                       # Utility modules
│   ├── __init__.py
│   ├── openai_client.py        # OpenAI client wrapper
│   ├── logger.py               # Structured logging setup
│   ├── constants.py            # Intent taxonomy, constants
│   └── validators.py           # Data validation utilities
│
└── tests/                       # Comprehensive test suite
    ├── __init__.py
    ├── conftest.py             # Pytest fixtures and configuration
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
    └── test_structured_logging.py
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

### Documentation

- **IMPLEMENTATION_GUIDE.md**: Step-by-step implementation instructions for all tasks
- **guides/MASTER_INDEX.md**: Master index of all task guides
- **guides/TASK_XX_*.md**: Detailed guides for each task (01-19)
- **DEPLOYMENT.md**: Complete deployment guide with multiple platform options
- **PRD.md**: Product Requirements Document
- **DETAILED_PLAN.md**: Detailed technical implementation plan

### Key Implementation Details

- All services use **async/await** for non-blocking operations
- **30-second timeout** for all API calls (configurable via `API_TIMEOUT`)
- **Structured logging** with ERROR, WARN, INFO levels using structlog
- **Retry logic** with exponential backoff for failed API calls
- **Non-blocking logging** to Supabase with retry queue

## Deployment

See `DEPLOYMENT.md` for deployment instructions.

## Known Limitations (MVP)

This is an MVP version with the following limitations:

- **No voice interactions**: Text-only interface
- **No CRM integration**: Standalone system
- **No personalized advice**: General information only
- **Simple authentication**: Password-based (not production-ready OAuth)
- **No proactive messaging**: Reactive responses only

## Troubleshooting

### Common Issues

1. **Configuration errors**: Verify all environment variables are set correctly in `.env`
2. **Vector Store not found**: Ensure Vector Stores are created and IDs are correct
3. **Database connection errors**: Check Supabase URL and API key
4. **API timeout errors**: Increase `API_TIMEOUT` or check network connectivity
5. **Import errors**: Ensure virtual environment is activated and dependencies installed

### Getting Help

- Check `DEPLOYMENT.md` for deployment issues
- Review `IMPLEMENTATION_GUIDE.md` for implementation questions
- Check test files in `tests/` directory for usage examples

## License

[Your License Here]

## Support

For issues or questions, please [contact method].

## Safety Notice

**ContactIQ does not provide financial advice and should always escalate when uncertainty exists.**
