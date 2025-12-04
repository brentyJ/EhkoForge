-- =============================================================================
-- MANA PURCHASE SYSTEM v0.1
-- Migration to add payment processing and user mana balance tracking
-- 
-- This migration adds:
-- - User accounts table (for multi-user support)
-- - Mana purchase tracking (Stripe integration)
-- - User mana balances (separate from regenerative mana)
-- - API key management (BYOK support)
-- - Configuration for Mana/BYOK/Hybrid modes
-- 
-- Run: python run_mana_migration.py
-- =============================================================================

-- -----------------------------------------------------------------------------
-- USERS TABLE
-- Core user account management
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE,
    password_hash TEXT,  -- For future auth, currently optional
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    account_status TEXT DEFAULT 'active' CHECK(account_status IN ('active', 'suspended', 'deleted'))
);

-- Default user for single-user MVP
INSERT OR IGNORE INTO users (id, email, username) 
VALUES (1, 'local@ehkoforge', 'Forger');

-- -----------------------------------------------------------------------------
-- USER MANA BALANCES
-- Tracks purchased mana (non-regenerative)
-- Separate from regenerative mana_state table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_mana_balance (
    user_id INTEGER PRIMARY KEY,
    purchased_mana REAL DEFAULT 0.0,       -- Total mana purchased (doesn't regenerate)
    lifetime_purchased REAL DEFAULT 0.0,   -- Cumulative all-time purchases
    lifetime_spent REAL DEFAULT 0.0,       -- Cumulative usage
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Initialize for default user
INSERT OR IGNORE INTO user_mana_balance (user_id) VALUES (1);

-- -----------------------------------------------------------------------------
-- MANA PURCHASES
-- Tracks all mana-core purchases via Stripe
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mana_purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount_mana REAL NOT NULL,             -- Mana purchased
    cost_usd REAL NOT NULL,                -- Price paid
    stripe_payment_intent_id TEXT UNIQUE,  -- Stripe reference
    stripe_charge_id TEXT,
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'completed' CHECK(status IN ('pending', 'completed', 'refunded', 'failed')),
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_mana_purchases_user ON mana_purchases(user_id);
CREATE INDEX IF NOT EXISTS idx_mana_purchases_date ON mana_purchases(purchase_date);

-- -----------------------------------------------------------------------------
-- API KEY STORAGE (BYOK)
-- Encrypted storage for user-provided API keys
-- NOTE: Keys should be encrypted at application layer before storage
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_api_keys (
    user_id INTEGER PRIMARY KEY,
    claude_api_key_encrypted TEXT,         -- Anthropic API key (encrypted)
    openai_api_key_encrypted TEXT,         -- OpenAI API key (encrypted)
    key_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

INSERT OR IGNORE INTO user_api_keys (user_id) VALUES (1);

-- -----------------------------------------------------------------------------
-- USER CONFIGURATION
-- Mana system preferences and mode selection
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_config (
    user_id INTEGER PRIMARY KEY,
    
    -- Mana Mode: 'byok' | 'mana' | 'hybrid'
    mana_mode TEXT DEFAULT 'mana' CHECK(mana_mode IN ('byok', 'mana', 'hybrid')),
    
    -- For BYOK mode: regenerative mana config
    byok_max_mana REAL DEFAULT 100.0,
    byok_regen_rate REAL DEFAULT 1.0,      -- Per hour
    
    -- For Hybrid mode: operation routing
    hybrid_chat_source TEXT DEFAULT 'mana' CHECK(hybrid_chat_source IN ('byok', 'mana')),
    hybrid_processing_source TEXT DEFAULT 'mana' CHECK(hybrid_processing_source IN ('byok', 'mana')),
    
    -- Spending limits (safety caps)
    daily_mana_cap REAL DEFAULT 1000.0,
    weekly_mana_cap REAL DEFAULT 5000.0,
    alert_threshold REAL DEFAULT 0.8,      -- Alert when 80% of cap used
    
    -- Provider preferences
    preferred_chat_provider TEXT DEFAULT 'claude',
    preferred_processing_provider TEXT DEFAULT 'openai',
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

INSERT OR IGNORE INTO user_config (user_id) VALUES (1);

-- -----------------------------------------------------------------------------
-- MANA USAGE TRACKING
-- Enhanced version of existing mana_transactions for analytics
-- Separates BYOK (regenerative) from purchased mana
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mana_usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    operation TEXT NOT NULL,
    mana_spent REAL NOT NULL,
    source TEXT NOT NULL CHECK(source IN ('byok', 'purchased', 'hybrid')),
    provider TEXT,                         -- 'claude', 'openai', etc.
    model TEXT,                            -- Specific model used
    tokens_used INTEGER,                   -- Actual API token count
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id INTEGER,                    -- Link to forge_sessions
    details TEXT,                          -- JSON metadata
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES forge_sessions(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_mana_usage_user ON mana_usage_log(user_id);
CREATE INDEX IF NOT EXISTS idx_mana_usage_date ON mana_usage_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_mana_usage_operation ON mana_usage_log(operation);

-- -----------------------------------------------------------------------------
-- MANA-CORE PRICING TIERS
-- Reference table for pricing (editable via admin)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mana_pricing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tier_name TEXT UNIQUE NOT NULL,        -- 'Spark', 'Ember', 'Flame', 'Forge'
    mana_amount REAL NOT NULL,
    price_usd REAL NOT NULL,
    bonus_percentage REAL DEFAULT 0.0,     -- Promotional bonus (e.g., +20%)
    active BOOLEAN DEFAULT 1,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initial pricing tiers (from design)
INSERT OR IGNORE INTO mana_pricing (tier_name, mana_amount, price_usd, display_order) VALUES
    ('Spark', 5000, 5.0, 1),
    ('Ember', 25000, 20.0, 2),
    ('Flame', 100000, 70.0, 3),
    ('Forge', 500000, 300.0, 4);

-- -----------------------------------------------------------------------------
-- VIEWS FOR CONVENIENT QUERIES
-- -----------------------------------------------------------------------------

-- User's total available mana (BYOK regenerative + purchased)
CREATE VIEW IF NOT EXISTS v_user_total_mana AS
SELECT 
    u.id AS user_id,
    u.email,
    uc.mana_mode,
    COALESCE(ms.current_mana, 0) AS regenerative_mana,  -- BYOK pool
    COALESCE(umb.purchased_mana, 0) AS purchased_mana,  -- Purchased pool
    (COALESCE(ms.current_mana, 0) + COALESCE(umb.purchased_mana, 0)) AS total_available,
    umb.lifetime_purchased,
    umb.lifetime_spent
FROM users u
LEFT JOIN user_config uc ON u.id = uc.user_id
LEFT JOIN mana_state ms ON 1=1  -- Single row table
LEFT JOIN user_mana_balance umb ON u.id = umb.user_id;

-- Daily mana usage summary
CREATE VIEW IF NOT EXISTS v_daily_mana_usage AS
SELECT 
    user_id,
    DATE(timestamp) AS usage_date,
    SUM(mana_spent) AS total_spent,
    COUNT(*) AS operation_count,
    GROUP_CONCAT(DISTINCT operation) AS operations_used
FROM mana_usage_log
GROUP BY user_id, DATE(timestamp)
ORDER BY usage_date DESC;

-- =============================================================================
-- MIGRATION COMPLETE
-- =============================================================================

-- Update db_schema_summary.md after running this migration
