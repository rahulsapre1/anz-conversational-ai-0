# ContactIQ - High-Level Technical Plan

## 1. System Architecture Overview

### 1.1 Architecture Pattern
**Linear Intent-First Pipeline Architecture**

```
┌─────────────────────────────────────────┐
│         Streamlit Frontend              │
│  (Customer/Banker Mode Selection)      │
│  (Chat Interface + KPI Dashboard)      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Linear AI Pipeline                 │
│                                         │
│  1. Intent Classification               │
│     (OpenAI Chat Model)                 │
│         ↓                               │
│  2. Router                              │
│     (Automatable/Sensitive/HumanOnly)   │
│         ↓                               │
│  3. Retrieval                           │
│     (Vector Store + Chat Completions)   │
│         ↓                               │
│  4. Response Generation                 │
│     (OpenAI Chat Model + Citations)     │
│         ↓                               │
│  5. Confidence Check                    │
│     (Threshold Evaluation)              │
│         ↓                               │
│  6. Escalation Handler                  │
│     (If threshold not met)              │
│         ↓                               │
│  7. Logging Service                     │
│     (Interaction Logging)               │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Data Layer                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │ OpenAI       │  │ Supabase     │   │
│  │ Vector Store │  │ Postgres     │   │
│  │ + Chat API   │  │ (Logging)    │   │
│  │ (Knowledge)  │  │ (Metrics)    │   │
│  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────┘
```

### 1.2 Core Components

1. **Authentication (ui/auth.py)**
   - Simple password authentication at session start
   - Password: "rahul" (configurable)
   - Session state management
   - Password prompt before accessing features

2. **Frontend (Streamlit)**
   - Password authentication (via auth.py)
   - Mode selection UI (Customer/Banker toggle)
   - Chat interface with conversation history
   - KPI dashboard (real-time metrics)
   - Response display with citations and confidence scores
   - Escalation notifications

2. **Intent Classification Service**
   - OpenAI Chat Model (GPT-4 or GPT-3.5-turbo)
   - Structured output: intent_name, intent_category, classification_reason
   - JSON schema enforcement for consistent parsing

3. **Routing Service**
   - Decision logic based on intent_category
   - Three categories: Automatable / Sensitive / HumanOnly
   - Mode-specific thresholds (Customer vs Banker)
   - Immediate routing decisions (no complex evaluation)

4. **Retrieval Service (OpenAI Vector Store + Chat Completions API)**
   - Vector Store for managed knowledge storage (no vector DB management)
   - Chat Completions API with `file_search` tool for semantic retrieval
   - Returns relevant chunks with metadata and citations
   - Handles ANZ public content + labeled synthetic documents

5. **Response Generation Service**
   - OpenAI Chat Model (GPT-4 or GPT-3.5-turbo)
   - Retrieval-augmented generation with citations
   - Mode-specific tone (simple for Customer, technical for Banker)
   - Disclaimer injection when applicable

6. **Confidence Scoring Service**
   - LLM self-assessment or retrieval similarity-based
   - Mode-specific thresholds (Customer: more conservative)
   - Comparison against threshold for escalation decision

7. **Escalation Handler**
   - Triggered by: HumanOnly category, low confidence, or explicit triggers
   - User-friendly escalation messages
   - Mode-appropriate explanations
   - Reason logging for analytics

8. **Logging & Metrics Service**
   - Structured logging with log levels (ERROR, WARN, INFO)
   - Comprehensive event capture (every interaction)
   - All API calls logged with processing times
   - Supabase Postgres persistence (async, 30s timeout, non-blocking)
   - Fields: timestamp, mode, intent_name, intent_category, outcome, confidence, escalation_reason, processing_time_ms
   - Real-time metric aggregation for dashboard
   - Enhanced observability: log all pipeline steps, API calls, processing times

9. **Knowledge Ingestion Service**
   - Web scraping/public content extraction (ANZ pages)
   - Document processing and formatting
   - Upload to OpenAI Retrieval API
   - Metadata tagging (source URL, content type, synthetic label)
   - Document version tracking

## 2. Technology Stack Decisions

### 2.1 Frontend
- **Streamlit** - Rapid UI development, built-in chat components, real-time dashboard updates

### 2.2 Backend
- **Python 3.12 or 3.13** - Core language
- **Streamlit** - Handles both frontend and backend logic (single application)
- **Async Architecture** - asyncio and aiohttp for concurrent operations
- **Structured Logging** - structlog for enhanced observability
- **Timeout Handling** - 30s timeout for all API calls (configurable)

### 2.3 AI/ML Services
- **OpenAI Chat Models** - **gpt-4o-mini** (or gpt-5-mini if available) for all LLM operations (intent classification and response generation)
  - Note: Using gpt-4o-mini as the confirmed model. Update if gpt-5-mini becomes available.
- **OpenAI Vector Store** - Managed knowledge store for RAG
  - Multiple Vector Stores organized by topic collections (customer/banker)
  - Files uploaded and attached to Vector Stores (OpenAI automatically parses/chunks/embeds)
  - Handles embeddings, chunking, and semantic search automatically
  - Supports file uploads (ANZ public content + synthetic documents)
- **OpenAI Chat Completions API with file_search tool** - Retrieval and response generation
  - Use `file_search` tool with `vector_store_ids` for semantic retrieval
  - Returns relevant chunks with metadata and citations
  - Direct API calls for retrieval (Step 3) and response generation (Step 4)
- **OpenAI Conversations API** - Session management and conversation history
  - Maintains conversation context using thread IDs
  - Stores conversation history for session continuity

### 2.4 Data Storage
- **Supabase PostgreSQL** - Relational data storage for:
  - Interaction logs
  - Intent classifications
  - Escalation events
  - Metrics aggregation
- **OpenAI Vector Store** - Managed vector store for knowledge base
  - No separate vector database needed
  - Automatic embedding generation and management
  - Files stored and indexed automatically when attached to Vector Store

### 2.5 Supporting Libraries
- **openai** - Official OpenAI Python SDK (for chat and retrieval API)
- **streamlit** - UI framework
- **supabase** - Supabase Python client (for logging)
- **BeautifulSoup** - Web scraping for ANZ content ingestion
- **aiohttp** - Async HTTP client for concurrent operations
- **asyncio** - Async/await support for concurrent operations
- **structlog** - Structured logging with log levels (ERROR, WARN, INFO)
- **httpx** - Async HTTP client with timeout support
- **pandas** - Data processing and analysis
- **python-dotenv** - Environment variable management
- **pydantic** (optional) - Data validation for intent classification outputs

## 3. Data Flow

### 3.1 Linear Query Processing Flow (Async Architecture)
```
User Query Input
    ↓
[Authentication Check - Password "rahul" required]
    ↓
1. Intent Classification (Async, 30s timeout)
   - OpenAI Chat Model (structured output)
   - Log: INFO with processing_time_ms
   - Output: intent_name, intent_category, classification_reason
    ↓
2. Router (Synchronous, fast)
   - Intent category evaluation:
     ├─→ HumanOnly → Go to Escalation (skip steps 3-5)
     ├─→ Sensitive → Continue to step 3
     └─→ Automatable → Continue to step 3
    ↓
3. Retrieval (Async, 30s timeout)
   - OpenAI Vector Store + Chat Completions API with file_search tool
   - Reference appropriate Vector Store by topic (customer/banker)
   - Retrieve top-k relevant chunks with citations
   - Include metadata (URL, title, document type)
   - Log: INFO with API call details, processing_time_ms, retrieved_chunks_count
    ↓
4. Response Generation (Async, 30s timeout)
   - OpenAI Chat Model with retrieved context
   - Generate response with numbered citations
   - Inject mode-appropriate tone and disclaimers
   - Log: INFO with API call details, processing_time_ms, response_length
    ↓
5. Confidence Check (Async, 30s timeout)
   - Evaluate confidence score against threshold (0.68)
   - Log: INFO with confidence_score, processing_time_ms
   - Compare against threshold
    ↓
6. Escalation Handler (if triggered)
   - HumanOnly category OR low confidence OR explicit triggers
   - Generate user-friendly escalation message
   - Log: INFO with trigger_type, escalation_reason
    ↓
7. Logging & Metrics (Async, 30s timeout, non-blocking)
   - Log interaction to Supabase Postgres:
     * timestamp, mode, intent_name, intent_category
     * outcome (resolved/escalated), confidence_score
     * escalation_reason (if applicable)
     * processing_time_ms per step
     * API call details (endpoint, tokens, time)
   - Update real-time metrics for dashboard
   - Log: ERROR if logging fails (queue for retry)
    ↓
Response to User (with citations & confidence)
```

### 3.2 Knowledge Ingestion Flow
```
Public ANZ URLs
    ↓
Content Extraction (Web Scraping)
    ↓
Content Processing & Formatting
    ↓
Metadata Tagging
   - Title, URL, content type
   - Source type (public vs synthetic)
   - Ingestion timestamp
    ↓
Upload to OpenAI Retrieval API
   - File upload via API
   - Automatic chunking and embedding
   - Managed storage (no manual vector DB setup)
    ↓
Metadata Storage (Optional - in Postgres)
   - Document registry for tracking
   - Version information
   - Synthetic content labeling
```

## 4. Database Schema (High-Level)

### 4.1 Knowledge Store (OpenAI Vector Store)
- Managed vector store (no schema definition needed)
- Files uploaded via Files API, then attached to Vector Store
- OpenAI automatically handles document parsing, chunking, and embedding generation
- Supports metadata tagging for documents
- Retrieval via Chat Completions API with `file_search` tool returns relevant chunks with citations
- Multiple Vector Stores by topic (customer vs banker collections)

### 4.2 Relational Tables (Supabase Postgres)
- **interactions** - Primary logging table
  - id (UUID, primary key)
  - timestamp (timestamp)
  - assistant_mode (enum: customer, banker)
  - user_query (text)
  - intent_name (text)
  - intent_category (enum: automatable, sensitive, human_only)
  - classification_reason (text)
  - outcome (enum: resolved, escalated)
  - confidence_score (float, nullable)
  - escalation_reason (text, nullable)
  - response_text (text, nullable)
  - created_at (timestamp)
  
- **escalations** (optional - can be derived from interactions)
  - id (UUID, primary key)
  - interaction_id (UUID, foreign key)
  - escalation_reason (text)
  - trigger_type (text)
  - created_at (timestamp)
  
- **knowledge_documents** (optional - for document tracking)
  - id (UUID, primary key)
  - openai_file_id (text, unique)
  - title (text)
  - source_url (text, nullable)
  - content_type (enum: public, synthetic)
  - ingested_at (timestamp)
  - metadata (jsonb)

## 5. Design Decisions Made

### 5.1 LLM Provider
- **Selected**: OpenAI Chat Models (GPT-4 or GPT-3.5-turbo)
- **Rationale**: Managed API, reliable structured outputs, citation support
- **Usage**: Intent classification and response generation

### 5.2 Knowledge Store
- **Selected**: OpenAI Vector Store (managed vector store)
- **Rationale**: No vector DB management, automatic embeddings, built-in citations, direct API access
- **Usage**: Document storage via file uploads and attachment to Vector Stores, semantic search via Chat Completions API with file_search tool

### 5.3 Pipeline Architecture
- **Selected**: Linear intent-first pipeline
- **Rationale**: Simple, predictable flow, easy to debug and monitor
- **Flow**: Classify → Route → Retrieve → Generate → Confidence Check → Escalate

### 5.4 Intent Classification
- **Selected**: LLM-based structured output
- **Rationale**: Flexible, explainable, no training data needed
- **Output Format**: JSON with intent_name, intent_category, classification_reason

### 5.5 Design Decisions Made
- **Authentication**: Simple password authentication ("rahul") at session start
- **Async Architecture**: asyncio and aiohttp for concurrent operations throughout pipeline
- **Structured Logging**: structlog with log levels (ERROR, WARN, INFO), all API calls logged with processing times
- **Timeout Handling**: 30s timeout for all API calls (configurable via API_TIMEOUT)
- **Confidence Scoring**: LLM self-assessment (ask model "How confident are you in this response?")
- **Confidence Threshold**: > 0.68 (same for both Customer and Banker modes - no mode-specific difference)
- **OpenAI Model**: gpt-4o-mini for all LLM operations
- **Knowledge Store**: OpenAI Vector Store + Chat Completions API with file_search tool (multiple Vector Stores by topic)
- **Session Management**: OpenAI Conversations API for maintaining chat history
- **Intent Taxonomy**: Defined based on PRD/README (see DETAILED_PLAN.md Section 3)
- **Knowledge Base**: 50 pages target (ANZ public pages + synthetic documents)
- **Escalation Triggers**: Comprehensive list including insufficient evidence, account-specific requests, security/fraud, financial advice, legal/hardship, emotional distress, repeated misunderstanding, explicit human request

## 6. Development Phases

### Phase 1: Foundation
- Project structure setup (Python package structure)
- Environment configuration (.env, OpenAI API key, Supabase credentials, SESSION_PASSWORD, API_TIMEOUT)
- Supabase Postgres setup (database connection, schema creation)
- Basic Streamlit UI scaffold (mode selection, chat interface skeleton)
- Authentication module (ui/auth.py)
- Structured logging setup (structlog)
- OpenAI client initialization (async support)

### Phase 2: Knowledge Base Setup
- Web scraping infrastructure (ANZ public pages, async with aiohttp)
- Document processing pipeline (formatting, metadata extraction)
- OpenAI Vector Store setup (file upload, Vector Store creation and file attachment, async with 30s timeout)
- Synthetic document creation and labeling
- Initial knowledge base population (50 pages target)
- Document metadata tracking (Supabase knowledge_documents table)
- Structured logging for ingestion operations

### Phase 3: Linear AI Pipeline - Part 1
- Intent classification service (OpenAI structured output, async, 30s timeout)
- Intent taxonomy definition
- JSON schema for intent output
- Router implementation (intent_category → decision logic)
- Structured logging for classification

### Phase 4: Linear AI Pipeline - Part 2
- Retrieval service (OpenAI Vector Store + Chat Completions API, async, 30s timeout)
- Response generation service (OpenAI Chat with citations, async, 30s timeout)
- Mode-specific response formatting (Customer vs Banker tone)
- Citation formatting and injection
- Structured logging for all API calls with processing times

### Phase 5: Safety & Escalation
- Confidence scoring implementation (async, 30s timeout)
- Mode-specific threshold configuration (0.68 for both modes)
- Escalation handler (HumanOnly, low confidence triggers)
- Escalation message generation (user-friendly)
- Structured logging for escalations

### Phase 6: Observability
- Structured logging service (structlog with ERROR, WARN, INFO levels)
- Interaction logging (all required fields, async, 30s timeout, non-blocking)
- API call logging with processing times
- Metrics calculation service (aggregations)
- KPI dashboard (Streamlit visualization)
- Real-time metric updates
- Enhanced observability (log all pipeline steps, processing times)

### Phase 7: Integration & Polish
- Authentication integration in main app
- Async pipeline orchestration
- Timeout handling throughout (30s default)
- End-to-end testing (full pipeline flow)
- Error handling and edge cases (with timeout scenarios)
- UI/UX refinement (response display, citations, confidence)
- Documentation (README, API docs, deployment guide)

## 7. Risk Mitigation Strategies

### 7.1 Hallucination Prevention
- OpenAI Retrieval API ensures only retrieved chunks inform responses
- Mandatory source citations in every response
- Structured prompts that constrain generation to retrieved content
- Mode-specific disclaimers for Customer assistant

### 7.2 Escalation Safety
- Conservative confidence thresholds (default to escalate on uncertainty)
- Multiple escalation triggers (HumanOnly category, low confidence, explicit flags)
- Clear, user-friendly escalation messages
- Comprehensive logging of escalation reasons for analysis

### 7.3 Data Quality
- Public ANZ content as primary source (validated URLs)
- Synthetic content clearly labeled and documented
- Document metadata tracking for audit trail
- Version tracking of knowledge base updates

## 8. Success Criteria

- Functional end-to-end linear pipeline (all 7 steps working)
- Accurate intent classification with structured outputs
- Reliable retrieval from OpenAI Retrieval API
- Response generation with mandatory citations
- Proper confidence scoring and threshold evaluation
- Correct escalation behavior (all triggers working)
- Complete interaction logging to Supabase
- Working real-time KPI dashboard
- Mode-specific behavior (Customer vs Banker)
- Production-ready code quality and error handling

## 9. Linear Pipeline Detailed Steps

### Step 1: Intent Classification
- **Input**: User query, assistant mode
- **Process**: OpenAI Chat API call (gpt-4o-mini) with structured output prompt
- **Output**: 
  ```json
  {
    "intent_name": "fee_inquiry",
    "intent_category": "automatable",
    "classification_reason": "User asking about standard fees"
  }
  ```
- **Model**: gpt-4o-mini with JSON schema enforcement
- **Error Handling**: Malformed JSON → ask user to re-enter

### Step 2: Router
- **Input**: intent_category from Step 1
- **Process**: Simple conditional logic
  - `HumanOnly` → Skip to Step 6 (Escalation)
  - `Sensitive` → Continue to Step 3 (Retrieval)
  - `Automatable` → Continue to Step 3 (Retrieval)
- **Output**: Routing decision (proceed to retrieval or escalate)

### Step 3: Retrieval
- **Input**: User query, assistant mode, intent_name
- **Process**: OpenAI Chat Completions API with file_search tool
  - Select appropriate Vector Store ID based on mode (customer/banker)
  - Use Chat Completions API with `file_search` tool referencing Vector Store ID
  - Tool automatically retrieves relevant chunks from Vector Store
  - Extract retrieved chunks with citations and metadata from tool response
- **Output**: Retrieved chunks with citations and metadata
- **Failure Handling**: If no results → escalate with user messaging
- **Organization**: Multiple Vector Stores by topic (customer/banker collections)

### Step 4: Response Generation
- **Input**: User query, retrieved chunks, assistant mode
- **Process**: OpenAI Chat API call (gpt-4o-mini) with:
  - System prompt (mode-specific tone - currently no specific difference)
  - Retrieved context
  - User query
  - Citation formatting instructions (numbered references [1], [2], etc.)
  - Synthetic content detection and disclaimer
- **Output**: Generated response with numbered citations
- **Citations**: Display as numbered references in UI
- **Synthetic Content**: Clearly marked with disclaimer

### Step 5: Confidence Check
- **Input**: Generated response, retrieved chunks, user query, assistant mode
- **Process**: LLM self-assessment (gpt-4o-mini)
  - Ask model "How confident are you in this response?"
  - Model returns confidence score (0.0-1.0) with reasoning
  - Parse confidence score
- **Threshold Comparison**:
  - Threshold: > 0.68 (same for both Customer and Banker modes)
  - Compare confidence score against threshold
- **Output**: Confidence score (visible to user) and threshold decision
- **Decision**: If confidence <= 0.68 → escalate

### Step 6: Escalation Handler (if triggered)
- **Triggers**: 
  - HumanOnly category from Step 1
  - Low confidence from Step 5
  - Explicit escalation triggers (emotional distress, financial advice indicators)
- **Process**: Generate user-friendly escalation message
  - Explain why escalation occurred
  - Provide next steps
  - Avoid technical jargon
- **Output**: Escalation message with reason

### Step 7: Logging & Metrics
- **Input**: All data from previous steps
- **Process**: Insert into Supabase Postgres
  - Log interaction with all required fields
  - Calculate and update metrics
  - Update dashboard in real-time
- **Output**: Logged interaction, updated metrics
