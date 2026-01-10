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
