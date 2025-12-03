# DATABASE SCHEMA SUMMARY

**Database:** `EhkoForge/_data/ehko_index.db`
**Purpose:** Quick reference for table structure. Read this instead of full Data Model spec.
**Updated:** 2025-12-03

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

## Ingot System Tables (AGPL)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `smelt_queue` | Pending content | id, source_type, source_id, status, priority |
| `transcript_segments` | Chunked transcripts | id, transcript_id, segment_index, content |
| `annotations` | User hints | id, segment_id, annotation_type, content |
| `ingots` | Core insight objects | id, type, tier, content, confidence, status |
| `ingot_sources` | Links ingots to sources | ingot_id, source_type, source_id |
| `ingot_history` | Audit trail | ingot_id, action, timestamp, details |
| `ehko_personality_layers` | Forged personality | id, layer_type, content, weight |

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
```

---

**Changelog:**
- v1.1 — 2025-12-03 — Added license annotations (MIT/AGPL split)
- v1.0 — 2025-12-02 — Initial schema summary created
