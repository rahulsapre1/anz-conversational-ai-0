-- Add conversation memory tables
-- Migration: 003_add_conversation_memory

-- Conversations table (for conversation memory)
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id VARCHAR(255) UNIQUE NOT NULL,  -- User-facing conversation identifier
    assistant_mode VARCHAR(10) NOT NULL CHECK (assistant_mode IN ('customer', 'banker')),
    user_id VARCHAR(255),  -- Optional: for authenticated users
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    title TEXT,  -- Auto-generated conversation title
    message_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

-- Conversation messages table
CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    citations JSONB,  -- For assistant messages
    confidence_score FLOAT,  -- For assistant messages
    escalated BOOLEAN DEFAULT FALSE,  -- For assistant messages
    escalation_message TEXT,  -- For escalated messages
    trigger_type VARCHAR(50),  -- For escalated messages
    interaction_id UUID REFERENCES interactions(id) ON DELETE SET NULL  -- Link to detailed interaction log
);

-- Conversation indexes
CREATE INDEX IF NOT EXISTS idx_conversations_conversation_id ON conversations(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversations_assistant_mode ON conversations(assistant_mode);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_active ON conversations(is_active);
CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at DESC);

-- Conversation messages indexes
CREATE INDEX IF NOT EXISTS idx_conversation_messages_conversation ON conversation_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_timestamp ON conversation_messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_role ON conversation_messages(role);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_interaction ON conversation_messages(interaction_id);

-- Add comment to document the new functionality
COMMENT ON TABLE conversations IS 'Stores conversation threads for persistent chat memory';
COMMENT ON TABLE conversation_messages IS 'Stores individual messages within conversations for context and history';