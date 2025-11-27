# 1.4 Data Model — v1.2 Patch Notes

**Changes required to integrate Prepared Messages system from 1.5 Behaviour Engine v1.1**

---

## 1. New Object Type: prepared_message

Add to Section 3.1.1 Required Frontmatter Fields, under `type: string`:

```yaml
type: string  # Object type: reflection, plant_entry, lore_entry, module, prepared_message
```

---

## 2. New Extension Fields: Prepared Messages

Add new section after 3.1.3 Vault-Specific Extension Fields:

### 3.1.4 Prepared Message Extension Fields

```yaml
# Required for type: prepared_message
addressed_to: array[string]          # Names from friend_registry, or ["*"] for anyone
trigger_type: string                 # One of: first_contact, topic, milestone, distress, manual
trigger_conditions: object           # Type-specific trigger configuration
  topics: array[string]              # Keywords/phrases that activate (for topic type)
  milestones: array[string]          # Life events (for milestone type)
  distress_keywords: array[string]   # Emotional signals (for distress type)
  manual_phrase: string              # Exact phrase required (for manual type)
delivery_priority: integer           # Lower = higher priority (default: 5)
one_time_delivery: boolean           # If true, only delivered once per person (default: true)
```

---

## 3. New SQLite Tables

Add to Section 4.3 SQLite Index Generation, after `custodians` table:

```sql
-- Prepared Messages tables (see 1.5 Behaviour Engine Section 3.6)

CREATE TABLE prepared_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    addressed_to TEXT NOT NULL,           -- JSON array of names or ["*"]
    trigger_type TEXT NOT NULL,           -- first_contact, topic, milestone, distress, manual
    trigger_conditions TEXT,              -- JSON object with topics, milestones, etc.
    delivery_priority INTEGER DEFAULT 5,
    one_time_delivery BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE message_deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL,
    friend_id INTEGER NOT NULL,
    delivered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    trigger_context TEXT,                 -- What triggered delivery
    session_id TEXT,                      -- Link to conversation session
    FOREIGN KEY (message_id) REFERENCES prepared_messages(id) ON DELETE CASCADE,
    FOREIGN KEY (friend_id) REFERENCES friend_registry(id) ON DELETE CASCADE
);

CREATE INDEX idx_prepared_addressed ON prepared_messages(addressed_to);
CREATE INDEX idx_prepared_trigger ON prepared_messages(trigger_type);
CREATE INDEX idx_prepared_priority ON prepared_messages(delivery_priority);
CREATE INDEX idx_delivery_message ON message_deliveries(message_id);
CREATE INDEX idx_delivery_friend ON message_deliveries(friend_id);
CREATE INDEX idx_delivery_timestamp ON message_deliveries(delivered_at);
```

---

## 4. New Query Examples

Add to Section 4.4 Cross-Vault Querying:

**Find all prepared messages for a specific friend:**
```sql
SELECT pm.title, pm.trigger_type, pm.file_path
FROM prepared_messages pm
WHERE pm.addressed_to LIKE '%"theo"%'
   OR pm.addressed_to = '["*"]'
ORDER BY pm.delivery_priority ASC;
```

**Find undelivered first-contact messages for a friend:**
```sql
SELECT pm.title, pm.file_path
FROM prepared_messages pm
WHERE pm.trigger_type = 'first_contact'
  AND (pm.addressed_to LIKE '%"theo"%' OR pm.addressed_to = '["*"]')
  AND pm.id NOT IN (
    SELECT message_id FROM message_deliveries md
    JOIN friend_registry fr ON md.friend_id = fr.id
    WHERE fr.name = 'theo'
  );
```

**Find topic-triggered messages matching keywords:**
```sql
SELECT pm.title, pm.file_path, pm.trigger_conditions
FROM prepared_messages pm
WHERE pm.trigger_type = 'topic'
  AND (
    json_extract(pm.trigger_conditions, '$.topics') LIKE '%grief%'
    OR json_extract(pm.trigger_conditions, '$.topics') LIKE '%loss%'
  );
```

**Get delivery history for a friend:**
```sql
SELECT pm.title, md.delivered_at, md.trigger_context
FROM message_deliveries md
JOIN prepared_messages pm ON md.message_id = pm.id
JOIN friend_registry fr ON md.friend_id = fr.id
WHERE fr.name = 'theo'
ORDER BY md.delivered_at DESC;
```

---

## 5. ehko_refresh.py Updates

Add to Section 7 Open Questions / TODOs under 7.5:

### 7.5 Prepared Messages Processing

- [ ] **prepared_message indexing:** ehko_refresh.py must parse prepared_message type files and populate prepared_messages table
- [ ] **JSON field handling:** trigger_conditions and addressed_to stored as JSON strings for SQLite querying
- [ ] **Delivery sync:** message_deliveries table updated by Behaviour Engine, not ehko_refresh.py
- [ ] **Validation:** Verify addressed_to names exist in friend_registry (warn if not)

---

## 6. Changelog Entry

Add to Data Model changelog:

```
- v1.2 — 2025-11-25 — Added prepared_message object type with extension fields; added prepared_messages and message_deliveries SQLite tables; added query examples for prepared message retrieval and delivery tracking; added ehko_refresh.py processing requirements
```
