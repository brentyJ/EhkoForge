-- =============================================================================
-- INGOT SYSTEM MIGRATION v0.1
-- =============================================================================
-- Run: sqlite3 ehko_index.db < ingot_migration_v0_1.sql
-- Or:  python -c "import sqlite3; conn = sqlite3.connect('ehko_index.db'); conn.executescript(open('ingot_migration_v0_1.sql').read())"
-- =============================================================================

-- Smelt queue: tracks pending raw input for analysis
CREATE TABLE IF NOT EXISTS smelt_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,          -- 'chat_session', 'transcript', 'upload'
    source_id TEXT NOT NULL,            -- session_id, file_path, segment_id
    queued_at TEXT NOT NULL,            -- ISO timestamp
    status TEXT DEFAULT 'pending',      -- 'pending', 'processing', 'complete', 'failed'
    priority INTEGER DEFAULT 0,         -- higher = process sooner
    word_count INTEGER,                 -- for threshold checks
    pre_annotation_json TEXT,           -- Tier 0 output (JSON blob)
    last_processed_at TEXT,             -- last smelt pass timestamp
    pass_count INTEGER DEFAULT 0,       -- how many times smelted
    notes TEXT                          -- error messages, processing notes
);

CREATE INDEX IF NOT EXISTS idx_smelt_queue_status ON smelt_queue(status, priority DESC);
CREATE INDEX IF NOT EXISTS idx_smelt_queue_source ON smelt_queue(source_type, source_id);

-- Transcript segments: breaks large uploads into chunks
CREATE TABLE IF NOT EXISTS transcript_segments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transcript_path TEXT NOT NULL,      -- original file path
    segment_index INTEGER NOT NULL,     -- order within transcript
    content TEXT NOT NULL,              -- segment text
    word_count INTEGER,
    start_timestamp TEXT,               -- if available from source
    end_timestamp TEXT,                 -- if available from source
    speaker TEXT,                       -- if identified
    pre_annotation_json TEXT,           -- Tier 0 output for this segment
    created_at TEXT NOT NULL,
    UNIQUE(transcript_path, segment_index)
);

CREATE INDEX IF NOT EXISTS idx_transcript_segments_path ON transcript_segments(transcript_path);

-- Annotations: user hints on raw content
CREATE TABLE IF NOT EXISTS annotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,          -- 'chat_message', 'transcript_segment'
    source_id INTEGER NOT NULL,         -- message_id or segment_id
    annotation_type TEXT NOT NULL,      -- 'highlight', 'comment', 'tag', 'intensity'
    content TEXT,                       -- comment text, tag value, intensity level
    char_start INTEGER,                 -- for partial highlights (nullable)
    char_end INTEGER,                   -- for partial highlights (nullable)
    created_at TEXT NOT NULL,
    UNIQUE(source_type, source_id, annotation_type, char_start)
);

CREATE INDEX IF NOT EXISTS idx_annotations_source ON annotations(source_type, source_id);

-- Ingots: core insight objects
CREATE TABLE IF NOT EXISTS ingots (
    id TEXT PRIMARY KEY,                -- UUID
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    status TEXT DEFAULT 'raw',          -- 'raw', 'refined', 'surfaced', 'forged', 'rejected', 'merged'
    
    -- Significance
    significance REAL DEFAULT 0.5,      -- 0.0-1.0
    significance_tier TEXT,             -- derived: 'copper', 'iron', 'silver', 'gold', 'mythic'
    confidence REAL DEFAULT 0.5,        -- how certain is this insight
    
    -- Content
    summary TEXT NOT NULL,              -- 1-3 sentence distillation
    themes_json TEXT,                   -- JSON array of theme tags
    emotional_tags_json TEXT,           -- JSON array of emotional tags
    patterns_json TEXT,                 -- JSON array of identified patterns
    
    -- Lineage
    source_count INTEGER DEFAULT 1,     -- how many sources contributed
    earliest_source_date TEXT,          -- oldest contributing source
    latest_source_date TEXT,            -- newest contributing source
    
    -- Integration
    forged_at TEXT,                     -- when accepted into Ehko
    forged_reflection_id INTEGER,       -- link to reflection_objects if file created
    merged_into_id TEXT,                -- if merged, points to surviving ingot
    
    -- Processing metadata
    last_analysis_at TEXT,
    analysis_model TEXT,                -- which LLM tier processed this
    analysis_pass INTEGER DEFAULT 1     -- which pass generated/updated this
);

CREATE INDEX IF NOT EXISTS idx_ingots_status ON ingots(status);
CREATE INDEX IF NOT EXISTS idx_ingots_significance ON ingots(significance DESC);

-- Ingot sources: links ingots to source material
CREATE TABLE IF NOT EXISTS ingot_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingot_id TEXT NOT NULL,
    source_type TEXT NOT NULL,          -- 'chat_message', 'transcript_segment', 'reflection'
    source_id TEXT NOT NULL,            -- message_id, segment_id, reflection file_path
    contribution_weight REAL DEFAULT 1.0, -- how much this source contributed
    excerpt TEXT,                       -- relevant snippet (for UI display)
    added_at TEXT NOT NULL,
    FOREIGN KEY (ingot_id) REFERENCES ingots(id),
    UNIQUE(ingot_id, source_type, source_id)
);

CREATE INDEX IF NOT EXISTS idx_ingot_sources_ingot ON ingot_sources(ingot_id);
CREATE INDEX IF NOT EXISTS idx_ingot_sources_source ON ingot_sources(source_type, source_id);

-- Ingot history: audit trail of ingot evolution
CREATE TABLE IF NOT EXISTS ingot_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingot_id TEXT NOT NULL,
    event_type TEXT NOT NULL,           -- 'created', 'significance_change', 'merged', 'forged', 'rejected', 'source_added'
    event_at TEXT NOT NULL,
    old_value TEXT,                     -- JSON of previous state
    new_value TEXT,                     -- JSON of new state
    trigger TEXT,                       -- 'smelt_pass', 'user_action', 'correlation'
    FOREIGN KEY (ingot_id) REFERENCES ingots(id)
);

CREATE INDEX IF NOT EXISTS idx_ingot_history_ingot ON ingot_history(ingot_id, event_at);

-- Ehko personality layers: forged insights as personality components
CREATE TABLE IF NOT EXISTS ehko_personality_layers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingot_id TEXT NOT NULL,
    layer_type TEXT NOT NULL,           -- 'trait', 'memory', 'pattern', 'value', 'voice'
    content TEXT NOT NULL,              -- the actual personality instruction/context
    weight REAL DEFAULT 1.0,            -- influence strength
    active INTEGER DEFAULT 1,           -- can be toggled off without deleting
    integrated_at TEXT NOT NULL,
    FOREIGN KEY (ingot_id) REFERENCES ingots(id)
);

CREATE INDEX IF NOT EXISTS idx_personality_layers_active ON ehko_personality_layers(active, layer_type);

-- =============================================================================
-- END MIGRATION
-- =============================================================================
