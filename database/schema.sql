-- Interactions table (primary logging)
CREATE TABLE IF NOT EXISTS interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assistant_mode VARCHAR(10) NOT NULL CHECK (assistant_mode IN ('customer', 'banker')),
    session_id VARCHAR(255),  -- OpenAI conversation ID
    
    -- User input
    user_query TEXT NOT NULL,
    
    -- Intent classification
    intent_name VARCHAR(100),
    intent_category VARCHAR(20) CHECK (intent_category IN ('automatable', 'sensitive', 'human_only')),
    classification_reason TEXT,
    
    -- Pipeline steps (logged for debugging)
    step_1_intent_completed BOOLEAN DEFAULT FALSE,
    step_2_routing_decision VARCHAR(50),
    step_3_retrieval_performed BOOLEAN DEFAULT FALSE,
    step_4_response_generated BOOLEAN DEFAULT FALSE,
    step_5_confidence_score FLOAT,
    step_6_escalation_triggered BOOLEAN DEFAULT FALSE,
    
    -- Outcome
    outcome VARCHAR(20) NOT NULL CHECK (outcome IN ('resolved', 'escalated')),
    confidence_score FLOAT,
    escalation_reason TEXT,
    
    -- Response
    response_text TEXT,
    citations JSONB,  -- Array of citation objects: [{"number": 1, "source": "...", "url": "..."}, ...]
    
    -- Metadata
    retrieved_chunks_count INTEGER,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Escalations table (for analytics)
CREATE TABLE IF NOT EXISTS escalations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interaction_id UUID REFERENCES interactions(id) ON DELETE CASCADE,
    trigger_type VARCHAR(50) NOT NULL,  -- 'human_only', 'low_confidence', 'insufficient_evidence', etc.
    escalation_reason TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

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

-- Knowledge documents registry (optional, for tracking)
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    openai_file_id VARCHAR(255) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    source_url TEXT,
    content_type VARCHAR(20) CHECK (content_type IN ('public', 'synthetic')),
    topic_collection VARCHAR(100),  -- Which assistant/topic collection
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB  -- Additional metadata
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_interactions_mode ON interactions(assistant_mode);
CREATE INDEX IF NOT EXISTS idx_interactions_intent ON interactions(intent_name);
CREATE INDEX IF NOT EXISTS idx_interactions_outcome ON interactions(outcome);
CREATE INDEX IF NOT EXISTS idx_interactions_session ON interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_escalations_interaction ON escalations(interaction_id);
CREATE INDEX IF NOT EXISTS idx_escalations_trigger ON escalations(trigger_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_file_id ON knowledge_documents(openai_file_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_type ON knowledge_documents(content_type);

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
