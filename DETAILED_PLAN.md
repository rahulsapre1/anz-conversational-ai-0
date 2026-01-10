# ContactIQ - Detailed Implementation Plan

## 1. Project Structure

```
contactiq/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── main.py                      # Streamlit app entry point
├── config.py                    # Configuration management
├── 
├── services/
│   ├── __init__.py
│   ├── intent_classifier.py     # Step 1: Intent classification
│   ├── router.py                # Step 2: Routing logic
│   ├── retrieval_service.py     # Step 3: OpenAI Vector Store + Chat Completions API with file_search
│   ├── response_generator.py    # Step 4: Response generation
│   ├── confidence_scorer.py     # Step 5: Confidence scoring
│   ├── escalation_handler.py    # Step 6: Escalation logic
│   └── logger.py                # Step 7: Logging service
│
├── knowledge/
│   ├── __init__.py
│   ├── ingestor.py              # Web scraping & ingestion
│   └── synthetic_generator.py   # Synthetic document creation
│
├── database/
│   ├── __init__.py
│   ├── schema.sql               # Supabase schema migrations
│   ├── supabase_client.py       # Supabase connection
│   └── migrations/              # SQL migration scripts
│
├── ui/
│   ├── __init__.py
│   ├── auth.py                  # Authentication (password check)
│   ├── chat_interface.py        # Streamlit chat UI
│   ├── dashboard.py             # KPI dashboard
│   └── components.py            # Reusable UI components
│
└── utils/
    ├── __init__.py
    ├── openai_client.py         # OpenAI client wrapper
    ├── validators.py            # Data validation
    └── constants.py             # Intent taxonomy, thresholds, etc.
```

## 2. Technology Stack (Confirmed)

### 2.1 Core Technologies
- **Python**: 3.12 or 3.13
- **Virtual Environment**: venv
- **Frontend**: Streamlit
- **LLM**: OpenAI gpt-4o-mini (for all LLM operations)
- **Knowledge Store**: OpenAI Vector Store + Chat Completions API with file_search tool
- **Database**: Supabase PostgreSQL
- **Session Management**: OpenAI Conversations API

### 2.2 Key Libraries
```python
# requirements.txt
streamlit>=1.31.0
openai>=1.12.0
supabase>=2.0.0
python-dotenv>=1.0.0
beautifulsoup4>=4.12.0
requests>=2.31.0
pandas>=2.1.0
pydantic>=2.5.0
python-dateutil>=2.8.0
# Async support
aiohttp>=3.9.0
asyncio>=3.4.3
# Structured logging
structlog>=23.2.0
# Timeout handling
httpx>=0.25.0  # For async HTTP with timeout support
```

## 3. Intent Taxonomy

Based on PRD and README, initial intent taxonomy:

### 3.1 Customer Assistant Intents

| Intent Name | Intent Category | Description |
|------------|----------------|-------------|
| `transaction_explanation` | Automatable | Questions about transaction details, codes, descriptions |
| `fee_inquiry` | Automatable | Questions about fees, charges, pricing |
| `account_limits` | Automatable | Questions about account limits, daily limits, transfer limits |
| `card_dispute_process` | Automatable | Guidance on disputing card transactions |
| `application_process` | Automatable | General information about account/product applications |
| `account_balance` | Sensitive | Account balance inquiries (escalate - needs authentication) |
| `transaction_history` | Sensitive | Transaction history requests (escalate - needs authentication) |
| `password_reset` | Sensitive | Password or security-related requests |
| `financial_advice` | HumanOnly | Requests for personalized financial advice |
| `complaint` | HumanOnly | Formal complaints or grievances |
| `hardship` | HumanOnly | Financial hardship indicators |
| `fraud_alert` | HumanOnly | Security/fraud concerns |
| `unknown` | HumanOnly | Unclassifiable or out-of-scope queries |

### 3.2 Banker Assistant Intents

| Intent Name | Intent Category | Description |
|------------|----------------|-------------|
| `policy_lookup` | Automatable | Looking up bank policies, terms, conditions |
| `process_clarification` | Automatable | Process steps, workflows, procedures |
| `product_comparison` | Automatable | Comparing products, features, differences |
| `compliance_phrasing` | Automatable | Guidance on compliant language, disclaimers |
| `fee_structure` | Automatable | Fee schedules, pricing information |
| `eligibility_criteria` | Automatable | Product eligibility requirements |
| `documentation_requirements` | Automatable | Required documents, forms, procedures |
| `customer_specific_query` | Sensitive | Questions requiring access to customer data |
| `complex_case` | HumanOnly | Complex cases requiring expert judgment |
| `complaint_handling` | HumanOnly | Formal complaint procedures |
| `regulatory_question` | HumanOnly | Regulatory or legal questions |
| `unknown` | HumanOnly | Unclassifiable or out-of-scope queries |

## 4. Configuration & Environment Variables

### 4.1 .env File Structure
```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_VECTOR_STORE_ID_CUSTOMER=vs_...  # Vector Store for customer content
OPENAI_VECTOR_STORE_ID_BANKER=vs_...    # Vector Store for banker content

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...

# Application
CONFIDENCE_THRESHOLD=0.68
LOG_LEVEL=INFO
SESSION_PASSWORD=rahul  # Simple password for session authentication
API_TIMEOUT=30  # Timeout in seconds for all API calls
```

### 4.2 Config Module (config.py)
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_VECTOR_STORE_ID_CUSTOMER = os.getenv("OPENAI_VECTOR_STORE_ID_CUSTOMER")
    OPENAI_VECTOR_STORE_ID_BANKER = os.getenv("OPENAI_VECTOR_STORE_ID_BANKER")
    
    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Thresholds
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.68"))
    
    # Authentication
    SESSION_PASSWORD = os.getenv("SESSION_PASSWORD", "rahul")
    
    # Timeouts
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))  # 30 seconds default
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Intent Taxonomy
    CUSTOMER_INTENTS = {...}  # From section 3.1
    BANKER_INTENTS = {...}    # From section 3.2
```

## 5. Database Schema

### 5.1 Supabase Tables (schema.sql)

```sql
-- Interactions table (primary logging)
CREATE TABLE interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assistant_mode VARCHAR(10) NOT NULL CHECK (assistant_mode IN ('customer', 'banker')),
    session_id VARCHAR(255),  -- OpenAI conversation ID
    
    -- User input
    user_query TEXT NOT NULL,
    
    -- Intent classification
    intent_name VARCHAR(100),
    intent_category VARCHAR(20) CHECK (intent_category IN ('automatable', 'sensitive', 'human_only')),
    classification_reason TEXT,
    
    -- Pipeline steps (logged for debugging)
    step_1_intent_completed BOOLEAN DEFAULT FALSE,
    step_2_routing_decision VARCHAR(50),
    step_3_retrieval_performed BOOLEAN DEFAULT FALSE,
    step_4_response_generated BOOLEAN DEFAULT FALSE,
    step_5_confidence_score FLOAT,
    step_6_escalation_triggered BOOLEAN DEFAULT FALSE,
    
    -- Outcome
    outcome VARCHAR(20) NOT NULL CHECK (outcome IN ('resolved', 'escalated')),
    confidence_score FLOAT,
    escalation_reason TEXT,
    
    -- Response
    response_text TEXT,
    citations JSONB,  -- Array of citation objects
    
    -- Metadata
    retrieved_chunks_count INTEGER,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Escalations table (derived data, optional but useful for analytics)
CREATE TABLE escalations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interaction_id UUID REFERENCES interactions(id),
    trigger_type VARCHAR(50) NOT NULL,  -- 'human_only', 'low_confidence', 'insufficient_evidence', etc.
    escalation_reason TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Knowledge documents registry (optional, for tracking)
CREATE TABLE knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    openai_file_id VARCHAR(255) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    source_url TEXT,
    content_type VARCHAR(20) CHECK (content_type IN ('public', 'synthetic')),
    topic_collection VARCHAR(100),  -- Which assistant/topic collection
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- Indexes for performance
CREATE INDEX idx_interactions_timestamp ON interactions(timestamp);
CREATE INDEX idx_interactions_mode ON interactions(assistant_mode);
CREATE INDEX idx_interactions_intent ON interactions(intent_name);
CREATE INDEX idx_interactions_outcome ON interactions(outcome);
CREATE INDEX idx_escalations_interaction ON escalations(interaction_id);
```

## 6. Architecture Enhancements

### 6.1 Async Architecture

**Implementation Strategy:**
- Use `asyncio` and `aiohttp` for concurrent operations
- Pipeline steps that can run in parallel should use async/await
- API calls should be async with proper timeout handling
- Database operations can be async where supported

**Async Opportunities:**
1. **Knowledge Ingestion**: Parallel scraping of multiple URLs
2. **Retrieval + Response Generation**: Can be parallelized if needed
3. **Logging**: Async logging to avoid blocking main pipeline
4. **Multiple API Calls**: Concurrent calls where independent

**Implementation Pattern:**
```python
import asyncio
import aiohttp
from typing import List, Dict, Any

async def process_pipeline_async(user_query: str, assistant_mode: str):
    """Async pipeline execution."""
    # Step 1: Intent Classification (async)
    intent_result = await classify_intent_async(user_query, assistant_mode)
    
    # Step 2: Router (synchronous, fast)
    route_decision = route(intent_result["intent_category"])
    
    if route_decision["route"] == "escalate":
        return await handle_escalation_async(...)
    
    # Step 3 & 4: Can run concurrently if needed
    retrieval_task = retrieve_chunks_async(user_query, assistant_mode)
    # ... other steps
    
    # Wait for all async operations
    results = await asyncio.gather(*[retrieval_task, ...])
    
    return results
```

### 6.2 Structured Logging

**Implementation:**
- Use `structlog` for structured logging
- Log levels: ERROR, WARN, INFO (configurable via LOG_LEVEL)
- Log all API calls with:
  - Request details (endpoint, parameters)
  - Response status/code
  - Processing time per step
  - Error details if any

**Log Structure:**
```python
import structlog
import time

logger = structlog.get_logger()

# Example structured log
logger.info(
    "intent_classification_completed",
    intent_name="fee_inquiry",
    intent_category="automatable",
    processing_time_ms=245,
    user_query_length=45,
    assistant_mode="customer"
)

# API call logging
logger.info(
    "openai_api_call",
    endpoint="chat.completions",
    model="gpt-4o-mini",
    request_tokens=150,
    response_tokens=200,
    processing_time_ms=1200,
    status="success"
)
```

**Logging Requirements:**
- **ERROR**: All errors, exceptions, failures
- **WARN**: Retries, degraded functionality, threshold warnings
- **INFO**: All API calls, pipeline step completions, processing times
- **Structured Fields**: Always include processing_time_ms, step_name, status

### 6.3 Timeout Handling

**Implementation:**
- Default timeout: 30 seconds for all API calls
- Configurable via API_TIMEOUT environment variable
- Use `asyncio.wait_for()` for async operations
- Use `timeout` parameter for HTTP clients

**Timeout Strategy:**
```python
import asyncio
from config import Config

async def api_call_with_timeout(coro, timeout=None):
    """Wrapper for async API calls with timeout."""
    timeout = timeout or Config.API_TIMEOUT
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(
            "api_call_timeout",
            timeout=timeout,
            operation=coro.__name__
        )
        raise
```

**Timeout Application:**
- All OpenAI API calls: 30s timeout
- Supabase operations: 30s timeout
- HTTP requests (scraping): 30s timeout
- File uploads: 30s timeout (or longer if needed)

## 7. Linear Pipeline Implementation Details

### 7.1 Step 1: Intent Classification (intent_classifier.py)

**Input:**
- `user_query`: str
- `assistant_mode`: str ('customer' | 'banker')

**Process:**
1. Load appropriate intent taxonomy (customer or banker)
2. Construct prompt with intent list and examples
3. Call OpenAI Chat API with structured output (JSON schema)
4. Parse and validate response
5. Handle malformed JSON (ask user to re-enter)

**Output:**
```python
{
    "intent_name": "fee_inquiry",
    "intent_category": "automatable",  # or "sensitive" or "human_only"
    "classification_reason": "User asking about standard fees for accounts"
}
```

**Error Handling:**
- Malformed JSON → Return None, log ERROR, ask user to re-enter
- Unknown intent_category → Default to "human_only", log WARN
- API failure → Retry (3 attempts with exponential backoff), log WARN for retries, log ERROR on final failure, then escalate
- Timeout → Log ERROR with timeout details, escalate

**Async Implementation:**
- Use async OpenAI client calls
- Apply 30s timeout via `asyncio.wait_for()`
- Log processing time and API call details

**Logging:**
- INFO: Intent classification started, completed with processing time
- ERROR: Classification failures, timeouts
- Structured logs include: intent_name, intent_category, processing_time_ms, status

### 6.2 Step 2: Router (router.py)

**Input:**
- `intent_category`: str
- `intent_name`: str

**Process:**
Simple conditional logic:
```python
if intent_category == "human_only":
    return {"route": "escalate", "skip_to_step": 6}
elif intent_category in ["automatable", "sensitive"]:
    return {"route": "continue", "next_step": 3}
```

**Output:**
- Routing decision (escalate or continue)

### 6.3 Step 3: Retrieval (retrieval_service.py)

**Input:**
- `user_query`: str
- `assistant_mode`: str
- `intent_name`: str

**Process:**
1. Determine appropriate Vector Store ID based on mode (customer/banker)
2. Use OpenAI Chat Completions API with `file_search` tool
3. Call Chat Completions API with:
   - User query
   - Tools: `[{"type": "file_search", "vector_store_ids": [vector_store_id]}]`
4. Extract retrieved chunks from tool call response
5. Parse citations from file_search tool response

**Output:**
```python
{
    "retrieved_chunks": [...],  # List of relevant document chunks
    "citations": [...],         # Citation metadata with file IDs and quotes
    "file_ids": [...]           # OpenAI file IDs used
}
```

**Error Handling:**
- No results → Return empty list, log WARN, trigger escalation
- API failure → Retry (3 attempts), log WARN for retries, log ERROR on final failure, then escalate with user messaging
- Timeout → Log ERROR with timeout details, escalate

**Async Implementation:**
- Use async Chat Completions API calls
- Apply 30s timeout via `asyncio.wait_for()`
- Log API call details and processing time

**Logging:**
- INFO: Retrieval started, completed with processing time, retrieved chunks count
- WARN: No results found, retries
- ERROR: API failures, timeouts
- Structured logs include: vector_store_id, retrieved_chunks_count, processing_time_ms, status

**Vector Store Configuration:**
- One Vector Store per topic collection (customer vs banker)
- Files uploaded via Files API, then attached to Vector Store
- OpenAI automatically handles parsing, chunking, and embedding
- Retrieval via Chat Completions API with file_search tool

### 7.4 Step 4: Response Generation (response_generator.py)

**Input:**
- `user_query`: str
- `retrieved_chunks`: list
- `assistant_mode`: str
- `intent_name`: str

**Process:**
1. Construct system prompt (mode-specific)
2. Format retrieved chunks as context
3. Call OpenAI Chat API (gpt-4o-mini) with 30s timeout
4. Generate response with numbered citations
5. Check for synthetic content markers and add disclaimers

**Error Handling:**
- API failure → Retry (3 attempts), log WARN for retries, log ERROR on final failure, then escalate
- Timeout → Log ERROR with timeout details, escalate

**Async Implementation:**
- Use async Chat Completions API calls
- Apply 30s timeout via `asyncio.wait_for()`
- Log API call details and processing time

**Logging:**
- INFO: Response generation started, completed with processing time, response length
- ERROR: API failures, timeouts
- Structured logs include: response_length, citations_count, processing_time_ms, status

**Output:**
```python
{
    "response_text": "Based on ANZ's fee schedule... [1] [2]",
    "citations": [
        {"number": 1, "source": "ANZ Fee Schedule", "url": "https://..."},
        {"number": 2, "source": "ANZ Terms", "url": "https://..."}
    ],
    "has_synthetic_content": False
}
```

**Prompt Structure:**
```python
SYSTEM_PROMPT_CUSTOMER = """
You are a helpful banking assistant for ANZ customers. 
- Provide clear, simple explanations
- Always cite sources using numbered references [1], [2], etc.
- If content is synthetic, clearly state "Note: This information is based on synthetic content and may not reflect official ANZ policy."
- Only use information from the provided context.
"""

SYSTEM_PROMPT_BANKER = """
You are an internal banking assistant for ANZ staff. 
- Provide technical, policy-focused responses
- Always include citations with numbered references [1], [2], etc.
- If content is synthetic, clearly state "Note: This information is based on synthetic content."
- Emphasize compliance and accuracy.
"""
```

### 7.5 Step 5: Confidence Scoring (confidence_scorer.py)

**Input:**
- `response_text`: str
- `retrieved_chunks`: list
- `user_query`: str
- `assistant_mode`: str

**Process:**
1. Call OpenAI Chat API with confidence assessment prompt (30s timeout)
2. Ask model to rate confidence on scale 0.0-1.0
3. Parse confidence score
4. Compare against threshold (0.68)
5. Return score and threshold decision

**Error Handling:**
- API failure → Retry (3 attempts), log WARN for retries, log ERROR on final failure, default to low confidence (escalate)
- Timeout → Log ERROR with timeout details, default to low confidence (escalate)
- Parse failure → Log ERROR, default to low confidence (escalate)

**Async Implementation:**
- Use async Chat Completions API calls
- Apply 30s timeout via `asyncio.wait_for()`
- Log API call details and processing time

**Logging:**
- INFO: Confidence scoring started, completed with score and processing time
- WARN: Low confidence scores, retries
- ERROR: API failures, timeouts, parse failures
- Structured logs include: confidence_score, meets_threshold, processing_time_ms, status

**Output:**
```python
{
    "confidence_score": 0.85,
    "meets_threshold": True,
    "threshold_value": 0.68
}
```

**Confidence Prompt:**
```
"On a scale of 0.0 to 1.0, how confident are you that the response 
you provided accurately answers the user's query based solely on 
the retrieved context? Consider: completeness, accuracy, relevance, 
and whether all information needed is present.

User Query: {user_query}
Response: {response_text}

Respond with only a JSON object: {"confidence": 0.85, "reasoning": "..."}"
```

### 7.6 Step 6: Escalation Handler (escalation_handler.py)

**Input:**
- `escalation_reason`: str
- `trigger_type`: str
- `assistant_mode`: str
- `intent_name`: str

**Triggers:**
1. `human_only` - Intent category is HumanOnly
2. `low_confidence` - Confidence score < 0.68
3. `insufficient_evidence` - No retrieval results
4. `conflicting_evidence` - Conflicting information in retrieved chunks
5. `account_specific` - Account-specific or personal data requests
6. `security_fraud` - Security/fraud indicators
7. `financial_advice` - Financial advice framing detected
8. `legal_hardship` - Legal or hardship signals
9. `emotional_distress` - Emotional distress or urgent language
10. `repeated_misunderstanding` - Multiple failed interactions
11. `explicit_human_request` - User explicitly requests human

**Process:**
1. Detect trigger type
2. Generate user-friendly escalation message
3. Log escalation reason (structured logging)
4. Return escalation response

**Error Handling:**
- Message generation failure → Use default escalation message, log ERROR
- Logging failure → Continue (non-blocking), log ERROR separately

**Async Implementation:**
- Escalation message generation can be async if using LLM
- Logging should be async (non-blocking)
- Apply timeout if using API calls

**Logging:**
- INFO: Escalation triggered with trigger type and reason
- ERROR: Escalation message generation failures
- Structured logs include: trigger_type, escalation_reason, assistant_mode, intent_name

**Output:**
```python
{
    "escalated": True,
    "escalation_message": "I understand you're asking about [topic]. 
                          This requires personalized assistance from 
                          our team. Please contact [next steps].",
    "trigger_type": "low_confidence",
    "escalation_reason": "Confidence score 0.65 below threshold 0.68"
}
```

### 7.7 Step 7: Logging Service (logger.py)

**Input:**
- All data from previous steps
- Pipeline execution metadata

**Process:**
1. Prepare interaction record with structured logging data
2. Insert into Supabase `interactions` table (async, 30s timeout)
3. If escalated, create `escalations` record (async, 30s timeout)
4. Calculate and update metrics (for dashboard)
5. Log structured events (ERROR, WARN, INFO) with processing times

**Logged Fields:**
- All fields from interactions table schema
- Each pipeline step completion status
- Processing time per step (processing_time_ms)
- Error information (if any)
- API call details (endpoint, status, tokens, time)

**Error Handling:**
- Database insert failure → Retry (3 attempts), log ERROR, queue for async retry
- Timeout → Log ERROR with timeout details, queue for async retry
- Non-blocking: Logging failures should not block user response

**Async Implementation:**
- Use async Supabase client operations
- Apply 30s timeout via `asyncio.wait_for()`
- Queue failed logs for background retry
- Log structured events asynchronously

**Structured Logging:**
- Use structlog for all logging
- Log levels: ERROR, WARN, INFO (from Config.LOG_LEVEL)
- All logs include: timestamp, step_name, processing_time_ms, status
- API calls logged with: endpoint, model, tokens, processing_time_ms, status
- Errors logged with: error_type, error_message, stack_trace (if applicable)

## 8. Knowledge Ingestion

### 8.1 ANZ Public Content Collection (ingestor.py)

**Target URLs Source:**
- All URLs listed in `@ANZ_web_scrape.xml`

**Process:**
1. Read the list of target URLs from `@ANZ_web_scrape.xml`.
2. Iterate through each URL using a rate-limited HTTP client (to respect robots.txt and avoid overloading servers).
3. For each URL:
   - Fetch the static HTML content (async, 30s timeout per URL).
   - Parse the response using BeautifulSoup.
   - Extract and store required fields:
     - Main content (stripping out navigation, footer, ads, etc.)
     - Page title
     - Source URL
     - Retrieval date
   - Clean and format extracted text.
   - Format content as plain text (.txt) file with structure:
     ```
     Title: [Page Title]
     Source URL: [Original URL]
     Retrieval Date: [YYYY-MM-DD]
     Content Type: public
     
     [Main content text]
     
     ---
     Original URL: [URL]
     Scraped: [Date]
     ```
   - Sanitize page title for use as filename (remove special characters, limit length).
   - Save as: `{sanitized_title}.txt` (UTF-8 encoding).
   - (If document is large) Split content into suitable chunks, naming each: `{sanitized_title}_chunk_{n}.txt`.
   - Upload the .txt file(s) to OpenAI Files API (async, 30s timeout).
   - Attach files to appropriate Vector Store (customer or banker based on topic) (async, 30s timeout).
   - Register each document/chunk entry in the Supabase `knowledge_documents` table with metadata (async, 30s timeout).
   - Log all operations with structured logging (INFO for success, ERROR for failures).

**Async Implementation:**
- Use `aiohttp` for concurrent URL fetching (with rate limiting)
- Parallel processing of multiple URLs (respect robots.txt)
- Async file uploads to OpenAI
- Async database operations
- All operations with 30s timeout

**Logging:**
- INFO: URL fetched, content extracted, file uploaded, processing time
- WARN: Rate limit warnings, retries
- ERROR: Fetch failures, parse errors, upload failures, timeouts
- Structured logs include: url, status, processing_time_ms, file_id (if uploaded)

**File Format Specifications:**
- **Format**: Plain text (.txt)
- **Encoding**: UTF-8
- **Naming**: Sanitized page title (e.g., "ANZ Fee Schedule" → "anz_fee_schedule.txt")
- **Structure**: Metadata header (Title, Source URL, Retrieval Date) + content + footer (Original URL, Scraped date)
- **Size Limits**: Max 512MB per file, max 2M tokens per file
- **Chunking**: If content exceeds limits, split into multiple .txt files with `_chunk_{n}` suffix

**Summary:**
> All ANZ public knowledge is collected by crawling the URLs listed in `@ANZ_web_scrape.xml`, rate-limited, and parsed with BeautifulSoup to extract content and metadata. Content is formatted as plain text (.txt) files with metadata headers (including source URL), sanitized filenames, and UTF-8 encoding for upload to OpenAI Files API and downstream ingestion.

### 8.2 Synthetic Document Generation (synthetic_generator.py)

**Creation Criteria:**
- Only when public content gaps identified
- Clearly labeled as synthetic
- Document assumptions separately

**Types:**
- Policy summaries (where public docs incomplete)
- Process flows (where documentation missing)
- Compliance guidelines (internal procedures)

**Format:**
```
Title: [Topic] - SYNTHETIC CONTENT
Label: SYNTHETIC
Content: [Document content]
Assumptions: [List of assumptions made]
Source: Generated for ContactIQ MVP
```

## 9. UI Implementation (Streamlit)

### 9.1 Authentication (auth.py)

**Implementation:**
- Simple password authentication at session start
- Password: "rahul" (configurable via SESSION_PASSWORD env var)
- Password prompt displayed before accessing any features
- Session state stored in Streamlit session_state
- Password validated once per session (not per request)

**Flow:**
1. User opens application
2. Password prompt displayed
3. User enters password
4. If correct, session authenticated and main interface shown
5. If incorrect, error message and retry prompt
6. Authenticated state persists for session duration

**Code Structure:**
```python
# ui/auth.py
import streamlit as st
from config import Config

def check_authentication():
    """Check if user is authenticated, show password prompt if not."""
    if "authenticated" not in st.session_state:
        st.title("ContactIQ - Authentication Required")
        password = st.text_input("Enter password:", type="password", key="password_input")
        
        if st.button("Login"):
            if password == Config.SESSION_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect password. Please try again.")
        st.stop()
    
    return st.session_state.get("authenticated", False)
```

### 9.2 Chat Interface (chat_interface.py)

**Features:**
- Password authentication (via auth.py) before accessing interface
- Mode selection (Customer/Banker toggle)
- Chat history display (from OpenAI Conversations API)
- Message input
- Response display with:
  - Response text
  - Numbered citations
  - Confidence score (visible to user)
  - Escalation messages
- Loading indicators

**Session Management:**
- Use OpenAI Conversations API
- Maintain conversation thread per user session
- Display full conversation history
- Authentication state managed via Streamlit session_state

### 9.3 KPI Dashboard (dashboard.py)

**Metrics (from PRD Section 5):**

1. **Overall Usage Metrics:**
   - Total conversations
   - Total interactions
   - Average interactions per conversation

2. **Mode Breakdown:**
   - Customer mode usage count
   - Banker mode usage count
   - Percentage split

3. **Resolution Metrics:**
   - Containment rate (resolved without escalation)
   - Escalation rate
   - Total resolved count
   - Total escalated count

4. **Intent Frequency:**
   - Intent frequency distribution (chart)
   - Top 10 intents
   - Intent category breakdown

5. **Escalation Analysis:**
   - Escalation reason frequency
   - Escalation by intent
   - Escalation by mode

6. **Confidence Metrics:**
   - Average confidence score (overall)
   - Average confidence by intent
   - Confidence distribution histogram

7. **Performance Metrics:**
   - Average processing time
   - Intents with lowest resolution rates

**Visualization:**
- Streamlit charts (bar, line, pie)
- Real-time updates (on interaction)
- Filters (by mode, date range, intent)

## 10. Error Handling Strategy

### 10.1 OpenAI API Failures
- **Retry Logic**: 3 attempts with exponential backoff (1s, 2s, 4s)
- **Timeout**: 30 seconds per attempt (configurable via API_TIMEOUT)
- **After Retries**: Escalate with user messaging
- **User Message**: "We're experiencing technical difficulties. Please try again or contact support."
- **Logging**: Log ERROR with retry count, timeout details, final failure reason

### 10.2 Retrieval API Failures
- **No Results**: Escalate with message explaining insufficient information, log WARN
- **API Failure**: Retry (3 attempts with 30s timeout each), log WARN for retries, log ERROR on final failure
- **Timeout**: 30 seconds, log ERROR with timeout details, escalate

### 10.3 Invalid Intent Classification
- **Malformed JSON**: Log ERROR, return None, ask user to re-enter query
- **Unknown Category**: Default to "human_only", log WARN, escalate
- **Timeout**: 30 seconds, log ERROR, default to "human_only"

### 10.4 Database Failures
- **Connection Issues**: Log ERROR, retry (3 attempts with 30s timeout), queue for async retry if all fail
- **Insert Failures**: Retry with exponential backoff (30s timeout per attempt)
- **Timeout**: 30 seconds, log ERROR, queue for async retry (non-blocking)
- **Non-Blocking**: Logging failures should not block user response

## 11. Development Phases & Timeline

### Phase 1: Foundation (2-3 hours)
- [ ] Project structure setup
- [ ] Environment configuration (including SESSION_PASSWORD, API_TIMEOUT)
- [ ] Requirements.txt (including async and logging libraries)
- [ ] Supabase setup and schema migration
- [ ] Basic Streamlit scaffold
- [ ] Authentication module (ui/auth.py)

### Phase 2: Knowledge Base (3-4 hours)
- [ ] Web scraping infrastructure (async with aiohttp)
- [ ] OpenAI Vector Store setup
- [ ] Document upload pipeline (async with 30s timeout)
- [ ] Initial content population (50 pages target)
- [ ] Synthetic document generation (as needed)
- [ ] Structured logging for ingestion operations

### Phase 3: Linear Pipeline - Part 1 (2-3 hours)
- [ ] Intent classifier (async with 30s timeout)
- [ ] Router
- [ ] Error handling for classification
- [ ] Structured logging for classification

### Phase 4: Linear Pipeline - Part 2 (3-4 hours)
- [ ] Retrieval service (async, Vector Store + Chat Completions API, 30s timeout)
- [ ] Response generator (async, 30s timeout)
- [ ] Citation formatting
- [ ] Synthetic content detection
- [ ] Structured logging for all API calls

### Phase 5: Safety & Escalation (2-3 hours)
- [ ] Confidence scorer (async, 30s timeout)
- [ ] Escalation handler
- [ ] All escalation triggers
- [ ] User messaging
- [ ] Structured logging for escalations

### Phase 6: Observability (2-3 hours)
- [ ] Structured logging service (using structlog)
- [ ] Log levels configuration (ERROR, WARN, INFO)
- [ ] API call logging with processing times
- [ ] Metrics calculation
- [ ] Dashboard implementation
- [ ] Real-time updates

### Phase 7: Integration & Testing (2-3 hours)
- [ ] Authentication integration in main app
- [ ] Async pipeline orchestration
- [ ] Timeout handling throughout
- [ ] End-to-end testing
- [ ] Error handling validation
- [ ] UI/UX refinement
- [ ] Documentation

**Total Estimated Time: ~16-23 hours** (fits within 2-day window with buffer)

## 12. Testing Strategy

### 12.1 Unit Tests
- Intent classification (various queries)
- Router logic (all categories)
- Confidence scoring (edge cases)
- Escalation triggers

### 12.2 Integration Tests
- Full pipeline flow (happy path)
- Pipeline with escalation
- Error handling scenarios
- Logging verification

### 12.3 Manual Testing
- UI functionality
- Dashboard metrics accuracy
- Conversation flow
- Citation display

## 13. Deployment Considerations

### 13.1 Local Development
- Run with `streamlit run main.py`
- Environment variables from .env
- Local Supabase connection

### 13.2 Production Deployment (Future)
- Streamlit Cloud or similar
- Environment variables in platform
- Supabase connection (same)

## 14. Success Criteria Checklist

- [ ] Password authentication working (password "rahul" required at session start)
- [ ] Intent classification working for all defined intents (async, 30s timeout)
- [ ] Router correctly handles all categories
- [ ] Retrieval returns relevant chunks with citations (async, 30s timeout)
- [ ] Response generation includes proper citations (async, 30s timeout)
- [ ] Confidence scoring meets threshold logic (async, 30s timeout)
- [ ] All escalation triggers work correctly
- [ ] All interactions logged to Supabase (async, 30s timeout, non-blocking)
- [ ] Structured logging implemented (ERROR, WARN, INFO levels)
- [ ] All API calls logged with processing times
- [ ] Timeout handling (30s) implemented throughout
- [ ] Async architecture implemented where applicable
- [ ] KPI dashboard shows all required metrics
- [ ] Error handling works for all failure modes (with timeouts)
- [ ] Knowledge base populated with 50+ pages (async ingestion)
- [ ] Synthetic content properly labeled
- [ ] User-facing features (chat, citations, confidence) working
