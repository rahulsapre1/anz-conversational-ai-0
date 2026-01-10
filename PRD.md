# Product Requirements Document: ContactIQ

## 1. Product Overview

**Product Name:** ContactIQ  
**Product Type:** Conversational AI (MVP)  
**Delivery Scope:** 2 days (~16 hours)  
**Primary Interfaces:** Customer Assistant, Banker Assistant

ContactIQ is a conversational AI system designed to explore how banks can use AI to safely handle common customer queries and support frontline staff using policy-backed responses, while maintaining transparency, escalation, and measurable outcomes.

The MVP focuses on controlled automation, explicit governance, and observable system behaviour, rather than feature breadth.

---

## 2. Problem Definition

### 2.1 Customer-Facing Challenges

- Contact centres receive large volumes of repeatable, low-complexity queries
- Customers often seek clarification rather than personalised advice
- Digital channels fail when explanations are unclear or untrusted

### 2.2 Employee-Facing Challenges

Frontline bankers and agents frequently need to:
- Look up policies
- Confirm process steps
- Ensure compliant wording

Information is fragmented across documents and systems.

### 2.3 AI-Specific Risks

- Hallucinated responses
- Inconsistent or non-compliant advice
- Lack of explainability
- Difficulty measuring real impact

---

## 3. Product Objectives

### 3.1 Primary Objectives

- Provide accurate, explainable responses for a limited set of banking-related queries
- Reduce avoidable human handling through safe automation
- Support bankers with policy-backed guidance
- Capture measurable outcomes from real system usage
- Establish clear control boundaries for AI behaviour

### 3.2 Secondary Objectives

- Identify intent coverage gaps
- Observe escalation patterns
- Validate feasibility of scaling within a regulated environment

---

## 4. In-Scope Users

### 4.1 Customer Assistant Users

- Retail banking customers
- Using digital interfaces
- Seeking general information (not personalised advice)

### 4.2 Banker Assistant Users

- Frontline bankers
- Contact centre agents
- Customer support staff

---

## 5. Success Metrics

**Note:** All success metrics must be derived from actual system interactions.

### 5.1 Core Metrics

- **Total conversations** - Overall system usage volume
- **Containment rate** - Percentage of conversations resolved without escalation
- **Escalation rate** - Percentage of conversations requiring human intervention
- **Intent frequency distribution** - Which intents are most common
- **Usage split** - Between Customer and Banker modes

### 5.2 Diagnostic Metrics

- **Escalation reason frequency** - Why escalations occur
- **Average confidence score by intent** - Performance per intent type
- **Intents with lowest resolution rates** - Areas needing improvement

### 5.3 Interpretation Notes

- Metrics are directional due to MVP usage volume
- Primary focus is instrumentation quality and insight generation

---

## 6. Constraints and Assumptions

### 6.1 Delivery Constraints

- 2-day development window
- Single-developer or agent-assisted build
- No access to internal ANZ systems

### 6.2 Data Constraints

- Use publicly available ANZ content as the authoritative source
- No customer-specific or sensitive data
- Synthetic policy content allowed only when gaps exist

### 6.3 Behavioural Constraints

- System must default to escalation when uncertain
- AI must not provide personalised financial advice

---

## 7. Functional Scope

### 7.1 In Scope

- Dual assistant interface (Customer and Banker modes)
- Simple password-based authentication (MVP-level, session-based)
- Intent classification and routing
- Retrieval-Augmented Generation (RAG) using OpenAI Vector Store
- Citations and confidence scoring
- Comprehensive escalation logic with multiple trigger types
- Event logging and KPI dashboard
- Async architecture with timeout handling
- Structured logging with ERROR, WARN, INFO levels

### 7.2 Explicitly Out of Scope

- Production-grade authentication (OAuth2, JWT, SSO)
- CRM or case creation
- Voice or IVR integration
- Personalised recommendations
- Multilingual support
- Proactive outreach
- Real-time session management (OpenAI Conversations API)

---

## 8. User Experience Flow

### 8.1 High-Level Flow

1. User selects assistant mode
2. User submits a query
3. System classifies intent
4. System routes based on intent category
5. Response is generated or escalation is triggered
6. Interaction is logged
7. Metrics are updated

---

## 9. Assistant Modes

### 9.1 Customer Assistant

- Narrow intent scope (focused on common customer queries)
- Conservative confidence thresholds (default: 0.68)
- Simple, explanatory tone
- Clear disclaimers
- Escalates early for sensitive topics
- User-friendly escalation messages with contact information
- Separate Vector Store for customer-facing content

### 9.2 Banker Assistant

- Broader intent tolerance (policy lookup, process clarification, etc.)
- Mandatory citations for all responses
- More technical language
- Emphasis on policy accuracy and compliance
- Escalation for ambiguity
- Professional escalation messages with internal guidance
- Separate Vector Store for banker-facing content

---

## 10. Intent Classification

### 10.1 Intent Output Schema

Each user message must produce:

- `intent_name` - Identified intent (e.g., "fee_inquiry", "policy_lookup")
- `intent_category` - One of: `automatable`, `sensitive`, `human_only` (lowercase with underscores)
- `classification_reason` - Explanation for the classification
- `assistant_mode` - Mode context ("customer" or "banker")

### 10.2 Routing Rules

- **automatable** → Continue to retrieval and response generation pipeline
- **sensitive** → Continue to retrieval and response generation pipeline (escalation occurs later if confidence is low)
- **human_only** → Immediate escalation (skip to escalation handler)

**Note**: Both `automatable` and `sensitive` intents go through the full pipeline (retrieval → generation → confidence scoring). Escalation occurs if:
- Confidence score < threshold (default: 0.68)
- Retrieval fails or returns no results
- Response generation fails

### 10.3 Logging

Intent decisions must be stored for audit and analysis.

---

## 11. Knowledge Management

### 11.1 Primary Knowledge Sources

- Public ANZ product pages
- Public ANZ policy and help pages
- Web scraping with hierarchical content extraction
- Content cleaning and normalization

Each document stored with:
- Title
- URL (source URL)
- Extracted content
- Ingestion timestamp
- Content type ("public" or "synthetic")
- Topic collection (customer vs banker)
- OpenAI file ID (for Vector Store)

### 11.2 Synthetic Knowledge

- Used only when public content is insufficient
- Clearly labelled as "SYNTHETIC CONTENT" or "Label: SYNTHETIC"
- Assumptions documented separately
- Never presented as official policy
- Automatic detection in responses with disclaimer
- Stored in separate Vector Store or clearly marked in metadata

---

## 12. Response Generation

### 12.1 Retrieval

- Retrieve relevant chunks from OpenAI Vector Store using Responses API with `file_search` tool
- Vector Store selected based on assistant mode (customer vs banker)
- Only retrieved content may inform responses
- Citations extracted from API response annotations

### 12.2 Response Requirements

- Clear answer within scope
- Source citations with numbered references [1], [2], etc.
- Confidence score displayed to user
- Disclaimer if synthetic content is detected
- Mode-specific tone (customer-friendly vs banker-technical)

### 12.3 Failure Handling

If retrieval fails or confidence is low:
- Escalate with appropriate trigger type
- Explain reason to user in mode-appropriate language
- Provide next-step guidance
- Log failure for analysis

---

## 13. Escalation Logic

### 13.1 Escalation Triggers

The system detects and handles multiple escalation trigger types:

1. **human_only** - Intent category requires human handling
2. **low_confidence** - Confidence score below threshold (default: 0.68)
3. **insufficient_evidence** - No retrieval results or insufficient information
4. **conflicting_evidence** - Conflicting information in retrieved sources
5. **account_specific** - Account-specific or personal data requests detected
6. **security_fraud** - Security or fraud indicators detected
7. **financial_advice** - Financial advice framing detected
8. **legal_hardship** - Legal or financial hardship signals
9. **emotional_distress** - Emotional distress or urgent language detected
10. **repeated_misunderstanding** - Multiple failed interactions in session
11. **explicit_human_request** - User explicitly requests human assistance

### 13.2 Escalation Behaviour

- Explain why escalation occurred in user-friendly language
- Avoid technical jargon
- Provide next-step guidance (contact information, support channels)
- Mode-specific messaging (different tone for Customer vs Banker modes)
- Log escalation with trigger type and reason for analytics

---

## 14. Instrumentation and Logging

### 14.1 Logged Fields

**Interactions Table:**
- `timestamp` - Interaction timestamp
- `assistant_mode` - "customer" or "banker"
- `session_id` - Session identifier
- `user_query` - Original user query
- `intent_name` - Classified intent
- `intent_category` - "automatable", "sensitive", or "human_only"
- `classification_reason` - Intent classification explanation
- `step_1_intent_completed` - Pipeline step tracking
- `step_2_routing_decision` - Routing decision
- `step_3_retrieval_performed` - Retrieval step status
- `step_4_response_generated` - Response generation status
- `step_5_confidence_score` - Confidence score from scorer
- `step_6_escalation_triggered` - Escalation status
- `outcome` - "resolved" or "escalated"
- `confidence_score` - Final confidence score
- `escalation_reason` - Reason for escalation (if applicable)
- `response_text` - Generated response text
- `citations` - JSON array of citations
- `retrieved_chunks_count` - Number of chunks retrieved
- `processing_time_ms` - Total processing time in milliseconds

**Escalations Table:**
- `interaction_id` - Reference to interaction
- `trigger_type` - Type of escalation trigger
- `escalation_reason` - Detailed escalation reason
- `created_at` - Escalation timestamp

### 14.2 Storage

- Supabase PostgreSQL tables
- Async, non-blocking logging with retry queue
- Structured logging with ERROR, WARN, INFO levels using structlog

---

## 15. KPI Dashboard

### 15.1 Required Views

- **Overall usage metrics** - Total interactions, conversations, sessions
- **Mode breakdown** - Usage split between Customer and Banker modes
- **Resolution metrics** - Containment rate, escalation rate
- **Intent frequency distribution** - Most common intents, intent trends
- **Escalation analysis** - Escalation reasons, trigger type frequency
- **Confidence metrics** - Average confidence scores, confidence distribution
- **Performance metrics** - Average processing times, response times
- **Time-based trends** - Usage over time, escalation trends

### 15.2 Update Frequency

- Real-time or near real-time
- Dashboard queries Supabase database directly
- Interactive charts using Plotly

---

## 16. Risks and Controls

| Risk | Control |
|------|---------|
| Hallucinations | RAG + source constraints |
| Incorrect advice | Intent gating + escalation |
| Overconfidence | Conservative thresholds |
| Low trust | Transparent explanations |

---

## 17. Iteration Strategy

The MVP is intended to inform:
- Which intents to expand
- Which documents require better coverage
- Where escalation thresholds should adjust

**No scope expansion should occur without reviewing usage data.**

---

## 18. Delivery Plan

**Note**: This section describes the original 2-day MVP plan. The actual implementation was more comprehensive and included additional features like authentication, comprehensive testing, and enhanced documentation.

### Original Plan (2 Days)

**Day 1:**
- Define intent taxonomy
- Ingest public ANZ content
- Build UI scaffold
- Implement intent classification and routing
- Implement RAG responses

**Day 2:**
- Implement escalation logic
- Implement logging and metrics
- Build KPI dashboard
- Documentation and deployment
- Generate real usage data

### MVP as Delivered

The delivered MVP includes all original requirements plus:
- Simple password-based authentication
- Comprehensive test suite (56 tests)
- Enhanced escalation logic with 11 trigger types
- Structured logging with multiple log levels
- Async architecture with timeout handling
- Complete deployment documentation
- Enhanced KPI dashboard with multiple metrics
- Comprehensive implementation guides

---

## 19. Technical Implementation Notes

### 19.1 Architecture

- **Frontend**: Streamlit web application
- **Backend**: Python 3.12/3.13 with async/await architecture
- **AI/ML**: OpenAI gpt-4o-mini, Vector Store API, Chat Completions API
- **Database**: Supabase PostgreSQL
- **Logging**: Structured logging with structlog (ERROR, WARN, INFO levels)

### 19.2 Key Technical Features

- **Async Operations**: All services use async/await for non-blocking operations
- **Timeout Handling**: 30-second timeout (configurable) for all API calls
- **Retry Logic**: Exponential backoff for failed API calls
- **Non-blocking Logging**: Async logging to Supabase with retry queue
- **Error Handling**: Comprehensive error handling with graceful degradation
- **Test Coverage**: 56 tests covering unit, integration, authentication, timeout, and logging scenarios

### 19.3 Configuration

All configuration via environment variables:
- OpenAI API key and model selection
- Vector Store IDs (separate for customer and banker modes)
- Supabase connection details
- Confidence threshold (default: 0.68)
- API timeout (default: 30 seconds)
- Session password for authentication
- Log level (INFO, WARN, ERROR)

---

## 20. Disclaimer

**ContactIQ is a demonstration system and does not provide financial advice.**
