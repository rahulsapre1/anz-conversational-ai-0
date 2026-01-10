# Task 8: Intent Classification Service

## Overview
Implement intent classification service using OpenAI gpt-4o-mini with structured JSON output.

## Prerequisites
- Task 1, 3 completed (OpenAI client, intent taxonomy)

## Deliverables

### services/intent_classifier.py

```python
import asyncio
import time
from typing import Optional, Dict, Any
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
    
    def classify(
        self,
        user_query: str,
        assistant_mode: str
    ) -> Optional[Dict[str, Any]]:
        """
        Classify user query into intent.
        
        Args:
            user_query: User query string
            assistant_mode: 'customer' or 'banker'
        
        Returns:
            Dictionary with intent_name, intent_category, classification_reason
            or None on failure
        """
        # Sanitize input
        user_query = sanitize_user_query(user_query)
        if not user_query:
            logger.error("Empty user query")
            return None
        
        # Get intent taxonomy for mode
        intent_taxonomy = get_intent_taxonomy(assistant_mode)
        valid_intents = get_valid_intents(assistant_mode)
        
        # Construct prompt
        prompt = self._construct_prompt(user_query, assistant_mode, intent_taxonomy, valid_intents)
        
        # Make API call
        messages = [
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]}
        ]
        
        response = self.client.chat_completion(
            messages=messages,
            temperature=0.3,  # Lower temperature for more consistent classification
            response_format={"type": "json_object"}
        )
        
        if not response:
            logger.error("OpenAI API call failed for intent classification")
            return None
        
        # Parse JSON response
        content = response.get("content", "")
        if not content:
            logger.error("Empty response from OpenAI")
            return None
        
        intent_data = self.client.parse_json_response(content)
        if not intent_data:
            logger.error(f"Failed to parse JSON response: {content}")
            return None
        
        # Validate classification
        is_valid, error = validate_intent_classification(intent_data, assistant_mode)
        if not is_valid:
            logger.error(f"Invalid intent classification: {error}")
            # Default to unknown intent
            intent_data = {
                "intent_name": "unknown",
                "intent_category": "human_only",
                "classification_reason": f"Classification validation failed: {error}"
            }
        
        # Ensure unknown intents default to human_only
        if intent_data.get("intent_name") == "unknown":
            intent_data["intent_category"] = "human_only"
        
        # Add metadata
        intent_data["assistant_mode"] = assistant_mode
        
        logger.info(f"Classified query: '{user_query[:50]}...' as {intent_data.get('intent_name')}")
        
        return intent_data
    
    def _construct_prompt(
        self,
        user_query: str,
        assistant_mode: str,
        intent_taxonomy: Dict[str, Any],
        valid_intents: list[str]
    ) -> Dict[str, str]:
        """Construct classification prompt."""
        
        # Format intent list for prompt
        intent_list = []
        for intent_name, intent_info in intent_taxonomy.items():
            intent_list.append(
                f"- {intent_name} ({intent_info['category']}): {intent_info['description']}"
            )
        
        intent_list_str = "\n".join(intent_list)
        
        system_prompt = f"""You are an intent classification system for a banking assistant.

Your task is to classify user queries into one of the predefined intents.

Available intents for {assistant_mode} mode:
{intent_list_str}

Intent categories:
- automatable: Can be answered automatically using knowledge base
- sensitive: Requires authentication or sensitive handling, should escalate
- human_only: Must be handled by human, should escalate immediately

Respond with a JSON object with the following structure:
{{
    "intent_name": "<intent_name>",
    "intent_category": "<automatable|sensitive|human_only>",
    "classification_reason": "<brief explanation>"
}}

If the query doesn't match any intent, use "unknown" as intent_name and "human_only" as intent_category.

Be accurate and consistent. Consider the full context of the query."""

        user_prompt = f"Classify this query: {user_query}"

        return {
            "system": system_prompt,
            "user": user_prompt
        }

def classify_intent(user_query: str, assistant_mode: str) -> Optional[Dict[str, Any]]:
    """Convenience function for intent classification."""
    classifier = IntentClassifier()
    return classifier.classify(user_query, assistant_mode)
```

## Usage Example

```python
from services.intent_classifier import classify_intent

# Classify customer query
result = classify_intent("What are the fees for my account?", "customer")
print(result)
# {
#     "intent_name": "fee_inquiry",
#     "intent_category": "automatable",
#     "classification_reason": "User asking about standard account fees",
#     "assistant_mode": "customer"
# }

# Classify banker query
result = classify_intent("What is the policy on fee waivers?", "banker")
print(result)
# {
#     "intent_name": "policy_lookup",
#     "intent_category": "automatable",
#     "classification_reason": "User asking about policy information",
#     "assistant_mode": "banker"
# }
```

## Error Handling

- **Empty query**: Returns None, logs error
- **API failure**: Returns None after retries, logs error
- **Malformed JSON**: Returns None, logs error (handled by parse_json_response)
- **Invalid classification**: Defaults to "unknown" intent with "human_only" category
- **Unknown intent**: Automatically sets category to "human_only"

## Validation Checklist

- [ ] Classifies user queries into correct intents
- [ ] Returns intent_name, intent_category, classification_reason
- [ ] Handles malformed JSON (returns None, logs error)
- [ ] Retries on API failures (3 attempts with exponential backoff)
- [ ] Defaults unknown intents to "human_only"
- [ ] Validates classification output
- [ ] Logs classification decisions

## Integration Points

- **Task 9**: Router will use intent_category from this service
- **Task 14**: Logger will log intent classification results

## Notes

- Uses structured output with JSON schema (response_format)
- Lower temperature (0.3) for consistency
- Unknown intents automatically route to escalation
- Classification reason helps with debugging and analytics

## Success Criteria

✅ Classifies queries into correct intents for both modes
✅ Returns properly formatted JSON output
✅ Handles errors gracefully
✅ Defaults to human_only for unknown/unclassifiable queries
