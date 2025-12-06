-- =============================================================================
-- MEMORY TIERS & PROGRESSION MIGRATION v0.1
-- =============================================================================
-- Purpose: Memory tier system, authority progression, ReCog processing state
-- Run: python run_memory_migration.py
-- =============================================================================

-- =============================================================================
-- 1. SESSION MEMORY MANAGEMENT
-- =============================================================================

-- Extend forge_sessions with memory tier tracking
ALTER TABLE forge_sessions ADD COLUMN memory_tier TEXT DEFAULT 'hot';
-- Values: 'hot' (raw, <2 days), 'warm' (summarised), 'cold' (archived)

ALTER TABLE forge_sessions ADD COLUMN archived_at TEXT;
-- When session moved to cold storage

ALTER TABLE forge_sessions ADD COLUMN last_accessed_at TEXT;
-- For LRU-style management

-- Session summaries: distilled versions of chat sessions
CREATE TABLE IF NOT EXISTS session_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL UNIQUE,        -- FK to forge_sessions.id
    summary TEXT NOT NULL,                  -- Distilled conversation summary
    key_points_json TEXT,                   -- JSON array of main points
    themes_json TEXT,                       -- JSON array of themes discussed
    emotional_tone TEXT,                    -- Overall emotional character
    user_intent TEXT,                       -- What user was trying to accomplish
    word_count INTEGER,                     -- Original session word count
    message_count INTEGER,                  -- Number of messages
    duration_minutes INTEGER,               -- Session duration if known
    created_at TEXT NOT NULL,               -- When summary was created
    model_used TEXT,                        -- Model that created summary
    FOREIGN KEY (session_id) REFERENCES forge_sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_session_summaries_session ON session_summaries(session_id);

-- =============================================================================
-- 2. AUTHORITY PROGRESSION SYSTEM
-- =============================================================================

-- Replace/extend ehko_authority with stage-based progression
-- Drop old table if exists and recreate with new structure
-- (Keeping old data requires migration logic in Python)

CREATE TABLE IF NOT EXISTS ehko_progression (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- Singleton
    
    -- Current stage
    stage TEXT DEFAULT 'nascent',           -- nascent/emergent/resonant/harmonic/sovereign
    stage_entered_at TEXT,                  -- When entered current stage
    
    -- Pillar completion tracking
    pillars_seeded INTEGER DEFAULT 0,       -- Count of pillars with any content
    pillars_populated INTEGER DEFAULT 0,    -- Count of pillars substantially filled
    pillars_json TEXT,                      -- JSON: {"web": 0.3, "thread": 0.5, ...}
    
    -- Core memory tracking
    core_memory_count INTEGER DEFAULT 0,    -- Total indexed core memories
    core_memories_curated INTEGER DEFAULT 0, -- User-reviewed/approved
    
    -- Overall progress
    total_xp INTEGER DEFAULT 0,             -- Legacy XP if needed
    last_synthesis_at TEXT,                 -- Last full ReCog synthesis
    
    -- Timestamps
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Stage requirements reference (not a table, just documentation)
-- nascent:   Account created, first session
-- emergent:  2+ pillars seeded, 3+ core memories
-- resonant:  4+ pillars populated, 10+ core memories
-- harmonic:  All 6 pillars substantial, 20+ core memories
-- sovereign: Pillars refined, memories curated, synthesis complete

-- =============================================================================
-- 3. RECOG PROCESSING STATE
-- =============================================================================

-- Track what ReCog has processed and when
CREATE TABLE IF NOT EXISTS recog_processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,              -- 'session', 'reflection', 'transcript'
    source_id TEXT NOT NULL,                -- ID of processed item
    tier INTEGER NOT NULL,                  -- 0, 1, 2, or 3
    processed_at TEXT NOT NULL,             -- ISO timestamp
    model_used TEXT,                        -- Which model processed
    tokens_used INTEGER,                    -- Token count if known
    mana_cost INTEGER DEFAULT 0,            -- Mana spent
    result_summary TEXT,                    -- Brief result (e.g., "3 insights extracted")
    UNIQUE(source_type, source_id, tier)    -- One record per source per tier
);

CREATE INDEX IF NOT EXISTS idx_recog_log_source ON recog_processing_log(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_recog_log_tier ON recog_processing_log(tier, processed_at);

-- ReCog reports: periodic snapshots of current thinking
CREATE TABLE IF NOT EXISTS recog_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,              -- 'synthesis', 'pattern_update', 'full_sweep'
    created_at TEXT NOT NULL,
    
    -- Content
    summary TEXT NOT NULL,                  -- Human-readable summary
    insights_count INTEGER DEFAULT 0,       -- Insights in this report
    patterns_count INTEGER DEFAULT 0,       -- Patterns identified
    syntheses_count INTEGER DEFAULT 0,      -- New personality syntheses
    
    -- Detailed data (JSON)
    insights_json TEXT,                     -- Array of insight IDs/summaries
    patterns_json TEXT,                     -- Array of pattern summaries
    syntheses_json TEXT,                    -- Array of synthesis summaries
    conclusions_json TEXT,                  -- "What I think now" statements
    suspended_json TEXT,                    -- Previously held conclusions now suspended
    
    -- Processing metadata
    documents_processed INTEGER DEFAULT 0,
    sessions_processed INTEGER DEFAULT 0,
    tokens_used INTEGER DEFAULT 0,
    mana_cost INTEGER DEFAULT 0,
    model_used TEXT,
    
    -- Status
    status TEXT DEFAULT 'current',          -- 'current', 'superseded', 'archived'
    superseded_by INTEGER,                  -- ID of newer report if superseded
    FOREIGN KEY (superseded_by) REFERENCES recog_reports(id)
);

CREATE INDEX IF NOT EXISTS idx_recog_reports_type ON recog_reports(report_type, status);
CREATE INDEX IF NOT EXISTS idx_recog_reports_date ON recog_reports(created_at DESC);

-- =============================================================================
-- 4. RECOG QUEUE (enhanced smelt_queue replacement)
-- =============================================================================

-- Pending ReCog operations with mana cost estimates
CREATE TABLE IF NOT EXISTS recog_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_type TEXT NOT NULL,           -- 'extract', 'correlate', 'synthesise'
    source_type TEXT,                       -- 'session', 'batch', etc.
    source_ids_json TEXT,                   -- JSON array of source IDs
    
    -- Queue management
    queued_at TEXT NOT NULL,
    priority INTEGER DEFAULT 0,             -- Higher = sooner
    status TEXT DEFAULT 'pending',          -- 'pending', 'ready', 'processing', 'complete', 'cancelled'
    
    -- Cost estimation
    estimated_tokens INTEGER,
    estimated_mana INTEGER,
    
    -- User confirmation (for Tier 2-3)
    requires_confirmation INTEGER DEFAULT 0, -- 1 if user must approve
    confirmed_at TEXT,                      -- When user approved
    
    -- Processing
    started_at TEXT,
    completed_at TEXT,
    actual_tokens INTEGER,
    actual_mana INTEGER,
    result_summary TEXT,
    error TEXT
);

CREATE INDEX IF NOT EXISTS idx_recog_queue_status ON recog_queue(status, priority DESC);

-- =============================================================================
-- 5. INITIALISE SINGLETON RECORDS
-- =============================================================================

INSERT OR IGNORE INTO ehko_progression (id, stage, created_at, updated_at)
VALUES (1, 'nascent', datetime('now'), datetime('now'));

-- =============================================================================
-- 6. UPDATE EXISTING SESSIONS
-- =============================================================================

-- Mark existing sessions as 'hot' and set last_accessed_at
UPDATE forge_sessions 
SET memory_tier = 'hot', 
    last_accessed_at = COALESCE(updated_at, created_at)
WHERE memory_tier IS NULL;
