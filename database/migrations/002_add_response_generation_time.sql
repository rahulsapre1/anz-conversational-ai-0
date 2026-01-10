-- Add response generation time tracking
-- Migration: 002_add_response_generation_time

ALTER TABLE interactions
ADD COLUMN response_generation_time_ms INTEGER;

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_interactions_response_time ON interactions(response_generation_time_ms);

-- Add comment to document the field
COMMENT ON COLUMN interactions.response_generation_time_ms IS 'Time spent specifically on response generation (LLM calls), in milliseconds';