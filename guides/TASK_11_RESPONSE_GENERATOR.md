# Task 11: Response Generation Service

## Overview
Implement response generation service using OpenAI gpt-4o-mini to generate responses with numbered citations based on retrieved chunks. Includes mode-specific prompts, synthetic content detection, and proper citation formatting.

## Prerequisites
- Task 1 completed (project structure, config, logging)
- Task 3 completed (OpenAI client setup)
- Task 10 completed (Retrieval service)
- Virtual environment activated

## Deliverables

### 1. Response Generator Service (services/response_generator.py)

Create `services/response_generator.py` with async response generation functionality.

**Key Requirements**:
- Async implementation with 30s timeout
- Mode-specific system prompts (Customer vs Banker)
- Response generation with numbered citations [1], [2], etc.
- Synthetic content detection and disclaimers
- Error handling with retries
- Structured logging

## Implementation

### Step 1: System Prompts

```python
# services/response_generator.py
SYSTEM_PROMPT_CUSTOMER = """You are a helpful banking assistant for ANZ customers. 

Your role is to provide clear, simple explanations about ANZ banking products, services, and processes.

Guidelines:
- Provide clear, simple explanations that are easy to understand
- Always cite sources using numbered references [1], [2], [3], etc. when referencing information
- If any content is marked as "SYNTHETIC CONTENT" or "Label: SYNTHETIC", clearly state: "Note: This information is based on synthetic content and may not reflect official ANZ policy."
- Only use information from the provided context - do not make up information
- If you don't have enough information to answer, say so clearly
- Be helpful, professional, and accurate
- Focus on what the customer needs to know

When citing sources:
- Use numbered references like [1], [2] in your response
- Reference the source documents provided in the context
- Make citations clear and easy to follow"""

SYSTEM_PROMPT_BANKER = """You are an internal banking assistant for ANZ staff. 

Your role is to provide technical, policy-focused responses to help frontline bankers and contact centre agents.

Guidelines:
- Provide technical, policy-focused responses
- Always include citations with numbered references [1], [2], [3], etc.
- If any content is marked as "SYNTHETIC CONTENT" or "Label: SYNTHETIC", clearly state: "Note: This information is based on synthetic content."
- Emphasize compliance and accuracy
- Only use information from the provided context
- If you don't have enough information, say so clearly
- Be precise and professional
- Focus on policy details and process steps

When citing sources:
- Use numbered references like [1], [2] in your response
- Reference the source documents provided in the context
- Make citations clear for verification purposes"""
```

### Step 2: Response Generator Implementation

```python
# services/response_generator.py
import asyncio
import time
import re
from typing import Optional, Dict, Any, List
from utils.openai_client import get_openai_client
from utils.logger import get_logger
from config import Config
import json

logger = get_logger(__name__)

# System prompts (from Step 1)
SYSTEM_PROMPT_CUSTOMER = """..."""  # See Step 1
SYSTEM_PROMPT_BANKER = """..."""    # See Step 1


class ResponseGenerator:
    """Generate responses with citations using OpenAI Chat Completions API."""
    
    def __init__(self):
        self.client = get_openai_client()
        self.model = Config.OPENAI_MODEL
    
    async def generate_async(
        self,
        user_query: str,
        retrieved_chunks: List[Dict[str, Any]],
        assistant_mode: str,
        intent_name: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate response with citations (async with timeout).
        
        Args:
            user_query: Original user query
            retrieved_chunks: List of retrieved chunks from retrieval service
            assistant_mode: 'customer' or 'banker'
            intent_name: Intent name (optional, for logging)
        
        Returns:
            Dictionary with response_text, citations, has_synthetic_content
            or None on failure
        """
        start_time = time.time()
        logger.info(
            "response_generation_started",
            assistant_mode=assistant_mode,
            intent_name=intent_name,
            retrieved_chunks_count=len(retrieved_chunks)
        )
        
        # Check if we have retrieved chunks
        if not retrieved_chunks:
            logger.warn("no_retrieved_chunks", assistant_mode=assistant_mode)
            return {
                "response_text": "I don't have enough information to answer your question. Please contact ANZ customer service for assistance.",
                "citations": [],
                "has_synthetic_content": False
            }
        
        # Format context from retrieved chunks
        context = self._format_context(retrieved_chunks)
        
        # Get system prompt based on mode
        system_prompt = SYSTEM_PROMPT_CUSTOMER if assistant_mode == "customer" else SYSTEM_PROMPT_BANKER
        
        # Construct messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User Query: {user_query}\n\nContext:\n{context}"}
        ]
        
        # Generate response with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await asyncio.wait_for(
                    self._call_openai_async(messages),
                    timeout=Config.API_TIMEOUT
                )
                
                if response:
                    # Parse response
                    response_text = response.get("content", "")
                    
                    # Extract citations from response
                    citations = self._extract_citations(response_text, retrieved_chunks)
                    
                    # Check for synthetic content
                    has_synthetic = self._detect_synthetic_content(retrieved_chunks)
                    
                    # Add synthetic disclaimer if needed
                    if has_synthetic and "synthetic content" not in response_text.lower():
                        response_text += "\n\nNote: This information is based on synthetic content and may not reflect official ANZ policy."
                    
                    processing_time = (time.time() - start_time) * 1000
                    logger.info(
                        "response_generation_completed",
                        assistant_mode=assistant_mode,
                        response_length=len(response_text),
                        citations_count=len(citations),
                        has_synthetic_content=has_synthetic,
                        processing_time_ms=processing_time
                    )
                    
                    return {
                        "response_text": response_text,
                        "citations": citations,
                        "has_synthetic_content": has_synthetic
                    }
                else:
                    logger.warn("empty_response", attempt=attempt + 1)
            
            except asyncio.TimeoutError:
                processing_time = (time.time() - start_time) * 1000
                logger.error(
                    "response_generation_timeout",
                    attempt=attempt + 1,
                    timeout=Config.API_TIMEOUT,
                    processing_time_ms=processing_time
                )
                if attempt == max_retries - 1:
                    return None
            
            except Exception as e:
                processing_time = (time.time() - start_time) * 1000
                logger.error(
                    "response_generation_error",
                    attempt=attempt + 1,
                    error=str(e),
                    processing_time_ms=processing_time
                )
                if attempt == max_retries - 1:
                    return None
            
            # Wait before retry (exponential backoff)
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
        
        return None
    
    async def _call_openai_async(self, messages: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        """
        Call OpenAI Chat Completions API (async).
        
        Args:
            messages: List of message dictionaries
        
        Returns:
            Response dictionary or None on failure
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,  # Balanced creativity and consistency
                max_tokens=1000   # Adjust based on needs
            )
            
            if response and response.choices:
                content = response.choices[0].message.content
                return {
                    "content": content,
                    "model": self.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0
                    }
                }
            return None
        
        except Exception as e:
            logger.error("openai_api_call_error", error=str(e))
            return None
    
    def _format_context(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Format retrieved chunks as context for the prompt.
        
        Args:
            retrieved_chunks: List of retrieved chunk dictionaries or strings
        
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, chunk in enumerate(retrieved_chunks, 1):
            # Handle both dict and string formats
            if isinstance(chunk, str):
                # Simple string chunk
                context_parts.append(f"[{i}] {chunk}")
            elif isinstance(chunk, dict):
                # Dictionary chunk with metadata
                content = chunk.get("content", chunk.get("text", ""))
                source = chunk.get("source", chunk.get("file_name", f"Source {i}"))
                url = chunk.get("url", chunk.get("source_url", ""))
                
                context_parts.append(f"[{i}] Source: {source}")
                if url:
                    context_parts.append(f"URL: {url}")
                context_parts.append(f"Content: {content}")
            else:
                # Fallback: convert to string
                context_parts.append(f"[{i}] {str(chunk)}")
            
            context_parts.append("")  # Empty line between chunks
        
        return "\n".join(context_parts)
    
    def _extract_citations(self, response_text: str, retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract citations from response text and match with retrieved chunks.
        
        Args:
            response_text: Generated response text
            retrieved_chunks: List of retrieved chunks (dicts or strings)
        
        Returns:
            List of citation dictionaries
        """
        citations = []
        
        # Find all citation references like [1], [2], etc.
        citation_pattern = r'\[(\d+)\]'
        matches = re.findall(citation_pattern, response_text)
        
        # Get unique citation numbers
        citation_numbers = sorted(set([int(m) for m in matches]))
        
        # Map citation numbers to chunks
        for num in citation_numbers:
            chunk_index = num - 1  # Convert to 0-based index
            if 0 <= chunk_index < len(retrieved_chunks):
                chunk = retrieved_chunks[chunk_index]
                
                # Handle both dict and string formats
                if isinstance(chunk, dict):
                    source = chunk.get("source", chunk.get("file_name", f"Source {num}"))
                    url = chunk.get("url", chunk.get("source_url", ""))
                else:
                    # String chunk - use generic source
                    source = f"Source {num}"
                    url = ""
                
                citations.append({
                    "number": num,
                    "source": source,
                    "url": url
                })
        
        return citations
    
    def _detect_synthetic_content(self, retrieved_chunks: List[Dict[str, Any]]) -> bool:
        """
        Detect if any retrieved chunks contain synthetic content.
        
        Args:
            retrieved_chunks: List of retrieved chunks (dicts or strings)
        
        Returns:
            True if synthetic content detected, False otherwise
        """
        synthetic_markers = [
            "SYNTHETIC CONTENT",
            "Label: SYNTHETIC",
            "Content Type: synthetic"
        ]
        
        for chunk in retrieved_chunks:
            # Handle both dict and string formats
            if isinstance(chunk, dict):
                content = chunk.get("content", chunk.get("text", ""))
            else:
                content = str(chunk)
            
            if any(marker in content for marker in synthetic_markers):
                return True
        
        return False
```

### Step 3: Integration with Retrieval Service

The response generator receives output from the retrieval service:

```python
# Example usage in pipeline
from services.retrieval_service import RetrievalService
from services.response_generator import ResponseGenerator

# Step 3: Retrieval
retrieval_service = RetrievalService()
retrieval_result = await retrieval_service.retrieve_async(
    user_query=user_query,
    assistant_mode=assistant_mode,
    intent_name=intent_name
)

if not retrieval_result or not retrieval_result.get("retrieved_chunks"):
    # Handle no results
    return handle_no_results()

# Step 4: Response Generation
response_generator = ResponseGenerator()
response_result = await response_generator.generate_async(
    user_query=user_query,
    retrieved_chunks=retrieval_result["retrieved_chunks"],
    assistant_mode=assistant_mode,
    intent_name=intent_name
)

if not response_result:
    # Handle generation failure
    return handle_generation_failure()

# Use response_result
response_text = response_result["response_text"]
citations = response_result["citations"]
has_synthetic = response_result["has_synthetic_content"]
```

## Response Format

The response generator returns:

```python
{
    "response_text": "Based on ANZ's fee schedule, the monthly account fee is $5.00 [1]. This fee applies to standard personal accounts [2].",
    "citations": [
        {
            "number": 1,
            "source": "ANZ Fee Schedule",
            "url": "https://www.anz.com.au/support/legal/rates-fees-terms/"
        },
        {
            "number": 2,
            "source": "ANZ Terms and Conditions",
            "url": "https://www.anz.com.au/support/legal/rates-fees-terms/fees-terms-conditions/bank-accounts/"
        }
    ],
    "has_synthetic_content": False
}
```

## Citation Formatting

Citations should appear in the response text as numbered references:

- `[1]` - First citation
- `[2]` - Second citation
- `[3]` - Third citation
- etc.

The citations list provides full metadata for each citation number.

## Synthetic Content Detection

The generator detects synthetic content by checking for markers:
- "SYNTHETIC CONTENT" in content
- "Label: SYNTHETIC" in content
- "Content Type: synthetic" in content

If synthetic content is detected:
- `has_synthetic_content` is set to `True`
- A disclaimer is added to the response if not already present

## Error Handling

- **No Retrieved Chunks**: Returns a helpful message asking user to contact support
- **API Failure**: Retries 3 times with exponential backoff
- **Timeout**: 30s timeout per attempt, logs ERROR, returns None after all retries
- **Empty Response**: Logs WARN, retries
- **All Errors**: Logged with structured logging

## Success Criteria

- [ ] Generates responses using gpt-4o-mini (async, 30s timeout)
- [ ] Uses mode-specific system prompts (Customer vs Banker)
- [ ] Includes numbered citations [1], [2], etc. in response
- [ ] Extracts citations as structured data
- [ ] Detects synthetic content correctly
- [ ] Adds synthetic content disclaimers when needed
- [ ] Handles errors gracefully (retries, timeouts)
- [ ] Logs all API calls with processing times
- [ ] Response format matches specification

## Testing

### Manual Testing

```python
# Test response generation
import asyncio
from services.response_generator import ResponseGenerator

async def test():
    generator = ResponseGenerator()
    
    # Mock retrieved chunks
    retrieved_chunks = [
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
    
    result = await generator.generate_async(
        user_query="What is the monthly account fee?",
        retrieved_chunks=retrieved_chunks,
        assistant_mode="customer"
    )
    
    print(f"Response: {result['response_text']}")
    print(f"Citations: {result['citations']}")
    print(f"Has Synthetic: {result['has_synthetic_content']}")

asyncio.run(test())
```

### Test Synthetic Content Detection

```python
# Test with synthetic content
retrieved_chunks_with_synthetic = [
    {
        "content": "Title: Account Closure - SYNTHETIC CONTENT\nLabel: SYNTHETIC\n...",
        "source": "Account Closure Process",
        "url": "synthetic://process/account_closure"
    }
]

result = await generator.generate_async(
    user_query="How do I close my account?",
    retrieved_chunks=retrieved_chunks_with_synthetic,
    assistant_mode="customer"
)

# Should detect synthetic content
assert result["has_synthetic_content"] == True
assert "synthetic content" in result["response_text"].lower()
```

## Integration Points

- **Task 10 (Retrieval Service)**: Receives retrieved_chunks from retrieval service
- **Task 12 (Confidence Scorer)**: Provides response_text for confidence scoring
- **Task 13 (Escalation Handler)**: May trigger escalation if generation fails
- **Task 14 (Logging)**: Logs response generation events
- **Task 18 (Main App)**: Used in main pipeline orchestration

## Pipeline Flow

```
Step 3: Retrieval
    ↓
    retrieval_result = {
        "retrieved_chunks": [...],
        "citations": [...],
        ...
    }
    ↓
Step 4: Response Generation
    ↓
    response_result = await generate_async(
        user_query,
        retrieved_chunks,
        assistant_mode
    )
    ↓
    {
        "response_text": "... [1] [2]",
        "citations": [...],
        "has_synthetic_content": False
    }
    ↓
Step 5: Confidence Scoring
```

## Notes

- **Async Required**: Uses async OpenAI client calls with timeout
- **Mode-Specific**: Different prompts for Customer vs Banker modes
- **Citation Format**: Must use numbered references [1], [2], etc.
- **Synthetic Detection**: Automatically detects and marks synthetic content
- **Error Recovery**: Retries on failures, escalates if all retries fail

## Reference

- **DETAILED_PLAN.md** Section 7.4 (Response Generation)
- **TASK_BREAKDOWN.md** Task 11
- **Task 10 Guide**: For retrieval service output format
- **Task 12 Guide**: For confidence scoring integration
