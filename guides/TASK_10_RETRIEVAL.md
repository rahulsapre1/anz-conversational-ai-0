# Task 10: Retrieval Service (OpenAI Vector Store + Chat Completions API)

## Overview
Implement retrieval service using OpenAI Vector Store and Chat Completions API with `file_search` tool for semantic retrieval.

## Prerequisites
- Task 1, 3, 6 completed (OpenAI client, Vector Store setup)

## Key Concepts

- **OpenAI Vector Store**: Managed vector store where files are uploaded and attached (OpenAI automatically parses/chunks/embeds)
- **Chat Completions API**: Direct API calls for retrieval using `file_search` tool
- **file_search tool**: Tool that references Vector Store IDs to retrieve relevant chunks
- **Multiple Vector Stores**: One per topic collection (customer/banker)

## Deliverables

### services/retrieval_service.py

```python
from typing import Optional, Dict, Any, List
from utils.openai_client import get_openai_client
from config import Config
import logging
import json

logger = logging.getLogger(__name__)

class RetrievalService:
    """Retrieval service using OpenAI Vector Store + Chat Completions API with file_search tool."""
    
    def __init__(self):
        self.client = get_openai_client()
        self.customer_vector_store_id = Config.OPENAI_VECTOR_STORE_ID_CUSTOMER
        self.banker_vector_store_id = Config.OPENAI_VECTOR_STORE_ID_BANKER
    
    def retrieve(
        self,
        user_query: str,
        assistant_mode: str
    ) -> Dict[str, Any]:
        """
        Retrieve relevant chunks using Chat Completions API with file_search tool.
        
        Args:
            user_query: User query string
            assistant_mode: 'customer' or 'banker'
        
        Returns:
            Dictionary with retrieved_chunks, citations, file_ids, success
        """
        # Select appropriate Vector Store ID
        vector_store_id = (
            self.customer_vector_store_id if assistant_mode == "customer"
            else self.banker_vector_store_id
        )
        
        if not vector_store_id:
            logger.error(f"No Vector Store ID configured for mode: {assistant_mode}")
            return {
                "retrieved_chunks": [],
                "citations": [],
                "file_ids": [],
                "success": False,
                "error": "No Vector Store configured"
            }
        
        try:
            # Call Chat Completions API with file_search tool
            response = self.client.chat_completion(
                messages=[
                    {
                        "role": "user",
                        "content": f"Retrieve relevant information for this query: {user_query}"
                    }
                ],
                tools=[
                    {
                        "type": "file_search",
                        "vector_store_ids": [vector_store_id]
                    }
                ],
                tool_choice={"type": "file_search"},  # Force file_search tool usage
                temperature=0.3
            )
            
            if not response:
                logger.error("Chat Completions API call failed for retrieval")
                return {
                    "retrieved_chunks": [],
                    "citations": [],
                    "file_ids": [],
                    "success": False,
                    "error": "API call failed"
                }
            
            # Parse response for tool calls
            content = response.get("content", "")
            retrieved_chunks = []
            citations = []
            file_ids = set()
            
            # Extract tool calls if present (OpenAI may return tool calls or content)
            # In practice, file_search tool returns results in tool calls
            # Check if response has tool calls or content
            
            # For file_search tool, the response typically includes:
            # - content: The retrieved information
            # - tool_calls: Metadata about files used
            
            # Parse citations from content (if OpenAI adds citation markers)
            # Or extract from tool_calls if available
            
            # For now, assume content contains the retrieved information
            # and we need to extract citations separately
            if content:
                retrieved_chunks.append(content)
                
                # Try to extract citations from content or metadata
                # Citations might be in format [file-xyz] or similar
                # This will depend on OpenAI's actual response format
                
            # If no content retrieved, check for errors
            if not retrieved_chunks:
                logger.warning("No chunks retrieved from Vector Store")
                return {
                    "retrieved_chunks": [],
                    "citations": [],
                    "file_ids": [],
                    "success": False,
                    "error": "No results found"
                }
            
            return {
                "retrieved_chunks": retrieved_chunks,
                "citations": citations,
                "file_ids": list(file_ids),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return {
                "retrieved_chunks": [],
                "citations": [],
                "file_ids": [],
                "success": False,
                "error": str(e)
            }

def retrieve_chunks(
    user_query: str,
    assistant_mode: str
) -> Dict[str, Any]:
    """Convenience function for retrieval."""
    service = RetrievalService()
    return service.retrieve(user_query, assistant_mode)
```

## Note on OpenAI API Response Format

**Important**: The actual response format from OpenAI's Chat Completions API with `file_search` tool may vary. The implementation above is a template. You may need to adjust based on:

1. **Response Structure**: Check if OpenAI returns tool calls, content, or both
2. **Citation Format**: Citations may be embedded in content or returned as separate metadata
3. **File IDs**: May be in tool_calls or response metadata

**Recommended**: Test with actual OpenAI API to understand exact response format, then adjust parsing logic accordingly.

## Alternative Implementation (More Explicit)

If the above doesn't work with actual API responses, here's an alternative approach:

```python
def retrieve(
    self,
    user_query: str,
    assistant_mode: str
) -> Dict[str, Any]:
    """Retrieve using explicit file_search approach."""
    
    vector_store_id = (
        self.customer_vector_store_id if assistant_mode == "customer"
        else self.banker_vector_store_id
    )
    
    if not vector_store_id:
        return {"retrieved_chunks": [], "citations": [], "file_ids": [], "success": False, "error": "No Vector Store configured"}
    
    try:
        # Make Chat Completions call with file_search
        response = self.client.client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a retrieval assistant. Retrieve relevant information using the file_search tool."},
                {"role": "user", "content": user_query}
            ],
            tools=[{
                "type": "file_search",
                "vector_store_ids": [vector_store_id]
            }],
            tool_choice={"type": "file_search"}
        )
        
        # Parse response
        message = response.choices[0].message
        
        # Extract retrieved content and citations
        retrieved_chunks = []
        citations = []
        file_ids = set()
        
        # Check for tool calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                if tool_call.type == "file_search":
                    # Extract file IDs from tool call
                    # (Actual structure depends on OpenAI API)
                    pass
        
        # Extract content
        if message.content:
            retrieved_chunks.append(message.content)
        
        # Extract citations from annotations or metadata
        # (Implementation depends on actual API response)
        
        return {
            "retrieved_chunks": retrieved_chunks,
            "citations": citations,
            "file_ids": list(file_ids),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return {
            "retrieved_chunks": [],
            "citations": [],
            "file_ids": [],
            "success": False,
            "error": str(e)
        }
```

## Vector Store Setup (from Task 6)

Vector Stores must be created with:
- Files uploaded via Files API
- Files attached to Vector Store (OpenAI automatically processes them)
- Vector Store ID used for retrieval

## Usage Example

```python
from services.retrieval_service import retrieve_chunks

# Retrieve chunks for customer query
result = retrieve_chunks(
    user_query="What are the fees for my account?",
    assistant_mode="customer"
)

print(result)
# {
#     "retrieved_chunks": ["Based on ANZ's fee schedule..."],
#     "citations": [
#         {
#             "number": 1,
#             "file_id": "file-abc123",
#             "quote": "Account fees are...",
#             "source": "ANZ Fee Schedule"
#         }
#     ],
#     "file_ids": ["file-abc123"],
#     "success": True
# }
```

## Error Handling

- **No Vector Store ID**: Returns empty result with error
- **API failure**: Returns empty result with error
- **No results**: Returns empty result, triggers escalation
- **Parsing errors**: Logs error, returns empty result

## Validation Checklist

- [ ] Uses Chat Completions API with file_search tool
- [ ] References correct Vector Store ID by mode
- [ ] Retrieves relevant chunks with citations
- [ ] Handles no results (returns empty, logs)
- [ ] Error handling with retries
- [ ] Extracts citations correctly from API response

## Integration Points

- **Task 6**: Vector Store must be created and files attached before retrieval
- **Task 11**: Response generator will use retrieved_chunks and citations
- **Task 14**: Logger will log retrieval results

## Notes

- **API Response Format**: The exact format of OpenAI's response may vary. Test with actual API and adjust parsing accordingly.
- **Citations**: Citations may be embedded in content, in tool calls, or as separate metadata. Implementation should handle actual format.
- **Session Management**: For Step 4 (Response Generation), we'll use the same retrieved context. Session continuity is maintained separately.

## Success Criteria

✅ Retrieves relevant chunks using Chat Completions API with file_search tool
✅ Extracts citations correctly (adjust based on actual API response format)
✅ Handles errors gracefully
✅ Returns structured data with citations
✅ Works with both customer and banker Vector Stores
