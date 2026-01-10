import re
from typing import Optional, Dict, Any, List
from utils.logger import get_logger
from config import Config

logger = get_logger(__name__)

# Escalation message templates
ESCALATION_MESSAGES_CUSTOMER = {
    "human_only": """I understand you're asking about {topic}. This requires personalized assistance from our team.

Please contact ANZ customer service:
• Phone: 13 13 14 (24/7)
• Visit your local ANZ branch
• Use ANZ Internet Banking or the ANZ App

Our team will be able to help you with this matter.""",

    "low_confidence": """I want to make sure I give you the most accurate information about {topic}.

For the most reliable answer, I recommend speaking directly with our customer service team:
• Phone: 13 13 14 (24/7)
• Visit your local ANZ branch
• Use ANZ Internet Banking or the ANZ App

They'll be able to provide you with the most up-to-date and accurate information.""",

    "insufficient_evidence": """I don't have enough information to answer your question about {topic} accurately.

To get the help you need, please contact:
• ANZ Customer Service: 13 13 14 (24/7)
• Visit your local ANZ branch
• Use ANZ Internet Banking or the ANZ App

Our team will be happy to assist you.""",

    "conflicting_evidence": """I found some conflicting information about {topic}, and I want to make sure you get the most accurate answer.

Please contact ANZ customer service for clarification:
• Phone: 13 13 14 (24/7)
• Visit your local ANZ branch
• Use ANZ Internet Banking or the ANZ App

They'll be able to provide you with the correct information.""",

    "account_specific": """I can't access your personal account information here for security reasons.

To get help with your account, please:
• Call ANZ Customer Service: 13 13 14 (24/7)
• Visit your local ANZ branch
• Log in to ANZ Internet Banking or the ANZ App

Our team will be able to assist you with your specific account.""",

    "security_fraud": """For security and fraud-related matters, it's important to speak directly with our security team.

Please contact ANZ immediately:
• Security Hotline: 1800 033 844 (24/7)
• Report via ANZ Internet Banking or the ANZ App
• Visit your local ANZ branch

Our security team will help you right away.""",

    "financial_advice": """I can provide general information, but for personalized financial advice, please speak with a qualified financial advisor.

ANZ offers financial advice services:
• Contact ANZ Financial Planning: 1800 989 888
• Visit your local ANZ branch
• Book an appointment online

A qualified advisor can help you with your specific situation.""",

    "legal_hardship": """I understand this is an important matter. For legal or financial hardship situations, please speak directly with our specialist team.

Please contact:
• Financial Hardship Team: 1800 149 549
• Visit your local ANZ branch
• Use ANZ Internet Banking or the ANZ App

Our team will work with you to find a solution.""",

    "emotional_distress": """I can hear this is important to you. Let me connect you with someone who can help right away.

Please contact ANZ customer service:
• Phone: 13 13 14 (24/7)
• Visit your local ANZ branch
• Use ANZ Internet Banking or the ANZ App

Our team is here to help and support you.""",

    "repeated_misunderstanding": """I want to make sure I understand your question correctly. Let me connect you with our team who can help.

Please contact ANZ customer service:
• Phone: 13 13 14 (24/7)
• Visit your local ANZ branch
• Use ANZ Internet Banking or the ANZ App

They'll be able to assist you better.""",

    "explicit_human_request": """Of course! I'll connect you with a member of our team.

Please contact ANZ customer service:
• Phone: 13 13 14 (24/7)
• Visit your local ANZ branch
• Use ANZ Internet Banking or the ANZ App

A team member will be happy to help you."""
}

ESCALATION_MESSAGES_BANKER = {
    "human_only": """This query requires human review and cannot be handled automatically.

Please escalate to:
• Senior banker or branch manager
• Specialist team (if applicable)
• Compliance team (if regulatory question)

Document the escalation reason: {reason}""",

    "low_confidence": """The confidence score for this response is below threshold ({confidence_score:.2f} < {threshold}).

Recommendation: Escalate to ensure accurate information is provided.

Please:
• Review the query and retrieved information
• Consult policy documents or specialist team if needed
• Document the escalation reason""",

    "insufficient_evidence": """Insufficient information retrieved to answer this query accurately.

Please:
• Review available resources
• Consult with specialist team if needed
• Escalate if information is not available

Document the escalation reason: {reason}""",

    "conflicting_evidence": """Conflicting information found in retrieved sources.

Please:
• Review the conflicting information
• Consult policy documents or specialist team
• Escalate for clarification if needed

Document the escalation reason: {reason}""",

    "account_specific": """This query requires access to customer-specific account information.

Please:
• Access customer account through appropriate systems
• Follow privacy and security protocols
• Escalate if additional authorization needed

Document the escalation reason: {reason}""",

    "security_fraud": """Security or fraud indicators detected.

IMMEDIATE ACTION REQUIRED:
• Follow security protocols
• Contact security team immediately
• Document all details
• Do not proceed with standard response

Escalate to security team: {reason}""",

    "financial_advice": """This query may require financial advice considerations.

Please:
• Review compliance requirements
• Consult with qualified financial advisor if needed
• Escalate if advice is required

Document the escalation reason: {reason}""",

    "legal_hardship": """Legal or financial hardship signals detected.

Please:
• Follow hardship procedures
• Consult with hardship specialist team
• Escalate to appropriate team

Document the escalation reason: {reason}""",

    "emotional_distress": """Emotional distress or urgent language detected in customer query.

Please:
• Handle with sensitivity
• Prioritize customer support
• Escalate to specialist team if needed

Document the escalation reason: {reason}""",

    "repeated_misunderstanding": """Multiple failed interactions detected.

Please:
• Review interaction history
• Escalate to senior staff
• Consider alternative communication methods

Document the escalation reason: {reason}""",

    "explicit_human_request": """Customer has explicitly requested human assistance.

Please:
• Acknowledge the request
• Transfer to appropriate team member
• Ensure smooth handoff

Document the escalation reason: {reason}"""
}


class EscalationHandler:
    """Handle escalations with user-friendly messages."""
    
    def __init__(self):
        self.threshold = Config.CONFIDENCE_THRESHOLD
    
    async def handle_escalation(
        self,
        trigger_type: str,
        assistant_mode: str,
        intent_name: Optional[str] = None,
        escalation_reason: Optional[str] = None,
        user_query: Optional[str] = None,
        confidence_score: Optional[float] = None,
        retrieved_chunks: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Handle escalation with appropriate message (async).
        
        Args:
            trigger_type: Type of escalation trigger
            assistant_mode: 'customer' or 'banker'
            intent_name: Intent name (optional)
            escalation_reason: Detailed reason for escalation
            user_query: Original user query (optional)
            confidence_score: Confidence score if low_confidence trigger
            retrieved_chunks: Retrieved chunks if insufficient_evidence trigger
        
        Returns:
            Dictionary with escalated, escalation_message, trigger_type, escalation_reason
        """
        logger.info(
            "escalation_triggered",
            trigger_type=trigger_type,
            assistant_mode=assistant_mode,
            intent_name=intent_name,
            escalation_reason=escalation_reason
        )
        
        # Validate trigger type
        valid_triggers = [
            "human_only", "low_confidence", "insufficient_evidence",
            "conflicting_evidence", "account_specific", "security_fraud",
            "financial_advice", "legal_hardship", "emotional_distress",
            "repeated_misunderstanding", "explicit_human_request"
        ]
        
        if trigger_type not in valid_triggers:
            logger.warning("invalid_trigger_type", trigger_type=trigger_type)
            trigger_type = "human_only"  # Default trigger
        
        # Format escalation reason if not provided
        if not escalation_reason:
            escalation_reason = self._format_escalation_reason(
                trigger_type=trigger_type,
                intent_name=intent_name,
                confidence_score=confidence_score
            )
        
        # Generate escalation message
        message = self._generate_escalation_message(
            trigger_type=trigger_type,
            assistant_mode=assistant_mode,
            intent_name=intent_name,
            escalation_reason=escalation_reason,
            user_query=user_query,
            confidence_score=confidence_score
        )
        
        logger.info(
            "escalation_handled",
            trigger_type=trigger_type,
            assistant_mode=assistant_mode,
            message_length=len(message)
        )
        
        return {
            "escalated": True,
            "escalation_message": message,
            "trigger_type": trigger_type,
            "escalation_reason": escalation_reason
        }
    
    def _generate_escalation_message(
        self,
        trigger_type: str,
        assistant_mode: str,
        intent_name: Optional[str] = None,
        escalation_reason: Optional[str] = None,
        user_query: Optional[str] = None,
        confidence_score: Optional[float] = None
    ) -> str:
        """
        Generate user-friendly escalation message.
        
        Args:
            trigger_type: Type of escalation trigger
            assistant_mode: 'customer' or 'banker'
            intent_name: Intent name
            escalation_reason: Detailed reason
            user_query: Original query
            confidence_score: Confidence score
        
        Returns:
            Escalation message string
        """
        # Select message template based on mode
        messages = ESCALATION_MESSAGES_CUSTOMER if assistant_mode == "customer" else ESCALATION_MESSAGES_BANKER
        
        # Get base message
        base_message = messages.get(trigger_type, messages["human_only"])
        
        # Format message with context
        topic = intent_name or "your question" if assistant_mode == "customer" else "this query"
        
        try:
            formatted_message = base_message.format(
                topic=topic,
                reason=escalation_reason or f"{trigger_type} trigger",
                confidence_score=confidence_score or 0.0,
                threshold=self.threshold
            )
        except KeyError:
            # Fallback if formatting fails
            logger.warning("message_formatting_failed", trigger_type=trigger_type)
            formatted_message = base_message
        
        return formatted_message
    
    def _format_escalation_reason(
        self,
        trigger_type: str,
        intent_name: Optional[str] = None,
        confidence_score: Optional[float] = None
    ) -> str:
        """
        Format escalation reason string.
        
        Args:
            trigger_type: Type of trigger
            intent_name: Intent name
            confidence_score: Confidence score
        
        Returns:
            Formatted reason string
        """
        reasons = {
            "human_only": f"Intent category is HumanOnly (intent: {intent_name or 'unknown'})",
            "low_confidence": f"Confidence score {confidence_score or 0.0:.2f} below threshold {self.threshold}",
            "insufficient_evidence": "No retrieval results or insufficient information",
            "conflicting_evidence": "Conflicting information in retrieved chunks",
            "account_specific": "Account-specific or personal data request",
            "security_fraud": "Security or fraud indicators detected",
            "financial_advice": "Financial advice framing detected",
            "legal_hardship": "Legal or financial hardship signals",
            "emotional_distress": "Emotional distress or urgent language detected",
            "repeated_misunderstanding": "Multiple failed interactions",
            "explicit_human_request": "User explicitly requested human assistance"
        }
        
        return reasons.get(trigger_type, f"Escalation triggered: {trigger_type}")
    
    def detect_escalation_triggers(
        self,
        user_query: str,
        intent_category: Optional[str] = None,
        confidence_score: Optional[float] = None,
        retrieved_chunks: Optional[List[str]] = None,
        interaction_history: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        Detect all applicable escalation triggers from context.
        
        Args:
            user_query: User query text
            intent_category: Intent category from classifier
            confidence_score: Confidence score from scorer
            retrieved_chunks: Retrieved chunks from retrieval service
            interaction_history: Previous interactions in session
        
        Returns:
            List of detected trigger types
        """
        triggers = []
        
        # 1. HumanOnly category
        if intent_category == "human_only":
            triggers.append("human_only")
        
        # 2. Low confidence
        if confidence_score is not None and confidence_score < self.threshold:
            triggers.append("low_confidence")
        
        # 3. Insufficient evidence
        if not retrieved_chunks or len(retrieved_chunks) == 0:
            triggers.append("insufficient_evidence")
        
        # 4. Conflicting evidence (simplified - could be enhanced with LLM)
        # Note: This is a simplified check. In production, could use LLM to detect actual conflicts
        if retrieved_chunks and len(retrieved_chunks) > 1:
            # For now, we'll skip automatic detection of conflicting evidence
            # as it requires more sophisticated analysis
            pass
        
        # 5. Account-specific requests
        account_patterns = [
            r'\bmy account\b', r'\bmy balance\b', r'\bmy transactions\b',
            r'\baccount number\b', r'\bmy card\b', r'\bpersonal information\b'
        ]
        if any(re.search(pattern, user_query, re.IGNORECASE) for pattern in account_patterns):
            triggers.append("account_specific")
        
        # 6. Security/fraud indicators
        security_patterns = [
            r'\bfraud\b', r'\bscam\b', r'\bstolen\b', r'\blost card\b',
            r'\bunauthorized\b', r'\bsuspicious\b', r'\bsecurity breach\b'
        ]
        if any(re.search(pattern, user_query, re.IGNORECASE) for pattern in security_patterns):
            triggers.append("security_fraud")
        
        # 7. Financial advice framing
        advice_patterns = [
            r'\bshould i\b', r'\bwhat should\b', r'\brecommend\b',
            r'\badvice\b', r'\bwhat do you think\b', r'\bis it good\b'
        ]
        if any(re.search(pattern, user_query, re.IGNORECASE) for pattern in advice_patterns):
            triggers.append("financial_advice")
        
        # 8. Legal/hardship signals
        hardship_patterns = [
            r'\bhardship\b', r'\bcan\'t pay\b', r'\bstruggling\b',
            r'\blegal\b', r'\blawsuit\b', r'\bdispute\b', r'\bcomplaint\b'
        ]
        if any(re.search(pattern, user_query, re.IGNORECASE) for pattern in hardship_patterns):
            triggers.append("legal_hardship")
        
        # 9. Emotional distress/urgent language
        emotional_patterns = [
            r'\burgent\b', r'\bemergency\b', r'\basap\b', r'\bimmediately\b',
            r'\bworried\b', r'\bconcerned\b', r'\bstressed\b', r'\bpanicked\b'
        ]
        if any(re.search(pattern, user_query, re.IGNORECASE) for pattern in emotional_patterns):
            triggers.append("emotional_distress")
        
        # 10. Repeated misunderstanding
        if interaction_history:
            failed_count = sum(1 for interaction in interaction_history[-3:] if interaction.get("escalated", False))
            if failed_count >= 2:
                triggers.append("repeated_misunderstanding")
        
        # 11. Explicit human request
        human_request_patterns = [
            r'\bspeak to.*human\b', r'\btalk to.*person\b', r'\bhuman agent\b',
            r'\breal person\b', r'\bactual person\b', r'\bnot a bot\b'
        ]
        if any(re.search(pattern, user_query, re.IGNORECASE) for pattern in human_request_patterns):
            triggers.append("explicit_human_request")
        
        return triggers

async def handle_escalation(
    trigger_type: str,
    assistant_mode: str,
    intent_name: Optional[str] = None,
    escalation_reason: Optional[str] = None,
    user_query: Optional[str] = None,
    confidence_score: Optional[float] = None,
    retrieved_chunks: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Convenience function for escalation handling."""
    handler = EscalationHandler()
    return await handler.handle_escalation(
        trigger_type, assistant_mode, intent_name, escalation_reason,
        user_query, confidence_score, retrieved_chunks
    )
