# Task 9: Router Service

## Overview
Implement a simple routing service that determines the next step in the pipeline based on the intent category from the intent classifier. This is a fast, synchronous decision-making component.

## Prerequisites
- Task 1 completed (project structure, config, logging)
- Task 8 completed (Intent Classifier)
- Virtual environment activated

## Deliverables

### 1. Router Service (services/router.py)

Create `services/router.py` with routing logic based on intent category.

**Key Requirements**:
- Simple conditional logic (synchronous, fast)
- Routes based on intent_category
- Returns clear routing decision
- Structured logging

## Implementation

### Step 1: Router Service Implementation

```python
# services/router.py
from typing import Dict, Any, Literal
from utils.logger import get_logger

logger = get_logger(__name__)


def route(
    intent_category: str,
    intent_name: str = None,
    assistant_mode: str = None
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
            intent_category=intent_category
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
            intent_category=intent_category
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
        intent_name: str = None,
        assistant_mode: str = None
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
```

### Step 2: Integration with Pipeline

The router is used in the main pipeline after intent classification:

```python
# Example usage in main pipeline
from services.intent_classifier import IntentClassifier
from services.router import Router

# Step 1: Intent Classification
intent_result = await intent_classifier.classify_async(user_query, assistant_mode)

if not intent_result:
    # Handle classification failure
    return handle_error("Intent classification failed")

# Step 2: Router
router = Router()
routing_decision = router.route(
    intent_category=intent_result["intent_category"],
    intent_name=intent_result["intent_name"],
    assistant_mode=assistant_mode
)

if routing_decision["route"] == "escalate":
    # Skip to escalation handler (Step 6)
    escalation_result = await handle_escalation(
        trigger_type="human_only",
        intent_name=intent_result["intent_name"],
        assistant_mode=assistant_mode
    )
    return escalation_result
else:
    # Continue to retrieval (Step 3)
    retrieval_result = await retrieval_service.retrieve_async(
        user_query, assistant_mode, intent_result["intent_name"]
    )
    # ... continue pipeline
```

## Routing Logic Details

### Intent Categories

1. **"human_only"** → Escalate
   - **Action**: Skip to Step 6 (Escalation Handler)
   - **Reason**: These intents require human handling
   - **Examples**: `financial_advice`, `complaint`, `hardship`, `fraud_alert`, `unknown`

2. **"automatable"** → Continue
   - **Action**: Continue to Step 3 (Retrieval Service)
   - **Reason**: Can be answered automatically using knowledge base
   - **Examples**: `transaction_explanation`, `fee_inquiry`, `account_limits`, `card_dispute_process`

3. **"sensitive"** → Continue (but may escalate later)
   - **Action**: Continue to Step 3 (Retrieval Service)
   - **Reason**: Can attempt automatic response, but may escalate based on confidence or other triggers
   - **Examples**: `account_balance`, `transaction_history`, `password_reset`
   - **Note**: Sensitive intents may still escalate in later steps (e.g., low confidence, insufficient evidence)

## Output Format

The router returns a dictionary with the following structure:

```python
{
    "route": "escalate" | "continue",
    "next_step": 3 | 6,  # Pipeline step number
    "skip_to_step": 6,   # Only present if route == "escalate"
    "reason": "Intent category 'human_only' requires human handling"
}
```

**Examples**:

```python
# HumanOnly intent
{
    "route": "escalate",
    "skip_to_step": 6,
    "next_step": 6,
    "reason": "Intent category 'human_only' requires human handling"
}

# Automatable intent
{
    "route": "continue",
    "next_step": 3,
    "reason": "Intent category 'automatable' can be handled automatically"
}

# Sensitive intent
{
    "route": "continue",
    "next_step": 3,
    "reason": "Intent category 'sensitive' can be handled automatically"
}
```

## Error Handling

- **Invalid intent_category**: Logs WARN, defaults to "human_only" (escalate)
- **Missing intent_category**: Logs ERROR, defaults to escalate
- **All errors**: Logged with structured logging

## Success Criteria

- [ ] Routes HumanOnly → escalate (skip to step 6)
- [ ] Routes Automatable → continue to step 3
- [ ] Routes Sensitive → continue to step 3
- [ ] Returns clear routing decision with reason
- [ ] Handles all intent categories correctly
- [ ] Handles invalid categories gracefully (defaults to escalate)
- [ ] Logs all routing decisions (structured logging)

## Testing

### Unit Tests

```python
# tests/test_router.py
import pytest
from services.router import Router, route

def test_route_human_only():
    """Test routing for human_only category."""
    result = route("human_only", "financial_advice", "customer")
    assert result["route"] == "escalate"
    assert result["next_step"] == 6
    assert result["skip_to_step"] == 6

def test_route_automatable():
    """Test routing for automatable category."""
    result = route("automatable", "fee_inquiry", "customer")
    assert result["route"] == "continue"
    assert result["next_step"] == 3

def test_route_sensitive():
    """Test routing for sensitive category."""
    result = route("sensitive", "account_balance", "customer")
    assert result["route"] == "continue"
    assert result["next_step"] == 3

def test_route_invalid_category():
    """Test routing for invalid category."""
    result = route("invalid_category", None, None)
    assert result["route"] == "escalate"  # Should default to escalate
    assert result["next_step"] == 6

def test_router_class():
    """Test Router class methods."""
    router = Router()
    
    assert router.should_escalate("human_only") == True
    assert router.should_escalate("automatable") == False
    assert router.should_escalate("sensitive") == False
    
    assert router.get_next_step("human_only") == 6
    assert router.get_next_step("automatable") == 3
    assert router.get_next_step("sensitive") == 3
```

### Manual Testing

```python
# In Python shell or script
from services.router import Router

router = Router()

# Test HumanOnly
result = router.route("human_only", "financial_advice", "customer")
print(result)
# Expected: {"route": "escalate", "next_step": 6, ...}

# Test Automatable
result = router.route("automatable", "fee_inquiry", "customer")
print(result)
# Expected: {"route": "continue", "next_step": 3, ...}

# Test Sensitive
result = router.route("sensitive", "account_balance", "customer")
print(result)
# Expected: {"route": "continue", "next_step": 3, ...}
```

## Integration Points

- **Task 8 (Intent Classifier)**: Receives intent_category from classifier
- **Task 10 (Retrieval Service)**: Routes to retrieval if continue
- **Task 13 (Escalation Handler)**: Routes to escalation if escalate
- **Task 18 (Main App)**: Used in main pipeline orchestration

## Pipeline Flow

```
Step 1: Intent Classification
    ↓
    intent_result = {
        "intent_name": "fee_inquiry",
        "intent_category": "automatable",
        ...
    }
    ↓
Step 2: Router
    ↓
    routing_decision = route(intent_category="automatable")
    ↓
    {
        "route": "continue",
        "next_step": 3
    }
    ↓
Step 3: Retrieval (if continue)
    OR
Step 6: Escalation (if escalate)
```

## Notes

- **Synchronous**: Router is fast and doesn't need async (just conditional logic)
- **Simple**: No complex evaluation, just category-based routing
- **Fast**: Should complete in < 1ms (no I/O operations)
- **Deterministic**: Same input always produces same output
- **No API Calls**: Pure logic, no external dependencies

## Reference

- **DETAILED_PLAN.md** Section 7.2 (Router)
- **TASK_BREAKDOWN.md** Task 9
- **Task 8 Guide**: For intent classification output format
- **Task 13 Guide**: For escalation handler integration
