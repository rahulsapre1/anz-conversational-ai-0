# ContactIQ - Task Breakdown for Independent Agents

This document breaks down the ContactIQ project into independent tasks that can be worked on by separate agents or developers.

## Task Organization

Each task is designed to be:
- **Independent**: Can be developed without blocking other tasks
- **Testable**: Has clear success criteria
- **Well-Documented**: Includes guidance in separate .md files
- **Integrated**: Has clear integration points with other tasks

## Task List

### Task 1: Project Foundation & Configuration
**Agent Guide**: `guides/TASK_01_FOUNDATION.md`
**Dependencies**: None
**Deliverables**:
- Project structure (flattish)
- Environment configuration (.env.example with SESSION_PASSWORD, API_TIMEOUT)
- Requirements.txt (including async and logging libraries)
- Config module (config.py with new settings)
- Basic Streamlit scaffold (main.py)
- Structured logging setup (structlog)
- .gitignore

**Success Criteria**:
- [ ] Project structure matches DETAILED_PLAN.md Section 1
- [ ] Environment variables loaded correctly (including SESSION_PASSWORD, API_TIMEOUT)
- [ ] Streamlit app runs without errors
- [ ] All dependencies installable from requirements.txt (including aiohttp, structlog, httpx)
- [ ] Structured logging configured (ERROR, WARN, INFO levels)

---

### Task 2: Database Schema & Supabase Setup
**Agent Guide**: `guides/TASK_02_DATABASE.md`
**Dependencies**: Task 1 (for project structure)
**Deliverables**:
- Supabase project setup instructions
- SQL schema migration (schema.sql)
- Supabase client wrapper (database/supabase_client.py)
- Connection testing

**Success Criteria**:
- [ ] Supabase project created and accessible
- [ ] All tables created (interactions, escalations, knowledge_documents)
- [ ] Indexes created
- [ ] Client wrapper can connect and insert test data
- [ ] Schema matches DETAILED_PLAN.md Section 5

---

### Task 3: OpenAI Client Setup & Intent Taxonomy
**Agent Guide**: `guides/TASK_03_OPENAI_SETUP.md`
**Dependencies**: Task 1
**Deliverables**:
- OpenAI client wrapper (utils/openai_client.py)
- Intent taxonomy constants (utils/constants.py)
- Intent validation helpers (utils/validators.py)

**Success Criteria**:
- [ ] OpenAI client initialized with gpt-4o-mini
- [ ] Intent taxonomy defined (Customer + Banker intents)
- [ ] Validation functions work for intent schema
- [ ] Constants module exports all required values

---

### Task 4: Knowledge Base Ingestion - Web Scraping
**Agent Guide**: `guides/TASK_04_KNOWLEDGE_SCRAPING.md`
**Dependencies**: Task 1, Task 3
**Deliverables**:
- Web scraping module (knowledge/ingestor.py)
- Async implementation with concurrent URL fetching (aiohttp)
- ANZ public page scraping (async, 30s timeout per URL)
- Content extraction and cleaning
- Metadata extraction (title, URL, date)
- Format content as .txt files with metadata header
- File naming using sanitized titles
- Source URL included in each file
- Structured logging (INFO for success, ERROR for failures, processing_time_ms)

**Success Criteria**:
- [ ] Can scrape ANZ public pages (async with concurrent requests)
- [ ] Extracts clean content (removes nav, footer)
- [ ] Extracts metadata correctly (title, URL, date)
- [ ] Formats content as .txt files with proper structure
- [ ] Sanitizes titles for file naming
- [ ] Includes source URL in file metadata
- [ ] Handles errors gracefully (with timeout handling)
- [ ] Timeout handling (30s per URL)
- [ ] Outputs .txt files ready for OpenAI upload (UTF-8 encoding)
- [ ] Logs all operations with structured logging

---

### Task 6: Knowledge Base Ingestion - OpenAI Vector Store Setup
**Agent Guide**: `guides/TASK_06_VECTOR_STORE_SETUP.md`
**Dependencies**: Task 1, Task 3, Task 4
**Deliverables**:
- Vector Store creation script
- File upload to OpenAI Files API
- File attachment to Vector Stores
- Multiple Vector Stores by topic (customer/banker collections)
- Document tracking in Supabase

**Success Criteria**:
- [ ] Vector Stores created for customer and banker content
- [ ] Documents uploaded to OpenAI Files API
- [ ] Files attached to Vector Stores (OpenAI processes automatically)
- [ ] Document metadata tracked in Supabase knowledge_documents table
- [ ] Vector Store IDs configured in .env
- [ ] Can retrieve chunks using Vector Store IDs (test with Task 10)

---

### Task 7: Knowledge Base Ingestion - Synthetic Documents
**Agent Guide**: `guides/TASK_07_SYNTHETIC_DOCS.md`
**Dependencies**: Task 6
**Deliverables**:
- Synthetic document generator (knowledge/synthetic_generator.py)
- Gap identification logic
- Document creation with proper labeling
- Assumptions documentation

**Success Criteria**:
- [ ] Synthetic documents clearly labeled
- [ ] Assumptions documented
- [ ] Documents uploaded to OpenAI Files API
- [ ] Documents attached to appropriate Vector Store
- [ ] Marked in metadata as "synthetic"
- [ ] Format matches specification (see DETAILED_PLAN.md)

---

### Task 8: Intent Classification Service
**Agent Guide**: `guides/TASK_08_INTENT_CLASSIFIER.md`
**Dependencies**: Task 1, Task 3
**Deliverables**:
- Intent classifier (services/intent_classifier.py)
- Async implementation with 30s timeout
- Structured output prompt with JSON schema
- Intent taxonomy integration
- Error handling (malformed JSON, API failures, timeouts)
- Structured logging (INFO for success, ERROR for failures, processing_time_ms)

**Success Criteria**:
- [ ] Classifies user queries into correct intents (async)
- [ ] Returns intent_name, intent_category, classification_reason
- [ ] Handles malformed JSON (returns None, user messaging, log ERROR)
- [ ] Retries on API failures (3 attempts with 30s timeout each)
- [ ] Handles timeouts (30s, log ERROR, escalate)
- [ ] Defaults unknown categories to "human_only"
- [ ] Logs all operations with structured logging (processing_time_ms)

---

### Task 9: Router Service
**Agent Guide**: `guides/TASK_09_ROUTER.md`
**Dependencies**: Task 8
**Deliverables**:
- Router service (services/router.py)
- Routing logic based on intent_category
- Decision output (escalate or continue)

**Success Criteria**:
- [ ] Routes HumanOnly → escalate (skip to step 6)
- [ ] Routes Automatable/Sensitive → continue to step 3
- [ ] Returns clear routing decision
- [ ] Handles all intent categories correctly

---

### Task 10: Retrieval Service (Vector Store + Chat Completions API)
**Agent Guide**: `guides/TASK_10_RETRIEVAL.md`
**Dependencies**: Task 6, Task 8
**Deliverables**:
- Retrieval service (services/retrieval_service.py)
- Async implementation with 30s timeout
- OpenAI Chat Completions API integration (async)
- Vector Store selection by mode (customer/banker)
- file_search tool execution for retrieval
- Citation extraction from tool response
- Structured logging (INFO for API calls, processing_time_ms)

**Success Criteria**:
- [ ] Uses Chat Completions API with file_search tool (async)
- [ ] References correct Vector Store ID by mode
- [ ] Retrieves relevant chunks with citations
- [ ] Handles no results (log WARN, escalate with user messaging)
- [ ] Error handling with retries (3 attempts, 30s timeout each)
- [ ] Handles timeouts (30s, log ERROR, escalate)
- [ ] Extracts citations correctly from API response
- [ ] Logs all API calls with processing times (structured logging)

---

### Task 11: Response Generation Service
**Agent Guide**: `guides/TASK_11_RESPONSE_GENERATOR.md`
**Dependencies**: Task 10, Task 3
**Deliverables**:
- Response generator (services/response_generator.py)
- Async implementation with 30s timeout
- System prompts (Customer/Banker)
- Response generation with citations (async)
- Synthetic content detection and disclaimers
- Numbered citation formatting
- Structured logging (INFO for API calls, processing_time_ms)

**Success Criteria**:
- [ ] Generates responses using gpt-4o-mini (async, 30s timeout)
- [ ] Includes numbered citations [1], [2], etc.
- [ ] Detects synthetic content and adds disclaimers
- [ ] Response format matches specification
- [ ] Citations extracted as structured data
- [ ] Handles timeouts (30s, log ERROR, escalate)
- [ ] Logs all API calls with processing times

---

### Task 12: Confidence Scoring Service
**Agent Guide**: `guides/TASK_12_CONFIDENCE_SCORER.md`
**Dependencies**: Task 11
**Deliverables**:
- Confidence scorer (services/confidence_scorer.py)
- Async implementation with 30s timeout
- LLM self-assessment prompt (async)
- Confidence score parsing (0.0-1.0)
- Threshold comparison (> 0.68)
- Decision output
- Structured logging (INFO for scores, WARN for low scores, ERROR for failures)

**Success Criteria**:
- [ ] Asks model for confidence assessment (async, 30s timeout)
- [ ] Parses confidence score correctly
- [ ] Compares against threshold (0.68)
- [ ] Returns score and threshold decision
- [ ] Handles parsing errors gracefully (log ERROR, default to low confidence)
- [ ] Handles timeouts (30s, log ERROR, default to low confidence)
- [ ] Logs all operations with processing times

---

### Task 13: Escalation Handler Service
**Agent Guide**: `guides/TASK_13_ESCALATION_HANDLER.md`
**Dependencies**: Task 8, Task 9, Task 12
**Deliverables**:
- Escalation handler (services/escalation_handler.py)
- All escalation trigger detection:
  - HumanOnly category
  - Low confidence
  - Insufficient evidence
  - Conflicting evidence
  - Account-specific requests
  - Security/fraud indicators
  - Financial advice framing
  - Legal/hardship signals
  - Emotional distress/urgent language
  - Repeated misunderstanding
  - Explicit human request
- User-friendly escalation messages

**Success Criteria**:
- [ ] All escalation triggers detected
- [ ] Generates appropriate escalation messages
- [ ] Messages are user-friendly (no technical jargon)
- [ ] Provides next-step guidance
- [ ] Logs escalation reason correctly

---

### Task 14: Logging Service
**Agent Guide**: `guides/TASK_14_LOGGING.md`
**Dependencies**: Task 2, Task 8, Task 9, Task 10, Task 11, Task 12, Task 13
**Deliverables**:
- Logging service (services/logger.py)
- Structured logging setup (structlog with ERROR, WARN, INFO)
- Interaction logging to Supabase (async, 30s timeout, non-blocking)
- Step-by-step pipeline logging with processing times
- API call logging with details (endpoint, tokens, processing_time_ms)
- Escalation logging
- Error logging
- Async retry queue for failed logs

**Success Criteria**:
- [ ] Structured logging configured (ERROR, WARN, INFO levels)
- [ ] Logs all interactions with complete fields (async)
- [ ] Logs each pipeline step completion with processing_time_ms
- [ ] Logs all API calls with processing times and details
- [ ] Logs escalations with reasons
- [ ] Handles database failures gracefully (async retry queue)
- [ ] Timeout handling (30s, non-blocking)
- [ ] All required fields populated (see schema.sql)

---

### Task 15: Authentication Module
**Agent Guide**: `guides/TASK_15_AUTH.md`
**Dependencies**: Task 1
**Deliverables**:
- Authentication module (ui/auth.py)
- Password prompt UI
- Session state management
- Password validation ("rahul" from config)

**Success Criteria**:
- [ ] Password prompt displayed at session start
- [ ] Password validation works (correct password grants access)
- [ ] Incorrect password shows error message
- [ ] Authenticated state persists for session
- [ ] Main interface only accessible after authentication

---

### Task 16: Chat Interface UI
**Agent Guide**: `guides/TASK_16_CHAT_UI.md`
**Dependencies**: Task 14, Task 15, Task 10 (for Conversations API)
**Deliverables**:
- Chat interface (ui/chat_interface.py)
- Authentication check (via auth.py)
- Mode selection (Customer/Banker toggle)
- Chat history display (from Conversations API)
- Message input
- Response display with:
  - Response text
  - Numbered citations
  - Confidence score (visible)
  - Escalation messages
- Loading indicators

**Success Criteria**:
- [ ] Authentication required before accessing interface
- [ ] Mode selection works
- [ ] Chat history maintained via Conversations API
- [ ] Citations displayed as numbered references
- [ ] Confidence score visible to user
- [ ] Escalation messages display correctly
- [ ] UI is responsive and user-friendly

---

### Task 17: KPI Dashboard UI
**Agent Guide**: `guides/TASK_17_DASHBOARD.md`
**Dependencies**: Task 2, Task 14
**Deliverables**:
- Dashboard (ui/dashboard.py)
- Metrics calculation from Supabase
- Visualizations:
  - Overall usage metrics
  - Mode breakdown
  - Resolution metrics (containment/escalation rates)
  - Intent frequency distribution
  - Escalation reason frequency
  - Confidence metrics
  - Performance metrics
- Real-time updates
- Filters (mode, date range, intent)

**Success Criteria**:
- [ ] All metrics from PRD Section 5 displayed
- [ ] Charts render correctly
- [ ] Real-time updates work
- [ ] Filters function properly
- [ ] Data matches database records

---

### Task 18: Main Application Integration
**Agent Guide**: `guides/TASK_18_MAIN_APP.md`
**Dependencies**: All previous tasks
**Deliverables**:
- Main application (main.py)
- Authentication integration (via auth.py)
- Async pipeline orchestration (all 7 steps)
- Integration of all services (async where applicable)
- Error handling across pipeline (with timeout handling)
- Streamlit page routing (Chat UI, Dashboard)
- Timeout handling throughout (30s default)

**Success Criteria**:
- [ ] Authentication required before accessing any features
- [ ] Full pipeline executes end-to-end (async)
- [ ] All 7 steps integrated correctly with async support
- [ ] Error handling works at each step (including timeouts)
- [ ] Timeout handling (30s) implemented throughout
- [ ] User can switch between Chat and Dashboard
- [ ] Session management works
- [ ] All interactions logged (async, non-blocking)

---

### Task 19: Testing & Documentation
**Agent Guide**: `guides/TASK_19_TESTING.md`
**Dependencies**: All tasks
**Deliverables**:
- Unit tests for key services
- Integration tests for pipeline
- README updates
- Deployment guide
- Error handling validation

**Success Criteria**:
- [ ] Unit tests pass for all services
- [ ] Integration tests validate full pipeline
- [ ] Documentation complete
- [ ] Error scenarios tested

---

## Task Dependency Graph

```
Task 1 (Foundation)
  ├─> Task 2 (Database)
  ├─> Task 3 (OpenAI Setup)
  ├─> Task 4 (Knowledge Scraping)
  ├─> Task 8 (Intent Classifier)
  └─> Task 15 (Authentication)

Task 2 (Database)
  └─> Task 14 (Logging)

Task 3 (OpenAI Setup)
  ├─> Task 4 (Knowledge Scraping)
  ├─> Task 8 (Intent Classifier)
  └─> Task 10 (Retrieval)

Task 4 (Knowledge Scraping)
  └─> Task 6 (Assistants Setup)

Task 6 (Assistants Setup)
  ├─> Task 7 (Synthetic Docs)
  └─> Task 10 (Retrieval)

Task 7 (Synthetic Docs)
  └─> (End of ingestion pipeline)

Task 8 (Intent Classifier)
  ├─> Task 9 (Router)
  └─> Task 13 (Escalation)

Task 9 (Router)
  └─> Task 10 (Retrieval)

Task 10 (Retrieval)
  └─> Task 11 (Response Generator)

Task 11 (Response Generator)
  └─> Task 12 (Confidence Scorer)

Task 12 (Confidence Scorer)
  └─> Task 13 (Escalation)

Task 13 (Escalation)
  └─> Task 14 (Logging)

Task 14 (Logging)
  └─> Task 18 (Main App)

Task 15 (Authentication)
  └─> Task 16 (Chat UI)

Task 16 (Chat UI)
  └─> Task 18 (Main App)

Task 17 (Dashboard)
  └─> Task 18 (Main App)

Task 16 (Dashboard)
  └─> Task 17 (Main App)

Task 18 (Main App)
  └─> Task 19 (Testing)
```

## Parallelization Opportunities

**Phase 1 (Foundation)**: Tasks 1-3 can start in parallel (with Task 1 first)
**Phase 2 (Knowledge Base)**: Tasks 4, 6-7 are sequential but can overlap slightly
**Phase 3 (Pipeline Services)**: Tasks 8-13 are sequential
**Phase 4 (UI & Integration)**: Tasks 14, 15, 16, 17 can be parallel after dependencies met, then Task 18 integrates

## Agent Assignment Recommendation

- **Agent 1**: Tasks 1, 2, 3 (Foundation & Setup)
- **Agent 2**: Tasks 4, 6, 7 (Knowledge Base)
- **Agent 3**: Tasks 8, 9, 10, 11, 12, 13 (Pipeline Services)
- **Agent 4**: Tasks 14, 15, 16, 17, 18, 19 (Logging, Authentication, UI, Dashboard, Integration, Testing)

Or:
- **Agent 1**: Tasks 1-4, 6-7 (Foundation + Knowledge)
- **Agent 2**: Tasks 8-13 (Pipeline)
- **Agent 3**: Tasks 14-18 (UI + Integration + Testing)
