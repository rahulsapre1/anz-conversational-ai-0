# services/router.py
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


def route(
    intent_category: str,
    intent_name: Optional[str] = None,
    assistant_mode: Optional[str] = None
) -> Dict[str, Any]:
    """
    Route based on intent category to determine next pipeline step.
    
    Args:
        intent_category: Intent category from classifier ('automatable', 'sensitive', 'human_only')
        intent_name: Intent name (optional, for logging)
        assistant_mode: Assistant mode (optional, for logging)
    
    Returns:
        Dictionary with routing decision:
        {
            "route": "escalate" | "continue",
            "next_step": int,  # Pipeline step number (3 for continue, 6 for escalate)
            "skip_to_step": int,  # If escalating, which step to skip to (6)
            "reason": str  # Reason for routing decision
        }
    """
    logger.info(
        "routing_started",
        intent_category=intent_category,
        intent_name=intent_name,
        assistant_mode=assistant_mode
    )
    
    # Validate intent_category
    valid_categories = ["automatable", "sensitive", "human_only"]
    if intent_category not in valid_categories:
        logger.warn(
            "invalid_intent_category",
            intent_category=intent_category,
            valid_categories=valid_categories
        )
        # Default to human_only for invalid categories
        intent_category = "human_only"
    
    # Routing logic
    if intent_category == "human_only":
        decision = {
            "route": "escalate",
            "skip_to_step": 6,  # Skip to escalation handler
            "next_step": 6,
            "reason": f"Intent category '{intent_category}' requires human handling"
        }
        logger.info(
            "routing_decision",
            decision=decision["route"],
            reason=decision["reason"],
            intent_category=intent_category,
            intent_name=intent_name,
            assistant_mode=assistant_mode
        )
        return decision
    
    elif intent_category in ["automatable", "sensitive"]:
        decision = {
            "route": "continue",
            "next_step": 3,  # Continue to retrieval service
            "reason": f"Intent category '{intent_category}' can be handled automatically"
        }
        logger.info(
            "routing_decision",
            decision=decision["route"],
            reason=decision["reason"],
            intent_category=intent_category,
            intent_name=intent_name,
            assistant_mode=assistant_mode
        )
        return decision
    
    else:
        # Fallback (should not reach here due to validation above)
        logger.error(
            "routing_fallback",
            intent_category=intent_category
        )
        return {
            "route": "escalate",
            "skip_to_step": 6,
            "next_step": 6,
            "reason": "Unknown intent category, defaulting to escalation"
        }


class Router:
    """
    Router service for pipeline step routing.
    
    This is a simple, synchronous service that makes fast routing decisions
    based on intent category. No async needed as it's just conditional logic.
    """
    
    def __init__(self):
        """Initialize router."""
        pass
    
    def route(
        self,
        intent_category: str,
        intent_name: Optional[str] = None,
        assistant_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Route based on intent category.
        
        Args:
            intent_category: Intent category from classifier
            intent_name: Intent name (optional, for logging)
            assistant_mode: Assistant mode (optional, for logging)
        
        Returns:
            Routing decision dictionary
        """
        return route(intent_category, intent_name, assistant_mode)
    
    def should_escalate(self, intent_category: str) -> bool:
        """
        Check if intent category should be escalated.
        
        Args:
            intent_category: Intent category
        
        Returns:
            True if should escalate, False otherwise
        """
        return intent_category == "human_only"
    
    def get_next_step(self, intent_category: str) -> int:
        """
        Get the next pipeline step number based on intent category.
        
        Args:
            intent_category: Intent category
        
        Returns:
            Next step number (3 for continue, 6 for escalate)
        """
        if intent_category == "human_only":
            return 6
        else:
            return 3
