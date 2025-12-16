-- =============================================================================
-- INSIGHTS COLUMNS MIGRATION v0.1
-- =============================================================================
-- Purpose: Add missing columns for insight review workflow
-- Run: python run_insights_migration.py
-- Issue: Code expects flagged/reviewed/rejected columns but original migration
--        only had status as enum ('raw', 'refined', 'surfaced', 'forged', 'rejected', 'merged')
-- =============================================================================

-- Add flagging columns
ALTER TABLE ingots ADD COLUMN flagged INTEGER DEFAULT 0;
ALTER TABLE ingots ADD COLUMN flagged_at TEXT;

-- Add review tracking columns
ALTER TABLE ingots ADD COLUMN reviewed INTEGER DEFAULT 0;
ALTER TABLE ingots ADD COLUMN reviewed_at TEXT;

-- Add rejection tracking (separate from status='rejected' for workflow)
ALTER TABLE ingots ADD COLUMN rejected INTEGER DEFAULT 0;
ALTER TABLE ingots ADD COLUMN rejected_at TEXT;

-- Add user context field
ALTER TABLE ingots ADD COLUMN user_context TEXT;

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_ingots_flagged ON ingots(flagged) WHERE flagged = 1;
CREATE INDEX IF NOT EXISTS idx_ingots_reviewed ON ingots(reviewed);

-- =============================================================================
-- END MIGRATION
-- =============================================================================
