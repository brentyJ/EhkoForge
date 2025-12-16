-- =============================================================================
-- INSIGHTS USER INTERACTION MIGRATION v0.1
-- Adds columns for user review workflow
-- =============================================================================

-- Add user context column (user can add missing context to insights)
ALTER TABLE ingots ADD COLUMN user_context TEXT;

-- Add flagged status (user marks insight as important/core)
ALTER TABLE ingots ADD COLUMN flagged INTEGER DEFAULT 0;

-- Add flagged timestamp
ALTER TABLE ingots ADD COLUMN flagged_at TEXT;

-- Add rejected status (user discards insight)
ALTER TABLE ingots ADD COLUMN rejected INTEGER DEFAULT 0;

-- Add rejected timestamp
ALTER TABLE ingots ADD COLUMN rejected_at TEXT;

-- Add reviewed status (user has seen this insight)
ALTER TABLE ingots ADD COLUMN reviewed INTEGER DEFAULT 0;

-- Add reviewed timestamp
ALTER TABLE ingots ADD COLUMN reviewed_at TEXT;

-- =============================================================================
-- REPORT DETAILS TABLE
-- Links reports to their contributing insights/patterns
-- =============================================================================

CREATE TABLE IF NOT EXISTS recog_report_sources (
    report_id INTEGER NOT NULL,
    source_type TEXT NOT NULL,  -- 'insight' | 'pattern' | 'synthesis'
    source_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (report_id, source_type, source_id),
    FOREIGN KEY (report_id) REFERENCES recog_reports(id)
);

-- Index for quick report lookups
CREATE INDEX IF NOT EXISTS idx_report_sources_report 
ON recog_report_sources(report_id);

-- Index for finding which reports an insight appears in
CREATE INDEX IF NOT EXISTS idx_report_sources_source 
ON recog_report_sources(source_type, source_id);

-- =============================================================================
-- VIEWS FOR INSIGHT BROWSING
-- =============================================================================

-- View for insight list with source counts
CREATE VIEW IF NOT EXISTS v_insights_summary AS
SELECT 
    i.id,
    i.summary,
    i.themes_json,
    i.significance,
    i.confidence,
    i.status,
    i.flagged,
    i.rejected,
    i.reviewed,
    i.user_context,
    i.created_at,
    i.updated_at,
    COUNT(DISTINCT s.source_id) as source_count,
    COUNT(DISTINCT pi.pattern_id) as pattern_count
FROM ingots i
LEFT JOIN ingot_sources s ON i.id = s.ingot_id
LEFT JOIN ingot_pattern_insights pi ON i.id = pi.ingot_id
GROUP BY i.id;
