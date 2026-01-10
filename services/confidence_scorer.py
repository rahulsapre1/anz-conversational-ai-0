import asyncio
import time
import json
import re
from typing import Optional, Dict, Any, List
from utils.openai_client import get_openai_client
from utils.logger import get_logger
from config import Config

logger = get_logger(__name__)

# Confidence assessment prompt template
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


class ConfidenceScorer:
    """Score confidence of generated responses using LLM self-assessment."""
    
    def __init__(self):
        self.client = get_openai_client()
        self.threshold = Config.CONFIDENCE_THRESHOLD  # Default: 0.68
        self.timeout = Config.API_TIMEOUT
    
    async def score(
        self,
        response_text: str,
        retrieved_chunks: List[str],
        user_query: str,
        assistant_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Score confidence of response (async with timeout).
        
        Args:
            response_text: Generated response text
            retrieved_chunks: List of retrieved chunk strings used for response
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
                # Run synchronous OpenAI call in thread pool with timeout
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.client.chat_completion,
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
                        response_format={"type": "json_object"}
                    ),
                    timeout=self.timeout
                )
                
                if response:
                    # Parse confidence score
                    content = response.get("content", "")
                    confidence_result = self._parse_confidence_response(content)
                    
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
                                processing_time_ms=processing_time,
                                assistant_mode=assistant_mode
                            )
                        else:
                            logger.warning(
                                "low_confidence_score",
                                confidence_score=confidence_score,
                                threshold=self.threshold,
                                meets_threshold=meets_threshold,
                                reasoning=reasoning,
                                processing_time_ms=processing_time,
                                assistant_mode=assistant_mode
                            )
                        
                        return {
                            "confidence_score": confidence_score,
                            "meets_threshold": meets_threshold,
                            "threshold_value": self.threshold,
                            "reasoning": reasoning
                        }
                    else:
                        logger.warning("confidence_parse_failed", attempt=attempt + 1)
            
            except asyncio.TimeoutError:
                processing_time = (time.time() - start_time) * 1000
                logger.error(
                    "confidence_scoring_timeout",
                    attempt=attempt + 1,
                    timeout=self.timeout,
                    processing_time_ms=processing_time,
                    assistant_mode=assistant_mode
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
                    error_type=type(e).__name__,
                    processing_time_ms=processing_time,
                    assistant_mode=assistant_mode
                )
                if attempt == max_retries - 1:
                    # Default to low confidence on error
                    return self._default_low_confidence(f"error: {str(e)}")
            
            # Wait before retry (exponential backoff)
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
        
        # Final fallback: default to low confidence
        return self._default_low_confidence("all_retries_failed")
    
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
            data = self.client.parse_json_response(response_text)
            
            if not data:
                # Try regex extraction as fallback
                logger.warning("json_parse_failed_trying_regex", response_text=response_text[:200])
                return self._extract_confidence_from_text(response_text)
            
            # Extract confidence score
            confidence = data.get("confidence")
            if confidence is None:
                # Try alternative keys
                confidence = data.get("confidence_score") or data.get("score")
            
            if confidence is None:
                logger.error("confidence_key_not_found", response_text=response_text[:200])
                # Try regex extraction as fallback
                return self._extract_confidence_from_text(response_text)
            
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
        
        except Exception as e:
            logger.error("confidence_parse_exception", error=str(e))
            # Try regex extraction as fallback
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
    
    def _format_context_summary(self, retrieved_chunks: List[str]) -> str:
        """
        Format retrieved chunks as a summary for confidence assessment.
        
        Args:
            retrieved_chunks: List of retrieved chunk strings
        
        Returns:
            Formatted context summary string
        """
        if not retrieved_chunks:
            return "No context retrieved"
        
        summary_parts = [f"Retrieved {len(retrieved_chunks)} chunk(s):"]
        
        for i, chunk in enumerate(retrieved_chunks[:5], 1):  # Limit to first 5 chunks
            # Truncate long content
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

async def score_confidence(
    response_text: str,
    retrieved_chunks: List[str],
    user_query: str,
    assistant_mode: Optional[str] = None
) -> Dict[str, Any]:
    """Convenience function for confidence scoring."""
    scorer = ConfidenceScorer()
    return await scorer.score(response_text, retrieved_chunks, user_query, assistant_mode)
