# ContactIQ - Master Task Index

This document provides an index to all task guides for independent agents working on ContactIQ.

## Available Task Guides

### Foundation & Setup Tasks

- **[TASK_01_FOUNDATION.md](TASK_01_FOUNDATION.md)** ✅ Complete
  - Project structure, environment config, requirements.txt, basic Streamlit scaffold
  - Status: Full guide with code examples

- **[TASK_02_DATABASE.md](TASK_02_DATABASE.md)** ✅ Complete
  - Supabase setup, database schema, Supabase client wrapper
  - Status: Full guide with SQL schema and client code

- **[TASK_03_OPENAI_SETUP.md](TASK_03_OPENAI_SETUP.md)** ✅ Complete
  - OpenAI client wrapper, intent taxonomy constants, validators
  - Status: Full guide with intent definitions and validation code

### Knowledge Base Tasks

- **[TASK_04_KNOWLEDGE_SCRAPING.md](TASK_04_KNOWLEDGE_SCRAPING.md)** ✅ Complete
  - Web scraping infrastructure for ANZ public pages
  - Async implementation with aiohttp
  - BeautifulSoup for content extraction
  - Status: Full guide with implementation code
  - Reference: DETAILED_PLAN.md Section 8.1

- **[TASK_06_VECTOR_STORE_SETUP.md](TASK_06_VECTOR_STORE_SETUP.md)** ✅ Complete
  - OpenAI Vector Store setup with file upload and attachment
  - Multiple Vector Stores by topic (customer/banker)
  - File upload to OpenAI Files API and attachment to Vector Stores
  - Status: Full guide with implementation code
  - Reference: DETAILED_PLAN.md Section 7.1, TASK_10_RETRIEVAL.md

- **[TASK_07_SYNTHETIC_DOCS.md](TASK_07_SYNTHETIC_DOCS.md)** ✅ Complete
  - Synthetic document generation for content gaps
  - Clear labeling and assumptions documentation
  - Status: Full guide with implementation code
  - Reference: DETAILED_PLAN.md Section 8.2

### Pipeline Service Tasks

- **[TASK_08_INTENT_CLASSIFIER.md](TASK_08_INTENT_CLASSIFIER.md)** ✅ Complete
  - Intent classification using OpenAI gpt-4o-mini
  - Structured JSON output with validation
  - Status: Full guide with implementation code

- **[TASK_09_ROUTER.md](TASK_09_ROUTER.md)** ✅ Complete
  - Routing logic based on intent_category
  - Simple conditional logic (HumanOnly → escalate, others → continue)
  - Status: Full guide with implementation code
  - Reference: DETAILED_PLAN.md Section 7.2

- **[TASK_10_RETRIEVAL.md](TASK_10_RETRIEVAL.md)** ✅ Complete
  - Retrieval service using OpenAI Vector Store + Chat Completions API with file_search tool
  - Direct API calls for semantic retrieval
  - Status: Full guide with implementation code

- **[TASK_11_RESPONSE_GENERATOR.md](TASK_11_RESPONSE_GENERATOR.md)** ✅ Complete
  - Response generation using OpenAI gpt-4o-mini (async)
  - Citation formatting and synthetic content detection
  - Mode-specific prompts (Customer vs Banker)
  - Status: Full guide with implementation code
  - Reference: DETAILED_PLAN.md Section 7.4

- **[TASK_12_CONFIDENCE_SCORER.md](TASK_12_CONFIDENCE_SCORER.md)** ✅ Complete
  - LLM self-assessment for confidence scoring (async)
  - Threshold comparison (> 0.68)
  - Safe defaults (low confidence on errors)
  - Status: Full guide with implementation code
  - Reference: DETAILED_PLAN.md Section 7.5

- **[TASK_13_ESCALATION_HANDLER.md](TASK_13_ESCALATION_HANDLER.md)** ✅ Complete
  - Escalation handler with all 11 trigger types
  - User-friendly escalation messages (mode-specific)
  - Trigger detection logic
  - Status: Full guide with implementation code
  - Reference: DETAILED_PLAN.md Section 7.6

- **[TASK_14_LOGGING.md](TASK_14_LOGGING.md)** ✅ Complete
  - Logging service to Supabase
  - Pipeline step tracking
  - Status: Full guide with implementation code

### UI Tasks

- **[TASK_15_AUTH.md](TASK_15_AUTH.md)** ✅ Complete
  - Simple password authentication at session start
  - Password prompt UI, session state management
  - Status: Full guide with implementation code
  - Reference: DETAILED_PLAN.md Section 9.1

- **[TASK_16_CHAT_UI.md](TASK_16_CHAT_UI.md)** ✅ Complete
  - Streamlit chat interface
  - Mode selection, chat history, citations display
  - Authentication integration
  - Full pipeline integration
  - Status: Full guide with implementation code
  - Reference: DETAILED_PLAN.md Section 9.2

- **[TASK_17_DASHBOARD.md](TASK_17_DASHBOARD.md)** ✅ Complete
  - KPI dashboard with metrics from PRD Section 5
  - Charts, filters, real-time updates
  - All 7 metric categories implemented
  - Status: Full guide with implementation code
  - Reference: DETAILED_PLAN.md Section 9.3, PRD.md Section 5

- **[TASK_18_MAIN_APP.md](TASK_18_MAIN_APP.md)** ✅ Complete
  - Main application integration
  - Async pipeline orchestration (all 7 steps)
  - Authentication integration
  - Error handling and timeout management
  - Status: Full guide with implementation code
  - Reference: DETAILED_PLAN.md Section 7, HIGH_LEVEL_PLAN.md Section 3.1

### Testing & Documentation

- **[TASK_19_TESTING.md](TASK_19_TESTING.md)** ✅ Complete
  - Unit tests, integration tests (including async)
  - Authentication, timeout, and logging tests
  - Documentation updates (README, DEPLOYMENT)
  - Status: Full guide with test examples
  - Reference: DETAILED_PLAN.md Section 12

## Task Summaries (For Tasks Without Full Guides)

### TASK_04: Knowledge Scraping

**Objective**: Scrape ANZ public pages and extract content for knowledge base.

**Key Requirements**:
- Use BeautifulSoup to scrape ANZ public pages
- Extract main content (remove navigation, footer, etc.)
- Extract metadata (title, URL, date)
- Format content as plain text (.txt) files
- File naming: Sanitized page title (e.g., "ANZ Fee Schedule" → "anz_fee_schedule.txt")
- Include source URL in each .txt file (in metadata header)
- Save files with UTF-8 encoding
- Chunk large documents if needed (naming: `{title}_chunk_{n}.txt`)

**Deliverable**: `knowledge/ingestor.py`

**File Format**:
- Format: `.txt` (plain text)
- Encoding: UTF-8
- Structure: Metadata header (Title, Source URL, Retrieval Date) + content + footer
- Naming: Sanitized title (remove special chars, limit length)

**Reference**: See `DETAILED_PLAN.md` Section 7.1 for details on web scraping infrastructure.

---

### TASK_06: Vector Store Setup

**Objective**: Create OpenAI Vector Stores and attach uploaded files for knowledge base storage.

**Key Requirements**:
- Create Vector Stores using OpenAI API (one per topic: customer/banker)
- Upload files via Files API
- Attach files to Vector Stores (OpenAI automatically processes them)
- Track documents in Supabase knowledge_documents table

**Deliverable**: `knowledge/vector_store_setup.py`

**Reference**: 
- See `TASK_10_RETRIEVAL.md` for how Vector Stores are used
- See `guides/TASK_06_VECTOR_STORE_SETUP.md` for full implementation guide
- OpenAI Vector Store API documentation
- `DETAILED_PLAN.md` Section 7.1

**Key Code Pattern**:
```python
from openai import OpenAI
client = OpenAI(api_key=Config.OPENAI_API_KEY)

# Create Vector Store
vector_store = client.beta.vector_stores.create(
    name="Customer Knowledge Base",
    description="Vector Store for customer-facing content"
)

# Upload file (.txt format, UTF-8 encoded)
file = client.files.create(
    file=open("anz_fee_schedule.txt", "rb"),
    purpose="assistants"
)

# Attach file to Vector Store
client.beta.vector_stores.files.create(
    vector_store_id=vector_store.id,
    file_ids=[file.id]
)

# Note: OpenAI automatically parses, chunks, and embeds files when attached
```

---

### TASK_07: Synthetic Documents

**Objective**: Create synthetic documents to fill content gaps.

**Key Requirements**:
- Identify gaps in public content
- Create synthetic documents with clear labeling
- Document assumptions separately
- Format: Title, Label (SYNTHETIC), Content, Assumptions, Source
- Upload to OpenAI Files API and attach to Vector Store

**Deliverable**: `knowledge/synthetic_generator.py`

**Reference**: See `DETAILED_PLAN.md` Section 7.2 for synthetic document format and requirements.

---

### TASK_09: Router

**Objective**: Implement routing logic based on intent_category.

**Key Requirements**:
- Simple conditional logic:
  - `HumanOnly` → escalate (skip to step 6)
  - `Automatable` or `Sensitive` → continue to step 3 (retrieval)
- Return routing decision

**Deliverable**: `services/router.py`

**Reference**: See `DETAILED_PLAN.md` Section 6.2 for router logic.

**Implementation**:
```python
def route(intent_category: str) -> Dict[str, Any]:
    if intent_category == "human_only":
        return {"route": "escalate", "skip_to_step": 6}
    elif intent_category in ["automatable", "sensitive"]:
        return {"route": "continue", "next_step": 3}
    else:
        # Default to escalate
        return {"route": "escalate", "skip_to_step": 6}
```

---

### TASK_11: Response Generator

**Objective**: Generate response with citations using OpenAI gpt-4o-mini.

**Key Requirements**:
- Use OpenAI Chat API (gpt-4o-mini)
- Include retrieved chunks as context
- Generate response with numbered citations [1], [2], etc.
- Detect synthetic content and add disclaimers
- Format citations as structured data

**Deliverable**: `services/response_generator.py`

**Reference**: See `DETAILED_PLAN.md` Section 6.4 for response generation requirements and prompts.

**Key Prompts** (from DETAILED_PLAN.md):
- Customer mode: Simple, explanatory tone
- Banker mode: Technical, policy-focused tone
- Both: Include numbered citations, detect synthetic content

---

### TASK_12: Confidence Scorer

**Objective**: Calculate confidence score using LLM self-assessment.

**Key Requirements**:
- Ask model "How confident are you in this response?"
- Parse confidence score (0.0-1.0)
- Compare against threshold (0.68)
- Return score and threshold decision

**Deliverable**: `services/confidence_scorer.py`

**Reference**: See `DETAILED_PLAN.md` Section 6.5 for confidence scoring prompt and logic.

**Key Prompt Template**:
```
"On a scale of 0.0 to 1.0, how confident are you that the response 
you provided accurately answers the user's query based solely on 
the retrieved context? Consider: completeness, accuracy, relevance, 
and whether all information needed is present.

User Query: {user_query}
Response: {response_text}

Respond with only a JSON object: {"confidence": 0.85, "reasoning": "..."}"
```

---

### TASK_13: Escalation Handler

**Objective**: Handle escalations with user-friendly messages.

**Key Requirements**:
- Detect all escalation triggers:
  - human_only, low_confidence, insufficient_evidence, conflicting_evidence
  - account_specific, security_fraud, financial_advice, legal_hardship
  - emotional_distress, repeated_misunderstanding, explicit_human_request
- Generate user-friendly escalation messages
- Log escalation reason

**Deliverable**: `services/escalation_handler.py`

**Reference**: See user requirements for escalation triggers and `DETAILED_PLAN.md` Section 6.6 for escalation logic.

---

### TASK_15: Authentication

**Objective**: Implement simple password authentication at session start.

**Key Requirements**:
- Password prompt displayed before accessing any features
- Password: "rahul" (configurable via SESSION_PASSWORD env var)
- Session state management (Streamlit session_state)
- Password validation
- Error messaging for incorrect password

**Deliverable**: `ui/auth.py`

**Reference**: See `DETAILED_PLAN.md` Section 9.1 for authentication requirements.

**Key Implementation**:
- `check_authentication()` function
- Streamlit session_state for authentication state
- Password input with hidden characters
- Clean, centered UI

---

### TASK_16: Chat UI

**Objective**: Implement Streamlit chat interface.

**Key Requirements**:
- Authentication check (via auth.py) before accessing interface
- Mode selection (Customer/Banker toggle)
- Chat history display (from OpenAI Conversations API)
- Message input
- Response display with:
  - Response text
  - Numbered citations [1], [2], etc.
  - Confidence score (visible to user)
  - Escalation messages
- Loading indicators

**Deliverable**: `ui/chat_interface.py`

**Reference**: See `DETAILED_PLAN.md` Section 9.2 for UI requirements.

**Key Streamlit Components**:
- `st.radio` or `st.selectbox` for mode selection
- `st.chat_message` for chat history
- `st.chat_input` for message input
- Display citations as numbered references
- Show confidence score prominently

---

### TASK_17: Dashboard

**Objective**: Implement KPI dashboard with metrics from PRD Section 5.

**Key Requirements**:
- Display all metrics from PRD Section 5:
  - Overall usage metrics (total conversations, interactions)
  - Mode breakdown (customer vs banker)
  - Resolution metrics (containment rate, escalation rate)
  - Intent frequency distribution
  - Escalation reason frequency
  - Confidence metrics (average, by intent, distribution)
  - Performance metrics (processing time, low resolution intents)
- Charts: bar, line, pie charts
- Filters: mode, date range, intent
- Real-time updates

**Deliverable**: `ui/dashboard.py`

**Reference**: 
- PRD.md Section 5 (Success Metrics)
- DETAILED_PLAN.md Section 8.2 (Dashboard requirements)
- Use SupabaseClient.get_metrics() from Task 2

**Key Metrics** (from PRD Section 5):
- Total conversations
- Containment rate (resolved without escalation)
- Escalation rate
- Intent frequency distribution
- Usage split (Customer vs Banker)
- Escalation reason frequency
- Average confidence score by intent
- Intents with lowest resolution rates

---

### TASK_18: Main App Integration

**Objective**: Integrate all services into main application.

**Key Requirements**:
- Orchestrate all 7 pipeline steps:
  1. Intent Classification
  2. Router
  3. Retrieval
  4. Response Generation
  5. Confidence Check
  6. Escalation Handler
  7. Logging
- Error handling at each step
- Streamlit page routing (Chat UI, Dashboard)
- Session management

**Deliverable**: `main.py` (update from Task 1)

**Reference**: 
- DETAILED_PLAN.md Section 6 (Linear Pipeline)
- HIGH_LEVEL_PLAN.md Section 9 (Pipeline Steps)
- All service guides

**Pipeline Flow**:
```python
def process_query(user_query, assistant_mode, session_id):
    logger = get_logger()
    logger.start_timer()
    
    # Step 1: Intent Classification
    intent_data = classify_intent(user_query, assistant_mode)
    logger.log_interaction(step_1_intent_completed=True, ...)
    
    # Step 2: Router
    route_decision = route(intent_data["intent_category"])
    logger.log_interaction(step_2_routing_decision=route_decision["route"], ...)
    
    if route_decision["route"] == "escalate":
        # Step 6: Escalation
        escalation = handle_escalation(...)
        logger.log_interaction(outcome="escalated", ...)
        return escalation
    
    # Step 3: Retrieval
    retrieval_result = retrieve_chunks(user_query, assistant_mode)
    logger.log_interaction(step_3_retrieval_performed=True, ...)
    
    if not retrieval_result["success"] or not retrieval_result["retrieved_chunks"]:
        # Escalate - insufficient evidence
        escalation = handle_escalation(trigger_type="insufficient_evidence", ...)
        logger.log_interaction(outcome="escalated", ...)
        return escalation
    
    # Step 4: Response Generation
    response = generate_response(user_query, retrieval_result, assistant_mode)
    logger.log_interaction(step_4_response_generated=True, ...)
    
    # Step 5: Confidence Check
    confidence_result = score_confidence(response, retrieval_result, user_query, assistant_mode)
    logger.log_interaction(step_5_confidence_score=confidence_result["confidence_score"], ...)
    
    if not confidence_result["meets_threshold"]:
        # Step 6: Escalation
        escalation = handle_escalation(trigger_type="low_confidence", ...)
        logger.log_interaction(outcome="escalated", ...)
        return escalation
    
    # Step 7: Logging
    logger.log_interaction(
        outcome="resolved",
        confidence_score=confidence_result["confidence_score"],
        response_text=response["response_text"],
        citations=response["citations"],
        ...
    )
    
    return response
```

---

### TASK_19: Testing & Documentation

**Objective**: Create tests and update documentation.

**Key Requirements**:
- Unit tests for key services (intent classifier, router, etc.)
- Integration tests for full pipeline
- README updates
- Deployment guide
- Error handling validation

**Deliverable**: `tests/` directory, updated README.md, DEPLOYMENT.md

**Reference**: See `DETAILED_PLAN.md` Section 11 for testing strategy.

---

## Getting Started

1. **Read the Master Documents**:
   - `HIGH_LEVEL_PLAN.md` - System architecture overview
   - `DETAILED_PLAN.md` - Detailed implementation plan
   - `TASK_BREAKDOWN.md` - Task dependencies and organization

2. **Identify Your Task**:
   - Check `TASK_BREAKDOWN.md` for task assignments
   - Find your task guide in this index

3. **Review Prerequisites**:
   - Each task guide lists prerequisites
   - Ensure dependencies are completed

4. **Follow the Guide**:
   - Complete guides have full implementation code
   - Summary tasks reference DETAILED_PLAN.md sections
   - Follow validation checklists

5. **Integrate Your Work**:
   - Check integration points in your task guide
   - Test integration with other tasks
   - Update documentation

## Questions or Issues?

- Review DETAILED_PLAN.md for detailed requirements
- Check HIGH_LEVEL_PLAN.md for architecture decisions
- Review PRD.md and README.md for product requirements
- Check existing code for patterns and conventions
