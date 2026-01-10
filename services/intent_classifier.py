import asyncio
import time
from typing import Optional, Dict, Any, List
from utils.openai_client import get_openai_client
from utils.constants import get_intent_taxonomy, get_valid_intents
from utils.validators import validate_intent_classification, sanitize_user_query
from utils.logger import get_logger
from config import Config
import json

logger = get_logger(__name__)

class IntentClassifier:
    """Classify user queries into intents."""
    
    def __init__(self):
        self.client = get_openai_client()
        self.timeout = Config.API_TIMEOUT
    
    async def classify(
        self,
        user_query: str,
        assistant_mode: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Classify user query into intent (async with timeout).

        Args:
            user_query: User query string
            assistant_mode: 'customer' or 'banker'
            conversation_history: Optional list of previous messages in format [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

        Returns:
            Dictionary with intent_name, intent_category, classification_reason
            or None on failure
        """
        start_time = time.time()

        # Debug: Log conversation history
        if conversation_history:
            logger.info(f"Intent classifier received conversation history: {len(conversation_history)} messages")
            for i, msg in enumerate(conversation_history):
                logger.info(f"History {i+1}: {msg.get('role')} - {msg.get('content', '')[:50]}...")
        else:
            logger.info("Intent classifier received no conversation history")

        # Sanitize input
        user_query = sanitize_user_query(user_query)
        if not user_query:
            logger.error("Empty user query after sanitization")
            return None
        
        # Get intent taxonomy for mode
        try:
            intent_taxonomy = get_intent_taxonomy(assistant_mode)
            valid_intents = get_valid_intents(assistant_mode)
        except ValueError as e:
            logger.error(f"Invalid assistant_mode: {assistant_mode}", error=str(e))
            return None
        
        # Construct prompt with conversation history context
        prompt = self._construct_prompt(
            user_query, 
            assistant_mode, 
            intent_taxonomy, 
            valid_intents,
            conversation_history
        )
        
        # Build messages array with conversation history
        messages = [{"role": "system", "content": prompt["system"]}]
        
        # Add conversation history (last 5 messages for context)
        if conversation_history:
            history_slice = conversation_history[-5:]  # Last 5 messages for context
            for msg in history_slice:
                if msg.get("role") in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg.get("content", "")
                    })
        
        # Add current user query
        messages.append({"role": "user", "content": prompt["user"]})
        
        try:
            # Run synchronous OpenAI call in thread pool with timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.chat_completion,
                    messages=messages,
                    temperature=0.3,  # Lower temperature for more consistent classification
                    response_format={"type": "json_object"}
                ),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            processing_time = (time.time() - start_time) * 1000
            logger.error(
                "Intent classification timeout",
                timeout_seconds=self.timeout,
                processing_time_ms=processing_time,
                user_query_preview=user_query[:50]
            )
            return None
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(
                "Intent classification error",
                error=str(e),
                error_type=type(e).__name__,
                processing_time_ms=processing_time,
                user_query_preview=user_query[:50]
            )
            return None
        
        if not response:
            processing_time = (time.time() - start_time) * 1000
            logger.error(
                "OpenAI API call failed for intent classification",
                processing_time_ms=processing_time,
                user_query_preview=user_query[:50]
            )
            return None
        
        # Parse JSON response
        content = response.get("content", "")
        if not content:
            processing_time = (time.time() - start_time) * 1000
            logger.error(
                "Empty response from OpenAI",
                processing_time_ms=processing_time,
                user_query_preview=user_query[:50]
            )
            return None
        
        intent_data = self.client.parse_json_response(content)
        if not intent_data:
            processing_time = (time.time() - start_time) * 1000
            logger.error(
                "Failed to parse JSON response",
                content_preview=content[:200],
                processing_time_ms=processing_time,
                user_query_preview=user_query[:50]
            )
            return None
        
        # Validate classification
        is_valid, error = validate_intent_classification(intent_data, assistant_mode)
        if not is_valid:
            processing_time = (time.time() - start_time) * 1000
            logger.error(
                "Invalid intent classification",
                error=error,
                intent_data=intent_data,
                processing_time_ms=processing_time,
                user_query_preview=user_query[:50]
            )
            # Default to unknown intent
            intent_data = {
                "intent_name": "unknown",
                "intent_category": "human_only",
                "classification_reason": f"Classification validation failed: {error}"
            }
        
        # Note: Unknown intents now default to automatable (changed to provide helpful guidance instead of escalation)
        # This is handled in the constants file
        
        # Add metadata
        intent_data["assistant_mode"] = assistant_mode
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(
            "Intent classification completed",
            intent_name=intent_data.get("intent_name"),
            intent_category=intent_data.get("intent_category"),
            assistant_mode=assistant_mode,
            processing_time_ms=processing_time,
            user_query_length=len(user_query),
            user_query_preview=user_query[:50]
        )
        
        return intent_data
    
    def _construct_prompt(
        self,
        user_query: str,
        assistant_mode: str,
        intent_taxonomy: Dict[str, Any],
        valid_intents: list[str],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, str]:
        """Construct classification prompt with conversation context."""
        
        # Format intent list for prompt
        intent_list = []
        for intent_name, intent_info in intent_taxonomy.items():
            intent_list.append(
                f"- {intent_name} ({intent_info['category']}): {intent_info['description']}"
            )
        
        intent_list_str = "\n".join(intent_list)
        
        # Build conversation context text if available
        conversation_context = ""
        if conversation_history:
            context_lines = []
            for msg in conversation_history[-3:]:  # Last 3 messages for context
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    context_lines.append(f"User: {content}")
                elif role == "assistant":
                    context_lines.append(f"Assistant: {content}")
            if context_lines:
                conversation_context = "\nPrevious conversation:\n" + "\n".join(context_lines) + "\n\n"
                logger.info(f"Intent classifier prompt context: {conversation_context.strip()}")
        
        system_prompt = f"""You are an intent classification system for a banking assistant.

Your task is to classify user queries into one of the predefined intents.

Available intents for {assistant_mode} mode:
{intent_list_str}

Intent categories:
- automatable: Can be answered automatically using knowledge base (includes greetings and general conversation)
- sensitive: Requires authentication or sensitive handling, should escalate
- human_only: Must be handled by human, should escalate immediately

Special handling:
- If the query is a greeting (hi, hello, hey, good morning, etc.), classify as "greeting" with category "automatable"
- Use conversation context to understand follow-up questions - if the previous conversation was about a specific topic (like card disputes), classify follow-up questions under that intent rather than "general_conversation"
- Only classify as "general_conversation" for truly general, off-topic, or conversational queries that don't relate to the previous banking topic
- If the query doesn't match any specific intent but could be answered with general guidance, use "unknown" with category "automatable" (we'll provide helpful guidance)
- Only use "human_only" category for queries that truly require human intervention (account access, financial advice, complaints, etc.)

Respond with a JSON object with the following structure:
{{
    "intent_name": "<intent_name>",
    "intent_category": "<automatable|sensitive|human_only>",
    "classification_reason": "<brief explanation>"
}}

Be accurate and consistent. Consider the full context of the query and any previous conversation."""

        user_prompt = f"{conversation_context}Classify this query, considering the conversation context above: {user_query}"

        return {
            "system": system_prompt,
            "user": user_prompt
        }

async def classify_intent(
    user_query: str, 
    assistant_mode: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Optional[Dict[str, Any]]:
    """Convenience function for intent classification."""
    classifier = IntentClassifier()
    return await classifier.classify(user_query, assistant_mode, conversation_history)
