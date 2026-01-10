from openai import OpenAI
from typing import Optional, Dict, Any, List
from config import Config
import logging
import json
import time

logger = logging.getLogger(__name__)

class OpenAIClient:
    """Wrapper for OpenAI API operations."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        logger.info(f"OpenAI client initialized with model: {self.model}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Make a chat completion request with retry logic.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            response_format: Optional response format (e.g., {"type": "json_object"})
            tools: Optional list of tools (e.g., file_search)
            tool_choice: Optional tool choice configuration
            max_retries: Maximum number of retry attempts
        
        Returns:
            Response dictionary with content, tool_calls, usage, or None on failure
        """
        for attempt in range(max_retries):
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                }
                
                if max_tokens:
                    kwargs["max_tokens"] = max_tokens
                
                if response_format:
                    kwargs["response_format"] = response_format
                
                if tools:
                    kwargs["tools"] = tools
                
                if tool_choice:
                    kwargs["tool_choice"] = tool_choice
                
                response = self.client.chat.completions.create(**kwargs)
                
                message = response.choices[0].message
                result = {
                    "content": message.content,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }
                }
                
                # Include tool calls if present
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    result["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            } if tc.function else None
                        }
                        for tc in message.tool_calls
                    ]
                
                # Include annotations if present (for citations)
                if hasattr(message, 'annotations') and message.annotations:
                    result["annotations"] = [
                        {
                            "type": ann.type,
                            "text": ann.text,
                            "file_id": ann.file_id if hasattr(ann, 'file_id') else None,
                            "quote": ann.quote if hasattr(ann, 'quote') else None
                        }
                        for ann in message.annotations
                    ]
                
                return result
            except Exception as e:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.warning(f"OpenAI API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                else:
                    logger.error(f"OpenAI API call failed after {max_retries} attempts")
                    return None
        
        return None
    
    def parse_json_response(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse JSON response from OpenAI.
        
        Args:
            content: Response content string
        
        Returns:
            Parsed JSON dictionary or None
        """
        try:
            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end].strip()
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response content: {content}")
            return None

# Singleton instance
_openai_client: Optional[OpenAIClient] = None

def get_openai_client() -> OpenAIClient:
    """Get singleton OpenAI client instance."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client
