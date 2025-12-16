-- =============================================================================
-- ENTITY REGISTRY MIGRATION v0.1
-- =============================================================================
-- Purpose: Store known entities (people, contacts) for preflight context
-- Run: python run_entity_migration.py
-- =============================================================================

-- =============================================================================
-- 1. ENTITY REGISTRY - Known entities with user-provided context
-- =============================================================================

CREATE TABLE IF NOT EXISTS entity_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Entity identification
    entity_type TEXT NOT NULL,              -- 'person', 'phone', 'email', 'organisation'
    raw_value TEXT NOT NULL,                -- Original extracted value (+61412345678, jane@example.com)
    normalised_value TEXT,                  -- Normalised form for matching (61412345678)
    
    -- User-provided context
    display_name TEXT,                      -- Human-friendly name ("Mum", "Jane Smith")
    relationship TEXT,                      -- Relationship to user ("mother", "therapist", "manager")
    notes TEXT,                             -- Any additional context
    
    -- Privacy controls
    anonymise_in_prompts INTEGER DEFAULT 0, -- If 1, use placeholder in LLM calls
    placeholder_name TEXT,                  -- Placeholder to use ("Person A", "Family Member 1")
    
    -- Metadata
    first_seen_at TEXT NOT NULL,            -- When first extracted
    last_seen_at TEXT,                      -- Most recent appearance
    occurrence_count INTEGER DEFAULT 1,     -- How many times seen
    source_types TEXT,                      -- JSON array of source types seen in
    
    -- Status
    confirmed INTEGER DEFAULT 0,            -- User has reviewed/confirmed this entity
    merged_into_id INTEGER,                 -- If merged with another entity
    
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    
    UNIQUE(entity_type, normalised_value)
);

CREATE INDEX IF NOT EXISTS idx_entity_type ON entity_registry(entity_type);
CREATE INDEX IF NOT EXISTS idx_entity_normalised ON entity_registry(normalised_value);
CREATE INDEX IF NOT EXISTS idx_entity_confirmed ON entity_registry(confirmed);

-- =============================================================================
-- 2. ENTITY ALIASES - Multiple values that map to same entity
-- =============================================================================

CREATE TABLE IF NOT EXISTS entity_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL,             -- FK to entity_registry
    alias_type TEXT NOT NULL,               -- 'phone', 'email', 'nickname', 'name_variation'
    alias_value TEXT NOT NULL,              -- The alternative value
    normalised_value TEXT,                  -- Normalised for matching
    
    created_at TEXT NOT NULL,
    
    FOREIGN KEY (entity_id) REFERENCES entity_registry(id) ON DELETE CASCADE,
    UNIQUE(alias_type, normalised_value)
);

CREATE INDEX IF NOT EXISTS idx_alias_entity ON entity_aliases(entity_id);
CREATE INDEX IF NOT EXISTS idx_alias_normalised ON entity_aliases(normalised_value);

-- =============================================================================
-- 3. ENTITY OCCURRENCES - Track where entities appear
-- =============================================================================

CREATE TABLE IF NOT EXISTS entity_occurrences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL,             -- FK to entity_registry
    
    -- Source reference
    source_type TEXT NOT NULL,              -- 'chat_session', 'document', 'transcript', 'chatgpt_export'
    source_id TEXT NOT NULL,                -- ID of source
    
    -- Context
    excerpt TEXT,                           -- Text snippet around the entity
    position_in_source INTEGER,             -- Approximate position (for ordering)
    
    detected_at TEXT NOT NULL,
    
    FOREIGN KEY (entity_id) REFERENCES entity_registry(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_occurrence_entity ON entity_occurrences(entity_id);
CREATE INDEX IF NOT EXISTS idx_occurrence_source ON entity_occurrences(source_type, source_id);

-- =============================================================================
-- 4. PREFLIGHT SESSIONS - Track batch processing context
-- =============================================================================

CREATE TABLE IF NOT EXISTS preflight_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Session info
    session_type TEXT NOT NULL,             -- 'single_file', 'batch', 'chatgpt_import'
    status TEXT DEFAULT 'pending',          -- 'pending', 'scanned', 'reviewing', 'confirmed', 'processing', 'complete'
    
    -- Source files
    source_files_json TEXT,                 -- JSON array of file paths
    source_count INTEGER DEFAULT 0,         -- Number of files/items
    
    -- Tier 0 results (aggregated)
    total_word_count INTEGER DEFAULT 0,
    total_entities_found INTEGER DEFAULT 0,
    unknown_entities_count INTEGER DEFAULT 0,
    estimated_tokens INTEGER DEFAULT 0,
    estimated_cost_cents INTEGER DEFAULT 0,
    
    -- Filtering applied
    filters_json TEXT,                      -- JSON: {date_range, min_words, keywords, etc}
    items_after_filter INTEGER,             -- Count after filtering
    
    -- Entity resolution
    entity_questions_json TEXT,             -- JSON: Questions needing user input
    entity_answers_json TEXT,               -- JSON: User's answers
    
    -- Processing
    started_at TEXT,
    completed_at TEXT,
    recog_operations_created INTEGER DEFAULT 0,
    
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_preflight_status ON preflight_sessions(status);

-- =============================================================================
-- 5. PREFLIGHT ITEMS - Individual items in a preflight session
-- =============================================================================

CREATE TABLE IF NOT EXISTS preflight_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    preflight_session_id INTEGER NOT NULL,
    
    -- Item info
    source_type TEXT NOT NULL,              -- 'chatgpt_conversation', 'sms_thread', 'document', etc
    source_id TEXT,                         -- Unique ID within source
    title TEXT,                             -- Display title
    
    -- Content summary
    word_count INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0,        -- For chat-type content
    date_range_start TEXT,                  -- Earliest date in content
    date_range_end TEXT,                    -- Latest date in content
    
    -- Tier 0 results
    pre_annotation_json TEXT,               -- Full Tier 0 output
    entities_found_json TEXT,               -- Entities specific to this item
    
    -- Filtering
    included INTEGER DEFAULT 1,             -- User can exclude items
    exclusion_reason TEXT,                  -- Why excluded (manual, filter, etc)
    
    -- Processing
    processed INTEGER DEFAULT 0,
    recog_operation_id INTEGER,             -- FK to recog_queue if processed
    
    created_at TEXT NOT NULL,
    
    FOREIGN KEY (preflight_session_id) REFERENCES preflight_sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_preflight_items_session ON preflight_items(preflight_session_id);
CREATE INDEX IF NOT EXISTS idx_preflight_items_included ON preflight_items(included, processed);
