-- EhkoForge Tethers Migration v0.1
-- Direct conduits to LLM Sources (BYOK)
-- Unlike mana, tethers never deplete - they channel directly from the Source
--
-- Run with: python run_tethers_migration.py

-- =============================================================================
-- TETHERS TABLE
-- =============================================================================
-- A tether represents a direct connection to an LLM provider.
-- While active, operations route through the tether without consuming mana.

CREATE TABLE IF NOT EXISTS tethers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL DEFAULT 1,
    provider TEXT NOT NULL,                    -- 'claude', 'openai', 'gemini', etc.
    display_name TEXT,                         -- User-friendly name, e.g. "Claude Sonnet"
    api_key_encrypted TEXT NOT NULL,           -- Encrypted API key
    active INTEGER NOT NULL DEFAULT 1,         -- 1 = connected, 0 = disconnected
    last_verified_at TEXT,                     -- Last successful API ping
    verification_status TEXT DEFAULT 'pending', -- 'pending', 'valid', 'invalid', 'expired'
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    
    UNIQUE(user_id, provider)                  -- One tether per provider per user
);

-- Index for quick lookups
CREATE INDEX IF NOT EXISTS idx_tethers_user_provider 
ON tethers(user_id, provider);

CREATE INDEX IF NOT EXISTS idx_tethers_active 
ON tethers(user_id, active);


-- =============================================================================
-- TETHER USAGE LOG
-- =============================================================================
-- Track operations routed through tethers (for analytics, not billing)

CREATE TABLE IF NOT EXISTS tether_usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL DEFAULT 1,
    tether_id INTEGER NOT NULL,
    operation TEXT NOT NULL,                   -- 'chat', 'processing', 'recog', etc.
    provider TEXT NOT NULL,
    model TEXT,
    tokens_input INTEGER,
    tokens_output INTEGER,
    session_id INTEGER,
    timestamp TEXT NOT NULL,
    
    FOREIGN KEY (tether_id) REFERENCES tethers(id)
);

CREATE INDEX IF NOT EXISTS idx_tether_usage_timestamp 
ON tether_usage_log(timestamp);

CREATE INDEX IF NOT EXISTS idx_tether_usage_user 
ON tether_usage_log(user_id, timestamp);


-- =============================================================================
-- PROVIDER METADATA
-- =============================================================================
-- Reference table for supported providers and their capabilities

CREATE TABLE IF NOT EXISTS tether_providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_key TEXT NOT NULL UNIQUE,         -- 'claude', 'openai', 'gemini'
    display_name TEXT NOT NULL,                -- 'Anthropic Claude', 'OpenAI', 'Google Gemini'
    icon_class TEXT,                           -- CSS class for provider icon
    default_model TEXT,                        -- Default model for this provider
    supports_chat INTEGER DEFAULT 1,
    supports_processing INTEGER DEFAULT 1,
    verification_endpoint TEXT,                -- API endpoint to verify key
    active INTEGER DEFAULT 1,
    display_order INTEGER DEFAULT 0
);

-- Seed supported providers
INSERT OR IGNORE INTO tether_providers (provider_key, display_name, default_model, verification_endpoint, display_order) VALUES
    ('claude', 'Anthropic Claude', 'claude-sonnet-4-20250514', 'https://api.anthropic.com/v1/messages', 1),
    ('openai', 'OpenAI', 'gpt-4o-mini', 'https://api.openai.com/v1/models', 2),
    ('gemini', 'Google Gemini', 'gemini-pro', 'https://generativelanguage.googleapis.com/v1/models', 3);


-- =============================================================================
-- VIEW: ACTIVE TETHERS WITH PROVIDER INFO
-- =============================================================================

CREATE VIEW IF NOT EXISTS v_active_tethers AS
SELECT 
    t.id,
    t.user_id,
    t.provider,
    t.display_name,
    t.active,
    t.last_verified_at,
    t.verification_status,
    tp.display_name as provider_display_name,
    tp.default_model,
    tp.supports_chat,
    tp.supports_processing
FROM tethers t
JOIN tether_providers tp ON t.provider = tp.provider_key
WHERE t.active = 1;


-- =============================================================================
-- VIEW: TETHER USAGE STATS (LAST 30 DAYS)
-- =============================================================================

CREATE VIEW IF NOT EXISTS v_tether_usage_stats AS
SELECT 
    user_id,
    provider,
    COUNT(*) as operation_count,
    SUM(tokens_input) as total_tokens_input,
    SUM(tokens_output) as total_tokens_output,
    MAX(timestamp) as last_used_at
FROM tether_usage_log
WHERE timestamp >= datetime('now', '-30 days')
GROUP BY user_id, provider;


-- =============================================================================
-- MIGRATION COMPLETE
-- =============================================================================
