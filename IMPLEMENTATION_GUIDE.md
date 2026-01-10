# ContactIQ - Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing ContactIQ from scratch. Follow the tasks in order, as they have dependencies.

**Total Tasks**: 19 tasks organized into 5 phases  
**Estimated Time**: 16-23 hours (2-3 days with buffer)

---

## Prerequisites

Before starting, ensure you have:

1. **Python 3.12 or 3.13** installed
2. **Git** installed (for version control)
3. **OpenAI API Account** with:
   - API key
   - Access to Vector Store API
   - Access to Chat Completions API
   - Access to Conversations API
4. **Supabase Account** (free tier is fine):
   - Project URL
   - API key
5. **Text Editor/IDE** (VS Code, PyCharm, etc.)

---

## Phase 1: Foundation (Tasks 1-3)

### Step 1: Task 1 - Project Foundation & Configuration

**Time**: 2-3 hours  
**Guide**: `guides/TASK_01_FOUNDATION.md`

**What to do**:
1. Create project directory structure (flattish structure)
2. Set up virtual environment:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Create `requirements.txt` with all dependencies (including async and logging libraries)
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create `.env.example` with all required environment variables
6. Create `.env` file (copy from `.env.example` and fill in your keys)
7. Create `config.py` with Config class
8. Create `utils/logger.py` with structured logging setup
9. Create basic `main.py` with Streamlit scaffold
10. Create all `__init__.py` files
11. Test that Streamlit app runs:
    ```bash
    streamlit run main.py
    ```

**Success Criteria**:
- [ ] Project structure matches DETAILED_PLAN.md Section 1
- [ ] All dependencies install without errors
- [ ] Streamlit app runs and shows basic interface
- [ ] Config loads environment variables correctly
- [ ] Structured logging configured

**Next**: Move to Task 2

---

### Step 2: Task 2 - Database Schema & Supabase Setup

**Time**: 1-2 hours  
**Guide**: `guides/TASK_02_DATABASE.md`

**What to do**:
1. Create Supabase project (if not already created)
2. Get Supabase URL and API key
3. Add to `.env` file:
   ```bash
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_KEY=eyJ...
   ```
4. Create `database/schema.sql` with all tables:
   - `interactions` table
   - `escalations` table
   - `knowledge_documents` table
5. Run SQL migration in Supabase SQL Editor
6. Create `database/supabase_client.py` with client wrapper
7. Test connection and insert test data

**Success Criteria**:
- [ ] All tables created in Supabase
- [ ] Indexes created
- [ ] Client wrapper can connect
- [ ] Can insert and query test data

**Next**: Move to Task 3

---

### Step 3: Task 3 - OpenAI Client Setup & Intent Taxonomy

**Time**: 1-2 hours  
**Guide**: `guides/TASK_03_OPENAI_SETUP.md`

**What to do**:
1. Get OpenAI API key
2. Add to `.env` file:
   ```bash
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o-mini
   ```
3. Create `utils/openai_client.py` with OpenAI client wrapper
4. Create `utils/constants.py` with intent taxonomy:
   - Customer intents (13 intents)
   - Banker intents (12 intents)
5. Create `utils/validators.py` with validation functions
6. Test OpenAI client connection

**Success Criteria**:
- [ ] OpenAI client can make API calls
- [ ] Intent taxonomy defined correctly
- [ ] Validators work correctly

**Next**: Move to Phase 2

---

## Phase 2: Knowledge Base (Tasks 4-7)

### Step 4: Task 4 - Knowledge Base Ingestion - Web Scraping

**Time**: 2-3 hours  
**Guide**: `guides/TASK_04_KNOWLEDGE_SCRAPING.md` (summary in MASTER_INDEX.md)

**What to do**:
1. Read `ANZ_web_scrape.xml` for target URLs
2. Create `knowledge/ingestor.py` with async web scraping:
   - Use `aiohttp` for concurrent requests
   - 30s timeout per URL
   - Rate limiting (respect robots.txt)
3. Extract content using BeautifulSoup
4. Format as `.txt` files with metadata header:
   - Title, Source URL, Retrieval Date
   - Sanitized filename
5. Implement structured logging for scraping operations
6. Test scraping a few URLs

**Success Criteria**:
- [ ] Can scrape ANZ pages (async)
- [ ] Content extracted and cleaned
- [ ] Files formatted as `.txt` with proper structure
- [ ] Source URL included in each file
- [ ] Logging works correctly

**Next**: Move to Task 6

---

### Step 6: Task 6 - Vector Store Setup

**Time**: 2-3 hours  
**Guide**: `guides/TASK_06_VECTOR_STORE_SETUP.md`

**What to do**:
1. Create `knowledge/vector_store_setup.py`
2. Upload scraped `.txt` files to OpenAI Files API (async, 30s timeout)
3. Create two Vector Stores:
   - Customer Vector Store
   - Banker Vector Store
4. Attach files to appropriate Vector Store based on topic
5. Get Vector Store IDs and add to `.env`:
   ```bash
   OPENAI_VECTOR_STORE_ID_CUSTOMER=vs_...
   OPENAI_VECTOR_STORE_ID_BANKER=vs_...
   ```
6. Register documents in Supabase `knowledge_documents` table
7. Test retrieval with a sample query

**Success Criteria**:
- [ ] Files uploaded to OpenAI
- [ ] Vector Stores created
- [ ] Files attached to Vector Stores
- [ ] Vector Store IDs in `.env`
- [ ] Documents registered in database
- [ ] Can retrieve documents via Chat Completions API

**Next**: Move to Task 7 (optional) or Phase 3

---

### Step 7: Task 7 - Synthetic Document Generation (Optional)

**Time**: 1-2 hours  
**Guide**: `guides/TASK_07_SYNTHETIC_DOCS.md` (summary in MASTER_INDEX.md)

**What to do**:
1. Identify content gaps
2. Create `knowledge/synthetic_generator.py`
3. Generate synthetic documents with clear labeling
4. Format with "SYNTHETIC CONTENT" markers
5. Upload to Vector Stores (same process as Task 6)
6. Register in database

**Success Criteria**:
- [ ] Synthetic documents clearly labeled
- [ ] Uploaded to Vector Stores
- [ ] Registered in database

**Next**: Move to Phase 3

---

## Phase 3: Pipeline Services (Tasks 8-13)

### Step 8: Task 8 - Intent Classification Service

**Time**: 2-3 hours  
**Guide**: `guides/TASK_08_INTENT_CLASSIFIER.md`

**What to do**:
1. Create `services/intent_classifier.py`
2. Implement async classification with 30s timeout:
   - Use OpenAI Chat Completions API
   - Structured JSON output
   - Intent taxonomy from constants
3. Add error handling (retries, timeouts)
4. Add structured logging (INFO for success, ERROR for failures)
5. Test with various queries

**Success Criteria**:
- [ ] Classifies queries correctly (async)
- [ ] Returns intent_name, intent_category, classification_reason
- [ ] Handles errors gracefully
- [ ] Logs all operations
- [ ] 30s timeout works

**Next**: Move to Task 9

---

### Step 9: Task 9 - Router Service

**Time**: 0.5-1 hour  
**Guide**: `guides/TASK_09_ROUTER.md` (summary in MASTER_INDEX.md)

**What to do**:
1. Create `services/router.py`
2. Implement routing logic:
   - HumanOnly → escalate (skip to step 6)
   - Automatable/Sensitive → continue to step 3
3. Test routing decisions

**Success Criteria**:
- [ ] Routes correctly based on intent_category
- [ ] Returns clear routing decision

**Next**: Move to Task 10

---

### Step 10: Task 10 - Retrieval Service

**Time**: 2-3 hours  
**Guide**: `guides/TASK_10_RETRIEVAL.md`

**What to do**:
1. Create `services/retrieval_service.py`
2. Implement async retrieval (30s timeout):
   - Use Chat Completions API with `file_search` tool
   - Select Vector Store by mode (customer/banker)
   - Extract retrieved chunks and citations
3. Add error handling (no results, timeouts)
4. Add structured logging
5. Test retrieval with sample queries

**Success Criteria**:
- [ ] Retrieves relevant chunks (async)
- [ ] Extracts citations correctly
- [ ] Handles no results gracefully
- [ ] Logs API calls with processing times
- [ ] 30s timeout works

**Next**: Move to Task 11

---

### Step 11: Task 11 - Response Generation Service

**Time**: 2-3 hours  
**Guide**: `guides/TASK_11_RESPONSE_GENERATOR.md` (summary in MASTER_INDEX.md)

**What to do**:
1. Create `services/response_generator.py`
2. Implement async response generation (30s timeout):
   - Use OpenAI Chat Completions API
   - Mode-specific system prompts
   - Include numbered citations [1], [2], etc.
   - Detect synthetic content and add disclaimers
3. Add error handling and logging
4. Test response generation

**Success Criteria**:
- [ ] Generates responses with citations (async)
- [ ] Citations numbered correctly
- [ ] Synthetic content detected and marked
- [ ] Logs API calls with processing times
- [ ] 30s timeout works

**Next**: Move to Task 12

---

### Step 12: Task 12 - Confidence Scoring Service

**Time**: 1-2 hours  
**Guide**: `guides/TASK_12_CONFIDENCE_SCORER.md` (summary in MASTER_INDEX.md)

**What to do**:
1. Create `services/confidence_scorer.py`
2. Implement async confidence scoring (30s timeout):
   - LLM self-assessment prompt
   - Parse confidence score (0.0-1.0)
   - Compare against threshold (0.68)
3. Add error handling (default to low confidence on failure)
4. Add structured logging
5. Test confidence scoring

**Success Criteria**:
- [ ] Scores confidence correctly (async)
- [ ] Compares against threshold
- [ ] Handles errors gracefully
- [ ] Logs operations
- [ ] 30s timeout works

**Next**: Move to Task 13

---

### Step 13: Task 13 - Escalation Handler Service

**Time**: 1-2 hours  
**Guide**: `guides/TASK_13_ESCALATION_HANDLER.md` (summary in MASTER_INDEX.md)

**What to do**:
1. Create `services/escalation_handler.py`
2. Implement all escalation triggers:
   - human_only, low_confidence, insufficient_evidence
   - conflicting_evidence, account_specific, security_fraud
   - financial_advice, legal_hardship, emotional_distress
   - repeated_misunderstanding, explicit_human_request
3. Generate user-friendly escalation messages
4. Add structured logging
5. Test all triggers

**Success Criteria**:
- [ ] All triggers detected
- [ ] Escalation messages user-friendly
- [ ] Logs escalations correctly

**Next**: Move to Phase 4

---

## Phase 4: UI & Integration (Tasks 14-18)

### Step 14: Task 14 - Logging Service

**Time**: 2-3 hours  
**Guide**: `guides/TASK_14_LOGGING.md`

**What to do**:
1. Create `services/logger.py`
2. Implement structured logging:
   - Use structlog (ERROR, WARN, INFO levels)
   - Log all pipeline steps with processing times
   - Log all API calls with details
3. Implement async logging to Supabase (30s timeout, non-blocking)
4. Add retry queue for failed logs
5. Test logging throughout pipeline

**Success Criteria**:
- [ ] Structured logging configured
- [ ] All interactions logged (async)
- [ ] API calls logged with processing times
- [ ] Non-blocking (doesn't block user response)
- [ ] Failed logs queued for retry

**Next**: Move to Task 15

---

### Step 15: Task 15 - Authentication Module

**Time**: 1 hour  
**Guide**: `guides/TASK_15_AUTH.md`

**What to do**:
1. Create `ui/auth.py`
2. Implement password authentication:
   - Password prompt at session start
   - Password: "rahul" (from Config.SESSION_PASSWORD)
   - Session state management
3. Integrate in `main.py`:
   ```python
   from ui.auth import check_authentication
   check_authentication()  # At start of main()
   ```
4. Test authentication flow

**Success Criteria**:
- [ ] Password prompt displayed
- [ ] Correct password grants access
- [ ] Incorrect password shows error
- [ ] Authentication persists for session

**Next**: Move to Task 16

---

### Step 16: Task 16 - Chat Interface UI

**Time**: 2-3 hours  
**Guide**: `guides/TASK_16_CHAT_UI.md` (summary in MASTER_INDEX.md)

**What to do**:
1. Create `ui/chat_interface.py`
2. Implement chat interface:
   - Authentication check (via auth.py)
   - Mode selection (Customer/Banker toggle)
   - Chat history (from Conversations API)
   - Message input
   - Response display with citations, confidence score
   - Loading indicators
3. Integrate with pipeline services
4. Test chat interface

**Success Criteria**:
- [ ] Authentication required
- [ ] Mode selection works
- [ ] Chat history maintained
- [ ] Citations displayed correctly
- [ ] Confidence score visible
- [ ] UI responsive

**Next**: Move to Task 17

---

### Step 17: Task 17 - KPI Dashboard UI

**Time**: 2-3 hours  
**Guide**: `guides/TASK_17_DASHBOARD.md` (summary in MASTER_INDEX.md)

**What to do**:
1. Create `ui/dashboard.py`
2. Implement dashboard with metrics:
   - Overall usage metrics
   - Mode breakdown
   - Resolution metrics (containment/escalation rates)
   - Intent frequency distribution
   - Escalation reason frequency
   - Confidence metrics
   - Performance metrics
3. Add charts and visualizations
4. Add filters (mode, date range, intent)
5. Test dashboard

**Success Criteria**:
- [ ] All metrics from PRD Section 5 displayed
- [ ] Charts render correctly
- [ ] Real-time updates work
- [ ] Filters function properly

**Next**: Move to Task 18

---

### Step 18: Task 18 - Main Application Integration

**Time**: 2-3 hours  
**Guide**: `guides/TASK_18_MAIN_APP.md` (summary in MASTER_INDEX.md)

**What to do**:
1. Update `main.py` with full pipeline orchestration:
   - Authentication check
   - Async pipeline execution (all 7 steps)
   - Error handling throughout
   - Timeout handling (30s default)
   - Page routing (Chat UI, Dashboard)
2. Integrate all services:
   - Intent classifier
   - Router
   - Retrieval service
   - Response generator
   - Confidence scorer
   - Escalation handler
   - Logger
3. Test end-to-end flow

**Success Criteria**:
- [ ] Full pipeline executes end-to-end (async)
- [ ] All 7 steps integrated correctly
- [ ] Error handling works
- [ ] Timeout handling works
- [ ] User can switch between Chat and Dashboard
- [ ] All interactions logged

**Next**: Move to Phase 5

---

## Phase 5: Testing & Documentation (Task 19)

### Step 19: Task 19 - Testing & Documentation

**Time**: 2-3 hours  
**Guide**: `guides/TASK_19_TESTING.md` (summary in MASTER_INDEX.md)

**What to do**:
1. Create `tests/` directory
2. Write unit tests for key services (including async tests)
3. Write integration tests for pipeline (async pipeline tests)
4. Write authentication tests
5. Write timeout handling tests
6. Write structured logging tests
7. Update README.md with:
   - Setup instructions
   - Environment variables
   - How to run
   - Architecture overview
8. Create DEPLOYMENT.md with deployment instructions
9. Run all tests

**Success Criteria**:
- [ ] Unit tests pass (including async)
- [ ] Integration tests pass
- [ ] Authentication tests pass
- [ ] Timeout tests pass
- [ ] Documentation complete

---

## Quick Start Checklist

Use this checklist to track your progress:

### Phase 1: Foundation
- [ ] Task 1: Project setup complete
- [ ] Task 2: Database setup complete
- [ ] Task 3: OpenAI setup complete

### Phase 2: Knowledge Base
- [ ] Task 4: Web scraping complete
- [ ] Task 6: Vector Store setup complete
- [ ] Task 7: Synthetic docs complete (optional)

### Phase 3: Pipeline
- [ ] Task 8: Intent classifier complete
- [ ] Task 9: Router complete
- [ ] Task 10: Retrieval service complete
- [ ] Task 11: Response generator complete
- [ ] Task 12: Confidence scorer complete
- [ ] Task 13: Escalation handler complete

### Phase 4: UI & Integration
- [ ] Task 14: Logging service complete
- [ ] Task 15: Authentication complete
- [ ] Task 16: Chat UI complete
- [ ] Task 17: Dashboard complete
- [ ] Task 18: Main app integration complete

### Phase 5: Testing
- [ ] Task 19: Testing & documentation complete

---

## Common Issues & Solutions

### Issue: OpenAI API Errors
**Solution**: 
- Check API key is correct
- Verify you have access to Vector Store API
- Check rate limits

### Issue: Supabase Connection Errors
**Solution**:
- Verify SUPABASE_URL and SUPABASE_KEY
- Check network connectivity
- Verify tables are created

### Issue: Async/Await Errors
**Solution**:
- Ensure you're using `async def` for async functions
- Use `await` for async calls
- Use `asyncio.run()` or `asyncio.gather()` for orchestration

### Issue: Timeout Errors
**Solution**:
- Check API_TIMEOUT is set (default 30s)
- Verify network connectivity
- Check OpenAI API status

### Issue: Import Errors
**Solution**:
- Ensure all `__init__.py` files exist
- Check virtual environment is activated
- Verify all dependencies installed

---

## Getting Help

1. **Check the Guides**: Each task has a detailed guide in `guides/` directory
2. **Check DETAILED_PLAN.md**: For detailed implementation specifications
3. **Check MASTER_INDEX.md**: For task summaries and references
4. **Check TASK_BREAKDOWN.md**: For task dependencies and organization

---

## Next Steps After Implementation

1. **Test End-to-End**: Run through complete user flows
2. **Populate Knowledge Base**: Ensure 50+ pages are ingested
3. **Monitor Logs**: Check structured logs for issues
4. **Review Metrics**: Check dashboard for accuracy
5. **Iterate**: Based on testing, make improvements

---

**Good luck with implementation!** 🚀
