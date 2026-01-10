# Task 3: OpenAI Client Setup & Intent Taxonomy

## Overview
Set up OpenAI client wrapper, define intent taxonomy constants, and create validation helpers.

## Prerequisites
- Task 1 completed (project structure and config.py)
- OpenAI API key available

## Deliverables

### 1. OpenAI Client Wrapper (utils/openai_client.py)

```python
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
        max_retries: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Make a chat completion request with retry logic.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            response_format: Optional response format (e.g., {"type": "json_object"})
            max_retries: Maximum number of retry attempts
        
        Returns:
            Response dictionary or None on failure
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
                
                response = self.client.chat.completions.create(**kwargs)
                
                return {
                    "content": response.choices[0].message.content,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }
                }
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
```

### 2. Intent Taxonomy Constants (utils/constants.py)

```python
"""
Intent taxonomy constants based on PRD and README.
"""

# Customer Assistant Intents
CUSTOMER_INTENTS = {
    "transaction_explanation": {
        "category": "automatable",
        "description": "Questions about transaction details, codes, descriptions"
    },
    "fee_inquiry": {
        "category": "automatable",
        "description": "Questions about fees, charges, pricing"
    },
    "account_limits": {
        "category": "automatable",
        "description": "Questions about account limits, daily limits, transfer limits"
    },
    "card_dispute_process": {
        "category": "automatable",
        "description": "Guidance on disputing card transactions"
    },
    "application_process": {
        "category": "automatable",
        "description": "General information about account/product applications"
    },
    "account_balance": {
        "category": "sensitive",
        "description": "Account balance inquiries (escalate - needs authentication)"
    },
    "transaction_history": {
        "category": "sensitive",
        "description": "Transaction history requests (escalate - needs authentication)"
    },
    "password_reset": {
        "category": "sensitive",
        "description": "Password or security-related requests"
    },
    "financial_advice": {
        "category": "human_only",
        "description": "Requests for personalized financial advice"
    },
    "complaint": {
        "category": "human_only",
        "description": "Formal complaints or grievances"
    },
    "hardship": {
        "category": "human_only",
        "description": "Financial hardship indicators"
    },
    "fraud_alert": {
        "category": "human_only",
        "description": "Security/fraud concerns"
    },
    "unknown": {
        "category": "human_only",
        "description": "Unclassifiable or out-of-scope queries"
    }
}

# Banker Assistant Intents
BANKER_INTENTS = {
    "policy_lookup": {
        "category": "automatable",
        "description": "Looking up bank policies, terms, conditions"
    },
    "process_clarification": {
        "category": "automatable",
        "description": "Process steps, workflows, procedures"
    },
    "product_comparison": {
        "category": "automatable",
        "description": "Comparing products, features, differences"
    },
    "compliance_phrasing": {
        "category": "automatable",
        "description": "Guidance on compliant language, disclaimers"
    },
    "fee_structure": {
        "category": "automatable",
        "description": "Fee schedules, pricing information"
    },
    "eligibility_criteria": {
        "category": "automatable",
        "description": "Product eligibility requirements"
    },
    "documentation_requirements": {
        "category": "automatable",
        "description": "Required documents, forms, procedures"
    },
    "customer_specific_query": {
        "category": "sensitive",
        "description": "Questions requiring access to customer data"
    },
    "complex_case": {
        "category": "human_only",
        "description": "Complex cases requiring expert judgment"
    },
    "complaint_handling": {
        "category": "human_only",
        "description": "Formal complaint procedures"
    },
    "regulatory_question": {
        "category": "human_only",
        "description": "Regulatory or legal questions"
    },
    "unknown": {
        "category": "human_only",
        "description": "Unclassifiable or out-of-scope queries"
    }
}

# Intent categories
INTENT_CATEGORIES = ["automatable", "sensitive", "human_only"]

# Confidence threshold
CONFIDENCE_THRESHOLD = 0.68

# Escalation trigger types
ESCALATION_TRIGGERS = [
    "human_only",
    "low_confidence",
    "insufficient_evidence",
    "conflicting_evidence",
    "account_specific",
    "security_fraud",
    "financial_advice",
    "legal_hardship",
    "emotional_distress",
    "repeated_misunderstanding",
    "explicit_human_request"
]

def get_intent_taxonomy(mode: str) -> dict:
    """
    Get intent taxonomy for specified mode.
    
    Args:
        mode: 'customer' or 'banker'
    
    Returns:
        Dictionary of intents
    """
    if mode == "customer":
        return CUSTOMER_INTENTS
    elif mode == "banker":
        return BANKER_INTENTS
    else:
        raise ValueError(f"Invalid mode: {mode}")

def get_valid_intents(mode: str) -> list[str]:
    """
    Get list of valid intent names for specified mode.
    
    Args:
        mode: 'customer' or 'banker'
    
    Returns:
        List of intent names
    """
    taxonomy = get_intent_taxonomy(mode)
    return list(taxonomy.keys())

def get_intent_category(intent_name: str, mode: str) -> Optional[str]:
    """
    Get category for an intent.
    
    Args:
        intent_name: Name of intent
        mode: 'customer' or 'banker'
    
    Returns:
        Intent category or None
    """
    taxonomy = get_intent_taxonomy(mode)
    intent = taxonomy.get(intent_name)
    return intent["category"] if intent else None
```

### 3. Validation Helpers (utils/validators.py)

```python
"""
Validation helpers for intent classification and other data.
"""
from typing import Optional, Dict, Any
from utils.constants import (
    INTENT_CATEGORIES,
    get_valid_intents,
    get_intent_category
)
import logging

logger = logging.getLogger(__name__)

def validate_intent_classification(
    intent_data: Dict[str, Any],
    mode: str
) -> tuple[bool, Optional[str]]:
    """
    Validate intent classification output.
    
    Args:
        intent_data: Dictionary with intent_name, intent_category, classification_reason
        mode: 'customer' or 'banker'
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    required_fields = ["intent_name", "intent_category", "classification_reason"]
    for field in required_fields:
        if field not in intent_data:
            return False, f"Missing required field: {field}"
    
    # Validate intent_name
    valid_intents = get_valid_intents(mode)
    intent_name = intent_data.get("intent_name")
    if intent_name not in valid_intents:
        logger.warning(f"Unknown intent: {intent_name} (mode: {mode})")
        # Don't fail validation - allow unknown intents but they should default to human_only
    
    # Validate intent_category
    intent_category = intent_data.get("intent_category")
    if intent_category not in INTENT_CATEGORIES:
        return False, f"Invalid intent_category: {intent_category}. Must be one of: {INTENT_CATEGORIES}"
    
    # Validate classification_reason
    classification_reason = intent_data.get("classification_reason")
    if not classification_reason or not isinstance(classification_reason, str):
        return False, "classification_reason must be a non-empty string"
    
    # Cross-validate: if intent_name is valid, check category matches expected
    if intent_name in valid_intents:
        expected_category = get_intent_category(intent_name, mode)
        if expected_category and expected_category != intent_category:
            logger.warning(
                f"Intent {intent_name} has category {intent_category} but expected {expected_category}"
            )
            # Don't fail - LLM may have good reason for different classification
    
    return True, None

def validate_confidence_score(score: Optional[float]) -> bool:
    """
    Validate confidence score is in valid range.
    
    Args:
        score: Confidence score (0.0-1.0)
    
    Returns:
        True if valid, False otherwise
    """
    if score is None:
        return False
    return 0.0 <= score <= 1.0

def sanitize_user_query(query: str) -> str:
    """
    Sanitize user query input.
    
    Args:
        query: User query string
    
    Returns:
        Sanitized query string
    """
    if not query:
        return ""
    
    # Trim whitespace
    query = query.strip()
    
    # Limit length (prevent abuse)
    max_length = 2000
    if len(query) > max_length:
        query = query[:max_length]
        logger.warning(f"User query truncated to {max_length} characters")
    
    return query
```

## Setup Instructions

1. **Test OpenAI Client:**
```python
# In Python shell
from utils.openai_client import get_openai_client
client = get_openai_client()

# Test simple chat completion
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, how are you?"}
]
response = client.chat_completion(messages)
print(response["content"])
```

2. **Test Intent Constants:**
```python
from utils.constants import get_intent_taxonomy, get_valid_intents

# Get customer intents
customer_intents = get_intent_taxonomy("customer")
print(f"Customer intents: {list(customer_intents.keys())}")

# Get banker intents
banker_intents = get_intent_taxonomy("banker")
print(f"Banker intents: {list(banker_intents.keys())}")

# Get valid intents for a mode
valid = get_valid_intents("customer")
print(f"Valid customer intents: {valid}")
```

3. **Test Validators:**
```python
from utils.validators import validate_intent_classification

# Test valid intent classification
valid_data = {
    "intent_name": "fee_inquiry",
    "intent_category": "automatable",
    "classification_reason": "User asking about standard fees"
}
is_valid, error = validate_intent_classification(valid_data, "customer")
print(f"Valid: {is_valid}, Error: {error}")

# Test invalid intent classification
invalid_data = {
    "intent_name": "fee_inquiry",
    "intent_category": "invalid_category",  # Invalid
    "classification_reason": "User asking about standard fees"
}
is_valid, error = validate_intent_classification(invalid_data, "customer")
print(f"Valid: {is_valid}, Error: {error}")
```

## Validation Checklist

- [ ] OpenAI client initialized with gpt-4o-mini
- [ ] Chat completion works with retry logic
- [ ] JSON parsing works correctly
- [ ] Intent taxonomy defined (Customer + Banker intents)
- [ ] Validation functions work for intent schema
- [ ] Constants module exports all required values
- [ ] Helpers work for getting intents by mode

## Integration Points

This task sets up the foundation for:
- **Task 8**: Intent classifier will use OpenAI client and intent taxonomy
- **Task 10**: Retrieval will use OpenAI client for Conversations API
- **Task 11**: Response generator will use OpenAI client
- **Task 12**: Confidence scorer will use OpenAI client

## Notes

- Use gpt-4o-mini model for all LLM operations
- Implement retry logic with exponential backoff
- Handle JSON parsing errors gracefully
- Intent taxonomy is based on PRD and README requirements
- Unknown intents default to "human_only" category

## Common Issues

1. **API key invalid**: Check OPENAI_API_KEY in .env
2. **JSON parse error**: Check response format, handle markdown code blocks
3. **Rate limits**: Implement retry logic (already done)
4. **Unknown intent**: Allow but log warning, default to human_only

## Success Criteria

✅ OpenAI client initialized with gpt-4o-mini
✅ Chat completion works with retry logic
✅ Intent taxonomy defined (Customer + Banker intents)
✅ Validation functions work correctly
✅ Constants module exports all required values
