"""
Intent taxonomy constants based on PRD and README.
"""
from typing import Optional

# Customer Assistant Intents
CUSTOMER_INTENTS = {
    "greeting": {
        "category": "automatable",
        "description": "Greetings, hello, hi, small talk, conversational openers"
    },
    "general_conversation": {
        "category": "automatable",
        "description": "General conversational queries, follow-ups, clarifications that don't require knowledge base"
    },
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
        "category": "automatable",  # Changed from human_only - will provide helpful guidance instead of escalation
        "description": "Unclassifiable or out-of-scope queries - provide helpful guidance"
    }
}

# Banker Assistant Intents
BANKER_INTENTS = {
    "greeting": {
        "category": "automatable",
        "description": "Greetings, hello, hi, small talk, conversational openers"
    },
    "general_conversation": {
        "category": "automatable",
        "description": "General conversational queries, follow-ups, clarifications that don't require knowledge base"
    },
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
        "category": "automatable",  # Changed from human_only - will provide helpful guidance instead of escalation
        "description": "Unclassifiable or out-of-scope queries - provide helpful guidance"
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
