# Task 12: Confidence Scoring Service

## Overview
Implement confidence scoring service using OpenAI gpt-4o-mini to perform LLM self-assessment of response quality. Compares confidence score against threshold (0.68) to determine if response should be escalated.

## Prerequisites
- Task 1 completed (project structure, config, logging)
- Task 3 completed (OpenAI client setup)
- Task 11 completed (Response generator)
- Virtual environment activated

## Deliverables

### 1. Confidence Scorer Service (services/confidence_scorer.py)

Create `services/confidence_scorer.py` with async confidence scoring functionality.

**Key Requirements**:
- Async implementation with 30s timeout
- LLM self-assessment prompt
- Confidence score parsing (0.0-1.0)
- Threshold comparison (> 0.68)
- Error handling (default to low confidence on failures)
- Structured logging

## Implementation

### Step 1: Confidence Assessment Prompt

```python
# services/confidence_scorer.py
CONFIDENCE_PROMPT_TEMPLATE = """On a scale of 0.0 to 1.0, how confident are you that the response you provided accurately answers the user's query based solely on the retrieved context?

Consider the following factors:
1. **Completeness**: Does the response fully address the user's query?
2. **Accuracy**: Is the information in the response accurate based on the context?
3. **Relevance**: Is the response directly relevant to what the user asked?
4. **Information Availability**: Is all necessary information present in the retrieved context?

User Query: {user_query}

Response: {response_text}

Retrieved Context Summary: {context_summary}

Respond with ONLY a JSON object in this exact format:
{{
    "confidence": 0.85,
    "reasoning": "Brief explanation of your confidence level"
}}

The confidence score should be between 0.0 and 1.0, where:
- 0.0-0.3: Very low confidence (major gaps or inaccuracies)
- 0.3-0.5: Low confidence (some gaps or uncertainties)
- 0.5-0.7: Moderate confidence (mostly accurate but some limitations)
- 0.7-0.9: High confidence (accurate and complete)
- 0.9-1.0: Very high confidence (completely accurate and comprehensive)
"""
```

### Step 2: Confidence Scorer Implementation

```python
# services/confidence_scorer.py
import asyncio
import time
import json
import re
from typing import Optional, Dict, Any, List
from utils.openai_client import get_openai_client
from utils.logger import get_logger
from config import Config

logger = get_logger(__name__)

# Confidence prompt (from Step 1)
CONFIDENCE_PROMPT_TEMPLATE = """..."""  # See Step 1


class ConfidenceScorer:
    """Score confidence of generated responses using LLM self-assessment."""
    
    def __init__(self):
        self.client = get_openai_client()
        self.model = Config.OPENAI_MODEL
        self.threshold = Config.CONFIDENCE_THRESHOLD  # Default: 0.68
    
    async def score_async(
        self,
        response_text: str,
        retrieved_chunks: List[Dict[str, Any]],
        user_query: str,
        assistant_mode: str = None
    ) -> Dict[str, Any]:
        """
        Score confidence of response (async with timeout).
        
        Args:
            response_text: Generated response text
            retrieved_chunks: List of retrieved chunks used for response
            user_query: Original user query
            assistant_mode: Assistant mode (optional, for logging)
        
        Returns:
            Dictionary with confidence_score, meets_threshold, threshold_value, reasoning
            On error, returns low confidence (meets_threshold=False)
        """
        start_time = time.time()
        logger.info(
            "confidence_scoring_started",
            assistant_mode=assistant_mode,
            response_length=len(response_text),
            retrieved_chunks_count=len(retrieved_chunks)
        )
        
        # Format context summary
        context_summary = self._format_context_summary(retrieved_chunks)
        
        # Construct prompt
        prompt = CONFIDENCE_PROMPT_TEMPLATE.format(
            user_query=user_query,
            response_text=response_text,
            context_summary=context_summary
        )
        
        # Generate confidence assessment with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await asyncio.wait_for(
                    self._call_openai_async(prompt),
                    timeout=Config.API_TIMEOUT
                )
                
                if response:
                    # Parse confidence score
                    confidence_result = self._parse_confidence_response(response)
                    
                    if confidence_result:
                        confidence_score = confidence_result["confidence"]
                        reasoning = confidence_result.get("reasoning", "")
                        meets_threshold = confidence_score >= self.threshold
                        
                        processing_time = (time.time() - start_time) * 1000
                        
                        if meets_threshold:
                            logger.info(
                                "confidence_scoring_completed",
                                confidence_score=confidence_score,
                                threshold=self.threshold,
                                meets_threshold=meets_threshold,
                                reasoning=reasoning,
                                processing_time_ms=processing_time
                            )
                        else:
                            logger.warn(
                                "low_confidence_score",
                                confidence_score=confidence_score,
                                threshold=self.threshold,
                                meets_threshold=meets_threshold,
                                reasoning=reasoning,
                                processing_time_ms=processing_time
                            )
                        
                        return {
                            "confidence_score": confidence_score,
                            "meets_threshold": meets_threshold,
                            "threshold_value": self.threshold,
                            "reasoning": reasoning
                        }
                    else:
                        logger.warn("confidence_parse_failed", attempt=attempt + 1)
            
            except asyncio.TimeoutError:
                processing_time = (time.time() - start_time) * 1000
                logger.error(
                    "confidence_scoring_timeout",
                    attempt=attempt + 1,
                    timeout=Config.API_TIMEOUT,
                    processing_time_ms=processing_time
                )
                if attempt == max_retries - 1:
                    # Default to low confidence on timeout
                    return self._default_low_confidence("timeout")
            
            except Exception as e:
                processing_time = (time.time() - start_time) * 1000
                logger.error(
                    "confidence_scoring_error",
                    attempt=attempt + 1,
                    error=str(e),
                    processing_time_ms=processing_time
                )
                if attempt == max_retries - 1:
                    # Default to low confidence on error
                    return self._default_low_confidence(f"error: {str(e)}")
            
            # Wait before retry (exponential backoff)
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
        
        # Final fallback: default to low confidence
        return self._default_low_confidence("all_retries_failed")
    
    async def _call_openai_async(self, prompt: str) -> Optional[str]:
        """
        Call OpenAI Chat Completions API for confidence assessment (async).
        
        Args:
            prompt: Confidence assessment prompt
        
        Returns:
            Response content or None on failure
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a confidence assessment assistant. Analyze responses and provide confidence scores as JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent scoring
                response_format={"type": "json_object"}  # Request JSON response
            )
            
            if response and response.choices:
                content = response.choices[0].message.content
                return content
            return None
        
        except Exception as e:
            logger.error("openai_api_call_error", error=str(e))
            return None
    
    def _parse_confidence_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse confidence score from LLM response.
        
        Args:
            response_text: LLM response text (should be JSON)
        
        Returns:
            Dictionary with confidence and reasoning, or None on parse failure
        """
        try:
            # Try to parse as JSON first
            data = json.loads(response_text)
            
            # Extract confidence score
            confidence = data.get("confidence")
            if confidence is None:
                # Try alternative keys
                confidence = data.get("confidence_score") or data.get("score")
            
            if confidence is None:
                logger.error("confidence_key_not_found", response_text=response_text[:200])
                return None
            
            # Convert to float and validate range
            try:
                confidence_float = float(confidence)
                # Clamp to 0.0-1.0 range
                confidence_float = max(0.0, min(1.0, confidence_float))
            except (ValueError, TypeError):
                logger.error("confidence_value_invalid", confidence=confidence)
                return None
            
            reasoning = data.get("reasoning", data.get("reason", ""))
            
            return {
                "confidence": confidence_float,
                "reasoning": reasoning
            }
        
        except json.JSONDecodeError:
            # Try to extract confidence from text using regex
            logger.warn("json_parse_failed_trying_regex", response_text=response_text[:200])
            return self._extract_confidence_from_text(response_text)
    
    def _extract_confidence_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract confidence score from text using regex (fallback).
        
        Args:
            text: Response text
        
        Returns:
            Dictionary with confidence and reasoning, or None
        """
        # Look for patterns like "confidence": 0.85 or "confidence": 0.85
        patterns = [
            r'"confidence"\s*:\s*([0-9.]+)',
            r'"confidence_score"\s*:\s*([0-9.]+)',
            r'"score"\s*:\s*([0-9.]+)',
            r'confidence[:\s]+([0-9.]+)',
            r'([0-9]\.[0-9]+)',  # Any decimal number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    confidence = float(match.group(1))
                    confidence = max(0.0, min(1.0, confidence))  # Clamp to range
                    
                    # Try to extract reasoning
                    reasoning_match = re.search(r'"reasoning"\s*:\s*"([^"]+)"', text, re.IGNORECASE)
                    reasoning = reasoning_match.group(1) if reasoning_match else ""
                    
                    logger.info("confidence_extracted_from_text", confidence=confidence)
                    return {
                        "confidence": confidence,
                        "reasoning": reasoning
                    }
                except (ValueError, IndexError):
                    continue
        
        logger.error("confidence_extraction_failed", text=text[:200])
        return None
    
    def _format_context_summary(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Format retrieved chunks as a summary for confidence assessment.
        
        Args:
            retrieved_chunks: List of retrieved chunks
        
        Returns:
            Formatted context summary string
        """
        if not retrieved_chunks:
            return "No context retrieved"
        
        summary_parts = [f"Retrieved {len(retrieved_chunks)} chunk(s):"]
        
        for i, chunk in enumerate(retrieved_chunks[:5], 1):  # Limit to first 5 chunks
            if isinstance(chunk, dict):
                content = chunk.get("content", chunk.get("text", ""))
                # Truncate long content
                if len(content) > 200:
                    content = content[:200] + "..."
                summary_parts.append(f"Chunk {i}: {content}")
            else:
                content = str(chunk)
                if len(content) > 200:
                    content = content[:200] + "..."
                summary_parts.append(f"Chunk {i}: {content}")
        
        if len(retrieved_chunks) > 5:
            summary_parts.append(f"... and {len(retrieved_chunks) - 5} more chunk(s)")
        
        return "\n".join(summary_parts)
    
    def _default_low_confidence(self, reason: str) -> Dict[str, Any]:
        """
        Return default low confidence result on error.
        
        Args:
            reason: Reason for defaulting to low confidence
        
        Returns:
            Dictionary with low confidence score
        """
        logger.error("defaulting_to_low_confidence", reason=reason)
        return {
            "confidence_score": 0.0,
            "meets_threshold": False,
            "threshold_value": self.threshold,
            "reasoning": f"Confidence scoring failed: {reason}. Defaulting to low confidence for safety."
        }
```

### Step 3: Integration with Pipeline

The confidence scorer is used after response generation:

```python
# Example usage in pipeline
from services.response_generator import ResponseGenerator
from services.confidence_scorer import ConfidenceScorer

# Step 4: Response Generation
response_generator = ResponseGenerator()
response_result = await response_generator.generate_async(
    user_query=user_query,
    retrieved_chunks=retrieval_result["retrieved_chunks"],
    assistant_mode=assistant_mode
)

# Step 5: Confidence Scoring
confidence_scorer = ConfidenceScorer()
confidence_result = await confidence_scorer.score_async(
    response_text=response_result["response_text"],
    retrieved_chunks=retrieval_result["retrieved_chunks"],
    user_query=user_query,
    assistant_mode=assistant_mode
)

if not confidence_result["meets_threshold"]:
    # Low confidence - escalate
    escalation_result = await handle_escalation(
        trigger_type="low_confidence",
        confidence_score=confidence_result["confidence_score"],
        assistant_mode=assistant_mode
    )
    return escalation_result
else:
    # High confidence - continue
    return response_result
```

## Output Format

The confidence scorer returns:

```python
{
    "confidence_score": 0.85,
    "meets_threshold": True,
    "threshold_value": 0.68,
    "reasoning": "The response accurately addresses the user's query with complete information from the retrieved context."
}
```

**On Error** (defaults to low confidence):
```python
{
    "confidence_score": 0.0,
    "meets_threshold": False,
    "threshold_value": 0.68,
    "reasoning": "Confidence scoring failed: timeout. Defaulting to low confidence for safety."
}
```

## Threshold Logic

- **Threshold**: 0.68 (configurable via `CONFIDENCE_THRESHOLD` env var)
- **Comparison**: `confidence_score >= threshold` → `meets_threshold = True`
- **Decision**:
  - `meets_threshold = True` → Continue with response
  - `meets_threshold = False` → Escalate to human

## Error Handling

- **API Failure**: Retries 3 times with exponential backoff
- **Timeout**: 30s timeout per attempt, defaults to low confidence after all retries
- **Parse Failure**: Tries regex extraction, defaults to low confidence if fails
- **All Errors**: Default to low confidence (safe default - escalates rather than giving potentially wrong answer)

## Success Criteria

- [ ] Asks model for confidence assessment (async, 30s timeout)
- [ ] Parses confidence score correctly (0.0-1.0 range)
- [ ] Compares against threshold (0.68)
- [ ] Returns score and threshold decision
- [ ] Handles parsing errors gracefully (log ERROR, default to low confidence)
- [ ] Handles timeouts (30s, log ERROR, default to low confidence)
- [ ] Logs all operations with processing times
- [ ] Uses structured logging (INFO for success, WARN for low scores, ERROR for failures)

## Testing

### Manual Testing

```python
# Test confidence scoring
import asyncio
from services.confidence_scorer import ConfidenceScorer

async def test():
    scorer = ConfidenceScorer()
    
    # Test with good response
    result = await scorer.score_async(
        response_text="Based on ANZ's fee schedule, the monthly account fee is $5.00 [1].",
        retrieved_chunks=[
            {"content": "ANZ monthly account fee is $5.00 for standard accounts.", "source": "ANZ Fee Schedule"}
        ],
        user_query="What is the monthly account fee?",
        assistant_mode="customer"
    )
    
    print(f"Confidence: {result['confidence_score']}")
    print(f"Meets Threshold: {result['meets_threshold']}")
    print(f"Reasoning: {result['reasoning']}")

asyncio.run(test())
```

### Test Low Confidence

```python
# Test with incomplete response
result = await scorer.score_async(
    response_text="I don't have complete information about that.",
    retrieved_chunks=[],
    user_query="What is the account fee?",
    assistant_mode="customer"
)

# Should return low confidence
assert result["meets_threshold"] == False
assert result["confidence_score"] < 0.68
```

### Test Error Handling

```python
# Test with invalid response (should handle gracefully)
result = await scorer.score_async(
    response_text="",  # Empty response
    retrieved_chunks=[],
    user_query="Test query",
    assistant_mode="customer"
)

# Should default to low confidence
assert result["meets_threshold"] == False
```

## Integration Points

- **Task 11 (Response Generator)**: Receives response_text from response generator
- **Task 10 (Retrieval Service)**: Receives retrieved_chunks for context
- **Task 13 (Escalation Handler)**: Triggers escalation if `meets_threshold = False`
- **Task 14 (Logging)**: Logs confidence scoring events
- **Task 18 (Main App)**: Used in main pipeline orchestration

## Pipeline Flow

```
Step 4: Response Generation
    ↓
    response_result = {
        "response_text": "...",
        "citations": [...],
        ...
    }
    ↓
Step 5: Confidence Scoring
    ↓
    confidence_result = await score_async(
        response_text,
        retrieved_chunks,
        user_query
    )
    ↓
    {
        "confidence_score": 0.85,
        "meets_threshold": True,
        ...
    }
    ↓
    if meets_threshold:
        Continue with response
    else:
        Escalate (Step 6)
```

## Notes

- **Safe Defaults**: Always defaults to low confidence on errors (escalates rather than giving wrong answer)
- **JSON Response Format**: Uses `response_format={"type": "json_object"}` for more reliable parsing
- **Fallback Parsing**: Has regex fallback if JSON parsing fails
- **Threshold Configurable**: Can be changed via `CONFIDENCE_THRESHOLD` env var
- **Async Required**: Uses async OpenAI client calls with timeout

## Reference

- **DETAILED_PLAN.md** Section 7.5 (Confidence Scoring)
- **TASK_BREAKDOWN.md** Task 12
- **Task 11 Guide**: For response generator output format
- **Task 13 Guide**: For escalation handler integration
