-- =============================================================================
-- ENTITY REGISTRY MIGRATION v0.2 - Add content column
-- =============================================================================
-- Purpose: Store full content in preflight_items for ReCog processing
-- =============================================================================

-- Add content column to preflight_items
ALTER TABLE preflight_items ADD COLUMN content TEXT;
