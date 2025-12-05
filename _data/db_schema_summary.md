# DATABASE SCHEMA SUMMARY

**Database:** `EhkoForge/_data/ehko_index.db`
**Purpose:** Quick reference for table structure. Read this instead of full Data Model spec.
**Updated:** 2025-12-05 (Session 22)

---

## Core Tables (MIT)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `reflection_objects` | Indexed vault entries | id, vault, path, title, type, status, version, content_hash |
| `tags` | General tags | object_id, tag |
| `emotional_tags` | Emotional markers | object_id, emotion |
| `cross_references` | Links between entries | source_id, target_id, relationship |
| `changelog_entries` | Version history | object_id, version, date, description |
| `mirrorwell_extensions` | Personal metadata | object_id, core_memory, identity_pillar, shared_with |

## Auth/Social Tables (MIT)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `friend_registry` | Known people | id, name, email, relationship, trust_level |
| `shared_with_friends` | Sharing permissions | friend_id, object_id, access_level |
| `shared_memories` | Shared content | id, memory_id, friend_id, shared_at |
| `authentication_tokens` | Active sessions | token, user_id, expires_at |
| `authentication_logs` | Auth history | id, action, timestamp, ip |
| `custodians` | Posthumous access | id, friend_id, activation_trigger |
| `prepared_messages` | Time-capsule messages | id, recipient_id, trigger_condition, content |
| `message_deliveries` | Delivery tracking | message_id, delivered_at, status |

## Forge Session Tables (MIT)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `forge_sessions` | Chat sessions | id, created_at, title, ehko_state |
| `forge_messages` | Session messages | id, session_id, role, content, timestamp |

## Ingot/Insite System Tables (AGPL)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `smelt_queue` | Pending content | id, source_type, source_id, status, priority |
| `transcript_segments` | Chunked transcripts | id, transcript_id, segment_index, content |
| `annotations` | User hints | id, segment_id, annotation_type, content |
| `ingots` / `insites` | Core insight objects | id, type, tier, content, confidence, status |
| `ingot_sources` / `insite_sources` | Links to sources | ingot_id, source_type, source_id |
| `ingot_history` / `insite_history` | Audit trail | ingot_id, action, timestamp, details |
| `ehko_personality_layers` | Forged personality | id, layer_type, content, weight |

## ReCog Pattern Tables (AGPL)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `ingot_patterns` | ReCog patterns across insights | id, summary, pattern_type, strength |
| `ingot_pattern_insights` | Pattern-to-insight links | pattern_id, ingot_id |

## Authority & Mana Tables (AGPL)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `ehko_authority` | Ehko advancement state (singleton) | total_xp, stage, component levels (5) |
| `identity_pillars` | Pillar tracking | id, name, level, xp |
| `mana_state` | Regenerating mana (singleton) | current_mana, max_mana, regen_rate |
| `mana_costs` | Operation costs | operation, cost |
| `mana_transactions` | Spending/regen log | id, operation, amount, timestamp |

## Mana Purchase Tables (AGPL)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `users` | User accounts | id, email, created_at |
| `user_mana_balance` | Purchased mana balance | user_id, purchased_mana, lifetime_purchased |
| `mana_purchases` | Purchase history | id, user_id, tier_id, amount_mana, cost_usd, timestamp |
| `user_api_keys` | BYOK keys (encrypted) | user_id, provider, encrypted_key |
| `user_config` | Mode settings | user_id, mana_mode, byok_max_mana, spending_limits |
| `mana_usage_log` | Usage tracking | id, user_id, operation, amount, mode, timestamp |
| `mana_pricing` | Pricing tiers | id, name, mana_amount, price_usd, bonus_percent |

---

## Common Queries

```sql
-- Get all reflections for a vault
SELECT * FROM reflection_objects WHERE vault = 'Mirrorwell';

-- Get tags for an object
SELECT tag FROM tags WHERE object_id = ?;

-- Get pending ingots
SELECT * FROM ingots WHERE status = 'pending' ORDER BY created_at;

-- Get session messages
SELECT * FROM forge_messages WHERE session_id = ? ORDER BY timestamp;

-- Get user's total mana (regen + purchased)
SELECT 
    ms.current_mana as regen_mana,
    COALESCE(umb.purchased_mana, 0) as purchased_mana,
    ms.current_mana + COALESCE(umb.purchased_mana, 0) as total_mana
FROM mana_state ms
LEFT JOIN user_mana_balance umb ON umb.user_id = 1;

-- Get mana usage by operation
SELECT operation, SUM(amount) as total_spent
FROM mana_usage_log
WHERE user_id = ? AND timestamp > datetime('now', '-30 days')
GROUP BY operation;
```

---

**Changelog:**
- v1.3 — 2025-12-05 — Added ReCog Pattern Tables (ingot_patterns, ingot_pattern_insights).
- v1.2 — 2025-12-05 — Added Mana Purchase Tables section (7 tables). Added mana queries.
- v1.1 — 2025-12-03 — Added Authority & Mana Tables. License annotations (MIT/AGPL split).
- v1.0 — 2025-12-02 — Initial schema summary created
