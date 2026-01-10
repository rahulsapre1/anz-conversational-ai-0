import asyncio
import time
import re
from typing import Optional, Dict, Any, List
from utils.openai_client import get_openai_client
from utils.logger import get_logger
from config import Config

logger = get_logger(__name__)

# System prompts
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


class ResponseGenerator:
    """Generate responses with citations using OpenAI Chat Completions API."""
    
    def __init__(self):
        self.client = get_openai_client()
        self.timeout = Config.API_TIMEOUT
    
    async def generate(
        self,
        user_query: str,
        retrieved_chunks: List[str],
        assistant_mode: str,
        intent_name: Optional[str] = None,
        citations: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate response with citations (async with timeout).
        
        Args:
            user_query: Original user query
            retrieved_chunks: List of retrieved chunk strings from retrieval service
            assistant_mode: 'customer' or 'banker'
            intent_name: Intent name (optional, for logging)
            citations: List of citations from retrieval service (optional)
            conversation_history: Optional list of previous messages
        
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
        
        # Handle greeting intent without retrieval
        if intent_name == "greeting":
            greeting_responses = {
                "customer": "Hello! I'm here to help you with ANZ banking questions. How can I assist you today?",
                "banker": "Hello! I'm here to help you with policy lookups and process questions. What can I help you with?"
            }
            response_text = greeting_responses.get(assistant_mode, greeting_responses["customer"])
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(
                "greeting_response_generated",
                assistant_mode=assistant_mode,
                processing_time_ms=processing_time
            )
            return {
                "response_text": response_text,
                "citations": [],
                "has_synthetic_content": False,
                "response_generation_time_ms": int(processing_time)
            }
        
        # Handle unknown intent with helpful guidance
        if intent_name == "unknown":
            guidance_responses = {
                "customer": """I'm not entirely sure what you're looking for, but I can help with:

• **Account questions**: Fees, limits, transactions, applications
• **Product information**: Cards, accounts, loans, savings
• **Process guidance**: How to apply, dispute processes, card issues

Could you rephrase your question, or tell me what you'd like to know about? I can also connect you with our customer service team if you prefer.""",
                "banker": """I'm not entirely sure what you're looking for, but I can help with:

• **Policy lookups**: Terms, conditions, bank policies
• **Process clarification**: Workflows, procedures, compliance
• **Product information**: Features, eligibility, documentation requirements

Could you rephrase your question, or specify what you'd like to know? I can also suggest escalating to a specialist team if needed."""
            }
            response_text = guidance_responses.get(assistant_mode, guidance_responses["customer"])
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(
                "unknown_intent_guidance_generated",
                assistant_mode=assistant_mode,
                processing_time_ms=processing_time
            )
            return {
                "response_text": response_text,
                "citations": [],
                "has_synthetic_content": False,
                "response_generation_time_ms": int(processing_time)
            }
        
        # Check if we have retrieved chunks for knowledge-based queries
        if not retrieved_chunks:
            processing_time = (time.time() - start_time) * 1000
            logger.warning(
                "no_retrieved_chunks",
                assistant_mode=assistant_mode,
                intent_name=intent_name,
                processing_time_ms=processing_time
            )
            # Provide helpful guidance instead of generic escalation message
            if intent_name == "general_conversation":
                return {
                    "response_text": "I'm here to help! Could you let me know what specific information you're looking for? I can assist with ANZ banking questions, product information, and processes.",
                    "citations": [],
                    "has_synthetic_content": False,
                    "response_generation_time_ms": int(processing_time)
                }
            return {
                "response_text": "I don't have enough information to answer your question. Could you rephrase it, or would you like me to connect you with ANZ customer service?",
                "citations": [],
                "has_synthetic_content": False,
                "response_generation_time_ms": int(processing_time)
            }
        
        # Format context from retrieved chunks
        context = self._format_context(retrieved_chunks)
        
        # Get system prompt based on mode
        system_prompt = SYSTEM_PROMPT_CUSTOMER if assistant_mode == "customer" else SYSTEM_PROMPT_BANKER
        
        # Build messages array with conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (last 10 messages for context, but avoid token limits)
        if conversation_history:
            history_slice = conversation_history[-10:]  # Last 10 messages
            for msg in history_slice:
                if msg.get("role") in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg.get("content", "")
                    })
        
        # Add current user query with retrieved context
        messages.append({
            "role": "user", 
            "content": f"User Query: {user_query}\n\nContext:\n{context}"
        })
        
        # Generate response with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Run synchronous OpenAI call in thread pool with timeout
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.client.chat_completion,
                        messages=messages,
                        temperature=0.7,  # Balanced creativity and consistency
                        max_tokens=1000
                    ),
                    timeout=self.timeout
                )
                
                if response:
                    # Parse response
                    response_text = response.get("content", "")
                    
                    if not response_text:
                        logger.warning("empty_response", attempt=attempt + 1)
                        if attempt < max_retries - 1:
                            continue
                        else:
                            return None
                    
                    # Clean response text: replace file citation placeholders and sanitize markdown
                    response_text = self._clean_response_text(response_text, citations)
                    
                    # Extract citations from response text
                    extracted_citations = self._extract_citations(response_text, citations)
                    
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
                        citations_count=len(extracted_citations),
                        has_synthetic_content=has_synthetic,
                        processing_time_ms=processing_time,
                        intent_name=intent_name
                    )
                    
                    return {
                        "response_text": response_text,
                        "citations": extracted_citations,
                        "has_synthetic_content": has_synthetic,
                        "response_generation_time_ms": int(processing_time)
                    }
                else:
                    logger.warning("empty_response", attempt=attempt + 1)
            
            except asyncio.TimeoutError:
                processing_time = (time.time() - start_time) * 1000
                logger.error(
                    "response_generation_timeout",
                    attempt=attempt + 1,
                    timeout=self.timeout,
                    processing_time_ms=processing_time,
                    assistant_mode=assistant_mode
                )
                if attempt == max_retries - 1:
                    return None
            
            except Exception as e:
                processing_time = (time.time() - start_time) * 1000
                logger.error(
                    "response_generation_error",
                    attempt=attempt + 1,
                    error=str(e),
                    error_type=type(e).__name__,
                    processing_time_ms=processing_time,
                    assistant_mode=assistant_mode
                )
                if attempt == max_retries - 1:
                    return None
            
            # Wait before retry (exponential backoff)
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
        
        return None
    
    def _clean_response_text(self, response_text: str, citations: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Clean response text by replacing file citation placeholders and fixing markdown issues.
        
        Args:
            response_text: Raw response text from OpenAI
            citations: Optional list of citations to map file IDs to citation numbers
        
        Returns:
            Cleaned response text
        """
        # Replace file citation placeholders like [file-xyz] or similar patterns
        # OpenAI might include raw file IDs that need to be replaced with citation numbers
        if citations:
            # Create mapping from file_id to citation number
            file_id_to_number = {}
            for citation in citations:
                file_id = citation.get("file_id")
                number = citation.get("number")
                if file_id and number:
                    file_id_to_number[file_id] = number
            
            # Replace file ID patterns with citation numbers
            # Pattern to match file citations like [file-xyz] or similar
            file_pattern = r'\[file-([a-zA-Z0-9_-]+)\]'
            def replace_file_citation(match):
                file_id = f"file-{match.group(1)}"
                if file_id in file_id_to_number:
                    return f"[{file_id_to_number[file_id]}]"
                return match.group(0)  # Keep original if no mapping found
            
            response_text = re.sub(file_pattern, replace_file_citation, response_text)
        
        # Fix common markdown formatting issues
        # Remove any malformed markdown that might cause rendering issues
        # For now, just ensure the text is properly formatted
        
        return response_text
    
    def _format_context(self, retrieved_chunks: List[str]) -> str:
        """
        Format retrieved chunks as context for the prompt.
        
        Args:
            retrieved_chunks: List of retrieved chunk strings
        
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, chunk in enumerate(retrieved_chunks, 1):
            # Format each chunk with a number
            context_parts.append(f"[{i}] {chunk}")
            context_parts.append("")  # Empty line between chunks
        
        return "\n".join(context_parts)
    
    def _extract_citations(self, response_text: str, retrieval_citations: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Extract citations from response text and match with retrieval citations.
        
        Args:
            response_text: Generated response text
            retrieval_citations: List of citations from retrieval service (optional)
        
        Returns:
            List of citation dictionaries
        """
        citations = []
        
        # Find all citation references like [1], [2], etc.
        citation_pattern = r'\[(\d+)\]'
        matches = re.findall(citation_pattern, response_text)
        
        # Get unique citation numbers
        citation_numbers = sorted(set([int(m) for m in matches]))
        
        # Map citation numbers to retrieval citations if available
        if retrieval_citations:
            # Create a mapping from citation number to citation data
            citation_map = {}
            for citation in retrieval_citations:
                num = citation.get("number")
                if num:
                    citation_map[num] = citation
            
            # Use retrieval citations when available
            for num in citation_numbers:
                if num in citation_map:
                    citations.append(citation_map[num])
                else:
                    # Fallback: create basic citation
                    citations.append({
                        "number": num,
                        "source": f"Source {num}",
                        "url": ""
                    })
        else:
            # No retrieval citations - create basic citations
            for num in citation_numbers:
                citations.append({
                    "number": num,
                    "source": f"Source {num}",
                    "url": ""
                })
        
        return citations
    
    def _detect_synthetic_content(self, retrieved_chunks: List[str]) -> bool:
        """
        Detect if any retrieved chunks contain synthetic content.
        
        Args:
            retrieved_chunks: List of retrieved chunk strings
        
        Returns:
            True if synthetic content detected, False otherwise
        """
        synthetic_markers = [
            "SYNTHETIC CONTENT",
            "Label: SYNTHETIC",
            "Content Type: synthetic"
        ]
        
        for chunk in retrieved_chunks:
            if any(marker in chunk for marker in synthetic_markers):
                return True
        
        return False

async def generate_response(
    user_query: str,
    retrieved_chunks: List[str],
    assistant_mode: str,
    intent_name: Optional[str] = None,
    citations: Optional[List[Dict[str, Any]]] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Optional[Dict[str, Any]]:
    """Convenience function for response generation."""
    generator = ResponseGenerator()
    return await generator.generate(
        user_query, 
        retrieved_chunks, 
        assistant_mode, 
        intent_name, 
        citations,
        conversation_history
    )
