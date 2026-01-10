#!/usr/bin/env python3
"""
Test script for intent classification with conversation history.
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.intent_classifier import IntentClassifier

async def test_intent_with_history():
    """Test intent classification with conversation history."""

    classifier = IntentClassifier()

    # Test case 1: First message about card dispute
    print("Test 1: First message about card dispute")
    result1 = await classifier.classify(
        user_query="How do I dispute a transaction on my ANZ credit card?",
        assistant_mode="customer"
    )
    print(f"Result: {result1}")
    print()

    # Test case 2: Follow-up question with conversation history
    print("Test 2: Follow-up question with conversation history")
    conversation_history = [
        {
            "role": "user",
            "content": "How do I dispute a transaction on my ANZ credit card?"
        },
        {
            "role": "assistant",
            "content": "To dispute a transaction on your ANZ credit card, you can contact ANZ customer service. Here are the steps: 1. Call 1800 123 456, 2. Have your card details ready, 3. Explain the dispute clearly."
        }
    ]

    result2 = await classifier.classify(
        user_query="Can I do it via phone call?",
        assistant_mode="customer",
        conversation_history=conversation_history
    )
    print(f"Result: {result2}")
    print()

    # Test case 3: General conversation without history
    print("Test 3: General conversation without history")
    result3 = await classifier.classify(
        user_query="How is the weather today?",
        assistant_mode="customer"
    )
    print(f"Result: {result3}")

if __name__ == "__main__":
    asyncio.run(test_intent_with_history())