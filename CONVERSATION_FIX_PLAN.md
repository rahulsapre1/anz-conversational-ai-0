# Conversation Fix Plan

## Issues Identified

### Issue 1: No Conversational Greeting Handling
**Problem**: When user says "hi", the intent classifier tries to match it to banking intents. Since "hi" doesn't match any banking intent, it gets classified as "unknown" → "human_only" → immediate escalation.

**Root Cause**: 
- No "greeting" or "conversational" intent exists in the taxonomy
- System is designed purely for knowledge-seeking queries
- Greetings are treated as unclassifiable queries

**Evidence**: 
- `utils/constants.py` - No greeting intent in CUSTOMER_INTENTS or BANKER_INTENTS
- `services/intent_classifier.py` line 142-143: Unknown intents default to "human_only"

### Issue 2: No Conversation History/Context
**Problem**: Each message is processed independently. The system has no memory of previous messages in the conversation.

**Root Cause**:
- Chat history is stored in `st.session_state.chat_history` but never passed to pipeline services
- `run_pipeline_async()` only receives `user_query` and `assistant_mode` - no history
- Intent classifier, response generator, etc. only see the current message
- Response generator creates messages with only current query, no conversation context

**Evidence**:
- `ui/chat_interface.py` line 185-426: `run_pipeline_async()` signature doesn't include chat_history
- `services/intent_classifier.py` line 56-59: Messages array only contains system prompt and current user query
- `services/response_generator.py` line 108-110: Messages array only contains system prompt and current user query with context

### Issue 3: One-Shot Architecture
**Problem**: System behaves like a Q&A system, not a conversational assistant. Cannot handle:
- Follow-up questions ("What about fees?")
- Contextual references ("Tell me more about that")
- Multi-turn conversations
- Clarifications

**Root Cause**: Same as Issue 2 - no conversation history passed through pipeline.

## Solution Plan

### Step 1: Add Conversational Intents
**File**: `utils/constants.py`

Add new intents for both Customer and Banker modes:
- `greeting`: "automatable" - Handle greetings, small talk
- `general_conversation`: "automatable" - Handle conversational queries that don't require knowledge base

### Step 2: Add Conversation History Parameter
**Files**: 
- `ui/chat_interface.py` - Pass chat_history to pipeline
- `services/intent_classifier.py` - Accept and use conversation history
- `services/response_generator.py` - Accept and use conversation history

**Changes**:
1. Modify `run_pipeline_async()` to accept `chat_history` parameter
2. Extract conversation messages from chat_history (last N messages for context)
3. Pass conversation history to intent classifier and response generator
4. Update intent classifier prompt to consider conversation context
5. Update response generator to build messages array with full conversation history

### Step 3: Implement Conversational Response Handling
**Files**:
- `services/response_generator.py` - Add greeting response logic
- `ui/chat_interface.py` - Handle conversational intents

**Logic**:
- If intent is "greeting", return friendly greeting without retrieval
- If intent is "general_conversation", generate conversational response without retrieval
- For all other intents, maintain existing RAG-based flow

### Step 4: Update Response Generator for Contextual Responses
**File**: `services/response_generator.py`

**Changes**:
- Accept `conversation_history` parameter
- Build messages array with full conversation history (user/assistant alternating)
- Limit history to last 10 messages to avoid token limits
- Use OpenAI's chat format with role-based messages

### Step 5: Update Intent Classifier for Context Awareness
**File**: `services/intent_classifier.py`

**Changes**:
- Accept `conversation_history` parameter
- Include last 3-5 messages in prompt for context
- Update prompt to help classifier understand conversational context
- Example: "If this is a greeting or continuation of conversation, classify as 'greeting' or 'general_conversation'"

### Step 6: Update Pipeline Flow
**File**: `ui/chat_interface.py`

**Changes**:
1. Extract conversation history from `st.session_state.chat_history`
2. Format as list of dicts: `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]`
3. Pass to `run_pipeline_async()` as `conversation_history`
4. Update all service calls to pass conversation_history where needed

### Step 7: Testing
- Test greeting response ("hi", "hello")
- Test follow-up questions
- Test multi-turn conversations
- Test that knowledge-seeking queries still work
- Test that escalation still works appropriately

## Implementation Details

### Conversation History Format
```python
conversation_history = [
    {"role": "user", "content": "hi"},
    {"role": "assistant", "content": "Hello! How can I help you today?"},
    {"role": "user", "content": "What are your fees?"},
    {"role": "assistant", "content": "Our fees vary by product..."}
]
```

### Intent Classifier Prompt Update
Include conversation context:
```
Previous conversation:
{format_conversation_history(conversation_history[-5:])}

Current query: {user_query}
```

### Response Generator Messages Update
```python
messages = [
    {"role": "system", "content": system_prompt},
    *format_conversation_history(conversation_history[-20:]),
    {"role": "user", "content": f"User Query: {user_query}\n\nContext:\n{context}"}
]
```

### Greeting Response Logic
```python
if intent_name == "greeting":
    # Return friendly greeting without retrieval
    greeting_responses = {
        "customer": "Hello! I'm here to help you with ANZ banking questions. How can I assist you today?",
        "banker": "Hello! I'm here to help you with policy lookups and process questions. What can I help you with?"
    }
    return {"response_text": greeting_responses[assistant_mode], ...}
```

## Files to Modify

1. `utils/constants.py` - Add greeting and general_conversation intents
2. `ui/chat_interface.py` - Pass conversation history to pipeline
3. `services/intent_classifier.py` - Accept and use conversation history
4. `services/response_generator.py` - Accept and use conversation history, add greeting handling
5. `services/retrieval_service.py` - Optional: Pass conversation context for better retrieval (future enhancement)

## Risk Assessment

**Low Risk Changes**:
- Adding intents to constants (backward compatible)
- Adding optional parameters to functions
- Adding greeting response logic (doesn't affect existing flow)

**Medium Risk Changes**:
- Modifying message construction in response generator (could affect output format)
- Updating intent classifier prompt (could change classification behavior)

**Mitigation**:
- Test thoroughly with existing queries
- Keep existing logic for non-conversational intents
- Add feature flags if needed

## Additional Requirements (User Feedback)

### Issue 4: Duplicate Message Display
**Problem**: Escalation messages are displayed twice - once as regular response and once as error box.

**Solution**: Fix UI to only display escalation message once, not duplicating it.

### Issue 5: Poor "Unknown" Intent Handling
**Problem**: Unknown queries immediately escalate. Should try to provide helpful guidance or rephrase suggestions.

**Solution**: 
- For "unknown" intent, attempt to provide helpful guidance
- Suggest possible queries the system can handle
- Only escalate if truly cannot provide any value

### Issue 6: Missing/Incorrect Citation URLs
**Problem**: Citations don't have proper webpage links. Critical for RAG responses.

**Solution**:
- Add Supabase lookup method to get document metadata (title, URL) by file_id
- Enhance retrieval service to lookup and enrich citations with URLs
- Ensure multiple citations are extracted when available
- Map file_ids from OpenAI annotations to actual document URLs stored in Supabase

## Success Criteria

1. ✅ User says "hi" → Gets friendly greeting back (no escalation)
2. ✅ User says "hello" → Gets greeting response
3. ✅ User asks "What are your fees?" then "Tell me more" → System understands context
4. ✅ Multi-turn conversations work with context awareness
5. ✅ Knowledge-seeking queries still work as before
6. ✅ Escalation logic still works for sensitive queries
7. ✅ **NEW**: No duplicate messages displayed in UI
8. ✅ **NEW**: Unknown queries provide helpful guidance instead of immediate escalation
9. ✅ **NEW**: All citations have correct webpage URLs
10. ✅ **NEW**: Multiple citations displayed when available
