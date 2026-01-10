#!/usr/bin/env python3
"""
Test script for conversation memory functionality.

This script demonstrates the new conversation memory feature that allows
persistent chat history across browser sessions.
"""

import uuid
from database.supabase_client import get_db_client

def generate_conversation_id():
    """Generate a unique conversation ID."""
    return f"conv_{uuid.uuid4().hex[:16]}"

def test_conversation_memory():
    """Test the conversation memory functionality."""
    print("🧠 Testing Conversation Memory Implementation")
    print("=" * 50)

    # Initialize database client
    db_client = get_db_client()
    print("✅ Database client initialized")

    # Generate conversation ID
    conversation_id = generate_conversation_id()
    print(f"✅ Generated conversation ID: {conversation_id}")

    # Create conversation
    print("\n📝 Creating conversation...")
    conversation_uuid = db_client.create_conversation(
        conversation_id=conversation_id,
        assistant_mode="customer"
    )

    if not conversation_uuid:
        print("❌ Failed to create conversation")
        return

    print(f"✅ Conversation created with UUID: {conversation_uuid}")

    # Save some test messages
    print("\n💬 Saving test messages...")

    # User message 1
    db_client.save_message(
        conversation_uuid=conversation_uuid,
        role="user",
        content="Hello, I need help with my ANZ account"
    )
    print("✅ Saved user message 1")

    # Assistant message 1
    db_client.save_message(
        conversation_uuid=conversation_uuid,
        role="assistant",
        content="Hello! I'd be happy to help you with your ANZ account. What specific assistance do you need today?",
        citations=[{"number": 1, "source": "ANZ Website", "url": "https://www.anz.com"}],
        confidence_score=0.95
    )
    print("✅ Saved assistant message 1")

    # User message 2
    db_client.save_message(
        conversation_uuid=conversation_uuid,
        role="user",
        content="I want to check my transaction history"
    )
    print("✅ Saved user message 2")

    # Assistant message 2
    db_client.save_message(
        conversation_uuid=conversation_uuid,
        role="assistant",
        content="I can help you check your transaction history. To access this securely, you'll need to log into ANZ Online Banking or use the ANZ app.",
        citations=[{"number": 1, "source": "ANZ Transaction History Guide", "url": "https://www.anz.com/help/transaction-history"}],
        confidence_score=0.92
    )
    print("✅ Saved assistant message 2")

    # Load conversation history
    print("\n📚 Loading conversation history...")
    messages = db_client.load_conversation_history(conversation_uuid)

    print(f"✅ Loaded {len(messages)} messages:")
    for i, msg in enumerate(messages, 1):
        role = msg["role"].title()
        content_preview = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
        print(f"  {i}. {role}: {content_preview}")

        if msg["role"] == "assistant" and msg.get("confidence_score"):
            print(f"     Confidence: {msg['confidence_score']:.2f}")

    # Test conversation retrieval
    print("\n🔍 Testing conversation retrieval...")
    conversation = db_client.get_conversation_by_id(conversation_id)
    if conversation:
        print(f"✅ Retrieved conversation: {conversation['conversation_id']}")
        print(f"   Mode: {conversation['assistant_mode']}")
        print(f"   Active: {conversation['is_active']}")
        print(f"   Messages: {conversation['message_count']}")
    else:
        print("❌ Failed to retrieve conversation")

    # Test recent conversations
    print("\n📋 Testing recent conversations...")
    recent = db_client.get_recent_conversations(limit=5)
    print(f"✅ Found {len(recent)} recent conversations")

    print("\n🎉 Conversation memory test completed successfully!")
    print("\n📋 To use this in production:")
    print("1. Run the migration SQL in Supabase SQL Editor:")
    print("   database/migrations/003_add_conversation_memory.sql")
    print("2. The chat interface will now automatically persist conversations")
    print("3. Users can now have continuous conversations across browser sessions!")

if __name__ == "__main__":
    test_conversation_memory()