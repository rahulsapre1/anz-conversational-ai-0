# Task 2: Database Schema & Supabase Setup

## Overview
Set up Supabase PostgreSQL database with schema for logging interactions, escalations, and knowledge documents.

## Prerequisites
- Task 1 completed (project structure and config.py)
- Supabase account created (if not already)
- Supabase project created

## Deliverables

### 1. Supabase Project Setup

**If Supabase project doesn't exist:**

1. Go to https://supabase.com
2. Create a new project
3. Note down:
   - Project URL (e.g., `https://xxx.supabase.co`)
   - API Key (anon/public key)
   - Service Role Key (for admin operations - keep secret)

4. Add to `.env`:
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...  # Use anon/public key for client operations
```

### 2. Database Schema (schema.sql)

Create `database/schema.sql` with the following schema:

```sql
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
```

### 3. Supabase Client Wrapper (database/supabase_client.py)

```python
from supabase import create_client, Client
from typing import Optional, Dict, List, Any
from config import Config
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Wrapper for Supabase client operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_KEY
        )
        logger.info("Supabase client initialized")
    
    def test_connection(self) -> bool:
        """Test connection to Supabase."""
        try:
            # Simple query to test connection
            result = self.client.table("interactions").select("id").limit(1).execute()
            logger.info("Supabase connection test successful")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False
    
    def insert_interaction(self, interaction_data: Dict[str, Any]) -> Optional[str]:
        """
        Insert an interaction record.
        
        Args:
            interaction_data: Dictionary with interaction fields
        
        Returns:
            Interaction ID if successful, None otherwise
        """
        try:
            result = self.client.table("interactions").insert(interaction_data).execute()
            if result.data and len(result.data) > 0:
                interaction_id = result.data[0]["id"]
                logger.info(f"Interaction logged: {interaction_id}")
                return interaction_id
            return None
        except Exception as e:
            logger.error(f"Failed to insert interaction: {e}")
            return None
    
    def insert_escalation(self, escalation_data: Dict[str, Any]) -> Optional[str]:
        """
        Insert an escalation record.
        
        Args:
            escalation_data: Dictionary with escalation fields
        
        Returns:
            Escalation ID if successful, None otherwise
        """
        try:
            result = self.client.table("escalations").insert(escalation_data).execute()
            if result.data and len(result.data) > 0:
                escalation_id = result.data[0]["id"]
                logger.info(f"Escalation logged: {escalation_id}")
                return escalation_id
            return None
        except Exception as e:
            logger.error(f"Failed to insert escalation: {e}")
            return None
    
    def insert_knowledge_document(self, doc_data: Dict[str, Any]) -> Optional[str]:
        """
        Insert a knowledge document record.
        
        Args:
            doc_data: Dictionary with document fields
        
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            result = self.client.table("knowledge_documents").insert(doc_data).execute()
            if result.data and len(result.data) > 0:
                doc_id = result.data[0]["id"]
                logger.info(f"Knowledge document logged: {doc_id}")
                return doc_id
            return None
        except Exception as e:
            logger.error(f"Failed to insert knowledge document: {e}")
            return None
    
    def get_metrics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get aggregated metrics for dashboard.
        
        Args:
            filters: Optional filters (mode, date_range, etc.)
        
        Returns:
            Dictionary with metric values
        """
        try:
            # Build query with filters
            query = self.client.table("interactions").select("*")
            
            if filters:
                if "mode" in filters:
                    query = query.eq("assistant_mode", filters["mode"])
                if "date_from" in filters:
                    query = query.gte("timestamp", filters["date_from"])
                if "date_to" in filters:
                    query = query.lte("timestamp", filters["date_to"])
            
            result = query.execute()
            interactions = result.data if result.data else []
            
            # Calculate metrics (will be implemented in Task 16)
            # For now, return basic structure
            return {
                "total_interactions": len(interactions),
                "interactions": interactions
            }
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {"total_interactions": 0, "interactions": []}

# Singleton instance
_db_client: Optional[SupabaseClient] = None

def get_db_client() -> SupabaseClient:
    """Get singleton Supabase client instance."""
    global _db_client
    if _db_client is None:
        _db_client = SupabaseClient()
    return _db_client
```

### 4. Migration Script (database/migrations/001_initial_schema.sql)

Copy `schema.sql` content to this file for version control.

### 5. Migration Runner (database/run_migrations.py) - Optional

```python
"""
Run database migrations.
Can be executed manually or via Supabase SQL editor.
"""
import sys
from pathlib import Path

# Read schema.sql
schema_file = Path(__file__).parent / "schema.sql"
with open(schema_file, "r") as f:
    schema_sql = f.read()

print("=" * 60)
print("Database Migration Script")
print("=" * 60)
print("\nCopy and paste the following SQL into Supabase SQL Editor:\n")
print(schema_sql)
print("\n" + "=" * 60)
print("After running the SQL, verify tables were created.")
print("=" * 60)
```

## Setup Instructions

### Manual Setup (Recommended for MVP)

1. **Open Supabase SQL Editor:**
   - Go to your Supabase project dashboard
   - Navigate to SQL Editor

2. **Run Schema SQL:**
   - Copy contents of `database/schema.sql`
   - Paste into SQL Editor
   - Execute

3. **Verify Tables Created:**
   - Go to Table Editor in Supabase
   - Verify these tables exist:
     - `interactions`
     - `escalations`
     - `knowledge_documents`

4. **Verify Indexes:**
   - Check that indexes were created (in SQL Editor, run):
   ```sql
   SELECT indexname, tablename 
   FROM pg_indexes 
   WHERE schemaname = 'public'
   ORDER BY tablename, indexname;
   ```

5. **Test Connection:**
   ```python
   # In Python shell
   from database.supabase_client import get_db_client
   client = get_db_client()
   client.test_connection()  # Should return True
   ```

6. **Test Insert:**
   ```python
   # Test insert (will be cleaned up)
   test_data = {
       "assistant_mode": "customer",
       "user_query": "test query",
       "outcome": "resolved",
       "step_1_intent_completed": True
   }
   interaction_id = client.insert_interaction(test_data)
   print(f"Inserted interaction: {interaction_id}")
   ```

## Validation Checklist

- [ ] Supabase project created and accessible
- [ ] All tables created (interactions, escalations, knowledge_documents)
- [ ] All indexes created
- [ ] Constraints work (CHECK constraints for enums)
- [ ] Foreign key relationship works (escalations.interaction_id → interactions.id)
- [ ] Client wrapper can connect
- [ ] Client wrapper can insert test data
- [ ] Client wrapper can query data
- [ ] Schema matches DETAILED_PLAN.md Section 5

## Integration Points

This task sets up the database for:
- **Task 14**: Logging service will use SupabaseClient
- **Task 16**: Dashboard will use SupabaseClient for metrics
- **Task 6**: Knowledge ingestion will use knowledge_documents table

## Notes

- Use Supabase anon/public key for client operations (not service role key)
- All inserts should handle errors gracefully
- Use JSONB for flexible metadata storage (citations, document metadata)
- Indexes are critical for dashboard performance
- Foreign keys use ON DELETE CASCADE for escalations (cleanup on interaction delete)

## Common Issues

1. **Connection refused**: Check SUPABASE_URL and SUPABASE_KEY in .env
2. **Permission denied**: Ensure using correct API key (anon/public key)
3. **Table not found**: Verify schema was executed in SQL Editor
4. **Constraint violation**: Check enum values match CHECK constraints

## Success Criteria

✅ Supabase project created and accessible
✅ All tables created with correct schema
✅ All indexes created
✅ Client wrapper can connect and insert data
✅ Schema matches specification exactly
