-- =============================================================================
-- EHKOFORGE REORIENTATION MIGRATION v0.1
-- =============================================================================
-- 
-- This migration:
-- 1. Renames ingot tables to insite
-- 2. Adds ehko_authority table
-- 3. Adds mana_state and mana_costs tables
-- 4. Adds identity_pillars table for Authority tracking
--
-- Run with: python run_reorientation_migration.py
-- =============================================================================

-- -----------------------------------------------------------------------------
-- STEP 1: RENAME INGOT TABLES TO INSITE
-- -----------------------------------------------------------------------------

-- SQLite doesn't support RENAME TABLE directly for all cases
-- We need to recreate tables with new names

-- Create new insites table (copy of ingots structure)
CREATE TABLE IF NOT EXISTS insites (
    id TEXT PRIMARY KEY,
    summary TEXT,
    themes_json TEXT,
    emotional_tags_json TEXT,
    patterns_json TEXT,
    significance REAL DEFAULT 0.0,
    confidence REAL DEFAULT 0.5,
    source_count INTEGER DEFAULT 1,
    analysis_pass INTEGER DEFAULT 0,
    status TEXT DEFAULT 'raw',
    forged_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Copy data from ingots if it exists
INSERT OR IGNORE INTO insites 
SELECT * FROM ingots WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='ingots');

-- Create new insite_sources table
CREATE TABLE IF NOT EXISTS insite_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insite_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    excerpt TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (insite_id) REFERENCES insites(id)
);

-- Copy data from ingot_sources if it exists
INSERT OR IGNORE INTO insite_sources (insite_id, source_type, source_id, excerpt, added_at)
SELECT ingot_id, source_type, source_id, excerpt, added_at 
FROM ingot_sources WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='ingot_sources');

-- Create new insite_history table
CREATE TABLE IF NOT EXISTS insite_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insite_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trigger TEXT,
    details_json TEXT,
    FOREIGN KEY (insite_id) REFERENCES insites(id)
);

-- Copy data from ingot_history if it exists
INSERT OR IGNORE INTO insite_history (insite_id, event_type, event_at, trigger, details_json)
SELECT ingot_id, event_type, event_at, trigger, details_json 
FROM ingot_history WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='ingot_history');

-- Update ehko_personality_layers to reference insite_id instead of ingot_id
-- (We'll keep the column name as ingot_id for now to avoid breaking existing code,
-- but add an alias column)
ALTER TABLE ehko_personality_layers ADD COLUMN insite_id TEXT;
UPDATE ehko_personality_layers SET insite_id = ingot_id WHERE insite_id IS NULL;

-- Create indexes for new tables
CREATE INDEX IF NOT EXISTS idx_insites_status ON insites(status);
CREATE INDEX IF NOT EXISTS idx_insites_significance ON insites(significance);
CREATE INDEX IF NOT EXISTS idx_insite_sources_insite ON insite_sources(insite_id);
CREATE INDEX IF NOT EXISTS idx_insite_history_insite ON insite_history(insite_id);


-- -----------------------------------------------------------------------------
-- STEP 2: AUTHORITY SYSTEM
-- -----------------------------------------------------------------------------

-- Main authority tracking table (singleton - one row per Ehko)
CREATE TABLE IF NOT EXISTS ehko_authority (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    
    -- Component scores (0.0 - 1.0)
    memory_depth REAL DEFAULT 0.0,
    identity_clarity REAL DEFAULT 0.0,
    emotional_range REAL DEFAULT 0.0,
    temporal_coverage REAL DEFAULT 0.0,
    core_density REAL DEFAULT 0.0,
    
    -- Aggregate Authority (0.0 - 1.0)
    authority_total REAL DEFAULT 0.0,
    
    -- Advancement stage
    advancement_stage TEXT DEFAULT 'nascent',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default row if not exists
INSERT OR IGNORE INTO ehko_authority (id) VALUES (1);

-- Identity pillars tracking (for Identity Clarity component)
CREATE TABLE IF NOT EXISTS identity_pillars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pillar_name TEXT NOT NULL UNIQUE,
    pillar_type TEXT NOT NULL,  -- web, thread, mirror, compass, anchor, flame
    description TEXT,
    populated INTEGER DEFAULT 0,  -- 0 = empty, 1 = has content
    content_count INTEGER DEFAULT 0,  -- number of linked reflections/insites
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed the six pillars
INSERT OR IGNORE INTO identity_pillars (pillar_name, pillar_type, description) VALUES
    ('Web', 'web', 'Relationships and social connections'),
    ('Thread', 'thread', 'Continuity and life narrative'),
    ('Mirror', 'mirror', 'Self-perception and identity'),
    ('Compass', 'compass', 'Values and beliefs'),
    ('Anchor', 'anchor', 'Grounding and stability'),
    ('Flame', 'flame', 'Drive and motivation');


-- -----------------------------------------------------------------------------
-- STEP 3: MANA SYSTEM
-- -----------------------------------------------------------------------------

-- Mana state (singleton - one row)
CREATE TABLE IF NOT EXISTS mana_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    current_mana REAL DEFAULT 100.0,
    max_mana REAL DEFAULT 100.0,
    regen_rate REAL DEFAULT 1.0,  -- mana per hour
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default row
INSERT OR IGNORE INTO mana_state (id) VALUES (1);

-- Mana costs for operations
CREATE TABLE IF NOT EXISTS mana_costs (
    operation TEXT PRIMARY KEY,
    cost REAL NOT NULL,
    description TEXT
);

-- Seed initial costs (tunable)
INSERT OR IGNORE INTO mana_costs (operation, cost, description) VALUES
    ('terminal_message', 1.0, 'Send a message in terminal mode'),
    ('reflection_message', 3.0, 'Send a message in reflection mode'),
    ('recog_sweep', 20.0, 'Manual ReCog engine sweep'),
    ('flag_for_processing', 0.0, 'Flag chat for priority processing');

-- Mana transaction log
CREATE TABLE IF NOT EXISTS mana_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL,
    amount REAL NOT NULL,  -- negative = spent, positive = regenerated
    balance_after REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);


-- -----------------------------------------------------------------------------
-- STEP 4: UPDATE FORGE SESSIONS FOR MODE TRACKING
-- -----------------------------------------------------------------------------

-- Add mode column to forge_sessions
ALTER TABLE forge_sessions ADD COLUMN mode TEXT DEFAULT 'terminal';

-- Add session_tags for click-to-tag feature (if not exists - already exists but ensure it's there)
-- ALTER TABLE forge_sessions ADD COLUMN session_tags TEXT;  -- Already exists


-- -----------------------------------------------------------------------------
-- VERIFICATION QUERIES
-- -----------------------------------------------------------------------------

-- These can be run to verify the migration succeeded:
-- SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;
-- SELECT * FROM ehko_authority;
-- SELECT * FROM mana_state;
-- SELECT * FROM mana_costs;
-- SELECT * FROM identity_pillars;
